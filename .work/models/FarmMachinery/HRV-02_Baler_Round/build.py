# HRV-02 Baler_Round (FMS_Mach_Baler_Round) - FarmMachinery pack, stage E7 (series batch 2). Procedural, idempotent.
# Round baler: 16-sided red bale chamber (front half static, rear half = Tailgate hinged at the top), grey bands, drive
# cover box, pickup with tine rows under a red guard, chassis, red fenders, red A-drawbar with the shared eye (Hitch_Front),
# PTO stub (PTO_Front), support stand, Bale_Out point. Closed in the FBX; Open = Tailgate rotated in the prefab.
ITEM_ID = 'HRV-02'
FOLDER = 'HRV-02_Baler_Round'
ASSET = 'Baler_Round'
BUDGET = 5000
CENTER_X = False
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- <ID> build|export
#   check  = build + printed checks only (used to compare the live and headless fingerprints)
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/<ID>/ + mating checks (temporary partner
#            copies loaded from art/FarmMachinery/Blend, removed in the same run)
#   export = build + FBX + collection-only .blend + ONE preview (reference camera) + FBX re-import verify; then LOD1 with
#            Tools/blender/make_lod1.py when the catalogue says LOD (standard convention: <part>_Low1 as direct root children)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['<ID>', 'build']})
#   Live builds go to an own scene + collection '<ID>_<Name>'; nothing else is touched.
# Geometry is written in UNITY coordinates (x right, y up, z forward) and mapped to Blender as (-x, -z, y); the FBX export
# (-Z forward, Y up, baked) gives back the design coordinates in Unity. The design is shifted in Z (and X if needed) at the
# end so the root sits at the bbox centre; all printed point positions are final (after the shift).
# Shared helpers (pack wheel, tbox, rod, arch, plate_x/y/z, prism_x, linkage_frame, drawbar_eye, scene, render, verify)
# are verbatim copies from the accepted batch-1 scripts (TRC-01, IMP-01, IMP-03, ATT-03); rear_fork = TRC-01 fork after
# the 2026-11-24 fix (front plate 0.125 ahead of the pin, shared eye Ø0.24).
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
BLEND_DIR = os.path.join(REPO, 'art', 'FarmMachinery', 'Blend')          # partner models for mating checks
PREFIX, ATLAS = 'FMS_Mach_', 'FarmMachinery_Red'          # shared pack atlas T_FarmMachinery_Red_BaseColor.png
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', ITEM_ID)
SCENE = OUTER = FOLDER
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else ITEM_ID
MODE = _a[1] if len(_a) > 1 else 'build'

# FarmMachinery palette (STYLE.md): cells 0-9 standard, 10-15 machinery colours; Red atlas
PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)


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


def xbox(P, n, x0, x1, y0, y1, z0, z1, side=METAL, top=METAL, bot=METAL_D):
    """box with sorted bounds (convenience for mirrored parts)"""
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    tbox(P, n, x0, x1, y0, y1, z0, z1, 0, top, side, bot)


def rod(P, n, p0, p1, r, slot, cap, seg=8):
    a = Vector(p1) - Vector(p0)
    ref = (0, 1, 0) if abs(a.normalized().y) < 0.9 else (1, 0, 0)
    sweep(P, n, Vector(p0), Vector(p1), ngon(r, seg, math.pi / seg), [(0, 1, 0), (1, 1, 0)], slot, cap, cap, ref=ref)


def beam(P, n, p0, p1, w, h, side, top=None, bot=None, c=0.015, ref=(0, 1, 0)):
    """chamfered rectangular bar between two points; w across (horizontal), h along ref"""
    t = top if top is not None else side; b = bot if bot is not None else side
    sweep(P, n, Vector(p0), Vector(p1), chamf_rect(w, h, c), [(0, 1, 0), (1, 1, 0)], side, b, t, ref=ref)


def arch(P, n, cz, cy, r, th, xa, xb, angles, s_out=RED, s_side=RED_D):
    """mudguard: chamfered plate swept over a wheel (centre z, y), inner radius r, thickness th, across X xa..xb"""
    pts = [V(0, cy + r * math.sin(math.radians(t)), cz + r * math.cos(math.radians(t))) for t in angles]
    s = 1 if xb > xa else -1
    sec = [(0, xa), (0, xb), (-th + 0.03, xb), (-th, xb - s * 0.03), (-th, xa)]
    sl = {0: s_side, 1: s_side, 2: s_out, 3: s_out, 4: s_side}
    path_sweep(P, n, pts, (1, 0, 0), sec, lambda j, k: sl[k], s_side)


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


def plate_z(P, n, z0, z1, outline, holes, s_face, s_side, s_hole):
    """plate between z0 and z1 from an (x, y) outline with optional (x, y) hole loops (ATT-03)"""
    bm = P.bm
    o0 = [bm.verts.new((x, y, z0)) for x, y in outline]; o1 = [bm.verts.new((x, y, z1)) for x, y in outline]
    h0 = [[bm.verts.new((x, y, z0)) for x, y in h] for h in holes]; h1 = [[bm.verts.new((x, y, z1)) for x, y in h] for h in holes]
    faces = fill(P, [o0] + h0, s_face, (0, 0, 1)) + fill(P, [o1] + h1, s_face, (0, 0, 1)) + tube(P, o0, o1, s_side)
    for a, b in zip(h0, h1): faces += tube(P, a, b, s_hole)
    P.comp.append((n, faces, False))


def prism_x(P, n, x0, x1, zy, side, cap0, cap1):
    """prism along X of a closed (z, y) polygon; side(k) per polygon edge"""
    P.loft(n, [[V(x0, y, z) for z, y in zy], [V(x1, y, z) for z, y in zy]], lambda j, k: side(k) if callable(side) else side, cap0, cap1)


def cr(cx, cy, w, h, c):
    return [(cx + x, cy + y) for x, y in chamf_rect(w, h, c)]


def cyl_ring(z, apo, n=16, cy=0.0, cx=0.0, ph=None):
    ph = math.pi / n if ph is None else ph
    rc = apo / math.cos(math.pi / n)
    return [V(cx + rc * math.cos(ph + 2 * math.pi * k / n), cy + rc * math.sin(ph + 2 * math.pi * k / n), z) for k in range(n)]


def xring(x, apo, cy, cz, n=16, ph=None):
    """ring in a plane normal to X (for drums with axis X), apothem apo, centre (cy, cz)"""
    ph = math.pi / n if ph is None else ph
    rc = apo / math.cos(math.pi / n)
    return [V(x, cy + rc * math.cos(ph + 2 * math.pi * k / n), cz + rc * math.sin(ph + 2 * math.pi * k / n)) for k in range(n)]


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


def a_drawbar(P, hy, hz, x_root, y_root, z_root, slot=METAL, slot_d=METAL_D, tip_len=0.24):
    """shared A-drawbar (IMP-03 pattern): two 0.12 bars from (+-x_root, y_root, z_root) converging into a single tip block
    that holds the shared eye; Hitch_Front = eye centre (0, hy, hz)"""
    for s in (-1, 1):
        sweep(P, f'drawbar{s}', V(s * x_root, y_root, z_root), V(s * 0.07, hy + 0.01, hz - 0.10 - tip_len + 0.06),
              chamf_rect(0.12, 0.12, 0.02), [(0, 1, 0), (1, 1, 0)], slot, slot_d, slot_d, ref=(0, 1, 0))
    tbox(P, 'drawbar_tip', -0.07, 0.07, hy - 0.06, hy + 0.06, hz - 0.10 - tip_len, hz - 0.10, 0.015, slot, slot, slot_d)
    drawbar_eye(P, 'eye', 0, hy, hz)


def rear_fork(P, hy, hz, z_end, support_top=None, x=0.09):
    """rear drawbar fork (TRC-01 after the 2026-11-24 fix) around the pin Hitch_Rear (0, hy, hz): front plate 0.125-0.175
    ahead of the pin (+Z), bottom/top jaws back to z_end, vertical pin; support_top = y up to which the front plate rises
    (it joins the chassis above)"""
    yt = support_top if support_top is not None else hy + 0.095
    tbox(P, 'fork_front', -x, x, hy - 0.145, yt, hz + 0.125, hz + 0.175, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_bottom', -x, x, hy - 0.15, hy - 0.09, z_end, hz + 0.13, 0, METAL, METAL, METAL_D)
    tbox(P, 'fork_top', -x, x, hy + 0.09, hy + 0.15, z_end, hz + 0.13, 0, METAL, METAL, METAL_D)
    rod(P, 'fork_pin', (0, hy - 0.17, hz), (0, hy + 0.17, hz), 0.03, METAL_D, METAL_D)


# ---------------- scene / objects ----------------
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


def unity_of(ob):
    t = ob.matrix_world.translation; return [round(-t.x, 4), round(t.z, 4), round(-t.y, 4)]


def fingerprint(obs):
    out = {}
    for k, o in obs.items():
        vs = sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in o.data.vertices)
        out[k] = (len(o.data.vertices), len(o.data.polygons), round(sum(a + 2 * b + 3 * c for a, b, c in vs), 4), round(sum(a * a + b * b + c * c for a, b, c in vs), 4))
    print('FINGERPRINT', out)
    return out


def clearance(obs, wheel_names, body_names):
    for wn in wheel_names:
        wo = obs[wn]; wb = bvh_world(wo); wc = wo.matrix_world.translation
        R = max(wo.dimensions[1], wo.dimensions[2]) / 2
        for bn in body_names:
            if bn not in obs: continue
            bb = bvh_world(obs[bn])
            dmin = min((bb.find_nearest(wo.matrix_world @ v.co)[3] for v in wo.data.vertices
                        if (wo.matrix_world @ v.co - wc).length > R * 0.72), default=None)
            print(f'  {wn} x {bn}: overlap pairs {len(bb.overlap(wb))} (axle/hub only expected) | min tyre->{bn} {dmin:.3f} m')


def pair_overlaps(obs, pairs):
    for a, b in pairs:
        if a in obs and b in obs:
            print(f'  overlap {a} x {b}: {len(bvh_world(obs[a]).overlap(bvh_world(obs[b])))} face pairs')


SHIFT = V(0, 0, 0)


def build():
    global SHIFT
    name = PREFIX + ASSET
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{ATLAS}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{ATLAS}', img)
    parts = make_parts()                       # [(Part, pivot (design), parent part name or None)]
    pts = [v.co for P, _, _ in parts for v in P.bm.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    SHIFT = V(round((lo[0] + hi[0]) / 2, 4) if CENTER_X else 0.0, 0, round((lo[2] + hi[2]) / 2, 4))
    print(f'DESIGN bbox x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f} -> shift {tuple(-SHIFT)}')
    for P, _, _ in parts:
        for v in P.bm.verts: v.co = to_blender(v.co - SHIFT)
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 0.5
    obs = {}
    for P, piv, parent in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, to_blender(V(*piv) - SHIFT), root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    sc.view_layers[0].update()
    for P, piv, parent in parts:
        if parent:
            ob = obs[P.name]; mw = ob.matrix_world.copy(); ob.parent = obs[parent]; ob.matrix_world = mw
    sc.view_layers[0].update()
    for nm, pos, parent, roty in POINTS:
        e = bpy.data.objects.new(nm, None); coll.objects.link(e)
        e.empty_display_type = 'ARROWS'; e.empty_display_size = 0.25
        e.parent = obs[parent] if parent else root
        sc.view_layers[0].update()
        e.matrix_world = Matrix.Translation(to_blender(V(*pos) - SHIFT)) @ Matrix.Rotation(math.radians(roty), 4, 'Z')
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values():
        n_, smp = pc.coplanar_overlaps(o)
        for a_, b_ in smp[:4]:
            pa = o.matrix_world @ o.data.polygons[a_].center; pb = o.matrix_world @ o.data.polygons[b_].center
            print(f'    coplanar sample (Unity) {[round(-pa.x, 3), round(pa.z, 3), round(-pa.y, 3)]} / {[round(-pb.x, 3), round(pb.z, 3), round(-pb.y, 3)]}')
    for o in obs.values():
        for pg in o.data.polygons:
            if pg.area < 1e-7:
                c_ = o.matrix_world @ pg.center; print(f'    degenerate face in {o.name} at (Unity) {[round(-c_.x, 3), round(c_.z, 3), round(-c_.y, 3)]}')
    print(f'  budget {BUDGET} -> {"OK" if tot <= BUDGET else "OVER"} ({tot} tris, {100 * tot / BUDGET:.0f} %)')
    for nm, _, _, _ in POINTS:
        e = next(o for o in coll.objects if o.name.split('.')[0] == nm)
        print(f'  point {nm} (Unity) {unity_of(e)} parent {e.parent.name} rotZ(blender) {round(math.degrees(e.matrix_world.to_euler().z), 2)}')
    for nm, o in obs.items():
        print(f'  pivot {nm} (Unity) {unity_of(o)} parent {o.parent.name} rot {tuple(o.rotation_euler)}')
    item_checks(sc, coll, obs)
    return name, sc, coll, root, img, mat, obs


# ---------------- mating (temporary partner copies) ----------------
def load_partner(sc, cname):
    blend = os.path.join(BLEND_DIR, cname + '.blend')
    st = dict(c=set(bpy.data.collections), m=set(bpy.data.materials), i=set(bpy.data.images), o=set(bpy.data.objects))
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == cname]
    pcoll = dst.collections[0]; sc.collection.children.link(pcoll)
    sc.view_layers[0].update()
    return dict(coll=pcoll, st=st, name=cname)


def pobj(coll, nm):
    return next(o for o in coll.all_objects if o.name.split('.')[0] == nm)


def proot(p):
    return next(o for o in p['coll'].objects if o.type == 'EMPTY' and o.parent is None)


def align(sc, p, theirs, target):
    """move partner root so its point `theirs` (None = root) coincides (position + rotation) with object `target`"""
    r = proot(p); pt = r if theirs is None else pobj(p['coll'], theirs)
    loc = r.matrix_world.inverted() @ pt.matrix_world
    r.matrix_world = target.matrix_world @ loc.inverted()
    sc.view_layers[0].update()
    d = (pt.matrix_world.translation - target.matrix_world.translation).length
    rd = (pt.matrix_world.to_quaternion().rotation_difference(target.matrix_world.to_quaternion())).angle
    print(f'MATE {p["name"]}.{theirs or "root"} -> {target.name}: position error {d:.6f} m, rotation error {math.degrees(rd):.4f} deg')
    return d


def meshes(coll):
    return [o for o in coll.all_objects if o.type == 'MESH' and not o.name.split('.')[0].endswith('_Low1')]


def overlaps(la, lb, label, skip=()):
    total = 0; dmin = 1e9
    for a in la:
        ba = bvh_world(a)
        for b in lb:
            if (a.name.split('.')[0], b.name.split('.')[0]) in skip: continue
            pr = ba.overlap(bvh_world(b)); n = len(pr); total += n
            if n:
                c_ = a.matrix_world @ a.data.polygons[pr[0][0]].center
                print(f'  MATE overlap {a.name} x {b.name}: {n} face pairs, e.g. at (Unity) {[round(-c_.x, 3), round(c_.z, 3), round(-c_.y, 3)]}')
    for b in lb:
        bb = bvh_world(b)
        dmin = min(dmin, min(bb.find_nearest(a.matrix_world @ v.co)[3] for a in la for v in a.data.vertices))
    print(f'MATE {label}: total overlapping face pairs {total}, min vertex->surface distance {dmin * 1000:.1f} mm')
    return total


def point_dist(a, b, label):
    d = (a.matrix_world.translation - b.matrix_world.translation).length
    print(f'  MATE {label}: {a.name} <-> {b.name} distance {d:.4f} m')
    return d


def remove_partner(p):
    pcoll, st = p['coll'], p['st']
    for o in list(pcoll.all_objects):
        dd = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(dd, bpy.types.Mesh) and dd.users == 0: bpy.data.meshes.remove(dd)
    for c in set(bpy.data.collections) - st['c']: bpy.data.collections.remove(c)
    for m in set(bpy.data.materials) - st['m']:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in set(bpy.data.images) - st['i']:
        if i.users == 0: bpy.data.images.remove(i)
    print('MATE temp copy removed:', p['name'], '| leftover new objects', [o.name for o in set(bpy.data.objects) - st['o']])


# ---------------- renders ----------------
def render(sc, coll, out, view_dir=None, fill_w=0.70, res=(1280, 800), lens=50, bg=(0xc7, 0xcc, 0xd3), extra=(), focus=None, frad=1.3):
    from bpy_extras.object_utils import world_to_camera_view
    view_dir = view_dir or REF_VIEW
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
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.name.endswith(('_Low1', '_LOD1')) and not o.hide_render]
    for ex in extra: objs += [o for o in ex.all_objects if o.type == 'MESH' and not o.name.split('.')[0].endswith('_Low1')]
    hidden = [o for o in sc.objects if o.type == 'MESH' and o not in objs]
    for o in hidden: o.hide_render = True
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    if focus is not None:
        fc = focus.matrix_world.translation; pts = [p for p in pts if (p - fc).length < frad]
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
    for o in hidden: o.hide_render = False
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


def main():
    name, sc, coll, root, img, mat, obs = build()
    fingerprint(obs)
    os.makedirs(CHECK_DIR, exist_ok=True)
    if MODE == 'build':
        for tag, view in CHECK_VIEWS:
            render(sc, coll, os.path.join(CHECK_DIR, f'{ITEM_ID}_check_{tag}.png'), view, 0.80, (960, 600))
        if os.environ.get('PACK_NO_MATES') != '1':
            item_mates(sc, coll, obs)
    elif MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = os.path.join(ART, 'Meshes', name + '.fbx')
        with_scene(sc, globals().get('EXPORT_FN') or pc.export, name, coll, root, fbx)
        pc.save_lib(os.path.join(ART, 'Blend', name + '.blend'), coll, mat, img)
        hid = [o for o in coll.objects if o.name.split('.')[0] in globals().get('PREVIEW_HIDE', ())]
        for o in hid: o.hide_render = True                       # preview shows the reference state (e.g. Empty variant)
        render(sc, coll, os.path.join(ART, 'Previews', name + '_Preview.png'), REF_VIEW, 0.75, (1280, 800))
        for o in hid: o.hide_render = False
        if bpy.context.window:
            with_scene(sc, pc.verify, fbx)
        else:
            verify_headless(fbx, sc)


# ================= item =================
HF = (0.55, 2.15)                # Hitch_Front = shared eye centre (spec)
PTO_F = (0.70, 2.30)             # PTO_Front = Hitch_Front + (0, 0.15, 0.15) (CATALOG item 6)
BALE_OUT = (0.90, -2.15)
CH = dict(y=1.45, z=-0.90, r=0.90, x=0.82, e=0.06)   # chamber: axis X at (y, z), vertex radius r, side plates at +-x
TG_PIV = (2.35, -0.90)           # Tailgate hinge axis X (y, z) at the top of the chamber
PU_PIV = (0.55, 0.10)            # Pickup hinge axis X (y, z)
PU_C, PU_R, PU_TIP = (0.48, 0.90), 0.20, 0.33    # pickup drum centre (y, z), drum radius, tine tip radius
WHEEL = dict(d=1.00, w=0.50, x=1.10, y=0.50, z=-0.70, lugs=14)
REF_VIEW = (0.70, -0.70, 0.50)   # Blender dir target->camera: front-left 3/4, ~30 deg up (reference)
CHECK_VIEWS = [('ref', REF_VIEW), ('rear', (-0.6, 0.8, 0.45)), ('side', (1.0, 0.0, 0.05)), ('top', (0.001, -0.02, 1.0))]


def arc_pts(a0, a1, r, n=8, dz=0.0):
    """points of the 16-gon (vertex at the top) between angles a0..a1 (deg) in the (z, y) plane around the chamber axis"""
    cy, cz = CH['y'], CH['z']
    return [(cz + dz + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def half_drum(P, tag, a0, a1, dz):
    """half chamber: loft along X of a half 16-gon closed by the vertical chord, chamfered side edges (dark rim)"""
    R, x, e = CH['r'], CH['x'], CH['e']
    full = arc_pts(a0, a1, R, dz=dz); inner = arc_pts(a0, a1, R - e, dz=dz)
    rings = [[V(xx, y, z) for z, y in prof] for xx, prof in ((-x, inner), (-x + e, full), (x - e, full), (x, inner))]
    up = lambda k: (full[k][1] + full[(k + 1) % len(full)][1]) / 2 > CH['y'] - 0.05
    P.loft(f'{tag}_drum', rings, lambda j, k: (RED if up(k) else RED_D) if j == 1 and k < 8 else RED_D, RED, RED)
    # three grey bands around this half (5 mm off the facets, no coplanar faces)
    for i, xb in enumerate((-0.45, 0.0, 0.45)):
        pts = [V(xb, y, z) for z, y in arc_pts(a0, a1, R + 0.01, dz=dz)]
        path_sweep(P, f'{tag}_band{i}', pts, (1, 0, 0), [(-0.015, -0.04), (0.015, -0.04), (0.015, 0.04), (-0.015, 0.04)], METAL, METAL)


def body_part():
    P = Part('Body')
    cy, cz = CH['y'], CH['z']
    half_drum(P, 'front', -90, 90, 0.0)
    # hinge shaft on the top with knuckles
    rod(P, 'hinge_shaft', (-0.90, TG_PIV[0] + 0.02, TG_PIV[1]), (0.90, TG_PIV[0] + 0.02, TG_PIV[1]), 0.05, METAL, METAL_D)
    for x in (-0.86, 0.0, 0.86):
        tbox(P, f'knuckle{x}', x - 0.05, x + 0.05, TG_PIV[0] - 0.04, TG_PIV[0] + 0.10, TG_PIV[1] + 0.005, TG_PIV[1] + 0.12, 0.02, METAL, METAL, METAL_D)
    for s in (-1, 1):
        xbox(P, f'ram_boss{s}', s * 0.81, s * 0.90, 2.12, 2.26, -0.74, -0.62, METAL, METAL, METAL_D)
    # drive cover box on the chamber front
    tbox(P, 'drive_box', -0.45, 0.45, 1.15, 1.62, -0.25, 0.30, 0.05, RED, RED_D, RED_D)
    # chassis: two beams under the chamber, front cross member, axle with stub hubs
    for s in (-1, 1):
        xbox(P, f'beam{s}', s * 0.52, s * 0.68, 0.45, 0.60, -1.70, 0.34, METAL, METAL, METAL_D)
    tbox(P, 'front_cross', -0.67, 0.67, 0.45, 0.60, 0.22, 0.33, 0, METAL, METAL, METAL_D)
    rod(P, 'axle', (-1.06, WHEEL['y'], WHEEL['z']), (1.06, WHEEL['y'], WHEEL['z']), 0.06, METAL_D, METAL_D)
    for s in (-1, 1):
        xbox(P, f'axle_hanger{s}', s * 0.51, s * 0.69, 0.44, 0.61, WHEEL['z'] - 0.08, WHEEL['z'] + 0.08, METAL_D, METAL, METAL_D)
        # red fender over the wheel, joined to the side plate
        arch(P, f'fender{s}', WHEEL['z'], WHEEL['y'], 0.60, 0.06, s * 0.83, s * 1.36, (20, 60, 100, 140, 160))
        xbox(P, f'fender_bracket{s}', s * 0.80, s * 0.86, 0.95, 1.10, -0.40, -0.25, RED_D, RED_D, RED_D)
    # rear bale ramp on the chassis ends (Bale_Out above it)
    for s in (-1, 1):
        beam(P, f'ramp{s}', V(s * 0.60, 0.50, -1.66), V(s * 0.60, 0.22, -2.20), 0.10, 0.08, METAL, ref=(1, 0, 0))
    tbox(P, 'ramp_bar', -0.66, 0.66, 0.18, 0.27, -2.2609, -2.17, 0, METAL, METAL, METAL_D)
    # red A-drawbar: from the chamber front at mid height forward, then down to the grey tip + shared eye
    hy, hz = HF
    for s in (-1, 1):
        path_sweep(P, f'drawbar{s}', [V(s * 0.62, 1.05, -0.15), V(s * 0.42, 1.02, 1.30), V(s * 0.07, hy + 0.01, hz - 0.28)],
                   (0, 1, 0), [(-0.06, -0.06), (0.06, -0.06), (0.06, 0.06), (-0.06, 0.06)], lambda j, k: RED if k == 2 else RED_D, RED_D)
    tbox(P, 'drawbar_tip', -0.07, 0.07, hy - 0.06, hy + 0.06, hz - 0.34, hz - 0.10, 0.015, METAL, METAL, METAL_D)
    drawbar_eye(P, 'eye', 0, hy, hz)
    rod(P, 'pto_stub', (0, PTO_F[0] - 0.06, hz - 0.42), (0, PTO_F[0] - 0.06, hz - 0.30), 0.06, METAL_D, METAL_D)
    # support stand (jack) under the drawbar near the eye
    rod(P, 'stand', (0.0, 0.045, hz - 0.55), (0.0, hy - 0.02, hz - 0.55), 0.04, METAL, METAL_D)
    tbox(P, 'stand_foot', -0.09, 0.09, 0.0, 0.05, hz - 0.64, hz - 0.46, 0, METAL, METAL, METAL_D)
    return P


def tailgate_part():
    P = Part('Tailgate')
    half_drum(P, 'rear', 90, 270, -0.004)
    # orange stripes on both side plates, hydraulic rams from the front-half bosses to the tailgate sides
    for s in (-1, 1):
        x0, x1 = sorted((s * (CH['x'] - 0.001), s * (CH['x'] + 0.008)))
        for i, st in enumerate(([(-1.55, 1.30), (-1.68, 1.45), (-1.30, 2.05), (-1.17, 1.90)],
                                [(-1.40, 0.85), (-1.55, 1.00), (-1.15, 1.62), (-1.02, 1.47)])):
            prism_x(P, f'stripe{s}{i}', x0, x1, st, SIGNAL, SIGNAL, SIGNAL)
        xbox(P, f'ram_foot{s}', s * (CH['x'] - 0.01), s * 0.90, 1.22, 1.36, -1.48, -1.36, METAL, METAL, METAL_D)
        sweep(P, f'ram{s}', V(s * 0.86, 1.30, -1.42), V(s * 0.86, 2.19, -0.70), ngon(0.04, 8, math.pi / 8),
              [(0, 1, 0), (0.55, 1, 0), (0.56, 0.7, 0), (1, 0.7, 0)], METAL, METAL_D, METAL_D, ref=(1, 0, 0))
    return P


def pickup_part():
    P = Part('Pickup')
    py, pz = PU_PIV; cy, cz = PU_C
    rod(P, 'hinge', (-0.835, py, pz), (0.835, py, pz), 0.04, METAL_D, METAL_D)
    for s in (-1, 1):
        beam(P, f'arm{s}', V(s * 0.79, py, pz), V(s * 0.79, cy, cz), 0.06, 0.10, METAL_D, ref=(1, 0, 0))
    rod(P, 'drum', (-0.755, cy, cz), (0.755, cy, cz), PU_R, METAL, METAL_D, seg=12)
    # 8 tine rows x 6 tines (chunky 0.05 bars standing out of the drum)
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        u = V(0, math.sin(a), math.cos(a))
        for i in range(6):
            x = -0.625 + 0.25 * i
            sweep(P, f'tine{k}_{i}', V(x, cy, cz) + u * (PU_R - 0.02), V(x, cy, cz) + u * PU_TIP,
                  [(0.025, 0.025), (-0.025, 0.025), (-0.025, -0.025), (0.025, -0.025)], [(0, 1, 0), (1, 1, 0)],
                  METAL, METAL, METAL, ref=(1, 0, 0))
    # red guard hood above the tines with side shields, grey guard bar in front
    guard = [(0.20, 0.82), (0.72, 0.88), (0.92, 0.85), (0.92, 0.80), (0.72, 0.83), (0.20, 0.77)]   # rear half only: tines show in front
    prism_x(P, 'guard', -0.805, 0.805, guard, lambda k: RED if k in (0, 1) else RED_D, RED_D, RED_D)
    for s in (-1, 1):
        xa, xb = sorted((s * 0.80, s * 0.86))
        prism_x(P, f'shield{s}', xa, xb, [(0.30, 0.40), (1.00, 0.30), (1.30, 0.50), (1.26, 0.60), (0.95, 0.84), (0.30, 0.83)], RED_D, RED, RED)
    rod(P, 'guard_bar', (-0.84, 0.52, 1.24), (0.84, 0.52, 1.24), 0.03, METAL_D, METAL_D)
    return P


def wheel_parts():
    out = []
    for nm, s in (('Wheel_L', -1), ('Wheel_R', 1)):
        P = Part(nm); c = (s * WHEEL['x'], WHEEL['y'], WHEEL['z'])
        wheel(P, c, WHEEL['d'], WHEEL['w'], WHEEL['lugs'], outer=s)
        out.append((P, c, None))
    return out


def make_parts():
    return [(body_part(), (0, 0, 0), None), (tailgate_part(), (0,) + TG_PIV, None), (pickup_part(), (0,) + PU_PIV, None)] + wheel_parts()


POINTS = [('Hitch_Front', (0, HF[0], HF[1]), None, 0), ('PTO_Front', (0, PTO_F[0], PTO_F[1]), None, 0),
          ('Bale_Out', (0, BALE_OUT[0], BALE_OUT[1]), None, 0)]


def item_checks(sc, coll, obs):
    clearance(obs, ('Wheel_L', 'Wheel_R'), ('Body', 'Tailgate', 'Pickup'))
    pair_overlaps(obs, [('Tailgate', 'Body'), ('Pickup', 'Body'), ('Pickup', 'Tailgate')])
    tg, bd = obs['Tailgate'], obs['Body']
    seen = set()
    for a_, b_ in bvh_world(tg).overlap(bvh_world(bd)):
        c_ = tg.matrix_world @ tg.data.polygons[a_].center; key = (round(-c_.x, 1), round(c_.z, 1), round(-c_.y, 1))
        if key not in seen: seen.add(key)
    print('  Tailgate x Body overlap locations (Unity, 0.1 m grid):', sorted(seen)[:20])
    tg = obs['Tailgate']
    for sgn in (1, -1):                                 # Open pose: rear lower edge swings up and back
        tg.rotation_euler = (sgn * math.radians(80), 0, 0); sc.view_layers[0].update()
        zmin = min((tg.matrix_world @ v.co).z for v in tg.data.vertices)
        if zmin > 0.8: break
    print(f'  OPEN Tailgate 80 deg (blender rot X {math.degrees(tg.rotation_euler.x):+.0f}): lowest {zmin:.2f} m, overlaps Body '
          f'{len(bvh_world(tg).overlap(bvh_world(obs["Body"])))}, wheels {sum(len(bvh_world(tg).overlap(bvh_world(obs[w]))) for w in ("Wheel_L", "Wheel_R"))}')
    if MODE == 'build':
        render(sc, coll, os.path.join(CHECK_DIR, 'HRV-02_check_open.png'), (0.75, 0.62, 0.40), 0.80, (960, 600))
    tg.rotation_euler = (0, 0, 0); sc.view_layers[0].update()


def item_mates(sc, coll, obs):
    me_f = pobj(coll, 'Hitch_Front'); me_p = pobj(coll, 'PTO_Front')
    for cname, tag in (('FMS_Mach_Tractor_Cab', 'TRC-01'), ('FMS_Mach_Tractor_Large', 'TRC-02')):
        p = load_partner(sc, cname)
        align(sc, p, 'Hitch_Rear', me_f)
        point_dist(me_p, pobj(p['coll'], 'PTO_Rear'), f'PTO_Front <-> {tag} PTO_Rear')
        overlaps(list(obs.values()), meshes(p['coll']), f'HRV-02 Hitch_Front on {tag} Hitch_Rear')
        if tag == 'TRC-01':
            render(sc, coll, os.path.join(CHECK_DIR, f'HRV-02_mate_{tag}.png'), (0.80, 0.55, 0.45), 0.85, (960, 600), extra=[p['coll']])
            render(sc, coll, os.path.join(CHECK_DIR, f'HRV-02_mate_{tag}_close.png'), (0.9, 0.3, 0.35), 0.85, (960, 600), extra=[p['coll']], focus=me_f, frad=0.7)
        remove_partner(p)


main()
