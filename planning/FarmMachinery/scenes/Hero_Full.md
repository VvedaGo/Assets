# Hero_Full — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5): Hero / зерновая и кормовая уборка Full · Store files built from it: 05_Hero (Full)
Reference image: `planning/FarmMachinery/scenes/Hero_Full.png`

Кадрирование: 16:9, 1672 × 941 px.
Референс постановки для Unity (MKT-01). Опорные изображения моделей из `art/FarmMachinery/Previews/`: лист принятых превью grain-harvest, лист принятых превью forage-harvest, лист принятых превью hay-harvest, лист принятых превью grain-yard, HRV-01.

## Prompt (Codex, Sol 6.2)

```
Wide 16:9 landscape single-frame Unity staging reference, elevated front oblique camera 41° down. Four separate but continuous flat ground zones, no visible dividers or boxes. Large foreground LEFT and center: exact red grain combine from sheet 1 and image 5 with the wide red ATT-03 steel cylindrical reel header physically mounted on its front, silver side unload auger swung outward horizontally over the open trapezoid red TRL-05 cart. That cart is the single giant tyre per side type, trails one GREEN four-equal-wheel TRC-02 and has a low gold grain load. Exact body and tyres from the references. Foreground but behind on right: exact shorter red forage harvester HRV-03 with one narrow ATT-05 pickup mounted at front and high bent red spout aimed down into one empty red TRL-01 tipper, which is correctly towed by one smaller RED TRC-01, sheet 2. Distinct groups parallel, same heading, space between. Use visual posture to imply unloading, with no rendered particle streams. On the distant LEFT muted sage lane, separate recognizable round red closed HRV-02 baler and unfold the two grey IMP-07 rake rotors level in work pose; two parallel straight straw-gold windrows each formed by two joined PRP-01 flat modules, sheet 3. On the FAR RIGHT edge, only two short broad corrugated grey cylindrical EQP-02 bins with low gray cone roofs and one diagonal grey/red EQP-01 conveyor nearby, sheet 4. Low-poly matte exact input object shape; backs of smaller groups visible. No hay bales, no signs, no dust, no trees, no crop plants or texture clumps, no other props. Background is a high narrow strip of light neutral sky. Uniform matte earth, pale stubble paint and sage paint zones on a single texture-free plane.

Use only the catalog models specified, treat individual input images as exact geometry and colour references, never reuse their isolated backgrounds. Actual Blender preview proportions and construction must win over stylized interpretations. Muted red #C8473B, opaque blue-grey windows, dark tread blocks and cream solid rims, simple hard-edged geometry; limited cool gray-blue sky gradient if visible, texture-free ground in two or three calm flat tones, soft daylight from upper left, subtle contact shadows only, wheels and implements seated on the same plane. Pure concept stage reference for Unity scene placement, no type or poster graphics. Return the requested landscape ratio with full silhouettes.

Edit prompt for the selected generation:
Input 1 is the draft composition to correct, the following four image sheets are official exact models for grain, forage, hay, yard in that order. Keep all four existing zones and machines and nothing else. Repaint the LARGE foreground tractor towing the red trapezoid grain cart GREEN atlas #6E9F4A. It is the larger four-equal-size-wheel tractor; retain the SMALL second tractor towing the tall red tipper in red. At upper left keep the closed red baler and the two-rotor rake SEPARATE. Delete any thin line or stray connecting bar between them. Rotate the rake's two booms DOWN and out into its working pose, with BOTH circular star rotor planes lying horizontal, no upright spokes. Keep the two PRP windrows in two parallel lines, two bins and single auger and all other machines in location. Aim the forage outlet into the empty tipper but shorten its curved spout to match the accepted photo, by positioning tipper a little nearer if necessary, without collision. No particulate streams. Move the wide header just enough inward so the full scene has more breathing room from left edge. Exact nominal 16:9 landscape, clean flat ground and sky.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Передний левый план: зерно | HRV-01 Red ×1, ATT-03 ×1, TRC-02 Green ×1, TRL-05 Full ×1 | Жатку установить на Feeder_Front. Перегрузчик на Hitch_Rear трактора, слева от комбайна по стороне шнека. Раскрыть шнек комбайна, Auger_Out над центром перегрузчика. Шнек TRL-05 сложить, чтобы у связки была одна линия выгрузки. |
| Средний правый план: кормоуборка | HRV-03 Red ×1, ATT-05 ×1, TRC-01 Red ×1, TRL-01 Empty ×1 | ATT-05 установлен на Feeder_Front. Параллельные маршруты, носы смотрят в одну сторону. Силосопровод повернуть к кузову, наконечник над бортом. |
| Дальний левый план: сенокос | HRV-02 Closed ×1, IMP-07 Work ×1, PRP-01 ×4 | Пресс на опоре, камера пуста. Валкователь раскрыт. Два валка по два модуля, стык 4 м. |
| Дальний правый край: зерноток | EQP-02 ×2, EQP-01 ×1 | Два бункера на дальнем краю. Транспортёр вдоль края площадки, рядом, с зазором от корпуса бункера. На общей плоскости выпуск находится ниже люка. |

## Camera and light

- Angle / height / FOV: 41° вниз, азимут 34° к переднему проходу, высота 26 м над плоскостью, вертикальный FOV 35°. Визир на зерновую связку в левом центре.
- Light: мягкий дневной ключ сверху слева, холодное рассеянное заполнение, короткие мягкие контактные тени.
- Background: одна ровная плоскость с двумя или тремя плоскими цветами — почва, стерня, короткая трава. Светлый серо-голубой фон, если виден горизонт.
- Free area for plates: Плашки нет. Чистый край кадра 5% по периметру.

## Not in pack — remove

- Посторонних объектов в выбранном кадре не обнаружено.

## Поправки для постановки в Unity

- Оставить зазор между выпуском EQP-01 и корпусом EQP-02. Референс задаёт соседство, уровень люка выше выпуска транспортёра на общей плоскости.
- Сведение Spout_Out с кузовом выполнить поворотом принятого силосопровода и более тесной параллельной постановкой тягача, сохранив форму и длину трубы HRV-03.

## Generations

| # | Settings | Result |
|---|---|---|
| 1 | ImageGen, session model gpt-6.2-sol | Отклонено: тягач перегрузчика был красным, роторам оставлена транспортная поза, между прессом и валкователем лишняя штанга. |
| 2 | ImageGen, session model gpt-6.2-sol | Выбрано: зелёный TRC-02, две линии выгрузки, рабочий валкователь, два валка из четырёх модулей и зерноток. |

## Fixes

<!-- The render reviewer appends "## Fix N (<date>)" sections. -->
