# IMP-03 Sprayer (FMS_Mach_Sprayer) - FarmMachinery pack, stage E7 (series batch 1). Procedural, idempotent.
# Trailed sprayer: 16-segment tank on a steel chassis, folding lattice booms (Transport = rest), two wheels, shared drawbar eye.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- IMP-03 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/IMP-03/ + mating check (temporary partner copy)
#   export = build + FBX + collection-only .blend + ONE preview (reference camera) + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children, CATALOG item 3)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['IMP-03', 'build']})
#   Live builds go to an own scene + collection 'IMP-03_Sprayer'; nothing else is touched.
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
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'IMP-03')
SCENE = OUTER = 'IMP-03_Sprayer'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'IMP-03'
MODE = _a[1] if len(_a) > 1 else 'build'

PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))


# ---------------- design numbers (Unity coordinates, metres; root on the ground at the bbox centre) ----------------
HITCH_F = (0.55, 2.80)                           # Hitch_Front = drawbar eye centre (y, z), spec
PTO_F = (0.70, 2.95)                             # PTO_Front = Hitch_Front + (0, 0.15, 0.15) (CATALOG item 6)
REAR_END = -2.911                                # rear boom carrier = -(eye front 2.92): root stays at the bbox centre
WHEEL = dict(d=1.30, w=0.40, x=1.05, y=0.65, z=-0.50, lugs=16, lug_h=0.10)
TANK = dict(y=1.90, z0=-1.95, z1=1.45, r=0.80)   # 16-segment cylinder (apothem r); reference: longer and slimmer than spec 1.8 x 3.0
BOOM_PIV = (1.10, 1.90, -2.60)                   # Boom hinge (|x|, y, z), axis Y; rest = folded forward (Transport)
BOOM_X, BOOM_Y0, BOOM_Y1 = 1.20, 1.65, 2.15      # truss plane X, bottom / top rail centres
BOOM_TIP = 1.45                                  # rail tips (reference: just ahead of the tank front)
REF_VIEW = (0.80, -0.60, 0.50)                   # Blender dir target->camera: front-left 3/4 (~53 deg off the nose), ~27 deg up (reference)



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




def cyl_ring(z, apo, n=16, cy=0.0, cx=0.0):
    rc = apo / math.cos(math.pi / n)
    return [V(cx + rc * math.cos(math.pi / n + 2 * math.pi * k / n), cy + rc * math.sin(math.pi / n + 2 * math.pi * k / n), z) for k in range(n)]


def chassis_part():
    P = Part('Chassis')
    hy, hz = HITCH_F
    # frame rails, cross members, rear boom carrier with posts and pivot pins, tank saddles, axle with hangers
    for s in (-1, 1):
        tbox(P, f'rail{s}', min(s * 0.48, s * 0.62), max(s * 0.48, s * 0.62), 0.75, 0.91, REAR_END + 0.14, 1.40, 0.02, METAL, METAL, METAL_D)
    for z in (-1.60, 0.60):
        tbox(P, f'cross{z:+.1f}', -0.50, 0.50, 0.77, 0.89, z - 0.06, z + 0.06, 0, METAL, METAL, METAL_D)
    tbox(P, 'boom_carrier', -1.20, 1.20, 0.76, 0.92, REAR_END, REAR_END + 0.15, 0.02, METAL, METAL, METAL_D)
    bx, by, bz = BOOM_PIV
    for s in (-1, 1):
        tbox(P, f'boom_post{s}', min(s * 1.04, s * 1.16), max(s * 1.04, s * 1.16), 0.85, 2.30, REAR_END + 0.10, bz - 0.085, 0,
             METAL, METAL, METAL_D)
        rod(P, f'boom_pin{s}', (s * bx, 2.20, bz), (s * bx, 2.38, bz), 0.06, METAL_D, METAL_D)
        tbox(P, f'boom_pin_arm{s}', min(s * 1.04, s * 1.16), max(s * 1.04, s * 1.16), 2.28, 2.36, bz - 0.09, bz + 0.03, 0,
             METAL, METAL, METAL_D)
        # front boom rest: bar from the rail out, post up to the boom bottom rail
        tbox(P, f'rest_bar{s}', min(s * 0.55, s * 1.19), max(s * 0.55, s * 1.19), 0.80, 0.90, 0.95, 1.05, 0, METAL, METAL, METAL_D)
        tbox(P, f'rest_post{s}', min(s * 1.12, s * 1.18), max(s * 1.12, s * 1.18), 0.82, BOOM_Y0 - 0.03, 0.96, 1.04, 0, METAL, METAL, METAL_D)
    for z in (-1.20, 0.80):
        tbox(P, f'saddle{z:+.1f}', -0.62, 0.62, 0.88, 1.12, z - 0.08, z + 0.08, 0, METAL, METAL, METAL_D)
    tbox(P, 'axle', -1.00, 1.00, 0.58, 0.72, WHEEL['z'] - 0.07, WHEEL['z'] + 0.07, 0, METAL_D, METAL_D, METAL_D)
    for s in (-1, 1):
        tbox(P, f'axle_hanger{s}', min(s * 0.50, s * 0.60), max(s * 0.50, s * 0.60), 0.70, 0.78, WHEEL['z'] - 0.06, WHEEL['z'] + 0.06, 0,
             METAL_D, METAL_D, METAL_D)
    # tank: 16-segment cylinder along Z with chamfered flat ends, lower facets darker; straps; filler dome; beacon
    ty, z0, z1, r = TANK['y'], TANK['z0'], TANK['z1'], TANK['r']
    rings = [cyl_ring(z0, r - 0.06, cy=ty), cyl_ring(z0 + 0.06, r, cy=ty), cyl_ring(z1 - 0.06, r, cy=ty), cyl_ring(z1, r - 0.06, cy=ty)]
    lower = lambda k: math.sin(math.pi / 16 + 2 * math.pi * (k + 0.5) / 16) < -0.05
    P.loft('tank', rings, lambda j, k: RED_D if lower(k) else RED, RED, RED)
    for z in (-1.10, 0.70):
        P.loft(f'strap{z:+.1f}', [cyl_ring(z - 0.04, r + 0.015, cy=ty), cyl_ring(z + 0.04, r + 0.015, cy=ty)], METAL, METAL, METAL)
    dz = 0.55
    dome = [[V(p.x, p.z, dz + p.y) for p in ring] for ring in (cyl_ring(ty + r - 0.10, 0.30, 8), cyl_ring(2.94, 0.30, 8), cyl_ring(3.00, 0.24, 8))]
    P.loft('dome', dome, lambda j, k: METAL if j < 1 else METAL_L, METAL_D, METAL_L)
    beacon = [[V(p.x, p.z, -0.10 + p.y) for p in ring] for ring in (cyl_ring(ty + r - 0.06, 0.07, 8), cyl_ring(ty + r + 0.14, 0.07, 8))]
    P.loft('beacon', beacon, SIGNAL, SIGNAL, SIGNAL)
    # ladder at the rear left: platform on the rails, two rails bent into the tank end, three rungs (galvanised, slot 9)
    tbox(P, 'platform', -0.62, 0.0, 0.88, 0.93, -2.40, -2.00, 0, METAL_L, METAL_L, METAL_D)
    for x in (-0.45, -0.15):
        tbox(P, f'ladder_rail{x:+.2f}', x - 0.03, x + 0.03, 0.90, 2.45, -2.04, -1.98, 0, METAL_L, METAL_L, METAL_L)
        sweep(P, f'ladder_top{x:+.2f}', V(x, 2.42, -2.01), V(x, 2.62, -1.82), chamf_rect(0.06, 0.06, 0.01),
              [(0, 1, 0), (1, 1, 0)], METAL_L, METAL_L, METAL_L, ref=(1, 0, 0))
    for y in (1.30, 1.70, 2.10):
        tbox(P, f'rung{y:.2f}', -0.47, -0.13, y, y + 0.05, -2.03, -1.99, 0, METAL_L, METAL_L, METAL_L)
    # shared drawbar: A-beams from the rails to a single beam into the ring eye (Hitch_Front at the eye centre)
    for s in (-1, 1):
        sweep(P, f'drawbar{s}', V(s * 0.55, 0.83, 1.30), V(s * 0.07, hy + 0.01, hz - 0.28), chamf_rect(0.12, 0.12, 0.02),
              [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(0, 1, 0))
    tbox(P, 'drawbar_tip', -0.07, 0.07, hy - 0.06, hy + 0.06, hz - 0.34, hz - 0.10, 0.015, METAL, METAL, METAL_D)
    drawbar_eye(P, 'eye', 0, hy, hz)
    rod(P, 'pto_stub', (0, PTO_F[0] - 0.06, hz - 0.42), (0, PTO_F[0] - 0.06, hz - 0.30), 0.06, METAL_D, METAL_D, seg=6)
    return P


def boom_part(s):
    P = Part('Boom_' + ('L' if s < 0 else 'R'))
    bx, by, bz = BOOM_PIV; x = s * BOOM_X
    X = lambda a, b: (min(s * a, s * b), max(s * a, s * b))
    k0, k1 = X(1.04, 1.24)
    tbox(P, 'knuckle', k0, k1, 1.58, 2.22, bz - 0.09, bz + 0.09, 0.02, METAL, METAL, METAL_D)
    ra, rb = X(BOOM_X - 0.035, BOOM_X + 0.035)
    ta, tb = X(BOOM_X - 0.0375, BOOM_X + 0.0375)
    tip0 = BOOM_TIP - 0.50
    for y in (BOOM_Y0, BOOM_Y1):
        tbox(P, f'rail{y:.2f}', ra, rb, y - 0.035, y + 0.035, bz + 0.05, BOOM_TIP - 0.10, 0, METAL_D, METAL_D, METAL_D)
    za, zb = bz + 0.09, BOOM_TIP - 0.25
    n = 6
    for i in range(n):
        z_a = za + (zb - za) * i / n; z_b = za + (zb - za) * (i + 1) / n
        ya, yb = (BOOM_Y0, BOOM_Y1) if i % 2 == 0 else (BOOM_Y1, BOOM_Y0)
        sweep(P, f'diag{i}', V(x, ya, z_a), V(x, yb, z_b), chamf_rect(0.06, 0.06, 0.01), [(0, 1, 0), (1, 1, 0)],
              METAL, METAL, METAL, ref=(1, 0, 0))
    pa, pb = X(BOOM_X - 0.03, BOOM_X + 0.03)
    tbox(P, 'post_end', pa, pb, BOOM_Y0, BOOM_Y1, BOOM_TIP - 0.28, BOOM_TIP - 0.22, 0, METAL, METAL, METAL)
    oa, ob = X(1.13, 1.25)
    tbox(P, 'tip_block', oa, ob, BOOM_Y0 - 0.06, BOOM_Y1 + 0.06, BOOM_TIP - 0.245, BOOM_TIP + 0.08, 0.03, SIGNAL, SIGNAL, SIGNAL)

    return P


def wheel_parts():
    out = []
    for nm, s in (('Wheel_L', -1), ('Wheel_R', 1)):
        P = Part(nm); c = (s * WHEEL['x'], WHEEL['y'], WHEEL['z'])
        wheel(P, c, WHEEL['d'], WHEEL['w'], WHEEL['lugs'], outer=s, lug_h=WHEEL['lug_h'])
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
    name = PREFIX + 'Sprayer'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    bx, by, bz = BOOM_PIV
    parts = [(chassis_part(), (0, 0, 0)), (boom_part(-1), (-bx, by, bz)), (boom_part(1), (bx, by, bz))] + wheel_parts()
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
    empty(coll, 'Hitch_Front', root, V(0, HITCH_F[0], HITCH_F[1]))
    empty(coll, 'PTO_Front', root, V(0, PTO_F[0], PTO_F[1]))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 5000 (lattice up to 10000) -> {"OK" if tot <= 5000 else "OVER"} ({tot} tris, {100 * tot / 5000:.0f} %)')
    report_points(coll, ('Hitch_Front', 'PTO_Front'))
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} rot {tuple(o.rotation_euler)}')
    clearance(obs, ('Wheel_L', 'Wheel_R'), ('Chassis', 'Boom_L', 'Boom_R'))
    B = {k: bvh_world(o) for k, o in obs.items()}
    for a, b in (('Boom_L', 'Chassis'), ('Boom_R', 'Chassis')):
        print(f'  overlap {a} x {b}: {len(B[a].overlap(B[b]))} face pairs (pivot pin / rest post expected)')
    # Work pose check: booms rotated about their Y hinge so each swings outward
    import mathutils
    for nm, sgn in (('Boom_L', 1), ('Boom_R', -1)):
        o = obs[nm]; o.rotation_euler = (0, 0, sgn * math.radians(90))
    sc.view_layers[0].update()
    wp = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    print(f'  WORK pose (booms +-90 deg about Y): span X {max(-p.x for p in wp) - min(-p.x for p in wp):.3f} m, '
          f'boom tips X {[round(-(obs[n].matrix_world @ max(obs[n].data.vertices, key=lambda v: (obs[n].matrix_world @ v.co - obs[n].matrix_world.translation).length).co).x, 3) for n in ("Boom_L", "Boom_R")]}')
    if MODE == 'build':
        render(sc, coll, os.path.join(CHECK_DIR, 'IMP-03_check_work.png'), REF_VIEW, 0.85, (960, 600), lens=50)
    for nm in ('Boom_L', 'Boom_R'): obs[nm].rotation_euler = (0, 0, 0)
    sc.view_layers[0].update()
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
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-03_check_ref.png'), REF_VIEW, 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-03_check_rear.png'), (-0.55, 0.85, 0.45), 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-03_check_top.png'), (0.001, -0.02, 1.0), 0.80, (960, 600), lens=50)
    mate_check(sc, coll, obs, os.path.join(BLEND_DIR, 'FMS_Mach_Tractor_Cab.blend'), 'FMS_Mach_Tractor_Cab', 'Hitch_Front', 'Hitch_Rear',
               os.path.join(CHECK_DIR, 'IMP-03_mate_TRC-01.png'), view=(0.85, 0.75, 0.45), extra=(('PTO_Front', 'PTO_Rear'),),
               focus=(0.9, 0.35, 0.45))
elif MODE == 'export':
    for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
    fbx = os.path.join(ART, 'Meshes', name + '.fbx')
    with_scene(sc, pc.export, name, coll, root, fbx)
    pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
    render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.75, (1280, 800), lens=50)
    if bpy.context.window:
        with_scene(sc, pc.verify, fbx)
    else:
        verify_headless(fbx, sc)
