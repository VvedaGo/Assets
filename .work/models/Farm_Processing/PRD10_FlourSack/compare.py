from PIL import Image,ImageOps
from pathlib import Path
import os,sys
root=Path(__file__).resolve().parents[4]
check=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD10'
mode=sys.argv[1]
ref=Image.open(root/'planning/FarmProcessing/references/PRD-10.png').convert('RGB')
preview=Image.open(check/(mode+'.png')).convert('RGB') if mode!='final' else Image.open(root/'art/Farm_Processing/Previews/FMS_Workshop_PRD_10_Preview.png').convert('RGB')
out=Image.new('RGB',(1024,512),'#c7ccd3')
for x,im in ((0,ref),(512,preview)):
    im=ImageOps.contain(im,(512,512));out.paste(im,(x+(512-im.width)//2,(512-im.height)//2))
out.save(check/(mode+'_compare.png'))
preview.thumbnail((128,128));preview.save(check/(mode+'_thumb.png'))
