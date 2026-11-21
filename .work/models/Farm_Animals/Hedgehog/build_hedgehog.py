# build_hedgehog.py - SML-04 Hedgehog (Farm Animals, skeleton Q-S), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_hedgehog.py -- SML-04 build|look|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_hedgehog)
# look  : EEVEE frames (reference angle, preview, side, front, back, top) composed into one sheet + 128 px thumbnail
# export: build + FBX (root empty + one mesh per skeleton part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Mouse/Rabbit).
# Helpers adapted from ../Mouse/build_mouse.py (loft, joints, eyes, checks, export) and ../Sheep/build_sheep.py (lobes
# as separate closed solids grouped per bone); shared modules imported read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Hedgehog'
TAG = 'FarmAnimals_Hedgehog'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\SML-04.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_hedgehog')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.80, -1.0, 0.36)          # SML-04 reference: front-left, ~40 deg off the front, ~16 deg above
PREVIEW_VIEW = (0.85, -1.0, 0.22)    # pack standard low 3/4 from the front-left, horizon + sky (Sheep/Lamb/Ram/Cat)
PREVIEW_FILL = (0.62, 0.78)
TARGET = 1100
LIMIT = 1900

PALETTE = ['#EDC79C', '#E3B98C', '#CFA176', '#D49E74',     # 0 cream light, 1 cream mid, 2 cream dark, 3 ear inner
           '#6B443D', '#5A3430', '#462823', '#4C2B26',     # 4 spike light, 5 spike mid, 6 spike dark, 7 core/hood
           '#2E1A15', '#4A2A22', '#C8A07A', '#B5835A',     # 8 eye, 9 nose, 10 sole, 11-15 series spares
           '#7A5233', '#6E9F4A', '#F2E6C9', '#D8B65A']
CR_L, CR_M, CR_D, EAR_IN, SP_L, SP_M, SP_D, CORE, EYE, NOSE, SOLE = range(11)
CREAM = 100            # placeholder: cream tone resolved per quad by its normal
BROWN = 101            # placeholder: core brown, belly underside -> cream dark

# ---------------- layout (before the centre-of-mass shift) ----------------
CORE_C = Vector((0.0, 0.016, 0.072)); CORE_R = (0.072, 0.090, 0.058); CORE_RZB = 0.046   # rz top / bottom
CORE_Q = 2.6                       # section superellipse exponent
CORE_N = 12
CORE_U = [-0.955, -0.80, -0.56, -0.28, 0.0, 0.24, 0.48, 0.70, 0.88, 0.975]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 9)}
# spike rows (round 3 rework): 4 staggered rows of broad low pyramids overlapping like scales.
# (u along the body, [(v deg around the body, 0 = top; size factor)]), mirrored in v. Front row starts just behind the
# face mask; the lowest spike of each row is smaller and placed between the legs.
_R = lambda pairs: sorted({(sg * v, f) for v, f in pairs for sg in (1, -1)})
ROWS = [(-0.82, _R([(30, 0.78)])), (-0.60, _R([(125, 0.85)])),
        (-0.24, _R([(0, 1.0), (40, 1.0), (80, 1.0), (120, 0.95), (152, 0.70)])),
        (0.24, _R([(20, 1.0), (60, 1.0), (100, 1.0)])), (0.10, _R([(132, 0.62)])),
        (0.70, _R([(0, 1.0), (44, 1.0), (88, 1.0), (122, 0.62)]))]
SPIKE_W = 0.050; SPIKE_L = 0.054; SPIKE_H = 0.030; SPIKE_TILT = 35.0     # base ~0.2 x body length, height 0.6 x base


# front-row centre spike rooted on the head at the hood line (front corner over the forehead = jagged border):
# x, y (world, after the head transform), size factor of the standard spike -> Spikes_Neck
HEAD_SPIKES = [(0.0, -0.072, 0.85)]


def row_group(u):
    return 'Spikes_Neck' if u < -0.5 else 'Spikes_Spine2' if u < 0.0 else 'Spikes_Spine1' if u < 0.5 else 'Spikes_Pelvis'


SPIKE_BONE = {'Spikes_Pelvis': 'Pelvis', 'Spikes_Spine1': 'Spine1', 'Spikes_Spine2': 'Spine2', 'Spikes_Neck': 'Neck1'}
SINK = 0.003
LEG_VIS = 0.035                   # leg faces below this height are visible (above it the leg is inside the shell)
# head rings along -Y: y, half width top, half width bottom (cheeks), z bottom, z top (12-gon, vertex on top)
HEAD_RINGS = [(-0.038, 0.030, 0.030, 0.036, 0.076), (-0.050, 0.046, 0.048, 0.025, 0.087),
              (-0.068, 0.053, 0.056, 0.020, 0.091), (-0.088, 0.051, 0.055, 0.021, 0.088),
              (-0.101, 0.042, 0.048, 0.025, 0.080), (-0.109, 0.031, 0.036, 0.029, 0.070),
              (-0.115, 0.018, 0.021, 0.036, 0.060)]
HEAD_EXP = 2.2
HEAD_N = 12
HOOD_FULL = {0: {0, 1, 2, 9, 10, 11}, 1: {0, 1, 10, 11}, 2: {0, 11}}    # head band -> brown hood faces k
HOOD_TEETH = {1: {2, 9}, 2: {1, 10}, 3: {0, 11}}       # zig-zag border: rear triangle brown (tooth pointing forward)
NECK = [Vector((0, -0.028, 0.062)), Vector((0, -0.043, 0.063)), Vector((0, -0.058, 0.064))]
EYE_AP = 0.0055
EYE_T = (0.026, -0.100, 0.068)
NOSE_Z = 0.048
EAR_C = Vector((0.043, -0.082, 0.073)); EAR_AX = Vector((0.35, -1.0, 0.10)); EAR_W = 0.0145; EAR_H = 0.032
EAR_TILT = 14.0                    # deg, tips splayed outwards
FRONT = (0.032, -0.058)
HIND = (0.037, 0.050)
LEG_TOP = 0.046
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_Q = Vector((0, -0.060, 0.020)); HEAD_S = Vector((1.18, 1.05, 1.10)); HEAD_MOVE = Vector((0, 0.012, 0))
PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Spikes_Pelvis', 'Spikes_Spine1', 'Spikes_Spine2', 'Spikes_Neck']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-04', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def head_ring(y, wt, wb, zb, zt, n=HEAD_N, p=HEAD_EXP):
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        w = wt if s > 1e-9 else (wb if s < -1e-9 else (wt + wb) / 2)
        out.append(Vector((w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
    return out


def core_s(u):
    pe = 5.0 if u < 0 else 2.2          # blunt full front: the shell meets the cheeks
    return max(0.0, 1 - abs(u) ** pe) ** (1 / pe)


def core_pt(u, v):
    s = core_s(u)
    return Vector((CORE_R[0] * s * spow(math.sin(v), 2 / CORE_Q), CORE_C.y + CORE_R[1] * u,
                   CORE_C.z + (CORE_R[2] if math.cos(v) > 0 else CORE_RZB) * s * spow(math.cos(v), 2 / CORE_Q)))


def core_frame(u, v):
    e = 1e-3
    p = core_pt(u, v)
    du = core_pt(min(u + e, 0.999), v) - core_pt(u - e, v)
    dv = core_pt(u, v + e) - core_pt(u, v - e)
    n = du.cross(dv).normalized()
    if n.dot(p - Vector((0, CORE_C.y, CORE_C.z))) < 0: n = -n
    return p, n


def centroid(r):
    return sum(r, Vector()) / len(r)


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Hedgehog'); self.pivot = {}; self.quads = []; self.spikes = []
        self.pl = self.P.bm.faces.layers.int.new('part')

    def _reg(self, name, faces, ground=False):
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        self.P.comp.append((name, faces, ground))

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False, mirror_diag=False):
        """cap: None | slot (flat n-gon) | ('apex', point, slot) (hidden cone into the neighbour part).
        col may return (slot of the rear triangle, slot of the front triangle). mirror_diag: quads on the first half
        of the ring split along the other diagonal, so the triangulation (and per-triangle colours) is X-symmetric."""
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                s = col(j, k) if callable(col) else col
                s1, s2 = s if isinstance(s, tuple) else (s, s)
                if mirror_diag and k < n // 2:
                    pair = [P.face([a, b, d], s1), P.face([b, c, d], s2)]
                else:
                    pair = [P.face([a, b, c], s1), P.face([a, c, d], s2)]
                faces += pair
                if s1 >= CREAM and s2 >= CREAM: self.quads.append(pair)
                else: self.quads += [[f] for f, sx in zip(pair, (s1, s2)) if sx >= CREAM]
        for cap, ring in ((cap0, list(reversed(R[0]))), (cap1, list(R[-1]))):
            if cap is None: continue
            if isinstance(cap, tuple):
                _, apex, s = cap; A = bm.verts.new(apex)
                for k in range(n):
                    f = P.face([ring[k], ring[(k + 1) % n], A], s); faces.append(f)
                    if s >= CREAM: self.quads.append([f])
            else:
                f = P.face(ring, cap); faces.append(f)
                if cap >= CREAM: self.quads.append([f])
        self._reg(name, faces, ground)
        return R

    def cone(self, name, ring, apex, slot):
        P = self.P; bm = P.bm
        R = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(R)
        faces = [P.face(R, slot)] + [P.face([R[(k + 1) % n], R[k], A], slot) for k in range(n)]
        self._reg(name, faces)

    def spike_on(self, name, bvh, p, n, t, h, ang, Lb, Wb):
        """broad 4-sided pyramid whose base corners are ray-projected onto the real (faceted) core/head surface and
        sunk SINK, so a wide base on a curved body has no floating edge; base split along F-B (non-planar)."""
        P = self.P; bm = P.bm
        s = n.cross(t).normalized()
        def on(q):
            hit = bvh.ray_cast(q + n * 0.05, -n)
            return (hit[0] if hit[0] is not None else q) - n * SINK
        d = (n * math.cos(ang) + t * math.sin(ang)).normalized()
        F = bm.verts.new(on(p - t * (0.55 * Lb))); B = bm.verts.new(on(p + t * (0.45 * Lb)))
        L = bm.verts.new(on(p - t * (0.05 * Lb) + s * (0.5 * Wb))); R = bm.verts.new(on(p - t * (0.05 * Lb) - s * (0.5 * Wb)))
        A = bm.verts.new(p + d * h)
        front = [P.face([F, L, A], SP_M), P.face([R, F, A], SP_M)]
        back = [P.face([L, B, A], SP_D), P.face([B, R, A], SP_D), P.face([F, R, B], SP_D), P.face([F, B, L], SP_D)]
        self._reg(name, front + back)
        self.spikes.append((name, front, back, A))

    def spike(self, name, p, n, t, h, ang, Lb, Wb):
        """thick 4-sided pyramid: diamond base sunk SINK below the core tangent plane, apex tilted ang from the normal
        towards t (back along the body). front (ridge) faces / back faces shaded later by their normals."""
        P = self.P; bm = P.bm
        s = n.cross(t).normalized()
        b0 = p - n * SINK
        d = (n * math.cos(ang) + t * math.sin(ang)).normalized()
        F = bm.verts.new(b0 - t * (0.55 * Lb)); B = bm.verts.new(b0 + t * (0.45 * Lb))
        L = bm.verts.new(b0 - t * (0.08 * Lb) + s * (0.5 * Wb)); R = bm.verts.new(b0 - t * (0.08 * Lb) - s * (0.5 * Wb))
        A = bm.verts.new(p + d * h)
        front = [P.face([F, L, A], SP_M), P.face([R, F, A], SP_M)]
        back = [P.face([L, B, A], SP_D), P.face([B, R, A], SP_D), P.face([F, R, B, L], SP_D)]
        self._reg(name, front + back)
        self.spikes.append((name, front, back, A))


def build_core(M):
    rings = [[core_pt(u, 2 * math.pi * k / CORE_N + math.pi / CORE_N) for k in range(CORE_N)] for u in CORE_U]
    D = 0.010
    Y = Vector((0, 1, 0))
    for part, (i0, i1) in SPLIT.items():
        rs = list(rings[i0:i1 + 1])
        c0 = BROWN if part == 'Spine2' else ('apex', centroid(rs[0]) - Y * D, BROWN)
        c1 = BROWN if part == 'Pelvis' else ('apex', centroid(rs[-1]) + Y * D, BROWN)
        M.loft(part, rs, BROWN, c0, c1)
    yz = lambda u: Vector((0, CORE_C.y + CORE_R[1] * u, CORE_C.z - 0.004))
    M.pivot['Pelvis'] = yz(0.48)
    M.pivot['Spine1'] = yz(CORE_U[5])
    M.pivot['Spine2'] = yz(CORE_U[3])


def build_spikes(M, bvh):
    """spike rows on the shell; centre point and normal from the parametric dome, then projected onto the facets"""
    count = 0; groups = {}
    for u, vf in ROWS:
        g = row_group(u)
        for v, f in vf:
            p, n = core_frame(u, math.radians(v))
            hit = bvh.ray_cast(p + n * 0.05, -n)
            if hit[0] is not None: p = hit[0]
            if v == 0: p.x = 0.0
            r = Vector((0, 1, -0.2)); t = (r - n * r.dot(n)).normalized()
            k = f
            M.spike_on(g, bvh, p, n, t, SPIKE_H * k, math.radians(SPIKE_TILT), SPIKE_L * k, SPIKE_W * k); count += 1
            groups[g] = groups.get(g, 0) + 1
    return count, groups


def build_head_spikes(M, head_faces):
    """hood-edge spikes rooted in the (transformed) head top between the ears; their front corner overlaps the
    forehead edge so the face/spine border is jagged"""
    bvh = head_bvh(head_faces); n_ = 0
    sh = [f for nm, faces, _ in M.P.comp if nm in ('Pelvis', 'Spine1', 'Spine2') for f in faces]
    bvh_all = head_bvh(list(head_faces) + sh)
    for x, y, f in HEAD_SPIKES:
        for xx in ((x,) if x == 0 else (x, -x)):
            hit = bvh.ray_cast(Vector((xx, y, 0.3)), Vector((0, 0, -1)))
            if hit[0] is None: raise RuntimeError(f'no head hit for the hood spike at {xx, y}')
            p, n = hit[0], (hit[1] if hit[1].z > 0 else -hit[1])
            if xx == 0: p.x = 0.0; n = Vector((0.0, n.y, n.z)).normalized()    # centre: symmetric frame
            r = Vector((0, 1, -0.2)); t = (r - n * r.dot(n)).normalized()
            M.spike_on('Spikes_Neck', bvh_all, p, n, t, SPIKE_H * f, math.radians(SPIKE_TILT), SPIKE_L * f, SPIKE_W * f); n_ += 1
    M.spike_groups['Spikes_Neck'] = M.spike_groups.get('Spikes_Neck', 0) + n_
    M.n_spikes += n_


def build_neck(M):
    def ring(c, t, r):
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 3, math.pi / 2)
    t1 = (NECK[1] - NECK[0]).normalized(); t2 = (NECK[2] - NECK[1]).normalized()
    M.loft('Neck1', [ring(NECK[0], t1, 0.010), ring(NECK[1] + t1 * 0.003, t1, 0.0095)], BROWN, BROWN, BROWN)
    M.loft('Neck2', [ring(NECK[1] - t2 * 0.003, t2, 0.0095), ring(NECK[2], t2, 0.009)], BROWN, BROWN, BROWN)
    M.pivot['Neck1'] = NECK[0].copy(); M.pivot['Neck2'] = NECK[1].copy()


def build_head(M):
    rings = [head_ring(*r) for r in HEAD_RINGS]
    def col(j, k):
        if k in HOOD_FULL.get(j, ()): return CORE
        if k in HOOD_TEETH.get(j, ()): return (CORE, CREAM)
        return CREAM
    M.loft('Head', rings, col, CORE, CREAM, mirror_diag=True)
    M.pivot['Head'] = NECK[2].copy()
    return list(M.P.comp[-1][1])


def head_bvh(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: id(v)); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d):
    d = Vector(d).normalized(); o = Vector(target) - d * 0.1
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no head hit at {target}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n


def build_face(M, head_faces):
    bvh = head_bvh(head_faces)
    # eyes: dark-brown 8-gon discs, 1.5 mm proud, looking forward and a little out
    hp, n = surf(bvh, EYE_T, (-0.30, 0.95, 0.0))
    ax = (n + Vector((0.0, -0.5, 0.0))).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.0015, e1, e2, EYE_AP, 8), c - a * 0.005, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: round faceted 8-gon dome on the muzzle tip
    ty = HEAD_RINGS[-1][0]
    X = Vector((1, 0, 0)); Z = Vector((0, 0, 1))
    nring = lambda y, w, h, dz=0.0: ngon_ring(Vector((0, y, NOSE_Z + dz)), X, Z, w, 8, math.pi / 8, h / w)
    M.loft('Nose', [nring(ty + 0.008, 0.0070, 0.0052), nring(ty - 0.0028, 0.0086, 0.0066),
                    nring(ty - 0.0072, 0.0056, 0.0042, 0.0004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = Vector((0, ty + 0.004, NOSE_Z))
    # ears: rounded-triangle plates (cream back + rim, darker inner facet), base sunk into the head
    a = EAR_AX.normalized()
    _, e1, e2 = pc.basis(a, (0, 0, 1))               # e1 ~ up in the ear plane, e2 sideways
    tl = math.radians(EAR_TILT)
    up = (e1 * math.cos(tl) + e2 * math.sin(tl) * (1 if e2.x > 0 else -1)).normalized()
    sd = a.cross(up).normalized()
    prof = [(-1.0, 0.0), (1.0, 0.0), (0.95, 0.55), (0.42, 1.0), (-0.42, 1.0), (-0.95, 0.55)]
    def ring(off, sc, lift=0.0):
        return [EAR_C + a * off + sd * (x * EAR_W * sc) + up * (lift + z * EAR_H * sc) for x, z in prof]
    rings = [ring(-0.0045, 1.0), ring(0.0035, 0.97), ring(0.0025, 0.56, 0.016)]
    cols = {0: CREAM, 1: CR_L}
    piv = EAR_C + up * 0.012
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k: cols[j], CREAM, EAR_IN)
        M.pivot['Ear' + sfx] = piv.copy() if sx > 0 else mir(piv)
    # jaw: hidden chin block inside the head (connector for the Jaw bone)
    jr = [(-0.070, 0.012, 0.028, 0.040), (-0.108, 0.006, 0.034, 0.046)]     # front end anchored in the nose root
    M.loft('Jaw', [ngon_ring(Vector((0, y, (lo + hi) / 2)), X, Z, wd * 0.6, 3, math.pi / 2, (hi - lo) / (2 * wd))
                   for y, wd, lo, hi in jr], CREAM, CREAM, CREAM)
    M.pivot['Jaw'] = Vector((0, -0.068, 0.036))
    return bvh


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (lx, ly) in (('Front', FRONT), ('Hind', HIND)):
            x = lx * sx
            ring = lambda z, r, n, ph, dy=0.0: ngon_ring(Vector((x, ly + dy, z)), X, Y, r, n, ph)
            M.loft(kind + 'Upper' + sfx, [ring(LEG_TOP + 0.010, 0.005, 3, math.pi / 2), ring(LEG_TOP - 0.010, 0.005, 3, math.pi / 2)],
                   BROWN, BROWN, BROWN)
            M.loft(kind + 'Lower' + sfx, [ring(LEG_TOP, 0.0150, 8, math.pi / 8), ring(0.008, 0.0140, 8, math.pi / 8)],
                   CREAM, CREAM, CREAM)
            # flat foot: starts inside the leg, flares at the ankle, sole forward a little, bottom on z = 0
            M.loft(kind + 'Foot' + sfx, [ring(0.015, 0.0122, 8, math.pi / 8), ring(0.008, 0.0148, 8, math.pi / 8, -0.001),
                                         ring(0.0025, 0.0165, 8, math.pi / 8, -0.003), ring(0.0, 0.0158, 8, math.pi / 8, -0.003)],
                   CREAM, CREAM, SOLE, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, ly, LEG_TOP + 0.006))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, ly, LEG_TOP - 0.006))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, ly, 0.010))


def shade(M):
    """placeholder faces get a tone by the quad's outward normal (large-scale tonal shift, no noise); spikes: front
    faces light when facing up, mid otherwise, back faces dark"""
    sl = M.P.slot
    for grp in M.quads:
        n = sum((f.normal for f in grp), Vector()).normalized()
        if grp[0][sl] == BROWN:
            s = CR_D if n.z < -0.85 else CORE
        else:
            if n.z < -0.45: s = CR_D
            elif n.z > 0.55 or n.y < -0.55: s = CR_L
            else: s = CR_M
        for f in grp: f[sl] = s
    for name, front, back, A in M.spikes:
        for f in front: f[sl] = SP_L if f.normal.z > 0.45 else SP_M
    left = [f for f in M.P.bm.faces if f[sl] >= CREAM]
    if left: raise RuntimeError(f'{len(left)} unresolved placeholder faces')


# ---------------- assemble ----------------
def com_of(bm):
    vol = 0.0; acc = Vector()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]; v = a.dot(b.cross(c)) / 6.0
            vol += v; acc += v * (a + b + c) / 4.0
    return acc / vol, vol


def prune_spikes(M):
    """drop spikes that cut an ear, or the visible leg below the shell (z < LEG_VIS); geometry is X-symmetric, so the drops are
    symmetric too. Returns the number dropped."""
    bm = M.P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    tree = lambda fs: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs])
    comp = {}
    for nm, faces, _ in M.P.comp: comp.setdefault(nm, []).extend(faces)
    ears = tree(comp['Ear.L'] + comp['Ear.R'])
    legs = tree([f for nm in comp if 'Lower' in nm or 'Foot' in nm for f in comp[nm] if f.calc_center_median().z < LEG_VIS])
    drop = []
    for sp in M.spikes:
        fs = sp[1] + sp[2]; t = tree(fs)
        if t.overlap(ears) or t.overlap(legs): drop.append(sp)
    print('  pruned spikes at', [tuple(round(c, 3) for c in sp[3].co) for sp in drop])
    for sp in drop:
        fs = sp[1] + sp[2]; vs = list({v for f in fs for v in f.verts})
        M.P.comp = [c for c in M.P.comp if c[1][0] is not fs[0]]
        M.spikes.remove(sp)
        M.spike_groups[sp[0]] -= 1; M.n_spikes -= 1
        bmesh.ops.delete(bm, geom=vs, context='VERTS')
    return len(drop)


def face_intrusions(M):
    """spike triangles that cut the face (cream head faces looking forward, n.y < -0.6), the eyes, the nose or the
    ears; also spike/leg cuts (reported). Returns {'face': n, 'ears': n, 'legs': n} (overlapping triangle pairs)."""
    bm = M.P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]; sl = M.P.slot
    tree = lambda fs: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs])
    comp = {}
    for nm, faces, _ in M.P.comp: comp.setdefault(nm, []).extend(faces)
    sp = tree([f for _, fr, bk, _ in M.spikes for f in fr + bk])
    face = [f for f in comp['Head'] if f[sl] != CORE and f.normal.y < -0.6] + comp['Eye.L'] + comp['Eye.R'] + comp['Nose']
    ears = comp['Ear.L'] + comp['Ear.R']
    legs = [f for nm in comp if 'Lower' in nm or 'Foot' in nm for f in comp[nm] if f.calc_center_median().z < LEG_VIS]
    return {k: len(sp.overlap(tree(fs))) for k, fs in (('face', face), ('ears', ears), ('legs', legs))}


def build_model():
    M = Model()
    build_core(M)
    build_neck(M)
    hf = build_head(M); bvh = build_face(M, hf)
    build_legs(M)
    bm = M.P.bm
    hx = lambda c: HEAD_Q + Vector([a * b for a, b in zip(c - HEAD_Q, HEAD_S)]) + HEAD_MOVE
    for nm, faces, _ in M.P.comp:
        if nm in HEAD_GROUP:
            for v in {v for f in faces for v in f.verts}: v.co = hx(v.co)
    for k in HEAD_GROUP[1:]: M.pivot[k] = hx(M.pivot[k])        # Head pivot stays on the neck joint
    shell = [f for nm, faces, _ in M.P.comp if nm in ('Pelvis', 'Spine1', 'Spine2', 'Head') for f in faces]
    M.n_spikes, M.spike_groups = build_spikes(M, head_bvh(shell))
    build_head_spikes(M, hf)
    M.pruned = prune_spikes(M)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    shade(M)
    M.cuts = face_intrusions(M); M.intrusions = M.cuts['face'] + M.cuts['ears']
    com, vol = com_of(bm)
    shift = Vector((0, -com.y, 0))
    for v in bm.verts: v.co += shift
    for k in list(M.pivot): M.pivot[k] = M.pivot[k] + shift
    for g, b in SPIKE_BONE.items(): M.pivot[g] = M.pivot[b].copy()
    M.com = com + shift; M.vol = vol; M.shift = shift
    return M


def objects(M, coll, mat):
    P = M.P; bm = P.bm
    names = [c[0] for c in P.comp]
    missing = set(PART_ORDER) - set(names); extra = set(names) - set(PART_ORDER)
    if missing or extra: raise RuntimeError(f'parts missing {missing} extra {extra}')
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.05
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


def coplanar_all(M, coll, scale=1.0):
    b2 = M.P.bm.copy()
    bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3])
    for v in b2.verts: v.co *= scale
    me = bpy.data.meshes.new('TMP_All'); b2.to_mesh(me); b2.free()
    ob = bpy.data.objects.new('TMP_All', me); coll.objects.link(ob)
    n, s = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def coplanar_true(M, eps=1e-5, pen=2e-7):
    """small-model coplanar test (from the Mouse): triangles in one plane (|d| < 0.01 mm) that really overlap in 2D (SAT)"""
    b2 = M.P.bm.copy()
    bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3])
    b2.faces.ensure_lookup_table(); b2.normal_update()
    tree = BVHTree.FromBMesh(b2); bad = set()
    tris = [[v.co.copy() for v in f.verts] for f in b2.faces]

    def sat(A, B, n):
        _, u, w = pc.basis(n, (1, 0, 0) if abs(n.x) < 0.9 else (0, 1, 0))
        a = [(p.dot(u), p.dot(w)) for p in A]; b = [(p.dot(u), p.dot(w)) for p in B]
        for poly in (a, b):
            for i in range(3):
                (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % 3]
                ax, ay = y1 - y0, x0 - x1; ln = math.hypot(ax, ay)
                if ln < 1e-12: return False
                pa = [(x * ax + y * ay) / ln for x, y in a]; pb = [(x * ax + y * ay) / ln for x, y in b]
                if min(max(pa), max(pb)) - max(min(pa), min(pb)) < pen: return False
        return True
    for f in b2.faces:
        if f.calc_area() < 1e-12: continue
        c = f.calc_center_median(); n = f.normal; rr = max((v.co - c).length for v in f.verts)
        for co, nn, idx, d in tree.find_nearest_range(c, rr * 1.01):
            if idx is None or idx <= f.index: continue
            g = b2.faces[idx]
            if abs(abs(g.normal.dot(n)) - 1) > 1e-4 or abs((g.calc_center_median() - c).dot(n)) > eps: continue
            if sat(tris[f.index], tris[idx], n): bad.add((f.index, idx))
    pl2 = b2.faces.layers.int['part']
    names = [(PART_ORDER[b2.faces[a][pl2]], PART_ORDER[b2.faces[b][pl2]], tuple(round(c, 4) for c in b2.faces[a].calc_center_median()))
             for a, b in sorted(bad)[:6]]
    b2.free()
    print(f'  coplanar_true (plane < {eps*1000:.2f} mm, real 2D overlap): {len(bad)} pairs', names)
    return len(bad)


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    chk = pc.comp_checks(M.P)
    cop = coplanar_all(M, coll)
    cop10 = coplanar_all(M, coll, 10.0)
    copt = coplanar_true(M)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root, obs = objects(M, coll, mat)
    bpy.context.view_layer.update()
    print('TRIS per part:')
    tot = 0
    for nm in PART_ORDER:
        t = len(obs[nm].data.polygons); tot += t
        print(f'   {nm:14s} {t:4d}  pivot {tuple(round(c, 4) for c in obs[nm].location)}')
    print(f'TRIS total {tot} | target ~{TARGET} ({100.0 * (tot - TARGET) / TARGET:+.1f}%), limit {LIMIT}')
    print(f'SPIKES {M.n_spikes} (pruned {M.pruned}) groups {M.spike_groups} | spike cuts (tri pairs) face/eyes/nose {M.cuts["face"]} '
          f'ears {M.cuts["ears"]} legs {M.cuts["legs"]}')
    W = lambda names: [o.matrix_world @ v.co for o in (obs[n] for n in names) for v in o.data.vertices]
    pts = W(PART_ORDER)
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    hd = W(('Head',)); sp = W(('Spikes_Pelvis', 'Spikes_Spine1', 'Spikes_Spine2', 'Spikes_Neck'))
    print(f'SIZE width x {hi[0]-lo[0]:.4f} length y {hi[1]-lo[1]:.4f} height z {hi[2]-lo[2]:.4f} | y {lo[1]:.4f}..{hi[1]:.4f} '
          f'min z {lo[2]:.5f} | spikes top {max(p.z for p in sp):.4f} width {2*max(p.x for p in sp):.4f} rear {max(p.y for p in sp):.4f} '
          f'lowest spike z {min(p.z for p in sp):.4f}')
    print(f'HEAD w {max(p.x for p in hd) * 2:.4f} z {min(p.z for p in hd):.4f}..{max(p.z for p in hd):.4f} front y {min(p.y for p in hd):.4f} '
          f'| ear top {max(p.z for p in W(("Ear.L",))):.4f} | nose front y {min(p.y for p in W(("Nose",))):.4f} '
          f'| belly (core min z) {min(p.z for p in W(("Pelvis", "Spine1", "Spine2"))):.4f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1e6:.1f} cm3 | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"]} coplanar(shared) {cop} coplanar_x10 {cop10} '
          f'coplanar_true {copt} face intrusions {M.intrusions} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop + cop10 + copt,
                intrusions=M.intrusions, total=tot, size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.5, 1, 0.30), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Hedgehog_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B, views, tag='look'):
    """EEVEE preview-style frames composed into one sheet (each tile 400 px high) + a 128 px thumbnail of the first"""
    tiles = []
    for i, (nm, v, fill) in enumerate(views):
        p = os.path.join(CHECK, f'look_{i}.png')
        rn.preview(B['sc'], list(B['obs'].values()), p, view=v, fill=fill)
        a = rn.load_px(p); tiles.append(rn.resize(a, 400))
        if i == 0:
            t = rn.resize(a, 80); img = bpy.data.images.new('TMP_Thumb', t.shape[1], t.shape[0], alpha=True)
            img.pixels.foreach_set(t.ravel()); img.filepath_raw = os.path.join(CHECK, f'Hedgehog_{tag}_128.png')
            img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
        os.remove(p)
    rn.compose([rn.ref_tile(REF, 400)] + tiles, 3, os.path.join(CHECK, f'Hedgehog_{tag}_sheet.png'))


LOOK_VIEWS = (('ref', REF_VIEW, (0.62, 0.78)), ('prev', PREVIEW_VIEW, PREVIEW_FILL), ('side', (1, 0.0, 0.10), (0.75, 0.75)),
              ('front', (0.0, -1, 0.15), (0.6, 0.8)), ('back', (-0.5, 1.0, 0.35), (0.7, 0.8)), ('top', (0.2, -0.25, 1.0), (0.7, 0.8)))

if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-04 Hedgehog', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B, LOOK_VIEWS)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        bad = B['checks']['nonmanifold'] or B['checks']['loose'] or B['checks']['degenerate'] or B['coplanar'] \
            or B['checks']['problems'] or abs(B['minz']) > 1e-6 or B['intrusions'] or B['checks']['mirror'] > 1e-5
        if bad: raise RuntimeError('checks failed - not exporting')
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
