from PIL import Image
from pathlib import Path
import os,sys
root=Path(r'C:\Users\Sergv\orca\workspaces\VFX\master-2')
tmp=Path(os.environ['TEMP'])/'FarmProcessing_check/TOL-10'
n=sys.argv[1]
a=Image.open(root/'planning/FarmProcessing/references/TOL-10.png').convert('RGB');a.thumbnail((512,400))
b=Image.open(tmp/f'round{n}.png').convert('RGB');b.thumbnail((512,400))
out=Image.new('RGB',(1024,400),'#c7ccd3');out.paste(a,((512-a.width)//2,(400-a.height)//2));out.paste(b,(512+(512-b.width)//2,(400-b.height)//2));out.save(tmp/f'compare{n}.png')
b.thumbnail((128,128));b.save(tmp/f'thumb{n}.png')
