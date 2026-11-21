# build_kid.py - LIV-13 Kid (baby goat, Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_kid.py -- LIV-13 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_kid)
# look  : build + EEVEE frames (reference angle, preview, side, back, front, top) -> one sheet in the check folder
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the other animals).
# Structure copied from ../Goat/build_goat.py (Model/loft/tuck/objects/coplanar_all/check sheet). Shared modules are
# only imported (read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Kid'
TAG = 'FarmAnimals_Kid'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-13.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_kid')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.75, -0.85, 0.30)       # LIV-13 reference: front-left three-quarter, ~15 deg above
PREVIEW_VIEW = (0.72, -0.80, 0.20)   # front-left three-quarter (~42 deg), both ears and the torso visible
BUDGET = 1200

PALETTE = ['#F2E8DE', '#E6D9CC', '#D6C7B8', '#F8F1E9',     # 0 warm white coat, 1 shade, 2 underside, 3 bright face
           '#857169', '#6B5850', '#E5A49C', '#D9958E',     # 4 horn, 5 horn tip, 6 nose, 7 ear inner
           '#2A1D17', '#3A2E28', '#EADFD3', '#F2E8DE',     # 8 eye, 9 hoof, 10 spare, 11 spare
           '#B5835A', '#6E9F4A', '#8E959B', '#C8473B']     # 12-15 series spares
WHITE, SHADE, UNDER, FACE, HORN, HORN_D, NOSE, EAR_IN, EYE, HOOF = range(10)

# ---------------- layout (before the centre-of-mass shift) ----------------
NB = 10                                  # body sides (few, large facets)
# body profile: y, half width, z bottom, z top
# chest: gradual, low-shouldered rounded front (one convex volume from under the chin into the barrel)
BODY_PROF = [(-0.252, 0.050, 0.330, 0.410), (-0.238, 0.110, 0.262, 0.452), (-0.205, 0.148, 0.226, 0.482),
             (-0.158, 0.170, 0.209, 0.498), (-0.110, 0.178, 0.205, 0.506), (0.000, 0.180, 0.205, 0.510),
             (0.110, 0.174, 0.215, 0.512), (0.198, 0.142, 0.245, 0.507), (0.230, 0.080, 0.305, 0.465)]
BODY_RINGS = [-0.252, -0.238, -0.205, -0.158, -0.110, 0.000, 0.110, 0.198, 0.230]
SPLIT = {'Spine2': (0, 4), 'Spine1': (4, 6), 'Pelvis': (6, 8)}
NECK_AXIS = [(-0.120, 0.400), (-0.140, 0.450), (-0.155, 0.500), (-0.165, 0.545), (-0.172, 0.585)]
NECK_R = [(0.098, 0.098), (0.094, 0.096), (0.088, 0.090), (0.078, 0.080), (0.066, 0.066)]
# head frame: U = poll -> chin (straight down: vertical face, so the eye discs are not skewed), VV = face side (forward)
HEAD_TILT = math.radians(90)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
P0 = Vector((0, -0.220, 0.660))
# rounded-cube head: (s down, half width, half depth face side, half depth back side, face-side offset, face ridge)
# rings 1-2 have an identical front -> two planar vertical eye facets angled 18 deg outward; rings 3-4 share the face plane
# -> flat vertical muzzle front for the inset nose
HEAD_RINGS = [(-0.048, 0.040, 0.032, 0.036, -0.004, 0.006),      # small crown cap
              (-0.034, 0.092, 0.074, 0.080, -0.004, 0.014),      # 3 bevel rings: rounded faceted crown, no flat top
              (-0.008, 0.132, 0.108, 0.110, -0.002, 0.026), (0.030, 0.150, 0.122, 0.120, 0.000, 0.034),
              (0.140, 0.150, 0.122, 0.118, 0.000, 0.034), (0.190, 0.118, 0.110, 0.090, 0.045, 0.000),
              (0.262, 0.085, 0.100, 0.065, 0.055, 0.000), (0.290, 0.055, 0.075, 0.040, 0.055, 0.000)]
FRONT_FACET = 0.70                       # half width of the face facets / half width
HEAD_SCALE = 1.14                        # head group scale about the neck joint (head width 0.34 m)
HEAD_Q = Vector((0, -0.20, 0.52))
DZ = -0.045                              # body, neck, head and tail lowered: short stubby legs
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'Horn.L', 'Horn.R')
# horn nubs: offsets from the base point on the head top (x outward, y back, z up); apothems per ring
HORN_PATH = [(0.0, 0.0, -0.036), (0.016, 0.008, 0.035), (0.036, 0.020, 0.068)]
HORN_R = [0.034, 0.027, 0.012]
FRONT = (0.090, -0.120)
HIND = (0.090, 0.128)
TAIL_PTS = [(0.195, 0.450), (0.225, 0.505), (0.242, 0.565), (0.252, 0.625)]
TAIL_R = [(0.030, 0.055), (0.032, 0.060), (0.024, 0.044), (0.005, 0.008)]

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Horn.L', 'Horn.R',
              'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']
COAT = {'Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Tail1', 'Tail2', 'Tail3'}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-13', 'build'])[:2]


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


def body_ring(yk, n=NB, pt=2.4, pb=2.6):
    w, zb, zt = lerp_tab(BODY_PROF, yk)
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(Vector((w * spow(c, 2 / p), yk, zc + h * spow(s, 2 / p))))
    return out


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4, ph=0.0):
    out = []
    for k in range(n):
        th = math.pi / 2 + ph + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def head_ring(cen, w, ht, hb, dr):
    fw = FRONT_FACET * w
    pts = [(fw, ht), (0.0, ht + dr), (-fw, ht), (-w, 0.40 * ht), (-w, -0.40 * hb), (-fw, -hb), (fw, -hb), (w, -0.40 * hb),
           (w, 0.40 * ht)]
    return [cen + X * x + VV * v for x, v in pts]


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.86, depth=0.03, gap=0.001):
    """child's proximal end: boundary ring moved gap forward + a smaller ring hidden inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    inner = [c + (p - c) * scale + ab * depth for p in ring]
    edge = [p - ab * gap for p in ring]
    return [inner, edge]


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Kid'); self.pivot = {}
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


# ---------------- body ----------------
def build_body(M):
    rings = [body_ring(y) for y in BODY_RINGS]
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft(part, rs, WHITE, WHITE, WHITE)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0))
            M.loft(part, rs[:-1] + [pre[1], pre[0]], WHITE, WHITE, WHITE)
    M.pivot['Pelvis'] = Vector((0, 0.17, 0.39))
    M.pivot['Spine1'] = Vector((0, BODY_RINGS[6], 0.37))
    M.pivot['Spine2'] = Vector((0, BODY_RINGS[4], 0.37))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    M.loft('Neck1', rings[0:3], WHITE, WHITE, WHITE)
    t = (cs[2] - cs[3]).normalized()
    pre = tuck(rings[2], t, 0.86, 0.02)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], WHITE, WHITE, WHITE)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- head ----------------
def build_head(M):
    rings = [head_ring(P0 + U * s + VV * o, w, ht, hb, dr) for s, w, ht, hb, o, dr in HEAD_RINGS]
    faces = M.loft('Head', rings, WHITE, WHITE, WHITE)
    M.pivot['Head'] = P0 + U * 0.02
    return faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d, back=0.5):
    d = Vector(d).normalized(); o = Vector(target) - d * back
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {tuple(target)}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n.normalized()


def build_face(M, head_faces):
    hb = bvh_of(head_faces)
    # eyes: dark hexagon discs (pointy top, as the reference) lying flush on the planar vertical eye facets (axis = facet
    # normal, 18 deg outward), 3 mm proud, set wide apart
    hp, n = surf(hb, P0 + U * 0.085 + VV * 0.20 + X * 0.072, -VV)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(c - a * 0.010, e1, e2, 0.026, 6, 0.0), ngon_ring(c + a * 0.003, e1, e2, 0.026, 6, 0.0)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: small pink inverted triangle inset flush in the flat muzzle front (1.5 mm proud) + philtrum line (0.8 mm proud)
    hp, n = surf(hb, P0 + U * 0.207 + VV * 0.25, -VV)
    up = (Z - n * Z.dot(n)).normalized(); side = up.cross(n).normalized()
    if side.x < 0: side = -side
    tri = lambda off, r: ngon_ring(hp + n * off, side, up, r, 3, -math.pi / 2, 0.6)
    M.loft('Nose', [tri(-0.006, 0.019), tri(0.0015, 0.019)], NOSE, NOSE, NOSE)
    st = hp - up * 0.034
    box = lambda off: [st + n * off + side * sx_ * 0.004 + up * sy_ * 0.013 for sx_, sy_ in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    M.loft('Nose', [box(-0.005), box(0.0008)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # jaw: chin block under the muzzle
    jr = [(0.200, 0.045, 0.026), (0.255, 0.044, 0.026), (0.298, 0.024, 0.015)]
    rings = [ring_xyz(P0 + U * s + VV * 0.035, w, h, h, 8, X, VV, 2.2, 2.2) for s, w, h in jr]
    M.loft('Jaw', rings, WHITE, WHITE, WHITE)
    M.pivot['Jaw'] = P0 + U * 0.17
    # ears: big flat pointed leaves straight out sideways (horizontal), cupped pink inner face facing forward-up
    hp, n = surf(hb, P0 + U * 0.085 + VV * 0.045 + X * 0.16, -X)      # head side at eye level
    d = Vector((1.0, -0.12, 0.0)).normalized()
    _, ea, eb = pc.basis(d, (0, 0.6, 0.8))             # ea = leaf width (up-back), eb = thickness (forward-up)
    if eb.y > 0: eb = -eb                              # +eb = front (inner) face
    prof = [(1, 0.5), (0.55, 0.05), (-0.55, 0.05), (-1, 0.5), (-0.6, -0.8), (0.6, -0.8)]
    base = hp - d * 0.035
    spec = [(0.0, 0.038, 0.016), (0.05, 0.066, 0.022), (0.120, 0.060, 0.022), (0.180, 0.032, 0.015), (0.215, 0.006, 0.006)]
    rings = [[base + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = lambda j, k: (EAR_IN if k == 1 else WHITE) if (k in (0, 1, 2) and j >= 1) else (WHITE if k in (0, 1, 2) else SHADE)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, SHADE, WHITE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # horn buds: short tapered 6-sided tubes from the poll corners, up -> back -> out
    hp, n = surf(hb, P0 - U * 0.010 + VV * 0.005 + X * 0.064, U)
    pts = [hp + Vector(o) for o in HORN_PATH]
    rings = []
    for i, (c, r) in enumerate(zip(pts, HORN_R)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        rings.append(ngon_ring(c, e1, e2, r, 6, 0.0))
    hc = lambda j, k: HORN if j < 1 else HORN_D
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Horn' + sfx, rr, hc, HORN, HORN_D)
        M.pivot['Horn' + sfx] = hp.copy() if sx > 0 else mir(hp)


# ---------------- legs ----------------
def build_legs(M):
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda yy, z, r, sy=1.0: ngon_ring(Vector((x, yy, z)), X, Y, r, 6, 0.0, sy)
            # one continuous tapered prism (top radius ~1.13x the bottom) split at the knee; no band, no step
            if kind == 'Front':
                up = [(y, 0.330, 0.062), (y, 0.160, 0.0518), (y, 0.090, 0.0485)]
                z_up = 0.30
            else:
                up = [(y, 0.330, 0.060), (y, 0.160, 0.0518), (y, 0.090, 0.0485)]
                z_up = 0.32
            lo = [(y, 0.110, 0.0482), (y, 0.040, 0.0458)]
            z_lo = 0.10
            M.loft(kind + 'Upper' + sfx, [ring(*r) for r in up], WHITE, WHITE, WHITE)
            M.loft(kind + 'Lower' + sfx, [ring(*r) for r in lo], WHITE, WHITE, WHITE)
            M.loft(kind + 'Foot' + sfx, [ring(y, z, r) for z, r in [(0.0, 0.055), (0.058, 0.0535)]],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, lo[0][0], z_lo))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.055))


# ---------------- tail: short upright leaf, Tail1-3 ----------------
def build_tail(M):
    pts = [Vector((0, y, z)) for y, z in TAIL_PTS]

    def ring(i):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        rx, ry = TAIL_R[i]
        return [pts[i] + e1 * (rx * math.cos(a)) + e2 * (ry * math.sin(a)) for a in [2 * math.pi * k / 6 for k in range(6)]]
    R = [ring(i) for i in range(len(pts))]
    M.loft('Tail1', [R[0], R[1]], WHITE, WHITE, WHITE)
    pre = tuck(R[1], -(pts[2] - pts[1]), 0.86, 0.015)
    M.loft('Tail2', [pre[0], pre[1], R[2]], WHITE, WHITE, WHITE)
    pre = tuck(R[2], -(pts[3] - pts[2]), 0.86, 0.015)
    M.loft('Tail3', [pre[0], pre[1], R[3]], WHITE, WHITE, WHITE)
    M.pivot['Tail1'] = pts[0].lerp(pts[1], 0.5); M.pivot['Tail2'] = pts[1].copy(); M.pivot['Tail3'] = pts[2].copy()


# ---------------- coat shading: palette cell by face normal (white top, shade low sides, underside) ----------------
def shade_coat(M):
    P = M.P
    for nm, faces, _ in P.comp:
        if nm not in COAT: continue
        hd = nm in ('Head', 'Jaw')
        for f in faces:
            nz = f.normal.z
            if hd and f.normal.y < -0.80: f[P.slot] = FACE        # flat face facet and muzzle front: brightest
            elif nz < (-0.80 if hd else -0.60): f[P.slot] = UNDER
            elif nz < (-0.50 if hd else -0.20): f[P.slot] = SHADE
            else: f[P.slot] = WHITE


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
    build_body(M); build_neck(M)
    hf = build_head(M); build_face(M, hf)
    build_tail(M)
    bm = M.P.bm
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
    for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
    for v in bm.verts: v.co.z += DZ                    # everything above the legs sits lower (short legs)
    for k in M.pivot: M.pivot[k] = M.pivot[k] + Vector((0, 0, DZ))
    build_legs(M)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    shade_coat(M)
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
    W = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in W(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for nm_ in ('Head', 'Nose', 'Jaw') for p in W(obs[nm_]))
    tail = max(p.y for nm_ in ('Tail1', 'Tail2', 'Tail3', 'Pelvis') for p in W(obs[nm_]))
    back = max(p.z for nm_ in ('Spine1', 'Spine2', 'Pelvis') for p in W(obs[nm_]))
    belly = min(p.z for p in W(obs['Spine1']))
    hpts = W(obs['Head']) + W(obs['Jaw'])
    poll = max(p.z for p in W(obs['Head'])); chin = min(p.z for p in hpts)
    hw = max(p.x for p in hpts) - min(p.x for p in hpts)
    horn = max(p.z for p in W(obs['Horn.L']))
    ear = max(p.x for p in W(obs['Ear.L'])) - min(p.x for p in W(obs['Ear.R']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->tail {tail - nose:.3f} back {back:.3f} belly {belly:.3f} poll {poll:.3f} chin {chin:.3f} '
          f'head width {hw:.3f} head height {poll - chin:.3f} horn tip {horn:.3f} ear span {ear:.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


# ---------------- preview: copy of _common/animal_render.preview (read-only) with the key sun mirrored to the camera
# side (front-left), so the near cheek of the white head is lit instead of falling into the sun shadow ----------------
def preview_kid(sc, objs, out, view=(1.0, -0.62, 0.34), fill=(0.70, 0.80), lens=50):
    """EEVEE 1280x800, three-quarter front-left; camera-visible sky gradient + meadow ground disc, sun + fill."""
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('TMP_PreviewWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (rn._lin('e3'), rn._lin('ec'), rn._lin('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (rn._lin('86'), rn._lin('b4'), rn._lin('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1)
    amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface'])
    old_world = sc.world; sc.world = w
    # meadow ground: big disc, soft green, fades into the horizon haze
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = 60.0
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(rn._solid_mat('TMP_Meadow_M', '#93AE6E'))
    gob = bpy.data.objects.new('TMP_Meadow', me); sc.collection.objects.link(gob)
    lights = []
    for nm, rot, e, sh in (('TMP_Sun', (48, 0, 35), 3.6, True), ('TMP_Fill', (70, 0, -160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(8); ld.use_shadow = sh
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob); lights.append(ob)
    cam = rn.camera(sc, 'TMP_PrevCam', lens)
    pts = rn.mesh_points(objs)
    rn.fit(sc, cam, pts, view, fill)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights + [gob, cam]:
        d = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
        if isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
        elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    sc.world = old_world; bpy.data.worlds.remove(w)
    print('preview', out)


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.8, 0.9, 0.45), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Kid_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B):
    views = [('ref', REF_VIEW), ('prev', PREVIEW_VIEW), ('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)),
             ('front', (0.0, -1.0, 0.12)), ('top', (0.3, -0.25, 1.0))]
    tiles = [rn.ref_tile(REF, 400)]
    for nm, v in views:
        p = os.path.join(CHECK, f'Kid_look_{nm}.png')
        preview_kid(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.62, 0.78))
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Kid_look_sheet.png'))
    sm = rn.resize(rn.load_px(os.path.join(CHECK, 'Kid_look_ref.png')), 128)
    rn.compose([sm], 1, os.path.join(CHECK, 'Kid_look_128.png'), pad=0)
    os.remove(os.path.join(CHECK, 'Kid_look_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-13 Kid', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview_kid(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
