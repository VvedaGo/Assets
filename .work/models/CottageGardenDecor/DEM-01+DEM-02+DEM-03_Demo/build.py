# build.py - DEM-01 / DEM-02 / DEM-03 demo environment of the scene Demo_CottageGarden, pack CottageGardenDecor
# (Cottage Garden Decor). DEMO ONLY: not catalogue models, removable, not counted (like FMS_Mach_Demo_* of Farm Machinery).
#   DEM-01 FMS_Garden_Demo_Island  floating garden island ~20.3 x 16.2 m (x0.75 after review renders_1), flat lawn top at Y 0, underside to Y -2.93
#   DEM-02 FMS_Garden_Demo_Path    sandy path slab (top Y 0.01, bottom Y 0.002): main S-curve front edge -> gazebo + branch
#   DEM-03 FMS_Garden_Demo_Clouds  5 faceted low-poly clouds (child objects Cloud_A..E, origin at each bottom centre)
# Approach and helpers copied from Farm Machinery DEM_IslandBase / DEM_Clouds (origin/Farm-Machinery, read-only), adapted.
# Own demo atlas art/CottageGardenDecor/Textures/FMS_Garden_Demo_Atlas.png + material M_Garden_Demo; the pack atlases
# FMS_Garden_AtlasA / AtlasF are never read or written here.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- <ID> build|export
#   check  = build + printed checks only
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + checks + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify
# Live Blender (MCP): exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'BUILD_ARGS': ['<ID>', 'build']})
#   Live builds go to an own scene 'DEM_Demo' with collection DEM_Demo / <asset>; nothing else is touched.
# Layout space (= Unity world of the demo scene, PackSceneBuilder): X east (right), Y up, Z north (camera at -Z looking +Z).
# Garden layout origin (0, 0, 0) = centre of the 18 x 13.5 m garden (x -9..9, z -6.75..6.75), lawn top Y 0.
# Geometry is written in UNITY coordinates and mapped to Blender as (-x, -z, y); the FBX export (-Z forward, Y up, baked)
# gives the design coordinates back in Unity (same convention as the Farm Machinery demo).
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '') or '.'))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor', 'Demo')
TEX_PATH = os.path.join(REPO, 'art', 'CottageGardenDecor', 'Textures', 'FMS_Garden_Demo_Atlas.png')
TEX_NAME, MAT_NAME = 'FMS_Garden_Demo_Atlas.png', 'M_Garden_Demo'
SCENE = OUTER = 'DEM_Demo'
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'DEM-01'
MODE = _a[1] if len(_a) > 1 else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)

# Demo atlas (16 flat cells, 4 x 4, 64 px). Series HEX where the pack has them (STYLE.md atlas F / A), new cells marked *
PAL_DEMO = ['#7DB93C', '#76B137', '#84BF45', '#6E9F4A',     # 0 lawn* (review renders_1: deeper green), 1 lawn shade*, 2 lawn light*, 3 lawn lip (F0)
            '#805433', '#8C5E3A', '#6B4429', '#5E4436',     # 4 soil (F12), 5 soil light*, 6 soil dark*, 7 underside rock*
            '#E2B07C', '#DBA874', '#E7B985', '#C8925E',     # 8 sand path*, 9 sand shade*, 10 sand light*, 11 sand bottom*
            '#F4F1E8', '#E3E7EC', '#7A5233', '#A7A39A']     # 12 cloud white (F8), 13 cloud shade*, 14 dark wood (A1), 15 stone (A12)
LAWN, LAWN_S, LAWN_L, LIP, SOIL, SOIL_L, SOIL_D, UNDER, SAND, SAND_S, SAND_L, SAND_B, CLOUD, CLOUD_S = range(14)

ITEMS = {
    'DEM-01': dict(asset='FMS_Garden_Demo_Island', budget=3000),
    'DEM-02': dict(asset='FMS_Garden_Demo_Path', budget=600),
    'DEM-03': dict(asset='FMS_Garden_Demo_Clouds', budget=1500),
}
# camera directions (Blender, target -> camera). Hero: from south-south-east, ~40 deg down
REF_VIEW = (-0.41, 1.0, 0.90)
TOP_VIEW = (0.0, 0.001, 1.0)
SIDE_VIEW = (0.0, 1.0, 0.10)


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))


def hsh(i, salt=0.0):
    """deterministic pseudo random 0..1"""
    s = math.sin(i * 12.9898 + salt * 78.233 + 0.123) * 43758.5453
    return s - math.floor(s)


# ================= DEM-01 island =================
PLAN = 0.75                        # review renders_1 Fix 1: whole island scaled x0.75 (planform AND depth) from the 26 x 20 design
GARDEN = (9.0, 6.75)               # garden half sizes after the scale (18 x 13.5 m), must stay inside the lawn
RR = (13.0, 10.0, 3.0)             # base rounded rectangle half sizes + corner radius, BEFORE the PLAN scale (26 x 20 design)
N_OUT = 56                         # outline points


def rr_point(s):
    """point + outward normal on the rounded rectangle at arc length s (CCW from the front middle (0, -B))"""
    A, B, R = RR
    a, b = A - R, B - R
    segs = [('L', (0, -B), (a, -B)), ('C', (a, -b), -90), ('L', (A, -b), (A, b)), ('C', (a, b), 0),
            ('L', (a, B), (-a, B)), ('C', (-a, b), 90), ('L', (-A, b), (-A, -b)), ('C', (-a, -b), 180), ('L', (-a, -B), (0, -B))]
    for sg in segs:
        if sg[0] == 'L':
            p0, p1 = Vector(sg[1]), Vector(sg[2]); L = (p1 - p0).length
            if s <= L:
                t = (p1 - p0).normalized(); return p0 + t * s, Vector((t.y, -t.x))
            s -= L
        else:
            L = R * math.pi / 2
            if s <= L:
                ang = math.radians(sg[2]) + s / R; n = Vector((math.cos(ang), math.sin(ang)))
                return Vector(sg[1]) + n * R, n
            s -= L
    return Vector((0, -B)), Vector((0, -1))


def outline():
    """irregular faceted outline: rounded rectangle pushed outwards by 0.05..0.8 m of smooth noise (never inwards)"""
    A, B, R = RR
    L = 4 * (A - R) + 4 * (B - R) + 2 * math.pi * R
    out = []
    for k in range(N_OUT):
        t = k / N_OUT
        p, n = rr_point(t * L + 0.35 * (hsh(k, 1) - 0.5) * L / N_OUT)
        d = 0.36 + 0.26 * math.sin(3 * 2 * math.pi * t + 0.7) + 0.18 * math.sin(5 * 2 * math.pi * t + 2.1) \
            + 0.10 * math.sin(11 * 2 * math.pi * t + 0.3) + 0.08 * (hsh(k, 2) - 0.5)
        d = max(0.05, d)
        out.append(p + n * d)
    return out


def vnormals(poly):
    n = len(poly); out = []
    for i in range(n):
        e0 = (poly[i] - poly[i - 1]).normalized(); e1 = (poly[(i + 1) % n] - poly[i]).normalized()
        m = Vector((e0.y, -e0.x)) + Vector((e1.y, -e1.x)); out.append(m.normalized())
    return out


def inside(poly, p):
    c = False; n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[i - 1]
        if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x: c = not c
    return c


def seg_dist(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.dot(ab))); return (a + ab * t - p).length


def lawn_area(poly):
    return abs(sum(poly[i - 1].x * poly[i].y - poly[i].x * poly[i - 1].y for i in range(len(poly)))) / 2


def poly_dist(poly, p):
    return min(seg_dist(p, poly[i - 1], poly[i]) for i in range(len(poly)))


def island_part():
    P = Part('Island'); bm = P.bm
    o = outline(); n = len(o); nrm = vnormals(o)
    # top: CDT of the outline + jittered interior grid (~2.6 m) -> large flat triangles in three lawn tones
    steiner = []; idx = 0
    for gx in range(-6, 7):
        for gz in range(-5, 6):
            idx += 1
            p = Vector((gx * 2.15 + 1.3 * (hsh(idx, 3) - 0.5) + (0.9 if gz % 2 else 0.0), gz * 1.95 + 1.1 * (hsh(idx, 4) - 0.5)))
            if inside(o, p) and poly_dist(o, p) > 1.1: steiner.append(p)
    pts = [(p.x, p.y) for p in o] + [(p.x, p.y) for p in steiner]
    vs, _, fs, orig, _, _ = delaunay_2d_cdt(pts, [], [list(range(n))], 1, 1e-5, True)
    tv = [bm.verts.new(V(x, 0.0, z)) for x, z in vs]
    ring0 = [None] * n
    for i, ids in enumerate(orig):
        for j in ids:
            if j < n: ring0[j] = tv[i]
    assert all(r is not None for r in ring0), 'outline vertex lost in CDT'
    faces = []
    for fi, f in enumerate(fs):
        h = hsh(fi, 5); slot = LAWN if h < 0.68 else (LAWN_S if h < 0.85 else LAWN_L)
        faces.append(P.face([tv[i] for i in f], slot))
    # cliff rings: (y, jitter y, offset along the outline normal, jitter, or scale towards the centre)
    def ring(y, jy, off=None, jo=0.0, scale=None, salt=0):
        r = []
        for k in range(n):
            yy = y + jy * (hsh(k, 10 + salt) - 0.5) * 2
            if scale is None:
                p = o[k] + nrm[k] * (off + jo * (hsh(k, 20 + salt) - 0.5) * 2)
            else:
                p = o[k] * (scale + 0.05 * (hsh(k, 30 + salt) - 0.5))
            r.append(bm.verts.new(V(p.x, yy, p.y)))
        return r
    rings = [ring0,
             ring(-0.20, 0.0, 0.08, 0.0, salt=1),                 # grass lip
             ring(-0.34, 0.03, 0.03, 0.02, salt=2),               # soil top edge
             ring(-1.30, 0.22, -0.18, 0.20, salt=3),              # cliff (vertical faceted wall)
             ring(-2.05, 0.20, -1.10, 0.40, salt=4),              # soil dark, start of the taper
             ring(-2.90, 0.18, scale=0.70, salt=5),               # underside rock
             ring(-3.50, 0.12, scale=0.38, salt=6)]
    bands = [lambda k: LIP, lambda k: SOIL_L,
             lambda k: SOIL if hsh(k, 40) < 0.6 else SOIL_L,
             lambda k: SOIL_D if hsh(k, 41) < 0.65 else SOIL,
             lambda k: UNDER if hsh(k, 42) < 0.7 else SOIL_D,
             lambda k: UNDER]
    for j in range(len(rings) - 1):
        a, b = rings[j], rings[j + 1]
        for k in range(n):
            k1 = (k + 1) % n; s = bands[j](k)
            if (k + j) % 2 == 0:
                faces.append(P.face([a[k], a[k1], b[k1]], s)); faces.append(P.face([a[k], b[k1], b[k]], s))
            else:
                faces.append(P.face([a[k], a[k1], b[k]], s)); faces.append(P.face([a[k1], b[k1], b[k]], s))
    c = bm.verts.new(V(0.0, -3.9, 0.0)); last = rings[-1]
    for k in range(n):
        faces.append(P.face([last[k], last[(k + 1) % n], c], UNDER))
    for v in bm.verts: v.co *= PLAN            # uniform x0.75: lawn ~20.3 x 16.2 m, underside to Y -2.93
    P.comp.append(('island', faces, False))
    return P


# ================= DEM-02 path =================
PATH_Y, PATH_Y0 = 0.01, 0.002      # top of the slab (0.01 above the lawn) / bottom (2 mm above the lawn, no coplanar faces)
W_MAIN, W_BRANCH = 1.8, 1.5         # widths kept (review: 'width kept', main >= 1.5); centrelines scaled by PLAN
MAIN_CP = [(-2.4, None), (-2.6, -7.4), (-2.0, -4.6), (-0.8, -1.8), (0.4, 0.9), (1.3, 3.2), (2.5, 4.9), (3.6, 5.7)]   # z None = island edge
BRANCH_CP = [(0.7, 2.2), (-0.2, 3.6), (-1.6, 4.6), (-3.3, 5.2)]


def edge_z(o, x):
    """front (south) edge of the lawn at x: highest z of the outline crossing x below the origin"""
    zs = []
    for i in range(len(o)):
        a, b = o[i - 1], o[i]
        if (a.x - x) * (b.x - x) <= 0 and a.x != b.x:
            t = (x - a.x) / (b.x - a.x); z = a.y + (b.y - a.y) * t
            if z < 0: zs.append(z)
    return max(zs)


def catmull(cps, step):
    P_ = [Vector(p) for p in cps]; P_ = [P_[0] * 2 - P_[1]] + P_ + [P_[-1] * 2 - P_[-2]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        m = max(2, int(round((p2 - p1).length / step)))
        for j in range(m):
            t = j / m; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P_[-2])
    return out


def strip(cps, w, salt, tip_start, tip_end):
    """closed outline of a strip along a Catmull-Rom centreline; ends square or with a blunt faceted tip (0.25 m)"""
    c = catmull(cps, 0.80); n = len(c); L, R = [], []
    for i in range(n):
        t = (c[min(i + 1, n - 1)] - c[max(i - 1, 0)]).normalized(); nn = Vector((-t.y, t.x))
        hw = w / 2 + (0.05 * (hsh(i, salt) - 0.5) * 2 if 0 < i < n - 1 else 0.0)
        L.append(c[i] + nn * hw); R.append(c[i] - nn * hw)
    poly = []
    if tip_start:
        t = (c[1] - c[0]).normalized(); poly.append(c[0] - t * 0.25)
    poly += R
    if tip_end:
        t = (c[-1] - c[-2]).normalized(); poly.append(c[-1] + t * 0.25)
    poly += list(reversed(L))
    return poly, c


def path_part():
    P = Part('Path'); bm = P.bm
    o = [p * PLAN for p in outline()]
    x0 = MAIN_CP[0][0] * PLAN
    z0 = max(edge_z(o, x0 - W_MAIN / 2 - 0.1), edge_z(o, x0 + W_MAIN / 2 + 0.1)) + 0.15
    main_cp = [(x0, z0)] + [(x * PLAN, z * PLAN) for x, z in MAIN_CP[1:]]
    main, cm = strip(main_cp, W_MAIN, 50, False, True)
    branch, cb = strip([(x * PLAN, z * PLAN) for x, z in BRANCH_CP], W_BRANCH, 60, False, True)
    # facet points: along both centrelines, alternately 0.35 m left / right
    steiner = []
    for cl, salt in ((cm, 70), (cb, 80)):
        for i in range(1, len(cl) - 1):
            t = (cl[i + 1] - cl[i - 1]).normalized(); nn = Vector((-t.y, t.x))
            steiner.append(cl[i] + nn * (0.35 if i % 2 else -0.35) * (0.6 + 0.4 * hsh(i, salt)))
    pts = [(p.x, p.y) for p in main + branch + steiner]
    nm_, nb = len(main), len(branch)
    vs, es, fs, orig, _, _ = delaunay_2d_cdt(pts, [], [list(range(nm_)), list(range(nm_, nm_ + nb))], 1, 1e-5, True)
    top = [bm.verts.new(V(x, PATH_Y, z)) for x, z in vs]
    bot = [bm.verts.new(V(x, PATH_Y0, z)) for x, z in vs]
    faces = []; ecount = {}
    for fi, f in enumerate(fs):
        h = hsh(fi, 90); slot = SAND if h < 0.55 else (SAND_S if h < 0.80 else SAND_L)
        faces.append(P.face([top[i] for i in f], slot))
        faces.append(P.face([bot[i] for i in reversed(f)], SAND_B))
        for k in range(len(f)):
            e = tuple(sorted((f[k], f[(k + 1) % len(f)]))); ecount[e] = ecount.get(e, 0) + 1
    for (a, b), cnt in ecount.items():
        if cnt == 1: faces.append(P.face([top[a], top[b], bot[b], bot[a]], SAND_S))
    P.comp.append(('path', faces, False))
    global PATH_INFO
    PATH_INFO = dict(main_cp=[(round(x, 3), round(z, 3)) for x, z in main_cp], branch_cp=[(round(x * PLAN, 3), round(z * PLAN, 3)) for x, z in BRANCH_CP],
                     main_end=tuple(round(v, 3) for v in cm[-1]), branch_end=tuple(round(v, 3) for v in cb[-1]))
    return P


PATH_INFO = {}

# ================= DEM-03 clouds =================
# lumps (cx, cy, cz, rx, ry, rz) in the cloud's own frame; lower halves squashed -> flat-ish faceted bottom
CLOUDS = {   # first lump = wide flat base (one continuous flat bottom), then 2-3 rounded bumps on top (Hero clouds)
    'Cloud_A': [(0.0, 1.0, 0.0, 5.6, 1.5, 2.6), (-2.4, 2.0, 0.2, 2.6, 2.1, 2.2), (1.6, 2.4, -0.2, 2.9, 2.4, 2.3),
                (4.2, 1.6, 0.1, 1.9, 1.6, 1.8)],
    'Cloud_B': [(0.0, 0.9, 0.0, 4.6, 1.3, 2.3), (-2.0, 1.8, 0.2, 2.2, 1.8, 1.9), (1.2, 2.1, -0.2, 2.5, 2.1, 2.0),
                (3.4, 1.4, 0.1, 1.5, 1.3, 1.5)],
    'Cloud_C': [(0.0, 0.8, 0.0, 3.7, 1.1, 1.9), (-1.2, 1.7, 0.1, 2.0, 1.7, 1.7), (1.5, 1.5, -0.1, 1.7, 1.5, 1.5)],
    'Cloud_D': [(0.0, 0.7, 0.0, 3.2, 1.0, 1.7), (-0.9, 1.5, 0.1, 1.8, 1.5, 1.5), (1.4, 1.3, -0.1, 1.4, 1.2, 1.3)],
    'Cloud_E': [(0.0, 0.6, 0.0, 2.6, 0.8, 1.4), (-0.6, 1.2, 0.1, 1.5, 1.2, 1.2), (1.2, 1.0, 0.0, 1.1, 1.0, 1.0)],
}
CLOUD_X = {'Cloud_A': -22.0, 'Cloud_B': -8.0, 'Cloud_C': 4.0, 'Cloud_D': 13.0, 'Cloud_E': 21.0}


def lump(P, n, c, r, seed):
    """jittered icosphere (subdivisions 2 = 80 tris), lower half squashed to 30 %; faces turned down get the shade cell"""
    res = bmesh.ops.create_icosphere(P.bm, subdivisions=2, radius=1.0)
    vs = res['verts']
    for i, v in enumerate(vs):
        d = v.co.copy()
        j = 1.0 + 0.10 * math.sin(7.3 * i + 2.1 * seed) * math.cos(3.1 * i + seed)
        x, y, z = d.x * j, d.z * j, d.y * j
        if y < 0: y *= 0.30
        v.co = V(c[0] + x * r[0], c[1] + y * r[1], c[2] + z * r[2])
    fs = list({f for v in vs for f in v.link_faces})
    for f in fs:
        f.normal_update()
        f[P.slot] = CLOUD_S if f.normal.y < -0.45 else CLOUD
    P.comp.append((n, fs, False))


def cloud_part(name):
    P = Part(name); ox = CLOUD_X[name]
    for i, (cx, cy, cz, rx, ry, rz) in enumerate(CLOUDS[name]):
        lump(P, f'lump{i}', (ox + cx, cy, cz), (rx, ry, rz), i + len(name) + ord(name[-1]))
    lo = min(v.co.y for v in P.bm.verts)
    for v in P.bm.verts: v.co.y -= lo                 # bottom of every cloud on y 0 (its origin)
    return P


# ================= scene / objects =================
def make_parts(item):
    if item == 'DEM-01': return [(island_part(), (0, 0, 0))]
    if item == 'DEM-02': return [(path_part(), (0, 0, 0))]
    return [(cloud_part(nm), (CLOUD_X[nm], 0.0, 0.0)) for nm in CLOUDS]


def build_scene():
    if bpy.app.background:
        sc = bpy.context.scene
        for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    else:
        sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
    return sc


def own_collection(sc, name):
    outer = bpy.data.collections.get(OUTER) or bpy.data.collections.new(OUTER)
    if outer.name not in [c.name for c in sc.collection.children]: sc.collection.children.link(outer)
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll.name not in [c.name for c in outer.children]: outer.children.link(coll)
    for o in list(coll.all_objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    return coll


def unity_of(ob):
    t = ob.matrix_world.translation; return [round(-t.x, 4), round(t.z, 4), round(-t.y, 4)]


def fingerprint(obs):
    out = {}
    for k, o in obs.items():
        vs = sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in o.data.vertices)
        out[k] = (len(o.data.vertices), len(o.data.polygons), round(sum(a + 2 * b + 3 * c for a, b, c in vs), 4),
                  round(sum(a * a + b * b + c * c for a, b, c in vs), 4))
    print('FINGERPRINT', out)
    return out


def bvh_world(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t


def make_objects(item, sc, coll, mat):
    name = ITEMS[item]['asset']
    parts = make_parts(item)
    for P, _ in parts:
        for v in P.bm.verts: v.co = to_blender(v.co)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 1.0
    obs = {}
    for P, piv in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, to_blender(V(*piv)), root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    sc.view_layers[0].update()
    return name, root, obs


def build(item=ID):
    sc = build_scene(); name = ITEMS[item]['asset']
    coll = own_collection(sc, name)
    os.makedirs(os.path.dirname(TEX_PATH), exist_ok=True)
    img = pc.atlas_image(TEX_NAME, TEX_PATH, PAL_DEMO); mat = pc.material(MAT_NAME, img)
    name, root, obs = make_objects(item, sc, coll, mat)
    tot = pc.report(obs)
    for o in obs.values():
        pc.coplanar_overlaps(o)
        deg = sum(1 for pg in o.data.polygons if pg.area < 1e-7)
        if deg: print(f'    degenerate faces in {o.name}: {deg}')
    bud = ITEMS[item]['budget']
    print(f'  budget {bud} -> {"OK" if tot <= bud else "OVER"} ({tot} tris, {100 * tot / bud:.0f} %)')
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} parent {o.parent.name}')
    print(f'  root {name} (Unity) {unity_of(root)}')
    extra = None
    if item == 'DEM-01': check_island(obs['Island'])
    if item == 'DEM-02': extra = check_path(sc, obs['Path'], mat)
    if item == 'DEM-03': check_clouds(obs)
    return name, sc, coll, root, img, mat, obs, extra


# ================= item checks =================
def check_island(o):
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    top = [v for v in vs if abs(v.z) < 1e-9]
    up = [p for p in o.data.polygons if p.normal.z > 0.999]
    up_off = [p.index for p in up if any(abs(o.data.vertices[i].co.z) > 0.0 for i in p.vertices)]
    xs = [-v.x for v in top]; zs = [-v.y for v in top]
    print(f'  ISLAND top vertices at Y 0: {len(top)}; upward faces {len(up)}, upward faces not exactly at Y 0: {len(up_off)}')
    print(f'  ISLAND lawn extent X {min(xs):.2f}..{max(xs):.2f} ({max(xs) - min(xs):.2f}) Z {min(zs):.2f}..{max(zs):.2f} '
          f'({max(zs) - min(zs):.2f}) m; bottom Y {min(v.z for v in vs):.2f}')
    bvh = bvh_world(o); miss = 0; bad = 0; n = 0; dev = 0.0
    for i in range(-36, 37):
        for j in range(-27, 28):
            x, z = i * 0.25, j * 0.25; n += 1
            hit = bvh.ray_cast(to_blender(V(x, 1.0, z)), Vector((0, 0, -1)))
            if hit[0] is None: miss += 1
            else:
                dev = max(dev, abs(hit[0].z))
                if abs(hit[0].z) > 1e-5 or hit[1].z < 0.9999: bad += 1
    print(f'  ISLAND garden area x -9..9 z -6.75..6.75 (0.25 m grid, {n} rays): misses {miss}, hits not on the flat Y 0 lawn {bad} '
          f'(max |hit Y| {dev:.1e} m = float ray precision; the lawn vertices themselves are exactly 0)')
    o_ = [p * PLAN for p in outline()]; gx, gz = GARDEN
    print(f'  ISLAND min margin garden rectangle corner -> lawn edge {min(poly_dist(o_, Vector((sx * gx, sz * gz))) for sx in (-1, 1) for sz in (-1, 1)):.2f} m, '
          f'side margin {min(min(abs(p.x) for p in o_ if abs(p.y) < 4.5) - gx, min(abs(p.y) for p in o_ if abs(p.x) < 6) - gz):.2f} m; '
          f'garden {2 * gx:.1f} x {2 * gz:.1f} m = {100 * 4 * gx * gz / lawn_area(o_):.0f} % of the lawn area')


def check_path(sc, o, mat):
    print('  PATH', PATH_INFO)
    tcoll = own_collection(sc, 'TMP_IslandForPathCheck')
    _, troot, tobs = make_objects('DEM-01', sc, tcoll, mat)
    bvh = bvh_world(tobs['Island'])
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    tops = [v for v in vs if abs(v.z - PATH_Y) < 1e-6]; bots = [v for v in vs if abs(v.z - PATH_Y0) < 1e-6]
    gaps = []; miss = 0
    for v in tops:
        hit = bvh.ray_cast(v + Vector((0, 0, 1)), Vector((0, 0, -1)))
        if hit[0] is None or hit[1].z < 0.9999: miss += 1
        else: gaps.append(v.z - hit[0].z)
    xs = [-v.x for v in vs]; zs = [-v.y for v in vs]
    print(f'  PATH vertices {len(vs)}: top Y {PATH_Y} x{len(tops)}, bottom Y {PATH_Y0} x{len(bots)}, other {len(vs) - len(tops) - len(bots)}')
    print(f'  PATH over the lawn: top vertices not over the flat lawn {miss}; top-to-lawn gap min {min(gaps):.4f} max {max(gaps):.4f} m')
    print(f'  PATH extent X {min(xs):.2f}..{max(xs):.2f} Z {min(zs):.2f}..{max(zs):.2f} m')
    return tcoll


def check_clouds(obs):
    for nm, o in obs.items():
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        vs = [o.matrix_world @ v.co for v in o.data.vertices]
        print(f'  {nm}: {t} tris, size {max(v.x for v in vs) - min(v.x for v in vs):.2f} (X) x {max(v.z for v in vs) - min(v.z for v in vs):.2f} (Y) '
              f'x {max(v.y for v in vs) - min(v.y for v in vs):.2f} (Z) m, bottom Y {min(v.z for v in vs):.3f}, origin (Unity) {unity_of(o)}')


# ================= render / verify (from the Farm Machinery demo scripts) =================
def render(sc, coll, out, view_dir, fill_w=0.80, res=(1280, 800), lens=50, bg=(0xB4, 0xD4, 0xF0), extra=()):
    from bpy_extras.object_utils import world_to_camera_view
    r = sc.render
    saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath,
                 vt=sc.view_settings.view_transform, cam=sc.camera, world=sc.world, ft=r.film_transparent)
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_World'); w.use_nodes = True; nt = w.node_tree
    wout = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bgn.inputs['Color'].default_value = (lin(bg[0]), lin(bg[1]), lin(bg[2]), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.82, 0.86, 0.95, 1); amb.inputs['Strength'].default_value = 0.45
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bgn.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], wout.inputs['Surface'])
    sc.world = w
    def sun(nm, rot, e, shadow=True, ang=10):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(ang); ld.use_shadow = shadow
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob); return ob
    s1 = sun('TMP_Sun', (45, 0, 150), 3.4); s2 = sun('TMP_Fill', (70, 0, -20), 0.9, shadow=False)
    cd = bpy.data.cameras.new('TMP_Cam'); cd.lens = lens; cd.clip_end = 1000
    cam = bpy.data.objects.new('TMP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.hide_render]
    for ex in extra: objs += [o for o in ex.all_objects if o.type == 'MESH']
    hidden = [o for o in sc.objects if o.type == 'MESH' and o not in objs]
    for o in hidden: o.hide_render = True
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    target = Vector([(lo[i] + hi[i]) / 2 for i in range(3)]); dirv = Vector(view_dir).normalized()
    def place(dist):
        cam.location = target + dirv * dist
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.view_layers[0].update()
        xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    cd.shift_x = cd.shift_y = 0.0; dist = 60.0
    for _ in range(25):
        x0, x1, y0, y1 = place(dist); dist *= max((x1 - x0) / fill_w, (y1 - y0) / 0.90)
    x0, x1, y0, y1 = place(dist)
    cd.shift_x = (x0 + x1) / 2 - 0.5; cd.shift_y = ((y0 + y1) / 2 - 0.5) * (res[1] / res[0])
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for o in hidden: o.hide_render = False
    for ob in (s1, s2):
        dat = ob.data; bpy.data.objects.remove(ob, do_unlink=True); bpy.data.lights.remove(dat)
    dat = cam.data; bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(dat)
    sc.world = saved['world']; bpy.data.worlds.remove(w)
    r.engine = saved['engine']; r.resolution_x, r.resolution_y, r.resolution_percentage = saved['rx'], saved['ry'], saved['pct']
    r.filepath = saved['fp']; sc.view_settings.view_transform = saved['vt']; sc.camera = saved['cam']; r.film_transparent = saved['ft']
    print('render', out)


def verify_headless(fbx, sc):
    before_o, before_i = set(sc.objects), set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in sc.objects if o not in before_o]
    print('VERIFY objects', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'loc', [round(x, 3) for x in o.matrix_world.translation])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4), 'maxz', round(max(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)


def main():
    name, sc, coll, root, img, mat, obs, extra = build(ID)
    fingerprint(obs)
    ex = (extra,) if extra is not None else ()
    if MODE == 'build':
        os.makedirs(CHECK_DIR, exist_ok=True)
        views = [('ref', REF_VIEW), ('top', TOP_VIEW)] + ([('side', SIDE_VIEW)] if ID != 'DEM-02' else [])
        for tag, view in views:
            render(sc, coll, os.path.join(CHECK_DIR, f'{ID}_check_{tag}.png'), view, 0.85, (960, 600), extra=ex)
        if ID == 'DEM-02':
            render(sc, coll, os.path.join(CHECK_DIR, f'{ID}_check_pathonly_top.png'), TOP_VIEW, 0.85, (960, 600))
    elif MODE == 'export':
        if not bpy.app.background:
            raise RuntimeError('export runs headless only (it selects objects in the context scene)')
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        if extra is not None:                       # the temporary island must not go into the path FBX / blend
            for o in list(extra.all_objects): bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(extra)
        fbx = os.path.join(ART, 'Meshes', name + '.fbx')
        pc.export(name, coll, root, fbx)
        pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
        pv_extra = ()
        if ID == 'DEM-02':                          # preview shows the path on the island (context only)
            tcoll = own_collection(sc, 'TMP_IslandForPreview'); make_objects('DEM-01', sc, tcoll, mat); pv_extra = (tcoll,)
        render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.80, (1280, 800), extra=pv_extra)
        for c in pv_extra:
            for o in list(c.all_objects): bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
        verify_headless(fbx, sc)


main()
