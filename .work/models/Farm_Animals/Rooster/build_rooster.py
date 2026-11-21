# build_rooster.py - BRD-02 Rooster (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_rooster.py -- BRD-02 build|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_rooster)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure follows ../Hen/build_hen.py (helpers copied, shared modules imported read-only).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Rooster'
TAG = 'FarmAnimals_Rooster'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-02.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_rooster')
REF_VIEW = (0.85, -0.72, 0.15)       # reference: front-left three-quarter, ~50 deg from the front, ~9 deg above
PALETTE = ['#9A2A1F', '#7A2018', '#C93A25', '#DD5A2C',
           '#F0B033', '#D3901F', '#8E2620', '#D9502A',
           '#D8412F', '#C93A2C', '#F4B740', '#E39A2C',
           '#F08A33', '#D06A1C', '#2A1D17', '#E8992A']
(BODY, BODY_D, WING, WING_O, GOLD, GOLD_D, TAIL_R, TAIL_O, COMB, HEAD, BEAK, BEAK_D, LEG, LEG_D, EYE, GOLD_T) = range(16)
BUDGET = 1800

LEG_X, LEG_Y = 0.058, -0.030
# joints = part pivots (shifted with the mesh so the root sits under the centre of mass)
JOINTS = {
    'Body': (0, -0.020, 0.290), 'Neck1': (0, -0.098, 0.390), 'Neck2': (0, -0.108, 0.460), 'Head': (0, -0.112, 0.500),
    'Beak_Lower': (0, -0.168, 0.466), 'Comb': (0, -0.120, 0.530), 'Wattle': (0, -0.170, 0.462),
    'Hackle': (0, -0.100, 0.440),
    'WingUpper.L': (0.100, -0.070, 0.340), 'WingLower.L': (0.105, -0.050, 0.290), 'WingTip.L': (0.100, 0.020, 0.240),
    'TailFan1': (0, 0.060, 0.315), 'TailFan2': (0, 0.120, 0.340), 'Tail_Sickle': (0, 0.120, 0.355),
    'LegUpper.L': (LEG_X, LEG_Y, 0.210), 'LegLower.L': (LEG_X, LEG_Y, 0.150), 'Foot.L': (LEG_X, LEG_Y, 0.020),
}

# body rings: section plane through the front-bottom point F and the back-top point B (X across), neck cap -> rump.
# Upright bird: chest high and forward, back slopes down to the tail, belly at 0.175 (visible leg ~0.15 m).
BODY_RINGS = [(-0.150, 0.385, -0.112, 0.418, 0.028), (-0.180, 0.320, -0.094, 0.420, 0.085),
              (-0.176, 0.258, -0.072, 0.412, 0.104), (-0.140, 0.205, -0.046, 0.400, 0.112),
              (-0.082, 0.178, -0.016, 0.388, 0.115), (-0.012, 0.175, 0.030, 0.374, 0.111),
              (0.055, 0.195, 0.074, 0.360, 0.095), (0.104, 0.228, 0.114, 0.346, 0.066), (0.130, 0.262, 0.133, 0.332, 0.036)]
# neck rings, horizontal (z, y centre, half x, half front, half back): rises almost vertically
NECK1 = [(0.385, -0.098, 0.072, 0.064, 0.066), (0.430, -0.104, 0.062, 0.055, 0.057), (0.475, -0.108, 0.049, 0.044, 0.046)]
NECK2 = [(0.455, -0.108, 0.052, 0.048, 0.050), (0.505, -0.112, 0.041, 0.038, 0.042)]
# head rings along -Y (y, half width, z bottom, z top)
HEAD_RINGS = [(-0.060, 0.024, 0.482, 0.520), (-0.082, 0.043, 0.454, 0.539), (-0.120, 0.047, 0.449, 0.544),
              (-0.158, 0.039, 0.455, 0.530), (-0.177, 0.026, 0.463, 0.510)]
# small upper beak (y, half width, mouth z, top z); lower beak (y, half width, depth below the mouth)
BEAK_UP = [(-0.170, 0.022, 0.467, 0.497), (-0.186, 0.016, 0.464, 0.488), (-0.200, 0.009, 0.459, 0.475), (-0.212, 0.003, 0.452, 0.457)]
BEAK_LO = [(-0.168, 0.018, 0.014), (-0.186, 0.012, 0.010), (-0.200, 0.004, 0.003)]
# comb outline (y, z): front-bottom, 5 thick spikes (tallest in the middle), rear, then back along the sunk base
COMB_OUT = [(-0.172, 0.512), (-0.200, 0.572), (-0.174, 0.584), (-0.168, 0.628), (-0.142, 0.600), (-0.127, 0.645),
            (-0.100, 0.604), (-0.084, 0.634), (-0.064, 0.592), (-0.034, 0.610), (-0.038, 0.560), (-0.066, 0.514),
            (-0.100, 0.522), (-0.140, 0.518)]
COMB_C, COMB_T, COMB_SHRINK = Vector((-0.118, 0.565)), 0.016, 0.78
# wattle lobes, horizontal rings (z, y, half depth y, half width x, lobe centre x): heart shape (lobes meet at the bottom)
WATTLE = [(0.462, -0.170, 0.012, 0.014, 0.018), (0.430, -0.178, 0.017, 0.021, 0.023), (0.396, -0.178, 0.015, 0.017, 0.017),
          (0.368, -0.172, 0.005, 0.005, 0.007)]
# wing = overlapping leaf plates on the body side: (part, outline (y, z), proud at top, proud at bottom, slot)
WING_PLATES = [
    ('WingUpper', [(-0.092, 0.336), (-0.062, 0.362), (0.000, 0.364), (0.052, 0.352), (0.088, 0.300), (0.030, 0.290), (-0.042, 0.298)],
     0.004, 0.030, WING),
    ('WingLower', [(-0.078, 0.300), (-0.020, 0.314), (0.042, 0.308), (0.104, 0.262), (0.116, 0.232), (0.040, 0.238), (-0.052, 0.254)],
     0.006, 0.034, WING_O),
    ('WingLower', [(-0.062, 0.262), (0.000, 0.270), (0.070, 0.254), (0.118, 0.214), (0.124, 0.196), (0.050, 0.202), (-0.040, 0.222)],
     0.006, 0.036, WING),
    ('WingTip', [(0.020, 0.252), (0.080, 0.262), (0.132, 0.232), (0.156, 0.186), (0.112, 0.196), (0.052, 0.212), (0.002, 0.230)],
     0.008, 0.042, WING_O),
]
PLATE_BURY = 0.006
# hackle: 2 overlapping rows of 8 LARGE leaf wedges (closed double pyramid on a 5-point outline L-SL-T-SR-R, raised
# ridge M, buried back B: 10 tris, 4 visible facets). Placed by height: horizontal rays from the neck axis, normal offsets.
# row: (first angle deg, z base front/back, z tip front/back, half angle base deg, half angle shoulder deg)
HACK_AXIS_Y = -0.100
HACK_ROWS = [(0.0, (0.458, 0.490), (0.335, 0.416), 20.0, 34.0),
             (22.5, (0.405, 0.452), (0.262, 0.372), 22.0, 38.0)]
HACK_OFF = dict(base=0.010, shoulder=0.012, tip=0.008, ridge=0.026, back=-0.012)
# head group (Head, beak, Comb, Wattle, eyes) scaled about the head-neck joint and lowered to keep the total height
HEAD_S, HEAD_C, HEAD_DZ = 1.10, Vector((0, -0.110, 0.470)), -0.012
HEAD_PARTS = ('Head', 'Beak_Lower', 'Comb', 'Wattle')
# tail: rump wedge + 8 thick plates; path angle phi(s) = a0 + turn * s**p (straight rise, curl at the tips)
FAN_ROOT = Vector((0, 0.120, 0.340))
FEATHERS = [('Tail_Sickle', 82, -158, 0.48, 1.7, 0.020, TAIL_R), ('Tail_Sickle', 70, -158, 0.46, 1.6, 0.014, TAIL_O),
            ('Tail_Sickle', 58, -155, 0.43, 1.5, 0.008, GOLD), ('TailFan2', 46, -150, 0.40, 1.4, 0.002, TAIL_R),
            ('TailFan2', 34, -142, 0.37, 1.3, -0.004, TAIL_O), ('TailFan2', 22, -132, 0.33, 1.2, -0.010, GOLD),
            ('TailFan2', 10, -120, 0.29, 1.1, -0.016, TAIL_R), ('TailFan2', -4, -104, 0.25, 1.0, -0.022, TAIL_O)]
FEATHER_W = [(0.0, 0.020, 0.008), (0.25, 0.032, 0.011), (0.50, 0.033, 0.011), (0.75, 0.026, 0.009), (1.0, 0.011, 0.005)]
SICKLE_W = [(0.0, 0.020, 0.008), (0.20, 0.032, 0.011), (0.40, 0.034, 0.011), (0.60, 0.032, 0.010), (0.80, 0.025, 0.008),
            (1.0, 0.011, 0.005)]


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-02', 'build'])[:2]


# ---------------- ring helpers (copied from the hen / cow) ----------------
def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ring_y(y, w, zb, zt, n, pt=2.4, pb=2.2, x0=0.0):
    zc, h = (zt + zb) / 2, (zt - zb) / 2; out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; c, s = math.cos(th), math.sin(th)
        p = pt if s >= 0 else pb
        out.append(Vector((x0 + w * spow(c, 2 / p), y, zc + h * spow(s, 2 / p))))
    return out


def ring_tilt(fy, fz, by, bz, w, n, pt=2.4, pb=2.2):
    """ring_y generalised: section plane through the front-bottom point F and the back-top point B (X stays across)"""
    F, B = Vector((0, fy, fz)), Vector((0, by, bz)); c = (F + B) / 2; U = (B - F).normalized(); h = (B - F).length / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; co, si = math.cos(th), math.sin(th)
        out.append(c + Vector((w * spow(co, 2 / (pt if si >= 0 else pb)), 0, 0)) + U * (h * spow(si, 2 / (pt if si >= 0 else pb))))
    return out


def ring_frame(c, ax, ay, w, ht, hb, n, p=2.4):
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; co, si = math.cos(th), math.sin(th)
        out.append(c + ax * (w * spow(co, 2 / p)) + ay * ((ht if si >= 0 else hb) * spow(si, 2 / p)))
    return out


def ngon_ring(c, e1, e2, r, n, phase=None):
    ph = math.pi / n if phase is None else phase
    rc = r / math.cos(math.pi / n)
    return [c + e1 * (rc * math.cos(ph + 2 * math.pi * k / n)) + e2 * (rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


def mir(rings):
    return [[Vector((-p.x, p.y, p.z)) for p in r] for r in rings]


V = lambda *a: Vector(a)
EYE_R, EYE_PROUD = 0.0105, 0.004


def cone(P, ring, apex, slot):
    """closed pyramid: flat n-gon disc + triangles to a buried apex; returns its faces"""
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def lerp_prof(prof, s):
    for (s0, w0, t0), (s1, w1, t1) in zip(prof, prof[1:]):
        if s0 <= s <= s1:
            f = (s - s0) / (s1 - s0); return w0 + (w1 - w0) * f, t0 + (t1 - t0) * f
    return prof[-1][1], prof[-1][2]


def sym_ring(half):
    """half ring k = 0..N/2 (front -> back on +X side, x of k=0 and N/2 forced to 0) -> full X-symmetric ring"""
    h = [Vector(p) for p in half]; h[0].x = 0.0; h[-1].x = 0.0
    return h + [Vector((-p.x, p.y, p.z)) for p in reversed(h[1:-1])]


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def cast_in(bvh, inner, d, what):
    """outermost surface point along the line inner + t d (cast from outside towards inner)"""
    o = inner + d * 0.6
    hit = bvh.ray_cast(o, -d, 0.6)
    if hit[0] is None: raise RuntimeError(f'no surface hit for {what} from {tuple(inner)} dir {tuple(d)}')
    return hit[0]


# ---------------- mesh ----------------
def head_xf(p):
    return HEAD_C + (Vector(p) - HEAD_C) * HEAD_S + Vector((0, 0, HEAD_DZ))


def sym_half(half, closed_ends):
    """half ring on +X side front -> back. closed_ends: first/last vertex on the mirror plane (x forced 0)."""
    h = [Vector(p) for p in half]
    if closed_ends:
        h[0].x = 0.0; h[-1].x = 0.0
        return h + [Vector((-p.x, p.y, p.z)) for p in reversed(h[1:-1])]
    return h + [Vector((-p.x, p.y, p.z)) for p in reversed(h)]


def feather_path(root, a0, turn, L, p, svals, steps=80):
    """integrate the arc phi(s) = a0 + turn * s**p in the YZ plane; returns [(centre, phi)] at svals"""
    a0r, tr = math.radians(a0), math.radians(turn)
    out = []; pos = Vector(root); ds = 1.0 / steps; s = 0.0; want = list(svals)
    ph = lambda u: a0r + tr * u ** p
    for i in range(steps + 1):
        while want and want[0] <= s + 1e-9:
            out.append((pos.copy(), ph(want[0]))); want.pop(0)
        if i == steps: break
        m = ph(s + ds / 2)
        pos = pos + Vector((0, math.cos(m), math.sin(m))) * (L * ds); s += ds
    return out


def build_mesh():
    P = pc.Part('Rooster')
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 10) for fy, fz, by, bz, w in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK1], GOLD, GOLD, GOLD)
    neck_faces = list(P.comp[-1][1])
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK2], GOLD, GOLD, GOLD)
    neck_faces += list(P.comp[-1][1])
    # head (red face) + small upper beak (triangle section, flat mouth line)
    P.loft('Head', [ring_y(y, w, zb, zt, 10, 2.3, 2.1) for y, w, zb, zt in HEAD_RINGS], HEAD, HEAD, HEAD)
    head_faces = list(P.comp[-1][1])
    P.loft('Head', [[V(0, y, zt), V(-w, y, zm), V(w, y, zm)] for y, w, zm, zt in BEAK_UP], BEAK, BEAK, BEAK)
    y0, z0, y1, z1 = BEAK_UP[0][0], BEAK_UP[0][2], BEAK_UP[2][0], BEAK_UP[2][2]
    zm_at = lambda y: z0 + (y - y0) * (z1 - z0) / (y1 - y0)
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.001), V(-w, y, zm_at(y) - 0.001), V(0, y, zm_at(y) - d)] for y, w, d in BEAK_LO],
           BEAK_D, BEAK_D, BEAK_D)
    # comb: outline at x=0 (ridge), shrunk outline at x=+-T (flat sides); thick spikes
    out = [Vector(p) for p in COMB_OUT]
    sh = [COMB_C + (p - COMB_C) * COMB_SHRINK for p in out]
    rings = [[V(-COMB_T, p.x, p.y) for p in sh], [V(0, p.x, p.y) for p in out], [V(COMB_T, p.x, p.y) for p in sh]]
    P.loft('Comb', rings, COMB, COMB, COMB)
    # wattles: two lobes converging at the bottom (heart), hanging under the beak
    wl = [ring_frame(V(xc, y, z), V(0, -1, 0), V(1, 0, 0), hy, hx, hx, 5, 2.0) for z, y, hy, hx, xc in WATTLE]
    P.loft('Wattle', wl, COMB, COMB, COMB); P.loft('Wattle', mir(wl), COMB, COMB, COMB)

    hv = {v for nm, faces, _ in P.comp if nm in HEAD_PARTS for f in faces for v in f.verts}
    for v in hv: v.co = head_xf(v.co)
    for nm in HEAD_PARTS: JOINTS[nm] = tuple(head_xf(Vector(JOINTS[nm])))
    P.bm.verts.index_update()
    bvh_body, bvh_head, bvh_bn = bvh_of(body_faces), bvh_of(head_faces), bvh_of(body_faces + neck_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: raise RuntimeError(f'no surface hit at y {y} z {z}')
        return hit[0].x, hit[1]

    def surf_x(y, z):
        hit = bvh_body.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is not None: return hit[0].x
        return bvh_body.find_nearest(V(0.12, y, z))[0].x      # plate tip hanging past the body outline
    # eyes: 8-gon dark discs, proud, backed by a pyramid buried in the head
    ec = head_xf(V(0, -0.140, 0.497))
    hx_, n = side_x(bvh_head, ec.y, ec.z); hp = V(hx_, ec.y, ec.z)
    n = (n + V(0, -0.45, 0.06)).normalized()
    t_, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R * HEAD_S, 8); apex = hp - n * 0.009
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # hackle: 2 rows x 8 large leaf wedges (lower row offset half a step, hangs over the breast)
    def cast_pt(z, th, off):
        d = V(math.sin(th), -math.cos(th), 0)
        o = V(0, HACK_AXIS_Y, z) + d * 0.6
        hit = bvh_bn.ray_cast(o, -d, 0.6)
        if hit[0] is None: raise RuntimeError(f'hackle: no hit at z {z} th {th}')
        n = hit[1] if hit[1].dot(d) > 0 else -hit[1]
        return hit[0] + n * off

    def wedge_pts(th, zb, zt, hb, hs):
        zs = zb + (zt - zb) * 0.45; o = HACK_OFF
        pts = dict(L=cast_pt(zb, th - hb, o['base']), R=cast_pt(zb, th + hb, o['base']),
                   SL=cast_pt(zs, th - hs, o['shoulder']), SR=cast_pt(zs, th + hs, o['shoulder']),
                   T=cast_pt(zt, th, o['tip']), M=cast_pt(zb + (zt - zb) * 0.40, th, o['ridge']),
                   B=cast_pt(zb + (zt - zb) * 0.30, th, o['back']))
        return pts

    def mirror_pts(p):
        m = lambda v: Vector((-v.x, v.y, v.z))
        return dict(L=m(p['R']), R=m(p['L']), SL=m(p['SR']), SR=m(p['SL']), T=m(p['T']), M=m(p['M']), B=m(p['B']))

    def centre_pts(p):                   # wedge on the mirror plane: make it exactly symmetric
        q = mirror_pts(p); out = {}
        for k in p: out[k] = (p[k] + q[k]) / 2
        for k in ('T', 'M', 'B'): out[k].x = 0.0
        return out

    def add_wedge(p):
        vs = {k: P.bm.verts.new(v) for k, v in p.items()}
        rim = [vs['L'], vs['SL'], vs['T'], vs['SR'], vs['R']]
        cols = [GOLD, GOLD_T, GOLD_T, GOLD]
        faces = [P.face([rim[i], rim[i + 1], vs['M']], cols[i]) for i in range(4)]
        faces.append(P.face([vs['R'], vs['L'], vs['M']], GOLD_D))
        faces += [P.face([rim[i + 1], rim[i], vs['B']], GOLD_D) for i in range(4)]
        faces.append(P.face([vs['L'], vs['R'], vs['B']], GOLD_D))
        P.comp.append(('Hackle', faces, False))
    tipz = []
    for a0, zb_, zt_, hb, hs in HACK_ROWS:
        for k in range(8):
            a = a0 + 45.0 * k
            if a > 180.0 + 1e-6: continue
            th = math.radians(a); c = (1 + math.cos(th)) / 2
            zb = zb_[1] + (zb_[0] - zb_[1]) * c; zt = zt_[1] + (zt_[0] - zt_[1]) * c
            p = wedge_pts(th, zb, zt, math.radians(hb), math.radians(hs))
            if abs(a) < 1e-6 or abs(a - 180.0) < 1e-6:
                add_wedge(centre_pts(p))
            else:
                add_wedge(p); add_wedge(mirror_pts(p))
            tipz.append((a, round(p['T'].z, 3)))
    print('HACKLE wedge tips (deg, z)', tipz)

    # wings: overlapping leaf plates projected onto the body side (outer face proud, inner face buried)
    for nm, outline, ptop, pbot, slot in WING_PLATES:
        zt = max(z for y, z in outline); zb = min(z for y, z in outline)
        cy = sum(y for y, z in outline) / len(outline); cz = sum(z for y, z in outline) / len(outline)
        outer, inner = [], []
        for y, z in outline:
            pr = ptop + (pbot - ptop) * (zt - z) / (zt - zb)
            outer.append(V(surf_x(y, z) + pr, y, z))
            ys, zs = cy + (y - cy) * 0.82, cz + (z - cz) * 0.82
            inner.append(V(surf_x(ys, zs) - PLATE_BURY, ys, zs))
        P.loft(nm + '.L', [inner, outer], slot, slot, slot); P.loft(nm + '.R', mir([inner, outer]), slot, slot, slot)

    # tail: rump wedge (TailFan1) + 8 thick arched diamond-section plates (TailFan2 5, Tail_Sickle 3)
    a0, a1 = V(0, 0.060, 0.315), V(0, 0.140, 0.352)
    d = (a1 - a0).normalized(); up = V(1, 0, 0).cross(d).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.058, 0.042), (1.0, 0.032, 0.028)]], BODY, BODY, BODY)
    tail_tips = []; peak = 0.0
    for i, (part, a0d, turn, L, p, dz, slot) in enumerate(FEATHERS):
        prof = SICKLE_W if part == 'Tail_Sickle' else FEATHER_W
        tk = 1.15 if i % 2 else 1.0                      # alternate thickness -> layered fan, still X-symmetric
        fr = []
        for (c, ph), (s, w, t) in zip(feather_path(FAN_ROOT + V(0, 0, dz), a0d, turn, L, p, [q[0] for q in prof]), prof):
            ew = V(0, -math.sin(ph), math.cos(ph))
            fr.append([c + ew * w, c + V(t * tk, 0, 0), c - ew * w, c - V(t * tk, 0, 0)])
            peak = max(peak, (c + ew * w).z)
        tail_tips.append(fr[-1][0])
        P.loft(part, fr, slot, slot, slot)
    print(f'TAIL peak z {peak:.3f}')

    # legs: small red feathered thigh, thick 6-gon orange shank, ankle pad + 4 separated toes
    X, Y = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.222, 0.037), (0.172, 0.033), (0.142, 0.020)]],
               BODY, BODY, BODY)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.156, 0.0210), (0.012, 0.0160)]],
               LEG, LEG, LEG)
        P.loft('Foot' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.0, 0.023), (0.028, 0.0180)]],
               LEG_D, LEG_D, LEG_D, ground=True)
        base = c(0.0)
        for yaw, L in [(0, 0.086), (34, 0.074), (-34, 0.074), (180 - 15, 0.042)]:
            a = math.radians(yaw); dv = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            r0 = base + dv * 0.012; r1 = base + dv * L
            toe = [[r0 + sd * 0.0110 + V(0, 0, 0.003), r0 - sd * 0.0110 + V(0, 0, 0.003), r0 + V(0, 0, 0.022)],
                   [r1 + sd * 0.0060, r1 - sd * 0.0060, r1 + V(0, 0, 0.011)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, tail_tips


# ---------------- colours ----------------
def colour(P):
    for nm, faces, _ in P.comp:
        if nm == 'Body':
            for f in faces:
                if f.normal.z < -0.55: f[P.slot] = BODY_D


# ---------------- numbers ----------------
def com_of(bm):
    vol = 0.0; acc = Vector()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]; v = a.dot(b.cross(c)) / 6.0
            vol += v; acc += v * (a + b + c) / 4.0
    return acc / vol, vol


def tris_by_part(P):
    out = {}
    for nm, faces, _ in P.comp:
        out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in faces)
    return out


def joint(nm):
    if nm in JOINTS: return Vector(JOINTS[nm])
    base = nm[:-2] + '.L'
    if nm.endswith('.R') and base in JOINTS:
        j = Vector(JOINTS[base]); return Vector((-j.x, j.y, j.z))
    return None


def split_to_objects(P, coll, mat, root, eye_centres):
    groups = {}
    for nm, faces, _ in P.comp: groups.setdefault(nm, []).extend(faces)
    obs = {}
    for nm, faces in groups.items():
        piv = joint(nm) if joint(nm) is not None else eye_centres[nm]
        bm = bmesh.new(); sl = bm.faces.layers.int.new('slot'); vm = {}
        for f in faces:
            vs = []
            for v in f.verts:
                if v not in vm: vm[v] = bm.verts.new(v.co - piv)
                vs.append(vm[v])
            nf = bm.faces.new(vs); nf[sl] = f[P.slot]
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        uvl = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            f.smooth = False; uv = pc.cell_uv(f[sl])
            for lp in f.loops: lp[uvl].uv = uv
        me = bpy.data.meshes.new(ASSET + '_' + nm); bm.to_mesh(me); bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(nm, me); coll.objects.link(ob)
        ob.parent = root; ob.location = piv
        obs[nm] = ob
    return obs


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)     # factory-startup cube/light/camera
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    P, tips = build_mesh()
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    colour(P)
    com, vol = com_of(P.bm)
    sh = Vector((0, -com.y, 0))                    # root pivot = ground under the centre of mass
    for v in P.bm.verts: v.co += sh
    for k in JOINTS: JOINTS[k] = tuple(Vector(JOINTS[k]) + sh)
    eyes = {}
    for nm, faces, _ in P.comp:
        if nm.startswith('Eye'):
            vs = {v for f in faces for v in f.verts}; eyes[nm] = sum((v.co for v in vs), Vector()) / len(vs)
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1000:.2f} L -> shifted y by {sh.y:+.4f}')
    print('TAIL tip (y,z) after shift:', [(round(t.y + sh.y, 3), round(t.z, 3)) for t in tips])
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_RoosterAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_RoosterAll', me)
    coll.objects.link(tmp); cop = pc.coplanar_overlaps(tmp)
    for a, b in cop[1]:
        print('   coplanar pair at', [tuple(round(c, 4) for c in me.polygons[i].center) for i in (a, b)])
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.1
    obs = split_to_objects(P, coll, mat, root, eyes)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target {BUDGET} ({100 * tot / BUDGET - 100:+.0f} %)')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'SIZE width(x) {hi[0]-lo[0]:.3f} length(y) {hi[1]-lo[1]:.3f} height(z) {hi[2]-lo[2]:.3f} | lowest z {lo[2]:.5f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop[0]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop[0], tris=tri, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))


VIEWS = [REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (0.03, 1, 0.15), (0.25, 0.15, 1.0)]


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Rooster_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Rooster_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-02 Rooster', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Rooster_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=REF_VIEW,
                   fill=(0.62, 0.82))
