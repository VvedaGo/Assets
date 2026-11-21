# build_pig.py - LIV-06 Pig (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_pig.py -- LIV-06 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_pig)
# look  : build + EEVEE frames (reference angle, side) into the check folder
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Cow/Cat/Calf).
# Structure copied from ../Calf/build_calf.py (Model/loft/tuck/objects), head frame + ray-cast features from ../Cow.
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import pack_common as pc
import pack_shapes as ps
import animal_render as rn

ASSET = 'FMS_Pig'
TAG = 'FarmAnimals_Pig'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-06.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_pig')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.42, -1.0, 0.15)       # LIV-06 reference: front-left, head almost frontal, slightly above
PREVIEW_VIEW = (0.55, -1.00, 0.18)
BUDGET = 1700
DROP = 0.035                         # body, head and tail lowered onto the legs (short-legged look of the reference)

PALETTE = ['#F2A6A1', '#E59692', '#F8C0B9', '#E08985',     # 0 body, 1 back, 2 belly, 3 ear outside
           '#D47A7C', '#EC8B88', '#D5767A', '#8E3D42',     # 4 ear inside, 5 snout, 6 snout rim, 7 nostril
           '#2A1D17', '#3A2E28', '#E08E8B', '#B5835A',     # 8 eye, 9 hoof, 10 knee band, 11-15 spare series colours
           '#6E9F4A', '#8E959B', '#C8473B', '#F2E6C9']
BODY, BACK, BELLY, EAR, EAR_IN, SNOUT, SNOUT_RIM, NOSTRIL, EYE, HOOF, KNEE = range(11)

# ---------------- layout (before the centre-of-mass shift) ----------------
NB = 10                                  # body sides (large flat facets)
# body profile: y, half width, z bottom, z top
BODY_PROF = [(-0.46, 0.150, 0.400, 0.740), (-0.39, 0.265, 0.290, 0.845), (-0.22, 0.318, 0.248, 0.885),
             (-0.02, 0.328, 0.238, 0.902), (0.18, 0.325, 0.242, 0.912), (0.36, 0.292, 0.290, 0.898),
             (0.50, 0.205, 0.420, 0.825), (0.575, 0.060, 0.565, 0.690)]
SPLIT = {'Spine2': (0, 2), 'Spine1': (2, 4), 'Pelvis': (4, 7)}

# head frame: U along the head (poll -> snout), VV head 'up'
HEAD_TILT = math.radians(6)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))
X = Vector((1, 0, 0))
P0 = Vector((0, -0.42, 0.695))
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.10
HEAD_Q = Vector((0, -0.42, 0.66))          # head/neck joint the head group is scaled about
# (s along U, half width top, half width bottom, half height top, half height bottom)
HEAD_RINGS = [(0.00, 0.140, 0.150, 0.130, 0.130), (0.05, 0.205, 0.222, 0.190, 0.200), (0.13, 0.238, 0.252, 0.215, 0.225),
              (0.22, 0.238, 0.258, 0.212, 0.226), (0.30, 0.222, 0.248, 0.198, 0.214), (0.355, 0.190, 0.218, 0.168, 0.188),
              (0.385, 0.140, 0.165, 0.120, 0.140)]
SNOUT_DV = -0.055                       # snout centre below the head axis
# snout rings (s, half width, half height)
SNOUT_RINGS = [(0.27, 0.095, 0.085), (0.34, 0.130, 0.115), (0.43, 0.130, 0.115), (0.455, 0.108, 0.094)]
NOS = dict(dx=0.055, dv=-0.004, r=0.024, sy=1.25, depth=0.025)
NECK_AXIS = [(-0.34, 0.600), (-0.41, 0.630), (-0.48, 0.660)]
NECK_R = [(0.230, 0.225), (0.215, 0.215), (0.190, 0.185)]
FRONT = (0.172, -0.30)
HIND = (0.175, 0.36)
TAIL = dict(root=(0.515, 0.735), centre=(0.71, 0.87), yaw=-35.0, r0=0.110, r1=0.036, th0=-80.0, th1=330.0, step=37.0,
            rad0=0.026, rad1=0.019, split=(0.15, 0.34))

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-06', 'build'])[:2]


def hsh(*a):
    """deterministic pseudo-random in [-1, 1] (same input -> same value, so mirrored vertices get the same offset)"""
    x = math.sin(sum((i + 1) * 12.9898 * (v + 0.37) for i, v in enumerate(a))) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


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


JIT = 0.015            # body facet jitter: radial +-1.5 % (large near-planar facets, as the Piglet)


def body_ring(y, w, zb, zt, n=NB, pt=2.5, pb=2.7, j=0):
    out = []; zc, h = (zt + zb) / 2, (zt - zb) / 2
    end = j in (0, len(BODY_PROF) - 1)
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        lvl = min(k, n - k)
        f = 1.0 if end else 1.0 + JIT * hsh(j, lvl, 1)
        dy = 0.0
        out.append(Vector((w * f * spow(c, 2 / p), y + dy, zc + h * f * spow(s, 2 / p))))
    return out


def ring_xyz(cen, wt, wb, ht, hb, n, ex, ey, pt=2.4, pb=2.4, ph=0.0):
    out = []
    for k in range(n):
        th = math.pi / 2 + ph + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * ((wt if s >= 0 else wb) * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
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
        self.P = pc.Part('Pig'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False, diag=None):
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                zk = (a.co.z + d.co.z) / 2; zk1 = (b.co.z + c.co.z) / 2
                up = 0 if zk1 > zk else 1
                tris = ((a, b, c), (a, c, d))
                if diag is not None and diag(j, k):
                    tris = ((a, b, d), (b, c, d)); up = 0 if (a.co.z + b.co.z) / 2 < (c.co.z + d.co.z) / 2 else 1
                for ti, tri in enumerate(tris):
                    s = col(j, k, ti == up) if callable(col) else col
                    faces.append(P.face(list(tri), s))
        if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(R[-1]), cap1))
        self.tag(name, faces)
        P.comp.append((name, faces, ground))
        return R

    def tag(self, name, faces):
        for f in faces: f[self.pl] = PART_ORDER.index(name)


# ---------------- body: pink, darker back strip, lighter belly ----------------
def body_col_for(j0):
    def col(j, k, tip):
        gj = j0 + j                                  # global band index along the body
        lvl = k if k < NB // 2 else NB - 1 - k      # 0 = beside the back ridge, NB/2-1 = beside the belly line
        if lvl == 0: return BACK
        if lvl == NB // 2 - 1 and 1 <= gj <= 5: return BELLY
        return BODY
    return col


def body_diag(j0):
    def d(j, k):
        lvl = k if k < NB // 2 else NB - 1 - k
        v = hsh(j0 + j, lvl, 3) > 0
        return v if k < NB // 2 else not v
    return d


def build_body(M):
    rings = [body_ring(*r, j=i) for i, r in enumerate(BODY_PROF)]
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft(part, rs, body_col_for(i0), BODY, BODY)
        else:   # rear end tucked into the part behind it
            pre = tuck(rs[-1], (0, 1, 0))
            M.loft(part, rs[:-1] + [pre[1], pre[0]], body_col_for(i0), BODY, BODY)
    M.pivot['Pelvis'] = Vector((0, 0.30, 0.60))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[SPLIT['Spine1'][0]][0], 0.60))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[0][0] + 0.05, 0.60))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = [ring_xyz(c, w, w, h, h, 8, X, Vector((0, 0, 1)), 2.4, 2.4, 0.0) for c, (w, h) in zip(cs, NECK_R)]
    col = lambda j, k, tip: BELLY if k in (3, 4) else BODY
    M.loft('Neck1', rings[0:2], col, BODY, BODY)
    pre = tuck(rings[1], (0, 1, 0), 0.86, 0.02)
    M.loft('Neck2', [pre[0], pre[1], rings[2]], col, BODY, BODY)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[1].copy()


# ---------------- head ----------------
def head_col(j, k, tip):
    kk = (k + 1) % 12; lvl = min(kk, 12 - kk)           # 0 = top face (centred), 6 = bottom face
    if lvl == 0 and j >= 1: return BACK
    if lvl >= 5: return BELLY
    return BODY


def build_head(M):
    rings = [ring_xyz(P0 + U * s, wt, wb, ht, hb, 12, X, VV, 2.4, 2.6, math.pi / 12) for s, wt, wb, ht, hb in HEAD_RINGS]
    for j, r in enumerate(rings):
        if j in (0, len(rings) - 1): continue
        c = P0 + U * HEAD_RINGS[j][0]
        for k in range(12):
            r[k] = c + (r[k] - c) * (1.0 + 0.035 * hsh(j, min(k, 11 - k), 5))
    M.loft('Head', rings, head_col, BODY, BODY,
           diag=lambda j, k: (hsh(j, min(k, 11 - k), 6) > 0) if k < 6 else not (hsh(j, min(k, 11 - k), 6) > 0))
    head_faces = list(M.P.comp[-1][1])
    M.pivot['Head'] = P0 + U * 0.03
    # snout disc: 12-gon, protruding, chamfered front edge, flat front with 2 recessed nostrils
    cen = lambda s: P0 + U * s + VV * SNOUT_DV
    rings = [ring_xyz(cen(s), w, w, h, h, 12, X, VV, 2.0, 2.0, math.pi / 12) for s, w, h in SNOUT_RINGS]
    R = M.loft('Nose', rings, lambda j, k, tip: SNOUT_RIM, SNOUT_RIM, None)
    nose_faces = M.P.comp[-1][1]
    fc = cen(SNOUT_RINGS[-1][0]); nr = NOS
    holes = []
    for sx in (1, -1):
        c = fc + X * (sx * nr['dx']) + VV * nr['dv']
        holes.append([M.P.bm.verts.new(p) for p in ngon_ring(c, X, VV, nr['r'], 8, math.pi / 8, nr['sy'])])
    new = ps.fill(M.P, [R[-1]] + holes, SNOUT, U)
    for hl in holes: new += ps.blind(M.P, hl, U, nr['depth'], NOSTRIL, NOSTRIL)
    M.tag('Nose', new); nose_faces += new
    M.pivot['Nose'] = cen(0.34)
    return head_faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d):
    d = Vector(d).normalized(); o = Vector(target) - d * 0.5
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {target}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n


# ---------------- flat folded pig ear: one triangular slab, hinged on the top-outer skull corner ----------------
HEAD_HW = 0.507                            # head width before HEAD_SCALE (0.558 m in the model)
HEAD_HH = 0.431                            # head height before HEAD_SCALE (0.474 m in the model)
FLAP = dict(
    hinge=(0.185, 0.150, 0.145),      # ray target for the hinge on the upper outer skull corner (X, along U, along VV), pre scale
    base=0.45,                        # base width x head width
    length=0.50,                      # base -> tip x head height
    thick=0.050,                      # slab thickness x head width (< 0.06)
    fold_at=0.40,                     # fold line at 40 % of the length
    fwd=60.0, out=25.0,               # first section: from vertical 60 deg forward and 25 deg out
    tip=(0.255, 0.300, 0.090),        # tip target (X, along U, along VV): level with the eyes, just outside the cheek
    tip_w=0.035,                      # blunt tip width x head width
    tip_shift=0.30,                   # tip centre shifted towards the outer base corner (x half base): points down-out
    sink=0.030)                       # root depth below the hinge (m, pre scale)
FLAP_PROF = [(1.0, 0.0), (0.7, 1.0), (-0.7, 1.0), (-1.0, 0.0), (-0.7, -1.0), (0.7, -1.0)]   # (width, thickness): flat slab
FLAP_OUTER, FLAP_INNER = (1,), (4,)   # profile faces: flat outer (+N) face, flat inner (-N) face


def flat_ear(hinge):
    """left ear: flat triangular slab. Section 1 (0 -> fold) rises along D1 (60 deg forward, 25 deg out from vertical),
    section 2 (fold -> tip) drapes along D2 towards the tip target. Both sections share the fold line W = D1 x D2, so the
    slab stays flat in each section with one crisp bend. Outer normal = convex side of the fold."""
    E = FLAP; L = E['length'] * HEAD_HH; Lf = E['fold_at'] * L
    up = VV; fw = U; out = X
    a1, a2 = math.radians(E['fwd']), math.radians(E['out'])
    D1 = (out * math.sin(a2) + (up * math.cos(a1) + fw * math.sin(a1)) * math.cos(a2)).normalized()
    F = hinge + D1 * Lf
    tx, tu, tv = E['tip']
    T = P0 + U * tu + VV * tv + X * tx
    D2 = (T - F).normalized()
    W = D1.cross(D2).normalized()
    if W.dot(out) < 0: W = -W                                    # + width = outer side of the base
    N1 = W.cross(D1).normalized(); N2 = W.cross(D2).normalized()
    if N1.dot(D2 - D1) > 0: N1, N2 = -N1, -N2                    # outer normal on the convex side of the fold
    Nf = (N1 + N2).normalized(); mit = 1.0 / max(0.4, N1.dot(Nf))
    a = 0.5 * E['base'] * HEAD_HW; t = 0.5 * E['thick'] * HEAD_HW
    tipc = F + D2 * (L - Lf)
    tw = 0.5 * E['tip_w'] * HEAD_HW; sh = E['tip_shift'] * a
    edge = lambda u: (-a + u * (sh + a), a + u * (sh - a))        # (inner, outer) width coordinate at u = h / L
    st = [(hinge - D1 * E['sink'], N1, edge(0.0), 1.0), (hinge, N1, edge(0.0), 1.0),
          (F, Nf, edge(E['fold_at']), mit), (tipc, N2, (sh - tw, sh + tw), 1.0)]
    rings = []
    for c, n, (wi, wo), m in st:
        mid = 0.5 * (wi + wo); hw = 0.5 * (wo - wi)
        rings.append([c + W * (mid + hw * pa) + n * (t * m * pb) for pa, pb in FLAP_PROF])
    return rings, dict(fold=F, tip=tipc, W=W, D1=D1, D2=D2, L=L, Lf=Lf, a=a, t=t)


EYE_C = P0 + U * 0.37 + VV * 0.105 + X * 0.118     # eye target on the face (pre head scale)


def build_face(M, head_faces):
    hb = bvh_of(head_faces)
    # eyes: dark 12-gon discs set flush on the face (best-fit plane of the facets under them, 1.5 mm clear, 12 mm sunk)
    hp, n = surf(hb, EYE_C, -U)
    for sfx, sx in (('.L', 1),):
        c = hp; a = n
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        H = [surf(hb, p, -a)[0] for p in ngon_ring(c, e1, e2, 0.027, 12)]
        nrm = Vector()
        for i in range(12):
            p, q = H[i], H[(i + 1) % 12]
            nrm += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
        nrm.normalize()
        if nrm.dot(a) < 0: nrm = -nrm
        cc = sum(H, Vector()) / 12
        off = max(max((h - cc).dot(nrm) for h in H), (surf(hb, c, -a)[0] - cc).dot(nrm)) + 0.0015
        _, e1, e2 = pc.basis(nrm, (0, 0, 1))
        er = [ngon_ring(cc - nrm * 0.012, e1, e2, 0.026, 12), ngon_ring(cc + nrm * off, e1, e2, 0.026, 12)]
        M.loft('Eye.L', er, EYE, EYE, EYE)
        M.loft('Eye.R', [[mir(q) for q in r] for r in er], EYE, EYE, EYE)
        print(f'  eye proud {off*1000:.1f} mm (right eye mirrored)')
        M.pivot['Eye.L'] = c.copy(); M.pivot['Eye.R'] = mir(c)
    # ears: flat folded flaps hinged on the upper outer skull corners; right ear = exact X-mirror of the left
    tx, tu, tv = FLAP['hinge']
    hp, n = surf(hb, P0 + U * tu + VV * tv + X * tx, -X * 0.6 - VV * 0.8)
    rings, info = flat_ear(hp)
    col = lambda j, k, tip: EAR_IN if k in FLAP_INNER else (BODY if k in FLAP_OUTER else EAR)
    def sdist(p):
        co, nn, _, d = hb.find_nearest(p)
        return d if (p - co).dot(nn) >= 0 else -d
    pts = [p for r in rings for p in r]
    crown = max(v.co.z for f in head_faces for v in f.verts)
    rear = max(v.co.y for f in head_faces for v in f.verts)
    fold_h = (info['fold'] - hp).z
    ev = (EYE_C - P0).dot(VV); tip = info['tip']
    gap_eye = min(math.hypot(p.x - EYE_C.x, p.z - EYE_C.z) for p in pts if p.y < EYE_C.y + 0.08) if any(p.y < EYE_C.y + 0.08 for p in pts) else 9.0
    S = HEAD_SCALE
    print(f'  EAR hinge (pre-scale) {tuple(round(c, 3) for c in hp)} | tip {tuple(round(c, 3) for c in tip)} | base {2 * info["a"] * S:.3f} m '
          f'({FLAP["base"]:.2f} x head w) length {info["L"] * S:.3f} m ({FLAP["length"]:.2f} x head h) thick {2 * info["t"] * S:.3f} m | '
          f'tip vs eye height {((tip - P0).dot(VV) - ev) * S:+.3f} m, tip X {tip.x * S:.3f} | '
          f'behind head rear plane {max(0.0, max(p.y for p in pts) - rear) * S:.3f} m | above crown {(max(p.z for p in pts) - crown) * S:+.3f} m '
          f'(fold height {fold_h * S:.3f}) | eye gap {gap_eye * S:.3f} m | flap clearance (fold+tip) {min(sdist(p) for r in rings[2:] for p in r) * S:+.3f} m')
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, col, EAR, EAR)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # jaw: small light chin under the snout
    j0 = P0 + U * 0.25 - VV * 0.165
    jr = [(-0.03, 0.085, 0.040, 0.030), (0.07, 0.105, 0.048, 0.045), (0.155, 0.080, 0.038, 0.034)]
    M.loft('Jaw', [ring_xyz(j0 + U * t, w, w, ht, hb_, 8, X, VV, 2.4, 2.4, math.pi / 8) for t, w, ht, hb_ in jr],
           BELLY, BELLY, BELLY)
    M.pivot['Jaw'] = j0.copy()


# ---------------- legs: each one tapered 8-gon prism (top radius 1.15 x bottom), one loop at the hoof line ----------------
LEG = dict(rb=0.080, rt=0.092, z_top=0.45, z_knee=0.17, z_hoof=0.075, inset=0.985)


def build_legs(M):
    Y = Vector((0, 1, 0)); L = LEG
    r = lambda z: L['rb'] + (L['rt'] - L['rb']) * z / L['z_top']
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, rr: ngon_ring(Vector((x, y, z)), X, Y, rr, 8, math.pi / 8)
            zk, zh = L['z_knee'], L['z_hoof']
            # Upper: inside the body -> knee on the taper; Lower: starts 15 mm up inside the Upper (0.985 x radius)
            M.loft(kind + 'Upper' + sfx, [ring(L['z_top'], r(L['z_top'])), ring(zk, r(zk))], BODY, BODY, BODY)
            M.loft(kind + 'Lower' + sfx, [ring(zk + 0.015, r(zk + 0.015) * L['inset']), ring(zh - 0.006, r(zh - 0.006) * L['inset'])],
                   BODY, BODY, BODY)
            M.loft(kind + 'Foot' + sfx, [ring(0.0, r(0.0) * 1.02), ring(zh, r(zh) * 1.02)], HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, L['z_top']))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, zk))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, zh))


# ---------------- tail: corkscrew in the mid plane (x = 0) ----------------
def tail_curve():
    T = TAIL; ry, rz = T['root']; cy, cz = T['centre']
    th0, th1 = math.radians(T['th0']), math.radians(T['th1'])
    r = lambda th: T['r0'] + (T['r1'] - T['r0']) * (th - th0) / (th1 - th0)
    sp = lambda th: Vector((0, cy + r(th) * math.cos(th), cz + r(th) * math.sin(th)))
    s0 = sp(th0)
    pts = [Vector((0, ry, rz)).lerp(s0, i / 12) for i in range(12)]
    n = 240
    pts += [sp(th0 + (th1 - th0) * i / n) for i in range(n + 1)]
    Rz = Matrix.Rotation(math.radians(T['yaw']), 3, 'Z'); o = Vector((0, ry + 0.06, 0))
    pts = [o + Rz @ (p - o) if p.y > o.y else p for p in pts]
    S = [0.0]
    for a, b in zip(pts, pts[1:]): S.append(S[-1] + (b - a).length)
    stem = (s0 - Vector((0, ry, rz))).length
    return pts, S, stem


def tail_at(pts, S, s):
    s = max(0.0, min(s, S[-1]))
    for i in range(len(S) - 1):
        if S[i] <= s <= S[i + 1]:
            t = (s - S[i]) / max(1e-9, S[i + 1] - S[i])
            return pts[i].lerp(pts[i + 1], t), (pts[i + 1] - pts[i]).normalized()
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def build_tail(M):
    T = TAIL; pts, S, stem = tail_curve(); L = S[-1]
    th0, th1 = math.radians(T['th0']), math.radians(T['th1'])
    # ring stations: stem every ~0.05 m, spiral every `step` degrees (arc length found by search)
    st = [0.0, 0.07, 0.14, stem]
    nsp = int(round((T['th1'] - T['th0']) / T['step']))
    seg = S[12:]
    for i in range(1, nsp + 1):
        st.append(seg[round(240 * i / nsp)])
    st = sorted(set(round(s, 5) for s in st))
    rad = lambda s: T['rad0'] + (T['rad1'] - T['rad0']) * s / L

    def ring(s, r=None):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, rad(s) if r is None else r, 6, 0.0)
    s1, s2 = T['split']
    s1 = min(st, key=lambda v: abs(v - s1)); s2 = min(st, key=lambda v: abs(v - s2))
    segs = [('Tail1', [s for s in st if s <= s1], BODY), ('Tail2', [s for s in st if s1 <= s <= s2], BODY),
            ('Tail3', [s for s in st if s >= s2], BODY)]
    for name, ss, colr in segs:
        rs = [ring(e) for e in ss]
        if name == 'Tail1':
            c, t = tail_at(pts, S, 0.0)
            rs = [ngon_ring(c - t * 0.04, *pc.basis(t, (1, 0, 0))[1:], rad(0) * 0.9, 6, 0.0)] + rs[1:]
        else:
            c, t = tail_at(pts, S, ss[0])
            pre = tuck(rs[0], -t, 0.86, 0.015)
            rs = [pre[0], pre[1]] + rs[1:]
        if name == 'Tail3':     # blunt rounded tip
            c, t = tail_at(pts, S, L); _, e1, e2 = pc.basis(t, (1, 0, 0))
            rs.append(ngon_ring(c + t * 0.010, e1, e2, rad(L) * 0.82, 6, 0.0))
            rs.append(ngon_ring(c + t * 0.019, e1, e2, rad(L) * 0.42, 6, 0.0))
        M.loft(name, rs, colr, colr, colr)
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
    build_body(M); build_neck(M)
    hf = build_head(M); build_face(M, hf)
    build_legs(M); tl = build_tail(M)
    bm = M.P.bm
    hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
    for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
    LEGP = ('Upper', 'Lower', 'Foot')
    dv = {v for nm, faces, _ in M.P.comp if not any(t in nm for t in LEGP) for f in faces for v in f.verts}
    for v in dv: v.co.z -= DROP
    for k in M.pivot:
        if not any(t in k for t in LEGP): M.pivot[k] = M.pivot[k] - Vector((0, 0, DROP))
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
    chk = pc.comp_checks(M.P, mirror_skip=('Tail1', 'Tail2', 'Tail3'))
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
    back = max((obs['Pelvis'].matrix_world @ v.co).z for v in obs['Pelvis'].data.vertices)
    hd = [obs['Head'].matrix_world @ v.co for v in obs['Head'].data.vertices]
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} back top {back:.3f} | head w '
          f'{max(p.x for p in hd) - min(p.x for p in hd):.3f} h {max(p.z for p in hd) - min(p.z for p in hd):.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.1f} L | geometry shift {tuple(round(c, 4) for c in M.shift)} '
          f'| tail length {M.tail_len:.3f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Pig_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Pig_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== LIV-06 Pig', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Pig_look_ref.png'), view=REF_VIEW, fill=(0.62, 0.78))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Pig_look_prev.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
    elif CMD == 'views':
        B = build(os.path.join(CHECK, 'tex')); tiles = []
        tag = sys.argv[sys.argv.index('--') + 3] if len(sys.argv) > sys.argv.index('--') + 3 else 'v'
        for i, (v, fl) in enumerate([(REF_VIEW, (0.62, 0.78)), ((1, 0, 0.06), (0.8, 0.8)), ((0, 1, 0.18), (0.6, 0.78)),
                                     ((-0.8, 0.9, 0.35), (0.7, 0.8)), ((0, -1, 0.08), (0.6, 0.78)), ((0.6, -0.5, 0.45), (0.7, 0.8))]):
            pth = os.path.join(CHECK, f'v{i}.png')
            rn.preview(B['sc'], list(B['obs'].values()), pth, view=v, fill=fl)
            tiles.append(rn.resize(rn.load_px(pth), 330)); os.remove(pth)
        rn.compose([rn.ref_tile(REF, 330)] + tiles, 4, os.path.join(CHECK, f'Pig_{tag}_views.png'))
    elif CMD == 'close':
        B = build(os.path.join(CHECK, 'tex')); O = B['obs']; tiles = []
        shots = [(['Head', 'Nose', 'Jaw'], (0.35, -1, -0.25)), (['Head', 'Nose', 'Jaw', 'Ear.L'], (1, -0.15, -0.1)),
                 (['Tail1', 'Tail2', 'Tail3'], (0.2, 1, 0.3)), (['Tail1', 'Tail2', 'Tail3'], (-1, 0.2, 0.1)),
                 (['FrontUpper.L', 'Spine2', 'FrontLower.L'], (1, -0.4, -0.05)), (['HindUpper.L', 'Pelvis', 'HindLower.L'], (1, 0.5, -0.05))]
        for i, (nms, v) in enumerate(shots):
            pth = os.path.join(CHECK, f'c{i}.png')
            rn.preview(B['sc'], [O[n] for n in nms], pth, view=v, fill=(0.8, 0.85))
            tiles.append(rn.resize(rn.load_px(pth), 330)); os.remove(pth)
        rn.compose(tiles, 3, os.path.join(CHECK, 'Pig_close.png'))
    elif CMD == 'probe':
        B = build(os.path.join(CHECK, 'tex')); O = B['obs']; tiles = []
        for i, nms in enumerate((['Head'], ['Ear.L', 'Ear.R'], ['Neck1', 'Neck2', 'Spine2'])):
            for o in O.values(): o.hide_render = o.name[len(ASSET) + 1:] not in nms
            pth = os.path.join(CHECK, f'p{i}.png')
            rn.preview(B['sc'], [O[n] for n in nms], pth, view=(0.35, -1, 0.1), fill=(0.8, 0.85))
            tiles.append(rn.resize(rn.load_px(pth), 300)); os.remove(pth)
        for o in O.values(): o.hide_render = False
        rn.compose(tiles, 3, os.path.join(CHECK, 'Pig_probe.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
