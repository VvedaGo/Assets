# TRC-01 Tractor_Cab (FMS_Mach_Tractor_Cab) - FarmMachinery pack, stage E7. Procedural, idempotent.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- TRC-01 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/TRC-01/ (+ IMP-01 docking check)
#   export = build + FBX + collection-only .blend + ONE preview + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['TRC-01', 'build']})
#   Live builds go to an own scene + collection 'TRC-01_Tractor_Cab'; nothing else is touched.
# Geometry is written in UNITY coordinates (x right, y up, z forward) and mapped to Blender as (-x, -z, y); the FBX
# export (-Z forward, Y up, baked) gives back the design coordinates in Unity.
import bpy, bmesh, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
IMP01_BLEND = os.path.join(REPO, 'art', 'FarmMachinery', 'Blend', 'FMS_Mach_Plough.blend')   # docking check only
PREFIX, ATLAS = 'FMS_Mach_', 'FarmMachinery_Red'          # shared pack atlas T_FarmMachinery_Red_BaseColor.png
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'TRC-01')
SCENE = OUTER = 'TRC-01_Tractor_Cab'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'TRC-01'
MODE = _a[1] if len(_a) > 1 else 'build'

# FarmMachinery palette (STYLE.md): cells 0-9 standard, 10-15 machinery colours; Red atlas
PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)

# ---------------- design numbers (Unity coordinates, metres; root = footprint centre on the ground) ----------------
WF = dict(d=1.10, w=0.45, y=0.55, x=0.95, z=1.35, lugs=12, lug_h=0.088)    # front wheels
WR = dict(d=1.70, w=0.60, y=0.85, x=0.90, z=-1.00, lugs=16, lug_h=0.10)    # rear wheels (outer tyre edge X 1.20)
CAB_X = 0.55                                     # pillar outer face
CAB_Z0, CAB_Z1 = -1.20, 0.30                     # cab rear / front (pillar outer faces)
DOOR_Z0, DOOR_Z1 = -0.46, 0.19                   # door rear edge / hinge (front edge)
LINK_PIV = (0.60, -1.45)                         # Linkage_Rear: lower-link pivot axis (y, z), axis X
LINK_PIN = (0.45, 0.60, -2.00)                   # lower-link pins X +-0.45, Y 0.60 -> Link3P_Rear (CATALOG item 6)
PTO = (0.70, -2.00)                              # PTO_Rear (y, z)
HITCH = (0.55, -2.15)                            # Hitch_Rear (y, z)
FRONT_Z = 2.21                                   # front face of the weights (= -rear fork end, keeps root at bbox centre)
SEAT = (0.0, 1.60, -0.70)


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))


# ---------------- shared pack wheel (same function as IMP-01 build.py; lug_h optional, default 8 % of D) ----------------
def wheel(P, centre, d, w, lugs, outer=-1, n=16, lug_h=None):
    """tyre n segments near-black (slot 10) with `lugs` blocky lugs standing proud by lug_h (default 8 % of D), cream
    dished rim (3) with dark-cream inner face (4) and a 10-segment hub. Spin axis X; outer face at centre.x + outer*w/2.
    Lowest lug face is centred at the bottom, so the wheel rests on y = centre.y - d / 2."""
    c = Vector(centre); R = d / 2; h = w / 2; o = outer; Rc = R - (0.08 * d if lug_h is None else lug_h)
    def ring(x, r):
        rc = r / math.cos(math.pi / n)
        return [c + V(x, rc * math.cos(math.pi / n + 2 * math.pi * k / n), rc * math.sin(math.pi / n + 2 * math.pi * k / n)) for k in range(n)]
    prof = [(o * 0.20 * h, 0.50 * R), (o * 0.90 * h, 0.60 * R), (o * h, 0.773 * R), (o * 0.85 * h, Rc),
            (-o * 0.85 * h, Rc), (-o * h, 0.773 * R), (-o * 0.90 * h, 0.60 * R), (-o * 0.30 * h, 0.50 * R)]
    band = (CREAM, TYRE, TYRE, TYRE, TYRE, TYRE, CREAM_D)
    P.loft('tyre', [ring(x, r) for x, r in prof], lambda j, k: band[j], CREAM, CREAM_D)
    sweep(P, 'hub', c + V(0, 0, 0), c + V(o * (0.20 * h + 0.04), 0, 0), ngon(0.22 * R, 10, math.pi / 10),
          [(0, 1, 0), (1, 1, 0)], CREAM_D, CREAM_D, CREAM, ref=(0, 1, 0))
    tw = 0.125 * R
    for k in range(lugs):
        a = math.pi + 2 * math.pi * k / lugs
        u = V(0, math.cos(a), math.sin(a))
        x0, x1 = ((-0.98 * h, 0.50 * h) if k % 2 == 0 else (-0.50 * h, 0.98 * h))
        sweep(P, f'lug{k}', c + V(x0, 0, 0), c + V(x1, 0, 0), [(0.75 * R, -tw), (R, -tw), (R, tw), (0.75 * R, tw)],
              [(0, 1, 0), (1, 1, 0)], TYRE, TYRE, TYRE, ref=tuple(u))


# ---------------- helpers ----------------
def tbox(P, n, x0, x1, y0, y1, z0, z1, c=0.0, top=RED, side=RED_D, bot=RED_D, cham=None):
    """axis-aligned box, optional 45 deg chamfer on all four top edges; side may be callable(k): k 0 back(-z) 1 +x 2 front 3 -x"""
    def R(y, d): return [V(x0 + d, y, z0 + d), V(x1 - d, y, z0 + d), V(x1 - d, y, z1 - d), V(x0 + d, y, z1 - d)]
    rings = [R(y0, 0), R(y1 - c, 0), R(y1, c)] if c > 0 else [R(y0, 0), R(y1, 0)]
    ch = top if cham is None else cham
    P.loft(n, rings, lambda j, k: (side(k) if callable(side) else side) if j == 0 else ch, bot, top)


def rod(P, n, p0, p1, r, slot, cap, seg=8):
    a = Vector(p1) - Vector(p0)
    ref = (0, 1, 0) if abs(a.normalized().y) < 0.9 else (1, 0, 0)
    sweep(P, n, Vector(p0), Vector(p1), ngon(r, seg, math.pi / seg), [(0, 1, 0), (1, 1, 0)], slot, cap, cap, ref=ref)


def arch(P, n, cz, cy, r, th, xa, xb, angles):
    """mudguard: chamfered plate swept over a wheel (centre z, y), inner radius r, thickness th, across X xa..xb"""
    pts = [V(0, cy + r * math.sin(math.radians(t)), cz + r * math.cos(math.radians(t))) for t in angles]
    s = 1 if xb > xa else -1
    sec = [(0, xa), (0, xb), (-th + 0.03, xb), (-th, xb - s * 0.03), (-th, xa)]
    sl = {0: RED_D, 1: RED_D, 2: RED, 3: RED, 4: RED_D}
    path_sweep(P, n, pts, (1, 0, 0), sec, lambda j, k: sl[k], RED_D)


def door_frame(P, s, tag):
    """cab door (s = -1 left, +1 right): 4-bar red frame, opaque glass panel, dark handle"""
    xo, xi = s * 0.53, s * 0.46
    X = lambda a, b: (min(a, b), max(a, b))
    x0, x1 = X(xo, xi); hx0, hx1 = X(s * 0.525, s * 0.465)
    tbox(P, f'{tag}_front', x0, x1, 1.41, 2.555, DOOR_Z1 - 0.06, DOOR_Z1, 0, RED, RED, RED)
    tbox(P, f'{tag}_rear', x0, x1, 1.41, 2.555, DOOR_Z0, DOOR_Z0 + 0.06, 0, RED, RED, RED)
    tbox(P, f'{tag}_bottom', hx0, hx1, 1.415, 1.47, DOOR_Z0 + 0.03, DOOR_Z1 - 0.03, 0, RED, RED, RED)
    tbox(P, f'{tag}_top', hx0, hx1, 2.495, 2.55, DOOR_Z0 + 0.03, DOOR_Z1 - 0.03, 0, RED, RED, RED)
    gx0, gx1 = X(s * 0.515, s * 0.495)
    tbox(P, f'{tag}_glass', gx0, gx1, 1.44, 2.52, DOOR_Z0 + 0.04, DOOR_Z1 - 0.04, 0, GLASS, GLASS, GLASS)
    kx0, kx1 = X(s * 0.51, s * 0.55)
    tbox(P, f'{tag}_handle', kx0, kx1, 1.95, 2.00, DOOR_Z0 + 0.10, DOOR_Z0 + 0.22, 0, RUBBER, RUBBER, RUBBER)


# ---------------- parts ----------------
def body_part():
    P = Part('Body')
    # chassis, cab underframe, rear transmission housing (dark), axles
    tbox(P, 'chassis', -0.30, 0.30, 0.52, 0.98, -1.15, 1.95, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'cab_under', -0.50, 0.50, 0.62, 1.30, CAB_Z0, CAB_Z1, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'rear_housing', -0.40, 0.40, 0.50, 1.30, -1.78, -1.10, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'front_axle', -0.89, 0.89, 0.49, 0.59, WF['z'] - 0.05, WF['z'] + 0.05, 0, RUBBER, RUBBER, RUBBER)
    for s in (-1, 1):
        rod(P, f'rear_axle{s}', (s * 0.28, WR['y'], WR['z']), (s * 0.82, WR['y'], WR['z']), 0.09, RUBBER, METAL_D)
    # bonnet: long box, single 45 deg chamfer on the top edges; grille, headlights, front weights
    tbox(P, 'bonnet', -0.42, 0.42, 0.95, 1.85, 0.22, 2.00, 0.08, RED, RED_D, RED_D, RED)
    tbox(P, 'grille', -0.34, 0.34, 1.00, 1.58, 1.99, 2.03, 0, TYRE, TYRE, TYRE)
    for i in range(5):
        x = -0.24 + 0.12 * i
        tbox(P, f'grille_bar{i}', x - 0.03, x + 0.03, 1.05, 1.53, 2.02, 2.06, 0, RUBBER, RUBBER, RUBBER)
    for s in (-1, 1):
        tbox(P, f'headlight{s}', min(s * 0.20, s * 0.34), max(s * 0.20, s * 0.34), 1.64, 1.75, 1.99, 2.04, 0, RUBBER,
             lambda k: LAMP if k == 2 else RUBBER, RUBBER)
    tbox(P, 'weight_bar', -0.40, 0.40, 0.60, 0.82, 1.85, 2.00, 0, METAL_D, METAL_D, METAL_D)
    for i in range(4):
        x = -0.315 + 0.21 * i
        tbox(P, f'weight{i}', x - 0.095, x + 0.095, 0.55, 0.88, 1.98, FRONT_Z, 0.03, METAL, METAL, METAL_D)
    # fuel tank (left), exhaust: on the RIGHT of the bonnet beside the cab pillar, as in the reference (spec said left)
    tbox(P, 'tank', -0.62, -0.28, 0.62, 1.02, 0.32, 0.72, 0.04, RED_D, RED_D, RUBBER)
    sweep(P, 'exhaust', V(0.27, 1.80, 0.42), V(0.27, 2.42, 0.42), ngon(0.07, 8, math.pi / 8),
          [(0, 1, 0), (0.50, 1, 0), (0.51, 0.72, 0), (1, 0.72, 0)], METAL, METAL_D, METAL_D, ref=(1, 0, 0))
    sweep(P, 'exhaust_tip', V(0.27, 2.38, 0.42), V(0.27, 2.52, 0.49), ngon(0.05, 8, math.pi / 8),
          [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(1, 0, 0))
    # cab: cream base stripe, opaque glass core, red pillars and rails, flat chamfered roof, beacon, mirrors
    tbox(P, 'cab_base', -0.545, 0.545, 1.28, 1.40, CAB_Z0 - 0.04, CAB_Z1 + 0.04, 0, CREAM, CREAM, CREAM_D)
    tbox(P, 'glass', -0.47, 0.47, 1.36, 2.62, CAB_Z0 + 0.04, CAB_Z1 - 0.04, 0, GLASS, GLASS, GLASS)
    for s in (-1, 1):
        xa, xb = min(s * 0.45, s * CAB_X), max(s * 0.45, s * CAB_X)
        tbox(P, f'pillar_f{s}', xa, xb, 1.39, 2.60, CAB_Z1 - 0.10, CAB_Z1, 0, RED, RED, RED)
        tbox(P, f'pillar_r{s}', xa, xb, 1.39, 2.60, CAB_Z0, CAB_Z0 + 0.10, 0, RED, RED, RED)
        ra, rb = min(s * 0.475, s * 0.525), max(s * 0.475, s * 0.525)
        tbox(P, f'rail_side{s}', ra, rb, 1.395, 1.46, CAB_Z0 + 0.08, DOOR_Z0 + 0.01, 0, RED, RED, RED)
    tbox(P, 'rail_front', -0.46, 0.46, 1.395, 1.46, CAB_Z1 - 0.05, CAB_Z1 - 0.01, 0, RED, RED, RED)
    tbox(P, 'rail_rear', -0.46, 0.46, 1.395, 1.46, CAB_Z0 + 0.01, CAB_Z0 + 0.06, 0, RED, RED, RED)
    tbox(P, 'rail_top', -0.53, 0.53, 2.56, 2.68, CAB_Z0 + 0.02, CAB_Z1 - 0.02, 0, RED, RED_D, RED_D)
    tbox(P, 'roof', -0.61, 0.61, 2.66, 2.92, CAB_Z0 - 0.07, CAB_Z1 + 0.07, 0.07, RED, RED_D, RED_D, RED)
    rod(P, 'beacon', (-0.45, 2.90, -1.08), (-0.45, 3.00, -1.08), 0.065, SIGNAL, SIGNAL)
    door_frame(P, 1, 'door_R')                       # right door: static look-alike of Door_L (reference shows it)
    for s in (-1, 1):
        rod(P, f'mirror_arm{s}', (s * 0.52, 2.45, CAB_Z1 - 0.05), (s * 0.81, 2.52, CAB_Z1 + 0.03), 0.022, RUBBER, RUBBER)
        tbox(P, f'mirror{s}', min(s * 0.78, s * 0.84), max(s * 0.78, s * 0.84), 2.18, 2.54, CAB_Z1 - 0.04, CAB_Z1 + 0.10,
             0, RUBBER, RUBBER, RUBBER)
    # mudguards: front arches on brackets, wide rear arches joined to the cab, dark front mud flaps; steps both sides
    for s in (-1, 1):
        arch(P, f'fender_f{s}', WF['z'], WF['y'], 0.645, 0.06, s * 0.70, s * 1.20, (40, 75, 110, 145))
        tbox(P, f'fender_f_bracket{s}', min(s * 0.40, s * 0.73), max(s * 0.40, s * 0.73), 1.16, 1.20, WF['z'] - 0.05,
             WF['z'] + 0.05, 0, RED_D, RED_D, RED_D)
        arch(P, f'fender_r{s}', WR['z'], WR['y'], 1.02, 0.07, s * 0.54, s * 1.20, (25, 65, 115, 155))
        tbox(P, f'fender_r_join{s}', min(s * 0.50, s * 0.55), max(s * 0.50, s * 0.55), 1.30, 1.78, CAB_Z0 + 0.05,
             DOOR_Z0 - 0.01, 0, RED_D, RED_D, RED_D)
        tbox(P, f'mudflap{s}', min(s * 0.60, s * 1.18), max(s * 0.60, s * 1.18), 0.97, 1.28, -0.10, -0.04, 0,
             RUBBER, RUBBER, RUBBER)
        for i, y in enumerate((0.60, 0.95)):
            tbox(P, f'step{s}_{i}', min(s * 0.48, s * 0.80), max(s * 0.48, s * 0.80), y, y + 0.05, -0.08, 0.20, 0,
                 RUBBER, RUBBER, RUBBER)
    # rear: top-link bracket, PTO stub, drawbar with fork plates and vertical pin
    tbox(P, 'toplink_bracket', -0.10, 0.10, 1.05, 1.25, -1.84, -1.70, 0, METAL, METAL, METAL_D)
    rod(P, 'pto', (0, PTO[0], -1.76), (0, PTO[0], PTO[1]), 0.05, METAL_D, METAL_D)
    # fork mouth deep enough for the shared drawbar eye Ø0.24 (CATALOG item 6, orchestrator 2026-11-24): the front plate
    # starts 0.125 ahead of the pin (Z -2.025) and runs under the PTO stub (top Y 0.645 < stub bottom 0.65) to Z -1.975
    tbox(P, 'drawbar', -0.08, 0.08, 0.42, 0.52, -1.99, -1.70, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_front', -0.09, 0.09, 0.405, 0.645, HITCH[1] + 0.125, HITCH[1] + 0.175, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_bottom', -0.09, 0.09, 0.40, 0.46, -FRONT_Z, HITCH[1] + 0.13, 0, METAL, METAL, METAL_D)
    # top jaw held by the pin; stops 0.12 ahead of it so a mounted implement's PTO stub at PTO_Rear stays clear
    tbox(P, 'fork_top', -0.09, 0.09, 0.64, 0.70, -FRONT_Z, HITCH[1] + 0.12, 0, METAL, METAL, METAL_D)
    rod(P, 'fork_pin', (0, 0.38, HITCH[1]), (0, 0.72, HITCH[1]), 0.03, METAL_D, METAL_D)
    return P


def linkage_part():
    P = Part('Linkage_Rear')
    py, pz = LINK_PIV; lx, ly, lz = LINK_PIN
    rod(P, 'cross_shaft', (-0.50, py, pz), (0.50, py, pz), 0.05, METAL_D, METAL_D)
    for s in (-1, 1):
        rod(P, f'boss{s}', (s * 0.38, py, pz), (s * 0.52, py, pz), 0.065, METAL, METAL_D)
        sweep(P, f'arm{s}', V(s * 0.46, py, pz), V(s * 0.54, ly, lz + 0.03), chamf_rect(0.08, 0.10, 0.015),
              [(0, 1, 0), (1, 1, 0)], METAL_D, METAL_D, METAL_D, ref=(1, 0, 0))
        tbox(P, f'eye{s}', min(s * 0.505, s * 0.565), max(s * 0.505, s * 0.565), ly - 0.08, ly + 0.08, lz - 0.07, lz + 0.07,
             0.02, METAL, METAL, METAL_D)
        rod(P, f'pin{s}', (s * 0.40, ly, lz), (s * 0.555, ly, lz), 0.026, METAL_D, METAL_D)
        rod(P, f'lift_strut{s}', (s * 0.37, 1.22, -1.60), (s * 0.50, 0.62, -1.72), 0.028, METAL, METAL)
    rod(P, 'top_link', (0, 1.15, -1.76), (0, 1.27, -2.165), 0.035, METAL, METAL_D)
    return P


def door_part():
    P = Part('Door_L')
    door_frame(P, -1, 'door_L')
    return P


def wheel_parts():
    out = []
    for nm, W, s in (('Wheel_FL', WF, -1), ('Wheel_FR', WF, 1), ('Wheel_RL', WR, -1), ('Wheel_RR', WR, 1)):
        P = Part(nm); c = (s * W['x'], W['y'], W['z'])
        wheel(P, c, W['d'], W['w'], W['lugs'], outer=s, lug_h=W['lug_h'])
        out.append((P, c))
    return out


# ---------------- scene / build ----------------
def build_scene():
    if bpy.app.background:
        sc = bpy.context.scene
        for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    else:
        sc = bpy.data.scenes.get(SCENE) or bpy.data.scenes.new(SCENE)
    return sc


def own_collections(sc, name):
    outer = bpy.data.collections.get(OUTER) or bpy.data.collections.new(OUTER)
    if outer.name not in [c.name for c in sc.collection.children]: sc.collection.children.link(outer)
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll.name not in [c.name for c in outer.children]: outer.children.link(coll)
    for o in list(coll.all_objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    return coll


def bvh_world(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm); bm.free(); return t


def empty(coll, nm, parent, unity_pos, size=0.25):
    e = bpy.data.objects.new(nm, None); coll.objects.link(e)
    e.empty_display_type = 'ARROWS'; e.empty_display_size = size
    e.parent = parent
    e.location = to_blender(unity_pos) - (parent.location if parent.parent is not None else Vector((0, 0, 0)))
    return e


def unity_of(ob):
    t = ob.matrix_world.translation; return [round(-t.x, 4), round(t.z, 4), round(-t.y, 4)]


def build():
    name = PREFIX + 'Tractor_Cab'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    py, pz = LINK_PIV
    parts = [(body_part(), (0, 0, 0)), (linkage_part(), (0, py, pz)), (door_part(), (-0.53, 1.41, DOOR_Z1))]
    parts += wheel_parts()
    pts = [v.co for P, _ in parts for v in P.bm.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'DESIGN bbox x {lo[0]:.4f}..{hi[0]:.4f} (centre {(lo[0] + hi[0]) / 2:+.4f}) y {lo[1]:.4f}..{hi[1]:.4f} '
          f'z {lo[2]:.4f}..{hi[2]:.4f} (centre {(lo[2] + hi[2]) / 2:+.4f})')
    for P, _ in parts:
        for v in P.bm.verts: v.co = to_blender(v.co)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 0.4
    obs = {}
    for P, piv in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, to_blender(piv), root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    sc.view_layers[0].update()
    link = obs['Linkage_Rear']
    e_l3p = empty(coll, 'Link3P_Rear', link, V(0, LINK_PIN[1], LINK_PIN[2]))
    e_pto = empty(coll, 'PTO_Rear', root, V(0, PTO[0], PTO[1]))
    e_hit = empty(coll, 'Hitch_Rear', root, V(0, HITCH[0], HITCH[1]))
    e_seat = empty(coll, 'Seat', root, V(*SEAT))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 7000 -> {"OK" if tot <= 7000 else "OVER"} ({tot} tris, {100 * tot / 7000:.0f} %)')
    for e in (e_l3p, e_pto, e_hit, e_seat):
        print(f'  {e.name} (Unity) {unity_of(e)} parent {e.parent.name} rot {tuple(e.matrix_world.to_euler())}')
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} rot {tuple(o.rotation_euler)}')
    # clearance: wheels vs body (tyre may only touch the axle ends), mudguard radial clearance
    bb = bvh_world(obs['Body']); lb = bvh_world(obs['Linkage_Rear']); db = bvh_world(obs['Door_L'])
    for nm in ('Wheel_FL', 'Wheel_FR', 'Wheel_RL', 'Wheel_RR'):
        wo = obs[nm]; wb = bvh_world(wo)
        pairs = bb.overlap(wb); me = obs['Body'].data
        xs = [abs(-(obs['Body'].matrix_world @ me.vertices[vi].co).x) for fi, _ in pairs for vi in me.polygons[fi].vertices]
        wc = wo.matrix_world.translation
        dmin = min((bb.find_nearest(wo.matrix_world @ v.co)[3] for v in wo.data.vertices
                    if (wo.matrix_world @ v.co - wc).length > (WF['d'] if nm[-2] == 'F' else WR['d']) * 0.36), default=None)
        print(f'  {nm}: body overlap pairs {len(pairs)} (|x| of body faces {round(min(xs), 3) if xs else "-"}..{round(max(xs), 3) if xs else "-"}, '
              f'axle only expected) | linkage overlap {len(lb.overlap(wb))} door overlap {len(db.overlap(wb))} | '
              f'min tyre->body distance {dmin:.3f}')
    print(f'  linkage<->body overlap pairs {len(bb.overlap(lb))} (bosses/struts/top link into housing expected) | '
          f'door<->body overlap pairs {len(bb.overlap(db))}')
    return name, sc, coll, root, img, mat, obs


def fingerprint(obs):
    out = {}
    for k, o in obs.items():
        vs = sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in o.data.vertices)
        out[k] = (len(o.data.vertices), len(o.data.polygons), round(sum(a + 2 * b + 3 * c for a, b, c in vs), 4))
    print('FINGERPRINT', out)
    return out


# ---------------- IMP-01 docking check (temporary copy, removed afterwards) ----------------
def dock_check(sc, coll, obs, out_png=None):
    if not os.path.isfile(IMP01_BLEND):
        print('DOCK: IMP-01 blend missing', IMP01_BLEND); return
    before = set(bpy.data.collections); before_m, before_i = set(bpy.data.materials), set(bpy.data.images)
    with bpy.data.libraries.load(IMP01_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == 'FMS_Mach_Plough']
    pc_coll = dst.collections[0]; sc.collection.children.link(pc_coll)
    proot = next(o for o in pc_coll.objects if o.type == 'EMPTY' and o.parent is None)
    pfront = next(o for o in pc_coll.objects if o.name.startswith('Link3P_Front'))
    sc.view_layers[0].update()
    loc = proot.matrix_world.inverted() @ pfront.matrix_world
    rear = next(o for o in coll.objects if o.name == 'Link3P_Rear')
    proot.matrix_world = rear.matrix_world @ loc.inverted()
    sc.view_layers[0].update()
    d = (pfront.matrix_world.translation - rear.matrix_world.translation).length
    print(f'DOCK Link3P_Front->Link3P_Rear position error {d:.6f} m, rot front {tuple(round(math.degrees(a), 3) for a in pfront.matrix_world.to_euler())} '
          f'rear {tuple(round(math.degrees(a), 3) for a in rear.matrix_world.to_euler())}')
    pmeshes = [o for o in pc_coll.objects if o.type == 'MESH']
    tmeshes = list(obs.values())
    total = 0
    for po in pmeshes:
        pb = bvh_world(po)
        for to in tmeshes:
            n = len(pb.overlap(bvh_world(to))); total += n
            if n: print(f'  DOCK overlap {po.name} x {to.name}: {n} face pairs')
        dm = min(bvh_world(obs['Linkage_Rear']).find_nearest(po.matrix_world @ v.co)[3] for v in po.data.vertices)
        db_ = min(bvh_world(obs['Body']).find_nearest(po.matrix_world @ v.co)[3] for v in po.data.vertices)
        print(f'  DOCK {po.name}: min distance to Linkage_Rear {dm:.4f} m, to Body {db_:.4f} m')
    print(f'DOCK total overlapping face pairs {total}; plough min y {min((o.matrix_world @ v.co).z for o in pmeshes for v in o.data.vertices):.4f}')
    if out_png:
        render(sc, coll, out_png, (-0.95, 0.55, 0.45), 0.85, (960, 600), extra=pc_coll)
        render(sc, coll, out_png.replace('.png', '_close.png'), (-0.9, 0.35, 0.30), 0.85, (960, 600), extra=pc_coll, focus=rear)
    # remove the temporary copy
    for o in list(pc_coll.all_objects):
        dd = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dd, bpy.types.Mesh) and dd.users == 0: bpy.data.meshes.remove(dd)
    for c in set(bpy.data.collections) - before: bpy.data.collections.remove(c)
    for m in set(bpy.data.materials) - before_m:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - before_i:
        if i.users == 0: bpy.data.images.remove(i)
    print('DOCK temp copy removed; collections', [c.name for c in bpy.data.collections])


# ---------------- renders (from the skill's render_preview_template.py, as a function) ----------------
REF_VIEW = (0.70, -0.70, 0.47)     # Blender dir target->camera: front-LEFT three-quarter, ~25 deg up (reference)

def render(sc, coll, out, view_dir=REF_VIEW, fill_w=0.70, res=(1280, 800), lens=70, bg=(0xc7, 0xcc, 0xd3), extra=None, focus=None):
    from bpy_extras.object_utils import world_to_camera_view
    r = sc.render
    saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath,
                 vt=sc.view_settings.view_transform, cam=sc.camera, world=sc.world, ft=r.film_transparent)
    try:
        r.engine = 'BLENDER_EEVEE'
    except TypeError:
        r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], 100
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_World'); w.use_nodes = True; nt = w.node_tree
    wout = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bgn.inputs['Color'].default_value = (lin(bg[0]), lin(bg[1]), lin(bg[2]), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.82, 0.86, 0.95, 1); amb.inputs['Strength'].default_value = 0.45
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bgn.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], wout.inputs['Surface'])
    sc.world = w
    def sun(nm, rot, e, shadow=True, ang=10):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(ang); ld.use_shadow = shadow
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob); return ob
    s1 = sun('TMP_Sun', (45, 0, -30), 3.4); s2 = sun('TMP_Fill', (70, 0, 160), 0.9, shadow=False)
    cd = bpy.data.cameras.new('TMP_Cam'); cd.lens = lens
    cam = bpy.data.objects.new('TMP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.name.endswith(('_Low1', '_LOD1'))]
    if extra is not None: objs += [o for o in extra.all_objects if o.type == 'MESH']
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    if focus is not None:
        fc = focus.matrix_world.translation; pts = [p for p in pts if (p - fc).length < 1.3]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    target = Vector([(lo[i] + hi[i]) / 2 for i in range(3)]); dirv = Vector(view_dir).normalized()
    def place(dist):
        cam.location = target + dirv * dist
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.view_layers[0].update()
        xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    cd.shift_x = cd.shift_y = 0.0; dist = 10.0
    for _ in range(25):
        x0, x1, y0, y1 = place(dist); dist *= max((x1 - x0) / fill_w, (y1 - y0) / 0.90)
    x0, x1, y0, y1 = place(dist)
    cd.shift_x = (x0 + x1) / 2 - 0.5; cd.shift_y = ((y0 + y1) / 2 - 0.5) * (res[1] / res[0])
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in (s1, s2):
        dat = ob.data; bpy.data.objects.remove(ob, do_unlink=True); bpy.data.lights.remove(dat)
    dat = cam.data; bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(dat)
    sc.world = saved['world']; bpy.data.worlds.remove(w)
    r.engine = saved['engine']; r.resolution_x, r.resolution_y, r.resolution_percentage = saved['rx'], saved['ry'], saved['pct']
    r.filepath = saved['fp']; sc.view_settings.view_transform = saved['vt']; sc.camera = saved['cam']; r.film_transparent = saved['ft']
    print('render', out)


def with_scene(sc, fn, *a):
    win = bpy.context.window; prev = win.scene if win else None
    if win and prev != sc: win.scene = sc
    try:
        return fn(*a)
    finally:
        if win and prev is not None and win.scene != prev: win.scene = prev


def verify_headless(fbx, sc):
    before_o, before_i, before_m = set(sc.objects), set(bpy.data.images), set(bpy.data.materials)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in sc.objects if o not in before_o]
    print('VERIFY objects', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation])
        else:
            print('  ', o.name, o.type, 'loc', [round(x, 3) for x in o.matrix_world.translation])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)


name, sc, coll, root, img, mat, obs = build()
fingerprint(obs)
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'build':
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-01_check_ref.png'), REF_VIEW, 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-01_check_right.png'), (-0.75, -0.55, 0.40), 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-01_check_rear.png'), (0.55, 0.85, 0.40), 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-01_check_side.png'), (-1.0, 0.0, 0.05), 0.85, (960, 600))
    dock_check(sc, coll, obs, os.path.join(CHECK_DIR, 'TRC-01_dock_IMP-01.png'))
elif MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = os.path.join(ART, 'Meshes', name + '.fbx')
    with_scene(sc, pc.export, name, coll, root, fbx)
    pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
    render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.70, (1280, 800))
    if bpy.context.window:
        with_scene(sc, pc.verify, fbx)
    else:
        verify_headless(fbx, sc)
