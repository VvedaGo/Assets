import bpy,bmesh,math,os,sys,random
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_09'
ART=ROOT/'art/Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD09'
CHECK.mkdir(parents=True,exist_ok=True)
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'build'
for d in ('Meshes','Textures','Blend','Previews'): (ART/d).mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME);sc.collection.children.link(coll)
P=pc.Part('Body')
def solid(nm,vs,fs,slots):
    vv=[P.bm.verts.new(Vector(v)) for v in vs]
    ff=[P.face([vv[i] for i in f],slots[k%len(slots)]) for k,f in enumerate(fs)]
    P.comp.append((nm,ff,False))
def cone(nm,a,b,r,n,slot):
    a,b=Vector(a),Vector(b);d=(b-a).normalized();s=d.cross(Vector((0,1,0))).normalized();t=d.cross(s)
    vs=[a+s*math.cos(i*2*math.pi/n)*r+t*math.sin(i*2*math.pi/n)*r for i in range(n)]+[b]
    fs=[tuple(reversed(range(n)))]+[(i,(i+1)%n,n) for i in range(n)]
    solid(nm,vs,fs,[slot])
def leaf(nm,base,d,n,L,W,hex=True):
    base=Vector(base);d=Vector(d).normalized();n=Vector(n);n=(n-d*n.dot(d)).normalized();s=n.cross(d)
    outline=[(0,0),(.35,.5),(.72,.38),(1,0),(.72,-.38),(.35,-.5)] if hex else [(0,0),(.48,.5),(1,0),(.48,-.5)]
    vs=[base+d*(a*L)+s*(b*W) for a,b in outline]
    vs += [base+d*L*.46+n*.005,base+d*L*.46-n*.002]
    k=len(outline);fs=[];slots=[]
    for i in range(k):
        fs.extend([(k,i,(i+1)%k),(k+1,(i+1)%k,i)]);slots.extend([13 if i<k//2 else 14,14])
    solid(nm,vs,fs,slots)
def pod(nm,c):
    c=Vector(c);r=.011
    vs=[c+Vector(v)*r for v in ((1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,.88),(0,0,-.88))]
    fs=[(i,(i+1)%4,4) for i in range(4)]+[((i+1)%4,i,5) for i in range(4)]
    solid(nm,vs,fs,[15,12,15,15])
# Octagonal stalks taper down through the binding into the leafy twigs.
stems=[]
for i in range(8):
    a=i*math.tau/8
    top=Vector((.030*math.cos(a),.023*math.sin(a),[.37,.385,.355,.4,.365,.38,.345,.36][i]))
    bottom=Vector((-.051*math.cos(a),-.039*math.sin(a),.048+(.018 if i%2 else 0)))
    cone('stalk%02d'%i,top,bottom,.011,8,[0,2,1][i%3]);stems.append((top,bottom))
# Leaves rooted on supporting stalks. Front/back layers create real volume.
for i,(top,bottom) in enumerate(stems):
    a=i*math.tau/8
    for j in range(3 if i>=4 else 4):
        t=[.56,.70,.84,.95][j]
        base=top.lerp(bottom,t)
        ang=a+math.pi+(-.36 if j%2 else .28)
        d=Vector((math.cos(ang)*.8,math.sin(ang)*.55,-.70))
        if j==3: d=Vector((-base.x*5,-base.y*3,-1))
        normal=Vector((math.cos(ang),math.sin(ang),.24))
        leaf('leaf%02d_%d'%(i,j),base,d,normal,.086+(i%3)*.003,.055,hex=(i<6))
# Lead review: eight broad outer leaves on real branching twigs.
# 35-55 degrees outward from vertical; widest rank around z=.14 after fitting.
for i in range(8):
    ang=math.tau*i/8
    radial=Vector((math.cos(ang),math.sin(ang),0))
    top,bottom=stems[(i+4)%8]
    start=top.lerp(bottom,.62)
    base=Vector((radial.x*.045,radial.y*.042,.166+(i%2)*.008))
    cone('outertwig%02d'%i,start,base,.0033,3,2)
    theta=math.radians([50,45,40,55,50,45,35,55][i])
    direction=radial*math.sin(theta)+Vector((0,0,-math.cos(theta)))
    normal=radial+Vector((0,0,.25))
    leaf('outerleaf%02d'%i,base,direction,normal,.100,.061,hex=True)
# Each cream trio is supported by one branched tip; pods touch one another.
for k,(x,y,z) in enumerate(((-.088,-.076,.137),(.088,-.076,.125),(0,-.096,.075))):
    c=Vector((x,y,z));top,bottom=stems[[5,7,6][k]]
    start=top.lerp(bottom,.55 if k<2 else .72)
    cone('seedtwig%d'%k,start,c,.0032,3,2)
    for j,off in enumerate(((-.007,0,.004),(.007,0,.004),(0,-.001,-.005))): pod('pod%d_%d'%(k,j),c+Vector(off))
# Additional branches: tapered tetrahedral twigs connect to the main stems.
for i in range(5):
    top,bt=stems[i];start=top.lerp(bt,.50);end=top.lerp(bt,.84)+Vector((.005,0,0))
    cone('twig%d'%i,start,end,.0028,3,2)
# Two complete solid octagonal red wraps, closely stacked.
for i,z in enumerate((.274,.295)):
    pc.zprism(P,'wrap%d'%i,0,0,pc.ngon(.030,8,math.pi/8),[(z,0),(z+.019,0)],5,6,5)
# Closed cloth tails.
for i,(x,z) in enumerate(((-.011,.218),(.035,.222))):
    pc.sweep(P,'tail%d'%i,(.012,-.034,.282),(x,-.047,z),[(-.011,-.002),(.011,-.002),(.011,.002),(-.011,.002)],[(0,1,0),(1,1.15,0)],5,6,5,ref=(1,0,0))
# Knot is a squashed faceted solid with a bold front face.
vs=[(-.002,-.037,.271),(.027,-.037,.271),(.029,-.037,.285),(.004,-.037,.291),(-.002,-.049,.273),(.027,-.049,.273),(.029,-.049,.285),(.004,-.049,.289)]
solid('knot',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],[6,5,5,5,5,5])
# Fit exact catalogue envelope while keeping the bundle centre on the hanging axis.
lo=[min(v.co[k] for v in P.bm.verts) for k in range(3)];hi=[max(v.co[k] for v in P.bm.verts) for k in range(3)]
scale=[.26/(hi[0]-lo[0]),.18/(hi[1]-lo[1]),.40/(hi[2]-lo[2])]
for v in P.bm.verts:
    v.co=Vector((v.co.x*scale[0],v.co.y*scale[1],(v.co.z-lo[2])*scale[2]))
# Print canopy rank envelope for the lead's 35%-height requirement.
leafverts={v for name,faces,_ in P.comp if 'leaf' in name for f in faces for v in f.verts}
rank=[v.co for v in leafverts if .105 <= v.co.z <= .175]
print('CANOPY_MID_RANK z=.105..175 width',round(max(v.x for v in rank)-min(v.x for v in rank),4),'depth',round(max(v.y for v in rank)-min(v.y for v in rank),4))
for nm,fs,_ in P.comp: print('COMPONENT',nm,'tris',sum(len(f.verts)-2 for f in fs))
q=pc.comp_checks(P,mirror_skip=[n for n,_,_ in P.comp])
assert q['nonmanifold']==q['loose']==q['degenerate']==0
assert not q['problems'], q['problems']
pal=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#8E956A','#6F7552','#E8D6A8']
tex='T_FarmProcessing_PRD09_BaseColor.png'
img=pc.atlas_image(tex,str(ART/'Textures'/tex),pal);mat=pc.material('M_FarmProcessing_PRD09',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root);root.location=(0,0,.4)
body=pc.to_object(P,NAME,coll,mat,(0,0,.4),root,mirror_skip=[n for n,_,_ in P.comp]);body.location=(0,0,0)
bpy.context.view_layer.update();total=pc.report({'Body':body});print('BUDGET',total,'vs 500 nominal / about 760 permitted after lead review; HANG POINT z=.4; ASYMMETRIC organic; SNAP N/A')
exec((HERE/'render_preview.py').read_text(encoding='utf-8-sig'))
render(str(CHECK/'front.png'),40)
if MODE=='export':
    fbx=str(ART/'Meshes'/(NAME+'.fbx'));pc.export(NAME,coll,root,fbx)
    pc.save_lib(str(ART/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(ART/'Previews'/(NAME+'_Preview.png')),100)
    render(str(CHECK/'side.png'),40,(1,0,.22));render(str(CHECK/'back.png'),40,(.25,1,.3));render(str(CHECK/'top.png'),40,(.1,-.3,1))
    pc.verify(fbx)






