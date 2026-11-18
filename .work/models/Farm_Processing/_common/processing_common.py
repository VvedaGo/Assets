# Shared helpers for Farm Processing procedural builds (extracted from STA02 build_cheese_press.py, which stays standalone).
# Usage in a build script (inside Blender):
#   import sys, importlib; sys.path.insert(0, COMMON_DIR); import processing_common as pc; importlib.reload(pc)
import bpy, bmesh, math, os
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

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
        n1 = Vector((e1.y, -e1.x)); n2 = Vector((e2.y, -e2.x))
        m = n1 + n2; k = d / max(1e-6, (1 + n1.dot(n2)))
        q = p1 - m * k
        out.append((q.x, q.y))
    return out

class Part:
    """collects components (name -> list of faces) in one bmesh, world coordinates; face int layer 'slot' = palette cell"""
    def __init__(self, name):
        self.name = name; self.bm = bmesh.new(); self.comp = []; self.slot = self.bm.faces.layers.int.new('slot')
    def face(self, vs, slot):
        f = self.bm.faces.new(vs); f[self.slot] = slot; return f
    def loft(self, cname, rings, side, cap0, cap1, closed_profile=True, ground=False):
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

def rect_prism(part, cname, cx, cy, w, h, c, zspec, side, cap0, cap1, ground=False):
    """vertical chamfered-rect prism; zspec [(z, inset_m)]. Rings are rebuilt as smaller chamf_rects, so an inset larger
    than the corner chamfer cannot flip the corner vertices (which inset() does on short edges)."""
    k = math.tan(math.pi / 8)
    rings = [[Vector((cx + x, cy + y, z)) for x, y in chamf_rect(w - 2 * d, h - 2 * d, max(c - k * d, 0.3 * c))] for z, d in zspec]
    return part.loft(cname, rings, side, cap0, cap1, ground=ground)

def chamf_spec(L, c0, c1, mid=()):
    s = [(0.0, 1.0, c0)] if c0 else []
    s += [(c0 / L if c0 else 0.0, 1.0, 0.0)] + [(m, 1.0, 0.0) for m in mid] + [(1 - c1 / L if c1 else 1.0, 1.0, 0.0)]
    if c1: s.append((1.0, 1.0, c1))
    return s

# ---------------- atlas / material (4x4 solid cells, 64 px; UVs at cell centres => padding) ----------------
def cell_uv(slot):
    col, row = slot % 4, slot // 4
    return ((col + 0.5) / 4, 1 - (row + 0.5) / 4)

def atlas_image(tex_name, path, pal):
    img = bpy.data.images.get(tex_name) or bpy.data.images.new(tex_name, 256, 256, alpha=False)
    rgb = [tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) for h in pal]
    px = []
    for y in range(256):
        row = 3 - y // 64
        for x in range(256):
            px.extend(rgb[row * 4 + x // 64] + (1.0,))
    img.pixels.foreach_set(px)
    img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    img.filepath = path; img.reload()
    return img

def material(mat_name, img):
    m = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    m.use_nodes = True; nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    for nd in [nd for nd in nt.nodes if nd.type == 'TEX_IMAGE']: nt.nodes.remove(nd)
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.interpolation = 'Closest'
    nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.0; bsdf.inputs['Roughness'].default_value = 0.75
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
    return m

# ---------------- checks ----------------
def comp_checks(P, mirror_skip=()):
    """non-manifold / loose / degenerate, X-mirror (components named in mirror_skip excluded), per-component contact gap"""
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
    mv = [v for v in bm.verts if P.comp[vc[v.index]][0] not in mirror_skip]
    mir = 0.0
    if mv:
        kd = kdtree.KDTree(len(mv))
        for i, v in enumerate(mv): kd.insert(v.co, i)
        kd.balance()
        mir = max(kd.find(Vector((-v.co.x, v.co.y, v.co.z)))[2] for v in mv)
    nm_ = sum(1 for e in bm.edges if not e.is_manifold); loose = sum(1 for v in bm.verts if not v.link_faces)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    print(f'  {P.name}: non-manifold {nm_} loose {loose} degenerate {deg} mirrorX {mir:.6f} worst gap {worst[0]:.5f} {worst[1]} problems {bad}')
    return dict(nonmanifold=nm_, loose=loose, degenerate=deg, mirror=mir, gap=worst, problems=bad)

def to_object(P, asset, coll, mat, pivot, root, mirror_skip=()):
    bm = P.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    comp_checks(P, mirror_skip)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        f.smooth = False; uv = cell_uv(f[P.slot])
        for lp in f.loops: lp[uvl].uv = uv
    for v in bm.verts: v.co -= Vector(pivot)
    me = bpy.data.meshes.new(asset + '_' + P.name); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(asset + '_' + P.name, me); coll.objects.link(ob)
    ob.parent = root; ob.location = pivot
    return ob

def clear_collection(asset):
    """own collection, linked into own build scene <asset>_Build (user's scene objects untouched)"""
    coll = bpy.data.collections.get(asset)
    if coll is None:
        coll = bpy.data.collections.new(asset)
    bsc = bpy.data.scenes.get(asset + '_Build') or bpy.data.scenes.new(asset + '_Build')
    if coll.name not in bsc.collection.children: bsc.collection.children.link(coll)
    for o in list(coll.objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and d.users == 0 and isinstance(d, bpy.types.Mesh): bpy.data.meshes.remove(d)
    return coll

def report(obs):
    tot = 0
    for k, o in obs.items():
        t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
        print(f'  {o.name}: tris {t} dims {[round(x, 3) for x in o.dimensions]} pivot {[round(x, 3) for x in o.matrix_world.translation]}')
    pts = [o.matrix_world @ v.co for o in obs.values() for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    print(f'TOTAL tris {tot} | size X {hi[0]-lo[0]:.3f} Y {hi[1]-lo[1]:.3f} Z {hi[2]-lo[2]:.3f} | '
          f'x {lo[0]:.3f}..{hi[0]:.3f} y {lo[1]:.3f}..{hi[1]:.3f} min z {lo[2]:.4f}')
    return tot

# ---------------- export + verify + lib ----------------
def export(asset, coll, root, fbx):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in coll.objects: o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z', axis_up='Y', bake_space_transform=True, object_types={'EMPTY', 'MESH'},
        mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, path_mode='COPY',
        embed_textures=False, bake_anim=False)
    print('exported', fbx)
    return fbx

def verify(fbx):
    win = bpy.context.window; prev = win.scene
    sc = bpy.data.scenes.new('TMP_FBXVerify'); win.scene = sc
    before_i, before_mat = set(bpy.data.images), set(bpy.data.materials)
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

def save_lib(path, coll, mat, img):
    data = {coll} | set(coll.objects) | {o.data for o in coll.objects if o.data} | {mat, img}
    bpy.data.libraries.write(path, data, fake_user=True, path_remap='ABSOLUTE')
    print('lib blend', path)
