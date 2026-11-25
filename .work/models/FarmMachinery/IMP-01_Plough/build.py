# IMP-01 Plough (FMS_Mach_Plough) - FarmMachinery pack, stage E7. Procedural, idempotent.
# Headless:
#   set PYTHONUTF8=1
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build.py -- IMP-01 build|export
#   build  = build + printed checks + check renders to %TEMP%/farmmachinery_check/IMP-01/
#   export = build + FBX + collection-only .blend + ONE preview + FBX re-import verify (then run make_lod1.py separately)
# Live Blender (MCP): exec(compile(open(p).read(), p, 'exec'), {'__name__': '__main__', 'BUILD_ARGS': ['IMP-01', 'build']})
#   Live builds go to an own scene 'IMP-01_Plough_Build' / collection 'IMP-01_Plough'; nothing else is touched.
# Geometry is written in UNITY coordinates (x right, y up, z forward = hitch end) and mapped to Blender at the end:
#   Blender = (-x, -z, y)  ->  after the FBX export (-Z forward, Y up, baked) Unity sees exactly the design coordinates.
import bpy, bmesh, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------- CONFIG ----------------
REPO = r"C:\Users\Sergv\orca\workspaces\Assets_Farm\master-2"
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'FarmMachinery')
PREFIX, TEX_TAG = 'FMS_Mach_', 'FarmMachinery'
CHECK_DIR = os.environ.get('PACK_CHECK') or os.path.join(os.environ.get('TEMP', '.'), 'farmmachinery_check', 'IMP-01')
SCENE, OUTER = 'IMP-01_Plough_Build', 'IMP-01_Plough'
# ----------------------------------------
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import pack_common as pc
from pack_shapes import *          # Part, sweep, path_sweep, fill, tube, oct_rod, chamf_rect, ngon, palette slots

_a = globals().get('BUILD_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = _a[0] if _a else 'IMP-01'
MODE = _a[1] if len(_a) > 1 else 'build'

# FarmMachinery palette (STYLE.md): cells 0-9 standard, 10-15 machinery colours
PAL_FM = list(PAL)
PAL_FM[10:16] = ['#2B2D31', '#474B51', '#7FA3B5', '#F4E3A1', '#E8913A', '#D8B65A']
TYRE, RUBBER, GLASS, LAMP, SIGNAL, GRAIN = range(10, 16)

# ---------------- design numbers (Unity coordinates, metres) ----------------
LUG_X, LUG_Y, LUG_Z = 0.45, 0.60, 1.70        # lower hitch lug pin axes: X +-0.45, Y 0.60 (CATALOG item 6); Z = lug centre
# Coordinator decision 2026-11-24 (option B): ONE straight beam like the reference, from inside the left mast leg foot
# to the spec rear end; bodies on the beam line at the spec Z (stagger 0.22 m/body instead of the spec 0.35)
BEAM_A, BEAM_B = (-0.47, 1.58), (0.55, -1.65)  # main beam centreline in plan (x, z)
BEAM_Y = 0.57                                  # beam centre height (Y 0.50-0.64)
BODY_Z = (0.75, 0.05, -0.65, -1.35)            # plough bodies, spec Z; X = beam centreline at that Z (legs hang from the beam)
MB_OUT = 0.2647                                # mouldboard rear-top wing, local x (keeps the root bbox symmetric in X)
WHEEL_C, WHEEL_D, WHEEL_W, WHEEL_LUGS = (-0.62, 0.30, -1.55), 0.60, 0.20, 12
ARM_Z, ARM_Y0, ARM_Y1 = -1.55, 0.635, 0.74     # gauge wheel cross-arm (5 mm sunk into the beam top, no coplanar faces)
LEG_FOOT, LEG_TOP = (0.45, 0.50, 1.60), (0.07, 1.19, 1.46)   # A-frame leg axis (right leg; left mirrored)
BRACKET = (1.30, 1.45)                         # top-link pin (y, z), pin axis X


def V(x, y, z): return Vector((x, y, z))
def to_blender(v): return Vector((-v[0], -v[2], v[1]))
def beam_x(z): return BEAM_A[0] + (BEAM_B[0] - BEAM_A[0]) * (BEAM_A[1] - z) / (BEAM_A[1] - BEAM_B[1])


# ---------------- shared pack wheel (same function in every FarmMachinery model) ----------------
def wheel(P, centre, d, w, lugs, outer=-1, n=16):
    """tyre n segments near-black (slot 10) with `lugs` blocky lugs standing proud by 8 % of D, cream dished rim (3) with
    dark-cream inner face (4) and a 10-segment hub. Spin axis X; outer face at centre.x + outer * w / 2. Lowest lug face
    is centred at the bottom, so the wheel rests on y = centre.y - d / 2."""
    c = Vector(centre); R = d / 2; h = w / 2; o = outer; Rc = R - 0.08 * d
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
def plate_x(P, cname, x0, x1, cy, cz, wy, wz, ch, hole_r, s_face, s_side, s_bore, hn=8):
    """plate / block with flat faces normal to X, chamfered (y, z) outline and a through pin hole along X"""
    bm = P.bm
    out = [(cy + a, cz + b) for a, b in chamf_rect(wy, wz, ch)]
    hole = [(cy + hole_r * math.cos(math.pi / hn + 2 * math.pi * i / hn), cz + hole_r * math.sin(math.pi / hn + 2 * math.pi * i / hn)) for i in range(hn)]
    o0 = [bm.verts.new((x0, y, z)) for y, z in out]; o1 = [bm.verts.new((x1, y, z)) for y, z in out]
    h0 = [bm.verts.new((x0, y, z)) for y, z in hole]; h1 = [bm.verts.new((x1, y, z)) for y, z in hole]
    faces = fill(P, [o0, h0], s_face, (1, 0, 0)) + fill(P, [o1, h1], s_face, (1, 0, 0))
    faces += tube(P, o0, o1, s_side) + tube(P, h0, h1, s_bore)
    P.comp.append((cname, faces, False))


def tri2(P, a, b, c, d, slot):
    return [P.face([a, b, c], slot), P.face([a, c, d], slot)]


def plough_body(P, i, x, z):
    """one bottom: leg, beam clamp, 3-facet twisted mouldboard (0.04 plate), share wedge with a dark cutting-edge strip"""
    d = (V(BEAM_B[0], 0, BEAM_B[1]) - V(BEAM_A[0], 0, BEAM_A[1])).normalized(); perp = V(-d.z, 0, d.x)
    cc = V(x, BEAM_Y, z)
    sweep(P, f'clamp{i}', cc - d * 0.08, cc + d * 0.08, chamf_rect(0.20, 0.24, 0.03), [(0, 1, 0), (1, 1, 0)],
          METAL, METAL, METAL, ref=tuple(perp))
    sweep(P, f'leg{i}', V(x, 0.10, z), V(x, BEAM_Y, z), chamf_rect(0.10, 0.10, 0.015), [(0, 1, 0), (1, 1, 0)],
          METAL, METAL_D, METAL_D, ref=(0, 0, 1))
    # mouldboard: 4 ribs (front -> rear) x 3 rows (bottom, mid, top); vertical at the front, leaning outward at the rear
    # (reference: the board starts right under the clamp, tall and long; concave working face = mid row held back)
    # silhouette leans back like the reference: low front edge rising from the share, lifted rear edge, high rear wing
    ribs = [(0.20, [(-0.060, 0.05), (-0.062, 0.15), (-0.064, 0.26)]),
            (0.00, [(0.010, 0.06), (0.014, 0.26), (0.040, 0.45)]),
            (-0.24, [(0.085, 0.10), (0.110, 0.31), (0.185, 0.50)]),
            (-0.48, [(0.150, 0.20), (0.190, 0.36), (MB_OUT, 0.52)])]
    G = [[V(x + lx, ly, z + lz) for lx, ly in pts] for lz, pts in ribs]
    def nrm(a, b):
        tz = G[min(a + 1, 3)][b] - G[max(a - 1, 0)][b]; ty = G[a][min(b + 1, 2)] - G[a][max(b - 1, 0)]
        return tz.cross(ty).normalized()
    bm = P.bm
    F = [[bm.verts.new(G[a][b]) for b in range(3)] for a in range(4)]
    B = [[bm.verts.new(G[a][b] - nrm(a, b) * 0.04) for b in range(3)] for a in range(4)]
    fs = []
    for a in range(3):
        for b in range(2):
            fs += tri2(P, F[a][b], F[a + 1][b], F[a + 1][b + 1], F[a][b + 1], METAL)
            fs += tri2(P, B[a][b + 1], B[a + 1][b + 1], B[a + 1][b], B[a][b], METAL)
    loop = [(a, 0) for a in range(4)] + [(3, 1), (3, 2)] + [(a, 2) for a in (2, 1, 0)] + [(0, 1)]
    for m in range(len(loop)):
        (a0, b0), (a1, b1) = loop[m], loop[(m + 1) % len(loop)]
        s = METAL if (b0 == 2 and b1 == 2) else METAL_D
        fs += tri2(P, F[a0][b0], B[a0][b0], B[a1][b1], F[a1][b1], s)
    P.comp.append((f'mouldboard{i}', fs, False))
    # share: wedge on the ground, tip forward; bevelled front edge = cutting edge strip (slot 8)
    bot = [V(x - 0.07, 0, z + 0.38), V(x + 0.23, 0, z - 0.02), V(x - 0.07, 0, z - 0.02)]
    top = [V(x - 0.062, 0.08, z + 0.27), V(x + 0.15, 0.08, z - 0.012), V(x - 0.062, 0.08, z - 0.012)]
    P.loft(f'share{i}', [bot, top], lambda j, k: (METAL_D, METAL_D, METAL)[k], METAL_D, METAL, ground=True)


def frame_part():
    P = Part('Frame')
    # main beam, straight, front end inside the left mast leg foot; top red, sides grey, bottom dark
    # section split at mid-height: reference shows red top and red upper half of the sides, grey lower half
    a, c = 0.07, 0.04
    sec = [(a - c, -a), (a, -a + c), (a, 0.0), (a, a - c), (a - c, a), (-a + c, a), (-a, a - c), (-a, 0.0), (-a, -a + c), (-a + c, -a)]
    bslot = {2: RED_D, 3: RED, 4: RED, 5: RED, 6: RED_D, 9: METAL_D}
    path_sweep(P, 'beam', [V(BEAM_A[0], BEAM_Y, BEAM_A[1]), V(BEAM_B[0], BEAM_Y, BEAM_B[1])],
               (0, 1, 0), sec, lambda j, k: bslot.get(k, METAL), METAL_D)
    for i, z in enumerate(BODY_Z):
        plough_body(P, i + 1, beam_x(z), z)
    # A-frame mast: two red legs (front/back faces bright, sides dark), cross bar at Y 0.80, grey top-link bracket
    fx, fy, fz = LEG_FOOT; tx, ty, tz = LEG_TOP
    for s in (-1, 1):
        sweep(P, f'mast_leg{"LR"[s > 0]}', V(s * fx, fy, fz), V(s * tx, ty, tz), chamf_rect(0.12, 0.12, 0.02),
              [(0, 1, 0), (1, 1, 0)], lambda j, k: RED if k in (1, 5) else RED_D, RED_D, RED_D, ref=(0, 0, 1))
    t = (0.80 - fy) / (ty - fy); xc = fx + (tx - fx) * t; zc = fz + (tz - fz) * t
    sweep(P, 'mast_cross', V(-(xc + 0.015), 0.80, zc), V(xc + 0.015, 0.80, zc), chamf_rect(0.10, 0.10, 0.02),
          [(0, 1, 0), (1, 1, 0)], lambda j, k: RED if k in (1, 7) else RED_D, RED_D, RED_D, ref=(0, 0, 1))
    plate_x(P, 'top_bracket', -0.12, 0.12, BRACKET[0], BRACKET[1], 0.20, 0.14, 0.03, 0.035, METAL, METAL, METAL_D)
    for s in (-1, 1):
        plate_x(P, f'lug{"LR"[s > 0]}', s * LUG_X - 0.04, s * LUG_X + 0.04, LUG_Y, LUG_Z, 0.22, 0.14, 0.03, 0.035, METAL, METAL, METAL_D)
    # gauge wheel stub: cross-arm on the beam top, vertical plate inboard of the wheel, axle into the wheel hub
    wx, wy, wz = WHEEL_C
    sweep(P, 'arm', V(-0.47, (ARM_Y0 + ARM_Y1) / 2, ARM_Z), V(0.60, (ARM_Y0 + ARM_Y1) / 2, ARM_Z),
          chamf_rect(0.10, ARM_Y1 - ARM_Y0, 0.015), [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(0, 0, 1))
    sweep(P, 'arm_plate', V(-0.45, 0.22, ARM_Z), V(-0.45, 0.72, ARM_Z), chamf_rect(0.10, 0.16, 0.015),
          [(0, 1, 0), (1, 1, 0)], METAL, METAL_D, METAL_D, ref=(1, 0, 0))
    oct_rod(P, 'axle', V(-0.42, wy, wz), V(wx + 0.02, wy, wz), [(0, 0.035), (1, 0.035)], METAL_D, METAL_D, ref=(0, 1, 0))
    return P


def wheel_part():
    P = Part('Wheel_Gauge')
    wheel(P, WHEEL_C, WHEEL_D, WHEEL_W, WHEEL_LUGS, outer=-1)
    return P


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


def build():
    name = PREFIX + 'Plough'; tag = TEX_TAG + '_Red'          # shared pack atlas (orchestrator 2026-11-24)
    sc = build_scene(); coll = own_collections(sc, name)
    os.makedirs(os.path.join(ART, 'Textures'), exist_ok=True)
    tex = f'T_{tag}_BaseColor.png'
    img = pc.atlas_image(tex, os.path.join(ART, 'Textures', tex), PAL_FM); mat = pc.material(f'M_{tag}', img)
    parts = [frame_part(), wheel_part()]
    # root: ground, centre of the bbox in X and Z (Z shifted; X is symmetric by design, Link3P_Front stays at X = 0)
    pts = [v.co for P in parts for v in P.bm.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    zoff = (lo[2] + hi[2]) / 2
    print(f'DESIGN bbox x {lo[0]:.4f}..{hi[0]:.4f} (centre {(lo[0] + hi[0]) / 2:+.4f}) y {lo[1]:.4f}..{hi[1]:.4f} '
          f'z {lo[2]:.4f}..{hi[2]:.4f} -> z shift {-zoff:+.4f}')
    for P in parts:
        for v in P.bm.verts: v.co = to_blender(v.co - V(0, 0, zoff))
    root = bpy.data.objects.new(name, None); coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'; root.empty_display_size = 0.3
    piv = {'Frame': Vector((0, 0, 0)), 'Wheel_Gauge': to_blender(V(*WHEEL_C) - V(0, 0, zoff))}
    obs = {}
    for P in parts:
        nm = P.name; ob = pc.to_object(P, '', coll, mat, piv[nm], root)
        ob.name = nm; ob.data.name = nm; obs[nm] = ob
    link = bpy.data.objects.new('Link3P_Front', None); coll.objects.link(link)
    link.empty_display_type = 'ARROWS'; link.empty_display_size = 0.25
    link.parent = root; link.location = to_blender(V(0, LUG_Y, LUG_Z - zoff))
    sc.view_layers[0].update()
    tot = pc.report(obs)
    for o in obs.values(): pc.coplanar_overlaps(o)
    print(f'  budget 2500 -> {"OK" if tot <= 2500 else "OVER"} ({tot} tris, {100 * tot / 2500:.0f} %)')
    ul = Vector((-link.matrix_world.translation.x, link.matrix_world.translation.z, -link.matrix_world.translation.y))
    print(f'  Link3P_Front (Unity) {[round(c, 4) for c in ul]} | lug pin axes X +-{LUG_X} Y {LUG_Y} Z {LUG_Z - zoff:.4f}')
    wt = obs['Wheel_Gauge'].matrix_world.translation
    print(f'  Wheel_Gauge pivot (Unity) {[round(c, 4) for c in (-wt.x, wt.z, -wt.y)]} rot {tuple(obs["Wheel_Gauge"].rotation_euler)}')
    fb, wb = bvh_world(obs['Frame']), bvh_world(obs['Wheel_Gauge'])
    pairs = fb.overlap(wb)
    fme = obs['Frame'].data
    xs = [obs['Frame'].matrix_world @ fme.vertices[vi].co for fi, _ in pairs for vi in fme.polygons[fi].vertices]
    print(f'  contact wheel<->frame: {len(pairs)} overlapping face pairs; frame faces involved x(Unity) '
          f'{round(min(-p.x for p in xs), 3) if xs else None}..{round(max(-p.x for p in xs), 3) if xs else None} (axle only expected)')
    return name, sc, coll, root, img, mat, obs


# ---------------- renders (from the skill's render_preview_template.py, as a function) ----------------
REF_VIEW = (0.77, -0.64, 0.47)     # Blender dir target->camera: front-left three-quarter (~50 deg off the nose), ~25 deg up (reference)

def render(sc, coll, out, view_dir=REF_VIEW, fill_w=0.70, res=(1280, 800), lens=70, bg=(0xc7, 0xcc, 0xd3)):
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
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.name.endswith('_Low1')]
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    target = Vector([(lo[i] + hi[i]) / 2 for i in range(3)]); dirv = Vector(view_dir).normalized()
    def place(dist):
        cam.location = target + dirv * dist
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.view_layers[0].update()
        xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    cd.shift_x = cd.shift_y = 0.0; dist = 8.0
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
    """run fn with sc as the window scene (live Blender), restoring the owner's scene afterwards"""
    win = bpy.context.window; prev = win.scene if win else None
    if win and prev != sc: win.scene = sc
    try:
        return fn(*a)
    finally:
        if win and prev is not None and win.scene != prev: win.scene = prev


def verify_headless(fbx, sc):
    """pc.verify needs a window (it switches scenes); headless: import into the build scene, measure, remove"""
    before_o, before_i, before_m = set(sc.objects), set(bpy.data.images), set(bpy.data.materials)
    bpy.ops.import_scene.fbx(filepath=fbx)
    obs = [o for o in sc.objects if o not in before_o]
    print('VERIFY objects', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'loc', [round(x, 3) for x in o.matrix_world.translation], 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs: bpy.data.objects.remove(o, do_unlink=True)
    for m in set(bpy.data.materials) - before_m:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in imgs:
        if i.users == 0: bpy.data.images.remove(i)


def fingerprint(obs):
    """order-independent geometry hash for live vs headless comparison"""
    out = {}
    for k, o in obs.items():
        vs = sorted((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in o.data.vertices)
        out[k] = (len(o.data.vertices), len(o.data.polygons), round(sum(a + 2 * b + 3 * c for a, b, c in vs), 4))
    print('FINGERPRINT', out)
    return out


name, sc, coll, root, img, mat, obs = build()
fingerprint(obs)
os.makedirs(CHECK_DIR, exist_ok=True)
if MODE == 'build':
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-01_check_ref.png'), REF_VIEW, 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-01_check_top.png'), (0.001, -0.02, 1.0), 0.80, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-01_check_side.png'), (1.0, 0.0, 0.08), 0.85, (960, 600))
    render(sc, coll, os.path.join(CHECK_DIR, 'IMP-01_check_back.png'), (-0.8, 0.9, 0.45), 0.80, (960, 600))
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
