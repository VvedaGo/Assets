# build.py - FUR-04 Wrought-iron bistro chair (FMS_Garden_Bistro_Chair + _White), pack CottageGardenDecor (Cottage Garden Decor),
# atlas A Garden_Build. Set partner of FUR-03 Bistro_Table (same rods, same slot, same iron helpers).
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- FUR-04 build|export|verify|dump
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/FUR-04/
#   export = build + 2 FBX (base, _White; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 for the live/headless comparison)
#   verify = only re-import the FBX files in art/
#   dump   = build + geometry dump only
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\FUR-04_Bistro_Chair\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FUR-04', 'build']})
#   Live mode touches only the collection FUR-04_Bistro_Chair and its child FUR-04_Bistro_Chair_White.
# Axes (Blender): X = right (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: centre of the footprint on the ground (bounding box centred in X and Y). No LOD (catalogue).
# One palette slot: 13 wrought iron (_White: 10).
# Iron helpers copied from FUR-03 build.py (oct_sec, rod_rings, hermite, s_clearance) - same wording as STR-02.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FUR-04')
NAME = 'FMS_Garden_Bistro_Chair'
PREVIEW = 'FMS_Garden_FUR_04_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 1400, '_White': 1400}          # orchestrator 2026-11-25: 700 -> 1400 (6-sided rods, round curls)
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
IRON, WHITE = 13, 10
VARIANTS = ('_White',)
COLL = 'FUR-04_Bistro_Chair'
TMP = 'TMP_FUR04'
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part, ngon

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FUR-04'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/FUR-04.3d.md; reference references/FUR-04.png measured in notes.md) ----
H_TOP = 0.85                                   # total height (catalogue; reference ~0.82-0.85)
SEAT_N, SEAT_AF = 12, 0.41                     # 12-sided seat (FUR-03 top wording), a flat to the front, across the flats
SEAT_CY = -0.02                                # seat centre 0.02 to the front (spec)
SEAT_Z0, SEAT_Z1 = 0.40, 0.45                  # seat slab 0.05 (reference edge band; functional seat height 0.45)
SEAT_CH, SEAT_CHZ = 0.016, 0.012               # top edge chamfer (reference band): inset / drop
ROD_N = 6                                      # all iron rods 6-sided (FUR-03 option C)
LEG_A = 0.018                                  # legs and hoop: 0.036 across the flats (FUR-03 legs)
SROD = 0.017                                   # back scroll bar: 0.034 across (spec ~0.035; 128 px read)
RING_A = 0.015                                 # ring brace bar: 0.030 across (>= 0.03)
EMBED = 0.004
LEG_AZ = (45.0, 135.0, 225.0, 315.0)           # four legs on the diagonals around the seat centre
LEG_R0, LEG_R1, LEG_ZT = 0.20, 0.15, 0.41      # leg centre-line radius at the ground / under the seat (spec)
LEG_TOP = 0.435                                # leg top sunk into the seat slab
RING_Z, RING_SEG = 0.20, 16                    # ring brace height (spec 0.20), 16 segments (vertices on the legs)
HOOP_O = Vector((0.0, 0.10, SEAT_Z1))          # hoop plane origin on the seat top (v = 0)
HOOP_U0, HOOP_UW = 0.14, 0.182                 # hoop centre-line half-width at the seat / at the widest point
HOOP_VC_K = 0.58                               # widest point at 58 % of the hoop height (reference)
HOOP_SIDE_SEG, HOOP_TOP_SEG = 4, 14            # lower straight-ish sides, elliptic crown
Y_BACK = 0.225                                 # hoop back face -> bbox centred in Y with the seat front at -0.225
# back scroll (2D in the hoop plane: u = right, v = up from the seat top)
S_LOW = dict(cu=-0.012, R0=0.072, Rt=0.022, span=400.0, seg=15)   # lower spiral (clockwise from the right side inward)
S_PB = (-0.055, 0.285)                         # upper bowl of the S (left), then up into the hoop crown
S_CURL = dict(cu=0.056, cv=0.272, R0=0.050, tip_k=0.42, span=315.0, seg=11)   # upper-right spiral (CCW), branch
S_SPINE_SEG, S_TOP_SEG = 5, 5


# ---------------- shared iron helpers (copied from FUR-03 build.py) ----------------
def oct_sec(a, n=8):
    return ngon(a / math.cos(math.pi / n), n, math.pi / n)          # flats normal to the section axes


def rod_rings(pts, up, sec, closed=False):
    """mitred rings along a polyline (pack_shapes.path_sweep without the loft); closed=True for a loop"""
    up = Vector(up); rings = []; n = len(pts)
    for i, c in enumerate(pts):
        has_p = closed or i > 0; has_n = closed or i < n - 1
        d1 = (c - pts[i - 1]).normalized() if has_p else None
        d2 = (pts[(i + 1) % n] - c).normalized() if has_n else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in sec])
    return rings


def hermite(P0, T0, P1, T1, n):
    """n - 1 interior points of a cubic Hermite curve (ends excluded)"""
    P0, T0, P1, T1 = Vector(P0), Vector(T0), Vector(P1), Vector(T1); out = []
    for k in range(1, n):
        s = k / n
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        out.append(P0 * h00 + T0 * h10 + P1 * h01 + T1 * h11)
    return out


def s_clearance(pts, skip=0.075):
    """min distance between centre-line samples further apart than `skip` along the curve (self-touch check)"""
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + (b - a).length)
    best = 9.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if acc[j] - acc[i] > skip: best = min(best, (pts[i] - pts[j]).length)
    return best


def spiral(cu, cv, R0, R1, th0, span, seg):
    """2D spiral samples from angle th0 (deg) over `span` (signed deg, + = CCW), radius R0 -> R1"""
    out = []
    for k in range(seg + 1):
        f = k / seg; th = math.radians(th0 + span * f); r = R0 + (R1 - R0) * f
        out.append(Vector((cu + r * math.cos(th), cv + r * math.sin(th))))
    return out


# ---------------- chair ----------------
def seat(P, slot):
    """12-sided slab, a flat to the front, chamfered top edge (reference band); top = 0.45"""
    a0 = math.pi / SEAT_N + math.pi / 2
    rc = lambda af: af / 2 / math.cos(math.pi / SEAT_N)
    R = rc(SEAT_AF); Ri = rc(SEAT_AF - 2 * SEAT_CH)
    prof = [(Ri, SEAT_Z1), (R, SEAT_Z1 - SEAT_CHZ), (R, SEAT_Z0)]
    rings = [[Vector((x, y + SEAT_CY, z)) for x, y in ngon(r, SEAT_N, a0)] for r, z in prof]
    P.loft('Seat', list(reversed(rings)), slot, slot, slot)


def leg_r(z):
    return LEG_R0 + (LEG_R1 - LEG_R0) * z / LEG_ZT


def legs(P, slot):
    sec = oct_sec(LEG_A, ROD_N)
    for az in LEG_AZ:
        a = math.radians(az); rad = Vector((math.cos(a), math.sin(a), 0)); tng = Vector((-math.sin(a), math.cos(a), 0))
        c = Vector((0, SEAT_CY, 0))
        p0 = c + rad * leg_r(-0.05); p0.z = -0.05                           # extended below, then cut flat at z = 0
        p1 = c + rad * leg_r(LEG_TOP); p1.z = LEG_TOP
        rings = rod_rings([p0, p1], tng, sec)
        t = (p1 - p0).normalized()
        rings[0] = [v - t * (v.z / t.z) for v in rings[0]]                 # flat foot on the ground
        P.loft('Leg', rings, slot, slot, slot, ground=True)


def ring_brace(P, slot):
    r = leg_r(RING_Z) - LEG_A; c = Vector((0, SEAT_CY, RING_Z))          # centre-line on the legs' inner faces (spec Ø0.30)
    pts = [c + Vector((r * math.cos(math.radians(45 + 360 * k / RING_SEG)), r * math.sin(math.radians(45 + 360 * k / RING_SEG)), 0))
           for k in range(RING_SEG)]
    rings = rod_rings(pts, (0, 0, 1), oct_sec(RING_A, ROD_N), closed=True)
    P.torus_loft('Ring', rings, slot)


def hoop_frame(tilt, vtop):
    """hoop plane basis and 2D hoop centre-line (u, v)"""
    eu = Vector((1, 0, 0)); ev = Vector((0, math.sin(tilt), math.cos(tilt))); n = eu.cross(ev)
    vc = HOOP_VC_K * vtop; b = vtop - vc
    crown = [Vector((HOOP_UW * math.cos(math.pi * k / HOOP_TOP_SEG), vc + b * math.sin(math.pi * k / HOOP_TOP_SEG)))
             for k in range(HOOP_TOP_SEG + 1)]
    v0 = -0.022                                                             # ends sunk into the seat slab
    right = [Vector((HOOP_U0, v0))] + hermite((HOOP_U0, v0), (0.03, vc), (HOOP_UW, vc), (0, vc), HOOP_SIDE_SEG)
    left = [Vector((-p.x, p.y)) for p in reversed(right)]
    pts2 = right + crown + left
    to3 = lambda p: HOOP_O + eu * p.x + ev * p.y
    crown_v = lambda u: vc + b * math.sqrt(max(0.0, 1 - (u / HOOP_UW) ** 2))
    return eu, ev, n, pts2, to3, crown_v


def solve_hoop():
    """tilt and crown height so the hoop outer surface reaches z = H_TOP and y = Y_BACK"""
    tilt, vtop = math.radians(15), 0.38
    for _ in range(8):
        eu, ev, n, pts2, to3, _ = hoop_frame(tilt, vtop)
        rings = rod_rings([to3(p) for p in pts2], n, oct_sec(LEG_A, ROD_N))
        zmax = max(v.z for r in rings for v in r); ymax = max(v.y for r in rings for v in r)
        apex = to3(max(pts2, key=lambda p: p.y))
        zt = apex.z + (H_TOP - zmax); yt = apex.y + (Y_BACK - ymax)
        dy, dz = yt - HOOP_O.y, zt - HOOP_O.z
        tilt = math.atan2(dy, dz); vtop = math.hypot(dy, dz)
    return tilt, vtop


def scroll_lines(crown_v):
    """2D centre-lines: main S (lower spiral tip -> spine -> upper bowl -> into the hoop crown) and the branch curl"""
    L = S_LOW
    low = spiral(L['cu'], 0.0, L['Rt'], L['R0'], -L['span'], L['span'], L['seg'])  # tip -> outer (right side, th 0)
    lift = SROD - EMBED - min(p.y for p in low)                             # lowest bar edge 4 mm into the seat top
    low = [p + Vector((0, lift)) for p in low]
    Pa = low[-1]; Pb = Vector(S_PB)
    dv = LEG_A + SROD - 0.014                                               # 14 mm overlap where it meets the hoop bar
    Pc = Vector((0.030, crown_v(0.030) - dv))
    Pd = Vector((0.085, crown_v(0.085) - 0.004))                            # end runs inside the hoop bar (cap hidden)
    spine = hermite(Pa, (0, 0.26), Pb, (0, 0.20), S_SPINE_SEG)
    top = hermite(Pb, (0, 0.16), Pc, (0.14, 0), S_TOP_SEG)
    main = low + spine + [Pb] + top + [Pc, Pd]
    C = S_CURL; start = Vector((C['cu'], C['cv'] - C['R0']))
    att = min(spine, key=lambda p: abs(p.y - (start.y - 0.012)))            # attach on the spine just below the curl
    att = att + Vector((0.006, 0))
    curl = spiral(C['cu'], C['cv'], C['R0'], C['R0'] * C['tip_k'], -90.0, C['span'], C['seg'])
    branch = [att] + hermite(att, (0.06, 0.02), start, (0.06, 0), 2) + curl
    return main, branch, low, curl


def build_chair(slot):
    P = Part('Body')
    seat(P, slot); legs(P, slot); ring_brace(P, slot)
    tilt, vtop = solve_hoop()
    eu, ev, n, hoop2, to3, crown_v = hoop_frame(tilt, vtop)
    P.loft('Hoop', rod_rings([to3(p) for p in hoop2], n, oct_sec(LEG_A, ROD_N)), slot, slot, slot)
    main, branch, low, curl = scroll_lines(crown_v)
    P.loft('Scroll', rod_rings([to3(p) for p in main], n, oct_sec(SROD, ROD_N)), slot, slot, slot)
    P.loft('Curl', rod_rings([to3(p) for p in branch], n, oct_sec(SROD, ROD_N)), slot, slot, slot)
    info = dict(tilt=math.degrees(tilt), vtop=vtop, hoop2=hoop2, main=main, branch=branch, low=low, curl=curl)
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
        allv.append(vs); allf.append(fs)
    h = hashlib.sha1(json.dumps([allv, allf]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=[len(v) for v in allv], faces=[len(x) for x in allf], sha1=h), f)
    print('  geometry dump', path, [len(v) for v in allv], 'verts', [len(x) for x in allf], 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), box=None):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_FUR04_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_FUR04_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_FUR04_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_FUR04_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_FUR04_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_FUR04_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_FUR04_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    if box: pts = [p for p in pts if all(box[0][i] <= p[i] <= box[1][i] for i in range(3))]   # close-up framing
    target = Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2 if box else 0,
                     (min(p.y for p in pts) + max(p.y for p in pts)) / 2 if box else 0,
                     (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
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
    bpy.ops.render.render(write_still=True, scene=sc.name)
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
    """the selection and the active object are restored after the export (live Blender)"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx



def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def size_report(body):
    pts = [body.matrix_world @ v.co for v in body.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    ok = True
    seat_top = max(p.z for p in pts if math.hypot(p.x, p.y - SEAT_CY) < 0.22 and p.y < 0.0 and p.z < 0.6)   # front half: no back rods
    rows = [('width X (<= 0.45)', hi[0] - lo[0], 0.45, 'le'), ('depth Y (<= 0.50)', hi[1] - lo[1], 0.50, 'le'),
            ('height (= 0.85)', hi[2], H_TOP, 'eq'), ('seat top (= 0.45)', seat_top, SEAT_Z1, 'eq'),
            ('min z (ground contact)', lo[2], 0.0, 'eq')]
    for nm, got, want, how in rows:
        good = (got <= want + 1e-4) if how == 'le' else abs(got - want) <= 1e-4
        ok &= good
        print(f'  SIZE {nm}: {got:.4f} (want {"<= " if how == "le" else ""}{want}) {"OK" if good else "FAIL"}')
    print(f'  bbox x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} (centre {(lo[0] + hi[0]) / 2:.3f}, {(lo[1] + hi[1]) / 2:.3f})')
    ground = [p for p in pts if abs(p.z) < 1e-6]
    feet = {}
    for p in ground: feet.setdefault((p.x > 0, p.y > SEAT_CY), []).append(p)
    print(f'  ground verts (z = 0): {len(ground)} in {len(feet)} feet;',
          [(len(v), round(sum(p.x for p in v) / len(v), 3), round(sum(p.y for p in v) / len(v), 3)) for v in feet.values()])
    ok &= len(feet) == 4
    print('  SIZE', 'OK' if ok else 'FAIL')
    return ok


def curl_across(pts, bar):
    return min(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts)) + 2 * bar


def cross_clear(a, b, skip_pts=3):
    """min centre-line distance between the branch (minus its attach samples) and the main S"""
    return min((p - q).length for p in a[skip_pts:] for q in b)


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        P, info = build_chair(WHITE if suf else IRON); tris = part_tris(P)
        body = pc.to_object(P, asset, coll, mat, (0, 0, 0), root, mirror_skip=('Scroll', 'Curl'))
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
            print(f'  base: cells used {cells}')
            print(f'  hoop tilt {info["tilt"]:.1f} deg, crown v {info["vtop"]:.3f}; hoop self-clearance '
                  f'{s_clearance(info["hoop2"]):.4f}')
            print(f'  scroll self-clearance {s_clearance(info["main"]):.4f} (>= {2 * SROD:.3f}); branch vs S '
                  f'{cross_clear(info["branch"], info["main"]):.4f}; branch self {s_clearance(info["branch"]):.4f}')
            print(f'  lower spiral across {curl_across(info["low"], SROD):.3f}, upper curl across '
                  f'{curl_across(info["curl"], SROD):.3f} (>= 0.10)')
            mu = [p.x for p in info['main']]; mv = [p.y for p in info['main']]
            print(f'  S extent u {min(mu) - SROD:.3f}..{max(mu) + SROD:.3f} v {min(mv) - SROD:.3f}..{max(mv) + SROD:.3f}')
            size_report(body)
        res[suf] = (coll, root, body, tot)
    return colls, img, mat, res


VIEW_REF = (0.12, -1.0, 0.36)                 # reference: nearly frontal, a little from the right, ~20 deg above
VIEW_PREVIEW = (0.85, -1.25, 0.75)            # series preview 3/4 from the front-right (~25 deg), as FUR-03 / STR-02

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, b, t = res[suf]; return [r, b]
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-04_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.62, fill_h=0.92, lens=50)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-04_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-04_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_White'), os.path.join(CHECK_DIR, f'FUR-04_white_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-04_side_{tag}.png'), (1, 0, 0.0), res=(1000, 1000), fill_w=0.85, fill_h=0.85, lens=0)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-04_front_{tag}.png'), (0, -1, 0.0), res=(1000, 1000), fill_w=0.85, fill_h=0.85, lens=0)
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
