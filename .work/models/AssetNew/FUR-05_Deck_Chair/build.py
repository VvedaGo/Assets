# build.py - FUR-05 Folding deck chair (FMS_Garden_Deck_Chair + _Blue), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build (shared, read only).
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- FUR-05 build|export|verify|dump
#   build  = build both meshes + printed checks + check renders to %TEMP%/assetnew_check/FUR-05/
#   export = build + 2 FBX (base, _Blue; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 for the live/headless comparison)
#   verify = only re-import the FBX files in art/
#   dump   = build + geometry dump only
#   LOD: none (catalogue).
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\FUR-05_Deck_Chair\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FUR-05', 'build']})
#   Live mode touches only the collection FUR-05_Deck_Chair and its child FUR-05_Deck_Chair_Blue.
# Axes (Blender): X = right (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: centre of the footprint (bounding box centred in X and Y) on the ground. One static mesh per asset.
# Slots (atlas A): 0 light wood frame, 1 dark wood foot bar, 5 red stripes (_Blue: 15), 3 cream stripes.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FUR-05')
NAME = 'FMS_Garden_Deck_Chair'
PREVIEW = 'FMS_Garden_FUR_05_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 400, '_Blue': 400}
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, CREAM, RED, BLUE = 0, 1, 3, 5, 15
VARIANTS = ('_Blue',)
COLL = 'FUR-05_Deck_Chair'
TMP = 'TMP_FUR05'
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FUR-05'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/FUR-05.3d.md; reference references/FUR-05.png measured in notes.md) ----
# Side frame in the (d, z) plane: d = depth from the front-leg foot axis toward the back (Blender +Y), z = up.
X_IN = 0.28                                   # plane of the front legs and the long back rails (centre)
X_OUT = 0.31                                 # plane of the rear legs (outside the back rails; 2 cm halving overlap at the crossing)
LEG_W, LEG_D = 0.055, 0.06                    # front legs 0.055 (X) x 0.06 (sides offset from the rails: no coplanar)
RAIL_W, RAIL_D = 0.05, 0.06                   # back rails / rear legs 0.05 (X) x 0.06
LEG_LEAN, LEG_TOP = 0.06, 0.56                # front leg axis (0, 0) -> (0.06, 0.56), top end inside the armrest
ARM_T, ARM_ZF, ARM_ZB = 0.05, 0.555, 0.525    # armrest 0.05 thick; axis z at the front / back end (top 0.58 -> 0.55)
ARM_X0, ARM_X1 = 0.2475, 0.3375               # armrest 0.09 wide: covers the front leg, the back rail and the rear leg
ARM_FRONT, ARM_BACK = -0.005, 0.63            # armrest d range (overhangs the front leg by ~3.5 cm)
RAIL_P0 = (0.012, 0.10)                       # back rail lower end: inside the front leg (corners 2+ mm inside), z 0.10
RAIL_P1 = (0.97, 0.88)                        # back rail upper end (perpendicular cut)
REAR_TOP, REAR_FOOT = (0.57, 0.53), 0.92      # rear leg: top inside the armrest back, foot at d 0.92 on the ground
FOOT_Z, FOOT_S = 0.10, 0.05                   # dark foot bar between the rear legs, 0.05 square
TOP_AP, TOP_N, TOP_DOWN = 0.025, 6, 0.11      # round top bar: 6 sides, apothem 0.025 (Ø0.05), 0.11 below the rail top
TOP_X = 0.30                                  # top bar ends inside the rail width
FB_AP, FB_N, FB_Z, FB_X = 0.03, 6, 0.36, 0.34  # front (seat) bar: 6 sides, 0.06 across, centre z 0.36, ends 3.25 cm past the legs
SINK = 0.005                                  # bars sunk 5 mm into the member they sit on
CLOTH_T, CLOTH_G = 0.025, -0.002              # cloth 0.025 thick; inner face 2 mm inside the bar flats (contact)
CLOTH_HW, STRIPE_N = 0.235, 5                 # cloth 0.47 wide (5 stripes of 0.094), clear of the rails (inner 0.255)
SEAT_LOW, SPAN_N = 0.33, 4                    # hanging cloth: lowest centre-line point z 0.33; 4 straight span segments
TOP_WRAP = (90.0, 30.0, -30.0)                # cloth vertices around the hex top bar (deg from the span normal)
FB_WRAP = (-30.0, 30.0, 90.0, 150.0)          # cloth vertices around the front bar (covers its top and front face)


def v2(d, z): return Vector((d, z))


def front_leg_d(z):
    return LEG_LEAN * z / LEG_TOP


def rail_dir():
    return (v2(*RAIL_P1) - v2(*RAIL_P0)).normalized()


def frame_points():
    t = rail_dir(); n = Vector((-t.y, t.x))                      # n: upper-front normal of the back rail
    top_c = v2(*RAIL_P1) - t * TOP_DOWN + n * (RAIL_D / 2 + TOP_AP - SINK)
    # front face of the front leg at FB_Z (leg axis leans back; perpendicular offset LEG_D / 2)
    la = Vector((LEG_LEAN, LEG_TOP)).normalized(); ln = Vector((-la.y, la.x))   # ln points to the front (-d) and up
    face = v2(front_leg_d(FB_Z), FB_Z) + ln * (LEG_D / 2)
    fb_c = v2(face.x - (FB_AP - SINK), FB_Z)
    return top_c, fb_c, t, n


def cloth_path():
    """centre line of the cloth in (d, z): wrap around the top bar, hanging span, wrap over the front bar.
    The span is a vertical-axis parabola (gravity sag) with its lowest centre-line point at SEAT_LOW; each bar is turned
    so the flat next to the span is parallel to the span tangent there (cloth lies on the flats, never cuts a bar)."""
    top_c, fb_c, _, _ = frame_points()
    rho_t = TOP_AP + CLOTH_G + CLOTH_T / 2; rho_f = FB_AP + CLOTH_G + CLOTH_T / 2
    perp = lambda w: Vector((w.y, -w.x))                           # outer side (up) of a down-front / up-front direction
    u_t = u_f = (fb_c - top_c).normalized()
    for _ in range(40):
        e0 = top_c + perp(u_t) * rho_t + u_t * rho_t * math.tan(math.pi / TOP_N)
        e1 = fb_c + perp(u_f) * rho_f - u_f * rho_f * math.tan(math.pi / FB_N)
        r = math.sqrt((e0.y - SEAT_LOW) / (e1.y - SEAT_LOW))
        dl = e1.x + (e0.x - e1.x) / (1 + r); k = (e1.y - SEAT_LOW) / (e1.x - dl) ** 2
        slope = lambda d: 2 * k * (d - dl)
        u_t = Vector((-1.0, -slope(e0.x))).normalized(); u_f = Vector((-1.0, -slope(e1.x))).normalized()
    v_t, v_f = perp(u_t), perp(u_f)
    pts = [top_c + (v_t * math.cos(math.radians(a)) - u_t * math.sin(math.radians(a))) * (rho_t / math.cos(math.pi / TOP_N))
           for a in TOP_WRAP]
    for i in range(1, SPAN_N):
        d = e0.x + (e1.x - e0.x) * i / SPAN_N
        pts.append(Vector((d, SEAT_LOW + k * (d - dl) ** 2)))
    pts += [fb_c + (v_f * math.cos(math.radians(b)) + u_f * math.sin(math.radians(b))) * (rho_f / math.cos(math.pi / FB_N))
            for b in FB_WRAP]
    return pts, v_t, dict(top=(u_t, v_t), front=(u_f, v_f), low=(dl, SEAT_LOW))


def offset_path(pts, up):
    """mitred offsets (thickness kept): returns (outer, inner) lists; outer = side of `up` (away from the bars)"""
    out, inn = [], []
    n = len(pts)
    def nrm(a, b):
        d = (b - a).normalized(); m = Vector((-d.y, d.x))
        return m
    segn = [nrm(pts[i], pts[i + 1]) for i in range(n - 1)]
    sgn = 1 if segn[0].dot(up) > 0 else -1
    segn = [m * sgn for m in segn]
    for i in range(n):
        if i == 0: m = segn[0]
        elif i == n - 1: m = segn[-1]
        else:
            m = (segn[i - 1] + segn[i]).normalized(); m = m / m.dot(segn[i])
        out.append(pts[i] + m * CLOTH_T / 2); inn.append(pts[i] - m * CLOTH_T / 2)
    return out, inn


# ---------------- small geometry helpers ----------------
def obox(P, cn, x0, x1, y0, y1, z0, z1, slot, ground=False):
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], slot), P.face([v[4], v[5], v[7], v[6]], slot),
          P.face([v[0], v[1], v[5], v[4]], slot), P.face([v[2], v[6], v[7], v[3]], slot),
          P.face([v[0], v[4], v[6], v[2]], slot), P.face([v[1], v[3], v[7], v[5]], slot)]
    P.comp.append((cn, fs, ground))


def sq(w, d):
    return [(w / 2, d / 2), (-w / 2, d / 2), (-w / 2, -d / 2), (w / 2, -d / 2)]


def member(P, cn, x, a, b, w, d, slot, ground=False):
    """straight member in the plane X = x from (d, z) a to b; ground=True cuts the a end on z = 0"""
    p0 = Vector((x, a[0], a[1])); p1 = Vector((x, b[0], b[1]))
    pc.sweep(P, cn, p0, p1, sq(w, d), [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0)], slot, slot, slot,
             ref=(1, 0, 0), flat0=ground, ground=ground)


def x_bar(P, cn, c, ap, n, half, wrap_dirs, slot):
    """prism along X (|x| <= half) with a regular n-gon section of apothem ap, vertices at the given 2D directions"""
    r = ap / math.cos(math.pi / n)
    sec = [c + d * r for d in wrap_dirs]
    rings = [[Vector((x, p.x, p.y)) for p in sec] for x in (-half, half)]
    P.loft(cn, rings, slot, slot, slot)


def build_chair(stripe):
    P = Part('Body')
    for s in (-1, 1):
        member(P, 'FrontLegs', s * X_IN, (0.0, 0.0), (LEG_LEAN, LEG_TOP), LEG_W, LEG_D, WOOD, ground=True)
        member(P, 'BackRails', s * X_IN, RAIL_P0, RAIL_P1, RAIL_W, RAIL_D, WOOD)
        member(P, 'RearLegs', s * X_OUT, (REAR_FOOT, 0.0), REAR_TOP, RAIL_W, RAIL_D, WOOD, ground=True)
        member(P, 'Armrests', s * (ARM_X0 + ARM_X1) / 2, (ARM_FRONT, ARM_ZF), (ARM_BACK, ARM_ZB), ARM_X1 - ARM_X0, ARM_T, WOOD)
    rd = REAR_FOOT + (REAR_TOP[0] - REAR_FOOT) * FOOT_Z / REAR_TOP[1]
    obox(P, 'FootBar', -(X_OUT - 0.005), X_OUT - 0.005, rd - FOOT_S / 2, rd + FOOT_S / 2, FOOT_Z - FOOT_S / 2,
         FOOT_Z + FOOT_S / 2, WOOD_D)
    top_c, fb_c, _, _ = frame_points()
    path, v, orient = cloth_path()
    # bars oriented so their flats carry the cloth wrap (cloth inner face parallel to the flats)
    (ut, vt), (uf, vf) = orient['top'], orient['front']
    tdirs = [(vt * math.cos(math.radians(a)) - ut * math.sin(math.radians(a))) for a in
             [30.0 + 60.0 * k for k in range(TOP_N)]]
    fdirs = [(vf * math.cos(math.radians(b)) + uf * math.sin(math.radians(b))) for b in
             [180.0 / FB_N + 360.0 / FB_N * k for k in range(FB_N)]]
    x_bar(P, 'TopBar', top_c, TOP_AP, TOP_N, TOP_X, tdirs, WOOD)
    x_bar(P, 'FrontBar', fb_c, FB_AP, FB_N, FB_X, fdirs, WOOD)
    # cloth: closed shell; ring = 6 outer points (stripe borders) + 6 inner points; one palette cell per stripe
    outer, inner = offset_path(path, v)
    xs = [-CLOTH_HW + 2 * CLOTH_HW * k / STRIPE_N for k in range(STRIPE_N + 1)]
    rings = []
    for po, pi in zip(outer, inner):
        rings.append([Vector((x, po.x, po.y)) for x in xs] + [Vector((x, pi.x, pi.y)) for x in reversed(xs)])
    cols = [stripe if k % 2 == 0 else CREAM for k in range(STRIPE_N)]
    def side(j, k):
        if k < STRIPE_N: return cols[k]
        if k == STRIPE_N or k == 2 * STRIPE_N + 1: return stripe          # cloth edges (outer stripes are red)
        return cols[2 * STRIPE_N - k]
    P.loft('Cloth', rings, side, stripe, stripe)
    # pivot: centre of the bounding box in X and Y (Blender Y = d before centring)
    ys = [vv.co.y for vv in P.bm.verts]
    dc = (min(ys) + max(ys)) / 2
    for vv in P.bm.verts: vv.co.y -= dc
    info = dict(dc=dc, top_c=top_c, fb_c=fb_c, path=path, outer=outer, inner=inner, low=orient['low'], orient=orient)
    return P, info


# ---------------- scene / atlas ----------------
def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    colls = [coll]
    for suf in VARIANTS:
        c = bpy.data.collections.get(COLL + suf) or bpy.data.collections.new(COLL + suf)
        if c.name not in coll.children: coll.children.link(c)
        colls.append(c)
    for c in colls:
        for o in list(c.objects):
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return colls


def atlas_and_material():
    """reuse the shared atlas A PNG (never rewritten here) and M_Garden_Build (created only when missing)"""
    path = os.path.join(ART, 'Textures', ATLAS_TEX)
    img = bpy.data.images.get(ATLAS_TEX)
    if img is None: img = bpy.data.images.load(path, check_existing=True)
    px = list(img.pixels); W_, H_ = img.size
    lin = lambda h: tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bad = []
    for s, hx in enumerate(PAL_A):
        col, row = s % 4, s // 4; x = int((col + 0.5) * W_ / 4); y = int(H_ - (row + 0.5) * H_ / 4)
        got = px[(y * W_ + x) * 4:(y * W_ + x) * 4 + 3]
        if max(abs(a - b) for a, b in zip(got, lin(hx))) > 2 / 255: bad.append((s, hx, [round(g * 255) for g in got]))
    print('  atlas', bpy.path.abspath(img.filepath), img.size[:], 'palette mismatches', bad)
    mat = bpy.data.materials.get(ATLAS_MAT)
    if mat is None:
        mat = pc.material(ATLAS_MAT, img)
        next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Roughness'].default_value = 0.85
    return img, mat


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        me = ob.data; uv = me.uv_layers.active.data
        vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
        fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                     tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
        allv.append(vs + [tuple(round(c, 5) for c in ob.matrix_world.translation)]); allf.append(fs)
    h = hashlib.sha1(json.dumps([allv, allf]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=[len(v) for v in allv], faces=[len(x) for x in allf], sha1=h), f)
    print('  geometry dump', path, [len(v) for v in allv], 'verts', [len(x) for x in allf], 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), frame=None):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new(TMP + '_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new(TMP + '_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new(TMP + '_World'); w.use_nodes = True; nt = w.node_tree
    wo = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD'); bgn = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bgn.inputs['Color'].default_value = (lin(bg[0]), lin(bg[1]), lin(bg[2]), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.85, 0.88, 0.95, 1)
    amb.inputs['Strength'].default_value = 0.65
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bgn.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], wo.inputs['Surface']); sc.world = w
    tmp = []
    def sun(nm, rot, e, col, shadow=True):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.color = col; ld.angle = math.radians(28); ld.use_shadow = shadow
        o = bpy.data.objects.new(nm, ld); o.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(o)
        tmp.append(o)
    sun(TMP + '_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun(TMP + '_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new(TMP + '_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new(TMP + '_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    bpy.context.view_layer.update()
    pts = frame or [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = (sum(pts, Vector()) / len(pts)) if frame else Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2))
    dv = Vector(view_dir).normalized()
    def place(d):
        loc = target + dv * d; q = (target - loc).to_track_quat('-Z', 'Y')
        cam.matrix_world = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        cs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs)
    d = 10.0
    for _ in range(30):
        x0, x1, y0, y1 = place(d); k = max((x1 - x0) / fill_w, (y1 - y0) / fill_h)
        if lens: d *= k
        else: cd.ortho_scale *= k
    x0, x1, y0, y1 = place(d)
    asp = res[1] / res[0]
    cd.shift_x = (x0 + x1) / 2 - 0.5; cd.shift_y = ((y0 + y1) / 2 - 0.5) * asp
    sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
    try:
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        for o in tmp:
            dat = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(dat, bpy.types.Light): bpy.data.lights.remove(dat)
            else: bpy.data.cameras.remove(dat)
        bpy.data.collections.remove(tc); bpy.data.scenes.remove(sc); bpy.data.worlds.remove(w)
    print('  render', out)


def save_lib(path, colls, mat, img):
    data = set(colls) | {mat, img}
    for c in colls: data |= set(c.objects) | {o.data for o in c.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(asset, coll, root, fbx):
    """the owner's selection and active object are restored after the export (live Blender)"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx


# ---------------- checks ----------------
def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def comp_tree(P, names):
    from mathutils.bvhtree import BVHTree
    P.bm.verts.index_update()
    vs = [v.co.copy() for v in P.bm.verts]
    polys = [[v.index for v in f.verts] for nm, fs, _ in P.comp if nm in names for f in fs]
    return BVHTree.FromPolygons(vs, polys), vs, polys


def functional_checks(P, info):
    ok = True
    cloth, vs, cp = comp_tree(P, {'Cloth'})
    cv = {i for f in cp for i in f}
    rows = []
    for nm in ('TopBar', 'FrontBar'):
        t, _, _ = comp_tree(P, {nm})
        rows.append((f'cloth touches {nm}', 1.0 if cloth.overlap(t) else 0.0, 1.0, 'eq'))
    for nm in ('BackRails', 'FrontLegs', 'Armrests', 'RearLegs', 'FootBar'):
        t, _, _ = comp_tree(P, {nm})
        rows.append((f'cloth clear of {nm}', 0.0 if cloth.overlap(t) else 1.0, 1.0, 'eq'))
    low = min(vs[i].z for i in cv)
    pth = info['path']; nt = len(TOP_WRAP); nf = len(FB_WRAP)
    (ut, _), (uf, _) = info['orient']['top'], info['orient']['front']
    a_top = math.degrees(ut.angle(pth[nt] - pth[nt - 1])); a_fb = math.degrees(uf.angle(pth[-nf] - pth[-nf - 1]))
    rows.append(('top bar: span bend below the bar facet angle (no cut into the bar)', 360 / TOP_N - a_top, 0.0, 'ge'))
    rows.append(('front bar: span bend below the bar facet angle (no cut into the bar)', 360 / FB_N - a_fb, 0.0, 'ge'))
    print(f'  cloth: bend top {a_top:.1f} deg, front {a_fb:.1f} deg; lowest centre line at d {info["low"][0]:.3f}')
    fb_top = info['fb_c'].y + FB_AP
    rows.append(('cloth lowest point (seat sag)', low, 0.25, 'ge'))
    rows.append(('front bar top', fb_top, 0.30, 'ge'))
    for nm, got, want, how in rows:
        good = got >= want - 1e-4 if how == 'ge' else abs(got - want) <= 1e-4
        ok &= good
        print(f'  FUNC {nm}: {got:.4f} (want {">= " if how == "ge" else ""}{want}) {"OK" if good else "FAIL"}')
    return ok


def size_report(body):
    pts = [body.matrix_world @ v.co for v in body.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    ground = [p for p in pts if abs(p.z) < 1e-6]
    feet = {}
    for p in ground: feet.setdefault((p.x > 0, p.y > 0), []).append(p)
    ok = abs(lo[2]) < 1e-6 and len(feet) == 4 and len(ground) == 16
    print(f'  SIZE X {hi[0]-lo[0]:.3f} Y {hi[1]-lo[1]:.3f} Z {hi[2]-lo[2]:.3f} | bbox centre ({(lo[0]+hi[0])/2:.4f}, {(lo[1]+hi[1])/2:.4f})')
    print(f'  GROUND min z {lo[2]:.4f}, verts on z=0: {len(ground)} in {len(feet)} feet',
          [(len(v), round(sum(p.x for p in v) / len(v), 3), round(sum(p.y for p in v) / len(v), 3)) for v in feet.values()],
          '->', 'OK' if ok else 'FAIL')
    return ok


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        P, info = build_chair(BLUE if suf else RED); tris = part_tris(P)
        fok = functional_checks(P, info) if not suf else True
        body = pc.to_object(P, asset, coll, mat, (0, 0, 0), root)
        bpy.context.view_layer.update()
        print(f'== {asset}')
        tot = pc.report({'Body': body})
        print('  tris per component (before triangulation of the caps):', tris)
        print(f'  budget {BUDGET[suf]} ->', 'OK' if tot <= BUDGET[suf] else f'OVER x{tot / BUDGET[suf]:.2f}')
        pc.coplanar_overlaps(body)
        cells = sorted({cell_of(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
        if suf:
            same = [tuple(round(c, 6) for c in v.co) for v in body.data.vertices] == \
                   [tuple(round(c, 6) for c in v.co) for v in res[''][2].data.vertices]
            print(f'  {suf}: same vertices as the base {same}; cells used {cells}')
        else:
            print(f'  base: cells used {cells}; footprint shift d {info["dc"]:.4f}')
            size_report(body)
            print('  FUNCTIONAL', 'OK' if fok else 'FAIL')
            print('  SNAP: no contract (free-standing furniture)')
        res[suf] = (coll, root, body, tot)
    return colls, img, mat, res


VIEW_REF = (0.494, -0.732, 0.469)             # reference: front-right 3/4 (yaw 34, elevation 28 deg; fitted, notes.md)
REF_LENS = 150
VIEW_PREVIEW = (0.85, -1.25, 0.75)            # series preview 3/4 from the front-right (~25 deg), as FUR-02 / FUR-04

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, b, t = res[suf]; return [r, b]
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.70, fill_h=0.86, lens=REF_LENS)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_Blue'), os.path.join(CHECK_DIR, f'FUR-05_blue_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_side_{tag}.png'), (1, 0, 0.0), res=(1000, 1000), fill_w=0.85, fill_h=0.85, lens=0)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_back_{tag}.png'), (-0.6, 1.0, 0.5), res=(1000, 800))
        body = res[''][2]
        fr = [body.matrix_world @ v.co for v in body.data.vertices if (body.matrix_world @ v.co).y < -0.25 and (body.matrix_world @ v.co).z < 0.65]
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_close_front_{tag}.png'), VIEW_REF, res=(1000, 700), lens=REF_LENS, frame=fr, fill_w=0.9, fill_h=0.9)
        tp = [body.matrix_world @ v.co for v in body.data.vertices if (body.matrix_world @ v.co).z > 0.7]
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-05_close_top_{tag}.png'), VIEW_REF, res=(1000, 700), lens=REF_LENS, frame=tp, fill_w=0.9, fill_h=0.9)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbxs = []
        for suf in ('',) + VARIANTS:
            c, r, b, t = res[suf]
            fbxs.append(export_one(NAME + suf, c, r, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
        render(objs_of(''), os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        for f in fbxs: pc.verify(f)
    if MODE in ('export', 'dump'):
        geom_dump([res[s][2] for s in ('',) + VARIANTS], os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
