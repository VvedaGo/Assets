# MOD-04 Workshop wall with window 2 m -> FMS_Workshop_MOD_04 (Farm Processing pack). Defines the WALL MODULE CONTRACT
# (see spec.md) reused by MOD-03 (kind='plain') and MOD-05 (kind='door').
# Headless run (factory startup, the default scene is the build scene):
#   blender --background --factory-startup --python build_wall_window.py -- <mode> [kind] [round]
#   mode: check  = build + checks + check renders to %TEMP%\FarmProcessing_check\MOD-04 (front, back, snap pair, 128 px thumb)
#         export = build + checks + FBX + .fbm + .blend + preview + FBX re-import verify   (kind must be 'window' for MOD-04)
import bpy, math, os, sys, shutil, importlib
from mathutils import Vector, kdtree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'MOD04_WallWindow')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, sweep

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = ARGV[0] if ARGV else 'check'
KIND = ARGV[1] if len(ARGV) > 1 else 'window'
ROUND = ARGV[2] if len(ARGV) > 2 else '1'
IDS = {'window': ('MOD_04', 'MOD04'), 'plain': ('MOD_03', 'MOD03'), 'door': ('MOD_05', 'MOD05')}
NAME = 'FMS_Workshop_' + IDS[KIND][0]
TEX_NAME = 'T_FarmProcessing_%s_BaseColor.png' % IDS[KIND][1]
MAT_NAME = 'M_FarmProcessing_' + IDS[KIND][1]
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'MOD-04')
os.makedirs(CHECK_DIR, exist_ok=True)
BUDGET = {'window': (350, 700), 'plain': (250, 550), 'door': (300, 650)}[KIND]

# ---------------- palette: cells 0-12 identical to STA-02/05 (mergeable), 13-15 wall-specific ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#ADA89E', '#8C877E', '#F6E2BC']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, STONE, STONE_D, PLASTER = range(16)

# ---------------- WALL MODULE CONTRACT (m); front = -Y, both faces mirrored in Y ----------------
W, D, H = 2.0, 0.18, 2.4                 # bbox exactly x +-1, y +-0.09, z 0..2.4
HX, HY = W / 2, D / 2
POST_W = 0.10                            # half-post at each end (two neighbours = one 0.20 post = MOD-06 width)
PX0 = HX - POST_W                        # post inner face x 0.90
# relief layers (half-depths, front face y = -value)
Y_PLASTER, Y_BRACE, Y_STONE, Y_FRAME, Y_CASE, Y_BLOCK, Y_CAP, Y_SILL = 0.045, 0.060, 0.072, 0.075, 0.080, 0.084, 0.090, 0.090
STONE_Z1 = 0.42
STONE_BEV = (0.050, 0.034)             # pillow bevel: inset on the face, depth
STONES = (0.35, 0.37, 0.36, 0.37, 0.35)  # widths between the posts (sum 1.80, X-symmetric)
RAIL_Z = (0.52, 0.70)
PLATE_Z = (2.20, 2.40)
BLOCK_X0, BLOCK_ZS = 0.80, ((0.48, 0.74), (2.08, 2.36))
CAP_S, CAP_IN, CAP_Y0 = 0.085, 0.014, 0.080
PLASTER_Z = (0.40, 2.22)
BR_W = 0.05                              # brace half-width
SINK = 0.02                              # members run this far into the posts / plate (hidden)
KINDS = {
    'window': dict(open=(0.43, 1.05, 1.77), jamb=0.12, head=(0.58, 0.14), sill=(0.65, 0.94), brace=(1.60, 0.50)),
    'plain':  dict(open=None, brace=(1.60, 0.50)),
    'door':   dict(open=(0.48, 0.0, 2.02), jamb=0.11, head=(0.61, 0.12), sill=None, brace=(1.80, 0.68)),
}

# ---------------- helpers ----------------
def yr(yh, bev):
    """symmetric through-depth rings: bevelled front/back faces"""
    return [(-yh, bev), (-yh + bev, 0.0), (yh - bev, 0.0), (yh, bev)] if bev else [(-yh, 0.0), (yh, 0.0)]

def ybox(P, name, x0, x1, z0, z1, rings, side, bevel, cap, snap0=False, snap1=False):
    """box lofted along +Y; rings [(y, inset)]. An inset never moves a face lying on a snap plane (x0/x1 flags),
    so the end face at x = +-1 stays a flat full rectangle edge (no groove when two modules butt)."""
    R = []
    for y, d in rings:
        a = x0 + (0 if snap0 else d); b = x1 - (0 if snap1 else d)
        R.append([Vector((a, y, z0 + d)), Vector((b, y, z0 + d)), Vector((b, y, z1 - d)), Vector((a, y, z1 - d))])
    def sd(j, k):
        return bevel if (rings[j][1] or rings[j + 1][1]) else (side(k) if callable(side) else side)
    return P.loft(name, R, sd, cap, cap, ground=(z0 == 0.0))

def brace_ext(u):
    """how far the brace runs past the post face / plate underside so its square end corners stay hidden"""
    return (max(0.03, (BR_W * abs(u.z) + 0.006) / abs(u.x)), max(0.03, (BR_W * abs(u.x) + 0.006) / abs(u.z)))

def mirror_x(fn):
    """call fn(sign) for the right (+1) and left (-1) half"""
    for s in (1, -1): fn(s)

def xb(P, name, s, xa, xb_, z0, z1, rings, side, bevel, cap, snap_outer=False):
    """ybox on the side s: xa < xb_ given for the right half (x >= 0); mirrored for s = -1"""
    if s > 0: ybox(P, name, xa, xb_, z0, z1, rings, side, bevel, cap, snap1=snap_outer)
    else:     ybox(P, name, -xb_, -xa, z0, z1, rings, side, bevel, cap, snap0=snap_outer)

# ---------------- the wall ----------------
def build_wall(kind='window'):
    K = KINDS[kind]; P = Part('Body'); op = K['open']
    # half-posts (snap face square), plate over the full width (both ends snap), rail between the posts
    mirror_x(lambda s: xb(P, 'post', s, PX0, HX, 0.0, PLATE_Z[0] + SINK, yr(Y_FRAME, 0.010), WOOD, WOOD, WOOD, snap_outer=True))
    ybox(P, 'plate', -HX, HX, PLATE_Z[0], PLATE_Z[1], yr(Y_FRAME, 0.012), WOOD, WOOD, WOOD, snap0=True, snap1=True)
    if op and op[1] == 0.0:      # door: rail stops at the jambs
        xj = op[0] + K['jamb']
        mirror_x(lambda s: xb(P, 'rail', s, xj, PX0 + SINK, RAIL_Z[0], RAIL_Z[1], yr(Y_FRAME - 0.003, 0.010), WOOD, WOOD, WOOD))
    else:
        ybox(P, 'rail', -PX0 - SINK, PX0 + SINK, RAIL_Z[0], RAIL_Z[1], yr(Y_FRAME - 0.003, 0.010), WOOD, WOOD, WOOD)
    # joint blocks (proud of the frame, snap face square) + red peg caps front and back
    for z0, z1 in BLOCK_ZS:
        mirror_x(lambda s: xb(P, 'block', s, BLOCK_X0, HX, z0, z1, yr(Y_BLOCK, 0.008), WOOD, WOOD, WOOD, snap_outer=True))
        cx, cz, h = (BLOCK_X0 + HX) / 2, (z0 + z1) / 2, CAP_S / 2
        for s in (1, -1):
            for rings in ([(-Y_CAP, CAP_IN), (-CAP_Y0, 0.0)], [(CAP_Y0, 0.0), (Y_CAP, CAP_IN)]):
                ybox(P, 'cap', s * cx - h, s * cx + h, cz - h, cz + h, rings, RED, RED, RED)
    # stone plinth between the posts (pillow bevel front/back => V-grooves between stones)
    if op and op[1] == 0.0:      # door: one run of stones on each side of the jambs
        xj = op[0] + K['jamb']; n = max(1, round((PX0 - xj) / 0.36)); runs = []
        for s in (1, -1):
            for i in range(n):
                a, b = xj + (PX0 - xj) * i / n, xj + (PX0 - xj) * (i + 1) / n
                runs.append((a, b) if s > 0 else (-b, -a))
    else:
        xs = [-PX0]
        for w in STONES: xs.append(xs[-1] + w)
        runs = list(zip(xs[:-1], xs[1:]))
    for a, b in runs:
        ybox(P, 'stone', a, b, 0.0, STONE_Z1, [(-Y_STONE, STONE_BEV[0]), (-Y_STONE + STONE_BEV[1], 0.0), (Y_STONE - STONE_BEV[1], 0.0), (Y_STONE, STONE_BEV[0])], STONE, STONE_D, STONE)
    # plaster infill (recessed); a ring slab around a window, box pieces around a door
    plaster(P, K)
    # diagonal braces in the upper corners, darker wood, ends sunk into the post and the plate
    bz0, bx1 = K['brace']
    for s in (1, -1):
        A, B = Vector((s * PX0, 0, bz0)), Vector((s * bx1, 0, PLATE_Z[0]))
        u = (B - A).normalized()
        e0, e1 = brace_ext(u)
        sweep(P, 'brace', A - u * e0, B + u * e1, [(-Y_BRACE, -BR_W), (Y_BRACE, -BR_W), (Y_BRACE, BR_W), (-Y_BRACE, BR_W)],
              [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 1, 0))
    # opening: jambs + head through the full depth (wood reveal), thick protruding sill (window)
    if op:
        hx, oz0, oz1 = op; jw = K['jamb']; hw, hh = K['head']
        mirror_x(lambda s: xb(P, 'jamb', s, hx, hx + jw, oz0, oz1, yr(Y_CASE, 0.008), WOOD, WOOD, WOOD))
        ybox(P, 'head', -hw, hw, oz1, oz1 + hh, yr(Y_CASE + 0.002, 0.010), WOOD, WOOD, WOOD)
        if K['sill']:
            sw, sz0 = K['sill']
            ybox(P, 'sill', -sw, sw, sz0, oz0, yr(Y_SILL, 0.016), WOOD, WOOD, WOOD)
    return P

def plaster(P, K):
    x0, x1, z0, z1 = -PX0 - SINK, PX0 + SINK, PLASTER_Z[0], PLASTER_Z[1]
    op = K['open']; rings = yr(Y_PLASTER, 0.0)
    if not op:
        ybox(P, 'plaster', x0, x1, z0, z1, rings, PLASTER, PLASTER, PLASTER); return
    hx, oz0, oz1 = op; jw = K['jamb']; hh = K['head'][1]
    hx_in = hx + jw / 2                                   # hole edge hidden under the middle of the jamb / sill / head
    if oz0 == 0.0:                                         # door: U of three boxes
        mirror_x(lambda s: xb(P, 'plaster', s, hx_in, x1, z0, z1, rings, PLASTER, PLASTER, PLASTER))
        ybox(P, 'plaster', -hx_in, hx_in, oz1 + hh / 2, z1, rings, PLASTER, PLASTER, PLASTER); return
    hz0 = (K['sill'][1] + oz0) / 2; hz1 = oz1 + hh / 2
    bm = P.bm
    def rect(xa, xb_, za, zb, y): return [bm.verts.new((xa, y, za)), bm.verts.new((xb_, y, za)), bm.verts.new((xb_, y, zb)), bm.verts.new((xa, y, zb))]
    of, ob = rect(x0, x1, z0, z1, -Y_PLASTER), rect(x0, x1, z0, z1, Y_PLASTER)
    hf, hb = rect(-hx_in, hx_in, hz0, hz1, -Y_PLASTER), rect(-hx_in, hx_in, hz0, hz1, Y_PLASTER)
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces += [P.face([of[i], of[j], hf[j], hf[i]], PLASTER), P.face([ob[j], ob[i], hb[i], hb[j]], PLASTER),
                  P.face([of[j], of[i], ob[i], ob[j]], PLASTER), P.face([hf[i], hf[j], hb[j], hb[i]], PLASTER)]
    P.comp.append(('plaster', faces, False))

# ---------------- checks ----------------
def snap_check(ob):
    """WALL MODULE CONTRACT: exact bbox, nothing beyond x=+-1, end faces planar + X-mirror identical, end face covers the
    frame section (no see-through at a seam). Raises AssertionError on failure."""
    me = ob.data; mw = ob.matrix_world; eps = 1e-5
    vs = [mw @ v.co for v in me.vertices]
    lo = [min(v[i] for v in vs) for i in range(3)]; hi = [max(v[i] for v in vs) for i in range(3)]
    exp_lo, exp_hi = (-HX, -HY, 0.0), (HX, HY, H)
    for i in range(3):
        assert abs(lo[i] - exp_lo[i]) < eps and abs(hi[i] - exp_hi[i]) < eps, ('bbox', i, lo[i], hi[i])
    ends = {1: [], -1: []}
    for p in me.polygons:
        pts = [mw @ me.vertices[k].co for k in p.vertices]
        for s in (1, -1):
            if all(abs(q.x - s * HX) < eps for q in pts):
                n = (mw.to_3x3() @ p.normal).normalized()
                assert abs(abs(n.x) - 1) < 1e-6, ('end face not planar/vertical', s, tuple(n))
                ends[s].append([(round(q.y, 5), round(q.z, 5)) for q in pts])
    key = lambda polys: sorted(tuple(sorted(f)) for f in polys)
    assert key(ends[1]) == key(ends[-1]), 'end faces at +1 and -1 differ (modules would not butt cleanly)'
    def inside(y, z, poly):
        c = False; n = len(poly)
        for i in range(n):
            (y1, z1), (y2, z2) = poly[i], poly[(i + 1) % n]
            if (z1 > z) != (z2 > z) and y < (y2 - y1) * (z - z1) / (z2 - z1) + y1: c = not c
        return c
    miss = 0
    for iy in range(13):
        for iz in range(97):
            y = -Y_FRAME + 0.012 + iy * (2 * Y_FRAME - 0.024) / 12; z = 0.012 + iz * (H - 0.024) / 96
            if not any(inside(y, z, f) for f in ends[1]): miss += 1
    assert miss == 0, ('end face does not cover the frame section', miss)
    area = sum(abs(sum(f[i][0] * f[(i + 1) % len(f)][1] - f[(i + 1) % len(f)][0] * f[i][1] for i in range(len(f)))) / 2 for f in ends[1])
    print(f'SNAP OK  bbox {hi[0]-lo[0]:.3f} x {hi[1]-lo[1]:.3f} x {hi[2]-lo[2]:.3f} | end faces {len(ends[1])}+{len(ends[-1])} identical, '
          f'planar at x=+-{HX:.3f}, covered frame section {2*Y_FRAME:.3f} x {H:.3f} (face area sum {area:.4f} m2)')

def ymirror_check(ob):
    vs = [v.co.copy() for v in ob.data.vertices]
    kd = kdtree.KDTree(len(vs))
    for i, v in enumerate(vs): kd.insert(v, i)
    kd.balance()
    m = max(kd.find(Vector((v.x, -v.y, v.z)))[2] for v in vs)
    print(f'  Y-mirror (front == back) max dev {m:.6f}')
    assert m < 1e-5

# ---------------- build ----------------
def build():
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    img = pc.atlas_image(TEX_NAME, os.path.join(ART if MODE == 'export' else CHECK_DIR, 'Textures' if MODE == 'export' else '', TEX_NAME), PAL)
    mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    P = build_wall(KIND)
    ncomp = {}
    for nm, faces, _ in P.comp: ncomp[nm] = ncomp.get(nm, 0) + sum(len(f.verts) - 2 for f in faces)
    print('  tris per part', ncomp)
    body = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)
    bpy.context.view_layer.update()
    tot = pc.report({'Body': body})
    assert BUDGET[0] <= tot <= BUDGET[1], ('budget', tot, BUDGET)
    print(f'  budget {BUDGET[0]}-{BUDGET[1]}: OK ({tot})')
    snap_check(body); ymirror_check(body)
    for s in (1, -1):        # brace end corners must stay hidden inside the post / plate
        bz0, bx1 = KINDS[KIND]['brace']
        A, B = Vector((s * PX0, 0, bz0)), Vector((s * bx1, 0, PLATE_Z[0])); u = (B - A).normalized(); e2 = Vector((u.z, 0, -u.x))
        e0, e1 = brace_ext(u)
        for p, ok in ((A - u * e0, lambda q: PX0 - 1e-6 <= abs(q.x) <= HX), (B + u * e1, lambda q: PLATE_Z[0] <= q.z <= H)):
            for c in (p + e2 * BR_W, p - e2 * BR_W): assert ok(c), ('brace end visible', tuple(c))
    print('  brace ends hidden in post/plate: OK')
    return root, coll, img, mat, body

def render(out, view=None, pct=50, extra=None):
    g = dict(OUT=out, PCT=pct, SCENE_NAME=bpy.context.scene.name, COLLECTION=NAME)
    if view: g['VIEW_DIR'] = view
    exec(open(os.path.join(HERE, 'render_preview.py')).read(), g)

def thumb(src, dst, h=128):
    im = bpy.data.images.load(src); w = round(im.size[0] * h / im.size[1]); im.scale(w, h)
    im.filepath_raw = dst; im.file_format = 'PNG'; im.save(); bpy.data.images.remove(im)

def verify_headless(fbx):
    """re-import the FBX into the same (now emptied) scene: nodes, tris, dims, rotation/scale, texture found"""
    sc = bpy.context.scene
    for c in list(sc.collection.children): sc.collection.children.unlink(c)
    before_i = set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx); bpy.context.view_layer.update()
    obs = list(sc.objects); tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
        print('VERIFY', o.name, o.type, 'parent', o.parent.name if o.parent else None, 'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()],
              'scale', [round(s, 4) for s in o.matrix_world.to_scale()], 'loc', [round(x, 4) for x in o.matrix_world.translation])
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('VERIFY total tris', tot, 'bbox', [round(a, 4) for a in lo], [round(b, 4) for b in hi])
    print('VERIFY images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])

ROOTOB, COLL, IMG, MAT, BODY = build()

if MODE == 'check':
    os.makedirs(CHECK_DIR, exist_ok=True)
    tag = f'{KIND}_r{ROUND}'
    front = os.path.join(CHECK_DIR, tag + '_front.png'); render(front)
    thumb(front, os.path.join(CHECK_DIR, tag + '_thumb128.png'))
    if '--back' in ARGV: render(os.path.join(CHECK_DIR, tag + '_back.png'), view=(-0.42, 1.0, 0.36))
    if '--pair' in ARGV:     # two butted copies (linked mesh at x = +2) to prove the snap
        dup = bpy.data.objects.new(NAME + '_SnapTest', BODY.data); dup.location = (W, 0, 0); COLL.objects.link(dup); bpy.context.view_layer.update()
        render(os.path.join(CHECK_DIR, tag + '_pair.png'), view=(0.30, -1.0, 0.30))
        bpy.data.objects.remove(dup, do_unlink=True)
elif MODE == 'export':
    assert KIND == 'window', 'only MOD-04 is exported by this pilot'
    fbx = os.path.join(ART, 'Meshes', NAME + '.fbx')
    pc.export(NAME, COLL, ROOTOB, fbx)
    fbm = os.path.join(ART, 'Meshes', NAME + '.fbm'); os.makedirs(fbm, exist_ok=True)
    shutil.copy2(os.path.join(ART, 'Textures', TEX_NAME), os.path.join(fbm, TEX_NAME))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), pct=100)
    verify_headless(fbx)
