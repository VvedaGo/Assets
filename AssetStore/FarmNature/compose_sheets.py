"""Compose Farm Nature store sheets 02 (showcase) and 03 (local compositions) from Unity renders.

Input:  Draft/_parts02/Island_*.png|json, Draft/_parts03/<Comp>.png|json
        (Unity: Tools/Farm Nature/Render Hero 02 Showcase Parts, Render Hero 03 Local Parts)
Output: Draft/02_Showcase_Scene.png, Draft/03_Local_Compositions.png (1920x1080)
Style per NATURE_COMPOSITIONS/README.md: dark-green rounded plaques, cream text, one sans-serif font.
Usage:  python compose_sheets.py [en|ru]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DRAFT = HERE / 'Draft'
W, H = 1920, 1080
BG = (244, 235, 218)
GREEN = (46, 74, 38)
CREAM = (243, 233, 210)
INK = (46, 58, 36)
FONT_B = 'C:/Windows/Fonts/segoeuib.ttf'
FONT_R = 'C:/Windows/Fonts/segoeui.ttf'

LANG = sys.argv[1] if len(sys.argv) > 1 else 'en'
TEXT = {
    'en': {
        'sub02': '02 / SHOWCASE SCENE', 'sub03': '03 / LOCAL COMPOSITIONS',
        'foot_l': 'UNITY DEMO SHOWROOM', 'foot_r': 'LOW-POLY COLLECTION',
        'Beds': 'BEDS', 'Crops': 'CROPS', 'Trees': 'TREES', 'Plants': 'PLANTS', 'WaterRocks': 'WATER & ROCKS', 'Modules': 'MODULES',
        'Wheat': 'WHEAT', 'Corn': 'CORN', 'Carrot': 'CARROT', 'Cabbage': 'CABBAGE', 'Tomato': 'TOMATO', 'Pumpkin': 'PUMPKIN',
        'Sunflower': 'SUNFLOWER', 'WheatField': 'WHEAT FIELD',
        'Ogorod': 'VEGETABLE GARDEN', 'Pole': 'FIELD', 'Sad': 'APPLE ORCHARD', 'Prud': 'POND & BRIDGE',
        'Opushka': 'FOREST EDGE', 'Tropa': 'FLOWER PATH',
    },
    'ru': {
        'sub02': '02 / ВЫСТАВОЧНАЯ СЦЕНА', 'sub03': '03 / ЛОКАЛЬНЫЕ КОМПОЗИЦИИ',
        'foot_l': 'UNITY DEMO SHOWROOM', 'foot_r': 'LOW-POLY COLLECTION',
        'Beds': 'ГРЯДКИ', 'Crops': 'КУЛЬТУРЫ', 'Trees': 'ДЕРЕВЬЯ', 'Plants': 'РАСТЕНИЯ', 'WaterRocks': 'ВОДА И КАМНИ', 'Modules': 'МОДУЛИ',
        'Wheat': 'ПШЕНИЦА', 'Corn': 'КУКУРУЗА', 'Carrot': 'МОРКОВЬ', 'Cabbage': 'КАПУСТА', 'Tomato': 'ТОМАТЫ', 'Pumpkin': 'ТЫКВА',
        'Sunflower': 'ПОДСОЛНУХ', 'WheatField': 'ПШЕНИЧНОЕ ПОЛЕ',
        'Ogorod': 'ОГОРОД', 'Pole': 'ПОЛЕ', 'Sad': 'ЯБЛОНЕВЫЙ САД', 'Prud': 'ПРУД И МОСТ',
        'Opushka': 'ЛЕСНАЯ ОПУШКА', 'Tropa': 'ЦВЕТОЧНАЯ ТРОПА',
    },
}[LANG]


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def spaced(draw, xy, text, fnt, fill, spacing, anchor_center=False):
    """Letter-spaced text; returns its width."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor_center:
        x -= total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing
    return total


def plaque(draw, cx, cy, text, size=24, pad=(16, 7), fill=GREEN, ink=CREAM, radius=9):
    fnt = font(size)
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt)
    w, h = r - l + 2 * pad[0], b - t + 2 * pad[1]
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    draw.text((cx, cy), text, font=fnt, fill=ink, anchor='mm')
    return box


def header_footer(img, subtitle):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 116), fill=GREEN)
    d.text((W / 2, 50), 'FARM NATURE', font=font(64), fill=CREAM, anchor='mm')
    sub_w = spaced(d, (W / 2, 82), subtitle, font(22, False), CREAM, 4, anchor_center=True)
    for side in (-1, 1):
        x0 = W / 2 + side * (sub_w / 2 + 30)
        d.line((x0, 96, x0 + side * 200, 96), fill=CREAM, width=2)
    d.rectangle((0, H - 44, W, H), fill=GREEN)
    spaced(d, (48, H - 33), TEXT['foot_l'], font(17, False), CREAM, 5)
    fr = font(17, False)
    wr = sum(d.textlength(c, font=fr) for c in TEXT['foot_r']) + 5 * (len(TEXT['foot_r']) - 1)
    spaced(d, (W - 48 - wr, H - 33), TEXT['foot_r'], fr, CREAM, 5)


def fit_into(src, w, h):
    s = min(w / src.width, h / src.height)
    return src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS), s


def grid_cells(top, bottom, cols=3, rows=2, margin=24, gap=16):
    cw = (W - 2 * margin - gap * (cols - 1)) / cols
    ch = (bottom - top - gap * (rows - 1)) / rows
    for r in range(rows):
        for c in range(cols):
            yield margin + c * (cw + gap), top + r * (ch + gap), cw, ch


def tag(draw, x, y, text):
    fnt = font(15)
    w = max(24, draw.textlength(text, font=fnt) + 12)
    draw.rounded_rectangle((x - w / 2, y - 11, x + w / 2, y + 11), radius=5, fill=CREAM, outline=(205, 190, 160))
    draw.text((x, y), text, font=fnt, fill=INK, anchor='mm')


def sheet02():
    img = Image.new('RGB', (W, H), BG)
    header_footer(img, TEXT['sub02'])
    d = ImageDraw.Draw(img)
    order = ['Beds', 'Crops', 'Trees', 'Plants', 'WaterRocks', 'Modules']
    for key, (x, y, cw, ch) in zip(order, grid_cells(132, H - 58)):
        part = Image.open(DRAFT / '_parts02' / f'Island_{key}.png').convert('RGB')
        anchors = json.loads((DRAFT / '_parts02' / f'Island_{key}.json').read_text(encoding='utf-8'))
        pic, s = fit_into(part, cw, ch)
        ox, oy = x + (cw - pic.width) / 2, y + (ch - pic.height) / 2
        img.paste(pic, (round(ox), round(oy)))

        def px(a, kx, ky):
            return ox + a[kx] * part.width * s, oy + (1 - a[ky]) * part.height * s

        if key == 'Crops':
            rows = {}
            for a in anchors:
                crop = a['name'].split('_')[1]
                rows.setdefault(crop, []).append(a)
            last = None
            for crop, items in rows.items():
                lx, ly = px(min(items, key=lambda a: a['lx']), 'lx', 'ly')
                plaque(d, lx - 62, ly - 8, TEXT[crop], size=12, pad=(8, 3), fill=CREAM, ink=INK, radius=4)
                last = items
            for i, a in enumerate(last):
                fx, fy = px(a, 'fx', 'fy')
                tag(d, fx, fy + 16, str(i + 1))
        else:
            for a in anchors:
                fx, fy = px(a, 'fx', 'fy')
                tag(d, fx, fy + 14, str(a['num']))
        plaque(d, x + 16 + d.textlength(TEXT[key], font=font(24)) / 2 + 16, y + 26, TEXT[key])
    out = DRAFT / '02_Showcase_Scene.png'
    img.save(out)
    return out


def sheet03():
    img = Image.new('RGB', (W, H), BG)
    header_footer(img, TEXT['sub03'])
    d = ImageDraw.Draw(img)
    order = ['Ogorod', 'Pole', 'Sad', 'Prud', 'Opushka', 'Tropa']
    for i, (key, (x, y, cw, ch)) in enumerate(zip(order, grid_cells(132, H - 58))):
        part = Image.open(DRAFT / '_parts03' / f'{key}.png').convert('RGB')
        pic, s = fit_into(part, cw, ch - 46)
        img.paste(pic, (round(x + (cw - pic.width) / 2), round(y + (ch - 46 - pic.height) / 2)))
        plaque(d, x + 34, y + 22, f'{i + 1:02d}', size=20, pad=(10, 4))
        plaque(d, x + cw / 2, y + ch - 22, TEXT[key], size=22)
    if True:  # thin dividers like the reference sheet
        for x in (W / 3, 2 * W / 3):
            d.line((x, 140, x, H - 66), fill=(225, 212, 188), width=2)
        d.line((40, (132 + H - 58) / 2, W - 40, (132 + H - 58) / 2), fill=(225, 212, 188), width=2)
    out = DRAFT / '03_Local_Compositions.png'
    img.save(out)
    return out


if __name__ == '__main__':
    print(sheet02())
    print(sheet03())
