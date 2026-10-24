# Farm Market Starter (Full) — всё для публикации в Unity Asset Store

> Пакет: `Assets/FarmMarketFull` · ветка `FarmMarket` · версия 1.0.0
> Основа: чеклист `Searcher/ASSET_STORE_CHECKLIST.md` (эталон Synty «Simple Farm») + реальные цифры пака.
> Поля ниже оформлены блоками для копирования в Publisher Portal (publisher.unity.com).
> Пометка **[ПРОВЕРИТЬ]** = цифры, которые я не мог получить без Unity (триангулы и т.п.) или решение за тобой.

---

## 0. Состояние на сегодня

| Что | Статус |
|---|---|
| Префабы (119 одиночных + 6 композиций) | готово, не закоммичено |
| Демо-сцена `Demo_MarketSquare` | готова, есть одна сцена (в чеклисте — 2–3) |
| Картинки | 11 файлов в `AssetStore/Full/Draft`, на всех плашка «Farm Market Starter» |
| Wireframe-кадр, Lite vs Full, Unity Editor, палитра | **не сделаны** |
| YouTube-трейлер | **не сделан** |
| `Documentation/README.txt` | устарел: пишет «50 items», реально 119 префабов — переписать |
| Валидатор Asset Store Publishing Tools | не запускался |
| Проверка в чистом проекте (URP, Unity 6) | не делалась |

---

## 1. Основные поля карточки

### Title
```text
Farm Market Starter – Low Poly Vegetables, Fruits & Stalls
```
> [ПРОВЕРИТЬ] Lite-версия лежит в `Assets/FarmMarketStarter`. Если Lite называется так же, Full лучше назвать `Farm Market Starter Full – …` или Lite — `… Lite`, иначе пакеты будут путаться. На картинках надпись «Farm Market Starter», поэтому основное имя оставлено им.

### Category
```text
3D / Props / Exterior
```
(альтернатива: `3D / Environments / Fantasy`)

### Price
```text
$12.99   (старт-акция $9.99 первые 2 недели)
```
Ориентиры: Synty Simple Farm $9.99, медиана ниши $15.99. В Full 119 префабов, поэтому цену можно поднять до $14.99–$19.99 — решение за тобой.

### Keywords / Tags (до ~15)
```text
low poly, stylized, farm, farming, market, grocery, vegetables, fruit, food, props, crates, stalls, harvest, mobile, URP
```

### Хештеги для соцсетей
```text
#gamedev #unity3d #indiedev #3dassets #lowpoly #stylizedart #madewithunity #gameassets #farming
```

---

## 2. Краткое описание (Short Description)
```text
119 stylized low-poly props for farm and market scenes: vegetables, fruits, crates, stalls, food and decorations. LOD0-2, colliders, 6 ready compositions and a demo scene. Mobile-friendly, URP ready.
```

---

## 3. Полное описание (Description, English)
```markdown
**Farm Market Starter** is a modular low-poly collection for farm, village and market scenes — vegetables, fruits, crates, stalls, bakery and dairy food, signs, lanterns and more. Everything is built to be arranged freely: drop in a stall, fill it with produce, and your market square comes alive.

Includes a demo scene and 6 ready-made, filled market compositions.

### Key Features
* 119 single prefabs + 6 ready compositions
* 117 unique meshes, all with LOD0–LOD2
* Colliders on every prefab
* Real-world scale (1 unit = 1 m), pivot at the base
* Mobile friendly: SRP Batcher and GPU Instancing compatible
* URP (Unity 6) ready
* Demo scene: a full market square built only from pack props
* Consistent naming: FMS_<Category>_<Name>_<Variant>

### What's Inside
* **Vegetables (17):** Tomato, Carrot, Potato, Cabbage, Corn, Pumpkin, Cucumber, Onion, Garlic, Peppers, Eggplant, Beet, Radish, Salad & Greens and more
* **Fruits (8):** Apple, Pear, Watermelon, Grape, Strawberry, Lemon, Orange and more
* **Crates, Baskets & Sacks (32):** produce crates, wicker baskets, mesh trays, grain sacks, seed packets, eggs, milk churns and more
* **Stalls & Furniture (14):** small, medium and corner stalls, canopy, merchant cart, display shelves, balance scale, cash box, market umbrellas (red, blue, green)
* **Decor & Signs (31):** chalkboards, signposts, bunting, lanterns, street lamps, picnic table & benches, planters & pots, barrels, hay bales and more
* **Food (17):** bread & bakery, cheese, milk bottles & buckets, honey & jam jars, meat & fish and more
* **6 ready compositions:** Vegetable Row, Fruit Row, Dairy & Food Corner, Merchant Cart (full), Market Square Plaza, Floral Planter Stand

### Technical Details
* Unique meshes: 117 (FBX, LOD0–LOD2)
* Prefabs: 125 (119 single + 6 compositions)
* Triangles: [ПРОВЕРИТЬ — min/max LOD0 и сумма по паку]
* Materials: 43 (URP/Lit)
* Textures: 41 base-colour textures (3 × 2048², 7 × 1024², 8 × 512², 23 × 256²)
* Colliders: yes
* LODs: yes (LOD1 ~56%, LOD2 ~16% of triangles)
* Animations: none
* Render pipeline: URP (Unity 6000.3+). Built-in/HDRP — via Unity's material upgrade tools

### Support
Contact us through the publisher profile on the Asset Store. Reviews are appreciated!
```

---

## 4. Русский вариант (ArtStation / DTF / Boosty)
```markdown
**Farm Market Starter** — модульный low-poly набор для ферм, деревень и рынков: овощи, фрукты, ящики, прилавки, еда, вывески, фонари и декор.

* 119 одиночных префабов + 6 готовых композиций
* 117 уникальных мешей с LOD0–LOD2, коллайдеры на каждом префабе
* Масштаб 1 unit = 1 м, pivot у основания
* SRP Batcher / GPU Instancing, URP (Unity 6)
* Демо-сцена: рыночная площадь целиком из предметов пака
```

---

## 5. Release Notes (v1.0.0)
```text
Version 1.0.0 — Initial release:
* 119 single prefabs in 6 categories (Vegetables, Fruits, Crates, Stalls, Decor, Food).
* 6 ready-made market compositions.
* LOD0–LOD2 and colliders on all props.
* Demo scene: Demo_MarketSquare.
* URP (Unity 6) ready, SRP Batcher compatible.
```

---

## 6. Картинки — что куда загружать

Правила из чеклиста: одна серия, одинаковая плашка внизу слева, единый размер скриншотов (16:9, минимум 1200 px по ширине), JPG 85% до 300–500 KB, один фон на серию, бейдж «3D» на Card/Cover, «UPDATE x.x» только после обновления.

Папка: `wreckfish/AssetStore/Full/Draft/`

| Поле портала | Размер по правилам | Файл | Заметка |
|---|---|---|---|
| Icon | 160×160 (Asset Store принимает 1024×1024) | `01_Icon_2048x2048.jpg` | уменьшить до 1024×1024; без текста |
| Card | 420×280 | `02_Card_1260x840.png` | уменьшить; плашка читается в 420 px? |
| Cover | 1950×1300 | `03_Cover_1950x1300.png` | |
| Screenshot 1 | 16:9 | `04_Hero_Showcase_1920x1080.png` | обзор |
| Screenshot 2 | | `05_Full_Collection_2730x1536.jpg` | вся коллекция |
| Screenshot 3 | | `06_Produce_Closeup_1920x1080.png` | овощи/фрукты |
| Screenshot 4 | | `07_Stalls_Furniture_2752x1536.jpg` | прилавки |
| Screenshot 5 | | `08_Crates_Food_2730x1536.jpg` | ящики и еда |
| Screenshot 6 | | `09_Ready_Presets_2730x1536.jpg` | композиции |
| Screenshot 7 | | `10_Demo_Scene_2730x1536.jpg` | демо-сцена |
| Screenshot 8 | | `11_Collection_Captioned_2730x1536.jpg` | дублирует `05` — оставить только один |

**Единый размер:** сейчас смешаны 1920×1080, 2730×1536, 2752×1536. Привести к одному (рекомендую 1920×1080) и сжать.

### Ещё не снято (из расширенного списка чеклиста)
- [ ] Wireframe-кадр (Scene View → Shaded Wireframe, tris по категориям)
- [ ] Палитра и материалы
- [ ] Скриншот Unity Editor: префаб, инспектор, структура папок
- [ ] Сравнение Lite vs Full
- [ ] Вторая сцена / другой ракурс демо (в чеклисте — «Demo_MarketStreet», «Demo_FarmStand»)
- [ ] YouTube-трейлер 30–60 с (turntable + пролёт камеры) — слот 1 в портале

---

## 7. Состав ассета — чеклист по Unity-части

- [x] Именование `FMS_<Категория>_<Название>_<Вариант>`
- [x] Масштаб 1 unit = 1 м, pivot у основания (по README)
- [x] LOD0–LOD2 и коллайдеры (по README; у части моделей `item_*_v2` LOD1/2 нет — см. память проекта) **[ПРОВЕРИТЬ]**
- [ ] Вес пака < 30 MB: сейчас Art 19.9 MB + Demo 27.6 MB = ~48 MB в папке (в пакет попадёт меньше без `.meta`/Library) **[ПРОВЕРИТЬ после экспорта]**
- [ ] Заявленные в чеклисте «3 материала, 1 палитра» не выполняются: 43 материала и 41 текстура. Либо принять (описание уже исправлено на реальные цифры), либо объединить в атласы
- [ ] Цветовые варианты отдельными префабами: есть только зонты (Blue/Green); навес только красный
- [ ] Демо-сцены: сейчас 1 (`Demo_MarketSquare`)
- [ ] URP- и Built-in-пакеты отдельно: Built-in не делался
- [ ] Нет розовых материалов, Z-fighting, торчащих углов
- [ ] `Documentation/README.txt`, `Changelog.txt` обновить (в README «50 items», версия «work in progress»)
- [ ] Нет Library/Temp/.blend/пустых папок (`Demo/Scripts/.gitkeep` — убрать пустую папку или положить скрипт камеры)
- [ ] Demo зависит от Input System — указать в описании или убрать зависимость
- [ ] Asset Store Publishing Tools → Validator без ошибок
- [ ] Раскрытие использования ИИ — если применялся (картинки сгенерированы)

---

## 8. Итоговый контроль перед загрузкой

- [ ] Все изображения одного стиля, одинаковые плашки/шрифты
- [ ] Первый скриншот понятен без описания
- [ ] Видео загружено, заглавный кадр в стиле cover
- [ ] Название, теги, описание совпадают с реальным содержимым (числа префабов/tris)
- [ ] Lite и Full ссылаются друг на друга
- [ ] Версия, дата, changelog заполнены
- [ ] Проверено в чистом проекте Unity 6 на URP (и Built-in, если заявляется)
- [ ] Лицензия: стандартная Unity Asset Store EULA; сторонних ассетов в паке нет **[ПРОВЕРИТЬ]**

---

## 9. Что я не проверял

- Триангулы, наличие LOD у каждой модели, размер итогового .unitypackage — для этого нужна Unity.
- Содержимое самих картинок построчно сверено только по тем, что ты присылал в чате; файлы `02`, `03`, `04`, `06` я не открывал.
- Правила портала взяты из чеклиста в `Searcher`, а не с живой страницы Asset Store — размеры полей загрузки стоит сверить в Publisher Portal.
