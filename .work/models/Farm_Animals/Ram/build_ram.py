# build_ram.py - LIV-12 Ram (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_ram.py -- LIV-12 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_ram)
# look  : build + EEVEE frames (reference angle, preview, side, front, back, top) to TEMP
# export: build + FBX (root empty + one mesh per part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Sheep/Lamb/Cow).
# Template: ../Sheep/build_sheep.py + ../Lamb/build_lamb.py (lobes, tuck rings, naming, objects/coplanar/check sheet),
# horns: ../Bull, ../Goat (tapered tube with a lighter tip) extended to a spiral. Shared modules are only imported.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Ram'
TAG = 'FarmAnimals_Ram'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-12.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_ram')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.85, -0.80, 0.30)        # LIV-12 reference: front-left three-quarter, ~15 deg above
PREVIEW_VIEW = (1.0, -0.95, 0.19)     # preview template of the pack (Sheep/Lamb/Cat/Cow)
TARGET = 2000

PALETTE = ['#F3EFE9', '#EEE9E2', '#E5DED2', '#DCD2C3',     # 0 wool up-facing, 1 wool base #EEE9E2, 2 wool down-facing, 3 core
           '#F0DCC3', '#D9BE9E', '#E8D1B4', '#D6BC9C',     # 4 face cream, 5 face shade, 6 leg cream, 7 spare
           '#2A1D17', '#3A2E28', '#E3BBAA', '#4B342C',     # 8 eye, 9 hoof, 10 ear inner, 11 nose
           '#B4865A', '#9A6E45', '#E2C9A0', '#C8473B']     # 12 horn, 13 horn ridge, 14 horn tip, 15 series spare
W0, W1, W2, W3, FACE, FACE_D, LEG, LEG_D, EYE, HOOF, EAR_IN, NOSE, HORN, HORN_D, HORN_T = range(15)

# ---------------- layout (before the centre-of-mass shift) ----------------
CORE_C = Vector((0, 0.03, 0.595))           # wool core superellipsoid (lobe centres sit on it)
CORE_R = (0.31, 0.45, 0.275)
END_E = 0.6                                 # section factor cos(theta)**END_E: fuller chest and rump
# lobe rows: (theta deg along the body: -90 front .. +90 rear, [(phi deg: 0 top, 90 left side, 180 bottom, radius)])
LOBE_ROWS = [(-66, [(118, 0.172), (180, 0.170)]),
             (-38, [(28, 0.168), (88, 0.170), (150, 0.162)]),
             (-10, [(0, 0.168), (60, 0.165), (120, 0.162)]),
             (18, [(30, 0.168), (90, 0.165), (150, 0.160)]),
             (46, [(0, 0.165), (60, 0.165), (120, 0.160)]),
             (74, [(40, 0.165), (130, 0.160)])]
LOBE_SINK = -0.15                            # lobe centre offset along the normal from the core surface (x radius)
LOBE_SPEC = [(-0.85, 0.0, 0.0), (-0.02, 1.0, 0.5), (0.60, 0.63, 0.0)]      # (h, radius, phase): hidden apex, equator, top
FRONT = (0.165, -0.25)                      # leg (x, y)
HIND = (0.165, 0.31)
# head frame
HEAD_TILT = math.radians(55)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))      # poll -> nose
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))      # forehead side
XV = Vector((1, 0, 0))
P0 = Vector((0, -0.49, 0.99))                                    # back of the skull, centre
HEAD_LEN = 0.33
# (s along U, half width, half height forehead side, half height throat side) - broad skull, Roman (convex) nose
HEAD_RINGS = [(0.00, 0.100, 0.090, 0.088), (0.06, 0.148, 0.122, 0.108), (0.14, 0.150, 0.124, 0.104),
              (0.21, 0.118, 0.116, 0.090), (0.28, 0.094, 0.098, 0.078), (0.33, 0.068, 0.070, 0.060)]
# poll tuft lobes between the horns: (s, v, x, radius) in the head frame (x>0 mirrored)
TUFT = [(0.050, 0.112, 0.0, 0.082), (0.115, 0.104, 0.0, 0.064), (-0.010, 0.090, 0.062, 0.070)]
HEAD_SCALE = 1.16
HEAD_Q = Vector((0, -0.42, 0.86))                 # head group scaled about the head/neck joint
HEAD_MOVE = Vector((0, -0.02, 0.03))
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'Horn.L', 'Horn.R', 'Wool_Head')
# neck ruff (heavier than the sheep): (centre, normal, radius); x>0 mirrored -> Wool_Neck
NECK_LOBES = [((0, -0.555, 0.700), (0, -1.0, -0.15), 0.150),          # throat bib under the chin
              ((0.165, -0.47, 0.780), (1.0, -0.45, 0.25), 0.150),      # neck sides
              ((0, -0.36, 0.900), (0, 0.25, 1.0), 0.145)]               # nape behind the poll
# horn spiral (left horn, x>0; mirrored): root on the skull, curl centre offset, plane normal, outward drift
HORN_ROOT = (0.020, 0.080, 0.085)            # (s, v, x) target on the skull, ray towards the head centre
HORN_C_OFF = Vector((0.09, 0.085, -0.135))    # curl centre = root + offset (world)
HORN_N = Vector((0.80, -0.58, 0.12)).normalized()    # curl plane normal (mostly sideways, a little forward)
HORN_TURN = 355.0                            # degrees swept from the root
HORN_R1 = 0.40                               # curl radius at the tip / at the root
HORN_ADV = 0.00                              # drift along the plane normal over the sweep (tip clears the root)
HORN_OUT = 0.20                              # drift outward (+x) over the sweep (tip clears the cheek)
HORN_ST = 20                                 # stations along the horn
HORN_TH = (0.060, 0.020)                     # tube apothem root -> tip
HORN_RIDGE = 0.92                            # every other station shrunk -> ridge rings

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Horn.L', 'Horn.R',
              'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2', 'Wool_Neck', 'Wool_Head']
WOOL_BONE = {'Wool_Pelvis': 'Pelvis', 'Wool_Spine1': 'Spine1', 'Wool_Spine2': 'Spine2', 'Wool_Neck': 'Neck1',
             'Wool_Head': 'Head'}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-12', 'build'])[:2]


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
        self.P = pc.Part('Ram'); self.pivot = {}
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

    def puff(self, name, c, n, r, nside, phase, tone, shade=W2):
        """wool lobe: hidden apex inside the core, wide equator ring, upper ring, flat top facet"""
        P = self.P; bm = P.bm
        ref = (1, 0, 0) if abs(Vector(n).normalized().x) < 0.9 else (0, 0, 1)
        _, e1, e2 = pc.basis(n, ref); t = Vector(n).normalized()
        step = 2 * math.pi / nside
        R = []
        for h, rr, ph in LOBE_SPEC:
            R.append([bm.verts.new(c + t * (h * r) + e1 * (rr * r * math.cos(phase + (k + ph) * step)) +
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
            faces.append(P.face([a[k1], a[k], apex], shade))
            faces.append(P.face([u[k], a[k], u[k1]], tone))
            faces.append(P.face([a[k], a[k1], u[k1]], tone))
        faces.append(P.face(list(u), tone))
        cen = sum((v.co for v in a), Vector()) / n
        for f in faces:
            f.normal_update(); nv = f.normal if f.normal.dot(f.calc_center_median() - cen) >= 0 else -f.normal
            f[P.slot] = W0 if nv.z > 0.55 else (W2 if nv.z < -0.35 else W1)
        self._reg(name, faces)
        return R

    def cone(self, name, front, apex, slot):
        """disc proud of a surface: flat front n-gon + a fan to a hidden apex inside the parent"""
        P = self.P; bm = P.bm
        F = [bm.verts.new(p) for p in front]; A = bm.verts.new(apex); n = len(F); faces = []
        for k in range(n):
            faces.append(P.face([F[(k + 1) % n], F[k], A], slot))
        faces.append(P.face(F, slot))
        self._reg(name, faces)

    def lobe(self, name, c, n, r, nside, phase, tone, centre_line):
        if centre_line:
            self.puff(name, c, n, r, nside, phase, tone); return 1
        R = self.puff(name, c, n, r, nside, phase, tone)
        self.puff_rings(name, [[mir(v.co) for v in ring] for ring in R], tone)
        return 2


def core_p(th, ph):
    f = max(math.cos(th), 0.0) ** END_E
    return CORE_C + Vector((CORE_R[0] * math.sin(ph) * f, CORE_R[1] * math.sin(th), CORE_R[2] * math.cos(ph) * f))


def ell_point(theta, phi):
    th, ph = math.radians(theta), math.radians(phi); e = 1e-3
    p = core_p(th, ph)
    n = (core_p(th + e, ph) - core_p(th - e, ph)).cross(core_p(th, ph + e) - core_p(th, ph - e)).normalized()
    if n.dot(p - CORE_C) < 0: n = -n
    return p, n


def wool_group(c):
    if c.y < -0.20: return 'Wool_Spine2'
    if c.y < 0.08: return 'Wool_Spine1'
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
    for i, (c, n, r) in enumerate(NECK_LOBES):
        c = Vector(c)
        k = M.lobe('Wool_Neck', c, Vector(n).normalized(), r, 6, 0.0 if c.x == 0 else 0.4, W1 if i % 2 == 0 else W0, c.x == 0)
        count += k; groups['Wool_Neck'] = groups.get('Wool_Neck', 0) + k
    return count, groups


def build_core(M):
    """hidden body core (Pelvis / Spine1 / Spine2), 6 sides, children tucked into the parent behind them"""
    def sec(y, f=1.0):
        s = max(0.0, 1 - ((y - CORE_C.y) / CORE_R[1]) ** 2) ** (END_E / 2) * f
        return ring_xyz(Vector((0, y, CORE_C.z)), CORE_R[0] * s, CORE_R[2] * s, CORE_R[2] * s, 6, XV, Vector((0, 0, 1)),
                        2.3, 2.3)
    ya = CORE_C.y - CORE_R[1]; yb = CORE_C.y + CORE_R[1]
    sp2 = [sec(ya + 0.03, 0.98), sec(-0.30), sec(-0.19)]
    sp1 = [sec(-0.19), sec(0.07)]
    pel = [sec(0.07), sec(0.30), sec(yb - 0.025, 0.98)]
    pre = tuck(sp2[-1], (0, 1, 0)); M.loft('Spine2', sp2[:-1] + [pre[1], pre[0]], W3, W3, W3)
    pre = tuck(sp1[-1], (0, 1, 0)); M.loft('Spine1', sp1[:-1] + [pre[1], pre[0]], W3, W3, W3)
    M.loft('Pelvis', pel, W3, W3, W3)
    M.pivot['Pelvis'] = Vector((0, 0.28, 0.66))
    M.pivot['Spine1'] = Vector((0, 0.07, 0.66))
    M.pivot['Spine2'] = Vector((0, -0.19, 0.665))


def build_neck(M):
    cs = [Vector((0, -0.28, 0.66)), Vector((0, -0.34, 0.73)), Vector((0, -0.40, 0.80)), Vector((0, -0.44, 0.86)),
          Vector((0, -0.47, 0.92))]
    rs = [0.135, 0.130, 0.122, 0.112, 0.100]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))
        rings.append(ring_xyz(c, rs[i], rs[i] * 0.95, rs[i] * 0.95, 6, XV, e1))
    M.loft('Neck1', [rings[0], rings[2]], W3, W3, W3)
    pre = tuck(rings[2], (cs[1] - cs[2]).normalized(), 0.86, 0.025)
    M.loft('Neck2', [pre[0], pre[1], rings[4]], W3, W3, W3)
    M.pivot['Neck1'] = Vector((0, -0.30, 0.69)); M.pivot['Neck2'] = cs[2].copy()


def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, 8, XV, VV, 2.6, 2.3) for s, w, ht, hb in HEAD_RINGS]

    def col(j, k):
        L = min(k, 7 - k)              # side 0 (forehead centre) .. 3 (throat sides)
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


def horn_path(root):
    """spiral centre line from the root: up over the top, back/out, down, forward under, tip curling up in front"""
    C = root + HORN_C_OFF
    nrm = HORN_N
    up = (Vector((0, 0, 1)) - nrm * nrm.z).normalized()
    bk = nrm.cross(up)
    if bk.y < 0: bk = -bk
    v0 = root - C; v0 = v0 - nrm * v0.dot(nrm)
    R0 = v0.length
    th0 = math.atan2(v0.dot(bk), v0.dot(up))
    print(f'HORN (pre head scale) curl R0 {R0:.3f} -> R1 {R0 * HORN_R1:.3f} | th0 {math.degrees(th0):.0f} deg, sweep {HORN_TURN:.0f} deg | tube {HORN_TH}')
    pts = []
    for i in range(HORN_ST):
        t = i / (HORN_ST - 1)
        th = th0 + math.radians(HORN_TURN) * t
        R = R0 * (1 - (1 - HORN_R1) * t)
        pts.append(C + up * (R * math.cos(th)) + bk * (R * math.sin(th)) + nrm * (HORN_ADV * t) + XV * (HORN_OUT * t ** 1.5))
    return pts


def build_horns(M, bvh):
    s, v, x = HORN_ROOT
    tgt = P0 + U * s + VV * v + XV * x
    root, n = surf(bvh, tgt, -(VV * 0.75 + XV * 0.66))
    pts = horn_path(root)
    rings = []
    # hidden root ring sunk into the skull along -tangent
    t0 = (pts[1] - pts[0]).normalized()
    sunk = root - t0 * 0.045
    _, e1, e2 = pc.basis(t0, (0, 0, 1))
    rings.append(ngon_ring(sunk, e1, e2, HORN_TH[0] * 0.85, 6, 0.0))
    prev_e1 = e1
    nst = len(pts)
    for i, c in enumerate(pts):
        t = (pts[min(i + 1, nst - 1)] - pts[max(i - 1, 0)]).normalized()
        # parallel transport of the ring frame (no twist between stations)
        e1 = (prev_e1 - t * prev_e1.dot(t)).normalized(); e2 = t.cross(e1); prev_e1 = e1
        u = i / (nst - 1)
        r = HORN_TH[0] + (HORN_TH[1] - HORN_TH[0]) * (u ** 1.15)
        if i % 2 == 1 and 0 < i < nst - 2: r *= HORN_RIDGE
        rings.append(ngon_ring(c, e1, e2, r, 6, 0.0))
    # blunt tip: small cap ring
    tt = (pts[-1] - pts[-2]).normalized(); e1 = (prev_e1 - tt * prev_e1.dot(tt)).normalized(); e2 = tt.cross(e1)
    rings.append(ngon_ring(pts[-1] + tt * 0.022, e1, e2, HORN_TH[1] * 0.45, 6, 0.0))
    nb = len(rings) - 1
    tip_j = nb - 3

    def hc(j, k):
        if j >= tip_j: return HORN_T
        return HORN if (j // 2) % 2 == 0 else HORN_D
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r_] for r_ in rings]
        M.loft('Horn' + sfx, rr, hc, HORN, HORN_T)
        M.pivot['Horn' + sfx] = root.copy() if sx > 0 else mir(root)


def build_face(M, head_faces):
    bvh = head_bvh(head_faces)
    # eyes: dark 8-gon discs, 6 mm proud, on the broad front of the face
    tgt = P0 + U * 0.150 + VV * 0.07 + XV * 0.10
    hp, n = surf(bvh, tgt, -(VV * 0.78 + XV * 0.50 - U * 0.15))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.006, e1, e2, 0.025, 8), c - a * 0.02, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: dark inverted-triangle pad on the muzzle end (forehead side of the cap)
    cap_c = P0 + U * HEAD_LEN + VV * 0.016
    poly = [(-1.0, 0.45), (-0.55, -0.25), (0.0, -0.80), (0.55, -0.25), (1.0, 0.45)]
    front = [cap_c + U * 0.005 + XV * (0.040 * a) + VV * (0.040 * b) for a, b in poly]
    M.cone('Nose', front, cap_c - U * 0.03, NOSE)
    M.pivot['Nose'] = cap_c.copy()
    # jaw: chin block on the throat side of the muzzle
    jr = [(0.15, 0.058, 0.028), (0.24, 0.068, 0.032), (0.315, 0.046, 0.022)]
    rings = []
    for s, w, h in jr:
        hb = min(HEAD_RINGS, key=lambda q: abs(q[0] - s))[3]
        c = P0 + U * s - VV * (hb - 0.006)
        rings.append(ring_xyz(c, w, h, h, 6, XV, VV, 2.2, 2.2))
    M.loft('Jaw', rings, FACE_D, FACE_D, FACE_D)
    M.pivot['Jaw'] = P0 + U * 0.15 - VV * 0.08
    # ears: leaves sideways under the horn roots, slightly forward and drooping; pink inner (front) face
    hp, n = surf(bvh, P0 + U * 0.085 + VV * 0.035 + XV * 0.14, -XV)
    d = Vector((1.0, -0.18, -0.45)).normalized()
    _, ea, eb = pc.basis(d, (0, 0.30, 1.0))
    if eb.y > 0: eb = -eb                              # +eb = front (inner) face
    prof = [(1, 0), (0.5, 1), (-0.5, 1), (-1, 0), (-0.5, -1), (0.5, -1)]
    base = hp - d * 0.060
    spec = [(0.0, 0.036, 0.017), (0.095, 0.058, 0.019), (0.155, 0.050, 0.016), (0.200, 0.014, 0.008)]
    rings = [[base + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = lambda j, k: EAR_IN if (k == 1 and j in (1, 2)) else FACE
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, FACE, FACE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    build_horns(M, bvh)
    # poll tuft between the horns (Wool_Head)
    nt = 0
    for i, (s, v, x, r) in enumerate(TUFT):
        c = P0 + U * s + VV * v + XV * x
        nn = (VV * max(v, 0.03) + XV * x * 1.2 - U * 0.02).normalized()
        nt += M.lobe('Wool_Head', c, nn, r, 6, 0.0 if x == 0 else 0.5, W0 if i % 2 == 0 else W1, x == 0)
    return nt


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r: ngon_ring(Vector((x, y, z)), X, Y, r, 6, 0.0)
            zk = 0.200 if kind == 'Front' else 0.215
            # one straight taper (top 1.15x bottom over the visible leg); Upper ends at the knee, Lower continues the
            # same taper 0.5% thinner with its top tucked inside Upper (no visible step), bottom sunk into the hoof cap
            lr = lambda z: 0.055 + 0.0346 * (z - 0.06)
            M.loft(kind + 'Upper' + sfx, [ring(0.52, lr(0.52)), ring(zk, lr(zk))], LEG, LEG, LEG)
            M.loft(kind + 'Lower' + sfx, [ring(zk + 0.03, lr(zk + 0.03) * 0.86), ring(zk + 0.001, lr(zk + 0.001) * 0.995),
                                          ring(0.05, lr(0.05) * 0.995)], LEG, LEG, LEG)
            M.loft(kind + 'Foot' + sfx, [ring(z, r) for z, r in [(0.0, 0.066), (0.060, 0.063), (0.072, 0.057)]],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, 0.50))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, zk))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.06))


def build_tail(M):
    a = Vector((0, 0.40, 0.74)); b = Vector((0, 0.54, 0.78))
    t = (b - a).normalized(); _, e1, e2 = pc.basis(t, (1, 0, 0))
    M.loft('Tail1', [ngon_ring(a, e1, e2, 0.052, 6, 0.0), ngon_ring(b, e1, e2, 0.044, 6, 0.0)], W2, W2, W2)
    M.pivot['Tail1'] = a.copy()
    c = Vector((0, 0.575, 0.795)); n = Vector((0, 1.0, 0.45)).normalized()
    M.puff('Tail2', c, n, 0.100, 6, 0.0, W0)
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
    print(f'TRIS total {tot} | target ~{TARGET} (+15% = {int(TARGET * 1.15)}) | lobes body+neck {M.n_lobes} {M.wool_groups} '
          f'+ tuft {M.n_tuft} + tail puff 1 = {M.n_lobes + M.n_tuft + 1}')
    W = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in W(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    wool = [p for k in ('Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2') for p in W(obs[k])]
    face = W(obs['Head']); horn = W(obs['Horn.L']) + W(obs['Horn.R'])
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | wool body top {max(p.z for p in wool):.3f} bottom {min(p.z for p in wool):.3f} '
          f'width {max(p.x for p in wool) - min(p.x for p in wool):.3f} length {max(p.y for p in wool) - min(p.y for p in wool):.3f}')
    print(f'HEAD face width {max(p.x for p in face) - min(p.x for p in face):.3f} face z {min(p.z for p in face):.3f}..'
          f'{max(p.z for p in face):.3f} nose y {min(p.y for p in face):.3f} | HORNS z {min(p.z for p in horn):.3f}..'
          f'{max(p.z for p in horn):.3f} span x {max(p.x for p in horn) - min(p.x for p in horn):.3f} '
          f'y {min(p.y for p in horn):.3f}..{max(p.y for p in horn):.3f} | eye z {obs["Eye.L"].location.z:.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


VIEWS = [('ref', REF_VIEW), ('side', (1, 0, 0.06)), ('front', (0.02, -1, 0.12)), ('back', (-0.5, 1, 0.3)),
         ('top', (0.25, -0.3, 1.0)), ('prev', PREVIEW_VIEW), ('low', (0.8, -0.6, 0.02)), ('right', (-1, -0.3, 0.15))]


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for nm, view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Ram_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Ram_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-12 Ram', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        tiles = [rn.ref_tile(REF, 400)]
        for nm, v in VIEWS[:6]:
            p = os.path.join(CHECK, f'Ram_look_{nm}.png')
            rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.62, 0.78))
            tiles.append(rn.resize(rn.load_px(p), 400)); os.remove(p)
        rn.compose(tiles, 3, os.path.join(CHECK, 'Ram_look_sheet.png'))
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
