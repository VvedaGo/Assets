# Cover_Full — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Cover / обзор линейки Full · Store files built from it: 03_Cover (Full)
Reference image: `planning/FarmMachinery/scenes/Cover_Full.png`

Кадрирование: 3:2, 1536 × 1024 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: HRV-01, лист принятых превью grain-harvest, лист принятых превью forage-harvest, лист принятых превью hay-harvest, лист принятых превью grain-yard.

## Prompt (Codex, Sol 6.2)

```
3:2 landscape cover overview staging reference, one biggest machine. Upper central foreground: the exact RED HRV-01 body from direct reference 1 with one wide red ATT-03 reel header mounted from sheet 2, folded gray auger and largest in composition. Set it safely above y=73% by moving all machines upward. Upper mid left: one RED HRV-03 from sheet 3 with distinctive curved red chute and mounted narrow red ATT-05 pickup head. Upper mid right: one GREEN broad four-equal-wheel TRC-02 (sheet 2) towing one empty red large single-axle TRL-05 cart, its unload pipe folded against the cart. In small left rear cluster from sheet 4: one red closed HRV-02 baler, one folded steel and red IMP-07 with two raised rotors and one empty open wooden-deck TRL-06 bale platform with red lattice end boards. At far right: one wide gray EQP-02 low conical roof grain bin and one separate steel-gray diagonal EQP-01 conveyor with red hopper (sheet 5). Show no other models than these, focus on clean spacing and only one focus. Sky light and neutral. Bottom 25% of the entire picture is a flat solid calm sand brown part of the continuous ground plane, absolutely no asset pixel or shadow in it, no distinct graphic/stripe, no text. Everything else stays in upper three quarters with enough margins. Ground elsewhere two additional flat warm-tan and muted sage patches with no clutter, plant texture or pattern. No bales.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit prompt for the selected generation:
Input 1 is the draft image to edit, other inputs are true models. Preserve each of the 11 model IDs/placements, their scale, the main combine's mounted reel header, figure and palette. Remove the horizontal tan strip at bottom that looks like a graphic plate. Make one continuous matte tan plane under the combine and for the whole foreground, with no stripe or line across the canvas. Shift the entire model scene 4% up in frame or modestly back to leave 24–25% of the frame height towards the bottom with no geometry or shadow at all. No text or graphic. Keep exact same range with one main focus, and 1536x1024 landscape.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Верхний центр, главный план | HRV-01 Red ×1, ATT-03 ×1 | Главный силуэт. Жатка на комбайне, шнек сложен. |
| Слева, средний план | HRV-03 Red ×1, ATT-05 ×1 | Подборщик смонтирован, силосопровод в транспортном положении. |
| Справа, средний план | TRC-02 Green ×1, TRL-05 Empty ×1 | Трактор с перегрузчиком, шнек TRL-05 сложен. |
| Верхний левый край | HRV-02 Closed ×1, IMP-07 Transport ×1, TRL-06 ×1 | Пресс и платформа пусты. Валкователь со сложенными роторами. |
| Верхний правый край | EQP-02 ×1, EQP-01 ×1 | Низкий металлический зерновой бункер и шнековый транспортёр. |
| Нижняя четверть | — | Сплошная незатенённая плоскость. |

## Camera and light

- Angle / height / FOV: 33° вниз, азимут 34° к главному комбайну, высота 22 м, вертикальный FOV 38°. Главная сборка смещена вверх в пределах рабочего кадра.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Снизу 25% по всей ширине (y ≥ 75% высоты).

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Поправки для постановки в Unity

- Для техники среднего и дальнего планов использовать силуэты и размеры принятых моделей.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: нижняя полоса выглядела как нарисованная плашка. |
| 2 | ImageGen, session model gpt-6.2-sol | Выбрано: один главный комбайн, все одиннадцать позиций и чистая нижняя четверть. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
