# goat_clips.py - LIV-08 Goat clips (ANIMATIONS.md: Idle "stands", Walk "walks", Browse "browses leaves").
# Shared helpers from _common/animal_anim.py are imported read-only. gait_goat() is the Sheep/Pig gait copy (overlay applied
# BEFORE the leg IK, so the feet stay planted); write_action_loc keys Neck1 location in every take (Browse neck stretch).
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi
NOSE_MASK = [None]          # set by rig_goat: boolean mask of the Nose part vertices in the TMP joined mesh


# ---------------- leg IK with rest offsets (copied from ../Horse/horse_clips.py): the goat hind leg rests with the hock
# bent (~24 deg between gaskin and cannon); animal_anim.leg_ik assumes collinear bones. This copy subtracts the rest
# angles and replaces animal_anim.leg_ik in THIS process only (plant() calls it by module global); the file is untouched.
import animal_anim as _an
from mathutils import Matrix
_IK = {}


def setup_ik(sk):
    global leg_ik
    for k in LEGS:
        up, lo, ft, front = ar.LEGS[k]
        cl = sk.rel[lo].to_3x3().col[1]; cf = sk.rel[ft].to_3x3().col[1]
        de = math.atan2(cl.z, cl.y); ep = math.atan2(cf.z, cf.y)
        t = sk.rest[up].inverted() @ sk.rest[ft].translation
        base = math.atan2(t.z, math.hypot(t.x, t.y))
        sgn = (1.0 if base > 0 else -1.0) if abs(base) > math.radians(1.0) else (1.0 if front else -1.0)
        _IK[k] = (de, ep, sgn)
        print(f'IK {k}: lower rest {math.degrees(de):.1f} deg, foot rest {math.degrees(ep):.1f} deg, knee side {sgn:+.0f}')
    _an.leg_ik = leg_ik_h; leg_ik = leg_ik_h


def leg_ik_h(sk, pose, leg, fetlock, hoof_pitch=0.0):
    up, lo, ft, front = ar.LEGS[leg]; de, ep, sgn = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
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
    pose[up][1] = [a1, 0.0, beta]; pose[lo][1] = [phi2 - a1 - de, 0.0, 0.0]; pose[ft][1] = [phid + hoof_pitch - phi2 - ep, 0.0, 0.0]
    return d0 - (L1 + L2)


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def burst(t, c, w, n=2):
    """n fast oscillations inside a window [c, c+w) of the loop phase, zero elsewhere"""
    x = ((t - c) % 1.0) / w
    return math.sin(n * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0


def tail_flick(p, b, base=0.0):
    """short upright goat tail: quick side flicks along Tail1-3 (amplitude grows to the tip), small upward cock"""
    rot(p, 'Tail1', x=-3 * abs(b) + base, z=12 * b); rot(p, 'Tail2', z=16 * b); rot(p, 'Tail3', z=20 * b)


def gait_goat(sk, sp, name, overlay):
    """copy of the Sheep/Pig gait (animal_anim.gait + overlay hook before the leg IK)"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            fl = g['flick'][0 if k.startswith('Front') else 1]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** 1.1; hp = R(fl) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((G.x, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = 0.985 * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        Fc = np.fft.rfft(a); Fc[4:] = 0; sm = np.fft.irfft(Fc, N)
        sm += max(0.0, float((a - sm).max())); drops[gk] = sm + g['crouch']
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)), roll=g['roll'] * math.sin(TW * ph))
        overlay(pose, ph)
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drops={k: [round(float(x), 4) for x in d] for k, d in drops.items()})


def head_angle(M):
    """head bone axis above the forward horizontal (deg); rest pose ~ -58 (face looking down-forward)"""
    ya = M['Head'].to_3x3().col[1]
    return math.degrees(math.atan2(ya.z, -ya.y))


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS, feet=None):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted, feet); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.5 s): 2 breaths, the head turns a little left/right (lagged neck), ears flick in turn (L 0.15, R 0.50,
    # small L twitch 0.82), the short tail flicks twice (0.30, 0.72), the beard sways behind the head. All periodic.
    def ov_idle(p, t):
        breathe(sk, p, t, 0.004, 2, 1.0)
        rot(p, 'Neck1', x=1.2 * math.sin(TW * t + 0.4), z=3.0 * math.sin(TW * t - 0.3))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=7.0 * math.sin(TW * t))
        fl = flick(t, 0.15, 0.10) + 0.5 * flick(t, 0.82, 0.08); fr_ = flick(t, 0.50, 0.10)
        rot(p, 'Ear.L', x=-2 + 2 * math.sin(TW * t) + 16 * fl, z=-(3 * math.sin(TW * t + 0.5)) + 26 * fl)
        rot(p, 'Ear.R', x=-2 + 2 * math.sin(TW * t + 1.7) + 16 * fr_, z=-(-3 * math.sin(TW * t + 2.2) + 26 * fr_))
        tail_flick(p, burst(t, 0.30, 0.10, 3) + 0.8 * burst(t, 0.72, 0.09, 3) + 0.10 * math.sin(TW * 2 * t))
        rot(p, 'Beard', x=3.0 * math.sin(TW * 2 * t - 2.2), z=-5.0 * math.sin(TW * t - 0.9))
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.9 s): light, precise lateral-sequence walk with high, quick swings; small head bob twice per cycle, ears and
    # beard swing with a lag, the upright tail flicks with the steps
    g = sp['gait']['Walk']

    def ov_walk(p, ph):
        nod = g['nod'] * math.sin(TW * 2 * ph - 1.2)
        rot(p, 'Neck1', x=0.5 * nod, z=1.2 * math.sin(TW * ph - 0.6)); rot(p, 'Head', x=-0.3 * nod, z=-1.0 * math.sin(TW * ph - 0.9))
        e = g['ear'] * math.sin(TW * 2 * ph - 2.0)
        rot(p, 'Ear.L', x=e, z=0.5 * e); rot(p, 'Ear.R', x=g['ear'] * math.sin(TW * 2 * ph - 2.3), z=-0.5 * e)
        tail_flick(p, 0.45 * math.sin(TW * 2 * ph - 1.5), base=2.0 * math.sin(TW * 2 * ph))
        rot(p, 'Beard', x=g['beard'] * math.sin(TW * 2 * ph - 2.4), z=0.6 * g['beard'] * math.sin(TW * ph - 1.4))
    fr, ev, extra = gait_goat(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Browse (4 s loop): front of the body raised a little, neck pitched UP and stretched forward-up along its axis (keyed
    # Neck1 translation) so the muzzle reaches a branch above the poll height; 2 bites per loop: reach + mouth opens, bite,
    # small tug (head down + neck slides back), then chewing; ears forward, tail flicks. All periodic.
    bw = sp['browse']
    br = copy_pose(STAND); body(sk, br, (0, 0.0, 0.0), pitch=bw['body_pitch']); plant(sk, br)
    nm = NOSE_MASK[0] if NOSE_MASK[0] is not None else sk.mask(['Head'])
    base = {bn: br[bn][1][0] for bn in ('Neck1', 'Neck2', 'Head')}
    cand = []
    for r in range(0, 11, 1):
        br['Neck1'][0] = [0.0, r / 100.0, 0.0]
        for n in range(0, -61, -5):
            for h in range(0, -51, -5):
                br['Neck1'][1][0] = base['Neck1'] + R(0.55 * n); br['Neck2'][1][0] = base['Neck2'] + R(0.45 * n)
                br['Head'][1][0] = base['Head'] + R(h)
                M_ = sk.fk(br); Pn = sk.skin(M_, nm); zc = float(Pn[:, 2].mean()); a = head_angle(M_)
                if abs(zc - bw['nose_z']) < 0.025 and bw['head_ang'][0] <= a <= bw['head_ang'][1]:
                    cand.append((abs(n) + abs(h) + 1.5 * r + 200 * abs(zc - bw['nose_z']), r, n, h, zc, a))
    if not cand: raise RuntimeError('BROWSE: no neck/head solution')
    _, r_, n_, h_, zc_, a_ = min(cand)
    br['Neck1'][0] = [0.0, r_ / 100.0, 0.0]
    br['Neck1'][1][0] = base['Neck1'] + R(0.55 * n_); br['Neck2'][1][0] = base['Neck2'] + R(0.45 * n_); br['Head'][1][0] = base['Head'] + R(h_)
    print(f'BROWSE neck stretch {r_ / 100.0} m, neck pitch {n_} (Neck1 {0.55 * n_:.1f} Neck2 {0.45 * n_:.1f}), head pitch {h_}, '
          f'nose centre z {zc_:.3f}, head axis {a_:.1f} deg above horizontal, candidates {len(cand)}')

    hang = -0.9 * (n_ + h_ + bw['body_pitch'])
    print(f'BROWSE beard hang counter-rotation {hang:.1f} deg')

    def ov_browse(p, t):
        u = (2 * t) % 1.0                                                   # 2 bites per loop
        reach = smooth(u / 0.12) if u < 0.12 else (1 - smooth((u - 0.12) / 0.10) if u < 0.22 else 0.0)
        tug = math.sin(math.pi * (u - 0.16) / 0.16) if 0.16 <= u < 0.32 else 0.0
        jaw = 12 * smooth(u / 0.12) if u < 0.12 else (12 * (1 - smooth((u - 0.12) / 0.05)) if u < 0.17 else 0.0)
        if u >= 0.34: jaw = 3.5 * (1 - math.cos(TW * 4 * (u - 0.34) / 0.66))            # 4 chews after each bite
        loc = p['Neck1'][0]
        p['Neck1'][0] = [loc[0], loc[1] + bw['reach_extra'] * reach - bw['tug_back'] * tug, loc[2]]
        rot(p, 'Neck1', x=-2.0 * reach + 2.0 * tug); rot(p, 'Head', x=-4.0 * reach + bw['tug_deg'] * tug, z=2.0 * math.sin(TW * t))
        rot(p, 'Jaw', x=jaw, z=(2.5 * math.sin(TW * 4 * (u - 0.34) / 0.66) if u >= 0.34 else 0.0))
        # the beard keeps hanging down (gravity): counter the raised head/neck pitch, then a small lagged sway
        rot(p, 'Beard', x=hang - 0.4 * jaw + 6.0 * reach - 4.0 * tug + 3.0 * math.sin(TW * 2 * t - 2.0), z=3.0 * math.sin(TW * t - 0.8))
        breathe(sk, p, t, 0.003, 2, 0.8)
        fe = flick(t, 0.62, 0.08)
        rot(p, 'Ear.L', x=4 + 10 * fe, z=-bw['ear_fwd'] + 20 * fe); rot(p, 'Ear.R', x=4, z=bw['ear_fwd'] - 3 * math.sin(TW * t))
        tail_flick(p, burst(t, 0.40, 0.09, 3) + 0.8 * burst(t, 0.88, 0.08, 3))
    out['Browse'] = dict(frames=loop_static('Browse', br, ov_browse), events=[],
                         extra=dict(stretch=r_ / 100.0, neck=n_, head=h_, nose_z=zc_, head_angle=a_))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


LOC_BONES = ('Pelvis', 'Neck1')


def write_action_loc(rig, name, frames, loop, bones=None):
    """copy of animal_anim.write_action that also keys Neck1 location (Browse stretch) in every take (0 outside Browse)"""
    import bpy
    from bpy_extras import anim_utils
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for bn in (bones or [n for n in frames[0]]):
        chans = [('rotation_euler', 1)] + ([('location', 0)] if bn in LOC_BONES else [])
        for path, ix in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{bn}"].{path}', index=i, group_name=bn)
                fc.keyframe_points.add(N + 1)
                co = []
                for f, p in enumerate(frames): co += [float(f), p[bn][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act
