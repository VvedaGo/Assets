# build_mouse.py - SML-03 Mouse (Farm Animals, skeleton Q-S), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_mouse.py -- SML-03 build|look|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_mouse)
# look  : EEVEE frames (reference angle, preview, side, front, back, top) composed into one sheet in the check folder
# export: build + FBX (root empty + one mesh per skeleton part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Rabbit/Cat).
# Helpers adapted from ../Rabbit/build_rabbit.py and ../Cat/build_cat.py; shared modules imported read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Mouse'
TAG = 'FarmAnimals_Mouse'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\SML-03.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_mouse')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -1.10, 0.40)          # SML-03 reference: left side from the front-left, ~18 deg above
PREVIEW_VIEW = (1.0, -1.30, 0.29)      # pack standard low 3/4 from the front-left (~10 deg above the ground): horizon + sky
PREVIEW_FILL = (0.66, 0.74)
PREVIEW_LENS = 40         # slightly wider than 50 mm so the horizon stays in frame at ~10 deg elevation
TARGET = 600
LIMIT = 900

PALETTE = ['#9D9696', '#8F8888', '#968E8D', '#868080',     # 0 top, 1 side, 2 front, 3 rear
           '#787272', '#D48B87', '#E2A19F', '#3A2219',     # 4 under, 5 ear pink walls, 6 nose, 7 eye
           '#DA9692', '#E0A09E', '#D99895', '#B5835A',     # 8 ear dish floor, 9 feet, 10 tail, 11-15 series spares
           '#7A5233', '#6E9F4A', '#F2E6C9', '#D8B65A']
F_TOP, F_SIDE, F_FRONT, F_BACK, F_UNDER, EAR_PINK, NOSE, EYE, EAR_FLOOR, FEET, TAILC = range(11)
FUR = 100              # placeholder slot: resolved per quad by its normal (shade pass)

# ---------------- layout (before the centre-of-mass shift) ----------------
# body profile: y, half width, z bottom, z top (chest -Y .. rump +Y); 8-gon rings with a flat top
BODY_PROF = [(-0.026, 0.0135, 0.0215, 0.0440), (-0.016, 0.0205, 0.0145, 0.0505), (-0.002, 0.0240, 0.0120, 0.0545),
             (0.014, 0.0250, 0.0115, 0.0550), (0.028, 0.0235, 0.0125, 0.0525), (0.038, 0.0180, 0.0170, 0.0455),
             (0.044, 0.0090, 0.0250, 0.0365)]
SPLIT = {'Spine2': (0, 2), 'Spine1': (2, 3), 'Pelvis': (3, 6)}
BODY_EXP = 2.5
# head rings along -Y: y, half width top, half width bottom (cheeks), z bottom, z top (10-gon, vertex on top)
HEAD_RINGS = [(-0.008, 0.0120, 0.0120, 0.0300, 0.0520), (-0.014, 0.0190, 0.0195, 0.0225, 0.0600),
              (-0.024, 0.0235, 0.0240, 0.0190, 0.0645), (-0.035, 0.0220, 0.0238, 0.0195, 0.0620),
              (-0.043, 0.0160, 0.0180, 0.0215, 0.0525), (-0.049, 0.0080, 0.0090, 0.0250, 0.0400)]
HEAD_EXP = 2.2
NECK = [Vector((0, -0.016, 0.030)), Vector((0, -0.021, 0.034)), Vector((0, -0.025, 0.039))]
EAR_C = Vector((0.0215, -0.016, 0.0610)); EAR_AX = Vector((0.45, -1.0, 0.12)); EAR_R = 0.0190; EAR_N = 10
EYE_AP = 0.0028                 # eye 8-gon apothem (dia 5.6 mm)
NOSE_C = (-0.0515, 0.0310)      # y, z of the nose's widest ring
FRONT = (0.0125, -0.012)
HIND = (0.0140, 0.027)
# polish round 2: tail leaves the rump low and runs just above the ground in a gentle S (absolute, after LEG_DROP)
TAIL_CP = [(0.0, 0.031, 0.0225), (0.0, 0.044, 0.0180), (0.003, 0.059, 0.0080), (0.012, 0.077, 0.0040),
           (0.027, 0.095, 0.0030), (0.042, 0.115, 0.0025), (0.051, 0.138, 0.0022), (0.054, 0.158, 0.0024)]
LEG_DROP = 0.0022      # polish round 2: legs ~20 % shorter -> everything above the lower legs drops by this
TAIL_SPLIT = (0.050, 0.095)
TAIL_N = 5
PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']
TAIL_PARTS = ('Tail1', 'Tail2', 'Tail3')


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-03', 'build'])[:2]


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


def body_ring(yk, n=8, p=BODY_EXP):
    w, zb, zt = lerp_tab(BODY_PROF, yk)
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + math.pi / n + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        out.append(Vector((w * spow(c, 2 / p), yk, zc + h * spow(s, 2 / p))))
    return out


def head_ring(y, wt, wb, zb, zt, n=10, p=HEAD_EXP):
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        w = wt if s > 1e-9 else (wb if s < -1e-9 else (wt + wb) / 2)
        out.append(Vector((w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Mouse'); self.pivot = {}; self.quads = []
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        """cap: None | slot (flat n-gon) | ('apex', point, slot) (hidden cone into the neighbour part)"""
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
                if s == FUR: self.quads.append(pair)
        for cap, ring in ((cap0, list(reversed(R[0]))), (cap1, list(R[-1]))):
            if cap is None: continue
            if isinstance(cap, tuple):
                _, apex, s = cap; A = bm.verts.new(apex)
                for k in range(n):
                    f = P.face([ring[k], ring[(k + 1) % n], A], s); faces.append(f)
                    if s == FUR: self.quads.append([f])
            else:
                f = P.face(ring, cap); faces.append(f)
                if cap == FUR: self.quads.append([f])
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R

    def cone(self, name, ring, apex, slot):
        # flat n-gon face + apex hidden inside the head
        P = self.P; bm = P.bm
        R = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(R)
        faces = [P.face(R, slot)] + [P.face([R[(k + 1) % n], R[k], A], slot) for k in range(n)]
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, False))


def build_body(M):
    rings = [body_ring(p[0]) for p in BODY_PROF]
    D = 0.008
    for part, (i0, i1) in SPLIT.items():
        # joint rings shared exactly by both parts (one continuous outer surface, no seam line); each part closes the
        # joint with a hidden cone reaching D into the neighbour = overlap that keeps a later bend closed
        rs = list(rings[i0:i1 + 1])
        c0 = FUR if part == 'Spine2' else ('apex', centroid(rs[0]) + Vector((0, -D, 0)), FUR)
        c1 = FUR if part == 'Pelvis' else ('apex', centroid(rs[-1]) + Vector((0, D, 0)), FUR)
        M.loft(part, rs, FUR, c0, c1)
    zc = 0.032
    M.pivot['Pelvis'] = Vector((0, BODY_PROF[3][0], zc))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[2][0], zc))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[1][0], zc))


def build_neck(M):
    def ring(c, t, r):
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 3, math.pi / 2)
    t1 = (NECK[1] - NECK[0]).normalized(); t2 = (NECK[2] - NECK[1]).normalized()
    M.loft('Neck1', [ring(NECK[0], t1, 0.0080), ring(NECK[1] + t1 * 0.002, t1, 0.0075)], FUR, FUR, FUR)
    M.loft('Neck2', [ring(NECK[1] - t2 * 0.002, t2, 0.0070), ring(NECK[2], t2, 0.0065)], FUR, FUR, FUR)
    M.pivot['Neck1'] = NECK[0].copy(); M.pivot['Neck2'] = NECK[1].copy()


def build_head(M):
    rings = [head_ring(*r) for r in HEAD_RINGS]
    M.loft('Head', rings, FUR, FUR, FUR)
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
    # eyes: dark-brown 8-gon discs, 0.5 mm proud, looking forward and a little out
    hp, n = surf(bvh, (0.0120, -0.044, 0.0425), (-0.35, 0.94, 0.0))
    ax = (n + Vector((0.0, -0.30, 0.0))).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.0006, e1, e2, EYE_AP, 8), c - a * 0.0025, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: pink hexagon cap (wider on top) over the muzzle tip
    hexp = [(0.0026, 0.0030), (0.0044, 0.0006), (0.0017, -0.0032), (-0.0017, -0.0032), (-0.0044, 0.0006), (-0.0026, 0.0030)]
    ny, nz = NOSE_C
    nring = lambda y, s, dz=0.0: [Vector((x * s * 1.08, y, nz + dz + z * s * 1.08)) for x, z in hexp]
    M.loft('Nose', [nring(ny + 0.0055, 0.90), nring(ny, 1.0), nring(ny - 0.0045, 0.60, -0.0004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = Vector((0, ny + 0.004, nz))
    # ears: thick discs (grey back + rim, deep pink dish) on the top-back corners of the head, facing forward/outward
    R = EAR_R; N = EAR_N
    rings_def = [(-0.0028, 1.00), (0.0022, 0.96), (0.0025, 0.76), (-0.0008, 0.42)]   # (offset along the axis, radius)
    c = EAR_C; a = EAR_AX.normalized()
    _, e1, e2 = pc.basis(a, (0, 0, 1))              # e1 ~ up in the disc plane
    rings = [ngon_ring(c + a * h, e1, e2, R * r, N, math.pi / N) for h, r in rings_def]
    down_in = (-e1 * 0.8 - Vector((1, 0, 0)) * 0.6); down_in = (down_in - a * down_in.dot(a)).normalized()
    piv = c + down_in * (0.55 * R)
    cols = {0: FUR, 1: FUR, 2: EAR_PINK}
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k: cols[j], FUR, EAR_FLOOR)
        M.pivot['Ear' + sfx] = piv.copy() if sx > 0 else mir(piv)
    # jaw: hidden chin block inside the head (connector for the Jaw bone)
    X = Vector((1, 0, 0)); Z = Vector((0, 0, 1))
    jr = [(-0.030, 0.0075, 0.0186, 0.0300), (-0.044, 0.0055, 0.0240, 0.0310)]
    M.loft('Jaw', [ngon_ring(Vector((0, y, (a + b) / 2)), X, Z, wd * 0.6, 3, math.pi / 2, (b - a) / (2 * wd)) for y, wd, a, b in jr],
           FUR, FUR, FUR)
    M.pivot['Jaw'] = Vector((0, -0.030, 0.029))


def foot(M, name, x, y, heel, front, w, h, z0=0.0004):
    """pink foot: chamfered pad (6-vertex section, 0.4 mm above the ground) + 3 toe blocks standing on z = 0"""
    def sec(yy, sw, sh):
        a, b = w * sw, h * sh
        return [Vector((x + px, yy, z0 + pz)) for px, pz in ((-a, 0.0), (a, 0.0), (a, 0.55 * b), (0.55 * a, b), (-0.55 * a, b), (-a, 0.55 * b))]
    y1 = y + heel; y0 = y - front; L = y1 - y0
    M.loft(name, [sec(y1, 0.90, 0.85), sec(y0, 1.0, 0.75)], FEET, FEET, FEET)
    tw = 0.00190; pitch = 0.0040
    for i in (-1, 0, 1):
        tx = x + i * pitch
        yb, yf = y0 + 0.0018, y0 - 0.0048
        back = [Vector((tx - tw, yb, 0)), Vector((tx + tw, yb, 0)), Vector((tx + 0.70 * tw, yb, 0.0026)), Vector((tx - 0.70 * tw, yb, 0.0026))]
        fr = [Vector((tx - 0.85 * tw, yf, 0)), Vector((tx + 0.85 * tw, yf, 0)), Vector((tx + 0.50 * tw, yf, 0.0016)), Vector((tx - 0.50 * tw, yf, 0.0016))]
        M.loft(name, [back, fr], FEET, FEET, FEET, ground=True)


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (lx, ly), heel, front in (('Front', FRONT, 0.0058, 0.0052), ('Hind', HIND, 0.0078, 0.0052)):
            x = lx * sx
            ring = lambda z, r, n, ph: ngon_ring(Vector((x, ly, z)), X, Y, r, n, ph)
            # Upper: hidden 4-gon connector inside the body and the top of the lower leg
            M.loft(kind + 'Upper' + sfx, [ring(0.028, 0.0018, 3, math.pi / 2), ring(0.015, 0.0018, 3, math.pi / 2)], FUR, FUR, FUR)
            M.loft(kind + 'Lower' + sfx, [ring(0.0198, 0.0069, 6, math.pi / 6), ring(0.0016, 0.0052, 6, math.pi / 6)], FUR, FUR, FUR)
            foot(M, kind + 'Foot' + sfx, x, ly, heel, front, 0.0064, 0.0034)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, ly, 0.026))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, ly, 0.0138))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, ly, 0.0025))


def tail_curve():
    P = [Vector(p) for p in TAIL_CP]
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
    rad = lambda s: 0.0034 - (0.0034 - 0.0006) * min(1.0, s / (L - 0.006))

    def ring(s):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (0, 0, 1))
        return ngon_ring(c, e1, e2, rad(s), TAIL_N, math.pi / 2)
    s1, s2 = TAIL_SPLIT; D = 0.006
    apex = lambda s: ('apex', tail_at(pts, S, s)[0], TAILC)
    M.loft('Tail1', [ring(0.0), ring(0.026), ring(s1)], TAILC, TAILC, apex(s1 + D))
    M.loft('Tail2', [ring(s1), ring((s1 + s2) / 2), ring(s2)], TAILC, apex(s1 - D), apex(s2 + D))
    M.loft('Tail3', [ring(s2), ring((s2 + L) / 2)], TAILC, apex(s2 - D), apex(L))
    M.pivot['Tail1'] = tail_at(pts, S, 0.010)[0]
    M.pivot['Tail2'] = tail_at(pts, S, s1)[0]
    M.pivot['Tail3'] = tail_at(pts, S, s2)[0]
    M.tail_len = L


def shade(M):
    """fur faces get one of 5 grey tones by the quad's outward normal (large-scale tonal shift, no noise)"""
    sl = M.P.slot
    for grp in M.quads:
        n = sum((f.normal for f in grp), Vector()).normalized()
        if n.z > 0.62: s = F_TOP
        elif n.z < -0.50: s = F_UNDER
        elif n.y < -0.40: s = F_FRONT
        elif n.y > 0.40: s = F_BACK
        else: s = F_SIDE
        for f in grp: f[sl] = s
    left = [f for f in M.P.bm.faces if f[sl] == FUR]
    if left: raise RuntimeError(f'{len(left)} unresolved fur faces')


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
    # legs ~20 % shorter: body, neck, head group and the hidden upper legs drop by LEG_DROP (lower legs/feet/tail absolute)
    for v in {v for nm, faces, _ in M.P.comp for f in faces for v in f.verts}: v.co.z -= LEG_DROP
    for k in M.pivot: M.pivot[k] = M.pivot[k] - Vector((0, 0, LEG_DROP))
    build_legs(M)
    for nm, faces, _ in M.P.comp:
        if 'Upper' in nm:
            for v in {v for f in faces for v in f.verts}: v.co.z -= LEG_DROP
    for k in M.pivot:
        if 'Upper' in k: M.pivot[k] = M.pivot[k] - Vector((0, 0, LEG_DROP))
    build_tail(M)
    bm = M.P.bm
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
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.03
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
    """tiny-model coplanar test: pairs of triangles in one plane (|d| < eps = 0.01 mm) that really overlap in 2D (SAT,
    penetration > pen). The shared pc.coplanar_overlaps only tests plane + 2 mm proximity, which at mouse scale also
    flags neighbouring toe soles that merely share the ground plane."""
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
    b2.free()
    print(f'  coplanar_true (plane < {eps*1000:.2f} mm, real 2D overlap): {len(bad)} pairs')
    return len(bad)


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    print('checks with the tail (deliberate +X curve):')
    chk_all = pc.comp_checks(M.P)
    print('checks, tail excluded from the mirror test:')
    chk = pc.comp_checks(M.P, mirror_skip=TAIL_PARTS)
    cop = coplanar_all(M, coll)
    cop10 = coplanar_all(M, coll, 10.0)   # tiny model: the shared check skips faces < 1 mm2, so also test a x10 copy
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
    W = lambda names: [o.matrix_world @ v.co for o in (obs[n] for n in names) for v in o.data.vertices]
    pts = W(PART_ORDER)
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = W(('Pelvis', 'Spine1', 'Spine2', 'Head', 'Nose'))
    hd = W(('Head',))
    er = W(('Ear.L',))
    print(f'SIZE width x {hi[0]-lo[0]:.4f} length y {hi[1]-lo[1]:.4f} height z {hi[2]-lo[2]:.4f} | y {lo[1]:.4f}..{hi[1]:.4f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.4f} back top '
          f'{max(p.z for p in W(("Pelvis", "Spine1"))):.4f} belly {min(p.z for p in W(("Spine1",))):.4f} '
          f'body width {max(p.x for p in W(("Pelvis", "Spine1"))) * 2:.4f}')
    print(f'HEAD w {max(p.x for p in hd) * 2:.4f} h {max(p.z for p in hd) - min(p.z for p in hd):.4f} top {max(p.z for p in hd):.4f} '
          f'| EAR dia ~{2 * EAR_R:.4f} ({2 * EAR_R / (max(p.z for p in hd) - min(p.z for p in hd)) * 100:.0f}% of head h) '
          f'top {max(p.z for p in er):.4f} outer x {max(p.x for p in er):.4f} | tail curve length {M.tail_len:.4f} '
          f'tail min z {min(p.z for p in W(TAIL_PARTS)):.4f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1e6:.2f} cm3 | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} '
          f'mirror (tail excluded) {chk["mirror"]:.6f} mirror (all) {chk_all["mirror"]:.6f} '
          f'worst gap {chk["gap"]} coplanar(shared, real scale: plane+proximity) {cop} coplanar_x10 {cop10} '
          f'coplanar_true {copt} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop10 + copt, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.02, 1, 0.20), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Mouse_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Mouse_{tag}_128.png'))
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
            img.pixels.foreach_set(t.ravel()); img.filepath_raw = os.path.join(CHECK, f'Mouse_{tag}_128.png')
            img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
        os.remove(p)
    rn.compose([rn.ref_tile(REF, 400)] + tiles, 3, os.path.join(CHECK, f'Mouse_{tag}_sheet.png'))


LOOK_VIEWS = (('ref', REF_VIEW, (0.62, 0.78)), ('prev', PREVIEW_VIEW, PREVIEW_FILL), ('side', (1, 0.0, 0.10), (0.75, 0.75)),
              ('front', (0.03, -1, 0.15), (0.6, 0.8)), ('back', (-0.5, 1.0, 0.35), (0.7, 0.8)), ('top', (0.2, -0.25, 1.0), (0.7, 0.8)))

if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-03 Mouse', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B, LOOK_VIEWS)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        bad = B['checks']['nonmanifold'] or B['checks']['loose'] or B['checks']['degenerate'] or B['coplanar'] \
            or B['checks']['problems'] or abs(B['minz']) > 1e-6
        if bad: raise RuntimeError('checks failed - not exporting')
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL,
                   lens=PREVIEW_LENS)
    elif CMD in ('preview', 'preview_check'):
        # preview only (mesh/FBX/blend untouched): 'preview_check' renders to the check folder, 'preview' to art/
        B = build(os.path.join(CHECK, 'tex'))
        out = os.path.join(CHECK, 'Mouse_prev_check.png') if CMD == 'preview_check' else os.path.join(ART, ASSET + '_Preview.png')
        rn.preview(B['sc'], list(B['obs'].values()), out, view=PREVIEW_VIEW, fill=PREVIEW_FILL, lens=PREVIEW_LENS)
        a = rn.load_px(out); t = rn.resize(a, 80)
        img = bpy.data.images.new('TMP_Thumb', t.shape[1], t.shape[0], alpha=True); img.pixels.foreach_set(t.ravel())
        img.filepath_raw = os.path.join(CHECK, 'Mouse_prev_128.png'); img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
