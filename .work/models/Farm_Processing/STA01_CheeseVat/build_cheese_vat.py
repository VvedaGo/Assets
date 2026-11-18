# STA-01 Cheese-making vat -> FMS_Workshop_STA_01 (Farm Processing pack). Headless, one call:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_cheese_vat.py -- <mode>
#   mode: build (checks only) | check (+ check render to %TEMP%) | final (+ export, verify, .blend, preview)
# Idempotent: rebuilds only its own collection in scene FMS_Workshop_STA_01_Build. Helpers: ../_common/processing_common.py (read-only).
import bpy, bmesh, math, os, sys, importlib, tempfile
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'STA01_CheeseVat')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, zprism, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_01'
TEX_NAME = 'T_FarmProcessing_STA01_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA01'
CHECK_DIR = os.path.join(tempfile.gettempdir(), 'FarmProcessing_check', 'STA-01')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = argv[0] if argv else globals().get('MODE', 'build')
TAG = argv[1] if len(argv) > 1 else 'r'

# ---------------- palette: cells 0-12 identical to STA-02/05; 13 curd, 14 curd edge, 15 spare ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#E3CD95', '#CDB37A', '#B5835A']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, CURD, CURD_D = range(15)

# ---------------- dimensions (m); front = -Y ----------------
N = 20                                   # pot / ring facets
A0 = -math.pi / 2 + math.pi / N          # face centred on -Y and on +-X (X-mirror exact)
R = 0.41                                 # pot outer wall (vertex radius)
WALL = 0.035
LIP_O, LIP_H = 0.028, 0.05               # rim lip: outward overhang, height
RS, ZS0, ZS1, RIN = R + 0.07, 0.30, 0.40, R - 0.15   # stand top ring board: outer/inner radius, z range
Z0, ZR = ZS1 - 0.003, 0.88               # pot flat bottom rests ON the ring board (3 mm sunk for contact), rim top
ZC = ZR - 0.065                          # curd edge level
HEAD_C, HEAD_S, HEAD_Z0, HEAD_Z1 = 0.36, 0.13, 0.24, ZS1 + 0.025
FOOT_C, FOOT_S, LEG_TOP_S = 0.44, 0.14, 0.115
RAIL_Z = 0.12
BOSS_ZL, BOSS_ZU = ZR - 0.25, ZR - 0.088    # lower / upper hex bolt bosses of each loop handle
# lid
RL = R + LIP_O + 0.002
LID_AZ, LID_TILT = math.radians(205), math.radians(15)   # outward normal azimuth (left, a bit front), lean back towards the pot
LID_SHIFT = 0.24                                          # start offset along the lid's horizontal axis (towards -Y)
# paddle: blade tip B (in the curd) -> top T
PAD_B, PAD_T = Vector((0.13, 0.10, ZC - 0.045)), Vector((0.50, 0.30, 1.10))
BLADE_L, BLADE_W, BLADE_T = 0.22, 0.12, 0.036

def ring(r, z, n=N, a0=A0):
    return [Vector((r * math.cos(a0 + 2 * math.pi * k / n), r * math.sin(a0 + 2 * math.pi * k / n), z)) for k in range(n)]

def poly_sweep(P, cname, pts, prof, plane_n, side, cap0, cap1):
    """planar polyline sweep with mitred joints; prof (x in-plane, y along plane_n)"""
    pts = [Vector(p) for p in pts]; nrm = Vector(plane_n).normalized(); rings = []
    for i, c in enumerate(pts):
        if i == 0: t = (pts[1] - pts[0]).normalized(); s = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); s = 1.0
        else:
            ta = (c - pts[i - 1]).normalized(); tb = (pts[i + 1] - c).normalized(); t = (ta + tb).normalized()
            s = 1.0 / max(0.3, t.dot(ta))
        e1 = nrm.cross(t).normalized()
        rings.append([c + e1 * (x * s) + nrm * y for x, y in prof])
    return P.loft(cname, rings, side, cap0, cap1)

# ---------------- body: pot + curd + handles + stand ----------------
def build_body():
    P = Part('Body')
    ri = R - WALL
    prof = [(R - 0.03, Z0), (R, Z0 + 0.03), (R, ZR - LIP_H - 0.012), (R + LIP_O, ZR - LIP_H), (R + LIP_O, ZR - 0.014),
            (R + LIP_O - 0.014, ZR), (ri + 0.008, ZR), (ri, ZR - 0.008), (ri, ZC), (ri - 0.03, ZC + 0.01), (ri * 0.55, ZC + 0.02)]
    bands = [METAL_D, METAL, METAL_D, METAL, METAL_L, METAL_L, METAL_L, METAL_D, CURD_D, CURD]
    P.loft('pot', [ring(r, z) for r, z in prof], lambda j, k: bands[j], METAL_D, CURD)
    # curd chunks: lumpy faceted mounds, half-sunk into the curd (fixed layout, no randomness)
    def curd_z(x, y):
        r = math.hypot(x, y); t = min(1.0, max(0.0, (r - ri * 0.55) / (ri - 0.03 - ri * 0.55)))
        return ZC + 0.02 - 0.01 * t
    for x, y, rr, rot, h in ((-0.19, 0.14, 0.09, 0.2, 0.03), (0.02, 0.23, 0.08, 0.7, 0.026), (0.21, 0.17, 0.075, 0.4, 0.024),
                             (-0.25, -0.10, 0.08, 0.9, 0.026), (-0.06, 0.0, 0.095, 0.1, 0.032), (0.05, -0.22, 0.08, 0.5, 0.024),
                             (0.24, -0.08, 0.065, 0.3, 0.022), (-0.15, -0.25, 0.07, 0.6, 0.022)):
        sz = curd_z(x, y); h = 1.9 * h
        hexp = [(rr * (1 - 0.18 * (k % 2)) * math.cos(rot + k * math.pi / 3), rr * (1 - 0.18 * (k % 2)) * math.sin(rot + k * math.pi / 3)) for k in range(6)]
        zprism(P, 'chunk', x, y, hexp, [(sz - 0.02, 0), (sz + 0.25 * h, 0), (sz + 0.7 * h, rr * 0.22), (sz + h, rr * 0.52)],
               lambda j, kk: (CREAM_B, CREAM_B, CREAM)[j], CURD, CREAM)
    # handles: chunky round-section (8-gon) loop, 6-segment arc between two hex bolt bosses on the +-X wall face
    apo = R * math.cos(math.pi / N)
    zm, b = (BOSS_ZL + BOSS_ZU) / 2, (BOSS_ZU - BOSS_ZL) / 2
    for sx in (-1, 1):
        for bz in (BOSS_ZL, BOSS_ZU):
            sweep(P, 'boss', (sx * (apo - 0.012), 0, bz), (sx * (apo + 0.03), 0, bz), ngon(0.036, 6, math.pi / 2),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.01)], METAL, METAL, METAL_L, ref=(0, 0, 1))
        arc = []
        for i in range(7):
            t = -math.pi / 2 + math.pi * i / 6
            arc.append((sx * (apo + 0.014 + 0.15 * math.cos(t)), 0, zm + b * math.sin(t) + 0.075 * math.cos(t)))
        poly_sweep(P, 'handle', arc, ngon(0.019, 8, math.pi / 8), (0, 1, 0), METAL, METAL, METAL)
    # stand (low stool): thick chamfered ring board the pot's flat bottom rests on, 4 splayed legs at the diagonals with head
    # blocks under/through the board edge, red caps, low stretchers
    rprof = [(RIN, ZS0), (RS - 0.016, ZS0), (RS, ZS0 + 0.016), (RS, ZS1 - 0.024), (RS - 0.024, ZS1), (RIN, ZS1)]
    P.torus_loft('ring', [ring(r, z) for r, z in rprof], lambda j, k: (WOOD_M, WOOD_M, WOOD, WOOD, WOOD, WOOD_M)[j])
    k = LEG_TOP_S / FOOT_S
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * HEAD_C, sy * HEAD_C
            rect_prism(P, 'head', cx, cy, HEAD_S, HEAD_S, 0.012,
                       [(HEAD_Z0, 0.006), (HEAD_Z0 + 0.006, 0), (HEAD_Z1 - 0.025, 0), (HEAD_Z1, 0.025)], WOOD, WOOD, WOOD)
            sweep(P, 'leg', (sx * FOOT_C, sy * FOOT_C, 0.0), (cx, cy, HEAD_Z0 + 0.04), chamf_rect(FOOT_S, FOOT_S, 0.012),
                  [(0.0, 1.0, 0.0), (1.0, k, 0.0)], WOOD, WOOD_M, WOOD, flat0=True, ground=True)
            y0 = sy * (HEAD_C + HEAD_S / 2 - 0.004); y1 = sy * (HEAD_C + HEAD_S / 2 + 0.013)
            zc = (HEAD_Z0 + HEAD_Z1) / 2 - 0.01
            sweep(P, 'redcap', (cx, y0, zc), (cx, y1, zc), chamf_rect(0.056, 0.056, 0.007),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.005)], RED, RED, RED, ref=(0, 0, 1))
    t = RAIL_Z / (HEAD_Z0 + 0.04)
    l = FOOT_C + (HEAD_C - FOOT_C) * t
    rp = chamf_rect(0.07, 0.06, 0.009)
    for sy in (-1, 1):
        sweep(P, 'rail_x', (-l, sy * l, RAIL_Z), (l, sy * l, RAIL_Z), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    for sx in (-1, 1):
        sweep(P, 'rail_y', (sx * l, -l, RAIL_Z - 0.012), (sx * l, l, RAIL_Z - 0.012), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    return P

# ---------------- lid: built at the origin, then leaned and slid towards the body until it touches ----------------
def build_lid(body_bvh):
    P = Part('Lid')
    nh = Vector((math.cos(LID_AZ), math.sin(LID_AZ), 0))
    n = (nh * math.cos(LID_TILT) + Vector((0, 0, math.sin(LID_TILT)))).normalized()
    u = (-nh * math.sin(LID_TILT) + Vector((0, 0, math.cos(LID_TILT)))).normalized()
    e = u.cross(n).normalized()
    L = lambda x, y, z: e * x + u * y + n * z
    lprof = [(RL - 0.014, 0.0), (RL, 0.014), (RL, 0.03), (RL - 0.04, 0.05), (RL * 0.6, 0.062)]
    rings = [[L(p.x, p.y, z) for p in ring(r, 0)] for r, z in lprof]
    P.loft('lid', rings, lambda j, k: (METAL, METAL, METAL_L, METAL)[j], METAL_D, METAL)
    gp = [L(0, -0.14, 0.04), L(0, -0.115, 0.14), L(0, 0.115, 0.14), L(0, 0.14, 0.04)]
    poly_sweep(P, 'grip', gp, chamf_rect(0.046, 0.052, 0.012), e, METAL, METAL, METAL)
    bm = P.bm
    mz = min(v.co.z for v in bm.verts)
    eh = Vector((e.x, e.y, 0)).normalized(); eh = eh if eh.y < 0 else -eh
    start = nh * 1.3 + eh * -LID_SHIFT + Vector((0, 0, -mz))
    for v in bm.verts: v.co += start
    d = -nh; hits = []
    for v in bm.verts:
        h = body_bvh.ray_cast(v.co, d)
        if h[0] is not None: hits.append(h[3])
    move = min(hits) + 0.0015
    for v in bm.verts: v.co += d * move
    low = min(bm.verts, key=lambda v: v.co.z).co
    piv = Vector((low.x, low.y, 0.0))
    print(f'  lid: slid {move:.3f} m, bottom contact at {[round(x, 3) for x in piv]}')
    return P, piv

# ---------------- paddle ----------------
def build_paddle():
    P = Part('Paddle')
    d = (PAD_T - PAD_B).normalized(); Lt = (PAD_T - PAD_B).length
    bl = BLADE_L / Lt
    # blade: flat (thin along e1, wide along e2 = horizontal), chamfered tip, tapered neck
    sweep(P, 'blade', PAD_B, PAD_B + d * BLADE_L, chamf_rect(BLADE_T, BLADE_W, 0.007),
          [(0, 1, 0.012), (0.06, 1, 0), (0.72, 1, 0), (1, 0.34, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    h0 = PAD_B + d * (BLADE_L * 0.85)
    sweep(P, 'handle', h0, PAD_T, ngon(0.024, 8, math.pi / 8),
          [(0, 1, 0), (0.86, 1, 0), (0.92, 1.22, 0), (1, 1.22, 0.014)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    piv = PAD_B.lerp(PAD_T, 0.5)
    return P, piv

# ---------------- checks / render / verify ----------------
def part_overlap(a, b):
    ba = BVHTree.FromObject(a, bpy.context.evaluated_depsgraph_get()); bb = BVHTree.FromObject(b, bpy.context.evaluated_depsgraph_get())
    return len(ba.overlap(bb)) > 0

def world_bvh(ob):
    me = ob.data; mw = ob.matrix_world
    return BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])

def contact(a, b):
    ba, bb = world_bvh(a), world_bvh(b)
    if ba.overlap(bb): return 0.0
    mw = a.matrix_world
    return min(bb.find_nearest(mw @ v.co)[3] for v in a.data.vertices)

def render(out, pct, view=None):
    g = {'__name__': '__preview__', 'OUT': out, 'PCT': pct}
    if view: g['VIEW_DIR'] = view
    exec(open(os.path.join(HERE, 'render_preview.py'), encoding='utf-8').read(), g)

def verify_headless(fbx):
    sc = bpy.context.scene                      # default (emptied) scene; the build scene stays untouched
    before_o, before_i, before_m = set(bpy.data.objects), set(bpy.data.images), set(bpy.data.materials)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in bpy.data.objects if o not in before_o]
    bpy.context.view_layer.update()
    print('VERIFY nodes', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
            pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler], 'scale', [round(s, 4) for s in o.scale])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)

# ---------------- build ----------------
def build():
    for o in list(bpy.context.scene.objects):              # factory startup: drop default cube/camera/light
        if o.name in ('Cube', 'Camera', 'Light'): bpy.data.objects.remove(o, do_unlink=True)
    coll = pc.clear_collection(NAME)
    if coll.name not in bpy.context.scene.collection.children:   # headless: no window to switch scenes -> export selects here
        bpy.context.scene.collection.children.link(coll)
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), PAL); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    body = build_body()
    body.bm.verts.ensure_lookup_table()
    bvh = BVHTree.FromBMesh(body.bm)
    lid, lpiv = build_lid(bvh)
    pad, ppiv = build_paddle()
    obs = {}
    obs['Body'] = pc.to_object(body, NAME, coll, mat, (0, 0, 0), root, mirror_skip=('chunk',))
    obs['Lid'] = pc.to_object(lid, NAME, coll, mat, tuple(lpiv), root, mirror_skip=('lid', 'grip'))
    obs['Paddle'] = pc.to_object(pad, NAME, coll, mat, tuple(ppiv), root, mirror_skip=('blade', 'handle'))
    bpy.data.scenes[NAME + '_Build'].view_layers[0].update()
    tot = pc.report(obs)
    print(f'  budget 1200-2400: {"OK" if 1200 <= tot <= 2400 else "OUT"}')
    print('  contact lid-body', round(contact(obs['Lid'], obs['Body']), 5), '| paddle-body', round(contact(obs['Paddle'], obs['Body']), 5))
    print('  curd edge z', ZC, 'rim', ZR, '| paddle top', PAD_T.z)
    return obs, root, coll, img, mat

OBS, ROOTOB, COLL, IMG, MAT = build()

if MODE == 'check':
    os.makedirs(CHECK_DIR, exist_ok=True)
    render(os.path.join(CHECK_DIR, f'{TAG}_ref.png'), 50)
    render(os.path.join(CHECK_DIR, f'{TAG}_thumb.png'), 10)
    if len(argv) > 2:
        render(os.path.join(CHECK_DIR, f'{TAG}_side.png'), 40, view=tuple(float(x) for x in argv[2].split(',')))
elif MODE == 'final':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify_headless(_fbx)
