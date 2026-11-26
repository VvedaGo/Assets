# build.py - FUR-02 Hammock on a stand (FMS_Garden_Hammock), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build (shared, read only).
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- FUR-02 build|export|verify|dump
#   build  = build the model + printed checks + check renders to %TEMP%/assetnew_check/FUR-02/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify = only re-import the FBX in art/
#   dump   = build + geometry dump only (live: compare with the headless export)
#   LOD: none (catalogue).
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\FUR-02_Hammock\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FUR-02', 'build']})
#   Live mode touches only the collection FUR-02_Hammock; headless the collection is FMS_Garden_Hammock.
# Axes (Blender): X = along the hammock (Unity X), -Y = front (Unity +Z), Z = up (Unity Y).
# Pivot: root = centre of the footprint on the ground. One static mesh `FMS_Garden_Hammock_Body`, pivot at the root.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FUR-02')
NAME = 'FMS_Garden_Hammock'
PREVIEW = 'FMS_Garden_FUR_02_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 1000
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, CREAM, CREAM_D, IRON, BLUE = 0, 1, 3, 4, 13, 15
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FUR-02'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'FUR-02_Hammock' if LIVE else NAME

# ---- dimensions (spec prompts/FUR-02.3d.md; reference planning/AssetNew/references/FUR-02.png, see notes.md) ----
POST_X, POST_W, POST_Z1 = 1.45, 0.14, 1.10   # end posts at X +-1.45, 0.14 square, top 1.10 (= catalogue height)
FOOT_W, FOOT_H, FOOT_L = 0.16, 0.12, 0.90    # cross-feet 0.16 (X) x 0.12 high x 0.90 (Y); post sits 1 cm into the foot
BEAM_ZJ, BEAM_ZC = 0.72, 0.19                # bowed beam centre line: 0.72 at the post axis, 0.19 at X = 0 (reference)
BEAM_T, BEAM_D, BEAM_N = 0.12, 0.12, 12      # beam 0.12 thick (in the bow plane) x 0.12 deep (Y), 12 straight segments
BEAM_A = 1.48                                # half-axis of the ellipse the bow follows (steep near the posts, flat middle)
RING_Z, RING_R, ROD_R = 1.00, 0.06, 0.02     # wrought-iron eye: centre z 1.00, centre-line radius 0.06 (outer 0.16),
RING_GAP = (85.0, 135.0)                     # rod 0.04 across flats, 8-sided; open between these angles (0 = post, 90 = up)
RING_SEG = 8
CLOTH_X, CLOTH_N = 1.16, 12                  # cloth ends at X +-1.16 (gathered), 12 segments along X
CLOTH_ZMID, CLOTH_ZEND, CLOTH_K = 0.62, 0.84, 2.4   # cloth top: 0.62 at X = 0 (bottom 0.59), 0.84 at the gathered ends
CLOTH_T = 0.03                               # cloth thickness (closed shell, measured normal to the sag)
CLOTH_W, CLOTH_W_END = 0.90, 0.14            # width at the middle / at the gathered ends
CLOTH_DISH = 0.06                            # edges 6 cm above the centre stripe at the middle (shallow sling)
STRIPES = (CREAM, BLUE, CREAM, BLUE, CREAM)  # five lengthwise stripes, centre cream
CORD_W, CORD_Y, CORD_IN = 0.04, 0.055, 0.03  # cords 0.04 square, from Y +-0.055 / 3 cm inside the cloth end to the ring


# ---------------- small geometry helpers ----------------
def obox(P, cn, x0, x1, y0, y1, z0, z1, sx, sy, sz, ground=False):
    """axis-aligned box (12 tris), slot per face direction: sx for the +-X faces, sy for +-Y, sz for +-Z"""
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], sz), P.face([v[4], v[5], v[7], v[6]], sz),
          P.face([v[0], v[1], v[5], v[4]], sy), P.face([v[2], v[6], v[7], v[3]], sy),
          P.face([v[0], v[4], v[6], v[2]], sx), P.face([v[1], v[3], v[7], v[5]], sx)]
    P.comp.append((cn, fs, ground))


def sq(w, d):
    return [(w / 2, d / 2), (-w / 2, d / 2), (-w / 2, -d / 2), (w / 2, -d / 2)]


def beam_points():
    """bow centre line: half-ellipse x = A sin(f), z = zc + B (1 - cos f), resampled to BEAM_N equal-length segments"""
    fe = math.asin(POST_X / BEAM_A); B = (BEAM_ZJ - BEAM_ZC) / (1 - math.cos(fe))
    dense = [(BEAM_A * math.sin(f), BEAM_ZC + B * (1 - math.cos(f))) for f in
             (-fe + 2 * fe * i / 2000 for i in range(2001))]
    cum = [0.0]
    for a, b in zip(dense, dense[1:]): cum.append(cum[-1] + math.dist(a, b))
    out, j = [], 0
    for i in range(BEAM_N + 1):
        s = cum[-1] * i / BEAM_N
        while j < len(cum) - 2 and cum[j + 1] < s: j += 1
        t = (s - cum[j]) / max(1e-9, cum[j + 1] - cum[j])
        x = dense[j][0] + (dense[j + 1][0] - dense[j][0]) * t; z = dense[j][1] + (dense[j + 1][1] - dense[j][1]) * t
        out.append(Vector((x, 0.0, z)))
    out[0].x, out[-1].x = -POST_X, POST_X
    return out


def cloth_z(x):
    """top of the centre stripe along X (catenary-like sag)"""
    u = abs(x) / CLOTH_X
    return CLOTH_ZMID + (CLOTH_ZEND - CLOTH_ZMID) * (math.cosh(CLOTH_K * u) - 1) / (math.cosh(CLOTH_K) - 1)


def cloth_slope(x):
    h = 1e-4; return (cloth_z(x + h) - cloth_z(x - h)) / (2 * h)


def cloth_w(x):
    u = min(1.0, abs(x) / CLOTH_X)
    return CLOTH_W_END + (CLOTH_W - CLOTH_W_END) * max(0.0, 1 - u ** 4) ** 0.5


def cloth_tv(x):
    """vertical offset of the bottom surface so the thickness normal to the sag stays CLOTH_T"""
    return CLOTH_T * math.sqrt(1 + cloth_slope(x) ** 2)


# ---------------- the model ----------------
def build_body():
    P = Part('Body')
    for sx in (-1, 1):
        x = sx * POST_X
        obox(P, 'Feet', x - FOOT_W / 2, x + FOOT_W / 2, -FOOT_L / 2, FOOT_L / 2, 0.0, FOOT_H, WOOD, WOOD, WOOD, ground=True)
        obox(P, 'Posts', x - POST_W / 2, x + POST_W / 2, -POST_W / 2, POST_W / 2, FOOT_H - 0.01, POST_Z1, WOOD, WOOD, WOOD)
    # bowed beam: straight segments with mitred joints, both ends inside the posts
    from pack_shapes import path_sweep
    path_sweep(P, 'Beam', beam_points(), (0, 1, 0), sq(BEAM_T, BEAM_D), WOOD, WOOD)
    # wrought-iron eyes on the inner post faces (open rings in the XZ plane), cords from the cloth ends
    a0, a1 = RING_GAP[1], RING_GAP[0] + 360.0
    for sx in (-1, 1):
        cx = sx * (POST_X - POST_W / 2 - RING_R - ROD_R + 0.012)       # rod sunk ~1 cm into the post face
        pts = []
        for i in range(RING_SEG + 1):
            a = math.radians(a0 + (a1 - a0) * i / RING_SEG)
            pts.append(Vector((cx + sx * RING_R * math.cos(a), 0.0, RING_Z + RING_R * math.sin(a))))
        path_sweep(P, 'Rings', pts, (0, 1, 0), pc.ngon(ROD_R / math.cos(math.pi / 8), 8, math.pi / 8), IRON, IRON)
        # cords: start inside the gathered cloth end, end on the ring centre line at its lowest point
        xs = sx * (CLOTH_X - CORD_IN)
        lo = min(pts, key=lambda p: p.z)
        for sy in (-1, 1):
            p0 = Vector((xs, sy * CORD_Y, cloth_z(xs) - cloth_tv(xs) / 2))
            p1 = Vector((lo.x, sy * 0.008, lo.z))
            pc.sweep(P, 'Cords', p0, p1, sq(CORD_W, CORD_W), [(0, 1, 0), (1, 1, 0)], CREAM_D, CREAM_D, CREAM_D, ref=(0, 1, 0))
    # cloth: sagging sling, closed shell, 5 stripes (one palette cell per stripe), cream-dark edges
    rings = []
    for i in range(CLOTH_N + 1):
        x = -CLOTH_X + 2 * CLOTH_X * i / CLOTH_N
        w, zt, tv = cloth_w(x), cloth_z(x), cloth_tv(x)
        dish = CLOTH_DISH * (w - CLOTH_W_END) / (CLOTH_W - CLOTH_W_END)
        top = [Vector((x, s * w / 2, zt + dish * s * s)) for s in (-1, -0.6, -0.2, 0.2, 0.6, 1)]
        bot = [Vector((p.x, p.y, p.z - tv)) for p in reversed(top)]
        rings.append(top + bot)
    def side(j, k):
        if k < 5: return STRIPES[k]
        if k in (5, 11): return CREAM_D
        return STRIPES[10 - k]
    P.loft('Cloth', rings, side, CREAM_D, CREAM_D)
    return P


# ---------------- assembly ----------------
def clear_own():
    sc = bpy.context.scene
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return coll


def atlas_and_material():
    """reuse the shared atlas A PNG (never rewritten here) and M_Garden_Build (created only when missing)"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(PAL_A):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), img.size[:], 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def comp_tree(P, names):
    from mathutils.bvhtree import BVHTree
    P.bm.verts.index_update()
    vs = [v.co.copy() for v in P.bm.verts]
    polys = [[v.index for v in f.verts] for nm, fs, _ in P.comp if nm in names for f in fs]
    return BVHTree.FromPolygons(vs, polys), vs, polys


def functional_checks(P):
    """cloth clear of the beam and the posts; beam clear of the ground; cords end in rings and cloth"""
    beam, vs, _ = comp_tree(P, {'Beam'})
    cloth, _, cp = comp_tree(P, {'Cloth'})
    posts, _, _ = comp_tree(P, {'Posts'})
    cv = {i for f in cp for i in f}
    gap_beam = min(beam.find_nearest(vs[i])[3] for i in cv)
    gap_post = min(posts.find_nearest(vs[i])[3] for i in cv)
    bverts = {v.index for nm, fs, _ in P.comp if nm == 'Beam' for f in fs for v in f.verts}
    beam_min = min(vs[i].z for i in bverts)
    cloth_bot_mid = min(vs[i].z for i in cv if abs(vs[i].x) < 1e-6)
    rows = [('cloth -> beam clearance', gap_beam, 0.15, 'ge'), ('cloth -> posts clearance', gap_post, 0.05, 'ge'),
            ('no cloth/beam overlap', 0.0 if cloth.overlap(beam) else 1.0, 1.0, 'eq'),
            ('beam lowest point above ground', beam_min, 0.10, 'ge'),
            ('cloth bottom at X = 0 (centre stripe)', cloth_bot_mid, 0.59, 'near')]
    ok = True
    for nm, got, want, how in rows:
        good = got >= want - 1e-4 if how == 'ge' else (abs(got - want) <= 0.01 if how == 'near' else abs(got - want) <= 1e-4)
        ok &= good
        print(f'  FUNC {nm}: {got:.4f} (want {">= " if how == "ge" else ""}{want}) {"OK" if good else "FAIL"}')
    return ok


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_body()
    tris = part_tris(P)
    fok = functional_checks(P)
    body = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)
    obs = {'Body': body}
    bpy.context.view_layer.update()
    print(f'== {NAME}')
    tot = pc.report(obs)
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    n, smp = pc.coplanar_overlaps(body)
    pts = [body.matrix_world @ v.co for v in body.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    feet = sum(1 for p in pts if abs(p.z) < 1e-6)
    print(f'  GROUND min z {lo[2]:.4f}, vertices on z=0: {feet} (2 feet x 4) ->', 'OK' if abs(lo[2]) < 1e-6 and feet == 8 else 'FAIL')
    print(f'  SIZE X {hi[0]-lo[0]:.3f} Y {hi[1]-lo[1]:.3f} Z {hi[2]-lo[2]:.3f}')
    print('  SNAP: no contract (free-standing furniture)')
    print('  FUNCTIONAL', 'OK' if fok else 'FAIL')
    return coll, root, obs, img, mat


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        me = ob.data; uv = me.uv_layers.active.data
        vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
        fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                     tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
        allv.append(vs + [tuple(round(c, 5) for c in ob.matrix_world.translation)]); allf.append(fs)
    h = hashlib.sha1(json.dumps([allv, allf]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=[len(v) for v in allv], faces=[len(x) for x in allf], sha1=h), f)
    print('  geometry dump', path, [len(v) for v in allv], 'verts', [len(x) for x in allf], 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), frame=None):
    """frame: optional world points to frame (close-up checks); default = all vertices of objs"""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_FUR02_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_FUR02_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_FUR02_World'); w.use_nodes = True; nt = w.node_tree
    wo = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bgn.inputs['Color'].default_value = (lin(bg[0]), lin(bg[1]), lin(bg[2]), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.85, 0.88, 0.95, 1)
    amb.inputs['Strength'].default_value = 0.65
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bgn.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], wo.inputs['Surface']); sc.world = w
    tmp = []
    def sun(nm, rot, e, col, shadow=True):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.color = col; ld.angle = math.radians(28); ld.use_shadow = shadow
        o = bpy.data.objects.new(nm, ld); o.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(o)
        tmp.append(o)
    sun('TMP_FUR02_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_FUR02_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_FUR02_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_FUR02_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    bpy.context.view_layer.update()
    pts = frame or [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = (sum(pts, Vector()) / len(pts)) if frame else Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 10.0
    for _ in range(30):
        x0, x1, y0, y1 = place(d); k = max((x1 - x0) / fill_w, (y1 - y0) / fill_h)
        if lens: d *= k
        else: cd.ortho_scale *= k
    x0, x1, y0, y1 = place(d)
    asp = res[1] / res[0]
    cd.shift_x = (x0 + x1) / 2 - 0.5; cd.shift_y = ((y0 + y1) / 2 - 0.5) * asp
    sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
    try:
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        for o in tmp:
            dat = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(dat, bpy.types.Light): bpy.data.lights.remove(dat)
            else: bpy.data.cameras.remove(dat)
        bpy.data.collections.remove(tc); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(coll, root, fbx):
    """the owner's selection / active object are restored after the export"""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act
    return fbx


VIEW_REF = (-0.449, -0.844, 0.292)                 # reference: front-left (left post nearer), yaw 28, elevation 17 deg, long lens
VIEW_PREVIEW = (0.85, -1.25, 0.75)                 # series preview 3/4 (~25-30 deg), front-right, as FUR-01 / STR-01

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, obs, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs, os.path.join(CHECK_DIR, f'FUR-02_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.94, fill_h=0.8, lens=120)
        render(objs, os.path.join(CHECK_DIR, f'FUR-02_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'FUR-02_front_{tag}.png'), (0.0, -1.0, 0.05), res=(1280, 600), lens=70)
        render(objs, os.path.join(CHECK_DIR, f'FUR-02_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_one(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()), os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
