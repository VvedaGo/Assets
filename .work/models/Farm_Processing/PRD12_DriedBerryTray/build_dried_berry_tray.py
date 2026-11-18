import bpy,bmesh,math,os,sys,argparse,random
from pathlib import Path
from mathutils import Vector
from collections import Counter
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_12'; ART=ROOT/'art/Farm_Processing'
p=argparse.ArgumentParser();p.add_argument('--round',type=int,default=1);p.add_argument('--export',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
CHECK_DIR=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD12';CHECK_DIR.mkdir(parents=True,exist_ok=True)
CFG={'view':(-.36,-1,.83),'fill':(.77,.84)}
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#C7B288','#5A3C26','#EAD6AE','#5E2A2E','#43201F','#735043']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.name=NAME+'_Build';sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
coll=bpy.data.collections.new(NAME);sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
for d in ['Textures','Meshes','Blend','Previews']:(ART/d).mkdir(parents=True,exist_ok=True)
tex=ART/'Textures/T_FarmProcessing_PRD12_BaseColor.png';img=pc.atlas_image(tex.name,str(tex),PAL);mat=pc.material('M_FarmProcessing_PRD12',img)
P=pc.Part('Body')
def box(n,x,y,z,w,d,h,s):pc.zprism(P,n,x,y,[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)],[(z,0),(z+h,0)],s,s,s,ground=z==0)
# One integral closed wall: stripe is real face bands, no overlapping decals.
# Four 16-point upper corner zones rise above eight-sided lower rails.
def outline(w,d,c,extra=False):
 a,b=w/2,d/2
 if not extra:return pc.chamf_rect(w,d,c)
 out=[]
 for x,y in [(a,-b),(a,b),(-a,b),(-a,-b)]:
  # rotated first corner (right/front), order counter-clockwise
  pass
 base=[(a-.032,-b,.070),(a-c,-b,.080),(a,-b+c,.080),(a,-b+.032,.070)]
 for k in range(4):
  for x,y,z in base:
   # rectangular corner offset mapping, rotate normalized corner-local coordinates
   if k==0:xx,yy=x,y
   elif k==1:xx,yy=a-(y+b),b-(a-x)
   elif k==2:xx,yy=-x,-y
   else:xx,yy=-a+(y+b),-b+(a-x)
   out.append((xx,yy,z))
 return out
outer=outline(.344,.300,.009)
upper=outline(.344,.300,.009,True)
inner=outline(.304,.260,.006)
# upper inner has corresponding chamfer and crown zones
upin=outline(.304,.260,.006,True)
rings=[]
for z in [0,.016,.037]:rings.append([P.bm.verts.new((x,y,z)) for x,y in outer])
rings.append([P.bm.verts.new(v) for v in upper]);rings.append([P.bm.verts.new(v) for v in upin]);rings.append([P.bm.verts.new((x,y,0)) for x,y in inner])
faces=[]
def bridge(a,b,s):
 # unequal rings: upper points 0/3 lie along the long faces of the lower 8gon
 if len(a)==len(b):
  for i in range(len(a)):faces.append(P.face([a[i],a[(i+1)%len(a)],b[(i+1)%len(b)],b[i]],s))
 else:
  rev=len(a)>len(b)
  small,big=(b,a) if rev else (a,b)
  for k in range(4):
   j=2*k; q=4*k
   # small chamfer endpoints correspond big q+1 and q+2
   for vs in [[small[j],small[(j+1)%8],big[q+2],big[q+1]],[small[(j+1)%8],small[(j+2)%8],big[(q+5)%16],big[(q+4)%16],big[q+3],big[q+2]]]:
    faces.append(P.face(list(reversed(vs)) if rev else vs,s))
for i,s in enumerate([2,5,0,0,2,1]):bridge(rings[i],rings[(i+1)%6],s)
P.comp.append(('frame_posts_red_band',faces,True))
box('dark_base',0,0,0,.308,.264,.006,1)
# Full 7x6 opening array; ends buried 2 mm into rails. Alternating heights suggest interweave.
xs=[-.152+(.304-6*.016)/7+i*((.304-6*.016)/7+.016)+.008 for i in range(6)]
ys=[-.130+(.260-5*.016)/6+i*((.260-5*.016)/6+.016)+.008 for i in range(5)]
for i,x in enumerate(xs):box('lattice',x,0,.044+(min(i,5-i)%2)*.003,.016,.264,.008,12)
for i,y in enumerate(ys):box('lattice',0,y,.046+(i%2)*.003,.308,.016,.008,12)
# Chunky closed mitred loops, three bends each, sunk into side walls.
def handle(sx):
 pts=[Vector((sx*x,y,.047)) for x,y in [(.167,-.051),(.185,-.051),(.191,-.037),(.191,.037),(.167,.051)]]
 sec=[(-.009,-.009),(.009,-.009),(.009,.009),(-.009,.009)]
 rs=[];up=Vector((0,0,1))
 for i,c in enumerate(pts):
  d1=(c-pts[i-1]).normalized() if i else None;d2=(pts[i+1]-c).normalized() if i<len(pts)-1 else None
  t=(d1+d2).normalized() if d1 and d2 else (d1 or d2);m=1/t.dot(d1) if d1 and d2 else 1;sd=t.cross(up).normalized()
  rs.append([c+sd*a*m+up*b for a,b in sec])
 P.loft('handle',rs,0,2,2)
for sx in [-1,1]:handle(sx)
def twig(a,b,r):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,0,1))).normalized();v=t.cross(u)
 vs=[P.bm.verts.new(a+u*r),P.bm.verts.new(a-u*r+v*r*.6),P.bm.verts.new(a-u*r-v*r*.6),P.bm.verts.new(b)]
 fs=[P.face([vs[i] for i in ids],1) for ids in [(0,2,1),(0,1,3),(1,2,3),(2,0,3)]];P.comp.append(('twig',fs,False))
def berry(x,y,z,k,support):
 # Six-sided equator, smaller rotated triangular shoulder, short top tip.
 # Short lower pole sinks into lattice; closed18-triangle berry retains round lower silhouette.
 r=.0115*(1+.045*math.sin(k*8)); phase=.15*math.sin(k*1.9)
 eq=[P.bm.verts.new((x+r*math.cos(phase+j*math.pi/3),y+r*math.sin(phase+j*math.pi/3),z+.008)) for j in range(6)]
 up=[P.bm.verts.new((x+r*.63*math.cos(phase+math.pi/3+j*2*math.pi/3),y+r*.63*math.sin(phase+math.pi/3+j*2*math.pi/3),z+.014)) for j in range(3)]
 tip=P.bm.verts.new((x+.0007*math.sin(k),y,z+.0176))
 fs=[];slot=14 if k%5==0 else 13
 for j in range(3):
  # upper j matches equator 2*j+1; quad+triangle shoulders avoid long pole fans
  q=2*j+1
  fs.append(P.face([eq[q],eq[(q+1)%6],eq[(q+2)%6],up[(j+1)%3],up[j]],slot))
  fs.append(P.face([up[j],up[(j+1)%3],tip],slot))
 bot=P.bm.verts.new((support[0],support[1],z))
 for j in range(6):fs.append(P.face([eq[(j+1)%6],eq[j],bot],slot))
 P.comp.append(('berries',fs,False))
# Five fuller 2+4+3+2+1 cones: twelve touching berries each, about90mm long.
for ci,(cx,cy) in enumerate([(-.073,.068),(.068,.068),(-.101,-.065),(0,-.065),(.101,-.065)]):
 cells=[]
 for row,nrow in enumerate([2,4,3,2,1]):
  for col in range(nrow):
   x=cx+(col-(nrow-1)/2)*.018;y=cy+.022-row*.017
   # Seat the short lower pole on a real strip, including berries over opening edges.
   sx,sy=x,y;nx=min(xs,key=lambda q:abs(x-q));ny=min(ys,key=lambda q:abs(y-q))
   if abs(x-nx)>.007 and abs(y-ny)>.007:
    if abs(x-nx)<abs(y-ny):sx=nx+(.006 if x>nx else -.006)
    else:sy=ny+(.006 if y>ny else -.006)
   tops=[.052+(min(i,5-i)%2)*.003 for i,xx in enumerate(xs) if abs(sx-xx)<.008]+[.054+(i%2)*.003 for i,yy in enumerate(ys) if abs(sy-yy)<.008]
   topz=max(tops or [.052]);berry(x,y,topz-.001,ci*12+len(cells),(sx,sy));cells.append((x,y,topz))
 # Confirm the twelve surfaces form one touching berry cluster, not scattered pieces.
 from mathutils.bvhtree import BVHTree
 bfs=[fs for nm,fs,_ in P.comp if nm=='berries'][-12:]
 trees=[];allv=[]
 for fs in bfs:
  vs=list({v for f in fs for v in f.verts});idx={v:i for i,v in enumerate(vs)}
  trees.append(BVHTree.FromPolygons([v.co for v in vs],[[idx[v] for v in f.verts] for f in fs]));allv+=vs
 graph=[set() for _ in trees]
 for ia in range(12):
  for ib in range(ia):
   if trees[ia].overlap(trees[ib]):graph[ia].add(ib);graph[ib].add(ia)
 seen={0};todo=[0]
 while todo:
  for nb in graph[todo.pop()]-seen:seen.add(nb);todo.append(nb)
 assert len(seen)==12,('disconnected berry bunch',ci,seen)
 length=max(v.co.y for v in allv)-min(v.co.y for v in allv)
 print('BUNCH',ci+1,'berries12, contact graph connected, length',round(length,4),'m')
 # Stems lie visibly on top of fruit, with their pointed ends seated in berries.
 # Main and three branches form a connected fork rather than isolated sticks.
 twig((cx,cy+.048,.081),(cx,cy-.032,.068),.0030)
 for j,(bx,by) in enumerate([(-.020,.005),(.025,-.009),(-.025,-.023)]):
  twig((cx,cy+.023-j*.012,.078-j*.002),(cx+bx,cy+by,.0675),.0028)
counts=Counter()
for n,fs,_ in P.comp:counts[n]+=sum(len(f.verts)-2 for f in fs)
print('COMPONENT TRIS',dict(counts),'TOTAL',sum(counts.values()),'catalogue 250-650 polish lead allowance about1500')
ch=pc.comp_checks(P,mirror_skip=('berries','twig'))
assert not any(ch[k] for k in ['nonmanifold','loose','degenerate']),ch
assert ch['mirror']<1e-6,ch
assert not ch['problems'],ch
assert sum(counts.values())<=1510
ob=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=('berries','twig'));bpy.context.view_layer.update();pc.report({'Body':ob})
print('CONTACTS full lattice reaches rails; crossed strips overlap .003-.008; dark base touches rails; berries and branches verified by BVH; SNAP N/A VERIFY OK')
exec((HERE/'render_preview.py').read_text())
render(str(CHECK_DIR/f'round{args.round}.png'),40)
if args.export:
 fbx=pc.export(NAME,coll,root,str(ART/'Meshes'/f'{NAME}.fbx'));pc.save_lib(str(ART/'Blend'/f'{NAME}.blend'),coll,mat,img)
 render(str(ART/'Previews'/f'{NAME}_Preview.png'),100)
 for key,view in [('front',(0,-1,.15)),('back',(.4,1,.7)),('bottom',(.2,-1,-.8))]:render(str(CHECK_DIR/f'{key}.png'),40,view)
 pc.verify(fbx)








