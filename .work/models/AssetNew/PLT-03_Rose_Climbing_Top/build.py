# build.py - PLT-03 Climbing Rose, Top garland (FMS_Garden_Rose_Climbing_Top + _Pink), pack AssetNew (Cottage Garden
# Decor), atlas F Garden_Flora (read only: the shared PNG is loaded, never rewritten).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- PLT-03 build|export
#   build  = build + printed checks (+ SNAP) + check renders to %TEMP%/assetnew_check/PLT-03/ (headless also renders the
#            garland mounted on the exported STR-01 arch FBX)
#   export = build + 2 FBX (base, _Pink; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 of both meshes incl. UV cells)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\PLT-03_Rose_Climbing_Top\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['PLT-03', 'build']})
#   Live mode touches only the collection PLT-03_Rose_Climbing_Top and its variant child collection.
#
# Axes (Blender): X = length (1.6), -Y = front (Unity +Z with the -Z-forward FBX export), Z = up (Unity Y).
# Underside Blender Z = 0 (Unity Y = 0) = ATTACHMENT PLANE: nothing below it. Pivot (0, 0, 0) = centre of the underside.
# Organic generators copied unchanged from PLT-02 / PLT-01 build.py (PLT-01 accepted pass 3): ring, bridge, leaf_cluster,
# add_bmesh, rose_bloom_v2, closed_bud, leaf, top_hit, inside.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'PLT-03')
COLL = 'PLT-03_Rose_Climbing_Top'
NAME = 'FMS_Garden_Rose_Climbing_Top'
PREVIEW = 'FMS_Garden_PLT_03_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'
ATLAS_MAT = 'M_Garden_Flora'
ARCH_FBX = 'FMS_Garden_Arch_Wood.fbx'          # STR-01, mounting check render only (read)
BUDGET = 1100                                  # owner note 2026-11-25 (was 700)
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
CUP, BUD, BARK, SEPAL = 4, 5, 13, 0
VARIANTS = {'_Pink': {CUP: 7, BUD: 6}}        # spec: cup slot 7, bud slot 6; foliage and canes unchanged
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'PLT-03'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi


# ============ organic generators (copied from PLT-01 build.py, unchanged) ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def bridge(P, A, angA, B, angB, slot):
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
    slots = {f: (LEAF_UP if f.normal.z > up else (LEAF_DN if f.normal.z < down else LEAF)) for f in bm.faces}
    return bm, slots


def add_bmesh(P, cname, bm, slots, comp):
    vm = {v: P.bm.verts.new(v.co) for v in bm.verts}
    comp[cname] = [P.face([vm[v] for v in f.verts], slots[f]) for f in bm.faces]


def rose_bloom_v2(P, p, a, spin=0.0, depth=0.05, neck=0.02,
                  r_base=0.035, r_rim=0.058, h_rim=0.05,
                  r_in0=0.030, h_in0=0.015, r_in1=0.040, h_in1=0.045,
                  r_bud=0.018, h_bud=0.030, h_tip=0.060, twist=math.pi / 6,
                  slot_calyx=SEPAL, slot_outer=CUP, slot_inner=BUD):
    """ROSE BLOOM v2 (PLT-01 Fix 2): one closed shell, 68 tris, rim 0.116, cup height 0.05."""
    a = Vector(a).normalized(); p = Vector(p); O = p + a * neck
    def rg(r, h, n, a0): return [P.bm.verts.new(v) for v in ring(O + a * h, a, r, n, spin + a0)[0]], \
        [spin + a0 + TAU * k / n for k in range(n)]
    apex = P.bm.verts.new(p - a * depth); tip = P.bm.verts.new(O + a * h_tip)
    B, aB = rg(r_base, 0.0, 8, 0.0)
    R, aR = rg(r_rim, h_rim, 8, math.pi / 8)
    I, aI = rg(r_in0, h_in0, 6, 0.0)
    J, aJ = rg(r_in1, h_in1, 6, twist)
    K, aK = rg(r_bud, h_bud, 6, 2 * twist)
    f = [P.face([apex, B[(k + 1) % 8], B[k]], slot_calyx) for k in range(8)]
    f += bridge(P, B, aB, R, aR, slot_outer) + bridge(P, R, aR, I, aI, slot_outer)
    f += bridge(P, I, aI, J, aJ, slot_inner) + bridge(P, J, aJ, K, aK, slot_inner)
    f += [P.face([K[k], K[(k + 1) % 6], tip], slot_inner) for k in range(6)]
    return f


def closed_bud(P, p, a, spin=0.0, depth=0.03, r=0.022, h_ring=0.025, h_tip=0.065, n=6, slot_calyx=SEPAL, slot_bud=BUD):
    a = Vector(a).normalized(); p = Vector(p)
    lo = P.bm.verts.new(p - a * depth); hi = P.bm.verts.new(p + a * h_tip)
    Rg = [P.bm.verts.new(v) for v in ring(p + a * h_ring, a, r, n, spin)[0]]
    return [P.face([lo, Rg[(k + 1) % n], Rg[k]], slot_calyx) for k in range(n)] + \
           [P.face([Rg[k], Rg[(k + 1) % n], hi], slot_bud) for k in range(n)]


def leaf(P, base, d, L=0.10, W=0.045, T=0.016, slot_top=LEAF, slot_bot=LEAF_DN):
    d = Vector(d).normalized(); up = Vector((0, 0, 1))
    side = d.cross(up); side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    nrm = side.cross(d).normalized()
    b = Vector(base); m = b + d * (L * 0.45)
    V = [P.bm.verts.new(q) for q in (b, m + side * W / 2, b + d * L, m - side * W / 2, m + nrm * T, m - nrm * T)]
    vb, vl, vt, vr, vu, vd = V
    return [P.face([vb, vl, vu], slot_top), P.face([vl, vt, vu], slot_top), P.face([vt, vr, vu], slot_top),
            P.face([vr, vb, vu], slot_top), P.face([vb, vd, vl], slot_bot), P.face([vl, vd, vt], slot_bot),
            P.face([vt, vd, vr], slot_bot), P.face([vr, vd, vb], slot_bot)]


def top_hit(bvh, c, offs):
    return bvh.ray_cast(Vector(c) + Vector(offs) + Vector((0, 0, 1)), Vector((0, 0, -1)))[0]


def inside(bvh, q):
    n_hit = 0; o = Vector(q)
    for _ in range(12):
        h = bvh.ray_cast(o + Vector((0, 0, 1e-5)), Vector((0, 0, 1)))
        if h[0] is None: break
        n_hit += 1; o = h[0]
    return n_hit % 2 == 1


# ============ PLT-03 specific ============
def flat_cluster(c, D, seed, H, kd, clip):
    """LEAF CLUSTER of PLT-01 (80 tris), depth (Blender Y) scaled by kd around the centre, the part below the attachment
    plane pressed flat onto Z = clip (vertices clamped, no new faces: the bottom cap is a graph over the plane, so the
    clamp cannot fold faces). Slots recomputed from the final normals."""
    bm, _ = leaf_cluster(c, D, seed, H=H)
    cy = Vector(c).y
    for v in bm.verts:
        v.co.y = cy + (v.co.y - cy) * kd
        v.co.z = max(v.co.z, clip)
    bm.normal_update()
    slots = {f: (LEAF_UP if f.normal.z > 0.6 else (LEAF_DN if f.normal.z < -0.2 else LEAF)) for f in bm.faces}
    return bm, slots


def cane(P, pts, radii, n=6):
    """n-sided tapered prism along pts, mitred rings; ring vertex 0 points DOWN (-Z), so a cane resting on the attachment
    plane touches it with one edge line (no coplanar faces). Both ends capped (closed)."""
    pts = [Vector(q) for q in pts]; rings = []
    for i, q in enumerate(pts):
        if i == 0: d = pts[1] - pts[0]
        elif i == len(pts) - 1: d = pts[-1] - pts[-2]
        else: d = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        rings.append(ring(q, d, radii[i], n, 0.0, ref=(0, 0, -1))[0])
    R = [[P.bm.verts.new(v) for v in r] for r in rings]; faces = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], BARK))
    faces.append(P.face(list(reversed(R[0])), BARK)); faces.append(P.face(list(R[-1]), BARK))
    return faces


# canes: two strands braided along X as straight diagonals (triangle wave). Seen from the front they cross as a steep X
# every half period (z weave, the reference look: crossings in the gaps between the front clusters, under the back
# clusters); in depth they pass each other front/back alternately (y weave), so they never intersect. The turning
# points lie inside the front clusters and are chamfered (two rings +-CANE_CH instead of one sharp corner).
CANE_X = 0.66                                  # cane ends at x = +-CANE_X (inside clusters C1 / C5)
CANE_R = (0.0275, 0.0225)                      # Ø0.055 -> Ø0.045 (spec >= 0.04; reference ~0.055), thick end left for A, right for B
PERIOD, X_CROSS = 0.60, -0.30                  # crossings at x -0.6, -0.3, 0, 0.3, 0.6 (visible ones: reference ~-0.31 / +0.28)
LIFT, YW = 0.16, 0.045                         # z swing (front X crossings) and depth swing (+-, over the beam)
CANE_CH = 0.035                                # chamfer half-width at the turning points
CANE_XS = [-CANE_X] + [t + d for t in (-0.45, -0.15, 0.15, 0.45) for d in (-CANE_CH, CANE_CH)] + [CANE_X]   # 10 rings


def tri_wave(u):
    """triangle 'sine': 0 at u = 0, +1 at 0.25, 0 at 0.5, -1 at 0.75 (period 1)"""
    return 4 * abs(((u - 0.25) % 1.0) - 0.5) - 1


def cane_pt(x, s, r):
    u = (x - X_CROSS) / PERIOD
    z = r + LIFT * 0.5 * (1 + s * tri_wave(u))
    y = -s * YW * (1 if tri_wave(u + 0.25) >= 0 else -1)   # ring points only: front/back by the nearest crossing
    return Vector((x, y, z))


# clusters: name -> (x, y centre, z mid, D, H (height / D), seed). Measured on the reference (727 px/m, front view
# ~12 deg above): front row C1/C3/C5 low (top ~0.29, flat bottom on the plane), back row C2/C4 raised on the canes
# (bottom ~0.10, top ~0.44; the cane crossings show under them as in the reference), D 0.42-0.45.
CLUSTERS = {
    'C1': (-0.590, -0.085, 0.140, 0.42, 0.72, 41),
    'C2': (-0.250, 0.085, 0.270, 0.45, 0.75, 42),
    'C3': (-0.015, -0.090, 0.145, 0.42, 0.72, 43),
    'C4': (0.285, 0.085, 0.270, 0.45, 0.75, 44),
    'C5': (0.550, -0.080, 0.140, 0.42, 0.72, 45),
}
CL_KD = 0.80                                   # depth scale of the clusters
CLIP0, CLIP_STEP = 0.010, 0.0015               # flattened bottoms at 0.010, 0.0115, ... (no coplanar bottoms)
# blooms on cluster tops: (cluster, dx, front offset (toward -Y), tilt to the front deg, lean outward (+X away from 0) deg)
BLOOMS = [('C1', -0.075, -0.02, 18, 12), ('C1', 0.085, 0.07, 24, 6), ('C2', 0.010, 0.05, 20, 4),
          ('C3', 0.025, 0.06, 24, 0), ('C4', 0.025, 0.05, 20, 4), ('C5', 0.025, 0.06, 22, 12)]
BLOOM_NECK, BLOOM_DEPTH, BLOOM_K = 0.045, 0.07, 1.25     # rim 0.145 (reference ~0.16), visible green neck
BLOOM_SIZE = {k: v * BLOOM_K for k, v in dict(r_base=0.035, r_rim=0.058, h_rim=0.05, r_in0=0.030, h_in0=0.015, r_in1=0.040,
              h_in1=0.045, r_bud=0.018, h_bud=0.030, h_tip=0.060).items()}
BUDS = [('C2', 0.105, 0.02, 12, 1), ('C4', -0.100, 0.02, 12, -1)]   # closed buds: (cluster, dx, front offset, tilt, side)


def build_rose():
    P = Part('Body'); comp = {}
    bvh = {}
    for i, (nm, (x, y, z, D, H, seed)) in enumerate(CLUSTERS.items()):
        bm, slots = flat_cluster((x, y, z), D, seed, H, CL_KD, CLIP0 + CLIP_STEP * i)
        bvh[nm] = BVHTree.FromBMesh(bm)
        add_bmesh(P, 'Cluster_' + nm, bm, slots, comp); bm.free()
    for nm, s in (('A', 1), ('B', -1)):
        xs = CANE_XS
        rs = [CANE_R[0] + (CANE_R[1] - CANE_R[0]) * (x + CANE_X) / (2 * CANE_X) for x in xs]
        if s < 0: rs = rs[::-1]
        v0 = len(P.bm.verts)
        comp['Cane_' + nm] = cane(P, [cane_pt(x, s, r) for x, r in zip(xs, rs)], rs)
        P.bm.verts.ensure_lookup_table()
        vs = [P.bm.verts[k] for k in range(v0, len(P.bm.verts))]
        dz = min(v.co.z for v in vs)                          # lowest edge exactly on the attachment plane
        for v in vs: v.co.z -= dz
    for i, (cn, dx, fy, tilt, lean) in enumerate(BLOOMS):
        x, y, z, D, H, s = CLUSTERS[cn]
        out = 1 if x + dx > 0.05 else (-1 if x + dx < -0.05 else 0)
        hit = top_hit(bvh[cn], (x, y, z), (dx, -fy, 0))
        a = Matrix.Rotation(math.radians(out * lean), 3, 'Y') @ (Matrix.Rotation(math.radians(tilt), 3, 'X') @ Vector((0, 0, 1)))
        a = Vector((a.x, -abs(a.y), a.z))
        comp[f'Bloom_{cn}{i}'] = rose_bloom_v2(P, hit, a, spin=0.2 * i, depth=BLOOM_DEPTH, neck=BLOOM_NECK, **BLOOM_SIZE)
        if not inside(bvh[cn], hit - a * (BLOOM_DEPTH - 0.005)): print(f'  WARNING bloom {cn}{i}: calyx apex outside its cluster')
    for i, (cn, dx, fy, tilt, side) in enumerate(BUDS):
        x, y, z, D, H, s = CLUSTERS[cn]
        hit = top_hit(bvh[cn], (x, y, z), (dx, -fy, 0))
        a = Matrix.Rotation(math.radians(side * 10), 3, 'Y') @ (Matrix.Rotation(math.radians(tilt), 3, 'X') @ Vector((0, 0, 1)))
        a = Vector((a.x, -abs(a.y), a.z))
        comp[f'Bud_{cn}{i}'] = closed_bud(P, hit, a, spin=0.5 * i, depth=0.03, r=0.034, h_ring=0.055, h_tip=0.125)
        if not inside(bvh[cn], hit - a * 0.025): print(f'  WARNING bud {cn}{i}: base outside its cluster')
    print('  blooms', len(BLOOMS), '| buds', len(BUDS), '| clusters', len(CLUSTERS))
    for cn in list(comp):
        P.comp.append((cn, comp[cn], False))
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
    if mat is None:                                                   # headless: same setup as PLT-01
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
        s = cell_of(uvl[p.loop_start].uv)
        uv = pc.cell_uv(remap.get(s, s))
        for li in p.loop_indices: uvl[li].uv = uv
    vo = bpy.data.objects.new(NAME + suffix + '_Body', me); coll.objects.link(vo); vo.parent = root
    return root, vo


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def snap_checks(ob):
    """attachment plane + mounting numbers (spec 'Mounting', CATALOG 'Модули и стыковка' 7 and the STR-04 beam).
    STR-01 top measured on the exported FMS_Garden_Arch_Wood.fbx: X -0.80..0.80, beam tops Y -0.335..0.335 at z 2.40,
    Plant_Top empty at (0, 0, 2.40)."""
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    W, Dp = x1 - x0, y1 - y0
    low = [p for p in pts if p.z < 0.0005]
    me = ob.data; uv = me.uv_layers.active.data
    cane_c = [ob.matrix_world @ me.vertices[i].co for p in me.polygons if cell_of(uv[p.loop_start].uv) == BARK for i in p.vertices]
    cy = max(abs(p.y) for p in cane_c)
    rows = [
        ('nothing below the attachment plane (min z >= 0)', z0, z0 >= -1e-6),
        ('attachment plane touched (min z = 0, cane edges)', len(low), abs(z0) <= 1e-6 and len(low) >= 2),
        ('STR-01 top: length <= 1.60 (= arch top width) and >= 1.55', W, 1.55 <= W <= 1.60 + 1e-6),
        ('pivot X centred (|x0 + x1| / 2 <= 0.02)', (x0 + x1) / 2, abs(x0 + x1) / 2 <= 0.02),
        ('STR-01 top: depth <= 0.60 (catalogue) and inside the beam tops |y| <= 0.335', Dp, Dp <= 0.60 + 1e-6 and max(-y0, y1) <= 0.335),
        ('pivot Y centred (|y0 + y1| / 2 <= 0.03)', (y0 + y1) / 2, abs(y0 + y1) / 2 <= 0.03),
        ('STR-04 beam 0.10 wide: canes over the beam (max |y| of cane surface <= 0.05 + cane r 0.025)', cy, cy <= 0.075 + 1e-6),
        ('STR-04 beam: length 1.6 < beam 3.5', W, W < 3.5),
    ]
    ok = all(r[2] for r in rows)
    for nm, v, g in rows: print(f'  SNAP {nm}: {v:.4f} {"OK" if g else "FAIL"}')
    print(f'  height {z1:.3f} (catalogue 0.40, reference ~0.55)')
    print('SNAP OK' if ok else 'SNAP FAIL')
    return ok


def build():
    colls = clear_own(); coll = colls[0]
    img, mat = atlas_readonly()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_rose()
    pt = part_tris(P)
    ov_cc = overlaps(P, 'Cluster_', 'Cluster_'); ov_bb = overlaps(P, 'Bloom_', 'Bloom_')
    ov_bc = [(a, b) for a, b in overlaps(P, 'Bloom_', 'Cluster_') if b.startswith('Cluster_') and a[6:8] != b[8:]]
    ov_aa = overlaps(P, 'Cane_A', 'Cane_B')
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    n_cop, _ = pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris):', pt, '| clusters touching', ov_cc, '| blooms touching', ov_bb, '| bloom in foreign cluster', ov_bc,
          '| canes intersecting', ov_aa)
    snap_checks(ob)
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
    sc = bpy.data.scenes.new('TMP_PLT03_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_PLT03_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_PLT03_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_PLT03_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_PLT03_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_PLT03_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_PLT03_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


def mount_render(out):
    """headless only: the garland on top of the exported STR-01 arch (Plant_Top 0, 0, 2.40), view from the front 3/4"""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(ART, 'Meshes', ARCH_FBX))
    arch = [o for o in bpy.data.objects if o not in before]
    top = next((o for o in arch if o.name.startswith('Plant_Top')), None)
    zt = top.matrix_world.translation.z if top else 2.40
    print('  STR-01 Plant_Top z', round(zt, 4))
    g = bpy.data.objects.new('TMP_PLT03_Mounted', ob.data); g.matrix_world = Matrix.Translation((0, 0, zt))
    bpy.context.view_layer.update()
    render([o for o in arch if o.type == 'MESH'] + [g], out, (0.9, -1.6, 0.55), res=(1000, 1100), fill_w=0.8, fill_h=0.9)
    bpy.data.objects.remove(g, do_unlink=True)
    for o in arch: bpy.data.objects.remove(o, do_unlink=True)


VIEW_REF = (0.0, -1.0, 0.21)                                                    # reference: front, ~12 deg above
VIEW_PREVIEW = (1.0, -1.25, 0.75)                                               # series preview 3/4 (~25 deg)

colls, root, ob, img, mat, tot, var = build()
os.makedirs(CHECK_DIR, exist_ok=True)
base_objs = [root, ob]
if MODE == 'build':
    tag = 'live' if LIVE else 'headless'
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-03_check_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.93, fill_h=0.9)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-03_check34_{tag}.png'), VIEW_PREVIEW)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-03_checktop_{tag}.png'), (0.0, -0.25, 1.0), res=(1280, 800), fill_w=0.9)
    pv = [var['_Pink'][0], var['_Pink'][1]]
    render(pv, os.path.join(CHECK_DIR, f'PLT-03_check34_pink_{tag}.png'), VIEW_PREVIEW)
    if not LIVE: mount_render(os.path.join(CHECK_DIR, 'PLT-03_check_mounted_headless.png'))
if MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbxs = [pc.export(NAME, colls[0], root, os.path.join(ART, 'Meshes', NAME + '.fbx'))]
    for (suf, (vr, vo)), c in zip(var.items(), colls[1:]):
        fbxs.append(pc.export(NAME + suf, c, vr, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
    render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    for f in fbxs: pc.verify(f)
if MODE in ('export', 'dump'):
    geom_dump([ob] + [vo for _, vo in var.values()],
              os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
