from pathlib import Path
from PIL import Image
import os,sys
root=Path(__file__).resolve().parents[4]
d=Path(os.environ['TEMP'])/'FarmProcessing_check'/'PRD06'
n=sys.argv[1] if len(sys.argv)>1 else '1'
ref=Image.open(root/'planning/FarmProcessing/references/PRD-06.png').convert('RGB')
src=Path(sys.argv[2]) if len(sys.argv)>2 else d/f'round{n}.png'
im=Image.open(src).convert('RGB')
sheet=Image.new('RGB',(1024,512),'#c7ccd3')
for i,pic in enumerate((ref,im)):
    pic.thumbnail((512,512));sheet.paste(pic,(512*i+(512-pic.width)//2,(512-pic.height)//2))
sheet.save(d/f'compare{n}.png')
im.thumbnail((128,128));im.save(d/f'thumb{n}.png')
