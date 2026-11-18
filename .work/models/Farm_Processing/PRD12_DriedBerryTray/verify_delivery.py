import bpy,sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];ART=ROOT/'art/Farm_Processing';N='FMS_Workshop_PRD_12'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(ART/'Meshes'/f'{N}.fbx'))
obs=list(bpy.context.scene.objects);meshes=[o for o in obs if o.type=='MESH'];bpy.context.view_layer.update()
assert len(obs)==2 and len(meshes)==1
assert sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)==1504
pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];dims=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
assert all(abs(x-y)<.0005 for x,y in zip(dims,[.400,.300,.083]))
assert abs(min(v.z for v in pts))<.0001
assert all(abs(s-1)<.0001 for o in obs for s in o.matrix_world.to_scale())
imgs=[i for i in bpy.data.images if i.source=='FILE' and 'PRD12' in i.name];assert imgs and all(Path(bpy.path.abspath(i.filepath)).is_file() for i in imgs)
for p in [ART/'Blend'/f'{N}.blend',ART/'Previews'/f'{N}_Preview.png',ART/'Textures/T_FarmProcessing_PRD12_BaseColor.png']:assert p.is_file()
print('DELIVERY ASSERTIONS PASS: 2 nodes, 1504 triangles, .400/.300/.083 dimensions, minZ0, unit scale, texture found and all artifacts exist')


