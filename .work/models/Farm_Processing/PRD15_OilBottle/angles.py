from PIL import Image
from pathlib import Path
import os
p=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD15'
s=Image.new('RGB',(1024,320))
for i,n in enumerate(['back','side','top']):
 im=Image.open(p/(n+'.png'));im.thumbnail((340,320));s.paste(im,(i*340,0))
s.save(p/'angles.png')
