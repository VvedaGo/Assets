from PIL import Image
from pathlib import Path
import os,sys
n=sys.argv[1]; d=Path(os.environ['TEMP'])/'FarmProcessing_check'/'TOL06'
a=Image.open('planning/FarmProcessing/references/TOL-06.png').convert('RGB'); b=Image.open(d/('round'+n+'.png')).convert('RGB')
a.thumbnail((512,440));b.thumbnail((512,440)); out=Image.new('RGB',(1024,568),'#c7ccd3');out.paste(a,((512-a.width)//2,0));out.paste(b,(512+(512-b.width)//2,0))
for i,img in enumerate([a,b]):
 t=img.copy();t.thumbnail((128,128));out.paste(t,(192+i*512,440))
out.save(d/('compare'+n+'.png'))
