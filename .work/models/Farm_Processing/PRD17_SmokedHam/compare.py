from PIL import Image,ImageOps
import os
root=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
c=os.path.join(os.environ['TEMP'],'FarmProcessing_check/PRD17')
ref=Image.open(os.path.join(root,'planning/FarmProcessing/references/PRD-17.png')).convert('RGB')
for i in (1,2,3):
 p=os.path.join(c,f'round{i}.png')
 if not os.path.isfile(p):continue
 im=Image.open(p).convert('RGB'); sheet=Image.new('RGB',(840,512),'#c7ccd3')
 sheet.paste(ImageOps.contain(ref,(420,512)),(0,0)); sheet.paste(ImageOps.contain(im,(420,512)),(420,0)); sheet.save(os.path.join(c,f'compare{i}.png'))
 ImageOps.contain(im,(128,128)).save(os.path.join(c,f'thumb{i}.png'))
