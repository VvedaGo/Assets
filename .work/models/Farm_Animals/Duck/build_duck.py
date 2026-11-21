# build_duck.py - BRD-04 Duck (mallard drake), Farm Animals, skeleton B parts, MESH ONLY (no armature/weights/clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_duck.py -- BRD-04 build|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_duck)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Hen/build_hen.py (ring helpers, split_to_objects, checks, renders).
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Duck'
TAG = 'FarmAnimals_Duck'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-04.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_duck')
REF_VIEW = (0.72, -0.69, 0.18)       # reference: front-left three-quarter, yaw ~45 deg, ~10 deg above
PALETTE = ['#968679', '#74665D', '#7C4E3F', '#4E3128',
           '#6E9F4A', '#5B8A3D', '#EEE6D3', '#AC9E92',
           '#85766C', '#5A4B44', '#4B5277', '#F28C38',
           '#CF6420', '#F08A36', '#2A1D17', '#3B302C']
(BODY, BELLY, CHEST, NOSTRIL, HEAD, HEAD_D, CREAM, WING, WING_L, WING_D, SPEC, BILL, BILL_D, LEG, EYE, CURL) = range(16)
BUDGET = 800

JOINTS = {
    'Body': (0, 0.0, 0.17), 'Neck1': (0, -0.112, 0.215), 'Neck2': (0, -0.121, 0.288), 'Head': (0, -0.120, 0.322),
    'Beak_Lower': (0, -0.172, 0.298),
    'WingUpper.L': (0.100, -0.080, 0.215), 'WingLower.L': (0.100, -0.060, 0.163), 'WingTip.L': (0.080, 0.060, 0.205),
    'TailFan1': (0, 0.110, 0.188), 'TailFan2': (0, 0.160, 0.200),
    'LegUpper.L': (0.054, -0.024, 0.110), 'LegLower.L': (0.054, -0.024, 0.056), 'Foot.L': (0.054, -0.024, 0.012),
}
LEG_X, LEG_Y = 0.054, -0.024

# body rings (front-bottom y, z, back-top y, z, half width), breast -> rear; the front rings are tilted so the breast curves
# up into the neck and the front cap lies inside Neck1 (no visible cap or pole)
BODY_RINGS = [(-0.150, 0.226, -0.100, 0.262, 0.046), (-0.182, 0.186, -0.090, 0.265, 0.082),
              (-0.194, 0.138, -0.076, 0.265, 0.106), (-0.172, 0.094, -0.058, 0.264, 0.116),
              (-0.090, 0.076, -0.030, 0.262, 0.120), (0.020, 0.078, 0.030, 0.258, 0.116),
              (0.090, 0.092, 0.090, 0.250, 0.098), (0.135, 0.118, 0.135, 0.236, 0.068),
              (0.160, 0.150, 0.160, 0.220, 0.034)]
# neck rings, horizontal (z, y centre, half x, half front, half back); Neck1 segment 0 = cream ring
NECK1 = [(0.200, -0.112, 0.052, 0.050, 0.055), (0.234, -0.117, 0.050, 0.048, 0.052), (0.295, -0.122, 0.046, 0.045, 0.050)]
NECK2 = [(0.280, -0.121, 0.047, 0.046, 0.050), (0.340, -0.120, 0.042, 0.040, 0.050)]
# head rings along -Y (y, half width, z bottom, z top)
HEAD_RINGS = [(-0.064, 0.030, 0.310, 0.368), (-0.080, 0.050, 0.290, 0.392), (-0.118, 0.059, 0.278, 0.402),
              (-0.160, 0.051, 0.278, 0.392), (-0.183, 0.035, 0.284, 0.370), (-0.194, 0.018, 0.293, 0.345)]
# upper bill (y, half width, mouth z, top z): 5-point section (ridge, shoulders, lips); flat bottom = mouth line
BILL_UP = [(-0.172, 0.022, 0.300, 0.334), (-0.196, 0.021, 0.297, 0.327), (-0.207, 0.0215, 0.295, 0.322),
           (-0.240, 0.023, 0.286, 0.303), (-0.256, 0.016, 0.283, 0.294)]
NOSTRIL_SEG = 1                      # shoulder quads between rings 1 and 2 = dark nostril cells
# lower bill (y, half width top, depth below the mouth line)
BILL_LO = [(-0.170, 0.019, 0.014), (-0.212, 0.020, 0.012), (-0.248, 0.017, 0.006)]
# wing tiers along y: (y, z centre, half height, proud)
WING_UP = [(-0.118, 0.220, 0.018, 0.008), (-0.094, 0.219, 0.036, 0.022), (0.040, 0.219, 0.034, 0.026),
           (0.112, 0.216, 0.020, 0.020)]
WING_LO = [(-0.092, 0.168, 0.018, 0.009), (0.022, 0.165, 0.032, 0.024),
           (0.036, 0.165, 0.032, 0.025), (0.080, 0.167, 0.030, 0.024), (0.093, 0.168, 0.028, 0.022),
           (0.115, 0.172, 0.016, 0.015)]
SPEC_SEG = {1: CREAM, 2: SPEC, 3: CREAM}     # WingLower segments -> speculum colours on the outer face
EYE_R, EYE_PROUD = 0.0088, 0.004


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-04', 'build'])[:2]


# ---------------- ring helpers (copied from the hen) ----------------
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


def cone(P, ring, apex, slot):
    vs = [P.bm.verts.new(p) for p in ring]; a = P.bm.verts.new(apex); n = len(vs)
    faces = [P.face([vs[k], vs[(k + 1) % n], a], slot) for k in range(n)]
    faces.append(P.face(list(reversed(vs)), slot))
    return faces


def web_foot(P, nm, c0, sx):
    """flat triangular webbed foot: concave 8-point outline (heel, sides, 3 toe tips, 2 notches), thin rim, raised toe
    ridges meeting at the ankle point; flat sole at z = 0. 36 tris."""
    yaw = math.radians(9); f = V(sx * math.sin(yaw), -math.cos(yaw), 0); s = V(sx * math.cos(yaw), math.sin(yaw), 0)
    def pt(a, r, z):
        a = math.radians(a); return c0 + (f * math.cos(a) + s * math.sin(a)) * r + V(0, 0, z)
    outl = [(180, 0.016, 0.010), (112, 0.019, 0.009), (33, 0.073, 0.008), (16, 0.046, 0.008), (0, 0.086, 0.008),
            (-16, 0.046, 0.008), (-33, 0.073, 0.008), (-112, 0.019, 0.009)]
    top = [P.bm.verts.new(pt(a, r, z)) for a, r, z in outl]
    bot = [P.bm.verts.new(pt(a, r, 0.0)) for a, r, z in outl]
    A = P.bm.verts.new(pt(0, 0.0, 0.019))
    Ro, Rm, Ri = (P.bm.verts.new(pt(a, r, z)) for a, r, z in ((33, 0.035, 0.014), (0, 0.040, 0.015), (-33, 0.035, 0.014)))
    B, So, To, No, Tm, Ni, Ti, Si = top
    tris = [(A, B, So), (A, So, Ro), (So, To, Ro), (Ro, To, No), (Ro, No, Rm), (A, Ro, Rm), (Rm, No, Tm), (Rm, Tm, Ni),
            (Rm, Ni, Ri), (A, Rm, Ri), (Ri, Ni, Ti), (Ri, Ti, Si), (A, Ri, Si), (A, Si, B)]
    faces = [P.face(list(t), LEG) for t in tris]
    n = len(top)
    for k in range(n):
        faces.append(P.face([top[k], bot[k], bot[(k + 1) % n], top[(k + 1) % n]], BILL_D))
    faces.append(P.face(list(reversed(bot)), BILL_D))
    P.comp.append((nm, faces, True))


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Duck')
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 10) for fy, fz, by, bz, w in BODY_RINGS], BODY, BODY, BODY)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK1],
           lambda j, k: CREAM if j == 0 else HEAD, CREAM, HEAD)
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK2], HEAD, HEAD, HEAD)
    P.loft('Head', [ring_y(y, w, zb, zt, 10, 2.3, 2.1) for y, w, zb, zt in HEAD_RINGS], HEAD, HEAD, HEAD)
    head_faces = list(P.comp[-1][1])
    # upper bill: section ridge, shoulder L, lip L, lip R, shoulder R (flat bottom between the lips = mouth line)
    def bill_ring(y, w, zm, zt):
        zs = zt - 0.30 * (zt - zm)
        return [V(0, y, zt), V(0.80 * w, y, zs), V(w, y, zm), V(-w, y, zm), V(-0.80 * w, y, zs)]
    nost = lambda j, k: NOSTRIL if (j == NOSTRIL_SEG and k in (0, 4)) else BILL
    P.loft('Head', [bill_ring(*r) for r in BILL_UP], nost, BILL, BILL)
    zm_at = lambda y: 0.300 + (y + 0.172) * ((0.283 - 0.300) / (-0.256 + 0.172))
    lo = []
    for y, w, d in BILL_LO:
        z = zm_at(y) - 0.001
        lo.append([V(w, y, z), V(-w, y, z), V(-0.55 * w, y, z - d), V(0.55 * w, y, z - d)])
    P.loft('Beak_Lower', lo, BILL_D, BILL_D, BILL_D)

    def bvh_of(faces):
        vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])
    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: raise RuntimeError(f'no surface hit at y {y} z {z}')
        return hit[0].x, hit[1]
    # eyes: 8-gon dark discs, proud, backed by a pyramid buried in the head
    hx, n = side_x(bvh_head, -0.155, 0.348); hp = V(hx, -0.155, 0.348)
    n = (n + V(0, -0.45, 0.05)).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); apex = hp - n * 0.008
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # wings: 5-point sections hugging the body side (top tucked in, lower lip proud)
    def wing_rings(spec):
        rings = []
        for y, zc, h, pr in spec:
            pts = []
            for dz, dx in [(h, -0.003), (0.45 * h, 0.8 * pr), (-0.45 * h, pr), (-h, 0.65 * pr), (0.0, -0.012)]:
                xs, _ = side_x(bvh_body, y, zc + dz); pts.append(V(xs + dx, y, zc + dz))
            rings.append(pts)
        return rings
    lo_side = lambda j, k: SPEC_SEG.get(j, WING_L) if k == 1 else WING_L
    for nm, spec, side in (('WingUpper', WING_UP, WING), ('WingLower', WING_LO, lo_side)):
        r = wing_rings(spec)
        P.loft(nm + '.L', r, side, side if not callable(side) else WING_L, side if not callable(side) else WING_L)
        P.loft(nm + '.R', mir(r), side, side if not callable(side) else WING_L, side if not callable(side) else WING_L)
    # wing tip: dark primaries running back over the rump (explicit sections, the body ends under it)
    tip = []
    for y, xo, xi, zc, h in [(0.055, 0.106, 0.070, 0.205, 0.034), (0.140, 0.074, 0.040, 0.212, 0.022),
                             (0.198, 0.038, 0.026, 0.222, 0.007)]:
        tip.append([V(xi, y, zc + h), V(xo, y, zc + 0.2 * h), V(xo - 0.006, y, zc - 0.7 * h), V(xi - 0.004, y, zc - 0.5 * h)])
    P.loft('WingTip.L', tip, WING_D, WING_D, WING_D); P.loft('WingTip.R', mir(tip), WING_D, WING_D, WING_D)

    # tail: dark rump wedge (TailFan1), cream upturned point + dark curl (TailFan2)
    a0, a1 = V(0, 0.100, 0.180), V(0, 0.185, 0.205)
    d = (a1 - a0).normalized(); up = V(1, 0, 0).cross(d).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.060, 0.050), (1.0, 0.034, 0.026)]], WING_D, WING_D, WING_D)
    tl = []
    for y, z, w, t in [(0.158, 0.198, 0.040, 0.016), (0.210, 0.208, 0.034, 0.013), (0.250, 0.224, 0.006, 0.005)]:
        tl.append([V(0, y, z + t), V(w, y, z), V(0, y, z - t), V(-w, y, z)])
    P.loft('TailFan2', tl, CREAM, CREAM, CREAM)
    path = [V(0, 0.138, 0.218), V(0, 0.163, 0.244), V(0, 0.150, 0.260)]      # short chunky hook curling forward
    cr = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, 2)] - path[max(i - 1, 0)]).normalized(); e2 = V(1, 0, 0).cross(t).normalized()
        w, h = [(0.013, 0.013), (0.011, 0.011), (0.006, 0.006)][i]
        cr.append([p + e2 * h, p + V(w, 0, 0), p - e2 * h, p - V(w, 0, 0)])
    P.loft('TailFan2', cr, CURL, CURL, CURL)

    # legs: thick orange 6-gon upper/lower shank, flat webbed foot
    X, Y = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.118, 0.0152), (0.050, 0.0134)]], LEG, LEG, LEG)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.060, 0.0130), (0.006, 0.0118)]], LEG, LEG, LEG)
        web_foot(P, 'Foot' + sfx, c(0.0), sx)
    return P, body_faces


# ---------------- colours ----------------
def colour(P):
    for nm, faces, _ in P.comp:
        if nm == 'Body':
            for f in faces:
                c = f.calc_center_median()
                if f.normal.z < -0.55: f[P.slot] = BELLY
                elif c.z > 0.104 and c.y < -0.06 and f.normal.y < -0.42 and abs(f.normal.x) < 0.80: f[P.slot] = CHEST
        elif nm == 'Head':
            for f in faces:
                if f[P.slot] == HEAD and f.normal.z < -0.45: f[P.slot] = HEAD_D


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
    feet = [v.co for nm, faces, _ in P.comp if nm.startswith('Foot') for f in faces for v in f.verts]
    print(f'feet y range {min(p.y for p in feet):.3f}..{max(p.y for p in feet):.3f} (COM y = 0 after shift)')
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_DuckAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_DuckAll', me)
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Duck_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Duck_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-04 Duck', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Duck_look.png'), view=REF_VIEW, fill=(0.55, 0.85))
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
