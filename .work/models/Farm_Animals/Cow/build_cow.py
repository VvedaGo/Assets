# build_cow.py - LIV-01 Cow (Farm Animals pilot, skeleton Q). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_cow.py -- LIV-01 build|bend|anim|export
# build : mesh in parts + palette + patches + rig + binding + checks + check render (TEMP)
# bend  : build + extreme joint poses -> strip (TEMP)
# anim  : build + 13 clips + metrics report + frame strips (TEMP)
# export: anim + FBX (all clips as takes) + verify + events json + .blend + preview
import sys, os, math, json, copy
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common', REPO + r'\.work\models\Farm_Animals\Cow'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import importlib
import pack_common as pc
import animal_species as asp, animal_rig as ar, animal_render as rn
for m in (asp, ar, rn): importlib.reload(m)

SP = copy.deepcopy(asp.SPECIES['Cow'])         # cow-local overrides below (shared _common files stay untouched)
SP['poses'] = dict(SP['poses'], eat_muzzle_z=0.03)
SP['clips'] = [(c, 3.6 if c == 'Idle' else T, lp) for c, T, lp in SP['clips']]   # Idle rebuilt per ANIMATIONS.md (3.6 s)
SP['clips'] = SP['clips'] + [('Graze', 4.0, True)]                   # ANIMATIONS.md minimum set: Idle, Walk, Graze
SP['gait']['Walk'].update(nod=5.0, tail=(6, 9, 12), ear=5.0)         # Walk: slightly stronger head bob / tail / ear sway
_TD = (0.0, math.sin(math.radians(15)), -math.cos(math.radians(15)))       # tail hangs 15 deg behind vertical
_T0 = (0.0, 0.92, 1.37); _TL = (0.0, 0.22, 0.44, 0.65)                      # strand 0.65 m = 0.45 x withers height
_tp = [tuple(_T0[i] + _TD[i] * L for i in range(3)) for L in _TL]
SP['bones'].update({'Tail1': (_tp[0], _tp[1]), 'Tail2': (_tp[1], _tp[2]), 'Tail3': (_tp[2], _tp[3])})
LEG_RB, LEG_RT = 0.088, 0.101                      # leg taper radii (apothem) at z 0.10 / 0.62
HS = 1.12                                          # head group scale about the skull centre (reference: big head)
_P0 = (0.0, -0.92, 1.55)
for _bn in ('Jaw', 'Ear.L', 'Horn.L'):
    SP['bones'][_bn] = tuple(tuple(_P0[i] + (c[i] - _P0[i]) * HS for i in range(3)) for c in SP['bones'][_bn])
SP['bones']['Head'] = (SP['bones']['Head'][0], tuple(_P0[i] + (SP['bones']['Head'][1][i] - _P0[i]) * HS for i in range(3)))
ASSET = SP['asset']
ART = REPO + r'\art\Farm_Animals'
WORK = REPO + r'\.work\models\Farm_Animals\Cow'
REF = REPO + r'\planning\FarmAnimals\references\LIV-01.png'
CHECK = rn.CHECK
os.makedirs(CHECK, exist_ok=True)
(WHITE, WHITE_D, BLACK, BLACK_D, PINK, PINK_D, UDDER, NOSTRIL, EYE, HOOF, HORN, HORN_D) = range(12)
BONES = ar.bone_table(SP)

# ---------------- head frame (shared by head, jaw, eyes, nostrils, colouring) ----------------
HEAD_TILT = math.radians(40)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))       # along the head, poll -> nose
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))       # head 'up' (forehead side)
P0 = Vector((0, -0.92, 1.55))                                     # back of skull centre
HEAD_LEN = 0.60 * HS
# (s along U, half width, half height top, half height bottom)
HEAD_RINGS = [(s * HS, w * 1.06 * HS, ht * 1.06 * HS, hb * 1.06 * HS) for s, w, ht, hb in
              [(0.00, 0.15, 0.155, 0.14), (0.06, 0.21, 0.226, 0.198), (0.18, 0.228, 0.236, 0.212), (0.30, 0.210, 0.208, 0.195),
               (0.41, 0.165, 0.165, 0.158), (0.49, 0.180, 0.150, 0.152), (0.56, 0.171, 0.130, 0.139), (0.60, 0.130, 0.094, 0.105)]]
UDDER_ELL = ((0.0, 0.37, 0.555), (0.14, 0.18, 0.125))
BODY_Y = [-0.88, -0.80, -0.62, -0.42, -0.22, -0.02, 0.18, 0.38, 0.58, 0.80, 0.93]   # low-segment torso (large quads)
BODY_SIDES = 14
SLANT = 0.13          # body rings lean back going down the flank -> diagonal facets (patch edges not on a stair grid)
MUZZLE_S = 0.41 * HS
# body rings (y, half width, z bottom, z top)
BODY_RINGS = [(-0.88, 0.20, 0.74, 1.24), (-0.82, 0.30, 0.66, 1.36), (-0.70, 0.355, 0.625, 1.42), (-0.55, 0.375, 0.61, 1.445),
              (-0.40, 0.388, 0.60, 1.45), (-0.24, 0.397, 0.59, 1.445), (-0.08, 0.402, 0.585, 1.44), (0.08, 0.405, 0.585, 1.435),
              (0.24, 0.402, 0.595, 1.43), (0.40, 0.395, 0.61, 1.43), (0.55, 0.385, 0.63, 1.44), (0.70, 0.37, 0.655, 1.45),
              (0.82, 0.345, 0.69, 1.44), (0.89, 0.29, 0.73, 1.40), (0.93, 0.20, 0.80, 1.32)]
NECK_RINGS = [(-0.58, 0.30, 0.80, 1.38), (-0.80, 0.30, 0.82, 1.425), (-0.92, 0.25, 0.98, 1.57), (-1.00, 0.185, 1.30, 1.60)]
# Holstein patches: ellipsoids (centre, radii); left side follows the reference, right side differs on purpose
PATCH_GROUPS = {   # 3 big blobs per side (shoulder/neck saddle, mid flank over the back, rump); right side differs
    'L_shoulder': [((0.34, -0.62, 1.04), (0.30, 0.22, 0.25)), ((0.30, -0.47, 1.22), (0.26, 0.13, 0.13))],
    'L_mid': [((0.20, 0.08, 1.26), (0.46, 0.26, 0.26)), ((0.38, 0.17, 0.95), (0.20, 0.15, 0.17))],
    'L_rump': [((0.30, 0.79, 1.14), (0.32, 0.18, 0.24)), ((0.18, 0.92, 1.30), (0.22, 0.12, 0.12))],
    'R_shoulder': [((-0.34, -0.55, 1.12), (0.30, 0.20, 0.22))],
    'R_mid': [((-0.32, 0.0, 1.00), (0.34, 0.24, 0.24)), ((-0.12, 0.10, 1.38), (0.26, 0.16, 0.12))],
    'R_rump': [((-0.28, 0.72, 1.22), (0.32, 0.17, 0.22))]}
PATCHES_OLD = [  # superseded by PATCH_GROUPS (round 2)
    ((0.36, -0.70, 1.02), (0.24, 0.19, 0.23)), ((0.32, -0.56, 1.20), (0.22, 0.13, 0.15)),
    ((0.32, 0.06, 1.20), (0.38, 0.21, 0.28)), ((0.38, 0.20, 0.94), (0.18, 0.15, 0.17)), ((0.08, -0.02, 1.46), (0.30, 0.19, 0.12)),
    ((0.32, 0.80, 1.04), (0.28, 0.15, 0.25)), ((0.18, 0.93, 1.24), (0.24, 0.12, 0.14)),
    # right side (different on purpose)
    ((-0.36, -0.60, 1.10), (0.24, 0.17, 0.21)), ((-0.32, -0.06, 1.00), (0.30, 0.21, 0.25)), ((-0.14, 0.14, 1.40), (0.24, 0.17, 0.14)),
    ((-0.32, 0.66, 1.22), (0.26, 0.15, 0.19))]
# round 2b: patches as side-projected ellipses (y, z, ry, rz) per side -> 3 separated blobs, white bands and belly
PATCH2D = {
    'L_shoulder': [(-0.62, 1.06, 0.22, 0.25), (-0.50, 1.24, 0.13, 0.12)],
    'L_mid': [(0.10, 1.20, 0.26, 0.27), (0.21, 0.94, 0.13, 0.14)],
    'L_rump': [(0.80, 1.12, 0.17, 0.26), (0.90, 1.32, 0.12, 0.10)],
    'R_shoulder': [(-0.56, 1.10, 0.20, 0.22)],
    'R_mid': [(0.00, 1.04, 0.25, 0.24), (0.08, 1.32, 0.17, 0.13)],
    'R_rump': [(0.72, 1.20, 0.17, 0.23)]}
PATCH2D = {k: [(cy, cz, ry * 1.2, rz * 1.2) for cy, cz, ry, rz in v] for k, v in PATCH2D.items()}   # size tuned to the reference
PATCHES = [e for g in PATCH_GROUPS.values() for e in g]
HEAD_PATCHES = [((0.20, -1.077, 1.528), (0.18, 0.20, 0.20)), ((-0.20, -1.077, 1.528), (0.18, 0.20, 0.20))]


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-01', 'build'])[:2] if len(a) < 2 else a[:2]


# ---------------- ring helpers ----------------
def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ring_y(y, w, zb, zt, n, pt=3.0, pb=2.3, x0=0.0):
    zc, h = (zt + zb) / 2, (zt - zb) / 2; out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(Vector((x0 + w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
    return out


def ring_body(j, y, w, zb, zt, n, nr, pt=3.0, pb=2.3):
    """body ring j of nr: odd rings rotated half a step (triangle lattice), interior rings slanted back with depth"""
    f = 0.0 if j in (0, nr - 1) else (0.5 if j in (1, nr - 2) else 1.0)
    zc, h = (zt + zb) / 2, (zt - zb) / 2; out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)       # aligned rings (no zigzag lattice)
        p = pt if s >= 0 else pb
        z = zc + h * spow(s, 2 / p)
        out.append(Vector((w * spow(c, 2 / p), y + SLANT * f * (zt - z), z)))
    return out


def profile_at(y):
    T = BODY_RINGS
    if y <= T[0][0]: return T[0][1:]
    for a, b in zip(T, T[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return [a[i] + (b[i] - a[i]) * t for i in (1, 2, 3)]
    return T[-1][1:]


def ell(p, c, r):
    return math.sqrt(sum(((p[i] - c[i]) / r[i]) ** 2 for i in range(3))) - 1.0


def field_body(p):
    """< 0 inside a black patch"""
    sd = 'L' if p[0] >= 0 else 'R'
    return min(patch_d(p, e) for g, e in PATCH2D.items() if g[0] == sd)


def patch_d(p, ells):
    return min(math.sqrt(((p[1] - cy) / ry) ** 2 + ((p[2] - cz) / rz) ** 2) - 1.0 for cy, cz, ry, rz in ells)


def field_head(p):
    return max(min(ell(p, c, r) for c, r in HEAD_PATCHES), (0.075 - abs(p.x)) / 0.10)


def snap(P, idx, field, max_len=0.24, max_move=0.075):
    """move grid vertices next to the patch boundary onto it (along their edges): smooth, slanted colour edges
    without new geometry; topology unchanged"""
    faces = P.comp[idx][1]; vs = {v for f in faces for v in f.verts}; fv = {v: field(v.co) for v in vs}
    for f in faces: f.normal_update()
    best = {}
    for e in {e for f in faces for e in f.edges}:
        a, b_ = e.verts
        if a not in fv or b_ not in fv or fv[a] * fv[b_] >= 0: continue
        t = fv[a] / (fv[a] - fv[b_]); p = a.co.lerp(b_.co, t); L = e.calc_length()
        if L > max_len or len(e.link_faces) != 2 or e.link_faces[0].normal.angle(e.link_faces[1].normal, 0) < 0.02: continue
        for v, d in ((a, t), (b_, 1 - t)):
            if d < 0.5 and d * L < max_move and (v not in best or d * L < best[v][0]): best[v] = (d * L, p.copy())
    for v, (d, p) in best.items(): v.co = p
    return len(best)


def ring_frame(c, ax, ay, w, ht, hb, n, p=2.6):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; co, si = math.cos(th), math.sin(th)
        out.append(c + ax * (w * spow(co, 2 / p)) + ay * ((ht if si >= 0 else hb) * spow(si, 2 / p)))
    return out


def ngon_ring(c, e1, e2, r, n, phase=None):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)                 # r = apothem
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def axis_rings(p0, p1, spec, n, ref=(1, 0, 0), phase=None):
    """rings along p0->p1; spec [(t, apothem)] (t may be <0 or >1)"""
    t_, e1, e2 = pc.basis(Vector(p1) - Vector(p0), ref)
    return [ngon_ring(Vector(p0).lerp(Vector(p1), t), e1, e2, r, n, phase) for t, r in spec]


def tri_comp(P, idx):
    """triangulate a component's quads (patch colours per triangle) and refresh its face list"""
    nm, faces, g = P.comp[idx]
    res = bmesh.ops.triangulate(P.bm, faces=faces, quad_method='ALTERNATE', ngon_method='BEAUTY')
    P.comp[idx] = (nm, res['faces'], g)


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Cow')
    # body: 11 rings x 22 sides (440 triangles for the patch colouring)
    prof = [(y,) + tuple(profile_at(y)) for y in BODY_Y]; nr = len(prof)
    P.loft('body', [ring_body(j, y, w, zb, zt, BODY_SIDES, nr) for j, (y, w, zb, zt) in enumerate(prof)], WHITE, WHITE, WHITE)
    tri_comp(P, len(P.comp) - 1); P.snapped = 0      # large triangles (alternating diagonals), whole-face patch painting
    # neck: thick wedge from inside the chest into the back of the head
    P.loft('neck', [ring_y(y, w, zb, zt, 12, 2.6, 2.2) for y, w, zb, zt in NECK_RINGS], WHITE, WHITE, WHITE)
    # head: 8 rings x 12 sides along the tilted head axis
    P.loft('head', [ring_frame(P0 + U * s, Vector((1, 0, 0)), VV, w, ht, hb, 12) for s, w, ht, hb in HEAD_RINGS], WHITE, WHITE, PINK)
    tri_comp(P, len(P.comp) - 1); P.snapped += snap(P, len(P.comp) - 1, field_head)
    head_faces = list(P.comp[-1][1])
    # jaw: chin block under the muzzle, hinge at Jaw bone head
    j0, j1 = BONES['Jaw']; uj = (j1 - j0).normalized(); vj = Vector((1, 0, 0)).cross(uj).normalized()
    if vj.dot(VV) < 0: vj = -vj
    P.loft('jaw', [ring_frame(j0 + uj * (s * HS), Vector((1, 0, 0)), vj, w * HS, ht * HS, hb * HS, 8, 2.4) for s, w, ht, hb in
                   [(-0.02, 0.07, 0.05, 0.03), (0.08, 0.105, 0.06, 0.055), (0.20, 0.11, 0.06, 0.065), (0.29, 0.10, 0.05, 0.055),
                    (0.33, 0.075, 0.035, 0.035)]], WHITE, WHITE, WHITE)
    # BVH of the head only for placing eyes / nostrils / horns on its surface
    bm = P.bm; bm.verts.index_update()
    hv = sorted({v for f in head_faces for v in f.verts}, key=lambda v: v.index); hix = {v: i for i, v in enumerate(hv)}
    bvh = BVHTree.FromPolygons([v.co.copy() for v in hv], [[hix[v] for v in f.verts] for f in head_faces])

    def surf(origin, direction):
        hit = bvh.ray_cast(Vector(origin), Vector(direction).normalized())
        if hit[0] is None: raise RuntimeError(f'no head hit from {origin}')
        n = hit[1] if hit[1].dot(Vector(direction)) < 0 else -hit[1]
        return hit[0], n
    # eyes: dark 8-gon discs, 5 mm proud
    ec = P0 + (U * 0.19 + VV * 0.06) * HS
    mir = lambda p: Vector((-p.x, p.y, p.z))
    for sx in (1, -1):                                # per side: the patch-snapped head is not exactly mirrored
        hp, n = surf((sx * 1.0, ec.y, ec.z), (-sx, 0, 0)); n = (n + Vector((0, -0.25, 0))).normalized()
        P.loft('eye', axis_rings(hp - n * 0.02, hp + n * 0.005, [(0, 0.040), (1, 0.040)], 8, ref=(0, 0, 1)), EYE, EYE, EYE)
    # nostrils on the muzzle front
    hpL, nL = surf(P0 + U * (HEAD_LEN + 0.3) + Vector((0.054, 0, 0)) + VV * 0.014, -U)
    for sx in (1, -1):
        hp, n = (hpL, nL) if sx > 0 else (mir(hpL), mir(nL))
        P.loft('nostril', axis_rings(hp - n * 0.015, hp + n * 0.003, [(0, 0.025), (1, 0.025)], 6, ref=(0, 0, 1)), NOSTRIL, NOSTRIL, NOSTRIL)
    # horns: short cream cones on the poll
    h0, h1 = BONES['Horn.L']; hdir = (h1 - h0).normalized()
    hpL, nL = surf((h0.x, h0.y, 3.0), (0, 0, -1))
    for sx in (1, -1):
        hp = hpL if sx > 0 else mir(hpL)
        d = hdir if sx > 0 else Vector((-hdir.x, hdir.y, hdir.z)); base = hp - d * 0.035
        P.loft('horn', axis_rings(base, base + d * 0.17, [(0, 0.038), (0.30, 0.036), (0.72, 0.024), (1.0, 0.006)], 6),
               lambda j, k: HORN if j < 2 else HORN_D, HORN, HORN_D)
    # ears: black leaves sticking out sideways, roots sunk into the head
    e0, e1 = BONES['Ear.L']; L = (e1 - e0).length
    for sx in (1, -1):
        a0 = Vector((sx * e0.x, e0.y, e0.z)); a1 = Vector((sx * e1.x, e1.y, e1.z)); d = (a1 - a0).normalized()
        t_, ea, eb = pc.basis(d, (0, 0, 1))
        rings = []
        for t, a, b in [(-0.07, 0.054, 0.030), (0.0, 0.070, 0.035), (0.13, 0.124, 0.040), (0.26, 0.112, 0.034), (0.34, 0.066, 0.027),
                        (L, 0.016, 0.010)]:
            c = a0 + d * t
            rings.append([c + ea * (a * pa) + eb * (b * pb) for pa, pb in [(1, 0), (0.5, 1), (-0.5, 1), (-1, 0), (-0.5, -1), (0.5, -1)]])
        P.loft('ear', rings, BLACK, BLACK, BLACK)
        fwd = eb if eb.y < 0 else -eb                     # pink inner ear on the front face
        for f in P.comp[-1][1]:
            c = f.calc_center_median(); t = (c - a0).dot(d)
            if 0.07 < t < 0.30 and (c - (a0 + d * t)).dot(fwd) > 0.027: f[P.slot] = PINK     # flat inner strip only, black rim
    # legs: upper (thick, knee band), lower, hoof with an inner collar; 8 sides, flat face to the front
    for key, (up, lo, ft, front) in ar.LEGS.items():
        hu, tu = BONES[up]; x, y = hu.x, hu.y
        hock = 0.0 if front else 0.022                 # hind: the hock point sits 2 cm back -> subtle angle
        dyz = lambda z: hock * (1 - abs(z - 0.47) / 0.40) if 0.07 < z < 0.87 else 0.0
        cx = lambda z, r: ngon_ring(Vector((x, y + dyz(z), z)), Vector((1, 0, 0)), Vector((0, 1, 0)), r, 8, math.pi / 8)
        rr = lambda z: LEG_RB + (LEG_RT - LEG_RB) * (z - 0.10) / 0.52          # one taper: r(0.62) = 1.15 x r(0.10)
        kz = 0.42 if front else 0.46                                              # part split, hidden in the taper
        top = [(0.98, rr(0.98))] if front else [(1.02, 0.13), (0.80, rr(0.80) + 0.006)]
        P.loft('legupper', [cx(z, r) for z, r in top + [(0.62, rr(0.62)), (kz, rr(kz) + 0.002)]], WHITE, WHITE, WHITE)
        P.loft('leglower', [cx(z, r) for z, r in [(kz + 0.05, rr(kz + 0.05) - 0.006), (kz, rr(kz)), (0.083, rr(0.083))]],
               WHITE, WHITE, WHITE)
        P.loft('hoof', [cx(z, r) for z, r in [(0.0, 0.102), (0.105, 0.094), (0.105, 0.074), (0.15, 0.074)]],
               HOOF, HOOF, HOOF, ground=True)
    # udder + 4 teats
    P.loft('udder', [ring_y(y, w, zb, zt, 10, 2.4, 2.2) for y, w, zb, zt in
                     [(0.19, 0.09, 0.56, 0.66), (0.25, 0.13, 0.465, 0.68), (0.37, 0.14, 0.43, 0.68), (0.49, 0.125, 0.455, 0.68),
                      (0.555, 0.075, 0.56, 0.66)]], UDDER, UDDER, UDDER)
    for tx in (0.062, -0.062):
        for ty in (0.30, 0.45):
            P.loft('teat', [ngon_ring(Vector((tx, ty, z)), Vector((1, 0, 0)), Vector((0, 1, 0)), r, 6) for z, r in
                            [(0.47, 0.027), (0.365, 0.019)]], PINK_D, PINK_D, PINK_D)
    # tail: one tube along Tail1-3 (smooth ring weights) + black spindle tuft on Tail3
    t1h, t1t = BONES['Tail1']; t2h, t2t = BONES['Tail2']; t3h, t3t = BONES['Tail3']
    chain = [(t1h + (t1h - t1t).normalized() * 0.07, 0.030), (t1h, 0.030), (t1t, 0.027), (t2t, 0.024), (t3t, 0.022)]
    rings = []
    for i, (c, r) in enumerate(chain):
        d = (chain[min(i + 1, len(chain) - 1)][0] - chain[max(i - 1, 0)][0]).normalized()
        t_, e1, e2 = pc.basis(d, (1, 0, 0)); rings.append(ngon_ring(c, e1, e2, r, 5, math.pi / 2))
    P.loft('tail', rings, WHITE, WHITE, WHITE)
    td = (t3t - t3h).normalized()                     # diamond tuft: 5-sided bipyramid, width 2 x strand
    P.loft('tuft', axis_rings(t3t - td * 0.04, t3t + td * 0.26, [(0, 0.020), (0.38, 0.046), (1.0, 0.004)], 5, phase=math.pi / 2),
           BLACK, BLACK, BLACK)
    return P


# ---------------- colours (patches by distance to ellipsoid centres) ----------------
def in_patch(c, patches):
    return any(sum(((c[i] - pc_[i]) / r[i]) ** 2 for i in range(3)) <= 1.0 for pc_, r in patches)


def colour(P):
    n_black = 0
    for nm, faces, _ in P.comp:
        for f in faces:
            c = f.calc_center_median()
            if nm in ('body', 'neck'):
                f[P.slot] = BLACK if field_body(c) < 0 else WHITE
            elif nm == 'head':
                s = (c - P0).dot(U); up = (c - (P0 + U * s)).dot(VV)
                if min((v.co - P0).dot(U) for v in f.verts) >= MUZZLE_S - 0.002: f[P.slot] = PINK
                elif field_head(c) < 0: f[P.slot] = BLACK
                else: f[P.slot] = WHITE
            elif nm == 'jaw':
                s = min((v.co - P0).dot(U) for v in f.verts); f[P.slot] = PINK if s >= MUZZLE_S - 0.01 else WHITE
    # clean-up on the torso + neck facet graph: drop black teeth, fill white notches (2 passes)
    fs = [f for nm, faces, _ in P.comp if nm in ('body', 'neck') for f in faces]; fset = set(fs)
    nb = {f: [g for e in f.edges for g in e.link_faces if g is not f and g in fset] for f in fs}
    for _ in range(4):
        new = {}
        for f in fs:
            k = sum(1 for g in nb[f] if g[P.slot] == BLACK)
            if f[P.slot] == BLACK and k <= 1: new[f] = WHITE
            elif f[P.slot] == WHITE and k >= (2 if len(f.verts) == 3 else 3): new[f] = BLACK
        for f, v in new.items(): f[P.slot] = v
    n_black = sum(1 for f in fs if f[P.slot] == BLACK)
    # side-area share of each patch (left: centroid x > 0.12, right: x < -0.12)
    share = {}
    for side, sg in (('L', 1), ('R', -1)):
        sf = [f for f in fs if sg * f.calc_center_median().x > 0.12]; tot = sum(f.calc_area() for f in sf)
        for gname, ells in PATCH2D.items():
            if gname[0] != side: continue
            a = sum(f.calc_area() for f in sf if f[P.slot] == BLACK and
                    patch_d(f.calc_center_median(), ells) <= field_body(f.calc_center_median()) + 1e-9)
            share[gname] = round(100 * a / tot, 1)
    P.share = share; print('PATCH share of side area %', share)
    return n_black


# ---------------- weights ----------------
def lerp_w(y, knots):
    """knots [(y, bone)] ascending y -> piecewise linear 2-bone blend"""
    if y <= knots[0][0]: return {knots[0][1]: 1.0}
    if y >= knots[-1][0]: return {knots[-1][1]: 1.0}
    for (y0, b0), (y1, b1) in zip(knots, knots[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0); return {b0: 1 - t, b1: t} if b0 != b1 else {b0: 1.0}


def weights(P):
    bm = P.bm; bm.verts.index_update()
    vcomp = {}
    leg_of = {}
    li = 0; legkeys = list(ar.LEGS.keys())
    side = {}
    for ci, (nm, faces, _) in enumerate(P.comp):
        for f in faces:
            for v in f.verts: vcomp[v.index] = (nm, ci)
    # component index -> leg key (3 comps per leg in build order), ear/horn side by x
    leg_comps = [ci for ci, (nm, _, _) in enumerate(P.comp) if nm in ('legupper', 'leglower', 'hoof')]
    for k, ci in enumerate(leg_comps): leg_of[ci] = legkeys[k // 3]
    W = []
    tail_pts = [BONES['Tail1'][0], BONES['Tail1'][1], BONES['Tail2'][1], BONES['Tail3'][1]]
    for v in bm.verts:
        nm, ci = vcomp[v.index]; co = v.co
        sfx = '.L' if co.x >= 0 else '.R'
        if nm == 'body':
            w = lerp_w(co.y, [(-0.45, 'Spine2'), (0.0, 'Spine1'), (0.45, 'Pelvis')])
        elif nm == 'neck':
            w = lerp_w(co.y, [(-1.00, 'Head'), (-0.94, 'Neck2'), (-0.84, 'Neck1'), (-0.66, 'Spine2')])
            if co.y < -0.97: w = {'Head': 0.65, 'Neck2': 0.35}
        elif nm in ('head', 'eye', 'nostril'):
            w = {'Head': 1.0}
        elif nm == 'jaw':
            w = {'Jaw': 1.0}
        elif nm == 'ear':
            w = {'Ear' + sfx: 1.0}
        elif nm == 'horn':
            w = {'Horn' + sfx: 1.0}
        elif nm in ('udder', 'teat'):
            w = {'Pelvis': 1.0}
        elif nm in ('legupper', 'leglower', 'hoof'):
            up, lo, ft, front = ar.LEGS[leg_of[ci]]
            par = 'Spine2' if front else 'Pelvis'
            if nm == 'legupper':
                if co.z > 0.9: w = {par: 0.5, up: 0.5}                 # top ring inside the body
                elif co.z < 0.43 + (0 if front else 0.04): w = {up: 0.75, lo: 0.25}   # knee/hock bottom ring
                else: w = {up: 1.0}
            elif nm == 'leglower':
                w = {up: 0.5, lo: 0.5} if co.z > (0.45 if front else 0.49) else {lo: 1.0}
            else:
                w = {ft: 1.0}
        elif nm == 'tail':
            # nearest point on the tail chain -> bone; joints blended 50/50
            zs = [p.z for p in tail_pts]
            if co.z >= zs[0] - 0.01: w = {'Tail1': 1.0}
            elif abs(co.z - zs[1]) < 0.03: w = {'Tail1': 0.5, 'Tail2': 0.5}
            elif co.z > zs[1]: w = {'Tail1': 1.0}
            elif abs(co.z - zs[2]) < 0.03: w = {'Tail2': 0.5, 'Tail3': 0.5}
            elif co.z > zs[2]: w = {'Tail2': 1.0}
            else: w = {'Tail3': 1.0}
        elif nm == 'tuft':
            w = {'Tail3': 1.0}
        else:
            raise RuntimeError('no weight rule for ' + nm)
        W.append(w)
    return W


def to_object(P, name, coll, mat):
    """pack_common.to_object without the internal checks/pivot handling (pivot is the world origin)"""
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = pc.cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob


def com_estimate(ob):
    """volume centroid of the closed parts (signed tetra volumes)"""
    me = ob.data; vol = 0.0; acc = Vector()
    for p in me.polygons:
        vs = [me.vertices[i].co for i in p.vertices]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]; v = a.dot(b.cross(c)) / 6.0
            vol += v; acc += v * (a + b + c) / 4.0
    return acc / vol, vol


def tris_by_comp(P):
    out = {}
    for nm, faces, _ in P.comp:
        out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in faces)
    return out


def build(tex_dir):
    sc = bpy.context.scene; sc.render.fps = an.FPS if 'an' in globals() else 30; sc.render.fps_base = 1.0
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    P = build_mesh()
    nb = colour(P)
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    chk = pc.comp_checks(P, mirror_skip=('head', 'eye', 'nostril', 'horn', 'jaw'))
    chk['snapped_vertices'] = P.snapped
    # snapped parts: distance of each mirrored vertex to the original surface (shape symmetry of the whole mesh)
    bm_ = P.bm; bm_.verts.index_update(); tree = BVHTree.FromBMesh(bm_)
    sym = max(tree.find_nearest(Vector((-v.co.x, v.co.y, v.co.z)))[3] for v in bm_.verts)
    chk['mirror_surface'] = sym; print(f'  mirror (surface distance, all parts) {sym:.5f} | patch-snapped vertices {P.snapped}')
    tri = tris_by_comp(P)
    W = weights(P)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + SP['tag'] + '_BaseColor', os.path.join(tex_dir, 'T_' + SP['tag'] + '_BaseColor.png'), SP['palette'])
    mat = pc.material('M_' + SP['tag'], img)
    ob = to_object(P, ASSET, coll, mat)
    rig = ar.build_armature(SP, coll)
    rchk = ar.check_rig(rig)
    ar.bind(ob, rig, W)
    tot = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print('TRIS per part', tri, '| total', tot, '| budget 2200')
    pts = [v.co for v in ob.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'SIZE x {hi[0]-lo[0]:.3f} y(length) {hi[1]-lo[1]:.3f} z(height) {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} minz {lo[2]:.4f}')
    com, vol = com_estimate(ob)
    print(f'COM {tuple(round(c, 3) for c in com)} volume {vol:.3f} m3 | black patch faces {nb}')
    cop = pc.coplanar_overlaps(ob)
    return dict(sc=sc, coll=coll, ob=ob, rig=rig, mat=mat, img=img, checks=chk, rig_checks=rchk, tris=tri, total=tot,
                coplanar=cop[0], com=com, size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    pts = rn.mesh_points([B['ob']])
    tiles = []
    for view in (rn.REF_VIEW, (1, 0, 0.08), (0.02, -1, 0.15), (-0.8, 0.9, 0.45)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    rn.fit(sc, cam, pts, rn.REF_VIEW, (0.9, 0.9))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Cow_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Cow_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


# ---------------- bend test, clips, strips ----------------
import animal_anim as an
importlib.reload(an)


def apply_pose(rig, pose):
    for n, (l, r) in pose.items():
        pb = rig.pose.bones[n]; pb.location = l; pb.rotation_euler = r
    bpy.context.view_layer.update()


def strip(B, setters, out, view=rn.REF_VIEW, cols=4, size=(320, 240)):
    """setters: list of callables that put the rig into a state; one tile per state, fixed camera"""
    sc = B['sc']; rn.setup_workbench(sc, *size); g = rn.ground(sc); cam = rn.camera(sc)
    pts = []
    for st in setters:
        st(); pts += rn.mesh_points([B['ob']])[::7]
    rn.fit(sc, cam, pts, view, (0.94, 0.92))
    tiles = []
    for i, st in enumerate(setters):
        st(); p = rn.render_to(sc, os.path.join(CHECK, f'tile_{i}.png')); tiles.append(rn.load_px(p)); os.remove(p)
    rn.compose(tiles, cols, out)
    bpy.data.objects.remove(g, do_unlink=True)


def bend_poses(sk):
    P = []
    def mk(fn):
        p = an.new_pose(sk); fn(p); P.append(p)
    mk(lambda p: [an.rot(p, 'FrontUpper.L', x=-75), an.rot(p, 'FrontUpper.R', x=60), an.rot(p, 'HindUpper.L', x=75), an.rot(p, 'HindUpper.R', x=-60)])
    mk(lambda p: [an.rot(p, 'FrontLower.L', x=165), an.rot(p, 'FrontFoot.L', x=110), an.rot(p, 'HindLower.L', x=-165), an.rot(p, 'HindFoot.L', x=-110),
                  an.rot(p, 'FrontUpper.R', z=-25), an.rot(p, 'HindUpper.R', z=25)])
    mk(lambda p: [an.rot(p, 'Neck1', x=85), an.rot(p, 'Neck2', x=60), an.rot(p, 'Head', x=45)])
    mk(lambda p: [an.rot(p, 'Neck1', x=-45), an.rot(p, 'Neck2', x=-40), an.rot(p, 'Head', x=-50), an.rot(p, 'Jaw', x=30)])
    mk(lambda p: [an.rot(p, 'Neck1', z=45), an.rot(p, 'Neck2', z=45), an.rot(p, 'Head', z=30)])
    mk(lambda p: [an.ear(p, up=70, back=-70), an.rot(p, 'Tail1', x=80, z=50), an.rot(p, 'Tail2', z=60), an.rot(p, 'Tail3', z=60)])
    mk(lambda p: [an.body(sk, p, (0, 0, 0), pitch=25, roll=15), an.rot(p, 'Spine1', x=15, z=15), an.rot(p, 'Spine2', x=15, z=-15)])
    P.append(an.lie_pose(sk, SP))
    return P


def anim(B):
    sk = an.Skel(B['rig'], B['ob'])
    import cow_clips; importlib.reload(cow_clips)
    clips = cow_clips.build_clips(sk, SP)
    acts = {}
    for c, _, _ in SP['clips']:
        C = clips[c]; acts[c] = cow_clips.write_action(B['rig'], f"{SP['species']}_{c}", C['frames'], C['loop'], C['bones'])
    rep = an.metrics(B['sc'], B['rig'], B['ob'], {c: clips[c] for c, _, _ in SP['clips']}, acts, SP['limits'])
    # self-intersection check: hind-leg vertices inside the udder (ellipsoid fit, pelvis space) per gait frame
    import numpy as np
    hl = sk.mask(['HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R'])
    uc = np.array(UDDER_ELL[0]); ur = np.array(UDDER_ELL[1])
    for c in ('Walk', 'Run', 'Graze'):
        worst = 0
        for fr in clips[c]['frames']:
            M = sk.fk(fr); P_ = sk.skin(M, hl)
            Mi = np.array(sk.rest['Pelvis'] @ M['Pelvis'].inverted())
            Q = (np.c_[P_, np.ones(len(P_))] @ Mi.T)[:, :3]
            worst = max(worst, int((((Q - uc) / ur) ** 2).sum(1).__lt__(1.0).sum()))
        rep[c]['hindleg_verts_in_udder_max'] = worst
        print(f'UDDER {c}: max hind-leg vertices inside the udder per frame {worst}')
    return sk, clips, acts, rep


def clip_strips(B, clips, acts, only=None):
    sc = B['sc']; rig = B['rig']
    for c, _, _ in SP['clips']:
        if only and c not in only: continue
        act = acts[c]; N = int(act.frame_end); C = clips[c]
        fr = [round(i * N / 8) for i in range(8)] if C['loop'] else [round(i * N / 7) for i in range(8)]
        an.assign(rig, act)
        setters = [(lambda f=f: (sc.frame_set(f), bpy.context.view_layer.update())) for f in fr]
        view = (1.0, -0.25, 0.22) if c in ('Walk', 'Run') else rn.REF_VIEW
        if c == 'Tail_Swish': view = (0.3, 1.0, 0.35)
        if c in ('Eat', 'Drink'): view = (0.55, -1.0, 0.35)
        if c == 'Sleep': view = (0.9, -0.8, 0.30)
        strip(B, setters, os.path.join(CHECK, f'Cow_strip_{c}.png'), view)
    an.assign(rig, None); sc.frame_set(0)


import animal_export as ax
importlib.reload(ax)


def events_json(clips, path):
    d = dict(species=SP['species'], asset=ASSET, fps=an.FPS, note='Unity AnimationEvents to add on import (FBX does not carry them)',
             clips={})
    for c, T, loop in SP['clips']:
        C = clips[c]; N = len(C['frames']) - 1
        e = dict(take=f"{SP['species']}_{c}", seconds=round(N / an.FPS, 3), last_frame=N, loop=loop,
                 events=[dict(name=n, frame=f, time=round(f / an.FPS, 4), stringParameter=p) for f, n, p in C['events']])
        if c in SP['gait']: e['speed_mps'] = SP['gait'][c]['speed']
        if C.get('bones'):
            e['keyed_bones_only'] = C['bones']
            chain = ['Rig', 'Rig/Root', 'Rig/Root/Pelvis', 'Rig/Root/Pelvis/Tail1', 'Rig/Root/Pelvis/Tail1/Tail2', 'Rig/Root/Pelvis/Tail1/Tail2/Tail3']
            e['unity_clip_mask'] = dict(
                note='The Blender FBX baker writes curves for every bone in every take (NLA path forces it), so this take also '
                     'holds rest-pose curves for the other 24 bones. On import set ModelImporterClipAnimation.maskType = '
                     'CopyFromOther with an AvatarMask whose active transforms are only Tail1-3; the imported clip then '
                     'contains tail curves only and can play on a Tail layer over any clip.',
                active_transforms=chain[3:], inactive_parents=chain[:3])
        d['clips'][c] = e
    json.dump(d, open(path, 'w'), indent=1); print('events', path)


ALL_BONES = os.environ.get('COW_ALL_BONES', '0') == '1'


def export_nla(rig, mesh, actions, fbx, all_bones):
    """cow-local copy of animal_export.export (mode 'nla') with bake_anim_use_all_bones exposed: with False the
    exporter writes curves only for bones that move in a take, so Cow_Tail_Swish carries the 3 tail bones only"""
    ad = rig.animation_data or rig.animation_data_create(); sc = bpy.context.scene
    assert sc.render.fps == 30 and sc.render.fps_base == 1.0
    for pb in rig.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    for o in sc.objects: o.select_set(False)
    rig.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = rig
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    ad.action = None
    for act in actions:
        tr = ad.nla_tracks.new(); tr.name = act.name
        st = tr.strips.new(act.name, int(act.frame_start), act); st.name = act.name
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                             bake_space_transform=True, object_types={'ARMATURE', 'MESH'}, mesh_smooth_type='FACE',
                             use_mesh_modifiers=True, use_armature_deform_only=False, add_leaf_bones=False, primary_bone_axis='Y',
                             secondary_bone_axis='X', armature_nodetype='NULL', path_mode='COPY', embed_textures=False, bake_anim=True,
                             bake_anim_use_all_bones=all_bones, bake_anim_force_startend_keying=True, bake_anim_step=1.0,
                             bake_anim_simplify_factor=0.0, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False)
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    return [fbx]


def curves_per_take(fbx):
    """take -> sorted list of bone/model names that have an AnimationCurveNode in that take"""
    ver, top = ax._read_fbx(fbx)
    objs = next(n for n in top if n[0] == 'Objects'); conns = next(n for n in top if n[0] == 'Connections')
    name = {n[1][0]: (n[0], n[1][1].split('\x00')[0]) for n in objs[2] if n[0] in ('Model', 'AnimationStack', 'AnimationLayer', 'AnimationCurveNode')}
    up = {}; target = {}
    for c in conns[2]:
        if c[1][0] == 'OO': up.setdefault(c[1][1], []).append(c[1][2])
        elif c[1][0] == 'OP' and c[1][1] in name and name[c[1][1]][0] == 'AnimationCurveNode': target[c[1][1]] = c[1][2]
    out = {}
    for cid, (kind, nm) in name.items():
        if kind != 'AnimationCurveNode': continue
        for lay in up.get(cid, []):
            for stk in up.get(lay, []):
                if stk in name and name[stk][0] == 'AnimationStack':
                    out.setdefault(name[stk][1], set()).add(name.get(target.get(cid), ('', '?'))[1])
    return {k: sorted(v) for k, v in out.items()}


def do_export(B, acts_d, clips, rep, mode='nla', bake_space=True, out_dir=None, tag=''):
    out_dir = out_dir or os.path.join(ART, 'Meshes'); os.makedirs(out_dir, exist_ok=True)
    acts = [acts_d[c] for c, _, _ in SP['clips']]
    fbx = os.path.join(out_dir, ASSET + tag + '.fbx')
    paths = export_nla(B['rig'], B['ob'], acts, fbx, ALL_BONES) if mode == 'nla' else ax.export(B['rig'], B['ob'], acts, fbx, mode, bake_space)
    summ = ax.fbx_summary(paths[0])
    cmp_ = ax.reimport_compare(paths[0], B['rig'], B['ob'], acts if mode != 'perclip' else acts[:1])
    cpt = curves_per_take(paths[0]); summ['curve_targets_per_take'] = {k: len(v) for k, v in cpt.items()}
    summ['tail_swish_targets'] = cpt.get(f"{SP['species']}_Tail_Swish")
    print('CURVES per take', summ['curve_targets_per_take']); print('TAIL_SWISH targets', summ['tail_swish_targets'])
    names = [s_['name'] for s_ in summ['stacks']]
    want = [a.name for a in acts]
    ok = (sorted(names) == sorted(want)) if mode == 'nla' else (len([n for n in names if n.split('|')[-1] in want]) == len(want))
    print(f'EXPORT CHECK mode {mode} bake_space {bake_space}: takes {len(names)} names_match {ok} limbs {summ["limb_nodes"]} '
          f'roots {[(r["name"], r["rot"], r["scale"]) for r in summ["roots"]]} max vertex err {max(v for v in cmp_["max_vertex_error_m"].values() if v is not None)}')
    return dict(paths=paths, summary=summ, reimport=cmp_, takes_ok=ok)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-01 Cow', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'bend':
        B = build(os.path.join(CHECK, 'tex')); sk = an.Skel(B['rig'], B['ob'])
        poses = bend_poses(sk)
        strip(B, [(lambda p=p: apply_pose(B['rig'], p)) for p in poses], os.path.join(CHECK, 'Cow_bend_side.png'))
        strip(B, [(lambda p=p: apply_pose(B['rig'], p)) for p in poses], os.path.join(CHECK, 'Cow_bend_front.png'), view=(-0.6, -1.0, 0.25))
    elif CMD in ('anim', 'strips'):
        B = build(os.path.join(CHECK, 'tex'))
        sk, clips, acts, rep = anim(B)
        json.dump(rep, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1)
        if CMD == 'strips' or len(sys.argv) > sys.argv.index('--') + 3:
            only = sys.argv[sys.argv.index('--') + 3:] or None
            clip_strips(B, clips, acts, only)
    elif CMD == 'exptest':
        B = build(os.path.join(CHECK, 'tex')); sk, clips, acts, rep = anim(B)
        tdir = os.path.join(CHECK, 'exptest')
        for mode, bs in (('nla', True),):
            try:
                do_export(B, acts, clips, rep, mode, bs, tdir, f'_{mode}_{int(bs)}')
            except Exception as e:
                import traceback; traceback.print_exc(); print('EXPORT FAILED', mode, bs, e)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures')); sk, clips, acts, rep = anim(B)
        mode = os.environ.get('COW_EXPORT_MODE', 'nla'); bs = os.environ.get('COW_BAKE_SPACE', '1') == '1'
        X = do_export(B, acts, clips, rep, mode, bs)
        events_json(clips, os.path.join(ART, 'Meshes', ASSET + '.events.json'))
        os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        data = {B['coll'], B['ob'], B['rig'], B['ob'].data, B['rig'].data, B['mat'], B['img']} | set(acts.values())
        bpy.data.libraries.write(os.path.join(ART, 'Blend', ASSET + '.blend'), data, fake_user=True, path_remap='ABSOLUTE')
        an.assign(B['rig'], None)
        for pb in B['rig'].pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()
        rn.preview(B['sc'], [B['ob']], os.path.join(ART, ASSET + '_Preview.png'), view=(1.0, -0.40, 0.17), fill=(0.70, 0.80))
        rp = rn.preview(B['sc'], [B['ob']], os.path.join(CHECK, 'Cow_refangle.png'), view=rn.REF_VIEW, fill=(0.80, 0.86))
        rn.compose([rn.ref_tile(REF, 512), rn.ref_tile(os.path.join(CHECK, 'Cow_refangle.png'), 512)], 2, os.path.join(CHECK, 'Cow_ref_compare.png'))
        full = dict(asset=ASSET, tris=B['total'], tris_per_part=B['tris'], size_m=[round(x, 3) for x in B['size']],
                    com=[round(c, 3) for c in B['com']], mesh_checks={k: (v if not isinstance(v, float) else round(v, 6)) for k, v in B['checks'].items()},
                    coplanar=B['coplanar'], rig=B['rig_checks'], clips=rep, export=dict(mode=mode, bake_space=bs, paths=X['paths'],
                    takes_ok=X['takes_ok'], fbx=X['summary'], reimport=X['reimport']))
        json.dump(full, open(os.path.join(WORK, 'metrics_report.json'), 'w'), indent=1, default=str)
        print('report', os.path.join(WORK, 'metrics_report.json'))
