# bull_clips.py - LIV-09 Bull clip set (planning/FarmAnimals/ANIMATIONS.md): Idle, Walk (heavy), Paw_Ground (scrapes the
# ground with a front hoof). Built on the shared _common/animal_anim helpers (imported read-only) and a copy of the Calf
# straight-leg gait (Calf/calf_clips.calf_gait: long Upper over a short Lower -> stance reach 0.998, the body bobs instead
# of the knees folding), with a roll parameter for the heavy walk.
import math
import numpy as np
from mathutils import Vector
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar
import animal_anim as _an
import animal_rig as _ar
from mathutils import Matrix, Euler

TW = 2 * math.pi

# ---------------- leg IK with rest offsets (horse legs are NOT collinear at rest: the hind gaskin and cannon meet at
# ~30 deg). animal_anim.leg_ik assumes collinear upper/lower/foot; this copy subtracts the rest angles of the lower bone
# in the upper frame (delta) and of the foot in the lower frame (eps), and picks the knee side from the rest pose.
# (copied from Horse/horse_clips.py) It replaces animal_anim.leg_ik in THIS process only (gait/plant call it by module global); the file is untouched.
_IK = {}


def setup_ik(sk):
    for k in LEGS:
        up, lo, ft, front = _ar.LEGS[k]
        cl = sk.rel[lo].to_3x3().col[1]; cf = sk.rel[ft].to_3x3().col[1]
        de = math.atan2(cl.z, cl.y); ep = math.atan2(cf.z, cf.y)
        t = sk.rest[up].inverted() @ sk.rest[ft].translation
        base = math.atan2(t.z, math.hypot(t.x, t.y))
        sgn = (1.0 if base > 0 else -1.0) if abs(base) > math.radians(1.0) else (1.0 if front else -1.0)
        _IK[k] = (de, ep, sgn)
        print(f'IK {k}: lower rest {math.degrees(de):.1f} deg, foot rest {math.degrees(ep):.1f} deg, knee side {sgn:+.0f}')
    _an.leg_ik = leg_ik_h


def leg_ik_h(sk, pose, leg, fetlock, hoof_pitch=0.0):
    up, lo, ft, front = _ar.LEGS[leg]; de, ep, sgn = _IK[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
    t = M0.inverted() @ Vector(fetlock)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    # rest knee angle: at rest the upper is at 0 and the knee/hock is on the side given by sgn
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


def ease(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def tail_idle(p, t, swish_at=0.58, amps=(5.0, 7.0, 9.0), swish=(22.0, 30.0, 38.0), cycles=2):
    """lagged sway + one S-shaped swish (cow/calf pattern)"""
    for i, (b, a) in enumerate(zip(('Tail1', 'Tail2', 'Tail3'), amps)):
        sw = 0.0; x = ((t - swish_at - 0.025 * i) % 1.0) / 0.20
        if x < 1.0: sw = math.sin(TW * x) * math.sin(math.pi * x)
        rot(p, b, x=(6.0 * math.sin(math.pi * x) * (1 - 0.4 * i)) if x < 1.0 else 0.0,
            z=a * math.sin(TW * (cycles * t) - 0.7 * (i + 1)) + swish[i] * sw)


def bull_gait(sk, sp, name, reach=0.998, lift_exp=0.6):
    """copy of Calf calf_gait (exact per-frame body drop, 3-frame average) + roll amplitude from the gait table"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    # max stance reach = REST hip -> fetlock distance (hind legs rest with a bent hock: never straighten past rest)
    Lrest = {k: (piv[k] - (sk.feet[k] + Vector((0, 0, sk.length[ar.LEGS[k][2]])))).length for k in LEGS}
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
            if True:     # stance AND swing targets must stay within the rest reach (no hock over-straightening in swing)
                up, lo, ft, front = ar.LEGS[k]; Lm = reach * Lrest[k]
                dy = y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
                gk = 'Front' if front else 'Hind'
                need[gk][f] = max(need[gk][f], (piv[k].z - (z + L3)) - vert)
        targ.append(row)
    drops = {}
    for gk, a in need.items():
        sm = np.maximum(a, (np.roll(a, 1) + a + np.roll(a, -1)) / 3)
        drops[gk] = sm + g['crouch']
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)), roll=g['roll'] * math.sin(2 * math.pi * ph))
        nod = g['nod'] * math.sin(2 * math.pi * (2 * ph) - 1.2)
        rot(pose, 'Neck1', x=nod * 0.6); rot(pose, 'Head', x=-nod * 0.3)
        rot(pose, 'Neck1', z=2.0 * math.sin(2 * math.pi * ph - 0.6))
        tail_sway(pose, ph, g['tail'], lag=0.1)
        ear(pose, up=g['ear'] * math.sin(2 * math.pi * 2 * ph - 2.0), back=-4.0 + g['ear'] * 0.5 * math.sin(2 * math.pi * 2 * ph - 2.6))
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik_h(sk, pose, k, fet, hp)
            level_foot(sk, pose, k)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                body_drop_m=dict(front=[round(float(drops['Front'].min()), 4), round(float(drops['Front'].max()), 4)],
                                                 hind=[round(float(drops['Hind'].min()), 4), round(float(drops['Hind'].max()), 4)]))


def level_foot(sk, pose, k):
    """remove the sideways (world X) tilt of a foot bone left by body roll / leg abduction (the IK only solves pitch):
    the wide bull hoof would otherwise dig one edge ~r*sin(roll) into the ground"""
    ft = ar.LEGS[k][2]; M = sk.fk(pose); Mf = M[ft].to_3x3(); cur = Mf.col[1].normalized()
    want = Vector((0.0, cur.y, cur.z)).normalized()
    Rw = cur.rotation_difference(want).to_matrix()
    Pm = (M[sk.parent[ft]] @ sk.rel[ft]).to_3x3()
    Bm = Euler(pose[ft][1], 'XYZ').to_matrix()
    Bn = Pm.inverted() @ Rw @ Pm @ Bm
    pose[ft][1] = list(Bn.to_euler('XYZ'))


# breathing copied from Horse/horse_clips.py (front legs are straight at rest: the shoulder must keep its height)
def breathe_h(sk, p, t, A, cycles=2):
    """breathing on the back line only: Spine1 and Spine2 counter-rotate so the front-leg joint keeps its height
    (front legs are straight at rest; a lifted shoulder would lift the hooves)"""
    l1 = sk.rest['Spine1'].translation.y - sk.rest['FrontUpper.L'].translation.y
    l2 = sk.rest['Spine2'].translation.y - sk.rest['FrontUpper.L'].translation.y
    k = l1 / l2 - 1.0; s_ = math.sin(TW * cycles * t)
    rot(p, 'Spine1', x=A * s_); rot(p, 'Spine2', x=-k * A * s_)


# ---------------- Paw_Ground ----------------
PAW = dict(leg='FrontL', strokes=((0.16, 0.44), (0.46, 0.74)), reach_fwd=0.14, drag_back=0.10, lift=0.13, dig=0.004,
           toe=18.0, drop=0.035, pitch=2.5, settle=(0.06, 0.82))


def paw_track(u):
    """hoof (dy, dz, toe pitch deg, contact) of the pawing leg on the loop phase u; per stroke: lift + reach forward (0-35%),
    strike and drag back along the ground (35-75%), lift and return under the shoulder (75-100%)"""
    for a, b in PAW['strokes']:
        if a <= u < b:
            s = (u - a) / (b - a)
            if s < 0.35:
                w = s / 0.35; return (-PAW['reach_fwd'] * ease(w), PAW['lift'] * math.sin(math.pi * w), PAW['toe'] * math.sin(math.pi * w), False)
            if s < 0.75:
                w = (s - 0.35) / 0.40; y = -PAW['reach_fwd'] + (PAW['reach_fwd'] + PAW['drag_back']) * ease(w)
                return (y, -PAW['dig'] * math.sin(math.pi * w), 0.0, True)
            w = (s - 0.75) / 0.25; y = PAW['drag_back'] * (1 - ease(w))
            return (y, 0.6 * PAW['lift'] * math.sin(math.pi * w), PAW['toe'] * 0.5 * math.sin(math.pi * w), False)
    return (0.0, 0.0, 0.0, False)


def paw_weight(u):
    """0..1: weight shifted back / head lowered over the pawing phase (eases in before stroke 1, out after stroke 2)"""
    a, b = PAW['settle']
    if u < a: return ease(u / a) if a > 0 else 1.0
    if u <= b: return 1.0
    return 1.0 - ease((u - b) / (1.0 - b))


def paw_pose(sk, base, u):
    p = copy_pose(base); w = paw_weight(u)
    sg = 1.0 if PAW['leg'].endswith('L') else -1.0           # weight shifts away from the pawing leg
    body(sk, p, (-0.015 * sg * w, 0.03 * w, -PAW['drop'] * w), pitch=PAW['pitch'] * w, roll=0.0)
    rot(p, 'Neck1', x=10 * w); rot(p, 'Neck2', x=4 * w); rot(p, 'Head', x=8 * w, z=-4 * w)
    planted = [k for k in LEGS if k != PAW['leg']]
    plant(sk, p, planted)
    for k in planted: level_foot(sk, p, k)
    dy, dz, toe, contact = paw_track(u)
    k = PAW['leg']; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
    leg_ik_h(sk, p, k, Vector((G.x, G.y + dy, dz + L3)), R(toe)); level_foot(sk, p, k)
    return p, planted, contact


def paw_probe_pose(sk):
    """bend-test pose: the deepest point of the drag (leg reached forward, weight back)"""
    setup_ik(sk)
    base = stand_pose(sk); a, b = PAW['strokes'][0]
    return paw_pose(sk, base, a + 0.40 * (b - a))[0]


def build_clips(sk, sp):
    setup_ik(sk)
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle (4 s): 2 deep breaths, heavy head sway + one snort toss, ear flicks, tail sway with one swish
    def ov_idle(p, t):
        breathe_h(sk, p, t, 0.6, 2)
        toss = flick(t, 0.70, 0.12)
        rot(p, 'Neck1', x=1.8 * math.sin(TW * t + 0.4) - 4.0 * toss, z=2.5 * math.sin(TW * t))
        rot(p, 'Head', x=-1.0 * math.sin(2 * TW * t + 1.0) - 5.0 * toss, z=3.0 * math.sin(TW * t - 0.3))
        fl = flick(t, 0.18, 0.10); fr_ = flick(t, 0.50, 0.10)
        rot(p, 'Ear.L', x=-2 + 2 * math.sin(TW * t) + 16 * fl, z=-(3 * math.sin(TW * t + 0.5)) + 22 * fl)
        rot(p, 'Ear.R', x=-2 + 2 * math.sin(TW * t + 1.7) + 16 * fr_, z=-(-3 * math.sin(TW * t + 2.2) + 22 * fr_))
        rot(p, 'Jaw', x=3.0 * toss)
        tail_idle(p, t, 0.36)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[(round(0.72 * frames_of(dur['Idle'][0])), 'Vocal', 'Snort')],
                       extra=dict(planted=list(LEGS)))

    # Walk (heavy): straight-leg gait copy, slow long cycle, more roll
    fr, ev, extra = bull_gait(sk, sp, 'Walk')
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # Paw_Ground (3 s loop): weight back + head down, two scrapes with the right front hoof, settle; tail swishes
    N = frames_of(dur['Paw_Ground'][0]); fr = []; contact_frames = []; ev = []
    prev_c = False
    for f in range(N):
        u = f / N; p, planted, c = paw_pose(sk, STAND, u)
        tail_idle(p, u, 0.50, amps=(6.0, 8.0, 10.0), swish=(26.0, 34.0, 42.0), cycles=2)
        ear(p, up=-4 * paw_weight(u), back=10 * paw_weight(u))
        rot(p, 'Jaw', x=2.0 * paw_weight(u) * (0.5 + 0.5 * math.sin(TW * 3 * u)))
        if c and not prev_c: ev.append((f, 'Paw', PAW['leg']))
        if c: contact_frames.append(f)
        prev_c = c; fr.append(p)
    fr.append(copy_pose(fr[0]))
    ev.append((round(0.60 * N), 'Vocal', 'Snort'))
    out['Paw_Ground'] = dict(frames=fr, events=sorted(ev),
                             extra=dict(planted=[k for k in LEGS if k != PAW['leg']],
                                        paw=dict(paw_leg=PAW['leg'], strokes=len(PAW['strokes']), drag_frames=len(contact_frames),
                                                 reach_fwd_m=PAW['reach_fwd'], drag_back_m=PAW['drag_back'], dig_m=PAW['dig'])))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
