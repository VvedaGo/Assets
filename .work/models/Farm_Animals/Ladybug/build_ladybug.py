# build_ladybug.py - INS-03 Ladybug (Farm Animals extension, skeleton I parts, MESH ONLY: no armature/weights/clips).
#   PYTHONUTF8=1 blender --background --factory-startup --python build_ladybug.py -- INS-03 build|look|export
# build : parts + palette + checks + Workbench check sheet (reference tile first) + 128 px thumbnail (TEMP/FarmAnimals_check_ladybug)
# look  : build + EEVEE preview into TEMP (check only)
# export: build + FBX (pack_common.export) + verify + collection .blend + EEVEE preview (art/Farm_Animals)
# Blender axes: front = -Y, left = +X, up = +Z, metres (FBX: Y up, Z forward in Unity).
# Structure from ../Bee/build_bee.py (helpers copied); coplanar_true from ../Mouse/build_mouse.py. Shared modules read-only.
import sys, os, math
REPO = r'D:\GitProjects\Assets_Farm'
for p in (REPO + r'\Tools\blender', REPO + r'\.work\models\Farm_Animals\_common'):
    if p not in sys.path: sys.path.insert(0, p)
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
import pack_common as pc
import animal_render as rn          # read-only shared module (render helpers only)

ASSET = 'FMS_Ladybug'
TAG = 'FarmAnimals_Ladybug'
ART = REPO + r'\art\Farm_Animals'
REF = REPO + r'\planning\FarmAnimals\references\INS-03.png'
CHECK = os.path.join(os.environ.get('TEMP', '/tmp'), 'FarmAnimals_check_ladybug')
PALETTE = ['#E25B44', '#D6452F', '#CB3D2B', '#B5362A',
           '#3A2E2C', '#2F2523', '#7E2418', '#6E2016',
           '#653A29', '#463836', '#4A2A20', '#241815',
           '#3A2E2C', '#2C2321', '#CFC7BC', '#A39A8E']
(R_TOP, R_MID, R_LOW, R_RIM, SPOT, SPOT_D, GROOVE, UNDER, EYE_C, HEAD_L, EYE, EYE_RIM, LEG, LEG_D, WING, WING_E) = range(16)
HEAD = LEG                        # head black = body black (#3A2E2C); cell 8 = eye front cap (readable at 128 px)
BUDGET = (800, 1100)

V = lambda *a: Vector(a)
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)

# ---------------- design numbers (m), see spec.md ----------------
# dome (elytra): superellipsoid param over an azimuthal domain (a = side, b = back), theta = r * THMAX
G = 0.00025                       # half gap of the split groove (each half shifted by G in x)
RX, RY, RZ = 0.0180, 0.0205, 0.0195
YC = 0.0040
THMAX = math.radians(95.0)        # rim curls slightly under the widest line = overhang over the black body
QZ = 0.85                         # z = RZ * cos^QZ: fuller crown, steeper shoulders
RIM_Z = 0.0095
ZC = RIM_Z + RZ * abs(math.cos(THMAX)) ** QZ
GROOVE_D, BEVEL_A = 0.0006, 0.014 # split edge drop (m) and bevel row offset in domain units
LIP_IN, LIP_UP = 0.0013, 0.0010
RIM_N = 12                        # rim segments per half (24 around)
STEINER = [(0.21, 3), (0.42, 5), (0.62, 8), (0.81, 10)]
SPLIT_B = [-0.9 + 0.225 * i for i in range(9)]
# spots per half: domain centre (a, b), circumradius (m), rotation (deg)
SPOTS = [((0.30, -0.25), 0.0042, 0.0), ((0.72, 0.08), 0.0052, 0.0), ((0.45, 0.66), 0.0042, 10.0), ((0.60, -0.52), 0.0045, 0.0)]
SPOT_MARGIN = 0.07
# body (black underside) and head
BODY_C, BODY_R = V(0, 0.0030, 0.0100), V(0.0155, 0.0190, 0.0058)
HEAD_W, HEAD_H, HEAD_CH, HEAD_Z = 0.0210, 0.0160, 0.0055, 0.0140
HEAD_RINGS = [(-0.0100, 0.80, 0.0), (-0.0170, 1.00, 0.0), (-0.0228, 0.97, 0.0), (-0.0249, 0.95, 0.0010),
              (-0.0258, 0.95, 0.0024)]  # y, scale, inset: double front bevel = rounded octagon block
EYE_X, EYE_Z, EYE_R, EYE_PROUD = 0.0050, 0.0132, 0.0019, 0.0007
# antennae (+X): base on the head top, elbow, club
ANT_BASE = V(0.0045, -0.0195, 0.0210)
ANT_ELBOW = V(0.0074, -0.0207, 0.0272)
ANT_D2 = V(0.78, -0.45, 0.30)
ANT_R, ANT_CLUB = 0.0010, 0.0016
# legs (+X): hip (inside body), knee, ankle, sole on z = 0; radii hip/knee/ankle/sole
# polish round 2: everything except the legs is lowered by DZ (shell close to the ground); legs given in FINAL coords,
# lower segment 0.0066 -> 0.0040 (-39 %), radii +20-24 %
DZ = 0.0020
LEG_SPEC = [('Leg_1', (0.0075, -0.0040, 0.0055), (0.0160, -0.0148, 0.0040), (0.0167, -0.0163, 0.0019), (0.0168, -0.0166, 0.0)),
            ('Leg_2', (0.0080, 0.0010, 0.0055), (0.0196, 0.0005, 0.0040), (0.0203, 0.0000, 0.0019), (0.0204, 0.0000, 0.0)),
            ('Leg_3', (0.0075, 0.0100, 0.0055), (0.0172, 0.0165, 0.0040), (0.0179, 0.0180, 0.0019), (0.0180, 0.0183, 0.0))]
LEG_RAD = (0.0025, 0.0026, 0.0028, 0.0030)        # chunky shin, foot block flares to a flat sole
# underwings (+X): root, tip, half chord at root/mid/tip, half thickness
WING_ROOT, WING_TIP = V(0.0035, -0.0020, 0.0108), V(0.0062, 0.0255, 0.0084)
WING_ST, WING_T = ((0.0, 0.0015), (0.5, 0.0040), (0.88, 0.0034), (1.0, 0.0018)), 0.0003   # blunt rounded tip


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return (a + ['INS-03', 'build'])[:2]


def mirv(p):
    return Vector((-p.x, p.y, p.z))


def mir(rings):
    return [[mirv(p) for p in r] for r in rings]


# ---------------- copied helpers (bee) ----------------
def qball(P, cname, c, r, thetas, n, slot_fn, ph=0.0):
    R = []
    for th in thetas:
        t = math.radians(th)
        R.append([P.bm.verts.new(c + V(r.x * math.sin(t) * math.cos(math.radians(ph + 360.0 * k / n)),
                                       r.y * math.sin(t) * math.sin(math.radians(ph + 360.0 * k / n)), r.z * math.cos(t)))
                  for k in range(n)])
    faces = []

    def add(vs):
        p = sum((v.co for v in vs), Vector()) / len(vs)
        faces.append(P.face(vs, slot_fn(p)))
    for j in range(len(R) - 1):
        for k in range(n):
            add([R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]])
    add(list(reversed(R[0]))); add(list(R[-1]))
    P.comp.append((cname, faces, False))
    return faces


def tube_rings(pts, radii, n, ref, phase=0.0, flat_end=False):
    rings = []
    for i, p in enumerate(pts):
        if i == 0: t = (pts[1] - pts[0]).normalized(); k = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); k = 1.0
        else:
            d0 = (pts[i] - pts[i - 1]).normalized(); d1 = (pts[i + 1] - pts[i]).normalized()
            t = (d0 + d1).normalized(); k = 1.0 / max(0.5, t.dot(d1))
        _, e1, e2 = pc.basis(t, ref)
        bd = None                                   # exact mitre: stretch only along the bend direction
        if 0 < i < len(pts) - 1:
            bd = (d1 - d0) - t * (d1 - d0).dot(t)
            bd = bd.normalized() if bd.length > 1e-9 else None
        ring = []
        for j in range(n):
            a = phase + 2 * math.pi * j / n
            o = e1 * (radii[i] * math.cos(a)) + e2 * (radii[i] * math.sin(a))
            if bd is not None: o = o + bd * (o.dot(bd) * (k - 1.0))
            ring.append(p + o)
        if flat_end and i == len(pts) - 1:
            ring = [v - t * (v.z / t.z) for v in ring]
        rings.append(ring)
    return rings


# ---------------- elytra (dome half via constrained Delaunay) ----------------
def dome(a, b):
    r = math.hypot(a, b); ph = math.atan2(b, a) if r > 1e-12 else 0.0
    th = r * THMAX; s, c = math.sin(th), math.cos(th)
    fz = math.copysign(abs(c) ** QZ, c)
    return V(G + RX * s * math.cos(ph), YC + RY * s * math.sin(ph), ZC + RZ * fz)


def dome_frame(a, b, h=1e-4):
    p = dome(a, b)
    da = (dome(a + h, b) - dome(a - h, b)) / (2 * h); db = (dome(a, b + h) - dome(a, b - h)) / (2 * h)
    n = da.cross(db).normalized()
    if n.dot(p - V(G, YC, ZC)) < 0: n = -n
    return p, da, db, n


def elytron(P, name):
    """+X half as world points; returns component faces and hinge point. Mirrored for .R by the caller."""
    verts2, pos3, kind = [], [], []

    def add(a, b, p3, k):
        verts2.append(Vector((a, b))); pos3.append(p3); kind.append(k); return len(verts2) - 1
    # rim arc (phi -90 .. 90) - endpoints are the split endpoints
    rim = []
    for k in range(RIM_N + 1):
        ph = math.radians(-90 + 180.0 * k / RIM_N); a, b = math.cos(ph), math.sin(ph)
        if k in (0, RIM_N): a = 0.0
        rim.append(add(a, b, dome(a, b), 'rim'))
    # split row (lowered towards the dome centre inside the x = G plane) and bevel row
    split, bevel = [], []
    for b in SPLIT_B:
        p = dome(0.0, b); q = V(0, (p.y - YC) / RY ** 2, (p.z - ZC) / RZ ** 2).normalized()
        split.append(add(0.0, b, p - q * GROOVE_D, 'split'))
    for b in SPLIT_B:
        bevel.append(add(BEVEL_A, b, dome(BEVEL_A, b), 'bevel'))
    # spots: regular hexagons in the tangent plane -> domain via pseudo-inverse -> flattened on one plane
    spot_faces, spot_info = [], []
    for (ca, cb), R, rot in SPOTS:
        p0, da, db, n = dome_frame(ca, cb)
        JtJi = Matrix(((da.dot(da), da.dot(db)), (da.dot(db), db.dot(db)))).inverted()   # pseudo-inverse of [da db]
        t1 = db.normalized(); t2 = n.cross(t1).normalized()
        dom = []
        for k in range(6):
            al = math.radians(rot + 60 * k); o = (t1 * math.cos(al) + t2 * math.sin(al)) * R
            d = JtJi @ Vector((da.dot(o), db.dot(o))); dom.append((ca + d[0], cb + d[1]))
        pts3 = [dome(u, v) for u, v in dom]
        mean = sum(pts3, Vector()) / 6
        flat = lambda q: q - n * (q - mean).dot(n)
        ids = [add(u, v, flat(q), 'spot') for (u, v), q in zip(dom, pts3)]
        cid = add(ca, cb, flat(p0), 'spot')
        rr = max(math.hypot(u - ca, v - cb) for u, v in dom)
        spot_faces.append(ids); spot_info.append((ca, cb, rr))
    # Steiner rings (skip near the split/bevel and inside spot margins)
    for r, nn in STEINER:
        for k in range(nn):
            ph = math.radians(-90 + 180.0 * (k + 0.5) / nn); a, b = r * math.cos(ph), r * math.sin(ph)
            if a < BEVEL_A + 0.07: continue
            if any(math.hypot(a - ca, b - cb) < rr + SPOT_MARGIN for ca, cb, rr in spot_info): continue
            add(a, b, dome(a, b), 'in')
    outer = rim + list(reversed(split))
    faces_in = [outer] + spot_faces
    edges_in = [(bevel[i], bevel[i + 1]) for i in range(len(bevel) - 1)]
    out = delaunay_2d_cdt(verts2, edges_in, faces_in, 1, 1e-7)
    ov, oe, of, o_verts, o_edges, o_faces = out
    assert len(ov) == len(verts2), ('CDT added vertices', len(ov), len(verts2))
    imap = [ovs[0] for ovs in o_verts]          # output vertex -> input index
    bv = [P.bm.verts.new(pos3[i]) for i in range(len(verts2))]
    faces = []
    spot_set = set(range(1, 1 + len(SPOTS)))
    for fi, f in enumerate(of):
        ids = [imap[i] for i in f]
        vs = [bv[i] for i in ids]
        c = sum((pos3[i] for i in ids), Vector()) / 3
        nrm = (pos3[ids[1]] - pos3[ids[0]]).cross(pos3[ids[2]] - pos3[ids[0]])
        if nrm.length < 1e-14: continue
        nrm.normalize()
        if nrm.dot(c - V(G, YC, ZC)) < 0: vs = vs[::-1]; nrm = -nrm
        if set(o_faces[fi]) & spot_set: slot = SPOT if nrm.z > 0.45 else SPOT_D
        elif all(kind[i] in ('split', 'bevel') or i in (rim[0], rim[-1]) for i in ids): slot = GROOVE
        elif nrm.z > 0.80: slot = R_TOP
        elif nrm.z > 0.45: slot = R_MID
        elif nrm.z > 0.05: slot = R_LOW
        else: slot = R_RIM
        faces.append(P.face(vs, slot))
    # lip band + underside cap + split wall (closed solid)
    lip = []
    for i in rim:
        p = pos3[i]; q = V((p.x - G) / RX ** 2, (p.y - YC) / RY ** 2, 0).normalized()
        lp = p - q * LIP_IN + V(0, 0, LIP_UP)
        lp.x = max(lp.x, G)
        lip.append(P.bm.verts.new(lp))
    lip[0].co.x = lip[-1].co.x = G
    rv = [bv[i] for i in rim]
    for k in range(RIM_N):
        faces.append(P.face([rv[k + 1], rv[k], lip[k], lip[k + 1]], R_RIM))
    faces.append(P.face(list(reversed(lip)), UNDER))
    wall = [rv[0]] + [bv[i] for i in split] + [rv[-1], lip[-1], lip[0]]
    faces.append(P.face(wall, UNDER))
    P.comp.append((name, faces, False))
    hinge = pos3[split[1]].copy()               # top-front of the split (b = -0.675)
    return faces, hinge


def mirror_component(P, src_name, dst_name):
    faces = next(f for nm, f, _ in P.comp if nm == src_name)
    vm = {}; out = []
    for f in faces:
        vs = []
        for v in f.verts:
            if v not in vm: vm[v] = P.bm.verts.new(mirv(v.co))
            vs.append(vm[v])
        out.append(P.face(list(reversed(vs)), f[P.slot]))
    P.comp.append((dst_name, out, False))


# ---------------- mesh ----------------
def build_mesh():
    P = pc.Part('Ladybug')
    J = {}
    # elytra
    _, hinge = elytron(P, 'Elytra.L')
    mirror_component(P, 'Elytra.L', 'Elytra.R')
    J['Elytra.L'] = hinge; J['Elytra.R'] = mirv(hinge)
    # body
    qball(P, 'Body', BODY_C, BODY_R, [30, 70, 110, 150], 10, lambda p: LEG_D if (p - BODY_C).z < -0.6 * BODY_R.z else LEG)
    J['Body'] = BODY_C.copy()
    # head: octagon loft along -Y with a front bevel
    rings = []
    for y, s, d in HEAD_RINGS:
        prof = pc.chamf_rect(HEAD_W * s - 2 * d, HEAD_H * s - 2 * d, max(HEAD_CH * s - d * math.tan(math.pi / 8), 0.3 * HEAD_CH))
        rings.append([V(x, y, HEAD_Z + z) for x, z in prof])

    def head_side(j, k):
        a = rings[j][k]; b = rings[j][(k + 1) % 8]; c = rings[j + 1][k]
        n = (b - a).cross(c - a).normalized()
        mid = (a + b) / 2
        if n.dot(mid - V(0, mid.y, HEAD_Z)) < 0: n = -n
        return HEAD_L if n.z > 0.5 else HEAD
    P.loft('Head', rings, head_side, HEAD, HEAD)
    J['Head'] = V(0, -0.0120, HEAD_Z)
    # eyes: 8-gon proud discs with a bevel, back buried in the head
    yf = HEAD_RINGS[-1][0]
    for nm, sx in (('Eye.L', 1), ('Eye.R', -1)):
        c = V(sx * EYE_X, 0, EYE_Z)
        er = []
        for y, r in ((yf + 0.0010, EYE_R), (yf - EYE_PROUD, EYE_R), (yf - EYE_PROUD - 0.00035, EYE_R * 0.72)):
            er.append([V(c.x + r * math.cos(math.pi / 8 + 2 * math.pi * k / 8), y, c.z + r * math.sin(math.pi / 8 + 2 * math.pi * k / 8))
                       for k in range(8)])
        if sx < 0: er = [list(reversed(r)) for r in er]
        P.loft(nm, er, lambda j, k: EYE_RIM if j == 0 else EYE, EYE, EYE_C)
        J[nm] = V(c.x, yf, c.z)
    # antennae: 6-gon tubes, elbow, club tip
    d2 = ANT_D2.normalized()
    neck = ANT_ELBOW + d2 * 0.0011; ca = neck + d2 * 0.0006; cb = ca + d2 * 0.0020; tip = cb + d2 * 0.0006
    pts = [ANT_BASE, ANT_ELBOW, neck, ca, cb, tip]
    ar = tube_rings(pts, [ANT_R, ANT_R, ANT_R, ANT_CLUB, ANT_CLUB, ANT_R * 1.05], 6, Y, 0.0)
    P.loft('Antenna.L', ar, LEG, LEG, LEG); P.loft('Antenna.R', [list(reversed(r)) for r in mir(ar)], LEG, LEG, LEG)
    J['Antenna.L'] = ANT_BASE + Z * 0.001; J['Antenna.R'] = mirv(J['Antenna.L'])
    # lower everything built so far (shell, body, head, eyes, antennae) by DZ; legs/wings below use final coords
    for nm, faces, _ in P.comp:
        for v in {v for f in faces for v in f.verts}: v.co.z -= DZ
    for k in J: J[k] = J[k] - V(0, 0, DZ)
    # legs: hip -> knee -> flared foot, flat sole
    for nm, hip, knee, ank, sole in LEG_SPEC:
        lr = tube_rings([V(*hip), V(*knee), V(*ank), V(*sole)], LEG_RAD, 6, Y, math.pi / 6, flat_end=True)
        side = lambda j, k: LEG_D if j == 2 else LEG
        P.loft(nm + '.L', lr, side, LEG, LEG_D)
        P.loft(nm + '.R', [list(reversed(r)) for r in mir(lr)], side, LEG, LEG_D)
        J[nm + '.L'] = V(*hip); J[nm + '.R'] = mirv(V(*hip))
    # underwings: thin plates folded under the elytra, tip out behind the rim
    wroot, wtip = WING_ROOT - V(0, 0, DZ), WING_TIP - V(0, 0, DZ)
    ax = (wtip - wroot)
    wr = []
    for t, w in WING_ST:
        c = wroot + ax * t
        wr.append([c - X * w, c + Z * WING_T, c + X * w, c - Z * WING_T])
    wside = lambda j, k: WING_E if j == len(WING_ST) - 2 else WING
    P.loft('Wing.L', wr, wside, WING, WING_E)
    P.loft('Wing.R', [list(reversed(r)) for r in mir(wr)], wside, WING, WING_E)
    J['Wing.L'] = wroot.copy(); J['Wing.R'] = mirv(wroot)
    return P, J


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


def split_to_objects(P, coll, mat, root, joints):
    groups = {}
    for nm, faces, _ in P.comp: groups.setdefault(nm, []).extend(faces)
    obs = {}
    for nm, faces in groups.items():
        piv = joints[nm]
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


def coplanar_all(P, coll, scale=1.0, tri=False):
    b2 = P.bm.copy()
    if tri: bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3])
    for v in b2.verts: v.co *= scale
    me = bpy.data.meshes.new('TMP_All'); b2.to_mesh(me); b2.free()
    ob = bpy.data.objects.new('TMP_All', me); coll.objects.link(ob)
    n, s = pc.coplanar_overlaps(ob)
    for a, b in s[:4]:
        print('   coplanar pair at', [tuple(round(c / scale, 4) for c in me.polygons[i].center) for i in (a, b)])
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def coplanar_true(P, eps=1e-5, pen=2e-7):
    """(copied from the mouse) triangles in one plane (|d| < 0.01 mm) that really overlap in 2D (SAT)"""
    b2 = P.bm.copy()
    bmesh.ops.triangulate(b2, faces=[f for f in b2.faces if len(f.verts) > 3])
    b2.faces.ensure_lookup_table(); b2.normal_update()
    tree = BVHTree.FromBMesh(b2); bad = set()
    tris = [[v.co.copy() for v in f.verts] for f in b2.faces]

    def sat(A, B, n):
        _, u, w = pc.basis(n, (1, 0, 0) if abs(n.x) < 0.9 else (0, 1, 0))
        a = [(p.dot(u), p.dot(w)) for p in A]; b = [(p.dot(u), p.dot(w)) for p in B]
        for poly in (a, b):
            for i in range(3):
                (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % 3]
                ax, ay = y1 - y0, x0 - x1; ln = math.hypot(ax, ay)
                if ln < 1e-12: return False
                pa = [(x * ax + y * ay) / ln for x, y in a]; pb = [(x * ax + y * ay) / ln for x, y in b]
                if min(max(pa), max(pb)) - max(min(pa), min(pb)) < pen: return False
        return True
    for f in b2.faces:
        if f.calc_area() < 1e-12: continue
        c = f.calc_center_median(); n = f.normal; rr = max((v.co - c).length for v in f.verts)
        for co, nn, idx, d in tree.find_nearest_range(c, rr * 1.01):
            if idx is None or idx <= f.index: continue
            g = b2.faces[idx]
            if abs(abs(g.normal.dot(n)) - 1) > 1e-4 or abs((g.calc_center_median() - c).dot(n)) > eps: continue
            if sat(tris[f.index], tris[idx], n): bad.add((f.index, idx))
    b2.free()
    print(f'  coplanar_true (plane < {eps*1000:.2f} mm, real 2D overlap): {len(bad)} pairs')
    return len(bad)


def build(tex_dir):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)     # factory-startup cube/light/camera
    coll = bpy.data.collections.get(ASSET) or bpy.data.collections.new(ASSET)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    P, J = build_mesh()
    bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
    com, vol = com_of(P.bm)
    minz = min(v.co.z for v in P.bm.verts)
    sh = Vector((0, -com.y, -minz))                # root pivot = ground under the centre of mass, soles on z = 0
    for v in P.bm.verts: v.co += sh
    for k in J: J[k] = J[k] + sh
    print(f'COM before shift {tuple(round(c, 4) for c in com)} volume {vol * 1e6:.3f} cm3 -> shift {tuple(round(c, 4) for c in sh)}')
    chk = pc.comp_checks(P)
    # legs must clear the shell (Walk bends them; Open_Wings lifts the elytra): BVH overlap + nearest distance
    P.bm.verts.index_update(); allp = [v.co.copy() for v in P.bm.verts]
    tree = lambda nm: BVHTree.FromPolygons(allp, [[v.index for v in f.verts] for f in next(fs for n, fs, _ in P.comp if n == nm)])
    el = [tree('Elytra.L'), tree('Elytra.R')]
    for nm, faces, _ in P.comp:
        if not nm.startswith('Leg'): continue
        t = tree(nm); hit = any(t.overlap(e) for e in el)
        dmin = min(e.find_nearest(v.co)[3] for e in el for v in {v for f in faces for v in f.verts})
        print(f'  LEG CLEARANCE {nm}: intersects elytra {hit}, min distance {dmin * 1000:.2f} mm')
    tri = tris_by_part(P)
    print('coplanar, shared check on the quad/ngon mesh (real scale):')
    cop = coplanar_all(P, coll)
    print('coplanar, shared check on a x10 copy (tiny model: the shared check skips faces < 1 mm2):')
    cop10 = coplanar_all(P, coll, 10.0)
    print('coplanar, shared check on the triangulated x10 copy:')
    cop10t = coplanar_all(P, coll, 10.0, tri=True)
    copt = coplanar_true(P)
    os.makedirs(tex_dir, exist_ok=True)
    img = pc.atlas_image('T_' + TAG + '_BaseColor', os.path.join(tex_dir, 'T_' + TAG + '_BaseColor.png'), PALETTE)
    mat = pc.material('M_' + TAG, img)
    root = bpy.data.objects.new(ASSET, None); coll.objects.link(root); root.empty_display_size = 0.02
    obs = split_to_objects(P, coll, mat, root, J)
    P.bm.free()
    bpy.context.view_layer.update()
    print('TRIS per part:')
    for nm in sorted(tri): print(f'   {nm:12s} {tri[nm]:4d}')
    tot = pc.report(obs)
    print(f'TRIS total {tot} | target ~{BUDGET[0]}, cap {BUDGET[1]}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    body = [o.matrix_world @ v.co for k in ('Head', 'Elytra.L', 'Elytra.R') for o in [obs[k]] for v in o.data.vertices]
    dm = [o.matrix_world @ v.co for k in ('Elytra.L', 'Elytra.R') for o in [obs[k]] for v in o.data.vertices]
    print(f'SIZE span(x) {hi[0]-lo[0]:.4f} length(y) {hi[1]-lo[1]:.4f} height(z) {hi[2]-lo[2]:.4f} | lowest z {lo[2]:.6f} | '
          f'body length head->dome {max(p.y for p in body) - min(p.y for p in body):.4f} dome width {max(p.x for p in dm) - min(p.x for p in dm):.4f}'
          f' dome top {max(p.z for p in dm):.4f} rim z {min(p.z for p in dm):.4f}')
    print('PIVOTS', {k: tuple(round(c, 4) for c in o.matrix_world.translation) for k, o in obs.items() if k.startswith(('Elytra', 'Wing', 'Head'))})
    print(f'CHECKS non-manifold {chk["nonmanifold"]} loose {chk["loose"]} degenerate {chk["degenerate"]} coplanar {cop} x10 {cop10} '
          f'x10tri {cop10t} true {copt} mirror {chk["mirror"]:.6f} worst gap {chk["gap"][0]:.5f} {chk["gap"][1]} problems {chk["problems"]}')
    return dict(sc=sc, coll=coll, root=root, obs=obs, mat=mat, img=img, checks=chk, coplanar=cop, tris=tri, total=tot)


REF_VIEW = (0.72, -1.0, 0.45)      # reference: ladybug faces image-left, we see the face and its left (+X) flank
VIEWS = [REF_VIEW, (1, 0, 0.04), (0.0, -1, 0.10), (0.0, 1, 0.12), (0.02, 0.01, 1.0), (-0.8, 0.9, 0.45), (-0.9, -0.8, 0.3)]


def check_render(B, tag='build'):
    os.makedirs(CHECK, exist_ok=True)
    sc = B['sc']; rn.setup_workbench(sc, 600, 400)
    g = rn.ground(sc); cam = rn.camera(sc, lens=70); cam.data.clip_start = 0.002
    objs = list(B['obs'].values()); pts = rn.mesh_points(objs)
    tiles = []
    for view in VIEWS:
        rn.fit(sc, cam, pts, view, (0.86, 0.86))
        p = rn.render_to(sc, os.path.join(CHECK, f'tile_{len(tiles)}.png')); tiles.append(rn.load_px(p))
    out = rn.compose([rn.ref_tile(REF, 400)] + tiles, 4, os.path.join(CHECK, f'Ladybug_{tag}_sheet.png'))
    sc.render.resolution_x, sc.render.resolution_y = 128, 128
    rn.fit(sc, cam, pts, REF_VIEW, (0.9, 0.9))
    rn.render_to(sc, os.path.join(CHECK, f'Ladybug_{tag}_128.png'))
    for i in range(len(tiles)): os.remove(os.path.join(CHECK, f'tile_{i}.png'))
    bpy.data.objects.remove(g, do_unlink=True)
    return out


# ---------------- preview (copied from the bee: no hover, shadow kept in frame, near clip) -------
# pack standard (as Mouse/Hedgehog/Cat): low 3/4 from the front-left, ~10 deg above the ground, sky + horizon in frame
PREVIEW_VIEW, PREVIEW_FILL = (0.85, -1.30, 0.315), (0.70, 0.76)   # ~11.5 deg up: split line reads, horizon stays in frame
PREVIEW_LENS = 35                          # a bit wider than the mouse's 40 mm so the horizon stays in at 11.5 deg
SUN_ROT = (48, 0, -35)                     # pack sun; angle 3 deg = finer shadow at insect scale


def preview(sc, root, objs, out):
    r = sc.render
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    old_samples = sc.eevee.taa_render_samples; sc.eevee.taa_render_samples = 128
    w = bpy.data.worlds.new('TMP_PreviewWorld'); w.use_nodes = True; nt = w.node_tree
    out_n = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    L = rn._lin
    ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (L('e3'), L('ec'), L('f2'), 1)
    ramp.color_ramp.elements[1].position = 0.45; ramp.color_ramp.elements[1].color = (L('86'), L('b4'), L('de'), 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.80, 0.86, 0.96, 1)
    amb.inputs['Strength'].default_value = 0.55
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out_n.inputs['Surface'])
    old_world = sc.world; sc.world = w
    me = bpy.data.meshes.new('TMP_Meadow'); n = 48; R = 60.0
    me.from_pydata([(0, 0, 0)] + [(R * math.cos(2 * math.pi * k / n), R * math.sin(2 * math.pi * k / n), 0) for k in range(n)], [],
                   [(0, k + 1, (k + 1) % n + 1) for k in range(n)])
    me.materials.append(rn._solid_mat('TMP_Meadow_M', '#93AE6E'))
    gob = bpy.data.objects.new('TMP_Meadow', me); sc.collection.objects.link(gob)
    lights = []
    for nm, rot, e, shd in (('TMP_Sun', SUN_ROT, 3.6, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(3); ld.use_shadow = shd
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]
        sc.collection.objects.link(ob); lights.append(ob)
    cam = rn.camera(sc, 'TMP_PrevCam', PREVIEW_LENS); cam.data.clip_start = 0.002
    pts = rn.mesh_points(objs)
    rn.fit(sc, cam, pts, PREVIEW_VIEW, PREVIEW_FILL)             # model fills the frame (shadow not in the fit, as Mouse)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights + [gob, cam]:
        d = ob.data; bpy.data.objects.remove(ob, do_unlink=True)
        if isinstance(d, bpy.types.Light): bpy.data.lights.remove(d)
        elif isinstance(d, bpy.types.Camera): bpy.data.cameras.remove(d)
        elif isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    sc.world = old_world; bpy.data.worlds.remove(w); sc.eevee.taa_render_samples = old_samples
    print('preview', out)


if __name__ == '__main__':
    ID, CMD = args()
    print('=== INS-03 Ladybug', CMD)
    if CMD == 'build':
        B = build(os.path.join(CHECK, 'tex'))
        check_render(B)
    elif CMD == 'look':
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(CHECK, 'Ladybug_look.png'))
    elif CMD in ('preview', 'preview_check'):
        # preview only (mesh/FBX/blend/atlas in art untouched; texture for the render goes to the check folder)
        B = build(os.path.join(CHECK, 'tex')); os.makedirs(CHECK, exist_ok=True)
        out = os.path.join(CHECK, 'Ladybug_prev_check.png') if CMD == 'preview_check' else os.path.join(ART, ASSET + '_Preview.png')
        preview(B['sc'], B['root'], list(B['obs'].values()), out)
        if CMD == 'preview_check':                                   # 128 px thumbnail of the preview
            im = bpy.data.images.load(out); im.scale(128, 80)
            im.filepath_raw = os.path.join(CHECK, 'Ladybug_prev_128.png'); im.file_format = 'PNG'; im.save()
    elif CMD == 'export':
        B = build(os.path.join(ART, 'Textures'))
        for d in ('Meshes', 'Blend'): os.makedirs(os.path.join(ART, d), exist_ok=True)
        fbx = pc.export(ASSET, B['coll'], B['root'], os.path.join(ART, 'Meshes', ASSET + '.fbx'))
        fbm = os.path.join(ART, 'Meshes', ASSET + '.fbm', 'T_' + TAG + '_BaseColor.png')
        print('fbm texture', fbm, os.path.isfile(fbm))
        pc.verify(fbx)
        pc.save_lib(os.path.join(ART, 'Blend', ASSET + '.blend'), B['coll'], B['mat'], B['img'])
        preview(B['sc'], B['root'], list(B['obs'].values()), os.path.join(ART, ASSET + '_Preview.png'))
