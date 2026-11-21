# build_kitten.py - PET-04 Kitten (Farm Animals, skeleton Q), MESH ONLY (no armature, no weights, no clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_kitten.py -- PET-04 build|look|export
# build : parts + palette + checks + check sheet (%TEMP%/FarmAnimals_check_kitten)
# look  : EEVEE frames (reference angle, side, front, back, top, 128 px) into the check folder
# export: build + FBX (root empty + one mesh per skeleton-Q part, pivot on the joint) + verify + .blend + preview
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity, as the Cat).
# Based on ../Cat/build_cat.py (copied helpers); joints share the boundary ring + hidden child band (no seam lines).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn

ASSET = 'FMS_Kitten'
TAG = 'FarmAnimals_Kitten'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\PET-04.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_kitten')
os.makedirs(CHECK, exist_ok=True)
REF_VIEW = (0.75, -1.0, 0.14)         # PET-04 reference: front three-quarter from the front-left, ~12 deg above
PREVIEW_VIEW = (1.00, -1.0, 0.20)

PALETTE = ['#9A9496', '#A8A2A4', '#8A8486', '#BFB8BA',     # 0 grey, 1 grey light, 2 grey dark, 3 ear inner
           '#3A261F', '#4A3530', '#3A2E28', '#7D7779',     # 4 eye, 5 nose, 6 sole, 7 grey darker
           '#B5835A', '#7A5233', '#C8473B', '#F2E6C9',     # 8-15 series spares
           '#6E9F4A', '#8E959B', '#D8B65A', '#2A1D17']
GREY, GREY_L, GREY_D, EAR_IN, EYE, NOSE, SOLE, GREY_DD = range(8)
FACET_SHADES = True    # fur faces: light on top-facing facets, dark on the underside (soft, follows the light)

# ---------------- layout (before the centre-of-mass shift) ----------------
# torso profile: y, half width, z bottom, z top (one ring per row, 10 sides)
BODY = [(-0.112, 0.040, 0.090, 0.150), (-0.101, 0.066, 0.064, 0.166), (-0.080, 0.080, 0.051, 0.174),
        (-0.040, 0.086, 0.048, 0.177), (0.012, 0.086, 0.048, 0.179), (0.056, 0.084, 0.050, 0.181),
        (0.086, 0.078, 0.056, 0.181), (0.106, 0.066, 0.068, 0.176), (0.119, 0.048, 0.085, 0.164),
        (0.125, 0.026, 0.104, 0.148)]
SPLIT = {'Spine2': (0, 3), 'Spine1': (3, 5), 'Pelvis': (5, 9)}
# head rings along -Y: y, half width, z centre (cheek line), half height up, half height down (12 sides)
HEAD = [(0.000, 0.055, 0.213, 0.050, 0.040), (-0.020, 0.100, 0.210, 0.088, 0.066), (-0.052, 0.127, 0.205, 0.108, 0.075),
        (-0.095, 0.131, 0.202, 0.112, 0.072), (-0.135, 0.116, 0.201, 0.100, 0.066), (-0.160, 0.086, 0.203, 0.080, 0.050),
        (-0.172, 0.054, 0.207, 0.052, 0.030)]
HEAD_PT, HEAD_PB = 2.2, 3.0
NECK_AXIS = [(-0.055, 0.140), (-0.068, 0.165), (-0.080, 0.192)]
NECK_R = 0.034
FRONT = (0.048, -0.058)
HIND = (0.048, 0.070)
LEG_R = 0.0300
TAIL_CP = [(0.096, 0.146), (0.127, 0.161), (0.158, 0.178), (0.182, 0.200), (0.194, 0.228), (0.195, 0.256), (0.186, 0.281),
           (0.171, 0.297)]
TAIL_R = (0.0285, 0.0245)
EYE_R = 0.0125         # 8-gon apothem (0.027 across corners)
EYE_X, EYE_Z = 0.049, 0.212
HEAD_SCALE = 1.10       # head group (Head, Jaw, Ears, Eyes, Nose) scaled about the chin/chest contact
HEAD_Q = Vector((0, -0.060, 0.135))
EXT_SCALE = 0.94       # hidden child band inside the parent

PART_ORDER = ['Pelvis', 'Spine1', 'Spine2', 'Neck1', 'Neck2', 'Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose',
              'FrontUpper.L', 'FrontLower.L', 'FrontFoot.L', 'FrontUpper.R', 'FrontLower.R', 'FrontFoot.R',
              'HindUpper.L', 'HindLower.L', 'HindFoot.L', 'HindUpper.R', 'HindLower.R', 'HindFoot.R',
              'Tail1', 'Tail2', 'Tail3']
FUR_PARTS = set(PART_ORDER) - {'Eye.L', 'Eye.R', 'Nose', 'Jaw', 'Ear.L', 'Ear.R'}
X = Vector((1, 0, 0)); Y = Vector((0, 1, 0)); Z = Vector((0, 0, 1))


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['PET-04', 'build'])[:2]


def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ngon_ring(c, e1, e2, r, n, phase=None, sy=1.0):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (sy * rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def ring_xyz(cen, w, ht, hb, n, ex, ey, pt=2.4, pb=2.4):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(cen + ex * (w * spow(c, 2 / p)) + ey * ((ht if s >= 0 else hb) * spow(s, 2 / p)))
    return out


def centroid(r):
    return sum(r, Vector()) / len(r)


def ext(ring, axis_into_parent, depth, scale=EXT_SCALE):
    """hidden child band end: the shared boundary ring shrunk and pushed `depth` into the parent"""
    c = centroid(ring); a = Vector(axis_into_parent).normalized()
    return [c + (p - c) * scale + a * depth for p in ring]


def mir(p):
    return Vector((-p.x, p.y, p.z))


# ---------------- model ----------------
class Model:
    def __init__(self):
        self.P = pc.Part('Kitten'); self.pivot = {}
        self.pl = self.P.bm.faces.layers.int.new('part')

    def loft(self, name, rings, col, cap0=None, cap1=None, ground=False):
        P = self.P; bm = P.bm
        R = [[bm.verts.new(p) for p in r] for r in rings]
        n = len(R[0]); faces = []
        for j in range(len(R) - 1):
            for k in range(n):
                k1 = (k + 1) % n
                a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
                for tri in ((a, b, c), (a, c, d)):
                    faces.append(P.face(list(tri), col(j, k) if callable(col) else col))
        if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(P.face(list(R[-1]), cap1))
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, ground))
        return R

    def cone(self, name, ring, apex, slot):
        P = self.P; bm = P.bm
        R = [bm.verts.new(p) for p in ring]; A = bm.verts.new(apex); n = len(R)
        faces = [P.face(R, slot)] + [P.face([R[(k + 1) % n], R[k], A], slot) for k in range(n)]
        for f in faces: f[self.pl] = PART_ORDER.index(name)
        P.comp.append((name, faces, False))


def build_body(M):
    rings = [ring_xyz(Vector((0, y, (zb + zt) / 2)), w, (zt - zb) / 2, (zt - zb) / 2, 10, X, Z, 2.6, 4.0)
             for y, w, zb, zt in BODY]   # (pt 2.6 top, pb 4.0 flat belly)
    for part, (i0, i1) in SPLIT.items():
        rs = rings[i0:i1 + 1]
        if part != 'Pelvis':     # child: shares its rear ring with the parent behind it, hidden band into the parent
            rs = rs + [ext(rs[-1], Y, 0.016)]
        M.loft(part, rs, GREY, GREY, GREY)
    M.pivot['Pelvis'] = Vector((0, 0.070, 0.125))
    M.pivot['Spine1'] = Vector((0, BODY[5][0], 0.125))
    M.pivot['Spine2'] = Vector((0, BODY[3][0], 0.125))


def build_neck(M):
    cs = [Vector((0, y, z)) for y, z in NECK_AXIS]
    rings = []
    for i, c in enumerate(cs):
        t = (cs[min(i + 1, 2)] - cs[max(i - 1, 0)]).normalized()
        _, e1, _ = pc.basis(t, (0, 1, 0))
        rings.append(ring_xyz(c, NECK_R, NECK_R * 0.9, NECK_R * 0.9, 6, X, e1))
    M.loft('Neck1', rings[0:2], GREY, GREY, GREY)
    t = (cs[1] - cs[0]).normalized()
    M.loft('Neck2', [ext(rings[1], -t, 0.010), rings[1], rings[2]], GREY, GREY, GREY)
    M.pivot['Neck1'] = cs[0].copy(); M.pivot['Neck2'] = cs[1].copy()


def build_head(M):
    rings = [ring_xyz(Vector((0, y, zc)), w, ht, hb, 12, X, Z, HEAD_PT, HEAD_PB) for y, w, zc, ht, hb in HEAD]
    M.loft('Head', rings, GREY, GREY, GREY)
    M.pivot['Head'] = Vector((0, NECK_AXIS[2][0], NECK_AXIS[2][1]))
    return list(M.P.comp[-1][1])


def bvh_of(faces):
    vs = list({v for f in faces for v in f.verts}); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def surf(bvh, target, d):
    d = Vector(d).normalized(); o = Vector(target) - d * 0.4
    hit = bvh.ray_cast(o, d)
    if hit[0] is None: raise RuntimeError(f'no hit at {target}')
    n = hit[1] if hit[1].dot(d) < 0 else -hit[1]
    return hit[0], n


def build_jaw(M):
    # muzzle wedge: V-shaped front (two cheek facets + centre crease), loft along Z, back half sunk into the face
    yc = -0.159
    prof = [(0.0, -0.021), (0.034, -0.009), (0.056, 0.006), (0.040, 0.034), (-0.040, 0.034), (-0.056, 0.006),
            (-0.034, -0.009)]
    rows = [(0.144, 0.74, 0.008), (0.168, 1.0, 0.0), (0.200, 0.86, 0.012)]     # z, scale, y push back
    rings = [[Vector((a * s, yc + b * s + dy, z)) for a, b in prof] for z, s, dy in rows]
    M.loft('Jaw', rings, GREY, GREY, GREY)
    M.pivot['Jaw'] = Vector((0, -0.120, 0.180))
    return list(M.P.comp[-1][1])


def build_face(M, head_faces, jaw_faces):
    bvh = bvh_of(head_faces)
    # eyes: dark 8-gon discs, 2.5 mm proud, flat on their facet
    hp, n = surf(bvh, (EYE_X, -0.25, EYE_Z), (-0.10, 1.0, 0.0))
    a = n.normalized()
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = hp if sx > 0 else mir(hp); ax = a if sx > 0 else mir(a)
        _, e1, e2 = pc.basis(ax, (0, 0, 1))
        M.cone('Eye' + sfx, ngon_ring(c + ax * 0.0025, e1, e2, EYE_R, 8, math.pi / 8), c - ax * 0.010, EYE)
        M.pivot['Eye' + sfx] = c.copy()
    # nose: dark inverted triangle on top of the muzzle crease
    bv2 = bvh_of(head_faces + jaw_faces)
    hp, n = surf(bv2, (0, -0.25, 0.193), (0, 1, 0))
    up = Z - n * Z.dot(n); up.normalize(); side = X
    tri = [Vector((0.0125, 0, 0.005)), Vector((-0.0125, 0, 0.005)), Vector((0, 0, -0.011))]
    ring = lambda off: [hp + n * off + side * p.x + up * p.z for p in tri]
    M.loft('Nose', [ring(-0.006), ring(0.004)], NOSE, NOSE, NOSE)
    M.pivot['Nose'] = hp.copy()
    # ears: big thick triangles, lighter inner dish framed by a grey rim, roots sunk into the skull
    hp, n = surf(bvh, (0.082, -0.084, 0.5), (0, 0, -1))
    u = Vector((0.55, 0.03, 1.0)).normalized()
    f = Vector((0.10, -1.0, 0.0)); f = (f - u * f.dot(u)).normalized()
    s = u.cross(f).normalized()
    if s.x < 0: s = -s
    prof = [(0.068, 0.0), (0.040, 0.015), (0.0, 0.002), (-0.040, 0.015), (-0.068, 0.0), (0.0, -0.046)]
    base = hp - u * 0.014
    rings = [[base + u * h + s * (pa * sc) + f * (pb * sc) for pa, pb in prof] for h, sc in ((0.0, 1.0), (0.070, 0.42), (0.104, 0.12))]
    for sfx, sx in (('.L', 1), ('.R', -1)):
        rr = rings if sx > 0 else [[mir(p) for p in r] for r in rings]
        M.loft('Ear' + sfx, rr, lambda j, k: EAR_IN if j == 0 and k in (1, 2) else GREY, GREY, GREY)
        M.pivot['Ear' + sfx] = hp.copy() if sx > 0 else mir(hp)


def build_legs(M):
    for sfx, sx in (('.L', 1), ('.R', -1)):
        for kind, (x, y) in (('Front', FRONT), ('Hind', HIND)):
            x *= sx
            def ring(z, r, xo=0.0, sy=1.0):
                return ngon_ring(Vector((x - sx * xo, y, z)), X, Y, r, 8, math.pi / 8, sy)
            top_r = 0.031 if kind == 'Front' else 0.033
            knee = ring(0.036, LEG_R)
            ankle = ring(0.018, LEG_R)
            up = [ring(0.120, top_r, 0.012, 1.1), ring(0.080, LEG_R * 1.03, 0.003), knee]
            lo = [ext(knee, Z, 0.012), knee, ankle]
            ft = [ext(ankle, Z, 0.010), ankle, ring(0.010, LEG_R * 1.11), ring(0.0, LEG_R * 1.08)]
            M.loft(kind + 'Upper' + sfx, up, GREY, GREY, GREY)
            M.loft(kind + 'Lower' + sfx, lo, GREY, GREY, GREY)
            M.loft(kind + 'Foot' + sfx, ft, lambda j, k: SOLE if j == 2 else GREY, GREY, SOLE, ground=True)
            M.pivot[kind + 'Upper' + sfx] = Vector((x, y, 0.110))
            M.pivot[kind + 'Lower' + sfx] = Vector((x, y, 0.036))
            M.pivot[kind + 'Foot' + sfx] = Vector((x, y, 0.018))


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

    def ring(s, r):
        c, t = tail_at(pts, S, s)
        _, e1, e2 = pc.basis(t, (1, 0, 0))
        return ngon_ring(c, e1, e2, r, 8, math.pi / 8)
    rad = lambda s: TAIL_R[0] + (TAIL_R[1] - TAIL_R[0]) * s / L
    s1, s2 = 0.40 * L, 0.70 * L
    R1 = ring(s1, rad(s1)); R2 = ring(s2, rad(s2))
    t1 = tail_at(pts, S, s1)[1]; t2 = tail_at(pts, S, s2)[1]
    M.loft('Tail1', [ring(0.0, rad(0.0)), ring(0.5 * s1, rad(0.5 * s1)), R1], GREY, GREY, GREY)
    M.loft('Tail2', [ext(R1, -t1, 0.010, 0.84), R1, R2], GREY, GREY, GREY)
    M.loft('Tail3', [ext(R2, -t2, 0.010, 0.84), R2, ring(0.5 * (s2 + L), rad(0.5 * (s2 + L))), ring(L, rad(L) * 0.92)],
           GREY, GREY, GREY)
    for nm, a in (('Tail1', 0.0), ('Tail2', s1), ('Tail3', s2)):
        M.pivot[nm] = tail_at(pts, S, a)[0]
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


def facet_shades(M):
    if not FACET_SHADES: return
    sl = M.P.slot; pl = M.pl
    fur = {PART_ORDER.index(n) for n in FUR_PARTS}
    for f in M.P.bm.faces:
        if f[pl] in fur and f[sl] == GREY:
            nz = f.normal.z
            if nz > 0.80: f[sl] = GREY_L
            elif nz < -0.55: f[sl] = GREY_D


def build_model():
    M = Model()
    build_body(M); build_neck(M)
    hf = build_head(M); jf = build_jaw(M); build_face(M, hf, jf)
    build_legs(M); tl = build_tail(M)
    bm = M.P.bm
    hg = ('Head', 'Jaw', 'Ear.L', 'Ear.R', 'Eye.L', 'Eye.R', 'Nose')
    hv = {v for nm, faces, _ in M.P.comp if nm in hg for f in faces for v in f.verts}
    for v in hv: v.co = HEAD_Q + (v.co - HEAD_Q) * HEAD_SCALE
    for k in hg[1:]: M.pivot[k] = HEAD_Q + (M.pivot[k] - HEAD_Q) * HEAD_SCALE   # Head pivot stays on the neck end
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    facet_shades(M)
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
        pa = me.attributes.get('part')
        print('  coplanar pairs (parts):', [(PART_ORDER[pa.data[i].value], PART_ORDER[pa.data[j].value]) for i, j in s] if pa else s)
        for i, j in s:
            for q in (i, j):
                pp = me.polygons[q]; print('    face', q, PART_ORDER[pa.data[q].value], tuple(round(c, 4) for c in pp.center), tuple(round(c, 3) for c in pp.normal), round(pp.area * 1e6, 2), 'mm2')
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def wpts(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


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
    print(f'TRIS total {tot} | target ~900, ceiling ~1400')
    pts = [p for o in obs.values() for p in wpts(o)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    bl = [p for nm in ('Pelvis', 'Spine1', 'Spine2', 'Head', 'Jaw') for p in wpts(obs[nm])]
    hd = wpts(obs['Head'])
    print(f'SIZE width x {hi[0]-lo[0]:.3f} length y {hi[1]-lo[1]:.3f} height z {hi[2]-lo[2]:.3f} | y {lo[1]:.3f}..{hi[1]:.3f} '
          f'min z {lo[2]:.5f} | nose->rump {max(p.y for p in bl) - min(p.y for p in bl):.3f} | back top '
          f'{max(p.z for p in wpts(obs["Pelvis"])):.3f} belly {min(p.z for p in wpts(obs["Spine1"])):.3f} | head w '
          f'{max(p.x for p in hd) - min(p.x for p in hd):.3f} h {max(p.z for p in hd) - min(p.z for p in hd):.3f} '
          f'crown {max(p.z for p in hd):.3f} | tail top {max(p.z for p in wpts(obs["Tail3"])):.3f}')
    print(f'COM (after shift) {tuple(round(c, 4) for c in M.com)} volume {M.vol*1000:.2f} L | geometry shift '
          f'{tuple(round(c, 4) for c in M.shift)} | tail length {M.tail_len:.3f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} mirror {chk["mirror"]:.6f} '
          f'worst gap {chk["gap"]} coplanar {cop} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), minz=lo[2])


VIEWS = [('ref', REF_VIEW), ('side', (1, 0, 0.06)), ('front', (0.0, -1, 0.10)), ('back', (-0.6, 1.0, 0.35)),
         ('top', (0.25, -0.3, 1.0))]


def check_render(B, tag='build'):
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    obs = list(B['obs'].values()); pts = rn.mesh_points(obs)
    tiles = []
    for _, view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Kitten_{tag}_sheet.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== PET-04 Kitten', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex'))
        obs = list(B['obs'].values())
        rn.preview(B['sc'], obs, os.path.join(CHECK, 'Kitten_look_warm.png'), view=REF_VIEW, fill=(0.62, 0.80))
        for nm, v in VIEWS[:4] + [('prev', PREVIEW_VIEW)]:
            rn.preview(B['sc'], obs, os.path.join(CHECK, f'Kitten_look_{nm}.png'), view=v, fill=(0.62, 0.80))
        sc = B['sc']; sc.render.resolution_x, sc.render.resolution_y = 1280, 800
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        os.makedirs(os.path.join(ART, 'Meshes'), exist_ok=True); os.makedirs(os.path.join(ART, 'Blend'), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        obs = list(B['obs'].values())
        rn.preview(B['sc'], obs, os.path.join(CHECK, 'warmup.png'), view=PREVIEW_VIEW, fill=(0.66, 0.82))
        rn.preview(B['sc'], obs, os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW, fill=(0.66, 0.82))
