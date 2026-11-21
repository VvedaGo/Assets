# kitten_clips.py - PET-04 Kitten clips (ANIMATIONS.md: Idle "moves its tail", Walk "walks", Pounce "a short playful
# lunge"). Copied from ../Cat/cat_clips.py (read-only there): flick, s_wave, ears, gait_cat; Lie_Idle code dropped,
# Pounce added. Shared helpers from _common/animal_anim.py are imported read-only. Kitten legs rest with offsets -> the Dog rest-offset leg IK (setup_ik / leg_ik_h).
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar
from mathutils import Matrix
import animal_anim as _an

TW = 2 * math.pi
_IK = {}
TAIL_WAVES = 2              # Idle: 2 slow S-waves in 3.5 s (integer -> closed loop)
FRONT_LEGS = ['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R']
HIND_LEGS = ['HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R']
BODY = ['Pelvis', 'Spine1', 'Spine2']
TAIL = ['Tail1', 'Tail2', 'Tail3']


# ---------------- leg IK with rest offsets (copy of ../Dog/dog_clips.py without the dog front-knee override) ----------------
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


def tip_ik(sk, pose, leg, tip):
    """kitten swing IK: Upper + (Lower+Foot as one straight segment) reaching the paw TIP; of the two knee solutions the
    one with the joint more forward is used (the paw trails / curls back like a cat's carpus)"""
    up, lo, ft, front = ar.LEGS[leg]; de, ep, _ = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
    t = M0.inverted() @ Vector(tip)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo] + sk.length[ft]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    best = None
    for sgn in ((1.0, -1.0) if front else (_IK[leg][2],)):
        a1 = base - sgn * al
        ky, kz = L1 * math.cos(a1), L1 * math.sin(a1)
        ty, tz2 = d * math.cos(base), d * math.sin(base)
        phi2 = math.atan2(tz2 - kz, ty - ky)
        q = {up: [a1, 0.0, beta], lo: [phi2 - a1 - de, 0.0, 0.0], ft: [-ep, 0.0, 0.0]}
        test = {n: [list(v[0]), list(v[1])] for n, v in pose.items()}
        for n, v in q.items(): test[n][1] = v
        ky_w = sk.fk(test)[lo].translation.y
        if best is None or ky_w < best[0]: best = (ky_w, q)
    for n, v in best[1].items(): pose[n][1] = v


def swing_leg(sk, pose, leg, ankle, w):
    """blend (weight w, 0 at lift-off/touch-down) from the ankle IK already in `pose` (paw vertical) to tip_ik"""
    if w <= 1e-6: return
    up, lo, ft, _ = ar.LEGS[leg]
    a = {n: list(pose[n][1]) for n in (up, lo, ft)}
    tip_ik(sk, pose, leg, Vector(ankle) - Vector((0, 0, sk.length[ft])))
    for n in (up, lo, ft): pose[n][1] = [x + (y - x) * w for x, y in zip(a[n], pose[n][1])]


def sw_weight(s):
    return smooth(min(1.0, 3.0 * s)) * smooth(min(1.0, 3.0 * (1.0 - s)))


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def s_wave(p, ph, amps, lag, pitch=(0.0, 0.0, 0.0)):
    """travelling lateral wave up Tail1-3 (each bone `lag` of a cycle later) -> the held-up tail draws slow S-curves"""
    for i, (b, a) in enumerate(zip(TAIL, amps)):
        rot(p, b, x=pitch[i], z=a * math.sin(TW * (ph - lag * i)))


def ears(p, t, events, amp=22.0):
    """ear twitches: events [(side, centre, width, strength)] -> quick flick back/out, slow relax"""
    for side, c, w, k in events:
        e = k * flick(t, c, w); sg = 1 if side == 'L' else -1
        rot(p, 'Ear.' + side, x=amp * 0.6 * e, z=sg * amp * e)


def gait_cat(sk, sp, name, overlay):
    """copy of animal_anim.gait (via ../Dog/dog_clips.gait_dog): overlay applied BEFORE the leg IK, feet placed closer to
    the midline (cats put their paws nearly in a line), stance reach as a parameter"""
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
            row[k] = (Vector((gx, y, z + L3)), hp, (sw_weight((p - duty) / (1 - duty)) if p >= duty else 0.0))
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
            fet, hp, sw = targ[f][k]
            ex = leg_ik(sk, pose, k, fet, hp)
            if ex > 1e-4 and sw == 0.0: print(f'GAIT stance over-reach {name} f{f} {k} {ex:.4f}')
            if k in g.get('tip_swing', ()): swing_leg(sk, pose, k, fet, sw)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                drops={k: [round(float(d.min()), 4), round(float(d.max()), 4)] for k, d in drops.items()})


def seg(t, a, b):
    """0 before a, smooth 0..1 between a and b, 1 after b"""
    return smooth((t - a) / (b - a)) if t > a else 0.0


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.5 s): standing; the raised tail draws 2 slow S-curves (wave travels up Tail1-3 with a lag, the tip curls a
    # little) - the main feature; 2 breaths; the head turns a little; ear twitches L 0.16, R 0.47, L small 0.78; the rump
    # answers the tail with a tiny sway. All periodic over the loop. (Cat Idle copy, kitten amplitudes.)
    idl = sp['idle']

    def ov_idle(p, t):
        breathe(sk, p, t, 0.0015, 2, 0.8)
        w = TAIL_WAVES * t
        s_wave(p, w, idl['tail'], idl['lag'], pitch=(2.0 * math.sin(TW * w + 0.5), 3.0 * math.sin(TW * w - 0.3),
                                                      6.0 * math.sin(TW * w - 1.1)))
        rot(p, 'Pelvis', z=-idl['hip'] * math.sin(TW * w))
        rot(p, 'Neck1', x=1.0 * math.sin(TW * t + 0.4), z=3.0 * math.sin(TW * t - 0.3))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=8.0 * math.sin(TW * t), y=6.0 * bump(t, 0.60, 0.10))
        ears(p, t, [('L', 0.16, 0.08, 1.0), ('R', 0.47, 0.08, 1.0), ('L', 0.78, 0.06, 0.6)], idl['ear'])
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.6 s): quick little lateral-sequence walk (HindL, FrontL, HindR, FrontR), paws near the midline, the back
    # undulates, head level, tail up with a lagged sway, ears bob. (Cat Walk copy, kitten tempo/step.)
    g = sp['gait']['Walk']

    def ov_walk(p, ph, pitch):
        u = g['spine']
        rot(p, 'Spine1', z=u * math.sin(TW * ph), x=g.get('spine_pitch', 0.6) * math.sin(2 * TW * ph))
        rot(p, 'Spine2', z=-u * math.sin(TW * ph - 0.4))
        rot(p, 'Neck1', x=-0.6 * pitch + 0.5 * math.sin(2 * TW * ph - 1.0), z=0.8 * u * math.sin(TW * ph - 0.9))
        rot(p, 'Head', x=-0.4 * pitch - 0.6 * math.sin(2 * TW * ph - 1.3), z=-0.6 * u * math.sin(TW * ph - 1.2))
        s_wave(p, ph, g['tail'], 0.12, pitch=(2.0 * math.sin(2 * TW * ph - 1.5), 0.0, 3.0 * math.sin(2 * TW * ph - 2.2)))
        rot(p, 'Ear.L', x=g['ear'] * math.sin(2 * TW * ph - 2.0)); rot(p, 'Ear.R', x=g['ear'] * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = gait_cat(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Pounce (2.0 s): stand -> crouch low (belly down, head low and forward, ears forward, tail low) -> butt wiggle (pelvis
    # yaw/roll, tail tip twitches) -> short lunge: the body springs forward and up, front paws leave the ground, reach and
    # land ahead, the hind paws hop along by the lunge -> holds the "prey" with the head down -> front paws hop
    # back with a little bounce of all four paws, the body returns -> stand. Loop: first pose == last pose; paws move only
    # in the air (no sliding).
    q = sp['pounce']; N = frames_of(dur['Pounce'][0]); t0, t1, t2, t3, t4, t5 = q['times']
    hind = ['HindL', 'HindR']; front = ['FrontL', 'FrontR']
    fr = []; worst_hind = -1.0; worst_front = -1.0
    for f in range(N):
        t = f / N
        air = math.sin(math.pi * (t - t2) / (t3 - t2)) if t2 <= t < t3 else 0.0
        back = math.sin(math.pi * (t - t4) / (t5 - t4)) if t4 <= t < t5 else 0.0
        swg = sw_weight((t - t2) / (t3 - t2)) if t2 <= t < t3 else sw_weight((t - t4) / (t5 - t4)) if t4 <= t < t5 else 0.0
        c = seg(t, t0, t1) * (1 - seg(t, t2, t3)) + 0.55 * seg(t, t2, t3) * (1 - seg(t, t4, t5))
        lunge = q['lunge'] * seg(t, t2, t3) * (1 - seg(t, t4, t5))
        paw = q['paw_fwd'] * seg(t, t2, t3) * (1 - seg(t, t4, t5))
        wig = 0.0
        if t1 <= t < t2:
            x = (t - t1) / (t2 - t1); wig = math.sin(TW * q['wiggles'] * x) * math.sin(math.pi * x)
        land = seg(t, t3 - 0.03, t3 + 0.03) * (1 - seg(t, t4, t4 + 0.08))
        pitch = q['crouch_pitch'] * c + q['air_pitch'] * air + q['land_pitch'] * land
        p = new_pose(sk)
        body(sk, p, (0, -lunge, -q['crouch'] * c + q['rise'] * air), pitch=pitch, roll=2.0 * wig, yaw=q['wiggle'] * wig)
        rot(p, 'Spine1', z=-0.5 * q['wiggle'] * wig)
        # head: low and forward in the crouch, eyes on the target (counter the body pitch), lifts in the air, down on the paws
        hl = q['head_low'] * c
        rot(p, 'Neck1', x=0.6 * hl - 0.6 * pitch - 10.0 * air + 8.0 * land)
        rot(p, 'Neck2', x=0.3 * hl)
        rot(p, 'Head', x=-0.7 * hl - 0.3 * pitch + 6.0 * land, z=3.0 * math.sin(TW * t))
        ear(p, up=6.0 * c, back=-10.0 * c)                                          # ears pricked forward
        # tail: S-wave when standing, low and straight in the crouch with a twitching tip, flicks up after the landing
        st = 1.0 - seg(t, t0, t1) * (1 - seg(t, t4, t5))
        s_wave(p, TAIL_WAVES * t, tuple(a * st for a in sp['idle']['tail']), sp['idle']['lag'])
        rot(p, 'Tail1', x=q['tail_low'] * c + 20.0 * land)
        rot(p, 'Tail3', z=14.0 * wig, x=8.0 * abs(wig))
        feet = {k: sk.feet[k] + Vector((0, -paw, q['paw_hop'] * air + 0.5 * q['paw_hop'] * back)) for k in front}
        hz = q['hind_hop'] * (air + back)                 # hind paws hop along with the body (move only in the air)
        for k in hind:
            worst_hind = max(worst_hind, leg_ik(sk, p, k, sk.feet[k] + Vector((0, -lunge, hz + sk.length[ar.LEGS[k][2]])),
                                                R(5.0) * (air + back)))
        for k in front:
            exf = leg_ik(sk, p, k, feet[k] + Vector((0, 0, sk.length[ar.LEGS[k][2]])))
            worst_front = max(worst_front, exf)
            swing_leg(sk, p, k, feet[k] + Vector((0, 0, sk.length[ar.LEGS[k][2]])), swg)
        fr.append(p)
    fr.append(copy_pose(fr[0]))
    info = dict(lunge_m=q['lunge'], paw_forward_m=q['paw_fwd'], crouch_m=q['crouch'], hind_reach_excess_m=round(worst_hind, 4),
                front_reach_excess_m=round(worst_front, 4))
    print('POUNCE', info)
    ev = [(round(t2 * N), 'Pounce', ''), (round(t3 * N), 'Land', 'Front')]
    out['Pounce'] = dict(frames=fr, events=ev, extra=dict(pounce=info))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
