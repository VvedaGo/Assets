# foal_clips.py - LIV-10 Foal clip set (ANIMATIONS.md: Idle, Walk, Trot). Copy of Horse/horse_clips.py (rest-offset leg IK,
# pastern-tilt gait, ear/mane/forelock/tail overlays) with: gait roll per table, Trot = two-beat diagonal pairs with a
# mid-stance body compression (bob) and tail lift; Graze removed. Shared _common helpers imported read-only.
import math
from mathutils import Vector, Matrix
from animal_anim import *
from animal_anim import R, LEGS

TW = 2 * math.pi
import animal_anim as _an
import numpy as np
import animal_rig as _ar

# ---------------- leg IK with rest offsets (horse legs are NOT collinear at rest: the hind gaskin and cannon meet at
# ~30 deg). animal_anim.leg_ik assumes collinear upper/lower/foot; this copy subtracts the rest angles of the lower bone
# in the upper frame (delta) and of the foot in the lower frame (eps), and picks the knee side from the rest pose.
# It replaces animal_anim.leg_ik in THIS process only (gait/plant call it by module global); the file is untouched.
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
    """0..1 envelope on the loop phase: fast rise (first 25% of w), slow relax; zero outside [c, c+w) (periodic)"""
    x = ((t - c) % 1.0) / w
    if x >= 1.0: return 0.0
    return math.sin(0.5 * math.pi * x / 0.25) if x < 0.25 else 0.5 * (1 + math.cos(math.pi * (x - 0.25) / 0.75))


def ears(p, l_swivel=0.0, r_swivel=0.0, l_tilt=0.0, r_tilt=0.0, l_flare=0.0, r_flare=0.0):
    """ear bones point up: local Y = ear axis (swivel: + turns the opening outward/back), local X = world X
    (tilt: + forward, - pinned back), local Z = forward (flare: + tips outward)"""
    rot(p, 'Ear.L', x=l_tilt, y=l_swivel, z=-l_flare)
    rot(p, 'Ear.R', x=r_tilt, y=-r_swivel, z=r_flare)


def mane(p, t, amp, cycles=1.0, lag=0.07, phase=0.0, lift=0.0):
    """chain sway: Mane1 (poll) leads, Mane2/3 follow with lag; z = side swing, y = twist, x = lift"""
    for i, b in enumerate(('Mane1', 'Mane2', 'Mane3')):
        s = math.sin(TW * (cycles * t - lag * i) + phase)
        rot(p, b, x=lift * (1 - 0.3 * i), y=0.6 * amp * s, z=amp * (1 + 0.25 * i) * s)


def forelock(p, t, amp, cycles=1.0, phase=0.0):
    rot(p, 'Forelock', x=0.5 * amp * math.sin(TW * cycles * t + phase + 1.1), z=amp * math.sin(TW * cycles * t + phase))


def tail_idle(p, t, swish_at=0.58, amps=(5.0, 7.0, 9.0), swish=(24.0, 32.0, 40.0), cycles=2):
    """lagged sway + one S-shaped swish (cow pattern)"""
    for i, (b, a) in enumerate(zip(('Tail1', 'Tail2', 'Tail3'), amps)):
        sw = 0.0; x = ((t - swish_at - 0.025 * i) % 1.0) / 0.20
        if x < 1.0: sw = math.sin(TW * x) * math.sin(math.pi * x)
        rot(p, b, x=(5.0 * math.sin(math.pi * x) * (1 - 0.4 * i)) if x < 1.0 else 0.0,
            z=a * math.sin(TW * (cycles * t) - 0.7 * (i + 1)) + swish[i] * sw)


def foot_tilt(sk, M, k, G, Lk=0.995, fallback='max'):
    """hoof planted at G; tilt the foot bone (pastern/fetlock) about the hoof until the fetlock is within Lk x the
    upper+lower length of the leg pivot (straight-ish leg, no knee crouch). Returns (fetlock target, hoof pitch rad)."""
    up, lo, ft, front = _ar.LEGS[k]
    L1, L2, L3 = sk.length[up], sk.length[lo], sk.length[ft]; Lm = Lk * (L1 + L2)
    piv = (M[sk.parent[up]] @ sk.rel[up]).translation
    sg = 1.0 if G.y - piv.y > 0 else -1.0                # hoof behind the pivot -> fetlock leans forward
    best = None
    for deg in range(0, 46):
        a = R(deg) * sg
        F = Vector((G.x, G.y - L3 * math.sin(a), G.z + L3 * math.cos(a))); d = (F - piv).length
        if d <= Lm: return F, a
        if best is None or d < best[0] - 1e-6: best = (d, F, a)
    if fallback == 'max': return F, a     # gait: keep the max tilt; the body drop is solved from it
    return best[1], best[2]          # static: the tilt with the shortest reach (0 when the hoof is under the joint)


def breathe_h(sk, p, t, A, cycles=2):
    """breathing on the back line only: Spine1 and Spine2 counter-rotate so the front-leg joint keeps its height
    (front legs are straight at rest; a lifted shoulder would lift the hooves)"""
    l1 = sk.rest['Spine1'].translation.y - sk.rest['FrontUpper.L'].translation.y
    l2 = sk.rest['Spine2'].translation.y - sk.rest['FrontUpper.L'].translation.y
    k = l1 / l2 - 1.0; s_ = math.sin(TW * cycles * t)
    rot(p, 'Spine1', x=A * s_); rot(p, 'Spine2', x=-k * A * s_)


def plant_h(sk, pose, legs=None, feet=None):
    feet = feet or {}
    for k in (legs if legs is not None else LEGS):
        M = sk.fk(pose); G = Vector(feet.get(k, sk.feet[k]))
        F, a = foot_tilt(sk, M, k, G, 0.9995, 'best')
        leg_ik_h(sk, pose, k, F, a)


def gait_h(sk, sp, name):
    """copy of animal_anim.gait: stance hooves stay planted and the pastern tilts (foot_tilt) instead of the body
    dropping/knees folding; swing arcs and body drop (only what the tilt cannot absorb) as in the shared solver"""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[_ar.LEGS[k][0]].translation.copy() for k in LEGS}
    M_rest = sk.fk(new_pose(sk))
    rows = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[_ar.LEGS[k][2]]
            up, lo, ft, front = _ar.LEGS[k]; gk = 'Front' if front else 'Hind'
            flick = g['flick'][0 if front else 1]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; stance[k].append(f)
                Gs = Vector((G.x, y, 0.0)); F, a = foot_tilt(sk, M_rest, k, Gs)
                Lm = 0.995 * (sk.length[up] + sk.length[lo])
                dy = F.y - piv[k].y; vert = math.sqrt(max(Lm * Lm - dy * dy, 0.0))
                need[gk][f] = max(need[gk][f], (piv[k].z - F.z) - vert)
                row[k] = ('stance', Gs, a)
            else:
                s_ = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s_ - math.sin(2 * math.pi * s_) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s_) ** 1.3; hp = R(flick) * math.sin(math.pi * s_) ** 2
                row[k] = ('swing', Vector((G.x, y, z + L3)), hp)
        rows.append(row)
    drops = {}
    # trot: extra body lowering at the mid-stance of each diagonal pair (lowering is always reachable), highest in the
    # suspension between the beats
    comp = np.array([g.get('bob', 0.0) * 0.5 * (1 + math.cos(2 * math.pi * 2 * (f / N - duty / 2))) for f in range(N)])         if name == 'Trot' else np.zeros(N)
    for gk, a in need.items():
        Fc = np.fft.rfft(a); Fc[4:] = 0; sm = np.fft.irfft(Fc, N)
        sm += max(0.0, float((a - sm).max())); drops[gk] = sm + g['crouch'] + comp
    span = piv['HindL'].y - piv['FrontL'].y
    frames = []
    for f in range(N):
        ph = f / N; pose = new_pose(sk)
        df, dh = drops['Front'][f], drops['Hind'][f]
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)), roll=g.get('roll', 1.2) * math.sin(2 * math.pi * ph))
        nod = g['nod'] * math.sin(2 * math.pi * (2 * ph) - 1.2)
        rot(pose, 'Neck1', x=nod * 0.6); rot(pose, 'Head', x=-nod * 0.3)
        rot(pose, 'Neck1', z=1.5 * math.sin(2 * math.pi * ph - 0.6))
        tail_sway(pose, ph, g['tail'], lag=0.1, lift=g.get('tail_lift', 0.0))
        ear(pose, up=g['ear'] * math.sin(2 * math.pi * 2 * ph - 2.0), back=-4.0 + g['ear'] * 0.5 * math.sin(2 * math.pi * 2 * ph - 2.6))
        for k in LEGS:
            kind, P_, a = rows[f][k]
            if kind == 'stance':
                M = sk.fk(pose); F, a2 = foot_tilt(sk, M, k, P_); leg_ik_h(sk, pose, k, F, a2)
            else:
                leg_ik_h(sk, pose, k, P_, a)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N,
                                body_drop_m={k: [round(float(a.min()), 4), round(float(a.max()), 4)] for k, a in drops.items()})


def build_clips(sk, sp):
    setup_ik(sk)
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}
    STAND = new_pose(sk); plant_h(sk, STAND)

    def loop_static(name, base, overlay, planted=LEGS, feet=None):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant_h(sk, p, planted, feet); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # ---- Idle (3 s): breathing, head drift, ears turn and flick in turn, tail sway + swish, mane/forelock follow
    def ov_idle(p, t):
        breathe_h(sk, p, t, 0.45, 2)
        hz = 3.0 * math.sin(TW * t); hx = 1.5 * math.sin(TW * t + 0.4)
        rot(p, 'Neck1', x=hx); rot(p, 'Neck2', z=0.4 * hz); rot(p, 'Head', x=-1.0 * math.sin(2 * TW * t + 1.0), z=0.6 * hz)
        # left ear swivels back-out at 0.10, flicks at 0.36; right ear swivels at 0.52, flicks at 0.78; both forward 0.90
        lsw = flick(t, 0.10, 0.22); rsw = flick(t, 0.52, 0.22)
        lfl = flick(t, 0.36, 0.08); rfl = flick(t, 0.78, 0.08); both = flick(t, 0.90, 0.10)
        ears(p, l_swivel=55 * lsw + 4 * math.sin(TW * t), r_swivel=55 * rsw + 4 * math.sin(TW * t + 1.7),
             l_tilt=-14 * lsw - 22 * lfl + 10 * both, r_tilt=-14 * rsw - 22 * rfl + 10 * both,
             l_flare=12 * lfl, r_flare=12 * rfl)
        tail_idle(p, t, 0.62)
        mane(p, t, 2.0, 1.0, 0.08, 0.5 + 0.0, 0.0); rot(p, 'Mane1', z=0.5 * hz); rot(p, 'Mane2', z=0.3 * hz)
        forelock(p, t, 2.5, 1.0, 0.8)
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # ---- Walk (four-beat LH-LF-RH-RF, shared gait solver) + mane / forelock / ear overlays
    fr, ev, extra = gait_h(sk, sp, 'Walk'); N = extra['N']
    for f in range(N):
        t = f / N; p = fr[f]
        mane(p, t, 4.0, 2.0, 0.10, -1.6, 2.0 * math.sin(TW * 2 * t - 2.2))
        forelock(p, t, 4.0, 2.0, -1.2)
        ears(p, l_tilt=4.0, r_tilt=4.0)
    fr[N] = copy_pose(fr[0])
    out['Walk'] = dict(frames=fr, events=ev, extra=extra)

    # ---- Trot (two-beat diagonal pairs, suspension, body compression at mid-stance) + livelier mane / forelock
    fr, ev, extra = gait_h(sk, sp, 'Trot'); N = extra['N']
    for f in range(N):
        t = f / N; p = fr[f]
        mane(p, t, 5.0, 2.0, 0.10, -1.6, 4.0 * math.sin(TW * 2 * t - 2.2))
        forelock(p, t, 5.0, 2.0, -1.2)
        ears(p, l_tilt=6.0, r_tilt=6.0)
    fr[N] = copy_pose(fr[0])
    out['Trot'] = dict(frames=fr, events=ev, extra=extra)
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
