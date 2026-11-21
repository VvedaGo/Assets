# build_duckling.py - BRD-06 Duckling (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_duckling.py -- BRD-06 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_duckling)
# look  : build + EEVEE renders at the reference and preview views (TEMP)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Chick/build_chick.py (balls, neck, eyes, wings) and ../Duck/build_duck.py (bill, webbed foot);
# helpers copied, shared modules imported read-only.
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Duckling'
TAG = 'FarmAnimals_Duckling'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-06.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_duckling')
REF_VIEW = (0.55, -1.0, 0.18)        # reference: front-left 3/4, duckling yawed ~30 deg to its right (we see its left, +X)
PALETTE = ['#F4C845', '#E2B13A', '#F8D45E', '#E9B036',
           '#D9A532', '#F68A2E', '#C5561A', '#F2862C',
           '#D8651E', '#2A1D17', '#F2E6C9', '#B5835A',
           '#7A5233', '#C8473B', '#6E9F4A', '#8E959B']
(BODY, BODY_D, BODY_L, WING, WING_D, BILL, BILL_D, LEG, LEG_D, EYE) = range(10)
BUDGET = 350

# ---------------- design numbers (m) ----------------
HEAD_C, HEAD_R = Vector((0, -0.014, 0.104)), Vector((0.053, 0.046, 0.046))
BODY_C, BODY_R = Vector((0, 0.010, 0.050)), Vector((0.045, 0.050, 0.034))
# rings: (theta deg from +Z, vertex count, phase deg). Staggered 10-gons + pentagon caps = geodesic-like facets, no pole fan.
# Head bottom ends in a flat 6-gon cap buried in the body (hidden), saves tris.
HEAD_RINGS = [(22, 5, 18), (52, 10, 18), (82, 10, 0), (112, 10, 18), (145, 6, 30)]
BODY_RINGS = [(28, 5, 18), (62, 10, 18), (98, 10, 0), (130, 10, 18), (160, 5, 18)]
NECK = [(0.060, 0.002, 0.034), (0.082, -0.008, 0.035)]          # (z, y centre, apothem), 8-gon
EYE_X, EYE_Z, EYE_R, EYE_PROUD = 0.027, 0.111, 0.0065, 0.0012
# upper bill rings (y, half width, mouth z, top z): buried root, widest middle, blunt tip; mouth line straight
BILL_K = 0.12                                                    # mouth line drop per metre forward
zm = lambda y: 0.089 + (y + 0.048) * BILL_K
BILL_UP = [(-0.048, 0.019, zm(-0.048), 0.108), (-0.078, 0.025, zm(-0.078), 0.100), (-0.092, 0.021, zm(-0.092), 0.093)]
BILL_LO = [(-0.050, 0.018, 0.0080), (-0.089, 0.019, 0.0052)]   # (y, half width top, depth below the mouth line)
LEG_X, LEG_Y = 0.017, 0.006
LEG_R0, LEG_R1, LEG_TOP, LEG_BOT = 0.0050, 0.0046, 0.026, 0.003
TAIL_A, TAIL_B = Vector((0, 0.048, 0.062)), Vector((0, 0.066, 0.077))
# wings: sections along y (y, z centre, half height, proud)
WING_UP = [(0.002, 0.055, 0.007, -0.0010), (0.010, 0.054, 0.008, 0.0005)]
WING_LO = [(0.000, 0.054, 0.013, 0.0015), (0.020, 0.052, 0.016, 0.0065), (0.044, 0.058, 0.005, 0.0025)]

JOINTS = {
    'Body': tuple(BODY_C), 'Neck': (0, -0.002, 0.062), 'Head': (0, -0.010, 0.076),
    'Beak_Lower': (0, -0.050, 0.088), 'WingUpper.L': (0.036, -0.006, 0.054), 'WingLower.L': (0.038, 0.000, 0.053),
    'TailFan1': tuple(TAIL_A),
    'LegUpper.L': (LEG_X, LEG_Y, 0.032), 'LegLower.L': (LEG_X, LEG_Y, LEG_TOP), 'Foot.L': (LEG_X, LEG_Y, 0.004),
}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-06', 'build'])[:2]


V = lambda *a: Vector(a)


# ---------------- helpers (copied from the chick / duck) ----------------
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


def ball(P, cname, c, r, rings, slot_fn):
    """closed faceted ellipsoid; rings (theta deg, n, phase deg); neighbouring rings are zipped by angle; the end rings
    are flat n-gon caps."""
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


def web_foot(P, nm, c0, sx):
    """flat triangular webbed foot (duck template, scaled): concave 8-point outline (heel, sides, 3 toe tips, 2 notches),
    sloped rim, fan top rising to the ankle point; flat sole at z = 0. 30 tris."""
    yaw = math.radians(10); f = V(sx * math.sin(yaw), -math.cos(yaw), 0); s = V(sx * math.cos(yaw), math.sin(yaw), 0)

    def pt(a, r, z):
        a = math.radians(a); return c0 + (f * math.cos(a) + s * math.sin(a)) * r + V(0, 0, z)
    outl = [(180, 0.0060, 0.0045), (105, 0.0072, 0.0045), (36, 0.0265, 0.0036), (17, 0.0175, 0.0036), (0, 0.0300, 0.0036),
            (-17, 0.0175, 0.0036), (-36, 0.0265, 0.0036), (-105, 0.0072, 0.0045)]
    top = [P.bm.verts.new(pt(a, r, z)) for a, r, z in outl]
    bot = [P.bm.verts.new(pt(a, r * 0.96, 0.0)) for a, r, z in outl]       # sole 4 % smaller: sloped rim, no vertical wall
    A = P.bm.verts.new(pt(0, 0.003, 0.0085))
    n = len(top)
    faces = [P.face([A, top[k], top[(k + 1) % n]], LEG) for k in range(n)]
    for k in range(n):
        faces.append(P.face([top[(k + 1) % n], top[k], bot[k], bot[(k + 1) % n]], LEG_D))
    faces.append(P.face(list(bot), LEG_D))
    P.comp.append((nm, faces, True))


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Duckling')
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
    # eyes: 8-gon dark discs EYE_PROUD above the facets, pyramid back buried in the head
    hp, n = hit(bvh_head, V(EYE_X, -1.0, EYE_Z), V(0, 1, 0))
    q = hp - HEAD_C
    if n.dot(q) < 0: n = -n
    n = (V(q.x / HEAD_R.x ** 2, q.y / HEAD_R.y ** 2, q.z / HEAD_R.z ** 2).normalized() + n).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    base = ngon_ring(hp, e1, e2, EYE_R, 8)
    hts = [bvh_head.ray_cast(v + n * 0.02, -n)[3] - 0.02 for v in base + [hp]]
    off = EYE_PROUD + max(hts)
    ring = [v + n * off for v in base]; apex = hp - n * 0.007
    print(f'EYE disc offset {off * 1000:.2f} mm, heights above facets {[round(-h * 1000, 2) for h in hts]} mm')
    eyes = {}
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], V(-apex.x, apex.y, apex.z))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False)); eyes[nm] = sum(rg, Vector()) / len(rg)

    # upper bill (part of Head): 5-point section ridge, shoulder L, lip L, lip R, shoulder R; flat bottom = mouth line
    def bill_ring(y, w, zm_, zt):
        zs = zt - 0.25 * (zt - zm_)
        return [V(0, y, zt), V(0.80 * w, y, zs), V(w, y, zm_), V(-w, y, zm_), V(-0.80 * w, y, zs)]
    P.loft('Head', [bill_ring(*r) for r in BILL_UP], BILL, BILL, BILL)
    lo = []
    for y, w, d in BILL_LO:
        z = zm(y) + 0.0025                         # top buried 2.5 mm inside the upper bill: no near-coplanar mouth faces
        lo.append([V(w, y, z), V(-w, y, z), V(-0.60 * w, y, z - d - 0.0025), V(0.60 * w, y, z - d - 0.0025)])
    P.loft('Beak_Lower', lo, BILL_D, BILL_D, BILL_D)
    JOINTS['Beak_Lower'] = (0, BILL_LO[0][0], zm(BILL_LO[0][0]) - 0.001)

    # wings: triangle sections hugging the body side (top/bottom tucked, middle proud)
    def wing_rings(spec):
        ex = lambda y, z: BODY_R.x * math.sqrt(max(0.0, 1 - ((y - BODY_C.y) / BODY_R.y) ** 2 - ((z - BODY_C.z) / BODY_R.z) ** 2))
        return [[V(ex(y, zc + h) - 0.003, y, zc + h), V(ex(y, zc - 0.3 * h) + pr, y, zc - 0.3 * h), V(ex(y, zc - h) - 0.003, y, zc - h)]
                for y, zc, h, pr in spec]
    for nm, spec, slot in (('WingUpper', WING_UP, WING), ('WingLower', WING_LO, WING)):
        r = wing_rings(spec)
        P.loft(nm + '.L', r, slot, slot, slot); P.loft(nm + '.R', mir(r), slot, slot, slot)

    for sx in (1, -1):
        h = bvh_body.ray_cast(V(sx * LEG_X, LEG_Y, 0.0), V(0, 0, 1))
        print(f'LEG exit z {h[0].z:.4f} (visible leg incl. foot)')
    # tail nub: flat diamond section, root buried in the upper back
    dv = (TAIL_B - TAIL_A).normalized(); tu = X.cross(dv).normalized()
    if tu.z < 0: tu = -tu
    P.loft('TailFan1', [ring_frame(TAIL_A.lerp(TAIL_B, t), X, tu, w, h, h, 4, 2.0)
                        for t, w, h in [(0.0, 0.011, 0.007), (1.0, 0.0035, 0.0022)]], BODY, BODY, BODY)

    # legs: hidden thigh prism, short 6-gon shank, webbed foot
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, 0.0032, 3, math.pi / 2) for z in (0.036, 0.020)], LEG, LEG, LEG)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6, 0.0) for z, r in [(LEG_TOP, LEG_R0), (LEG_BOT, LEG_R1)]],
               LEG, LEG, LEG)
        web_foot(P, 'Foot' + sfx, c(0.0), sx)
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
    me = bpy.data.meshes.new('TMP_DucklingAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_DucklingAll', me)
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
    print(f'TRIS total {tot} | target {BUDGET} ({100 * tot / BUDGET - 100:+.0f} %), limit {int(BUDGET * 1.2)}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 4, os.path.join(CHECK, f'Duckling_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Duckling_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


PREVIEW_VIEW, PREVIEW_FILL = (0.60, -1.0, 0.20), (0.50, 0.80)


def _make_preview():
    """local copy of animal_render.preview (shared module untouched): the sun gets shadow jitter and the render more
    samples, because at duckling scale (4 cm bill) EEVEE's filtered soft shadow under the bill lip shows as a sawtooth."""
    import inspect
    src = inspect.getsource(rn.preview)
    a = "ld.use_shadow = sh\n"
    assert a in src
    src = src.replace(a, a + "        ld.use_shadow_jitter = sh; ld.shadow_jitter_overblur = 10.0\n"
                             "        sc.eevee.taa_render_samples = 128\n")
    ns = dict(vars(rn)); exec(src, ns)
    return ns['preview']


preview = _make_preview()

if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-06 Duckling', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Duckling_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
        preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Duckling_look_prev.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
