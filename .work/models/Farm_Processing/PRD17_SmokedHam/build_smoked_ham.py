import bpy, bmesh, math, os, sys
from mathutils import Vector
ROOT = r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
HERE=os.path.join(ROOT,'.work/models/Farm_Processing/PRD17_SmokedHam')
sys.path.insert(0,os.path.join(ROOT,'.work/models/Farm_Processing/_common'))
import processing_common as pc
ART=os.path.join(ROOT,'art/Farm_Processing'); NAME='FMS_Workshop_PRD_17'
CHECK=os.path.join(os.environ['TEMP'],'FarmProcessing_check/PRD17'); os.makedirs(CHECK,exist_ok=True)
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROUND=int(ARGS[0]) if ARGS else 1
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#EFD7A8','#EAD6AE','#D2BA8A','#D08A55','#A9683A','#BD7847']

def tube_path(P,name,pts,up,closed=True):
    up=Vector(up); rings=[]
    for i,c in enumerate(pts):
        a=(c-pts[i-1]).normalized() if i>0 or closed else None
        b=(pts[(i+1)%len(pts)]-c).normalized() if i<len(pts)-1 or closed else None
        t=(a+b).normalized() if a and b else (a or b)
        fac=1/t.dot(a) if a and b else 1
        sd=t.cross(up).normalized(); uu=sd.cross(t).normalized()
        rings.append([c+sd*(.006*math.cos(k*math.tau/6)*fac)+uu*(.006*math.sin(k*math.tau/6)) for k in range(6)])
    P.torus_loft(name,rings,lambda j,k:12 if k in (3,4) else 11)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene; sc.name=NAME+'_Build'; sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME); sc.collection.children.link(coll)
P=pc.Part('Body'); bm=P.bm
# z, centre x, x radius, y radius
profile=[(0,-.018,.034,.036),(.025,-.022,.072,.064),(.075,-.015,.1,.08),(.13,-.005,.096,.077),(.18,.008,.073,.060),(.215,.027,.044,.037),(.245,.042,.023,.023),(.272,.047,.0225,.0225),(.291,.060,.029,.026),(.306,.067,.022,.021),(.313,.067,.012,.012)]
rings=[[Vector((cx+rx*math.cos(k*math.tau/12), ry*math.sin(k*math.tau/12)*(1.18 if math.sin(k*math.tau/12)>0 else 1),z)) for k in range(12)] for z,cx,rx,ry in profile]
P.loft('skin',rings,lambda j,k: 14 if k in (1,2,3) else (15 if k in (0,5,6,11) else 13),14,13)
# Trim lower front left with a plane, leaving a real open boundary.
n=Vector((-.35,-1,-.12)).normalized(); plane=Vector((-.018,-.032,.083))
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=plane,plane_no=n,clear_outer=True,clear_inner=False)
bound=[e for e in bm.edges if e.is_boundary]
assert bound
v=bound[0].verts[0]; outer=[v]; prev=None
while True:
    es=[e for e in v.link_edges if e.is_boundary and e is not prev]; e=es[0]; nxt=e.other_vert(v)
    if nxt==outer[0]: break
    outer.append(nxt); prev=e; v=nxt
# planar inset in its own orthonormal basis, true 12mm width
c=sum((v.co for v in outer),Vector())/len(outer); u=Vector((1,0,0)); u=(u-n*u.dot(n)).normalized(); w=n.cross(u)
xy=[((v.co-c).dot(u),(v.co-c).dot(w)) for v in outer]
area=sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
if area<0: outer.reverse(); xy.reverse()
innerxy=pc.inset(xy,.012)
inner=[bm.verts.new(c+u*x+w*y+n*.0015) for x,y in innerxy]
for i in range(len(outer)):
    j=(i+1)%len(outer); P.face([outer[i],outer[j],inner[j],inner[i]],10)
f=P.face(inner,5)
r=bmesh.ops.triangulate(bm,faces=[f],ngon_method='BEAUTY')
for f in r['faces']:
    cen=f.calc_center_median(); f[P.slot]=6 if (cen.z<.040 or (cen.x<-.030 and cen.z>.085) or (cen.x>.015 and cen.z<.090)) else 5
# The body including cut is a single connected manifold component.
P.comp=[('ham_with_integrated_cut',list(bm.faces),True)]
for z in (.256,.268):
    pts=[Vector((.044+.026*math.cos(k*math.tau/8),.026*math.sin(k*math.tau/8),z-.12*.026*math.cos(k*math.tau/8))) for k in range(8)]
    tube_path(P,'wrap_'+str(z),pts,(0,0,1))
pts=[Vector((x,-.012,z)) for x,z in [(.039,.269),(.020,.328),(.015,.365),(.022,.387),(.034,.396),(.047,.393),(.058,.378),(.060,.361),(.052,.326),(.042,.280)]]
tube_path(P,'hanging_loop',pts,(0,1,0))
# Normalize bottom after the planar trim removes the lowest front edge.
low=min(v.co.z for v in bm.verts)
for v in bm.verts: v.co.z-=low
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
res=pc.comp_checks(P,mirror_skip=[v[0] for v in P.comp]); assert res['nonmanifold']==res['loose']==res['degenerate']==0
assert not res['problems'],res
for name,fs,g in P.comp: print('COMPONENT',name,'tris',sum(len(f.verts)-2 for f in fs))
height=max(v.co.z for v in bm.verts); pivot=max(bm.verts,key=lambda v:v.co.z).co.copy()
root=bpy.data.objects.new(NAME,None); coll.objects.link(root); root.location=pivot
for sub in ('Meshes','Textures','Previews','Blend'):os.makedirs(os.path.join(ART,sub),exist_ok=True)
tex=os.path.join(ART,'Textures/T_FarmProcessing_PRD17_BaseColor.png')
img=pc.atlas_image('T_FarmProcessing_PRD17_BaseColor',tex,PAL); mat=pc.material('M_FarmProcessing_PRD17',img)
ob=pc.to_object(P,NAME,coll,mat,pivot,root,mirror_skip=[v[0] for v in P.comp]); ob.location=(0,0,0)
bpy.context.view_layer.update(); total=pc.report({'Body':ob}); assert 250<=total<=600
pts=[ob.matrix_world@v.co for v in ob.data.vertices]; assert abs(min(v.z for v in pts))<1e-6
print('HANG POINT',list(pivot),'MIRROR asymmetric by reference; CONTACTS OK; SNAP n/a')
# Save library only asset objects; preview utility restores temporary setup.
if ROUND==3:
    fbx=os.path.join(ART,'Meshes',NAME+'.fbx'); pc.export(NAME,coll,root,fbx); pc.verify(fbx)
    pc.save_lib(os.path.join(ART,'Blend',NAME+'.blend'),coll,mat,img)

def render(out,pct,view=None):
    cfg={'OUT':out,'PCT':pct,'VIEW_DIR':view or (-.36,-1,.36)}
    exec(compile(open(os.path.join(HERE,'render_preview.py')).read(),'render_preview.py','exec'),cfg)
render(os.path.join(CHECK,'round'+str(ROUND)+'.png'),40)
if ROUND==3:
    for nm,view in [('back',(0,1,.3)),('side',(1,0,.2)),('other',(-1,0,.2))]:render(os.path.join(CHECK,nm+'.png'),40,view)
    render(os.path.join(ART,'Previews',NAME+'_Preview.png'),100)




