# build_turkey.py - BRD-07 Turkey (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_turkey.py -- BRD-07 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_turkey)
# look  : build + EEVEE look at the reference angle into TEMP (no art output)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure follows ../Rooster/build_rooster.py (helpers copied, shared modules imported read-only).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Turkey'
TAG = 'FarmAnimals_Turkey'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-07.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_turkey')
REF_VIEW = (0.62, -0.78, 0.17)       # reference: front-left three-quarter, ~40 deg from the front, ~10 deg above
PALETTE = ['#3E2D28', '#2F221E', '#4E3A32', '#3A2A25',
           '#33251F', '#5F4232', '#85603F', '#47352E',
           '#D8656A', '#B9474E', '#CC2F38', '#EBB070',
           '#CF8F52', '#E57A30', '#C45F24', '#2A1D17']
(BODY, BODY_D, WING, WING_D, FAN_D, FAN_M, FAN_T, BODY_L, HEAD, HEAD_D, WATTLE, BEAK, BEAK_D, LEG, LEG_D, EYE) = range(16)
BUDGET = 1300

JOINTS = {
    'Body': (0, 0.0, 0.36), 'Neck1': (0, -0.180, 0.440), 'Neck2': (0, -0.195, 0.560), 'Head': (0, -0.205, 0.640),
    'Beak_Lower': (0, -0.262, 0.630), 'Wattle': (0, -0.255, 0.620), 'BreastTuft': (0, -0.300, 0.360),
    'WingUpper.L': (0.150, -0.090, 0.450), 'WingLower.L': (0.160, -0.060, 0.330), 'WingTip.L': (0.160, 0.030, 0.300),
    'TailFan1': (0, 0.150, 0.380), 'TailFan2': (0, 0.250, 0.360), 'TailFan_Side.L': (0, 0.250, 0.360),
    'LegUpper.L': (0.100, -0.020, 0.300), 'LegLower.L': (0.100, -0.020, 0.150), 'Foot.L': (0.100, -0.020, 0.020),
}
LEG_X, LEG_Y = 0.100, -0.020

# body rings (front-bottom y, z, back-top y, z, half width), breast -> rump; front rings tilted (breast flows into the neck)
BODY_RINGS = [(-0.240, 0.425, -0.178, 0.475, 0.045), (-0.292, 0.360, -0.152, 0.505, 0.125),
              (-0.312, 0.262, -0.105, 0.540, 0.172), (-0.262, 0.190, -0.060, 0.556, 0.190),
              (-0.160, 0.165, 0.000, 0.550, 0.200), (-0.040, 0.165, 0.060, 0.540, 0.200),
              (0.080, 0.180, 0.120, 0.520, 0.180), (0.170, 0.230, 0.190, 0.480, 0.140),
              (0.230, 0.300, 0.235, 0.440, 0.080)]
BODY_N = 10
# neck rings, horizontal (z, y centre, half x, half front, half back)
NECK1 = [(0.375, -0.188, 0.082, 0.076, 0.070), (0.470, -0.196, 0.068, 0.064, 0.058), (0.565, -0.202, 0.058, 0.055, 0.048)]
NECK2 = [(0.535, -0.201, 0.061, 0.057, 0.050), (0.665, -0.207, 0.048, 0.047, 0.038)]
# head rings along -Y (y, half width, z bottom, z top)
HEAD_RINGS = [(-0.148, 0.036, 0.618, 0.684), (-0.170, 0.056, 0.598, 0.708), (-0.212, 0.062, 0.591, 0.718),
              (-0.252, 0.052, 0.602, 0.708), (-0.280, 0.031, 0.620, 0.688)]
# upper beak (y, half width, mouth z, top z); lower beak (y, half width, depth below the mouth)
BEAK_UP = [(-0.262, 0.026, 0.636, 0.680), (-0.285, 0.021, 0.626, 0.664), (-0.305, 0.013, 0.612, 0.640), (-0.322, 0.004, 0.596, 0.608)]
BEAK_LO = [(-0.262, 0.021, 0.018), (-0.282, 0.015, 0.012), (-0.300, 0.005, 0.004)]
# dewlap rings, horizontal (z, half depth, half width, sink into the surface behind)
DEWLAP = [(0.632, 0.014, 0.020, 0.010), (0.570, 0.017, 0.023, 0.007), (0.500, 0.017, 0.027, 0.007),
          (0.440, 0.015, 0.025, 0.007), (0.392, 0.008, 0.012, 0.006)]
# caruncles: (centre of the cast, az from the front towards +X deg, elevation deg, radius, part); az 0/180 = centre bumps
HEAD_C = (0, -0.215, 0.655)
CARUNCLES = [(HEAD_C, 0, 58, 0.023, 'Wattle'), (HEAD_C, 0, 86, 0.025, 'Wattle'), (HEAD_C, 180, 52, 0.023, 'Wattle'),
             (HEAD_C, 40, 60, 0.023, 'Wattle'), (HEAD_C, 118, 48, 0.023, 'Wattle'), (HEAD_C, 150, 12, 0.020, 'Wattle'),
             ((0, -0.205, 0.615), 110, 0, 0.022, 'Neck2'), ((0, -0.203, 0.575), 74, 0, 0.023, 'Neck2'),
             ((0, -0.200, 0.535), 106, 0, 0.024, 'Neck1'), ((0, -0.198, 0.497), 76, 0, 0.023, 'Neck1')]
BUMP_N, BUMP_LIFT, BUMP_TOP, BUMP_SINK = 6, 0.008, 0.018, 0.012
# wing tiers along y: (y, z centre, half height, proud)
WING_UP = [(-0.110, 0.448, 0.020, 0.020), (-0.080, 0.442, 0.062, 0.046), (0.070, 0.436, 0.070, 0.050), (0.170, 0.428, 0.020, 0.025)]
WING_LO = [(-0.070, 0.332, 0.020, 0.020), (-0.040, 0.325, 0.055, 0.040), (0.100, 0.316, 0.060, 0.040), (0.180, 0.322, 0.020, 0.022)]
# drooping primaries: (root y, root z, tip y, tip z, extra x at the tip, slot)
PRIMARIES = [(0.020, 0.300, 0.150, 0.190, 0.004, WING), (0.085, 0.298, 0.228, 0.186, -0.004, WING_D)]
PRIM_W = [(0.0, 0.044, 0.018), (0.5, 0.054, 0.020), (1.0, 0.014, 0.010)]   # (s, half width, half thick)
# tail fan
FAN_ROOT = Vector((0, 0.250, 0.360))
FAN_R, FAN_R0, FAN_TILT, FAN_CUP, FAN_STEP = 0.410, 0.040, 15.0, 0.090, 0.022
FAN_ANG = [-80, -60, -40, -20, 0, 20, 40, 60, 80]
FAN_PROF = [(0.00, 0.034, 0.012, FAN_D), (0.42, 0.064, 0.016, FAN_M), (0.60, 0.072, 0.016, FAN_D),
            (0.82, 0.080, 0.016, FAN_T), (1.00, 0.068, 0.012, None)]      # (s, half width, half thick, slot of the next segment)


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-07', 'build'])[:2]


# ---------------- ring helpers (copied from the rooster) ----------------
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
EYE_R, EYE_PROUD = 0.0135, 0.005


def cone(P, ring, apex, slot):
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def bump(P, ring, top, apex, slot):
    """faceted caruncle: lifted n-gon ring, dome point on top, buried apex below (closed, 2n tris)"""
    vs = [P.bm.verts.new(p) for p in ring]; t = P.bm.verts.new(top); a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], t], slot) for k in range(n)]
    faces += [P.face([vs[(k + 1) % n], vs[k], a], slot) for k in range(n)]
    return faces


def lerp_prof(prof, s):
    for (s0, w0, t0), (s1, w1, t1) in zip(prof, prof[1:]):
        if s0 <= s <= s1:
            f = (s - s0) / (s1 - s0); return w0 + (w1 - w0) * f, t0 + (t1 - t0) * f
    return prof[-1][1], prof[-1][2]


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def cast_n(bvh, inner, d, what):
    """outermost surface point + outward normal along the line inner + t d (cast from outside towards inner)"""
    d = d.normalized(); o = inner + d * 0.8
    hit = bvh.ray_cast(o, -d, 0.8)
    if hit[0] is None: raise RuntimeError(f'no surface hit for {what} from {tuple(inner)} dir {tuple(d)}')
    n = hit[1].normalized()
    if n.dot(d) < 0: n = -n
    return hit[0], n


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Turkey')
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, BODY_N) for fy, fz, by, bz, w in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK1], HEAD, HEAD, HEAD)
    neck_faces = list(P.comp[-1][1])
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK2], HEAD, HEAD, HEAD)
    neck_faces += list(P.comp[-1][1])
    P.loft('Head', [ring_y(y, w, zb, zt, 10, 2.3, 2.1) for y, w, zb, zt in HEAD_RINGS], HEAD, HEAD, HEAD)
    head_faces = list(P.comp[-1][1])
    P.loft('Head', [[V(0, y, zt), V(-w, y, zm), V(w, y, zm)] for y, w, zm, zt in BEAK_UP], BEAK, BEAK, BEAK)
    y0, z0, y1, z1 = BEAK_UP[0][0], BEAK_UP[0][2], BEAK_UP[2][0], BEAK_UP[2][2]
    zm_at = lambda y: z0 + (y - y0) * (z1 - z0) / (y1 - y0)
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.001), V(-w, y, zm_at(y) - 0.001), V(0, y, zm_at(y) - d)] for y, w, d in BEAK_LO],
           BEAK_D, BEAK_D, BEAK_D)

    P.bm.verts.index_update()
    bvh_body = bvh_of(body_faces); bvh_head = bvh_of(head_faces)
    bvh_all = bvh_of(body_faces + neck_faces + head_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: return None
        return hit[0].x

    # dewlap: long tapered red tongue from under the chin down the neck front onto the breast (x = 0, front surface cast)
    rings = []
    for z, hd, hw, sink in DEWLAP:
        p, _ = cast_n(bvh_all, V(0, -0.15, z), V(0, -1, 0), 'dewlap')
        c = V(0, p.y - hd + sink, z)
        rings.append(ring_frame(c, ax, front, hw, hd, hd, 6, 2.2))
    P.loft('Wattle', rings, WATTLE, WATTLE, WATTLE)

    # caruncles: faceted 5-gon bumps on the crown (Wattle) and the neck sides (Neck1/Neck2), +X side mirrored
    for cen, az, el, r, part in CARUNCLES:
        a, e = math.radians(az), math.radians(el)
        d = V(math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e))
        p, n = cast_n(bvh_all, V(*cen), d, 'caruncle')
        centre = az in (0, 180)
        if centre: p.x = 0.0; n.x = 0.0; n.normalize()
        _, e1, e2 = pc.basis(n, (0, 0, 1))
        ring = ngon_ring(p + n * BUMP_LIFT, e1, e2, r, BUMP_N)
        top, apex = p + n * BUMP_TOP, p - n * BUMP_SINK
        P.comp.append((part, bump(P, ring, top, apex, WATTLE), False))
        if not centre:
            m = lambda q: Vector((-q.x, q.y, q.z))
            P.comp.append((part, bump(P, list(reversed([m(q) for q in ring])), m(top), m(apex), WATTLE), False))

    # eyes: 8-gon dark discs, EYE_PROUD proud, backed by a pyramid buried in the head
    hx_ = side_x(bvh_head, -0.228, 0.684)
    hit = bvh_head.ray_cast(V(1.0, -0.228, 0.684), V(-1, 0, 0)); n = hit[1].normalized()
    if n.x < 0: n = -n
    hp = V(hx_, -0.228, 0.684)
    n = (n + V(0, -0.50, 0.05)).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); apex = hp - n * 0.010
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # breast tuft: small near-black tassel following the breast front below the dewlap
    # straight tassel: top sunk into the breast, lower part hangs free in front of the receding lower breast
    p, _ = cast_n(bvh_body, V(0, -0.10, 0.360), V(0, -1, 0), 'tuft')
    rings = []
    for z, dy, w, hd in [(0.352, 0.004, 0.022, 0.016), (0.300, -0.007, 0.025, 0.018), (0.252, -0.012, 0.011, 0.009)]:
        c = V(0, p.y + dy, z)
        rings.append([c + V(w, 0, 0), c + V(0, -hd, 0), c - V(w, 0, 0), c + V(0, hd, 0)])
    P.loft('BreastTuft', rings, EYE, EYE, EYE)

    # wings: hexagon-ish sections hugging the body side (top tucked in, lower lip proud)
    def wing_rings(spec):
        rings = []
        for y, zc, h, pr in spec:
            pts = []
            for dz, dx in [(h, -0.003), (0.45 * h, 0.8 * pr), (-0.45 * h, pr), (-h, 0.65 * pr), (0.0, -0.014)]:
                xs = side_x(bvh_body, y, zc + dz)
                if xs is None: raise RuntimeError(f'wing ray miss y {y} z {zc + dz}')
                pts.append(V(xs + dx, y, zc + dz))
            rings.append(pts)
        return rings
    for nm, spec, slot in (('WingUpper', WING_UP, WING), ('WingLower', WING_LO, WING_D)):
        r = wing_rings(spec)
        P.loft(nm + '.L', r, slot, slot, slot); P.loft(nm + '.R', mir(r), slot, slot, slot)
    # drooping primaries: diamond-section pointed plates, rooted under the lower wing, outside the body side
    for ry, rz, ty, tz, tx, slot in PRIMARIES:
        R0, R1 = V(0, ry, rz), V(0, ty, tz)
        axv = (R1 - R0).normalized(); ew = V(1, 0, 0).cross(axv).normalized()
        x_root = side_x(bvh_body, ry, rz) + 0.004
        x_tip = 0.165 + tx
        fr = []
        for s, w, t in PRIM_W:
            c = R0.lerp(R1, s); x = x_root + (x_tip - x_root) * s
            xs = side_x(bvh_body, c.y, c.z)
            if xs is not None and s > 0: x = max(x, xs + t + 0.004)
            c.x = x
            fr.append([c + ew * w, c + V(t, 0, 0), c - ew * w, c - V(t, 0, 0)])
        P.loft('WingTip.L', fr, slot, slot, slot); P.loft('WingTip.R', mir(fr), slot, slot, slot)

    # tail: rump wedge (TailFan1) + fan of diamond-section plates (TailFan2 centre, TailFan_Side.L/.R outer)
    a0, a1 = V(0, 0.150, 0.385), V(0, 0.300, 0.360)
    d = (a1 - a0).normalized(); up = V(1, 0, 0).cross(d).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.110, 0.075), (1.0, 0.060, 0.045)]], BODY_L, BODY_L, BODY_L)
    tl = math.radians(FAN_TILT)
    nf = V(0, math.cos(tl), -math.sin(tl))                     # fan plane normal (backwards)
    tips = []
    for i, ang in enumerate(FAN_ANG):
        ph = math.radians(ang)
        u = V(math.sin(ph), math.cos(ph) * math.sin(tl), math.cos(ph) * math.cos(tl))
        ew = nf.cross(u).normalized()
        depth = FAN_STEP if (abs(ang) // 20) % 2 else 0.0
        part = 'TailFan2' if abs(ang) <= 40 else ('TailFan_Side.L' if ang > 0 else 'TailFan_Side.R')
        rings, slots = [], []
        for s, w, t, sl in FAN_PROF:
            r = FAN_R0 + (FAN_R - FAN_R0) * s
            c = FAN_ROOT + u * r + nf * depth - nf * (FAN_CUP * (1 - math.cos(ph)) * s * s)
            rings.append([c + ew * w, c - nf * t, c - ew * w, c + nf * t]); slots.append(sl)
        tips.append(rings[-1][1])
        P.loft(part, rings, lambda j, k, sl=slots: sl[j], FAN_D, FAN_T)

    # legs: dark feathered thigh, thick 6-gon orange shank, ankle pad + 4 toes
    X, Y = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.310, 0.068), (0.205, 0.060), (0.135, 0.038)]],
               BODY_D, BODY_D, BODY_D)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.150, 0.0250), (0.014, 0.0210)]],
               LEG, LEG, LEG)
        P.loft('Foot' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.0, 0.032), (0.034, 0.024)]],
               LEG_D, LEG_D, LEG_D, ground=True)
        base = c(0.0)
        for yaw, L in [(0, 0.110), (34, 0.095), (-34, 0.095), (180 - 12, 0.052)]:
            a = math.radians(yaw); dv = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            r0 = base + dv * 0.010; r1 = base + dv * L
            toe = [[r0 + sd * 0.0140 + V(0, 0, 0.003), r0 - sd * 0.0140 + V(0, 0, 0.003), r0 + V(0, 0, 0.030)],
                   [r1 + sd * 0.0075, r1 - sd * 0.0075, r1 + V(0, 0, 0.014)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, tips


# ---------------- colours ----------------
def colour(P):
    for nm, faces, _ in P.comp:
        if nm == 'Body':
            for f in faces:
                if f.normal.z < -0.55: f[P.slot] = BODY_D
        if nm.startswith('Neck'):
            for f in faces:
                if f[P.slot] == HEAD and f.normal.z < -0.6: f[P.slot] = HEAD_D


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
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1000:.2f} L -> shifted y by {sh.y:+.4f}; '
          f'legs at y {LEG_Y + sh.y:+.4f}')
    print('FAN tip (x,y,z) after shift:', [(round(t.x, 3), round(t.y + sh.y, 3), round(t.z, 3)) for t in tips])
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_TurkeyAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_TurkeyAll', me)
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
    for nm in sorted(tri): print(f'   {nm:15s} {tri[nm]:4d}')
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Turkey_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Turkey_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


PREVIEW_VIEW, PREVIEW_FILL = (0.80, -0.80, 0.16), (0.62, 0.80)

if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-07 Turkey', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Turkey_look.png'), view=PREVIEW_VIEW, fill=PREVIEW_FILL)
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
