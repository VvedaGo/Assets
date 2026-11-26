# CMP-04 — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — FountainParterre, отдельная виньетка для общей сетки и источник ракурсов деталей. Store files built from it — `12_Compositions, 07_Closeups`.
Reference image: `planning/CottageGardenDecor/scenes/CMP-04.png`

## Prompt (Codex, Sol 6.2)

```
Render the exact four-corner, one-fountain formal vignette of image 1 with the isometric-style southwest camera of reference 2, using only the camera from image 2. Same square frame, near-white warm background, lawn/earth and common 40-degree downward tilt, 30-degree azimuth away from direct front. The projected angle of the two front adjacent platform edges should clearly match reference 2. Keep the four identical L-shaped stone planted beds 2 by 2 m (one at each corner), the four rose standards and exactly four cones; cones must have the narrow straight planar silhouette, visible short trunk and brown ground disk in reference 3. One cream two-tier 2.42 m fountain in center. One thin low red sawtooth 6×6 m rounded-square perimeter, four straight 1 m runs per side joined by four R1 quarters. All four corners and whole lawn platform visible. No props from second reference, no extras or text.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Центр | WTR-01 ×1 | Фонтан Ø2,4 м и высотой 2,42 м, две чаши, непрозрачные диски и струи. |
| Четыре угла | FLB-02_Planted ×4, TOP-02 ×4, TOP-01_Rose ×4 | По одной Г-образной клумбе 2 × 2 м, одному конусу и одной штамбовой розе в каждом углу. |
| Периметр | MOD-05 ×16, MOD-06 ×4 | По четыре прямых модуля на сторону и одна дуга радиуса 1 м на угол. Габарит по оси 6 × 6 м. |

## Camera and light

- Ракурс, высота и FOV. Наклон 40° вниз, азимут 30° к фронту площадки, слабая перспектива близкая к ортографической, квадрат 1:1. Единая ориентация камеры для всех шести виньеток, высота и дистанция под габарит площадки, поля около 10%.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Сплошной тёплый светлый фон #F5F1E9, как у виньеток Farm Processing, и небольшой остров с ровным газоном.
- Свободная область. Поля по периметру, подписи размещаются отдельно при сборке сетки.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Читаются четыре клумбы, четыре штамбовые розы, четыре конуса на коротких стволах и фонтан. Количество прямых и дуговых элементов кольца задать по таблице, межмодульные стыки на PNG ненадёжны.
- Азимут PNG ближе к фронту, чем у CMP-02 и CMP-05. В Unity использовать общий шаблон камеры по разделу выше.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Фронтальный угол выбивается из серии виньеток, ограничитель слишком массивный. |
| 2 | Отклонена. Бордюр и ракурс улучшены, у конусов нет характерного короткого ствола и диска грунта. |
| 3 | Выбрана. Состав читается, конусы ближе к превью; общей камере понадобится выравнивание в Unity. |

## Fixes

<!-- The render reviewer appends fix sections. -->
