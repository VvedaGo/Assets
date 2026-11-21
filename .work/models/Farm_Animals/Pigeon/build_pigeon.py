# build_pigeon.py - BRD-08 Pigeon, Farm Animals, skeleton B parts, MESH ONLY (no armature/weights/clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_pigeon.py -- BRD-08 build|look|export
# build : parts + palette + checks + Workbench check sheet and 128 px thumbnail (TEMP/FarmAnimals_check_pigeon)
# look  : build + EEVEE look at the reference angle (TEMP)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure copied from ../Duck/build_duck.py (ring helpers, split_to_objects, checks, renders).
# v2 (rework): plump pear body 12 sides, big egg head of horizontal tilted rings (one ring edge = collar line),
# one blue collar band (body front segment + necks + lower head) with a V point on the chest, shield wing, fanned tail.
import sys, os, math
REPO = r'C:\Users\Sergv\orca\workspaces\VFX\master-3'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Pigeon'
TAG = 'FarmAnimals_Pigeon'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\BRD-08.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_pigeon')
REF_VIEW = (0.66, -0.75, 0.14)       # reference: front-left three-quarter, body yaw ~35 deg from the front, ~8 deg above
PREVIEW_VIEW = (0.66, -0.75, 0.16)
PALETTE = ['#A09FAB', '#85848F', '#ABAAB5', '#5E7FA3',
           '#6C8BB2', '#6F84B0', '#93929E', '#6A6A74',
           '#F2F2F4', '#4A4A53', '#62626C', '#8E8C98',
           '#C9C7D1', '#E8A23A', '#CC862C', '#2A1D17']
(BODY, BODY_D, BODY_L, NECK, NECK_L, IRID, WING, WING_D, WHITE, TIP, TAIL, BEAK, CERE, LEG, LEG_D, EYE) = range(16)
BUDGET = 600

LEG_X, LEG_Y = 0.038, -0.012
JOINTS = {
    'Body': (0, 0.0, 0.12), 'Neck1': (0, -0.062, 0.165), 'Neck2': (0, -0.064, 0.185), 'Head': (0, -0.068, 0.205),
    'Beak_Lower': (0, -0.104, 0.204),
    'WingUpper.L': (0.070, -0.068, 0.160), 'WingLower.L': (0.070, -0.040, 0.105), 'WingTip.L': (0.060, 0.060, 0.112),
    'TailFan1': (0, 0.080, 0.112), 'TailFan2': (0, 0.095, 0.108),
    'LegUpper.L': (LEG_X, LEG_Y, 0.075), 'LegLower.L': (LEG_X, LEG_Y, 0.046), 'Foot.L': (LEG_X, LEG_Y, 0.004),
}

# body rings, tilted sections (front-bottom y, z, back-top y, z, half width, bottom exponent); 12 sides.
# R0 = cap inside Neck1; R1 = lower edge of the blue collar (pointed front vertex -> V on the chest); R2 widest chest.
BODY_RINGS = [(-0.090, 0.175, -0.045, 0.212, 0.040, 2.2), (-0.124, 0.130, -0.020, 0.212, 0.066, 1.45),
              (-0.130, 0.095, 0.020, 0.188, 0.077, 2.2), (-0.092, 0.050, 0.050, 0.172, 0.075, 2.2),
              (-0.012, 0.040, 0.075, 0.150, 0.063, 2.2), (0.060, 0.062, 0.100, 0.130, 0.040, 2.2),
              (0.095, 0.088, 0.115, 0.115, 0.018, 2.2)]
# neck rings, horizontal (z, y centre, half x, half front, half back), 8 sides
NECK1 = [(0.150, -0.062, 0.046, 0.034, 0.032), (0.200, -0.066, 0.038, 0.030, 0.028)]
NECK2 = [(0.180, -0.064, 0.042, 0.033, 0.031), (0.214, -0.067, 0.038, 0.032, 0.030)]
# head rings, horizontal tilted (z centre, y centre, tilt deg (front down), half x, half front, half back), 12 sides
# H1 is the collar line on the head (front under the beak, rising to the cheeks at the back)
HEAD_RINGS = [(0.165, -0.064, 30, 0.052, 0.058, 0.040), (0.210, -0.068, 23, 0.050, 0.050, 0.042),
              (0.234, -0.070, 8, 0.049, 0.045, 0.041), (0.253, -0.071, 0, 0.042, 0.039, 0.036),
              (0.266, -0.071, 0, 0.029, 0.027, 0.025), (0.272, -0.071, 0, 0.013, 0.012, 0.011)]
# upper beak (y, half width, mouth z, top z): 5-point rounded wedge, first segment top = pale cere bump
BEAK_UP = [(-0.102, 0.014, 0.205, 0.229), (-0.116, 0.012, 0.202, 0.222), (-0.130, 0.0045, 0.189, 0.195)]
BEAK_LO = [(-0.104, 0.0135, 0.008), (-0.125, 0.005, 0.0035)]
# wing: one shield, sections (y, z centre, half height, proud, fixed base x or None = ray-cast onto the body side)
WING_SECTIONS = [(-0.072, 0.160, 0.016, 0.008, None), (-0.042, 0.143, 0.044, 0.020, None), (0.008, 0.124, 0.048, 0.026, None),
                 (0.050, 0.113, 0.040, 0.032, None), (0.088, 0.106, 0.024, 0.020, 0.044),
                 (0.125, 0.102, 0.014, 0.014, 0.034), (0.152, 0.098, 0.004, 0.005, 0.020)]
# tail fan (t along root -> end, half width, half thickness)
TAIL_SECTIONS = [(0.0, 0.028, 0.018), (0.6, 0.033, 0.012), (1.0, 0.036, 0.008)]
EYE_R, EYE_PROUD, EYE_YAW = 0.0068, 0.0025, 55


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['BRD-08', 'build'])[:2]


# ---------------- ring helpers (copied from the duck) ----------------
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



# ---------------- mesh ----------------
def tilt_ring(z, yc, tilt, hx, hf, hb, n, p=2.2):
    a = math.radians(tilt)
    return ring_frame(V(0, yc, z), V(1, 0, 0), V(0, -math.cos(a), -math.sin(a)), hx, hf, hb, n, p)


def build_mesh():
    P = pc.Part('Pigeon')
    # body: plump pear; segment 0 (R0 -> R1) is the blue collar on the chest, R1 has a pointed front vertex (V)
    collar = lambda j, k: NECK if j == 0 else BODY
    P.loft('Body', [ring_tilt(fy, fz, by, bz, w, 12, 2.2, pb) for fy, fz, by, bz, w, pb in BODY_RINGS], collar, NECK, BODY)
    body_faces = list(P.comp[-1][1])
    ax, front = V(1, 0, 0), V(0, -1, 0)
    P.loft('Neck1', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK1], NECK, NECK, NECK)
    P.loft('Neck2', [ring_frame(V(0, y, z), ax, front, w, df, db, 8) for z, y, w, df, db in NECK2], NECK, NECK, NECK)
    # head: egg of horizontal rings; segment 0 (H0 -> H1) blue (collar wraps the lower head), above grey
    P.loft('Head', [tilt_ring(*r, 12) for r in HEAD_RINGS], lambda j, k: NECK if j == 0 else BODY, NECK, BODY)
    head_faces = list(P.comp[-1][1])
    # upper beak: rounded wedge, section ridge, shoulder R, lip R, lip L, shoulder L; cere = top of segment 0
    def bill_ring(y, w, zm, zt):
        zs = zt - 0.35 * (zt - zm)
        return [V(0, y, zt), V(0.80 * w, y, zs), V(w, y, zm), V(-w, y, zm), V(-0.80 * w, y, zs)]
    P.loft('Head', [bill_ring(*r) for r in BEAK_UP], lambda j, k: CERE if (j == 0 and k in (0, 4)) else BEAK, BEAK, BEAK)
    y0, z0, y1, z1 = BEAK_UP[0][0], BEAK_UP[0][2], BEAK_UP[-1][0], BEAK_UP[-1][2]
    zm_at = lambda y: z0 + (y - y0) * (z1 - z0) / (y1 - y0)
    P.loft('Beak_Lower', [[V(w, y, zm_at(y) - 0.001), V(-w, y, zm_at(y) - 0.001), V(0, y, zm_at(y) - d)]
                          for y, w, d in BEAK_LO], BEAK, BEAK, BEAK)

    def bvh_of(faces):
        vs = sorted({v for f in faces for v in f.verts}, key=lambda v: v.index); ix = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co.copy() for v in vs], [[ix[v] for v in f.verts] for f in faces])
    P.bm.verts.index_update()
    bvh_body, bvh_head = bvh_of(body_faces), bvh_of(head_faces)

    def side_x(bvh, y, z):
        hit = bvh.ray_cast(V(1.0, y, z), V(-1, 0, 0))
        if hit[0] is None: raise RuntimeError(f'no surface hit at y {y} z {z}')
        return hit[0].x, hit[1]
    # eyes: big 8-gon dark discs on the front-side of the head (EYE_YAW from the front), backed by a buried pyramid
    a = math.radians(EYE_YAW); d = V(math.sin(a), -math.cos(a), 0.08).normalized(); hc = V(0, -0.070, 0.236)
    hit = bvh_head.ray_cast(hc + d * 0.3, -d)
    if hit[0] is None: raise RuntimeError('eye ray missed the head')
    hn = hit[1] if hit[1].dot(d) > 0 else -hit[1]          # loft winding may give an inward normal
    hp, n = hit[0], (hn + d).normalized()
    _, e1, e2 = pc.basis(n, (0, 0, 1))
    ring = ngon_ring(hp + n * EYE_PROUD, e1, e2, EYE_R, 8); apex = hp - n * 0.007
    for nm, rg, ap in (('Eye.L', ring, apex), ('Eye.R', mir([ring])[0], Vector((-apex.x, apex.y, apex.z)))):
        P.comp.append((nm, cone(P, rg, ap, EYE), False))

    # wing: ONE shield along the body side (7-point section), split along its length into WingUpper (shoulder),
    # WingLower (middle, flush white diagonal stripe) and WingTip (dark point over the tail). Each part starts 4 mm inside
    # the previous one, 1.5 mm smaller (overlap for bending, no visible flap or step).
    SEC7 = [(1.0, -0.3), (0.60, 0.80), (0.20, 1.0), (-0.25, 1.0), (-0.65, 0.92), (-1.0, 0.55), (0.0, -0.5)]
    def wing_section(y, zc, h, pr, xb):
        pts = []
        for fz, fx in SEC7:
            z = zc + fz * h
            xs = side_x(bvh_body, y, z)[0] if xb is None else xb * (1.0 - 0.25 * fz * fz)
            pts.append(V(xs + fx * pr, y, z))
        return pts
    def wing_part(name, spec, col):
        rings = [wing_section(*s) for s in spec]
        for sfx, R in (('.L', rings), ('.R', mir(rings))):
            faces = []; vs = [[P.bm.verts.new(p) for p in r] for r in R]; n = len(vs[0])
            for j in range(len(vs) - 1):
                for k in range(n):
                    a, b, c, d = vs[j][k], vs[j][(k + 1) % n], vs[j + 1][(k + 1) % n], vs[j + 1][k]
                    faces.append(P.face([a, b, c], col(j, k, 1)))      # front-lower triangle
                    faces.append(P.face([a, c, d], col(j, k, 2)))      # back-upper triangle (diagonal a-c runs down-back)
            faces.append(P.face(list(reversed(vs[0])), col(0, 0, 0))); faces.append(P.face(list(vs[-1]), col(len(vs) - 2, 0, 0)))
            P.comp.append((name + sfx, faces, False))
    shrink = lambda s, dy: (s[0] - dy, s[1], s[2] - 0.0015, s[3] - 0.0015, s[4])
    W = WING_SECTIONS
    base = lambda j, k, t: WING_D if k == 4 else WING
    def upper_col(j, k, t):
        if j == 1 and ((k == 1 and t == 1) or k == 2 or (k == 3 and t == 2)): return WHITE    # flush diagonal parallelogram
        return base(j, k, t)
    def lower_col(j, k, t):
        if j == 1 and k in (3, 4, 5): return WING_D
        return base(j, k, t)
    wing_part('WingUpper', W[0:3], upper_col)
    wing_part('WingLower', [shrink(W[2], 0.004)] + W[3:5], lower_col)
    wing_part('WingTip', [shrink(W[4], 0.004)] + W[5:7], lambda j, k, t: TIP)

    # tail: grey rump wedge (TailFan1); TailFan2 = thick flat wedge fan, dark grey, squared end beyond the wing tip
    a0, a1 = V(0, 0.080, 0.112), V(0, 0.130, 0.100)
    dv = (a1 - a0).normalized(); up = V(1, 0, 0).cross(dv).normalized()
    if up.z < 0: up = -up
    P.loft('TailFan1', [ring_frame(a0.lerp(a1, t), V(1, 0, 0), up, w, h, h, 6, 2.2) for t, w, h in
                        [(0.0, 0.034, 0.030), (1.0, 0.028, 0.018)]], BODY, BODY, BODY)
    r0, r1 = V(0, 0.095, 0.110), V(0, 0.192, 0.070)
    dv = (r1 - r0).normalized(); up = V(1, 0, 0).cross(dv).normalized()
    if up.z < 0: up = -up
    tl = []
    for s, w, t in TAIL_SECTIONS:
        c = r0.lerp(r1, s); X = V(1, 0, 0)
        tl.append([c + X * w, c + X * (0.60 * w) + up * t, c - X * (0.60 * w) + up * t, c - X * w,
                   c - X * (0.60 * w) - up * t, c + X * (0.60 * w) - up * t])
    P.loft('TailFan2', tl, lambda j, k: TAIL if j == 0 else TIP, TAIL, TIP)

    # legs: grey thigh cuff, short thick orange 6-gon shank, big foot: 3 front toes + 1 back toe
    X, Y = V(1, 0, 0), V(0, 1, 0)
    for sfx, sx in (('.L', 1), ('.R', -1)):
        c = lambda z: V(sx * LEG_X, LEG_Y, z)
        P.loft('LegUpper' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.080, 0.020), (0.042, 0.0145)]],
               BODY_D, BODY_D, BODY_D)
        P.loft('LegLower' + sfx, [ngon_ring(c(z), X, Y, r, 6) for z, r in [(0.050, 0.0108), (0.003, 0.0100)]],
               LEG, LEG, LEG_D)
        base = c(0.0)
        for yaw, L, wr in [(0, 0.046, 0.0078), (36, 0.040, 0.0072), (-36, 0.040, 0.0072), (180, 0.022, 0.0065)]:
            a = math.radians(yaw); dv = V(sx * math.sin(a), -math.cos(a), 0); sd = V(-dv.y, dv.x, 0)
            q0 = base + dv * 0.004; q1 = base + dv * L
            toe = [[q0 + sd * wr + V(0, 0, 0.002), q0 - sd * wr + V(0, 0, 0.002), q0 - sd * wr * 0.75 + V(0, 0, 0.015),
                    q0 + sd * wr * 0.75 + V(0, 0, 0.015)],
                   [q1 + sd * wr * 0.72, q1 - sd * wr * 0.72, q1 - sd * wr * 0.5 + V(0, 0, 0.009), q1 + sd * wr * 0.5 + V(0, 0, 0.009)]]
            P.loft('Foot' + sfx, toe, LEG, LEG, LEG)
    return P, body_faces


# ---------------- colours ----------------
def colour(P):
    pass                             # all colours are assigned per segment in build_mesh (clean ring-edge boundaries)


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
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1000:.3f} L -> shifted y by {sh.y:+.4f}')
    feet = [v.co for nm, faces, _ in P.comp if nm.startswith('Foot') for f in faces for v in f.verts]
    print(f'feet y range {min(p.y for p in feet):.3f}..{max(p.y for p in feet):.3f} (COM y = 0 after shift)')
    chk = pc.comp_checks(P)
    tri = tris_by_part(P)
    me = bpy.data.meshes.new('TMP_PigeonAll'); P.bm.to_mesh(me); tmp = bpy.data.objects.new('TMP_PigeonAll', me)
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
    out = rn.compose([rn.ref_tile(REF, 512)] + tiles, 3, os.path.join(CHECK, f'Pigeon_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Pigeon_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


if __name__ == '__main__':
    ID, CMD = args()
    print('=== BRD-08 Pigeon', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        rn.preview(B['sc'], list(B['obs'].values()), os.path.join(CHECK, 'Pigeon_look.png'), view=PREVIEW_VIEW, fill=(0.64, 0.86))
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
