# TOL-01..05 small processing tools -> FMS_Workshop_TOL_0X (Farm Processing pack). One parametric script, registry by ID.
# Headless, idempotent:
#   PYTHONUTF8=1 blender.exe --background --factory-startup --python build_tools.py -- <ID> <mode>
#   ID: TOL01 mold | TOL02 harp | TOL03 spatula | TOL04 colander | TOL05 ladle
#   mode: build  = build + checks + check renders to %TEMP%\FarmProcessing_check\TOL\<ID>_*.png
#         export = build + checks + FBX + .blend lib + final preview + FBX re-import verify
# Shared helpers (read-only): ../_common/processing_common.py. Tools have no moving parts: root empty + one child _Body.
import bpy, bmesh, math, os, sys, importlib
from mathutils import Vector, Matrix

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
HERE = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', 'TOL06_MeasuringJug')
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, sweep, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ID = ARGS[0] if ARGS else 'TOL06'
MODE = ARGS[1] if len(ARGS) > 1 else 'build'
CHECK_DIR = os.path.join(os.environ.get('TEMP', HERE), 'FarmProcessing_check', 'TOL06')

# ---------------- palette: cells 0-12 identical to STA-03/STA-05 ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#B39C74', '#5A3C26',      # cell 10 darker than STA-05 (#C7B288) so perforations read
       '#EADAB4', '#C99263', '#A26A43', '#857B6E']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, HWOOD, BLADE, FOOT = range(16)

# ---------------- generic helpers ----------------
def ringco(z, apo, n, phase=0.5):
    rc = apo / math.cos(math.pi / n)
    return [Vector((rc * math.cos(-math.pi / 2 + (k + phase) * 2 * math.pi / n), rc * math.sin(-math.pi / 2 + (k + phase) * 2 * math.pi / n), z)) for k in range(n)]

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

def shell(P, cname, prof, n, side_slot, cap0, cap1, holes=None, pairs=(), hole_slot=CREAM_IN, cap_holes=None, hn=6, ground=True):
    """n-gon solid of revolution. prof: [(z, apothem)] closed section path (outer bottom -> up -> rim -> down inside -> floor).
    holes: {band j: (radius, skip_facets)} a hole through every facet of band j; pairs: [(outer band, inner band)] -> tubes.
    cap_holes: [(x, y, r)] holes through both caps (prof[0] and prof[-1]), joined by vertical tubes."""
    holes = holes or {}
    R = [[P.bm.verts.new(v) for v in ringco(z, a, n)] for z, a in prof]; faces = []; H = {}
    for j in range(len(R) - 1):
        for k in range(n):
            A, B, C, D = R[j][k], R[j][(k + 1) % n], R[j + 1][(k + 1) % n], R[j + 1][k]
            s = side_slot(j, k) if callable(side_slot) else side_slot
            if j in holes and k not in holes[j][1]:
                c = (A.co + B.co + C.co + D.co) / 4; u = (B.co - A.co).normalized()
                w = (C.co + D.co) / 2 - (A.co + B.co) / 2; w = (w - u * w.dot(u)).normalized()
                if w.z < 0: w = -w
                hl = hole_loop(P, c, u, w, holes[j][0], hn); H[(j, k)] = hl
                faces += fill(P, [[A, B, C, D], hl], s, u.cross(w))
            else:
                faces.append(P.face([A, B, C, D], s))
    def cap(ring, z, slot):
        if not cap_holes: return [P.face(list(ring), slot)], []
        hls = [hole_loop(P, Vector((x, y, z)), Vector((1, 0, 0)), Vector((0, 1, 0)), r, hn) for x, y, r in cap_holes]
        return fill(P, [ring] + hls, slot, (0, 0, 1)), hls
    f0, h0 = cap(R[0], prof[0][0], cap0); f1, h1 = cap(R[-1], prof[-1][0], cap1); faces += f0 + f1
    for a, b in zip(h0, h1): faces += tube(P, a, b, hole_slot)
    for jo, ji in pairs:
        for k in range(n):
            if (jo, k) in H: faces += tube(P, H[(jo, k)], H[(ji, k)], hole_slot)
    P.comp.append((cname, faces, ground))

def path_sweep(P, cname, pts, up, sec, slot, slot_cap):
    """sweep a 2D section [(side, up)] along a polyline with mitred joints (thickness kept in the bends)"""
    up = Vector(up); rings = []
    for i, c in enumerate(pts):
        d1 = (c - pts[i - 1]).normalized() if i > 0 else None
        d2 = (pts[i + 1] - c).normalized() if i < len(pts) - 1 else None
        t = (d1 + d2).normalized() if d1 and d2 else (d1 or d2)
        k = 1.0 / t.dot(d1) if d1 and d2 else 1.0
        sd = t.cross(up).normalized(); uu = sd.cross(t).normalized()
        rings.append([c + sd * x * k + uu * y for x, y in sec])
    return P.loft(cname, rings, slot, slot_cap, slot_cap)

def bolt(P, p0, axis, r=0.008, h=0.010, sunk=0.003):
    a = Vector(axis).normalized(); p0 = Vector(p0)
    ref = (0, 0, 1) if abs(a.z) < 0.9 else (1, 0, 0)
    sweep(P, 'bolt', p0 - a * sunk, p0 + a * h, ngon(r, 6, math.pi / 2), [(0, 1, 0), (1, 0.75, 0)], METAL, METAL, METAL_L, ref=ref)

def oct_rod(P, cname, p0, p1, radii, slot, slot_cap, n=8, ref=(0, 0, 1)):
    """octagonal rod along p0->p1, radii = [(t, r)]"""
    r0 = max(r for _, r in radii)
    sweep(P, cname, p0, p1, ngon(r0, n, math.pi / n), [(t, r / r0, 0) for t, r in radii], slot, slot_cap, slot_cap, ref=ref)

def rest_on_ground(P):
    """tilt about X so the lowest point of the front half and of the back half both touch z=0 (a tool lying on a table)"""
    vs = list(P.bm.verts); yc = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    def f(a):
        c, s = math.cos(a), math.sin(a)
        zf = min(v.co.z * c + v.co.y * s for v in vs if v.co.y < yc); zb = min(v.co.z * c + v.co.y * s for v in vs if v.co.y >= yc)
        return zf - zb
    lo, hi = math.radians(-20), math.radians(20)
    for _ in range(60):
        m = (lo + hi) / 2
        if (f(lo) > 0) == (f(m) > 0): lo = m
        else: hi = m
    a = (lo + hi) / 2; M = Matrix.Rotation(-a, 4, 'X')
    for v in vs: v.co = M @ v.co
    print(f'  rest tilt {math.degrees(a):.2f} deg')

def center_on_ground(P):
    vs = list(P.bm.verts)
    lo = [min(v.co[i] for v in vs) for i in range(3)]; hi = [max(v.co[i] for v in vs) for i in range(3)]
    off = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]))
    for v in vs: v.co -= off


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

def verify(fbx):
    sc = bpy.context.scene
    for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
    before_i = set(bpy.data.images)
    bpy.ops.import_scene.fbx(filepath=fbx); bpy.context.view_layer.update()
    obs = list(sc.objects); tot = 0; pts = []
    for o in obs:
        if o.type == 'MESH':
            t = sum(len(p.vertices) - 2 for p in o.data.polygons); tot += t; pts += [o.matrix_world @ v.co for v in o.data.vertices]
            print('  VERIFY', o.name, 'parent', o.parent.name if o.parent else None, 'tris', t, 'scale', [round(s, 4) for s in o.matrix_world.to_scale()])
        else:
            print('  VERIFY', o.name, o.type)
    dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
    imgs = [i for i in bpy.data.images if i not in before_i]
    print('  VERIFY nodes', len(obs), 'total tris', tot, 'dims', [round(x, 3) for x in dims], 'minz', round(min(p.z for p in pts), 4))
    print('  VERIFY images', [(i.name, os.path.isfile(bpy.path.abspath(i.filepath)), tuple(i.size)) for i in imgs])


NAME='FMS_Workshop_TOL_06'; ID='TOL06'
TEX_NAME='T_FarmProcessing_TOL06_BaseColor.png'; MAT_NAME='M_FarmProcessing_TOL06'
CFG={'view':(-0.35,-1.0,0.57),'fill':(.78,.88)}

def jug():
    P=Part('Body')
    # Closed 13-vertex shell: original 12-gon plus a centre vertex at -X.
    # The shoulder vertices sit +/-40 degrees from -X; three vertices follow
    # each straight V side. Every rim and inner ring shares that exact outline.
    prof=[(0,.094),(.005,.100),(.036,.100),(.036,.096),(.195,.08382),
          (.284,.077),(.284,.081),(.296,.081),(.297,.077),(.291,.071),
          (.195,.07754),(.012,.090)]
    angles=[15,45,75,105,140,165,180,195,220,255,285,315,345]
    rings=[]
    for z,apo in prof:
        r=apo*1.3/math.cos(math.pi/12)
        ring=[]
        for deg in angles:
            ang=math.radians(deg); x,y=r*math.cos(ang),r*math.sin(ang); zz=z
            if z>.28 and 140<=deg<=220:
                # Keep +/-40 degree shoulders on the circular body outline;
                # place intermediate points on straight lines to the raised tip.
                side_y=r*math.sin(math.radians(40))
                tip_x=-(apo*1.3+.050)
                f=abs(y)/side_y
                x=tip_x*(1-f)-r*math.cos(math.radians(40))*f
                zz+=.010*(1-f)
            ring.append(Vector((x,y,zz)))
        rings.append(ring)
    P.loft('vessel',rings,lambda j,k:(15,15,15,CREAM,CREAM,METAL_D,METAL,METAL_L,METAL,CREAM_B,CREAM_B)[j],15,CREAM_D,ground=True)
    print('SPOUT shoulders +/-40deg, extension .050m, tip rise .010m, blend z .195m')
    # Short 4x5cm plates sit directly on the +X wall, with 6mm proud faces.
    for z in (.255,.105):
        x=1.3*(.096+(.077-.096)*(z-.036)/(.284-.036))
        sweep(P,'plate',(x-.003,0,z),(x+.006,0,z),chamf_rect(.040,.050,.007),
              [(0,1,0),(.75,1,0),(1,.88,0)],METAL,METAL_D,METAL_L,ref=(0,1,0))
        sweep(P,'red_hex_bolt',(x+.004,-.027,z),(x+.004,.027,z),ngon(.008,6,math.pi/2),
              [(0,1,0),(1,1,0)],RED_D,RED,RED,ref=(1,0,0))
    pts=[Vector(p) for p in [(.108,0,.255),(.144,0,.268),(.168,0,.242),(.168,0,.139),(.148,0,.113),(.123,0,.105)]]
    path_sweep(P,'handle',pts,(0,1,0),chamf_rect(.030,.030,.004),RED,RED_D)
    print('HANDLE section .030m chamfer .004m, reach approx .070m, wall plates .040x.050m proud .006m')
    center_on_ground(P)
    # Axis-specific symmetry, so asymmetrical spout/handle do not produce a false failure.
    from mathutils import kdtree
    vs=list(P.bm.verts); kd=kdtree.KDTree(len(vs))
    for i,v in enumerate(vs): kd.insert(v.co,i)
    kd.balance(); err=max(kd.find(Vector((v.co.x,-v.co.y,v.co.z)))[2] for v in vs)
    print('MIRROR Y',round(err,8),'X skipped: spout and handle; apothem ratio',.096/.077)
    assert err<1e-6
    checks=pc.comp_checks(P,mirror_skip=tuple(c[0] for c in P.comp))
    assert not any(checks[k] for k in ['nonmanifold','loose','degenerate','problems'])
    # Explicit triangles keep the nonplanar chute surfaces identical in render and FBX.
    comps=[]
    for nm,fs,ground in P.comp:
        result=bmesh.ops.triangulate(P.bm,faces=fs,quad_method='BEAUTY',ngon_method='BEAUTY')
        comps.append((nm,list(result['faces']),ground))
    P.comp=comps
    for nm,fs,_ in P.comp: print('COMP',nm,'tris',sum(len(f.verts)-2 for f in fs))
    return P

def build():
    for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o,do_unlink=True)
    coll=bpy.data.collections.new(NAME); bpy.context.scene.collection.children.link(coll)
    for folder in ['Textures','Meshes','Blend','Previews']: os.makedirs(os.path.join(ART,folder),exist_ok=True)
    img=pc.atlas_image(TEX_NAME,os.path.join(ART,'Textures',TEX_NAME),PAL)
    mat=pc.material(MAT_NAME,img)
    root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
    P=jug(); skips=tuple(c[0] for c in P.comp)
    ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=skips)
    bpy.context.view_layer.update(); total=pc.report({'Body':ob}); assert 200<=total<=560
    print('BUDGET OK 200-560 (lead handle polish budget); CONTACT OK; ground bbox pivot OK; no moving parts')
    return coll,root,img,mat

if __name__=='__main__':
    coll,root,img,mat=build(); os.makedirs(CHECK_DIR,exist_ok=True)
    if MODE=='export':
        fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx'))
        pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
        render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)
        verify(fbx)
    else:
        render(os.path.join(CHECK_DIR,'round'+MODE+'.png'),40)
        if MODE=='3':
            for nm,v in [('back',(0.5,1,.45)),('spout',(-1,-.3,.45)),('top',(.1,-.2,1))]: render(os.path.join(CHECK_DIR,nm+'.png'),30,v)

