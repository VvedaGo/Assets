# build_fox.py - SML-02 Fox (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_fox.py -- SML-02 build|look|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_fox)
# look  : EEVEE sheet (reference, ref angle, side, back, front, top, right) + 128 px thumbnail
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Fox'
TAG = 'FarmAnimals_Fox'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\SML-02.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_fox')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -0.85, 0.32)        # SML-02 reference: face towards the camera, left flank receding, ~15 deg above
PREVIEW_VIEW = (0.85, -0.95, 0.25)
LENS = 50                            # the reference is a close, wide-angle shot (big near head, small rump)
PREVIEW_FILL = (0.74, 0.84)
BUDGET = 1500

PALETTE = ['#E2661E', '#EE7A2C', '#C9561A', '#B04716',     # 0 orange, 1 orange light, 2 orange dark, 3 orange deep
           '#F0DCC8', '#E1C8B0', '#3E2B25', '#2E1F1A',     # 4 cream, 5 cream shade, 6 stocking brown, 7 nose
           '#2A1D17', '#B5835A', '#6E9F4A', '#8E959B',     # 8 eye, 9-15 series spares
           '#C8473B', '#F2E6C9', '#D8B65A', '#7A5233']
OR, OR_L, OR_D, OR_DD, CR, CR_D, DK, NOSE, EYE = range(9)
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))

# ---------------- layout (before the centre-of-mass shift) ----------------
NB = 10
# body profile: y, half width, z bottom, z top (rework 2: torso ~+35% deeper/wider than round 1, deep chest, level back)
BODY_PROF = [(-0.282, 0.118, 0.290, 0.462), (-0.258, 0.172, 0.222, 0.518), (-0.190, 0.188, 0.196, 0.542),
             (-0.110, 0.182, 0.204, 0.547), (-0.020, 0.160, 0.232, 0.544), (0.080, 0.157, 0.240, 0.540),
             (0.200, 0.172, 0.236, 0.538), (0.275, 0.166, 0.250, 0.532), (0.322, 0.130, 0.286, 0.516),
             (0.345, 0.072, 0.336, 0.486)]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 9)}
FROZEN_LONG = {0, 3, 5, 9}
# bib: cream where y < BIB_Y and |x| < BIB_W * ((z - BIB_Z0) / (BIB_Z1 - BIB_Z0)) ** BIB_P  (centred rounded V,
# top width ~0.6 x chest width, front only)
BIB_Y, BIB_W, BIB_Z0, BIB_Z1, BIB_P = -0.200, 0.112, 0.200, 0.470, 0.6

NECK_AXIS = [(-0.170, 0.420), (-0.205, 0.468), (-0.234, 0.507), (-0.257, 0.540), (-0.277, 0.566)]
NECK_R = [(0.128, 0.112), (0.132, 0.115), (0.130, 0.112), (0.122, 0.104), (0.108, 0.094)]

# head: custom 10-point profile (x, z) unit, vertex 0 = top centre (nose ridge), 3/7 = cheek points (mutton chops)
HEAD_U = [(0.0, 1.0), (0.62, 0.86), (0.97, 0.32), (1.0, -0.30), (0.48, -0.86), (0.0, -1.0),
          (-0.48, -0.86), (-1.0, -0.30), (-0.97, 0.32), (-0.62, 0.86)]
# y, half width, z centre, half height top, half height bottom, cheek factor, cheek dz  (wider face, flared cheeks,
# snout ~10% shorter than round 1)
HEAD_RINGS = [(-0.255, 0.092, 0.590, 0.075, 0.070, 1.00, 0.0),
              (-0.290, 0.146, 0.600, 0.122, 0.108, 1.14, -0.006),
              (-0.335, 0.162, 0.596, 0.128, 0.110, 1.38, -0.020),
              (-0.380, 0.132, 0.586, 0.100, 0.098, 1.20, -0.006),
              (-0.416, 0.076, 0.562, 0.060, 0.074, 1.00, 0.0),
              (-0.448, 0.048, 0.544, 0.041, 0.055, 1.00, 0.0),
              (-0.476, 0.025, 0.537, 0.025, 0.032, 1.00, 0.0)]
JAW_RINGS = [(-0.370, 0.052, 0.480, 0.518), (-0.414, 0.043, 0.486, 0.520), (-0.456, 0.022, 0.498, 0.520)]
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.10
HEAD_Q = Vector((0, -0.265, 0.57))
EYE_R = 0.018
EYE_AT = (0.068, -0.396, 0.640)
EYE_LOOK = (0.42, -0.88, 0.10)
EAR_AT = (0.108, -0.312, 0.84)
EAR_H, EAR_HW = 0.170, 0.080

FRONT = (0.100, -0.165)
HIND = (0.108, 0.225)
STOCK_F, STOCK_H = 0.170, 0.190          # elbow / hock: dark stocking starts here, same radius above and below
TAIL_CP = [(0.275, 0.462), (0.385, 0.452), (0.500, 0.405), (0.600, 0.322), (0.685, 0.232), (0.760, 0.160),
           (0.830, 0.122), (0.890, 0.128)]
TAIL_RAD = [(0.0, 0.058), (0.07, 0.090), (0.15, 0.112), (0.25, 0.124), (0.34, 0.122), (0.42, 0.110), (0.49, 0.088),
            (0.55, 0.054), (0.60, 0.010)]
TAIL_SPLIT = (0.15, 0.32)
TAIL_WHITE = 0.39          # white brush tip from here (saw-tooth band before it)

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-02', 'build'])[:2]


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


def body_ring(y, n=NB, pt=2.15, pb=2.3):
    w, zb, zt = lerp_tab(BODY_PROF, y)
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(Vector((w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
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


def inner(ring, axis_into, scale=0.86, depth=0.025):
    """hidden ring `depth` inside the neighbouring part: the shared ring stays exact (no seam groove)"""
    c = centroid(ring); ab = Vector(axis_into).normalized()
    return [c + (p - c) * scale + ab * depth for p in ring]


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- bib label field (symmetric) + contour snap (copied from the Dog, one layout) ----------------
def label(p):
    ax, y, z = abs(p.x), p.y, p.z
    if y < BIB_Y and z > BIB_Z0:
        t = min(1.0, (z - BIB_Z0) / (BIB_Z1 - BIB_Z0))
        if ax < BIB_W * t ** BIB_P: return CR
    return OR


def crossing(a, b):
    la = label(a)
    if label(b) == la: return None
    lo, hi = 0.0, 1.0
    for _ in range(16):
        m = (lo + hi) / 2
        if label(a.lerp(b, m)) == la: lo = m
        else: hi = m
    return (lo + hi) / 2


def snap_rings(R, frozen_long):
    """move grid vertices onto the bib contour (each vertex at most once, at most half an edge). Only the left half is
    searched; the mirrored vertex (n - k) gets the mirrored move -> mirror-exact geometry."""
    n = len(R[0]); snapped = [[0] * n for _ in R]; cand = []
    for j in range(len(R)):
        for k in range(n):
            a = R[j][k]
            if a.x < -1e-7: continue
            nbs = [] if abs(a.x) < 1e-7 else [(j, (k + 1) % n), (j, (k - 1) % n)]
            if j not in frozen_long: nbs += [(jj, k) for jj in (j - 1, j + 1) if 0 <= jj < len(R)]
            for jj, kk in nbs:
                b = R[jj][kk]
                if b.x < -1e-7: continue
                t = crossing(a, b)
                if t is not None and t <= 0.5: cand.append((round(t, 9), j, k, jj, kk))
    cand.sort(); moved = 0
    for t, j, k, jj, kk in cand:
        mk, mkk = (n - k) % n, (n - kk) % n
        if snapped[j][k] or snapped[jj][kk] or snapped[j][mk] or snapped[jj][mkk]: continue
        R[j][k] = R[j][k].lerp(R[jj][kk], t); snapped[j][k] = 1; moved += 1
        if mk != k:
            R[j][mk] = mir(R[j][k]); snapped[j][mk] = 1; moved += 1
    return snapped, moved


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Fox'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')
        self.snapped = 0

    def _done(self, name, faces, ground=False):
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        self.P.comp.append((name, faces, ground))
        return faces

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False, diag=None):
        """col(j, k, upper) -> slot; diag(j, k) True splits the quad along b-d instead of a-c"""
        P = self.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(Rv[0]); faces = []
        for j in range(len(Rv) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k]
                tris = ((a, b, d), (b, c, d)) if (diag and diag(j, k)) else ((a, b, c), (a, c, d))
                qz = (a.co.z + b.co.z + c.co.z + d.co.z) / 4
                for tri in tris:
                    up = sum(v.co.z for v in tri) / 3 > qz
                    s = col(j, k, up) if callable(col) else col
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(Rv[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(Rv[-1]), cap1))
        return self._done(name, faces, ground)

    def loft_field(self, name, rings, snapped, cap0, cap1):
        """quads split along the contour; triangle colour from its free vertices, else centroid"""
        P = self.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(Rv[0]); faces = []

        def lab(j, k):
            if snapped[j][k]: return None
            return label(Rv[j][k].co)

        def colour(tri, idx):
            ls = {lab(*i) for i in idx} - {None}
            if len(ls) == 1: return ls.pop()
            return label(sum((v.co for v in tri), Vector()) / 3)
        for j in range(len(Rv) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                ia, ib, ic, id_ = (j, k), (j, k1), (j + 1, k1), (j + 1, k)
                a, b, c, d = Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k]
                la, lb, lc, ld = lab(*ia), lab(*ib), lab(*ic), lab(*id_)
                if la is None and lc is None: bd = False
                elif lb is None and ld is None: bd = True
                else: bd = (la is not None and lc is not None and la != lc) and not (lb is not None and ld is not None and lb != ld)
                tris = [((a, b, d), (ia, ib, id_)), ((b, c, d), (ib, ic, id_))] if bd else \
                       [((a, b, c), (ia, ib, ic)), ((a, c, d), (ia, ic, id_))]
                for tri, idx in tris:
                    faces.append(P.face(list(tri), colour(tri, idx)))
        for cap, r in ((cap0, 0), (cap1, len(Rv) - 1)):
            if cap is None: continue
            ring = list(reversed(Rv[0])) if r == 0 else list(Rv[-1])
            if cap is True: cap = label(sum((v.co for v in ring), Vector()) / len(ring))
            faces.append(P.face(ring, cap))
        return self._done(name, faces)

    def cone(self, name, ring, apex, slot):
        P = self.P; bm = P.bm
        Rv = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(Rv)
        faces = [P.face(Rv, slot)] + [P.face([Rv[(k + 1) % n], Rv[k], A], slot) for k in range(n)]
        return self._done(name, faces)


# ---------------- body ----------------
def build_body(M):
    ys = [p[0] for p in BODY_PROF]
    rings = [body_ring(y) for y in ys]
    snapped, moved = snap_rings(rings, FROZEN_LONG)
    M.snapped += moved
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]; zs = snapped[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft_field(part, rs, zs, OR, OR)
        else:   # rear (proximal to the pelvis) ring kept exact + hidden ring inside the part behind
            M.loft_field(part, rs + [inner(rs[-1], (0, 1, 0))], zs + [[0] * NB], True if part == 'Spine2' else OR, OR)
    M.pivot['Pelvis'] = Vector((0, ys[5], 0.39))
    M.pivot['Spine1'] = Vector((0, ys[3], 0.39))
    M.pivot['Spine2'] = Vector((0, ys[0] + 0.06, 0.39))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    L = lambda k: min(k, 7 - k)                            # 0 nape .. 3 throat
    col = lambda j, k, up: CR if L(k) >= 2 else OR
    M.loft('Neck1', rings[0:3], col, OR, OR)
    t = (cs[2] - cs[1]).normalized()
    M.loft('Neck2', [inner(rings[2], -t, 0.86, 0.025)] + rings[2:5], col, OR, OR)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- head ----------------
def head_ring(y, hw, zc, ht, hb, ch, cdz):
    out = []
    for k, (ux, uz) in enumerate(HEAD_U):
        f = ch if k in (3, 7) else 1.0
        out.append(Vector((hw * ux * f, y, zc + (ht if uz >= 0 else hb) * uz + (cdz if k in (3, 7) else 0.0))))
    return out


def head_colour(j, k, up):
    D = min(k, 9 - k)                    # 0 ridge, 1 forehead/eye slope, 2 temple->cheek point, 3 lower cheek, 4 under
    if D >= 3: return CR if j >= 1 else OR
    if D == 2:
        if j >= 3: return CR                               # muzzle sides cream
        if j == 2: return OR if up else CR                 # slanted border: cheek point -> under the eye
        return OR
    if D == 1 and j == 2 and not up: return OR_DD          # angled brow facet over the eye
    return OR


def head_diag(j, k):
    # band 2 (cheek point -> eye ring), side faces: split from the cheek point (ring 2) to the temple of ring 3
    return j == 2 and k == 2


def build_head(M):
    rings = [head_ring(*r) for r in HEAD_RINGS]
    faces = M.loft('Head', rings, head_colour, OR, NOSE, diag=head_diag)
    M.pivot['Head'] = HEAD_Q.copy()
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
    # eyes: dark-brown 8-gon cone discs on the forward slope, 2 mm proud
    look = Vector(EYE_LOOK).normalized()
    hp, n = surf(hb, EYE_AT, -look)
    ax = (n + look).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.002, e1, e2, EYE_R, 8), c - a * 0.012, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: dark rounded pad over the muzzle tip
    tip = HEAD_RINGS[-1]
    hp, n = surf(hb, (0, tip[0] - 0.01, tip[2] + 0.004), (0, 1, 0))
    up = (Z - n * Z.dot(n)).normalized(); side = up.cross(n).normalized()
    if side.x < 0: side = -side
    nr = lambda off, sc, dz=0.0: ngon_ring(hp + n * off + up * dz, side, up, 0.020 * sc, 8, math.pi / 8, 0.74)
    M.loft('Nose', [nr(-0.016, 0.85), nr(0.004, 1.0), nr(0.014, 0.70, -0.002)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # jaw: cream chin block under the muzzle
    jr = JAW_RINGS
    M.loft('Jaw', [ring_xyz(Vector((0, y, (a + b) / 2)), w, (b - a) / 2, (b - a) / 2, 6, X, Z) for y, w, a, b in jr], CR, CR, CR)
    M.pivot['Jaw'] = Vector((0, JAW_RINGS[0][0], 0.502))
    # ears: big upright triangles, cream inner dish framed by an orange rim, orange back; roots sunk into the skull
    hp, n = surf(hb, EAR_AT, (0, 0, -1))
    u = Vector((0.40, 0.08, 1.0)).normalized()
    f = Vector((0.30, -1.0, 0.0)); f = (f - u * f.dot(u)).normalized()
    s = u.cross(f).normalized()                                    # outer side (+X for the left ear)
    prof = [(1.0, 0.0), (0.66, 0.30), (0.0, 0.04), (-0.66, 0.30), (-1.0, 0.0), (0.0, -0.44)]
    base = hp - u * 0.018
    rings = [[base + u * h + s * (a * EAR_HW * sc) + f * (b * EAR_HW * sc) for a, b in prof]
             for h, sc in ((0.0, 1.0), (EAR_H * 0.55, 0.62), (EAR_H, 0.07))]
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k, up: CR if k in (1, 2) else OR, OR, OR)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)


# ---------------- legs ----------------
def build_legs(M):
    """tapered 8-sided prisms. Upper (orange) and Lower (dark stocking) share the elbow/hock ring exactly (same radius:
    no cuff, no step); the upper continues into the lower with a hidden smaller ring. Paw 1.1x the ankle, 3 short toes."""
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda yy, z, r, sy=1.0, xs=1.0: ngon_ring(Vector((x * xs, yy, z)), X, Y, r, 8, math.pi / 8, sy)
            if kind == 'Front':
                zs = STOCK_F
                up = [(y, 0.430, 0.052, 1.25, 0.6), (y, 0.300, 0.066, 1.15)]          # top sunk inwards: no shoulder box
                joint = (y - 0.004, zs, 0.057, 1.06)
                lo = [(y - 0.008, 0.100, 0.053, 1.02), (y - 0.010, 0.042, 0.050, 1.0)]
                fy = y - 0.014; z_up = 0.40
            else:
                zs = STOCK_H
                up = [(y, 0.460, 0.056, 1.50, 0.55), (y, 0.345, 0.080, 1.35), (y + 0.028, 0.255, 0.065, 1.15)]
                joint = (y + 0.045, zs, 0.057, 1.06)
                lo = [(y + 0.038, 0.100, 0.053, 1.02), (y + 0.033, 0.042, 0.050, 1.0)]
                fy = y + 0.026; z_up = 0.43
            jr = ring(*joint)
            M.loft(kind + 'Upper' + sfx, [ring(*r) for r in up] + [jr, inner(jr, (0, 0, -1), 0.86, 0.022)], OR, OR, OR)
            M.loft(kind + 'Lower' + sfx, [jr] + [ring(*r) for r in lo], DK, DK, DK)
            pr = lambda z, r, sy: ngon_ring(Vector((x, fy, z)), X, Y, r, 8, math.pi / 8, sy)
            M.loft(kind + 'Foot' + sfx, [pr(0.0, 0.051, 1.15), pr(0.008, 0.055, 1.15), pr(0.034, 0.055, 1.12),
                                         pr(0.058, 0.046, 1.0)], DK, DK, DK, ground=True)
            # three short toe blocks at the paw front (2 mm above the ground: no coplanar sole)
            for cx in (-0.034, 0.0, 0.034):
                def toe(yy, w, h, cx=cx):
                    return [Vector((x + cx - w / 2, yy, 0.002)), Vector((x + cx + w / 2, yy, 0.002)),
                            Vector((x + cx + 0.33 * w, yy, h)), Vector((x + cx - 0.33 * w, yy, h))]
                M.loft(kind + 'Foot' + sfx, [toe(fy - 0.040, 0.030, 0.040), toe(fy - 0.074, 0.027, 0.025)], DK, DK, DK)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, joint[0], zs))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, fy, 0.045))


# ---------------- tail: big bushy brush carried low, white tip ----------------
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
    sc = TAIL_RAD[-1][0] / L
    rad = lambda s: lerp_tab(TAIL_RAD, s * sc)[0]

    def ring(s):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, rad(s), 8, math.pi / 8)
    s1, s2 = TAIL_SPLIT[0] / sc, TAIL_SPLIT[1] / sc
    wf = TAIL_WHITE / sc
    segs = [('Tail1', [0.0, 0.07 / sc, s1]), ('Tail2', [s1, 0.24 / sc, s2]),
            ('Tail3', [s2, 0.38 / sc, wf, 0.49 / sc, 0.55 / sc, L])]
    for name, ss in segs:
        rs = [ring(e) for e in ss]
        sv = list(ss)
        if name != 'Tail1':                      # proximal ring exact + hidden ring inside the previous segment
            c, t = tail_at(pts, S, ss[0])
            rs = [inner(rs[0], -t, 0.86, 0.03)] + rs; sv = [ss[0] - 0.03] + sv
        cols = {}                                # W white, O orange, Z border band (saw-tooth)
        for j in range(len(sv) - 1):
            a, b = sv[j], sv[j + 1]
            cols[j] = 'W' if a >= wf - 1e-6 else ('Z' if b >= wf - 1e-6 else 'O')

        # saw-tooth: in the border band the triangle with two vertices on the tip-side ring is white
        P = M.P; bm = P.bm
        Rv = [[bm.verts.new(p) for p in r] for r in rs]
        faces = []
        for j in range(len(Rv) - 1):
            for k in range(8):
                k1 = (k + 1) % 8
                a, b, c, d = Rv[j][k], Rv[j][k1], Rv[j + 1][k1], Rv[j + 1][k]
                for tri, tip_side in (((a, b, c), False), ((a, c, d), True)):
                    s_ = {'W': CR, 'O': OR, 'Z': CR if tip_side else OR}[cols[j]]
                    faces.append(P.face(list(tri), s_))
        faces.append(P.face(list(reversed(Rv[0])), OR))
        faces.append(P.face(list(Rv[-1]), CR if name == 'Tail3' else OR))
        M._done(name, faces)
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


def shade_facets(M):
    """paper-craft shades: top-facing orange faces lighter, underside faces darker; cream underside shade"""
    sl = M.P.slot
    for f in M.P.bm.faces:
        nz = f.normal.z
        if f[sl] == OR:
            if nz > 0.55: f[sl] = OR_L
            elif nz < -0.45: f[sl] = OR_D
        elif f[sl] == CR and nz < -0.55:
            f[sl] = CR_D


def build_model():
    M = Model()
    build_body(M); build_neck(M)
    hf = build_head(M); build_face(M, hf)
    build_legs(M); tl = build_tail(M)
    bm = M.P.bm
    if HEAD_SCALE != 1.0:
        hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
        for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
        for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    shade_facets(M)
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
    print(f'TRIS total {tot} | target ~{BUDGET} (lead limit ~2200)')
    Wp = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    pts = [p for o in obs.values() for p in Wp(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    nose = min(p.y for nm_ in ('Head', 'Nose', 'Jaw') for p in Wp(obs[nm_]))
    rump = max(p.y for p in Wp(obs['Pelvis']))
    back = max(p.z for nm_ in ('Spine1', 'Spine2', 'Pelvis') for p in Wp(obs[nm_]))
    belly = min(p.z for p in Wp(obs['Spine1']))
    crown = max(p.z for p in Wp(obs['Head'])); ear = max(p.z for p in Wp(obs['Ear.L']))
    tailz = min(p.z for nm_ in ('Tail2', 'Tail3') for p in Wp(obs[nm_]))
    tail_end = max(p.y for p in Wp(obs['Tail3']))
    cheek = max(p.x for p in Wp(obs['Head']))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {rump - nose:.3f} rump->tail end {tail_end - rump:.3f} back {back:.3f} '
          f'belly {belly:.3f} crown {crown:.3f} ear top {ear:.3f} cheek span {2 * cheek:.3f} tail low z {tailz:.3f} '
          f'tail len {M.tail_len:.3f}')
    print(f'BIB contour-snapped vertices {M.snapped}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} problems {chk["problems"]} coplanar {cop}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 600, 400)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.8, 0.9, 0.45), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 400)] + tiles, 3, os.path.join(CHECK, f'Fox_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def box_down(a, f):
    H, W = a.shape[:2]; h, w = H // f, W // f
    return a[:h * f, :w * f].reshape(h, f, w, f, 4).mean(axis=(1, 3)).astype(np.float32)


def look(B, views=None):
    views = views or [('ref', REF_VIEW), ('side', (1, 0.0, 0.1)), ('back', (-0.55, 1.0, 0.3)),
                      ('front', (0.0, -1.0, 0.12)), ('top', (0.3, -0.25, 1.0)), ('right', (-1.0, -0.7, 0.25))]
    tiles = [rn.ref_tile(REF, 400)]
    for nm, v in views:
        p = os.path.join(CHECK, f'Fox_look_{nm}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=(0.66, 0.80), lens=LENS if nm == 'ref' else 50)
        tiles.append(rn.resize(rn.load_px(p), 400))
        if nm != 'ref': os.remove(p)
    rn.compose(tiles, 3, os.path.join(CHECK, 'Fox_look_sheet.png'))
    big = rn.load_px(os.path.join(CHECK, 'Fox_look_ref.png'))
    rn.compose([box_down(big, 6)], 1, os.path.join(CHECK, 'Fox_look_128.png'), pad=0)
    os.remove(os.path.join(CHECK, 'Fox_look_ref.png'))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-02 Fox', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B)
    elif CMD == 'head':
        B = build(os.path.join(CHECK, 'tex'))
        hs = [B['obs'][n] for n in HEAD_GROUP]; tiles = []
        for i, v in enumerate(((0.0, -1.0, 0.15), (1.0, 0.0, 0.1), (0.85, -1.0, 0.30), (-0.4, 1.0, 0.4))):
            p = os.path.join(CHECK, f'h{i}.png'); rn.preview(B['sc'], hs, p, view=v, fill=(0.8, 0.8))
            tiles.append(rn.resize(rn.load_px(p), 360)); os.remove(p)
        rn.compose(tiles, 2, os.path.join(CHECK, 'Fox_head_sheet.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL,
                   lens=LENS)
