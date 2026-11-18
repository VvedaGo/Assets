import bpy,bmesh,math,os,sys,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
sys.path.insert(0,str(HERE))
from render_preview import render
NAME='FMS_Workshop_PRD_04'; ART=ROOT/'art/Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD04'
CHECK.mkdir(parents=True,exist_ok=True)
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'round1'
for ob in list(bpy.context.scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
sc=bpy.context.scene; sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None); coll.objects.link(root)
pal=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#D9C08F','#5A3C26','#EAD6AE','#F4F1E8','#E6E1D3','#C5AA7E']
tex='T_FarmProcessing_PRD04_BaseColor.png'
img=pc.atlas_image(tex,str(ART/'Textures'/tex),pal)
mat=pc.material('M_FarmProcessing_PRD04',img)
P=pc.Part('Body')
# Adapted shell() loft: outer bottom -> belly -> shoulder -> neck -> upper neck -> ruffle -> inside ruffle -> fill floor.
# Twelve belly facets; 24 rim vertices give eight soft paired-vertex crests.
prof=[(0,.088),(.055,.120),(.078,.108),(.104,.082),(.123,.082),(.148,.104),(.176,.1195),(.178,.1115),(.148,.090)]
counts=[12,12,12,12,12,12,24,24,12]
ruffle_hi=[.004,.003,.0045,.0035,.0042,.0032,.0044,.0038]
ruffle_lo=[-.0035,-.0045,-.003,-.004,-.0034,-.0043,-.0032,-.004]
rings=[]
for j,(z,r) in enumerate(prof):
    count=counts[j]; ring=[]
    for k in range(count):
        a=2*math.pi*k/count
        fold=(.005 if k%2==0 else -.001) if j in (1,2) else 0
        dz=0
        if j in (6,7):
            # Two adjacent crest vertices form a broad top; the third is the soft trough.
            group=k//3; pos=k%3
            fold=(.0045 if pos<2 else -.002)*(1+.10*math.sin(group*1.7))
            dz=ruffle_hi[group]-(.0004 if pos==1 else 0) if pos<2 else ruffle_lo[group]
        elif j==5:
            fold=.0025*math.sin(a*4+.3)
            dz=.001*math.cos(a*4)
        ring.append((math.cos(a)*(r+fold),math.sin(a)*(r+fold),z+dz))
    rings.append(ring)
# shell() topology with unequal ring counts, triangulated zipper at transitions.
R=[[P.bm.verts.new(v) for v in ring] for ring in rings]; faces=[]
for j,(A,B) in enumerate(zip(R,R[1:])):
    na,nb=len(A),len(B); i=k=0
    while i<na or k<nb:
        u=(i+1)/na if i<na else 2; v=(k+1)/nb if k<nb else 2
        slot=10 if j==7 or (j in (1,2,4,5) and (i+k)%3==0) else 12
        if abs(u-v)<1e-8:
            vs=[A[i%na],A[(i+1)%na],B[(k+1)%nb],B[k%nb]];i+=1;k+=1
        elif u<v:
            vs=[A[i%na],A[(i+1)%na],B[k%nb]];i+=1
        else:
            vs=[A[i%na],B[(k+1)%nb],B[k%nb]];k+=1
        faces.append(P.face(vs,slot))
faces.append(P.face(list(reversed(R[0])),10));faces.append(P.face(R[-1],14))
P.comp.append(('cloth_shell_fill',faces,True))
n=12
# geometry BVH used to drape tails on the exact faceted outer wall.
vs=[Vector(p) for r in rings[:5] for p in r]
fs=[]
for j in range(4):
    for k in range(n): fs.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
bvh=BVHTree.FromPolygons(vs,fs)
def surface(a,z):
    d=Vector((math.cos(a),math.sin(a),0))
    hit=bvh.ray_cast(Vector((0,0,z)),d)
    assert hit[0] is not None,(a,z)
    return hit[0],d
# Closed band section, follows waist and overlaps cloth by 1mm on hidden side.
def radius(z):
    for (z0,r0),(z1,r1) in zip(prof[:4],prof[1:5]):
        if z0<=z<=z1:return r0+(r1-r0)*(z-z0)/(z1-z0)
    return .082
band=[]
for z,off in [(.098,-.001),(.098,.006),(.123,.006),(.123,-.001)]:
    r=radius(z)+off
    band.append([(r*math.cos(2*math.pi*k/10),r*math.sin(2*math.pi*k/10),z) for k in range(10)])
P.torus_loft('red_tie_band',band,lambda j,k:6 if j==0 else 5)
# Two seven-vertex V-notched solid ribbons, width in arc length 25mm.
for ii,ac in enumerate((-1.38,-.85)):
    # bottom edges splay away from knot; upper tips converge under knot
    outline=[(-.011,.108),(.011,.108),(.012,.098),(.015,.078),(.018,.055),(.019,.040),(.007,.046),(-.006,.040),(-.009,.055),(-.010,.078),(-.011,.098)]
    layers=[]
    for offset in (-.0003,.0032):
        layer=[]
        for u,z in outline:
            a=(-1.20+u/radius(z)*.55) if z==.108 else ac+u/radius(z)
            p,d=surface(a,z)
            # above belly contact tails emerge from outer surface of the band
            dr=max(0,(z-.095)/.013)*.007
            layer.append(p+d*(offset+dr))
        layers.append(layer)
    # Explicit cross-ribbon panels prevent a single cap triangulation spanning the belly crest.
    L=[[P.bm.verts.new(v) for v in layer] for layer in layers]; faces=[]
    panels=((0,1,2,10),(10,2,3,9),(9,3,4,8),(8,4,5,6,7))
    for panel in panels:
        faces.append(P.face([L[0][i] for i in reversed(panel)],6))
        faces.append(P.face([L[1][i] for i in panel],5))
    for k in range(11):faces.append(P.face([L[0][k],L[0][(k+1)%11],L[1][(k+1)%11],L[1][k]],5))
    P.comp.append(('ribbon_tail_'+str(ii),faces,False))
# Knot a solid chunky small block local radial/tangent basis, underside in tie.
a=-1.20; d=Vector((math.cos(a),math.sin(a),0)); t=Vector((-math.sin(a),math.cos(a),0))
kr=[]
for z in (.097,.127):
    kr.append([d*r+t*u+Vector((0,0,z)) for r,u in ((.083,-.014),(.097,-.014),(.097,.014),(.083,.014))])
P.loft('knot',kr,5,6,5)
# Lead-requested domed polyhedra: equator6 + rotated upper6 + top/bottom vertices,24tris.
centres=[(0,0,.030),(-.047,-.011,.028),(.045,-.016,.028),(-.023,-.053,.027),(.025,-.054,.026),(-.040,.040,.028),(.012,.046,.029),(.059,.033,.025),(-.067,.023,.024)]
for i,(x,y,r) in enumerate(centres):
    phase=i*.73
    h=2*r*(.63+.025*math.sin(i))
    centre_z=.146+.009*max(0,1-math.hypot(x,y)/.075)
    eq=[P.bm.verts.new((x+r*math.cos(phase+k*math.pi/3),y+r*math.sin(phase+k*math.pi/3),centre_z)) for k in range(6)]
    upper=[P.bm.verts.new((x+r*.66*math.cos(phase+math.pi/6+k*math.pi/3),y+r*.66*math.sin(phase+math.pi/6+k*math.pi/3),centre_z+h*.31)) for k in range(6)]
    top=P.bm.verts.new((x,y,centre_z+h*.5)); bottom=P.bm.verts.new((x,y,centre_z-h*.5))
    faces=[]
    for k in range(6):
        k1=(k+1)%6
        faces.append(P.face([bottom,eq[k1],eq[k]],14))
        faces.append(P.face([eq[k],eq[k1],upper[k]],13 if k%3 else 14))
        faces.append(P.face([eq[k1],upper[k1],upper[k]],13))
        faces.append(P.face([upper[k],upper[k1],top],13))
    P.comp.append(('curd_'+str(i),faces,False))
# Preserve exact ground-centred catalogue footprint after changing facet count.
for axis in (0,1):
    lo=min(v.co[axis] for v in P.bm.verts);hi=max(v.co[axis] for v in P.bm.verts)
    for vert in P.bm.verts:vert.co[axis]=(vert.co[axis]-(lo+hi)/2)*(.250/(hi-lo))
bmesh.ops.recalc_face_normals(P.bm,faces=P.bm.faces)
checks=pc.comp_checks(P,mirror_skip=[c[0] for c in P.comp if c[0]!='red_tie_band'])
assert checks['nonmanifold']==checks['loose']==checks['degenerate']==0
# Component contact overlap test reports exact mesh intersection or distance.
assert not checks['problems'],checks
components={nm:sum(len(f.verts)-2 for f in faces) for nm,faces,_ in P.comp}
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=[c[0] for c in P.comp if c[0]!='red_tie_band'])
bpy.context.view_layer.update()
total=pc.report({'Body':ob})
print('COMPONENT_TRIS',components,'budget250..650 lead revision',total)
# body dimensions and ground pivot must match catalogue.
assert abs(ob.dimensions.x-.25)<.001 and abs(ob.dimensions.y-.25)<.001
assert abs(min(v.co.z for v in ob.data.vertices))<1e-8
print('CONTACTS OK; draped tails offset -0.3..3.2 mm, curds straddle fill z=.148; waist X-mirror exact; ruffles/knot/curds intentionally asymmetric; SNAP/verify N/A standalone prop')
if MODE=='export':
    assert total<=650,total
    fbx=pc.export(NAME,coll,root,str(ART/'Meshes'/(NAME+'.fbx')))
    pc.save_lib(str(ART/'Blend'/(NAME+'.blend')),coll,mat,img)
    render(str(ART/'Previews'/(NAME+'_Preview.png')),100)
    pc.verify(fbx)
else:
    render(str(CHECK/(MODE+'.png')),40)
    if MODE=='round3':
        for key,view in [('back',(0,1,.5)),('side',(1,0,.4)),('top',(0,-.01,1))]:render(str(CHECK/(key+'.png')),40,view)


