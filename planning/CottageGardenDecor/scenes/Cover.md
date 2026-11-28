# Cover — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — Обложка Demo_CottageGarden и центрированный кроп для соцсетей. Store files built from it — `03_Cover, 04_Social`.
Reference image: `planning/CottageGardenDecor/scenes/Cover.png`

## Prompt (Codex, Sol 6.2)

```
Edit the first reference into the cover staging shot for the SAME garden layout as ref 2 (Hero), now re-rendered from east-northeast obliquely looking across a side of the island. Preserve from first reference its 3:2 frame, high-centred iconic 4 m red-shingle gazebo and diagonal path, grass island, clean faceted stylized geometry, pale blue sky and soft clouds. Lower 24% of frame must be entirely empty pale blue sky, with all island and models having their lowest point no lower than y=76%. Keep gazebo centered for a later social crop. Fix catalog props: remove the separate bare pergola behind/right; the garden has only one timber two-bay pergola with wisteria and dark bistro, west of central path across from fountain parterre. Remove any stone flowerpots under topiaries, topiaries grow directly from grass. Keep raised rectangular 3×2 pond on northwest with low L wall, four ball-cap pillars and black open curved iron arch between pillars (no gate in that arch). Replace invented water chute with the small cream semicircular stela fountain from reference three, on dry ground tight to wall. At fountain parterre use four low pale L-shaped flower beds as ref four planted with little faceted blooms, two-tier stone fountain, 4 cones plus 4 rose standards, all inside an outer rounded-square brick border. South entry arbor keeps red climbers and short white diamond lattice gate with curved top, a tiny gnome and two separate rose bushes just behind the two planted pale stone beds. Opposite the southern entrance across the path keep swing and matching striped loungers, blue/white hammock, white curved lattice bench, birdbath, wooden obelisk, two hanging dark hooks and insect hotel as ref five. In spaces between use only three empty stone bed shapes, one small white open trellis arbor, one white obelisk and one white chair and one white round table. No text, logo, plates, foreign props, houses, trees, people, animals.
```

## Zones and items

| Zone | Items (ID × count) | Notes |
|---|---|---|
| Юго-запад | CMP-01 ×1 | Калитка поперёк короткого ответвления, отдельный вход. |
| Юго-восток | CMP-06 ×1 | Качели в глубине зоны, гамак и шезлонги на открытой стороне газона. |
| Запад, средняя зона | CMP-02 ×1 | Пергола поперёк площадки, белые ширмы с тыла. |
| Восток, средняя зона | CMP-04 ×1 | Регулярный партер с центральным фонтаном. |
| Северо-запад | CMP-05 ×1 | Пруд за низкой стеной, просвет арки со стороны дорожки. |
| Северо-восток | CMP-03 ×1 | Беседка на ответвлении дорожки, вход развёрнут к развилке. |
| Между композициями | FLB-01 ×1, FLB-02 ×1, FLB-03 ×1, STR-01_White ×1, STR-07_White ×1, FUR-03_White ×1, FUR-04_White ×1 | Три пустые клумбы, белые арка и обелиск, один белый стол и один белый стул. |
| Ось юг–север | Демо-дорожка ×1 | Простая песочная полоса с короткими подходами, остров около 24 × 18 м. |

## Camera and light

- Ракурс, высота и FOV. Востоко-северо-восток, наклон 37° вниз, ориентир высоты 21 м, вертикальный FOV 39°, 3:2. Беседка в центральной трети.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Ясное голубое небо и редкие гранёные облака вверху, остров с открытым срезом земли.
- Свободная область. Нижние 24% — ровное небо. Для Social выделить центральную область 1200 × 630 с запасом по краям.

## Not in pack — remove

- Удалить лишний мини-партер между перголой и главной дорожкой: кирпичное кольцо, четыре засаженные Г-образные клумбы и два цветущих штамба. Это лишняя группа из похожих на каталог предметов.

## Проверка референса

- Беседка по центру, дорожка диагональная. Нижние ≈22,5% свободны под плашку, все предметы выше этой границы.
- В постановке снять ту же сборку, что для Hero, с другого угла. Сохранить положение зон по общей карте. Поставить две засаженные урны у перголы и восстановить остальные мелкие предметы и варианты по MD композиций. Бордюр подхода провести с обеих сторон ответвления к калитке.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Почти тот же фронтальный ракурс, чистого низа около 14%, беседка смещена от центра. |
| 2 | Отклонена. Центр и поле лучше, но есть вторая пергола, топиарии в нетипичных вазонах и выдуманный слив в пруд. |
| 3 | Выбрана. Центрированная беседка, чистая зона около 22,5%, лишнюю группу убрать по списку выше. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_1)
Problem: plate area is fine (free 24 %, island lowest point at 76 %: keep) but the garden is tiny and sparse: ~45 % of the island top is empty lawn (front left, front right, band behind the pond, below the path end), the gazebo is ~9 % of the frame width and its apex is 3 % from the top edge. It reads as a small island on a big sky, not as a cover.
- Island: same rebuild as Hero Fix 1 (top ~18 x 13.5 m, path scaled, garden >= 80 % of the top).
- Camera: keep the plate rule (every island/pack pixel above y = 988 px of 1300, band 988-1300 px empty sky). Closer, vFOV 30-32: island 90-94 % of 1950 px (x 3-97 %), lowest point at 74-76 %. Gazebo apex at 8-10 % of the height (now 3 %), gazebo 14-16 % of the width, x centre 50 +- 3 % (the social crop 1200x630 must contain gazebo and the path start). Top sky margin 6-8 % with 3-4 clouds not touching the gazebo.
- Angle: Cover.md says ENE; the assembler used SSW because the gazebo entrance faces SW (ENE shows its back). SSW is accepted, update the camera line here; keep it 30-40 deg yaw away from Hero.
- Densify as in Hero Fix 1. Move CMP-01 and CMP-06 2-3 m towards the front edge; the front 20 % of the island top holds >= 3 readable items.
- Lawn colour as Hero Fix 1. Nothing (clouds, items) below y = 76 %.
