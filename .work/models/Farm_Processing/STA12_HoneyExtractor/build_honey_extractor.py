import bpy, math, os, sys, bmesh
from mathutils import Vector
ROOT=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(os.path.dirname(HERE),'_common'))
import processing_common as pc
from processing_common import Part, sweep, ngon, chamf_rect
ART=os.path.join(ROOT,'art','Farm_Processing'); NAME='FMS_Workshop_STA_12'
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=ARGS[0] if ARGS else 'build'; TAG=ARGS[1] if len(ARGS)>1 else 'r1'
CHECK_DIR=os.path.join(os.environ['TEMP'],'FarmProcessing_check','STA-12')
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#C9C2B6','#ADA79E','#DDD5CA']
WOOD,WD,WM,CREAM,CD,RED,RD,METAL,MD,ML,CI,WDD,CB,LID,LD,LL=range(16)
def ring(r,z,n=16): return [(x,y,z) for x,y in ngon(r,n,math.pi/n)]
def box(P,n,x,y,w,d,z0,z1,col=WOOD,c=.008,ch=.005):
    pc.rect_prism(P,n,x,y,w,d,c,[(z0,ch),(z0+ch,0),(z1-ch,0),(z1,ch)],col,WD,col)
def cyl(P,n,p0,p1,r,col=METAL,sides=8,ch=.004):
    sweep(P,n,p0,p1,ngon(r,sides,math.pi/sides),pc.chamf_spec((Vector(p1)-Vector(p0)).length,ch,ch),col,MD,col,ref=(0,1,0) if abs(p1[0]-p0[0])>.001 else (1,0,0))
def beam(P,n,p0,p1,w,d,col=WOOD):
    sweep(P,n,p0,p1,chamf_rect(w,d,.006),[(0,1,0),(1,1,0)],col,WD,col,ref=(0,0,1))
def build_body():
    P=Part('Body')
    # Closed vessel shell with interior floor, faceted walls and an open mouth.
    P.loft('drum',[ring(.318,.40),ring(.33,.412),ring(.33,.95),ring(.322,.96),ring(.312,.96),ring(.312,.425)],METAL,MD,MD)
    for n,z0,z1 in [('band_bottom',.40,.465),('band_top',.885,.96)]:
        P.torus_loft(n,[ring(.328,z0),ring(.341,z0+.008),ring(.344,z1-.008),ring(.334,z1),ring(.329,z1)],lambda j,k: ML if j in (0,2) else METAL)
    for a in (0,90,180,270):
        u=Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0)); v=Vector((-u.y,u.x,0))
        rings=[]
        for z,r,w,d in [(0,.385,.105,.004),(.008,.383,.105,0),(.34,.305,.09,0)]:
            rings.append([u*(r+x)+v*y+Vector((0,0,z)) for x,y in chamf_rect(w-2*d,.105-2*d,.012)])
        P.loft('leg',rings,lambda j,k: WOOD if k%2==0 else WM,WD,WOOD,ground=True)
        pcx=u*.305
        # rotated head has level top exactly at vessel underside
        rings=[]
        for z,d in [(.285,.006),(.291,0),(.382,0),(.40,.018)]:
            rings.append([pcx+u*x+v*y+Vector((0,0,z)) for x,y in chamf_rect(.14-2*d,.14-2*d,max(.012-d*.414,.004))])
        P.loft('head',rings,WOOD,WD,WOOD)
        sweep(P,'redcap',u*.372+Vector((0,0,.335)),u*.39+Vector((0,0,.335)),chamf_rect(.052,.052,.007),[(0,1,.002),(.75,1,0),(1,1,.003)],RED,RD,RED,ref=(0,0,1))
    # square links rotated 45 degrees: no rail wraps vessel
    pts=[(.348,0,.15),(0,.348,.15),(-.348,0,.15),(0,-.348,.15)]
    for i in range(4): beam(P,'stretcher',pts[i],pts[(i+1)%4],.075,.07,WD if i in (0,1) else WM)
    # wall mounted gearbox on +X
    sweep(P,'gearbox',(.313,0,.865),(.385,0,.865),chamf_rect(.145,.155,.022),[(0,1,.006),(.15,1,0),(.85,1,0),(1,1,.012)],METAL,MD,ML,ref=(0,1,0))
    # tap flange faces -Y, opposite leg at front beneath it
    cyl(P,'tapnut',(0,-.322,.48),(0,-.364,.48),.066,ML,6)
    cyl(P,'valve',(0,-.352,.48),(0,-.405,.48),.038,METAL)
    # spout continuous square bent outlet, closed wall thickness and genuinely open mouth
    def sq(y,z,w): return [(-w,y,z-w),(w,y,z-w),(w,y,z+w),(-w,y,z+w)]
    # along forward/down direction using orthonormal section
    p0=Vector((0,-.375,.46)); p1=Vector((0,-.44,.425)); t,e1,e2=pc.basis(p1-p0,(1,0,0))
    rr=lambda p,w:[p+e1*x+e2*y for x,y in [(-w,-w),(w,-w),(w,w),(-w,w)]]
    P.torus_loft('spout',[rr(p0,.036),rr(p1,.036),rr(p1,.025),rr(p0,.025)],lambda j,k: MD if j==2 else ML)
    beam(P,'lever',(0,-.409,.50),(.13,-.409,.55),.028,.035,RED)
    cyl(P,'leverpin',(0,-.402,.49),(0,-.427,.49),.027,ML,8)
    # turn gearbox toward the front-right diagonal for reference visibility
    from mathutils import Matrix
    R=Matrix.Rotation(math.radians(-30),4,'Z')
    for nm,faces,_ in P.comp:
        if nm=='gearbox':
            for v in {v for f in faces for v in f.verts}: v.co=R @ v.co
    return P

def build_lid():
    P=Part('Lid')
    P.loft('lid',[ring(.344,.959),ring(.353,.971),ring(.353,.998),ring(.332,1.025),ring(.10,1.075)],lambda j,k: LD if j==0 else LID,LD,LID)
    for x in (-.115,.115): box(P,'handlefoot',x,0,.08,.095,1.068,1.105,WOOD)
    # solid arch with chamfered angled shoulders, extruded in Y (no pole fan)
    prof=[(-.15,1.097),(-.15,1.145),(-.115,1.20),(.115,1.20),(.15,1.145),(.15,1.097),(.098,1.097),(.098,1.127),(.082,1.145),(-.082,1.145),(-.098,1.127),(-.098,1.097)]
    P.loft('bridge',[[(x,y,z) for x,z in prof] for y in (-.033,.033)],WD,WD,WD)
    return P

def build_crank():
    P=Part('Crank')
    cyl(P,'hub',(.378,0,.865),(.425,0,.865),.045,ML,6)
    pts=[Vector(p) for p in [(.415,0,.865),(.45,0,.865),(.47,0,.81),(.515,0,.705),(.55,0,.705)]]
    # mitred square section Z crank following approved mill approach
    rings=[]; side=Vector((0,1,0)); h=.022
    for i,p in enumerate(pts):
        d1=(p-pts[i-1]).normalized() if i else None; d2=(pts[i+1]-p).normalized() if i<len(pts)-1 else None
        t=(d1+d2).normalized() if d1 and d2 else (d1 or d2); k=1/t.dot(d1) if d1 and d2 else 1
        nn=t.cross(side).normalized()*h*k
        rings.append([p+nn-side*h,p+nn+side*h,p-nn+side*h,p-nn-side*h])
    P.loft('arm',rings,METAL,MD,ML)
    cyl(P,'grip',(.545,0,.705),(.79,0,.705),.058,RED,8,.013)
    from mathutils import Matrix
    R=Matrix.Rotation(math.radians(-30),4,'Z')
    for v in P.bm.verts: v.co=R @ v.co
    return P

def build_basket():
    P=Part('Basket')
    # two rectangular open frames in radial planes, cheap crossbars imply mesh
    cyl(P,'axle',(0,0,.43),(0,0,.93),.018,MD,8,0)
    for a in (0,180):
        u=Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0))
        def q(r,z): return u*r+Vector((0,0,z))
        for r in (.012,.25): sweep(P,'frame',q(r,.46),q(r,.895),[(-.009,-.009),(.009,-.009),(.009,.009),(-.009,.009)],[(0,1,0),(1,1,0)],MD,MD,MD,ref=(1,0,0))
        for z in (.46,.675,.895): sweep(P,'frame',q(.012,z),q(.25,z),[(-.009,-.009),(.009,-.009),(.009,.009),(-.009,.009)],[(0,1,0),(1,1,0)],METAL,MD,METAL,ref=(0,0,1))
    return P

def render(out,pct,view=None):
    g={'OUT':out,'PCT':pct}
    if view:g['VIEW_DIR']=view
    exec(open(os.path.join(HERE,'render_preview.py')).read(),g)

for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME);bpy.context.scene.collection.children.link(coll)
for d in ('Meshes','Textures','Previews','Blend'):os.makedirs(os.path.join(ART,d),exist_ok=True)
img=pc.atlas_image('T_FarmProcessing_STA12_BaseColor.png',os.path.join(ART,'Textures','T_FarmProcessing_STA12_BaseColor.png'),PAL)
mat=pc.material('M_FarmProcessing_STA12',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
obs={}
for P,piv,skip in [(build_body(),(0,0,0),('gearbox','lever')), (build_lid(),(0,0,.96),()),(build_crank(),(.32909,-.19,.865),('hub','arm','grip')),(build_basket(),(0,0,.43),())]:
    obs[P.name]=pc.to_object(P,NAME,coll,mat,piv,root,mirror_skip=skip)
bpy.context.view_layer.update(); tot=pc.report(obs)
assert 1600<=tot<=3200,tot
assert sum(len(p.vertices)-2 for p in obs['Basket'].data.polygons)<=300
print('CONTACTS drum bottom .400 = leg heads .400; lid nominal seat .960 = drum rim .960 (underside .959, 1mm hidden engagement); leg bottoms 0; basket radius .260 < inner drum .312; top .930 < lid .960; SNAP N/A freestanding prop')
os.makedirs(CHECK_DIR,exist_ok=True)
if MODE=='build':
    render(os.path.join(CHECK_DIR,TAG+'_ref.png'),40)
    render(os.path.join(CHECK_DIR,TAG+'_thumb.png'),10)
    if len(ARGS)>2:
        render(os.path.join(CHECK_DIR,TAG+'_back.png'),40,(-.7,.8,.45))
        obs['Lid'].hide_render=True
        render(os.path.join(CHECK_DIR,TAG+'_open.png'),40,(.6,-.8,1.1))
else:
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)





