# PRD-05 Apple pomace in a tray; headless Blender 5.2.
import bpy,bmesh,math,os,sys,random
from mathutils import Vector
ROOT=r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE=os.path.join(ROOT,'.work','models','Farm_Processing','PRD05_PomaceTray')
sys.path.insert(0,os.path.join(ROOT,'.work','models','Farm_Processing','_common'))
import processing_common as pc
from processing_common import Part,chamf_rect
ART=os.path.join(ROOT,'art','Farm_Processing')
NAME='FMS_Workshop_PRD_05'; ID='PRD05'
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=ARGS[0] if ARGS else 'build'
CHECK_DIR=os.path.join(os.environ['TEMP'],'FarmProcessing_check',ID)
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#B39C74','#5A3C26','#EADAB4','#E8C9A0','#C0503E','#B24034']
CFG=dict(view=(-0.60,-1.4,0.88),fill=(0.80,0.88))

def path_sweep(P,cname,pts,up,sec,slot,slot_cap):
    # Copied from approved TOL07_Funnel: mitred open loop, attachment ends buried.
    up=Vector(up); rings=[]
    for i,c in enumerate(pts):
        d1=(c-pts[i-1]).normalized() if i>0 else None
        d2=(pts[i+1]-c).normalized() if i<len(pts)-1 else None
        t=(d1+d2).normalized() if d1 and d2 else (d1 or d2)
        k=1/t.dot(d1) if d1 and d2 else 1
        sd=t.cross(up).normalized(); uu=sd.cross(t).normalized()
        rings.append([c+sd*x*k+uu*y for x,y in sec])
    return P.loft(cname,rings,slot,slot_cap,slot_cap)

def build_geometry():
    P=Part('Body'); rng=random.Random(305)
    # Continuous thick shell including rim, cavity, and flat bottom.
    prof=[(.430,.280,.018,0),(.444,.294,.022,.008),(.482,.332,.025,.100),(.500,.350,.025,.102),(.500,.350,.025,.116),(.492,.342,.023,.120),(.448,.298,.019,.120),(.406,.256,.014,.012)]
    P.loft('Tray',[[Vector((x,y,z)) for x,y in chamf_rect(w,d,c)] for w,d,c,z in prof],lambda j,k:[8,7,8,7,9,9,8][j],8,8,ground=True)
    for sign in [-1,1]:
        coords=[(.237,-.057),(.287,-.057),(.302,-.042),(.302,.042),(.287,.057),(.237,.057)]
        pts=[Vector((sign*x,y,.101+max(0,x-.237)*.30)) for x,y in coords]
        path_sweep(P,'Handle_'+str(sign),pts,(0,0,1),[(.008,-.008),(.008,.008),(-.008,.008),(-.008,-.008)],7,8)
    # Closed 8x5 quad fill: coarse red height variation, no texture noise.
    NX,NY=8,5; W,D=.440,.290
    grid=[]
    for j in range(NY+1):
        row=[]
        for i in range(NX+1):
            x=-W/2+W*i/NX; y=-D/2+D*j/NY
            if i in (0,NX) and j in (0,NY): x*=.955; y*=.955
            edge=i in (0,NX) or j in (0,NY)
            z=.084 if edge else rng.uniform(.089,.109)
            row.append(P.bm.verts.new((x,y,z)))
        grid.append(row)
    fs=[]
    for j in range(NY):
        for i in range(NX): fs.append(P.face([grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]],rng.choice([5,5,14,15])))
    tri_result=bmesh.ops.triangulate(P.bm,faces=list(fs),quad_method='BEAUTY')
    fs=tri_result['faces']
    boundary=grid[0]+[grid[j][-1] for j in range(1,NY+1)]+list(reversed(grid[-1][:-1]))+[grid[j][0] for j in range(NY-1,0,-1)]
    bottom=[P.bm.verts.new((v.co.x*.93,v.co.y*.93,.011)) for v in boundary]
    for i,v in enumerate(boundary): fs.append(P.face([v,boundary[(i+1)%len(boundary)],bottom[(i+1)%len(bottom)],bottom[i]],6))
    fs.append(P.face(list(reversed(bottom)),6)); P.comp.append(('PomaceBase',fs,False))
    def height(x,y):
        u=(x+W/2)/W*NX; v=(y+D/2)/D*NY
        i=max(0,min(NX-1,int(u))); j=max(0,min(NY-1,int(v))); u-=i; v-=j
        return grid[j][i].co.z*(1-u)*(1-v)+grid[j][i+1].co.z*u*(1-v)+grid[j+1][i].co.z*(1-u)*v+grid[j+1][i+1].co.z*u*v
    # Polish: 30 rounded low-poly chunks, with a hexagonal foot, smaller
    # triangular upper ring and a shallow offset crown vertex. Squash Z to0.7.
    for j in range(5):
        for i in range(6):
            x=(i-2.5)*.066+rng.uniform(-.010,.010)
            y=(j-2)*.048+rng.uniform(-.008,.008)
            diameter=rng.uniform(.044,.050); z=height(x,y)
            angle=rng.uniform(0,2*math.pi); aspect=rng.uniform(.85,1.05)
            points=[]
            for count,scale,h,phase in [(6,1,-.005,0),(3,.76,.016,.18)]:
                for q in range(count):
                    t=angle+q*2*math.pi/count+phase
                    radius=diameter*.5*scale*rng.uniform(.94,1.06)
                    xx=math.cos(t)*radius; yy=math.sin(t)*radius*aspect
                    zz=min(.116,z+.7*(h+rng.uniform(-.002,.002)))
                    points.append(P.bm.verts.new((x+xx,y+yy,zz)))
            points.append(P.bm.verts.new((x+rng.uniform(-.003,.003),y+rng.uniform(-.003,.003),min(.118,z+.7*.026))))
            hull=bmesh.ops.convex_hull(P.bm,input=points,use_existing_faces=False)
            faces=[f for f in hull['geom'] if isinstance(f,bmesh.types.BMFace)]
            for f in faces: f[P.slot]=5 if rng.random()<.82 else 6
            P.comp.append(('Chunk_%02d'%(j*6+i),faces,False))
    # Project flecks onto the actual top (base or chunks), then sink their lower half.
    from mathutils.bvhtree import BVHTree
    P.bm.verts.index_update()
    food_faces=[f for nm,fs,g in P.comp if nm.startswith('Chunk') or nm=='PomaceBase' for f in fs]
    tree=BVHTree.FromPolygons([v.co for v in P.bm.verts],[[v.index for v in f.verts] for f in food_faces])
    for k in range(22):
        x=(k%6-2.5)*.065+rng.uniform(-.019,.019)
        y=(k//6-1.5)*.061+rng.uniform(-.016,.016)
        hit=tree.ray_cast(Vector((x,y,.3)),Vector((0,0,-1)))[0]
        z=hit.z if hit else height(x,y); a=rng.random()*6.28; w=rng.uniform(.014,.021)
        tri=[(math.cos(a+t*2*math.pi/3)*w*.65,math.sin(a+t*2*math.pi/3)*w*.48) for t in range(3)]
        # A broad, almost flat triangular chip, closed by a buried lower vertex.
        # Four triangles retain real thickness without spending on hidden side quads.
        upper=[P.bm.verts.new((x+u,y+v,z+.002+rng.uniform(0,.001))) for u,v in tri]
        lower=P.bm.verts.new((x,y,z-.004))
        fs=[P.face(upper,13)]
        for q in range(3): fs.append(P.face([upper[q],lower,upper[(q+1)%3]],13))
        P.comp.append(('Fleck_%02d'%k,fs,False))
    skip=[nm for nm,fs,g in P.comp if nm not in ('Tray','Handle_-1','Handle_1')]
    for nm,fs,g in P.comp: print('COMPONENT',nm,sum(len(f.verts)-2 for f in fs))
    check=pc.comp_checks(P,mirror_skip=skip)
    assert check['nonmanifold']==check['loose']==check['degenerate']==0
    assert check['mirror']<1e-6 and not check['problems'],check
    # Every visible food vertex stays inside the inner rim; outer ground is flat.
    food=[v for nm,fs,g in P.comp if nm in skip for f in fs for v in f.verts]
    assert all(abs(v.co.x)<.2241 and abs(v.co.y)<.1491 and v.co.z<.124 for v in food)
    print('CONTACTS OK; tray/handles mirrorX OK; food containment OK; SNAP N/A static prop')
    return P,skip

def build():
    for ob in list(bpy.context.scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
    coll=bpy.data.collections.new(NAME); bpy.context.scene.collection.children.link(coll)
    img=pc.atlas_image('T_FarmProcessing_PRD05_BaseColor.png',os.path.join(ART,'Textures','T_FarmProcessing_PRD05_BaseColor.png'),PAL)
    mat=pc.material('M_FarmProcessing_PRD05',img)
    root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
    P,skip=build_geometry()
    ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=skip)
    bpy.context.view_layer.update(); total=pc.report({'Body':ob}); assert total<=950,total
    print('BUDGET catalogue250-600; polish allowance950; TOTAL',total)
    return coll,root,img,mat,total

def render(out, pct, view=None, lens=70):
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; r = sc.render
    saved = dict(engine=r.engine, rx=r.resolution_x, ry=r.resolution_y, pct=r.resolution_percentage, fp=r.filepath,
                 vt=sc.view_settings.view_transform, cam=sc.camera, world=sc.world)
    try: r.engine = 'BLENDER_EEVEE'
    except TypeError: r.engine = 'BLENDER_EEVEE_NEXT'
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1280, 800, pct
    r.film_transparent = False; sc.view_settings.view_transform = 'Standard'
    lin = lambda c: ((c / 255) / 12.92) if c / 255 <= 0.04045 else (((c / 255) + 0.055) / 1.055) ** 2.4
    w = bpy.data.worlds.new('TMP_World'); w.use_nodes = True; nt = w.node_tree
    outn = next(nd for nd in nt.nodes if nd.type == 'OUTPUT_WORLD'); bg = next(nd for nd in nt.nodes if nd.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (lin(0xc7), lin(0xcc), lin(0xd3), 1)
    amb = nt.nodes.new('ShaderNodeBackground'); amb.inputs['Color'].default_value = (0.82, 0.86, 0.95, 1); amb.inputs['Strength'].default_value = 0.45
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], outn.inputs['Surface']); sc.world = w
    lights = []
    for nm, rot, e, sh in (('TMP_Sun', (45, 0, -30), 3.4, True), ('TMP_Fill', (70, 0, 160), 0.9, False)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(10); ld.use_shadow = sh
        ob = bpy.data.objects.new(nm, ld); ob.rotation_euler = [math.radians(a) for a in rot]; sc.collection.objects.link(ob); lights.append(ob)
    cd = bpy.data.cameras.new('TMP_Cam'); cd.lens = lens
    cam = bpy.data.objects.new('TMP_Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    objs = [o for o in bpy.data.collections[NAME].all_objects if o.type == 'MESH']
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    target = (lo + hi) / 2; dirv = Vector(view or CFG['view']).normalized(); FW, FH = CFG['fill']
    def place(d):
        cam.location = target + dirv * d; cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update(); xs = [world_to_camera_view(sc, cam, p) for p in pts]
        return min(p.x for p in xs), max(p.x for p in xs), min(p.y for p in xs), max(p.y for p in xs)
    cd.shift_x = cd.shift_y = 0.0; d = 3.0
    for _ in range(25):
        x0, x1, y0, y1 = place(d); d *= max((x1 - x0) / FW, (y1 - y0) / FH)
    x0, x1, y0, y1 = place(d)
    cd.shift_x = ((x0 + x1) / 2 - 0.5); cd.shift_y = ((y0 + y1) / 2 - 0.5) * (800 / 1280)
    place(d)
    r.filepath = out; r.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True, scene=sc.name)
    for ob in lights:
        dat = ob.data; bpy.data.objects.remove(ob, do_unlink=True); bpy.data.lights.remove(dat)
    dat = cam.data; bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(dat)
    sc.world = saved['world']; bpy.data.worlds.remove(w)
    r.engine = saved['engine']; r.resolution_x, r.resolution_y, r.resolution_percentage = saved['rx'], saved['ry'], saved['pct']
    r.filepath = saved['fp']; sc.view_settings.view_transform = saved['vt']; sc.camera = saved['cam']
    print('rendered', out)

COLL,ROOTOB,IMG,MAT,TOTAL=build()
os.makedirs(CHECK_DIR,exist_ok=True)
if MODE=='build':
    render(os.path.join(CHECK_DIR,'round.png'),40)
    if len(ARGS)>1: render(os.path.join(CHECK_DIR,'alt.png'),40,tuple(map(float,ARGS[1].split(','))))
elif MODE=='export':
    fbx=pc.export(NAME,COLL,ROOTOB,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),COLL,MAT,IMG)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)
    assert os.path.isfile(os.path.join(ART,'Meshes',NAME+'.fbm','T_FarmProcessing_PRD05_BaseColor.png'))
    print('VERIFY texture copy found; export complete')

