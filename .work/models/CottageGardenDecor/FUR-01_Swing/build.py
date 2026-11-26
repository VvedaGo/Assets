# build.py - FUR-01 Garden swing, A-frame (FMS_Garden_Swing), pack CottageGardenDecor (Cottage Garden Decor),
# atlas A Garden_Build (shared, read only).
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- FUR-01 build|export|verify|dump
#   build  = build the model + printed checks + check renders to %TEMP%/assetnew_check/FUR-01/
#   export = build + FBX (+ .fbm) + collection-only .blend (for make_lod1.py) + ONE preview + FBX re-import verify
#            + geometry dump (JSON, SHA1 for the live/headless comparison)
#   verify = only re-import the FBX in art/ (run after make_lod1.py, which rewrites the FBX with _Low1 children)
#   dump   = build + geometry dump only (live: compare with the headless export)
#   LOD1 (catalogue: yes; `Seat` stays a separate node):
#     blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#       --python Tools/blender/make_lod1.py -- --art <ABSOLUTE repo>/art/CottageGardenDecor FMS_Garden_Swing
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\FUR-01_Swing\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FUR-01', 'build']})
#   Live mode touches only the collection FUR-01_Swing (moving part named FMS_Garden_Swing_Seat there). Headless the
#   collection is FMS_Garden_Swing and the moving part carries the bare spec name `Seat` (the .blend that make_lod1.py
#   re-exports keeps it, so the final FBX has `Seat` + `Seat_Low1`).
# Axes (Blender): X = along the top beam (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: root = centre of the footprint on the ground. `Seat` (bench + cushion + 4 hanger rods + seat brackets) pivots
#   on the top-beam axis (0, 0, 2.04) Blender = (0, 2.04, 0) Unity; rotation axis X, rest 0, travel +-30 deg.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FUR-01')
NAME = 'FMS_Garden_Swing'
PREVIEW = 'FMS_Garden_FUR_01_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 1600
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, CREAM, CREAM_D, IRON = 0, 1, 3, 4, 13
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FUR-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'FUR-01_Swing' if LIVE else NAME
SEAT_NAME = (NAME + '_Seat') if LIVE else 'Seat'

# ---- dimensions (spec prompts/FUR-01.3d.md; reference planning/CottageGardenDecor/references/FUR-01.png, see notes.md) ----
# A-frame
LEG_X, LEG_W = 1.10, 0.12                    # frame planes X = +-1.10, legs 0.12 square, plain (spec: 8-12 tris per leg)
FOOT_Y = 0.687                               # leg centre at the ground; outer leg face at the ground = 0.75 (depth 1.50)
Z_AXIS = 2.04                                # top beam axis = seat pivot (functional)
BEAM_X, BEAM_H = 1.24, 0.12                  # beam 0.12 square, top 2.10; ends 7 cm past the apex blocks (reference stub)
APEX_X0, APEX_X1, APEX_Y, APEX_Z0, APEX_Z1 = 1.03, 1.17, 0.10, 1.92, 2.16   # apex block (reference: 6 cm over the beam), 1 cm proud of the legs
BRACE_Z, BRACE_W = 0.45, 0.10                # cross-brace centre height (spec), 0.10 square
CLAMP_X, CLAMP_W, CLAMP_Y, CLAMP_Z0, CLAMP_Z1 = 0.84, 0.08, 0.075, 1.93, 2.06   # iron hanger clamps under the beam
# Seat (moving)
SEAT_X, SEAT_Y, Z_SEAT0, Z_SEAT1 = 0.80, 0.225, 0.40, 0.45   # plank seat 1.6 x 0.45 x 0.05, top 0.45 (functional)
APRON_X, APRON_Y0, APRON_Y1, Z_APRON0 = 0.79, 0.175, 0.215, 0.35   # front / rear aprons under the seat (1 cm inset)
POST_X0, POST_X1 = 0.745, 0.805             # side frames: arm post (front) and back post, 0.06 square, 5 mm proud
ARM_Y0, ARM_Y1 = -0.23, -0.17                # front arm post Y
ARM_X0, ARM_X1, ARM_FRONT, Z_ARM0, Z_ARM1 = 0.72, 0.81, -0.25, 0.70, 0.765  # armrest 0.09 x 0.065 (reference)
BACK_TILT = math.radians(10)                 # backrest leans back 10 deg
BACK_O = Vector((0.0, 0.20, 0.35))           # backrest plane origin (bottom of the back posts, post centre line)
BACK_POST_L = 0.70                           # back post length along the tilt (top z ~1.04)
RAIL_X = 0.775                               # rails end 3 cm inside the back posts
RAIL_B, RAIL_T = (0.22, 0.27), (0.59, 0.66)  # bottom / top rail (v range along the tilt), depth 0.04
SLAT_N, SLAT_W, SLAT_D, SLAT_V = 8, 0.05, 0.03, (0.26, 0.60)   # vertical back slats 0.05 x 0.03, 1 cm into the rails
CUSH_X, CUSH_Y0, CUSH_Y1, Z_CUSH0, Z_CUSH1 = 0.70, -0.22, 0.17, 0.445, 0.545  # cushion 1.40 x 0.39 x 0.10 (reference; 5 mm sunk)
ROD_X, ROD_R = 0.84, 0.019                   # hanger rods: 8-sided, 0.035 across flats, plane X = +-0.84
ROD_YB, ROD_ZB, ROD_ZEND = 0.22, 0.50, 0.44  # rod line passes (+-0.84, +-0.22, 0.50) and ends inside the bracket
BRK_X0, BRK_X1, BRK_Y0, BRK_Y1, BRK_Z0, BRK_Z1 = 0.785, 0.885, 0.195, 0.255, 0.34, 0.47   # iron corner brackets


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


def back_pt(x, v, d=0.0):
    """point in the tilted backrest frame: v up along the 10 deg tilt, d along the backrest normal (rear +)"""
    s, c = math.sin(BACK_TILT), math.cos(BACK_TILT)
    return Vector((x, BACK_O.y + v * s + d * c, BACK_O.z + v * c - d * s))


def tilted_box(P, cn, x0, x1, v0, v1, dd, slot):
    """box in the backrest frame: X x0..x1, v0..v1 along the tilt, depth +-dd/2 (12 tris)"""
    c0 = back_pt((x0 + x1) / 2, v0); c1 = back_pt((x0 + x1) / 2, v1)
    pc.sweep(P, cn, c0, c1, sq(x1 - x0, dd), [(0, 1, 0), (1, 1, 0)], slot, slot, slot, ref=(1, 0, 0))


def leg_y(z):
    return FOOT_Y * (1 - z / Z_AXIS)


# ---------------- parts ----------------
FRAME_PARTS = (('EndFrame_A', -1), ('EndFrame_B', 1), ('Beam', 0))   # A = Blender -X end frame, B = +X, Beam = beam + clamps


def build_frame(name='Frame', side=None):
    """the static frame. side None = whole frame (used for the checks); -1 / +1 = one end frame (legs, apex block, brace);
    0 = beam + hanger clamps. The exported frame is split into these three parts of <= 60 tris each: make_lod1.py keeps
    such small parts unchanged (decimating 12-tri boxes to 50 % turns legs into wedges and braces into slivers)."""
    P = Part(name)
    for sx in (-1, 1):
        if side not in (None, sx): continue
        x = sx * LEG_X
        for sy in (-1, 1):                     # leg from the foot to the apex point on the beam axis, foot cut flat on z = 0
            pc.sweep(P, 'Legs', (x, sy * FOOT_Y, 0.0), (x, 0.0, Z_AXIS), sq(LEG_W, LEG_W), [(0, 1, 0), (1, 1, 0)],
                     WOOD, WOOD, WOOD, ref=(1, 0, 0), flat0=True, ground=True)
        x0, x1 = sorted((sx * APEX_X0, sx * APEX_X1))
        obox(P, 'Apex', x0, x1, -APEX_Y, APEX_Y, APEX_Z0, APEX_Z1, WOOD, WOOD, WOOD)
        yb = leg_y(BRACE_Z)                    # brace ends on the leg centre lines (inside the legs)
        obox(P, 'Braces', x - BRACE_W / 2, x + BRACE_W / 2, -yb, yb, BRACE_Z - BRACE_W / 2, BRACE_Z + BRACE_W / 2,
             WOOD_D, WOOD_D, WOOD_D)
    if side in (None, 0):
        obox(P, 'Beam', -BEAM_X, BEAM_X, -BEAM_H / 2, BEAM_H / 2, Z_AXIS - BEAM_H / 2, Z_AXIS + BEAM_H / 2, WOOD, WOOD, WOOD)
        for sx in (-1, 1):
            obox(P, 'Clamps', sx * CLAMP_X - CLAMP_W / 2, sx * CLAMP_X + CLAMP_W / 2, -CLAMP_Y, CLAMP_Y, CLAMP_Z0, CLAMP_Z1,
                 IRON, IRON, IRON)
    return P


def build_seat():
    P = Part('Seat')
    obox(P, 'SeatBoard', -SEAT_X, SEAT_X, -SEAT_Y, SEAT_Y, Z_SEAT0, Z_SEAT1, WOOD, WOOD, WOOD)
    for sy in (-1, 1):
        y0, y1 = sorted((sy * APRON_Y0, sy * APRON_Y1))
        obox(P, 'Aprons', -APRON_X, APRON_X, y0, y1, Z_APRON0, Z_SEAT0 + 0.005, WOOD, WOOD, WOOD)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * POST_X0, sx * POST_X1))
        obox(P, 'ArmPosts', x0, x1, ARM_Y0, ARM_Y1, Z_APRON0 + 0.005, Z_ARM0 + 0.005, WOOD, WOOD, WOOD)
        tilted_box(P, 'BackPosts', x0, x1, 0.0, BACK_POST_L, 0.06, WOOD)
        a0, a1 = sorted((sx * ARM_X0, sx * ARM_X1))
        arm_y1 = back_pt(0, (Z_ARM0 - BACK_O.z) / math.cos(BACK_TILT)).y + 0.025   # into the back post
        obox(P, 'Armrests', a0, a1, ARM_FRONT, arm_y1, Z_ARM0, Z_ARM1, WOOD, WOOD, WOOD)
    for v0, v1 in (RAIL_B, RAIL_T):
        tilted_box(P, 'Rails', -RAIL_X, RAIL_X, v0, v1, 0.04, WOOD)
    span = 2 * POST_X0
    for i in range(SLAT_N):
        xc = -POST_X0 + span * (i + 0.5) / SLAT_N
        tilted_box(P, 'Slats', xc - SLAT_W / 2, xc + SLAT_W / 2, SLAT_V[0], SLAT_V[1], SLAT_D, WOOD)
    # cushion: slightly rounded box (8-sided chamfered outline, softened top and bottom edges)
    cy, w, h, c = (CUSH_Y0 + CUSH_Y1) / 2, 2 * CUSH_X, CUSH_Y1 - CUSH_Y0, 0.03
    def ring(z, d): return [Vector((x, cy + y, z)) for x, y in pc.chamf_rect(w - 2 * d, h - 2 * d, c)]
    P.loft('Cushion', [ring(Z_CUSH0, 0.015), ring(Z_CUSH0 + 0.02, 0.0), ring(Z_CUSH1 - 0.025, 0.0), ring(Z_CUSH1, 0.02)],
           lambda j, k: CREAM_D if j == 0 else CREAM, CREAM_D, CREAM)
    # hangers + corner brackets
    for sx in (-1, 1):
        bx0, bx1 = sorted((sx * BRK_X0, sx * BRK_X1))
        for sy in (-1, 1):
            by0, by1 = sorted((sy * BRK_Y0, sy * BRK_Y1))
            obox(P, 'Brackets', bx0, bx1, by0, by1, BRK_Z0, BRK_Z1, IRON, IRON, IRON)
            top = Vector((sx * ROD_X, 0.0, Z_AXIS)); mid = Vector((sx * ROD_X, sy * ROD_YB, ROD_ZB))
            end = top + (mid - top) * ((Z_AXIS - ROD_ZEND) / (Z_AXIS - ROD_ZB))
            pc.sweep(P, 'Rods', end, top, pc.ngon(ROD_R, 8, math.pi / 8), [(0, 1, 0), (1, 1, 0)], IRON, IRON, IRON, ref=(1, 0, 0))
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
    """BVH of the named components of a Part (world coordinates, before to_object)"""
    from mathutils.bvhtree import BVHTree
    P.bm.verts.index_update()
    vs = [v.co.copy() for v in P.bm.verts]
    polys = [[v.index for v in f.verts] for nm, fs, _ in P.comp if nm in names for f in fs]
    return BVHTree.FromPolygons(vs, polys), vs


def swing_check(Pf, Ps):
    """functional checks of the moving seat: clearance to the A-frame at rest, ground and frame clearance over +-30 deg"""
    from mathutils.bvhtree import BVHTree
    legs, _ = comp_tree(Pf, {'Legs', 'Braces', 'Apex'})
    Ps.bm.verts.index_update()
    sv = [v.co.copy() for v in Ps.bm.verts]; sp = [[v.index for v in f.verts] for f in Ps.bm.faces]
    rest = min(legs.find_nearest(p)[3] for p in sv)
    seat_x = max(abs(p.x) for p in sv); leg_x = LEG_X - LEG_W / 2
    ok = rest >= 0.15 - 1e-6
    print(f'  SWING clearance seat -> legs/braces at rest {rest:.4f} (want >= 0.15) {"OK" if rest >= 0.15 - 1e-6 else "FAIL"}'
          f' | seat max |x| {seat_x:.3f}, leg inner face {leg_x:.3f}')
    piv = Vector((0, 0, Z_AXIS)); worst = (9.0, 0)
    for a in range(-30, 31, 5):
        R = Matrix.Rotation(math.radians(a), 3, 'X')
        rv = [piv + R @ (p - piv) for p in sv]
        mz = min(p.z for p in rv)
        hit = BVHTree.FromPolygons(rv, sp).overlap(legs)
        if mz < worst[0]: worst = (mz, a)
        if mz <= 0 or hit:
            ok = False; print(f'  SWING {a:+d} deg: min z {mz:.3f} frame overlap {len(hit)} FAIL')
    print(f'  SWING +-30 deg: lowest seat point {worst[0]:.3f} at {worst[1]:+d} deg, no overlap with legs/braces/apex -> '
          f'{"OK" if ok else "FAIL"}')
    return ok


def functional_report(obs):
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    seat = obs['Seat']; sp = [seat.matrix_world @ v.co for v in seat.data.vertices]
    rows = [('seat pivot (beam axis)', (seat.matrix_world.translation - Vector((0, 0, Z_AXIS))).length, 0.0, 'eq'),
            ('seat board top', Z_SEAT1, 0.45, 'eq'),
            ('seat bottom above ground at rest', min(p.z for p in sp), 0.30, 'ge'),
            ('width X', hi[0] - lo[0], 2 * BEAM_X, 'eq'),
            ('depth Y', hi[1] - lo[1], 1.50, 'near'),
            ('total height', hi[2], APEX_Z1, 'eq'),
            ('min z (ground contact)', lo[2], 0.0, 'eq')]
    ok = True
    for nm, got, want, how in rows:
        good = got >= want - 1e-3 if how == 'ge' else (abs(got - want) <= 0.01 if how == 'near' else abs(got - want) <= 1e-3)
        ok &= good
        print(f'  FUNC {nm}: {got:.4f} (want {">= " if how == "ge" else ""}{want}) {"OK" if good else "FAIL"}')
    return ok


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    Pf, Ps = build_frame(), build_seat()
    tris = {'Frame': part_tris(Pf), 'Seat': part_tris(Ps)}
    sw = swing_check(Pf, Ps)
    print('  whole frame (before the split):'); pc.comp_checks(Pf); Pf.bm.free()
    obs = {}
    for nm, side in FRAME_PARTS:
        P = build_frame(nm, side)
        skip = () if side == 0 else tuple({c for c, _, _ in P.comp})     # an end frame alone is not X-symmetric
        obs[nm] = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    obs['Seat'] = pc.to_object(Ps, NAME, coll, mat, (0, 0, Z_AXIS), root, mirror_skip=())
    obs['Seat'].name = SEAT_NAME; obs['Seat'].data.name = SEAT_NAME
    if obs['Seat'].name != SEAT_NAME: raise RuntimeError(f'seat name clash: {obs["Seat"].name}')
    bpy.context.view_layer.update()
    print(f'== {NAME}')
    tot = pc.report(obs)
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    for o in obs.values(): pc.coplanar_overlaps(o)
    print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values())))
    part_contacts(obs)
    f = functional_report(obs)
    print('  FUNCTIONAL', 'OK' if (f and sw) else 'FAIL')
    return coll, root, obs, img, mat


def all_coplanar(obs):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_FUR01_all'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_FUR01_all', me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def part_contacts(obs):
    """every part touches another part (BVH overlap)"""
    from mathutils.bvhtree import BVHTree
    trees = {}
    for k, o in obs.items():
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        trees[k] = BVHTree.FromPolygons(vs, [p.vertices for p in o.data.polygons])
    for k in trees:
        hits = [j for j in trees if j != k and trees[k].overlap(trees[j])]
        print(f'  contact {k}: touches {hits} {"OK" if hits else "FAIL"}')


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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), swing=0.0):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_FUR01_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_FUR01_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    seat = next((o for o in objs if o.name == SEAT_NAME), None); rot0 = None
    if seat is not None and swing:
        rot0 = seat.rotation_euler.copy(); seat.rotation_euler.x = math.radians(swing); bpy.context.view_layer.update()
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_FUR01_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_FUR01_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_FUR01_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_FUR01_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_FUR01_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    bpy.context.view_layer.update()
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
    try:
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        if rot0 is not None: seat.rotation_euler = rot0
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


def export_one(coll, root, seat, fbx):
    """the moving part carries the bare spec name `Seat` inside the FBX; the owner's selection / active object are restored"""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    old = seat.name; seat.name = 'Seat'
    if seat.name != 'Seat': raise RuntimeError(f'another object is named Seat: got {seat.name}')
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        seat.name = old
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act
    return fbx


VIEW_REF = (0.42, -0.88, 0.50)                     # reference: front-right (right frame nearer), ~27 deg, wide lens
VIEW_PREVIEW = (0.85, -1.25, 0.75)                 # series preview 3/4 (~25-30 deg), front-right, as STR-01 / STR-03

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, obs, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs, os.path.join(CHECK_DIR, f'FUR-01_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.80, fill_h=0.85, lens=32)
        render(objs, os.path.join(CHECK_DIR, f'FUR-01_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'FUR-01_swing30_{tag}.png'), (1.0, 0.0, 0.15), res=(900, 800), lens=70, swing=30)
        render(objs, os.path.join(CHECK_DIR, f'FUR-01_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_one(coll, root, obs['Seat'], os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()), os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
