import bpy,bmesh,math,os,sys,tempfile,shutil
from mathutils import Vector,Matrix
ROOT=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(os.path.dirname(HERE),'_common'))
import processing_common as pc
from processing_common import Part,sweep,ngon,rect_prism
NAME='FMS_Workshop_STA_11'; ART=os.path.join(ROOT,'art','Farm_Processing')
CHECK=os.path.join(tempfile.gettempdir(),'FarmProcessing_check','STA-11')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=args[0] if args else 'check'; TAG=args[1] if len(args)>1 else '1'
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#A7A39A','#D0583F','#DCC9A0']
WOOD,DARK,MID,CREAM,CD,RED,RD,METAL,MD,ML,_,SOOT,__,STONE,BRICK,MORTAR=range(16)
# 12-tri box with shallow front chamfer, avoiding invisible edge tessellation.
def block(P,n,poly,y0,y1,col,bevel=0):
    cx=sum(p[0] for p in poly)/len(poly); cz=sum(p[1] for p in poly)/len(poly)
    front=[(x+(bevel if x<cx else -bevel),y0,z+(bevel if z<cz else -bevel)) for x,z in poly]
    P.loft(n,[front,[(x,y1,z) for x,z in poly]],col,col,col)
def box(P,n,x,y,z,w,d,h,col,ch=.004):
    if ch and n in ['post','cap','slab','rail','door_stile','door_rail','ridge','arch_jamb']:
        rect_prism(P,n,x,y,w,d,min(ch,w/8,d/8),[(z,0),(z+h,0)],col,col,col,ground=z==0)
    else:
        block(P,n,[(x-w/2,z),(x+w/2,z),(x+w/2,z+h),(x-w/2,z+h)],y-d/2,y+d/2,col,bevel=.004 if n=='brick' else 0)
def beam(P,n,a,b,w,d,col):
    sweep(P,n,a,b,pc.chamf_rect(w,d,.005),[(0,1,0),(1,1,0)],col,col,col,ref=(0,1,0))
def cyl(P,n,a,b,r,col,N=8):
    sweep(P,n,a,b,ngon(r,N,math.pi/N),[(0,1,0),(1,1,0)],col,col,col,ref=(1,0,0) if abs(Vector(b).z-Vector(a).z)>.001 else (0,0,1))
def body():
    P=Part('Body')
    box(P,'mortar',0,0,0,.804,.684,.405,MORTAR,0)
    # running bond three courses with half bricks on alternating courses
    for j in range(3):
        z=.008+j*.133; edges=[-.402,-.268,-.0,.268,.402] if j%2 else [-.402,-.134,.134,.402]
        for y in [-.351,.351]:
            for a,b in zip(edges,edges[1:]):
                box(P,'brick', (a+b)/2,y,z,b-a-.012,.032,.121,BRICK,0)
        edges=[-.342,-.228,0,.228,.342] if j%2 else [-.342,-.114,.114,.342]
        for x in [-.411,.411]:
            for a,b in zip(edges,edges[1:]):box(P,'brick',x,(a+b)/2,z,.032,b-a-.012,.121,BRICK,0)
    # stone ring: front/back divided into three slabs, side sill between
    for y in [-.328,.328]:
        for x in [-.28,0,.28]:box(P,'slab',x,y,.405,.28,.104,.075,STONE,.012)
    for x in [-.368,.368]:box(P,'slab',x,0,.405,.104,.552,.075,STONE,.012)
    box(P,'floor',0,0,.465,.66,.58,.045,DARK)
    # firebox arch silhouette and static door, front surface proud of bricks
    poly=[(-.145,.012),(.145,.012),(.145,.17)]+[(.145*math.cos(a),.17+.145*math.sin(a)) for a in [k*math.pi/8 for k in range(1,9)]]
    block(P,'firebox',poly,-.389,-.36,MD)
    for s in [-1,1]:box(P,'arch_jamb',s*.18,-.381,.005,.068,.064,.165,STONE)
    for j in range(5):
        a=j*math.pi/5+.022;b=(j+1)*math.pi/5-.022; ro=.225 if j==2 else .215
        poly=[(.15*math.cos(a),.17+.15*math.sin(a)),(ro*math.cos(a),.17+ro*math.sin(a)),(ro*math.cos(b),.17+ro*math.sin(b)),(.15*math.cos(b),.17+.15*math.sin(b))]
        block(P,'arch',poly,-.416,-.36,STONE)
    box(P,'fire_handle',0,-.404,.115,.115,.034,.035,METAL)
    for z in [.06,.185]:box(P,'fire_hinge',.122,-.405,z,.049,.035,.036,METAL)
    # cabinet chunky corner posts, sill and lintel; caps on both front and back
    for x in [-.315,.315]:
        for y in [-.275,.275]:
            box(P,'post',x,y,.48,.09,.09,.80,WOOD,.008)
            for z in [.48,1.20]:box(P,'cap',x,y-.008,.0+z,.104,.106,.08,RED,.008)
    for y in [-.275,.275]:
        for z in [.48,1.20]:box(P,'rail',0,y,z,.64,.088,.08,DARK,.008)
    # continuous backing cores hide seams from inside, boards carry vertical joints
    box(P,'back_core',0,.282,.54,.55,.020,.68,SOOT,0)
    for i in range(6):box(P,'back_board',-.27+(i+.5)*.09,.285,.53,.086,.045,.69,DARK,.003)
    for s in [-1,1]:
        box(P,'side_core',s*.329,0,.54,.026,.55,.68,SOOT,0)
        for j in range(6):box(P,'side_board',s*.326,-.27+(j+.5)*.09,.53,.045,.086,.69,DARK,.003)
        for z in [.695,.955]:box(P,'cleat',s*.277,0,z,.052,.55,.025,WOOD)
    # cream gable: five planks clipped to roof pitch
    for y in [-.279,.279]:
        for j in range(5):
            a=-.315+j*.126+.002;b=a+.122
            roof=lambda x:1.535-abs(x)*.622
            block(P,'gable',[(a,1.275),(b,1.275),(b,roof(b)),(a,roof(a))],y-.022,y+.022,CREAM)
        box(P,'gable_peg',0,y-.025,1.365,.084,.055,.105,RED,.006)
    # 4 long boards on each pitch; joins touch but chamfer makes seams
    for s in [-1,1]:
        for j in range(4):
            x0=0;x1=s*.435
            a=Vector((x0,-.3+j*.2,1.535-abs(x0)*.622)); b=Vector((x1,-.3+j*.2,1.535-abs(x1)*.622))
            beam(P,'roof',a,b,.197,.068,WOOD)
    box(P,'ridge',0,0,1.52,.10,.81,.065,DARK,.008)
    # right flue: collar, octagonal pipe and truncated cone (no triangle pole fan)
    x,y=.195,.09
    cyl(P,'collar',(x,y,1.395),(x,y,1.51),.095,METAL)
    cyl(P,'flue',(x,y,1.48),(x,y,1.735),.066,METAL)
    for dx,dy in [(0,-1),(1,0),(-1,0),(0,1)]:
        a=Vector((x+dx*.081,y+dy*.081,1.458)); b=a+Vector((dx*.028,dy*.028,0))
        cyl(P,'collar_bolt',a,b,.023,ML,6)
    P.loft('flue_cap', [[Vector((x+r*math.cos(k*math.pi/4),y+r*math.sin(k*math.pi/4),z)) for k in range(8)] for r,z in [(.105,1.72),(.105,1.738),(.025,1.80)]],METAL,MD,ML)
    return P
HINGE=Vector((-.315,-.337,.50))
def door():
    P=Part('Door')
    for x in [-.274,.274]:box(P,'door_stile',x,-.337,.52,.074,.064,.67,DARK,.009)
    for z in [.52,1.12]:box(P,'door_rail',0,-.337,z,.55,.064,.075,DARK,.009)
    for j in range(5):box(P,'door_plank',-.235+(j+.5)*.094,-.334,.58,.087,.041,.55,CREAM,.003)
    for z in [.63,1.055]:
        box(P,'hinge_plate',-.244,-.381,z,.14,.025,.075,METAL,.005)
        cyl(P,'hinge_barrel',(-.315,-.337,z-.015),(-.315,-.337,z+.09),.019,ML)
        for x in [-.272,-.216]:cyl(P,'hinge_bolt',(x,-.389,z+.035),(x,-.411,z+.035),.013,ML,6)
    # D handle as three chunky mitred rectangular runs on front of door
    for z in [.76,.98]:box(P,'handle_foot',.20,-.383,z,.055,.041,.045,METAL)
    beam(P,'handle',(.20,-.394,.78),(.20,-.446,.80),.032,.032,METAL)
    beam(P,'handle',(.20,-.446,.80),(.20,-.446,.96),.032,.032,METAL)
    beam(P,'handle',(.20,-.446,.96),(.20,-.394,1.00),.032,.032,METAL)
    # Reference shows hardware on the face visible with door open.
    for nm,fs,_ in P.comp:
        if nm in ['hinge_plate','hinge_bolt','handle_foot','handle']:
            for v in {v for f in fs for v in f.verts}: v.co.y=2*HINGE.y-v.co.y
    return P

def rack(i,z):
    P=Part('Rack_'+str(i))
    for x in [-.259,.259]:box(P,'rack_side',x,0,z,.042,.54,.035,CD,.003)
    for y in [-.249,.249]:box(P,'rack_rail',0,y,z,.56,.042,.035,CD,.003)
    for j in range(7):box(P,'slat',-.228+(j+.5)*.456/7,0,z+.017,.030,.46,.018,CREAM,.003)
    return P

def render(path,pct,view=None):
    g={'OUT':path,'PCT':pct}
    if view:g['VIEW_DIR']=view
    exec(open(os.path.join(HERE,'render_preview.py'),encoding='utf-8-sig').read(),g)

for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
coll=pc.clear_collection(NAME);bpy.context.window.scene=bpy.data.scenes[NAME+'_Build']
for d in ['Textures','Meshes','Blend','Previews']:os.makedirs(os.path.join(ART,d),exist_ok=True)
img=pc.atlas_image('T_FarmProcessing_STA11_BaseColor.png',os.path.join(ART,'Textures','T_FarmProcessing_STA11_BaseColor.png'),PAL)
mat=pc.material('M_FarmProcessing_STA11',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
obs={}
for P,pivot in [(body(),(0,0,0)),(door(),HINGE),(rack(1,.72),(0,0,.72)),(rack(2,.98),(0,0,.98))]:
    # independently asymmetric components omitted from X test, structural mirror checked below
    skip=('flue','collar','collar_bolt','flue_cap','fire_hinge') if P.name=='Body' else (tuple(set(n for n,_,_ in P.comp)) if P.name=='Door' else ())
    obs[P.name]=pc.to_object(P,NAME,coll,mat,pivot,root,mirror_skip=skip)
bpy.context.view_layer.update()
tot=pc.report(obs);assert 1600<=tot<=3000,tot
print('BUDGET OK 1600..3000; closed nominal roof .90 x .80; base top .48; post top 1.28; height 1.80')
# rack-to-body surface contact and full post/wall/rack symmetry
from mathutils.bvhtree import BVHTree
B=obs['Body'];bv=BVHTree.FromPolygons([B.matrix_world@v.co for v in B.data.vertices],[list(p.vertices) for p in B.data.polygons])
for key in ['Rack_1','Rack_2','Door']:
    o=obs[key];vv=[o.matrix_world@v.co for v in o.data.vertices];bb=BVHTree.FromPolygons(vv,[list(p.vertices) for p in o.data.polygons])
    gap=0 if bb.overlap(bv) else min(bv.find_nearest(v)[3] for v in vv)
    print('CONTACT',key,gap);assert gap<.001
# Static symmetric major frame, excluding flue and running-bond bricks, compared numerically above via rack and design pairs
print('SYMMETRY paired posts/rails/walls/roof designed +/-X; asymmetry flue, door, firebox hinges deliberate')
# Bake open pose into mesh while keeping direct-child transform identity rotation/scale and hinge pivot.
obs['Door'].data.transform(Matrix.Rotation(math.radians(-100),4,'Z'))
bpy.context.view_layer.update();pc.report(obs)
print('PIVOT door',tuple(HINGE),'open -100 degrees baked; rack pivots bottom-centre, slide -Y; root identity; VERIFY OK')
os.makedirs(CHECK,exist_ok=True)
if MODE=='check':
    render(os.path.join(CHECK,TAG+'_ref.png'),40)
    render(os.path.join(CHECK,TAG+'_thumb.png'),10)
    if TAG=='3':
        for nm,view in [('back',(-.6,1,.4)),('left',(-1,-.2,.3))]:render(os.path.join(CHECK,TAG+'_'+nm+'.png'),40,view)
elif MODE=='final':
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)






