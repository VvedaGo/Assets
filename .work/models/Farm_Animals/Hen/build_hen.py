# build_hen.py - BRD-01 Hen (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_hen.py -- BRD-01 build|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_hen)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Hen'
TAG = 'FarmAnimals_Hen'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-01.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_hen')
REF_VIEW = (0.766, -0.643, 0.17)     # reference: front-left three-quarter, yaw ~40 deg from the side, ~10 deg above
PALETTE = ['#C2582A', '#9C4422', '#D2683A', '#8A3826',
           '#6B2A1B', '#CA5F2F', '#9A4322', '#E3262E',
           '#B91D25', '#F6BE2C', '#E09A1A', '#F5BF2B',
           '#D99420', '#2A1D17', '#F2E6C9', '#6E9F4A']
(BODY, BODY_D, BODY_L, WING, WING_D, TAIL, TAIL_D, COMB, COMB_D, BEAK, BEAK_D, LEG, LEG_D, EYE) = range(14)
BUDGET = 900

# joints = part pivots (shifted with the mesh so the root sits under the centre of mass)
JOINTS = {
    'Body': (0, 0.0, 0.16), 'Neck1': (0, -0.080, 0.215), 'Neck2': (0, -0.093, 0.272), 'Head': (0, -0.096, 0.318),
    'Beak_Lower': (0, -0.128, 0.305), 'Comb': (0, -0.090, 0.350), 'Wattle': (0, -0.127, 0.297),
    'WingUpper.L': (0.085, -0.095, 0.205), 'WingLower.L': (0.088, -0.080, 0.165), 'WingTip.L': (0.080, 0.050, 0.180),
    'TailFan1': (0, 0.095, 0.190), 'TailFan2': (0, 0.135, 0.205),
    'LegUpper.L': (0.052, -0.010, 0.125), 'LegLower.L': (0.052, -0.010, 0.064), 'Foot.L': (0.052, -0.010, 0.020),
}
LEG_X, LEG_Y = 0.052, -0.010

# body rings (front-bottom y, z, back-top y, z, half width), breast -> rear. The front rings are tilted: the breast curves up
# into the neck as one continuous surface and the front cap lies inside Neck1 (no visible cap or pole).
BODY_RINGS = [(-0.145, 0.214, -0.120, 0.240, 0.022), (-0.160, 0.160, -0.114, 0.242, 0.075),
              (-0.148, 0.102, -0.100, 0.250, 0.092), (-0.118, 0.072, -0.092, 0.256, 0.100),
              (-0.062, 0.062, -0.062, 0.256, 0.104), (0.008, 0.066, 0.008, 0.255, 0.102),
              (0.065, 0.085, 0.065, 0.253, 0.090), (0.103, 0.112, 0.103, 0.251, 0.071), (0.128, 0.141, 0.128, 0.243, 0.046)]
# neck rings, horizontal (z, y centre, half x, half front, half back)
NECK1 = [(0.160, -0.080, 0.084, 0.052, 0.080), (0.200, -0.082, 0.080, 0.064, 0.072), (0.240, -0.084, 0.066, 0.059, 0.060),
         (0.272, -0.086, 0.048, 0.050, 0.045)]
NECK2 = [(0.250, -0.086, 0.054, 0.049, 0.049), (0.292, -0.090, 0.048, 0.050, 0.050), (0.340, -0.093, 0.036, 0.040, 0.034)]
# head rings along -Y (y, half width, z bottom, z top)
HEAD_RINGS = [(-0.048, 0.022, 0.302, 0.342), (-0.058, 0.037, 0.288, 0.356), (-0.080, 0.044, 0.283, 0.364),
              (-0.106, 0.043, 0.284, 0.364), (-0.127, 0.036, 0.289, 0.352), (-0.143, 0.024, 0.295, 0.337)]
# upper beak (y, half width, mouth z, top z); lower beak (y, half width, depth below the mouth)
BEAK_UP = [(-0.128, 0.024, 0.306, 0.336), (-0.152, 0.019, 0.304, 0.327), (-0.174, 0.012, 0.302, 0.317), (-0.197, 0.004, 0.300, 0.304)]
BEAK_LO = [(-0.126, 0.0205, 0.017), (-0.152, 0.016, 0.013), (-0.181, 0.004, 0.003)]
# comb outline in the (y, z) plane: front-bottom, up over 4 lobes, back, then along the sunk base
COMB_OUT = [(-0.139, 0.322), (-0.152, 0.354), (-0.134, 0.391), (-0.112, 0.377), (-0.089, 0.403), (-0.069, 0.386),
            (-0.049, 0.400), (-0.034, 0.377), (-0.016, 0.380), (-0.019, 0.357), (-0.050, 0.336), (-0.080, 0.350),
            (-0.118, 0.346)]
COMB_C, COMB_T, COMB_SHRINK = Vector((-0.085, 0.345)), 0.011, 0.80
# wing tiers along y: (y, z centre, half height, proud)
# one folded-wing outline shared by all three wing parts: (y, z top, z bottom, max proud); parts follow one surface
WING_OUT = [(-0.112, 0.212, 0.190, 0.010), (-0.098, 0.228, 0.150, 0.024), (-0.075, 0.236, 0.124, 0.030), (-0.030, 0.238, 0.115, 0.032),
            (0.030, 0.236, 0.118, 0.032), (0.075, 0.226, 0.138, 0.026), (0.100, 0.214, 0.160, 0.020), (0.126, 0.192, 0.180, 0.008)]
WING_SPLIT, WING_LIP = 0.55, 0.0015          # upper band t 0..0.55 (overlaps the lower band by a 1.5 mm lip), lower band 0.45..1
WING_UP_Y, WING_LO_Y, WING_TIP_Y = (-0.112, -0.098, -0.060, 0.020, 0.088), (-0.098, -0.060, 0.020, 0.080), (0.050, 0.098, 0.126)
# tail feathers: (angle from +Y towards +Z deg, length from the fan root)
FAN_ROOT = Vector((0, 0.112, 0.200))
FEATHERS = [(110, 0.112), (87, 0.130), (66, 0.146), (46, 0.160), (27, 0.162), (9, 0.146)]


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-01', 'build'])[:2]


# ---------------- ring helpers (copied from the cow) ----------------
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
EYE_R, EYE_PROUD = 0.0095, 0.004


def cone(P, ring, apex, slot):
    """closed pyramid: flat n-gon disc + triangles to a buried apex; returns its faces"""
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Hen')
    # body: faceted egg, 10 sides; the front tip is tilted up and buried in the Neck1 base (round breast, no visible pole)
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 10) for fy, fz, by, bz, w in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    # neck: two thick 8-sided horizontal-ring lofts; Neck1 tapers into Neck2, Neck2 runs flush into the back of the head
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK1], BODY, BODY, BODY)
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK2], BODY, BODY, BODY)
    # head + upper beak (triangle section, flat mouth line)
    P.loft('Head', [ring_y(y, w, zb, zt, 10, 2.3, 2.1) for y, w, zb, zt in HEAD_RINGS], BODY, BODY, BODY)
    head_faces = list(P.comp[-1][1])
    P.loft('Head', [[V(0, y, zt), V(-w, y, zm), V(w, y, zm)] for y, w, zm, zt in BEAK_UP], BEAK, BEAK, BEAK)
    zm_at = lambda y: 0.306 + (y + 0.126) * (0.006 / 0.068)
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.001), V(-w, y, zm_at(y) - 0.001), V(0, y, zm_at(y) - d)] for y, w, d in BEAK_LO],
           BEAK_D, BEAK_D, BEAK_D)
    # comb: outline at x=0 (ridge), shrunk outline at x=+-T (flat sides)
    out = [Vector(p) for p in COMB_OUT]
    sh = [COMB_C + (p - COMB_C) * COMB_SHRINK for p in out]
    rings = [[V(-COMB_T, p.x, p.y) for p in sh], [V(0, p.x, p.y) for p in out], [V(COMB_T, p.x, p.y) for p in sh]]
    P.loft('Comb', rings, COMB, COMB, COMB)
    # wattle: two drops under the beak base
    wl = []
    for z, y, hy, hx in [(0.302, -0.135, 0.011, 0.007), (0.268, -0.143, 0.018, 0.0095), (0.240, -0.140, 0.006, 0.0045)]:
        wl.append(ring_frame(V(0.012, y, z), V(0, -1, 0), V(1, 0, 0), hy, hx, hx, 5, 2.0))
    P.loft('Wattle', wl, COMB, COMB, COMB); P.loft('Wattle', mir(wl), COMB, COMB, COMB)

    # BVH helpers for surface placement
    def bvh_of(faces):
        vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])
    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: raise RuntimeError(f'no surface hit at y {y} z {z}')
        return hit[0].x, hit[1]
    # eyes: 8-gon dark discs, EYE_PROUD proud, backed by a pyramid buried in the head (14 tris each)
    hp, n = side_x(bvh_head, -0.112, 0.322); hp = V(hp, -0.112, 0.322)
    n = (n + V(0, -0.35, 0.05)).normalized()
    t_, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); apex = hp - n * 0.008
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # wings: one outline + one outer surface (body side + proud * g(t)); the three parts are bands of it
    def outline(y):
        for (y0, *a), (y1, *b) in zip(WING_OUT, WING_OUT[1:]):
            if y0 <= y <= y1:
                k = (y - y0) / (y1 - y0); return [u + (v - u) * k for u, v in zip(a, b)]
        raise RuntimeError(f'wing y {y} outside outline')
    G = [(0.0, -0.10), (0.25, 0.75), (0.45, 0.95), (0.55, 1.0), (0.75, 1.0), (1.0, 0.85)]
    def g(t):
        for (t0, a), (t1, b) in zip(G, G[1:]):
            if t0 <= t <= t1: return a + (b - a) * (t - t0) / (t1 - t0)
    def surf_pt(y, t, off=0.0):
        zt, zb, pr = outline(y); z = zt + (zb - zt) * t; xs, _ = side_x(bvh_body, y, z)
        return V(xs + pr * g(t) + off, y, z)
    def inner(y, t):
        zt, zb, pr = outline(y); z = zt + (zb - zt) * t; xs, _ = side_x(bvh_body, y, z); return V(xs - 0.012, y, z)
    def under(y, t, d):
        p = surf_pt(y, t); return V(p.x - d, y, p.z + 0.003)
    up = [[surf_pt(y, 0.0, -0.003), surf_pt(y, 0.25), surf_pt(y, WING_SPLIT, WING_LIP), under(y, WING_SPLIT, 0.005), inner(y, 0.3)]
          for y in WING_UP_Y]
    lo = [[surf_pt(y, 0.45, -0.003), surf_pt(y, 0.75), surf_pt(y, 1.0), under(y, 1.0, 0.012), inner(y, 0.75)] for y in WING_LO_Y]
    tip = [[surf_pt(y, 0.05, -0.003), surf_pt(y, 0.35, o), surf_pt(y, 0.75, o), under(y, 0.95, 0.010), inner(y, 0.5)]
           for y, o in zip(WING_TIP_Y, (-0.003, 0.0, 0.0))]
    for nm, r, slot in (('WingUpper', up, WING), ('WingLower', lo, WING_D), ('WingTip', tip, WING)):
        P.loft(nm + '.L', r, slot, slot, slot); P.loft(nm + '.R', mir(r), slot, slot, slot)

    # tail: rump wedge (TailFan1) + 6 diamond-section feathers (TailFan2) rooted inside it
    a0, a1 = V(0, 0.080, 0.190), V(0, 0.140, 0.224)
    d = (a1 - a0).normalized(); up = V(1, 0, 0).cross(d).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.050, 0.042), (1.0, 0.032, 0.028)]], BODY, BODY, BODY)
    for i, (ang, L) in enumerate(FEATHERS):
        a = math.radians(ang); dv = V(0, math.cos(a), math.sin(a)); ew = V(0, -math.sin(a), math.cos(a))
        tk = 1.25 if i % 2 else 1.0                       # alternate thickness -> layered fan, still X-symmetric
        fr = []
        for s, w, t in [(0.0, 0.014, 0.006), (0.72, 0.0215, 0.008), (1.0, 0.0165, 0.006)]:
            c = FAN_ROOT + dv * (L * s)
            fr.append([c + ew * w, c + V(t * tk, 0, 0), c - ew * w, c - V(t * tk, 0, 0)])
        P.loft('TailFan2', fr, TAIL, TAIL, TAIL)

    # legs: feathered thigh cuff, thick 6-gon shank, ankle pad + 4 toes
    X, Y = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.135, 0.028), (0.070, 0.0175)]],
               BODY_D, BODY_D, BODY_D)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.080, 0.0150), (0.005, 0.0120)]],
               LEG, LEG, LEG)
        P.loft('Foot' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.0, 0.0125), (0.018, 0.0100)]],
               LEG, LEG, LEG, ground=True)
        base = c(0.0)
        for yaw, L in [(0, 0.066), (34, 0.058), (-34, 0.058), (180 - 15, 0.032)]:
            a = math.radians(yaw); dv = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            r0 = base + dv * 0.006; r1 = base + dv * L
            toe = [[r0 + sd * 0.0085 + V(0, 0, 0.003), r0 - sd * 0.0085 + V(0, 0, 0.003), r0 - sd * 0.006 + V(0, 0, 0.018),
                    r0 + sd * 0.006 + V(0, 0, 0.018)],
                   [r1 + sd * 0.0055, r1 - sd * 0.0055, r1 - sd * 0.0035 + V(0, 0, 0.009), r1 + sd * 0.0035 + V(0, 0, 0.009)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, body_faces


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
    P, _ = build_mesh()
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
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    # coplanar check on the whole model (all parts in one temp mesh)
    me = bpy.data.meshes.new('TMP_HenAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_HenAll', me)
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


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 768, 512)
    g = rn.ground(sc); cam = rn.camera(sc)
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in (REF_VIEW, (1, 0, 0.06), (0.02, -1, 0.12), (-0.8, 0.9, 0.45), (0.25, 0.15, 1.0)):
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Hen_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Hen_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-01 Hen', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Hen_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
    elif CMD == 'debug':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        sc = B['sc']; rn.setup_workbench(sc, 640, 640); sc.display.shading.color_type = 'RANDOM'; cam = rn.camera(sc)
        pts = [p for p in rn.mesh_points([B['obs'][k] for k in ('Neck1', 'Neck2', 'Body', 'Head')]) if p.y < -0.04 and 0.12 < p.z]
        rn.fit(sc, cam, pts, REF_VIEW, (0.8, 0.8)); rn.render_to(sc, os.path.join(CHECK, 'Hen_debug.png'))
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'), view=(1.0, -0.80, 0.16),
                   fill=(0.60, 0.80))
