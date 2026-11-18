from PIL import Image
from pathlib import Path
import os
d=Path(os.environ['TEMP'])/'FarmProcessing_check/STA08'
ref=Image.open('planning/FarmProcessing/references/STA-08.png').convert('RGB').crop((185,38,1175,1105))
def sheet(n,path=None):
    im=Image.open(path or d/('round'+str(n)+'.png')).convert('RGB')
    # crop neutral margins on our image to compare silhouettes at equal height
    bg=im.getpixel((0,0))
    from PIL import ImageChops
    delta=ImageChops.difference(im,Image.new('RGB',im.size,bg)).convert('L').point(lambda x:255 if x>25 else 0)
    im=im.crop(delta.getbbox())
    out=Image.new('RGB',(900,512),(220,223,228))
    for k,x in enumerate([ref,im]):
        x.thumbnail((440,500));out.paste(x,(k*450+(450-x.width)//2,(512-x.height)//2))
    out.save(d/('compare'+str(n)+'.png'))
    im.thumbnail((128,128));im.save(d/('thumb'+str(n)+'.png'))
import sys
sheet(int(sys.argv[1]) if len(sys.argv)>1 else 1)
