"""Build the Farm Animals store graphics from local sources.

Run with Python/Pillow and Node. Pass the path to an installed @resvg/resvg-js
package directory as the first argument.
"""
from base64 import b64encode
from html import escape
from io import BytesIO
from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

MEDIA = Path(__file__).resolve().parent.parent
REPO = MEDIA.parents[2]
RAW = MEDIA / "Raw"
STUDIO = RAW / "Studio"
RENDERS = MEDIA / "Renders"
EDITABLE = MEDIA / "Editable"
FINAL = MEDIA / "Final"
ATLAS = REPO / "Assets/FarmAnimals/Art/Textures"

DARK = "#20242A"
RED = "#C8473B"
GOLD = "#F5C85D"
CREAM = "#FFF9EB"
PAPER = "#F0EEE9"
NEUTRAL = "#E9E9EC"
BORDER = "#D6D3CE"
INK = "#333941"
PROPS = "Buildings & plants: Farm Yard / Farm Nature (not included)"
DECOR = "Set dressing: Farm Yard / Farm Nature (not included)"

GROUPS = {
    "LIVESTOCK": "Cow Calf Bull Horse Foal Donkey Sheep Lamb Ram Goat Kid Pig Piglet".split(),
    "BIRDS": "Hen Rooster Chick Turkey Duck Duckling Goose Pigeon Sparrow Crow".split(),
    "PETS": "Dog Puppy Cat Kitten".split(),
    "SMALL ANIMALS": "Fox Rabbit Hedgehog Mouse Frog".split(),
    "INSECTS": "Bee Butterfly Ladybug".split(),
}


def rect(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def polygon(points, fill):
    return f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{fill}"/>'


def label(x, y, value, size, fill=CREAM, *, face="Arial", bold=False, anchor="start"):
    weight = ' font-weight="700"' if bold else ""
    return (f'<text x="{x}" y="{y}" font-family="{face}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}"{weight}>{escape(value)}</text>')


def heading(x, y, value, size, fill=CREAM, anchor="start"):
    return label(x, y, value, size, fill, face="Impact", anchor=anchor)


def layer(name, *body):
    return f'<g inkscape:groupmode="layer" inkscape:label="{escape(name, quote=True)}">{"".join(body)}</g>'


def picture(x, y, w, h, path, *, center=(.5,.5), crop=None, nearest=False):
    with Image.open(path) as source:
        source = source.convert("RGB")
        if crop:
            source = source.crop(crop)
        # Work at native source resolution where possible. The SVG scales the raster
        # at export, with nearest-neighbour reserved for displaying palette texels.
        if nearest:
            source = source.resize((w,h), Image.Resampling.NEAREST)
        else:
            factor = min(1, source.width / w, source.height / h)
            source = ImageOps.fit(source, (round(w * factor), round(h * factor)),
                                  Image.Resampling.LANCZOS, centering=center)
        data = BytesIO()
        source.save(data, format="PNG")
    encoded = b64encode(data.getvalue()).decode("ascii")
    return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" '
            f'xlink:href="data:image/png;base64,{encoded}"/>')


def master(name, width, height, *layers):
    content = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
               f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
               f'<title>{name.replace("_", " ")}</title>{"".join(layers)}</svg>')
    (EDITABLE / f"{name}.svg").write_text(content, encoding="utf-8")


def badge(edge, size):
    baseline = round(edge * .43)
    x = round(edge * .35)
    return layer("3D corner badge",
                 polygon([(0,0),(edge,0),(0,edge)], RED),
                 f'<g transform="rotate(-45 {x} {baseline})">'
                 f'{label(x, baseline, "3D", size, bold=True, anchor="middle")}</g>')


def footer(title, subtitle, note="", width=900):
    y = 964
    return layer("Gallery plate",
                 polygon([(0,y),(width-44,y),(width,y+44),(width,1080),(0,1080)], DARK),
                 polygon([(0,y),(width-44,y),(width-34,y+10),(0,y+10)], RED),
                 heading(48,1020,title,40), label(48,1055,subtitle,23),
                 label(width-53,1017,"FARM ANIMALS",16,GOLD,bold=True,anchor="end"),
                 (polygon([(1920,y+44),(1920,1080),(1920-max(660, len(note)*10+48),1080),
                           (1920-max(660, len(note)*10+48),y+71),
                           (1920-max(660, len(note)*10+48)+27,y+44)], DARK) +
                  label(1880,1055,note,21,anchor="end")) if note else "")


def key_title(width, height, y, title_size, tagline):
    big = width > 1500
    left = 54 if not big else 70
    base = y + (157 if not big else 158)
    slant = 25
    accent = 600 if not big else 810
    x2 = left + accent
    stripe_top = base + (30 if not big else 27)
    stripe_end = stripe_top + (58 if not big else 63)
    return layer("Title, tagline and attribution",
                 rect(0,y,width,height-y,DARK),
                 polygon([(0,y),(width*.60,y),(width*.60+25,y+10),(0,y+10)],GOLD),
                 heading(left,base,"FARM ANIMALS",title_size),
                 polygon([(left,stripe_top),(x2,stripe_top),(x2-slant,stripe_end),(left,stripe_end)],RED),
                 label(left+18,stripe_end-17,tagline,31 if not big else 36,bold=True),
                 label(width-left,height-40,PROPS,26 if not big else 28,anchor="end"))


def catalog_group(name, x, y, cols, cell_width, cell_height):
    entries = GROUPS[name]
    body = [rect(x,y,cell_width*cols-6,31,DARK),
            rect(x,y,6,31,RED),
            label(x+15,y+22,f"{name}  ·  {len(entries)}",19,bold=True)]
    for i, animal in enumerate(entries):
        cx = x + (i % cols)*cell_width
        cy = y + 35 + (i // cols)*cell_height
        body += [layer(animal, picture(cx,cy,cell_width-6,cell_height-27,STUDIO/f"{animal}.png",
                                        center=(.5,.5)),
                       rect(cx,cy+cell_height-27,cell_width-6,23,"#FAF9F7"),
                       label(cx+(cell_width-6)/2,cy+cell_height-9,animal,18,INK,
                             bold=True,anchor="middle"))]
    return layer(name,*body)


def build():
    master("01_Icon", 1024,1024,
           layer("Illustrated cow",picture(0,0,1024,1024,MEDIA/"Concepts/Generated_Original.png")),
           badge(243,90))
    master("02_Card",1260,840,
           layer("Farm morning",picture(0,0,1260,526,RENDERS/"01_FarmMorning.png",center=(.43,.50))),
           badge(166,63), key_title(1260,840,526,137,"LOW POLY FARM LIFE"))
    master("03_Cover",1950,1300,
           layer("Farmyard",picture(0,0,1950,988,RAW/"Hero_Farmyard_2p4.png",center=(.50,.74))),
           badge(220,83), key_title(1950,1300,988,151,"LIVESTOCK, POULTRY & PETS"))
    master("04_Social",1200,630,
           layer("Pasture families",picture(0,0,1200,630,RENDERS/"02_PastureFamilies.png",center=(.5,.58))))

    master("05_Hero",1920,1080,
           layer("Livestock yard",picture(0,0,1920,975,RENDERS/"07_LivestockYard.png",center=(.50,.68))),
           layer("Footer backdrop",rect(0,975,1920,105,DARK)),
           footer("LIFE IN THE FARMYARD","Bull, donkey, ram, pig and piglet",PROPS))

    master("06_FullCollection",1920,1080,layer("Catalog backing",rect(0,0,1920,1080,NEUTRAL)),
           catalog_group("LIVESTOCK",36,24,7,265,157),
           catalog_group("BIRDS",36,378,5,231,174),
           catalog_group("PETS",1196,378,2,344,174),
           catalog_group("SMALL ANIMALS",36,766,5,231,153),
           catalog_group("INSECTS",1196,766,3,229,153),
           footer("FULL COLLECTION","35 rigged animals  ·  35 animal prefabs"))

    detail = []
    for i, (name, caption) in enumerate([
        ("Cow","HOLSTEIN COAT & FACETED MUZZLE"),("Rooster","COMB & TAIL FEATHERS"),
        ("Dog","TRICOLOUR COAT"),("Fox","POINTED EARS & WHITE TAIL TIP")
    ]):
        x = 42 + (i%2)*928
        y = 33 + (i//2)*454
        detail.append(layer(name, picture(x,y,908,382,STUDIO/f"Detail_{name}.png"),
                            rect(x,y+382,908,53,DARK),rect(x,y+382,7,53,RED),
                            heading(x+20,y+420,name.upper(),35),
                            label(x+228,y+416,caption,21,bold=True)))
    master("07_Closeups",1920,1080,layer("Detail backing",rect(0,0,1920,1080,PAPER)),
           *detail,footer("MODEL CLOSE-UPS","Four examples of the pack’s flat-colour geometry"))

    strips = []
    for i, (action, title) in enumerate([("Walk","WALK"),("Graze","GRAZE"),("Lie_Down","LIE DOWN")]):
        y = 40+i*298
        strips.append(layer(title,rect(40,y,194,272,DARK),rect(40,y,194,8,RED),
                            label(62,y+117,"COW",23,GOLD,bold=True),heading(62,y+166,title,39),
                            *(layer(f"Pose {phase}%",picture(248+j*409,y,400,272,STUDIO/f"Cow_{action}_{phase}.png"))
                              for j,phase in enumerate([10,33,59,85]))))
    master("08_Animations",1920,1080,layer("Animation backing",rect(0,0,1920,1080,PAPER)),
           *strips,footer("ANIMATION CLIPS","113 in-place clips  ·  14 for the cow  ·  Animation events"))

    views = []
    for i, (name,count) in enumerate([("Cow","1,852"),("Rooster","1,430"),("Rabbit","1,096")]):
        x = 40+i*619
        views.append(layer(name,
                           picture(x,44,602,415,STUDIO/f"Beauty_{name}.png"),
                           picture(x,474,602,415,STUDIO/f"Wire_{name}.png"),
                           rect(x,889,602,53,DARK),rect(x,889,7,53,RED),
                           heading(x+20,927,name.upper(),35),label(x+575,923,f"{count} TRIANGLES",24,bold=True,anchor="end")))
    master("09_Technical",1920,1080,layer("Technical backing",rect(0,0,1920,1080,PAPER)),
           *views,footer("SHADED WIREFRAME","Generic rig  ·  Bones visible in hierarchy  ·  No LODs"))

    demo = []
    for name,x,y,w,h in [("Livestock",42,34,896,434),("Birds",954,34,924,434),
                         ("Pets",42,484,600,445),("SmallAnimals",658,484,600,445),
                         ("Insects",1274,484,604,445)]:
        title = "SMALL ANIMALS" if name == "SmallAnimals" else name.upper()
        # Keep full-width island views on matching sky blue to preserve the silhouettes.
        ph = round(w * 9/16)
        iw = min(w, round((h-48) * 16/9))
        ih = min(ph,h-48)
        demo.append(layer(title,rect(x,y,w,h,"#B9DBF3"),
                          picture(x+(w-iw)//2,y+(h-48-ih)//2,iw,ih,RAW/f"Demo_FarmAnimals_Showcase_Cam_{name}.png"),
                          rect(x,y+h-48,w,48,DARK),heading(x+19,y+h-14,title,31)))
    master("10_Demo",1920,1080,layer("Demo backing",rect(0,0,1920,1080,PAPER)),*demo,
           footer("SHOWCASE ISLANDS","Five animal categories  ·  Two included demo scenes"))

    category = []
    for i,name in enumerate(["Bee","Butterfly","Ladybug"]):
        y = 41+302*i
        category.append(layer(name,picture(1162,y,464,277,STUDIO/f"Category_{name}.png"),
                              rect(1626,y,250,277,DARK),rect(1626,y,250,8,RED),
                              heading(1650,y+152,name.upper(),35)))
    master("11_CategoryDetails",1920,1080,
           layer("Category backing",rect(0,0,1920,1080,PAPER)),
           layer("Meadow scene",
                 picture(42,87,1098,618,RENDERS/"06_MeadowFriends.png"),
                 rect(42,41,1098,46,DARK),heading(61,74,"MEADOW FRIENDS",31)),
           *(layer(name,picture(42+i*557,723,349,201,STUDIO/f"Category_{name}.png"),
                   rect(391+i*557,723,192,201,DARK),rect(391+i*557,723,192,8,RED),
                   heading(407+i*557,835,name.upper(),31))
             for i,name in enumerate(["Rabbit","Hedgehog"])),
           *category,footer("SMALL ANIMALS & INSECTS","Meadow scene and close-ups of all three insects",DECOR,930))

    scenes = []
    for i,name in enumerate(["Pasture","Stable","SheepFlock","Pigsty","Barnyard","Pond","Garden","Orchard"]):
        x = 42+(i%4)*463
        y = 36+(i//4)*453
        title = "SHEEP FLOCK" if name=="SheepFlock" else name.upper()
        scenes.append(layer(title,rect(x,y,444,418,"#B9DBF4"),
                            picture(x,y+39,444,320,RAW/f"Demo_FarmAnimals_Compositions_Cam_{name}.png",
                                    crop=(137,0,1463,900),center=(.5,.52)),
                            rect(x,y+369,444,49,DARK),rect(x,y+369,7,49,RED),
                            heading(x+19,y+404,title,31)))
    master("12_Compositions",1920,1080,layer("Composition backing",rect(0,0,1920,1080,PAPER)),*scenes,
           footer("8 COMPOSITIONS","Animal group prefabs shown on their demo islands"))

    materials = []
    for i,name in enumerate(["Cow","Rooster","Rabbit"]):
        x = 42+i*619
        y = 45
        materials.append(layer(name,
                               picture(x,y,598,441,STUDIO/f"Beauty_{name}.png"),
                               rect(x,y+441,598,410,"#E4E2DF"),
                               rect(x+141,y+480,316,316,DARK),
                               picture(x+143,y+482,312,312,ATLAS/f"T_FarmAnimals_{name}_BaseColor.png",nearest=True),
                               heading(x+299,y+833,name.upper(),36,DARK,anchor="middle")))
    master("13_Materials",1920,1080,layer("Material backing",rect(0,0,1920,1080,PAPER)),*materials,
           footer("PALETTE ATLASES","35 base-colour atlases  ·  256 × 256 px  ·  One URP/Lit material per animal",width=1150))

    master("14_Unity",1920,1080,
           layer("Editor backing",rect(0,0,1920,1080,DARK),rect(42,40,1836,888,"#32373D")),
           layer("Animator graph",
                 picture(56,89,1304,607,RAW/"Unity_Animator.png",crop=(0,0,1228,572)),
                 rect(56,52,1304,37,RED),label(73,78,"ANIMATOR CONTROLLER  /  AC_FarmAnimals_Cow",22,bold=True)),
           layer("Project window",
                 picture(56,712,654,202,RAW/"Unity_Project.png",crop=(0,0,505,156))),
           layer("Prefab preview",
                 picture(724,712,636,202,STUDIO/"Editor_Cow.png")),
           layer("Inspector",
                 picture(1376,89,488,629,RAW/"Unity_Inspector.png",crop=(0,0,340,438)),
                 picture(1376,730,488,184,RAW/"Unity_Inspector.png",crop=(0,529,340,657)),
                 rect(1376,52,488,37,RED),label(1393,78,"PREFAB  /  FMS_Cow",22,bold=True)),
           footer("BUILT FOR UNITY 6","Prefab Animator  ·  Generic avatar  ·  Controller per animal",width=1120))


def rasterize(resvg):
    program = """
const fs = require('node:fs');
const path = require('node:path');
const {Resvg} = require(process.argv[1]);
for (const file of fs.readdirSync(process.argv[2]).filter(n => n.endsWith('.svg'))) {
    const source = fs.readFileSync(path.join(process.argv[2],file));
    const render = new Resvg(source);
    fs.writeFileSync(path.join(process.argv[3],file.replace(/\\.svg$/,'.png')),render.render().asPng());
}
"""
    subprocess.run(["node","-e",program,str(Path(resvg).resolve()),str(EDITABLE),str(FINAL)],check=True)
    for path in FINAL.glob("*.png"):
        with Image.open(path) as image:
            if image.mode == "RGBA" and image.getchannel("A").getextrema() != (255,255):
                raise ValueError(f"Non-opaque export: {path}")
            rgb = image.convert("RGB")
        rgb.save(path,optimize=True)
    for name, size in [("01_Icon",160),("02_Card",420)]:
        with Image.open(FINAL/f"{name}.png") as image:
            width,height = size, round(image.height*size/image.width)
            small = image.resize((width,height), Image.Resampling.LANCZOS)
            small.save(FINAL/f"{name}_{width}x{height}.png",optimize=True)
    with Image.open(FINAL/"01_Icon.png") as image:
        image.resize((60,60),Image.Resampling.LANCZOS).save(RAW/"Icon_60px_Review.png")


def contact_sheet():
    files = sorted(FINAL.glob("*.png"))
    width, cols, cell_w, cell_h = 1752, 4, 420, 328
    rows = (len(files)+cols-1)//cols
    sheet = Image.new("RGB",(width,140+rows*cell_h),CREAM)
    draw = ImageDraw.Draw(sheet)
    impact = ImageFont.truetype("impact.ttf",58)
    arial = ImageFont.truetype("arial.ttf",20)
    draw.text((35,26),"FARM ANIMALS",DARK,font=impact)
    draw.text((38,102),"ASSET STORE MEDIA  /  KEY IMAGES & GALLERY",INK,font=arial)
    files = sorted(files, key=lambda p: (0 if p.stem.startswith("01_") else 1,p.stem))
    for i,path in enumerate(files):
        c,r = i%cols,i//cols
        x,y = 36+c*cell_w,154+r*cell_h
        draw.rectangle((x,y,x+399,y+276),fill=PAPER)
        with Image.open(path) as source:
            dims = f"{source.width} × {source.height}"
            if "_" in path.stem[3:] and source.width <= 420:
                # Native-size thumbnail review; do not enlarge the small icon.
                preview = source.copy()
                preview.thumbnail((400,276),Image.Resampling.LANCZOS)
            else:
                preview = ImageOps.contain(source,(400,276),Image.Resampling.LANCZOS)
            sheet.paste(preview,(x+(400-preview.width)//2,y+(276-preview.height)//2))
        draw.text((x,y+282),f"{path.stem}  ·  {dims}",DARK,font=arial)
    sheet.save(MEDIA/"ContactSheet.jpg",quality=93,subsampling=0,optimize=True)


if __name__ == "__main__":
    build()
    rasterize(sys.argv[1])
    contact_sheet()
