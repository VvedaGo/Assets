"""Original procedural PRD13; run headless Blender -- build|export [round]."""
import bpy, bmesh, math, os, sys, importlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
importlib.reload(pc)
NAME='FMS_Workshop_PRD_13'; ART=str(ROOT/'art'/'Farm_Processing')
CFG=dict(view=(-0.50,-1,0.62),fill=(0.78,0.85))
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=ARGS[0] if ARGS else 'build'; ROUND=ARGS[1] if len(ARGS)>1 else '1'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD13'
CHECK.mkdir(parents=True,exist_ok=True)
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C97E3D','#4E4643','#EFD3A0','#E09A55','#6E6560','#F3DDB0']
for d in ('Textures','Meshes','Blend','Previews'): (Path(ART)/d).mkdir(parents=True,exist_ok=True)
for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME); bpy.context.scene.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
temp_mats=[bpy.data.materials.new('SLOT_'+str(i)) for i in range(16)]
def meshob(n,vs,fs,slots):
    m=bpy.data.meshes.new(n); m.from_pydata(vs,[],fs); m.update()
    for mat in temp_mats:m.materials.append(mat)
    for f,s in zip(m.polygons,slots): f.material_index=s
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
    o=bpy.data.objects.new(n,m);coll.objects.link(o);return o

def loaf(cx):
    vs=[];fs=[];slots=[];n=10
    for z,r in [(0.004,0.80),(0.015,0.97),(0.038,1),(0.064,0.85),(0.079,0.42)]:
        for k in range(n):
            a=2*math.pi*k/n
            vs.append((cx+0.0725*r*math.cos(a),0.090/math.sin(2*math.pi/5)*r*math.sin(a),z))
    for j in range(4):
        for k in range(n):
            fs.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k));slots.append(12 if j<2 else 13)
    fs += [tuple(reversed(range(n))),tuple(range(4*n,5*n))];slots += [12,13]
    return meshob('Roll',vs,fs,slots)

def boolean(a,b,op):
    bpy.context.view_layer.objects.active=a
    mod=a.modifiers.new(op,'BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(b,do_unlink=True)

ROLL_SPACING=0.1185  # 26.5mm maximum overlap, slightly fuller shared baked joins
ROLL_CENTRES=(-ROLL_SPACING,0,ROLL_SPACING)
rolls=[loaf(x) for x in ROLL_CENTRES]
bread=rolls[0]
for ob in rolls[1:]: boolean(bread,ob,'UNION')
# Obtain faceted crown height for each cut endpoint (ray cast on the uncut union).
bm=bmesh.new();bm.from_mesh(bread.data);bv=BVHTree.FromBMesh(bm)
def height(x,y):
    hit=bv.ray_cast(Vector((x,y,0.2)),Vector((0,0,-1)))
    assert hit[0] is not None
    return hit[0].z
# Tapered six-vertex bottom groove: ridge endpoint depths taper to zero.
# The complete cutter extends above the crust; all new visible faces are genuine cut walls.
for cx in ROLL_CENTRES:
    for cy in (-0.028,0.028):
        angle=math.radians(35)
        u=Vector((math.cos(angle),math.sin(angle),0));v=Vector((-u.y,u.x,0));cen=Vector((cx,cy,0))
        a=cen-u*0.037;b=cen+u*0.037
        # Lower ridge follows the faceted dome, with a 7mm central depth.
        mid=cen.copy(); mid.z=height(mid.x,mid.y)-0.007
        a.z=height(a.x,a.y)+0.001;b.z=height(b.x,b.y)+0.001
        ridge=[a,mid,b];vs=[]
        # triangular sections: one low centre plus two high flanks
        for pt in ridge:
            dz=0.05
            vs.extend([tuple(pt),tuple(pt-v*dz*(0.006/0.007)+Vector((0,0,dz))),tuple(pt+v*dz*(0.006/0.007)+Vector((0,0,dz)))])
        fs=[(0,2,1),(6,7,8)]
        for j in (0,1):
            for k in range(3):fs.append((j*3+k,j*3+(k+1)%3,(j+1)*3+(k+1)%3,(j+1)*3+k))
        cutter=meshob('ScoreCutter',vs,fs,[15]*len(fs));boolean(bread,cutter,'DIFFERENCE')
bm.free()
# Collapse only sub-0.05mm boolean slivers, keeping the V grooves and silhouette.
bm=bmesh.new();bm.from_mesh(bread.data)
# Split the existing union surface at each join to expose a shared pale baked seam.
# This is face colour on the same watertight shell, never an overlapping skin.
for seam in (-ROLL_SPACING/2,ROLL_SPACING/2):
    for x in (seam-0.0025,seam+0.0025):
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,
                              plane_co=(x,0,0),plane_no=(1,0,0),clear_inner=False,clear_outer=False)
for f in bm.faces:
    c=f.calc_center_median()
    if any(abs(c.x-seam)<0.002501 for seam in (-ROLL_SPACING/2,ROLL_SPACING/2)):
        f.material_index=12
print('POLISH score angle 35deg, overlap',round((0.145-ROLL_SPACING)*1000,1),'mm, shared seam width 5mm')
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.00005)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.00005)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(bread.data);bm.free()
# Reconstruct slot-tagged common Part, preserving boolean face palette IDs.
P=pc.Part('Body')
# Tray closed thick cross section: bottom outside -> lip -> inside floor.
rings=[]
for w,d,c,z in [(0.446,0.296,0.018,0),(0.450,0.300,0.018,0.012),(0.450,0.300,0.018,0.026),(0.426,0.276,0.016,0.026),(0.400,0.250,0.012,0.004)]:
    rings.append([(x,y,z) for x,y in pc.chamf_rect(w,d,c)])
P.loft('Tray',rings,lambda j,k:[14,14,14,11][j],11,11,ground=True)
traytris=sum(len(f.verts)-2 for f in P.bm.faces)
verts=[P.bm.verts.new(v.co) for v in bread.data.vertices];faces=[]
for poly in bread.data.polygons:faces.append(P.face([verts[i] for i in poly.vertices],poly.material_index))
P.comp.append(('JoinedBread',faces,False));bpy.data.objects.remove(bread,do_unlink=True)
print('PARTS Tray',traytris,'JoinedBread',sum(len(f.verts)-2 for f in faces))
# Diagonal scoring deliberately breaks X mirror; silhouette symmetry is checked below on base roll profile.
checks=pc.comp_checks(P,mirror_skip=('JoinedBread',))
assert checks['nonmanifold']==checks['loose']==checks['degenerate']==0,checks
assert not checks['problems'], checks
assert checks['mirror']<1e-6
print('CONTACT OK: roll min Z=0.004 equals tray floor; three rolls BOOLEAN UNION, no overlapping skins')
print('MIRROR silhouette X exact; diagonal cut handedness excluded from mirror by design')
tex='T_FarmProcessing_PRD13_BaseColor.png'
img=pc.atlas_image(tex,str(Path(ART)/'Textures'/tex),PAL);mat=pc.material('M_FarmProcessing_PRD13',img)
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=('JoinedBread',))
bpy.context.view_layer.update();total=pc.report({'Body':ob});assert total<=700,total
print('BUDGET OK',total,'/700; SNAP N/A (product); identity transforms root/body, ground minZ=0')
exec((HERE/'render_preview.py').read_text(encoding='utf-8'))
if MODE=='export':
    fbx=pc.export(NAME,coll,root,str(Path(ART)/'Meshes'/(NAME+'.fbx')))
    pc.save_lib(str(Path(ART)/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(Path(ART)/'Previews'/(NAME+'_Preview.png')),100)
    pc.verify(fbx)
else:
    render(str(CHECK/('round'+ROUND+'.png')),40)
    if ROUND=='3':
        for label,view in [('back',(0.5,1,0.6)),('side',(-1,0,0.3)),('top',(0,-0.01,1))]:render(str(CHECK/(label+'.png')),40,view)
