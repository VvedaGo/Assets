# WTR-01 Tiered Fountain — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/WTR-01.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: WTR-01 Фонтан ярусный `FMS_Garden_Fountain_Tiered`, atlas A `Garden_Build`, material `M_Garden_Build`. Silhouette difference from duplicates (Farm Yard `FMS_Well`, `FMS_Trough_Water`): wide stone basin with stacked bowls and a pine-cone finial; no well shaft, no roof, no crank.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.4×2.4×1.9 | 2800 | yes: LOD1 by `make_lod1.py` (50% per part, palette recalculated), not Unity auto LOD | no | none |

Static, no moving parts. Pivot: centre of the basin on the ground (Y = 0), root scale 1, rotation 0, Y up. Basin 12 segments, bowls 12, baluster 12, finial 8; all rings share the same angles, first vertex on +X.

Shared wording, stone: pale limestone main `#C9C3B6` (slot 11), warm grey stone `#A7A39A` (slot 12) as second tone for plinths and inner faces only; chunky faceted forms, flat shading, bevel 0.01–0.02 on large edges only, none on small parts; no cracks, moss, carving or text.
Shared wording, water: opaque flat blue `#4A78A8` (slot 15); plain flat disc, no transparency, no ripples, splashes, droplets or foam; no separate material.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Basin floor | 12-gon disc Ø2.4 at Y 0.05, thickness 0.05 (~50) | 12 stone | static |
| Basin wall | 12-sided ring wall: outer Ø2.4, inner Ø2.04 (thickness 0.18), Y 0–0.45; outer face slot 11, inner face slot 12 (~170) | 11 outer, 12 inner | static |
| Basin coping | flat thick ring on the wall, Y 0.45–0.50, Ø2.4 → Ø1.96 (inner overhang 0.04), edge chamfer 0.015 (~120) | 11 | static |
| Basin water | flat 12-gon disc Ø2.0 at Y 0.40, edge exactly on the inner wall (12 tris) | 15 water | static |
| Foot block | 12-sided prism Ø0.8, Y 0.05–0.30 (~50) | 12 | static |
| Lower pedestal | turned baluster Ø0.55 at Y 0.30 → waist Ø0.30 at Y 0.55 → Ø0.5 at Y 0.75 (collar), ~5 rings (~140) | 11 | static |
| Lower bowl | shallow thick-lipped bowl, outer from Ø0.5 at Y 0.75 out to Ø1.3 at Y 0.92, rim wall Y 0.92–0.97, rim ring Ø1.3 → 1.14, inner slope down to Ø0.6 at Y 0.86 (~250) | 11 outer, 12 inner slope | static |
| Lower bowl water | flat 12-gon disc Ø1.12 at Y 0.93 (12) | 15 | static |
| Upper neck | baluster Ø0.28 at Y 0.86 → waist Ø0.2 at Y 1.10 → Ø0.34 at Y 1.28 (~100) | 11 | static |
| Upper bowl | shallow bowl, outer Ø0.34 at Y 1.28 → Ø0.7 at Y 1.38, rim wall Y 1.38–1.42, rim ring Ø0.7 → 0.56, inner slope to Ø0.3 at Y 1.34 (~200) | 11 outer, 12 inner | static |
| Upper bowl water | flat 12-gon disc Ø0.56 at Y 1.40 (12) | 15 | static |
| Finial stem | prism Ø0.12, Y 1.38–1.58 (8 sides, ~20) | 11 | static |
| Finial cone | pine-cone: stacked 8-sided frustums/cone with 3 stepped tiers, Y 1.58–1.90, max Ø0.3 (~120) | 11, tier edges 12 | static |
| Streams, upper bowl | 8 flat ribbons (0.05 wide, 0.02 thick) hanging from the upper rim, Y 1.40 → 0.93, 2 segments each, slightly flared at the top, ends touch the lower water disc (~130) | 15, one face row in 9 `#A9AFB4` | static |
| Streams, lower bowl | 8 flat ribbons from the lower rim, Y 0.95 → 0.40, offset 22.5° from the upper streams, ends touch the basin water (~170) | 15, one face row in 9 | static |

Budget: rough sum ~1700 tris, up to 2800 allowed; spend the rest on cleaner ring segmentation, not on detail below 0.03 m. Water ribbons never pass through bowls: they start outside the rim edge and end exactly on the water disc below.

## Anchor

Closest approved model: WTR-03 (this pack, pilot, preview/spec not yet approved) for stone wording, 10-12 facets and palette A. Earlier packs by name only: Farm Yard `FMS_Well` (stone scale), превью нет в ветке.

## What NOT to do

- No splashes, spray, droplets, foam or particles; no transparent or wavy water; no separate water material.
- No thin pencil jets: ribbons are ≥ 0.05 wide, stiff, straight.
- No well shaft, roof, crank, bucket, statue, fish or coins.
- No pedestal thinner than Ø0.2; no bowls floating above the stem; every tier rests on the one below.
- No sphere-smoothing of the pine cone: faceted tiers, 8 segments.
- No coplanar overlap between water discs and rim rings; water top stays below the rim top (basin 0.10, lower bowl 0.04, upper bowl 0.02).
- No smoothed normals; do not exceed 2800 tris; LOD1 keeps the ribbons and the silhouette of three discs.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
