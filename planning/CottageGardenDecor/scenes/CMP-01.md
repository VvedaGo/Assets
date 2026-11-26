# CMP-01 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — RoseArchEntrance, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-01.png`

## Prompt (Codex, Sol 6.2)

```
undefined Re-stage only this composition RoseArchEntrance, approximate footprint 4×3 meters. One flat-top tan slatted wooden arbor with diagonal wooden lattices on sides and short single rounded-top white lattice gate leaf. Exactly 2 red climbing roses (discrete angular leaf drops on bare tan stems), one on each side, and one red garland on roof slats. Exactly 2 low 2×1 m straight rectangular cream stone-block beds with small pink, white, lilac, and yellow angular flower clumps rooted inside. Behind each bed one separate vase-shaped rose bush, red left, pink right, each 1.09 m high, clearly angular leaf drops and bare brown stems. Four 1 m straight red sawtooth brick strips, joined into two inline runs, one per side of the simple sand approach. One tiny 0.45 m red-hat blue-coat gnome standing outside right bed; arbor with garland 2.94 m high. Single square image 1:1, each composition on its own shallow flat grass-topped brown earth rectangle with lightly clipped corners. Sparse plain lawn, no loose foliage, rocks or props; a short flat tan demo path only if necessary. Common view across all vignettes: azimuth 30 degrees from direct front, tilt down 40 degrees, weak perspective close to orthographic. Centered with calm margins, seamless solid warm near-white background #F5F1E9. Last reference is Farm Processing series framing and palette only. No text, plates, clouds or branding.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Вход | STR-01_Gate ×1, PLT-02 ×2, PLT-03 ×1 | По красной плети на боковину, красная гирлянда на плоском реечном верху. Белая створка в проёме. Арка с гирляндой 2,94 м. |
| Обе стороны | FLB-01_Planted ×2, PLT-01 ×1, PLT-01_Pink ×1 | По одной клумбе 2 × 1 м и кусту высотой 1,09 м с каждой стороны. Красный куст слева, розовый справа. |
| Подход | MOD-05 ×4, ORN-02 ×1 | По два последовательно состыкованных модуля вдоль каждого края дорожки. Гном 0,45 м справа. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Арка, две боковые плети, гирлянда, створка, две клумбы, два куста, гном и два ряда бордюра читаются. Точные стыки четырёх MOD-05 на PNG неразличимы. Клумбы установить по высоте каталога 0,25 м.

| Генерация | Результат |
|---:|---|
| 1 | Выбрана. Все группы читаются, характерные силуэты совпадают с превью. |

## Fixes

<!-- The render reviewer appends fix sections. -->
