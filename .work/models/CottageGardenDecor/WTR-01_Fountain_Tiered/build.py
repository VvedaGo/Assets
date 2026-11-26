# build.py - WTR-01 Tiered fountain (FMS_Garden_Fountain_Tiered), pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- WTR-01 build|export|verify|dump
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/WTR-01/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
#   verify = only re-import the FBX in art/ (run after make_lod1.py, which rewrites the FBX with the _Low1 children)
#   LOD1:  blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#            --python Tools/blender/make_lod1.py -- --art <ABSOLUTE repo>/art/CottageGardenDecor FMS_Garden_Fountain_Tiered
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\WTR-01_Fountain_Tiered\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['WTR-01', 'build']})
#   Live mode touches only the collection WTR-01_Fountain_Tiered (other objects, scenes and the owner's .blend stay as
#   they are). Headless the collection is named FMS_Garden_Fountain_Tiered (make_lod1.py looks it up by the asset name).
# Axes (Blender): -Y = front (reference view), Z = up. Pivot: centre of the basin on the ground (0, 0, 0).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
ATLAS_PATH = os.environ.get('PACK_ATLAS') or os.path.join(REPO, 'art', 'CottageGardenDecor', 'Textures', 'FMS_Garden_AtlasA.png')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'WTR-01')
NAME = 'FMS_Garden_Fountain_Tiered'
PREVIEW = 'FMS_Garden_WTR_01_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here (loaded, never saved)
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 2800
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
MET_L, LIME, STONE, WATER = 9, 11, 12, 15       # A-9 metal light (stream side), A-11 limestone, A-12 stone, A-15 water
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'WTR-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'WTR-01_Fountain_Tiered' if LIVE else NAME

# ---------------- dimensions (measured on references/WTR-01.png, see notes.md) ----------------
# Reference: front view, ~24 deg above, near-orthographic; basin 2.4 m = 966 px => 402 px/m.
# Profiles: (z, apothem, slot of the band from this ring to the next). Apothem = centre -> middle of a flat face.
# Segments / phase (all rings symmetric to the YZ plane, front = -Y):
#   basin 16 sides, vertex on +X and to the front (as the reference);
#   bowls 16 sides, flat face on +X and to the front (streams sit on face centres at 22.5 + 45k deg);
#   pedestals and finial 8 sides, flat face on +X and to the front.
N_BASIN, N_BOWL, N_PED = 16, 16, 8
PH_BASIN, PH_BOWL, PH_PED = 0.0, math.pi / 16, math.pi / 8

BASIN_R = 1.2                                   # vertex radius (bbox 2.4 x 2.4)
BASIN_A = BASIN_R * math.cos(math.pi / N_BASIN) # outer apothem 1.177
BASIN_T = 0.22                                  # wall thickness (top ring width, reference)
BASIN_TOP, BASIN_WATER = 0.34, 0.21               # inner wall 0.13 visible (reference)
BASIN = [                                       # closed shell: bottom -> outer wall -> top ring -> inner wall -> water cap
    (0.00, BASIN_A, LIME),                      # outer wall
    (BASIN_TOP, BASIN_A, LIME),                 # flat top ring
    (BASIN_TOP, BASIN_A - BASIN_T, STONE),      # inner wall (second tone)
    (BASIN_WATER, BASIN_A - BASIN_T, None),     # -> water cap
]

LOW_RIM, LOW_A, LOW_IN = 1.37, 0.735, 0.59       # lower bowl: rim top z, outer apothem, inner apothem
LOW_WATER = LOW_RIM - 0.04
LOW_BOWL = [
    (0.87, 0.20, LIME),                         # bottom (cap hidden inside the pedestal collar)
    (1.04, 0.50, LIME),                         # underside, lower band
    (1.255, LOW_A, LIME),                       # rim band (vertical)
    (LOW_RIM, LOW_A, LIME),                     # rim top ring
    (LOW_RIM, LOW_IN, STONE),                   # inner wall (second tone)
    (LOW_WATER, LOW_IN, None),                  # -> water cap
]
LOW_PED = [                                     # lower pedestal, 8 sides; starts below the basin water, ends inside the bowl
    (BASIN_WATER - 0.04, 0.265, STONE),         # foot block (plinth, second tone)
    (0.31, 0.265, STONE),                       # block top ring
    (0.31, 0.225, LIME),                        # foot flare
    (0.43, 0.165, LIME),                        # waist
    (0.46, 0.16, LIME),                         # knob lower chamfer
    (0.50, 0.20, LIME),                         # knob band
    (0.555, 0.20, LIME),                        # knob upper chamfer
    (0.60, 0.15, LIME),                         # neck (slight taper)
    (0.80, 0.14, LIME),                         # collar cone under the bowl
    (0.87, 0.21, LIME),                         # collar top part (inside the bowl)
    (0.91, 0.21, None),
]

UP_RIM, UP_A, UP_IN = 2.03, 0.42, 0.34          # upper bowl
UP_WATER = UP_RIM - 0.02
UP_BOWL = [
    (1.72, 0.13, LIME),                         # bottom (cap hidden inside the neck collar)
    (1.85, 0.30, LIME),
    (1.965, UP_A, LIME),
    (UP_RIM, UP_A, LIME),
    (UP_RIM, UP_IN, STONE),
    (UP_WATER, UP_IN, None),
]
UP_PED = [                                      # upper neck, 8 sides; starts below the lower water, ends inside the upper bowl
    (LOW_WATER - 0.04, 0.165, LIME),
    (LOW_WATER, 0.165, LIME),                   # foot flare (trapezoid rising out of the water)
    (1.43, 0.11, LIME),
    (1.45, 0.11, LIME),                         # knob lower chamfer
    (1.47, 0.135, LIME),                        # knob band
    (1.50, 0.135, LIME),                        # knob upper chamfer
    (1.53, 0.093, LIME),                        # neck (0.20 across corners: spec minimum, reference is slimmer)
    (1.68, 0.093, LIME),                        # flare into the upper bowl
    (1.72, 0.145, LIME),
    (1.75, 0.145, None),                        # (inside the upper bowl)
]
FINIAL = [                                      # stepped pine-cone finial, 8 sides, rises out of the upper water
    (UP_WATER - 0.05, 0.075, LIME),
    (UP_WATER, 0.10, LIME),                     # lower inverted cone
    (2.14, 0.175, LIME),                        # shoulder (tier 1)
    (2.18, 0.125, STONE),                       # band 1 (tier edge, second tone)
    (2.25, 0.125, LIME),                        # tier 2 slope
    (2.29, 0.07, STONE),                        # band 2 (tier edge)
    (2.34, 0.07, LIME),                         # tip cone
    (2.42, 0.0, None),
]

ST_W, ST_T, ST_GAP = 0.07, 0.035, 0.012         # stream ribbon width (tangential), thickness, gap to the rim face
ST_AZ = [math.radians(22.5 + 45 * k) for k in range(8)]


# ---------------- shapes ----------------
def ring(bm, z, a, n, ph):
    if a <= 0: return [bm.verts.new(Vector((0, 0, z)))]
    r = a / math.cos(math.pi / n)
    return [bm.verts.new(Vector((x, y, z))) for x, y in pc.ngon(r, n, ph)]


def revolve(P, comp, cname, prof, n, ph, cap0, cap1, ground=False):
    """closed solid of revolution; band j gets slot prof[j][2]; cap0 = bottom slot, cap1 = top slot (None = apex)"""
    R = [ring(P.bm, z, a, n, ph) for z, a, _ in prof]; fs = []
    for j in range(len(R) - 1):
        A, B, s = R[j], R[j + 1], prof[j][2]
        for k in range(n):
            k1 = (k + 1) % n
            if len(B) == 1: fs.append(P.face([A[k], A[k1], B[0]], s))
            elif len(A) == 1: fs.append(P.face([A[0], B[k1], B[k]], s))
            else: fs.append(P.face([A[k], A[k1], B[k1], B[k]], s))
    if len(R[0]) > 1: fs.append(P.face(list(reversed(R[0])), cap0))
    if len(R[-1]) > 1: fs.append(P.face(list(R[-1]), cap1))
    comp.append((cname, fs, ground))
    return R


def stream(P, comp, cname, az, a_in, a_out, z_rim, z_end):
    """water ribbon: lies on the rim top (sunk 5 mm), bends over the outer edge, falls straight down into the water below.
    Ring = [(inner, -w), (inner, +w), (outer, +w), (outer, -w)]; inner = side facing the bowl (bottom / radial inside)."""
    er = Vector((math.cos(az), math.sin(az), 0)); et = Vector((-math.sin(az), math.cos(az), 0)); ez = Vector((0, 0, 1))
    w, t = ST_W / 2, ST_T
    zb = z_rim - 0.005; zt = zb + t                                    # horizontal part: bottom 5 mm inside the rim
    r0 = a_in - 0.01                                                   # starts 1 cm over the water (comes out of the bowl)
    rv_in = a_out + ST_GAP; rv_out = rv_in + t                         # vertical part, radial faces
    def pt(r, z, s): return er * r + et * s + ez * z
    rings = [[(r0, zb), (r0, zt)],                                     # (inner, outer) corner (r, z)
             [(rv_in, zb), (rv_out, zt)],                              # mitred bend
             [(rv_in, z_end), (rv_out, z_end)]]
    R = []
    for (ri, zi), (ro, zo) in rings:
        R.append([P.bm.verts.new(pt(ri, zi, -w)), P.bm.verts.new(pt(ri, zi, w)),
                  P.bm.verts.new(pt(ro, zo, w)), P.bm.verts.new(pt(ro, zo, -w))])
    # faces per segment: inner, +w side, outer, -w side. The -w side is the A-9 light row along the whole ribbon; on the rim
    # (segment 0) the top face is A-9 too, so the hook over the lip reads light as in the reference, not as a blue spoke.
    side_slots = [[WATER, WATER, MET_L, MET_L], [WATER, WATER, WATER, MET_L]]
    fs = []
    for j in range(2):
        for k in range(4):
            k1 = (k + 1) % 4
            fs.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], side_slots[j][k]))
    fs.append(P.face(list(reversed(R[0])), WATER)); fs.append(P.face(list(R[-1]), WATER))
    comp.append((cname, fs, False))


def build_basin():
    P = Part('Basin'); c = P.comp
    revolve(P, c, 'Basin', BASIN, N_BASIN, PH_BASIN, LIME, WATER, ground=True)
    return P


def build_lower():
    P = Part('Lower'); c = P.comp
    revolve(P, c, 'LowerPedestal', LOW_PED, N_PED, PH_PED, STONE, LIME)
    revolve(P, c, 'LowerBowl', LOW_BOWL, N_BOWL, PH_BOWL, LIME, WATER)
    return P


def build_upper():
    P = Part('Upper'); c = P.comp
    revolve(P, c, 'UpperNeck', UP_PED, N_PED, PH_PED, LIME, LIME)
    revolve(P, c, 'UpperBowl', UP_BOWL, N_BOWL, PH_BOWL, LIME, WATER)
    revolve(P, c, 'Finial', FINIAL, N_PED, PH_PED, LIME, None)
    return P


def build_stream_pair(k):
    """one azimuth: the upper-bowl stream (into the lower water) and the lower-bowl stream (into the basin water).
    Kept as its own small object (36 tris <= 60) so make_lod1.py leaves the ribbons intact in LOD1."""
    P = Part(f'Stream{k + 1}'); c = P.comp; az = ST_AZ[k]
    stream(P, c, 'StreamUp', az, UP_IN, UP_A, UP_RIM, LOW_WATER - 0.015)
    stream(P, c, 'StreamLow', az, LOW_IN, LOW_A, LOW_RIM, BASIN_WATER - 0.015)
    return P


# ---------------- assembly ----------------
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


def atlas_and_material():
    """reuse the shared atlas A PNG (never rewritten here) and M_Garden_Build (created only when missing)"""
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(ATLAS_PATH, check_existing=True)
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


def cross_contacts(obs):
    from mathutils.bvhtree import BVHTree
    trees = {}
    for o in obs:
        vs = [o.matrix_world @ v.co for v in o.data.vertices]; trees[o.name] = (BVHTree.FromPolygons(vs, [p.vertices for p in o.data.polygons]), vs)
    out = {}
    for a in obs:
        ta, va = trees[a.name]; best = None
        for b in obs:
            if b is a: continue
            tb, _ = trees[b.name]
            if ta.overlap(tb): best = (0.0, b.name); break
            dd = min(tb.find_nearest(v)[3] for v in va)
            if best is None or dd < best[0]: best = (dd, b.name)
        out[a.name.replace(NAME + '_', '')] = (round(best[0], 5), best[1].replace(NAME + '_', ''))
    print('  part contacts (gap to nearest other part):', out)
    return out


def all_coplanar(obs):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_WTR01_all'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_WTR01_all', me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def ribbon_contacts(P, obs):
    """each ribbon must intersect the bowl it starts on (sunk into the rim) and the part holding the water it falls into"""
    from mathutils.bvhtree import BVHTree
    def tree_of(o):
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        return BVHTree.FromPolygons(vs, [p.vertices for p in o.data.polygons])
    tgt = {'StreamUp': ('Upper', 'Lower'), 'StreamLow': ('Lower', 'Basin')}
    P.bm.verts.index_update(); allpos = [v.co.copy() for v in P.bm.verts]; res = []
    for nm, fs, _ in P.comp:
        t = BVHTree.FromPolygons(allpos, [[v.index for v in f.verts] for f in fs])
        a, b = tgt[nm]
        res.append(f'{nm}: rim {"OK" if t.overlap(tree_of(obs[a])) else "NO CONTACT"} / water {"OK" if t.overlap(tree_of(obs[b])) else "NO CONTACT"}')
    print(f'  {P.name} contacts:', ' | '.join(res))


def mirror_all(obs):
    from mathutils import kdtree
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    kd = kdtree.KDTree(len(pts))
    for i, q in enumerate(pts): kd.insert(q, i)
    kd.balance()
    print(f'  mirror X (whole model) max {max(kd.find(Vector((-q.x, q.y, q.z)))[2] for q in pts):.6f}')


def stream_landing():
    """each stream must start on its rim and end below the water surface it falls into, inside the water disc"""
    rows = []
    for nm, a_in, a_out, z_rim, z_w, a_w in (('up', UP_IN, UP_A, UP_RIM, LOW_WATER, LOW_IN),
                                             ('low', LOW_IN, LOW_A, LOW_RIM, BASIN_WATER, BASIN_A - BASIN_T)):
        r_out = a_out + ST_GAP + ST_T
        corner = math.hypot(r_out, ST_W / 2)                           # farthest point of the ribbon from the axis
        ok = corner < a_w and (z_w - 0.015) < z_w
        rows.append(f'{nm}: rim z {z_rim} -> water z {z_w} (end 15 mm under), ribbon r {a_out + ST_GAP:.3f}..{corner:.3f}'
                    f' inside water apothem {a_w:.3f}: {"OK" if ok else "FAIL"}')
    print('  streams:', ' | '.join(rows))


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    parts = [build_basin(), build_lower(), build_upper()] + [build_stream_pair(k) for k in range(8)]
    obs = {}; tris = {}
    for P in parts:
        tris[P.name] = part_tris(P)
        if P.name.startswith('Stream'):                                # the two ribbons of a pair are apart by design:
            ribbon_contacts(P, obs)                                    # each one is checked against its rim and water
            skip = ('StreamUp', 'StreamLow')                           # mirror: checked on the whole model below
        else: skip = ()
        obs[P.name] = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    bpy.context.view_layer.update()
    mirror_all(list(obs.values()))
    tot = pc.report(obs)
    print('  tris per part/component:', {k: v for k, v in tris.items() if not k.startswith('Stream')},
          '| each stream pair', tris['Stream1'], '| streams total', sum(sum(v.values()) for k, v in tris.items() if k.startswith('Stream')))
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    for o in obs.values(): pc.coplanar_overlaps(o)
    print('  coplanar overlaps, all parts merged:', all_coplanar(list(obs.values())))
    cross_contacts(list(obs.values()))
    stream_landing()
    zmin = min((o.matrix_world @ v.co).z for o in obs.values() for v in o.data.vertices)
    print(f'  min z {zmin:.4f} (basin bottom on the ground) | smooth faces',
          sum(p.use_smooth for o in obs.values() for p in o.data.polygons), '| materials',
          sorted({m.name for o in obs.values() for m in o.data.materials}))
    print('  SNAP: no contract for WTR-01 (CATALOG «Модули и стыковка» has none) -> n/a')
    return coll, root, obs, img, mat, tot


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
    print('  geometry dump', path, sum(len(v) for v in allv), 'verts', sum(len(x) for x in allf), 'faces sha1', h)
    return h


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_live_safe(coll, root, fbx):
    """pc.export changes the selection/active object: restore the owner's selection afterwards"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        return pc.export(NAME, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), ref_fit=None):
    """lens=None: orthographic. ref_fit=(width share, bottom share): scale by the width only and put the bbox bottom at
    that share of the frame height (direct overlay on the reference sheet)."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_WTR01_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_WTR01_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_WTR01_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_WTR01_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_WTR01_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_WTR01_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_WTR01_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 14.0
    for _ in range(30):
        x0, x1, y0, y1 = place(d)
        k = (x1 - x0) / ref_fit[0] if ref_fit else max((x1 - x0) / fill_w, (y1 - y0) / fill_h)
        if lens: d *= k
        else: cd.ortho_scale *= k
    x0, x1, y0, y1 = place(d)
    asp = res[1] / res[0]
    cd.shift_x = (x0 + x1) / 2 - 0.5
    cd.shift_y = ((y0 - ref_fit[1]) if ref_fit else ((y0 + y1) / 2 - 0.5)) * asp
    sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for o in tmp:
        dat = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dat, bpy.types.Light): bpy.data.lights.remove(dat)
        else: bpy.data.cameras.remove(dat)
    bpy.data.collections.remove(tc); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


E_REF = math.radians(24.1)
VIEW_REF = (0.0, -math.cos(E_REF), math.sin(E_REF))          # reference: front, ~24 deg above, near-orthographic
REF_FIT = (966 / 1254, (1254 - 1160) / 1254)                  # reference bbox: width share, bottom margin share
VIEW_PREVIEW = (1.0, -1.25, 0.75)                              # series preview 3/4 (as WTR-03)

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, obs, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs, os.path.join(CHECK_DIR, f'WTR-01_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), lens=None, ref_fit=REF_FIT)
        render(objs, os.path.join(CHECK_DIR, f'WTR-01_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'WTR-01_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()), os.path.join(CHECK_DIR, f'geom_{tag}.json'))
