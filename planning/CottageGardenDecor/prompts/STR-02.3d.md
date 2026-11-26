# STR-02 Arch_Iron — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/STR-02.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

Line: STR-02 · Wrought-iron arch · `FMS_Garden_Arch_Iron` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.4×0.5×2.5 | 1400 (scrolls allow up to ~2× with a note in the builder notes; target ≤ 1400) | no | no | — |

Opening 1.2 wide. It must fit the 1.5 m gap of a stone wall (MOD-03/04, CMP-05).

## Parts

Pivot: centre of the footprint on the ground (Y = 0).

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Uprights (4) | Wrought-iron rods: 8-sided rod about 0.035 m across (≥ 0.03), vertical at X = ±0.60, Z = ±0.20 (centres), Y 0.08 → 1.90; below each upright a short 8-sided pointed cone foot Y 0 → 0.08 (nothing goes below Y = 0) | 13 wrought iron | static |
| Hoops (2) | Half-round rod arch, centre (0, 1.90), radius 0.60 (centre-line), 12 segments from X −0.60 to +0.60, in two flat frames at Z = ±0.20; crown top = 2.50 incl. rod thickness | 13 | static |
| Cross-rods | 3 short rods across Z (0.40 long) at the crown and at ±45° on the hoop; 2 spreader rods across Z near the ground (Y 0.20) at X = ±0.60 | 13 | static |
| Side scrolls (4) | Wrought-iron scrolls (shared construction): rod of 8-sided cross-section, about 0.035 m across, bent into open S-shaped scrolls with rounded curls (each curl at least 0.10 m across). One large S per upright on the outer side, reaching X = ±0.70 (total width 1.4), mirrored; 6-8 segments per curve | 13 | static |
| Corner scrolls (4) | Smaller S-scrolls (curl ≥ 0.10) between upright and hoop at Y ≈ 1.6-1.9 inside each frame | 13 | static |
| Finial | Short upright rod with a small 8-sided cone tip on the hoop crown, +0.0 to the height limit (stay inside 2.5) | 13 | static |

Everything is one palette slot; mixing slots 7/8 for "highlights" is not allowed.

## Anchor

Within this pack: this is the anchor for the iron wording of FUR-03 and FUR-04 (same rod section 8-sided ~0.035, same S-scroll wording, same slot 13). Earlier packs: none (iron is new); thickness style only from Farm Yard `FMS_Fence_Picket` (превью нет в ветке).

## What NOT to do

- No rods thinner than 0.03; no round-section or smooth-shaded rods (8-sided, flat shaded).
- No wood or lattice; the rods are the only material, one slot (#3A3A3F).
- Keep the open passage 1.2 m wide; scrolls must not intrude into it.
- No dense decorative filigree finer than 0.03 m; curls < 0.10 across merge into blobs at 10 m.
- No floating scrolls: every scroll touches an upright or the hoop. No coplanar overlapping faces.
- Do not add a gate, a base plate, plants or a ground plane.
- Do not exceed the budget by more than the allowed ~2× for scrolls; note it if you do.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
