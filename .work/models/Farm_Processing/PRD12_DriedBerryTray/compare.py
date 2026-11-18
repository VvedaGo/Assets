from PIL import Image,ImageOps
from pathlib import Path
import os,sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]; D=Path(os.environ['TEMP'])/'FarmProcessing_check/PRD12'
r=int(sys.argv[1]); ref=Image.open(ROOT/'planning/FarmProcessing/references/PRD-12.png').convert('RGB'); out=Image.open(D/f'round{r}.png').convert('RGB')
a=ImageOps.contain(ref,(512,427));b=ImageOps.contain(out,(512,427)); sheet=Image.new('RGB',(1024,427),'#c7ccd3');sheet.paste(a,((512-a.width)//2,(427-a.height)//2));sheet.paste(b,(512+(512-b.width)//2,(427-b.height)//2));sheet.save(D/f'compare{r}.png');ImageOps.contain(out,(128,128)).save(D/f'thumb{r}.png')
