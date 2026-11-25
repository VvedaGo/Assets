# Card_Lite — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Card / композиция из CMP-01 · Store files built from it: 02_Card (Lite)
Reference image: `planning/FarmMachinery/scenes/Card_Lite.png`

Кадрирование: 3:2, 1536 × 1024 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: TRC-01, IMP-01.

## Prompt (Codex, Sol 6.2)

```
A 3:2 landscape Unity staging reference for the Lite card. Show exactly ONE compact red cab tractor with small front wheels and large rear wheels (first input) with exactly ONE four-bottom plough (second input) correctly coupled BEHIND the tractor at its rear three-point linkage, on the same soil plane. The nose faces toward the lower left of the composition. Render from 28 degrees above in three-quarter front-left and enough side angle to see the plough separately behind. Keep the complete connected tractor and plough centered horizontally in the upper 62% of the frame. Crucially the bottom 38% (from y=62% to bottom across the entire canvas) is a perfectly clean unobstructed single muted warm soil colour: place the lowest tyre and every small contact shadow ABOVE y=60%. Give the top 5% clear margin. The group is large and readable within that upper band, using up to about 72% of width. Uniform light blue-grey backdrop high in the frame, textureless warm soil beneath, minimal distant sage stubble tone if needed. Only this asset group. No graphic plate, letters, sign, crops or decorative props.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit input image one purely for the layout. Preserve precisely the machinery shape, colours, detailed connections and lighting. Keep the four-share plough linked to the rear of TRC-01 and lower it to working height so shares meet the soil. Scale the connected group down by around 20 percent, move above the middle so the topmost point sits at 7–9 percent of canvas height and the lowest model pixel and shadow are no lower than 57–58 percent down from the top. Top-to-bottom: light neutral sky or distant backdrop, still ground, object contained in the upper area, uninterrupted muted tan ground for all of the empty lower 40+ percent. This is a continuous ground plane; no foreground border, change of shade creating a plate, line, stripe, logo or text. Keep the output exactly 1536x1024 3:2 landscape. The second and third input images are the actual accepted model shape anchors.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Верхний центр, главный план | TRC-01 Red ×1, IMP-01 ×1 | Плуг закрепить на Link3P_Rear и опустить. Нос трактора влево и к камере. |
| Нижнее поле | — | Только спокойный цвет плоскости, без объектов и контактных теней. |

## Camera and light

- Angle / height / FOV: 28° вниз, азимут 36° от носа TRC-01, высота около 5,3 м, вертикальный FOV 34°. Поднять группу в кадре через смещение визира или кадрирование.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Снизу 38% всей ширины (y ≥ 62% высоты от верхнего края).

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: переднее колесо и тень заходили в нижнее поле, рабочая высота плуга читалась слабо. |
| 2 | ImageGen, session model gpt-6.2-sol | Выбрано: группа поднята в кадре, низ свободен, видно крепление и опущенный плуг. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
