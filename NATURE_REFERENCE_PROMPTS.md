# Farm Nature — промпты референсов (шаг 4)

Версия: 0.1 (черновик) · Дата: 2026-10-31 · Связан с [FARM_NATURE_PACK.md](FARM_NATURE_PACK.md) (состав и стиль).

> Здесь только **тексты**: ни одна картинка не сгенерирована. Промпты не проверялись на генераторе; стиль и формулировки нужно подогнать на пилотах (раздел 3). Референс не доказывает наличие ассета в паке.

## 1. Как собирать итоговый промпт

Итоговый промпт = **ОБЩИЙ БЛОК** + **РАКУРС** + **описание модели из раздела 4** (+ **NEGATIVE**, если генератор его поддерживает). Формат такой же, как у `Plan/PACK2_FARM_YARD_PLAN.md`. Имя файла картинки: `<ID>_<имя меша без FMS_>.png`, например `TRE-01_Tree_Oak_L.png` (встроенный инструмент выдаёт PNG 1254×1254; BED-01 сохранён как JPG).

### 1.1 Общий блок

```
Stylized low-poly 3D game asset, single isolated object, faceted flat-shaded look with clearly visible polygon facets, chunky simplified shapes, flat colour fills from a limited warm palette (#6E9F4A green, #8AB257 light green, #739E52 dark green, #B5835A and #7A5233 wood, #A7A39A stone, #D8B65A straw, #C8473B red, #4A78A8 water, #F2E6C9 cream), no textures, no noise, matte, clean hand-painted look, subtle soft ambient occlusion, mobile game asset-store product render. Foliage and grass are built from chunky faceted solid shapes, never from flat leaf cards or transparent leaf textures. Large clean flat facets, few big simple shapes, no tiny pebbles, no small bumps, no surface clutter or fine detail, details only as big chunky shapes; all earth and soil in matte dark brown (#805433 and #664229), never orange or terracotta. Soft diffused studio lighting, one gentle key light from top-left, soft fill, no harsh highlights, soft contact shadow directly under the object only. Plain uniform light-grey background (#C8CCD4), no floor, no horizon, no other objects, no text, no watermark, no logo. Square 1:1 image, 1024x1024, crisp edges, high clarity.
```

### 1.2 Negative prompt

```
realistic photo, photorealistic, high-poly, subsurface scattering, hyper-detailed textures, leaf textures, alpha-cut leaves, leaf cards, billboard trees, photographic bark, realistic grass blades, fur, noise, grain, blur, motion blur, depth of field, text, letters, numbers, watermark, signature, logo, hands, people, animals, insects, multiple scenes, background clutter, dramatic shadows, harsh rim light, glow, bloom, neon, dark moody lighting, wireframe overlay, cropped object, border, frame, outlines in black, cartoon outline, anime, pixel art, oversaturated, interior view, terrain, sky, fog
```

### 1.3 Ракурс

- **Стандартный:** `Three-quarter front view from slightly above (about 30 degrees), object centered and fully in frame with a small margin; the object fills about 70% of the frame (trees about 85% of the frame height).`
- **Модули (грядки, дорожки, вода, земля):** `Three-quarter view from higher above (about 45 degrees), the module centered and fully in frame with a small margin, edges and thickness clearly visible.`
- **Культуры:** стандартный ракурс плюс фраза: `The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed.` Диск почвы нужен только как опора для генератора и вырезается при доводке.

## 2. Правила

1. Один объект на картинку. Стадии роста — три отдельные картинки с одним и тем же ракурсом и масштабом, чтобы силуэты можно было сравнить.
2. Группы (пучок травы, цветы, камыш, поленница, группа камней) — один объект из нескольких частей, а не несколько картинок.
3. Вода и лужи — плоские объекты; их читаемость проверяется в первую очередь.
4. Для всех: нет земли вокруг (кроме указанного исключения для культур и конструктивной подложки модулей), нет надписей, нет животных и насекомых.
5. Принимать референс только если силуэт читаем, пропорции правдоподобны, нет невозможных конструкций и видны грани, а не гладкие поверхности.

## 3. Порядок генерации

1. **Пилоты:** CRP-07, CRP-08, CRP-09, ROC-04, TRE-01 (дуб, три стадии моркови, валун). Подобрать формулировки и сохранить итоговый общий блок.
2. Остальное ядро (отметка «ядро»), затем расширение.
3. Для каждой принятой картинки записать генератор, seed и точный промпт.

## 4. Промпты моделей

### Грядки и участки (BED)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| BED-01 | `FMS_Bed_Row_Soil` | ядро |  | a low rounded rectangular mound of matte dark brown tilled soil, about 2.5 times longer than wide, with exactly four wide shallow furrows running along its length and open at both short ends (no raised wall or rim around the edge, no tray or trough shape), rounded corners, only a few large flat facets, smooth simple surface with no small clumps, no plants. (ракурс: модуль) | `BED-01_Bed_Row_Soil.jpg` | принято как черновой референс (v2; v1 отклонена) |
| BED-02 | `FMS_Bed_Raised_2x1` | ядро |  | rectangular raised garden bed built from chunky warm wooden planks with square corner posts, filled to the brim with dark brown soil, 2:1 proportions, no plants. (ракурс: модуль) | `BED-02_Bed_Raised_2x1.png` | принято |
| BED-03 | `FMS_Bed_Raised_1x1` | ядро |  | square raised garden bed built from chunky warm wooden planks with square corner posts, filled to the brim with dark brown soil, 1:1 proportions, no plants. (ракурс: модуль) | `BED-03_Bed_Raised_1x1.png` | принято |
| BED-04 | `FMS_Bed_Plot_4x4` | ядро |  | square plot of freshly ploughed field soil with six parallel soil ridges and furrows between them, low flat rim, dark brown faceted clumps, no plants. (ракурс: модуль) | `BED-04_Bed_Plot_4x4.png` | принято |
| BED-05 | `FMS_Bed_Trellis` | расширение |  | wooden garden trellis made of two stout vertical posts with four horizontal rails and two diagonal braces, tall rectangle, no plants. (ракурс: стандарт) | `BED-05_Bed_Trellis.png` | принято |
| BED-06 | `FMS_Bed_Stakes_Row` | расширение |  | row of five thin wooden stakes in a straight line tied together with two lines of twine, each stake with a small flat wooden foot, no plants. (ракурс: стандарт) | `BED-06_Bed_Stakes_Row.png` | принято |

### Культуры по стадиям роста (CRP)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| CRP-01 | `FMS_Crop_Wheat_S1` | ядро |  | a tiny cluster of six short bright green blade-like sprouts. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-01_Crop_Wheat_S1.png` | принято условно (мало отличается от S2, в 3D сделать мельче) |
| CRP-02 | `FMS_Crop_Wheat_S2` | ядро |  | a cluster of ten tall green stalks with narrow leaves, no ears yet. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-02_Crop_Wheat_S2.png` | принято |
| CRP-03 | `FMS_Crop_Wheat_S3` | ядро |  | a cluster of twelve tall golden-yellow stalks with plump wheat ears, bending slightly. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-03_Crop_Wheat_S3.png` | принято |
| CRP-04 | `FMS_Crop_Corn_S1` | ядро |  | two small young corn seedlings with a few broad curled leaves. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-04_Crop_Corn_S1.png` | принято |
| CRP-05 | `FMS_Crop_Corn_S2` | ядро |  | one knee-high corn plant with a thick green stalk and six long arching leaves, no cob. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-05_Crop_Corn_S2.png` | принято (метёлка уже на S2) |
| CRP-06 | `FMS_Crop_Corn_S3` | ядро |  | tall corn plant with thick stalk, long arching leaves, two yellow cobs in green husks and a tassel on top. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-06_Crop_Corn_S3.png` | принято |
| CRP-07 | `FMS_Crop_Carrot_S1` | ядро | да | three or four thin upright stems growing from the soil, each ending in a small finely divided feathery leaf with narrow pointed lobes like a carrot or parsley leaf, small and delicate, much smaller than a mature plant, no root visible, no broad leaves. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-07_Crop_Carrot_S1.png` | принято (v2) |
| CRP-08 | `FMS_Crop_Carrot_S2` | ядро | да | a fuller bushy tuft of eight feathery green leaves with the top of an orange carrot just peeking out. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-08_Crop_Carrot_S2.png` | принято |
| CRP-09 | `FMS_Crop_Carrot_S3` | ядро | да | a dense feathery leaf tuft with the thick orange carrot shoulder half exposed above the soil. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-09_Crop_Carrot_S3.png` | принято (морковь крупновата, плотная ботва) |
| CRP-10 | `FMS_Crop_Cabbage_S1` | ядро |  | two small round seedling leaves with a tiny bud between them. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-10_Crop_Cabbage_S1.png` | принято |
| CRP-11 | `FMS_Crop_Cabbage_S2` | ядро |  | a loose rosette of broad wavy green leaves, the head just beginning to form. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-11_Crop_Cabbage_S2.png` | принято |
| CRP-12 | `FMS_Crop_Cabbage_S3` | ядро |  | a large round compact cabbage head with pale veins, surrounded by broad outer leaves. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-12_Crop_Cabbage_S3.png` | принято |
| CRP-13 | `FMS_Crop_Tomato_S1` | ядро |  | a small seedling with two oval leaves and a pair of serrated leaves, one thin wooden stake beside it. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-13_Crop_Tomato_S1.png` | принято |
| CRP-14 | `FMS_Crop_Tomato_S2` | ядро |  | a bushy plant on a thin wooden stake with serrated leaves, small yellow flowers and a few small green tomatoes. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-14_Crop_Tomato_S2.png` | принято |
| CRP-15 | `FMS_Crop_Tomato_S3` | ядро |  | a tall staked plant with serrated leaves and many ripe red round tomatoes. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-15_Crop_Tomato_S3.png` | принято |
| CRP-16 | `FMS_Crop_Pumpkin_S1` | ядро |  | two large oval seedling leaves on a short stem. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-16_Crop_Pumpkin_S1.png` | принято |
| CRP-17 | `FMS_Crop_Pumpkin_S2` | ядро |  | a spreading vine with big lobed leaves, one yellow flower and a small green pumpkin. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-17_Crop_Pumpkin_S2.png` | принято |
| CRP-18 | `FMS_Crop_Pumpkin_S3` | ядро |  | a spreading vine with big lobed leaves and one large orange ribbed pumpkin with a green stem. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-18_Crop_Pumpkin_S3.png` | принято |
| CRP-19 | `FMS_Crop_Sunflower_S1` | расширение |  | a small seedling with two oval leaves and a pair of heart-shaped leaves. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-19_Crop_Sunflower_S1.png` | принято |
| CRP-20 | `FMS_Crop_Sunflower_S2` | расширение |  | a tall green stalk with large heart-shaped leaves and a closed green flower bud. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-20_Crop_Sunflower_S2.png` | принято |
| CRP-21 | `FMS_Crop_Sunflower_S3` | расширение |  | a tall thick stalk with big heart-shaped leaves and one large open flower, yellow petals around a brown seed disc, drooping slightly. The plant grows out of a small flat disc of brown soil that is only a construction base and will be removed. (ракурс: стандарт) | `CRP-21_Crop_Sunflower_S3.png` | принято |
| CRP-22 | `FMS_Crop_WheatField_Green` | ядро |  | a square patch of densely planted very young wheat: only short upright blade-like leaves, every blade bright fresh green, no ears, no golden or yellow colour at all, all blades about the same short height in neat rows, on a flat thin soil base. (ракурс: стандарт) | `CRP-22_Crop_WheatField_Green.png` | принято (v2) |
| CRP-23 | `FMS_Crop_WheatField_Golden` | ядро |  | a square patch of densely planted ripe golden wheat with heavy ears, slightly swaying uneven heights, on a flat thin soil base. (ракурс: стандарт) | `CRP-23_Crop_WheatField_Golden.png` | принято |
| CRP-24 | `FMS_Crop_WheatField_Stubble` | ядро |  | a square patch of harvested wheat field: short cut stalks and a few scattered straw pieces, on a flat thin soil base. (ракурс: стандарт) | `CRP-24_Crop_WheatField_Stubble.png` | принято |

### Деревья, пни и брёвна (TRE)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| TRE-01 | `FMS_Tree_Oak_L` | ядро | да | large stylized oak tree, short thick brown trunk splitting into three main limbs, a wide round crown made of five or six big faceted rounded green clusters in two or three green tones, small root flare at the base. (ракурс: стандарт) | `TRE-01_Tree_Oak_L.png` | принято |
| TRE-02 | `FMS_Tree_Oak_Autumn` | расширение |  | large stylized oak tree, short thick brown trunk splitting into three main limbs, a wide round crown of five or six big faceted rounded clusters in autumn orange, ochre and red-brown tones. (ракурс: стандарт) | `TRE-02_Tree_Oak_Autumn.png` | принято (форма как у TRE-01: в 3D материальный вариант) |
| TRE-03 | `FMS_Tree_Birch` | ядро |  | slim birch tree with a creamy white trunk with dark horizontal marks, thin branches, an airy crown of four or five small faceted light yellow-green clusters. (ракурс: стандарт) | `TRE-03_Tree_Birch.png` | принято |
| TRE-04 | `FMS_Tree_Birch_S` | расширение |  | young small birch tree, half the height of a mature birch, creamy white trunk with dark marks, three small faceted light green clusters. (ракурс: стандарт) | `TRE-04_Tree_Birch_S.png` | принято |
| TRE-05 | `FMS_Tree_Spruce_L` | ядро |  | tall conical spruce of five stacked faceted tiers in dark green, tiers getting smaller towards a pointed top, short brown trunk visible at the bottom. (ракурс: стандарт) | `TRE-05_Tree_Spruce_L.png` | принято |
| TRE-06 | `FMS_Tree_Spruce_S` | расширение |  | small young spruce of three stacked faceted tiers in dark green, pointed top, short brown trunk visible at the bottom. (ракурс: стандарт) | `TRE-06_Tree_Spruce_S.png` | принято |
| TRE-07 | `FMS_Tree_Apple_Fruit` | ядро |  | stout apple tree with a short gnarled brown trunk, a rounded wide crown of four or five green faceted clusters and about twelve bright red apples visible. (ракурс: стандарт) | `TRE-07_Tree_Apple_Fruit.png` | принято |
| TRE-08 | `FMS_Tree_Apple_Blossom` | расширение |  | stout apple tree with a short gnarled brown trunk, a rounded wide crown of four or five faceted clusters covered in light pink and white blossoms, no apples. (ракурс: стандарт) | `TRE-08_Tree_Apple_Blossom.png` | принято |
| TRE-09 | `FMS_Tree_Willow` | расширение |  | weeping willow with a thick leaning trunk and a dome crown with many long drooping faceted strips of light grey-green foliage hanging almost to the ground. (ракурс: стандарт) | `TRE-09_Tree_Willow.png` | принято |
| TRE-10 | `FMS_Wood_Stump` | ядро |  | cut tree stump, thick, light cut top with flat-colour growth rings, brown bark sides and a chunky root flare. (ракурс: стандарт) | `TRE-10_Wood_Stump.png` | принято |
| TRE-11 | `FMS_Wood_Log` | ядро |  | a single lying log with round cut ends showing flat-colour rings, dark brown bark with two small branch stubs. (ракурс: стандарт) | `TRE-11_Wood_Log.png` | принято |
| TRE-12 | `FMS_Wood_Log_Fallen` | расширение |  | large fallen tree trunk lying on the ground with the root ball upturned at one end and a few broken branch stubs. (ракурс: стандарт) | `TRE-12_Wood_Log_Fallen.png` | принято (мох и трава у корней) |
| TRE-13 | `FMS_Wood_Firewood_Stack` | ядро |  | neat stack of split firewood in four tight rows held between two vertical wooden posts, light cut ends facing the viewer. (ракурс: стандарт) | `TRE-13_Wood_Firewood_Stack.png` | принято |
| TRE-14 | `FMS_Wood_Firewood_Pile` | расширение |  | loose heap of about ten split firewood logs piled into a pyramid. (ракурс: стандарт) | `TRE-14_Wood_Firewood_Pile.png` | принято |

### Кусты, живая изгородь, цветы и трава (PLT)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| PLT-01 | `FMS_Bush_Round` | ядро |  | dense round green bush made of four or five faceted bumps in two green tones, a few thin twigs at the base. (ракурс: стандарт) | `PLT-01_Bush_Round.png` | принято |
| PLT-02 | `FMS_Bush_Berry` | ядро |  | dense round green bush made of four or five faceted bumps with about fifteen small red berries. (ракурс: стандарт) | `PLT-02_Bush_Berry.png` | принято |
| PLT-03 | `FMS_Bush_Flowering` | расширение |  | dense round green bush made of four or five faceted bumps covered in clusters of pink and white flowers. (ракурс: стандарт) | `PLT-03_Bush_Flowering.png` | принято |
| PLT-04 | `FMS_Hedge_Straight` | ядро |  | straight trimmed garden hedge, a long rectangular box with a slightly rounded faceted top in dark green, short thin brown trunks visible at the bottom. (ракурс: стандарт) | `PLT-04_Hedge_Straight.png` | принято (грани мельче, чем нужно) |
| PLT-05 | `FMS_Hedge_Corner` | расширение |  | trimmed garden hedge turning a 90-degree corner, L-shaped, rounded faceted top in dark green, short brown trunks at the bottom. (ракурс: стандарт) | `PLT-05_Hedge_Corner.png` | принято (угол тупее 90°) |
| PLT-06 | `FMS_Hedge_End` | расширение |  | trimmed garden hedge end piece, a short box with a rounded faceted end cap in dark green, short brown trunks at the bottom. (ракурс: стандарт) | `PLT-06_Hedge_End.png` | принято |
| PLT-07 | `FMS_Flower_Daisy` | ядро |  | clump of seven daisies on thin green stems with a few leaves, white petals and yellow centres. (ракурс: стандарт) | `PLT-07_Flower_Daisy.png` | принято (лепестки гладковаты) |
| PLT-08 | `FMS_Flower_Tulip` | ядро |  | clump of five red tulips with broad green leaves. (ракурс: стандарт) | `PLT-08_Flower_Tulip.png` | принято |
| PLT-09 | `FMS_Flower_Lavender` | расширение |  | clump of seven purple lavender spikes on green stems with narrow grey-green leaves. (ракурс: стандарт) | `PLT-09_Flower_Lavender.png` | принято |
| PLT-10 | `FMS_Flower_Poppy` | расширение |  | clump of five red poppies with dark centres on thin green stems. (ракурс: стандарт) | `PLT-10_Flower_Poppy.png` | принято |
| PLT-11 | `FMS_Flower_Meadow` | ядро |  | mixed meadow clump of small white, yellow, pink and blue flowers with grass blades. (ракурс: стандарт) | `PLT-11_Flower_Meadow.png` | принято (основа из земли и 2 камня убрать в 3D) |
| PLT-12 | `FMS_Grass_Tuft_S` | ядро |  | small fan of seven sharp triangular grass blades in two greens. (ракурс: стандарт) | `PLT-12_Grass_Tuft_S.png` | принято |
| PLT-13 | `FMS_Grass_Tuft_M` | ядро |  | fan of twelve sharp triangular grass blades of varying heights in two greens. (ракурс: стандарт) | `PLT-13_Grass_Tuft_M.png` | принято |
| PLT-14 | `FMS_Grass_Tall` | ядро |  | dense bunch of sixteen long arching grass blades with golden tips. (ракурс: стандарт) | `PLT-14_Grass_Tall.png` | принято |
| PLT-15 | `FMS_Grass_Reeds` | ядро |  | cluster of six tall reeds with three brown cattail heads and a few long blade leaves. (ракурс: стандарт) | `PLT-15_Grass_Reeds.png` | принято |
| PLT-16 | `FMS_Plant_Fern` | расширение |  | fern with seven arching fronds, each frond with chunky zigzag leaflets, dark green. (ракурс: стандарт) | `PLT-16_Plant_Fern.png` | принято (небольшой пятачок земли убрать) |

### Камни (ROC)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| ROC-01 | `FMS_Rock_S` | ядро |  | small grey rock with about eight chunky facets, flat bottom. (ракурс: стандарт) | `ROC-01_Rock_S.png` | принято |
| ROC-02 | `FMS_Rock_M` | ядро |  | medium grey rock with about ten chunky facets, flat bottom, slightly irregular. (ракурс: стандарт) | `ROC-02_Rock_M.png` | принято |
| ROC-03 | `FMS_Rock_L` | ядро |  | large grey rock with about twelve chunky facets, flat bottom, one steeper side. (ракурс: стандарт) | `ROC-03_Rock_L.png` | принято |
| ROC-04 | `FMS_Rock_Boulder` | ядро | да | large grey boulder with a flat top, a few chunky cracks made as geometry, a small patch of green moss on top. (ракурс: стандарт) | `ROC-04_Rock_Boulder.png` | принято (чуть мягче и детальнее Yard) |
| ROC-05 | `FMS_Rock_Cluster` | расширение |  | group of three grey rocks of different sizes touching each other, chunky facets. (ракурс: стандарт) | `ROC-05_Rock_Cluster.png` | принято |
| ROC-06 | `FMS_Rock_Flat` | расширение |  | a single flat grey slab stone with a slightly irregular hexagonal outline and chunky facets, thin like a paving stone, lying alone: only the stone itself, no tree, no plants, no grass, no soil, no base slab, nothing else in the picture. (ракурс: модуль) | `ROC-06_Rock_Flat.png` | принято (v2) |

### Дорожки (PTH)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| PTH-01 | `FMS_Path_Dirt_Straight` | ядро |  | straight strip of light brown packed dirt path with zigzag edges and a thin darker rim, flat top, no grass. (ракурс: модуль) | `PTH-01_Path_Dirt_Straight.png` | принято |
| PTH-02 | `FMS_Path_Dirt_Curve` | ядро |  | 90-degree curve of a light brown packed dirt path with zigzag edges and a thin darker rim, flat top, no grass. (ракурс: модуль) | `PTH-02_Path_Dirt_Curve.png` | принято |
| PTH-03 | `FMS_Path_Dirt_T` | расширение |  | T-junction of a light brown packed dirt path with zigzag edges and a thin darker rim, flat top, no grass. (ракурс: модуль) | `PTH-03_Path_Dirt_T.png` | принято |
| PTH-04 | `FMS_Path_Dirt_End` | расширение |  | dead end of a light brown packed dirt path with a rounded end, zigzag edges and a thin darker rim, flat top, no grass. (ракурс: модуль) | `PTH-04_Path_Dirt_End.png` | принято условно (форма с перетяжкой, сделать чёткий тупик) |
| PTH-05 | `FMS_Path_Stone_Straight` | ядро |  | straight path made of six irregular flat grey stones set in two rows with narrow gaps of brown soil. (ракурс: модуль) | `PTH-05_Path_Stone_Straight.png` | принято (добавлены травинки по краю) |
| PTH-06 | `FMS_Path_Stone_Curve` | расширение |  | 90-degree curved path made of irregular flat grey stones with narrow gaps of brown soil. (ракурс: модуль) | `PTH-06_Path_Stone_Curve.png` | принято (травяная кромка убрать в 3D) |
| PTH-07 | `FMS_Path_Stepping_Stones` | ядро |  | five flat roundish grey stepping stones in a gentle line, each a different size, standing completely alone: no grass, no soil, no ground slab, no bushes, no other rocks, nothing else around them. (ракурс: модуль) | `PTH-07_Path_Stepping_Stones.png` | принято (v2) |

### Вода и мостик (WAT)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| WAT-01 | `FMS_Water_Pond_Round` | ядро |  | round pond with a ring of about eight grey stones around the edge, flat blue water surface slightly lower than the rim. (ракурс: модуль) | `WAT-01_Water_Pond_Round.png` | принято |
| WAT-02 | `FMS_Water_Pond_Oval` | расширение |  | oval pond with a ring of grey stones around the edge, flat blue water surface slightly lower than the rim. (ракурс: модуль) | `WAT-02_Water_Pond_Oval.png` | принято |
| WAT-03 | `FMS_Water_Puddle_Round` | ядро |  | very flat round puddle of blue-grey water with a thin rim of wet brown soil. (ракурс: модуль) | `WAT-03_Water_Puddle_Round.png` | принято условно (толще и с травой/камнями; в 3D плоская лужа) |
| WAT-04 | `FMS_Water_Puddle_Irregular` | расширение |  | a very thin flat irregular patch of blue-grey water lying directly on flat ground, only a few centimetres thick, with a thin slightly darker wet rim, like a puddle after rain: nothing else in the picture, no plants, no reeds, no stones, no dock, no lily pads, no soil mound, no ground slab. (ракурс: модуль) | `WAT-04_Water_Puddle_Irregular.png` | принято (v2) |
| WAT-05 | `FMS_Water_Stream_Straight` | ядро |  | straight segment of a stream: a sunken blue water strip between two earth banks with a few grey stones. (ракурс: модуль) | `WAT-05_Water_Stream_Straight.png` | принято (берега с травой) |
| WAT-06 | `FMS_Water_Stream_Curve` | ядро |  | 90-degree curved segment of a stream: a sunken blue water strip between two earth banks with a few grey stones. (ракурс: модуль) | `WAT-06_Water_Stream_Curve.png` | принято (берега с травой) |
| WAT-07 | `FMS_Water_Stream_End` | расширение |  | start of a stream: a small spring where water comes out of a pile of grey stones and runs down a short channel between earth banks. (ракурс: модуль) | `WAT-07_Water_Stream_End.png` | принято |
| WAT-08 | `FMS_Water_LilyPads` | расширение |  | three green lily pads of different sizes with one pink lotus flower, flat, floating. (ракурс: стандарт) | `WAT-08_Water_LilyPads.png` | принято |
| WAT-09 | `FMS_Water_Bridge_Wood` | ядро |  | short wooden footbridge: flat deck of eight planks, two side railings with posts, two thick support beams resting on small stone footings at both ends. (ракурс: стандарт) | `WAT-09_Water_Bridge_Wood.png` | принято |

### Земля (модульные плитки) (GRD)

| ID | Файл меша | Очередь | Пилот | Описание модели для промпта | Картинка | Статус |
|---|---|---|---|---|---|---|
| GRD-01 | `FMS_Ground_Grass_4x4` | ядро |  | square slab of ground: a bright faceted green grass top and three layers of brown soil visible on the sides. (ракурс: модуль) | `GRD-01_Ground_Grass_4x4.png` | принято |
| GRD-02 | `FMS_Ground_Dirt_4x4` | ядро |  | square slab of ground: a light brown packed dirt top and three layers of brown soil visible on the sides. (ракурс: модуль) | `GRD-02_Ground_Dirt_4x4.png` | принято (травинки сверху убрать в 3D) |
| GRD-03 | `FMS_Ground_Edge` | ядро |  | square slab of ground, half bright faceted grass and half light brown dirt with a zigzag boundary, three layers of brown soil on the sides. (ракурс: модуль) | `GRD-03_Ground_Edge.png` | принято |
| GRD-04 | `FMS_Ground_Corner_Out` | расширение |  | square slab of ground, light brown dirt with a grass-covered corner area and a zigzag boundary, three layers of brown soil on the sides. (ракурс: модуль) | `GRD-04_Ground_Corner_Out.png` | принято |
| GRD-05 | `FMS_Ground_Corner_In` | расширение |  | square slab of ground, bright faceted grass with a dirt-covered corner area and a zigzag boundary, three layers of brown soil on the sides. (ракурс: модуль) | `GRD-05_Ground_Corner_In.png` | принято (камешки на земле убрать) |
| GRD-06 | `FMS_Ground_Hill` | расширение |  | square slab of ground with a gentle round faceted grass hill in the middle, three layers of brown soil on the sides. (ракурс: модуль) | `GRD-06_Ground_Hill.png` | принято (холм низковат) |

## 5. Что дальше

1. Сгенерировать пилоты и утвердить общий блок.
2. Сгенерировать остальные картинки, вести статус в колонке «Статус».
3. Шаг 6: на основе утверждённых картинок составить 3D-промпты (объём, обратная сторона, разделение частей, габариты и бюджет из FARM_NATURE_PACK.md).