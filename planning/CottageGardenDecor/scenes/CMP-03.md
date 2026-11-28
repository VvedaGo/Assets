# CMP-03 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — GazeboRetreat, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-03.png`

## Prompt (Codex, Sol 6.2)

```
Match exactly the warm off-white square background, clipped grass slab, 40° down 30° azimuth camera and placement in first image. Change two foreground rose bushes from pink to WHITE (creamy white faceted rose cups) and model the open vase shaped bare woody stems and spherical angular leaf drops from ref 3. Keep the walk-through flat tan wood arbor STR-01 with exactly two separated pink climbing meshes, one on each side lattice, like ref 5 with pink blooms. Keep one round planted stone bed placed clearly OFF the path to its right, so it does not block the approach. Replace the slabbed path with an unbroken flat plain sand walk under the entrance. Keep the two spirals, replace the two rounded cone topiaries with straight triangular silhouettes per the exact cone mesh in ref 4. Retain precisely two pink and one cream-white distinct tall hollyhock groups. Match ref 2 gazebo closely, including shallow front steps, red faceted shingle roof, six open sides, trim rails and seats in approved shape only. No new props or plants, no stones or tiles on the path, no text.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Главный план | STR-06 ×1, TOP-03 ×2, TOP-02 ×2 | Беседка 3,58 × 3,58 × 4 м. Спирали ближе к задним углам, конусы перед боковыми перилами. |
| Подход | STR-01 ×1, PLT-02_Pink ×2 | Открытая деревянная арка на оси входа, по розовой плети на боковину. |
| Цветы | FLB-03_Planted ×1, PLT-06 ×2, PLT-06_White ×1, PLT-01_White ×2 | Круглая клумба справа от прохода. Две розовые и одна белая куртины мальвы по 1,80 м по бокам, два белых куста по 1,09 м у передних углов. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Две спирали, два конуса, три группы мальвы и оба белых куста читаются. При постановке взять утверждённый STR-06 с собственными перилами, настилом и ступенями, фаски и толщину по превью.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Оба куста розовые вместо белых, клумба прерывает подход, конусы скруглены. |
| 2 | Выбрана. Варианты роз и мальвы различимы, проход к беседке свободен. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_2)
Problem: the gazebo group is 54 % of the width, the lower ~35 % of the frame is empty lime lawn (plinth front margin ~4 m), items on the left and right are small.
- Plinth: crop to the group bounding box + 0.7 m on the left/right/back and +1.0 m in front (front margin now ~4 m); the plinth should take 85-90 % of the frame width, the lowest plinth pixel at 88-92 % of the height, the gazebo finial at 5-7 % of the height.
- Camera: same angle (30 deg off-axis, 36 deg down); distance/vFOV so the group (gazebo + arbor + obelisk + bed + topiary) is 62-68 % of the width; if the gazebo hits the frame height first, accept 60 %.
- Fill the plinth edge zones only with items from the composition (move bed and topiaries 0.5-1 m closer to the gazebo); no extra items.
- Lawn/backdrop/look: see renders_2.md "Vignette rules" (lawn lit ~#86C24A, backdrop warm #EFEBE4).

## Fix 2 (2026-11-26, review renders_2 pass 2)
Reviewer decision (framing policy): keep the 16:9 frame, the angle (30 deg off-axis, 36 deg down) and the composition prefab unchanged. Fix the plinth (demo asset, scaled per vignette in the wrapper), not the prefab.
- Plinth: front margin (gazebo steps to the plinth front edge) 1.0 m, now ~3.5 m (about 400 px of 1080); left margin 0.7 m, right 0.7 m, back 0.7 m. Result plinth ~ 8.0 x 5.5 m; the plinth centre moves to the group centre.
- Camera: once the plinth is shorter, move the camera closer (dolly, not FOV change) until the finial is at 5-6 % of the height and the plinth bottom at 90-93 %: expected zoom x1.25-1.3, group 60-64 % of the width, plinth 80-86 %.
- Acceptance: plinth area not occupied by items <= 45 %; no lawn band in front of the gazebo steps taller than 12 % of the frame height.
