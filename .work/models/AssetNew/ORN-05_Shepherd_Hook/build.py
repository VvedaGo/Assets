# build.py - ORN-05 Shepherd's hook with hanging basket (FMS_Garden_Shepherd_Hook + _Feeder), pack AssetNew
# (Cottage Garden Decor), atlas F Garden_Flora (read only), material M_Garden_Flora.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- ORN-05 build|export|verify|dump
#   build  = build both assets + printed checks + check renders to %TEMP%/assetnew_check/ORN-05/
#   export = build + 2 FBX (base, _Feeder; each with its .fbm) + 2 collection-only .blend + ONE preview (base)
#            + _Feeder check render (%TEMP%) + FBX re-import verify + geometry dump (JSON, SHA1)
#   verify = only re-import both FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\ORN-05_Shepherd_Hook\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['ORN-05', 'build']})
#   Live mode touches only the collections ORN-05_Shepherd_Hook and ORN-05_Shepherd_Hook_Feeder.
# Axes (Blender): X = towards the hook (Unity X under the series assumption is -X, see notes.md), -Y = front, Z = up.
# Pivot: root = foot of the pole = spike tip on the ground (0, 0, 0). Moving part `Hanging` (direct root child): pivot on
# the hanging point = centre-line of the hook curl where the ring hangs. No LOD (catalogue).
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'ORN-05')
NAME = 'FMS_Garden_Shepherd_Hook'
VAR = '_Feeder'
COLL = 'ORN-05_Shepherd_Hook'
COLL_VAR = COLL + VAR
PREVIEW = 'FMS_Garden_ORN_05_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'          # shared atlas F (Garden_Flora) - READ ONLY here
ATLAS_MAT = 'M_Garden_Flora'
BUDGET = {'': 600, VAR: 600}
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
PINK, PINK_L, WHITE, IRON, YELLOW, SOIL, BASKET, STONE = 6, 7, 8, 10, 11, 12, 13, 14
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part, ngon

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'ORN-05'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi

# ---------------- dimensions (spec prompts/ORN-05.3d.md; reference references/ORN-05.png measured, see notes.md) ----------------
A_POLE = 0.020           # pole / arc apothem: 8-sided, 0.040 across the flats (STR-02 frame anchor; spec 0.035, reference ~0.045)
A_THIN = 0.015           # footrest, scroll, suspension rods: 0.030 across (STYLE minimum)
A_TIP = 0.015            # the hook curl tapers to 0.030 at its end
Z_COLLAR, A_COLLAR = 0.13, 0.027   # spike: tip on the ground -> widest collar ring -> pole
Z_POLE0 = 0.165          # pole starts above the collar
Z_BEND = 1.50            # straight pole ends, hook arc starts (reference 1.50)
RA = 0.18                # hook arc radius (centre-line): top 1.68 (+rod = 1.70), right side at x 0.36
N_ARC = 6                # arc segments (180 deg)
CURL_R0, CURL_R1 = 0.066, 0.024    # curl radius, start -> end (spiral inward, clockwise seen from the front)
CURL_SPAN, N_CURL = 300.0, 5       # 60 deg steps: the segment from -60 to -120 deg is the (almost) horizontal bottom
Z_FOOT, FOOT_X1 = 0.28, 0.15       # footrest along +X (reference height; spec 0.18)
# S-scroll on the -X side of the pole (STR-02 s_curve construction, both curls touch the pole)
EMBED = 0.004
SCROLL = dict(R=0.045, dv=0.18, vt=1.04, seg_top=4, seg_bot=4, spine_seg=1)
S_SPAN, S_TIPK = 290.0, 0.48
SIDES_ROD = 6            # suspension rods: 6-sided (budget 600: see notes.md)
SIDES_SQ = 4             # scroll and footrest: square bar 0.03 (wrought-iron flat-faced scroll; budget, see notes.md)
# ring: 5 segments (flat top, vertex at the bottom where the rods meet), triangular wire section, in the YZ plane (threaded on the curl bottom, where the rod runs along X)
RING_R, RING_W, RING_N = 0.040, 0.014, 5   # centre-line radius (to the vertices), wire section circumradius, segments
# basket (8-sided, a flat faces -Y)
BOWL = dict(z0=1.03, a0=0.080, z2=1.15, a2=0.137, z3=1.136, a3=0.116)
ROD_AZ = (8.7, 128.7, 248.7)       # two rods at +-60 deg from the preview camera azimuth (-51.3), one behind
ROD_END = (0.122, 1.138)           # (radius, z) of the rod ends, in the basket rim / feeder roof
DROP_AZ = (68.7, 188.7, 308.7)     # foliage drops between the rods
DROP_R, DROP_D, DROP_SINK = 0.050, 0.170, 0.022
# feeder
FEED = dict(tray=(0.935, 0.955, 0.130), body=(0.950, 1.132, 0.100), win_w=0.064, win_z=(0.992, 1.072), win_d=0.045, win_az=(270.0, 0.0),
            roof=(1.127, 1.142, 1.227, 0.152), knob=(1.212, 1.240, 1.268, 0.020))
TOWARD = Vector((0.62, -0.78, 0.0)).normalized()   # preview camera side (blooms tilt towards it)


def V(x, y, z): return Vector((x, y, z))


def oct_sec(a, n=8):
    return ngon(a / math.cos(math.pi / n), n, math.pi / n)          # flats normal to the section axes


def pol(az, r, z, c=(0.0, 0.0)):
    a = math.radians(az); return V(c[0] + r * math.cos(a), c[1] + r * math.sin(a), z)


# ---------------- hook geometry (Body) ----------------
def hook_path():
    """centre-line points (pole bottom ring -> arc -> curl) and apothems; the spike tip is added separately"""
    pts = [V(0, 0, Z_COLLAR), V(0, 0, Z_POLE0), V(0, 0, Z_BEND)]; aps = [A_COLLAR, A_POLE, A_POLE]
    for k in range(1, N_ARC + 1):
        th = math.pi - math.pi * k / N_ARC
        pts.append(V(RA + RA * math.cos(th), 0, Z_BEND + RA * math.sin(th))); aps.append(A_POLE)
    cx = 2 * RA - CURL_R0
    for k in range(1, N_CURL + 1):
        f = k / N_CURL; th = -math.radians(CURL_SPAN) * f; r = CURL_R0 + (CURL_R1 - CURL_R0) * f
        pts.append(V(cx + r * math.cos(th), 0, Z_BEND + r * math.sin(th))); aps.append(A_POLE + (A_TIP - A_POLE) * f)
    return pts, aps


def hanging_point():
    """middle of the curl segment between -60 and -120 deg (its bottom, the rod runs along X there)"""
    pts, aps = hook_path(); i = 3 + N_ARC                             # index of the curl point at -60 deg (k = 1)
    a, b = pts[i], pts[i + 1]
    return (a + b) / 2, (aps[i] + aps[i + 1]) / 2


def mitred_rings(pts, aps, n=8, up=Vector((0, 1, 0))):
    rings = []
    for i, c in enumerate(pts):
        d1 = (c - pts[i - 1]).normalized() if i > 0 else None
        d2 = (pts[i + 1] - c).normalized() if i < len(pts) - 1 else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in oct_sec(aps[i], n)])
    return rings


def main_rod(P):
    """spike tip (ground) + collar + pole + hook arc + curl: ONE closed 8-sided sweep, end cap at the curl tip"""
    pts, aps = hook_path(); R = [[P.bm.verts.new(v) for v in r] for r in mitred_rings(pts, aps)]
    tip = P.bm.verts.new(V(0, 0, 0)); n = 8; fs = []
    fs += [P.face([tip, R[0][(k + 1) % n], R[0][k]], IRON) for k in range(n)]
    for j in range(len(R) - 1):
        fs += [P.face([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]], IRON) for k in range(n)]
    fs.append(P.face(list(R[-1]), IRON))
    P.comp.append(('Hook', fs, True))


def straight_rod(P, cname, p0, p1, a, n, ref, slot=IRON):
    p0, p1 = Vector(p0), Vector(p1)
    t = (p1 - p0).normalized(); r = Vector(ref)
    if abs(t.dot(r.normalized())) > 0.95: r = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
    e1 = (r - t * r.dot(t)).normalized(); e2 = t.cross(e1)
    rings = [[P.bm.verts.new(c + e1 * u + e2 * v) for u, v in oct_sec(a, n)] for c in (p0, p1)]
    fs = [P.face(list(reversed(rings[0])), slot), P.face(list(rings[1]), slot)]
    fs += [P.face([rings[0][k], rings[0][(k + 1) % n], rings[1][(k + 1) % n], rings[1][k]], slot) for k in range(n)]
    P.comp.append((cname, fs, False))


def s_curve(R, dv, vt, seg_top, seg_bot, spine_seg):
    """STR-02 S-scroll centre-line (u = away from the pole axis, v = up), both curls touch the pole; own curl counts"""
    span = math.radians(S_SPAN); rt = S_TIPK * R
    rad = lambda frac: rt + (R - rt) * frac
    u_l = A_POLE + A_THIN - EMBED
    uct = u_l + R
    rb180 = rad(1 - math.pi / span)
    ucb = u_l + rb180
    vb = vt - dv
    pts = []
    for k in range(seg_top + 1):
        f = k / seg_top; th = math.pi - span * (1 - f)
        pts.append((uct + rad(f) * math.cos(th), vt + rad(f) * math.sin(th)))
    P0, P1 = Vector((uct - R, vt)), Vector((ucb + R, vb)); T = Vector((0, -dv))
    for k in range(1, spine_seg):
        s = k / spine_seg
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        q = P0 * h00 + T * h10 + P1 * h01 + T * h11; pts.append((q.x, q.y))
    for k in range(seg_bot + 1):
        f = 1 - k / seg_bot; th = -span * (1 - f)
        pts.append((ucb + rad(f) * math.cos(th), vb + rad(f) * math.sin(th)))
    return pts


def s_clearance(pts, skip=0.06):
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + math.dist(a, b))
    best = 9.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if acc[j] - acc[i] > skip: best = min(best, math.dist(pts[i], pts[j]))
    return best


def scroll(P):
    p2 = s_curve(**SCROLL)
    pts = [V(-u, 0, v) for u, v in p2]
    R = [[P.bm.verts.new(v) for v in r] for r in mitred_rings(pts, [A_THIN] * len(pts), SIDES_SQ)]
    n = SIDES_SQ; fs = [P.face(list(reversed(R[0])), IRON), P.face(list(R[-1]), IRON)]
    for j in range(len(R) - 1):
        fs += [P.face([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]], IRON) for k in range(n)]
    P.comp.append(('Scroll', fs, False))
    return p2


def build_body():
    P = Part('Body')
    main_rod(P)
    straight_rod(P, 'Footrest', (0, 0, Z_FOOT), (FOOT_X1, 0, Z_FOOT), A_THIN, SIDES_SQ, (0, 0, 1))
    p2 = scroll(P)
    return P, p2


# ---------------- hanging part ----------------
def ring_geo():
    H, a_h = hanging_point()
    inner_flat = RING_R * math.cos(math.pi / RING_N) - RING_W     # inner edge of the top segment, from the ring centre
    C = V(H.x, 0, H.z + a_h - 0.001 - inner_flat)                  # ring rests on the rod top (1 mm overlap)
    return H, a_h, C


def ring(P, C):
    """pentagonal ring, triangular wire (an edge on the inside), in the YZ plane (hole axis = X); flat top, vertex at the bottom"""
    n = RING_N; rings = []
    for k in range(n):
        th = math.pi / 2 + math.pi / n + TAU * k / n                # flat segment at the top, a vertex at 270 deg
        nrm = V(0, math.cos(th), math.sin(th)); c = C + nrm * RING_R; s = 1 / math.cos(math.pi / n)
        rings.append([c - nrm * (RING_W * s), c + nrm * (0.5 * RING_W * s) + V(0.866 * RING_W, 0, 0),
                      c + nrm * (0.5 * RING_W * s) - V(0.866 * RING_W, 0, 0)])
    P.torus_loft('Ring', rings, IRON)


def rods(P, C):
    top = C - V(0, 0, RING_R)                                       # bottom vertex of the ring (centre-line)
    for i, az in enumerate(ROD_AZ):
        end = pol(az, ROD_END[0], ROD_END[1], (C.x, 0.0))
        straight_rod(P, f'Rod_{i}', top, end, A_THIN, SIDES_ROD, (0, 0, 1))


def ring8(c, a, z, n=8, phase=math.pi / 8 + math.pi / 2):
    """n-gon ring by apothem a, a flat facing -Y (phase: first vertex at -90 + 22.5 deg)"""
    rv = a / math.cos(math.pi / n)
    return [V(c[0] + rv * math.cos(-phase + TAU * k / n + 0.0), c[1] + rv * math.sin(-phase + TAU * k / n), z) for k in range(n)]


def bowl(P, c):
    b = BOWL
    rings = [ring8(c, b['a0'], b['z0']), ring8(c, b['a2'], b['z2']), ring8(c, b['a3'], b['z3'])]   # wall, sloped lip, soil
    P.loft('Bowl', rings, BASKET, BASKET, SOIL)


def ring_pts(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def bridge(P, A, angA, B, angB, slot):
    """triangle strip between two closed rings of different vertex counts (both CCW in the same frame), by angle (PLT-01)"""
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


def leaf_cluster(c, D, seed, H=0.80, widest=0.40, noise=0.012, sub=1, under_k=0.85, up=0.6, down=-0.2):
    """LEAF CLUSTER v2 (PLT-01), ico sub 1 (20 tris) for the small basket: faceted domed drop"""
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
    slots = [LEAF_UP if f.normal.z > up else (LEAF_DN if f.normal.z < down else LEAF) for f in bm.faces]
    return bm, slots


def cup6(P, p, a, spin, slots, depth=0.022, r=0.045, h=0.034, hc=0.016, rc=0.015):
    """6-sided cup bloom, ONE closed shell, 16 tris, O0.09: buried apex -> petal rim -> inner cup -> 3-vertex centre"""
    so, si, sc = slots; a = Vector(a).normalized(); p = Vector(p)
    A = P.bm.verts.new(p - a * depth)
    rp, ra = ring_pts(p + a * h, a, r, 6, spin); R = [P.bm.verts.new(q) for q in rp]
    cp, ca = ring_pts(p + a * hc, a, rc, 3, spin + math.pi / 6); C = [P.bm.verts.new(q) for q in cp]
    f = [P.face([A, R[(k + 1) % 6], R[k]], so) for k in range(6)]
    f += bridge(P, R, ra, C, ca, si)
    f.append(P.face(C, sc))
    return f


# blooms: (drop index, direction azimuth deg, elevation deg, slots (outer, inner, centre))
CUP_PINK, CUP_DEEP, CUP_WHITE = (PINK_L, PINK, YELLOW), (PINK, PINK, YELLOW), (WHITE, WHITE, YELLOW)
BLOOMS = [(0, 235, 78, CUP_WHITE),                                  # crown of the mound (reference: white bloom on top)
          (1, 200, 32, CUP_DEEP), (1, 275, 52, CUP_PINK),            # left side, front-left top
          (2, 295, 30, CUP_PINK), (2, 5, 42, CUP_WHITE),             # front, right
          (0, 40, 50, CUP_DEEP)]                                     # back-right top


def flora(P, c):
    cs = []; trees = []
    for i, az in enumerate(DROP_AZ):
        zc = BOWL['z3'] - DROP_SINK + 0.5 * 0.80 * DROP_D
        cc = pol(az, DROP_R, zc, c); bm, slots = leaf_cluster(cc, DROP_D, 51 + i)
        trees.append(BVHTree.FromBMesh(bm)); cs.append(cc)
        vm = {v: P.bm.verts.new(v.co) for v in bm.verts}
        P.comp.append((f'Drop_{i}', [P.face([vm[v] for v in f.verts], s) for f, s in zip(bm.faces, slots)], False)); bm.free()
    for i, (di, az, el, slots) in enumerate(BLOOMS):
        d = Vector((math.cos(math.radians(el)) * math.cos(math.radians(az)), math.cos(math.radians(el)) * math.sin(math.radians(az)),
                    math.sin(math.radians(el))))
        hit = trees[di].ray_cast(cs[di] + d * DROP_D, -d)[0]
        a = (d + TOWARD * 0.35 + V(0, 0, 0.25)).normalized()
        P.comp.append((f'Bloom_{i}', cup6(P, hit, a, math.radians(az), slots), False))


def feeder(P, c):
    t0, t1, ta = FEED['tray']; b0, b1, ba = FEED['body']
    P.loft('Tray', [ring8(c, ta, t0, phase=math.pi / 8 + math.pi / 2), ring8(c, ta, t1, phase=math.pi / 8 + math.pi / 2)],
           STONE, STONE, STONE)
    # body: 8-sided prism, a flat faces -Y; the -Y (front) and +X facets carry a window with a recess (grain inside)
    lo = ring8(c, ba, b0); hi = ring8(c, ba, b1); bm = P.bm
    L = [bm.verts.new(v) for v in lo]; Hh = [bm.verts.new(v) for v in hi]; fs = []
    fs.append(P.face(list(reversed(L)), BASKET)); fs.append(P.face(list(Hh), BASKET))
    cen = V(c[0], c[1], 0)
    def facet_az(k):
        m = (lo[k] + lo[(k + 1) % 8]) / 2 - cen; return math.degrees(math.atan2(m.y, m.x)) % 360
    wins = [min(range(8), key=lambda k: abs(((facet_az(k) - az + 180) % 360) - 180)) for az in FEED['win_az']]
    for k in range(8):
        if k not in wins: fs.append(P.face([L[k], L[(k + 1) % 8], Hh[(k + 1) % 8], Hh[k]], BASKET))
    w = FEED['win_w'] / 2; z0, z1 = FEED['win_z']; dpt = FEED['win_d']; gi = 0
    for k in wins:                                                   # window: frame on the facet + recess + grain lumps
        A, B, Cc, D = L[k], L[(k + 1) % 8], Hh[(k + 1) % 8], Hh[k]
        m = (A.co + B.co) / 2; u = (B.co - A.co).normalized(); nin = (cen - V(m.x, m.y, 0)).normalized()
        W = [bm.verts.new(V(m.x, m.y, zz) + u * uu) for uu, zz in ((-w, z0), (w, z0), (w, z1), (-w, z1))]
        fs += [P.face([A, B, W[1], W[0]], BASKET), P.face([B, Cc, W[2], W[1]], BASKET),
               P.face([Cc, D, W[3], W[2]], BASKET), P.face([D, A, W[0], W[3]], BASKET)]
        Wb = [bm.verts.new(v.co + nin * dpt) for v in W]
        for j in range(4): fs.append(P.face([W[j], W[(j + 1) % 4], Wb[(j + 1) % 4], Wb[j]], BASKET))
        fs.append(P.face(list(reversed(Wb)), BASKET))
        # grain: 3 squashed octahedra on the recess floor, poking out of the window
        for du, dn, s, hz in ((-0.016, 0.014, 0.020, 0.030), (0.015, 0.016, 0.019, 0.028), (0.0, 0.003, 0.017, 0.024)):
            g = V(m.x, m.y, z0 + hz * 0.45) + u * du + nin * dn
            vs = [bm.verts.new(g + q) for q in (u * s, nin * s, -u * s, -nin * s, V(0, 0, hz * 0.55), V(0, 0, -hz * 0.6))]
            gf = [P.face([vs[j], vs[(j + 1) % 4], vs[4]], YELLOW) for j in range(4)]
            gf += [P.face([vs[(j + 1) % 4], vs[j], vs[5]], YELLOW) for j in range(4)]
            P.comp.append((f'Grain_{gi}', gf, False)); gi += 1
    P.comp.append(('Feeder_Body', fs, False))
    # roof: eave band + 8-sided cone + knob
    r0, r1, rt, ra = FEED['roof']
    E0 = ring8(c, ra, r0); E1 = ring8(c, ra, r1)
    E0v = [bm.verts.new(v) for v in E0]; E1v = [bm.verts.new(v) for v in E1]; apex = bm.verts.new(V(c[0], c[1], rt))
    rf = [P.face(list(reversed(E0v)), SOIL)]
    rf += [P.face([E0v[k], E0v[(k + 1) % 8], E1v[(k + 1) % 8], E1v[k]], SOIL) for k in range(8)]
    rf += [P.face([E1v[k], E1v[(k + 1) % 8], apex], SOIL) for k in range(8)]
    P.comp.append(('Roof', rf, False))
    k0, k1, k2, kr = FEED['knob']; n = 6
    kb = bm.verts.new(V(c[0], c[1], k0)); kt = bm.verts.new(V(c[0], c[1], k2))
    KR = [bm.verts.new(V(c[0] + kr * math.cos(TAU * k / n), c[1] + kr * math.sin(TAU * k / n), k1)) for k in range(n)]
    kf = [P.face([KR[(k + 1) % n], KR[k], kb], SOIL) for k in range(n)] + [P.face([KR[k], KR[(k + 1) % n], kt], SOIL) for k in range(n)]
    P.comp.append(('Knob', kf, False))


def build_hanging(var):
    H, a_h, C = ring_geo()
    P = Part('Hanging')
    ring(P, C); rods(P, C)
    c = (C.x, 0.0)
    if var == VAR: feeder(P, c)
    else: bowl(P, c); flora(P, c)
    return P, H


# ---------------- scene / atlas ----------------
def clear_own():
    sc = bpy.context.scene; cs = []
    for nm in (COLL, COLL_VAR):
        c = bpy.data.collections.get(nm) or bpy.data.collections.new(nm)
        if c.name not in sc.collection.children: sc.collection.children.link(c)
        for o in list(c.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
        cs.append(c)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        keep = set(o for c in cs for o in c.objects)
        for o in list(sc.objects):
            if o not in keep: bpy.data.objects.remove(o, do_unlink=True)
    return cs


def atlas_and_material():
    """reuse the shared atlas F PNG (never rewritten here) and M_Garden_Flora (created only when missing)"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(PAL_F):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), tuple(img.size), 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def world_pts(objs):
    return [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]


def bbox(objs):
    pts = world_pts(objs)
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def merged_bm(objs):
    bm = bmesh.new()
    for o in objs:
        if o.type != 'MESH': continue
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        tm = bpy.data.meshes.new('TMP_ORN05_part'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm)
    return bm


def all_coplanar(objs):
    me = bpy.data.meshes.new('TMP_ORN05_cop'); bm = merged_bm(objs); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_ORN05_cop', me)
    n, s = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def contact(oa, ob):
    """0 when the two parts intersect/touch, else the smallest vertex-to-surface distance"""
    ta = BVHTree.FromBMesh(merged_bm([oa])); tb = BVHTree.FromBMesh(merged_bm([ob]))
    if ta.overlap(tb): return 0.0
    return min(tb.find_nearest(oa.matrix_world @ v.co)[3] for v in oa.data.vertices)


def to_obj(P, oname, coll, mat, root, pivot):
    """pc.to_object (recalc normals, comp_checks print, triangulate, atlas UVs, pivot) with an explicit object name"""
    ob = pc.to_object(P, NAME, coll, mat, pivot, root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    ob.name = oname; ob.data.name = oname
    return ob


def build():
    cs = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('', VAR), cs):
        asset = NAME + suf
        print(f'== {asset}')
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        B, p2 = build_body(); tb = part_tris(B)
        bchk = pc.comp_checks(B, mirror_skip=tuple(nm for nm, _, _ in B.comp))
        body = to_obj(B, asset + '_Body', coll, mat, root, (0, 0, 0))
        Hg, H = build_hanging(suf); th = part_tris(Hg)
        hchk = pc.comp_checks(Hg, mirror_skip=tuple(nm for nm, _, _ in Hg.comp))
        hang = to_obj(Hg, asset + '_Hanging', coll, mat, root, tuple(H))
        bpy.context.view_layer.update()
        tot = pc.report({'Body': body, 'Hanging': hang})
        print('  tris per component: Body', tb, '| Hanging', th)
        print(f'  budget {BUDGET[suf]} ->', 'OK' if tot <= BUDGET[suf] else f'OVER x{tot / BUDGET[suf]:.2f}')
        ncop = all_coplanar([body, hang]); gap = contact(hang, body)
        lo, hi = bbox([body, hang])
        ground = sorted({(round(p.x, 4), round(p.y, 4)) for p in world_pts([body, hang]) if abs(p.z) < 1e-6})
        cells = sorted({cell_of(o.data.uv_layers.active.data[p.loop_start].uv) for o in (body, hang) for p in o.data.polygons})
        print(f'  ring-on-hook contact gap {gap:.5f} (0 = touching) | hanging pivot {[round(x, 4) for x in H]}')
        print(f'  ground points (z = 0): {ground} | min z {lo[2]:.5f} | x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} '
              f'z ..{hi[2]:.3f} | size {hi[0]-lo[0]:.3f} x {hi[1]-lo[1]:.3f} x {hi[2]-lo[2]:.3f}')
        print(f'  atlas cells used {cells}')
        lh, hh = bbox([hang]); print(f'  hanging part z {lh[2]:.3f}..{hh[2]:.3f}, x {lh[0]:.3f}..{hh[0]:.3f}, y {lh[1]:.3f}..{hh[1]:.3f}')
        if not suf:
            print(f'  scroll self-clearance (centre-lines, >= bar {2 * A_THIN:.3f}): {s_clearance(p2):.4f}; '
                  f'u {min(u for u, v in p2) - A_THIN:.3f}..{max(u for u, v in p2) + A_THIN:.3f} v {min(v for u, v in p2) - A_THIN:.3f}..'
                  f'{max(v for u, v in p2) + A_THIN:.3f}')
        ok = (bchk['nonmanifold'] + hchk['nonmanifold'] + bchk['loose'] + hchk['loose'] + bchk['degenerate'] + hchk['degenerate']
              == 0 and not bchk['problems'] and not hchk['problems'] and ncop == 0 and gap == 0.0 and abs(lo[2]) < 1e-6
              and len(ground) == 1 and tot <= BUDGET[suf])
        print(f'SUMMARY {asset}: tris {tot}/{BUDGET[suf]} nonmanifold {bchk["nonmanifold"]}+{hchk["nonmanifold"]} loose '
              f'{bchk["loose"]}+{hchk["loose"]} degenerate {bchk["degenerate"]}+{hchk["degenerate"]} coplanar {ncop} contact problems '
              f'{bchk["problems"] + hchk["problems"]} ring gap {gap:.5f} -> {"ALL OK" if ok else "CHECK FAILED"}')
        res[suf] = dict(coll=coll, root=root, body=body, hang=hang, tot=tot)
    return res, img, mat


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


# ---------------- renders (temporary scene: the open scene and its settings are not touched; from WTR-03/ORN-03) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_ORN05_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_ORN05_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_ORN05_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_ORN05_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_ORN05_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_ORN05_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new('TMP_ORN05_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = world_pts(objs)
    target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)]); dv = Vector(view_dir).normalized()
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


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(asset, coll, root, hang, fbx):
    """the moving part carries the bare spec name `Hanging` inside the FBX (in Blender it is <asset>_Hanging because names
    are unique per file); the owner's selection and active object are restored afterwards"""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    old = hang.name; hang.name = 'Hanging'
    if hang.name != 'Hanging': raise RuntimeError(f'another object is named Hanging: got {hang.name}')
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        hang.name = old
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act
    return fbx


VIEW_REF = (-0.36, -0.88, 0.42)               # reference: from the front, slightly left (footrest rises to the right), ~25 deg
VIEW_PREVIEW = (1.0, -1.25, 0.75)             # series preview 3/4 (front-right, ~30 deg), 70 mm

if MODE == 'verify':
    for suf in ('', VAR): pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    R_, img, mat = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = {suf: [r['root'], r['body'], r['hang']] for suf, r in R_.items()}
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs[''], os.path.join(CHECK_DIR, f'ORN-05_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.62, fill_h=0.9, lens=None)
        render(objs[''], os.path.join(CHECK_DIR, f'ORN-05_34_{tag}.png'), VIEW_PREVIEW)
        render(objs[''], os.path.join(CHECK_DIR, f'ORN-05_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
        render(objs[VAR], os.path.join(CHECK_DIR, f'ORN-05{VAR}_34_{tag}.png'), VIEW_PREVIEW)
        render(objs[VAR], os.path.join(CHECK_DIR, f'ORN-05{VAR}_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbxs = []
        for suf in ('', VAR):
            r = R_[suf]
            fbxs.append(export_one(NAME + suf, r['coll'], r['root'], r['hang'], os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
            save_lib(os.path.join(ART, 'Blend', NAME + suf + '.blend'), r['coll'], mat, img)
        render(objs[''], os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        render(objs[VAR], os.path.join(CHECK_DIR, f'ORN-05{VAR}_check{"_live" if LIVE else ""}.png'), VIEW_PREVIEW)
        for f in fbxs: pc.verify(f)
    if MODE in ('export', 'dump'):
        geom_dump([R_[s][k] for s in ('', VAR) for k in ('body', 'hang')], os.path.join(CHECK_DIR, f'geom_{tag}.json'))
