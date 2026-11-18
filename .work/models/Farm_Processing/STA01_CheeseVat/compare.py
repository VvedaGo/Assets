# compare sheet: reference | check render (both 400 px high) -> %TEMP%\FarmProcessing_check\STA-01\<tag>_cmp.png
import sys, os, tempfile
from PIL import Image
tag = sys.argv[1]; d = os.path.join(tempfile.gettempdir(), 'FarmProcessing_check', 'STA-01')
ref = Image.open(r"C:\Users\Sergv\orca\workspaces\VFX\master-2\planning\FarmProcessing\references\STA-01.png").convert('RGB')
ren = Image.open(os.path.join(d, tag + '_ref.png')).convert('RGB')
H = 400
ref = ref.resize((round(ref.width * H / ref.height), H)); ren = ren.resize((round(ren.width * H / ren.height), H))
th = Image.open(os.path.join(d, tag + '_thumb.png')).convert('RGB')
out = Image.new('RGB', (ref.width + ren.width + th.width, H), (255, 255, 255))
out.paste(ref, (0, 0)); out.paste(ren, (ref.width, 0)); out.paste(th, (ref.width + ren.width, 0))
out.save(os.path.join(d, tag + '_cmp.png')); print(os.path.join(d, tag + '_cmp.png'), out.size)
