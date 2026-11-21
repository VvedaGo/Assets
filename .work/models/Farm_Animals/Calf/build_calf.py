# build_calf.py - LIV-02 Calf (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_calf.py -- LIV-02 build|look|export
# build : parts + palette + patches + checks + check sheet (%TEMP%/FarmAnimals_check_calf)
# look  : build + EEVEE frames (reference angle, side) into the check folder
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Cow/Cat).
# Structure copied from ../Cat/build_cat.py (Model/loft/tuck/objects), head frame + ray-cast features from ../Cow.
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Calf'
TAG = 'FarmAnimals_Calf'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-02.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_calf')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -0.78, 0.22)        # LIV-02 reference: left side from the front-left, low camera
PREVIEW_VIEW = (0.70, -1.0, 0.14)    # more frontal than REF_VIEW: the sun-lit face front + blaze read, sky behind the head
BUDGET = 1500

PALETTE = ['#AE6740', '#86492B', '#F2E7DC', '#E2D5C6',     # 0 brown, 1 brown dark (tuft), 2 white, 3 white shade
           '#DE9B88', '#9A5649', '#D4877A', '#2A1D17',     # 4 nose pink, 5 nostril, 6 ear pink, 7 eye
           '#3A2E28', '#B5835A', '#6E9F4A', '#8E959B',     # 8 hoof, 9-15 spare series colours
           '#C8473B', '#F2E6C9', '#D8B65A', '#7A5233']
BROWN, BROWN_D, WHITE, WHITE_D, NOSE, NOSTRIL, EAR_PINK, EYE, HOOF = range(9)

# ---------------- layout (before the centre-of-mass shift) ----------------
SLANT = 0.12
NB = 14                                  # body sides
# body profile (polish pass: chest -> rump 1.125 m, belly 0.32): y, half width, z bottom, z top
BODY_PROF = [(-0.55, 0.150, 0.480, 0.800), (-0.51, 0.220, 0.340, 0.865), (-0.43, 0.260, 0.270, 0.895),
             (-0.30, 0.275, 0.245, 0.905), (-0.12, 0.280, 0.240, 0.910), (0.08, 0.280, 0.240, 0.915),
             (0.26, 0.276, 0.248, 0.922), (0.40, 0.267, 0.265, 0.925), (0.49, 0.245, 0.300, 0.920),
             (0.545, 0.180, 0.400, 0.880), (0.575, 0.100, 0.520, 0.810)]
BODY_RINGS = [(-0.55, 0), (-0.51, 0), (-0.43, 0.3), (-0.33, 0.7), (-0.22, 1), (-0.11, 1), (0.0, 1), (0.11, 1), (0.22, 1),
              (0.33, 1), (0.43, 0.6), (0.51, 0.25), (0.575, 0)]
SPLIT = {'Spine2': (0, 4), 'Spine1': (4, 8), 'Pelvis': (8, 12)}
FROZEN_LONG = {0, 4, 8, 12}              # joint/end rings stay planar (vertices may only slide along the ring)
# BROWN patches on the cream coat (|x| -> mirror-symmetric geometry): centre, radii, slant dy/dz, wobble amplitude, phase.
# A saddle over shoulder + back and one rump patch; the cream gap between them widens downward (reference band).
BLOBS = [((0.15, -0.33, 0.64), (0.27, 0.15, 0.44), 0.05, 0.07, 0.4),     # shoulder: withers down into the front legs
         ((0.18, 0.16, 0.82), (0.24, 0.24, 0.26), 0.20, 0.08, 1.7),      # big mid-rear patch over the back (upper flank)
         ((0.20, 0.44, 0.40), (0.18, 0.16, 0.24), -0.10, 0.07, 2.2)]     # thigh patch down into the hind legs
# white: chest, slanted band widening into the belly, belly, rump top around the (brown) tail root
TAIL_SWING = math.radians(32)            # tail swung out towards +X (camera side) so it clears the rump

# head frame (cow approach): U along the head poll -> nose, VV head 'up'
HEAD_TILT = math.radians(45)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))
X = Vector((1, 0, 0))
P0 = Vector((0, -0.53, 0.99))
# (s along U, half width, half height top, half height bottom)
HEAD_RINGS = [(0.00, 0.110, 0.110, 0.100), (0.05, 0.195, 0.185, 0.165), (0.14, 0.240, 0.215, 0.190),
              (0.25, 0.228, 0.195, 0.175), (0.34, 0.180, 0.140, 0.160), (0.42, 0.150, 0.100, 0.135),
              (0.48, 0.118, 0.065, 0.100)]
# muzzle pad (s, half w, ht, hb, centre offset along VV)
MUZZLE_S = 0.38                          # pink starts here (shell over the head front, rings at the head ring positions)
NECK_AXIS = [(-0.43, 0.66), (-0.47, 0.76), (-0.50, 0.82), (-0.52, 0.89), (-0.54, 0.95)]
NECK_R = [(0.150, 0.150), (0.150, 0.150), (0.140, 0.140), (0.120, 0.120), (0.100, 0.100)]
FRONT = (0.125, -0.33)
HIND = (0.125, 0.37)
TAIL_CP = [(0.52, 0.86), (0.60, 0.87), (0.67, 0.84), (0.725, 0.77), (0.755, 0.68), (0.765, 0.59)]
TAIL_SPLIT = (0.12, 0.25)

HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.22
HEAD_Q = Vector((0, -0.51, 0.89))          # head/neck joint the head group is scaled about

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-02', 'build'])[:2]


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


def body_ring(yk, f, n=NB, pt=2.6, pb=3.0):
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
        self.P = pc.Part('Calf'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')
        self.P.slot = self.P.bm.faces.layers.int['slot']

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                zk = (a.co.z + d.co.z) / 2; zk1 = (b.co.z + c.co.z) / 2
                up = 0 if zk1 > zk else 1
                for ti, tri in enumerate(((a, b, c), (a, c, d))):
                    s = col(j, k, ti == up) if callable(col) else col
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(R[-1]), cap1))
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R


# ---------------- body: brown with white bib, belly, flank band and rump (left = reference side) ----------------
def field(p):
    """< 0 inside a brown patch. Ellipsoid distance with a low-frequency wobble -> organic, rounded patch edges"""
    ax = abs(p.x); best = 9.0
    for (cx, cy, cz), (rx, ry, rz), sl, amp, ph in BLOBS:
        dy = p.y - (cy + sl * (p.z - cz))
        d = math.sqrt(((ax - cx) / rx) ** 2 + (dy / ry) ** 2 + ((p.z - cz) / rz) ** 2)
        wob = amp * math.sin(13.0 * p.y + 9.0 * p.z + 6.0 * ax + ph)
        best = min(best, d - 1.0 - wob)
    return best


def snap_rings(R):
    """move grid vertices onto the blob contour (each vertex at most once, at most half an edge) -> patch edges follow
    the contour instead of stair-stepping; returns field values and 'on contour' flags"""
    n = len(R[0]); F = [[field(p) for p in r] for r in R]; Z = [[False] * n for _ in R]
    cand = []
    for j in range(len(R)):
        for k in range(n):
            nbs = [] if k in (0, n // 2) else [(j, (k + 1) % n), (j, (k - 1) % n)]   # centre-line verts: no sideways move
            if j not in FROZEN_LONG: nbs += [(jj, k) for jj in (j - 1, j + 1) if 0 <= jj < len(R)]
            for jj, kk in nbs:
                if F[j][k] * F[jj][kk] < 0:
                    t = F[j][k] / (F[j][k] - F[jj][kk])
                    if t <= 0.5: cand.append((round(t, 9), j, k, jj, kk))
    cand.sort()
    moved = 0
    for t, j, k, jj, kk in cand:
        if Z[j][k] or Z[jj][kk] or F[j][k] * F[jj][kk] >= 0: continue
        t = F[j][k] / (F[j][k] - F[jj][kk])
        if t > 0.5: continue
        R[j][k] = R[j][k].lerp(R[jj][kk], t); Z[j][k] = True; F[j][k] = 0.0; moved += 1
    return F, Z, moved


def loft_field(M, name, rings, Fs, Zs, cap0, cap1):
    """quads split along the contour diagonal; triangle colour from its off-contour vertices (brown < 0)"""
    P = M.P; bm = P.bm
    R = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(R[0]); faces = []
    sg = lambda j, k: 0 if Zs[j][k] else (1 if Fs[j][k] > 0 else -1)

    def colour(tri, idx):
        ss = {sg(*i) for i in idx} - {0}
        if len(ss) == 1: return WHITE if ss.pop() > 0 else BROWN
        c = sum((v.co for v in tri), Vector()) / 3
        return WHITE if field(c) > 0 else BROWN
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
        faces.append(P.face(ring, WHITE if field(c) > 0 else BROWN))
    for f in faces: f[M.pl] = PART_ORDER.index(name)
    P.comp.append((name, faces, False))


def build_body(M):
    rings = [body_ring(y, f) for y, f in BODY_RINGS]
    F, Z, moved = snap_rings(rings)
    M.snapped = moved
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]; fs = F[i0:i1 + 1]; zs = Z[i0:i1 + 1]
        if part == 'Pelvis':
            loft_field(M, part, rs, fs, zs, True, True)
        else:   # rear end tucked into the parent behind it
            pre = tuck(rs[-1], (0, 1, 0))
            ext = [pre[1], pre[0]]
            loft_field(M, part, rs[:-1] + ext, fs[:-1] + [[field(p) for p in r] for r in ext],
                       zs[:-1] + [[False] * NB for _ in ext], True, True)
    M.pivot['Pelvis'] = Vector((0, 0.40, 0.65))
    M.pivot['Spine1'] = Vector((0, BODY_RINGS[8][0], 0.65))
    M.pivot['Spine2'] = Vector((0, BODY_RINGS[4][0], 0.65))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 8, X, e1))
    # k=0 nape (brown), k=3..4 throat (white)
    col = lambda j, k, tip: WHITE if k in (3, 4) else BROWN
    M.loft('Neck1', rings[0:3], col, BROWN, BROWN)
    t = (cs[2] - cs[3]).normalized()
    pre = tuck(rings[2], t, 0.86, 0.02)
    M.loft('Neck2', [pre[0], pre[1], rings[3], rings[4]], col, BROWN, BROWN)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


# ---------------- head ----------------
def head_colour(j, k, tip):
    """one centred face column (+-15 deg, ~0.27 x head width) is the blaze from the poll to the muzzle top"""
    m = (k + 1) % 12                                    # ring phase pi/12: face k=11 is the centred top face
    lvl = min(m, 12 - m)                                # 0 = top face (centred), 6 = bottom face
    if lvl == 0: return WHITE
    if j == 4 and lvl >= 5: return WHITE                # under the muzzle (chin side)
    return BROWN


def head_ring_at(s, grow=0.0):
    """head cross-section at s (linear between HEAD_RINGS, exactly like the loft), optionally grown outwards"""
    for a, b in zip(HEAD_RINGS, HEAD_RINGS[1:]):
        if a[0] <= s <= b[0] + 1e-9:
            t = (s - a[0]) / (b[0] - a[0])
            ra = ring_xyz(P0 + U * a[0], *a[1:], 12, X, VV, 2.5, 2.3, math.pi / 12)
            rb = ring_xyz(P0 + U * b[0], *b[1:], 12, X, VV, 2.5, 2.3, math.pi / 12)
            pts = [pa.lerp(pb, t) for pa, pb in zip(ra, rb)]
            c = P0 + U * s
            if grow:
                pts = [p + ((p - c) - U * (p - c).dot(U)).normalized() * grow for p in pts]
            return pts
    raise ValueError(s)


def build_head(M):
    rings = [ring_xyz(P0 + U * s, w, ht, hb, 12, X, VV, 2.5, 2.3, math.pi / 12) for s, w, ht, hb in HEAD_RINGS]
    M.loft('Head', rings, head_colour, BROWN, NOSE)          # front cap lies under the muzzle shell
    head_faces = list(M.P.comp[-1][1])
    M.pivot['Head'] = P0 + U * 0.02
    # muzzle (Nose): pink shell 4 mm proud over the front of the head, same ring stations (no step, no box);
    # closed by an inner ring sunk into the head; front cap 4 mm in front of the head's front cap
    g = 0.004; s_end = HEAD_RINGS[-1][0]
    inner = [P0 + U * (MUZZLE_S - 0.02) + (p - (P0 + U * MUZZLE_S)) * 0.80 for p in head_ring_at(MUZZLE_S)]
    shell = [inner, head_ring_at(MUZZLE_S, g), head_ring_at(0.42, g), [p + U * g for p in head_ring_at(s_end, g)]]
    M.loft('Nose', shell, NOSE, NOSE, NOSE)
    pad_faces = list(M.P.comp[-1][1])
    M.pivot['Nose'] = P0 + U * MUZZLE_S
    return head_faces, pad_faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d):
    d = Vector(d).normalized(); o = Vector(target) - d * 0.5
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {target}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n


def build_face(M, head_faces, pad_faces):
    hb = bvh_of(head_faces); pb = bvh_of(pad_faces)
    # eyes: dark 8-gon discs, 5 mm proud, on the brown cheeks looking forward-sideways
    hp, n = surf(hb, P0 + U * 0.22 + VV * 0.15 + X * 0.13, -X * 0.66 - VV * 0.75)
    ax = (n + Vector((0, -0.6, 0))).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(c - a * 0.012, e1, e2, 0.028, 8), ngon_ring(c + a * 0.005, e1, e2, 0.028, 8)],
               EYE, EYE, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nostrils: slanted flat 6-gons on the pad front, 3 mm proud
    hp, n = surf(pb, P0 + U * 0.49 + VV * -0.005 + X * 0.05, -U)
    up = (VV - n * VV.dot(n)).normalized(); side = up.cross(n).normalized()
    if side.x < 0: side = -side
    ang = math.radians(28)
    e1 = side * math.cos(ang) + up * math.sin(ang); e2 = n.cross(e1).normalized()
    for sx in (1, -1):
        c = hp if sx > 0 else mir(hp); nn = n if sx > 0 else mir(n)
        f1 = e1 if sx > 0 else mir(e1); f2 = e2 if sx > 0 else mir(e2)
        M.loft('Nose', [ngon_ring(c - nn * 0.008, f1, f2, 0.022, 6, sy=0.5), ngon_ring(c + nn * 0.003, f1, f2, 0.022, 6, sy=0.5)],
               NOSTRIL, NOSTRIL, NOSTRIL)
    # ears: leaf sideways, brown outside + rim, pink dish facing forward; roots sunk into the skull
    hp, n = surf(hb, P0 + U * 0.09 + VV * 0.09 + X * 0.2, -X * 0.8 - VV * 0.6)
    u = Vector((1.0, 0.12, 0.22)).normalized()                   # sideways, a little up and back
    fw = Vector((0, -1, -0.15))
    f = (fw - u * fw.dot(u)).normalized()                        # pink side faces forward
    s = u.cross(f).normalized()
    prof = [(1.0, 0.30), (0.70, 0.55), (0.40, -0.05), (-0.40, -0.05), (-0.70, 0.55), (-1.0, 0.30), (-0.45, -1.0), (0.45, -1.0)]
    base = hp - u * 0.035
    spec = [(0.0, 0.045, 0.022), (0.035, 0.060, 0.026), (0.11, 0.084, 0.030), (0.19, 0.088, 0.028), (0.28, 0.036, 0.016)]
    rings = [[base + u * t + s * (a * pa) + f * (b * pb_) for pa, pb_ in prof] for t, a, b in spec]
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k, tip: EAR_PINK if (k in (1, 2, 3) and j >= 1) else BROWN, BROWN, BROWN)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # jaw: white chin under the pad, pink lower lip at the front
    # jaw: chin block INSIDE the muzzle box and the head (no separate lip slab); it shows only when the Jaw bone opens
    j0 = P0 + U * 0.26 - VV * 0.07
    jr = [(-0.02, 0.065, 0.030, 0.022), (0.09, 0.085, 0.035, 0.030), (0.17, 0.070, 0.028, 0.024)]
    M.loft('Jaw', [ring_xyz(j0 + U * t, w, ht, hb_, 8, X, VV) for t, w, ht, hb_ in jr], NOSE, NOSE, NOSE)
    M.pivot['Jaw'] = j0.copy()


# ---------------- legs ----------------
def leg_r(z):
    return 0.109 + 0.068 * z               # 0.109 at the ground, 0.125 at the belly (0.24): top/bottom 1.15 (1.4x thicker)


def build_legs(M):
    Y = Vector((0, 1, 0)); Z_K, Z_H = 0.170, 0.075      # sock top = Upper|Lower joint, hoof top = Lower|Foot
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r: ngon_ring(Vector((x, y, z)), X, Y, r, 8, math.pi / 8)
            z_up = 0.45
            # upper (brown): top ring narrowed inside the body, then the straight taper down to the sock
            M.loft(kind + 'Upper' + sfx, [ring(z_up, 0.085), ring(0.30, leg_r(0.30)), ring(Z_K, leg_r(Z_K))], BROWN, BROWN, BROWN)
            # lower (white sock): proximal end tucked flush into the upper, down into the hoof cap
            pre = tuck(ring(Z_K, leg_r(Z_K)), (0, 0, 1), 0.86, 0.02)
            M.loft(kind + 'Lower' + sfx, [pre[0], pre[1], ring(0.04, leg_r(0.04))], WHITE, WHITE, WHITE)
            M.loft(kind + 'Foot' + sfx, [ring(0.0, leg_r(0.0) + 0.004), ring(Z_H, leg_r(Z_H) + 0.004)], HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, Z_K))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, Z_H))


# ---------------- tail ----------------
def tail_curve():
    y0 = TAIL_CP[0][0]
    P = [Vector(((y - y0) * math.sin(TAIL_SWING), y0 + (y - y0) * math.cos(TAIL_SWING), z)) for y, z in TAIL_CP]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    pts = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in [j / 16 for j in range(16)]:
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

    def ring(s, r):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 6, 0.0)
    rad = lambda s: 0.032 - 0.008 * s / L
    s1, s2 = TAIL_SPLIT
    segs = [('Tail1', [0.0, 0.06, s1], BROWN), ('Tail2', [s1, s2], WHITE), ('Tail3', [s2, L], WHITE)]
    for name, ss, colr in segs:
        rs = [ring(e, rad(e)) for e in ss]
        if name == 'Tail1':
            c, t = tail_at(pts, S, 0.0)
            rs = [ngon_ring(c - t * 0.05, *pc.basis(t, (1, 0, 0))[1:], rad(0) * 0.9, 6, 0.0)] + rs[1:]
        else:
            c, t = tail_at(pts, S, ss[0])
            pre = tuck(rs[0], -t, 0.86, 0.015)
            rs = [pre[0], pre[1]] + rs[1:]
        M.loft(name, rs, colr, colr, colr)
        M.pivot[name] = tail_at(pts, S, ss[0])[0]
    # leaf tuft on Tail3: spindle starting inside the tail end
    c, t = tail_at(pts, S, L)
    _, e1, e2 = pc.basis(t, (1, 0, 0))
    rr = [(-0.035, 0.024), (0.03, 0.058), (0.12, 0.064), (0.22, 0.008)]
    M.loft('Tail3', [ngon_ring(c + t * a, e1, e2, r, 6, 0.0, 0.75) for a, r in rr], BROWN_D, BROWN_D, BROWN_D)
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
    build_body(M); build_neck(M)
    hf, pf = build_head(M); build_face(M, hf, pf)
    build_legs(M); tl = build_tail(M)
    bm = M.P.bm
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
    for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
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
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    chk = pc.comp_checks(M.P, mirror_skip=('Tail1', 'Tail2', 'Tail3'))      # tail swung out on purpose
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
    print(f'TRIS total {tot} | target ~{BUDGET} (+20% = {int(BUDGET * 1.2)})')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = [o.matrix_world @ v.co for nm_ in ('Pelvis', 'Spine1', 'Spine2', 'Nose') for o in (obs[nm_],) for v in o.data.vertices]
    back = max((obs['Spine1'].matrix_world @ v.co).z for v in obs['Spine1'].data.vertices)
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} back top {back:.3f}')
    print(f'BODY contour-snapped vertices {M.snapped}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)} '
          f'| tail length {M.tail_len:.3f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror(excl. tail) {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} coplanar {cop}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Calf_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Calf_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-02 Calf', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Calf_look_ref.png'), view=REF_VIEW, fill=(0.62, 0.78))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Calf_look_front.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
