# Unity Asset Store — Тексты и метаданные для публикации (LITE, бесплатный)
> **Пакет:** Farm Market Starter Lite  
> **Версия:** 1.0.0 · **Цена:** Free  
> **Формат:** поля ниже соответствуют форме Publisher Portal (`publisher.unity.com`). Редактор портала НЕ поддерживает Markdown (нет `#`, `**`), только жирный/курсив/ссылку/списки кнопками, поэтому тексты даны простыми, списки через `- `.  
> **Источники:** `Plan/FARM_MARKET_STARTER_PLAN.md`, `Assets/FarmMarketStarter/`, `Lite_Reference_Concepts/README_Lite_Composition_Guide.md`.

> ⚠️ Это НЕ описание платного пакета "Stylized Medieval Market & Farm" из `AssetStore_Text_Metadata.md`. Lite — подмножество Farm Market Starter, слова "medieval" в нём нет.

---

## 1. General Information

### Package Title
```text
Farm Market Starter Lite - Free Low Poly Veggies
```
*(Короткая альтернатива: `Farm Market Starter Lite`)*

### Category
```text
3D / Props / Exterior
```
*(Альтернатива: `3D / Environments / Historic`. Предметы в Lite не средневековые, поэтому Props предпочтительнее.)*

### Price
```text
Free
```

### Keywords / Tags
```text
low poly, farm, market, vegetables, fruits, food, stylized, props, stall, crates, mobile, urp, free, starter
```

### Хештеги для соцсетей
```text
#gamedev #unity3d #indiedev #freeassets #lowpoly #stylizedart #gameassets #madewithunity #3dassets #farming
```

---

## 2. Summary (лимит 10–200 символов, здесь 179)

```text
Free stylized low-poly farm market starter: 22 prefabs - vegetables, fruits, crates, baskets, a market stall, cart, scales and signs, plus a demo scene. Mobile-friendly, URP ready.
```

---

## 3. Description

```text
Start your farm, market or tycoon scene for free with Farm Market Starter Lite - a compact set of stylized low-poly props: ripe vegetables, fruits, crates, baskets, a market stall, a merchant cart, balance scales and signs.

Lite is a hand-picked subset of the full Farm Market Starter pack: same style, same palette, same scale. Try it in your project and upgrade when you need more.

Suitable for farming sims, tycoon and management games, top-down and isometric RPGs, mobile games, and quick prototypes of market scenes. All props are separate prefabs, so you can rearrange them or fill stalls, crates and baskets your own way.

What's inside:
- Market: stall with striped canopy, open stall table, merchant cart, balance scale with weights, chalk signboard, hanging signs
- Containers: 3 wooden crates, 2 wicker baskets
- Vegetables: tomato (whole, half, branch), carrot, potato, cabbage, pumpkin
- Fruits: apple, watermelon
- Ready-made vegetable stand prefab
- Demo scene: Demo_Lite_Showcase

Want more? The full Farm Market Starter pack includes 50 items, extra stalls and canopies, decorations, hay, barrels, ready food and more compositions.
```

---

## 4. Technical details (обязательное поле)

```text
- 22 prefabs: 21 single props + 1 pre-assembled vegetable stand
- Naming: FMS_<Category>_<Name>_<Variant>, e.g. FMS_Veg_Tomato_Whole
- Colliders on every prefab
- No LODs (included in the full pack)
- 8 PNG base color textures (1-2K), 8 URP/Lit materials
- Real-world scale: 1 unit = 1 meter, pivot at the base of each object
- Demo scene: Demo_Lite_Showcase
- Render pipeline: Universal Render Pipeline (URP). Developed and tested in Unity 6 (6000.3), URP 17.3
- Source files: FBX + prefabs, no .blend included
```

---

## 5. Release Notes (вкладка Releases)

```text
Version 1.0.0 - Initial Release:
- 22 prefabs: 21 single props + 1 ready-made vegetable stand
- Market stall (with/without canopy), merchant cart, scales with weights, chalk and hanging signs
- 3 wooden crates, 2 wicker baskets
- Vegetables: tomato (whole/half/branch), carrot, potato, cabbage, pumpkin. Fruits: apple, watermelon
- Colliders on every prefab
- Demo scene: Demo_Lite_Showcase
- Universal Render Pipeline (URP), Unity 6
```

---

## 6. Медиа (папка `AssetStore/Lite/Hero/`)

### Screenshots & videos (мин. ширина 1200 px)
| № | Файл | Размер |
|---|---|---|
| 1 | `03_Lite_Detail_Closeup_1920x1080.png` | 1920 × 1080 |
| 2 | `04_Lite_Stall_Layout_Staging_1920x1080.png` | 1920 × 1080 |

### Marketing images (портал требует icon + card + cover)
| Поле | Файл | Размер |
|---|---|---|
| **Card** | `02_Lite_Store_Card_420x280.png` (запас: `02_Lite_Store_Card_1260x840.png`) | 420 × 280 |
| **Cover** | `01_Lite_Hero_Cover_1950x1300.png` | 1950 × 1300 |
| **Icon** | ❌ готового файла нет — нужно сделать | 160 × 160 (по плану: один яркий предмет, помидор или ящик с овощами, на чистом фоне) |

Опционально: Social media image 1200 × 630 (нет), Media link на YouTube/Vimeo (нет), больше скриншотов (план рекомендует 6–10).

---

## 7. Что проверить перед отправкой

1. **Блокер:** нет иконки 160×160, портал не даст отправить пакет без неё.
2. **План vs. проект.** План (раздел 4): Lite без композиций, с одним материалом. В проекте: 8 материалов, 8 текстур (после чистки) и композиция `FMS_Comp_VegetableStand`. Текст написан по проекту. LOD нет (совпадает с планом).
3. **Число предметов.** План: «13 предметов + 1 композиция = 14 позиций». В проекте 22 префаба, потому что варианты (3 ящика, 2 корзины, 3 помидора) считаются отдельно. В тексте «22 prefabs».
4. **Треугольники** по FBX не считались, цифр в описании нет. Проверьте в Unity (Stats) и при желании добавьте строку в Technical details.
5. **Совместимость Unity.** План заявляет 2021.3 LTS+, проверен только Unity 6 (6000.3.10f1, URP 17.3). Расширяйте текст только после реального теста.
6. **Не выполнено:** прогон в чистом проекте и Asset Store Publishing Tools (Validator).
7. **Документация.** Для Lite по плану нужна 1 страница README и ссылка на Full; `Documentation/` в `Assets/FarmMarketStarter/` нет.
8. **ИИ.** Если модели или картинки сгенерированы ИИ, заполните раскрытие использования ИИ в Publisher Portal.

---

## 9. Submit package for approval (окно «Submit package for approval»)

### Поле «What additional information would you like our Curation team to know…»
Поле необязательное. Текст ниже вставляйте только после того, как проверите каждый пункт, особенно блок про ИИ: я не знаю, как именно создавались модели и картинки.

```text
Farm Market Starter Lite is the free version of our Farm Market Starter pack: 22 low-poly prefabs (market stall, cart, scale, signs, crates, baskets, vegetables, fruits) and one ready-made vegetable stand.

- Render pipeline: URP only (tested in Unity 6000.3.10f1, URP 17.3). The demo skybox uses a custom URP-compatible shader included in the package.
- Demo scene: Demo/Scenes/Demo_Lite_Showcase.unity. Its camera script uses the Input System package; the props, materials and prefabs work without it.
- Documentation: Documentation/README.txt and Changelog.txt.
- Third-party assets: [none / list them here].
- AI disclosure: [fill in: which parts, if any, were created or assisted with AI tools - 3D models, textures, store images].
- The demo ground and grass use textures and meshes created for this package.
```
Скобки `[...]` заполните сами, прежде чем отправлять.

### Чекбоксы в окне
- **Auto publish** — сейчас стоит галочка: пакет опубликуется сам сразу после одобрения. Если хотите сначала проверить страницу, снимите галочку и публикуйте вручную. Решение за вами.
- **«I swear, under penalty of perjury…»** — подтверждение, что права на все ассеты у вас есть. Это юридическое заявление, отметить его можете только вы после проверки: чужих ассетов нет, всё, что сгенерировано ИИ, соответствует правилам Unity. Я его за вас не ставлю.
- **I accept** — кнопка станет активной после этой галочки.

### Перед нажатием «I accept»
1. Валидатор (Asset Store Tools → Validator) без ошибок.
2. Иконка 160×160, card и cover загружены, скриншоты на месте.
3. Блок про ИИ и Third-Party заполнен фактами.
4. `Third-Party-Notices.txt` добавлен, если есть сторонние ресурсы.
