# build.py - ORN-01 Sundial (FMS_Garden_Sundial, atlas A) and ORN-03 Stone urn on a pedestal (FMS_Garden_Urn + mesh
# variant _Planted, atlas F), pack CottageGardenDecor (Cottage Garden Decor). ONE registry script, shared pedestal profile helper.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- <ORN-01|ORN-03> build|export|verify
#   build  = build + printed checks (topology, coplanar, ground, contacts, tris, footprint) + check renders to
#            %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ .fbm) per model (ORN-03 also _Planted) + collection-only .blend + ONE preview per ID
#            + (ORN-03) headless check render of _Planted + FBX re-import verify + geometry dump (JSON, SHA1 of all meshes)
#   verify = only re-import the FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\ORN-01+ORN-03_Sundial\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['ORN-01', 'build']})
#   Live mode touches only the collection ORN-01_Sundial / ORN-03_Urn (+ child ORN-03_Urn_Planted).
# Axes (Blender): Z up, pivot = centre of the plinth base on the ground (0,0,0); Unity Y up after the FBX axis bake.
# No LOD (catalogue). The shared atlases are READ ONLY here (loaded, palette verified by pixel read, never written).
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
ATLAS = {'A': ('FMS_Garden_AtlasA.png', 'M_Garden_Build', PAL_A), 'F': ('FMS_Garden_AtlasF.png', 'M_Garden_Flora', PAL_F)}
# atlas A slots
A_METAL, A_METAL_D, A_LIME, A_STONE, A_IRON = 7, 8, 11, 12, 13
# atlas F slots
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
PINK, PINK_L, WHITE, YELLOW = 6, 7, 8, 11
SOIL, F_STONE, F_LIME = 12, 14, 15
STEM = LEAF_DN                                # trailing stems green (review lesson: no brown stalks), spec said F13
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'ORN-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi
K8 = math.tan(math.pi / 8)


# ======================= shared: pedestal / lathe profile helper =======================
# A profile is a list of rings bottom -> top (-> inside), each (z, kind, a, b, comp, slot):
#   kind 'sq': axis-aligned square, a = half size, b = corner chamfer of the vertical edges (0 -> 4 corners, else 8 verts)
#   kind 'ng': n-gon, a = vertex radius, b = n (first vertex on +X)
#   comp, slot = component name and palette slot of the band from this ring to the next one.
# Bands between rings of the same kind and count are quads; otherwise a triangle strip zipped by angle (bridge), so the
# whole stack is ONE closed shell: no coplanar faces between stacked blocks, no gaps.
def ring_pts(kind, a, b, z):
    if kind == 'sq':
        pts = [(a, -a), (a, a), (-a, a), (-a, -a)] if b <= 0 else pc.chamf_rect(2 * a, 2 * a, b)
    else:
        pts = pc.ngon(a, b, 0.0)
    return [Vector((x, y, z)) for x, y in pts], [math.atan2(y, x) for x, y in pts]


def bridge(P, A, angA, B, angB, slot):
    """triangle strip between two closed CCW rings of different vertex counts, zipped by angle (PLT-01 / FLB-01)"""
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


def lathe(P, prof, cap0=None, cap1=None):
    """rings of `prof` lofted into one shell; cap0/cap1 = (comp, slot) of the bottom/top cap or None. -> {comp: faces}"""
    R, Ang = [], []
    for z, kind, a, b, _, _ in prof:
        pts, ang = ring_pts(kind, a, b, z); R.append([P.bm.verts.new(p) for p in pts]); Ang.append(ang)
    comp = {}
    for j in range(len(prof) - 1):
        cn, slot = prof[j][4], prof[j][5]
        same = prof[j][1] == prof[j + 1][1] and len(R[j]) == len(R[j + 1])
        if same:
            n = len(R[j])
            fs = [P.face([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]], slot) for k in range(n)]
        else:
            fs = bridge(P, R[j], Ang[j], R[j + 1], Ang[j + 1], slot)
        comp.setdefault(cn, []).extend(fs)
    if cap0: comp.setdefault(cap0[0], []).append(P.face(list(reversed(R[0])), cap0[1]))
    if cap1: comp.setdefault(cap1[0], []).append(P.face(list(R[-1]), cap1[1]))
    return comp


def box_stage(comp, z0, z1, h, side, cv=0.0, bot=None, top=None, chs=None, under=None, topslot=None):
    """square block of a pedestal as profile rings. bot/top = (inset, height) chamfer of the bottom/top horizontal edges;
    chs = slot of the chamfer bands; under/topslot = slot of the ledge below / above it (when it is the wider block)."""
    chs = side if chs is None else chs
    cvi = lambda d: max(cv - K8 * d, 0.4 * cv) if cv else 0.0
    r = []
    if bot: r += [(z0, 'sq', h - bot[0], cvi(bot[0]), comp, chs), (z0 + bot[1], 'sq', h, cv, comp, side)]
    else: r += [(z0, 'sq', h, cv, comp, side)]
    if top: r += [(z1 - top[1], 'sq', h, cv, comp, chs), (z1, 'sq', h - top[0], cvi(top[0]), comp, None)]
    else: r += [(z1, 'sq', h, cv, comp, None)]
    return dict(rings=r, under=side if under is None else under, top=side if topslot is None else topslot, comp=comp)


def ng_stage(comp, pts, n, side):
    """n-gon solid-of-revolution stage: pts [(z, R)] or [(z, R, slot)]"""
    r = [(p[0], 'ng', p[1], n, comp, p[2] if len(p) > 2 else side) for p in pts]
    r[-1] = r[-1][:4] + (comp, None)
    return dict(rings=r, under=side, top=side, comp=comp)


def stack(stages):
    """concatenate stages; the flat ledge between two stages belongs to the wider one (top face of the lower block or
    underside of the upper block). The last ring keeps slot None (closed by a cap)."""
    out = []
    for i, st in enumerate(stages):
        if out:
            lo, up = out[-1], st['rings'][0]
            wide_lo = lo[2] * (1.0 if lo[1] == 'sq' else 0.9) >= up[2] * (1.0 if up[1] == 'sq' else 0.9)
            owner = (stages[i - 1]['comp'], stages[i - 1]['top']) if wide_lo else (st['comp'], st['under'])
            out[-1] = lo[:4] + owner
        out += st['rings']
    return out


# ======================= ORN-01 Sundial (atlas A) =======================
# Measured on references/ORN-01.png (dial O0.45 = 490 px => ~1090 px/m across, ~975 px/m vertical at ~26 deg), see notes.md.
S_PLINTH_H, S_MOULD_H, S_SHAFT_H, S_CAP_H = 0.170, 0.125, 0.090, 0.170
S_Z = dict(plinth=(0.0, 0.100), mould=(0.100, 0.205), shaft=(0.205, 0.605), cap=(0.605, 0.750))
DIAL = [(0.747, 0.198), (0.765, 0.225), (0.788, 0.225), (0.797, 0.210)]   # (z, R) 12-gon, bottom sunk 3 mm in the capital
DIAL_TOP = DIAL[-1][0]
RIB = dict(r0=0.114, r1=0.190, w=0.030, z0=DIAL_TOP - 0.003, z1=DIAL_TOP + 0.014, az0=15.0)   # 12 ribs on the dial flats
GNOMON = dict(t=0.034, y0=-0.010, y1=0.178, top=0.955, cap=0.022, z0=DIAL_TOP - 0.003)       # blade on the +Y axis


def sundial_profile():
    zp, zm, zs, zc = S_Z['plinth'], S_Z['mould'], S_Z['shaft'], S_Z['cap']
    return stack([
        box_stage('Plinth', zp[0], zp[1], S_PLINTH_H, A_STONE, top=(0.022, 0.020)),
        box_stage('Moulding', zm[0], zm[1], S_MOULD_H, A_LIME, top=(0.030, 0.035)),
        box_stage('Shaft', zs[0], zs[1], S_SHAFT_H, A_LIME, cv=0.012),
        box_stage('Capital', zc[0], zc[1], S_CAP_H, A_LIME, bot=(0.062, 0.080)),
    ])


def rib(P, az):
    a = math.radians(az); u = Vector((math.cos(a), math.sin(a), 0)); t = Vector((-math.sin(a), math.cos(a), 0))
    V = [P.bm.verts.new(u * r + t * s + Vector((0, 0, z)))
         for z in (RIB['z0'], RIB['z1']) for (r, s) in ((RIB['r0'], -RIB['w'] / 2), (RIB['r1'], -RIB['w'] / 2),
                                                        (RIB['r1'], RIB['w'] / 2), (RIB['r0'], RIB['w'] / 2))]
    f = [P.face([V[3], V[2], V[1], V[0]], A_METAL_D), P.face([V[4], V[5], V[6], V[7]], A_METAL_D)]
    for k in range(4): f.append(P.face([V[k], V[(k + 1) % 4], V[4 + (k + 1) % 4], V[4 + k]], A_METAL_D))
    return f


def gnomon(P):
    """triangular blade (reference): low tip at the dial centre, tall vertical edge towards the rim on +Y, small flat top"""
    g = GNOMON; prof = [(g['y0'], g['z0']), (g['y1'], g['z0']), (g['y1'], g['top']), (g['y1'] - g['cap'], g['top'])]
    L = [P.bm.verts.new((-g['t'] / 2, y, z)) for y, z in prof]; Rr = [P.bm.verts.new((g['t'] / 2, y, z)) for y, z in prof]
    f = [P.face(list(reversed(L)), A_IRON), P.face(Rr, A_IRON)]
    for k in range(4): f.append(P.face([L[k], L[(k + 1) % 4], Rr[(k + 1) % 4], Rr[k]], A_IRON))
    return f


def gen_sundial(P):
    comp = lathe(P, sundial_profile(), cap0=('Plinth', A_STONE), cap1=('Capital', A_LIME))
    for cn in ('Plinth', 'Moulding', 'Shaft', 'Capital'): P.comp.append((cn, comp[cn], cn == 'Plinth'))
    prof = [(z, 'ng', r, 12, 'Dial', A_METAL) for z, r in DIAL]
    prof[0] = prof[0][:4] + ('Dial', A_METAL_D)                     # chamfered underside a shade darker
    d = lathe(P, prof, cap0=('Dial', A_METAL_D), cap1=('Dial', A_METAL)); P.comp.append(('Dial', d['Dial'], False))
    for k in range(12): P.comp.append((f'Rib_{k:02d}', rib(P, RIB['az0'] + 30 * k), False))
    P.comp.append(('Gnomon', gnomon(P), False))


# ======================= ORN-03 Urn (atlas F) =======================
# Measured on references/ORN-03.png (lip O0.60 = 467 px => ~780 px/m across, ~22 deg elevation), see notes.md.
U_Z = dict(plinth=(0.0, 0.085), shaft=(0.085, 0.565), cap=(0.565, 0.635))
U_PLINTH_H, U_SHAFT_H, U_CAP_H = 0.220, 0.150, 0.185
URN = [  # (z, vertex radius) 12-gon, outer profile from the foot to the lip top, then the inner wall down to the soil
    (0.635, 0.135), (0.652, 0.135),                 # foot base band
    (0.700, 0.078), (0.745, 0.066),                 # foot trumpet -> stem
    (0.770, 0.080), (0.815, 0.175),                 # stem -> belly underside
    (0.870, 0.250), (0.930, 0.272),                 # belly (max)
    (0.985, 0.258), (1.040, 0.222),                 # shoulder -> neck
    (1.065, 0.222), (1.115, 0.300),                 # neck -> lip flare
    (1.200, 0.300),                                 # lip vertical band (sharp top edge, reference)
    (1.200, 0.238, F_STONE),                        # flat lip top ring -> inner wall (stone F14)
]
SOIL_Z, SOIL_R = 1.150, 0.222
LIP_TOP = 1.200


def urn_profile():
    zp, zs, zc = U_Z['plinth'], U_Z['shaft'], U_Z['cap']
    urn = ng_stage('Urn', URN + [(SOIL_Z, SOIL_R)], 12, F_LIME)
    return stack([
        box_stage('Plinth', zp[0], zp[1], U_PLINTH_H, F_STONE, top=(0.012, 0.012)),
        box_stage('Shaft', zs[0], zs[1], U_SHAFT_H, F_LIME, cv=0.010),
        box_stage('Cap', zc[0], zc[1], U_CAP_H, F_STONE, top=(0.012, 0.012)),     # sharp underside (reference)
        urn,
    ])


def gen_urn(P):
    comp = lathe(P, urn_profile(), cap0=('Plinth', F_STONE), cap1=('Soil', SOIL))
    for cn in ('Plinth', 'Shaft', 'Cap', 'Urn', 'Soil'): P.comp.append((cn, comp[cn], cn == 'Plinth'))


# ---------------- _Planted: helpers copied from PLT-01 / FLB-01 build.py (approved generators) ----------------
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def leaf_cluster(c, D, seed, H=0.80, widest=0.40, noise=0.035, sub=2, under_k=0.85, up=0.6, down=-0.2):
    """LEAF CLUSTER v2 (PLT-01): faceted domed foliage drop from a full ico sphere (sub 2 = 80 tris)"""
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


def petal_rim(p, a, r, h, spin, notch_r=0.90, notch_dz=0.014):
    rp, ra = ring(p + a * h, a, r, 8, spin); O = p + a * h
    return [O + (q - O) * (1.0 if k % 2 == 0 else notch_r) - (a * (0.0 if k % 2 == 0 else notch_dz))
            for k, q in enumerate(rp)], ra


def cup_bloom(P, p, a, spin, slots, depth=0.03, r=0.05, h=0.045, hc=0.022, rc=0.016):
    """8-sided cup bloom (FLB-01), ONE closed shell, 22 tris, O0.10: buried apex -> petal rim -> inner cup -> centre"""
    so, si, sc = slots; a = Vector(a).normalized(); p = Vector(p)
    A = P.bm.verts.new(p - a * depth)
    rp, ra = petal_rim(p, a, r, h, spin)
    R = [P.bm.verts.new(q) for q in rp]
    cp, ca = ring(p + a * hc, a, rc, 4, spin + math.pi / 8)
    C = [P.bm.verts.new(q) for q in cp]
    f = [P.face([A, R[(k + 1) % 8], R[k]], so) for k in range(8)]
    f += bridge(P, R, ra, C, ca, si)
    f.append(P.face(C, sc))
    return f


def rod(P, pts, r=0.015, n=8, slot=STEM):
    """8-sided rod along a polyline (mitre-like rings on the bisectors), both ends capped: (len-1)*2n + 2(n-2) tris"""
    pts = [Vector(p) for p in pts]; rings = []
    ref = Vector((0, 0, 1))
    for i, p in enumerate(pts):
        if i == 0: d = pts[1] - p
        elif i == len(pts) - 1: d = p - pts[i - 1]
        else: d = (p - pts[i - 1]).normalized() + (pts[i + 1] - p).normalized()
        rings.append([P.bm.verts.new(q) for q in ring(p, d, r, n, 0.0, ref=(0.0, 0.0, 1.0) if abs(d.normalized().z) < 0.9 else (1, 0, 0))[0]])
    f = []
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        f += [P.face([A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]], slot) for k in range(n)]
    f += [P.face(list(reversed(rings[0])), slot), P.face(list(rings[-1]), slot)]
    return f


# planting layout (_Planted). az = azimuth from +X (deg); preview camera sits at az -51 (front-right)
TOWARD = Vector((0.62, -0.78, 0.0)).normalized()
DROPS = [  # (az, r, D, z_bottom, seed): mound of faceted domed drops in the urn opening, bottoms sunk in the soil
    (-45.0, 0.100, 0.31, SOIL_Z - 0.030, 41), (75.0, 0.100, 0.31, SOIL_Z - 0.030, 42), (195.0, 0.100, 0.31, SOIL_Z - 0.030, 43),
]
LEAF_D = 0.095                    # small leaf drops (ico sub 1 = 20 tris) along the hanging stems
STEMS = [  # (az, z_end, bloom slots, bloom on the arc?, leaf drops at t along the hanging part) trailing stems over the lip
    (-50.0, 0.900, (PINK_L, PINK, YELLOW), True, (0.30, 0.66)), (-39.0, 0.990, (WHITE, WHITE, YELLOW), False, (0.30, 0.66)),
    (-130.0, 0.930, (PINK, PINK, YELLOW), True, (0.30, 0.66)), (-141.0, 1.000, (WHITE, WHITE, YELLOW), False, (0.30, 0.66)),
    (40.0, 0.950, (PINK_L, PINK, YELLOW), False, (0.45,)), (130.0, 0.960, (WHITE, WHITE, YELLOW), False, ()),
]
CUP_PINK, CUP_WHITE, CUP_DEEP = (PINK_L, PINK, YELLOW), (WHITE, WHITE, YELLOW), (PINK, PINK, YELLOW)


def pol(az, r, z):
    a = math.radians(az); return Vector((r * math.cos(a), r * math.sin(a), z))


def stem_path(az, z_end):
    """2 segments: from inside the foliage mound over the lip edge, then hanging down past the belly"""
    return [pol(az, 0.205, LIP_TOP + 0.022), pol(az, 0.318, LIP_TOP + 0.026), pol(az, 0.288, z_end)]


def plan_planting():
    drops, prims = [], []
    for i, (az, r, D, zb, seed) in enumerate(DROPS):
        c = pol(az, r, zb + 0.5 * 0.80 * D)
        bm, slots = leaf_cluster(c, D, seed, H=0.80, noise=0.025); bm.verts.index_update()
        drops.append((f'Drop_{i}', [v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces], slots))
        bm.free()
    for i, (az, z_end, cup, on_arc, leaves) in enumerate(STEMS):
        path = stem_path(az, z_end); prims.append((f'Stem_{i}', 'rod', (path,)))
        out = pol(az, 1.0, 0.0); side = pol(az + 90.0, 1.0, 0.0)
        a = (out * 0.85 + TOWARD * 0.35 + Vector((0, 0, -0.10))).normalized()
        prims.append((f'Bloom_{i}E', 'cup', (path[-1] + a * 0.008, a, math.radians(9 * i), cup)))
        if on_arc:
            p = path[0].lerp(path[1], 0.62); a2 = (out * 0.5 + TOWARD * 0.4 + Vector((0, 0, 0.8))).normalized()
            prims.append((f'Bloom_{i}A', 'cup', (p + a2 * 0.008, a2, math.radians(20 + 9 * i), CUP_DEEP if cup != CUP_DEEP else CUP_WHITE)))
        for k, t in enumerate(leaves):
            c = path[1].lerp(path[2], t) + side * (0.020 * (1.0 if k % 2 == 0 else -1.0))
            bm, slots = leaf_cluster(c, LEAF_D, 100 + 10 * i + k, H=0.75, noise=0.010, sub=1); bm.verts.index_update()
            drops.append((f'Drop_L{i}{k}', [v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces], slots))
            bm.free()
    return drops, prims


def emit_planting(P, drops, prims):
    for nm, vs, fs, slots in drops:
        V = [P.bm.verts.new(v) for v in vs]
        P.comp.append((nm, [P.face([V[i] for i in f], s) for f, s in zip(fs, slots)], False))
    for nm, kind, args in prims:
        P.comp.append((nm, rod(P, *args) if kind == 'rod' else cup_bloom(P, *args), False))


# ======================= registry =======================
REG = {
    'ORN-01': dict(name='FMS_Garden_Sundial', coll='ORN-01_Sundial', preview='FMS_Garden_ORN_01_Preview.png', atlas='A',
                   budget=400, gen=gen_sundial, footprint=0.45, view_ref=(0.609, -0.793, 0.488)),
    'ORN-03': dict(name='FMS_Garden_Urn', coll='ORN-03_Urn', preview='FMS_Garden_ORN_03_Preview.png', atlas='F',
                   budget=700, gen=gen_urn, footprint=0.60, view_ref=(0.695, -0.719, 0.404),
                   var='_Planted', budget_var=1300),
}
CFG = REG[ID]
NAME = CFG['name']
COLL = CFG['coll'] if LIVE else NAME
VAR = CFG.get('var')
COLL_VAR = (COLL + VAR) if VAR else None
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)
VIEW_PREVIEW = (1.0, -1.25, 0.75)                # series preview 3/4 (front-right, ~30 deg), 70 mm


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def to_obj(P, oname, coll, mat, root):
    """pc.to_object without the per-part comp_checks (checks run on the whole model, see build())"""
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = pc.cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    me = bpy.data.meshes.new(oname); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(oname, me); coll.objects.link(ob); ob.parent = root
    return ob


def clear_own():
    sc = bpy.context.scene
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    cs = [coll]
    if VAR:
        cv = bpy.data.collections.get(COLL_VAR) or bpy.data.collections.new(COLL_VAR); cs.append(cv)
    if LIVE:                                   # live: variant nested in the item collection
        if coll.name not in sc.collection.children: sc.collection.children.link(coll)
        if VAR and cv.name not in coll.children: coll.children.link(cv)
    else:
        for c in cs:
            if c.name not in sc.collection.children: sc.collection.children.link(c)
    for c in cs:
        for o in list(c.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:        # factory-startup scene: drop the default cube/light/camera
        keep = set(o for c in cs for o in c.objects)
        for o in list(sc.objects):
            if o not in keep: bpy.data.objects.remove(o, do_unlink=True)
    return cs


def atlas_and_material():
    """reuse the shared atlas PNG (never rewritten here) and its material (created only when missing)"""
    tex, mname, pal = ATLAS[CFG['atlas']]
    img = bpy.data.images.get(tex)
    if img is None: img = bpy.data.images.load(os.path.join(ART, 'Textures', tex), check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(pal):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), tuple(img.size), 'palette mismatches', bad)
    mat = bpy.data.materials.get(mname)
    if mat is None:
        mat = pc.material(mname, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


# ---------------- checks ----------------
def world_pts(objs):
    return [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]


def bbox(objs):
    pts = world_pts(objs)
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def all_coplanar(objs):
    """coplanar overlapping face pairs on all parts merged (also catches overlaps between part objects)"""
    me = bpy.data.meshes.new('TMP_ORN_cop'); bm = bmesh.new()
    for o in objs:
        if o.type != 'MESH': continue
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        tm = bpy.data.meshes.new('TMP_ORN_part'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_ORN_cop', me)
    n, s = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def whole_checks(label, gen):
    P = Part(label); gen(P); pt = part_tris(P)
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    c = pc.comp_checks(P, mirror_skip=tuple(n for n, _, _ in P.comp if n.startswith(('Gnomon', 'Drop', 'Stem', 'Bloom'))))
    P.bm.free()
    return c, pt


def footprint(label, objs, fp):
    lo, hi = bbox(objs); h = fp / 2
    ok = max(abs(lo[0]), abs(hi[0]), abs(lo[1]), abs(hi[1])) <= h + 1e-4 and abs(lo[2]) <= 1e-6
    print(f'  {label}: x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f} | footprint '
          f'{fp:.2f} x {fp:.2f}, on ground -> {"OK" if ok else "FAIL"}')
    return ok


def build():
    cs = clear_own(); coll = cs[0]
    img, mat = atlas_and_material()
    gen = CFG['gen']
    print(f'CHECK {ID} base:'); cb, pt = whole_checks('Base', gen)
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = Part('Body'); gen(P); ob = to_obj(P, NAME + '_Body', coll, mat, root)
    res = dict(coll=coll, root=root, obs=[ob], img=img, mat=mat)
    bpy.context.view_layer.update()
    print('REPORT base:'); tot = pc.report({'Body': ob})
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'x{tot / CFG["budget"]:.2f}', '| parts', pt)
    ncop = all_coplanar([ob]); fok = footprint('base', [ob], CFG['footprint'])
    print(f'SUMMARY {ID} base: tris {tot}/{CFG["budget"]} nonmanifold {cb["nonmanifold"]} loose {cb["loose"]} '
          f'degenerate {cb["degenerate"]} coplanar {ncop} contact problems {cb["problems"]} footprint {"OK" if fok else "FAIL"}')
    if VAR:
        cv = cs[1]; drops, prims = plan_planting()
        gen_v = lambda Q: (gen(Q), emit_planting(Q, drops, prims))
        print(f'CHECK {ID} {VAR}:'); cvv, ptv = whole_checks('Planted', gen_v)
        vroot = bpy.data.objects.new(NAME + VAR, None); cv.objects.link(vroot)
        P = Part('Body'); gen(P); vb = to_obj(P, NAME + VAR + '_Body', cv, mat, vroot)
        P = Part('Plants'); emit_planting(P, drops, prims); vp = to_obj(P, NAME + VAR + '_Plants', cv, mat, vroot)
        bpy.context.view_layer.update()
        print(f'REPORT {VAR}:'); totv = pc.report({'Body': vb, 'Plants': vp})
        print(f'  budget {CFG["budget_var"]} ->', 'OK' if totv <= CFG['budget_var'] else f'x{totv / CFG["budget_var"]:.2f}', '| parts', ptv)
        ncv = all_coplanar([vb, vp]); fov = footprint(VAR, [vb, vp], CFG['footprint'])
        lo, hi = bbox([vp])
        print(f'  plants: lowest {lo[2]:.3f} (pedestal cap top {U_Z["cap"][1]:.3f}) top {hi[2]:.3f}')
        print(f'SUMMARY {ID} {VAR}: tris {totv}/{CFG["budget_var"]} nonmanifold {cvv["nonmanifold"]} loose {cvv["loose"]} '
              f'degenerate {cvv["degenerate"]} coplanar {ncv} contact problems {cvv["problems"]} footprint {"OK" if fov else "FAIL"}')
        res.update(cv=cv, vroot=vroot, vobs=[vb, vp])
    return res


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


# ---------------- renders (temporary scene: the open scene and its settings are not touched; copied from FLB-01) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_ORN_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_ORN_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_ORN_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_ORN_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_ORN_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_ORN_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0                   # lens=None: orthographic (reference sheet comparison)
    cam = bpy.data.objects.new('TMP_ORN_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = world_pts(objs)
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


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_keep_selection(name, coll, root, fbx):
    """pc.export changes the selection: restore the owner's selection and active object afterwards (live)"""
    vl = bpy.context.view_layer
    sel = [o for o in vl.objects if o.select_get()]; act = vl.objects.active
    try:
        return pc.export(name, coll, root, fbx)
    finally:
        for o in vl.objects: o.select_set(o in sel)
        vl.objects.active = act


if MODE == 'verify':
    for suf in ('',) + ((VAR,) if VAR else ()): pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    R_ = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    base_objs = [R_['root']] + R_['obs']
    var_objs = ([R_['vroot']] + R_['vobs']) if VAR else None
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), CFG['view_ref'], res=(1254, 1254), fill_w=0.9, fill_h=0.9, lens=None)
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_34_{tag}.png'), VIEW_PREVIEW)
        render(base_objs, os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
        if VAR:
            render(var_objs, os.path.join(CHECK_DIR, f'{ID}{VAR}_34_{tag}.png'), VIEW_PREVIEW)
            render(var_objs, os.path.join(CHECK_DIR, f'{ID}{VAR}_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.88, fill_h=0.88)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_keep_selection(NAME, R_['coll'], R_['root'], os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), R_['coll'], R_['mat'], R_['img'])
        render(base_objs, os.path.join(ART, 'Previews', CFG['preview']), VIEW_PREVIEW)
        if VAR:
            fbx_v = export_keep_selection(NAME + VAR, R_['cv'], R_['vroot'], os.path.join(ART, 'Meshes', NAME + VAR + '.fbx'))
            save_lib(os.path.join(ART, 'Blend', NAME + VAR + '.blend'), R_['cv'], R_['mat'], R_['img'])
            render(var_objs, os.path.join(CHECK_DIR, f'{ID}{VAR}_check.png'), VIEW_PREVIEW)
        pc.verify(fbx)
        if VAR: pc.verify(fbx_v)
    if MODE in ('export', 'dump'):
        geom_dump(R_['obs'] + (R_['vobs'] if VAR else []), os.path.join(CHECK_DIR, f'geom_{tag}.json'))
