from PIL import Image
import os
from pathlib import Path
d=Path(os.environ['TEMP'])/'FarmProcessing_check'/'TOL06'
a=Image.open('planning/FarmProcessing/references/TOL-06.png').convert('RGB');b=Image.open('art/Farm_Processing/Previews/FMS_Workshop_TOL_06_Preview.png').convert('RGB')
a.thumbnail((640,600));b.thumbnail((640,600));out=Image.new('RGB',(1280,728),'#c7ccd3');out.paste(a,((640-a.width)//2,0));out.paste(b,(640+(640-b.width)//2,0))
for i,img in enumerate([a,b]):
 t=img.copy();t.thumbnail((128,128));out.paste(t,(256+i*640,600))
out.save(d/'final_compare.png')
