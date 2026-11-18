# TOL-01..05 small processing tools -> FMS_Workshop_TOL_0X (Farm Processing pack). One parametric script, registry by ID.
# Headless, idempotent:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_tools.py -- <ID> <mode>
#   ID: TOL01 mold | TOL02 harp | TOL03 spatula | TOL04 colander | TOL05 ladle
#   mode: build  = build + checks + check renders to %TEMP%\FarmProcessing_check\TOL\<ID>_*.png
#         export = build + checks + FBX + .blend lib + final preview + FBX re-import verify
# Shared helpers (read-only): ../_common/processing_common.py. Tools have no moving parts: root empty + one child _Body.
import bpy, bmesh, math, os, sys, importlib
from mathutils import Vector, Matrix

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'TOL_Tools')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ID = ARGS[0] if ARGS else 'TOL01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'TOL')

# ---------------- palette: cells 0-12 identical to STA-03/STA-05 ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#B39C74', '#5A3C26',      # cell 10 darker than STA-05 (#C7B288) so perforations read
       '#EADAB4', '#C99263', '#A26A43', '#857B6E']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, HWOOD, BLADE, FOOT = range(16)

# ---------------- generic helpers ----------------
def ringco(z, apo, n, phase=0.5):
    rc = apo / math.cos(math.pi / n)
    return [Vector((rc * math.cos(-math.pi / 2 + (k + phase) * 2 * math.pi / n), rc * math.sin(-math.pi / 2 + (k + phase) * 2 * math.pi / n), z)) for k in range(n)]

def edge(bm, a, b):
    return bm.edges.get((a, b)) or bm.edges.new((a, b))

def fill(P, loops, slot, normal):
    """planar region bounded by loops[0] with holes loops[1:] (scanfill)"""
    es = [edge(P.bm, L[i], L[(i + 1) % len(L)]) for L in loops for i in range(len(L))]
    r = bmesh.ops.triangle_fill(P.bm, use_beauty=True, use_dissolve=False, edges=es, normal=Vector(normal))
    fs = [g for g in r['geom'] if isinstance(g, bmesh.types.BMFace)]
    for f in fs: f[P.slot] = slot
    return fs

def hole_loop(P, c, u, w, r, hn, a0=0.0):
    return [P.bm.verts.new(c + u * r * math.cos(a0 + 2 * math.pi * i / hn) + w * r * math.sin(a0 + 2 * math.pi * i / hn)) for i in range(hn)]

def tube(P, a, b, slot):
    n = len(a); return [P.face([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], slot) for i in range(n)]

def blind(P, hl, n_out, depth, wall_slot, bottom_slot):
    """recess behind a hole loop: tube inward by depth along -n_out, closed by a flat bottom"""
    inner = [P.bm.verts.new(v.co - n_out * depth) for v in hl]
    fs = tube(P, hl, inner, wall_slot); fs.append(P.face(list(reversed(inner)), bottom_slot))
    return fs

def shell(P, cname, prof, n, side_slot, cap0, cap1, holes=None, pairs=(), hole_slot=CREAM_IN, cap_holes=None, hn=6, ground=True,
          phase=0.5, a0=0.0):
    """n-gon solid of revolution. prof: [(z, apothem)] closed section path (outer bottom -> up -> rim -> down inside -> floor).
    holes: {band j: (radius, skip_facets)} a hole through every facet of band j; pairs: [(outer band, inner band)] -> tubes.
    A 4-tuple (radius, skip, depth, bottom_slot) makes a blind recess instead (no pair needed).
    cap_holes: [(x, y, r)] holes through both caps (prof[0] and prof[-1]), joined by vertical tubes."""
    holes = holes or {}
    R = [[P.bm.verts.new(v) for v in ringco(z, a, n, phase)] for z, a in prof]; faces = []; H = {}
    for j in range(len(R) - 1):
        for k in range(n):
            A, B, C, D = R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]
            s = side_slot(j, k) if callable(side_slot) else side_slot
            if j in holes and k not in holes[j][1]:
                c = (A.co + B.co + C.co + D.co) / 4; u = (B.co - A.co).normalized()
                w = (C.co + D.co) / 2 - (A.co + B.co) / 2; w = (w - u * w.dot(u)).normalized()
                if w.z < 0: w = -w
                hl = hole_loop(P, c, u, w, holes[j][0], hn, a0); H[(j, k)] = hl
                faces += fill(P, [[A, B, C, D], hl], s, u.cross(w))
                if len(holes[j]) == 4: faces += blind(P, hl, u.cross(w).normalized(), holes[j][2], hole_slot, holes[j][3])
            else:
                faces.append(P.face([A, B, C, D], s))
    def cap(ring, z, slot):
        if not cap_holes: return [P.face(list(ring), slot)], []
        hls = [hole_loop(P, Vector((x, y, z)), Vector((1, 0, 0)), Vector((0, 1, 0)), r, hn) for x, y, r in cap_holes]
        return fill(P, [ring] + hls, slot, (0, 0, 1)), hls
    f0, h0 = cap(R[0], prof[0][0], cap0); f1, h1 = cap(R[-1], prof[-1][0], cap1); faces += f0 + f1
    for a, b in zip(h0, h1): faces += tube(P, a, b, hole_slot)
    for jo, ji in pairs:
        for k in range(n):
            if (jo, k) in H: faces += tube(P, H[(jo, k)], H[(ji, k)], hole_slot)
    P.comp.append((cname, faces, ground))

def path_sweep(P, cname, pts, up, sec, slot, slot_cap, closed=False):
    """sweep a 2D section [(side, up)] along a polyline with mitred joints (thickness kept in the bends); closed=True -> ring"""
    up = Vector(up); rings = []; n = len(pts)
    for i, c in enumerate(pts):
        d1 = (c - pts[i - 1]).normalized() if (i > 0 or closed) else None
        d2 = (pts[(i + 1) % n] - c).normalized() if (i < n - 1 or closed) else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in sec])
    if closed: return P.torus_loft(cname, rings, slot)
    return P.loft(cname, rings, slot, slot_cap, slot_cap)

def flat_plate(P, cname, outline, z0, z1, holes, slot_top, slot_bot, slot_side, slot_hole, ground=True):
    """flat plate from a CCW outline [(x, y)] with through-holes (list of [(x, y)] loops), top/bottom via scanfill"""
    bm = P.bm
    ob = [bm.verts.new((x, y, z0)) for x, y in outline]; ot = [bm.verts.new((x, y, z1)) for x, y in outline]
    hb = [[bm.verts.new((x, y, z0)) for x, y in h] for h in holes]; ht = [[bm.verts.new((x, y, z1)) for x, y in h] for h in holes]
    faces = fill(P, [ot] + ht, slot_top, (0, 0, 1)) + fill(P, [ob] + hb, slot_bot, (0, 0, 1)) + tube(P, ob, ot, slot_side)
    for a, b in zip(hb, ht): faces += tube(P, a, b, slot_hole)
    P.comp.append((cname, faces, ground))

def bolt(P, p0, axis, r=0.008, h=0.010, sunk=0.003):
    a = Vector(axis).normalized(); p0 = Vector(p0)
    ref = (0, 0, 1) if abs(a.z) < 0.9 else (1, 0, 0)
    sweep(P, 'bolt', p0 - a * sunk, p0 + a * h, ngon(r, 6, math.pi / 2), [(0, 1, 0), (1, 0.75, 0)], METAL, METAL, METAL_L, ref=ref)

def oct_rod(P, cname, p0, p1, radii, slot, slot_cap, n=8, ref=(0, 0, 1)):
    """octagonal rod along p0->p1, radii = [(t, r)]"""
    r0 = max(r for _, r in radii)
    sweep(P, cname, p0, p1, ngon(r0, n, math.pi / n), [(t, r / r0, 0) for t, r in radii], slot, slot_cap, slot_cap, ref=ref)

def rest_on_ground(P):
    """tilt about X so the lowest point of the front half and of the back half both touch z=0 (a tool lying on a table)"""
    # rigid body on a plane: it rests on the edge of the lower convex hull (YZ projection) that lies under the centre
    vs = list(P.bm.verts); yc = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    pts = sorted({(round(v.co.y, 6), round(v.co.z, 6)) for v in vs})
    hull = []
    for p in pts:                                               # monotone chain, lower hull
        while len(hull) >= 2 and (hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1]) - (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0]) <= 0:
            hull.pop()
        hull.append(p)
    p, q = next((a_, b_) for a_, b_ in zip(hull, hull[1:]) if a_[0] <= yc <= b_[0])
    a = math.atan2(-(q[1] - p[1]), q[0] - p[0])                 # rotate so p and q get the same height
    M = Matrix.Rotation(a, 4, 'X')                              # z' = y sin a + z cos a
    for v in vs: v.co = M @ v.co
    print(f'  rest tilt {math.degrees(a):.2f} deg')

def center_on_ground(P):
    vs = list(P.bm.verts)
    lo = [min(v.co[i] for v in vs) for i in range(3)]; hi = [max(v.co[i] for v in vs) for i in range(3)]
    off = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]))
    for v in vs: v.co -= off

# ---------------- TOL-01 cheese mold ----------------
def build_mold():
    P = Part('Body'); n = 12
    AB2, AB, T = 0.124, 0.113, 0.012           # base band apothem (proud 11 mm), wall apothem, wall thickness
    Z0, ZB, Z1, Z2, ZT, ZF = 0.005, 0.032, 0.071, 0.110, 0.150, 0.016
    prof = [(0.0, AB2 - 0.005), (Z0, AB2), (ZB, AB2), (ZB, AB), (Z1, AB), (Z2, AB), (ZT, AB),
            (ZT, AB - T), (Z2, AB - T), (Z1, AB - T), (ZB, AB - T), (ZF, AB - T)]
    slots = {0: CREAM_D, 1: CREAM_D, 2: CREAM_B, 3: CREAM, 4: CREAM, 5: CREAM, 6: CREAM_B, 7: CREAM_B, 8: CREAM_B, 9: CREAM_B, 10: CREAM_B}
    side = [k for k in range(n) if abs(math.cos(-math.pi / 2 + (k + 1) * 2 * math.pi / n)) > 0.99]   # facets facing +-X (handles)
    odd = sorted(set(side) | {k for k in range(n) if k % 2}); even = sorted(set(side) | {k for k in range(n) if not k % 2})
    HR = 0.0125                                  # 3 staggered rows, octagonal through-holes (as the ref)
    shell(P, 'wall', prof, n, lambda j, k: slots[j], CREAM_D, CREAM_D,
          holes={3: (HR, odd), 4: (HR, even), 5: (HR, odd), 9: (HR, odd), 8: (HR, even), 7: (HR, odd)},
          pairs=[(3, 9), (4, 8), (5, 7)], hole_slot=CREAM_IN, hn=8, a0=math.pi / 8)
    for sx in (-1, 1):                           # clean loop handles on bolted plates (TOL-04 style)
        zc = 0.112
        sweep(P, 'plate', (sx * (AB - 0.003), 0, zc), (sx * (AB + 0.010), 0, zc), chamf_rect(0.045, 0.060, 0.007),
              [(0, 1, 0), (0.7, 1, 0), (1, 0.85, 0)], METAL, METAL_D, METAL_L, ref=(0, 0, 1))
        bolt(P, (sx * (AB + 0.010), 0, zc), (sx, 0, 0), r=0.0095, h=0.009)
        pts = [Vector((sx * x, y, zc)) for x, y in ((AB + 0.006, -0.019), (AB + 0.016, -0.036), (AB + 0.041, -0.042), (AB + 0.048, -0.027),
                                                     (AB + 0.048, 0.027), (AB + 0.041, 0.042), (AB + 0.016, 0.036), (AB + 0.006, 0.019))]
        path_sweep(P, 'handle', pts, (0, 0, 1), [(0.007 * math.cos(i * math.pi / 3), 0.007 * math.sin(i * math.pi / 3)) for i in range(6)], METAL, METAL_D)
    return P

# ---------------- TOL-02 curd harp ----------------
def build_harp():
    P = Part('Body'); W, L, BW, TH, C = 0.240, 0.240, 0.020, 0.014, 0.030
    outer = chamf_rect(W, L, C); inner = chamf_rect(W - 2 * BW, L - 2 * BW, C * 0.55)
    P.torus_loft('frame', [[Vector((x, y, 0)) for x, y in outer], [Vector((x, y, TH)) for x, y in outer],
                           [Vector((x, y, TH)) for x, y in inner], [Vector((x, y, 0)) for x, y in inner]],
                 lambda j, k: (METAL, METAL_L, METAL_D, METAL_D)[j])
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)            # frame rests on the table: include it in the ground check
    yi = L / 2 - BW
    for x in (-0.072, -0.024, 0.024, 0.072):
        sweep(P, 'wire', (x, -yi - 0.006, 0.0085), (x, yi + 0.006, 0.0085), ngon(0.0034, 6, math.pi / 2), [(0, 1, 0), (1, 1, 0)],
              METAL_L, METAL_L, METAL_L, ref=(0, 0, 1))
        for sy in (-1, 1):            # plain 4-sided blocks (12 tris each)
            yb = sy * (yi + BW * 0.45)
            sweep(P, 'block', (x, yb, TH - 0.002), (x, yb, TH + 0.009), [(0.008, 0.008), (-0.008, 0.008), (-0.008, -0.008), (0.008, -0.008)],
                  [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_L, ref=(1, 0, 0))
    zf = TH / 2; zc = TH / 2 + 0.0065; y0 = L / 2      # handle axis slightly above the frame: frame edge + grip end are the supports
    sweep(P, 'stem', (0, y0 - 0.006, zf), (0, y0 + 0.040, zc), chamf_rect(0.012, 0.022, 0.002), [(0, 1.35, 0), (0.35, 1, 0), (1, 1, 0)],
          METAL, METAL_D, METAL_L, ref=(0, 0, 1))
    oct_rod(P, 'ferrule', (0, y0 + 0.034, zc), (0, y0 + 0.074, zc), [(0, 0.019), (1, 0.019)], RED, RED_D)
    bolt(P, (0, y0 + 0.054, zc + 0.019 * math.cos(math.pi / 8)), (0, 0, 1), r=0.0085, h=0.008)
    oct_rod(P, 'collar', (0, y0 + 0.070, zc), (0, y0 + 0.094, zc), [(0, 0.0175), (1, 0.0175)], WOOD_D, WOOD_DD)
    oct_rod(P, 'grip', (0, y0 + 0.090, zc), (0, y0 + 0.330, zc), [(0, 0.017), (0.3, 0.019), (0.78, 0.026), (0.92, 0.025), (1, 0.015)], HWOOD, WOOD)
    rest_on_ground(P); center_on_ground(P)
    return P

# ---------------- TOL-03 slotted cheese paddle ----------------
def build_spatula():
    P = Part('Body'); TH = 0.016; bm = P.bm
    out = [(-0.045, -0.085), (0.045, -0.085), (0.060, -0.070), (0.060, 0.035), (0.024, 0.085), (-0.024, 0.085), (-0.060, 0.035), (-0.060, -0.070)]
    slots_xy = [[(x - 0.0075, -0.060), (x + 0.0075, -0.060), (x + 0.0075, 0.032), (x - 0.0075, 0.032)] for x in (-0.031, 0.0, 0.031)]
    ob = [bm.verts.new((x, y, 0)) for x, y in out]; ot = [bm.verts.new((x, y, TH)) for x, y in out]
    sb = [[bm.verts.new((x, y, 0)) for x, y in s] for s in slots_xy]; st = [[bm.verts.new((x, y, TH)) for x, y in s] for s in slots_xy]
    faces = fill(P, [ot] + st, WOOD_M, (0, 0, 1)) + fill(P, [ob] + sb, WOOD_D, (0, 0, 1))
    faces += tube(P, ob, ot, WOOD_D)
    for a, b in zip(sb, st): faces += tube(P, a, b, WOOD_DD)
    P.comp.append(('blade', faces, True))
    zc = 0.020                     # collar bottom 3 mm above the blade bottom: the blade tip and the grip end are the two supports
    sweep(P, 'collar', (0, 0.080, zc), (0, 0.118, zc), chamf_rect(0.034, 0.048, 0.007), [(0, 1, 0), (1, 1, 0)], RED, RED_D, RED_D, ref=(0, 0, 1))
    oct_rod(P, 'grip', (0, 0.112, zc), (0, 0.565, zc), [(0, 0.0175), (0.55, 0.0195), (0.94, 0.024), (1, 0.020)], HWOOD, WOOD)
    rest_on_ground(P); center_on_ground(P)
    return P

# ---------------- TOL-04 curd colander ----------------
def build_colander():
    P = Part('Body'); n = 12; t = 0.008
    zb, z1, z2 = 0.024, 0.068, 0.136          # deeper bowl: the ref shows two hole rows below a narrow rim band
    a0, a1, a2 = 0.068, 0.110, 0.126
    sl = (a1 - a0) / (z1 - zb); zf = zb + t
    prof = [(zb, a0), (z1, a1), (z2, a2), (z2, a2 - t), (z1, a1 - t), (zf, a1 - t - (z1 - zf) * sl)]
    side = [k for k in range(n) if abs(math.cos(-math.pi / 2 + (k + 1) * 2 * math.pi / n)) > 0.99]
    caph = [(0.0, 0.0, 0.0085)] + [(0.037 * math.cos(math.radians(30 + 60 * i)), 0.037 * math.sin(math.radians(30 + 60 * i)), 0.0085) for i in range(6)]
    shell(P, 'bowl', prof, n, lambda j, k: (CREAM, CREAM, CREAM_B, CREAM_B, CREAM_B)[j], CREAM_D, CREAM_B,
          holes={0: (0.0105, ()), 1: (0.0105, side), 3: (0.0105, side), 4: (0.0105, ())}, pairs=[(0, 4), (1, 3)], hole_slot=CREAM_IN, cap_holes=caph, ground=False)
    # grey rim band wrapping the wall top (its lower inner edge sunk inside the wall: outer wall apothem at z 0.121 ~ 0.1215)
    P.torus_loft('rim', [ringco(0.121, 0.119, n), ringco(0.121, 0.131, n), ringco(0.143, 0.133, n), ringco(0.143, 0.114, n), ringco(0.133, 0.114, n)],
                 lambda j, k: (METAL_D, METAL, METAL_L, METAL_D, METAL_D)[j])
    # foot ring (flared)
    P.torus_loft('foot', [ringco(0.0, 0.050, n), ringco(0.0, 0.068, n), ringco(0.005, 0.068, n), ringco(zb, 0.058, n), ringco(zb, 0.050, n)],
                 lambda j, k: (FOOT, FOOT, FOOT, METAL_D, FOOT)[j])
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)
    zc = 0.130
    for sx in (-1, 1):
        sweep(P, 'plate', (sx * 0.129, 0, zc), (sx * 0.142, 0, zc), chamf_rect(0.034, 0.050, 0.007), [(0, 1, 0), (0.7, 1, 0), (1, 0.85, 0)],
              METAL, METAL_D, METAL_L, ref=(0, 0, 1))
        bolt(P, (sx * 0.142, 0, zc), (sx, 0, 0), r=0.0085, h=0.009)
        pts = [Vector((sx * x, y, zc)) for x, y in ((0.137, -0.019), (0.146, -0.034), (0.160, -0.040), (0.168, -0.026),
                                                     (0.168, 0.026), (0.160, 0.040), (0.146, 0.034), (0.137, 0.019))]
        path_sweep(P, 'handle', pts, (0, 0, 1), [(0.009 * math.cos(i * math.pi / 3), 0.009 * math.sin(i * math.pi / 3)) for i in range(6)],
                   RED, RED_D)
    return P

# ---------------- TOL-05 ladle ----------------
def build_ladle():
    P = Part('Body'); n = 12
    prof = [(0.0, 0.046), (0.028, 0.068), (0.084, 0.078), (0.084, 0.071), (0.032, 0.061), (0.010, 0.041)]   # review: bowl ~1.35x
    shell(P, 'bowl', prof, n, lambda j, k: (METAL, METAL, METAL_L, METAL_D, METAL_D)[j], METAL_D, METAL_D)
    ang = math.radians(25); d = Vector((0, math.cos(ang), math.sin(ang)))
    base = Vector((0, 0.074, 0.068))
    sweep(P, 'bracket', base, base + Vector((0, 0.028, 0)), chamf_rect(0.036, 0.040, 0.006), [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_L, ref=(0, 0, 1))
    bolt(P, base + Vector((0, 0.014, 0.018)), (0, 0, 1), r=0.011, h=0.009)
    s0 = base + Vector((0, 0.022, 0.0)); s1 = s0 + d * 0.095
    sweep(P, 'shaft', s0, s1, chamf_rect(0.016, 0.024, 0.003), [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_L, ref=(0, 0, 1))
    f0 = s1 - d * 0.006; f1 = f0 + d * 0.034
    oct_rod(P, 'ferrule', f0, f1, [(0, 0.020), (1, 0.020)], RED, RED_D, ref=(1, 0, 0))
    oct_rod(P, 'grip', f1 - d * 0.004, f1 + d * 0.130, [(0, 0.017), (0.6, 0.021), (0.93, 0.022), (1, 0.014)], HWOOD, WOOD, ref=(1, 0, 0))
    center_on_ground(P)
    return P

# ---------------- TOL-11 cheese knife ----------------
def build_knife():
    P = Part('Body'); TH = 0.006
    # wide spade blade whose base runs straight into the bolster (no visible tang)
    TH = 0.008
    out = [(0.0, -0.152), (0.019, -0.130), (0.033, -0.100), (0.039, -0.070), (0.035, -0.040), (0.019, -0.016), (0.011, 0.002),
           (-0.011, 0.002), (-0.019, -0.016), (-0.035, -0.040), (-0.039, -0.070), (-0.033, -0.100), (-0.019, -0.130)]
    ins = pc.inset(out, 0.007)                                   # bevelled cutting edge: vertical 2.5 mm, then a 7 mm slope to the face
    hc = ((0.0, -0.101), (0.0, -0.071), (0.0, -0.042))
    bm = P.bm
    ob = [bm.verts.new((x, y, 0.0)) for x, y in out]; om = [bm.verts.new((x, y, 0.0025)) for x, y in out]
    ot = [bm.verts.new((x, y, TH)) for x, y in ins]
    hb = [hole_loop(P, Vector((x, y, 0.0)), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.0105, 8, math.pi / 8) for x, y in hc]
    ht = [hole_loop(P, Vector((x, y, TH)), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.0105, 8, math.pi / 8) for x, y in hc]
    faces = fill(P, [ot] + ht, METAL, (0, 0, 1)) + fill(P, [ob] + hb, METAL_D, (0, 0, 1)) + tube(P, ob, om, METAL_D) + tube(P, om, ot, METAL_L)
    for a, b in zip(hb, ht): faces += tube(P, a, b, METAL_D)
    P.comp.append(('blade', faces, True))
    zc = 0.0215                    # bolster bottom just above the blade bottom: blade tip and grip end are the supports
    oct_rod(P, 'bolster', (0, -0.010, zc), (0, 0.016, zc), [(0, 0.018), (0.25, 0.021), (0.75, 0.021), (1, 0.018)], FOOT, METAL_D)
    oct_rod(P, 'grip', (0, 0.014, zc), (0, 0.158, zc), [(0, 0.016), (0.25, 0.017), (0.8, 0.0235), (0.93, 0.023), (1, 0.013)], HWOOD, WOOD)
    sweep(P, 'rivet', (0, 0.125, zc + 0.0205), (0, 0.125, zc + 0.0265), chamf_rect(0.012, 0.012, 0.002), [(0, 1, 0), (1, 0.8, 0)],
          RED, RED_D, RED, ref=(1, 0, 0))
    rest_on_ground(P); center_on_ground(P)
    return P

# ---------------- TOL-12 ceramic bowl ----------------
def build_bowl():
    P = Part('Body'); n = 16
    prof = [(0.0, 0.084), (0.024, 0.082), (0.024, 0.096), (0.050, 0.125), (0.080, 0.1453), (0.118, 0.163), (0.128, 0.164),
            (0.128, 0.146), (0.118, 0.143), (0.060, 0.112), (0.034, 0.080)]
    sl = {0: FOOT, 1: METAL_D, 2: CREAM, 3: RED, 4: CREAM, 5: CREAM, 6: CREAM_B, 7: CREAM_D, 8: CREAM_B, 9: CREAM_B}
    shell(P, 'bowl', prof, n, lambda j, k: sl[j], FOOT, CREAM_B)
    return P

# ---------------- TOL-13 bread peel ----------------
def build_peel():
    P = Part('Body'); TH = 0.018
    head = [(-0.068, -0.17), (0.068, -0.17), (0.1473, -0.14), (0.17, -0.08), (0.17, 0.15), (-0.17, 0.15), (-0.17, -0.08), (-0.1473, -0.14)]
    flat_plate(P, 'head', head, 0.0, TH, [], CREAM_B, CREAM_D, CREAM_D, CREAM_D)
    zc = 0.017
    # neck: constant thickness, widening only in X toward the head (explicit rings; sweep would scale the thickness too)
    nk = [(0.090, 0.160), (0.150, 0.130), (0.250, 0.046), (0.290, 0.044)]          # broad shoulder starting under the strap -> shaft
    P.loft('neck', [[Vector((x, y, zc + z)) for x, z in chamf_rect(w, 0.036, 0.005)] for y, w in nk], WOOD, WOOD_M, WOOD_M)
    sweep(P, 'strap', (0, 0.085, 0.010), (0, 0.122, 0.010), [(0.0275, 0.088), (-0.002, 0.088), (-0.002, -0.088), (0.0275, -0.088)],
          [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_L, ref=(0, 0, 1))
    for x in (-0.046, 0.046): bolt(P, (x, 0.1035, 0.0375), (0, 0, 1), r=0.009, h=0.007)
    sweep(P, 'shaft', (0, 0.280, zc), (0, 1.115, zc), chamf_rect(0.036, 0.044, 0.005), [(0, 1, 0), (1, 1, 0)], WOOD, WOOD_M, WOOD_M, ref=(0, 0, 1))
    sweep(P, 'ring', (0, 1.105, zc), (0, 1.150, zc), chamf_rect(0.040, 0.048, 0.006), [(0, 1, 0), (1, 1, 0)], RED, RED_D, RED_D, ref=(0, 0, 1))
    oct_rod(P, 'knob', (0, 1.142, zc), (0, 1.230, zc), [(0, 0.020), (0.35, 0.030), (0.8, 0.029), (1, 0.016)], WOOD_D, WOOD_DD)
    rest_on_ground(P); center_on_ground(P)
    return P

# ---------------- TOL-14 rolling pin ----------------
def build_pin():
    P = Part('Body'); r = 0.040 / math.cos(math.pi / 8)          # 8-gon with apothem 4 cm (8 cm thick)
    L, B = 0.135, 0.020                                           # half body length, end band length
    zc = 0.040
    oct_rod(P, 'body', (0, -L, zc), (0, L, zc), [(0, r), (1, r)], CREAM_B, CREAM_D)
    for s in (-1, 1):
        oct_rod(P, 'band', (0, s * L, zc), (0, s * (L + B), zc), [(0, r), (0.55, r), (1, r * 0.80)], FOOT, FOOT)
        oct_rod(P, 'washer', (0, s * (L + B - 0.002), zc), (0, s * (L + B + 0.012), zc), [(0, 0.024), (1, 0.024)], RED, RED_D)
        oct_rod(P, 'handle', (0, s * (L + B + 0.010), zc), (0, s * (L + B + 0.097), zc),
                [(0, 0.012), (0.3, 0.0125), (0.72, 0.021), (0.9, 0.0215), (1, 0.014)], HWOOD, WOOD)
    center_on_ground(P)
    return P

# ---------------- TOL-15 smoking hook ----------------
def build_hook():
    P = Part('Body'); Y = (0, 1, 0)
    sq = [(0.0085, 0.0045), (0.0045, 0.0085), (-0.0045, 0.0085), (-0.0085, 0.0045),
          (-0.0085, -0.0045), (-0.0045, -0.0085), (0.0045, -0.0085), (0.0085, -0.0045)]
    ec = Vector((0.0, 0.0, 0.132)); er = 0.021
    eye = [ec + Vector((er * math.cos(math.pi / 8 + i * math.pi / 4), 0, er * math.sin(math.pi / 8 + i * math.pi / 4))) for i in range(8)]
    path_sweep(P, 'eye', eye, Y, [(x * 0.95, y * 0.85) for x, y in sq], METAL, METAL_D, closed=True)
    pts = [Vector((x, 0, z)) for x, z in ((0.004, 0.106), (-0.012, 0.093), (-0.016, 0.078), (-0.006, 0.066), (0.016, 0.053),
                                          (0.027, 0.034), (0.022, 0.014), (0.006, 0.004), (-0.012, 0.009), (-0.021, 0.024), (-0.021, 0.040))]
    path_sweep(P, 'hook', pts, Y, sq, METAL, METAL_L)
    sweep(P, 'clamp', (0.002, 0.0, 0.094), (0.002, 0.0, 0.120), chamf_rect(0.028, 0.024, 0.003), [(0, 1, 0), (1, 1, 0)], RED, RED_D, RED_D, ref=(1, 0, 0))
    bolt(P, (0.002, -0.012, 0.107), (0, -1, 0), r=0.0075, h=0.006)
    center_on_ground(P)
    return P

# ---------------- TOL-16 oven tongs ----------------
def build_tongs():
    P = Part('Body'); Z = (0, 0, 1)
    sec = [(0.008, -0.006), (0.008, 0.006), (-0.008, 0.006), (-0.008, -0.006)]          # arm bar 16 x 12 mm
    PV = Vector((0, -0.055, 0))
    for s in (1, -1):                       # s=+1: jaw on +x, handle on -x (lower layer); s=-1 mirrored, raised over the pivot
        zl = 0.006 if s == 1 else 0.018
        pts = [Vector(p) for p in ((s * 0.014, -0.165, 0.006), (s * 0.010, -0.120, 0.006), (s * 0.003, -0.078, zl), (0, -0.055, zl),
                                   (-s * 0.006, -0.032, zl), (-s * 0.030, 0.012, 0.006), (-s * 0.036, 0.060, 0.006))]
        path_sweep(P, 'arm', pts, Z, sec, METAL, METAL_D)
        jaw = [(0.002, -0.250), (0.052, -0.250), (0.058, -0.236), (0.050, -0.190), (0.024, -0.150), (0.004, -0.150)]
        if s < 0: jaw = [(-x, y) for x, y in reversed(jaw)]
        flat_plate(P, 'jaw', jaw, 0.0, 0.016, [], METAL_L, METAL_D, METAL, METAL)
        g0, g1 = Vector((-s * 0.035, 0.052, 0.006)), Vector((-s * 0.052, 0.245, 0.006)); g = lambda t: g0.lerp(g1, t)
        oct_rod(P, 'collar', g(0.0), g(0.17), [(0, 0.017), (1, 0.019)], WOOD_D, WOOD_DD)
        oct_rod(P, 'grip', g(0.15), g(1.0), [(0, 0.019), (0.35, 0.021), (0.9, 0.021), (1, 0.014)], HWOOD, WOOD)
        oct_rod(P, 'band', g(0.52), g(0.64), [(0, 0.0225), (1, 0.0225)], RED, RED_D)
    oct_rod(P, 'pivot', PV, PV + Vector((0, 0, 0.026)), [(0, 0.017), (1, 0.017)], FOOT, FOOT, ref=(1, 0, 0))
    bolt(P, PV + Vector((0, 0, 0.026)), (0, 0, 1), r=0.011, h=0.008)
    rest_on_ground(P); center_on_ground(P)
    return P

# ---------------- TOL-17 honeycomb frame ----------------
def build_comb():
    """built lying (local Y = height, local Z = thickness), then stood up"""
    P = Part('Body')
    def box(cn, x0, x1, y0, y1, z0, z1, side, cap, c=0.003):
        rect_prism(P, cn, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, c, [(z0, 0), (z1, 0)], side, cap, cap)
    box('top', -0.180, 0.180, 0.095, 0.125, -0.019, 0.019, WOOD_M, WOOD)
    for sx in (-1, 1):
        box('lug', min(sx * 0.165, sx * 0.200), max(sx * 0.165, sx * 0.200), 0.088, 0.132, -0.023, 0.023, WOOD_M, WOOD)
        box('side', min(sx * 0.165, sx * 0.185), max(sx * 0.165, sx * 0.185), -0.115, 0.096, -0.017, 0.017, WOOD_D, WOOD_M)
        x0, x1 = sorted((sx * 0.168, sx * 0.197))
        sweep(P, 'cap', ((x0 + x1) / 2, 0.130, 0), ((x0 + x1) / 2, 0.146, 0), chamf_rect(0.036, 0.029, 0.005), [(0, 1, 0), (1, 0.8, 0)],
              RED, RED_D, RED, ref=(0, 0, 1))
    box('bottom', -0.185, 0.185, -0.127, -0.105, -0.017, 0.017, WOOD_M, WOOD)
    # comb panel: flat-top hex cells recessed into both faces
    bm = P.bm; T = 0.012; HX0, HX1, HY0, HY1 = -0.1655, 0.1655, -0.1055, 0.0955
    out = [(HX0, HY0), (HX1, HY0), (HX1, HY1), (HX0, HY1)]
    Rh = 0.026; rc = Rh - 0.004 / math.sqrt(3); cy = (HY0 + HY1) / 2; cells = []
    for k in range(-5, 6):
        off = 0.0 if k % 2 == 0 else math.sqrt(3) * Rh / 2
        for m in range(-5, 6):
            x, y = k * 1.5 * Rh, cy + off + m * math.sqrt(3) * Rh
            if abs(x) < HX1 + Rh * 0.4 and HY0 - Rh * 0.4 < y < HY1 + Rh * 0.4: cells.append((x, y))
    # Extend boundary cells to the timber rim; inset the bounded honey grid
    # by 2 mm on each side so adjoining cells leave uniform 4 mm webs.
    cell_outlines = []
    for cx, cy_ in cells:
        poly = list(out)
        for ox, oy in cells:
            if (ox, oy) == (cx, cy_): continue
            nx, ny = ox - cx, oy - cy_
            limit = (ox * ox + oy * oy - cx * cx - cy_ * cy_) / 2
            clipped = []
            for A, B in zip(poly, poly[1:] + poly[:1]):
                da = A[0] * nx + A[1] * ny - limit
                db = B[0] * nx + B[1] * ny - limit
                if da <= 1e-10: clipped.append(A)
                if (da < -1e-10 and db > 1e-10) or (da > 1e-10 and db < -1e-10):
                    f = da / (da - db)
                    clipped.append((A[0] + f * (B[0] - A[0]), A[1] + f * (B[1] - A[1])))
            poly = clipped
        # Drop coincident/collinear corners before offsetting the convex cell.
        clean = []
        for i, B in enumerate(poly):
            A, C = poly[i - 1], poly[(i + 1) % len(poly)]
            if abs((B[0]-A[0])*(C[1]-B[1])-(B[1]-A[1])*(C[0]-B[0])) > 1e-10:
                clean.append(B)
        cell_outlines.append(pc.inset(clean, 0.002))
    faces = []
    ob = [bm.verts.new((x, y, -T)) for x, y in out]; ot = [bm.verts.new((x, y, T)) for x, y in out]
    for zf, ring, nz in ((T, ot, 1), (-T, ob, -1)):
        hls = [[bm.verts.new((x, y, zf)) for x, y in poly] for poly in cell_outlines]
        faces += fill(P, [ring] + hls, CREAM_B, (0, 0, nz))
        for hl in hls: faces += blind(P, hl, Vector((0, 0, nz)), 0.006, CREAM_IN, FOOT)
    faces += tube(P, ob, ot, CREAM_IN)
    P.comp.append(('comb', faces, False))
    print(f'  comb cells per face: {len(cells)}')
    M = Matrix.Rotation(math.radians(90), 4, 'X')               # local Y (height) -> Z, local +Z (front face) -> -Y
    for v in bm.verts: v.co = M @ v.co
    center_on_ground(P)
    return P

# ---------------- TOL-18 oil strainer funnel on a tripod ----------------
def build_strainer():
    P = Part('Body'); n = 12; ZR = 0.215
    leg_top, leg_bot = 0.098, 0.150
    def leg_pt(u, z): return u * (leg_bot + (leg_top - leg_bot) * z / ZR) + Vector((0, 0, z))
    us = [Vector((math.cos(math.radians(-90 + 120 * i)), math.sin(math.radians(-90 + 120 * i)), 0)) for i in range(3)]
    for u in us:
        sweep(P, 'leg', leg_pt(u, 0.0), leg_pt(u, ZR - 0.030), chamf_rect(0.046, 0.046, 0.006), [(0, 1, 0), (1, 1, 0)], WOOD, WOOD_M, WOOD_M,
              ref=(u.x, u.y, 0), flat0=True, ground=True)
        sweep(P, 'head', leg_pt(u, ZR - 0.034) , leg_pt(u, ZR - 0.034) + Vector((0, 0, 0.050)), chamf_rect(0.060, 0.060, 0.008),
              [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(u.x, u.y, 0))
        hc = leg_pt(u, ZR - 0.034) + Vector((0, 0, 0.025))
        sweep(P, 'cap', hc + u * 0.027, hc + u * 0.037, chamf_rect(0.018, 0.018, 0.003), [(0, 1, 0), (1, 0.8, 0)], RED, RED_D, RED, ref=(0, 0, 1))
    for i in range(3):
        a, b = leg_pt(us[i], 0.070), leg_pt(us[(i + 1) % 3], 0.070)
        sweep(P, 'stretcher', a, b, chamf_rect(0.030, 0.030, 0.004), [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_D, WOOD_D, ref=(0, 0, 1))
    P.torus_loft('ring', [ringco(ZR - 0.0312, 0.056, n), ringco(ZR - 0.0312, 0.1314, n), ringco(ZR, 0.1314, n), ringco(ZR, 0.056, n)],
                 lambda j, k: (WOOD_D, WOOD_M, WOOD, WOOD_M)[j])
    # funnel bowl (vertex at 180 deg for the spout), resting on the ring's inner top edge
    nv0 = len(P.bm.verts)
    prof = [(0.165, 0.020), (0.300, 0.115), (0.330, 0.122), (0.336, 0.122), (0.336, 0.112), (0.300, 0.106), (0.182, 0.023)]
    shell(P, 'bowl', prof, n, lambda j, k: (METAL, METAL, METAL, METAL_L, METAL_D, METAL_D)[j], METAL_D, METAL_D, ground=False, phase=0.0)
    P.bm.verts.ensure_lookup_table()
    for v in list(P.bm.verts)[nv0:]:                             # spout: pull the -X rim out into a V lip
        rr = math.hypot(v.co.x, v.co.y); ang = math.degrees(math.atan2(v.co.y, v.co.x)) % 360
        if rr < 0.08 or v.co.z < 0.29: continue
        k = 1.0 if abs(ang - 180) < 1 else (0.22 if abs(ang - 180) < 31 else 0.0)
        push = (0.046 if v.co.z > 0.32 else 0.018) * k
        v.co += Vector((-push, 0, 0.007 * k if v.co.z > 0.32 else 0))
    oct_rod(P, 'stem', (0, 0, 0.112), (0, 0, 0.172), [(0, 0.015), (1, 0.015)], METAL, METAL_D, ref=(1, 0, 0))
    oct_rod(P, 'collar', (0, 0, 0.150), (0, 0, 0.168), [(0, 0.024), (1, 0.024)], FOOT, METAL_D, ref=(1, 0, 0))
    # perforated filter disc (blind holes) with a lip and three clamps
    bm = P.bm; z0, z1 = 0.296, 0.308; dap = 0.100                # review: filter raised 2 cm so it reads
    rim = ringco(z1, dap, n); rimb = ringco(z0, dap, n)
    ot = [bm.verts.new(v) for v in rim]; ob = [bm.verts.new(v) for v in rimb]
    cen = [(0.0, 0.0)] + [(r * math.cos(math.radians(360 / k * i + o)), r * math.sin(math.radians(360 / k * i + o)))
                          for r, k, o in ((0.022, 6, 0), (0.044, 12, 15), (0.066, 18, 0)) for i in range(k)]   # 37 holes
    hls = [hole_loop(P, Vector((x, y, z1)), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.0072, 6) for x, y in cen]
    faces = fill(P, [ot] + hls, FOOT, (0, 0, 1)) + fill(P, [ob], METAL_D, (0, 0, 1)) + tube(P, ob, ot, METAL_D)
    for hl in hls: faces += blind(P, hl, Vector((0, 0, 1)), 0.008, METAL_D, METAL_D)
    P.comp.append(('filter', faces, False))
    P.torus_loft('lip', [ringco(z1 - 0.002, 0.083, n), ringco(z1 - 0.002, 0.099, n), ringco(z1 + 0.010, 0.099, n), ringco(z1 + 0.010, 0.083, n)],
                 lambda j, k: (METAL_D, CREAM_D, FOOT, CREAM_D)[j])
    for ad in (90, 210, 330):
        u = Vector((math.cos(math.radians(ad)), math.sin(math.radians(ad)), 0))
        sweep(P, 'clamp', u * 0.078 + Vector((0, 0, z1 + 0.015)), u * 0.101 + Vector((0, 0, z1 + 0.015)), chamf_rect(0.026, 0.026, 0.005),
              [(0, 1, 0), (1, 1, 0)], FOOT, CREAM_D, CREAM_D, ref=(0, 0, 1))
    AB = 0.122; zc = 0.318
    sweep(P, 'plate', (AB - 0.004, 0, zc), (AB + 0.008, 0, zc), chamf_rect(0.030, 0.046, 0.006), [(0, 1, 0), (1, 0.85, 0)], METAL, METAL_D, METAL_L, ref=(0, 0, 1))
    bolt(P, (AB + 0.008, 0, zc), (1, 0, 0), r=0.008, h=0.008)
    pts = [Vector(p) for p in ((AB + 0.004, -0.017, zc), (AB + 0.026, -0.030, 0.336), (AB + 0.046, -0.022, 0.364),
                               (AB + 0.046, 0.022, 0.364), (AB + 0.026, 0.030, 0.336), (AB + 0.004, 0.017, zc))]
    path_sweep(P, 'handle', pts, (0, 0, 1), [(0.008 * math.cos(i * math.pi / 3), 0.008 * math.sin(i * math.pi / 3)) for i in range(6)], METAL, METAL_D)
    return P

# ---------------- PRD-01 fresh cheese in a perforated mold ----------------
def build_cheese_mold():
    P = Part('Body'); n = 16
    prof = [(0.0, 0.121), (0.006, 0.125), (0.064, 0.125), (0.122, 0.125), (0.130, 0.125), (0.130, 0.113), (0.112, 0.113),
            (0.140, 0.107), (0.158, 0.088), (0.167, 0.055)]          # review: the dome rises ~3.5 cm above the rim, as in the ref
    sl = (METAL_D, METAL, METAL, METAL, METAL_L, METAL_D, CREAM, CREAM_B, CREAM_B)
    odd = [k for k in range(n) if k % 2]; even = [k for k in range(n) if not k % 2]
    shell(P, 'mold', prof, n, lambda j, k: sl[j], METAL_D, CREAM_B, holes={1: (0.0145, odd, 0.012, CREAM), 2: (0.0145, even, 0.012, CREAM)},
          hole_slot=METAL_D, hn=8, a0=math.pi / 8)
    return P

# ---------------- PRD-02 cheese wheel with a wedge removed ----------------
def build_cut_wheel():
    P = Part('Body'); bm = P.bm; R0, H, c = 0.172, 0.150, 0.014
    cut, half, nseg = math.radians(-55), math.radians(33), 10
    t1, t2 = cut + half, cut - half + 2 * math.pi
    angs = [t1 + (t2 - t1) * i / nseg for i in range(nseg + 1)]
    zs = [(0.0, R0 - c), (c, R0), (H - c, R0), (H, R0 - c)]
    C = [bm.verts.new((0, 0, z)) for z, _ in zs]
    A = [[bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in angs] for z, r in zs]
    faces = []
    for j in range(3):
        for i in range(nseg): faces.append(P.face([A[j][i], A[j][i + 1], A[j + 1][i + 1], A[j + 1][i]], (RED_D, RED_D, RED)[j]))
    faces.append(P.face([C[3]] + A[3], RED)); faces.append(P.face(list(reversed([C[0]] + A[0])), RED_D))
    eyes = {0: [(0.045, 0.104, 0.010), (0.095, 0.110, 0.016), (0.058, 0.058, 0.009), (0.126, 0.072, 0.010), (0.098, 0.040, 0.015), (0.142, 0.030, 0.007)],
            1: [(0.050, 0.082, 0.012), (0.108, 0.104, 0.014), (0.130, 0.046, 0.011), (0.074, 0.034, 0.008)]}
    for side, (t, idx) in enumerate(((t1, 0), (t2, nseg))):
        d = Vector((math.cos(t), math.sin(t), 0))
        n_out = Vector((math.sin(t), -math.cos(t), 0)) if side == 0 else Vector((-math.sin(t), math.cos(t), 0))
        outer = [C[0], A[0][idx], A[1][idx], A[2][idx], A[3][idx], C[3], C[2], C[1]]
        q = lambda s, z: d * s + Vector((0, 0, z))
        inner = [bm.verts.new(q(s, z)) for s, z in ((0.006, 0.005), (R0 - 0.010, 0.005), (R0 - 0.010, H - 0.008), (0.006, H - 0.008))]
        faces += fill(P, [outer, inner], RED_D, n_out)
        hls = [hole_loop(P, q(s, z), d, Vector((0, 0, 1)), r, 6) for s, z, r in eyes[side]]
        faces += fill(P, [inner] + hls, CREAM_B, n_out)
        for hl in hls: faces += blind(P, hl, n_out, 0.009, CREAM_IN, CREAM_D)
    P.comp.append(('wheel', faces, True))
    return P

# ---------------- PRD-18 honey crock with dipper ----------------
def build_honey_crock():
    P = Part('Body'); n = 12
    prof = [(0.0, 0.062), (0.012, 0.074), (0.084, 0.10752), (0.115, 0.103), (0.145, 0.078), (0.152, 0.076), (0.160, 0.085),
            (0.180, 0.085), (0.186, 0.079), (0.186, 0.068), (0.166, 0.065), (0.150, 0.067)]
    sl = (CREAM_D, CREAM, RED, CREAM, CREAM_D, CREAM_D, CREAM_B, CREAM_B, CREAM_B, CREAM_D, CREAM_D)
    shell(P, 'crock', prof, n, lambda j, k: sl[j], CREAM_D, FOOT)
    # dipper: grooved head resting in the honey, handle across the back-right rim
    d = Vector((1, 1, 0)).normalized(); H = Vector((-0.018, -0.018, 0.163))
    t_rim = (0.018 * math.sqrt(2) + 0.0845)                      # horizontal distance from H to the rim crossing
    slope = (0.186 + 0.010625 - H.z) / t_rim
    ax = (d + Vector((0, 0, slope))).normalized()
    s0 = H - ax * 0.032
    for i in range(5):
        a = s0 + ax * (i * 0.015625)
        oct_rod(P, 'disc', a, a + ax * 0.01125, [(0, 0.03125), (1, 0.03125)], WOOD, WOOD_M, ref=(0, 0, 1))
    oct_rod(P, 'core', s0 - ax * 0.002, s0 + ax * 0.080, [(0, 0.015), (1, 0.015)], WOOD_M, WOOD_M, ref=(0, 0, 1))
    oct_rod(P, 'handle', s0 + ax * 0.0725, s0 + ax * 0.245, [(0, 0.010625), (0.85, 0.010625), (0.88, 0.015625), (1, 0.0125)], HWOOD, WOOD, ref=(0, 0, 1))
    return P

# ---------------- furniture helpers ----------------
def box(P, cn, x0, x1, y0, y1, z0, z1, side, top, c=0.006, ground=False):
    rect_prism(P, cn, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, c, [(z0, 0), (z1, 0)], side, top, top, ground=ground)

def plain_box(P, cn, x0, x1, y0, y1, z0, z1, side, top):
    """4-sided box (12 tris) for slats/caps"""
    sweep(P, cn, ((x0 + x1) / 2, (y0 + y1) / 2, z0), ((x0 + x1) / 2, (y0 + y1) / 2, z1),
          [((x1 - x0) / 2, (y1 - y0) / 2), (-(x1 - x0) / 2, (y1 - y0) / 2), (-(x1 - x0) / 2, -(y1 - y0) / 2), ((x1 - x0) / 2, -(y1 - y0) / 2)],
          [(0, 1, 0), (1, 1, 0)], side, top, top, ref=(1, 0, 0))

def splay_leg(P, foot, top, s=0.10, c=0.012):
    sweep(P, 'leg', foot, top, chamf_rect(s, s, c), [(0, 1, 0), (1, 1, 0)], WOOD, WOOD_M, WOOD_M, ref=(0, 1, 0), flat0=True, ground=True)

def red_cap(P, x, y_face, z, size=0.050, t=0.012):
    plain_box(P, 'cap', x - size / 2, x + size / 2, y_face - t, y_face + 0.002, z - size / 2, z + size / 2, RED, RED_D)

# ---------------- FUR-01 cheesemaker's workbench (stone top) ----------------
def build_workbench():
    P = Part('Body'); ZT = 0.80
    for sx in (-1, 1):
        for sy in (-1, 1):
            splay_leg(P, Vector((sx * 0.70, sy * 0.25, 0)), Vector((sx * 0.62, sy * 0.25, ZT - 0.10)), s=0.13)
            box(P, 'head', sx * 0.62 - 0.075, sx * 0.62 + 0.075, sy * 0.25 - 0.075, sy * 0.25 + 0.075, ZT - 0.115, ZT, WOOD, WOOD_M)
            if sy < 0: red_cap(P, sx * 0.62, -0.25 - 0.075, ZT - 0.057, size=0.064)
        box(P, 'apron_s', sx * 0.62 - 0.03, sx * 0.62 + 0.03, -0.184, 0.184, ZT - 0.095, ZT - 0.005, WOOD_M, WOOD_M, c=0.004)
        # side stretcher of the lower shelf
        box(P, 'shelf_s', sx * 0.672 - 0.03, sx * 0.672 + 0.03, -0.20, 0.20, 0.200, 0.255, WOOD_D, WOOD_M, c=0.004)
    for sy in (-1, 1):
        box(P, 'apron', -0.554, 0.554, sy * 0.25 - 0.03, sy * 0.25 + 0.03, ZT - 0.095, ZT - 0.005, WOOD_M, WOOD_M, c=0.004)
        box(P, 'shelf_r', -0.640, 0.640, sy * 0.25 - 0.03, sy * 0.25 + 0.03, 0.200, 0.255, WOOD_D, WOOD_M, c=0.004)
    for i in range(6):                                             # shelf boards run front-back
        x0 = -0.600 + i * 0.2015; plain_box(P, 'slat', x0, x0 + 0.192, -0.22, 0.22, 0.255, 0.280, WOOD_D, WOOD_M)
    # pale stone top with chamfered corners and edge bevels
    # A few broad, shallow chips in plan; matching rings retain flat faces and bevels.
    rings = []
    for z, inset in [(ZT, 0.012), (ZT + 0.014, 0.0), (ZT + 0.086, 0.0), (ZT + 0.100, 0.014)]:
        outline = chamf_rect(1.60 - 2 * inset, 0.70 - 2 * inset, 0.07 - inset)
        ring = []
        for i, (x, y) in enumerate(outline):
            xx, yy = outline[(i + 1) % len(outline)]
            ring.append(Vector((x, y, z)))
            mx, my = (x + xx) / 2, (y + yy) / 2
            if abs(xx - x) > 0.5: my -= math.copysign(0.009, my)
            elif abs(yy - y) > 0.2: mx -= math.copysign(0.008, mx)
            else: continue  # keep the corner chamfers
            ring.append(Vector((mx, my, z)))
        rings.append(ring)
    P.loft('top', rings, CREAM_IN, FOOT, CREAM_IN)
    return P

# ---------------- FUR-02 bottling table (back rail, low front rim) ----------------
def build_bottling_table():
    P = Part('Body'); ZT = 0.80; W, D = 1.40, 0.60
    for sx in (-1, 1):
        for sy in (-1, 1):
            top_z = ZT + (0.20 if sy > 0 else 0.0)
            splay_leg(P, Vector((sx * 0.64, sy * 0.24, 0)), Vector((sx * 0.60, sy * 0.24, ZT - 0.10)), s=0.14)
            box(P, 'head', sx * 0.60 - 0.080, sx * 0.60 + 0.080, sy * 0.24 - 0.080, sy * 0.24 + 0.080, ZT - 0.12, top_z + 0.06, WOOD, WOOD_M, c=0.010)
            if sy < 0: red_cap(P, sx * 0.60, -0.24 - 0.080, ZT - 0.045, size=0.058)
        box(P, 'low_s', sx * 0.625 - 0.032, sx * 0.625 + 0.032, -0.19, 0.19, 0.16, 0.230, WOOD_D, WOOD_M, c=0.005)
        # side diagonal brace: from the low rail up to the apron
        sweep(P, 'brace', Vector((sx * 0.63, -0.17, 0.21)), Vector((sx * 0.60, 0.17, ZT - 0.08)), chamf_rect(0.055, 0.05, 0.006),
              [(0, 1, 0), (1, 1, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(1, 0, 0))
    for sy in (-1, 1):
        box(P, 'low', -0.585, 0.585, sy * 0.24 - 0.032, sy * 0.24 + 0.032, 0.16, 0.230, WOOD_D, WOOD_M, c=0.005)
    # top: frame border slightly raised (low front rim) + 3 pale planks on a dark bed
    fo = chamf_rect(W - 0.10, D - 0.06, 0.03); fi = chamf_rect(W - 0.10 - 0.10, D - 0.06 - 0.10, 0.012)
    P.torus_loft('frame', [[Vector((x, y, ZT - 0.06)) for x, y in fo], [Vector((x, y, ZT + 0.06)) for x, y in fo],
                           [Vector((x, y, ZT + 0.06)) for x, y in fi], [Vector((x, y, ZT - 0.06)) for x, y in fi]],
                 lambda j, k: (WOOD_M, WOOD, WOOD_M, WOOD_D)[j])
    pw = (D - 0.06 - 2 * 0.05 - 2 * 0.006) / 3
    for i in range(3):
        y0 = -(D - 0.06) / 2 + 0.05 + i * (pw + 0.006)
        plain_box(P, 'plank', -(W - 0.10) / 2 + 0.05, (W - 0.10) / 2 - 0.05, y0, y0 + pw, ZT + 0.020, ZT + 0.045, CREAM_D, CREAM_B)
    # inner bed (dark) under the planks, inside the frame
    plain_box(P, 'bed', -(W - 0.10) / 2 + 0.049, (W - 0.10) / 2 - 0.049, -(D - 0.06) / 2 + 0.049, (D - 0.06) / 2 - 0.049, ZT - 0.02, ZT + 0.021, WOOD_DD, WOOD_DD)
    # back board between the tall back heads
    box(P, 'back', -0.528, 0.528, 0.24 - 0.032, 0.24 + 0.032, ZT + 0.06, ZT + 0.22, WOOD_M, WOOD, c=0.006)
    return P

# ---------------- FUR-03 cheese aging shelf ----------------
def build_aging_shelf():
    P = Part('Body'); H = 1.80; L = [0.16, 0.60, 1.04, 1.48]
    for sx in (-1, 1):
        for sy in (-1, 1):
            rect_prism(P, 'post', sx * 0.56, sy * 0.20, 0.13, 0.13, 0.016, [(0.0, 0), (H - 0.04, 0), (H, 0.03)], WOOD, WOOD, WOOD, ground=True)
        for z in L:
            box(P, 'side', sx * 0.56 - 0.025, sx * 0.56 + 0.025, -0.155, 0.155, z - 0.05, z, WOOD_M, WOOD_M, c=0.004)
        for z0, z1 in zip(L[:-1], L[1:]):                           # side diagonal braces
            sweep(P, 'brace', Vector((sx * 0.585, -0.15, z0 + 0.01)), Vector((sx * 0.585, 0.15, z1 - 0.07)), chamf_rect(0.05, 0.045, 0.005),
                  [(0, 1, 0), (1, 1, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(1, 0, 0))
    for z in L:
        for sy in (-1, 1):
            box(P, 'rail', -0.515, 0.515, sy * 0.20 - 0.028, sy * 0.20 + 0.028, z - 0.06, z, WOOD, WOOD_M, c=0.004)
        for i in range(7):                                          # slats run front-back
            x0 = -0.505 + i * 0.1457; plain_box(P, 'slat', x0, x0 + 0.120, -0.22, 0.22, z, z + 0.024, WOOD_D, WOOD_M)
        for sx in (-1, 1): red_cap(P, sx * 0.56, -0.20 - 0.065, z - 0.030, size=0.058)
    return P

# ---------------- FUR-04 wall herb rail with pegs ----------------
def build_herb_rail():
    P = Part('Body')                                                 # back = wall plane y = 0, front -Y
    for sx in (-1, 1):
        # mounting board: flat plank against the wall with chamfered top/bottom corners (outline in XZ, thickness along Y)
        mo = [(-0.045, 0.0), (0.045, 0.0), (0.075, 0.045), (0.075, 0.255), (0.045, 0.30), (-0.045, 0.30), (-0.075, 0.255), (-0.075, 0.045)]
        P.loft('mount', [[Vector((sx * 0.48 + x, yy, z)) for x, z in mo] for yy in (-0.040, 0.0)], WOOD, WOOD_M, WOOD_M, ground=True)
        box(P, 'block', sx * 0.48 - 0.072, sx * 0.48 + 0.072, -0.125, -0.036, 0.085, 0.225, WOOD_M, WOOD, c=0.010)
        red_cap(P, sx * 0.48, -0.125, 0.155, size=0.056)
    box(P, 'rail', -0.418, 0.418, -0.112, -0.036, 0.095, 0.215, WOOD_M, WOOD_D, c=0.008)
    for i in range(6):
        x = -0.325 + i * 0.13; a = math.radians(10)
        p0 = Vector((x, -0.106, 0.155)); p1 = p0 + Vector((0, -math.cos(a), math.sin(a))) * 0.115
        oct_rod(P, 'peg', p0, p1, [(0, 0.028), (0.82, 0.030), (1, 0.020)], HWOOD, WOOD, ref=(0, 0, 1))
    return P

def basin_loft(P, cn, cx, cy, z_bot, z_top, z_flange, bot_wh, top_wh, fl_wh, in_wh, z_floor, c, out_slot, rim_slot, in_slot, floor_slot):
    """open rectangular basin: outer wall bottom->top, flange (outer lip), inner wall down to a floor (closed manifold)"""
    def R(z, wh, cc): return [Vector((cx + x, cy + y, z)) for x, y in chamf_rect(wh[0], wh[1], cc)]
    rings = [R(z_bot, bot_wh, c * 0.8), R(z_top, top_wh, c), R(z_top, fl_wh, c * 1.1), R(z_flange, fl_wh, c * 1.1),
             R(z_flange, in_wh, c * 0.9), R(z_floor, (in_wh[0] - 0.06, in_wh[1] - 0.06), c * 0.7)]
    P.loft(cn, rings, lambda j, k: (out_slot, rim_slot, rim_slot, rim_slot, in_slot)[j], out_slot, floor_slot)

# ---------------- FUR-05 pantry jar shelf ----------------
def build_pantry_shelf():
    P = Part('Body'); H = 1.42; L = [0.20, 0.68, 1.16]
    for sx in (-1, 1):
        for sy in (-1, 1):
            rect_prism(P, 'post', sx * 0.40, sy * 0.15, 0.12, 0.12, 0.016, [(0.0, 0), (H - 0.04, 0), (H, 0.03)], WOOD, WOOD, WOOD, ground=True)
        for z in L:
            box(P, 'side', sx * 0.40 - 0.022, sx * 0.40 + 0.022, -0.108, 0.108, z - 0.055, z - 0.005, WOOD_D, WOOD_M, c=0.004)
        for z0, z1 in zip(L[:-1], L[1:]):
            sweep(P, 'brace', Vector((sx * 0.425, -0.10, z0 + 0.02)), Vector((sx * 0.425, 0.10, z1 - 0.08)), chamf_rect(0.032, 0.026, 0.004),
                  [(0, 1, 0), (1, 1, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(1, 0, 0))
        red_cap(P, sx * 0.40, -0.15 - 0.06, H - 0.13, size=0.055); red_cap(P, sx * 0.40, -0.15 - 0.06, 0.10, size=0.055)
    for z in L:
        box(P, 'rail', -0.357, 0.357, -0.17, -0.12, z - 0.07, z - 0.005, WOOD_D, WOOD_M, c=0.004)
        box(P, 'board', -0.345, 0.345, -0.185, 0.17, z - 0.006, z + 0.060, CREAM_D, CREAM_B, c=0.012)
    # short grey back rail above the top shelf (chamfered top corners)
    bo = [(-0.357, L[-1] + 0.04), (0.357, L[-1] + 0.04), (0.357, L[-1] + 0.15), (0.31, L[-1] + 0.20), (-0.31, L[-1] + 0.20), (-0.357, L[-1] + 0.15)]
    P.loft('backrail', [[Vector((x, yy, z)) for x, z in bo] for yy in (0.13, 0.165)], CREAM_IN, FOOT, FOOT)
    return P

# ---------------- FUR-06 washstand with basin and hand pump (lever separate) ----------------
def build_washstand():
    P = Part('Body'); ZT = 0.70; TT = 0.07
    for sx in (-1, 1):
        for sy in (-1, 1):
            splay_leg(P, Vector((sx * 0.40, sy * 0.22, 0)), Vector((sx * 0.36, sy * 0.22, ZT - 0.08)), s=0.11)
            box(P, 'head', sx * 0.36 - 0.07, sx * 0.36 + 0.07, sy * 0.22 - 0.07, sy * 0.22 + 0.07, ZT - 0.11, ZT, WOOD, WOOD_M, c=0.010)
            if sy < 0: red_cap(P, sx * 0.36, -0.22 - 0.07, ZT - 0.055, size=0.054)
            red_cap_side = sx * (0.36 + 0.07)
            plain_box(P, 'capS', min(red_cap_side, red_cap_side + sx * 0.012), max(red_cap_side, red_cap_side + sx * 0.012),
                      sy * 0.22 - 0.024, sy * 0.22 + 0.024, ZT - 0.074, ZT - 0.026, RED, RED_D)
        box(P, 'low_s', sx * 0.388 - 0.03, sx * 0.388 + 0.03, -0.19, 0.19, 0.14, 0.205, WOOD_D, WOOD_M, c=0.005)
    for sy in (-1, 1):
        box(P, 'apron', -0.30, 0.30, sy * 0.22 - 0.025, sy * 0.22 + 0.025, ZT - 0.08, ZT - 0.005, WOOD_M, WOOD_M, c=0.004)
        box(P, 'low', -0.366, 0.366, sy * 0.22 - 0.03, sy * 0.22 + 0.03, 0.14, 0.205, WOOD_D, WOOD_M, c=0.005)
    # top slab with the basin opening
    bx, by, hw, hd = -0.11, -0.05, 0.44, 0.34                    # review: bigger basin
    top = chamf_rect(0.90, 0.60, 0.03); hole = [(bx + x, by + y) for x, y in chamf_rect(hw, hd, 0.03)]
    flat_plate(P, 'top', top, ZT, ZT + TT, [hole], WOOD, WOOD_M, WOOD_M, WOOD_M, ground=False)
    basin_loft(P, 'basin', bx, by, ZT - 0.24, ZT + TT, ZT + TT + 0.024, (hw - 0.05, hd - 0.04), (hw - 0.004, hd - 0.004),
               (hw + 0.05, hd + 0.05), (hw - 0.03, hd - 0.03), ZT - 0.20, 0.03, CREAM_D, CREAM_B, CREAM, CREAM_B)   # hangs ~24 cm below
    # hand pump on the back-right
    PX, PY, Z0 = 0.27, 0.13, ZT + TT
    oct_rod(P, 'plinth', (PX, PY, Z0 - 0.004), (PX, PY, Z0 + 0.045), [(0, 0.088), (0.6, 0.088), (1, 0.072)], METAL_D, METAL, ref=(1, 0, 0))
    oct_rod(P, 'barrel', (PX, PY, Z0 + 0.04), (PX, PY, Z0 + 0.30), [(0, 0.068), (1, 0.068)], METAL, METAL_L, ref=(1, 0, 0))
    oct_rod(P, 'capring', (PX, PY, Z0 + 0.29), (PX, PY, Z0 + 0.33), [(0, 0.080), (1, 0.072)], METAL_D, METAL_L, ref=(1, 0, 0))
    oct_rod(P, 'neck', (PX, PY, Z0 + 0.32), (PX, PY, Z0 + 0.42), [(0, 0.026), (1, 0.026)], METAL, METAL_L, ref=(1, 0, 0))
    sp = [Vector((PX - 0.04, PY, Z0 + 0.22)), Vector((PX - 0.15, PY, Z0 + 0.22)), Vector((PX - 0.18, PY, Z0 + 0.19)), Vector((PX - 0.18, PY, Z0 + 0.15))]
    path_sweep(P, 'spout', sp, (0, 1, 0), [(0.021, -0.021), (0.021, 0.021), (-0.021, 0.021), (-0.021, -0.021)], METAL, METAL_D)
    piv = Vector((PX, PY, Z0 + 0.405))
    sweep(P, 'pin', piv + Vector((0, -0.022, 0)), piv + Vector((0, -0.038, 0)), ngon(0.017, 8, math.pi / 8), [(0, 1, 0), (1, 0.8, 0)], RED, RED_D, RED, ref=(0, 0, 1))
    L = Part('Lever')
    lp = [piv + Vector(v) for v in ((-0.03, 0, 0.0), (0.04, 0, 0.03), (0.13, 0, -0.03), (0.23, 0, -0.14), (0.26, 0, -0.17))]
    path_sweep(L, 'lever', lp, (0, 1, 0), [(0.027, -0.021), (0.027, 0.021), (-0.027, 0.021), (-0.027, -0.021)], HWOOD, WOOD)
    return [(P, (0, 0, 0)), (L, tuple(piv))]

# ---------------- FUR-07 low press stand ----------------
def build_press_stand():
    P = Part('Body'); ZT = 0.42
    for sx in (-1, 1):
        for sy in (-1, 1):
            splay_leg(P, Vector((sx * 0.37, sy * 0.37, 0)), Vector((sx * 0.33, sy * 0.33, ZT - 0.05)), s=0.10)
            rect_prism(P, 'head', sx * 0.33, sy * 0.33, 0.135, 0.135, 0.015, [(ZT - 0.08, 0), (ZT + 0.07, 0), (ZT + 0.085, 0.015)], WOOD, WOOD, WOOD)
            if sy < 0: red_cap(P, sx * 0.33, -0.33 - 0.0675, ZT + 0.005, size=0.05)
    rect_prism(P, 'top', 0, 0, 0.66, 0.66, 0.02, [(ZT, 0), (ZT + 0.07, 0), (ZT + 0.08, 0.01)], WOOD_M, WOOD_M, WOOD)
    for s in (-1, 1):
        box(P, 'low_x', -0.30, 0.30, s * 0.345 - 0.025, s * 0.345 + 0.025, 0.10, 0.155, WOOD_D, WOOD_M, c=0.004)
        box(P, 'low_y', s * 0.345 - 0.025, s * 0.345 + 0.025, -0.30, 0.30, 0.10, 0.155, WOOD_D, WOOD_M, c=0.004)
        sweep(P, 'brace', Vector((-0.20, s * 0.345, 0.15)), Vector((0.0, s * 0.33, ZT - 0.002)), chamf_rect(0.04, 0.035, 0.004),
              [(0, 1, 0), (1, 1, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(0, 1, 0))
        sweep(P, 'brace', Vector((s * 0.345, 0.20, 0.15)), Vector((s * 0.33, 0.0, ZT - 0.002)), chamf_rect(0.04, 0.035, 0.004),
              [(0, 1, 0), (1, 1, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(1, 0, 0))
    return P

# ---------------- FUR-08 workshop trolley (4 separate wheels) ----------------
def build_trolley():
    P = Part('Body'); ZB, ZP = 0.150, 0.76; PXs, PYs = 0.33, 0.19
    for sx in (-1, 1):
        for sy in (-1, 1):
            rect_prism(P, 'post', sx * PXs, sy * PYs, 0.08, 0.08, 0.012, [(ZB, 0.006), (ZB + 0.008, 0), (ZP - 0.02, 0), (ZP, 0.022)], WOOD, WOOD, WOOD)
            for z in (0.31, 0.68):
                plain_box(P, 'joint', sx * PXs - 0.0475, sx * PXs + 0.0475, sy * PYs - 0.0475, sy * PYs + 0.0475, z - 0.06, z + 0.02, WOOD, WOOD)
                if sy < 0: red_cap(P, sx * PXs, -PYs - 0.0475, z - 0.02, size=0.04)
            sweep(P, 'fork', (sx * PXs, sy * PYs, ZB + 0.004), (sx * PXs, sy * PYs, 0.13), chamf_rect(0.05, 0.05, 0.006), [(0, 1, 0), (1, 1, 0)],
                  METAL_D, METAL_D, METAL_D, ref=(1, 0, 0))
    for z in (0.31, 0.68):
        for s in (-1, 1):
            box(P, 'rail_x', -PXs + 0.0475, PXs - 0.0475, s * PYs - 0.025, s * PYs + 0.025, z - 0.05, z + 0.015, WOOD_D, WOOD_M, c=0.004)
            box(P, 'rail_y', s * PXs - 0.025, s * PXs + 0.025, -PYs + 0.0475, PYs - 0.0475, z - 0.05, z + 0.015, WOOD_D, WOOD_M, c=0.004)
        plain_box(P, 'board', -PXs + 0.03, PXs - 0.03, -PYs + 0.03, PYs - 0.03, z - 0.035, z - 0.012, CREAM_D, CREAM_B)
    # push handle on the +X end
    for sy in (-1, 1):
        sweep(P, 'arm', Vector((PXs, sy * PYs, ZP - 0.03)), Vector((PXs + 0.13, sy * PYs, 0.92)), chamf_rect(0.07, 0.07, 0.012),
              [(0, 1, 0), (0.85, 1, 0), (1, 0.8, 0.012)], WOOD, WOOD_M, WOOD, ref=(0, 1, 0))
    oct_rod(P, 'bar', (PXs + 0.12, -PYs + 0.02, 0.905), (PXs + 0.12, PYs - 0.02, 0.905), [(0, 0.025), (1, 0.025)], METAL, METAL_L, ref=(0, 0, 1))
    parts = [(P, (0, 0, 0))]
    for sx in (-1, 1):
        for sy in (-1, 1):
            W = Part(f'Wheel_{"F" if sy < 0 else "B"}{"L" if sx < 0 else "R"}')
            c = Vector((sx * PXs, sy * PYs, 0.086 * math.cos(math.pi / 10)))   # flat face of the 10-gon on the ground
            oct_rod(W, 'tyre', c - Vector((0, 0.022, 0)), c + Vector((0, 0.022, 0)), [(0, 0.077), (0.18, 0.086), (0.82, 0.086), (1, 0.077)],
                    FOOT, FOOT, n=10, ref=(0, 0, 1))
            d = -1 if sy < 0 else 1; bolt(W, c + Vector((0, d * 0.022, 0)), (0, d, 0), r=0.019, h=0.010)   # hub bolt on the outer face
            W.comp[0] = (W.comp[0][0], W.comp[0][1], True)
            parts.append((W, tuple(c)))
    return parts

# ---------------- FUR-09 baker's worktable with flour trough ----------------
def build_baker_table():
    P = Part('Body'); ZT = 0.80; TT = 0.10
    for sx in (-1, 1):
        for sy in (-1, 1):
            splay_leg(P, Vector((sx * 0.70, sy * 0.28, 0)), Vector((sx * 0.62, sy * 0.28, ZT - 0.10)), s=0.13)
            box(P, 'head', sx * 0.62 - 0.08, sx * 0.62 + 0.08, sy * 0.28 - 0.08, sy * 0.28 + 0.08, ZT - 0.14, ZT, RED, RED_D, c=0.014)
        box(P, 'apron_s', sx * 0.62 - 0.03, sx * 0.62 + 0.03, -0.212, 0.212, ZT - 0.11, ZT - 0.005, WOOD_D, WOOD_M, c=0.004)
        box(P, 'low_s', sx * 0.672 - 0.026, sx * 0.672 + 0.026, -0.245, 0.245, 0.17, 0.225, WOOD_D, WOOD_M, c=0.004)
    for sy in (-1, 1):
        box(P, 'apron', -0.552, 0.552, sy * 0.28 - 0.03, sy * 0.28 + 0.03, ZT - 0.11, ZT - 0.005, WOOD_D, WOOD_M, c=0.004)
        box(P, 'low', -0.646, 0.646, sy * 0.28 - 0.026, sy * 0.28 + 0.026, 0.17, 0.225, WOOD_D, WOOD_M, c=0.004)
    tx, tw, td = 0.52, 0.40, 0.62
    top = chamf_rect(1.60, 0.80, 0.06); hole = [(tx + x, y) for x, y in chamf_rect(tw, td, 0.03)]
    flat_plate(P, 'top', top, ZT, ZT + TT, [hole], WOOD, WOOD_M, WOOD_M, CREAM_IN, ground=False)
    for yy in (-0.20, 0.0, 0.20):                                 # plank seams (dark strips 1.5 mm proud, they stop at the trough)
        plain_box(P, 'seam', -0.77, tx - tw / 2 - 0.035, yy - 0.004, yy + 0.004, ZT + TT - 0.001, ZT + TT + 0.0015, WOOD_DD, WOOD_D)
    basin_loft(P, 'trough', tx, 0.0, ZT - 0.02, ZT + TT, ZT + TT + 0.012, (tw - 0.06, td - 0.06), (tw - 0.004, td - 0.004),
               (tw + 0.03, td + 0.03), (tw - 0.05, td - 0.05), ZT + 0.015, 0.03, CREAM_IN, FOOT, CREAM_IN, FOOT)
    return P

# ---------------- FUR-10 smoking rail ----------------
def build_smoke_rail():
    P = Part('Body'); H = 1.50; XU = 0.55; ZB = 1.22
    for sx in (-1, 1):
        x = sx * XU
        rect_prism(P, 'upright', x, 0, 0.16, 0.16, 0.02, [(0.08, 0), (H - 0.05, 0), (H, 0.035)], WOOD, WOOD, WOOD)
        rect_prism(P, 'foot', x, 0, 0.20, 0.46, 0.028, [(0.0, 0), (0.08, 0), (0.105, 0.024)], WOOD, WOOD_M, WOOD, ground=True)
        for sy in (-1, 1):                                          # triangular braces, front and back
            tri = [(sy * 0.078, 0.095), (sy * 0.215, 0.095), (sy * 0.078, 0.50)]
            P.loft('brace', [[Vector((x + dx, y, z)) for y, z in (tri if sy > 0 else list(reversed(tri)))] for dx in (-0.05, 0.05)],
                   WOOD_D, WOOD_D, WOOD_D)
        rect_prism(P, 'band', x, 0, 0.19, 0.19, 0.026, [(0.56, 0), (0.66, 0)], RED, RED_D, RED_D)
        for d in (-1, 1):                                           # octagonal bosses either side of the upright
            oct_rod(P, 'boss', (x + d * 0.078, 0, ZB), (x + d * 0.135, 0, ZB), [(0, 0.080), (0.7, 0.080), (1, 0.064)], FOOT, FOOT, ref=(0, 0, 1))
    oct_rod(P, 'bar', (-XU, 0, ZB), (XU, 0, ZB), [(0, 0.046), (1, 0.046)], METAL, METAL_L, ref=(0, 0, 1))
    return P

# ---------------- FUR-11 honey frame draining stand ----------------
def build_honey_stand():
    P = Part('Body'); XS = 0.31; ZTOP = 0.68
    def ly(z): return 0.24 - 0.20 * z / ZTOP                      # leg centre |y| at height z
    for sx in (-1, 1):
        x = sx * XS
        for sy in (-1, 1):
            splay_leg(P, Vector((x, sy * 0.24, 0)), Vector((x, sy * 0.045, ZTOP - 0.02)), s=0.075)
        rect_prism(P, 'apex', x, 0, 0.08, 0.12, 0.016, [(ZTOP - 0.08, 0), (ZTOP + 0.03, 0), (ZTOP + 0.05, 0.02)], WOOD, WOOD, WOOD)
        bolt(P, (x + sx * 0.04, 0, ZTOP - 0.03), (sx, 0, 0), r=0.024, h=0.014)
        for sy in (-1, 1):                                          # small posts holding the frame rails
            plain_box(P, 'rpost', x - sx * 0.055 - 0.02, x - sx * 0.055 + 0.02, sy * ly(0.42) - 0.02, sy * ly(0.42) + 0.02, 0.36, 0.47, WOOD_D, WOOD_M)
    box(P, 'topbar', -XS, XS, -0.03, 0.03, ZTOP - 0.065, ZTOP - 0.005, WOOD_D, WOOD_M, c=0.006)
    for sy in (-1, 1):
        box(P, 'low', -XS, XS, sy * ly(0.13) - 0.025, sy * ly(0.13) + 0.025, 0.105, 0.155, WOOD_D, WOOD_M, c=0.005)
        box(P, 'rail', -XS + 0.035, XS - 0.035, sy * ly(0.42) - 0.022, sy * ly(0.42) + 0.022, 0.415, 0.455, WOOD_D, WOOD_M, c=0.004)
    # sloped collection tray (tilted toward the front) with a tap
    nv0 = len(P.bm.verts)
    basin_loft(P, 'tray', 0, -0.01, 0.195, 0.355, 0.37, (0.43, 0.18), (0.53, 0.28), (0.55, 0.30), (0.50, 0.25), 0.227, 0.03,
               CREAM_D, CREAM_B, CREAM, CREAM_B)
    M = Matrix.Translation((0, -0.01, 0.30)) @ Matrix.Rotation(math.radians(8), 4, 'X') @ Matrix.Translation((0, 0.01, -0.30))
    P.bm.verts.ensure_lookup_table()
    for v in list(P.bm.verts)[nv0:]: v.co = M @ v.co
    tap = M @ Vector((0, -0.10, 0.21))
    oct_rod(P, 'pipe', tap + Vector((0, 0, 0.02)), tap - Vector((0, 0, 0.05)), [(0, 0.016), (1, 0.016)], METAL, METAL_D, ref=(1, 0, 0))
    oct_rod(P, 'valve', tap - Vector((0, 0.022, 0.03)), tap + Vector((0, 0.022, -0.03)), [(0, 0.026), (1, 0.026)], METAL_D, METAL, ref=(0, 0, 1))
    plain_box(P, 'lever', tap.x - 0.004, tap.x + 0.075, tap.y - 0.032, tap.y - 0.018, tap.z - 0.024, tap.z - 0.010, RED, RED_D)
    return P

# ---------------- FUR-12 low processing pallet ----------------
def build_pallet():
    # Review polish: 9 cm feet and 4 cm slats; total height 0.18 m (was 0.15).
    P = Part('Body')
    for sx in (-1, 1):
        for sy in (-1, 1):
            rect_prism(P, 'foot', sx * 0.33, sy * 0.24, 0.10, 0.12, 0.012, [(0.0, 0), (0.090, 0)], WOOD, WOOD_M, WOOD_M, ground=True)
    for sy in (-1, 1):
        box(P, 'stringer', -0.40, 0.40, sy * 0.24 - 0.035, sy * 0.24 + 0.035, 0.085, 0.142, WOOD_D, WOOD_M, c=0.005)
        if sy < 0:
            for sx in (-1, 1): red_cap(P, sx * 0.33, -0.24 - 0.035, 0.112, size=0.036)
    sw, g = 0.145, 0.0125
    for i in range(5):
        x0 = -0.40 + i * (sw + g)
        rect_prism(P, 'slat', x0 + sw / 2, 0, sw, 0.60, 0.022, [(0.14, 0), (0.172, 0), (0.18, 0.008)], WOOD, WOOD_M, WOOD)
    return P

# ---------------- MOD-01 / MOD-02 floor tiles (2 x 2 m snap modules) ----------------
def plank4(P, cn, x0, x1, y0, y1, z0, z1, ch, side, top):
    """4-sided board with a top chamfer (20 tris); its side faces stay vertical up to z1-ch"""
    def ring(z, d): return [Vector(v) for v in ((x0 + d, y0 + d, z), (x1 - d, y0 + d, z), (x1 - d, y1 - d, z), (x0 + d, y1 - d, z))]
    P.loft(cn, [ring(z0, 0), ring(z1 - ch, 0), ring(z1, ch)], lambda j, k: side if j == 0 else top, side, top)

def build_wood_floor():
    P = Part('Body'); Z0, ZP, ZT = 0.0, 0.11, 0.15
    plank4(P, 'slab', -1.0, 1.0, -1.0, 1.0, Z0, ZP + 0.002, 0.0001, WOOD_D, WOOD_DD)
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)
    splits = (0.20, -0.50, 0.60, -0.20, 0.30); gap = 0.005          # review: visible seams
    for r in range(5):
        y0, y1 = -1.0 + r * 0.4, -1.0 + (r + 1) * 0.4
        ya, yb = (y0 if r == 0 else y0 + gap), (y1 if r == 4 else y1 - gap)
        xs = splits[r]
        for k, (xa, xb) in enumerate(((-1.0, xs - gap), (xs + gap, 1.0))):
            shade = WOOD if (r + k) % 2 == 0 else WOOD_D                 # review: stronger contrast
            plank4(P, 'plank', xa, xb, ya, yb, ZP, ZT, 0.016, WOOD_DD, shade)
    return P

def build_stone_floor(plain=False):
    P = Part('Body'); ZB, ZT = 0.10, 0.15; IN = 0.86
    import random
    rnd = random.Random(7)
    plank4(P, 'base', -1.0, 1.0, -1.0, 1.0, 0.0, ZB + 0.004, 0.0001, CREAM_IN, CREAM_IN)
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)
    # border ring (flush outer edge, chamfered top on both edges)
    def sq(h, z): return [Vector((x, y, z)) for x, y in ((-h, -h), (h, -h), (h, h), (-h, h))]
    P.torus_loft('border', [sq(1.0, ZB), sq(1.0, ZT - 0.012), sq(0.988, ZT), sq(IN + 0.012, ZT), sq(IN, ZT - 0.012), sq(IN, ZB)],
                 lambda j, k: (CREAM_IN, FOOT, FOOT, CREAM_IN, CREAM_IN, CREAM_IN)[j])
    # Voronoi flagstones inside the border: irregular 4-7 sided cells, a big stone in the centre, joints 2.2 cm, pillow bevels
    seeds = [(0.0, 0.02)]                                        # centre seed with an empty ring around it -> big centre stone
    for i in range(4):
        for j in range(4):
            x, y = -IN + (i + 0.5) * IN / 2, -IN + (j + 0.5) * IN / 2
            if abs(x) < 0.3 and abs(y) < 0.3: continue
            seeds.append((x + rnd.uniform(-0.09, 0.09), y + rnd.uniform(-0.09, 0.09)))
    def clip(poly, a, b):                                        # keep the half-plane closer to seed a than to seed b
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); dx, dy = b[0] - a[0], b[1] - a[1]
        f = lambda p: (p[0] - m[0]) * dx + (p[1] - m[1]) * dy
        out = []
        for k in range(len(poly)):
            p, q = poly[k], poly[(k + 1) % len(poly)]; fp, fq = f(p), f(q)
            if fp <= 0: out.append(p)
            if (fp < 0) != (fq < 0) and fp != fq:
                t = fp / (fp - fq); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        return out
    accents = {3: CREAM_B, 8: CREAM_B, 12: CREAM_B, 5: RED, 10: RED, 14: RED}
    if plain: accents = {3: CREAM_B, 6: CREAM_B, 8: CREAM_B, 12: CREAM_B, 15: CREAM_B}   # MOD-02 Plain: tonal greys only (CREAM_B/D are greys in its palette)
    for si, s0 in enumerate(seeds):
        poly = [(-IN, -IN), (IN, -IN), (IN, IN), (-IN, IN)]
        for sj, s1 in enumerate(seeds):
            if sj != si: poly = clip(poly, s0, s1)
        poly = [p for k, p in enumerate(poly) if math.dist(p, poly[k - 1]) > 0.01]      # drop near-duplicate verts
        q = pc.inset(poly, 0.011)
        top = accents.get(si, FOOT); side = RED_D if top == RED else (CREAM_D if top == CREAM_B else CREAM_IN)
        P.loft('stone', [[Vector((x, y, ZB - 0.003)) for x, y in q], [Vector((x, y, ZT - 0.018)) for x, y in q],
                         [Vector((x, y, ZT)) for x, y in pc.inset(q, 0.020)]], lambda jj, k: side, side, top)
    return P

def snap_check_floor(obs, box_=(-1, 1, -1, 1, 0, 0.15)):
    """asserts the exact module bbox; box_ entries set to None are not checked"""
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    got = (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    ok = all(w is None or abs(g - w) < 1e-5 for g, w in zip(got, box_))
    print('  SNAP', 'OK' if ok else 'FAIL', 'got', [round(v, 5) for v in got], 'want', box_)
    assert ok

# ---------------- MOD-06 / MOD-11 posts (0.2 x 0.2 x 2.4, centred on the grid point) ----------------
def post_section(h, grooves, g_w=0.020, g_d=0.010, g_off=0.030):
    """square section of half-size h, CCW; grooves=True adds 2 notches per face (depth g_d), else the same verts on the edges"""
    corners = [(-h, -h), (h, -h), (h, h), (-h, h)]; pts = []
    for i in range(4):
        a, b = Vector(corners[i]), Vector(corners[(i + 1) % 4]); d = (b - a).normalized(); n = Vector((d.y, -d.x))   # outward normal
        pts.append(tuple(a))
        for s0 in (g_off, 2 * h - g_off - g_w):
            for s, dep in ((s0, 0), (s0, g_d), (s0 + g_w, g_d), (s0 + g_w, 0)):
                q = a + d * s - n * (dep if grooves else 0.0); pts.append((q.x, q.y))
    return pts

def build_post(grooved):
    P = Part('Body'); h = 0.10
    if not grooved:
        rings = [(0.0, FOOT), (0.04, RED), (0.18, WOOD), (2.40, None)]
        sq = [(-h, -h), (h, -h), (h, h), (-h, h)]
        R = [[Vector((x, y, z)) for x, y in sq] for z, _ in rings]
        P.loft('post', R, lambda j, k: (FOOT, RED, WOOD)[j], FOOT, WOOD, ground=True)
        return P
    # three closed solids stacked: plain foot/band/base (0..0.21), grooved shaft (0.21..2.33), plain top (2.33..2.40);
    # the shaft's end caps are the groove ends (no zero-height bands -> no degenerate faces)
    sq = [(-h, -h), (h, -h), (h, h), (-h, h)]
    P.loft('base', [[Vector((x, y, z)) for x, y in sq] for z in (0.0, 0.03, 0.17, 0.21)], lambda j, k: (CREAM_IN, RED, WOOD)[j], CREAM_IN, WOOD_D, ground=True)
    groove = post_section(h, True)
    P.loft('shaft', [[Vector((x, y, z)) for x, y in groove] for z in (0.21, 2.33)], WOOD, WOOD_D, WOOD_D)
    P.loft('cap', [[Vector((x, y, z)) for x, y in sq] for z in (2.33, 2.40)], WOOD, WOOD_D, WOOD)
    return P

# ---------------- MOD-07 canopy beam ----------------
def build_beam():
    P = Part('Body')
    sweep(P, 'beam', (-1.0, 0, 0.10), (1.0, 0, 0.10), chamf_rect(0.20, 0.20, 0.022), [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 0, 1))
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)
    return P

# ---------------- MOD-08 flat canopy roof panel 2 x 2 ----------------
def build_roof():
    P = Part('Body'); RW, ZR, ZC = 0.10, 0.14, 0.18
    plank4(P, 'sheet', -0.905, 0.905, -0.905, 0.905, 0.030, 0.045, 0.0001, WOOD_DD, WOOD_DD)
    for s in (-1, 1):                                               # frame rails, outer faces flush on the grid
        plank4(P, 'rail_x', -0.88, 0.88, min(s * 1.0, s * (1.0 - RW)), max(s * 1.0, s * (1.0 - RW)), 0.0, ZR, 0.010, WOOD_M, WOOD)
        plank4(P, 'rail_y', min(s * 1.0, s * (1.0 - RW)), max(s * 1.0, s * (1.0 - RW)), -0.88, 0.88, 0.0, ZR, 0.010, WOOD_M, WOOD)
    P.comp[-1] = (P.comp[-1][0], P.comp[-1][1], True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * 1.0, sx * 0.88)); y0, y1 = sorted((sy * 1.0, sy * 0.88))
            plank4(P, 'corner', x0, x1, y0, y1, 0.0, ZC, 0.012, WOOD, WOOD)
    n, g = 6, 0.028; w = (1.80 - (n - 1) * g) / n
    for i in range(n):
        x0 = -0.90 + i * (w + g); plank4(P, 'slat', x0, x0 + w, -0.90, 0.90, 0.044, 0.115, 0.010, RED_D, RED)
    return P

# ---------------- MOD-09 arched workshop door: frame + hinged leaf (frame outer = the arched MOD-05 opening) ----------------
DOOR_HX, DOOR_ZS, DOOR_ZA = 0.48, 1.78, 2.02          # MUST equal MOD03_Wall/build_wall_modules.py KINDS['door'] open/arch

def poly_offset(pts, d):
    """true-miter inward offset of a closed polygon (any orientation)"""
    n = len(pts); area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)); sg = 1 if area > 0 else -1
    def nrm(a, b):
        dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz); return (-dz / L * sg, dx / L * sg)
    out = []
    for i in range(n):
        n1, n2 = nrm(pts[i - 1], pts[i]), nrm(pts[i], pts[(i + 1) % n]); k = d / max(1e-6, 1 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((pts[i][0] + k * (n1[0] + n2[0]), pts[i][1] + k * (n1[1] + n2[1])))
    return out

def arc(zc, r, x_from, x_to, n):
    a0 = math.atan2(math.sqrt(max(r * r - x_from * x_from, 0)), x_from); a1 = math.atan2(math.sqrt(max(r * r - x_to * x_to, 0)), x_to)
    return [(r * math.cos(a0 + (a1 - a0) * k / n), zc + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(1, n)]

def build_door():
    hx, zs, za = DOOR_HX, DOOR_ZS, DOOR_ZA
    zc = (za * za - zs * zs - hx * hx) / (2 * (za - zs)); R = za - zc
    FW, FY = 0.075, 0.065                                       # frame width / half depth
    hi, Ri = hx - FW, R - FW; zsi = zc + math.sqrt(Ri * Ri - hi * hi)
    # ---- frame: arched inverted U (no threshold), chamfered front/back edges
    F = [(-hx, 0.0), (-hi, 0.0), (-hi, zsi)] + arc(zc, Ri, -hi, hi, 8) + [(hi, zsi), (hi, 0.0), (hx, 0.0), (hx, zs)] + arc(zc, R, hx, -hx, 8) + [(-hx, zs)]
    Fr = Part('Body')
    Fr.loft('frame', [[Vector((x, y, z)) for x, z in poly_offset(F, d)] for y, d in ((-FY, 0.010), (-FY + 0.011, 0.0), (FY - 0.011, 0.0), (FY, 0.010))],
            lambda j, k: (WOOD, WOOD_D, WOOD)[j], WOOD_M, WOOD_M, ground=True)
    for z in (0.62, 1.40):                                      # hinge pins on the frame (+X jamb, front)
        oct_rod(Fr, 'pin', (hi + 0.004, -FY - 0.012, z - 0.10), (hi + 0.004, -FY - 0.012, z + 0.10), [(0, 0.022), (1, 0.022)], METAL, METAL_L, ref=(1, 0, 0))
        plain_box(Fr, 'pinplate', hi - 0.004, hi + 0.050, -FY - 0.004, -FY + 0.002, z - 0.10, z + 0.10, METAL_D, METAL)
    # ---- leaf: 5 vertical planks with an arched top over a dark core plate
    G = 0.006; hl = hi - G; Rl = Ri - G; Z0 = 0.012; T = 0.024
    top = lambda x: zc + math.sqrt(Rl * Rl - x * x)
    L = Part('Leaf'); n = 5; gw = 0.006; w = (2 * hl - (n - 1) * gw) / n
    for i in range(n):
        a = -hl + i * (w + gw); b = a + w; m = (a + b) / 2
        ol = [(a, Z0), (b, Z0), (b, top(b) - 0.004), (m, top(m) - 0.004), (a, top(a) - 0.004)]
        L.loft('plank', [[Vector((x, y, z)) for x, z in poly_offset(ol, d)] for y, d in ((-T, 0.005), (-T + 0.005, 0.0), (T, 0.0))],
               lambda j, k: (WOOD, WOOD_M)[j], WOOD_M, WOOD if i % 2 == 0 else HWOOD)
    core = [(-hl + 0.012, Z0 + 0.012), (hl - 0.012, Z0 + 0.012)] + [(x, top(x) - 0.016) for x in [hl - 0.012 - k * (2 * hl - 0.024) / 8 for k in range(9)]]
    L.loft('core', [[Vector((x, y, z)) for x, z in core] for y in (-T + 0.010, T - 0.010)], WOOD_DD, WOOD_DD, WOOD_DD)
    yf = -T
    for z in (0.42, 1.38):                                      # cream battens + red caps
        plain_box(L, 'batten', -hl + 0.035, hl - 0.035, yf - 0.026, yf + 0.003, z - 0.075, z + 0.075, CREAM_D, CREAM_B)
        for x in (-hl + 0.085, hl - 0.085): red_cap(L, x, yf - 0.026, z, size=0.060, t=0.010)
    sweep(L, 'zbrace', Vector((-hl + 0.085, yf - 0.013, 0.49)), Vector((hl - 0.085, yf - 0.013, 1.31)),
          [(0.07, 0.0135), (-0.07, 0.0135), (-0.07, -0.0135), (0.07, -0.0135)], [(0, 1, 0), (1, 1, 0)], CREAM_D, CREAM_B, CREAM_B, ref=(0, 1, 0))
    for z in (0.62, 1.40):                                      # strap hinges on the +X (hinge) side
        plain_box(L, 'strap', hl - 0.27, hl + 0.004, yf - 0.016, yf + 0.002, z - 0.045, z + 0.045, METAL, METAL_L)
        bolt(L, (hl - 0.22, yf - 0.016, z), (0, -1, 0), r=0.020, h=0.008)
    for z in (0.86, 1.14):                                      # D-handle on the -X side
        sweep(L, 'hplate', (-hl + 0.10, yf + 0.002, z), (-hl + 0.10, yf - 0.016, z), ngon(0.028, 8, math.pi / 8), [(0, 1, 0), (1, 1, 0)], METAL_D, METAL_D, METAL, ref=(0, 0, 1))
    hp = [Vector((-hl + 0.10, yf - 0.012, 0.86)), Vector((-hl + 0.10, yf - 0.078, 0.89)), Vector((-hl + 0.10, yf - 0.078, 1.11)), Vector((-hl + 0.10, yf - 0.012, 1.14))]
    path_sweep(L, 'handle', hp, (1, 0, 0), [(0.018, -0.020), (0.018, 0.020), (-0.018, 0.020), (-0.018, -0.020)], METAL, METAL_D)
    print(f'  DOOR frame outer = MOD-05 opening: half-width {hx}, springs {zs}, apex {za}; leaf {2 * hl:.3f} wide, apex {top(0):.3f}, hinge x {hl:.3f}')
    return [(Fr, (0, 0, 0)), (L, (hl, 0.0, 0.0))]

# ---------------- MOD-10 low partition 2 m ----------------
def build_partition():
    P = Part('Body'); XP = 0.88
    for sx in (-1, 1):
        rect_prism(P, 'post', sx * XP, 0, 0.15, 0.15, 0.0175, [(0.0, 0), (1.06, 0), (1.10, 0.03)], WOOD_M, WOOD_M, WOOD_M)
        rect_prism(P, 'foot', sx * XP, 0, 0.2125, 0.325, 0.025, [(0.0, 0), (0.06, 0), (0.11, 0.035)], CREAM_IN, CREAM_IN, FOOT, ground=True)
    tops = (0.94, 1.00, 0.96, 1.01, 0.97)
    n, g = 5, 0.012; inner = 2 * (XP - 0.075); w = (inner - (n - 1) * g) / n
    for i in range(n):
        x0 = -(XP - 0.075) + i * (w + g); zt = tops[i]
        ol = [(x0, 0.10), (x0 + w, 0.10), (x0 + w, zt - 0.05), (x0 + w - 0.035, zt), (x0 + 0.035, zt), (x0, zt - 0.05)]
        L_ = [[Vector((x, y, z)) for x, z in ol] for y in (-0.02, 0.02)]
        P.loft('plank', L_, WOOD, WOOD, WOOD)
    for zc in (0.26, 0.86):                                         # front rails run to the flat ends at x = +-1
        plain_box(P, 'rail', -1.0, 1.0, -0.083, -0.018, zc - 0.06, zc + 0.06, WOOD_M, WOOD)       # 2 mm into the planks (no coplanar faces)
        for sx in (-1, 1): red_cap(P, sx * XP, -0.083, zc, size=0.05, t=0.010)
    return P

# ---------------- MOD-12 wall shelf under a window ----------------
def build_window_shelf():
    P = Part('Body'); ZB0, ZB1 = 0.28, 0.38                         # back = wall plane y = 0, front -Y
    rect_prism(P, 'board', 0, -0.20, 1.50, 0.40, 0.035, [(ZB0, 0.02), (ZB0 + 0.02, 0), (ZB1 - 0.02, 0), (ZB1, 0.02)], WOOD, WOOD_M, WOOD)
    for sx in (-1, 1):
        x = sx * 0.52
        bo = [(-0.055, 0.0), (0.055, 0.0), (0.055, ZB0), (-0.055, ZB0)]
        bo = [(-0.05, 0.0), (0.05, 0.0), (0.065, 0.03), (0.065, ZB0), (-0.065, ZB0), (-0.065, 0.03)]
        P.loft('bracket', [[Vector((x + 1.3 * bx, y, z)) for bx, z in bo] for y in (-0.065, 0.0)], WOOD_D, WOOD_M, WOOD_D, ground=True)
        # knee brace along the wall, from the bracket post inward under the board (as in the ref), set behind the cap plane
        sweep(P, 'brace', Vector((x - sx * 0.050, -0.032, 0.07)), Vector((x - sx * 0.25, -0.032, ZB0 + 0.002)), chamf_rect(0.055, 0.05, 0.006),
              [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 1, 0))
        for z in (0.14, 0.25): red_cap(P, x, -0.065, z, size=0.042, t=0.010)    # above the brace foot (it covered the low cap)
    return P

REG_EXTRA = {
    'MOD06': dict(id='MOD-06', name='FMS_Workshop_MOD_06', build=lambda: build_post(False), budget=(100, 250), view=(-0.75, -1.0, 0.35),
                  fill=(0.70, 0.90), snapbox=(-0.1, 0.1, -0.1, 0.1, 0, 2.4), pal={15: '#B4AEA5'}),
    'MOD07': dict(id='MOD-07', name='FMS_Workshop_MOD_07', build=build_beam, budget=(60, 150), view=(-0.55, -1.0, 0.40), fill=(0.76, 0.84),
                  snapbox=(-1, 1, -0.1, 0.1, 0, 0.2)),
    'MOD08': dict(id='MOD-08', name='FMS_Workshop_MOD_08', build=build_roof, budget=(200, 450), view=(-0.75, -1.0, 0.80), fill=(0.72, 0.80),
                  snapbox=(-1, 1, -1, 1, 0, 0.18), pal={5: '#C2563F', 6: '#A3432F'}),
    'MOD09': dict(id='MOD-09', name='FMS_Workshop_MOD_09', build=build_door, budget=(200, 750), view=(-0.40, -1.0, 0.25), fill=(0.70, 0.90),
                  snapbox=(-0.48, 0.48, None, None, 0.0, 2.02)),
    'MOD10': dict(id='MOD-10', name='FMS_Workshop_MOD_10', build=build_partition, budget=(200, 450), view=(-0.45, -1.0, 0.30), fill=(0.76, 0.86),
                  snapbox=(-1, 1, None, None, 0, 1.1), pal={15: '#B4AEA5', 10: '#9D978E'}),
    'MOD11': dict(id='MOD-11', name='FMS_Workshop_MOD_11', build=lambda: build_post(True), budget=(80, 200), view=(-0.75, -1.0, 0.35),
                  fill=(0.70, 0.90), snapbox=(-0.1, 0.1, -0.1, 0.1, 0, 2.4)),
    'MOD12': dict(id='MOD-12', name='FMS_Workshop_MOD_12', build=build_window_shelf, budget=(150, 350), view=(-0.45, -1.0, 0.12), fill=(0.76, 0.84)),
}

REG = {
    'TOL01': dict(id='TOL-01', name='FMS_Workshop_TOL_01', build=build_mold, budget=(150, 400), view=(-0.10, -1.0, 0.60), fill=(0.70, 0.80)),
    'TOL02': dict(id='TOL-02', name='FMS_Workshop_TOL_02', build=build_harp, budget=(120, 350), view=(-0.75, -1.0, 1.25), fill=(0.66, 0.84)),
    'TOL03': dict(id='TOL-03', name='FMS_Workshop_TOL_03', build=build_spatula, budget=(80, 200), view=(-0.75, -1.0, 1.20), fill=(0.70, 0.84)),
    'TOL04': dict(id='TOL-04', name='FMS_Workshop_TOL_04', build=build_colander, budget=(200, 500), view=(0.0, -1.0, 0.50), fill=(0.72, 0.80)),
    'TOL05': dict(id='TOL-05', name='FMS_Workshop_TOL_05', build=build_ladle, budget=(120, 300), view=(-0.80, -1.0, 0.75), fill=(0.66, 0.84)),
    'TOL11': dict(id='TOL-11', name='FMS_Workshop_TOL_11', build=build_knife, budget=(80, 200), view=(-0.85, -1.0, 1.10), fill=(0.66, 0.84)),
    'TOL12': dict(id='TOL-12', name='FMS_Workshop_TOL_12', build=build_bowl, budget=(150, 350), view=(0.0, -1.0, 0.50), fill=(0.72, 0.80)),
    'TOL13': dict(id='TOL-13', name='FMS_Workshop_TOL_13', build=build_peel, budget=(120, 300), view=(-0.80, -1.0, 0.95), fill=(0.74, 0.84)),
    'TOL14': dict(id='TOL-14', name='FMS_Workshop_TOL_14', build=build_pin, budget=(100, 250), view=(-0.95, -1.0, 0.55), fill=(0.74, 0.84)),
    'TOL15': dict(id='TOL-15', name='FMS_Workshop_TOL_15', build=build_hook, budget=(80, 180), view=(0.20, -1.0, 0.12), fill=(0.66, 0.86)),
    'TOL16': dict(id='TOL-16', name='FMS_Workshop_TOL_16', build=build_tongs, budget=(150, 350), view=(-0.85, -1.0, 1.10), fill=(0.66, 0.84)),
    'TOL17': dict(id='TOL-17', name='FMS_Workshop_TOL_17', build=build_comb, budget=(250, 2200), view=(-0.45, -1.0, 0.28), fill=(0.70, 0.84),
                  pal={10: '#E2A63C', 12: '#F5CF66', 15: '#C98420'}),
    'TOL18': dict(id='TOL-18', name='FMS_Workshop_TOL_18', build=build_strainer, budget=(200, 500), view=(-0.30, -1.0, 0.55), fill=(0.66, 0.88),
                  pal={15: '#C9BFAE'}),
    'PRD01': dict(id='PRD-01', name='FMS_Workshop_PRD_01', build=build_cheese_mold, budget=(200, 450), view=(0.0, -1.0, 0.62), fill=(0.70, 0.80)),
    'PRD02': dict(id='PRD-02', name='FMS_Workshop_PRD_02', build=build_cut_wheel, budget=(200, 450), view=(0.30, -1.0, 0.62), fill=(0.70, 0.80),
                  pal={10: '#D9C38E'}),
    'PRD18': dict(id='PRD-18', name='FMS_Workshop_PRD_18', build=build_honey_crock, budget=(250, 550), view=(0.05, -1.0, 0.72), fill=(0.70, 0.86),
                  pal={15: '#F0A230'}),
    'FUR01': dict(id='FUR-01', name='FMS_Workshop_FUR_01', build=build_workbench, budget=(500, 1000), view=(-0.55, -1.0, 0.50), fill=(0.74, 0.84),
                  pal={15: '#B4AEA5', 10: '#9D978E'}),
    'FUR02': dict(id='FUR-02', name='FMS_Workshop_FUR_02', build=build_bottling_table, budget=(450, 900), view=(-0.55, -1.0, 0.55), fill=(0.74, 0.84),
                  pal={4: '#E3C796', 12: '#EED6A9'}),
    'FUR03': dict(id='FUR-03', name='FMS_Workshop_FUR_03', build=build_aging_shelf, budget=(600, 1200), view=(-0.45, -1.0, 0.30), fill=(0.74, 0.88)),
    'FUR04': dict(id='FUR-04', name='FMS_Workshop_FUR_04', build=build_herb_rail, budget=(180, 400), view=(-0.45, -1.0, 0.32), fill=(0.76, 0.84)),
    'FUR05': dict(id='FUR-05', name='FMS_Workshop_FUR_05', build=build_pantry_shelf, budget=(400, 850), view=(-0.45, -1.0, 0.30), fill=(0.74, 0.88),
                  pal={4: '#E3C796', 12: '#EED6A9', 10: '#9D978E', 15: '#B4AEA5'}),
    'FUR06': dict(id='FUR-06', name='FMS_Workshop_FUR_06', build=build_washstand, budget=(700, 1400), view=(-0.45, -1.0, 0.40), fill=(0.74, 0.88)),
    'FUR07': dict(id='FUR-07', name='FMS_Workshop_FUR_07', build=build_press_stand, budget=(300, 650), view=(-0.50, -1.0, 0.45), fill=(0.74, 0.84)),
    'FUR08': dict(id='FUR-08', name='FMS_Workshop_FUR_08', build=build_trolley, budget=(600, 1200), view=(-0.55, -1.0, 0.40), fill=(0.74, 0.88),
                  pal={4: '#E3C796', 12: '#EED6A9', 15: '#A8A39C'}),
    'FUR09': dict(id='FUR-09', name='FMS_Workshop_FUR_09', build=build_baker_table, budget=(600, 1200), view=(-0.55, -1.0, 0.50), fill=(0.74, 0.84),
                  pal={10: '#9D978E', 15: '#B4AEA5'}),
    'FUR10': dict(id='FUR-10', name='FMS_Workshop_FUR_10', build=build_smoke_rail, budget=(300, 650), view=(-0.50, -1.0, 0.35), fill=(0.74, 0.86),
                  pal={15: '#BDB6AA'}),
    'FUR11': dict(id='FUR-11', name='FMS_Workshop_FUR_11', build=build_honey_stand, budget=(400, 850), view=(-0.50, -1.0, 0.45), fill=(0.70, 0.86)),
    'FUR12': dict(id='FUR-12', name='FMS_Workshop_FUR_12', build=build_pallet, budget=(200, 450), view=(-0.55, -1.0, 0.55), fill=(0.74, 0.80)),
    'MOD01': dict(id='MOD-01', name='FMS_Workshop_MOD_01', build=build_wood_floor, budget=(120, 300), view=(-0.75, -1.0, 0.80), fill=(0.72, 0.80),
                  snap=True),
    'MOD02P': dict(id='MOD-02', name='FMS_Workshop_MOD_02_Plain', build=lambda: build_stone_floor(True), budget=(180, 400), view=(-0.75, -1.0, 0.80),
                   fill=(0.72, 0.80), snap=True, pal={15: '#A69E95', 10: '#746E68', 12: '#988F86', 4: '#7E776F'}),   # calm scene variant (user, 2026-11-18)
    'MOD02': dict(id='MOD-02', name='FMS_Workshop_MOD_02', build=build_stone_floor, budget=(180, 400), view=(-0.75, -1.0, 0.80), fill=(0.72, 0.80),
                  snap=True, pal={15: '#B4AEA5', 10: '#8F8A83', 12: '#EED9B0', 4: '#D9C49A'}),
}
REG.update(REG_EXTRA)
CFG = REG[ID]; NAME = CFG['name']; IDN = ID
TEX_NAME = f'T_FarmProcessing_{IDN}_BaseColor.png'; MAT_NAME = f'M_FarmProcessing_{IDN}'

# ---------------- scene / build ----------------
def clear_scene():
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    return coll

def build():
    coll = clear_scene()
    pal = list(PAL)
    for k, v in CFG.get('pal', {}).items(): pal[k] = v          # per-item colour overrides (e.g. honey)
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), pal); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.1; coll.objects.link(root)
    res = CFG['build']()
    parts = res if isinstance(res, list) else [(res, (0, 0, 0))]     # moving parts: [(Part, pivot)], each a direct child of the root
    obs = {Pt.name: pc.to_object(Pt, NAME, coll, mat, piv, root) for Pt, piv in parts}
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    if CFG.get('snap'): snap_check_floor(obs)
    if CFG.get('snapbox'): snap_check_floor(obs, CFG['snapbox'])
    lo, hi = CFG['budget']
    print(f'  budget {lo}-{hi} ->', 'OK' if lo <= tot <= hi else f'OVER x{tot / hi:.2f}' if tot > hi else 'UNDER')
    return obs, root, coll, img, mat

# ---------------- preview (STA-03 render_preview.py logic, CONFIG from the registry) ----------------
def render(out, pct, view=None, lens=70):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; r = sc.render
    saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath,
                 vt=sc.view_settings.view_transform, cam=sc.camera, world=sc.world)
    try: r.engine = 'BLENDER_EEVEE'
    except TypeError: r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, pct
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_World'); w.use_nodes = True; nt = w.node_tree
    outn = next(nd for nd in nt.nodes if nd.type == 'OUTPUT_WORLD'); bg = next(nd for nd in nt.nodes if nd.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (lin(0xc7), lin(0xcc), lin(0xd3), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.82, 0.86, 0.95, 1); amb.inputs['Strength'].default_value = 0.45
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], outn.inputs['Surface']); sc.world = w
    lights = []
    for nm, rot, e, sh in (('TMP_Sun', (45, 0, -30), 3.4, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(10); ld.use_shadow = sh
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob); lights.append(ob)
    cd = bpy.data.cameras.new('TMP_Cam'); cd.lens = lens
    cam = bpy.data.objects.new('TMP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    objs = [o for o in bpy.data.collections[NAME].all_objects if o.type == 'MESH']
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    target = (lo + hi) / 2; dirv = Vector(view or CFG['view']).normalized(); FW, FH = CFG['fill']
    def place(d):
        cam.location = target + dirv * d; cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update(); xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    cd.shift_x = cd.shift_y = 0.0; d = 3.0
    for _ in range(25):
        x0, x1, y0, y1 = place(d); d *= max((x1 - x0) / FW, (y1 - y0) / FH)
    x0, x1, y0, y1 = place(d)
    cd.shift_x = ((x0 + x1) / 2 - 0.5); cd.shift_y = ((y0 + y1) / 2 - 0.5) * (800 / 1280)
    place(d)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights:
        dat = ob.data; bpy.data.objects.remove(ob, do_unlink=True); bpy.data.lights.remove(dat)
    dat = cam.data; bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(dat)
    sc.world = saved['world']; bpy.data.worlds.remove(w)
    r.engine = saved['engine']; r.resolution_x, r.resolution_y, r.resolution_percentage = saved['rx'], saved['ry'], saved['pct']
    r.filepath = saved['fp']; sc.view_settings.view_transform = saved['vt']; sc.camera = saved['cam']
    print('rendered', out)

def verify(fbx):
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    before_i = set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx); bpy.context.view_layer.update()
    obs = list(sc.objects); tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  VERIFY', o.name, 'parent', o.parent.name if o.parent else None, 'tris', t, 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  VERIFY', o.name, o.type)
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  VERIFY nodes', len(obs), 'total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  VERIFY images', [(i.name, os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])

OBS, ROOTOB, COLL, IMG, MAT = build()
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'build':
    render(os.path.join(CHECK_DIR, f'{ID}_check.png'), 50)
    if len(ARGS) > 2:
        render(os.path.join(CHECK_DIR, f'{ID}_alt.png'), 40, tuple(float(x) for x in ARGS[2].split(',')))
elif MODE == 'export':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify(_fbx)
