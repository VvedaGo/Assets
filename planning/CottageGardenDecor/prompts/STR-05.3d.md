# STR-05 Pergola_Bay — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/STR-05.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

Line: STR-05 · Pergola, 3 m extension bay · `FMS_Garden_Pergola_Bay` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.25×3.5×2.62 (X 0.25 → 3.25 of beams, Z ±1.75) | 1000 | yes (LOD1, `make_lod1.py`) | no | — |

## Parts

Pivot: the middle of the shared post line at ground level, i.e. X = 0 of the section = the +X post line of the previous part; Z = 0; Y = 0. Section coordinates below.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Posts (2) | Wooden posts (shared construction): square 0.16×0.16, centres at (3.0, ±1.5), Y 0 → 2.24, 0.01 bevel on long edges (identical to STR-04) | 0 light wood | static |
| Main beams (2) | Along X at Z = ±1.5, section 0.10 × 0.22, Y 2.24 → 2.46, X from 0.25 to 3.25 (starts exactly where the previous beam's 0.25 overhang ends: butt joint, zero gap, no overlap) | 0 | static |
| Rafters (6) | Along Z at X = 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, section 0.06 × 0.16, Y 2.46 → 2.62, Z ±1.75; stepped-point end cut, end faces dark (identical to STR-04) | 0; end faces 1 dark wood | static |

SNAP contract: placement = STR-04 pivot + (1.5, 0, 0); the next STR-05 = previous + (3.0, 0, 0). Beam joint at X = 0.25 (zero gap), rafter pitch 0.5 continuous (previous part has the last rafter at its +1.5 = the section X = 0), no rafter duplicated on the shared line. The beam end at X = 3.25 gets the normal 0.25 overhang, which the next bay butts against at its X = 0.25. The assembly script must print `SNAP OK` for pairs STR-04 + STR-05 and STR-05 + STR-05.

## Anchor

Within this pack: STR-04 (same parts and wording; build both with one script). Earlier packs: Farm Market `FMS_Stall_Canopy` (cloth canopy; this model has none) — превью нет в ветке.

## What NOT to do

- No posts at the joining end (X = 0), no end rafter at X = 0: the neighbour owns that line.
- Do not overlap beams with the neighbour (no coplanar overlapping faces); the joint is a flush butt.
- No cloth, table, counter, lattice, plants, ground plate.
- Do not change the section dimensions or the end cut from STR-04.
- No floating rafters; each rests on both beams.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
