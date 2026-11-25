# HRV-01 Combine (FMS_Mach_Combine) - FarmMachinery pack, stage E7. Procedural, idempotent. Header ATT-03 is NOT part
# of this model (own FBX, nested prefab on Feeder_Front).
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- HRV-01 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/HRV-01/
#   export = build + FBX + collection-only .blend + ONE preview + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children, CATALOG item 3)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['HRV-01', 'build']})
#   Live builds go to an own scene + collection 'HRV-01_Combine'; nothing else is touched.
# Geometry is written in UNITY coordinates (x right, y up, z forward) and mapped to Blender as (-x, -z, y).
# Shared helpers (wheel, tbox, rod, scene, render, verify) are verbatim copies from TRC-01 build.py.
import bpy, bmesh, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
PREFIX, ATLAS = 'FMS_Mach_', 'FarmMachinery_Red'          # shared pack atlas T_FarmMachinery_Red_BaseColor.png
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'HRV-01')
SCENE = OUTER = 'HRV-01_Combine'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'HRV-01'
MODE = _a[1] if len(_a) > 1 else 'build'

PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)

# ---------------- design numbers (Unity coordinates, metres; root = footprint centre on the ground) ----------------
WF = dict(d=1.80, w=0.90, y=0.90, x=1.35, z=1.20, lugs=16, lug_h=0.12)     # front drive wheels (outer tyre X 1.80)
WR = dict(d=1.10, w=0.50, y=0.55, x=1.00, z=-3.00, lugs=12, lug_h=0.088)   # rear steering wheels
FEEDER_PIV = (2.00, 1.60)                        # Feeder hinge axis X at (y, z)
FEEDER_FRONT = (0.80, 4.20)                      # Feeder_Front (y, z); interface 1.60 x 0.90, front face Z 4.20
AUGER_PIV = (-1.25, 3.45, -1.40)                 # Auger_Unload base pivot, axis Y
AUGER_Y, AUGER_TIP = 3.62, 2.20                  # folded tube centre height, tip Z
HITCH = (0.55, -4.13)                            # Hitch_Rear on the fork pin (fork plates end at Z -4.20 = bbox rear)
SEAT = (0.0, 2.45, 2.25)
CAB_X, CAB_Z0, CAB_Z1 = 0.87, 1.50, 3.05         # cab posts outer face, rear / front
DOOR_Z0, DOOR_Z1, DOOR_Y0, DOOR_Y1 = 2.05, 2.85, 2.20, 3.34


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




def ring_c(z, yc, w, h, c):
    """chamfered rectangle ring in the XY plane at z, centred (0, yc)"""
    return [V(x, yc + y, z) for x, y in chamf_rect(w, h, c)]


# ---------------- parts ----------------
def body_part():
    P = Part('Body')
    # threshing body: dark lower section between the drive wheels, wider red upper section over them
    tbox(P, 'lower_body', -0.85, 0.85, 0.70, 1.95, -1.60, 2.38, 0, RED, lambda k: RED_D if k == 2 else RUBBER, RUBBER)
    tbox(P, 'upper_body', -1.30, 1.30, 1.90, 2.42, -1.62, 2.40, 0.06, RED, RED_D, RUBBER, RED)
    for s in (-1, 1):
        rod(P, f'front_axle{s}', (s * 0.70, WF['y'], WF['z']), (s * 1.22, WF['y'], WF['z']), 0.12, RUBBER, METAL_D)
    # grain tank with a sloped (wide-chamfered) cover and two hatch lids; auger cradle near the front
    tbox(P, 'tank', -1.40, 1.40, 2.40, 3.40, -1.55, 1.40, 0.25, RED, RED_D, RED_D, RED)
    for i, (z0, z1) in enumerate(((-1.00, -0.25), (0.20, 0.95))):
        tbox(P, f'hatch{i}', -0.55, 0.55, 3.39, 3.44, z0, z1, 0, RED_D, RED_D, RED_D)
    tbox(P, 'auger_cradle', AUGER_PIV[0] - 0.08, AUGER_PIV[0] + 0.08, 3.25, 3.45, 1.00, 1.12, 0, METAL, METAL, METAL)
    # engine compartment at the rear: side grilles (slats), exhaust on the right, rear lights
    tbox(P, 'engine', -1.25, 1.25, 1.18, 2.90, -4.00, -1.50, 0.06, RED, RED_D, RUBBER, RED)
    for s in (-1, 1):
        tbox(P, f'grille{s}', min(s * 1.24, s * 1.28), max(s * 1.24, s * 1.28), 1.55, 2.60, -3.70, -2.40, 0, TYRE, TYRE, TYRE)
        for i in range(4):
            y = 1.68 + 0.26 * i
            tbox(P, f'slat{s}_{i}', min(s * 1.27, s * 1.31), max(s * 1.27, s * 1.31), y, y + 0.08, -3.62, -2.48, 0,
                 METAL_D, METAL_D, METAL_D)
        tbox(P, f'rear_light{s}', min(s * 0.85, s * 1.10), max(s * 0.85, s * 1.10), 2.40, 2.55, -4.03, -3.98, 0, RUBBER,
             lambda k: LAMP if k == 0 else RUBBER, RUBBER)
    rod(P, 'exhaust', (1.00, 2.85, -3.60), (1.00, 3.55, -3.60), 0.08, RUBBER, RUBBER)
    rod(P, 'exhaust_tip', (1.00, 3.50, -3.60), (1.00, 3.66, -3.48), 0.065, RUBBER, METAL_D)
    # rear steering axle: pivot post under the engine + beam into the wheel hubs
    tbox(P, 'rear_post', -0.12, 0.12, 0.55, 1.22, WR['z'] - 0.10, WR['z'] + 0.10, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'rear_axle', -0.93, 0.93, 0.48, 0.62, WR['z'] - 0.06, WR['z'] + 0.06, 0, RUBBER, RUBBER, RUBBER)
    # hitch: vertical plate under the engine rear, fork plates, vertical pin (Hitch_Rear on the pin)
    # front plate 0.125 ahead of the pin (CATALOG item 6, orchestrator fix 2026-11-24, same as TRC-01): the shared drawbar
    # eye (outer 0.24) fits with 0 overlaps; rear face Z -4.005 (5 mm behind the engine rear face, no coplanar faces)
    tbox(P, 'hitch_plate', -0.09, 0.09, 0.42, 1.22, HITCH[1] + 0.125, HITCH[1] + 0.225, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_bottom', -0.09, 0.09, 0.44, 0.49, -4.20, -3.95, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_top', -0.09, 0.09, 0.61, 0.66, -4.20, -3.95, 0, METAL, METAL, METAL_D)
    rod(P, 'fork_pin', (0, 0.41, HITCH[1]), (0, 0.69, HITCH[1]), 0.03, METAL_D, METAL_D)
    # cab at the front above the feeder: red nose with headlights, glass core, posts, rails, cream roof stripe, roof
    tbox(P, 'cab_base', -CAB_X, CAB_X, 1.98, 2.18, CAB_Z0 - 0.05, CAB_Z1 + 0.05, 0.04, RED, RED_D, RUBBER, RED)
    for s in (-1, 1):
        tbox(P, f'headlight{s}', min(s * 0.35, s * 0.62), max(s * 0.35, s * 0.62), 2.03, 2.13, CAB_Z1 + 0.03, CAB_Z1 + 0.08, 0,
             RUBBER, lambda k: LAMP if k == 2 else RUBBER, RUBBER)
    tbox(P, 'glass', -0.80, 0.80, 2.14, 3.42, CAB_Z0 + 0.04, CAB_Z1 - 0.04, 0, GLASS, GLASS, GLASS)
    for s in (-1, 1):
        xa, xb = min(s * 0.77, s * CAB_X), max(s * 0.77, s * CAB_X)
        tbox(P, f'post_f{s}', xa, xb, 2.17, 3.46, CAB_Z1 - 0.10, CAB_Z1, 0, RED, RED, RED)
        tbox(P, f'post_r{s}', xa, xb, 2.17, 3.46, CAB_Z0, CAB_Z0 + 0.10, 0, RED, RED, RED)
    tbox(P, 'rail_top', -0.85, 0.85, 3.36, 3.47, CAB_Z0 + 0.02, CAB_Z1 - 0.02, 0, RED, RED_D, RED_D)
    tbox(P, 'roof_stripe', -0.96, 0.96, 3.44, 3.50, CAB_Z0 - 0.09, CAB_Z1 + 0.09, 0, CREAM, CREAM, CREAM_D)
    tbox(P, 'roof', -0.95, 0.95, 3.49, 3.62, CAB_Z0 - 0.08, CAB_Z1 + 0.08, 0.06, RED, RED_D, RED_D, RED)
    rod(P, 'beacon_post', (-0.30, 3.60, 2.70), (-0.30, 3.82, 2.70), 0.04, METAL_D, METAL_D)
    rod(P, 'beacon', (-0.30, 3.80, 2.70), (-0.30, 4.00, 2.70), 0.09, SIGNAL, SIGNAL)
    for s in (-1, 1):
        rod(P, f'mirror_arm{s}', (s * 0.84, 3.25, CAB_Z1 - 0.05), (s * 1.12, 3.32, CAB_Z1 + 0.05), 0.022, RUBBER, RUBBER)
        tbox(P, f'mirror{s}', min(s * 1.08, s * 1.15), max(s * 1.08, s * 1.15), 2.95, 3.36, CAB_Z1 - 0.02, CAB_Z1 + 0.12, 0,
             RUBBER, RUBBER, RUBBER)
    return P


def door_part():
    """left cab door: 4-bar red frame, opaque glass, dark handle; hinge at the front vertical edge (axis Y)"""
    P = Part('Door_L')
    xo, xi, hxo, hxi = -0.86, -0.785, -0.855, -0.79
    tbox(P, 'front', xo, xi, DOOR_Y0, DOOR_Y1, DOOR_Z1 - 0.06, DOOR_Z1, 0, RED, RED, RED)
    tbox(P, 'rear', xo, xi, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z0 + 0.06, 0, RED, RED, RED)
    tbox(P, 'bottom', hxo, hxi, DOOR_Y0 + 0.005, DOOR_Y0 + 0.06, DOOR_Z0 + 0.03, DOOR_Z1 - 0.03, 0, RED, RED, RED)
    tbox(P, 'top', hxo, hxi, DOOR_Y1 - 0.06, DOOR_Y1 - 0.005, DOOR_Z0 + 0.03, DOOR_Z1 - 0.03, 0, RED, RED, RED)
    tbox(P, 'glass', -0.835, -0.815, DOOR_Y0 + 0.03, DOOR_Y1 - 0.03, DOOR_Z0 + 0.04, DOOR_Z1 - 0.04, 0, GLASS, GLASS, GLASS)
    tbox(P, 'handle', -0.88, -0.83, 2.70, 2.75, DOOR_Z0 + 0.10, DOOR_Z0 + 0.22, 0, RUBBER, RUBBER, RUBBER)
    return P


def feeder_part():
    """inclined feeder housing, 1.60 wide, from inside the body down to the interface frame (front face Z 4.20):
    outer 1.60 x 0.90 frame with 0.10 walls around a dark throat"""
    P = Part('Feeder')
    fy, fz = FEEDER_FRONT
    rings = [ring_c(1.70, 1.925, 1.60, 0.75, 0.06), ring_c(fz - 0.10, fy, 1.60, 0.90, 0.06), ring_c(fz, fy, 1.60, 0.90, 0.06),
             ring_c(fz, fy, 1.40, 0.70, 0.02), ring_c(fz - 0.25, fy, 1.40, 0.70, 0.02)]
    outer = {3: RED, 2: RED, 4: RED, 1: RED_D, 5: RED_D, 0: RED_D, 6: RED_D, 7: RUBBER}
    P.loft('feeder', rings, lambda j, k: outer[k] if j < 2 else (RED_D if j == 2 else METAL_D), RED_D, TYRE)
    return P


def auger_part():
    """unloading auger, folded along the left top edge of the tank pointing forward; riser at the base, spout at the tip"""
    P = Part('Auger_Unload')
    x, _, z0 = AUGER_PIV
    rod(P, 'riser', (x, 3.15, z0), (x, AUGER_Y + 0.08, z0), 0.18, METAL, METAL_D)
    rod(P, 'tube', (x, AUGER_Y, z0 - 0.10), (x, AUGER_Y, AUGER_TIP), 0.20, METAL, METAL_D)
    rod(P, 'stripe', (x, AUGER_Y, AUGER_TIP - 0.50), (x, AUGER_Y, AUGER_TIP - 0.35), 0.21, SIGNAL, SIGNAL)
    rod(P, 'spout', (x, AUGER_Y, AUGER_TIP), (x, 3.25, AUGER_TIP), 0.14, METAL, METAL_D)
    return P


def wheel_parts():
    out = []
    for nm, W, s in (('Wheel_FL', WF, -1), ('Wheel_FR', WF, 1), ('Wheel_RL', WR, -1), ('Wheel_RR', WR, 1)):
        P = Part(nm); c = (s * W['x'], W['y'], W['z'])
        wheel(P, c, W['d'], W['w'], W['lugs'], outer=s, lug_h=W['lug_h'])
        out.append((P, c))
    return out


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


def fingerprint(obs):
    out = {}
    for k, o in obs.items():
        vs = sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in o.data.vertices)
        out[k] = (len(o.data.vertices), len(o.data.polygons), round(sum(a + 2 * b + 3 * c for a, b, c in vs), 4))
    print('FINGERPRINT', out)
    return out




def build():
    name = PREFIX + 'Combine'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    parts = [(body_part(), (0, 0, 0)), (feeder_part(), (0, FEEDER_PIV[0], FEEDER_PIV[1])), (auger_part(), AUGER_PIV),
             (door_part(), (-0.86, (DOOR_Y0 + DOOR_Y1) / 2, DOOR_Z1))]
    parts += wheel_parts()
    pts = [v.co for P, _ in parts for v in P.bm.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'DESIGN bbox x {lo[0]:.4f}..{hi[0]:.4f} (centre {(lo[0] + hi[0]) / 2:+.4f}) y {lo[1]:.4f}..{hi[1]:.4f} '
          f'z {lo[2]:.4f}..{hi[2]:.4f} (centre {(lo[2] + hi[2]) / 2:+.4f})')
    for P, _ in parts:
        for v in P.bm.verts: v.co = to_blender(v.co)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 0.5
    obs = {}
    for P, piv in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, to_blender(piv), root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    sc.view_layers[0].update()
    e_ff = empty(coll, 'Feeder_Front', obs['Feeder'], V(0, FEEDER_FRONT[0], FEEDER_FRONT[1]))
    e_ao = empty(coll, 'Auger_Out', obs['Auger_Unload'], V(AUGER_PIV[0], 3.25, AUGER_TIP))
    e_hit = empty(coll, 'Hitch_Rear', root, V(0, HITCH[0], HITCH[1]))
    e_seat = empty(coll, 'Seat', root, V(*SEAT))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 12000 -> {"OK" if tot <= 12000 else "OVER"} ({tot} tris, {100 * tot / 12000:.0f} %)')
    for e in (e_ff, e_ao, e_hit, e_seat):
        print(f'  {e.name} (Unity) {unity_of(e)} parent {e.parent.name} rot {tuple(e.matrix_world.to_euler())}')
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} rot {tuple(o.rotation_euler)}')
    bb = bvh_world(obs['Body'])
    for nm in ('Wheel_FL', 'Wheel_FR', 'Wheel_RL', 'Wheel_RR'):
        wo = obs[nm]; wb = bvh_world(wo); wc = wo.matrix_world.translation
        others = [k for k in ('Feeder', 'Auger_Unload', 'Door_L') if bvh_world(obs[k]).overlap(wb)]
        dmin = min((bb.find_nearest(wo.matrix_world @ v.co)[3] for v in wo.data.vertices
                    if (wo.matrix_world @ v.co - wc).length > (WF['d'] if nm[-2] == 'F' else WR['d']) * 0.36), default=None)
        print(f'  {nm}: body overlap pairs {len(bb.overlap(wb))} (axle only expected) | other parts touching {others} | '
              f'min tyre->body distance {dmin:.3f}')
    for k in ('Feeder', 'Auger_Unload', 'Door_L'):
        print(f'  {k}<->Body overlap pairs {len(bb.overlap(bvh_world(obs[k])))}')
    return name, sc, coll, root, img, mat, obs


REF_VIEW = (0.72, -0.70, 0.45)     # Blender dir target->camera: front-LEFT three-quarter, ~25 deg up (reference)

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
    render(sc, coll, os.path.join(CHECK_DIR, 'HRV-01_check_ref.png'), REF_VIEW, 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'HRV-01_check_right.png'), (-0.75, -0.55, 0.40), 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'HRV-01_check_rear.png'), (0.55, 0.85, 0.40), 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'HRV-01_check_side.png'), (1.0, 0.0, 0.05), 0.85, (960, 600))
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
