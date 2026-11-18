# STA-05 Basket juice press -> FMS_Workshop_STA_05 (Farm Processing pack, cover/hero model). Idempotent: rebuilds only its own
# collection (in its own scene FMS_Workshop_STA_05_Build). Run inside Blender: MODE = 'build' | 'export'; exec(open(__file__).read())
# Shared helpers: ../_common/processing_common.py (extracted from STA-02; build_cheese_press.py stays standalone).
import bpy, math, os, sys, importlib
from mathutils import Vector

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, inset, sweep, zprism, chamf_spec, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_05'
TEX_NAME = 'T_FarmProcessing_STA05_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA05'
MODE = globals().get('MODE', 'build')

# ---------------- palette: cells 0-12 identical to STA-02 (mergeable), 13/14 = plate grey-beige, 15 spare ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#B4AA9D', '#978D82', '#B5835A']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, PLATE, PLATE_D = range(15)

# ---------------- dimensions (m); front = -Y ----------------
TT_X, TT_Y, TT_Z0, TT_Z1 = 0.535, 0.40, 0.35, 0.47           # table slab half-sizes, z range (basket stands on TT_Z1)
HEAD_C, HEAD_S, HEAD_Z0, HEAD_Z1 = (0.50, 0.385), 0.165, 0.31, 0.525   # leg heads (corner blocks, red caps on front/back)
LEG_FOOT_C, LEG_FOOT_S, LEG_TOP_S = (0.52, 0.43), 0.185, 0.15
RAIL_Z = 0.20
POST_X, POST_S, POST_TOP = 0.50, 0.165, 1.42
BEAM_Z0, BEAM_Z1, BEAM_D = 1.18, 1.32, 0.13
BK_Z1, BK_AO, BK_AI, STAVES = 1.00, 0.38, 0.33, 21         # basket top, outer/inner apothem, stave count
HOOPS = ((0.905, 0.085), (0.68, 0.085))
HOOP_T, RIVET_EVERY = 0.016, 3                       # (centre z, height)
PLATE_R, PLATE_Z0, PLATE_Z1, PLATE_N = 0.315, 0.875, 0.945, 16
COLLAR_Z1 = 1.04
SP_R, SP_r, SP_Z0, SP_Z1, PITCH, TILT = 0.064, 0.046, 1.0, 1.47, 0.075, 0.03
HUB_W, HUB_Z0, HUB_Z1 = 0.17, 1.45, 1.60
BAR_Z, BAR_HALF, BAR_R = 1.525, 0.38, 0.058
SPOUT_Z, SPOUT_A, SPOUT_L, SPOUT_W = 0.575, math.radians(28), 0.32, 0.105
FLANGE_W, FLANGE_H, FLANGE_Y0, FLANGE_Y1 = 0.28, 0.125, -0.35, -0.40
SCREW_PIVOT_Z = (BEAM_Z0 + BEAM_Z1) / 2

# ---------------- parts ----------------
def build_frame():
    P = Part('Frame')
    # table slab (reads as the front/side beams of the bench), chamfered plan corners and top edge
    rect_prism(P, 'slab', 0, 0, 2 * TT_X, 2 * TT_Y, 0.03,
           [(TT_Z0, 0.006), (TT_Z0 + 0.006, 0), (TT_Z1 - 0.014, 0), (TT_Z1, 0.014)], WOOD, WOOD, WOOD)
    k = LEG_TOP_S / LEG_FOOT_S
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * HEAD_C[0], sy * HEAD_C[1]
            # leg head block with chamfered top
            rect_prism(P, 'head', cx, cy, HEAD_S, HEAD_S, 0.012, [(HEAD_Z0, 0.006), (HEAD_Z0 + 0.006, 0), (HEAD_Z1 - 0.03, 0), (HEAD_Z1, 0.03)], WOOD, WOOD, WOOD)
            # splayed tapered leg, flat foot on z=0, top inside the head
            foot = (sx * LEG_FOOT_C[0], sy * LEG_FOOT_C[1], 0.0); top = (cx, cy, HEAD_Z0 + 0.04)
            sweep(P, 'leg', foot, top, chamf_rect(LEG_FOOT_S, LEG_FOOT_S, 0.012), [(0.0, 1.0, 0.0), (1.0, k, 0.0)],
                  WOOD, WOOD_M, WOOD, flat0=True, ground=True)
            # red square cap on the front / back face of the head
            y0 = sy * (HEAD_C[1] + HEAD_S / 2 - 0.004); y1 = sy * (HEAD_C[1] + HEAD_S / 2 + 0.013)
            sweep(P, 'redcap', (cx, y0, 0.425), (cx, y1, 0.425), chamf_rect(0.066, 0.066, 0.008),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.005)], RED, RED, RED, ref=(0, 0, 1))
    # stretchers at RAIL_Z between the leg centre lines
    t = RAIL_Z / (HEAD_Z0 + 0.04)
    lx = LEG_FOOT_C[0] + (HEAD_C[0] - LEG_FOOT_C[0]) * t; ly = LEG_FOOT_C[1] + (HEAD_C[1] - LEG_FOOT_C[1]) * t
    rp = chamf_rect(0.08, 0.065, 0.01)
    for sy in (-1, 1):
        sweep(P, 'rail_x', (-lx, sy * ly, RAIL_Z), (lx, sy * ly, RAIL_Z), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    for sx in (-1, 1):
        sweep(P, 'rail_y', (sx * lx, -ly, RAIL_Z - 0.012), (sx * lx, ly, RAIL_Z - 0.012), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    # back-plane diagonal braces "/ \" from the back stretcher up to the slab underside
    bp = chamf_rect(0.07, 0.06, 0.009)
    for sx in (-1, 1):
        sweep(P, 'brace', (sx * (lx - 0.07), ly - 0.005, RAIL_Z - 0.01), (sx * 0.15, TT_Y - 0.05, TT_Z0 + 0.025), bp,
              [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 1, 0))
    # posts with pyramid-chamfered tops
    for sx in (-1, 1):
        rect_prism(P, 'post', sx * POST_X, 0, POST_S, POST_S, 0.014, [(TT_Z1 - 0.03, 0), (POST_TOP - 0.045, 0), (POST_TOP, 0.04)], WOOD, WOOD, WOOD)
    # crossbeam (runs into the posts)
    sweep(P, 'beam', (-POST_X, 0, SCREW_PIVOT_Z), (POST_X, 0, SCREW_PIVOT_Z), chamf_rect(BEAM_Z1 - BEAM_Z0, BEAM_D, 0.012),
          [(0, 1, 0), (1, 1, 0)], lambda j, k: WOOD if k in (0, 1, 2) else WOOD_M, WOOD, WOOD, ref=(0, 0, 1))   # darker front/back/bottom like the ref
    # hex bolts on the post front/back faces at beam height
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * (POST_S / 2 - 0.004); y1 = sy * (POST_S / 2 + 0.026)
            sweep(P, 'bolt', (sx * POST_X, y0, SCREW_PIVOT_Z), (sx * POST_X, y1, SCREW_PIVOT_Z), ngon(0.05, 6, math.pi / 2),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.012)], METAL, METAL, METAL, ref=(0, 0, 1))
    return P

def build_screw():
    P = Part('Screw')
    n = 8; ang = [2 * math.pi * k / n + math.pi / 8 for k in range(n)]
    def ring(z, r, tilt):
        return [Vector((r * math.cos(a), r * math.sin(a), z + tilt * math.cos(a))) for a in ang]
    rings = [ring(SP_Z0, SP_r, 0.0)]
    z = SP_Z0 + TILT + 0.006; i = 0
    while z < SP_Z1 - TILT - 0.006:
        rings.append(ring(z, SP_R if i % 2 == 0 else SP_r, TILT)); z += PITCH / 2; i += 1
    rings.append(ring(SP_Z1, SP_r, 0.0))
    P.loft('spindle', rings, lambda j, k: METAL if j % 2 == 0 else METAL_D, METAL, METAL)
    # red chamfered hub block
    rect_prism(P, 'hub', 0, 0, HUB_W, HUB_W, 0.03,
           [(HUB_Z0, 0.024), (HUB_Z0 + 0.024, 0), (HUB_Z1 - 0.024, 0), (HUB_Z1, 0.024)], RED, RED, RED)
    # wooden T-bar: thin near the hub, thicker faceted ends with big end chamfers
    sweep(P, 'bar', (-BAR_HALF, 0, BAR_Z), (BAR_HALF, 0, BAR_Z), ngon(BAR_R, 8, math.pi / 8),
          [(0, 1, 0.02), (0.035, 1, 0), (0.12, 1, 0), (0.32, 0.68, 0), (0.68, 0.68, 0), (0.88, 1, 0), (0.965, 1, 0), (1, 1, 0.02)],
          WOOD, WOOD, WOOD, ref=(0, 0, 1))
    return P

def build_plate():
    P = Part('Plate')
    zprism(P, 'plate', 0, 0, ngon(PLATE_R, PLATE_N, math.pi / PLATE_N),
           [(PLATE_Z0, 0.006), (PLATE_Z0 + 0.006, 0), (PLATE_Z1 - 0.02, 0), (PLATE_Z1, 0.02)], PLATE_D, PLATE_D, PLATE)
    oc = ngon(0.085, 8, math.pi / 8)
    zprism(P, 'collar_base', 0, 0, ngon(0.105, 8, math.pi / 8), [(PLATE_Z1 - 0.01, 0), (PLATE_Z1 + 0.02, 0), (PLATE_Z1 + 0.03, 0.01)],
           METAL, METAL, METAL)
    zprism(P, 'collar', 0, 0, oc, [(PLATE_Z1 + 0.025, 0), (COLLAR_Z1 - 0.016, 0), (COLLAR_Z1, 0.014)], METAL, METAL, METAL_L)
    return P

def build_basket():
    P = Part('Basket')
    d = 2 * math.pi / STAVES; gap = 0.0025; ch = 0.009; tch = 0.011
    for k in range(STAVES):
        c = -math.pi / 2 + k * d; a, b = c - d / 2, c + d / 2
        ro = BK_AO / math.cos(d / 2); ri = BK_AI / math.cos(d / 2)
        ua, ub = Vector((math.cos(a), math.sin(a))), Vector((math.cos(b), math.sin(b)))
        na, nb = Vector((-ua.y, ua.x)), Vector((-ub.y, ub.x))
        fa = (ub * ro - ua * ro).normalized()
        pts = [ua * ri + na * gap, ua * (ro - ch) + na * gap, ua * ro + fa * (ch + gap),
               ub * ro - fa * (ch + gap), ub * (ro - ch) - nb * gap, ub * ri - nb * gap]
        prof = [(p.x, p.y) for p in pts]
        rings = [[Vector((x, y, z)) for x, y in inset(prof, dd)] for z, dd in ((TT_Z1, 0), (BK_Z1 - tch, 0), (BK_Z1, tch))]
        outer = CREAM if k % 2 == 0 else CREAM_B
        sides = {0: CREAM_D, 1: CREAM_D, 2: outer, 3: CREAM_D, 4: CREAM_D, 5: CREAM_IN}
        P.loft('stave', rings, lambda j, kk: sides[kk] if j == 0 else (CREAM_IN if kk == 5 else CREAM), CREAM_IN, CREAM)
    # hoops: 20-gon bands aligned with the stave faces, rectangular section; hex rivets every 2nd stave
    for hi, (zc, h) in enumerate(HOOPS):
        aoi, aoo = BK_AO - 0.004, BK_AO + HOOP_T
        def hring(apo, z):
            r = apo / math.cos(d / 2)
            return [Vector((r * math.cos(-math.pi / 2 + (k + 0.5) * d), r * math.sin(-math.pi / 2 + (k + 0.5) * d), z)) for k in range(STAVES)]
        P.torus_loft('hoop', [hring(aoi, zc - h / 2), hring(aoo, zc - h / 2), hring(aoo, zc + h / 2), hring(aoi, zc + h / 2)], METAL_D)
        for k in range(0, STAVES, RIVET_EVERY):
            if hi == 1 and k == 0: continue                    # front rivet of the lower hoop sits under the spout flange
            c = -math.pi / 2 + k * d; u = Vector((math.cos(c), math.sin(c), 0))
            p0 = Vector((0, 0, zc)) + u * (aoo - 0.003); p1 = Vector((0, 0, zc)) + u * (aoo + 0.016)
            sweep(P, 'rivet', p0, p1, ngon(0.024, 6, math.pi / 2), [(0, 1, 0), (1, 0.72, 0)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    # juice outlet: bolted flange plate + square open spout sloping forward/down
    fz = SPOUT_Z
    sweep(P, 'flange', (0, FLANGE_Y0, fz), (0, FLANGE_Y1, fz), chamf_rect(FLANGE_H, FLANGE_W, 0.02),
          [(0, 1, 0), (0.7, 1, 0), (1, 1, 0.007)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    for sx in (-1, 1):
        sweep(P, 'fbolt', (sx * 0.105, FLANGE_Y1 + 0.004, fz), (sx * 0.105, FLANGE_Y1 - 0.02, fz), ngon(0.028, 6, math.pi / 2),
              [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.006)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    dirv = Vector((0, -math.cos(SPOUT_A), -math.sin(SPOUT_A)))
    s0 = Vector((0, FLANGE_Y0 + 0.01, fz)); s1 = s0 + dirv * SPOUT_L
    wall = 0.016; deep = 0.12 / SPOUT_L; si = 1 - 2 * wall / SPOUT_W   # inner ring = scaled profile (no corner flip)
    sweep(P, 'spout', s0, s1, chamf_rect(SPOUT_W, SPOUT_W, 0.008),
          [(0, 1, 0), (1 - 0.006 / SPOUT_L, 1, 0), (1, 1, 0.004), (1, si, 0), (1 - deep, si, 0)],
          lambda j, k: (METAL, METAL, METAL_L, METAL_D)[j], METAL, METAL_D, ref=(1, 0, 0))
    return P

# ---------------- build ----------------
def build():
    coll = pc.clear_collection(NAME)
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), PAL); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    obs = {}
    for P, piv, skip in ((build_frame(), (0, 0, 0), ()), (build_screw(), (0, 0, SCREW_PIVOT_Z), ('spindle',)),
                         (build_plate(), (0, 0, (PLATE_Z0 + PLATE_Z1) / 2), ()), (build_basket(), (0, 0, TT_Z1), ())):
        obs[P.name] = pc.to_object(P, NAME, coll, mat, piv, root, mirror_skip=skip)
    bpy.data.scenes[NAME + '_Build'].view_layers[0].update()
    pc.report(obs)
    sd = 2 * math.pi / STAVES
    hoop_v = (BK_AO + HOOP_T) / math.cos(sd / 2)
    print('  plate R', PLATE_R, '< basket inner apothem', BK_AI, '| plate top', PLATE_Z1, '< rim', BK_Z1, '| collar top', COLLAR_Z1)
    print('  hoop vertex radius', round(hoop_v, 4), 'post inner face', POST_X - POST_S / 2, 'clearance', round(POST_X - POST_S / 2 - hoop_v, 4))
    print('  spindle', (SP_Z0, SP_Z1), 'crossbeam', (BEAM_Z0, BEAM_Z1), 'hub bottom', HUB_Z0, '-> screw travel down', round(HUB_Z0 - BEAM_Z1, 3))
    tip = Vector((0, FLANGE_Y0 + 0.01, SPOUT_Z)) + Vector((0, -math.cos(SPOUT_A), -math.sin(SPOUT_A))) * SPOUT_L
    print('  spout tip', [round(x, 3) for x in tip], '| slab front y', -TT_Y, 'top', TT_Z1)
    return obs, root, coll, img, mat

OBS, ROOTOB, COLL, IMG, MAT = build()

if MODE == 'export':
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    pc.verify(_fbx)
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
