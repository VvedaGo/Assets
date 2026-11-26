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
