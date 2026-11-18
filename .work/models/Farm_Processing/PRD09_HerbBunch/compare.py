from PIL import Image,ImageOps
from pathlib import Path
import os
root=Path(__file__).resolve().parents[4]
p=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD09'
a=Image.open(root/'planning/FarmProcessing/references/PRD-09.png').convert('RGB');b=Image.open(p/'front.png').convert('RGB')
out=Image.new('RGB',(1024,512),'#c7ccd3');out.paste(ImageOps.contain(a,(512,512)),(0,0));out.paste(ImageOps.contain(b,(512,512)),(512,0));out.save(p/'compare.png');ImageOps.contain(b,(128,128)).save(p/'thumb.png')
