# CMP-05 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — WalledPondCorner, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-05.png`

## Prompt (Codex, Sol 6.2)

```
Precisely restage the first image with the same square composition, aim 40° down and 30° from front, warm near-white matte backdrop and same object counts. Use the exact approved shapes in references 2 to 5. Lower the raised cream rectangular pond to a single thin skin of big blocks and trim so the top edge is 0.45 m and clearly lower than the 0.60 m wall. Water still a 3×2 field, opaque muted blue, with six equal TIGHT tiles flush so only subtle flat-shaded color changes, no dark grooves. Standard coping: exactly three straight top pieces on each long side plus two on each short side, plus four distinct small square corner blocks, not mitered diagonal corner seams. Retain one empty stone cup on pedestal, four stone ball pillars, four wall segments, two patches of ivy, one black iron arch and one wall fountain, matching approved warm off-white stone textures and thin black arch shape. Hard-flat stylized low-poly prototypes, no outlines or extra details. No added models or text.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Передний план | MOD-07 ×10, MOD-08 ×4, MOD-09 ×6 | Пруд 3 × 2 по внутренней сетке 1 м. Вода Y=0,38 м, борт Y=0,45 м. |
| Левый и задний края | MOD-03 ×4, MOD-04 ×4, STR-02 ×1 | По два звена на каждом плече. Столбы на левом конце, в углу и по обе стороны крайнего пропущенного пролёта задней стены. Арка 1,48 × 0,46 × 2,50 м в проёме. |
| Внутренняя сторона стены | WTR-02 ×1, PLT-04 ×2 | Стела 1,30 м вплотную к стене. Два пятна плюща на разных звеньях. |
| Передний край | ORN-03 ×1 | Пустая каменная урна на пьедестале 1,20 м. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Видны четыре столба, две аппликации плюща, свободная арка, стела и пустая урна. Шесть водных ячеек читаются по оттенкам. В Unity собрать прямые борта и углы из исходных мешей, выровнять копинг углов и воды по размерам каталога.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Пруд завышен, углы с диагональным резом, у воды тёмные стыки. |
| 2 | Выбрана. Пруд ниже стены, видны отдельные угловые блоки и 3 × 2 плиты без тёмных швов. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_2)
Problem: pond 68 % of the width is good, but the right half and the front (~30 % of the frame) are empty lime lawn; the composition (pond, wall, stela, arch, ivy, urn) is spread over a plinth about 1.6x too large; arch is at the far right edge of the group.
- Plinth: group bounding box + 0.7 m left/right/back, +1.0 m front (now ~3 m front, ~2.5 m right of the arch pillars); lowest plinth pixel at 88-92 % of the height, plinth 85-90 % of the width.
- Camera: closer so the group (wall + arch + pond) is 75-80 % of the width (the arch top must stay >= 5 % below the frame top); keep angle 30 deg off-axis, 36 deg down.
- Optional: move the iron arch 0.5 m towards the pond (only if the CMP-05 snap contract allows; otherwise keep).
- Lawn/backdrop/look: as in renders_2.md "Vignette rules".

## Fix 2 (2026-11-26, review renders_2 pass 2)
Reviewer decision: same policy as CMP-03 Fix 2 (16:9, same angle, prefab unchanged; fix the plinth and dolly the camera).
- Plinth: front margin (pond front wall to plinth edge) 1.0 m, now ~3 m (about 330 px); right margin (arch pillar to plinth edge) 0.8 m, now ~2 m; left/back 0.7 m. Plinth ~ 7.0 x 5.0 m.
- Camera: dolly closer so the arch top is at 5-6 % of the height and the plinth bottom at 90-93 %; expected zoom x1.25, group (wall + arch + pond) 72-78 % of the width, plinth 82-88 %.
- Acceptance: empty lawn in front of the pond <= 12 % of the frame height; the arch is fully inside the frame with >= 3 % margin to the right edge.
