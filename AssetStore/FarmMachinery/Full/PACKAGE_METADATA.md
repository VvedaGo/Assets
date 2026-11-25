# Farm Machinery — Asset Store card

Product: Farm Machinery (Full) · Version: 1.0.0 · Updated: 2026-11-25 · Status: draft — Э13 done, Э12 media accepted (media_1); numbers to be re-checked in Э14
Fields and rules: REQUIREMENTS.md 7.1–7.3. Final texts go into the labelled blocks only; notes, options, TODO and
`[ПРОВЕРИТЬ]` go into the Notes block at the end. Lite version card: [../Lite/PACKAGE_METADATA.md](../Lite/PACKAGE_METADATA.md).

Sources of numbers: `.work/ImportCheck_FarmMachinery.md` (FarmMachineryChecks, 2026-11-24 19:28, Unity 6000.3.10f1, URP),
`.work/ImportReport_FarmMachinery.txt`, `.work/ImportReport_FarmMachinery_Demo.txt`, `.work/ImportNotes_FarmMachinery.md`,
`AssetStore/FarmMachinery/Media/raw/Catalog/09_Technical_numbers.md`. Content = all rows of `planning/FarmMachinery/CATALOG.md`.

## Package Title

```text
Farm Machinery - Low Poly Tractors & Harvesters
```

## Category

```text
3D / Vehicles / Land
```

## Keywords / Tags

```text
low poly, farm, tractor, combine, harvester, trailer, plough, baler, agriculture, machinery, vehicles, stylized, LOD, URP
```

## Summary
<!-- characters incl. spaces: 186 -->

```text
Stylized low poly farm machinery: 26 models - tractors, implements, trailers, combine and forage harvesters with swappable headers, baler, grain yard. Separate wheels, hitch points. URP.
```

## Description

```text
Build a complete farm machine fleet - from ploughing to harvest - with Farm Machinery: 26 stylized low poly models of tractors, implements, trailers, harvesters and grain yard equipment, prepared to be hitched together and driven by your own code.

Same style, palette and scale as our Farm Market, Farm Yard and Farm Nature packs. Use it for farming sims, tycoon and idle games, top-down and isometric farms, harvest scenes and quick prototypes.

KEY FEATURES
- Gameplay-ready hierarchy: every wheel is a separate object with its pivot at the wheel centre (rotation axis X), ready for your own WheelCollider setup
- Named attach points as empty objects: Hitch, Link3P (3-point linkage), PTO and Feeder. Matching pairs share position and rotation (Hitch_Rear to Hitch_Front, Link3P_Rear to Link3P_Front, PTO_Rear to PTO_Front, Feeder_Front to Feeder_Rear), with the same standard heights on every model
- Swappable combine headers: grain, corn and pickup headers are separate prefabs that share one Feeder interface on the combine and the forage harvester
- Moving parts are separate objects pivoted on their hinge axes: doors, tractor links, tipper bed and tailgate, sprayer booms, mower bar, harrow wings, combine feeder and unloading auger, reel, forage spout, baler pickup and tailgate, rake arms and rotors, grain cart auger, bin door and hatch
- 3 colour atlases (Red, Green, Blue): tractors and harvesters come as Red, Green and Blue prefabs; implements and trailers are Red, recolour them by swapping the material
- Pose variants: transport / work (sprayer, mower, disc harrow, hay rake), closed / open baler; load variants: empty / grain tipper, empty / full grain cart
- LOD1 (about 50% triangles) on 22 of 26 models, Box Collider on every prefab
- 5 ready compositions and 3 demo scenes

WHAT'S INCLUDED
- Tractors (2): medium cab tractor, large 4-wheel tractor with front linkage - each in Red, Green and Blue
- Implements (7): 4-furrow plough, 3 m seeder, trailed sprayer, disc mower, trailed disc harrow, 3 m cultivator, twin-rotor hay rake
- Trailers (6): 2-axle tipper (empty / grain), flatbed, tank trailer, grain cart (empty / full), bale trailer, header trailer
- Harvesters (3): combine harvester and forage harvester (each in Red, Green and Blue), round baler (closed / open)
- Attachments and headers (5): quick hitch frame, front weight, 6 m grain header, 6-row corn header, pickup header
- Grain yard (2): grain auger, corrugated grain bin
- Field prop (1): 4 m windrow module that snaps end to end
- 41 prefabs in total: 26 models + 15 variants (8 colour, 5 pose, 2 load)
- 5 compositions: Ploughing, Grain Haul, Machine Yard, Harvest (combine, grain cart and tipper), Haymaking (mower, rake, baler and bale trailer)
- Demo scenes: Demo_FieldWork, Demo_Harvest and a catalogue scene with all 41 prefabs

LIMITATIONS
This is an art pack. It has no scripts, driving physics, WheelColliders, Rigidbodies, rigs or animation clips. Separate wheels and moving parts are prepared for your own scripts or animations; they are not animated. Cab glass is opaque, there is no cab interior. Drive shafts are not modelled. The ground, wheat field, bales, road, grass and clouds in the demo scenes are demo-only assets.

LITE VERSION
Farm Machinery Lite contains the 13 tractor, implement and trailer models of this pack (21 prefabs, 3 compositions). Farm Machinery adds the harvesters, headers, baler, hay rake, grain cart, bale and header trailers, grain yard and windrow, plus the Harvest demo.

Works on its own. Requires only the Universal Render Pipeline.
```

## Technical Details

| Block | Value |
|---|---|
| Unique Assets / Prefabs | 26 unique models (26 FBX, one per model). 41 single-item prefabs = 26 base + 15 Prefab Variants: colour 8 (Tractor_Cab, Tractor_Large, Combine, ForageHarvester × Green / Blue), pose 5 (Sprayer, Mower, DiscHarrow, HayRake `_Work`; Baler_Round `_Open`), load 2 (Trailer_Tipper `_Grain`, GrainCart `_Full`). 5 composition prefabs (CMP_01 Ploughing, CMP_02 GrainHaul, CMP_03 MachineYard, CMP_04 Harvest, CMP_05 Haymaking) built only from pack prefabs. 46 prefabs in total. A unique asset = one model/FBX; variants and compositions reuse its mesh |
| Polygon Count | Triangles, LOD0 per model incl. wheels and moving parts, measured in Unity on the imported meshes: min 76 (Windrow), max 3,708 (Disc Harrow), average 2,095, total 54,464 for the 26 unique models (variants and compositions not counted again). By category: Tractors 2 — 3,348 / 3,652 (7,000); Implements 7 — 908…3,708 (15,028); Trailers 6 — 1,836…3,172 (15,872); Attachments & headers 5 — 312…1,472 (4,136); Harvesters 3 — 2,820…3,036 (8,764); Grain yard 2 — 1,508 / 2,080 (3,588); Windrow 1 — 76 |
| LODs | LOD Group with LOD0 + LOD1 on 22 of 26 models; LOD1 = about 50% of LOD0 per part (total 25,580 triangles, min 270, max 1,854). No LOD on Quick Hitch (404 tris), Front Weight (312), Header Trailer (2,648) and Windrow (76). LOD1 meshes are children of their moving parts, so a rotated wheel, bed, auger or arm keeps both levels aligned |
| Textures | 3 PNG Base Color atlases, 256 × 256 (T_FarmMachinery_Red / Green / Blue_BaseColor): 4 × 4 grid of flat 64 px colour cells, no alpha. Import: Point filter, no mipmaps, uncompressed, sRGB. No Normal, Metallic, AO or other maps. Demo-only textures are listed under Demo / Scripts |
| Materials / Shaders | 3 materials (M_FarmMachinery_Red / Green / Blue), shader Universal Render Pipeline/Lit, one material per prefab. Demo-only materials are listed under Demo / Scripts |
| UVs | One UV channel (UV0): every face is mapped to the centre of one flat colour cell of the atlas (no unwrap, no texture detail). Colour variants differ only in the body-colour cells of the atlas. No lightmap UV2 |
| Rigging / Animations | Static meshes, no rig, no skinning, 0 animation clips. Wheels, links, doors, beds, booms, augers, reels, spouts and other moving parts are separate objects with pivots on their axes, not animations |
| Colliders | One BoxCollider on every single-item prefab (41/41), sized to the whole model including wheels; pose variants have their own recomputed box. No MeshColliders. Compositions use the colliders of their nested prefabs |
| Scale / Setup | 1 unit = 1 m, Y up, machines face +Z. Root pivot on the ground at the centre of the footprint, root scale 1, rotation 0. Wheels: `Wheel_FL/FR/RL/RR` (single axle `Wheel_L/R`, plough gauge `Wheel_Gauge`), pivot at the wheel centre, spin axis local X. Attach points are empty objects (+Z forward, +Y up): `Hitch_*`, `Link3P_*`, `PTO_*`, `Feeder_Front` / `Feeder_Rear`, plus `Seat`, `Auger_Out`, `Spout_Out`, `Bale_Out`, `Header_Rest`. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Naming `FMS_Mach_<Name>` for base prefabs and `FMS_Mach_<Name>_<Variant>` for variants. Combine and forage harvester prefabs come without a header; attach one by its Feeder points. Quick hitch, front weight and the 3 headers are modelled at their mounted height and float above Y = 0 when placed alone. The windrow module is exactly 4 m long and snaps end to end |
| Files / Sources | FBX models (26), PNG textures (3), URP materials (3), prefabs (46), demo scenes. Blender files and build scripts are not included |
| Demo / Scripts | Demo scenes: Demo_FieldWork (CMP_01–03 on a farm island), Demo_Harvest (CMP_04–05, forage harvester with tipper, combine with corn header, header trailer, grain bins and auger on a farm island with wheat and stubble) and a catalogue scene with all 41 prefabs in rows. No scripts in the package; no camera controller (use the Scene view). Demo scenes use a URP Volume for post-processing. Demo-only assets in `Demo/`: environment models and prefabs (island base, ploughed / stubble / seedling / wheat field modules, road, grass tufts, clouds, straw bales), their own atlas materials, a sky panorama and two simple sky / cloud shaders; they are not counted above |
| Compatibility / Dependencies | Unity 6000.3 (built with 6000.3.10f1), Universal Render Pipeline 17.3. Built-in Render Pipeline and HDRP are not supported. No other packages required; no Input System dependency |
| Package Size | Measured on the exported 1.0.0 .unitypackage (Э14) |

## Price

```text
USD 19.99
```

(Owner decision 2026-11-25; no launch discount.)

## Version / Release Notes

Version: `1.0.0`

```text
1.0.0 - First release.
- 26 low poly farm machines: 2 tractors, 7 implements, 6 trailers, 3 harvesters, 5 attachments and headers, 2 grain yard items, 1 windrow module
- 41 prefabs (26 models + 15 colour, pose and load variants) and 5 compositions
- Separate wheels and moving parts with pivots, named Hitch / Link3P / PTO / Feeder attach points, swappable combine headers
- LOD1 on 22 models, Box Collider on every prefab
- Demo scenes: Demo_FieldWork, Demo_Harvest and a catalogue scene
- Unity 6000.3, URP 17.3
```

## Compatibility

```text
Unity 6000.3 (built with 6000.3.10f1). Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported. The package contains no code, so there are no platform-specific requirements; performance on specific mobile devices has not been measured.
```

## Dependencies

```text
Required: Universal Render Pipeline (com.unity.render-pipelines.universal) 17.3.
No other Asset Store products are needed. The demo scenes use only assets included in this package (the demo bales are demo-only props, not Farm Market assets).
```

## Support

```text
Support: contact via the publisher profile
Documentation: Assets/FarmMachinery/Documentation/README
Lite version: Farm Machinery Lite - [Asset Store link]
Same series: Farm Market Starter (https://assetstore.unity.com/packages/package/421724), Farm Yard (https://assetstore.unity.com/packages/package/424220), Farm Nature, Farm Processing
```

## AI / Third-party

```text
AI use: reference images for each model and the scene layouts were generated with an AI image generator (Codex ImageGen, Sol 6.2). The 3D models were built procedurally in Blender with Python scripts from those references and reviewed by hand; no AI 3D generator was used. Textures are flat-colour atlases made by script. The store icon artwork is AI-generated (Codex ImageGen) from our real Unity render of the combine harvester. The other store images are renders of the included prefabs and demo scenes in Unity; their text plates were designed with AI assistance and composited over the unaltered renders.
Third-party content: none. No third-party models, textures, code, fonts or audio are included in the package.
```

Fonts on store images (not in the package): Montserrat 9.000, SIL Open Font License 1.1 — `AssetStore/FarmMachinery/Media/layout/FONTS.md`,
`Media/layout/fonts/OFL.txt`. The badge lettering on 01_Icon is drawn by ImageGen inside the raster (family unknown).

## Media

Full set = 14 images (REQUIREMENTS 7.4: 4 main + 10 screenshots). Raw sources: `AssetStore/FarmMachinery/Media/raw/` and
`raw/Catalog/` (all accepted in `planning/FarmMachinery/reviews/renders_2.md`, slot mapping "Full — 14 слотов"). Final files: `AssetStore/FarmMachinery/Full/Media/final/` (PNG RGB; icon also 1024 master and 60 px check, card also 1260×840), accepted in `planning/FarmMachinery/reviews/media_1.md` after fixes.
Plate system (7.6): Icon/Card/Cover — one badge system: red corner triangle top left with white `3D` (owner decision 2026-11-25; REQUIREMENTS 7.6 optional paid badge); Card/Cover — dark plate `#20242A` with cream title `#F2E6C9`, red accent strip `#C8473B`;
no separate logo (owner decision 2026-11-25); gallery — compact dark plate bottom left, line 1 = pack name, line 2 = frame theme.
Typography: `·` = middle dot U+00B7, `×` = U+00D7, `→` = U+2192, `—` = em dash; letters exactly as written (case included).

| File | Size | Purpose | Plate text (exact) | Source render | Status |
|---|---|---|---|---|---|
| 01_Icon | 160×160 (+1024 master, check at 60) · PNG RGB | Store icon: AI-generated artwork of the HRV-01 Red combine with grain header, made from our real render, on flat teal `#173C45` | Corner badge: `3D` (red triangle top left, white letters) · no other text | Icon_Full.png (base for the generated artwork) | accepted (media_1); AI-generated artwork from the real render, badge lettering drawn by ImageGen |
| 02_Card | 420×280 (+1260×840) · PNG RGB | Search card: combine + grain header | Corner badge: `3D` (red triangle top left) · Title: `FARM MACHINERY` · Accent: `26 MODELS + 5 COMPOSITIONS` | Card_Full.png | accepted (media_1, after fix: `3D` corner recorded) |
| 03_Cover | 1950×1300 · PNG RGB | Page cover: harvest fleet | Corner badge: `3D` (red triangle top left) · Title: `FARM MACHINERY` · Accent: `26 MODELS · SEPARATE WHEELS · HITCH POINTS` | Cover_Full.png | accepted (media_1, after fix: `3D` corner recorded) |
| 04_Social | 1200×630 · PNG RGB | Link preview, clean render | — (no text) | Social_Full.png | accepted (media_1) |
| 05_Hero | 1920×1080 · PNG RGB | Ready scene: harvest | `FARM MACHINERY` / `HARVEST` | Hero_Full.png | accepted (media_1) |
| 06_FullCollection | 1920×1080 · PNG RGB | All 26 models and 15 variants | `FARM MACHINERY` / `FULL COLLECTION · 26 MODELS · 41 PREFABS` | Catalog/06_FullCollection_Full.png (spare: 06a_Machines, 06b_Implements) | accepted (media_1) |
| 07_Closeups | 1920×1080 · PNG RGB | 5 detail panels | `FARM MACHINERY` / `DETAILS` | Demo_Harvest_LowNode_Header, Demo_Harvest_CloseHaymaking, Demo_Harvest_CloseGrainYard, Demo_FieldWork_LowNode_Plough, Demo_FieldWork_CloseCMP01 | accepted (media_1) |
| 08_VariantsAndModules | 1920×1080 · PNG RGB | Colours, poses, swappable headers, attach points (4 panels) | `FARM MACHINERY` / `VARIANTS & MODULARITY` | Catalog/08_ColourVariants, 08_Poses, 08_Modularity, 08_AttachPoints | accepted (media_1) |
| 09_Technical | 1920×1080 · PNG RGB | Wireframe LOD0 / LOD1, colliders, real tris | `FARM MACHINERY` / `LOD & COLLIDERS` | Catalog/09_Technical.png + 09_Technical_numbers.md | accepted (media_1) |
| 10_DemoAndVersion | 1920×1080 · PNG RGB | Harvest demo + what is / is not included | `FARM MACHINERY` / `HARVEST DEMO & CONTENTS` | Demo_Harvest_Overview.png (alt. Demo_Harvest_Beauty.png) + text block | accepted (media_1) |
| 11_CategoryDetails | 1920×1080 · PNG RGB | Harvest machines, headers, grain yard | `FARM MACHINERY` / `HARVEST & GRAIN YARD` | Catalog/11_Category_Harvest.png (spare: 11_Category_Implements, 11_Category_Trailers) | accepted after Fix 3 (tighter tile crops, media_1) |
| 12_Compositions | 1920×1080 · PNG RGB | 5 composition prefabs | `FARM MACHINERY` / `5 READY COMPOSITIONS` | Catalog/12_Compositions_Grid.png or 12_CMP_01…05 laid out as a grid (CMP_05 small on the grid — prefer the single renders) | accepted (media_1) |
| 13_Materials | 1920×1080 · PNG RGB | 3 atlases + result on models | `FARM MACHINERY` / `MATERIALS & COLOUR ATLASES` | Catalog/13_Materials_Models.png + 13_Atlas_Red / Green / Blue.png | accepted (media_1) |
| 14_UnityAndComparison | 1920×1080 · PNG RGB | Prefab in Unity (Hierarchy, LOD Group, Box Collider) + Lite vs Full panel | `FARM MACHINERY` / `UNITY SETUP · LITE VS FULL` | Catalog/14_Unity_Full.png + comparison panel | accepted (media_1) |

### Captions inside images (exact)

**06_FullCollection** — legend strip under the sheet (two lines):
- `TRACTORS 2 · IMPLEMENTS 7 · TRAILERS 6 · ATTACHMENTS & HEADERS 5 · HARVESTERS 3 · GRAIN YARD 2 · WINDROW 1`
- `VARIANTS: 8 COLOUR · 5 POSE · 2 LOAD`

**07_Closeups** — one caption per panel:
- Demo_Harvest_LowNode_Header: `SWAPPABLE GRAIN HEADER`
- Demo_Harvest_CloseHaymaking: `ROUND BALER ON THE DRAWBAR`
- Demo_Harvest_CloseGrainYard: `GRAIN AUGER & BINS`
- Demo_FieldWork_LowNode_Plough: `4-FURROW PLOUGH`
- Demo_FieldWork_CloseCMP01: `PLOUGH ON THE 3-POINT LINKAGE`
- footnote (small): `Wheat, bales and ground: demo-only environment`

**08_VariantsAndModules** — one caption per panel:
- 08_ColourVariants: `3 COLOURS · MATERIAL SWAP`
- 08_Poses: `TRANSPORT / WORK · EMPTY / FULL`
- 08_Modularity: `SWAPPABLE HEADERS · IMPLEMENTS · TRAILER CHAIN`
- 08_AttachPoints: `HITCH · LINK3P · PTO · FEEDER POINTS`
- footnote (small, under the attach-points panel): `Points are empty GameObjects; gizmos drawn for this image`

**09_Technical** — column heads `LOD0` · `LOD1` · `BOX COLLIDER`; row labels:
- row HRV-01: `COMBINE · LOD0 2,820 TRIS · LOD1 1,410 TRIS`
- row TRC-01: `CAB TRACTOR · LOD0 3,348 TRIS · LOD1 1,674 TRIS`
- row IMP-01: `PLOUGH · LOD0 1,260 TRIS · LOD1 630 TRIS`
- summary line: `FULL: 54,464 TRIS LOD0 (26 MODELS) · LOD1 ON 22 MODELS · BOX COLLIDER ON EVERY PREFAB`

**10_DemoAndVersion** — text block (side panel over calm sky/ground):
- heading: `WHAT'S INCLUDED`
- `26 MODELS · 41 PREFABS · 5 COMPOSITIONS`
- `3 DEMO SCENES: FIELD WORK · HARVEST · CATALOGUE`
- `SEPARATE WHEELS · NAMED ATTACH POINTS · LOD1 · COLLIDERS`
- heading: `NOT INCLUDED`
- `DRIVING SCRIPTS · ANIMATIONS · CHARACTERS`
- footnote (small): `Ground, wheat, bales and clouds: demo-only environment`

**11_CategoryDetails** — one label under each item (sheet rows back to front):
- row 1: `GRAIN BIN` · `GRAIN AUGER` · `ROUND BALER` · `ROUND BALER · OPEN`
- row 2: `COMBINE HARVESTER` · `FORAGE HARVESTER`
- row 3: `GRAIN HEADER 6 M` · `CORN HEADER 6 ROWS` · `PICKUP HEADER` · `WINDROW 4 M MODULE`

**12_Compositions** — one label per vignette + footnote:
- `CMP 01 · PLOUGHING · 2 PREFABS`
- `CMP 02 · GRAIN HAUL · 3 PREFABS`
- `CMP 03 · MACHINE YARD · 11 PREFABS`
- `CMP 04 · HARVEST · 6 PREFABS`
- `CMP 05 · HAYMAKING · 11 PREFABS`
- footnote (small): `Compositions reuse pack prefabs; they add no new models`

**13_Materials** — swatch labels and info line:
- under the three atlas swatches: `RED` · `GREEN` · `BLUE`
- info line: `3 ATLASES · 256×256 BASE COLOR · URP/LIT · 1 MATERIAL PER PREFAB`
- close-up panel: `FLAT-SHADED FACES · ONE COLOUR PER FACE`

**14_UnityAndComparison** — callouts on the Unity screenshot (FMS_Mach_Combine):
- `SEPARATE WHEELS · PIVOT AT CENTRE`
- `ATTACH POINTS: Feeder_Front · Hitch_Rear`
- `LOD GROUP: 2,820 / 1,410 TRIS`
- `BOX COLLIDER`

Comparison panel (heading + 3-column table; `—` = not included):
- heading: `LITE VS FULL`
- header row: ` ` | `LITE` | `FULL`
- `MODELS` | `13` | `26`
- `PREFABS (INCL. VARIANTS)` | `21` | `41`
- `COMPOSITIONS` | `3` | `5`
- `DEMO SCENES` | `2` | `3`
- `TRACTORS · IMPLEMENTS · TRAILERS` | `YES` | `YES`
- `HARVESTERS · HEADERS · BALER · GRAIN YARD` | `—` | `YES`

## Submission Notes

```text
Art-only package: no scripts. Demo scenes use a URP Volume and two simple unlit sky / cloud shaders included in Demo/Shaders. Assets in Demo/Environment (island base, field and wheat modules, road, grass, clouds, straw bales) exist only for the demo scenes and are not counted as product models. Attachments and headers are modelled at their mounted height, so they sit above Y = 0 when placed alone. Farm Machinery Lite is a subset of this package with the same file names.
```

## Notes (not for the portal)

**Решения владельца 2026-11-25:** цена Full — **USD 19.99**, без стартовой скидки (если владелец не попросит); Support — без
e-mail/URL, контакт в профиле издателя; категория `3D / Vehicles / Land` подтверждена; отдельного логотипа нет — store icon =
сгенерированная картинка по нашему рендеру с угловым бейджем `3D` (раскрыто в AI / Third-party).

Справка по цене (обоснование предложения до решения): прямые конкуренты Э3 (02_DEMAND.md, 2026-11-24) стоят $15–20 при 0 оценок и неподтверждённом
составе — Poly Pro Vehicles Farm $15.99, Stylized Tractor Pack $15.99, PolyOne Farm Vehicles $15.00 (по веб-поиску 28 моделей),
Gridness $15.00, Yorakeys $19.98, Stylized Farm Props and Vehicles $20.00, Low poly farm asset pack $29.99; общие паки фермы
Synty $49.99, ithappy $79.00. У нас 26 моделей / 41 префаб / 5 композиций и заявленное отличие (отдельные колёса, точки сцепки,
сменные жатки). Наши: Farm Yard $7.99, Farm Processing — предложение $19.99.

**[ПРОВЕРИТЬ после экспорта] (Э14):**
1. Package Size — нет экспорта; вписать размер `.unitypackage` 1.0.0 (не размер папки: `Assets/FarmMachinery` сейчас 79 МБ вместе
   с медиа-сценами и V1/V2-версиями демо-материалов).
2. Демо-сцены: в проекте нет `Demo_Catalog` из CATALOG — есть `Catalog_06_Full.unity` (те же 41 префаб рядами). Решить имя; в
   тексте «a catalogue scene» без имени. Медиа-сцены (Icon/Card/Cover/Hero/Catalog_*), `M_Demo_Backdrop_*`, `*_Soft`, `*_V2`,
   3 панорамы неба — исключить или оставить; после этого вписать число демо-текстур и материалов в Technical Details (7.2).
3. Описание Demo_Harvest в Demo / Scripts взято из CATALOG «Композиции и демо» и layout-файла — сверить со сценой после чистки.
4. Чистый импорт в Unity 6000.3.10f1 + URP 17.3: компиляция, missing scripts, розовые материалы (облака/небо на своих шейдерах),
   открытие 3 сцен, Validator. До этого «built with» вместо «tested with».
5. Все числа (tris 54,464 / 25,580, min/max, 41 префаб, 22 LOD, 46 всего) — из ImportCheck 2026-11-24 19:28; сверить после
   экспорта и при расхождении поправить подписи 06/09/10/12/14 (→ Э12).
6. Документации нет: `Assets/FarmMachinery/Documentation/` отсутствует (README + Changelog — Э14).
7. Lite ↔ Full: одинаковые имена/GUID в обоих пакетах (обещано в Submission Notes) — подтвердить способ сборки Lite.
8. Нет зависимости от Input System: скриптов нет, в Demo_Harvest.unity только компоненты URP (Volume,
   UniversalAdditionalCameraData/LightData) по m_Script — подтвердить в чистом проекте.

**Прочие открытые пункты:**
- Жатка в префабе комбайна: CATALOG HRV-01 говорит «несут вложенную жатку ATT-03», фактически префабы комбайна без жатки,
  жатки ставятся по Feeder-точкам (ImportNotes п. 2, renders_2: «нет вложенной жатки в иерархии» 14_Unity_Full). Карточка
  написана по факту; если владелец захочет вложенную жатку — поменять Scale / Setup и Description.
- Э12 (медиа) принят после исправлений: `planning/FarmMachinery/reviews/media_1.md` (Fix 1–2 — тексты карточек и угол `3D`
  на Card/Cover внесены сюда; Fix 3 — кадрирование 11_CategoryDetails в `build_media.py`, Codex; файл и CHECKS.md — после него). Шрифт плашек — Montserrat 9.000, SIL OFL 1.1 (`Media/layout/FONTS.md`,
  `fonts/OFL.txt`), в пакет не входит. Логотипа нет. `build_media.py` читает тексты из столбца «Plate text» и разделов
  «Captions» этой карточки — при правке строк Media пересобрать изображения.
- Отличия от пробной генерации: акцент Cover Full был `26 MODELS + 5 COMPOSITIONS` — теперь он только на Card, на Cover второй
  тезис (отдельные колёса и точки сцепки — главное отличие из Э3).
- Cover_Full и Hero_Full показывают демо-тюки DEM-08 (свои, решение владельца 2026-11-24) — это демо-окружение, входит в
  папку Demo, в счёт моделей не входит; сноска есть на 07 и 10.
- Ссылка на Lite в Support — после черновика Lite (Э15); ID Farm Nature и Farm Processing в Asset Store не нашёл — добавить
  или убрать.
- Лимиты Title (47 симв.), Summary (186, рабочий диапазон 10–200), тегов (14) — сверить с формой портала.
- Коллайдер — одна коробка на всю модель, включая колёса (PackPrefabBuilder), а не «без колёс» из контракта CATALOG п. 9.
- Перерасход tris ATT-01, TRL-04, TRL-06 покупателю не важен, в тексте не упоминается.
- Демо-окружение: ImportCheck пишет «DEM-01…05, 14 prefabs» — устарело; ImportReport_Demo перечисляет DEM-01…09 (20 префабов).
