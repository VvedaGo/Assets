# Cover_Lite — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Cover / обзор машин и орудий Lite · Store files built from it: 03_Cover (Lite)
Reference image: `planning/FarmMachinery/scenes/Cover_Lite.png`

Кадрирование: 3:2, 1536 × 1024 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: TRC-01, TRC-02, лист принятых превью lite-implements, лист принятых превью lite-trailers.

## Prompt (Codex, Sol 6.2)

```
3:2 landscape overview composition for Unity staging of a Lite cover. One most prominent compact RED cab tractor TRC-01 from input 1 at front-center, nose toward the left front, clearly bigger in the composition by proximity. Secondary nearer the right but deeper: one BLUE TRC-02 from input 2 towing exactly one empty red steel high-wall tipper TRL-01. A farther left diagonal shows exactly four implements from the reference sheet: box-shaped red seeder IMP-02, folded-boom red sprayer IMP-03, raised upright red side disc mower IMP-04 and gray three-row cultivator IMP-06 with red hitch and roller. Far back: one long empty wood-deck low platform TRL-02 and one red faceted liquid tanker TRL-03. Exactly the listed models, do not include other sheet items or labels. Quiet stage on a flat warm soil / pale stubble / gray-green patch plane, light neutral sky band high up. All asset geometry and all contact shadows completely above y=73% of the frame, with bottom 25% an uninterrupted solid warm muted earth tone without any object, text, plate graphic, gradient stripe or hard boundary. Keep clean left and right margins. Hierarchy of depth; no other machines or environmental props.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit prompt for the selected generation:
Input 1 is the draft image to edit. Preserve the locations, exact count, colour, size, poses and design of all 9 machines; the other four images are the true approved model anchors. Remove EVERY plant blade, grass tuft, ground speckle, texture or terrain noise on the entire plane. Ground should become completely smooth, textureless and flat with at most one quiet sage area beyond foreground and warm tan soil in front. Keep that continuous uniform tan ground on the whole lower quarter without a straight graphic strip or shadow there. Move the red main tractor and its contact shadow about 3% up if needed so the entire bottom 25% is empty. No additions. Keep the sky, angle and landscape 1536x1024 ratio.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Верхний центр, ближний ряд | TRC-01 Red ×1 | Главный акцент. Нос налево, свободный силуэт, передний ряд. |
| Верхняя правая диагональ | TRC-02 Blue ×1, TRL-01 Empty ×1 | Прицеп сцепить с большим трактором. Сместить глубже главного акцента. |
| Верхний левый сектор | IMP-02 ×1, IMP-03 Transport ×1, IMP-04 Transport ×1, IMP-06 ×1 | Разнести орудия в ряд с просветами. |
| Верхний дальний ряд | TRL-02 ×1, TRL-03 ×1 | Пустая платформа и цистерна закрепляют дальнюю диагональ. |
| Нижняя четверть | — | Сплошная спокойная плоскость без моделей. |

## Camera and light

- Angle / height / FOV: 34° вниз, азимут 27° к диагонали парка, высота 18 м, вертикальный FOV 38°. Визир поднять относительно главного ряда.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Снизу 25% всей ширины (y ≥ 75% высоты).

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Поправки для постановки в Unity

- TRC-02 узнаётся по корпусу и крупным колёсам. В Unity сохранить передние тяги принятого TRC-02.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: на плоскости появились пучки травы и фактура стерни. |
| 2 | ImageGen, session model gpt-6.2-sol | Выбрано: сохранены девять моделей, плоскость без растительности, низ свободен. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
