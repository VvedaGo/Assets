import json,re,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image,ImageOps,ImageDraw
out=Path(__file__).parent/'Media'/'References-v2'
out.mkdir(exist_ok=True)
urls=[
('Synty Nature','https://assetstore.unity.com/packages/3d/vegetation/trees/polygon-nature-pack-art-by-synty-120152'),
('Polyperfect Ultimate','https://assetstore.unity.com/packages/3d/props/low-poly-ultimate-pack-54733'),
('Synty Simple Farm','https://assetstore.unity.com/packages/3d/environments/industrial/simple-farm-cartoon-assets-47003'),
('Polytope Low Poly Farm','https://assetstore.unity.com/packages/3d/environments/industrial/low-poly-farm-pack-lite-188100')]
class Meta(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta' and a.get('property')=='og:image': self.image=a.get('content')
records=[]
for name,url in urls:
 try:
  s=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode()
  p=Meta();p.feed(s)
  image=p.image
  dest=out/(name.replace(' ','_')+'.png')
  dest.write_bytes(urllib.request.urlopen(image,timeout=30).read())
  # Inspect embedded state for current key images, without dumping the page.
  ident=url.rsplit('-',1)[-1]
  match=re.search('"'+ident+'":'+r'\s*(?=\{)',s)
  product=json.JSONDecoder().raw_decode(s[match.end():])[0] if match else {}
  keys=product.get('mainImage',{})
  for key in ['big','small','icon']:
   u=keys.get(key)
   if isinstance(u,str) and u:
    if u.startswith('//'):u='https:'+u
    if u.startswith('http'):
     (out/(name.replace(' ','_')+'_'+key+'.png')).write_bytes(urllib.request.urlopen(u,timeout=30).read())
  records.append({'name':name,'page':url,'image':image,'keys':keys})
  print(name,Image.open(dest).size,list(keys))
 except Exception as e: print(name,str(e)[:150])
(out/'sources.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
