from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, shutil, hashlib, csv, zipfile, sys

root=Path(__file__).resolve().parent
delivery=root.parents[2]/'output/FarmMarket_421724_Media_2026-11-02'
masters=root/'IllustratedIcon'
masters.mkdir(exist_ok=True)
src=Path(sys.argv[1])
shutil.copy2(src,masters/'Icon_Master.png')
im=Image.open(src).convert('RGB')
assert im.width==im.height
for size in (1024,512,160,60):
 im.resize((size,size),Image.Resampling.LANCZOS).save(masters/f'Icon_{size}x{size}.png',optimize=True)
uploads=[root/'Upload',root.parent/'Upload',delivery/'Upload']
for dest in uploads:
 old=dest/'Icon_160x160.png'
 backup=masters/('Previous_Render_Icon_'+('delivery' if dest==delivery/'Upload' else 'local')+'.png')
 if old.exists() and not backup.exists():shutil.copy2(old,backup)
 shutil.copy2(masters/'Icon_160x160.png',old)
for folder in (root,delivery):
 manifest=folder/'media-manifest.json'
 if manifest.exists():
  entries=json.loads(manifest.read_text(encoding='utf-8-sig'))
  for item in entries:
   if item.get('file')=='Icon_160x160.png':item.update(source='IllustratedIcon/Icon_Master.png — generated with built-in imagegen',caption='3D',scene=None,status='exported; visually checked at 160 and 60 px')
  manifest.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
 note='\n\n## Обновление иконки — иллюстрация\n\nПо запросу владельца Icon заменён на отдельную иллюстрацию: ящик с овощами, зелёный атмосферный фон и небольшая плашка 3D в цветах серии. Создано встроенным imagegen; это рекламная иллюстрация, а не рендер моделей. Файл для слота магазина: Upload/Icon_160x160.png. Мастер и экспорты 1024/512/160/60 сохранены в IllustratedIcon рабочей копии. Остальные изображения этой правкой не изменялись.\n'
 doc=folder/'REUPLOAD.md'
 if doc.exists() and '## Обновление иконки — иллюстрация' not in doc.read_text(encoding='utf-8-sig'):
  with doc.open('a',encoding='utf-8') as f:f.write(note)
 # Use the current Upload contents: do not restore removed gallery images.
 fs=sorted((folder/'Upload').glob('*.png'))
 sheet=Image.new('RGB',(1200,((len(fs)+2)//3)*260),'white');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(fs):
  x=i%3*400;y=i//3*260;sheet.paste(ImageOps.contain(Image.open(p),(390,225),Image.Resampling.LANCZOS),(x+5,y+25));draw.text((x+8,y+5),p.name,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',14),fill='#20242A')
 sheet.save(folder/'REVIEW_CONTACT_SHEET.jpg',quality=92)
shutil.copy2(masters/'Icon_Master.png',delivery/'Icon_Illustrated_Master.png')
with (delivery/'SHA256.csv').open('w',newline='',encoding='utf-8') as f:
 writer=csv.writer(f);writer.writerow(['File','SHA256'])
 for p in sorted((delivery/'Upload').glob('*.png')):writer.writerow([p.name,hashlib.sha256(p.read_bytes()).hexdigest()])
with zipfile.ZipFile(delivery/'FarmMarket_421724_Reupload.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((delivery/'Upload').glob('*.png')):z.write(p,'Upload/'+p.name)
 for name in ('REUPLOAD.md','REVIEW_CONTACT_SHEET.jpg'):z.write(delivery/name,name)
print('Icon exported; Upload copies, contact sheets, manifest and archive updated.')
