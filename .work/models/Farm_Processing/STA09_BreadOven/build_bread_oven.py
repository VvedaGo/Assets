import bpy,bmesh,math,os,sys,tempfile
from mathutils import Vector
ROOT=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE=os.path.join(ROOT,'.work/models/Farm_Processing/STA09_BreadOven')
sys.path.insert(0,os.path.join(ROOT,'.work/models/Farm_Processing/_common'))
import processing_common as pc
from processing_common import Part,ngon,chamf_rect,rect_prism,sweep,zprism
NAME='FMS_Workshop_STA_09'; ART=os.path.join(ROOT,'art/Farm_Processing')
CHECK=os.path.join(tempfile.gettempdir(),'FarmProcessing_check','STA-09')
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#A7A39A','#8C8B88','#D0583F']
W,WD,WM,C,CD,R,RD,M,MD,ML,CI,BLACK,CB,S,SD,B=range(16)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=args[0] if args else 'build'; TAG=args[1] if len(args)>1 else 'r1'
ZBASE=.78; AZ=1.015; RI=.265; RO=.425

def ring(r,z,n=12,a=math.pi/12):
    return [Vector((r*math.cos(a+2*math.pi*k/n),r*math.sin(a+2*math.pi*k/n),z)) for k in range(n)]

def block(P,n,poly,y0,y1,slot,bevel=.008):
    # Front in XZ; insetting the front outline produces a broad readable edge bevel.
    area=sum(poly[i-1][0]*poly[i][1]-poly[i][0]*poly[i-1][1] for i in range(len(poly)))
    if area<0: poly=list(reversed(poly))
    p1=pc.inset(poly,bevel)
    P.loft(n,[[Vector((x,y0,z)) for x,z in poly],[Vector((x,y1+bevel,z)) for x,z in poly],[Vector((x,y1,z)) for x,z in p1]],slot,slot,slot)

def archpoly(r,bottom=ZBASE):
    return [(-r,bottom),(r,bottom)]+[(r*math.cos(math.pi*k/12),AZ+r*math.sin(math.pi*k/12)) for k in range(13)]

def cut_dome(P):
    D=Part('tmp'); D.loft('dome',[ring(r,z) for r,z in ((.64,ZBASE),(.64,.90),(.59,1.095),(.47,1.27),(.29,1.405),(.17,1.44))],C,C,C)
    def obj(part,n):
        bmesh.ops.recalc_face_normals(part.bm,faces=list(part.bm.faces)); me=bpy.data.meshes.new(n);part.bm.to_mesh(me);part.bm.free()
        ob=bpy.data.objects.new(n,me);bpy.context.scene.collection.objects.link(ob);return ob
    ob=obj(D,'tmpdome')
    Q=Part('cut'); block(Q,'cut',archpoly(RI+.009,ZBASE-.02),.27,-1.0,BLACK,0)
    cutter=obj(Q,'tmpcut')
    mod=ob.modifiers.new('OpenChamber','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    old=set(P.bm.faces); P.bm.from_mesh(ob.data)
    ff=[f for f in P.bm.faces if f not in old]
    for f in ff:
        cen=f.calc_center_median(); f[P.slot]=BLACK if f.normal.dot(Vector((cen.x,cen.y,cen.z-ZBASE))) < -.01 else C
    P.comp.append(('dome',ff,False))
    for o in (ob,cutter):
        me=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me)

def body():
    P=Part('Body')
    for sx in (-1,1):
        for sy in (-1,1):
            # splayed legs with horizontal grounded footprints
            rings=[]
            for z,a,w in ((0,.63,.23),(.012,.628,.25),(.61,.52,.20)):
                rings.append([Vector((sx*a+x,sy*(a-.04)+y,z)) for x,y in chamf_rect(w,w,.018)])
            P.loft('leg',rings,lambda j,k: W if k in (0,1,6,7) else WM,WD,W,ground=True)
            rect_prism(P,'cap',sx*.52,sy*.52,.26,.26,.018,[(.50,.006),(.512,0),(.65,0),(.67,.02)],W,WD,W)
            block(P,'plate',[(sx*.52-.05,.54),(sx*.52+.05,.54),(sx*.52+.05,.63),(sx*.52-.05,.63)],sy*.65,sy*.673,R,.006)
    for sg in (-1,1):
        for z,a,t in ((.565,.52,.14),(.205,.592,.115)):
            sweep(P,'rail',(-a,sg*a,z),(a,sg*a,z),chamf_rect(t,t,.013),[(0,1,0),(1,1,0)],W,WD,WD,ref=(0,0,1))
            sweep(P,'rail',(sg*a,-a,z),(sg*a,a,z),chamf_rect(t,t,.013),[(0,1,0),(1,1,0)],WM,WD,WD,ref=(0,0,1))
    # ring of ten broad stone blocks, joints bevelled rather than disconnected
    for k in range(10):
        a0=-math.pi/2-math.pi/10+2*math.pi*k/10; a1=a0+2*math.pi/10
        poly=[(r*math.cos(a),r*math.sin(a)) for r,a in ((.35,a0),(.72,a0),(.72,a1),(.35,a1))]
        zprism(P,'slab',0,0,poly,[(.64,.005),(.653,0),(.755,0),(.78,.018)],S,SD,S)
    P.loft('hearth',[ring(.39,.635),ring(.39,.78)],SD,SD,SD)
    cut_dome(P)
    # plaster bridge supports the projecting arch where the dome curves away.
    for k in range(12):
        a0=k*math.pi/12;a1=(k+1)*math.pi/12
        poly=[(r*math.cos(a),AZ+r*math.sin(a)) for r,a in ((RI,a0),(.430,a0),(.430,a1),(RI,a1))]
        block(P,'plaster_bridge',poly,-.21,-.565,C,.003)
    for sg in (-1,1):
        block(P,'plaster_jamb',[(sg*RI,ZBASE),(sg*.430,ZBASE),(sg*.430,AZ),(sg*RI,AZ)],-.21,-.565,C,.003)
    # ONE radial parametric arch; 9 equal wedges, constant joint width.
    hg=.004
    for k in range(9):
        a0=k*math.pi/9;a1=(k+1)*math.pi/9
        v0=Vector((math.cos(a0),math.sin(a0)));t0=Vector((-math.sin(a0),math.cos(a0)))
        v1=Vector((math.cos(a1),math.sin(a1)));t1=Vector((-math.sin(a1),math.cos(a1)))
        c=Vector((0,AZ))
        poly=[tuple(c+v0*RI+t0*hg),tuple(c+v0*RO+t0*hg),tuple(c+v1*RO-t1*hg),tuple(c+v1*RI-t1*hg)]
        block(P,'voussoir',poly,-.558,-.635,B,.007)
    for sg in (-1,1):
        for z0,z1 in ((ZBASE,.89),(.898,AZ)):
            block(P,'jamb',[(sg*RI,z0),(sg*RO,z0),(sg*RO,z1),(sg*RI,z1)],-.558,-.635,B,.008)
    # hollow octagonal chimney: collar, sixteen separate coursed stones, cap.
    def tube(n,r0,r1,z0,z1,slot):
        P.torus_loft(n,[ring(r0,z0,8,math.pi/8),ring(r1,z0,8,math.pi/8),ring(r1,z1-.012,8,math.pi/8),ring(r1-.012,z1,8,math.pi/8),ring(r0,z1,8,math.pi/8)],slot)
    tube('collar',.105,.235,1.395,1.49,B)
    for course in range(2):
        for k in range(8):
            a0=math.pi/8+k*math.pi/4+(course%2)*math.pi/8;a1=a0+math.pi/4
            poly=[(r*math.cos(a),r*math.sin(a)) for r,a in ((.11,a0),(.18,a0),(.18,a1),(.11,a1))]
            z=1.48+course*.115
            zprism(P,'stack',0,0,poly,[(z,.002),(z+.008,0),(z+.108,0),(z+.115,.006)],S,SD,S)
    tube('capstone',.12,.23,1.70,1.80,MD)
    # fixed halves of hinge barrels, attached to brick jambs
    for z in (.865,1.065):
        sweep(P,'fixed_hinge',(-.273,-.665,z-.042),(-.273,-.665,z+.042),ngon(.026,8),[(0,1,0),(1,1,0)],MD,MD,ML)
        block(P,'fixed_strap',[(-.32,z-.03),(-.265,z-.03),(-.265,z+.03),(-.32,z+.03)],-.61,-.669,M,.003)
    return P

def door():
    P=Part('Door')
    block(P,'door',archpoly(RI-.007,.789),-.604,-.65,M,.014)
    for z in (.865,1.065):
        for dz in (-.029,.029):
            sweep(P,'moving_hinge',(-.273,-.665,z+dz-.012),(-.273,-.665,z+dz+.012),ngon(.028,8),[(0,1,0),(1,1,0)],M,MD,ML)
        block(P,'strap',[(-.27,z-.028),(-.16,z-.028),(-.15,z+.018),(-.25,z+.028)],-.644,-.682,M,.004)
        sweep(P,'bolt',(-.19,-.68,z),(-.19,-.695,z),ngon(.020,6),[(0,1,0),(1,1,.003)],ML,MD,ML,ref=(1,0,0))
    # chunky D handle with bevelled corners, left open through its centre
    for z in (.88,1.075):
        sweep(P,'handle_boss',(.175,-.647,z),(.175,-.676,z),ngon(.032,6),[(0,1,0),(1,1,.003)],MD,MD,M,ref=(1,0,0))
    pts=[Vector(p) for p in ((.175,-.663,.88),(.175,-.716,.898),(.175,-.735,.922),(.175,-.735,1.035),(.175,-.716,1.057),(.175,-.663,1.075))]
    rings=[]
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized(); e=Vector((1,0,0));f=t.cross(e)
        rings.append([p+e*x+f*y for x,y in chamf_rect(.045,.045,.006)])
    P.loft('handle',rings,M,MD,ML)
    return P

def render(path,pct=50,view=None):
    g={'OUT':path,'PCT':pct}
    if view:g['VIEW_DIR']=view
    exec(open(os.path.join(HERE,'render_preview.py')).read(),g)

def build():
    for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
    for folder in ('Textures','Meshes','Blend','Previews'):os.makedirs(os.path.join(ART,folder),exist_ok=True)
    col=pc.clear_collection(NAME);bpy.context.scene.collection.children.link(col)
    bpy.context.window.scene=bpy.data.scenes[NAME+'_Build']
    img=pc.atlas_image('T_FarmProcessing_STA09_BaseColor.png',os.path.join(ART,'Textures/T_FarmProcessing_STA09_BaseColor.png'),PAL)
    mat=pc.material('M_FarmProcessing_STA09',img)
    root=bpy.data.objects.new(NAME,None);col.objects.link(root)
    bp=body();dp=door()
    # Door is deliberately asymmetric; hinge assemblies are excluded from body mirror test.
    bcheck=pc.comp_checks(bp,('fixed_hinge','fixed_strap'))
    assert not any(bcheck[k] for k in ('nonmanifold','loose','degenerate'))
    assert bcheck['mirror']<1e-6 and not bcheck['problems']
    dcheck=pc.comp_checks(dp,tuple(n for n,_,_ in dp.comp))
    assert not any(dcheck[k] for k in ('nonmanifold','loose','degenerate')) and not dcheck['problems']
    obs={'Body':pc.to_object(bp,NAME,col,mat,(0,0,0),root,('fixed_hinge','fixed_strap')),
         'Door':pc.to_object(dp,NAME,col,mat,(-.273,-.665,.789),root,tuple(n for n,_,_ in dp.comp))}
    bpy.context.view_layer.update();total=pc.report(obs);assert 2200<=total<=4000,total
    from mathutils.bvhtree import BVHTree
    trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in obs.values()]
    assert trees[0].overlap(trees[1]), 'door must contact fixed hinge'
    print('CONTACT door-body hinge overlap OK; transforms identity rotation, scale1; arch 9 equal radial wedges RI .265 RO .425 joint .008 depth .077')
    print('BUDGET OK 2200..4000; stand top .64 = stone bottom .64; stone top .78 = dome bottom .78; base Z=0')
    print('SNAP N/A freestanding station; hinge axis vertical (-.273,-.665); door clearance 7mm; permitted outward rotation -110..0 degrees')
    return col,root,obs,img,mat

COL,ROOTOB,OBS,IMG,MAT=build()
if MODE=='check':
    os.makedirs(CHECK,exist_ok=True);render(os.path.join(CHECK,TAG+'_ref.png'));render(os.path.join(CHECK,TAG+'_thumb.png'),10)
    if len(args)>2:
        render(os.path.join(CHECK,TAG+'_back.png'),40,(.6,1,.45))
        render(os.path.join(CHECK,TAG+'_side.png'),40,(-1,0,.32))
        render(os.path.join(CHECK,TAG+'_front.png'),40,(0,-1,.32))
        OBS['Door'].rotation_euler.z=math.radians(-100);bpy.context.view_layer.update()
        render(os.path.join(CHECK,TAG+'_open.png'),40,(-.5,-1,.38))
elif MODE=='final':
    fbx=pc.export(NAME,COL,ROOTOB,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),COL,MAT,IMG)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)




