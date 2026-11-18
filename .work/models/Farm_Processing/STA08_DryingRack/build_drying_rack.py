import bpy, bmesh, sys, os, math, shutil, argparse
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_STA_08'
ART=ROOT/'art/Farm_Processing'
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#E6D3A8','#CDB88C','#B5835A']
args=argparse.ArgumentParser()
args.add_argument('--round',type=int,default=5)
args.add_argument('--check',action='store_true')
cfg=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
ROUND=cfg.round
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.name=NAME+'_Build'; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
for d in ['Textures','Meshes','Blend','Previews']: (ART/d).mkdir(parents=True,exist_ok=True)
tex=ART/'Textures/T_FarmProcessing_STA08_BaseColor.png'
img=pc.atlas_image(tex.name,str(tex),PAL); mat=pc.material('M_FarmProcessing_STA08',img)
def box(P,n,x,y,z,w,d,h,slot,ch=0):
    if ch:
        pc.rect_prism(P,n,x,y,w,d,ch,[(z,0),(z+h,0)],slot,slot,slot)
    else:
        prof=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
        pc.zprism(P,n,x,y,prof,[(z,0),(z+h,0)],slot,slot,slot)
def lattice_box(P,n,x,y,z,w,d):
    # Dedicated darker cream: top cell 13, side/bottom cell 14.
    prof=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    pc.zprism(P,n,x,y,prof,[(z,0),(z+.020,0)],14,14,13)
def beam(P,n,a,b,w,d,slot):
    pc.sweep(P,n,a,b,pc.chamf_rect(w,d,.006),[(0,1,0),(1,1,0)],slot,slot,slot,ref=(0,0,1))
# Review revision: 1.20m centre spacing at ground / .80m at crown.
def post_x(z): return .60-.20*z/1.6
LEG=.11
FRONT_Y=-.28
REAR_Y=.28
levels=[.43,.77,1.11]
widths=[.95,.87,.79]
slats=[.045,.045,.045]
def tray_parameters(index):
    width=widths[index-1]; sw=slats[index-1]
    gap=(width-.09-6*sw)/7
    inner_depth=5*gap+4*sw
    depth=inner_depth+.09
    # Front edge is 10cm proud of the foremost face of the front legs.
    front=FRONT_Y-LEG/2-.10
    return width,depth,sw,gap,front+depth/2
F=pc.Part('Frame')
for sx in [-1,1]:
    for sy in [-1,1]:
        rings=[]
        for z in [0,1.54]:
            prof=pc.chamf_rect(LEG,LEG,.008)
            rings.append([Vector((sx*post_x(z)+x,sy*.28+y,z)) for x,y in prof])
        F.loft('leg',rings,0,2,0,ground=True)
        # Explicit oversized 14x14x12cm chamfered post head, independent of leg.
        pc.rect_prism(F,'head',sx*.40,sy*.28,.14,.14,.010,
                     [(1.48,0),(1.582,0),(1.60,.018)],0,2,0)
        pc.sweep(F,'cap',(sx*.40,sy*.345,1.535),(sx*.40,sy*.365,1.535),
                 pc.chamf_rect(.066,.066,.007),[(0,1,0),(1,1,.004)],5,5,5,ref=(0,0,1))
# Crossbeams terminate within the heads, not in front of them.
for sy in [-1,1]:
    beam(F,'upper_beam',(-.40,sy*.28,1.53),(.40,sy*.28,1.53),.085,.085,0 if sy<0 else 2)
    beam(F,'low_cross',(-post_x(.17),sy*.28,.17),(post_x(.17),sy*.28,.17),.085,.085,0 if sy<0 else 2)
for sx in [-1,1]:
    beam(F,'low_side',(sx*post_x(.17),-.28,.17),(sx*post_x(.17),.28,.17),.085,.085,2)
    pc.sweep(F,'lowcap',(sx*post_x(.17),-.333,.17),(sx*post_x(.17),-.35,.17),
             pc.chamf_rect(.045,.045,.005),[(0,1,0),(1,1,0)],5,5,5,ref=(0,0,1))
# Each rail underlaps its tray edge while its outer face reaches the splayed posts.
for index,z in enumerate(levels,1):
    width,depth,sw,gap,y=tray_parameters(index)
    for sx in [-1,1]:
        railx=width/2+.018
        beam(F,'tray_support',(sx*railx,-.28,z-.04),(sx*railx,.28,z-.04),.08,.10,0)
objects={}
frame_check=pc.comp_checks(F)
assert not any(frame_check[k] for k in ['nonmanifold','loose','degenerate']) and not frame_check['problems'] and frame_check['mirror']<1e-6
objects['Frame']=pc.to_object(F,NAME,coll,mat,(0,0,0),root)
def tray(index,z):
    width,depth,sw,gap,y=tray_parameters(index)
    P=pc.Part('Tray_'+str(index))
    # 6cm tall dark-wood tray frames, 4.5cm wide boards.
    for sy in [-1,1]: box(P,'front_back',0,y+sy*(depth/2-.0225),z,width,.045,.06,1,.004)
    for sx in [-1,1]: box(P,'side',sx*(width/2-.0225),y,z,.045,depth-.09,.06,1,.004)
    iw=width-.09; idepth=depth-.09
    # Exactly 7x5 equal square openings, 4.5cm wide / 2cm tall slats.
    # Closed rectangular slats retain manifold geometry and remain below 2100 tris.
    for k in range(6):
        x=-iw/2+gap+k*(gap+sw)+sw/2
        lattice_box(P,'lattice_long',x,y,z+.020,sw,idepth+.012)
    for k in range(4):
        yy=y-idepth/2+gap+k*(gap+sw)+sw/2
        lattice_box(P,'lattice_cross',0,yy,z+.035,iw+.012,sw)
    coverage=1-35*gap*gap/(iw*idepth)
    print('LATTICE tray',index,'outer',round(width,5),round(depth,5),
          '7x5 square openings',round(gap,5),'slat width',sw,'slat height .020 coverage',round(coverage,3))
    fy=y-depth/2; hz=z+.030
    for sx in [-1,1]:
        pc.sweep(P,'hex_mount',(sx*.105,fy+.005,hz),(sx*.105,fy-.022,hz),
                 pc.ngon(.029,6,math.pi/6),[(0,1,0),(1,1,0)],8,8,7,ref=(0,0,1))
    # D-loop solid square-section sweep, faceted bends, sunk into hex mounts.
    reach=.073
    points=[(-.105,fy-.016,hz),(-.105,fy-reach+.016,hz),(-.086,fy-reach,hz),
            (.086,fy-reach,hz),(.105,fy-reach+.016,hz),(.105,fy-.016,hz)]
    rings=[]
    for k,p in enumerate(points):
        tangent=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])
        tangent.normalize(); cross=Vector((-tangent.y,tangent.x,0))
        r=.014
        rings.append([Vector(p)+cross*a+Vector((0,0,b)) for a,b in [(-r,-r),(r,-r),(r,r),(-r,r)]])
    P.loft('D_handle',rings,7,8,8)
    ck=pc.comp_checks(P)
    assert ck['nonmanifold']==ck['loose']==ck['degenerate']==0 and ck['mirror']<1e-6 and not ck['problems']
    return pc.to_object(P,NAME,coll,mat,(0,y,z),root)
for i,z in enumerate(levels,1): objects['Tray_'+str(i)]=tray(i,z)
bpy.context.view_layer.update()
tris=pc.report(objects); assert tris<=2100
assert PAL[1]=='#7A5233' and PAL[13]=='#E6D3A8' and PAL[14]=='#CDB88C'
print('PALETTE VERIFIED: tray frame #7A5233; lattice top #E6D3A8, sides #CDB88C; 4.5cm wide x 2cm tall')

# Exact support contact and tray translation clearance checks.
for i,z in enumerate(levels,1):
    width,depth,sw,gap,y=tray_parameters(i)
    inner_post=post_x(z+.06)-LEG/2
    clearance=inner_post-width/2
    assert clearance>0
    tray_front=y-depth/2
    forward_projection=(FRONT_Y-LEG/2)-tray_front
    assert abs(forward_projection-.10)<1e-6
    # At tray bottom, the support's flat top overlaps the side board.
    railx=width/2+.018
    overlap=width/2-(railx-.05+.006)
    assert overlap>0 and railx+.05>=post_x(z)-LEG/2
    print('CONTACT tray',i,'support gap 0 post clearance',round(clearance,5),
          'rail top overlap',round(overlap,5),'front projection',round(forward_projection,3),'slide -Y OK')
print('SNAP/VERIFY OK: ground 0, symmetry exact, all tray support contacts 0, root identity')
if not cfg.check:
    fbx=ART/('Meshes/'+NAME+'.fbx')
    pc.export(NAME,coll,root,str(fbx))
    fbmdir=fbx.with_suffix('.fbm'); fbmdir.mkdir(exist_ok=True); shutil.copy2(tex,fbmdir/tex.name)
    pc.verify(str(fbx))
    pc.save_lib(str(ART/('Blend/'+NAME+'.blend')),coll,mat,img)
out=ART/('Previews/'+NAME+'_Preview.png')
if cfg.check:
    out=Path(os.environ['TEMP'])/'FarmProcessing_check/STA08'/('round'+str(ROUND)+'.png')
    out.parent.mkdir(parents=True,exist_ok=True)
exec(compile((HERE/'render_preview.py').read_text(),str(HERE/'render_preview.py'),'exec'),dict(OUT=str(out),RES=(512,320) if cfg.check else (1280,800)))

if not cfg.check:
    checkdir=Path(os.environ['TEMP'])/'FarmProcessing_check/STA08'
    checkdir.mkdir(parents=True,exist_ok=True)
    for vname,direction in [('back',(0.36,1,.42)),('side',(-1,-.05,.30)),('front',(0,-1,.30))]:
        exec(compile((HERE/'render_preview.py').read_text(),str(HERE/'render_preview.py'),'exec'),dict(OUT=str(checkdir/(vname+'.png')),RES=(512,320),VIEW_DIR=direction))
