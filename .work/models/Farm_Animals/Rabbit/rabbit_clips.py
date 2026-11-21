# rabbit_clips.py - SML-01 Rabbit clips (ANIMATIONS.md: Idle "twitches nose and ears", Hop "hops", Nibble "nibbles food").
# Shared helpers from _common/animal_anim.py are imported read-only (pose dicts, FK/IK, plant, chew, breathe).
# Hop pattern after ../Lamb/lamb_clips.py (Play_Hop), but a bounding rabbit hop: hind push, front legs tucked then
# reaching, front paws land first, hind feet after; root in place, feet return to their rest spots.
import math
from mathutils import Vector, Matrix
from animal_anim import *
from animal_anim import R, LEGS
import animal_rig as ar

TW = 2 * math.pi
GROUND_TOL = -0.002          # lowest vertex limit: pack -1 cm (Cow, 2.3 m) scaled to the 0.45 m rabbit


def flick(t, c, w):
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def ears(p, fl=0.0, ol=0.0, sl=0.0, fr=0.0, or_=0.0, sr=0.0):
    """rabbit ears (upright bones, local X = world +X): f = tilt forward (+) / back (-), o = splay outwards,
    s = swivel the opening outwards (about the ear axis); L and R independent"""
    rot(p, 'Ear.L', x=fl, y=sl, z=-ol); rot(p, 'Ear.R', x=fr, y=-sr, z=or_)


def _herm(p0, p1, m0, m1, u, dt):
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * dt * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * dt * m1


def pcurve(keys, t):
    """periodic Catmull-Rom through keys [(t, v)] (t in [0, 1)) -> value at phase t (C1, closed loop)"""
    E = [(a - 1, v) for a, v in keys] + list(keys) + [(a + 1, v) for a, v in keys]
    t = t % 1.0
    k = max(i for i in range(len(E) - 1) if E[i][0] <= t)
    (ta, a), (tb, b) = E[k], E[k + 1]
    ma = (b - E[k - 1][1]) / (tb - E[k - 1][0]); mb = (E[k + 2][1] - a) / (E[k + 2][0] - ta)
    return _herm(a, b, ma, mb, (t - ta) / (tb - ta), tb - ta)


def air(keys, t):
    """flight curve of one foot: keys [(t, dy, lift, pitch_deg)] from lift-off to touch-down (zero at both ends, zero
    end tangents); outside the interval the foot is planted -> (0, 0, 0)"""
    t0, t1 = keys[0][0], keys[-1][0]
    if not (t0 < t < t1): return 0.0, 0.0, 0.0
    k = max(i for i in range(len(keys) - 1) if keys[i][0] <= t)
    out = []
    for c in (1, 2, 3):
        (ta, a), (tb, b) = (keys[k][0], keys[k][c]), (keys[k + 1][0], keys[k + 1][c])
        ma = 0.0 if k == 0 else (b - keys[k - 1][c]) / (tb - keys[k - 1][0])
        mb = 0.0 if k + 1 == len(keys) - 1 else (keys[k + 2][c] - a) / (keys[k + 2][0] - ta)
        out.append(_herm(a, b, ma, mb, (t - ta) / (tb - ta), tb - ta))
    out[1] = max(out[1], 0.0)
    return tuple(out)


# ---------------- Hop timing (phase of the 0.6 s loop) ----------------
HOP_T = dict(front_off=0.15, hind_off=0.30, front_on=0.60, hind_on=0.70)
HOP_H = [(0.00, -0.008), (0.15, -0.005), (0.30, 0.002), (0.45, 0.100), (0.60, 0.024), (0.70, 0.000), (0.85, -0.009)]
HOP_P = [(0.00, -4.0), (0.15, -7.0), (0.30, -12.0), (0.45, -2.0), (0.60, 8.0), (0.70, -1.0), (0.85, -4.0)]   # + nose down
FRONT_AIR = [(0.15, 0.0, 0.0, 0.0), (0.26, 0.016, 0.036, 22.0), (0.40, 0.010, 0.045, 50.0), (0.52, -0.030, 0.022, -10.0),
             (0.60, 0.0, 0.0, 0.0)]
HIND_AIR = [(0.30, 0.0, 0.0, 0.0), (0.40, 0.035, 0.018, 30.0), (0.55, -0.005, 0.040, 10.0), (0.65, -0.010, 0.012, 0.0),
            (0.70, 0.0, 0.0, 0.0)]


def foot_flat(sk, pose, k, pitch_deg=0.0):
    """set the foot's local rotation so its WORLD orientation = rest orientation pitched by pitch_deg (+ = toe down).
    animal_anim.leg_ik keeps only the pitch; its abduction (beta) would roll the wide rabbit paws into the ground."""
    up, lo, ft, _ = ar.LEGS[k]
    M = sk.fk(pose)
    Pm = (M[lo] @ sk.rel[ft]).to_3x3()
    want = Matrix.Rotation(R(pitch_deg), 3, 'X') @ sk.rest[ft].to_3x3()
    pose[ft][1] = list((Pm.inverted() @ want).to_euler('XYZ'))


def plant_flat(sk, pose, legs=None):
    legs = LEGS if legs is None else legs
    plant(sk, pose, legs)
    for k in legs: foot_flat(sk, pose, k)


def nibble_arms(sk, pose, jaw_off):
    """front legs by FK (the shared IK is built for legs pointing down): grid search of shoulder/elbow pitch so the
    fetlock comes to the jaw + jaw_off (side view plane); same angles mirrored on the right; returns (a, b, dist)"""
    best = None; base = copy_pose(pose)
    for a in [-115 + 2.5 * i for i in range(47)]:
        for b in [-2.5 + 2.5 * j for j in range(70)]:
            q = copy_pose(base)
            for s in ('L', 'R'):
                q['FrontUpper.' + s][1] = [R(a), 0.0, 0.0]; q['FrontLower.' + s][1] = [R(b), 0.0, 0.0]
            M = sk.fk(q); J = M['Jaw'].translation; F = M['FrontFoot.L'].translation
            d = math.hypot(F.y - (J.y + jaw_off[1]), F.z - (J.z + jaw_off[2]))
            if best is None or d < best[2]: best = (a, b, d)
    return best


def foot_z(sk, pose, k):
    M = sk.fk(pose); return (M[ar.LEGS[k][2]].translation.z - sk.length[ar.LEGS[k][2]])


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant_flat(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # ---- Idle (3 s): alert stand, 3 breaths, small head turn, 3 nose-twitch bursts, ears move independently
    # (L flicks forward, R tilts back, L swivels out, R swivels out), pom-pom wiggle bursts; all terms periodic
    STAND = new_pose(sk); body(sk, STAND, (0, 0, -0.006)); plant_flat(sk, STAND)

    def ov_idle(p, t):
        breathe(sk, p, t, 0.0015, 3, 1.0)
        rot(p, 'Neck1', x=1.0 * math.sin(TW * t + 0.4), z=4.0 * math.sin(TW * t))
        rot(p, 'Head', x=-1.5 * math.sin(2 * TW * t + 1.0), z=4.0 * math.sin(TW * t - 0.6))
        tw = flick(t, 0.08, 0.16) + flick(t, 0.42, 0.14) + flick(t, 0.74, 0.16)
        rot(p, 'Nose', x=7 * tw * math.sin(15 * TW * t), z=3 * tw * math.sin(15 * TW * t + 1.2))
        rot(p, 'Jaw', x=2.0 * tw * (0.5 - 0.5 * math.cos(15 * TW * t)))
        ears(p, fl=-3 + 2 * math.sin(TW * t) + 14 * flick(t, 0.20, 0.16) - 6 * flick(t, 0.86, 0.12),
             ol=3 + 2 * math.sin(TW * t + 0.5), sl=26 * flick(t, 0.55, 0.20),
             fr=-3 + 2 * math.sin(TW * t + 1.7) - 16 * flick(t, 0.32, 0.22),
             or_=3 + 2 * math.sin(TW * t + 2.2) + 8 * flick(t, 0.32, 0.22), sr=24 * flick(t, 0.78, 0.18))
        wig = flick(t, 0.60, 0.14) + 0.6 * flick(t, 0.12, 0.10)
        rot(p, 'Tail1', x=3 * math.sin(TW * t), z=14 * wig * math.sin(15 * TW * t))
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # ---- Hop (0.6 s loop, in place)
    N = frames_of(dur['Hop'][0]); fr = []; info = []

    def ov_hop(p, t, pitch):
        rot(p, 'Spine1', x=-4 * bump(t, 0.30, 0.15) + 5 * bump(t, 0.64, 0.12))
        rot(p, 'Spine2', x=-3 * bump(t, 0.30, 0.15) + 4 * bump(t, 0.64, 0.12))
        rot(p, 'Neck1', x=-0.25 * pitch); rot(p, 'Head', x=-0.30 * pitch + 3 * bump(t, 0.70, 0.12))
        # ears lag: blown back on the push/rise, float at the top, flop forward and out after the landing
        eL = -22 * bump(t, 0.40, 0.16) + 18 * bump(t, 0.74, 0.14) - 4
        eR = -20 * bump(t, 0.43, 0.16) + 20 * bump(t, 0.77, 0.14) - 4
        ears(p, fl=eL, ol=4 + 10 * bump(t, 0.76, 0.14), fr=eR, or_=4 + 12 * bump(t, 0.79, 0.14))
        rot(p, 'Tail1', x=22 * bump(t, 0.34, 0.14) - 10 * bump(t, 0.74, 0.12), z=6 * math.sin(TW * 2 * t))
        rot(p, 'Nose', x=3 * math.sin(TW * 3 * t))
    for f in range(N):
        t = f / N; h = pcurve(HOP_H, t); pitch = pcurve(HOP_P, t)
        pose = new_pose(sk); body(sk, pose, (0, 0, h), pitch=pitch); ov_hop(pose, t, pitch)
        row = {}
        for k in LEGS:
            dy, lift, fp = air(FRONT_AIR if k.startswith('Front') else HIND_AIR, t)
            G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            leg_ik(sk, pose, k, Vector((G.x, G.y + dy, lift + L3)), R(fp)); foot_flat(sk, pose, k, fp)
        for k in LEGS: row[k] = round(foot_z(sk, pose, k), 4)
        fr.append(pose); info.append(dict(f=f, h=round(h, 4), pitch=round(pitch, 1), **row))
    fr.append(copy_pose(fr[0]))
    ev = [(round(HOP_T['front_off'] * N), 'Footstep', 'FrontOff'), (round(HOP_T['hind_off'] * N), 'Footstep', 'Takeoff'),
          (round(HOP_T['front_on'] * N), 'Footstep', 'LandFront'), (round(HOP_T['hind_on'] * N), 'Footstep', 'LandHind')]
    airborne = [i['f'] for i in info if min(i[k] for k in LEGS) > 0.003]
    def planted(k, t):
        a, b = (HOP_T['front_off'], HOP_T['front_on']) if k.startswith('Front') else (HOP_T['hind_off'], HOP_T['hind_on'])
        return not (a < t < b)
    stance_lift = max([i[k] for i in info for k in LEGS if planted(k, i['f'] / N)] or [0.0])
    out['Hop'] = dict(frames=fr, events=ev,
                      extra=dict(airborne_frames=airborne, mid_frame=N // 2, mid_feet_min_z=min(info[N // 2][k] for k in LEGS),
                                 peak_m=max(i['h'] for i in info), squash_m=min(i['h'] for i in info),
                                 stance_foot_max_z=round(stance_lift, 4), events=ev))

    # ---- Nibble (2 s loop): sits back on the haunches (rump down 3 cm, chest up 14 deg), head dips to the paws, front
    # paws raised to the chin (IK to the Jaw), Jaw chews 12x (6 Hz) in small steps, nose twitches, ears relaxed back/out
    N = frames_of(dur['Nibble'][0]); fr = []; gap = []; arms = None
    for f in range(N):
        t = f / N; s12 = math.sin(12 * TW * t)
        pose = new_pose(sk)
        body(sk, pose, (0, 0, -0.012 + 0.0012 * math.sin(2 * TW * t)), pitch=-18.0 + 0.8 * math.sin(2 * TW * t))
        rot(pose, 'Spine1', x=-4); rot(pose, 'Spine2', x=-6)
        rot(pose, 'Neck1', x=8 + 0.5 * math.sin(TW * t)); rot(pose, 'Neck2', x=6); rot(pose, 'Head', x=16 + 1.5 * s12, z=2 * math.sin(TW * t))
        chew(pose, t, 12, open_deg=10.0, side_deg=3.0)
        rot(pose, 'Nose', x=5 * math.sin(10 * TW * t), z=2 * math.sin(10 * TW * t + 1.0))
        ears(pose, fl=-14 + 2 * math.sin(TW * t), ol=12, sl=8, fr=-12 + 2 * math.sin(TW * t + 1.0), or_=14, sr=6)
        rot(pose, 'Tail1', x=-5, z=3 * math.sin(2 * TW * t))
        plant_flat(sk, pose, ['HindL', 'HindR'])
        if arms is None: arms = nibble_arms(sk, pose, NIB_PAW)
        for sx, s in ((1, 'L'), (-1, 'R')):
            pose['FrontUpper.' + s][1] = [R(arms[0] - 3.0 * s12), 0.0, R(NIB_IN * sx)]
            pose['FrontLower.' + s][1] = [R(arms[1] + 4.0 * s12), 0.0, 0.0]
            foot_flat(sk, pose, 'Front' + s, NIB_PAW_PITCH)
        M = sk.fk(pose)
        gap.append(round((M['FrontFoot.L'].translation - M['Jaw'].translation).length, 4))
        fr.append(pose)
    fr.append(copy_pose(fr[0]))
    out['Nibble'] = dict(frames=fr, events=[], extra=dict(paw_to_jaw_m=[min(gap), max(gap)], arm_search=[round(x, 3) for x in arms]))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


NIB_PAW = (0.0, -0.040, -0.050)      # fetlock target relative to the Jaw head (side plane: y - = in front, z down), m
NIB_IN = 6.0                         # front legs turned slightly inwards (deg) so the paws come together under the chin
NIB_PAW_PITCH = -60.0                # paws turned toes-up (deg, - = toe up)
