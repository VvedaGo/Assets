import bpy,bmesh,sys,os,math,random
from pathlib import Path
from mathutils import Vector,Quaternion
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'_common'))
import processing_common as pc
NAME='FMS_Workshop_PRD_14'
ART=ROOT/'art'/'Farm_Processing'
CHECK=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD14'
CHECK.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROUND=int(args[0]) if args else 3
PAL=['#B5835A','#7A5233','#9C6B44','#F2E6C9','#DCC9A0','#C8473B','#A8372E','#8E959B','#6E757B','#A9AFB4','#A89A88','#8C7F6E','#EFE0BC','#DCC79A','#A29582','#9B8D79']
for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o,do_unlink=True)
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
coll=bpy.data.collections.new(NAME);sc.collection.children.link(coll)
root=bpy.data.objects.new(NAME,None);coll.objects.link(root)
for d in ('Textures','Meshes','Blend','Previews'): (ART/d).mkdir(exist_ok=True,parents=True)
img=pc.atlas_image('T_FarmProcessing_PRD14_BaseColor.png',str(ART/'Textures'/'T_FarmProcessing_PRD14_BaseColor.png'),PAL)
mat=pc.material('M_FarmProcessing_PRD14',img)
P=pc.Part('Body');bm=P.bm
# Accepted eleven-cobble design, polished with 20 vertices and +/-15mm radial samples.
radii=[.155,.165,.146,.135,.151,.160,.139,.144,.163,.153,.141,.161,.156,.135,.147,.165,.142,.154,.138,.158]
jitter=[0,1,-2,2,-1,1,0,-2,2,0,-1,2,-2,1,0,-1,2,-1,1,-2]
outline=[Vector((r*math.cos(i*math.tau/20+math.radians(jitter[i])),r*math.sin(i*math.tau/20+math.radians(jitter[i])))) for i,r in enumerate(radii)]
for axis in (0,1):
 lo=min(v[axis] for v in outline);hi=max(v[axis] for v in outline)
 for v in outline:v[axis]=(v[axis]-(lo+hi)/2)*.300/(hi-lo)
sites=[(-.084,-.083),(-.006,-.108),(.078,-.078),(-.085,-.006),(-.028,-.026),(.052,-.015),(.115,.030),(-.088,.078),(-.011,.063),(.068,.084),(.001,.124)]
heights=[.071,.078,.070,.080,.074,.0715,.079,.073,.080,.0765,.070]
slopes=[(.031,-.021),(-.035,.023),(.024,.036),(-.027,-.030),(.038,-.016),(-.024,.035),(.029,.027),(-.032,.026),(.028,-.036),(-.035,-.021),(.023,.033)]
def plate_z(ci,x,y):
 return heights[ci]+slopes[ci][0]*(x-sites[ci][0])+slopes[ci][1]*(y-sites[ci][1])
def clip(poly,n,d):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=a.dot(n)-d;db=b.dot(n)-d
  if da<=1e-10:out.append(a.copy())
  if (da<0)!=(db<0):out.append(a+(b-a)*(da/(da-db)))
 return out
cells=[]
for i,s in enumerate(sites):
 s=Vector(s);poly=[v.copy() for v in outline]
 for j,t in enumerate(sites):
  if i!=j:
   t=Vector(t);poly=clip(poly,t-s,(t.length_squared-s.length_squared)/2)
 cells.append(poly)
# Coordinate registry welds the true V-grooves (no intersecting fake crack strips).
registry={}
def vert(x,y,z):
 key=tuple(round(v,6) for v in (x,y,z))
 if key not in registry:registry[key]=bm.verts.new(key)
 return registry[key]
def boundary(p):
 return any(abs((b-a).cross(p-a))/(b-a).length<1e-6 and (p-a).dot(p-b)<=1e-8 for a,b in zip(outline,outline[1:]+outline[:1]))
# Shared low vertices follow the lower adjacent plate, 3mm below it.
levels={}
for ci,poly in enumerate(cells):
 for v in poly:
  key=(round(v.x,6),round(v.y,6))
  levels[key]=min(levels.get(key,1),plate_z(ci,v.x,v.y)-.003)
# Keep the broadest (almost straight) corners uncut to avoid spending triangles on invisible bevels.
corner_angles=[]
for ci,poly in enumerate(cells):
 for k,v in enumerate(poly):
  dot=(poly[k-1]-v).normalized().dot((poly[(k+1)%len(poly)]-v).normalized())
  corner_angles.append((dot,ci,k))
skip_corners={(ci,k) for _,ci,k in sorted(corner_angles)[:16]}
faces=[];outeredges=[]
for ci,poly in enumerate(cells):
 # A wide bevel plus clipped corners makes each plate a rounded chunky cobble.
 inner=[Vector(v) for v in pc.inset([tuple(v) for v in poly],.0038)]
 low=[vert(v.x,v.y,levels[(round(v.x,6),round(v.y,6))]) for v in poly]
 entry=[];exit=[];top=[]
 for k,v in enumerate(inner):
  prev=inner[k-1];nxt=inner[(k+1)%len(inner)]
  if (ci,k) in skip_corners:
   vv=vert(v.x,v.y,plate_z(ci,v.x,v.y));entry.append(vv);exit.append(vv);top.append(vv)
   continue
  cut=min(.0055,(v-prev).length*.22,(nxt-v).length*.22)
  a=v+(prev-v).normalized()*cut;b=v+(nxt-v).normalized()*cut
  va=vert(a.x,a.y,plate_z(ci,a.x,a.y));vb=vert(b.x,b.y,plate_z(ci,b.x,b.y))
  entry.append(va);exit.append(vb);top.extend((va,vb))
 faces.append(P.face(top,[10,14,10,14,10,15,10,14,10,15,10][ci]))
 for k in range(len(poly)):
  j=(k+1)%len(poly)
  if entry[k]!=exit[k]:faces.append(P.face([low[k],exit[k],entry[k]],15))
  faces.append(P.face([low[k],low[j],entry[j],exit[k]],15))
  if boundary((poly[k]+poly[j])/2):outeredges.append((poly[k],poly[j],low[k],low[j]))
 print('PLATE',ci,'main sides',len(poly),'top height',heights[ci])
# One flat wall per outer segment; top edge slopes into chamfer. Collinear splits are intentional.
bottom=[]
for a,b,va,vb in outeredges:
 ba=vert(a.x,a.y,0);bb=vert(b.x,b.y,0)
 if ROUND<3:
  faces.append(P.face([ba,bb,vb,va],11 if len(bottom)%3 else 15))
 else:
  def mid(p):
   angle=math.atan2(p.y,p.x)
   dr=.0055*math.sin(angle*5+.7)
   pp=p.normalized()*(p.length+dr)
   return vert(pp.x,pp.y,.029+.002*math.sin(angle*3))
  ma,mb=mid(a),mid(b)
  faces.append(P.face([ba,bb,mb,ma],11))
  faces.append(P.face([ma,mb,vb,va],11 if len(bottom)%3 else 15))
 bottom.append(ba)
bottom=list(set(bottom));bottom.sort(key=lambda v:math.atan2(v.co.y,v.co.x))
faces.append(P.face(list(reversed(bottom)),11))
# Drop orphan vertices from the initial candidate list.
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
P.comp.append(('cake_cracked_body',faces,True))
# Closed low-poly lens with a short ridge, rather than a radial pole fan.
seed_rng=random.Random(1405)
def seed(name,c,u,v,n,L,W,cream):
 c,u,v,n=Vector(c),Vector(u),Vector(v),Vector(n)
 if name.startswith('top_'):c-=n*.0025  # preserve embedded seating after tilt
 azimuth=seed_rng.uniform(0,math.tau);angle=seed_rng.uniform(10,25)
 axis=u*math.cos(azimuth)+v*math.sin(azimuth)
 rotation=Quaternion(axis,math.radians(angle))
 u,v,n=rotation@u,rotation@v,rotation@n
 print('SEED_TILT',name,round(angle,2),'deg axis azimuth',round(math.degrees(azimuth),2))
 xy=[(-.5,0),(-.26,-.5),(.26,-.40),(.5,0),(.22,.50),(-.28,.43)]
 vs=[bm.verts.new(c+u*(x*L)+v*(y*W)) for x,y in xy]
 vs += [bm.verts.new(c+u*(-.16*L)+n*(.007 if cream else .005)),bm.verts.new(c+u*(.18*L)+n*(.007 if cream else .005)),bm.verts.new(c-n*(.007 if cream else .005))]
 idx=[(0,1,6),(1,2,7,6),(2,3,7),(3,4,7),(4,5,6,7),(5,0,6),(0,8,1),(1,8,2),(2,8,3),(3,8,4),(4,8,5),(5,8,0)]
 fs=[P.face([vs[k] for k in inds],(12 if i%3 else 13) if cream else (5 if i%3 else 6)) for i,inds in enumerate(idx)]
 P.comp.append((name,fs,False))
# Five cream and four russet top fragments, located well inside individual plates.
tops=[(-.077,-.073,25,True),(-.004,-.094,-15,True),(.074,-.069,60,True),(-.079,.072,-15,True),(.060,.078,30,True),(-.017,.057,75,True),(-.103,-.008,65,False),(-.027,-.024,15,False),(.053,-.010,-25,False),(.002,.117,-10,False)]
for k,(x,y,a,cream) in enumerate(tops):
 ci=min(range(len(sites)),key=lambda i:(x-sites[i][0])**2+(y-sites[i][1])**2)
 a=math.radians(a);z=plate_z(ci,x,y)+.001
 sx,sy=slopes[ci];n=Vector((-sx,-sy,1)).normalized()
 u=Vector((math.cos(a),math.sin(a),sx*math.cos(a)+sy*math.sin(a))).normalized();v=n.cross(u)
 seed(f'top_{k}',(x,y,z),u,v,n,.065 if cream else .040,.029 if cream else .024,cream)
# Wall fragments: derive exact side-facet support, equators sunk 1 mm.
for k,(ang,z,tilt,cream) in enumerate([(-155,.041,40,True),(-108,.026,-20,True),(-63,.039,50,True),(-13,.044,70,True),(-132,.048,75,False),(-37,.022,30,False)]):
 a=math.radians(ang);d=Vector((math.cos(a),math.sin(a)))
 # Intersect radial ray with each external segment, then use that segment's outward normal.
 best=None
 for j,p in enumerate(outline):
  q=outline[(j+1)%len(outline)];e=q-p;den=d.cross(e)
  if abs(den)<1e-8:continue
  t=p.cross(e)/den;s=p.cross(d)/den
  if t>0 and 0<=s<=1:best=(t,p,q)
 t,p,q=best;e=(q-p).normalized();n=Vector((e.y,-e.x,0));tang=Vector((e.x,e.y,0));up=Vector((0,0,1));tilt=math.radians(tilt)
 u=tang*math.cos(tilt)+up*math.sin(tilt);v=-tang*math.sin(tilt)+up*math.cos(tilt)
 c=Vector((d.x*t,d.y*t,z))-n*.001
 seed(f'wall_{k}',c,u,v,n,.060 if cream else .040,.028 if cream else .024,cream)
# Center complete bbox for exact ground-centre pivot.
lo=Vector([min(v.co[i] for v in bm.verts) for i in range(3)]);hi=Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
off=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,0))
for v in bm.verts:v.co-=off
# Measured per-component triangle evidence.
for nm,fs,_ in P.comp:print('COMPONENT',nm,'tris',sum(len(f.verts)-2 for f in fs))
for e in bm.edges:
 if not e.is_manifold: print('BAD_EDGE', [tuple(round(t,8) for t in v.co) for v in e.verts],len(e.link_faces))
chk=pc.comp_checks(P,mirror_skip=[c[0] for c in P.comp]);assert not(chk['nonmanifold'] or chk['loose'] or chk['degenerate'] or chk['problems']),chk
body=pc.to_object(P,NAME,coll,mat,(0,0,0),root,mirror_skip=[c[0] for c in P.comp]);bpy.context.view_layer.update()
total=pc.report({'Body':body});assert total<=720
print('Budget 150-350; authorized ceiling 720:',total,'| Asymmetry intentional | SNAP/verify ground and bbox center OK')
CFG={'view':(-.30,-1,.68),'fill':(.74,.85)}
exec((HERE/'render_preview.py').read_text())
if ROUND<3:
 render(str(CHECK/f'round{ROUND}.png'),40)
else:
 fbx=str(ART/'Meshes'/f'{NAME}.fbx');pc.export(NAME,coll,root,fbx)
 pc.save_lib(str(ART/'Blend'/f'{NAME}.blend'),coll,mat,img)
 render(str(ART/'Previews'/f'{NAME}_Preview.png'),100)
 for nm,view in [('back',(.4,1,.5)),('side',(1,0,.3)),('top',(0,-.001,1))]:render(str(CHECK/f'{nm}.png'),40,view)
 pc.verify(fbx)
