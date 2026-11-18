from PIL import Image,ImageOps
import os
root=r'C:\Users\Sergv\orca\workspaces\VFX\master-2'
c=os.path.join(os.environ['TEMP'],'FarmProcessing_check/PRD17')
ref=Image.open(os.path.join(root,'planning/FarmProcessing/references/PRD-17.png')).convert('RGB').crop((370,35,900,1095))
im=Image.open(os.path.join(root,'art/Farm_Processing/Previews/FMS_Workshop_PRD_17_Preview.png')).convert('RGB').crop((450,35,830,766))
sheet=Image.new('RGB',(650,512),'#c7ccd3')
sheet.paste(ImageOps.contain(ref,(325,512)),(0,0));sheet.paste(ImageOps.contain(im,(325,512)),(325,0));sheet.save(os.path.join(c,'compare_final.png'))
ImageOps.contain(im,(128,128)).save(os.path.join(c,'thumb_final.png'))
