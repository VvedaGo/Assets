from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,shutil,csv,hashlib,zipfile

root=Path(__file__).resolve().parent
delivery=root.parents[2]/'output/FarmMarket_421724_Media_2026-11-02'
allowed=json.loads((root/'delivery-current-files.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((root/'media-manifest.json').read_text(encoding='utf-8'))
for p in (root/'Upload').glob('*.png'):shutil.copy2(p,root.parent/'Upload'/p.name)
for name in allowed:shutil.copy2(root/'Upload'/name,delivery/'Upload'/name)
manifest=[m for m in manifest if m['file'] in allowed]
for m in manifest:m['background_style']='sage 2026-11-02; illustrated icon retained'
(delivery/'media-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in (root,delivery):
 fs=sorted((folder/'Upload').glob('*.png'))
 out=Image.new('RGB',(1200,((len(fs)+2)//3)*260),'#F2F4EE');d=ImageDraw.Draw(out)
 for i,p in enumerate(fs):
  x=i%3*400;y=i//3*260;out.paste(ImageOps.contain(Image.open(p),(390,225),Image.Resampling.LANCZOS),(x+5,y+25));d.text((x+8,y+5),p.name,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',14),fill='#20242A')
 out.save(folder/'REVIEW_CONTACT_SHEET.jpg',quality=94)
 doc=folder/'REUPLOAD.md'
 note='\n\n## Обновление фона — шалфейная палитра\n\nHero, Card, Cover и Social заново отрендерены на мягкой шалфейной заливке (целевой #B8C8B0). Каталожные и технические постановки — на светлом серо-зелёном фоне (#DEE5D8). Песчаная подставка осветлена и стала менее жёлтой (#DDD0AF); цвета материалов откалиброваны по результату Unity-рендера. Графические поля и коллажи согласованы с новой палитрой. Рисованная иконка сохранена. Состав текущей папки Upload оставлен прежним, ранее убранные из неё кадры не возвращены. Прошлый светлый вариант сохранён в рабочей копии в PreviousWhiteBackground_2026-11-02.\n'
 if doc.exists() and '## Обновление фона — шалфейная палитра' not in doc.read_text(encoding='utf-8-sig'):
  with doc.open('a',encoding='utf-8') as f:f.write(note)
with (delivery/'SHA256.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['File','SHA256'])
 for p in sorted((delivery/'Upload').glob('*.png')):
  with Image.open(p) as im:im.verify()
  w.writerow([p.name,hashlib.sha256(p.read_bytes()).hexdigest()])
with zipfile.ZipFile(delivery/'FarmMarket_421724_Reupload.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted((delivery/'Upload').glob('*.png')):z.write(p,'Upload/'+p.name)
 for name in ('REUPLOAD.md','REVIEW_CONTACT_SHEET.jpg'):z.write(delivery/name,name)
assert hashlib.sha256((delivery/'Upload/Icon_160x160.png').read_bytes()).hexdigest()==hashlib.sha256((root/'IllustratedIcon/Icon_160x160.png').read_bytes()).hexdigest()
print(f'PASS: {len(allowed)} existing delivery files updated; illustrated icon unchanged; ZIP and hashes rebuilt.')
