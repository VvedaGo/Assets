from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import os
p=Path(__file__).parent
check=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD-03'
ref=Image.open('planning/FarmProcessing/references/PRD-03.png').convert('RGB')
# crop neutral border; compare same occupied width rather than image canvas aspect.
ref=ref.crop((100,260,1280,940))
for i in (1,2,3):
 f=check/f'round{i}.png'
 if not f.exists():continue
 im=Image.open(f).convert('RGB')
 sheet=Image.new('RGB',(1024,460),'#c7ccd3')
 for j,src in enumerate((ref,im)):
  tile=ImageOps.contain(src,(500,340));sheet.paste(tile,(j*512+(512-tile.width)//2,20+(340-tile.height)//2))
  thumb=ImageOps.contain(src,(128,100));sheet.paste(thumb,(j*512+192,360))
 sheet.save(check/f'compare{i}.png')
