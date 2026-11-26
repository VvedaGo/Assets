# STR-03 Arbor_Bench — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/STR-03.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

Line: STR-03 · Arbor with bench · `FMS_Garden_Arbor_Bench` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.8×0.8×2.3 | 1600 | yes (LOD1, `make_lod1.py`) | no | — |

The arbor is closed on the sides and back, open at the front; inner clear width 1.5 m for the 2-seat bench (the 1.2 m opening of the other arches does not apply here).

## Parts

Pivot: centre of the footprint on the ground (Y = 0). Front = +Z, back wall at Z = −0.34.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Posts (4) | Wooden posts (shared construction): 0.12×0.12, X = ±0.84, Z = ±0.34 centres, Y 0 → 1.95, faceted, 0.01 bevel on long edges | 10 white paint | static |
| Side lattice panels (2) | In the YZ plane at X = ±0.84, between front and rear post, Y 0.15 → 1.95, depth 0.56. Lattice (shared construction): diagonal slats crossing at 45°, about 0.03 m square, real open gaps of about 0.10 m between the slats, closed by a flat frame rim about 0.05 m wide | 10 | static |
| Back lattice panel | Same lattice, in the XZ plane at Z = −0.34, between the rear posts, X ±0.78, Y 0.45 → 1.95 (starts at the seat so the bench back is lattice) | 10 | static |
| Seat | Plank board 1.5 × 0.45 × 0.05, top at Y 0.45, front edge Z +0.30; two plank splits optional (0.01 gap not needed) | 0 light wood | static |
| Seat supports | 2 side supports 0.06 wide × 0.40 high under the seat at X = ±0.62, a front rail 1.5 × 0.06 × 0.10 at Z +0.28 under the seat edge | 10 white | static |
| Arch rafters (2) | Curved half-arch beams, thick 0.10 × 0.10, front (Z +0.34) and rear (Z −0.34): spring from the post tops (Y 1.95) rising over a span of 1.8 to the crown at Y 2.30 (outer top), 8 segments, straight-segment polyline with flat faces | 10 | static |
| Cross slats (5) | 0.06 × 0.06 slats along Z linking front and rear rafters at X = −0.72, −0.36, 0, +0.36, +0.72 (sitting on the rafter curve), length 0.68 | 10 | static |
| Empties `Plant_L`, `Plant_R`, `Plant_Top` | `Plant_L` (−0.84, 0, 0), `Plant_R` (+0.84, 0, 0) at the middle of the side panels on the outer face; `Plant_Top` (0, 2.30, 0) | — | for compositions |

## Anchor

Within this pack: STR-01 (lattice construction, post wording identical; STR-01 is written in this same batch). Earlier packs: Farm Market `FMS_Deco_Bench_Plank` (a free-standing plank bench — this model must differ: the bench is built into the arch) — превью нет в ветке.

## What NOT to do

- Do not make a free-standing bench with a frame around it: the bench is attached to the posts and lattice; the lattice back starts at seat height.
- Do not draw the lattice as a flat solid panel; real open gaps edge to edge, ending in the rim.
- Do not leave the seat floating: it rests on its supports at 0.45, supports touch the ground and posts.
- No cushions, no plants, no ground plate, no arrow-slit roofing; the arch is open with cross slats.
- No thin posts (< 0.10); coplanar faces between lattice rim and posts offset ≥ 1 mm.
- Do not exceed 1600 tris without noting (lattice may go up to ~2×).

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
