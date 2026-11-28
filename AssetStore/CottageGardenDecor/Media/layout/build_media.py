"""Build opaque store PNGs from the Unity renders. Requires Python 3.10+ and Pillow."""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re

from PIL import Image, ImageChops, ImageDraw, ImageFont

LAYOUT = Path(__file__).resolve().parent
MEDIA = LAYOUT.parent
PACK = MEDIA.parent
ROOT = PACK.parents[1]
RAW = MEDIA / "raw"
CHECKS = ROOT / ".work/pipeline/CottageGardenDecor/media_checks"
TEXTURES = ROOT / "Assets/CottageGardenDecor/Art/Textures"
DARK, RED, CREAM = "#20242A", "#C8473B", "#F2E6C9"
PAPER, PANEL, WHITE = "#E9E9EC", "#F6F6F7", "#FFFFFF"
GALLERY = (1920, 1080)
Box = tuple[int, int, int, int]


def literals(line):
    return re.findall(r"\x60([^\x60]*)\x60", line)


class Copy:
    def __init__(self):
        product = (PACK / "PACKAGE_METADATA.md").read_text(encoding="utf-8-sig")
        media = re.search(r"(?ms)^## Media\s*\n(.*?)(?=^## |\Z)", product).group(1)
        self.slots = {}
        self.captions = {}
        self.sizes = {}
        for line in media.splitlines():
            row = re.match(r"^\|\s*(\d{2}b?_\w+)\s*\|([^|]+)\|[^|]*\|([^|]*)\|", line)
            if row:
                name, size, plate = row.groups()
                self.sizes[name] = tuple(map(int, re.search(r"(\d+)×(\d+)", size).groups()))
                self.slots[name] = literals(plate)
        for section in re.split(r"(?m)^\*\*(?=\d{2}b?_)", media)[1:]:
            name, body = section.split("**", 1)
            if name == "14_UnityAndComparison":
                # The heading names the selected prefab; the list carries the callout copy.
                body = body.partition("\n")[2]
            self.captions[name] = [value for value in literals(body)
                                   if not value.endswith((".json", ".md"))]
        order = next(line for line in media.splitlines() if line.startswith("Gallery upload order"))
        self.gallery = [next(name for name in self.slots if name.startswith(slot + "_"))
                        for slot in re.findall(r"\b\d{2}b?\b", order.split(": ", 1)[1])]
        if len(self.slots) != 15:
            raise ValueError("Incomplete Media table")


@lru_cache(maxsize=96)
def font(size, weight):
    face = ImageFont.truetype(str(LAYOUT / "fonts/Montserrat.ttf"), size)
    face.set_variation_by_axes([weight])
    return face


def dims(box):
    return box[2] - box[0], box[3] - box[1]


def text(draw, value, box, size, weight=700, fill=DARK, align="left"):
    width, height = dims(box)
    for pt in range(size, 7, -1):
        face = font(pt, weight)
        left, top, right, bottom = face.getbbox(value)
        if right - left <= width and bottom - top <= height:
            break
    else:
        raise ValueError(f"Text does not fit: {value}")
    x = box[0] - left
    if align == "center":
        x += (width - (right - left)) // 2
    y = box[1] + (height - (bottom - top)) // 2 - top
    draw.text((x, y), value, font=face, fill=fill)


def wrapped(frame, value, box, size, weight=650, fill=DARK):
    width, height = dims(box)
    face = font(size, weight)
    lines = [""]
    nbsp = "\N{NO-BREAK SPACE}"
    nonbreaking = re.sub(r"\b(\d+) (?=[A-Z])", r"\1" + nbsp, value)
    for word in nonbreaking.split(" "):
        candidate = f"{lines[-1]} {word}".strip()
        if lines[-1] and face.getlength(candidate) > width:
            lines.append(word)
        else:
            lines[-1] = candidate
    leading = round(size * 1.35)
    if leading * len(lines) > height:
        raise ValueError(f"Paragraph does not fit: {value}")
    for i, line in enumerate(lines):
        y = box[1] + i * leading
        frame.label(line.replace(nbsp, " "), (box[0], y, box[2], y + leading),
                    size, weight=weight, fill=fill)


@lru_cache(maxsize=4)
def pixels(path):
    with Image.open(path) as source:
        return source.convert("RGB")


@dataclass(frozen=True)
class Render:
    path: Path
    crop: Box
    size: tuple[int, int]
    at: tuple[int, int]
    nearest: bool = False

    @property
    def sampling(self):
        if dims(self.crop) == self.size:
            return "native"
        return "NEAREST" if self.nearest else "Lanczos"

    def pixels(self):
        image = pixels(self.path).crop(self.crop)
        if image.size != self.size:
            filter_ = Image.Resampling.NEAREST if self.nearest else Image.Resampling.LANCZOS
            image = image.resize(self.size, filter_)
        return image

    def project(self, rect):
        x, y, w, h = rect
        ow, oh = dims(self.crop)
        sx, sy = self.size[0] / ow, self.size[1] / oh
        ax, ay = self.at
        l, t = self.crop[:2]
        return (round(ax + (x - l) * sx), round(ay + (y - t) * sy),
                round(ax + (x + w - l) * sx), round(ay + (y + h - t) * sy))


class Frame:
    def __init__(self, size=GALLERY, background=PAPER):
        self.image = Image.new("RGB", size, background)
        self.draw = ImageDraw.Draw(self.image)
        self.renders = []
        self.overlay_mask = Image.new("L", size)
        self.mask_draw = ImageDraw.Draw(self.overlay_mask)

    def add(self, source, box, crop=None, nearest=False, feather=0):
        path = (TEXTURES if nearest else RAW) / f"{source}.png"
        origin = pixels(path).size
        crop = crop or (0, 0, *origin)
        if not (0 <= crop[0] < crop[2] <= origin[0] and 0 <= crop[1] < crop[3] <= origin[1]):
            raise ValueError(f"Invalid crop {crop} for {source}")
        ow, oh = dims(crop)
        width, height = dims(box)
        factor = min(width / ow, height / oh)
        size = round(ow * factor), round(oh * factor)
        at = box[0] + (width - size[0]) // 2, box[1] + (height - size[1]) // 2
        render = Render(path, crop, size, at, nearest)
        mask = None
        if feather:
            mask = Image.new("L", size)
            edge = ImageDraw.Draw(mask)
            for i in range(1, feather + 1):
                edge.rectangle((i, i, size[0] - i - 1, size[1] - i - 1),
                               fill=round(255 * i / feather))
            self.overlay_mask.paste(255, (at[0], at[1], at[0] + size[0], at[1] + size[1]),
                                    mask.point(lambda alpha: 255 if alpha < 255 else 0))
        self.image.paste(render.pixels(), at, mask)
        self.renders.append(render)
        return render

    def rect(self, box, fill, overlay=False):
        bounds = (box[0], box[1], box[2] - 1, box[3] - 1)
        self.draw.rectangle(bounds, fill=fill)
        if overlay:
            self.mask_draw.rectangle(bounds, fill=255)

    def label(self, value, box, size=25, overlay=False, **kwargs):
        text(self.draw, value, box, size, **kwargs)
        if overlay:
            self.mask_draw.rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=255)

    def corner(self, value, extent):
        triangle = ((0, 0), (extent - 1, 0), (0, extent - 1))
        self.draw.polygon(triangle, fill=RED)
        self.mask_draw.polygon(triangle, fill=255)
        self.label(value, (round(extent * .10), round(extent * .08),
                          round(extent * .57), round(extent * .42)),
                   round(extent * .31), weight=900, fill=WHITE)

    def save(self, path, size):
        path.parent.mkdir(parents=True, exist_ok=True)
        scratch = path.with_suffix(".pending.png")
        try:
            self.image.save(scratch, optimize=True)
            with Image.open(scratch) as saved:
                if saved.format != "PNG" or saved.mode != "RGB" or saved.size != size:
                    raise ValueError(f"Invalid export: {path}")
                for render in self.renders:
                    x, y = render.at
                    w, h = render.size
                    box = x, y, x + w, y + h
                    diff = ImageChops.difference(render.pixels(), saved.crop(box))
                    diff.paste((0, 0, 0), (0, 0, w, h), self.overlay_mask.crop(box))
                    if diff.getbbox():
                        raise ValueError(f"Render pixels changed outside graphics: {path.name} / {render.path.name}")
            scratch.replace(path)
        finally:
            scratch.unlink(missing_ok=True)


def title_page(source, size, copy, card):
    w, h = size
    # At 65% the Card ends below the beds. Cover retains the original frame.
    top = round(h * (.65 if card else .78))
    strip = round(h * (.88 if card else .925))
    badge, title, accent = copy
    frame = Frame(size)
    if card:
        frame.add(source, (0, 0, w, top), (0, 0, 1260, 546))
    else:
        frame.add(source, (0, 0, w, h))
    frame.rect((0, top, w, h), DARK, overlay=True)
    frame.rect((0, strip, w, h), RED)
    # Same relative inset on Card and Cover, reserved for the series mark.
    left, right = round(w * .12), round(w * .965)
    frame.label(title, (left, top + 3, right, strip - 3), round(h * (.115 if card else .091)),
                weight=900, fill=CREAM)
    frame.label(accent, (left, strip + 2, right, h - 2), round(h * (.054 if card else .031)),
                weight=800, fill=WHITE)
    frame.corner(badge, round(h * .182))
    return frame


def gallery_plate(frame, copy):
    title, theme = copy
    w = round(max(font(26, 900).getlength(title), font(22, 650).getlength(theme))) + 40
    frame.rect((28, 954, 28 + w, 1058), DARK, overlay=True)
    frame.label(title, (48, 965, 8 + w, 1007), 26, weight=900, fill=CREAM)
    frame.label(theme, (48, 1007, 8 + w, 1046), 22, weight=650, fill=CREAM)


def item_label(frame, value, rect, size=22, width=340, offset=3, x_offset=0):
    x = (rect[0] + rect[2]) // 2 + x_offset
    y = rect[3] + offset
    frame.label(value, (x - width // 2, y, x + width // 2, y + size + 7), size,
                weight=650, align="center", overlay=True)


def label_map(source):
    data = json.loads((RAW / f"{source}_labels.json").read_text(encoding="utf-8-sig"))
    return {item["id"]: item["rect"] for item in data["items"]}, data["categories"]


def union(items, ids):
    rects = [items[key] for key in ids]
    l = min(x for x, y, w, h in rects)
    t = min(y for x, y, w, h in rects)
    r = max(x + w for x, y, w, h in rects)
    b = max(y + h for x, y, w, h in rects)
    return l, t, r - l, b - t


def full_collection(frame, words):
    source = "06_FullCollection"
    render = frame.add(source, (0, 0, *GALLERY))
    _, categories = label_map(source)
    ids = ("STR", "WTR", "FUR", "FLB", "PLT", "MOD", "ORN", "TOP")
    # The water and furniture overlap the structures' union vertically.
    for key, value in zip(ids, words[:8], strict=True):
        rect = render.project(categories[key])
        if key == "STR":
            y = (rect[1] + rect[3]) // 2
            frame.label(value, (62, y - 18, rect[0] - 58, y + 18), 23, weight=800, overlay=True)
            frame.rect((255, y, rect[0] - 20, y + 2), RED, overlay=True)
        elif key == "MOD":
            frame.label(value, (rect[2] + 22, rect[3] - 31, 1882, rect[3] - 2), 22, overlay=True)
        else:
            item_label(frame, value, rect, offset=2)
    frame.label(words[8], (615, 1033, 1588, 1065), 16, overlay=True)
    frame.label(words[9], (1607, 1033, 1901, 1065), 15, overlay=True)


def collection_details(frame, words):
    source = "06_FullCollection_2"
    render = frame.add(source, (220, 18, 1884, 936), (150, 34, 1820, 1010), feather=22)
    items, categories = label_map(source)
    for key, value in zip(("PLT", "TOP", "ORN"), words[:3], strict=True):
        _, top, _, _ = render.project(categories[key])
        frame.rect((34, top + 2, 205, top + 48), PANEL)
        frame.label(value, (43, top + 2, 196, top + 48), 21, weight=850)
    ids = [f"{key}-{i:02}" for key, count in (("PLT", 6), ("TOP", 4), ("ORN", 5))
           for i in range(1, count + 1)]
    for key, value in zip(ids, words[3:], strict=True):
        item_label(frame, value, render.project(items[key]), size=20, width=230, offset=1,
                   x_offset=64 if key == "PLT-04" else 0)


def caption_tile(frame, source, label, box, crop, size=22):
    x, y, r, b = box
    frame.rect(box, PANEL)
    frame.add(source, (x + 4, y + 4, r - 4, b - 36), crop)
    frame.label(label, (x + 11, b - 33, r - 11, b - 4), size, weight=800)


def closeups(frame, words):
    # Main arch detail at left, four closer views in a two-by-two rack.
    views = (
        (1, (30, 22, 786, 905), (510, 38, 1230, 842)),
        (4, (802, 22, 1338, 456), (399, 36, 1480, 822)),
        (2, (1354, 22, 1890, 456), (323, 56, 1568, 834)),
        (5, (802, 471, 1338, 905), (418, 114, 1622, 866)),
        (6, (1354, 471, 1890, 905), (686, 343, 1586, 929)),
    )
    for (i, box, crop), value in zip(views, words[:5], strict=True):
        caption_tile(frame, f"CMP-{i:02}", value, box, crop, 21)
    frame.label(words[5], (38, 909, 1882, 944), 21, weight=600)


def variants(frame, words):
    frame.label(words[13], (44, 20, 1170, 70), 32, weight=900)
    frame.label(words[19], (1202, 20, 1886, 70), 32, weight=900)
    frame.rect((44, 74, 1170, 78), RED)
    frame.rect((1202, 74, 1886, 78), RED)
    panels = (
        ("08_Variants_A", (30, 86, 1176, 578), (38, 134, 1872, 920), words[:6], (
            ("STR-01", "STR-01_White", "STR-01_Gate"),
            ("STR-07", "STR-07_White"),
            tuple(f"FLB-{i:02}{suffix}" for i in range(1, 4) for suffix in ("", "_Planted")),
            ("PLT-02", "PLT-02_Pink"),
            ("PLT-06", "PLT-06_White"),
            ("FUR-05", "FUR-05_Blue"),
        )),
        ("08_Variants_B", (30, 587, 1176, 935), (38, 264, 1872, 820), words[6:13], (
            ("PLT-01", "PLT-01_Pink", "PLT-01_White"),
            ("PLT-03", "PLT-03_Pink"),
            ("TOP-01", "TOP-01_Rose"),
            ("ORN-03", "ORN-03_Planted"),
            ("ORN-05", "ORN-05_Feeder"),
            ("ORN-02", "ORN-02_Blue"),
            ("FUR-03", "FUR-03_White", "FUR-04", "FUR-04_White"),
        )),
    )
    nudges = {
        "08_Variants_A": {1: (26, 0), 2: (289, -8), 3: (-12, 0), 4: (13, 4), 5: (27, 0)},
        "08_Variants_B": {2: (-33, 0), 3: (8, 3), 4: (-10, 17)},
    }
    for source, box, crop, values, groups in panels:
        frame.rect(box, PANEL)
        render = frame.add(source, box, crop)
        items, _ = label_map(source)
        for i, (value, keys) in enumerate(zip(values, groups, strict=True)):
            rect = render.project(union(items, keys))
            size = 17
            width = round(font(size, 650).getlength(value)) + 10
            left, _, right, _ = box
            shift, offset = nudges[source].get(i, (0, 0))
            center = (rect[0] + rect[2]) // 2 + shift
            if source.endswith("_B") and i == 4:
                # The hooks abut the right edge of the sheet.
                size, width = 15, 241
            center = max(left + width // 2 + 20, min(right - width // 2 - 20, center))
            item_label(frame, value, rect, size=size, width=width, offset=offset,
                       x_offset=center - (rect[0] + rect[2]) // 2)

    frame.rect((1193, 149, 1890, 752), PANEL)
    render = frame.add("Modules", (1193, 234, 1890, 700), (188, 42, 1749, 1027))
    tags = (
        (440, 639, 183), (817, 876, 235), (1440, 1068, 242),
        (555, -47, 213), (1364, -59, 190),
    )
    for value, (x, y, width) in zip(words[14:19], tags, strict=True):
        px, py, _, _ = render.project((x, y, 0, 0))
        box = px - width // 2, py, px + width // 2, py + 31
        frame.rect(box, DARK, overlay=True)
        frame.label(value, (box[0] + 6, py, box[2] - 6, py + 31), 18,
                    weight=700, align="center", fill=CREAM)


def technical(frame, words):
    source = "09_Technical"
    render = frame.add(source, (36, 18, 1884, 837), (341, 62, 1690, 954), feather=20)
    items, categories = label_map(source)
    rects = [items["STR-06"], items["STR-06 (LOD1)"], items["PLT-01"], categories["MOD"]]
    for value, rect in zip(words[:4], rects, strict=True):
        item_label(frame, value, render.project(rect), 23, width=550)
    frame.label(words[4], (38, 840, 1882, 872), 26, weight=800)
    frame.label(words[5], (38, 875, 1882, 906), 23)
    frame.label(words[6], (38, 909, 1882, 942), 21, weight=600)


def demo_contents(frame, words):
    frame.rect((28, 121, 1888, 845), PANEL)
    frame.add("AltView", (638, 121, 1888, 845))
    frame.rect((28, 121, 638, 845), DARK)
    for y, heading, values in ((194, words[0], words[1:4]), (640, words[4], words[5:6])):
        frame.label(heading, (60, y, 610, y + 42), 32, weight=900, fill=CREAM)
        frame.rect((60, y + 54, 603, y + 58), RED)
        for index, value in enumerate(values):
            top = y + 83 + index * 83
            wrapped(frame, value, (60, top, 572, top + 82), 26, fill=CREAM)
    frame.label(words[6], (648, 850, 1882, 887), 22, weight=600)


def category_details(frame, words):
    source = "11_CategoryDetails"
    render = frame.add(source, (190, 16, 1884, 930), (280, 36, 1815, 1015), feather=22)
    items, _ = label_map(source)
    frame.label(words[0], (36, 54, 372, 92), 24, weight=850, overlay=True)
    frame.label(words[1], (36, 717, 372, 755), 24, weight=850, overlay=True)
    ids = ("STR-06", "STR-04", "STR-05", "STR-01", "STR-02", "STR-03", "STR-07",
           "FUR-01", "FUR-02", "FUR-03", "FUR-04", "FUR-05")
    for key, value in zip(ids, words[2:], strict=True):
        item_label(frame, value, render.project(items[key]), 18 if key in ("FUR-03", "FUR-04", "FUR-05") else 20,
                   width=178 if key.startswith("FUR") else 210)


def compositions(frame, words):
    crop = (92, 12, 1828, 1040)
    for i, value in enumerate(words[:6]):
        x = 30 + (i % 3) * 626
        y = 18 + (i // 3) * 450
        caption_tile(frame, f"CMP-{i + 1:02}", value, (x, y, x + 608, y + 434), crop)
    frame.label(words[6], (38, 909, 1882, 944), 21, weight=600)


def materials(frame, words):
    render = frame.add("13_Materials", (693, 38, 1886, 871), (694, 127, 1887, 960), feather=22)
    frame.rect((30, 184, 675, 752), PANEL)
    for i, letter in enumerate(("A", "F")):
        x = 43 + 314 * i
        frame.add(f"FMS_Garden_Atlas{letter}", (x, 282, x + 304, 586), nearest=True)
        title, separator, contents = words[i].partition(" · ")
        frame.label(title + separator.rstrip(), (x, 605, x + 304, 638), 23, weight=800, align="center")
        frame.label(contents, (x, 639, x + 304, 671), 20, weight=800, align="center")
    items, _ = label_map("13_Materials")
    ids = ("STR-01_Gate", "WTR-01", "FUR-01", "PLT-01", "PLT-06", "TOP-03", "FLB-03_Planted")
    for key, value in zip(ids, words[2:9], strict=True):
        item_label(frame, value, render.project(items[key]), 20, width=244)
    frame.label(words[9], (38, 876, 1882, 908), 26, weight=800)
    frame.label(words[10], (38, 912, 1882, 941), 22)


def unity_setup(frame, words):
    lod, pivot, material, heading, *entries = words
    source = "14_Unity"
    frame.add(source, (28, 24, 1024, 702), (330, 86, 1326, 764))
    project = frame.add(source, (28, 720, 654, 928), (0, 764, 566, 952))
    frame.add(source, (673, 720, 1024, 809), (0, 86, 329, 169))
    inspector = frame.add(source, (1360, 24, 1892, 732), (1496, 86, 1920, 650))

    # Leaders stop in the gutter, at the actual Position and triangle rows.
    for value, (top, bottom) in ((pivot, (316, 335)), (lod, (590, 646))):
        x, y1, _, y2 = inspector.project((1496, top, 0, bottom - top))
        y = (y1 + y2) // 2
        frame.rect((1046, y - 36, 1331, y + 36), DARK)
        if value == pivot:
            wrapped(frame, value, (1060, y - 26, 1318, y + 27), 19, weight=800, fill=CREAM)
        else:
            frame.label(value, (1060, y - 21, 1318, y + 21), 19, weight=800, fill=CREAM)
        frame.draw.line(((1331, y), (x - 6, y)), fill=RED, width=3)
        frame.draw.line(((x - 6, y1), (x - 6, y2)), fill=RED, width=3)
        for edge in (y1, y2):
            frame.draw.line(((x - 6, edge), (x - 2, edge)), fill=RED, width=3)

    # The material name describes the selected prefab; its renderer is not open.
    _, y, x, _ = project.project((0, 915, 566, 0))
    frame.rect((673, y - 25, 1110, y + 25), DARK)
    frame.label(material, (687, y - 20, 1096, y + 20), 22, weight=800, fill=CREAM)
    frame.draw.line(((x + 4, y), (674, y)), fill=RED, width=3)
    frame.draw.polygon(((x + 3, y), (x + 12, y - 5), (x + 12, y + 5)), fill=RED)

    frame.rect((1134, 750, 1892, 932), DARK)
    frame.label(heading, (1156, 761, 1870, 802), 28, weight=900, fill=CREAM)
    frame.rect((1156, 805, 1870, 808), RED)
    for i, entry in enumerate(entries):
        y = 817 + i * 26
        frame.label(entry, (1156, y, 1870, y + 25), 22, weight=650, fill=CREAM)


def builds(copy):
    icon, card, cover, social = tuple(copy.slots)[:4]
    for name, size in ((icon, copy.sizes[icon]), (icon + "_1024", (1024, 1024))):
        frame = Frame(size)
        frame.add("IconSource", (0, 0, *size), (59, 64, 965, 970))
        frame.corner(copy.slots[icon][0], round(size[0] * .30))
        yield name, frame, size
    for name, size in ((card, copy.sizes[card]), (card + "_1260x840", (1260, 840))):
        yield name, title_page("Card", size, copy.slots[card], card=True), size
    size = copy.sizes[cover]
    yield cover, title_page("Cover", size, copy.slots[cover], card=False), size
    size = copy.sizes[social]
    frame = Frame(size)
    frame.add("Hero", (0, 0, *size), (0, 20, 1920, 1028))
    yield social, frame, size

    layouts = {
        "06_FullCollection": full_collection,
        "06b_FullCollection": collection_details,
        "07_Closeups": closeups,
        "08_VariantsAndModules": variants,
        "09_Technical": technical,
        "10_DemoAndVersion": demo_contents,
        "11_CategoryDetails": category_details,
        "12_Compositions": compositions,
        "13_Materials": materials,
        "14_UnityAndComparison": unity_setup,
    }
    for name in copy.gallery:
        frame = Frame()
        if name == "05_Hero":
            frame.add("Hero", (0, 0, *GALLERY))
        else:
            layouts[name](frame, copy.captions[name])
        gallery_plate(frame, copy.slots[name])
        yield name, frame, copy.sizes[name]


def main():
    for name, frame, size in builds(Copy()):
        path = MEDIA / "final" / f"{name}.png"
        frame.save(path, size)
        print(f"{path.name}: {size[0]}x{size[1]}")
    CHECKS.mkdir(parents=True, exist_ok=True)
    for name in ("02_Card", "01_Icon"):
        with Image.open(MEDIA / "final" / f"{name}.png") as image:
            image.save(CHECKS / f"{name}_{image.width}_check.png")
            if name == "01_Icon":
                image.resize((60, 60), Image.Resampling.LANCZOS).save(CHECKS / "01_Icon_60_check.png")
    for name in ("06_FullCollection", "06b_FullCollection", "08_VariantsAndModules",
                 "09_Technical", "11_CategoryDetails", "13_Materials", "14_UnityAndComparison"):
        with Image.open(MEDIA / "final" / f"{name}.png") as image:
            image.resize((1280, 720), Image.Resampling.LANCZOS).save(
                CHECKS / f"{name}_1280_check.png"
            )


if __name__ == "__main__":
    main()
