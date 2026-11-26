# CMP-06 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — WildlifeLawn, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-06.png`

## Prompt (Codex, Sol 6.2)

```
undefined Re-stage only this composition WildlifeLawn, approximate footprint 8×6 meters. A timber A-frame swing bench back left (four suspension rods), white shallow curved lattice arbor with built-in tan bench back right, one slender four-legged wooden pyramid obelisk with a round finial. Foreground left one blue-and-white striped hammock on a low curved wooden cradle (3.06 m long, 1.1 m high). Near foreground center exactly two plain matching folding fabric deck chairs on wood frames, red/cream and blue/cream. On right one shallow beige stone birdbath with opaque blue disk, one stone and black metal sundial, one tiny blue-cap red-coat garden gnome, one wooden insect hotel with open visible cells and gabled roof 0.88 m tall. Two thin dark curled shepherd hooks, one with flower basket and one with cylindrical bird feeder. Exactly two three-tier ball topiary standards and one one-ball standard, each with a bare stem. No live creatures. Single square image 1:1, each composition on its own shallow flat grass-topped brown earth rectangle with lightly clipped corners. Sparse plain lawn, no loose foliage, rocks or props; a short flat tan demo path only if necessary. Common view across all vignettes: azimuth 30 degrees from direct front, tilt down 40 degrees, weak perspective close to orthographic. Centered with calm margins, seamless solid warm near-white background #F5F1E9. Last reference is Farm Processing series framing and palette only. No text, plates, clouds or branding.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Задняя полоса | FUR-01 ×1, STR-03 ×1, STR-07 ×1, TOP-04 ×2 | А-качели 2,48 × 1,50 × 2,16 м слева, белая арка-скамья справа. Обелиск и два трёхъярусных топиария по краям. |
| Отдых спереди | FUR-02 ×1, FUR-05 ×1, FUR-05_Blue ×1 | Гамак 3,06 × 0,90 × 1,10 м слева, два складных шезлонга с красной и синей полосой по центру. |
| Правая сторона | WTR-03 ×1, ORN-01 ×1, ORN-02_Blue ×1, ORN-04 ×1, ORN-05 ×1, ORN-05_Feeder ×1, TOP-01 ×1 | Поилка 0,70 м, часы, статуэтка с синим колпаком, домик для насекомых, корзина и кормушка на двух отдельных крюках, один шар на штамбе. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Видны оба варианта шезлонга, оба отдельных крюка, все три топиария и остальные предметы. У топиариев на PNG слишком мелкая гранёность. В Unity использовать гладкие крупные грани мешей TOP-01 и TOP-04.

| Генерация | Результат |
|---:|---|
| 1 | Выбрана. Число предметов читается, включая две расцветки шезлонга и два подвеса. |

## Fixes

<!-- The render reviewer appends fix sections. -->
