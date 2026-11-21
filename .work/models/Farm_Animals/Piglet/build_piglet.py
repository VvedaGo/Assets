# build_piglet.py - LIV-07 Piglet (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_piglet.py -- LIV-07 build|views|close|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_piglet)
# views : build + EEVEE sheet (reference + 6 views) + 128 px thumbnail
# close : build + EEVEE close-ups (head, ear roots, tail, leg joins)
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as Pig/Calf).
# Structure copied from ../Pig/build_pig.py (Model/loft/tuck, head frame, ear builder, snout, tail); baby proportions.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import pack_common as pc
import pack_shapes as ps
import animal_render as rn

ASSET = 'FMS_Piglet'
TAG = 'FarmAnimals_Piglet'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\LIV-07.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_piglet')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.75, -0.80, 0.16)      # LIV-07 reference: body ~50 deg off head-on from the front-left, slightly above
PREVIEW_VIEW = (0.80, -0.90, 0.20)  # pack preview template (Pig)
BUDGET = 1100

PALETTE = ['#F6A4AC', '#F9B3B9', '#F0909B', '#EE909A',    # 0 body side, 1 top (light), 2 low (warm), 3 ear outside
           '#CF6A7B', '#F3A2AB', '#DD7D8B', '#B4505F',     # 4 ear inside, 5 snout face, 6 snout wall, 7 nostril
           '#4A2C22', '#5A3A2C', '#E58D99', '#B5835A',     # 8 eye (dark brown), 9 hoof, 10 knee band, 11-15 spares
           '#6E9F4A', '#8E959B', '#C8473B', '#F2E6C9']
BODY, BACK, BELLY, EAR, EAR_IN, SNOUT, SNOUT_RIM, NOSTRIL, EYE, HOOF, KNEE = range(11)

# ---------------- layout (before the centre-of-mass shift) ----------------
NB = 12                                  # body sides
DZ = 0.035                               # body/head/tail raised above the legs (belly ~0.10)
# body profile: y, half width, z bottom, z top  (plump barrel ~1.1x head width; front rings hidden inside the big head)
BODY_PROF = [(-0.21, 0.095, 0.160, 0.330), (-0.17, 0.150, 0.104, 0.362), (-0.09, 0.182, 0.080, 0.386),
             (0.01, 0.193, 0.066, 0.402), (0.11, 0.194, 0.063, 0.411), (0.20, 0.183, 0.074, 0.405),
             (0.265, 0.155, 0.100, 0.384), (0.31, 0.105, 0.145, 0.345), (0.332, 0.045, 0.205, 0.290)]
SPLIT = {'Spine2': (0, 2), 'Spine1': (2, 5), 'Pelvis': (5, 8)}

# head frame: U along the head (poll -> snout), VV head 'up'
HEAD_TILT = math.radians(6)
U = Vector((0, -math.cos(HEAD_TILT), -math.sin(HEAD_TILT)))
VV = Vector((0, -math.sin(HEAD_TILT), math.cos(HEAD_TILT)))
X = Vector((1, 0, 0))
P0 = Vector((0, -0.07, 0.298))
HEAD_GROUP = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
HEAD_SCALE = 1.15
HEAD_HW = 0.438                            # head width before HEAD_SCALE (0.504 m in the model): ear sizes are x HEAD_HW
HEAD_Q = Vector((0, -0.26, 0.13))          # head group grows about the chin front: up and back over the chest
# (s along U, half width top, half width bottom, half height top, half height bottom)
HEAD_RINGS = [(0.00, 0.120, 0.125, 0.115, 0.110), (0.045, 0.180, 0.190, 0.166, 0.160),
              (0.105, 0.212, 0.222, 0.188, 0.185), (0.165, 0.214, 0.226, 0.184, 0.184),
              (0.212, 0.198, 0.210, 0.172, 0.170), (0.245, 0.172, 0.180, 0.152, 0.140)]   # broad flat face (eyes on it)
SNOUT_DV = -0.060                       # snout centre below the head axis
# snout rings (s, half width, half height)
SNOUT_RINGS = [(0.200, 0.090, 0.075), (0.282, 0.090, 0.075), (0.292, 0.081, 0.066)]
SN = 14                                 # snout sides
NOS = dict(dx=0.037, dv=-0.006, r=0.0165, sy=1.05, depth=0.012, n=10)
NECK = [((-0.10, 0.260), (-0.150, 0.280), 0.105, 0.100), ((-0.135, 0.275), (-0.185, 0.295), 0.095, 0.090)]
FRONT = (0.106, -0.10)
HIND = (0.108, 0.215)
TAIL = dict(root=(0.305, 0.335), centre=(0.352, 0.438), yaw=-35.0, r0=0.066, r1=0.022, th0=-100.0, th1=330.0, step=45.0,
            rad0=0.024, rad1=0.017, split=(0.09, 0.25))

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['LIV-07', 'build'])[:2]


def hsh(*a):
    """deterministic pseudo-random in [-1, 1] (same input -> same value, so mirrored vertices get the same offset)"""
    x = math.sin(sum((i + 1) * 12.9898 * (v + 0.37) for i, v in enumerate(a))) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


JIT = 0.015            # body facet jitter: radial +-1.5 % (clean paper-craft facets, quads stay near planar)


def body_ring(y, w, zb, zt, n=NB, pt=2.0, pb=2.4, j=0):
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
        self.P = pc.Part('Piglet'); self.pivot = {}
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


# ---------------- body: pink, slightly darker back strip, lighter belly ----------------
def body_col_for(j0):
    def col(j, k, tip):
        gj = j0 + j                                  # global band index along the body
        lvl = k if k < NB // 2 else NB - 1 - k      # 0 = beside the back ridge, NB/2-1 = beside the belly line
        if lvl <= 1: return BACK                    # top: light shade
        if lvl >= NB // 2 - 2: return BELLY         # lower flank + belly: warm deeper shade
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
            M.loft(part, rs, body_col_for(i0), BODY, BODY, diag=body_diag(i0))
        else:   # rear end tucked into the part behind it
            pre = tuck(rs[-1], (0, 1, 0), 0.86, 0.02)
            M.loft(part, rs[:-1] + [pre[1], pre[0]], body_col_for(i0), BODY, BODY, diag=body_diag(i0))
    M.pivot['Pelvis'] = Vector((0, BODY_PROF[5][0], 0.25))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[2][0], 0.25))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[0][0] + 0.03, 0.25))


def build_neck(M):
    for nm, (a, b, w, h) in zip(('Neck1', 'Neck2'), NECK):
        ca, cb = Vector((0, a[0], a[1])), Vector((0, b[0], b[1]))
        rings = [ring_xyz(c, w, w, h, h, 4, X, Vector((0, 0, 1)), 2.0, 2.0, math.pi / 4) for c in (ca, cb)]
        M.loft(nm, rings, BODY, BODY, BODY)
        M.pivot[nm] = ca.copy()


# ---------------- head ----------------
def head_col(j, k, tip):
    kk = (k + 1) % 12; lvl = min(kk, 12 - kk)           # 0 = top face (centred), 6 = bottom face
    if lvl <= 1: return BACK
    if lvl >= 5: return BELLY
    return BODY


def build_head(M):
    rings = [ring_xyz(P0 + U * s, wt, wb, ht, hb, 12, X, VV, 2.4, 2.6, math.pi / 12) for s, wt, wb, ht, hb in HEAD_RINGS]
    for j, r in enumerate(rings):
        if j in (0, len(rings) - 1): continue
        c = P0 + U * HEAD_RINGS[j][0]
        for k in range(12):
            r[k] = c + (r[k] - c) * (1.0 + 0.015 * hsh(j, min(k, 11 - k), 5))
    M.loft('Head', rings, head_col, BODY, BODY,
           diag=lambda j, k: (hsh(j, min(k, 11 - k), 6) > 0) if k < 6 else not (hsh(j, min(k, 11 - k), 6) > 0))
    head_faces = list(M.P.comp[-1][1])
    M.pivot['Head'] = P0 + U * 0.02
    # snout disc: 12-gon, protruding, chamfered front edge, flat front with 2 recessed nostrils
    cen = lambda s: P0 + U * s + VV * SNOUT_DV
    rings = [ring_xyz(cen(s), w, w, h, h, SN, X, VV, 2.0, 2.0, math.pi / SN) for s, w, h in SNOUT_RINGS]
    R = M.loft('Nose', rings, lambda j, k, tip: SNOUT_RIM if j == 0 else BACK, SNOUT_RIM, None)   # dark wall, light rim bevel
    fc = cen(SNOUT_RINGS[-1][0]); nr = NOS
    holes = []
    for sx in (1, -1):
        c = fc + X * (sx * nr['dx']) + VV * nr['dv']
        holes.append([M.P.bm.verts.new(p) for p in ngon_ring(c, X, VV, nr['r'], nr['n'], math.pi / nr['n'], nr['sy'])])
    new = ps.fill(M.P, [R[-1]] + holes, SNOUT, U)
    for hl in holes: new += ps.blind(M.P, hl, U, nr['depth'], NOSTRIL, NOSTRIL)
    M.tag('Nose', new); M.P.comp[-1][1].extend(new)
    M.pivot['Nose'] = cen(0.24)
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


# ---------------- pig ear: thick triangular flap with one fold (reusable; sizes in head widths hw) ----------------
# Piglet placement in the head frame (X out, U forward, VV up from P0), before HEAD_SCALE. The Pig passes its own points.
EAR_FLAP = dict(
    hinge_target=(0.150, 0.110, 0.175),   # ray target on the upper outer skull corner (X, U, VV)
    lean_out=30.0,                        # rise leans 30 deg outward from vertical
    rise=0.09,                            # hinge -> fold line, x hw
    tip=(0.200, 0.240, 0.082),            # tip point (X, U, VV): ~eye level, slightly outside the front cheek, in front
    sink=0.06,                            # hidden base ring below the hinge, x hw
    # full widths x hw at: hidden base, hinge, fold, 40 %, 70 %, 92 % of the drop, tip (blunt)
    width=(0.32, 0.40, 0.38, 0.28, 0.17, 0.07, 0.025),
    thick=(0.09, 0.10, 0.10, 0.08, 0.06, 0.04, 0.025),   # full thickness x hw
    drop_at=(0.40, 0.70, 0.92, 1.0))
EAR_PROF = [(1.0, 0.0), (0.55, 1.0), (-0.55, 1.0), (-1.0, 0.0), (-0.55, -1.0), (0.55, -1.0)]   # (width, thickness); +thick = outer
EAR_INNER_FACES = (3, 4, 5)           # profile faces on the inner (-thick) side: darker


def flap_ear(hinge, out, up, tip, hw, E=EAR_FLAP):
    """LEFT ear as rings: hinge (on the skull) -> short rise leaning `lean_out` outward -> ONE fold line -> straight
    droop to `tip`. The width axis W = rise x droop is the same for every section (no twist); sections are thick lenses
    tapering to a blunt tip. The right ear = exact X-mirror of these points."""
    out = Vector(out).normalized(); up = Vector(up).normalized()
    a = math.radians(E['lean_out'])
    D0 = (up * math.cos(a) + out * math.sin(a)).normalized()
    F = hinge + D0 * (E['rise'] * hw)
    D1 = (Vector(tip) - F).normalized(); L1 = (Vector(tip) - F).length
    W = D0.cross(D1).normalized()
    df = (D0 + D1).normalized(); mitre = 1.0 / max(0.4, math.cos(0.5 * D0.angle(D1)))
    st = [(hinge - D0 * (E['sink'] * hw), D0, 1.0), (hinge, D0, 1.0), (F, df, mitre)]
    st += [(F + D1 * (t * L1), D1, 1.0) for t in E['drop_at']]
    sgn = 1.0 if D1.cross(W).dot(up) > 0 else -1.0       # +thickness side = outer (upper) face of the droop
    rings = [[c + W * (0.5 * wd * hw * pa) + d.cross(W).normalized() * (sgn * 0.5 * th * hw * m * pb) for pa, pb in EAR_PROF]
             for (c, d, m), wd, th in zip(st, E['width'], E['thick'])]
    return rings, dict(hinge=hinge.copy(), fold=F, tip=Vector(tip), fold_deg=math.degrees(D0.angle(D1)),
                       droop_deg=math.degrees(math.asin(max(-1.0, min(1.0, -D1.dot(up))))))


def build_face(M, head_faces):
    hb = bvh_of(head_faces)
    # eyes: dark-brown 12-gon discs set flush on the face facet (2 mm proud, 10 mm sunk; depth 12 mm < 0.03 x head)
    hp, n = surf(hb, P0 + U * 0.24 + VV * 0.066 + X * 0.116, -U)          # on the planar front cap
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); a = n if sx > 0 else mir(n)
        _, e1, e2 = pc.basis(a, (0, 0, 1))
        # planar disc on the best-fit plane of the face under it, raised only to clear the highest sample by 1.5 mm
        H = [surf(hb, p, -a)[0] for p in ngon_ring(c, e1, e2, 0.023, 12)]
        nrm = Vector()
        for i in range(12):
            p, q = H[i], H[(i + 1) % 12]
            nrm += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
        nrm.normalize()
        if nrm.dot(a) < 0: nrm = -nrm
        cc = sum(H, Vector()) / 12
        off = max(max((h - cc).dot(nrm) for h in H), (surf(hb, c, -a)[0] - cc).dot(nrm)) + 0.0015
        _, e1, e2 = pc.basis(nrm, (0, 0, 1))
        M.loft('Eye' + sfx, [ngon_ring(cc - nrm * 0.010, e1, e2, 0.022, 12), ngon_ring(cc + nrm * off, e1, e2, 0.022, 12)],
               EYE, EYE, EYE)
        print(f'  eye{sfx} proud {off*1000:.1f} mm, depth {(off + 0.010)*1000:.1f} mm')
        M.pivot['Eye' + sfx] = c.copy()
    # ears: one thick triangular flap (left) built in the head frame, right ear = exact X-mirror
    E = EAR_FLAP; tx, tu, tv = E['hinge_target']
    hp, n = surf(hb, P0 + U * tu + VV * tv + X * tx, -VV * 0.8 - X * 0.6)
    tx, tu, tv = E['tip']
    rings, info = flap_ear(hp, X, VV, P0 + X * tx + U * tu + VV * tv, HEAD_HW)
    print(f'  EAR fold angle {info["fold_deg"]:.0f} deg, droop {info["droop_deg"]:.0f} deg below horizontal')
    col = lambda j, k, tip: EAR_IN if k in EAR_INNER_FACES and j >= 1 else EAR
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]     # winding is unified by recalc_face_normals
        M.loft('Ear' + sfx, rr, col, EAR, EAR)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)
    M.ear_info = info
    # jaw: small light chin under the snout (4-gon, mostly inside the head)
    j0 = P0 + U * 0.15 - VV * 0.135
    jr = [(-0.02, 0.060, 0.030, 0.026), (0.075, 0.066, 0.032, 0.030)]
    M.loft('Jaw', [ring_xyz(j0 + U * t, w, w, ht, hb_, 4, X, VV, 2.0, 2.0, math.pi / 4) for t, w, ht, hb_ in jr],
           BELLY, BELLY, BELLY)
    M.pivot['Jaw'] = j0.copy()


# ---------------- legs: each one tapered 8-gon prism (top radius 1.15 x bottom), one loop at the hoof line ----------------
LEG = dict(rb=0.046, rt=0.053, z_top=0.235, z_knee=0.078, z_hoof=0.042, inset=0.985)


def build_legs(M):
    Y = Vector((0, 1, 0)); L = LEG
    r = lambda z: L['rb'] + (L['rt'] - L['rb']) * z / L['z_top']
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            ring = lambda z, rr: ngon_ring(Vector((x, y, z)), X, Y, rr, 8, math.pi / 8)
            zk, zh = L['z_knee'], L['z_hoof']
            # Upper: body -> knee on the taper; Lower: starts 15 mm up inside the Upper, 0.3 mm under its surface at the knee
            M.loft(kind + 'Upper' + sfx, [ring(L['z_top'], r(L['z_top'])), ring(zk, r(zk))], BODY, BODY, BODY)
            M.loft(kind + 'Lower' + sfx, [ring(zk + 0.015, r(zk + 0.015) * L['inset']), ring(zh - 0.006, r(zh - 0.006) * L['inset'])],
                   BODY, BODY, BODY)
            M.loft(kind + 'Foot' + sfx, [ring(0.0, r(0.0) * 1.02), ring(zh, r(zh) * 1.02)], HOOF, HOOF, HOOF, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, L['z_top']))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, zk))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, zh))


# ---------------- tail: corkscrew in the mid plane (x = 0), curl plane yawed to the front-left ----------------
def tail_curve():
    T = TAIL; ry, rz = T['root']; cy, cz = T['centre']
    th0, th1 = math.radians(T['th0']), math.radians(T['th1'])
    r = lambda th: T['r0'] + (T['r1'] - T['r0']) * (th - th0) / (th1 - th0)
    sp = lambda th: Vector((0, cy + r(th) * math.cos(th), cz + r(th) * math.sin(th)))
    s0 = sp(th0)
    pts = [Vector((0, ry, rz)).lerp(s0, i / 12) for i in range(12)]
    n = 240
    pts += [sp(th0 + (th1 - th0) * i / n) for i in range(n + 1)]
    Rz = Matrix.Rotation(math.radians(T['yaw']), 3, 'Z'); o = Vector((0, ry, 0))      # whole curl yawed about the root
    pts = [o + Rz @ (p - o) for p in pts]
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


TN = 6                 # tail tube sides


def build_tail(M):
    T = TAIL; pts, S, stem = tail_curve(); L = S[-1]
    st = [0.0, 0.035, stem]
    nsp = int(round((T['th1'] - T['th0']) / T['step']))
    seg = S[12:]
    for i in range(1, nsp + 1):
        st.append(seg[round(240 * i / nsp)])
    st = sorted(set(round(s, 5) for s in st))
    rad = lambda s: T['rad0'] + (T['rad1'] - T['rad0']) * s / L

    def ring(s, r=None):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, rad(s) if r is None else r, TN, 0.0)
    s1, s2 = T['split']
    s1 = min(st, key=lambda v: abs(v - s1)); s2 = min(st, key=lambda v: abs(v - s2))
    segs = [('Tail1', [s for s in st if s <= s1], BODY), ('Tail2', [s for s in st if s1 <= s <= s2], BODY),
            ('Tail3', [s for s in st if s >= s2], BODY)]
    for name, ss, colr in segs:
        rs = [ring(e) for e in ss]
        if name == 'Tail1':      # root sunk into the rump
            c, t = tail_at(pts, S, 0.0)
            rs = [ngon_ring(c - t * 0.03, *pc.basis(t, (1, 0, 0))[1:], rad(0) * 0.95, TN, 0.0)] + rs[1:]
        else:
            c, t = tail_at(pts, S, ss[0])
            pre = tuck(rs[0], -t, 0.86, 0.010)
            rs = [pre[0], pre[1]] + rs[1:]
        if name == 'Tail3':     # blunt rounded tip
            c, t = tail_at(pts, S, L); _, e1, e2 = pc.basis(t, (1, 0, 0))
            rs.append(ngon_ring(c + t * 0.008, e1, e2, rad(L) * 0.60, TN, 0.0))
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
    if HEAD_SCALE != 1.0:
        hv = {v for nm, faces, _ in M.P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}
        for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
        for k in HEAD_GROUP: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE
    legs = {k + s + x for k in ('Front', 'Hind') for s in ('Upper', 'Lower', 'Foot') for x in ('.L', '.R')}
    up = {v for nm, faces, _ in M.P.comp if nm not in legs for f in faces for v in f.verts}
    for v in up: v.co.z += DZ
    for k in M.pivot:
        if k not in legs: M.pivot[k] = M.pivot[k] + Vector((0, 0, DZ))
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
    print(f'TRIS total {tot} | target ~{BUDGET} (+15% = {int(BUDGET * 1.15)})')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = [o.matrix_world @ v.co for nm_ in ('Pelvis', 'Spine1', 'Spine2', 'Nose') for o in (obs[nm_],) for v in o.data.vertices]
    back = max((obs['Pelvis'].matrix_world @ v.co).z for v in obs['Pelvis'].data.vertices)
    hd = [obs['Head'].matrix_world @ v.co for v in obs['Head'].data.vertices]
    bz = [obs[n].matrix_world @ v.co for n in ('Spine1', 'Pelvis') for v in obs[n].data.vertices]
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} back top {back:.3f} '
          f'belly {min(p.z for p in bz):.3f} | head w {max(p.x for p in hd) - min(p.x for p in hd):.3f} '
          f'h {max(p.z for p in hd) - min(p.z for p in hd):.3f} top {max(p.z for p in hd):.3f}')
    # ear checks: exact mirror pair (world), inside the head silhouette from above, nothing behind the skull or below the eye
    eL = [obs['Ear.L'].matrix_world @ v.co for v in obs['Ear.L'].data.vertices]
    eR = [obs['Ear.R'].matrix_world @ v.co for v in obs['Ear.R'].data.vertices]
    from mathutils import kdtree
    kd = kdtree.KDTree(len(eR))
    for i, p in enumerate(eR): kd.insert(p, i)
    kd.balance()
    emir = max(kd.find(Vector((-p.x, p.y, p.z)))[2] for p in eL)
    pivm = (obs['Ear.R'].location - Vector((-obs['Ear.L'].location.x, obs['Ear.L'].location.y, obs['Ear.L'].location.z))).length
    eye_z = obs['Eye.L'].location.z
    hx = max(abs(p.x) for p in hd); hy0 = min(p.y for p in hd); hy1 = max(p.y for p in hd)
    ex = max(abs(p.x) for p in eL + eR); ey0 = min(p.y for p in eL + eR); ey1 = max(p.y for p in eL + eR)
    ez = min(p.z for p in eL + eR)
    S = HEAD_SCALE; sh = M.shift + Vector((0, 0, DZ))
    w = lambda p: HEAD_Q + (p - HEAD_Q) * S + sh
    hi_, fo_, ti_ = w(M.ear_info['hinge']), w(M.ear_info['fold']), w(M.ear_info['tip'])
    ok = ex <= hx and ey1 <= hy1 and ez >= eye_z - 0.03
    print(f'EARS mirror error {emir:.6f} (pivots {pivm:.6f}) | from above: ear |x| max {ex:.3f} <= head {hx:.3f}, '
          f'ear y {ey0:.3f}..{ey1:.3f} within head y {hy0:.3f}..{hy1:.3f} (rear plane) | ear min z {ez:.3f} vs eye centre {eye_z:.3f} '
          f'| {"PASS" if ok else "FAIL"}')
    print(f'EAR.L hinge {tuple(round(c, 3) for c in hi_)} fold {tuple(round(c, 3) for c in fo_)} tip {tuple(round(c, 3) for c in ti_)}'
          f' | tip vs eye {ti_.z - eye_z:+.3f} m')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.2f} L | geometry shift {tuple(round(c, 4) for c in M.shift)} '
          f'| tail length {M.tail_len:.3f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} coplanar {cop} problems {chk["problems"]}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Piglet_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    extra = sys.argv[sys.argv.index('--') + 3:] if '--' in sys.argv else []
    tag = extra[0] if extra else 'v'
    print('=== LIV-07 Piglet', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'views':
        B = build(os.path.join(CHECK, 'tex')); tiles = []
        for i, (v, fl) in enumerate([(PREVIEW_VIEW, (0.56, 0.70)), ((1, 0, 0.06), (0.8, 0.8)), ((0, 1, 0.18), (0.6, 0.78)),
                                     ((-0.8, 0.9, 0.35), (0.7, 0.8)), ((0, -1, 0.08), (0.6, 0.78)), ((0.3, -0.25, 1.0), (0.7, 0.8)), (REF_VIEW, (0.56, 0.70))]):
            pth = os.path.join(CHECK, f'v{i}.png')
            rn.preview(B['sc'], list(B['obs'].values()), pth, view=v, fill=fl)
            a = rn.load_px(pth)
            if i == 0: rn.compose([rn.resize(a, 128)], 1, os.path.join(CHECK, f'Piglet_{tag}_128.png'))
            tiles.append(rn.resize(a, 330)); os.remove(pth)
        rn.compose([rn.ref_tile(REF, 330)] + tiles, 4, os.path.join(CHECK, f'Piglet_{tag}_views.png'))
    elif CMD == 'close':
        B = build(os.path.join(CHECK, 'tex')); O = B['obs']; tiles = []
        shots = [(['Head', 'Nose', 'Jaw', 'Eye.L', 'Eye.R'], (0.35, -1, -0.15)), (['Head', 'Nose', 'Jaw', 'Ear.L', 'Ear.R'], (1, 0.35, 0.2)),
                 (['Head', 'Ear.L', 'Ear.R', 'Spine2', 'Spine1'], (-0.3, 0.8, 0.8)),
                 (['Tail1', 'Tail2', 'Tail3', 'Pelvis'], (0.2, 1, 0.3)), (['Tail1', 'Tail2', 'Tail3', 'Pelvis'], (-1, 0.2, 0.1)),
                 (['FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'Spine2', 'Spine1', 'Pelvis'], (1, -0.2, -0.05))]
        for i, (nms, v) in enumerate(shots):
            pth = os.path.join(CHECK, f'c{i}.png')
            rn.preview(B['sc'], [O[n] for n in nms], pth, view=v, fill=(0.8, 0.85))
            tiles.append(rn.resize(rn.load_px(pth), 330)); os.remove(pth)
        rn.compose(tiles, 3, os.path.join(CHECK, f'Piglet_{tag}_close.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.56, 0.70))
