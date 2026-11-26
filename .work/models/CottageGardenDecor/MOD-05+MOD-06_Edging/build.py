# build.py - MOD-05 Brick edging 1 m (FMS_Garden_Edging_Brick) + MOD-06 Brick edging 90 deg curve
# (FMS_Garden_Edging_Brick_Curve), pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build (read only).
# One registry script for both modules (form of Tools/blender/build_registry_template.py).
# Headless:
#   set PYTHONUTF8=1
#   blender.exe --background --factory-startup --python build.py -- MOD-05|MOD-06 build|export|verify|dump
#   build  = build the model + printed checks (topology, coplanar, ground, tris, SNAP MOD-05 <-> MOD-06)
#            + check renders to %TEMP%/assetnew_check/<ID>/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (SHA1)
#   verify = only re-import the FBX in art/
#   dump   = build + geometry dump only (live/headless comparison)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\MOD-05+MOD-06_Edging\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['MOD-05', 'build']})
#   Live mode touches only the collection MOD-05_Edging_Brick / MOD-06_Edging_Brick_Curve.
# Axes (Blender): Z = up (Unity Y). FBX export -Z forward, Y up: Blender (x, y, z) -> Unity (-x, z, -y)
#   (Unity's FBX importer negates X; same convention as STR-01/PLT-02 notes: Blender -Y = Unity +Z).
#   MOD-05: Blender X = length (-0.5..0.5), Y = depth (+-0.05). Symmetric, so Unity sees the same numbers.
#   MOD-06: arc centre = pivot; arc in the Blender quadrant x <= 0, y <= 0 so that its ends lie at Unity (1, 0, 0)
#           [Blender (-1, 0, 0)] and Unity (0, 0, 1) [Blender (0, -1, 0)] as the snap contract says.
import bpy, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
BRICK, RED_D = 14, 6                          # A-14 Brick #9C3F33 (even bricks), A-6 Red dark #A8372E (odd bricks)
# section (identical on both modules, snap contract)
H_V, H_P, HALF_D = 0.0875, 0.15, 0.05         # valley (eave) height, peak height, half depth
N_STR, L_STR = 8, 1.0                         # MOD-05: 8 bricks, pitch 0.125
N_ARC, R_AX = 12, 1.0                         # MOD-06: 12 bricks of 7.5 deg, axis radius 1.0 (0.95 .. 1.05)
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'MOD-05'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'


# ---------------- geometry (pure python: also used by the SNAP check without creating objects) ----------------
# One closed shell per module. Brick k = two side pentagons (flat bottom, vertical sides to H_V, roof to the peak),
# two roof quads, one bottom quad; neighbouring bricks share the border edges (no internal faces, no coplanar overlaps).
# End faces = flat vertical rectangles at the valley (0.10 x 0.0875). Faces: (vertex indices, slot, component).
def edging(border, peak, n):
    """border(i, s, z) -> point on brick border i (0..n), side s (0 = -side, 1 = +side); peak(k, s) -> ridge end of brick k"""
    V, F = [], []
    def add(p): V.append(tuple(p)); return len(V) - 1
    B = [[(add(border(i, s, 0.0)), add(border(i, s, H_V))) for s in (0, 1)] for i in range(n + 1)]
    Pk = [[add(peak(k, s)) for s in (0, 1)] for k in range(n)]
    for k in range(n):
        sl = BRICK if k % 2 == 0 else RED_D
        b0m, e0m = B[k][0]; b0p, e0p = B[k][1]; b1m, e1m = B[k + 1][0]; b1p, e1p = B[k + 1][1]
        pm, pp = Pk[k]
        F += [([b0m, b1m, e1m, pm, e0m], sl, 'Bricks'), ([b0p, e0p, pp, e1p, b1p], sl, 'Bricks'),
              ([e0m, pm, pp, e0p], sl, 'Bricks'), ([pm, e1m, e1p, pp], sl, 'Bricks'),
              ([b0m, b0p, b1p, b1m], sl, 'Bricks')]
    ends = []
    for i, k in ((0, 0), (n, n - 1)):
        (bm_, em_), (bp_, ep_) = B[i]
        F.append(([bm_, em_, ep_, bp_], BRICK if k % 2 == 0 else RED_D, 'Ends')); ends.append([bm_, em_, ep_, bp_])
    return V, F, ends


def geo_straight():
    pitch = L_STR / N_STR
    border = lambda i, s, z: (-L_STR / 2 + pitch * i, (-HALF_D, HALF_D)[s], z)
    peak = lambda k, s: (-L_STR / 2 + pitch * (k + 0.5), (-HALF_D, HALF_D)[s], H_P)
    return edging(border, peak, N_STR)


A0, DA = math.pi, math.radians(90.0 / N_ARC)  # arc from Blender 180 deg (Unity (1,0,0)) to 270 deg (Unity (0,0,1))
RI, RO = R_AX - HALF_D, R_AX + HALF_D
# Planar faces on a fan-shaped brick: the side pentagons lie on the chords (ridge ends at r*cos(DA/2)); the two roof
# planes contain the eave lines, which pass through the axis at H_V, so the ridge (their intersection) rises outward:
# z = H_V + K*d. K is fitted so the outer ridge end is exactly H_P = 0.15 (height = MOD-05); inner end 0.144.
K_RIDGE = (H_P - H_V) / (RO * math.cos(DA / 2))


def geo_curve():
    def border(i, s, z):
        r = (RI, RO)[s]; a = A0 + DA * i
        return (r * math.cos(a), r * math.sin(a), z)
    def peak(k, s):
        d = (RI, RO)[s] * math.cos(DA / 2); a = A0 + DA * (k + 0.5)
        return (d * math.cos(a), d * math.sin(a), H_V + K_RIDGE * d)
    return edging(border, peak, N_ARC)


def to_part(V, F, name='Body'):
    P = Part(name); bm = P.bm
    vs = [bm.verts.new(Vector(p)) for p in V]; comp = {}
    for idx, sl, cn in F: comp.setdefault(cn, []).append(P.face([vs[i] for i in idx], sl))
    for cn in ('Bricks', 'Ends'): P.comp.append((cn, comp[cn], cn == 'Bricks'))
    return P


def planarity(V, F):
    worst = 0.0
    for idx, _, _ in F:
        if len(idx) < 4: continue
        p = [Vector(V[i]) for i in idx]; n = (p[1] - p[0]).cross(p[2] - p[0]).normalized()
        worst = max(worst, max(abs((q - p[0]).dot(n)) for q in p))
    return worst


# ---------------- SNAP (contract: CATALOG «Модули и стыковка» item 3, grid 1.0 m) ----------------
def xform(V, rot_deg, t):
    M = Matrix.Translation(Vector(t)) @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
    return [tuple(M @ Vector(p)) for p in V]


def same_set(a, b, tol=1e-3):
    if len(a) != len(b): return False, 9.9
    dev = max(min((Vector(p) - Vector(q)).length for q in b) for p in a)
    return dev <= tol, dev


def unity(p): return (round(-p[0], 4), round(p[2], 4), round(-p[1], 4))


def snap_check():
    ok = True
    def row(nm, good, txt):
        nonlocal ok; ok &= bool(good); print(f'  SNAP {nm}: {txt} {"OK" if good else "FAIL"}')
    Vs, Fs, Es = geo_straight(); Vc, Fc, Ec = geo_curve()
    sec = lambda V, E: [V[i] for i in E]
    # MOD-05 alone
    lo = [min(p[j] for p in Vs) for j in range(3)]; hi = [max(p[j] for p in Vs) for j in range(3)]
    row('MOD-05 bbox', abs(lo[0] + .5) < 1e-6 and abs(hi[0] - .5) < 1e-6 and abs(lo[1] + HALF_D) < 1e-6 and
        abs(hi[1] - HALF_D) < 1e-6 and abs(lo[2]) < 1e-6 and abs(hi[2] - H_P) < 1e-6,
        f'x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f} (want +-0.5, +-0.05, 0..0.15)')
    sA, sB = sec(Vs, Es[0]), sec(Vs, Es[1])
    row('MOD-05 end faces flat at x = +-0.5', all(abs(p[0] + .5) < 1e-6 for p in sA) and all(abs(p[0] - .5) < 1e-6 for p in sB), '')
    g, dev = same_set([(p[0] + 1.0, p[1], p[2]) for p in sA], sB)
    row('MOD-05 <-> MOD-05 (next cell, +1.0)', g, f'end sections identical, max dev {dev * 1000:.3f} mm')
    row('MOD-05 valley on both ends', all(p[2] <= H_V + 1e-6 for p in sA + sB),
        f'end top {max(p[2] for p in sA + sB):.4f} = valley {H_V}; first peak {L_STR / N_STR / 2:.4f} m from the end')
    # placed at node + 0.5 => ends on nodes
    for c in (0.5, 1.5, -0.5):
        e = (c - .5, c + .5); row(f'MOD-05 at grid x {c} -> ends on nodes', all(abs(x - round(x)) < 1e-6 for x in e), f'ends {e}')
    # MOD-06 alone
    lo = [min(p[j] for p in Vc) for j in range(3)]; hi = [max(p[j] for p in Vc) for j in range(3)]
    row('MOD-06 bbox', abs(lo[0] + RO) < 1e-6 and abs(hi[0]) < 1e-6 and abs(lo[1] + RO) < 1e-6 and abs(hi[1]) < 1e-6
        and abs(lo[2]) < 1e-6 and abs(hi[2] - H_P) < 1e-6,
        f'size {hi[0] - lo[0]:.4f} x {hi[1] - lo[1]:.4f} x {hi[2] - lo[2]:.4f} (want 1.05 x 1.05 x 0.15), pivot = circle centre')
    c0, c1 = sec(Vc, Ec[0]), sec(Vc, Ec[1])
    m0 = tuple(sum(p[j] for p in c0) / 4 for j in range(2)); m1 = tuple(sum(p[j] for p in c1) / 4 for j in range(2))
    row('MOD-06 end faces = radial cuts', all(abs(p[1]) < 1e-9 for p in c0) and all(abs(p[0]) < 1e-9 for p in c1),
        'Blender y = 0 / x = 0 (Unity z = 0 / x = 0)')
    row('MOD-06 ends on grid nodes (axis)', abs(m0[0] + 1) < 1e-6 and abs(m0[1]) < 1e-6 and abs(m1[0]) < 1e-6 and abs(m1[1] + 1) < 1e-6,
        f'Blender {tuple(round(x, 4) for x in m0)}, {tuple(round(x, 4) for x in m1)} = Unity {unity(m0 + (0,))}, {unity(m1 + (0,))}')
    row('MOD-06 valley on both ends', all(p[2] <= H_V + 1e-6 for p in c0 + c1),
        f'end top {max(p[2] for p in c0 + c1):.4f}; first peak {R_AX * DA / 2:.4f} m (arc on the axis) from the end vs MOD-05 0.0625')
    # MOD-05 <-> MOD-06: arc at node (0,0); strip A on the grid line Blender x = -1 (rot 90, centre (-1, 0.5)),
    # strip B on the grid line Blender y = -1 (rot 0, centre (0.5, -1)). Arc tangent at both ends = grid line.
    VA = xform(Vs, 90, (-1.0, 0.5, 0)); VB = xform(Vs, 0, (0.5, -1.0, 0))
    jA = [p for p in VA if abs(p[1]) < 1e-6]; jB = [p for p in VB if abs(p[0]) < 1e-6]
    g, dev = same_set(jA, c0); row('MOD-05 <-> MOD-06 joint A (Unity end (1,0,0))', g, f'{len(jA)}/{len(c0)} verts, max dev {dev * 1000:.3f} mm')
    g, dev = same_set(jB, c1); row('MOD-05 <-> MOD-06 joint B (Unity end (0,0,1))', g, f'{len(jB)}/{len(c1)} verts, max dev {dev * 1000:.3f} mm')
    row('no interpenetration (strips outside the arc quadrant)', min(p[1] for p in VA) >= -1e-6 and min(p[0] for p in VB) >= -1e-6, '')
    # four arcs = ring of axis diameter 2.0
    devs = []
    for r in (90, 180, 270):
        Vr = xform(Vc, r, (0, 0, 0)); Er = [Vr[i] for i in Ec[0]]
        prev = [p for p in xform(Vc, r - 90, (0, 0, 0))]; Ep = [prev[i] for i in Ec[1]]
        g, dev = same_set(Er, Ep); devs.append(dev); ok &= g
    row('4 x MOD-06 = ring (axis diameter 2.0)', max(devs) <= 1e-3, f'max dev {max(devs) * 1000:.3f} mm')
    # diagonal symmetry of the arc (mirror across the bisector)
    mir = max(min((Vector((p[1], p[0], p[2])) - Vector(q)).length for q in Vc) for p in Vc)
    print(f'  MOD-06 symmetry across the bisector: {mir:.6f}')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


# ---------------- registry ----------------
REG = {
    'MOD-05': dict(name='FMS_Garden_Edging_Brick', coll='MOD-05_Edging_Brick', preview='FMS_Garden_MOD_05_Preview.png',
                   budget=200, geo=geo_straight, mirror_skip=(),
                   view_ref=(-math.sin(math.radians(15)), -math.cos(math.radians(15)), math.tan(math.radians(27))),
                   view_prev=(-0.45, -1.25, 0.70)),
    'MOD-06': dict(name='FMS_Garden_Edging_Brick_Curve', coll='MOD-06_Edging_Brick_Curve', preview='FMS_Garden_MOD_06_Preview.png',
                   budget=300, geo=geo_curve, mirror_skip=('Bricks', 'Ends'),
                   view_ref=(0.7071, 0.7071, math.tan(math.radians(36))),
                   view_prev=(0.7071, 0.7071, math.tan(math.radians(33))),
                   light_az=100.0),        # lights turned with the camera (series key light relative to the view)
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
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
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


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    V, F, _ = CFG['geo']()
    tris = {cn: sum(len(i) - 2 for i, _, c in F if c == cn) for cn in ('Bricks', 'Ends')}
    print(f'== {ID} {NAME}: max face non-planarity {planarity(V, F) * 1000:.4f} mm')
    ob = pc.to_object(to_part(V, F), NAME, coll, mat, (0, 0, 0), root, mirror_skip=CFG['mirror_skip'])
    bpy.context.view_layer.update()
    tot = pc.report({'Body': ob})
    print('  tris per component:', tris)
    print(f'  budget {CFG["budget"]} ->', 'OK' if tot <= CFG['budget'] else f'OVER x{tot / CFG["budget"]:.2f}')
    pc.coplanar_overlaps(ob)
    slots = sorted({cell_of(ob.data.uv_layers.active.data[p.loop_start].uv) for p in ob.data.polygons})
    print('  atlas cells used', slots, '| smooth faces', sum(p.use_smooth for p in ob.data.polygons),
          '| materials', [m.name for m in ob.data.materials])
    snap_check()
    return coll, root, ob, img, mat, tot


def cell_of(uv): return int((1 - uv[1]) * 4) * 4 + int(uv[0] * 4)


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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.70, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
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
    target = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])   # bbox centre (arc pivot is off the mesh)
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
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_ref_{tag}.png'), CFG['view_ref'], res=(1254, 1254), fill_w=0.88, fill_h=0.88, lens=85)
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_prev_{tag}.png'), CFG['view_prev'])
        render([root, ob], os.path.join(CHECK_DIR, f'{ID}_thumb_{tag}.png'), CFG['view_prev'], res=(128, 128), fill_w=0.9, fill_h=0.9)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_live_safe(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render([root, ob], os.path.join(ART, 'Previews', CFG['preview']), CFG['view_prev'])
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, f'geom_{tag}.json'))
