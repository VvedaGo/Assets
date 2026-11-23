"""Finalize preview PNGs and the comparison sheet after running build_sit.py."""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

out = Path(__file__).resolve().parent
repo = out.parents[3]
temp = Path(os.environ["TEMP"]) / "FarmAnimalsCodex"
for view in ("q", "side", "front", "back"):
    name = f"sit_{view}.png"
    with Image.open(temp / name) as source:
        source.convert("RGB").resize((1000, 625), Image.Resampling.LANCZOS).save(temp / f"final_{name}")
    (out / name).write_bytes((temp / f"final_{name}").read_bytes())

tiles = (
    (repo / "planning/FarmAnimals/references/PET-01.png", None, "PET-01 reference"),
    (repo / "art/Farm_Animals/Previews/Anim/Dog_Sit_Idle.gif", (100, 0, 530, 370), "Existing sit · frame 0"),
    (temp / "sit_q.png", (235, 22, 1035, 765), "Static sit · front-left"),
)
panel_w, panel_h = 484, 410
margin, gutter = 24, 14
sheet = Image.new("RGB", (2 * margin + 3 * panel_w + 2 * gutter, panel_h + 2 * margin + 45), "#f2f0eb")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype(str(Path(os.environ["WINDIR"]) / "Fonts/segoeui.ttf"), 25)
for index, (path, crop, label) in enumerate(tiles):
    x = margin + index * (panel_w + gutter)
    with Image.open(path) as source:
        img = source.convert("RGB")
    if crop:
        img = img.crop(crop)
    img = ImageOps.contain(img, (panel_w, panel_h), Image.Resampling.LANCZOS)
    sheet.paste(img, (x + (panel_w - img.width) // 2, margin + (panel_h - img.height) // 2))
    draw.text((x + panel_w / 2, margin + panel_h + 25), label, fill="#262020", font=font, anchor="mm")
sheet.save(temp / "compare.png")
(out / "compare.png").write_bytes((temp / "compare.png").read_bytes())

