# make_lod1.py - LOD1 for flat-palette pack models (Unity's automatic Mesh LOD smears the flat-colour atlas: it merges
# vertices across palette cells, e.g. red stripes on a cream barrel).
# Headless:
#   blender --background --factory-startup --python make_lod1.py -- --art <art dir> NAME [NAME ...] [--ratio 0.5]
#   NAME = asset root, e.g. FMS_Workshop_STA_05; reads <art>/Blend/NAME.blend (collection-only library written by the
#   build script via pack_common.save_lib) and rewrites <art>/Meshes/NAME.fbx (LOD0 untouched).
# For each part it adds a decimated copy "<part>_Low1" as a DIRECT child of the root at the part's world pose (2nd-level
# FBX children export wrongly in Blender 5.2; the Unity PackPrefabBuilder re-parents it under its part and adds a LODGroup),
# then re-snaps every LOD1 face to the palette cell of the VISIBLE LOD0 surface (ray vote over 4 samples).
# Rerun after ANY re-export of the model by its build script (the build script writes the FBX without LOD1).
# NOTE: suffix is _Low1, not _LOD1: Unity treats "_LODn" names as an LOD set and warns about a missing _LOD0.
import bpy, bmesh, os, sys, math
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pack_common as pc

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ratio = float(args[args.index('--ratio') + 1]) if '--ratio' in args else 0.5
ART = args[args.index('--art') + 1]
skip = {args[args.index(k) + 1] for k in ('--ratio', '--art') if k in args}
ids = [a for a in args if not a.startswith('--') and a not in skip]

def lod1_for(src, root, coll, ratio):
    me = src.data.copy(); ob = bpy.data.objects.new(src.name + '_Low1', me); coll.objects.link(ob)
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

for name in ids:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(os.path.join(ART, 'Blend', name + '.blend'), link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == name]
    coll = dst.collections[0]; bpy.context.scene.collection.children.link(coll)
    root = next(o for o in coll.objects if o.type == 'EMPTY' and o.parent is None)
    parts = [o for o in coll.objects if o.type == 'MESH' and not o.name.endswith('_Low1')]
    for o in [o for o in coll.objects if o.name.endswith('_Low1')]: bpy.data.objects.remove(o, do_unlink=True)
    t0 = t1 = 0; lines = []
    for p in parts:
        ob, a, b = lod1_for(p, root, coll, ratio); t0 += a; t1 += b; lines.append(f'{p.name} {a}->{b}')
    bpy.context.view_layer.update()
    print(f'LOD {name}: LOD0 {t0} LOD1 {t1} ({100 * t1 / t0:.0f}%) | ' + ', '.join(lines))
    pc.export(name, coll, root, os.path.join(ART, 'Meshes', name + '.fbx'))
