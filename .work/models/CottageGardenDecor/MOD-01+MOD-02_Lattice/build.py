# build.py - MOD-01 Lattice panel 2 m (FMS_Garden_Lattice_Panel) + MOD-02 Lattice post (FMS_Garden_Lattice_Post),
# pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build (read only).
# One registry script for both modules (form of Tools/blender/build_registry_template.py).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- MOD-01|MOD-02 build|export|verify|dump
#   build  = build the model + printed checks (topology, coplanar, ground, tris, SNAP MOD-01 <-> MOD-02, PLT-02 mount)
#            + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify = only re-import the FBX in art/
#   dump   = build + geometry dump only (live/headless comparison)
#   PACK_ART=<dir> redirects the outputs (headless reproduction); the atlas and the PLT-02 FBX are always read from the
#   repo art/CottageGardenDecor (read only).
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\MOD-01+MOD-02_Lattice\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['MOD-01', 'build']})
#   Live mode touches only the collection MOD-01_Lattice_Panel / MOD-02_Lattice_Post.
# Axes (Blender): Z = up (Unity Y). FBX export -Z forward, Y up: Blender (x, y, z) -> Unity (-x, z, -y).
#   Spec "X" = Blender X (span direction), spec "Z" (thickness, post axis) = Blender -Y, spec "Y" = Blender Z.
#   Both modules are symmetric in X and in Y except the two slat layers (layer A spec Z 0..+0.03 = Blender Y -0.03..0).
import bpy, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART_REPO = os.path.join(REPO, 'art', 'CottageGardenDecor')
ART = os.environ.get('PACK_ART') or ART_REPO
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WHITE = 10                                    # A-10 White paint #EEEDE7 (same white as STR-01_White / STR-06 frame)
# panel (snap contract CATALOG «Модули и стыковка» item 1, grid 2.0 m)
FX_O, FX_I = 0.94, 0.86                       # frame outer / inner half width (member 0.08)
FZ_O0, FZ_I0, FZ_I1, FZ_O1 = 0.05, 0.13, 1.72, 1.80   # frame bottom, opening bottom/top, frame top
FT = 0.03                                     # frame half thickness (0.06 on the post axis)
SLAT_W, SLAT_PITCH = 0.05, 0.20               # slat width (reference measured ~0.055; spec 0.04), perpendicular pitch
SLAT_EMBED = 0.01                             # slat ends run 1 cm into the frame members (ends hidden, visually flush)
# slat layers (Blender Y): A (+45 deg, spec Z 0..+0.03) and B (-45 deg, spec Z -0.03..0); 0.030 thick each,
# 1 mm behind the frame faces and 2 mm interpenetrating at the crossings (no coplanar faces anywhere)
LAYER_A = (-0.029, 0.001)
LAYER_B = (-0.001, 0.029)
# post
PS, PC, P_TOP, P_CAP0, P_CHAMF = 0.06, 0.08, 1.95, 1.80, 0.02   # shaft half 0.12, cap half 0.16, cap Y 1.80..1.95
GRID = 2.0
ROSE_FBX = os.path.join(ART_REPO, 'Meshes', 'FMS_Garden_Rose_Climbing_Side.fbx')
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'MOD-01'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'


# ---------------- 2D helpers (x, z) ----------------
def clip(poly, a, b, c):
    """Sutherland-Hodgman: keep a*x + b*z <= c"""
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fq <= 0:
            if fp > 0: t = fp / (fp - fq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
            out.append(q)
        elif fp <= 0:
            t = fp / (fp - fq); out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    # drop near-duplicate points
    res = []
    for p in out:
        if not res or (abs(p[0] - res[-1][0]) > 1e-7 or abs(p[1] - res[-1][1]) > 1e-7): res.append(p)
    if len(res) > 1 and abs(res[0][0] - res[-1][0]) < 1e-7 and abs(res[0][1] - res[-1][1]) < 1e-7: res.pop()
    return res


def clip_rect(poly, x0, x1, z0, z1):
    for a, b, c in ((1, 0, x1), (-1, 0, -x0), (0, 1, z1), (0, -1, -z0)):
        poly = clip(poly, a, b, c)
        if len(poly) < 3: return []
    return poly


def area(poly):
    return 0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


# ---------------- geometry (pure python: also used by the SNAP check without creating objects) ----------------
# Faces: (vertex indices, slot, component). Every component is one closed shell.
def prism(V, F, poly, y0, y1, comp):
    """extrude a CCW (x, z) polygon along Blender Y from y0 to y1 -> closed shell"""
    n = len(poly); b = len(V)
    for x, z in poly: V.append((x, y0, z))
    for x, z in poly: V.append((x, y1, z))
    F.append((list(range(b, b + n)), WHITE, comp))                       # y0 face
    F.append((list(range(b + n, b + 2 * n))[::-1], WHITE, comp))         # y1 face
    for i in range(n):
        j = (i + 1) % n
        F.append(([b + i, b + n + i, b + n + j, b + j], WHITE, comp))


def geo_panel():
    V, F = [], []
    # Frame: one closed rectangular ring (4 members as one shell; no internal faces between stiles and rails)
    o = [(-FX_O, FZ_O0), (FX_O, FZ_O0), (FX_O, FZ_O1), (-FX_O, FZ_O1)]
    i_ = [(-FX_I, FZ_I0), (FX_I, FZ_I0), (FX_I, FZ_I1), (-FX_I, FZ_I1)]
    b = len(V)
    for y in (-FT, FT):
        for x, z in o + i_: V.append((x, y, z))
    Of = lambda k, s: b + s * 8 + k           # outer corner k, side s (0 front -Y, 1 back +Y)
    If = lambda k, s: b + s * 8 + 4 + k
    for k in range(4):
        k1 = (k + 1) % 4
        F.append(([Of(k, 0), Of(k1, 0), If(k1, 0), If(k, 0)], WHITE, 'Frame'))    # front trapezoids
        F.append(([Of(k, 1), If(k, 1), If(k1, 1), Of(k1, 1)], WHITE, 'Frame'))    # back trapezoids
        F.append(([Of(k, 0), Of(k, 1), Of(k1, 1), Of(k1, 0)], WHITE, 'Frame'))    # outer faces
        F.append(([If(k, 0), If(k1, 0), If(k1, 1), If(k, 1)], WHITE, 'Frame'))    # inner faces
    # Slats: bands of width 0.04 at +-45 deg, perpendicular pitch 0.20, centre lines through the opening centre,
    # clipped to the opening expanded by SLAT_EMBED (ends buried in the frame members)
    zc = (FZ_I0 + FZ_I1) / 2; r2 = math.sqrt(2.0); Lb = 6.0
    ex = (-FX_I - SLAT_EMBED, FX_I + SLAT_EMBED, FZ_I0 - SLAT_EMBED, FZ_I1 + SLAT_EMBED)
    slats = []
    for layer, sgn, (y0, y1) in (('A', 1, LAYER_A), ('B', -1, LAYER_B)):
        d = Vector((sgn, 1)).normalized()          # slat direction in (x, z): A = (1, 1) +45 deg, B = (-1, 1)
        nrm = Vector((-d.y, d.x))                  # perpendicular
        for k in range(-8, 9):
            c = Vector((0.0, zc)) + nrm * (SLAT_PITCH * k)
            hw = SLAT_W / 2
            band = [tuple(c - d * Lb - nrm * hw), tuple(c + d * Lb - nrm * hw), tuple(c + d * Lb + nrm * hw), tuple(c - d * Lb + nrm * hw)]
            if area(band) < 0: band = band[::-1]
            vis = clip_rect(band, -FX_I, FX_I, FZ_I0, FZ_I1)
            if not vis or area(vis) < 0.004: continue          # nothing (or only a sliver) inside the opening
            poly = clip_rect(band, *ex)
            nm = f'Slat{layer}{k:+d}'
            prism(V, F, poly, y0, y1, nm); slats.append((nm, len(poly), area(vis)))
    return V, F, slats


def geo_post():
    V, F = [], []
    sq = lambda h, z: [(-h, -h, z), (h, -h, z), (h, h, z), (-h, h, z)]
    rings = [sq(PS, 0.0), sq(PS, P_CAP0), sq(PC, P_CAP0), sq(PC, P_TOP - P_CHAMF), sq(PC - P_CHAMF, P_TOP)]
    comps = ['Shaft', 'Cap', 'Cap', 'Cap']       # band j (ring j -> j+1)
    R = []
    for r in rings:
        R.append(list(range(len(V), len(V) + 4))); V.extend(r)
    F.append(([R[0][3], R[0][2], R[0][1], R[0][0]], WHITE, 'Shaft'))      # bottom (on the ground)
    for j in range(4):
        for k in range(4):
            k1 = (k + 1) % 4
            F.append(([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], WHITE, comps[j]))
    F.append((R[4][:], WHITE, 'Cap'))                                       # flat top 0.12 x 0.12
    return V, F, []


def to_part(V, F, name='Body'):
    P = Part(name); bm = P.bm
    vs = [bm.verts.new(Vector(p)) for p in V]; comp = {}
    order = []
    for idx, sl, cn in F:
        if cn not in comp: order.append(cn)
        comp.setdefault(cn, []).append(P.face([vs[i] for i in idx], sl))
    for cn in order: P.comp.append((cn, comp[cn], cn == 'Shaft'))
    return P


def planarity(V, F):
    worst = 0.0
    for idx, _, _ in F:
        if len(idx) < 4: continue
        p = [Vector(V[i]) for i in idx]; n = (p[1] - p[0]).cross(p[2] - p[0]).normalized()
        worst = max(worst, max(abs((q - p[0]).dot(n)) for q in p))
    return worst


# ---------------- SNAP (contract: CATALOG «Модули и стыковка» item 1, grid 2.0 m) ----------------
def xform(V, rot_deg, t):
    M = Matrix.Translation(Vector(t)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
    return [tuple(M @ Vector(p)) for p in V]


def bbox(V):
    return [min(p[j] for p in V) for j in range(3)], [max(p[j] for p in V) for j in range(3)]


def inside_box(p, lo, hi, e=1e-6):
    return all(lo[j] + e < p[j] < hi[j] - e for j in range(3))


def rose_bbox():
    """bbox of the approved PLT-02 FBX (read only; imported into a temporary scene and removed again)"""
    if not os.path.isfile(ROSE_FBX): return None
    win = bpy.context.window if bpy.context.window else None
    sc = bpy.data.scenes.new('TMP_MOD01_RoseMount')
    prev = win.scene if win else None
    before = (set(bpy.data.objects), set(bpy.data.meshes), set(bpy.data.materials), set(bpy.data.images))
    try:
        if win: win.scene = sc
        else: bpy.context.window_manager.windows[0].scene = sc
        bpy.ops.import_scene.fbx(filepath=ROSE_FBX)
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ v.co for o in sc.objects if o.type == 'MESH' for v in o.data.vertices]
        lo, hi = [min(p[j] for p in pts) for j in range(3)], [max(p[j] for p in pts) for j in range(3)]
    finally:
        for o in set(bpy.data.objects) - before[0]: bpy.data.objects.remove(o, do_unlink=True)
        for m in set(bpy.data.meshes) - before[1]: bpy.data.meshes.remove(m)
        for m in set(bpy.data.materials) - before[2]:
            if m.users == 0: bpy.data.materials.remove(m)
        for i in set(bpy.data.images) - before[3]:
            if i.users == 0: bpy.data.images.remove(i)
        if win: win.scene = prev
        else: bpy.context.window_manager.windows[0].scene = prev
        bpy.data.scenes.remove(sc)
    return lo, hi


def snap_check():
    ok = True
    def row(nm, good, txt=''):
        nonlocal ok; ok &= bool(good); print(f'  SNAP {nm}: {txt} {"OK" if good else "FAIL"}')
    Vp, Fp, _ = geo_panel(); Vq, Fq, _ = geo_post()
    lo, hi = bbox(Vp)
    row('MOD-01 bbox', abs(lo[0] + FX_O) < 1e-6 and abs(hi[0] - FX_O) < 1e-6 and abs(lo[1] + FT) < 1e-6 and
        abs(hi[1] - FT) < 1e-6 and abs(lo[2] - FZ_O0) < 1e-6 and abs(hi[2] - FZ_O1) < 1e-6,
        f'x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f} (want +-0.94, +-0.03, 0.05..1.80)')
    lo2, hi2 = bbox(Vq)
    row('MOD-02 bbox', abs(lo2[0] + PC) < 1e-6 and abs(hi2[0] - PC) < 1e-6 and abs(lo2[1] + PC) < 1e-6 and
        abs(lo2[2]) < 1e-6 and abs(hi2[2] - P_TOP) < 1e-6,
        f'{hi2[0] - lo2[0]:.4f} x {hi2[1] - lo2[1]:.4f} x {hi2[2] - lo2[2]:.4f} (want 0.16 x 0.16 x 1.95), pivot = base centre')
    shaft = [p for p in Vq if p[2] <= P_CAP0 + 1e-9 and abs(abs(p[0]) - PS) < 1e-9]
    row('MOD-02 shaft faces at +-0.06 up to the cap underside 1.80', len(shaft) == 8 and
        all(abs(abs(p[1]) - PS) < 1e-9 for p in shaft), f'{len(shaft)} shaft verts')
    # straight run: posts at nodes 0 and 2.0, panel at node + 1.0
    VP = xform(Vp, 0, (GRID / 2, 0, 0)); Q0 = xform(Vq, 0, (0, 0, 0)); Q1 = xform(Vq, 0, (GRID, 0, 0))
    endL = [p for p in VP if abs(p[0] - min(q[0] for q in VP)) < 1e-9]
    endR = [p for p in VP if abs(p[0] - max(q[0] for q in VP)) < 1e-9]
    gL = min(p[0] for p in VP) - PS; gR = (GRID - PS) - max(p[0] for p in VP)
    row('gap frame end <-> post shaft face (left / right)', abs(gL) <= 1e-3 and abs(gR) <= 1e-3, f'{gL * 1000:.3f} / {gR * 1000:.3f} mm')
    within = lambda E: all(abs(p[1]) <= PS + 1e-9 and 0 <= p[2] <= P_CAP0 + 1e-9 for p in E)
    row('frame end faces lie inside the shaft faces', within(endL) and within(endR),
        f'end y +-{max(abs(p[1]) for p in endL):.3f} z {min(p[2] for p in endL):.2f}..{max(p[2] for p in endL):.2f}')
    pitch = (max(p[0] for p in VP) + PS) - (min(p[0] for p in VP) - PS)
    row('post pitch', abs(pitch - GRID) < 1e-6, f'{pitch:.3f} (want 2.000)')
    row('frame top level with the cap underside, below the cap', abs(max(p[2] for p in VP) - P_CAP0) < 1e-6,
        f'frame top {max(p[2] for p in VP):.3f}, cap underside {P_CAP0:.3f}, cap top {P_TOP:.3f}')
    shaft_lo, shaft_hi = (-PS, -PS, 0), (PS, PS, P_CAP0)
    pen = [p for p in VP if inside_box(p, (shaft_lo[0], shaft_lo[1], 0), (shaft_hi[0], shaft_hi[1], P_CAP0)) or
           inside_box(p, (GRID - PS, -PS, 0), (GRID + PS, PS, P_CAP0))]
    row('no panel vertex inside a post', not pen, f'{len(pen)} verts')
    # 90 deg corner: second panel rotated around the shared post at node (2, 0): centre (2, 1), rot 90
    VC = xform(Vp, 90, (GRID, GRID / 2, 0)); Q2 = xform(Vq, 0, (GRID, GRID, 0))
    gC = min(p[1] for p in VC) - PS
    row('corner: rotated panel end <-> shared post face', abs(gC) <= 1e-3 and all(abs(p[0] - GRID) <= PS + 1e-9 for p in VC if abs(p[1] - min(q[1] for q in VC)) < 1e-9),
        f'gap {gC * 1000:.3f} mm, one post per corner')
    l1, h1 = bbox(VP); l2, h2 = bbox(VC)
    clash = all(l1[j] < h2[j] - 1e-6 and l2[j] < h1[j] - 1e-6 for j in range(3))
    row('corner: the two panels do not overlap', not clash, f'panel 1 x..{h1[0]:.3f}, panel 2 x {l2[0]:.3f}.. y {l2[1]:.3f}..')
    # PLT-02 climbing rose on the panel face (front = Blender -Y = Unity +Z)
    rb = rose_bbox()
    if rb is None:
        row('PLT-02 mount', False, f'missing {ROSE_FBX}')
    else:
        (rl, rh) = rb
        w, dpt, h = rh[0] - rl[0], rh[1] - rl[1], rh[2] - rl[2]
        print(f'  PLT-02 FBX bbox: x {rl[0]:.3f}..{rh[0]:.3f} y {rl[1]:.3f}..{rh[1]:.3f} z {rl[2]:.3f}..{rh[2]:.3f} '
              f'(size {w:.3f} x {dpt:.3f} x {h:.3f})')
        # mount: rose pivot (back plane, ground) at the panel front face, panel centre: rose offset (x, -FT, 0)
        back = rh[1] - FT                       # rose back plane in panel space
        slat_front = LAYER_A[0]
        row('PLT-02 back plane on the frame front face', abs(back - (-FT)) <= 1e-3,
            f'rose back y {back:.4f} = frame face {-FT:.3f}; {(slat_front - back) * 1000:.1f} mm in front of the slats')
        row('PLT-02 width fits the opening', w <= 2 * FX_I, f'{w:.3f} <= opening {2 * FX_I:.2f} (panel {2 * FX_O:.2f})')
        row('PLT-02 on the ground in front of the panel', abs(rl[2]) <= 1e-3, f'rose min z {rl[2]:.4f}, panel bottom {FZ_O0}')
        print(f'  PLT-02 top {rh[2]:.3f} = {rh[2] - FZ_O1:+.3f} vs panel top {FZ_O1}, {rh[2] - P_TOP:+.3f} vs post cap top '
              f'{P_TOP} (climber spills over the top); depth {dpt:.3f} in front of the face')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


# ---------------- registry ----------------
REG = {
    'MOD-01': dict(name='FMS_Garden_Lattice_Panel', coll='MOD-01_Lattice_Panel', preview='FMS_Garden_MOD_01_Preview.png',
                   budget=900, geo=geo_panel, view_ref=(0.33, -1.0, 0.45), view_prev=(0.42, -1.0, 0.50)),
    'MOD-02': dict(name='FMS_Garden_Lattice_Post', coll='MOD-02_Lattice_Post', preview='FMS_Garden_MOD_02_Preview.png',
                   budget=60, geo=geo_post, view_ref=(-0.62, -1.0, 0.62), view_prev=(-0.62, -1.0, 0.55)),
}
CFG = REG[ID]; NAME = CFG['name']; COLL = CFG['coll']
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', ID)


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


def cell_of(uv): return int((1 - uv[1]) * 4) * 4 + int(uv[0] * 4)


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    V, F, slats = CFG['geo']()
    comps = []
    for _, _, c in F:
        if c not in comps: comps.append(c)
    tris = {}
    for idx, _, c in F:
        key = 'Slats' if c.startswith('Slat') else c
        tris[key] = tris.get(key, 0) + len(idx) - 2
    print(f'== {ID} {NAME}: max face non-planarity {planarity(V, F) * 1000:.4f} mm')
    if slats:
        print(f'  slats: {len(slats)} ({sum(1 for s in slats if s[0][4] == "A")} A +45, {sum(1 for s in slats if s[0][4] == "B")} B -45);'
              f' sides {sorted({s[1] for s in slats})}; smallest visible piece {min(s[2] for s in slats):.4f} m2')
    skip = tuple(c for c in comps if c.startswith('Slat'))
    ob = pc.to_object(to_part(V, F), NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    bpy.context.view_layer.update()
    tot = pc.report({'Body': ob})
    print('  tris per part:', tris)
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'OVER x{tot / CFG["budget"]:.2f}')
    if skip:   # mirror X of the whole slat set: layer A mirrors onto layer B's footprint (different Y), check in (x, z)
        ptsA = {(round(-x, 5), round(z, 5)) for (x, y, z) in V if LAYER_A[0] - 1e-9 <= y <= LAYER_A[1] + 1e-9}
        ptsB = {(round(x, 5), round(z, 5)) for (x, y, z) in V if LAYER_B[0] - 1e-9 <= y <= LAYER_B[1] + 1e-9}
        print(f'  slat layers mirror in X (A mirrored == B footprint): {ptsA == ptsB}')
    pc.coplanar_overlaps(ob)
    slots = sorted({cell_of(ob.data.uv_layers.active.data[p.loop_start].uv) for p in ob.data.polygons})
    zmin = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    print('  atlas cells used', slots, '| smooth faces', sum(p.use_smooth for p in ob.data.polygons),
          '| materials', [m.name for m in ob.data.materials], f'| min z {zmin:.4f}',
          '(ground contact: post base on z 0)' if ID == 'MOD-02' else '(frame bottom 0.05 by contract; carried by the posts)')
    snap_check()
    return coll, root, ob, img, mat, tot


def geom_dump(ob, path):
    me = ob.data; uv = me.uv_layers.active.data
    vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
    fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                 tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
    h = hashlib.sha1(json.dumps([vs, fs]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=len(vs), faces=len(fs), sha1=h), f)
    print('  geometry dump', path, len(vs), 'verts', len(fs), 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.70, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), extra=()):
    laz = CFG.get('light_az', 0.0)
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
    for o in list(objs) + list(extra): tc.objects.link(o)
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
    pts = [o.matrix_world @ v.co for o in list(objs) + list(extra) if o.type == 'MESH' for v in o.data.vertices]
    target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 10.0
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


def assembly_render(out):
    """check render only: post + panel + post (+ corner panel) built from the same geometry, temporary objects"""
    img, mat = atlas_and_material()
    made = []
    def mk(nm, V, F, rot, t):
        P = to_part(xform(V, rot, t), F, nm)
        import bmesh
        bm = P.bm; bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        uvl = bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = pc.cell_uv(f[P.slot])
        me = bpy.data.meshes.new('TMP_' + nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        o = bpy.data.objects.new('TMP_' + nm, me); made.append(o); return o
    Vp, Fp, _ = geo_panel(); Vq, Fq, _ = geo_post()
    mk('P0', Vq, Fq, 0, (0, 0, 0)); mk('P1', Vq, Fq, 0, (GRID, 0, 0)); mk('P2', Vq, Fq, 0, (GRID, GRID, 0))
    mk('L0', Vp, Fp, 0, (GRID / 2, 0, 0)); mk('L1', Vp, Fp, 90, (GRID, GRID / 2, 0))
    try:
        render(made, out, (-0.55, -1.0, 0.45), res=(1280, 800), fill_w=0.8, fill_h=0.85)
    finally:
        for o in made:
            me = o.data; bpy.data.objects.remove(o, do_unlink=True); bpy.data.meshes.remove(me)


def export_live_safe(coll, root, fbx):
    """pc.export changes the selection/active object: restore the owner's selection afterwards"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        return pc.export(NAME, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act


if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, ob, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), CFG['view_ref'], res=(1254, 1254), fill_w=0.80, fill_h=0.80, lens=85)
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_prev_{tag}.png'), CFG['view_prev'])
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), CFG['view_prev'], res=(128, 128), fill_w=0.9, fill_h=0.9)
        if ID == 'MOD-01': assembly_render(os.path.join(CHECK_DIR, f'assembly_{tag}.png'))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render([root, ob], os.path.join(ART, 'Previews', CFG['preview']), CFG['view_prev'])
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, f'geom_{tag}.json'))
