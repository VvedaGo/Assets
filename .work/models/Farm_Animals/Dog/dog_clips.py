# dog_clips.py - PET-01 Dog clips (ANIMATIONS.md: Idle "wags its tail", Walk "walks"; Sit_Idle not in this batch).
# Shared helpers from _common/animal_anim.py are imported read-only. setup_ik/leg_ik_h = the Horse/Goat rest-offset leg IK
# copy (the dog hind leg rests with the hock bent); gait_dog = the Goat gait copy (overlay applied BEFORE the leg IK).
import math
import numpy as np
from mathutils import Vector, Matrix
from animal_anim import *
from animal_anim import R, LEGS
import animal_anim as _an
import animal_rig as ar

TW = 2 * math.pi
WAGS = 7                    # Idle: 7 wags in 3.0 s (2.33 Hz), integer -> closed loop
_IK = {}
FOOT_CAP = math.radians(float(__import__('os').environ.get('DOG_FOOT_CAP', '36')))


# ---------------- leg IK with rest offsets (copy of ../Goat/goat_clips.py, itself from ../Horse/horse_clips.py) ----------------
def setup_ik(sk):
    global leg_ik
    for k in LEGS:
        up, lo, ft, front = ar.LEGS[k]
        cl = sk.rel[lo].to_3x3().col[1]; cf = sk.rel[ft].to_3x3().col[1]
        de = math.atan2(cl.z, cl.y); ep = math.atan2(cf.z, cf.y)
        t = sk.rest[up].inverted() @ sk.rest[ft].translation
        base = math.atan2(t.z, math.hypot(t.x, t.y))
        sgn = (1.0 if base > 0 else -1.0) if abs(base) > math.radians(1.0) else (1.0 if front else -1.0)
        if front: sgn = 1.0      # dog: the front paw rests a little forward of the shoulder; the carpus still flexes back
        _IK[k] = (de, ep, sgn)
        print(f'IK {k}: lower rest {math.degrees(de):.1f} deg, foot rest {math.degrees(ep):.1f} deg, knee side {sgn:+.0f}')
    _an.leg_ik = leg_ik_h; leg_ik = leg_ik_h


def leg_ik_h(sk, pose, leg, fetlock, hoof_pitch=0.0):
    up, lo, ft, front = ar.LEGS[leg]; de, ep, sgn = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up] @ Matrix.Translation(pose[up][0])   # Sit: FrontUpper slide
    t = M0.inverted() @ Vector(fetlock)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    a1 = base - sgn * al
    ky, kz = L1 * math.cos(a1), L1 * math.sin(a1)
    ty, tz2 = d * math.cos(base), d * math.sin(base)
    phi2 = math.atan2(tz2 - kz, ty - ky)
    dd = Matrix.Rotation(-beta, 3, 'Z') @ (M0.to_3x3().inverted() @ Vector((0, 0, -1)))
    phid = math.atan2(dd.z, dd.y)
    # round 4: the paw follows the ground only within FOOT_CAP of the lower leg: in swing the folded leg used to turn the
    # rigid paw block 60-90 deg against the shank and it came loose from it (user: paws 'crawl out of each other')
    fx = phid + hoof_pitch - phi2 - ep; fx = max(-FOOT_CAP, min(FOOT_CAP, fx))
    pose[up][1] = [a1, 0.0, beta]; pose[lo][1] = [phi2 - a1 - de, 0.0, 0.0]; pose[ft][1] = [fx, 0.0, 0.0]
    return d0 - (L1 + L2)


LOC_BONES = ('Pelvis', 'FrontUpper.L', 'FrontUpper.R')


def write_action(rig, name, frames, loop, bones=None):
    """copy of animal_anim.write_action that also keys the location of FrontUpper.L/R (Sit_Idle shoulder slide: the
    leg slides up along its rest axis into the chest, like the scapula); all channels LINEAR"""
    from bpy_extras import anim_utils
    import bpy
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in (bones or [n for n in frames[0]]):
        chans = [('rotation_euler', 1)] + ([('location', 0)] if b in LOC_BONES else [])
        for path, ix in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1)
                co = []
                for f, p in enumerate(frames): co += [float(f), p[b][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def wag(p, ph, amps, lag, lift=(0.0, 0.0, 0.0)):
    """lateral tail wag along Tail1-3: amplitude grows to the tip, each bone lags the previous by `lag` of a cycle"""
    for i, (b, a) in enumerate(zip(('Tail1', 'Tail2', 'Tail3'), amps)):
        rot(p, b, x=lift[i], z=a * math.sin(TW * (ph - lag * i)))


def walk_dog(sk, sp, name, overlay):
    """dog walk (round 2 rebuild). Diagonal couplets (HindL+FrontR, HindR+FrontL, the front foot `lag` of a cycle after
    its diagonal hind), stance windows centred under the shoulder / hip, stance travel S = duty x stride. Feet: stance =
    straight line back at the walking speed (no slip); swing = cycloid forward with a sine lift, the paw flexes (sole
    turns back) in swing. Body height per girdle = the highest pose in which every stance leg is at most `straight` x its
    length (front legs nearly straight -> no forward bow in stance; hind legs keep a visible hock bend), smoothed with
    `harm` harmonics and never higher than reachable; pitch from the front/hind difference; light roll."""
    g = sp['gait'][name]; N = frames_of(g['T']); T = N / FPS; duty = g['duty']; D = g['stride']; v = D / T; S = duty * D
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    ctr = {k: Vector((sk.feet[k].x + (1 if k.endswith('L') else -1) * g['out'][0 if k.startswith('Front') else 1],
                      piv[k].y + g['centre'][0 if k.startswith('Front') else 1], 0.0)) for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            fr_ = k.startswith('Front'); i = 0 if fr_ else 1
            p = (ph - g['phases'][k]) % 1.0; G = ctr[k]; L3 = sk.length[ar.LEGS[k][2]]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'][i] * math.sin(math.pi * s ** g['lift_skew'][i]); hp = R(g['flick'][i]) * math.sin(math.pi * s ** 0.8) ** 2
            row[k] = (Vector((G.x, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = g['straight'][i] * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; dx = G.x - piv[k].x; vert = math.sqrt(max(Lm * Lm - dy * dy - dx * dx, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        sm = a.copy()                       # smooth upper envelope of the need (iterated low-pass of max(sm, need))
        for _ in range(60):
            Fc = np.fft.rfft(np.maximum(sm, a)); Fc[g['harm']:] = 0; sm = np.fft.irfft(Fc, N)
        drops[gk] = np.maximum(sm, a) + g['crouch']
    span = piv['HindL'].y - piv['FrontL'].y
    Lm = {k: g['straight'][0 if k.startswith('Front') else 1] * (sk.length[ar.LEGS[k][0]] + sk.length[ar.LEGS[k][1]]) for k in LEGS}
    Lf = {k: sk.length[ar.LEGS[k][0]] + sk.length[ar.LEGS[k][1]] for k in LEGS}

    def make(f, df, dh, sroll):
        ph = f / N; pose = new_pose(sk)
        pitch = math.degrees(math.asin((df - dh) / span))
        body(sk, pose, (g['sway'] * math.sin(TW * ph - 0.3), 0, -dh), pitch=pitch, roll=g['roll'] * math.sin(TW * ph))
        rot(pose, 'Spine2', y=sroll); rot(pose, 'Neck1', y=-sroll)       # shoulder roll (double support), head kept level
        overlay(pose, ph, pitch)
        e = {}
        for k in LEGS:
            fet, hp, st = targ[f][k]
            ex_ = leg_ik(sk, pose, k, fet, hp) + Lf[k] - Lm[k]             # > 0: stance leg longer than its straightness
            if st: e[k] = ex_
        return pose, e

    def envelope(a, harm):
        sm = a.copy()
        for _ in range(80):
            Fc = np.fft.rfft(np.maximum(sm, a)); Fc[harm:] = 0; sm = np.fft.irfft(Fc, N)
        return np.maximum(sm, a)

    def solve(f, df, dh, sroll, free_roll, fix_hind=False):
        """girdle drops so the most loaded stance leg of each girdle sits exactly at its straightness; in front double
        support the shoulder roll is solved too so BOTH front legs are straight (no slack -> no forward bow)"""
        for _ in range(10):
            pose, e = make(f, df, dh, sroll)
            fe = [e[k] for k in ('FrontL', 'FrontR') if k in e]; he = [e[k] for k in ('HindL', 'HindR') if k in e]
            if free_roll and len(fe) == 2:
                _, e2 = make(f, df, dh, sroll + 0.5)
                dd = ((e2['FrontL'] - e2['FrontR']) - (e['FrontL'] - e['FrontR'])) / 0.5
                if abs(dd) > 1e-6: sroll -= (e['FrontL'] - e['FrontR']) / dd
            if fe: df += max(fe)
            if he and not fix_hind: dh += max(he)
        return df, dh, sroll
    # pass 1: free roll in front double support -> the roll curve; eased (smoothstep) across single support frames
    dsf = {f for f in range(N) if f in stance['FrontL'] and f in stance['FrontR']}
    roll_ds = {}
    for f in sorted(dsf):
        df, dh, r = solve(f, drops['Front'][f], drops['Hind'][f], 0.0, True); roll_ds[f] = r
    sroll = np.zeros(N)
    if roll_ds:
        keys = sorted(roll_ds)
        for f in range(N):
            if f in roll_ds: sroll[f] = roll_ds[f]; continue
            a = max([k for k in keys if k < f] or [keys[-1] - N]); b = min([k for k in keys if k > f] or [keys[0] + N])
            u = smooth((f - a) / (b - a)); sroll[f] = roll_ds[a % N] * (1 - u) + roll_ds[b % N] * u
    # pass 2: drops solved per frame with the fixed roll curve; the hind curve is then smoothed as an upper envelope (the
    # hind legs may take slack: the hock just bends a little more), pass 3 re-solves the front with that hind curve
    for f in range(N):
        drops['Front'][f], drops['Hind'][f], _ = solve(f, drops['Front'][f], drops['Hind'][f], float(sroll[f]), False)
    drops['Hind'] = envelope(drops['Hind'], g['harm_hind'])
    frames = []; excess = 0.0
    for f in range(N):
        df, dh, _ = solve(f, drops['Front'][f], drops['Hind'][f], float(sroll[f]), False, fix_hind=True)
        drops['Front'][f] = df
        pose, e = make(f, df, dh, float(sroll[f]))
        excess = max([excess] + [e[k] - (Lf[k] - Lm[k]) for k in e])
        frames.append(pose)
    print('WALK shoulder roll (deg) min/max', round(float(sroll.min()), 2), round(float(sroll.max()), 2),
          '| drops front', round(float(drops['Front'].min()), 4), round(float(drops['Front'].max()), 4),
          'hind', round(float(drops['Hind'].min()), 4), round(float(drops['Hind'].max()), 4))
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    print(f'WALK N {N} T {T:.3f}s stride {D:.3f} stance travel {S:.3f} speed {v:.3f} m/s, worst stance reach excess {excess * 1000:.1f} mm')
    return frames, events, dict(stance=stance, speed=v, step=S, stride=D, N=N, targets=targ,
                                drops={k: [round(float(x), 4) for x in d] for k, d in drops.items()})


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.0 s): relaxed stance with the hind girdle lowered (`hind_drop`) and the hind paws a little back, so the hock
    # shows a clear backward bend (front legs stay straight); the weight shifts once left-right over the loop (body sways
    # sideways + rolls, all four paws planted); 2 breaths (chest rises, spine flexes); the bushy tail is carried a little
    # higher and wags wide 7x (2.33 Hz) with a lag along Tail1-3; the rump answers each wag; head turn, ear twitches.
    idl = sp['idle']
    span = sk.rest['HindUpper.L'].translation.y - sk.rest['FrontUpper.L'].translation.y
    i_pitch = math.degrees(math.asin((idl['front_drop'] - idl['hind_drop']) / span))
    i_feet = {k: Vector((sk.feet[k].x, sk.feet[k].y + (idl['hind_back'] if k.startswith('Hind') else 0.0), 0.0)) for k in LEGS}

    def idle_base(p, t, corr=0.0):
        ws = math.sin(TW * t)                                                # weight shift: once per loop
        body(sk, p, (idl['shift'] * ws, 0.0, -idl['hind_drop']), pitch=i_pitch + corr, roll=-idl['shift_roll'] * ws,
             yaw=0.8 * math.sin(TW * t - 0.6))
        plant(sk, p, LEGS, i_feet)

    Lfr = sk.length['FrontUpper.L'] + sk.length['FrontLower.L']; L3f = sk.length['FrontFoot.L']

    def idle_frame(t):
        """pitch corrected per frame so the more loaded front leg sits at 0.9995 of its length (no forward bow)"""
        corr = 0.0
        for _ in range(8):
            p = new_pose(sk); idle_base(p, t, corr); ov_idle(p, t)
            e = max(leg_ik(sk, p, k, i_feet[k] + Vector((0, 0, L3f))) for k in ('FrontL', 'FrontR')) + 0.0005 * Lfr
            corr += math.degrees(math.asin(max(-0.2, min(0.2, e / span))))
        plant(sk, p, LEGS, i_feet); return p

    def ov_idle(p, t):
        breathe(sk, p, t, idl['breath'], 2, idl['breath_spine'])
        rot(p, 'Ruff', x=-1.0 * math.sin(2 * TW * t))
        w = WAGS * t
        wag(p, w, idl['wag'], idl['lag'], lift=idl['tail_lift'])
        rot(p, 'Pelvis', z=-idl['hip'] * math.sin(TW * (w + 0.25)))          # rump sways against the wag
        rot(p, 'Neck1', x=1.0 * math.sin(TW * t + 0.4), z=3.0 * math.sin(TW * t - 0.3))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=6.0 * math.sin(TW * t))
        rot(p, 'Ruff', x=0.6 * math.sin(2 * TW * t - 0.5))
        fl = flick(t, 0.18, 0.09) + 0.5 * flick(t, 0.83, 0.07); fr_ = flick(t, 0.52, 0.09)
        rot(p, 'Ear.L', x=-idl['ear'] * fl + 1.5 * math.sin(TW * t), z=8 * fl)
        rot(p, 'Ear.R', x=-idl['ear'] * fr_ + 1.5 * math.sin(TW * t + 1.7), z=-8 * fr_)
    Ni = frames_of(dur['Idle'][0]); fr = []
    for f in range(Ni):
        fr.append(idle_frame(f / Ni))
    fr.append(copy_pose(fr[0]))
    out['Idle'] = dict(frames=fr, events=[])

    # Walk (34 fr = 1.133 s): diagonal couplets (HindL+FrontR, HindR+FrontL, the front foot 0.18 cycle after its hind),
    # stride 0.60 m, body rises over the vertical legs twice per cycle, the head held level (neck counters the body
    # pitch), the low bushy tail sways once per cycle with a lag along Tail1-3 and bounces lightly, ruff and ears bob.
    g = sp['gait']['Walk']

    def ov_walk(p, ph, pitch):
        rot(p, 'Neck1', x=-0.6 * pitch + 0.6 * math.sin(2 * TW * ph - 1.0), z=1.0 * math.sin(TW * ph - 0.6))
        rot(p, 'Head', x=-0.4 * pitch - 0.8 * math.sin(2 * TW * ph - 1.3), z=-0.8 * math.sin(TW * ph - 0.9))
        wag(p, ph, g['tail'], 0.10, lift=tuple(g.get('tail_carry', (0, 0, 0))[i] + g['tail_bounce'] * math.sin(2 * TW * ph - 1.6 - 0.5 * i) for i in range(3)))
        rot(p, 'Ruff', x=g['ruff'] * math.sin(2 * TW * ph - 1.9))
        e = g['ear'] * math.sin(2 * TW * ph - 2.0)
        rot(p, 'Ear.L', x=e); rot(p, 'Ear.R', x=g['ear'] * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = walk_dog(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)
    if 'Sit_Idle' in dur:
        fr, info = sit_clip(sk, sp, frames_of(dur['Sit_Idle'][0]))
        out['Sit_Idle'] = dict(frames=fr, events=[], extra=dict(sit=info))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


# ---------------- Sit_Idle: a ready sitting pose (no transitions) ----------------
def aim(sk, pose, bone, d):
    """set the bone's local rotation so its axis points along world direction d (minimal rotation from the rest axis)"""
    M = sk.fk(pose); par = sk.parent[bone]
    Mp = (M[par] @ sk.rel[bone]) if par else sk.rel[bone]
    tl = Mp.to_3x3().normalized().inverted() @ Vector(d).normalized()
    pose[bone][1] = list(Vector((0, 1, 0)).rotation_difference(tl).to_euler('XYZ'))


def aim_xz(sk, pose, bone, d):
    """like aim() but twist-free: local euler (x, 0, z) with the smaller |z| (x = flexion, z = abduction)"""
    M = sk.fk(pose); par = sk.parent[bone]
    Mp = (M[par] @ sk.rel[bone]) if par else sk.rel[bone]
    tl = (Mp.to_3x3().normalized().inverted() @ Vector(d)).normalized()
    best = None
    for sg in (1.0, -1.0):
        a = math.atan2(tl.z, sg * math.hypot(tl.x, tl.y)); ca = math.cos(a)
        b = math.atan2(-tl.x / ca, tl.y / ca)
        if best is None or abs(b) < abs(best[1]): best = (a, b)
    pose[bone][1] = [best[0], 0.0, best[1]]


def hinge(sk, pose, bone, y, nxt):
    """orient `bone` so its Y axis is world direction y and its X axis (the hinge of the child joint) is normal to the
    plane (y, nxt), on the same side as the bone's unrotated X axis"""
    M = sk.fk(pose); par = sk.parent[bone]
    Mp = ((M[par] @ sk.rel[bone]) if par else sk.rel[bone]).to_3x3().normalized()
    x = y.cross(nxt).normalized()
    if x.dot(Mp.col[0]) < 0: x = -x
    z = x.cross(y).normalized()
    Rw = Matrix((x, y, z)).transposed()
    pose[bone][1] = list((Mp.inverted() @ Rw).to_euler('XYZ'))


def sit_pose(sk, st):
    """Sit (rig round 2). Pelvis pitched nose-up + Spine1/2 lift, rump on the ground; pitch searched for the asked torso
    tilt (line Pelvis joint -> Spine2 joint vs the ground). Front legs: the FrontUpper joint (now at the chest bottom)
    slides straight up inside the chest (bone location, like the scapula) until the straight leg reaches the ground at
    `front_slant` deg forward; paws `front_out` apart. Hind legs: thigh (hip -> hock) forward-out beside the belly, joint
    near the ground, lower leg forward along the ground to the paw beside the front paw; neck/head counter-pitched to look ahead; tail on the ground."""
    bodym = sk.mask(['Pelvis', 'Spine1', 'Spine2'])
    L1f, L2f = sk.length['FrontUpper.L'], sk.length['FrontLower.L']; L3f = sk.length['FrontFoot.L']
    Lf = L1f + L2f + L3f

    def seat(P):
        p = new_pose(sk); body(sk, p, (0, 0, 0), pitch=P)
        rot(p, 'Spine1', x=st['spine'][0]); rot(p, 'Spine2', x=st['spine'][1])
        raise_body(sk, p, st['rump_z'] - sk.minz(p, bodym))          # rump (lowest body vertex) on the ground
        M = sk.fk(p); A = M['Pelvis'].translation; Bv = M['Spine2'].translation
        return p, math.degrees(math.atan2(Bv.z - A.z, A.y - Bv.y))
    tab = []; best = None
    for P in range(-15, -80, -1):
        p, tilt = seat(P); tab.append((P, round(tilt, 1)))
        if tilt >= st['tilt']: best = (P, p, tilt); break
    if best is None: best = (P, p, tilt)
    print('SIT pelvis pitch -> torso tilt', tab[::4] + tab[-1:])
    P, p, tilt = best
    back = -(P + st['spine'][0] + st['spine'][1])          # total nose-up pitch of the chest
    # round 6 (user: the sit is still 'ужас'; the Codex reference sit shows why): the counter-pitch left the neck leaning BACK
    # 25 deg past vertical (Neck2 joint 6 cm behind Spine2), so the head sat above the rump looking at the sky. The neck is
    # now aimed in world space: Neck1/Neck2 lean `neck` deg FORWARD of vertical (Codex sit: 21 / 14), the head stays level.
    c2 = math.radians(st['chest'])                       # Spine2 (chest) continues the spine line: Codex sit 59 deg
    aim_xz(sk, p, 'Spine2', Vector((0.0, -math.cos(c2), math.sin(c2))))
    n1, n2 = (math.radians(v) for v in st['neck'])
    aim_xz(sk, p, 'Neck1', Vector((0.0, -math.sin(n1), math.cos(n1))))
    aim_xz(sk, p, 'Neck2', Vector((0.0, -math.sin(n2), math.cos(n2))))
    hd = sk.rest['Head'].to_3x3() @ Vector((0, 1, 0)); hu = math.radians(st['head_up'])
    hd = Vector((hd.x, hd.y * math.cos(hu) - hd.z * math.sin(hu), hd.z * math.cos(hu) + hd.y * math.sin(hu)))
    aim_xz(sk, p, 'Head', hd)
    rot(p, 'Ruff', x=st['ruff'])
    # front legs: slide the joint up (world vertical) until the straight leg stands at front_slant
    a = math.radians(st['front_slant']); Lm = st['front_ext'] * (L1f + L2f)
    feet = {}; slide = {}
    for k in ('FrontL', 'FrontR'):
        up = ar.LEGS[k][0]; sx = 1.0 if k.endswith('L') else -1.0
        M = sk.fk(p); Mp = (M[sk.parent[up]] @ sk.rel[up]).to_3x3()
        J0 = (M[sk.parent[up]] @ sk.rel[up]).translation
        need = Lm * math.cos(a) * math.cos(math.atan2(st['front_out'], Lm)) + L3f
        s = max(0.0, need - J0.z); slide[k] = s
        p[up][0] = list(Mp.inverted() @ Vector((0.0, 0.0, s)))
        J = J0 + Vector((0, 0, s)); h = J.z - L3f
        feet[k] = Vector((J.x + sx * st['front_out'], J.y - h * math.tan(a), 0.0))
    plant(sk, p, ['FrontL', 'FrontR'], feet)
    # hind legs: thigh forward-out beside the belly to the joint near the ground, white lower leg forward along the
    # ground (turned in) to the paw beside the front paw (in the sit this joint reads as the stifle: it folds forward)
    for k in ('HindL', 'HindR'):
      up, lo, ft, _ = ar.LEGS[k]; sx = 1.0 if k.endswith('L') else -1.0
      pm = sk.mask([ft, lo]); zk = st['hock_z']
      for _it in range(4):                                  # raise the joint until the paw box rests on the ground
        H = sk.fk(p)[up].translation; Lu = sk.length[up]; Ll = sk.length[lo]; L3 = sk.length[ft]
        dz = H.z - zk; hr = math.sqrt(max(Lu * Lu - dz * dz, 0.0)); sp_ = math.radians(st['hock_splay'])
        Kp = Vector((H.x + sx * hr * math.sin(sp_), H.y - hr * math.cos(sp_), zk))
        sl = math.asin(max(0.0, min(0.9, (st['hock_z'] - L3 - 0.004) / Ll))); ci = math.radians(st['cannon_in'])
        cd = Vector((-sx * math.sin(ci) * math.cos(sl), -math.cos(ci) * math.cos(sl), -math.sin(sl)))   # forward along the ground
        hinge(sk, p, up, (Kp - H).normalized(), cd)
        aim(sk, p, lo, cd)
        aim(sk, p, ft, Vector((0.0, -0.25, -1.0)))
        mz = sk.minz(p, pm)
        if abs(mz) < 5e-4: break
        zk -= mz
    # tail on the ground behind, gentle sideways curve
    T0 = sk.fk(p)['Tail1'].translation; L1 = sk.length['Tail1']
    a = math.asin(max(-1.0, min(1.0, (T0.z - st['tail_z']) / L1)))
    aim(sk, p, 'Tail1', Vector((0.0, math.cos(a), -math.sin(a))))
    for b, ang, up_ in (('Tail2', st['tail_curve'][0], 0.0), ('Tail3', st['tail_curve'][1], st['tail_tip_up'])):
        c = math.radians(ang); aim(sk, p, b, Vector((math.sin(c), math.cos(c), math.sin(math.radians(up_)))))
    Vw = sk.skin(sk.fk(p)); iv = int(np.argmin(Vw[:, 2]))
    print('SIT lowest vertex', round(float(Vw[iv, 2]), 4), 'bone', sk.order[int(np.argmax(sk.W[iv]))])
    M = sk.fk(p)
    info = dict(pelvis_pitch=P, torso_tilt=round(tilt, 1), shoulder_slide_m=round(slide['FrontL'], 3),
                shoulder_z=round(M['FrontUpper.L'].translation.z, 3), hip_z=round(M['HindUpper.L'].translation.z, 3),
                front_leg=round(Lf, 3), front_slant_deg=st['front_slant'],
                front_paws_x=round(feet['FrontL'].x - feet['FrontR'].x, 3),
                hind_paws_y=[round(M['HindFoot.L'].translation.y, 3)], front_paws_y=round(feet['FrontL'].y, 3))
    print('SIT', info)
    return p, feet, info


def sit_clip(sk, sp, N):
    st = sp['sit']; base, feet, info = sit_pose(sk, st)

    def ov(p, t):
        b = math.sin(TW * st['breaths'] * t)                            # breathing: chest + ruff rise and fall
        rot(p, 'Spine2', x=-1.6 * b); rot(p, 'Spine1', x=0.6 * b); rot(p, 'Ruff', x=-2.2 * b); rot(p, 'Neck1', x=0.7 * b)
        rot(p, 'Neck1', z=3.0 * math.sin(TW * t - 0.4))                 # head turns a little and tilts
        rot(p, 'Head', z=6.0 * math.sin(TW * t), y=5.0 * math.sin(TW * t + 1.2), x=-1.2 * math.sin(2 * TW * t + 0.7))
        fl = flick(t, 0.22, 0.09); fr_ = flick(t, 0.64, 0.09)            # one ear at a time
        rot(p, 'Ear.L', x=-14 * fl + 1.2 * math.sin(TW * t), z=8 * fl)
        rot(p, 'Ear.R', x=-14 * fr_ + 1.2 * math.sin(TW * t + 1.7), z=-8 * fr_)
        lift = bump(t, 0.35, 0.16) + bump(t, 0.85, 0.14)                # tail tip lifts and wags slowly twice
        rot(p, 'Tail3', x=st['tip_lift'] * lift, z=st['tip_wag'] * math.sin(TW * 2 * t) * (0.4 + 0.6 * lift))
        rot(p, 'Tail2', x=0.3 * st['tip_lift'] * lift, z=0.3 * st['tip_wag'] * math.sin(TW * 2 * t - 0.6))
    import os as _o
    if _o.environ.get('DOG_JOINTS'):
        _M = sk.fk(base)
        for _b in ('Pelvis','Spine1','Spine2','Neck1','Neck2','Ruff','Head','FrontUpper.L','FrontLower.L','FrontFoot.L','HindUpper.L','HindLower.L','HindFoot.L','Tail1','Tail2','Tail3'):
            _t = _M[_b].translation; print('JOINT', _b, round(_t.x,3), round(_t.y,3), round(_t.z,3))
    fr = []
    for f in range(N):
        p = copy_pose(base); ov(p, f / N); plant(sk, p, ['FrontL', 'FrontR'], feet); fr.append(p)
    fr.append(copy_pose(fr[0]))
    return fr, info
