# FarmMachinery — Э12 Trial

Декоративные растровые макеты для просмотра владельцем. В каждом запросе на редактирование первый исходник — реальный Unity-рендер из `../raw/` либо пробный вариант, с исходным рендером во втором входе при повторном выравнивании. Оформление создал ImageGen из сессии `gpt-6.2-sol`. Pillow использовался для численной проверки и экспорта требуемых размеров.

Систему плашек сверил с `02_Card`, `03_Cover` и `01_Icon` Farm Processing, а выбор масштаба и композиции — с черновыми `02_Card` и `03_Cover` Farm Market. Раздел «Что видит покупатель» использовал для сравнения иерархии форматов. Оставил прямую графитовую плашку, кремовый заголовок, более тонкую красную полосу и пустое место слева под логотип. У Lite есть верхний угловой LITE, у Full верхнего бейджа нет. У Hero только небольшая двухстрочная подпись снизу слева.

## Приёмка пробных файлов

- Визуально сверил состав, силуэты, мелкие детали и цвет с каждым исходником. Проверил точное начертание строк в выбранных пробах и читаемость Card на 420 × 280. На 160 и 60 px трактор и комбайн с жаткой различимы. Надпись LITE на 60 px хорошо различима как бейдж, сами буквы мелкие.
- Все 7 выбранных композиций имеют отличия в изображении техники. Суффикс `_preview_only` добавлен к мастерам, уменьшенным файлам и проверкам 60 px. Для публикации требуется верстка поверх исходных машин без генеративных изменений.
- На выбранных пробах плашки не закрывают технику. Фактическая высота плашки Card Full — 34,6%, примерно на 0,4 процентного пункта ниже ориентира. ImageGen даёт близкие, но не везде побитово точные цвета.
- В оригинальном `Cover_Full.png` на дальнем плане видны круглые тюки. Они сохранены в декоративной пробе. Для магазинной версии нужен исходный Unity-рендер, учитывающий решение о составе пака.

## Цвет и доля плашек

Целевые цвета — графит `#20242A`, красный `#C8473B`, кремовый `#F2E6C9` и тёмный бирюзовый фон иконок `#173C45`. Ниже — медианы свободных участков, доля высоты дана вместе с полосой для Card и Cover.

```text
Icon_Lite background #15414A
Icon_Full background #174149
Card_Lite plate 36.2 dark #22262C accent #D04338
Card_Full plate 34.6 dark #25292D accent #C74939
Cover_Lite plate 24.0 dark #20252C accent #D1463A
Cover_Full plate 21.0 dark #22262C accent #C8473B
Hero_Lite plate 9.1 dark #25292E
```

## Проверка исходной техники

Для каждой попытки сравнил участки техники после масштабирования кандидата к исходному разрешению. MAE — средняя абсолютная разница RGB от 0 до 255. SSIM — среднее структурное сходство яркости в окнах 8 × 8 внутри выбранных областей без геометрической подгонки, поэтому показатель реагирует и на сдвиг. Часть прямоугольников включает края модели. Результаты дополняют визуальную сверку, а не заменяют её.

| Исходник | Попытка | PNG ImageGen | MAE | SSIM | Решение |
|---|---:|---|---:|---:|---|
| Icon_Lite.png | 1 | 1254 × 1254 | 5.556 | 0.96432 | Выбрано для пробы. LITE точный, исходный трактор узнаваем, но изменились контур протектора и светлые грани обода. |
| Icon_Full.png | 1 | 1254 × 1254 | 52.969 | 0.29178 | Отклонено. Машина выше исходного положения, наибольшие расхождения в жатке и колёсах. |
| Icon_Full.png | 2 | 1254 × 1254 | 15.713 | 0.82226 | Выбрано для пробы. Крупные контуры ближе к исходнику, но отдельные рейки мотовила, блики и шины перерисованы. |
| Card_Lite.png | 1 | 1536 × 1024 | 4.809 | 0.93712 | Не выбрано. Текст точный, но слева красная строка начиналась не на оси заголовка. |
| Card_Lite.png | 2 | 1536 × 1024 | 5.669 | 0.92656 | Выбрано для пробы. Одинаковый отступ строк, LITE и точный текст на 420 × 280. Есть отличия на гранях кабины и колёс. |
| Card_Full.png | 1 | 1536 × 1024 | 42.910 | 0.28181 | Отклонено. Текст точный, но комбайн смещён вверх, контуры не совпадают с исходником. |
| Card_Full.png | 2 | 1536 × 1024 | 6.059 | 0.91293 | Выбрано для пробы. Жатка выше плашки, текст точный, сохранились различия в деталях мотовила и колёс. |
| Cover_Lite.png | 1 | 1536 × 1024 | 6.543 | 0.93475 | Не выбрано. Текст точный, но разный левый отступ заголовка и акцентной строки. |
| Cover_Lite.png | 2 | 1536 × 1024 | 8.369 | 0.91983 | Выбрано для пробы. Заголовок и акцент выровнены, LITE читается, есть отклонения в оттенках и мелких гранях тракторов. |
| Cover_Full.png | 1 | 1536 × 1024 | 8.184 | 0.90334 | Отклонено. Текст точный, но плашка вплотную подошла к нижнему краю жатки. |
| Cover_Full.png | 2 | 1536 × 1024 | 9.208 | 0.89278 | Выбрано для пробы. Между жаткой и плашкой есть зазор, однако колёса и мотовило перерисованы. Тюки уже есть в исходнике. |
| Hero_Lite.png | 1 | 1672 × 941 | 4.925 | 0.94851 | Выбрано для пробы. FIELD WORK и заголовок точные, плашка вне техники. Отличаются детали ободов и дальних орудий. |

<details>
<summary>Области проверки</summary>

Координаты даны в базе указанного размера, перед сравнением пропорционально приводятся к размеру исходника. Формат прямоугольника — left, top, right, bottom.

```json
{
  "Icon_Lite": [
    1024,
    1024,
    [
      [
        175,
        486,
        405,
        591
      ],
      [
        457,
        221,
        660,
        292
      ],
      [
        520,
        345,
        605,
        469
      ],
      [
        286,
        714,
        458,
        835
      ],
      [
        650,
        522,
        865,
        695
      ],
      [
        553,
        441,
        839,
        540
      ]
    ]
  ],
  "Icon_Full": [
    1024,
    1024,
    [
      [
        352,
        347,
        500,
        473
      ],
      [
        580,
        311,
        812,
        402
      ],
      [
        812,
        309,
        915,
        421
      ],
      [
        538,
        510,
        685,
        641
      ],
      [
        94,
        514,
        335,
        735
      ],
      [
        309,
        668,
        465,
        805
      ]
    ]
  ],
  "Card_Lite": [
    1260,
    840,
    [
      [
        330,
        250,
        480,
        345
      ],
      [
        488,
        93,
        683,
        242
      ],
      [
        614,
        250,
        773,
        413
      ],
      [
        411,
        387,
        537,
        481
      ],
      [
        786,
        236,
        938,
        302
      ],
      [
        959,
        253,
        1006,
        301
      ]
    ]
  ],
  "Card_Full": [
    1260,
    840,
    [
      [
        517,
        113,
        714,
        233
      ],
      [
        668,
        123,
        936,
        263
      ],
      [
        645,
        269,
        758,
        376
      ],
      [
        303,
        283,
        512,
        470
      ],
      [
        449,
        397,
        592,
        499
      ]
    ]
  ],
  "Cover_Lite": [
    1920,
    1280,
    [
      [
        278,
        555,
        558,
        708
      ],
      [
        498,
        370,
        772,
        603
      ],
      [
        695,
        601,
        910,
        772
      ],
      [
        850,
        130,
        1113,
        256
      ],
      [
        1132,
        115,
        1358,
        204
      ],
      [
        1438,
        89,
        1581,
        157
      ]
    ]
  ],
  "Cover_Full": [
    1920,
    1280,
    [
      [
        1199,
        566,
        1450,
        737
      ],
      [
        1115,
        826,
        1333,
        957
      ],
      [
        1191,
        731,
        1333,
        798
      ],
      [
        447,
        410,
        768,
        570
      ],
      [
        907,
        328,
        1107,
        459
      ],
      [
        1067,
        98,
        1220,
        257
      ],
      [
        1166,
        268,
        1293,
        363
      ],
      [
        543,
        359,
        596,
        404
      ]
    ]
  ],
  "Hero_Lite": [
    1920,
    1080,
    [
      [
        381,
        782,
        671,
        952
      ],
      [
        482,
        731,
        607,
        815
      ],
      [
        702,
        746,
        930,
        842
      ],
      [
        533,
        407,
        769,
        603
      ],
      [
        1007,
        279,
        1226,
        426
      ],
      [
        1245,
        88,
        1414,
        177
      ],
      [
        1490,
        138,
        1568,
        179
      ]
    ]
  ]
}
```

</details>

## Icon_Lite

Выбрана попытка 1. Экспорт из этой генерации:

- [01_Icon_Lite_1024_preview_only.png](../final/_draft/01_Icon_Lite_1024_preview_only.png) · 1024 × 1024 px
- [01_Icon_Lite_160_preview_only.png](../final/_draft/01_Icon_Lite_160_preview_only.png) · 160 × 160 px
- [01_Icon_Lite_60_preview_only.png](../final/_draft/01_Icon_Lite_60_preview_only.png) · 60 × 60 px

### Промпт 1

```text
Make a square 1024 × 1024 store icon. The single red cab tractor is locked to the source exactly, including silhouette, size, gutters and every vehicle pixel. Replace only the surrounding field and grass outside its silhouette with an opaque, flat uniform deep teal #173C45 matching the series icon mood. No new ground objects, border or title. Add one small red #C8473B upper-left rectangular tag (width 19%, height 7.5%, inset 4%), exact cream bold uppercase text “LITE”. Do not overlap any machine pixel. No other text. It should read as a machine at 60 pixels. Do not smooth, recolour or relight the model.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.
```

## Icon_Full

Выбрана попытка 2. Экспорт из этой генерации:

- [01_Icon_Full_1024_preview_only.png](../final/_draft/01_Icon_Full_1024_preview_only.png) · 1024 × 1024 px
- [01_Icon_Full_160_preview_only.png](../final/_draft/01_Icon_Full_160_preview_only.png) · 160 × 160 px
- [01_Icon_Full_60_preview_only.png](../final/_draft/01_Icon_Full_60_preview_only.png) · 60 × 60 px

### Промпт 1

```text
Make a square 1024 × 1024 store icon. The single red combine with attached reel header is locked to the source exactly, including silhouette, size, gutters and every vehicle pixel. Replace only the surrounding field and grass outside its silhouette with an opaque, flat uniform deep teal #173C45 matching the series icon mood. No new ground objects, border or title. No badge, logo or text. It should read as a machine at 60 pixels. Do not smooth, recolour or relight the model.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

Use its teal colour only. The Full icon has no LITE badge and no text.
```

### Промпт 2

```text
Make a square 1024 × 1024 store icon. The single red combine with attached reel header is locked to the source exactly, including silhouette, size, gutters and every vehicle pixel. Replace only the surrounding field and grass outside its silhouette with an opaque, flat uniform deep teal #173C45 matching the series icon mood. No new ground objects, border or title. No badge, logo or text. It should read as a machine at 60 pixels. Do not smooth, recolour or relight the model.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. There is only one input; preserve its actual art. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

Mask-only restyle. Conceptual polygon mask to lock the complete combine at the input positions: the exhaust reaches down to y=19% from top at x=77%, the header's extreme close yellow divider reaches y=85% at x=30%, and the body right edge reaches x=91%. Keep the reel bars, all end dividers, flat body panels and tyres with original geometry and exactly those coordinates. Only choose the solid opaque deep teal background matching #173C45. No repositioning or enlarging, no crop, no ground contour, no logo, badge or text.
```

## Card_Lite

Выбрана попытка 2. Экспорт из этой генерации:

- [02_Card_Lite_1260x840_preview_only.png](../final/_draft/02_Card_Lite_1260x840_preview_only.png) · 1260 × 840 px
- [02_Card_Lite_420x280_preview_only.png](../final/_draft/02_Card_Lite_420x280_preview_only.png) · 420 × 280 px

### Промпт 1

```text
Create a 3:2 card trial at 1260 × 840 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 37% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (8% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 10% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “13 MODELS · LOW POLY · URP”, left-aligned with the title, large enough for a 420 × 280 reduction. Add only one small red #C8473B rectangular upper-left edition badge saying “LITE” in the exact cream uppercase face, ~10% canvas width, 6% height, placed over free pixels so no machine is obscured. Use actual centered dots ·, never periods or dash shapes. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.
```

### Промпт 2

```text
Edit input one for one simple grid change. The series heading and accent line need one shared left margin. Within the bottom full-width red strip, move the existing cream text horizontally to the right until its left edge is aligned exactly below the left edge of the main cream headline. Clear the old lettering and preserve plain red background in its place. Use the exact wording and raised middle dots “13 MODELS · LOW POLY · URP”. The top says exactly “LITE” and the dark footer already says exactly “FARM MACHINERY”; keep both where they are. Preserve plate height, color, blank logo slot, typography and complete 3:2 framing. Preserve every pixel of the actual machinery and landscape. Input two is its original unaltered Unity rendering; do not change the tractors, wheels, plough or scenery, and leave all machines clear above the plate. The change is the horizontal positioning of the claim only. No new copy or visual elements.
```

## Card_Full

Выбрана попытка 2. Экспорт из этой генерации:

- [02_Card_Full_1260x840_preview_only.png](../final/_draft/02_Card_Full_1260x840_preview_only.png) · 1260 × 840 px
- [02_Card_Full_420x280_preview_only.png](../final/_draft/02_Card_Full_420x280_preview_only.png) · 420 × 280 px

### Промпт 1

```text
Create a 3:2 card trial at 1260 × 840 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 37% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (8% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 10% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “26 MODELS + 5 COMPOSITIONS”, left-aligned with the title, large enough for a 420 × 280 reduction. The Full edition has no top badge. Preserve the plus sign and spaces in the claim. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

Match input 2's title scale, left empty logo space, full-width rectangular plate proportion and cream typography. Full copy only, no badge.
```

### Промпт 2

```text
Create a 3:2 card trial at 1260 × 840 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 37% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (8% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 10% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “26 MODELS + 5 COMPOSITIONS”, left-aligned with the title, large enough for a 420 × 280 reduction. The Full edition has no top badge. Preserve the plus sign and spaces in the claim. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. There is only one input; preserve its actual art. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

Precision overlay aligned to input 1 with no crop/reframe and no shift at all. Keep empty field space in y=63% to bottom, use only that space for graphics. The source combine far top exhaust is at x=67%, y=7%; the yellow near divider tip at x=37%, y=62%; the left reel end around x=22%, y=34%. Do not move or change any of these parts. Full-width graphite title band and thinner red strip, use the literal exact text “FARM MACHINERY” on the dark band with a clear empty logo square on the left and “26 MODELS + 5 COMPOSITIONS” on red, no upper tag. Reserve the same sized late title start around x=18% and same strong heavy simple sans as the Lite card. Do not decorate any part of the render outside the two straight horizontal graphic rectangles.
```

## Cover_Lite

Выбрана попытка 2. Экспорт из этой генерации:

- [03_Cover_Lite_1950x1300_preview_only.png](../final/_draft/03_Cover_Lite_1950x1300_preview_only.png) · 1950 × 1300 px

### Промпт 1

```text
Create a 3:2 cover trial at 1950 × 1300 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 22% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (6% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 8% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “13 MODELS · LOW POLY · URP”, left-aligned with the title, large enough for a 420 × 280 reduction. Add only one small red #C8473B rectangular upper-left edition badge saying “LITE” in the exact cream uppercase face, ~10% canvas width, 6% height, placed over free pixels so no machine is obscured. Use actual centered dots ·, never periods or dash shapes. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

Footer begins at exactly y=77% or slightly lower. Match Card_Lite visual system: very heavy cream type and flat graphite/red bars, one LITE badge. Use actual dots, not a dash.
```

### Промпт 2

```text
Edit input one for one simple grid change. The series heading and accent line need one shared left margin. Within the bottom full-width red strip, move the existing cream text horizontally to the right until its left edge is aligned exactly below the left edge of the main cream headline. Clear the old lettering and preserve plain red background in its place. Use the exact wording and raised middle dots “13 MODELS · LOW POLY · URP”. The top says exactly “LITE” and the dark footer already says exactly “FARM MACHINERY”; keep both where they are. Preserve plate height, color, blank logo slot, typography and complete 3:2 framing. Preserve every pixel of the actual machinery and landscape. Input two is its original unaltered Unity rendering; do not change the tractors, wheels, plough or scenery, and leave all machines clear above the plate. The change is the horizontal positioning of the claim only. No new copy or visual elements.
```

## Cover_Full

Выбрана попытка 2. Экспорт из этой генерации:

- [03_Cover_Full_1950x1300_preview_only.png](../final/_draft/03_Cover_Full_1950x1300_preview_only.png) · 1950 × 1300 px

### Промпт 1

```text
Create a 3:2 cover trial at 1950 × 1300 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 22% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (6% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 8% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “26 MODELS + 5 COMPOSITIONS”, left-aligned with the title, large enough for a 420 × 280 reduction. The Full edition has no top badge. Preserve the plus sign and spaces in the claim. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.
```

### Промпт 2

```text
Create a 3:2 cover trial at 1950 × 1300 with graphic overlays only. Retain original scene pixels above footer except the badge if applicable. Limit the full-width footer to the bottom 20% clear of all machines. The footer is a straight flat solid dark #20242A headline block above a thin full-width red #C8473B accent strip (6% of total image height). Inside the main dark graphite band, start at 5% margin with a wholly empty square about 8% of canvas width for a future logo. The square is the very same dark fill as the main plate, no outline and no graphic. Start the oversized cream #F2E6C9 bold one-line title “FARM MACHINERY” to its right, all caps, left-aligned. Under it in the red strip put one single claim exactly “26 MODELS + 5 COMPOSITIONS”, left-aligned with the title, large enough for a 420 × 280 reduction. The Full edition has no top badge. Preserve the plus sign and spaces in the claim. Match the source ratio, exact framing and position of all model edges; do not crop or enlarge the image.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.

PRIORITY: plate can only start at 80% down the canvas, so it is bottom 20% and the entire reel cutter and orange end divider keep at least 1.5% image-height clearance above the plate. Preserve all pixels and model positions of source image 1. Do not zoom, shift or rearrange the image. Same dark band over shorter bright red bottom strip. Correct exact typography.
```

## Hero_Lite

Выбрана попытка 1. Экспорт из этой генерации:

- [05_Hero_Lite_1920x1080_preview_only.png](../final/_draft/05_Hero_Lite_1920x1080_preview_only.png) · 1920 × 1080 px

### Промпт 1

```text
Make a 1920 × 1080, 16:9 gallery plate version. Overlay only one small flat solid #20242A rectangle in the lower-left, approximately x=1.3% to 18% and y=89% to 98.5%. The actual tractor silhouette begins well to its right. Keep all source content exactly at its original coordinates, including the complete tractor, plough and other equipment. Inside the plate use one bold cream line “FARM MACHINERY” then a smaller cream line “FIELD WORK”, left-aligned and comfortably padded. No other text or graphic. No frame or badge.

Edit IMAGE 1 (an actual Unity render). Preserve the input scene framing and every machine pixel verbatim at the same coordinates. The vehicles, their tyres, cabs, crop headers, small attachments, hardware, color, lighting, shadows and equipment count are protected and may not be redrawn, recoloured, restyled, re-lit, moved or resized. Never redraw anything under an overlay, just place graphical shapes in the stated open space. Use image 2 only for graphic hierarchy or icon background inspiration, never for objects, branding or text. Use simple flat matte blocks and bold conventional Arial-like sans in cream #F2E6C9. No logo, fake logo, NEW or award badges, gradients in graphic plates, borders, extra language or other decorations. Write the provided lettering and punctuation exactly.
```

## Э12 · финальные иконки

ImageGen, модель сессии `gpt-6.2-sol`. Источники — реальные Unity-рендеры и пробные иконки как ориентир оформления. Для каждого продукта выбрана первая попытка.

### Lite

Оригинал Unity — `../raw/Icon_Lite.png`. Ориентир оформления — `../final/_draft/01_Icon_Lite_1024_preview_only.png`.

```text
Square 1:1, opaque 1024px store icon. Input 1 is the actual Unity source render and sets the real machine shape, color, geometry, perspective and identifying parts. Input 2 is an approved graphic mood/layout trial only. Keep one machine faithfully matching input 1. One red TRC-01 cab tractor, original compact cab and cream rims, larger rear tyres, front ballast and red mudguards. Add a small separate horizontal red LITE tag with bold white exact lettering LITE directly below the triangle, x around 4–25%, y around 24–32%, fully in empty background, never covering machine. Replace the environment/background with a clean deep muted teal #173C45 backdrop, subtle tonal depth only, and a soft restrained contact shadow. No crop on machine, fill roughly 72–78% of canvas, center slightly right/down to leave empty upper left. In the absolute top-left corner add a flat red right triangular corner tab #C8473B, approximately 25% of the image width and height, with the two short square legs flush with the top and left canvas edges. Place very clear bold snug WHITE horizontal text '3D' inside the triangle near the upper left, no rotated letters, no other marks. Strong clean silhouettes and chunky details clear at 160 and 60 px. No graphics elsewhere, no logo, no title, no extra machinery. Match the existing real geometry as closely as possible, unbranded, matte faceted Unity low-poly, no new mechanical details.
```

Выбрана попытка 1. На иконке один красный TRC-01 с кремовыми дисками, уголком 3D и меткой LITE. [Мастер](icons/Icon_Lite.png) · [160 px](../../Lite/Media/final/01_Icon.png) · [60 px](../../Lite/Media/final/01_Icon_60_check.png).

### Full

Оригинал Unity — `../raw/Icon_Full.png`. Ориентир оформления — `../final/_draft/01_Icon_Full_1024_preview_only.png`.

```text
Square 1:1, opaque 1024px store icon. Input 1 is the actual Unity source render and sets the real machine shape, color, geometry, perspective and identifying parts. Input 2 is an approved graphic mood/layout trial only. Keep one machine faithfully matching input 1. One red HRV-01 combine with exactly the wide gray reel and red ATT-03 grain header mounted, yellow dividers, front cab, cream hubs, and folded silver-gray unload tube. No LITE tag or any other copy. Replace the environment/background with a clean deep muted teal #173C45 backdrop, subtle tonal depth only, and a soft restrained contact shadow. No crop on machine, fill roughly 72–78% of canvas, center slightly right/down to leave empty upper left. In the absolute top-left corner add a flat red right triangular corner tab #C8473B, approximately 25% of the image width and height, with the two short square legs flush with the top and left canvas edges. Place very clear bold snug WHITE horizontal text '3D' inside the triangle near the upper left, no rotated letters, no other marks. Strong clean silhouettes and chunky details clear at 160 and 60 px. No graphics elsewhere, no logo, no title, no extra machinery. Match the existing real geometry as closely as possible, unbranded, matte faceted Unity low-poly, no new mechanical details.
```

Выбрана попытка 1. На иконке один красный HRV-01 со смонтированной зерновой жаткой ATT-03 и уголком 3D. [Мастер](icons/Icon_Full.png) · [160 px](../../Full/Media/final/01_Icon.png) · [60 px](../../Full/Media/final/01_Icon_60_check.png).
