# FUR-04 Bistro_Chair — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/FUR-04.png  (selected 2026-11-26, Э6 batch 4)

## Catalogue

Line: FUR-04 · Wrought-iron bistro chair · `FMS_Garden_Bistro_Chair` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.45×0.5×0.85 | 700 | no | no | `_White` (colour: same mesh, UV to slot 10 white paint; separate FBX and prefab) |

## Parts

Pivot: centre of the footprint on the ground (Y = 0). Front of the chair = +Z; the back hoop on −Z.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Seat disc | 10-sided cylinder Ø0.40, Y 0.41 → 0.45 (top at 0.45), centred at Z = 0.02 | 13 wrought iron (`_White`: 10) | static |
| Legs (4) | Wrought-iron rods: 8-sided, about 0.035 across (≥ 0.03); from under the seat edge at r 0.15 down to the floor, splayed to r 0.20 at Y = 0; the footprint stays inside 0.45 × 0.5 | 13 (`_White`: 10) | static |
| Ring brace | 8-sided rod ring Ø0.30 at Y 0.20, joining the legs | 13 (`_White`: 10) | static |
| Back hoop | One half-round hoop of the same rod, 10 segments, rising from the back edge of the seat (Z ≈ −0.20) over 0.40 width to a top at Y 0.85; slightly bowed back (top 0.06 behind the seat edge) | 13 (`_White`: 10) | static |
| Back scroll | Wrought-iron scrolls (shared construction): rod of 8-sided cross-section, about 0.035 m across, one large open S-scroll (curl ≥ 0.10 across) in the middle of the hoop, touching the hoop at both ends | 13 (`_White`: 10) | static |
| Hoop links (2) | Two short rods joining the hoop ends to the seat edge | 13 (`_White`: 10) | static |

Same iron wording and rod section as FUR-03 and STR-02; the series must look like one set of furniture.

## Anchor

Within this pack: FUR-03 (same rod, same slot, same S-scroll); STR-02 (iron anchor). Earlier packs by name: Farm Market `FMS_Deco_Table_Set` (plank benches; this model is a round-seat iron chair) — превью нет в ветке.

## What NOT to do

- No wood, cushion or armrests; iron only, one slot.
- No rods thinner than 0.03; no spindly filigree smaller than a 0.10 curl.
- Seat disc on legs: every leg touches the seat and Y = 0; the hoop touches the seat; no floating scrolls.
- Do not make the back rectangular or a flat panel; it is an open hoop with an S-scroll.
- No glossy metal; `_White` uses only slot 10.
- Do not exceed 700 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Orchestrator note (2026-11-25, budget)
- Tris budget raised to 1400 (was 700): iron rods 6-sided (>= 0.03), curls >= 0.10 across and round at 128 px, as for STR-02. This overrides "do not exceed" lines above.
