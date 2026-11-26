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
