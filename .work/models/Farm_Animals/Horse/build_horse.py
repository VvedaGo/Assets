# build_horse.py - LIV-03 Horse (Farm Animals, skeleton Q-H), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_horse.py -- LIV-03 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_horse)
# look  : build + EEVEE frames from the reference angle and the side (TEMP)
# export: build + FBX (root empty + one mesh per skeleton part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Cow/Cat).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Horse'
TAG = 'FarmAnimals_Horse'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-03.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_horse')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -1.45, 0.30)         # LIV-03 reference: near (left, +X) side from the front-left, ~12 deg above
PREVIEW_VIEW = (1.0, -0.78, 0.16)

PALETTE = ['#A05A33', '#7E4426', '#2A2929', '#373636',     # 0 bay brown, 1 brown shade, 2 mane black, 3 mane black 2
           '#4E2C1C', '#3A221A', '#2A1D17', '#3C3B3E',     # 4 inner ear, 5 nostril, 6 eye, 7 hoof (reference dark grey)
           '#2D2C2E', '#4A494B', '#B5835A', '#6E9F4A',     # 8 sock, 9 joint band, 10-15 series spares
           '#8E959B', '#C8473B', '#F2E6C9', '#D8B65A']
BROWN, BROWN_D, MANE, MANE_D, EAR_IN, NOSTRIL, EYE, HOOF, SOCK, BAND = range(10)

# ---------------- layout (before the centre-of-mass shift) ----------------
# body profile: y, half width, z bottom, z top
BODY_PROF = [(-0.88, 0.24, 0.90, 1.36), (-0.82, 0.34, 0.79, 1.49), (-0.68, 0.39, 0.725, 1.60), (-0.50, 0.405, 0.71, 1.65),
             (-0.30, 0.41, 0.725, 1.62), (-0.10, 0.41, 0.75, 1.605), (0.10, 0.405, 0.78, 1.61), (0.30, 0.40, 0.825, 1.635),
             (0.48, 0.395, 0.885, 1.655), (0.62, 0.38, 0.96, 1.645), (0.73, 0.345, 1.045, 1.61), (0.81, 0.275, 1.15, 1.54),
             (0.86, 0.155, 1.27, 1.45)]
SPLIT = {'Spine2': (0, 4), 'Spine1': (4, 7), 'Pelvis': (7, 12)}
BODY_N = 14
# neck axis (y, z) and (half width, half depth) per ring; Neck1 = rings 0..2, Neck2 = 2..4
NECK_AX = [(-0.60, 1.29), (-0.79, 1.52), (-0.94, 1.71), (-1.05, 1.86), (-1.12, 1.97)]
NECK_R = [(0.325, 0.435), (0.30, 0.40), (0.26, 0.345), (0.21, 0.275), (0.17, 0.21)]
# head frame: tilted HEAD_TILT below horizontal, P0 = back of the skull
HEAD_TILT = math.radians(58)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))      # poll -> nose
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))      # forehead normal (front/up)
P0 = Vector((0, -1.10, 2.05))
HEAD_LEN = 0.615
# (s along U, half width, half height forehead side, half height jaw side)
HEAD_RINGS = [(-0.03, 0.10, 0.10, 0.10), (0.04, 0.18, 0.135, 0.16), (0.15, 0.20, 0.125, 0.18), (0.26, 0.19, 0.11, 0.15),
              (0.355, 0.175, 0.10, 0.12), (0.45, 0.165, 0.095, 0.105), (0.555, 0.172, 0.098, 0.10), (0.615, 0.152, 0.082, 0.085)]
FRONT = (0.195, -0.56)
HIND = (0.205, 0.56)
LEG_K = 1.26             # leg thickness factor (reference legs are chunky)
HEAD_SCALE = 1.18        # head group about P0 (reference head is big)
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nostrils', 'Forelock')
# mane strands: (s root on the neck 0 base..1 poll, max angle from the crest toward +X, backward sweep in s, width)
# (part, s root, hanging length (world -Z), backward drift (+Y), width) - strands hang by gravity on the near side
MANE_STRANDS = [('Mane1', 0.965, 0.30, 0.05, 0.17), ('Mane1', 0.85, 0.42, 0.07, 0.20), ('Mane2', 0.73, 0.52, 0.09, 0.22),
        ('Mane2', 0.61, 0.55, 0.10, 0.22), ('Mane3', 0.49, 0.50, 0.10, 0.22), ('Mane3', 0.38, 0.40, 0.09, 0.20),
        ('Mane3', 0.28, 0.28, 0.08, 0.17)]
MANE_RIDGE_H = {'Mane1': (0.055, 0.060), 'Mane2': (0.064, 0.066), 'Mane3': (0.055, 0.060)}   # differ per chunk: no coplanar joints
MANE_RIDGE = {'Mane1': [0.975, 0.88, 0.79], 'Mane2': [0.67, 0.55], 'Mane3': [0.42, 0.30, 0.18]}

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nostrils',
              'Forelock', 'Mane1', 'Mane2', 'Mane3',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']
MIRROR_SKIP = ()          # mane is symmetric about the crest now
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-03', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4, flat=True):
    """superellipse ring; flat=True puts a face (not a vertex) on the top and bottom"""
    out = []; ph = math.pi / n if flat else 0.0
    for k in range(n):
        th = math.pi / 2 + ph + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.86, depth=0.03, gap=0.001):
    """child's proximal end: boundary ring moved gap away from the parent + a smaller ring hidden inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    inner = [c + (p - c) * scale + ab * depth for p in ring]
    edge = [p - ab * gap for p in ring]
    return [inner, edge]


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Horse'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                for tri in ((a, b, c), (a, c, d)):
                    s = col(j, k) if callable(col) else col
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(R[-1]), cap1))
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return faces

    def strand(self, name, cs, sides, norms, ws, ts, col):
        """diamond-section strand: rings (c +- side*w/2, c +- n*t/2)"""
        rings = [[c + sd * (w / 2), c + n * (t / 2), c - sd * (w / 2), c - n * (t / 2)]
                 for c, sd, n, w, t in zip(cs, sides, norms, ws, ts)]
        return self.loft(name, rings, col, col, col)


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d, back=0.6):
    d = Vector(d).normalized(); o = Vector(target) - d * back
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no surface hit at {tuple(target)} dir {tuple(d)}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n.normalized()


def mir(p):
    return Vector((-p.x, p.y, p.z))


def lerp_list(L, s):
    """s in [0,1] over the list (vectors or floats)"""
    f = max(0.0, min(1.0, s)) * (len(L) - 1); i = min(int(f), len(L) - 2); t = f - i
    a, b = L[i], L[i + 1]
    return a + (b - a) * t


# ---------------- body ----------------
def body_ring(y, w, zb, zt):
    return ring_xyz(Vector((0, y, (zb + zt) / 2)), w, (zt - zb) / 2, (zt - zb) / 2, BODY_N, X, Z, 2.6, 2.2)


def build_body(M):
    rings = [body_ring(*r) for r in BODY_PROF]
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft(part, rs, BROWN, BROWN, BROWN)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0), 0.86, 0.05)
            M.loft(part, rs[:-1] + [pre[1], pre[0]], BROWN, BROWN, BROWN)
    M.pivot['Pelvis'] = Vector((0, BODY_PROF[7][0], 1.30))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[4][0], 1.30))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[0][0] + 0.30, 1.32))


# ---------------- neck ----------------
def neck_frames():
    cs = [Vector((0, y, z)) for y, z in NECK_AX]; T = []; E = []
    for i in range(len(cs)):
        t = (cs[min(i + 1, len(cs) - 1)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                    # e1 = crest direction (back/up)
        T.append(t); E.append(e1)
    return cs, T, E


def build_neck(M):
    cs, T, E = neck_frames()
    rings = [ring_xyz(c, w, h, h, 10, X, e1, 2.4, 2.4) for c, e1, (w, h) in zip(cs, E, NECK_R)]
    f1 = M.loft('Neck1', rings[0:3], BROWN, BROWN, BROWN)
    pre = tuck(rings[2], -T[2], 0.86, 0.035)
    f2 = M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], BROWN, BROWN, BROWN)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()
    return f1 + f2


# ---------------- head ----------------
def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, 10, X, VV, 2.6, 2.4) for s, w, ht, hb in HEAD_RINGS]
    faces = M.loft('Head', rings, BROWN, BROWN, BROWN)
    M.pivot['Head'] = P0 + U * 0.02
    return faces


def build_face(M, head_faces):
    bvh = bvh_of(head_faces)
    # eyes: dark 6-gon discs, 5 mm proud, looking sideways and a little forward
    hp, n = surf(bvh, P0 + U * 0.19 + VV * 0.04, (-1, 0, 0))
    ax = n.copy()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, U)
        M.loft('Eye' + sfx, [ngon_ring(c - a * 0.02, e1, e2, 0.036, 6, 0.0), ngon_ring(c + a * 0.008, e1, e2, 0.036, 6, 0.0)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nostrils: dark ovals on the flat muzzle front, near its sides
    hp, n = surf(bvh, P0 + U * HEAD_LEN + X * 0.062 + VV * 0.005, -U)
    ax = (n + X * 0.35).normalized()
    cen = []
    for sx in (1, -1):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, X)
        M.loft('Nostrils', [ngon_ring(c - a * 0.015, e1, e2, 0.021, 6, 0.0, 1.5), ngon_ring(c + a * 0.004, e1, e2, 0.021, 6, 0.0, 1.5)],
               NOSTRIL, NOSTRIL, NOSTRIL)
        cen.append(c)
    M.pivot['Nostrils'] = (cen[0] + cen[1]) / 2
    # ears: upright cupped leaves, dark inner face, roots sunk into the poll
    hp, n = surf(bvh, P0 + U * 0.035 + X * 0.095, -VV)
    u = Vector((0.16, 0.06, 1.0)).normalized()
    f = Vector((0.30, -1.0, 0.0)); f = (f - u * f.dot(u)).normalized()
    s = u.cross(f).normalized()
    if s.x < 0: s = -s
    prof = [(1.0, 0.35), (0.45, -0.05), (-0.45, -0.05), (-1.0, 0.35), (-0.5, -0.8), (0.5, -0.8)]
    base = hp - u * 0.035
    spec = [(0.0, 0.044, 0.044), (0.035, 0.062, 0.050), (0.12, 0.068, 0.054), (0.21, 0.050, 0.040), (0.30, 0.007, 0.007)]
    rings = [[base + u * h + s * (a * sa) + f * (b * sb) for a, b in prof] for h, sa, sb in spec]
    col = lambda j, k: EAR_IN if k in (0, 1, 2) and j >= 1 else BROWN
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, BROWN, BROWN)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # jaw: chin / lower lip block under the muzzle front
    jc = lambda s_: P0 + U * s_ - VV * 0.08
    jr = [(0.42, 0.055, 0.03, 0.02), (0.49, 0.088, 0.04, 0.035), (0.56, 0.092, 0.04, 0.035), (0.60, 0.076, 0.03, 0.028)]
    M.loft('Jaw', [ring_xyz(jc(s_), w, a, b, 8, X, VV, 2.4, 2.4) for s_, w, a, b in jr], BROWN, BROWN, BROWN)
    M.pivot['Jaw'] = jc(0.45)
    # forelock: 3 black strands lying on the forehead from the poll down between the eyes
    for i, (x0, x1, L, w) in enumerate([(0.0, 0.0, 0.36, 0.15), (0.055, 0.10, 0.28, 0.115)]):
        cs, sd, nn = [], [], []
        ss = [-0.01, 0.10 * L / 0.36 + 0.02, L * 0.62, L]
        for j, s_ in enumerate(ss):
            xx = x0 + (x1 - x0) * j / 3
            h, nrm = surf(bvh, P0 + U * s_ + X * xx, -VV)
            if i == 0:
                h.x = 0.0; nrm.x = 0.0; nrm.normalize()
            off = [-0.012, 0.016, 0.022, 0.016][j]
            cs.append(h + nrm * off); nn.append(nrm)
            side = X - nrm * X.dot(nrm); sd.append(side.normalized())
        ws = [w, w * 1.1, w * 0.8, 0.014]; ts = [0.06, 0.06, 0.045, 0.01]
        M.strand('Forelock', cs, sd, nn, ws, ts, MANE if i == 0 else MANE_D)
        if i > 0:
            M.strand('Forelock', [mir(c) for c in cs], [mir(v) for v in sd], [mir(v) for v in nn], ws, ts, MANE_D)
    M.pivot['Forelock'] = surf(bvh, P0, -VV)[0]


# ---------------- mane ----------------
def build_mane(M, neck_faces):
    bvh = bvh_of(neck_faces)
    bvh_nb = bvh_of(neck_faces + [f for nm, faces, _ in M.P.comp if nm in ('Spine2', 'Spine1') for f in faces])
    cs, T, E = neck_frames()

    def at(s):
        return lerp_list(cs, s), lerp_list(T, s).normalized(), lerp_list(E, s).normalized()

    def hit(s, phi):
        c, t, e1 = at(s); ph = math.radians(phi)
        d = e1 * math.cos(ph) + X * math.sin(ph)
        return surf(bvh, c, -d, 1.2)[0:2] + (t,)
    # crest ridge, one chunk per mane bone; Mane2/3 tuck into the chunk above them
    prev_end = None
    for part, ss in MANE_RIDGE.items():
        rings = []
        rh, rw = MANE_RIDGE_H[part]
        for s in ss:
            h, n, t = hit(s, 0.0)
            sd = X
            rings.append([h + n * rh, h + sd * rw - n * 0.015, h - n * 0.05, h - sd * rw - n * 0.015])
        if prev_end is not None:
            ab = (centroid(prev_end[1]) - centroid(prev_end[0])).normalized()     # into the parent chunk
            pre = tuck(prev_end[0], ab, 0.86, 0.035)
            rings = [pre[0], pre[1]] + rings
        M.loft(part, rings, MANE, MANE, MANE)
        prev_end = (rings[-1], rings[-2])
        M.pivot.setdefault(part, hit(ss[0], 0.0)[0])
    # strands: diamond blades from the crest down the near (+X) side, sweeping back, tips lifted off the neck
    for i, (part, s0, L, back, w) in enumerate(MANE_STRANDS):
        h0, n0, t0 = hit(s0, 0.0)
        cs_, nn_ = [h0 - n0 * 0.01 + X * 0.025], [n0]
        for j, f in enumerate((0.33, 0.67, 1.0)):
            tgt = Vector((0.0, h0.y + back * f, h0.z - L * f))
            h, n = surf(bvh_nb, tgt, (-1, 0, 0), 1.5)
            n = (n + Vector((0, 0, 0.25 * (1 - f)))).normalized()
            cs_.append(h + n * [0.03, 0.06, 0.09][j]); nn_.append(n)
        sd_ = []
        for j in range(4):
            dv = cs_[min(j + 1, 3)] - cs_[max(j - 1, 0)]
            sd_.append(dv.cross(nn_[j]).normalized())
        ws = [w, w * 1.05, w * 0.72, 0.016]; ts = [0.08, 0.08, 0.06, 0.012]
        c_ = MANE if i % 2 == 0 else MANE_D
        M.strand(part, cs_, sd_, nn_, ws, ts, c_)
        M.strand(part, [mir(c) for c in cs_], [mir(v) for v in sd_], [mir(v) for v in nn_], ws, ts, MANE_D if c_ == MANE else MANE)


# ---------------- legs ----------------
def build_legs(M):
    """Upper = body colour, tapers smoothly into the sock (its last two rings are a 4 mm parallel offset of the sock prism,
    so there is no cuff). Lower = ONE tapered black prism knee -> hoof (top apothem 1.15x the bottom, no rings/bands).
    Foot = hoof cap 1.15x the prism bottom + a hidden stem up inside the prism (pivot at the fetlock)."""
    Z_HOOF = 0.155
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r, yy, sy=1.0, xk=1.0: ngon_ring(Vector((x * xk, yy, z)), X, Y, r, 8, math.pi / 8, sy)
            if kind == 'Front':
                zk, rb, y_top, y_bot = 0.50, 0.095, y, y - 0.015          # knee; cannon leans 1.5 cm forward
            else:
                zk, rb, y_top, y_bot = 0.56, 0.098, 0.655, y + 0.04       # hock behind; cannon slopes forward
            rt = rb * 1.15
            z_top = zk + 0.06                                              # sock top hidden 6 cm inside the upper leg
            r_at = lambda z: rb + (rt - rb) * (z - 0.15) / (z_top - 0.15)
            y_at = lambda z: y_bot + (y_top - y_bot) * (z - 0.15) / (z_top - 0.15)
            if kind == 'Front':
                up = [ring(1.10, 0.120, y, 1.05, 0.70), ring(0.86, 0.165, y, 1.10, 0.95), ring(0.68, 0.142, y),
                      ring(z_top, r_at(z_top) + 0.004, y_at(z_top)), ring(zk, r_at(zk) + 0.004, y_at(zk))]
            else:
                up = [ring(1.16, 0.145, 0.46, 1.25, 0.70), ring(0.97, 0.180, 0.52, 1.15, 0.95), ring(0.76, 0.152, 0.58, 1.20),
                      ring(z_top, r_at(z_top) + 0.004, y_at(z_top)), ring(zk, r_at(zk) + 0.004, y_at(zk))]
            M.loft(kind + 'Upper' + sfx, up, BROWN, BROWN, BROWN)
            M.loft(kind + 'Lower' + sfx, [ring(z_top, rt, y_top), ring(0.15, rb, y_bot)], SOCK, SOCK, SOCK)
            fy = y_bot
            ft = [ring(0.27, rb * 0.80, y_at(0.27)), ring(Z_HOOF, rb * 0.80, fy), ring(Z_HOOF, rb * 1.15, fy),
                  ring(0.0, rb * 1.24, fy)]
            M.loft(kind + 'Foot' + sfx, ft, lambda j, k: SOCK if j == 0 else HOOF, SOCK, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y if kind == 'Front' else 0.44, 1.02 if kind == 'Front' else 1.05))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y_at(zk), zk))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y_at(0.27), 0.27))


# ---------------- tail ----------------
def build_tail(M):
    # Tail1: black dock out of the top of the rump
    pts = [Vector((0, 0.76, 1.46)), Vector((0, 0.89, 1.46)), Vector((0, 0.98, 1.39)), Vector((0, 1.03, 1.27))]
    rr = [0.08, 0.095, 0.10, 0.105]
    rings = []
    for i, (c, r) in enumerate(zip(pts, rr)):
        t = (pts[min(i + 1, 3)] - pts[max(i - 1, 0)]).normalized(); _, e1, e2 = pc.basis(t, X)
        rings.append(ngon_ring(c, e1, e2, r, 8, math.pi / 8))
    M.loft('Tail1', rings, MANE, MANE, MANE)
    M.pivot['Tail1'] = pts[0].copy()
    # Tail2: broad mass (deep front-back), 8 sides with alternating radius = strand ridges
    t2 = [(Vector((0, 1.03, 1.27)), 0.12, 0.15), (Vector((0, 1.10, 1.07)), 0.16, 0.24), (Vector((0, 1.15, 0.84)), 0.16, 0.25)]
    rings = []
    for i, (c, hw, hd) in enumerate(t2):
        t = (t2[min(i + 1, 2)][0] - t2[max(i - 1, 0)][0]).normalized(); _, e1, e2 = pc.basis(t, X)
        rings.append([c + e1 * (hw * math.cos(a) * (1.0 if k % 2 == 0 else 0.86)) + e2 * (hd * math.sin(a) * (1.0 if k % 2 == 0 else 0.86))
                      for k, a in enumerate([2 * math.pi * k / 8 for k in range(8)])])
    t_end = (t2[2][0] - t2[1][0]).normalized()
    pre = tuck(rings[0], -(t2[1][0] - t2[0][0]).normalized(), 0.86, 0.04)
    M.loft('Tail2', [pre[0], pre[1]] + rings[1:], lambda j, k: MANE if k % 2 == 0 else MANE_D, MANE, MANE)
    M.pivot['Tail2'] = t2[0][0].copy()
    # Tail3: 3 pointed strands from inside the mass end down to tips of different length
    base = t2[2][0]
    for i, (dx, tip, hd, hw) in enumerate([(0.0, Vector((0, 1.20, 0.30)), 0.22, 0.11), (0.08, Vector((0.11, 1.21, 0.44)), 0.15, 0.08),
                                           (-0.08, Vector((-0.11, 1.21, 0.44)), 0.15, 0.08)]):
        p0 = base + Vector((dx, 0, 0.06)); p1 = p0.lerp(tip, 0.45) + Vector((dx * 0.3, 0.02, 0)); p2 = p0.lerp(tip, 0.8)
        cs = [p0, p1, p2, tip]; sd, nn = [], []
        for j in range(4):
            t = (cs[min(j + 1, 3)] - cs[max(j - 1, 0)]).normalized()
            depth = (Y - t * Y.dot(t)).normalized(); sd.append(depth); nn.append(t.cross(depth).normalized())
        ws = [hd * 2, hd * 2 * 0.95, hd * 2 * 0.55, 0.014]; ts = [hw * 2, hw * 2 * 0.9, hw * 2 * 0.55, 0.01]
        M.strand('Tail3', cs, sd, nn, ws, ts, MANE if i == 0 else MANE_D)
    M.pivot['Tail3'] = base.copy()


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
    build_body(M)
    nf = build_neck(M)
    hf = build_head(M); build_face(M, hf)
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = P0 + (v.co - P0) * HEAD_SCALE
    for k in HEAD_GROUP: M.pivot[k] = P0 + (M.pivot[k] - P0) * HEAD_SCALE
    build_mane(M, nf)
    build_legs(M); build_tail(M)
    bm = M.P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    com, vol = com_of(bm)
    shift = Vector((0, -com.y, 0))
    for v in bm.verts: v.co += shift
    for k in M.pivot: M.pivot[k] = M.pivot[k] + shift
    M.com = com + shift; M.vol = vol; M.shift = shift
    return M


def objects(M, coll, mat):
    P = M.P; bm = P.bm
    names = [c[0] for c in P.comp]
    missing = set(PART_ORDER) - set(names); extra = set(names) - set(PART_ORDER)
    if missing or extra: raise RuntimeError(f'parts missing {missing} extra {extra}')
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.3
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
    chk = pc.comp_checks(M.P, MIRROR_SKIP)
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
    print(f'TRIS total {tot} | target ~2600 (+20% = 3120)')
    W = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in W(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for o in (obs['Head'], obs['Jaw']) for p in W(o))
    troot = M.pivot['Tail1'].y + 0.06
    withers = max(p.z for p in W(obs['Spine2']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->tail root {troot - nose:.3f} | withers(body top) {withers:.3f} | ear tips {hi[2]:.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'(all parts) worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Horse_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Horse_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-03 Horse', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_ref.png'), view=REF_VIEW, fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_side.png'), view=(1, 0.0, 0.1), fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_back.png'), view=(-0.7, 1.0, 0.3), fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_far.png'), view=(-1.0, -0.6, 0.2), fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_front.png'), view=(0.0, -1.0, 0.12), fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_top.png'), view=(0.3, -0.2, 1.0), fill=(0.62, 0.80))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Horse_look_prev.png'), view=PREVIEW_VIEW, fill=(0.62, 0.80))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.80))
