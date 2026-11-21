# build_butterfly.py - INS-02 Butterfly (Farm Animals, skeleton I parts, MESH ONLY: no armature/weights/clips). Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_butterfly.py -- INS-02 build|look|export
# build : parts + palette + checks + Workbench check sheet (reference tile first) + 128 px thumbnail (TEMP/FarmAnimals_check_butterfly)
# look  : build + EEVEE preview into TEMP (check only)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Follows planning/FarmAnimals/references/INS-02.png. Helpers copied from ../Bee/build_bee.py (shared modules read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Butterfly'
TAG = 'FarmAnimals_Butterfly'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\INS-02.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_butterfly')
PALETTE = ['#F57B1E', '#E86D18', '#3B302C', '#2C2421',
           '#F7832A', '#D9661C', '#2A1D17', '#F6F1E7',
           '#F28024', '#D56A1E', '#3A2F2C', '#2A221F',
           '#4A3C37', '#F2E6C9', '#B5835A', '#6E9F4A']
(WORG, WORG_B, BLK, BLK_D, HEAD, HEAD_D, EYE, DOT, ABO, ABO_D, LEG, LEG_D, ANT) = range(13)
BUDGET = (350, 450)
SPAN = 0.150                                                   # wingspan target (catalogue, enlarged)

# ---------------- design numbers (m), measured from the reference (see spec.md) ----------------
S = 1.0e-4                                                     # reference px -> m (wing layout)
THX_C, THX_R = Vector((0, 0.0040, 0.0285)), Vector((0.0118, 0.0135, 0.0132))
THX_RINGS = [40, 90, 140]
HEAD_C, HEAD_R = Vector((0, -0.0085, 0.0440)), Vector((0.0137, 0.0118, 0.0116))
HEAD_RINGS = [24, 58, 92, 126, 158]
ABD_A0, ABD_TILT, ABD_L = Vector((0, 0.0110, 0.0230)), 26.0, 0.0420
ABD_RMAX = (0.0080, 0.0078)
ABD_SLANT = 16.0
ABD_RINGS = [(0.00, 0.80), (0.15, 0.97), (0.31, 1.00), (0.45, 0.98), (0.61, 0.90), (0.77, 0.70)]
ABD_BANDS = [BLK, ABO, BLK, ABO, BLK]                          # dark with 2 orange bands + dark tip cone
ABD_N = 6
EYE_YAW, EYE_ELEV, EYE_R, EYE_PROUD, EYE_DOME, EYE_N = 29.0, 0.0, 0.0030, 0.0006, 0.0009, 6
ANT_DIR = Vector((0.50, -0.18, 0.85))                          # straight, up and out (reference)
ANT_BASE_DIR = Vector((0.36, -0.30, 0.88))                     # where it leaves the head (from the head centre)
ANT_L, ANT_R, ANT_KNOB, ANT_TIP = 0.0240, 0.0011, 0.0024, 0.0012
# legs (+X side): hip inside the thorax, knee out, vertical shin, flat sole on z = 0; 4-gon (square faces)
LEG_SPEC = [('Leg_1', (0.0035, -0.0020, 0.0200), (0.0135, -0.0090, 0.0150), (0.0140, -0.0105, 0.0)),
            ('Leg_2', (0.0050, 0.0035, 0.0185), (0.0150, 0.0035, 0.0145), (0.0155, 0.0040, 0.0)),
            ('Leg_3', (0.0040, 0.0075, 0.0195), (0.0135, 0.0105, 0.0150), (0.0140, 0.0115, 0.0))]
LEG_RAD = (0.0028, 0.0027, 0.0030)

# wings: px layout of the image-left (-X, .R) wings; a = (WPX0 - px) * S outward, b = (WPY0 - py) * S up in the plane
WPX0, WPY0 = 735, 600
WING_ROOT = Vector((0.0110, 0.0060, 0.0330))                   # (a, b) = (0, 0) in the body frame (.L side)
WING_TILT, WING_YAW = 30.0, 0.0                                # forewing plane leans back from vertical; no sweep (review 2)
HIND_TILT = -10.0                                              # hindwing plane: lower edge 10 deg back (abdomen shows below it)
WING_T = 0.0006                                                # half thickness (1.2 mm plate)
WING_DROOP = 0.0040                                            # tip bend back/down (quadratic in a)
HIND_BACK = 0.0055                                             # hindwing plate behind the forewing plate
FW_OUT = [(790, 520), (600, 300), (340, 100), (130, 45), (50, 135), (65, 265), (150, 475), (290, 555), (790, 605)]
FW_CELLS = [[(248, 155), (335, 108), (520, 262), (506, 312), (275, 222)],
            [(145, 230), (268, 245), (470, 420), (228, 405), (150, 352)],
            [(478, 326), (662, 428), (722, 562), (470, 425)],
            [(252, 455), (455, 442), (712, 583), (298, 553)]]
FW_DOTS = [(190, 102), (98, 190), (178, 425)]
HW_OUT = [(785, 612), (330, 580), (225, 625), (185, 690), (182, 752), (250, 838), (378, 855), (560, 770), (785, 668)]
HW_CELLS = [[(290, 645), (705, 628), (695, 665), (545, 762), (325, 828), (332, 762), (500, 662), (262, 750)]]
HW_DOTS = [(222, 742)]
DOT_PROUD = 0.0002
DOT_R, DOTS_BACK = 17, False                                   # dot half-size px; dots on the front face only


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['INS-02', 'build'])[:2]


V = lambda *a: Vector(a)
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def mirv(p):
    return Vector((-p.x, p.y, p.z))


def mir(rings):
    return [[mirv(p) for p in r] for r in rings]


def qball(P, cname, c, r, thetas, n, slot_fn, ph=0.0):
    """closed faceted ellipsoid of n-gon rings: planar quad bands + flat n-gon caps (no pole fan). (copied from the Bee)"""
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
    """rings along a polyline; interior rings mitred (copied from the Bee)"""
    rings = []
    for i, p in enumerate(pts):
        if i == 0: t = (pts[1] - pts[0]).normalized(); k = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); k = 1.0
        else:
            d0 = (pts[i] - pts[i - 1]).normalized(); d1 = (pts[i + 1] - pts[i]).normalized()
            t = (d0 + d1).normalized(); k = 1.0 / max(0.5, t.dot(d1))
        _, e1, e2 = pc.basis(t, ref)
        ring = [p + e1 * (radii[i] * k * math.cos(phase + 2 * math.pi * j / n)) + e2 * (radii[i] * k * math.sin(phase + 2 * math.pi * j / n))
                for j in range(n)]
        if flat_end and i == len(pts) - 1:
            ring = [v - t * (v.z / t.z) for v in ring]
        rings.append(ring)
    return rings


def poly_area(L):
    return 0.5 * abs(sum(L[i][0] * L[(i + 1) % len(L)][1] - L[(i + 1) % len(L)][0] * L[i][1] for i in range(len(L))))


# ---------------- wing layout: 2D scanfill of the border region with cell/dot holes ----------------
def wing_template(outline, cells, dots):
    """returns 2D coords (a, b), region triangles (index lists), loops (outline first, then cells, then dots)"""
    to_ab = lambda q: ((WPX0 - q[0]) * S, (WPY0 - q[1]) * S)
    Ls = [[to_ab(q) for q in outline]] + [[to_ab(q) for q in c] for c in cells]
    Ls += [[to_ab((x + dx, y + dy)) for dx, dy in ((0, -DOT_R), (DOT_R * 0.9, 0), (0, DOT_R), (-DOT_R * 0.9, 0))] for x, y in dots]
    bm = bmesh.new(); loops = []
    for L in Ls: loops.append([bm.verts.new((a, b, 0.0)) for a, b in L])
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for vs in loops for i in range(len(vs))]
    r = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es, normal=Vector((0, 0, 1)))
    region = [g for g in r['geom'] if isinstance(g, bmesh.types.BMFace)]
    bm.verts.index_update()
    area = sum(f.calc_area() for f in region)
    want = poly_area(Ls[0]) - sum(poly_area(L) for L in Ls[1:])
    if abs(area - want) > 1e-3 * want:
        raise RuntimeError(f'wing scanfill area {area:.6e} != outline - holes {want:.6e}')
    coords = [v.co.copy() for v in bm.verts]
    tris = [[v.index for v in f.verts] for f in region]
    idx = [[v.index for v in vs] for vs in loops]
    bm.free()
    # cells/dots: own 2D tessellation (concave cells, e.g. the hindwing wedge, triangulated in the plane, not after the bend)
    from mathutils.geometry import tessellate_polygon
    ctri = [(j, [L[i] for i in t]) for j, L in enumerate(idx[1:]) for t in tessellate_polygon([[coords[i] for i in L]])]
    return coords, tris, idx, ctri


def wing_frame(tilt=WING_TILT):
    e_out = V(math.cos(math.radians(WING_YAW)), math.sin(math.radians(WING_YAW)), 0)
    e_up = V(0, math.sin(math.radians(tilt)), math.cos(math.radians(tilt)))
    e_up = (e_up - e_out * e_out.dot(e_up)).normalized()
    n = e_out.cross(e_up).normalized()                         # plate normal (front: forward-up)
    return e_out, e_up, n


def build_wing(P, nm, outline, cells, dots, back, amax, tilt):
    e_out, e_up, n = wing_frame(tilt)
    tf = wing_template(outline, cells, dots)
    tb = wing_template(outline, cells, dots if DOTS_BACK else [])
    no, nc = len(outline), len(cells)

    def place(ab, side):
        a, b = ab.x, ab.y
        bend = WING_DROOP * (max(0.0, a) / amax) ** 2
        return WING_ROOT + e_out * a + e_up * b - n * (back + bend) + n * (side * WING_T)
    out = {}
    for sfx, mf in (('.L', lambda p: p), ('.R', mirv)):
        dotv = {i for L in tf[2][1 + nc:] for i in L}           # white dots stand 0.2 mm proud (never coplanar with the border)
        Fv = [P.bm.verts.new(mf(place(c, +1) + n * (DOT_PROUD if i in dotv else 0.0))) for i, c in enumerate(tf[0])]
        Bv = [P.bm.verts.new(mf(place(c, -1))) for c in tb[0]]
        fs = []
        for t in tf[1]: fs.append(P.face([Fv[i] for i in t], BLK))
        for t in tb[1]: fs.append(P.face([Bv[i] for i in reversed(t)], BLK))
        for j, t in tf[3]: fs.append(P.face([Fv[i] for i in t], WORG if j < nc else DOT))
        for j, t in tb[3]: fs.append(P.face([Bv[i] for i in reversed(t)], WORG_B if j < nc else DOT))
        O = tf[2][0]; Ob = tb[2][0]
        for i in range(no):
            k = (i + 1) % no
            fs.append(P.face([Fv[O[i]], Fv[O[k]], Bv[Ob[k]], Bv[Ob[i]]], BLK_D))
        P.comp.append((nm + sfx, fs, False))
        piv = WING_ROOT + e_up * (0.004 if nm == 'WingFront' else -0.003) - n * back
        out[nm + sfx] = mf(piv)
        out['_tree' + nm + sfx] = BVHTree.FromPolygons([v.co.copy() for v in Fv + Bv],
                                                     [[i for i in t] for t in tf[1]] + [[len(Fv) + i for i in t] for t in tb[1]])
    return out


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Butterfly')
    J = {}
    # thorax (dark) + abdomen = Body
    body_faces = qball(P, 'Body', THX_C, THX_R, THX_RINGS, 8, lambda p: BLK_D if (p - THX_C).z < -0.5 * THX_R.z else BLK, ph=22.5)
    J['Body'] = THX_C.copy()
    tl = math.radians(ABD_TILT); ax = V(0, math.cos(tl), -math.sin(tl)); up = X.cross(ax).normalized()
    if up.z < 0: up = -up
    sl = math.tan(math.radians(ABD_SLANT))
    angs = [math.radians(360.0 * k / ABD_N) for k in range(ABD_N)]
    rings = []
    for t, s in ABD_RINGS:
        c = ABD_A0 + ax * (ABD_L * t)
        ring = []
        for a in angs:
            zl = ABD_RMAX[1] * s * math.sin(a)
            ring.append(c + X * (ABD_RMAX[0] * s * math.cos(a)) + up * zl - ax * (zl * sl * min(1.0, 4 * t)))
        rings.append(ring)

    def abd_slot(j, k):
        a = math.radians(360.0 * (k + 0.5) / ABD_N); b = ABD_BANDS[j]
        return (b + 1) if (math.sin(a) < -0.6 and b == ABO) else (BLK_D if math.sin(a) < -0.6 else b)
    R = P.loft('Body', rings, abd_slot, BLK, None)
    apex = P.bm.verts.new(ABD_A0 + ax * ABD_L - up * 0.0010)
    P.comp.append(('Body', [P.face([R[-1][k], R[-1][(k + 1) % ABD_N], apex], BLK) for k in range(ABD_N)], False))

    # head (orange faceted ball)
    head_faces = qball(P, 'Head', HEAD_C, HEAD_R, HEAD_RINGS, 10, lambda p: HEAD_D if (p - HEAD_C).z < -0.55 * HEAD_R.z else HEAD, ph=0.0)
    J['Head'] = V(0, HEAD_C.y + 0.004, HEAD_C.z - 0.008)
    P.bm.verts.index_update()
    bvh_head = bvh_of(head_faces)

    # eyes: dark 6-gon domes draped on the head facets, buried pyramid back (Bee method)
    yaw, el = math.radians(EYE_YAW), math.radians(EYE_ELEV)
    d = V(math.sin(yaw) * math.cos(el), -math.cos(yaw) * math.cos(el), math.sin(el))
    h = bvh_head.ray_cast(HEAD_C + d * 0.1, -d)
    hp, n = h[0], h[1]
    q = hp - HEAD_C
    if n.dot(q) < 0: n = -n
    n = (V(q.x / HEAD_R.x ** 2, q.y / HEAD_R.y ** 2, q.z / HEAD_R.z ** 2).normalized() + n).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    base = [hp + e1 * (EYE_R * math.cos(a)) + e2 * (EYE_R * math.sin(a)) for a in [math.pi / EYE_N + 2 * math.pi * k / EYE_N for k in range(EYE_N)]]

    def drape(p, extra=0.0):
        hh = bvh_head.ray_cast(p + n * 0.02, -n)
        return hh[0] + n * (EYE_PROUD + extra)
    ring = [drape(v) for v in base]; ctr = drape(hp, EYE_DOME); back = hp - n * 0.0030
    clear = []
    for i in range(EYE_N):
        for p in ((ring[i] + ring[(i + 1) % EYE_N]) / 2, (ring[i] + ring[(i + 1) % EYE_N] + ctr) / 3):
            hh = bvh_head.ray_cast(p + n * 0.02, -n); clear.append((hh[3] - 0.02) * 1000)
    print(f'EYE dome clearance above the head facets min {min(clear):.2f} max {max(clear):.2f} mm')
    for nm, rg, c0, ap in (('Eye.L', ring, ctr, back), ('Eye.R', mir([ring])[0], mirv(ctr), mirv(back))):
        vs = [P.bm.verts.new(p) for p in rg]; vc = P.bm.verts.new(c0); va = P.bm.verts.new(ap)
        fs = [P.face([vs[k], vs[(k + 1) % EYE_N], vc], EYE) for k in range(EYE_N)] + \
             [P.face([vs[(k + 1) % EYE_N], vs[k], va], EYE) for k in range(EYE_N)]
        P.comp.append((nm, fs, False)); J[nm] = c0.copy()

    # antennae: straight 4-gon stalks with a club
    bp = ell_point(HEAD_C, HEAD_R, ANT_BASE_DIR); dv = ANT_DIR.normalized()
    pts = [bp - dv * 0.0020, bp + dv * (ANT_L * 0.66), bp + dv * (ANT_L * 0.84), bp + dv * ANT_L]
    ar = tube_rings(pts, [ANT_R, ANT_R, ANT_KNOB, ANT_TIP], 4, Y, math.pi / 4)
    P.loft('Antenna.L', ar, ANT, ANT, ANT); P.loft('Antenna.R', mir(ar), ANT, ANT, ANT)
    J['Antenna.L'] = bp.copy(); J['Antenna.R'] = mirv(bp)

    # legs: hip -> knee -> flat sole, 4-gon
    for nm, hip, knee, foot in LEG_SPEC:
        lr = tube_rings([V(*hip), V(*knee), V(*foot)], LEG_RAD, 4, Y, math.pi / 4, flat_end=True)
        side = lambda j, k: LEG_D if k == 2 else LEG
        P.loft(nm + '.L', lr, side, LEG, LEG_D); P.loft(nm + '.R', mir(lr), side, LEG, LEG_D)
        J[nm + '.L'] = V(*hip); J[nm + '.R'] = mirv(V(*hip))

    # wings
    amax = max((WPX0 - x) * S for x, _ in FW_OUT)
    W = build_wing(P, 'WingFront', FW_OUT, FW_CELLS, FW_DOTS, 0.0, amax, WING_TILT)
    W.update(build_wing(P, 'WingBack', HW_OUT, HW_CELLS, HW_DOTS, HIND_BACK, amax, HIND_TILT))
    for k, v in W.items():
        if not k.startswith('_tree'): J[k] = v
    for s in ('.L', '.R'):
        print(f'WING{s} front/back plates intersect:', bool(W['_treeWingFront' + s].overlap(W['_treeWingBack' + s])))
    P.bm.verts.index_update()
    hb = bvh_of(head_faces)
    for s in ('.L', '.R'):
        print(f'WINGFRONT{s} intersects head:', bool(W['_treeWingFront' + s].overlap(hb)))
    return P, J


# ---------------- numbers ----------------
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
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    xs = [v.co.x for v in P.bm.verts]; K = SPAN / (max(xs) - min(xs))
    for v in P.bm.verts: v.co *= K                 # uniform scale: wingspan exactly SPAN (layout measured in ref px)
    for k in J: J[k] = J[k] * K
    print(f'SCALE uniform K {K:.4f}')
    minz = min(v.co.z for v in P.bm.verts)
    sh = Vector((0, -THX_C.y * K, -minz))              # root pivot = ground under the thorax (body) centre, soles on z = 0
    for v in P.bm.verts: v.co += sh
    for k in J: J[k] = J[k] + sh
    chk = pc.comp_checks(P)
    seen = {}
    for f in P.bm.faces: seen.setdefault(frozenset(v.index for v in f.verts), []).append(f.index)
    dup = sum(1 for v in seen.values() if len(v) > 1)
    print(f'DUPLICATE faces (same vertex set) {dup}')
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_BflyAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_BflyAll', me)
    coll.objects.link(tmp); cop = pc.coplanar_overlaps(tmp)
    from mathutils.geometry import intersect_tri_tri_2d
    real = 0
    for a, b in cop[1]:
        pa, pb = me.polygons[a], me.polygons[b]
        _, e1, e2 = pc.basis(pa.normal, (0, 0, 1) if abs(pa.normal.z) < 0.9 else (1, 0, 0))
        to2 = lambda poly: [Vector(((me.vertices[i].co).dot(e1), (me.vertices[i].co).dot(e2))) for i in poly.vertices]
        A2, B2 = to2(pa), to2(pb)
        ov = any(intersect_tri_tri_2d(A2[0], A2[i], A2[i + 1], B2[0], B2[j], B2[j + 1])
                 for i in range(1, len(A2) - 1) for j in range(1, len(B2) - 1))
        real += 1 if ov else 0
        print('   coplanar pair at', [tuple(round(c, 4) for c in me.polygons[i].center) for i in (a, b)],
              'normals dot', round(pa.normal.dot(pb.normal), 4), 'areas overlap', ov)
    print(f'COPLANAR flagged {cop[0]} of which really overlapping {real}')
    for v in me.vertices: v.co *= 10.0             # x10 copy: the coplanar eps (0.1 mm) is coarse at insect scale
    me.update(); cop10 = pc.coplanar_overlaps(tmp)
    print(f'COPLANAR x10 copy {cop10[0]}')
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.03
    obs = split_to_objects(P, coll, mat, root, J)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target {BUDGET[0]}-{BUDGET[1]}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    body = [o.matrix_world @ v.co for k in ('Head', 'Body') for o in [obs[k]] for v in o.data.vertices]
    print(f'SIZE span(x) {hi[0]-lo[0]:.4f} (target {SPAN}) length(y) {hi[1]-lo[1]:.4f} height(z) {hi[2]-lo[2]:.4f} | lowest z {lo[2]:.5f} | '
          f'body length head->tip {max(p.y for p in body) - min(p.y for p in body):.4f} body top {max(p.z for p in body):.4f}')
    bz = min((obs['Body'].matrix_world @ v.co).z for v in obs['Body'].data.vertices)
    wz = min((o.matrix_world @ v.co).z for k, o in obs.items() if k.startswith('Wing') for v in o.data.vertices)
    print(f'CLEARANCE abdomen lowest z {bz:.4f} | wings lowest z {wz:.4f} | legs carry z = 0')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop[0]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop[0], tris=tri, total=tot, dup=dup)


REF_VIEW = (-0.33, -1.0, 0.26)       # reference: near-frontal from the butterfly's front-right (-X), ~15 deg above
VIEWS = [REF_VIEW, (1, 0, 0.04), (0.0, -1, 0.10), (0.0, 1, 0.12), (0.1, 0.15, 1.0), (-0.8, 0.9, 0.45), (0.9, -0.8, 0.5)]


def view_numbers(sc, cam, obs, label):
    """screen area of each wing pair (projected triangles, front-most not resolved) and abdomen-tip visibility by ray cast"""
    from bpy_extras.object_utils import world_to_camera_view
    asp = sc.render.resolution_x / sc.render.resolution_y
    def area(names):
        A = 0.0
        for nm in names:
            o = obs[nm]; P2 = [world_to_camera_view(sc, cam, o.matrix_world @ v.co) for v in o.data.vertices]
            for p in o.data.polygons:
                a_, b_, c_ = (P2[i] for i in p.vertices)
                A += abs((b_.x - a_.x) * (c_.y - a_.y) - (c_.x - a_.x) * (b_.y - a_.y)) * 0.5 * asp
        return A / 2                                            # front + back sheet both project
    aL, aR = area(['WingFront.L', 'WingBack.L']), area(['WingFront.R', 'WingBack.R'])
    dg = bpy.context.evaluated_depsgraph_get(); o = obs['Body']
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    tail = sorted(vs, key=lambda q: -q.y)[:14]                 # rear 14 verts of the abdomen (last bands + tip)
    vis = 0
    for q in tail:
        d = (cam.matrix_world.translation - q); L = d.length; d.normalize()
        hit = sc.ray_cast(dg, q + d * 0.0005, d, distance=L)
        vis += 0 if hit[0] else 1
    print(f'VIEW {label}: wing pair screen area L {aL:.4f} R {aR:.4f} ratio {min(aL, aR) / max(aL, aR):.2f} | '
          f'abdomen rear verts visible {vis}/{len(tail)}')


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 600, 400)
    g = rn.ground(sc); cam = rn.camera(sc); cam.data.clip_start = 0.002; cam.data.lens = PREVIEW_LENS
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        if view == REF_VIEW: view_numbers(sc, cam, B['obs'], 'ref')
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 400)] + tiles, 4, os.path.join(CHECK, f'Butterfly_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Butterfly_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


# pack-standard preview (review round 3): low 3/4 front-left, ~12 deg above the ground, horizon + sky, 40 mm, standard sun/fill
STD_VIEW, STD_FILL, STD_LENS = (0.34, -1.0, 0.18), (0.80, 0.84), 40


# ---------------- preview (copied from the Bee: hover lift, shadow kept in frame, near clip) ----------------
PREVIEW_VIEW, PREVIEW_FILL, HOVER = (-0.55, -1.0, 0.14), (0.80, 0.86), 0.015
SUN_ROT = (26, 0, -30)
PREVIEW_LENS = 120                         # long lens: near and far wing pairs read at a similar size


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
    shadow = [p - sd * (p.z / sd.z) for p in pts]
    rn.fit(sc, cam, pts + shadow, PREVIEW_VIEW, PREVIEW_FILL)
    view_numbers(sc, cam, {o.name: o for o in objs}, 'preview')
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
    print('=== INS-02 Butterfly', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'probe':                                        # numbers only: wing pair size ratio + abdomen visibility
        B = build(os.path.join(CHECK, 'tex')); sc = B['sc']
        sc.render.resolution_x, sc.render.resolution_y = 1280, 800
        cam = rn.camera(sc, 'TMP_Probe', PREVIEW_LENS); cam.data.clip_start = 0.002
        pts = rn.mesh_points(list(B['obs'].values()))
        for vw in [(-0.36, -1, 0.26), (-0.45, -1, 0.16), (-0.55, -1, 0.12), (-0.70, -1, 0.12), (-0.55, -1, 0.06), (-0.70, -1, 0.06)]:
            rn.fit(sc, cam, pts, vw, PREVIEW_FILL); view_numbers(sc, cam, B['obs'], str(vw))
    elif CMD in ('std_look', 'std_preview'):                    # pack-standard preview (animal_render.preview: 40 mm, low 3/4, sky + horizon)
        B = build(os.path.join(CHECK, 'tex')); sc = B['sc']; objs = list(B['obs'].values())
        sc.render.resolution_x, sc.render.resolution_y = 1280, 800
        cam = rn.camera(sc, 'TMP_Probe', STD_LENS); cam.data.clip_start = 0.002
        rn.fit(sc, cam, rn.mesh_points(objs), STD_VIEW, STD_FILL); view_numbers(sc, cam, B['obs'], 'std preview')
        bpy.data.objects.remove(cam, do_unlink=True)
        os.makedirs(CHECK, exist_ok=True)
        out = os.path.join(ART, ASSET + '_Preview.png') if CMD == 'std_preview' else os.path.join(CHECK, 'Butterfly_std_look.png')
        rn.preview(sc, objs, out, view=STD_VIEW, fill=STD_FILL, lens=STD_LENS)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(CHECK, 'Butterfly_look.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'))
