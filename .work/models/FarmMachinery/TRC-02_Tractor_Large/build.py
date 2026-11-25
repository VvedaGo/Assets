# TRC-02 Tractor_Large (FMS_Mach_Tractor_Large) - FarmMachinery pack, stage E7 (series batch 1). Procedural, idempotent.
# Large tractor: four equal wheels, broad bonnet, mid cab, front and rear three-point linkage.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- TRC-02 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/TRC-02/ + mating check (temporary partner copy)
#   export = build + FBX + collection-only .blend + ONE preview (reference camera) + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children, CATALOG item 3)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['TRC-02', 'build']})
#   Live builds go to an own scene + collection 'TRC-02_Tractor_Large'; nothing else is touched.
# Geometry is written in UNITY coordinates (x right, y up, z forward) and mapped to Blender as (-x, -z, y).
# Shared helpers (wheel, tbox, rod, arch, scene, render, verify) are verbatim copies from TRC-01 build.py; plate_x from
# IMP-01, prism_x from ATT-03.
import bpy, bmesh, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
BLEND_DIR = os.path.join(REPO, 'art', 'FarmMachinery', 'Blend')          # partner models for mating checks
PREFIX, ATLAS = 'FMS_Mach_', 'FarmMachinery_Red'          # shared pack atlas T_FarmMachinery_Red_BaseColor.png
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'TRC-02')
SCENE = OUTER = 'TRC-02_Tractor_Large'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'TRC-02'
MODE = _a[1] if len(_a) > 1 else 'build'

PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))


# ---------------- design numbers (Unity coordinates, metres; root = footprint centre on the ground) ----------------
WF = dict(d=1.90, w=0.65, y=0.95, x=1.12, z=1.35, lugs=16, lug_h=0.10)     # front wheels (outer tyre X 1.445)
WR = dict(d=1.90, w=0.65, y=0.95, x=1.12, z=-1.70, lugs=16, lug_h=0.10)    # rear wheels, same size
CAB_X, CAB_Z0, CAB_Z1 = 0.65, -1.15, 0.35        # cab pillars outer face, rear / front
DOOR_Z0, DOOR_Z1, DOOR_Y0, DOOR_Y1 = -0.50, 0.24, 1.63, 2.92
LINK_R_PIV = (0.60, -2.20)                       # Linkage_Rear pivot axis X (y, z)
LINK_R_PIN = (0.45, 0.60, -2.75)                 # rear lower-link pins -> Link3P_Rear (CATALOG item 6: TRC-02 Z -2.75)
LINK_F_PIV = (0.60, 2.40)                        # Linkage_Front pivot axis X (y, z)
LINK_F_PIN = (0.45, 0.60, 2.87)                  # front lower-link pins -> Link3P_Front (spec ~2.75; eye front = bbox front)
PTO = (0.70, -2.75)                              # PTO_Rear (y, z)
HITCH = (0.55, -2.90)                            # Hitch_Rear on the fork pin (item 6)
FORK_END = -2.94                                 # rear fork plates end = -front eye face (root stays at the bbox centre)
SEAT = (0.0, 1.80, -0.40)
REF_VIEW = (0.82, -0.57, 0.47)                   # Blender dir target->camera: front-left 3/4 (~55 deg off the nose), ~25 deg up (reference)



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




def plate_x(P, cname, x0, x1, cy, cz, wy, wz, ch, hole_r, s_face, s_side, s_bore, hn=8):
    """plate / block with flat faces normal to X, chamfered (y, z) outline and a through pin hole along X (IMP-01)"""
    bm = P.bm
    out = [(cy + a, cz + b) for a, b in chamf_rect(wy, wz, ch)]
    hole = [(cy + hole_r * math.cos(math.pi / hn + 2 * math.pi * i / hn), cz + hole_r * math.sin(math.pi / hn + 2 * math.pi * i / hn)) for i in range(hn)]
    o0 = [bm.verts.new((x0, y, z)) for y, z in out]; o1 = [bm.verts.new((x1, y, z)) for y, z in out]
    h0 = [bm.verts.new((x0, y, z)) for y, z in hole]; h1 = [bm.verts.new((x1, y, z)) for y, z in hole]
    faces = fill(P, [o0, h0], s_face, (1, 0, 0)) + fill(P, [o1, h1], s_face, (1, 0, 0))
    faces += tube(P, o0, o1, s_side) + tube(P, h0, h1, s_bore)
    P.comp.append((cname, faces, False))


def plate_y(P, n, y0, y1, outline, holes, s_face, s_side, s_hole):
    """horizontal plate between y0 and y1 from an (x, z) outline with optional (x, z) hole loops"""
    bm = P.bm
    o0 = [bm.verts.new((x, y0, z)) for x, z in outline]; o1 = [bm.verts.new((x, y1, z)) for x, z in outline]
    h0 = [[bm.verts.new((x, y0, z)) for x, z in h] for h in holes]; h1 = [[bm.verts.new((x, y1, z)) for x, z in h] for h in holes]
    faces = fill(P, [o0] + h0, s_face, (0, 1, 0)) + fill(P, [o1] + h1, s_face, (0, 1, 0)) + tube(P, o0, o1, s_side)
    for a, b in zip(h0, h1): faces += tube(P, a, b, s_hole)
    P.comp.append((n, faces, False))


def prism_x(P, n, x0, x1, zy, side, cap0, cap1):
    """prism along X of a closed (z, y) polygon; side(k) per polygon edge"""
    P.loft(n, [[V(x0, y, z) for z, y in zy], [V(x1, y, z) for z, y in zy]], lambda j, k: side(k) if callable(side) else side, cap0, cap1)


def linkage_frame(P, pin_z, top_y, top_z, pin_y=0.60, lug_x=0.45, cross_y=None):
    """shared three-point linkage frame (IMP-01 pattern): two lower lugs 0.14 (Z) x 0.22 (Y) x 0.08 (X) with 8-segment
    pin holes Ø0.07 on the pin axis X at (pin_y, pin_z), X +-lug_x; red A-mast legs 0.12 from the lug feet (behind the
    lugs) to a grey top-link bracket with a pin hole at (top_y, top_z); red cross bar between the legs"""
    fx, fy, fz = lug_x, pin_y - 0.10, pin_z - 0.10
    tx, ty, tz = 0.07, top_y - 0.11, top_z + 0.01
    for s in (-1, 1):
        sweep(P, f'mast_leg{s}', V(s * fx, fy, fz), V(s * tx, ty, tz), chamf_rect(0.12, 0.12, 0.02),
              [(0, 1, 0), (1, 1, 0)], lambda j, k: RED if k in (1, 5) else RED_D, RED_D, RED_D, ref=(0, 0, 1))
        plate_x(P, f'lug{s}', s * lug_x - 0.04, s * lug_x + 0.04, pin_y, pin_z, 0.22, 0.14, 0.03, 0.035, METAL, METAL, METAL_D)
    cy = cross_y if cross_y is not None else fy + 0.40 * (ty - fy)
    t = (cy - fy) / (ty - fy); xc = fx + (tx - fx) * t; zc = fz + (tz - fz) * t
    sweep(P, 'mast_cross', V(-(xc + 0.015), cy, zc), V(xc + 0.015, cy, zc), chamf_rect(0.10, 0.10, 0.02),
          [(0, 1, 0), (1, 1, 0)], lambda j, k: RED if k in (1, 7) else RED_D, RED_D, RED_D, ref=(0, 0, 1))
    plate_x(P, 'top_bracket', -0.12, 0.12, top_y, top_z, 0.20, 0.14, 0.03, 0.035, METAL, METAL, METAL_D)
    return dict(foot=(fx, fy, fz), top=(tx, ty, tz))


def drawbar_eye(P, n, cx, cy, cz, slot=METAL_D):
    """shared drawbar ring eye: octagonal outer 0.24, hole 0.08, 0.08 thick, hole axis vertical, centred (cx, cy, cz)"""
    out = [(cx + 0.12 * math.cos(math.pi / 8 + k * math.pi / 4), cz + 0.12 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    hole = [(cx + 0.04 * math.cos(math.pi / 8 + k * math.pi / 4), cz + 0.04 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    plate_y(P, n, cy - 0.04, cy + 0.04, out, [hole], slot, slot, slot)


def mate_check(sc, coll, obs, blend, cname, mine, theirs, out_png=None, view=(0.75, -0.65, 0.45), extra=(), focus=None):
    """temporary copy of a partner model from its exported .blend; partner root moved so its point `theirs` coincides
    with my point `mine`; prints error, overlaps, min distances; optional render; copy removed afterwards"""
    if not os.path.isfile(blend):
        print('MATE: partner blend missing', blend); return
    before = set(bpy.data.collections); before_m, before_i = set(bpy.data.materials), set(bpy.data.images)
    before_o = set(bpy.data.objects)
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == cname]
    pcoll = dst.collections[0]; sc.collection.children.link(pcoll)
    proot = next(o for o in pcoll.objects if o.type == 'EMPTY' and o.parent is None)
    ppt = next(o for o in pcoll.objects if o.name.split('.')[0] == theirs)
    mpt = next(o for o in coll.objects if o.name.split('.')[0] == mine)
    sc.view_layers[0].update()
    loc = proot.matrix_world.inverted() @ ppt.matrix_world
    proot.matrix_world = mpt.matrix_world @ loc.inverted()
    sc.view_layers[0].update()
    d = (ppt.matrix_world.translation - mpt.matrix_world.translation).length
    print(f'MATE {cname}.{theirs} -> {mine}: position error {d:.6f} m, rot partner {tuple(round(math.degrees(a), 3) for a in ppt.matrix_world.to_euler())} '
          f'mine {tuple(round(math.degrees(a), 3) for a in mpt.matrix_world.to_euler())}')
    for a, b in extra:
        ea = next(o for o in coll.objects if o.name.split('.')[0] == a); eb = next(o for o in pcoll.objects if o.name.split('.')[0] == b)
        print(f'  MATE extra {a} <-> partner {b}: distance {(ea.matrix_world.translation - eb.matrix_world.translation).length:.4f} m')
    pm = [o for o in pcoll.objects if o.type == 'MESH']; total = 0
    for mo in obs.values():
        mb = bvh_world(mo)
        for po in pm:
            n = len(mb.overlap(bvh_world(po))); total += n
            if n: print(f'  MATE overlap {mo.name} x {po.name}: {n} face pairs')
    for po in pm:
        pb = bvh_world(po)
        dmin = min(pb.find_nearest(mo.matrix_world @ v.co)[3] for mo in obs.values() for v in mo.data.vertices)
        print(f'  MATE min distance my meshes -> {po.name}: {dmin * 1000:.1f} mm')
    print(f'MATE total overlapping face pairs {total}; partner min height {min((o.matrix_world @ v.co).z for o in pm for v in o.data.vertices):.4f} '
          f'| my min height {min((o.matrix_world @ v.co).z for o in obs.values() for v in o.data.vertices):.4f}')
    if out_png:
        render(sc, coll, out_png, view, 0.80, (1280, 800), extra=pcoll, lens=50)
        if focus:
            render(sc, coll, out_png.replace('.png', '_close.png'), focus, 0.80, (960, 600), extra=pcoll, lens=50, focus=mpt)
    for o in list(pcoll.all_objects):
        dd = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dd, bpy.types.Mesh) and dd.users == 0: bpy.data.meshes.remove(dd)
    for c in set(bpy.data.collections) - before: bpy.data.collections.remove(c)
    for m in set(bpy.data.materials) - before_m:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - before_i:
        if i.users == 0: bpy.data.images.remove(i)
    sc.view_layers[0].update()
    print('MATE temp copy removed; leftover new objects', [o.name for o in set(bpy.data.objects) - before_o])


def report_points(coll, names):
    for nm in names:
        e = next(o for o in coll.objects if o.name.split('.')[0] == nm)
        print(f'  {nm} (Unity) {unity_of(e)} parent {e.parent.name if e.parent else None} rot {tuple(round(a, 4) for a in e.matrix_world.to_euler())}')


def clearance(obs, wheel_names, body_names=('Body',)):
    for wn in wheel_names:
        wo = obs[wn]; wb = bvh_world(wo); wc = wo.matrix_world.translation
        R = max(wo.dimensions[1], wo.dimensions[2]) / 2
        for bn in body_names:
            if bn not in obs: continue
            bb = bvh_world(obs[bn])
            dmin = min((bb.find_nearest(wo.matrix_world @ v.co)[3] for v in wo.data.vertices
                        if (wo.matrix_world @ v.co - wc).length > R * 0.72), default=None)
            print(f'  {wn} x {bn}: overlap pairs {len(bb.overlap(wb))} (axle only expected) | min tyre->{bn} {dmin:.3f} m')




def door_frame2(P, s, tag, xo, xi, y0, y1, z0, z1):
    """cab door (s = -1 left, +1 right): 4-bar red frame, opaque glass panel, dark handle (TRC-01 pattern, parametric)"""
    X = lambda a, b: (min(a, b), max(a, b))
    x0, x1 = X(s * xo, s * xi); hx0, hx1 = X(s * (xo - 0.005), s * (xi + 0.005))
    tbox(P, f'{tag}_front', x0, x1, y0, y1, z1 - 0.06, z1, 0, RED, RED, RED)
    tbox(P, f'{tag}_rear', x0, x1, y0, y1, z0, z0 + 0.06, 0, RED, RED, RED)
    tbox(P, f'{tag}_bottom', hx0, hx1, y0 + 0.005, y0 + 0.06, z0 + 0.03, z1 - 0.03, 0, RED, RED, RED)
    tbox(P, f'{tag}_top', hx0, hx1, y1 - 0.06, y1 - 0.005, z0 + 0.03, z1 - 0.03, 0, RED, RED, RED)
    gm = (xo + xi) / 2
    gx0, gx1 = X(s * (gm + 0.01), s * (gm - 0.01))
    tbox(P, f'{tag}_glass', gx0, gx1, y0 + 0.03, y1 - 0.03, z0 + 0.04, z1 - 0.04, 0, GLASS, GLASS, GLASS)
    kx0, kx1 = X(s * (gm - 0.005), s * (xo + 0.025))
    tbox(P, f'{tag}_handle', kx0, kx1, (y0 + y1) / 2 - 0.03, (y0 + y1) / 2 + 0.03, z0 + 0.10, z0 + 0.22, 0, RUBBER, RUBBER, RUBBER)


def body_part():
    P = Part('Body')
    tbox(P, 'chassis', -0.40, 0.40, 0.55, 1.12, -2.25, 2.42, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'cab_under', -0.62, 0.62, 0.70, 1.52, CAB_Z0, CAB_Z1, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'rear_housing', -0.48, 0.48, 0.56, 1.50, -2.48, -1.40, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'front_axle', -1.03, 1.03, 0.89, 1.01, WF['z'] - 0.05, WF['z'] + 0.05, 0, RUBBER, RUBBER, RUBBER)
    for s in (-1, 1):
        rod(P, f'rear_axle{s}', (s * 0.35, WR['y'], WR['z']), (s * 1.03, WR['y'], WR['z']), 0.10, RUBBER, METAL_D)
    # broad bonnet with chamfered top edges, dark grille frame with bars, corner headlights
    tbox(P, 'bonnet', -0.55, 0.55, 1.10, 2.05, 0.28, 2.55, 0.10, RED, RED_D, RED_D, RED)
    tbox(P, 'grille', -0.44, 0.44, 1.18, 1.90, 2.54, 2.58, 0, TYRE, TYRE, TYRE)
    for i in range(6):
        x = -0.325 + 0.13 * i
        tbox(P, f'grille_bar{i}', x - 0.035, x + 0.035, 1.25, 1.83, 2.57, 2.61, 0, RUBBER, RUBBER, RUBBER)
    for s in (-1, 1):
        tbox(P, f'headlight{s}', min(s * 0.45, s * 0.545), max(s * 0.45, s * 0.545), 1.66, 1.86, 2.54, 2.59, 0, RUBBER,
             lambda k: LAMP if k == 2 else RUBBER, RUBBER)
    # nose plate carrying the front linkage, top-link bracket
    tbox(P, 'nose_plate', -0.50, 0.50, 0.48, 1.15, 2.30, 2.44, 0, RUBBER, RUBBER, RUBBER)
    tbox(P, 'front_toplink_bracket', -0.10, 0.10, 0.98, 1.14, 2.41, 2.52, 0, METAL, METAL, METAL_D)
    # fuel tank (right, under the cab between the wheels), exhaust on the right of the bonnet with an elbow
    tbox(P, 'tank', 0.58, 0.80, 0.70, 1.15, -0.45, 0.10, 0.04, RED_D, RED_D, RUBBER)
    rod(P, 'exhaust', (0.38, 1.95, 0.60), (0.38, 2.70, 0.60), 0.075, METAL, METAL_D)
    sweep(P, 'exhaust_tip', V(0.38, 2.66, 0.60), V(0.38, 2.80, 0.70), ngon(0.06, 8, math.pi / 8),
          [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(1, 0, 0))
    # cab in the middle: cream base, glass core, pillars, rails, roof, beacon, mirrors, static right door frame
    tbox(P, 'cab_base', -0.635, 0.635, 1.50, 1.62, CAB_Z0 - 0.04, CAB_Z1 + 0.04, 0, CREAM, CREAM, CREAM_D)
    tbox(P, 'glass', -0.57, 0.57, 1.58, 2.95, CAB_Z0 + 0.04, CAB_Z1 - 0.04, 0, GLASS, GLASS, GLASS)
    for s in (-1, 1):
        xa, xb = min(s * 0.55, s * CAB_X), max(s * 0.55, s * CAB_X)
        tbox(P, f'pillar_f{s}', xa, xb, 1.61, 3.00, CAB_Z1 - 0.10, CAB_Z1, 0, RED, RED, RED)
        tbox(P, f'pillar_r{s}', xa, xb, 1.61, 3.00, CAB_Z0, CAB_Z0 + 0.10, 0, RED, RED, RED)
        ra, rb = min(s * 0.575, s * 0.625), max(s * 0.575, s * 0.625)
        tbox(P, f'rail_side{s}', ra, rb, 1.615, 1.68, CAB_Z0 + 0.08, DOOR_Z0 + 0.01, 0, RED, RED, RED)
    tbox(P, 'rail_front', -0.56, 0.56, 1.615, 1.68, CAB_Z1 - 0.05, CAB_Z1 - 0.01, 0, RED, RED, RED)
    tbox(P, 'rail_rear', -0.56, 0.56, 1.615, 1.68, CAB_Z0 + 0.01, CAB_Z0 + 0.06, 0, RED, RED, RED)
    tbox(P, 'rail_top', -0.63, 0.63, 2.93, 3.05, CAB_Z0 + 0.02, CAB_Z1 - 0.02, 0, RED, RED_D, RED_D)
    tbox(P, 'roof', -0.72, 0.72, 3.03, 3.32, CAB_Z0 - 0.08, CAB_Z1 + 0.08, 0.07, RED, RED_D, RED_D, RED)
    rod(P, 'beacon', (0.0, 3.30, 0.05), (0.0, 3.50, 0.05), 0.08, SIGNAL, SIGNAL)
    door_frame2(P, 1, 'door_R', 0.64, 0.56, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1)
    for s in (-1, 1):
        rod(P, f'mirror_arm{s}', (s * 0.62, 2.75, CAB_Z1 - 0.05), (s * 0.95, 2.82, CAB_Z1 + 0.04), 0.022, RUBBER, RUBBER)
        tbox(P, f'mirror{s}', min(s * 0.92, s * 0.98), max(s * 0.92, s * 0.98), 2.45, 2.85, CAB_Z1 - 0.04, CAB_Z1 + 0.10,
             0, RUBBER, RUBBER, RUBBER)
    # mudguards over all four wheels; rear ones joined to the cab; dark flaps; steps both sides
    for s in (-1, 1):
        arch(P, f'fender_f{s}', WF['z'], WF['y'], 1.06, 0.06, s * 0.78, s * 1.45, (40, 75, 110, 145))
        tbox(P, f'fender_f_bracket{s}', min(s * 0.50, s * 0.80), max(s * 0.50, s * 0.80), 1.97, 2.02, WF['z'] - 0.05,
             WF['z'] + 0.05, 0, RED_D, RED_D, RED_D)
        arch(P, f'fender_r{s}', WR['z'], WR['y'], 1.11, 0.07, s * 0.70, s * 1.45, (25, 65, 115, 155))
        tbox(P, f'fender_r_join{s}', min(s * 0.60, s * 0.71), max(s * 0.60, s * 0.71), 1.60, 2.00, CAB_Z0 + 0.05,
             DOOR_Z0 - 0.01, 0, RED_D, RED_D, RED_D)
        tbox(P, f'mudflap{s}', min(s * 0.80, s * 1.43), max(s * 0.80, s * 1.43), 1.10, 1.43, -0.70, -0.64, 0,
             RUBBER, RUBBER, RUBBER)
        for i, y in enumerate((0.72, 1.10) if s < 0 else ()):     # steps under the left door
            tbox(P, f'step{s}_{i}', min(s * 0.60, s * 0.86), max(s * 0.60, s * 0.86), y, y + 0.05, -0.40, 0.10, 0,
                 RUBBER, RUBBER, RUBBER)
    # rear: top-link bracket, PTO stub, drawbar with fork plates and vertical pin
    tbox(P, 'toplink_bracket', -0.10, 0.10, 1.25, 1.45, -2.56, -2.42, 0, METAL, METAL, METAL_D)
    rod(P, 'pto', (0, PTO[0], -2.46), (0, PTO[0], PTO[1]), 0.05, METAL_D, METAL_D)
    # fork mouth deep enough for the shared drawbar eye (outer 0.24): front plate 0.115 ahead of the pin, 5 mm behind the PTO end
    tbox(P, 'drawbar', -0.08, 0.08, 0.42, 0.52, -2.765, -2.42, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_front', -0.09, 0.09, 0.40, 0.70, -2.785, -2.755, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_bottom', -0.09, 0.09, 0.40, 0.46, FORK_END, -2.775, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_top', -0.09, 0.09, 0.64, 0.70, FORK_END, -2.775, 0, METAL, METAL, METAL_D)
    rod(P, 'fork_pin', (0, 0.38, HITCH[1]), (0, 0.72, HITCH[1]), 0.03, METAL_D, METAL_D)
    return P


def linkage(name, piv, pin, sgn, strut_top, toplink):
    """three-point linkage: cross shaft, bosses, lower arms, eyes with pins along X, lift struts, top link.
    sgn = -1 rear (arms go -Z), +1 front (arms go +Z)"""
    P = Part(name)
    py, pz = piv; lx, ly, lz = pin
    rod(P, 'cross_shaft', (-0.40, py, pz), (0.40, py, pz), 0.045, METAL_D, METAL_D)
    for s in (-1, 1):
        rod(P, f'boss{s}', (s * 0.36, py, pz), (s * 0.52, py, pz), 0.065, METAL, METAL_D)
        sweep(P, f'arm{s}', V(s * 0.46, py, pz), V(s * 0.54, ly, lz - sgn * 0.03), chamf_rect(0.08, 0.10, 0.015),
              [(0, 1, 0), (1, 1, 0)], METAL_D, METAL_D, METAL_D, ref=(1, 0, 0))
        tbox(P, f'eye{s}', min(s * 0.505, s * 0.565), max(s * 0.505, s * 0.565), ly - 0.08, ly + 0.08, lz - 0.07, lz + 0.07,
             0.02, METAL, METAL, METAL_D)
        rod(P, f'pin{s}', (s * 0.40, ly, lz), (s * 0.555, ly, lz), 0.026, METAL_D, METAL_D)
        t = 0.45
        ax, az = 0.46 + (0.54 - 0.46) * t, pz + (lz - sgn * 0.03 - pz) * t
        rod(P, f'lift_strut{s}', (s * strut_top[0], strut_top[1], strut_top[2]), (s * ax, ly + 0.02, az), 0.028, METAL, METAL)
    rod(P, 'top_link', toplink[0], toplink[1], 0.035, METAL, METAL_D)
    return P


def door_part():
    P = Part('Door_L')
    door_frame2(P, -1, 'door_L', 0.64, 0.56, DOOR_Y0, DOOR_Y1, DOOR_Z0, DOOR_Z1)
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
    name = PREFIX + 'Tractor_Large'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    lr = linkage('Linkage_Rear', LINK_R_PIV, LINK_R_PIN, -1, (0.44, 1.30, -2.10), ((0, 1.35, -2.50), (0, 1.40, -2.915)))
    lf = linkage('Linkage_Front', LINK_F_PIV, LINK_F_PIN, 1, (0.30, 1.05, 2.38), ((0, 1.06, 2.47), (0, 1.10, 2.80)))
    parts = [(body_part(), (0, 0, 0)), (lr, (0,) + LINK_R_PIV), (lf, (0,) + LINK_F_PIV),
             (door_part(), (-0.64, DOOR_Y0, DOOR_Z1))] + wheel_parts()
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
    empty(coll, 'Link3P_Rear', obs['Linkage_Rear'], V(0, LINK_R_PIN[1], LINK_R_PIN[2]))
    empty(coll, 'Link3P_Front', obs['Linkage_Front'], V(0, LINK_F_PIN[1], LINK_F_PIN[2]))
    empty(coll, 'PTO_Rear', root, V(0, PTO[0], PTO[1]))
    empty(coll, 'Hitch_Rear', root, V(0, HITCH[0], HITCH[1]))
    empty(coll, 'Seat', root, V(*SEAT))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 9000 -> {"OK" if tot <= 9000 else "OVER"} ({tot} tris, {100 * tot / 9000:.0f} %)')
    report_points(coll, ('Link3P_Rear', 'Link3P_Front', 'PTO_Rear', 'Hitch_Rear', 'Seat'))
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} rot {tuple(o.rotation_euler)}')
    clearance(obs, ('Wheel_FL', 'Wheel_FR', 'Wheel_RL', 'Wheel_RR'), ('Body', 'Linkage_Rear', 'Linkage_Front', 'Door_L'))
    return name, sc, coll, root, img, mat, obs


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
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-02_check_ref.png'), REF_VIEW, 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-02_check_right.png'), (-0.75, -0.55, 0.45), 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'TRC-02_check_rear.png'), (0.55, 0.85, 0.45), 0.80, (960, 600), lens=50)
    mate_check(sc, coll, obs, os.path.join(BLEND_DIR, 'FMS_Mach_Plough.blend'), 'FMS_Mach_Plough', 'Link3P_Rear', 'Link3P_Front',
               os.path.join(CHECK_DIR, 'TRC-02_mate_IMP-01.png'), view=(-0.85, 0.75, 0.45), focus=(-0.9, 0.35, 0.30))
elif MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = os.path.join(ART, 'Meshes', name + '.fbx')
    with_scene(sc, pc.export, name, coll, root, fbx)
    pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
    render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.70, (1280, 800), lens=50)
    if bpy.context.window:
        with_scene(sc, pc.verify, fbx)
    else:
        verify_headless(fbx, sc)
