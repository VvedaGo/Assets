# puppy_clips.py - PET-03 Puppy clips (ANIMATIONS.md: Idle "wags its tail", Trot "trots", Play_Bow "drops onto the
# front legs inviting play"). Copied from ../Dog/dog_clips.py (read-only there): setup_ik / leg_ik_h (rest-offset leg
# IK), flick, wag, gait_dog (overlay before the leg IK). Shared helpers from _common/animal_anim.py are read-only.
import math
import numpy as np
from mathutils import Vector, Matrix
from animal_anim import *
from animal_anim import R, LEGS
import animal_anim as _an
import animal_rig as ar

TW = 2 * math.pi
WAGS = 9                    # Idle: 9 wags in 3.0 s (3 Hz, puppy), integer -> closed loop
_IK = {}


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


def wag(p, ph, amps, lag, lift=(0.0, 0.0, 0.0)):
    """lateral tail wag along Tail1-3: amplitude grows to the tip, each bone lags the previous by `lag` of a cycle"""
    for i, (b, a) in enumerate(zip(('Tail1', 'Tail2', 'Tail3'), amps)):
        rot(p, b, x=lift[i], z=a * math.sin(TW * (ph - lag * i)))


def gait_dog(sk, sp, name, overlay):
    """copy of the Goat gait (animal_anim.gait + overlay hook before the leg IK)"""
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
        bob = g['bob'] * math.cos(2 * TW * ph)
        body(sk, pose, (0, 0, -dh + bob), pitch=math.degrees(math.asin((df - dh) / span)), roll=g['roll'] * math.sin(TW * ph))
        overlay(pose, ph, math.degrees(math.asin((df - dh) / span)))
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drops={k: [round(float(x), 4) for x in d] for k, d in drops.items()})




FRONT_BODY = ['Spine2', 'Ruff', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R']
FRONT_LEGS = ['FrontL', 'FrontR']; HIND_LEGS = ['HindL', 'HindR']


def bow_body(sk, p, b, P, rise, u):
    """chest down: pelvis pitched nose-down by P (deg), rump up by rise*u; neck/head counter-pitched so the face looks
    ahead, ruff hangs, ears perked"""
    hip0 = (sk.rest['HindUpper.L'].translation + sk.rest['HindUpper.R'].translation) / 2
    body(sk, p, (0, 0, 0), pitch=P)                                      # pitch about the hips: hind legs unchanged
    M = sk.fk(p); hip = (M['HindUpper.L'].translation + M['HindUpper.R'].translation) / 2
    body(sk, p, tuple(hip0 - hip + Vector((0, 0, rise * u))), pitch=P)
    for bn, w in (('Neck1', 0.40), ('Neck2', 0.30), ('Head', 0.30)): rot(p, bn, x=-w * P * b['head_up'])
    rot(p, 'Ruff', x=-0.3 * P)
    ear(p, up=12 * u, back=-6 * u)


def solve_bow(sk, b):
    """largest pitch (0.5 deg steps) that keeps chest/ruff/head >= chest_clear + bounce above the ground with the front
    paws paw_fwd ahead, the elbow < 165 deg and the hind legs not overstretched (rump rise tried 0..15 mm)"""
    mask = sk.mask(FRONT_BODY)
    feet = {k: sk.feet[k] + Vector((0, -b['paw_fwd'], 0)) for k in FRONT_LEGS}
    best = (0.0, 0.0); tab = []
    for i in range(1, 91):
        P = 0.5 * i; ok = None
        for rise in b['rises']:
            p = new_pose(sk); bow_body(sk, p, b, P, rise, 1.0)
            ex = max(leg_ik(sk, p, k, sk.feet[k] + Vector((0, 0, sk.length[ar.LEGS[k][2]]))) for k in HIND_LEGS)
            if ex > -0.0005:
                if i == 1: tab.append(('hind', P, rise, round(ex, 4)))
                continue
            exf = max(leg_ik(sk, p, k, feet[k] + Vector((0, 0, sk.length[ar.LEGS[k][2]]))) for k in FRONT_LEGS)
            z = sk.minz(p, mask); elbow = max(math.degrees(p[ar.LEGS[k][1]][1][0]) for k in FRONT_LEGS)
            if i % 10 == 0 or i == 1: tab.append((P, rise, round(z, 3), round(elbow, 1), round(exf, 3), round(ex, 4)))
            if z >= b['chest_clear'] + b['bounce'] and elbow < 165.0:
                ok = (P, rise); break
        if ok is None: break
        best = ok
    print('BOW search (pitch, rise, chest z, elbow, front reach)', tab, '-> best', best)
    return best, feet


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    setup_ik(sk)
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3.0 s): the plume tail wags fast 9x (3 Hz) with a lag along Tail1-3 (main feature), the whole rump wiggles
    # against it (Pelvis + Spine1 yaw), 2 breaths, head turns/tilts a little, the ears twitch in turn. All periodic.
    idl = sp['idle']

    def ov_idle(p, t):
        breathe(sk, p, t, 0.002, 2, 1.0)
        w = WAGS * t
        wag(p, w, idl['wag'], idl['lag'], lift=(6.0, 3.0, 1.0))
        rot(p, 'Pelvis', z=-idl['hip'] * math.sin(TW * (w + 0.25)))
        rot(p, 'Spine1', z=0.5 * idl['hip'] * math.sin(TW * (w + 0.25)))
        rot(p, 'Neck1', x=1.0 * math.sin(TW * t + 0.4), z=3.0 * math.sin(TW * t - 0.3))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=6.0 * math.sin(TW * t), y=5.0 * bump(t, 0.62, 0.12))
        rot(p, 'Ruff', x=0.8 * math.sin(2 * TW * t - 0.5))
        fl = flick(t, 0.18, 0.09) + 0.5 * flick(t, 0.83, 0.07); fr_ = flick(t, 0.52, 0.09)
        rot(p, 'Ear.L', x=-idl['ear'] * fl + 1.5 * math.sin(TW * t), z=8 * fl)
        rot(p, 'Ear.R', x=-idl['ear'] * fr_ + 1.5 * math.sin(TW * t + 1.7), z=-8 * fr_)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Trot (0.5 s): bouncy diagonal trot (HindL+FrontR, HindR+FrontL together, duty 0.45 -> short suspension), body bobs
    # twice per cycle, head held level, the raised plume bounces and sways with a lag, the ruff and the ears bounce.
    g = sp['gait']['Trot']

    def ov_trot(p, ph, pitch):
        rot(p, 'Neck1', x=-0.6 * pitch + 1.0 * math.sin(2 * TW * ph - 1.0), z=1.0 * math.sin(TW * ph - 0.6))
        rot(p, 'Head', x=-0.4 * pitch - 1.2 * math.sin(2 * TW * ph - 1.3), z=-0.8 * math.sin(TW * ph - 0.9))
        wag(p, ph, g['tail'], 0.10, lift=tuple(g['tail_bounce'] * math.sin(2 * TW * ph - 1.6 - 0.5 * i) for i in range(3)))
        rot(p, 'Ruff', x=g['ruff'] * math.sin(2 * TW * ph - 1.9))
        rot(p, 'Ear.L', x=g['ear'] * math.sin(2 * TW * ph - 2.0)); rot(p, 'Ear.R', x=g['ear'] * math.sin(2 * TW * ph - 2.3))
    fr, ev, extra = gait_dog(sk, sp, 'Trot', ov_trot)
    out['Trot'] = dict(frames=fr, events=ev, extra=extra)

    # Play_Bow (2.5 s): stand + wag -> the front paws hop forward and the chest drops onto the front legs (rump stays up,
    # tail high, head up looking ahead) -> hold with a very fast wag, two little chest bounces and a cocked head ->
    # hop back onto straight front legs -> stand + wag. Hind paws never move; front paws only move in the air.
    b = sp['bow']; N = frames_of(dur['Play_Bow'][0])
    (Pm, rise), bow_feet = solve_bow(sk, b)
    t_dn0, t_dn1, t_up0, t_up1 = b['times']
    fr = []
    for f in range(N):
        t = f / N; s = None
        if t < t_dn0 or t >= t_up1: u = 0.0; fw = 0.0
        elif t < t_dn1: s = (t - t_dn0) / (t_dn1 - t_dn0); u = smooth(s); fw = smooth(s)
        elif t < t_up0: u = 1.0; fw = 1.0
        else: s = (t - t_up0) / (t_up1 - t_up0); u = 1.0 - smooth(s); fw = 1.0 - smooth(s)
        hop = b['hop'] * math.sin(math.pi * s) if s is not None else 0.0
        bnc = 0.0
        if t_dn1 <= t < t_up0:
            x = (t - t_dn1) / (t_up0 - t_dn1); bnc = math.sin(math.pi * x) ** 2 * abs(math.sin(2 * math.pi * x))
        P = Pm * u * (1.0 - b['bounce_share'] * bnc)
        p = new_pose(sk); bow_body(sk, p, b, P, rise, u)
        tilt = b['tilt'] * u * math.sin(math.pi * min(1.0, max(0.0, (t - t_dn1 - 0.04) / (t_up0 - t_dn1 - 0.08))))
        rot(p, 'Head', y=tilt, z=4.0 * math.sin(TW * t))
        wg = tuple(a0 + (a1 - a0) * u for a0, a1 in zip(sp['idle']['wag'], b['wag']))
        wag(p, b['wags'] * t, wg, 0.10, lift=(b['tail_up'] * u + 6.0, 3.0, 1.0))
        rot(p, 'Pelvis', z=-1.5 * math.sin(TW * (b['wags'] * t + 0.25)))
        breathe(sk, p, t, 0.0, 2, 0.6)
        feet = {k: sk.feet[k] + Vector((0, -b['paw_fwd'] * fw, hop)) for k in FRONT_LEGS}
        plant(sk, p, HIND_LEGS); plant(sk, p, FRONT_LEGS, feet)
        fr.append(p)
    fr.append(copy_pose(fr[0]))
    ev = [(round(t_dn0 * N), 'Takeoff', 'Front'), (round(t_dn1 * N), 'Land', 'Front'), (round(t_up0 * N), 'Takeoff', 'Front'),
          (round(t_up1 * N), 'Land', 'Front')]
    out['Play_Bow'] = dict(frames=fr, events=ev, extra=dict(bow=dict(pitch=Pm, rump_rise=rise, paw_fwd=b['paw_fwd'])))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
