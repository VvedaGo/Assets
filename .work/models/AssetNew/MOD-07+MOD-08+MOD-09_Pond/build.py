# build.py - formal raised pond modules, pack AssetNew (Cottage Garden Decor), atlas A Garden_Build (read only):
#   MOD-07 Pond edge 1 m        FMS_Garden_Pond_Edge
#   MOD-08 Pond edge corner     FMS_Garden_Pond_Edge_Corner
#   MOD-09 Pond water tile 1x1  FMS_Garden_Pond_Water (opaque)
# One registry script for the three modules (form of Tools/blender/build_registry_template.py).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- MOD-07|MOD-08|MOD-09 build|export|verify|dump
#   build  = build the model + printed checks (topology, coplanar, ground, tris, SNAP pond contract)
#            + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify = only re-import the FBX in art/
#   dump   = build + geometry dump only (live/headless comparison)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\MOD-07+MOD-08+MOD-09_Pond\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['MOD-07', 'build']})
#   Live mode touches only the collection MOD-07_Pond_Edge / MOD-08_Pond_Edge_Corner / MOD-09_Pond_Water.
# Axes (Blender): Z = up (Unity Y). FBX export -Z forward, Y up: Blender (x, y, z) -> Unity (-x, z, -y).
#   Spec (Unity) Z = -Blender y: the basin interior (Unity +Z) is Blender -y, "outward" (Unity -Z) is Blender +y.
#   MOD-07: Blender x -0.5..0.5 (length), y 0..0.37 (inner face y = 0, outer block face y = 0.35, coping 0.37),
#           z 0..0.45. Pivot = middle of the inner face at ground level.
#   MOD-08: Blender x 0..0.37, y 0..0.37 (inner butt faces x = 0 and y = 0), z 0..0.45. Pivot = inner corner of the
#           basin (Unity X <= 0, Z <= 0 = Blender x >= 0, y >= 0). The basin interior is Blender x < 0, y < 0.
#   MOD-09: Blender x, y -0.5..0.5, z 0.34..0.38 (slab raised inside the mesh). Pivot = centre of the base on the ground.
# Stone wording/cells as MOD-03 / WTR-03 / FLB-01: A-12 Stone #A7A39A = masonry, core; A-11 Stone light #C9C3B6 =
# coping and the second-tone blocks. Water as WTR-03: A-15 #4A78A8, opaque, same material.
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
LIME, STONE, WATER = 11, 12, 15              # A-11 Stone light (coping, 2nd tone), A-12 Stone, A-15 Water
G = 0.012                                    # joint width; blocks stop G/2 short of the module ends (12 mm butt joint)
# pond edge section (snap contract, CATALOG «Модули и стыковка» item 4)
CORE = 0.34                                  # core outer face (Unity Z -0.34)
FACE = 0.35                                  # proud block face (Unity Z -0.35), blocks 0.01 proud
BLK_BACK = 0.33                              # block back face, 1 cm inside the core (no coplanar faces)
COPE = 0.37                                  # coping outer face (0.02 overhang)
Z_CORE0 = 0.003                              # core bottom 3 mm above the ground (the blocks own z 0, no coplanar bottoms)
Z_COPE, Z_TOP, BEV = 0.40, 0.45, 0.015       # coping underside, top, bevel on the outer long top edge(s) only
COURSES = [(0.0, 0.20 - G / 2), (0.20 + G / 2, Z_COPE - G / 2)]   # 2 courses, 12 mm joint, 6 mm mortar bed under the coping
# MOD-07 joints (x of the vertical joint centre) per course, light (A-11) blocks as the reference: top course light on the
# right of the reference view (Blender -x), bottom course light on the left (Blender +x); 2 of 4 blocks, as the picture.
E_JOINT = {0: 0.02, 1: -0.12}
E_LIGHT = {(0, 1), (1, 0)}                   # (course, block index from -x)
# MOD-08 (Fix 1, budget 80): per course a quoin wrapping the outer corner (0.21 on one face, 0.344 on the other) + a face
# block (0.122) on the short side, pinwheel between the courses; shell 32 + 4 x 12 = 80 tris
C_QUOIN = 0.21
# MOD-09 water
W_Z0, W_Z1 = 0.34, 0.38
RIPPLE = {(1, 1): -0.004, (2, 1): -0.001, (1, 2): -0.002, (2, 2): -0.005}  # inner top vertices dz (<= +-0.005); only
                                             # downwards, so the slab bbox stays 0.34..0.38 (catalogue 0.04, top at 0.38)
GRID = 1.0
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'MOD-07'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'


# ---------------- geometry (V = [(x, y, z)], F = [(vertex indices, slot, component)]) ----------------
class Geo:
    def __init__(self): self.V, self.F, self._ix = [], [], {}
    def add(self, p, comp=None):
        """vertex; shared by exact position inside one component (comp given) so faces of a shell weld"""
        key = (comp, tuple(round(float(c), 9) for c in p)) if comp else None
        if key and key in self._ix: return self._ix[key]
        self.V.append(tuple(float(c) for c in p)); i = len(self.V) - 1
        if key: self._ix[key] = i
        return i
    def poly(self, comp, pts, slot):
        self.F.append(([self.add(p, comp) for p in pts], slot, comp))
    def box(self, comp, x0, x1, y0, y1, z0, z1, slot):
        i = [self.add((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        for q in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
            self.F.append(([i[k] for k in q], slot, comp))


def cope_fan(pts):
    """fan triangles from pts[-1] of an end polygon whose first three points are collinear (no degenerate triangle)"""
    a = pts[-1]
    return [(a, pts[k], pts[k + 1]) for k in range(len(pts) - 2)]


def geo_edge():
    g = Geo(); blocks = []; S = 'Shell'
    # section (y, z), closed: core part below z 0.40 (A-12), coping part above (A-11); the inner face y = 0 is split at
    # the coping underside so the coping band and the core show their own colour; one closed shell, inner face flat.
    yb, zb = COPE - BEV, Z_TOP - BEV
    for x in (-0.5, 0.5):                                      # ends: core quad + coping polygon (fan, collinear base)
        g.poly(S, [(x, 0, Z_CORE0), (x, CORE, Z_CORE0), (x, CORE, Z_COPE), (x, 0, Z_COPE)], STONE)
        for t in cope_fan([(x, 0, Z_COPE), (x, CORE, Z_COPE), (x, COPE, Z_COPE), (x, COPE, zb), (x, yb, Z_TOP), (x, 0, Z_TOP)]):
            g.poly(S, t, LIME)
    sec = [((0, Z_CORE0), (CORE, Z_CORE0), STONE),            # bottom
           ((CORE, Z_CORE0), (CORE, Z_COPE), STONE),          # core outer face (seen in the joints)
           ((CORE, Z_COPE), (COPE, Z_COPE), LIME),            # coping underside (overhang)
           ((COPE, Z_COPE), (COPE, zb), LIME),                # coping outer face
           ((COPE, zb), (yb, Z_TOP), LIME),                   # bevel 0.015 on the outer long top edge
           ((yb, Z_TOP), (0, Z_TOP), LIME),                   # coping top
           ((0, Z_TOP), (0, Z_COPE), LIME),                   # inner face, coping band
           ((0, Z_COPE), (0, Z_CORE0), STONE)]                # inner face, core (flat, no relief)
    for (y0, z0), (y1, z1), sl in sec:
        g.poly(S, [(-0.5, y0, z0), (0.5, y0, z0), (0.5, y1, z1), (-0.5, y1, z1)], sl)
    for c, (z0, z1) in enumerate(COURSES):
        j = E_JOINT[c]; xs = [(-0.5 + G / 2, j - G / 2), (j + G / 2, 0.5 - G / 2)]
        for b, (x0, x1) in enumerate(xs):
            sl = LIME if (c, b) in E_LIGHT else STONE; cn = f'Block_{c}{b}'
            g.box(cn, x0, x1, BLK_BACK, FACE, z0, z1, sl); blocks.append((cn, x1 - x0, sl))
    return g.V, g.F, blocks


def geo_corner():
    g = Geo(); blocks = []; S = 'Shell'
    a, c, b, zb = CORE, COPE, COPE - BEV, Z_TOP - BEV
    z0, zc, zt = Z_CORE0, Z_COPE, Z_TOP
    g.poly(S, [(0, 0, z0), (a, 0, z0), (a, a, z0), (0, a, z0)], STONE)                     # bottom
    g.poly(S, [(0, 0, z0), (0, a, z0), (0, a, zc), (0, 0, zc)], STONE)                     # inner x = 0, core
    g.poly(S, [(0, 0, z0), (a, 0, z0), (a, 0, zc), (0, 0, zc)], STONE)                     # inner y = 0, core
    for t in cope_fan([(0, 0, zc), (0, a, zc), (0, c, zc), (0, c, zb), (0, b, zt), (0, 0, zt)]): g.poly(S, t, LIME)
    for t in cope_fan([(0, 0, zc), (a, 0, zc), (c, 0, zc), (c, 0, zb), (b, 0, zt), (0, 0, zt)]): g.poly(S, t, LIME)
    g.poly(S, [(a, 0, z0), (a, a, z0), (a, a, zc), (a, 0, zc)], STONE)                     # core outer x = 0.34
    g.poly(S, [(0, a, z0), (a, a, z0), (a, a, zc), (0, a, zc)], STONE)                     # core outer y = 0.34
    g.poly(S, [(a, 0, zc), (c, 0, zc), (c, c, zc), (0, c, zc), (0, a, zc), (a, a, zc)], LIME)   # coping underside (L)
    g.poly(S, [(c, 0, zc), (c, c, zc), (c, c, zb), (c, 0, zb)], LIME)                      # coping outer x
    g.poly(S, [(0, c, zc), (c, c, zc), (c, c, zb), (0, c, zb)], LIME)                      # coping outer y
    g.poly(S, [(c, 0, zb), (c, c, zb), (b, b, zt), (b, 0, zt)], LIME)                      # bevel x (mitred)
    g.poly(S, [(0, c, zb), (c, c, zb), (b, b, zt), (0, b, zt)], LIME)                      # bevel y
    g.poly(S, [(0, 0, zt), (b, 0, zt), (b, b, zt), (0, b, zt)], LIME)                      # top
    # Fix 1 (review models_2): 2 blocks per course in a pinwheel = quoin wrapping the outer corner (full 0.344 on one face,
    # C_QUOIN on the other) + a face block of different length; the joint is on the x face in the bottom course and on the
    # y face in the top course. Tones alternate between the courses (bottom quoin A-12 / block A-11, top A-11 / A-12).
    j0, j1 = FACE - C_QUOIN - G / 2, FACE - C_QUOIN + G / 2     # joint edges (0.134 / 0.146): face block 0.128, quoin 0.204 on the short face
    for k, (q0, q1) in enumerate(COURSES):
        qs, bs = (STONE, LIME) if k == 0 else (LIME, STONE)
        if k == 0:   # quoin: whole y face (x 0.006..0.35) + 0.21 of the x face; face block on the x face
            g.box('Block_0Q', G / 2, FACE, j1, FACE, q0, q1, qs); blocks.append(('Block_0Q', FACE - j1, qs))
            g.box('Block_0F', BLK_BACK, FACE, G / 2, j0, q0, q1, bs); blocks.append(('Block_0F', j0 - G / 2, bs))
        else:        # mirrored: whole x face + 0.21 of the y face; face block on the y face
            g.box('Block_1Q', j1, FACE, G / 2, FACE, q0, q1, qs); blocks.append(('Block_1Q', FACE - j1, qs))
            g.box('Block_1F', G / 2, j0, BLK_BACK, FACE, q0, q1, bs); blocks.append(('Block_1F', j0 - G / 2, bs))
    return g.V, g.F, blocks


def geo_water():
    g = Geo(); S = 'Water'; n = 3; h = 0.5
    xs = [-h + k / n for k in range(n + 1)]
    top = {(i, j): (xs[i], xs[j], W_Z1 + RIPPLE.get((i, j), 0.0)) for i in range(n + 1) for j in range(n + 1)}
    for i in range(n):
        for j in range(n):                                   # 3 x 3 quads -> 18 tris, diagonal alternates (soft facets)
            p00, p10, p11, p01 = top[(i, j)], top[(i + 1, j)], top[(i + 1, j + 1)], top[(i, j + 1)]
            if (i + j) % 2 == 0: tris = [(p00, p10, p11), (p00, p11, p01)]
            else: tris = [(p00, p10, p01), (p10, p11, p01)]
            for t in tris: g.poly(S, t, WATER)
    g.poly(S, [(-h, -h, W_Z0), (h, -h, W_Z0), (h, h, W_Z0), (-h, h, W_Z0)], WATER)         # bottom
    for side in range(4):                                     # sides: 4 tris each, border vertices exactly at 0.38
        if side == 0: e = [top[(i, 0)] for i in range(n + 1)]
        elif side == 1: e = [top[(n, j)] for j in range(n + 1)]
        elif side == 2: e = [top[(i, n)] for i in range(n, -1, -1)]
        else: e = [top[(0, j)] for j in range(n, -1, -1)]
        b0 = (e[0][0], e[0][1], W_Z0); b1 = (e[-1][0], e[-1][1], W_Z0)
        for t in [(b0, b1, e[1]), (b1, e[2], e[1]), (b1, e[3], e[2]), (b0, e[1], e[0])]: g.poly(S, t, WATER)
    return g.V, g.F, []


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


# ---------------- SNAP (contract: CATALOG «Модули и стыковка» item 4, internal grid 1.0 m) ----------------
def xform(V, rot_deg, t):
    """exact quarter turns in double precision (mathutils matrices are float32: ~1e-8 noise reads as fake overlaps)"""
    c, s = {0: (1, 0), 90: (0, 1), 180: (-1, 0), -90: (0, -1), 270: (0, -1)}[rot_deg]
    return [(c * p[0] - s * p[1] + t[0], s * p[0] + c * p[1] + t[1], p[2] + t[2]) for p in V]


def bbox(V): return [min(p[j] for p in V) for j in range(3)], [max(p[j] for p in V) for j in range(3)]


def oriented_faces(V, F):
    """faces as (comp, pts, outward unit normal, plane d); normals from bmesh recalc per closed shell (concave-safe)"""
    bm = bmesh.new(); vs = [bm.verts.new(Vector(p)) for p in V]; comps = []
    for idx, _, cn in F: bm.faces.new([vs[i] for i in idx]); comps.append(cn)
    bm.faces.ensure_lookup_table(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out = []
    for f, cn in zip(bm.faces, comps):
        n = f.normal.copy(); p = [v.co.copy() for v in f.verts]
        out.append((cn, p, n, n.dot(p[0])))
    bm.free()
    return out


def poly_overlap_area(P, Q, n):
    """area of the intersection of two convex coplanar polygons (Sutherland-Hodgman in the plane)"""
    u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized(); w = n.cross(u)
    to2 = lambda pts: [(p.dot(u), p.dot(w)) for p in pts]
    def ccw(pts):
        a = sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))
        return pts if a < 0 else pts[::-1]
    subj, clip = ccw(to2(P)), ccw(to2(Q))
    def inside(p, a, b): return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-12
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


def concave_safe(poly_pts, n):
    """split a face into triangles for the convex overlap test (the corner coping underside is an L hexagon)"""
    if len(poly_pts) <= 4: return [poly_pts]
    bm = bmesh.new(); vs = [bm.verts.new(p) for p in poly_pts]; f = bm.faces.new(vs)
    r = bmesh.ops.triangulate(bm, faces=[f]); tris = [[v.co.copy() for v in t.verts] for t in r['faces']]; bm.free()
    return tris


def cross_coplanar(A, B):
    """coplanar overlapping face pairs between two placed pieces: same-facing (z-fight), back-to-back contact, ground"""
    res = dict(zfight=[], contact=[], ground=[])
    for (ca, pa, na, da) in A:
        for (cb, pb, nb, db) in B:
            dot = na.dot(nb)
            if abs(abs(dot) - 1) > 1e-6 or abs(da - db * (1 if dot > 0 else -1)) > 1e-4: continue
            ar = sum(poly_overlap_area(x, y, na) for x in concave_safe(pa, na) for y in concave_safe(pb, nb))
            if ar <= 1e-8: continue
            if dot > 0 and na.z < -0.999 and abs(pa[0].z) < 1e-9: res['ground'].append((ca, cb, ar))
            elif dot > 0: res['zfight'].append((ca, cb, round(ar, 6)))
            else: res['contact'].append((ca, cb, round(ar, 6)))
    return res


def bbox_overlap_volume(A, B):
    (la, ha), (lb, hb) = A, B
    d = [min(ha[i], hb[i]) - max(la[i], lb[i]) for i in range(3)]
    return 0.0 if min(d) <= 0 else d[0] * d[1] * d[2], d


def pond(N, M):
    """pieces of a closed N x M pond, interior x 0..N, y 0..M (Blender); (kind, rot, t)"""
    P = [('W', 0, (i + 0.5, j + 0.5, 0)) for i in range(N) for j in range(M)]
    P += [('E', 180, (i + 0.5, 0, 0)) for i in range(N)] + [('E', 0, (i + 0.5, M, 0)) for i in range(N)]
    P += [('E', 90, (0, j + 0.5, 0)) for j in range(M)] + [('E', -90, (N, j + 0.5, 0)) for j in range(M)]
    P += [('C', 180, (0, 0, 0)), ('C', -90, (N, 0, 0)), ('C', 0, (N, M, 0)), ('C', 90, (0, M, 0))]
    return P


def snap_check():
    ok = True
    def row(nm, good, txt=''):
        nonlocal ok; ok &= bool(good); print(f'  SNAP {nm}: {txt} {"OK" if good else "FAIL"}')
    geo = {'E': geo_edge(), 'C': geo_corner(), 'W': geo_water()}
    Ve, Fe, _ = geo['E']; Vc, Fc, _ = geo['C']; Vw, Fw, _ = geo['W']
    # single pieces
    lo, hi = bbox(Ve)
    row('MOD-07 bbox', all(abs(a - b) < 1e-6 for a, b in zip(lo + hi, [-0.5, 0, 0, 0.5, COPE, Z_TOP])),
        f'x {lo[0]:.3f}..{hi[0]:.3f} y(out) {lo[1]:.3f}..{hi[1]:.3f} z {lo[2]:.3f}..{hi[2]:.3f} (want +-0.5, 0..0.37, 0..0.45)')
    inner = [p for idx, _, cn in Fe for p in [Ve[i] for i in idx] if abs(p[1]) < 1e-9]
    infaces = [idx for idx, _, cn in Fe if all(abs(Ve[i][1]) < 1e-9 for i in idx)]
    row('MOD-07 inner face flat on the grid line (y = 0, Unity Z = 0)', min(p[1] for p in Ve) > -1e-9 and len(infaces) == 2,
        f'{len(infaces)} faces on y = 0 (core + coping band), nothing at y < 0')
    blk = [Ve[i] for idx, _, cn in Fe if cn.startswith('Block') for i in idx]
    row('MOD-07 blocks 0.01 proud, outer face 0.35, core 0.34', abs(max(p[1] for p in blk) - FACE) < 1e-9,
        f'block face {max(p[1] for p in blk):.3f}, core {CORE:.3f}, coping overhang {COPE - FACE:.3f}')
    endA = {(round(p[1], 6), round(p[2], 6)) for p in Ve if abs(p[0] + 0.5) < 1e-9}
    endB = {(round(p[1], 6), round(p[2], 6)) for p in Ve if abs(p[0] - 0.5) < 1e-9}
    row('MOD-07 ends flat on x = +-0.5, equal sections (no notch)', endA == endB and not [p for p in Ve if abs(p[0]) > 0.5 + 1e-9],
        f'{len(endA)} section verts per end')
    lo, hi = bbox(Vc)
    row('MOD-08 bbox / pivot = inner corner', all(abs(a - b) < 1e-6 for a, b in zip(lo + hi, [0, 0, 0, COPE, COPE, Z_TOP])),
        f'x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} z {lo[2]:.3f}..{hi[2]:.3f} (want 0..0.37 x 0..0.37 x 0..0.45)')
    secC = {(round(p[1], 6), round(p[2], 6)) for p in Vc if abs(p[0]) < 1e-9}
    secCy = {(round(p[0], 6), round(p[2], 6)) for p in Vc if abs(p[1]) < 1e-9}
    shellE = {q for q in endA}
    row('MOD-08 butt faces = MOD-07 end section', secC == secCy and secC <= shellE | {(0.0, round(Z_COPE, 6))},
        f'x = 0 face {len(secC)} verts, y = 0 face {len(secCy)} verts')
    lo, hi = bbox(Vw)
    border = [p for p in Vw if abs(abs(p[0]) - 0.5) < 1e-9 or abs(abs(p[1]) - 0.5) < 1e-9]
    top_border = [p for p in border if p[2] > W_Z0 + 1e-6]
    rip = [p[2] - W_Z1 for p in Vw if p[2] > W_Z0 + 1e-6 and p not in border]
    row('MOD-09 slab 1.0 x 1.0, top 0.38 / bottom 0.34', abs(hi[0] - 0.5) < 1e-9 and abs(lo[0] + 0.5) < 1e-9 and
        abs(lo[2] - W_Z0) < 1e-9 and all(abs(p[2] - W_Z1) < 1e-9 for p in top_border),
        f'{hi[0] - lo[0]:.3f} x {hi[1] - lo[1]:.3f}, z {lo[2]:.3f}..{hi[2]:.4f}; {len(top_border)} top border verts at 0.38')
    row('MOD-09 ripple inside +-0.005', rip and max(abs(r) for r in rip) <= 0.005 + 1e-9,
        f'inner dz {[round(r * 1000, 1) for r in rip]} mm')
    row('water top 0.07 below the edge top', abs((Z_TOP - W_Z1) - 0.07) < 1e-9, f'{Z_TOP:.2f} - {W_Z1:.2f} = {Z_TOP - W_Z1:.2f}')
    # pairs and closed ponds
    cache = {}
    def placed(kind, rot, t):
        key = (kind, rot, t)
        if key not in cache:
            V, F, _ = geo[kind]; PV = xform(V, rot, t)
            cache[key] = (PV, oriented_faces(PV, F), bbox(PV))
        return cache[key]
    def check_set(label, pieces):
        nonlocal ok
        zf, ov, pairs = [], [], 0
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                A = placed(*pieces[i]); B = placed(*pieces[j])
                vol, d = bbox_overlap_volume(A[2], B[2])
                if min(d) < -1e-6: continue                   # not touching
                pairs += 1
                if vol > 1e-9: ov.append((pieces[i][0], pieces[j][0], round(vol, 6)))
                r = cross_coplanar(A[1], B[1])
                zf += [(pieces[i][:1], pieces[j][:1], z) for z in r['zfight']]
        row(f'{label}: no interpenetration, no same-facing coplanar faces', not zf and not ov,
            f'{len(pieces)} pieces, {pairs} touching pairs, volume overlaps {len(ov)} {ov[:2]}, z-fight {len(zf)} {zf[:2]}')
    # edge | edge
    check_set('edge | edge (butt at a node)', [('E', 0, (-0.5, 0, 0)), ('E', 0, (0.5, 0, 0))])
    A = placed('E', 0, (-0.5, 0, 0)); B = placed('E', 0, (0.5, 0, 0))
    row('edge | edge gap', abs(A[2][1][0] - B[2][0][0]) < 1e-9, f'{(B[2][0][0] - A[2][1][0]) * 1000:.3f} mm at x = 0 (node)')
    # edge | corner (both legs)
    pcs = [('C', 0, (0, 0, 0)), ('E', 0, (-0.5, 0, 0)), ('E', -90, (0, -0.5, 0))]
    check_set('edge | corner | edge (90 deg)', pcs)
    C = placed(*pcs[0]); E1 = placed(*pcs[1]); E2 = placed(*pcs[2])
    row('edge | corner gaps', abs(E1[2][1][0] - C[2][0][0]) < 1e-9 and abs(E2[2][1][1] - C[2][0][1]) < 1e-9,
        f'edge end x {E1[2][1][0]:.4f} vs corner face x {C[2][0][0]:.4f}; turned edge end y {E2[2][1][1]:.4f} vs corner face y {C[2][0][1]:.4f}')
    row('edge | corner outer faces continue', abs(E1[2][1][1] - C[2][1][1]) < 1e-9 and abs(E2[2][1][0] - C[2][1][0]) < 1e-9,
        f'coping line y {E1[2][1][1]:.3f} / {C[2][1][1]:.3f}, x {E2[2][1][0]:.3f} / {C[2][1][0]:.3f}')
    for N, M in ((2, 2), (3, 2)):
        P = pond(N, M)
        nW = sum(1 for p in P if p[0] == 'W'); nE = sum(1 for p in P if p[0] == 'E'); nC = sum(1 for p in P if p[0] == 'C')
        row(f'pond {N}x{M} piece count', (nW, nE, nC) == (N * M, 2 * (N + M), 4), f'water {nW} + edges {nE} + corners {nC}')
        check_set(f'pond {N}x{M}', P)
        # water coverage = interior exactly; inner faces of edges/corners bound the interior with gap 0
        wb = [placed(*p)[2] for p in P if p[0] == 'W']
        area = sum((h[0] - l[0]) * (h[1] - l[1]) for l, h in wb)
        inside = all(l[0] >= -1e-9 and l[1] >= -1e-9 and h[0] <= N + 1e-9 and h[1] <= M + 1e-9 for l, h in wb)
        row(f'pond {N}x{M} water covers the interior', inside and abs(area - N * M) < 1e-9,
            f'area {area:.3f} of {N * M}, all slabs inside 0..{N} x 0..{M}')
        stone = [placed(*p)[2] for p in P if p[0] != 'W']
        intrude = [b for b in stone if b[0][0] < N - 1e-9 and b[1][0] > 1e-9 and b[0][1] < M - 1e-9 and b[1][1] > 1e-9]
        sides = {'y=0': [], 'y=M': [], 'x=0': [], 'x=N': []}
        for l, h in stone:
            if abs(h[1]) < 1e-9: sides['y=0'].append((l[0], h[0]))
            if abs(l[1] - M) < 1e-9: sides['y=M'].append((l[0], h[0]))
            if abs(h[0]) < 1e-9: sides['x=0'].append((l[1], h[1]))
            if abs(l[0] - N) < 1e-9: sides['x=N'].append((l[1], h[1]))
        def covered(iv, L):
            iv = sorted((max(0, a), min(L, b)) for a, b in iv if b > 0 and a < L); x = 0.0
            for a, b in iv:
                if a > x + 1e-9: return False
                x = max(x, b)
            return x >= L - 1e-9
        cov = {k: covered(v, N if k.startswith('y') else M) for k, v in sides.items()}
        row(f'pond {N}x{M} inner faces enclose the water (gap 0)', not intrude and all(cov.values()), f'{cov}, stone inside the basin {len(intrude)}')
        wt = [placed(*p) for p in P if p[0] == 'W']
        steps = 0
        for i in range(len(wt)):
            for j in range(i + 1, len(wt)):
                a = {(round(v[0], 6), round(v[1], 6)): v[2] for v in wt[i][0] if v[2] > W_Z0 + 1e-6}
                b = {(round(v[0], 6), round(v[1], 6)): v[2] for v in wt[j][0] if v[2] > W_Z0 + 1e-6}
                steps += sum(1 for k in set(a) & set(b) if abs(a[k] - b[k]) > 1e-9)
        row(f'pond {N}x{M} neighbouring water slabs without a step', steps == 0, f'{steps} mismatched shared top vertices')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


# ---------------- registry ----------------
REG = {
    'MOD-07': dict(name='FMS_Garden_Pond_Edge', coll='MOD-07_Pond_Edge', preview='FMS_Garden_MOD_07_Preview.png',
                   budget=120, geo=geo_edge, light_az=180,
                   view_ref=(0.55, 1.0, 0.70), view_prev=(0.55, 1.0, 0.62)),
    'MOD-08': dict(name='FMS_Garden_Pond_Edge_Corner', coll='MOD-08_Pond_Edge_Corner', preview='FMS_Garden_MOD_08_Preview.png',
                   budget=80, geo=geo_corner, light_az=180,
                   view_ref=(1.0, 0.80, 0.95), view_prev=(1.0, 0.80, 0.85)),
    'MOD-09': dict(name='FMS_Garden_Pond_Water', coll='MOD-09_Pond_Water', preview='FMS_Garden_MOD_09_Preview.png',
                   budget=50, geo=geo_water, light_az=0,
                   view_ref=(-1.0, -1.0, 1.1), view_prev=(-0.75, -1.0, 0.80)),
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
    if blocks:
        print(f'  blocks {len(blocks)} ({sum(1 for b in blocks if b[2] == LIME)} second tone A-11, '
              f'{sum(1 for b in blocks if b[2] == STONE)} A-12); face lengths {sorted(round(b[1], 3) for b in blocks)}')
    skip = tuple(sorted({c for _, _, c in F})) if ID != 'MOD-07' else tuple(b[0] for b in blocks)
    ob = pc.to_object(to_part(V, F), NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    bpy.context.view_layer.update()
    tot = pc.report({'Body': ob})
    print('  tris per part:', tris)
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'OVER x{tot / CFG["budget"]:.2f}')
    pc.coplanar_overlaps(ob)
    slots = sorted({cell_of(ob.data.uv_layers.active.data[p.loop_start].uv) for p in ob.data.polygons})
    zmin = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    print('  atlas cells used', slots, '| smooth faces', sum(p.use_smooth for p in ob.data.polygons),
          '| materials', [m.name for m in ob.data.materials], f'| min z {zmin:.4f}',
          '(blocks on the ground)' if ID != 'MOD-09' else '(slab lifted inside the mesh, pivot on the ground)')
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


def assembly_render(out, mat, N=3, M=2, view=(-0.55, -1.0, 0.85)):
    """check render only: a closed N x M pond from all three modules, temporary objects"""
    made = []
    geo = {'E': geo_edge(), 'C': geo_corner(), 'W': geo_water()}
    for k, (kind, rot, t) in enumerate(pond(N, M)):
        V, F, _ = geo[kind]
        P = to_part(xform(V, rot, t), F, f'{kind}{k}'); bm = P.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        uvl = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = pc.cell_uv(f[P.slot])
        me = bpy.data.meshes.new(f'TMP_{kind}{k}'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        made.append(bpy.data.objects.new(f'TMP_{kind}{k}', me))
    try:
        render(made, out, view, res=(1280, 800), fill_w=0.85, fill_h=0.85)
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
        assembly_render(os.path.join(CHECK_DIR, f'assembly_3x2_{tag}.png'), mat)
        assembly_render(os.path.join(CHECK_DIR, f'assembly_2x2_out_{tag}.png'), mat, 2, 2, (0.75, 1.0, 0.75))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render([root, ob], os.path.join(ART, 'Previews', CFG['preview']), CFG['view_prev'])
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, f'geom_{tag}.json'))
