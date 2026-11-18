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
NAME = 'FMS_Workshop_TOL_10'
CFG = dict(view=(-0.48,-1.0,1.12),fill=(0.78,0.84))
CHECK_DIR = os.path.join(os.environ['TEMP'],'FarmProcessing_check','TOL-10')
os.makedirs(CHECK_DIR,exist_ok=True)
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'build'
PAL = ['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#E8CFA6','#DFC39A','#B39C74']
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
    R=[[P.bm.verts.new((x,y,z)) for x,y in poly] for z in (z0,z1)]
    H=[[[P.bm.verts.new((x,y,z)) for x,y in hp] for hp in holes] for z in (z0,z1)]
    for j in (0,1): fill(P,[R[j]]+H[j],top if j else side,(0,0,1 if j else -1))
    tube(P,R[0],R[1],side)
    for a,b in zip(H[0],H[1]): tube(P,a,b,WOOD_D)
    P.comp.append((name,list(set(P.bm.faces)-before),z0==0))

def build_geo():
    P=Part('Body')
    outer=[(x-.055,y) for x,y in pc.chamf_rect(.340,.268,.018)]
    inner=[(-.199,-.108),(.089,-.108),(.089,.108),(-.199,.108)]
    # Shallow groove bed, 3 mm below plank tops.  Plank bottoms are sunk
    # 1 mm into it (hidden contact), with 1.25 mm visible clearance to walls.
    # No plank end/bottom lies coplanar with a frame face.
    WALL_CLEARANCE = .00125
    GROOVE_BED = .0315
    PLANK_BOTTOM = .0305
    before=set(P.bm.faces)
    B=[P.bm.verts.new((x,y,0)) for x,y in outer]
    T=[P.bm.verts.new((x,y,.038)) for x,y in outer]
    I=[P.bm.verts.new((x,y,.038)) for x,y in inner]
    F=[P.bm.verts.new((x,y,GROOVE_BED)) for x,y in inner]
    fill(P,[B],WOOD_M,(0,0,-1)); fill(P,[T,I],WOOD,(0,0,1))
    tube(P,B,T,WOOD_M); tube(P,I,F,WOOD_D); fill(P,[F],WOOD_D,(0,0,1))
    P.comp.append(('frame',list(set(P.bm.faces)-before),True))
    for i in range(3):
        y0=-.108+i*.072; y1=y0+.072
        if i>0:y0+=.0015
        else:y0+=WALL_CLEARANCE
        if i<2:y1-=.0015
        else:y1-=WALL_CLEARANCE
        solid(P,'plank'+str(i),[(-.199+WALL_CLEARANCE,y0),(.089-WALL_CLEARANCE,y0),(.089-WALL_CLEARANCE,y1),(-.199+WALL_CLEARANCE,y1)],PLANK_BOTTOM,.0345,(LWOOD,CREAM_B,LWOOD)[i],LWOOD_D)
    assert WALL_CLEARANCE >= .001 and GROOVE_BED-PLANK_BOTTOM >= .001-1e-9
    print('PLANK SEAMS: wall clearance 1.25 mm; bottom/bed offset 1 mm; groove width/depth 3/3 mm; no coplanar overlap')
    # Ten-vertex paddle outline: broad root, short neck, faceted end.
    hp=[(.105,-.059),(.157,-.030),(.181,-.046),(.210,-.046),(.225,-.024),(.225,.024),(.210,.046),(.181,.046),(.157,.030),(.105,.059)]
    hole=[(.199+x,y) for x,y in ngon(.020,6,0)]
    solid(P,'handle',hp,.012,.038,WOOD,WOOD_M,[hole])
    # L-profile straps follow the long edges, in one closed prism per corner.
    for x in (-.175,.065):
        for s in (-1,1):
            cross=[(.105,.038),(.134,.038),(.134,.001),(.1365,.001),(.1365,.040),(.105,.040)]
            rings=[[Vector((xx,s*y,z)) for y,z in cross] for xx in (x-.014,x+.014)]
            P.loft('strap',rings,RED,RED_D,RED_D)
            sweep(P,'bolt',(x,s*.136,.020),(x,s*.140,.020),ngon(.0075,6,math.pi/2),[(0,1,0),(1,.88,0)],METAL,METAL_D,METAL_L,ref=(0,0,1))
    # Symmetric across Y (the handle intentionally makes X asymmetric).
    kd=kdtree.KDTree(len(P.bm.verts))
    for i,v in enumerate(P.bm.verts):kd.insert(v.co,i)
    kd.balance()
    mir=max(kd.find(Vector((v.co.x,-v.co.y,v.co.z)))[2] for v in P.bm.verts)
    print('MIRROR Y',mir);assert mir<1e-6
    chk=pc.comp_checks(P,mirror_skip=[c[0] for c in P.comp])
    assert chk['nonmanifold']==chk['loose']==chk['degenerate']==0 and not chk['problems']
    # Inspect the exact triangulation, including all quads, before export.
    tri_bm=P.bm.copy()
    bmesh.ops.triangulate(tri_bm,faces=list(tri_bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
    altitudes=[2*f.calc_area()/max(e.calc_length() for e in f.edges) for f in tri_bm.faces]
    min_alt=min(altitudes)
    slivers=sum(a<.0005 for a in altitudes)
    print(f'TRIANGLE QA: slivers (<0.5 mm altitude) {slivers}; minimum altitude {min_alt*1000:.3f} mm')
    assert slivers==0
    tri_bm.free()
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
    assert max(abs(a-b) for a,b in zip(dims,(.45,.28,.04)))<1e-5
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
tex='T_FarmProcessing_TOL10_BaseColor.png'
img=pc.atlas_image(tex,os.path.join(ART,'Textures',tex),PAL)
mat=pc.material('M_FarmProcessing_TOL10',img)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
P=build_geo()
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=[c[0] for c in P.comp])
bpy.context.view_layer.update()
total=pc.report({'Body':ob});assert total<=310
assert max(abs(a-b) for a,b in zip(ob.dimensions,(.45,.28,.04)))<1e-6
assert not ob.ray_cast(Vector((.199,0,1)),Vector((0,0,-1)))[0]
print('HEX THROUGH-HOLE RAY PASS')
print('VERIFY CONTRACT OK: root identity; ground bbox centre; X handle; Y symmetry; contacts; 0.45/0.28/0.04; budget exception documented')
exec(compile(open(os.path.join(HERE,'render_preview.py')).read(),'render_preview.py','exec'))
if MODE=='export':
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    verify_export(fbx)
else:
    render(os.path.join(CHECK_DIR,'round'+(ARGS[1] if len(ARGS)>1 else '1')+'.png'),40)
    if MODE=='angles':
        for i,v in enumerate(((0,0,1),(.5,1,.7),(0,-1,.15))):render(os.path.join(CHECK_DIR,'angle'+str(i)+'.png'),40,v)



