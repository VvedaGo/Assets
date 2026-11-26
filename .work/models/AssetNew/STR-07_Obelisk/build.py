# build.py - STR-07 Obelisk for climbers (FMS_Garden_Obelisk + _White), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- STR-07 build|export|verify
#   build  = build both models + printed checks + check renders to %TEMP%/assetnew_check/STR-07/
#   export = build + 2 FBX (base, _White; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, for the live/headless comparison)
#   verify = only re-import the 2 FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\STR-07_Obelisk\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-07', 'build']})
#   Live mode touches only the collection STR-07_Obelisk and its child collection STR-07_Obelisk_White.
# Axes (Blender): X = right, -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y). The obelisk is the same from all
# four sides. Pivot: centre of the footprint on the ground. No LOD (catalogue).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'STR-07')
NAME = 'FMS_Garden_Obelisk'
PREVIEW = 'FMS_Garden_STR_07_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 500, '_White': 500}
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, WOOD_M, WHITE = 0, 1, 2, 10
COLL = 'STR-07_Obelisk'
VARIANTS = ('_White',)
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-07'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/STR-07.3d.md; reference planning/AssetNew/references/STR-07.png, see notes.md) ----
POST_H = 0.081 / 2            # half side of the HORIZONTAL post section; the posts lean ~7 deg per axis, so the true
                              # (perpendicular) section is 0.0804 >= 0.08 (spec minimum)
POST_B = 0.30 - POST_H        # base centres +-0.2595 -> outer base box exactly 0.60 x 0.60
POST_T, Z_POST_TOP = 0.05, 1.70   # post axis passes the top centres +-0.05 at z 1.70 (spec) = the collar bottom ...
Z_POST_END = 1.73             # ... and continues 3 cm into the collar, top cut flat (buried, posts still do not touch)
BAND_ZS = (0.36, 0.90, 1.40)  # band centre heights (spec 0.35/0.85/1.35; reference measured ~0.37/0.96/1.39, notes)
BAND_T, BAND_D = 0.05, 0.05   # band section: height x depth
BAND_INSET = 0.008            # band outer face 8 mm INSIDE the post outer face at the band centre height (reference:
                              # rails run between the posts, flush-ish with their faces; the corners hide in the posts)
COLLAR_H, Z_COL0, Z_COL1 = 0.095, 1.70, 1.77  # collar 0.19 x 0.19 x 0.07 (must contain the 0.08 post tops, notes dev. 1)
BALL_R, BALL_Z, BALL_SUB = 0.08, 1.82, 2      # icosphere Ø0.16 (spec), subdivisions 2 = 80 tris (reference facets),
                                              # pole vertex on top exactly 1.90, bottom 3 cm in the collar
H_TOTAL = BALL_Z + BALL_R


def post_c(z):
    """post centre (both X and Y magnitude) at height z"""
    return POST_B + (POST_T - POST_B) * z / Z_POST_TOP


# ---------------- small geometry helpers ----------------
def obox(P, cn, x0, x1, y0, y1, z0, z1, sx, sy, sz, ground=False):
    """axis-aligned box (12 tris), slot per face direction: sx for the +-X faces, sy for +-Y, sz for +-Z"""
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], sz), P.face([v[4], v[5], v[7], v[6]], sz),
          P.face([v[0], v[1], v[5], v[4]], sy), P.face([v[2], v[6], v[7], v[3]], sy),
          P.face([v[0], v[4], v[6], v[2]], sx), P.face([v[1], v[3], v[7], v[5]], sx)]
    P.comp.append((cn, fs, ground))


def leaning_post(P, sx, sy, slot):
    """sheared square prism: horizontal 0.081 square sections, axis-aligned faces (front faces face the viewer, as in the
    reference), from the base centre at z 0 to the top centre at Z_POST_TOP; bottom and top cut horizontally"""
    bc = (sx * POST_B, sy * POST_B); tc = (sx * POST_T, sy * POST_T)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    r0 = [Vector((bc[0] + a * POST_H, bc[1] + b * POST_H, 0.0)) for a, b in sq]
    te = post_c(Z_POST_END); tc = (sx * te, sy * te)
    r1 = [Vector((tc[0] + a * POST_H, tc[1] + b * POST_H, Z_POST_END)) for a, b in sq]
    P.loft('Posts', [r0, r1], slot, slot, slot, ground=True)


def band(P, zc, slot):
    """square ring on the four posts: one closed loop (4 corner sections), outer face BAND_INSET inside the post outer
    faces at zc, depth BAND_D: the rails show between the posts, their ends/corners are buried in the posts
    (no floating, no coplanar: the post faces lean 7 deg)"""
    o = post_c(zc) + POST_H - BAND_INSET; i = o - BAND_D; z0, z1 = zc - BAND_T / 2, zc + BAND_T / 2
    def sqr(h, z): return [Vector((-h, -h, z)), Vector((h, -h, z)), Vector((h, h, z)), Vector((-h, h, z))]
    P.torus_loft('Bands', [sqr(o, z0), sqr(o, z1), sqr(i, z1), sqr(i, z0)], slot)


def ball(P, slot):
    """faceted icosphere (subdivisions 2 = 80 tris), pole vertex on top at exactly H_TOTAL"""
    ret = bmesh.ops.create_icosphere(P.bm, subdivisions=BALL_SUB, radius=BALL_R,
                                     matrix=Matrix.Translation((0, 0, BALL_Z)) @ Matrix.Rotation(math.pi / 2, 4, 'Z'),
                                     calc_uvs=False)    # 90 deg: the Blender icosphere is Y-symmetric, the pack checks X
    vs = set(ret['verts']); fs = [f for f in P.bm.faces if f.verts[0] in vs]
    for f in fs: f[P.slot] = slot
    P.comp.append(('Ball', fs, False))


def build_obelisk(slot):
    P = Part('Body')
    for sx in (-1, 1):
        for sy in (-1, 1):
            leaning_post(P, sx, sy, slot)
    for z in BAND_ZS: band(P, z, slot)
    obox(P, 'Collar', -COLLAR_H, COLLAR_H, -COLLAR_H, COLLAR_H, Z_COL0, Z_COL1, slot, slot, slot)
    ball(P, slot)
    return P


# ---------------- assembly ----------------
def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    colls = [coll]
    for suf in VARIANTS:
        c = bpy.data.collections.get(COLL + suf) or bpy.data.collections.new(COLL + suf)
        if c.name not in coll.children: coll.children.link(c)
        colls.append(c)
    for c in colls:
        for o in list(c.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return colls


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


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def mirror_y(ob):
    """the obelisk is the same from all sides: also check the Y mirror and the 90 deg rotation symmetry"""
    from mathutils import kdtree
    vs = [v.co.copy() for v in ob.data.vertices]
    kd = kdtree.KDTree(len(vs))
    for i, v in enumerate(vs): kd.insert(v, i)
    kd.balance()
    my = max(kd.find(Vector((v.x, -v.y, v.z)))[2] for v in vs)
    r90 = max(kd.find(Vector((-v.y, v.x, v.z)))[2] for v in vs if v.z < BALL_Z - BALL_R - 1e-4)   # without the ball
    print(f'  mirrorY {my:.6f} | rot90 (posts, bands, collar) {r90:.6f}')
    return my, r90


def contacts(P):
    """band inner faces must cut into every post; collar must contain all post tops; ball must sit in the collar"""
    rows = []
    for z in BAND_ZS:
        o = post_c(z) + POST_H - BAND_INSET; i = o - BAND_D
        for zz in (z - BAND_T / 2, z + BAND_T / 2):
            pin, pout = post_c(zz) - POST_H, post_c(zz) + POST_H
            rows.append((f'band {z} @z{zz:.3f}: post {pin:.4f}..{pout:.4f} band {i:.4f}..{o:.4f} (rail face inset '
                         f'{pout - o:.4f}, rail end buried {o - pin:.4f})', pout - o > 0.002 and o - pin > 0.02))
    pout_c0 = post_c(Z_COL0) + POST_H
    rows.append((f'collar half {COLLAR_H} vs post outer face at collar bottom {pout_c0:.4f}', pout_c0 < COLLAR_H - 0.002))
    rows.append((f'post tops z {Z_POST_END} inside collar {Z_COL0}..{Z_COL1}', Z_COL0 < Z_POST_END < Z_COL1 - 0.01))
    rows.append((f'ball bottom {BALL_Z - BALL_R:.3f} sunk in collar top {Z_COL1}', BALL_Z - BALL_R < Z_COL1 - 0.005))
    gap_top = 2 * (post_c(Z_POST_END) - POST_H)
    rows.append((f'gap between neighbouring posts at the top {gap_top:.4f} (>0, posts do not touch)', gap_top > 0.005))
    ok = True
    for t, g in rows:
        ok &= g; print(f'  CONTACT {t}: {"OK" if g else "FAIL"}')
    return ok


def all_coplanar(obs, tag):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_STR07_all_' + tag); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_STR07_all_' + tag, me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def size_report(objs):
    """no SNAP contract for STR-07 (free-standing decor); functional sizes of the spec instead"""
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    rows = [('footprint X (outer base box)', hi[0] - lo[0], 0.60), ('footprint Y (outer base box)', hi[1] - lo[1], 0.60),
            ('total height (ball top)', hi[2], 1.90), ('min z (ground contact)', lo[2], 0.0),
            ('footprint centre X', (hi[0] + lo[0]) / 2, 0.0), ('footprint centre Y', (hi[1] + lo[1]) / 2, 0.0)]
    ok = True
    for nm, got, want in rows:
        good = abs(got - want) <= 1e-3; ok &= good
        print(f'  SIZE {nm}: {got:.4f} (want {want}) {"OK" if good else "FAIL"}')
    print(f'  ground verts (z = 0): {sum(1 for p in pts if abs(p.z) < 1e-6)} (4 posts x 4)')
    print('  SIZE', 'OK' if ok else 'FAIL')
    return ok


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        P = build_obelisk(WHITE if suf else WOOD); tris = {'Body': part_tris(P)}
        if not suf: contacts(P)
        body = pc.to_object(P, asset, coll, mat, (0, 0, 0), root)
        obs = {'Body': body}
        bpy.context.view_layer.update()
        print(f'== {asset}')
        tot = pc.report(obs)
        print('  tris per component:', tris)
        print(f'  budget {BUDGET[suf]} ->', 'OK' if tot <= BUDGET[suf] else f'OVER x{tot / BUDGET[suf]:.2f}')
        for o in obs.values(): pc.coplanar_overlaps(o)
        print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values()), suf or 'base'))
        mirror_y(body)
        if suf == '_White':                        # same mesh as the base, only the UV cells differ
            same = [tuple(round(c, 6) for c in v.co) for v in body.data.vertices] == \
                   [tuple(round(c, 6) for c in v.co) for v in res[''][2]['Body'].data.vertices]
            cells = sorted({cell_of(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
            print(f'  _White: same vertices as the base {same}; cells used {cells}')
        else:
            cells = sorted({cell_of(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
            print(f'  base: cells used {cells}')
        size_report([root] + list(obs.values()))
        res[suf] = (coll, root, obs, [], tot)
    return colls, img, mat, res


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        me = ob.data; uv = me.uv_layers.active.data
        vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
        fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                     tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
        allv.append(vs); allf.append(fs)
    h = hashlib.sha1(json.dumps([allv, allf]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=[len(v) for v in allv], faces=[len(x) for x in allf], sha1=h), f)
    print('  geometry dump', path, [len(v) for v in allv], 'verts', [len(x) for x in allf], 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_STR07_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_STR07_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_STR07_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_STR07_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_STR07_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_STR07_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_STR07_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
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
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for o in tmp:
        dat = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dat, bpy.types.Light): bpy.data.lights.remove(dat)
        else: bpy.data.cameras.remove(dat)
    bpy.data.collections.remove(tc); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


def save_lib(path, colls, mat, img):
    data = set(colls) | {mat, img}
    for c in colls: data |= set(c.objects) | {o.data for o in c.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(asset, coll, root, fbx):
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx


VIEW_REF = (0.50, -1.0, 0.60)                               # reference: ~27 deg yaw from the front-right (4 legs evenly spaced), ~28 deg above, 28 mm
VIEW_PREVIEW = (0.85, -1.25, 0.75)                          # series preview 3/4 from the front-right (~25 deg)

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, o, e, t = res[suf]; return [r] + list(o.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-07_ref_{tag}.png'), VIEW_REF, res=(1024, 1536), fill_w=0.70, fill_h=0.83, lens=28)
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-07_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-07_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_White'), os.path.join(CHECK_DIR, f'STR-07_white_{tag}.png'), VIEW_PREVIEW)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbxs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]
            fbxs.append(export_one(NAME + suf, c, r, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
        render(objs_of(''), os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        for f in fbxs: pc.verify(f)
    if MODE in ('export', 'dump'):
        allobs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]; allobs += list(o.values())
        geom_dump(allobs, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
