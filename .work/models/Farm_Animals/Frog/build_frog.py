# build_frog.py - SML-05 Frog (Farm Animals, skeleton H = Q-S without tail), MESH ONLY (no armature, weights, clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_frog.py -- SML-05 build|look|export
# build : parts + palette + checks + Workbench check sheet (%TEMP%/FarmAnimals_check_frog)
# look  : EEVEE frames (reference angle, preview, side, front, back, top) in one sheet + 128 px thumbnail
# export: build + FBX (root empty + one mesh per skeleton part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Helpers adapted from ../Mouse/build_mouse.py; shared modules imported read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Frog'
TAG = 'FarmAnimals_Frog'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\SML-05.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_frog')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.58, -1.0, 0.36)          # SML-05 reference: front-left 3/4 (we see the frog's left = +X), ~18 deg above
PREVIEW_VIEW = (0.55, -1.0, 0.15)      # pack standard low 3/4 from the front-left (horizon + sky), as Cat/Pig
PREVIEW_FILL = (0.62, 0.78)
TARGET = 900
SUN_ROT = (48, 0, -35)     # pack standard key light (animal_render.preview)
LIMIT = 1300

PALETTE = ['#80A94A', '#749C42', '#7BA446', '#6A923C',     # 0 green top, 1 side, 2 front, 3 back
           '#5A7F33', '#DECDA0', '#D3C08F', '#C2AD7C',     # 4 green under, 5 cream light, 6 cream mid, 7 cream dark
           '#3E2A20', '#B5835A', '#7A5233', '#C8473B',     # 8 eye, 9-15 series spares
           '#F2E6C9', '#6E9F4A', '#8E959B', '#D8B65A']
G_TOP, G_SIDE, G_FRONT, G_BACK, G_UNDER, C_LIGHT, C_MID, C_DARK, EYE = range(9)
GREEN = 100            # placeholder: green, tone by the quad normal
SKIN = 101             # placeholder: cream bib or green (per triangle, by part + position + normal)

# ---------------- layout (before the centre-of-mass shift) ----------------
# body profile along +Y: y, half width, z bottom, z top (10-gon superellipse rings, flat top and bottom edge)
BODY_PROF = [(-0.0485, 0.0130, 0.0130, 0.0320), (-0.044, 0.0210, 0.0090, 0.0375), (-0.036, 0.0262, 0.0062, 0.0470),
             (-0.022, 0.0290, 0.0058, 0.0525), (-0.006, 0.0285, 0.0075, 0.0505), (0.010, 0.0280, 0.0085, 0.0465),
             (0.023, 0.0245, 0.0105, 0.0410), (0.032, 0.0185, 0.0135, 0.0355), (0.037, 0.0100, 0.0180, 0.0305)]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 8)}
BODY_EXP = 2.3
DZ = -0.0025           # rework round 2: body + head lowered (front legs ~15 % shorter); belly bottoms lowered less
BELLY_UP = 0.0015
# head = horizontal slices (z, half width, y front, y back), lofted upwards from the mouth crease; jaw downwards
HEAD_ANG = [0, 38, 82, 132, 180, 228, 278, 322]   # 8 points: larger, cleaner head facets
HEAD_EXP = 2.4
HEAD_TAPER = 0.22      # snout narrower than the back of the head (plan view)
# rework round 3: lip ring (head) and the jaw's top ring share one outline -> flush; the crease between them is a thin
# groove (0.6 mm deep, 1 mm wide), no overhang step
CREASE = (0.0400, 0.0284, -0.0514, -0.0100)
HEAD_LV = [(0.0405, 0.0290, -0.0520, -0.0080), (0.0492, 0.0272, -0.0492, -0.0090), (0.0585, 0.0185, -0.0380, -0.0140)]
JAW_LV = [(0.0395, 0.0290, -0.0520, -0.0080), (0.0310, 0.0262, -0.0478, -0.0120), (0.0225, 0.0185, -0.0405, -0.0160)]
NECK = [Vector((0, -0.016, 0.036 + DZ)), Vector((0, -0.030, 0.044 + DZ))]
# eye dome: sphere-ish loft along the eye axis; (offset along the axis, radius) in units of EYE_R
# rework round 2: sphere dome (dia 0.3 x head width), the pupil disc is the flat front cut of the sphere at 0.8 R
# (radius 0.6 R = 0.6 x the dome diameter), flush, no rim ring; the axis points forward/out and a little down, so green
# dome shows around and above the disc
EYE_S = Vector((0.0180, -0.0280, 0.0605 + DZ)); EYE_R = 0.0083; EYE_AX = Vector((0.36, -0.93, -0.04))
EYE_RINGS = [(-0.80, 0.60), (-0.40, 0.92), (0.10, 1.00), (0.50, 0.87), (0.80, 0.60)]
EYE_COLS = [GREEN, GREEN, GREEN, GREEN]
# front leg (left): shoulder, elbow, wrist; apothems
FL = [Vector((0.0200, -0.0300, 0.0220)), Vector((0.0262, -0.0365, 0.0125)), Vector((0.0295, -0.0415, 0.0028))]
FL_R = (0.0072, 0.0064, 0.0058)
FF_DIR = Vector((0.36, -1.0, 0.0)).normalized()
# hind leg (left): hip, knee (thigh), shin start, ankle
# rework round 2: one teardrop thigh (thin at the hip inside the body, swelling to a big round knee, forward-up) along
# the body side, knee out-forward-up (40 deg off the reference view axis so the teardrop is not seen end-on); shin
# back-down on its outer side from the knee to the heel; long flat foot forward
# rework round 3: flattened angular wedge thigh against the body side, hip (back, low) -> knee point (front, top);
# (t, half height, half thickness): 0.050 long (0.56 x body length), 0.018 tall (0.38 x body height), 0.013 thick
HIP = Vector((0.0225, 0.0310, 0.0140)); KNEE = Vector((0.0315, -0.0140, 0.0340))
THIGH = [(0.00, 0.0078, 0.0052), (0.22, 0.0092, 0.0064), (0.55, 0.0078, 0.0060), (0.84, 0.0048, 0.0044), (1.00, 0.0020, 0.0022)]
SHIN0 = Vector((0.0365, -0.0100, 0.0235)); ANKLE = Vector((0.0395, 0.0260, 0.0055)); SHIN_R = (0.0056, 0.0046)
HF_DIR = Vector((0.35, -1.0, 0.0)).normalized()
PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Head', 'Jaw', 'Eye.L', 'Eye.R',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R']


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['SML-05', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def lerp_tab(T, y):
    if y <= T[0][0]: return T[0][1:]
    if y >= T[-1][0]: return T[-1][1:]
    for a, b in zip(T, T[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return tuple(a[i] + (b[i] - a[i]) * t for i in range(1, len(a)))


def ngon_ring(c, e1, e2, r, n, phase=None):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def axis_ring(c, t, r, n, ref=(0, 0, 1), ph=None):
    _, e1, e2 = pc.basis(t, ref)
    return ngon_ring(c, e1, e2, r, n, ph)


def body_ring(yk, n=10, p=BODY_EXP):
    w, zb, zt = lerp_tab(BODY_PROF, yk)
    zb += DZ + BELLY_UP; zt += DZ
    zc, h = (zt + zb) / 2, (zt - zb) / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + math.pi / n + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        out.append(Vector((w * spow(c, 2 / p), yk, zc + h * spow(s, 2 / p))))
    return out


def outline(z, w, yf, yb, p=HEAD_EXP):
    yc, b = (yf + yb) / 2, (yb - yf) / 2
    out = []
    for a in HEAD_ANG:
        y = yc - b * spow(math.cos(math.radians(a)), 2 / p)
        f = 1.0 - HEAD_TAPER * ((yb - y) / (yb - yf)) ** 2
        out.append(Vector((w * f * spow(math.sin(math.radians(a)), 2 / p), y, z + DZ)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def mir(p):
    return Vector((-p.x, p.y, p.z))


def mir_cap(cap):
    return ('apex', mir(cap[1]), cap[2]) if isinstance(cap, tuple) else cap


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Frog'); self.pivot = {}; self.groups = []
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        """cap: None | slot (flat n-gon) | ('apex', point, slot) (cone; hidden when the apex is inside the neighbour)"""
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
                if s >= 100: self.groups.append(pair)
        for cap, ring in ((cap0, list(reversed(R[0]))), (cap1, list(R[-1]))):
            if cap is None: continue
            if isinstance(cap, tuple):
                _, apex, s = cap; A = bm.verts.new(apex)
                for k in range(n):
                    f = P.face([ring[k], ring[(k + 1) % n], A], s); faces.append(f)
                    if s >= 100: self.groups.append([f])
            else:
                f = P.face(ring, cap); faces.append(f)
                if cap >= 100: self.groups.append([f])
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R

    def pair(self, base, rings, col, cap0=None, cap1=None, ground=False):
        self.loft(base + '.L', rings, col, cap0, cap1, ground)
        self.loft(base + '.R', [[mir(p) for p in r] for r in rings], col, mir_cap(cap0), mir_cap(cap1), ground)


def build_body(M):
    rings = [body_ring(p[0]) for p in BODY_PROF]
    D = 0.007
    for part, (i0, i1) in SPLIT.items():
        rs = list(rings[i0:i1 + 1])
        # chest front and rump end: small flat caps (no visible cone fans); joints: hidden cones
        c0 = SKIN if part == 'Spine2' else ('apex', centroid(rs[0]) + Vector((0, -D, 0)), SKIN)
        c1 = SKIN if part == 'Pelvis' else ('apex', centroid(rs[-1]) + Vector((0, D, 0)), SKIN)
        M.loft(part, rs, SKIN, c0, c1)
    zc = 0.030 + DZ
    M.pivot['Pelvis'] = Vector((0, BODY_PROF[SPLIT['Pelvis'][0]][0], zc))
    M.pivot['Spine1'] = Vector((0, BODY_PROF[SPLIT['Spine1'][0]][0], zc))
    M.pivot['Spine2'] = Vector((0, BODY_PROF[2][0], zc + 0.004))


def build_head(M):
    X = Vector((1, 0, 0))
    t = (NECK[1] - NECK[0]).normalized()
    M.loft('Neck1', [axis_ring(NECK[0], t, 0.006, 3, X, math.pi / 2), axis_ring(NECK[1], t, 0.006, 3, X, math.pi / 2)],
           GREEN, GREEN, GREEN)
    M.pivot['Neck1'] = NECK[0].copy()
    cr = outline(*CREASE)
    hr = [cr] + [outline(*lv) for lv in HEAD_LV]
    M.loft('Head', hr, GREEN, ('apex', centroid(cr) - Vector((0, 0, 0.006)), GREEN), GREEN)
    M.pivot['Head'] = NECK[1].copy()
    jr = [cr] + [outline(*lv) for lv in JAW_LV]
    M.loft('Jaw', jr, SKIN, ('apex', centroid(cr) + Vector((0, 0, 0.006)), SKIN), SKIN)
    M.pivot['Jaw'] = Vector((0, -0.016, CREASE[0] + DZ))


def build_eyes(M):
    a = EYE_AX.normalized(); R = EYE_R
    rings = [axis_ring(EYE_S + a * (t * R), a, r * R, 8, (0, 0, 1)) for t, r in EYE_RINGS]
    M.pair('Eye', rings, lambda j, k: EYE_COLS[j], GREEN, EYE)     # front cap = flush dark pupil disc
    base = EYE_S - a * (0.5 * R)
    M.pivot['Eye.L'] = base; M.pivot['Eye.R'] = mir(base)


def pad_rings(c, d, heel, front, w0, w1, h, z0=0.0004):
    u = Vector((-d.y, d.x, 0))

    def sec(p, w, sh):
        a, b = w, h * sh
        return [p + u * px + Vector((0, 0, z0 + pz)) for px, pz in ((-a, 0), (a, 0), (a, 0.55 * b), (0.55 * a, b), (-0.55 * a, b), (-a, 0.55 * b))]
    return [sec(c - d * heel, w0, 0.9), sec(c + d * front, w1, 0.8)]


def toe_rings(base, d, L, wb, wt, h, lift=0.0008):
    """flat toe: trapezoid section, widening to a spatula tip whose top edge is set back (rounded look). The sole rises
    from z = 0 at the tip to `lift` at the base, so neighbouring toe soles (different directions) are never coplanar."""
    u = Vector((-d.y, d.x, 0)); Z = Vector((0, 0, 1))

    def sec(p, w, hh, back, z0):
        p = p + Z * z0
        return [p - u * w, p + u * w, p + u * (0.68 * w) + Z * hh - d * back, p - u * (0.68 * w) + Z * hh - d * back]
    return [sec(base, wb, h, 0.0, lift), sec(base + d * L, wt, 0.8 * h, 0.0012, 0.0)]


def rot(d, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return Vector((d.x * c - d.y * s, d.x * s + d.y * c, 0)).normalized()


def foot(M, name, c, d, heel, front, w0, w1, h, angs, L, wb, wt, pitch):
    M.pair(name, pad_rings(c, d, heel, front, w0, w1, h), GREEN, GREEN, GREEN)
    u = Vector((-d.y, d.x, 0)); n = len(angs)
    for i, ag in enumerate(angs):
        dd = rot(d, ag)             # toe i sits at -u..+u, so its angle runs the same way (no crossing)
        b = c + d * (front - 0.0025) + u * ((i - (n - 1) / 2) * pitch)
        b.z = 0.0
        M.pair(name, toe_rings(b, dd, L, wb, wt, 0.0031), GREEN, GREEN, GREEN, ground=True)


def build_legs(M):
    S, E, W = FL
    t1 = (E - S).normalized(); t2 = (W - E).normalized(); tb = (t1 + t2).normalized()
    X = (1, 0, 0)
    M.pair('FrontUpper', [axis_ring(S, t1, FL_R[0], 6, X), axis_ring(E, tb, FL_R[1], 6, X)], GREEN,
           ('apex', S - t1 * 0.006, GREEN), ('apex', E + t2 * 0.005, GREEN))
    tw = (t2 + Vector((0, 0, -1))).normalized()   # wrist ring tilted only half way, so it stays above z = 0 inside the pad
    M.pair('FrontLower', [axis_ring(E, tb, FL_R[1], 6, X), axis_ring(W, tw, FL_R[2], 6, X)], GREEN,
           ('apex', E - t1 * 0.005, GREEN), GREEN)
    foot(M, 'FrontFoot', Vector((W.x, W.y, 0)), FF_DIR, 0.0045, 0.0055, 0.0062, 0.0082, 0.0050,
         (-36, -12, 12, 36), 0.0075, 0.0025, 0.0030, 0.0042)
    M.pivot['FrontUpper.L'] = S.copy(); M.pivot['FrontLower.L'] = E.copy(); M.pivot['FrontFoot.L'] = W.copy()
    # hind: thigh forward from the hip, shin back down to the ankle, foot forward-outward on the ground
    th = (KNEE - HIP).normalized()
    _, e1, e2 = pc.basis(th, (0, 0, 1))        # e1 ~ up (in the vertical plane of the axis), e2 lateral
    if e2.x < 0: e2 = -e2
    sec = lambda c, hh, ht: [c + e1 * hh, c + e2 * ht + e1 * (0.45 * hh), c + e2 * ht - e1 * (0.50 * hh), c - e1 * hh,
                             c - e2 * ht - e1 * (0.50 * hh), c - e2 * ht + e1 * (0.45 * hh)]
    rings = [sec(HIP.lerp(KNEE, t), hh, ht) for t, hh, ht in THIGH]
    M.pair('HindUpper', rings, GREEN, ('apex', HIP - th * 0.005, GREEN), GREEN)
    ts = (ANKLE - SHIN0).normalized()
    M.pair('HindLower', [axis_ring(SHIN0, ts, SHIN_R[0], 6), axis_ring(ANKLE, ts, SHIN_R[1], 6)], GREEN,
           ('apex', HIP.lerp(KNEE, 0.80), GREEN), GREEN)
    foot(M, 'HindFoot', Vector((ANKLE.x, ANKLE.y, 0)), HF_DIR, 0.0040, 0.0200, 0.0052, 0.0074, 0.0048,
         (-36, -18, 0, 18, 36), 0.0090, 0.0017, 0.0021, 0.0030)   # heel 4 mm, pad 20 mm forward
    M.pivot['HindUpper.L'] = HIP.copy(); M.pivot['HindLower.L'] = KNEE.copy(); M.pivot['HindFoot.L'] = ANKLE.copy()
    for k in [k for k in M.pivot if k.endswith('.L') and not k.startswith('Eye')]:
        M.pivot[k[:-2] + '.R'] = mir(M.pivot[k])


def is_bib(part, c, n):
    if part == 'Jaw':
        return (n.y < -0.15 or n.z < -0.25) and abs(n.x) < 0.62     # jaw sides under the mouth corners stay green
    if part in ('Spine2', 'Spine1', 'Pelvis'):
        return n.z < -0.30 or (n.y < -0.30 and abs(n.x) < 0.75 and c.z < 0.045)
    return False


def green_tone(n):
    if n.z > 0.62: return G_TOP
    if n.z < -0.45: return G_UNDER
    if n.y < -0.45: return G_FRONT
    if n.y > 0.45: return G_BACK
    return G_SIDE


def cream_tone(n):
    if n.z < -0.45: return C_DARK
    if n.z > 0.20 or n.y < -0.75: return C_LIGHT
    return C_MID


def shade(M):
    sl = M.P.slot; pl = M.pl
    for grp in M.groups:
        n = sum((f.normal for f in grp), Vector()).normalized()
        for f in grp:
            if f[sl] == SKIN and is_bib(PART_ORDER[f[pl]], f.calc_center_median(), f.normal):
                f[sl] = cream_tone(n)
            else:
                f[sl] = green_tone(n)
    left = [f for f in M.P.bm.faces if f[sl] >= 100]
    if left: raise RuntimeError(f'{len(left)} unresolved faces')


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
    build_body(M); build_head(M); build_eyes(M); build_legs(M)
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
    """tiny-model coplanar test (from the Mouse): triangles in one plane (|d| < 0.01 mm) that really overlap in 2D (SAT)"""
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
    pl = b2.faces.layers.int['part']; kinds = {}
    for i, j in bad:
        k = (PART_ORDER[b2.faces[i][pl]], PART_ORDER[b2.faces[j][pl]]); kinds[k] = kinds.get(k, 0) + 1
    b2.free()
    print(f'  coplanar_true (plane < {eps*1000:.2f} mm, real 2D overlap): {len(bad)} pairs {kinds}')
    return len(bad)


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    M = build_model()
    chk = pc.comp_checks(M.P)
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
    bl = W(('Pelvis', 'Spine1', 'Spine2', 'Head', 'Jaw'))
    hd = W(('Head',)); ey = W(('Eye.L',))
    print(f'SIZE width x {hi[0]-lo[0]:.4f} length y {hi[1]-lo[1]:.4f} height z {hi[2]-lo[2]:.4f} | y {lo[1]:.4f}..{hi[1]:.4f} '
          f'min z {lo[2]:.5f} | snout->rump {max(p.y for p in bl) - min(p.y for p in bl):.4f} '
          f'belly {min(p.z for p in W(("Spine1",))):.4f} body width {max(p.x for p in W(("Pelvis", "Spine1", "Spine2"))) * 2:.4f}')
    print(f'HEAD w {max(p.x for p in hd) * 2:.4f} top {max(p.z for p in hd):.4f} | EYE top {max(p.z for p in ey):.4f} '
          f'dome dia {2 * EYE_R:.4f} ({2 * EYE_R / (max(p.x for p in hd) * 2) * 100:.0f}% of head w) disc/socket '
          f'{EYE_RINGS[-1][1] / EYE_RINGS[2][1] * 100:.0f}% (disc dia / dome dia) thigh len {(KNEE - HIP).length:.4f} | hind outer x {max(p.x for p in W(("HindUpper.L", "HindLower.L"))):.4f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1e6:.2f} cm3 | geometry shift {tuple(round(c, 4) for c in M.shift)}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"]} coplanar(shared, real scale) {cop} coplanar_x10 {cop10} '
          f'coplanar_true {copt} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop10 + copt, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.4, 1, 0.30), (0.25, -0.3, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Frog_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


def look(B, views, tag='look'):
    """EEVEE preview-style frames composed into one sheet (each tile 400 px high) + a 128 px thumbnail of the first"""
    tiles = []
    for i, (nm, v, fill) in enumerate(views):
        p = os.path.join(CHECK, f'look_{i}.png')
        preview(B['sc'], list(B['obs'].values()), p, view=v, fill=fill)
        a = rn.load_px(p); tiles.append(rn.resize(a, 400))
        if i == 0:
            t = rn.resize(a, 80); img = bpy.data.images.new('TMP_Thumb', t.shape[1], t.shape[0], alpha=True)
            img.pixels.foreach_set(t.ravel()); img.filepath_raw = os.path.join(CHECK, f'Frog_{tag}_128.png')
            img.file_format = 'PNG'; img.save(); bpy.data.images.remove(img)
        os.remove(p)
    rn.compose([rn.ref_tile(REF, 400)] + tiles, 3, os.path.join(CHECK, f'Frog_{tag}_sheet.png'))


# ---------------- preview (copy of _common/animal_render.preview; frog change: fine sun shadow texels for a 7 cm model)
def preview(sc, objs, out, view=(1.0, -0.62, 0.34), fill=(0.70, 0.80), lens=50):
    """EEVEE 1280x800, three-quarter front-left; camera-visible sky gradient + meadow ground disc, sun + fill."""
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, 100
    sc.eevee.shadow_ray_count = 3; sc.eevee.shadow_step_count = 12; sc.eevee.taa_render_samples = 128
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('TMP_PreviewWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (rn._lin('e3'), rn._lin('ec'), rn._lin('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (rn._lin('86'), rn._lin('b4'), rn._lin('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1)
    amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface'])
    old_world = sc.world; sc.world = w
    # meadow ground: big disc, soft green, fades into the horizon haze
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = 60.0
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(rn._solid_mat('TMP_Meadow_M', '#93AE6E'))
    gob = bpy.data.objects.new('TMP_Meadow', me); sc.collection.objects.link(gob)
    lights = []
    for nm, rot, e, sh in (('TMP_Sun', SUN_ROT, 3.6, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(8); ld.use_shadow = sh
        ld.shadow_maximum_resolution = 0.00005   # tiny model: default 1 mm shadow texels give blotchy self-shadows
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob); lights.append(ob)
    cam = rn.camera(sc, 'TMP_PrevCam', lens)
    pts = rn.mesh_points(objs)
    rn.fit(sc, cam, pts, view, fill)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights + [gob, cam]:
        d = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
        if isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
        elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    sc.world = old_world; bpy.data.worlds.remove(w)
    print('preview', out)


LOOK_VIEWS = (('ref', REF_VIEW, (0.70, 0.80)), ('side', (1, 0.0, 0.10), (0.75, 0.75)), ('front', (0.03, -1, 0.15), (0.6, 0.8)),
              ('back', (-0.5, 1.0, 0.35), (0.7, 0.8)), ('top', (0.2, -0.25, 1.0), (0.7, 0.8)))

if __name__ == '__main__':
    ID, CMD = args()
    print('=== SML-05 Frog', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        look(B, LOOK_VIEWS)
    elif CMD == 'refview':
        B = build(os.path.join(CHECK, 'tex'))
        preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Frog_refview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        bad = B['checks']['nonmanifold'] or B['checks']['loose'] or B['checks']['degenerate'] or B['coplanar'] \
            or B['checks']['problems'] or abs(B['minz']) > 1e-6
        if bad: raise RuntimeError('checks failed - not exporting')
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
