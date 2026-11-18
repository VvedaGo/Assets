# STA-06 Hand millstones / quern -> FMS_Workshop_STA_06 (Farm Processing pack). Headless, idempotent:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_hand_mill.py -- <mode> [tag]
#   mode: build  = build + checks + check renders (<tag>_ref.png 50%, <tag>_thumb.png 128 px) to %TEMP%\FarmProcessing_check\STA-06
#         export = build + checks + FBX export + .blend lib + final preview + FBX re-import verify
# Shared helpers (read-only): ../_common/processing_common.py. Structure copied from STA-03 build_butter_churn.py.
import bpy, math, os, sys, importlib
from mathutils import Vector

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'STA06_HandMill')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_06'
TEX_NAME = 'T_FarmProcessing_STA06_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA06'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
TAG = ARGS[1] if len(ARGS) > 1 else 'r1'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'STA-06')

# ---------------- palette: cells 0-12 identical to STA-05/STA-03, 13-15 stones ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#A7A39A', '#8C8B88', '#66635E']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, STONE, STONE_D, STONE_DD = range(16)

# ---------------- dimensions (m); front = -Y; angles: math angle in XY (deg) ----------------
N = 16
S = 1.08                                   # uniform scale applied to every part after the build (round 3: legs shortened
                                           # by DZ, whole model scaled back up to the 0.9 m catalogue height); constants below are pre-scale
DZ = -0.070                                # round 3: support 7 cm lower (ref base squatter)
A = 0.325                                  # stone apothem (faces centred at -90 + k*22.5 deg)
Z_RB, Z_RT = 0.270 + DZ, 0.325 + DZ                  # support ring bottom / top
RI, RO = 0.220, 0.365                      # ring inner / outer apothem
Z_L0, Z_L1, CH_L0, CH_L1 = Z_RT, 0.445 + DZ, 0.010, 0.010      # lower stone
Z_U0, Z_U1, CH_U0, CH_U1 = Z_L1, 0.545 + DZ, 0.010, 0.016      # upper stone (rests on the lower one)
HOLE_RC, HOLE_CH = 0.082, 0.012            # grain inlet hole circumradius (16-gon, off 0) + top chamfer
LEG_ANG = (45, 135, -135, -45)
LEG_R0, LEG_R1, LEG_W0, LEG_W1, LEG_C = 0.460, 0.405, 0.074, 0.088, 0.012   # foot / top radius + width
LEG_TOP = Z_RB + 0.02
CAP_R, CAP_W, CAP_Z0, CAP_Z1, CAP_TOPCH = 0.405, 0.122, 0.250 + DZ, 0.400 + DZ, 0.022
PLATE_S, PLATE_Z, PLATE_P = 0.050, 0.328 + DZ, 0.010
STR_Z, STR_S, STR_C = 0.110, 0.062, 0.011  # stretchers
OUT_ANG = -157.5                           # flour outlet facet (67.5 deg from -Y toward -X)
OUT_ZC, FR_HW, FR_HH, OP_HW, OP_HH, FR_P = 0.385 + DZ, 0.075, 0.050, 0.055, 0.033, 0.014
CH_ANG, CH_LEN, CH_HW, CH_H, CH_T, CH_FT = 25.0, 0.200, 0.051, 0.050, 0.011, 0.011
CH_Z0 = OUT_ZC - OP_HH + 0.003             # chute floor bottom at the stone face
HOP_ZN, HOP_ZT, HOP_RN, HOP_RT, HOP_RIM = Z_U1 + 0.050, Z_U1 + 0.250, 0.046, 0.188, 0.017
COL_Z0, COL_RT, COL_RI = Z_U1 - 0.040, 0.052, 0.036
CRANK_ANG, CRANK_RAD = -45.0, 0.180
ARM_S = 0.034
ARM_PATH = [(0.0, 0.040), (0.0, 0.095), (0.075, 0.165), (0.270, 0.165)]   # (radial offset from peg, height above stone top)
GRIP_S = 0.255

def uvec(deg): return Vector((math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0.0))
def ring(rc, z, n=N, off=0.5, c=(0.0, 0.0)):
    return [Vector((c[0] + rc * math.cos(-math.pi / 2 + (k + off) * 2 * math.pi / n), c[1] + rc * math.sin(-math.pi / 2 + (k + off) * 2 * math.pi / n), z)) for k in range(n)]
def ringA(a, z, n=N, off=0.5, c=(0.0, 0.0)): return ring(a / math.cos(math.pi / n), z, n, off, c)
def crect(cx, cy, z, u, w, h, c, d=0.0):
    """horizontal chamfered rect ring, local x along u (radial); inset d rebuilds a smaller rect (no corner flip)"""
    k = math.tan(math.pi / 8); v = Vector((-u.y, u.x, 0))
    return [Vector((cx, cy, z)) + u * x + v * y for x, y in chamf_rect(w - 2 * d, h - 2 * d, max(c - k * d, 0.3 * c))]
def leg_r(z): return LEG_R0 + (LEG_R1 - LEG_R0) * z / LEG_TOP

# ---------------- parts ----------------
def build_base():
    P = Part('Base')
    # support ring (16-gon annulus, chamfered outer edges)
    P.torus_loft('ring', [ringA(RI, Z_RB), ringA(RO - 0.008, Z_RB), ringA(RO, Z_RB + 0.008), ringA(RO, Z_RT - 0.012),
                          ringA(RO - 0.012, Z_RT), ringA(RI, Z_RT)],
                 lambda j, k: (WOOD_DD, WOOD_M, WOOD, WOOD, WOOD, WOOD_D)[j])
    # lower stone (solid 16-gon), rests on the ring top
    P.loft('lower', [ringA(A - CH_L0, Z_L0), ringA(A, Z_L0 + CH_L0), ringA(A, Z_L1 - CH_L1), ringA(A - CH_L1, Z_L1)],
           lambda j, k: (STONE, STONE, STONE_DD)[j], STONE_DD, STONE)
    for ang in LEG_ANG:
        u = uvec(ang)
        # splayed square leg (radially aligned), foot on z=0, top inside the cap
        rings = []
        for z, d in ((0.0, 0.006), (0.006, 0.0), (LEG_TOP, 0.0)):
            c = u * leg_r(z); w = LEG_W0 + (LEG_W1 - LEG_W0) * z / LEG_TOP
            rings.append(crect(c.x, c.y, z, u, w, w, LEG_C, d))
        P.loft('leg', rings, lambda j, k: WOOD_M if j == 0 else (WOOD if k % 2 == 0 else WOOD_M), WOOD_DD, WOOD, ground=True)
        # cap block at the ring with a chamfered top
        c = u * CAP_R
        rings = [crect(c.x, c.y, z, u, CAP_W, CAP_W, 0.012, d) for z, d in
                 ((CAP_Z0, 0.008), (CAP_Z0 + 0.008, 0.0), (CAP_Z1 - CAP_TOPCH, 0.0), (CAP_Z1, CAP_TOPCH))]
        P.loft('cap', rings, lambda j, k: (WOOD_M, WOOD, WOOD)[j], WOOD_DD, WOOD)
        # red square plate on the outward face
        s0 = CAP_R + CAP_W / 2
        sweep(P, 'plate', u * (s0 - 0.003) + Vector((0, 0, PLATE_Z)), u * (s0 + PLATE_P) + Vector((0, 0, PLATE_Z)),
              [(PLATE_S / 2, -PLATE_S / 2), (PLATE_S / 2, PLATE_S / 2), (-PLATE_S / 2, PLATE_S / 2), (-PLATE_S / 2, -PLATE_S / 2)],
              [(0, 1, 0), (0.65, 1, 0), (1, 1, 0.003)], RED_D, RED_D, RED, ref=(0, 0, 1))
    # stretchers between adjacent legs (end at the leg centre lines)
    a = leg_r(STR_Z) / math.sqrt(2)
    prof = chamf_rect(STR_S, STR_S, STR_C)
    for sgn in (-1, 1):
        sweep(P, 'stretcher', (-a, sgn * a, STR_Z), (a, sgn * a, STR_Z), prof, [(0, 1, 0), (1, 1, 0)],
              lambda j, k: WOOD_M if k in (0, 1, 7) else WOOD, WOOD, WOOD, ref=(0, 0, 1))
        sweep(P, 'stretcher', (sgn * a, -a, STR_Z), (sgn * a, a, STR_Z), prof, [(0, 1, 0), (1, 1, 0)],
              lambda j, k: WOOD_M if k in (0, 1, 7) else WOOD, WOOD, WOOD, ref=(0, 0, 1))
    # flour outlet: red frame on one facet, dark opening plate, cream U chute sloping out
    u = uvec(OUT_ANG); t = Vector((-u.y, u.x, 0)); Z = Vector((0, 0, 1)); zc = Vector((0, 0, OUT_ZC))
    rect = lambda s, hw, hh: [zc + u * s + t * x + Z * y for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
    P.torus_loft('frame', [rect(A - 0.006, OP_HW, OP_HH), rect(A - 0.006, FR_HW, FR_HH), rect(A + FR_P, FR_HW, FR_HH),
                           rect(A + FR_P, OP_HW, OP_HH)], lambda j, k: (RED_D, RED_D, RED, RED_D)[j])
    P.loft('opening', [rect(A - 0.008, OP_HW + 0.003, OP_HH + 0.003), rect(A + 0.002, OP_HW + 0.003, OP_HH + 0.003)],
           STONE_DD, STONE_DD, STONE_DD)
    ca, sa = math.cos(math.radians(CH_ANG)), math.sin(math.radians(CH_ANG))
    dvec = u * ca - Z * sa; nvec = u * sa + Z * ca
    s0 = A - 0.012; c0 = u * s0 + Z * CH_Z0
    pr = [(-CH_HW, 0), (CH_HW, 0), (CH_HW, CH_H), (CH_HW - CH_T, CH_H), (CH_HW - CH_T, CH_FT), (-CH_HW + CH_T, CH_FT),
          (-CH_HW + CH_T, CH_H), (-CH_HW, CH_H)]
    r0 = [c0 + t * x + nvec * y for x, y in pr]
    r0 = [p - dvec * ((p.dot(u) - s0) / dvec.dot(u)) for p in r0]          # start ring projected onto the vertical plane s0
    r1 = [c0 + dvec * CH_LEN + t * x + nvec * y for x, y in pr]
    P.loft('chute', [r0, r1], lambda j, k: (CREAM_D, CREAM_B, CREAM, CREAM_IN, CREAM, CREAM_IN, CREAM, CREAM_B)[k], CREAM_D, CREAM_D)
    return P

def build_upper():
    P = Part('UpperStone')
    rh = lambda r, z: ring(r, z, N, 0.0)
    P.torus_loft('stone', [rh(HOLE_RC, Z_U0), ringA(A - CH_U0, Z_U0), ringA(A, Z_U0 + CH_U0), ringA(A, Z_U1 - CH_U1),
                           ringA(A - CH_U1, Z_U1), rh(HOLE_RC + HOLE_CH, Z_U1), rh(HOLE_RC, Z_U1 - HOLE_CH)],
                 lambda j, k: (STONE_DD, STONE_DD, STONE_D, STONE_D, STONE_D, STONE_DD, STONE_DD)[j])
    # red collar in the eye: 8-gon frustum tube, outer bottom vertices embedded 1 mm into the hole wall (hidden contact)
    r8 = lambda r, z: ring(r, z, 8, 0.0)
    P.torus_loft('collar', [r8(COL_RI, COL_Z0), r8(HOLE_RC + 0.001, COL_Z0), r8(COL_RT, HOP_ZN), r8(COL_RI, HOP_ZN)],
                 lambda j, k: (RED_D, RED, RED_D, RED_D)[j])
    # octagonal funnel hopper on the collar
    P.torus_loft('hopper', [r8(HOP_RN, HOP_ZN), r8(HOP_RT, HOP_ZT), r8(HOP_RT - HOP_RIM, HOP_ZT), r8(COL_RI - 0.002, HOP_ZN)],
                 lambda j, k: (CREAM_B, CREAM, CREAM_IN, CREAM_D)[j])
    return P

def build_crank():
    P = Part('Crank')
    u = uvec(CRANK_ANG); pc0 = u * CRANK_RAD; c = (pc0.x, pc0.y); Z = Vector((0, 0, 1)); side = Vector((-u.y, u.x, 0))
    P.loft('flange', [ring(0.064, Z_U1 - 0.003, 8, 0.5, c), ring(0.064, Z_U1 + 0.014, 8, 0.5, c), ring(0.055, Z_U1 + 0.023, 8, 0.5, c)],
           lambda j, k: METAL, METAL_D, METAL_L)
    P.loft('nut', [ring(0.042, Z_U1 + 0.020, 8, 0.5, c), ring(0.042, Z_U1 + 0.050, 8, 0.5, c), ring(0.035, Z_U1 + 0.057, 8, 0.5, c)],
           lambda j, k: METAL, METAL_D, METAL_L)
    # square-section arm along the bent path (mitred rings, as the STA-03 staple handles)
    pts = [pc0 + u * s + Z * (Z_U1 + h) for s, h in ARM_PATH]; h2 = ARM_S / 2; rings = []
    for i, p in enumerate(pts):
        d1 = (p - pts[i - 1]).normalized() if i > 0 else None
        d2 = (pts[i + 1] - p).normalized() if i < len(pts) - 1 else None
        tt = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / tt.dot(d1) if d1 and d2 else 1.0
        nn = tt.cross(side).normalized() * h2 * k
        rings.append([p + nn - side * h2, p + nn + side * h2, p - nn + side * h2, p - nn - side * h2])
    P.loft('arm', rings, lambda j, k: METAL_L if k == 0 else METAL, METAL_D, METAL_D)
    # handle collar + octagonal wooden grip with chamfered cap
    hc = pc0 + u * GRIP_S; c2 = (hc.x, hc.y); ztop_arm = Z_U1 + ARM_PATH[-1][1] + h2
    P.loft('hcollar', [ring(0.024, ztop_arm - 0.003, 8, 0.5, c2), ring(0.024, ztop_arm + 0.018, 8, 0.5, c2)], METAL, METAL_D, METAL_L)
    zg = ztop_arm + 0.016
    P.loft('grip', [ring(0.026, zg, 8, 0.5, c2), ring(0.033, zg + 0.135, 8, 0.5, c2), ring(0.022, zg + 0.160, 8, 0.5, c2)],
           lambda j, k: WOOD if k % 2 == 0 else WOOD_M, WOOD_D, WOOD)
    return P, (pc0.x, pc0.y, Z_U1)

# ---------------- scene ----------------
def clear_scene():
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
    def sc(P):
        for v in P.bm.verts: v.co *= S
        return P
    obs['Base'] = pc.to_object(sc(build_base()), NAME, coll, mat, (0, 0, 0), root, mirror_skip=('frame', 'opening', 'chute'))
    obs['UpperStone'] = pc.to_object(sc(build_upper()), NAME, coll, mat, (0, 0, Z_U0 * S), root)
    Pc, piv = build_crank(); sc(Pc); piv = tuple(x * S for x in piv)
    obs['Crank'] = pc.to_object(Pc, NAME, coll, mat, piv, root, mirror_skip=('flange', 'nut', 'arm', 'hcollar', 'grip'))
    obs['Crank'].parent = obs['UpperStone']; obs['Crank'].location = Vector(piv) - Vector((0, 0, Z_U0 * S))
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    print('  budget 1000-2000 ->', 'OK' if 1000 <= tot <= 2000 else 'OUT OF BUDGET')
    W = lambda o: [o.matrix_world @ v.co for v in o.data.vertices]
    up, cr = W(obs['UpperStone']), W(obs['Crank'])
    print('  (numbers below are pre-scale constants unless measured; scale', S, ')')
    print('  upper stone bottom', round(min(p.z for p in up), 4), '= lower stone top', round(Z_L1 * S, 4), '| lower stone bottom', round(Z_L0 * S, 4), '= ring top', round(Z_RT * S, 4),
          '| stone apothem', A, 'ring', RI, '..', RO)
    print('  crank min z', round(min(p.z for p in cr), 4), '(stone top', round(Z_U1 * S, 4), ') flange outer radius from axis',
          round(CRANK_RAD + 0.064, 3), '< top flat', round(A - CH_U1, 3), '| top z', round(max(p.z for p in cr), 4),
          '| handle radial', round(CRANK_RAD + GRIP_S, 3))
    print('  crank world pivot', [round(x, 4) for x in obs['Crank'].matrix_world.translation], 'parent', obs['Crank'].parent.name)
    ta = math.tan(math.radians(CH_ANG)); s0 = A - 0.012
    print('  chute bottom z at ring outer apothem', round(CH_Z0 - (RO - s0) * ta, 4), 'vs ring top', Z_RT,
          '| chute end bottom z', round(CH_Z0 - CH_LEN * math.cos(math.radians(CH_ANG)) * ta, 3),
          '| chute in opening: z', round(CH_Z0, 3), '..', round(CH_Z0 + CH_H, 3), 'opening', OUT_ZC - OP_HH, '..', OUT_ZC + OP_HH,
          'half widths', CH_HW, '<', OP_HW, '| facet half width', round(A * math.tan(math.pi / N), 4), '> frame', FR_HW)
    print('  cap to stone clearance', round(CAP_R - CAP_W / 2 - A, 4), '| stretcher z', STR_Z, 'leg spacing a', round(leg_r(STR_Z) / math.sqrt(2), 3))
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
    render(os.path.join(CHECK_DIR, TAG + '_ref.png'), 50)
    render(os.path.join(CHECK_DIR, TAG + '_thumb.png'), 10)
    if len(ARGS) > 2 and ARGS[2] == 'side':
        render(os.path.join(CHECK_DIR, TAG + '_back.png'), 40, (0.7, 0.75, 0.35))
elif MODE == 'export':
    # Blender 5.2 FBX exporter bug: with bake_space_transform a 2nd-level child (Crank under UpperStone) is written as
    # G P^-1 G^-1 P C G^-1 instead of G C G^-1 (fbx_utils.fbx_object_matrix uses the parent's FBX-local matrix, which is
    # only right for children of the root). Pre-compensate the crank's local matrix during export only (C' = P^-1 G P C),
    # then restore it; the FBX dump / re-import below prove the written transform.
    from bpy_extras.io_utils import axis_conversion
    G = axis_conversion(to_forward='-Z', to_up='Y').to_4x4()
    cr, up = OBS['Crank'], OBS['UpperStone']; saved = cr.matrix_basis.copy(); Pm = up.matrix_local.copy()
    cr.matrix_local = Pm.inverted() @ G @ Pm @ cr.matrix_local; bpy.context.view_layer.update()
    _fbx = pc.export(NAME, COLL, ROOTOB, os.path.join(ART, 'Meshes', NAME + '.fbx'))
    cr.matrix_basis = saved; bpy.context.view_layer.update()
    print('  crank restored world pivot', [round(x, 4) for x in cr.matrix_world.translation], 'rot', [round(math.degrees(x), 2) for x in cr.matrix_world.to_euler()])
    pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), COLL, MAT, IMG)
    render(os.path.join(ART, 'Previews', NAME + '_Preview.png'), 100)
    verify(_fbx)
