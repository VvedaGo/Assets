# overlay: my check render scaled to the ref's model bbox height, bottom-centre aligned, 50% blend + edge lines
import sys, os, tempfile
from PIL import Image, ImageChops, ImageDraw, ImageFilter
tag = sys.argv[1]; d = os.path.join(tempfile.gettempdir(), 'FarmProcessing_check', 'STA-04')
ref = Image.open(r"C:\Users\Sergv\orca\workspaces\VFX\master-2\planning\FarmProcessing\references\STA-04.png").convert('RGB')
ren = Image.open(os.path.join(d, tag + '_ref.png')).convert('RGB')
def bbox(im):
    bg = Image.new('RGB', im.size, im.getpixel((5, 5)))
    m = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 18 else 0)
    return m.getbbox(), m
(rb, rm), (mb, mm) = bbox(ref), bbox(ren)
k = (rb[3] - rb[1]) / (mb[3] - mb[1])
ren2 = ren.resize((round(ren.width * k), round(ren.height * k))); mm2 = mm.resize(ren2.size)
mb2 = [round(v * k) for v in mb]
dx = (rb[0] + rb[2]) // 2 - (mb2[0] + mb2[2]) // 2; dy = rb[3] - mb2[3]
canvas = Image.new('RGB', ref.size, (255, 255, 255)); canvas.paste(ren2, (dx, dy))
out = Image.blend(ref, canvas, 0.5)
edge = Image.new('L', ref.size, 0); edge.paste(mm2.filter(ImageFilter.FIND_EDGES), (dx, dy))
out.paste((0, 90, 255), mask=edge)
dr = ImageDraw.Draw(out)
for y in range(0, out.height, 50): dr.line([(0, y), (12, y)], fill=(255, 0, 0))
out = out.resize((out.width * 2 // 3, out.height * 2 // 3)); out.save(os.path.join(d, tag + '_ovl.png'))
print('ref bbox', rb, 'render bbox scaled', [v + o for v, o in zip(mb2, (dx, dy, dx, dy))], 'widths', rb[2] - rb[0], mb2[2] - mb2[0])
