# STA-10 Seed oil press (Farm Processing pack). Based on approved STA-05 primitives; rebuilds only its own
# collection (in its own scene FMS_Workshop_STA_10_Build). Run inside Blender: MODE = 'build' | 'export'; exec(open(__file__).read())
# Shared helpers: ../_common/processing_common.py (extracted from STA-02; build_cheese_press.py stays standalone).
import bpy, math, os, sys, importlib
from mathutils import Vector

ROOT = r"C:\Users\Sergv\orca\workspaces\VFX\master-2"
COMMON = os.path.join(ROOT, '.work', 'models', 'Farm_Processing', '_common')
if COMMON not in sys.path: sys.path.insert(0, COMMON)
import processing_common as pc
importlib.reload(pc)
from processing_common import Part, ngon, chamf_rect, inset, sweep, zprism, chamf_spec, rect_prism

ART = os.path.join(ROOT, 'art', 'Farm_Processing')
NAME = 'FMS_Workshop_STA_10'
TEX_NAME = 'T_FarmProcessing_STA10_BaseColor.png'
MAT_NAME = 'M_FarmProcessing_STA10'
MODE = globals().get('MODE', 'build')

# ---------------- palette: cells 0-12 identical to STA-02 (mergeable), 13/14 = plate grey-beige, 15 spare ----------------
PAL = ['#B5835A', '#7A5233', '#9C6B44', '#F2E6C9',
       '#DCC9A0', '#C8473B', '#A8372E', '#8E959B',
       '#6E757B', '#A9AFB4', '#C7B288', '#5A3C26',
       '#EADAB4', '#B4AA9D', '#978D82', '#B5835A']
WOOD, WOOD_D, WOOD_M, CREAM, CREAM_D, RED, RED_D, METAL, METAL_D, METAL_L, CREAM_IN, WOOD_DD, CREAM_B, PLATE, PLATE_D = range(15)

# Dimensions metres, front -Y
TT_X, TT_Y, TT_Z0, TT_Z1 = .37, .245, .335, .42
BK_Z1, BK_AO, BK_AI, STAVES = .78, .25, .224, 22
HOOPS = ((.710,.048),(.490,.048))
HOOP_T, RIVET_EVERY = .013, 3
PLATE_R, PLATE_Z0, PLATE_Z1, PLATE_N = .216,.698,.740,12
COLLAR_Z1 = .801
SP_R, SP_r, SP_Z0, SP_Z1, PITCH, TILT = .045,.037,.778,1.325,.057,.006
HUB_W, HUB_Z0, HUB_Z1 = .115,1.28,1.39
BAR_Z, BAR_HALF, BAR_R = 1.337,.325,.048
SCREW_PIVOT_Z = 1.09

def box(P,n,x,y,w,d,z0,z1,s=WOOD):
    rect_prism(P,n,x,y,w,d,.008,[(z0,.004),(z0+.004,0),(z1-.008,0),(z1,.008)],s,s,s)

def cap(P,x,y,z):
    sweep(P,'redcap',(x,y,z),(x,y-.019,z),chamf_rect(.074,.074,.007),[(0,1,0),(1,1,.004)],RED,RED,RED,ref=(0,0,1))

def build_frame():
    P=Part('Frame')
    box(P,'platform',0,0,2*TT_X,2*TT_Y,TT_Z0,TT_Z1)
    # Four full-height legs: splayed feet, narrow top stance (side A-frames).
    for sx in (-1,1):
        for sy in (-1,1):
            sweep(P,'leg',(sx*.421,sy*.29,0),(sx*.345,sy*.065,1.04),chamf_rect(.145,.145,.012),[(0,1.16,0),(1,1,0)],WOOD,WOOD_M,WOOD,flat0=True,ground=True)
            box(P,'joint',sx*.39,sy*.205,.165,.20,.325,.445)
            if sy==-1: cap(P,sx*.39,sy*.205-.10,.385)
        box(P,'head',sx*.345,0,.16,.31,.935,1.085)
        cap(P,sx*.345,-.155,1.005)
    # Low stretcher frame intersects all legs.
    for sy in (-1,1):
        sweep(P,'rail',(-.415,sy*.255,.15),(.415,sy*.255,.15),chamf_rect(.080,.070,.008),[(0,1,0),(1,1,0)],WOOD_D,WOOD_D,WOOD_D,ref=(0,0,1))
    for sx in (-1,1):
        sweep(P,'rail',(sx*.410,-.26,.15),(sx*.410,.26,.15),chamf_rect(.080,.070,.008),[(0,1,0),(1,1,0)],WOOD_D,WOOD_D,WOOD_D,ref=(0,0,1))
        sweep(P,'brace',(sx*.34,0,.69),(sx*.145,0,.97),chamf_rect(.085,.075,.009),[(0,1,0),(1,1,0)],WOOD_D,WOOD_D,WOOD_D,ref=(0,1,0))
    box(P,'beam',0,0,.74,.145,.94,1.06,WOOD)
    box(P,'nut',0,0,.18,.18,1.054,1.12,METAL)
    # Left hopper on a substantial dark mounting block.
    box(P,'hopper_block',-.345,0,.205,.18,1.065,1.115,WOOD_D)
    # Tapered closed wall mesh, inner surface turns down to throat.
    def ring(w,z): return [Vector((-.345+x,y,z)) for x,y in [(-w/2,-w/2),(w/2,-w/2),(w/2,w/2),(-w/2,w/2)]]
    P.torus_loft('hopper',[ring(.105,1.115),ring(.255,1.255),ring(.255,1.277),ring(.219,1.277),ring(.219,1.255),ring(.081,1.13)],lambda j,k: METAL_L if j==2 else METAL)
    zprism(P,'fill',-.345,0,[(-.101,-.101),(.101,-.101),(.101,.101),(-.101,.101)],[(1.237,0),(1.247,0)],CREAM_D,CREAM_D,CREAM)
    return P
def build_screw():
    P = Part('Screw')
    # Real helical crest around a solid core: three axial samples per pitch,
    # ten angular facets; flat ends, no detached thread strips.
    n=10
    steps=math.ceil((SP_Z1-SP_Z0)/(PITCH/3))
    rings=[]
    for j in range(steps+1):
        z=SP_Z0+(SP_Z1-SP_Z0)*j/steps
        ring=[]
        for k in range(n):
            a=2*math.pi*k/n+math.pi/12
            phase=(z/PITCH-a/(2*math.pi))%1
            crest=max(0,1-2*abs(phase-.5))
            r=SP_r+(SP_R-SP_r)*crest if 0<j<steps else SP_r
            ring.append(Vector((r*math.cos(a),r*math.sin(a),z)))
        rings.append(ring)
    P.loft('spindle',rings,lambda j,k: METAL_D if ((SP_Z0+(SP_Z1-SP_Z0)*(j+.5)/steps)/PITCH-((k+.5)/n+1/24))%1 < .23 else METAL,METAL,METAL)
    zprism(P,'hub',0,0,ngon(.070,6,math.pi/6),[(HUB_Z0,.008),(HUB_Z0+.008,0),(HUB_Z1-.010,0),(HUB_Z1,.010)],METAL,METAL_D,METAL_L)
    zprism(P,'topcap',0,0,ngon(.045,8,math.pi/8),[(1.387,0),(1.40,0)],METAL,METAL,METAL_L)
    # wooden T-bar: thin near the hub, thicker faceted ends with big end chamfers
    sweep(P, 'bar', (-BAR_HALF, 0, BAR_Z), (BAR_HALF, 0, BAR_Z), ngon(BAR_R, 8, math.pi / 8),
          [(0, 1, 0.009), (0.035, 1, 0), (0.12, 1, 0), (0.17, 0.75, 0), (0.83, 0.75, 0), (0.88, 1, 0), (0.965, 1, 0), (1, 1, 0.009)],
          WOOD, WOOD, WOOD, ref=(0, 0, 1))
    return P

def build_plate():
    P = Part('Plate')
    zprism(P, 'plate', 0, 0, ngon(PLATE_R, PLATE_N, math.pi / PLATE_N),
           [(PLATE_Z0, 0.006), (PLATE_Z0 + 0.006, 0), (PLATE_Z1 - 0.02, 0), (PLATE_Z1, 0.02)], METAL_D, METAL_D, METAL)
    oc = ngon(0.055, 6, math.pi / 6)
    zprism(P, 'collar_base', 0, 0, ngon(0.068, 6, math.pi / 6), [(PLATE_Z1 - 0.01, 0), (PLATE_Z1 + 0.02, 0), (PLATE_Z1 + 0.03, 0.01)],
           METAL, METAL, METAL)
    zprism(P, 'collar', 0, 0, oc, [(PLATE_Z1 + 0.025, 0), (COLLAR_Z1 - 0.016, 0), (COLLAR_Z1, 0.014)], METAL, METAL, METAL_L)
    return P

def build_basket():
    P = Part('Chamber')
    d = 2 * math.pi / STAVES; gap = 0.0025; ch = 0.004; tch = 0.006
    for k in range(STAVES):
        c = -math.pi / 2 + k * d; a, b = c - d / 2, c + d / 2
        ro = BK_AO / math.cos(d / 2); ri = BK_AI / math.cos(d / 2)
        ua, ub = Vector((math.cos(a), math.sin(a))), Vector((math.cos(b), math.sin(b)))
        na, nb = Vector((-ua.y, ua.x)), Vector((-ub.y, ub.x))
        fa = (ub * ro - ua * ro).normalized()
        pts = [ua * ri + na * gap, ua * (ro - ch) + na * gap, ua * ro + fa * (ch + gap),
               ub * ro - fa * (ch + gap), ub * (ro - ch) - nb * gap, ub * ri - nb * gap]
        prof = [(p.x, p.y) for p in pts]
        rings = [[Vector((x, y, z)) for x, y in inset(prof, dd)] for z, dd in ((TT_Z1, 0), (BK_Z1 - tch, 0), (BK_Z1, tch))]
        outer = CREAM if k % 2 == 0 else CREAM_B
        sides = {0: CREAM_D, 1: CREAM_D, 2: outer, 3: CREAM_D, 4: CREAM_D, 5: CREAM_IN}
        P.loft('stave', rings, lambda j, kk: sides[kk] if j == 0 else (CREAM_IN if kk == 5 else CREAM), CREAM_IN, CREAM)
    # Hoops align to the stave faces; eight evenly spaced mirror-symmetric hex rivets.
    for hi, (zc, h) in enumerate(HOOPS):
        aoi, aoo = BK_AO - 0.004, BK_AO + HOOP_T
        def hring(apo, z):
            r = apo / math.cos(d / 2)
            return [Vector((r * math.cos(-math.pi / 2 + (k + 0.5) * d), r * math.sin(-math.pi / 2 + (k + 0.5) * d), z)) for k in range(STAVES)]
        P.torus_loft('hoop', [hring(aoi, zc - h / 2), hring(aoo, zc - h / 2), hring(aoo, zc + h / 2), hring(aoi, zc + h / 2)], METAL)
        for k in sorted({round(j*STAVES/8) % STAVES for j in range(8)}):
            if hi == 1 and k == 0: continue                    # front rivet of the lower hoop sits under the spout flange
            c = -math.pi / 2 + k * d; u = Vector((math.cos(c), math.sin(c), 0))
            p0 = Vector((0, 0, zc)) + u * (aoo - 0.003); p1 = Vector((0, 0, zc)) + u * (aoo + 0.016)
            sweep(P, 'rivet', p0, p1, ngon(0.019, 6, math.pi / 2), [(0, 1, 0), (1, 0.72, 0)], METAL, METAL, METAL_L, ref=(0, 0, 1))
    # Three solid walls form an open U-channel (no top, visibly open along its length).
    a=Vector((0,-.237,.490)); b=Vector((0,-.451,.383))
    # A concave U cross section is watertight as a solid extrusion.
    prof=[(-.050,-.028),(.050,-.028),(.050,.030),(.037,.030),(.037,-.014),(-.037,-.014),(-.037,.030),(-.050,.030)]
    sweep(P,'spout',a,b,prof,[(0,1,0),(1,1,0)],METAL,METAL_D,METAL_L,ref=(1,0,0))
    return P

def build():
    coll=pc.clear_collection(NAME)
    bpy.context.window.scene=bpy.data.scenes[NAME+'_Build']
    img=pc.atlas_image(TEX_NAME,os.path.join(ART,'Textures',TEX_NAME),PAL); mat=pc.material(MAT_NAME,img)
    root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
    obs={}
    for P,piv,skip in ((build_frame(),(0,0,0),('hopper','hopper_block','fill')),(build_screw(),(0,0,SCREW_PIVOT_Z),('spindle',)),(build_plate(),(0,0,(PLATE_Z0+PLATE_Z1)/2),()),(build_basket(),(0,0,TT_Z1),())):
        obs[P.name]=pc.to_object(P,NAME,coll,mat,piv,root,mirror_skip=skip)
    bpy.context.view_layer.update()
    total=pc.report(obs)
    assert 1800 <= total <= 3500, total
    print('CONTACTS platform top = chamber base',TT_Z1,'plate radius',PLATE_R,'< inner apothem',BK_AI,'plate top',PLATE_Z1,'< rim',BK_Z1)
    print('CONTACTS screw bottom',SP_Z0,'<= collar top',COLLAR_Z1,'nut rests on beam 1.06; hopper rests on block 1.115; feet z=0; SNAP n/a freestanding')
    fbx=pc.export(NAME,coll,root,os.path.join(ART,'Meshes',NAME+'.fbx')); pc.verify(fbx)
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)
    return obs
# Convert the shared diagnostic to a hard acceptance gate locally, without editing common code.
_check=pc.comp_checks
def checked(P,mirror_skip=()):
    result=_check(P,mirror_skip)
    assert result['nonmanifold']==result['loose']==result['degenerate']==0,result
    assert result['mirror']<1e-5 and not result['problems'],result
    return result
pc.comp_checks=checked
OBS=build()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT=args[0] if args else os.path.join(ART,'Previews',NAME+'_Preview.png')
PCT=50 if len(args)>1 and args[1]=='check' else 100
exec(compile(open(os.path.join(os.path.dirname(__file__),'render_preview.py'),encoding='utf8').read(),'render_preview.py','exec'))
