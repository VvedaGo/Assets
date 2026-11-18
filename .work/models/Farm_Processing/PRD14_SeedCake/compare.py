from PIL import Image,ImageOps
from pathlib import Path
import os,sys
base=Path(__file__).resolve().parent
check=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD14'
n=int(sys.argv[1]);ref=Image.open('planning/FarmProcessing/references/PRD-14.png').convert('RGB')
pic=Image.open(check/f'round{n}.png') if n<3 else Image.open('art/Farm_Processing/Previews/FMS_Workshop_PRD_14_Preview.png')
sheet=Image.new('RGB',(1024,512),'#c7ccd3')
sheet.paste(ImageOps.contain(ref,(512,512)),(0,0));sheet.paste(ImageOps.contain(pic.convert('RGB'),(512,512)),(512,80))
sheet.save(check/f'compare{n}.png');ImageOps.contain(pic,(128,128)).save(check/f'thumb{n}.png')
