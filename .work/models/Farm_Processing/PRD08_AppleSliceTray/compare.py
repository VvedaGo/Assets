from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import os,argparse
p=argparse.ArgumentParser();p.add_argument('round',type=int);p.add_argument('--final',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[4]
tmp=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD08'
r=Image.open(root/'planning/FarmProcessing/references/PRD-08.png').convert('RGB')
s=Image.open(root/'art/Farm_Processing/Previews/FMS_Workshop_PRD_08_Preview.png' if a.final else tmp/('round%d.png'%a.round)).convert('RGB')
# Normalize canvas proportions for a useful comparison; retain the whole object.
r=ImageOps.contain(r,(512,427));s=ImageOps.contain(s,(512,427))
c=Image.new('RGB',(1024,460),'#c7ccd3');c.paste(r,((512-r.width)//2,25));c.paste(s,(512+(512-s.width)//2,25+(427-s.height)//2))
d=ImageDraw.Draw(c);d.text((15,5),'REFERENCE',fill='black');d.text((527,5),'ROUND %d'%a.round,fill='black')
c.save(tmp/('compare%d.png'%a.round))
t=ImageOps.contain(s,(128,128));t.save(tmp/('thumb%d.png'%a.round))
