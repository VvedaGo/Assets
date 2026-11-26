# build.py - FLB-02 Corner (L) flower bed 2x2 (FMS_Garden_Bed_Corner) and FLB-03 Round flower bed D2
# (FMS_Garden_Bed_Round), each + mesh variant _Planted; pack CottageGardenDecor (Cottage Garden Decor), atlas F Garden_Flora.
# Registry form (one file, two items):
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- <FLB-02|FLB-03> build|export|verify
#   build  = build both models of the item + printed checks (topology, coplanar, ground, tris, SNAP) + check renders to
#            %TEMP%/assetnew_check/<ID>/
#   export = build + 2 FBX (base, _Planted; each with its .fbm) + 2 collection-only .blend (base; _Planted for
#            make_lod1.py) + ONE preview (base) + FBX re-import verify + geometry dump (JSON, SHA1 of all meshes)
#            + headless _Planted check render <ID>_Planted_check.png (same camera as the preview)
#   verify = only re-import both FBX in art/ (run after make_lod1.py, which rewrites the _Planted FBX with _Low1 children)
#   LOD1 (only _Planted, catalogue):
#     blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#       --python Tools/blender/make_lod1.py -- --art <ABSOLUTE repo>/art/CottageGardenDecor FMS_Garden_Bed_Corner_Planted
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\FLB-02+FLB-03_Bed\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FLB-02', 'build']})
#   Live mode touches only the collection <ID>_Bed_<Name> and its child <ID>_Bed_<Name>_Planted.
#   Headless the collections are named after the asset (make_lod1.py looks the collection up by the asset name).
# Axes (Blender): X, Y ground, Z up. Pivot: centre of the 2.0 x 2.0 footprint bounding box on the ground.
# Series mapping Blender (x, y, z) -> Unity (-x, z, -y) (Unity's FBX import negates X; -Z forward baked).
#   FLB-02: spec missing quadrant Unity X > 0, Z > 0  ->  Blender x < 0, y < 0 (front-left, faces the preview camera as in
#   the reference); corner square Unity X, Z -1..0 -> Blender x, y 0..1.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
ATLAS_TEX = 'FMS_Garden_AtlasF.png'          # shared atlas F (Garden_Flora) - READ ONLY here
ATLAS_MAT = 'M_Garden_Flora'
FLB01_BLEND = os.path.join(ART, 'Blend', 'FMS_Garden_Bed_Straight.blend')   # read-only (linked for the SNAP pair test)
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
PINK, PINK_L, WHITE, LILAC, YELLOW = 6, 7, 8, 9, 11
SOIL, STEM, STONE, STONE_L = 12, 13, 14, 15
VAR = '_Planted'
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FLB-02'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi

# ============ snap contract (CATALOG «Модули и стыковка» 6, grid 1.0) ============
BW, BH = 0.12, 0.25               # border width (inside the footprint), border top
JOINT = 0.01                      # reveal between blocks (spec: 0.01 allowed)
SOIL_CROWN = 0.20
SOIL_IN = 0.01                    # soil rim reaches 0.01 into the blocks (closed against the inner faces, no coplanar faces)
SOIL_Z0 = 0.005                   # soil bottom (5 mm above the block bottoms: no coplanar bottom faces)
PLANT_MARGIN = 0.02               # plants at least 0.02 inside the outer faces
TOWARD = Vector((-0.45, -0.89, 0.0)).normalized()   # blooms lean towards the front-left viewer side (preview camera)
DROP_SINK = 0.03                  # drop bottom below the soil surface
CUP_SLOTS = {'pink': (PINK_L, PINK, YELLOW), 'white': (WHITE, WHITE, YELLOW)}   # outer petals, inner petals, centre


def pol(az, r, z=None):
    a = math.radians(az); return (r * math.cos(a), r * math.sin(a)) if z is None else (r * math.cos(a), r * math.sin(a), z)


# =====================================================================================================================
# FLB-02 corner bed: L polygon (Blender), CCW: missing quadrant x < 0, y < 0
# =====================================================================================================================
L_POLY = [(-1.0, 0.0), (0.0, 0.0), (0.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]


def blocks_L():
    """16 hewn blocks [(name, quad CCW)]: outer faces exactly on the L outline, 0.01 reveals, staggered lengths 0.40-0.53.
    back (y 0.88..1) runs x -0.87..1.0 (owns corner +x+y); right (x 0.88..1) y 0.87..-1.0 (owns +x-y); front of the right
    arm (y -1..-0.88) x 0..0.87 (owns 0,-1); inner x side (x 0..0.12) y -0.87..0.12 (its top block is the closed
    re-entrant corner block); inner y side (y 0..0.12) x -1.0..-0.01 (owns -1,0); left (x -1..-0.88) y 0.13..1.0 (owns -1,+1)"""
    out = []
    def run(tag, lens, start, sign, fixed0, fixed1, along_x):
        p = start
        for i, L in enumerate(lens):
            a, b = (p, p + L) if sign > 0 else (p - L, p)
            x0, x1, y0, y1 = (a, b, fixed0, fixed1) if along_x else (fixed0, fixed1, a, b)
            out.append((f'Block_{tag}{i}', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
            p += sign * (L + JOINT)
        return p - sign * JOINT
    e = run('B', [0.48, 0.42, 0.50, 0.44], -0.87, +1, 1.0 - BW, 1.0, True); assert abs(e - 1.0) < 1e-9, e
    e = run('R', [0.44, 0.50, 0.42, 0.48], 0.87, -1, 1.0 - BW, 1.0, False); assert abs(e + 1.0) < 1e-9, e
    e = run('F', [0.46, 0.40], 0.0, +1, -1.0, -1.0 + BW, True); assert abs(e - 0.87) < 1e-9, e
    e = run('X', [0.45, 0.53], -0.87, +1, 0.0, BW, False); assert abs(e - 0.12) < 1e-9, e
    e = run('Y', [0.52, 0.46], -1.0, +1, 0.0, BW, True); assert abs(e + 0.01) < 1e-9, e
    e = run('W', [0.42, 0.44], 0.13, +1, -1.0, -1.0 + BW, False); assert abs(e - 1.0) < 1e-9, e
    return out


def soil_L():
    """faceted mound inside the L: rim (inset 0.11 = 0.01 into the blocks) 16 points (0.141-0.168) + 10 interior points (crown on the
    arm centre lines 0.192-0.20, valleys 0.142-0.150); skirt = one vertical polygon per rim edge down to the 6 corners at
    SOIL_Z0, L-shaped bottom cap. 34 top + 22 skirt + 4 bottom = 60 tris (<= 60: make_lod1 keeps it exact)."""
    r = 1.0 - BW + SOIL_IN                                    # 0.89
    c = 0.0 + BW - SOIL_IN                                    # 0.11 (re-entrant corner)
    corners = [(-r, c), (c, c), (c, -r), (r, -r), (r, r), (-r, r)]
    # rim heights 0.146-0.165, mid-edge points per edge (t along the edge, z)
    mids = [[(0.50, 0.167)],                                   # inner y edge  (-r,c)->(c,c)
            [(0.50, 0.166)],                                   # inner x edge  (c,c)->(c,-r)
            [(0.50, 0.142)],                                   # front edge    (c,-r)->(r,-r)
            [(0.25, 0.167), (0.52, 0.141), (0.77, 0.168)],     # right edge    (r,-r)->(r,r)
            [(0.24, 0.142), (0.50, 0.168), (0.76, 0.141)],     # back edge     (r,r)->(-r,r)
            [(0.50, 0.142)]]                                   # left edge     (-r,r)->(-r,c)
    cz = [0.145, 0.156, 0.144, 0.146, 0.143, 0.146]
    rim, corner_idx = [], []
    for k, (p, ms) in enumerate(zip(corners, mids)):
        q = corners[(k + 1) % 6]; corner_idx.append(len(rim)); rim.append((p[0], p[1], cz[k]))
        for t, z in ms: rim.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, z))
    inner = [(-0.60, 0.52, 0.196), (-0.18, 0.49, 0.200), (0.52, 0.52, 0.200), (0.50, -0.18, 0.197), (0.48, -0.60, 0.192),
             (-0.40, 0.27, 0.144), (-0.02, 0.75, 0.146), (0.30, 0.30, 0.150), (0.76, 0.06, 0.145), (0.26, -0.42, 0.142)]
    return rim, corner_idx, corners, inner


# =====================================================================================================================
# FLB-03 round bed: 16 trapezoid blocks, outer 16-gon vertices on radius 1.0 (one at 0/90/180/270 deg -> bbox +-1.0)
# =====================================================================================================================
N_RING = 16
R_OUT, R_IN = 1.0, 1.0 - BW       # 1.0 / 0.88 (polygon vertex radii)
RING_POLY = [pol(22.5 * k, R_OUT) for k in range(N_RING)]


def blocks_round():
    """block k between outer vertices O_k, O_k+1 (shared exactly with the neighbour: footprint vertices stay on R 1.0);
    the inner corners are pulled back along the inner polygon edge by JOINT/2 -> tapered reveal 0 (outer) .. 0.01 (inner)
    = a dark joint line on top as in the reference, no coplanar joint faces (faces diverge 4.8 deg)."""
    out = []
    for k in range(N_RING):
        o0, o1 = Vector(pol(22.5 * k, R_OUT)), Vector(pol(22.5 * (k + 1), R_OUT))
        i0, i1 = Vector(pol(22.5 * k, R_IN)), Vector(pol(22.5 * (k + 1), R_IN))
        d = (i1 - i0).normalized() * (JOINT / 2)
        out.append((f'Block_{k:02d}', [tuple(o0), tuple(o1), tuple(i1 - d), tuple(i0 + d)]))
    return out


def soil_round():
    """faceted low dome: rim of 16 points on R 0.89 (0.01 into the blocks) at the block joint angles, apex 0.20,
    rim 0.136-0.168 + 6 shoulder points on R 0.47-0.52 (0.172-0.194) -> 28 top tris; skirt: 16 triangles down to an
    octagon on R 0.963 (its edges pass under the odd rim points) + 8 vertical triangles; octagon cap. 28 + 24 + 6 = 58 tris (<= 60: make_lod1 keeps it exact)."""
    rr = R_IN + SOIL_IN
    rz = [0.138, 0.166, 0.144, 0.168, 0.136, 0.164, 0.146, 0.168, 0.137, 0.165, 0.143, 0.168, 0.136, 0.166, 0.147, 0.167]
    rim = [pol(22.5 * k, rr, rz[k]) for k in range(N_RING)]
    inner = [(0.0, 0.0, 0.200)] + [pol(az, r, z) for az, r, z in ((-160, 0.50, 0.177), (-100, 0.47, 0.194), (-40, 0.52, 0.172),
                                                                  (20, 0.48, 0.193), (80, 0.51, 0.175), (140, 0.47, 0.192))]
    bottom = [pol(45 * j, rr / math.cos(math.radians(22.5)), SOIL_Z0) for j in range(8)]
    return rim, inner, bottom


# =====================================================================================================================
# planting layouts: (kind, x, y, D, seed[, H]) ; kinds alternate so that no two same colours touch
# =====================================================================================================================
REG = {
    'FLB-02': dict(name='FMS_Garden_Bed_Corner', coll='FLB-02_Bed_Corner', preview='FMS_Garden_FLB_02_Preview.png',
                   budget=(400, 2200), h_max=0.70, lilac_top=0.70,
                   clumps=[('yellow', -0.64, 0.38, 0.34, 41), ('pink', -0.43, 0.64, 0.38, 42),
                           ('white', -0.21, 0.37, 0.38, 43), ('pink', 0.03, 0.64, 0.40, 44),
                           ('white', 0.33, 0.33, 0.36, 45), ('lilac', 0.57, 0.57, 0.48, 46, 0.70),
                           ('pink', 0.64, 0.03, 0.40, 47), ('white', 0.37, -0.21, 0.38, 48),
                           ('pink', 0.64, -0.43, 0.38, 49), ('yellow', 0.38, -0.64, 0.34, 50)],
                   fillers=[(-0.72, 0.70, 0.24, 61), (-0.43, 0.27, 0.26, 62), (0.03, 0.28, 0.26, 63),
                            (0.28, 0.03, 0.26, 64), (0.27, -0.43, 0.26, 65), (0.62, -0.68, 0.24, 66)]),
    'FLB-03': dict(name='FMS_Garden_Bed_Round', coll='FLB-03_Bed_Round', preview='FMS_Garden_FLB_03_Preview.png',
                   budget=(400, 1800), h_max=0.80, lilac_top=0.80,
                   clumps=[('lilac', 0.0, 0.0, 0.46, 51, 0.80)] +
                          [(k, *pol(az, 0.37), 0.40, 52 + i, 0.92)
                           for i, (k, az) in enumerate((('pink', -120), ('white', -30), ('pink', 60), ('white', 150)))] +
                          [('yellow', *pol(az, 0.62), 0.38, 56 + i, 0.70) for i, az in enumerate((-75, 15, 105, 195))],
                   fillers=[(*pol(az, 0.56), 0.30, 66 + i, 0.64) for i, az in enumerate((-120, -30, 60, 150))]),
}
CFG = REG[ID]
NAME = CFG['name']
COLL = CFG['coll'] if LIVE else NAME
COLL_VAR = COLL + VAR
PREVIEW = CFG['preview']
BUDGET, BUDGET_VAR = CFG['budget']
H_MAX = CFG['h_max']
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)
TMP = 'TMP_' + ID.replace('-', '')


def footprint():
    return L_POLY if ID == 'FLB-02' else RING_POLY


def border_blocks():
    return blocks_L() if ID == 'FLB-02' else blocks_round()


# ============ helpers copied from PLT-01 / FLB-01 build.py (approved generator) ============
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
    """LEAF CLUSTER v2 (PLT-01): faceted domed foliage drop from a full ico sphere (sub 2 = 80 tris, sub 1 = 20 tris),
    re-profiled (widest ring at `widest` of the height, domed top, rounded underside), +-noise per vertex (fixed seed).
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
def block(P, cname, quad):
    """hewn stone block: closed prism on the ground from a CCW quad, flat light top (F-15), sides and bottom stone (F-14)"""
    bm = P.bm
    V = [bm.verts.new((x, y, z)) for z in (0.0, BH) for (x, y) in quad]
    f = [P.face([V[3], V[2], V[1], V[0]], STONE), P.face([V[4], V[5], V[6], V[7]], STONE_L)]
    for k in range(4):
        k1 = (k + 1) % 4
        f.append(P.face([V[k], V[k1], V[4 + k1], V[4 + k]], STONE))
    P.comp.append((cname, f, True))


def soil_mesh():
    """-> (points xyz, faces [index lists], top triangles [index triples]) of the closed soil solid"""
    if ID == 'FLB-02':
        rim, cidx, corners, inner = soil_L()
    else:
        rim, inner, bottom = soil_round()
    pts = list(rim) + list(inner); n = len(rim)
    res = delaunay_2d_cdt([Vector((x, y)) for x, y, _ in pts], [], [list(range(n))], 1, 1e-6)
    vco, _, faces, orig, _, _ = res
    assert len(vco) == len(pts), 'CDT inserted vertices'
    m = [orig[i][0] for i in range(len(vco))]
    top = [tuple(m[i] for i in f) for f in faces]
    allp = list(pts); fl = [list(t) for t in top]
    if ID == 'FLB-02':
        B = []
        for x, y in corners: B.append(len(allp)); allp.append((x, y, SOIL_Z0))
        for k in range(6):
            a, b = cidx[k], (cidx[(k + 1) % 6] if k < 5 else n)
            run = [i % n for i in range(a, b + 1)]
            fl.append(run + [B[(k + 1) % 6], B[k]])
        fl.append(list(reversed(B)))
    else:
        B = []
        for p in bottom: B.append(len(allp)); allp.append(p)
        for j in range(8):
            r0, r1, r2 = 2 * j, 2 * j + 1, (2 * j + 2) % n
            b0, b1 = B[j], B[(j + 1) % 8]
            fl += [[r0, r1, b0], [r1, r2, b1], [r1, b1, b0]]
        fl.append(list(reversed(B)))
    return allp, fl, top


def soil(P):
    allp, fl, _ = soil_mesh()
    V = [P.bm.verts.new(p) for p in allp]
    P.comp.append(('Soil', [P.face([V[i] for i in f], SOIL) for f in fl], False))


def soil_bvh():
    allp, _, top = soil_mesh()
    return BVHTree.FromPolygons([Vector(p) for p in allp], [list(t) for t in top])


def petal_rim(p, a, r, h, spin, notch_r=0.90, notch_dz=0.014):
    """8 rim points: petal tips (r, height h) alternating with notches (notch_r * r, h - notch_dz)"""
    rp, ra = ring(p + a * h, a, r, 8, spin); O = p + a * h
    return [O + (q - O) * (1.0 if k % 2 == 0 else notch_r) - (a * (0.0 if k % 2 == 0 else notch_dz))
            for k, q in enumerate(rp)], ra


def cup_bloom(P, p, a, spin, slots, depth=0.03, r=0.05, h=0.048, hc=0.022, rc=0.016):
    """8-sided cup bloom, ONE closed shell, 22 tris, D 0.10 x 0.048: buried apex -> petal rim (4 raised tips + 4 notches,
    outer petals) -> inside of the cup to a 4-sided centre (inner petals) -> flat centre (yellow)."""
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
    """small 8-sided yellow cup, ONE closed shell, 16 tris, D 0.084: buried apex -> petal rim -> sunken centre"""
    a = Vector(a).normalized(); p = Vector(p)
    A = P.bm.verts.new(p - a * depth); Cv = P.bm.verts.new(p + a * hc)
    R = [P.bm.verts.new(q) for q in petal_rim(p, a, r, h, spin, notch_dz=0.010)[0]]
    return [P.face([A, R[(k + 1) % 8], R[k]], slot) for k in range(8)] + \
           [P.face([R[k], R[(k + 1) % 8], Cv], slot) for k in range(8)]


def spike(P, base, a, L, spin, r=0.038, t_ring=0.28, depth=0.05, slot=LILAC):
    """lilac flower spike: 6-sided bipyramid, ONE closed shell, 12 tris; lower apex buried `depth` in the foliage,
    widest ring at t_ring of the visible length L, tip at base + a*L"""
    a = Vector(a).normalized(); base = Vector(base)
    lo = P.bm.verts.new(base - a * depth); hi = P.bm.verts.new(base + a * L)
    Rg = [P.bm.verts.new(q) for q in ring(base + a * (L * t_ring), a, r, 6, spin)[0]]
    return [P.face([lo, Rg[(k + 1) % 6], Rg[k]], slot) for k in range(6)] + \
           [P.face([Rg[k], Rg[(k + 1) % 6], hi], slot) for k in range(6)]


# ============ planting layout (computed once, emitted into any Part) ============
def plan_planting():
    """returns drops [(name, verts, faces, slots)] and flower primitives [(name, kind, args)].
    FLB-01 review: no brown stalks (no 'lollipops'); pink/white cups sit on the foliage, tilted ~10 deg more towards the
    viewer than FLB-01 (32-40 deg); low filler drops cover the bare soil at the front edges."""
    sb = soil_bvh(); drops = []; prims = []; warn = []
    down = Vector((0, 0, -1))
    def soil_z(x, y): return sb.ray_cast(Vector((x, y, 1.0)), down)[0].z
    def tilt_axis(dx, dy, deg):
        out = Vector((dx, dy, 0.0)); out = out.normalized() if out.length > 1e-6 else Vector((0, 0, 0))
        d = (TOWARD + out * 0.45).normalized(); ax = d.cross(Vector((0, 0, 1)))
        return Matrix.Rotation(math.radians(-deg), 3, ax.normalized()) @ Vector((0, 0, 1))
    for fi, fl in enumerate(CFG['fillers']):
        x, y, D, seed = fl[:4]; H = fl[4] if len(fl) > 4 else 0.70
        z0 = soil_z(x, y) - DROP_SINK * 0.7
        bm, slots = leaf_cluster(Vector((x, y, z0 + 0.5 * H * D)), D, seed, H=H, noise=0.012, sub=1)
        bm.verts.index_update()
        drops.append((f'Filler_{fi}', [v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces], slots))
        bm.free()
    for ci, cl in enumerate(CFG['clumps']):
        kind, x, y, D, seed = cl[:5]; H = cl[5] if len(cl) > 5 else 0.80
        z0 = soil_z(x, y) - DROP_SINK
        c = Vector((x, y, z0 + 0.5 * H * D))
        bm, slots = leaf_cluster(c, D, seed, H=H, noise=0.025)
        bvh = BVHTree.FromBMesh(bm)
        bm.verts.index_update()
        drops.append((f'Drop_{ci}{kind[0].upper()}', [v.co.copy() for v in bm.verts],
                      [[v.index for v in f.verts] for f in bm.faces], slots))
        bm.free()
        def hit(dx, dy): return bvh.ray_cast(Vector((x + dx, y + dy, 2.0)), down)[0]
        if kind in CUP_SLOTS:
            # 4 cups on the foliage: two on the viewer side, one on the back shoulder, one on the crown
            for bi, (dx, dy, tl) in enumerate(((-0.10, -0.07, 40), (0.07, -0.10, 38), (-0.04, 0.09, 30), (0.03, 0.0, 26))):
                k = D / 0.38; p = hit(dx * k, dy * k); a = tilt_axis(dx, dy, tl)
                prims.append((f'Bloom_{ci}{bi}', 'cup', (p, a, math.radians(20 * bi + 5 * ci), CUP_SLOTS[kind])))
                if not inside(bvh, p - a * 0.025): warn.append(f'bloom {ci}{bi} apex outside its drop')
        elif kind == 'yellow':
            offs = [(0.0, 0.0, 14)] + [(0.085 * math.cos(math.radians(az)), 0.085 * math.sin(math.radians(az)), 34)
                                        for az in (-115, -10, 120)]
            for bi, (dx, dy, tl) in enumerate(offs):
                p = hit(dx, dy); a = tilt_axis(dx, dy, tl)
                prims.append((f'Cup_{ci}{bi}', 'small', (p, a, math.radians(13 * bi))))
                if not inside(bvh, p - a * 0.02): warn.append(f'cup {ci}{bi} apex outside its drop')
        elif kind == 'lilac':
            top = CFG['lilac_top']
            n_ring = 8
            rr = 0.115 * D / 0.40
            offs = [(0.0, 0.0)] + [(rr * math.cos(math.radians(az)), rr * math.sin(math.radians(az)))
                                   for az in [-100 + 360 * k / n_ring for k in range(n_ring)]]
            for bi, (dx, dy) in enumerate(offs):
                p = hit(dx, dy)
                lean = Vector((dx * 1.8, dy * 1.8, 1.0)).normalized()
                tip_z = top - (0.0 if bi == 0 else (0.03, 0.08, 0.05)[bi % 3])
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
        else: f = spike(P, *args)
        P.comp.append((nm, f, False))


# ============ parts (objects) ============
# base: one mesh. _Planted: role-based parts so make_lod1.py halves only the planting (border parts of 4 blocks =
# 48 tris and the soil <= 60 tris stay below its 60-tri threshold and keep their exact LOD0 shape -> snap holds in LOD1).
def planted_border_groups():
    names = [n for n, _ in border_blocks()]
    if ID == 'FLB-02':
        g = {'Border_Back': 'Block_B', 'Border_Right': 'Block_R', 'Border_FrontInner': ('Block_F', 'Block_X'),
             'Border_LeftInner': ('Block_Y', 'Block_W')}
        return {k: (lambda n, v=v: n.startswith(v)) for k, v in g.items()}
    return {f'Border_Q{q}': (lambda n, q=q: int(n[-2:]) // 4 == q) for q in range(4)}


def gen_bed(P, pick=lambda n: True, with_soil=True):
    for nm, quad in border_blocks():
        if pick(nm): block(P, nm, quad)
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
    me = bpy.data.meshes.new(TMP + '_cop'); bm = bmesh.new()
    for o in objs:
        if o.type != 'MESH': continue
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        tm = bpy.data.meshes.new(TMP + '_part'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(TMP + '_cop', me)
    n, s = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def poly_side(poly, p):
    """signed distance-ish: (+d) inside by d, (-d) outside by d (even-odd test + distance to the boundary)"""
    x, y = p; ins = False; n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0): ins = not ins
    d = min(seg_dist(p, poly[i], poly[(i + 1) % n]) for i in range(n))
    return d if ins else -d


def xf(pts2, rot_deg=0, off=(0, 0)):
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    return [(c * x - s * y + off[0], s * x + c * y + off[1]) for x, y in pts2]


def flb01_points():
    """vertices of the approved FLB-01 base (linked read-only from its .blend, the library is removed afterwards)"""
    if not os.path.isfile(FLB01_BLEND): return None
    libs0 = set(bpy.data.libraries)
    with bpy.data.libraries.load(FLB01_BLEND, link=True) as (src, dst):
        dst.meshes = [n for n in src.meshes if n == 'FMS_Garden_Bed_Straight_Body']
    me = dst.meshes[0]
    pts = [(v.co.x, v.co.y, v.co.z) for v in me.vertices]
    for lib in set(bpy.data.libraries) - libs0: bpy.data.libraries.remove(lib)
    return pts


def snap_checks(base_objs, var_objs, var_plants):
    """SNAP contract: footprint on the 1.0 grid, border top 0.25, soil 0.20, neighbouring beds touch without overlap,
    plants inside the footprint (margin 0.02) and below the height limit"""
    tol = 0.001; ok_all = True; fp = footprint()
    def say(ok, msg):
        nonlocal ok_all; ok_all &= ok; print(('  SNAP OK   ' if ok else '  SNAP FAIL ') + msg)
    base3 = world_pts(base_objs); base2 = [(p.x, p.y) for p in base3]
    for label, objs in (('base', base_objs), ('planted', var_objs)):
        lo, hi = bbox(objs)
        say(all(abs(abs(v) - 1.0) <= tol for v in (lo[0], hi[0], lo[1], hi[1])) and abs(lo[2]) <= 1e-6,
            f'{label}: footprint bbox x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} min z {lo[2]:.4f}')
        pts2 = [(p.x, p.y) for p in world_pts(objs)]
        worst = min(poly_side(fp, p) for p in pts2)
        say(worst >= -tol, f'{label}: all vertices inside the footprint polygon (worst {worst:+.4f})'
            + (' - missing quadrant x<0,y<0 empty' if ID == 'FLB-02' else ''))
    # outer faces / vertices exactly on the footprint
    if ID == 'FLB-02':
        for i in range(6):
            a, b = fp[i], fp[(i + 1) % 6]
            cov = sum(1 for nm, quad in border_blocks()
                      for k in range(4) if seg_dist(quad[k], a, b) < 1e-9 and seg_dist(quad[(k + 1) % 4], a, b) < 1e-9)
            say(cov >= 2, f'outline edge {a}->{b}: {cov} block faces exactly on it')
    else:
        rs = sorted(round(math.hypot(x, y), 6) for nm, q in border_blocks() for x, y in q[:2])
        say(abs(rs[0] - 1.0) < 1e-6 and abs(rs[-1] - 1.0) < 1e-6, f'16 outer vertices on R {rs[0]:.4f}..{rs[-1]:.4f}')
    # pairs (2D footprints: no vertex strictly inside the other bed, contact within tol)
    def pair(label, ptsA, polyA, ptsB, polyB):
        inB = max(poly_side(polyB, p) for p in ptsA); inA = max(poly_side(polyA, p) for p in ptsB)
        touch = sum(1 for p in ptsA if abs(poly_side(polyB, p)) <= tol)
        say(inB <= tol and inA <= tol and touch >= 1,
            f'{label}: max penetration {max(inA, inB):+.4f} (<= 0.001), touching vertices {touch}')
    rect01 = [(-1.0, -0.5), (1.0, -0.5), (1.0, 0.5), (-1.0, 0.5)]
    f01 = flb01_points()
    f01_2 = [(x, y) for x, y, z in f01] if f01 else None
    if f01_2 is None: say(False, 'FLB-01 blend not found: ' + FLB01_BLEND)
    if ID == 'FLB-02':
        if f01_2:
            say(abs(max(z for _, _, z in f01) - BH) < 1e-6, f'FLB-01 border top {max(z for _, _, z in f01):.4f} = FLB-02 border top {BH}')
            pair('FLB-02 | FLB-01 at the back-arm end (FLB-01 at x -2.0, y +0.5)',
                 base2, fp, xf(f01_2, 0, (-2.0, 0.5)), xf(rect01, 0, (-2.0, 0.5)))
            pair('FLB-02 | FLB-01 turned 90 deg at the right-arm end (at x +0.5, y -2.0)',
                 base2, fp, xf(f01_2, 90, (0.5, -2.0)), xf(rect01, 90, (0.5, -2.0)))
            pair('FLB-02 | FLB-01 along the back (FLB-01 at x 0, y +1.5)',
                 base2, fp, xf(f01_2, 0, (0.0, 1.5)), xf(rect01, 0, (0.0, 1.5)))
        pair('FLB-02 | FLB-02 along X (+2.0)', base2, fp, xf(base2, 0, (2.0, 0)), xf(fp, 0, (2.0, 0)))
        pair('FLB-02 | FLB-02 along Y (+2.0)', base2, fp, xf(base2, 0, (0, 2.0)), xf(fp, 0, (0, 2.0)))
    else:
        if f01_2:
            pair('FLB-03 | FLB-01 tangent (FLB-01 at x +2.0)', base2, fp, xf(f01_2, 0, (2.0, 0)), xf(rect01, 0, (2.0, 0)))
        pair('FLB-03 | FLB-03 along X (+2.0)', base2, fp, xf(base2, 0, (2.0, 0)), xf(fp, 0, (2.0, 0)))
        pair('FLB-03 | FLB-03 along Y (+2.0)', base2, fp, xf(base2, 0, (0, 2.0)), xf(fp, 0, (0, 2.0)))
    lo_b, hi_b = bbox(base_objs)
    say(abs(hi_b[2] - BH) <= tol, f'border top {hi_b[2]:.4f} (contract 0.25)')
    sz = max(p[2] for p in soil_mesh()[0])
    say(abs(sz - SOIL_CROWN) <= tol, f'soil crown {sz:.3f} (contract 0.20, below the border top)')
    pp = world_pts(var_plants)
    m = min(poly_side(fp, (p.x, p.y)) for p in pp); top = max(p.z for p in pp)
    say(m >= PLANT_MARGIN - 1e-6 and top <= H_MAX + tol,
        f'planting top {top:.3f} (<= {H_MAX}) | margin to the outer faces {m:.3f} (>= 0.02)')
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
    print('CHECK base (blocks + soil):')
    Pc = Part('Base'); gen_bed(Pc); pt_base = part_tris(Pc)
    Pc.bm.normal_update(); bmesh.ops.recalc_face_normals(Pc.bm, faces=Pc.bm.faces)
    cb = pc.comp_checks(Pc, mirror_skip=tuple(n for n, _, _ in Pc.comp)); Pc.bm.free()
    print('CHECK planted (blocks + soil + planting):')
    Pc = Part('Planted'); gen_bed(Pc); emit_drops(Pc, drops); emit_flowers(Pc, prims); pt_var = part_tris(Pc)
    bmesh.ops.recalc_face_normals(Pc.bm, faces=Pc.bm.faces)
    cv_ = pc.comp_checks(Pc, mirror_skip=tuple(n for n, _, _ in Pc.comp)); Pc.bm.free()
    pvb = plants_vs_border(drops, prims)
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = Part('Body'); gen_bed(P); ob = to_obj(P, NAME + '_Body', coll, mat, root)
    vroot = bpy.data.objects.new(NAME + VAR, None); cv.objects.link(vroot)
    vobs = {}
    for pn, pick in planted_border_groups().items():
        P = Part(pn); gen_bed(P, pick, with_soil=False); vobs[pn] = to_obj(P, f'{NAME}{VAR}_{pn}', cv, mat, vroot)
    P = Part('Soil'); soil(P); vobs['Soil'] = to_obj(P, f'{NAME}{VAR}_Soil', cv, mat, vroot)
    P = Part('Foliage'); emit_drops(P, drops); vobs['Foliage'] = to_obj(P, f'{NAME}{VAR}_Foliage', cv, mat, vroot)
    P = Part('Flowers'); emit_flowers(P, prims); vobs['Flowers'] = to_obj(P, f'{NAME}{VAR}_Flowers', cv, mat, vroot)
    bpy.context.view_layer.update()
    print('REPORT base:'); tot = pc.report({'Body': ob})
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}', '| parts', pt_base)
    print('REPORT planted:'); tot_v = pc.report(vobs)
    print(f'  budget {BUDGET_VAR} ->', 'OK' if tot_v <= BUDGET_VAR else f'x{tot_v / BUDGET_VAR:.2f}', '| parts', pt_var)
    print('  flowers:', {k: sum(1 for _, kk, _ in prims if kk == k) for k in ('cup', 'small', 'spike')},
          'drops', sum(1 for d in drops if d[0].startswith('Drop')), 'fillers', sum(1 for d in drops if d[0].startswith('Filler')))
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


# ---------------- renders (temporary scene: the open scene and its settings are not touched; copied from FLB-01) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new(TMP + '_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new(TMP + '_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new(TMP + '_World'); w.use_nodes = True; nt = w.node_tree
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
    sun(TMP + '_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun(TMP + '_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new(TMP + '_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new(TMP + '_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


# reference: front-left 3/4 (missing quadrant of the L towards the camera), ~30 deg above, near-orthographic
VIEW_REF = (-0.62, -1.0, 0.95) if ID == 'FLB-02' else (-0.10, -1.0, 0.62)
VIEW_PREVIEW = (-0.55, -1.0, 0.68)            # series preview 3/4 (~30 deg), same as FLB-01

if MODE == 'verify':
    for suf in ('', VAR): pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    coll, cv, root, ob, vroot, vobs, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    base_objs = [root, ob]; var_objs = [vroot] + list(vobs.values())
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.84, fill_h=0.84, lens=None)
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_34_{tag}.png'), VIEW_PREVIEW)
        render(var_objs, os.path.join(CHECK_DIR, f'{ID}P_34_{tag}.png'), VIEW_PREVIEW)
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
        render(var_objs, os.path.join(CHECK_DIR, f'{ID}P_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_keep_selection(NAME, coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        fbx_v = export_keep_selection(NAME + VAR, cv, vroot, os.path.join(ART, 'Meshes', NAME + VAR + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        save_lib(os.path.join(ART, 'Blend', NAME + VAR + '.blend'), cv, mat, img)
        render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        if not LIVE:
            render(var_objs, os.path.join(CHECK_DIR, f'{ID}_Planted_check.png'), VIEW_PREVIEW)
        pc.verify(fbx); pc.verify(fbx_v)
    if MODE in ('export', 'dump'):
        geom_dump([ob] + list(vobs.values()), os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
