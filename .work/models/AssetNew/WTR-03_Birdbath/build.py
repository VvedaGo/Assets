# build.py - WTR-03 Birdbath (FMS_Garden_Birdbath), pack AssetNew (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- WTR-03 build|export
#   build  = build + printed checks + check render to %TEMP%/assetnew_check/WTR-03/WTR-03_check.png
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\WTR-03_Birdbath\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['WTR-03', 'build']})
#   Live mode touches only the collection WTR-03_Birdbath (other objects, scenes and the owner's .blend stay as they are).
import bpy, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'WTR-03')
COLL = 'WTR-03_Birdbath'
NAME = 'FMS_Garden_Birdbath'
PREVIEW = 'FMS_Garden_WTR_03_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build), cell layout in notes.md
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 350
# atlas A palette, STYLE.md (slot = cell index; row-major from the top-left of the PNG)
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
LIME, STONE, WATER = 11, 12, 15
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'WTR-03'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
SEG_P, SEG_B = 10, 12                       # pedestal 10 sides (vertex on +X), bowl 12 sides (flat face to +X/-Y) - reference

# Solid of revolution, one closed shell (shared rings => no gaps, no coplanar overlaps between parts).
# Heights/radii measured on references/WTR-03.png (orthographic ~22 deg, bowl 0.60 m => 1270 px/m), see notes.md.
# (z, R vertex radius, component of the band from this ring to the next, slot of that band)
PED = [
    (0.000, 0.1665, 'Plinth', STONE),      # plinth wall (bottom cap = plinth, slot 12)
    (0.070, 0.1665, 'Plinth', STONE),      # plinth top, gently sloped (reads as the chamfered top)
    (0.078, 0.115, 'Foot', LIME),          # foot cone
    (0.1786, 0.068, 'Knob', LIME),         # knob lower chamfer
    (0.2045, 0.0866, 'Knob', LIME),        # knob band
    (0.242, 0.0866, 'Knob', LIME),         # knob upper chamfer
    (0.257, 0.064, 'Stem', LIME),          # stem (tapers upwards)
    (0.433, 0.0515, 'Collar', LIME),       # trumpet 1
    (0.478, 0.070, 'Collar', LIME),        # trumpet 2 (concave flare, flat top so the collar band reads)
    (0.509, 0.105, 'Collar', LIME),        # collar band (slightly widening)
    (0.548, 0.109, 'Collar', LIME),        # -> flat ledge (10-gon -> 12-gon annulus, bowl overhang 2.5 cm)
]
BOWL = [
    (0.548, 0.138, 'Bowl', LIME),          # bowl underside
    (0.657, 0.310, 'Bowl', LIME),          # rim wall (12-gon R 0.31 => 0.599 across flats)
    (0.700, 0.310, 'Bowl', LIME),          # rim top (flat annulus)
    (0.700, 0.2588, 'Bowl', STONE),        # inner wall, down to the water line
    (0.676, 0.2535, 'Water', WATER),       # water disc = top cap
]


def rings(bm, prof, n, a0):
    return [[bm.verts.new(Vector((x, y, z))) for x, y in pc.ngon(r, n, a0)] for z, r, _, _ in prof]


def bands(P, R, prof, comp):
    n = len(R[0])
    for j in range(len(R) - 1):
        cn, slot = prof[j][2], prof[j][3]
        for k in range(n):
            k1 = (k + 1) % n
            comp.setdefault(cn, []).append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], slot))


def build_birdbath():
    from pack_shapes import fill
    P = Part('Body'); bm = P.bm; comp = {}
    RP = rings(bm, PED, SEG_P, 0.0); RB = rings(bm, BOWL, SEG_B, math.pi / SEG_B)
    bands(P, RP, PED, comp); bands(P, RB, BOWL, comp)
    comp['Plinth'].append(P.face(list(reversed(RP[0])), STONE))      # bottom (kept: closed manifold for Unity/LOD tools)
    comp['Collar'] += fill(P, [RB[0], RP[-1]], LIME, (0, 0, 1))      # flat ledge under the bowl (shares both rings)
    comp['Water'] = [P.face(list(RB[-1]), WATER)]                    # flat 12-gon water disc on the inner-wall ring
    for cn in ('Plinth', 'Foot', 'Knob', 'Stem', 'Collar', 'Bowl', 'Water'):
        P.comp.append((cn, comp[cn], cn == 'Plinth'))
    return P


def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.objects: bpy.data.objects.remove(o, do_unlink=True)
    return coll


def build():
    coll = clear_own()
    img = pc.atlas_image(ATLAS_TEX, os.path.join(ART, 'Textures', ATLAS_TEX), PAL_A)
    mat = pc.material(ATLAS_MAT, img)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.85                     # Smoothness ~0.15 (STYLE.md)
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_birdbath()
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    n_cop, _ = pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris, analytic):', {cn: n for cn, n in part_tris().items()})
    return coll, root, ob, img, mat, tot


def part_tris():
    out = {}
    for prof, n in ((PED, SEG_P), (BOWL, SEG_B)):
        for j in range(len(prof) - 1): out[prof[j][2]] = out.get(prof[j][2], 0) + 2 * n
    out['Plinth'] += SEG_P - 2; out['Collar'] += SEG_P + SEG_B; out['Water'] = SEG_B - 2
    return out


def geom_dump(ob, path):
    me = ob.data; uv = me.uv_layers.active.data
    vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
    fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                 tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
    h = hashlib.sha1(json.dumps([vs, fs]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=len(vs), faces=len(fs), sha1=h), f)
    print('  geometry dump', path, len(vs), 'verts', len(fs), 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(coll, out, view_dir, elev_target=None, res=(1280, 800), fill_w=0.62, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_WTR03_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.collection.children.link(coll)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_WTR03_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_WTR03_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_WTR03_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_WTR03_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new('TMP_WTR03_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in coll.all_objects if o.type == 'MESH' for v in o.data.vertices]
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.location = loc; cam.rotation_euler = q.to_euler()
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 8.0
    for _ in range(30):
        x0, x1, y0, y1 = place(d); k = max((x1 - x0) / fill_w, (y1 - y0) / 0.9)
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
    bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


VIEW_REF = (0.0, -math.cos(math.radians(22)), math.sin(math.radians(22)))     # reference: front, ~22 deg above, near-orthographic
VIEW_PREVIEW = (1.0, -1.25, 0.75)                                               # series preview 3/4 (flat face to camera)

coll, root, ob, img, mat, tot = build()
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'build':
    tag = 'live' if LIVE else 'headless'
    render(coll, os.path.join(CHECK_DIR, f'WTR-03_check_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.61, lens=None)
    render(coll, os.path.join(CHECK_DIR, f'WTR-03_check34_{tag}.png'), VIEW_PREVIEW)
if MODE == 'export':
    for sub in ('Meshes', 'Textures', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = pc.export(NAME, coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
    render(coll, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    pc.verify(fbx)
    geom_dump(ob, os.path.join(CHECK_DIR, 'geom_headless.json' if not LIVE else 'geom_live.json'))
elif MODE == 'dump':
    geom_dump(ob, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
