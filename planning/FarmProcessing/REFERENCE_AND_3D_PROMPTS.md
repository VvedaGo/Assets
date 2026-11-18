# Промпты изображений и 3D

3D-модели ещё не созданы. Все 72 изображения доступны в [каталоге](MODEL_CATALOG.md), колонка «Референс».
Референсы сгенерированы последовательно в порядке строк; общий стиль закреплён в каталоге. Точные использованные промпты: [журнал генерации](references/GENERATION_MANIFEST.json), поле `used_prompt`.
Общий блок ниже соединять с описанием предмета. Reference задаёт форму; размеры и детали проверяются вручную.

## Общий блок изображения

Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. 

No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

## Общие правила 3D

Use the approved reference image as the shape and color guide. Generate ONLY the single described object. Complete the back, underside and hidden sides consistently. Do not include floor, shadow mesh, camera, lights, smoke, fire or floating fragments. Keep mechanical gaps open and parts geometrically plausible. No baked lighting or baked text. Low-poly game asset with simple palette UVs. Separate moving components if supported; otherwise rebuild these components manually after generation.

Dimensions and topology are acceptance targets, not guaranteed generator outputs. Simple tools, modular architecture and repeated structural parts should normally be modeled directly. Do not generate a complete station again for each moving part. Maximum three attempts per object, then rebuild manually or re-estimate scope. No paid generation is launched by this document.

## STA-01 — Сыроварочный чан

Prefab: `FMS_Workshop_STA_01`. Очередь: core. Размер X/Z/Y: 1.2/1.0/1.1 м. LOD0: 1200–2400 tris. Части для отделения: крышка; мешалка.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: open round cheese-making vat on a low stand, a removable lid and separate stirring paddle, simple cream curd surface. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only open round cheese-making vat on a low stand, a removable lid and separate stirring paddle, simple cream curd surface. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-02 — Винтовой сырный пресс

Prefab: `FMS_Workshop_STA_02`. Очередь: core. Размер X/Z/Y: 0.8/0.7/1.2 м. LOD0: 1600–3000 tris. Части для отделения: винт; нажимная плита.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: tabletop wooden screw cheese press with a clear vertical threaded spindle, pressing plate and removable cheese mold. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only tabletop wooden screw cheese press with a clear vertical threaded spindle, pressing plate and removable cheese mold. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-03 — Вертикальная маслобойка

Prefab: `FMS_Workshop_STA_03`. Очередь: core. Размер X/Z/Y: 0.5/0.5/1.0 м. LOD0: 700–1400 tris. Части для отделения: шток; крышка.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: traditional upright wooden butter churn with a narrow barrel, removable lid and vertical dasher. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only traditional upright wooden butter churn with a narrow barrel, removable lid and vertical dasher. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-04 — Дробилка фруктов

Prefab: `FMS_Workshop_STA_04`. Очередь: core. Размер X/Z/Y: 1.0/0.8/1.2 м. LOD0: 1600–3000 tris. Части для отделения: рукоять; два вала.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: hand-cranked fruit crusher on a wooden stand, square hopper, two simple rollers, open output chute. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only hand-cranked fruit crusher on a wooden stand, square hopper, two simple rollers, open output chute. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-05 — Пресс для сока

Prefab: `FMS_Workshop_STA_05`. Очередь: core. Размер X/Z/Y: 1.0/0.9/1.6 м. LOD0: 2200–4000 tris. Части для отделения: винт; нажимная плита.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: wooden basket fruit press on a raised frame, vertical screw, pressing plate and a clearly visible juice outlet. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only wooden basket fruit press on a raised frame, vertical screw, pressing plate and a clearly visible juice outlet. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-06 — Ручные жернова

Prefab: `FMS_Workshop_STA_06`. Очередь: core. Размер X/Z/Y: 0.9/0.8/0.9 м. LOD0: 1000–2000 tris. Части для отделения: верхний жернов; рукоять.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: two horizontal circular millstones on a low wooden support, central grain inlet, upper stone with a hand crank and flour outlet. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only two horizontal circular millstones on a low wooden support, central grain inlet, upper stone with a hand crank and flour outlet. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-07 — Котёл для варенья

Prefab: `FMS_Workshop_STA_07`. Очередь: core. Размер X/Z/Y: 1.0/0.9/1.1 м. LOD0: 1200–2400 tris. Части для отделения: крышка; мешалка.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: wide copper jam kettle on a small brick hearth, removable lid, separate wooden stirring paddle, opaque red jam surface. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only wide copper jam kettle on a small brick hearth, removable lid, separate wooden stirring paddle, opaque red jam surface. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-08 — Сушильная стойка

Prefab: `FMS_Workshop_STA_08`. Очередь: core. Размер X/Z/Y: 1.1/0.7/1.6 м. LOD0: 900–1800 tris. Части для отделения: три лотка.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: freestanding wooden food drying rack with three removable mesh trays, open sides and simple chunky frame. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only freestanding wooden food drying rack with three removable mesh trays, open sides and simple chunky frame. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-09 — Печь для хлеба

Prefab: `FMS_Workshop_STA_09`. Очередь: extension. Размер X/Z/Y: 1.5/1.4/1.8 м. LOD0: 2200–4000 tris. Части для отделения: дверца.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: small freestanding rustic brick bread oven with a domed chamber, arched opening, hinged metal door and short chimney. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only small freestanding rustic brick bread oven with a domed chamber, arched opening, hinged metal door and short chimney. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-10 — Масляный пресс

Prefab: `FMS_Workshop_STA_10`. Очередь: extension. Размер X/Z/Y: 1.0/0.8/1.4 м. LOD0: 1800–3500 tris. Части для отделения: винт; рукоять.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: rustic manual seed oil screw press, wooden frame, small seed hopper, pressing chamber and oil spout, visibly distinct from fruit press. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only rustic manual seed oil screw press, wooden frame, small seed hopper, pressing chamber and oil spout, visibly distinct from fruit press. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-11 — Коптильный шкаф

Prefab: `FMS_Workshop_STA_11`. Очередь: extension. Размер X/Z/Y: 0.9/0.8/1.8 м. LOD0: 1600–3000 tris. Части для отделения: дверь; две решётки.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: freestanding wooden food smoking cabinet on a brick base, hinged front door, two removable racks and short metal flue. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only freestanding wooden food smoking cabinet on a brick base, hinged front door, two removable racks and short metal flue. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## STA-12 — Ручная медогонка

Prefab: `FMS_Workshop_STA_12`. Очередь: extension. Размер X/Z/Y: 0.8/0.8/1.2 м. LOD0: 1600–3200 tris. Части для отделения: крышка; рукоять; корзина.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: small hand-cranked cylindrical honey extractor on three legs, removable opaque lid, simple internal basket and bottom honey tap. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only small hand-cranked cylindrical honey extractor on three legs, removable opaque lid, simple internal basket and bottom honey tap. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-01 — Форма для сыра

Prefab: `FMS_Workshop_TOL_01`. Очередь: core. Размер X/Z/Y: 0.25/0.25/0.18 м. LOD0: 150–400 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single round perforated cheese mold with a solid base and thick cream-colored walls. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single round perforated cheese mold with a solid base and thick cream-colored walls. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-02 — Сырная лира

Prefab: `FMS_Workshop_TOL_02`. Очередь: core. Размер X/Z/Y: 0.25/0.03/0.55 м. LOD0: 120–350 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rectangular stainless steel curd cutting harp with a wooden handle and a few thick parallel wires. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rectangular stainless steel curd cutting harp with a wooden handle and a few thick parallel wires. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-03 — Лопатка сыродела

Prefab: `FMS_Workshop_TOL_03`. Очередь: core. Размер X/Z/Y: 0.12/0.04/0.65 м. LOD0: 80–200 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single broad wooden cheese stirring paddle with a short slotted head. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single broad wooden cheese stirring paddle with a short slotted head. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-04 — Дуршлаг для творога

Prefab: `FMS_Workshop_TOL_04`. Очередь: core. Размер X/Z/Y: 0.35/0.3/0.15 м. LOD0: 200–500 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single shallow cream metal colander with two small handles and readable large perforations. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single shallow cream metal colander with two small handles and readable large perforations. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-05 — Черпак

Prefab: `FMS_Workshop_TOL_05`. Очередь: core. Размер X/Z/Y: 0.12/0.08/0.45 м. LOD0: 120–300 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single deep metal ladle with a long wooden grip. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single deep metal ladle with a long wooden grip. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-06 — Мерный кувшин

Prefab: `FMS_Workshop_TOL_06`. Очередь: core. Размер X/Z/Y: 0.25/0.2/0.3 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single opaque cream enamel measuring jug with a spout and handle, no writing or transparent glass. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single opaque cream enamel measuring jug with a spout and handle, no writing or transparent glass. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-07 — Воронка для розлива

Prefab: `FMS_Workshop_TOL_07`. Очередь: core. Размер X/Z/Y: 0.2/0.2/0.22 м. LOD0: 100–250 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wide metal bottling funnel with a short narrow stem. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wide metal bottling funnel with a short narrow stem. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-08 — Сито для муки

Prefab: `FMS_Workshop_TOL_08`. Очередь: core. Размер X/Z/Y: 0.35/0.35/0.1 м. LOD0: 150–400 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single round wooden flour sieve with a coarse simplified mesh base. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single round wooden flour sieve with a coarse simplified mesh base. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-09 — Совок для зерна

Prefab: `FMS_Workshop_TOL_09`. Очередь: core. Размер X/Z/Y: 0.15/0.32/0.1 м. LOD0: 100–250 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wooden grain scoop with a broad open bowl and a short handle. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wooden grain scoop with a broad open bowl and a short handle. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-10 — Доска для сыра

Prefab: `FMS_Workshop_TOL_10`. Очередь: core. Размер X/Z/Y: 0.45/0.28/0.04 м. LOD0: 80–180 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single thick rectangular cheese cutting board with a short handle and no food. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single thick rectangular cheese cutting board with a short handle and no food. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-11 — Нож для сыра

Prefab: `FMS_Workshop_TOL_11`. Очередь: core. Размер X/Z/Y: 0.05/0.03/0.3 м. LOD0: 80–200 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single short broad cheese knife with a simple wooden handle. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single short broad cheese knife with a simple wooden handle. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-12 — Керамическая миска

Prefab: `FMS_Workshop_TOL_12`. Очередь: core. Размер X/Z/Y: 0.35/0.35/0.13 м. LOD0: 150–350 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wide shallow cream ceramic preparation bowl, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wide shallow cream ceramic preparation bowl, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-13 — Пекарская лопата

Prefab: `FMS_Workshop_TOL_13`. Очередь: extension. Размер X/Z/Y: 0.35/0.06/1.4 м. LOD0: 120–300 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single long wooden bread peel with a flat rounded head. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single long wooden bread peel with a flat rounded head. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-14 — Скалка

Prefab: `FMS_Workshop_TOL_14`. Очередь: extension. Размер X/Z/Y: 0.08/0.5/0.08 м. LOD0: 100–250 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single thick wooden rolling pin with two short handles. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single thick wooden rolling pin with two short handles. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-15 — Крюк для копчения

Prefab: `FMS_Workshop_TOL_15`. Очередь: extension. Размер X/Z/Y: 0.08/0.03/0.16 м. LOD0: 80–180 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single chunky S-shaped metal smoking hook. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single chunky S-shaped metal smoking hook. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-16 — Щипцы для печи

Prefab: `FMS_Workshop_TOL_16`. Очередь: extension. Размер X/Z/Y: 0.08/0.05/0.5 м. LOD0: 150–350 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single pair of closed iron oven tongs with thick handles. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single pair of closed iron oven tongs with thick handles. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-17 — Рамка с сотами

Prefab: `FMS_Workshop_TOL_17`. Очередь: extension. Размер X/Z/Y: 0.4/0.04/0.25 м. LOD0: 250–700 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rectangular wooden honeycomb frame with simplified golden hexagonal cells, no bees. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rectangular wooden honeycomb frame with simplified golden hexagonal cells, no bees. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## TOL-18 — Масляная воронка с фильтром

Prefab: `FMS_Workshop_TOL_18`. Очередь: extension. Размер X/Z/Y: 0.25/0.25/0.35 м. LOD0: 200–500 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small metal oil strainer funnel on a three-legged tabletop support, visibly distinct from a plain funnel. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small metal oil strainer funnel on a three-legged tabletop support, visibly distinct from a plain funnel. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-01 — Круг сыра в форме

Prefab: `FMS_Workshop_PRD_01`. Очередь: core. Размер X/Z/Y: 0.25/0.25/0.15 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small fresh cheese wheel resting inside a shallow perforated mold, integrated food process prop. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small fresh cheese wheel resting inside a shallow perforated mold, integrated food process prop. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-02 — Сырный круг с вырезанным сектором

Prefab: `FMS_Workshop_PRD_02`. Очередь: core. Размер X/Z/Y: 0.35/0.35/0.15 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single mature cheese wheel with one wedge removed and a readable cream interior. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single mature cheese wheel with one wedge removed and a readable cream interior. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-03 — Брусок масла на дощечке

Prefab: `FMS_Workshop_PRD_03`. Очередь: core. Размер X/Z/Y: 0.22/0.16/0.08 м. LOD0: 120–300 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rectangular butter block on a small dedicated wooden butter board. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rectangular butter block on a small dedicated wooden butter board. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-04 — Творог в ткани

Prefab: `FMS_Workshop_PRD_04`. Очередь: core. Размер X/Z/Y: 0.25/0.25/0.18 м. LOD0: 250–600 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single cloth-lined curd bundle with an open top showing simple white curds. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single cloth-lined curd bundle with an open top showing simple white curds. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-05 — Фруктовая мезга в лотке

Prefab: `FMS_Workshop_PRD_05`. Очередь: core. Размер X/Z/Y: 0.5/0.35/0.12 м. LOD0: 250–600 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single shallow rectangular processing tray filled with chunky red apple pomace, no separate apples. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single shallow rectangular processing tray filled with chunky red apple pomace, no separate apples. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-06 — Сок в керамическом кувшине

Prefab: `FMS_Workshop_PRD_06`. Очередь: core. Размер X/Z/Y: 0.25/0.25/0.35 м. LOD0: 250–500 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wide-mouth cream ceramic juice pitcher with a simple opaque orange liquid surface. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wide-mouth cream ceramic juice pitcher with a simple opaque orange liquid surface. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-07 — Банка варенья под тканью

Prefab: `FMS_Workshop_PRD_07`. Очередь: core. Размер X/Z/Y: 0.16/0.16/0.2 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single squat opaque jam pot with a tied cloth lid and a visible red fruit-colored body, no label. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single squat opaque jam pot with a tied cloth lid and a visible red fruit-colored body, no label. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-08 — Поднос долек для сушки

Prefab: `FMS_Workshop_PRD_08`. Очередь: core. Размер X/Z/Y: 0.5/0.35/0.07 м. LOD0: 300–700 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rectangular shallow drying tray with separated chunky apple slices attached as one process prop. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rectangular shallow drying tray with separated chunky apple slices attached as one process prop. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-09 — Пучок сушёных трав

Prefab: `FMS_Workshop_PRD_09`. Очередь: core. Размер X/Z/Y: 0.2/0.15/0.4 м. LOD0: 200–500 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single tied bunch of dried culinary herbs hanging stem-up, simple clustered leaves. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single tied bunch of dried culinary herbs hanging stem-up, simple clustered leaves. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-10 — Открытый мешок с мукой

Prefab: `FMS_Workshop_PRD_10`. Очередь: core. Размер X/Z/Y: 0.35/0.3/0.45 м. LOD0: 250–550 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small open flour sack with rolled cloth rim and a pale flour mound visible inside. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small open flour sack with rolled cloth rim and a pale flour mound visible inside. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-11 — Тесто в миске

Prefab: `FMS_Workshop_PRD_11`. Очередь: core. Размер X/Z/Y: 0.35/0.35/0.2 м. LOD0: 250–550 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single ceramic mixing bowl holding one large risen bread dough mound. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single ceramic mixing bowl holding one large risen bread dough mound. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-12 — Лоток сушёных ягод

Prefab: `FMS_Workshop_PRD_12`. Очередь: core. Размер X/Z/Y: 0.4/0.3/0.08 м. LOD0: 250–650 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small wooden drying tray with attached clusters of dark dried berries, not fresh market fruit. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small wooden drying tray with attached clusters of dark dried berries, not fresh market fruit. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-13 — Хлеб на пекарском противне

Prefab: `FMS_Workshop_PRD_13`. Очередь: extension. Размер X/Z/Y: 0.45/0.35/0.12 м. LOD0: 300–700 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single flat dark baking tray with three attached small scored bread rolls. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single flat dark baking tray with three attached small scored bread rolls. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-14 — Семенной жмых

Prefab: `FMS_Workshop_PRD_14`. Очередь: extension. Размер X/Z/Y: 0.3/0.3/0.08 м. LOD0: 150–350 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rough round compressed seed oil cake with large simple visible seed fragments. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rough round compressed seed oil cake with large simple visible seed fragments. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-15 — Керамическая бутылка масла

Prefab: `FMS_Workshop_PRD_15`. Очередь: extension. Размер X/Z/Y: 0.12/0.12/0.32 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single tall opaque ceramic oil bottle with a narrow neck and a small wooden stopper, no label. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single tall opaque ceramic oil bottle with a narrow neck and a small wooden stopper, no label. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-16 — Подвес копчёной рыбы

Prefab: `FMS_Workshop_PRD_16`. Очередь: extension. Размер X/Z/Y: 0.1/0.08/0.4 м. LOD0: 250–600 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single smoked fish hanging from an integrated short cord, dark golden skin and clear stylized silhouette. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single smoked fish hanging from an integrated short cord, dark golden skin and clear stylized silhouette. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-17 — Подвес копчёного окорока

Prefab: `FMS_Workshop_PRD_17`. Очередь: extension. Размер X/Z/Y: 0.2/0.16/0.4 м. LOD0: 250–600 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single smoked ham hanging from an integrated short cord, simple reddish brown meat shape. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single smoked ham hanging from an integrated short cord, simple reddish brown meat shape. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## PRD-18 — Мёд в керамическом горшке

Prefab: `FMS_Workshop_PRD_18`. Очередь: extension. Размер X/Z/Y: 0.2/0.2/0.22 м. LOD0: 250–550 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small open honey crock with an opaque golden honey surface and a wooden honey dipper resting across its rim. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small open honey crock with an opaque golden honey surface and a wooden honey dipper resting across its rim. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-01 — Рабочий стол сыродела

Prefab: `FMS_Workshop_FUR_01`. Очередь: core. Размер X/Z/Y: 1.6/0.7/0.9 м. LOD0: 500–1000 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single sturdy wooden preparation workbench with a pale stone top, lower shelf and no props. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single sturdy wooden preparation workbench with a pale stone top, lower shelf and no props. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-02 — Стол фасовки

Prefab: `FMS_Workshop_FUR_02`. Очередь: core. Размер X/Z/Y: 1.4/0.6/0.9 м. LOD0: 450–900 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single narrow wooden bottling table with a raised back rail and a low front rim, no props. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single narrow wooden bottling table with a raised back rail and a low front rim, no props. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-03 — Стеллаж созревания сыра

Prefab: `FMS_Workshop_FUR_03`. Очередь: core. Размер X/Z/Y: 1.2/0.5/1.8 м. LOD0: 600–1200 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single open wooden cheese aging shelf with four widely spaced slatted shelves, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single open wooden cheese aging shelf with four widely spaced slatted shelves, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-04 — Сушильная полка для трав

Prefab: `FMS_Workshop_FUR_04`. Очередь: core. Размер X/Z/Y: 1.2/0.25/0.3 м. LOD0: 180–400 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wall-mounted wooden herb drying rail with six thick wooden pegs, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wall-mounted wooden herb drying rail with six thick wooden pegs, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-05 — Стеллаж банок

Prefab: `FMS_Workshop_FUR_05`. Очередь: core. Размер X/Z/Y: 0.9/0.4/1.5 м. LOD0: 400–850 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single narrow freestanding pantry shelf with three shelves and a short back rail, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single narrow freestanding pantry shelf with three shelves and a short back rail, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-06 — Деревянная мойка

Prefab: `FMS_Workshop_FUR_06`. Очередь: core. Размер X/Z/Y: 0.9/0.6/1.1 м. LOD0: 700–1400 tris. Части для отделения: рычаг насоса.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single rustic washstand with an integrated opaque enamel basin and separate simple hand pump, no water animation. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single rustic washstand with an integrated opaque enamel basin and separate simple hand pump, no water animation. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-07 — Подставка для пресса

Prefab: `FMS_Workshop_FUR_07`. Очередь: core. Размер X/Z/Y: 0.8/0.8/0.5 м. LOD0: 300–650 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single low reinforced square wooden press stand with diagonal braces. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single low reinforced square wooden press stand with diagonal braces. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-08 — Тележка для лотков

Prefab: `FMS_Workshop_FUR_08`. Очередь: core. Размер X/Z/Y: 0.8/0.5/0.9 м. LOD0: 600–1200 tris. Части для отделения: четыре колеса.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single two-shelf wooden workshop trolley with four separate small wheels and a push handle, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single two-shelf wooden workshop trolley with four separate small wheels and a push handle, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-09 — Стол пекаря

Prefab: `FMS_Workshop_FUR_09`. Очередь: extension. Размер X/Z/Y: 1.6/0.8/0.9 м. LOD0: 600–1200 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single broad wooden baker worktable with a thick top and integrated flour trough on one side, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single broad wooden baker worktable with a thick top and integrated flour trough on one side, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-10 — Рейка коптильных крюков

Prefab: `FMS_Workshop_FUR_10`. Очередь: extension. Размер X/Z/Y: 1.2/0.4/1.5 м. LOD0: 300–650 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single freestanding metal smoking rail on two upright supports, empty and without hooks. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single freestanding metal smoking rail on two upright supports, empty and without hooks. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-11 — Подставка для медовых рамок

Prefab: `FMS_Workshop_FUR_11`. Очередь: extension. Размер X/Z/Y: 0.7/0.5/0.7 м. LOD0: 400–850 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wooden honey frame draining stand with a sloped collection tray, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wooden honey frame draining stand with a sloped collection tray, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## FUR-12 — Низкий поддон для продукции

Prefab: `FMS_Workshop_FUR_12`. Очередь: extension. Размер X/Z/Y: 0.8/0.6/0.15 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single small dedicated wooden processing pallet with short feet and broad slats, empty. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single small dedicated wooden processing pallet with short feet and broad slats, empty. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-01 — Плитка деревянного пола 2×2

Prefab: `FMS_Workshop_MOD_01`. Очередь: core. Размер X/Z/Y: 2.0/2.0/0.15 м. LOD0: 120–300 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single square rustic plank floor module with flush edges, no surrounding ground. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single square rustic plank floor module with flush edges, no surrounding ground. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-02 — Плитка каменного пола 2×2

Prefab: `FMS_Workshop_MOD_02`. Очередь: core. Размер X/Z/Y: 2.0/2.0/0.15 м. LOD0: 180–400 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single square chunky stone floor module with flush edges, no surrounding ground. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single square chunky stone floor module with flush edges, no surrounding ground. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-03 — Стена мастерской 2 м

Prefab: `FMS_Workshop_MOD_03`. Очередь: core. Размер X/Z/Y: 2.0/0.18/2.4 м. LOD0: 250–550 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single timber-framed cream plaster workshop wall module, 2 meters wide, flat straight side edges. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single timber-framed cream plaster workshop wall module, 2 meters wide, flat straight side edges. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-04 — Стена с окном 2 м

Prefab: `FMS_Workshop_MOD_04`. Очередь: core. Размер X/Z/Y: 2.0/0.18/2.4 м. LOD0: 350–700 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single timber-framed workshop wall module with a large open window and thick sill, no glass. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single timber-framed workshop wall module with a large open window and thick sill, no glass. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-05 — Стена с дверным проёмом 2 м

Prefab: `FMS_Workshop_MOD_05`. Очередь: core. Размер X/Z/Y: 2.0/0.18/2.4 м. LOD0: 300–650 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single timber-framed workshop wall module with an open walk-through doorway, no door leaf. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single timber-framed workshop wall module with an open walk-through doorway, no door leaf. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-06 — Опорный столб

Prefab: `FMS_Workshop_MOD_06`. Очередь: core. Размер X/Z/Y: 0.2/0.2/2.4 м. LOD0: 100–250 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single chunky square wooden canopy support post with a simple stone foot, no surrounding floor. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single chunky square wooden canopy support post with a simple stone foot, no surrounding floor. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-07 — Балка навеса 2 м

Prefab: `FMS_Workshop_MOD_07`. Очередь: core. Размер X/Z/Y: 2.0/0.2/0.2 м. LOD0: 60–150 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single horizontal wooden canopy beam with flat ends, no roof or posts. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single horizontal wooden canopy beam with flat ends, no roof or posts. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-08 — Плоская крыша навеса 2×2

Prefab: `FMS_Workshop_MOD_08`. Очередь: core. Размер X/Z/Y: 2.0/2.0/0.18 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single nearly flat slatted wooden canopy roof panel with a dark terracotta top and flush grid edges. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single nearly flat slatted wooden canopy roof panel with a dark terracotta top and flush grid edges. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-09 — Дверь мастерской

Prefab: `FMS_Workshop_MOD_09`. Очередь: extension. Размер X/Z/Y: 0.9/0.08/2.0 м. LOD0: 200–450 tris. Части для отделения: дверь на петлях.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single thick rustic wooden door leaf with two hinges and a simple metal handle, isolated without a wall. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single thick rustic wooden door leaf with two hinges and a simple metal handle, isolated without a wall. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-10 — Низкая перегородка 2 м

Prefab: `FMS_Workshop_MOD_10`. Очередь: extension. Размер X/Z/Y: 2.0/0.15/1.1 м. LOD0: 200–450 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single low wooden workshop partition with chunky slats and flat ends. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single low wooden workshop partition with chunky slats and flat ends. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-11 — Угловой столб

Prefab: `FMS_Workshop_MOD_11`. Очередь: extension. Размер X/Z/Y: 0.2/0.2/2.4 м. LOD0: 80–200 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single vertical square timber corner post with simple flat faces for two adjoining wall modules. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single vertical square timber corner post with simple flat faces for two adjoining wall modules. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

## MOD-12 — Полка под окном

Prefab: `FMS_Workshop_MOD_12`. Очередь: extension. Размер X/Z/Y: 1.5/0.4/0.12 м. LOD0: 150–350 tris. Части для отделения: нет.

**Image prompt:** Stylized low-poly 3D game asset for a cozy rustic farm workshop, chunky functional shapes, flat shaded planar surfaces, warm wood #B5835A and #7A5233, cream #F2E6C9, muted red #C8473B, matte metal #8E959B, stone #A7A39A, restrained palette texture. One isolated object, complete and centered, three-quarter front view from 30 degrees above, soft neutral studio lighting, uniform light grey background #E9E9EC, no environment. Object: single wall-mounted broad wooden serving shelf with two triangular brackets, no window or wall. No people, animals, extra props, scenery, terrain, pedestal, labels, text, logos, watermark, photorealism, heavy weathering, tiny ornamental detail, transparent glass, smoke, fire or cropped geometry.

**3D prompt:** Generate only single wall-mounted broad wooden serving shelf with two triangular brackets, no window or wall. Match the approved reference; complete every side and remove any background geometry. Use the common 3D rules above. Final dimensions, triangle count, component separation, pivots and UVs must be corrected and verified during manual preparation.

