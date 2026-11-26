# build.py - STR-06 Hexagonal gazebo (FMS_Garden_Gazebo), pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- STR-06 build|export|verify
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/STR-06/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
#   verify = only re-import the FBX in art/ (run after make_lod1.py, which rewrites the FBX with the _Low1 children)
#   LOD1:  blender.exe --background --factory-startup --python Tools/blender/make_lod1.py -- --art art/CottageGardenDecor FMS_Garden_Gazebo
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\STR-06_Gazebo\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-06', 'build']})
#   Live mode touches only the collection STR-06_Gazebo (other objects, scenes and the owner's .blend stay as they are).
#   Headless the collection is named FMS_Garden_Gazebo (make_lod1.py looks the collection up by the asset name).
# Axes (Blender): X = entrance (Unity +X), Y = across, Z = up. Pivot: centre of the hexagon on the ground.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'STR-06')
NAME = 'FMS_Garden_Gazebo'
PREVIEW = 'FMS_Garden_STR_06_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here, written by WTR-03
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 5000
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, WOOD_M, RED, RED_D, WHITE, IRON, TILE = 0, 1, 2, 5, 6, 10, 13, 14
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part
from pack_shapes import oct_rod

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-06'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'STR-06_Gazebo' if LIVE else NAME

C30 = math.cos(math.pi / 6); T30 = math.tan(math.pi / 6)
# ---- dimensions (spec prompts/STR-06.3d.md, checked against references/STR-06.png, see notes.md) ----
DECK_R, SKIRT_R = 1.55, 1.50                  # circumradius, vertices on +-Y, flat face (entrance) to +X
Z_SKIRT, Z_DECK = 0.24, 0.36
BOARD_N, JOINT_W = 12, 0.016                  # deck boards across X (joints = flush mid-wood strips)
POST_R, POST_W, CAP_W = 1.45, 0.18, 0.24      # reference: post ~0.057 of the roof width      # posts at the hexagon vertices, flared capital at the top
Z_POST0, Z_CAP0, Z_CAP1, Z_CAP2 = 0.34, 2.27, 2.31, 2.47
BEAM_W, Z_BEAM0, Z_BEAM1 = 0.10, 2.46, 2.60   # ring beam on the post line; clear opening deck->beam = 2.10
STEP_W, STEP_X0, STEP_X1, STEP_X2 = 1.40, 1.297, 1.672, 2.002   # treads 0.33 (reference), not 0.55
ROOF_R = 1.70; ROOF_A = ROOF_R * C30          # eave circumradius / apothem
Z_SOFFIT, Z_FASCIA, Z_PEAK = 2.59, 2.71, 3.68
COURSES, TILE_W, SH_H, OVERHANG = 7, 0.22, 0.035, 0.06
RAIL_FACES = (60, 120, 180, 240, 300)         # face normal angles (deg); 0 = entrance, open
BENCH_FACES = (120, 180, 240)


def hexc(r, z):
    return [Vector((r * math.cos(math.radians(30 + 60 * k)), r * math.sin(math.radians(30 + 60 * k)), z)) for k in range(6)]


def zipper(P, A, B, slot):
    """strip between two parallel polylines A, B (same direction): quad if both are 2 points, else a triangle zipper"""
    if len(A) == 2 and len(B) == 2:
        return [P.face([A[0], A[1], B[1], B[0]], slot)]
    def par(L):
        d = L[-1].co - L[0].co; return [(v.co - L[0].co).dot(d) / d.length_squared for v in L]
    ta, tb = par(A), par(B); i = j = 0; out = []
    while i < len(A) - 1 or j < len(B) - 1:
        if j == len(B) - 1 or (i < len(A) - 1 and ta[i + 1] <= tb[j + 1]):
            out.append(P.face([A[i], A[i + 1], B[j]], slot)); i += 1
        else:
            out.append(P.face([A[i], B[j + 1], B[j]], slot)); j += 1
    return out


def rand01(*k):
    h = 2166136261
    for x in k: h = ((h ^ (x & 0xFF)) * 16777619) & 0xFFFFFFFF
    return h / 0xFFFFFFFF


# ---------------- Base: skirt + deck (one shell, planks) + steps ----------------
def build_base():
    P = Part('Base'); bm = P.bm
    S0 = [bm.verts.new(v) for v in hexc(SKIRT_R, 0.0)]; S1 = [bm.verts.new(v) for v in hexc(SKIRT_R, Z_SKIRT)]
    D0 = [bm.verts.new(v) for v in hexc(DECK_R, Z_SKIRT)]
    skirt = [P.face(list(reversed(S0)), WOOD_D)]
    for k in range(6):
        k1 = (k + 1) % 6
        skirt.append(P.face([S0[k], S0[k1], S1[k1], S1[k]], WOOD_D))
        skirt.append(P.face([S1[k], S1[k1], D0[k1], D0[k]], WOOD_D))           # ledge under the deck overhang
    # deck top: boundary loop with the board/joint lines x = const
    A = DECK_R * C30; bw = (2 * A - (BOARD_N - 1) * JOINT_W) / BOARD_N
    xs = []; x = -A
    for b in range(BOARD_N - 1):
        x += bw; xs.append(x); x += JOINT_W; xs.append(x)
    C = hexc(DECK_R, Z_DECK); sides = []
    for k in range(6):
        p0, p1 = C[k], C[(k + 1) % 6]; pts = [p0]
        if abs(p1.x - p0.x) > 1e-6:
            ts = sorted((xx - p0.x) / (p1.x - p0.x) for xx in xs if min(p0.x, p1.x) + 1e-6 < xx < max(p0.x, p1.x) - 1e-6)
            pts += [p0.lerp(p1, t) for t in ts]
        sides.append(pts)
    corner = [bm.verts.new(C[k]) for k in range(6)]
    loop_sides = [[corner[k]] + [bm.verts.new(p) for p in sides[k][1:]] + [corner[(k + 1) % 6]] for k in range(6)]
    deck = []
    for k in range(6):
        deck += zipper(P, [D0[k], D0[(k + 1) % 6]], loop_sides[k], WOOD)
    loop = [v for s in loop_sides for v in s[:-1]]
    bounds = [-A] + xs + [A]
    for b in range(len(bounds) - 1):
        x0, x1 = bounds[b], bounds[b + 1]
        vs = [v for v in loop if x0 - 1e-6 <= v.co.x <= x1 + 1e-6]
        c = sum((v.co for v in vs), Vector()) / len(vs)
        vs.sort(key=lambda v: math.atan2(v.co.y - c.y, v.co.x - c.x))
        deck.append(P.face(vs, WOOD if b % 2 == 0 else WOOD_M))
    P.comp.append(('Skirt', skirt, True)); P.comp.append(('Deck', deck, False))
    # steps: one L-section solid (two equal 0.12 rises; the deck top is the third), back face 2 mm inside the skirt
    prof = [(STEP_X0, 0.0), (STEP_X2, 0.0), (STEP_X2, 0.12), (STEP_X1, 0.12), (STEP_X1, 0.238), (STEP_X0, 0.238)]
    slots = [WOOD_D, WOOD_D, WOOD, WOOD_D, WOOD, WOOD_D]          # bottom, outer riser, outer tread, inner riser, inner tread, back
    L = [bm.verts.new((x, -STEP_W / 2, z)) for x, z in prof]; R = [bm.verts.new((x, STEP_W / 2, z)) for x, z in prof]
    st = [P.face(L, WOOD_D), P.face(list(reversed(R)), WOOD_D)]
    for i in range(6):
        i1 = (i + 1) % 6; st.append(P.face([L[i], R[i], R[i1], L[i1]], slots[i]))
    P.comp.append(('Steps', st, True))
    return P


# ---------------- Frame: posts with capitals, ring beam, rafters, centre boss ----------------
def build_frame():
    P = Part('Frame'); d = (POST_W - CAP_W) / -2 + 0.0
    for v in hexc(POST_R, 0):
        pc.rect_prism(P, 'Posts', v.x, v.y, CAP_W, CAP_W, 0.015,
                      [(Z_POST0, d), (Z_CAP0, d), (Z_CAP1, 0.0), (Z_CAP2, 0.0)], WHITE, WHITE, WHITE)
    ro, ri = POST_R + BEAM_W / 2 / C30, POST_R - BEAM_W / 2 / C30
    P.torus_loft('RingBeam', [hexc(ro, Z_BEAM0), hexc(ro, Z_BEAM1), hexc(ri, Z_BEAM1), hexc(ri, Z_BEAM0)], WHITE)
    P.comp[-1] = ('RingBeam', P.comp[-1][1], False)
    prof = [(0.05, 0.04), (-0.05, 0.04), (-0.05, -0.04), (0.05, -0.04)]
    for k in range(6):
        u = Vector((math.cos(math.radians(30 + 60 * k)), math.sin(math.radians(30 + 60 * k)), 0))
        pc.sweep(P, 'Rafters', u * 0.12 + Vector((0, 0, 2.555)), u * 1.42 + Vector((0, 0, 2.555)), prof,
                 [(0, 1, 0), (1, 1, 0)], WHITE, WHITE, WHITE, ref=(0, 0, 1))
    pc.zprism(P, 'Rafters', 0, 0, [(v.x, v.y) for v in hexc(0.17, 0)], [(2.44, 0), (2.48, -0.0), (2.595, 0)], WHITE, WHITE, WHITE)
    return P


# ---------------- Railings (5 faces, entrance open) ----------------
def build_railings():
    P = Part('Railings')
    for th in RAIL_FACES:
        a = math.radians(th - 30); b = math.radians(th + 30)
        Va = Vector((POST_R * math.cos(a), POST_R * math.sin(a), 0)); Vb = Vector((POST_R * math.cos(b), POST_R * math.sin(b), 0))
        d = (Vb - Va).normalized(); Lf = (Vb - Va).length
        for zc, h, w in ((1.22, 0.08, 0.10), (0.50, 0.08, 0.07)):
            pr = [(h / 2, w / 2), (-h / 2, w / 2), (-h / 2, -w / 2), (h / 2, -w / 2)]
            pc.sweep(P, 'Rails', Va + d * 0.02 + Vector((0, 0, zc)), Vb - d * 0.02 + Vector((0, 0, zc)), pr,
                     [(0, 1, 0), (1, 1, 0)], WHITE, WHITE, WHITE, ref=(0, 0, 1))
        n = 8; span = Lf - 0.20
        for j in range(n):
            c = Va + d * (0.10 + (j + 0.5) * span / n)
            pr = [(0.03, 0.025), (-0.03, 0.025), (-0.03, -0.025), (0.03, -0.025)]     # 0.06 along the rail x 0.05
            pc.sweep(P, 'Balusters', c + Vector((0, 0, 0.52)), c + Vector((0, 0, 1.21)), pr,
                     [(0, 1, 0), (1, 1, 0)], WHITE, WHITE, WHITE, ref=tuple(d))
    return P


# ---------------- Benches (3 back faces) ----------------
def build_benches():
    P = Part('Benches')
    def loc(u, v, a, s): return (u * a + v * s).to_tuple()[:2]
    for th in BENCH_FACES:
        t = math.radians(th); u = Vector((math.cos(t), math.sin(t), 0)); v = Vector((-math.sin(t), math.cos(t), 0))
        ao, ai = 1.19, 0.79; so, si = ao * T30 - 0.12, ai * T30 - 0.12
        seat = [loc(u, v, ao, -so), loc(u, v, ao, so), loc(u, v, ai, si), loc(u, v, ai, -si)]
        pc.zprism(P, 'Seats', 0, 0, seat, [(0.73, 0), (0.81, 0)], WOOD, WOOD, WOOD)
        for sg in (-1, 1):
            leg = [loc(u, v, 0.85, sg * 0.23), loc(u, v, 0.85, sg * 0.32), loc(u, v, 1.13, sg * 0.32), loc(u, v, 1.13, sg * 0.23)]
            pc.zprism(P, 'Legs', 0, 0, leg, [(Z_DECK - 0.01, 0), (0.74, 0)], WHITE, WHITE, WHITE)
    return P


# ---------------- Roof: shingle courses (one closed hex shell), hip ribs, spire ----------------
def build_roof():
    P = Part('Roof'); bm = P.bm
    run, rise = ROOF_A, Z_PEAK - Z_FASCIA; Ls = math.hypot(run, rise); phi = math.atan2(rise, run)
    n2 = (math.sin(phi), math.cos(phi))
    def p(s, h=0.0): return (ROOF_A - s * math.cos(phi) + h * n2[0], Z_FASCIA + s * math.sin(phi) + h * n2[1])
    def ring(az, fr):
        a, z = az; C = [bm.verts.new(v) for v in hexc(a / C30, z)]
        return [[C[k]] + [bm.verts.new(C[k].co.lerp(C[(k + 1) % 6].co, f)) for f in fr] + [C[(k + 1) % 6]] for k in range(6)]
    W = (Ls - 0.16) / COURSES; s_ = [i * W for i in range(COURSES + 1)]
    fracs = []
    for i in range(COURSES):
        side = p((s_[i] + s_[i + 1]) / 2)[0] / C30; n = max(1, round(side / TILE_W))
        fracs.append([(j + 0.5) / n for j in range(n)] if i % 2 else [j / n for j in range(1, n)])
    roof = []
    SO = ring((ROOF_A, Z_SOFFIT), []); F = ring(p(0), []); E = ring(p(-OVERHANG), [])
    roof.append(P.face([s[0] for s in reversed(SO)], WHITE))                          # soffit / ceiling
    for k in range(6):
        roof += zipper(P, SO[k], F[k], WHITE)                                          # fascia
        roof += zipper(P, F[k], E[k], RED_D)                                           # underside of the first course
    prev = E
    for i in range(COURSES):
        B = ring(p(s_[i] if i else -OVERHANG, SH_H), fracs[i]); T = ring(p(s_[i + 1]), fracs[i])
        for k in range(6):
            roof += zipper(P, prev[k], B[k], RED_D)                                    # riser (exposed butt of the course)
            tone = int(rand01(i, k, 3) < 0.5)
            for m in range(len(B[k]) - 1):
                if m and rand01(i, k, m, 7) < 0.75: tone ^= 1          # mostly alternating, random runs (no diagonal stripes)
                slot = (RED, TILE)[tone]
                roof.append(P.face([B[k][m], B[k][m + 1], T[k][m + 1], T[k][m]], slot))
        prev = T
    Cb = ring(p(s_[-1], SH_H), [])
    s_ap = (ROOF_A + SH_H * n2[0]) / math.cos(phi); z_ap = Z_FASCIA + s_ap * math.sin(phi) + SH_H * n2[1]
    apex = bm.verts.new((0, 0, z_ap))
    for k in range(6):
        roof += zipper(P, prev[k], Cb[k], RED_D)
        roof.append(P.face([Cb[k][0], Cb[k][1], apex], RED_D))                       # hexagonal peak cap
    P.comp.append(('Shingles', roof, False))
    # hip ribs: boards on the six hips, proud of the courses
    rc_e = ROOF_R; tan_psi = rise / rc_e
    prof = [(-0.04, -0.05), (0.085, -0.05), (0.085, 0.05), (-0.04, 0.05)]
    for k in range(6):
        u = Vector((math.cos(math.radians(30 + 60 * k)), math.sin(math.radians(30 + 60 * k)), 0))
        def hp(r): return u * r + Vector((0, 0, Z_FASCIA + (rc_e - r) * tan_psi))
        pc.sweep(P, 'Ribs', hp(rc_e + 0.05), hp(0.10), prof, [(0, 1, 0), (1, 1, 0)], WHITE, WHITE, WHITE, ref=(0, 0, 1))
    # spire: iron rod with a flared foot, faceted ball
    oct_rod(P, 'Spire', (0, 0, 3.60), (0, 0, 3.86), [(0, 0.13), (0.55, 0.13), (0.70, 0.05), (1, 0.045)], IRON, IRON, ref=(1, 0, 0))
    r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.105, matrix=Matrix.Translation((0, 0, 3.895)))
    fs = list({f for v in r['verts'] for f in v.link_faces})
    for f in fs: f[P.slot] = IRON
    P.comp.append(('Spire', fs, False))
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
    me = bpy.data.meshes.new('TMP_STR06_all'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_STR06_all', me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def mirror_y(obs):
    from mathutils import kdtree
    pts = [o.matrix_world @ v.co for o in obs for v in o.data.vertices]
    kd = kdtree.KDTree(len(pts))
    for i, q in enumerate(pts): kd.insert(q, i)
    kd.balance()
    m = max(kd.find(Vector((q.x, -q.y, q.z)))[2] for q in pts)
    print(f'  mirror Y (across the entrance axis) max {m:.6f}')
    return m


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    obs = {}; tris = {}
    for fn in (build_base, build_frame, build_railings, build_benches, build_roof):
        P = fn(); tris[P.name] = part_tris(P)
        obs[P.name] = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    for o in obs.values(): pc.coplanar_overlaps(o)
    print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values())))
    cross_contacts(list(obs.values())); mirror_y(list(obs.values()))
    clear = Z_BEAM0 - Z_DECK
    print(f'  entrance opening: clear height deck->beam {clear:.2f} m, clear width between front posts '
          f'{2 * POST_R * math.sin(math.radians(30)) - POST_W:.2f} m (capitals {2 * POST_R * 0.5 - CAP_W:.2f} m from z {Z_CAP0})')
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
    print('  geometry dump', path, [len(v) for v in allv], 'verts', [len(x) for x in allf], 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_STR06_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_STR06_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_STR06_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_STR06_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_STR06_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_STR06_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_STR06_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 12.0
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


VIEW_REF = (1.0, 0.0, math.tan(math.radians(14)))          # reference: entrance face to the camera, ~14 deg above, ~50 mm
VIEW_PREVIEW = (1.0, -0.55, 0.55)                           # series preview 3/4 (entrance side visible)

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, obs, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs, os.path.join(CHECK_DIR, f'STR-06_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.77, fill_h=0.87, lens=50)
        render(objs, os.path.join(CHECK_DIR, f'STR-06_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'STR-06_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = pc.export(NAME, coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()), os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
