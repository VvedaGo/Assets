# Cottage Garden Decor — Asset Store card

Product: Cottage Garden Decor (one paid product, no Lite) · Version: 1.0.0 · Updated: 2026-11-26 · Status: checked — Э13 done, Asset Store data decisions applied 2026-11-26; Э14 release check passed 2026-11-26 (numbers confirmed on the exported package); Э12 media not done yet
Fields and rules: REQUIREMENTS.md 7.1–7.3. Final texts go into the labelled blocks only; notes, options, TODO and
`[ПРОВЕРИТЬ]` go into the Notes block at the end.

Sources of numbers (all re-checked on disk 2026-11-26, Unity 6000.3.10f1, URP 17.3.0): `.work/ImportReport_CottageGardenDecor.txt`,
`.work/pipeline/CottageGardenDecor/import_report.md` (incl. follow-ups «no colliders» and «rename»), `.work/pipeline/CottageGardenDecor/scene_{demo,compositions,catalog}_report.md`,
files under `Assets/CottageGardenDecor/` (60 FBX, 60 + 6 prefabs, 2 materials, 2 textures, 3 scenes; YAML scan: 0 Collider components, 9 LODGroups,
composition contents counted from the CMP prefabs). Content = all rows of `planning/CottageGardenDecor/CATALOG.md` (sizes = «Фактические размеры после сборки»).

## Package Title

```text
Cottage Garden Decor - Arches, Gazebo & Pergola
```

## Category

```text
3D / Props / Exterior
```

## Keywords / Tags

```text
low poly, garden, cottage, cottagecore, gazebo, pergola, arch, roses, fountain, topiary, flower bed, garden furniture, modular, stylized, URP
```

## Summary
<!-- characters incl. spaces: 193 -->

```text
Stylized low poly cottage garden: 42 models + 18 variants - rose arches, gazebo, pergola, fountains, flower beds, roses, topiaries, garden furniture, modular wall and pond. 6 compositions. URP.
```

## Description

```text
Build a cozy cottage garden - rose arches, a hexagonal gazebo, a wisteria pergola, fountains and flower beds - with Cottage Garden Decor: 42 stylized low poly models, 18 variants and 6 ready compositions for front gardens, parks, village greens and backyard scenes.

This is the final pack of our Farm series. It shares the style, palette and 1 unit = 1 m scale of Farm Market, Farm Yard, Farm Nature, Farm Processing and Farm Machinery, and none of its items repeat those packs - it adds the decorative garden layer to them and works fully on its own. Use it for cozy and life sims, farming and town-building games, top-down and isometric scenes, mobile games and quick prototypes.

KEY FEATURES
- 60 single prefabs (42 models + 18 colour and mesh variants) and 6 composition prefabs built only from pack prefabs
- Garden structures that low poly packs rarely include: hexagonal gazebo, pergola with a 3 m extension bay, wooden and wrought iron arches, arbor bench, obelisk
- 5 snap-together modular systems on exact grids: lattice screen (2 m), low stone wall with ball pillars (2 m), brick edging with a 90° curve (1 m), raised formal pond with edges, corners and water tiles (1 m), pergola + extension bay (3 m)
- Climbing roses, rose garland, wisteria and ivy are separate models; the arches and the arbor bench have empty Plant_L, Plant_R and Plant_Top points for placing them
- Ready for your own animation: the gate leaf is pivoted on its hinge, the swing seat on its top beam, the hanging basket and bird feeder at their hang point
- Lightweight: 26,918 triangles for all 42 models (36 to 2,722 per model), LOD1 on 9 prefabs (gazebo, pergola and bay, arbor bench, tiered fountain, swing, planted beds), 2 atlas textures 256 x 256 and 2 URP/Lit materials for the whole pack
- 3 demo scenes: a cottage garden, the compositions, and a full catalogue

WHAT'S INCLUDED
- Structures (7): wooden rose arch, wrought iron arch, arbor bench, pergola 3 x 3 m, pergola extension bay 3 m, hexagonal gazebo, obelisk
- Modular pieces (9): lattice panel 2 m, lattice post, low stone wall 2 m, wall pillar with ball, brick edging 1 m, brick edging curve 90°, pond edge 1 m, pond corner, pond water tile 1 x 1 m
- Flower beds (3): straight 2 x 1 m, corner 2 x 2 m, round 2 m - each empty and planted
- Water (3): tiered fountain, wall fountain, birdbath
- Ornaments (5): sundial, garden gnome, stone urn, insect hotel, shepherd's hook with hanging basket
- Furniture (5): garden swing, hammock, bistro table, bistro chair, deck chair
- Plants (6): rose bush, climbing rose, rose garland, ivy patch, wisteria drape, hollyhock
- Topiary (4): ball standard, cone, spiral, three-ball tiered
- 18 variants (11 colour, 7 mesh): white arch, white arch with gate, white obelisk, 3 planted flower beds, blue-hat gnome, planted urn, hook with bird feeder, white bistro table and chair, blue deck chair, pink and white rose bush, pink climbing rose, pink rose garland, white hollyhock, rose standard topiary
- 6 compositions: Rose Arch Entrance, Pergola Terrace, Gazebo Retreat, Fountain Parterre, Walled Pond Corner, Wildlife Lawn
- 3 demo scenes: Demo_CottageGarden (all six compositions in one garden), Demo_Compositions (each composition and the modular systems on their own plinths), Demo_Catalog (all 60 prefabs and the 6 compositions with ID labels)

LIMITATIONS
This is an art pack: no scripts, no colliders, no rigs and no animation clips. Add a MeshCollider or simple colliders where your game needs them. The gate, swing seat, hanging basket and feeder are separate pivoted objects, not animations. Water is opaque stylized geometry without a water shader or simulation; plants are static meshes without wind. The island, lawn, path, sky and clouds in the demo scenes are demo-only assets and are not counted as models.

Works on its own. Requires only the Universal Render Pipeline.
```

## Technical Details

| Block | Value |
|---|---|
| Unique Assets / Prefabs | 42 unique models. 60 FBX files and 60 single-item prefabs = 42 base models + 18 variants (11 colour: same mesh, UVs moved to other atlas cells; 7 mesh: added geometry — gate, planted flowers, feeder, roses). 6 composition prefabs (`FMS_Garden_Comp_RoseArchEntrance` 13 prefab instances, `_PergolaTerrace` 17, `_GazeboRetreat` 14, `_FountainParterre` 33, `_WalledPondCorner` 33, `_WildlifeLawn` 15) built only from pack prefabs, no new meshes. 66 prefabs in total. A unique asset = one catalogue model; variants and compositions are counted separately |
| Polygon Count | Triangles, LOD0, measured in Unity on the imported meshes, each prefab counted once (compositions not counted again). 42 base models: min 36 (lattice post, pond water tile), max 2,722 (wrought iron arch), average 641, total 26,918. All 60 single prefabs incl. variants: total 47,604, average 793, largest variant 2,024 (corner bed, planted). By category, base models: Structures 7 — 236…2,722 (7,940); Modular 9 — 36…464 (1,492); Flower beds 3 — 204…252 (706; planted variants 1,456…2,024); Water 3 — 336…1,258 (2,022); Ornaments 5 — 348…888 (2,858); Furniture 5 — 384…1,096 (3,844); Plants 6 — 498…1,996 (6,730); Topiary 4 — 158…672 (1,326) |
| LODs | LOD Group with LOD0 + LOD1 on 9 prefabs: gazebo (2,314 / 1,156), pergola (332 / 178), pergola bay (248 / 164), arbor bench (1,276 / 638), tiered fountain (1,258 / 788), swing (580 / 356), straight / corner / round planted beds (1,456 / 830, 2,024 / 1,138, 1,766 / 1,008). LOD1 = 50–66 % of LOD0, 6,256 triangles in total. Transitions: LOD0 down to 25 % screen height, LOD1 down to 1.5 %, culled below. No LOD on the other 51 prefabs (all 2,722 triangles or less). The swing's LOD1 seat is a child of its pivoted seat |
| Textures | 2 PNG Base Color atlases, 256 × 256, RGB, no alpha: `FMS_Garden_AtlasA` (structures, furniture, stone, metal, water) and `FMS_Garden_AtlasF` (plants, flower beds, topiary, urn, shepherd's hook). Each is a 4 × 4 grid of flat colour cells (one colour per cell). Import: Point filter, no mipmaps, uncompressed, sRGB. No Normal, Metallic, AO or other maps. Demo-only textures are listed under Demo / Scripts |
| Materials / Shaders | 2 materials (`FMS_Garden_AtlasA`, `FMS_Garden_AtlasF`), shader Universal Render Pipeline/Lit, opaque, smoothness 0.15, metallic 0, GPU instancing on. Every model uses exactly one of the two. Demo-only materials are listed under Demo / Scripts |
| UVs | One UV channel (UV0) per mesh: every face is mapped to one flat colour cell of its atlas (no unwrap, no texture detail). Colour variants differ only in the cells they use. No lightmap UV2 (Generate Lightmap UVs off) |
| Rigging / Animations | Static meshes, no rig, no skinning, 0 animation clips. Separate pivoted objects (not animations): `Gate_Leaf` on the arch with gate (hinge axis Y), `Seat` on the swing (top-beam axis X), `Hanging` basket / feeder on the shepherd's hook (hang point) |
| Colliders | None. No collider components on any prefab (60 single + 6 compositions). Add a MeshCollider or primitive colliders as your game needs |
| Scale / Setup | 1 unit = 1 m, Y up. Root pivot on the ground (Y = 0) at the base centre, root position 0, rotation 0, scale 1. Grid pieces: lattice panel + post and stone wall + pillar on a 2 m grid, brick edging and pond on a 1 m grid, pergola bay at pergola + 1.5 m, then every 3.0 m; flower beds fill whole 1 m cells. Deliberate exceptions: lattice panel frame starts 0.05 m above its pivot (the posts carry it); pond water slab top at 0.38 m with the pivot on the ground; wisteria pivot on its top face (hangs under a beam, e.g. the pergola beam at 2.24 m); pond edge pivot at the middle of its inner face, pond corner and curved edging pivots at the grid corner / circle centre. Empty attach points `Plant_L`, `Plant_R`, `Plant_Top` on the wooden, white, gated and iron arches and the arbor bench. Naming `FMS_Garden_<Name>`, variants `FMS_Garden_<Name>_<Variant>`, compositions `FMS_Garden_Comp_<Name>` (origin at the front centre, root identity). Real sizes, e.g. gazebo 3.58 × 3.58 × 4.00 m, tiered fountain 2.40 × 2.40 × 2.42 m, garden gnome 0.24 × 0.23 × 0.45 m |
| Files / Sources | `Assets/CottageGardenDecor/Art`: 60 FBX (Models/<category>), 60 prefabs (Prefabs/<category>) + 6 composition prefabs (Prefabs/CMP), 2 materials, 2 PNG textures. `Assets/CottageGardenDecor/Demo`: demo scenes and demo-only assets. `Assets/CottageGardenDecor/Documentation`: README.txt, Changelog.txt. 155 files in 32 folders, all under `Assets/CottageGardenDecor` (no Editor scripts, no files outside the pack folder). Blender files, Blender build scripts and the Unity editor build tools are not included |
| Demo / Scripts | 3 demo scenes in `Demo/Scenes`: Demo_CottageGarden (six compositions and free-standing items in one garden on a floating island), Demo_Compositions (the 6 compositions and the 5 modular systems, each on its own island plinth), Demo_Catalog (all 60 prefabs in rows by category + the 6 compositions, with ID labels as TextMesh in the built-in font). Each scene has one camera (Main Camera). No scripts in the package and no camera controller; the scenes use a URP Volume for post-processing. Demo-only assets (not counted above): 3 FBX (island, path, clouds), 7 prefabs (island, path, 5 clouds), 6 materials (demo atlas, island plinth, catalogue floor, backdrop, sky, clouds), 1 texture 256 × 256 (demo atlas), 2 shaders (gradient sky, clouds), 1 Volume profile (`FMS_Garden_Look`) |
| Compatibility / Dependencies | Unity 6000.3 (tested with 6000.3.10f1, clean import of the exported package), Universal Render Pipeline 17.3. Built-in Render Pipeline and HDRP are not supported. No other packages required; no Input System dependency |
| Package Size | 2.6 MB (2,550,536 bytes) — CottageGardenDecor_1.0.0.unitypackage, version 1.0.0 (folder `Assets/CottageGardenDecor` only) |

## Price

```text
USD 12.99
```

(Decision 2026-11-26, delegated by the owner to the pipeline; no launch discount. Reasoning in Notes.)

## Version / Release Notes

Version: `1.0.0`

```text
1.0.0 - First release.
- 42 low poly cottage garden models: 7 structures, 9 modular pieces, 3 flower beds, 3 water features, 5 ornaments, 5 furniture pieces, 6 plants, 4 topiaries
- 60 prefabs (42 models + 18 colour and mesh variants) and 6 compositions
- 5 modular systems on 1 m / 2 m / 3 m grids, plant attach points on arches, pivoted gate, swing seat and hanging basket
- LOD1 on 9 prefabs; 2 atlases 256 x 256, 2 URP/Lit materials; no colliders
- 3 demo scenes: Demo_CottageGarden, Demo_Compositions, Demo_Catalog
- Unity 6000.3, URP 17.3
```

## Compatibility

```text
Unity 6000.3 (tested with 6000.3.10f1). Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported. The package contains no code, so there are no platform-specific requirements; performance on specific mobile devices has not been measured.
```

## Dependencies

```text
Required: Universal Render Pipeline (com.unity.render-pipelines.universal) 17.3.
No other Asset Store products are needed. The demo scenes use only assets included in this package.
```

## Support

```text
Support: contact via the publisher profile
Documentation: Assets/CottageGardenDecor/Documentation/README.txt
Same series: Farm Market, Farm Yard, Farm Nature, Farm Processing, Farm Machinery, Farm Animals
```

## AI / Third-party

```text
AI use: reference images for each model and for the demo scene layouts were generated with an AI image generator (Sol 6.2) and used only as references. The 3D models were built procedurally in Blender with Python scripts, written with AI coding assistance, from those references and reviewed by hand; no AI 3D generator was used. Textures are two flat-colour atlases made by script. All store images are renders of the included prefabs and demo scenes in Unity; text plates and labels are composited over the unaltered renders.
Third-party content: none. No third-party models, textures, code, fonts or audio are included in the package.
```

Fonts on store images (not in the package): Montserrat 9.000, SIL Open Font License 1.1 — the series font from
`origin/Farm-Machinery:AssetStore/FarmMachinery/Media/layout/fonts/Montserrat.ttf` + `OFL.txt` (SHA-256 of the font
`0f7b311b2f3279e4eef9b2f968bcdbab6e28f4daeb1f049f4f278a902bcd82f7`, source Google Fonts, see that branch's `Media/layout/FONTS.md`).
Э12 copies both files into `AssetStore/CottageGardenDecor/Media/layout/fonts/` and writes `Media/layout/FONTS.md`. No other fonts.

## Media

Paid set = 15 images: REQUIREMENTS 7.4 standard 14 (4 main + 10 screenshots) + `06b_FullCollection` (REQUIREMENTS 7.5: «Если предметы
становятся мелкими — разделить на дополнительные кадры»; renders_3: gnome, edging, pond pieces, hooks too small in 06 at 50 %). Video: none.
Raw sources: `AssetStore/CottageGardenDecor/Media/raw/` (clean, no text; accepted in `planning/CottageGardenDecor/reviews/renders_1.md`,
`renders_2.md`, `renders_3.md`). Label maps `*_labels.json` next to the raws: per item `id`, `prefab`, pixel `rect [x, y, w, h]` (top-left origin,
projected LOD0 mesh; label goes under the rect) and per-category union rects. Final files → `AssetStore/CottageGardenDecor/Media/final/`
(PNG RGB, opaque; icon also 1024 master and a 60 px check; card also 1260×840).

Plate system (REQUIREMENTS 7.6, same as Farm Machinery):
- Icon / Card / Cover — corner badge `3D` (red `#C8473B` triangle top left, white letters); no LITE / FREE / NEW / UPDATE badges. No logo (series decision).
- Card / Cover — dark plate `#20242A` bottom left, cream title `#F2E6C9`, red accent strip `#C8473B` under the title. Card plate 35–40 % of the height, Cover 20–25 %.
- Gallery — compact dark plate bottom left, 8–12 % of the height: line 1 = `COTTAGE GARDEN DECOR`, line 2 = frame theme. Never over items, catalogue labels or Inspector text.
- Font: Montserrat (Bold / ExtraBold for titles, SemiBold for labels). Typography: `·` = U+00B7, `×` = U+00D7, `²` = U+00B2, `–` = en dash, `—` = em dash; letters exactly as written, case included.
- Item labels: under the rect from the label map, centred, one line, uppercase, dark text on the light catalogue floor (`#20242A` on `#E9E9EC`), or cream on a small dark tag over sky/lawn.

Gallery upload order (REQUIREMENTS 7.5): 05 → 06 → 06b → 07 → 08 → 11 → 12 → 10 → 13 → 09 → 14.

| File | Size | Purpose | Plate text (exact) | Source render | Status |
|---|---|---|---|---|---|
| 01_Icon | 160×160 (+1024 master, check at 60) · PNG RGB | Store icon: white rose arch with gate, climbing roses and garland, rose bushes on a small island, light sky | Corner badge: `3D` · no other text | raw/IconSource.png (1024²); crop slightly tighter, arch ~85 % of the width (renders_3) | raw ✅ (renders_3); final — Э12 |
| 02_Card | 420×280 (+1260×840) · PNG RGB | Search card: rose arch entrance (arch with gate, roses, planted beds, gnome) | Corner badge: `3D` · Title: `COTTAGE GARDEN DECOR` · Accent: `42 MODELS + 6 COMPOSITIONS` | raw/Card.png (1260×840; bottom 35 % free sky, lowest item row 64.9 %) | raw ✅ (renders_3 pass 2); final — Э12 |
| 03_Cover | 1950×1300 · PNG RGB | Page cover: whole cottage garden, gazebo focus | Corner badge: `3D` · Title: `COTTAGE GARDEN DECOR` · Accent: `42 MODELS · 18 VARIANTS · 6 COMPOSITIONS` | raw/Cover.png (1950×1300; rows 971–1300 clean sky for the plate) | raw 🟡 accepted (renders_1/2); final — Э12 |
| 04_Social | 1200×630 · PNG RGB | Link preview, clean render | — (no text, no badge) | raw/Hero.png: crop rows 20–1028 (full width 1920 × 1008), scale to 1200×630; gazebo apex stays inside | raw ✅; final — Э12 |
| 05_Hero | 1920×1080 · PNG RGB | Ready scene: the demo garden with all six compositions | `COTTAGE GARDEN DECOR` / `COTTAGE GARDEN DEMO` | raw/Hero.png | raw ✅ (renders_2); final — Э12 |
| 06_FullCollection | 1920×1080 · PNG RGB | All 42 base models, one scale, by category | `COTTAGE GARDEN DECOR` / `FULL COLLECTION · 42 MODELS · 60 PREFABS` | raw/06_FullCollection.png + _labels.json (category rects) | raw 🟡 accepted (renders_3); final — Э12 |
| 06b_FullCollection | 1920×1080 · PNG RGB | Plants, topiary and ornaments larger (small items of 06) | `COTTAGE GARDEN DECOR` / `PLANTS · TOPIARY · ORNAMENTS` | raw/06_FullCollection_2.png + _labels.json (per item) | raw ✅ (renders_3 pass 2); final — Э12 |
| 07_Closeups | 1920×1080 · PNG RGB | 5 detail panels cropped from the composition vignettes | `COTTAGE GARDEN DECOR` / `DETAILS` | crops of raw/CMP-01, CMP-04, CMP-02, CMP-05, CMP-06 (see Captions) | raw ✅/🟡 (renders_2); final — Э12 |
| 08_VariantsAndModules | 1920×1080 · PNG RGB | 18 variants next to their base + 5 modular systems assembled (3 panels) | `COTTAGE GARDEN DECOR` / `VARIANTS & MODULES` | raw/08_Variants_A.png, 08_Variants_B.png (+ _labels.json), raw/Modules.png (no label map) | raw ✅ / 🟡 (renders_2/3); final — Э12 |
| 09_Technical | 1920×1080 · PNG RGB | Shaded wireframe, real LOD0 / LOD1 tris, no-collider note | `COTTAGE GARDEN DECOR` / `WIREFRAME & LOD` | raw/09_Technical.png + _labels.json | raw ✅ (renders_3); final — Э12 |
| 10_DemoAndVersion | 1920×1080 · PNG RGB | Demo from another angle (walled pond with iron arch, gazebo) + what is / is not included | `COTTAGE GARDEN DECOR` / `DEMO & CONTENTS` | raw/AltView.png + text block in the clean sky corner (upper left per scene_demo_report; confirm on the PNG) | raw 🟡 accepted (renders_1/2); final — Э12 |
| 11_CategoryDetails | 1920×1080 · PNG RGB | Structures and furniture larger, each labelled | `COTTAGE GARDEN DECOR` / `STRUCTURES & FURNITURE` | raw/11_CategoryDetails.png + _labels.json | raw ✅ (renders_3); final — Э12 |
| 12_Compositions | 1920×1080 · PNG RGB | The 6 composition prefabs, 3 × 2 grid | `COTTAGE GARDEN DECOR` / `6 READY COMPOSITIONS` | raw/CMP-01 … CMP-06.png (one vignette per cell, same camera) | raw ✅/🟡 (renders_2 pass 3); final — Э12 |
| 13_Materials | 1920×1080 · PNG RGB | 2 atlases + result on models | `COTTAGE GARDEN DECOR` / `MATERIALS & ATLASES` | raw/13_Materials.png + _labels.json; swatches from `Assets/CottageGardenDecor/Art/Textures/FMS_Garden_AtlasA.png`, `FMS_Garden_AtlasF.png` (nearest-neighbour upscale) in the free left ~36 % | raw ✅ (renders_3); final — Э12 |
| 14_UnityAndComparison | 1920×1080 · PNG RGB | Single product → Unity setup and package structure instead of a Lite/Full comparison | `COTTAGE GARDEN DECOR` / `UNITY SETUP` | raw/14_Unity.png — automatic capture of this project's Editor (Project on Art/Prefabs/STR, `FMS_Garden_Gazebo` selected, Inspector with the LOD Group) | final ✅ 🟡 (media_1 pass 2) |

### Captions inside images (exact)

**01_Icon** — no text; badge `3D` only.

**06_FullCollection** — one category label under each category rect of `06_FullCollection_labels.json` (rows back to front):
- row 1: `STRUCTURES 7` (STR rect; pergola and bay shown assembled)
- row 2: `WATER 3` (WTR) · `FURNITURE 5` (FUR)
- row 3: `FLOWER BEDS 3` (FLB) · `PLANTS 6` (PLT)
- row 4: `MODULAR PIECES 9` (MOD)
- row 5: `ORNAMENTS 5` (ORN) · `TOPIARY 4` (TOP)
- legend strip under the sheet (two lines):
  - `STRUCTURES 7 · MODULAR 9 · FLOWER BEDS 3 · WATER 3 · ORNAMENTS 5 · FURNITURE 5 · PLANTS 6 · TOPIARY 4`
  - `+ 18 VARIANTS: 11 COLOUR · 7 MESH`

**06b_FullCollection** — one label under each item rect of `06_FullCollection_2_labels.json`, plus a small category heading over each row:
- headings: `PLANTS 6` · `TOPIARY 4` · `ORNAMENTS 5`
- PLT-01 `ROSE BUSH` · PLT-02 `CLIMBING ROSE` · PLT-03 `ROSE GARLAND` · PLT-04 `IVY PATCH` · PLT-05 `WISTERIA` · PLT-06 `HOLLYHOCK`
- TOP-01 `BALL STANDARD` · TOP-02 `CONE` · TOP-03 `SPIRAL` · TOP-04 `TIERED`
- ORN-01 `SUNDIAL` · ORN-02 `GNOME` · ORN-03 `STONE URN` · ORN-04 `INSECT HOTEL` · ORN-05 `SHEPHERD'S HOOK`

**07_Closeups** — 5 panels (one large + four small), one caption per panel:
- crop of CMP-01 on the arch: `ROSE ARCH WITH GATE · CLIMBING ROSES`
- crop of CMP-04 on the fountain: `TIERED FOUNTAIN · TOPIARY PARTERRE`
- crop of CMP-02 under the pergola: `WISTERIA PERGOLA · BISTRO SET`
- crop of CMP-05 on the pond: `WALL FOUNTAIN · MODULAR POND · IRON ARCH`
- crop of CMP-06 on the wildlife corner: `INSECT HOTEL · BIRDBATH · SUNDIAL`
- footnote (small): `Lawn plinths: demo-only environment`

**08_VariantsAndModules** — two variant panels (08_Variants_A, 08_Variants_B) and one modules panel; one caption per variant group (under the group, positions from the item rects):
- 08_Variants_A: `ARCH: WOOD · WHITE · WHITE WITH GATE` · `OBELISK: WOOD · WHITE` · `FLOWER BEDS: EMPTY · PLANTED` · `CLIMBING ROSE: RED · PINK` · `HOLLYHOCK: PINK · WHITE` · `DECK CHAIR: RED · BLUE`
- 08_Variants_B: `ROSE BUSH: RED · PINK · WHITE` · `ROSE GARLAND: RED · PINK` · `TOPIARY: BALL · ROSE STANDARD` · `URN: EMPTY · PLANTED` · `HOOK: BASKET · BIRD FEEDER` · `GNOME: 2 COLOURS` · `BISTRO SET: IRON · WHITE`
- variants panel heading: `18 VARIANTS · 11 COLOUR · 7 MESH`
- Modules panel (no label map — place by eye, see `scene_compositions_report.md` «Modules layout»): `POND · 1 M GRID` (front left) · `BRICK EDGING · 1 M GRID` (front centre) · `LATTICE SCREEN · 2 M GRID` (front right) · `STONE WALL · 2 M GRID` (back left) · `PERGOLA + 3 M BAY` (back right)
- modules panel heading: `5 SNAP-TOGETHER SYSTEMS`

**09_Technical** — labels under the rects of `09_Technical_labels.json`:
- STR-06 (LOD0, left): `GAZEBO · LOD0 · 2,314 TRIS`
- STR-06 (LOD1, right): `GAZEBO · LOD1 · 1,156 TRIS`
- PLT-01: `ROSE BUSH · 1,996 TRIS · NO LOD`
- MOD group (pond kit 2×1): `POND KIT · EDGE 76 · CORNER 80 · WATER 36 TRIS`
- summary line: `42 MODELS · 26,918 TRIS LOD0 · 36–2,722 PER MODEL · LOD1 ON 9 PREFABS`
- note line: `NO COLLIDERS — ADD MESHCOLLIDER OR PRIMITIVES AS NEEDED`
- footnote (small): `Wireframe drawn for this image`

**10_DemoAndVersion** — text block over the clean sky corner:
- heading: `WHAT'S INCLUDED`
- `42 MODELS · 60 PREFABS · 6 COMPOSITIONS`
- `3 DEMO SCENES: GARDEN · COMPOSITIONS · CATALOGUE`
- `5 MODULAR SYSTEMS · LOD1 ON 9 PREFABS · 2 ATLASES 256²`
- heading: `NOT INCLUDED`
- `COLLIDERS · SCRIPTS · ANIMATIONS`
- footnote (small): `Island, lawn, path, sky and clouds: demo-only environment`

**11_CategoryDetails** — group headings `STRUCTURES 7` · `FURNITURE 5`; one label under each rect of `11_CategoryDetails_labels.json`:
- STR-06 `HEXAGONAL GAZEBO` · STR-04 `PERGOLA 3×3 M` · STR-05 `PERGOLA BAY 3 M` · STR-01 `ROSE ARCH` · STR-02 `IRON ARCH` · STR-03 `ARBOR BENCH` · STR-07 `OBELISK`
- FUR-01 `GARDEN SWING` · FUR-02 `HAMMOCK` · FUR-03 `BISTRO TABLE` · FUR-04 `BISTRO CHAIR` · FUR-05 `DECK CHAIR`

**12_Compositions** — one label per vignette + footnote (numbers = prefab instances counted in the CMP prefabs):
- `CMP 01 · ROSE ARCH ENTRANCE · 13 PREFABS`
- `CMP 02 · PERGOLA TERRACE · 17 PREFABS`
- `CMP 03 · GAZEBO RETREAT · 14 PREFABS`
- `CMP 04 · FOUNTAIN PARTERRE · 33 PREFABS`
- `CMP 05 · WALLED POND CORNER · 33 PREFABS`
- `CMP 06 · WILDLIFE LAWN · 15 PREFABS`
- footnote (small): `Compositions reuse pack prefabs; they add no new models · plinths are demo-only`

**13_Materials** — swatch labels, model labels and info line:
- under the swatches: `ATLAS A · STRUCTURES & FURNITURE` · `ATLAS F · PLANTS & BEDS`
- model labels under the rects of `13_Materials_labels.json`: STR-01_Gate `ARCH WITH GATE · A` · WTR-01 `TIERED FOUNTAIN · A` · FUR-01 `SWING · A` · PLT-01 `ROSE BUSH · F` · PLT-06 `HOLLYHOCK · F` · TOP-03 `SPIRAL TOPIARY · F` · FLB-03_Planted `ROUND BED, PLANTED · F`
- info line: `2 ATLASES · 256×256 BASE COLOR · URP/LIT · 2 MATERIALS`
- second line: `FLAT-SHADED FACES · ONE COLOUR PER FACE`

**14_UnityAndComparison** — callouts on the Editor capture (`FMS_Garden_Gazebo` selected):
- `LOD GROUP: 2,314 / 1,156 TRIS`
- `PIVOT ON THE GROUND · 1 UNIT = 1 M`
- `ONE MATERIAL: FMS_Garden_AtlasA`
- side panel heading: `PACKAGE STRUCTURE`
  - `Art/Models — 60 FBX`
  - `Art/Prefabs — 60 PREFABS + 6 COMPOSITIONS`
  - `Art/Materials — 2 · Art/Textures — 2`
  - `Demo/Scenes — 3`

## Submission Notes

```text
Art-only package: no scripts. Prefabs intentionally have no colliders (stated in the description). Demo scenes use a URP Volume and two simple sky / cloud shaders included in Demo/Shaders. The island, path, clouds and plinths in Demo/ exist only for the demo scenes and are not counted as product models. Three prefabs have deliberate pivots off the base: the lattice panel (frame starts 0.05 m up, carried by the posts), the pond water tile (slab at 0.34-0.38 m, pivot on the ground) and the wisteria drape (pivot on the top face, hangs under a beam).
```

## Notes (not for the portal)

**Решения 2026-11-26 (владелец передал данные Asset Store конвейеру; оркестратор зафиксировал):**
1. **Title:** `Cottage Garden Decor - Arches, Gazebo & Pergola` — 47 симв., максимум серии; «low poly» оставлен в тегах и Summary.
   Плашки медиа не меняются: на всех изображениях короткое имя `COTTAGE GARDEN DECOR` (сверено по разделу Media).
2. **Цена:** **USD 12.99**, без стартовой скидки. Обоснование: якорь серии — Farm Nature $9.99 и Farm Market $9.99 при большем
   числе предметов; спрос в Э3 не подтверждён (у 13 из 15 страниц конкурентов «not enough ratings», NO-GO отменён владельцем);
   но у пака 42 модели + 18 вариантов + 6 композиций (5 модульных систем) — самое большое содержимое среди садовых конкурентов Э3
   (Low Poly Garden & Backyard Kit $6, Low-poly garden $12.50, Flowers Pack $18.49, Low Poly Style Fountains $22.90,
   Stylized Garden Asset Pack $30 — у всех состав не виден или меньше). Отсюда цена чуть выше якоря серии и ниже Farm Animals
   ($14.99) и Machinery ($19.99). Цена нигде не публиковалась.
3. **06b** остаётся 15-м изображением галереи.
4. **Support:** «contact via the publisher profile», как в Farm Machinery (последний пак); e-mail в карточке нет.
5. **Ссылки на серию:** только названия паков, без ID и ссылок Asset Store.
6. **AI-формулировка** «Python scripts, written with AI coding assistance» — оставлена.

**Сверка цифр (все проверены на диске 2026-11-26):** 60 FBX = 60 префабов (STR 10, MOD 9, FLB 6, WTR 3, ORN 8, FUR 8, PLT 11, TOP 5); 42 базовых + 18 вариантов
(11 цвет + 7 меш — по CATALOG и по файлам); 6 CMP-префабов, составы совпадают с CATALOG (13 / 17 / 14 / 33 / 33 / 15 экземпляров);
3 сцены; Collider-компонентов 0; LODGroup 9 (списки совпадают с import_report); 2 материала, 2 текстуры 256×256 RGB без альфы;
один UV-канал (FBX: по одному LayerElementUV на меш), Generate Lightmap UVs выключен; tris — по ImportReport (сумма 42 = 26,918, 60 = 47,604,
LOD1 = 6,256 — пересчитано). Демо-сцены ссылаются только на компоненты URP (Volume, UniversalAdditionalCamera/LightData, overrides) — своих скриптов 0.
Точки `Plant_L/R/Top` есть на STR-01, _White, _Gate, STR-02, STR-03.

**Э14 — проверка поставки (2026-11-26), все 7 пунктов `[ПРОВЕРИТЬ после экспорта]` закрыты** (подробно — `.work/pipeline/CottageGardenDecor/release_check.md`):
1. Package Size — **2.6 MB (2,550,536 байт)**, `.work/release/CottageGardenDecor_1.0.0.unitypackage` (размер `.unitypackage`, не папки; папка с .meta — 5.0 MB). Вписано в Technical Details.
2. Демо-материалы — **6** (Sky_Light и Wire перенесены в `Assets/Editor/CottageGardenDecor/MediaOnly` и в пакет не входят). Technical Details исправлен (было 8).
3. Чистый импорт: новый проект Unity 6000.3.10f1, шаблон Universal 3D (URP 17.3.0), `-importPackage` в batchmode → ошибок компиляции 0, ошибок/предупреждений по паку в логе 0, missing scripts 0, розовых/битых материалов 0 (8 материалов, 2 шейдера — supported, 0 ошибок), префабы 73/73 загружаются (60 + 6 CMP + 7 демо), 3 сцены: missing references 0, broken prefab instances 0, по одной камере, Volume `FMS_Garden_Look` с 7 overrides, рендер каждой сцены без magenta. «tested with 6000.3.10f1» вписано в Technical Details и Compatibility. Отчёт `.work/release/clean_check/check.txt`, рендеры `.work/release/clean_DemoCottageGarden.png` и `clean_check/*.png`, логи `.work/release/logs/`.
4. Documentation: `Assets/CottageGardenDecor/Documentation/README.txt` и `Changelog.txt` (1.0.0, 2026-11-26) созданы и входят в пакет.
5. Состав экспорта: только `Assets/CottageGardenDecor` (155 файлов, 32 папки); `Assets/Editor/**`, `.work`, `art/`, `planning/` не входят. Зависимости вне папки пака — только пакеты URP / Core RP (Lit.shader / Lit.mat, Volume, VolumeProfile, overrides, UniversalAdditionalCamera/LightData). Список с GUID — `.work/release/CottageGardenDecor_1.0.0_files.txt`.
6. Asset Store Validator 12.0.6 (категория 3D, путь `Assets/CottageGardenDecor`, тип UnityPackage): **37 Pass, 0 Warning, 0 Fail** — `.work/release/Validator_CottageGardenDecor.txt`. Примечание: «Check Colliders» проверяет только префабы с флагом Static; наши не static, поэтому Pass при отсутствии коллайдеров — это не подтверждение коллайдеров.
7. Число файлов поставки — 155 (+ 32 папки, 187 записей в пакете).
Числа на изображениях не меняются (составы, tris, материалы атласов прежние; демо-материалы на картинках не указаны).

**Прочие открытые пункты:**
- **14_UnityAndComparison:** готов (автоматический снимок редактора этого проекта, Gazebo в Inspector), принят в media_1 pass 2.
- **Цвета в подписях 08** (`RED`, `PINK`, `WHITE`, `WOOD`, `IRON`, `BLUE`) взяты из CATALOG/STYLE и проверки вариантов в scene_catalog_report; Э12 сверяет глазами на 08_Variants_A/B. Базовый цвет гнома в каталоге не назван однозначно — поэтому `GNOME: 2 COLOURS`.
- **04_Social** взят из Hero (Cover с пустым небом снизу под плашку обрезался бы плохо); если нужен отличающийся кадр — AltView.png с той же обрезкой.
- **Иконка:** по плану — реальный рендер IconSource с бейджем `3D` (в Machinery иконка была ImageGen-артом по рендеру). Если Э12 сделает ИИ-арт — дописать это в AI / Third-party, как в Machinery.
- **Category:** `3D / Props / Exterior` — там же конкуренты Э3 (Low-poly garden, Garden & Backyard Kit, Low Poly Style Fountains). Альтернатива `3D / Environments` (если продаём как «сад целиком»). Сверить список категорий портала.
- **Лимиты:** Title 47 симв., Summary 193 (рабочий диапазон 10–200), Description 3,874, тегов 15 — сверить с формой портала.
- **Не упомянуто для покупателя:** перерасход tris STR-02 (2,722 при бюджете 1,400, в пределах допуска ×2 для кованых деталей) — покупателю не важно.
- **Известные особенности моделей (renders_1/2):** STR-01_Gate целиком белая; плети PLT-02 стоят на боковых гранях арки — не дефекты, в тексте не обещается иное.
