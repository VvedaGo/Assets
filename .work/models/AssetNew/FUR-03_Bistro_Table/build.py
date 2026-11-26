# build.py - FUR-03 Wrought-iron bistro table (FMS_Garden_Bistro_Table + _White), pack AssetNew (Cottage Garden Decor),
# atlas A Garden_Build.
# Headless:
#   set PYTHONUTF8=1 & set PYTHONDONTWRITEBYTECODE=1
#   blender.exe --background --factory-startup --python build.py -- FUR-03 build|export|verify|dump
#   build  = build + printed checks + check renders to %TEMP%/assetnew_check/FUR-03/
#   export = build + 2 FBX (base, _White; each with its .fbm) + collection-only .blend + ONE preview (base)
#            + FBX re-import verify + geometry dump (JSON, SHA1 for the live/headless comparison)
#   verify = only re-import the FBX files in art/
#   dump   = build + geometry dump only
# Live (MCP execute_blender_code):
#   p = r'<repo>\.work\models\AssetNew\FUR-03_Bistro_Table\build.py'
#   exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, 'LIVE_ARGS': ['FUR-03', 'build']})
#   Live mode touches only the collection FUR-03_Bistro_Table and its child FUR-03_Bistro_Table_White.
# Axes (Blender): X = right (Unity X), -Y = front (Unity +Z, FBX -Z forward), Z = up (Unity Y).
# Pivot: centre of the footprint on the ground. No LOD (catalogue). One palette slot: 13 wrought iron (_White: 10).
#
# Shared iron helpers for FUR-04 (Bistro_Chair), same wording as STR-02 (Arch_Iron):
#   oct_sec(a, n=8)       n-sided rod section (FUR-03 uses n = 6), apothem a (flats normal to the section axes)
#   plane_pt(phi, u, v)   point in the vertical radial plane at azimuth phi: u = outward from the axis, v = up
#   rod_rings(pts, up, sec) mitred rings along a polyline (copy of pack_shapes.path_sweep without the loft)
#   foot_leg(...)         S-leg: Hermite from a hub to a vertical drop + outward foot curl (spiral), touching the ground
#   s_scroll(...)         S-scroll: bottom curl (CCW) + Hermite spine + top curl (CW), 2D centre-line
#   s_clearance(pts)      self-clearance of a centre-line (>= bar width = no self-touch)
import bpy, bmesh, math, os, sys, json, hashlib
from mathutils import Vector, Matrix

# ---------------- CONFIG ----------------
HERE = os.path.dirname(os.path.abspath(globals().get('__file__', '')))
REPO = os.environ.get('PACK_REPO') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TOOLS = os.environ.get('PACK_TOOLS') or os.path.join(REPO, 'Tools', 'blender')
ART = os.environ.get('PACK_ART') or os.path.join(REPO, 'art', 'AssetNew')
CHECK_DIR = os.path.join(os.environ.get('TEMP', '.'), 'assetnew_check', 'FUR-03')
NAME = 'FMS_Garden_Bistro_Table'
PREVIEW = 'FMS_Garden_FUR_03_Preview.png'
ATLAS_TEX = 'FMS_Garden_AtlasA.png'          # shared atlas A (Garden_Build) - READ ONLY here
ATLAS_MAT = 'M_Garden_Build'
BUDGET = {'': 1000, '_White': 1000}     # coordinator 2026-11-25: option C, 500 -> 1000 (2.0x, STR-02 ratio)
PAL_A = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
         '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
         '#6E757B', '#A9AFB4', '#EEEDE7', '#C9C3B6',
         '#A7A39A', '#3A3A3F', '#9C3F33', '#4A78A8']
IRON, WHITE = 13, 10
VARIANTS = ('_White',)
COLL = 'FUR-03_Bistro_Table'
# ----------------------------------------
sys.dont_write_bytecode = True                # no __pycache__ inside Tools/ (read-only shared helpers)
sys.path.insert(0, TOOLS)
import pack_common as pc
from pack_common import Part, ngon

LIVE = 'LIVE_ARGS' in globals()
ARGS = globals().get('LIVE_ARGS') or (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
ID = ARGS[0] if ARGS else 'FUR-03'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'

# ---- dimensions (spec prompts/FUR-03.3d.md; reference references/FUR-03.png measured in notes.md) ----
TOP_N = 12                                     # 12-sided top, a flat facing the front (-Y)
TOP_AF = 0.70                                  # top across the flats (footprint 0.70 x 0.70)
TOP_Z0, TOP_Z1, FIELD_Z = 0.70, 0.75, 0.737    # top slab bottom / rim top (total height) / recessed field
RIM_W = 0.030                                  # rim width (across the flats)
RING_AF0, RING_AF1, RING_Z0 = 0.46, 0.42, 0.66  # underside ring: across flats at the top / bottom, bottom z (top = TOP_Z0)
HUB_N, HUB_AF, HUB_Z0, HUB_Z1 = 6, 0.12, 0.40, 0.46   # hex hub, flats toward the legs (spec 8-sided; -8 tris for the budget)
LEG_A = 0.018                                  # leg rod apothem: 6-sided, 0.036 across the flats (spec ~0.035, >= 0.03)
SROD = 0.015                                   # scroll bar apothem: 0.030 across (STR-02 scroll bars)
EMBED = 0.004                                  # rods sunk 4 mm into their supports
LEG_AZ = (90.0, 210.0, 330.0)                  # legs: one to the back, two to the front sides (reference)
SCROLL_AZ = LEG_AZ                             # scrolls stand above the legs (reference; spec said "between")
FOOT_MAX = 0.347                               # outermost foot curl point (radius): feet stay inside the 0.70 top
LEG_R, LEG_SPAN, LEG_TIP = 0.055, 300.0, 0.42  # foot curl outer radius, angle span, tip radius / R
LEG_DROP = FOOT_MAX - LEG_A - LEG_R * (2 - (1 - LEG_TIP) * 180 / LEG_SPAN)   # vertical drop radius (spec r ~0.28)
LEG = dict(u0=0.030, v0=0.415, t0=(0.30, -0.30), drop=LEG_DROP, t1=0.40, spine_seg=4,
           R=LEG_R, span=LEG_SPAN, tip_k=LEG_TIP, curl_seg=8)
ROD_N = 6                                      # all iron rods 6-sided (coordinator option C; STR-02 used 8)
SCR = dict(u_in=0.025, R=0.045, span=290.0, tip_k=0.45, seg_b=4, seg_t=5, spine_seg=1, du=0.020)


# ---------------- shared iron helpers (FUR-04 reuses them) ----------------
def oct_sec(a, n=8):
    return ngon(a / math.cos(math.pi / n), n, math.pi / n)          # flats normal to the section axes


def plane_pt(phi_deg, u, v):
    p = math.radians(phi_deg)
    return Vector((u * math.cos(p), u * math.sin(p), v))


def plane_normal(phi_deg):
    p = math.radians(phi_deg)
    return Vector((-math.sin(p), math.cos(p), 0))


def rod_rings(pts, up, sec):
    """mitred rings along an open polyline (pack_shapes.path_sweep without the loft, so the rings can be moved first)"""
    up = Vector(up); rings = []; n = len(pts)
    for i, c in enumerate(pts):
        d1 = (c - pts[i - 1]).normalized() if i > 0 else None
        d2 = (pts[i + 1] - c).normalized() if i < n - 1 else None
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


def foot_leg(u0, v0, t0, drop, t1, spine_seg, R, span, tip_k, curl_seg, rod):
    """2D centre-line (u outward, v up) of an S-leg: Hermite from (u0, v0) (inside the hub, tangent t0) down to a vertical
    drop at u = drop, then an outward foot curl (CCW spiral from its inner side, radius R -> tip_k R over `span` deg).
    v is returned with the curl's lowest centre-line sample at v = rod (bar bottom on the ground before the exact shift)."""
    rt = tip_k * R; uc = drop + R
    curl = []
    for k in range(curl_seg + 1):
        f = k / curl_seg; th = math.radians(180 + span * f); r = R - (R - rt) * f
        curl.append(Vector((uc + r * math.cos(th), r * math.sin(th))))
    lift = rod - min(p.y for p in curl)
    curl = [p + Vector((0, lift)) for p in curl]
    P1 = curl[0]
    spine = hermite((u0, v0), t0, P1, (0, -t1), spine_seg)
    return [Vector((u0, v0))] + spine + curl


def s_scroll(u_in, R, span, tip_k, seg_b, seg_t, spine_seg, du, v_bot, v_top, bar):
    """2D centre-line of an S-scroll between a support below (bar bottom at v_bot) and above (bar top at v_top):
    bottom curl CCW (tip -> outer side going up), Hermite spine, top curl CW (inner side going up -> tip).
    u_in = innermost centre-line u of the bottom curl; du = spine offset outward (S lean)."""
    span_r = math.radians(span); rt = tip_k * R
    rb = lambda th: rt + (R - rt) * (1 - abs(th) / span_r)              # bottom curl: th in [-span, 0]
    rtp = lambda th: R - (R - rt) * ((math.pi - th) / span_r)            # top curl: th in [pi - span, pi]
    ub = u_in + rb(-math.pi)
    bot = [(th, rb(th)) for th in (-span_r * (1 - k / seg_b) for k in range(seg_b + 1))]
    vb = v_bot - min(r * math.sin(th) for th, r in bot) + bar - EMBED
    ut = ub + R + du + R
    top = [(th, rtp(th)) for th in (math.pi - span_r * k / seg_t for k in range(seg_t + 1))]
    vt = v_top - max(r * math.sin(th) for th, r in top) - bar + EMBED
    pts = [Vector((ub + r * math.cos(th), vb + r * math.sin(th))) for th, r in bot]
    pts += hermite(pts[-1], (0, vt - vb), (ut - R, vt), (0, vt - vb), spine_seg)
    pts += [Vector((ut + r * math.cos(th), vt + r * math.sin(th))) for th, r in top]
    return pts


def s_clearance(pts, skip=0.075):
    """min distance between centre-line samples further apart than `skip` along the curve (self-touch check)"""
    acc = [0.0]
    for a, b in zip(pts, pts[1:]): acc.append(acc[-1] + (b - a).length)
    best = 9.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if acc[j] - acc[i] > skip: best = min(best, (pts[i] - pts[j]).length)
    return best


# ---------------- table ----------------
def top_and_ring(P, slot):
    """one solid of revolution: recessed field, rim, slab edge, underside ring (12-sided, flat to the front)"""
    a0 = math.pi / TOP_N + math.pi / 2                              # a flat faces -Y (vertices at 270 +- 15 deg)
    rc = lambda af: af / 2 / math.cos(math.pi / TOP_N)              # across flats -> circumradius
    R = rc(TOP_AF); Ri = rc(TOP_AF - 2 * RIM_W)
    prof = [(Ri, FIELD_Z), (Ri, TOP_Z1), (R, TOP_Z1), (R, TOP_Z0), (rc(RING_AF0), TOP_Z0), (rc(RING_AF1), RING_Z0)]
    rings = [[Vector((x, y, z)) for x, y in ngon(r, TOP_N, a0)] for r, z in prof]
    P.loft('Top', rings, slot, slot, slot)


def hub(P, slot):
    rc = HUB_AF / 2 / math.cos(math.pi / HUB_N)
    rings = [[Vector((x, y, z)) for x, y in ngon(rc, HUB_N, 0.0)] for z in (HUB_Z0, HUB_Z1)]   # corners at 0/60/.. deg: flats face the legs
    P.loft('Hub', rings, slot, slot, slot)


def build_table(slot):
    P = Part('Body')
    top_and_ring(P, slot)
    hub(P, slot)
    leg2d = foot_leg(rod=LEG_A, **LEG)
    for phi in LEG_AZ:
        rings = rod_rings([plane_pt(phi, u, v) for u, v in leg2d], plane_normal(phi), oct_sec(LEG_A, ROD_N))
        dz = min(p.z for r in rings for p in r)
        rings = [[p - Vector((0, 0, dz)) for p in r] for r in rings]              # exact ground contact
        P.loft('Leg', rings, slot, slot, slot, ground=True)
    scr2d = s_scroll(v_bot=HUB_Z1, v_top=RING_Z0, bar=SROD, **SCR)
    for phi in SCROLL_AZ:
        rings = rod_rings([plane_pt(phi, u, v) for u, v in scr2d], plane_normal(phi), oct_sec(SROD, ROD_N))
        P.loft('Scroll', rings, slot, slot, slot)
    return P, leg2d, scr2d


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


def part_tris(P):
    out = {}
    for nm, fs, _ in P.comp: out[nm] = out.get(nm, 0) + sum(len(f.verts) - 2 if len(f.verts) <= 4 else len(f.verts) - 2 for f in fs)
    return out


def cell_of(uv):
    col = min(3, int(uv[0] * 4)); row = min(3, int((1 - uv[1]) * 4)); return row * 4 + col


def size_report(body, leg2d):
    pts = [body.matrix_world @ v.co for v in body.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    ok = True
    rows = [('width X (<= 0.70)', hi[0] - lo[0], 0.70, 'le'), ('depth Y (<= 0.70)', hi[1] - lo[1], 0.70, 'le'),
            ('height (= 0.75, table top)', hi[2], 0.75, 'eq'), ('min z (ground contact)', lo[2], 0.0, 'eq')]
    for nm, got, want, how in rows:
        good = (got <= want + 1e-4) if how == 'le' else abs(got - want) <= 1e-4
        ok &= good
        print(f'  SIZE {nm}: {got:.4f} (want {"≤ " if how == "le" else ""}{want}) {"OK" if good else "FAIL"}')
    ground = [p for p in pts if abs(p.z) < 1e-6]
    feet = {}
    for p in ground: feet.setdefault(round(math.degrees(math.atan2(p.y, p.x))) % 360, []).append(p)
    print(f'  ground verts (z = 0): {len(ground)}; per foot azimuth:',
          {k: (len(v), round(sum(math.hypot(p.x, p.y) for p in v) / len(v), 3)) for k, v in sorted(feet.items())})
    ok &= len(feet) >= 3
    fp = [p for p in pts if p.z < 0.12]
    print(f'  foot footprint x {min(p.x for p in fp):.3f}..{max(p.x for p in fp):.3f} '
          f'y {min(p.y for p in fp):.3f}..{max(p.y for p in fp):.3f} (inside the top 0.70 x 0.70)')
    print('  SIZE', 'OK' if ok else 'FAIL')
    return ok


def build():
    colls = clear_own()
    img, mat = atlas_and_material()
    res = {}
    for suf, coll in zip(('',) + VARIANTS, colls):
        asset = NAME + suf
        root = bpy.data.objects.new(asset, None); coll.objects.link(root)
        P, leg2d, scr2d = build_table(WHITE if suf else IRON); tris = part_tris(P)
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
            print(f'  base: cells used {cells}')
            print(f'  leg self-clearance {s_clearance(leg2d):.4f} (>= {2 * LEG_A:.3f}); '
                  f'scroll self-clearance {s_clearance(scr2d):.4f} (>= {2 * SROD:.3f})')
            lu = [p.x for p in leg2d]; su = [p.x for p in scr2d]; sv = [p.y for p in scr2d]
            print(f'  leg u {min(lu):.3f}..{max(lu) + LEG_A:.3f} | foot curl across {max(lu[-LEG["curl_seg"] - 1:]) - min(lu[-LEG["curl_seg"] - 1:]) + 2 * LEG_A:.3f} (>= 0.10)')
            nb = SCR['seg_b'] + 1; nt = SCR['seg_t'] + 1
            print(f'  scroll u {min(su) - SROD:.3f}..{max(su) + SROD:.3f} v {min(sv) - SROD:.3f}..{max(sv) + SROD:.3f} | '
                  f'bottom curl across {max(su[:nb]) - min(su[:nb]) + 2 * SROD:.3f}, top curl across '
                  f'{max(su[-nt:]) - min(su[-nt:]) + 2 * SROD:.3f} (>= 0.10)')
            size_report(body, leg2d)
        res[suf] = (coll, root, body, tot)
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
def render(objs, out, view_dir, res=(1280, 800), fill_w=0.62, fill_h=0.9, lens=70, bg=(0xC8, 0xCC, 0xD4), box=None):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.data.scenes.new('TMP_FUR03_Render')
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    tc = bpy.data.collections.new('TMP_FUR03_Objects'); sc.collection.children.link(tc)
    for o in objs: tc.objects.link(o)
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_FUR03_World'); w.use_nodes = True; nt = w.node_tree
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
    sun('TMP_FUR03_Sun', (40, 0, -35), 3.2, (1, 0.96, 0.88))
    sun('TMP_FUR03_Fill', (65, 0, 150), 0.8, (0.9, 0.93, 1.0), False)
    cd = bpy.data.cameras.new('TMP_FUR03_Cam')
    if lens: cd.lens = lens
    else: cd.type = 'ORTHO'; cd.ortho_scale = 1.0
    cam = bpy.data.objects.new('TMP_FUR03_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; tmp.append(cam)
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


VIEW_REF = (0.0, -1.0, 0.31)                  # reference: straight from the front, ~17 deg above (top ellipse 0.30), back leg behind the hub
VIEW_PREVIEW = (0.85, -1.25, 0.75)           # series preview 3/4 from the front-right (~25 deg), as STR-02 / STR-07

if MODE == 'verify':
    for suf in ('',) + VARIANTS: pc.verify(os.path.join(ART, 'Meshes', NAME + suf + '.fbx'))
else:
    colls, img, mat, res = build()
    os.makedirs(CHECK_DIR, exist_ok=True)
    def objs_of(suf): c, r, b, t = res[suf]; return [r, b]
    tag = 'live' if LIVE else 'headless'
    if MODE == 'build':
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-03_ref_{tag}.png'), VIEW_REF, res=(1254, 1254), fill_w=0.66, fill_h=0.80, lens=50)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-03_34_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-03_thumb_{tag}.png'), VIEW_PREVIEW, res=(128, 128), fill_w=0.85, fill_h=0.85)
        render(objs_of('_White'), os.path.join(CHECK_DIR, f'FUR-03_white_{tag}.png'), VIEW_PREVIEW)
        render(objs_of(''), os.path.join(CHECK_DIR, f'FUR-03_side_{tag}.png'), (1, 0, 0.0), res=(1000, 1000), fill_w=0.85, fill_h=0.85, lens=0)
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
