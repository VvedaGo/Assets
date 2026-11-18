"""Headless Blender 5.2: -- build|export; own files only, common helpers read-only."""
import bpy, bmesh, math, os, sys, importlib
from mathutils import Vector
ROOT = r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
sys.path.insert(0, os.path.join(HERE, '..', '_common'))
import processing_common as pc
importlib.reload(pc)
NAME = 'FMS_Workshop_PRD_07'
ART = os.path.join(ROOT, 'art', 'Farm_Processing')
CHECK_DIR = os.path.join(os.environ['TEMP'], 'FarmProcessing_check', 'PRD07')
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
PAL = ['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4',
       '#B83A30','#93302A','#EAD6AE','#D9C08F','#B87945','#8E5A33']
RED, DARK, CREAM, SHADE, CORD, CORD_D = range(10,16)
def ring(z,r,n=12):
    return [Vector((r*math.cos(2*math.pi*k/n),r*math.sin(2*math.pi*k/n),z)) for k in range(n)]
def verts(P, co): return [P.bm.verts.new(v) for v in co]
def bridge(P,a,b,slot):
    if len(a)==len(b):
        return [P.face([a[k],a[(k+1)%len(a)],b[(k+1)%len(a)],b[k]],slot) for k in range(len(a))]
    if len(a)>len(b): return bridge(P,b,a,slot)
    assert len(b)==2*len(a)
    fs=[]; n=len(a)
    for k in range(n):
        fs.append(P.face([a[k],a[(k+1)%n],b[(2*k+2)%(2*n)],b[2*k+1]],slot))
        fs.append(P.face([a[k],b[2*k+1],b[2*k]],slot))
    return fs
def build_prop():
    P=pc.Part('Body')
    P.loft('pot',[ring(z,r) for z,r in [(0,.060),(.014,.071),(.066,.080),(.139,.060)]],RED,DARK,RED,ground=True)
    # Thick ruffled skirt: 24-edge hem gives twelve pointed flutes, alternating deep/shallow tips.
    outer=[]
    for k in range(24):
        a=2*math.pi*k/24
        z=(.098 if (k//2)%2==0 else .104) if k%2==0 else .110
        r=.082 if k%2==0 else .077
        outer.append(Vector((r*math.cos(a),r*math.sin(a),z)))
    A=verts(P,ring(.134,.061)); B=verts(P,outer)
    C=verts(P,[v-Vector((v.x,v.y,0)).normalized()*.0015 for v in outer]); D=verts(P,ring(.134,.0595))
    fs=bridge(P,A,B,CREAM)+bridge(P,B,C,SHADE)+bridge(P,C,D,SHADE)+bridge(P,D,A,SHADE)
    P.comp.append(('skirt',fs,False))
    # Two radial dome transitions, hexagonal planar top, no pole fan.
    A=verts(P,ring(.132,.060)); B=verts(P,ring(.164,.066)); C=verts(P,ring(.180,.057,6))
    fs=bridge(P,A,B,CREAM)+bridge(P,B,C,CREAM)
    fs += [P.face(list(reversed(A)),SHADE),P.face(C,CREAM)]
    P.comp.append(('dome',fs,False))
    # Closed 12-sided cord with diamond section: four facets approximate round 12mm cord.
    P.torus_loft('cord',[ring(.134+.006*math.sin(j*math.pi/2),.064+.006*math.cos(j*math.pi/2)) for j in range(4)],
                 lambda j,k: CORD if j<2 else CORD_D)
    # Knot at front-right. Flat ribbons follow the skirt and then the body.
    angle=math.radians(-71); u=Vector((math.cos(angle),math.sin(angle),0)); t=Vector((-u.y,u.x,0))
    center=u*.070+Vector((0,0,.133))
    pc.sweep(P,'knot',center-u*.006,center+u*.009,[(-.011,-.005),(-.004,-.012),(.008,-.009),(.011,.005),(.004,.012),(-.008,.009)],
             [(0,.85,0),(1,1,0)],CORD,CORD_D,CORD,ref=t)
    for idx,(ang,lowest) in enumerate([(-78,.073),(-64,.063)]):
        a=math.radians(ang); uu=Vector((math.cos(a),math.sin(a),0)); tt=Vector((-uu.y,uu.x,0))
        points=[(.070,.130),(.084,.100),(.081,lowest)]
        rings=[]
        for r,z in points:
            cen=uu*r+Vector((0,0,z))
            rings.append([cen+tt*x+uu*y for x,y in [(-.005,-.0015),(.005,-.0015),(.005,.002),(-.005,.002)]])
        P.loft('tail'+str(idx),rings,lambda j,k: CORD if k!=0 else CORD_D,CORD_D,CORD)
    # Centre the full prop's ground bounding box, including the front ribbons.
    cy=(min(v.co.y for v in P.bm.verts)+max(v.co.y for v in P.bm.verts))/2
    for v in P.bm.verts:
        v.co.y-=cy
        v.co.z*=.94
    # Quantitative checks before conversion; only tied ribbons/knot are intentionally asymmetric.
    bmesh.ops.recalc_face_normals(P.bm,faces=P.bm.faces)
    for nm,fs,_ in P.comp: print('COMPONENT',nm,'tris',sum(len(f.verts)-2 for f in fs))
    ck=pc.comp_checks(P,mirror_skip=('knot','tail0','tail1'))
    assert ck['nonmanifold']==ck['loose']==ck['degenerate']==0
    assert ck['mirror']<1e-6
    assert not ck['problems'],ck
    print('CONTACT OK; ground z=0; skirt thickness=0.0015; cord width=0.012 / height=0.01128; tails delta=0.0094')
    return P
def build():
    for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o,do_unlink=True)
    sc=bpy.context.scene; sc.name=NAME+'_Build'; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
    coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
    for d in ('Textures','Meshes','Blend','Previews'): os.makedirs(os.path.join(ART,d),exist_ok=True)
    tex='T_FarmProcessing_PRD07_BaseColor.png'
    img=pc.atlas_image(tex,os.path.join(ART,'Textures',tex),PAL); mat=pc.material('M_FarmProcessing_PRD07',img)
    root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
    P=build_prop(); ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=('knot','tail0','tail1'))
    bpy.context.view_layer.update(); tot=pc.report({'Body':ob}); assert 200<=tot<=450,tot
    print('BUDGET OK',tot,'/450; pivot identity / ground centre; SNAP not applicable (standalone prop)')
    return coll,root,img,mat
if __name__=='__main__':
    coll,root,img,mat=build()
    os.makedirs(CHECK_DIR,exist_ok=True)
    from render_preview import render
    if MODE=='export':
        fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
        pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
        render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
        pc.verify(fbx)
    else:
        render(os.path.join(CHECK_DIR,'check.png'),40)
        for i,v in enumerate(((1,-1,.40),(1,1,.40),(-1,1,.40))): render(os.path.join(CHECK_DIR,'angle'+str(i)+'.png'),30,v)
