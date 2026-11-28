# Hero — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — Обзор Demo_CottageGarden с беседкой в качестве главного фокуса. Store files built from it — `05_Hero`.
Reference image: `planning/CottageGardenDecor/scenes/Hero.png`

## Prompt (Codex, Sol 6.2)

```
Keep the first image, same overall garden island layout, strongly identifiable six named zones, blue sky and fluffy faceted clouds, 16:9 from south-southeast 40 degrees down. Pull back slightly for stronger sky margins and mesh silhouettes. Fix exact approved props in existing locations: by the gated rose arbor add a tiny approved red-cap blue-coat statue and two inline sawtooth red brick strips beside path; move separate red and pink rose bushes behind the two low beds of mixed-colored planted small flowers. The freestanding white arbor at back is a painted version of ref 2, two white lattice side walls. Move one narrow wooden pyramid obelisk to underused open far right next to bench arbor. Add the small stone birdbath (ref 4) near the chairs and one thin curled dark shepherd hook with a cylindrical feeder next to the flower basket hook; keep insect hotel. At parterre, change the four rectangular beds to the L-shaped footprint in ref 5, and move the continuous red rounded-square edging outside all four beds. Keep one six-sided open gazebo with red shingles and its rose entrance framing as the clear highest focal point. Delete no other existing catalogue items, add no items besides these, no text.
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

- Ракурс, высота и FOV. Юго-юго-восток, наклон 40° вниз, ориентир высоты 22 м, вертикальный FOV 35°, широкий кадр.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Ясное голубое небо, несколько мягких гранёных облаков, остров с открытым коричневым срезом земли.
- Свободная область. Остров занимает примерно 85% доступного поля. Оставить небольшой запас по периметру.

## Not in pack — remove

- Убрать лишний мини-партер между перголой и дорожкой: второе красное кольцо, четыре засаженные Г-образные клумбы и два штамба с цветами. Детали похожи на модели пака, но такой группы в демо нет.

## Проверка референса

- Остров целиком в кадре, шесть основных зон различимы, беседка — главный фокус.
- В Unity вернуть три пустые клумбы. Поставить стелу вплотную к низкой стене, поилку — на лужайку. Два ряда MOD-05 у входа расположить по разным сторонам локального подхода. Заменить белый обелиск у скамьи на базовый деревянный. Расставить невидимые или пропущенные малые предметы по MD композиций.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Два отдельно стоящих каменных навершия, стела внутри пруда, неподходящий силуэт створки и однотонные шезлонги. |
| 2 | Отклонена. Створка, стела и шезлонги исправлены, но пропали гном, поилка и обелиск лужайки, клумбы партера остались прямыми. |
| 3 | Выбрана. Главный фокус и шесть зон читаются. Удалить повторную группу по списку выше. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_1)
Problem: island fills 80 % of the frame width but the garden is small on it. Compositions cover ~55 % of the island top; the foreground (bottom 25 %), left and right edges and the zone between path and edges are empty lawn. The gazebo is ~9 % of the frame width and is not the clear focus.
- Island (demo-asset rebuild in Blender, not a layout change): shrink the top from ~24 x 18 m to ~18 x 13.5 m (x0.75), keep the soil cut and faceted edge. Re-export the FBX; path scaled/shortened the same way (width 2.4 m kept).
- Layout: move the six compositions inwards so the garden (bounding box of all pack items) occupies >= 80 % of the island top area; gap composition to island edge 0.8-1.5 m, gaps between compositions 1.5-2.5 m (now 4-6 m). Zones stay as in the reference (CMP-03 NE, CMP-05 NW, CMP-02 W, CMP-04 E, CMP-01 SW, CMP-06 SE).
- Camera: keep ~SSE (8 deg east), 40 deg down, vFOV 31-33; move closer so the island is 88-92 % of the frame width and the soil cut bottom is at 93-95 % of the height. Top sky margin 6-10 % (clouds only). Gazebo roof >= 13 % of the frame width, tallest and most contrasting object, nothing in front of it; move free STR-07_White and STR-01_White away from the gazebo front (e.g. 3 m east of the pond).
- Densify with allowed free pack items (extra to the compositions): +4 TOP-01/TOP-02 topiaries along the island edge, +3 PLT-01/PLT-03 rose bushes near the front lawn edge, +2 FLB-01_Planted/FLB-03_Planted at the path fork, +2 TOP-04 near the swing zone. The lower 25 % of the island top must hold >= 2 readable items (e.g. CMP-06 hammock/loungers moved 2 m towards the camera); no bare strip wider than 2.5 m.
- Lawn colour: now lime yellow-green (~#A5D24F, flat, bright). Target deeper clean green ~#7DB93C, saturation -8 %, exposure -0.15; keep the faceted tone variation. Soil cut unchanged.
- Light/post: keep warm key from upper left and the shadows. Make the top of the sky slightly bluer (less grey). Remove clouds that overlap island corners (bottom left, bottom right) so the silhouette is clean.
- Check after render: no pack item (except gnome, birdbath, sundial, hooks) lower than 3 % of the frame height.
