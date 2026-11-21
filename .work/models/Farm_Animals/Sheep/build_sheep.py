# build_sheep.py - LIV-04 Sheep (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_sheep.py -- LIV-04 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_sheep)
# look  : build + EEVEE frames at the reference angle and from the side (TEMP)
# export: build + FBX (root empty + one mesh per part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Cow/Cat).
# Template: ../Cat/build_cat.py (helpers copied here; shared modules are read-only).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Sheep'
TAG = 'FarmAnimals_Sheep'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-04.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_sheep')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.85, -0.75, 0.35)        # LIV-04 reference: front-left, ~17 deg above
PREVIEW_VIEW = (0.85, -1.0, 0.20)     # pack preview template, a bit more frontal like the LIV-04 reference

PALETTE = ['#EEE9E2', '#F4F1EC', '#E3DDD4', '#E3DDD4',     # 0 wool, 1 wool top facets, 2 wool under facets, 3 core (= 2)
           '#7C5547', '#5F4137', '#553A32', '#43302A',     # 4 face, 5 face shade, 6 leg, 7 leg dark (spare)
           '#2A1D17', '#3A2E28', '#6B463B', '#3B2722',     # 8 eye, 9 hoof, 10 ear inner, 11 nose
           '#946A5A', '#6E9F4A', '#8E959B', '#C8473B']     # 12 eye ring (lighter brow), 13-15 series spares
W0, W1, W2, W3, FACE, FACE_D, LEG, LEG_D, EYE, HOOF, EAR_IN, NOSE, EYE_RING = range(13)

# ---------------- layout (before the centre-of-mass shift) ----------------
CORE_C = Vector((0, 0.02, 0.52))           # wool core superellipsoid (lobe centres sit on it)
CORE_R = (0.28, 0.415, 0.225)
END_E = 0.6                                 # section factor cos(theta)**END_E: fuller chest and rump than an ellipsoid
# lobe rows: (theta deg along the body: -90 front .. +90 rear, [(phi deg: 0 top, 90 left side, 180 bottom, radius)])
LOBE_ROWS = [(-68, [(122, 0.145), (180, 0.145)]),
             (-38, [(30, 0.150), (90, 0.150), (152, 0.145)]),
             (-10, [(0, 0.155), (60, 0.150), (120, 0.148)]),
             (18, [(30, 0.155), (90, 0.150), (152, 0.145)]),
             (46, [(0, 0.150), (60, 0.150), (120, 0.148)]),
             (74, [(40, 0.150), (135, 0.148)])]
LOBE_SINK = -0.06                            # lobe centre offset along the normal from the core surface
FRONT = (0.150, -0.24)                      # leg (x, y)
HIND = (0.150, 0.30)
# head frame
HEAD_TILT = math.radians(58)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))      # poll -> nose
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))      # forehead side
XV = Vector((1, 0, 0))
P0 = Vector((0, -0.43, 0.855))                                   # back of the skull, centre
HEAD_LEN = 0.30
EYE_R = 0.020                                   # eye apothem before the head scale -> disc ~0.13 x head width
EAR_S, EAR_V = 0.075, 0.062                      # ear root under the wool cap, side of the head
EAR_DIR = (1.0, -0.38, -0.29)                    # sideways, ~20 deg forward, ~15 deg down
BODY_DROP = 0.02                                 # everything above the legs lowered -> legs ~10% shorter
# (s along U, half width, half height forehead side, half height throat side)
HEAD_RINGS = [(0.00, 0.090, 0.090, 0.085), (0.05, 0.142, 0.122, 0.105), (0.13, 0.155, 0.120, 0.105),
              (0.20, 0.126, 0.100, 0.092), (0.26, 0.096, 0.080, 0.076), (0.30, 0.068, 0.058, 0.060)]
# head tuft lobes: (s, v, x, radius) in the head frame (left + centre; x>0 mirrored)
TUFT = [(0.030, 0.108, 0.0, 0.076), (0.088, 0.092, 0.0, 0.066), (0.072, 0.078, 0.080, 0.066),
        (0.012, 0.064, 0.120, 0.073), (-0.038, 0.076, 0.066, 0.071)]
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'Wool_Head')
HEAD_SCALE = 1.12
HEAD_Q = Vector((0, -0.37, 0.77))                 # head group scaled about the head/neck joint
HEAD_MOVE = Vector((0, -0.04, 0.0))
# neck wool: (centre, normal, radius); left + centre, mirrored -> Wool_Neck
NECK_LOBES = [((0, -0.315, 0.770), (0, 0.35, 1.0), 0.125), ((0.150, -0.36, 0.680), (1.0, -0.25, 0.35), 0.140)]

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2', 'Wool_Neck', 'Wool_Head']
WOOL_BONE = {'Wool_Pelvis': 'Pelvis', 'Wool_Spine1': 'Spine1', 'Wool_Spine2': 'Spine2', 'Wool_Neck': 'Neck1',
             'Wool_Head': 'Head'}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-04', 'build'])[:2]


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
        self.P = pc.Part('Sheep'); self.pivot = {}
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
        spec = [(-0.62, 0.55, 0.0), (-0.05, 1.0, 0.5), (0.52, 0.64, 0.0)]     # (h, radius, phase in steps)
        R = []
        for h, rr, ph in spec:
            R.append([bm.verts.new(c + t * (h * r * hs) + e1 * (rr * r * math.cos(phase + (k + ph) * step)) +
                                   e2 * (rr * r * math.sin(phase + (k + ph) * step))) for k in range(nside)])
        return self._puff_faces(name, R, tone, shade)

    def puff_rings(self, name, rings, tone, shade=W2):
        R = [[self.P.bm.verts.new(p) for p in r] for r in rings]
        return self._puff_faces(name, R, tone, shade)

    def _puff_faces(self, name, R, tone, shade):
        P = self.P; n = len(R[0]); faces = []
        b, a, u = R
        faces.append(P.face(list(reversed(b)), shade))
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([b[k], b[k1], a[k]], shade))
            faces.append(P.face([a[k], b[k1], a[k1]], shade))
            faces.append(P.face([u[k], a[k], u[k1]], tone))
            faces.append(P.face([a[k], a[k1], u[k1]], tone))
        faces.append(P.face(list(u), tone))
        self._reg(name, faces)
        return R


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
    if c.y < -0.28 and c.z > 0.60: return 'Wool_Neck'
    if c.y < -0.17: return 'Wool_Spine2'
    if c.y < 0.05: return 'Wool_Spine1'
    return 'Wool_Pelvis'


def build_wool(M):
    """body lobes in staggered rows, X-mirrored; tone checker so neighbours differ"""
    count = 0; groups = {}
    for ri, (theta, lobes) in enumerate(LOBE_ROWS):
        for ci, (phi, r) in enumerate(lobes):
            i = ri * 10 + ci
            p, n = ell_point(theta, phi)
            # small deterministic tilt + size jitter (the same on both sides)
            tilt = Vector(((rnd(i, 1) - 0.5) * 0.10, (rnd(i, 2) - 0.5) * 0.10, (rnd(i, 3) - 0.5) * 0.10))
            centre_line = phi in (0, 180)
            if centre_line: tilt.x = 0.0
            nn = (n + tilt).normalized()
            rr = r * (0.97 + 0.06 * rnd(i, 4))
            c = p + n * LOBE_SINK * rr
            tone = W0 if (ri + ci) % 2 == 0 else W1
            nside = 5 if phi >= 120 else 6
            phase = (math.pi / 2 if nside == 5 else 0.0) if centre_line else rnd(i, 5) * 2 * math.pi
            g = wool_group(c)
            if centre_line:
                M.puff(g, c, nn, rr, nside, phase, tone); count += 1
            else:
                R = M.puff(g, c, nn, rr, nside, phase, tone); count += 1
                M.puff_rings(g, [[mir(v.co) for v in ring] for ring in R], tone); count += 1
            groups[g] = groups.get(g, 0) + (1 if centre_line else 2)
    for i, (c, n, r) in enumerate(NECK_LOBES):
        c = Vector(c); n = Vector(n).normalized(); tone = W1 if i % 2 == 0 else W0
        if c.x == 0:
            M.puff('Wool_Neck', c, n, r, 6, 0.0, tone); count += 1
        else:
            R = M.puff('Wool_Neck', c, n, r, 6, rnd(200 + i) * 6.28, tone); count += 1
            M.puff_rings('Wool_Neck', [[mir(v.co) for v in ring] for ring in R], tone); count += 1
        groups['Wool_Neck'] = groups.get('Wool_Neck', 0) + (1 if c.x == 0 else 2)
    return count, groups


def build_core(M):
    """hidden body core (Pelvis / Spine1 / Spine2), 8 sides, children tucked into the parent behind them"""
    def sec(y, f=1.0):
        s = max(0.0, 1 - ((y - CORE_C.y) / CORE_R[1]) ** 2) ** (END_E / 2) * f
        return ring_xyz(Vector((0, y, CORE_C.z)), CORE_R[0] * s, CORE_R[2] * s, CORE_R[2] * s, 6, XV, Vector((0, 0, 1)),
                        2.3, 2.3)
    ya = CORE_C.y - CORE_R[1]; yb = CORE_C.y + CORE_R[1]
    sp2 = [sec(ya + 0.03, 0.98), sec(-0.28), sec(-0.17)]
    sp1 = [sec(-0.17), sec(0.05)]
    pel = [sec(0.05), sec(0.26), sec(0.36), sec(yb - 0.025, 0.98)]
    pre = tuck(sp2[-1], (0, 1, 0)); M.loft('Spine2', sp2[:-1] + [pre[1], pre[0]], W3, W3, W3)
    pre = tuck(sp1[-1], (0, 1, 0)); M.loft('Spine1', sp1[:-1] + [pre[1], pre[0]], W3, W3, W3)
    M.loft('Pelvis', pel, W3, W3, W3)
    M.pivot['Pelvis'] = Vector((0, 0.26, 0.57))
    M.pivot['Spine1'] = Vector((0, 0.05, 0.57))
    M.pivot['Spine2'] = Vector((0, -0.17, 0.575))


def build_neck(M):
    cs = [Vector((0, -0.24, 0.59)), Vector((0, -0.31, 0.66)), Vector((0, -0.375, 0.735)), Vector((0, -0.41, 0.79)),
          Vector((0, -0.435, 0.84))]
    rs = [0.115, 0.110, 0.102, 0.095, 0.085]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))
        rings.append(ring_xyz(c, rs[i], rs[i] * 0.95, rs[i] * 0.95, 6, XV, e1))
    M.loft('Neck1', rings[0:3], W3, W3, W3)
    pre = tuck(rings[2], (cs[1] - cs[2]).normalized(), 0.86, 0.025)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], W3, W3, W3)
    M.pivot['Neck1'] = Vector((0, -0.28, 0.625)); M.pivot['Neck2'] = cs[2].copy()


def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, 8, XV, VV, 2.6, 2.3) for s, w, ht, hb in HEAD_RINGS]

    def col(j, k):
        L = min(k, 7 - k)              # side 0 (forehead centre) .. 3 (throat sides); k=3,4 straddle the throat
        if L >= 3: return FACE_D
        return FACE
    M.loft('Head', rings, col, FACE, FACE_D)
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
    # eyes: dark 8-gon discs, 5 mm proud, on the front face near its outer edge
    tgt = P0 + U * 0.15 + VV * 0.09 + XV * 0.085
    hp, n = surf(bvh, tgt, -(VV * 0.85 + XV * 0.55))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(c - a * 0.008, e1, e2, EYE_R, 8), ngon_ring(c + a * 0.003, e1, e2, EYE_R, 8)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: dark flattened hexagon pad on the muzzle end (forehead side of the cap)
    cap_c = P0 + U * HEAD_LEN + VV * 0.012
    _, e1, e2 = XV, XV, VV
    nr = lambda off: ngon_ring(cap_c + U * off, XV, VV, 0.034, 6, 0.0, 0.62)
    M.loft('Nose', [nr(-0.008), nr(0.004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = cap_c.copy()
    # jaw: chin block on the throat side of the muzzle
    jr = [(0.15, 0.052, 0.026), (0.23, 0.068, 0.032), (0.295, 0.046, 0.024)]
    rings = []
    for s, w, h in jr:
        hb = HEAD_RINGS[[x[0] for x in HEAD_RINGS].index(min(HEAD_RINGS, key=lambda q: abs(q[0] - s))[0])][3]
        c = P0 + U * s - VV * (hb - 0.004)
        rings.append(ring_xyz(c, w, h, h, 6, XV, VV, 2.2, 2.2))
    M.loft('Jaw', rings, FACE_D, FACE_D, FACE_D)
    M.pivot['Jaw'] = P0 + U * 0.15 - VV * 0.08
    # ears: thick leaves sticking out sideways, slightly forward and drooping; lighter inner (front) face
    hp, n = surf(bvh, P0 + U * EAR_S + VV * EAR_V + XV * 0.13, -XV)
    d = Vector(EAR_DIR).normalized()
    _, ea, eb = pc.basis(d, (0, 0, 1))                # ea = leaf width (about vertical), eb = thickness
    prof = [(1, 0), (0.5, 1), (-0.5, 1), (-1, 0), (-0.5, -1), (0.5, -1)]
    L = 0.45 * HEAD_LEN + 0.04                         # visible ear beyond the cap = 0.45 x head length (+0.04 under the cap)
    spec = [(-0.035, 0.024, 0.012), (0.35 * L, 0.046, 0.014), (0.70 * L, 0.044, 0.013), (L, 0.011, 0.006)]
    rings = [[hp + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = FACE
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, FACE, FACE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # head tuft: wool lobes on the poll (Wool_Head)
    nt = 0
    for i, (s, v, x, r) in enumerate(TUFT):
        c = P0 + U * s + VV * v + XV * x
        nn = (VV * max(v, 0.03) + XV * x * 1.2 - U * 0.03).normalized()
        tone = W0 if i % 2 == 0 else W1
        if s < 0: nn = (nn - U * 0.6).normalized()
        if x == 0:
            M.puff('Wool_Head', c, nn, r, 5, math.pi / 2, tone); nt += 1
        else:
            R = M.puff('Wool_Head', c, nn, r, 5, rnd(100 + i) * 6.28, tone); nt += 1
            M.puff_rings('Wool_Head', [[mir(q.co) for q in ring] for ring in R], tone); nt += 1
    return nt


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r: ngon_ring(Vector((x, y, z)), X, Y, r, 6, 0.0)
            rb, ztop, zk = (0.047, 0.45, 0.165) if kind == 'Front' else (0.049, 0.47, 0.185)
            lr = lambda z: rb * (1 + 0.15 * (z - 0.08) / (0.24 - 0.08))    # top radius 1.15 x bottom over the visible leg
            M.loft(kind + 'Upper' + sfx, [ring(ztop, lr(ztop)), ring(zk, lr(zk))], LEG, LEG, LEG)
            M.loft(kind + 'Lower' + sfx, [ring(zk + 0.025, lr(zk + 0.025) - 0.004), ring(zk - 0.0005, lr(zk) - 0.0005),
                                          ring(0.06, lr(0.06) - 0.0005)], LEG, LEG, LEG)
            M.loft(kind + 'Foot' + sfx, [ring(z, r) for z, r in [(0.0, 0.060), (0.066, 0.057), (0.080, 0.050)]],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, ztop - 0.06))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, zk))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.07))


def build_tail(M):
    a = Vector((0, 0.36, 0.66)); b = Vector((0, 0.50, 0.695))
    t = (b - a).normalized(); _, e1, e2 = pc.basis(t, (1, 0, 0))
    M.loft('Tail1', [ngon_ring(a, e1, e2, 0.05, 6, 0.0), ngon_ring(b, e1, e2, 0.043, 6, 0.0)], W2, W2, W2)
    M.pivot['Tail1'] = a.copy()
    c = Vector((0, 0.545, 0.715)); n = Vector((0, 1.0, 0.45)).normalized()
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
    for g, b in WOOL_BONE.items():
        if g != 'Wool_Head': M.pivot[g] = M.pivot[b].copy()
    for k in HEAD_GROUP:
        if k != 'Wool_Head': M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE + HEAD_MOVE
    M.pivot['Wool_Head'] = M.pivot['Head'].copy()
    legs = {k + s_ + sd for k in ('Front', 'Hind') for s_ in ('Upper', 'Lower', 'Foot') for sd in ('.L', '.R')}
    dv = {v for nm, faces, _ in M.P.comp if nm not in legs for f in faces for v in f.verts}
    for v in dv: v.co.z -= BODY_DROP
    for k in M.pivot:
        if k not in legs: M.pivot[k] = M.pivot[k] - Vector((0, 0, BODY_DROP))
    bm = M.P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for nm, faces, _ in M.P.comp:            # one wool colour + 2 shades by facet direction
        if nm.startswith('Wool_') or nm in ('Tail1', 'Tail2'):
            for f in faces:
                nz = f.normal.z
                f[M.P.slot] = W1 if nz > 0.55 else (W2 if nz < -0.30 else W0)
        elif nm in ('Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2'):
            for f in faces: f[M.P.slot] = W3
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
    print(f'TRIS total {tot} | target ~1800, previous 2074 (+10% = 2280) | lobes body {M.n_lobes} {M.wool_groups} + tuft {M.n_tuft}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    wool = [o.matrix_world @ v.co for k in ('Wool_Pelvis', 'Wool_Spine1', 'Wool_Spine2', 'Wool_Neck') for o in (obs[k],)
            for v in o.data.vertices]
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | wool body top {max(p.z for p in wool):.3f} bottom {min(p.z for p in wool):.3f} '
          f'width {max(p.x for p in wool) - min(p.x for p in wool):.3f}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Sheep_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Sheep_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def compose_looks():
    tiles = [rn.ref_tile(REF, 400)]
    for nm in ('ref', 'prev', 'side', 'back', 'front', 'top'):
        p = os.path.join(CHECK, f'Sheep_look_{nm}.png'); tiles.append(rn.resize(rn.load_px(p), 400)); os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Sheep_look_sheet.png'))
    t = rn.resize(rn.load_px(os.path.join(CHECK, 'Sheep_look_sheet.png')), 128)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-04 Sheep', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Sheep_look_ref.png'), view=REF_VIEW, fill=(0.62, 0.78))
        for nm, v in (('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)), ('front', (0.0, -1.0, 0.12)), ('prev', PREVIEW_VIEW),
                      ('top', (0.25, -0.35, 1.0))):
            rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, f'Sheep_look_{nm}.png'), view=v, fill=(0.62, 0.78))
        compose_looks()
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
