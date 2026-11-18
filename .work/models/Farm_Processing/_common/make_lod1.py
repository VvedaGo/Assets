# LOD1 for the Farm Processing stations (Unity's automatic Mesh LOD smears the flat-colour atlas, so LOD1 is made here).
# Headless: blender --background --factory-startup --python make_lod1.py -- STA_01 [STA_02 ...] [--ratio 0.5]
# For every station: loads art/Farm_Processing/Blend/FMS_Workshop_<ID>.blend (collection-only library written by the build
# scripts), adds for each part a decimated copy "<part>_LOD1" as a DIRECT child of the root (same pivot; the Unity builder
# re-parents it under its part — 2nd-level FBX children are exported with a wrong transform in Blender 5.2), re-snaps every
# LOD1 face to the palette cell of the nearest LOD0 face (no colour bleeding), and re-exports the same FBX (LOD0 untouched).
import bpy, bmesh, os, sys, math
from mathutils.bvhtree import BVHTree

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
ART = os.path.join(ROOT, 'art', 'Farm_Processing')
sys.path.insert(0, os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common'))
import processing_common as pc

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ratio = float(args[args.index('--ratio') + 1]) if '--ratio' in args else 0.5
ids = [a for a in args if a.startswith('STA_')]

def lod1_for(src, root, coll, ratio):
    me = src.data.copy(); ob = bpy.data.objects.new(src.name + '_LOD1', me); coll.objects.link(ob)
    ob.parent = root; bpy.context.view_layer.update(); ob.matrix_world = src.matrix_world.copy()   # world pose of the part (also for nested parts)
    tris0 = sum(len(p.vertices) - 2 for p in src.data.polygons)
    if tris0 > 60:                                       # tiny parts (bolts, pins) keep their LOD0 shape
        mod = ob.modifiers.new('dec', 'DECIMATE'); mod.decimate_type = 'COLLAPSE'; mod.ratio = ratio; mod.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = ob
        for o in bpy.context.view_layer.objects: o.select_set(o == ob)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    # re-snap UVs: each LOD1 face takes the UV (palette cell centre) of the nearest LOD0 face
    bs = bmesh.new(); bs.from_mesh(src.data); bs.faces.ensure_lookup_table(); uvs = bs.loops.layers.uv.active
    tree = BVHTree.FromBMesh(bs)
    bm = bmesh.new(); bm.from_mesh(ob.data); uvl = bm.loops.layers.uv.active
    from collections import Counter
    for f in bm.faces:
        # vote over 4 samples (centre + towards each corner); each sample casts a ray back onto LOD0 along -normal from just
        # outside the face, so it picks the VISIBLE LOD0 surface (not a proud hoop or a hidden inner face next to it)
        c = f.calc_center_median(); n = f.normal; votes = Counter()
        for q in [c] + [c.lerp(v.co, 0.55) for v in f.verts[:3]]:
            hit = tree.ray_cast(q + n * 0.02, -n, 0.06)
            if hit[2] is None: hit = tree.find_nearest(q)
            if hit[2] is not None: votes[tuple(bs.faces[hit[2]].loops[0][uvs].uv)] += 1
        if not votes: continue
        uv = votes.most_common(1)[0][0]
        for lp in f.loops: lp[uvl].uv = uv
        f.smooth = False
    bm.to_mesh(ob.data); bm.free(); bs.free()
    return ob, tris0, sum(len(p.vertices) - 2 for p in ob.data.polygons)

for sid in ids:
    name = 'FMS_Workshop_' + sid
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(os.path.join(ART, 'Blend', name + '.blend'), link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == name]
    coll = dst.collections[0]; bpy.context.scene.collection.children.link(coll)
    root = next(o for o in coll.objects if o.type == 'EMPTY' and o.parent is None)
    parts = [o for o in coll.objects if o.type == 'MESH' and not o.name.endswith('_LOD1')]
    for o in [o for o in coll.objects if o.name.endswith('_LOD1')]: bpy.data.objects.remove(o, do_unlink=True)
    t0 = t1 = 0; lines = []
    for p in parts:
        ob, a, b = lod1_for(p, root, coll, ratio); t0 += a; t1 += b; lines.append(f'{p.name} {a}->{b}')
    bpy.context.view_layer.update()
    print(f'LOD {name}: LOD0 {t0} LOD1 {t1} ({100 * t1 / t0:.0f}%) | ' + ', '.join(lines))
    # Blender 5.2 FBX bug with bake_space_transform: 2nd-level children (e.g. STA-06 Crank under UpperStone) are written with
    # a wrong transform. Pre-compensate their local matrix during export only (same fix as STA06 build_hand_mill.py).
    from bpy_extras.io_utils import axis_conversion
    G = axis_conversion(to_forward='-Z', to_up='Y').to_4x4()
    nested = [(o, o.matrix_basis.copy()) for o in coll.objects if o.parent is not None and o.parent != root]
    for o, _ in nested:
        Pm = o.parent.matrix_local.copy(); o.matrix_local = Pm.inverted() @ G @ Pm @ o.matrix_local
    bpy.context.view_layer.update()
    pc.export(name, coll, root, os.path.join(ART, 'Meshes', name + '.fbx'))
    for o, m in nested: o.matrix_basis = m
    if nested: print('  nested parts pre-compensated:', [o.name for o, _ in nested])
