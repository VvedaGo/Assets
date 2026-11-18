# STA-02 Screw cheese press -> FMS_Workshop_STA_02 (Farm Processing pack). Idempotent: rebuilds only its own collection.
# Run inside Blender: MODE = 'build' | 'export' (build + export + reimport verify + lib .blend); exec(open(__file__).read())
import bpy, bmesh, math, os, shutil
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_02'
TEX_NAME = 'T_FarmProcessing_STA02_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA02'
MODE = globals().get('MODE', 'build')

# ---------------- palette (4x4 cells, 64 px each, solid) ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#B5835A', '#B5835A', '#B5835A']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B = range(13)

# ---------------- dimensions (m) ----------------
TT_X, TT_Y, TT_Z0, TT_Z1 = 0.44, 0.29, 0.31, 0.38          # table top half-sizes and z range
LEG_TOP_C, LEG_FOOT_C, LEG_TOP_S, LEG_FOOT_S = (0.34, 0.20), (0.39, 0.25), 0.095, 0.12
RAIL_Z = 0.13
POST_X, POST_S, POST_TOP = 0.31, 0.11, 1.04
BEAM_Z0, BEAM_Z1, BEAM_D = 0.89, 0.97, 0.085
NUT_W, NUT_D, NUT_Z0, NUT_Z1 = 0.17, 0.13, 0.845, 1.0
MOULD_Z1, MOULD_AO, MOULD_AI, STAVES = 0.67, 0.235, 0.205, 14
PLATE_R, PLATE_Z0, PLATE_Z1, PLATE_N = 0.2, 0.64, 0.695, 16
COLLAR_R, COLLAR_Z1 = 0.056, 0.745
SP_R, SP_r, SP_Z0, SP_Z1, PITCH, TILT = 0.036, 0.026, 0.73, 1.11, 0.04, 0.016
HUB_R, HUB_Z0, HUB_Z1 = 0.06, 1.095, 1.165
BAR_Z, BAR_HALF, BAR_R = 1.13, 0.24, 0.026
KNOB_X, KNOB_L, KNOB_R = 0.285, 0.09, 0.05
CAP_R, CAP_Z0, CAP_Z1 = 0.042, 1.155, 1.20
SCREW_PIVOT_Z = (NUT_Z0 + NUT_Z1) / 2

# ---------------- geometry helpers ----------------
def ngon(r, n, a0=0.0):
    return [(r * math.cos(a0 + 2 * math.pi * k / n), r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]

def chamf_rect(w, h, c):
    a, b = w / 2, h / 2
    return [(a - c, -b), (a, -b + c), (a, b - c), (a - c, b), (-a + c, b), (-a, b - c), (-a, -b + c), (-a + c, -b)]

def inset(poly, d):
    """offset a convex CCW polygon inwards by d (true parallel offset)"""
    if d == 0: return list(poly)
    n = len(poly); out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1 = (p1 - p0).normalized(); e2 = (p2 - p1).normalized()
        n1 = Vector((e1.y, -e1.x)); n2 = Vector((e2.y, -e2.x))          # outward normals for CCW
        m = n1 + n2; k = d / max(1e-6, (1 + n1.dot(n2)))
        q = p1 - m * k
        out.append((q.x, q.y))
    return out

class Part:
    """collects components (name -> list of faces) in one bmesh, world coordinates"""
    def __init__(self, name):
        self.name = name; self.bm = bmesh.new(); self.comp = []; self.slot = self.bm.faces.layers.int.new('slot')
    def face(self, vs, slot):
        f = self.bm.faces.new(vs); f[self.slot] = slot; return f
    def loft(self, cname, rings, side, cap0, cap1, closed_profile=True, ground=False):
        """rings: list of vertex-coordinate lists; side: slot or fn(band, k) -> slot"""
        bm = self.bm; R = [[bm.verts.new(p) for p in r] for r in rings]; faces = []
        n = len(R[0])
        for j in range(len(R) - 1):
            for k in range(n if closed_profile else n - 1):
                k1 = (k + 1) % n
                s = side(j, k) if callable(side) else side
                faces.append(self.face([R[j][k], R[j][k1], R[j + 1][k1], R[j + 1][k]], s))
        if cap0 is not None: faces.append(self.face(list(reversed(R[0])), cap0))
        if cap1 is not None: faces.append(self.face(list(R[-1]), cap1))
        self.comp.append((cname, faces, ground))
        return R
    def torus_loft(self, cname, rings, side):
        bm = self.bm; R = [[bm.verts.new(p) for p in r] for r in rings]; faces = []
        n = len(R[0]); m = len(R)
        for j in range(m):
            for k in range(n):
                faces.append(self.face([R[j][k], R[j][(k + 1) % n], R[(j + 1) % m][(k + 1) % n], R[(j + 1) % m][k]],
                                       side(j, k) if callable(side) else side))
        self.comp.append((cname, faces, False))

def basis(axis, ref):
    t = Vector(axis).normalized(); r = Vector(ref)
    e1 = (r - t * r.dot(t)).normalized(); e2 = t.cross(e1)
    return t, e1, e2

def sweep(part, cname, p0, p1, prof, spec, side, cap0, cap1, ref=(1, 0, 0), flat0=False, ground=False):
    """prof 2D (along e1, e2); spec [(t, scale, inset_m)] rings along p0->p1"""
    p0, p1 = Vector(p0), Vector(p1); t, e1, e2 = basis(p1 - p0, ref)
    rings = []
    for tt, s, d in spec:
        c = p0.lerp(p1, tt); pr = inset([(x * s, y * s) for x, y in prof], d)
        ring = [c + e1 * x + e2 * y for x, y in pr]
        if flat0 and tt == 0.0:
            ring = [v - t * (v.z / t.z) for v in ring]
        rings.append(ring)
    return part.loft(cname, rings, side, cap0, cap1, ground=ground)

def zprism(part, cname, cx, cy, prof, zspec, side, cap0, cap1, ground=False):
    """vertical prism; zspec [(z, inset_m)]"""
    rings = [[Vector((cx + x, cy + y, z)) for x, y in inset(prof, d)] for z, d in zspec]
    return part.loft(cname, rings, side, cap0, cap1, ground=ground)

def chamf_spec(L, c0, c1, mid=()):
    s = [(0.0, 1.0, c0)] if c0 else []
    s += [(c0 / L if c0 else 0.0, 1.0, 0.0)] + [(m, 1.0, 0.0) for m in mid] + [(1 - c1 / L if c1 else 1.0, 1.0, 0.0)]
    if c1: s.append((1.0, 1.0, c1))
    return s

# ---------------- parts ----------------
def build_frame():
    P = Part('Frame')
    # table top: plan with chamfered corners, chamfered top/bottom edges
    tp = chamf_rect(2 * TT_X, 2 * TT_Y, 0.035)
    zprism(P, 'top', 0, 0, tp, [(TT_Z0, 0.008), (TT_Z0 + 0.008, 0), (TT_Z1 - 0.014, 0), (TT_Z1, 0.014)], WOOD, WOOD, WOOD)
    # legs: splayed, tapered (wider foot), flat foot on z=0, top inside the table
    for sx in (-1, 1):
        for sy in (-1, 1):
            foot = (sx * LEG_FOOT_C[0], sy * LEG_FOOT_C[1], 0.0); top = (sx * LEG_TOP_C[0], sy * LEG_TOP_C[1], TT_Z0 + 0.03)
            k = LEG_TOP_S / LEG_FOOT_S
            sweep(P, 'leg', foot, top, chamf_rect(LEG_FOOT_S, LEG_FOOT_S, 0.012), [(0.0, 1.0, 0.0), (1.0, k, 0.0)],
                  WOOD, WOOD_M, WOOD, flat0=True, ground=True)
    # stretchers at RAIL_Z, ending at the leg centre lines
    t = RAIL_Z / (TT_Z0 + 0.03)
    lx = LEG_FOOT_C[0] + (LEG_TOP_C[0] - LEG_FOOT_C[0]) * t; ly = LEG_FOOT_C[1] + (LEG_TOP_C[1] - LEG_FOOT_C[1]) * t
    rp = chamf_rect(0.055, 0.05, 0.008)
    for sy in (-1, 1):
        sweep(P, 'rail_x', (-lx, sy * ly, RAIL_Z), (lx, sy * ly, RAIL_Z), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    for sx in (-1, 1):
        sweep(P, 'rail_y', (sx * lx, -ly, RAIL_Z - 0.01), (sx * lx, ly, RAIL_Z - 0.01), rp, [(0, 1, 0), (1, 1, 0)], WOOD, WOOD, WOOD, ref=(0, 0, 1))
    # red caps on the front/back faces above the legs
    cp = chamf_rect(0.055, 0.055, 0.007)
    zc = (TT_Z0 + TT_Z1) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * (TT_Y - 0.004); y1 = sy * (TT_Y + 0.012)
            sweep(P, 'redcap', (sx * (TT_X - 0.07), y0, zc), (sx * (TT_X - 0.07), y1, zc), cp, [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.004)],
                  RED, RED, RED, ref=(0, 0, 1))
    # posts with pyramid-chamfered tops
    pp = chamf_rect(POST_S, POST_S, 0.012)
    for sx in (-1, 1):
        zprism(P, 'post', sx * POST_X, 0, pp, [(TT_Z1 - 0.02, 0), (POST_TOP - 0.035, 0), (POST_TOP, 0.026)], WOOD, WOOD, WOOD)
    # braces (XZ boards outside the posts)
    po = POST_X + POST_S / 2
    for sx in (-1, 1):
        poly = [(po - 0.005, TT_Z1 + 0.13), (po + 0.012, TT_Z1 - 0.005), (TT_X - 0.002, TT_Z1 - 0.005), (po - 0.005, TT_Z1 + 0.32)]
        if sx < 0: poly = [(-x, z) for x, z in reversed(poly)]
        rings = [[Vector((x, y, z)) for x, z in poly] for y in (-0.045, 0.045)]
        P.loft('brace', rings, WOOD, WOOD, WOOD)
    # crossbeam
    bp = chamf_rect(BEAM_Z1 - BEAM_Z0, BEAM_D, 0.01)
    sweep(P, 'beam', (-POST_X, 0, (BEAM_Z0 + BEAM_Z1) / 2), (POST_X, 0, (BEAM_Z0 + BEAM_Z1) / 2), bp, [(0, 1, 0), (1, 1, 0)],
          WOOD, WOOD, WOOD, ref=(0, 0, 1))
    # hex bolts on the post front/back faces
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * (POST_S / 2 - 0.004); y1 = sy * (POST_S / 2 + 0.02)
            sweep(P, 'bolt', (sx * POST_X, y0, (BEAM_Z0 + BEAM_Z1) / 2), (sx * POST_X, y1, (BEAM_Z0 + BEAM_Z1) / 2), ngon(0.035, 6, math.pi / 2),
                  [(0, 1, 0), (0.6, 1, 0), (1, 1, 0.009)], METAL, METAL, METAL, ref=(0, 0, 1))
    # nut block on the beam
    npf = chamf_rect(NUT_W, NUT_D, 0.026)
    zprism(P, 'nut', 0, 0, npf, [(NUT_Z0, 0.01), (NUT_Z0 + 0.012, 0), (NUT_Z1 - 0.016, 0), (NUT_Z1, 0.014)], METAL, METAL, METAL)
    return P

def build_screw():
    P = Part('Screw')
    # threaded spindle: flat end rings + tilted crest/root rings (reads as a slanted thread)
    n = 8; ang = [2 * math.pi * k / n + math.pi / 8 for k in range(n)]
    def ring(z, r, tilt):
        return [Vector((r * math.cos(a), r * math.sin(a), z + tilt * math.cos(a))) for a in ang]
    rings = [ring(SP_Z0, SP_r, 0.0)]
    z = SP_Z0 + TILT + 0.006; i = 0; slots = []
    while z < SP_Z1 - TILT - 0.006:
        rings.append(ring(z, SP_R if i % 2 == 0 else SP_r, TILT)); z += PITCH / 2; i += 1
    rings.append(ring(SP_Z1, SP_r, 0.0))
    P.loft('spindle', rings, lambda j, k: METAL if j % 2 == 0 else METAL_D, METAL, METAL)
    # hub (red octagon), bar (dark wood, thicker towards the ends), knobs (red octagons), hex cap (metal)
    oc = ngon(HUB_R, 8, math.pi / 8)
    zprism(P, 'hub', 0, 0, oc, [(HUB_Z0, 0.012), (HUB_Z0 + 0.012, 0), (HUB_Z1 - 0.012, 0), (HUB_Z1, 0.012)], RED, RED, RED)
    bar = ngon(BAR_R, 8, math.pi / 8)
    sweep(P, 'bar', (-BAR_HALF, 0, BAR_Z), (BAR_HALF, 0, BAR_Z), bar,
          [(0, 1.05, 0), (0.36, 0.8, 0), (0.64, 0.8, 0), (1, 1.05, 0)], WOOD_D, WOOD_D, WOOD_D, ref=(0, 0, 1))
    kn = ngon(KNOB_R, 8, math.pi / 8)
    for sx in (-1, 1):
        a = (sx * (KNOB_X - KNOB_L / 2), 0, BAR_Z); b = (sx * (KNOB_X + KNOB_L / 2), 0, BAR_Z)
        sweep(P, 'knob', a, b, kn, chamf_spec(KNOB_L, 0.012, 0.016), RED, RED, RED, ref=(0, 0, 1))
    zprism(P, 'cap', 0, 0, ngon(CAP_R, 6, 0.0), [(CAP_Z0, 0), (CAP_Z1 - 0.012, 0), (CAP_Z1, 0.01)], METAL, METAL, METAL)
    return P

def build_plate():
    P = Part('Plate')
    pl = ngon(PLATE_R, PLATE_N, math.pi / PLATE_N)
    zprism(P, 'plate', 0, 0, pl, [(PLATE_Z0, 0.006), (PLATE_Z0 + 0.006, 0), (PLATE_Z1 - 0.012, 0), (PLATE_Z1, 0.012)], METAL, METAL, METAL_L)
    zprism(P, 'collar', 0, 0, ngon(COLLAR_R, 6, 0.0), [(PLATE_Z1 - 0.01, 0), (COLLAR_Z1 - 0.01, 0), (COLLAR_Z1, 0.01)], METAL, METAL, METAL)
    return P

def build_mould():
    P = Part('Mould')
    d = 2 * math.pi / STAVES; gap = 0.0006; ch = 0.008
    for k in range(STAVES):
        c = -math.pi / 2 + k * d; a, b = c - d / 2, c + d / 2
        ro = MOULD_AO / math.cos(d / 2); ri = MOULD_AI / math.cos(d / 2)
        ua, ub = Vector((math.cos(a), math.sin(a))), Vector((math.cos(b), math.sin(b)))
        na, nb = Vector((-ua.y, ua.x)), Vector((-ub.y, ub.x))                 # side-face normals (CCW tangent)
        fa = (ub * ro - ua * ro).normalized()
        pts = [ua * ri + na * gap, ua * (ro - ch) + na * gap, ua * ro + fa * ch + na * gap * 0,
               ub * ro - fa * ch, ub * (ro - ch) - nb * gap, ub * ri - nb * gap]
        pts2 = [(p.x, p.y) for p in pts]
        rings = [[Vector((x, y, z)) for x, y in pts2] for z in (TT_Z1, MOULD_Z1)]
        sides = {0: CREAM_D, 1: CREAM_D, 2: CREAM if k % 2 == 0 else CREAM_B, 3: CREAM_D, 4: CREAM_D, 5: CREAM_IN}
        P.loft('stave', rings, lambda j, kk: sides[kk], CREAM_IN, CREAM)
    # hoops: 14-gon bands aligned with the stave faces, rectangular section
    for zc in (TT_Z1 + 0.30 * (MOULD_Z1 - TT_Z1), TT_Z1 + 0.73 * (MOULD_Z1 - TT_Z1)):
        h = 0.04; aoi, aoo = MOULD_AO - 0.004, MOULD_AO + 0.009
        def hring(apo, z):
            r = apo / math.cos(d / 2)
            return [Vector((r * math.cos(-math.pi / 2 + (k + 0.5) * d), r * math.sin(-math.pi / 2 + (k + 0.5) * d), z)) for k in range(STAVES)]
        P.torus_loft('hoop', [hring(aoi, zc - h / 2), hring(aoo, zc - h / 2), hring(aoo, zc + h / 2), hring(aoi, zc + h / 2)], METAL_D)
        for k in range(0, STAVES, 2):
            c = -math.pi / 2 + k * d; u = Vector((math.cos(c), math.sin(c), 0))
            p0 = Vector((0, 0, zc)) + u * (aoo - 0.003); p1 = Vector((0, 0, zc)) + u * (aoo + 0.012)
            sweep(P, 'rivet', p0, p1, ngon(0.014, 6, math.pi / 2), [(0, 1, 0), (1, 0.72, 0)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    return P

# ---------------- atlas / material ----------------
def cell_uv(slot):
    col, row = slot % 4, slot // 4
    return ((col + 0.5) / 4, 1 - (row + 0.5) / 4)

def atlas_image():
    path = os.path.join(ART, 'Textures', TEX_NAME)
    img = bpy.data.images.get(TEX_NAME)
    if img is None:
        img = bpy.data.images.new(TEX_NAME, 256, 256, alpha=False)
    rgb = [tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) for h in PAL]
    px = []
    for y in range(256):
        row = 3 - y // 64
        for x in range(256):
            px.extend(rgb[row * 4 + x // 64] + (1.0,))
    img.pixels.foreach_set(px)
    img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    img.filepath = path; img.reload()
    return img

def material(img):
    m = bpy.data.materials.get(MAT_NAME) or bpy.data.materials.new(MAT_NAME)
    m.use_nodes = True; nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    for nd in [nd for nd in nt.nodes if nd.type == 'TEX_IMAGE']: nt.nodes.remove(nd)
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.interpolation = 'Closest'
    nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.0; bsdf.inputs['Roughness'].default_value = 0.75
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
    return m

# ---------------- checks ----------------
def comp_checks(P):
    bm = P.bm; bm.verts.index_update()
    allpos = [v.co.copy() for v in bm.verts]
    vc = {}
    for ci, (_, faces, _) in enumerate(P.comp):
        for f in faces:
            for v in f.verts: vc[v.index] = ci
    worst = (0.0, ''); bad = []
    for ci, (nm, faces, ground) in enumerate(P.comp):
        vs = {v for f in faces for v in f.verts}
        if ground and abs(min(v.co.z for v in vs)) > 1e-6: bad.append((nm, 'ground', round(min(v.co.z for v in vs), 5)))
        others = [f for f in bm.faces if vc[f.verts[0].index] != ci]
        if not others: continue
        bo = BVHTree.FromPolygons(allpos, [[v.index for v in f.verts] for f in others])
        bc = BVHTree.FromPolygons(allpos, [[v.index for v in f.verts] for f in faces])
        dd = 0.0 if bc.overlap(bo) else min(bo.find_nearest(v.co)[3] for v in vs)
        if dd > worst[0]: worst = (dd, nm)
        if dd > 1e-4: bad.append((nm, 'gap', round(dd, 5)))
    kd = kdtree.KDTree(len(bm.verts))
    for v in bm.verts: kd.insert(v.co, v.index)
    kd.balance()
    mir = max(kd.find(Vector((-v.co.x, v.co.y, v.co.z)))[2] for v in bm.verts)
    nm_ = sum(1 for e in bm.edges if not e.is_manifold); loose = sum(1 for v in bm.verts if not v.link_faces)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    print(f'  {P.name}: non-manifold {nm_} loose {loose} degenerate {deg} mirrorX {mir:.6f} worst gap {worst[0]:.5f} {worst[1]} problems {bad}')

def to_object(P, coll, mat, pivot, root):
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    comp_checks(P)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    for v in bm.verts: v.co -= Vector(pivot)
    me = bpy.data.meshes.new(NAME + '_' + P.name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(NAME + '_' + P.name, me); coll.objects.link(ob)
    ob.parent = root; ob.location = pivot
    return ob

def clear_collection():
    coll = bpy.data.collections.get(NAME)
    if coll is None:
        coll = bpy.data.collections.new(NAME); bpy.context.scene.collection.children.link(coll)
    bsc = bpy.data.scenes.get(NAME + '_Build') or bpy.data.scenes.new(NAME + '_Build')   # clean view/render scene (user's Cube stays untouched)
    if coll.name not in bsc.collection.children: bsc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and d.users == 0 and isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    return coll

def build():
    coll = clear_collection()
    img = atlas_image(); mat = material(img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.3; coll.objects.link(root)
    obs = {}
    for P, piv in ((build_frame(), (0, 0, 0)), (build_screw(), (0, 0, SCREW_PIVOT_Z)),
                   (build_plate(), (0, 0, (PLATE_Z0 + PLATE_Z1) / 2)), (build_mould(), (0, 0, TT_Z1))):
        obs[P.name] = to_object(P, coll, mat, piv, root)
    bpy.context.view_layer.update()
    tot = 0
    for k, o in obs.items():
        t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
        print(f'  {o.name}: tris {t} dims {[round(x, 3) for x in o.dimensions]} pivot {[round(x, 3) for x in o.matrix_world.translation]}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    print(f'TOTAL tris {tot} | size X {dims[0]:.3f} Y {dims[1]:.3f} Z {dims[2]:.3f} | min z {min(p.z for p in pts):.4f}')
    # cross-part contacts
    def zr(o):
        zs = [(o.matrix_world @ v.co).z for v in o.data.vertices]; return min(zs), max(zs)
    def rr(o):
        return max(math.hypot(*(o.matrix_world @ v.co).xy) for v in o.data.vertices)
    pz, mz = zr(obs['Plate']), zr(obs['Mould'])
    print('  plate in mould: plate z', [round(x, 3) for x in pz], 'mould top', round(mz[1], 3),
          'plate R', round(PLATE_R, 3), '< mould inner apothem', MOULD_AI * 1.0, 'mould base == table top', round(mz[0], 4), TT_Z1)
    print('  spindle through nut: thread z', (SP_Z0, SP_Z1), 'nut z', (NUT_Z0, NUT_Z1), 'spindle R', SP_R, '< nut half', NUT_D / 2,
          '| spindle bottom in collar', SP_Z0, 'in', (PLATE_Z1, COLLAR_Z1))
    print('  mould vs posts clearance (m)', round(POST_X - POST_S / 2 - (MOULD_AO + 0.009) / math.cos(math.pi / STAVES), 4))
    return obs, root, coll, img, mat

OBS, ROOTOB, COLL, IMG, MAT = build()

# ---------------- export + verify ----------------
def export():
    fbx = os.path.join(ART, 'Meshes', NAME + '.fbx')
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in COLL.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = ROOTOB
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z', axis_up='Y', bake_space_transform=True, object_types={'EMPTY', 'MESH'},
        mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, path_mode='COPY',
        embed_textures=False, bake_anim=False)
    print('exported', fbx)
    return fbx

def verify(fbx):
    win = bpy.context.window; prev = win.scene
    sc = bpy.data.scenes.new('TMP_FBXVerify'); win.scene = sc
    before_m, before_i, before_mat = set(bpy.data.meshes), set(bpy.data.images), set(bpy.data.materials)
    bpy.ops.import_scene.fbx(filepath=fbx)
    bpy.context.view_layer.update()
    obs = list(sc.objects)
    print('VERIFY objects', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
            pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler], 'scale', [round(s, 4) for s in o.scale])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    for o in obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    for m in set(bpy.data.materials) - before_mat:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in imgs:
        if i.users == 0: bpy.data.images.remove(i)
    win.scene = prev; bpy.data.scenes.remove(sc)
    print('  temp cleanup done; scenes', [s.name for s in bpy.data.scenes])

def save_lib():
    path = os.path.join(ART, 'Blend', NAME + '.blend')
    data = {COLL} | set(COLL.objects) | {o.data for o in COLL.objects if o.data} | {MAT, IMG}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)

if MODE == 'export':
    _fbx = export(); verify(_fbx); save_lib()
