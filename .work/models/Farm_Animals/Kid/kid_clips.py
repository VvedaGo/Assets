# kid_clips.py - LIV-13 Kid clips (ANIMATIONS.md: Idle "stands", Walk "walks", Play_Hop "playful hop").
# Copied from ../Lamb/lamb_clips.py (read-only): same Idle / Walk / Play_Hop builders; the 2-bone lamb tail is replaced by
# the Goat's 3-bone upright tail flick (../Goat/goat_clips.py tail_flick), "wool" = small spine bounce.
# Shared helpers from _common/animal_anim.py are imported read-only; gait() is copied here with an overlay hook that runs
# BEFORE the leg IK (head bob, lagged wool bounce on Spine1/Spine2, ears, 2-bone tail), so the feet stay planted.
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi

# The kid mesh bends at a LOW joint (Lower pivot 0.10 m, a fetlock-like joint; Lower = 4.5 cm pastern): every leg folds with
# the pastern going BACK (knee-forward branch of the IK) and, off the ground, the hoof follows the pastern (foot local
# pitch >= FOOT_FOLLOW) instead of being held vertical (that read as a broken ankle). Runtime-only change of the leg table
# in this process (animal_rig.py is not edited).
for _k in ('HindL', 'HindR'):
    ar.LEGS[_k] = ar.LEGS[_k][:3] + (True,)
FOOT_FOLLOW = R(-12.0)


_FMASK = {}


def leg_ik_f(sk, pose, k, fet, hp, follow):
    """IK + hoof follow off the ground; the follow is backed off (bisection) where the curled hoof block would dip below
    the ground (near lift-off / touch-down)"""
    ex = leg_ik(sk, pose, k, fet, hp)
    if follow:
        ft = ar.LEGS[k][2]; a0 = pose[ft][1][0]; a1 = max(a0, FOOT_FOLLOW)
        if a1 != a0:
            m = _FMASK.get(ft)
            if m is None: m = _FMASK[ft] = sk.mask([ft])
            pose[ft][1][0] = a1
            if sk.minz(pose, m) < 0.0:
                lo, hi = 0.0, 1.0
                for _ in range(12):
                    u = (lo + hi) / 2; pose[ft][1][0] = a0 + (a1 - a0) * u
                    if sk.minz(pose, m) < 0.0: hi = u
                    else: lo = u
                pose[ft][1][0] = a0 + (a1 - a0) * lo
    return ex


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def gait_lamb(sk, sp, name, overlay):
    """copy of animal_anim.gait (feet move back at speed in stance, swing arcs, body height per girdle from reach)
    with overlay(pose, phase) applied before the leg IK and a 2-bone tail"""
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
                z = g['lift'] * math.sin(math.pi * s) ** 1.3; hp = R(fl) * math.sin(math.pi * s) ** 2
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
            leg_ik_f(sk, pose, k, fet, hp, not st)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N, drops={k: [round(float(x), 4) for x in d] for k, d in drops.items()})



def tail_flick(p, b, base=0.0):
    """short upright goat tail (copy of ../Goat/goat_clips.tail_flick): side flicks along Tail1-3 growing to the tip"""
    rot(p, 'Tail1', x=-3 * abs(b) + base, z=12 * b); rot(p, 'Tail2', z=16 * b); rot(p, 'Tail3', z=20 * b)


def hop_curve(t, H):
    """Play_Hop body height (m above rest), airborne flag, air phase u: push from the squash (ease-in), ballistic arc,
    landing squash (fast decel); periodic in t with zero slope at the loop seam (t = 0 = bottom of the squash)"""
    t0, t1, sq, hp = H['takeoff'], H['land'], H['squash'], H['height']
    if t < t0:
        return -sq * math.cos(0.5 * math.pi * (t / t0) ** 2), False, 0.0
    if t <= t1:
        u = (t - t0) / (t1 - t0); return 4 * hp * u * (1 - u), True, u
    x = (t - t1) / (1 - t1)
    return -sq * math.sin(0.5 * math.pi * (1 - (1 - x) ** 2)), False, 1.0


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3 s): 2 slow breaths (body + Spine pitch), small head drift, ear flicks in turn (L 0.15, R 0.48, L twitch 0.80),
    # tail wiggle with a quick burst at 0.62; all terms periodic -> closed loop
    def ov_idle(p, t):
        breathe(sk, p, t, 0.004, 2, 1.3)
        rot(p, 'Neck1', x=1.5 * math.sin(TW * t + 0.4)); rot(p, 'Head', x=-1.2 * math.sin(2 * TW * t + 1.0), z=4.0 * math.sin(TW * t))
        fl = flick(t, 0.15, 0.10) + 0.5 * flick(t, 0.80, 0.08); fr_ = flick(t, 0.48, 0.10)
        rot(p, 'Ear.L', x=-2 + 2 * math.sin(TW * t) + 16 * fl, z=-(3 * math.sin(TW * t + 0.5)) + 26 * fl)
        rot(p, 'Ear.R', x=-2 + 2 * math.sin(TW * t + 1.7) + 16 * fr_, z=-(-3 * math.sin(TW * t + 2.2) + 26 * fr_))
        x = ((t - 0.62) % 1.0) / 0.16; burst = math.sin(2 * TW * x) * math.sin(math.pi * x) if x < 1.0 else 0.0
        tail_flick(p, 1.1 * burst + 0.12 * math.sin(TW * 3 * t), base=2 * math.sin(TW * 2 * t))
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk (0.7 s): quick short lateral-sequence steps; head bob twice per cycle, wool bounce with lag, ears and tail swing
    g = sp['gait']['Walk']

    def ov_walk(p, ph):
        nod = g['nod'] * math.sin(TW * 2 * ph - 1.2)
        rot(p, 'Neck1', x=0.6 * nod, z=2.0 * math.sin(TW * ph - 0.6)); rot(p, 'Head', x=-0.3 * nod)
        rot(p, 'Spine1', x=g['wool'] * math.sin(TW * 2 * ph - 2.0)); rot(p, 'Spine2', x=-0.8 * g['wool'] * math.sin(TW * 2 * ph - 2.6))
        tail_flick(p, 0.5 * math.sin(TW * 2 * ph - 1.5), base=2.0 * math.sin(TW * 2 * ph))
        ear(p, up=g['ear'] * math.sin(TW * 2 * ph - 2.0), back=-2.0 + 0.5 * g['ear'] * math.sin(TW * 2 * ph - 2.6))
    fr, ev, extra = gait_lamb(sk, sp, 'Walk', ov_walk)
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Play_Hop (1.0 s loop, in place): squash -> push (all four planted, IK) -> all four feet leave the ground together,
    # legs tucked, body arc 0.10 m with nose-up/nose-down pitch -> land on all fours -> squash 4.2 cm. Ears and tail lag:
    # dip on the push, float up in the air, flop down on the landing; head counter-nods.
    H = sp['hop']; N = frames_of(H['T'])

    def ov_hop(p, t):
        e_up = 20 * bump(t, 0.50, 0.20) - 24 * bump(t, 0.80, 0.13) - 10 * bump(t, 0.15, 0.10)
        ear(p, up=e_up, back=4 * bump(t, 0.45, 0.2))
        tail_flick(p, 0.6 * math.sin(TW * 2 * t), base=12 * bump(t, 0.52, 0.20) - 14 * bump(t, 0.84, 0.13))
        rot(p, 'Tail2', x=8 * bump(t, 0.58, 0.20) - 10 * bump(t, 0.88, 0.13))
        rot(p, 'Neck1', x=-6 * bump(t, 0.38, 0.18) + 8 * bump(t, 0.82, 0.14)); rot(p, 'Head', x=-3 * bump(t, 0.45, 0.2) + 4 * bump(t, 0.86, 0.12))
        rot(p, 'Spine1', x=3 * bump(t, 0.88, 0.14) - 2 * bump(t, 0.45, 0.2)); rot(p, 'Spine2', x=-2 * bump(t, 0.88, 0.14))
    fr = []; heights = []; air_frames = []
    for f in range(N):
        t = f / N; h, air, u = hop_curve(t, H); s = math.sin(math.pi * u) if air else 0.0
        pose = new_pose(sk)
        body(sk, pose, (0, 0, h), pitch=-H['pitch'] * math.sin(TW * u) if air else 0.0)
        ov_hop(pose, t)
        if not air:
            plant(sk, pose)
        else:
            air_frames.append(f)
            for k in LEGS:
                G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]; front = k.startswith('Front')
                tgt = Vector((G.x, G.y + (0.02 if front else -0.02) * s, h + H['tuck'] * s + L3))
                leg_ik_f(sk, pose, k, tgt, R(45 if front else 20) * s, True)
        fr.append(pose); heights.append(round(h, 4))
    fr.append(copy_pose(fr[0]))
    t_off = round(H['takeoff'] * N); t_land = round(H['land'] * N)
    out['Play_Hop'] = dict(frames=fr, events=[(t_off, 'Footstep', 'Takeoff'), (t_land, 'Footstep', 'Land')],
                           extra=dict(air_frames=[air_frames[0], air_frames[-1]], peak=max(heights), squash=min(heights),
                                      front_foot_x=[round(math.degrees(q['FrontFoot.L'][1][0]), 1) for q in fr[:N]]))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
