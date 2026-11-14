"""Read-only FBX/Unity file audit for store metadata. No Unity state mutations."""
from pathlib import Path
import struct,zlib,json,re,csv,collections,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/'Assets/FarmNature'
OUT=Path(__file__).parent
def read_fbx(p):
 data=p.read_bytes()
 assert data.startswith(b'Kaydara FBX Binary'),str(p)
 version=struct.unpack_from('<I',data,23)[0]
 fmt,hs=('<QQQB',25) if version>=7500 else ('<IIIB',13)
 def node(pos):
  end,nprops,plen,nlen=struct.unpack_from(fmt,data,pos)
  if not end:return None,pos+hs
  pos+=hs; name=data[pos:pos+nlen].decode();pos+=nlen;props=[]
  for _ in range(nprops):
   t=chr(data[pos]);pos+=1
   if t in 'YCFDIL':
    f={'Y':'h','C':'?','F':'f','D':'d','I':'i','L':'q'}[t];props.append(struct.unpack_from('<'+f,data,pos)[0]);pos+=struct.calcsize(f)
   elif t in 'SR':
    n=struct.unpack_from('<I',data,pos)[0];pos+=4;v=data[pos:pos+n];pos+=n;props.append(v.decode('utf8',errors='replace') if t=='S' else v)
   elif t in 'fdlibc':
    n,enc,size=struct.unpack_from('<III',data,pos);pos+=12;raw=data[pos:pos+size];pos+=size
    if enc:raw=zlib.decompress(raw)
    f={'f':'f','d':'d','l':'q','i':'i','b':'?','c':'b'}[t];props.append(list(struct.unpack('<'+str(n)+f,raw)))
   else:raise ValueError(t)
  kids=[]
  while pos<end-hs:
   child,pos=node(pos)
   if child is None:break
   kids.append(child)
  return (name,props,kids),end
 nodes=[];pos=27
 while pos<len(data):
  v,pos=node(pos)
  if v is None:break
  nodes.append(v)
 return nodes
def walk(ns):
 for n in ns:
  yield n
  yield from walk(n[2])
models=[]
for p in sorted((PACK/'Art/Models').rglob('*.fbx')):
 ns=read_fbx(p);allnodes=list(walk(ns));geos=[n for n in allnodes if n[0]=='Geometry' and n[1][-1]=='Mesh']
 tris=polys=verts=0;uvs=[];ys=[]
 for g in geos:
  idx=next(n[1][0] for n in g[2] if n[0]=='PolygonVertexIndex')
  count=0
  for ix in idx:
   count+=1
   if ix<0:tris+=count-2;polys+=1;count=0
  points=next(n[1][0] for n in g[2] if n[0]=='Vertices');verts+=len(points)//3;ys+=points[1::3]
  uvs.append(len([n for n in g[2] if n[0]=='LayerElementUV']))
 props={n[1][0]:n[1][4:] for n in allnodes if n[0]=='P' and len(n[1])>=5}
 models.append({'file':p.relative_to(ROOT).as_posix(),'category':p.parent.name,'name':p.stem,'mesh_objects':len(geos),'triangles':tris,'polygons':polys,'vertices':verts,'uv_channels_per_mesh':uvs,'fbx_unit_scale_factor':props.get('UnitScaleFactor'),'fbx_up_axis':props.get('UpAxis'),'rig_nodes':sum(n[0]=='NodeAttribute' and 'LimbNode' in n[1] for n in allnodes),'animation_stacks':sum(n[0]=='AnimationStack' for n in allnodes),'geometry_min_y':min(ys) if ys else None,'geometry_max_y':max(ys) if ys else None})
prefabs=[]
for p in sorted((PACK/'Art/Prefabs').rglob('*.prefab')):
 s=p.read_text(encoding='utf8');types=collections.Counter(re.findall(r'^--- !u!(\d+) ',s,re.M))
 prefabs.append({'name':p.stem,'category':p.parent.name,'box_colliders':types['65'],'mesh_colliders':types['64'],'lod_groups':types['205'],'skinned_renderers':types['137'],'animators':types['95'],'scripts':types['114'],'mesh_filters':types['33'],'root_position':re.search(r'm_LocalPosition: (.+)',s).group(1),'root_scale':re.search(r'm_LocalScale: (.+)',s).group(1)})
textures=[]
for p in sorted(PACK.rglob('*.png')):
 im=Image.open(p)
 textures.append({'file':p.relative_to(ROOT).as_posix(),'scope':'art' if '/Art/' in p.as_posix() else 'demo','size':im.size,'mode':im.mode,'has_transparency':('A' in im.getbands() and im.getextrema()[im.getbands().index('A')][0]<255) or ('transparency' in im.info),'bytes':p.stat().st_size})
materials=[]
for p in sorted(PACK.rglob('*.mat')):
 s=p.read_text(encoding='utf8')
 materials.append({'file':p.relative_to(ROOT).as_posix(),'scope':'art' if '/Art/' in p.as_posix() else 'demo','shader':re.search(r'm_Shader: (.+)',s).group(1),'texture_guids':sorted(set(re.findall(r'guid: ([a-f0-9]{32})',s)))})
stats={}
for cat in sorted(set(m['category'] for m in models)):
 vals=[m['triangles'] for m in models if m['category']==cat]
 stats[cat]={'model_files':len(vals),'triangles_min':min(vals),'triangles_max':max(vals),'triangles_mean':round(sum(vals)/len(vals),2),'triangles_sum':sum(vals)}
 scene=(PACK/'Demo/Scenes/Demo_FarmNature_Showcase.unity').read_text(encoding='utf8')
audit={'method':'FBX binary polygon indices triangulated as n-2 per polygon; one source file counted once. Does not measure Unity mesh import changes or runtime scene draw calls. Prefab and scene checks are serialized-data checks, not play-mode tests.','models':models,'prefabs':prefabs,'textures':textures,'materials':materials,'category_stats':stats,'summary':{'model_files':len(models),'mesh_objects':sum(m['mesh_objects'] for m in models),'prefabs':len(prefabs),'triangles_min':min(m['triangles'] for m in models),'triangles_max':max(m['triangles'] for m in models),'triangles_mean':round(sum(m['triangles'] for m in models)/len(models),2),'triangles_sum':sum(m['triangles'] for m in models),'box_colliders':sum(p['box_colliders'] for p in prefabs),'lod_groups':sum(p['lod_groups'] for p in prefabs),'uv_channels':sorted(set(v for m in models for v in m['uv_channels_per_mesh'])),'rig_nodes':sum(m['rig_nodes'] for m in models),'animation_stacks':sum(m['animation_stacks'] for m in models),'scene_composition_names':sorted(set(re.findall(r'm_Name: (Comp_[^\r\n]+)',scene))),'scene_scripts':re.findall(r'm_Script: (.+)',scene),'raw_folder_bytes':sum(p.stat().st_size for p in PACK.rglob('*') if p.is_file())}}
release_studies=re.findall(r'm_Name: (0[1-6]_(?:VegetableGarden|HarvestField|AppleOrchard|PondAndBridge|ForestEdge|FlowerPath))',scene)
if release_studies:
 audit['summary']['scene_composition_names']=sorted(set(release_studies))
(OUT/'PACKAGE_AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
with (OUT/'MODEL_INVENTORY.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=['category','name','mesh_objects','triangles','polygons','vertices','uv_channels_per_mesh']);writer.writeheader();writer.writerows({k:m[k] for k in writer.fieldnames} for m in models)
print(json.dumps(audit['summary'],indent=2));print(json.dumps(stats,indent=2))
