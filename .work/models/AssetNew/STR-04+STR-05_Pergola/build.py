# build.py - STR-04 Pergola 3x3 (FMS_Garden_Pergola) + STR-05 Pergola extension bay 3 m (FMS_Garden_Pergola_Bay),
# pack AssetNew (Cottage Garden Decor), atlas A Garden_Build (read only). One registry script for both modules.
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- STR-04|STR-05 build|export|verify|dump|lodcheck
#   build    = build the model + printed checks (topology, coplanar, ground, tris, functional heights,
#              SNAP STR-04|STR-05 and STR-05|STR-05, PLT-03 garland on a beam) + check renders to %TEMP%/assetnew_check/<ID>/
#   export   = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify   = only re-import the FBX in art/ (run after make_lod1.py)
#   dump     = build + geometry dump only (live/headless comparison)
#   lodcheck = import the FBX (after make_lod1.py) and render LOD0 | LOD1 into the check dir
#   PACK_ART=<dir> redirects the outputs (headless reproduction); the atlas and the PLT-03 FBX are always read from the
#   repo art/AssetNew (read only).
# LOD1: blender.exe --background --factory-startup --python-expr "import sys; sys.dont_write_bytecode=True"
#         --python Tools/blender/make_lod1.py -- --art <ABSOLUTE art/AssetNew> FMS_Garden_Pergola FMS_Garden_Pergola_Bay
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\STR-04+STR-05_Pergola\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-04', 'build']})
#   Live mode touches only the collection STR-04_Pergola / STR-05_Pergola_Bay (+ temporary TMP_* scenes, removed).
# Axes (Blender): Z = up (Unity Y). FBX export -Z forward, Y up: Blender (x, y, z) -> Unity (-x, z, -y)
#   (Unity's FBX import negates X; same convention as STR-01 / MOD-06 notes).
#   Spec X (along the beams)   = Blender -X  -> the bay extends to Blender -X so that it extends to Unity +X.
#   Spec Z (along the rafters) = Blender -Y  (the model is symmetric in Y, so only the sign convention matters).
#   Spec Y (up)                = Blender Z.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART_REPO = os.path.join(REPO, 'art', 'AssetNew')
ART = os.environ.get('PACK_ART') or ART_REPO
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
ROSE_FBX = os.path.join(ART_REPO, 'Meshes', 'FMS_Garden_Rose_Climbing_Top.fbx')   # PLT-03 garland, read only
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D = 0, 1                           # A-0 light wood #B5835A (= STR-01), A-1 dark wood (cut rafter ends)
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-04'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/STR-04.3d.md, STR-05.3d.md; CATALOG «Модули и стыковка» item 5) ----
STEP = 3.0                                    # module step along spec X
P_OFF = 1.5                                   # post centres at spec X +-1.5 (STR-04), Z +-1.5
POST_W, POST_C = 0.18, 0.01                   # post 0.18 square (reference ~0.18; spec minimum 0.16), 0.01 chamfer on the long edges
Z_BEAM0, Z_BEAM1 = 2.24, 2.46                 # beam underside (PLT-05 hangs here) / beam top (PLT-03 rests here)
SEAT = 0.005                                  # posts and rafters seated 5 mm in the beam (no coplanar contact faces)
Z_POST1 = Z_BEAM0 + SEAT                      # post top 2.245, 5 mm inside the beam
BEAM_T = 0.10                                 # beam thickness (spec Z), height 0.22
OVH = 0.25                                    # beam and rafter overhang past the post centres
Z_RAF0, Z_RAF1 = Z_BEAM1 - SEAT, 2.62         # rafter bottom 2.455 (5 mm in the beam), top 2.62 -> section 0.06 x 0.165
RAF_W, RAF_PITCH = 0.08, 0.5                 # rafter 0.08 wide: reference ~0.09 (spec minimum 0.06), see notes
# rafter end: stepped point (side profile, measured from the end): vertical end face E high, steep chamfer to (C1, V1),
# shallow chamfer to (C2, top). Both chamfers start outside the beam (beam outer face 0.20 from the rafter end).
TIP_E, TIP_C1, TIP_V1, TIP_C2 = 0.075, 0.05, 0.125, 0.17


# ---------------- members (pure python: geometry + SNAP use the same list) ----------------
# member = (kind, group, params); all coordinates in the model's own (Blender) space, pivot (0, 0, 0)
def members(mid):
    out = []
    if mid == 'STR-04':
        post_x = (-P_OFF, P_OFF); beam_x = (-P_OFF - OVH, P_OFF + OVH)
        raf_x = [-P_OFF + k * RAF_PITCH for k in range(7)]
    else:                                     # STR-05: shared post line at x = 0 (owned by the neighbour), own posts at -3.0
        post_x = (-STEP,); beam_x = (-STEP - OVH, -OVH)
        raf_x = [-RAF_PITCH * (k + 1) for k in range(6)]
    for x in post_x:
        for y in (-P_OFF, P_OFF):
            out.append(('post', 'Posts', dict(x=x, y=y)))
    for y in (-P_OFF, P_OFF):
        out.append(('beam', 'Beams', dict(x0=beam_x[0], x1=beam_x[1], y=y)))
    for x in raf_x:
        out.append(('rafter', 'Rafters', dict(x=x)))
    return out


def member_bbox(m, off=(0.0, 0.0, 0.0)):
    k, _, p = m; ox, oy, oz = off
    if k == 'post':
        h = POST_W / 2; lo, hi = (p['x'] - h, p['y'] - h, 0.0), (p['x'] + h, p['y'] + h, Z_POST1)
    elif k == 'beam':
        lo, hi = (p['x0'], p['y'] - BEAM_T / 2, Z_BEAM0), (p['x1'], p['y'] + BEAM_T / 2, Z_BEAM1)
    else:
        L = P_OFF + OVH; lo, hi = (p['x'] - RAF_W / 2, -L, Z_RAF0), (p['x'] + RAF_W / 2, L, Z_RAF1)
    return (lo[0] + ox, lo[1] + oy, lo[2] + oz), (hi[0] + ox, hi[1] + oy, hi[2] + oz)


def obox(P, cn, x0, x1, y0, y1, z0, z1, sx, sy, sz, ground=False):
    """axis-aligned box (12 tris), slot per face direction: sx for the +-X faces, sy for +-Y, sz for +-Z"""
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], sz), P.face([v[4], v[5], v[7], v[6]], sz),
          P.face([v[0], v[1], v[5], v[4]], sy), P.face([v[2], v[6], v[7], v[3]], sy),
          P.face([v[0], v[4], v[6], v[2]], sx), P.face([v[1], v[3], v[7], v[5]], sx)]
    P.comp.append((cn, fs, ground))


def rafter_profile():
    """closed side profile (s along the rafter = Blender Y, z) with slot per edge i -> i+1"""
    L = P_OFF + OVH; zb, zt = Z_RAF0, Z_RAF1
    pts = [(-L, zb), (L, zb), (L, zb + TIP_E), (L - TIP_C1, zb + TIP_V1), (L - TIP_C2, zt),
           (-L + TIP_C2, zt), (-L + TIP_C1, zb + TIP_V1), (-L, zb + TIP_E)]
    slots = [WOOD, WOOD_D, WOOD_D, WOOD, WOOD, WOOD, WOOD_D, WOOD_D]   # bottom, end, steep cut, shallow cut, top, ...
    return pts, slots


def add_member(P, m):
    k, grp, p = m
    if k == 'post':
        pc.rect_prism(P, 'Post', p['x'], p['y'], POST_W, POST_W, POST_C, [(0.0, 0), (Z_POST1, 0)], WOOD, WOOD, WOOD,
                      ground=True)
    elif k == 'beam':
        obox(P, 'Beam', p['x0'], p['x1'], p['y'] - BEAM_T / 2, p['y'] + BEAM_T / 2, Z_BEAM0, Z_BEAM1, WOOD, WOOD, WOOD)
    else:
        pts, slots = rafter_profile(); bm = P.bm; n = len(pts)
        a = [bm.verts.new((p['x'] - RAF_W / 2, s, z)) for s, z in pts]
        b = [bm.verts.new((p['x'] + RAF_W / 2, s, z)) for s, z in pts]
        fs = [P.face(list(reversed(a)), WOOD), P.face(list(b), WOOD)]
        for i in range(n):
            j = (i + 1) % n
            fs.append(P.face([a[i], a[j], b[j], b[i]], slots[i]))
        P.comp.append(('Rafter', fs, False))


GROUPS = ('Posts', 'Beams', 'Rafters')        # one mesh object per role: make_lod1 halves each role separately


# ---------------- checks / SNAP (contract: CATALOG «Модули и стыковка» item 5, step 3.0 along spec X) ----------------
def vol_overlap(a, b):
    return all(a[0][j] < b[1][j] - 1e-6 and b[0][j] < a[1][j] - 1e-6 for j in range(3))


def snap_pair(tag, A, offA, B, offB):
    """A = existing part, B = attached bay (B extends to Blender -X = Unity +X)"""
    ok = True
    def row(nm, good, txt=''):
        nonlocal ok; ok &= bool(good); print(f'  SNAP {tag} {nm}: {txt} {"OK" if good else "FAIL"}')
    ma = [(m, member_bbox(m, offA)) for m in members(A)]; mb = [(m, member_bbox(m, offB)) for m in members(B)]
    # beams: butt joint with zero gap, identical sections
    for y in (-P_OFF, P_OFF):
        ba = next(bb for m, bb in ma if m[0] == 'beam' and m[2]['y'] == y)
        bbb = next(bb for m, bb in mb if m[0] == 'beam' and m[2]['y'] == y)
        gap = ba[0][0] - bbb[1][0]
        same = all(abs(ba[i][j] - bbb[i][j]) < 1e-9 for i in (0, 1) for j in (1, 2))
        row(f'beam y={y:+.1f} joint', abs(gap) <= 1e-3 and same,
            f'joint at Blender x {ba[0][0]:.3f} (Unity X {-ba[0][0]:+.3f}), gap {gap * 1000:.3f} mm, same section {same}')
    # posts: no duplicate on the shared line, the bay has none there
    pa = [(round(bb[0][0] + POST_W / 2, 6), round(bb[0][1] + POST_W / 2, 6)) for m, bb in ma if m[0] == 'post']
    pb = [(round(bb[0][0] + POST_W / 2, 6), round(bb[0][1] + POST_W / 2, 6)) for m, bb in mb if m[0] == 'post']
    shared_x = round(offB[0], 6)
    on_line_b = [p for p in pb if abs(p[0] - shared_x) < 1e-6]
    on_line_a = [p for p in pa if abs(p[0] - shared_x) < 1e-6]
    row('posts on the shared line', len(on_line_a) == 2 and not on_line_b and len(set(pa + pb)) == len(pa + pb),
        f'{len(on_line_a)} from {A} + {len(on_line_b)} from {B} at Blender x {shared_x:.2f}; bay posts at x {sorted({p[0] for p in pb})}')
    xs = sorted({p[0] for p in pa + pb})
    row('post line pitch', all(abs((xs[i + 1] - xs[i]) - STEP) < 1e-6 for i in range(len(xs) - 1)), f'lines {xs}')
    # rafters: continuous 0.5 pitch, none duplicated on the shared line
    ra = [round((bb[0][0] + bb[1][0]) / 2, 6) for m, bb in ma + mb if m[0] == 'rafter']
    rs = sorted(ra); d = [round(rs[i + 1] - rs[i], 6) for i in range(len(rs) - 1)]
    row('rafter pitch', len(set(ra)) == len(ra) and all(abs(x - RAF_PITCH) < 1e-6 for x in d),
        f'{len(ra)} rafters, x {rs[0]:.2f}..{rs[-1]:.2f}, pitches {sorted(set(d))}, duplicates {len(ra) - len(set(ra))}')
    # nothing of one module inside the other (touching faces allowed)
    clash = [(m1[0], m2[0]) for m1, b1 in ma for m2, b2 in mb if vol_overlap(b1, b2)]
    row('no volume overlap between the modules', not clash, f'{len(clash)} pairs')
    # heights continue: beam underside / top, rafter top identical
    for k, j, i in (('beam underside', 'beam', 0), ('beam top', 'beam', 1), ('rafter top', 'rafter', 1)):
        za = {round(bb[i][2], 6) for m, bb in ma if m[0] == j}; zb = {round(bb[i][2], 6) for m, bb in mb if m[0] == j}
        row(k, za == zb and len(za) == 1, f'{sorted(za)} / {sorted(zb)}')
    print(f'  SNAP {tag}', 'OK' if ok else 'FAIL')
    return ok


def snap_check(mesh_check=True):
    ok1 = snap_pair('STR-04|STR-05', 'STR-04', (0, 0, 0), 'STR-05', (-1.5, 0, 0))
    ok2 = snap_pair('STR-05|STR-05', 'STR-05', (-1.5, 0, 0), 'STR-05', (-4.5, 0, 0))
    ok3 = True
    if mesh_check:   # real meshes, all three modules merged: coplanar pairs = only the back-to-back beam butt faces
        bm = bmesh.new()
        for mid, off in (('STR-04', (0, 0, 0)), ('STR-05', (-1.5, 0, 0)), ('STR-05', (-4.5, 0, 0))):
            P = Part('tmp')
            for m in members(mid): add_member(P, m)
            bmesh.ops.recalc_face_normals(P.bm, faces=P.bm.faces)
            bmesh.ops.translate(P.bm, vec=Vector(off), verts=P.bm.verts)
            me = bpy.data.meshes.new('TMP_STR04_snap'); P.bm.to_mesh(me); P.bm.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
        me = bpy.data.meshes.new('TMP_STR04_snap_all'); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new('TMP_STR04_snap_all', me)
        n, smp = pc.coplanar_overlaps(ob)
        bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
        ok3 = n == 4
        print(f'  SNAP assembly STR-04 + STR-05 + STR-05 (real meshes): coplanar pairs {n} (want 4 = 2 joints x 2 beams, '
              f'end faces back to back, both hidden) {"OK" if ok3 else "FAIL"}')
    ok = ok1 and ok2 and ok3
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


def functional_checks(obs):
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[j] for p in pts) for j in range(3)]; hi = [max(p[j] for p in pts) for j in range(3)]
    want = dict(STR04=((-1.75, -1.75, 0.0), (1.75, 1.75, 2.62)), STR05=((-3.25, -1.75, 0.0), (-0.25, 1.75, 2.62)))[ID.replace('-', '')]
    good = all(abs(lo[j] - want[0][j]) < 1e-6 and abs(hi[j] - want[1][j]) < 1e-6 for j in range(3))
    print(f'  size {hi[0] - lo[0]:.3f} x {hi[1] - lo[1]:.3f} x {hi[2] - lo[2]:.3f} (Blender X x Y x Z); '
          f'x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} z {lo[2]:.4f}..{hi[2]:.3f} -> {"OK" if good else "FAIL"}')
    bz = [(obs['Beams'].matrix_world @ v.co).z for v in obs['Beams'].data.vertices]
    rz = [(obs['Rafters'].matrix_world @ v.co).z for v in obs['Rafters'].data.vertices]
    print(f'  beam underside {min(bz):.3f} (2.24) top {max(bz):.3f} (2.46); rafter bottom {min(rz):.3f} (seated 5 mm) '
          f'top {max(rz):.3f} (2.62); post section {POST_W} (>= 0.16, reference ~0.18); rafter section {RAF_W} x {Z_RAF1 - Z_RAF0:.3f} (>= 0.06 x 0.16)')
    return good


def all_coplanar(obs):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_STR04_all'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_STR04_all', me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def cross_contacts(obs):
    from mathutils.bvhtree import BVHTree
    trees = {}
    for k, o in obs.items():
        vs = [o.matrix_world @ v.co for v in o.data.vertices]; trees[k] = BVHTree.FromPolygons(vs, [p.vertices for p in o.data.polygons])
    out = {k: [k2 for k2 in obs if k2 != k and trees[k].overlap(trees[k2])] for k in obs}
    print('  part contacts (overlapping/seated parts):', out)
    return out


# ---------------- PLT-03 garland on a beam (catalogue: centred on the beam top, Y 2.46) ----------------
def import_rose(sc_name):
    """import the approved PLT-03 FBX (read only) into a temporary scene; returns (scene, objects, root)"""
    if not os.path.isfile(ROSE_FBX): return None, [], None
    win = bpy.context.window or bpy.context.window_manager.windows[0]
    prev = win.scene; sc = bpy.data.scenes.new(sc_name)
    try:
        win.scene = sc; bpy.ops.import_scene.fbx(filepath=ROSE_FBX); bpy.context.view_layer.update()
    finally:
        win.scene = prev
    obs = list(sc.objects); root = next(o for o in obs if o.parent is None)
    return sc, obs, root


def drop_import(sc, obs, before_mats, before_imgs):
    for o in obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    for m in set(bpy.data.materials) - before_mats:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - before_imgs:
        if i.users == 0: bpy.data.images.remove(i)
    if sc: bpy.data.scenes.remove(sc)


def rose_mount(obs_model, render_to=None):
    beam = next(member_bbox(m) for m in members(ID) if m[0] == 'beam' and m[2]['y'] == -P_OFF)
    cx = (beam[0][0] + beam[1][0]) / 2                # beam middle: STR-04 x 0, STR-05 x -1.75 (span -3.25..-0.25)
    by = -P_OFF                                       # front beam (Blender -Y = Unity +Z front)
    bm_, bi_ = set(bpy.data.materials), set(bpy.data.images)
    sc, robs, root = import_rose('TMP_STR04_Rose')
    if root is None:
        print('  PLT-03 mount: FBX missing', ROSE_FBX, 'FAIL'); return False
    try:
        root.location = (cx, by, Z_BEAM1); sc.view_layers[0].update()
        pts = [o.matrix_world @ v.co for o in robs if o.type == 'MESH' for v in o.data.vertices]
        lo = [min(p[j] for p in pts) for j in range(3)]; hi = [max(p[j] for p in pts) for j in range(3)]
        low = [p for p in pts if p.z < Z_BEAM1 + 0.002]
        beam = next(member_bbox(m) for m in members(ID) if m[0] == 'beam' and m[2]['y'] == by)
        on_beam = all(beam[0][1] - 1e-6 <= p.y <= beam[1][1] + 1e-6 and beam[0][0] <= p.x <= beam[1][0] for p in low)
        inside_len = beam[0][0] <= lo[0] and hi[0] <= beam[1][0]
        raf = [m[2]['x'] for m in members(ID) if m[0] == 'rafter' and lo[0] - RAF_W / 2 < m[2]['x'] < hi[0] + RAF_W / 2]
        ok = abs(lo[2] - Z_BEAM1) <= 1e-3 and on_beam and inside_len and bool(low)
        print(f'  PLT-03 mount on the front beam: pivot ({cx:.2f}, {by:.2f}, {Z_BEAM1}) | garland x {lo[0]:.3f}..{hi[0]:.3f} '
              f'y {lo[1]:.3f}..{hi[1]:.3f} z {lo[2]:.4f}..{hi[2]:.3f} | lowest points ({len(low)} verts within 2 mm of the beam top) '
              f'all over the beam top (y {beam[0][1]:.2f}..{beam[1][1]:.2f}): {on_beam} | within the beam length: {inside_len} | '
              f'passes {len(raf)} rafters at x {raf} (foliage through the rafters, decoration without collider) '
              f'-> {"OK" if ok else "FAIL"}')
        if render_to:
            render(list(obs_model) + robs, render_to, VIEW_REF[ID], res=(1000, 1000), fill_w=0.82, fill_h=0.82)
        return ok
    finally:
        drop_import(sc, robs, bm_, bi_)


# ---------------- registry ----------------
REG = {
    'STR-04': dict(name='FMS_Garden_Pergola', coll='STR-04_Pergola', preview='FMS_Garden_STR_04_Preview.png', budget=1600),
    'STR-05': dict(name='FMS_Garden_Pergola_Bay', coll='STR-05_Pergola_Bay', preview='FMS_Garden_STR_05_Preview.png', budget=1000),
}
CFG = REG.get(ID, REG['STR-04']); NAME = CFG['name']; COLL = CFG['coll']
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)
# views (direction target -> eye). Reference STR-04: front-right 3/4, beams flatter than the rafters (~30 deg above).
# STR-05 reference shows its own posts on the RIGHT: the bay lies at Blender -X, so it is seen from the back-left
# (the module is symmetric in Y, so this is the same picture as the front view of the Unity +X bay).
VIEW_REF = {'STR-04': (0.50, -1.0, 0.66), 'STR-05': (-0.50, 1.0, 0.66)}
VIEW_PREVIEW = {'STR-04': (0.62, -1.0, 0.70), 'STR-05': (-0.62, 1.0, 0.70)}


def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.objects: bpy.data.objects.remove(o, do_unlink=True)
    return coll


def atlas_and_material():
    """reuse the shared atlas A PNG (never rewritten here) and M_Garden_Build (created only when missing)"""
    path = os.path.join(ART_REPO, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(PAL_A):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), img.size[:], 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def cell_of(uv): return min(3, int((1 - uv[1]) * 4)) * 4 + min(3, int(uv[0] * 4))


def to_object(P, asset, coll, mat, root):
    """pc.to_object without its per-Part comp_checks (the parts are split by role, so a single part's members do not
    touch each other; the topology/contact check runs once on the whole model, see build())"""
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = pc.cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    me = bpy.data.meshes.new(asset + '_' + P.name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(asset + '_' + P.name, me); coll.objects.link(ob)
    ob.parent = root; ob.location = (0, 0, 0)
    return ob


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    ms = members(ID)
    print(f'== {ID} {NAME}: {sum(m[0] == "post" for m in ms)} posts, {sum(m[0] == "beam" for m in ms)} beams, '
          f'{sum(m[0] == "rafter" for m in ms)} rafters')
    # whole-model topology / contact / ground / mirror check (one Part with every member as a component)
    W = Part('Whole')
    for m in ms: add_member(W, m)
    bmesh.ops.recalc_face_normals(W.bm, faces=W.bm.faces)
    skip = () if ID == 'STR-04' else tuple({c for c, _, _ in W.comp})    # STR-05 is not symmetric in X
    res = pc.comp_checks(W, mirror_skip=skip)
    if skip: print('  (mirror X not applicable to STR-05: open joining end)')
    W.bm.free()
    obs = {}; tris = {}
    for g in GROUPS:
        P = Part(g)
        for m in ms:
            if m[1] == g: add_member(P, m)
        tris[g] = sum(len(f.verts) - 2 for f in P.bm.faces)
        obs[g] = to_object(P, NAME, coll, mat, root)
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    print('  tris per part:', tris)
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'OVER x{tot / CFG["budget"]:.2f}')
    for o in obs.values(): pc.coplanar_overlaps(o)
    print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values())))
    cross_contacts(obs)
    cells = sorted({cell_of(o.data.uv_layers.active.data[p.loop_start].uv) for o in obs.values() for p in o.data.polygons})
    zmin = min((o.matrix_world @ v.co).z for o in obs.values() for v in o.data.vertices)
    print('  atlas cells used', cells, '| smooth faces', sum(p.use_smooth for o in obs.values() for p in o.data.polygons),
          '| materials', sorted({m.name for o in obs.values() for m in o.data.materials}),
          f'| min z {zmin:.4f} (posts on the ground)')
    functional_checks(obs)
    snap_check()
    return coll, root, obs, img, mat, tot


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


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.70, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    tg = 'TMP_' + ID.replace('-', '')
    sc = bpy.data.scenes.new(tg + '_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new(tg + '_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new(tg + '_World'); w.use_nodes = True; nt = w.node_tree
    wo = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bgn.inputs['Color'].default_value = (lin(bg[0]), lin(bg[1]), lin(bg[2]), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.85, 0.88, 0.95, 1)
    amb.inputs['Strength'].default_value = 0.65
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bgn.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], wo.inputs['Surface']); sc.world = w
    tmp = []
    laz = 0.0 if view_dir[0] >= 0 else 180.0        # key light from the camera's side (STR-05 is seen from the back-left)
    def sun(nm, rot, e, col, shadow=True):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.color = col; ld.angle = math.radians(28); ld.use_shadow = shadow
        o = bpy.data.objects.new(nm, ld); o.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(o)
        tmp.append(o)
    sun(tg + '_Sun', (40, 0, -35 + laz), 3.2, (1, 0.96, 0.88))
    sun(tg + '_Fill', (65, 0, 150 + laz), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new(tg + '_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new(tg + '_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 15.0
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
    """collection-only library; inside the .blend the collection carries the ASSET name (make_lod1.py looks it up by it)"""
    old = coll.name; clash = bpy.data.collections.get(NAME)
    if clash is not None and clash != coll: raise RuntimeError(f'collection {NAME} already exists')
    coll.name = NAME
    try:
        data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
        bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    finally:
        coll.name = old
    print('lib blend', path, '(collection written as', NAME + ')')


def export_one(coll, root, fbx):
    """pc.export with the user's selection / active object saved and restored (live)"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx


def lodcheck():
    """import the FBX (with _Low1 children from make_lod1.py) and render LOD0 / LOD1 separately into the check dir"""
    fbx = os.path.join(ART, 'Meshes', NAME + '.fbx')
    win = bpy.context.window or bpy.context.window_manager.windows[0]
    prev = win.scene; sc = bpy.data.scenes.new('TMP_STR04_LOD'); bm_, bi_ = set(bpy.data.materials), set(bpy.data.images)
    try:
        win.scene = sc; bpy.ops.import_scene.fbx(filepath=fbx); bpy.context.view_layer.update()
    finally:
        win.scene = prev
    obs = list(sc.objects)
    l0 = [o for o in obs if o.type == 'MESH' and not o.name.endswith('_Low1')]; l1 = [o for o in obs if o.name.endswith('_Low1')]
    for tag, grp in (('LOD0', l0), ('LOD1', l1)):
        t = sum(len(p.vertices) - 2 for o in grp for p in o.data.polygons)
        print(f'  {tag}: {[o.name for o in grp]} tris {t}')
        if grp: render(grp, os.path.join(CHECK_DIR, f'{ID}_{tag}.png'), VIEW_PREVIEW[ID], res=(800, 600))
    drop_import(sc, obs, bm_, bi_)


if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
elif MODE == 'lodcheck':
    os.makedirs(CHECK_DIR, exist_ok=True); lodcheck()
else:
    coll, root, obs, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root] + list(obs.values())
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        rose_mount(list(obs.values()), os.path.join(CHECK_DIR, f'{ID}_rose_mount_{tag}.png'))
        render(objs, os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), VIEW_REF[ID], res=(1254, 1254), fill_w=0.82, fill_h=0.82)
        render(objs, os.path.join(CHECK_DIR, f'{ID}_34_{tag}.png'), VIEW_PREVIEW[ID])
        render(objs, os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), VIEW_PREVIEW[ID], res=(128, 128), fill_w=0.85, fill_h=0.85)
    else:
        rose_mount(list(obs.values()))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_one(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', CFG['preview']), VIEW_PREVIEW[ID])
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(list(obs.values()), os.path.join(CHECK_DIR, f'geom_{tag}.json'))
