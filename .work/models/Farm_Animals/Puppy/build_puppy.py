# build_puppy.py - PET-03 Puppy (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_puppy.py -- PET-03 build|look|export
# build : parts + palette + checks (numbers only)
# look  : build + EEVEE sheet (reference, ref angle, preview angle, side, back, front, top) + 128 px thumbnail
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Dog/build_dog.py (Model/loft/tuck/tail/objects/look); shared modules are imported read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Puppy'
TAG = 'FarmAnimals_Puppy'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\PET-03.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_puppy')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.15, -1.0, 0.20)        # PET-03 reference: face to the camera, left flank receding to the right
PREVIEW_VIEW = (0.90, -1.0, 0.24)    # preview: three-quarter front-left, tail visible above the rump
PREVIEW_FILL = (0.72, 0.84)
BUDGET = 1500

PALETTE = ['#F2E8D8', '#E6D9C3', '#D9823A', '#E3A35E',     # 0 cream white, 1 white shade, 2 orange, 3 orange light (spare)
           '#3E3033', '#D8C8AE', '#2A1E1E', '#3A2E28',     # 4 black-brown coat, 5 cream shade, 6 nose, 7 sole
           '#2A1D17', '#B96C2C', '#B5835A', '#6E9F4A',     # 8 eye, 9 orange shade (spare), 10-15 series spares
           '#8E959B', '#C8473B', '#D8B65A', '#7A5233']
W, W2, R, RL, K, W3, NOSE, SOLE, EYE = range(9)
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))

# ---------------- layout (before the centre-of-mass shift) ----------------
# body: y, half width, z bottom, z top (chubby round barrel, back 0.30, belly 0.115)
BODY = [(-0.140, 0.058, 0.170, 0.265), (-0.115, 0.092, 0.128, 0.290), (-0.075, 0.108, 0.108, 0.300),
        (-0.035, 0.112, 0.100, 0.303), (0.005, 0.113, 0.098, 0.304), (0.045, 0.113, 0.099, 0.304),
        (0.085, 0.110, 0.104, 0.302), (0.120, 0.098, 0.118, 0.294), (0.150, 0.074, 0.142, 0.279),
        (0.170, 0.037, 0.182, 0.253)]
STRETCH0 = lambda y: y + max(0.0, y + 0.035) * 0.14
STRETCH = lambda y: -0.14 + (STRETCH0(y) + 0.14) * 1.15     # rework: body +15% (chest front fixed)
BODY = [(STRETCH(y), hw, zb, zt) for y, hw, zb, zt in BODY]
BODY_PHI = [20, 58, 95, 118, 150, 210, 242, 265, 302, 340]     # vertex angles from the top (left side first)
BODY_D = [1, 2, 3, 4, 5, 4, 3, 2, 1, 0]                        # face column: 0 top .. 5 belly
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 9)}
FRONT = (0.074, -0.072)
HIND = (0.074, STRETCH(0.100))

NECK_AXIS = [(-0.095, 0.235), (-0.085, 0.275), (-0.072, 0.310), (-0.060, 0.335), (-0.050, 0.352)]
NECK_R = [(0.075, 0.070), (0.075, 0.068), (0.072, 0.064), (0.066, 0.058), (0.045, 0.040)]

# head: y, half width, z bottom, z top, blaze half-angle (deg)   (huge puppy head: 0.25 wide, 0.22 tall)
HEAD = [(-0.035, 0.064, 0.300, 0.392, 14), (-0.058, 0.112, 0.258, 0.452, 10), (-0.090, 0.137, 0.244, 0.474, 8),
        (-0.122, 0.134, 0.242, 0.468, 8), (-0.147, 0.118, 0.246, 0.428, 9), (-0.168, 0.090, 0.251, 0.368, 18),
        (-0.190, 0.065, 0.256, 0.340, 27), (-0.205, 0.047, 0.265, 0.324, 31)]
HEAD_PHI = [35, 62, 95, 130, 160]                                # side vertices after the blaze vertex
HEAD_D = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1, 0]
#            D0 blaze, D1, D2, D3, D4, D5, D6 (bottom)
HEAD_COL = [[K, K, K, K, K, W, W],          # j0 back of the head (sunk)
            [K, K, K, K, K, W, W],          # j1 back of the skull
            [W, K, K, K, R, W, W],          # j2 crown / side: blaze starts, orange lower cheek side
            [W, R, K, K, R, W, W],          # j3 forehead: orange brows by the blaze
            [W, R, R, R, R, W, W],          # j4 face: eyes in the orange
            [W, W, W, R, R, W, W],          # j5 muzzle: white, orange cheeks at the sides
            [W, W, W, W, W, W, W]]          # j6 muzzle tip
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
EYE_R = 0.0138
EAR_X, EAR_Y = 0.085, -0.095
EAR_NE = (0.25, -0.97, 0.0)        # slab normal (outer face, front-out)
# hanging slab rings (horizontal rings, loft runs down): dz from the skull hit, dy lean, half width, half thickness;
# ring 0 sunk in the skull, ring 1 = folded-over ridge on top, rings 2-4 hang beside the head, tip at eye level
EAR_RINGS = [(-0.024, 0.0, 0.032, 0.012), (0.032, 0.0, 0.036, 0.011), (-0.012, -0.006, 0.047, 0.010),
             (-0.054, -0.010, 0.045, 0.0095), (-0.084, -0.012, 0.020, 0.006)]
EAR_SINK = 0.006                   # inner edge sunk into the head side
# chest bib rings (k = 0 front): z, (front, half width, back) from centre y RUFF_YC, radial facet jitter
RUFF_YC = -0.090
RUFF_RINGS = [(0.330, (0.060, 0.095, 0.030), 0.0), (0.290, (0.092, 0.150, 0.040), 0.045), (0.232, (0.112, 0.175, 0.050), -0.045),
              (0.180, (0.110, 0.168, 0.056), 0.035)]
RUFF_EDGE = (0.128, 0.030, (0.100, 0.155, 0.060))     # tip z, notch rise (<= 0.15 x head height), dims
NRF = 14

TAIL_DY = STRETCH(0.170) - 0.173
TAIL_CP = [(y + TAIL_DY, z) for y, z in [(0.140, 0.258), (0.172, 0.308), (0.210, 0.345), (0.255, 0.360), (0.290, 0.345),
                                        (0.308, 0.310)]]
TAIL_RAD = [(0.0, 0.034), (0.04, 0.054), (0.09, 0.068), (0.14, 0.072), (0.18, 0.060), (0.21, 0.024)]
TAIL_SPLIT = (0.060, 0.112)

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Ruff', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-03', 'build'])[:2]


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


def angle_ring(cen, hw, ht, hb, phis, pt=2.2, pb=2.4, ex=X, ez=Z):
    """superellipse ring, vertices at angles phi measured from the top (x = sin, z = cos)"""
    out = []
    for ph in phis:
        r = math.radians(ph); s, c = math.sin(r), math.cos(r)
        p = pt if c >= 0 else pb
        out.append(cen + ex * (hw * spow(s, 2 / p)) + ez * ((ht if c >= 0 else hb) * spow(c, 2 / p)))
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


def tuck(ring, axis_back, scale=0.86, depth=0.02, gap=0.001):
    """child's proximal end: boundary ring moved `gap` forward + a smaller ring hidden `depth` inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    inner = [c + (p - c) * scale + ab * depth for p in ring]
    edge = [p - ab * gap for p in ring]
    return [inner, edge]


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Puppy'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')

    def _done(self, name, faces, ground=False):
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        self.P.comp.append((name, faces, ground))
        return faces

    @staticmethod
    def quad_tris(a, b, c, d, spec, sym):
        """spec: slot | ('zj', top, bot, rising): border along the loft (body flank) |
        ('zk', slot ring j, slot ring j+1, diag): border around the ring (legs, tail)"""
        if isinstance(spec, tuple):
            if spec[0] == 'zj':
                _, top, bot, rising = spec
                if (a.co.z + d.co.z) > (b.co.z + c.co.z):
                    return [((a, b, d), top), ((b, c, d), bot)] if rising else [((a, b, c), bot), ((a, c, d), top)]
                return [((a, b, c), top), ((a, c, d), bot)] if rising else [((a, b, d), bot), ((b, c, d), top)]
            _, sj, sj1, dg = spec
            return [((a, b, c), sj), ((a, c, d), sj1)] if dg == 0 else [((a, b, d), sj), ((b, c, d), sj1)]
        cx = (a.co.x + b.co.x + c.co.x + d.co.x) / 4
        if not sym or cx >= 0: return [((a, b, c), spec), ((a, c, d), spec)]
        return [((a, b, d), spec), ((b, c, d), spec)]          # mirror-consistent diagonal on the right half

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False, sym=True):
        P = self.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(Rv[0]); faces = []
        for j in range(len(Rv) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                spec = col(j, k) if callable(col) else col
                for tri, s in self.quad_tris(Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k], spec, sym):
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(Rv[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(Rv[-1]), cap1))
        return self._done(name, faces, ground)

    def cone(self, name, ring, apex, slot):
        P = self.P; bm = P.bm
        Rv = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(Rv)
        faces = [P.face(Rv, slot)] + [P.face([Rv[(k + 1) % n], Rv[k], A], slot) for k in range(n)]
        return self._done(name, faces)


# ---------------- body ----------------
def body_col(jg, k):
    D = BODY_D[k]
    if jg == 0: return K if D <= 1 else W                   # chest front (under the ruff)
    if D <= 2: return K                                     # black saddle: back and upper flank
    if D == 3: return ('zj', K, R, jg % 2 == 0)             # zig-zag black / orange border along the flank
    if D == 4: return R                                     # orange lower flank
    return W                                                # white belly


def build_body(M):
    rings = [angle_ring(Vector((0, y, (zb + zt) / 2)), hw, (zt - zb) / 2, (zt - zb) / 2, BODY_PHI) for y, hw, zb, zt in BODY]
    for part, (i0, i1) in SPLIT.items():
        nreal = i1 - i0
        if part == 'Pelvis':
            rs = rings[i0:i1 + 1]
        else:   # rear end tucked into the parent behind it
            pre = tuck(rings[i1], (0, 1, 0))
            rs = rings[i0:i1] + [pre[1], pre[0]]
        col = lambda j, k, i0=i0, nreal=nreal: K if j >= nreal else body_col(i0 + j, k)
        M.loft(part, rs, col, W if i0 == 0 else K, R if part == 'Pelvis' else K)
    M.pivot['Pelvis'] = Vector((0, BODY[5][0], 0.21))
    M.pivot['Spine1'] = Vector((0, BODY[3][0], 0.21))
    M.pivot['Spine2'] = Vector((0, BODY[0][0] + 0.03, 0.21))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    L = lambda k: min(k, 7 - k)                            # 0 nape .. 3 throat
    M.loft('Neck1', rings[0:3], lambda j, k: (K, K, W, W)[L(k)], K, W)
    t = (cs[2] - cs[3]).normalized()
    pre = tuck(rings[2], t, 0.86, 0.02)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], lambda j, k: (K, K, W, W)[L(k)], K, K)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- ruff: 3 rows of skirt plates with pointed leaf tips, rows staggered ----------------
def ruff_pt(k, z, yc, dims, scale=1.0, inset=0.0):
    th = 2 * math.pi * k / NRF; c, s = math.cos(th), math.sin(th)
    df, hw, db = dims
    d = (df if c >= 0 else db) * scale - inset; w = hw * scale - inset
    return Vector((w * spow(s, 0.85), yc - d * spow(c, 0.85), z))


def build_ruff(M):
    """broad white chest bib: one faceted shell from under the cheeks to mid-foreleg, short zig-zag lower edge,
    back half and top sunk into body / neck / head (shoulder sides wrap outside the body)"""
    rings = []
    for z, dims, jit in RUFF_RINGS:
        rings.append([ruff_pt(k, z, RUFF_YC, dims, 1.0 + (jit if k % 2 == 0 else -jit)) for k in range(NRF)])
    zt, nh, dims = RUFF_EDGE
    edge, inner = [], []
    for k in range(NRF):
        tip = k % 2 == 0
        z = zt if tip else zt + nh; sc = 1.02 if tip else 0.95
        edge.append(ruff_pt(k, z, RUFF_YC, dims, sc))
        inner.append(ruff_pt(k, z + 0.02, RUFF_YC, dims, sc, inset=0.035))
    core = [ruff_pt(k, 0.226, RUFF_YC, RUFF_RINGS[2][1], 0.40) for k in range(NRF)]
    rs = rings + [edge, inner, core]
    nout = len(rings)
    M.loft('Ruff', rs, lambda j, k: W if j < nout else W3, W3, W3)
    M.pivot['Ruff'] = Vector((0, -0.085, 0.25))


# ---------------- head ----------------
def head_ring(y, hw, zb, zt, a):
    phis = [a] + HEAD_PHI + [360 - p for p in reversed(HEAD_PHI)] + [360 - a]
    return angle_ring(Vector((0, y, (zb + zt) / 2)), hw, (zt - zb) / 2, (zt - zb) / 2, phis, 2.2, 2.6)


def build_head(M):
    rings = [head_ring(*h) for h in HEAD]
    faces = M.loft('Head', rings, lambda j, k: HEAD_COL[j][HEAD_D[k]], K, W)
    M.pivot['Head'] = Vector((0, -0.05, 0.33))
    return faces


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
    # eyes: dark-brown 8-gon cone discs in the orange, 2 mm proud
    look = Vector((0.20, -0.97, 0.05)).normalized()
    hp, n = surf(hb, (0.053, -0.30, 0.386), (0, 1, 0))
    ax = (n + look).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.002, e1, e2, EYE_R, 8), c - a * 0.010, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: dark rounded triangle pad on the muzzle tip, proud
    hp, n = surf(hb, (0, -0.30, 0.312), (0, 1, 0))
    up = (Z - n * Z.dot(n)).normalized(); side = up.cross(n).normalized()
    if side.x < 0: side = -side
    shape = [(1.0, 0.45), (0.55, -0.20), (0.14, -0.85), (-0.14, -0.85), (-0.55, -0.20), (-1.0, 0.45), (-0.50, 0.75), (0.50, 0.75)]
    nr = lambda off, sc: [hp + n * off + side * (0.022 * sc * u) + up * (0.017 * sc * v) for u, v in shape]
    M.loft('Nose', [nr(-0.012, 0.85), nr(0.006, 1.0), nr(0.014, 0.62)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # jaw: white chin block under the muzzle
    jr = [(-0.150, 0.050, 0.232, 0.268), (-0.185, 0.045, 0.235, 0.270), (-0.208, 0.030, 0.248, 0.274)]
    M.loft('Jaw', [ring_xyz(Vector((0, y, (a + b) / 2)), w, (b - a) / 2, (b - a) / 2, 6, X, Z) for y, w, a, b in jr], W, W, W)
    M.pivot['Jaw'] = Vector((0, -0.15, 0.255))
    # ears: identical (mirrored) thick floppy flaps hanging from the skull top-side: root sunk in the skull, folded-over
    # ridge on top, slab hanging down beside the head (inner edge resting on the head side), tip at eye level.
    # Outer face dark brown; inner face + inner-edge bevel tan (the bevel shows from the front).
    hp, n = surf(hb, (EAR_X, EAR_Y, 0.60), (0, 0, -1))
    nE = Vector(EAR_NE).normalized()
    wv = Vector((-nE.y, nE.x, 0)).normalized()
    if wv.x < 0: wv = -wv
    prof = [(1, 0), (0.6, 1), (-0.3, 1), (-1, 0), (-0.3, -1), (0.6, -1)]     # +a outward edge, +b outer face
    rings = []
    for i, (dz, dy, w, th) in enumerate(EAR_RINGS):
        y = hp.y + dy; z = hp.z + dz
        if i == 0:
            c = Vector((hp.x - 0.010, y, z))
        else:
            hit = hb.ray_cast(Vector((0.5, y, z)), Vector((-1, 0, 0)))
            xs = hit[0].x if hit[0] is not None else hp.x - 0.02
            c = Vector((xs + wv.x * w - EAR_SINK, y, z))
        rings.append([c + wv * (a * w) + nE * (b * th) for a, b in prof])
    # k: 0 outer-edge bevel, 1 outer face, 2 inner-edge bevel (front), 3 inner-edge bevel (back), 4 inner face, 5 bevel
    col = lambda j, k: K if k in (0, 1, 5) or (j == 0 and k == 2) else RL
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, K, K, sym=False)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)


# ---------------- legs ----------------
def build_legs(M):
    """short thick 8-gon legs: orange upper with a zig-zag ring border to the white lower leg, big round white paws"""
    for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
        ring = lambda yy, z, r, sy=1.0: ngon_ring(Vector((x, yy, z)), X, Y, r, 8, math.pi / 8, sy)
        if kind == 'Front':
            up = [(y, 0.215, 0.041), (y, 0.160, 0.040), (y - 0.002, 0.120, 0.039), (y - 0.003, 0.098, 0.0386)]
            lo = [(y - 0.003, 0.104, 0.0384), (y - 0.004, 0.040, 0.036)]
            fy = y - 0.012; z_up, z_lo = 0.21, 0.10
        else:
            up = [(y - 0.010, 0.235, 0.034), (y - 0.005, 0.190, 0.050), (y, 0.150, 0.050), (y + 0.005, 0.115, 0.043),
                  (y + 0.008, 0.090, 0.0388)]
            lo = [(y + 0.008, 0.096, 0.0385), (y + 0.008, 0.040, 0.036)]
            fy = y + 0.002; z_up, z_lo = 0.22, 0.10
        nb = len(up) - 1
        ucol = lambda j, k, nb=nb: ('zk', R, W, k % 2) if j == nb - 1 else R
        pr = lambda z, r, sy: ngon_ring(Vector((x, fy, z)), X, Y, r, 8, math.pi / 8, sy)
        parts = [(kind + 'Upper', [ring(*r) for r in up], ucol, R, W, False),
                 (kind + 'Lower', [ring(*r) for r in lo], W, W, W, False),
                 (kind + 'Foot', [pr(0.0, 0.041, 1.15), pr(0.007, 0.044, 1.15), pr(0.032, 0.046, 1.13), pr(0.058, 0.031, 1.05)],
                  lambda j, k: SOLE if j == 0 else W, SOLE, W, True)]
        for nm, rs, col, c0, c1, gr in parts:
            for sfx, sx in (('.L', 1), ('.R', -1)):
                rr = rs if sx > 0 else [[mir(p) for p in r] for r in rs]
                M.loft(nm + sfx, rr, col, c0, c1, ground=gr, sym=False)
        for sfx, sx in (('.L', 1), ('.R', -1)):
            M.pivot[kind + 'Upper' + sfx] = Vector((x * sx, up[0][0], z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x * sx, lo[0][0], z_lo))
            M.pivot[kind + 'Foot' + sfx] = Vector((x * sx, fy, 0.03))


# ---------------- tail: big bushy plume raised in a curve, black base, zig-zag border, big white tip ----------------
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
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 8, math.pi / 8, 1.22)     # plume: taller than wide (broad from the side)
    s1, s2 = TAIL_SPLIT
    sm = 0.5 * (s2 + L)
    segs = [('Tail1', [0.0, 0.032, s1]), ('Tail2', [s1, 0.088, s2]), ('Tail3', [s2, 0.140, L - 0.055, L - 0.018, L])]
    for name, ss in segs:
        rs = []
        for i, e in enumerate(ss):
            r = rad(e)
            if name == 'Tail3' and i == len(ss) - 1: r = 0.022
            rs.append(ring(e, r))
        off = 0
        if name != 'Tail1':
            c, t = tail_at(pts, S, ss[0])
            pre = tuck(rs[0], -t, 0.86, 0.022)
            rs = [pre[0], pre[1]] + rs[1:]; off = 1
        if name == 'Tail3':
            col = lambda j, k, off=off: K if j < off else (('zk', K, W, k % 2) if j == off else W)
        else:
            col = K
        M.loft(name, rs, col, K, W if name == 'Tail3' else K, sym=False)
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
    hf = build_head(M); build_face(M, hf)
    build_legs(M); tl = build_tail(M)
    bm = M.P.bm
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


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    chk = pc.comp_checks(M.P)
    dg = [PART_ORDER[f[M.pl]] for f in M.P.bm.faces if f.calc_area() < 1e-9]
    if dg: print('  degenerate faces in', dg)
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
    print(f'TRIS total {tot} | target ~{BUDGET} (max ~2200)')
    Wp = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in Wp(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for nm_ in ('Head', 'Nose', 'Jaw') for p in Wp(obs[nm_]))
    rump = max(p.y for p in Wp(obs['Pelvis']))
    tail = max(p.y for nm_ in ('Tail1', 'Tail2', 'Tail3', 'Pelvis') for p in Wp(obs[nm_]))
    back = max(p.z for nm_ in ('Spine1', 'Spine2', 'Pelvis') for p in Wp(obs[nm_]))
    belly = min(p.z for p in Wp(obs['Spine1']))
    crown = max(p.z for p in Wp(obs['Head'])); ear = max(p.z for p in Wp(obs['Ear.L']))
    hw = max(p.x for p in Wp(obs['Head'])) * 2; tailtop = max(p.z for p in Wp(obs['Tail3']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | min z {lo[2]:.5f} | '
          f'nose->rump {rump - nose:.3f} nose->tail {tail - nose:.3f} back {back:.3f} belly {belly:.3f} crown {crown:.3f} '
          f'ear top {ear:.3f} head width {hw:.3f} tail top {tailtop:.3f} tail len {M.tail_len:.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.2f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def warm(B):
    """the first EEVEE render of a session comes out dark (lights/shadows not ready): render once and discard"""
    p = os.path.join(CHECK, 'warmup.png')
    rn.preview(B['sc'], list(B['obs'].values()), p, view=PREVIEW_VIEW, fill=(0.3, 0.3)); os.remove(p)


def look(B, tag='look'):
    views = [('ref', REF_VIEW), ('prev', PREVIEW_VIEW), ('side', (1, 0.0, 0.08)), ('back', (-0.55, 1.0, 0.3)),
             ('front', (0.0, -1.0, 0.10)), ('top', (0.3, -0.25, 1.0))]
    tiles = [rn.ref_tile(REF, 400)]
    warm(B)
    for nm, v in views:
        p = os.path.join(CHECK, f'Puppy_{tag}_{nm}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.66, 0.80))
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, f'Puppy_{tag}_sheet.png'))
    sm = rn.resize(rn.load_px(os.path.join(CHECK, f'Puppy_{tag}_ref.png')), 128)
    rn.compose([sm], 1, os.path.join(CHECK, f'Puppy_{tag}_128.png'), pad=0)
    os.remove(os.path.join(CHECK, f'Puppy_{tag}_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-03 Puppy', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B)
    elif CMD == 'head':
        B = build(os.path.join(CHECK, 'tex'))
        hs = [B['obs'][n] for n in HEAD_GROUP + ('Ruff',)]; tiles = []
        for i, v in enumerate(((0.0, -1.0, 0.15), (1.0, 0.0, 0.1), (0.8, -1.0, 0.22), (-0.4, 1.0, 0.4))):
            p = os.path.join(CHECK, f'h{i}.png'); rn.preview(B['sc'], hs, p, view=v, fill=(0.8, 0.8))
            tiles.append(rn.resize(rn.load_px(p), 400)); os.remove(p)
        rn.compose(tiles, 2, os.path.join(CHECK, 'Puppy_head_sheet.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        warm(B)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
