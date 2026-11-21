# hedgehog_clips.py - SML-04 Hedgehog clips (planning/FarmAnimals/ANIMATIONS.md: Idle "sniffs", Walk "walks",
# Curl_Up "curls into a ball"). Shared helpers from _common/animal_anim.py are imported read-only.
# setup_ik/leg_ik_h: copy of ../Dog/dog_clips.py (rest-offset leg IK; the hedgehog legs rest straight, offsets ~0);
# gait_hh: copy of ../Fox/fox_clips.gait_fox; write_action: copy of animal_anim.write_action with location channels for
# the bones in `loc_bones` (Curl_Up keys the head and the leg roots moving INTO the shell).
import math
import numpy as np
from mathutils import Vector, Matrix, Euler
from bpy_extras import anim_utils
import bpy
from animal_anim import *
from animal_anim import R, LEGS
import animal_anim as _an
import animal_rig as ar

TW = 2 * math.pi
_IK = {}
UPPERS = ['FrontUpper.L', 'FrontUpper.R', 'HindUpper.L', 'HindUpper.R']


# ---------------- leg IK with rest offsets (copy of ../Dog/dog_clips.py) ----------------
def setup_ik(sk):
    global leg_ik
    for k in LEGS:
        up, lo, ft, front = ar.LEGS[k]
        cl = sk.rel[lo].to_3x3().col[1]; cf = sk.rel[ft].to_3x3().col[1]
        de = math.atan2(cl.z, cl.y); ep = math.atan2(cf.z, cf.y)
        t = sk.rest[up].inverted() @ sk.rest[ft].translation
        base = math.atan2(t.z, math.hypot(t.x, t.y))
        sgn = (1.0 if base > 0 else -1.0) if abs(base) > math.radians(1.0) else (1.0 if front else -1.0)
        if front: sgn = 1.0
        _IK[k] = (de, ep, sgn)
        print(f'IK {k}: lower rest {math.degrees(de):.1f} deg, foot rest {math.degrees(ep):.1f} deg, knee side {sgn:+.0f}')
    _an.leg_ik = leg_ik_h; leg_ik = leg_ik_h


def leg_ik_h(sk, pose, leg, fetlock, hoof_pitch=0.0):
    up, lo, ft, front = ar.LEGS[leg]; de, ep, sgn = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up] @ Matrix.Translation(pose[up][0])
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
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def hold(t, a, b, ramp):
    """periodic plateau: 0 before a, smooth rise over `ramp`, 1 until b, smooth fall over `ramp` (phase units)"""
    x = (t - a) % 1.0; L = (b - a) % 1.0
    if x < ramp: return smooth(x / ramp)
    if x < L: return 1.0
    if x < L + ramp: return 1.0 - smooth((x - L) / ramp)
    return 0.0


def loc_off(sk, pose, bone, off):
    """bone location from an offset given in armature space at rest (m)"""
    pose[bone][0] = list(sk.rest[bone].to_3x3().transposed() @ Vector(off))


# ---------------- actions (location channels for loc_bones) ----------------
def write_action(rig, name, frames, loop, loc_bones, scales=None):
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in frames[0]:
        chans = [('rotation_euler', 1)] + ([('location', 0)] if b in loc_bones else [])
        for path, ix in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1)
                co = []
                for f, p in enumerate(frames): co += [float(f), p[b][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))   # LINEAR
                fc.update()
    for b, sv in (scales or {}).items():          # uniform bone scale keys (Curl_Up: head + legs shrink inside the ball)
        for i in range(3):
            fc = cb.fcurves.new(f'pose.bones["{b}"].scale', index=i, group_name=b)
            fc.keyframe_points.add(N + 1)
            co = []
            for f, v in enumerate(sv): co += [float(f), v]
            fc.keyframe_points.foreach_set('co', co)
            fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))
            fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act


def loc_closure(act):
    cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0]); N = act.frame_end; w = 0.0
    for fc in cb.fcurves:
        if fc.data_path.endswith('.location'): w = max(w, abs(fc.evaluate(0) - fc.evaluate(N)))
    return round(w, 7)


def gait_hh(sk, sp, name, overlay):
    """copy of ../Fox/fox_clips.gait_fox (overlay applied BEFORE the leg IK)"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            fl = g['flick'][0 if k.startswith('Front') else 1]; gx = G.x * g['narrow']
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** 0.9; hp = R(fl) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((gx, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = g['reach'] * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; dx = gx - piv[k].x; vert = math.sqrt(max(Lm * Lm - dy * dy - dx * dx, 0.0))
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
        pitch = math.degrees(math.asin((df - dh) / span))
        body(sk, pose, (0, 0, -dh + g['bob'] * math.cos(2 * TW * ph)), pitch=pitch, roll=g['roll'] * math.sin(TW * ph))
        overlay(pose, ph, pitch)
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                drops={k: [round(float(d.min()), 4), round(float(d.max()), 4)] for k, d in drops.items()})


# ---------------- ball ----------------
def ball_pose(sk, cu):
    """the back arches (pelvis tips the rump down, Spine1/Spine2 bend the front down), the head tucks down and back
    under the shell front (rotation + keyed translation into the body), the ears fold back, the legs are pulled up into
    the shell (keyed translation of the leg roots); set down on its lowest vertex"""
    p = new_pose(sk)
    body(sk, p, (0, 0, 0), pitch=cu['pelvis'])
    rot(p, 'Spine1', x=cu['spine'][0]); rot(p, 'Spine2', x=cu['spine'][1])
    rot(p, 'Neck1', x=cu['neck'][0]); rot(p, 'Neck2', x=cu['neck'][1]); rot(p, 'Head', x=cu['head'][0])
    loc_off(sk, p, 'Head', (0.0, cu['head_back'], -cu['head_down']))
    ear(p, up=cu['ear'][0], back=cu['ear'][1])
    for b, sx in (('Ear.L', 1.0), ('Ear.R', -1.0)):          # folded ears slid in towards the crown (inside the shell)
        loc_off(sk, p, b, (-sx * cu['ear_in'], 0.0, -cu['ear_down']))
    for k in LEGS:                       # legs pulled up into the shell and folded in towards the belly centre
        up, lo, ft, front = ar.LEGS[k]
        loc_off(sk, p, up, cu['leg_front'] if front else cu['leg_hind'])
        rot(p, up, x=cu['leg_fold'] if front else -cu['leg_fold'])
    if cu.get('to_centre'):
        # rework 2026-11-21: the shell closes into a loop (Pelvis/Spine1/Spine2 ~115 deg each), so the local head/leg
        # offsets above no longer point inside -> move each hidden sub-chain rigidly (bone location of its root) so its
        # mesh centroid sits at the ball centre (+ small spread), where the closed shell covers it
        shell = sk.mask(['Pelvis', 'Spine1', 'Spine2'])
        C = Vector(sk.skin(sk.fk(p), shell).mean(0))
        subs = [('Head', ['Head', 'Nose', 'Ear.L', 'Ear.R'], cu['to_centre']['head'])]
        for k in LEGS:
            up, lo, ft, front = ar.LEGS[k]; sx = 1.0 if up.endswith('.L') else -1.0
            o = cu['to_centre']['front' if front else 'hind']
            subs.append((up, [up, lo, ft], (sx * o[0], o[1], o[2])))
        for root, bones, off in subs:
            M = sk.fk(p); cur = Vector(sk.skin(M, sk.mask(bones)).mean(0))
            d = C + Vector(off) - cur
            par = M[sk.parent[root]] @ sk.rel[root]
            p[root][0] = list(Vector(p[root][0]) + par.to_3x3().inverted() @ d)
    no_penetration(sk, p, exact=True)
    return p


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.0 s) "sniffs": three sniff bouts - the head lifts and points a little left / up / right, the snout
    # twitches fast (8 Hz) during each bout, the ears flick; 2 breaths; feet planted. All periodic over the loop.
    idl = sp['idle']; NS = 24                         # 24 snout cycles in 3 s (8 Hz) - integer -> closed loop

    def ov_idle(p, t):
        breathe(sk, p, t, 0.0006, 2, 0.8)
        b1 = hold(t, 0.05, 0.22, 0.06); b2 = hold(t, 0.38, 0.52, 0.06); b3 = hold(t, 0.68, 0.84, 0.06)
        up = idl['head_up'] * (b1 + 0.7 * b2 + 1.0 * b3)
        yaw = idl['turn'] * (b1 - b3) + 0.3 * idl['turn'] * b2
        rot(p, 'Neck1', x=-0.5 * up, z=0.4 * yaw); rot(p, 'Head', x=-0.5 * up, z=0.6 * yaw)
        sn = b1 + b2 + b3
        rot(p, 'Nose', x=idl['nose'][0] * sn * math.sin(TW * NS * t), z=idl['nose'][1] * sn * math.sin(TW * NS * t + 1.1))
        rot(p, 'Head', x=0.8 * sn * math.sin(TW * NS * t + 0.6))          # tiny head bob with each sniff
        fl = flick(t, 0.30, 0.07); fr_ = flick(t, 0.60, 0.07)
        rot(p, 'Ear.L', x=-idl['ear'] * fl, z=6 * fl); rot(p, 'Ear.R', x=-idl['ear'] * fr_, z=-6 * fr_)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.5 s): busy lateral-sequence patter on the short legs, the shell rolls and sways a little, the head bobs and
    # the snout keeps sniffing (2x per cycle).
    g = sp['gait']['Walk']

    def ov_walk(p, ph, pitch):
        rot(p, 'Spine1', z=g['sway'] * math.sin(TW * ph)); rot(p, 'Spine2', z=-g['sway'] * math.sin(TW * ph - 0.4))
        rot(p, 'Neck1', x=-0.6 * pitch + 1.5 * math.sin(2 * TW * ph - 1.0), z=-0.8 * g['sway'] * math.sin(TW * ph - 0.9))
        rot(p, 'Head', x=-1.0 * math.sin(2 * TW * ph - 1.4))
        rot(p, 'Nose', x=g['nose'] * math.sin(4 * TW * ph), z=0.6 * g['nose'] * math.sin(2 * TW * ph + 0.5))
        rot(p, 'Ear.L', x=3.0 * math.sin(2 * TW * ph - 2.0)); rot(p, 'Ear.R', x=3.0 * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = gait_hh(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Curl_Up (3.0 s, loop): the ears fold first, the head tucks, the back arches and the legs pull in -> a spiky ball resting on the
    # ground (lowest vertex = 0 every frame), holds it with 2 small breaths, then uncurls: the legs come out, the back
    # flattens and the head comes out last (peeking). First frame = last frame = the standing pose -> closed loop.
    cu = sp['curl']; BALL = ball_pose(sk, cu); N = frames_of(dur['Curl_Up'][0])
    HEAD_B = ['Neck1', 'Neck2', 'Head', 'Nose']; EAR_B = ['Ear.L', 'Ear.R']
    LEG_B = [b for k in LEGS for b in ar.LEGS[k][:3]]
    (a0, a1), (b0, b1) = cu['t_in'], cu['t_out']

    def env(t, lead):
        """0 -> 1 over [a0, a1] (shifted by lead), hold, 1 -> 0 over [b0, b1] (head leaves last: lead < 0 on the way out)"""
        x0, x1 = a0 + lead[0], a1 + lead[0]; y0, y1 = b0 + lead[1], b1 + lead[1]
        if t <= x0: return 0.0
        if t < x1: return smooth((t - x0) / (x1 - x0))
        if t <= y0: return 1.0
        if t < y1: return 1.0 - smooth((t - y0) / (y1 - y0))
        return 0.0
    fr = []; hold_frames = []; shr = cu.get('shrink', {})
    scales = {b: [] for b in shr}
    for f in range(N + 1):
        t = f / N
        ch = env(t, cu.get('lead_head', (-0.03, 0.05))); ce = env(t, (-0.05, 0.08)); cb = env(t, (0.0, 0.0)); cl = env(t, cu.get('lead_legs', (0.04, -0.04)))
        for b, (sm, lead) in shr.items():         # shrink runs ahead of the curl and ends after the uncurl
            c = env(t, lead); scales[b].append(1.0 if f in (0, N) else 1.0 - (1.0 - sm) * c)
        p = copy_pose(STAND)
        for b in p:
            c = ch if b in HEAD_B else ce if b in EAR_B else cl if b in LEG_B else cb
            p[b] = [[x + (y - x) * c for x, y in zip(STAND[b][0], BALL[b][0])], [x + (y - x) * c for x, y in zip(STAND[b][1], BALL[b][1])]]
        if min(ch, ce, cb, cl) >= 1.0:
            hold_frames.append(f)
            s = math.sin(TW * 2 * (t - (a1 + 0.04)) / (b0 - a1 - 0.08))
            rot(p, 'Spine1', x=1.2 * s); rot(p, 'Spine2', x=0.8 * s)
        if f in (0, N): p = copy_pose(STAND)
        else: no_penetration(sk, p, exact=True)
        fr.append(p)
    hf = [hold_frames[0], hold_frames[len(hold_frames) // 2], hold_frames[-1]]
    out['Curl_Up'] = dict(frames=fr, scale=scales, events=[(round(a0 * N), 'Curl', 'In'), (round(b0 * N), 'Curl', 'Out')],
                          extra=dict(hold_frames=hf, ball=dict(hold=[hold_frames[0], hold_frames[-1]])))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
