# build_rabbit.py - SML-01 Rabbit (Farm Animals, skeleton Q-S), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_rabbit.py -- SML-01 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_rabbit)
# look  : EEVEE frames (reference angle, side, front, back, top) into the check folder
# export: build + FBX (root empty + one mesh per skeleton part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Cat/Cow).
# Helpers copied from ../Cat/build_cat.py (Model/loft/tuck/ray-cast/objects); shared modules imported read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Rabbit'
TAG = 'FarmAnimals_Rabbit'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\SML-01.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_rabbit')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -1.10, 0.40)         # SML-01 reference: left side from the front-left, ~20 deg above
PREVIEW_VIEW = (1.0, -1.20, 0.34)     # preview: reference side, ~15 deg above (sky band as the other pack previews)
TARGET = 800
LIMIT = 1100          # coordinator rework: up to ~1100 tris

PALETTE = ['#F8F5F2', '#EEE7E1', '#F4F0EE', '#EEE7E1',     # 0 top, 1 side, 2 front, 3 rear (= side): warm whites
           '#DFD0C7', '#F2A6B0', '#EE9AA7', '#2A1D17',     # 4 under (warm grey-pink), 5 ear pink, 6 nose, 7 eye
           '#C4949B', '#B5835A', '#7A5233', '#6E9F4A',     # 8 mouth line, 9-15 series spares
           '#8E959B', '#C8473B', '#F2E6C9', '#D8B65A']
W_TOP, W_SIDE, W_FRONT, W_BACK, W_UNDER, EAR_PINK, NOSE, EYE, MOUTH = range(9)
WHITE = 100            # placeholder slot: resolved per quad by its normal (shade pass)

# ---------------- layout (before the centre-of-mass shift) ----------------
# body profile: y, half width, z bottom, z top  (chest front -Y .. rump +Y)
BODY_PROF = [(-0.145, 0.064, 0.112, 0.228), (-0.126, 0.098, 0.082, 0.264), (-0.090, 0.114, 0.068, 0.282),
             (-0.045, 0.120, 0.064, 0.290), (0.035, 0.126, 0.066, 0.298), (0.080, 0.128, 0.070, 0.304),
             (0.115, 0.118, 0.082, 0.300), (0.140, 0.092, 0.104, 0.282), (0.155, 0.050, 0.146, 0.248)]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 4), 'Pelvis': (4, 8)}
# head rings along -Y: y, half width top, half width bottom (cheeks), z bottom, z top
HEAD_RINGS = [(-0.070, 0.055, 0.060, 0.272, 0.382), (-0.090, 0.086, 0.096, 0.240, 0.410),
              (-0.128, 0.098, 0.114, 0.226, 0.418), (-0.170, 0.088, 0.110, 0.228, 0.405),
              (-0.203, 0.060, 0.084, 0.240, 0.374), (-0.222, 0.032, 0.050, 0.262, 0.342)]
NECK = [Vector((0, -0.068, 0.225)), Vector((0, -0.086, 0.262)), Vector((0, -0.100, 0.300))]
FRONT = (0.068, -0.070)
HIND = (0.086, 0.066)          # haunch centre x/y (HindUpper), foot under it
HAUNCH_Z = 0.145
TAIL_AIM = Vector((0, 0.150, 0.250)); TAIL_AX = Vector((0, 0.82, 0.57)).normalized(); TAIL_R = 0.066
EYE_R = 0.0126                 # eye 10-gon apothem before the head scale
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.52              # big baby head: scaled about a point behind the crown -> grows down and forward
HEAD_Q = Vector((0, -0.120, 0.384))
PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R', 'Tail1']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-01', 'build'])[:2]


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


def body_ring(yk, n=10, pt=2.0, pb=2.0):
    w, zb, zt = lerp_tab(BODY_PROF, yk)
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(Vector((w * spow(c, 2 / p), yk, zc + h * spow(s, 2 / p))))
    return out


def head_ring(y, wt, wb, zb, zt, n=10, pt=2.2, pb=2.2):
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb; w = wt if s >= 0 else wb
        if abs(s) < 1e-9: w = (wt + wb) / 2
        out.append(Vector((w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.965, depth=0.02):
    """child's proximal end: boundary ring replaced by a slightly smaller ring hidden `depth` inside the parent"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    return [c + (p - c) * scale + ab * depth for p in ring]


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Rabbit'); self.pivot = {}; self.quads = []
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
                s = col(j, k) if callable(col) else col
                pair = [P.face([a, b, c], s), P.face([a, c, d], s)]
                faces += pair
                if s == WHITE: self.quads.append(pair)
        for cap, ring in ((cap0, list(reversed(R[0]))), (cap1, list(R[-1]))):
            if cap is not None:
                f = P.face(ring, cap); faces.append(f)
                if cap == WHITE: self.quads.append([f])
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R

    def cone(self, name, ring, apex, slot):
        # flat n-gon face + apex hidden inside the head (n + n-2 tris)
        P = self.P; bm = P.bm
        R = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(R)
        faces = [P.face(R, slot)] + [P.face([R[(k + 1) % n], R[k], A], slot) for k in range(n)]
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, False))


def build_body(M):
    rings = [body_ring(p[0]) for p in BODY_PROF]
    for part, (i0, i1) in SPLIT.items():
        # joint rings shared exactly by both parts (one continuous outer surface, no seam line); each part continues
        # past the joint with one hidden band turning inwards = overlap that keeps a bend closed
        rs = list(rings[i0:i1 + 1])
        if part != 'Pelvis': rs = rs + [tuck(rings[i1], (0, 1, 0), 0.80, 0.026)]
        if part != 'Spine2': rs = [tuck(rings[i0], (0, -1, 0), 0.80, 0.026)] + rs
        M.loft(part, rs, WHITE, WHITE, WHITE)
    M.pivot['Pelvis'] = Vector((0, BODY_PROF[4][0] + 0.05, 0.19))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[3][0], 0.19))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[1][0] + 0.02, 0.19))


def build_neck(M):
    X = Vector((1, 0, 0))
    def ring(c, t, r):
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 4, 0.0)
    t1 = (NECK[1] - NECK[0]).normalized(); t2 = (NECK[2] - NECK[1]).normalized()
    M.loft('Neck1', [ring(NECK[0], t1, 0.050), ring(NECK[1], t1, 0.048)], WHITE, WHITE, WHITE)
    M.loft('Neck2', [ring(NECK[1] - t2 * 0.012, t2, 0.044), ring(NECK[2], t2, 0.042)], WHITE, WHITE, WHITE)
    M.pivot['Neck1'] = NECK[0].copy(); M.pivot['Neck2'] = NECK[1].copy()


def build_head(M):
    rings = [head_ring(*r) for r in HEAD_RINGS]
    M.loft('Head', rings, WHITE, WHITE, WHITE)
    M.pivot['Head'] = HEAD_Q + (NECK[2] - HEAD_Q) / HEAD_SCALE   # lands on the Neck2 end after the scale
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


def mir(p):
    return Vector((-p.x, p.y, p.z))


def build_face(M, head_faces):
    bvh = head_bvh(head_faces)
    # eyes: dark 8-gon discs, 3 mm proud, looking forward and a little out
    hp, n = surf(bvh, (0.061, -0.186, 0.350), (-0.42, 0.91, 0.0))
    ax = (n + Vector((0.0, -0.25, 0.0))).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.0025, e1, e2, EYE_R, 10), c - a * 0.008, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: pink inverted triangle on the muzzle front
    hp, n = surf(bvh, (0, -0.23, 0.318), (0, 1, 0))
    up = Vector((0, 0, 1)); up = (up - n * up.dot(n)).normalized(); side = Vector((1, 0, 0))
    tri = [Vector((0.016, 0, 0.006)), Vector((-0.016, 0, 0.006)), Vector((0, 0, -0.012))]
    ring = lambda off: [hp + n * off + side * p.x + up * p.z for p in tri]
    M.loft('Nose', [ring(-0.008), ring(0.004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # mouth line: thin grey-pink strip from the nose tip down the muzzle front (ray-cast ends, 1.5 mm proud)
    p0 = hp + up * (-0.009)
    p1, n1 = surf(bvh, (0, -0.25, hp.z - 0.030), (0, 1, 0.25))
    def mring(p, nn):
        return [p + side * 0.0024 + nn * 0.0015, p - side * 0.0024 + nn * 0.0015, p - side * 0.0024 - nn * 0.005,
                p + side * 0.0024 - nn * 0.005]
    M.loft('Nose', [mring(p0, n), mring(p1, n1)], MOUTH, MOUTH, MOUTH)
    # ears: long thick blades, pink inner dish with a white rim, roots sunk into the skull, slight V
    hp, n = surf(bvh, (0.038, -0.122, 0.40), (0, 0, -1))
    u = Vector((0.30, 0.08, 1.0)).normalized()
    f = Vector((0.30, -1.0, 0.0)); f = (f - u * f.dot(u)).normalized()
    s = u.cross(f).normalized()                                  # outer side (+X for the left ear)
    w = 0.040
    prof = [(w, -0.008), (0.76 * w, 0.010), (0.0, 0.001), (-0.76 * w, 0.010), (-w, -0.008), (0.0, -0.023)]
    base = hp - u * 0.016
    st = [(0.0, 0.64, 0.85), (0.050, 1.0, 1.0), (0.095, 0.92, 0.92), (0.122, 0.62, 0.75), (0.137, 0.22, 0.50)]
    rings = [[base + u * h + s * (a * sw) + f * (b * stt) for a, b in prof] for h, sw, stt in st]
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k: EAR_PINK if k in (1, 2) else WHITE, WHITE, WHITE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # jaw: small white chin block under the muzzle (a few mm proud of the head bottom)
    X = Vector((1, 0, 0)); Z = Vector((0, 0, 1))
    jr = [(-0.150, 0.034, 0.224, 0.272), (-0.204, 0.030, 0.254, 0.282)]
    M.loft('Jaw', [ngon_ring(Vector((0, y, (a + b) / 2)), X, Z, wd, 4, math.pi / 4, (b - a) / (2 * wd)) for y, wd, a, b in jr],
           WHITE, WHITE, WHITE)
    M.pivot['Jaw'] = Vector((0, -0.160, 0.272))


def foot_rings(x, y0, y1, w, h, st):
    """rounded wedge paw along Y: 6-vertex section with a flat bottom at z = 0 and a domed top; st = [(t, sw, sh)]
    from the heel (t = 0, at y1) to the toe (t = 1, at y0): low rounded heel, high instep, tapering rounded toe"""
    def sec(y, sw, sh):
        a, b = w * sw, h * sh
        return [Vector((x + px, y, pz)) for px, pz in ((-a, 0.0), (a, 0.0), (a, 0.48 * b), (0.50 * a, b), (-0.50 * a, b), (-a, 0.48 * b))]
    return [sec(y1 + (y0 - y1) * t, sw, sh) for t, sw, sh in st]


FRONT_PAW = [(0.0, 0.76, 0.68), (0.25, 1.0, 1.0), (0.80, 0.92, 0.66), (1.0, 0.58, 0.32)]
HIND_PAW = [(0.0, 0.76, 0.70), (0.20, 1.0, 1.0), (0.52, 0.97, 0.76), (0.86, 0.88, 0.52), (1.0, 0.56, 0.28)]


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        # front: shoulder column sunk into the chest, short lower leg, short foot
        x, y = FRONT[0] * sx, FRONT[1]
        ring = lambda z, r, dy=0.0, dx=0.0: ngon_ring(Vector((x - dx * sx, y + dy, z)), X, Y, r, 6, 0.0)
        M.loft('FrontUpper' + sfx, [ring(0.172, 0.033, 0.0, 0.014), ring(0.066, 0.048)], WHITE, WHITE, WHITE)
        M.loft('FrontLower' + sfx, [ring(0.074, 0.044, -0.002), ring(0.018, 0.044, -0.004)], WHITE, WHITE, WHITE)
        M.loft('FrontFoot' + sfx, foot_rings(x, y - 0.062, y + 0.038, 0.054, 0.052, FRONT_PAW), WHITE, WHITE, WHITE, ground=True)
        M.pivot['FrontUpper' + sfx] = Vector((x, y, 0.180))
        M.pivot['FrontLower' + sfx] = Vector((x, y, 0.078))
        M.pivot['FrontFoot' + sfx] = Vector((x, y - 0.004, 0.025))
        # hind: haunch disc on the flank (HindUpper), short shin, long flat foot
        hx, hy = HIND[0] * sx, HIND[1]
        # thigh column: top ring inside the pelvis, haunch ring bulging out of the lower flank (elongated in Y),
        # bottom ring just wider than the shin -> one tapering form from the rump to the paw, no dome edge
        hr = lambda xx, yy, z, r, sy: ngon_ring(Vector((xx * sx, hy + yy, z)), X, Y, r, 8, math.pi / 8, sy)
        M.loft('HindUpper' + sfx, [hr(0.058, -0.012, 0.205, 0.062, 1.00), hr(0.080, -0.012, 0.138, 0.064, 1.00),
                                   hr(0.088, 0.008, 0.074, 0.048, 1.05)], WHITE, WHITE, WHITE)
        lx = 0.088 * sx
        lr = lambda z, r, dy: ngon_ring(Vector((lx, hy + dy, z)), X, Y, r, 6, 0.0)
        M.loft('HindLower' + sfx, [lr(0.090, 0.045, 0.008), lr(0.020, 0.044, 0.010)], WHITE, WHITE, WHITE)
        M.loft('HindFoot' + sfx, foot_rings(lx, hy - 0.095, hy + 0.065, 0.054, 0.056, HIND_PAW), WHITE, WHITE, WHITE, ground=True)
        M.pivot['HindUpper' + sfx] = Vector((0.064 * sx, hy, 0.185))
        M.pivot['HindLower' + sfx] = Vector((lx, hy + 0.008, 0.082))
        M.pivot['HindFoot' + sfx] = Vector((lx, hy + 0.010, 0.025))


def build_tail(M):
    pel = [f for nm, faces, _ in M.P.comp if nm == 'Pelvis' for f in faces]
    hit, _ = surf(head_bvh(pel), TAIL_AIM + TAIL_AX * 0.05, -TAIL_AX)       # rump surface along the tail axis
    c = hit + TAIL_AX * (TAIL_R - 0.30 * 2 * TAIL_R)                       # 30% of the diameter inside the rump
    tb = bmesh.new()
    bmesh.ops.create_icosphere(tb, subdivisions=2, radius=TAIL_R)          # 80 tris (icosahedron + 1 subdivision)
    # spin about Z to the orientation that is exactly X-symmetric (rabbit mirror check)
    from mathutils import Matrix
    def mir_err(m):
        ps = [m @ v.co for v in tb.verts]
        return max(min((q - Vector((-p.x, p.y, p.z))).length for q in ps) for p in ps)
    best = min((mir_err(Matrix.Rotation(math.pi * k / 20, 3, 'Z')), k) for k in range(20))
    bmesh.ops.rotate(tb, verts=tb.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi * best[1] / 20, 3, 'Z'))
    print(f'  tail icosphere spin {best[1] * 9} deg, mirror {best[0]:.6f}')
    P = M.P; vm = {v: P.bm.verts.new(c + v.co) for v in tb.verts}
    faces = []
    for f in tb.faces:
        nf = P.face([vm[v] for v in f.verts], WHITE); nf[M.pl] = PART_ORDER.index('Tail1')
        faces.append(nf); M.quads.append([nf])
    tb.free()
    P.comp.append(('Tail1', faces, False))
    M.pivot['Tail1'] = hit.copy()
    M.tail_c = c


def shade(M):
    """white faces get one of 4 warm-white tones by the quad's outward normal (large-scale tonal shift, no noise)"""
    sl = M.P.slot
    for grp in M.quads:
        n = sum((f.normal for f in grp), Vector()).normalized()
        if n.z > 0.62: s = W_TOP
        elif n.z < -0.50: s = W_UNDER
        elif n.y < -0.40: s = W_FRONT
        elif n.y > 0.40: s = W_BACK
        else: s = W_SIDE
        for f in grp: f[sl] = s
    dbg = os.environ.get('RABBIT_DBG')          # check renders only: tint the named parts pink to locate a defect
    if dbg:
        ids = {PART_ORDER.index(n) for n in dbg.split(',')}
        for f in M.P.bm.faces:
            if f[M.pl] in ids: f[sl] = EAR_PINK
    left = [f for f in M.P.bm.faces if f[sl] == WHITE]
    if left: raise RuntimeError(f'{len(left)} unresolved white faces')


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
    shade(M)
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
    print(f'TRIS total {tot} | target ~{TARGET} ({100.0 * (tot - TARGET) / TARGET:+.1f}%), rework limit {LIMIT}')
    W = lambda names: [o.matrix_world @ v.co for o in (obs[n] for n in names) for v in o.data.vertices]
    pts = W(PART_ORDER)
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = W(('Pelvis', 'Spine1', 'Spine2', 'Head', 'Nose'))
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} back top '
          f'{max(p.z for p in W(("Pelvis", "Spine1"))):.3f} head top {max(p.z for p in W(("Head",))):.3f} '
          f'belly {min(p.z for p in W(("Spine1",))):.3f} body width {max(p.x for p in W(("Pelvis",))) * 2:.3f} '
          f'haunch width {max(p.x for p in W(("HindUpper.L",))) * 2:.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.2f} L | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} coplanar {cop} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.02, 1, 0.20), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Rabbit_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Rabbit_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B, views):
    for nm, v in views:
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, f'Rabbit_look_{nm}.png'), view=v, fill=(0.62, 0.78))


if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-01 Rabbit', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B, (('ref', REF_VIEW), ('side', (1, 0.0, 0.1)), ('front', (0.05, -1, 0.15)), ('back', (-0.5, 1.0, 0.35)),
                 ('top', (0.2, -0.25, 1.0))))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        bad = B['checks']['nonmanifold'] or B['checks']['loose'] or B['checks']['degenerate'] or B['coplanar'] \
            or B['checks']['problems'] or abs(B['minz']) > 1e-6
        if bad: raise RuntimeError('checks failed - not exporting')
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
