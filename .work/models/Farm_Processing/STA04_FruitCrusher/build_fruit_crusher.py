# STA-04 Fruit crusher -> FMS_Workshop_STA_04 (Farm Processing pack). Headless, idempotent:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_fruit_crusher.py -- <mode> [views]
#   mode: build  = build + checks + check renders (50% and 128 px thumbnail) to %TEMP%\FarmProcessing_check\STA-04
#                  optional 2nd arg 'views' adds side / back / top renders
#         export = build + checks + FBX export + .blend lib + final preview + FBX re-import verify
# Shared helpers (read-only): ../_common/processing_common.py. Stand/caps/bolts adapted from STA-05 build_juice_press.py,
# headless scene/render/verify structure from STA-03 build_butter_churn.py.
import bpy, math, os, sys, importlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'STA04_FruitCrusher')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, rect_prism, basis

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_04'
TEX_NAME = 'T_FarmProcessing_STA04_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA04'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'STA-04')
BUDGET = (1600, 2300)

# ---------------- palette: cells 0-14 identical to STA-05 (13/14 warm grey plate), 15 = roller beige ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#B4AA9D', '#978D82', '#C9BFB1']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, PLATE, PLATE_D, ROLLER = range(16)

# ---------------- dimensions (m); front = -Y, crank on -X ----------------
HEAD_C, HEAD_S, HEAD_Z0, HEAD_Z1 = (0.37, 0.18), 0.15, 0.46, 0.62      # leg head blocks (tops = housing bottom)
LEG_FOOT_C, LEG_FOOT_S, LEG_TOP_S = (0.43, 0.23), 0.13, 0.105
RAIL_X, RAIL_W, RAIL_Z0, RAIL_Z1 = 0.37, 0.10, 0.52, 0.62               # top side rails (with the heads they carry the housing)
STR_Z = 0.26                                                             # low stretchers
HX_IN, HX_OUT, HY, HZ0, HZ1 = 0.295, 0.36, 0.20, 0.62, 1.00              # housing: plate inner/outer x, back y, z range
HYF = 0.24                                                               # housing front y (-HYF): window flush with the rollers
PIL_X0, PIL_X1, PIL_D = 0.285, 0.36, 0.04                                 # front pillars (flange)
LIN_Z0 = 0.955                                                           # lintel bottom
ROLL_N, ROLL_R, ROLL_L, AX_R = 12, 0.0758, 0.275, 0.026                 # 12-sided round rollers, vertex toward the front
ROLL_APO = ROLL_R * math.cos(math.pi / ROLL_N)
CHUTE_ROLL_Y = -HYF - 0.005 + ROLL_R * math.cos(math.pi / 8)            # preserve the accepted chute geometry
ROLL_Y = -HYF - 0.020 + ROLL_R                                        # both rollers 20 mm proud of the window
ZB = HZ0 + 0.015 + ROLL_R; ZA = ZB + 2 * ROLL_R + 0.013                  # lower / upper roller axes
BOSS_R, BOSS_X1 = 0.085, HX_OUT + 0.04
CAP_R, CAP_RB, CAP_X1 = 0.05, 0.035, HX_OUT + 0.025                               # bearing caps: upper (right), lower (both sides)
CHUTE_A, CHUTE_Y1, CHUTE_HW, CH_T, FLOOR_Z0 = math.radians(28), -0.38, 0.30, 0.03, 0.62
BOARD_T, BOARD_H = 0.035, 0.07                                          # low side walls (7 cm above the floor)
CR_X0, CR_X1, CR_ARM, CR_W, CR_T = BOSS_X1 - 0.005, 0.50, 0.30, 0.06, 0.05          # crank: hub start, elbow x, total drop, bar section
CR_KINK = (0.10, 0.17, 0.045)                                            # Z-kink: straight down 0.10, offset -X 0.045 by 0.17
GRIP_DZ, GRIP_X1, GRIP_R = 0.27, 0.74, 0.066
BOLTS = ((-0.04, 0.975), (0.162, 0.975), (0.162, 0.66), (-0.04, 0.655))  # (y, z) on both side plates
HOP = [  # hopper cross-section rings (w, d, corner chamfer, z), torus-lofted; rests on the housing top HZ1
    (2 * HX_OUT, HY + HYF, 0.012, HZ1), (0.80, 0.62, 0.016, 1.155), (0.86, 0.68, 0.02, 1.155), (0.86, 0.68, 0.02, 1.185),
    (0.84, 0.66, 0.016, 1.20), (0.76, 0.58, 0.014, 1.20), (2 * HX_OUT - 0.04, HY + HYF - 0.04, 0.01, HZ1)]
HOP_YC = (HY - HYF) / 2

def zf(y):
    """chute floor top surface height at depth y (CHUTE_A slope, FLOOR_Z0 under the roller axis)"""
    return FLOOR_Z0 + math.tan(CHUTE_A) * (y - CHUTE_ROLL_Y)

# ---------------- extra helpers (own; processing_common is read-only) ----------------
def xprism(P, cname, x0, x1, poly_yz, side, cap0, cap1):
    return P.loft(cname, [[Vector((x, y, z)) for y, z in poly_yz] for x in (x0, x1)], side, cap0, cap1)

def polysweep(P, cname, pts, prof, ref, side, cap0, cap1):
    """sweep a 2D profile along a polyline, mitred rings at the bends, profile frame parallel-transported"""
    pts = [Vector(p) for p in pts]
    _, e1, e2 = basis(pts[1] - pts[0], ref)
    ring = lambda c, a, b: [c + a * x + b * y for x, y in prof]
    rings = [ring(pts[0], e1, e2)]
    for i in range(1, len(pts) - 1):
        t1 = (pts[i] - pts[i - 1]).normalized(); t2 = (pts[i + 1] - pts[i]).normalized(); nb = (t1 + t2).normalized()
        rings.append([q + t1 * ((pts[i] - q).dot(nb) / t1.dot(nb)) for q in ring(pts[i], e1, e2)])
        rot = t1.rotation_difference(t2); e1 = rot @ e1; e2 = rot @ e2
    rings.append(ring(pts[-1], e1, e2))
    return P.loft(cname, rings, side, cap0, cap1)

def xspec(xs, x0, x1):
    """[(x, scale)] -> sweep spec (t, scale, 0)"""
    return [((x - x0) / (x1 - x0), s, 0.0) for x, s in xs]

# ---------------- parts ----------------
def build_frame():
    P = Part('Frame')
    # --- stand: splayed chamfered legs, head blocks, red caps ---
    k = LEG_TOP_S / LEG_FOOT_S
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * HEAD_C[0], sy * HEAD_C[1]
            rect_prism(P, 'head', cx, cy, HEAD_S, HEAD_S, 0.012,
                       [(HEAD_Z0, 0.006), (HEAD_Z0 + 0.006, 0), (HEAD_Z1 - 0.03, 0), (HEAD_Z1, 0.03)], WOOD, WOOD, WOOD)
            foot = (sx * LEG_FOOT_C[0], sy * LEG_FOOT_C[1], 0.0); top = (cx, cy, HEAD_Z0 + 0.04)
            sweep(P, 'leg', foot, top, chamf_rect(LEG_FOOT_S, LEG_FOOT_S, 0.012), [(0.0, 1.0, 0.0), (1.0, k, 0.0)],
                  WOOD, WOOD_M, WOOD, flat0=True, ground=True)
            zc = (HEAD_Z0 + HEAD_Z1 - 0.03) / 2
            if sy < 0:   # front heads: cap on the front face
                y0 = cy - HEAD_S / 2 + 0.004; y1 = cy - HEAD_S / 2 - 0.013
                sweep(P, 'redcap', (cx, y0, zc), (cx, y1, zc), chamf_rect(0.055, 0.055, 0.008),
                      [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.005)], RED, RED, RED, ref=(0, 0, 1))
            else:        # back heads: cap (rail peg end) on the outer side face
                x0 = cx + sx * (HEAD_S / 2 - 0.004); x1 = cx + sx * (HEAD_S / 2 + 0.013)
                sweep(P, 'redcap', (x0, cy, zc), (x1, cy, zc), chamf_rect(0.055, 0.055, 0.008),
                      [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.005)], RED, RED, RED, ref=(0, 0, 1))
    # top side rails (housing rests on them) and back top rail
    rp = chamf_rect(RAIL_Z1 - RAIL_Z0, RAIL_W, 0.012); rz = (RAIL_Z0 + RAIL_Z1) / 2
    for sx in (-1, 1):
        sweep(P, 'rail_side', (sx * RAIL_X, -HEAD_C[1] + HEAD_S / 2 - 0.01, rz), (sx * RAIL_X, HEAD_C[1] - HEAD_S / 2 + 0.01, rz),
              rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    sweep(P, 'rail_back', (-HEAD_C[0] + HEAD_S / 2 - 0.01, HEAD_C[1], rz), (HEAD_C[0] - HEAD_S / 2 + 0.01, HEAD_C[1], rz),
          chamf_rect(RAIL_Z1 - RAIL_Z0, 0.08, 0.012), [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    # low stretchers between the leg centre lines
    t = STR_Z / (HEAD_Z0 + 0.04)
    lx = LEG_FOOT_C[0] + (HEAD_C[0] - LEG_FOOT_C[0]) * t; ly = LEG_FOOT_C[1] + (HEAD_C[1] - LEG_FOOT_C[1]) * t
    sp = chamf_rect(0.07, 0.06, 0.01)
    for sy in (-1, 1):
        sweep(P, 'str_x', (-lx, sy * ly, STR_Z), (lx, sy * ly, STR_Z), sp, [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 0, 1))
    for sx in (-1, 1):
        sweep(P, 'str_y', (sx * lx, -ly, STR_Z - 0.012), (sx * lx, ly, STR_Z - 0.012), sp, [(0, 1, 0), (1, 1, 0)], WOOD_M, WOOD_M, WOOD_M, ref=(0, 0, 1))
    # --- metal housing on the side rails ---
    for sx in (-1, 1):
        cx = sx * (HX_IN + HX_OUT) / 2
        py0 = -HYF + PIL_D - 0.005
        rect_prism(P, 'plate', cx, (py0 + HY) / 2, HX_OUT - HX_IN, HY - py0, 0.008, [(HZ0, 0), (HZ1, 0)], METAL_D, METAL_D, METAL_D)
        rect_prism(P, 'pillar', sx * (PIL_X0 + PIL_X1) / 2, -HYF + PIL_D / 2, PIL_X1 - PIL_X0, PIL_D, 0.008, [(HZ0, 0), (HZ1, 0)], METAL_D, METAL_D, METAL_D)
    rect_prism(P, 'backplate', 0, HY - 0.02, 2 * HX_IN + 0.01, 0.04, 0.006, [(HZ0, 0), (HZ1, 0)], METAL_D, METAL_D, METAL_D)
    sweep(P, 'lintel', (-PIL_X0 - 0.005, -HYF + PIL_D / 2, (LIN_Z0 + HZ1) / 2), (PIL_X0 + 0.005, -HYF + PIL_D / 2, (LIN_Z0 + HZ1) / 2),
          chamf_rect(HZ1 - LIN_Z0, PIL_D, 0.008), [(0, 1, 0), (1, 1, 0)], METAL_D, METAL_D, METAL_D, ref=(0, 0, 1))
    # hex bolts on the side plates (top-front, top-back, bottom-back), both sides
    for sx in (-1, 1):
        for by, bz in BOLTS:
            sweep(P, 'bolt', (sx * (HX_OUT - 0.004), by, bz), (sx * (HX_OUT + 0.022), by, bz), ngon(0.024, 6, math.pi / 2),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.006)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    # round bearing boss disc (left, upper axle; crank side) and small bearing caps (lower axle both sides, upper axle right)
    sweep(P, 'boss', (-(HX_OUT - 0.004), ROLL_Y, ZA), (-BOSS_X1, ROLL_Y, ZA), ngon(BOSS_R, 12, math.pi / 12),
          [(0, 1, 0), (0.62, 1, 0), (1, 0.84, 0)], METAL_L, METAL_L, METAL_L, ref=(0, 0, 1))
    for nm, sx, z, r in (('bcap', -1, ZB, CAP_RB), ('bcap', 1, ZB, CAP_RB), ('bcapA', 1, ZA, CAP_R)):
        sweep(P, nm, (sx * (HX_OUT - 0.004), ROLL_Y, z), (sx * CAP_X1, ROLL_Y, z), ngon(r, 8, math.pi / 8),
              [(0, 1, 0), (0.55, 1, 0), (1, 0.8, 0)], METAL_L, METAL_L, METAL_L, ref=(0, 0, 1))
    # --- hopper: square funnel on the housing top (one closed torus loft: outer wall, lip, inner wall, bottom ring) ---
    rings = [[Vector((x, y + HOP_YC, z)) for x, y in chamf_rect(w, d, c)] for w, d, c, z in HOP]
    P.torus_loft('hopper', rings, lambda j, kk: (METAL, METAL, METAL_L, METAL_L, METAL_L, METAL, METAL)[j])   # grey metal pair
    # --- open U-chute (grey metal): flat floor sloping CHUTE_A forward from just under the lower roller to the lip in front
    #     of the front heads, two low side walls BOARD_H high along the whole length (no flap over the rollers) ---
    a = CHUTE_A; n = Vector((0, -math.sin(a), math.cos(a)))
    y0 = CHUTE_ROLL_Y + 0.02                             # accepted floor position (between the plates)
    p0 = Vector((0, y0, zf(y0))) - n * CH_T / 2; p1 = Vector((0, CHUTE_Y1, zf(CHUTE_Y1))) - n * CH_T / 2
    L = (p1 - p0).length
    sweep(P, 'floor', p0, p1, chamf_rect(2 * CHUTE_HW, CH_T, 0.006), [(0, 1, 0), (1 - 0.008 / L, 1, 0), (1, 1, 0.005)],
          METAL_L, METAL, METAL, ref=(1, 0, 0))
    yb = -HYF - 0.005 - 0.012                         # accepted walls; x clearance keeps them outside the chamfered ends
    zl = zf(CHUTE_Y1)
    poly = [(yb, zf(yb) - 0.01), (CHUTE_Y1, zl - 0.01), (CHUTE_Y1, zl + BOARD_H - 0.018), (CHUTE_Y1 + 0.018, zl + BOARD_H),
            (yb, zf(yb) + BOARD_H)]
    for sx in (-1, 1):
        xa, xb = sx * (CHUTE_HW - BOARD_T), sx * CHUTE_HW
        xprism(P, 'board', min(xa, xb), max(xa, xb), poly, METAL, METAL, METAL)
    # housing bottom plate behind the chute floor (hides the stand when looking down the hopper throat)
    rect_prism(P, 'bottom', 0, (y0 - 0.01 + HY - 0.02) / 2, 2 * HX_IN + 0.01, HY - 0.02 - y0 + 0.01, 0.004, [(HZ0 - 0.02, 0), (HZ0 + 0.008, 0)],
               METAL_D, METAL_D, METAL_D)
    return P

def roller(name, cname, z, left_x):
    P = Part(name)
    x0, x1 = -left_x, CAP_X1 + 0.01
    s = AX_R / ROLL_R
    # Integrated end discs: closed, shared-ring mesh; dark hub faces and bevels,
    # then a beige chamfer into the full-radius cylinder. No overlapping caps.
    xs = [(x0, s), (-ROLL_L, s), (-ROLL_L, 0.82), (-ROLL_L + 0.035, 0.94),
          (-ROLL_L + 0.052, 1), (ROLL_L - 0.052, 1),
          (ROLL_L - 0.035, 0.94), (ROLL_L, 0.82), (ROLL_L, s), (x1, s)]
    sweep(P, cname, (x0, ROLL_Y, z), (x1, ROLL_Y, z), ngon(ROLL_R, ROLL_N, 0), xspec(xs, x0, x1),
          lambda j, kk: ROLLER if 3 <= j <= 5 else METAL_D, METAL_D, METAL_D, ref=(0, 0, 1))
    return P

def build_crank():
    """metal crank with the ref's Z-kink: axle out of the boss -> elbow -> arm down -> offset outwards -> down to the handle;
    round hub collar on the boss; faceted wooden handle pointing -X"""
    P = Part('Crank')
    sweep(P, 'hub', (-CR_X0, ROLL_Y, ZA), (-(CR_X0 + 0.035), ROLL_Y, ZA), ngon(0.048, 12, math.pi / 12),
          [(0, 1, 0), (0.6, 1, 0), (1, 0.85, 0)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    d1, d2, off = CR_KINK
    pts = [(-(CR_X0 + 0.03), ROLL_Y, ZA), (-CR_X1, ROLL_Y, ZA), (-CR_X1, ROLL_Y, ZA - d1),
           (-(CR_X1 + off), ROLL_Y, ZA - d2), (-(CR_X1 + off), ROLL_Y, ZA - CR_ARM)]
    polysweep(P, 'crank_bar', pts, chamf_rect(CR_W, CR_T, 0.011), (0, 1, 0), METAL_L, METAL_L, METAL_L)
    gx0 = CR_X1 + off + CR_T / 2 - 0.004; zg = ZA - GRIP_DZ
    xs = [(-gx0, 0.62), (-gx0 - 0.012, 1), (-GRIP_X1 + 0.016, 1), (-GRIP_X1, 0.7)]
    sweep(P, 'grip', (-gx0, ROLL_Y, zg), (-GRIP_X1, ROLL_Y, zg), ngon(GRIP_R, 8, math.pi / 8), xspec(xs, -gx0, -GRIP_X1),
          WOOD, WOOD, WOOD, ref=(0, 0, 1))
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
    for P, piv, skip in ((build_frame(), (0, 0, 0), ('boss', 'bcapA')),
                         (roller('Roller_A', 'rollerA', ZA, BOSS_X1 + 0.012), (0, ROLL_Y, ZA), ('rollerA',)),
                         (roller('Roller_B', 'rollerB', ZB, CAP_X1 + 0.01), (0, ROLL_Y, ZB), ()),
                         (build_crank(), (-BOSS_X1, ROLL_Y, ZA), ('hub', 'crank_bar', 'grip'))):
        obs[P.name] = pc.to_object(P, NAME, coll, mat, piv, root, mirror_skip=skip)
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    print(f'  budget {BUDGET[0]}-{BUDGET[1]} ->', 'OK' if BUDGET[0] <= tot <= BUDGET[1] else 'OUT OF BUDGET')
    # cross-part numeric checks
    assert tot <= BUDGET[1], 'triangle budget exceeded'
    assert ZA - ZB > 2 * ROLL_R and ZA + ROLL_R < LIN_Z0
    assert ROLL_L < PIL_X0 and ROLL_L < HX_IN
    # Bounding circle vs sloped chute plane: conservative for the faceted mesh.
    floor_clear = (ZB - zf(ROLL_Y)) * math.cos(CHUTE_A) - ROLL_R
    assert floor_clear > 0, 'lower roller intersects chute floor'
    def tree(ob, barrel_only=False):
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        faces = [list(p.vertices) for p in ob.data.polygons
                 if not barrel_only or all(abs(pts[i].x) <= ROLL_L + 1e-6 for i in p.vertices)]
        return BVHTree.FromPolygons(pts, faces)
    frame_tree = tree(obs['Frame'])
    for key in ('Roller_A', 'Roller_B'):
        hits = len(tree(obs[key], True).overlap(frame_tree))
        print('  INTERSECTION', key, 'barrel vs housing/chute/frame', hits)
        assert hits == 0, 'roller barrel intersects frame'
    assert not tree(obs['Roller_A']).overlap(tree(obs['Roller_B'])), 'rollers intersect'
    print('  CLEARANCE conservative roller-floor normal', round(floor_clear, 5),
          '| roller-pillar x', round(PIL_X0 - ROLL_L, 5),
          '| protrusion', round(-HYF - (ROLL_Y - ROLL_R), 5))
    print('  roller gap (circumradius)', round(ZA - ZB - 2 * ROLL_R, 4), '| upper top', round(ZA + ROLL_R, 4), '< lintel', LIN_Z0,
          '| lower bottom', round(ZB - ROLL_R, 4), '> floor top under axis', round(zf(ROLL_Y), 4))
    for dy in (0.02, 0.0, -0.03):
        yy = ROLL_Y + dy; rb = ZB - ROLL_R           # conservative circular bottom bound
        print('    floor vs lower roller at y', yy, 'floor', round(zf(yy), 4), 'roller bottom', round(rb, 4), 'clear', round(rb - zf(yy), 4))
    print('  boss z', (round(ZA - BOSS_R, 3), round(ZA + BOSS_R, 3)), 'lower cap top', round(ZB + CAP_RB, 3),
          '| bolt-boss min dist', round(min(math.hypot(by - ROLL_Y, bz - ZA) for by, bz in BOLTS) - BOSS_R - 0.024, 4),
          '| bolt-lowercap', round(min(math.hypot(by - ROLL_Y, bz - ZB) for by, bz in BOLTS) - CAP_RB - 0.024, 4))
    print('  roller end', ROLL_L, '< plate inner', HX_IN, '| pillar inner', PIL_X0, '| both roller fronts y', round(ROLL_Y - ROLL_R, 4),
          'window front', -HYF, '| wall start y', round(-HYF - 0.005 - 0.012, 3), '| boss front y', round(ROLL_Y - BOSS_R, 3),
          '| front head face y', -(HEAD_C[1] + HEAD_S / 2), '| wall height', BOARD_H)
    print('  chute outer', CHUTE_HW, 'seated 5 mm into the front heads (inner x', HEAD_C[0] - HEAD_S / 2, ')', '| chute lip z', round(zf(CHUTE_Y1), 3), 'y', CHUTE_Y1)
    print('  housing bottom', HZ0, '= rail top', RAIL_Z1, '| plates x', (HX_IN, HX_OUT), 'over rail x', (RAIL_X - RAIL_W / 2, RAIL_X + RAIL_W / 2),
          '| hopper bottom', HOP[0][3], '= housing top', HZ1)
    print('  crank upper arm x', -(CR_X1 - CR_T / 2), 'sweeps down to z', round(ZA - CR_KINK[1], 3), '> head top', HEAD_Z1,
          '| lower arm x', -(CR_X1 + CR_KINK[2] - CR_T / 2), 'vs head outer', -(HEAD_C[0] + HEAD_S / 2))
    print('  crank arm inner x', -(CR_X1 - CR_T / 2), 'vs head outer x', -(HEAD_C[0] + HEAD_S / 2), '| crank lowest z',
          round(ZA - CR_ARM, 3), '| grip x', -GRIP_X1, '| crank sweep radius', round(CR_ARM + CR_W / 2, 3))
    # Roller_A axle end inside the crank hub
    ra = obs['Roller_A']; mn = min((ra.matrix_world @ v.co).x for v in ra.data.vertices)
    print('  Roller_A axle min x', round(mn, 4), '< crank hub start', -CR_X0, '| boss outer', -BOSS_X1)
    return obs, root, coll, img, mat

def render(out, pct, view=None):
    g = {'OUT': out, 'PCT': pct, '__name__': 'preview'}
    if view: g['VIEW_DIR'] = view
    elif os.environ.get('STA04_VIEW'): g['VIEW_DIR'] = tuple(float(v) for v in os.environ['STA04_VIEW'].split(','))   # camera trials
    if os.environ.get('STA04_LENS'): g['LENS'] = float(os.environ['STA04_LENS'])
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
    tag = ARGS[2] if len(ARGS) > 2 else 'r'
    render(os.path.join(CHECK_DIR, tag + '_ref.png'), 50)
    render(os.path.join(CHECK_DIR, tag + '_thumb.png'), 10)
    if len(ARGS) > 1 and ARGS[1] == 'views':
        render(os.path.join(CHECK_DIR, tag + '_side.png'), 35, (-1.0, -0.12, 0.15))
        render(os.path.join(CHECK_DIR, tag + '_back.png'), 35, (0.45, 1.0, 0.35))
        render(os.path.join(CHECK_DIR, tag + '_top.png'), 35, (-0.2, -0.45, 1.0))
elif MODE == 'export':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify(_fbx)
