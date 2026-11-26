# build.py - MOD-03 Low stone wall 2 m (FMS_Garden_Wall_Stone) + MOD-04 Wall pillar with ball (FMS_Garden_Wall_Pillar),
# pack AssetNew (Cottage Garden Decor), atlas A Garden_Build (read only).
# One registry script for both modules (form of Tools/blender/build_registry_template.py).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- MOD-03|MOD-04 build|export|verify|dump
#   build  = build the model + printed checks (topology, coplanar, ground, tris, SNAP MOD-03 <-> MOD-04)
#            + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify = only re-import the FBX in art/
#   dump   = build + geometry dump only (live/headless comparison)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\MOD-03+MOD-04_Wall\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['MOD-03', 'build']})
#   Live mode touches only the collection MOD-03_Wall_Stone / MOD-04_Wall_Pillar.
# Axes (Blender): Z = up (Unity Y). FBX export -Z forward, Y up: Blender (x, y, z) -> Unity (-x, z, -y).
#   MOD-03: Blender X = wall length (-1.0 .. 1.0), Y = thickness (blocks +-0.20, coping +-0.22), Z = height (0 .. 0.60).
#   MOD-04: square +-0.25 in X/Y, Z 0 .. 1.05. Both pivots = centre of the base (0, 0, 0).
# Stone wording/cells as WTR-03 and the FLB-01 kerb: A-12 Stone #A7A39A = main masonry, A-11 Stone light #C9C3B6 =
# limestone (coping, cap, ball) and the second-tone blocks (about one in four).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_TEX_PATH = os.environ.get('PACK_ATLAS') or os.path.join(REPO, 'art', 'AssetNew', 'Textures', ATLAS_TEX)
ATLAS_MAT = 'M_Garden_Build'
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
LIME, STONE = 11, 12                         # A-11 Stone light (limestone), A-12 Stone
G = 0.012                                    # joint width (horizontal and vertical), groove depth 0.01 to the core
# MOD-03 wall (snap contract: length 2.0, thickness 0.40, coping 0.44 x 0.06, top 0.60)
W_HALF, W_BLOCK, W_CORE, W_IN = 1.0, 0.20, 0.19, G / 2    # half length, block face, core face, block inner face (12 mm middle joint on the ends)
W_COPE_Y, W_COPE_Z0, W_TOP, W_BEV = 0.22, 0.54, 0.60, 0.015
W_COURSE = [0.0, 0.135, 0.27, 0.405, 0.54]                 # 4 courses of 0.135
W_TOP_BLOCK = 0.54 - G / 2                   # top course: a half joint (6 mm mortar bed) under the coping
W_CORE_Z = (0.003, 0.55)                     # core: bottom above the ground (blocks own z 0), top inside the coping
W_CORE_X = 0.998                             # core ends 2 mm inside the flat cut (block ends own x +-1.0)
# vertical joint centre lines per course (x), bottom -> top: 5/4 blocks alternating (0.35-0.60, reference ~0.4),
# joints of neighbouring courses >= 0.18 apart, no joint within 0.1 of x = +-0.75 (pillar faces in an assembly)
W_FRONT = [[-0.62, -0.20, 0.25, 0.60], [-0.42, 0.04, 0.43], [-0.65, -0.20, 0.22, 0.63], [-0.43, 0.01, 0.42]]
W_BACK = [[-0.40, 0.00, 0.45], [-0.62, -0.20, 0.22, 0.65], [-0.42, 0.02, 0.44], [-0.63, -0.20, 0.23, 0.64]]
W_FRONT_LIGHT = {(0, 1), (1, 3), (2, 2), (3, 3)}           # (course, block) in the second tone, 4 of 18 per side
W_BACK_LIGHT = {(0, 1), (1, 4), (2, 0), (3, 2)}
# MOD-04 pillar (snap contract: 0.50 x 0.50 x 0.80 + ball up to 1.05)
P_HALF, P_CORE = 0.25, 0.24
P_COURSE = [0.0, 0.74 / 3, 2 * 0.74 / 3, 0.74]             # 3 courses
P_TOP_BLOCK = 0.74 - G / 2                   # top course: a half joint (6 mm mortar bed) under the cap (a 2 mm slit aliased)
P_CORE_Z = (0.004, 0.75)                     # 0.004: not in the wall core bottom plane (0.003) in an assembly
P_LONG = 0.29                                # pinwheel block: long face 0.29, end 0.198 (0.29 + 0.012 + 0.198 = 0.50)
P_CAP = (0.74, 0.80, 0.015)                  # cap z0, z1, top bevel
BALL_R, BALL_SINK = 0.125, 0.0005            # icosphere 80 tris, sits 0.5 mm into the cap (<= 1 mm), top 1.0495
P_LIGHT = {(0, 'R'), (1, 'L'), (2, 'R'), (2, 'L')}   # pinwheel blocks in the second tone (4 of 12), as the reference:
                                             # bottom/top right face light, middle short piece on the front face light
GRID = 2.0
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'MOD-03'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'


# ---------------- geometry (V = [(x, y, z)], F = [(vertex indices, slot, component)]) ----------------
class Geo:
    def __init__(self): self.V, self.F = [], []
    def add(self, p): self.V.append(tuple(float(c) for c in p)); return len(self.V) - 1
    def box(self, comp, x0, x1, y0, y1, z0, z1, slot):
        i = [self.add((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        for q in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
            self.F.append(([i[k] for k in q], slot, comp))
    def prism_x(self, comp, x0, x1, prof, slot):
        """closed prism along X from a convex YZ profile"""
        a = [self.add((x0, y, z)) for y, z in prof]; b = [self.add((x1, y, z)) for y, z in prof]; n = len(prof)
        for k in range(n): self.F.append(([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]], slot, comp))
        self.F.append((list(reversed(a)), slot, comp)); self.F.append((list(b), slot, comp))
    def loft_z(self, comp, rings, slot):
        """closed vertical loft of square rings [(z, half)]"""
        R = [[self.add((sx * h, sy * h, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))] for z, h in rings]
        for j in range(len(R) - 1):
            for k in range(4): self.F.append(([R[j][k], R[j][(k + 1) % 4], R[j + 1][(k + 1) % 4], R[j + 1][k]], slot, comp))
        self.F.append((list(reversed(R[0])), slot, comp)); self.F.append((list(R[-1]), slot, comp))


def geo_wall():
    g = Geo(); blocks = []
    g.box('Core', -W_CORE_X, W_CORE_X, -W_CORE, W_CORE, W_CORE_Z[0], W_CORE_Z[1], STONE)
    for side, pattern, light, (y0, y1) in (('F', W_FRONT, W_FRONT_LIGHT, (-W_BLOCK, -W_IN)),
                                          ('B', W_BACK, W_BACK_LIGHT, (W_IN, W_BLOCK))):
        for c, joints in enumerate(pattern):
            z0 = W_COURSE[c] + (G / 2 if c else 0.0)
            z1 = W_COURSE[c + 1] - G / 2 if c < len(pattern) - 1 else W_TOP_BLOCK
            xs = [-W_HALF] + [v for j in joints for v in (j - G / 2, j + G / 2)] + [W_HALF]
            for b in range(len(joints) + 1):
                x0, x1 = xs[2 * b], xs[2 * b + 1]
                slot = LIME if (c, b) in light else STONE
                cn = f'Block_{side}{c}_{b}'; g.box(cn, x0, x1, y0, y1, z0, z1, slot); blocks.append((cn, x1 - x0, slot))
    by, bz = W_COPE_Y - W_BEV, W_TOP - W_BEV
    prof = [(-W_COPE_Y, W_COPE_Z0), (W_COPE_Y, W_COPE_Z0), (W_COPE_Y, bz), (by, W_TOP), (-by, W_TOP), (-W_COPE_Y, bz)]
    g.prism_x('Coping', -W_HALF, W_HALF, prof, LIME)
    return g.V, g.F, blocks


def pinwheel(cw):
    """4 blocks around the shaft, each 0.29 along its face x 0.198 deep; the next block's end shows on the same face"""
    S, a, b = P_HALF, P_LONG, 2 * P_HALF - P_LONG - G
    R = {'F': (-S, -S + a, -S, -S + b), 'R': (S - b, S, -S, -S + a),
         'B': (S - a, S, S - b, S), 'L': (-S, -S + b, S - a, S)}     # x0, x1, y0, y1 (clockwise seen from below = CCW from top)
    if not cw:                                                      # mirror in X for the next course (staggered joints)
        R = {('L' if k == 'R' else 'R' if k == 'L' else k): (-x1, -x0, y0, y1) for k, (x0, x1, y0, y1) in R.items()}
    return R


def ico_ball(r, zc):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=Matrix.Identity(4), calc_uvs=False)
    vs = [v.co.copy() for v in bm.verts]; k = r / max(v.length for v in vs)
    V = [(v.x * k, v.y * k, v.z * k + zc) for v in vs]
    bm.verts.index_update(); F = [[v.index for v in f.verts] for f in bm.faces]; bm.free()
    return V, F


def geo_pillar():
    g = Geo(); blocks = []
    g.box('Core', -P_CORE, P_CORE, -P_CORE, P_CORE, P_CORE_Z[0], P_CORE_Z[1], STONE)
    for c in range(3):
        z0 = P_COURSE[c] + (G / 2 if c else 0.0)
        z1 = P_COURSE[c + 1] - G / 2 if c < 2 else P_TOP_BLOCK
        for k, (x0, x1, y0, y1) in sorted(pinwheel(c % 2 == 0).items()):
            slot = LIME if (c, k) in P_LIGHT else STONE
            cn = f'Block_{c}{k}'; g.box(cn, x0, x1, y0, y1, z0, z1, slot); blocks.append((cn, max(x1 - x0, y1 - y0), slot))
    z0, z1, bev = P_CAP
    g.loft_z('Cap', [(z0, P_HALF), (z1 - bev, P_HALF), (z1, P_HALF - bev)], LIME)
    BV, BF = ico_ball(BALL_R, z1 + BALL_R - BALL_SINK)
    o = len(g.V); g.V += BV
    for f in BF: g.F.append(([o + i for i in f], LIME, 'Ball'))
    return g.V, g.F, blocks


def to_part(V, F, name='Body'):
    P = Part(name); bm = P.bm
    vs = [bm.verts.new(Vector(p)) for p in V]; comp = {}
    for idx, sl, cn in F: comp.setdefault(cn, []).append(P.face([vs[i] for i in idx], sl))
    for cn, fs in comp.items():
        P.comp.append((cn, fs, min(v.co.z for f in fs for v in f.verts) < 1e-9))
    return P


def planarity(V, F):
    worst = 0.0
    for idx, _, _ in F:
        if len(idx) < 4: continue
        p = [Vector(V[i]) for i in idx]; n = (p[1] - p[0]).cross(p[2] - p[0]).normalized()
        worst = max(worst, max(abs((q - p[0]).dot(n)) for q in p))
    return worst


# ---------------- SNAP (contract: CATALOG «Модули и стыковка» item 2, grid 2.0 m) ----------------
def xform(V, rot_deg, t):
    M = Matrix.Translation(Vector(t)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
    return [tuple(M @ Vector(p)) for p in V]


def bbox(V): return [min(p[j] for p in V) for j in range(3)], [max(p[j] for p in V) for j in range(3)]


def outward_faces(V, F, tag):
    """faces as (tag, comp, pts, outward unit normal, plane d); every component is a convex closed shell"""
    cen = {}
    for idx, _, cn in F:
        for i in idx: cen.setdefault(cn, []).append(Vector(V[i]))
    cen = {k: sum(v, Vector()) / len(v) for k, v in cen.items()}
    out = []
    for idx, _, cn in F:
        p = [Vector(V[i]) for i in idx]; n = (p[1] - p[0]).cross(p[2] - p[0])
        if n.length < 1e-12: continue
        n.normalize(); c = sum(p, Vector()) / len(p)
        if n.dot(c - cen[cn]) < 0: n = -n
        out.append((tag, cn, p, n, n.dot(p[0])))
    return out


def poly_overlap_area(P, Q, n):
    """area of the intersection of two convex coplanar polygons (Sutherland-Hodgman in the plane)"""
    u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized(); w = n.cross(u)
    to2 = lambda pts: [(p.dot(u), p.dot(w)) for p in pts]
    def ccw(pts):
        a = sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))
        return pts if a < 0 else pts[::-1]
    subj, clip = ccw(to2(P)), ccw(to2(Q))
    def inside(p, a, b): return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-12   # left of a->b (CCW)
    def inter(p, q, a, b):
        x1, y1, x2, y2, x3, y3, x4, y4 = *p, *q, *a, *b
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-15: return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    outp = subj
    for i in range(len(clip)):
        a, b = clip[i - 1], clip[i]; inp = outp; outp = []
        if not inp: break
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q, a, b):
                if not inside(p, a, b): outp.append(inter(p, q, a, b))
                outp.append(q)
            elif inside(p, a, b): outp.append(inter(p, q, a, b))
    if len(outp) < 3: return 0.0
    return abs(sum(outp[i][0] * outp[i - 1][1] - outp[i - 1][0] * outp[i][1] for i in range(len(outp)))) / 2


def cross_coplanar(A, B):
    """coplanar overlapping face pairs between two placed pieces: same-facing (z-fight), back-to-back contact, ground"""
    res = dict(zfight=[], contact=[], ground=[])
    for (_, ca, pa, na, da) in A:
        for (_, cb, pb, nb, db) in B:
            dot = na.dot(nb)
            if abs(abs(dot) - 1) > 1e-6 or abs(da - db * (1 if dot > 0 else -1)) > 1e-4: continue
            ar = poly_overlap_area(pa, pb, na)
            if ar <= 1e-8: continue
            if dot > 0 and na.z < -0.999 and abs(pa[0].z) < 1e-9: res['ground'].append((ca, cb, ar))
            elif dot > 0: res['zfight'].append((ca, cb, round(ar, 6)))
            else: res['contact'].append((ca, cb, round(ar, 6)))
    return res


def snap_check():
    ok = True
    def row(nm, good, txt=''):
        nonlocal ok; ok &= bool(good); print(f'  SNAP {nm}: {txt} {"OK" if good else "FAIL"}')
    Vw, Fw, _ = geo_wall(); Vp, Fp, _ = geo_pillar()
    # MOD-03 alone
    lo, hi = bbox(Vw)
    row('MOD-03 bbox', all(abs(a - b) < 1e-6 for a, b in zip(lo + hi, [-1, -W_COPE_Y, 0, 1, W_COPE_Y, W_TOP])),
        f'x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f} (want +-1.0, +-0.22, 0..0.60)')
    yb = max(abs(p[1]) for idx, _, cn in Fw if cn.startswith('Block') for p in [Vw[i] for i in idx])
    row('MOD-03 thickness (block faces)', abs(yb - W_BLOCK) < 1e-9, f'{2 * yb:.3f} (want 0.40); coping {2 * W_COPE_Y:.2f} x {W_TOP - W_COPE_Z0:.2f}')
    endA = [p for p in Vw if abs(p[0] + 1) < 1e-9]; endB = [p for p in Vw if abs(p[0] - 1) < 1e-9]
    beyond = [p for p in Vw if abs(p[0]) > 1 + 1e-9]
    row('MOD-03 flat cut at x = +-1.0 (nothing beyond)', not beyond and endA and endB,
        f'{len(endA)} / {len(endB)} verts on the end planes')
    W2 = xform(Vw, 0, (GRID, 0, 0)); lo2, _ = bbox(W2)
    row('MOD-03 <-> MOD-03 butt (+2.0)', abs(lo2[0] - hi[0]) < 1e-9, f'gap {(lo2[0] - hi[0]) * 1000:.3f} mm')
    secA = {(round(p[1], 6), round(p[2], 6)) for p in endA if not (abs(p[1]) < W_IN - 1e-9)}
    secB = {(round(p[1], 6), round(p[2], 6)) for p in endB if not (abs(p[1]) < W_IN - 1e-9)}
    cope = lambda S: {q for q in S if q[1] >= W_COPE_Z0 - 1e-9}
    row('MOD-03 coping sections equal at both ends (no notch)', cope(secA) == cope(secB), f'{len(cope(secA))} verts')
    fw = outward_faces(Vw, Fw, 'W'); fw2 = outward_faces(W2, Fw, 'W2')
    r = cross_coplanar(fw, fw2)
    row('MOD-03 <-> MOD-03 no same-facing coplanar faces', not r['zfight'],
        f'z-fight {len(r["zfight"])}, back-to-back butt contacts {len(r["contact"])} (hidden in the joint)')
    # MOD-04 alone
    lo, hi = bbox(Vp)
    shaft = [Vp[i] for idx, _, cn in Fp if cn.startswith('Block') or cn == 'Cap' for i in idx]
    slo, shi = bbox(shaft)
    row('MOD-04 shaft + cap footprint +-0.25', all(abs(abs(v) - P_HALF) < 1e-9 for v in slo[:2] + shi[:2]),
        f'x {slo[0]:.3f}..{shi[0]:.3f} y {slo[1]:.3f}..{shi[1]:.3f}; cap top {P_CAP[1]:.2f}')
    ball = [Vp[i] for idx, _, cn in Fp if cn == 'Ball' for i in idx]; blo, bhi = bbox(ball)
    row('MOD-04 ball on the cap', 0 <= P_CAP[1] - blo[2] <= 0.001 + 1e-9,
        f'ball {bhi[0] - blo[0]:.3f} x {bhi[1] - blo[1]:.3f} x {bhi[2] - blo[2]:.3f}, sink {(P_CAP[1] - blo[2]) * 1000:.1f} mm, top {bhi[2]:.4f}')
    row('MOD-04 bbox', abs(lo[2]) < 1e-9 and abs(hi[2] - 1.05) <= 0.001 and abs(hi[0] - P_HALF) < 1e-9,
        f'{hi[0] - lo[0]:.3f} x {hi[1] - lo[1]:.3f} x {hi[2] - lo[2]:.4f} (want 0.50 x 0.50 x 1.05 +-1 mm)')
    fp = outward_faces(Vp, Fp, 'P')
    # MOD-03 <-> MOD-04 assemblies (pillars at nodes, walls at node + 1.0)
    def wall_at(rot, t): return outward_faces(xform(Vw, rot, t), Fw, f'W{rot}{t}'), xform(Vw, rot, t)
    fA, VA = wall_at(0, (1.0, 0, 0))
    loA, hiA = bbox(VA)
    row('free end: wall end on the pillar node, inside the pillar', abs(loA[0]) < 1e-9 and loA[0] < P_HALF,
        f'wall x {loA[0]:.3f}..{hiA[0]:.3f}, pillar x +-{P_HALF}; wall end {P_HALF * 1000:.0f} mm inside')
    planes_w = {round(abs(p[1]), 6) for p in VA}; planes_p = {round(abs(p[1]), 6) for p in Vp if abs(p[1]) > 0.2}
    row('pillar faces vs wall faces do not coincide', P_HALF not in planes_w and not ({W_BLOCK, W_COPE_Y} & planes_p),
        f'pillar +-{P_HALF} vs wall +-{W_BLOCK} / +-{W_COPE_Y}')
    row('wall top under the pillar cap', W_TOP < P_CAP[0], f'wall top {W_TOP} vs cap underside {P_CAP[0]} (gap {P_CAP[0] - W_TOP:.2f})')
    r = cross_coplanar(fA, fp)
    row('wall | pillar no same-facing coplanar faces', not r['zfight'],
        f'z-fight {len(r["zfight"])} {r["zfight"][:3]}, contacts {len(r["contact"])}, ground-only (hidden) {len(r["ground"])}')
    # corner: second wall rotated 90 deg along +Y from the same node
    fC, VC = wall_at(90, (0, 1.0, 0))
    def cope_rect(V):
        c = [p for p in V if p[2] >= W_COPE_Z0 - 1e-9]; l, h = bbox(c); return l, h
    la, ha = cope_rect(VA); lc, hc = cope_rect(VC)
    ox = (max(la[0], lc[0]), min(ha[0], hc[0])); oy = (max(la[1], lc[1]), min(ha[1], hc[1]))
    inside = all(abs(v) <= P_HALF for v in ox + oy)
    row('corner: coping overlap inside the pillar', inside,
        f'overlap x {ox[0]:.2f}..{ox[1]:.2f} y {oy[0]:.2f}..{oy[1]:.2f} ({ox[1] - ox[0]:.2f} x {oy[1] - oy[0]:.2f}) within +-{P_HALF}')
    r = cross_coplanar(fC, fp)
    row('corner wall | pillar no same-facing coplanar faces', not r['zfight'], f'z-fight {len(r["zfight"])}, ground-only {len(r["ground"])}')
    # straight joint through a pillar and a doorway between two pillars
    fD, VD = wall_at(0, (-1.0, 0, 0))
    r = cross_coplanar(fA, fD)
    row('straight joint at a pillar (wall | wall)', not r['zfight'] and abs(bbox(VD)[1][0] - bbox(VA)[0][0]) < 1e-9,
        f'butt gap 0, z-fight {len(r["zfight"])}, back-to-back {len(r["contact"])}')
    clear = GRID - 2 * P_HALF
    row('doorway = skipped segment between two pillars', abs(clear - 1.5) < 1e-9 and clear >= 1.4, f'clear width {clear:.2f} (STR-02 1.4 fits)')
    print(f'  WTR-02 against the wall: stele back face at {W_COPE_Y:.2f} from the wall axis (coping overhang)')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


# ---------------- registry ----------------
REG = {
    'MOD-03': dict(name='FMS_Garden_Wall_Stone', coll='MOD-03_Wall_Stone', preview='FMS_Garden_MOD_03_Preview.png',
                   budget=600, geo=geo_wall,
                   view_ref=(-0.42, -1.0, 0.55), view_prev=(-0.50, -1.0, 0.60)),
    'MOD-04': dict(name='FMS_Garden_Wall_Pillar', coll='MOD-04_Wall_Pillar', preview='FMS_Garden_MOD_04_Preview.png',
                   budget=300, geo=geo_pillar,
                   view_ref=(0.62, -1.0, 0.80), view_prev=(0.62, -1.0, 0.75)),
}
CFG = REG[ID]; NAME = CFG['name']; COLL = CFG['coll']
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)


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
    if img is None: img = bpy.data.images.load(ATLAS_TEX_PATH, check_existing=True)
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


def cell_of(uv): return int((1 - uv[1]) * 4) * 4 + int(uv[0] * 4)


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    V, F, blocks = CFG['geo']()
    tris = {}
    for idx, _, c in F:
        key = 'Blocks' if c.startswith('Block') else c
        tris[key] = tris.get(key, 0) + len(idx) - 2
    print(f'== {ID} {NAME}: max face non-planarity {planarity(V, F) * 1000:.4f} mm')
    lens_ = sorted(round(b[1], 3) for b in blocks)
    print(f'  blocks {len(blocks)} ({sum(1 for b in blocks if b[2] == LIME)} second tone A-11, '
          f'{sum(1 for b in blocks if b[2] == STONE)} A-12); face lengths {lens_[0]}..{lens_[-1]}')
    skip = tuple(b[0] for b in blocks) + (('Ball',) if ID == 'MOD-04' else ())
    ob = pc.to_object(to_part(V, F), NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    bpy.context.view_layer.update()
    tot = pc.report({'Body': ob})
    print('  tris per part:', tris)
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'OVER x{tot / CFG["budget"]:.2f}')
    pc.coplanar_overlaps(ob)
    slots = sorted({cell_of(ob.data.uv_layers.active.data[p.loop_start].uv) for p in ob.data.polygons})
    zmin = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    print('  atlas cells used', slots, '| smooth faces', sum(p.use_smooth for p in ob.data.polygons),
          '| materials', [m.name for m in ob.data.materials], f'| min z {zmin:.4f} (bottom course blocks on z 0)')
    snap_check()
    return coll, root, ob, img, mat, tot


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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.70, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    laz = CFG.get('light_az', 0.0)
    from bpy_extras.object_utils import world_to_camera_view
    tg = 'TMP_' + ID.replace('-', '')
    sc = bpy.data.scenes.new(tg + '_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new(tg + '_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new(tg + '_World'); w.use_nodes = True; nt = w.node_tree
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
    sun(tg + '_Sun', (40, 0, -35 + laz), 3.2, (1, 0.96, 0.88))
    sun(tg + '_Fill', (65, 0, 150 + laz), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new(tg + '_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new(tg + '_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    dv = Vector(view_dir).normalized()
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


def assembly_render(out, mat):
    """check render only: pillar | wall | pillar | wall | corner pillar + corner wall, temporary objects"""
    made = []
    def mk(nm, V, F, rot, t):
        P = to_part(xform(V, rot, t), F, nm); bm = P.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        uvl = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = pc.cell_uv(f[P.slot])
        me = bpy.data.meshes.new('TMP_' + nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        o = bpy.data.objects.new('TMP_' + nm, me); made.append(o)
    Vw, Fw, _ = geo_wall(); Vp, Fp, _ = geo_pillar()
    for i, x in enumerate((0, GRID, 2 * GRID)): mk(f'P{i}', Vp, Fp, 0, (x, 0, 0))
    mk('P3', Vp, Fp, 0, (2 * GRID, GRID, 0))
    mk('W0', Vw, Fw, 0, (GRID / 2, 0, 0)); mk('W1', Vw, Fw, 0, (1.5 * GRID, 0, 0)); mk('W2', Vw, Fw, 90, (2 * GRID, GRID / 2, 0))
    try:
        render(made, out, (-0.45, -1.0, 0.55), res=(1280, 800), fill_w=0.85, fill_h=0.85)
    finally:
        for o in made:
            me = o.data; bpy.data.objects.remove(o, do_unlink=True); bpy.data.meshes.remove(me)


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


if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, ob, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), CFG['view_ref'], res=(1254, 1254), fill_w=0.80, fill_h=0.80, lens=85)
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_prev_{tag}.png'), CFG['view_prev'])
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), CFG['view_prev'], res=(128, 128), fill_w=0.9, fill_h=0.9)
        assembly_render(os.path.join(CHECK_DIR, f'assembly_{tag}.png'), mat)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render([root, ob], os.path.join(ART, 'Previews', CFG['preview']), CFG['view_prev'])
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, f'geom_{tag}.json'))
