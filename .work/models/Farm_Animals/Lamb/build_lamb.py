# build_lamb.py - LIV-05 Lamb (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_lamb.py -- LIV-05 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_lamb)
# look  : build + EEVEE frames at the reference angle and from the side (TEMP)
# export: build + FBX (root empty + one mesh per part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Sheep/Cow/Cat).
# Template: ../Sheep/build_sheep.py (wool-lobe approach, part naming, helpers copied; shared modules are read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Lamb'
TAG = 'FarmAnimals_Lamb'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-05.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_lamb')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.85, -0.75, 0.38)        # LIV-05 reference: front-left, ~20 deg above
PREVIEW_VIEW = (1.0, -0.95, 0.19)     # preview template of the pack (Sheep/Cat/Cow)

PALETTE = ['#F5F1EA', '#EEE9E2', '#E9E0D1', '#DCD0BE',     # 0 wool up-facing, 1 wool base #EEE9E2, 2 wool down-facing, 3 core
           '#F4DFBF', '#EBD2B0', '#EED5B2', '#EED5B2',     # 4 face cream, 5 face shade, 6 leg cream, 7 spare (= leg)
           '#2A1D17', '#3A2E28', '#EAD0AE', '#E6BE9E',     # 8 eye, 9 hoof, 10 ear inner (slightly darker cream), 11 nose
           '#B5835A', '#6E9F4A', '#8E959B', '#C8473B']     # 12-15 series spares
W0, W1, W2, W3, FACE, FACE_D, LEG, LEG_D, EYE, HOOF, EAR_IN, NOSE = range(12)

# ---------------- layout (before the centre-of-mass shift) ----------------
CORE_C = Vector((0, 0.02, 0.341))          # wool core ellipsoid (lobe centres sit on it)
CORE_R = (0.222, 0.268, 0.170)
# lobe rows: (theta deg along the body: -90 front .. +90 rear, [(phi deg: 0 top, 90 left side, 180 bottom, radius)])
LOBE_ROWS = [(-60, [(38, 0.118), (112, 0.116)]),
             (-24, [(0, 0.122), (72, 0.120), (140, 0.114)]),
             (14, [(36, 0.122), (108, 0.120)]),
             (50, [(0, 0.120), (72, 0.118), (140, 0.112)])]
LOBE_REAR = [((0, 0.272, 0.290), (0.0, 1.0, -0.25), 0.108)]           # rear centre lobe under the tail
LOBE_SINK = -0.21                            # lobe centre offset along the normal from the core surface
LOBE_SPEC = [(-0.80, 0.0, 0.0), (-0.02, 1.0, 0.5), (0.58, 0.64, 0.0)]      # (h, radius, phase): hidden apex, equator, top facet
LEG_RB = 0.046                               # leg apothem at the hoof top
FRONT = (0.118, -0.150)                     # leg (x, y)
HIND = (0.118, 0.160)
# head frame
HEAD_TILT = math.radians(28)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))      # poll -> nose
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))      # forehead side
XV = Vector((1, 0, 0))
P0 = Vector((0, -0.19, 0.665))                                   # back of the skull, centre
HEAD_LEN = 0.25
# (s along U, half width, half height forehead side, half height throat side)
HEAD_RINGS = [(0.00, 0.100, 0.095, 0.090), (0.05, 0.145, 0.128, 0.112), (0.12, 0.152, 0.126, 0.110),
              (0.185, 0.132, 0.106, 0.096), (0.215, 0.104, 0.084, 0.078), (0.25, 0.040, 0.036, 0.040)]
# head hood lobes: (s, v, x, radius) in the head frame (left + centre; x>0 mirrored)
TUFT = [(0.065, 0.138, 0.0, 0.100), (-0.050, 0.112, 0.0, 0.098), (0.030, 0.105, 0.112, 0.090),
        (-0.055, 0.060, 0.108, 0.086), (0.055, 0.000, 0.146, 0.080), (-0.085, 0.000, 0.0, 0.088)]
HEAD_SCALE = 1.22
HEAD_Q = Vector((0, -0.20, 0.56))                 # head group scaled about the head/neck joint
HEAD_MOVE = Vector((0, 0.030, -0.036))            # then moved down/back ~8% of the head size: chin sinks into the chest wool
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'Wool_Head')
# neck wool: (centre, normal, radius); centre line -> Wool_Neck (chest bib under the chin + nape)
NECK_LOBES = [((0, -0.300, 0.420), (0, -1.0, 0.15), 0.120), ((0, -0.255, 0.485), (0, -1.0, -0.35), 0.100)]   # chest bib + chin puff

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2', 'Wool_Neck', 'Wool_Head']
WOOL_BONE = {'Wool_Pelvis': 'Pelvis', 'Wool_Spine1': 'Spine1', 'Wool_Spine2': 'Spine2', 'Wool_Neck': 'Neck1',
             'Wool_Head': 'Head'}
TARGET = 1300


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-05', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def rnd(i, k=0):
    """deterministic pseudo random 0..1"""
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)


def mir(p):
    return Vector((-p.x, p.y, p.z))


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.86, depth=0.03, gap=0.001):
    """child's proximal end: boundary ring moved gap forward + a smaller ring hidden inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    inner = [c + (p - c) * scale + ab * depth for p in ring]
    edge = [p - ab * gap for p in ring]
    return [inner, edge]


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Lamb'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')

    def _reg(self, name, faces, ground=False):
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        self.P.comp.append((name, faces, ground))

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        """quads split into two triangles; col(j, k) per band/side or a slot"""
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                s = col(j, k) if callable(col) else col
                faces.append(P.face([R[j][k], R[j][k1], R[j + 1][k1]], s))
                faces.append(P.face([R[j][k], R[j + 1][k1], R[j + 1][k]], s))
        if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(R[-1]), cap1))
        self._reg(name, faces, ground)
        return R

    def puff(self, name, c, n, r, nside, phase, tone, hs=1.0, shade=W2):
        """wool lobe: antiprism dome - sunk base cap, wide equator ring A, upper ring B, flat top facet"""
        P = self.P; bm = P.bm
        ref = (1, 0, 0) if abs(Vector(n).normalized().x) < 0.9 else (0, 0, 1)
        _, e1, e2 = pc.basis(n, ref); t = Vector(n).normalized()
        step = 2 * math.pi / nside
        R = []
        for h, rr, ph in LOBE_SPEC:
            R.append([bm.verts.new(c + t * (h * r * hs) + e1 * (rr * r * math.cos(phase + (k + ph) * step)) +
                                   e2 * (rr * r * math.sin(phase + (k + ph) * step))) for k in range(1 if rr == 0 else nside)])
        return self._puff_faces(name, R, tone, shade)

    def puff_rings(self, name, rings, tone, shade=W2):
        R = [[self.P.bm.verts.new(p) for p in r] for r in rings]
        return self._puff_faces(name, R, tone, shade)

    def _puff_faces(self, name, R, tone, shade):
        P = self.P; faces = []
        b, a, u = R
        n = len(a); apex = b[0]
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([a[k1], a[k], apex], W1))
            faces.append(P.face([u[k], a[k], u[k1]], W1))
            faces.append(P.face([a[k], a[k1], u[k1]], W1))
        faces.append(P.face(list(u), W1))
        # one warm off-white; lighter on up-facing facets, slightly darker on down-facing ones (by facet direction)
        lc = sum((v.co for v in a), Vector()) / n
        for f in faces:
            d = (f.calc_center_median() - lc).normalized()
            f[P.slot] = W0 if d.z > 0.45 else (W2 if d.z < -0.35 else W1)
        self._reg(name, faces)
        return R

    def cone(self, name, front, apex, slot):
        """disc proud of a surface: flat front n-gon + a fan to a hidden apex inside the parent (n + n-2 tris)"""
        P = self.P; bm = P.bm
        F = [bm.verts.new(p) for p in front]; A = bm.verts.new(apex); n = len(F); faces = []
        for k in range(n):
            faces.append(P.face([F[(k + 1) % n], F[k], A], slot))
        faces.append(P.face(F, slot))
        self._reg(name, faces)

    def lobe(self, name, c, n, r, nside, phase, tone, centre_line):
        """one lobe on the centre line, or a lobe + its exact X mirror; returns the number of lobes"""
        if centre_line:
            self.puff(name, c, n, r, nside, phase, tone); return 1
        R = self.puff(name, c, n, r, nside, phase, tone)
        self.puff_rings(name, [[mir(v.co) for v in ring] for ring in R], tone)
        return 2


def ell_point(theta, phi):
    th, ph = math.radians(theta), math.radians(phi)
    d = Vector((math.sin(ph) * math.cos(th), math.sin(th), math.cos(ph) * math.cos(th)))
    p = CORE_C + Vector((CORE_R[0] * d.x, CORE_R[1] * d.y, CORE_R[2] * d.z))
    n = Vector((d.x / CORE_R[0], d.y / CORE_R[1], d.z / CORE_R[2])).normalized()
    return p, n


def wool_group(c):
    if c.y < -0.16: return 'Wool_Spine2'      # chest column
    if c.y < 0.15: return 'Wool_Spine1'       # two middle columns
    return 'Wool_Pelvis'


def build_wool(M):
    """body lobes in staggered rows, X-mirrored; tone checker so neighbours differ"""
    count = 0; groups = {}
    for ri, (theta, lobes) in enumerate(LOBE_ROWS):
        for ci, (phi, r) in enumerate(lobes):
            i = ri * 10 + ci
            p, n = ell_point(theta, phi)
            tilt = Vector(((rnd(i, 1) - 0.5) * 0.10, (rnd(i, 2) - 0.5) * 0.10, (rnd(i, 3) - 0.5) * 0.10))
            centre_line = phi in (0, 180)
            if centre_line: tilt.x = 0.0
            nn = (n + tilt).normalized()
            rr = r * (0.97 + 0.06 * rnd(i, 4))
            c = p + n * LOBE_SINK * rr
            tone = W0 if (ri + ci) % 2 == 0 else W1
            nside = 6
            phase = 0.0 if centre_line else (ri * 0.5 + ci * 0.3)
            g = wool_group(c)
            k = M.lobe(g, c, nn, rr, nside, phase, tone, centre_line); count += k
            groups[g] = groups.get(g, 0) + k
    for i, (c, n, r) in enumerate(LOBE_REAR):
        c = Vector(c); g = wool_group(c)
        k = M.lobe(g, c, Vector(n).normalized(), r, 6, 0.0, W1, True); count += k; groups[g] = groups.get(g, 0) + k
    for i, (c, n, r) in enumerate(NECK_LOBES):
        k = M.lobe('Wool_Neck', Vector(c), Vector(n).normalized(), r, 6, 0.0, W1 if i % 2 == 0 else W0, True)
        count += k; groups['Wool_Neck'] = groups.get('Wool_Neck', 0) + k
    return count, groups


def build_core(M):
    """hidden body core (Pelvis / Spine1 / Spine2), 6 sides, children tucked into the parent behind them"""
    def sec(y, f=1.0):
        s = math.sqrt(max(0.0, 1 - ((y - CORE_C.y) / CORE_R[1]) ** 2)) * f
        return ring_xyz(Vector((0, y, CORE_C.z)), CORE_R[0] * s, CORE_R[2] * s, CORE_R[2] * s, 6, XV, Vector((0, 0, 1)),
                        2.3, 2.3)
    ya = CORE_C.y - CORE_R[1]; yb = CORE_C.y + CORE_R[1]
    sp2 = [sec(ya + 0.025, 0.98), sec(-0.17), sec(-0.09)]
    sp1 = [sec(-0.09), sec(0.08)]
    pel = [sec(0.08), sec(0.20), sec(yb - 0.025, 0.98)]
    pre = tuck(sp2[-1], (0, 1, 0)); M.loft('Spine2', sp2[:-1] + [pre[1], pre[0]], W3, W3, W3)
    pre = tuck(sp1[-1], (0, 1, 0)); M.loft('Spine1', sp1[:-1] + [pre[1], pre[0]], W3, W3, W3)
    M.loft('Pelvis', pel, W3, W3, W3)
    M.pivot['Pelvis'] = Vector((0, 0.17, 0.38))
    M.pivot['Spine1'] = Vector((0, 0.08, 0.38))
    M.pivot['Spine2'] = Vector((0, -0.09, 0.385))


def build_neck(M):
    cs = [Vector((0, -0.150, 0.420)), Vector((0, -0.185, 0.480)), Vector((0, -0.205, 0.545)), Vector((0, -0.215, 0.600)),
          Vector((0, -0.215, 0.650))]
    rs = [0.090, 0.086, 0.080, 0.075, 0.070]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))
        rings.append(ring_xyz(c, rs[i], rs[i] * 0.95, rs[i] * 0.95, 6, XV, e1))
    M.loft('Neck1', [rings[0], rings[2]], W3, W3, W3)
    pre = tuck(rings[2], (cs[1] - cs[2]).normalized(), 0.86, 0.025)
    M.loft('Neck2', [pre[0], pre[1], rings[4]], W3, W3, W3)
    M.pivot['Neck1'] = Vector((0, -0.165, 0.445)); M.pivot['Neck2'] = cs[2].copy()


def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, 8, XV, VV, 2.6, 2.3) for s, w, ht, hb in HEAD_RINGS]

    def col(j, k):
        L = min(k, 7 - k)              # side 0 (forehead centre) .. 3 (throat sides); k=3,4 straddle the throat
        if L >= 3 and j <= 2: return FACE_D
        return FACE
    M.loft('Head', rings, col, FACE, FACE)
    M.pivot['Head'] = P0 + U * 0.02
    return list(M.P.comp[-1][1])


def head_bvh(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d):
    d = Vector(d).normalized(); o = Vector(target) - d * 0.4
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no head hit at {target}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n


def build_face(M, head_faces):
    bvh = head_bvh(head_faces)
    # eyes: dark 8-gon discs, 5 mm proud, on the broad front of the face, wide apart
    tgt = P0 + U * 0.14 + VV * 0.06 + XV * 0.095
    hp, n = surf(bvh, tgt, -(VV * 0.75 + XV * 0.45 - U * 0.25))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.006, e1, e2, 0.025, 8), c - a * 0.018, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: small warm pad on the muzzle end (forehead side of the cap), low contrast as in the reference
    cap_c = P0 + U * HEAD_LEN + VV * 0.004
    M.cone('Nose', ngon_ring(cap_c + U * 0.004, XV, VV, 0.020, 6, 0.0, 0.62), cap_c - U * 0.02, NOSE)
    M.pivot['Nose'] = cap_c.copy()
    # jaw: chin block on the throat side of the muzzle
    jr = [(0.13, 0.050, 0.024), (0.19, 0.060, 0.028), (0.235, 0.034, 0.018)]
    rings = []
    for s, w, h in jr:
        hb = min(HEAD_RINGS, key=lambda q: abs(q[0] - s))[3]
        c = P0 + U * s - VV * (hb - 0.006)
        rings.append(ring_xyz(c, w, h, h, 6, XV, VV, 2.2, 2.2))
    M.loft('Jaw', rings, FACE, FACE, FACE)
    M.pivot['Jaw'] = P0 + U * 0.13 - VV * 0.07
    # ears: thin flat cream leaves at the head sides just below the wool cap, pointing straight sideways (no sweep),
    # ~77 deg from vertical = 13 deg drooping; leaf face turned forward/up so both read from the front and the 3/4 camera.
    # Sizes are before the head-group scale (x1.22): visible length 0.167 -> 0.20 m = 0.55 x face width 0.371,
    # thickness 0.036 -> 0.044 m = 0.12 x, width 0.088 -> 0.107 m. Built once (.L) and mirrored exactly (.R).
    hp, n = surf(bvh, P0 + U * 0.090 + VV * 0.035 + XV * 0.13, -XV)
    d = Vector((1.0, -0.27, -0.24)).normalized()      # sideways, 15 deg forward (far ear clears the face), 13 deg down
    _, ea, eb = pc.basis(d, (0, 0.45, 0.90))          # ea = leaf width (up, tipped back), eb = leaf normal (thickness)
    if eb.y > 0: eb = -eb                              # +eb = front (inner) face, facing forward and up
    prof = [(1, 0), (0.5, 1), (-0.5, 1), (-1, 0), (-0.5, -1), (0.5, -1)]     # flat lens section
    base = hp - d * 0.040                              # root sunk 4 cm into the head
    spec = [(0.0, 0.024, 0.011), (0.085, 0.044, 0.018), (0.160, 0.038, 0.014), (0.207, 0.008, 0.005)]
    rings = [[base + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = lambda j, k: EAR_IN if (k == 1 and j in (1, 2)) else FACE
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, FACE, FACE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # hood: wool lobes on the poll and down the sides, framing the face (Wool_Head)
    nt = 0
    for i, (s, v, x, r) in enumerate(TUFT):
        c = P0 + U * s + VV * v + XV * x
        nn = (VV * max(v, 0.03) + XV * x * 1.2 - U * 0.03).normalized()
        nt += M.lobe('Wool_Head', c, nn, r, 6, 0.0 if x == 0 else rnd(100 + i) * 6.28, W0 if i % 2 == 0 else W1, x == 0)
    return nt


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r: ngon_ring(Vector((x, y, z)), X, Y, r, 6, 0.0)
            # upper: from inside the core down to a raised darker knee/hock band; lower sunk into the band and the hoof
            rz = lambda z: LEG_RB + (z - 0.06) / 0.24 * (LEG_RB * 0.15)       # linear taper, r(0.30) = 1.15 r(0.06)
            up = [(0.30, rz(0.30)), (0.11, rz(0.11))]
            lo = [(0.125, rz(0.125) - 0.0015), (0.045, rz(0.045) - 0.0015)]   # tucked 1.5 mm inside the upper
            M.loft(kind + 'Upper' + sfx, [ring(z, r) for z, r in up], LEG, LEG, LEG)
            M.loft(kind + 'Lower' + sfx, [ring(z, r) for z, r in lo], LEG, LEG, LEG)
            M.loft(kind + 'Foot' + sfx, [ring(z, r) for z, r in [(0.0, 0.054), (0.060, 0.051)]],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, 0.27))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, 0.112))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.05))


def build_tail(M):
    a = Vector((0, 0.250, 0.395)); b = Vector((0, 0.335, 0.415))
    t = (b - a).normalized(); _, e1, e2 = pc.basis(t, (1, 0, 0))
    M.loft('Tail1', [ngon_ring(a, e1, e2, 0.036, 6, 0.0), ngon_ring(b, e1, e2, 0.030, 6, 0.0)], W2, W2, W2)
    M.pivot['Tail1'] = a.copy()
    c = Vector((0, 0.352, 0.420)); n = Vector((0, 1.0, 0.25)).normalized()
    M.puff('Tail2', c, n, 0.084, 6, 0.0, W0)
    M.pivot['Tail2'] = b.copy()


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
    build_core(M); build_neck(M)
    hf = build_head(M); M.n_tuft = build_face(M, hf)
    build_legs(M); build_tail(M)
    M.n_lobes, M.wool_groups = build_wool(M)
    bm = M.P.bm
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE + HEAD_MOVE
    for k in HEAD_GROUP:
        if k != 'Wool_Head': M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE + HEAD_MOVE
    for g, b in WOOL_BONE.items():
        M.pivot[g] = M.pivot[b].copy()
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
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


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
    print(f'TRIS total {tot} | target ~{TARGET} (+20% = {int(TARGET * 1.2)}) | lobes body+neck {M.n_lobes} {M.wool_groups} '
          f'+ hood {M.n_tuft} + tail puff 1 = {M.n_lobes + M.n_tuft + 1}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    wool = [o.matrix_world @ v.co for k in ('Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2') for o in (obs[k],)
            for v in o.data.vertices]
    hp = [o.matrix_world @ v.co for k in HEAD_GROUP for o in (obs[k],) for v in o.data.vertices]
    face = [obs['Head'].matrix_world @ v.co for v in obs['Head'].data.vertices]
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | wool body top {max(p.z for p in wool):.3f} bottom {min(p.z for p in wool):.3f} '
          f'width {max(p.x for p in wool) - min(p.x for p in wool):.3f} length {max(p.y for p in wool) - min(p.y for p in wool):.3f}')
    print(f'HEAD group z {min(p.z for p in hp):.3f}..{max(p.z for p in hp):.3f} | face width {max(p.x for p in face) - min(p.x for p in face):.3f} '
          f'face z {min(p.z for p in face):.3f}..{max(p.z for p in face):.3f} nose y {min(p.y for p in face):.3f}')
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
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.8, 0.9, 0.45), (0.03, 1, 0.2), PREVIEW_VIEW, (0.8, -0.6, 0.02), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Lamb_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Lamb_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-05 Lamb', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        for nm, v in (('ref', REF_VIEW), ('side', (1, 0.0, 0.1)), ('front', (0.0, -1, 0.15)), ('back', (-0.5, 1, 0.3)),
                      ('prev', PREVIEW_VIEW), ('top', (0.25, -0.3, 1.0)), ('low', (0.9, -0.6, 0.03))):
            rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, f'Lamb_look_{nm}.png'), view=v, fill=(0.62, 0.78))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        bad = (B['checks']['nonmanifold'], B['checks']['loose'], B['checks']['degenerate'], B['coplanar'])
        if any(bad) or B['checks']['problems'] or abs(B['minz']) > 1e-5:
            raise SystemExit(f'EXPORT ABORTED: checks failed {bad} {B["checks"]["problems"]} minz {B["minz"]}')
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
