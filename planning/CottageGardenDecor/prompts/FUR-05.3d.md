# FUR-05 Deck_Chair — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/FUR-05.png  (selected 2026-11-26, Э6 batch 4)

## Catalogue

Line: FUR-05 · Folding deck chair, unfolded · `FMS_Garden_Deck_Chair` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×1.0×0.9 | 400 | no | no | `_Blue` (colour: stripes blue `#4A78A8` instead of red; same mesh, UV to slot 15; separate FBX and prefab) |

Static, unfolded; no moving parts.

## Parts

Pivot: centre of the footprint on the ground (Y = 0). Front of the chair = +Z (feet toward the viewer), reclined back toward −Z.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Front legs (2) | Wooden posts (shared construction, slimmer on this small folding chair): 0.05 × 0.06, X = ±0.26, from the foot (Z +0.45, Y 0) up to the armrest joint (Z +0.40, Y 0.55), leaning back slightly | 0 light wood | static |
| Back rails (2) | Long reclined rails 0.05 × 0.06 from the foot (Z −0.10, Y 0) rising and leaning BACK to the backrest top (Z −0.45, Y 0.90), X = ±0.26 | 0 | static |
| Armrest rails (2) | 0.05 × 0.06, sloping from the front leg top (Z +0.40, Y 0.55) to the back rail (Z −0.30, Y 0.62) | 0 | static |
| Cross-bars (3) | Square 0.05 rods across X (0.52 long): foot bar between the back rail feet (Z −0.10, Y 0.04), middle bar (Z −0.28, Y 0.55), top bar (Z −0.45, Y 0.85); the foot bar is dark | 0; foot bar 1 dark wood | static |
| Cloth | A sling from the top bar (Y 0.85) down to a front bar at the armrest joints (Z +0.40, Y 0.45), sagging 0.06 in the middle; width 0.50; 6-8 segments along the length; solid shell, 0.025 thick; 5 lengthwise stripes of 0.10 each, one flat palette cell per stripe | 5 red, 3 cream, alternating R-C-R-C-R (`_Blue`: 15 instead of 5) | static |

Axes/pivots: rails and cloth joints must touch: the cloth ends rest on the bars (wrapped around, no gaps).

## Anchor

Within this pack: FUR-02 (faceted striped sag cloth; same stripe wording; FUR-02 uses cream/blue). Earlier packs: none for this object.

## What NOT to do

- Do not make it a folded or flat chair; unfolded and leaning.
- No flat card for the cloth: a thick shell with a hem; no noise on stripes.
- Frame wood must not go thinner than 0.05; do not use metal.
- No cushion, no footrest, no canopy, no armchair box shape.
- Cloth and bars must touch; no floating parts; no coplanar overlaps.
- Do not exceed 400 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
