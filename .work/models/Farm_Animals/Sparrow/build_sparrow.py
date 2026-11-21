# build_sparrow.py - BRD-09 Sparrow, Farm Animals, skeleton B parts, MESH ONLY (no armature/weights/clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_sparrow.py -- BRD-09 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_sparrow)
# look  : build + EEVEE look at the preview angle (TEMP)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Pigeon/build_pigeon.py (ring helpers, split_to_objects, checks, renders).
# Head and body are lofted from explicit triangles (diagonal chosen per quad) so colour areas end on slanted facet edges.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Sparrow'
TAG = 'FarmAnimals_Sparrow'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-09.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_sparrow')
REF_VIEW = (0.62, -0.78, 0.16)       # reference: front three-quarter from the bird's left, ~9 deg above
PREVIEW_VIEW, PREVIEW_FILL = (0.71, -0.70, 0.27), (0.68, 0.84)
PALETTE = ['#A85A3C', '#8A4630', '#B86C4A', '#DFC0A2',
           '#93583C', '#2B2420', '#AD9480', '#8F7969',
           '#C0AC99', '#A0573A', '#6B3B28', '#D8BE9C',
           '#7C4A34', '#8E7A6C', '#E8A23A', '#2A1D17']
(CAP, CROWN, CAP_L, CHEEK, NAPE, BIB, BODY, BODY_D, BELLY, WING, WING_D, BAR, TAIL, BEAK, LEG, EYE) = range(16)
BUDGET = 450

LEG_X, LEG_Y = 0.017, 0.006
JOINTS = {
    'Body': (0, 0.006, 0.050), 'Neck1': (0, -0.010, 0.066), 'Neck2': (0, -0.012, 0.076), 'Head': (0, -0.016, 0.084),
    'Beak_Lower': (0, -0.045, 0.085),
    'WingUpper.L': (0.030, -0.004, 0.078), 'WingLower.L': (0.034, 0.012, 0.054), 'WingTip.L': (0.026, 0.038, 0.054),
    'TailFan1': (0, 0.036, 0.0565), 'TailFan2': (0, 0.0529, 0.0503),
    'LegUpper.L': (LEG_X, LEG_Y, 0.040), 'LegLower.L': (LEG_X, LEG_Y, 0.026), 'Foot.L': (LEG_X, LEG_Y, 0.002),
}

# body rings, tilted sections (front-bottom y, z, back-top y, z, half width, bottom exponent); 12 sides, k=0 back-top.
# R0 = cap inside the head; R1 = lower edge of the bib (pointed front vertex -> V); R2 widest chest; R3 belly.
BODY_RINGS = [(-0.040, 0.077, 0.000, 0.088, 0.026, 2.0), (-0.047, 0.060, 0.020, 0.090, 0.037, 1.5),
              (-0.048, 0.040, 0.034, 0.082, 0.042, 2.0), (-0.024, 0.018, 0.050, 0.070, 0.040, 2.4),
              (0.020, 0.019, 0.058, 0.059, 0.030, 2.4), (0.045, 0.037, 0.058, 0.053, 0.013, 2.0)]
# neck connectors, horizontal 6-gons (z, y centre, apothem)
NECK1 = [(0.062, -0.010, 0.016), (0.078, -0.012, 0.015)]
NECK2 = [(0.072, -0.012, 0.015), (0.088, -0.014, 0.014)]
# head: faceted ellipsoid ball (radii x, y, z), 12-vertex latitude rings with alternating half-step offsets (antiprism
# strips = paper-craft triangles, no vertical columns), a 6-vertex ring and an apex on the crown (no flat top)
HEAD_C = Vector((0, -0.019, 0.093))
HEAD_R = (0.0315, 0.0300, 0.0290)
HEAD_LAT = [(-55, 0), (-30, 15), (-6, 0), (18, 15), (42, 0)]      # (latitude deg, ring offset deg)
HEAD_TOP_LAT = 66
# cheek pads: 8-gon faceted domes sunk into the head (azimuth from the front, latitude, radius, proud mid, proud centre)
CHEEK_PAD = (42, -19, 0.0102, 0.0006, 0.0009)
# upper beak (y, half width, mouth z, top z): 5-point rounded cone (ridge, shoulders, lips)
BEAK_UP = [(-0.043, 0.0088, 0.0850, 0.0950), (-0.0535, 0.0062, 0.0835, 0.0905), (-0.0605, 0.0012, 0.0817, 0.0835)]
BEAK_LO = [(-0.044, 0.0082, 0.0060), (-0.0575, 0.0030, 0.0022)]
# wing shield along y: (y, z centre, half height, proud)
WING_UP = [(-0.018, 0.077, 0.010, 0.005), (0.008, 0.067, 0.027, 0.0150), (0.042, 0.055, 0.013, 0.0110)]
WING_LO = [(0.006, 0.045, 0.005, 0.0030), (0.026, 0.042, 0.010, 0.0120), (0.044, 0.049, 0.005, 0.0040)]
# wing tip (primaries) folded back from the wing onto the tail base: start (y, z, proud), end (x, y, lift over tail)
WING_TIP0, WING_TIP1 = (0.036, 0.054, 0.006), (0.0080, 0.076, 0.0012)
EYE_R, EYE_PROUD, EYE_YAW, EYE_UP = 0.0042, 0.0013, 20, 0.07
# tail: ONE flat wedge (6-pt section), root inside the rump, 20 deg down; TailFan1 = root part, TailFan2 = tip part
TAIL_R0, TAIL_L, TAIL_PITCH = Vector((0, 0.036, 0.0565)), 0.060, -20
TAIL_W, TAIL_T, TAIL_SPLIT = (0.0100, 0.0180), (0.0048, 0.0040), 0.30       # half width, half thickness root/tip


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-09', 'build'])[:2]


# ---------------- ring helpers (copied from the pigeon) ----------------
def spow(c, e):
    return math.copysign(abs(c) ** e, c)


def ring_tilt(fy, fz, by, bz, w, n, pt=2.0, pb=2.0):
    F, B = Vector((0, fy, fz)), Vector((0, by, bz)); c = (F + B) / 2; U = (B - F).normalized(); h = (B - F).length / 2
    out = []
    for k in range(n):
        th = math.pi / 2 + 2 * math.pi * k / n; co, si = math.cos(th), math.sin(th)
        p = pt if si >= 0 else pb
        out.append(c + Vector((w * spow(co, 2 / p), 0, 0)) + U * (h * spow(si, 2 / p)))
    return out


def ring_frame(c, ax, ay, w, ht, hb, n, p=2.0):
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


def cone(P, ring, apex, slot):
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def tilt_ring(z, yc, tilt, hx, hf, hb, n, p=2.0):
    a = math.radians(tilt)
    return ring_frame(V(0, yc, z), V(1, 0, 0), V(0, -math.cos(a), -math.sin(a)), hx, hf, hb, n, p)


def loft_tri(P, cname, rings, colfn, cap0, cap1, hex_cap1=False):
    """closed loft from triangles. Face k spans ring vertices k..k+1 (k=0 = vertex on the symmetry plane);
    s = mirror-symmetric face index. colfn(j, s) -> slot, or (diag, slot_e0, slot_e1): diag 0 splits a quad from the
    lower vertex of the edge nearer vertex 0 to the upper vertex of the far edge, diag 1 the other way; slot_e0 is the
    triangle that owns the near edge. Diagonals are mirrored, so colour areas are exactly symmetric."""
    R = [[P.bm.verts.new(p) for p in r] for r in rings]; n = len(R[0]); faces = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            a, b, c, d = R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]
            if k < n // 2: e0l, e1l, e1u, e0u = a, b, c, d
            else: e0l, e1l, e1u, e0u = b, a, d, c
            s = k if k < n // 2 else n - 1 - k
            r = colfn(j, s)
            diag, c0, c1 = ((j + s) % 2, r, r) if isinstance(r, int) else r
            if diag == 0: t0, t1 = (e0l, e1u, e0u), (e0l, e1l, e1u)
            else: t0, t1 = (e0l, e1l, e0u), (e1l, e1u, e0u)
            faces.append(P.face(list(t0), c0)); faces.append(P.face(list(t1), c1))
    if cap0 is not None: faces.append(P.face(list(reversed(R[0])), cap0))
    if cap1 is not None:
        top = R[-1]
        if hex_cap1:                  # 6 border triangles + planar hexagon: no slivers, no pole fan
            for i in range(0, n, 2): faces.append(P.face([top[i], top[i + 1], top[(i + 2) % n]], cap1))
            faces.append(P.face([top[i] for i in range(0, n, 2)], cap1))
        else:
            faces.append(P.face(list(top), cap1))
    P.comp.append((cname, faces, False))
    return R


# ---------------- colour maps ----------------
def head_tri_col(c):
    d = Vector((c.x / HEAD_R[0], (c.y - HEAD_C.y) / HEAD_R[1], (c.z - HEAD_C.z) / HEAD_R[2]))
    el = math.degrees(math.asin(max(-1.0, min(1.0, d.z / d.length))))
    az = math.degrees(math.atan2(abs(d.x), -d.y))
    if el > 46: return CROWN
    if el > -10: return CAP_L if (az < 16 and el < 30) else CAP
    if az < 31: return BIB
    if az > 105: return NAPE
    return BODY if el < -34 else CAP             # lower side: brown round the cheek pad, tan below it


def body_col(j, s):
    # j: 0 R0-R1 (under the head / bib), 1 R1-R2 chest, 2 R2-R3 belly, 3 R3-R4 under tail, 4 rump
    # s: 0 back-top .. 5 front-bottom
    if j == 0:
        if s == 5: return BIB
        if s == 4: return (0, BODY, BIB)             # widens the bib shield under the head
        return NAPE if s <= 2 else BODY
    if j == 1:
        return WING if s <= 2 else BODY
    if j == 2:
        if s <= 1: return WING_D
        return BELLY if s >= 4 else BODY
    if j == 3:
        return WING_D if s <= 1 else BELLY if s >= 4 else BODY_D
    return WING_D if s <= 2 else BODY_D


# ---------------- tail frame ----------------
TDIR = Vector((0, math.cos(math.radians(TAIL_PITCH)), math.sin(math.radians(TAIL_PITCH))))
TX = Vector((1, 0, 0)); TUP = TDIR.cross(Vector((-1, 0, 0))).normalized()
if TUP.z < 0: TUP = -TUP


def tail_at(sv):
    return (TAIL_R0 + TDIR * (TAIL_L * sv), TAIL_W[0] + (TAIL_W[1] - TAIL_W[0]) * sv,
            TAIL_T[0] + (TAIL_T[1] - TAIL_T[0]) * sv)


def tail_top(y):
    sv = (y - TAIL_R0.y) / (TDIR.y * TAIL_L); c, w, t = tail_at(sv)
    return c.z + t / TUP.z


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Sparrow')
    body_r = [ring_tilt(fy, fz, by, bz, w, 12, 2.0, pb) for fy, fz, by, bz, w, pb in BODY_RINGS]
    loft_tri(P, 'Body', body_r, body_col, BODY, WING_D)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    for nm, spec in (('Neck1', NECK1), ('Neck2', NECK2)):       # hidden connectors: 4-gon boxes
        P.loft(nm, [ngon_ring(V(0, y, z), ax, front, r, 4) for z, y, r in spec], NAPE, NAPE, NAPE)
    def hpt(lat, az):
        la, a = math.radians(lat), math.radians(az)
        return V(HEAD_R[0] * math.cos(la) * math.sin(a), HEAD_C.y - HEAD_R[1] * math.cos(la) * math.cos(a),
                 HEAD_C.z + HEAD_R[2] * math.sin(la))
    rings = [[P.bm.verts.new(hpt(lat, off + 30 * k)) for k in range(12)] for lat, off in HEAD_LAT]
    tris = []
    for (A, (_, oa)), (B, (_, ob)) in zip(zip(rings, HEAD_LAT), zip(rings[1:], HEAD_LAT[1:])):
        sh = 0 if ob > oa else 1                     # index of the B vertex between A_k and A_k+1
        for k in range(12):
            bm_, bp = B[(k + sh) % 12], B[(k + sh - 1) % 12]
            tris += [(A[k], A[(k + 1) % 12], bm_), (A[k], bm_, bp)]
    A = rings[-1]                                    # offset 0: 6-ring vertices above the odd A vertices
    top = [P.bm.verts.new(hpt(HEAD_TOP_LAT, 30 + 60 * i)) for i in range(6)]
    apex = P.bm.verts.new(hpt(90, 0))
    for i in range(6):
        a0, a1, a2 = A[2 * i], A[2 * i + 1], A[(2 * i + 2) % 12]
        tris += [(a0, a1, top[i]), (a1, a2, top[i]), (a2, top[(i + 1) % 6], top[i]), (top[i], top[(i + 1) % 6], apex)]
    hf = [P.face(list(t), head_tri_col(sum((v.co for v in t), Vector()) / 3)) for t in tris]
    hf.append(P.face(list(reversed(rings[0])), NAPE))
    P.comp.append(('Head', hf, False))
    head_faces = list(hf)

    # upper beak: rounded cone; section = ridge, shoulder R, lip R, lip L, shoulder L
    def bill_ring(y, w, zm, zt):
        zs = zt - 0.40 * (zt - zm)
        return [V(0, y, zt), V(0.85 * w, y, zs), V(w, y, zm), V(-w, y, zm), V(-0.85 * w, y, zs)]
    R = P.loft('Head', [bill_ring(*r) for r in BEAK_UP[:2]], BEAK, BEAK, None)     # base ring + mid ring
    tipv = P.bm.verts.new(V(0, BEAK_UP[2][0], BEAK_UP[2][2]))                      # blunt cone tip
    last = R[-1]
    P.comp[-1][1].extend(P.face([last[k], last[(k + 1) % 5], tipv], BEAK) for k in range(5))
    y0, z0, y1, z1 = BEAK_UP[0][0], BEAK_UP[0][2], BEAK_UP[-1][0], BEAK_UP[-1][2]
    zm_at = lambda y: z0 + (y - y0) * (z1 - z0) / (y1 - y0)
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.0006), V(-w, y, zm_at(y) - 0.0006), V(0, y, zm_at(y) - d)]
                          for y, w, d in BEAK_LO], BEAK, BEAK, BEAK)

    def bvh_of(faces):
        vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])
    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def side_x(bvh, y, z):
        for zz in (z, z - 0.003, z + 0.003, z - 0.006, z + 0.006, z - 0.009, z + 0.009):   # off the body: nearest row
            hit = bvh.ray_cast(V(1.0, y, zz), V(-1, 0, 0))
            if hit[0] is not None: return hit[0].x
        raise RuntimeError(f'no surface hit at y {y} z {z}')
    # eyes: dark 8-gon discs on the front-side of the head, backed by a buried pyramid
    a = math.radians(EYE_YAW); d = V(math.sin(a), -math.cos(a), EYE_UP).normalized()
    hit = bvh_head.ray_cast(HEAD_C + d * 0.3, -d)
    if hit[0] is None: raise RuntimeError('eye ray missed the head')
    hn = hit[1] if hit[1].dot(d) > 0 else -hit[1]
    hp, n = hit[0], (hn + d).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); apex = hp - n * 0.005
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # cheek pads: 8-gon faceted cream domes, rim sunk 0.6 mm into the head, all points projected onto the head
    caz, clat, crad, cmid, ctop = CHEEK_PAD
    la, a = math.radians(clat), math.radians(caz)
    dc = V(math.cos(la) * math.sin(a), -math.cos(la) * math.cos(a), math.sin(la))

    def onhead(p, lift):
        dd = (p - HEAD_C).normalized(); h = bvh_head.ray_cast(HEAD_C + dd * 0.2, -dd)
        if h[0] is None: raise RuntimeError('cheek ray missed the head')
        return h[0] + dd * lift
    pc0 = onhead(HEAD_C + dc * 0.03, 0.0)
    _, c1, c2 = pc.basis(dc, (0, 0, 1))
    ang = lambda k, ph: c1 * math.cos(ph + k * math.pi / 4) + c2 * math.sin(ph + k * math.pi / 4)
    rim = [onhead(pc0 + ang(k, math.pi / 8) * crad, -0.0006) for k in range(8)]
    mid = [onhead(pc0 + ang(k, 0.0) * crad * 0.58, cmid) for k in range(8)]
    ctr = onhead(pc0, ctop)
    for sgn in (1, -1):
        f = (lambda q: q) if sgn == 1 else (lambda q: V(-q.x, q.y, q.z))
        R0 = [P.bm.verts.new(f(q)) for q in rim]; R1 = [P.bm.verts.new(f(q)) for q in mid]; C = P.bm.verts.new(f(ctr))
        fs = []
        for k in range(8):
            k1 = (k + 1) % 8
            fs += [P.face([R0[k], R0[k1], R1[k1]], CHEEK), P.face([R0[k], R1[k1], R1[k]], CHEEK),
                   P.face([R1[k], R1[k1], C], CHEEK)]
        fs.append(P.face(list(reversed(R0)), CAP))
        P.comp.append(('Head', fs, False))

    # wing shield: sections hugging the body side (fz = height factor, fx = proud factor, negative = inside)
    def wing_rings(spec, sec):
        rings = []
        for y, zc, h, pr in spec:
            rings.append([V(side_x(bvh_body, y, zc + fz * h) + fx * pr, y, zc + fz * h) for fz, fx in sec])
        return rings
    SEC5 = [(1.0, -0.4), (0.40, 0.85), (-0.60, 1.0), (-1.0, 0.75), (0.0, -0.9)]
    SEC6 = [(1.0, -0.4), (0.50, 0.80), (-0.05, 1.0), (-0.55, 0.95), (-1.0, 0.60), (0.0, -0.9)]
    up_col = lambda j, k: BAR if k == 2 else WING_D if k == 3 else WING
    lo_col = lambda j, k: BAR if k == 1 else WING_D if k in (2, 3) else WING
    r = wing_rings(WING_UP, SEC5)
    P.loft('WingUpper.L', r, up_col, WING, WING); P.loft('WingUpper.R', mir(r), up_col, WING, WING)
    r = wing_rings(WING_LO, SEC5)
    P.loft('WingLower.L', r, lo_col, WING, WING_D); P.loft('WingLower.R', mir(r), lo_col, WING, WING_D)
    # wing tip: dark primaries folded back from the rear of the wing onto the tail base (tapered plate)
    (ty0, tz0, tpr), (tx1, ty1, tlift) = WING_TIP0, WING_TIP1
    p0 = V(side_x(bvh_body, ty0, tz0) + tpr, ty0, tz0)
    p1 = V(tx1, ty1, tail_top(ty1) + tlift)
    dv = (p1 - p0).normalized(); sd = V(-dv.y, dv.x, 0).normalized(); uu = dv.cross(sd).normalized()
    if uu.z < 0: uu = -uu
    tip = [[p + sd * w + uu * t, p - sd * w + uu * t, p - sd * w * 0.8 - uu * t, p + sd * w * 0.8 - uu * t]
           for p, w, t in ((p0, 0.0085, 0.0030), (p1, 0.0040, 0.0013))]
    P.loft('WingTip.L', tip, WING_D, WING_D, WING_D); P.loft('WingTip.R', mir(tip), WING_D, WING_D, WING_D)

    # tail: ONE flat wedge; TailFan1 = root part (mostly inside the rump), TailFan2 = visible part starting 0.8 mm
    # inset inside TailFan1 (overlap at the joint, no coplanar faces)
    for nm, s0, s1, ins in (('TailFan1', 0.0, TAIL_SPLIT + 0.06, 0.0), ('TailFan2', TAIL_SPLIT, 1.0, 0.0008)):
        rings = []
        for sv, d in ((s0, ins), (s1, 0.0)):
            c, w, t = tail_at(sv); w -= d; t -= d
            rings.append([c + TX * w, c + TX * (0.5 * w) + TUP * t, c - TX * (0.5 * w) + TUP * t, c - TX * w,
                          c - TX * (0.5 * w) - TUP * t, c + TX * (0.5 * w) - TUP * t])
        P.loft(nm, rings, lambda j, k: TAIL if k in (0, 1, 2) else WING_D, WING_D, WING_D)

    # legs: hidden thigh, thick orange 6-gon shank, foot: 3 front toes + 1 back toe (ridged triangular prisms)
    Xa, Ya = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), Xa, Ya, r, 4) for z, r in [(0.042, 0.0056), (0.026, 0.0048)]],
               BODY_D, BODY_D, BODY_D)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), Xa, Ya, r, 6) for z, r in [(0.030, 0.0043), (0.0015, 0.0041)]],
               LEG, LEG, LEG)
        base = c(0.0)
        for yaw, L, wr in [(0, 0.0140, 0.0022), (36, 0.0122, 0.0020), (-36, 0.0122, 0.0020), (180, 0.0080, 0.0019)]:
            a = math.radians(yaw); dv = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            q0 = base + dv * 0.0010; q1 = base + dv * L
            toe = [[q0 + sd * wr + V(0, 0, 0.0006), q0 - sd * wr + V(0, 0, 0.0006), q0 + V(0, 0, 0.0040)],
                   [q1 + sd * wr * 0.70, q1 - sd * wr * 0.70, q1 + V(0, 0, 0.0016)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, body_faces


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
    P, _ = build_mesh()
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    com, vol = com_of(P.bm)
    sh = Vector((0, -com.y, 0))                    # root pivot = ground under the centre of mass
    for v in P.bm.verts: v.co += sh
    for k in JOINTS: JOINTS[k] = tuple(Vector(JOINTS[k]) + sh)
    eyes = {}
    for nm, faces, _ in P.comp:
        if nm.startswith('Eye'):
            vs = {v for f in faces for v in f.verts}; eyes[nm] = sum((v.co for v in vs), Vector()) / len(vs)
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1e6:.1f} cm3 -> shifted y by {sh.y:+.4f}')
    feet = [v.co for nm, faces, _ in P.comp if nm.startswith('Foot') for f in faces for v in f.verts]
    print(f'feet y range {min(p.y for p in feet):.4f}..{max(p.y for p in feet):.4f} (COM y = 0 after shift)')
    small = [(nm, round(f.calc_area() * 1e6, 2)) for nm, faces, _ in P.comp for f in faces if f.calc_area() < 1.5e-6]
    print(f'faces < 1.5 mm2: {len(small)} {small[:12]}')
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_SparrowAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_SparrowAll', me)
    coll.objects.link(tmp); cop = pc.coplanar_overlaps(tmp)
    for a, b in cop[1]:
        print('   coplanar pair at', [tuple(round(c, 4) for c in me.polygons[i].center) for i in (a, b)])
    bpy.data.objects.remove(tmp, do_unlink=True); bpy.data.meshes.remove(me)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.05
    obs = split_to_objects(P, coll, mat, root, eyes)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target {BUDGET} ({100 * tot / BUDGET - 100:+.0f} %), ceiling 650')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'SIZE width(x) {hi[0]-lo[0]:.4f} length(y) {hi[1]-lo[1]:.4f} height(z) {hi[2]-lo[2]:.4f} | lowest z {lo[2]:.5f}')
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop[0]} '
          f'mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop[0], tris=tri, total=tot,
                size=(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.10), (0.0, 1, 0.15), (-0.8, 0.9, 0.45), (0.25, 0.15, 1.0),
                 (-0.62, -0.78, 0.16)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 4, os.path.join(CHECK, f'Sparrow_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Sparrow_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-09 Sparrow', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Sparrow_look.png'), view=PREVIEW_VIEW,
                   fill=PREVIEW_FILL)
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
