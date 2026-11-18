# STA-03 Upright butter churn -> FMS_Workshop_STA_03 (Farm Processing pack). Headless, idempotent:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_butter_churn.py -- <mode>
#   mode: build  = build + checks + check renders (50% and 128 px thumbnail) to %TEMP%\FarmProcessing_check\STA-03
#         export = build + checks + FBX export + .blend lib + final preview + FBX re-import verify
# Shared helpers (read-only): ../_common/processing_common.py. Stave/hoop/rivet code adapted from STA-05 build_juice_press.py.
import bpy, math, os, sys, importlib
from mathutils import Vector

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'STA03_ButterChurn')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_03'
TEX_NAME = 'T_FarmProcessing_STA03_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA03'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'STA-03')

# ---------------- palette: cells 0-12 identical to STA-05/STA-02, 13 = rod light wood, 14/15 spare ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#C99263', '#B5835A', '#B5835A']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, ROD = range(14)

# ---------------- dimensions (m); front = -Y ----------------
N = 16                                   # staves / hoop / lid segments (faces centred at -90 deg + k * 22.5)
H_B = 0.585                              # barrel top (lid sits here)
AO0, AO1, WALL = 0.214, 0.184, 0.030     # outer apothem at z=0 / at H_B, stave thickness
GAP, BOT_CH = 0.0012, 0.004              # stave seam half-gap, outer bottom chamfer
HOOPS = (0.10, 0.27, 0.545); HOOP_H, HOOP_T = 0.060, 0.014
RIV_R, RIV_H = 0.023, 0.017
LID_R, LID_T, LID_CH, LID_HOLE = 0.203, 0.06, 0.012, 0.028     # lid apothem, thickness, top chamfer, hole circumradius
LID_TOP = H_B + LID_T
GR_RI, GR_RO, GR_H = 0.028, 0.052, 0.030                      # grommet 8-gon circumradii, height above the lid
HAND_X0, HAND_X1, HAND_Y, HAND_H, HAND_S, HAND_R = 0.082, 0.170, 0.012, 0.060, 0.026, 0.022   # red rounded staple handles
ROD_Z0, ROD_TOP = 0.088, 1.0
ROD_R = ((ROD_Z0, 0.0175), (0.67, 0.0175), (0.95, 0.030))   # (z, circumradius) 8-gon
CROSS_Z, CROSS_L, CROSS_W, CROSS_T = 0.083, 0.26, 0.034, 0.026

def apo(z): return AO0 + (AO1 - AO0) * z / H_B
def ring(rc, z, n=N, off=0.5):
    """n-gon ring, vertices between face centres (faces centred at -90 deg + k*360/n)"""
    return [Vector((rc * math.cos(-math.pi / 2 + (k + off) * 2 * math.pi / n), rc * math.sin(-math.pi / 2 + (k + off) * 2 * math.pi / n), z)) for k in range(n)]

# ---------------- parts ----------------
def build_body():
    P = Part('Body'); d = 2 * math.pi / N
    for k in range(N):
        c = -math.pi / 2 + k * d; a, b = c - d / 2, c + d / 2
        ua, ub = Vector((math.cos(a), math.sin(a), 0)), Vector((math.cos(b), math.sin(b), 0))
        na, nb = Vector((-ua.y, ua.x, 0)), Vector((-ub.y, ub.x, 0))
        def prof(z, sh):
            ro = (apo(z) - sh) / math.cos(d / 2); ri = (apo(z) - WALL) / math.cos(d / 2); zz = Vector((0, 0, z))
            return [zz + ua * ri + na * GAP, zz + ua * ro + na * GAP, zz + ub * ro - nb * GAP, zz + ub * ri - nb * GAP]
        rings = [prof(0.0, BOT_CH), prof(BOT_CH, 0.0), prof(H_B, 0.0)]
        sides = {0: WOOD_M, 1: WOOD, 2: WOOD_M, 3: WOOD_DD}
        P.loft('stave', rings, lambda j, kk: (WOOD_M if kk == 1 else sides[kk]) if j == 0 else sides[kk], WOOD_DD, WOOD_M, ground=True)
    # hidden bottom board (8-gon, sunk into the staves): closes the open bottom so seams do not show the backdrop
    rb = (apo(0.0) - WALL + 0.002) / math.cos(math.pi / 8)      # corners sit in the staves, below the outer bottom chamfer
    P.loft('bottom', [ring(rb, 0.0, 8), ring(rb, 0.03, 8)], WOOD_DD, WOOD_DD, WOOD_DD, ground=True)
    for zc in HOOPS:
        z0, z1 = zc - HOOP_H / 2, zc + HOOP_H / 2
        rc = lambda a, z: a / math.cos(d / 2)
        P.torus_loft('hoop', [ring(rc(apo(z0) - 0.003, z0), z0), ring(rc(apo(z0) + HOOP_T, z0), z0),
                              ring(rc(apo(z1) + HOOP_T, z1), z1), ring(rc(apo(z1) - 0.003, z1), z1)],
                     lambda j, k: WOOD_D if j == 1 else WOOD_DD)
        for ang in (45, 135, 225, 315):
            u = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0)); a0 = apo(zc) + HOOP_T
            sweep(P, 'rivet', Vector((0, 0, zc)) + u * (a0 - 0.004), Vector((0, 0, zc)) + u * (a0 + RIV_H),
                  ngon(RIV_R, 6, math.pi / 2), [(0, 1, 0), (1, 0.72, 0)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    return P

def build_lid():
    P = Part('Lid'); z0, z1 = H_B, LID_TOP
    rl = LID_R / math.cos(math.pi / N); rch = (LID_R - LID_CH) / math.cos(math.pi / N)
    # closed ring section: hole bottom -> outer bottom -> outer top-chamfer -> top inset -> hole top
    P.torus_loft('lid', [ring(LID_HOLE, z0), ring(rl, z0), ring(rl, z1 - LID_CH), ring(rch, z1), ring(LID_HOLE, z1)],
                 lambda j, k: (CREAM_D, CREAM_B, CREAM_B, CREAM, CREAM_IN)[j])
    # octagonal metal grommet around the rod hole (sunk 3 mm into the lid)
    gb, gt = z1 - 0.003, z1 + GR_H
    P.torus_loft('grommet', [ring(GR_RI, gb, 8), ring(GR_RO, gb, 8), ring(GR_RO - 0.007, gt, 8), ring(GR_RI, gt, 8)],
                 lambda j, k: (METAL_D, METAL, METAL_L, METAL_D)[j])
    # two red staple handles (legs sunk 5 mm into the lid), long axis along X
    # rounded staples: square section swept along leg -> 3-segment bend -> bar -> 3-segment bend -> leg (mitred rings)
    s = HAND_S; h = s / 2; R = HAND_R; zt = z1 + HAND_H - h; Y = Vector((0, 1, 0))
    path = [(HAND_X0, z1 - 0.005)]
    path += [(HAND_X0 + R + R * math.cos(math.radians(a)), zt - R + R * math.sin(math.radians(a))) for a in (180, 150, 120, 90)]
    path += [(HAND_X1 - R + R * math.cos(math.radians(a)), zt - R + R * math.sin(math.radians(a))) for a in (90, 60, 30, 0)]
    path += [(HAND_X1, z1 - 0.005)]
    for sx in (-1, 1):
        pts = [Vector((sx * x, HAND_Y, z)) for x, z in path]; rings = []
        for i, c in enumerate(pts):
            d1 = (c - pts[i - 1]).normalized() if i > 0 else None
            d2 = (pts[i + 1] - c).normalized() if i < len(pts) - 1 else None
            t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
            k = 1.0 / t.dot(d1) if d1 and d2 else 1.0           # mitre scale keeps the section thickness in the bends
            nn = t.cross(Y).normalized() * h * k
            rings.append([c + nn - Y * h, c + nn + Y * h, c - nn + Y * h, c - nn - Y * h])
        P.loft('handle', rings, RED, RED_D, RED_D)
    return P

def build_dasher():
    P = Part('Dasher'); n = 8
    rings = [ring(r, z, n) for z, r in ROD_R] + [ring(ROD_R[-1][1] * 0.86, ROD_TOP - 0.022, n), ring(ROD_R[-1][1] * 0.5, ROD_TOP, n)]
    P.loft('rod', rings, ROD, ROD, ROD)
    # cross of two boards at the bottom (inside the barrel)
    for w, h in ((CROSS_L, CROSS_W), (CROSS_W, CROSS_L)):
        sweep(P, 'cross', (0, 0, CROSS_Z - CROSS_T / 2), (0, 0, CROSS_Z + CROSS_T / 2),
              [(w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2)], [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(1, 0, 0))
    return P

# ---------------- scene ----------------
def clear_scene():
    """factory startup: the default scene holds only this asset (own collection rebuilt each run)"""
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects): bpy.data.objects.remove(o, do_unlink=True)
    return coll

def build():
    coll = clear_scene()
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), PAL); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    obs = {}
    for P, piv in ((build_body(), (0, 0, 0)), (build_lid(), (0, 0, H_B)), (build_dasher(), (0, 0, LID_TOP))):
        obs[P.name] = pc.to_object(P, NAME, coll, mat, piv, root)
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    print('  budget 700-1400 (lead-approved overrun to ~1500 for rounded handles) ->', 'OK' if 700 <= tot <= 1500 else 'OUT OF BUDGET')
    print('  stave outer apothem bottom', AO0, 'top', AO1, 'ratio', round(AO0 / AO1, 3), '| hoop proud', HOOP_T, '| hoop z ranges',
          [(round(z - HOOP_H / 2, 3), round(z + HOOP_H / 2, 3)) for z in HOOPS])
    # cross-part numeric checks
    lid_bot = min((obs['Lid'].matrix_world @ v.co).z for v in obs['Lid'].data.vertices)
    print('  lid bottom', round(lid_bot, 4), '= barrel top', H_B, '| lid apothem', LID_R, 'barrel top apothem', AO1, 'overhang', round(LID_R - AO1, 3))
    rod_apo = ROD_R[1][1] * math.cos(math.pi / 8)
    print('  rod apothem at lid', round(rod_apo, 4), '| grommet inner apothem', round(GR_RI * math.cos(math.pi / 8), 4),
          '| lid hole apothem', round(LID_HOLE * math.cos(math.pi / N), 4), '-> clearance', round(GR_RI * math.cos(math.pi / 8) - rod_apo, 4))
    zt = (GR_RI * math.cos(math.pi / 8) / math.cos(math.pi / 8) - ROD_R[1][1]) / (ROD_R[2][1] - ROD_R[1][1]) * (ROD_R[2][0] - ROD_R[1][0]) + ROD_R[1][0]
    print('  dasher travel: down', round(CROSS_Z - CROSS_T / 2 - 0.03, 3), '(cross to bottom board) / up',
          round(H_B - (CROSS_Z + CROSS_T / 2), 3), '(cross to lid) ; rod reaches grommet radius at z', round(zt, 3), '(travel down allowed', round(zt - LID_TOP - GR_H, 3), ')')
    print('  cross half length', CROSS_L / 2, 'corner', round(math.hypot(CROSS_L / 2, CROSS_W / 2), 3), '< inner apothem at cross', round(apo(CROSS_Z) - WALL, 3))
    for zc in HOOPS: print('  hoop', zc, 'outer apothem', round(apo(zc) + HOOP_T, 4))
    return obs, root, coll, img, mat

def render(out, pct, view=None):
    g = {'OUT': out, 'PCT': pct, '__name__': 'preview'}
    if view: g['VIEW_DIR'] = view
    exec(open(os.path.join(HERE, 'render_preview.py')).read(), g)

def verify(fbx):
    """re-import the exported FBX into the (now emptied) scene and print nodes/tris/dims/texture"""
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    before_i = set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx); bpy.context.view_layer.update()
    obs = list(sc.objects); tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  VERIFY', o.name, 'parent', o.parent.name if o.parent else None, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  VERIFY', o.name, o.type, 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler], 'scale', [round(s, 4) for s in o.scale])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  VERIFY nodes', len(obs), 'total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  VERIFY images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])

OBS, ROOTOB, COLL, IMG, MAT = build()
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'build':
    render(os.path.join(CHECK_DIR, 'check.png'), 50)
    render(os.path.join(CHECK_DIR, 'thumb.png'), 10)
    if len(ARGS) > 1 and ARGS[1] == 'side':
        render(os.path.join(CHECK_DIR, 'side.png'), int(ARGS[2]) if len(ARGS) > 2 else 40, (1.0, -0.15, 0.12))
        render(os.path.join(CHECK_DIR, 'top.png'), 40, (0.05, -0.3, 1.0))
elif MODE == 'export':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify(_fbx)
