import bpy,bmesh,math,os,sys
from pathlib import Path
from mathutils import Vector,kdtree
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_16'
ART=ROOT/'art/Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD16'
CHECK.mkdir(parents=True,exist_ok=True)
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'build'
for d in ('Meshes','Textures','Blend','Previews'): (ART/d).mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME);sc.collection.children.link(coll)
P=pc.Part('Body')

def plate(nm,outline,y0,y1,slot=5,bevel=False):
    if bevel:
        cx=sum(x for x,z in outline)/len(outline);cz=sum(z for x,z in outline)/len(outline)
        rings=[[(cx+(x-cx)*f,y,cz+(z-cz)*f) for x,z in outline] for y,f in ((y0,.88),(y0+.0015,1),(y1-.0015,1),(y1,.88))]
    else: rings=[[(x,y,z) for x,z in outline] for y in (y0,y1)]
    return P.loft(nm,rings,6 if slot==5 else 14,slot,slot)

def path_loop(nm,pts,r):
    pts=[Vector(p) for p in pts];up=Vector((0,1,0));rings=[]
    for i,c in enumerate(pts):
        d1=(c-pts[i-1]).normalized();d2=(pts[(i+1)%len(pts)]-c).normalized()
        t=(d1+d2).normalized();sd=t.cross(up).normalized();k=1/t.dot(d1)
        rings.append([c+sd*(r*math.cos(j*math.tau/6)*k)+up*(r*math.sin(j*math.tau/6)) for j in range(6)])
    P.torus_loft(nm,rings,lambda j,k:12 if k<3 else 15)

# Continuous shared-ring spindle: the head is the bottom 30%, not an overlay.
# Bottom octagon rises at front/back centre to create a genuine V mouth notch.
# Asymmetric jaw outline: upper snout / deep inward notch / extended lower jaw.
# The notch opens toward the forward-left silhouette, rather than splitting the chin.
rings=[[(.010,0,.018),(-.004,.010,.004),(-.025,.014,0),(-.014,.010,.035),
        (-.042,0,.016),(-.014,-.010,.035),(-.025,-.014,0),(-.004,-.010,.004)]]
profile=[(.040,.035),(.068,.044),(.083,.047),
         (.098,.050),(.145,.046),(.200,.035),(.245,.021),(.278,.010)]
for z,rx in profile:
    rings.append([(rx*math.cos(k*math.tau/8),rx*.55*math.sin(k*math.tau/8),z) for k in range(8)])
def skin_slot(j,k):
    return 13 if k in (0,7) else (10 if k in (1,6) else 14)
P.loft('continuous_curved_fish',rings,skin_slot,14,10)
# Eye radius10mm; center surface at |Y| about .019, cap at .023 (4mm proud).
for s in (-1,1):
    pc.sweep(P,'eye'+str(s),(-.012,s*.017,.052),(-.012,s*.023,.052),pc.ngon(.010,8,math.pi/8),[(0,1,0),(1,1,0)],8,8,7,ref=(1,0,0))
print('PROFILE widest z=.098 / fish .278 =',.098/.278,'head zone 0.. .083; paired raised crescent edges .005m; continuous single shell')
# Curved crescent edging follows the surface behind each eye, rather than a belt.
def fish_radius(z):
    for (za,ra),(zb,rb) in zip(profile,profile[1:]):
        if za<=z<=zb:return ra+(rb-ra)*(z-za)/(zb-za)
    return profile[0][1]
def surface_y(x,z):
    rx=fish_radius(z);ry=rx*.55;t=abs(x)/rx
    return ry*(1-t*.41421356) if t<=.70710678 else ry*(1-t)/.41421356
gillpath=[(-.034,.076),(-.019,.087),(.004,.086),(.024,.071),(.027,.054),(.014,.039)]
for sign in (-1,1):
    rr=[]
    for i,(x,z) in enumerate(gillpath):
        a=Vector(gillpath[max(0,i-1)]);b=Vector(gillpath[min(len(gillpath)-1,i+1)])
        t=(b-a).normalized();n=Vector((-t.y,t.x))*.0027
        ring=[]
        for u,h in ((-1,-.0015),(1,-.0015),(1,.005),(-1,.005)):
            xx=x+n.x*u;zz=z+n.y*u;ring.append((xx,sign*(surface_y(xx,zz)+h),zz))
        rr.append(ring)
    P.loft('crescent_gill'+str(sign),rr,lambda j,k:13 if k==2 else 14,14,14)
# Red plates have real six-millimetre thickness and roots buried in the body.
plate('dorsal',[(.025,.207),(.042,.247),(.049,.250),(.068,.211),(.043,.171)],-.003,.003)
plate('ventral',[(-.041,.159),(-.059,.149),(-.070,.109),(-.058,.087),(-.043,.098)],-.003,.003)
pect=[(-.005,.094),(.015,.135),(.029,.141),(.031,.112),(.006,.087)]
for s in (-1,1): plate('pectoral'+str(s),pect,s*.021,s*.027)
plate('tailL',[(-.009,.277),(-.043,.310),(-.050,.337),(-.025,.329),(.003,.297)],-.003,.003)
plate('tailR',[(.009,.277),(.043,.310),(.050,.337),(.025,.329),(-.003,.297)],-.003,.003)
# Tight solid wrap cuffs; no empty sleeve interior or floating ribbon.
for i,z in enumerate((.270,.283)):
    pc.zprism(P,'wrap'+str(i),0,0,[(x,y*.8) for x,y in pc.ngon(.018,6,math.pi/6)],[(z,.0015),(z+.003,0),(z+.007,0),(z+.010,.0015)],12,15,12)
path_loop('cordloop',[(0,0,.287),(-.006,0,.318),(-.013,0,.353),(-.014,0,.381),(-.008,0,.393),(0,0,.395),(.009,0,.390),(.014,0,.378),(.010,0,.349),(.004,0,.318)],.005)
# Validate bilateral construction before the deliberate forward snout bend.
kd=kdtree.KDTree(len(P.bm.verts))
for i,v in enumerate(P.bm.verts):kd.insert(v.co,i)
kd.balance();err=max(kd.find(Vector((v.co.x,-v.co.y,v.co.z)))[2] for v in P.bm.verts)
assert err<1e-6
print('BASE MIRROR Y',err,'before intentional head bend')
for v in P.bm.verts:
    z=v.co.z
    if z<.278:v.co.x+=math.tan(math.radians(8))*(.278-z)**2/(2*.278)
    if z<.083:v.co.y+=math.tan(math.radians(10))*(z-.083)
print('POSE body tangent 8deg; head forward -Y 10deg; mouth depth .035; crescent rise .005; eye diameter .020 proud .004')
hi=max(v.co.z for v in P.bm.verts)
top=max(P.bm.verts,key=lambda v:v.co.z).co.copy()
for v in P.bm.verts:
    v.co.x-=top.x
    v.co.z*=.4/hi
print('HANG EXACT',tuple(max(P.bm.verts,key=lambda v:v.co.z).co))
for nm,fs,_ in P.comp:print('COMPONENT',nm,'tris',sum(len(f.verts)-2 for f in fs))
skip=[n for n,_,_ in P.comp]
q=pc.comp_checks(P,mirror_skip=skip)
assert q['nonmanifold']==q['loose']==q['degenerate']==0
assert not q['problems'],q['problems']
print('CONTACTS OK; SNAP N/A; HANG z=.400 mouth minZ=0; mirror posed head intentionally asymmetric in Y')
pal=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#E39A3E','#5A3C26','#EAD6AE','#F0AF52','#C47A2A','#D2BA8A']
tex='T_FarmProcessing_PRD16_BaseColor.png'
img=pc.atlas_image(tex,str(ART/'Textures'/tex),pal);mat=pc.material('M_FarmProcessing_PRD16',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root);root.location=(0,0,.4)
body=pc.to_object(P,NAME,coll,mat,(0,0,.4),root,mirror_skip=skip);body.location=(0,0,0)
bpy.context.view_layer.update();total=pc.report({'Body':body});assert total<=650
exec((HERE/'render_preview.py').read_text(encoding='utf-8-sig'))
render(str(CHECK/'front.png'),40)
if MODE=='export':
    fbx=str(ART/'Meshes'/(NAME+'.fbx'));pc.export(NAME,coll,root,fbx)
    pc.save_lib(str(ART/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(ART/'Previews'/(NAME+'_Preview.png')),100)
    render(str(CHECK/'side.png'),40,(1,0,.22));render(str(CHECK/'back.png'),40,(.22,1,.35));render(str(CHECK/'top.png'),40,(.1,-.3,1))
    pc.verify(fbx)








