# FarmMachinery — Э12: проверка PNG

Тексты взяты из Media обеих карточек PACKAGE_METADATA.md. Скрипт проверяет повторно открытый RGB PNG и публикует файл после проверки.

- Для нативных кадров ожидается побитовое совпадение декодированных RGB-пикселей с Unity-исходником вне указанных прямоугольников оформления.
- Для карточек 420 px и составных кадров эталон — явно указанные кадрирование и/или масштабирование исходника. Каждая вставка совпадает с этим эталоном, вне плашек нет цветокоррекции или дорисовки.
- Иконки — разрешённое исключение: ImageGen по Unity-рендерам, с уголком 3D. Их эталон — выбранное изображение из layout/icons, масштабированное к размеру файла. Проверка на совпадение иконки с raw не применяется.

| Файл | Эталонные регионы | Допустимая перекрывающая графика (координаты в пикселях) | Разница RGB |
|---|---|---|---:|
| Lite/01_Icon.png | generated/Icon_Lite → 160×160 @ (0,0), Lanczos | — | 0 |
| Lite/01_Icon_1024.png | generated/Icon_Lite → 1024×1024 @ (0,0), Lanczos | — | 0 |
| Lite/01_Icon_60_check.png | generated/Icon_Lite → 60×60 @ (0,0), Lanczos | — | 0 |
| Lite/02_Card.png | Card_Lite → 420×280 @ (0,0), Lanczos | (0, 178, 420, 280), (11, 11, 56, 30) | 0 |
| Lite/02_Card_1260x840.png | Card_Lite → 1260×840 @ (0,0), native pixels | (0, 533, 1260, 840), (34, 34, 170, 92) | 0 |
| Lite/03_Cover.png | Cover_Lite → 1950×1300 @ (0,0), native pixels | (0, 1014, 1950, 1300), (53, 52, 264, 142) | 0 |
| Lite/04_Social.png | Social_Lite → 1200×630 @ (0,0), native pixels | — | 0 |
| Lite/05_Hero.png | Hero_Lite → 1920×1080 @ (0,0), native pixels | (28, 954, 340, 1058) | 0 |
| Lite/06_FullCollection.png | Catalog/06_FullCollection_Lite, crop (10, 38, 1910, 1024) → 1665×864 @ (127,12), Lanczos | — | 0 |
| Lite/07_Closeups.png | Demo_FieldWork_CloseCMP01 → 780×439 @ (106,30), Lanczos<br>Demo_FieldWork_LowNode_Plough → 780×439 @ (1034,30), Lanczos<br>Closeup_Lite_RearLinkage → 594×334 @ (44,529), Lanczos<br>Closeup_Lite_Sprayer → 594×334 @ (662,529), Lanczos<br>Closeup_Lite_Tipper → 594×334 @ (1280,529), Lanczos | — | 0 |
| Lite/08_VariantsAndModules.png | Catalog/08_Modularity_Lite, crop (145, 239, 465, 399) → 260×130 @ (50,148), Lanczos<br>Catalog/08_Modularity_Lite, crop (620, 255, 1220, 397) → 432×102 @ (317,162), Lanczos<br>Catalog/08_Modularity_Lite, crop (175, 392, 434, 584) → 260×193 @ (50,398), Lanczos<br>Catalog/08_Modularity_Lite, crop (620, 450, 752, 572) → 269×249 @ (398,370), Lanczos<br>Catalog/08_Modularity_Lite, crop (120, 578, 415, 845) → 260×235 @ (50,658), Lanczos<br>Catalog/08_Modularity_Lite, crop (535, 576, 848, 848) → 287×249 @ (389,651), Lanczos<br>Catalog/08_Modularity_Lite, crop (1410, 222, 1840, 870) → 381×574 @ (785,207), Lanczos<br>Catalog/08_ColourVariants_Lite, crop (122, 190, 1839, 945) → 537×236 @ (1268,30), Lanczos<br>Catalog/08_Poses_Lite, crop (116, 142, 1825, 929) → 512×236 @ (1281,321), Lanczos<br>Catalog/08_AttachPoints_Lite, crop (265, 135, 1762, 957) → 430×236 @ (1322,612), Lanczos | — | 0 |
| Lite/09_Technical.png | Catalog/09_Technical_Lite, crop (80, 112, 1828, 1030) → 1296×681 @ (34,163), Lanczos | — | 0 |
| Lite/10_DemoAndVersion.png | Demo_FieldWork_Overview → 1188×668 @ (40,129), Lanczos | — | 0 |
| Full/01_Icon.png | generated/Icon_Full → 160×160 @ (0,0), Lanczos | — | 0 |
| Full/01_Icon_1024.png | generated/Icon_Full → 1024×1024 @ (0,0), Lanczos | — | 0 |
| Full/01_Icon_60_check.png | generated/Icon_Full → 60×60 @ (0,0), Lanczos | — | 0 |
| Full/02_Card.png | Card_Full → 420×280 @ (0,0), Lanczos | (0, 178, 420, 280), triangle ((0, 0), (50, 0), (0, 50)) | 0 |
| Full/02_Card_1260x840.png | Card_Full → 1260×840 @ (0,0), native pixels | (0, 533, 1260, 840), triangle ((0, 0), (152, 0), (0, 152)) | 0 |
| Full/03_Cover.png | Cover_Full → 1950×1300 @ (0,0), native pixels | (0, 1014, 1950, 1300), triangle ((0, 0), (236, 0), (0, 236)) | 0 |
| Full/04_Social.png | Social_Full → 1200×630 @ (0,0), native pixels | — | 0 |
| Full/05_Hero.png | Hero_Full → 1920×1080 @ (0,0), native pixels | (28, 954, 340, 1058) | 0 |
| Full/06_FullCollection.png | Catalog/06_FullCollection_Full, crop (10, 38, 1910, 1024) → 1665×864 @ (127,12), Lanczos | — | 0 |
| Full/07_Closeups.png | Demo_Harvest_LowNode_Header → 780×439 @ (106,30), Lanczos<br>Demo_Harvest_CloseHaymaking → 780×439 @ (1034,30), Lanczos<br>Demo_Harvest_CloseGrainYard → 594×334 @ (44,529), Lanczos<br>Demo_FieldWork_LowNode_Plough → 594×334 @ (662,529), Lanczos<br>Demo_FieldWork_CloseCMP01 → 594×334 @ (1280,529), Lanczos | — | 0 |
| Full/08_VariantsAndModules.png | Catalog/08_Modularity, crop (199, 185, 485, 422) → 260×215 @ (50,106), Lanczos<br>Catalog/08_Modularity, crop (596, 265, 1225, 422) → 432×108 @ (317,159), Lanczos<br>Catalog/08_Modularity, crop (203, 438, 383, 606) → 260×243 @ (50,373), Lanczos<br>Catalog/08_Modularity, crop (629, 456, 1044, 609) → 432×159 @ (317,415), Lanczos<br>Catalog/08_Modularity, crop (116, 622, 413, 880) → 260×226 @ (50,662), Lanczos<br>Catalog/08_Modularity, crop (555, 626, 854, 880) → 293×249 @ (386,651), Lanczos<br>Catalog/08_Modularity, crop (1352, 170, 1840, 910) → 381×578 @ (785,205), Lanczos<br>Catalog/08_ColourVariants, crop (410, 50, 1515, 1040) → 263×236 @ (1405,30), Lanczos<br>Catalog/08_Poses, crop (116, 142, 1825, 929) → 512×236 @ (1281,321), Lanczos<br>Catalog/08_AttachPoints, crop (265, 135, 1762, 957) → 430×236 @ (1322,612), Lanczos | — | 0 |
| Full/09_Technical.png | Catalog/09_Technical, crop (80, 45, 1828, 1042) → 1296×739 @ (34,134), Lanczos | — | 0 |
| Full/10_DemoAndVersion.png | Demo_Harvest_Overview → 1188×668 @ (40,129), Lanczos | — | 0 |
| Full/11_CategoryDetails.png | Catalog/11_Category_Harvest, crop (389, 101, 766, 418) → 321×270 @ (103,38), Lanczos<br>Catalog/06_FullCollection_Full, crop (528, 126, 688, 316) → 227×270 @ (613,38), Lanczos<br>Catalog/06a_Machines, crop (680, 770, 853, 944) → 268×270 @ (1056,38), Lanczos<br>Catalog/11_Category_Harvest, crop (1384, 190, 1610, 383) → 316×270 @ (1495,38), Lanczos<br>Catalog/06a_Machines, crop (323, 106, 551, 312) → 269×243 @ (361,357), Lanczos<br>Catalog/06a_Machines, crop (1015, 103, 1218, 296) → 256×243 @ (1295,357), Lanczos<br>Catalog/11_Category_Harvest, crop (134, 776, 566, 1034) → 414×247 @ (57,649), Lanczos<br>Catalog/11_Category_Harvest, crop (662, 776, 1080, 1034) → 400×247 @ (527,649), Lanczos<br>Catalog/11_Category_Harvest, crop (1177, 797, 1486, 1004) → 369×247 @ (1005,649), Lanczos<br>Catalog/11_Category_Harvest, crop (1577, 831, 1797, 1014) → 297×247 @ (1504,649), Lanczos | — | 0 |
| Full/12_Compositions.png | Catalog/12_CMP_01 → 780×439 @ (106,30), Lanczos<br>Catalog/12_CMP_02 → 780×439 @ (1034,30), Lanczos<br>Catalog/12_CMP_03 → 594×334 @ (44,529), Lanczos<br>Catalog/12_CMP_04 → 594×334 @ (662,529), Lanczos<br>Catalog/12_CMP_05 → 594×334 @ (1280,529), Lanczos | — | 0 |
| Full/13_Materials.png | Catalog/13_Materials_Models, crop (100, 164, 1193, 911) → 1092×746 @ (70,137), Lanczos<br>Catalog/13_Atlas_Red → 234×234 @ (1255,59), nearest<br>Catalog/13_Atlas_Green → 234×234 @ (1255,336), nearest<br>Catalog/13_Atlas_Blue → 234×234 @ (1255,613), nearest | — | 0 |
| Full/14_UnityAndComparison.png | Catalog/14_Unity_Full → 1208×680 @ (36,81), Lanczos | — | 0 |

## Визуальная проверка

- Карточки 420×280 проверены при размере 1:1. Заголовки, акцентные строки и верхние бейджи читаются. Кромки плашек карточек и обложек проходят ниже техники.
- Проверены иконки 160×160 и 60×60. Узнаются трактор Lite и комбайн с жаткой Full. Уголок 3D различим в обоих размерах. Метка LITE в файле 60×60 читается мельче уголка.
- Проверены 16 кадров галереи. Плашки не перекрывают модели и подписи. В Lite 10 содержимое Full представлено только текстом с заголовком «FULL ONLY — NOT INCLUDED IN LITE». На Full 13 видны все три атласа и три цветовых варианта трактора.

## 2026-11-26. ?????????? Full ????? ?????????? Lite ? Full

- ???? 10 ?????????? ?? ???????? Full ? ???????? ?4 DEMO SCENES: FIELD WORK · HARVEST · 2 CATALOGUES?. ??????? RGB ? ???????? ???????? ????? ??????????????? ? 0.
- ???? 14 ?????????? ?????????? Unity-???????? ? ????? ??????? `Assets > FarmMachinery > Full > Art > Prefabs > HRV`. SHA-256 ????????? PNG ? `b901c399e112941ebeac330752b9e684e35986d74182294cc9ad80d81ad54f44`. ??????? RGB ????? ??????????????? ? 0. ? ?????? DEMO SCENES ??????? Lite 2, Full 4.
- SHA-256 ????????? 28 ????????? PNG ??????? ?? ? ????? ??????????.
