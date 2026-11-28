# AltView — scene reference (Э9 → Э10)

Purpose (REQUIREMENTS 7.5) — Обратный ракурс Demo_CottageGarden от пруда к беседке. Store files built from it — `10_DemoAndVersion`.
Reference image: `planning/CottageGardenDecor/scenes/AltView.png`

## Prompt (Codex, Sol 6.2)

```
Surgical edit of first image, absolutely preserve its 16:9 framing, original reverse angle from left NW, positions of all six named zones, gazebo, pond and sky. Focus on strictly removing alien props. At the red rose gateway on far right DELETE entirely the huge curved white background lattice fence and its tall end posts, and DELETE the two spherical green shrubs in stone vases. Replace entrance cluster with the approved exact elements in ref 2, but at original scale and reverse camera: simple low lattice gate leaf, two planted beds, two separate rose bushes, two edging rows, and tiny red hat gnome. No screen behind the entrance. At the pond in near left keep the passage open and narrow rectangular opaque blue water, lower walls to the proportions and geometry in ref 3. Stela with semicircular basin should touch wall on dry ground. Behind the insect hotel of ref 4, keep the original hook and add the nearby second hook with cylindrical feeder only. Keep original island shape and paint, gazebo, source garden locations and scale throughout. No houses, extra bushes, fences, trees, people, animals, text or other objects.
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

- Ракурс, высота и FOV. Северо-запад, наклон 36° вниз, ориентир высоты 19 м, вертикальный FOV 38°, широкий кадр. Пруд впереди, беседка за дорожкой.
- Свет. Тёплый мягкий дневной свет сверху слева и контактные тени.
- Фон. Ясное голубое небо и редкие мягкие облака, остров с открытым срезом земли.
- Свободная область. Оставить чистый верхний угол под возможный блок состава.

## Not in pack — remove

При визуальной проверке посторонних объектов не обнаружено.

## Проверка референса

- Отдельный ракурс, пруд и арка на переднем плане, беседка за дорожкой. Пруд и стелу в Unity поставить отдельно по схеме CMP-05; на PNG чаша слишком близка к водной плитке.
- Мелкие предметы, варианты и точные стыки расставить по MD композиций. У второго крюка на PNG кормушка не видна.

| Генерация | Результат |
|---:|---|
| 1 | Отклонена. Стена пересекает проход кованой арки, плющ лежит на газоне, край острова обрезан. |
| 2 | Отклонена. Проход открыт и кадр шире, но за розовым входом возникли белый дуговой забор и два посторонних шара в вазонах. |
| 3 | Выбрана. Забор и вазоны удалены, проём, две аппликации плюща и обратный ракурс читаются. |

## Fixes

<!-- The render reviewer appends fix sections. -->

## Fix 1 (2026-11-26, review renders_1)
Problem: island is 72 % of the width with ~28 % empty sky left and right, items small (gazebo ~10 % of the width), the front lawn is empty beside the walled pond, soil cut touches 98 % of the height (looks cropped low), the pond is seen from the outside of the L wall so the iron arch and stela are hidden, no clear focus.
- Island: rebuilt smaller as Hero Fix 1 (~18 x 13.5 m, garden >= 80 % of the top).
- Camera: from NW, 36 deg down, vFOV 32-34; island 86-90 % of the width (x 5-95 %), soil cut bottom at 93-95 %; sky margin >= 5 % at the top, one clean upper corner (left, ~15 % x 15 %) for the composition block, max 2 clouds. Island centroid at x 50 +- 3 %, y 52 +- 4 % (now ~54 % / 60 %).
- Focus: pond + low wall + iron arch (CMP-05) in the front and the red gazebo behind the path must both read: rotate the camera 15-20 deg towards W (or CMP-05 in place) so the arch opening and stela face the camera/path; pond block >= 14 % of the width.
- Densify as in Hero Fix 1; additionally fill the front-left lawn with free items (STR-01_White, FUR-03_White/FUR-04_White, FLB-01..03) 1.5-2.5 m from the pond wall, +3 TOP-01/02 near the near edge.
- Lawn colour/light as Hero Fix 1; keep the long shadows.
