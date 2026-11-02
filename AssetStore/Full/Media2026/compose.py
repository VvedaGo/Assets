"""Typography/layout for Unity renders, with an explicitly illustrated promotional icon."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import csv, json, shutil

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'Raw'
DEST=ROOT/'Upload'
DEST.mkdir(exist_ok=True)
INK='#20242A'; CREAM='#F2E6C9'; RED='#C8473B'; GRAY='#DEE5D8'
FONT='C:/Windows/Fonts/arialbd.ttf'
def font(s): return ImageFont.truetype(FONT,s)
def load(n): return Image.open(RAW/(n+'.png')).convert('RGB')
def fit(im,size): return ImageOps.fit(im,size,Image.Resampling.LANCZOS)
manifest=[]
def save(im,name,caption,source):
 im.save(DEST/name,optimize=True)
 manifest.append(dict(file=name,width=im.width,height=im.height,format='PNG',caption=caption,source=source,scene=None if source.startswith('AI ') else 'Assets/Scenes/StoreMedia2026/FarmMarket_Store.unity',package='Farm Market Starter 1.0',status='exported'))
def label(im,topic,note=None):
 d=ImageDraw.Draw(im);x,y=30,932;w=max(550,int(d.textlength(topic,font=font(32)))+65)
 d.rectangle((x,y,x+w,y+116),fill=INK);d.rectangle((x,y,x+6,y+116),fill=RED)
 d.text((x+24,y+15),'FARM MARKET STARTER',font=font(25),fill=CREAM)
 d.text((x+24,y+53),topic,font=font(32),fill='white')
 if note:d.text((1900-d.textlength(note,font=font(20)),1042),note,font=font(20),fill=INK)
 return im
def branded(raw,size,band,small=False):
 w,h=size; im=Image.new('RGB',size,INK)
 im.paste(fit(raw,(w,h-band)),(0,0))
 d=ImageDraw.Draw(im);p=round(w*.04);s=round(w*(.068 if small else .055))
 # Reserved logo position until the series logo has been selected.
 title=['FARM MARKET','STARTER'] if small else ['FARM MARKET STARTER']
 y=h-band+round(band*.13)
 for line in title:d.text((p,y),line,font=font(s),fill=CREAM);y+=round(s*1.1)
 stripe=round(band*.23);d.rectangle((0,h-stripe,w,h),fill=RED)
 d.text((p,h-stripe+round(stripe*.13)),'LOW POLY · URP',font=font(round(stripe*.62)),fill=CREAM)
 return im
def collage(names,labels,cols=2,crop=False):
 im=Image.new('RGB',(1920,1080),GRAY);d=ImageDraw.Draw(im)
 rows=(len(names)+cols-1)//cols;cw=1920//cols;ch=910//rows
 for i,(n,lab) in enumerate(zip(names,labels)):
  x=(i%cols)*cw;y=(i//cols)*ch
  src=load(n); pic=fit(src,(cw-18,ch-55)) if crop else ImageOps.contain(src,(cw-18,ch-55),Image.Resampling.LANCZOS)
  im.paste(pic,(x+(cw-pic.width)//2,y+8));d.text((x+25,y+ch-40),lab,font=font(25),fill=INK)
 return im

if __name__=='__main__':
 illustrated_icon=ROOT/'IllustratedIcon'/'Icon_Master.png'
 icon_source=Image.open(illustrated_icon).convert('RGB') if illustrated_icon.exists() else load('Icon')
 save(icon_source.resize((160,160),Image.Resampling.LANCZOS),'Icon_160x160.png','3D' if illustrated_icon.exists() else '', 'AI illustrated promotional icon' if illustrated_icon.exists() else 'Icon')
 save(branded(load('Card'),(1260,840),310,True).resize((420,280),Image.Resampling.LANCZOS),'Card_420x280.png','FARM MARKET STARTER / LOW POLY · URP','Card')
 save(branded(load('Cover'),(1950,1300),290),'Cover_1950x1300.png','FARM MARKET STARTER / LOW POLY · URP','Cover')
 save(fit(load('01_Hero'),(1200,630)),'Social_1200x630.png','','01_Hero')
 save(label(load('01_Hero'),'MARKET SHOWCASE','Display base and lighting: presentation setup'),'05_Hero.png','MARKET SHOWCASE','01_Hero')
 save(label(load('02_Collection'),'FULL COLLECTION · 119 PROPS'),'06_FullCollection.png','FULL COLLECTION · 119 PROPS','02_Collection')
 save(label(collage(['03_Produce_Detail','03b_Fruit_Detail','07_Food_Dairy'],['VEGETABLES','FRUIT','FOOD & DAIRY'],3,True),'MODEL DETAILS'),'07_Closeups.png','MODEL DETAILS','03_Produce_Detail / 03b_Fruit_Detail / 07_Food_Dairy')
 save(label(load('04_Stalls_Furniture'),'STALLS & FURNITURE'),'08_VariantsAndModules.png','STALLS & FURNITURE','04_Stalls_Furniture')
 tech=collage(['12_LOD','13_Colliders'],['ACTUAL LOD MESHES & TRIANGLE EDGES','ACTUAL BOX COLLIDER BOUNDS'])
 td=ImageDraw.Draw(tech)
 for x,txt in [(50,'LOD0: 384 tris'),(365,'LOD1: 288 tris'),(680,'LOD2: 192 tris')]:td.text((x,590),txt,font=font(27),fill=INK)
 td.text((45,660),'Example: berry basket filling (enlarged)',font=font(24),fill=INK)
 td.text((45,705),'LOD coverage varies by prefab.',font=font(24),fill=INK)
 td.text((1010,590),'Stall / crate / cart',font=font(30),fill=INK)
 td.text((1010,650),'Green outlines show actual BoxCollider bounds.',font=font(24),fill=INK)
 save(label(tech,'LOD & COLLIDERS'),'09_Technical.png','LOD & COLLIDERS','12_LOD / 13_Colliders')
 save(label(load('11_Demo_Layout'),'DEMO MARKET SQUARE · 119 PROPS + 6 COMPOSITIONS'),'10_DemoAndVersion.png','DEMO MARKET SQUARE · 119 PROPS + 6 COMPOSITIONS','11_Demo_Layout')
 cat=collage(['05_Produce_Collection','06_Containers'],['25 VEGETABLE & FRUIT PREFABS','32 CRATES, BASKETS & SACKS']);cd=ImageDraw.Draw(cat)
 cd.text((35,650),'Whole produce, cut pieces and greens',font=font(28),fill=INK)
 cd.text((995,650),'Empty containers and modular fillings',font=font(28),fill=INK)
 save(label(cat,'PRODUCE & CONTAINERS'),'11_CategoryDetails.png','PRODUCE & CONTAINERS','05_Produce_Collection / 06_Containers')
 save(label(load('10_Compositions'),'6 READY COMPOSITIONS'),'12_ModularityOrAnimation.png','6 READY COMPOSITIONS','10_Compositions')
 textures=Path(__file__).resolve().parents[3]/'Assets/FarmMarketFull/Art/Textures'
 tex=Image.new('RGB',(1920,1080),GRAY);d=ImageDraw.Draw(tex)
 samples=['T_Barrels_BaseColor.png','T_Basket_BaseColor.png','T_Bread_BaseColor.png','T_Cheese_BaseColor.png','T_Cart_BaseColor.png','T_Beet_BaseColor.png']
 for i,n in enumerate(samples):
  p=textures/n;src=Image.open(p).convert('RGB');x=35+(i%3)*310;y=35+(i//3)*390
  tex.paste(src.resize((280,280),Image.Resampling.NEAREST),(x,y));d.text((x,y+292),n.replace('T_','').replace('_BaseColor.png',''),font=font(26),fill=INK);d.text((x,y+328),f'{src.width} × {src.height}',font=font(22),fill=INK)
 tex.paste(ImageOps.contain(load('08_Food_Collection'),(900,490),Image.Resampling.LANCZOS),(990,25))
 for y,txt in [(540,'41 base-color textures'),(600,'43 URP materials'),(670,'256² / 512² / 1024² / 2048²'),(750,'Texture samples shown at left.')]:d.text((1010,y),txt,font=font(36 if y<650 else 26),fill=INK)
 save(label(tex,'MATERIALS & TEXTURES'),'13_MaterialsAndTextures.png','MATERIALS & TEXTURES','Actual texture files / 08_Food_Collection')
 if (RAW/'Editor.png').exists():
  ed=Image.new('RGB',(1920,1080),GRAY);pic=ImageOps.contain(load('Editor'),(1920,930),Image.Resampling.LANCZOS);ed.paste(pic,((1920-pic.width)//2,0))
  save(label(ed,'UNITY PROJECT & PREFAB'),'14_UnityAndComparison.png','UNITY PROJECT & PREFAB','Actual Unity Editor screenshot')
 (ROOT/'media-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
 out=Image.new('RGB',(1200,((len(manifest)+2)//3)*260),'white');d=ImageDraw.Draw(out)
 for i,m in enumerate(manifest):
  x=i%3*400;y=i//3*260;out.paste(ImageOps.contain(Image.open(DEST/m['file']),(390,225)),(x+5,y+25));d.text((x+8,y+5),m['file'],font=font(14),fill=INK)
 out.save(ROOT/'REVIEW_CONTACT_SHEET.jpg',quality=92)
