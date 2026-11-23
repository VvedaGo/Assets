# build_dog.py - PET-01 Dog (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_dog.py -- PET-01 build|look|export
# build : parts + palette + patches + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_dog)
# look  : EEVEE sheet (reference, preview angle, side, back, front, top) + 128 px thumbnail
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Dog'
TAG = 'FarmAnimals_Dog'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\PET-01.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_dog')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.75, -1.0, 0.25)        # PET-01 reference: chest towards the camera, left flank receding, ~11 deg above
PREVIEW_VIEW = (0.95, -0.95, 0.22)   # preview: three-quarter front-left (head rework 4: a bit more frontal so the face reads)
PREVIEW_FILL = (0.78, 0.86)
BUDGET = 2800

PALETTE = ['#F2E8D8', '#E6D9C3', '#D2843F', '#E3A35E',     # 0 cream white, 1 white shade 2, 2 orange/rust, 3 ear inner tan
           '#3F3332', '#D8C8AE', '#262020', '#3A2E28',     # 4 black coat, 5 white shade 3, 6 nose, 7 sole
           '#2A1D17', '#B96C2C', '#B5835A', '#6E9F4A',     # 8 eye, 9 rust shade (spare), 10-15 series spares
           '#8E959B', '#C8473B', '#D8B65A', '#7A5233']
W, W2, R, TAN, K, W3, NOSE, SOLE, EYE = range(9)
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))

# ---------------- layout (before the centre-of-mass shift) ----------------
SLANT = 0.10
NB = 10                                 # body sides: few large facets (paper-craft reference)
BY = lambda y: -0.29 + (y + 0.37) * 0.753    # rework 3: compact sheltie torso 0.58 m (1.7x its depth)
BZ = lambda z: 0.40 + (z - 0.33) * 1.20      # rework 3: torso 1.2x deeper, belly raised to 0.40 (longer legs)
MOVE = Vector((0, 0.10, 0.13))               # neck + ruff + head group moved onto the shorter, higher chest
DYH = -0.04                                  # head/neck/ruff moved forward with the longer chest
# body profile: y, half width, z bottom, z top  (level back ~0.62, deep chest, domed rump)
BODY_PROF = [(BY(y), w * 1.15, BZ(zb), BZ(zt)) for y, w, zb, zt in
             [(-0.370, 0.100, 0.420, 0.560), (-0.340, 0.170, 0.350, 0.610), (-0.270, 0.210, 0.312, 0.630),
              (-0.150, 0.200, 0.320, 0.625), (0.000, 0.185, 0.330, 0.615), (0.150, 0.190, 0.335, 0.615),
              (0.270, 0.195, 0.350, 0.615), (0.340, 0.170, 0.385, 0.605), (0.380, 0.120, 0.430, 0.590),
              (0.400, 0.060, 0.480, 0.560)]]
BODY_RINGS = [(BY(y), f) for y, f in [(-0.370, 0), (-0.340, 0), (-0.270, 0.4), (-0.150, 1), (0.000, 1), (0.150, 1),
                                      (0.270, 1), (0.340, 0.5), (0.380, 0), (0.400, 0)]]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 9)}
FROZEN_LONG = {0, 3, 5, 9}
FRONT = (0.135, BY(-0.250))
FRONT_SHOULDER_Z = 0.40     # rig round 2 (Sit_Idle): FrontUpper pivot at the chest bottom (was 0.52 = leg top inside the
                            # chest); the leg mesh above it is bound to Spine2 in rig_dog (mesh unchanged)
HIND = (0.130, BY(0.270))
# patch layout per side (+1 left / -1 right): chest line, black saddle bottom z(y), wobble phase
COLLAR = {1: BY(-0.300), -1: BY(-0.292)}
SADDLE = {1: [(BY(y), BZ(z)) for y, z in [(-0.40, 0.62), (-0.30, 0.56), (-0.20, 0.50), (-0.08, 0.47), (0.05, 0.455),
                                       (0.18, 0.475), (0.28, 0.52), (0.36, 0.51), (0.45, 0.50)]],
          -1: [(BY(y), BZ(z)) for y, z in [(-0.40, 0.62), (-0.30, 0.55), (-0.20, 0.51), (-0.08, 0.46), (0.05, 0.44),
                                        (0.18, 0.465), (0.28, 0.51), (0.36, 0.52), (0.45, 0.50)]]}
PHASE = {1: 0.0, -1: 1.9}
BELLY_Y = (BY(-0.26), BY(0.22))

NECK_AXIS = [(y + DYH, z) for y, z in [(-0.250, 0.500), (-0.280, 0.570), (-0.310, 0.625), (-0.335, 0.665), (-0.355, 0.700)]]
NECK_R = [(0.150, 0.130), (0.150, 0.130), (0.145, 0.125), (0.125, 0.110), (0.080, 0.065)]
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
# Head rework 4 (2026-11-21, collie face): built directly in final metres around the head pivot HP (neck joint, after
# MOVE; the old x1.46 group scale is gone). Broad skull with a real stop, short tapered muzzle, eyes forward on the stop,
# big semi-erect ears folding forward-out, dark mane tufts framing the face, orange cheek tufts. Offsets: x left, -y fwd.
HP = Vector((0, -0.34 + DYH, 0.68)) + MOVE
NH = 12
HEAD_ANG = [5, 35, 70, 105, 140, 172]   # ring vertex angles from the top (left side; right = 360 - a): narrow top face
# rings: y, half width top, half width bottom, z bottom, z top (relative to HP)
HEAD_RINGS = [(0.035, 0.100, 0.090, -0.040, 0.150), (-0.020, 0.160, 0.145, -0.090, 0.215),
              (-0.090, 0.180, 0.165, -0.110, 0.245), (-0.150, 0.170, 0.160, -0.115, 0.230),
              (-0.200, 0.122, 0.128, -0.110, 0.158), (-0.235, 0.098, 0.100, -0.105, 0.112),
              (-0.268, 0.080, 0.080, -0.098, 0.082), (-0.292, 0.058, 0.058, -0.088, 0.056)]
EYE_R = 0.024
EYE_AT = (0.088, -0.185, 0.082)
EAR_AT = (0.118, -0.075, 0.30)          # ear base: ray down onto the skull
EAR_D1 = (0.80, 0.06, 1.0)              # standing part leans out
EAR_UP, EAR_FLAP = 0.115, 0.13
EAR_W = (0.082, 0.078, 0.020)           # half widths base / fold / tip
EAR_FOLD = (-0.40, 0.90, 0.22)          # flap direction = a*d1 + b*forward + c*width axis (out-down)
# mane tufts (left side; mirrored): base (inside the skull), direction, length, half width, half thickness, slot
MANE = [((0.120, 0.000, 0.170), (0.62, 0.25, -0.75), 0.20, 0.095, 0.055, 'K'),
        ((0.130, -0.060, 0.070), (0.55, 0.05, -0.83), 0.22, 0.095, 0.055, 'K'),
        ((0.120, -0.075, -0.040), (0.62, -0.05, -0.78), 0.20, 0.090, 0.055, 'K'),
        ((0.085, 0.050, 0.130), (0.45, 0.55, -0.70), 0.21, 0.100, 0.055, 'K'),
        ((0.100, 0.010, 0.010), (0.50, 0.35, -0.79), 0.22, 0.095, 0.055, 'K'),
        ((0.125, -0.020, 0.120), (0.72, 0.15, -0.68), 0.18, 0.100, 0.060, 'K'),
        ((0.115, -0.045, -0.085), (0.45, 0.10, -0.89), 0.20, 0.095, 0.060, 'K'),
        ((0.110, -0.150, -0.010), (0.70, -0.20, -0.68), 0.13, 0.075, 0.045, 'R'),
        ((0.080, -0.165, -0.075), (0.45, -0.30, -0.84), 0.12, 0.070, 0.045, 'R')]
# Ruff = mane: horizontal slices around the neck from under the ears/cheeks down to the chest, back half sunk into the
# neck and shoulders; z, centre y, half width, front, back. Last slice = jagged lower edge (5 points on the front).
RUFF = [(0.760, -0.370 + DYH, 0.150, 0.040, 0.100), (0.680, -0.380 + DYH, 0.215, 0.100, 0.150),
        (0.580, -0.385 + DYH, 0.235, 0.140, 0.170), (0.490, -0.395 + DYH, 0.225, 0.150, 0.150),
        (0.410, -0.405 + DYH, 0.185, 0.125, 0.100), (None, -0.410 + DYH, 0.130, 0.090, 0.050)]
RUFF_JAG = (0.265, 0.330, 0.345)       # point z, notch z, back z
NR = 12
# tail: thick bushy wedge from the rump top, back and ~20 deg down, clear of the hind legs
TAIL_CP = [(BY(0.385) + 0.85 * dy, BZ(0.548) + 0.85 * (z - 0.548)) for dy, z in [(0.0, 0.548), (0.083, 0.536), (0.178, 0.503), (0.275, 0.462),
                                                (0.365, 0.422), (0.430, 0.395), (0.470, 0.383)]]
TAIL_RAD = [(0.0, 0.058), (0.08, 0.090), (0.20, 0.112), (0.33, 0.115), (0.44, 0.092), (0.51, 0.055), (0.54, 0.028)]
TAIL_FLAT = 0.80                        # horizontal / vertical radius (brush is taller than wide)
TAIL_SPLIT = (0.15, 0.31)

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Ruff', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-01', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def lerp_tab(T, y):
    if y <= T[0][0]: return T[0][1:]
    if y >= T[-1][0]: return T[-1][1:]
    for a, b in zip(T, T[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, len(a)))


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def body_ring(yk, f, n=NB, pt=2.4, pb=2.7):
    out = []
    zt0 = lerp_tab(BODY_PROF, yk)[2]
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        y = yk
        for _ in range(5):
            w, zb, zt = lerp_tab(BODY_PROF, y)
            zc, h = (zt + zb) / 2, (zt - zb) / 2
            p = pt if s >= 0 else pb
            x = w * spow(c, 2 / p); z = zc + h * spow(s, 2 / p)
            y = yk + SLANT * f * (zt0 - z)
        out.append(Vector((x, y, z)))
    return out


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4, ph=0.0):
    out = []
    for k in range(n):
        th = math.pi / 2 + ph + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.86, depth=0.025, gap=0.001):
    """child's proximal end: boundary ring moved `gap` forward + a smaller ring hidden `depth` inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    inner = [c + (p - c) * scale + ab * depth for p in ring]
    edge = [p - ab * gap for p in ring]
    return [inner, edge]


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- coat label field (world space, |x| -> symmetric geometry; side picks the layout) ----------------
def wob(y, z, ax, s):
    ph = PHASE[s]
    return 0.015 * math.sin(13 * y + 7 * z + ph) + 0.008 * math.sin(29 * y - 17 * ax + 2.3 * ph)


def label(p, s):
    ax, y, z = abs(p.x), p.y, p.z
    w = wob(y, z, ax, s)
    if y < COLLAR[s] + 0.35 * (z - BZ(0.60)) + 0.6 * w: return W          # white chest under the ruff
    if z < (0.385 if y < 0 else 0.225) + 0.3 * w: return W             # white legs to the elbow / hock
    zb = lerp_tab(BODY_PROF, y)[1]
    if ax < 0.12 and z < zb + 0.045 + 0.5 * w and BELLY_Y[0] < y < BELLY_Y[1]: return W        # white belly
    if z > lerp_tab(SADDLE[s], y)[0] + w: return K                    # black saddle neck -> tail
    return R                                                           # orange flanks, thighs ("trousers")


def side_of(p):
    return 1 if p.x >= -1e-7 else -1


def crossing(a, b, s):
    """t in (0,1) of the first label change from a towards b (bisection) or None"""
    la = label(a, s)
    if label(b, s) == la: return None
    lo, hi = 0.0, 1.0
    for _ in range(14):
        m = (lo + hi) / 2
        if label(a.lerp(b, m), s) == la: lo = m
        else: hi = m
    return (lo + hi) / 2


def snap_rings(R, frozen_long):
    """move grid vertices onto the patch contours of BOTH side layouts (each vertex at most once, at most half an edge).
    Positions use |x|, so the mirrored vertex gets the same move -> mirror-exact geometry."""
    n = len(R[0]); snapped = [[0] * n for _ in R]           # 0 = free, else the side whose contour it lies on
    cand = []
    for j in range(len(R)):
        for k in range(n):
            a = R[j][k]
            nbs = [] if abs(a.x) < 1e-7 else [(j, (k + 1) % n), (j, (k - 1) % n)]   # centre-line verts never slide sideways
            if j not in frozen_long: nbs += [(jj, k) for jj in (j - 1, j + 1) if 0 <= jj < len(R)]
            aa = Vector((abs(a.x), a.y, a.z))
            for jj, kk in nbs:
                b = R[jj][kk]; bb = Vector((abs(b.x), b.y, b.z)) if a.x * b.x >= 0 or abs(a.x) < 1e-7 or abs(b.x) < 1e-7 else None
                if bb is None: continue
                for s in (1, -1):
                    t = crossing(aa, bb, s)
                    if t is not None and t <= 0.5: cand.append((round(t, 9), j, k, jj, kk, s))
    cand.sort()
    moved = 0
    for t, j, k, jj, kk, s in cand:
        if snapped[j][k] or snapped[jj][kk]: continue
        R[j][k] = R[j][k].lerp(R[jj][kk], t); snapped[j][k] = s; moved += 1
    return snapped, moved


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Dog'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')
        self.snapped = 0

    def _done(self, name, faces, ground=False):
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        self.P.comp.append((name, faces, ground))
        return faces

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        P = self.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(Rv[0]); faces = []
        for j in range(len(Rv) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k]
                for tri in ((a, b, c), (a, c, d)):
                    s = col(j, k) if callable(col) else col
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(Rv[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(Rv[-1]), cap1))
        return self._done(name, faces, ground)

    def loft_field(self, name, rings, snapped, cap0, cap1, override=None, ground=False):
        """quads split along the contour; triangle colour from its free vertices (label of its side), else centroid.
        override(j, k) -> slot or None forces a colour (joint bands, soles)."""
        P = self.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(Rv[0]); faces = []

        def lab(j, k, s):
            if snapped[j][k] == s: return None
            v = Rv[j][k].co; return label(Vector((abs(v.x), v.y, v.z)), s)

        def colour(tri, idx, s):
            ls = {lab(*i, s) for i in idx} - {None}
            if len(ls) == 1: return ls.pop()
            c = sum((v.co for v in tri), Vector()) / 3
            return label(Vector((abs(c.x), c.y, c.z)), s)
        for j in range(len(Rv) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                ia, ib, ic, id_ = (j, k), (j, k1), (j + 1, k1), (j + 1, k)
                a, b, c, d = Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k]
                s = side_of((a.co + b.co + c.co + d.co) / 4)
                la, lb, lc, ld = lab(*ia, s), lab(*ib, s), lab(*ic, s), lab(*id_, s)
                if la is None and lc is None: bd = False
                elif lb is None and ld is None: bd = True
                else: bd = (la is not None and lc is not None and la != lc) and not (lb is not None and ld is not None and lb != ld)
                tris = [((a, b, d), (ia, ib, id_)), ((b, c, d), (ib, ic, id_))] if bd else \
                       [((a, b, c), (ia, ib, ic)), ((a, c, d), (ia, ic, id_))]
                ov = override(j, k) if override else None
                for tri, idx in tris:
                    ts = side_of(sum((v.co for v in tri), Vector()) / 3)
                    faces.append(P.face(list(tri), ov if ov is not None else colour(tri, idx, ts)))
        for cap, r in ((cap0, 0), (cap1, len(Rv) - 1)):
            if cap is None: continue
            ring = list(reversed(Rv[0])) if r == 0 else list(Rv[-1])
            if cap is True:
                c = sum((v.co for v in ring), Vector()) / len(ring)
                cap = label(Vector((abs(c.x), c.y, c.z)), side_of(c))
            faces.append(P.face(ring, cap))
        return self._done(name, faces, ground)

    def cone(self, name, ring, apex, slot):
        P = self.P; bm = P.bm
        Rv = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(Rv)
        faces = [P.face(Rv, slot)] + [P.face([Rv[(k + 1) % n], Rv[k], A], slot) for k in range(n)]
        return self._done(name, faces)


# ---------------- body ----------------
def build_body(M):
    rings = [body_ring(y, f) for y, f in BODY_RINGS]
    snapped, moved = snap_rings(rings, FROZEN_LONG)
    M.snapped += moved
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]; zs = snapped[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft_field(part, rs, zs, True, True)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0))
            ext = [pre[1], pre[0]]
            M.loft_field(part, rs[:-1] + ext, zs[:-1] + [[0] * NB for _ in ext], True, True)
    M.pivot['Pelvis'] = Vector((0, BY(0.27), BZ(0.49)))
    M.pivot['Spine1'] = Vector((0, BODY_RINGS[5][0], BZ(0.48)))
    M.pivot['Spine2'] = Vector((0, BODY_RINGS[3][0], BZ(0.48)))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    L = lambda k: min(k, 7 - k)                            # 0 nape .. 3 throat
    M.loft('Neck1', rings[0:3], lambda j, k: (K, K, R, W)[L(k)], K, W)
    t = (cs[2] - cs[3]).normalized()
    pre = tuck(rings[2], t, 0.86, 0.025)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], lambda j, k: (K, K, R, W)[L(k)], K, K)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


def build_ruff(M):
    """mane ~1.5x the neck width: wraps the neck from under the ears/cheeks down to the chest, jagged lower edge with
    5 points; white front (3 shades), orange sides, black nape so it blends into the neck and shoulders"""
    pz, nz, bz = RUFF_JAG
    rings = []
    for z, cy, hw, df, db in RUFF:
        r = []
        for k in range(NR):
            th = 2 * math.pi * k / NR; c, sn = math.cos(th), math.sin(th)
            d = df if c >= 0 else db
            zz = z
            if z is None:
                Dv = min(k, NR - k)
                zz = bz if Dv == 6 else (pz if Dv % 2 == 0 else nz)
            r.append(Vector((hw * spow(sn, 0.8), cy - d * spow(c, 0.8), zz)))
        rings.append(r)
    def col(j, k):
        D = min(k, NR - 1 - k)                             # 0 front .. 5 nape
        if D <= 1: return W3 if j == 4 else W              # big front shield, shaded jagged fringe
        if D == 2: return K if j == 0 else (W3 if j == 4 else W2)
        if D == 3: return K if j == 0 else (R if j <= 3 else W2)              # orange side blends into the orange shoulder
        if D == 4: return K if j <= 1 else R
        return K if j <= 2 else R
    M.loft('Ruff', rings, col, K, W2)
    M.pivot['Ruff'] = Vector((0, -0.33 + DYH, 0.56))


# ---------------- head ----------------
# head face columns (k = face between ring vertex k and k+1): 11 top centre (blaze), 0/10 upper, 1/9 brow side,
# 2/8 side (eyes), 3/7 lower side (cheek), 4/6 under, 5 bottom centre. Segments j: 0 back .. 2 crown, 3 eyes/stop, 4-6 muzzle
HEAD_COLS = {'top':     'KWWWWWW', 'upper': 'KKKKWWW', 'brow': 'KKKRRWW', 'side': 'KKRRRRW',
             'low':     'KRRRWWW', 'under': 'RRRWWWW', 'bottom': 'WWWWWWW'}
_COLK = {11: 'top', 0: 'upper', 10: 'upper', 1: 'brow', 9: 'brow', 2: 'side', 8: 'side', 3: 'low', 7: 'low',
         4: 'under', 6: 'under', 5: 'bottom'}
SLOT = {'K': K, 'W': W, 'R': R, 'T': TAN}


def head_ring(y, wt, wb, zb, zt, p=2.4):
    angs = HEAD_ANG + [360 - a for a in reversed(HEAD_ANG)]
    zc, h = (zt + zb) / 2, (zt - zb) / 2; out = []
    for a in angs:
        r = math.radians(a); s, c = math.sin(r), math.cos(r)
        w = wt if c >= 0 else wb
        out.append(HP + Vector((w * spow(s, 2 / p), y, zc + h * spow(c, 2 / p))))
    return out


def build_head(M):
    rings = [head_ring(*r) for r in HEAD_RINGS]
    faces = M.loft('Head', rings, lambda j, k: SLOT[HEAD_COLS[_COLK[k]][j]], K, W)
    M.pivot['Head'] = HP.copy()
    return faces


def tuft(M, name, b, d, L, w, t, slot, sx):
    """angular fur tuft: flattened 4-sided pyramid, base sunk in the skull, apex out along d (mirrored for sx = -1)"""
    b = HP + Vector(b); d = Vector(d).normalized()
    n0 = Vector((1, 0, 0))
    v = (n0 - d * n0.dot(d)).normalized(); u = d.cross(v).normalized()
    ring = [b + u * w, b + v * t, b - u * w, b - v * t]
    apex = b + d * L
    if sx < 0: ring = [mir(p) for p in reversed(ring)]; apex = mir(apex)
    return M.cone(name, ring, apex, slot)


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d, back=0.4):
    d = Vector(d).normalized(); o = Vector(target) - d * back
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {tuple(target)}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n.normalized()


def build_face(M, head_faces):
    hb = bvh_of(head_faces)
    # eyes: round dark-brown 8-gon discs on the stop, looking forward (slightly out), 3 mm proud
    look = Vector((0.22, -0.95, 0.12)).normalized()
    hp, n = surf(hb, HP + Vector(EYE_AT), -look)
    ax = (n + 2 * look).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.003, e1, e2, EYE_R, 8), c - a * 0.014, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: broad dark pad on the muzzle tip (wider than tall, flat bottom), proud
    hp, n = surf(hb, HP + Vector((0, -0.40, 0.012)), (0, 1, 0))
    up = (Z - n * Z.dot(n)).normalized(); side = up.cross(n).normalized()
    if side.x < 0: side = -side
    nr = lambda off, sc, sy: ngon_ring(hp + n * off + up * 0.004, side, up, 0.046 * sc, 8, math.pi / 8, sy)
    M.loft('Nose', [nr(-0.018, 0.92, 0.62), nr(0.006, 1.0, 0.64), nr(0.022, 0.74, 0.58)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # jaw: short white chin block under the muzzle, top sunk into the muzzle
    jr = [(-0.190, 0.064, -0.138, -0.086), (-0.236, 0.056, -0.142, -0.092), (-0.276, 0.038, -0.128, -0.092)]
    M.loft('Jaw', [ring_xyz(HP + Vector((0, y, (a + b) / 2)), w, (b - a) / 2, (b - a) / 2, 6, X, Z) for y, w, a, b in jr],
           W, W, W)
    M.pivot['Jaw'] = HP + Vector((0, -0.17, -0.09))
    # mane: dark angular tufts from behind the ears down past the cheeks (frame the face), orange cheek tufts in front
    for b, d, L, w, t, s in MANE:
        for sx in (1, -1): tuft(M, 'Head', b, d, L, w, t, SLOT[s], sx)
    # ears: big semi-erect leaf leaning out, the upper half folds forward-out-down over a fixed hinge;
    # tan inner face framed by a black rim, black flap (tan underside)
    hp, n = surf(hb, HP + Vector(EAR_AT), (0, 0, -1))
    d1 = Vector(EAR_D1).normalized()
    fwd = Vector((0, -1, 0))
    wa = d1.cross(fwd).normalized()
    d2 = (EAR_FOLD[0] * d1 + EAR_FOLD[1] * fwd + EAR_FOLD[2] * wa).normalized()
    base = hp - d1 * 0.025; fold = base + d1 * EAR_UP; tip = fold + d2 * EAR_FLAP
    prof = [(1, 0), (0.55, 1), (-0.55, 1), (-1, 0), (-0.8, -1), (0.8, -1)]     # +b = inner (front) face
    hinge = d1.cross(d2).normalized()
    if hinge.dot(wa) < 0: hinge = -hinge
    rings = []; prev = fwd
    for c, t, hw, ht in ((base, d1, EAR_W[0], 0.022), (fold, (d1 + d2).normalized(), EAR_W[1], 0.018), (tip, d2, EAR_W[2], 0.006)):
        w_ = (hinge - t * hinge.dot(t)).normalized()
        ta = t.cross(w_).normalized()
        if ta.dot(prev) < 0: ta = -ta
        prev = ta
        rings.append([c + w_ * (a * hw) + ta * (b * ht) for a, b in prof])
    col = lambda j, k: TAN if k == 1 else K                  # tan inner face framed by a black rim, black flap
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, K, K)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)


# ---------------- legs ----------------
def build_legs(M):
    """plain tapered legs (lower leg emerges ~1.5 mm inside the upper), paws = flat-bottomed chamfered boxes 1.1x the
    leg width with a thin dark sole"""
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda yy, z, r, sy=1.0: ngon_ring(Vector((x, yy, z)), X, Y, r, 8, math.pi / 8, sy)
            if kind == 'Front':
                up = [(y, 0.53, 0.064, 1.10), (y, 0.41, 0.083, 1.10), (y - 0.005, 0.25, 0.070, 1.0)]
                lo = [(y - 0.005, 0.275, 0.0685), (y - 0.009, 0.16, 0.064), (y - 0.016, 0.045, 0.058)]
                fy = y - 0.022; z_up, z_lo = FRONT_SHOULDER_Z, 0.255
            else:
                up = [(y, 0.56, 0.058, 1.15), (y, 0.47, 0.078, 1.25), (y + 0.025, 0.35, 0.083, 1.15), (y + 0.055, 0.23, 0.070, 1.0)]
                lo = [(y + 0.055, 0.255, 0.0685), (y + 0.047, 0.15, 0.064), (y + 0.040, 0.045, 0.058)]
                fy = y + 0.032; z_up, z_lo = 0.54, 0.235
            ru = [ring(*r) for r in up]
            M.loft(kind + 'Upper' + sfx, ru, W if kind == 'Front' else R, W if kind == 'Front' else R,
                   W if kind == 'Front' else R)          # white front legs to the elbow; orange "trousers" to the hock
            M.loft(kind + 'Lower' + sfx, [ring(*r) for r in lo], W, W, W)
            pr = lambda z, r, sy: ngon_ring(Vector((x, fy, z)), X, Y, r, 8, math.pi / 8, sy)
            # round 5 (user: paws come loose from the shank in Walk): the paw box was only 0.064 high with its joint at z 0.03,
            # 1.5 cm below the shank end (z 0.045), so any turn of the paw opened a gap. Now a hidden neck (r 0.050, inside
            # the shank, r 0.058-0.064) reaches up to z 0.115 and the joint sits at z 0.075 inside that overlap.
            M.loft(kind + 'Foot' + sfx, [pr(0.0, 0.069, 1.28), pr(0.006, 0.072, 1.28), pr(0.040, 0.072, 1.26),
                                         pr(0.064, 0.062, 1.12), pr(0.072, 0.050, 1.0), pr(0.115, 0.050, 1.0)],
                   lambda j, k: SOLE if j == 0 else W, SOLE, W, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, up[0][0], z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, lo[0][0], z_lo))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, fy, 0.075))


# ---------------- tail: bushy, carried low, black top / rust underside / white brush tip ----------------
def tail_curve():
    P = [Vector((0, y, z)) for y, z in TAIL_CP]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    pts = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in [j / 12 for j in range(12)]:
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(P[-2])
    S = [0.0]
    for a, b in zip(pts, pts[1:]): S.append(S[-1] + (b - a).length)
    return pts, S


def tail_at(pts, S, s):
    s = max(0.0, min(s, S[-1]))
    for i in range(len(S) - 1):
        if S[i] <= s <= S[i + 1]:
            t = (s - S[i]) / max(1e-9, S[i + 1] - S[i])
            return pts[i].lerp(pts[i + 1], t), (pts[i + 1] - pts[i]).normalized()
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def build_tail(M):
    pts, S = tail_curve(); L = S[-1]
    rad = lambda s: lerp_tab(TAIL_RAD, s * TAIL_RAD[-1][0] / L)[0]

    def ring(s, r):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))                # e1 sideways, e2 up/down
        return [c + e1 * (TAIL_FLAT * (p - c).dot(e1)) + e2 * (p - c).dot(e2) for p in ngon_ring(c, e1, e2, r, 8, math.pi / 8)], c
    s1, s2 = 0.30 * L, 0.60 * L                       # stations relative to the tail length
    segs = [('Tail1', [0.0, 0.15 * L, s1]), ('Tail2', [s1, 0.45 * L, s2]), ('Tail3', [s2, 0.67 * L, 0.84 * L, L - 0.025, L])]
    for name, ss in segs:
        rs, cs = [], []
        for i, e in enumerate(ss):
            r = rad(e)
            if name == 'Tail3' and i == len(ss) - 1: r = 0.026
            rg, c = ring(e, r); rs.append(rg); cs.append(c)
        sv = list(ss)
        if name != 'Tail1':
            c, t = tail_at(pts, S, ss[0])
            pre = tuck(rs[0], -t, 0.86, 0.03)
            rs = [pre[0], pre[1]] + rs[1:]; cs = [cs[0], cs[0]] + cs[1:]; sv = [ss[0] - 0.03] + sv
        nb = len(rs) - 1
        cols = {}
        for j in range(nb):
            sm = (sv[j] + sv[j + 1]) / 2; cc = (cs[j] + cs[j + 1]) / 2
            for k in range(8):
                fc = (rs[j][k] + rs[j][(k + 1) % 8] + rs[j + 1][k] + rs[j + 1][(k + 1) % 8]) / 4
                upv = (fc - cc).normalized().z
                if sm < 0.60 * L: cols[(j, k)] = K if upv > -0.20 else R  # black top, orange underside
                elif sm < 0.67 * L: cols[(j, k)] = R                            # orange band
                else: cols[(j, k)] = W                                      # big white brush tip
        M.loft(name, rs, lambda j, k, cc=cols: cc[(j, k)], K if name != 'Tail3' else R, W if name == 'Tail3' else R)
        M.pivot[name] = tail_at(pts, S, ss[0])[0]
    return L


# ---------------- assemble ----------------
def com_of(bm):
    vol = 0.0; acc = Vector()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]; v = a.dot(b.cross(c)) / 6.0
            vol += v; acc += v * (a + b + c) / 4.0
    return acc / vol, vol


def build_model():
    M = Model()
    build_body(M); build_neck(M); build_ruff(M)
    bm = M.P.bm
    mg = ('Neck1', 'Neck2', 'Ruff')
    mv = {v for nm, faces, _ in M.P.comp if nm in mg for f in faces for v in f.verts}
    for v in mv: v.co += MOVE
    for k in mg: M.pivot[k] = M.pivot[k] + MOVE
    hf = build_head(M); build_face(M, hf)                  # head group built in place (final metres around HP)
    build_legs(M); tl = build_tail(M)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    com, vol = com_of(bm)
    shift = Vector((0, -com.y, 0))
    for v in bm.verts: v.co += shift
    for k in M.pivot: M.pivot[k] = M.pivot[k] + shift
    M.com = com + shift; M.vol = vol; M.shift = shift; M.tail_len = tl
    return M


def objects(M, coll, mat):
    P = M.P; bm = P.bm
    names = [c[0] for c in P.comp]
    missing = set(PART_ORDER) - set(names); extra = set(names) - set(PART_ORDER)
    if missing or extra: raise RuntimeError(f'parts missing {missing} extra {extra}')
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.1
    obs = {}
    for pi, nm in enumerate(PART_ORDER):
        b2 = bm.copy(); pl2 = b2.faces.layers.int['part']; sl2 = b2.faces.layers.int['slot']
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f[pl2] != pi], context='FACES')
        bmesh.ops.delete(b2, geom=[v for v in b2.verts if not v.link_faces], context='VERTS')
        bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3], quad_method='BEAUTY', ngon_method='BEAUTY')
        bmesh.ops.recalc_face_normals(b2, faces=b2.faces)
        uvl = b2.loops.layers.uv.new('UVMap')
        piv = M.pivot[nm]
        for f in b2.faces:
            f.smooth = False; uv = pc.cell_uv(f[sl2])
            for lp in f.loops: lp[uvl].uv = uv
        for v in b2.verts: v.co -= piv
        me = bpy.data.meshes.new(ASSET + '_' + nm); b2.to_mesh(me); b2.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(ASSET + '_' + nm, me); coll.objects.link(ob)
        ob.parent = root; ob.location = piv
        obs[nm] = ob
    return root, obs


def coplanar_all(M, coll):
    b2 = M.P.bm.copy()
    bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3])
    me = bpy.data.meshes.new('TMP_All'); b2.to_mesh(me); b2.free()
    ob = bpy.data.objects.new('TMP_All', me); coll.objects.link(ob)
    n, s = pc.coplanar_overlaps(ob)
    if n:
        pa = me.attributes['part'].data
        print('  coplanar pairs (parts):', [(PART_ORDER[pa[a].value], PART_ORDER[pa[b].value]) for a, b in s])
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def colour_asym(obs):
    """count left/right faces whose colour differs from the mirrored face (patch layouts differ on purpose)"""
    diff = 0
    for nm in ('Spine2', 'Spine1', 'Pelvis'):
        me = obs[nm].data; uv = me.uv_layers[0].data
        cen = {}
        for p in me.polygons:
            c = p.center; cen[(round(c.x, 4), round(c.y, 4), round(c.z, 4))] = uv[p.loop_start].uv[:]
        for (x, y, z), u in cen.items():
            if x > 1e-4 and cen.get((round(-x, 4), y, z), u) != u: diff += 1
    return diff


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    chk = pc.comp_checks(M.P)
    cop = coplanar_all(M, coll)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root, obs = objects(M, coll, mat)
    bpy.context.view_layer.update()
    print('TRIS per part:')
    tot = 0
    for nm in PART_ORDER:
        t = len(obs[nm].data.polygons); tot += t
        print(f'   {nm:14s} {t:4d}  pivot {tuple(round(c, 3) for c in obs[nm].location)}')
    print(f'TRIS total {tot} | target ~{BUDGET} (+15% = {int(BUDGET * 1.15)})')
    Wp = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in Wp(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for nm_ in ('Head', 'Nose', 'Jaw') for p in Wp(obs[nm_]))
    tail = max(p.y for nm_ in ('Tail1', 'Tail2', 'Tail3', 'Pelvis') for p in Wp(obs[nm_]))
    back = max(p.z for nm_ in ('Spine1', 'Spine2', 'Pelvis') for p in Wp(obs[nm_]))
    belly = min(p.z for p in Wp(obs['Spine1']))
    crown = max(p.z for p in Wp(obs['Head'])); ear = max(p.z for p in Wp(obs['Ear.L']))
    tailz = min(p.z for p in Wp(obs['Tail3']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->tail {tail - nose:.3f} back {back:.3f} belly {belly:.3f} crown {crown:.3f} '
          f'ear top {ear:.3f} tail tip low z {tailz:.3f} tail len {M.tail_len:.3f}')
    print(f'PATCH contour-snapped vertices {M.snapped} | body faces coloured differently L/R {colour_asym(obs)}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.8, 0.9, 0.45), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Dog_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B):
    views = [('ref', REF_VIEW), ('prev', PREVIEW_VIEW), ('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)),
             ('front', (0.0, -1.0, 0.12)), ('top', (0.3, -0.25, 1.0))]
    tiles = [rn.ref_tile(REF, 400)]
    for nm, v in views:
        p = os.path.join(CHECK, f'Dog_look_{nm}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.62, 0.78))
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Dog_look_sheet.png'))
    sm = rn.resize(rn.load_px(os.path.join(CHECK, 'Dog_look_ref.png')), 128)
    rn.compose([sm], 1, os.path.join(CHECK, 'Dog_look_128.png'), pad=0)
    os.remove(os.path.join(CHECK, 'Dog_look_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-01 Dog', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B)
    elif CMD == 'head':
        B = build(os.path.join(CHECK, 'tex'))
        hs = [B['obs'][n] for n in HEAD_GROUP]; tiles = [rn.ref_tile(REF, 300)]
        for i, v in enumerate(((0.38, -1.0, 0.22), (0.0, -1.0, 0.15), (1.0, 0.0, 0.1), (1.0, -0.78, 0.22))):
            p = os.path.join(CHECK, f'h{i}.png'); rn.preview(B['sc'], hs, p, view=v, fill=(0.62, 0.72))
            tiles.append(rn.resize(rn.load_px(p), 300)); os.remove(p)
        p = os.path.join(CHECK, 'hall.png'); rn.preview(B['sc'], list(B['obs'].values()), p, view=REF_VIEW, fill=(0.7, 0.8))
        tiles.append(rn.resize(rn.load_px(p), 300)); os.remove(p)
        rn.compose(tiles, 3, os.path.join(CHECK, 'Dog_head_sheet.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
