"""Compose store media from the accepted RGB Unity renders. Requires Pillow."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

LAYOUT = Path(__file__).resolve().parent
PACK = LAYOUT.parents[1]
RAW = PACK / "Media" / "raw"
DARK, RED, CREAM = "#20242A", "#C8473B", "#F2E6C9"
PAPER, PANEL = "#E9E9EC", "#F6F6F7"
GALLERY = (1920, 1080)
Box = tuple[int, int, int, int]


def literals(line):
    return re.findall(r"\x60([^\x60]*)\x60", line)


class Copy:
    def __init__(self, edition):
        product = (PACK / edition / "PACKAGE_METADATA.md").read_text(encoding="utf-8-sig")
        media = re.search(r"(?ms)^## Media\s*\n(.*?)(?=^## |\Z)", product).group(1)
        self.slots = {}
        self.captions = {}
        for line in media.splitlines():
            if row := re.match(r"^\|\s*(\d{2}_\w+)\s*\|([^|]*\|){2}\s*([^|]*)\|", line):
                self.slots[row[1]] = tuple(literals(row[3]))
        for section in re.split(r"(?m)^\*\*(?=\d{2}_)", media)[1:]:
            name, body = section.split("**", 1)
            body = re.sub(r"(?m)^Comparison panel .*?$", "", body)
            self.captions[name] = tuple(literals(body))
        if len(self.slots) != (10 if edition == "Lite" else 14):
            raise ValueError(f"Incomplete Media table for {edition}")


@lru_cache(maxsize=48)
def font(size, weight):
    face = ImageFont.truetype(str(LAYOUT / "fonts" / "Montserrat.ttf"), size)
    face.set_variation_by_axes([weight])
    return face


def dims(box):
    return box[2] - box[0], box[3] - box[1]


def text(draw, value, box, size, weight=700, fill=DARK, align="left"):
    width, height = dims(box)
    for pt in range(size, 7, -1):
        face = font(pt, weight)
        left, top, right, bottom = face.getbbox(value)
        if right-left <= width and bottom-top <= height:
            break
    else:
        raise ValueError(f"Text does not fit: {value}")
    x = box[0] - left
    if align == "center":
        x += (width - (right - left)) // 2
    y = box[1] + (height - (bottom - top)) // 2 - top
    draw.text((x, y), value, font=face, fill=fill)


def wrapped(draw, value, box, size, weight=650, fill=DARK):
    width, height = dims(box)
    face = font(size, weight)
    line_height = round(size * 1.38)
    lines = []
    line = ""
    for word in value.split(" "):
        next_line = f"{line} {word}".strip()
        if line and face.getlength(next_line) > width:
            lines.append(line)
            line = word
        else:
            line = next_line
    lines.append(line)
    if line_height * len(lines) > height:
        raise ValueError(f"Paragraph does not fit: {value}")
    for i, line in enumerate(lines):
        y = box[1] + line_height * i
        text(draw, line, (box[0], y, box[2], y + line_height), size, weight, fill)


@dataclass(frozen=True)
class Render:
    source: str
    crop: Box | None
    size: tuple[int, int]
    at: tuple[int, int]
    nearest: bool = False

    @property
    def path(self):
        folder = LAYOUT / "icons" if self.source.startswith("generated/") else RAW
        name = self.source.removeprefix("generated/")
        return folder / f"{name}.png"

    def pixels(self):
        with Image.open(self.path) as raw:
            image = raw.convert("RGB")
        if self.crop:
            image = image.crop(self.crop)
        if image.size != self.size:
            filter_ = Image.Resampling.NEAREST if self.nearest else Image.Resampling.LANCZOS
            image = image.resize(self.size, filter_)
        return image


class Frame:
    def __init__(self, size=GALLERY, background=PAPER):
        self.image = Image.new("RGB", size, background)
        self.draw = ImageDraw.Draw(self.image)
        self.renders = []
        self.overlays = []
        self.overlay_mask = Image.new("L", size)
        self.mask_draw = ImageDraw.Draw(self.overlay_mask)

    def add(self, source, box, crop=None, nearest=False):
        with Image.open(Render(source, None, (0, 0), (0, 0)).path) as image:
            origin = image.size
        if crop and not (0 <= crop[0] < crop[2] <= origin[0] and 0 <= crop[1] < crop[3] <= origin[1]):
            raise ValueError(f"Invalid crop {crop} for {source}")
        ow, oh = dims(crop) if crop else origin
        width, height = dims(box)
        factor = min(width/ow, height/oh)
        size = round(ow*factor), round(oh*factor)
        at = box[0] + (width-size[0])//2, box[1] + (height-size[1])//2
        render = Render(source, crop, size, at, nearest)
        self.image.paste(render.pixels(), at)
        self.renders.append(render)
        return at, size

    def rect(self, box, fill, overlay=False):
        self.draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=fill)
        if overlay:
            self.mask_draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=255)
            self.overlays.append(str(box))

    def corner(self, extent):
        triangle = ((0, 0), (extent-1, 0), (0, extent-1))
        self.draw.polygon(triangle, fill=RED)
        self.mask_draw.polygon(triangle, fill=255)
        self.overlays.append(f"triangle {triangle}")

    def label(self, value, box, size=25, **kwargs):
        text(self.draw, value, box, size, **kwargs)

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        scratch = path.with_suffix(".pending.png")
        self.image.save(scratch, compress_level=6)
        descriptions = []
        with Image.open(scratch) as saved:
            if saved.mode != "RGB" or saved.size != self.image.size:
                raise ValueError(f"Invalid output: {path.name}")
            for render in self.renders:
                expected = render.pixels()
                x, y = render.at
                w, h = render.size
                diff = ImageChops.difference(expected, saved.crop((x, y, x+w, y+h)))
                diff.paste((0, 0, 0), (0, 0, w, h), self.overlay_mask.crop((x, y, x+w, y+h)))
                if diff.getbbox():
                    raise ValueError(f"Render pixels changed outside plates: {path.name} / {render.source}")
                crop = f", crop {render.crop}" if render.crop else ""
                with Image.open(render.path) as source:
                    input_size = dims(render.crop) if render.crop else source.size
                method = "native pixels" if input_size == render.size else ("nearest" if render.nearest else "Lanczos")
                descriptions.append(f"{render.source}{crop} → {w}×{h} @ ({x},{y}), {method}")
        scratch.replace(path)
        masks = ", ".join(self.overlays) if self.overlays else "—"
        return f"| {path.parent.parent.parent.name}/{path.name} | {'<br>'.join(descriptions)} | {masks} | 0 |"


def direct(source, size):
    frame = Frame(size)
    frame.add(source, (0, 0, *size))
    return frame


def badge(frame, value):
    w, h = frame.image.size
    left = round(w*.027)
    top = round(h*.04)
    width = round(w*.108)
    height = round(h*.069)
    rect = left, top, left+width, top+height
    frame.rect(rect, RED, overlay=True)
    frame.label(value, (left+1, top, left+width-1, top+height), round(height*.72),
                weight=900, fill=CREAM, align="center")


def title_page(source, size, copy, card, full_corner):
    frame = direct(source, size)
    w, h = size
    top = round(h*(.634 if card else .78))
    strip = round(h*(.91 if card else .939))
    frame.rect((0, top, w, h), DARK, overlay=True)
    frame.rect((0, strip, w, h), RED)
    headline = round(w*.053)
    width = w - round(w*.047)
    badge_text, title, accent = copy if len(copy) == 3 else (None, *copy)
    frame.label(title, (headline, top+3, width, strip-3), round(h*(.13 if card else .102)),
                weight=900, fill=CREAM)
    frame.label(accent, (headline, strip+2, width, h-2), round(h*(.047 if card else .031)),
                weight=800, fill=CREAM)
    if full_corner:
        extent = round(h*.182)
        frame.corner(extent)
        frame.label(badge_text or full_corner, (round(extent*.11), round(extent*.09),
                                                round(extent*.55), round(extent*.44)), round(extent*.30),
                    weight=900, fill="#FFFFFF")
    elif badge_text:
        badge(frame, badge_text)
    return frame


def gallery_plate(frame, copy, hero=False):
    title, theme = copy
    size = 30
    width = max(font(size, 850).getlength(title), font(23, 650).getlength(theme))
    w = int(width) + 42
    if hero:
        # The raw Lite front wheel starts to the right of x=358; preserve it.
        w = min(w, 312)
    frame.rect((28, 954, 28+w, 1058), DARK, overlay=hero)
    frame.label(title, (48, 966, 8+w, 1008), size, weight=900, fill=CREAM)
    frame.label(theme, (48, 1007, 8+w, 1046), 23, weight=650, fill=CREAM)


def legend(frame, values, y, x=48, right=1872, size=23):
    for i, value in enumerate(values):
        frame.label(value, (x, y+i*30, right, y+i*30+28), size)


def caption_tile(frame, source, label, box, crop=None):
    x, y, r, b = box
    frame.rect(box, PANEL)
    frame.add(source, (x+4, y+4, r-4, b-38), crop)
    frame.label(label, (x+12, b-34, r-12, b-5), 22, weight=800)


def five_tiles(frame, sources, captions):
    left, gap, right = 40, 16, 1880
    for start, count, y, bottom in ((0, 2, 26, 507), (2, 3, 522, 905)):
        w = (right-left-gap*(count-1))//count
        for i in range(count):
            x = left + i*(w+gap)
            caption_tile(frame, sources[start+i], captions[start+i], (x, y, x+w, bottom))


LITE_CLOSE = (
    "Demo_FieldWork_CloseCMP01", "Demo_FieldWork_LowNode_Plough",
    "Closeup_Lite_RearLinkage", "Closeup_Lite_Sprayer", "Closeup_Lite_Tipper",
)
FULL_CLOSE = (
    "Demo_Harvest_LowNode_Header", "Demo_Harvest_CloseHaymaking",
    "Demo_Harvest_CloseGrainYard", "Demo_FieldWork_LowNode_Plough", "Demo_FieldWork_CloseCMP01",
)


def variations(frame, labels, lite):
    suffix = "_Lite" if lite else ""
    frame.label(labels[2], (44, 26, 1174, 72), 25, weight=800)
    # Crop the separated parts by row. The assembled vignettes overlap in
    # height, so keep that column together to preserve the complete models.
    row_crops = (
        ((145, 239, 465, 399), (620, 255, 1220, 397)),
        ((175, 392, 434, 584), (620, 450, 752, 572)),
        ((120, 578, 415, 845), (535, 576, 848, 848)),
    ) if lite else (
        ((199, 185, 485, 422), (596, 265, 1225, 422)),
        ((203, 438, 383, 606), (629, 456, 1044, 609)),
        ((116, 622, 413, 880), (555, 626, 854, 880)),
    )
    modularity = "Catalog/08_Modularity"+suffix
    for i, row in enumerate(row_crops):
        y = 81+i*281
        frame.rect((40, y, 759, y+265), PANEL)
        for crop, (x1, x2) in zip(row, ((50, 310), (317, 749))):
            frame.add(modularity, (x1, y+8, x2, y+257), crop)
    frame.rect((775, 81, 1176, 908), PANEL)
    assembled = (1410, 222, 1840, 870) if lite else (1352, 170, 1840, 910)
    frame.add(modularity, (785, 89, 1166, 900), assembled)
    sources = ("08_ColourVariants", "08_Poses", "08_AttachPoints")
    colours = (122, 190, 1839, 945) if lite else (410, 50, 1515, 1040)
    crops = (colours, (116, 142, 1825, 929),
             (265, 135, 1762, 957))
    for i, (source, label, crop) in enumerate(zip(sources, (labels[0],labels[1],labels[3]), crops)):
        y = 26+i*291
        caption_tile(frame, "Catalog/"+source+suffix, label, (1196, y, 1878, y+278), crop)
    frame.label(labels[4], (1200, 902, 1873, 932), 20, weight=550)


def technical(frame, words, lite, heads):
    source = "Catalog/09_Technical" + ("_Lite" if lite else "")
    # Model sheet and captions have independent regions.
    bounds = (80, 112, 1828, 1030) if lite else (80, 45, 1828, 1042)
    frame.add(source, (34, 105, 1330, 903), bounds)
    for label, x in zip(heads, (38, 470, 900)):
        frame.label(label, (x, 47, x+405, 91), 28, weight=900, align="center")
    frame.rect((1348, 105, 1881, 903), PANEL)
    for i, value in enumerate(words[:-1]):
        y = 183 + i * (292 if lite else 222)
        frame.rect((1376, y, 1854, y+117), PAPER)
        wrapped(frame.draw, value, (1400, y+19, 1830, y+102), 25, 750)
    frame.label(words[-1], (48, 912, 1872, 944), 22, weight=800)


def demo_panel(frame, labels, lite):
    scene = "Demo_FieldWork_Overview" if lite else "Demo_Harvest_Overview"
    frame.add(scene, (40, 64, 1228, 863))
    frame.rect((1254, 64, 1880, 916), DARK)
    sections = (labels[:6], labels[6:-1]) if lite else (labels[:4], labels[4:-1])
    y = 106
    for i, (heading, *items) in enumerate(sections):
        frame.label(heading, (1282, y, 1852, y+47), 31, weight=900, fill=CREAM)
        frame.rect((1282, y+52, 1852, y+55), RED)
        y += 72
        for value in items:
            longest = len(value) > 96
            height = 135 if longest else (67 if len(value)>39 else 38)
            wrapped(frame.draw, value, (1282,y,1852,y+height), 23 if longest else 24,
                    700, CREAM)
            y += height + 6
        if i==0:
            y += 24
    frame.label(labels[-1], (40, 865, 1228, 907), 23, weight=550)


def categories(frame, labels):
    harvest = "Catalog/11_Category_Harvest"
    machines = "Catalog/06a_Machines"
    # The wider catalogue sheets separate these silhouettes from their neighbours.
    tiles = (
        (harvest, (389, 101, 766, 418)),
        ("Catalog/06_FullCollection_Full", (528, 126, 688, 316)),
        (machines, (680, 770, 853, 944)),
        (harvest, (1384, 190, 1610, 383)),
        (machines, (323, 106, 551, 312)),
        (machines, (1015, 103, 1218, 296)),
        (harvest, (134, 776, 566, 1034)),
        (harvest, (662, 776, 1080, 1034)),
        (harvest, (1177, 797, 1486, 1004)),
        (harvest, (1577, 831, 1797, 1014)),
    )
    rack = ((0,4,34,346),(4,2,353,638),(6,4,645,934))
    for first,count,y,bottom in rack:
        gap = 15
        w = (1840-gap*(count-1))//count
        for i in range(count):
            x=40+i*(w+gap)
            source, crop = tiles[first+i]
            caption_tile(frame, source, labels[first+i], (x,y,x+w,bottom), crop)


def materials(frame, words):
    frame.add("Catalog/13_Materials_Models", (35, 137, 1198, 883), (100, 164, 1193, 911))
    frame.label(words[4], (48, 82, 1192, 125), 27, weight=900)
    for i, name in enumerate(words[:3]):
        y = 46+i*277
        frame.rect((1220, y, 1880, y+260), PANEL)
        frame.add(f"Catalog/13_Atlas_{name.title()}", (1254, y+13, 1490, y+247), nearest=True)
        frame.label(name, (1519,y+18,1848,y+241), 37, weight=900)
    frame.label(words[3], (48, 910, 1872, 943), 25, weight=800)


def unity_panel(frame, words):
    frame.add("Catalog/14_Unity_Full", (36, 46, 1244, 796))
    for i, word in enumerate(words[:4]):
        x=48+(i%2)*597
        y=790+(i//2)*57
        frame.rect((x,y,x+578,y+46), PANEL)
        frame.label(word, (x+14,y+4,x+567,y+42), 21, weight=800)
    title, *cells = words[4:]
    frame.rect((1260, 46, 1880, 924), DARK)
    frame.label(title, (1285,79,1855,137), 37, weight=900, fill=CREAM)
    frame.rect((1285,146,1855,150), RED)
    for i in range(0,len(cells),3):
        y=183+(i//3)*92
        for col, value in enumerate(cells[i:i+3]):
            x,r=((1286,1663),(1673,1743),(1760,1854))[col]
            frame.label(value,(x,y,r,y+59),24 if col else 21,
                        weight=800 if col else 750,fill=CREAM,align="center" if col else "left")
        frame.rect((1286,y+70,1854,y+72),"#41474F")


def builds(edition, copy, include_icons=True):
    lite = edition == "Lite"
    suffix = "_Lite" if lite else ""
    if include_icons:
        for side, name in ((160, "01_Icon"), (1024, "01_Icon_1024"), (60, "01_Icon_60_check")):
            yield name, direct(f"generated/Icon_{edition}", (side, side))
    full_corner = None if lite else copy.slots["01_Icon"][0]
    for size, name in (((420,280),"02_Card"),((1260,840),"02_Card_1260x840")):
        yield name, title_page(f"Card_{edition}", size, copy.slots["02_Card"], card=True, full_corner=full_corner)
    yield "03_Cover", title_page(f"Cover_{edition}", (1950,1300), copy.slots["03_Cover"], card=False,
                                 full_corner=full_corner)
    yield "04_Social", direct(f"Social_{edition}", (1200,630))

    for slot, plate in copy.slots.items():
        if int(slot[:2]) < 5:
            continue
        captions = copy.captions.get(slot, ())
        if slot == "05_Hero":
            frame = direct(f"Hero_{edition}", GALLERY)
            gallery_plate(frame, plate, hero=True)
            yield slot, frame
            continue
        frame = Frame()
        if slot == "06_FullCollection":
            frame.add(f"Catalog/06_FullCollection_{edition}", (28,12,1892,876), (10,38,1910,1024))
            legend(frame, captions, 882)
        elif slot == "07_Closeups":
            five_tiles(frame, LITE_CLOSE if lite else FULL_CLOSE, captions[:5])
            if not lite:
                frame.label(captions[5], (48, 911, 1872, 941), 20, weight=550)
        elif slot == "08_VariantsAndModules":
            variations(frame, captions, lite)
        elif slot == "09_Technical":
            technical(frame, captions[3:], lite, captions[:3])
        elif slot == "10_DemoAndVersion":
            demo_panel(frame, captions, lite)
        elif slot == "11_CategoryDetails":
            categories(frame, captions)
        elif slot == "12_Compositions":
            five_tiles(frame, [f"Catalog/12_CMP_{i:02}" for i in range(1,6)], captions[:5])
            frame.label(captions[5], (48, 910, 1872, 942), 20, weight=550)
        elif slot == "13_Materials":
            materials(frame, captions)
        elif slot == "14_UnityAndComparison":
            unity_panel(frame, captions)
        else:
            raise ValueError(f"Unmapped slot {slot}")
        gallery_plate(frame, plate)
        yield slot, frame


def main():
    media = {edition: Copy(edition) for edition in ("Lite", "Full")}
    rows = []
    for edition, copy in media.items():
        for name, frame in builds(edition, copy):
            output = PACK / edition / "Media" / "final" / (name + ".png")
            rows.append(frame.save(output))
            print(f"{edition}/{name}.png  {frame.image.width}x{frame.image.height}")
    report = [
        "# FarmMachinery — Э12: проверка PNG",
        "",
        "Тексты взяты из Media обеих карточек PACKAGE_METADATA.md. "
        "Скрипт проверяет повторно открытый RGB PNG и публикует файл после проверки.",
        "",
        "- Для нативных кадров ожидается побитовое совпадение декодированных RGB-пикселей с Unity-исходником вне указанных прямоугольников оформления.",
        "- Для карточек 420 px и составных кадров эталон — явно указанные кадрирование и/или масштабирование исходника. "
        "Каждая вставка совпадает с этим эталоном, вне плашек нет цветокоррекции или дорисовки.",
        "- Иконки — разрешённое исключение: ImageGen по Unity-рендерам, с уголком 3D. "
        "Их эталон — выбранное изображение из layout/icons, масштабированное к размеру файла. Проверка на совпадение иконки с raw не применяется.",
        "",
        "| Файл | Эталонные регионы | Допустимая перекрывающая графика (координаты в пикселях) | Разница RGB |",
        "|---|---|---|---:|",
        *rows,
        "",
    ]
    (LAYOUT / "CHECKS.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()

