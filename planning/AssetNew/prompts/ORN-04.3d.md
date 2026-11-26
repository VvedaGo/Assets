# ORN-04 Insect Hotel — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/ORN-04.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: ORN-04 Домик для насекомых `FMS_Garden_Insect_Hotel`, atlas A `Garden_Build`, material `M_Garden_Build`. Silhouette difference from duplicate (Farm Yard `FMS_Birdhouse`): wide open rack 0.6 × 1.1 on legs, cells with logs, straw and bricks, no entrance hole; the birdhouse is a closed box.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.3×1.1 | 900 | no | no | none |

Static, no moving parts. Pivot: centre of the footprint on the ground (Y = 0), root scale 1, rotation 0, Y up; the open front faces +Z. Round holes and logs use 6–8 segments.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Legs | 4 boxes 0.10 × 0.10 × 0.20 at the frame corners, X ±0.22, Z ±0.10, Y 0–0.20 (~48) | 1 dark wood `#7A5233` | static, model pivot at ground centre |
| Frame boards | outer box frame X ±0.27 (0.54 wide), Z ±0.14 (0.28 deep), Y 0.20–0.96; boards 0.05 thick (top, bottom, 2 sides), open front and no closed back (~90) | 1 dark wood | static |
| Back panel | flat panel 0.44 × 0.02 × 0.66 at the rear inside, Z −0.12 (12) | 1 | static |
| Dividers | 2 uprights 0.03 × 0.22 × 0.66 and 2 shelves 0.44 × 0.22 × 0.03 → 3 columns × 3 rows of cells, each about 0.127 wide × 0.20 high × 0.20 deep (~96) | 0 light wood `#B5835A` | static |
| Log cells (3 cells) | 4–5 short log ends per cell, 6-sided prisms Ø0.05–0.06, length 0.18, front caps proud by 0.01, alternating slots; on some logs a recessed 6-gon hole Ø0.02 (~270) | logs 0, 2 `#9C6B44`, 1; holes 8 `#6E757B` | static |
| Straw cells (3 cells) | 6–8 upright 4-sided tapered stalks per cell in a bundle with a slight lean, fill cell height (~110) | 4 straw `#DCC9A0` | static |
| Brick cells (3 cells) | 1 brick block per cell 0.12 × 0.19 × 0.17, face with 6 recessed hole 6-gons Ø0.025 (~150) | 14 `#9C3F33`, 6 `#A8372E`, holes 8 | static |
| Roof boards | 2 boards 0.62 × 0.20 × 0.03 at about 25° pitch forming a gable, ridge along X, ridge height Y 1.10, overhang 0.03 front/back/sides; width 0.60 (~50) | 0 light wood | static |
| Ridge board | thin board 0.62 × 0.05 × 0.03 along the ridge (~12) | 1 dark wood | static |

Cells are assigned so neighbours differ, e.g. row top: log / straw / brick; row middle: brick / log / straw; row bottom: straw / brick / log. Estimated sum ~830 tris, up to 900 allowed; the builder trims log or hole counts to stay within the budget, never the frame thickness.

## Anchor

Closest approved model: none in this pack. Earlier packs by name only: Farm Yard `FMS_Birdhouse` (wood board thickness), превью нет в ветке.

## What NOT to do

- No closed box, no entrance hole, no perch, no door: the front stays open.
- No thin slats: boards ≥ 0.05, dividers ≥ 0.03.
- No full-size roof overhang beyond 0.60 width; no ridge higher than Y 1.10.
- No insects, birds or bees; no wire mesh.
- Logs and bricks must sit inside the cells and touch the back panel or shelves (no floating pieces).
- Holes are recessed faces in slot 8, not alpha holes or boolean cutters that leave coplanar faces.
- No coplanar overlap between roof boards, frame top and ridge; offset ≥ 1 mm.
- Do not exceed 900 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
