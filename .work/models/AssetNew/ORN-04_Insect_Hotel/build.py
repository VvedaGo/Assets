# build.py - ORN-04 Insect hotel (FMS_Garden_Insect_Hotel), pack AssetNew (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- ORN-04 build|export|verify
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/ORN-04/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
#   verify = only re-import the FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\ORN-04_Insect_Hotel\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['ORN-04', 'build']})
#   Live mode touches only the collection ORN-04_Insect_Hotel (other objects, scenes and the owner's .blend stay as they are).
# Axes (Blender): X = width, -Y = open front (Unity +Z with the -Z-forward export), Z = up (Unity Y).
# Pivot: centre of the footprint on the ground. No LOD (catalogue). One mesh, one material.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'ORN-04')
COLL = 'ORN-04_Insect_Hotel'
NAME = 'FMS_Garden_Insect_Hotel'
PREVIEW = 'FMS_Garden_ORN_04_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 900
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD, WOOD_D, WOOD_M, CREAM, STRAW, BRICK_F, HOLE, BRICK = 0, 1, 2, 3, 4, 6, 8, 14
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part
from pack_shapes import fill

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'ORN-04'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/ORN-04.3d.md; reference planning/AssetNew/references/ORN-04.png, see notes.md) ----
FX, FY, T = 0.27, 0.14, 0.05                   # frame (tray) outer half width / half depth, board thickness (spec 0.05)
LEG_W, LEG_H, LEG_IN = 0.08, 0.14, 0.01        # legs 0.08 square, frame bottom at 0.14, 1 cm inside the frame outline
CELL_H, DIV = 0.135, 0.03                      # cell clear height (reference cells ~1:1), dividers 0.03 (spec minimum)
BACK_IN = 0.12                                 # inner back face of the frame (back board 0.02)
Z0 = LEG_H                                     # frame bottom
ZI0 = Z0 + T                                   # inner bottom
XI = FX - T                                    # inner half width 0.22
CELL_W = (2 * XI - 2 * DIV) / 3                # 0.1267
ZI1 = ZI0 + 3 * CELL_H + 2 * DIV               # inner top
ZT = ZI1 + T                                   # frame top
ROOF_X, ROOF_T, PITCH, OVER = 0.30, 0.03, math.radians(38), 0.03   # roof 0.60 wide, boards 0.03, pitch, overhang front/back
RIDGE_W, RIDGE_H = 0.05, 0.03

CX = [-XI + CELL_W / 2, 0.0, XI - CELL_W / 2]                       # cell centres, viewer's left (-X) -> right
CZ0 = [ZI0 + r * (CELL_H + DIV) for r in range(3)]                  # cell floors, bottom -> top row
# fillings as seen from the front, rows top -> bottom (reference): L = logs, S = straw, B = brick
LAYOUT = ['LSB', 'SBL', 'BLS']


# ---------------- small geometry helpers ----------------
def obox(P, cn, x0, x1, y0, y1, z0, z1, sx, sy, sz, ground=False, sy_front=None):
    """axis-aligned box (12 tris), slot per face direction (sy_front overrides the -Y face)"""
    v = [P.bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    fs = [P.face([v[0], v[2], v[3], v[1]], sz), P.face([v[4], v[5], v[7], v[6]], sz),
          P.face([v[0], v[1], v[5], v[4]], sy if sy_front is None else sy_front), P.face([v[2], v[6], v[7], v[3]], sy),
          P.face([v[0], v[4], v[6], v[2]], sx), P.face([v[1], v[3], v[7], v[5]], sx)]
    P.comp.append((cn, fs, ground))
    return fs


def hexa(cx, cz, r, y, a0=0.0, n=6):
    return [Vector((cx + r * math.cos(a0 + 2 * math.pi * k / n), y, cz + r * math.sin(a0 + 2 * math.pi * k / n))) for k in range(n)]


def hole_cone(P, cx, cz, y, r, depth, faces, a0=math.pi / 6):
    """6-gon hole loop in the plane y (front face) + recessed cone (6 tris, slot 8). Returns the loop verts."""
    hl = [P.bm.verts.new(p) for p in hexa(cx, cz, r, y, a0)]
    apex = P.bm.verts.new((cx, y + depth, cz))
    for k in range(6): faces.append(P.face([hl[k], hl[(k + 1) % 6], apex], HOLE))
    return hl


# ---------------- structure ----------------
def frame(P):
    """one closed shell: outer box with the open front recess (frame boards + back board), slot 1"""
    bm = P.bm
    O = lambda y: [bm.verts.new(p) for p in ((-FX, y, Z0), (FX, y, Z0), (FX, y, ZT), (-FX, y, ZT))]
    I = lambda y: [bm.verts.new(p) for p in ((-XI, y, ZI0), (XI, y, ZI0), (XI, y, ZI1), (-XI, y, ZI1))]
    of, ob, inf, inb = O(-FY), O(FY), I(-FY), I(BACK_IN)
    fs = []
    for k in range(4):
        k1 = (k + 1) % 4
        fs.append(P.face([of[k], of[k1], ob[k1], ob[k]], WOOD_D))        # outer sides
        fs.append(P.face([of[k], inf[k], inf[k1], of[k1]], WOOD_D))      # front ring
        fs.append(P.face([inf[k], inb[k], inb[k1], inf[k1]], WOOD_D))    # inner walls
    fs.append(P.face(list(ob), WOOD_D)); fs.append(P.face(list(inb), WOOD_D))
    P.comp.append(('Frame', fs, False))


def legs(P):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x1 = sx * (FX - LEG_IN); x0 = x1 - sx * LEG_W
            y1 = sy * (FY - LEG_IN); y0 = y1 - sy * LEG_W
            obox(P, 'Legs', min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), 0.0, Z0 + 0.01, WOOD_D, WOOD_D, WOOD_D, ground=True)


def dividers(P):
    for sx in (-1, 1):                                   # uprights (fronts 4 mm behind the shelves' fronts)
        xc = sx * (XI - CELL_W - DIV / 2)
        obox(P, 'Dividers', xc - DIV / 2, xc + DIV / 2, -FY + 0.014, BACK_IN + 0.007, ZI0 - 0.005, ZI1 + 0.005, WOOD_D, WOOD_D, WOOD_D)
    for r in (1, 2):                                     # shelves
        z = CZ0[r] - DIV
        obox(P, 'Dividers', -XI - 0.005, XI + 0.005, -FY + 0.010, BACK_IN + 0.004, z, z + DIV, WOOD_D, WOOD_D, WOOD_D)


def roof_section():
    """chevron (Y, Z) of the two roof boards as one shell; underside sits 2 mm into the frame top at the frame front/back"""
    tp = math.tan(PITCH)
    zu0 = ZT - 0.002 + FY * tp                           # underside at the ridge line
    zt0 = zu0 + ROOF_T / math.cos(PITCH)                 # top surface at the ridge line
    ye = FY + OVER                                       # eave (underside) distance from the centre
    n = Vector((math.sin(PITCH), math.cos(PITCH)))       # back slope outward normal (Y, Z); front slope mirrored
    ub = Vector((ye, zu0 - ye * tp)); tb = ub + n * ROOF_T
    uf = Vector((-ye, zu0 - ye * tp)); tf = uf + Vector((-n.x, n.y)) * ROOF_T
    sec = [uf, tf, Vector((0.0, zt0)), tb, ub, Vector((0.0, zu0))]
    return sec, zt0


def roof(P):
    sec, zt0 = roof_section()
    rings = [[Vector((x, p.x, p.y)) for p in sec] for x in (-ROOF_X, ROOF_X)]
    P.loft('Roof', rings, lambda j, k: WOOD if k in (1, 2) else WOOD_M, WOOD_M, WOOD_M)
    obox(P, 'Ridge', -ROOF_X + 0.005, ROOF_X - 0.005, -RIDGE_W / 2, RIDGE_W / 2, zt0 - 0.014, zt0 + RIDGE_H, WOOD_D, WOOD_D, WOOD_D)
    return zt0 + RIDGE_H


# ---------------- cell fillings ----------------
LOG_A = (CELL_W - 0.002) / 4                          # pointy-top hexagon apothem (2 side by side + 1 nested on top)
LOG_R = LOG_A * 2 / math.sqrt(3)                       # vertex radius (log 0.062 across flats, honeycomb pile 3.5 R high)
A_LOG = math.pi / 2                                    # vertex up


def log(P, cn, cx, cz, yf, holed):
    """6-sided log end-on (axis Y) from the front cap yf to 5 mm into the back board; holed -> slot-0 end with a 6-gon hole"""
    F = [P.bm.verts.new(p) for p in hexa(cx, cz, LOG_R, yf, A_LOG)]
    B = [P.bm.verts.new(p) for p in hexa(cx, cz, LOG_R, BACK_IN + 0.005, A_LOG)]
    fs = [P.face([F[k], F[(k + 1) % 6], B[(k + 1) % 6], B[k]], WOOD_D) for k in range(6)]
    fs.append(P.face(list(reversed(B)), WOOD_M))
    if holed:
        hl = hole_cone(P, cx, cz, yf, 0.012, 0.045, fs, a0=A_LOG)
        fs += fill(P, [F, hl], WOOD, (0, -1, 0))
    else:
        fs.append(P.face(list(F), WOOD_M))
    P.comp.append((cn, fs, False))


def logs(P, tag, cx, z0, var):
    """3 logs as a honeycomb: 2 on the floor (bottom vertex 2 mm in the floor, side faces overlapping 1.5 mm), 1 nested
    on top (on the 60 deg faces, 1.7 mm embedded) - no coplanar contact faces"""
    zb = z0 - 0.002 + LOG_R; d = LOG_A - 0.00075
    holes = ((True, False, True), (False, True, True), (True, True, False))[var]
    fronts = ((-0.150, -0.143, -0.147), (-0.143, -0.150, -0.146), (-0.148, -0.144, -0.151))[var]
    log(P, f'Logs.{tag}.L', cx - d, zb, fronts[0], holes[0])
    log(P, f'Logs.{tag}.R', cx + d, zb, fronts[1], holes[1])
    log(P, f'Logs.{tag}.T', cx, zb + 1.5 * LOG_R - 0.0017, fronts[2], holes[2])


def brick(P, tag, cx, z0):
    """one brick block per cell: front slot 6 with 2 x 3 recessed 6-gon holes, other faces slot 14"""
    bw, bh, yf = 0.115, 0.115, -FY - 0.006
    x0, x1, za, zb = cx - bw / 2, cx + bw / 2, z0 - 0.001, z0 - 0.001 + bh
    fs = obox(P, f'Bricks.{tag}', x0, x1, yf, BACK_IN + 0.005, za, zb, BRICK, BRICK, BRICK)
    front = fs[2]; loop = list(front.verts); P.bm.faces.remove(front); fs.remove(front)
    hls = []
    zc = (za + zb) / 2
    for dz in (-0.022, 0.022):
        for dx in (-0.034, 0.0, 0.034):
            hls.append(hole_cone(P, cx + dx, zc + dz, yf, 0.0125, 0.050, fs))
    fs += fill(P, [loop] + hls, BRICK_F, (0, -1, 0))


STRAW_H = ((0.112, 0.126, 0.103, 0.121, 0.109), (0.119, 0.105, 0.125, 0.110, 0.122), (0.106, 0.123, 0.114, 0.104, 0.124))
STRAW_LEAN = (-0.004, -0.002, 0.0, 0.002, 0.004)
STRAW_DY = (0.0, -0.006, 0.004, -0.003, 0.002)


def straw(P, tag, cx, z0, var):
    """5 upright tapered 4-sided stalks (0.021 x 0.03, top 80 %) standing on the cell floor, slight fan-out lean"""
    w, d = 0.021, 0.030
    for i in range(5):
        x = cx + (i - 2) * 0.0245; yf = -FY + 0.002 + STRAW_DY[(i + var) % 5]
        h = STRAW_H[var][i]; lean = STRAW_LEAN[i]
        def ring(z, s, dx):
            return [Vector((x + dx + sx * w / 2 * s, yf + d / 2 + sy * d / 2 * s, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        P.loft(f'Straw.{tag}.{i}', [ring(z0 - 0.002, 1.0, 0.0), ring(z0 + h, 0.8, lean)], STRAW, STRAW, CREAM)


def build_hotel():
    P = Part('Body')
    frame(P); legs(P); dividers(P); top = roof(P)
    for row, s in enumerate(LAYOUT):                     # row 0 = top
        r = 2 - row
        for c, kind in enumerate(s):
            tag = f'r{row}c{c}'
            if kind == 'L': logs(P, tag, CX[c], CZ0[r], (row + c) % 3)
            elif kind == 'B': brick(P, tag, CX[c], CZ0[r])
            else: straw(P, tag, CX[c], CZ0[r], row)
    return P, top


# ---------------- assembly ----------------
def clear_own():
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    sc = bpy.context.scene
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    if bpy.app.background and not LIVE:                              # factory-startup scene: drop the default cube/light/camera
        for o in list(sc.objects):
            if o.name not in coll.all_objects: bpy.data.objects.remove(o, do_unlink=True)
    return coll


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


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp:
        k = nm.split('.')[0]; out[k] = out.get(k, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def size_report(ob, top):
    pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'  SIZE X {hi[0] - lo[0]:.3f} (spec 0.60) Y(depth) {hi[1] - lo[1]:.3f} (spec 0.30) Z {hi[2] - lo[2]:.3f} '
          f'(ridge top {top:.3f}) | centre x {(lo[0] + hi[0]) / 2:.4f} y {(lo[1] + hi[1]) / 2:.4f} | min z {lo[2]:.4f}')
    print(f'  frame 0.54 x 0.28 x {ZT - Z0:.3f} (z {Z0:.3f}..{ZT:.3f}); cells {CELL_W:.4f} x {CELL_H:.3f}; legs {LEG_W} x {LEG_H}')
    lp = [p for p in pts if p.z < 1e-6]
    print(f'  ground contact: {len(lp)} verts at z=0 (4 legs x 4 expected), x {min(p.x for p in lp):.3f}..{max(p.x for p in lp):.3f} '
          f'y {min(p.y for p in lp):.3f}..{max(p.y for p in lp):.3f}')


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P, top = build_hotel(); tris = part_tris(P)
    skip = tuple(nm for nm, _, _ in P.comp if nm.split('.')[0] in ('Logs', 'Bricks', 'Straw'))
    print(f'== {NAME}  components {len(P.comp)}')
    ob = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root, mirror_skip=skip)
    bpy.context.view_layer.update()
    tot = pc.report({'Body': ob})
    print('  tris per part:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f}')
    pc.coplanar_overlaps(ob)
    size_report(ob, top)
    return coll, root, ob, img, mat, tot


def geom_dump(ob, path):
    me = ob.data; uv = me.uv_layers.active.data
    vs = sorted(tuple(round(c, 5) for c in (ob.matrix_world @ v.co)) for v in me.vertices)
    fs = sorted((tuple(sorted(tuple(round(c, 5) for c in (ob.matrix_world @ me.vertices[i].co)) for i in p.vertices)),
                 tuple(round(c, 4) for c in uv[p.loop_start].uv)) for p in me.polygons)
    h = hashlib.sha1(json.dumps([vs, fs]).encode()).hexdigest()
    with open(path, 'w') as f: json.dump(dict(verts=len(vs), faces=len(fs), sha1=h), f)
    print('  geometry dump', path, len(vs), 'verts', len(fs), 'faces sha1', h)
    return h


# ---------------- renders (temporary scene: the open scene and its settings are not touched) ----------------
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_ORN04_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_ORN04_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_ORN04_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_ORN04_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_ORN04_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_ORN04_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_ORN04_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    target = Vector((0, 0, (min(p.z for p in pts) + max(p.z for p in pts)) / 2)); dv = Vector(view_dir).normalized()
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


def export_sel(coll, root, fbx):
    """pc.export changes the selection of the open view layer: save it and restore it afterwards (live)"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx


VIEW_REF = (0.36, -1.0, 0.36)                               # reference: front-right ~20 deg yaw, ~19 deg above
VIEW_PREVIEW = (0.85, -1.25, 0.75)                          # series preview 3/4 from the front-right (~25 deg)

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, root, ob, img, mat, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root, ob]
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs, os.path.join(CHECK_DIR, f'ORN-04_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.66, fill_h=0.87, lens=50)
        render(objs, os.path.join(CHECK_DIR, f'ORN-04_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'ORN-04_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs, os.path.join(CHECK_DIR, f'ORN-04_back_{tag}.png'), (-1.0, 0.9, 0.35), res=(800, 800), fill_w=0.7, fill_h=0.85)
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_sel(coll, root, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        pc.save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump(ob, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
