# build.py - WTR-02 Wall fountain stele (FMS_Garden_Fountain_Wall), pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- WTR-02 build|export|verify|dump
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/WTR-02/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
#   verify = only re-import the FBX in art/
#   PACK_ART=<dir> redirects every art/ output (used for the headless reproduction run, so art/ is not overwritten).
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\WTR-02_Fountain_Wall\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['WTR-02', 'build']})
#   Live mode touches only the collection WTR-02_Fountain_Wall (other objects, scenes and the owner's .blend stay as they are).
# Axes (Blender): -Y = front (Unity +Z), Z = up (Unity Y), X = across (Unity -X; the model is X-symmetric).
# Pivot: centre of the BACK face of the stele on the ground (0, 0, 0). Everything lies at y <= 0: the back face is one flat
# polygon in the plane y = 0 (it sits against the MOD-03 coping, 0.22 from the wall axis).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
ATLAS_PATH = os.path.join(REPO, 'art', 'CottageGardenDecor', 'Textures', 'FMS_Garden_AtlasA.png')   # READ ONLY (loaded, never saved)
WALL_FBX = os.path.join(REPO, 'art', 'CottageGardenDecor', 'Meshes', 'FMS_Garden_Wall_Stone.fbx')    # MOD-03, read only (SNAP check)
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'WTR-02')
COLL = 'WTR-02_Fountain_Wall'
NAME = 'FMS_Garden_Fountain_Wall'
PREVIEW = 'FMS_Garden_WTR_02_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 900
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
METAL, METAL_D, METAL_L, LIME, STONE, WATER = 7, 8, 9, 11, 12, 15
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'WTR-02'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---------------- dimensions (references/WTR-02.png measured, see notes.md; reference wins over the spec numbers) --------
# Stele + gabled cap: one closed solid (ridge runs front-back, gable faces the front as in the reference).
SW, SD, CH = 0.35, 0.15, 0.02        # slab half width, depth, chamfer of the two front vertical edges
CW, CD = 0.40, 0.20                  # cap half width (0.05 side overhang), cap depth (0.05 front overhang, flush at the back)
H, T_CAP, K = 1.30, 0.085, 0.30      # total height, cap thickness (vertical), gable slope (16.7 deg)
ZA = H - T_CAP                       # gable apex of the cap underside (= top of the slab)
EMB = 0.01                           # basin / medallion / collar sunk 1 cm into the slab front (no coplanar contact)
YF = -SD                             # slab front plane
YB = YF + EMB                        # back plane of the basin and of the attached parts (inside the slab)
# Basin: half of a 16-gon (flat face to the front, half facets at both ends), (vertex radius, z, slot of the band to the next)
NB = 16
RC = 0.459                           # coping vertex radius: bbox X = 2 * RC * cos(11.25 deg) = 0.90 (catalogue, reference)
BASIN = [
    (RC - 0.003, 0.000, STONE),      # plinth wall (slot 12 = second stone tone), 1.2 cm proud of the drum
    (RC - 0.003, 0.050, STONE),      # plinth top chamfer
    (RC - 0.015, 0.062, LIME),       # drum
    (RC - 0.015, 0.370, LIME),       # flat ledge under the coping (1.5 cm overhang, faces down)
    (RC, 0.370, LIME),               # coping outer face
    (RC, 0.425, LIME),               # coping top chamfer
    (RC - 0.015, 0.440, LIME),       # coping top
    (RC - 0.085, 0.440, STONE),      # inner wall (slot 12), slight slope down to the water line
    (RC - 0.095, 0.370, None),       # water line (flat half-disc, 7 cm under the coping top)
]
ZW = BASIN[-1][1]
# Medallion: 12-gon disc, flat top, front chamfer
MED_Z, MED_R, MED_T, MED_C = 1.00, 0.14, 0.03, 0.008
# Spout: 8-gon pipe (flat bottom) with a collar; hollow tip (bore in dark metal)
SP_Z, SP_R, SP_L, SP_BORE, SP_BD = 0.78, 0.050, 0.15, 0.034, 0.035
COL_R, COL_T, COL_C = 0.074, 0.024, 0.008
# Stream: flat ribbon 0.05 x 0.02 from the bore floor over the lip, out by 0.04 and straight down into the water
ST_W, ST_T = 0.050, 0.020


def U(x): return ZA - K * abs(x)                 # cap underside / slab top
def TT(x): return U(x) + T_CAP                   # cap top


def build_stele(P, comp):
    V = lambda x, y, z: P.bm.verts.new(Vector((x, y, z)))
    b = [V(-SW, 0, 0), V(SW, 0, 0), V(SW, 0, U(SW)), V(CW, 0, U(CW)), V(CW, 0, TT(CW)), V(0, 0, TT(0)),
         V(-CW, 0, TT(CW)), V(-CW, 0, U(CW)), V(-SW, 0, U(SW))]
    f = [V(-CW, -CD, U(CW)), V(0, -CD, ZA), V(CW, -CD, U(CW)), V(CW, -CD, TT(CW)), V(0, -CD, TT(0)), V(-CW, -CD, TT(CW))]
    s0, sA, s1 = V(-SW + CH, YF, U(SW - CH)), V(0, YF, ZA), V(SW - CH, YF, U(SW - CH))
    c0, c1 = V(-SW, YF + CH, U(SW)), V(SW, YF + CH, U(SW))
    gl1, gl2, gr2, gr1 = V(-SW, YF + CH, 0), V(-SW + CH, YF, 0), V(SW - CH, YF, 0), V(SW, YF + CH, 0)
    F = lambda vs, sl=LIME: P.face(vs, sl)
    slab = [F(b), F([b[0], gl1, gl2, gr2, gr1, b[1]]),                             # back (one flat polygon), bottom
            F([b[1], gr1, c1, b[2]]), F([gr1, gr2, s1, c1]), F([gl2, gr2, s1, sA, s0]),   # right side, chamfer, front
            F([gl2, gl1, c0, s0]), F([gl1, b[0], b[8], c0])]                      # left chamfer, left side
    cap = [F([sA, s1, c1, b[2], b[3], f[2], f[1]]), F([sA, f[1], f[0], b[7], b[8], c0, s0]),   # undersides
           F(f), F([f[4], f[3], b[4], b[5]]), F([f[5], f[4], b[5], b[6]]),       # gable front, two roof slopes
           F([f[2], b[3], b[4], f[3]]), F([f[0], f[5], b[6], b[7]])]             # cap ends
    comp['Slab'] = slab; comp['Cap'] = cap


def half_ring(r, z):
    """half 16-gon in front of the back plane YB: end (apothem, on the back plane), 8 vertices, end"""
    a = r * math.cos(math.pi / NB)
    pts = [(a, 0.0)] + [(r * math.cos((2 * k + 1) * math.pi / NB), r * math.sin((2 * k + 1) * math.pi / NB)) for k in range(NB // 2)] + [(-a, 0.0)]
    return [Vector((x, YB - y, z)) for x, y in pts]


def build_basin(P, comp):
    R = [[P.bm.verts.new(v) for v in half_ring(r, z)] for r, z, _ in BASIN]
    n = len(R[0]); fs = []; inner = []
    for j in range(len(R) - 1):
        for k in range(n - 1):
            f_ = P.face([R[j][k], R[j][k + 1], R[j + 1][k + 1], R[j + 1][k]], BASIN[j][2])
            (inner if BASIN[j][2] == STONE and j >= 6 else fs).append(f_)
    fs.append(P.face(list(reversed(R[0])), STONE))                               # bottom (closed manifold)
    back = [R[j][0] for j in range(len(R))] + [R[j][-1] for j in reversed(range(len(R)))]
    fs.append(P.face(back, LIME))                                                # back (inside the slab / wings)
    comp['Basin'] = fs; comp['InnerWall'] = inner
    comp['Water'] = [P.face(list(R[-1]), WATER)]                                 # flat half-disc on the water line


def zx_ring(r, n, a0, y, cz):
    return [Vector((r * math.cos(a0 + 2 * math.pi * k / n), y, cz + r * math.sin(a0 + 2 * math.pi * k / n))) for k in range(n)]


def disc_loft(P, comp, cname, rings, side_slots, back_slot, front_slot):
    R = [[P.bm.verts.new(v) for v in r] for r in rings]; n = len(R[0]); fs = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            fs.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], side_slots[j]))
    fs.append(P.face(list(R[0]), back_slot))
    if front_slot is not None: fs.append(P.face(list(reversed(R[-1])), front_slot))
    comp[cname] = fs
    return R


def build_medallion(P, comp):
    a0 = math.radians(15)                                                        # flat top and bottom
    disc_loft(P, comp, 'Medallion', [zx_ring(MED_R, 12, a0, YB, MED_Z), zx_ring(MED_R, 12, a0, YF - MED_T + MED_C, MED_Z),
                                     zx_ring(MED_R - MED_C * 2.2, 12, a0, YF - MED_T, MED_Z)], [STONE, STONE], STONE, STONE)


def build_spout(P, comp):
    a0 = -math.pi / 2 + math.pi / 8                                              # 8-gon with a flat bottom face
    disc_loft(P, comp, 'Collar', [zx_ring(COL_R, 8, a0, YB, SP_Z), zx_ring(COL_R, 8, a0, YF - COL_T + COL_C, SP_Z),
                                  zx_ring(COL_R - COL_C * 1.6, 8, a0, YF - COL_T, SP_Z)], [METAL, METAL], METAL, METAL)
    tip = YF - SP_L
    R = disc_loft(P, comp, 'Pipe', [zx_ring(SP_R, 8, a0, YF - 0.005, SP_Z), zx_ring(SP_R, 8, a0, tip, SP_Z),
                                    zx_ring(SP_BORE, 8, a0, tip, SP_Z), zx_ring(SP_BORE, 8, a0, tip + SP_BD, SP_Z)],
                  [METAL, METAL, METAL_D], METAL, METAL_D)
    return tip


def build_stream(P, comp, tip):
    floor = SP_Z - SP_BORE * math.cos(math.pi / 8)                               # bore floor (flat bottom face)
    zc = floor + ST_T / 2 - 0.004                                                # ribbon sunk 4 mm into the bore floor
    pts = [Vector((0, tip + SP_BD * 0.6, zc)), Vector((0, tip - 0.010, zc - 0.006)), Vector((0, tip - 0.024, zc - 0.030)),
           Vector((0, tip - 0.030, zc - 0.070)), Vector((0, tip - 0.030, ZW - 0.015))]
    up = Vector((1, 0, 0)); n = len(pts); rings = []
    sec = [(-ST_T / 2, -ST_W / 2), (ST_T / 2, -ST_W / 2), (ST_T / 2, ST_W / 2), (-ST_T / 2, ST_W / 2)]
    for i, c in enumerate(pts):                                                  # mitred sweep (as pack_shapes.path_sweep)
        d1 = (c - pts[i - 1]).normalized() if i > 0 else None
        d2 = (pts[i + 1] - c).normalized() if i < n - 1 else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in sec])
    # faces: k=0 back/under (-side), 1 front/top (+side), 2 the +X side (light highlight row, slot 9), 3 the -X side
    side = lambda j, k: METAL_L if k == 2 else WATER
    R = [[P.bm.verts.new(p) for p in r] for r in rings]; fs = []
    for j in range(n - 1):
        for k in range(4):
            k1 = (k + 1) % 4
            fs.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], side(j, k)))
    fs.append(P.face(list(reversed(R[0])), WATER)); fs.append(P.face(list(R[-1]), WATER))
    comp['Stream'] = fs


COMPS = ('Slab', 'Cap', 'Basin', 'InnerWall', 'Water', 'Medallion', 'Collar', 'Pipe', 'Stream')
GROUND = ('Slab', 'Basin')


def build_body():
    P = Part('Body'); comp = {}
    build_stele(P, comp); build_basin(P, comp); build_medallion(P, comp)
    tip = build_spout(P, comp); build_stream(P, comp, tip)
    for cn in COMPS: P.comp.append((cn, comp[cn], cn in GROUND))
    return P


# ---------------- scene / atlas ----------------
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
    print('  atlas', bpy.path.abspath(img.filepath), img.size[:], 'palette mismatches', bad, '| dirty', img.is_dirty)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


# ---------------- checks ----------------
def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def final_mesh_checks(ob):
    """after triangulation: non-manifold, loose, degenerate triangles, smooth faces, mirror X, back plane"""
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me)
    nm_ = sum(1 for e in bm.edges if not e.is_manifold); loose = sum(1 for v in bm.verts if not v.link_faces)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-8)
    minang = min(min(l.calc_angle() for l in f.loops) for f in bm.faces)
    from mathutils import kdtree
    pts = [ob.matrix_world @ v.co for v in bm.verts]
    kd = kdtree.KDTree(len(pts))
    for i, q in enumerate(pts): kd.insert(q, i)
    kd.balance()
    mir = max(kd.find(Vector((-q.x, q.y, q.z)))[2] for q in pts)
    ymax = max(q.y for q in pts); zmin = min(q.z for q in pts)
    back = [f for f in bm.faces if all(abs((ob.matrix_world @ v.co).y) < 1e-6 for v in f.verts)]
    back_area = sum(f.calc_area() for f in back); back_dir = [round(f.normal.y, 3) for f in back]
    smooth = sum(p.use_smooth for p in me.polygons)
    bm.free()
    print(f'  final mesh: non-manifold {nm_} loose {loose} degenerate {deg} (min corner angle {math.degrees(minang):.2f} deg)'
          f' smooth {smooth} mirrorX {mir:.6f} | max y {ymax:.6f} (nothing behind the back plane) min z {zmin:.4f}')
    print(f'  back plane y=0: {len(back)} tris, area {back_area:.4f} m2, normals y {sorted(set(back_dir))}')
    return dict(nonmanifold=nm_, loose=loose, degenerate=deg, mirror=mir, ymax=ymax, zmin=zmin)


def snap_check(ob):
    """CATALOG «Модули и стыковка»: WTR-02 at the wall = back face 0.22 from the MOD-03 wall axis (against the coping).
    Imports the MOD-03 FBX (read only) into a temporary scene, puts its axis at y = +0.22 and measures."""
    if not os.path.isfile(WALL_FBX):
        print('  SNAP: MOD-03 FBX missing -> contract numbers only'); return
    win = bpy.context.window; prev = win.scene if win else None
    sc = bpy.data.scenes.new('TMP_WTR02_Snap')
    if win: win.scene = sc
    before_i, before_m = set(bpy.data.images), set(bpy.data.materials)
    try:
        bpy.ops.import_scene.fbx(filepath=WALL_FBX)
        bpy.context.view_layer.update()
        wall = [o for o in sc.objects if o.type == 'MESH']
        wp = [o.matrix_world @ v.co for o in wall for v in o.data.vertices]
        lo = [min(p[i] for p in wp) for i in range(3)]; hi = [max(p[i] for p in wp) for i in range(3)]
        # the wall runs along X; its thickness is along Y; axis at y = 0 in its own file -> shift to +0.22
        shift = Vector((0, 0.22, 0))
        wp = [p + shift for p in wp]
        mp = [ob.matrix_world @ v.co for v in ob.data.vertices]
        from mathutils.bvhtree import BVHTree
        tw = BVHTree.FromPolygons(wp, [list(p.vertices) for o in wall for p in o.data.polygons]) if len(wall) == 1 else None
        wy_min = min(p.y for p in wp); wy_min_body = min(p.y for p in wp if p.z < 0.53)
        inside = sum(1 for p in mp if p.y > wy_min + 1e-6 and lo[0] <= p.x <= hi[0] and p.z <= hi[2])
        print(f'  SNAP MOD-03: wall bbox x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} z {lo[2]:.3f}..{hi[2]:.3f};'
              f' axis at y=+0.22 -> coping face y {wy_min:.4f}, wall face (below the coping) y {wy_min_body:.4f};'
              f' fountain back y {max(p.y for p in mp):.4f}; fountain verts inside the wall {inside} ->',
              'SNAP OK' if abs(wy_min) < 1e-4 and inside == 0 and max(p.y for p in mp) <= 1e-6 else 'SNAP FAIL')
        print(f'  SNAP: stele top {H:.3f} above wall top {hi[2]:.3f}; back face covers the coping band z {0.54}..{hi[2]:.2f}'
              f' over x +-{SW} (back-to-back contact, both faces hidden)')
    finally:
        for o in list(sc.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
        for m in set(bpy.data.materials) - before_m:
            if m.users == 0: bpy.data.materials.remove(m)
        for i in set(bpy.data.images) - before_i:
            if i.users == 0: bpy.data.images.remove(i)
        if win: win.scene = prev
        bpy.data.scenes.remove(sc)


def stream_check(P):
    from mathutils.bvhtree import BVHTree
    P.bm.verts.index_update(); allpos = [v.co.copy() for v in P.bm.verts]
    trees = {nm: BVHTree.FromPolygons(allpos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp}
    st = trees['Stream']
    print('  stream contacts: pipe', 'OK' if st.overlap(trees['Pipe']) else 'NO CONTACT',
          '| water', 'OK' if st.overlap(trees['Water']) else 'NO CONTACT',
          '| basin walls', 'touch (FAIL)' if st.overlap(trees['Basin']) or st.overlap(trees['InnerWall']) else 'clear')


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_body()
    tris = part_tris(P)
    stream_check(P)
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    pc.coplanar_overlaps(ob)
    final_mesh_checks(ob)
    snap_check(ob)
    print('  materials', [m.name for m in ob.data.materials], '| slots used', sorted({pc_slot(ob, p) for p in ob.data.polygons}))
    return coll, root, ob, img, mat, tot


def pc_slot(ob, p):
    u, v = ob.data.uv_layers.active.data[p.loop_start].uv
    return int(v * 0 + (3 - int(v * 4)) * 4 + int(u * 4))


def geom_dump(ob, path):
    me = ob.data; uv = me.uv_layers.active.data
    vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
    fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                 tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
    h = hashlib.sha1(json.dumps([vs, fs]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=len(vs), faces=len(fs), sha1=h), f)
    print('  geometry dump', path, len(vs), 'verts', len(fs), 'faces sha1', h)
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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_WTR02_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_WTR02_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_WTR02_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_WTR02_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_WTR02_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_WTR02_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_WTR02_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2,
                     (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 8.0
    for _ in range(30):
        x0, x1, y0, y1 = place(d)
        k = max((x1 - x0) / fill_w, (y1 - y0) / fill_h)
        if lens: d *= k
        else: cd.ortho_scale *= k
    x0, x1, y0, y1 = place(d)
    asp = res[1] / res[0]
    cd.shift_x = (x0 + x1) / 2 - 0.5
    cd.shift_y = ((y0 + y1) / 2 - 0.5) * asp
    sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for o in tmp:
        dat = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dat, bpy.types.Light): bpy.data.lights.remove(dat)
        else: bpy.data.cameras.remove(dat)
    bpy.data.collections.remove(tc); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


VIEW_REF = (0.36, -1.0, 0.68)            # reference: front-right, ~32 deg above (AI image, not a calibrated camera)
VIEW_PREVIEW = (1.0, -1.25, 0.75)        # series preview 3/4 (as WTR-03 / WTR-01)

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, ob, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root, ob]
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs, os.path.join(CHECK_DIR, f'WTR-02_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.52, fill_h=0.88)
        render(objs, os.path.join(CHECK_DIR, f'WTR-02_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'WTR-02_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs, os.path.join(CHECK_DIR, f'WTR-02_back_{tag}.png'), (-0.8, 1.0, 0.4), res=(800, 800))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, f'geom_{tag}.json'))
