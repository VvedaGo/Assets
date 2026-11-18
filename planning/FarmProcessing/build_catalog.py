"""Rebuild the planning catalog and reference prompts; does not create Unity assets."""
from pathlib import Path
import csv
import io

ROOT = Path(__file__).resolve().parent
# ID, name, English object description, dimensions X/Z/Y metres, triangle budget,
# release wave, moving parts. Each row is ONE independently usable object family.
DATA = """STA-01|Сыроварочный чан|open round cheese-making vat on a low stand, a removable lid and separate stirring paddle, simple cream curd surface|1.2/1.0/1.1|1200–2400|core|крышка; мешалка
STA-02|Винтовой сырный пресс|tabletop wooden screw cheese press with a clear vertical threaded spindle, pressing plate and removable cheese mold|0.8/0.7/1.2|1600–3000|core|винт; нажимная плита
STA-03|Вертикальная маслобойка|traditional upright wooden butter churn with a narrow barrel, removable lid and vertical dasher|0.5/0.5/1.0|700–1400|core|шток; крышка
STA-04|Дробилка фруктов|hand-cranked fruit crusher on a wooden stand, square hopper, two simple rollers, open output chute|1.0/0.8/1.2|1600–3000|core|рукоять; два вала
STA-05|Пресс для сока|wooden basket fruit press on a raised frame, vertical screw, pressing plate and a clearly visible juice outlet|1.0/0.9/1.6|2200–4000|core|винт; нажимная плита
STA-06|Ручные жернова|two horizontal circular millstones on a low wooden support, central grain inlet, upper stone with a hand crank and flour outlet|0.9/0.8/0.9|1000–2000|core|верхний жернов; рукоять
STA-07|Котёл для варенья|wide copper jam kettle on a small brick hearth, removable lid, separate wooden stirring paddle, opaque red jam surface|1.0/0.9/1.1|1200–2400|core|крышка; мешалка
STA-08|Сушильная стойка|freestanding wooden food drying rack with three removable mesh trays, open sides and simple chunky frame|1.1/0.7/1.6|900–1800|core|три лотка
STA-09|Печь для хлеба|small freestanding rustic brick bread oven with a domed chamber, arched opening, hinged metal door and short chimney|1.5/1.4/1.8|2200–4000|extension|дверца
STA-10|Масляный пресс|rustic manual seed oil screw press, wooden frame, small seed hopper, pressing chamber and oil spout, visibly distinct from fruit press|1.0/0.8/1.4|1800–3500|extension|винт; рукоять
STA-11|Коптильный шкаф|freestanding wooden food smoking cabinet on a brick base, hinged front door, two removable racks and short metal flue|0.9/0.8/1.8|1600–3000|extension|дверь; две решётки
STA-12|Ручная медогонка|small hand-cranked cylindrical honey extractor on three legs, removable opaque lid, simple internal basket and bottom honey tap|0.8/0.8/1.2|1600–3200|extension|крышка; рукоять; корзина
TOL-01|Форма для сыра|single round perforated cheese mold with a solid base and thick cream-colored walls|0.25/0.25/0.18|150–400|core|нет
TOL-02|Сырная лира|single rectangular stainless steel curd cutting harp with a wooden handle and a few thick parallel wires|0.25/0.03/0.55|120–350|core|нет
TOL-03|Лопатка сыродела|single broad wooden cheese stirring paddle with a short slotted head|0.12/0.04/0.65|80–200|core|нет
TOL-04|Дуршлаг для творога|single shallow cream metal colander with two small handles and readable large perforations|0.35/0.3/0.15|200–500|core|нет
TOL-05|Черпак|single deep metal ladle with a long wooden grip|0.12/0.08/0.45|120–300|core|нет
TOL-06|Мерный кувшин|single opaque cream enamel measuring jug with a spout and handle, no writing or transparent glass|0.25/0.2/0.3|200–450|core|нет
TOL-07|Воронка для розлива|single wide metal bottling funnel with a short narrow stem|0.2/0.2/0.22|100–250|core|нет
TOL-08|Сито для муки|single round wooden flour sieve with a coarse simplified mesh base|0.35/0.35/0.1|150–400|core|нет
TOL-09|Совок для зерна|single wooden grain scoop with a broad open bowl and a short handle|0.15/0.32/0.1|100–250|core|нет
TOL-10|Доска для сыра|single thick rectangular cheese cutting board with a short handle and no food|0.45/0.28/0.04|80–180|core|нет
TOL-11|Нож для сыра|single short broad cheese knife with a simple wooden handle|0.05/0.03/0.3|80–200|core|нет
TOL-12|Керамическая миска|single wide shallow cream ceramic preparation bowl, empty|0.35/0.35/0.13|150–350|core|нет
TOL-13|Пекарская лопата|single long wooden bread peel with a flat rounded head|0.35/0.06/1.4|120–300|extension|нет
TOL-14|Скалка|single thick wooden rolling pin with two short handles|0.08/0.5/0.08|100–250|extension|нет
TOL-15|Крюк для копчения|single chunky S-shaped metal smoking hook|0.08/0.03/0.16|80–180|extension|нет
TOL-16|Щипцы для печи|single pair of closed iron oven tongs with thick handles|0.08/0.05/0.5|150–350|extension|нет
TOL-17|Рамка с сотами|single rectangular wooden honeycomb frame with simplified golden hexagonal cells, no bees|0.4/0.04/0.25|250–700|extension|нет
TOL-18|Масляная воронка с фильтром|single small metal oil strainer funnel on a three-legged tabletop support, visibly distinct from a plain funnel|0.25/0.25/0.35|200–500|extension|нет
PRD-01|Круг сыра в форме|single small fresh cheese wheel resting inside a shallow perforated mold, integrated food process prop|0.25/0.25/0.15|200–450|core|нет
PRD-02|Сырный круг с вырезанным сектором|single mature cheese wheel with one wedge removed and a readable cream interior|0.35/0.35/0.15|200–450|core|нет
PRD-03|Брусок масла на дощечке|single rectangular butter block on a small dedicated wooden butter board|0.22/0.16/0.08|120–300|core|нет
PRD-04|Творог в ткани|single cloth-lined curd bundle with an open top showing simple white curds|0.25/0.25/0.18|250–600|core|нет
PRD-05|Фруктовая мезга в лотке|single shallow rectangular processing tray filled with chunky red apple pomace, no separate apples|0.5/0.35/0.12|250–600|core|нет
PRD-06|Сок в керамическом кувшине|single wide-mouth cream ceramic juice pitcher with a simple opaque orange liquid surface|0.25/0.25/0.35|250–500|core|нет
PRD-07|Банка варенья под тканью|single squat opaque jam pot with a tied cloth lid and a visible red fruit-colored body, no label|0.16/0.16/0.2|200–450|core|нет
PRD-08|Поднос долек для сушки|single rectangular shallow drying tray with separated chunky apple slices attached as one process prop|0.5/0.35/0.07|300–700|core|нет
PRD-09|Пучок сушёных трав|single tied bunch of dried culinary herbs hanging stem-up, simple clustered leaves|0.2/0.15/0.4|200–500|core|нет
PRD-10|Открытый мешок с мукой|single small open flour sack with rolled cloth rim and a pale flour mound visible inside|0.35/0.3/0.45|250–550|core|нет
PRD-11|Тесто в миске|single ceramic mixing bowl holding one large risen bread dough mound|0.35/0.35/0.2|250–550|core|нет
PRD-12|Лоток сушёных ягод|single small wooden drying tray with attached clusters of dark dried berries, not fresh market fruit|0.4/0.3/0.08|250–650|core|нет
PRD-13|Хлеб на пекарском противне|single flat dark baking tray with three attached small scored bread rolls|0.45/0.35/0.12|300–700|extension|нет
PRD-14|Семенной жмых|single rough round compressed seed oil cake with large simple visible seed fragments|0.3/0.3/0.08|150–350|extension|нет
PRD-15|Керамическая бутылка масла|single tall opaque ceramic oil bottle with a narrow neck and a small wooden stopper, no label|0.12/0.12/0.32|200–450|extension|нет
PRD-16|Подвес копчёной рыбы|single smoked fish hanging from an integrated short cord, dark golden skin and clear stylized silhouette|0.1/0.08/0.4|250–600|extension|нет
PRD-17|Подвес копчёного окорока|single smoked ham hanging from an integrated short cord, simple reddish brown meat shape|0.2/0.16/0.4|250–600|extension|нет
PRD-18|Мёд в керамическом горшке|single small open honey crock with an opaque golden honey surface and a wooden honey dipper resting across its rim|0.2/0.2/0.22|250–550|extension|нет
FUR-01|Рабочий стол сыродела|single sturdy wooden preparation workbench with a pale stone top, lower shelf and no props|1.6/0.7/0.9|500–1000|core|нет
FUR-02|Стол фасовки|single narrow wooden bottling table with a raised back rail and a low front rim, no props|1.4/0.6/0.9|450–900|core|нет
FUR-03|Стеллаж созревания сыра|single open wooden cheese aging shelf with four widely spaced slatted shelves, empty|1.2/0.5/1.8|600–1200|core|нет
FUR-04|Сушильная полка для трав|single wall-mounted wooden herb drying rail with six thick wooden pegs, empty|1.2/0.25/0.3|180–400|core|нет
FUR-05|Стеллаж банок|single narrow freestanding pantry shelf with three shelves and a short back rail, empty|0.9/0.4/1.5|400–850|core|нет
FUR-06|Деревянная мойка|single rustic washstand with an integrated opaque enamel basin and separate simple hand pump, no water animation|0.9/0.6/1.1|700–1400|core|рычаг насоса
FUR-07|Подставка для пресса|single low reinforced square wooden press stand with diagonal braces|0.8/0.8/0.5|300–650|core|нет
FUR-08|Тележка для лотков|single two-shelf wooden workshop trolley with four separate small wheels and a push handle, empty|0.8/0.5/0.9|600–1200|core|четыре колеса
FUR-09|Стол пекаря|single broad wooden baker worktable with a thick top and integrated flour trough on one side, empty|1.6/0.8/0.9|600–1200|extension|нет
FUR-10|Рейка коптильных крюков|single freestanding metal smoking rail on two upright supports, empty and without hooks|1.2/0.4/1.5|300–650|extension|нет
FUR-11|Подставка для медовых рамок|single wooden honey frame draining stand with a sloped collection tray, empty|0.7/0.5/0.7|400–850|extension|нет
FUR-12|Низкий поддон для продукции|single small dedicated wooden processing pallet with short feet and broad slats, empty|0.8/0.6/0.15|200–450|extension|нет
MOD-01|Плитка деревянного пола 2×2|single square rustic plank floor module with flush edges, no surrounding ground|2.0/2.0/0.15|120–300|core|нет
MOD-02|Плитка каменного пола 2×2|single square chunky stone floor module with flush edges, no surrounding ground|2.0/2.0/0.15|180–400|core|нет
MOD-03|Стена мастерской 2 м|single timber-framed cream plaster workshop wall module, 2 meters wide, flat straight side edges|2.0/0.18/2.4|250–550|core|нет
MOD-04|Стена с окном 2 м|single timber-framed workshop wall module with a large open window and thick sill, no glass|2.0/0.18/2.4|350–700|core|нет
MOD-05|Стена с дверным проёмом 2 м|single timber-framed workshop wall module with an open walk-through doorway, no door leaf|2.0/0.18/2.4|300–650|core|нет
MOD-06|Опорный столб|single chunky square wooden canopy support post with a simple stone foot, no surrounding floor|0.2/0.2/2.4|100–250|core|нет
MOD-07|Балка навеса 2 м|single horizontal wooden canopy beam with flat ends, no roof or posts|2.0/0.2/0.2|60–150|core|нет
MOD-08|Плоская крыша навеса 2×2|single nearly flat slatted wooden canopy roof panel with a dark terracotta top and flush grid edges|2.0/2.0/0.18|200–450|core|нет
MOD-09|Дверь мастерской|single thick rustic wooden door leaf with two hinges and a simple metal handle, isolated without a wall|0.9/0.08/2.0|200–450|extension|дверь на петлях
MOD-10|Низкая перегородка 2 м|single low wooden workshop partition with chunky slats and flat ends|2.0/0.15/1.1|200–450|extension|нет
MOD-11|Угловой столб|single vertical square timber corner post with simple flat faces for two adjoining wall modules|0.2/0.2/2.4|80–200|extension|нет
MOD-12|Полка под окном|single wall-mounted broad wooden serving shelf with two triangular brackets, no window or wall|1.5/0.4/0.12|150–350|extension|нет"""

rows = []
for line in DATA.splitlines():
    ident, name, desc, size, tris, wave, parts = line.split("|")
    category, number = ident.split("-")
    rows.append(dict(id=ident, name_ru=name, prefab=f"FMS_Workshop_{category}_{number}",
                     description_en=desc, size_x_z_y_m=size, tris_lod0_target=tris,
                     wave=wave, moving_parts=parts, status="planned"))

assert len(rows) == 72
assert sum(r["wave"] == "core" for r in rows) == 48
assert len({r['id'] for r in rows}) == len(rows)
buf = io.StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
writer.writeheader()
writer.writerows(rows)
(ROOT / "MODEL_CATALOG.csv").write_text(buf.getvalue(), encoding="utf-8-sig")

catalog_path = ROOT / "MODEL_CATALOG.md"
reference_style = ""
if catalog_path.exists():
    existing_catalog = catalog_path.read_text(encoding="utf-8")
    if "## Единый стиль референсов" in existing_catalog:
        reference_style = existing_catalog.split("## Единый стиль референсов", 1)[1].split("| ID |", 1)[0]
        reference_style = "## Единый стиль референсов" + reference_style

table = ["# Каталог Farm Processing & Workshops", "",
         "Проектные цели, 2026-11-13. Размеры: X × Z × Y, метры. Все 72 позиции пока planned.",
         "Одна строка — самостоятельное семейство предмета, а не гарантированно один mesh datablock.",
         "Внутренние подвижные детали, LOD и готовые композиции считаются отдельно после производства.", "",
         reference_style.rstrip(), "",
         "| ID | Предмет | Размер X/Z/Y, м | Tris LOD0, цель | Очередь | Отдельные части | Референс |",
         "|---|---|---|---|---|---|---|"]
for r in rows:
    image = ROOT / "references" / f"{r['id']}.png"
    reference = f"![{r['id']}](references/{image.name})" if image.exists() else "Ожидает"
    table.append(f"| {r['id']} | {r['name_ru']} | {r['size_x_z_y_m']} | {r['tris_lod0_target']} | {r['wave']} | {r['moving_parts']} | {reference} |")
(ROOT / "MODEL_CATALOG.md").write_text("\n".join(table)+"\n", encoding="utf-8")

style = ("Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, "
         "flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, "
         "muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. "
         "One isolated object, complete and centered, three-quarter front view from 30 degrees above, "
         "soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. ")
negative = ("No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, "
            "photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.")
prompts = ["# Промпты изображений и 3D", "",
           "3D-модели ещё не созданы. Готовые изображения и текущий прогресс — в MODEL_CATALOG.md, колонка «Референс».",
           "Референсы генерируются последовательно в порядке строк каталога; общий стиль закреплён в MODEL_CATALOG.md.",
           "Общий блок ниже соединять с описанием предмета. Reference задаёт форму; размеры и детали проверяются вручную.", "",
           "## Общий блок изображения", "", style, "", negative, "",
           "## Общие правила 3D", "",
           "Use the approved reference image as the shape and color guide. Generate ONLY the single described object. "
           "Complete the back, underside and hidden sides consistently. Do not include floor, shadow mesh, camera, "
           "lights, smoke, fire or floating fragments. Keep mechanical gaps open and parts geometrically plausible. "
           "No baked lighting or baked text. Low-poly game asset with simple palette UVs. "
           "Separate moving components if supported; otherwise rebuild these components manually after generation.", "",
           "Dimensions and topology are acceptance targets, not guaranteed generator outputs. "
           "Simple tools, modular architecture and repeated structural parts should normally be modeled directly. "
           "Do not generate a complete station again for each moving part. Maximum three attempts per object, "
           "then rebuild manually or re-estimate scope. No paid generation is launched by this document.", ""]
for r in rows:
    prompts += [f"## {r['id']} — {r['name_ru']}", "",
                f"Prefab: `{r['prefab']}`. Очередь: {r['wave']}. Размер X/Z/Y: {r['size_x_z_y_m']} м. "
                f"LOD0: {r['tris_lod0_target']} tris. Части для отделения: {r['moving_parts']}.", "",
                "**Image prompt:** " + style + "Object: " + r['description_en'] + ". " + negative, "",
                "**3D prompt:** " + "Generate only " + r['description_en'] + ". "
                "Match the approved reference; complete every side and remove any background geometry. "
                "Use the common 3D rules above. Final dimensions, triangle count, component separation, "
                "pivots and UVs must be corrected and verified during manual preparation.", ""]
(ROOT / "REFERENCE_AND_3D_PROMPTS.md").write_text("\n".join(prompts)+"\n", encoding="utf-8")
print(f"Generated {len(rows)} catalog entries and image/3D prompt pairs; core=48, extension=24.")
