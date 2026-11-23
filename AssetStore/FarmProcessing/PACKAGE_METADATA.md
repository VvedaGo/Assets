# Farm Processing — карточка для Asset Store (Publisher Portal)

Обновлено: 2026-11-23 по фактическому содержимому `Assets/FarmProcessing` (ветка Farm-Processing). Блоки в рамках «КОПИРОВАТЬ» вставляются в портал как есть. Всё, что ещё не готово или не проверено, собрано в разделе «НЕ ГОТОВО» в конце. Поля с пометкой ⚠ перед вставкой сверить с живой формой портала.

---

## 1. Package name — КОПИРОВАТЬ

```
Farm Processing - Low Poly Workshops & Production Props
```

## 2. Category — ⚠ проверить в портале

`3D > Props > Interior` (предложение; если такой категории нет в портале, выбрать ближайшую из реального списка).

## 3. Keywords / Tags — КОПИРОВАТЬ

```
low poly, farm, workshop, processing, production, crafting, cozy, cheese, juice, bakery, food, props, stylized, URP
```

(14 штук. `drying` убран ради лимита; лимит портала ⚠ проверить.)

## 4. Short description / Summary — КОПИРОВАТЬ

```
Low poly farm workshop kit: 12 production stations, 18 tools, 18 food products, 12 furniture and 12 modular pieces, plus 8 ready workshop compositions. Unity 6 URP.
```

Длина: 164 символа (лимит краткого описания ⚠ сверить).

## 5. Description — КОПИРОВАТЬ

```
Build cozy farm workshops with a complete low poly kit for food processing. Make cheese and butter, press juice, mill grain, cook jam, dry fruit, bake bread, press seed oil, smoke fish and extract honey.

WHAT'S INCLUDED
• 72 unique props, each as a ready prefab (one extra plain-floor variant: 73 single-item prefabs)
• 12 production stations: cheese vat, cheese press, butter churn, fruit crusher, juice press, hand mill, jam kettle, drying rack, bread oven, oil press, smoker, honey extractor
• 18 tools, 18 processed products, 12 furniture pieces
• 12 modular workshop pieces (2 m grid): floors, walls, window, door, posts, beams, roof panel, shelf
• 8 ready workshop compositions: dairy, juice, grain, jam and drying, bakery, seed oil, smokehouse, honey
• 4 demo scenes: catalog, workshop courtyard, compositions and a media scene

TECHNICAL
• 81 prefabs in total (73 single items + 8 compositions)
• 28 to 3,384 triangles per item; stations have a LOD1 at 50% (LOD Group)
• Moving parts (lids, screws, handles, doors) are separate objects, so you can animate them yourself
• One 256x256 Base Color texture and one material per item (73 materials)
• Simple Box Colliders on single items
• Scale 1 unit = 1 meter, Y up
• Made for Unity 6000.3 and URP 17.3

NOT INCLUDED
This is an art pack. It has no production logic, inventory, recipes, economy, saving, characters, animation clips or fluid simulation. Separated parts are not ready-made animations.

Works on its own. No other package is required.
```

⚠ Лимит длинного описания портала сверить (в тексте ~1500 символов). Пункты про «separate objects» и «Box Colliders» взяты из ImportReport и prefab-файлов; визуально детали подвижных частей я не открывал.

## 6. Key features (если портал просит список) — КОПИРОВАТЬ

```
- 72 unique low poly farm processing props, ready as prefabs
- 12 hero production stations with LOD1 and separated moving parts
- 8 ready workshop compositions and 4 demo scenes
- Modular 2 m workshop kit for building your own interiors
- Lightweight: 256x256 textures, 63,924 triangles for the whole set
- Unity 6 / URP 17.3, no extra dependencies
```

## 7. Technical details — КОПИРОВАТЬ / ВВЕСТИ В ПОЛЯ

| Поле | Значение | Откуда |
|---|---|---|
| Number of unique meshes | 73 FBX (1 файл на предмет, плюс вариант `MOD_02_Plain`) | `Art/Models`, 73 `.fbx` |
| FBX source files | 73 | то же |
| Prefabs | 81 (73 одиночных + 8 композиций CMP-01…08) | `Art/Prefabs` |
| Scenes | 4 (`Demo_Catalog`, `Demo_WorkshopCourtyard`, `Demo_Compositions`, `Demo_Media`) | `Demo/Scenes` |
| Triangles, per item | min 28 (MOD_06) · max 3,384 (STA_10) | ImportReport.txt |
| Triangles, all 73 items | 63,924 | ImportReport.txt |
| LOD | 12 станций STA_01–12: LOD0 + LOD1 (50 %), LOD Group | prefabs, ImportReport |
| Materials | 73 (по одному на предмет) | `Art/Materials` |
| Textures | 73 × Base Color PNG, все 256×256 | `Art/Textures` |
| UV | UV0, без UV2 | план |
| Colliders | BoxCollider на всех 73 одиночных префабах, MeshCollider нет | prefabs |
| Rigging / Animation | нет / 0 | — |
| Scale / axes | 1 unit = 1 m, Y up | план, ImportReport |
| Render pipeline | URP 17.3.0 | `Packages/manifest.json` |
| Unity version | 6000.3.10f1 | `ProjectVersion.txt` |
| Размер `Assets/FarmProcessing` | 6.6 МБ (Art 5.7 МБ, Demo 0.9 МБ) | диск |
| Размер .unitypackage | ⚠ не собран, цифры нет | — |

## 8. Price — ⚠ решение владельца

Предложение: **USD 19.99**. Стартовую скидку (USD 14.99) ставить только если портал это позволяет. Цена нигде не публиковалась.

## 9. Version and release notes — КОПИРОВАТЬ

Version: `1.0.0`

```
Version 1.0.0 - first release.
- 72 low poly farm processing props as prefabs (12 stations, 18 tools, 18 products, 12 furniture, 12 modular pieces) plus one plain-floor variant
- 8 ready workshop compositions
- 4 demo scenes
- LOD1 for all 12 stations
- Unity 6000.3.10f1, URP 17.3.0
```

## 10. Compatibility — КОПИРОВАТЬ

```
Unity 6000.3 (tested with 6000.3.10f1). Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported.
```

Проект открыт в Unity 6000.3.10f1, в Editor.log нет ошибок компиляции. **Чистый импорт пакета в пустой проект ещё не делали** — до этого формулировку «tested with» держать условной.

## 11. Support / Publisher info — ⚠ подтвердить

Support email: `sergvved@gmail.com` (контакт серии; подтвердить, что он должен быть публичным).
Support URL, сайт, соцсети: ⚠ нет в репозитории, указать свои или оставить пустыми.

## 12. Created with AI — КОПИРОВАТЬ (⚠ подтвердить фактом)

```
Reference images and concept art for the 72 props and promo scenes were created with an AI image generator. The 3D models were built procedurally in Blender with Python scripts from those references and checked by hand; no AI 3D generator was used. Store images were rendered from the included Unity demo scenes.
```

Основание: `Tools/README.md` («No AI 3D generators were available; models are procedural»), журналы референсов в `planning/FarmProcessing/references`. Подтвердить, что финальные картинки в `Media/Final` целиком отрендерены из Unity (коммит `ecb20fe` это подтверждает частично) и что формулировка устраивает вас.

## 13. Media — готовые файлы

Папка `AssetStore/FarmProcessing/Media/Final/` (файлы есть, размеры проверены):

| Поле портала | Файл | Размер |
|---|---|---|
| Icon | `01_Icon_160x160.png` | 160×160 |
| Card | `02_Card_420x280.png` | 420×280 |
| Cover | `03_Cover_1950x1300.png` | 1950×1300 |
| Social | `04_Social_1200x630.png` | 1200×630 |
| Галерея 1 | `05_Hero.png` | 1920×1080 |
| 2 | `06_FullCollection.png` | 2400×1440 ⚠ |
| 3 | `15_StationsCatalog.png` | 1920×1080 |
| 4 | `07_Closeups.png` | 1920×540 ⚠ |
| 5 | `08_ModularKit.png` | 1920×720 ⚠ |
| 6 | `16_ModulesCatalog.png` | 1920×1080 |
| 7 | `11_ToolsAndProducts.png` | 1920×790 ⚠ |
| 8 | `12_Compositions.png` | 1920×1080 |
| 9 | `10_AlternateView.png` | 1920×1080 |
| 10 | `09_StationLODs.png` | 1920×1080 |
| 11 | `13_Materials.png` | 1920×1080 |

⚠ Размеры 06, 07, 08, 11 не 1920×1080 — портал может требовать 16:9. Порядок галереи — по плану `MEDIA_PLAN.md`. Видео (30–60 с) нет.

---

# НЕ ГОТОВО (что осталось сделать до публикации)

1. **Собрать `.unitypackage`** (Assets > Export Package из `Assets/FarmProcessing`, без лишнего) и записать его размер в п. 7.
2. **Чистый импорт**: импортировать пакет в пустой Unity 6000.3.10f1 + URP 17.3, проверить: нет ошибок/предупреждений, материалы не розовые, префабы и 4 сцены открываются.
3. **Asset Store Validator / Publisher Portal Validator**: запустить, исправить замечания, приложить результат.
4. **Документация для покупателя**: в `Assets/FarmProcessing/Documentation` есть только `ImportReport.txt`. Нужен README (состав, версии, поддержка, как открыть демо, ограничения) — могу написать.
5. **Лицензия/авторские права**: проверить, что нет сторонних материалов; текст лицензии/EULA в пакет не добавлен (портал использует стандартную).
6. **Медиа**: проверить размеры 06/07/08/11 по требованиям портала; нет кадра `14_UnityAndComparison` (Unity Setup) и технических кадров с wireframe/коллайдерами (`09` сейчас — «Station LODs»); нет видео.
7. **Сцены**: в проекте 4 сцены вместо 2 по плану; решить, класть ли `Demo_Media` в поставку (она нужна для съёмки, покупателю, скорее всего, нет). `ProjectSettings/EditorBuildSettings.asset` изменён локально — решить, нужны ли изменения.
8. **Лишние данные в пакете**: убедиться, что в экспорт не попадут `Assets/Editor/PackTools`, `Assets/Resources`, `.work`, `art`, `Tools`.
9. **Визуальная приёмка**: я не открывал модели и сцены глазами. Нужен общий проход: подвижные части, LOD, коллайдеры, стыки модулей.
10. **Git**: `Media/Final/` и `FINAL_CONTACT_SHEET.jpg` не закоммичены.
11. **Решения владельца**: цена (п. 8), категория (п. 2), публичный email (п. 11), формулировка AI (п. 12).
12. **Устаревшие документы**: `FARM_PROCESSING_PACK.md`, `PLAN.md`, `MEDIA_PLAN.md` описывают «модели ещё не созданы»; привести к фактам или пометить архивными.
