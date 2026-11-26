# build.py - STR-03 Arbor with built-in bench (FMS_Garden_Arbor_Bench), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build (shared, read only).
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- STR-03 build|export|verify
#   build  = build the model + printed checks + check renders to %TEMP%/assetnew_check/STR-03/
#   export = build + FBX (+ .fbm) + collection-only .blend (for make_lod1.py) + ONE preview + FBX re-import verify
#            + geometry dump (JSON, SHA1 for the live/headless comparison)
#   verify = only re-import the FBX in art/ (run after make_lod1.py, which rewrites the FBX with _Low1 children)
#   dump   = build + geometry dump only (live: compare with the headless export)
#   LOD1 (catalogue: yes):
#     blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#       --python Tools/blender/make_lod1.py -- --art <ABSOLUTE repo>/art/AssetNew FMS_Garden_Arbor_Bench
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\STR-03_Arbor_Bench\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-03', 'build']})
#   Live mode touches only the collection STR-03_Arbor_Bench. Headless the collection is named FMS_Garden_Arbor_Bench
#   (make_lod1.py looks the collection up by the asset name).
# Axes (Blender): X = across (Unity X), -Y = front / open side (Unity +Z, FBX -Z forward), Z = up (Unity Y).
#   Spec (Unity) back wall Z = -0.34 -> Blender Y = +0.34; seat front edge Z +0.30 -> Blender Y = -0.30.
# Pivot: centre of the footprint on the ground.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'STR-03')
NAME = 'FMS_Garden_Arbor_Bench'
PREVIEW = 'FMS_Garden_STR_03_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 1600
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WHITE = 0, 10
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part
from pack_shapes import fill, tube

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-03'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'STR-03_Arbor_Bench' if LIVE else NAME

# ---- dimensions (spec prompts/STR-03.3d.md; reference planning/AssetNew/references/STR-03.png, see notes.md) ----
POST_X, POST_Y, POST_W, POST_C = 0.84, 0.34, 0.12, 0.01       # 4 posts, chamfer 0.01 on the long edges
Z_POST_TOP = 1.97                                              # post top 2 cm inside the rafter seat (no coplanar caps)
# arch rafters (front Y -0.34, rear Y +0.34): 0.10 x 0.10, seated flat on the post tops (z 1.95). The crown is lowered
# so that the cross slats on it top out at the catalogue height 2.30 (= Plant_Top); rafter crown top 2.248.
RAF_T, RAF_H, RAF_N = 0.10, 0.10, 8
RAF_X = 0.895                                                  # end faces 5 mm inside the post outer faces (0.90)
RAF_XI = 0.775                                                 # flat seat on the post, step 5 mm inside the post inner face
# cross slats on the arch: 0.06 square, along Y over both rafters (ends 5 mm inside the rafter outer faces),
# radial (symmetric), bottom 8 mm into the rafter circle (>= 4 mm into the 8-segment polyline)
XSL_XS, XSL_W, XSL_Y, XSL_SEAT = (-0.72, -0.36, 0.0, 0.36, 0.72), 0.06, 0.385, 0.008
Z_RAF0, Z_TOP = 1.95, 2.30
Z_CROWN = Z_TOP - XSL_W + XSL_SEAT                             # 2.248
R_TOP = ((0.90 ** 2) + (Z_CROWN - Z_RAF0 - RAF_H) ** 2) / (2 * (Z_CROWN - Z_RAF0 - RAF_H))   # circle through (+-0.9, 2.05) and the crown
Z_C = Z_CROWN - R_TOP
# lattice panels: rim (one closed frame ring) + 2-layer diagonal lattice
RIM_T, RIM_W = 0.05, 0.05                                      # rim thickness (across the panel) and face width
SIDE_Y, SIDE_Z0, SIDE_Z1 = 0.282, 0.15, 1.94                   # side panels X = +-0.84: 2 mm into the posts, 1 cm under the post top
BACK_X, BACK_Y, BACK_Z0, BACK_Z1 = 0.782, 0.34, 0.44, 1.94     # back panel: bottom 1 cm inside the seat (lattice starts at the seat)
SLAT_W, SLAT_GAP, SLAT_D = 0.05, 0.10, 0.03                    # 0.05 slats (MOD-01 / reference), 0.10 clear gaps, 45 deg
PITCH = (SLAT_W + SLAT_GAP) * math.sqrt(2)                     # spacing of the slat lines measured along the vertical
# bench (seat height 0.45 = functional)
SEAT_X, SEAT_Y0, SEAT_Y1, Z_SEAT0, Z_SEAT1 = 0.79, -0.30, 0.32, 0.38, 0.45   # 0.07 slab (reference), post to post, front edge -> into the back rim
LEG_X, LEG_W, LEG_YF, LEG_YR = 0.62, 0.09, -0.24, 0.255        # 4 legs 0.09 square (centres; reference ~0.09)
Z_RAIL0, Z_RAIL1 = 0.28, 0.385                                 # front rail 0.06 x 0.10(5) under the seat edge, 5 mm into the seat
RAIL_Y0, RAIL_Y1 = -0.275, -0.215
SRAIL_T, Z_SRAIL0 = 0.04, 0.30                                 # side rails front leg -> rear leg


# ---------------- small geometry helpers ----------------
def obox(P, cn, x0, x1, y0, y1, z0, z1, sx, sy, sz, ground=False):
    """axis-aligned box (12 tris), slot per face direction: sx for the +-X faces, sy for +-Y, sz for +-Z"""
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], sz), P.face([v[4], v[5], v[7], v[6]], sz),
          P.face([v[0], v[1], v[5], v[4]], sy), P.face([v[2], v[6], v[7], v[3]], sy),
          P.face([v[0], v[4], v[6], v[2]], sx), P.face([v[1], v[3], v[7], v[5]], sx)]
    P.comp.append((cn, fs, ground))


def clip_line(q0, d, poly):
    """Cyrus-Beck: parameter range [l0, l1] of the line q0 + l*d inside the convex CCW polygon (None if outside)"""
    l0, l1 = -1e9, 1e9
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        n = (b[1] - a[1], -(b[0] - a[0]))
        num = n[0] * (q0[0] - a[0]) + n[1] * (q0[1] - a[1]); den = n[0] * d[0] + n[1] * d[1]
        if abs(den) < 1e-12:
            if num > 0: return None
            continue
        t = -num / den
        if den > 0: l1 = min(l1, t)
        else: l0 = max(l0, t)
    return (l0, l1) if l1 > l0 else None


def lattice(P, cname, inner, embed, uc, v0, to3d, depth_ref, layers, slot):
    """the shared lattice (as STR-01 / MOD-01): 45 deg slats, real gaps, two layers (A up-right, B up-left) crossing
    with an overlap in depth; slat ends cut square half-way inside the rim. inner = visible opening (convex CCW, 2D u/v),
    embed = the same grown into the rim. to3d(u, v, depth) -> 3D. layers = (depth centre A, depth centre B, half depth)."""
    dA, dB, hd = layers; n = 0
    for fam, d, dc in (('A', (1 / math.sqrt(2), 1 / math.sqrt(2)), dA), ('B', (-1 / math.sqrt(2), 1 / math.sqrt(2)), dB)):
        for k in range(-40, 41):
            q0 = (uc, v0 + k * PITCH)
            vis = clip_line(q0, d, inner); emb = clip_line(q0, d, embed)
            if vis is None or emb is None or vis[1] - vis[0] < 0.04: continue
            p0 = (q0[0] + d[0] * emb[0], q0[1] + d[1] * emb[0]); p1 = (q0[0] + d[0] * emb[1], q0[1] + d[1] * emb[1])
            prof = [(hd, SLAT_W / 2), (-hd, SLAT_W / 2), (-hd, -SLAT_W / 2), (hd, -SLAT_W / 2)]
            pc.sweep(P, cname, to3d(p0[0], p0[1], dc), to3d(p1[0], p1[1], dc), prof, [(0, 1, 0), (1, 1, 0)],
                     slot, slot, slot, ref=depth_ref)
            n += 1
    return n


def xz_plate(P, cname, outer, y0, y1, slot):
    """vertical plate in the XZ plane from a CCW outline [(x, z)] (may be concave), thickness y0..y1 (scanfill caps)"""
    of = [P.bm.verts.new((x, y0, z)) for x, z in outer]; ob = [P.bm.verts.new((x, y1, z)) for x, z in outer]
    faces = fill(P, [of], slot, (0, -1, 0)) + fill(P, [ob], slot, (0, 1, 0)) + tube(P, of, ob, slot)
    P.comp.append((cname, faces, False))


def z_top(x):
    return Z_C + math.sqrt(R_TOP ** 2 - x * x)


def rafter_outline():
    """CCW (x, z): flat seats on the post tops, inner arc (radius R-0.10) between them, top arc (8 segments)"""
    ri = R_TOP - RAF_H
    a_in = math.asin(RAF_XI / ri); a_top = math.asin(RAF_X / R_TOP)
    inner = [(ri * math.sin(-a_in + 2 * a_in * k / RAF_N), Z_C + ri * math.cos(-a_in + 2 * a_in * k / RAF_N)) for k in range(RAF_N + 1)]
    top = [(R_TOP * math.sin(a_top - 2 * a_top * k / RAF_N), Z_C + R_TOP * math.cos(a_top - 2 * a_top * k / RAF_N)) for k in range(RAF_N + 1)]
    return [(-RAF_X, Z_RAF0), (-RAF_XI, Z_RAF0)] + inner + [(RAF_XI, Z_RAF0), (RAF_X, Z_RAF0)] + top


def panel_ring_yz(P, c, y, z0, z1):
    def rect(x, yy, za, zb): return [Vector((x, -yy, za)), Vector((x, yy, za)), Vector((x, yy, zb)), Vector((x, -yy, zb))]
    yi, z0i, z1i = y - RIM_W, z0 + RIM_W, z1 - RIM_W
    P.torus_loft('Rims', [rect(c - RIM_T / 2, y, z0, z1), rect(c + RIM_T / 2, y, z0, z1),
                          rect(c + RIM_T / 2, yi, z0i, z1i), rect(c - RIM_T / 2, yi, z0i, z1i)], WHITE)


def panel_ring_xz(P, yc, x, z0, z1):
    def rect(yy, xx, za, zb): return [Vector((-xx, yy, za)), Vector((xx, yy, za)), Vector((xx, yy, zb)), Vector((-xx, yy, zb))]
    xi, z0i, z1i = x - RIM_W, z0 + RIM_W, z1 - RIM_W
    P.torus_loft('Rims', [rect(yc - RIM_T / 2, x, z0, z1), rect(yc + RIM_T / 2, x, z0, z1),
                          rect(yc + RIM_T / 2, xi, z0i, z1i), rect(yc - RIM_T / 2, xi, z0i, z1i)], WHITE)


# ---------------- parts ----------------
def build_frame():
    P = Part('Frame')
    for sx in (-1, 1):
        for sy in (-1, 1):
            pc.rect_prism(P, 'Posts', sx * POST_X, sy * POST_Y, POST_W, POST_W, POST_C, [(0.0, 0), (Z_POST_TOP, 0)],
                          WHITE, WHITE, WHITE, ground=True)
    out = rafter_outline()
    for sy in (-1, 1):
        xz_plate(P, 'Rafters', out, sy * POST_Y - RAF_T / 2, sy * POST_Y + RAF_T / 2, WHITE)
    for x in XSL_XS:                                   # radial on the rafter circle, seated XSL_SEAT
        p = Vector((x, z_top(x))); nrm = (p - Vector((0.0, Z_C))).normalized()
        c = p + nrm * (XSL_W / 2 - XSL_SEAT)
        e1 = Vector((nrm.x, 0, nrm.y)); h = XSL_W / 2
        prof = [(h, h), (-h, h), (-h, -h), (h, -h)]
        pc.sweep(P, 'CrossSlats', (c.x, -XSL_Y, c.y), (c.x, XSL_Y, c.y), prof, [(0, 1, 0), (1, 1, 0)],
                 WHITE, WHITE, WHITE, ref=tuple(e1))
    return P


def build_panels():
    P = Part('Panels')
    # side panels in the YZ plane on the post axis X = +-0.84
    yi, z0i, z1i = SIDE_Y - RIM_W, SIDE_Z0 + RIM_W, SIDE_Z1 - RIM_W
    e = RIM_W / 2
    for sx in (-1, 1):
        c = sx * POST_X
        panel_ring_yz(P, c, SIDE_Y, SIDE_Z0, SIDE_Z1)
        inner = [(-yi, z0i), (yi, z0i), (yi, z1i), (-yi, z1i)]
        embed = [(-yi - e, z0i - e), (yi + e, z0i - e), (yi + e, z1i + e), (-yi - e, z1i + e)]
        lattice(P, 'LatticeSide', inner, embed, 0.0, (z0i + z1i) / 2, lambda u, v, dd, c=c: Vector((c + dd, u, v)),
                (1, 0, 0), (sx * 0.007, -sx * 0.007, SLAT_D / 2), WHITE)
    # back panel in the XZ plane at Y = +0.34 (rear posts), from the seat up
    xi, z0i, z1i = BACK_X - RIM_W, BACK_Z0 + RIM_W, BACK_Z1 - RIM_W
    panel_ring_xz(P, BACK_Y, BACK_X, BACK_Z0, BACK_Z1)
    inner = [(-xi, z0i), (xi, z0i), (xi, z1i), (-xi, z1i)]
    embed = [(-xi - e, z0i - e), (xi + e, z0i - e), (xi + e, z1i + e), (-xi - e, z1i + e)]
    lattice(P, 'LatticeBack', inner, embed, 0.0, (z0i + z1i) / 2, lambda u, v, dd: Vector((u, BACK_Y + dd, v)),
            (0, 1, 0), (0.007, -0.007, SLAT_D / 2), WHITE)
    return P


def build_bench():
    P = Part('Bench')
    obox(P, 'Seat', -SEAT_X, SEAT_X, SEAT_Y0, SEAT_Y1, Z_SEAT0, Z_SEAT1, WOOD, WOOD, WOOD)
    h = LEG_W / 2
    for sx in (-1, 1):
        for yc in (LEG_YF, LEG_YR):
            obox(P, 'Legs', sx * LEG_X - h, sx * LEG_X + h, yc - h, yc + h, 0.0, Z_RAIL1 + 0.005, WHITE, WHITE, WHITE, ground=True)
        obox(P, 'Rails', sx * LEG_X - SRAIL_T / 2, sx * LEG_X + SRAIL_T / 2, LEG_YF + h - 0.01, LEG_YR - h + 0.01,
             Z_SRAIL0, Z_RAIL1, WHITE, WHITE, WHITE)
    obox(P, 'Rails', -LEG_X + h - 0.01, LEG_X - h + 0.01, RAIL_Y0, RAIL_Y1, Z_RAIL0, Z_RAIL1, WHITE, WHITE, WHITE)
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


def ekey(e):
    return e.name.rsplit('Plant_', 1)[-1]                       # 'L' / 'R' / 'Top'


def empties(coll, root):
    """spec names Plant_L / Plant_R / Plant_Top. Headless (the .blend that make_lod1.py re-exports) they carry the bare
    names; live they are prefixed <asset>_Plant_* so they do not clash with STR-01's empties in the owner's file."""
    out = []
    for nm, loc in (('Plant_L', (-POST_X, 0, 0)), ('Plant_R', (POST_X, 0, 0)), ('Plant_Top', (0, 0, Z_TOP))):
        e = bpy.data.objects.new((NAME + '_' + nm) if LIVE else nm, None); e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.15
        coll.objects.link(e); e.parent = root; e.location = loc; out.append(e)
    return out


def all_coplanar(obs):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_STR03_all'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_STR03_all', me)
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


def snap_report(obs, ems):
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    em = {ekey(o): o.matrix_world.translation for o in ems}
    bo = next(o for o in obs if o.name.endswith('_Bench'))
    seat_top = max((bo.matrix_world @ v.co).z for v in bo.data.vertices)
    clear_h = Z_C + math.sqrt((R_TOP - RAF_H) ** 2 - RAF_XI ** 2)      # rafter underside at the opening edge (lowest point)
    print(f'  INFO front clear height under the arch (opening edge) {clear_h:.3f}, at the centre {Z_CROWN - RAF_H:.3f}; '
          f'post tops / rafter seats 1.95')
    rows = [('inner clear width (post inner faces)', 2 * (POST_X - POST_W / 2), 1.50, 'ge'),
            ('seat top height', seat_top, 0.45, 'eq'),
            ('front clear height (ground -> rafter underside)', clear_h, 1.95, 'ge'),
            ('width X', hi[0] - lo[0], 1.80, 'eq'),
            ('depth Y', hi[1] - lo[1], 0.80, 'eq'),
            ('total height', hi[2], 2.30, 'eq'),
            ('min z (ground contact)', lo[2], 0.0, 'eq')]
    ok = True
    for nm, got, want, how in rows:
        good = got >= want - 1e-3 if how == 'ge' else abs(got - want) <= 1e-3; ok &= good
        print(f'  SNAP {nm}: {got:.4f} (want {">= " if how == "ge" else ""}{want}) {"OK" if good else "FAIL"}')
    for k, want in (('L', (-POST_X, 0, 0)), ('R', (POST_X, 0, 0)), ('Top', (0, 0, Z_TOP))):
        got = em.get(k); good = got is not None and (got - Vector(want)).length <= 1e-3; ok &= good
        print(f'  SNAP empty Plant_{k}: {None if got is None else [round(x, 4) for x in got]} {"OK" if good else "FAIL"}')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    obs, tris = {}, {}
    for P, skip in ((build_frame(), ()), (build_panels(), ('LatticeBack',)), (build_bench(), ())):
        tris[P.name] = part_tris(P)
        obs[P.name] = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    ems = empties(coll, root)
    bpy.context.view_layer.update()
    print(f'== {NAME}')
    tot = pc.report(obs)
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    for o in obs.values(): pc.coplanar_overlaps(o)
    print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values())))
    part_contacts(obs)
    snap_report(list(obs.values()), ems)
    return coll, root, obs, ems, img, mat


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        if ob.type == 'EMPTY':
            allv.append(['Plant_' + ekey(ob), [round(c, 5) for c in ob.matrix_world.translation]]); allf.append([]); continue
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
    sc = bpy.data.scenes.new('TMP_STR03_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_STR03_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_STR03_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_STR03_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_STR03_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_STR03_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_STR03_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(coll, root, ems, fbx):
    """the spec names the empties Plant_L / Plant_R / Plant_Top: bare names inside the FBX (prefixed in the .blend so they
    do not clash with STR-01's empties in the live file). The owner's selection / active object are restored."""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    keys = [ekey(e) for e in ems]; old = [e.name for e in ems]
    for e, k in zip(ems, keys): e.name = 'Plant_' + k
    names = [e.name for e in ems]
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        for e, o in zip(ems, old): e.name = o
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act
    print('  empties exported as', names)
    return fbx


VIEW_REF = (0.42, -0.91, 0.58)                     # reference: front-right (rear posts shift right), ~30 deg above
VIEW_PREVIEW = (0.85, -1.25, 0.75)                 # series preview 3/4 (~25 deg, as STR-01), same side as the reference

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, obs, ems, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs, os.path.join(CHECK_DIR, f'STR-03_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.80, fill_h=0.85, lens=70)
        render(objs, os.path.join(CHECK_DIR, f'STR-03_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'STR-03_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_one(coll, root, ems, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()) + ems, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
