# build.py - STR-01 Rose arch, wooden (FMS_Garden_Arch_Wood + _White, _Gate), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- STR-01 build|export|verify
#   build  = build all 3 models + printed checks + check renders to %TEMP%/assetnew_check/STR-01/
#   export = build + 3 FBX (base, _White, _Gate; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, for the live/headless comparison)
#   verify = only re-import the 3 FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\STR-01_Arch_Wood\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-01', 'build']})
#   Live mode touches only the collection STR-01_Arch_Wood and its two variant child collections.
# Axes (Blender): X = across the opening (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: centre of the footprint on the ground. No LOD (catalogue).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'STR-01')
NAME = 'FMS_Garden_Arch_Wood'
PREVIEW = 'FMS_Garden_STR_01_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 1000, '_White': 1000, '_Gate': 1300}
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, WHITE, IRON = 0, 1, 10, 13
COLL = 'STR-01_Arch_Wood'
VARIANTS = ('_White', '_Gate')
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part
from pack_shapes import fill, tube

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/STR-01.3d.md; reference planning/AssetNew/references/STR-01.png, see notes.md) ----
POST_X, POST_Y, POST_W, POST_C = 0.66, 0.24, 0.12, 0.01       # 4 posts, chamfer 0.01 on the long edges
Z_POST_TOP = 2.16                                              # post top buried in the lintel (no coplanar caps)
LINT_X, LINT_W, Z_LINT0, Z_LINT1 = 0.76, 0.14, 2.10, 2.22      # lintels 0.04 past the posts (reference), 1 cm wider than posts
PURL_W, PURL_Y, Z_PURL0, Z_PURL1 = 0.08, 0.35, 2.215, 2.30     # purlins along Y on the lintels (5 mm seated)
BEAM_X, BEAM_W, Z_BEAM0, Z_BEAM1 = 0.80, 0.07, 2.295, 2.40     # 5 cross-beams 1.6 long on the purlins (5 mm seated)
BEAM_YS = (-0.30, -0.15, 0.0, 0.15, 0.30)
RIM_T, RIM_W = 0.05, 0.05                                      # side panel rim: thickness (X) and face width
PAN_Y, Z_PAN0, Z_PAN1 = 0.182, 0.15, 2.09                      # panel rim outer: 2 mm into the posts, 1 cm under the lintel
SLAT_W, SLAT_GAP, SLAT_D = 0.03, 0.10, 0.03                    # lattice: 0.03 square slats, 0.10 clear gaps, 45 deg
PITCH = (SLAT_W + SLAT_GAP) * math.sqrt(2)                     # spacing of the slat lines measured along the vertical
# gate leaf (only _Gate)
HINGE_X = -0.59                                                # hinge axis (pivot of Gate_Leaf), X = -0.59, Y = 0
LEAF_X0, LEAF_X1, LEAF_T = -0.575, 0.525, 0.05                 # leaf body 1.10 wide, thickness behind the axis (Y 0..0.05)
Z_LEAF0, Z_SPRING, ARC_N = 0.10, 1.05, 12                      # bottom, arch springing line, 12 arch segments (radius 0.55)
STILE = 0.06
Z_BRAIL1, Z_MRAIL0, Z_MRAIL1 = 0.18, 0.84, 0.90                # bottom rail 0.10-0.18, mid rail 0.84-0.90
BOARD_N, BOARD_GAP = 5, 0.02


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
        n = (b[1] - a[1], -(b[0] - a[0]))                       # outward normal of a CCW edge
        num = n[0] * (q0[0] - a[0]) + n[1] * (q0[1] - a[1]); den = n[0] * d[0] + n[1] * d[1]
        if abs(den) < 1e-12:
            if num > 0: return None
            continue
        t = -num / den
        if den > 0: l1 = min(l1, t)
        else: l0 = max(l0, t)
    return (l0, l1) if l1 > l0 else None


def lattice(P, cname, inner, embed, uc, v0, to3d, depth_ref, layers, slot):
    """the shared lattice: 45 deg slats (SLAT_W wide, square-ish), real gaps SLAT_GAP, two layers (A up-right, B up-left)
    crossing with an overlap in depth. inner = visible opening (convex CCW, 2D u/v), embed = the same grown into the rim
    (slat ends stop half-way in the rim, square cut, so the corners stay inside it). to3d(u, v, depth) -> 3D point.
    layers = (depth centre A, depth centre B, half depth). Pattern centred on u = uc, crossings on the axis at v0 + k*PITCH."""
    dA, dB, hd = layers; n = 0
    for fam, d, dc in (('A', (1 / math.sqrt(2), 1 / math.sqrt(2)), dA), ('B', (-1 / math.sqrt(2), 1 / math.sqrt(2)), dB)):
        for k in range(-40, 41):
            q0 = (uc, v0 + k * PITCH)
            vis = clip_line(q0, d, inner); emb = clip_line(q0, d, embed)
            if vis is None or emb is None or vis[1] - vis[0] < 0.03: continue
            p0 = (q0[0] + d[0] * emb[0], q0[1] + d[1] * emb[0]); p1 = (q0[0] + d[0] * emb[1], q0[1] + d[1] * emb[1])
            prof = [(hd, SLAT_W / 2), (-hd, SLAT_W / 2), (-hd, -SLAT_W / 2), (hd, -SLAT_W / 2)]
            pc.sweep(P, cname, to3d(p0[0], p0[1], dc), to3d(p1[0], p1[1], dc), prof, [(0, 1, 0), (1, 1, 0)],
                     slot, slot, slot, ref=depth_ref)
            n += 1
    return n


def arc_pts(cx, cz, r, n, a0=0.0, a1=math.pi):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cz + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def xz_plate(P, cname, outer, holes, y0, y1, slot):
    """vertical plate in the XZ plane from a CCW outline [(x, z)] with through-holes, thickness y0..y1 (scanfill caps)"""
    bm = P.bm
    of = [bm.verts.new((x, y0, z)) for x, z in outer]; ob = [bm.verts.new((x, y1, z)) for x, z in outer]
    hf = [[bm.verts.new((x, y0, z)) for x, z in h] for h in holes]; hb = [[bm.verts.new((x, y1, z)) for x, z in h] for h in holes]
    faces = fill(P, [of] + hf, slot, (0, -1, 0)) + fill(P, [ob] + hb, slot, (0, 1, 0)) + tube(P, of, ob, slot)
    for a, b in zip(hf, hb): faces += tube(P, a, b, slot)
    P.comp.append((cname, faces, False))


# ---------------- the arch (shared by all three models) ----------------
def panel_crossings():
    """heights of the lattice crossings on the panel axis (Y = 0) - the gate pintles sit on two of them"""
    tmid = (Z_PAN0 + RIM_W + Z_PAN1 - RIM_W) / 2
    return [tmid + k * PITCH for k in range(-6, 7)]


def build_arch(wood, end, gate=False):
    P = Part('Body')
    for sx in (-1, 1):
        for sy in (-1, 1):
            pc.rect_prism(P, 'Posts', sx * POST_X, sy * POST_Y, POST_W, POST_W, POST_C, [(0.0, 0), (Z_POST_TOP, 0)],
                          wood, wood, wood, ground=True)
    for sy in (-1, 1):
        obox(P, 'Lintels', -LINT_X, LINT_X, sy * POST_Y - LINT_W / 2, sy * POST_Y + LINT_W / 2, Z_LINT0, Z_LINT1, wood, wood, wood)
    for sx in (-1, 1):
        obox(P, 'Purlins', sx * POST_X - PURL_W / 2, sx * POST_X + PURL_W / 2, -PURL_Y, PURL_Y, Z_PURL0, Z_PURL1, end, wood, wood)
    for y in BEAM_YS:
        obox(P, 'Beams', -BEAM_X, BEAM_X, y - BEAM_W / 2, y + BEAM_W / 2, Z_BEAM0, Z_BEAM1, end, wood, wood)
    # side panels: rim (one closed frame ring) + 2-layer lattice, in the YZ plane on the post axis X = +-0.66
    yi, z0i, z1i = PAN_Y - RIM_W, Z_PAN0 + RIM_W, Z_PAN1 - RIM_W
    for sx in (-1, 1):
        c = sx * POST_X
        def rect(x, y, za, zb): return [Vector((x, -y, za)), Vector((x, y, za)), Vector((x, y, zb)), Vector((x, -y, zb))]
        P.torus_loft('Rims', [rect(c - RIM_T / 2, PAN_Y, Z_PAN0, Z_PAN1), rect(c + RIM_T / 2, PAN_Y, Z_PAN0, Z_PAN1),
                              rect(c + RIM_T / 2, yi, z0i, z1i), rect(c - RIM_T / 2, yi, z0i, z1i)], wood)
        inner = [(-yi, z0i), (yi, z0i), (yi, z1i), (-yi, z1i)]
        e = RIM_W / 2
        embed = [(-yi - e, z0i - e), (yi + e, z0i - e), (yi + e, z1i + e), (-yi - e, z1i + e)]
        lattice(P, 'Lattice', inner, embed, 0.0, (z0i + z1i) / 2, lambda u, v, dd, c=c: Vector((c + dd, u, v)), (1, 0, 0),
                (sx * 0.007, -sx * 0.007, SLAT_D / 2), wood)
    if gate:                                   # static iron pintles for the leaf: from the panel (rim / inner slat layer) to the axis
        for t in gate_hinge_heights():
            obox(P, 'Pintles', -POST_X + 0.012, HINGE_X, -0.0125, 0.0125, t - 0.0125, t + 0.0125, IRON, IRON, IRON)
    return P


def gate_hinge_heights():
    cr = panel_crossings()
    return (min(cr, key=lambda t: abs(t - 0.20)), min(cr, key=lambda t: abs(t - 0.75)))


# ---------------- gate leaf (only _Gate), world coordinates, pivot = hinge axis ----------------
def build_leaf():
    P = Part('Gate_Leaf'); xc = (LEAF_X0 + LEAF_X1) / 2; r = (LEAF_X1 - LEAF_X0) / 2; ri = r - STILE
    xi0, xi1 = LEAF_X0 + STILE, LEAF_X1 - STILE
    outer = [(LEAF_X0, Z_LEAF0), (LEAF_X1, Z_LEAF0)] + arc_pts(xc, Z_SPRING, r, ARC_N)
    low = [(xi0, Z_BRAIL1), (xi1, Z_BRAIL1), (xi1, Z_MRAIL0), (xi0, Z_MRAIL0)]
    up = [(xi0, Z_MRAIL1), (xi1, Z_MRAIL1)] + arc_pts(xc, Z_SPRING, ri, ARC_N)
    xz_plate(P, 'Frame', outer, [low, up], 0.0, LEAF_T, WHITE)
    # lower half: 5 vertical boards (0.02 gaps), thinner than the frame, ends seated 1 cm in the rails / stiles
    bw = ((xi1 - xi0) - (BOARD_N - 1) * BOARD_GAP) / BOARD_N
    for i in range(BOARD_N):
        x0 = xi0 + i * (bw + BOARD_GAP); x1 = x0 + bw
        obox(P, 'Boards', x0 - (0.01 if i == 0 else 0), x1 + (0.01 if i == BOARD_N - 1 else 0), 0.012, 0.038,
             Z_BRAIL1 - 0.01, Z_MRAIL0 + 0.01, WHITE, WHITE, WHITE)
    # upper half: the shared lattice inside the arch rim
    inner = [(xi0, Z_MRAIL1), (xi1, Z_MRAIL1)] + arc_pts(xc, Z_SPRING, ri, 24)   # CCW: bottom edge, then the arc 0 -> 180 deg
    e = STILE / 2
    embed = [(xi0 - e, Z_MRAIL1 - 0.03), (xi1 + e, Z_MRAIL1 - 0.03)] + arc_pts(xc, Z_SPRING, ri + e, 24)
    lattice(P, 'Lattice', inner, embed, xc, Z_SPRING, lambda u, v, dd: Vector((u, dd, v)), (0, 1, 0),
            (0.0205, 0.0295, 0.0125), WHITE)
    # iron: knuckles on the axis, hinge straps on the front face (boards + stile), latch bar on the mid rail
    for t in gate_hinge_heights():
        obox(P, 'Hinges', HINGE_X - 0.016, LEAF_X0 + 0.003, -0.0165, 0.0165, t + 0.0145, t + 0.0645, IRON, IRON, IRON)
        obox(P, 'Hinges', HINGE_X, -0.25, -0.006, 0.014, t + 0.0195, t + 0.0595, IRON, IRON, IRON)
    obox(P, 'Latch', 0.38, 0.54, -0.006, 0.004, Z_MRAIL0 + 0.01, Z_MRAIL1 - 0.01, IRON, IRON, IRON)
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


def empties(asset, coll, root):
    out = []
    for nm, loc in (('Plant_L', (-POST_X, 0, 0)), ('Plant_R', (POST_X, 0, 0)), ('Plant_Top', (0, 0, Z_BEAM1))):
        e = bpy.data.objects.new(asset + '_' + nm, None); e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.15
        coll.objects.link(e); e.parent = root; e.location = loc; out.append(e)
    return out


def all_coplanar(obs, tag):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_STR01_all_' + tag); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_STR01_all_' + tag, me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def world_bvh(o, M=None):
    from mathutils.bvhtree import BVHTree
    M = M or o.matrix_world
    vs = [M @ v.co for v in o.data.vertices]
    return BVHTree.FromPolygons(vs, [p.vertices for p in o.data.polygons]), vs


def gate_checks(body, leaf):
    """leaf at 0 deg: gap to the arch; swing toward the front (-Y) about the hinge axis: first colliding angle"""
    tb, _ = world_bvh(body); tl, vl = world_bvh(leaf)
    gap = 0.0 if tb.overlap(tl) else min(tb.find_nearest(v)[3] for v in vl)
    free = None
    for a in range(0, 101, 1):
        M = Matrix.Translation(leaf.matrix_world.translation) @ Matrix.Rotation(math.radians(-a), 4, 'Z') @ \
            Matrix.Translation(-leaf.matrix_world.translation) @ leaf.matrix_world
        t2, _ = world_bvh(leaf, M)
        if tb.overlap(t2): free = a; break
    pts = [leaf.matrix_world @ v.co for v in leaf.data.vertices]
    gap_r = (POST_X - POST_W / 2) - max(p.x for p in pts)
    print(f'  GATE leaf pivot {[round(x, 3) for x in leaf.matrix_world.translation]} | gap leaf-arch at 0 deg {gap:.4f} | '
          f'gap to the right post {gap_r:.3f} (>= 0.05 {"OK" if gap_r >= 0.05 - 1e-6 else "FAIL"}) | swing toward front: '
          f'{"free 0..100 deg" if free is None else f"first contact at {free} deg"}')
    return gap, gap_r, free


def snap_report(objs_all):
    pts = [o.matrix_world @ v.co for o in objs_all if o.type == 'MESH' for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    em = {o.name.split('_Plant_')[-1] if '_Plant_' in o.name else o.name: o.matrix_world.translation for o in objs_all if o.type == 'EMPTY'}
    rows = [('opening width (post inner faces)', 2 * (POST_X - POST_W / 2), 1.20, 'ge'),
            ('opening height (ground -> lintel)', Z_LINT0, 2.10, 'ge'),
            ('top width (beams, PLT-03)', hi[0] - lo[0], 1.60, 'eq'),
            ('side depth incl. posts (PLT-02)', 2 * (POST_Y + POST_W / 2), 0.60, 'eq'),
            ('total height', hi[2], 2.40, 'eq'),
            ('min z (ground contact)', lo[2], 0.0, 'eq')]
    ok = True
    for nm, got, want, how in rows:
        good = got >= want - 1e-3 if how == 'ge' else abs(got - want) <= 1e-3; ok &= good
        print(f'  SNAP {nm}: {got:.4f} (want {"≥ " if how == "ge" else ""}{want}) {"OK" if good else "FAIL"}')
    for k, want in (('L', (-POST_X, 0, 0)), ('R', (POST_X, 0, 0)), ('Top', (0, 0, 2.40))):
        got = em.get(k); good = got is not None and (got - Vector(want)).length <= 1e-3; ok &= good
        print(f'  SNAP empty Plant_{k}: {None if got is None else [round(x, 4) for x in got]} {"OK" if good else "FAIL"}')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        gate = suf == '_Gate'
        P = build_arch(WHITE if suf else WOOD, WHITE if suf else WOOD_D, gate=gate); tris = {'Body': part_tris(P)}
        body = pc.to_object(P, asset, coll, mat, (0, 0, 0), root,
                            mirror_skip=('Pintles',) if gate else ())
        obs = {'Body': body}
        if gate:
            L = build_leaf(); tris['Gate_Leaf'] = part_tris(L)
            leaf = pc.to_object(L, asset, coll, mat, (HINGE_X, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in L.comp))
            leaf.name = 'Gate_Leaf'; leaf.data.name = asset + '_Gate_Leaf'; obs['Gate_Leaf'] = leaf
        ems = empties(asset, coll, root)
        bpy.context.view_layer.update()
        print(f'== {asset}')
        tot = pc.report(obs)
        print('  tris per component:', tris)
        print(f'  budget {BUDGET[suf]} ->', 'OK' if tot <= BUDGET[suf] else f'OVER x{tot / BUDGET[suf]:.2f}')
        for o in obs.values(): pc.coplanar_overlaps(o)
        print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values()), suf or 'base'))
        if gate: gate_checks(body, obs['Gate_Leaf'])
        if suf == '_White':                        # same mesh as the base, only the UV cells differ
            same = [tuple(round(c, 6) for c in v.co) for v in body.data.vertices] == \
                   [tuple(round(c, 6) for c in v.co) for v in res[''][2]['Body'].data.vertices]
            cells = sorted({cell_of(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
            print(f'  _White: same vertices as the base {same}; cells used {cells}')
        snap_report([root] + list(obs.values()) + ems)
        res[suf] = (coll, root, obs, ems, tot)
    return colls, img, mat, res


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        if ob.type == 'EMPTY':
            allv.append([ob.name, [round(c, 5) for c in ob.matrix_world.translation]]); allf.append([]); continue
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
    sc = bpy.data.scenes.new('TMP_STR01_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_STR01_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_STR01_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_STR01_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_STR01_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_STR01_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_STR01_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


def export_one(asset, coll, root, ems, fbx):
    """the spec names the empties Plant_L / Plant_R / Plant_Top: they carry these bare names only inside the FBX
    (Blender needs unique names across the three models, so they are <asset>_Plant_* in the .blend)"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    keys = [e.name.split('_Plant_')[-1] for e in ems]
    for e, k in zip(ems, keys): e.name = 'Plant_' + k
    names = [e.name for e in ems]
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        for e, k in zip(ems, keys): e.name = asset + '_Plant_' + k
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    print('  empties exported as', names)
    return fbx


VIEW_REF = (0.0, -1.0, math.tan(math.radians(34)))          # reference: straight front, ~34 deg above (beam gaps), wide lens
VIEW_PREVIEW = (0.85, -1.25, 0.75)                          # series preview 3/4 from the front-right (~25 deg)

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, o, e, t = res[suf]; return [r] + list(o.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-01_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.80, fill_h=0.85, lens=35)
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-01_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'STR-01_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_Gate'), os.path.join(CHECK_DIR, f'STR-01_gate_{tag}.png'), (0.35, -1.0, 0.3), res=(1000, 1000), fill_w=0.8, fill_h=0.85, lens=50)
        render(objs_of('_White'), os.path.join(CHECK_DIR, f'STR-01_white_{tag}.png'), VIEW_PREVIEW)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbxs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]
            fbxs.append(export_one(NAME + suf, c, r, e, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
        render(objs_of(''), os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        for f in fbxs: pc.verify(f)
    if MODE in ('export', 'dump'):
        allobs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]; allobs += list(o.values()) + e
        geom_dump(allobs, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
