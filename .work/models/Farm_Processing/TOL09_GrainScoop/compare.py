from PIL import Image
from pathlib import Path
import os,sys
root=Path.cwd(); d=Path(os.environ['TEMP'])/'FarmProcessing_check/TOL09'
n=sys.argv[1] if len(sys.argv)>1 else '1'
ref=Image.open(root/'planning/FarmProcessing/references/TOL-09.png').convert('RGB'); ref.thumbnail((512,430))
im=Image.open(d/'TOL09_check.png').convert('RGB'); im.thumbnail((512,430))
out=Image.new('RGB',(1024,558),'#c7ccd3');out.paste(ref,((512-ref.width)//2,0));out.paste(im,(512,0))
thumb=im.copy();thumb.thumbnail((128,128));out.paste(thumb,(704,430));out.save(d/f'round{n}.png')
