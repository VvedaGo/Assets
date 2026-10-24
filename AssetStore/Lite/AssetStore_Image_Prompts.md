# Картинки Asset Store — Farm Market Starter Lite

Основа — готовые рендеры из `AssetStore/Lite/Hero/`. Всё в `AssetStore/Lite/Final/` собрано из них (кадрирование, коллажи, цветокоррекция), новых сцен в Unity не снималось, кроме двух правок, описанных ниже.

## Что изменено в Hero
Рендеры `Hero/` переснял с теми же камерами, что и раньше. Старые файлы лежат в `C:\Users\Sergv\orca\backups\Hero_before_rerender`. Отличия:
1. **Меловая доска:** вместо «APPLES / POTIONS / BREAD» теперь `FRESH PRODUCE` (текстура `T_Signs_BaseColor.png`; оригинал в `C:\Users\Sergv\orca\backups\T_Signs_BaseColor.orig.png`). Подвесные вывески: `MARKET / FRESH / FARM` вместо `MARKET / TOWN / INNKEEP`.
2. **Тележка** в `Hero/04`: добавлены 3 тыквы, чтобы она выглядела полной.

## Как работать
Каждый файл ниже — это **исходник**. Промпт [GEN] отдаём генератору изображений вместе с этим файлом как референсом. Если [GEN] нет, файл готов к загрузке как есть.

Общее для всех промптов: *«Keep the 3D props exactly as in the attached image. Do not add, remove or redraw any objects. Do not add people, animals, logos or watermarks.»*
Название везде: **FARM MARKET STARTER LITE**. Шрифт: округлый жирный sans, тёмно-коричневый `#3B2A1A` с кремовой обводкой.

---

## Marketing images

### 01_Icon — 160×160
Исходник: `Final/01_Icon_source_1024.png`
```text
Use the attached image as the subject: keep the wooden crate with red tomatoes and the crate with carrot greens exactly as they are. Crop tightly so the two crates fill the frame, centred. Replace the blurred cobblestone background with a flat saturated teal-blue (#2E9BB8) with a soft lighter glow behind the crates. Add a soft contact shadow under the crates. No text, no border. Square 1024x1024, bold silhouette that stays readable at 160x160.
```

### 02_Card — 420×280
Исходник: `Final/02_Card_source_1260x840.png` (уменьшенная версия: `02_Card_base_420x280.png`)
```text
Keep the attached render. Extend the top of the canvas with about 18% plain warm grey-beige background (same colour as the render background) so the image becomes 1260x960, then crop to 1260x840 keeping the stall in the lower 80%. Add the title "FARM MARKET STARTER LITE" in the top area, two lines ("FARM MARKET" / "STARTER LITE"), chunky rounded font, dark brown #3B2A1A with a cream outline and soft shadow. Add a small green rounded ribbon "FREE" in the top-left corner. Do not cover the stall. The text must stay legible after downscaling to 420x280.
```

### 03_Cover — 1950×1300
Исходник: `Final/03_Cover_source_1950x1300.png`
```text
Keep the attached render as the left and centre of the cover. Extend the canvas to the right and above with a smooth warm peach-to-beige gradient, matching the sky colour of the render, so that the market occupies the left 60% of a 1950x1300 image and the right 40% is free space. On the right add the title "FARM MARKET STARTER LITE" in three lines (FARM MARKET / STARTER / LITE), large chunky rounded font, dark brown #3B2A1A with cream outline and soft shadow. Under it a one-line subtitle "22 low-poly props - URP - Mobile friendly" and a green rounded badge "FREE". The text must not overlap the stall or cart.
```

---

## Screenshots (1920×1080)

| № | Файл | Исходник | [GEN] |
|---|---|---|---|
| 04 | `Final/04_Hero_Showcase.png` | `Hero/04` (кадр целиком) | не нужен |
| 05 | `Final/05_Full_Collection.png` | `Hero/01` (вся композиция, кадр 16:9) | не нужен |
| 06 | `Final/06_Closeup_Effect.png` | `Hero/03` | не нужен |
| 07 | `Final/07_Variations_source.png` | коллаж из 6 крупных планов Hero | нужен |
| 08 | `Final/08_Gameplay_Use_source.png` | `Hero/01` (кадр 16:9) | нужен |
| 09 | `Final/09_Second_Environment.png` | вечерняя версия `Hero/04` (рендер той же сцены) | не нужен |
| 10 | `Final/10_Features_source.png` | коллаж 3×2 из 6 кадров Hero | нужен |
| 11 | Скриншот Unity Editor | делается вручную | не нужен |

### 07_Variations
```text
Keep the attached 3x2 collage exactly as it is (do not change the tiles). Add short clean captions under each tile in a rounded font, dark brown #3B2A1A, cream outline: "Tomatoes", "Carrots", "Apples", "Pumpkins and watermelons", "Cabbage", "Pumpkins". At the top add the heading "Produce and crates". Keep the cream background (#FFF1D6).
```

### 08_Gameplay_Use
```text
Keep the attached render exactly as it is. Add a simple generic game HUD: a coin counter "128" with a small gold coin icon in the top-left, and three empty rounded inventory slots at the bottom centre. Flat semi-transparent dark brown panels with cream text, no copied or branded UI. In the bottom-right corner add a small caption "Example HUD - not included". Do not alter the 3D scene.
```

### 10_Features_Overview
```text
Keep the attached 3x2 collage exactly as it is (do not change the tiles). Add one short caption under each tile, rounded font, dark brown #3B2A1A with cream outline: "Market stall", "Merchant cart", "Crates and baskets", "Scale and sign", "Fresh produce", "Pumpkins and tomatoes". At the top add the heading "What's inside - 22 prefabs". Keep the cream background (#FFF1D6). Do not add any other claims.
```

### 11_Unity_Setup (вручную)
Откройте `Demo_Lite_Showcase`, выделите `Assets/FarmMarketStarter/Art/Prefabs/Single/FMS_Stall_Table_Canopy.prefab`, раскройте в Project `Assets/FarmMarketStarter` (Art, Demo, Documentation). В Inspector должны быть видны Mesh Renderer с материалом `M_MarketStall` и Box Collider. Сделайте скриншот окна редактора 1920×1080 (текст интерфейса должен читаться) и сохраните как `Final/11_Unity_Setup.png`. ИИ-редактирование к нему не применять.

---

## Что проверить
1. `Final/01_Icon_source_1024.png`: кадр взят из `Hero/03`, он грубый (много дерева). Если не нравится, можно взять другой фрагмент или попросить генератор перекадрировать на корзину с яблоками.
2. `07` и `10` собраны из кропов Hero. Некоторые тайлы увеличены примерно в 1.5–2 раза и чуть мягче оригинала.
3. `09` сделан рендером той же сцены, что `Hero/04`, но с вечерним светом.
4. Если картинки редактировались генератором ИИ, отметьте это в разделе раскрытия использования ИИ в Publisher Portal.
5. Загрузка: сначала `04`, затем `05`–`09`, в конце `10` и `11`. Icon, card и cover идут в блок Marketing images.
