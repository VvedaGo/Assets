# build.py - ORN-02 Garden gnome statuette (FMS_Garden_Gnome + _Blue), pack CottageGardenDecor (Cottage Garden Decor),
# atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- ORN-02 build|export|verify
#   build  = build both models + printed checks + check renders to %TEMP%/assetnew_check/ORN-02/
#   export = build + 2 FBX (base, _Blue; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, for the live/headless comparison)
#   verify = only re-import the 2 FBX in art/
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\ORN-02_Gnome\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['ORN-02', 'build']})
#   Live mode touches only the collection ORN-02_Gnome and its child collection ORN-02_Gnome_Blue.
# Axes (Blender): X = right, -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y). Pivot: centre between the boots on
# the ground. No LOD (catalogue).
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'ORN-02')
NAME = 'FMS_Garden_Gnome'
PREVIEW = 'FMS_Garden_ORN_02_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 600, '_Blue': 600}
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
WOOD_D, CREAM, RED, WHITE, IRON, BLUE = 1, 3, 5, 10, 13, 15
SLOTS = {'':      dict(boots=WOOD_D, coat=BLUE, belt=IRON, skin=CREAM, beard=WHITE, hat=RED),
         '_Blue': dict(boots=WOOD_D, coat=RED, belt=IRON, skin=CREAM, beard=WHITE, hat=BLUE)}
COLL = 'ORN-02_Gnome'
VARIANTS = ('_Blue',)
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'ORN-02'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/ORN-02.3d.md; reference planning/CottageGardenDecor/references/ORN-02.png, see notes.md) ----
N = 8                                          # round parts < 0.3 m: 8 segments
# boots: plan rect, toe toward -Y (front); top ring inset = chamfer
BOOT_CX, BOOT_HW = 0.042, 0.0375               # centres x +-0.042, width 0.075 (gap 0.009 between the boots)
BOOT_Y0, BOOT_Y1 = -0.095, 0.025               # toe .. heel (length 0.12, toe 7 mm in front of the coat hem)
BOOT_Z1, BOOT_Z2, BOOT_CH = 0.026, 0.056, 0.014  # straight sides to z1, chamfer to the top z2 (6 mm inside the coat)
# body (coat): 8-sided loft, [z, apothem]; belt = painted band between the belt rings (flush, reference)
COAT = [(0.050, 0.088), (0.085, 0.083), (0.110, 0.080), (0.155, 0.075), (0.222, 0.058)]
BELT_BAND = 1                                  # band index between COAT[1] and COAT[2]
BELLY_RING, BELLY_PUSH = 3, 0.012              # the 3 front vertices of the belly ring pushed forward
# head (mostly hidden under hat and beard): 8-sided loft
HEAD = [(0.195, 0.045), (0.225, 0.056), (0.256, 0.048)]
# hat: 8-sided cone, [z, apothem, dy (backwards = +Y)], brim band 0.012 high, apex point on top
HAT = [(0.245, 0.088, 0.0), (0.257, 0.088, 0.0), (0.330, 0.058, 0.010), (0.395, 0.032, 0.027), (0.435, 0.015, 0.045)]
HAT_APEX = (0.0, 0.050, 0.450)
# arms: 6-sided sleeves along shoulder -> elbow -> wrist (+X side, mirrored), apothem per point
ARM = [((0.045, 0.000, 0.200), 0.031), ((0.091, 0.006, 0.150), 0.029), ((0.064, -0.084, 0.133), 0.025)]
HAND_C, HAND_R = (0.056, -0.094, 0.133), 0.024
NOSE_C, NOSE_R = (0.0, -0.112, 0.238), 0.027
ICO_SUB = 2                                    # bmesh subdivisions 2 = 80 facets (1 is a bare 20-face icosahedron)
# beard: outline in XZ (right half, top -> tip), back plane y, front ring scaled about its centre, front apex
BEARD_HALF = [(0.064, 0.252), (0.076, 0.215), (0.068, 0.175), (0.048, 0.138), (0.024, 0.112)]
BEARD_TIP = (0.0, 0.098)
BEARD_YB, BEARD_YF, BEARD_SCALE, BEARD_CZ = -0.030, -0.097, 0.82, 0.190
BEARD_RIDGE = ((0.0, -0.118, 0.212), (0.0, -0.114, 0.150))   # front ridge: upper, lower
BEARD_SPLIT = 0.185                            # front vertices above -> upper ridge vertex, below -> lower
H_TOTAL = HAT_APEX[2]


def ring8(z, apo, dy=0.0, n=N, phase=0.5):
    """n-gon ring, a flat face toward -Y (front) with phase 0.5"""
    rc = apo / math.cos(math.pi / n)
    return [Vector((rc * math.cos(-math.pi / 2 + (k + phase) * 2 * math.pi / n),
                    dy + rc * math.sin(-math.pi / 2 + (k + phase) * 2 * math.pi / n), z)) for k in range(n)]


# ---------------- parts ----------------
def boots(P, s):
    for sx in (-1, 1):
        cx = sx * BOOT_CX
        def rect(z, d):
            x0, x1 = cx - BOOT_HW + d, cx + BOOT_HW - d; y0, y1 = BOOT_Y0 + d, BOOT_Y1 - d
            return [Vector((x0, y0, z)), Vector((x1, y0, z)), Vector((x1, y1, z)), Vector((x0, y1, z))]
        P.loft('Boots', [rect(0.0, 0.0), rect(BOOT_Z1, 0.0), rect(BOOT_Z2, BOOT_CH)], s['boots'], s['boots'], s['boots'],
               ground=True)


def coat(P, s):
    rings = [ring8(z, a) for z, a in COAT]
    for k, v in enumerate(rings[BELLY_RING]):
        if v.y < -0.01: v.y -= BELLY_PUSH * (1.0 if abs(v.x) < 0.02 else 0.6)
    P.loft('Coat', rings, lambda j, k: s['belt'] if j == BELT_BAND else s['coat'], s['coat'], s['coat'])


def head(P, s):
    P.loft('Head', [ring8(z, a) for z, a in HEAD], s['skin'], s['skin'], s['skin'])


def hat(P, s):
    rings = [ring8(z, a, dy) for z, a, dy in HAT]
    R = P.loft('Hat', rings, s['hat'], s['hat'], None)
    ap = P.bm.verts.new(HAT_APEX); top = R[-1]; fs = []
    for k in range(N):
        fs.append(P.face([top[k], top[(k + 1) % N], ap], s['hat']))
    P.comp[-1][1].extend(fs)


def arm_rings(side):
    """6-sided sleeve rings along the polyline; the elbow ring is mitred (scaled by 1/cos of the half bend angle)"""
    pts = [Vector((side * p[0], p[1], p[2])) for p, _ in ARM]; out = []
    for i, (p, apo) in enumerate(zip(pts, [a for _, a in ARM])):
        if i == 0: t = (pts[1] - pts[0]).normalized(); sc = 1.0
        elif i == len(pts) - 1: t = (pts[-1] - pts[-2]).normalized(); sc = 1.0
        else:
            a = (p - pts[i - 1]).normalized(); b = (pts[i + 1] - p).normalized(); t = (a + b).normalized()
            sc = 1.0 / max(0.5, math.cos(a.angle(b) / 2))
        _, e1, e2 = pc.basis(t, (0, 0, 1))
        rc = apo / math.cos(math.pi / 6)
        ring = [p + (e1 * math.cos(2 * math.pi * k / 6 + math.pi / 6) * sc + e2 * math.sin(2 * math.pi * k / 6 + math.pi / 6)) * rc
                for k in range(6)]
        out.append(ring)
    return out


def arms(P, s):
    for side in (1, -1):
        rings = arm_rings(side)
        if side < 0: rings = [list(reversed(r)) for r in rings]
        P.loft('Arms', rings, s['coat'], s['coat'], s['coat'])


def ico(P, cname, c, r, slot):
    """faceted icosphere, rotated 90 deg about Z (the bmesh icosphere is Y-symmetric, the pack checks X)"""
    ret = bmesh.ops.create_icosphere(P.bm, subdivisions=ICO_SUB, radius=r,
                                     matrix=Matrix.Translation(c) @ Matrix.Rotation(math.pi / 2, 4, 'Z'), calc_uvs=False)
    vs = set(ret['verts']); fs = [f for f in P.bm.faces if f.verts[0] in vs]
    for f in fs: f[P.slot] = slot
    P.comp.append((cname, fs, False))


def beard(P, s):
    half = BEARD_HALF
    # CCW seen from the front: start top-right going down the right side to the tip and up the left side
    outline = [(x, z) for x, z in half] + [BEARD_TIP] + [(-x, z) for x, z in reversed(half)]
    back = [P.bm.verts.new((x, BEARD_YB, z)) for x, z in outline]
    front = [P.bm.verts.new((x * BEARD_SCALE, BEARD_YF, BEARD_CZ + (z - BEARD_CZ) * BEARD_SCALE)) for x, z in outline]
    n = len(outline); fs = []
    for k in range(n):
        k1 = (k + 1) % n
        fs.append(P.face([back[k], back[k1], front[k1], front[k]], s['beard']))
    U, L = [P.bm.verts.new(v) for v in BEARD_RIDGE]       # vertical front ridge -> gem-like facets
    grp = [U if z >= BEARD_SPLIT else L for _, z in outline]
    for k in range(n):
        k1 = (k + 1) % n
        if grp[k] is grp[k1]: fs.append(P.face([front[k], front[k1], grp[k]], s['beard']))
        else: fs.append(P.face([front[k], front[k1], grp[k1], grp[k]], s['beard']))   # switch edge: quad to the ridge
    fs.append(P.face(list(reversed(back)), s['beard']))
    P.comp.append(('Beard', fs, False))


def build_gnome(s):
    P = Part('Body')
    boots(P, s); coat(P, s); head(P, s); hat(P, s); arms(P, s)
    for sx in (1, -1): ico(P, 'Hands', Vector((sx * HAND_C[0], HAND_C[1], HAND_C[2])), HAND_R, s['skin'])
    ico(P, 'Nose', Vector(NOSE_C), NOSE_R, s['skin'])
    beard(P, s)
    return P


# ---------------- assembly ----------------
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


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def contacts():
    """hands/nose/beard must touch body or head; the beard must cover the belly; nothing floats"""
    rows = []
    # hand: sleeve end (wrist) inside the hand sphere
    w = Vector(ARM[-1][0]); h = Vector(HAND_C)
    rows.append((f'wrist centre {tuple(round(c, 3) for c in w)} inside hand (dist {(w - h).length:.4f} < r {HAND_R})',
                 (w - h).length < HAND_R - 0.005))
    # hand sunk into the belly/beard: hand back point y vs coat front at that height (apothem ~0.077 + belly push)
    rows.append((f'hand back y {HAND_C[1] + HAND_R:.3f} behind the coat front (~-0.08)', HAND_C[1] + HAND_R > -0.08))
    # shoulder ring start inside the coat
    sh = Vector(ARM[0][0])
    rows.append((f'shoulder point x {sh.x} < coat apothem at z {sh.z} (~0.062)', sh.x + 0.005 < 0.062))
    # nose touches the beard front / hat brim: nose back y vs beard front plane
    rows.append((f'nose back y {NOSE_C[1] + NOSE_R:.3f} behind the beard front ring y {BEARD_YF}', NOSE_C[1] + NOSE_R > BEARD_YF))
    rows.append((f'beard top z {BEARD_HALF[0][1]} above the hat bottom {HAT[0][0]} (tucked under the hat)', BEARD_HALF[0][1] > HAT[0][0] + 0.003))
    rows.append((f'head top z {HEAD[-1][0]} inside the hat (> {HAT[0][0]})', HEAD[-1][0] > HAT[0][0] + 0.003))
    rows.append((f'head bottom z {HEAD[0][0]} inside the coat top {COAT[-1][0]}', HEAD[0][0] < COAT[-1][0] - 0.005))
    rows.append((f'boot top z {BOOT_Z2} above the coat hem {COAT[0][0]}', BOOT_Z2 > COAT[0][0] + 0.003))
    rows.append((f'hat tip ring width {2 * HAT[-1][1]:.3f} >= 0.03', 2 * HAT[-1][1] >= 0.03 - 1e-9))
    ok = True
    for t, g in rows:
        ok &= g; print(f'  CONTACT {t}: {"OK" if g else "FAIL"}')
    return ok


def all_coplanar(obs, tag):
    bm = bmesh.new()
    for o in obs:
        t = o.data.copy(); t.transform(o.matrix_world); bm.from_mesh(t); bpy.data.meshes.remove(t)
    me = bpy.data.meshes.new('TMP_ORN02_all_' + tag); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TMP_ORN02_all_' + tag, me)
    n, smp = pc.coplanar_overlaps(ob)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me)
    return n


def size_report(objs):
    """no SNAP contract for ORN-02 (free-standing decor); catalogue size 0.25 x 0.25 x 0.45, height must not exceed 0.45"""
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'  SIZE X {hi[0] - lo[0]:.4f} (cat 0.25) Y {hi[1] - lo[1]:.4f} (cat 0.25) Z {hi[2] - lo[2]:.4f} (cat 0.45)'
          f' | x {lo[0]:.4f}..{hi[0]:.4f} y {lo[1]:.4f}..{hi[1]:.4f} z {lo[2]:.4f}..{hi[2]:.4f}')
    ok = abs(hi[2] - 0.45) <= 1e-4 and abs(lo[2]) <= 1e-6 and hi[0] - lo[0] <= 0.25 + 1e-4 and hi[1] - lo[1] <= 0.25 + 1e-4
    print(f'  ground verts (z = 0): {sum(1 for p in pts if abs(p.z) < 1e-6)} (2 boots x 4)')
    print('  SIZE', 'OK' if ok else 'FAIL')
    return ok


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        P = build_gnome(SLOTS[suf]); tris = part_tris(P)
        if not suf: contacts()
        body = pc.to_object(P, asset, coll, mat, (0, 0, 0), root)
        obs = {'Body': body}
        bpy.context.view_layer.update()
        print(f'== {asset}')
        tot = pc.report(obs)
        print('  tris per component:', tris)
        print(f'  budget {BUDGET[suf]} ->', 'OK' if tot <= BUDGET[suf] else f'OVER x{tot / BUDGET[suf]:.2f}')
        for o in obs.values(): pc.coplanar_overlaps(o)
        print('  coplanar overlaps, all parts together:', all_coplanar(list(obs.values()), suf or 'base'))
        cells = sorted({cell_of(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
        if suf:                                     # same mesh as the base, only the UV cells differ
            same = [tuple(round(c, 6) for c in v.co) for v in body.data.vertices] == \
                   [tuple(round(c, 6) for c in v.co) for v in res[''][2]['Body'].data.vertices]
            print(f'  {suf}: same vertices as the base {same}; cells used {cells}')
        else:
            print(f'  base: cells used {cells}')
        size_report([root] + list(obs.values()))
        res[suf] = (coll, root, obs, [], tot)
    return colls, img, mat, res


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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4)):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_ORN02_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_ORN02_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_ORN02_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_ORN02_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_ORN02_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_ORN02_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_ORN02_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


def save_lib(path, colls, mat, img):
    data = set(colls) | {mat, img}
    for c in colls: data |= set(c.objects) | {o.data for o in c.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(asset, coll, root, fbx):
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    try:
        pc.export(asset, coll, root, fbx)
    finally:
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    return fbx


VIEW_REF = (0.30, -1.0, 0.22)                               # reference: front-right ~17 deg yaw, ~12 deg above
VIEW_PREVIEW = (0.85, -1.25, 0.75)                          # series preview 3/4 from the front-right (~25 deg)

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, o, e, t = res[suf]; return [r] + list(o.values())
    if MODE == 'build':
        tag = 'live' if LIVE else 'headless'
        render(objs_of(''), os.path.join(CHECK_DIR, f'ORN-02_ref_{tag}.png'), VIEW_REF, res=(1024, 1024), fill_w=0.62, fill_h=0.88)
        render(objs_of(''), os.path.join(CHECK_DIR, f'ORN-02_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'ORN-02_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_Blue'), os.path.join(CHECK_DIR, f'ORN-02_blue_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'ORN-02_back_{tag}.png'), (-0.6, 1.0, 0.45), res=(800, 800))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbxs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]
            fbxs.append(export_one(NAME + suf, c, r, os.path.join(ART, 'Meshes', NAME + suf + '.fbx')))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), colls, mat, img)
        render(objs_of(''), os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        for f in fbxs: pc.verify(f)
    if MODE in ('export', 'dump'):
        allobs = []
        for suf in ('',) + VARIANTS:
            c, r, o, e, t = res[suf]; allobs += list(o.values())
        geom_dump(allobs, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
