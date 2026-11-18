import bpy,bmesh,sys,os,shutil,argparse
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_08'; ART=ROOT/'art/Farm_Processing'
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#F3DDB8','#B5835A','#B5835A']
a=argparse.ArgumentParser(); a.add_argument('--round',type=int,default=3); a.add_argument('--check',action='store_true'); cfg=a.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.name=NAME+'_Build'; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
for d in ['Textures','Meshes','Blend','Previews']: (ART/d).mkdir(parents=True,exist_ok=True)
tex=ART/'Textures/T_FarmProcessing_PRD08_BaseColor.png'
img=pc.atlas_image(tex.name,str(tex),PAL); mat=pc.material('M_FarmProcessing_PRD08',img)
P=pc.Part('Body')
def box(n,x,y,w,d,z,h,side,top=None,ground=False):
    outline=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    pc.zprism(P,n,x,y,outline,[(z,0),(z+h,0)],side,side,side if top is None else top,ground=ground)
def rail(n,a,b):
    # Six-point section: broad flat top and two 2mm clipped shoulders.
    prof=[(-.0125,0),(.0125,0),(.0125,.033),(.0105,.035),(-.0105,.035),(-.0125,.033)]
    pc.sweep(P,n,a,b,prof,[(0,1,0),(1,1,0)],lambda j,k:0 if k in (2,3,4) else 2,2,2,ref=(0,1,0) if a[0]!=b[0] else (-1,0,0),ground=True)
for y in [-.1625,.1625]: rail('long_rail',(-.216,y,0),(.216,y,0))
for x in [-.2375,.2375]: rail('side_rail',(x,-.139,0),(x,.139,0))
for x in [-.2275,.2275]:
    for y in [-.1525,.1525]:
        pc.rect_prism(P,'red_corner',x,y,.045,.045,.003,[(0,0),(.042,0),(.045,.003)],5,6,5,ground=True)
for i in range(5):
    y=-.15+.0276+i*.0612
    box('floor_slat',0,y,.452,.0552,.006,.006,11,1)
traytris=sum(len(f.verts)-2 for f in P.bm.faces)
# CCW concave crescent, arc is -Y, notch is +Y. 9 boundary vertices, no pole fan.
outline=[(-.045,.014),(-.045,-.004),(-.028,-.026),(0,-.036),(.028,-.026),(.045,-.004),(.045,.014),(.018,.001),(-.018,.001)]
for row,y in enumerate([-.093,0,.093]):
    for col,x in enumerate([-.162,-.054,.054,.162]):
        pc.zprism(P,'slice_%d_%d'%(row,col),x,y,outline,[(.012,0),(.027,0)],lambda j,k:5 if k<6 else 13,13,13)
checks=pc.comp_checks(P)
assert checks['nonmanifold']==checks['loose']==checks['degenerate']==0
assert checks['mirror']<1e-6 and checks['gap'][0]<1e-6 and not checks['problems']
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root)
bpy.context.view_layer.update()
tris=pc.report({'Body':ob}); assert 300<=tris<=700
assert all(abs(ob.dimensions[i]-v)<1e-6 for i,v in enumerate((.5,.35,.045)))
print('PARTS tray',traytris,'food',tris-traytris,'each slice',(tris-traytris)//12,'TOTAL',tris,'budget 700')
print('CONTACT slices bottom .012 slat top .012 = zero gap; floor/rail overlap .001; slat gaps .006 real openings')
print('SNAP/VERIFY OK: 12 slices 3x4 same facing; exact X symmetry; minZ0; pivots ground bbox centre; source transforms identity')
checkdir=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD08'; checkdir.mkdir(parents=True,exist_ok=True)
if not cfg.check:
    fbx=ART/('Meshes/'+NAME+'.fbx'); pc.export(NAME,coll,root,str(fbx))
    fbmdir=fbx.with_suffix('.fbm'); fbmdir.mkdir(exist_ok=True); shutil.copy2(tex,fbmdir/tex.name)
    pc.verify(str(fbx)); pc.save_lib(str(ART/('Blend/'+NAME+'.blend')),coll,mat,img)
out=checkdir/('round%d.png'%cfg.round) if cfg.check else ART/('Previews/'+NAME+'_Preview.png')
exec(compile((HERE/'render_preview.py').read_text(),str(HERE/'render_preview.py'),'exec'),dict(OUT=str(out),RES=(512,320) if cfg.check else (1280,800)))
if not cfg.check:
    for vn,vd in [('back',(.55,1,.65)),('side',(-1,0,.40)),('front',(0,-1,.45))]:
        exec(compile((HERE/'render_preview.py').read_text(),str(HERE/'render_preview.py'),'exec'),dict(OUT=str(checkdir/(vn+'.png')),RES=(512,320),VIEW_DIR=vd))

