# Card — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — Крупный вид RoseArchEntrance и силуэт арки для иконки. Store files built from it — `02_Card, 01_Icon`.
Reference image: `planning/CottageGardenDecor/scenes/Card.png`

## Prompt (Codex, Sol 6.2)

```
Precisely edit ONLY three details of the first image, preserving square-topped arbor, one white lattice gate, roses mounted on it, two planted stone beds, canvas 3:2, composition, sky, island silhouette and clear bottom 40%. (1) Remove the two outer duplicate lines of red edging. Keep just one narrow red strip on each of the two sides of the sandy path; each strip consists of two inline connected 1 m segments, and the bricks are tilted up at 45 degrees making teeth, as third reference. Exactly TWO visible continuous rows. (2) Replace both spherical rose bushes with the faceted OPEN vase-shaped rose mesh of ref 2, red left and pink right. Keep them rooted behind the beds. (3) Scale the tiny gnome statue on right down approximately 25%, retaining his excellent original geometry. No other changes or added objects. Preserve warm matte flat shaded low-poly appearance.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Вход | STR-01_Gate ×1, PLT-02 ×2, PLT-03 ×1 | По красной плети на боковину, красная гирлянда на плоском реечном верху. Белая створка в проёме. Арка с гирляндой 2,94 м. |
| Обе стороны | FLB-01_Planted ×2, PLT-01 ×1, PLT-01_Pink ×1 | По одной клумбе 2 × 1 м и кусту высотой 1,09 м с каждой стороны. Красный куст слева, розовый справа. |
| Подход | MOD-05 ×4, ORN-02 ×1 | По два последовательно состыкованных модуля вдоль каждого края дорожки. Гном 0,45 м справа. |

## Camera and light

- Ракурс, высота и FOV. Почти фронтально с небольшим поворотом, наклон 36° вниз, ориентир высоты 5 м, вертикальный FOV 35°, 3:2.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Ясное голубое небо, мягкие облака в верхних углах, небольшой остров на срезе земли.
- Свободная область. Нижние 38% — свободное небо. Под иконку выделить арку со створкой и розами, центрировать силуэт.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Весь остров над y≈60%, свободны нижние ≈40%. Створка и розы образуют единый силуэт.
- Две палисадные линии читаются. Стыки четырёх MOD-05 в изображении неразличимы, ставить по два элемента в линию по схеме.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Свободно только около 26% снизу, бордюр разошёлся в четыре ряда, кусты слиты в шары. |
| 2 | Отклонена. Нижние 40% свободны, но удвоенные ряды и шаровидные кусты сохранились, гном крупный. |
| 3 | Выбрана. Две линии бордюра, отдельные гранёные кусты и меньший гном, свободно около 40% снизу. |

## Fixes

<!-- The render reviewer appends fix sections. -->
