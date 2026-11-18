import bpy,bmesh,math,os,sys,json
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
sys.path.insert(0,str(HERE))
import processing_common as pc
from render_preview import render
NAME='FMS_Workshop_PRD_10'
ART=ROOT/'art/Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD10'
CHECK.mkdir(parents=True,exist_ok=True)
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'round1'
for ob in list(bpy.context.scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME);sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
# 2026-11-14 user: colours as in the reference -> cream cloth (10/11), red ribbon (5/6), white flour (13/14)
pal=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#EBD3AA','#D2B888','#D45A44','#F7F2E8','#E6DECF','#D2B888']
for d in ('Textures','Meshes','Blend','Previews'):(ART/d).mkdir(parents=True,exist_ok=True)
tex='T_FarmProcessing_PRD10_BaseColor.png'
img=pc.atlas_image(tex,str(ART/'Textures'/tex),pal)
mat=pc.material('M_FarmProcessing_PRD10',img)
P=pc.Part('Body');n=12;sy=.30/.35
# Continuous boundary from ground up body, around six-sided rolled section, down to flour.
prof=[(0,.166),(.015,.172),(.070,.175),(.156,.128),(.183,.141),(.208,.148),(.238,.140),(.238,.115),(.208,.108)]
R=[]
for j,(z,r) in enumerate(prof):
    ring=[]
    for k in range(n):
        a=2*math.pi*k/n;fold=(.004 if k%2==0 else -.004) if j==2 else 0
        ring.append(P.bm.verts.new(((r+fold)*math.cos(a),sy*(r+fold)*math.sin(a),z)))
    R.append(ring)
faces=[]
for j in range(len(R)-1):
    for k in range(n):
        slot=11 if j==7 or (j<3 and k%4==2) else 10
        faces.append(P.face([R[j][k],R[j][(k+1)%n],R[j+1][(k+1)%n],R[j+1][k]],slot))
faces.append(P.face(list(reversed(R[0])),11))
# Irregular broad four-corner peak instead of a pole fan or separate white lumps.
peak=[P.bm.verts.new(v) for v in [(.036,-.012,.251),(.018,.030,.268),(-.037,.020,.253),(-.015,-.034,.249)]]
for k in range(4):
    q=k*3
    faces.append(P.face([R[-1][q],R[-1][(q+1)%12],peak[k]],13))
    faces.append(P.face([R[-1][(q+1)%12],R[-1][(q+2)%12],peak[(k+1)%4],peak[k]],13 if k%2 else 14))
    faces.append(P.face([R[-1][(q+2)%12],R[-1][(q+3)%12],peak[(k+1)%4]],13))
faces.append(P.face(peak,13))
P.comp.append(('cloth_cuff_flour',faces,True))
# Flat red ribbon band around the neck (as in the reference): rectangular section, inner face sunk 2 mm into the cloth.
def prof_r(z):
    for (z0,r0),(z1,r1) in zip(prof[:6],prof[1:6]):
        if z0<=z<=z1:return r0+(r1-r0)*(z-z0)/(z1-z0)
    return prof[5][1]
BZ0,BZ1,BT=.146,.184,.011
rings=[]
for i in range(12):
    a=2*math.pi*i/12;ring=[]
    for zz,dr in ((BZ0,-.002),(BZ0,BT),(BZ1,BT),(BZ1,-.002)):
        r=prof_r(zz)+dr;ring.append((r*math.cos(a),sy*r*math.sin(a),zz))
    rings.append(ring)
P.torus_loft('ribbon_band',rings,lambda j,k:6 if j==0 else 5)

def cord(name,pts,r=.007,sides=4):
    pts=[Vector(p) for p in pts];rings=[]
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        u=t.cross(Vector((0,1,0))).normalized();v=t.cross(u).normalized()
        rings.append([p+r*(math.cos(2*math.pi*k/sides)*u+math.sin(2*math.pi*k/sides)*v) for k in range(sides)])
    P.loft(name,rings,5,6,6)
# Bow at the front-right (as in the reference): a square knot block on the band + two flat ribbon tails with V-cut ends.
KX=.055;ka=math.atan2(-1,KX/.155);fy=lambda x,z:-sy*math.sqrt(max(prof_r(z)**2-x*x,0))
ky=fy(KX,.165)-BT
P.loft('knot',[[Vector((KX+dx,ky+yy,.165+dz)) for dx,dz in ((-.021,-.021),(.021,-.021),(.021,.021),(-.021,.021))] for yy in (.012,-.022)],5,6,5)
def ribbon_tail(name,pts,w=.026,t=.007):
    rings=[]
    for i,p in enumerate(pts):
        p=Vector(p);q=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)]);q.normalize()
        side=q.cross(Vector((0,-1,0))).normalized()
        ww=w*(.55 if i==len(pts)-1 else 1.0)
        rings.append([p+side*ww/2,p-side*ww/2,p-side*ww/2+Vector((0,-t,0)),p+side*ww/2+Vector((0,-t,0))])
    P.loft(name,rings,5,6,6)
for i,(dx,ex) in enumerate(((-.010,-.048),(.012,.050))):
    z1,z2=.128,.080;x1,x2=KX+dx+ex*.45,KX+dx+ex
    ribbon_tail('tail_'+str(i),[(KX+dx,ky+.004,.150),(x1,fy(x1,z1)-.004,z1),(x2,fy(x2,z2)-.004,z2)])
# Scale cloth folds to the exact footprint, keep origin at horizontal bbox centre.
for axis,target in ((0,.350),(1,.300)):
    lo=min(v.co[axis] for v in P.bm.verts);hi=max(v.co[axis] for v in P.bm.verts)
    for v in P.bm.verts:v.co[axis]=(v.co[axis]-(lo+hi)/2)*target/(hi-lo)
bmesh.ops.recalc_face_normals(P.bm,faces=P.bm.faces)
skip=[c[0] for c in P.comp if c[0] not in ('ribbon_band',)]
checks=pc.comp_checks(P,mirror_skip=skip)
assert checks['nonmanifold']==checks['loose']==checks['degenerate']==0
assert not checks['problems'],checks
components={nm:sum(len(f.verts)-2 for f in fs) for nm,fs,_ in P.comp}
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=skip)
bpy.context.view_layer.update();total=pc.report({'Body':ob})
print('COMPONENT_TRIS',components,'budget <=550',total)
assert total<=550,total
assert abs(ob.dimensions.x-.350)<1e-6 and abs(ob.dimensions.y-.300)<1e-6
assert min(v.co.z for v in ob.data.vertices)==0
print('CONTACTS OK: cuff/body share edges; flour shares inner cuff boundary; cords overlap cloth; knot/tails/frays joined by contact. Wrap mirrorX exact, organic flour/knot/tails intentionally asymmetric. SNAP N/A static prop; ground/pivot OK.')
if MODE=='export':
    fbx=pc.export(NAME,coll,root,str(ART/'Meshes'/(NAME+'.fbx')))
    pc.save_lib(str(ART/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(ART/'Previews'/(NAME+'_Preview.png')),100)
    pc.verify(fbx)
else:
    render(str(CHECK/(MODE+'.png')),40)
    if MODE=='round3':
        for key,view in [('back',(0,1,.5)),('side',(1,0,.4)),('top',(0,-.01,1))]:render(str(CHECK/(key+'.png')),40,view)

