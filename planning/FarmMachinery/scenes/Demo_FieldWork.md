# Demo_FieldWork — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Demo / пространственная схема CMP-01–03 · Store files built from it: 10_DemoAndVersion (Lite/Full), ориентир для Э10
Reference image: `planning/FarmMachinery/scenes/Demo_FieldWork.png`

Кадрирование: 16:9, 1672 × 941 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: TRC-01, IMP-01, TRC-02, лист принятых превью lite-trailers, лист принятых превью lite-implements.

## Prompt (Codex, Sol 6.2)

```
A 16:9 landscape clean Unity staging layout viewed from 56° above, top-down oblique, three clearly separated zones on ONE uninterrupted horizontal texture-free plane, no thick diorama edge, no text, no labels. Lower left on a warm muted brown rectangular patch, one RED medium cab tractor with one correctly rear-mounted four-share plough, inputs 1 and 2. Centre-right on a pale tan straight route, one BLUE large equal-wheel tractor from reference 3 towing two identical RED tall-steel tipper trailers in a connected straight line, loaded golden grain in the first and empty second (sheet 4). The tipper trailer drawbars are physically hitched one behind the other, no gaps. Distant upper lane on pale muted sage colour, separate tidy parking rows: one GREEN medium cab tractor and one RED large equal-wheel tractor, one plain grey quick hitch and one red block front ballast from sheet 5, one red box seeder, one red folded-boom sprayer, one red upright transport mower, one red and grey disc harrow (wings fold up on both sides for transport), one grey cultivator with red hitch, all from sheet 5. Match the shapes, place visible tiny hitch and ballast with space around. One empty plank-deck flatbed and one facet red cylinder tank trailer from sheet 4 stand along the right edge of that same lane. Keep exactly three groups and use no other machinery or body colour variants. Soft daylight from upper left, ortho-like visualization showing the total inventory as actual low-poly objects, not icons or a map. No soil patterns, plants, fences, characters, bales, signs or scenery. All silhouettes intact within perimeter.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Нижний левый сектор (CMP-01) | TRC-01 Red ×1, IMP-01 ×1 | Плуг опущен и установлен на Link3P_Rear. Путь по широкой однотонной коричневой полосе. |
| Средняя правая полоса (CMP-02) | TRC-02 Blue ×1, TRL-01 Grain ×1, TRL-01 Empty ×1 | Оба самосвала одной модели на одной линии, гружёный первым за тягачом, второй пуст. Стыки Hitch_Rear → Hitch_Front. |
| Дальний двор, тягачи и навеска (CMP-03) | TRC-01 Green ×1, TRC-02 Red ×1, ATT-01 ×1, ATT-02 ×1 | Малую навеску выделить справа от больших машин в отдельные позиции. |
| Дальний двор, орудия (CMP-03) | IMP-02 ×1, IMP-03 Transport ×1, IMP-04 Transport ×1, IMP-05 Transport ×1, IMP-06 ×1 | Разложить от левого края к центру, сохранять проходы; IMP-05 со сложенными крыльями в Unity. |
| Дальний правый край двора (CMP-03) | TRL-02 ×1, TRL-03 ×1 | Платформа пуста, цистерна рядом в отдельном месте. |

## Camera and light

- Angle / height / FOV: 56° вниз, азимут 26° к продольной дорожке, высота 30 м над плоскостью, вертикальный FOV 37°. Визир в свободный просвет между тремя зонами.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Плашки нет. Просветы 3–4 м между группами, чистая рамка 5%.

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Поправки для постановки в Unity

- В Unity использовать однотонный материал для Load_Grain. Изображение даёт композицию двора, точную геометрию брать из префабов.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Выбрано: различимы CMP-01, цепочка CMP-02 и все одиннадцать позиций CMP-03. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
