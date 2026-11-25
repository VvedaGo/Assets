# IMP-05 DiscHarrow (FMS_Mach_DiscHarrow) - FarmMachinery pack, stage E7 (series batch 1). Procedural, idempotent.
# Trailed disc harrow: central frame with two V gangs, folding wings (Transport = rest, folded up), two wheels, shared drawbar eye. Built from the spec only (no preview reference).
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- IMP-05 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/IMP-05/ + mating check (temporary partner copy)
#   export = build + FBX + collection-only .blend + ONE preview (reference camera) + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py (standard convention: <part>_Low1 as direct root children, CATALOG item 3)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['IMP-05', 'build']})
#   Live builds go to an own scene + collection 'IMP-05_DiscHarrow'; nothing else is touched.
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
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'IMP-05')
SCENE = OUTER = 'IMP-05_DiscHarrow'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'IMP-05'
MODE = _a[1] if len(_a) > 1 else 'build'

PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))


# ---------------- design numbers (Unity coordinates, metres; root on the ground at the bbox centre) ----------------
# No preview reference exists (owner decision 2026-11-24): built from IMP-05.3d.md. Fold geometry adjusted, see notes.md:
# hinge on the disc-axle side of the frame edge at Y 0.50 (spec 0.67) and fold 90 deg (spec ~65 deg), the only layout
# that keeps the folded discs inside the 2.6 m transport width with 0.70 m discs hanging under the wing arm.
HITCH_F = (0.55, 2.50)                           # Hitch_Front = drawbar eye centre (y, z), spec
REAR_END = -2.611                                # rear cross member = -(eye front 2.611): root stays at the bbox centre
HINGE = (0.80, 0.50)                             # Wing hinge (|x|, y), axis Z; rest = Transport (wing folded up 90 deg)
GANG_Z = (0.55, -1.85)                           # front / rear gang axle line at X 0
GANG_ANG = math.radians(12)                      # front gang V (outer ends back), rear gang inverted V (outer ends forward)
DISC_R, DISC_T, DISC_Y = 0.35, 0.04, 0.35        # 12-segment disc apothem, thickness, centre height (bottom at Y 0)
CENTRAL_X = (0.15, 0.45)                         # central section discs (each side)
WING_U = (0.30, 0.55, 0.80, 1.05)                # wing discs, distance from the hinge along the gang (first one clears the ear)
WHEEL = dict(d=0.90, w=0.30, x=0.70, y=0.45, z=-0.80, lugs=12)
RAIL_X = (0.24, 0.36)                            # central frame rails (inner, outer |x|): between the central discs
REF_VIEW = (0.64, -0.77, 0.58)                   # standard series camera: front-left 3/4 (~40 deg), ~30 deg up



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




def gang_z(g, x):
    """axle line of gang g (0 front V, 1 rear inverted V) at |x|"""
    return GANG_Z[g] + (-1 if g == 0 else 1) * math.tan(GANG_ANG) * abs(x)


def gang_dir(g, s):
    """unit direction along gang g going outward on side s (+1 right, -1 left), in the XZ plane"""
    dz = (-1 if g == 0 else 1) * math.tan(GANG_ANG)
    v = V(s, 0, dz); return v.normalized()


def disc(P, n, c, a, down=None):
    """flat 12-segment disc (apothem DISC_R, a flat side towards `down`), chamfered rim (slot 8), faces slot 7,
    thickness DISC_T, axis a"""
    a = Vector(a).normalized(); k = 12
    dn = Vector(down) if down is not None else V(0, -1, 0)
    e3 = (-dn - a * a.dot(-dn)).normalized(); e2 = a.cross(e3).normalized()
    def ring(off, apo):
        rc = apo / math.cos(math.pi / k)
        return [c + a * off + e2 * (rc * math.cos(math.pi / k + 2 * math.pi * i / k)) + e3 * (rc * math.sin(math.pi / k + 2 * math.pi * i / k)) for i in range(k)]
    h = DISC_T / 2
    P.loft(n, [ring(-h, DISC_R), ring(h - 0.015, DISC_R), ring(h, DISC_R - 0.02)], METAL_D, METAL, METAL)   # chamfer on the working face


def bar(P, n, p0, p1, w, h, slot, ref=None, chamf=False):
    """straight member; plain 4-sided section for small hangers/struts/axles (budget), chamfered for the main arms"""
    p0, p1 = Vector(p0), Vector(p1); d = (p1 - p0).normalized()
    if ref is None: ref = (0, 1, 0) if abs(d.y) < 0.9 else (1, 0, 0)
    prof = chamf_rect(w, h, min(w, h) * 0.15) if chamf else [(w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2)]
    sweep(P, n, p0, p1, prof, [(0, 1, 0), (1, 1, 0)], slot, METAL_D, METAL_D, ref=ref)


def frame_part():
    P = Part('Frame')
    hy, hz = HITCH_F; r0, r1 = RAIL_X
    for s in (-1, 1):
        tbox(P, f'rail{s}', min(s * r0, s * r1), max(s * r0, s * r1), 0.60, 0.74, REAR_END + 0.10, 1.33, 0.02, METAL, METAL, METAL_D)
    for nm, z0, z1 in (('front', 1.20, 1.34), ('mid', -0.86, -0.74), ('rear', REAR_END, REAR_END + 0.14)):
        tbox(P, f'cross_{nm}', -r1 - 0.01, r1 + 0.01, 0.62, 0.72, z0, z1, 0, METAL, METAL, METAL_D)
        tbox(P, f'cover_{nm}', -r1, r1, 0.73, 0.79, max(z0 - 0.10, REAR_END + 0.005), z1 + 0.10, 0.02, RED, RED_D, RED_D)
    # central gang sections: V-shaped axles, 4 discs each, hangers, gang beams with struts to the cross members
    for g in (0, 1):
        for s in (-1, 1):
            d = gang_dir(g, s)
            a0 = V(0, DISC_Y, gang_z(g, 0)); a1 = V(s * 0.66, DISC_Y, gang_z(g, 0.66))
            bar(P, f'axle{g}{s}', a0 - d * 0.04, a1, 0.08, 0.08, METAL_D)
            for i, x in enumerate(CENTRAL_X):
                disc(P, f'disc{g}{s}{i}', V(s * x, DISC_Y, gang_z(g, x)) + V(0, 0, 0), d)
            hx = 0.30
            bar(P, f'hanger{g}{s}', V(s * hx, DISC_Y, gang_z(g, hx)), V(s * hx, 0.84, gang_z(g, hx)), 0.07, 0.07, METAL)
            bar(P, f'gang_beam{g}{s}', V(0, 0.84, gang_z(g, 0)) - d * 0.04, V(s * 0.33, 0.84, gang_z(g, 0.33)), 0.10, 0.10, METAL, chamf=True)
            zt = 1.27 if g == 0 else -0.80
            bar(P, f'gang_strut{g}{s}', V(s * 0.25, 0.80, gang_z(g, 0.25)), V(s * 0.25, 0.70, zt), 0.07, 0.07, METAL)
        # hinge ears: a bar on the rail top over the outer central disc, then a drop to the wing knuckle on the hinge axis
        for s in (-1, 1):
            hz_ = gang_z(g, HINGE[0])
            tbox(P, f'hinge_ear{g}{s}', min(s * r0, s * (HINGE[0] - 0.03)), max(s * r0, s * (HINGE[0] - 0.03)),
                 0.71, 0.76, hz_ - 0.07, hz_ + 0.07, 0.01, METAL, METAL, METAL_D)
            tbox(P, f'hinge_drop{g}{s}', min(s * (HINGE[0] - 0.08), s * (HINGE[0] - 0.01)), max(s * (HINGE[0] - 0.08), s * (HINGE[0] - 0.005)),
                 HINGE[1] - 0.08, 0.75, hz_ - 0.065, hz_ + 0.065, 0, METAL_D, METAL_D, METAL_D)
    # wheel axle hangers and stubs under the mid cross member
    for s in (-1, 1):
        tbox(P, f'wheel_hanger{s}', min(s * r0, s * r1), max(s * r0, s * r1), WHEEL['y'] - 0.06, 0.63, WHEEL['z'] - 0.06, WHEEL['z'] + 0.06, 0,
             METAL_D, METAL_D, METAL_D)
        rod(P, f'wheel_axle{s}', (s * (r0 + 0.04), WHEEL['y'], WHEEL['z']), (s * 0.665, WHEEL['y'], WHEEL['z']), 0.04, METAL_D, METAL_D)
    # shared drawbar: A-beams from the rail fronts to a single beam into the ring eye
    for s in (-1, 1):
        sweep(P, f'drawbar{s}', V(s * 0.30, 0.67, 1.25), V(s * 0.07, hy + 0.01, hz - 0.28), chamf_rect(0.12, 0.12, 0.02),
              [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(0, 1, 0))
    tbox(P, 'drawbar_tip', -0.07, 0.07, hy - 0.06, hy + 0.06, hz - 0.34, hz - 0.10, 0.015, METAL, METAL, METAL_D)
    drawbar_eye(P, 'eye', 0, hy, hz)
    return P


def wing_part(s):
    """wing in its WORK layout (u along the gang outward from the hinge, v up), then folded 90 deg up about the Z hinge:
    x = s * (HINGE_x - v), y = HINGE_y + u"""
    P = Part('Wing_' + ('L' if s < 0 else 'R'))
    hxa, hya = HINGE
    def W(u, v, g):
        """work-layout point on gang g -> folded transport point"""
        x = hxa + u * math.cos(GANG_ANG); z = gang_z(g, x)
        return V(s * (hxa - v), hya + u * math.cos(GANG_ANG), z)
    for g in (0, 1):
        dz = gang_z(g, hxa + 1.0) - gang_z(g, hxa)
        a = V(0, 1.0, dz).normalized()                  # folded gang direction (up, with the V skew in Z)
        zc = gang_z(g, hxa)
        tbox(P, f'knuckle{g}', min(s * (hxa - 0.035), s * (hxa + 0.19)), max(s * (hxa - 0.035), s * (hxa + 0.19)),
             hya - 0.08, hya + 0.07, zc - 0.06, zc + 0.06, 0.015, METAL_D, METAL_D, METAL_D)
        v_ax = DISC_Y - hya
        bar(P, f'axle{g}', W(0.04, v_ax, g), W(1.14, v_ax, g), 0.08, 0.08, METAL_D, ref=(1, 0, 0))
        for i, u in enumerate(WING_U):
            disc(P, f'disc{g}{i}', W(u, v_ax, g), a, down=V(s, 0, 0))
        v_arm = 0.84 - hya
        bar(P, f'arm{g}', W(0.30, v_arm, g), W(1.24, v_arm, g), 0.12, 0.12, METAL, ref=(1, 0, 0), chamf=True)
        for u in (0.42, 0.92):
            bar(P, f'hanger{g}_{u:.1f}', W(u, v_ax, g), W(u, v_arm, g), 0.07, 0.07, METAL, ref=(0, 0, 1))
    # longitudinal wing beam joining the two arm ends, orange tip blocks at both ends
    p_f, p_r = W(1.18, 0.84 - hya, 0), W(1.18, 0.84 - hya, 1)
    bar(P, 'wing_beam', p_r + V(0, 0, -0.06), p_f + V(0, 0, 0.06), 0.12, 0.12, METAL, ref=(0, 1, 0), chamf=True)
    for nm, p, dzs in (('tip_front', p_f, 1), ('tip_rear', p_r, -1)):
        tbox(P, nm, p.x - 0.075, p.x + 0.075, p.y - 0.075, p.y + 0.075, p.z + dzs * 0.05 - 0.075, p.z + dzs * 0.05 + 0.075, 0.02,
             SIGNAL, SIGNAL, SIGNAL)
    return P


def wheel_parts():
    out = []
    for nm, s in (('Wheel_L', -1), ('Wheel_R', 1)):
        P = Part(nm); c = (s * WHEEL['x'], WHEEL['y'], WHEEL['z'])
        wheel(P, c, WHEEL['d'], WHEEL['w'], WHEEL['lugs'], outer=s)
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
    name = PREFIX + 'DiscHarrow'
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    hx, hy = HINGE
    parts = [(frame_part(), (0, 0, 0)), (wing_part(-1), (-hx, hy, 0.0)), (wing_part(1), (hx, hy, 0.0))] + wheel_parts()
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
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 4000 -> {"OK" if tot <= 4000 else "OVER"} ({tot} tris, {100 * tot / 4000:.0f} %)')
    report_points(coll, ('Hitch_Front',))
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} rot {tuple(o.rotation_euler)}')
    clearance(obs, ('Wheel_L', 'Wheel_R'), ('Frame', 'Wing_L', 'Wing_R'))
    B = {k: bvh_world(o) for k, o in obs.items()}
    for a, b in (('Wing_L', 'Frame'), ('Wing_R', 'Frame'), ('Wing_L', 'Wing_R')):
        print(f'  TRANSPORT overlap {a} x {b}: {len(B[a].overlap(B[b]))} face pairs (knuckle on the ears expected for wing x frame)')
    for nm in ('Wing_L', 'Wing_R'):
        o = obs[nm]
        for sgn in (1, -1):
            o.rotation_euler = (0, sgn * math.radians(90), 0); sc.view_layers[0].update()
            wp = [o.matrix_world @ v.co for v in o.data.vertices]
            if max(abs(p.x) for p in wp) > 1.7: break
        print(f'  WORK {nm}: Blender rot_y {sgn * 90} deg -> |X| max {max(abs(p.x) for p in wp):.3f}, min height {min(p.z for p in wp):.3f}')
    B = {k: bvh_world(o) for k, o in obs.items()}
    allp = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    print(f'  WORK pose: X {min(-p.x for p in allp):.3f}..{max(-p.x for p in allp):.3f} height {max(p.z for p in allp):.3f} | '
          f'overlap Wing_L x Frame {len(B["Wing_L"].overlap(B["Frame"]))}, Wing_R x Frame {len(B["Wing_R"].overlap(B["Frame"]))}, '
          f'wings x wheels {len(B["Wing_L"].overlap(B["Wheel_L"])) + len(B["Wing_R"].overlap(B["Wheel_R"]))}')
    if MODE in ('build', 'export'):
        os.makedirs(CHECK_DIR, exist_ok=True)
        render(sc, coll, os.path.join(CHECK_DIR, 'IMP-05_check_work.png'), REF_VIEW, 0.85, (1280, 800), lens=50)
    for nm in ('Wing_L', 'Wing_R'): obs[nm].rotation_euler = (0, 0, 0)
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
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-05_check_ref.png'), REF_VIEW, 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-05_check_rear.png'), (-0.55, 0.85, 0.45), 0.80, (960, 600), lens=50)
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-05_check_top.png'), (0.001, -0.02, 1.0), 0.80, (960, 600), lens=50)
    mate_check(sc, coll, obs, os.path.join(BLEND_DIR, 'FMS_Mach_Tractor_Cab.blend'), 'FMS_Mach_Tractor_Cab', 'Hitch_Front', 'Hitch_Rear',
               os.path.join(CHECK_DIR, 'IMP-05_mate_TRC-01.png'), view=(0.85, 0.75, 0.45),
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
