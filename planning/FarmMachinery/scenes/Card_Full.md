# Card_Full — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Card / ведущий комбайн Full · Store files built from it: 02_Card (Full)
Reference image: `planning/FarmMachinery/scenes/Card_Full.png`

Кадрирование: 3:2, 1536 × 1024 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: HRV-01, ATT-03.

## Prompt (Codex, Sol 6.2)

```
A 3:2 landscape Full card staging reference. Exactly ONE red grain combine from the first reference with ONE grain header from the second reference mounted cleanly onto the projecting front feeder, centred and low immediately ahead of the cab. The broad red header is wider than the combine and contains the exact steel-gray eight-sided open reel and front cutter, not pointed corn snouts. Keep the combine's compact boxy body, muted cream wheels, opaque blue-grey glass, flat rooftop and silver unloading auger folded along the upper side. Entire assembly, close easy-to-read front-left three-quarter from 28° above. Place the entire assembly centered horizontally within the TOP 62% of the picture, margins at top and sides and lowest contact point and all shadows above y=60%. Make the BOTTOM 38% completely empty unbroken muted soil colour across full width. No object, horizon, decal, shadow, border or graphic in that lower band. Subtle light sky / neutral gray-blue horizon high up and warm clean muted soil, matte faceted models, no other equipment.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit input image one purely for the layout. Preserve precisely the machinery shape, colours, detailed connections and lighting. Keep the red HRV-01 and its same ATT-03 assembly physically connected and fully visible. Scale the connected group down by around 20 percent, move above the middle so the topmost point sits at 7–9 percent of canvas height and the lowest model pixel and shadow are no lower than 57–58 percent down from the top. Top-to-bottom: light neutral sky or distant backdrop, still ground, object contained in the upper area, uninterrupted muted tan ground for all of the empty lower 40+ percent. This is a continuous ground plane; no foreground border, change of shade creating a plate, line, stripe, logo or text. Keep the output exactly 1536x1024 3:2 landscape. The second and third input images are the actual accepted model shape anchors.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Верхний центр, главный план | HRV-01 Red ×1, ATT-03 ×1 | Жатка установлена на Feeder_Front, используется одна сборка. Шнек сложен. |
| Нижнее поле | — | Только спокойная плоскость, без механики и теней. |

## Camera and light

- Angle / height / FOV: 28° вниз, азимут 36° от носа, высота около 7,0 м, вертикальный FOV 34°. Поднять сборку относительно центра кадра.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Снизу 38% всей ширины (y ≥ 62% высоты).

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: край жатки заходил в нижние 35% кадра, горизонтальная граница имитировала плашку. |
| 2 | ImageGen, session model gpt-6.2-sol | Выбрано: одна сборка с зерновой жаткой, чистая цельная нижняя зона. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
