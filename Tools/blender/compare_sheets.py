# compare_sheets.py - reference | model comparison sheets for model review (3 pairs per sheet, uniform background auto-cropped).
#   python -I compare_sheets.py --ref <dir with ID.png> --pre <dir with previews> \
#          [--pattern "FMS_Workshop_{id_}_Preview.png"] [--out <dir>] [ID ...]
# {id} = reference file name without .png (e.g. STA-05), {id_} = the same with '-' replaced by '_'.
# Without IDs: every reference in --ref, sorted. Output defaults to %TEMP%/pack_review (check renders never go into art/).
# Workflow: read every sheet, write verdicts into a review file (Tools/agents/REVIEW_TEMPLATE.md), delete the folder.
import os, glob, argparse
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('--ref', required=True)
ap.add_argument('--pre', required=True)
ap.add_argument('--pattern', default='{id}_Preview.png')
ap.add_argument('--out', default=os.path.join(os.environ.get('TEMP', '.'), 'pack_review'))
ap.add_argument('ids', nargs='*')
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)
ids = A.ids or sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(A.ref, '*.png')))
H, W = 250, 300


def crop_content(im, bg_thr=18):
    """trim the uniform background (sampled at the corner) so the object fills the cell"""
    g = im.convert('RGB'); px = g.load(); w, h = g.size; c0 = px[2, 2]
    xs, ys = [], []
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            p = px[x, y]
            if sum(abs(p[i] - c0[i]) for i in range(3)) > bg_thr: xs.append(x); ys.append(y)
    if not xs: return g
    m = 12
    return g.crop((max(0, min(xs) - m), max(0, min(ys) - m), min(w, max(xs) + m), min(h, max(ys) + m)))


def fit(im, w, h):
    im = im.copy(); im.thumbnail((w, h), Image.LANCZOS)
    cell = Image.new('RGB', (w, h), (235, 235, 238)); cell.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return cell


for si in range(0, len(ids), 3):
    group = ids[si:si + 3]
    sheet = Image.new('RGB', (2 * W + 10, len(group) * (H + 6)), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    for r, i in enumerate(group):
        ref = crop_content(Image.open(os.path.join(A.ref, i + '.png')))
        pre_path = os.path.join(A.pre, A.pattern.format(id=i, id_=i.replace('-', '_')))
        pre = crop_content(Image.open(pre_path)) if os.path.isfile(pre_path) else Image.new('RGB', (W, H), (255, 200, 200))
        y = r * (H + 6)
        sheet.paste(fit(ref, W, H), (0, y)); sheet.paste(fit(pre, W, H), (W + 10, y))
        d.text((4, y + 2), i + ' REF', fill=(200, 0, 0)); d.text((W + 14, y + 2), i + ' MODEL', fill=(0, 0, 200))
    sheet.save(os.path.join(A.out, f'sheet_{si // 3:02d}_{group[0]}_{group[-1]}.png'))
print(len(ids), 'ids ->', A.out)
