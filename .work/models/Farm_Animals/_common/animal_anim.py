# animal_anim.py - procedural FK clips for the Farm Animals pack (Q skeleton first).
# Pose = {bone: [loc(3), euler XYZ rad(3)]} in pose-bone space. Own FK + linear-blend skinning (numpy) is used by the
# generators (analytic 2-bone leg IK -> FK keys, ground contact, head aiming); the metrics (7.4) are measured on
# Blender's own evaluation of the written Actions, so generator and check are independent.
import bpy, math, json
import numpy as np
from mathutils import Matrix, Vector, Euler, Quaternion
from bpy_extras import anim_utils
import animal_rig as ar

FPS = 30
R = math.radians
LEGS = list(ar.LEGS.keys())


def smooth(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)


def bump(t, c, w):
    """periodic smooth bump on phase t (0..1) centred at c, half width w"""
    d = (t - c + 0.5) % 1.0 - 0.5
    return 0.5 * (1 + math.cos(math.pi * d / w)) if abs(d) < w else 0.0


class Skel:
    def __init__(self, rig, mesh):
        self.rig = rig; bones = rig.data.bones; order = []

        def visit(b):
            order.append(b.name)
            for c in b.children: visit(c)
        for b in bones:
            if b.parent is None: visit(b)
        self.order = order
        self.parent = {b.name: (b.parent.name if b.parent else None) for b in bones}
        self.rest = {b.name: b.matrix_local.copy() for b in bones}
        self.rel = {n: (self.rest[p].inverted() @ self.rest[n]) if p else self.rest[n].copy() for n, p in self.parent.items()}
        self.length = {b.name: b.length for b in bones}
        self.idx = {n: i for i, n in enumerate(order)}
        me = mesh.data
        self.V = np.array([tuple(v.co) + (1.0,) for v in me.vertices])
        W = np.zeros((len(me.vertices), len(order))); gname = {g.index: g.name for g in mesh.vertex_groups}
        for v in me.vertices:
            for g in v.groups: W[v.index, self.idx[gname[g.group]]] = g.weight
        self.W = W / W.sum(1, keepdims=True)
        self.rest_inv = np.array([np.array(self.rest[n].inverted()) for n in order])
        self.feet = {k: self.rest[ar.LEGS[k][2]] @ Vector((0, self.length[ar.LEGS[k][2]], 0)) for k in LEGS}
        self.feet = {k: Vector((v.x, v.y, 0.0)) for k, v in self.feet.items()}

    def mask(self, bones):
        ix = [self.idx[b] for b in bones]
        return self.W[:, ix].sum(1) > 0.5

    def fk(self, pose):
        M = {}
        for n in self.order:
            loc, rot = pose[n]
            B = Matrix.Translation(loc) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
            p = self.parent[n]
            M[n] = (M[p] @ self.rel[n] if p else self.rel[n]) @ B
        return M

    def skin(self, M, mask=None):
        S = np.array([np.array(M[n]) for n in self.order]) @ self.rest_inv
        V = self.V if mask is None else self.V[mask]; W = self.W if mask is None else self.W[mask]
        P = np.einsum('bij,vj->vbi', S, V)
        return (P * W[:, :, None]).sum(1)[:, :3]

    def minz(self, pose, mask=None):
        return float(self.skin(self.fk(pose), mask)[:, 2].min())


# ---------------- pose helpers ----------------
def new_pose(sk):
    return {n: [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]] for n in sk.order}


def copy_pose(p):
    return {n: [list(a), list(b)] for n, (a, b) in p.items()}


def blend(p0, p1, u):
    return {n: [[a + (b - a) * u for a, b in zip(p0[n][0], p1[n][0])], [a + (b - a) * u for a, b in zip(p0[n][1], p1[n][1])]] for n in p0}


def rot(pose, bone, x=0.0, y=0.0, z=0.0):
    """add degrees to the local euler of a bone (x = pitch: +nose down / +leg back / +tail up-back)"""
    r = pose[bone][1]; r[0] += R(x); r[1] += R(y); r[2] += R(z)


def ear(pose, up=0.0, back=0.0):
    rot(pose, 'Ear.L', x=up, z=back); rot(pose, 'Ear.R', x=up, z=-back)


def body(sk, pose, off=(0, 0, 0), pitch=0.0, roll=0.0, yaw=0.0):
    """Pelvis offset in world metres (+z up, +y back) and rotation in degrees (pitch + = nose down)"""
    Rm = sk.rest['Pelvis'].to_3x3()
    pose['Pelvis'][0] = list(Rm.transposed() @ Vector(off))
    pose['Pelvis'][1] = [R(pitch), R(roll), R(yaw)]


def body_off(sk, pose):
    return sk.rest['Pelvis'].to_3x3() @ Vector(pose['Pelvis'][0])


def raise_body(sk, pose, dz):
    o = body_off(sk, pose); o.z += dz
    pose['Pelvis'][0] = list(sk.rest['Pelvis'].to_3x3().transposed() @ o)


def leg_ik(sk, pose, leg, fetlock, hoof_pitch=0.0):
    """analytic 2-bone IK (upper+lower) with abduction, foot keeps hoof_pitch (rad) relative to world vertical.
    Returns reach excess in metres (>0: target out of reach, leg straight)."""
    up, lo, ft, front = ar.LEGS[leg]
    M = sk.fk(pose); M0 = M[sk.parent[up]] @ sk.rel[up]
    t = M0.inverted() @ Vector(fetlock)
    beta = math.atan2(-t.x, t.y); r = math.hypot(t.x, t.y); tz = t.z
    L1, L2 = sk.length[up], sk.length[lo]
    d0 = math.hypot(r, tz); d = min(max(d0, abs(L1 - L2) + 1e-4), L1 + L2 - 1e-6)
    base = math.atan2(tz, r)
    al = math.acos(max(-1.0, min(1.0, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    a1 = base - al if front else base + al
    ky, kz = L1 * math.cos(a1), L1 * math.sin(a1)
    ty, tz2 = d * math.cos(base), d * math.sin(base)
    phi2 = math.atan2(tz2 - kz, ty - ky)
    dd = Matrix.Rotation(-beta, 3, 'Z') @ (M0.to_3x3().inverted() @ Vector((0, 0, -1)))
    phid = math.atan2(dd.z, dd.y)
    pose[up][1] = [a1, 0.0, beta]; pose[lo][1] = [phi2 - a1, 0.0, 0.0]; pose[ft][1] = [phid + hoof_pitch - phi2, 0.0, 0.0]
    return d0 - (L1 + L2)


def plant(sk, pose, legs=None, feet=None):
    feet = feet or {}
    for k in (legs if legs is not None else LEGS):
        G = Vector(feet.get(k, sk.feet[k])); L3 = sk.length[ar.LEGS[k][2]]
        leg_ik(sk, pose, k, G + Vector((0, 0, L3)))


def no_penetration(sk, pose, planted=(), feet=None, exact=False, mask=None):
    for _ in range(3):
        z = sk.minz(pose, mask)
        if not exact and z >= -1e-4: break
        if abs(z) < 1e-5: break
        raise_body(sk, pose, -z); plant(sk, pose, planted, feet)


def aim_head(sk, pose, target_z, share=(('Neck1', 0.42), ('Neck2', 0.33), ('Head', 0.25)), lo=-30.0, hi=120.0):
    """add pitch A (deg, split by share) so the lowest head/jaw vertex is at target_z; returns A"""
    mask = sk.mask(['Head', 'Jaw', 'Ear.L', 'Ear.R', 'Horn.L', 'Horn.R'])
    base = {b: pose[b][1][0] for b, _ in share}

    def f(A):
        for b, s in share: pose[b][1][0] = base[b] + R(A * s)
        return sk.minz(pose, mask)
    grid = [lo + (hi - lo) * i / 60 for i in range(61)]
    vals = [f(A) for A in grid]
    i_min = min(range(61), key=lambda i: vals[i])
    if vals[i_min] > target_z: A = grid[i_min]; f(A); return A
    a, b = lo, grid[i_min]
    for _ in range(40):
        m = (a + b) / 2
        if f(m) > target_z: a = m
        else: b = m
    f(b); return b


# ---------------- overlays (secondary motion) ----------------
def tail_sway(pose, ph, amps, lag=0.12, lift=0.0, cycles=1):
    for i, (b, a) in enumerate(zip(('Tail1', 'Tail2', 'Tail3'), amps)):
        rot(pose, b, x=lift * (1 - 0.4 * i), z=a * math.sin(2 * math.pi * (cycles * ph - lag * (i + 1))))


def breathe(sk, pose, ph, amp=0.010, cycles=1, spine=1.0):
    s = math.sin(2 * math.pi * cycles * ph)
    if amp: raise_body(sk, pose, amp * s)
    rot(pose, 'Spine1', x=-0.8 * spine * s); rot(pose, 'Spine2', x=0.5 * spine * s)


def chew(pose, ph, n, open_deg=7.0, side_deg=3.0):
    rot(pose, 'Jaw', x=open_deg * 0.5 * (1 - math.cos(2 * math.pi * n * ph)), z=side_deg * math.sin(2 * math.pi * n * ph))


# ---------------- clip builders ----------------
def frames_of(T):
    return max(1, round(T * FPS))


def gait(sk, sp, name):
    """walk / trot: feet on ground in stance move back at speed (in place), swing arcs; body height per girdle from
    reach (smoothed, periodic), legs by IK. Returns frames, events, stance schedule."""
    g = sp['gait'][name]; T = g['T']; N = frames_of(T); duty = g['duty']; v = g['speed']; S = duty * v * T
    targ = []; need = {'Front': np.zeros(N), 'Hind': np.zeros(N)}
    stance = {k: [] for k in LEGS}
    piv = {k: sk.rest[ar.LEGS[k][0]].translation.copy() for k in LEGS}
    for f in range(N):
        ph = f / N; row = {}
        for k in LEGS:
            p = (ph - g['phases'][k]) % 1.0; G = sk.feet[k]; L3 = sk.length[ar.LEGS[k][2]]
            flick = g['flick'][0 if k.startswith('Front') else 1]
            if p < duty:
                y = G.y - S / 2 + S * p / duty; z = 0.0; hp = 0.0; stance[k].append(f)
            else:
                s = (p - duty) / (1 - duty)
                y = G.y + S / 2 - S * (s - math.sin(2 * math.pi * s) / (2 * math.pi))
                z = g['lift'] * math.sin(math.pi * s) ** 1.3; hp = R(flick) * math.sin(math.pi * s) ** 2
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
        body(sk, pose, (0, 0, -dh), pitch=math.degrees(math.asin((df - dh) / span)),
             roll=1.2 * math.sin(2 * math.pi * ph) if name == 'Walk' else 0.0)
        nod = g['nod'] * math.sin(2 * math.pi * (2 * ph) - 1.2)
        rot(pose, 'Neck1', x=nod * 0.6); rot(pose, 'Head', x=-nod * 0.3)
        rot(pose, 'Neck1', z=1.5 * math.sin(2 * math.pi * ph - 0.6))
        tail_sway(pose, ph, g['tail'], lag=0.1, lift=6.0 if name == 'Run' else 0.0)
        ear(pose, up=g['ear'] * math.sin(2 * math.pi * 2 * ph - 2.0), back=-4.0 + g['ear'] * 0.5 * math.sin(2 * math.pi * 2 * ph - 2.6))
        for k in LEGS:
            fet, hp, st = targ[f][k]
            leg_ik(sk, pose, k, fet, hp)
        frames.append(pose)
    frames.append(copy_pose(frames[0]))
    events = sorted([(round(g['phases'][k] * N) % N, 'Footstep', k) for k in LEGS])
    return frames, events, dict(stance=stance, speed=v, step=S, N=N)


def keyed(sk, N, keys, overlay=None, lift=True):
    """keys: [(t, pose, planted_legs)] ; legs planted in both neighbouring keys are re-solved by IK each frame,
    the others interpolate their angles. Overlay(pose, t) adds secondary motion; lift prevents ground penetration."""
    out = []
    for f in range(N + 1):
        t = f / N
        for i in range(len(keys) - 1):
            if keys[i][0] <= t <= keys[i + 1][0]: break
        (t0, p0, l0), (t1, p1, l1) = keys[i], keys[i + 1]
        u = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        pose = blend(p0, p1, u)
        if overlay: overlay(pose, t)
        pl = [k for k in LEGS if k in l0 and k in l1]
        plant(sk, pose, pl)
        if lift: no_penetration(sk, pose, pl)
        out.append(pose)
    return out


def stand_pose(sk):
    p = new_pose(sk); plant(sk, p); return p


def lie_pose(sk, sp):
    p = new_pose(sk)
    body(sk, p, (0, 0.02, -0.38), pitch=0.0, roll=sp['poses']['lie_roll'])
    for s, sg in (('L', 1), ('R', -1)):
        rot(p, 'FrontUpper.' + s, x=-32, z=-4 * sg); rot(p, 'FrontLower.' + s, x=125); rot(p, 'FrontFoot.' + s, x=35)
        rot(p, 'HindUpper.' + s, x=28, z=-14 * sg); rot(p, 'HindLower.' + s, x=-118); rot(p, 'HindFoot.' + s, x=-35)
    rot(p, 'Neck1', x=-6); rot(p, 'Head', x=4)
    rot(p, 'Tail1', x=18); rot(p, 'Tail2', x=-10, z=12); rot(p, 'Tail3', z=15)
    no_penetration(sk, p, exact=True)
    return p


def kneel_pose(sk):
    p = new_pose(sk)
    body(sk, p, (0, 0.02, -0.02), pitch=15.0)
    for s in ('L', 'R'):
        rot(p, 'FrontUpper.' + s, x=-6); rot(p, 'FrontLower.' + s, x=150); rot(p, 'FrontFoot.' + s, x=40)
    rot(p, 'Neck1', x=-12); rot(p, 'Head', x=-6)
    plant(sk, p, ['HindL', 'HindR'])
    front = sk.mask(['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R', 'Spine2', 'Neck1'])
    for _ in range(4):
        z = sk.minz(p, front); raise_body(sk, p, -z); plant(sk, p, ['HindL', 'HindR'])
    return p


def build_clips(sk, sp):
    """all clips of a Q species -> {clip: dict(frames, loop, events, bones, extra)}"""
    out = {}; dur = {c: (T, loop) for c, T, loop in sp['clips']}; ps = sp['poses']
    STAND = stand_pose(sk)

    def loop_static(name, base, overlay, planted=LEGS):
        N = frames_of(dur[name][0]); fr = []
        for f in range(N):
            p = copy_pose(base); overlay(p, f / N); plant(sk, p, planted); fr.append(p)
        fr.append(copy_pose(fr[0])); return fr

    # Idle: breathing, head nod, tail, one ear flick
    def ov_idle(p, t):
        breathe(sk, p, t, 0.012); rot(p, 'Neck1', x=1.5 * math.sin(2 * math.pi * t + 0.5)); tail_sway(p, t, (3, 5, 7))
        ear(p, up=-3 + 14 * bump(t, 0.62, 0.07), back=10 * bump(t, 0.64, 0.08))
    out['Idle'] = dict(frames=loop_static('Idle', STAND, ov_idle), events=[])

    # Idle_Look: head left/right with hold, ears follow
    def ov_look(p, t):
        breathe(sk, p, t, 0.010, 2)
        s = math.tanh(2.2 * math.sin(2 * math.pi * t)) / math.tanh(2.2); A = 50.0 * s
        rot(p, 'Neck1', z=-0.3 * A); rot(p, 'Neck2', z=-0.3 * A); rot(p, 'Head', z=-0.4 * A, x=-5 * abs(s))
        s2 = math.tanh(2.2 * math.sin(2 * math.pi * (t - 0.04))) / math.tanh(2.2)
        rot(p, 'Ear.L', z=-18 * s2, x=4); rot(p, 'Ear.R', z=-18 * s2, x=4)
        tail_sway(p, t, (3, 5, 7), cycles=2)
    out['Idle_Look'] = dict(frames=loop_static('Idle_Look', STAND, ov_look), events=[])

    # Eat: head down to the grass, one front foot forward, chewing
    eat = copy_pose(STAND); body(sk, eat, (0, -0.03, -0.03), pitch=7.0); rot(eat, 'Spine1', x=4); rot(eat, 'Spine2', x=6)
    eat_feet = {'FrontL': sk.feet['FrontL'] + Vector((0, -0.22, 0))}
    plant(sk, eat, None, eat_feet); rot(eat, 'Neck1', z=4)
    A_eat = aim_head(sk, eat, ps['eat_muzzle_z'] + 0.03, share=(('Neck1', 0.55), ('Neck2', 0.30), ('Head', 0.15)), hi=105.0)
    print('eat neck pitch', round(A_eat, 1))

    def ov_eat(p, t):
        chew(p, t, 4, 8, 3); rot(p, 'Head', x=3 * math.sin(2 * math.pi * t)); breathe(sk, p, t, 0.006)
        ear(p, up=-6 + 8 * bump(t, 0.3, 0.08), back=6); tail_sway(p, t, (4, 6, 9))
    N = frames_of(dur['Eat'][0]); fr = []
    for f in range(N):
        p = copy_pose(eat); ov_eat(p, f / N); plant(sk, p, None, eat_feet); fr.append(p)
    fr.append(copy_pose(fr[0])); out['Eat'] = dict(frames=fr, events=[])

    # Drink: head down to trough height, swallow pulses
    dr = copy_pose(STAND); body(sk, dr, (0, -0.02, -0.01), pitch=2.0); plant(sk, dr)
    aim_head(sk, dr, ps['drink_muzzle_z'])

    def ov_drink(p, t):
        rot(p, 'Neck1', x=2.5 * math.sin(2 * math.pi * 3 * t)); rot(p, 'Neck2', x=-1.5 * math.sin(2 * math.pi * 3 * t - 0.8))
        chew(p, t, 3, 3, 0); breathe(sk, p, t, 0.005); ear(p, up=-4, back=8 + 6 * bump(t, 0.5, 0.1)); tail_sway(p, t, (3, 5, 7))
    out['Drink'] = dict(frames=loop_static('Drink', dr, ov_drink), events=[])

    # Walk / Run
    for nm in ('Walk', 'Run'):
        fr, ev, extra = gait(sk, sp, nm); out[nm] = dict(frames=fr, events=ev, extra=extra)

    LIE = lie_pose(sk, sp); KNEEL = kneel_pose(sk)
    # Lie_Down (once): head lowers, front kneels, hind drops, settle
    k1 = copy_pose(STAND); rot(k1, 'Neck1', x=16); body(sk, k1, (0, 0.04, -0.01)); plant(sk, k1)
    k3 = copy_pose(LIE); body(sk, k3, tuple(body_off(sk, LIE) + Vector((0, 0, 0.06))), pitch=7.0, roll=1.0)
    out['Lie_Down'] = dict(frames=keyed(sk, frames_of(dur['Lie_Down'][0]),
                                        [(0.0, STAND, LEGS), (0.18, k1, LEGS), (0.50, KNEEL, ['HindL', 'HindR']), (0.80, k3, []),
                                         (1.0, LIE, [])]), events=[])
    # Lie_Idle: breathing + chewing cud + ear flick
    def ov_lie(p, t):
        breathe(sk, p, t, 0.0, 1, 1.6); chew(p, t, 4, 6, 4); ear(p, up=-5 + 12 * bump(t, 0.4, 0.06), back=4)
        rot(p, 'Neck1', x=1.5 * math.sin(2 * math.pi * t)); tail_sway(p, t, (0, 3, 5))
    out['Lie_Idle'] = dict(frames=loop_static('Lie_Idle', LIE, ov_lie, planted=[]), events=[])
    # Sleep: head turned and laid down, slow deep breathing, ears drooped
    sl = copy_pose(LIE); rot(sl, 'Neck1', z=-22); rot(sl, 'Neck2', z=-18); rot(sl, 'Head', z=-12)
    aim_head(sk, sl, ps['sleep_muzzle_z'] + 0.012)
    ear(sl, up=-22, back=12)

    def ov_sleep(p, t):
        breathe(sk, p, t, 0.0, 1, 2.2); rot(p, 'Head', x=-1.0 * math.sin(2 * math.pi * t))
    out['Sleep'] = dict(frames=loop_static('Sleep', sl, ov_sleep, planted=[]), events=[])
    # Stand_Up (once): lunge, hind rises first (kneeling front), then front, settle
    s1 = copy_pose(LIE); rot(s1, 'Neck1', x=22); body(sk, s1, tuple(body_off(sk, LIE) + Vector((0, -0.03, 0.0))), pitch=3.0)
    s3 = copy_pose(STAND); rot(s3, 'Neck1', x=-6); rot(s3, 'Head', x=-4); plant(sk, s3)
    out['Stand_Up'] = dict(frames=keyed(sk, frames_of(dur['Stand_Up'][0]),
                                        [(0.0, LIE, []), (0.18, s1, []), (0.55, KNEEL, ['HindL', 'HindR']), (0.85, s3, LEGS),
                                         (1.0, STAND, LEGS)]), events=[])
    # Hit_React (once): flinch sideways/back, head thrown up, ears back, tail up, recover
    h1 = copy_pose(STAND); body(sk, h1, (0.05, 0.05, -0.03), pitch=-3.0, roll=4.0, yaw=5.0)
    rot(h1, 'Spine2', x=-3); rot(h1, 'Neck1', x=-12); rot(h1, 'Neck2', x=-8); rot(h1, 'Head', x=-12, z=6); ear(h1, up=15, back=40)
    rot(h1, 'Tail1', x=40); rot(h1, 'Tail2', x=15); plant(sk, h1)
    h2 = blend(STAND, h1, -0.25); plant(sk, h2)
    out['Hit_React'] = dict(frames=keyed(sk, frames_of(dur['Hit_React'][0]),
                                         [(0.0, STAND, LEGS), (0.17, h1, LEGS), (0.45, h2, LEGS), (1.0, STAND, LEGS)]), events=[])
    # Moo (once): head up and forward, jaw opens, vocal event
    m1 = copy_pose(STAND); rot(m1, 'Neck1', x=6); rot(m1, 'Neck2', x=-14); rot(m1, 'Head', x=-24); ear(m1, up=-8, back=18)
    body(sk, m1, (0, 0.02, -0.01), pitch=1.5); plant(sk, m1)
    m2 = copy_pose(m1); rot(m2, 'Jaw', x=22); m3 = copy_pose(m1); rot(m3, 'Jaw', x=19); rot(m3, 'Head', x=-3)
    Nm = frames_of(dur['Moo'][0])

    def ov_moo(p, t):
        if 0.32 < t < 0.72: rot(p, 'Jaw', x=1.5 * math.sin(2 * math.pi * 14 * t))
    out['Moo'] = dict(frames=keyed(sk, Nm, [(0.0, STAND, LEGS), (0.22, m1, LEGS), (0.32, m2, LEGS), (0.72, m3, LEGS), (0.82, m1, LEGS),
                                            (1.0, STAND, LEGS)], ov_moo), events=[(round(0.27 * Nm), 'Vocal', 'Moo')])
    # Tail_Swish (loop, tail bones only -> for an AvatarMask layer)
    N = frames_of(dur['Tail_Swish'][0]); fr = []
    for f in range(N):
        p = copy_pose(STAND); t = f / N
        rot(p, 'Tail1', x=12 + 6 * math.sin(4 * math.pi * t), z=24 * math.sin(2 * math.pi * t))
        rot(p, 'Tail2', z=32 * math.sin(2 * math.pi * (t - 0.08))); rot(p, 'Tail3', z=40 * math.sin(2 * math.pi * (t - 0.16)))
        fr.append(p)
    fr.append(copy_pose(fr[0])); out['Tail_Swish'] = dict(frames=fr, events=[], bones=['Tail1', 'Tail2', 'Tail3'])
    for c, (T, loop) in dur.items():
        out[c]['loop'] = loop; out[c].setdefault('bones', None); out[c].setdefault('extra', {})
    return out


# ---------------- actions ----------------
def write_action(rig, name, frames, loop, bones=None):
    old = bpy.data.actions.get(name)
    if old: bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name); act.use_fake_user = True
    slot = act.slots.new(id_type='OBJECT', name=rig.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    N = len(frames) - 1
    for b in (bones or [n for n in frames[0]]):
        chans = [('rotation_euler', 1)] + ([('location', 0)] if b == 'Pelvis' else [])
        for path, ix in chans:
            for i in range(3):
                fc = cb.fcurves.new(f'pose.bones["{b}"].{path}', index=i, group_name=b)
                fc.keyframe_points.add(N + 1)
                co = []
                for f, p in enumerate(frames): co += [float(f), p[b][ix][i]]
                fc.keyframe_points.foreach_set('co', co)
                fc.keyframe_points.foreach_set('interpolation', [1] * (N + 1))   # LINEAR
                fc.update()
    act.use_frame_range = True; act.frame_start = 0; act.frame_end = N; act.use_cyclic = loop
    return act


def assign(rig, act):
    ad = rig.animation_data or rig.animation_data_create()
    ad.action = act
    if act is not None: ad.action_slot = act.slots[0]


# ---------------- metrics (FARM_ANIMALS_PACK 7.4) on Blender's evaluation ----------------
def metrics(sc, rig, mesh, clips, acts, limits, sample_mesh_every=1):
    rep = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for name, C in clips.items():
        act = acts[name]; assign(rig, act); N = int(act.frame_end)
        r = dict(frames=N + 1, seconds=round(N / FPS, 3), loop=C['loop'])
        # loop closure from the action curves
        cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0])
        worst = 0.0
        if C['loop']:
            for b in {fc.data_path.split('"')[1] for fc in cb.fcurves}:
                e = [[0, 0, 0], [0, 0, 0]]
                for fc in cb.fcurves:
                    if fc.data_path == f'pose.bones["{b}"].rotation_euler':
                        e[0][fc.array_index] = fc.evaluate(0); e[1][fc.array_index] = fc.evaluate(N)
                q0 = Euler(e[0]).to_quaternion(); q1 = Euler(e[1]).to_quaternion()
                worst = max(worst, math.degrees(q0.rotation_difference(q1).angle))
            r['loop_closure_deg'] = round(worst, 6)
        # lowest vertex, foot tracks
        minz = 1e9; minf = 0; feet = {k: [] for k in LEGS}
        for f in range(N + 1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            if f % sample_mesh_every == 0 or f == N:
                me = mesh.evaluated_get(dg).to_mesh(); z = min(v.co.z for v in me.vertices)
                mesh.evaluated_get(dg).to_mesh_clear()
                if z < minz: minz, minf = z, f
            for k in LEGS: feet[k].append(rig.pose.bones[ar.LEGS[k][2]].tail.copy())
        r['lowest_vertex_m'] = round(minz, 4); r['lowest_frame'] = minf
        # foot slip in stance (walk/run): deviation from ground moving back at speed, % of stance travel
        ex = C.get('extra') or {}
        if 'stance' in ex:
            v = ex['speed']; S = ex['step']; slip = 0.0; lift = 0.0
            for k in LEGS:
                fs = ex['stance'][k]; runs = []; cur = [fs[0]]
                for a, b in zip(fs, fs[1:]):
                    if b == a + 1: cur.append(b)
                    else: runs.append(cur); cur = [b]
                runs.append(cur)
                if len(runs) > 1 and runs[-1][-1] == ex['N'] - 1 and runs[0][0] == 0:
                    runs[0] = runs[-1] + [x + ex['N'] for x in runs[0]]; runs.pop()
                for run in runs:
                    p0 = feet[k][run[0] % ex['N']]
                    for fr_ in run:
                        p = feet[k][fr_ % ex['N']]; dt = (fr_ - run[0]) / FPS
                        dev = (p - p0 - Vector((0, v * dt, 0))).length; slip = max(slip, dev)
                        lift = max(lift, abs(p.z))
            r['foot_slip_m'] = round(slip, 4); r['foot_slip_pct_of_step'] = round(100 * slip / S, 2)
            r['step_m'] = round(S, 3); r['stance_foot_max_height_m'] = round(lift, 4); r['speed_mps'] = v
        # joint ranges vs limits (local euler, degrees)
        ranges = {}; viol = []
        nyaw = 0.0
        for fr_ in C['frames']:
            nyaw = max(nyaw, abs(math.degrees(fr_['Neck1'][1][2] + fr_['Neck2'][1][2] + fr_['Head'][1][2])))
            for b, (loc, rr) in fr_.items():
                for i, ax in enumerate('xyz'):
                    d = math.degrees(rr[i]); key = (b, ax)
                    lo, hi = ranges.get(key, (d, d)); ranges[key] = (min(lo, d), max(hi, d))
        for (b, ax), (lo, hi) in ranges.items():
            lim = limits.get(b.split('.')[0], {}).get(ax)
            if lim and (lo < lim[0] - 0.01 or hi > lim[1] + 0.01): viol.append(f'{b}.{ax} {lo:.1f}..{hi:.1f} (limit {lim})')
        if nyaw > limits['NECK_YAW_TOTAL']: viol.append(f'neck yaw total {nyaw:.1f}')
        r['neck_yaw_total_deg'] = round(nyaw, 1)
        r['joint_ranges_deg'] = {f'{b}.{ax}': [round(lo, 1), round(hi, 1)] for (b, ax), (lo, hi) in sorted(ranges.items())
                                 if hi - lo > 0.05 or abs(hi) > 0.05}
        r['limit_violations'] = viol
        rep[name] = r
        print(f"METRIC {name:11s} N={N:3d} loop={C['loop']!s:5s} closure={r.get('loop_closure_deg', '-')} lowest={r['lowest_vertex_m']} "
              f"slip={r.get('foot_slip_pct_of_step', '-')}% stanceZ={r.get('stance_foot_max_height_m', '-')} neckyaw={r['neck_yaw_total_deg']} viol={viol}")
    assign(rig, None)
    return rep
