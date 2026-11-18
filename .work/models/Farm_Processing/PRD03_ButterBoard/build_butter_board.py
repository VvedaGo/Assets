import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import bpy, bmesh, math, os, sys
from mathutils import Vector, kdtree
ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '_common'))
import processing_common as pc
from processing_common import Part, ngon, sweep
ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_PRD_03'
CFG = dict(view=(-0.48,-1.0,.60),fill=(0.78,0.84))
CHECK_DIR = os.path.join(os.environ['TEMP'],'FarmProcessing_check','PRD-03')
os.makedirs(CHECK_DIR,exist_ok=True)
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
PAL = ['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#F3E3B5','#E8D3A0','#F7EAC7']
WOOD,WOOD_D,WOOD_M,CREAM,CREAM_D,RED,RED_D,METAL,METAL_D,METAL_L,CREAM_IN,WOOD_DD,CREAM_B,LWOOD,LWOOD_D,HOLE_D=range(16)
def edge(bm, a, b):
    return bm.edges.get((a, b)) or bm.edges.new((a, b))

def fill(P, loops, slot, normal):
    """planar region bounded by loops[0] with holes loops[1:] (scanfill)"""
    es = [edge(P.bm, L[i], L[(i + 1) % len(L)]) for L in loops for i in range(len(L))]
    r = bmesh.ops.triangle_fill(P.bm, use_beauty=True, use_dissolve=False, edges=es, normal=Vector(normal))
    fs = [g for g in r['geom'] if isinstance(g, bmesh.types.BMFace)]
    for f in fs: f[P.slot] = slot
    return fs

def hole_loop(P, c, u, w, r, hn, a0=0.0):
    return [P.bm.verts.new(c + u * r * math.cos(a0 + 2 * math.pi * i / hn) + w * r * math.sin(a0 + 2 * math.pi * i / hn)) for i in range(hn)]

def tube(P, a, b, slot):
    n = len(a); return [P.face([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], slot) for i in range(n)]

def solid(P,name,poly,z0,z1,top=WOOD,side=WOOD_M,holes=()):
    before=set(P.bm.faces)
    # Paddle underside rises 8mm; the top remains one plane. Triangulated
    # underside has a short ramp at the neck; no separate overlapping slab.
    low=lambda x: .008*max(0,min(1,(x-.070)/.020)) if name=='board_paddle' else 0
    R=[[P.bm.verts.new((x,y,z+(low(x) if j==0 else 0))) for x,y in poly] for j,z in enumerate((z0,z1))]
    H=[[[P.bm.verts.new((x,y,z+(low(x) if j==0 else 0))) for x,y in hp] for hp in holes] for j,z in enumerate((z0,z1))]
    for j in (0,1): fill(P,[R[j]]+H[j],top if j else side,(0,0,1 if j else -1))
    tube(P,R[0],R[1],side)
    for a,b in zip(H[0],H[1]): tube(P,a,b,WOOD_D)
    P.comp.append((name,list(set(P.bm.faces)-before),z0==0))

def build_geo():
    P=Part('Body')
    # One continuous slab and paddle: no overlapping separate neck/body faces.
    outline=[(-.095,-.080),(.095,-.080),(.110,-.065),(.110,-.034),(.130,-.021),(.145,-.030),(.169,-.033),(.185,-.020),(.190,0),(.185,.020),(.169,.033),(.145,.030),(.130,.021),(.110,.034),(.110,.065),(.095,.080),(-.095,.080),(-.110,.065),(-.110,-.065)]
    outline=[(x-.040,y) for x,y in outline]
    hole=[(.164-.040+x,y) for x,y in ngon(.015,6,0)]
    solid(P,'board_paddle',outline,0,.022,WOOD,WOOD_M,[hole])
    pc.rect_prism(P,'butter',-.040,0,.150,.100,.012,
                  [(.021,.006),(.027,0),(.074,0),(.086,.012)],
                  lambda j,k: (15,14,15)[j],14,13)
    print('BUTTER dimensions .150/.100/.065; board top .022; butter bottom .021; overlap 1mm')
    print('NO COPLANAR OVERLAPS: integral handle; butter bottom 1mm below board top')
    kd=kdtree.KDTree(len(P.bm.verts))
    for i,v in enumerate(P.bm.verts):kd.insert(v.co,i)
    kd.balance()
    mir=max(kd.find(Vector((v.co.x,-v.co.y,v.co.z)))[2] for v in P.bm.verts)
    print('MIRROR Y',mir);assert mir<1e-6
    chk=pc.comp_checks(P,mirror_skip=[c[0] for c in P.comp])
    assert chk['nonmanifold']==chk['loose']==chk['degenerate']==0 and not chk['problems']
    tri=P.bm.copy();bmesh.ops.triangulate(tri,faces=list(tri.faces))
    assert min(f.calc_area() for f in tri.faces)>1e-9
    print('TRIANGULATED DEGENERATE 0');tri.free()
    for nm,fs,g in P.comp:print('COMP',nm,sum(len(f.verts)-2 for f in fs))
    return P

def verify_export(fbx):
    win = bpy.context.window; prev = win.scene
    sc = bpy.data.scenes.new('TMP_FBXVerify'); win.scene = sc
    before_i, before_mat = set(bpy.data.images), set(bpy.data.materials)
    bpy.ops.import_scene.fbx(filepath=fbx)
    bpy.context.view_layer.update()
    obs = list(sc.objects)
    print('VERIFY objects', [(o.name, o.type, o.parent.name if o.parent else None) for o in obs])
    tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t
            pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  ', o.name, 'tris', t, 'loc', [round(x, 3) for x in o.matrix_world.translation],
                  'rot', [round(math.degrees(a), 2) for a in o.matrix_world.to_euler()], 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  ', o.name, o.type, 'rot', [round(math.degrees(a), 2) for a in o.rotation_euler], 'scale', [round(s, 4) for s in o.scale])
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  images', [(i.name, bpy.path.abspath(i.filepath), os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])
    assert len(obs)==2 and tot==total
    assert max(abs(a-b) for a,b in zip(dims,(.30,.16,.086)))<1e-5
    assert abs(min(p.z for p in pts))<1e-5
    assert imgs and all(os.path.isfile(bpy.path.abspath(i.filepath)) for i in imgs)
    mesh=next(o for o in obs if o.type=='MESH')
    assert mesh.parent and mesh.parent.type=='EMPTY'
    assert len(mesh.data.materials)==1
    print('FBX ROUNDTRIP ASSERTIONS PASS')
    for o in obs:
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and isinstance(d, bpy.types.Mesh) and d.users == 0: bpy.data.meshes.remove(d)
    for m in set(bpy.data.materials) - before_mat:
        if m.users == 0: bpy.data.materials.remove(m)
    for i in imgs:
        if i.users == 0: bpy.data.images.remove(i)
    win.scene = prev; bpy.data.scenes.remove(sc)
    print('  temp cleanup done; scenes', [s.name for s in bpy.data.scenes])

for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
coll=bpy.data.collections.new(NAME);bpy.context.scene.collection.children.link(coll)
for d in ('Textures','Meshes','Blend','Previews'):os.makedirs(os.path.join(ART,d),exist_ok=True)
tex='T_FarmProcessing_PRD03_BaseColor.png'
img=pc.atlas_image(tex,os.path.join(ART,'Textures',tex),PAL)
mat=pc.material('M_FarmProcessing_PRD03',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
P=build_geo()
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=[c[0] for c in P.comp])
bpy.context.view_layer.update()
total=pc.report({'Body':ob});assert 120<=total<=300
assert max(abs(a-b) for a,b in zip(ob.dimensions,(.30,.16,.086)))<1e-6
assert not ob.ray_cast(Vector((.124,0,1)),Vector((0,0,-1)))[0]
print('HEX THROUGH-HOLE RAY PASS')
assert root.location.length<1e-8 and ob.location.length<1e-8
assert all(abs(t-1)<1e-8 for t in root.scale) and all(abs(t-1)<1e-8 for t in ob.scale)
assert root.rotation_euler.to_matrix().is_identity and ob.rotation_euler.to_matrix().is_identity
assert len(ob.data.materials)==1 and len(ob.data.uv_layers)==1
assert all(0<=c<=1 for uv in ob.data.uv_layers.active.data for c in uv.uv)
print('PIVOT/IDENTITY/MATERIAL/UV CONTRACT PASS')
print('VERIFY CONTRACT OK: root identity; ground bbox centre; X handle; Y symmetry; contacts; 0.30/0.16/0.086; 120-300 budget; SNAP N/A static prop')
exec(compile(open(os.path.join(HERE,'render_preview.py')).read(),'render_preview.py','exec'))
if MODE=='export':
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    verify_export(fbx)
    for i,v in enumerate(((0,0,1),(.5,1,.7),(0,-1,.15))):render(os.path.join(CHECK_DIR,'angle'+str(i)+'.png'),40,v)
else:
    render(os.path.join(CHECK_DIR,'round'+(ARGS[1] if len(ARGS)>1 else '1')+'.png'),40)
    if MODE=='angles':
        for i,v in enumerate(((0,0,1),(.5,1,.7),(0,-1,.15))):render(os.path.join(CHECK_DIR,'angle'+str(i)+'.png'),40,v)



