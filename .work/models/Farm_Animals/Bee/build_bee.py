# build_bee.py - INS-01 Bee v2 (Farm Animals, skeleton I parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_bee.py -- INS-01 build|look|export
# build : parts + palette + checks + Workbench check sheet (reference tile first) and 128 px thumbnail (TEMP/FarmAnimals_check_bee)
# look  : build + EEVEE preview into TEMP (check only)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# v2 follows planning/FarmAnimals/references/INS-01.png. Structure from ../Chick/build_chick.py (helpers copied,
# shared modules imported read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Bee'
TAG = 'FarmAnimals_Bee'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\INS-01.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_bee')
PALETTE = ['#EDBA55', '#D29E3A', '#4B4342', '#3A3332',
           '#E7B04A', '#C99238', '#F2C462', '#DDAA48',
           '#4A2A20', '#E8ECEF', '#A9ADB0', '#4E4644',
           '#3E3735', '#F2E6C9', '#B5835A', '#6E9F4A']
(YEL, YEL_D, DRK, DRK_D, THX, THX_D, HEAD, HEAD_D, EYE, WING, WING_E, LEG, LEG_D) = range(13)
BUDGET = (600, 800)

# ---------------- design numbers (m), measured from the reference (see spec.md) ----------------
ZB = 0.0240                                                    # body axis height (standing, soles at z = 0)
HEAD_C, HEAD_R = Vector((0, -0.0200, ZB + 0.0010)), Vector((0.0145, 0.0130, 0.0140))
HEAD_RINGS = [24, 52, 80, 108, 136, 160]                       # 10-gon quad bands (large flat 4-sided facets), flat caps
THX_C, THX_R = Vector((0, -0.0020, ZB + 0.0004)), Vector((0.0122, 0.0115, 0.0122))
THX_RINGS = [30, 70, 110, 150]
ABD_A0, ABD_TILT, ABD_L = Vector((0, 0.0060, ZB + 0.0008)), 6.0, 0.0290
ABD_RMAX = (0.0145, 0.0134)
ABD_SLANT = 16.0                                               # stripe planes lean forward at the top (reference)
ABD_RINGS = [(0.00, 0.58), (0.10, 0.84), (0.175, 0.93), (0.25, 0.98), (0.40, 1.00), (0.475, 0.97), (0.55, 0.92),
             (0.70, 0.78), (0.775, 0.69), (0.85, 0.58), (0.95, 0.38)]
# 3 bold dark bands of 0.15 L (~0.18 of the visible abdomen) with equal 0.15 L yellow gaps, + dark tip cone (review round 4)
ABD_BANDS = [YEL, DRK, DRK, YEL, DRK, DRK, YEL, DRK, DRK, YEL]
ABD_N = 9                                                      # 9-gon, flat top (vertex at the bottom), keeps <= ~900 tris
STING_L = 0.0050                                               # tip cone apex beyond the last ring (dark tip + sting point)
EYE_YAW, EYE_ELEV, EYE_R, EYE_PROUD, EYE_DOME = 25.0, -2.0, 0.0032, 0.0007, 0.0000   # flush discs, +-25 deg, 0.22 x head dia
HEAD_YAW = 32.0                     # rest-pose head turn toward +X (bee's left) around the Head pivot (neck), see spec.md
HEAD_GROUP = ('Head', 'Eye.L', 'Eye.R', 'Antenna.L', 'Antenna.R')
ANT_BASE_DIR = Vector((0.30, -0.40, 0.86))                     # where the antenna leaves the head (from the head centre)
ANT_PTS = [(-0.0018, None), (0.0080, Vector((0.22, -0.12, 0.97))), (0.0072, Vector((0.62, -0.70, 0.05)))]
ANT_R, ANT_KNOB = 0.0010, 0.0015
# legs (+X side): hip inside the body, knee, foot on the ground; 6-gon, mitred knee, flat flared sole
LEG_SPEC = [('Leg_1', (0.0055, -0.0130, ZB - 0.0080), (0.0170, -0.0215, 0.0105), (0.0185, -0.0255, 0.0)),
            ('Leg_2', (0.0065, -0.0020, ZB - 0.0090), (0.0205, -0.0020, 0.0110), (0.0220, -0.0020, 0.0)),
            ('Leg_3', (0.0065, 0.0080, ZB - 0.0080), (0.0185, 0.0165, 0.0110), (0.0200, 0.0205, 0.0))]
LEG_RAD = (0.0030, 0.0027, 0.0032)                             # hip, knee, sole: ~5.8 mm = 0.15 x body top height
# wings: root, span direction, plane-normal target, length, stations (u fraction, v leading, v trailing)
WING_SPEC = [('WingFront', Vector((0.0040, -0.0060, ZB + 0.0090)), Vector((0.30, 0.70, 0.65)), Vector((0.70, -0.30, 0.65)), 0.046,
              [(0.00, -0.0016, 0.0016), (0.20, -0.0052, 0.0056), (0.48, -0.0072, 0.0078), (0.78, -0.0060, 0.0062),
               (1.00, -0.0014, 0.0018)]),
             ('WingBack', Vector((0.0045, 0.0005, ZB + 0.0075)), Vector((0.42, 0.80, 0.45)), Vector((0.60, -0.25, 0.76)), 0.030,
              [(0.00, -0.0013, 0.0013), (0.35, -0.0046, 0.0050), (0.75, -0.0042, 0.0046), (1.00, -0.0010, 0.0012)])]
WING_TE, WING_TR, WING_RIDGE = 0.00030, 0.00070, 0.42         # half thickness at the edges / ridge, ridge chord fraction


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['INS-01', 'build'])[:2]


V = lambda *a: Vector(a)
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def mirv(p):
    return Vector((-p.x, p.y, p.z))


def mir(rings):
    return [[mirv(p) for p in r] for r in rings]


# ---------------- faceted ball: rings zipped by angle (copied from the chick) + optional radial fuzz ----------------
def ball(P, cname, c, r, rings, slot_fn, fuzz=0.0):
    R, A = [], []
    for th, n, ph in rings:
        t = math.radians(th); vs = []; ang = []
        for k in range(n):
            a = ph + 360.0 * k / n; ang.append(a); f = math.radians(a)
            # fuzz: sin(5a) is +-1 and X-mirror symmetric on the phase-18 10-gons (lumps alternate around the ring)
            m = 1.0 + (fuzz * math.sin(5 * f) if (fuzz and n == 10 and abs(ph - 18) < 1e-6) else 0.0)
            vs.append(P.bm.verts.new(c + V(r.x * m * math.sin(t) * math.cos(f), r.y * m * math.sin(t) * math.sin(f), r.z * math.cos(t))))
        R.append(vs); A.append(ang)
    faces = []

    def add(vs):
        p = sum((v.co for v in vs), Vector()) / len(vs)
        faces.append(P.face(vs, slot_fn(p)))
    for j in range(len(R) - 1):
        a, b, aa, ab = R[j], R[j + 1], A[j], A[j + 1]; na, nb = len(a), len(b)
        i = k = 0
        while i < na or k < nb:
            nxa = aa[0] + 360.0 * (i + 1) / na if i < na else 1e9
            nxb = ab[0] + 360.0 * (k + 1) / nb if k < nb else 1e9
            if nxa <= nxb + 1e-6:
                add([a[i % na], a[(i + 1) % na], b[k % nb]]); i += 1
            else:
                add([a[i % na], b[(k + 1) % nb], b[k % nb]]); k += 1
    add(list(reversed(R[0]))); add(list(R[-1]))
    P.comp.append((cname, faces, False))
    return faces


def qball(P, cname, c, r, thetas, n, slot_fn, ph=0.0):
    """closed faceted ellipsoid of n-gon rings at the same phase: planar quad bands (large 4-sided facets) + flat n-gon
    caps (no pole fan). ph = 0 keeps a facet centred on the front and the ring X-mirror symmetric for n = 10."""
    R = []
    for th in thetas:
        t = math.radians(th)
        R.append([P.bm.verts.new(c + V(r.x * math.sin(t) * math.cos(math.radians(ph + 360.0 * k / n)),
                                       r.y * math.sin(t) * math.sin(math.radians(ph + 360.0 * k / n)), r.z * math.cos(t)))
                  for k in range(n)])
    faces = []

    def add(vs):
        p = sum((v.co for v in vs), Vector()) / len(vs)
        faces.append(P.face(vs, slot_fn(p)))
    for j in range(len(R) - 1):
        for k in range(n):
            add([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]])
    add(list(reversed(R[0]))); add(list(R[-1]))
    P.comp.append((cname, faces, False))
    return faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def ell_point(c, r, d):
    d = d.normalized(); k = 1.0 / math.sqrt((d.x / r.x) ** 2 + (d.y / r.y) ** 2 + (d.z / r.z) ** 2)
    return c + d * k


def tube_rings(pts, radii, n, ref, phase=0.0, flat_end=False):
    """rings along a polyline; interior rings mitred (tangent = mean of in/out directions, radius / cos(half bend))"""
    rings = []
    for i, p in enumerate(pts):
        if i == 0: t = (pts[1] - pts[0]).normalized(); k = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); k = 1.0
        else:
            d0 = (pts[i] - pts[i - 1]).normalized(); d1 = (pts[i + 1] - pts[i]).normalized()
            t = (d0 + d1).normalized(); k = 1.0 / max(0.5, t.dot(d1))
        _, e1, e2 = pc.basis(t, ref)
        ring = []
        for j in range(n):
            a = phase + 2 * math.pi * j / n
            # stretch only in the bend plane would be exact; uniform k keeps it simple (k <= 1.15 here)
            ring.append(p + e1 * (radii[i] * k * math.cos(a)) + e2 * (radii[i] * k * math.sin(a)))
        if flat_end and i == len(pts) - 1:
            ring = [v - t * (v.z / t.z) for v in ring]          # sole flat on z = 0
        rings.append(ring)
    return rings


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Bee')
    J = {}
    head_faces = qball(P, 'Head', HEAD_C, HEAD_R, HEAD_RINGS, 10, lambda p: HEAD_D if (p - HEAD_C).z < -0.6 * HEAD_R.z else HEAD)
    qball(P, 'Body', THX_C, THX_R, THX_RINGS, 10, lambda p: THX_D if (p - THX_C).z < -0.55 * THX_R.z else THX)
    J['Body'] = THX_C.copy()
    J['Head'] = V(0, THX_C.y - THX_R.y + 0.0020, ZB)
    P.bm.verts.index_update()
    bvh_head = bvh_of(head_faces)

    # abdomen: 8-gon (flat top) loft; ring planes lean forward at the top by ABD_SLANT = clean slanted stripes
    tl = math.radians(ABD_TILT); ax = V(0, math.cos(tl), -math.sin(tl)); up = X.cross(ax).normalized()
    if up.z < 0: up = -up
    sl = math.tan(math.radians(ABD_SLANT))
    angs = [math.radians(-90.0 + 360.0 * k / ABD_N) for k in range(ABD_N)]   # vertex at the bottom, flat top facet
    rings = []
    for t, s in ABD_RINGS:
        c = ABD_A0 + ax * (ABD_L * t)
        ring = []
        for a in angs:
            zl = ABD_RMAX[1] * s * math.sin(a)
            ring.append(c + X * (ABD_RMAX[0] * s * math.cos(a)) + up * zl - ax * (zl * sl * min(1.0, 4 * t)))
        rings.append(ring)

    def abd_slot(j, k):
        a = math.radians(-90.0 + 360.0 * (k + 0.5) / ABD_N)
        b = ABD_BANDS[j]
        return b + 1 if math.sin(a) < -0.6 else b
    R = P.loft('Abdomen', rings, abd_slot, YEL, None)
    # dark tip cone = stinger (deliberate point)
    tipc = sum((v.co for v in R[-1]), Vector()) / ABD_N
    apex = P.bm.verts.new(ABD_A0 + ax * (ABD_L * ABD_RINGS[-1][0] + STING_L) - up * 0.0008)
    cone_faces = [P.face([R[-1][k], R[-1][(k + 1) % ABD_N], apex], DRK) for k in range(ABD_N)]
    P.comp.append(('Abdomen', cone_faces, False))
    J['Abdomen'] = ABD_A0 + ax * 0.002

    # eyes: 8-gon dark dome, rim draped on the head facets, low centre bump, buried pyramid back
    yaw, el = math.radians(EYE_YAW), math.radians(EYE_ELEV)
    d = V(math.sin(yaw) * math.cos(el), -math.cos(yaw) * math.cos(el), math.sin(el))
    h = bvh_head.ray_cast(HEAD_C + d * 0.1, -d)
    hp, n = h[0], h[1]
    q = hp - HEAD_C
    if n.dot(q) < 0: n = -n
    n = (V(q.x / HEAD_R.x ** 2, q.y / HEAD_R.y ** 2, q.z / HEAD_R.z ** 2).normalized() + n).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    base = [hp + e1 * (EYE_R * math.cos(a)) + e2 * (EYE_R * math.sin(a)) for a in [math.pi / 8 + 2 * math.pi * k / 8 for k in range(8)]]

    def drape(p, extra=0.0):
        hh = bvh_head.ray_cast(p + n * 0.02, -n)
        return hh[0] + n * (EYE_PROUD + extra)
    ring = [drape(v) for v in base]; ctr = drape(hp, EYE_DOME); back = hp - n * 0.0030
    clear = []
    for i in range(8):
        for p in ((ring[i] + ring[(i + 1) % 8]) / 2, (ring[i] + ring[(i + 1) % 8] + ctr) / 3):
            hh = bvh_head.ray_cast(p + n * 0.02, -n); clear.append((hh[3] - 0.02) * 1000)
    print(f'EYE dome, clearance of eye edges/faces above the head facets min {min(clear):.2f} max {max(clear):.2f} mm')
    for nm, rg, c0, ap in (('Eye.L', ring, ctr, back), ('Eye.R', mir([ring])[0], mirv(ctr), mirv(back))):
        vs = [P.bm.verts.new(p) for p in rg]; vc = P.bm.verts.new(c0); va = P.bm.verts.new(ap)
        fs = [P.face([vs[k], vs[(k + 1) % 8], vc], EYE) for k in range(8)] + [P.face([vs[(k + 1) % 8], vs[k], va], EYE) for k in range(8)]
        P.comp.append((nm, fs, False)); J[nm] = c0.copy()

    # antennae: elbowed 5-gon tubes (up, then forward-out), club knob at the tip
    bp = ell_point(HEAD_C, HEAD_R, ANT_BASE_DIR)
    pts = [bp + ANT_BASE_DIR.normalized() * ANT_PTS[0][0]]
    cur = bp.copy()
    for L, dv in ANT_PTS[1:]:
        cur = cur + dv.normalized() * L; pts.append(cur.copy())
    e, tp = pts[-2], pts[-1]
    pts = pts[:-1] + [e + (tp - e) * 0.55, e + (tp - e) * 0.82, tp]       # single elbow, then a blunt round club
    ar = tube_rings(pts, [ANT_R, ANT_R, ANT_R, ANT_KNOB, ANT_KNOB * 0.75], 5, Y, math.pi / 2)
    P.loft('Antenna.L', ar, DRK, DRK, DRK); P.loft('Antenna.R', mir(ar), DRK, DRK, DRK)
    J['Antenna.L'] = bp.copy(); J['Antenna.R'] = mirv(bp)

    # legs: 6-gon hip -> knee -> flat flared sole; three separate pairs
    for nm, hip, knee, foot in LEG_SPEC:
        lr = tube_rings([V(*hip), V(*knee), V(*foot)], LEG_RAD, 6, Y, 0.0, flat_end=True)
        side = lambda j, k: LEG_D if k in (3, 4) else LEG
        P.loft(nm + '.L', lr, side, LEG, LEG_D); P.loft(nm + '.R', mir(lr), side, LEG, LEG_D)
        J[nm + '.L'] = V(*hip); J[nm + '.R'] = mirv(V(*hip))

    # wings: thin folded plates (lens section: edges 0.6 mm, ridge 1.4 mm), light faces + darker edge/vein strips
    trees = {}
    for nm, root, sdir, ntgt, L, st in WING_SPEC:
        s = sdir.normalized()
        nn = (ntgt - s * s.dot(ntgt)).normalized()                     # plane normal: broad face to side, front and top
        c = nn.cross(s).normalized()                                   # chord (+v = trailing edge)
        if c.z > 0: c = -c                                             # leading edge on top/front, trailing edge below
        wr = []
        for u, vl, vt in st:
            p0 = root + s * (u * L); vr = vl + WING_RIDGE * (vt - vl)
            tr = WING_TR if 0.0 < u < 1.0 else WING_TE
            wr.append([p0 + c * vl + nn * WING_TE, p0 + c * vr + nn * tr, p0 + c * vt + nn * WING_TE,
                       p0 + c * vt - nn * WING_TE, p0 + c * vr - nn * tr, p0 + c * vl - nn * WING_TE])
        side = lambda j, k: WING_E if k in (2, 5) else WING
        P.loft(nm + '.L', wr, side, WING_E, WING_E); P.loft(nm + '.R', mir(wr), side, WING_E, WING_E)
        J[nm + '.L'] = root.copy(); J[nm + '.R'] = mirv(root)
        pts_ = [p for r in wr for p in r]; m = len(wr[0])
        polys = [[j * m + k, j * m + (k + 1) % m, (j + 1) * m + (k + 1) % m, (j + 1) * m + k] for j in range(len(wr) - 1) for k in range(m)]
        trees[nm] = BVHTree.FromPolygons(pts_, polys)
    print('WING front/back plates intersect:', bool(trees['WingFront'].overlap(trees['WingBack'])))
    # head yaw group: built symmetric, mirror measured, then turned HEAD_YAW about Z around the Head pivot (neck joint)
    gv = sorted({v for nm, faces, _ in P.comp if nm in HEAD_GROUP for f in faces for v in f.verts}, key=lambda v: v.index)
    kd = kdtree.KDTree(len(gv))
    for i, v in enumerate(gv): kd.insert(v.co, i)
    kd.balance()
    J['_head_mirror'] = max(kd.find(Vector((-v.co.x, v.co.y, v.co.z)))[2] for v in gv)
    piv = J['Head']; M = Matrix.Rotation(math.radians(HEAD_YAW), 3, 'Z')
    for v in gv: v.co = piv + M @ (v.co - piv)
    for nm in HEAD_GROUP[1:]: J[nm] = piv + M @ (J[nm] - piv)
    return P, J


# ---------------- numbers ----------------
def com_of(bm):
    vol = 0.0; acc = Vector()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]; v = a.dot(b.cross(c)) / 6.0
            vol += v; acc += v * (a + b + c) / 4.0
    return acc / vol, vol


def tris_by_part(P):
    out = {}
    for nm, faces, _ in P.comp:
        out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in faces)
    return out


def split_to_objects(P, coll, mat, root, joints):
    groups = {}
    for nm, faces, _ in P.comp: groups.setdefault(nm, []).extend(faces)
    obs = {}
    for nm, faces in groups.items():
        piv = joints[nm]
        bm = bmesh.new(); sl = bm.faces.layers.int.new('slot'); vm = {}
        for f in faces:
            vs = []
            for v in f.verts:
                if v not in vm: vm[v] = bm.verts.new(v.co - piv)
                vs.append(vm[v])
            nf = bm.faces.new(vs); nf[sl] = f[P.slot]
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        uvl = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            f.smooth = False; uv = pc.cell_uv(f[sl])
            for lp in f.loops: lp[uvl].uv = uv
        me = bpy.data.meshes.new(ASSET + '_' + nm); bm.to_mesh(me); bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(nm, me); coll.objects.link(ob)
        ob.parent = root; ob.location = piv
        obs[nm] = ob
    return obs


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)     # factory-startup cube/light/camera
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    P, J = build_mesh()
    hm = J.pop('_head_mirror')
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    com, vol = com_of(P.bm)
    minz = min(v.co.z for v in P.bm.verts)
    sh = Vector((0, -com.y, -minz))                # root pivot = ground under the centre of mass, soles on z = 0
    for v in P.bm.verts: v.co += sh
    for k in J: J[k] = J[k] + sh
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1e6:.2f} cm3 -> shift {tuple(round(c, 4) for c in sh)}')
    chk = pc.comp_checks(P, mirror_skip=HEAD_GROUP)
    print(f'MIRROR head group before the {HEAD_YAW:.0f} deg yaw: {hm:.6f} (group {HEAD_GROUP} rotated as one rigid group)')
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_BeeAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_BeeAll', me)
    coll.objects.link(tmp); cop = pc.coplanar_overlaps(tmp)
    for a, b in cop[1]:
        print('   coplanar pair at', [tuple(round(c, 4) for c in me.polygons[i].center) for i in (a, b)])
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.02
    obs = split_to_objects(P, coll, mat, root, J)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target {BUDGET[0]}-{BUDGET[1]}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    body = [o.matrix_world @ v.co for k in ('Head', 'Body', 'Abdomen') for o in [obs[k]] for v in o.data.vertices]
    print(f'SIZE span(x) {hi[0]-lo[0]:.4f} length(y) {hi[1]-lo[1]:.4f} height(z) {hi[2]-lo[2]:.4f} | lowest z {lo[2]:.5f} | '
          f'body length head->stinger {max(p.y for p in body) - min(p.y for p in body):.4f} body width {max(p.x for p in body) - min(p.x for p in body):.4f}'
          f' body top {max(p.z for p in body):.4f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop[0]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop[0], tris=tri, total=tot)


REF_VIEW = (0.85, -1.0, 0.22)        # reference: bee faces image-left, we see its left (+X) side and the face, ~12 deg above
VIEWS = [REF_VIEW, (1, 0, 0.04), (0.0, -1, 0.10), (0.0, 1, 0.12), (0.15, 0.1, 1.0), (-0.8, 0.9, 0.45), (-0.9, -0.8, 0.3)]


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 600, 400)
    g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 400)] + tiles, 4, os.path.join(CHECK, f'Bee_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Bee_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


# ---------------- preview (copied from animal_render.preview: hover lift, shadow kept in frame, near clip) -------
PREVIEW_VIEW, PREVIEW_FILL, HOVER = (0.883, -0.469, 0.16), (0.76, 0.84), 0.010
PREVIEW_LENS = 50                          # side-front 3/4: 62 deg from the bee's forward axis, 9 deg above
SUN_ROT = (28, 0, -35)                     # steeper than the pack sun (48): the shadow stays under the hovering bee


def preview(sc, root, objs, out):
    root.location.z += HOVER; bpy.context.view_layer.update()
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    old_samples = sc.eevee.taa_render_samples; sc.eevee.taa_render_samples = 128
    w = bpy.data.worlds.new('TMP_PreviewWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    L = rn._lin
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (L('e3'), L('ec'), L('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (L('86'), L('b4'), L('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1)
    amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface'])
    old_world = sc.world; sc.world = w
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = 60.0
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(rn._solid_mat('TMP_Meadow_M', '#93AE6E'))
    gob = bpy.data.objects.new('TMP_Meadow', me); sc.collection.objects.link(gob)
    lights = []
    for nm, rot, e, shd in (('TMP_Sun', SUN_ROT, 3.6, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(3); ld.use_shadow = shd
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob); lights.append(ob)
    cam = rn.camera(sc, 'TMP_PrevCam', PREVIEW_LENS); cam.data.clip_start = 0.002
    pts = rn.mesh_points(objs)
    sd = (lights[0].matrix_world.to_3x3() @ V(0, 0, -1)).normalized()
    shadow = [p - sd * (p.z / sd.z) for p in pts]                     # shadow footprint on z = 0, kept in frame
    rn.fit(sc, cam, pts + shadow, PREVIEW_VIEW, PREVIEW_FILL)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights + [gob, cam]:
        d = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
        if isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
        elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    sc.world = old_world; bpy.data.worlds.remove(w); sc.eevee.taa_render_samples = old_samples
    root.location.z -= HOVER; bpy.context.view_layer.update()
    print('preview', out)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== INS-01 Bee', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(CHECK, 'Bee_look.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'))
