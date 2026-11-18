from PIL import Image
import os
root=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
p=os.path.join(os.environ['TEMP'],'FarmProcessing_check','STA-09')
ref=Image.open(os.path.join(root,'planning/FarmProcessing/references/STA-09.png')); ref.thumbnail((540,500))
for tag in ['r1','r2','r3']:
 f=os.path.join(p,tag+'_ref.png')
 if os.path.exists(f):
  im=Image.open(f); im.thumbnail((640,500)); out=Image.new('RGB',(1180,500),'#c7ccd3');out.paste(ref,((540-ref.width)//2,0));out.paste(im,(540,0));out.save(os.path.join(p,tag+'_compare.png'))
