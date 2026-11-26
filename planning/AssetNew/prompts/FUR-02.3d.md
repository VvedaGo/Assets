# FUR-02 Hammock — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/FUR-02.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: FUR-02 · Hammock on a stand · `FMS_Garden_Hammock` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.2×1.1×1.1 | 1000 | no | no | — (static, no moving parts) |

## Parts

Pivot: centre of the footprint on the ground (Y = 0), X = along the hammock. Assumed construction (catalogue says only "arched wooden stand, sagging striped cloth"): a bowed beam under the cloth plus two end posts with hooks.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Bowed beam | Wooden post section 0.12 (Z) × 0.14 (Y), along X at Z = 0, a polyline of 10-12 straight segments forming a U-arc: centre-line Y 0.93 at the ends (X = ±1.45) falling to Y 0.25 at X = 0 (beam top 0.32 there) | 0 light wood | static |
| End posts (2) | Wooden posts (shared construction): 0.12 × 0.12, vertical at X = ±1.45, Y 0 → 1.00, joined to the beam ends | 0 | static |
| Cross-feet (2) | 0.12 × 0.12 × 0.90 across Z at X = ±1.45, Y 0 → 0.12 (the post stands in the middle; the beam also touches the ground nowhere else) | 0 | static |
| Hook rings (2) | Wrought-iron: 8-sided rod about 0.035 thick bent into an open ring ≈ Ø0.12 at the post tops, Y 1.00 → 1.10 | 13 wrought iron | static |
| Cords (2 × 2) | 4 short straight rods (0.04 square, cream dark) from the cloth ends to the hook rings | 4 dark cream | static |
| Hammock cloth | A sagging sling over X ±1.30: cloth top 0.62 at X = 0 (bottom 0.59), rising to the hooks at Y 1.00, width 0.9 at the middle, gathered to 0.14 at both ends; 10-12 segments along X, 5 stripes across Z (faces coloured per stripe, one palette cell each); cloth thickness 0.03 solid (two-sided closed shell, not a card) | 3 cream and 15 water blue, alternating, centre stripe cream | static |

Do not put the cloth on top of the bowed beam: the beam top at X = 0 (0.32) is about 0.27 below the cloth bottom (0.59).

## Anchor

Within this pack: FUR-05 (same cloth idea: faceted sag, alternating stripes; share the stripe wording) — FUR-05 is written in this batch. Earlier packs: none for this object. Colour note: stripes here are cream/blue (distinguishes it from the red-cream FUR-05).

## What NOT to do

- No smooth curve: the arc and the sag are straight-segment polylines (flat shading).
- Do not leave the cloth as a single-sided plane: it is a closed shell of ≥ 0.03 thickness.
- No cushion, pillow, fringe, tassels, blanket; no tree-hook trees, no ground plate.
- The beam, posts and cloth must not collide; no floating cords.
- No stripe noise: five clean lengthwise stripes, one flat colour each.
- Do not exceed 1000 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
