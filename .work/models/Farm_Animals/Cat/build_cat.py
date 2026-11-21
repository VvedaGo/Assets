# build_cat.py - PET-02 Cat (Farm Animals, skeleton Q), MESH ONLY this round (no armature, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_cat.py -- PET-02 build|export
# build : parts + palette + stripes + checks + check sheet (%TEMP%/FarmAnimals_check_cat)
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Cow).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Cat'
TAG = 'FarmAnimals_Cat'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\PET-02.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_cat')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (1.0, -1.0, 0.36)          # PET-02 reference: left side from the front-left, ~15 deg above
PREVIEW_VIEW = (1.0, -0.95, 0.19)     # preview: same side as the reference, a bit lower (sky behind the head)

PALETTE = ['#F0913A', '#E07F2C', '#C45A1C', '#A8481A',     # 0 orange, 1 orange shade, 2 stripe, 3 stripe dark
           '#F6DFB8', '#E9CDA2', '#EE9E8A', '#E3837C',     # 4 cream, 5 cream shade, 6 inner ear pink, 7 nose pink
           '#2A1D17', '#3A2E28', '#B5835A', '#6E9F4A',     # 8 eye, 9 paw sole, 10-15 spare series colours
           '#8E959B', '#C8473B', '#F2E6C9', '#D8B65A']
ORANGE, ORANGE_D, STRIPE, STRIPE_D, CREAM, CREAM_D, EAR_PINK, NOSE, EYE, SOLE = range(10)

# ---------------- layout (before the centre-of-mass shift) ----------------
SLANT = 0.32          # body rings lean back going down the flanks (stripe direction of the reference)
# body profile: y, half width, z bottom, z top
BODY_PROF = [(-0.165, 0.045, 0.175, 0.255), (-0.152, 0.066, 0.142, 0.275), (-0.130, 0.082, 0.122, 0.290),
             (-0.100, 0.088, 0.116, 0.298), (-0.050, 0.090, 0.115, 0.300), (0.020, 0.090, 0.117, 0.296),
             (0.080, 0.089, 0.123, 0.293), (0.125, 0.086, 0.132, 0.291), (0.150, 0.081, 0.143, 0.287),
             (0.166, 0.072, 0.156, 0.279), (0.177, 0.056, 0.172, 0.266), (0.183, 0.034, 0.192, 0.248)]
# body rings: (y at the spine, slant factor); parts split at ring 5 (Spine2|Spine1) and ring 8 (Spine1|Pelvis)
BODY_RINGS = [(-0.165, 0), (-0.152, 0), (-0.130, 0), (-0.105, 0.5), (-0.082, 1), (-0.060, 1), (-0.025, 1), (0.000, 1),
              (0.030, 1), (0.055, 1), (0.080, 1), (0.110, 1), (0.135, 0.45), (0.152, 0.25), (0.166, 0.1), (0.177, 0),
              (0.183, 0)]
# band j (ring j..j+1) -> lowest flank level reached (+ pointed tip below); left (+X) and right (-X) flanks differ
STRIPES_L = {4: 1, 6: 3, 9: 2, 11: 3, 13: 0}
STRIPES_R = {3: 1, 6: 2, 8: 3, 10: 2, 12: 3}
SPLIT = {'Spine2': (0, 5), 'Spine1': (5, 8), 'Pelvis': (8, 16)}

# head rings along -Y: y, half width, z bottom, z top
HEAD_RINGS = [(-0.122, 0.045, 0.300, 0.372), (-0.138, 0.068, 0.280, 0.402), (-0.168, 0.079, 0.272, 0.414),
              (-0.200, 0.075, 0.274, 0.408), (-0.226, 0.060, 0.278, 0.385), (-0.243, 0.040, 0.284, 0.350),
              (-0.253, 0.025, 0.292, 0.334)]
NECK_AXIS = [(-0.105, 0.232), (-0.120, 0.258), (-0.133, 0.279), (-0.146, 0.298), (-0.160, 0.320)]   # (y, z) centres
NECK_R = [(0.052, 0.044), (0.054, 0.046), (0.052, 0.045), (0.049, 0.043), (0.044, 0.038)]          # (half width, half depth)
FRONT = (0.048, -0.095)
HIND = (0.056, 0.115)
TAIL_CP = [(0.160, 0.255), (0.186, 0.276), (0.206, 0.305), (0.218, 0.340), (0.222, 0.376), (0.218, 0.410),
           (0.205, 0.437), (0.186, 0.452), (0.166, 0.455)]
TAIL_SPLIT = (0.085, 0.160)
TAIL_STRIPES = [(0.045, 0.067), (0.100, 0.122), (0.140, 0.160), (0.180, 0.202)]

HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.15
EYE_R = 0.0124        # eye 8-gon apothem before the head scale (0.0143 after)
HEAD_Q = Vector((0, -0.150, 0.300))

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-02', 'build'])[:2]


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


def body_ring(yk, f, n=10, pt=2.5, pb=2.2):
    out = []
    zt0 = lerp_tab(BODY_PROF, yk)[2]
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        y = yk
        for _ in range(4):
            w, zb, zt = lerp_tab(BODY_PROF, y)
            zc, h = (zt + zb) / 2, (zt - zb) / 2
            p = pt if s >= 0 else pb
            x = w * spow(c, 2 / p); z = zc + h * spow(s, 2 / p)
            y = yk + SLANT * f * (zt0 - z)
        out.append(Vector((x, y, z)))
    return out


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def tuck(ring, axis_back, scale=0.965, depth=0.02):
    """child's proximal end: the boundary ring is replaced by a slightly smaller ring hidden `depth` inside
    the parent; the child surface crosses the parent's capped end ~1.5% inside it (thin seam, no extra band)"""
    c = centroid(ring); ab = Vector(axis_back).normalized()
    return [c + (p - c) * scale + ab * depth for p in ring]


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Cat'); self.pivot = {}
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
        pl = P.bm.faces.layers.int['part']
        for f in faces: f[pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R

    def cone(self, name, ring, apex, slot):
        # flat n-gon face + apex hidden inside the head (n + n-2 tris)
        P = self.P; bm = P.bm
        R = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(R)
        faces = [P.face(R, slot)] + [P.face([R[(k + 1) % n], R[k], A], slot) for k in range(n)]
        pl = bm.faces.layers.int['part']
        for f in faces: f[pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, False))


def build_body(M):
    rings = [body_ring(y, f) for y, f in BODY_RINGS]

    def col_for(j0):
        def col(j, k, tip):
            gj = j0 + j; L = min(k, 9 - k)
            if L == 4: return CREAM if gj <= 12 else ORANGE           # belly strip (not under the tail)
            if gj <= 1: return CREAM                                  # chest bib (incl. the throat under the chin)
            if gj == 2 and L >= 2: return CREAM
            if gj == 3 and L >= 3: return CREAM
            m = (STRIPES_L if k >= 5 else STRIPES_R).get(gj)
            if m is not None and (L <= m or (L == m + 1 and tip)): return STRIPE
            return ORANGE
        return col
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part == 'Pelvis':
            M.loft(part, rs, col_for(i0), ORANGE, ORANGE)
        else:   # proximal (rear) end tucked into the parent behind it
            rs2 = rs[:-1] + [tuck(rs[-1], (0, 1, 0))]
            col0 = col_for(i0)
            M.loft(part, rs2, lambda j, k, tip, c0=col0, nb=len(rs) - 1: c0(min(j, nb - 1), k, tip),
                   CREAM if part == 'Spine2' else ORANGE, ORANGE)
    M.pivot['Pelvis'] = Vector((0, 0.110, 0.235))
    M.pivot['Spine1'] = Vector((0, BODY_RINGS[8][0], 0.240))
    M.pivot['Spine2'] = Vector((0, BODY_RINGS[5][0], 0.245))


def build_neck(M):
    X = Vector((1, 0, 0))
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 4)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))                 # e1 = nape direction (back/up)
        w, h = NECK_R[i]
        rings.append(ring_xyz(c, w, h, h, 6, X, e1))

    def col(L_cream, stripe):
        def f(j, k, tip):
            L = min(k, 5 - k)
            if L >= L_cream: return CREAM
            if stripe and L == 0 and j == stripe: return STRIPE
            return ORANGE
        return f
    M.loft('Neck1', rings[0:3], col(1, None), ORANGE, ORANGE)
    t = (cs[2] - cs[3]).normalized()
    M.loft('Neck2', [tuck(rings[2], t, 0.965, 0.012), rings[3], rings[4]], col(1, 0), ORANGE, ORANGE)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[2].copy()


def build_head(M):
    X = Vector((1, 0, 0)); Z = Vector((0, 0, 1))
    rings = [ring_xyz(Vector((0, y, (zb + zt) / 2)), w, (zt - zb) / 2, (zt - zb) / 2, 10, X, Z, 2.4, 3.0)
             for y, w, zb, zt in HEAD_RINGS]

    def col(j, k, tip):
        L = min(k, 9 - k)
        if L == 4: return CREAM
        if L == 3 and j >= 1: return CREAM
        if L == 2 and j >= 4: return CREAM
        if L == 2 and j == 3 and not tip: return CREAM
        if L == 1 and j == 2 and tip: return STRIPE               # temple stripe over the eye, running back
        if L == 0 and j == 3 and tip: return STRIPE               # pointed forehead marks (M)
        if L == 0 and j == 1: return STRIPE                       # crown stripe between the ears
        if L == 2 and j == 1 and tip: return STRIPE               # cheek stripe behind the eye
        if L == 2 and j == 2 and tip: return STRIPE
        return ORANGE
    R = M.loft('Head', rings, col, ORANGE, CREAM)
    head_faces = list(M.P.comp[-1][1])
    M.pivot['Head'] = Vector((0, -0.150, 0.305))
    return head_faces


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
    # eyes: dark 8-gon discs, 3 mm proud, looking forward-sideways
    hp, n = surf(bvh, (0.035, -0.205, 0.352), (-0.62, 0.78, 0.0))
    ax = (n + Vector((0.10, -0.30, 0.0))).normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = ax if sx > 0 else mir(ax)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + a * 0.002, e1, e2, EYE_R, 8), c - a * 0.008, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: pink inverted triangle on the top of the muzzle front
    hp, n = surf(bvh, (0, -0.25, 0.328), (0, 1, 0))
    up = Vector((0, 0, 1)); up = (up - n * up.dot(n)).normalized(); side = Vector((1, 0, 0))
    tri = [Vector((0.014, 0, 0.004)), Vector((-0.014, 0, 0.004)), Vector((0, 0, -0.011))]
    ring = lambda off: [hp + n * off + side * p.x + up * p.z for p in tri]
    M.loft('Nose', [ring(-0.006), ring(0.004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # ears: thick triangles, pink inner dish with an orange rim, roots sunk into the skull
    hp, n = surf(bvh, (0.052, -0.160, 0.35), (0, 0, -1))
    u = Vector((0.24, 0.06, 1.0)).normalized()
    f = Vector((0.18, -1.0, 0.0)); f = (f - u * f.dot(u)).normalized()
    s = u.cross(f).normalized()                                  # outer side (+X for the left ear)
    prof = [(0.049, 0.0), (0.036, 0.009), (0.0, -0.003), (-0.036, 0.009), (-0.049, 0.0), (0.0, -0.020)]
    base = hp - u * 0.011
    rings = [[base + u * h + s * (a * sc) + f * (b * sc) for a, b in prof] for h, sc in ((0.0, 1.0), (0.071, 0.07))]
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k, tip: EAR_PINK if k in (1, 2) else ORANGE, ORANGE, ORANGE)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    # jaw: cream chin block under the muzzle
    X = Vector((1, 0, 0)); Z = Vector((0, 0, 1))
    jr = [(-0.188, 0.022, 0.282, 0.298), (-0.212, 0.034, 0.268, 0.292), (-0.246, 0.020, 0.276, 0.292)]
    M.loft('Jaw', [ring_xyz(Vector((0, y, (a + b) / 2)), w, (b - a) / 2, (b - a) / 2, 6, X, Z) for y, w, a, b in jr],
           CREAM, CREAM, CREAM)
    M.pivot['Jaw'] = Vector((0, -0.188, 0.292))


def build_legs(M):
    X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, r, sy=1.0, dy=0.0: ngon_ring(Vector((x, y + dy, z)), X, Y, r, 8, math.pi / 8, sy)
            if kind == 'Front':
                up = [ring(0.200, 0.022), ring(0.112, 0.035), ring(0.098, 0.034)]
                up_stripe = 1
                lo = [ring(0.108, 0.029), ring(0.064, 0.0285), ring(0.030, 0.027)]
                z_up, z_lo = 0.215, 0.100
            else:
                up = [ring(0.250, 0.024, 1.35), ring(0.140, 0.036, 1.2, 0.003), ring(0.122, 0.035, 1.15, 0.004),
                      ring(0.104, 0.032, 1.1, 0.004)]
                up_stripe = 2
                lo = [ring(0.114, 0.028, 1.0, 0.004), ring(0.064, 0.0285, 1.0, 0.002), ring(0.030, 0.027)]
                z_up, z_lo = 0.225, 0.106
            def ucol(j, k, tip, s_=up_stripe, fr=(kind == 'Front')):
                if j == s_: return STRIPE
                if fr and j == 0 and (k == 5 or (k in (4, 6) and tip)): return CREAM     # bib flows down the leg front
                return ORANGE
            M.loft(kind + 'Upper' + sfx, up, ucol, ORANGE, ORANGE)
            M.loft(kind + 'Lower' + sfx, lo, lambda j, k, tip: STRIPE if j == 1 else ORANGE, ORANGE, ORANGE)
            pr = lambda z, sc: ngon_ring(Vector((x, y - 0.008, z)), X, Y, 0.036 * sc, 8, math.pi / 8, 1.2)
            M.loft(kind + 'Foot' + sfx, [pr(0.0, 0.94), pr(0.007, 1.0), pr(0.042, 0.66)],
                   lambda j, k, tip: SOLE if j == 0 else CREAM, SOLE, CREAM, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, z_up))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, z_lo))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.034))


def tail_curve():
    P = [Vector((0, y, z)) for y, z in TAIL_CP]
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
    X = Vector((1, 0, 0))

    def ring(s, r):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 8, math.pi / 8)
    rad = lambda s: 0.0255 - 0.004 * s / L
    s1, s2 = TAIL_SPLIT
    edges = sorted({0.0, s1, s2} | {a for a, b in TAIL_STRIPES} | {b for a, b in TAIL_STRIPES})
    tipS = [L - 0.014, L]
    def is_stripe(sa, sb):
        m = (sa + sb) / 2; return any(a <= m <= b for a, b in TAIL_STRIPES)
    segs = [('Tail1', 0.0, s1), ('Tail2', s1, s2), ('Tail3', s2, L)]
    for name, a, b in segs:
        ss = [e for e in edges if a <= e <= b]
        if name == 'Tail3': ss = [e for e in ss if e < tipS[0] - 0.004] + tipS
        rs = []
        for e in ss:
            r = rad(e)
            if name == 'Tail3' and e >= tipS[0]: r = {0: rad(e), 1: 0.011}[tipS.index(e)]
            rs.append(ring(e, r))
        sv = list(ss)
        if name != 'Tail1':
            c, t = tail_at(pts, S, a)
            rs = [tuck(rs[0], -t, 0.965, 0.012)] + rs[1:]
            sv = [a - 0.012] + sv[1:]
        cols = [STRIPE if is_stripe(sv[j], sv[j + 1]) else ORANGE for j in range(len(sv) - 1)]
        M.loft(name, rs, lambda j, k, tip, cc=cols: cc[j], ORANGE, ORANGE)
        M.pivot[name] = tail_at(pts, S, a)[0]
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
    # head group scaled about the head/neck joint (reference head is big and round)
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
    print(f'TRIS total {tot} | target ~1300')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = [p for o in (obs['Pelvis'], obs['Spine1'], obs['Spine2'], obs['Head']) for p in [o.matrix_world @ v.co for v in o.data.vertices]]
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} back top '
          f'{max(p.z for o in (obs["Spine1"],) for p in [o.matrix_world @ v.co for v in o.data.vertices]):.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.2f} L | geometry shift {tuple(round(c, 4) for c in M.shift)} '
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Cat_{tag}_sheet.png'))
    rn.fit(sc, cam, pts, REF_VIEW, (0.86, 0.86))
    sc.render.resolution_x, sc.render.resolution_y = 192, 128
    rn.render_to(sc, os.path.join(CHECK, f'Cat_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-02 Cat', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Cat_look_ref.png'), view=REF_VIEW, fill=(0.62, 0.78))
        for nm, v in (('side', (1, 0.0, 0.1)), ('right', (-1, -0.6, 0.25)), ('back', (-0.5, 1.0, 0.35))):
            rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, f'Cat_look_{nm}.png'), view=v, fill=(0.62, 0.78))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.62, 0.78))
