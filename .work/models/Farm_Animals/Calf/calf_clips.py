# calf_clips.py - LIV-02 Calf minimum clip set (planning/FarmAnimals/ANIMATIONS.md): Idle, Walk, Lie_Idle.
# Built on the shared generators of _common/animal_anim.py (imported read-only, nothing modified there); the lying pose
# is calf-specific (short stubby legs: front legs folded under the chest, hind legs folded beside the belly).
import math
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS

FRONT_LEGS = ['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R']
HIND_LEGS = ['HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R']
BODY = ['Pelvis', 'Spine1', 'Spine2']


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def set_dir(sk, p, bone, wd):
    """point a bone along the world direction wd (minimal rotation from its rest direction, parent pose as in p)"""
    M = sk.fk(p); M0 = M[sk.parent[bone]] @ sk.rel[bone]
    dl = M0.to_3x3().inverted() @ Vector(wd).normalized()
    e = Vector((0, 1, 0)).rotation_difference(dl).to_euler('XYZ'); p[bone][1] = [e.x, e.y, e.z]


# Lying pose, rework (ANIMATION_FIXES 1). The calf leg is a fat (r 0.12 m) rigid column hinged 0.45 m up inside a body whose
# belly is 0.24 m above the ground, so with the belly ON the ground the hip/shoulder pivots are only 0.21 m high: a leg can
# only lie (a) folded forward in front of / under the chest or (b) beside the belly, pointing forward-outward.
# Front: upper 75 deg forward (limit), carpus folded 165 deg back -> brown knee in front of the chest, sock + hoof folded
# back under the chest. Hind: thigh+shank pointed forward-out-down (beside the rear belly), hock 50 deg, hoof turned so its
# side, not the sole, faces out. Values chosen from rendered candidates (side / 3/4 / front views).
BREATH_SPINE = 3.0          # breathe() spine factor in Lie_Idle -> chest top travel ~1.5 cm (printed, ANIMATION_FIXES: 1-2 cm)
# Round 2 (ANIMATION_FIXES 1, re-check): with rigid knee binding (rig_calf KNEE_MODE 'rigid') the folded front forearm
# stays a clean brown column (the side-weighted knee ring crumpled it into jagged 'claws'); the hind leg is folded
# further (hock 90) and points forward beside the belly so the sock + hoof tuck in instead of sticking out sideways.
# Round 3 (user: Calf_Lie_Idle 'ужасно'): the 165-deg folded knee read as a crumpled clump and the hind hoof as a black
# crescent on the flank. Now a 'sphinx' lie: front upper leg forward 72 deg (knee on the ground ahead of the chest), the
# forearm and hoof lying forward on the ground; hind leg folded beside the rear belly, hoof tucked in. Legs rest ON the
# ground (front +0.3 mm, hind +10 mm); all joints inside the rig limits except HindUpper (thigh forward-out 79 deg, limit widened to -95 for the calf in rig_calf.py), values chosen from rendered candidates (side / front / back).
LIE = dict(fa=72, fl=0, ff=-60, hdir=(0.1, -0.5, -0.08), hl=-3, hf=0)
import os as _os, json as _json
LIE.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in _json.loads(_os.environ.get('CALF_LIE', '{}')).items()})


def lie_pose_calf(sk, sp, c=LIE):
    """sternal lying pose; the body is lowered until its lowest vertex (belly) sits at z = 0"""
    p = new_pose(sk)
    body(sk, p, (0, 0.0, -0.24), pitch=0.0, roll=sp['poses']['lie_roll'])
    for s, sg in (('L', 1), ('R', -1)):
        rot(p, 'FrontUpper.' + s, x=-c['fa']); rot(p, 'FrontLower.' + s, x=c['fl']); rot(p, 'FrontFoot.' + s, x=c['ff'])
        d = Vector(c['hdir']); d.x *= sg; set_dir(sk, p, 'HindUpper.' + s, d)
        rot(p, 'HindLower.' + s, x=-c['hl']); rot(p, 'HindFoot.' + s, x=c['hf'])
    rot(p, 'Neck1', x=8); rot(p, 'Neck2', x=-4); rot(p, 'Head', x=-2)
    rot(p, 'Tail1', x=20); rot(p, 'Tail2', x=-12, z=14); rot(p, 'Tail3', z=16)
    belly_down(sk, p)
    return p


def belly_down(sk, p):
    """exact: lowest BODY vertex (Pelvis/Spine1/Spine2 skin) at z = 0 (the folded legs are checked separately)"""
    bm = sk.mask(BODY)
    for _ in range(3):
        z = sk.minz(p, bm)
        if abs(z) < 1e-5: break
        raise_body(sk, p, -z)


def best_lie(sk, sp):
    """LIE values; the front upper angle is raised (<= 75, the FrontUpper limit) until the folded front leg clears the
    ground by 5 mm (breathing moves the shoulders by a few mm)"""
    fm = sk.mask(FRONT_LEGS); c = dict(LIE)
    for fa in range(LIE['fa'], LIE['fa'] + 1):
        c['fa'] = fa; p = lie_pose_calf(sk, sp, c)
        if sk.minz(p, fm) >= 0.005: break
    p = lie_pose_calf(sk, sp, c)
    M = sk.fk(p); BP = sk.skin(M, sk.mask(BODY)); FP = sk.skin(M, sk.mask(FRONT_LEGS)); HP = sk.skin(M, sk.mask(HIND_LEGS))
    hu = [round(math.degrees(a), 1) for a in p['HindUpper.L'][1]]
    info = dict(c, belly_z=round(float(BP[:, 2].min()), 4), front_leg_z=round(float(FP[:, 2].min()), 4),
                hind_leg_z=round(float(HP[:, 2].min()), 4), hind_upper_euler_deg=hu)
    print('LIE', info)
    return p, info


def calf_gait(sk, sp, name, reach=0.998, smooth_drop=False, lift_exp=0.6):
    """copy of animal_anim.gait with the stance reach as a parameter: the calf leg is a long upper bone (0.28 m) over a
    very short lower one (0.095 m), so the shared 0.985 reach bent the 'knee' 35-55 deg in stance and the thick sock
    poked 4 cm through the ground. 0.998 keeps the legs nearly straight (pendulum legs, the body bobs instead)."""
    import numpy as np
    import animal_rig as ar
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            fl_ = g['flick'][0 if k.startswith('Front') else 1]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** lift_exp; hp = R(fl_) * math.sin(math.pi * s) ** 2
            row[k] = (Vector((G.x, y, z + L3)), hp, p < duty)
            if p < duty:
                up, lo, ft, front = ar.LEGS[k]; Lm = reach * (sk.length[up] + sk.length[lo])
                dy = y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        if smooth_drop:
            Fc = np.fft.rfft(a); Fc[4:] = 0; sm = np.fft.irfft(Fc, N)
            sm += max(0.0, float((a - sm).max()))
        else:   # exact per-frame need, lightly averaged over 3 frames (periodic) and never below the need
            sm = np.maximum(a, (np.roll(a, 1) + a + np.roll(a, -1)) / 3)
        drops[gk] = sm + g['crouch']
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)), roll=1.2 * math.sin(2 * math.pi * ph))
        nod = g['nod'] * math.sin(2 * math.pi * (2 * ph) - 1.2)
        rot(pose, 'Neck1', x=nod * 0.6); rot(pose, 'Head', x=-nod * 0.3)
        rot(pose, 'Neck1', z=1.5 * math.sin(2 * math.pi * ph - 0.6))
        tail_sway(pose, ph, g['tail'], lag=0.1)
        ear(pose, up=g['ear'] * math.sin(2 * math.pi * 2 * ph - 2.0), back=-4.0 + g['ear'] * 0.5 * math.sin(2 * math.pi * 2 * ph - 2.6))
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                body_drop_m=dict(front=[round(float(drops['Front'].min()), 4), round(float(drops['Front'].max()), 4)],
                                                 hind=[round(float(drops['Hind'].min()), 4), round(float(drops['Hind'].max()), 4)]))


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (3 s): 3 quick calf breaths, small head drift + look, alternating ear flicks, tail sway with one swish
    def ov_idle(p, t):
        TW = 2 * math.pi
        breathe(sk, p, t, 0.005, 3, 0.8)
        rot(p, 'Neck1', x=1.5 * math.sin(TW * t + 0.4)); rot(p, 'Head', x=-1.2 * math.sin(2 * TW * t + 1.0), z=4.0 * math.sin(TW * t))
        fl = flick(t, 0.12, 0.10) + 0.6 * flick(t, 0.78, 0.08); fr_ = flick(t, 0.44, 0.10)
        rot(p, 'Ear.L', x=-3 + 2 * math.sin(TW * t) + 18 * fl, z=-(4 * math.sin(TW * t + 0.5)) + 30 * fl)
        rot(p, 'Ear.R', x=-3 + 2 * math.sin(TW * t + 1.7) + 18 * fr_, z=-(-4 * math.sin(TW * t + 2.2) + 30 * fr_))
        for i, (b, a) in enumerate((('Tail1', 6.0), ('Tail2', 8.0), ('Tail3', 10.0))):
            sw = 0.0; x = ((t - 0.58 - 0.025 * i) % 1.0) / 0.20
            if x < 1.0: sw = math.sin(TW * x) * math.sin(math.pi * x)
            rot(p, b, x=6.0 * math.sin(math.pi * x) * (1 - 0.4 * i) if x < 1.0 else 0.0,
                z=a * math.sin(TW * (2 * t) - 0.7 * (i + 1)) + (22 + 8 * i) * sw)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Walk: shared gait generator with the calf gait table (short quick steps, diagonal sequence)
    fr, ev, extra = calf_gait(sk, sp, 'Walk'); out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Lie_Idle (3.5 s): lying pose, slow breathing, head bob, ear flicks, lazy tail
    LIE, info = best_lie(sk, sp)

    def ov_lie(p, t):
        TW = 2 * math.pi
        breathe(sk, p, t, 0.0, 2, BREATH_SPINE)
        rot(p, 'Neck1', x=1.5 * math.sin(TW * t)); rot(p, 'Head', x=-1.5 * math.sin(TW * t + 0.8), z=3.0 * math.sin(TW * t + 0.3))
        ear(p, up=-6 + 14 * flick(t, 0.30, 0.10), back=6 + 12 * flick(t, 0.66, 0.10))
        tail_sway(p, t, (0, 4, 6))
        belly_down(sk, p)                       # the belly stays on the ground every frame; the chest/back rise and fall
    fr = loop_static('Lie_Idle', LIE, ov_lie, planted=[])
    sm = sk.mask(['Spine2']); tops = [float(sk.skin(sk.fk(q), sm)[:, 2].max()) for q in fr]
    bm = sk.mask(BODY); bel = [sk.minz(q, bm) for q in fr]
    info['breath_chest_top_m'] = round(max(tops) - min(tops), 4); info['belly_z_range_m'] = [round(min(bel), 4), round(max(bel), 4)]
    print('LIE breathing: chest top travel', info['breath_chest_top_m'], 'belly z', info['belly_z_range_m'])
    out['Lie_Idle'] = dict(frames=fr, events=[], extra=dict(lie=info))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
