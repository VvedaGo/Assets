# Demo_Harvest — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Demo / пространственная схема CMP-04, CMP-05 и зернотока · Store files built from it: 10_DemoAndVersion (Full), ориентир для Э10
Reference image: `planning/FarmMachinery/scenes/Demo_Harvest.png`

Кадрирование: 16:9, 1672 × 941 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: лист принятых превью grain-harvest, лист принятых превью forage-harvest, лист принятых превью hay-harvest, лист принятых превью grain-yard, лист принятых превью header-yard.

## Prompt (Codex, Sol 6.2)

```
Landscape 16:9 high-oblique 56° top-down Unity demo layout reference on one simple big flat plane, all separate zones with empty gaps. Fit all five zones precisely: LOWER LEFT on warm stubble, one red HRV-01 grain combine with mounted red reel ATT-03 from sheet 1, expand one silver auger to grain cart, one green big TRC-02 with full red single-axle TRL-05 with its unloading auger unfolded, and one distinct red TRC-01 hitched to grain-filled red TRL-01. MID LEFT sage zone, three parallel little haymaking pairs, green TRC-01 with red IMP-04 mower bar horizontal, red TRC-01 with two low unfolded round rake rotors IMP-07, red large TRC-02 towing one HRV-02 round baler with rear tailgate open and visibly empty. One separate empty long TRL-06 wood deck trailer with red lattice panels, and two even straw-gold lines PRP-01, each two joined modules, sheet 3. LOWER RIGHT on warm tan, one red HRV-03 with high curved red spout and one narrow attached ATT-05 pickup and one red TRC-01 towing empty red tall-sided TRL-01 tipper, sheet 2. MID FAR RIGHT, one BLUE HRV-01 with a RED ATT-04 seven-point corn header attached, then a standalone low red TRL-04 carrying one long red ATT-03 grain reel header ALONG the chassis length, sheet 5 with combine from sheet 1. FAR TOP RIGHT edge, exactly two identical galvanized squat round EQP-02 bins low cone roofs, with a single gray EQP-01 inclined auger conveyor on a red stand aligned toward one hatch, sheet 4. Every machine is seated on that plane at its true size. No bale in press or trailer, no straw bales anywhere, no other machines or environment decorations. Only two to three colours of flat painted ground to distinguish zoning, no field textures, no soil patterns, no tall crop, no plants, dust, maps, buildings except listed bins, signs, lines, markers, or people. Soft daylight, high clean technical staging composition.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit prompt for generation 2:
Edit input 1 diagram while preserving the five zones, camera and useful model placement; the next four sheets are reference anchors (grain, forage, hay, header). Specific corrections only: lower the mowing bar of the green tractor's disc mower to HORIZONTAL working position, and lower both grey rotors of the red tractor's hay rake to HORIZONTAL working position. Lowered rotating heads are open and are not wheels. The large tractor hitched to the open empty baler in the sage region should be RED. The stubble lower-left area must contain ONLY ONE red trapezoid cart TRL-05: remove the duplicate detached trapezoid cart under the main red combine's auger, and repark the GREEN large tractor AND its existing attached red cart next to that combine, with the gray discharge auger hanging over the same cart. Put the low grain load inside the attached cart only. Delete the yellow grain stream; only show a posed transfer. Keep the separate red tractor with red TRL-01 loaded tipper. Preserve the red forage harvester with front pickup and empty tipper group on right, the BLUE combine with a red corn header, the little carrier with red grain reel header, two squat grey bins and single conveyor. Preserve the empty red lattice trailer and flat gold windrows. Use only three uniform flat ground colors by unifying the two lower tan areas to one shade. No borders, paint markings, text or additions. Return a nominal 16:9 wide landscape.

Edit prompt for the selected generation:
Edit this exact full harvest DEMO Unity staging reference in input 1. Keep the camera, exactly five area groups, all machine types, colors, positions, sizes, mounted headers, open empty baler and empty bale trailer. Fix exactly three local details. UPPER LEFT: the small red disc mower directly hitched to the GREEN tractor is still in transport. Change its one upright red rectangular cutter bar with four or five grey circular cutters into the same one cutter bar pivoted fully DOWN so it lies FLAT at work height to the side of the mower frame, parallel to the ground. Its grey cutting discs are horizontal as on a real lowered side mower. Retain its grey and red colours and the coupling. Do not change the already-horizontal star-shaped rake rotors on the other nearby red tractor. LOWER LEFT: remove the tiny vertical yellow column of drawn falling grain from the tip of the combine's grey tube into the grain cart. The grain load inside the red trapezoid cart stays intact, the combine discharge head stays above the load, with a small visible AIR GAP between. Put that cart's own visible grey angled stowed or unfolded tube on the OPPOSITE side of its bin, solidly attached, never to the combine, and keep the cart hitched to the green tractor. FAR RIGHT yard: keep the two identical grey bins; place the long conveyor slightly in front of the bin rather than penetrating its hatch or wall. Exact same no-text layout, no bales, no environmental objects, flat matte pale taupe/tan and sage ground, clean 16:9. Input 2 is the actual Mower from which the horizontal work pose is derived. Inputs 3, 4, and 5 are accepted product model sheets for correct hay, grain, and yard shapes; the existing image's five zones stay.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Нижний левый сектор (CMP-04) | HRV-01 Red ×1, ATT-03 ×1, TRC-02 Green ×1, TRL-05 Full ×1, TRC-01 Red ×1, TRL-01 Grain ×1 | Жатка на HRV-01. Зерновая связка и отдельный отвоз. У TRL-05 раскрытый шнек по CMP-04. |
| Средний левый сектор (CMP-05) | TRC-01 Green ×1, IMP-04 Work ×1, TRC-01 Red ×1, IMP-07 Work ×1, TRC-02 Red ×1, HRV-02 Open ×1, TRL-06 ×1, PRP-01 ×4 | По одной сцепке на каждое орудие и пресс. Камера открыта и пуста. Платформа пуста. Валки по два модуля встык, шаг 4 м. |
| Нижний правый сектор | HRV-03 Red ×1, ATT-05 ×1, TRC-01 Red ×1, TRL-01 Empty ×1 | Собрать рабочую пару из Hero_Full: подборщик установлен, тягач с пустым кузовом под силосопроводом. |
| Дальний правый сектор: сменные жатки | HRV-01 Blue ×1, ATT-04 ×1, TRL-04 ×1, ATT-03 ×1 | Кукурузная жатка установлена на синий комбайн. На отдельной тележке зерновая жатка закреплена вдоль на Header_Rest. |
| Дальний край: зерноток | EQP-02 ×2, EQP-01 ×1 | Два одинаковых коротких бункера и отдельный транспортёр. Поставить его перед бункерами с габаритным зазором и сохранить проезд. |

## Camera and light

- Angle / height / FOV: 56° вниз, азимут 24° относительно дорожки, высота 42 м, вертикальный FOV 40°. Визир в центр межзонного проезда.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Плашки нет. Края свободны на 5%. Между зернотоком и рабочими связками нужен проезд не менее 5 м.

## Not in pack — remove

- Под выпуском серого шнека HRV-01 над TRL-05 видна короткая полупрозрачная жёлтая струйка. Убрать её в Unity, оставить лишь Load_Grain внутри перегрузчика.

## Поправки для постановки в Unity

- Шнек TRL-05 раскрыть на фактическом шарнире и оставить зазор до кузовов и шнека HRV-01. Точное положение брать из префаба CMP-04.
- Для тягача открытого HRV-02 и тягача TRL-05 использовать фактические TRC-02 Red и TRC-02 Green. Пропорции колёс в эскизе упрощены.
- В зоне кормоуборки один TRC-01 Red поставлен как тягач пустого TRL-01, рядом с HRV-03 и установленным ATT-05.
- Ограничить золотистый тон передней зоны до спокойной стерни. Оставить два валка из четырёх модулей с реальной высотой PRP-01.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: два перегрузчика вместо одного, IMP-04 и IMP-07 сложены, дополнительный поток зерна. |
| 2 | ImageGen, session model gpt-6.2-sol | Отклонено: валкователь раскрыт и лишний перегрузчик убран, но брус косилки оставался поднятым. |
| 3 | ImageGen, session model gpt-6.2-sol | Выбрано: пять зон, косилка и валкователь в рабочих позах, один перегрузчик, транспортёр отделён от бункера. Остаток струйки отмечен к удалению. |
| 4 | ImageGen, session model gpt-6.2-sol | Отклонено: локальная правка не убрала струйку и не уточнила сочленение шнека, сохранена третья попытка. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
