from pathlib import Path
from PIL import Image,ImageChops
import os,sys
root=Path(__file__).resolve().parents[4]
c=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD15'
r=int(sys.argv[1])
ref=Image.open(root/'planning/FarmProcessing/references/PRD-15.png').convert('RGB').crop((430,45,939,1095))
a=Image.open(c/f'round{r}.png').convert('RGB')
bg=Image.new('RGB',a.size,a.getpixel((0,0)))
mask=ImageChops.difference(a,bg).convert('L').point(lambda v:255 if v>30 else 0)
a=a.crop(mask.getbbox())
sheet=Image.new('RGB',(512,512),'#c7ccd3')
for i,im in enumerate((ref,a)):
 im=im.resize((int(im.width*470/im.height),470)); im.thumbnail((240,470)); sheet.paste(im,(i*256+(256-im.width)//2,(512-im.height)//2))
sheet.save(c/f'compare{r}.png')
a.thumbnail((128,128));a.save(c/f'thumb{r}.png')

