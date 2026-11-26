# build.py - PLT-01 Rose Bush (FMS_Garden_Rose_Bush + _Pink, _White), pack CottageGardenDecor (Cottage Garden Decor), atlas F Garden_Flora.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- PLT-01 build|export
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/PLT-01/
#   export = build + 3 FBX (base, _Pink, _White; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 of all three meshes incl. UV cells)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\PLT-01_Rose_Bush\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['PLT-01', 'build']})
#   Live mode touches only the collection PLT-01_Rose_Bush and its two variant child collections.
#
# Reusable organic generators (PLT-02/03/06, TOP-01_Rose) - plain parametric functions, copy them (do not import across
# item folders): leaf_cluster() + add_bmesh(), rose_bloom_v2(), closed_bud(), leaf() / leaf_tuft(), bezier_pts() + stem()
# + taper(), ring() / bridge(). Placement helpers: top_hit(), inside(). Dependencies: pack_common (Part, basis), the slot
# constants LEAF/LEAF_UP/LEAF_DN/CUP/BUD/BARK/SEPAL and TAU.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'PLT-01')
COLL = 'PLT-01_Rose_Bush'
NAME = 'FMS_Garden_Rose_Bush'
PREVIEW = 'FMS_Garden_PLT_01_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'          # atlas F (Garden_Flora), cell layout in notes.md
ATLAS_MAT = 'M_Garden_Flora'
BUDGET = 2000                                 # Fix 2 (owner 2026-11-25): was 1000
# atlas F palette, STYLE.md (slot = cell index; row-major from the top-left of the PNG)
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
CUP, BUD, BARK, SEPAL = 4, 5, 13, 0
# colour variants: same mesh, UV cells remapped (spec table)
VARIANTS = {'_Pink': {CUP: 7, BUD: 6}, '_White': {CUP: 8, BUD: 8}}
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'PLT-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi


def pol(az, r, z):
    a = math.radians(az)
    return Vector((r * math.cos(a), r * math.sin(a), z))


# ============ reusable organic generators ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    """n points around axis a through O, radius r, start angle a0 (radians, in the e1/e2 frame of pc.basis)."""
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def bridge(P, A, angA, B, angB, slot):
    """Triangle strip between two closed rings of different vertex counts (both CCW in the same frame), zipped by angle.
    Returns the faces; winding is fixed later by recalc_face_normals (closed shells)."""
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
    """LEAF CLUSTER v2 (Fix 2): faceted domed foliage 'drop', a FULL ico sphere (bpy subdivisions=sub: 2 -> 80 tris,
    closed, no cut), random Z spin by the seed. Each vertex is re-profiled from its original height zo in [-1, 1]:
    the equator becomes the widest ring at `widest` of the height, the upper half a dome (no flat top), the lower half a
    rounded underside pulled in by under_k; then every vertex is displaced +-noise (fixed seed) for a bumpy outline.
    Width ~D, height H*D, centre c = mid-height. Returns a temp bmesh (world space) and per-face slots
    (normal up -> LEAF_UP, sideways -> LEAF, down -> LEAF_DN)."""
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
    """ROSE BLOOM v2 (Fix 2), ONE closed shell, 68 tris, rim Ø 2*r_rim (0.116), cup height h_rim (0.05): wider than tall.
    Revolved profile around axis a from the cup bottom O = p + a*neck (p = anchor on the foliage / shoot tip):
      calyx cone  apex (p - a*depth, buried) -> 8-ring r_base at O                       8 tris  slot_calyx
      outer petals 8-ring -> 8-ring rim r_rim at h_rim, rim rotated 22.5 deg -> petal tips  16 tris  slot_outer
      inside of the outer petals: rim -> inner 6-ring r_in0 at h_in0                      14 tris  slot_outer
      inner petal ring (6-sided cup, offset `twist` = 30 deg): r_in0 -> r_in1 at h_in1     12 tris  slot_inner
      inside of the inner cup -> 6-ring bud base r_bud at h_bud, twisted again            12 tris  slot_inner
      spiral bud cone -> tip at h_tip (0.01 above the rim)                                  6 tris  slot_inner
    The profile (r, h) never crosses itself, so the shell is closed and manifold. Colour variants remap slot_outer
    (outer petals) and slot_inner (inner petals + bud). Returns the faces."""
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
    """Closed rose bud: n-sided bipyramid on the anchor p, green lower cone (apex buried `depth`), red upper cone. 2n tris."""
    a = Vector(a).normalized(); p = Vector(p)
    lo = P.bm.verts.new(p - a * depth); hi = P.bm.verts.new(p + a * h_tip)
    Rg = [P.bm.verts.new(v) for v in ring(p + a * h_ring, a, r, n, spin)[0]]
    return [P.face([lo, Rg[(k + 1) % n], Rg[k]], slot_calyx) for k in range(n)] + \
           [P.face([Rg[k], Rg[(k + 1) % n], hi], slot_bud) for k in range(n)]


def leaf(P, base, d, L=0.10, W=0.045, T=0.016, slot_top=LEAF, slot_bot=LEAF_DN):
    """One faceted closed leaf (8 tris): rhombus base -> tip in direction d, width W at 45 % of L, ridge +-T."""
    d = Vector(d).normalized(); up = Vector((0, 0, 1))
    side = d.cross(up); side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    nrm = side.cross(d).normalized()
    b = Vector(base); m = b + d * (L * 0.45)
    V = [P.bm.verts.new(q) for q in (b, m + side * W / 2, b + d * L, m - side * W / 2, m + nrm * T, m - nrm * T)]
    vb, vl, vt, vr, vu, vd = V
    return [P.face([vb, vl, vu], slot_top), P.face([vl, vt, vu], slot_top), P.face([vt, vr, vu], slot_top),
            P.face([vr, vb, vu], slot_top), P.face([vb, vd, vl], slot_bot), P.face([vl, vd, vt], slot_bot),
            P.face([vt, vd, vr], slot_bot), P.face([vr, vd, vb], slot_bot)]


def leaf_tuft(P, anchor, out, n=3, spread=40.0, lift=0.9, sink=0.015, L=0.15, W=0.065, seed=0):
    """Loose tuft of n leaves fanning from a point `sink` inside the foliage, around direction out (+ lift up)."""
    rnd = random.Random(seed); out = Vector(out).normalized(); faces = []
    for k in range(n):
        ang = math.radians(-spread + 2 * spread * k / max(1, n - 1) + rnd.uniform(-8, 8))
        d = Matrix.Rotation(ang, 3, 'Z') @ out; d.z += lift + rnd.uniform(-0.15, 0.15)
        faces += leaf(P, Vector(anchor) - d.normalized() * sink, d, L=L * rnd.uniform(0.85, 1.1), W=W)
    return faces


def bezier_pts(p0, pm, p2, n):
    """n points of the quadratic Bezier that starts at p0, passes through pm at t = 0.5 and ends at p2."""
    p0, pm, p2 = Vector(p0), Vector(pm), Vector(p2); c = 2 * pm - (p0 + p2) / 2
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t * t * p2 for t in (i / (n - 1) for i in range(n))]


def stem(P, pts, radii, n=8, az=0.0, slot=BARK):
    """Tapered n-sided prism along a polyline (use bezier_pts for a smooth bend), rings perpendicular to the averaged
    tangent (mitred), both ends capped (closed shell). Ring frames use the outward horizontal direction az (no twist)."""
    pts = [Vector(q) for q in pts]; ref = pol(az, 1.0, 0.0)
    rings = []
    for i, q in enumerate(pts):
        if i == 0: d = pts[1] - pts[0]
        elif i == len(pts) - 1: d = pts[-1] - pts[-2]
        else: d = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        rings.append(ring(q, d, radii[i], n, 0.0, ref)[0])
    R = [[P.bm.verts.new(v) for v in r] for r in rings]; faces = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], slot))
    faces.append(P.face(list(reversed(R[0])), slot)); faces.append(P.face(list(R[-1]), slot))
    return faces


def taper(r0, r1, n):
    return [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]


# ============ PLT-01 layout (Blender: X right, -Y front = reference view, Z up) ============
# clusters: name -> (azimuth deg, radius from axis, centre z, width D, seed). 3 lower + 5 upper.
# Fix 2: lower tier lifted ~0.06 and moved outward so the stem fan shows in the 3/4 view.
CLUSTERS = {
    'T':  (90, 0.08, 0.86, 0.32, 11),
    'TL': (160, 0.32, 0.78, 0.36, 12),
    'TR': (20, 0.32, 0.79, 0.36, 13),
    'ML': (215, 0.28, 0.64, 0.36, 14),
    'MR': (322, 0.28, 0.65, 0.36, 15),
    'L':  (192, 0.34, 0.46, 0.34, 16),
    'R':  (348, 0.34, 0.46, 0.34, 17),
    'C':  (255, 0.27, 0.47, 0.34, 18),
}
# stems: name -> (base azimuth, mid point (curve passes it at t=0.5), end cluster). 6 curved 8-sided stems, 4 segments.
STEMS = {
    'T':  (120, pol(115, 0.15, 0.42), 'T'),
    'TL': (180, pol(188, 0.27, 0.42), 'TL'),
    'TR': (0, pol(352, 0.27, 0.42), 'TR'),
    'ML': (215, pol(215, 0.20, 0.36), 'ML'),
    'MR': (322, pol(322, 0.20, 0.37), 'MR'),
    'C':  (258, pol(256, 0.17, 0.28), 'C'),
}
STEM_SEG = 4                                 # 4 segments (5 rings) per stem
STEM_R = (0.025, 0.015)                      # Ø0.05 -> Ø0.03
STEM_BASE_R, STEM_BASE_Z = 0.03, 0.05        # stem bases inside the stump (stump top z 0.10)
# side shoots: (parent stem, t on parent, mid point, end point). 6-sided, 2 segments, each ends in a bloom.
SHOOTS = {
    'S1': ('TR', 0.70, pol(45, 0.34, 0.86), pol(58, 0.38, 0.97)),
    'S2': ('ML', 0.70, pol(232, 0.36, 0.66), pol(240, 0.44, 0.76)),
}
SHOOT_R = (0.016, 0.0125)
# blooms on clusters: (cluster, tangential offset, radial offset, tilt deg outward, extra tilt along the tangent deg)
BLOOMS = [
    ('T', 0.0, 0.0, 12, 0), ('TL', 0.0, 0.03, 14, 0), ('TR', -0.03, 0.02, 14, 0),
    ('ML', 0.0, 0.04, 25, 0), ('MR', 0.0, 0.04, 25, 0),
    ('L', 0.03, 0.08, 28, 0), ('R', -0.03, 0.08, 28, 0), ('C', 0.0, 0.05, 22, 0),
]
# closed buds: (cluster, tangential offset, radial offset, tilt)
BUDS = [('L', -0.09, 0.03, 20), ('MR', 0.08, 0.02, 18)]
# leaf tufts: (cluster, azimuth offset deg from the cluster's outward direction, seed)
TUFTS = [('TL', 30, 21), ('MR', -35, 22), ('C', 40, 23)]


def cpos(name):
    az, r, z, D, s = CLUSTERS[name]; return pol(az, r, z)


def top_hit(bvh, c, offs):
    return bvh.ray_cast(Vector(c) + Vector(offs) + Vector((0, 0, 1)), Vector((0, 0, -1)))[0]


def inside(bvh, q):
    n_hit = 0; o = Vector(q)
    for _ in range(12):
        h = bvh.ray_cast(o + Vector((0, 0, 1e-5)), Vector((0, 0, 1)))
        if h[0] is None: break
        n_hit += 1; o = h[0]
    return n_hit % 2 == 1


def build_rose_bush():
    P = Part('Body'); comp = {}
    # stump: 8-sided frustum Ø0.12 -> Ø0.10, z 0..0.10, both caps (closed)
    P.loft('Stump', [[Vector((x, y, 0.0)) for x, y in pc.ngon(0.06, 8, math.pi / 8)],
                     [Vector((x, y, 0.10)) for x, y in pc.ngon(0.05, 8, math.pi / 8)]], BARK, BARK, BARK, ground=True)
    bvh = {}
    for nm, (az, r, z, D, seed) in CLUSTERS.items():
        bm, slots = leaf_cluster(pol(az, r, z), D, seed)
        bvh[nm] = BVHTree.FromBMesh(bm)
        add_bmesh(P, 'Cluster_' + nm, bm, slots, comp); bm.free()
    curves = {}
    for nm, (baz, mid, tip) in STEMS.items():
        pts = bezier_pts(pol(baz, STEM_BASE_R, STEM_BASE_Z), mid, cpos(tip), STEM_SEG + 1)
        curves[nm] = (pts, baz)
        comp['Stem_' + nm] = stem(P, pts, taper(*STEM_R, STEM_SEG + 1), n=8, az=baz)
    nb = 0
    for nm, (par, t, mid, end) in SHOOTS.items():
        baz = curves[par][1]
        # point on the parent curve at parameter t (re-evaluate the parent Bezier)
        az0, mid0, tip0 = STEMS[par]
        q0, qm, q2 = pol(az0, STEM_BASE_R, STEM_BASE_Z), Vector(mid0), cpos(tip0); cc = 2 * qm - (q0 + q2) / 2
        p0 = (1 - t) ** 2 * q0 + 2 * (1 - t) * t * cc + t * t * q2
        pts = bezier_pts(p0, mid, end, 3)
        comp['Shoot_' + nm] = stem(P, pts, taper(*SHOOT_R, 3), n=6, az=baz)
        a = (pts[-1] - pts[-2]).normalized()
        comp[f'Bloom_{nm}'] = rose_bloom_v2(P, pts[-1], a, spin=0.3, depth=0.02, neck=0.012); nb += 1
        side = a.cross(Vector((0, 0, 1))).normalized()                  # two leaves along the shoot
        q1 = pts[1].lerp(pts[2], 0.45); q2 = pts[1].lerp(pts[2], 0.15)
        comp[f'Leaf_{nm}'] = leaf(P, q1, side + a * 0.7, L=0.11, W=0.05) + leaf(P, q2, -side + a * 0.6, L=0.10, W=0.05)
    for i, (cn, dt, dr, tilt, ttan) in enumerate(BLOOMS):
        az, r, z, D, s = CLUSTERS[cn]
        out = pol(az, 1.0, 0.0); tan = pol(az + 90, 1.0, 0.0)
        hit = top_hit(bvh[cn], cpos(cn), out * dr + tan * dt)
        a = (Matrix.Rotation(math.radians(tilt), 3, tan) @ Matrix.Rotation(math.radians(-ttan), 3, out)) @ Vector((0, 0, 1))
        comp[f'Bloom_{cn}{i}'] = rose_bloom_v2(P, hit, a, spin=math.radians(az)); nb += 1
        if not inside(bvh[cn], hit - a * 0.05): print(f'  WARNING bloom {cn}{i}: calyx apex outside its cluster')
    for i, (cn, dt, dr, tilt) in enumerate(BUDS):
        az, r, z, D, s = CLUSTERS[cn]
        out = pol(az, 1.0, 0.0); tan = pol(az + 90, 1.0, 0.0)
        hit = top_hit(bvh[cn], cpos(cn), out * dr + tan * dt)
        a = Matrix.Rotation(math.radians(tilt), 3, tan) @ Vector((0, 0, 1))
        comp[f'Bud_{cn}{i}'] = closed_bud(P, hit, a, spin=math.radians(az))
        if not inside(bvh[cn], hit - a * 0.03): print(f'  WARNING bud {cn}{i}: base outside its cluster')
    for i, (cn, daz, seed) in enumerate(TUFTS):
        az, r, z, D, s = CLUSTERS[cn]
        out = pol(az + daz, 1.0, 0.0)
        dirn = (out + Vector((0, 0, 0.55))).normalized()                # upper side of the drop
        hit = bvh[cn].ray_cast(cpos(cn) + dirn * D, -dirn)[0]
        comp[f'Tuft_{cn}{i}'] = leaf_tuft(P, hit, out, seed=seed)
    print('  blooms', nb, '| buds', len(BUDS), '| tufts', len(TUFTS))
    for cn in list(comp):
        P.comp.append((cn, comp[cn], False))
    return P


def overlaps(P, prefix_a, prefix_b):
    """pairs of components (by name prefixes) whose shells intersect or touch"""
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    trees = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp
             if nm.startswith(prefix_a) or nm.startswith(prefix_b)}
    out = []
    names = sorted(trees)
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
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return colls


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


def build():
    colls = clear_own(); coll = colls[0]
    img = pc.atlas_image(ATLAS_TEX, os.path.join(ART, 'Textures', ATLAS_TEX), PAL_F)
    mat = pc.material(ATLAS_MAT, img)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Roughness'].default_value = 0.85                     # Smoothness ~0.15 (STYLE.md)
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_rose_bush()
    pt = part_tris(P)
    ov_cc = overlaps(P, 'Cluster_', 'Cluster_'); ov_bb = overlaps(P, 'Bloom_', 'Bloom_')
    ov_bc = [(a, b) for a, b in overlaps(P, 'Bloom_', 'Cluster_')
             if b.startswith('Cluster_') and a[6:].rstrip('0123456789') != b[8:]]
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    n_cop, _ = pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris):', pt, '| clusters touching', ov_cc, '| blooms touching', ov_bb, '| bloom in foreign cluster', ov_bc)
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


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_PLT01_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_PLT01_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_PLT01_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_PLT01_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_PLT01_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_PLT01_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new('TMP_PLT01_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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

colls, root, ob, img, mat, tot, var = build()
os.makedirs(CHECK_DIR, exist_ok=True)
base_objs = [root, ob]
if MODE == 'build':
    tag = 'live' if LIVE else 'headless'
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-01_check_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.80, fill_h=0.88, lens=None)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-01_check34_{tag}.png'), VIEW_PREVIEW)
if MODE == 'export':
    for sub in ('Meshes', 'Textures', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbxs = [pc.export(NAME, colls[0], root, os.path.join(ART, 'Meshes', NAME + '.fbx'))]
    for (suf, (vr, vo)), c in zip(var.items(), colls[1:]):
        fbxs.append(pc.export(NAME + suf, c, vr, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
    render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    for f in fbxs: pc.verify(f)
if MODE in ('export', 'dump'):
    geom_dump([ob] + [vo for _, vo in var.values()],
              os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
