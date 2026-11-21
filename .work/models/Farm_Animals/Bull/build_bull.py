# build_bull.py - LIV-09 Bull (Farm Animals extension, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_bull.py -- LIV-09 build|look|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_bull)
# look  : build + EEVEE frames (reference angle, preview, side, back, front, top) -> one sheet + 128 px thumb (TEMP)
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Cow/Goat/Horse).
# Structure copied from ../Goat/build_goat.py (Model/loft/tuck/objects/coplanar_all/look); horns + ear leaf from ../Cow,
# stocky legs + hind hock bend from ../Horse. Shared modules (Tools/blender, _common) are only imported.
# Rework 1 (coordinator): paper-craft look = few large facets (12-sided body, 9 rings on the muscle lines, no half-step
# lattice) + 4 brown shades assigned per facet (quad) from its normal; sideways cream horns; big ears; polygon head with a
# flat forehead and a brow over the eyes; nose pad; longer legs; tail close to the rump reaching the hocks.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Bull'
TAG = 'FarmAnimals_Bull'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-09.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_bull')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.53, -1.0, 0.30)        # LIV-09 reference: ~28 deg off the nose axis toward the bull's left, ~13 deg above
PREVIEW_VIEW = (0.92, -0.88, 0.20)    # pack preview: front-left three-quarter close to the reference angle
BUDGET = 2400

PALETTE = ['#8E5638', '#7E4A31', '#6C3D27', '#56301F',     # 0 brown light (top), 1 mid, 2 dark (rear/low side), 3 underside
           '#94593D', '#A87253', '#2E1B14', '#2E1E17',     # 4 muzzle, 5 nose pad, 6 nostril, 7 eye (dark brown)
           '#4A3228', '#F0C99A', '#C99474', '#9AA0A6',     # 8 hoof, 9 horn cream, 10 ear inner tan, 11 ring metal
           '#3F2519', '#B5835A', '#6E9F4A', '#8E959B']     # 12 tail tuft, 13-15 series spares
LIGHT, MID, DARK, UNDER, MUZZLE, PAD, NOSTRIL, EYE, HOOF, HORN, EAR_IN, RING, TUFT = range(13)
SH = -1                                   # placeholder: shade this facet from its normal
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))

# ---------------- layout (before head scale, length factor and centre-of-mass shift) ----------------
NB = 12                                   # body sides (large facets)
# body rings on the muscle lines: chest front, brisket, hump/shoulder, behind the shoulder, mid barrel, rear barrel, hip,
# rump, rump end. (y, half width, z bottom, z top)
BODY_PROF = [(-0.92, 0.30, 0.90, 1.52, 2.4), (-0.80, 0.50, 0.50, 1.78, 2.1), (-0.58, 0.56, 0.46, 1.90, 1.8),
             (-0.32, 0.54, 0.52, 1.80, 2.0), (0.02, 0.48, 0.62, 1.60, 2.3), (0.36, 0.43, 0.68, 1.45, 2.4),
             (0.64, 0.42, 0.72, 1.40, 2.4), (0.84, 0.36, 0.80, 1.37, 2.4), (0.94, 0.19, 0.95, 1.30, 2.4)]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 8)}
# neck: centre (y, z), (half width, half height); very short and thick, crest runs from the hump to the poll
NECK_AX = [(-0.64, 1.25), (-0.84, 1.32), (-0.96, 1.42), (-1.02, 1.52), (-1.06, 1.58)]
NECK_R = [(0.44, 0.50), (0.42, 0.47), (0.36, 0.40), (0.30, 0.31), (0.22, 0.22)]
# head: curved axis, polygon section (flat forehead, bevelled corners carrying the eyes, flat cheeks, flat jaw line)
P0 = Vector((0, -1.02, 1.66))
HPROF = [(0.55, 1.0), (1.0, 0.62), (1.0, -0.25), (0.62, -0.92), (0.22, -1.0), (-0.22, -1.0), (-0.62, -0.92), (-1.0, -0.25),
         (-1.0, 0.62), (-0.55, 1.0)]
# (s, tilt deg, half width, half h forehead side, half h throat side, brow)
HEAD = [(-0.04, 58, 0.180, 0.150, 0.150, 0), (0.05, 58, 0.270, 0.205, 0.190, 0), (0.115, 56, 0.290, 0.225, 0.200, 1),
        (0.205, 52, 0.270, 0.195, 0.200, 0), (0.335, 44, 0.245, 0.155, 0.175, 0), (0.465, 36, 0.265, 0.145, 0.160, 0),
        (0.54, 30, 0.225, 0.110, 0.125, 0)]
HEAD_LEN = HEAD[-1][0]
MUZZLE_J = 4                              # head bands from this ring on are muzzle colour
# horns: offsets from the base point on the poll (x outward, y, z) - mostly sideways, slightly up and forward
# horns (before the head scale): out sideways almost horizontally ~0.9x the head width, last third up and slightly forward
HORN_PATH = [(-0.05, 0.0, -0.02), (0.0, 0.0, 0.0), (0.14, -0.01, 0.0), (0.28, -0.02, 0.005), (0.40, -0.035, 0.02),
             (0.48, -0.06, 0.07), (0.53, -0.10, 0.14), (0.55, -0.13, 0.21)]
HORN_R = [0.060, 0.062, 0.056, 0.049, 0.040, 0.030, 0.018, 0.002]
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose', 'NoseRing', 'Horn.L', 'Horn.R')
HEAD_SCALE = 1.38                         # head group about the head/neck joint (reference head is big)
HEAD_Q = Vector((0, -1.00, 1.62))
YS = 1.00                                 # global length factor (nose -> rump ~2.5 m)
FRONT = (0.30, -0.56)
HIND = (0.27, 0.60)
LEG_SY = 1.08                             # leg/hoof depth factor (front-back)
# tail: root on the rump top, then hanging free 25 deg off vertical, away from the rump; diamond tuft (2x strand width)
TAIL_PTS = [(0.86, 1.30), (0.97, 1.36), (1.08, 1.30), (1.19, 1.11), (1.30, 0.92), (1.37, 0.80)]
TAIL_R = [0.048, 0.046, 0.040, 0.036, 0.034, 0.033]
TUFT_SPEC = [(0.05, 0.050), (0.13, 0.072), (0.23, 0.050), (0.31, 0.004)]   # (distance along the hang, apothem)
TAIL_DIR = (0.0, 0.50, -0.866)

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Horn.L', 'Horn.R',
              'Eye.L', 'Eye.R', 'Nose', 'NoseRing',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-09', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


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


def lerp_tab(T, s):
    if s <= T[0][0]: return T[0][1:]
    if s >= T[-1][0]: return T[-1][1:]
    for a, b in zip(T, T[1:]):
        if a[0] <= s <= b[0]:
            t = (s - a[0]) / (b[0] - a[0]); return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, len(a)))


def shade(n):
    """paper-craft shading per facet: light top, mid flanks facing forward/sideways, dark rear/low flanks, darkest belly"""
    if n.z > 0.55: return LIGHT
    if n.z < -0.50: return UNDER
    if n.y > 0.40 or n.z < -0.12: return DARK
    return MID


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Bull'); self.pivot = {}; self.groups = []
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                s = col(j, k) if callable(col) else col
                pair = [P.face([a, b, c], s), P.face([a, c, d], s)]
                faces += pair
                if s == SH: self.groups.append(pair)
        for cap, ring in ((cap0, list(reversed(R[0]))), (cap1, list(R[-1]))):
            if cap is None: continue
            f = P.face(ring, cap); faces.append(f)
            if cap == SH: self.groups.append([f])
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return faces

    def torus(self, name, rings, col):
        """closed ring of rings (no caps)"""
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); m = len(R); faces = []
        for j in range(m):
            for k in range(n):
                a, b = R[j][k], R[j][(k + 1) % n]; c, d = R[(j + 1) % m][(k + 1) % n], R[(j + 1) % m][k]
                for tri in ((a, b, c), (a, c, d)):
                    faces.append(P.face(list(tri), col))
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, False))
        return faces

    def apply_shading(self):
        """after normals are final: one shade per facet group (both triangles of a quad share it -> large facets)"""
        sl = self.P.slot
        for g in self.groups:
            n = sum((f.normal * f.calc_area() for f in g), Vector())
            n = n.normalized() if n.length > 1e-12 else Vector((0, 0, 1))
            for f in g: f[sl] = shade(n)


# ---------------- body ----------------
def body_ring(y, w, zb, zt, pt):
    return ring_xyz(Vector((0, y, (zb + zt) / 2)), w, (zt - zb) / 2, (zt - zb) / 2, NB, X, Z, pt, 2.6)


def build_body(M):
    rings = [body_ring(*r) for r in BODY_PROF]
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft(part, rs, SH, SH, SH)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0), 0.86, 0.05)
            M.loft(part, rs[:-1] + [pre[1], pre[0]], SH, SH, SH)
    M.pivot['Pelvis'] = Vector((0, 0.50, 1.10))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[5][0], 1.06))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[3][0], 1.10))


# ---------------- neck ----------------
def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AX]
    rings = []; T = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, len(cs) - 1)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = crest direction (up)
        if e1.z < 0: e1 = -e1
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h * 0.96, 10, X, e1, 2.5, 2.3)); T.append(t)
    M.loft('Neck1', rings[0:3], SH, SH, SH)
    pre = tuck(rings[2], -T[2], 0.86, 0.035)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], SH, SH, SH)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- head ----------------
def axes(tilt):
    a = math.radians(tilt)
    return Vector((0, -math.cos(a), -math.sin(a))), Vector((0, -math.sin(a), math.cos(a)))


def frame(s):
    """centre, U (poll -> nose) and VV (forehead normal) of the curved head axis at s (integrated from P0 at s = 0)"""
    tl = [(h[0], h[1]) for h in HEAD]
    n = 60; c = P0.copy(); step = s / n
    for i in range(n):
        u, _ = axes(lerp_tab(tl, step * (i + 0.5))[0]); c = c + u * step
    u, v = axes(lerp_tab(tl, s)[0])
    return c, u, v


def head_dims(s):
    return lerp_tab([(h[0], h[2], h[3], h[4]) for h in HEAD], s)


def head_ring(c, v, w, ht, hb, brow):
    out = []
    for px, pv in HPROF:
        sx = 1.0 + (0.05 * brow if abs(px) == 1.0 and pv > 0 else 0.0)
        sv = (ht * (1.0 + 0.14 * brow)) if pv > 0 else hb
        out.append(c + X * (px * w * sx) + v * (pv * sv))
    return out


def build_head(M):
    rings = []
    for s, tilt, w, ht, hb, brow in HEAD:
        c, u, v = frame(s)
        rings.append(head_ring(c, v, w, ht, hb, brow))
    col = lambda j, k: MUZZLE if j >= MUZZLE_J else SH
    faces = M.loft('Head', rings, col, SH, PAD)
    M.pivot['Head'] = frame(0.02)[0]
    return faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d, back=0.6):
    d = Vector(d).normalized(); o = Vector(target) - d * back
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {tuple(target)}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n.normalized()


def build_face(M, head_faces):
    hb = bvh_of(head_faces)
    # eyes: dark brown 8-gon discs, 5 mm proud, on the bevelled forehead corner just under the brow ridge
    s_eye = 0.20
    c, u, v = frame(s_eye); w, ht, hbt = head_dims(s_eye)
    nrm = (X * (0.38 * ht) + v * (0.45 * w)).normalized()
    hp, n = surf(hb, c + X * (0.80 * w) + v * (0.78 * ht), -nrm)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        cc = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(cc - a * 0.018, e1, e2, 0.046, 8), ngon_ring(cc + a * 0.005, e1, e2, 0.046, 8)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = cc.copy()
    # nostrils (part Nose): dark elongated 6-gons on the nose pad
    c, u, v = frame(HEAD_LEN)
    hp, n = surf(hb, c + X * 0.085 + v * 0.025, -u)
    ax = (n + X * 0.25).normalized()
    cen = []
    for sx in (1, -1):
        cc = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, X)
        M.loft('Nose', [ngon_ring(cc - a * 0.016, e1, e2, 0.025, 6, 0.0, 1.45), ngon_ring(cc + a * 0.004, e1, e2, 0.025, 6, 0.0, 1.45)],
               NOSTRIL, NOSTRIL, NOSTRIL)
        cen.append(cc)
    M.pivot['Nose'] = (cen[0] + cen[1]) / 2
    # nose ring: grey octagonal torus through the septum, hanging in front of the chin
    hs, ns = surf(hb, c - v * 0.045, -u)
    R, r = 0.070, 0.016
    C = hs - Z * 0.056 + Y * 0.004
    rings = []
    for k in range(8):
        a = math.pi / 8 + 2 * math.pi * k / 8
        rad = X * math.cos(a) + Z * math.sin(a)
        p = C + rad * (R / math.cos(math.pi / 8))
        rings.append([p + rad * (r * math.cos(b)) + Y * (r * math.sin(b)) for b in [2 * math.pi * i / 6 for i in range(6)]])
    M.torus('NoseRing', rings, RING)
    M.pivot['NoseRing'] = hs.copy()
    # jaw: chin block under the muzzle
    rings = []
    for s, w, h in [(0.335, 0.10, 0.040), (0.42, 0.13, 0.050), (0.50, 0.12, 0.045), (0.535, 0.09, 0.032)]:
        cc, uu, vv = frame(s); hbot = head_dims(s)[2]
        rings.append(ring_xyz(cc - vv * (hbot - 0.012), w, h, h, 8, X, vv, 2.2, 2.2))
    M.loft('Jaw', rings, lambda j, k: MUZZLE if j >= 1 else SH, SH, MUZZLE)
    M.pivot['Jaw'] = frame(0.40)[0] - frame(0.40)[2] * 0.12
    # ears: big leaves sideways under the horns (0.28 m out of the head), light tan inner face toward the front
    c, u, v = frame(0.10)
    hp, n = surf(hb, c + X * 0.6 - v * 0.04, -X)
    d = Vector((1.0, 0.12, -0.10)).normalized()
    _, ea, eb = pc.basis(d, (0, -0.6, 1.0))            # horizontal flap: width up-forward, inner face forward-down
    if eb.y > 0: eb = -eb                              # +eb = front (inner) face
    prof = [(1, 0), (0.6, 1), (-0.6, 1), (-1, 0), (-0.6, -1), (0.6, -1)]
    base = hp - d * 0.05
    spec = [(t * 0.84, a * 0.84, b * 0.84) for t, a, b in
            [(0.0, 0.050, 0.028), (0.09, 0.100, 0.036), (0.19, 0.105, 0.032), (0.27, 0.070, 0.024), (0.33, 0.012, 0.009)]]
    rings = [[base + d * t + ea * (a * pa) + eb * (b * pb) for pa, pb in prof] for t, a, b in spec]
    col = lambda j, k: EAR_IN if (k == 1 and j in (1, 2)) else SH
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, SH, SH)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # horns: long, thick at the root, mostly sideways, slightly up and forward, cream, sharp tip; root sunk in the poll
    c, u, v = frame(0.03)
    hp, n = surf(hb, c + X * 0.19, -(Z * 0.6 + v * 0.4))
    pts = [hp + Vector(o) for o in HORN_PATH]
    rings = []
    for i, (cc, rr_) in enumerate(zip(pts, HORN_R)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (0, 0, 1))
        rings.append(ngon_ring(cc, e1, e2, rr_, 6, 0.0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Horn' + sfx, rr, HORN, HORN, HORN)
        M.pivot['Horn' + sfx] = hp.copy() if sx > 0 else mir(hp)


# ---------------- legs ----------------
def build_legs(M):
    """each leg reads as ONE tapered 8-sided prism (top radius 1.15x the bottom); Lower is tucked inside Upper at the
    knee/hock, so the surface runs on without a band; hind leg has a subtle hock angle; flared dark hoof cap"""
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x0, y0) in (('Front', FRONT), ('Hind', HIND)):
            x = x0 * sx
            if kind == 'Front':
                rt, rb, zt = 0.218, 0.188, 0.48
                up = [(1.05, y0, 0.80), (0.48, y0, 1.0), (0.36, y0 - 0.005, 1.0)]
                lo_end = (0.11, y0, 1.0)
            else:
                rt, rb, zt = 0.212, 0.184, 0.72
                up = [(1.10, y0 - 0.07, 0.75), (0.72, y0 - 0.02, 1.0), (0.48, y0 + 0.05, 1.0)]
                lo_end = (0.11, y0 + 0.01, 1.0)
            rz = lambda z: rb + (rt - rb) * min(1.12, (z - 0.11) / (zt - 0.11))
            ring = lambda z, yy, xk: ngon_ring(Vector((x * xk, yy, z)), X, Y, rz(z), 8, math.pi / 8, LEG_SY)
            ur = [ring(*p) for p in up]
            M.loft(kind + 'Upper' + sfx, ur, SH, SH, SH)
            knee = Vector((x, up[-1][1], up[-1][0])); above = Vector((x * up[-2][2], up[-2][1], up[-2][0]))
            pre = tuck(ur[-1], above - knee, 0.86, 0.035)
            M.loft(kind + 'Lower' + sfx, [pre[0], pre[1], ring(*lo_end)], SH, SH, SH)
            fy = lo_end[1]
            M.loft(kind + 'Foot' + sfx, [ngon_ring(Vector((x, fy, z)), X, Y, r, 8, math.pi / 8, LEG_SY)
                                         for z, r in ([(0.0, 0.222), (0.12, 0.202), (0.12, 0.165), (0.19, 0.165)] if kind == 'Front' else
                                                       [(0.0, 0.218), (0.12, 0.198), (0.12, 0.162), (0.19, 0.162)])],
                   HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, up[1][1], 0.98))
            M.pivot[kind + 'Lower' + sfx] = knee.copy()
            M.pivot[kind + 'Foot' + sfx] = Vector((x, fy, 0.13))


# ---------------- tail: close to the rump, down to the hocks, pointed dark tuft ----------------
def build_tail(M):
    pts = [Vector((0, y, z)) for y, z in TAIL_PTS]
    last = pts[-1]; td = Vector(TAIL_DIR).normalized()
    tuft_pts = [last + td * t for t, _ in TUFT_SPEC]
    allp = pts + tuft_pts
    allr = TAIL_R + [r for _, r in TUFT_SPEC]

    def ring(i):
        t = (allp[min(i + 1, len(allp) - 1)] - allp[max(i - 1, 0)]).normalized()
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return [allp[i] + e1 * (allr[i] * math.cos(a)) + e2 * (allr[i] * math.sin(a)) for a in [2 * math.pi * k / 6 for k in range(6)]]
    R = [ring(i) for i in range(len(allp))]
    M.loft('Tail1', R[0:3], SH, SH, SH)
    pre = tuck(R[2], -(allp[3] - allp[2]), 0.86, 0.025)
    M.loft('Tail2', [pre[0], pre[1], R[3], R[4]], SH, SH, SH)
    pre = tuck(R[4], -(allp[5] - allp[4]), 0.86, 0.025)
    M.loft('Tail3', [pre[0], pre[1]] + R[5:], lambda j, k: TUFT if j >= 2 else SH, SH, TUFT)
    M.pivot['Tail1'] = pts[0].lerp(pts[1], 0.5); M.pivot['Tail2'] = pts[2].copy(); M.pivot['Tail3'] = pts[4].copy()


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
    for v in bm.verts: v.co.y *= YS
    for k in M.pivot: M.pivot[k].y *= YS
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    M.apply_shading()
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
            if f[sl2] < 0: raise RuntimeError(f'unshaded face in {nm}')
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
    print(f'TRIS total {tot} | target ~{BUDGET} (coordinator cap ~2800)')
    W = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in W(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for nm_ in ('Head', 'Nose', 'Jaw') for p in W(obs[nm_]))
    rump = max(p.y for p in W(obs['Pelvis']))
    tail = max(p.y for nm_ in ('Tail1', 'Tail2', 'Tail3') for p in W(obs[nm_]))
    back = max(p.z for nm_ in ('Spine1', 'Spine2', 'Pelvis') for p in W(obs[nm_]))
    belly = min(p.z for p in W(obs['Spine1']))
    poll = max(p.z for p in W(obs['Head'])); horn = max(p.z for p in W(obs['Horn.L']))
    span = max(p.x for p in W(obs['Horn.L'])) - min(p.x for p in W(obs['Horn.R']))
    hw = max(p.x for p in W(obs['Head'])) - min(p.x for p in W(obs['Head']))
    ear = max(p.x for p in W(obs['Ear.L'])) - max(p.x for p in W(obs['Head']))
    ringz = min(p.z for p in W(obs['NoseRing'])); tuftz = min(p.z for p in W(obs['Tail3']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f}')
    print(f'  nose->rump {rump - nose:.3f} nose->tail {tail - nose:.3f} withers {back:.3f} belly {belly:.3f} ({belly / back:.2f} of '
          f'withers) poll {poll:.3f} horn tip {horn:.3f} horn span {span:.3f} head width {hw:.3f} (span/head {span / hw:.2f}) '
          f'ear beyond head {ear:.3f} ring bottom {ringz:.3f} tuft bottom {tuftz:.3f}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Bull_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B):
    views = [('ref', REF_VIEW), ('prev', PREVIEW_VIEW), ('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)),
             ('front', (0.0, -1.0, 0.12)), ('top', (0.3, -0.25, 1.0))]
    tiles = [rn.ref_tile(REF, 400)]
    for nm, v in views:
        p = os.path.join(CHECK, f'Bull_look_{nm}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.62, 0.78))
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Bull_look_sheet.png'))
    sm = rn.resize(rn.load_px(os.path.join(CHECK, 'Bull_look_ref.png')), 128)
    rn.compose([sm], 1, os.path.join(CHECK, 'Bull_look_128.png'), pad=0)
    os.remove(os.path.join(CHECK, 'Bull_look_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-09 Bull', CMD)
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
