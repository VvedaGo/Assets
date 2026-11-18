# STA-07 Jam kettle -> FMS_Workshop_STA_07 (Farm Processing pack). Headless, one call:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_jam_kettle.py -- <mode> [tag] [side_view]
#   mode: build (checks only) | check (+ check renders to %TEMP%) | final (+ export, verify, .blend, preview)
# Idempotent: rebuilds only its own collection. Helpers: ../_common/processing_common.py (read-only); pot/handle/lid/paddle
# code adapted from STA01_CheeseVat/build_cheese_vat.py (not modified).
import bpy, bmesh, math, os, sys, importlib, tempfile
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'STA07_JamKettle')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, zprism, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_07'
TEX_NAME = 'T_FarmProcessing_STA07_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA07'
CHECK_DIR = os.path.join(tempfile.gettempdir(), 'FarmProcessing_check', 'STA-07')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = argv[0] if argv else globals().get('MODE', 'build')
TAG = argv[1] if len(argv) > 1 else 'r'

# ---------------- palette: cells kept from STA-05 where the colour is used; 2,10,12-15 repurposed ----------------
PAL = ['#B5835A', '#7A5233', '#A7A39A', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#B87945', '#5A3C26',
       '#D38E52', '#96603A', '#A93A31', '#D0583F']
(WOOD, MORTAR, STONE, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L,
 COPPER, SOOT, COPPER_L, COPPER_D, JAM, BRICK) = range(16)

# ---------------- dimensions (m); front = -Y ----------------
# hearth
HW, HD = 0.39, 0.38                       # brick core half width / half depth
ZP, ZT, ZS = 0.10, 0.335, 0.425           # plinth top / brick top (= slab bottom) / slab top (review: +2.5 cm for the round arch)
OW = 0.125                                # fire opening half width (= arch inner radius)
CH_Y = 0.10                               # chamber back wall front face (y)
AZC = 0.15                                # round arch: centre (springing) height, on short brick jambs (0.104-0.145)
ARCH_RI, ARCH_RO, ARCH_RK = OW, 0.19, 0.205   # inner / outer radius, keystone outer radius (top tucked under the slab)
ARCH_CUTS = (0, 35, 70, 110, 145, 180)    # 5 voussoirs, keystone 40 deg, others 35 deg
ARCH_GAP = 0.01                           # equal joints between blocks and to the bricks
CROWN = AZC + ARCH_RI
BR_BACK, BR_FRONT, BR_INS = 0.01, 0.018, 0.009   # brick: sunk into the core / proud / front bevel inset
COURSES = ((ZP + 0.004, 0.214), (0.224, ZT - 0.006))
# kettle
N = 20
A0 = -math.pi / 2 + math.pi / N           # face centred on -Y and on +-X (X-mirror exact)
Z0 = ZS - 0.003                           # pot flat bottom rests ON the slab top (3 mm sunk for contact)
PZ = 1.12                                 # pot height factor (round 3: ref pot taller)
POT = [(0.27, 0.0), (0.305, 0.03), (0.36, 0.09), (0.38, 0.15), (0.375, 0.21), (0.358, 0.262), (0.388, 0.276),
       (0.392, 0.312), (0.378, 0.33), (0.345, 0.33), (0.338, 0.27)]
POT_BANDS = [COPPER_D, COPPER, COPPER_L, COPPER_L, COPPER, COPPER_D, COPPER_L, COPPER_L, COPPER_L, COPPER]
POT = [(r, z * PZ) for r, z in POT]
ZJ = Z0 + POT[-1][1]                      # jam level
ZR = Z0 + 0.33 * PZ                           # rim top
HANDLE_AZ = math.radians(18)              # handles turned 18 deg to the front (face centre) so the bolt bosses face the camera
HZ_U, HZ_L = 0.262, 0.165                 # upper / lower attachment height above the pot bottom (bosses at both)
LUMPS = ((-0.11, 0.19, 0.064, 0.2, 0.022), (0.07, 0.19, 0.062, 0.7, 0.02), (-0.225, 0.0, 0.06, 0.4, 0.02),
         (-0.02, -0.02, 0.066, 0.1, 0.022), (-0.13, -0.18, 0.06, 0.5, 0.02), (0.04, -0.235, 0.04, 0.3, 0.016),
         (0.25, 0.06, 0.045, 0.9, 0.017))
# lid
RL = 0.355
LID_AZ, LID_TILT = math.radians(196), math.radians(14)
LID_SHIFT = 0.0
# paddle: blade bottom B (sunk in the jam) -> top T
PAD_B, PAD_T = Vector((0.10, -0.10, ZJ - 0.06)), Vector((0.52, 0.13, 1.07))
BLADE_L, BLADE_W, BLADE_T = 0.22, 0.19, 0.04

def ring(r, z, n=N, a0=A0):
    return [Vector((r * math.cos(a0 + 2 * math.pi * k / n), r * math.sin(a0 + 2 * math.pi * k / n), z)) for k in range(n)]

def poly_sweep(P, cname, pts, prof, plane_n, side, cap0, cap1):
    """planar polyline sweep with mitred joints; prof (x in-plane, y along plane_n)"""
    pts = [Vector(p) for p in pts]; nrm = Vector(plane_n).normalized(); rings = []
    for i, c in enumerate(pts):
        if i == 0: t = (pts[1] - pts[0]).normalized(); s = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); s = 1.0
        else:
            ta = (c - pts[i - 1]).normalized(); tb = (pts[i + 1] - c).normalized(); t = (ta + tb).normalized()
            s = 1.0 / max(0.3, t.dot(ta))
        e1 = nrm.cross(t).normalized()
        rings.append([c + e1 * (x * s) + nrm * y for x, y in prof])
    return P.loft(cname, rings, side, cap0, cap1)

def box(P, cname, x0, x1, y0, y1, z0, z1, slots, ground=False):
    """axis box; slots dict per face key ('-x','+x','-y','+y','-z','+z') -> cell, default MORTAR"""
    bm = P.bm
    v = {(i, j, k): bm.verts.new(((x0, x1)[i], (y0, y1)[j], (z0, z1)[k])) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    quads = {'-x': [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], '+x': [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)],
             '-y': [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)], '+y': [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],
             '-z': [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], '+z': [(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)]}
    faces = [P.face([v[q] for q in qs], slots.get(key, MORTAR)) for key, qs in quads.items()]
    P.comp.append((cname, faces, ground))

def block(P, cname, poly2d, frame, back, front, ins, side, cap_back, cap_front):
    """convex 2D outline (u, v) in a face frame (origin c, normal n, axes e1, e2) extruded from -back to +front along n,
    front ring inset by ins (bevelled frustum: 4-8 sides + 2 caps, cheap 'chamfered brick')"""
    c, n, e1, e2 = (Vector(x) for x in frame)
    area = sum(poly2d[i - 1][0] * poly2d[i][1] - poly2d[i][0] * poly2d[i - 1][1] for i in range(len(poly2d)))
    if area < 0: poly2d = list(reversed(poly2d))
    r0 = [c - n * back + e1 * u + e2 * w for u, w in poly2d]
    r1 = [c + n * front + e1 * u + e2 * w for u, w in pc.inset(poly2d, ins)]
    P.loft(cname, [r0, r1], side, cap_back, cap_front)

def brick(P, face, a0, a1, z0, z1):
    """brick on a core face: face in ('-y','+y','-x','+x'); a0..a1 along the face (x for front/back, y for sides)"""
    if face in ('-y', '+y'):
        s = -1 if face == '-y' else 1; fr = ((0, s * HD, 0), (0, s, 0), (1, 0, 0), (0, 0, 1))
    else:
        s = -1 if face == '-x' else 1; fr = ((s * HW, 0, 0), (s, 0, 0), (0, 1, 0), (0, 0, 1))
    rect = [(a0, z0), (a1, z0), (a1, z1), (a0, z1)]
    block(P, 'brick', rect, fr, BR_BACK, BR_FRONT, BR_INS, BRICK, MORTAR, BRICK)

# ---------------- body: hearth + kettle + jam + handles ----------------
def build_body():
    P = Part('Body')
    # --- hearth core (mortar), fire chamber faces dark
    box(P, 'pier', -HW, -OW, -HD, HD, ZP, ZT, {'+x': SOOT})
    box(P, 'pier', OW, HW, -HD, HD, ZP, ZT, {'-x': SOOT})
    box(P, 'chamber_back', -OW, OW, CH_Y, HD, 0.0, ZT, {'-y': SOOT}, ground=True)
    box(P, 'lintel', -OW, OW, -HD, CH_Y, CROWN, ZT, {'-z': SOOT})
    # --- stone plinth sills under the piers (full depth, top chamfer)
    for sx in (-1, 1):
        x0, x1 = OW - 0.02, HW + 0.035
        rect_prism(P, 'plinth', sx * (x0 + x1) / 2, 0, x1 - x0, 2 * HD + 0.06, 0.015,
                   [(0.0, 0.0), (ZP - 0.022, 0.0), (ZP, 0.022)], STONE, STONE, STONE, ground=True)
    # --- stone top slabs 3 x 2 (top chamfer -> V-grooves between them)
    SX = (-HW - 0.03, -0.20, 0.20, HW + 0.03); SY = (-HD - 0.025, 0.0, HD + 0.025)
    for i in range(3):
        for j in range(2):
            rect_prism(P, 'slab', (SX[i] + SX[i + 1]) / 2, (SY[j] + SY[j + 1]) / 2, SX[i + 1] - SX[i], SY[j + 1] - SY[j], 0.012,
                       [(ZT, 0.0), (ZS - 0.022, 0.0), (ZS, 0.02)], STONE, STONE, STONE)
    # --- bricks: front piers (2 courses), sides, back; offset joints, all X-mirror symmetric
    (l0, l1), (u0, u1) = COURSES
    # front: plain outer bricks + bricks cut along the arch (1 cm joint parallel to the voussoir faces / radial joints)
    C = Vector((0.0, AZC)); g = ARCH_GAP
    def ch(a0, a1, off):     # half-plane beyond the outer face (chord) of voussoir a0..a1 (+off): (nx, nz, d)
        m = math.radians((a0 + a1) / 2); h = math.radians((a1 - a0) / 2)
        return (math.cos(m), math.sin(m), ARCH_RO * math.cos(h) + off)
    def rad(a, above):       # half-plane above/below the radial line at angle a, half a joint away
        t = math.radians(a); k = 1 if above else -1
        return (-math.sin(t) * k, math.cos(t) * k, g / 2)
    def clip(poly, hp):
        nx, nz, d = hp; out = []
        f = lambda p: nx * p[0] + nz * (p[1] - AZC) - d
        for i in range(len(poly)):
            p, q = poly[i - 1], poly[i]; fp, fq = f(p), f(q)
            if fq >= 0:
                if fp < 0: t = fp / (fp - fq); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
                out.append(q)
            elif fp >= 0:
                t = fp / (fp - fq); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        return out
    nflip = lambda hp: (-hp[0], -hp[1], -hp[2])
    fr = ((0, -HD, 0), (0, -1, 0), (1, 0, 0), (0, 0, 1))
    right = [  # (rect x0, x1, z0, z1, half-planes) on the +X side; mirrored to -X
        (OW + 0.004, 0.25, l0, AZC - 0.005, [nflip(ch(0, 35, 0.0))]),            # short jamb under the springer
        (0.15, 0.385, l0, l1, [ch(0, 35, g)]),                                   # lower course, cut along the springer
        (0.315, 0.385, u0, u1, []),                                               # upper course outer
        (0.0, 0.31, u0, u1, [ch(0, 35, g), rad(35, False)]),                     # upper course beside the springer
        (0.0, 0.31, u0, u1, [ch(35, 70, g), rad(35, True), rad(70, False)])]     # upper course beside voussoir 2
    for x0, x1, z0, z1, hps in right:
        poly = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        for hp in hps: poly = clip(poly, hp)
        area = 0.5 * abs(sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly))))
        if len(poly) < 3 or area < 4e-4: continue
        for sx in (1, -1):
            block(P, 'brick', [(sx * x, z) for x, z in poly], fr, BR_BACK, BR_FRONT, 0.006 if hps else BR_INS, BRICK, MORTAR, BRICK)
    for face in ('-x', '+x'):
        for a0, a1 in ((-0.375, -0.13), (-0.12, 0.125), (0.135, 0.375)):
            brick(P, face, a0, a1, l0, l1)
        for a0, a1 in ((-0.375, -0.255), (-0.245, 0.0), (0.01, 0.255), (0.265, 0.375)):
            brick(P, face, a0, a1, u0, u1)
    for a0, a1 in ((-0.385, -0.135), (-0.125, 0.125), (0.135, 0.385)):
        brick(P, '+y', a0, a1, l0, l1)
    for a0, a1 in ((-0.385, -0.255), (-0.245, -0.005), (0.005, 0.245), (0.255, 0.385)):
        brick(P, '+y', a0, a1, u0, u1)
    # --- round arch from one parametric ring: centre (0, AZC), inner/outer radius, 5 radial blocks with equal 1 cm joints,
    #     all the same depth and flush with the brick faces; keystone 40 deg and slightly taller
    hg = ARCH_GAP / 2
    for i in range(5):
        a0, a1 = math.radians(ARCH_CUTS[i]), math.radians(ARCH_CUTS[i + 1])
        ro = ARCH_RK if i == 2 else ARCH_RO
        w0, t0 = Vector((math.cos(a0), math.sin(a0))), Vector((-math.sin(a0), math.cos(a0)))
        w1, t1 = Vector((math.cos(a1), math.sin(a1))), Vector((-math.sin(a1), math.cos(a1)))
        pts = [C + w0 * ARCH_RI + t0 * hg, C + w0 * ro + t0 * hg, C + w1 * ro - t1 * hg, C + w1 * ARCH_RI - t1 * hg]
        block(P, 'voussoir', [tuple(p) for p in pts], fr, BR_BACK, BR_FRONT, 0.006, CREAM_D, MORTAR, CREAM)
    # dark recessed fire chamber floor between the plinths
    box(P, 'chamber_floor', -OW, OW, -HD + 0.03, CH_Y, 0.0, 0.012, {k: SOOT for k in ('-x', '+x', '-y', '+y', '-z', '+z')}, ground=True)
    # --- kettle: lofted copper pot, flat bottom ON the slabs, rolled lip, inner wall, flat jam cap
    P.loft('pot', [ring(r, Z0 + z) for r, z in POT], lambda j, k: POT_BANDS[j], COPPER_D, JAM)
    # jam lumps: flat faceted hex plateaus, half-sunk (fixed layout)
    for x, y, rr, rot, h in LUMPS:
        hexp = [(rr * (1 - 0.15 * (k % 2)) * math.cos(rot + k * math.pi / 3), rr * (1 - 0.15 * (k % 2)) * math.sin(rot + k * math.pi / 3)) for k in range(6)]
        zprism(P, 'lump', x, y, hexp, [(ZJ - 0.012, 0), (ZJ + h, rr * 0.24)], RED_D, JAM, RED)
    # handles: chunky round (8-gon) D-loops between two copper boss plates with grey hex bolts (upper under the lip, lower on
    #     the bulge), turned 18 deg to the front onto a pot face centre
    def wall_r(z):
        for (r0, z0_), (r1, z1_) in zip(POT[:5], POT[1:6]):
            if z0_ <= z <= z1_: return r0 + (r1 - r0) * (z - z0_) / (z1_ - z0_)
    c9 = math.cos(math.pi / N)
    zu, zl = HZ_U * PZ, HZ_L * PZ
    au, al = wall_r(zu) * c9, wall_r(zl) * c9
    loop = [(au + 0.006, zu), (au + 0.06, zu + 0.045), (au + 0.105, zu + 0.062), (au + 0.14, zu + 0.035),
            (au + 0.148, zu - 0.015), (al + 0.11, zl + 0.035), (al + 0.006, zl)]
    for sx in (-1, 1):
        ud = Vector((sx * math.cos(HANDLE_AZ), -math.sin(HANDLE_AZ), 0)); pn = Vector((-ud.y, ud.x, 0))
        P3 = lambda dd, z: ud * dd + Vector((0, 0, Z0 + z))
        for a, z in ((au, zu), (al, zl)):
            sweep(P, 'boss', P3(a - 0.012, z), P3(a + 0.016, z), ngon(0.044, 8, math.pi / 8),
                  [(0, 1, 0), (1, 1, 0)], COPPER_L, COPPER_D, COPPER_L, ref=(0, 0, 1))
            sweep(P, 'bolt', P3(a + 0.010, z), P3(a + 0.038, z), ngon(0.027, 6, math.pi / 2),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.008)], METAL, METAL, METAL_L, ref=(0, 0, 1))
        poly_sweep(P, 'handle', [P3(dd, z) for dd, z in loop], ngon(0.021, 8, math.pi / 8), pn, COPPER, COPPER, COPPER)
    return P

# ---------------- lid: built at the origin, leaned and slid towards the body until it touches ----------------
def build_lid(body_bvh, body_bm):
    P = Part('Lid')
    nh = Vector((math.cos(LID_AZ), math.sin(LID_AZ), 0))
    n = (nh * math.cos(LID_TILT) + Vector((0, 0, math.sin(LID_TILT)))).normalized()
    u = (-nh * math.sin(LID_TILT) + Vector((0, 0, math.cos(LID_TILT)))).normalized()
    e = u.cross(n).normalized()
    L = lambda x, y, z: e * x + u * y + n * z
    lprof = [(RL - 0.014, 0.0), (RL, 0.014), (RL, 0.032), (RL - 0.045, 0.052), (RL * 0.6, 0.064)]
    rings = [[L(p.x, p.y, z) for p in ring(r, 0)] for r, z in lprof]
    P.loft('lid', rings, lambda j, k: (COPPER, COPPER_L, COPPER_L, COPPER)[j], COPPER_D, COPPER)
    gp = [L(0, -0.13, 0.04), L(0, -0.105, 0.135), L(0, 0.105, 0.135), L(0, 0.13, 0.04)]
    poly_sweep(P, 'grip', gp, chamf_rect(0.044, 0.05, 0.012), e, METAL, METAL, METAL)
    bm = P.bm
    mz = min(v.co.z for v in bm.verts)
    eh = Vector((e.x, e.y, 0)).normalized(); eh = eh if eh.y < 0 else -eh
    start = nh * 1.3 + eh * LID_SHIFT + Vector((0, 0, -mz))
    for v in bm.verts: v.co += start
    d = -nh; hits = []
    for v in bm.verts:
        h = body_bvh.ray_cast(v.co, d)
        if h[0] is not None: hits.append(h[3])
    lid_bvh = BVHTree.FromBMesh(bm)             # two-way: body parts (handle loops, slab corners) hitting the lid face count too
    for bv in body_bm.verts:
        h = lid_bvh.ray_cast(bv.co, -d)
        if h[0] is not None: hits.append(h[3])
    move = min(hits) + 0.0015
    for v in bm.verts: v.co += d * move
    # body corners (slab/plinth) must not pierce the lid face: back off along nh until they sit <= 1 mm inside the back face
    O = start + d * move
    pen = 0.0
    for bv in body_bm.verts:
        q = bv.co - O; h = q.dot(n)
        if 0.0 < h < 0.2 and (q - n * h).length < RL - 0.004: pen = max(pen, h)
    if pen > 0.001:
        back = (pen - 0.001) / max(0.2, nh.dot(n))
        for v in bm.verts: v.co += nh * back
        print(f'  lid: backed off {back:.4f} m (body corner pierced {pen:.4f})')
    low = min(bm.verts, key=lambda v: v.co.z).co
    piv = Vector((low.x, low.y, 0.0))
    print(f'  lid: slid {move:.3f} m, bottom contact at {[round(x, 3) for x in piv]}')
    return P, piv

# ---------------- paddle: spade blade (constant thickness, cut lower corners, tapered neck) + 8-gon handle ----------------
def build_paddle():
    P = Part('Paddle')
    d = (PAD_T - PAD_B).normalized()
    from processing_common import basis
    t, e1, e2 = basis(d, (0, 0, 1))
    rings = []
    for tt, w in ((0.0, 0.55), (0.16, 1.0), (0.72, 1.0), (1.0, 0.36)):
        c = PAD_B + d * (BLADE_L * tt)
        rings.append([c + e1 * x + e2 * y for x, y in chamf_rect(BLADE_T, BLADE_W * w, 0.007)])
    P.loft('blade', rings, WOOD, WOOD, WOOD)
    h0 = PAD_B + d * (BLADE_L * 0.85)
    sweep(P, 'handle', h0, PAD_T, ngon(0.028, 8, math.pi / 8),
          [(0, 1, 0), (0.88, 1, 0), (0.93, 1.2, 0), (1, 1.2, 0.013)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    piv = PAD_B.lerp(PAD_T, 0.5)
    return P, piv

# ---------------- checks / render / verify ----------------
def world_bvh(ob):
    me = ob.data; mw = ob.matrix_world
    return BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])

def contact(a, b):
    ba, bb = world_bvh(a), world_bvh(b)
    if ba.overlap(bb): return 0.0
    mw = a.matrix_world
    return min(bb.find_nearest(mw @ v.co)[3] for v in a.data.vertices)

def render(out, pct, view=None):
    g = {'__name__': '__preview__', 'OUT': out, 'PCT': pct}
    if view: g['VIEW_DIR'] = view
    exec(open(os.path.join(HERE, 'render_preview.py'), encoding='utf-8').read(), g)

def verify_headless(fbx):
    before_o, before_i = set(bpy.data.objects), set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in bpy.data.objects if o not in before_o]
    bpy.context.view_layer.update()
    print('VERIFY nodes', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
            pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler], 'scale', [round(s, 4) for s in o.scale])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)

# ---------------- build ----------------
def build():
    for o in list(bpy.context.scene.objects):              # factory startup: drop default cube/camera/light
        if o.name in ('Cube', 'Camera', 'Light'): bpy.data.objects.remove(o, do_unlink=True)
    coll = pc.clear_collection(NAME)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), PAL); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    body = build_body()
    body.bm.verts.ensure_lookup_table()
    bvh = BVHTree.FromBMesh(body.bm)
    lid, lpiv = build_lid(bvh, body.bm)
    pad, ppiv = build_paddle()
    obs = {}
    obs['Body'] = pc.to_object(body, NAME, coll, mat, (0, 0, 0), root, mirror_skip=('lump',))
    obs['Lid'] = pc.to_object(lid, NAME, coll, mat, tuple(lpiv), root, mirror_skip=('lid', 'grip'))
    obs['Paddle'] = pc.to_object(pad, NAME, coll, mat, tuple(ppiv), root, mirror_skip=('blade', 'handle'))
    bpy.data.scenes[NAME + '_Build'].view_layers[0].update()
    tot = pc.report(obs)
    print(f'  budget 1200-2400: {"OK" if 1200 <= tot <= 2400 else "OUT"}')
    print('  contact lid-body', round(contact(obs['Lid'], obs['Body']), 5), '| paddle-body', round(contact(obs['Paddle'], obs['Body']), 5))
    print(f'  hearth top {ZS} pot bottom {Z0:.3f} jam {ZJ:.3f} rim {ZR:.3f} | arch crown {CROWN:.3f} centre {AZC:.3f} | paddle top {PAD_T.z}')
    return obs, root, coll, img, mat

OBS, ROOTOB, COLL, IMG, MAT = build()

if MODE == 'check':
    os.makedirs(CHECK_DIR, exist_ok=True)
    render(os.path.join(CHECK_DIR, f'{TAG}_ref.png'), 50)
    render(os.path.join(CHECK_DIR, f'{TAG}_thumb.png'), 10)
    if len(argv) > 2:
        render(os.path.join(CHECK_DIR, f'{TAG}_side.png'), 40, view=tuple(float(x) for x in argv[2].split(',')))
elif MODE == 'final':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify_headless(_fbx)
