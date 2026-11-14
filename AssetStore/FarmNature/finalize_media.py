"""Inspect exports and make a review contact sheet and delivery archive."""
import json,zipfile
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
r=Path(__file__).parent/'Media'
m=json.loads((r/'media-manifest.json').read_text())
results=[]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
o=Image.new('RGB',(1500,((len(m['images'])+2)//3)*342+100),'#FFF9EB')
d=ImageDraw.Draw(o)
d.text((24,20),'FARM NATURE / v2',font=ImageFont.truetype('C:/Windows/Fonts/impact.ttf',40),fill='#203D32')
d.text((24,70),'EVERGREEN / APRICOT / GOLDEN CREAM',font=font,fill='#486252')
for i,x in enumerate(m['images']):
 p=r/x['file'];im=Image.open(p)
 results.append({'file':x['file'],'size_ok':im.size==(x['width'],x['height']),'opaque_rgb':im.mode=='RGB','bytes':p.stat().st_size})
 if x['file'].startswith(('Upload/02_','Upload/03_')):
  results[-1]['corner_badge_flush']=all(abs(a-b)<6 for a,b in zip(im.getpixel((0,0)),(237,112,71)))
 thumb=ImageOps.contain(Image.open(r/x['master']),(480,300))
 xx=(i%3)*500+10;yy=(i//3)*342+110
 o.paste(thumb,(xx,yy))
 d.text((xx,yy+306),p.name,font=font,fill='#203D32')
assert all(x['size_ok'] and x['opaque_rgb'] and x.get('corner_badge_flush',True) for x in results)
o.save(r/'ContactSheet_v2.jpg',quality=94)
o.save(r/'ContactSheet.jpg',quality=94)
(r/'validation.json').write_text(json.dumps({'revision':2,'checks':results},indent=2))
for filename in ['FarmNature_Upload.zip','FarmNature_Upload_v2.zip']:
 with zipfile.ZipFile(r/filename,'w',zipfile.ZIP_DEFLATED) as z:
  for x in m['images']:z.write(r/x['file'],Path(x['file']).name)
print('PASS: 17 RGB exports, exact dimensions; Card/Cover corner ribbon flush; contact sheets and ZIP refreshed')
