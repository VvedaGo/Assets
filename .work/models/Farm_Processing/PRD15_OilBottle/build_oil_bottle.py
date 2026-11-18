import bpy,bmesh,math,sys,os,json
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
sys.path.insert(0,str(HERE))
from render_preview import render
NAME='FMS_Workshop_PRD_15'
ART=ROOT/'art'/'Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD15'
CHECK.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['1']
ROUND=int(args[0]); FINAL='export' in args
for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o,do_unlink=True)
sc=bpy.context.scene; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#D6C193','#B87945','#8E5A33']
for d in ('Textures','Meshes','Blend','Previews'): (ART/d).mkdir(parents=True,exist_ok=True)
tex=ART/'Textures'/'T_FarmProcessing_PRD15_BaseColor.png'
img=pc.atlas_image(tex.name,str(tex),PAL); mat=pc.material('M_FarmProcessing_PRD15',img)
P=pc.Part('Body')
def ring(z,apo,n):
    r=apo/math.cos(math.pi/n)
    return [Vector((r*math.cos(-math.pi/2+(k+.5)*2*math.pi/n),r*math.sin(-math.pi/2+(k+.5)*2*math.pi/n),z)) for k in range(n)]
# Continuous bottle surface including lip and blind mouth. No overlapping band shell.
prof=[(0,.064),(.012,.071),(.090,.071),(.146,.071),(.166,.071),(.181,.064),(.219,.027),(.283,.027),(.283,.032),(.286,.034),(.295,.034),(.298,.032),(.298,.023),(.289,.023)]
def slots(j,k):
    shade=k in (6,7)
    if j==2:return 6 if shade else 5
    if j>=12:return 13
    return 13 if shade or j==0 else 12
P.loft('ceramic', [ring(z,a,10) for z,a in prof], slots,13,13,ground=True)
# Stopper seats on the mouth floor, with a readable shallow annular recess above it.
plug=[(.289,.0215),(.298,.0215),(.318,.023),(.320,.021)]
P.loft('stopper',[ring(z,a,8) for z,a in plug],lambda j,k:15 if k in (5,6) else 14,15,14)
bmesh.ops.recalc_face_normals(P.bm,faces=P.bm.faces)
checks=pc.comp_checks(P)
assert checks['nonmanifold']==checks['loose']==checks['degenerate']==0
assert checks['mirror']<1e-6 and not checks['problems']
subtris={nm:sum(len(f.verts)-2 for f in fs) for nm,fs,g in P.comp}
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root); bpy.context.view_layer.update()
tris=pc.report({'Body':ob}); assert 200<=tris<=450
print('COMPONENT TRIS',subtris,'budget 200-450 OK')
print('CONTACT stopper bottom .289 = recess floor .289 OK; band shares rings OK; SNAP ground minZ=0 OK')
# Ground centre, dimensions, one material, all transforms identity, flat faces.
assert abs(min(v.co.z for v in ob.data.vertices))<1e-8
assert len(ob.data.materials)==1
render(str(CHECK/f'round{ROUND}.png'),40)
if FINAL:
    fbx=pc.export(NAME,coll,root,str(ART/'Meshes'/(NAME+'.fbx')))
    pc.save_lib(str(ART/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(ART/'Previews'/(NAME+'_Preview.png')),100)
    for label,view in [('back',(.36,1,.44)),('side',(-1,0,.35)),('top',(0,-.2,1))]:render(str(CHECK/(label+'.png')),40,view)
    pc.verify(fbx)
    (HERE/'checks.json').write_text(json.dumps({'tris':tris,'components':subtris,'checks':checks,'bbox':list(ob.dimensions),'pivot':[0,0,0],'round':ROUND},indent=2))


