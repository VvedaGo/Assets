# TOL-09 Grain scoop, headless Blender 5.2. Run with -- build|views|export.
# Helpers copied from TOL_Tools; processing_common is read-only.
import bpy, bmesh, math, os, sys, importlib
from mathutils import Vector, Matrix

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'TOL09_GrainScoop')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ID = 'TOL09'
MODE = ARGS[0] if ARGS else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'TOL09')

# ---------------- palette: cells 0-12 identical to STA-03/STA-05 ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#B39C74', '#5A3C26',      # cell 10 darker than STA-05 (#C7B288) so perforations read
       '#EADAB4', '#C99263', '#A26A43', '#857B6E']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, HWOOD, BLADE, FOOT = range(16)

def oct_rod(P, cname, p0, p1, radii, slot, slot_cap, n=8, ref=(0, 0, 1)):
    """octagonal rod along p0->p1, radii = [(t, r)]"""
    r0 = max(r for _, r in radii)
    sweep(P, cname, p0, p1, ngon(r0, n, math.pi / n), [(t, r / r0, 0) for t, r in radii], slot, slot_cap, slot_cap, ref=ref)

def center_on_ground(P):
    vs = list(P.bm.verts)
    lo = [min(v.co[i] for v in vs) for i in range(3)]; hi = [max(v.co[i] for v in vs) for i in range(3)]
    off = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]))
    for v in vs: v.co -= off


# Hollow wood shell: matched outer/inner polygon loops, lowered front lip.
def build_scoop():
    P = Part('Body')
    plan=[(-.050,-.160),(.050,-.160),(.075,-.117),(.075,.016),(.044,.055),(-.044,.055),(-.075,.016),(-.075,-.117)]
    # Shorten only rearward station spacing: trough is 59.4% of total length.
    plan=[(x,-.160+(y+.160)*(.190/.215)) for x,y in plan]
    heights=[.018,.018,.061,.075,.075,.075,.075,.061]
    bottom=[(x*.72, y if y<-.15 else y-.014, 0) for x,y in plan]
    top=[(x,y,z) for (x,y),z in zip(plan,heights)]
    inner_top=[(x-(.012 if x>0 else -.012),y+(.008 if y<-.15 else -.012 if y>.0 else 0),z) for (x,y),z in zip(plan,heights)]
    floor=[(x*.72-(.007 if x>0 else -.007), y if y<-.15 else y-.023,.012) for x,y in plan]
    chine=[(x*.94,y if y<-.15 else y-.005,.007 if y<-.15 else .025) for x,y in plan]
    rings=[bottom,chine,top,inner_top,floor]
    P.loft('scoop_shell',rings,lambda j,k: (WOOD_M,WOOD,WOOD,WOOD_M)[j],WOOD_D,WOOD_D,ground=True)
    # Closed solid sleeve: no bore/open arch; front cap matches back-wall slope.
    # Back wall exterior: Y=.025 at Z=.025, Y=.030 at Z=.075.
    axis_z=.0525
    outer=.0275/math.cos(math.pi/8)
    rear=[]; front=[]
    for k in range(8):
        angle=math.pi/8+k*math.pi/4
        x=outer*math.sin(angle); z=axis_z+outer*math.cos(angle)
        front.append((x,.025+.1*(z-.025),z))
        rear.append((x,.054,z))
    P.loft('red_collar',[front,rear],RED,RED_D,RED_D)
    oct_rod(P,'wood_grip',(0,.030,axis_z),(0,.160,axis_z),
            [(0,.0175/math.cos(math.pi/8)),(.70,.0225/math.cos(math.pi/8)),(.91,.0225/math.cos(math.pi/8)),(1,.017)],
            lambda j,k: WOOD_D if k in (2,3,4,5) else WOOD_M,WOOD_D)
    print('HANDLE grip length .130 m = 40.6% of .320; exposed wood .106 m; collar .055 AF x .025; grip .035 to .045 AF')
    print('COLLAR axis z',axis_z,'bottom',axis_z-.0275,'top',axis_z+.0275,'solid closed sleeve, front cap flush to sloping back wall; rim overlap .025..075')
    center_on_ground(P)
    for nm, fs, ground in P.comp:
        print('COMPONENT', nm, 'tris',sum(len(f.verts)-2 for f in fs))
    result=pc.comp_checks(P)
    assert result['nonmanifold']==result['loose']==result['degenerate']==0
    assert result['mirror']<1e-6 and not result['problems']
    return P

CFG=dict(build=build_scoop,budget=(100,250),view=(.85,-1.0,.80),fill=(.74,.83))
NAME='FMS_Workshop_TOL_09'; IDN='TOL09'
TEX_NAME=f'T_FarmProcessing_{IDN}_BaseColor.png'; MAT_NAME=f'M_FarmProcessing_{IDN}'
def clear_scene():
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    return coll

def build():
    coll = clear_scene()
    img = pc.atlas_image(TEX_NAME, os.path.join(ART, 'Textures', TEX_NAME), PAL); mat = pc.material(MAT_NAME, img)
    root = bpy.data.objects.new(NAME, None); root.empty_display_size = 0.1; coll.objects.link(root)
    P = CFG['build']()
    obs = {'Body': pc.to_object(P, NAME, coll, mat, (0, 0, 0), root)}
    bpy.context.view_layer.update()
    tot = pc.report(obs)
    lo, hi = CFG['budget']
    assert lo <= tot <= hi
    print(f'  budget {lo}-{hi} ->', 'OK' if lo <= tot <= hi else f'OVER x{tot / hi:.2f}' if tot > hi else 'UNDER')
    return obs, root, coll, img, mat

# ---------------- preview (STA-03 render_preview.py logic, CONFIG from the registry) ----------------
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


OBS, ROOTOB, COLL, IMG, MAT = build()
os.makedirs(CHECK_DIR,exist_ok=True)
if MODE == 'build':
    render(os.path.join(CHECK_DIR,'TOL09_check.png'),40)
    if len(ARGS)>1:
        render(os.path.join(CHECK_DIR,'TOL09_alt.png'),40,tuple(float(x) for x in ARGS[1].split(',')))
elif MODE == 'views':
    for label, view in [('front',(0,-1,.35)),('side',(1,0,.35)),('rear',(.6,1,.65)),('bottom',(0,0,-1))]:
        render(os.path.join(CHECK_DIR,label+'.png'),40,view)
elif MODE == 'export':
    fbx=pc.export(NAME,COLL,ROOTOB,os.path.join(ART,'Meshes',NAME+'.fbx'))
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),COLL,MAT,IMG)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
    pc.verify(fbx)

