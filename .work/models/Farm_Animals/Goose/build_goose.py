# build_goose.py - BRD-05 Goose (Farm Animals, skeleton B parts, MESH ONLY: no armature/weights/clips). Headless Blender 5.2:
#   PYTHONUTF8=1 blender --background --factory-startup --python build_goose.py -- BRD-05 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_goose)
# look  : build + EEVEE look at the reference angle (TEMP)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure follows ../Hen/build_hen.py and ../Rooster/build_rooster.py (helpers copied, shared modules imported read-only).
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Goose'
TAG = 'FarmAnimals_Goose'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-05.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_goose')
REF_VIEW = (0.70, -0.75, 0.18)       # reference: front-left three-quarter, ~45 deg from the front, ~10 deg above
PALETTE = ['#E3DCD0', '#CEC5B7', '#EAE4DA', '#D6CEC0',
           '#C2B8A8', '#D3CABD', '#E7E1D7', '#F07A22',
           '#D7611B', '#E86C1E', '#F28A2E', '#D96A1E',
           '#2A1D17', '#B9AEA2', '#F2E6C9', '#6E9F4A']
(BODY, BODY_D, BODY_L, WING, WING_D, TAIL, NECK, BILL, BILL_D, KNOB, LEG, LEG_D, EYE, EYE_RING, CREAM, GREEN) = range(16)
BUDGET = 1100

# joints = part pivots (shifted with the mesh so the root sits under the centre of mass)
JOINTS = {
    'Body': (0, 0.0, 0.225), 'Neck1': (0, -0.140, 0.280), 'Neck2': (0, -0.144, 0.412), 'Head': (0, -0.150, 0.522),
    'Beak_Lower': (0, -0.208, 0.512),
    'WingUpper.L': (0.110, -0.100, 0.280), 'WingLower.L': (0.115, -0.070, 0.195), 'WingTip.L': (0.100, 0.095, 0.262),
    'TailFan1': (0, 0.150, 0.258), 'TailFan2': (0, 0.222, 0.284),
    'LegUpper.L': (0.066, -0.045, 0.170), 'LegLower.L': (0.066, -0.045, 0.110), 'Foot.L': (0.066, -0.045, 0.020),
}
LEG_X, LEG_Y = 0.066, -0.045

# body rings (front-bottom y, z, back-top y, z, half width), breast -> rear. Front rings tilted: the breast curves up into
# the neck as one surface and the small front ring lies inside the Neck1 base (no cap, no point).
BODY_RINGS = [(-0.205, 0.300, -0.140, 0.338, 0.055), (-0.228, 0.225, -0.108, 0.348, 0.105),
              (-0.248, 0.160, -0.095, 0.352, 0.128), (-0.220, 0.105, -0.075, 0.354, 0.138),
              (-0.140, 0.085, -0.045, 0.354, 0.142), (-0.050, 0.088, -0.010, 0.350, 0.140),
              (0.045, 0.108, 0.045, 0.342, 0.132), (0.115, 0.145, 0.115, 0.328, 0.112),
              (0.165, 0.185, 0.165, 0.312, 0.082), (0.198, 0.222, 0.198, 0.296, 0.045)]
# neck rings (z, y centre, half x, half front, half back); rings perpendicular to the centre line; gentle S in y
NECK1 = [(0.275, -0.140, 0.078, 0.070, 0.066), (0.335, -0.150, 0.064, 0.064, 0.056),
         (0.400, -0.148, 0.055, 0.053, 0.052), (0.440, -0.140, 0.052, 0.050, 0.049)]
NECK2 = [(0.412, -0.144, 0.053, 0.051, 0.050), (0.460, -0.137, 0.052, 0.050, 0.050),
         (0.500, -0.142, 0.049, 0.048, 0.047), (0.535, -0.152, 0.043, 0.042, 0.042)]
# head rings along -Y (y, half width, z bottom, z top)
HEAD_RINGS = [(-0.098, 0.028, 0.505, 0.552), (-0.112, 0.048, 0.486, 0.584), (-0.140, 0.059, 0.474, 0.600),
              (-0.174, 0.058, 0.476, 0.600), (-0.203, 0.048, 0.486, 0.590), (-0.222, 0.033, 0.500, 0.570)]
# bill: base point on the mouth line, direction forward-down, length; sections (s, half width, ridge height above mouth)
BILL_B0, BILL_DIR, BILL_L = Vector((0, -0.203, 0.528)), Vector((0, -0.78, -0.63)).normalized(), 0.088
BILL_UP = [(0.0, 0.036, 0.032), (0.22, 0.033, 0.027), (0.62, 0.030, 0.018), (1.0, 0.023, 0.010)]
BILL_LO = [(0.04, 0.031, 0.019), (0.60, 0.026, 0.013), (0.96, 0.017, 0.005)]       # (s, half width, depth)
KNOB_S, KNOB_SINK = 0.16, 0.010
KNOB_PROF = [(0.0, 0.024, 0.021), (0.011, 0.027, 0.023), (0.022, 0.019, 0.016), (0.028, 0.010, 0.009)]   # (h, rx, ru)
EYE_AT = (-0.180, 0.556)             # (y, z) on the head side
EYE_R, EYE_PROUD, RING_R, RING_PROUD = 0.011, 0.0045, 0.0150, 0.0018
# wing tiers along y: (y, z centre, half height, proud)
WING_UP = [(-0.120, 0.280, 0.020, 0.012), (-0.100, 0.274, 0.055, 0.026), (-0.005, 0.272, 0.062, 0.030),
           (0.080, 0.276, 0.050, 0.028), (0.135, 0.284, 0.020, 0.016)]
WING_LO = [(-0.090, 0.198, 0.018, 0.012), (-0.070, 0.196, 0.040, 0.022), (0.020, 0.192, 0.045, 0.025),
           (0.105, 0.210, 0.035, 0.020), (0.150, 0.228, 0.012, 0.012)]
WING_TIP = [(0.095, 0.262, 0.042, 0.020), (0.165, 0.268, 0.028, 0.016), (0.220, 0.280, 0.008, 0.008)]
WING_YMAX = 0.180                     # beyond this y the body is too thin: the wing tip takes x from here, tapered
# tail: rump wedge + 5 broad plates in a fan, tilted up (yaw deg, length, root dz, pitch deg)
FAN_ROOT = Vector((0, 0.222, 0.284))
FEATHERS = [(-22, 0.066, -0.004, 12), (-11, 0.076, 0.000, 16), (0, 0.084, 0.006, 20), (11, 0.076, 0.000, 16),
            (22, 0.066, -0.004, 12)]
FEATHER_W = [(0.0, 0.024, 0.016), (0.55, 0.030, 0.017), (1.0, 0.015, 0.009)]           # (s, half width, half thickness)
# webbed foot outline (angle from forward towards outside deg, radius, top z); centre top vertex hidden in the ankle pad
WEB = [(180, 0.020, 0.012), (-120, 0.026, 0.011), (-42, 0.074, 0.007), (-33, 0.088, 0.009), (-17, 0.066, 0.004),
       (-4, 0.094, 0.009), (4, 0.094, 0.009), (17, 0.066, 0.004), (33, 0.088, 0.009), (42, 0.074, 0.007),
       (120, 0.026, 0.011)]
WEB_TOP, FOOT_SPLAY = 0.022, 8.0


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-05', 'build'])[:2]


# ---------------- ring helpers (copied from the hen / rooster) ----------------
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
X_, Y_, Z_ = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def cone(P, ring, apex, slot):
    """closed pyramid: flat n-gon disc + triangles to a buried apex; returns its faces"""
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def bvh_of(faces):
    vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])


def lerp_prof(prof, s):
    for a, b in zip(prof, prof[1:]):
        if a[0] <= s <= b[0]:
            f = (s - a[0]) / (b[0] - a[0]); return tuple(x + (y - x) * f for x, y in zip(a[1:], b[1:]))
    return tuple(prof[-1][1:])


def neck_rings(spec, n=8):
    """rings perpendicular to the neck centre line (front axis = -Y made perpendicular to the tangent)"""
    cs = [V(0, y, z) for z, y, *_ in spec]; out = []
    for i, (z, y, w, df, db) in enumerate(spec):
        t = (cs[min(i + 1, len(cs) - 1)] - cs[max(i - 1, 0)]).normalized()
        fr = V(0, -1, 0); fr = (fr - t * fr.dot(t)).normalized()
        out.append(ring_frame(cs[i], X_, fr, w, df, db, n))
    return out


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Goose')
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 10) for fy, fz, by, bz, w in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    # neck: two thick 8-sided lofts with overlap rings, Neck2 runs into the lower back of the head
    P.loft('Neck1', neck_rings(NECK1), NECK, NECK, NECK)
    P.loft('Neck2', neck_rings(NECK2), NECK, NECK, NECK)
    # head (big round white head)
    P.loft('Head', [ring_y(y, w, zb, zt, 10, 2.3, 2.1) for y, w, zb, zt in HEAD_RINGS], NECK, NECK, NECK)
    head_faces = list(P.comp[-1][1])
    # upper bill: pentagon sections (ridge, shoulders, mouth corners) along BILL_DIR, flat mouth line
    D = BILL_DIR; U = D.cross(X_).normalized()
    if U.z < 0: U = -U
    c_at = lambda s: BILL_B0 + D * (BILL_L * s)
    rings = []
    for s, hw, top in BILL_UP:
        c = c_at(s)
        rings.append([c + U * top, c + X_ * (0.80 * hw) + U * (0.60 * top), c + X_ * hw, c - X_ * hw,
                      c - X_ * (0.80 * hw) + U * (0.60 * top)])
    P.loft('Head', rings, BILL, BILL, BILL)
    # lower bill: trapezoid sections 1 mm under the mouth line (no coplanar faces with the upper bill)
    rings = []
    for s, hw, dp in BILL_LO:
        c = c_at(s)
        rings.append([c + X_ * hw - U * 0.001, c - X_ * hw - U * 0.001, c - X_ * (0.55 * hw) - U * dp,
                      c + X_ * (0.55 * hw) - U * dp])
    P.loft('Beak_Lower', rings, BILL_D, BILL_D, BILL_D)
    # basal knob: rounded 8-sided lump on the bill base at the forehead
    top_k = lerp_prof([(s, hw, t) for s, hw, t in BILL_UP], KNOB_S)[1]
    K = c_at(KNOB_S) + U * (top_k - KNOB_SINK)
    nk = (U + V(0, 0.15, 0.20)).normalized(); e2 = nk.cross(X_).normalized()
    rings = [[K + nk * h + X_ * (rx * math.cos(a)) + e2 * (ru * math.sin(a))
              for a in [math.pi / 8 + 2 * math.pi * k / 8 for k in range(8)]] for h, rx, ru in KNOB_PROF]
    P.loft('Head', rings, KNOB, KNOB, KNOB)

    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: raise RuntimeError(f'no surface hit at y {y} z {z}')
        return hit[0].x, hit[1]
    # eyes: dark 8-gon disc on a slightly bigger warm-grey ring disc, both backed by pyramids buried in the head
    ey, ez = EYE_AT
    hx_, n = side_x(bvh_head, ey, ez); hp = V(hx_, ey, ez)
    n = (n + V(0, -0.45, 0.05)).normalized()
    t_, e1, e2 = pc.basis(n, (0, 0, 1))
    eye = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); eye_ap = hp - n * 0.010
    ring = ngon_ring(hp + n * RING_PROUD, e1, e2, RING_R, 8, phase=0.0); ring_ap = hp - n * 0.008
    for nm, sx in (('Eye.L', 1), ('Eye.R', -1)):
        f = (lambda p: p) if sx > 0 else (lambda p: V(-p.x, p.y, p.z))
        P.comp.append((nm, cone(P, [f(p) for p in eye], f(eye_ap), EYE) + cone(P, [f(p) for p in ring], f(ring_ap), EYE_RING),
                       False))

    # wings: pentagon sections hugging the body side (top tucked in, lower lip proud)
    def wing_rings(spec):
        out = []
        for y, zc, h, pr in spec:
            yy = min(y, WING_YMAX); taper = 1.0 - max(0.0, y - WING_YMAX) / 0.10
            pts = []
            for dz, dx in [(h, -0.003), (0.45 * h, 0.8 * pr), (-0.45 * h, pr), (-h, 0.65 * pr), (0.0, -0.012)]:
                xs, _ = side_x(bvh_body, yy, zc + dz); pts.append(V(xs * taper + dx, y, zc + dz))
            out.append(pts)
        return out
    for nm, spec, slot in (('WingUpper', WING_UP, WING), ('WingLower', WING_LO, WING_D), ('WingTip', WING_TIP, WING_D)):
        r = wing_rings(spec)
        P.loft(nm + '.L', r, slot, slot, slot); P.loft(nm + '.R', mir(r), slot, slot, slot)

    # tail: rump wedge (TailFan1) + 5 broad diamond-section plates fanned horizontally, tilted up (TailFan2)
    a0, a1 = V(0, 0.150, 0.256), V(0, 0.272, 0.292)
    d = (a1 - a0).normalized(); up = X_.cross(d).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), X_, up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.068, 0.048), (0.6, 0.054, 0.036), (1.0, 0.034, 0.022)]], TAIL, TAIL, TAIL)
    tips = []
    for i, (yaw, L, dz, pit) in enumerate(FEATHERS):
        a = math.radians(yaw); pt = math.radians(pit)
        dv = V(math.sin(a) * math.cos(pt), math.cos(a) * math.cos(pt), math.sin(pt))
        ew = V(math.cos(a), -math.sin(a), 0); tv = dv.cross(ew).normalized()
        if tv.z < 0: tv = -tv
        tk = 1.25 if i % 2 else 1.0
        root = FAN_ROOT + V(0, 0, dz); fr = []
        for s, w, t in FEATHER_W:
            c = root + dv * (L * s)
            fr.append([c + ew * w, c + tv * (t * tk), c - ew * w, c - tv * (t * tk)])
        tips.append(fr[-1][1])
        P.loft('TailFan2', fr, TAIL, TAIL, TAIL)

    # legs: white thigh cuff, thick orange 6-gon shank tapering into the webbed foot
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X_, Y_, r, 6) for z, r in [(0.185, 0.036), (0.100, 0.027)]],
               BODY_D, BODY_D, BODY_D)
        # one tapered shank prism running straight into the web (no ankle ring, no step)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X_, Y_, r, 6) for z, r in [(0.120, 0.0195), (0.008, 0.0170)]],
               LEG, LEG, LEG)
        base = c(0.0); faces = []
        bot, top = [], []
        for ang, r, zt in WEB:
            a = math.radians(ang + FOOT_SPLAY)              # whole foot turned outwards
            dv = V(sx * math.sin(a), -math.cos(a), 0)
            bot.append(P.bm.verts.new(base + dv * r)); top.append(P.bm.verts.new(base + dv * r + V(0, 0, zt)))
        ctr = P.bm.verts.new(base + V(0, 0, WEB_TOP)); n = len(WEB)
        if sx < 0: bot.reverse(); top.reverse()
        faces.append(P.face(list(reversed(bot)), LEG_D))
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([bot[k], bot[k1], top[k1], top[k]], LEG))
            faces.append(P.face([top[k], top[k1], ctr], LEG))
        P.comp.append(('Foot' + sfx, faces, True))
    return P, tips


# ---------------- colours ----------------
def colour(P):
    for nm, faces, _ in P.comp:
        if nm == 'Body':
            for f in faces:
                if f.normal.z < -0.50: f[P.slot] = BODY_D
                elif f.normal.z > 0.70: f[P.slot] = BODY_L
        elif nm in ('Neck1', 'Neck2', 'Head'):
            for f in faces:
                if f[P.slot] == NECK and f.normal.z < -0.55: f[P.slot] = BODY


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
    me = bpy.data.meshes.new('TMP_GooseAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_GooseAll', me)
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Goose_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Goose_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-05 Goose', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Goose_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
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
