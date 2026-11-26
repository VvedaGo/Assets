# build.py - STR-02 Rose arch, wrought iron (FMS_Garden_Arch_Iron), pack CottageGardenDecor (Cottage Garden Decor), atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- STR-02 build|export|verify|mount
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/STR-02/
#   export = build + FBX (+ .fbm) + collection-only .blend + ONE preview + FBX re-import verify + geometry dump (JSON)
#   verify = only re-import the FBX in art/
#   mount  = build + check render with PLT-02 (x2) and PLT-03 imported from art/ at the Plant_* empties (read only)
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\CottageGardenDecor\STR-02_Arch_Iron\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['STR-02', 'build']})
#   Live mode touches only the collection STR-02_Arch_Iron (other objects, scenes and the owner's .blend stay as they are).
# Axes (Blender): X = across the opening (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: centre of the footprint on the ground. No LOD (catalogue). One palette slot: 13 wrought iron #3A3A3F.
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'CottageGardenDecor')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'STR-02')
NAME = 'FMS_Garden_Arch_Iron'
PREVIEW = 'FMS_Garden_STR_02_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = 1400                                # spec: scrolls may take it to ~2x with a note (target <= 1400)
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
IRON = 13
COLL = 'STR-02_Arch_Iron'
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part, ngon
from pack_shapes import path_sweep

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'STR-02'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/STR-02.3d.md; reference references/STR-02.png, see notes.md) ----
ROD = 0.020                                    # frame rod apothem: 8-sided, 0.040 across the flats (reference: uprights
                                               # ~1.8x the scroll bars; spec ~0.035, >= 0.03)
SROD = 0.015                                   # scroll bar apothem: 0.030 across (spec minimum; reference bars ~0.025)
ROD_X = 0.62                                   # upright centres: inner faces at +-0.600 -> clear passage 1.20 (as STR-01)
FRAME_Y = 0.20                                 # front / back frame planes (centre-lines)
Z_ROD0 = 0.11                                  # upright bottom (inside the foot collar)
Z_SPRING = 1.90                                # hoop springing = upright top
RISE = 0.50                                    # hoop rise (centre-line); semi-ellipse, flatter than half-round (reference)
HOOP_N = 12                                    # hoop segments
FOOT_TIP, FOOT_C0, FOOT_C1 = 0.0, 0.095, 0.130  # spike tip on the ground, collar 0.095-0.130
FOOT_A0, FOOT_A1 = 0.026, 0.032                # collar apothem bottom / top (inverted frustum, reference)
X_ROD = 0.0185                                 # cross-rod / spreader apothem (0.037 across: 1.5 mm off the frame faces)
HOOP_CROSS = (45, 90, 135)                     # cross-rods on the hoop at these ellipse angles (spec: crown and +-45)
Z_SPREAD = (0.30, 1.85)                        # side spreaders at the bottom (reference ~0.30) and under the springing
# scrolls: S = top curl (CCW spiral) + Hermite spine + bottom curl (CW spiral); both curls touch the upright
EMBED = 0.004                                  # scroll rod sunk 4 mm into the upright
CURL_SPAN, TIP_K = 290.0, 0.48                 # curl angle span (deg) and tip radius / outer radius (reference: full curls)
BIG = dict(R=0.044, dv=0.19, vt=1.28, curl_seg=7, spine_seg=2)      # outer S, one per upright (x up to ~0.74)
SMALL = dict(R=0.042, dv=0.13, vt=1.80, curl_seg=5, spine_seg=2)    # corner S inside each frame, under the springing
# finial on the crown: stub + 8-sided diamond, top at 2.50
FIN_A, FIN_Z0, FIN_Z1, FIN_ZW, FIN_AW, FIN_TOP = 0.011, 2.39, 2.432, 2.458, 0.024, 2.50


# ---------------- geometry helpers ----------------
def oct_sec(a):
    return ngon(a / math.cos(math.pi / 8), 8, math.pi / 8)          # flats normal to the section axes


def hoop_pt(t_deg, y):
    t = math.radians(t_deg)
    return Vector((ROD_X * math.cos(t), y, Z_SPRING + RISE * math.sin(t)))


def frame_path(y):
    pts = [Vector((-ROD_X, y, Z_ROD0))]
    pts += [hoop_pt(180 - 180 * k / HOOP_N, y) for k in range(HOOP_N + 1)]
    pts.append(Vector((ROD_X, y, Z_ROD0)))
    return pts


def foot(P, x, y):
    """8-sided spike: tip on the ground, cone up to an inverted-frustum collar, top cap (rod enters from above)"""
    bm = P.bm
    tip = bm.verts.new((x, y, FOOT_TIP))
    r0 = [bm.verts.new((x + u, y + v, FOOT_C0)) for u, v in oct_sec(FOOT_A0)]
    r1 = [bm.verts.new((x + u, y + v, FOOT_C1)) for u, v in oct_sec(FOOT_A1)]
    fs = [P.face([r0[(k + 1) % 8], r0[k], tip], IRON) for k in range(8)]
    fs += [P.face([r0[k], r0[(k + 1) % 8], r1[(k + 1) % 8], r1[k]], IRON) for k in range(8)]
    fs.append(P.face(r1, IRON))
    P.comp.append(('Foot', fs, True))


def straight_rod(P, cname, p0, p1, a, ref):
    p0, p1 = Vector(p0), Vector(p1)
    t = (p1 - p0).normalized(); e1 = (Vector(ref) - t * Vector(ref).dot(t)).normalized(); e2 = t.cross(e1)
    rings = [[c + e1 * u + e2 * v for u, v in oct_sec(a)] for c in (p0, p1)]
    P.loft(cname, rings, IRON, IRON, IRON)


def s_curve(R, dv, vt, curl_seg, spine_seg):
    """2D centre-line (u = away from the upright axis, v = up) of an S-scroll touching the upright with both curls"""
    span = math.radians(CURL_SPAN); rt = TIP_K * R
    rad = lambda frac: rt + (R - rt) * frac                         # frac 0 at the tip, 1 at the join with the spine
    u_l = ROD + SROD - EMBED                                             # leftmost centre-line u: rod sunk EMBED into the upright
    uct = u_l + R                                                    # top curl: leftmost point (theta 180, r = R) touches
    rb180 = rad(1 - math.pi / span)                                  # bottom curl radius at theta -180 (its leftmost point)
    ucb = u_l + rb180
    vb = vt - dv
    pts = []
    for k in range(curl_seg + 1):                                    # top curl, tip -> join (CCW, theta up to 180 deg)
        f = k / curl_seg; th = math.pi - span * (1 - f)
        pts.append((uct + rad(f) * math.cos(th), vt + rad(f) * math.sin(th)))
    P0, P1 = Vector((uct - R, vt)), Vector((ucb + R, vb)); T = Vector((0, -dv))
    for k in range(1, spine_seg):                                    # Hermite spine, vertical tangents at both ends
        s = k / spine_seg
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        q = P0 * h00 + T * h10 + P1 * h01 + T * h11; pts.append((q.x, q.y))
    for k in range(curl_seg + 1):                                    # bottom curl, join -> tip (CW, theta 0 -> -span)
        f = 1 - k / curl_seg; th = -span * (1 - f)
        pts.append((ucb + rad(f) * math.cos(th), vb + rad(f) * math.sin(th)))
    return pts


def s_clearance(pts, skip=0.075):
    """min distance between centre-line samples further apart than `skip` along the curve (self-touch check)"""
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + math.dist(a, b))
    best = 9.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if acc[j] - acc[i] > skip: best = min(best, math.dist(pts[i], pts[j]))
    return best


def scroll(P, cname, side, y, inward, cfg):
    """side +1/-1 = right/left upright; inward False = S on the outer side, True = inside the frame"""
    pts2 = s_curve(**cfg)
    sgn = side * (-1 if inward else 1)
    pts = [Vector((side * ROD_X + sgn * u, y, v)) for u, v in pts2]
    path_sweep(P, cname, pts, (0, 1, 0), oct_sec(SROD), IRON, IRON)
    return pts2


def finial(P):
    bm = P.bm; z = FIN_Z0
    rings = [[bm.verts.new((u, v, zz)) for u, v in oct_sec(a)] for zz, a in ((FIN_Z0, FIN_A), (FIN_Z1, FIN_A), (FIN_ZW, FIN_AW))]
    tip = bm.verts.new((0, 0, FIN_TOP))
    fs = [P.face(list(reversed(rings[0])), IRON)]
    for j in range(2):
        fs += [P.face([rings[j][k], rings[j][(k + 1) % 8], rings[j + 1][(k + 1) % 8], rings[j + 1][k]], IRON) for k in range(8)]
    fs += [P.face([rings[2][k], rings[2][(k + 1) % 8], tip], IRON) for k in range(8)]
    P.comp.append(('Finial', fs, False))


def build_arch():
    P = Part('Body')
    for y in (-FRAME_Y, FRAME_Y):                                    # 2 frames: upright + semi-elliptic hoop + upright
        path_sweep(P, 'Frame', frame_path(y), (0, 1, 0), oct_sec(ROD), IRON, IRON)
        for sx in (-1, 1): foot(P, sx * ROD_X, y)
    for t in HOOP_CROSS:                                             # cross-rods on the hoop (along Y, frame centre to centre)
        c = hoop_pt(t, 0); nrm = Vector((math.cos(math.radians(t)) / ROD_X, 0, math.sin(math.radians(t)) / RISE)).normalized()
        straight_rod(P, 'Cross', c - Vector((0, FRAME_Y, 0)), c + Vector((0, FRAME_Y, 0)), X_ROD, nrm)
    for sx in (-1, 1):                                               # side spreaders at the bottom and under the springing
        for z in Z_SPREAD:
            straight_rod(P, 'Spreader', (sx * ROD_X, -FRAME_Y, z), (sx * ROD_X, FRAME_Y, z), X_ROD, (1, 0, 0))
    clear = {}
    for y in (-FRAME_Y, FRAME_Y):
        for sx in (-1, 1):
            clear['big'] = s_clearance(scroll(P, 'Scroll_Side', sx, y, False, BIG))
            clear['small'] = s_clearance(scroll(P, 'Scroll_Corner', sx, y, True, SMALL))
    finial(P)
    return P, clear


# ---------------- scene / atlas ----------------
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
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 for f in fs)
    return out


def empties(asset, coll, root):
    """Plant_L / Plant_R on the outer faces of the uprights (side plane, like STR-01's post plane), Plant_Top on the crown"""
    out = []
    for nm, loc in (('Plant_L', (-(ROD_X + ROD), 0, 0)), ('Plant_R', (ROD_X + ROD, 0, 0)),
                    ('Plant_Top', (0, 0, Z_SPRING + RISE + ROD))):
        e = bpy.data.objects.new(asset + '_' + nm, None); e.empty_display_type = 'PLAIN_AXES'; e.empty_display_size = 0.15
        coll.objects.link(e); e.parent = root; e.location = loc; out.append(e)
    return out


def snap_report(body, ems):
    pts = [body.matrix_world @ v.co for v in body.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    # clear passage width below the corner scrolls: nearest vertex to the axis among |x| < 0.7, z in [0.15, corner bottom)
    z_corner = min(p.z for p in pts if abs(p.x) < ROD_X - ROD - 1e-4 and p.z > 1.0 and p.z < Z_SPRING)
    inner = min([ROD_X - ROD] + [abs(p.x) for p in pts if FOOT_C1 + 1e-4 < p.z < z_corner - 1e-4])
    collar = min(abs(p.x) for p in pts if p.z <= FOOT_C1 + 1e-4)
    print(f'  clear width between the foot collars (z <= {FOOT_C1}): {2 * collar:.4f}')
    rows = [('clear passage width (upright inner faces)', 2 * inner, 1.20, 'ge'),
            ('clear passage height under the corner scrolls', z_corner, 1.60, 'ge'),
            ('total width (fits the 1.5 m wall gap MOD-03/04)', hi[0] - lo[0], 1.50, 'le'),
            ('total depth (<= 0.5, wall pillar 0.5)', hi[1] - lo[1], 0.50, 'le'),
            ('total height (<= 2.5)', hi[2], 2.50, 'le'),
            ('min z (ground contact, spike tips)', lo[2], 0.0, 'eq')]
    ok = True
    for nm, got, want, how in rows:
        good = (got >= want - 1e-4) if how == 'ge' else (got <= want + 1e-4) if how == 'le' else abs(got - want) <= 1e-4
        ok &= good
        print(f'  SNAP {nm}: {got:.4f} (want {dict(ge="≥ ", le="≤ ", eq="")[how]}{want}) {"OK" if good else "FAIL"}')
    tips = sorted({(round(p.x, 4), round(p.y, 4)) for p in pts if abs(p.z) < 1e-6})
    print(f'  ground points (z = 0): {tips}')
    ok &= len(tips) == 4
    em = {o.name.split('_Plant_')[-1]: o.matrix_world.translation for o in ems}
    for k, want in (('L', (-(ROD_X + ROD), 0, 0)), ('R', (ROD_X + ROD, 0, 0)), ('Top', (0, 0, Z_SPRING + RISE + ROD))):
        got = em.get(k); good = got is not None and (got - Vector(want)).length <= 1e-4; ok &= good
        print(f'  SNAP empty Plant_{k}: {None if got is None else [round(x, 4) for x in got]} {"OK" if good else "FAIL"}')
    print('  SNAP', 'OK' if ok else 'FAIL')
    return ok


def build():
    coll = clear_own()
    img, mat = atlas_and_material()
    root = bpy.data.objects.new(NAME, None); coll.objects.link(root)
    P, clear = build_arch(); tris = part_tris(P)
    body = pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)
    ems = empties(NAME, coll, root)
    bpy.context.view_layer.update()
    print(f'== {NAME}')
    tot = pc.report({'Body': body})
    print('  tris per component:', tris)
    print(f'  budget {BUDGET} ->', 'OK' if tot <= BUDGET else f'OVER x{tot / BUDGET:.2f} (spec allows ~2x for scrolls with a note)')
    print(f'  scroll self-clearance (centre-lines, >= bar {2 * SROD:.3f} means no self-touch): big {clear["big"]:.4f} small {clear["small"]:.4f}')
    for nm, cfg in (('big', BIG), ('small', SMALL)):
        p2 = s_curve(**cfg); us = [u for u, v in p2]; vs = [v for u, v in p2]
        rt = TIP_K * cfg['R']; r0 = rt + (cfg['R'] - rt) * (1 - (math.pi / 2) / math.radians(CURL_SPAN))
        print(f'  scroll {nm}: u {min(us) - SROD:.4f}..{max(us) + SROD:.4f} (outer, from the upright axis) '
              f'v {min(vs) - SROD:.3f}..{max(vs) + SROD:.3f} | curl across (outer) {r0 + cfg["R"] + 2 * SROD:.3f} (>= 0.10)')
    pc.coplanar_overlaps(body)
    cells = sorted({pc_cell(body.data.uv_layers.active.data[p.loop_start].uv) for p in body.data.polygons})
    print('  atlas cells used', cells)
    snap_report(body, ems)
    return coll, img, mat, root, body, ems, tot


def pc_cell(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def geom_dump(obs, path):
    allv, allf = [], []
    for ob in obs:
        if ob.type == 'EMPTY':
            allv.append([ob.name, [round(c, 5) for c in ob.matrix_world.translation]]); allf.append([]); continue
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
    sc = bpy.data.scenes.new('TMP_STR02_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_STR02_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_STR02_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_STR02_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_STR02_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_STR02_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_STR02_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
    pts = [o.matrix_world @ v.co for o in objs if o.type == 'MESH' for v in o.data.vertices]
    if box: pts = [p for p in pts if all(box[0][i] <= p[i] <= box[1][i] for i in range(3))]   # close-up framing
    target = Vector(((min(p.x for p in pts) + max(p.x for p in pts)) / 2 if box else 0, 0,
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


def save_lib(path, coll, mat, img):
    data = {coll, mat, img} | set(coll.objects) | {o.data for o in coll.objects if o.data}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)


def export_one(coll, root, ems, fbx):
    """the empties carry the bare spec names Plant_L / Plant_R / Plant_Top inside the FBX (in Blender they are
    <asset>_Plant_* because names are unique per file); the selection and active object are restored afterwards"""
    sel = [(o, o.select_get()) for o in bpy.context.view_layer.objects]; act = bpy.context.view_layer.objects.active
    keys = [e.name.split('_Plant_')[-1] for e in ems]
    for e, k in zip(ems, keys): e.name = 'Plant_' + k
    names = [e.name for e in ems]
    try:
        pc.export(NAME, coll, root, fbx)
    finally:
        for e, k in zip(ems, keys): e.name = NAME + '_Plant_' + k
        for o, s in sel:
            try: o.select_set(s)
            except Exception: pass
        bpy.context.view_layer.objects.active = act
    print('  empties exported as', names)
    return fbx


def mount_check(objs, ems, out):
    """import PLT-02 (x2) and PLT-03 FBX (read only) at the Plant_* empties into a temporary collection, render, remove"""
    made = []
    def imp(fname, M):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=os.path.join(ART, 'Meshes', fname))
        new = [o for o in bpy.data.objects if o not in before]
        for o in new:
            if o.parent is None: o.matrix_world = M @ o.matrix_world
        made.extend(new)
    em = {o.name.split('_Plant_')[-1]: o.matrix_world.translation for o in ems}
    # PLT-02: back plane = its Blender Y 0, grows toward -Y -> turn it so it grows outward (away from the arch)
    imp('FMS_Garden_Rose_Climbing_Side.fbx', Matrix.Translation(em['L']) @ Matrix.Rotation(math.radians(-90), 4, 'Z'))
    imp('FMS_Garden_Rose_Climbing_Side.fbx', Matrix.Translation(em['R']) @ Matrix.Rotation(math.radians(90), 4, 'Z'))
    imp('FMS_Garden_Rose_Climbing_Top.fbx', Matrix.Translation(em['Top']))
    bpy.context.view_layer.update()
    for o in made:
        for c in list(o.users_collection): c.objects.unlink(o)
    render(objs + [o for o in made if o.type == 'MESH'], out, VIEW_REF, res=(1000, 1000), fill_w=0.8, fill_h=0.85, lens=50)
    for o in made:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)


VIEW_REF = (0.40, -0.86, 0.42)               # reference: 3/4 from the front-right (~25 deg), ~25 deg above (notes.md)
VIEW_PREVIEW = (0.85, -1.25, 0.75)           # series preview 3/4 from the front-right (~25 deg), as STR-01 / STR-06

if MODE == 'verify':
    pc.verify(os.path.join(ART, 'Meshes', NAME + '.fbx'))
else:
    coll, img, mat, root, body, ems, tot = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    objs = [root, body]
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs, os.path.join(CHECK_DIR, f'STR-02_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.80, fill_h=0.88, lens=50)
        render(objs, os.path.join(CHECK_DIR, f'STR-02_34_{tag}.png'), VIEW_PREVIEW)
        render(objs, os.path.join(CHECK_DIR, f'STR-02_front_{tag}.png'), (0, -1, 0.05), res=(1000, 1000), fill_w=0.8, fill_h=0.9, lens=0)
        render(objs, os.path.join(CHECK_DIR, f'STR-02_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs, os.path.join(CHECK_DIR, f'STR-02_scrolls_{tag}.png'), (0, -1, 0.0), res=(700, 1000), fill_w=0.9, fill_h=0.9,
               lens=0, box=((-0.80, -0.30, 0.95), (-0.45, 0.30, 1.95)))
    if MODE == 'mount':
        mount_check(objs, ems, os.path.join(CHECK_DIR, f'STR-02_mount_{tag}.png'))
    if MODE == 'export':
        for sub in ('Meshes', 'Blend', 'Previews'): os.makedirs(os.path.join(ART, sub), exist_ok=True)
        fbx = export_one(coll, root, ems, os.path.join(ART, 'Meshes', NAME + '.fbx'))
        save_lib(os.path.join(ART, 'Blend', NAME + '.blend'), coll, mat, img)
        render(objs, os.path.join(ART, 'Previews', PREVIEW), VIEW_PREVIEW)
        pc.verify(fbx)
    if MODE in ('export', 'dump'):
        geom_dump([body] + ems, os.path.join(CHECK_DIR, 'geom_live.json' if LIVE else 'geom_headless.json'))
