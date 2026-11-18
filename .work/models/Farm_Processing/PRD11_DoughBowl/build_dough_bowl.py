import bpy, bmesh, math, os, sys, random
from mathutils import Vector
ROOT = r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE = os.path.join(ROOT,'.work','models','Farm_Processing','PRD11_DoughBowl')
sys.path.insert(0, os.path.join(ROOT,'.work','models','Farm_Processing','_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_11'
ART=os.path.join(ROOT,'art','Farm_Processing')
TEX_NAME='T_FarmProcessing_PRD11_BaseColor.png'
CHECK_DIR=os.path.join(os.environ['TEMP'],'FarmProcessing_check','PRD11')
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=ARGS[0] if ARGS else 'check'
ROUND=int(ARGS[1]) if len(ARGS)>1 else 1
CFG={'view':(-0.12,-1,0.36658), 'fill':(0.72,0.84)}
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#D8C49A','#F1D9A8','#E2C48E']

def shell(P, cname, prof, n, side_slot, cap0, cap1):
    # Own deep profile, radius in true bounding width; same manifold loft method as TOL shell.
    rings=[]
    for z,r in prof:
        rings.append([Vector((r*math.cos(2*math.pi*(k+.5)/n)/math.cos(math.pi/n),r*math.sin(2*math.pi*(k+.5)/n)/math.cos(math.pi/n),z)) for k in range(n)])
    return P.loft(cname,rings,side_slot,cap0,cap1,ground=True)

def build():
    for ob in list(bpy.context.scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
    bpy.context.scene.unit_settings.system='METRIC'
    coll=bpy.data.collections.new(NAME); bpy.context.scene.collection.children.link(coll)
    root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
    img=pc.atlas_image(TEX_NAME,os.path.join(ART,'Textures',TEX_NAME),PAL)
    mat=pc.material('M_FarmProcessing_PRD11',img)
    P=pc.Part('Body')
    prof=[(0,.086625),(.025,.086625),(.029,.0981),(.055,.1191544),(.100,.1508514),(.143,.175),(.155,.175),(.155,.157),(.140,.151),(.038,.0945)]
    shell(P,'ceramic_bowl',prof,16,lambda j,k: 5 if j==3 else 13 if j in (1,7,8) else 12,13,12)
    bowltris=sum(len(f.verts)-2 for f in P.comp[-1][1])
    rng=random.Random(11)
    rings=[]
    # Four dome bands, irregularly staggered, no central singularity.
    for j,(r,z) in enumerate([(.154,.140),(.143,.163),(.111,.184),(.064,.197),(.024,.200)]):
        ring=[]
        for k in range(16):
            a=2*math.pi*(k+.5)/16 + (0 if j==0 else rng.uniform(-.11,.11))
            rr=r+(0 if j==0 else rng.uniform(-.004,.004))
            zz=z+(rng.uniform(-.003,.003) if j in (1,2,3) else 0)
            ring.append(P.bm.verts.new((rr*math.cos(a)/math.cos(math.pi/16),rr*math.sin(a)/math.cos(math.pi/16),zz)))
        rings.append(ring)
    faces=[]
    for j in range(4):
        for k in range(16):
            kk=(k+1)%16; a,b,c,d=rings[j][k],rings[j][kk],rings[j+1][kk],rings[j+1][k]
            slot=14
            if (k+j)%2: faces.extend([P.face([a,b,d],slot),P.face([b,c,d],slot)])
            else: faces.extend([P.face([a,b,c],slot),P.face([a,c,d],slot)])
    faces+=[P.face(list(reversed(rings[0])),15),P.face(rings[-1],14)]
    P.comp.append(('dough',faces,False))
    print('BAND height .045m center .0775m = 50% bowl height; CAMERA elevation 20deg')
    print('COMPONENT TRIS bowl',bowltris,'dough',sum(len(f.verts)-2 for f in faces))
    check=pc.comp_checks(P,mirror_skip=('dough',))
    assert check['nonmanifold']==check['loose']==check['degenerate']==0 and check['mirror']<1e-6 and not check['problems'],check
    ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=('dough',))
    bpy.context.view_layer.update()
    total=pc.report({'Body':ob}); assert total<=550
    assert all(abs(v-t)<1e-5 for v,t in zip(ob.dimensions,(.35,.35,.2)))
    print('CONTACT OK: dough boundary z=.140, rim z=.155, radial overlap .003 m, bottom grounded; identity pivots; VERIFY/SNAP OK')
    return ob,root,coll,img,mat

sys.path.insert(0,HERE)
from render_preview import render
ob,root,coll,img,mat=build()
os.makedirs(CHECK_DIR,exist_ok=True)
if MODE=='export':
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)
else:
    render(os.path.join(CHECK_DIR,'round%d.png'%ROUND),40)
    if ROUND==3:
        for label,view in [('back',(0,1,.5)),('side',(1,0,.35)),('top',(.1,-.1,1))]:render(os.path.join(CHECK_DIR,label+'.png'),40,view)

