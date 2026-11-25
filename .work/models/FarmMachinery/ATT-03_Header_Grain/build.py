# ATT-03 Header_Grain (FMS_Mach_Header_Grain) - FarmMachinery pack, stage E7. Procedural, idempotent.
# Nested prefab of HRV-01: header root = combine Feeder_Front + (0, -0.80, +1.05); Feeder_Rear <-> Feeder_Front.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- ATT-03 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/ATT-03/ + assembly check on HRV-01
#            (temporary copy from art/.../Blend/FMS_Mach_Combine.blend, removed afterwards; assembly render saved to
#            %TEMP%/farmmachinery_check/HRV-01/HRV-01_assembly_ATT-03.png)
#   export = build + FBX + collection-only .blend + ONE preview + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children, CATALOG item 3)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['ATT-03', 'build']})
# Geometry is written in UNITY coordinates (x right, y up, z forward) and mapped to Blender as (-x, -z, y).
# Shared helpers (wheel, tbox, rod, scene, render, verify) are verbatim copies from TRC-01 build.py.
import bpy, bmesh, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
HRV01_BLEND = os.path.join(REPO, 'art', 'FarmMachinery', 'Blend', 'FMS_Mach_Combine.blend')   # assembly check only
PREFIX, ATLAS = 'FMS_Mach_', 'FarmMachinery_Red'
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'ATT-03')
ASM_DIR = os.environ.get('PACK_CHECK_ASM') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'HRV-01')
SCENE = OUTER = 'ATT-03_Header_Grain'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'ATT-03'
MODE = _a[1] if len(_a) > 1 else 'build'

PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)

# ---------------- design numbers (Unity coordinates, metres; root on the ground at the footprint centre) ----------------
FEEDER_REAR = (0.80, -1.05)                      # (y, z); interface rectangle 1.60 x 0.90 centred here, plane Z -1.05
FRAME_GAP = 0.001                                # rear frame face 1 mm in front of the interface plane (no coplanar faces)
AUGER_PIV = (0.70, -0.45)                        # Auger_Cross axis X at (y, z)
ARM_PIV = (1.25, -0.70)                          # Reel_Arm hinge axis X at (y, z)
REEL_PIV = (0.95, 0.45)                          # Reel axle (y, z)
REEL_R, REEL_HALF = 0.52, 2.85                   # bar circle radius, end disc X
END_X0, END_X1 = 2.98, 3.08                      # end walls (each side)


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




def plate_z(P, n, z0, z1, outline, holes, s_face, s_side, s_hole):
    """plate between z0 and z1 from an (x, y) outline with optional (x, y) hole loops"""
    bm = P.bm
    o0 = [bm.verts.new((x, y, z0)) for x, y in outline]; o1 = [bm.verts.new((x, y, z1)) for x, y in outline]
    h0 = [[bm.verts.new((x, y, z0)) for x, y in h] for h in holes]; h1 = [[bm.verts.new((x, y, z1)) for x, y in h] for h in holes]
    faces = fill(P, [o0] + h0, s_face, (0, 0, 1)) + fill(P, [o1] + h1, s_face, (0, 0, 1)) + tube(P, o0, o1, s_side)
    for a, b in zip(h0, h1): faces += tube(P, a, b, s_hole)
    P.comp.append((n, faces, False))


def prism_x(P, n, x0, x1, zy, side, cap0, cap1):
    """prism along X of a closed (z, y) polygon; side(k) per polygon edge"""
    P.loft(n, [[V(x0, y, z) for z, y in zy], [V(x1, y, z) for z, y in zy]], lambda j, k: side(k), cap0, cap1)


def cr(cx, cy, w, h, c):
    return [(cx + x, cy + y) for x, y in chamf_rect(w, h, c)]


# ---------------- parts ----------------
def frame_part():
    P = Part('Frame')
    fy, fz = FEEDER_REAR
    # rear wall with the throat and a raised centre around it; interface frame 1.60 x 0.90 on its back face
    wall = [(-3.05, 0.10), (3.05, 0.10), (3.05, 1.15), (1.25, 1.15), (1.00, 1.42), (-1.00, 1.42), (-1.25, 1.15), (-3.05, 1.15)]
    plate_z(P, 'rear_wall', -1.02, -0.88, wall, [cr(0, fy, 1.42, 0.72, 0.02)], RED_D, RED_D, TYRE)
    plate_z(P, 'throat_back', -0.96, -0.93, cr(0, fy, 1.44, 0.74, 0.02), [], TYRE, TYRE, TYRE)   # reads black as in the reference
    plate_z(P, 'throat_frame', fz + FRAME_GAP, -1.00, cr(0, fy, 1.60, 0.90, 0.06), [cr(0, fy, 1.40, 0.70, 0.02)],
            RED_D, RED, METAL_D)
    # sloped platform floor from the cutter bar up to the auger trough and the rear wall (ends inside the end walls)
    floor = [(0.86, 0.12), (0.86, 0.17), (0.05, 0.25), (-0.20, 0.22), (-0.70, 0.24), (-0.89, 0.55), (-0.89, 0.12)]
    prism_x(P, 'floor', -3.00, 3.00, floor, lambda k: (RED_D, RED, RED, RED, RED, RED_D, RED_D)[k], RED_D, RED_D)
    for s in (-1, 1):
        xa, xb = sorted((s * END_X0, s * END_X1))
        end = [(-1.01, 0.10), (0.60, 0.10), (0.60, 0.55), (-0.20, 1.06), (-1.01, 1.06)]
        prism_x(P, f'end_wall{s}', xa, xb, end, lambda k: (RED_D, RED_D, RED, RED, RED_D)[k], RED, RED)
        da, db = sorted((s * (END_X0 + 0.005), s * (END_X1 - 0.005)))
        prism_x(P, f'divider{s}', da, db, [(0.59, 0.10), (1.05, 0.10), (0.59, 0.55)],
                lambda k: (RED_D, SIGNAL, RED_D)[k], SIGNAL, SIGNAL)
        sa, sb = sorted((s * (END_X1 - 0.005), s * 3.10))
        prism_x(P, f'stripe{s}', sa, sb, [(0.52, 0.40), (0.52, 0.52), (-0.18, 0.97), (-0.18, 0.85)],
                lambda k: SIGNAL, SIGNAL, SIGNAL)
        pa, pb = sorted((s * 2.96, s * 3.06))
        tbox(P, f'arm_post{s}', pa, pb, 1.00, 1.20, ARM_PIV[1] - 0.08, ARM_PIV[1] + 0.08, 0, RED_D, RED_D, RED_D)
    # cutter bar with blocky finger points
    tbox(P, 'cutter_bar', -2.995, 2.995, 0.10, 0.24, 0.80, 0.92, 0, METAL_D, METAL_D, METAL_D)
    n = 36
    for i in range(n):
        x = -2.88 + 5.76 * i / (n - 1)
        tri = lambda y: [V(x - 0.05, y, 0.91), V(x + 0.05, y, 0.91), V(x, y, 1.04)]
        P.loft(f'finger{i}', [tri(0.13), tri(0.19)], METAL, METAL, METAL)
    return P


def auger_part():
    P = Part('Auger_Cross')
    ay, az = AUGER_PIV
    rod(P, 'tube', (-3.02, ay, az), (3.02, ay, az), 0.25, METAL, METAL_D)
    rod(P, 'centre', (-0.30, ay, az), (0.30, ay, az), 0.32, METAL_D, METAL_D)
    for x in (-2.45, -1.95, -1.45, -0.95, 0.95, 1.45, 1.95, 2.45):
        rod(P, f'flight{x:+.2f}', (x - 0.04, ay, az), (x + 0.04, ay, az), 0.35, METAL_D, METAL_D)
    return P


def arm_part():
    P = Part('Reel_Arm')
    hy, hz = ARM_PIV; ry, rz = REEL_PIV
    for s in (-1, 1):
        sweep(P, f'arm{s}', V(s * 3.0, hy, hz - 0.04), V(s * 3.0, ry - 0.02, rz + 0.06), chamf_rect(0.10, 0.14, 0.02),
              [(0, 1, 0), (1, 1, 0)], RED, RED_D, RED_D, ref=(1, 0, 0))
    rod(P, 'brace', (-3.0, hy, hz), (3.0, hy, hz), 0.05, RED_D, RED_D)
    return P


def reel_part():
    P = Part('Reel')
    ry, rz = REEL_PIV; R = REEL_R
    rod(P, 'axle', (-3.02, ry, rz), (3.02, ry, rz), 0.04, METAL_D, METAL_D)
    for s in (-1, 1):
        x = s * REEL_HALF
        pts = [V(x, ry + R * math.sin(2 * math.pi * k / 8), rz + R * math.cos(2 * math.pi * k / 8)) for k in range(8)]
        path_sweep(P, f'disc_rim{s}', pts, (1, 0, 0), [(0.03, 0.03), (-0.03, 0.03), (-0.03, -0.03), (0.03, -0.03)],
                   METAL_D, METAL_D, closed=True)
        for k in range(4):
            a = math.pi * k / 4
            d = V(0, math.sin(a), math.cos(a))
            hw = 0.026 - 0.002 * k                   # different widths: crossing spokes never share a face plane
            sweep(P, f'spoke{s}_{k}', V(x, ry, rz) - d * R, V(x, ry, rz) + d * R, [(hw, hw), (-hw, hw), (-hw, -hw), (hw, -hw)],
                  [(0, 1, 0), (1, 1, 0)], METAL_D, METAL_D, METAL_D, ref=(1, 0, 0))
        rod(P, f'hub{s}', (x - 0.07, ry, rz), (x + 0.07, ry, rz), 0.08, METAL_D, METAL_D)
    for k in range(8):
        a = 2 * math.pi * k / 8
        y, z = ry + R * math.sin(a), rz + R * math.cos(a)
        rod(P, f'bar{k}', (-REEL_HALF - 0.015, y, z), (REEL_HALF + 0.015, y, z), 0.035, METAL, METAL, seg=6)
    return P


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
    name = PREFIX + 'Header_Grain'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    parts = [(frame_part(), (0, 0, 0)), (auger_part(), (0,) + AUGER_PIV), (arm_part(), (0,) + ARM_PIV)]
    reel = reel_part()
    pts = [v.co for P, _ in parts for v in P.bm.verts] + [v.co for v in reel.bm.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'DESIGN bbox x {lo[0]:.4f}..{hi[0]:.4f} (centre {(lo[0] + hi[0]) / 2:+.4f}) y {lo[1]:.4f}..{hi[1]:.4f} '
          f'z {lo[2]:.4f}..{hi[2]:.4f} (centre {(lo[2] + hi[2]) / 2:+.4f})')
    for P in [p for p, _ in parts] + [reel]:
        for v in P.bm.verts: v.co = to_blender(v.co)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 0.5
    obs = {}
    for P, piv in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, to_blender(piv), root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    # Reel: child of Reel_Arm, own origin on its axle
    arm = obs['Reel_Arm']; rp = to_blender((0,) + REEL_PIV)
    ob = pc.to_object(reel, '', coll, mat, rp, arm)
    ob.location = rp - arm.location; ob.name = 'Reel'; ob.data.name = 'Reel'; obs['Reel'] = ob
    sc.view_layers[0].update()
    e_fr = empty(coll, 'Feeder_Rear', root, V(0, FEEDER_REAR[0], FEEDER_REAR[1]))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 5000 -> {"OK" if tot <= 5000 else "OVER"} ({tot} tris, {100 * tot / 5000:.0f} %)')
    print(f'  {e_fr.name} (Unity) {unity_of(e_fr)} parent {e_fr.parent.name} rot {tuple(e_fr.matrix_world.to_euler())}')
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} parent {o.parent.name} rot {tuple(o.rotation_euler)}')
    B = {k: bvh_world(o) for k, o in obs.items()}
    for a, b in (('Reel', 'Reel_Arm'), ('Reel', 'Frame'), ('Reel', 'Auger_Cross'), ('Auger_Cross', 'Frame'), ('Reel_Arm', 'Frame')):
        print(f'  overlap {a} x {b}: {len(B[a].overlap(B[b]))} face pairs')
    # reel <-> auger clearance during rotation: distance between the axes minus the swept radii
    print(f'  reel/auger swept clearance {math.hypot(REEL_PIV[0] - AUGER_PIV[0], REEL_PIV[1] - AUGER_PIV[1]) - (REEL_R + 0.035) - 0.35:.3f} m')
    return name, sc, coll, root, img, mat, obs


def assembly_check(sc, coll, obs, out_png=None):
    """temporary copy of HRV-01 from its exported .blend; header root placed so Feeder_Rear == Feeder_Front"""
    if not os.path.isfile(HRV01_BLEND):
        print('ASM: HRV-01 blend missing', HRV01_BLEND); return
    before = set(bpy.data.collections); before_m, before_i = set(bpy.data.materials), set(bpy.data.images)
    before_o = set(bpy.data.objects)
    with bpy.data.libraries.load(HRV01_BLEND, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == 'FMS_Mach_Combine']
    cc = dst.collections[0]; sc.collection.children.link(cc)
    croot = next(o for o in cc.objects if o.type == 'EMPTY' and o.parent is None)
    ffront = next(o for o in cc.objects if o.name.startswith('Feeder_Front'))
    root = next(o for o in coll.objects if o.type == 'EMPTY' and o.parent is None)
    frear = next(o for o in coll.objects if o.name == 'Feeder_Rear')
    saved = root.matrix_world.copy()
    sc.view_layers[0].update()
    loc = root.matrix_world.inverted() @ frear.matrix_world
    root.matrix_world = ffront.matrix_world @ loc.inverted()
    sc.view_layers[0].update()
    d = (frear.matrix_world.translation - ffront.matrix_world.translation).length
    t = root.matrix_world.translation; f = ffront.matrix_world.translation
    rel = Vector((-(t.x - f.x), t.z - f.z, -(t.y - f.y)))
    print(f'ASM Feeder_Rear->Feeder_Front position error {d:.6f} m; header root - Feeder_Front (Unity) '
          f'{[round(c, 4) for c in rel]} (spec (0, -0.80, +1.05)); rot rear {tuple(round(math.degrees(a), 3) for a in frear.matrix_world.to_euler())} '
          f'front {tuple(round(math.degrees(a), 3) for a in ffront.matrix_world.to_euler())}')
    cm = [o for o in cc.objects if o.type == 'MESH']; total = 0
    for ho in obs.values():
        hb = bvh_world(ho)
        for co in cm:
            n = len(hb.overlap(bvh_world(co))); total += n
            if n: print(f'  ASM overlap {ho.name} x {co.name}: {n} face pairs')
    feeder = next(o for o in cm if o.name.startswith('Feeder'))
    fb = bvh_world(feeder)
    dmin = min(fb.find_nearest(obs['Frame'].matrix_world @ v.co)[3] for v in obs['Frame'].data.vertices)
    print(f'ASM total overlapping face pairs {total}; header Frame <-> combine Feeder min distance {dmin * 1000:.2f} mm; '
          f'header min height {min((o.matrix_world @ v.co).z for o in obs.values() for v in o.data.vertices):.3f} m')
    if out_png:
        render(sc, cc, out_png, (0.72, -0.70, 0.45), 0.80, (1280, 800), extra=coll)
    root.matrix_world = saved
    for o in list(cc.all_objects):
        dd = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dd, bpy.types.Mesh) and dd.users == 0: bpy.data.meshes.remove(dd)
    for c in set(bpy.data.collections) - before: bpy.data.collections.remove(c)
    for m in set(bpy.data.materials) - before_m:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - before_i:
        if i.users == 0: bpy.data.images.remove(i)
    sc.view_layers[0].update()
    print('ASM temp copy removed; leftover new objects', [o.name for o in set(bpy.data.objects) - before_o],
          '| header root back at', [round(c, 4) for c in root.matrix_world.translation])


REF_VIEW = (0.35, -0.90, 0.55)     # Blender dir target->camera: front-left three-quarter, ~30 deg up (reference)

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
os.makedirs(CHECK_DIR, exist_ok=True); os.makedirs(ASM_DIR, exist_ok=True)
if MODE == 'build':
    render(sc, coll, os.path.join(CHECK_DIR, 'ATT-03_check_ref.png'), REF_VIEW, 0.85, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'ATT-03_check_rear.png'), (-0.45, 0.85, 0.55), 0.85, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'ATT-03_check_side.png'), (1.0, 0.0, 0.10), 0.60, (960, 600))
    assembly_check(sc, coll, obs, os.path.join(ASM_DIR, 'HRV-01_assembly_ATT-03.png'))
elif MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = os.path.join(ART, 'Meshes', name + '.fbx')
    with_scene(sc, pc.export, name, coll, root, fbx)
    pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
    render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.75, (1280, 800))
    if bpy.context.window:
        with_scene(sc, pc.verify, fbx)
    else:
        verify_headless(fbx, sc)
