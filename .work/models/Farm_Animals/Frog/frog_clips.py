# frog_clips.py - SML-05 Frog clips (ANIMATIONS.md: Idle "sits, throat slightly pulsing", Jump "jumps and lands").
# Skeleton F (rig_frog.py): Q-S style names without tail/ears + Throat (scaled, partial weights on the jaw underside) and
# Eye.L/R. The frog's legs are Z-folded (thigh forward-up, shin back-down, long foot forward), so the shared Q leg IK
# (legs pointing down) does not apply: ik2() is a generic analytic 2-bone IK that keeps the rest bend plane, feet get a
# world orientation (planted = rest = flat). Shared helpers of _common/animal_anim.py are imported read-only.
# Pose = {bone: [loc, euler]} (animal_anim format); bone scale (Throat) is kept per frame in clip['scale'].
import math
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from animal_anim import new_pose, copy_pose, rot, body, raise_body, frames_of, smooth, R
import animal_rig as ar

TW = 2 * math.pi
GROUND_TOL = -0.0005      # lowest vertex limit: pack -1 cm (Cow, 2.3 m) scaled to the 0.10 m frog (-0.43 mm)
LEGS = list(ar.LEGS.keys())
PARENT = {'FrontL': 'Spine2', 'FrontR': 'Spine2', 'HindL': 'Pelvis', 'HindR': 'Pelvis'}

# Idle: throat pulses (buccal pumping) - scale of the Throat bone (x lateral, y down = along the bone, z fore-aft)
THROAT_AMP = (0.10, 0.08, 0.16)
# Jump body track (phase of the 1.5 s loop): t, pelvis world z offset (m), pitch (deg, - = nose up), y offset (m, + back)
JUMP_BODY = [(0.00, 0.0, 0.0, 0.0), (0.16, 0.0, 0.0, 0.0), (0.30, -0.0030, -8.0, 0.002), (0.37, 0.050, -32.0, -0.006),
             (0.47, 0.078, -12.0, -0.008), (0.57, 0.020, 12.0, -0.004), (0.60, 0.003, 10.0, -0.001),
             (0.64, -0.004, 2.0, 0.0), (0.72, -0.0012, -1.0, 0.0), (0.82, 0.0, 0.0, 0.0), (1.00, 0.0, 0.0, 0.0)]
JUMP_T = dict(front_off=0.30, hind_off=0.37, front_on=0.60, hind_on=0.64)
HIND_EXT_DIR = Vector((0.25, 1.0, -0.40)).normalized()     # trailing hind leg direction in body (rest) space
FRONT_REACH_DIR = Vector((0.30, -0.55, -0.78)).normalized()  # front legs reaching for the ground (body space)


# ---------------- generic IK ----------------
def ik2(sk, pose, up, lo, T):
    """analytic 2-bone IK: upper+lower so the lower bone's tail reaches T (world); keeps the bend plane of the current
    parent (rest bend side); upper and lower local rotations are replaced. Returns reach excess (m, > 0: out of reach)"""
    M = sk.fk(pose)
    P_up = M[sk.parent[up]] @ sk.rel[up]
    H = P_up.translation.copy(); L1, L2 = sk.length[up], sk.length[lo]
    K0 = P_up @ Vector((0, L1, 0)); A0 = (P_up @ sk.rel[lo]) @ Vector((0, L2, 0))
    n0 = (K0 - H).cross(A0 - K0)
    if n0.length < 1e-10: n0 = P_up.to_3x3() @ Vector((1, 0, 0))
    n0.normalize()
    sgn = 1.0 if n0.dot((A0 - H).cross(K0 - H)) > 0 else -1.0
    t = Vector(T) - H; d0 = t.length; tu = t.normalized()
    d = min(max(d0, abs(L1 - L2) + 1e-6), L1 + L2 - 1e-7)
    n1 = n0 - tu * n0.dot(tu)
    n1 = n1.normalized() if n1.length > 1e-8 else n0
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    K1 = H + (Matrix.Rotation(sgn * al, 3, n1) @ tu) * L1
    u0 = (K0 - H).normalized(); u1 = (K1 - H).normalized()
    n0p = (n0 - u0 * n0.dot(u0)).normalized(); n1p = (n1 - u1 * n1.dot(u1)).normalized()
    F0 = Matrix((u0, n0p, u0.cross(n0p))).transposed(); F1 = Matrix((u1, n1p, u1.cross(n1p))).transposed()
    B = P_up.to_3x3()
    pose[up][1] = list((B.inverted() @ (F1 @ F0.transposed()) @ B).to_euler('XYZ'))
    pose[lo][1] = [0.0, 0.0, 0.0]
    M = sk.fk(pose); P_lo = M[up] @ sk.rel[lo]; K = P_lo.translation; A = P_lo @ Vector((0, L2, 0))
    Rw = (A - K).rotation_difference(Vector(T) - K).to_matrix()
    B2 = P_lo.to_3x3()
    pose[lo][1] = list((B2.inverted() @ Rw @ B2).to_euler('XYZ'))
    return d0 - (L1 + L2)


def foot_world(sk, pose, k, Rw):
    """foot bone local rotation so its world orientation = Rw (3x3)"""
    up, lo, ft, _ = ar.LEGS[k]
    Pm = (sk.fk(pose)[lo] @ sk.rel[ft]).to_3x3()
    pose[ft][1] = list((Pm.inverted() @ Rw).to_euler('XYZ'))


def delta(sk, M, bone):
    """world transform that carries the rest model of `bone` to its posed state"""
    return M[bone] @ sk.rest[bone].inverted()


REACH = {'max': -1.0}


def plant(sk, pose, legs=None):
    """planted feet: ankle/wrist at the rest spot, foot flat (rest world orientation); REACH['max'] records the worst
    reach excess (> 0 = the planted foot could not be reached -> slip)"""
    for k in (LEGS if legs is None else legs):
        up, lo, ft, _ = ar.LEGS[k]
        REACH['max'] = max(REACH['max'], ik2(sk, pose, up, lo, sk.rest[ft].translation))
        foot_world(sk, pose, k, sk.rest[ft].to_3x3())


def foot_pts(sk, pose, k):
    up, lo, ft, _ = ar.LEGS[k]; M = sk.fk(pose)
    return M[ft].translation.copy(), (M[ft] @ Vector((0, sk.length[ft], 0)))


# ---------------- curves ----------------
def _herm(p0, p1, m0, m1, u, dt):
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * dt * m0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * dt * m1


def track(keys, t, col):
    """Catmull-Rom through keys [(t, ...)] on column col, zero tangents at the first/last key (clamped)"""
    if t <= keys[0][0]: return keys[0][col]
    if t >= keys[-1][0]: return keys[-1][col]
    k = max(i for i in range(len(keys) - 1) if keys[i][0] <= t)
    (ta, a), (tb, b) = (keys[k][0], keys[k][col]), (keys[k + 1][0], keys[k + 1][col])
    ma = 0.0 if k == 0 else (b - keys[k - 1][col]) / (tb - keys[k - 1][0])
    mb = 0.0 if k + 1 == len(keys) - 1 else (keys[k + 2][col] - a) / (keys[k + 2][0] - ta)
    return _herm(a, b, ma, mb, (t - ta) / (tb - ta), tb - ta)


def vtrack(keys, t):
    """vector keys [(t, Vector)] -> Catmull-Rom with clamped ends"""
    flat = [(tk,) + tuple(v) for tk, v in keys]
    return Vector([track(flat, t, c) for c in (1, 2, 3)])


def qtrack(keys, t):
    """quaternion keys [(t, Quaternion)] -> piecewise smoothstep slerp"""
    if t <= keys[0][0]: return keys[0][1].copy()
    if t >= keys[-1][0]: return keys[-1][1].copy()
    k = max(i for i in range(len(keys) - 1) if keys[i][0] <= t)
    u = smooth((t - keys[k][0]) / (keys[k + 1][0] - keys[k][0]))
    return keys[k][1].slerp(keys[k + 1][1], u)


def bump(t, c, w):
    d = (t - c + 0.5) % 1.0 - 0.5
    return 0.5 * (1 + math.cos(math.pi * d / w)) if abs(d) < w else 0.0


def throat(t, n, sharp=1.0):
    """0..1 buccal pulse, n per loop: quick swell, slower release"""
    x = (n * t) % 1.0
    return math.sin(math.pi * min(1.0, x / 0.6)) ** 2 if x < 0.6 else 0.0


def throat_scale(a):
    return tuple(1.0 + a * A for A in THROAT_AMP)


def eye_blink(pose, a):
    """eyes sink into the head (frog blink/swallow): along the eye bone axis inwards and a bit down, a = 0..1"""
    for s in ('L', 'R'):
        pose['Eye.' + s][0] = [0.0, -0.0028 * a, 0.0]


# ---------------- clips ----------------
def foot_clear(sk, pose, k, q_flat, q_want, Dp, floor=0.0):
    """air foot: world orientation = Dp @ slerp(flat -> want); the rotation is reduced until no foot vertex is below floor"""
    m = sk.mask([ar.LEGS[k][2]])
    def setq(u):
        foot_world(sk, pose, k, Dp.to_3x3() @ q_flat.slerp(q_want, u).to_matrix())
    setq(1.0)
    if sk.minz(pose, m) >= floor: return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(16):
        mid = 0.5 * (lo + hi); setq(mid)
        if sk.minz(pose, m) >= floor: lo = mid
        else: hi = mid
    setq(lo); return lo


def build_clips(sk, sp):
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}

    # ---- Idle (3 s): sits, 2 slow breaths, throat pumps 6x (2 Hz), a slow blink at 0.62, head micro nod/turn
    N = frames_of(dur['Idle'][0]); fr = []; sc = []
    for f in range(N):
        t = f / N; p = new_pose(sk)
        s = math.sin(2 * TW * t); c = 0.5 + 0.5 * s
        # the straight front legs are at full reach in the rest pose: breathing only lowers/pitches the chest down
        body(sk, p, (0, 0, -0.0007 * c), pitch=0.5 * c)
        rot(p, 'Spine1', x=-0.9 * s)
        rot(p, 'Head', x=-1.2 * math.sin(TW * t + 0.7) + 0.6 * s, z=3.0 * math.sin(TW * t))
        rot(p, 'Neck1', z=1.5 * math.sin(TW * t - 0.4))
        a = throat(t, 6)
        rot(p, 'Jaw', x=-0.6 * a)                       # jaw floor drops a hair with the pump (mouth stays shut)
        eye_blink(p, bump(t, 0.62, 0.05))
        plant(sk, p)
        fr.append(p); sc.append({'Throat': throat_scale(a)})
    fr.append(copy_pose(fr[0])); sc.append(dict(sc[0]))
    out['Idle'] = dict(frames=fr, scale=sc, events=[], planted={k: list(range(N + 1)) for k in LEGS},
                       extra=dict(reach_excess_m=round(REACH['max'], 6)))
    REACH['max'] = -1.0

    # ---- Jump (1.5 s): pause, crouch (nose up), push (hind legs unfold, feet leave last), air (hind legs trail extended,
    # front legs fold then reach), front feet land, hind feet land + squash, eyes pulled in on the landing, settle, pause
    N = frames_of(dur['Jump'][0]); fr = []; sc = []; info = []
    REST = new_pose(sk)

    trunk = sk.mask(['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Head', 'Jaw', 'Throat', 'Eye.L', 'Eye.R'])

    def body_pose(t):
        p = new_pose(sk)
        body(sk, p, (0, track(JUMP_BODY, t, 3), track(JUMP_BODY, t, 1)), pitch=track(JUMP_BODY, t, 2))
        rot(p, 'Spine1', x=0.25 * track(JUMP_BODY, t, 2)); rot(p, 'Spine2', x=0.15 * track(JUMP_BODY, t, 2))
        hp = track(JUMP_BODY, t, 2)
        rot(p, 'Neck1', x=-0.20 * hp); rot(p, 'Head', x=-0.15 * hp)
        z = sk.minz(p, trunk)
        if z < 0.0005: raise_body(sk, p, 0.0005 - z)     # chest/chin never below 0.5 mm (nose-down landing)
        return p

    # liftoff / landing boundary data in parent (body) space, from the planted pose at those instants
    def planted_at(t, k):
        p = body_pose(t); plant(sk, p, [k]); return p
    bnd = {}
    for k in LEGS:
        front = k.startswith('Front'); par = PARENT[k]; ft = ar.LEGS[k][2]
        t_off = JUMP_T['front_off' if front else 'hind_off']; t_on = JUMP_T['front_on' if front else 'hind_on']
        po = planted_at(t_off, k); Mo = sk.fk(po); Do = delta(sk, Mo, par)
        pl = planted_at(t_on, k); Ml = sk.fk(pl); Dl = delta(sk, Ml, par)
        a_off = Do.inverted() @ Mo[ft].translation; a_on = Dl.inverted() @ Ml[ft].translation
        q_off = (Do.inverted().to_3x3() @ Mo[ft].to_3x3()).to_quaternion()
        q_on = (Dl.inverted().to_3x3() @ Ml[ft].to_3x3()).to_quaternion()
        hip = sk.rest[ar.LEGS[k][0]].translation; Lt = sk.length[ar.LEGS[k][0]] + sk.length[ar.LEGS[k][1]]
        sx = 1.0 if k.endswith('L') else -1.0
        if front:
            dr = Vector((FRONT_REACH_DIR.x * sx, FRONT_REACH_DIR.y, FRONT_REACH_DIR.z))
            tuck = a_off + Vector((0.004 * sx, 0.006, 0.012))
            reach = hip + dr * (0.93 * Lt)
            pos = [(t_off, a_off), (0.42, tuck), (0.53, reach), (t_on, a_on)]
            qx = lambda deg, q: Quaternion(Vector((1, 0, 0)), R(deg)) @ q       # + = toes down (body X axis)
            qs = [(t_off, q_off), (0.42, qx(35.0, q_off)), (0.53, qx(20.0, q_on)), (t_on, q_on)]
        else:
            dr = Vector((HIND_EXT_DIR.x * sx, HIND_EXT_DIR.y, HIND_EXT_DIR.z))
            ext = hip + dr * (0.90 * Lt)
            tuck = a_on + Vector((0.004 * sx, 0.010, 0.010))
            pos = [(t_off, a_off), (0.45, ext), (0.57, tuck), (t_on, a_on)]
            # toes pointing back along the extended leg: foot pitched toe-down about the body X axis
            qd = lambda deg: Quaternion(Vector((1, 0, 0)), R(deg)) @ q_off
            qs = [(t_off, q_off), (0.45, qd(105.0)), (0.57, Quaternion(Vector((1, 0, 0)), R(25.0)) @ q_on), (t_on, q_on)]
        bnd[k] = dict(par=par, pos=pos, qs=qs, t_off=t_off, t_on=t_on, q_flat=q_off)

    for f in range(N):
        t = f / N; p = body_pose(t)
        land = bump(t, 0.665, 0.07)
        eye_blink(p, land)
        rot(p, 'Jaw', x=-1.0 * land)
        a = 0.35 * throat(t, 3) * (1.0 - smooth((t - 0.25) / 0.05) * (1.0 - smooth((t - 0.75) / 0.05)))
        row = dict(f=f)
        for k in LEGS:
            b = bnd[k]; up, lo, ft, _ = ar.LEGS[k]
            if b['t_off'] < t < b['t_on']:
                M = sk.fk(p); D = delta(sk, M, b['par'])
                ik2(sk, p, up, lo, D @ vtrack(b['pos'], t))
                q = qtrack(b['qs'], t)
                M = sk.fk(p); D = delta(sk, M, b['par'])
                foot_clear(sk, p, k, b['q_flat'], q, D) if t - b['t_off'] < 0.06 or b['t_on'] - t < 0.06 else \
                    foot_world(sk, p, k, D.to_3x3() @ q.to_matrix())
                row[k] = 'air'
            else:
                plant(sk, p, [k]); row[k] = 'planted'
        fr.append(p); sc.append({'Throat': throat_scale(a)}); info.append(row)
    fr.append(copy_pose(fr[0])); sc.append(dict(sc[0]))
    ev = [(round(JUMP_T['hind_off'] * N), 'Jump', 'Takeoff'), (round(JUMP_T['front_on'] * N), 'Footstep', 'LandFront'),
          (round(JUMP_T['hind_on'] * N), 'Land', 'LandHind')]
    planted = {k: [r['f'] for r in info if r[k] == 'planted'] + [N] for k in LEGS}
    airborne = [r['f'] for r in info if all(r[k] == 'air' for k in LEGS)]
    out['Jump'] = dict(frames=fr, scale=sc, events=ev, planted=planted,
                       extra=dict(reach_excess_m=round(REACH['max'], 6), airborne_frames=[airborne[0], airborne[-1]] if airborne else [], events=ev,
                                  peak_body_m=max(k[1] for k in JUMP_BODY)))
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out
