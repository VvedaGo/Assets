# build_crow.py - BRD-10 Crow, Farm Animals, skeleton B parts, MESH ONLY (no armature/weights/clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_crow.py -- BRD-10 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_crow)
# look  : build + EEVEE look at the reference angle and the preview angle (TEMP)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Pigeon/build_pigeon.py (pear body of tilted rings, egg head, hidden necks, ray-cast eyes,
# split_to_objects, checks, renders) and ../Rooster/build_rooster.py (wing = overlapping plates projected on the body).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Crow'
TAG = 'FarmAnimals_Crow'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-10.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_crow')
REF_VIEW = (0.82, -0.57, 0.15)       # reference: front-left three-quarter, body yaw ~55 deg from the front, ~8 deg above
PREVIEW_VIEW = (0.72, -0.69, 0.17)   # preview: a bit more frontal so the straight head shows the face (ref turns the head)
PALETTE = ['#2A2733', '#1E1C26', '#3A364A', '#3E4E92',
           '#34438A', '#252B50', '#1C2038', '#24222F',
           '#34437E', '#8E959B', '#AAB1B6', '#6E757B',
           '#E86A2A', '#C2531C', '#3B1D16', '#5A3122']
(BODY, BODY_D, BODY_L, WING_L, WING, WING_D, WING_E, TAIL, TAIL_TOP, BEAK, BEAK_L, BEAK_D, LEG, LEG_D, EYE, EYE_RIM) = range(16)
BUDGET = 900

LEG_X, LEG_Y = 0.042, -0.034
JOINTS = {
    'Body': (0, -0.020, 0.220), 'Neck1': (0, -0.100, 0.268), 'Neck2': (0, -0.104, 0.292), 'Head': (0, -0.104, 0.312),
    'Beak_Lower': (0, -0.152, 0.299),
    'WingUpper.L': (0.066, -0.070, 0.278), 'WingLower.L': (0.072, -0.050, 0.232), 'WingTip.L': (0.062, 0.000, 0.195),
    'TailFan1': (0, 0.100, 0.200), 'TailFan2': (0, 0.125, 0.186),
    'LegUpper.L': (LEG_X, LEG_Y, 0.150), 'LegLower.L': (LEG_X, LEG_Y, 0.110), 'Foot.L': (LEG_X, LEG_Y, 0.010),
}

# body rings, tilted sections (front-bottom y, z, back-top y, z, half width, bottom exponent); 12 sides.
# R0 = cap inside the head, R1 throat, R2/R3 broad chest, R4/R5 belly, R6 vent, R7 cap inside the rump wedge
BODY_RINGS = [(-0.128, 0.300, -0.068, 0.338, 0.040, 2.2), (-0.164, 0.234, -0.028, 0.310, 0.074, 2.2),
              (-0.168, 0.185, -0.002, 0.292, 0.087, 2.2), (-0.150, 0.142, 0.028, 0.274, 0.084, 2.2),
              (-0.100, 0.112, 0.060, 0.254, 0.072, 2.2), (-0.025, 0.104, 0.090, 0.234, 0.057, 2.2),
              (0.045, 0.128, 0.115, 0.214, 0.042, 2.2), (0.092, 0.160, 0.135, 0.200, 0.022, 2.2)]
# neck rings, horizontal (z, y centre, half x, half front, half back), 6 sides (hidden connectors)
NECK1 = [(0.262, -0.096, 0.030, 0.026, 0.026), (0.300, -0.100, 0.028, 0.025, 0.025)]
NECK2 = [(0.286, -0.100, 0.029, 0.025, 0.025), (0.330, -0.104, 0.027, 0.024, 0.024)]
# head rings, horizontal tilted (z centre, y centre, tilt deg (front down), half x, half front, half back), 12 sides
HEAD_RINGS = [(0.276, -0.098, 15, 0.038, 0.036, 0.034), (0.296, -0.104, 6, 0.054, 0.047, 0.048),
              (0.326, -0.106, 5, 0.062, 0.060, 0.054), (0.360, -0.106, 0, 0.057, 0.055, 0.050),
              (0.385, -0.104, 0, 0.040, 0.040, 0.036), (0.399, -0.102, 0, 0.018, 0.018, 0.016)]
HEAD_S, HEAD_C = 1.06, 0.335          # head scale about its centre height (bigger head, top stays at ~0.40)
# upper beak (y, half width, mouth z, top z): 5-point wedge (ridge, 2 shoulders, 2 lips); last ring hooks down
BEAK_UP = [(-0.148, 0.030, 0.297, 0.350), (-0.172, 0.025, 0.295, 0.341), (-0.192, 0.016, 0.292, 0.329),
           (-0.207, 0.0075, 0.288, 0.313), (-0.217, 0.0018, 0.282, 0.292)]
BEAK_LO = [(-0.150, 0.027, 0.021), (-0.176, 0.017, 0.015), (-0.199, 0.007, 0.006)]
EYE_R, EYE_PROUD, EYE_YAW, EYE_Z, EYE_BASE = 0.0098, 0.005, 45, 0.346, 1.35
# wing plates: (part, outline (y, z) top edge front->back then lower edge back->front, proud top, proud bottom, slot, x floor)
WING_PLATES = [
    ('WingUpper', [(-0.108, 0.266), (-0.085, 0.300), (-0.040, 0.308), (0.020, 0.294), (0.072, 0.264), (0.086, 0.236),
                   (0.030, 0.224), (-0.035, 0.226), (-0.096, 0.236)], 0.004, 0.022, WING_L, 0.0),
    ('WingLower', [(-0.100, 0.240), (-0.050, 0.250), (0.020, 0.246), (0.088, 0.224), (0.118, 0.196), (0.055, 0.186),
                   (-0.015, 0.190), (-0.072, 0.196), (-0.104, 0.216)], 0.006, 0.025, WING_D, 0.0),
    ('WingLower', [(-0.090, 0.208), (-0.020, 0.216), (0.055, 0.210), (0.122, 0.188), (0.158, 0.160), (0.088, 0.154),
                   (0.015, 0.158), (-0.050, 0.166), (-0.088, 0.184)], 0.008, 0.028, WING, 0.024),
    ('WingTip', [(-0.035, 0.186), (0.050, 0.196), (0.125, 0.190), (0.175, 0.178), (0.206, 0.166), (0.160, 0.160),
                 (0.100, 0.150), (0.020, 0.152), (-0.035, 0.164)], 0.010, 0.030, WING_L, 0.022),
]
PLATE_BURY, PLATE_SHRINK, PLATE_BULGE, PLATE_FREE_T, PLATE_FREE_K = 0.006, 0.80, 0.004, 0.012, 0.5
# tail: rump wedge axis, main wedge root -> tip, sections (s, half width, half thickness)
RUMP = (Vector((0, 0.098, 0.202)), Vector((0, 0.150, 0.180)))
TAIL_AX = (Vector((0, 0.118, 0.194)), Vector((0, 0.296, 0.090)))
TAIL_SEC = [(0.0, 0.036, 0.022), (0.5, 0.048, 0.018), (1.0, 0.054, 0.014)]
TAIL_TOPW = 0.75                     # flat top spans +-0.75 of the half width
# top plates on the tail (part, [(s, half width)], ridge height); s along TAIL_AX
TAIL_PLATES = [('TailFan1', [(-0.10, 0.020), (0.08, 0.034), (0.30, 0.030), (0.40, 0.008)], 0.010),
               ('TailFan2', [(0.30, 0.020), (0.55, 0.036), (0.84, 0.032), (0.95, 0.010)], 0.008)]


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-10', 'build'])[:2]


# ---------------- ring helpers (copied from the pigeon) ----------------
def spow(c, e):
    return math.copysign(abs(c) ** e, c)


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


def tilt_ring(z, yc, tilt, hx, hf, hb, n, p=2.2):
    a = math.radians(tilt)
    return ring_frame(V(0, yc, z), V(1, 0, 0), V(0, -math.cos(a), -math.sin(a)), hx, hf, hb, n, p)


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def tail_frame():
    r0, r1 = TAIL_AX; dv = (r1 - r0).normalized(); up = V(1, 0, 0).cross(dv).normalized()
    if up.z < 0: up = -up
    return r0, r1, up


def tail_at(s):
    """half width / half thickness of the main tail wedge at s (linear in TAIL_SEC, clamped)"""
    if s <= TAIL_SEC[0][0]: return TAIL_SEC[0][1:]
    for (s0, w0, t0), (s1, w1, t1) in zip(TAIL_SEC, TAIL_SEC[1:]):
        if s0 <= s <= s1:
            f = (s - s0) / (s1 - s0); return w0 + (w1 - w0) * f, t0 + (t1 - t0) * f
    return TAIL_SEC[-1][1:]


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Crow')
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 12, 2.2, pb) for fy, fz, by, bz, w, pb in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK1], BODY, BODY, BODY)
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 6) for z, y, w, df, db in NECK2], BODY, BODY, BODY)
    hs = lambda z, yc, t, hx, hf, hb: (HEAD_C + (z - HEAD_C) * HEAD_S - 0.003, yc, t, hx * HEAD_S, hf * HEAD_S, hb * HEAD_S)
    P.loft('Head', [tilt_ring(*hs(*r), 12) for r in HEAD_RINGS], BODY, BODY, BODY)
    head_faces = list(P.comp[-1][1])
    P.hidden = []                    # (what, points, faces of the hiding shells) -> printed as exposed-vertex counts

    # upper beak: deep wedge (ridge, shoulder R, lip R, lip L, shoulder L), lighter ridge faces, hooked last ring
    def bill_ring(y, w, zm, zt):
        zs = zt - 0.40 * (zt - zm)
        return [V(0, y, zt), V(0.78 * w, y, zs), V(w, y, zm), V(-w, y, zm), V(-0.78 * w, y, zs)]
    P.loft('Head', [bill_ring(*r) for r in BEAK_UP], lambda j, k: BEAK_L if k in (0, 4) else (BEAK_D if k == 2 else BEAK),
           BEAK, BEAK)
    ys = [r[0] for r in BEAK_UP[:4]]; zs = [r[2] for r in BEAK_UP[:4]]

    def zm_at(y):
        for (y0, z0), (y1, z1) in zip(zip(ys, zs), zip(ys[1:], zs[1:])):
            if y1 <= y <= y0: return z0 + (y - y0) * (z1 - z0) / (y1 - y0)
        return zs[-1]
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.0012), V(-w, y, zm_at(y) - 0.0012), V(0, y, zm_at(y) - d)]
                          for y, w, d in BEAK_LO], BEAK_D, BEAK_D, BEAK_D)

    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)
    neck_pts = [v.co.copy() for nm, fs, _ in P.comp if nm.startswith('Neck') for f in fs for v in f.verts]
    r0 = ring_tilt(*BODY_RINGS[0][:5], 12, 2.2, BODY_RINGS[0][5])
    P.hidden = [('neck verts outside head+body', neck_pts, (bvh_body, bvh_head)), ('body cap R0 outside head', r0, (bvh_head,))]

    # eyes: 8-gon dark brown discs, proud, lighter brown walls down to a buried apex
    a = math.radians(EYE_YAW); d = V(math.sin(a), -math.cos(a), 0.05).normalized(); hc = V(0, -0.106, EYE_Z)
    hit = bvh_head.ray_cast(hc + d * 0.3, -d)
    if hit[0] is None: raise RuntimeError('eye ray missed the head')
    hn = hit[1] if hit[1].dot(d) > 0 else -hit[1]
    hp, n = hit[0], (hn + d).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8, 0.0); base = ngon_ring(hp - n * 0.002, e1, e2, EYE_R * EYE_BASE, 8, 0.0)
    apex = hp - n * 0.010
    for nm, rg, bs, apx in (('Eye.L', ring, base, apex), ('Eye.R', mir([ring])[0], mir([base])[0], V(-apex.x, apex.y, apex.z))):
        vs = [P.bm.verts.new(p) for p in rg]; vb = [P.bm.verts.new(p) for p in bs]; av = P.bm.verts.new(apx)
        faces = [P.face([vs[k], vs[(k + 1) % 8], vb[(k + 1) % 8], vb[k]], EYE_RIM) for k in range(8)]
        faces += [P.face([vb[k], vb[(k + 1) % 8], av], EYE_RIM) for k in range(8)]
        faces.append(P.face(list(reversed(vs)), EYE))
        P.comp.append((nm, faces, False))

    # wing: overlapping plates projected on the body side; outer face = fan to a proud centre (follows the body curve),
    # thickness band + buried inner cap in the dark edge colour
    def sx(y, z, floor):
        h = bvh_body.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if h[0] is None or h[0].x < floor: return floor, False
        return h[0].x, True
    for nm, outline, ptop, pbot, slot, floor in WING_PLATES:
        zt = max(z for y, z in outline); zb = min(z for y, z in outline)
        cy = sum(y for y, z in outline) / len(outline); cz = sum(z for y, z in outline) / len(outline)
        pr = lambda z: ptop + (pbot - ptop) * (zt - z) / (zt - zb)
        outer, inner = [], []
        for y, z in outline:
            xs_, on = sx(y, z, floor)
            xo = xs_ + pr(z) * (1.0 if on else PLATE_FREE_K); outer.append(V(xo, y, z))
            ys_, zs_ = cy + (y - cy) * PLATE_SHRINK, cz + (z - cz) * PLATE_SHRINK
            xi, on = sx(ys_, zs_, floor)
            inner.append(V(xi - PLATE_BURY if on else xi + pr(zs_) * PLATE_FREE_K - PLATE_FREE_T, ys_, zs_))
        centre = V(sx(cy, cz, floor)[0] + pr(cz) + PLATE_BULGE, cy, cz)
        for sfx, rings, cen in (('.L', [inner, outer], centre), ('.R', mir([inner, outer]), V(-centre.x, centre.y, centre.z))):
            R = P.loft(nm + sfx, rings, WING_E, WING_E, None)
            cv = P.bm.verts.new(cen); m = len(R[1])
            P.comp[-1][1].extend(P.face([R[1][k], R[1][(k + 1) % m], cv], slot) for k in range(m))

    # tail: rump wedge (TailFan1), long broad wedge with a blue flat top (TailFan2), blue top plates on both
    a0, a1 = RUMP; dv = (a1 - a0).normalized(); up = V(1, 0, 0).cross(dv).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.040, 0.030), (1.0, 0.032, 0.018)]], BODY, BODY, BODY)
    r0, r1, up = tail_frame(); X = V(1, 0, 0)
    tl = []
    for s, w, t in TAIL_SEC:
        c = r0.lerp(r1, s)
        tl.append([c + X * w + up * (0.3 * t), c + X * (TAIL_TOPW * w) + up * t, c - X * (TAIL_TOPW * w) + up * t, c - X * w + up * (0.3 * t),
                   c - X * (0.6 * w) - up * t, c + X * (0.6 * w) - up * t])
    P.loft('TailFan2', tl, lambda j, k: TAIL_TOP if k in (0, 1, 2) else (BODY_D if k == 4 else TAIL), TAIL, TAIL)
    for nm, prof, ridge in TAIL_PLATES:
        rings = []
        for s, w in prof:
            tw, tt = tail_at(s); c = r0.lerp(r1, s) + up * tt
            rings.append([c + X * w - up * 0.002, c + up * ridge, c - X * w - up * 0.002, c - up * 0.008])
        P.loft(nm, rings, lambda j, k: WING if k in (0, 1) else WING_E, WING_E, WING_E)

    # legs: dark thigh cuff, thick orange 6-gon shank, ankle pad + 4 separated ridged toes (3 front, 1 back)
    Y = V(0, 1, 0)
    for sfx, sxn in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sxn * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.165, 0.030), (0.122, 0.029), (0.098, 0.019)]],
               BODY, BODY, BODY_D)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.112, 0.0145), (0.014, 0.0130)]],
               LEG, LEG, LEG_D)
        P.loft('Foot' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.002, 0.0190), (0.026, 0.0155)]],
               LEG_D, LEG_D, LEG_D)
        base = c(0.0)
        for yaw, L, wr in [(0, 0.058, 0.0082), (37, 0.050, 0.0076), (-37, 0.050, 0.0076), (180, 0.034, 0.0074)]:
            a = math.radians(yaw); dv = V(sxn * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            q0 = base + dv * 0.006; q1 = base + dv * L
            toe = [[q0 + sd * wr + V(0, 0, 0.0015), q0 + sd * wr * 0.95 + V(0, 0, 0.011), q0 + V(0, 0, 0.018),
                    q0 - sd * wr * 0.95 + V(0, 0, 0.011), q0 - sd * wr + V(0, 0, 0.0015)],
                   [q1 + sd * wr * 0.62, q1 + sd * wr * 0.58 + V(0, 0, 0.006), q1 + V(0, 0, 0.009),
                    q1 - sd * wr * 0.58 + V(0, 0, 0.006), q1 - sd * wr * 0.62]]
            P.loft('Foot' + sfx, toe, lambda j, k: LEG_D if k == 4 else LEG, LEG, LEG)
    return P


def inside(bvh, p):
    """parity test along +X for a closed shell"""
    n, o = 0, Vector(p)
    for _ in range(50):
        h = bvh.ray_cast(o, Vector((1, 0, 0)), 2.0)
        if h[0] is None: break
        n += 1; o = h[0] + Vector((1e-5, 0, 0))
    return n % 2 == 1


def hidden_report(P):
    for what, pts, shells in P.hidden:
        out = sum(1 for p in pts if not any(inside(b, p) for b in shells))
        print(f'HIDDEN {what}: {out} of {len(pts)}')


# ---------------- colours ----------------
def colour(P):
    """three body shades by facet: up-facing lighter, down-facing darker (paper-craft look of the reference)"""
    for nm, faces, _ in P.comp:
        if nm in ('Body', 'Head', 'TailFan1', 'LegUpper.L', 'LegUpper.R'):
            for f in faces:
                if f[P.slot] != BODY: continue
                if f.normal.z > 0.55: f[P.slot] = BODY_L
                elif f.normal.z < -0.40: f[P.slot] = BODY_D


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
    P = build_mesh()
    hidden_report(P)
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
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1000:.3f} L -> shifted y by {sh.y:+.4f}')
    feet = [v.co for nm, faces, _ in P.comp if nm.startswith('Foot') for f in faces for v in f.verts]
    print(f'feet y range {min(p.y for p in feet):.3f}..{max(p.y for p in feet):.3f} (COM y = 0 after shift)')
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_CrowAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_CrowAll', me)
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


VIEWS = [REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (0.45, 1, 0.35), (0.25, 0.15, 1.0)]


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 600, 400)
    g = rn.ground(sc); cam = rn.camera(sc)
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 400)] + tiles, 3, os.path.join(CHECK, f'Crow_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Crow_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-10 Crow', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Crow_look_ref.png'), view=REF_VIEW, fill=(0.64, 0.86))
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Crow_look_prev.png'), view=PREVIEW_VIEW,
                   fill=(0.64, 0.86))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=PREVIEW_VIEW,
                   fill=(0.64, 0.86))
