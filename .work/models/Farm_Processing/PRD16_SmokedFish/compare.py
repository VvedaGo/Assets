from PIL import Image,ImageOps
from pathlib import Path
import os
root=Path(__file__).resolve().parents[4]
p=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD16'
a=Image.open(root/'planning/FarmProcessing/references/PRD-16.png').convert('RGB');b=Image.open(p/'front.png').convert('RGB')
def crop(im):
    import PIL.ImageChops as C
    bg=Image.new('RGB',im.size,im.getpixel((0,0)))
    diff=C.difference(im,bg).convert('L').point(lambda x:255 if x>35 else 0)
    return im.crop(diff.getbbox())
out=Image.new('RGB',(1024,512),'#c7ccd3')
for i,im in enumerate((a,b)):
    im=ImageOps.contain(crop(im),(480,480));out.paste(im,(i*512+(512-im.width)//2,(512-im.height)//2))
out.save(p/'compare.png');ImageOps.contain(b,(128,128)).save(p/'thumb.png')

