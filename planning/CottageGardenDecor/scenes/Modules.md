# Modules — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — Пять собранных модульных систем. Store files built from it — `08_VariantsAndModules, собранная часть`.
Reference image: `planning/CottageGardenDecor/scenes/Modules.png`

## Prompt (Codex, Sol 6.2)

```
Make a surgical edit to the existing first image preserving the camera, all five example positions, format, water and stone joints and all objects except the pergola posts. In the tan pergola, at EACH supporting node delete the duplicated extra square rod. Each location should show one clean vertical square post, with exactly SIX upright posts overall; the long front beam is supported by EXACTLY THREE separated posts: left end one, middle one, right end one. The rear beam also has EXACTLY THREE posts at corresponding positions. No crossing diagonal braces, no extra support near existing posts. Two smooth bays with one shared pair of square posts. Reuse the intended engineering of preview references 2 and 3. Retain four separate wisteria clusters fixed into the lower beam. Do not add props; keep the front-left pond, back-left two-part wall, front-center rounded brick ring, front-right white lattice panels as is.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Спереди слева | MOD-07 ×10, MOD-08 ×4, MOD-09 ×6 | Приподнятый пруд 3 × 2 м внутри, борта по сетке 1 м, вода на 7 см ниже копинга. |
| Сзади справа | STR-04 ×1, STR-05 ×1, PLT-05 ×4 | Продление 3 м, одна общая пара стоек, глициния под балкой на 2,24 м. |
| Спереди по центру | MOD-05 ×4, MOD-06 ×4 | Кольцо со скруглёнными углами, одна метровая прямая на сторону и четыре четверти окружности радиуса 1 м. |
| Сзади слева | MOD-03 ×2, MOD-04 ×3 | Два двухметровых звена в линию, столбы на концах и шве. |
| Спереди справа | MOD-01 ×2, MOD-02 ×3 | Два пролёта по 2 м с общим столбом. |

## Camera and light

- Ракурс, высота и FOV. Юго-восток, наклон 43° вниз, ориентир высоты 14 м, вертикальный FOV 35°, широкий кадр.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Тёплый светлый нейтральный фон #F5F1E9, низкий срез земли с простым газоном.
- Свободная область. Поля по периметру и пространство между пятью сборками.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Пять узлов на отдельных участках, у перголы три пары стоек с одной общей средней парой. Вода читается как 3 × 2. Точное число деталей борта и шаг кирпичных зубцов сверить по сетке и строкам таблицы, швы на изображении намеренно слабо различимы.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. У перголы удвоена передняя средняя стойка, у воды слишком тёмные швы, глициния стилизована одиночными кистями. |
| 2 | Отклонена. Вода и глициния ближе к превью, но генерация удвоила несколько стоек. |
| 3 | Выбрана. Шесть стоек, четыре подвеса, все пять сборок различимы. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_2)
Problem: five systems are placed 2-4 m apart on one long plinth; the pergola and the pond are readable but the pond, wall, ring and lattice are small and the middle of the plinth is empty lime lawn (about 45 % of the plinth area). The brick ring is an empty ring on bare grass (acceptable as a module demo).
- Layout (demo only): keep the arrangement but reduce gaps between systems to 0.8-1.2 m; target plinth 88-92 % of the frame width, lowest plinth pixel at 90 % of the height, empty lawn <= 25 % of the plinth.
- Arrangement: back row pergola (right) + two-part wall (left); front row pond (left), ring (centre), lattice (right), as now; move the ring 1 m closer to the pond and lattice, wall 1 m closer to the pergola.
- Camera: closer so the plinth is 88-92 % of the width; elevation 40-43 deg down (Modules.md: 43 deg, SE); keep vFOV 32-35.
- Backdrop per Modules.md: warm light neutral #F5F1E9 (assembler used #E5E4E2; use #EFEBE4 as a compromise for contrast with the white lattice/stone), lawn as in renders_2.md "Vignette rules".

## Fix 2 (2026-11-26, review renders_2 pass 2)
Items are readable at 75 % of the width, but ~35 % of the plinth is empty lawn: back-left (above the pond/wall), the centre between the ring and the pergola, and the right-front corner. Reviewer decision: fix by tightening the demo arrangement (placement of the five systems on the plinth, not the systems themselves) and the plinth outline.
- Move the wall 1.0 m towards the pergola and the pond 0.8 m right/back (towards the wall); move the ring 1.0 m right and 0.5 m back (towards the lattice); the lattice 0.5 m left. Gaps between systems 0.8-1.2 m.
- Plinth: left/back/right margins 0.7 m, front 0.9 m (outline follows the group, rounded rectangle, bounding ~ 14.5 x 8.5 m instead of the current ~17 x 10 m).
- Camera: dolly closer to get plinth 84-88 % of the width, pergola top at 5-6 %, plinth bottom at 92 %.
- Acceptance: empty lawn <= 25 % of the plinth area; every system >= 12 % of the frame width (lattice and ring are now ~11 %).
