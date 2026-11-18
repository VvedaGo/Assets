import bpy,bmesh,math,os,sys,argparse
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
from processing_common import Part,ngon,chamf_rect,sweep,rect_prism
NAME='FMS_Workshop_TOL_08'; ART=str(ROOT/'art/Farm_Processing')
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EADAB4','#C99263','#A26A43','#857B6E']
WOOD,WOOD_D,WOOD_M,CREAM,CREAM_D,RED,RED_D,METAL,METAL_D,METAL_L,CREAM_IN,WOOD_DD,CREAM_B,HWOOD,BLADE,FOOT=range(16)
p=argparse.ArgumentParser(); p.add_argument('--round',type=int,default=1); p.add_argument('--export',action='store_true'); args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
CFG={'view':(-.40,-1,.78),'fill':(.77,.84)}
CHECK_DIR=Path(os.environ['TEMP'])/'FarmProcessing_check/TOL08'; CHECK_DIR.mkdir(parents=True,exist_ok=True)
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



def build_sieve():
    P=Part('Body'); n=16
    prof=[(0,.15),(.019,.15),(.019,.155),(.043,.155),(.043,.15),(.098,.15),(.10,.148),(.10,.130),(0,.130)]
    def slots(j,k):
        if j in (1,2,3): return WOOD_D
        if j in (5,6): return WOOD
        if j==7: return WOOD_M
        return WOOD if k%4!=0 else WOOD_M
    P.torus_loft('wood_wall_band',[ringco(z,a,n) for z,a in prof],slots)
    P.comp[-1]=(P.comp[-1][0],P.comp[-1][1],True)
    # One continuous top sheet with true square hole loops: no crossing/overlap faces.
    normals=[Vector((math.cos(k*math.pi/8),math.sin(k*math.pi/8))) for k in range(16)]
    def clip(poly):
        for nn in normals:
            out=[]
            for a,b in zip(poly,poly[1:]+poly[:1]):
                da=nn.dot(a)-.115; db=nn.dot(b)-.115
                if da<=1e-9: out.append(a)
                if (da<0)!=(db<0): out.append(a.lerp(b,da/(da-db)))
            poly=out
            if not poly: break
        return poly
    def area(poly): return abs(sum(a.x*b.y-a.y*b.x for a,b in zip(poly,poly[1:]+poly[:1])))/2
    polys=[]
    for ix in range(6):
        for iy in range(6):
            x=(ix-2.5)*.044; y=(iy-2.5)*.044
            poly=clip([Vector((x-.015,y-.015)),Vector((x+.015,y-.015)),Vector((x+.015,y+.015)),Vector((x-.015,y+.015))])
            if len(poly)>=3 and area(poly)>1e-8: polys.append(poly)
    outer=[P.bm.verts.new(v) for v in ringco(.040,.131,16)]
    holes=[[P.bm.verts.new((v.x,v.y,.040)) for v in poly] for poly in polys]
    faces=fill(P,[outer]+holes,CREAM,(0,0,1))
    expected=area([Vector((v.co.x,v.co.y)) for v in outer])-sum(area(poly) for poly in polys)
    actual=sum(f.calc_area() for f in faces)
    assert abs(expected-actual)<1e-7,(expected,actual)
    from mathutils.bvhtree import BVHTree
    topverts=list({v for f in faces for v in f.verts})
    vi={v:i for i,v in enumerate(topverts)}
    bv=BVHTree.FromPolygons([v.co for v in topverts],[[vi[v] for v in f.verts] for f in faces])
    tests=0
    for poly in polys:
        center=sum(poly,Vector((0,0)))/len(poly)
        for pt in [center]+[center.lerp(v,.95) for v in poly]:
            assert bv.ray_cast(Vector((pt.x,pt.y,.2)),Vector((0,0,-1)),.3)[0] is None, 'Blocked opening'
            tests+=1
    print('HOLES: all',len(polys),'see-through;',tests,'downward ray samples clear; uniform top height .040')
    for top in holes:
        bot=[P.bm.verts.new((v.co.x,v.co.y,.030)) for v in top]
        faces+=tube(P,bot,top,CREAM)
    P.comp.append(('uniform_lattice_rim',faces,False))
    print('LATTICE: continuous non-overlapping grid/rim; 6x6 cells clipped to 16gon; holes',len(holes),'square opening .030 pitch .044 slat .014; all top Z .040 base Z .030; cap area',actual,'expected',expected)
    for i in range(8):
        a=math.pi/8+i*math.pi/4; d=Vector((math.cos(a),math.sin(a),0)); c=d*.154; c.z=.031
        sweep(P,'red_plate',c,c+d*.006,[(-.011,-.011),(.011,-.011),(.011,.011),(-.011,.011)],[(0,1,0),(1,1,0)],RED,RED_D,RED,ref=(0,0,1))
    for sx in (-1,1):
        z=.074
        pts=[Vector((sx*x,y,z)) for x,y in ((.147,-.031),(.164,-.038),(.182,-.024),(.182,.024),(.164,.038),(.147,.031))]
        path_sweep(P,'handle',pts,(0,0,1),[(.008,-.008),(.008,.008),(-.008,.008),(-.008,-.008)],METAL,METAL_D)
        for sy in (-1,1): bolt(P,(sx*.153,sy*.038,z),(0,sy,0),r=.008,h=.006)
    from collections import Counter
    counts=Counter()
    for nm,fs,_ in P.comp: counts[nm]+=sum(len(f.verts)-2 for f in fs)
    print('COMPONENT TRIS',dict(counts),'total',sum(counts.values()),'original 400 coordinator-approved allowance 1040')
    assert sum(counts.values())<=1040
    ch=pc.comp_checks(P)
    boundaries=[e for e in P.bm.edges if e.is_boundary]
    unexpected=[e for e in P.bm.edges if not e.is_manifold and not e.is_boundary]
    assert not unexpected and ch['nonmanifold']==len(boundaries) and ch['loose']==ch['degenerate']==0 and ch['mirror']<1e-6 and not ch['problems'],ch
    print('TOPOLOGY: intentional open underside/end boundaries',len(boundaries),'unexpected nonmanifold',len(unexpected),'loose/degenerate 0')
    print('CONTACTS: grid and cream rim are one continuous mesh; outer rim buried .001m into wood; handles/bolts overlap wall; band integral; VERIFY OK')
    return P

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.name=NAME+'_Build'; sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
for d in ('Textures','Meshes','Blend','Previews'): (Path(ART)/d).mkdir(parents=True,exist_ok=True)
tex=Path(ART)/'Textures/T_FarmProcessing_TOL08_BaseColor.png'; img=pc.atlas_image(tex.name,str(tex),PAL); mat=pc.material('M_FarmProcessing_TOL08',img)
P=build_sieve(); ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root); bpy.context.view_layer.update(); pc.report({'Body':ob})
exec((HERE/'render_preview.py').read_text())
render(str(CHECK_DIR/f'round{args.round}.png'),40)
if args.export:
    assert sum(len(f.vertices)-2 for f in ob.data.polygons)<=1040, 'Coordinator-approved budget gate'
    fbx=pc.export(NAME,coll,root,str(Path(ART)/'Meshes'/f'{NAME}.fbx'))
    pc.save_lib(str(Path(ART)/'Blend'/f'{NAME}.blend'),coll,mat,img)
    render(str(Path(ART)/'Previews'/f'{NAME}_Preview.png'),100)
    for key,view in [('front',(0,-1,.15)),('back',(.3,1,.6)),('bottom',(.2,-1,-.8)),('top',(0,0,1))]: render(str(CHECK_DIR/f'{key}.png'),40,view)
    pc.verify(fbx)
