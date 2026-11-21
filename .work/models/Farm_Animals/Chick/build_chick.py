# build_chick.py - BRD-03 Chick (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_chick.py -- BRD-03 build|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_chick)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Hen/build_hen.py (helpers copied, shared modules imported read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Chick'
TAG = 'FarmAnimals_Chick'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-03.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_chick')
REF_VIEW = (0.40, -1.0, 0.14)        # reference: near-front, chick yawed ~22 deg to its right (we see its left, +X side)
PALETTE = ['#D8B65A', '#C9A64E', '#E6C870', '#C8A048',
           '#B8933F', '#EE8A2A', '#C8681A', '#EE8A2A',
           '#C8681A', '#2A1D17', '#F2E6C9', '#B5835A',
           '#7A5233', '#C8473B', '#6E9F4A', '#8E959B']
(BODY, BODY_D, BODY_L, WING, WING_D, BEAK, BEAK_D, LEG, LEG_D, EYE) = range(10)
BUDGET = 350

# ---------------- design numbers (m) ----------------
HEAD_C, HEAD_R = Vector((0, -0.012, 0.103)), Vector((0.054, 0.050, 0.047))
BODY_C, BODY_R = Vector((0, 0.004, 0.046)), Vector((0.042, 0.042, 0.040))
# rings: (theta deg from +Z, vertex count, phase deg). Staggered 10-gons + pentagon caps = geodesic-like facets, no pole fan.
HEAD_RINGS = [(22, 5, 18), (52, 10, 18), (82, 10, 0), (112, 10, 18), (142, 10, 0), (164, 5, 18)]
BODY_RINGS = [(30, 10, 18), (65, 10, 0), (98, 10, 18), (130, 10, 0), (160, 5, 18)]
NECK = [(0.060, 0.000, 0.034), (0.074, -0.008, 0.034)]          # (z, y centre, apothem), 8-gon
EYE_X, EYE_Z, EYE_R, EYE_PROUD = 0.024, 0.095, 0.0065, 0.0009
BEAK_Z, BEAK_HW, BEAK_UP, BEAK_DN, BEAK_L, BEAK_LL = 0.084, 0.0082, 0.0082, 0.0072, 0.014, 0.0098
BEAK_DIR = Vector((0, -0.93, -0.36)).normalized()
LEG_X, LEG_Y = 0.016, -0.004
LEG_R0, LEG_R1, LEG_TOP, LEG_BOT = 0.0045, 0.0040, 0.022, 0.0005
TOES = [(0, 0.014), (40, 0.012), (-40, 0.012)]                   # (yaw deg from forward towards outside, length)
TAIL_A, TAIL_B = Vector((0, 0.030, 0.058)), Vector((0, 0.056, 0.074))
# wings: sections along y (y, z centre, half height, proud)
WING_UP = [(-0.014, 0.045, 0.007, 0.0010), (-0.004, 0.044, 0.010, 0.0030)]
WING_LO = [(-0.010, 0.044, 0.012, 0.0042), (0.008, 0.040, 0.015, 0.0065), (0.026, 0.032, 0.006, 0.0030)]

JOINTS = {
    'Body': (0, 0.004, 0.046), 'Neck': (0, -0.002, 0.060), 'Head': (0, -0.010, 0.074),
    'Beak_Lower': (0, -0.058, BEAK_Z), 'WingUpper.L': (0.038, -0.014, 0.044), 'WingLower.L': (0.040, -0.008, 0.043),
    'TailFan1': tuple(TAIL_A),
    'LegUpper.L': (LEG_X, LEG_Y, 0.030), 'LegLower.L': (LEG_X, LEG_Y, LEG_TOP), 'Foot.L': (LEG_X, LEG_Y, 0.002),
}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-03', 'build'])[:2]


V = lambda *a: Vector(a)


# ---------------- helpers (copied from the hen) ----------------
def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ring_frame(c, ax, ay, w, ht, hb, n, p=2.4):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; co, si = math.cos(th), math.sin(th)
        out.append(c + ax * (w * spow(co, 2 / p)) + ay * ((ht if si >= 0 else hb) * spow(si, 2 / p)))
    return out


def ngon_ring(c, e1, e2, r, n, phase=None):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def mir(rings):
    return [[Vector((-p.x, p.y, p.z)) for p in r] for r in rings]


def cone(P, ring, apex, slot):
    """closed pyramid: flat n-gon disc + triangles to a buried apex; returns its faces"""
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def tetra(P, pts, slot):
    vs = [P.bm.verts.new(p) for p in pts]
    return [P.face([vs[i] for i in f], slot) for f in ((0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0))]


# ---------------- faceted ball: rings zipped by angle ----------------
def ball(P, cname, c, r, rings, slot_fn):
    """closed faceted ellipsoid; rings (theta deg, n, phase deg); neighbouring rings are zipped by angle (staggered
    10-gons -> triangle strips, pentagon -> 10-gon -> 3 tris per pentagon edge); the end rings are flat n-gon caps."""
    R, A = [], []
    for th, n, ph in rings:
        t = math.radians(th); vs = []; ang = []
        for k in range(n):
            a = ph + 360.0 * k / n; ang.append(a); f = math.radians(a)
            vs.append(P.bm.verts.new(c + V(r.x * math.sin(t) * math.cos(f), r.y * math.sin(t) * math.sin(f), r.z * math.cos(t))))
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


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Chick')
    body_slot = lambda p: BODY_D if (p - BODY_C).z < -0.6 * BODY_R.z else BODY
    body_faces = ball(P, 'Body', BODY_C, BODY_R, BODY_RINGS, body_slot)
    head_faces = ball(P, 'Head', HEAD_C, HEAD_R, HEAD_RINGS, lambda p: BODY)
    X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    # neck: 8-gon frustum filling the crease between the two balls (ends buried in body and head)
    P.loft('Neck', [ngon_ring(V(0, y, z), X, Y, r, 8) for z, y, r in NECK], BODY, BODY, BODY)

    def bvh_of(faces):
        vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])
    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def hit(bvh, o, d):
        h = bvh.ray_cast(o, d)
        if h[0] is None: raise RuntimeError(f'no surface hit from {tuple(o)}')
        return h[0], h[1]
    # eyes: 8-gon dark discs EYE_PROUD proud of the facet, pyramid back buried in the head
    hp, n = hit(bvh_head, V(EYE_X, -1.0, EYE_Z), V(0, 1, 0))
    q = hp - HEAD_C
    if n.dot(q) < 0: n = -n                                   # BVH normals follow the raw winding
    n = (V(q.x / HEAD_R.x ** 2, q.y / HEAD_R.y ** 2, q.z / HEAD_R.z ** 2).normalized() + n).normalized()   # smooth+facet
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    base = ngon_ring(hp, e1, e2, EYE_R, 8)
    # lowest disc vertex EYE_PROUD above the facets (no edge sinks in, no big float)
    hts = [bvh_head.ray_cast(v + n * 0.02, -n)[3] - 0.02 for v in base + [hp]]
    off = EYE_PROUD + max(hts)          # hts = -(height above the facets)
    ring = [v + n * off for v in base]; apex = hp - n * 0.007
    print(f'EYE disc offset {off * 1000:.2f} mm, heights above facets {[round(-h * 1000, 2) for h in hts]} mm')
    eyes = {}
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], V(-apex.x, apex.y, apex.z))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False)); eyes[nm] = sum(rg, Vector()) / len(rg)
    # beak: upper tetrahedron (Head) + lower tetrahedron (Beak_Lower) 1 mm below the mouth plane
    bp, _ = hit(bvh_head, V(0, -1.0, BEAK_Z), V(0, 1, 0))
    d = BEAK_DIR; up = X.cross(d).normalized()
    if up.z < 0: up = -up
    back = bp - d * 0.004
    T, L, R_, A = back + up * BEAK_UP, back - X * BEAK_HW, back + X * BEAK_HW, bp + d * BEAK_L
    P.comp.append(('Head', tetra(P, [L, R_, A, T], BEAK), False))
    dn = up * 0.001
    B, A2 = back - up * BEAK_DN, bp + d * BEAK_LL - dn
    P.comp.append(('Beak_Lower', tetra(P, [R_ - dn - X * 0.0005, L - dn + X * 0.0005, A2, B], BEAK_D), False))
    JOINTS['Beak_Lower'] = tuple(back)

    # wings: triangle sections hugging the body side (top/bottom tucked 1 mm, middle proud)
    def side_x(y, z):
        h = bvh_body.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if h[0] is None: raise RuntimeError(f'no body hit at y {y} z {z}')
        return h[0].x

    def wing_rings(spec):
        # smooth lens: tucked points 3 mm inside the ellipsoid (always under the facets), ridge pr outside it
        ex = lambda y, z: BODY_R.x * math.sqrt(max(0.0, 1 - ((y - BODY_C.y) / BODY_R.y) ** 2 - ((z - BODY_C.z) / BODY_R.z) ** 2))
        return [[V(ex(y, zc + h) - 0.003, y, zc + h), V(ex(y, zc - 0.3 * h) + pr, y, zc - 0.3 * h), V(ex(y, zc - h) - 0.003, y, zc - h)]
                for y, zc, h, pr in spec]
    for nm, spec, slot in (('WingUpper', WING_UP, WING), ('WingLower', WING_LO, WING)):
        r = wing_rings(spec)
        P.loft(nm + '.L', r, slot, slot, slot); P.loft(nm + '.R', mir(r), slot, slot, slot)

    for sx in (1, -1):
        h = bvh_body.ray_cast(V(sx * LEG_X, LEG_Y, 0.0), V(0, 0, 1))
        print(f'LEG exit z {h[0].z:.4f} (visible leg incl. toes)')
    # tail nub: diamond section, root buried in the upper back
    dv = (TAIL_B - TAIL_A).normalized(); tu = X.cross(dv).normalized()
    if tu.z < 0: tu = -tu
    P.loft('TailFan1', [ring_frame(TAIL_A.lerp(TAIL_B, t), X, tu, w, h, h, 4, 2.0)
                        for t, w, h in [(0.0, 0.008, 0.007), (1.0, 0.005, 0.0035)]], BODY, BODY, BODY)

    # legs: hidden thigh prism, 6-gon shank, 3 toes with sloped soles (no coplanar soles)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, 0.0030, 3, math.pi / 2) for z in (0.034, 0.018)], LEG, LEG, LEG)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6, 0.0) for z, r in [(LEG_TOP, LEG_R0), (LEG_BOT, LEG_R1)]],
               LEG, LEG, LEG)
        base = c(0.0)
        for yaw, Lt in TOES:
            a = math.radians(yaw); fw = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-fw.y, fw.x, 0)
            r0 = base - fw * 0.002; r1 = base + fw * Lt
            toe = [[r0 + sd * 0.0035 + V(0, 0, 0.0009), r0 - sd * 0.0035 + V(0, 0, 0.0009), r0 + V(0, 0, 0.0056)],
                   [r1 + sd * 0.0021, r1 - sd * 0.0021, r1 + V(0, 0, 0.0027)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, eyes


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


def joint(nm):
    if nm in JOINTS: return Vector(JOINTS[nm])
    base = nm[:-2] + '.L'
    if nm.endswith('.R') and base in JOINTS:
        j = Vector(JOINTS[base]); return Vector((-j.x, j.y, j.z))
    return None


def split_to_objects(P, coll, mat, root, eye_centres):
    groups = {}
    for nm, faces, _ in P.comp: groups.setdefault(nm, []).extend(faces)
    obs = {}
    for nm, faces in groups.items():
        piv = joint(nm) if joint(nm) is not None else eye_centres[nm]
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
    P, eyes = build_mesh()
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    com, vol = com_of(P.bm)
    sh = Vector((0, -com.y, 0))                    # root pivot = ground under the centre of mass
    for v in P.bm.verts: v.co += sh
    for k in JOINTS: JOINTS[k] = tuple(Vector(JOINTS[k]) + sh)
    for k in eyes: eyes[k] = eyes[k] + sh
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1e6:.1f} cm3 -> shifted y by {sh.y:+.4f}')
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_ChickAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_ChickAll', me)
    coll.objects.link(tmp); cop = pc.coplanar_overlaps(tmp)
    for a, b in cop[1]:
        print('   coplanar pair at', [tuple(round(c, 4) for c in me.polygons[i].center) for i in (a, b)])
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.05
    obs = split_to_objects(P, coll, mat, root, eyes)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target {BUDGET} ({100 * tot / BUDGET - 100:+.0f} %)')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'SIZE width(x) {hi[0]-lo[0]:.4f} length(y) {hi[1]-lo[1]:.4f} height(z) {hi[2]-lo[2]:.4f} | lowest z {lo[2]:.5f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop[0]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop[0], tris=tri, total=tot)


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 640, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (0.0, 1, 0.15), (-0.8, 0.9, 0.45), (0.25, 0.15, 1.0),
                 (0.5, -0.8, 0.6)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 4, os.path.join(CHECK, f'Chick_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Chick_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


PREVIEW_VIEW, PREVIEW_FILL = (0.60, -1.0, 0.20), (0.50, 0.80)

if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-03 Chick', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Chick_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Chick_look_prev.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
