"""Farm Nature main store images: Icon, Card, Cover, Social.

Input:  Draft/_main/Overall_alpha.png (4800x2700), Draft/_main/Icon_alpha.png (2048x2048)
        (Unity: Tools/Farm Nature/Render Main Images Parts; transparent background)
Output: Draft/Icon_1024.png, Icon_160x160.png, Card_1260x840.png, Card_420x280.png,
        Cover_1950x1300.png, Social_1200x630.png
Series style (same as Farm Market, REQUIREMENTS 7.6): Arial Bold, plaque #20242A, cream #F2E6C9,
accent strip #C8473B. Background: warm light gradient (green island needs contrast; sage would swallow it).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DRAFT = HERE / 'Draft'
MAIN = DRAFT / '_main'
PLAQUE = (32, 36, 42)
CREAM = (242, 230, 201)
RED = (200, 71, 59)
TOP, BOTTOM = (248, 243, 231), (229, 220, 199)
FONT = 'C:/Windows/Fonts/arialbd.ttf'
TITLE = 'FARM NATURE'
ACCENT_COVER = '88 MODELS · LOW POLY · URP'   # 88 = verified prefab count of this build
ACCENT_CARD = 'LOW POLY · URP'


def gradient(w, h):
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / max(1, h - 1)
        d.line((0, y, w, y), fill=tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * k) for i in range(3)))
    return img


def place(canvas, src, box):
    """Fit src (RGBA) into box=(x, y, w, h), centred; returns the pasted rect."""
    x, y, w, h = box
    s = min(w / src.width, h / src.height)
    pic = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    px, py = round(x + (w - pic.width) / 2), round(y + (h - pic.height) / 2)
    canvas.paste(pic, (px, py), pic)
    return px, py, pic.width, pic.height


def crop_alpha(src, rect):
    return src.crop(rect)


def plaque(canvas, top, title_h, strip_h, title_size, accent, accent_size, left):
    w = canvas.width
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, top, w, top + title_h), fill=PLAQUE)
    d.text((left, top + title_h / 2), TITLE, font=ImageFont.truetype(FONT, title_size), fill=CREAM, anchor='lm')
    d.rectangle((0, top + title_h, w, top + title_h + strip_h), fill=RED)
    d.text((left, top + title_h + strip_h / 2), accent, font=ImageFont.truetype(FONT, accent_size), fill=CREAM, anchor='lm')


def cover(overall):
    img = gradient(1950, 1300).convert('RGBA')
    place(img, overall, (40, 18, 1870, 966))            # content: top 76%
    plaque(img, 1000, 225, 75, 118, ACCENT_COVER, 38, 64)
    out = DRAFT / 'Cover_1950x1300.png'
    img.convert('RGB').save(out)
    return out


def card(overall):
    # closer framing than the cover: oak, orchard, stream with bridge, pond (centre of the island)
    W, H = overall.size
    # crop aspect = 1260:530 (2.38) so the content fills the full card width; fields on the left are cut
    x0, x1, y0 = 0.10, 0.94, 0.0
    h = (x1 - x0) * W * 530 / 1260
    region = crop_alpha(overall, (round(W * x0), round(H * y0), round(W * x1), round(H * y0 + h)))
    img = gradient(1260, 840).convert('RGBA')
    place(img, region, (0, 0, 1260, 530))
    plaque(img, 530, 230, 80, 104, ACCENT_CARD, 42, 44)
    img = img.convert('RGB')
    img.save(DRAFT / 'Card_1260x840.png')
    small = img.resize((420, 280), Image.LANCZOS)
    small.save(DRAFT / 'Card_420x280.png')
    return DRAFT / 'Card_420x280.png'


def social(overall):
    img = gradient(1200, 630).convert('RGBA')
    place(img, overall, (60, 30, 1080, 570))            # clean scene, safe margins for cropping
    out = DRAFT / 'Social_1200x630.png'
    img.convert('RGB').save(out)
    return out


def icon(vignette):
    img = gradient(1024, 1024).convert('RGBA')
    place(img, vignette, (102, 102, 820, 820))          # ~80% of the frame
    img = img.convert('RGB')
    img.save(DRAFT / 'Icon_1024.png')
    img.resize((160, 160), Image.LANCZOS).save(DRAFT / 'Icon_160x160.png')
    return DRAFT / 'Icon_160x160.png'


if __name__ == '__main__':
    overall = Image.open(MAIN / 'Overall_alpha.png').convert('RGBA')
    vignette = Image.open(MAIN / 'Icon_alpha.png').convert('RGBA')
    for f in (cover(overall), card(overall), social(overall), icon(vignette)):
        print(f)
