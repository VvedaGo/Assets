from PIL import Image,ImageOps
from pathlib import Path
import os,sys
base=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD13'
r=sys.argv[1]
ref=Image.open('planning/FarmProcessing/references/PRD-13.png').convert('RGB')
out=Image.open(base/('round'+r+'.png')).convert('RGB')
sheet=Image.new('RGB',(1024,460),'#c7ccd3')
for i,im in enumerate((ref,out)):
 im=ImageOps.contain(im,(512,410));sheet.paste(im,(i*512+(512-im.width)//2,(410-im.height)//2))
 thumb=ImageOps.contain(im,(128,80));sheet.paste(thumb,(i*512+192,380))
sheet.save(base/('compare'+r+'.png'))
