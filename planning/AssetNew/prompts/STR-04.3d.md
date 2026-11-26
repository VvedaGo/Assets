# STR-04 Pergola — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/STR-04.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

Line: STR-04 · Pergola 3×3 · `FMS_Garden_Pergola` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.5×3.5×2.62 | 1600 | yes (LOD1, `make_lod1.py`) | no | — |

SNAP with STR-05 (pergola bay): see the contract below.

## Parts

Pivot: centre of the footprint on the ground (Y = 0), X along the beams, Z along the rafters.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Posts (4) | Wooden posts (shared construction): square 0.16×0.16, centres at (±1.5, ±1.5), Y 0 → 2.24 (reach the beam underside), 0.01 bevel on long edges | 0 light wood | static |
| Main beams (2) | Along X at Z = ±1.5, section 0.10 (Z) × 0.22 (Y), Y 2.24 → 2.46, X from −1.75 to +1.75 (overhang 0.25 past the post centres) | 0 | static |
| Rafters (7) | Along Z at X = −1.5, −1.0, −0.5, 0, 0.5, 1.0, 1.5, section 0.06 (X) × 0.16 (Y), Y 2.46 → 2.62, Z from −1.75 to +1.75 (overhang 0.25). Decorative end: a stepped-point cut (two chamfer steps, a flat angled notch, 3-4 extra triangles per end); end faces in the dark slot | 0; cut end faces 1 dark wood | static |

Rafters must not coincide in plane with the beam top (beam top 2.46 = rafter bottom: share the edge, no overlapped coplanar faces).

SNAP contract (pergola, 3.0 m step along +X): the +X post line is at X = +1.5; STR-05 pivot = STR-04 pivot + (1.5, 0, 0). STR-04 beams end at X = 1.75; STR-05 beams begin at its X = 0.25 (world 1.75) — butt joint with zero gap. The last STR-04 rafter is at X = +1.5; STR-05 rafters start at its X = 0.5 (world 2.0), so rafter spacing 0.5 stays continuous and no rafter is duplicated on the shared post line. The assembly script must print `SNAP OK` for the pair.

## Anchor

Within this pack: none (STR-04 is the first pergola); STR-05 is built from the same script and parts. Earlier packs: Farm Market `FMS_Stall_Canopy` (the cloth canopy; this model differs: bare rafters, no cloth) — превью нет в ветке; wood thickness reference Farm Yard `FMS_Fence_Picket` (превью нет в ветке).

## What NOT to do

- No cloth, no canopy, no table or counter (that would make it a Farm Market stall). The roof is open rafters only.
- No lattice, no cross-bracing between posts, no ground plate, no plants.
- Do not make rafters thinner than 0.06 × 0.16 or posts thinner than 0.16.
- Do not move the beam underside from 2.24 or the rafter top from 2.62 (plants hang at 2.24 and rest at 2.46).
- No overlapped coplanar faces at beam/rafter contacts; no floating rafters (each rests on both beams).
- Do not decorate the beams with carving finer than 0.03.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
