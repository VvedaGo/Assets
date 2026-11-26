# build.py - PLT-04 Ivy Patch (FMS_Garden_Ivy_Patch), pack CottageGardenDecor (Cottage Garden Decor),
# atlas F Garden_Flora (read only: the shared PNG is loaded, never rewritten).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- PLT-04 build|export
#   build  = build + printed checks + MOUNT proof (MOD-03 / MOD-01 FBX, read-only, headless only)
#            + check renders to %TEMP%/assetnew_check/PLT-04/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\PLT-04_Ivy_Patch\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['PLT-04', 'build']})
#   Live mode touches only the collection PLT-04_Ivy_Patch.
#
# Axes (Blender): X = width, -Y = front (Unity +Z with the -Z-forward FBX export; leaves grow toward it), Z = up.
# Back plane Blender Y = 0 (Unity Z = 0) = ATTACHMENT PLANE: nothing at Y > 0. Pivot (0, 0, 0) = centre of the bottom
# edge on the back plane. "out" below = distance in front of the plane (= -Y).
# Parts: Mat (back layer as ONE closed shell: a diamond tiling of 25 flat-based rhombus pyramids sharing their base edges,
# closed by one flat back face on Y = 0), middle leaves (slot 2), front leaves (slot 0, up to 4 with slot 1 on upward
# faces), vines (slot 13). Leaf = closed rhombus pyramid (4 front tris + 2 base tris), faceted as in the reference.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'PLT-04')
COLL = 'PLT-04_Ivy_Patch'
NAME = 'FMS_Garden_Ivy_Patch'
PREVIEW = 'FMS_Garden_PLT_04_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'
ATLAS_MAT = 'M_Garden_Flora'
BUDGET = 500
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
FRONT, LIGHT, MIDDLE, BACK, BARK = 0, 1, 2, 3, 13
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'PLT-04'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi
OUT = Vector((0, -1, 0))                       # "out of the wall" direction


def P3(x, out, z):
    return Vector((x, -out, z))


# ============ back layer: one closed diamond-tiled mat ============
MAT_A, MAT_B = 0.25, 0.24                      # diamond width (X) and height (Z)
MAT_Z0 = 0.03                                  # bottom tips of the lowest row (leaf tips hang below it)
MAT_ROWS = 7                                   # odd rows: 4 diamonds (x +-0.125, +-0.375), even rows: 3 (0, +-0.25)
MAT_IN_OUT = 0.012                             # interior base vertices raised off the plane (the shell keeps thickness)
MAT_APEX = (0.040, 0.056)                      # apex height range (out)
MAT_JIT = 0.022                                # in-plane jitter of the lattice vertices (shared, so the tiling stays closed)
SEED_MAT = 4104


def build_mat(P):
    rnd = random.Random(SEED_MAT)
    cells = []
    for j in range(1, MAT_ROWS + 1):
        zc = MAT_Z0 + j * MAT_B / 2
        xs = [-0.375, -0.125, 0.125, 0.375] if j % 2 else [-0.25, 0.0, 0.25]
        cells += [(x, zc) for x in xs]
    key = lambda x, z: (round(x * 1000), round(z * 1000))
    quads = []                                                    # (bottom, right, top, left) keys
    for x, z in cells:
        quads.append((key(x, z - MAT_B / 2), key(x + MAT_A / 2, z), key(x, z + MAT_B / 2), key(x - MAT_A / 2, z)))
    edge_use = {}
    for q in quads:
        for i in range(4):
            e = tuple(sorted((q[i], q[(i + 1) % 4]))); edge_use[e] = edge_use.get(e, 0) + 1
    boundary = {k for e, n in edge_use.items() if n == 1 for k in e}
    pos = {}
    for k in sorted({k for q in quads for k in q}):
        jit = MAT_JIT * (1.5 if k in boundary else 1.0)
        x = k[0] / 1000 + rnd.uniform(-jit, jit); z = k[1] / 1000 + rnd.uniform(-jit, jit)
        x = max(-0.52, min(0.52, x))
        pos[k] = P.bm.verts.new(P3(x, 0.0 if k in boundary else MAT_IN_OUT, z))
    faces = []
    for (x, z), q in zip(cells, quads):
        cx = sum(pos[k].co.x for k in q) / 4; cz = sum(pos[k].co.z for k in q) / 4
        ap = P.bm.verts.new(P3(cx + rnd.uniform(-0.02, 0.02), rnd.uniform(*MAT_APEX), cz - 0.015 + rnd.uniform(-0.015, 0.015)))
        for i in range(4):
            faces.append(P.face([pos[q[i]], pos[q[(i + 1) % 4]], ap], BACK))
    # back face: walk the boundary loop (edges used once) and close it with one flat polygon on Y = 0
    bnd = [e for e in P.bm.edges if len(e.link_faces) == 1 and all(v in pos.values() for v in e.verts)]
    nxt = {}
    for e in bnd:
        f = e.link_faces[0]
        lp = next(l for l in f.loops if l.edge == e)              # loop direction inside the front face
        nxt[lp.link_loop_next.vert] = lp.vert                     # reversed for the back face
    start = next(iter(nxt)); loop = [start]
    while True:
        v = nxt[loop[-1]]
        if v is start: break
        loop.append(v)
    assert len(loop) == len(nxt), 'mat boundary is not one loop'
    faces.append(P.face(loop, BACK))
    P.comp.append(('Mat', faces, False))
    return len(loop)


# ============ leaves ============
def leaf(P, c_x, c_z, L, W, theta, pitch, stem_out, h, slot, light=None, max_out=0.148, box=(-0.54, 0.54, 0.0, 1.07)):
    """closed rhombus pyramid (6 tris): base rhombus L x W, long axis pointing down (theta deg from straight down,
    + = toward +X), pitched out of the wall plane by 'pitch' (tip away from the wall), apex h above the base centre.
    Shifted into the box (X, Z) and pulled back so nothing passes max_out."""
    th, pt = math.radians(theta), math.radians(pitch)
    d0 = Vector((math.sin(th), 0, -math.cos(th)))
    d = (d0 * math.cos(pt) + OUT * math.sin(pt)).normalized()
    side = Vector((math.cos(th), 0, math.sin(th)))
    n = d.cross(side).normalized()
    if n.dot(OUT) < 0: n = -n
    c = P3(c_x, 0, c_z) + OUT * stem_out + d * (L / 2)
    pts = [c - d * (L / 2), c + side * (W / 2), c + d * (L / 2), c - side * (W / 2), c + n * h - d * (0.06 * L)]
    dx = max(0.0, box[0] - min(p.x for p in pts)) - max(0.0, max(p.x for p in pts) - box[1])
    dz = max(0.0, box[2] - min(p.z for p in pts)) - max(0.0, max(p.z for p in pts) - box[3])
    dy = max(0.0, max(-p.y for p in pts) - max_out)
    pts = [p + Vector((dx, dy, dz)) for p in pts]
    vs = [P.bm.verts.new(p) for p in pts]
    s, r, t, l, a = vs
    def sl(tri):
        if light is None: return slot
        nn = (tri[1].co - tri[0].co).cross(tri[2].co - tri[0].co).normalized()
        if nn.dot(OUT) < 0: nn = -nn
        return light if nn.z > 0.30 else slot
    tris = [(s, r, a), (r, t, a), (t, l, a), (l, s, a)]
    faces = [P.face(list(tr), sl(tr)) for tr in tris]
    faces += [P.face([s, t, r], slot), P.face([s, l, t], slot)]   # flat base (toward the wall), orientation fixed later
    return faces


SEED_MID, SEED_FRONT = 4204, 4304
VINE_X = (-0.30, 0.05, 0.32)


def leaf_layout():
    """middle: staggered 4 x 5 jittered grid (20); front: staggered 4/4 x 6 jittered grid (24), the opposite phase.
    Sizes from the reference (750 px/m): leaves 0.17-0.26 long, nearly square diamonds."""
    out = []
    rnd = random.Random(SEED_MID)
    for row in range(5):
        z = 0.13 + row * 0.19
        for col in range(4):
            x = -0.40 + col * 0.25 + (0.15 if row % 2 else 0.0)
            if x > 0.52: x -= 1.0
            out.append(('Mid', x + rnd.uniform(-0.04, 0.04), z + rnd.uniform(-0.04, 0.04),
                        rnd.uniform(0.17, 0.21), rnd.uniform(0.15, 0.19), rnd.uniform(-30, 30), rnd.uniform(10, 18),
                        rnd.uniform(0.016, 0.03), rnd.uniform(0.024, 0.030), MIDDLE))
    rnd = random.Random(SEED_FRONT)
    for row in range(6):
        z = 0.13 + row * 0.16
        for col in range(4):
            x = -0.33 + col * 0.24 + (-0.06 if row % 2 else 0.06)    # half-step stagger (no stacked look-alikes)
            out.append(('Front', x + rnd.uniform(-0.04, 0.04), z + rnd.uniform(-0.03, 0.03),
                        rnd.uniform(0.19, 0.25), rnd.uniform(0.18, 0.23), rnd.uniform(-30, 30), rnd.uniform(8, 15),
                        rnd.uniform(0.055, 0.07), rnd.uniform(0.028, 0.034), FRONT))
    # a hole in the middle layer on the centre vine (spec: vines visible in gaps); 19 middle leaves remain
    mids = [o for o in out if o[0] == 'Mid']
    out.remove(min(mids, key=lambda o: (o[1] - VINE_X[1]) ** 2 + (o[2] - 0.5) ** 2))
    return out


LIGHT_LEAVES = (2, 9, 15, 20)                  # front-leaf indices that get slot 1 on their upward faces


# ============ vines ============
VINE_R = 0.020                                 # 3-sided prism, circumradius 0.02 (face to the wall, ridge to the front)
VINE_OUT = 0.025
VINE_Z = (0.10, 0.90)
VINE_SEG = 6
VINE_ZIG = 0.030


def vine(P, x0, seed):
    rnd = random.Random(seed)
    pts = []
    for i in range(VINE_SEG + 1):
        z = VINE_Z[0] + (VINE_Z[1] - VINE_Z[0]) * i / VINE_SEG + rnd.uniform(-0.03, 0.03)
        x = x0 + (VINE_ZIG if i % 2 else -VINE_ZIG) + rnd.uniform(-0.01, 0.01)
        pts.append(P3(x, VINE_OUT, z))
    rings = []
    for i, q in enumerate(pts):
        if i == 0: dd = pts[1] - pts[0]
        elif i == len(pts) - 1: dd = pts[-1] - pts[-2]
        else: dd = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        t, e1, e2 = pc.basis(dd, (0, -1, 0))
        rings.append([P.bm.verts.new(q + e1 * (VINE_R * math.cos(TAU * k / 3)) + e2 * (VINE_R * math.sin(TAU * k / 3)))
                      for k in range(3)])
    faces = []
    for j in range(len(rings) - 1):
        for k in range(3):
            k1 = (k + 1) % 3
            faces.append(P.face([rings[j][k], rings[j][k1], rings[j + 1][k1], rings[j + 1][k]], BARK))
    faces.append(P.face(list(reversed(rings[0])), BARK)); faces.append(P.face(list(rings[-1]), BARK))
    return faces


def settle(P, faces, step=0.0025, min_back=0.012):
    """no floating leaves: push a leaf toward the wall (+Y) in 2.5 mm steps until it overlaps the geometry built before it
    (mat, vines, earlier leaves); its back-most vertex stays >= min_back in front of the plane."""
    own = set(faces); vs = list({v for f in faces for v in f.verts})
    others = [f for f in P.bm.faces if f not in own]
    P.bm.verts.index_update()
    pos = [v.co.copy() for v in P.bm.verts]
    tree = BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in others])
    onrm = [f.normal.copy() if f.normal.length > 0.5 else (f.verts[1].co - f.verts[0].co).cross(f.verts[2].co - f.verts[0].co).normalized()
            for f in others]
    ocen = [f.calc_center_median() for f in others]
    def near_coplanar():                                          # a face of this leaf within 2 mm of a parallel foreign face
        for f in faces:
            n = (f.verts[1].co - f.verts[0].co).cross(f.verts[2].co - f.verts[0].co).normalized()
            c = sum((v.co for v in f.verts), Vector()) / len(f.verts)
            for co, nn, idx, d in tree.find_nearest_range(c, 0.03):
                if abs(abs(onrm[idx].dot(n)) - 1) < 1e-3 and abs((ocen[idx] - c).dot(n)) < 0.002: return True
        return False
    moved = 0.0
    for _ in range(60):
        mine = BVHTree.FromPolygons([v.co for v in vs], [[vs.index(v) for v in f.verts] for f in faces])
        if tree.overlap(mine) and not near_coplanar(): return moved
        if max(v.co.y for v in vs) + step <= -min_back:
            for v in vs: v.co.y += step
            moved += step
        else:                                                     # over a notch of the mat edge: slide inward (X)
            sx = -0.005 if sum(v.co.x for v in vs) > 0 else 0.005
            for v in vs: v.co.x += sx
            moved += 0.005
    print('  WARNING leaf could not settle (floating)')
    return moved


def build_ivy():
    P = Part('Body')
    nb = build_mat(P)
    print('  mat boundary verts', nb)
    for i, x0 in enumerate(VINE_X):
        P.comp.append((f'Vine_{i}', vine(P, x0, 4400 + i), False))
    fi = 0
    for i, (kind, x, z, L, W, th, pit, so, h, slot) in enumerate(leaf_layout()):
        light = None
        if kind == 'Front':
            light = LIGHT if fi in LIGHT_LEAVES else None; fi += 1
        fs = leaf(P, x, z, L, W, th, pit, so, h, slot, light)
        mv = settle(P, fs)
        if mv > 0: print(f'  {kind}_{i:02d} settled {mv:.3f} toward the wall')
        P.comp.append((f'{kind}_{i:02d}', fs, False))
    return P


# ============ scene / atlas / helpers ============
def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return [coll]


def atlas_readonly():
    """shared atlas F: load the existing PNG (never generated or saved here); check the cell colours against PAL_F"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None or os.path.normcase(os.path.abspath(bpy.path.abspath(img.filepath))) != os.path.normcase(path):
        img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels[:]); bad = []
    for s, h in enumerate(PAL_F):
        col, row = s % 4, s // 4; x = col * 64 + 32; y = (3 - row) * 64 + 32; i = (y * 256 + x) * 4
        want = [int(h[k:k + 2], 16) for k in (1, 3, 5)]; got = [round(c * 255) for c in px[i:i + 3]]
        if max(abs(a - b) for a, b in zip(want, got)) > 2: bad.append((s, h, got))
    print('  atlas F', path, 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:                                                   # headless: same setup as PLT-01/02
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def attach_checks(ob):
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    ymax, ymin = max(p.y for p in pts), min(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    me = ob.data
    back = [p for p in me.polygons if abs(p.normal.y - 1) < 1e-6 and all(abs(me.vertices[i].co.y) < 1e-6 for i in p.vertices)]
    other = [p for p in me.polygons if p.normal.y > 0.999 and p not in back]
    area = sum(p.area for p in back)
    rows = [
        ('nothing behind the attachment plane (max Y <= 0)', ymax, ymax <= 1e-6),
        ('flat back on the plane: tris with normal +Y on Y = 0', len(back), len(back) > 0),
        ('back area m2 (one flat face, triangulated; covers the patch)', area, area > 0.70),
        ('other faces parallel to the back plane (coplanar risk)', len(other), True),
        ('depth (front) <= 0.15', -ymin, -ymin <= 0.15 + 1e-6),
        ('width <= 1.0 + 2 x 0.04 tips', x1 - x0, x1 - x0 <= 1.08 + 1e-6),
        ('height <= 1.0 + 0.04 tips', z1 - z0, z1 - z0 <= 1.04 + 1e-6),
        ('pivot X centred (|x0 + x1| / 2 <= 0.02)', (x0 + x1) / 2, abs(x0 + x1) / 2 <= 0.02),
        ('bottom edge at the pivot (min z = 0)', z0, abs(z0) <= 1e-6),
    ]
    ok = all(r[2] for r in rows)
    for nm, v, g in rows: print(f'  ATTACH {nm}: {v:.4f} {"OK" if g else "FAIL"}')
    print('ATTACH OK' if ok else 'ATTACH FAIL')
    return ok


def inside(bvh, q):
    n_hit = 0; o = Vector(q)
    for _ in range(40):
        h = bvh.ray_cast(o + Vector((0, 0, 1e-5)), Vector((0, 0, 1)))
        if h[0] is None: break
        n_hit += 1; o = h[0]
    return n_hit % 2 == 1


def mount_check(ob):
    """MOUNT proof against the approved module FBX (imported read-only, removed afterwards; headless only):
    MOD-03 wall: back plane on the coping front face (Y -0.22, the wall body face is 0.20), pivot on the ground;
    MOD-01 lattice: back plane on the panel face (Y -0.03), pivot at z 0.40 (patch inside the frame 0.05-1.80).
    Gap back plane <-> module face 1 mm (joint tolerance 0 +- 1 mm), no patch vertex inside the module, no overlap."""
    if LIVE:
        print('MOUNT skipped in live mode (proved by the headless run)'); return None
    pv = [ob.matrix_world @ v.co for v in ob.data.vertices]
    pf = [list(p.vertices) for p in ob.data.polygons]
    px0, px1 = min(p.x for p in pv), max(p.x for p in pv); pz1 = max(p.z for p in pv)
    allok = True
    for tag, fbx, z_off, frame in (('MOD-03', 'FMS_Garden_Wall_Stone.fbx', 0.0, None),
                                   ('MOD-01', 'FMS_Garden_Lattice_Panel.fbx', 0.40, (-0.94, 0.94, 0.05, 1.80))):
        path = os.path.join(ART, 'Meshes', fbx)
        before_o, before_m, before_i = set(bpy.data.objects), set(bpy.data.materials), set(bpy.data.images)
        bpy.ops.import_scene.fbx(filepath=path)
        new = [o for o in bpy.data.objects if o not in before_o]
        bpy.context.view_layer.update()
        mv, mf = [], []
        for o in new:
            if o.type != 'MESH': continue
            base = len(mv); mv += [o.matrix_world @ v.co for v in o.data.vertices]
            mf += [[base + i for i in p.vertices] for p in o.data.polygons]
        bm_mod = BVHTree.FromPolygons(mv, mf)
        def face_y(z_lo, z_hi):                                   # nearest module surface seen from the front (rays +Y)
            hits = []
            for i in range(41):
                for k in range(41):
                    x = px0 + (px1 - px0) * i / 40; z = z_lo + (z_hi - z_lo) * k / 40
                    h = bm_mod.ray_cast(Vector((x, -5.0, z)), Vector((0, 1, 0)))
                    if h[0] is not None: hits.append(h[0].y)
            return min(hits) if hits else float('nan')
        y_face = face_y(z_off, z_off + pz1)
        off = Vector((0, y_face - 0.001, z_off))
        pw = [p + off for p in pv]
        bm_pat = BVHTree.FromPolygons(pw, pf)
        n_in = sum(1 for p in pw if inside(bm_mod, p))
        n_ov = len(bm_mod.overlap(bm_pat))
        gap = y_face - max(p.y for p in pw)
        body_gap = face_y(0.1, 0.5) - max(p.y for p in pw)
        rows = [(f'{tag} module front face Y (in the patch footprint)', y_face, True),
                (f'{tag} gap back plane -> module face (0 +- 1 mm)', gap, 0.0 <= gap <= 0.0011),
                (f'{tag} patch vertices inside the module', n_in, n_in == 0),
                (f'{tag} overlapping face pairs patch/module', n_ov, n_ov == 0)]
        if frame:
            q = [min(p.x for p in pw), max(p.x for p in pw), min(p.z for p in pw), max(p.z for p in pw)]
            rows.append((f'{tag} patch inside the frame (x {q[0]:.3f}..{q[1]:.3f}, z {q[2]:.3f}..{q[3]:.3f})', 0.0,
                         q[0] >= frame[0] and q[1] <= frame[1] and q[2] >= frame[2] and q[3] <= frame[3]))
        else:
            rows.append((f'{tag} two patches side by side (pitch 1.0) cover the 2.0 wall; patch width', px1 - px0,
                         px1 - px0 >= 1.0))
            rows.append((f'{tag} patch top above the cap (0.60) - stands free', pz1 - 0.60, True))
            rows.append((f'{tag} gap to the wall body (face 0.20) at z 0.1-0.5', body_gap, True))
        for nm, v, g in rows: print(f'  MOUNT {nm}: {v:.4f} {"OK" if g else "FAIL"}')
        allok &= all(r[2] for r in rows)
        for o in new:
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
        for m in set(bpy.data.materials) - before_m:
            if m.users == 0: bpy.data.materials.remove(m)
        for i in set(bpy.data.images) - before_i:
            if i.users == 0: bpy.data.images.remove(i)
    print('MOUNT OK' if allok else 'MOUNT FAIL')
    return allok


def build():
    colls = clear_own(); coll = colls[0]
    img, mat = atlas_readonly()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_ivy()
    # pivot: centre of the bottom edge (min z -> 0, X bbox centred)
    vs = P.bm.verts
    zmin = min(v.co.z for v in vs); xc = (min(v.co.x for v in vs) + max(v.co.x for v in vs)) / 2
    for v in vs: v.co -= Vector((xc, 0, zmin))
    pt = part_tris(P)
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris):', pt)
    attach_checks(ob)
    return colls, root, ob, img, mat, tot


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


# ---------------- renders (temporary scene; copied from PLT-02 / WTR-03) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_PLT04_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_PLT04_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_PLT04_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_PLT04_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_PLT04_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_PLT04_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_PLT04_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
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


def save_lib(path, colls, mat, img):
    data = set(colls) | {mat, img}
    for c in colls: data |= set(c.objects) | {o.data for o in c.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


VIEW_REF = (0.30, -1.0, 0.30)                                                   # reference: front, slightly right, ~17 deg above
VIEW_PREVIEW = (1.0, -1.25, 0.75)                                               # series preview 3/4 (~25 deg)

colls, root, ob, img, mat, tot = build()
os.makedirs(CHECK_DIR, exist_ok=True)
base_objs = [root, ob]
if MODE in ('build', 'export'):
    mount_check(ob)
if MODE == 'build':
    tag = 'live' if LIVE else 'headless'
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-04_check_{tag}.png'), VIEW_REF, res=(1000, 1000), fill_w=0.70, fill_h=0.75)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-04_check34_{tag}.png'), VIEW_PREVIEW)
if MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = pc.export(NAME, colls[0], root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
    render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    pc.verify(fbx)
if MODE in ('export', 'dump'):
    geom_dump([ob], os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
