# FUR-01 Swing — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/FUR-01.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: FUR-01 · Garden swing, A-frame · `FMS_Garden_Swing` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.4×1.5×2.1 | 1600 | yes (LOD1, `make_lod1.py`; `Seat` stays a separate node) | no | — |

## Parts

Pivot of the model: centre of the footprint on the ground (Y = 0). X = along the top beam, Z = front-back.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| A-frame legs (4) | Wooden posts (shared construction): square 0.12×0.12; per end frame one leg leaning from the foot at Z = ±0.75 up to the apex at Z = 0, Y 2.04; ends at X = ±1.10 (frame plane YZ); 8-12 tris per leg | 0 light wood | static |
| Top beam | Wooden post, 0.12×0.12 along X, X ±1.20, centre axis Y 2.04 (top at 2.10) | 0 | static |
| Cross-braces (2) | One per A-frame at Y 0.45, 0.10×0.10, spanning the legs at the frame plane | 1 dark wood | static |
| Hanger rods (4) | Wrought-iron rods: 8-sided, about 0.035 m across (≥ 0.03). Two per bench end, forming a narrow V in the YZ plane at X = ±0.80: from the top beam axis point (±0.80, 2.04, 0) down to the front and rear seat corners (±0.80, 0.50, ±0.22). No chain links | 13 wrought iron | part of `Seat` |
| Seat bench | Plank seat 1.6 × 0.45 × 0.05 at Y 0.45, backrest 1.6 × 0.40 × 0.04 leaning back 10°, two armrests, two side frames 0.06 thick; all chunky, flat faces | 0 | child of `Seat` |
| Cushion | Slightly rounded box 1.4 × 0.40 × 0.08 on the seat | 3 cream | child of `Seat` |

Note on hangers: the catalogue says "4 hangers"; assumed 2 per bench end (V-shape above), so the seat keeps its Z position while swinging about the beam axis. The preview shows four straight rods; the V of 0.44 m at the bottom is acceptable.

**Moving part `Seat`** (Unity child node `Seat`): includes the bench, cushion and 4 hangers. Pivot on the AXIS of the top beam: (0, 2.04, 0), rotation axis X, rest 0°, travel ±30°. Hanger top ends must lie exactly on that axis. The seat must clear the A-frame legs and the ground over the whole ±30° range (seat at least 0.15 m from the legs at rest; at +30° the seat bottom is above the ground, since the arm length ≈ 1.55 m).

## Anchor

Within this pack: none (the first wooden frame furniture); wording for the posts is shared with STR-01 and STR-04. Earlier packs by name: Farm Market `FMS_Deco_Bench_Plank` (wood thickness only) — превью нет в ветке.

## What NOT to do

- No chain links (rods only), no rope; no canopy or roof.
- The seat does not touch the legs or the ground; hangers do not pass through the backrest or cushion.
- No thin legs (< 0.10); no ground plate.
- `Seat` must be a separate named node with its pivot on the beam axis; do not merge it into the frame.
- No coplanar overlapping faces where hangers meet the beam (offset ≥ 1 mm); no floating cushion.
- Do not exceed 1600 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
