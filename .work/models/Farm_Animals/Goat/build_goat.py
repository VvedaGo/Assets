# build_goat.py - LIV-08 Goat (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_goat.py -- LIV-08 build|look|export
# build : parts + palette + patches + checks + check sheet (%TEMP%/FarmAnimals_check_goat)
# look  : build + EEVEE frames (reference angle, preview, side, back, front, top) -> one sheet in the check folder
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Cow/Calf/Sheep).
# Structure copied from ../Calf/build_calf.py (Model/loft/tuck/patch field + contour snap/objects), ears from ../Sheep,
# horns from ../Cow (sunk tapered tube, darker tip), leg bend from ../Horse. Shared modules are only imported.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Goat'
TAG = 'FarmAnimals_Goat'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-08.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_goat')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.80, -1.0, 0.26)        # LIV-08 reference: chest towards the camera, left flank receding, ~14 deg above
PREVIEW_VIEW = (0.68, -1.0, 0.20)    # pack preview template (front-left three-quarter, low camera, sky behind the head)
BUDGET = 1700

PALETTE = ['#F3EBDF', '#E3D6C5', '#D6B593', '#D5C4AC',     # 0 white coat, 1 cream shade, 2 tan patch, 3 throat (behind the beard)
           '#FAF5EC', '#C9A685', '#86664B', '#D9A592',     # 4 face blaze / beard, 5 horn, 6 horn tip, 7 nose
           '#2A1D17', '#3A2E28', '#B48D6C', '#D6C8B3',     # 8 eye, 9 hoof, 10 ear inner, 11 joint band
           '#EFE3CD', '#6E9F4A', '#8E959B', '#C8473B']     # 12 beard cream, 13-15 series spares
WHITE, CREAM, TAN, THROAT, FACE, HORN, HORN_D, NOSE, EYE, HOOF, EAR_IN, BAND, BEARD = range(13)

# ---------------- layout (before the centre-of-mass shift) ----------------
SLANT = 0.10
NB = 14                                  # body sides
# body profile: y, half width, z bottom, z top
BODY_W = 1.30                            # body half-width factor (reference barrel is chunky)
BODY_PROF = [(y, w * BODY_W, zb, zt) for y, w, zb, zt in
             [(-0.40, 0.100, 0.490, 0.700), (-0.37, 0.150, 0.400, 0.765), (-0.30, 0.182, 0.335, 0.790),
              (-0.18, 0.196, 0.305, 0.800), (0.00, 0.200, 0.300, 0.800), (0.15, 0.198, 0.308, 0.800),
              (0.27, 0.190, 0.335, 0.805), (0.35, 0.172, 0.380, 0.805), (0.405, 0.135, 0.460, 0.790),
              (0.44, 0.075, 0.550, 0.750)]]
BODY_RINGS = [(-0.40, 0), (-0.37, 0), (-0.30, 0.3), (-0.22, 0.7), (-0.13, 1), (-0.04, 1), (0.05, 1), (0.14, 1), (0.23, 1),
              (0.31, 0.7), (0.37, 0.5), (0.41, 0.25), (0.44, 0)]
SPLIT = {'Spine2': (0, 4), 'Spine1': (4, 8), 'Pelvis': (8, 12)}
FROZEN_LONG = {0, 4, 8, 12}
# tan blobs on the white coat (|x| -> mirror-symmetric): centre, radii, slant dy/dz, wobble amplitude, phase
BLOBS = [((0.0, 0.04, 0.86), (0.30, 0.37, 0.235), 0.0, 0.07, 0.0),        # saddle over the back
         ((0.22, -0.21, 0.62), (0.15, 0.115, 0.22), 0.35, 0.08, 1.3),     # shoulder drape (withers -> elbow)
         ((0.19, 0.31, 0.68), (0.15, 0.12, 0.17), -0.30, 0.07, 2.4)]     # hip drape over the thigh
NECK_AXIS = [(-0.30, 0.60), (-0.35, 0.70), (-0.395, 0.80), (-0.42, 0.88), (-0.435, 0.95)]
NECK_R = [(0.175, 0.180), (0.165, 0.160), (0.148, 0.140), (0.125, 0.118), (0.098, 0.094)]
# head frame: U along the head poll -> nose, VV forehead side
HEAD_TILT = math.radians(58)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
P0 = Vector((0, -0.475, 1.00))
HEAD_LEN = 0.27
# (s along U, half width, half height forehead side, half height throat side)
HEAD_RINGS = [(0.00, 0.082, 0.076, 0.072), (0.042, 0.134, 0.104, 0.090), (0.105, 0.146, 0.104, 0.094),
              (0.170, 0.120, 0.086, 0.082), (0.228, 0.094, 0.070, 0.068), (0.270, 0.072, 0.052, 0.054)]
NH = 10
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'Horn.L', 'Horn.R', 'Beard')
HEAD_SCALE = 1.26
HEAD_Q = Vector((0, -0.43, 0.93))          # head/neck joint the head group is scaled about
# horn path: offsets from the base point on the poll (x outward, y back, z up); apothems per ring
HORN_PATH = [(0.0, 0.0, -0.032), (0.0, 0.0, 0.0), (0.014, 0.004, 0.068), (0.036, 0.036, 0.128), (0.060, 0.090, 0.162),
             (0.080, 0.150, 0.160), (0.092, 0.196, 0.134)]
HORN_R = [0.046, 0.045, 0.039, 0.031, 0.023, 0.014, 0.004]
FRONT = (0.140, -0.25)
HIND = (0.140, 0.28)
TAIL_PTS = [(0.40, 0.725), (0.44, 0.785), (0.465, 0.855), (0.48, 0.925), (0.487, 0.995)]
TAIL_R = [(0.034, 0.050), (0.035, 0.058), (0.031, 0.054), (0.021, 0.037), (0.003, 0.004)]

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Horn.L', 'Horn.R',
              'Eye.L', 'Eye.R', 'Nose', 'Beard',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-08', 'build'])[:2]


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
        self.P = pc.Part('Goat'); self.pivot = {}
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


# ---------------- body: white coat, tan saddle + shoulder and hip drapes ----------------
def field(p):
    """< 0 inside a tan blob. Ellipsoid distance with a low-frequency wobble -> organic, rounded patch edges"""
    ax = abs(p.x); best = 9.0
    for (cx, cy, cz), (rx, ry, rz), sl, amp, ph in BLOBS:
        dy = p.y - (cy + sl * (p.z - cz))
        d = math.sqrt(((ax - cx) / rx) ** 2 + (dy / ry) ** 2 + ((p.z - cz) / rz) ** 2)
        wob = amp * math.sin(13.0 * p.y + 9.0 * p.z + 6.0 * ax + ph)
        best = min(best, d - 1.0 - wob)
    return best


def snap_rings(R):
    """move grid vertices onto the blob contour (each vertex at most once, at most half an edge) -> patch edges follow
    the contour instead of stair-stepping"""
    n = len(R[0]); F = [[field(p) for p in r] for r in R]; Zf = [[False] * n for _ in R]
    cand = []
    for j in range(len(R)):
        for k in range(n):
            nbs = [(j, (k + 1) % n), (j, (k - 1) % n)]
            if j not in FROZEN_LONG: nbs += [(jj, k) for jj in (j - 1, j + 1) if 0 <= jj < len(R)]
            for jj, kk in nbs:
                if F[j][k] * F[jj][kk] < 0:
                    t = F[j][k] / (F[j][k] - F[jj][kk])
                    if t <= 0.5: cand.append((round(t, 9), j, k, jj, kk))
    cand.sort()
    moved = 0
    for t, j, k, jj, kk in cand:
        if Zf[j][k] or Zf[jj][kk] or F[j][k] * F[jj][kk] >= 0: continue
        t = F[j][k] / (F[j][k] - F[jj][kk])
        if t > 0.5: continue
        R[j][k] = R[j][k].lerp(R[jj][kk], t); Zf[j][k] = True; F[j][k] = 0.0; moved += 1
    return F, Zf, moved


def loft_field(M, name, rings, Fs, Zs, cap0, cap1):
    """quads split along the contour diagonal; triangle colour from its off-contour vertices (tan < 0)"""
    P = M.P; bm = P.bm
    R = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(R[0]); faces = []
    sg = lambda j, k: 0 if Zs[j][k] else (1 if Fs[j][k] > 0 else -1)

    def colour(tri, idx):
        ss = {sg(*i) for i in idx} - {0}
        if len(ss) == 1: return WHITE if ss.pop() > 0 else TAN
        c = sum((v.co for v in tri), Vector()) / 3
        return WHITE if field(c) > 0 else TAN
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            ia, ib, ic, id_ = (j, k), (j, k1), (j + 1, k1), (j + 1, k)
            a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
            za, zb, zc, zd = Zs[j][k], Zs[j][k1], Zs[j + 1][k1], Zs[j + 1][k]
            if za and zc: bd = False
            elif zb and zd: bd = True
            else: bd = sg(*ia) * sg(*ic) < 0 and sg(*ib) * sg(*id_) >= 0
            tris = [((a, b, d), (ia, ib, id_)), ((b, c, d), (ib, ic, id_))] if bd else [((a, b, c), (ia, ib, ic)), ((a, c, d), (ia, ic, id_))]
            for tri, idx in tris:
                faces.append(P.face(list(tri), colour(tri, idx)))
    for cap, r in ((cap0, 0), (cap1, len(R) - 1)):
        if not cap: continue
        ring = list(reversed(R[0])) if r == 0 else list(R[-1])
        c = sum((v.co for v in ring), Vector()) / len(ring)
        faces.append(P.face(ring, WHITE if field(c) > 0 else TAN))
    for f in faces: f[M.pl] = PART_ORDER.index(name)
    P.comp.append((name, faces, False))


def build_body(M):
    rings = [body_ring(y, f) for y, f in BODY_RINGS]
    F, Zf, moved = snap_rings(rings)
    M.snapped = moved
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]; fs = F[i0:i1 + 1]; zs = Zf[i0:i1 + 1]
        if part == 'Pelvis':
            loft_field(M, part, rs, fs, zs, True, True)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0))
            ext = [pre[1], pre[0]]
            loft_field(M, part, rs[:-1] + ext, fs[:-1] + [[field(p) for p in r] for r in ext],
                       zs[:-1] + [[False] * NB for _ in ext], True, True)
    M.pivot['Pelvis'] = Vector((0, 0.33, 0.64))
    M.pivot['Spine1'] = Vector((0, BODY_RINGS[8][0], 0.62))
    M.pivot['Spine2'] = Vector((0, BODY_RINGS[4][0], 0.62))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    col = lambda j, k: THROAT if k in (3, 4) else (CREAM if k in (2, 5) else WHITE)   # throat cream (beard reads against it)
    M.loft('Neck1', rings[0:3], col, WHITE, WHITE)
    t = (cs[2] - cs[3]).normalized()
    pre = tuck(rings[2], t, 0.86, 0.02)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], col, WHITE, WHITE)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- head ----------------
def head_colour(j, k):
    d = min((k - 9) % NH, (9 - k) % NH)              # 0 = forehead centre face, 5 = throat face
    if j == 0: return CREAM if d >= 3 else WHITE      # back of the skull
    if d == 0: return FACE                            # bright blaze down the face
    if d == 1: return WHITE
    return CREAM                                      # cheeks / sides / throat (greyer, as the reference)


def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, NH, X, VV, 2.5, 2.3, math.pi / NH) for s, w, ht, hb in HEAD_RINGS]
    faces = M.loft('Head', rings, head_colour, CREAM, FACE)
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
    # eyes: dark 8-gon discs, 5 mm proud, on the sides of the head looking sideways-forward
    look = (X * 0.70 + U * 0.66 + VV * 0.15).normalized()
    hp, n = surf(hb, P0 + U * 0.125 + VV * 0.040 + X * 0.11, -look)
    ax = (n + look).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(c - a * 0.014, e1, e2, 0.030, 8), ngon_ring(c + a * 0.005, e1, e2, 0.030, 8)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: small pink inverted triangle lying on the flat muzzle front (1.5 mm proud = reads as painted; no plate),
    # top edge horizontal, fully inside the muzzle cap outline
    cap_c = P0 + U * HEAD_LEN
    tri3 = [Vector((-0.044, 0.026)), Vector((0.044, 0.026)), Vector((0.0, -0.034))]
    nr = lambda off: [cap_c + U * off + X * p.x + VV * (p.y + 0.008) for p in tri3]
    M.loft('Nose', [nr(-0.006), nr(0.0015)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = cap_c.copy()
    # jaw: chin block under the muzzle
    jr = [(0.140, 0.050, 0.024), (0.205, 0.062, 0.030), (0.262, 0.048, 0.022)]
    rings = []
    for s, w, h in jr:
        hbot = lerp_tab([(r[0], r[3]) for r in HEAD_RINGS], s)[0]
        rings.append(ring_xyz(P0 + U * s - VV * (hbot - 0.006), w, h, h, 8, X, VV, 2.2, 2.2))
    jaw_faces = M.loft('Jaw', rings, WHITE, WHITE, WHITE)
    M.pivot['Jaw'] = P0 + U * 0.16 - VV * 0.07
    # ears: long leaves sticking out sideways (slightly back and drooping); tan inner (front) face, cream back
    hp, n = surf(hb, P0 + U * 0.06 + VV * 0.035 + X * 0.14, -X)
    d = Vector((1.0, 0.08, -0.08)).normalized()
    _, ea, eb = pc.basis(d, (0, -0.45, 0.9))           # ea = leaf width (up-back), eb = thickness
    if eb.y > 0: eb = -eb                              # +eb = front (inner) face
    prof = [(1, 0), (0.5, 1), (-0.5, 1), (-1, 0), (-0.5, -1), (0.5, -1)]
    base = hp - d * 0.035
    spec = [(0.0, 0.032, 0.016), (0.075, 0.062, 0.021), (0.155, 0.056, 0.018), (0.230, 0.013, 0.006)]
    rings = [[base + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = lambda j, k: (EAR_IN if k == 1 else WHITE) if (k in (0, 1, 2) and j >= 1) else BAND
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, BAND, BAND)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # horns: tapered 6-sided tubes from the poll, up -> back -> outward, darker tip
    hp, n = surf(hb, P0 + U * 0.075 + X * 0.052, -VV)
    pts = [hp + Vector(o) for o in HORN_PATH]
    rings = []
    for i, (c, r) in enumerate(zip(pts, HORN_R)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        rings.append(ngon_ring(c, e1, e2, r, 6, 0.0))
    hc = lambda j, k: HORN if j < 4 else HORN_D
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Horn' + sfx, rr, hc, HORN, HORN_D)
        M.pivot['Horn' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # beard: chunky tapered tuft hanging from the chin (bound later to Jaw)
    jb = bvh_of(jaw_faces)
    bp, _ = surf(jb, P0 + U * 0.245 - VV * 0.10, (0, 0, 1))         # chin underside, ray from below
    # wedge: wide flat front, ~0.35 x head length below the chin, tip slightly forward; one clean cream cell
    bl = 0.35 * HEAD_LEN + 0.035              # measured from the chin underside, which sits ~3.5 cm above the jaw bottom
    cs = [bp + Vector((0, 0.004, 0.028)), bp + Vector((0, -0.004, -0.010)), bp + Vector((0, -0.016, -bl * 0.55)),
          bp + Vector((0, -0.030, -bl))]
    rs = [(0.046, 0.028), (0.058, 0.034), (0.040, 0.025), (0.005, 0.005)]
    M.loft('Beard', [[c + X * (rx * math.cos(a)) + Y * (ry * math.sin(a)) for a in [2 * math.pi * k / 6 for k in range(6)]]
                     for c, (rx, ry) in zip(cs, rs)], BEARD, BEARD, BEARD)
    M.pivot['Beard'] = bp.copy()


# ---------------- legs: one continuous tapered 8-sided prism per leg (Upper + Lower tucked), dark hoof cap ----------------
def build_legs(M):
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda yy, z, r, sy=1.0: ngon_ring(Vector((x, yy, z)), X, Y, r, 8, math.pi / 8, sy)
            if kind == 'Front':
                # top ring hidden in the chest; visible top 0.064 -> bottom 0.056 (x1.14), knee at 0.235 (joint only)
                up = [(y, 0.60, 0.072, 1.12), (y, 0.36, 0.064, 1.06), (y - 0.004, 0.235, 0.060, 1.0)]
                z_up = 0.56
            else:
                # thigh slanting back to the hock, cannon forward-down to the hoof (clear hock bend, no band)
                up = [(y, 0.62, 0.080, 1.25), (y - 0.004, 0.40, 0.072, 1.2), (y + 0.025, 0.31, 0.066, 1.1),
                      (y + 0.050, 0.250, 0.061, 1.0)]
                z_up = 0.58
            R = [ring(*r) for r in up]
            M.loft(kind + 'Upper' + sfx, R, WHITE, WHITE, WHITE)
            back = centroid(R[-2]) - centroid(R[-1])
            pre = tuck(R[-1], back, 0.86, 0.03)
            M.loft(kind + 'Lower' + sfx, [pre[0], pre[1], ring(y, 0.06, 0.056)], WHITE, WHITE, WHITE)
            M.loft(kind + 'Foot' + sfx, [ring(y, z, r) for z, r in [(0.0, 0.066), (0.068, 0.062), (0.080, 0.050)]],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, z_up))
            M.pivot[kind + 'Lower' + sfx] = centroid(R[-1])
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.07))


# ---------------- tail: short upright pointed leaf, Tail1-3 ----------------
def build_tail(M):
    pts = [Vector((0, y, z)) for y, z in TAIL_PTS]

    def ring(i, scale=1.0):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        rx, ry = TAIL_R[i]
        return [pts[i] + e1 * (rx * scale * math.cos(a)) + e2 * (ry * scale * math.sin(a)) for a in [2 * math.pi * k / 6 for k in range(6)]]
    R = [ring(i) for i in range(len(pts))]
    M.loft('Tail1', [R[0], R[1]], WHITE, WHITE, WHITE)
    pre = tuck(R[1], -(pts[2] - pts[1]), 0.86, 0.02)
    M.loft('Tail2', [pre[0], pre[1], R[2]], WHITE, WHITE, WHITE)
    pre = tuck(R[2], -(pts[3] - pts[2]), 0.86, 0.02)
    M.loft('Tail3', [pre[0], pre[1], R[3], R[4]], WHITE, WHITE, WHITE)
    M.pivot['Tail1'] = pts[0].lerp(pts[1], 0.5); M.pivot['Tail2'] = pts[1].copy(); M.pivot['Tail3'] = pts[2].copy()


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
    build_legs(M); build_tail(M)
    bm = M.P.bm
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
    for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
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
    poll = max(p.z for p in W(obs['Head'])); horn = max(p.z for nm_ in ('Horn.L',) for p in W(obs[nm_]))
    beard = min(p.z for p in W(obs['Beard']))
    hl = max(p.z for p in W(obs['Horn.L'])); hr = max(p.z for p in W(obs['Horn.R']))
    hlen = (P0 + U * HEAD_LEN - P0).length * HEAD_SCALE
    hh = (poll - min(p.z for p in W(obs['Jaw'])))
    bc = sum((p for p in W(obs['Beard'])), Vector()) / len(W(obs['Beard']))
    print(f'BEARD centroid y {bc.y:.3f} z {bc.z:.3f} | neck2 front y {min(p.y for p in W(obs["Neck2"])):.3f} neck1 front y {min(p.y for p in W(obs["Neck1"])):.3f}')
    print(f'HORNS top L {hl:.4f} R {hr:.4f} | tip above poll {max(p.z for p in W(obs["Horn.L"]) if True) - poll:.3f} | head height {hh:.3f} '
          f'| beard length {max(p.z for p in W(obs["Jaw"])) and (min(p.z for p in W(obs["Jaw"])) - beard):.3f} vs head length {hlen:.3f}')
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->tail {tail - nose:.3f} back {back:.3f} belly {belly:.3f} poll {poll:.3f} horn tip {horn:.3f} '
          f'beard tip {beard:.3f}')
    print(f'BODY contour-snapped vertices {M.snapped}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Goat_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Goat_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B):
    views = [('ref', REF_VIEW), ('prev', PREVIEW_VIEW), ('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)),
             ('front', (0.0, -1.0, 0.12)), ('top', (0.3, -0.25, 1.0))]
    tiles = [rn.ref_tile(REF, 400)]
    for nm, v in views:
        p = os.path.join(CHECK, f'Goat_look_{nm}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.62, 0.78))
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Goat_look_sheet.png'))
    sm = rn.resize(rn.load_px(os.path.join(CHECK, 'Goat_look_ref.png')), 128)
    rn.compose([sm], 1, os.path.join(CHECK, 'Goat_look_128.png'), pad=0)
    os.remove(os.path.join(CHECK, 'Goat_look_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-08 Goat', CMD)
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
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
