from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import os,sys
p=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD11'
r=int(sys.argv[1])
ref=Image.open('planning/FarmProcessing/references/PRD-11.png').convert('RGB'); im=Image.open(p/f'round{r}.png').convert('RGB')
# Match occupied model bounding boxes before comparison, since source framing differs.
def crop(im,bg,tol):
 import PIL.ImageChops as C
 diff=C.difference(im,Image.new('RGB',im.size,bg)).convert('L').point(lambda x:255 if x>tol else 0)
 return im.crop(diff.getbbox())
ref=ref.crop((175,200,1195,1015))
im=im.crop((60,18,455,307))
sheet=Image.new('RGB',(1024,540),'#c7ccd3')
for k,x in enumerate([ref,im]):
 x=ImageOps.contain(x,(500,470));sheet.paste(x,(k*512+(512-x.width)//2,20+(470-x.height)//2))
 thumb=ImageOps.contain(x,(128,128));sheet.paste(thumb,(k*512+190,412))
sheet.save(p/f'compare{r}.png')
