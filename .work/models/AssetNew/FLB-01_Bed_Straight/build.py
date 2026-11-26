# build.py - FLB-01 Straight flower bed 2x1 (FMS_Garden_Bed_Straight + mesh variant _Planted), pack AssetNew
# (Cottage Garden Decor), atlas F Garden_Flora.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- FLB-01 build|export|verify
#   build  = build both models + printed checks (topology, coplanar, ground, tris, SNAP) + check renders to
#            %TEMP%/assetnew_check/FLB-01/
#   export = build + 2 FBX (base, _Planted; each with its .fbm) + 2 collection-only .blend (base; _Planted for
#            make_lod1.py) + ONE preview (base) + FBX re-import verify + geometry dump (JSON, SHA1 of all meshes)
#   verify = only re-import both FBX in art/ (run after make_lod1.py, which rewrites the _Planted FBX with _Low1 children)
#   LOD1 (only _Planted, catalogue):
#     blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#       --python Tools/blender/make_lod1.py -- --art <ABSOLUTE repo>/art/AssetNew FMS_Garden_Bed_Straight_Planted
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\FLB-01_Bed_Straight\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FLB-01', 'build']})
#   Live mode touches only the collection FLB-01_Bed_Straight and its child FLB-01_Bed_Straight_Planted.
#   Headless the collections are named FMS_Garden_Bed_Straight / FMS_Garden_Bed_Straight_Planted (make_lod1.py looks
#   the collection up by the asset name).
# Axes (Blender): X = long side (2.0), Y = short side (1.0), Z = up. Pivot: centre of the footprint on the ground.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FLB-01')
NAME = 'FMS_Garden_Bed_Straight'
VAR = '_Planted'
PREVIEW = 'FMS_Garden_FLB_01_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'          # shared atlas F (Garden_Flora) - READ ONLY here
ATLAS_MAT = 'M_Garden_Flora'
BUDGET, BUDGET_VAR = 300, 1500
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
PINK, PINK_L, WHITE, LILAC, YELLOW = 6, 7, 8, 9, 11
SOIL, STEM, STONE, STONE_L = 12, 13, 14, 15
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FLB-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
COLL = 'FLB-01_Bed_Straight' if LIVE else NAME
COLL_VAR = COLL + VAR
TAU = 2 * math.pi

# ============ snap contract (CATALOG «Модули и стыковка» 6, grid 1.0) ============
HX, HY = 1.0, 0.5                 # footprint half sizes (2.0 x 1.0)
BW, BH = 0.12, 0.25               # border width (inside the footprint), border top
JOINT = 0.01                      # reveal between blocks (spec: small 0.01 reveal allowed)
SOIL_CROWN, SOIL_RIM = 0.20, 0.16
SOIL_IN = 0.01                    # soil skirt reaches 0.01 into the blocks (closed against the inner faces, no coplanar faces)
SOIL_Z0 = 0.005                   # soil bottom (5 mm above the block bottoms: no coplanar bottom faces)
PLANT_MARGIN = 0.02               # plants at least 0.02 inside the outer faces
H_MAX, H_END = 0.70, 0.45         # planting crown on the centre line / at the short ends

# ============ border: 12 hewn blocks, staggered joints (lengths 0.33-0.56) ============
# long sides run the full 2.0 (corner blocks belong to them); short sides fill the inner 0.74 between them
LONG_S = [0.55, 0.45, 0.52, 0.45]          # front (-Y), from -X; sum + 3 joints = 2.0
LONG_N = [0.42, 0.56, 0.48, 0.51]          # back (+Y), from -X (joints staggered against the front)
SHORT_W = [0.40, 0.33]                     # -X end, from -Y; sum + 1 joint = 0.74 (inner span between the long blocks)
SHORT_E = [0.33, 0.40]                     # +X end, from -Y

# ============ soil mound (faceted, flat shaded) ============
# rim ring CCW (x, y, z) on the rectangle reaching SOIL_IN into the blocks; interior points (x, y, z), crown on the centre line
RX, RY = HX - BW + SOIL_IN, HY - BW + SOIL_IN        # 0.89, 0.39
SOIL_RIM_PTS = [(-RX, -RY, 0.146), (-0.50, -RY, 0.163), (-0.05, -RY, 0.150), (0.42, -RY, 0.164), (RX, -RY, 0.147),
                (RX, 0.02, 0.165), (RX, RY, 0.146), (0.60, RY, 0.162), (0.20, RY, 0.149), (-0.30, RY, 0.164),
                (-RX, RY, 0.147), (-RX, -0.02, 0.165)]
# crown line alternating 0.20 / 0.19 (cross ridges), side valleys 0.157-0.162 -> facets with readable light/dark planes.
# 8 interior points -> 26 top + 24 skirt + 10 bottom = 60 tris: at make_lod1's threshold (> 60 is decimated), so the
# soil keeps its exact LOD0 shape (rim closed against the blocks) in the _Planted LOD1.
SOIL_INNER_PTS = [(-0.60, 0.02, 0.192), (-0.24, -0.04, 0.200), (0.12, 0.04, 0.188), (0.50, -0.02, 0.200),
                  (-0.42, 0.22, 0.158), (0.30, 0.22, 0.157), (-0.06, -0.22, 0.162), (0.66, -0.20, 0.161)]

# ============ planting (_Planted) ============
# clumps along the bed: (kind, x, y, drop width D, seed); kinds alternate so that no two same colours touch
CLUMPS = [('yellow', -0.64, 0.12, 0.34, 31), ('pink', -0.43, -0.14, 0.38, 32), ('white', -0.215, 0.14, 0.40, 33),
          ('lilac', 0.00, 0.02, 0.38, 34), ('pink', 0.215, -0.14, 0.40, 35), ('white', 0.43, 0.14, 0.38, 36),
          ('yellow', 0.64, -0.12, 0.34, 37)]
DROP_H = 0.80                     # drop height / width (PLT-01 anchor: 0.80 D)
TOWARD = Vector((-0.45, -0.89, 0.0)).normalized()   # blooms lean towards the front-left viewer side (preview/reference camera)
STALK_ABOVE = 0.09               # stalk bloom at most this far above its drop top (short visible stalks)
DROP_SINK = 0.03                  # drop bottom below the soil surface
CUP_SLOTS = {'pink': (PINK_L, PINK, YELLOW), 'white': (WHITE, WHITE, YELLOW)}   # outer petals, inner petals, centre


def env(x):
    """planting crown height: H_MAX on the centre, H_END at x = +-0.66 (clump row ends)"""
    return max(H_END, H_MAX - (H_MAX - H_END) * (x / 0.66) ** 2)


def pol(az, r, z=0.0):
    a = math.radians(az); return Vector((r * math.cos(a), r * math.sin(a), z))


# ============ helpers copied from PLT-01 build.py (approved generator) ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def bridge(P, A, angA, B, angB, slot):
    """triangle strip between two closed rings of different vertex counts, zipped by angle (PLT-01)"""
    nA, nB = len(A), len(B); faces = []
    ua = [angA[0] + ((angA[i] - angA[0]) % TAU) for i in range(nA)] + [angA[0] + TAU]
    j0 = min(range(nB), key=lambda j: abs(((angB[j] - angA[0] + math.pi) % TAU) - math.pi))
    b0 = angA[0] + (((angB[j0] - angA[0] + math.pi) % TAU) - math.pi)
    ub = [b0 + ((angB[(j0 + k) % nB] - angB[j0]) % TAU) for k in range(nB)] + [b0 + TAU]
    i = j = 0
    while i < nA or j < nB:
        if j >= nB or (i < nA and ua[i + 1] <= ub[j + 1]):
            faces.append(P.face([A[i % nA], A[(i + 1) % nA], B[(j0 + j) % nB]], slot)); i += 1
        else:
            faces.append(P.face([A[i % nA], B[(j0 + j) % nB], B[(j0 + j + 1) % nB]], slot)); j += 1
    return faces


def leaf_cluster(c, D, seed, H=0.80, widest=0.40, noise=0.035, sub=2, under_k=0.85, up=0.6, down=-0.2):
    """LEAF CLUSTER v2 (PLT-01): faceted domed foliage drop from a full ico sphere (sub 2 = 80 tris), re-profiled
    (widest ring at `widest` of the height, domed top, rounded underside), +-noise per vertex (fixed seed).
    Width ~D, height H*D, centre c = mid-height. Face slot by normal: up -> LEAF_UP, side -> LEAF, down -> LEAF_DN."""
    rnd = random.Random(seed)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rnd.uniform(0, TAU), 3, 'Z'))
    for v in bm.verts:
        zo = max(-1.0, min(1.0, v.co.z)); ro = math.sqrt(max(0.0, 1 - zo * zo)); az = math.atan2(v.co.y, v.co.x)
        if zo >= 0: f, r = widest + (1 - widest) * zo, ro
        else: f, r = widest * (1 + zo), ro * (1 - (1 - under_k) * (-zo))
        n = Vector([rnd.uniform(-noise, noise) for _ in range(3)])
        v.co = Vector((r * math.cos(az) * D / 2, r * math.sin(az) * D / 2, (f - 0.5) * H * D)) + n + Vector(c)
    bm.normal_update()
    slots = [LEAF_UP if f.normal.z > up else (LEAF_DN if f.normal.z < down else LEAF) for f in bm.faces]
    return bm, slots


def inside(bvh, q):
    n_hit = 0; o = Vector(q)
    for _ in range(12):
        h = bvh.ray_cast(o + Vector((0, 0, 1e-5)), Vector((0, 0, 1)))
        if h[0] is None: break
        n_hit += 1; o = h[0]
    return n_hit % 2 == 1


# ============ primitives ============
def block(P, cname, x0, x1, y0, y1):
    """hewn stone block: closed box on the ground, flat light top (F-15), sides and bottom stone (F-14)"""
    bm = P.bm
    V = [bm.verts.new((x, y, z)) for z in (0.0, BH) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    f = [P.face([V[3], V[2], V[1], V[0]], STONE), P.face([V[4], V[5], V[6], V[7]], STONE_L)]
    for k in range(4):
        k1 = (k + 1) % 4
        f.append(P.face([V[k], V[k1], V[4 + k1], V[4 + k]], STONE))
    P.comp.append((cname, f, True))


def border_blocks():
    """[(name, x0, x1, y0, y1)] of the 12 blocks; outer faces exactly on X +-1.0 / Y +-0.5"""
    out = []
    for side, lens, y0, y1 in (('S', LONG_S, -HY, -HY + BW), ('N', LONG_N, HY - BW, HY)):
        x = -HX
        for i, L in enumerate(lens):
            out.append((f'Block_{side}{i}', x, x + L, y0, y1)); x += L + JOINT
        assert abs(x - JOINT - HX) < 1e-9, (side, x)
    ys = -HY + BW + JOINT
    for side, lens, x0, x1 in (('W', SHORT_W, -HX, -HX + BW), ('E', SHORT_E, HX - BW, HX)):
        y = ys
        for i, L in enumerate(lens):
            out.append((f'Block_{side}{i}', x0, x1, y, y + L)); y += L + JOINT
        assert abs(y - JOINT - (HY - BW - JOINT)) < 1e-9, (side, y)
    return out


def soil_tris():
    """faceted mound: CDT of the rim polygon + interior points -> (points xyz, triangles, rim indices)"""
    pts = SOIL_RIM_PTS + SOIL_INNER_PTS; n = len(SOIL_RIM_PTS)
    res = delaunay_2d_cdt([Vector((x, y)) for x, y, _ in pts], [(i, (i + 1) % n) for i in range(n)], [], 0, 1e-6)
    vco, _, faces, orig, _, _ = res
    assert len(vco) == len(pts), 'CDT inserted vertices'
    m = [orig[i][0] for i in range(len(vco))]
    return pts, [tuple(m[i] for i in f) for f in faces], list(range(n))


def soil(P):
    pts, tris, rim = soil_tris()
    V = [P.bm.verts.new(p) for p in pts]
    f = [P.face([V[a], V[b], V[c]], SOIL) for a, b, c in tris]
    B = [P.bm.verts.new((x, y, SOIL_Z0)) for x, y, _ in SOIL_RIM_PTS]
    n = len(rim)
    for k in range(n):
        k1 = (k + 1) % n
        f.append(P.face([V[k], V[k1], B[k1], B[k]], SOIL))
    f.append(P.face(list(reversed(B)), SOIL))
    P.comp.append(('Soil', f, False))


def soil_bvh():
    pts, tris, _ = soil_tris()
    return BVHTree.FromPolygons([Vector(p) for p in pts], [list(t) for t in tris])


def petal_rim(p, a, r, h, spin, notch_r=0.90, notch_dz=0.014):
    """8 rim points: petal tips (r, height h) alternating with notches (notch_r * r, h - notch_dz)"""
    rp, ra = ring(p + a * h, a, r, 8, spin); O = p + a * h
    return [O + (q - O) * (1.0 if k % 2 == 0 else notch_r) - (a * (0.0 if k % 2 == 0 else notch_dz))
            for k, q in enumerate(rp)], ra


def cup_bloom(P, p, a, spin, slots, depth=0.03, r=0.05, h=0.045, hc=0.022, rc=0.016):
    """8-sided cup bloom, ONE closed shell, 22 tris, Ø0.10 x 0.045 (wider than tall): buried apex -> petal rim
    (4 raised tips + 4 notches, outer petals) -> inside of the cup to a 4-sided centre (inner petals) -> flat centre
    (yellow)."""
    so, si, sc = slots; a = Vector(a).normalized(); p = Vector(p)
    A = P.bm.verts.new(p - a * depth)
    rp, ra = petal_rim(p, a, r, h, spin)
    R = [P.bm.verts.new(q) for q in rp]
    cp, ca = ring(p + a * hc, a, rc, 4, spin + math.pi / 8)
    C = [P.bm.verts.new(q) for q in cp]
    f = [P.face([A, R[(k + 1) % 8], R[k]], so) for k in range(8)]
    f += bridge(P, R, ra, C, ca, si)
    f.append(P.face(C, sc))
    return f


def small_cup(P, p, a, spin, slot=YELLOW, depth=0.025, r=0.042, h=0.034, hc=0.014):
    """small 8-sided yellow cup, ONE closed shell, 16 tris, Ø0.084: buried apex -> petal rim -> sunken centre"""
    a = Vector(a).normalized(); p = Vector(p)
    A = P.bm.verts.new(p - a * depth); Cv = P.bm.verts.new(p + a * hc)
    R = [P.bm.verts.new(q) for q in petal_rim(p, a, r, h, spin, notch_dz=0.010)[0]]
    return [P.face([A, R[(k + 1) % 8], R[k]], slot) for k in range(8)] + \
           [P.face([R[k], R[(k + 1) % 8], Cv], slot) for k in range(8)]


def spike(P, base, a, L, spin, r=0.036, t_ring=0.28, depth=0.05, slot=LILAC):
    """lilac flower spike: 6-sided bipyramid, ONE closed shell, 12 tris; lower apex buried `depth` in the foliage,
    widest ring at t_ring of the visible length L, tip at base + a*L"""
    a = Vector(a).normalized(); base = Vector(base)
    lo = P.bm.verts.new(base - a * depth); hi = P.bm.verts.new(base + a * L)
    Rg = [P.bm.verts.new(q) for q in ring(base + a * (L * t_ring), a, r, 6, spin)[0]]
    return [P.face([lo, Rg[(k + 1) % 6], Rg[k]], slot) for k in range(6)] + \
           [P.face([Rg[k], Rg[(k + 1) % 6], hi], slot) for k in range(6)]


def stalk(P, p0, p1, r=0.012, n=3, slot=STEM):
    """thin flower stalk: n-sided prism, both ends capped (closed), 3 sides = 8 tris"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    R0 = [P.bm.verts.new(q) for q in ring(p0, d, r, n, 0.0)[0]]
    R1 = [P.bm.verts.new(q) for q in ring(p1, d, r, n, 0.0)[0]]
    f = [P.face([R0[k], R0[(k + 1) % n], R1[(k + 1) % n], R1[k]], slot) for k in range(n)]
    f += [P.face(list(reversed(R0)), slot), P.face(list(R1), slot)]
    return f


# ============ planting layout (computed once, emitted into any Part) ============
def plan_planting():
    """returns drops [(name, verts, faces, slots)] and flower primitives [(name, kind, args)]"""
    sb = soil_bvh(); drops = []; prims = []; warn = []
    down = Vector((0, 0, -1))
    def soil_z(x, y): return sb.ray_cast(Vector((x, y, 1.0)), down)[0].z
    for ci, (kind, x, y, D, seed) in enumerate(CLUMPS):
        z0 = soil_z(x, y) - DROP_SINK
        c = Vector((x, y, z0 + 0.5 * DROP_H * D))
        bm, slots = leaf_cluster(c, D, seed, H=DROP_H, noise=0.025)
        bvh = BVHTree.FromBMesh(bm)
        bm.verts.index_update()
        drops.append((f'Drop_{ci}{kind[0].upper()}', [v.co.copy() for v in bm.verts],
                      [[v.index for v in f.verts] for f in bm.faces], slots))
        bm.free()
        def hit(dx, dy): return bvh.ray_cast(Vector((x + dx, y + dy, 2.0)), down)[0]
        def tilt_axis(dx, dy, deg):
            """bloom axis tilted `deg` from vertical towards the viewer side, with a little of the outward offset"""
            out = Vector((dx, dy, 0.0)); out = out.normalized() if out.length > 1e-6 else Vector((0, 0, 0))
            d = (TOWARD + out * 0.45).normalized(); ax = d.cross(Vector((0, 0, 1)))
            return Matrix.Rotation(math.radians(-deg), 3, ax.normalized()) @ Vector((0, 0, 1))
        top = env(x); dtop = hit(0.0, 0.0).z
        if kind in CUP_SLOTS:
            # 2 blooms on the foliage, 2 on short stalks rising towards the crown envelope (capped at drop top + 0.11)
            for bi, (dx, dy, tl) in enumerate(((-0.08, -0.06, 28), (0.085, 0.05, 24))):
                p = hit(dx, dy); a = tilt_axis(dx, dy, tl)
                prims.append((f'Bloom_{ci}{bi}', 'cup', (p, a, math.radians(20 * bi + 5 * ci), CUP_SLOTS[kind])))
                if not inside(bvh, p - a * 0.025): warn.append(f'bloom {ci}{bi} apex outside its drop')
            for si, (dx, dy, dz, tl) in enumerate(((0.035, -0.04, 0.0, 22), (-0.05, 0.06, -0.04, 20))):
                p1 = Vector((x + dx, y + dy, min(top - 0.035, dtop + STALK_ABOVE) + dz))
                p0 = c + Vector((dx * 0.3, dy * 0.3, 0.0))
                a = tilt_axis(dx, dy, tl)
                prims.append((f'Stalk_{ci}{si}', 'stalk', (p0, p1)))
                prims.append((f'Bloom_{ci}S{si}', 'cup', (p1, a, math.radians(10 + 30 * si), CUP_SLOTS[kind])))
        elif kind == 'yellow':
            offs = [(0.0, 0.0, 12)] + [(0.085 * math.cos(math.radians(az)), 0.085 * math.sin(math.radians(az)), 28)
                                        for az in (-100, -30, 40, 110, 180)]
            for bi, (dx, dy, tl) in enumerate(offs):
                p = hit(dx, dy); a = tilt_axis(dx, dy, tl)
                prims.append((f'Cup_{ci}{bi}', 'small', (p, a, math.radians(13 * bi))))
                if not inside(bvh, p - a * 0.02): warn.append(f'cup {ci}{bi} apex outside its drop')
        elif kind == 'lilac':
            offs = [(0.0, 0.0, 0.0)] + [(0.105 * math.cos(math.radians(az)), 0.105 * math.sin(math.radians(az)), 0.0)
                                        for az in (-95, -35, 25, 85, 150, 210)]
            for bi, (dx, dy, _) in enumerate(offs):
                p = hit(dx, dy)
                lean = Vector((dx * 1.8, dy * 1.8, 1.0)).normalized()
                tip_z = top - (0.0 if bi == 0 else (0.05, 0.09, 0.07)[bi % 3])
                L = (tip_z - p.z) / lean.z
                prims.append((f'Spike_{ci}{bi}', 'spike', (p, lean, L, math.radians(10 * bi))))
                if not inside(bvh, p - lean * 0.04): warn.append(f'spike {ci}{bi} base outside its drop')
    for w in warn: print('  WARNING', w)
    return drops, prims


def emit_drops(P, drops):
    for nm, vs, fs, slots in drops:
        V = [P.bm.verts.new(v) for v in vs]
        P.comp.append((nm, [P.face([V[i] for i in f], s) for f, s in zip(fs, slots)], False))


def emit_flowers(P, prims):
    for nm, kind, args in prims:
        if kind == 'cup': f = cup_bloom(P, *args)
        elif kind == 'small': f = small_cup(P, *args)
        elif kind == 'spike': f = spike(P, *args)
        else: f = stalk(P, *args)
        P.comp.append((nm, f, False))


# ============ parts (objects) ============
# base: one mesh. _Planted: role-based parts so make_lod1.py halves only the planting (border parts of 4 blocks =
# 48 tris and the soil stay below its 60-tri threshold and keep their exact LOD0 shape -> snap contract holds in LOD1).
PLANTED_PARTS = {'Border_S': lambda n: n.startswith('Block_S'), 'Border_N': lambda n: n.startswith('Block_N'),
                 'Border_Ends': lambda n: n[:7] in ('Block_W', 'Block_E')}


def gen_bed(P, pick=lambda n: True, with_soil=True):
    for nm, x0, x1, y0, y1 in border_blocks():
        if pick(nm): block(P, nm, x0, x1, y0, y1)
    if with_soil: soil(P)


def to_obj(P, oname, coll, mat, root):
    """pc.to_object without the per-part comp_checks (checks run on the whole model, see build())"""
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = pc.cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    me = bpy.data.meshes.new(oname); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(oname, me); coll.objects.link(ob); ob.parent = root
    return ob


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    cv = bpy.data.collections.get(COLL_VAR) or bpy.data.collections.new(COLL_VAR)
    if LIVE:                                   # live: variant nested in the item collection
        if coll.name not in sc.collection.children: sc.collection.children.link(coll)
        if cv.name not in coll.children: coll.children.link(cv)
    else:                                      # headless: both top level (make_lod1 loads each collection by name)
        for c in (coll, cv):
            if c.name not in sc.collection.children: sc.collection.children.link(c)
    for c in (coll, cv):
        for o in list(c.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:        # factory-startup scene: drop the default cube/light/camera
        keep = set(coll.objects) | set(cv.objects)
        for o in list(sc.objects):
            if o not in keep: bpy.data.objects.remove(o, do_unlink=True)
    return coll, cv


def atlas_and_material():
    """reuse the shared atlas F PNG (never rewritten here) and M_Garden_Flora (created only when missing)"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(PAL_F):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), tuple(img.size), 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


# ============ checks ============
def world_pts(objs):
    return [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]


def bbox(objs):
    pts = world_pts(objs)
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def all_coplanar(objs):
    """coplanar overlapping face pairs on all parts merged (also catches overlaps between part objects)"""
    me = bpy.data.meshes.new('TMP_FLB01_cop'); bm = bmesh.new()
    for o in objs:
        if o.type != 'MESH': continue
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        tm = bpy.data.meshes.new('TMP_FLB01_part'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_FLB01_cop', me)
    n, s = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def snap_checks(base_objs, var_objs, var_plants):
    """SNAP contract: footprint on the 1.0 grid, border top 0.25, soil <= 0.20, beds touching along X and Y without
    overlap, plants inside the footprint (margin 0.02) and below 0.70"""
    tol = 0.001; ok_all = True
    def say(ok, msg):
        nonlocal ok_all; ok_all &= ok; print(('  SNAP OK   ' if ok else '  SNAP FAIL ') + msg)
    for label, objs in (('base', base_objs), ('planted', var_objs)):
        lo, hi = bbox(objs)
        say(abs(lo[0] + HX) <= tol and abs(hi[0] - HX) <= tol and abs(lo[1] + HY) <= tol and abs(hi[1] - HY) <= tol
            and abs(lo[2]) <= 1e-6, f'{label}: footprint x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} min z {lo[2]:.4f}')
        for ax, step, nm in ((0, 2.0, 'X (end to end, +2.0)'), (1, 1.0, 'Y (side by side, +1.0)')):
            gap = (lo[ax] + step) - hi[ax]
            say(abs(gap) <= tol, f'{label} | {label} along {nm}: gap {gap:+.4f} (touch, no overlap)')
    lo_b, hi_b = bbox(base_objs); lo_v, hi_v = bbox(var_objs)
    gap = (lo_v[0] + 2.0) - hi_b[0]
    say(abs(gap) <= tol, f'base | planted along X (+2.0): gap {gap:+.4f}')
    gap = (lo_v[1] + 1.0) - hi_b[1]
    say(abs(gap) <= tol, f'base | planted along Y (+1.0): gap {gap:+.4f}')
    say(abs(hi_b[2] - BH) <= tol, f'border top {hi_b[2]:.4f} (contract 0.25)')
    sz = max(p[2] for p in SOIL_RIM_PTS + SOIL_INNER_PTS)
    say(sz <= SOIL_CROWN + 1e-9 and abs(sz - SOIL_CROWN) <= tol, f'soil crown {sz:.3f} (contract 0.20, below the border top)')
    lo_p, hi_p = bbox(var_plants)
    m = min(HX - max(abs(lo_p[0]), abs(hi_p[0])), HY - max(abs(lo_p[1]), abs(hi_p[1])))
    say(m >= PLANT_MARGIN - 1e-6 and hi_p[2] <= H_MAX + tol,
        f'planting x {lo_p[0]:.3f}..{hi_p[0]:.3f} y {lo_p[1]:.3f}..{hi_p[1]:.3f} top {hi_p[2]:.3f} | margin to the outer face {m:.3f} (>= 0.02)')
    for nm, x0, x1, y0, y1 in border_blocks():
        outer = [abs(c) for c in (x0, x1, y0, y1)]
        if not any(abs(c - HX) < 1e-9 or abs(c - HY) < 1e-9 for c in outer): say(False, f'{nm} has no outer face on the footprint')
    print('  SNAP', 'ALL OK' if ok_all else 'FAILED')
    return ok_all


def plants_vs_border(drops, prims):
    """planting shells that intersect a border block (should be none: plants grow from the soil, not through stones)"""
    Pb = Part('chk_b'); gen_bed(Pb, with_soil=False); Pb.bm.verts.index_update()
    pos = [v.co.copy() for v in Pb.bm.verts]
    bt = BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in Pb.bm.faces]); Pb.bm.free()
    Pp = Part('chk_p'); emit_drops(Pp, drops); emit_flowers(Pp, prims); Pp.bm.verts.index_update()
    pos = [v.co.copy() for v in Pp.bm.verts]; hits = []
    for nm, fs, _ in Pp.comp:
        t = BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs])
        if t.overlap(bt): hits.append(nm)
    Pp.bm.free()
    print('  planting shells touching the border blocks:', hits)
    return hits


def build():
    coll, cv = clear_own()
    img, mat = atlas_and_material()
    drops, prims = plan_planting()
    # --- whole-model checks (one Part each: blocks + soil + planting, so contacts between parts are counted)
    print('CHECK base (blocks + soil):')
    Pc = Part('Base'); gen_bed(Pc); pt_base = part_tris(Pc)
    Pc.bm.normal_update(); bmesh.ops.recalc_face_normals(Pc.bm, faces=Pc.bm.faces)
    cb = pc.comp_checks(Pc, mirror_skip=tuple(n for n, _, _ in Pc.comp)); Pc.bm.free()
    print('CHECK planted (blocks + soil + planting):')
    Pc = Part('Planted'); gen_bed(Pc); emit_drops(Pc, drops); emit_flowers(Pc, prims); pt_var = part_tris(Pc)
    bmesh.ops.recalc_face_normals(Pc.bm, faces=Pc.bm.faces)
    cv_ = pc.comp_checks(Pc, mirror_skip=tuple(n for n, _, _ in Pc.comp)); Pc.bm.free()
    pvb = plants_vs_border(drops, prims)
    # --- base: one mesh
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = Part('Body'); gen_bed(P); ob = to_obj(P, NAME + '_Body', coll, mat, root)
    # --- _Planted: role parts
    vroot = bpy.data.objects.new(NAME + VAR, None); cv.objects.link(vroot)
    vobs = {}
    for pn, pick in PLANTED_PARTS.items():
        P = Part(pn); gen_bed(P, pick, with_soil=False); vobs[pn] = to_obj(P, f'{NAME}{VAR}_{pn}', cv, mat, vroot)
    P = Part('Soil'); soil(P); vobs['Soil'] = to_obj(P, f'{NAME}{VAR}_Soil', cv, mat, vroot)
    P = Part('Foliage'); emit_drops(P, drops); vobs['Foliage'] = to_obj(P, f'{NAME}{VAR}_Foliage', cv, mat, vroot)
    P = Part('Flowers'); emit_flowers(P, prims); vobs['Flowers'] = to_obj(P, f'{NAME}{VAR}_Flowers', cv, mat, vroot)
    bpy.context.view_layer.update()
    print('REPORT base:'); tot = pc.report({'Body': ob})
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}', '| parts', pt_base)
    print('REPORT planted:'); tot_v = pc.report(vobs)
    print(f'  budget {BUDGET_VAR} ->', 'OK' if tot_v <= BUDGET_VAR else f'x{tot_v / BUDGET_VAR:.2f}', '| parts', pt_var)
    print('  flowers:', {k: sum(1 for _, kk, _ in prims if kk == k) for k in ('cup', 'small', 'spike', 'stalk')})
    n_cop = all_coplanar([ob]); n_cop_v = all_coplanar(list(vobs.values()))
    snap = snap_checks([ob], list(vobs.values()), [vobs['Foliage'], vobs['Flowers']])
    print(f'SUMMARY base: tris {tot}/{BUDGET} nonmanifold {cb["nonmanifold"]} loose {cb["loose"]} degenerate {cb["degenerate"]} '
          f'coplanar {n_cop} problems {cb["problems"]}')
    print(f'SUMMARY planted: tris {tot_v}/{BUDGET_VAR} nonmanifold {cv_["nonmanifold"]} loose {cv_["loose"]} '
          f'degenerate {cv_["degenerate"]} coplanar {n_cop_v} problems {cv_["problems"]} plants-in-border {pvb} SNAP {"OK" if snap else "FAIL"}')
    return coll, cv, root, ob, vroot, vobs, img, mat


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


# ---------------- renders (temporary scene: the open scene and its settings are not touched; copied from PLT-01) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_FLB01_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_FLB01_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_FLB01_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_FLB01_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_FLB01_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_FLB01_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new('TMP_FLB01_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = world_pts(objs)
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 8.0
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


def export_keep_selection(name, coll, root, fbx):
    """pc.export changes the selection: restore the owner's selection and active object afterwards (live)"""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    try:
        return pc.export(name, coll, root, fbx)
    finally:
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act


# reference: long side to the camera, left end visible (camera at front-left), ~30 deg above, near-orthographic
VIEW_REF = (-0.36, -1.0, 0.62)
VIEW_PREVIEW = (-0.55, -1.0, 0.68)            # series preview 3/4 (~30 deg), same side as the reference

if MODE == 'verify':
    for suf in ('', VAR): pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    coll, cv, root, ob, vroot, vobs, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    base_objs = [root, ob]; var_objs = [vroot] + list(vobs.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(base_objs, os.path.join(CHECK_DIR, f'FLB-01_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.84, fill_h=0.84, lens=None)
        render(var_objs, os.path.join(CHECK_DIR, f'FLB-01P_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.84, fill_h=0.84, lens=None)
        render(base_objs, os.path.join(CHECK_DIR, f'FLB-01_34_{tag}.png'), VIEW_PREVIEW)
        render(var_objs, os.path.join(CHECK_DIR, f'FLB-01P_34_{tag}.png'), VIEW_PREVIEW)
        render(base_objs, os.path.join(CHECK_DIR, f'FLB-01_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
        render(var_objs, os.path.join(CHECK_DIR, f'FLB-01P_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_keep_selection(NAME, coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        fbx_v = export_keep_selection(NAME + VAR, cv, vroot, os.path.join(ART, 'Meshes', NAME + VAR + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        save_lib(os.path.join(ART, 'Blend', NAME + VAR + '.blend'), cv, mat, img)
        render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx); pc.verify(fbx_v)
    if MODE in ('export', 'dump'):
        geom_dump([ob] + list(vobs.values()), os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
