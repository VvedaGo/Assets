# Farm Machinery Lite — Asset Store card

Product: Farm Machinery Lite · Version: 1.0.0 · Updated: 2026-11-25 · Status: draft (Э13; numbers to be re-checked in Э14)
Fields and rules: REQUIREMENTS.md 7.1–7.3. Final texts go into the labelled blocks only; notes, options, TODO and
`[ПРОВЕРИТЬ]` go into the Notes block at the end. Full version card: [../Full/PACKAGE_METADATA.md](../Full/PACKAGE_METADATA.md).

Sources of numbers: `.work/ImportCheck_FarmMachinery.md` (FarmMachineryChecks, 2026-11-24 19:28, Unity 6000.3.10f1, URP),
`.work/ImportReport_FarmMachinery.txt`, `.work/ImportReport_FarmMachinery_Demo.txt`, `.work/ImportNotes_FarmMachinery.md`,
`AssetStore/FarmMachinery/Media/raw/Catalog/09_Technical_numbers.md`. Lite content = the "Lite = да" rows of
`planning/FarmMachinery/CATALOG.md`.

## Package Title

```text
Farm Machinery Lite - Low Poly Tractors & Implements
```

## Category

```text
3D / Vehicles / Land
```

## Keywords / Tags

```text
low poly, farm, tractor, trailer, plough, seeder, sprayer, agriculture, machinery, vehicles, stylized, farming, LOD, URP
```

## Summary
<!-- characters incl. spaces: 180 -->

```text
Stylized low poly farm machinery: 13 models - 2 tractors, 6 implements, 3 trailers, quick hitch, front weight. Separate wheels, matching hitch points, LOD1, colliders. Unity 6 URP.
```

## Description

```text
Start your farm game's machine fleet with Farm Machinery Lite: two stylized low poly tractors, six implements and three trailers, built to be hitched together and driven by your own code.

Lite is a selection from the full Farm Machinery pack, in the same style, palette and scale as our Farm Market, Farm Yard and Farm Nature packs. Use it for farming sims, tycoon and idle games, top-down and isometric farms, and quick prototypes of field work.

KEY FEATURES
- Gameplay-ready hierarchy: every wheel is a separate object with its pivot at the wheel centre (rotation axis X), ready for your own WheelCollider setup
- Named attach points as empty objects: Hitch, Link3P (3-point linkage) and PTO on tractors, implements and trailers. Matching pairs share position and rotation (Hitch_Rear to Hitch_Front, Link3P_Rear to Link3P_Front, PTO_Rear to PTO_Front), with the same standard heights on every model
- Moving parts are separate objects pivoted on their hinge axes: tractor lower links and cab door, tipper bed and tailgate, sprayer booms, seeder lid and markers, mower bar, harrow wings, tank hatch
- 3 colour atlases (Red, Green, Blue): tractors come as Red, Green and Blue prefabs; implements and trailers are Red, recolour them by swapping the material
- Transport and work poses for the sprayer, mower and disc harrow; empty and grain-loaded tipper
- LOD1 (about 50% triangles) on 11 of 13 models, Box Collider on every prefab
- 3 ready compositions and 2 demo scenes

WHAT'S INCLUDED
- Tractors (2): medium cab tractor, large 4-wheel tractor with front linkage - each in Red, Green and Blue
- Implements (6): 4-furrow plough, 3 m seeder, trailed sprayer (transport / work), disc mower (transport / work), trailed disc harrow (transport / work), 3 m cultivator
- Trailers (3): 2-axle tipper (empty / grain), 2-axle flatbed, tank trailer
- Attachments (2): quick hitch frame, front weight
- 21 prefabs in total: 13 models + 8 variants (4 colour, 3 pose, 1 load)
- 3 compositions: Ploughing (tractor + plough), Grain Haul (tractor + 2 tippers), Machine Yard (the whole Lite fleet)
- Demo scenes: Demo_FieldWork (field work on a small farm island) and a catalogue scene with all 21 prefabs

LIMITATIONS
This is an art pack. It has no scripts, driving physics, WheelColliders, Rigidbodies, rigs or animation clips. Separate wheels and moving parts are prepared for your own scripts or animations; they are not animated. Cab glass is opaque, there is no cab interior. The ground, fields, road, grass and clouds in the demo scenes are demo-only assets.

UPGRADE TO FULL
Farm Machinery (Full) adds a combine harvester and a forage harvester with 3 swappable headers, a round baler, a hay rake, a grain cart, bale and header trailers, a grain auger, a grain bin and a windrow module: 26 models, 41 prefabs, 5 compositions and a harvest demo scene.

Works on its own. Requires only the Universal Render Pipeline.
```

## Technical Details

| Block | Value |
|---|---|
| Unique Assets / Prefabs | 13 unique models (13 FBX, one per model). 21 single-item prefabs = 13 base + 8 Prefab Variants: colour 4 (Tractor_Cab, Tractor_Large × Green / Blue), pose 3 (Sprayer, Mower, DiscHarrow `_Work`), load 1 (Trailer_Tipper `_Grain`). 3 composition prefabs (CMP_01 Ploughing, CMP_02 GrainHaul, CMP_03 MachineYard) built only from pack prefabs. 24 prefabs in total. A unique asset = one model/FBX; variants and compositions reuse its mesh |
| Polygon Count | Triangles, LOD0 per model incl. wheels and moving parts, measured in Unity on the imported meshes: min 312 (Front Weight), max 3,708 (Disc Harrow), average 2,221, total 28,872 for the 13 unique models (variants and compositions not counted again). By category: Tractors 2 — 3,348 / 3,652 (7,000); Implements 6 — 908…3,708 (12,940); Trailers 3 — 2,436…3,040 (8,216); Attachments 2 — 312 / 404 (716) |
| LODs | LOD Group with LOD0 + LOD1 on 11 of 13 models; LOD1 = about 50% of LOD0 per part (total 14,100 triangles, min 454, max 1,854). No LOD on Quick Hitch (404 tris) and Front Weight (312 tris). LOD1 meshes are children of their moving parts, so a rotated wheel or bed keeps both levels aligned |
| Textures | 3 PNG Base Color atlases, 256 × 256 (T_FarmMachinery_Red / Green / Blue_BaseColor): 4 × 4 grid of flat 64 px colour cells, no alpha. Import: Point filter, no mipmaps, uncompressed, sRGB. No Normal, Metallic, AO or other maps. Demo-only textures are listed under Demo / Scripts |
| Materials / Shaders | 3 materials (M_FarmMachinery_Red / Green / Blue), shader Universal Render Pipeline/Lit, one material per prefab. Demo-only materials are listed under Demo / Scripts |
| UVs | One UV channel (UV0): every face is mapped to the centre of one flat colour cell of the atlas (no unwrap, no texture detail). Colour variants differ only in the body-colour cells of the atlas. No lightmap UV2 |
| Rigging / Animations | Static meshes, no rig, no skinning, 0 animation clips. Wheels, links, doors, beds, booms and other moving parts are separate objects with pivots on their axes, not animations |
| Colliders | One BoxCollider on every single-item prefab (21/21), sized to the whole model including wheels; pose variants have their own recomputed box. No MeshColliders. Compositions use the colliders of their nested prefabs |
| Scale / Setup | 1 unit = 1 m, Y up, machines face +Z. Root pivot on the ground at the centre of the footprint, root scale 1, rotation 0. Wheels: `Wheel_FL/FR/RL/RR` (single axle `Wheel_L/R`, plough gauge `Wheel_Gauge`), pivot at the wheel centre, spin axis local X. Attach points are empty objects (+Z forward, +Y up): `Hitch_*`, `Link3P_*`, `PTO_*`, `Seat`. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Naming `FMS_Mach_<Name>` for base prefabs and `FMS_Mach_<Name>_<Variant>` for variants. Quick Hitch and Front Weight are modelled at their mounted height and float above Y = 0 when placed alone |
| Files / Sources | FBX models (13), PNG textures (3), URP materials (3), prefabs (24), demo scenes. Blender files and build scripts are not included |
| Demo / Scripts | Demo scenes: Demo_FieldWork (CMP_01–03 on a farm island with ploughed field, seedlings, road and grass) and a catalogue scene with all 21 prefabs in rows. No scripts in the package; no camera controller (use the Scene view). Demo scenes use a URP Volume for post-processing. Demo-only assets in `Demo/`: environment models and prefabs (island base, field modules, road, grass tufts, clouds), their own atlas material, a sky panorama and two simple sky / cloud shaders; they are not counted above |
| Compatibility / Dependencies | Unity 6000.3 (built with 6000.3.10f1), Universal Render Pipeline 17.3. Built-in Render Pipeline and HDRP are not supported. No other packages required; no Input System dependency |
| Package Size | Measured on the exported 1.0.0 .unitypackage (Э14) |

## Price

```text
Free
```

(Owner decision 2026-11-25.)

## Version / Release Notes

Version: `1.0.0`

```text
1.0.0 - First release.
- 13 low poly farm machines: 2 tractors, 6 implements, 3 trailers, quick hitch and front weight
- 21 prefabs (13 models + 8 colour, pose and load variants) and 3 compositions
- Separate wheels and moving parts with pivots, named Hitch / Link3P / PTO attach points
- LOD1 on 11 models, Box Collider on every prefab
- Demo scenes: Demo_FieldWork and a catalogue scene
- Unity 6000.3, URP 17.3
```

## Compatibility

```text
Unity 6000.3 (built with 6000.3.10f1). Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported. The package contains no code, so there are no platform-specific requirements; performance on specific mobile devices has not been measured.
```

## Dependencies

```text
Required: Universal Render Pipeline (com.unity.render-pipelines.universal) 17.3.
No other Asset Store products are needed. The demo scenes use only assets included in this package.
```

## Support

```text
Support: contact via the publisher profile
Documentation: Assets/FarmMachinery/Documentation/README
Full version: Farm Machinery - [Asset Store link]
Same series: Farm Market Starter (https://assetstore.unity.com/packages/package/421724), Farm Yard (https://assetstore.unity.com/packages/package/424220), Farm Nature, Farm Processing
```

## AI / Third-party

```text
AI use: reference images for each model and the scene layouts were generated with an AI image generator (Codex ImageGen, Sol 6.2). The 3D models were built procedurally in Blender with Python scripts from those references and reviewed by hand; no AI 3D generator was used. Textures are flat-colour atlases made by script. The store icon artwork is AI-generated (Codex ImageGen) from our real Unity render of the cab tractor. The other store images are renders of the included prefabs and demo scenes in Unity; their text plates were designed with AI assistance and composited over the unaltered renders.
Third-party content: none. No third-party models, textures, code, fonts or audio are included in the package.
```

Fonts on store images (not in the package): see `AssetStore/FarmMachinery/Media/layout/FONTS.md` — **open**, being finalised by
Codex (Э12).

## Media

Lite set = 10 images (REQUIREMENTS 7.4: 4 main + 6 screenshots). Raw sources: `AssetStore/FarmMachinery/Media/raw/` and
`raw/Catalog/` (all accepted in `planning/FarmMachinery/reviews/renders_2.md`, slot mapping "Lite — 10 слотов"). Final files: Э12.
Plate system (7.6): Card/Cover — badge top left, dark plate `#20242A` with cream title `#F2E6C9`, red accent strip `#C8473B`;
no separate logo (owner decision 2026-11-25); gallery — compact dark plate bottom left, line 1 = pack name, line 2 = frame theme.
Typography: `·` = middle dot U+00B7, `×` = U+00D7, `→` = U+2192, `—` = em dash; letters exactly as written (case included).

| File | Size | Purpose | Plate text (exact) | Source render | Status |
|---|---|---|---|---|---|
| 01_Icon | 160×160 (+1024 master, check at 60) | Store icon: AI-generated artwork of the TRC-01 Red cab tractor, made from our real render, on flat teal `#173C45` | Corner badges: `3D` + `LITE` · no other text | Icon_Lite.png (base for the generated artwork) | raw ✅; trial `final/_draft/01_Icon_Lite_*_preview_only`; final generated icon with corner badges — Э12 |
| 02_Card | 420×280 (+1260×840) | Search card: TRC-01 + plough | Badge: `LITE` · Title: `FARM MACHINERY` · Accent: `13 MODELS + 3 COMPOSITIONS` | Card_Lite.png | raw ✅; trial in `_draft` used another accent; final — Э12 |
| 03_Cover | 1950×1300 | Page cover: Lite fleet on the field | Badge: `LITE` · Title: `FARM MACHINERY` · Accent: `13 MODELS · SEPARATE WHEELS · HITCH POINTS` | Cover_Lite.png | raw ✅; trial in `_draft` used another accent; final — Э12 |
| 04_Social | 1200×630 | Link preview, clean render | — (no text) | Social_Lite.png | raw ✅; final — Э12 |
| 05_Hero | 1920×1080 | Ready scene: field work | `FARM MACHINERY LITE` / `FIELD WORK` | Hero_Lite.png | raw ✅; trial in `_draft` had line 1 `FARM MACHINERY`; final — Э12 |
| 06_FullCollection | 1920×1080 | All Lite models and variants | `FARM MACHINERY LITE` / `LITE COLLECTION · 13 MODELS · 21 PREFABS` | Catalog/06_FullCollection_Lite.png | raw ✅; final — Э12 |
| 07_Closeups | 1920×1080 | 5 detail panels | `FARM MACHINERY LITE` / `DETAILS` | Demo_FieldWork_CloseCMP01, Demo_FieldWork_LowNode_Plough, Closeup_Lite_RearLinkage, Closeup_Lite_Sprayer, Closeup_Lite_Tipper | raw ✅; final — Э12 |
| 08_VariantsAndModules | 1920×1080 | Colours, poses, assembly, attach points (4 panels) | `FARM MACHINERY LITE` / `VARIANTS & ATTACH POINTS` | Catalog/08_ColourVariants_Lite, 08_Poses_Lite, 08_Modularity_Lite, 08_AttachPoints_Lite | raw ✅ (sheets sparse — crop by rows); final — Э12 |
| 09_Technical | 1920×1080 | Wireframe LOD0 / LOD1, colliders, real tris | `FARM MACHINERY LITE` / `LOD & COLLIDERS` | Catalog/09_Technical_Lite.png + 09_Technical_numbers.md (spare: Catalog/14_Unity_Lite.png) | raw ✅; final — Э12 |
| 10_DemoAndVersion | 1920×1080 | Demo view + what is in Lite / Full only | `FARM MACHINERY LITE` / `DEMO & WHAT'S IN LITE` | Demo_FieldWork_Overview.png (alt. Demo_FieldWork_Beauty.png) + text block | raw ✅; block — Э12 |

### Captions inside images (exact)

**06_FullCollection** — legend strip under the sheet (two lines):
- `TRACTORS 2 · IMPLEMENTS 6 · TRAILERS 3 · ATTACHMENTS 2`
- `VARIANTS: 4 COLOUR · 3 POSE · 1 LOAD`

**07_Closeups** — one caption per panel:
- Demo_FieldWork_CloseCMP01: `PLOUGH ON THE 3-POINT LINKAGE`
- Demo_FieldWork_LowNode_Plough: `4-FURROW PLOUGH`
- Closeup_Lite_RearLinkage: `HITCH · LINKAGE · PTO`
- Closeup_Lite_Sprayer: `FOLDING SPRAYER BOOMS`
- Closeup_Lite_Tipper: `TIPPER WITH GRAIN LOAD`

**08_VariantsAndModules** — one caption per panel:
- 08_ColourVariants_Lite: `3 COLOURS · MATERIAL SWAP`
- 08_Poses_Lite: `TRANSPORT / WORK · EMPTY / GRAIN`
- 08_Modularity_Lite: `PARTS → ASSEMBLED`
- 08_AttachPoints_Lite: `HITCH · LINK3P · PTO POINTS`
- footnote (small, under the attach-points panel): `Points are empty GameObjects; gizmos drawn for this image`

**09_Technical** — column heads `LOD0` · `LOD1` · `BOX COLLIDER`; row labels:
- row TRC-01: `CAB TRACTOR · LOD0 3,348 TRIS · LOD1 1,674 TRIS`
- row IMP-01: `PLOUGH · LOD0 1,260 TRIS · LOD1 630 TRIS`
- summary line: `LITE: 28,872 TRIS LOD0 (13 MODELS) · LOD1 ON 11 MODELS · BOX COLLIDER ON EVERY PREFAB`

**10_DemoAndVersion** — text block (right side, over calm sky/ground; Full content only as text, no Full images):
- heading: `IN LITE`
- `2 TRACTORS · 3 COLOURS`
- `6 IMPLEMENTS · 3 WORK POSES`
- `3 TRAILERS · GRAIN LOAD`
- `QUICK HITCH · FRONT WEIGHT`
- `3 COMPOSITIONS · 2 DEMO SCENES`
- heading: `FULL ONLY — NOT INCLUDED IN LITE`
- `COMBINE · FORAGE HARVESTER · 3 HEADERS · ROUND BALER · HAY RAKE · GRAIN CART · BALE & HEADER TRAILERS · GRAIN AUGER · GRAIN BIN · WINDROW`
- `FARM MACHINERY: 26 MODELS · 41 PREFABS · 5 COMPOSITIONS`
- footnote (small): `Ground, fields, grass and clouds: demo-only environment`

## Submission Notes

```text
Art-only package: no scripts. Demo scenes use a URP Volume and two simple unlit sky / cloud shaders included in Demo/Shaders. Assets in Demo/Environment (island base, field modules, road, grass, clouds) exist only for the demo scenes and are not counted as product models. Quick Hitch and Front Weight are modelled at their mounted height, so they sit above Y = 0 when placed alone. Lite is a subset of Farm Machinery (Full) with the same file names.
```

## Notes (not for the portal)

**Решения владельца 2026-11-25:** цена Lite — **Free**; Support — без e-mail/URL, контакт в профиле издателя; категория
`3D / Vehicles / Land` подтверждена; отдельного логотипа нет — store icon = сгенерированная картинка по нашему рендеру с угловыми
бейджами `3D` + `LITE` (раскрыто в AI / Third-party).

Справка по цене (было предложение до решения): Lite Free как Farm Market Starter Lite (PRD-03). Цены Э3 (02_DEMAND.md, 2026-11-24): Poly Pro Vehicles Farm $15.99, Stylized Tractor Pack
$15.99, PolyOne Farm Vehicles $15.00, Gridness Farm Pack – Vehicles $15.00, Yorakeys Stylized Farm Vehicles $19.98, Stylized
Farm Props and Vehicles $20.00, Low poly farm asset pack $29.99; общие паки фермы Synty $49.99, ithappy $79.00; наш Farm Yard $7.99.
В Title/Tags слово «free» не добавлял (поле Price уже Free); при желании тег `free` можно поставить вместо `farming`.

**[ПРОВЕРИТЬ после экспорта] (Э14):**
1. Package Size — нет экспорта; вписать размер `.unitypackage` 1.0.0 (не размер папки: `Assets/FarmMachinery` сейчас 79 МБ вместе
   со всеми медиа-сценами и V1/V2-версиями демо-материалов).
2. Состав экспорта Lite: 13 FBX, 21 + 3 префаба, 3 материала, 3 атласа, Demo_FieldWork, каталожная сцена, подмножество демо-окружения.
   Как собирается Lite (отдельный экспорт из той же `Assets/FarmMachinery` или копия) — решить; одинаковые имена/GUID с Full,
   чтобы апгрейд Lite → Full не дублировал файлы (это обещано в Submission Notes).
3. Демо-сцены: в проекте нет `Demo_Catalog_Lite` из CATALOG — есть `Catalog_06_Lite.unity` (тот же ряд 21 префаба). Решить имя;
   в тексте написано «a catalogue scene» без имени. Медиа-сцены (Icon/Card/Cover/Hero/Catalog_*) и лишние материалы
   `M_Demo_Backdrop_*`, `*_Soft`, `*_V2`, 3 панорамы неба — исключить или оставить; после этого вписать число демо-текстур и
   материалов в Technical Details (7.2 требует считать демо отдельно).
4. Какие DEM-модели реально нужны Demo_FieldWork (DEM-01…06, 09?) — от этого список демо-окружения в Demo / Scripts.
5. Чистый импорт в Unity 6000.3.10f1 + URP 17.3: компиляция, missing scripts, розовые материалы (включая облака/небо на
   собственных шейдерах), открытие сцен, Validator. До этого формулировка «built with» вместо «tested with».
6. Все числа (tris 28,872 / 14,100, min/max, 21 префаб, 11 LOD) — из ImportCheck 2026-11-24 19:28; сверить после экспорта и
   при расхождении поправить и подписи 06/09/10 (→ Э12).
7. Документации нет: `Assets/FarmMachinery/Documentation/` отсутствует (README + Changelog — Э14). Ссылка в Support указывает
   на будущий README.
8. Отсутствие зависимости от Input System: скриптов в паке нет, в демо-сценах только компоненты URP (Volume,
   UniversalAdditionalCameraData/LightData) — проверено по m_Script в Demo_FieldWork.unity; подтвердить в чистом проекте.

**Прочие открытые пункты:**
- Шрифты плашек: `Media/layout/FONTS.md` открыт (сейчас Arial Bold как черновик, лицензия не проверена; Codex выбирает OFL-семью).
  После выбора — проверить, что строки с `·`, `×`, `→`, `—` поддерживаются шрифтом. Шрифт в пакет не входит.
- Тексты пробной генерации отличаются от карточки: акцент Card/Cover Lite был `13 MODELS · LOW POLY · URP`, на Hero_Lite строка 1
  была `FARM MACHINERY`. Финальные — из этой карточки (одна мысль на Card — по 7.6; на галерее без бейджа LITE виден в имени).
- Ссылка на Full в Support появится после создания черновика Full (Э15); ID Farm Nature и Farm Processing в Asset Store не
  нашёл — добавить или убрать из строки.
- Лимиты Title (52 симв.), Summary (180, рабочий диапазон 10–200), числа тегов (14) — сверить с формой портала.
- Card/Cover в пробе Э12 имеют пустой квадрат под логотип — по решению владельца логотипа нет; место убрать или занять (Э12).
- Коллайдер: контракт CATALOG п. 9 просил коробку «без колёс», PackPrefabBuilder делает одну коробку на всю модель — в карточке
  написано по факту.
- Перерасход tris ATT-01 (404/400) покупателю не важен, в тексте не упоминается.
