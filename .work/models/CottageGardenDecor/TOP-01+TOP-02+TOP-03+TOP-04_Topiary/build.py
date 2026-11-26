# build.py - TOP-01..04 Topiary registry (FMS_Garden_Topiary_Standard (+ _Rose), _Cone, _Spiral, _Tiered),
# pack CottageGardenDecor (Cottage Garden Decor), atlas F Garden_Flora (read only: the shared PNG is loaded, never rewritten),
# material M_Garden_Flora.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- <ID> build|export|dump     (ID = TOP-01 .. TOP-04)
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ variant FBX; each with its .fbm) + collection-only .blend + ONE preview
#            + FBX re-import verify + geometry dump (JSON, SHA1 of all meshes incl. UV cells)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\TOP-01+TOP-02+TOP-03+TOP-04_Topiary\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['TOP-01', 'build']})
#   Live mode touches only the collection <ID>_<Name> (and its variant child) + temporary TMP_ scenes removed again.
#
# Axes (Blender): X right, -Y front (= reference camera; Unity +Z after the -Z-forward export), Z up (Unity Y).
# Pivot (0, 0, 0) = centre of the soil disc bottom on the ground.
# Shared generators: soil_disc (12-sided, Ø0.50, 0.04), stem (8-sided tapered prism, closed), clipped_ball (faceted
# icosphere, inward radial jitter, fixed seed), foliage colouring by face direction (two greens), cone, helix band.
# Copied from PLT-01 build.py (accepted): ring, bridge, rose_bloom_v2, inside, render, geom_dump; atlas_readonly from PLT-06.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
ATLAS_TEX = 'FMS_Garden_AtlasF.png'
ATLAS_MAT = 'M_Garden_Flora'
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
SEPAL, CUP, BUD = 0, 4, 5
GREEN_L, GREEN_D = 0, 3                       # boxwood main #3F6B3A (slot 3) + light facets #6E9F4A (slot 0; spec said 2 -
                                              # too close to 3 in render, reference light facets ~#668B3A)
SOIL, BARK = 12, 13
FOL_LIGHT = 3                                 # foliage: light green where the direction hash % FOL_LIGHT == 0 (~30 %)
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'TOP-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi
UP = Vector((0, 0, 1))
VIEWER = Vector((0.0, -0.9, 0.42)).normalized()   # blooms tilt toward the reference/preview camera


def pol(az, r, z):
    a = math.radians(az)
    return Vector((r * math.cos(a), r * math.sin(a), z))


# ============ shared generators ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    """n points around axis a through O, radius r, start angle a0 (radians, in the e1/e2 frame of pc.basis)."""
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def bridge(P, A, angA, B, angB, slot):
    """Triangle strip between two closed rings of different vertex counts, zipped by angle (PLT-01)."""
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


def rose_bloom_v2(P, p, a, spin=0.0, depth=0.05, neck=0.02,
                  r_base=0.035, r_rim=0.058, h_rim=0.05,
                  r_in0=0.030, h_in0=0.015, r_in1=0.040, h_in1=0.045,
                  r_bud=0.018, h_bud=0.030, h_tip=0.060, twist=math.pi / 6,
                  slot_calyx=SEPAL, slot_outer=CUP, slot_inner=BUD):
    """ROSE BLOOM v2 (PLT-01 Fix 2, copied unchanged): ONE closed shell, 68 tris, rim Ø0.116, cup height 0.05."""
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


def soil_disc(P):
    """SOIL DISC (shared TOP-01..04): 12-sided flat cylinder Ø0.50 (circumradius 0.25), z 0..0.04, closed (bottom cap
    on the ground so the shell is manifold), slot 12."""
    rings = [[Vector((x, y, z)) for x, y in pc.ngon(0.25, 12, math.pi / 12)] for z in (0.0, 0.04)]
    R = P.loft('Soil', rings, SOIL, SOIL, SOIL)
    P.comp[-1] = ('Soil', P.comp[-1][1], True)
    return R


def stem(P, cname, z0, z1, r0, r1, n=8, segs=2, slot=BARK, tip=None):
    """STEM (shared): n-sided tapered prism on the Z axis (circumradius r0 -> r1), z0 sunk into the soil disc, both ends
    capped (closed); tip = (z, ) adds a pointed cone instead of the top cap."""
    rings = [[Vector((x, y, z0 + (z1 - z0) * j / segs)) for x, y in pc.ngon(r0 + (r1 - r0) * j / segs, n, math.pi / n)]
             for j in range(segs + 1)]
    if tip is None:
        return P.loft(cname, rings, slot, slot, slot)
    R = P.loft(cname, rings, slot, slot, None)
    t = P.bm.verts.new(Vector((0, 0, tip)))
    fs = [P.face([R[-1][k], R[-1][(k + 1) % n], t], slot) for k in range(n)]
    nm, faces, g = P.comp[-1]; P.comp[-1] = (nm, faces + fs, g)
    return R


def clipped_ball(P, cname, c, r, sub, seed, jitter=0.02):
    """CLIPPED BALL (shared): faceted icosphere (bmesh subdivisions: 2 -> 80 tris, 3 -> 320 tris), pole up, every vertex
    pulled inward radially by 0..jitter (fixed seed: hand-clipped look, outer size stays r). Flat shaded; colour later by
    face direction (foliage_slots). Returns the temp bmesh (world space) for placement ray casts."""
    rnd = random.Random(seed)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    for v in bm.verts:
        v.co = Vector(c) + v.co.normalized() * (r - rnd.uniform(0.0, jitter))
    bm.normal_update()
    vm = {v: P.bm.verts.new(v.co) for v in bm.verts}
    faces = [P.face([vm[v] for v in f.verts], GREEN_D) for f in bm.faces]
    P.comp.append((cname, faces, False))
    return bm


def dir_light(n, mod=None):
    """two greens by face direction: the face normal is binned (5 x 5 x 5) and hashed; ~1 in FOL_LIGHT directions is
    light green. Scattered facets (no horizontal band), identical for identical directions, no noise texture."""
    q = [min(4, int((c + 1) * 2.5)) for c in n]
    return (q[0] * 7 + q[1] * 3 + q[2] * 5) % (mod or FOL_LIGHT) == 0


def foliage_slots(P, prefixes, rule=None, mod=None):
    """two greens by face direction (dir_light -> GREEN_L, else GREEN_D); rule(cname, face) may override."""
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    P.bm.normal_update()
    cnt = [0, 0]
    for nm, faces, _ in P.comp:
        if not nm.startswith(prefixes): continue
        for f in faces:
            s = rule(nm, f) if rule else None
            if s is None: s = GREEN_L if dir_light(f.normal, mod) else GREEN_D
            f[P.slot] = s; cnt[s == GREEN_L] += 1
    print(f'  foliage faces: main {cnt[0]} light {cnt[1]} ({100 * cnt[1] / max(1, sum(cnt)):.0f} % light)')


def inside(bvh, q):
    n_hit = 0; o = Vector(q)
    for _ in range(12):
        h = bvh.ray_cast(o + Vector((0, 0, 1e-5)), Vector((0, 0, 1)))
        if h[0] is None: break
        n_hit += 1; o = h[0]
    return n_hit % 2 == 1


def overlaps(P, a, b):
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    fa = next(fs for nm, fs, _ in P.comp if nm == a); fb = next(fs for nm, fs, _ in P.comp if nm == b)
    ta = BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fa])
    tb = BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fb])
    return bool(ta.overlap(tb))


# ============ builders (return Part, extra info) ============
BLOOM_TILT = 22.0                             # coordinator 2026-11-26: blooms tilted 15-30 deg toward the viewer
TOP01_BALL = dict(c=(0, 0, 1.10), r=0.31, sub=2, seed=101)   # 80 tris (reference facet size)


def build_standard(rose=False):
    P = Part('Body')
    soil_disc(P)
    stem(P, 'Stem', 0.02, 0.88, 0.035, 0.030)
    b = TOP01_BALL
    bm = clipped_ball(P, 'Ball', b['c'], b['r'], b['sub'], b['seed'])
    foliage_slots(P, ('Ball',))
    print('  stem bare length (disc top -> ball bottom):', round(min(v.co.z for v in bm.verts) - 0.04, 3))
    if rose:
        bvh = BVHTree.FromBMesh(bm); c = Vector(b['c']); nb = 0; tilts = []
        dirs = [(0.0, 0.0)] + [(50.0, 90 + 72 * k) for k in range(5)] + [(100.0, 90 + 36 + 90 * k) for k in range(4)]
        for i, (pol_d, az) in enumerate(dirs):
            th, ph = math.radians(pol_d), math.radians(az)
            n = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
            hit = bvh.ray_cast(c + n * 0.5, -n)[0]
            ax = n.cross(VIEWER); tilt = min(n.angle(VIEWER), math.radians(BLOOM_TILT))
            a = (Matrix.Rotation(tilt, 3, ax.normalized()) @ n) if ax.length > 1e-6 else n.copy()
            tilts.append(round(math.degrees(n.angle(a)), 1))
            fs = rose_bloom_v2(P, hit, a, spin=ph, depth=0.05, neck=-0.008)   # cup base sunk into the ball (spec 0.015)
            P.comp.append((f'Bloom_{i}', fs, False)); nb += 1
            if not inside(bvh, hit - a * 0.04): print(f'  WARNING bloom {i}: calyx apex outside the ball')
        print('  blooms', nb, '| tilt toward the viewer (deg)', tilts)
    bm.free()
    return P


CONE_Z0 = 0.30                                # cone base (reference: ~0.26 bare stem shows)


def build_cone():
    P = Part('Body')
    soil_disc(P)
    z0, z_apex, r0 = CONE_Z0, 1.60, 0.36
    stem(P, 'Stem', 0.02, z0 + 0.08, 0.035, 0.030)
    rnd = random.Random(202); n = 12; zs = [z0 + (z_apex - z0) * j / 3 for j in range(3)]
    colk = [1.0 - rnd.uniform(0.0, 0.055) for _ in range(n)]        # per-column inward jitter: edges stay straight lines
    R = []
    for z in zs:
        rr = r0 * (1 - (z - z0) / (z_apex - z0))
        R.append([P.bm.verts.new(Vector((x * rr * colk[k], y * rr * colk[k], z)))
                  for k, (x, y) in enumerate(pc.ngon(1.0, n, math.pi / n))])
    apex = P.bm.verts.new(Vector((rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), z_apex)))
    faces = []; col = {}
    for j in range(len(R) - 1):
        for k in range(n):
            f = P.face([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]], GREEN_D); faces.append(f); col[f] = k
    for k in range(n):
        f = P.face([R[-1][k], R[-1][(k + 1) % n], apex], GREEN_D); faces.append(f); col[f] = k
    cap = P.face(list(reversed(R[0])), GREEN_D); faces.append(cap)
    P.comp.append(('Cone', faces, False))
    # colour: every 3rd vertical face column light (spec); base cap main green
    foliage_slots(P, ('Cone',), rule=lambda nm, f: (GREEN_L if col[f] % 3 == 0 else GREEN_D) if f in col else GREEN_D)
    print('  cone bare stem (disc top -> cone base):', round(min(v.co.z for v in R[0]) - 0.04, 3))
    return P


SPIRAL = dict(turns=3.5, seg_per_turn=16, z_bot=0.30, z_top=1.80, r_out=(0.36, 0.07), h_out=0.28, h_in=0.16,
              taper_from=0.72, h_tip=0.07, trunk=(0.05, 0.035, 1.68), tip=1.74, bulge=0.04, a0=150, seed=303)


def build_spiral():
    S = SPIRAL; P = Part('Body'); rnd = random.Random(S['seed'])
    soil_disc(P)
    r_tr0, r_tr1, z_tr1 = S['trunk']
    stem(P, 'Trunk', 0.02, z_tr1, r_tr0, r_tr1, segs=3, tip=S['tip'])
    nseg = int(S['turns'] * S['seg_per_turn']); apo = math.cos(math.pi / 8)
    def h_of(t):
        if t <= S['taper_from']: return 1.0
        return 1.0 - (1.0 - S['h_tip'] / S['h_out']) * (t - S['taper_from']) / (1 - S['taper_from'])
    zc0 = S['z_bot'] + S['h_out'] / 2; zc1 = S['z_top'] - S['h_tip'] / 2
    rings = []; tops = []
    for i in range(nseg + 1):
        t = i / nseg; th = TAU * S['turns'] * t + math.radians(S['a0'])
        zc = zc0 + (zc1 - zc0) * t; k = h_of(t)
        ho, hi = S['h_out'] * k / 2, S['h_in'] * k / 2
        R = S['r_out'][0] + (S['r_out'][1] - S['r_out'][0]) * t
        rtr = (r_tr0 + (r_tr1 - r_tr0) * min(1.0, (zc - 0.02) / (z_tr1 - 0.02))) * apo - 0.008   # inside the trunk
        u = Vector((math.cos(th), math.sin(th), 0))
        j = lambda a: rnd.uniform(-a, a)
        sec = [u * rtr + Vector((0, 0, zc - hi + j(0.008))),
               u * (R - rnd.uniform(0, 0.02)) + Vector((0, 0, zc - ho + j(0.01))),
               u * (R + S['bulge'] * k - rnd.uniform(0, 0.02)) + Vector((0, 0, zc + j(0.01))),
               u * (R - rnd.uniform(0, 0.02)) + Vector((0, 0, zc + ho + j(0.01))),
               u * rtr + Vector((0, 0, zc + hi + j(0.008)))]
        rings.append(sec); tops.append((th, zc - ho, zc + ho))
    P.loft('Band', rings, GREEN_D, GREEN_D, GREEN_D)
    foliage_slots(P, ('Band',), mod=4)                              # ~25 %: 1 in 3 reads as a checkerboard on the band
    turns = (TAU * S['turns']) / TAU
    gaps = [tops[i + S['seg_per_turn']][1] - tops[i][2] for i in range(nseg + 1 - S['seg_per_turn'])]
    print(f'  spiral turns {turns:.2f} | segments {nseg} | outer gap between turns min {min(gaps):.3f} max {max(gaps):.3f}'
          f' | band bottom z {min(v.z for v in rings[0]):.3f} (bare trunk {min(v.z for v in rings[0]) - 0.04:.3f})')
    return P


TIERS = [('Ball1', (0, 0, 0.60), 0.36, 2, 401), ('Ball2', (0, 0, 1.15), 0.26, 2, 402), ('Ball3', (0, 0, 1.535), 0.165, 2, 403)]


def build_tiered():
    P = Part('Body')
    soil_disc(P)
    stem(P, 'Stem', 0.02, 0.40, 0.035, 0.035)
    bms = [clipped_ball(P, nm, c, r, sub, seed) for nm, c, r, sub, seed in TIERS]
    foliage_slots(P, ('Ball',))
    print('  stack overlaps: Ball1/Ball2', overlaps(P, 'Ball1', 'Ball2'), '| Ball2/Ball3', overlaps(P, 'Ball2', 'Ball3'),
          '| bare stem', round(min(v.co.z for v in bms[0].verts) - 0.04, 3))
    for bm in bms: bm.free()
    return P


# id -> collection, asset name, preview, builder, budget, catalogue box (W, D, H), variants {suffix: (builder, budget)}
REG = {
    'TOP-01': dict(coll='TOP-01_Topiary_Standard', name='FMS_Garden_Topiary_Standard', preview='FMS_Garden_TOP_01_Preview.png',
                   build=build_standard, budget=500, box=(0.6, 0.6, 1.4),
                   # _Rose budget 800 -> 860 (coordinator, option A, 2026-11-26: keep 10 rose_bloom_v2)
                   variants={'_Rose': (lambda: build_standard(rose=True), 860, (0.7, 0.7, 1.45))}),
    'TOP-02': dict(coll='TOP-02_Topiary_Cone', name='FMS_Garden_Topiary_Cone', preview='FMS_Garden_TOP_02_Preview.png',
                   build=build_cone, budget=300, box=(0.7, 0.7, 1.6), variants={}),
    'TOP-03': dict(coll='TOP-03_Topiary_Spiral', name='FMS_Garden_Topiary_Spiral', preview='FMS_Garden_TOP_03_Preview.png',
                   build=build_spiral, budget=900, box=(0.7, 0.7, 1.8), variants={}),
    'TOP-04': dict(coll='TOP-04_Topiary_Tiered', name='FMS_Garden_Topiary_Tiered', preview='FMS_Garden_TOP_04_Preview.png',
                   build=build_tiered, budget=600, box=(0.7, 0.7, 1.7), variants={}),
}
CFG = REG[ID]
COLL, NAME = CFG['coll'], CFG['name']
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)


def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    colls = [coll]
    for suf in CFG['variants']:
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


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 if len(f.verts) <= 4 else len(f.verts) - 2 for f in fs)
    return out


def make(P, asset, coll, mat, budget, box):
    root = bpy.data.objects.new(asset, None); coll.objects.link(root)
    pt = part_tris(P)
    ob = pc.to_object(P, asset, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    pc.coplanar_overlaps(ob)
    d = ob.dimensions
    print(f'  {asset}: parts (tris) {pt} | total {tot} / budget {budget} ->', 'OK' if tot <= budget else f'OVER x{tot / budget:.2f}')
    print(f'  {asset}: size {d.x:.3f} x {d.y:.3f} x {d.z:.3f} vs catalogue {box} | ground min z',
          round(min((ob.matrix_world @ v.co).z for v in ob.data.vertices), 5))
    return root, ob, tot


def build():
    colls = clear_own()
    img, mat = atlas_readonly()
    out = [make(CFG['build'](), NAME, colls[0], mat, CFG['budget'], CFG['box'])]
    for (suf, (fn, bud, box)), c in zip(CFG['variants'].items(), colls[1:]):
        out.append(make(fn(), NAME + suf, c, mat, bud, box))
    return colls, out, img, mat


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


# ---------------- renders (temporary scene; copied from PLT-01 / PLT-06) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_TOP_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_TOP_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_TOP_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_TOP_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_TOP_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_TOP_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_TOP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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

colls, items, img, mat = build()
os.makedirs(CHECK_DIR, exist_ok=True)
tag = 'live' if LIVE else 'headless'
if MODE == 'build':
    for (root, ob, tot), suf in zip(items, [''] + list(CFG['variants'])):
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}{suf}_check_{tag}.png'), VIEW_REF, res=(1254, 1254),
               fill_w=0.62, fill_h=0.88, lens=None)
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}{suf}_check34_{tag}.png'), VIEW_PREVIEW)
if MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    vl = bpy.context.view_layer                                  # live: the owner's selection is saved and restored
    sel = [o.name for o in vl.objects if o.select_get()]; act = vl.objects.active.name if vl.objects.active else None
    fbxs = []
    try:
        for (root, ob, tot), suf, c in zip(items, [''] + list(CFG['variants']), colls):
            fbxs.append(pc.export(NAME + suf, c, root, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
    finally:
        for o in vl.objects: o.select_set(o.name in sel)
        vl.objects.active = vl.objects[act] if act and act in vl.objects else None
        print('  selection restored', sel, act)
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
    render([items[0][0], items[0][1]], os.path.join(ART, 'Previews', CFG['preview']), VIEW_PREVIEW)
    for suf, (root, ob, tot) in zip(list(CFG['variants']), items[1:]):          # variant check image (not in art/)
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}{suf}_check.png'), VIEW_PREVIEW)
    for f in fbxs: pc.verify(f)
if MODE in ('export', 'dump'):
    geom_dump([ob for _, ob, _ in items], os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
