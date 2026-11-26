# FUR-03 Bistro_Table — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/FUR-03.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: FUR-03 · Wrought-iron bistro table · `FMS_Garden_Bistro_Table` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.7×0.7×0.75 | 500 | no | no | `_White` (colour: same mesh, UV to slot 10 white paint; separate FBX and prefab) |

## Parts

Pivot: centre of the footprint on the ground (Y = 0).

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Top disc | 12-sided cylinder Ø0.70, Y 0.70 → 0.74; plus a rim ring 0.03 wide × 0.03 high on the edge (top at 0.75 total height) | 13 wrought iron (`_White`: 10) | static |
| Underside ring | 12-sided ring Ø0.40, 0.04 high, under the top at Y 0.66 → 0.70, carries the leg tops | 13 (`_White`: 10) | static |
| Legs (3) | Wrought-iron rods: 8-sided, about 0.035 across (≥ 0.03); three legs 120° apart, each an S-shaped 5-6 segment path from the hub (r 0.05, Y 0.62) out to the ground at r ≈ 0.28, Y 0; ends in a small curled foot (a curl ≥ 0.10 across) | 13 (`_White`: 10) | static |
| Hub | 8-sided small cylinder Ø0.10 × 0.10 at Y 0.58 → 0.68 joining the legs | 13 (`_White`: 10) | static |
| Link scrolls (3) | Wrought-iron scrolls (shared construction): rod of 8-sided cross-section, about 0.035 m across, S-shaped, from the hub to the underside ring, between the legs; curl ≥ 0.10 across | 13 (`_White`: 10) | static |

Feet must touch Y = 0; the stable footprint inside 0.7×0.7.

## Anchor

Within this pack: STR-02 (the iron: same rod section, same S-scroll wording, same slot 13); FUR-04 uses the same hardware. Earlier packs by name: Farm Market `FMS_Deco_Table_Set` and `FMS_Deco_Table_Plank` (plank picnic tables; this model must differ by being a round iron tripod) — превью нет в ветке.

## What NOT to do

- No wooden parts, no tablecloth, no props on the table.
- No rods thinner than 0.03 (the real rod is thinner; it is enlarged on purpose).
- Do not make it rectangular, do not use 4 square legs; it is a 3-leg S-curved tripod.
- Legs and scrolls must touch their supports (hub, ring, floor), no floating curls.
- No glossy metal: matte, one slot; `_White` uses slot 10 only.
- Do not exceed 500 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Orchestrator note (2026-11-25, budget)
- Tris budget raised to 1000 (was 500): iron rods 6-sided (>= 0.03), curls >= 0.10 across and round at 128 px, as for STR-02. This overrides "do not exceed" lines above.
