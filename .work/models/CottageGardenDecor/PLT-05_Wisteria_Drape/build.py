# build.py - PLT-05 Wisteria Drape (FMS_Garden_Wisteria_Drape), pack CottageGardenDecor (Cottage Garden Decor),
# atlas F Garden_Flora (read only: the shared PNG is loaded, never rewritten), material M_Garden_Flora.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- PLT-05 build|export|dump
#   build  = build + printed checks (ATTACH, MOUNT on the approved STR-04 FBX) + check renders to %TEMP%/assetnew_check/PLT-05/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\PLT-05_Wisteria_Drape\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['PLT-05', 'build']})
#   Live mode touches only the collection PLT-05_Wisteria_Drape (+ temporary TMP_ scenes that are removed again).
#
# Axes (Blender): X = along the beam (1.5), -Y = front (Unity +Z after the -Z-forward export), Z = up (Unity Y).
# TOP plane Blender Z = 0 (Unity Y = 0) = ATTACHMENT PLANE: everything hangs below it. Pivot (0, 0, 0) = centre of the
# top face; mounted pivot at the STR-04 beam underside (Unity Y 2.24).
# Organic generators copied from PLT-02 build.py (= PLT-01 accepted pass 3): ring, leaf_cluster, add_bmesh.
import bpy, bmesh, math, os, sys, json, hashlib, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'PLT-05')
COLL = 'PLT-05_Wisteria_Drape'
NAME = 'FMS_Garden_Wisteria_Drape'
PREVIEW = 'FMS_Garden_PLT_05_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasF.png'
ATLAS_MAT = 'M_Garden_Flora'
PERGOLA_FBX = 'FMS_Garden_Pergola.fbx'          # STR-04, mounting check only (read)
BUDGET = 900
PAL_F = ['#6E9F4A', '#8AB257', '#4E7A3A', '#3F6B3A',
         '#C8473B', '#A8372E', '#E58FA0', '#F2B8C2',
         '#F4F1E8', '#A58BC9', '#3A3A3F', '#E8B83A',
         '#805433', '#7A5233', '#A7A39A', '#C9C3B6']
LEAF, LEAF_UP, LEAF_DN = 0, 1, 2
WHITE, LILAC, BARK = 8, 9, 13
STUB = LEAF_DN                                  # green stalk (review lesson: no brown lollipop stalks); see notes
# ----------------------------------------
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'PLT-05'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
TAU = 2 * math.pi


# ============ organic generators (copied from PLT-02 build.py = PLT-01, unchanged) ============
def ring(O, a, r, n, a0, ref=(1, 0, 0)):
    a = Vector(a).normalized(); ref = Vector(ref)
    if abs(a.dot(ref.normalized())) > 0.9: ref = Vector((0, 1, 0))
    t, e1, e2 = pc.basis(a, ref)
    angs = [a0 + TAU * k / n for k in range(n)]
    return [O + e1 * (r * math.cos(g)) + e2 * (r * math.sin(g)) for g in angs], angs


def leaf_cluster(c, D, seed, H=0.80, widest=0.40, noise=0.035, sub=2, under_k=0.85, up=0.6, down=-0.2):
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
    slots = {f: (LEAF_UP if f.normal.z > up else (LEAF_DN if f.normal.z < down else LEAF)) for f in bm.faces}
    return bm, slots


def add_bmesh(P, cname, bm, slots, comp):
    vm = {v: P.bm.verts.new(v.co) for v in bm.verts}
    comp[cname] = [P.face([vm[v] for v in f.verts], slots[f]) for f in bm.faces]


# ============ PLT-05 specific ============
SLOT_UP, SLOT_DN = 0.55, -0.62                 # normal.z thresholds for light / dark foliage on the hanging drops


TH_TOP = math.radians(125)                      # the cut ring sits 35 deg above the ball's equator (rounded shoulders)


def hang_cluster(c, D, seed, Rv, kd, clip, noise=0.035):
    """Hanging LEAF CLUSTER (series 80-tri domed drop, cut in half): one hemisphere of the PLT-01 icosphere (subdiv 2,
    40 tris, random Z spin + noise +-0.035 as in leaf_cluster) is mapped onto a ball whose top is cut off: polar angle
    from the bottom pole stretched so the hemisphere's equator lands at TH_TOP (above the ball's equator, so the ball
    has rounded shoulders like the reference), horizontal radius D / 2, vertical radius Rv, depth (Y) scaled by kd.
    The cut ring (10 verts) lies exactly on Z = clip and is closed with one face (flattened against the beam): 48 tris.
    c = (x, y) of the ball; returns bm, slots (from the final normals)."""
    rnd = random.Random(seed)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rnd.uniform(0, TAU), 3, 'Z'))
    cz = clip + math.cos(TH_TOP) * Rv                    # ball centre (cos(125) < 0: centre below the cut)
    lower = []; eq = []
    for v in bm.verts:
        zo = max(-1.0, min(1.0, v.co.z)); az = math.atan2(v.co.y, v.co.x)
        n = Vector([rnd.uniform(-noise, noise) for _ in range(3)])
        if zo < -1e-4: lower.append(v); continue
        th = math.acos(zo) * TH_TOP / (math.pi / 2)
        v.co = Vector((c[0] + math.sin(th) * math.cos(az) * D / 2 + n.x,
                       c[1] + (math.sin(th) * math.sin(az) * D / 2 + n.y) * kd,
                       cz - math.cos(th) * Rv + n.z))
        if abs(zo) <= 1e-4: eq.append(v)
    assert len(eq) == 10, len(eq)
    bmesh.ops.delete(bm, geom=lower, context='VERTS')
    for v in eq: v.co.z = clip
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    slots = {f: (LEAF_UP if f.normal.z > SLOT_UP else (LEAF_DN if f.normal.z < SLOT_DN else LEAF)) for f in bm.faces}
    for f in bm.faces:                                   # the cut face (against the beam): mid green, not a lit lid
        if f.normal.z > 0.999 and all(abs(v.co.z - clip) < 1e-9 for v in f.verts): slots[f] = LEAF
    return bm, slots


def prism(P, pts, r, n, a0, slot, ref=(0, 0, 1)):
    """n-sided prism along pts (mitred rings), both ends capped (closed shell)"""
    pts = [Vector(q) for q in pts]; rings = []
    for i, q in enumerate(pts):
        if i == 0: d = pts[1] - pts[0]
        elif i == len(pts) - 1: d = pts[-1] - pts[-2]
        else: d = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        rr = r[i] if isinstance(r, (list, tuple)) else r
        rings.append(ring(q, d, rr, n, a0, ref=ref)[0])
    R = [[P.bm.verts.new(v) for v in rg] for rg in rings]; faces = []
    for j in range(len(R) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], slot))
    faces.append(P.face(list(reversed(R[0])), slot)); faces.append(P.face(list(R[-1]), slot))
    return faces


# raceme: 6-sided "two beads + tip" (reference): flat hex top, upper bead (belt), waist, lower bead (belt), tip point.
# (fraction of the body length, radius at the reference long raceme); radii scale with the body length. 46 tris.
RAC_RINGS = [(0.00, 0.064), (0.17, 0.102), (0.42, 0.058), (0.60, 0.084)]
SPECKLE_TIP = True                              # lilac racemes: every 3rd facet of the tip cone (lower section) white (spec)


def raceme(P, top, L, axis, spin, slot, speckle=False):
    a = Vector(axis).normalized(); top = Vector(top)
    s = max(0.92, min(1.12, 0.92 + 0.20 * (L - 0.36) / 0.24))
    R = [[P.bm.verts.new(v) for v in ring(top + a * (t * L), a, r * s, 6, spin, ref=(1, 0, 0))[0]] for t, r in RAC_RINGS]
    tip = P.bm.verts.new(top + a * L)
    f = [P.face(list(reversed(R[0])), slot)]
    for j in range(len(R) - 1):
        for k in range(6):
            k1 = (k + 1) % 6
            f.append(P.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], slot))
    for k in range(6):
        sl = WHITE if speckle and SPECKLE_TIP and k % 3 == 0 else slot
        f.append(P.face([R[-1][k], R[-1][(k + 1) % 6], tip], sl))
    return f


# racemes: X (spec; ends +-0.62 as measured on the reference), side (+1 back = +Y, -1 front = -Y), tip Z (reference,
# 777 px/m: band top 300 px), white. Each hangs straight under the bottom of its own leaf cluster.
RACEMES = [  # x, side, z_tip, white
    (-0.62, +1, -0.624, False),
    (-0.46, -1, -0.856, False),
    (-0.28, +1, -0.573, False),
    (-0.09, -1, -0.744, True),
    (+0.10, +1, -0.605, False),
    (+0.28, -1, -0.817, False),
    (+0.46, +1, -0.579, True),
    (+0.62, -1, -0.705, False),
]
RAC_Y = 0.12                                    # racemes at Y +-0.12 (spec +-0.20: see notes)
CL_Y = 0.065                                    # their clusters at Y +-0.065: front and back drops merge into one band
RAC_TILT = 4.0                                  # deg, alternating (spec +-5)

# vines: 4-sided bars (reference: flat lit top + darker side), 4 segments each; A behind (+Y), B in front (-Y), zigzag in Z
# out of phase so that they cross each other in the front view (weave), slight Y swing.
VINE_X = [-0.66, -0.33, 0.0, 0.33, 0.66]               # ends inside the end clusters
VINE_A = [(x, 0.02 + 0.11 * (k % 2), -0.10 - 0.13 * (k % 2)) for k, x in enumerate(VINE_X)]
VINE_B = [(x, -0.02 - 0.11 * ((k + 1) % 2), -0.10 - 0.13 * ((k + 1) % 2)) for k, x in enumerate(VINE_X)]
VINE_R = 0.035                                  # 4-sided: 0.05 across the flats (spec Ø0.05)
STUB_R = 0.018                                  # 3-sided stalk (8 tris), ~0.027 across

# one cluster over each raceme: (D, Rv, seed); ball bottom = -(1 - cos TH_TOP) Rv = -1.574 Rv; back ones higher, front lower
CLUSTERS = [
    (0.26, 0.150, 51),
    (0.31, 0.195, 52),
    (0.30, 0.150, 53),
    (0.30, 0.185, 54),
    (0.30, 0.155, 55),
    (0.31, 0.190, 56),
    (0.29, 0.150, 57),
    (0.27, 0.180, 58),
]
CL_ABOVE = 0.035                                # visible stalk between the dome bottom and the raceme top
CL_KD = 1.0                                     # depth scale (Y)
CLIPS = (0.0, -0.0015)                          # flat tops alternate 0 / -1.5 mm: neighbours never coplanar


def vine_at(V, x):
    for (x0, y0, z0), (x1, y1, z1) in zip(V[:-1], V[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0); return Vector((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t))
    raise ValueError(x)


def build_drape():
    P = Part('Body'); comp = {}; tops = []
    for i, (D, Rv, seed) in enumerate(CLUSTERS):
        x, side = RACEMES[i][0], RACEMES[i][1]
        bm, slots = hang_cluster((x, side * CL_Y), D, seed, Rv, CL_KD, CLIPS[i % 2])
        tree = BVHTree.FromBMesh(bm)                     # raceme top: CL_ABOVE under the dome over the whole top ring
        zs = [tree.ray_cast(Vector((x + 0.075 * math.cos(g), side * RAC_Y + 0.075 * math.sin(g), -2.0)), Vector((0, 0, 1)))[0]
              for g in [TAU * k / 12 for k in range(12)] + [None] if g is not None]
        zs = [h.z for h in zs if h] + [h.z for h in [tree.ray_cast(Vector((x, side * RAC_Y, -2.0)), Vector((0, 0, 1)))[0]] if h]
        tops.append(min(zs) - CL_ABOVE)
        add_bmesh(P, f'Cluster_{i}', bm, slots, comp); bm.free()
    comp['Vine_A'] = prism(P, VINE_A, VINE_R, 4, math.pi / 4, BARK)
    comp['Vine_B'] = prism(P, VINE_B, VINE_R, 4, math.pi / 4, BARK)
    stubs = []
    for i, (x, side, ztip, white) in enumerate(RACEMES):
        V = VINE_A if side > 0 else VINE_B
        pv = vine_at(V, x)
        zt = tops[i]
        top = Vector((x, side * RAC_Y, zt))
        a = Matrix.Rotation(math.radians(RAC_TILT * (1 if i % 2 else -1)), 3, 'Y') @ Vector((0, 0, -1))
        L = (zt - ztip) / -a.z
        comp[f'Raceme_{i}'] = raceme(P, top, L, a, 0.35 * i, WHITE if white else LILAC, speckle=not white)
        p1 = top + a * 0.012                                     # stalk ends 12 mm inside the raceme top
        comp[f'Stub_{i}'] = prism(P, [pv, p1], STUB_R, 3, math.pi / 2, STUB, ref=(0, -1, 0))
        d = p1 - pv
        stubs.append((i, round(zt, 3), round(L, 3), round(d.length, 3), round(math.degrees(math.acos(max(-1, min(1, -d.z / d.length)))), 1)))
    print('  racemes (i, top z, body L, stalk length, stalk deg from vertical):', stubs)
    for cn in comp:
        P.comp.append((cn, comp[cn], False))
    return P


def overlaps(P, prefix_a, prefix_b):
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    trees = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp
             if nm.startswith(prefix_a) or nm.startswith(prefix_b)}
    out = []; names = sorted(trees)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a.startswith(prefix_a) and b.startswith(prefix_b) or a.startswith(prefix_b) and b.startswith(prefix_a):
                if trees[a].overlap(trees[b]): out.append((a, b))
    return out


def raceme_gaps(P):
    """min distance between every pair of racemes (vertex -> other mesh); spec: >= 0.04"""
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    R = {nm: fs for nm, fs, _ in P.comp if nm.startswith('Raceme_')}
    T = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs in R.items()}
    worst = (9.0, None)
    names = sorted(R)
    for i, a in enumerate(names):
        va = {v for f in R[a] for v in f.verts}
        for b in names[i + 1:]:
            d = min(T[b].find_nearest(v.co)[3] for v in va)
            if d < worst[0]: worst = (d, (a, b))
    print(f'  raceme gap min {worst[0]:.4f} {worst[1]}', 'OK' if worst[0] >= 0.04 else 'FAIL')
    return worst


def stalk_contacts(P):
    """each stalk overlaps its vine and its raceme (no floating raceme)"""
    bm = P.bm; bm.verts.index_update(); pos = [v.co.copy() for v in bm.verts]
    tree = {nm: BVHTree.FromPolygons(pos, [[v.index for v in f.verts] for f in fs]) for nm, fs, _ in P.comp}
    bad = []
    for i, (x, side, *_r) in enumerate(RACEMES):
        s = tree[f'Stub_{i}']; vn = 'Vine_A' if side > 0 else 'Vine_B'
        if not s.overlap(tree[vn]): bad.append((i, vn))
        if not s.overlap(tree[f'Raceme_{i}']): bad.append((i, 'raceme'))
    print('  stalk contacts (vine + raceme):', 'OK' if not bad else f'FAIL {bad}')
    return not bad


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
    return coll


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
    if mat is None:                                                   # headless: same setup as PLT-01
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('_')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def attach_checks(ob):
    """top attachment plane + catalogue envelope (pivot on the top face, hangs under the beam)"""
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    me = ob.data
    top_area = sum(p.area for p in me.polygons if p.normal.z > 0.999 and
                   all(abs((ob.matrix_world @ me.vertices[i].co).z) < 1e-6 for i in p.vertices))
    beam_strip = sum(1 for p in me.polygons if p.normal.z > 0.999 and abs(p.center.z) < 1e-6 and abs(p.center.y) <= 0.05)
    rows = [
        ('nothing above the attachment plane (max Z <= 0)', z1, z1 <= 1e-6),
        ('top flush (max Z = 0)', z1, abs(z1) <= 1e-6),
        ('flat top faces on Z = 0 (m2)', top_area, top_area > 0.02),
        ('flat top faces centred under the 0.10 beam (|y| <= 0.05)', beam_strip, beam_strip > 0),
        ('length X <= 1.5 + 0.02', x1 - x0, x1 - x0 <= 1.52),
        ('depth Y <= 0.6 + 0.02', y1 - y0, y1 - y0 <= 0.62),
        ('hang <= 0.90 (tip >= 1.34 under a 2.24 beam)', -z0, -z0 <= 0.90 + 1e-6),
        ('pivot X centred (|x0 + x1| / 2 <= 0.02)', (x0 + x1) / 2, abs(x0 + x1) / 2 <= 0.02),
        ('pivot Y centred (|y0 + y1| / 2 <= 0.03)', (y0 + y1) / 2, abs(y0 + y1) / 2 <= 0.03),
    ]
    ok = all(r[2] for r in rows)
    for nm, v, g in rows: print(f'  ATTACH {nm}: {v:.4f} {"OK" if g else "FAIL"}')
    print('ATTACH OK' if ok else 'ATTACH FAIL')
    return ok


def mount_check(ob, render_to=None):
    """approved STR-04 FBX imported read-only into a temporary scene; the drape pivot placed on each beam's underside
    centre line. Checks: top flush with the underside, flat top under the beam, nothing inside the beam or the posts,
    within the beam length, clear of the posts, lowest tip height."""
    win = bpy.context.window
    prev = win.scene if win else bpy.context.scene
    vl_prev = bpy.context.view_layer
    sel = [o.name for o in vl_prev.objects if o.select_get()]; act = vl_prev.objects.active.name if vl_prev.objects.active else None
    sc = bpy.data.scenes.new('TMP_PLT05_Mount')
    if win: win.scene = sc
    before_o, before_i, before_m, before_me = set(bpy.data.objects), set(bpy.data.images), set(bpy.data.materials), set(bpy.data.meshes)
    bpy.ops.import_scene.fbx(filepath=os.path.join(ART, 'Meshes', PERGOLA_FBX))
    bpy.context.view_layer.update()
    per = [o for o in bpy.data.objects if o not in before_o]
    beams = next(o for o in per if o.type == 'MESH' and o.name.endswith('_Beams'))
    posts = next(o for o in per if o.type == 'MESH' and o.name.endswith('_Posts'))
    bv = [beams.matrix_world @ v.co for v in beams.data.vertices]
    pv = [posts.matrix_world @ v.co for v in posts.data.vertices]
    dv = [ob.matrix_world @ v.co for v in ob.data.vertices]
    ok = True; mounted = []
    for side in (-1, 1):
        b = [p for p in bv if p.y * side > 0]
        yc = (min(p.y for p in b) + max(p.y for p in b)) / 2; zu = min(p.z for p in b)
        bx0, bx1 = min(p.x for p in b), max(p.x for p in b); by0, by1 = min(p.y for p in b), max(p.y for p in b)
        off = Vector((0, yc, zu)); q = [p + off for p in dv]
        top = max(p.z for p in q)
        inside_beam = sum(1 for p in q if bx0 < p.x < bx1 and by0 < p.y < by1 and p.z > zu + 1e-5)
        flush = sum(1 for p in q if abs(p.z - zu) < 1e-5 and by0 <= p.y <= by1)
        px = [p for p in pv if p.y * side > 0]
        post_hits = 0
        for cx in sorted({round(p.x, 2) for p in px}):
            cp = [p for p in px if abs(p.x - cx) < 0.2]
            if not cp: continue
            ax0, ax1 = min(p.x for p in cp), max(p.x for p in cp); ay0, ay1 = min(p.y for p in cp), max(p.y for p in cp)
            post_hits += sum(1 for p in q if ax0 < p.x < ax1 and ay0 < p.y < ay1)
        post_clear = min(min(abs(p.x - c.x) for c in px) for p in q) - 0.0
        lo = min(p.z for p in q)
        rows = [(f'beam y {yc:+.3f}: underside z', zu, abs(zu - 2.24) < 1e-3),
                ('drape top = underside', top - zu, abs(top - zu) < 1e-6),
                ('drape vertices flush on the underside within the beam width', flush, flush > 0),
                ('drape vertices inside the beam', inside_beam, inside_beam == 0),
                ('drape within the beam length', min(p.x for p in q) - bx0, min(p.x for p in q) >= bx0 and max(p.x for p in q) <= bx1),
                ('drape vertices inside posts', post_hits, post_hits == 0),
                ('lowest tip above ground', lo, lo >= 1.30)]
        for nm, v, g in rows:
            print(f'  MOUNT {nm}: {v:.4f} {"OK" if g else "FAIL"}'); ok &= g
        mounted.append(off)
    if render_to:
        gs = []
        for off in mounted:
            g = bpy.data.objects.new('TMP_PLT05_Mounted', ob.data); g.matrix_world = Matrix.Translation(off)
            sc.collection.objects.link(g); gs.append(g)
        bpy.context.view_layer.update()
        render([o for o in per if o.type == 'MESH'] + gs, render_to, (0.9, -1.6, 0.35), res=(1200, 900), fill_w=0.85,
               fill_h=0.9, center=True)
        for g in gs: bpy.data.objects.remove(g, do_unlink=True)
    for o in per:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    for m in set(bpy.data.materials) - before_m:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - before_i:
        if i.users == 0: bpy.data.images.remove(i)
    if win: win.scene = prev
    bpy.data.scenes.remove(sc)
    vl = bpy.context.view_layer
    for o in vl.objects: o.select_set(o.name in sel)
    if act and act in vl.objects: vl.objects.active = vl.objects[act]
    print('MOUNT OK' if ok else 'MOUNT FAIL')
    return ok


def build():
    coll = clear_own()
    img, mat = atlas_readonly()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P = build_drape()
    pt = part_tris(P)
    ov_rr = overlaps(P, 'Raceme_', 'Raceme_')
    ov_rc = overlaps(P, 'Raceme_', 'Cluster_')
    gap = raceme_gaps(P); st = stalk_contacts(P)
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=tuple(nm for nm, _, _ in P.comp))
    bpy.context.view_layer.update()
    tot = pc.report({P.name: ob})
    n_cop, _ = pc.coplanar_overlaps(ob)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'x{tot / BUDGET:.2f}')
    print('  parts (tris):', pt, '| racemes touching', ov_rr, '| raceme in cluster', ov_rc)
    attach_checks(ob)
    return coll, root, ob, img, mat, tot


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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), center=False):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_PLT05_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_PLT05_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_PLT05_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_PLT05_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_PLT05_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_PLT05_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_PLT05_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    if center:
        target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    else:
        target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2))
    dv = Vector(view_dir).normalized()
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


VIEW_REF = (0.0, -1.0, 0.12)                                                    # reference: front, slightly above
VIEW_PREVIEW = (1.0, -1.25, 0.75)                                               # series preview 3/4 (~25 deg)
VIEW_UNDER = (0.5, -1.0, -0.45)                                                 # player under the pergola

coll, root, ob, img, mat, tot = build()
os.makedirs(CHECK_DIR, exist_ok=True)
base_objs = [root, ob]
tag = 'live' if LIVE else 'headless'
if MODE in ('build', 'export'):
    mount_check(ob, os.path.join(CHECK_DIR, f'PLT-05_check_mounted_{tag}.png') if MODE == 'build' else None)
if MODE == 'build':
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-05_check_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.93, fill_h=0.6)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-05_check34_{tag}.png'), VIEW_PREVIEW)
    render(base_objs, os.path.join(CHECK_DIR, f'PLT-05_checkunder_{tag}.png'), VIEW_UNDER)
if MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    vl = bpy.context.view_layer                                  # live: the owner's selection is saved and restored
    sel = [o.name for o in vl.objects if o.select_get()]; act = vl.objects.active.name if vl.objects.active else None
    try:
        fbx = pc.export(NAME, coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    finally:
        for o in vl.objects: o.select_set(o.name in sel)
        vl.objects.active = vl.objects[act] if act and act in vl.objects else None
        print('  selection restored', sel, act)
    save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
    render(base_objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
    pc.verify(fbx)
if MODE in ('export', 'dump'):
    geom_dump([ob], os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
