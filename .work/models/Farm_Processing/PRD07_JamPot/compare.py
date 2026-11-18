from PIL import Image, ImageChops, ImageDraw
from pathlib import Path
import os, sys
root=Path(__file__).resolve().parents[4]
tmp=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD07'
ref=Image.open(root/'planning/FarmProcessing/references/PRD-07.png').convert('RGB').crop((245,105,1112,1064))
our=Image.open(tmp/'check.png').convert('RGB')
bg=Image.new('RGB',our.size,our.getpixel((0,0)))
mask=ImageChops.difference(our,bg).convert('L').point(lambda p:255 if p>20 else 0)
our=our.crop(mask.getbbox())
sheet=Image.new('RGB',(780,490),'#c7ccd3')
for i,im in enumerate((ref,our)):
    scale=min(370/im.width,410/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)))
    sheet.paste(im,(i*390+(390-im.width)//2,20))
    th=im.copy();th.thumbnail((128,128));sheet.paste(th,(i*390+250,355))
out=tmp/('round'+(sys.argv[1] if len(sys.argv)>1 else '1')+'.png');sheet.save(out);print(out)
views=Image.new('RGB',(768,480),'#c7ccd3')
for i,n in enumerate(['check.png','angle0.png','angle1.png','angle2.png']):
    im=Image.open(tmp/n);im.thumbnail((384,240)); views.paste(im,((i%2)*384,(i//2)*240))
views.save(tmp/'views.png')
