# build.py - PLT-06 Hollyhock (FMS_Garden_Hollyhock + _White), pack AssetNew (Cottage Garden Decor),
# atlas F Garden_Flora (read only: the shared PNG is loaded, never rewritten), material M_Garden_Flora.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- PLT-06 build|export|dump
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/PLT-06/
#   export = build + 2 FBX (base, _White; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 of both meshes incl. UV cells)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\PLT-06_Hollyhock\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['PLT-06', 'build']})
#   Live mode touches only the collection PLT-06_Hollyhock and its child PLT-06_Hollyhock_White
#   (+ temporary TMP_ scenes that are removed again).
#
# Axes (Blender): X right, -Y front (= reference camera; Unity +Z after the -Z-forward export), Z up (Unity Y).
# Pivot (0, 0, 0) = centre of the foot on the ground.
# Helpers copied from PLT-01 build.py (accepted): ring, bezier_pts, taper, overlaps, render, geom_dump; atlas_readonly
# from PLT-05. Own generators: hollyhock_cup (closed 24-tri trumpet cup), leaf_plate (18-tri domed plate), stem_bud.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'PLT-06')
COLL = 'PLT-06_Hollyhock'
NAME = 'FMS_Garden_Hollyhock'
PREVIEW = 'FMS_Garden_PLT_06_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'
ATLAS_MAT = 'M_Garden_Flora'
BUDGET = 700
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
STEM = 0                                      # foliage green (reference stems are mid green; spec said 2), no brown
CALYX = 2                                     # dark green cup base (calyx) where the cup sits on the stem
BUD_LO, BUD_HI = 1, (1, 0)                    # bud: light belt, tip cone alternating light / mid facets
CUP_IN, CUP_OUT, CENTRE = 6, 7, 11            # inside deeper pink, outside/rim light pink, yellow centre
VARIANTS = {'_White': {CUP_IN: 8, CUP_OUT: 8}}  # same mesh, UV cells remapped; centre stays yellow
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'PLT-06'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi
UP = Vector((0, 0, 1))


def pol(az, r, z):
    a = math.radians(az)
    return Vector((r * math.cos(a), r * math.sin(a), z))


# ============ helpers (copied from PLT-01) ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    return [O + e1 * (r * math.cos(a0 + TAU * k / n)) + e2 * (r * math.sin(a0 + TAU * k / n)) for k in range(n)]


def bezier_pts(p0, pm, p2, n, ts=None):
    """points of the quadratic Bezier through p0, pm (at t = 0.5), p2; uniform t unless ts is given"""
    p0, pm, p2 = Vector(p0), Vector(pm), Vector(p2); c = 2 * pm - (p0 + p2) / 2
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t * t * p2 for t in (ts or [i / (n - 1) for i in range(n)])]


def taper(r0, r1, n):
    return [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]


# ============ PLT-06 generators ============
def stem_bud(P, pts, radii, az, bud_r=0.036, bud_h=0.035, bud_tip=0.10, n=6):
    """6-sided tapered stem along a polyline (base ring horizontal on the ground, other rings mitred) with the end bud
    fused on the top ring: top ring -> 3-sided bud belt (bud_r, bud_h along the tip tangent) -> point (bud_tip).
    Stem n*segments*2 + 4 (ground cap) tris, bud 12 tris. Returns (stem faces, bud faces)."""
    pts = [Vector(q) for q in pts]; ref = pol(az, 1.0, 0.0); rings = []
    for i, q in enumerate(pts):
        if i == 0: d = UP
        elif i == len(pts) - 1: d = pts[-1] - pts[-2]
        else: d = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        rings.append(ring(q, d, radii[i], n, 0.0, ref))
    R = [[P.bm.verts.new(v) for v in r] for r in rings]; fs = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            fs.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], STEM))
    fs.append(P.face(list(reversed(R[0])), STEM))
    t = (pts[-1] - pts[-2]).normalized()
    B = [P.bm.verts.new(v) for v in ring(pts[-1] + t * bud_h, t, bud_r, 3, math.pi / 3, ref)]   # B[j] over top[2j+1]
    tip = P.bm.verts.new(pts[-1] + t * bud_tip); top = R[-1]; bs = []
    for j in range(3):                                   # top ring (6) -> bud belt (3): 9 tris; belt -> point: 3 tris
        b0, b1 = B[j], B[(j + 1) % 3]
        r1, r2, r3 = top[(2 * j + 1) % n], top[(2 * j + 2) % n], top[(2 * j + 3) % n]
        bs += [P.face([b0, r1, r2], BUD_LO), P.face([b0, r2, b1], BUD_LO), P.face([b1, r2, r3], BUD_LO)]
        bs.append(P.face([b0, b1, tip], BUD_HI[j % 2]))
    return fs, bs


def hollyhock_cup(P, anchor, az, tilt, r_rim, r_b=0.02, H=0.075, depth=0.035, r_y=0.026, h_y=0.015, off=0.02,
                  spin=0.0, n=6):
    """HOLLYHOCK CUP v3: ONE closed shell, 28 tris. Base triangle r_b (centre `off` outward from the stem axis = on the
    stem surface, so the cup sits ON the stem; 1 dark-green calyx tri) -> outer wall to the hexagonal rim r_rim at H
    (9 tris, CUP_OUT light pink) -> inside wall rim -> yellow ring r_y `depth` below the rim, twisted half a step
    (12 tris, alternating CUP_OUT at the rim / CUP_IN deeper pink) -> yellow centre cone, tip h_y above its ring
    (6 tris, CENTRE). Axis = outward azimuth az tilted `tilt` deg up. Returns (faces, axis, rim centre, rim verts)."""
    a = (pol(az, math.cos(math.radians(tilt)), 0) + UP * math.sin(math.radians(tilt))).normalized()
    O = Vector(anchor) + pol(az, off, 0.0); C = O + a * H; ref = pol(az + 90, 1.0, 0.0)
    B = [P.bm.verts.new(v) for v in ring(O, a, r_b, 3, spin + math.pi / 3, ref)]      # B[j] under R[2j+1]
    R = [P.bm.verts.new(v) for v in ring(C, a, r_rim, n, spin, ref)]
    I = [P.bm.verts.new(v) for v in ring(C - a * depth, a, r_y, n, spin + math.pi / n, ref)]
    T = P.bm.verts.new(C - a * (depth - h_y))
    fs = [P.face(list(reversed(B)), CALYX)]
    for j in range(3):                                   # outer wall: triangle edge j -> rim verts 2j+1 .. 2j+3
        b0, b1 = B[j], B[(j + 1) % 3]
        r1, r2, r3 = R[(2 * j + 1) % n], R[(2 * j + 2) % n], R[(2 * j + 3) % n]
        fs += [P.face([b0, r1, r2], CUP_OUT), P.face([b0, r2, b1], CUP_OUT), P.face([b1, r2, r3], CUP_OUT)]
    for k in range(n):
        k1 = (k + 1) % n
        fs.append(P.face([R[k], R[k1], I[k]], CUP_OUT if k % 2 else CUP_IN))
        fs.append(P.face([I[k], R[k1], I[k1]], CUP_IN))
        fs.append(P.face([I[k], I[k1], T], CENTRE))
    return fs, a, C, R


# leaf outline in leaf space (x along the leaf from the base, y across), as fractions of L / W
LEAF_OUT = [(0.0, 0.0, 0.0), (0.14, -0.38, -0.02), (0.45, -0.50, -0.035), (0.76, -0.36, -0.045), (1.0, 0.0, -0.05),
            (0.76, 0.36, -0.045), (0.45, 0.50, -0.035), (0.14, 0.38, -0.02)]     # x / L, y / W, drop below the base (m)


def leaf_plate(P, az, base_r, base_z, L, W, tilt, hT, hB, seed, noise=0.008):
    """LEAF PLATE: closed faceted plate, 18 tris: 8-point outline drooping from the base to the tip (LEAF_OUT drops),
    raised midrib (2 vertices, hT above the base plane: a folded dome), one bottom vertex hB below. Leaf axis = azimuth az tilted `tilt` deg up. Top facets
    LEAF_UP when nearly flat, else LEAF; bottom LEAF_DN."""
    rnd = random.Random(seed)
    u = (pol(az, math.cos(math.radians(tilt)), 0) + UP * math.sin(math.radians(tilt))).normalized()
    s = pol(az + 90, 1.0, 0.0); nrm = s.cross(u).normalized()
    if nrm.z < 0: nrm = -nrm
    b = pol(az, base_r, base_z)
    def at(x, y, h, jit=True):
        j = Vector([rnd.uniform(-noise, noise) for _ in range(3)]) if jit else Vector()
        return b + u * (x * L) + s * (y * W) + nrm * h + j
    O = [P.bm.verts.new(at(x, y, h, k != 0)) for k, (x, y, h) in enumerate(LEAF_OUT)]
    M1 = P.bm.verts.new(at(0.32, 0.0, hT)); M2 = P.bm.verts.new(at(0.66, 0.0, hT * 0.72))
    D = P.bm.verts.new(at(0.45, 0.0, -hB, False))
    top = [(O[0], O[1], M1), (O[1], O[2], M1), (O[2], M2, M1), (O[2], O[3], M2), (O[3], O[4], M2),
           (O[0], M1, O[7]), (O[7], M1, O[6]), (O[6], M1, M2), (O[6], M2, O[5]), (O[5], M2, O[4])]
    fs = []
    for tri in top:
        nn = (tri[1].co - tri[0].co).cross(tri[2].co - tri[0].co).normalized()
        if nn.dot(nrm) < 0: nn = -nn
        fs.append(P.face(list(tri), LEAF_UP if nn.z > 0.80 else LEAF))
    for k in range(8):
        fs.append(P.face([O[(k + 1) % 8], O[k], D], LEAF_DN))
    return fs


# ============ layout (measured on the reference, 642 px/m: total 1155 px = 1.80 m) ============
# stems: name -> (base azimuth, mid point (curve passes it at t = 0.5), top-ring point). Bud adds 0.10 above the top.
STEMS = {
    'C': (100, pol(100, 0.05, 0.85), pol(100, 0.06, 1.70)),   # tall, centre-back, near vertical (bud tip 1.80)
    'L': (195, pol(195, 0.22, 0.62), pol(195, 0.29, 1.47)),   # left: leans out low, vertical at the top (bud tip 1.57)
    'R': (345, pol(345, 0.23, 0.55), pol(345, 0.31, 1.29)),   # right, shortest (bud tip 1.39)
}
STEM_BASE_R = 0.04
STEM_R = (0.030, 0.019)                       # Ø0.06 -> Ø0.038
STEM_SEG = 3
STEM_T = [0.0, 0.24, 0.55, 1.0]               # ring parameters: short first segment = the bend sits low, in the leaves
# cups per stem, bottom -> top: (anchor z on the stem axis, azimuth, rim radius). Front = 270.
# z from the reference (cup centres minus ~0.05); zigzag left / right of each stem, facing the viewer (review lesson).
CUPS = {
    'C': [(0.88, 235, 0.074), (1.02, 315, 0.074), (1.16, 235, 0.072), (1.31, 315, 0.072), (1.53, 305, 0.070)],
    'L': [(0.84, 230, 0.074), (0.97, 310, 0.074), (1.10, 230, 0.072), (1.23, 310, 0.072), (1.36, 235, 0.070)],
    'R': [(0.64, 240, 0.074), (0.78, 320, 0.074), (0.91, 240, 0.072), (1.04, 320, 0.072), (1.17, 245, 0.070)],
}
CUP_TILT = 40.0
# leaf plates: (azimuth, tilt deg, L, W, base z, seed). 60 deg apart, front leaf at 270.
LEAVES = [(270, 3, 0.37, 0.35, 0.05, 61), (330, 8, 0.36, 0.34, 0.06, 62), (30, 10, 0.35, 0.33, 0.07, 63),
          (90, 14, 0.34, 0.32, 0.08, 64), (150, 10, 0.35, 0.33, 0.07, 65), (210, 8, 0.37, 0.34, 0.06, 66)]
LEAF_BASE_R = 0.03
LEAF_HT, LEAF_HB = 0.11, 0.045


def stem_axis_at(pts, z):
    for p, q in zip(pts, pts[1:]):
        if p.z <= z <= q.z:
            t = (z - p.z) / (q.z - p.z); return p.lerp(q, t)
    raise ValueError(f'z {z} outside stem')


RIMS = {}


def build_hollyhock():
    P = Part('Body'); comp = {}; RIMS.clear()
    for nm, (baz, mid, top) in STEMS.items():
        pts = bezier_pts(pol(baz, STEM_BASE_R, 0.0), mid, top, STEM_SEG + 1, STEM_T)
        sf, bf = stem_bud(P, pts, taper(*STEM_R, STEM_SEG + 1), baz)
        comp['Stem_' + nm] = sf + bf                      # bud fused on the stem: one shell
        for i, (z, az, rr) in enumerate(CUPS[nm]):
            fs, a, C, R = hollyhock_cup(P, stem_axis_at(pts, z), az, CUP_TILT, rr, spin=math.radians(az) + math.pi / 6)
            comp[f'Cup_{nm}{i}'] = fs
            RIMS[f'Cup_{nm}{i}'] = ('Stem_' + nm, R)
    for i, (az, tilt, L, W, bz, seed) in enumerate(LEAVES):
        comp[f'Leaf_{i}'] = leaf_plate(P, az, LEAF_BASE_R, bz, L, W, tilt, LEAF_HT, LEAF_HB, seed)
    for cn in comp:
        P.comp.append((cn, comp[cn], cn.startswith('Stem_')))
    return P


def overlaps(P, prefix_a, prefix_b):
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    trees = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp
             if nm.startswith(prefix_a) or nm.startswith(prefix_b)}
    out = []; names = sorted(trees)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a.startswith(prefix_a) and b.startswith(prefix_b) or a.startswith(prefix_b) and b.startswith(prefix_a):
                if trees[a].overlap(trees[b]): out.append((a, b))
    return out


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


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
    if bpy.app.background and not LIVE:
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return colls


def atlas_readonly():
    """shared atlas F: load the existing PNG (never generated or saved here); check the cell colours against PAL_F"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None or os.path.normcase(os.path.abspath(bpy.path.abspath(img.filepath))) != os.path.normcase(path):
        img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels[:]); bad = []
    for s, h in enumerate(PAL_F):
        col, row = s % 4, s // 4; x = col * 64 + 32; y = (3 - row) * 64 + 32; i = (y * 256 + x) * 4
        want = [int(h[k:k + 2], 16) for k in (1, 3, 5)]; got = [round(c * 255) for c in px[i:i + 3]]
        if max(abs(a - b) for a, b in zip(want, got)) > 2: bad.append((s, h, got))
    print('  atlas F', path, 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def make_variant(ob, suffix, remap, coll):
    root = bpy.data.objects.new(NAME + suffix, None); coll.objects.link(root)
    me = ob.data.copy(); me.name = NAME + suffix + '_Body'
    uvl = me.uv_layers.active.data
    for p in me.polygons:
        s = cell_of(uvl[p.loop_start].uv); uv = pc.cell_uv(remap.get(s, s))
        for li in p.loop_indices: uvl[li].uv = uv
    vo = bpy.data.objects.new(NAME + suffix + '_Body', me); coll.objects.link(vo); vo.parent = root
    return root, vo


def cup_clearance(P):
    """minimum distance between rims of different cups (no intersecting cups), and leaf/cup overlaps"""
    rims = {}
    for nm, fs, _ in P.comp:
        if nm.startswith('Cup_'): rims[nm] = {v for f in fs for v in f.verts}
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    worst = (9.0, '')
    names = sorted(rims)
    trees = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp
             if nm.startswith('Cup_')}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = min(trees[b].find_nearest(v.co)[3] for v in rims[a])
            if d < worst[0]: worst = (d, f'{a}/{b}')
    print(f'  min cup-to-cup distance {worst[0]:.4f} ({worst[1]})')
    return worst


def rim_check(P):
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    trees = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp
             if nm.startswith('Stem_')}
    worst = (9.0, '')
    for cn, (sn, R) in RIMS.items():
        d = min(trees[sn].find_nearest(v.co)[3] for v in R)
        if d < worst[0]: worst = (d, cn)
    print(f'  min rim-to-own-stem distance {worst[0]:.4f} ({worst[1]})')
    return worst


def build():
    colls = clear_own(); coll = colls[0]
    img, mat = atlas_readonly()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_hollyhock()
    pt = part_tris(P)
    ov_cc = overlaps(P, 'Cup_', 'Cup_'); ov_cl = overlaps(P, 'Cup_', 'Leaf_')
    ov_cs = [(a, b) for a, b in overlaps(P, 'Cup_', 'Stem_') if a[4] != b[5]]
    cup_clearance(P); rim_check(P)
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris):', pt, '| cups touching', ov_cc, '| cup in leaf', ov_cl, '| cup touching a foreign stem', ov_cs)
    var = {suf: make_variant(ob, suf, VARIANTS[suf], c) for suf, c in zip(VARIANTS, colls[1:])}
    return colls, root, ob, img, mat, tot, var


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


# ---------------- renders (temporary scene; copied from PLT-01 / WTR-03) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_PLT06_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_PLT06_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_PLT06_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_PLT06_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_PLT06_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_PLT06_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_PLT06_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
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


def save_lib(path, colls, mat, img):
    data = set(colls) | {mat, img}
    for c in colls: data |= set(c.objects) | {o.data for o in c.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


VIEW_REF = (0.0, -math.cos(math.radians(25)), math.sin(math.radians(25)))     # reference: front, ~25 deg above
VIEW_PREVIEW = (1.0, -1.25, 0.75)                                               # series preview 3/4 (~25 deg)
VIEW_BACK = (-0.6, 1.0, 0.45)                                                   # back 3/4 (all-round read)

colls, root, ob, img, mat, tot, var = build()
os.makedirs(CHECK_DIR, exist_ok=True)
base_objs = [root, ob]
tag = 'live' if LIVE else 'headless'
if MODE == 'build':
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-06_check_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.62, fill_h=0.92, lens=None)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-06_check34_{tag}.png'), VIEW_PREVIEW)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-06_checkback_{tag}.png'), VIEW_BACK)
    vr, vo = var['_White']
    render([vr, vo], os.path.join(CHECK_DIR, f'PLT-06_check34_White_{tag}.png'), VIEW_PREVIEW)
if MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    vl = bpy.context.view_layer                                  # live: the owner's selection is saved and restored
    sel = [o.name for o in vl.objects if o.select_get()]; act = vl.objects.active.name if vl.objects.active else None
    try:
        fbxs = [pc.export(NAME, colls[0], root, os.path.join(ART, 'Meshes', NAME + '.fbx'))]
        for (suf, (vr, vo)), c in zip(var.items(), colls[1:]):
            fbxs.append(pc.export(NAME + suf, c, vr, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
    finally:
        for o in vl.objects: o.select_set(o.name in sel)
        vl.objects.active = vl.objects[act] if act and act in vl.objects else None
        print('  selection restored', sel, act)
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
    render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    for f in fbxs: pc.verify(f)
if MODE in ('export', 'dump'):
    geom_dump([ob] + [vo for _, vo in var.values()],
              os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
