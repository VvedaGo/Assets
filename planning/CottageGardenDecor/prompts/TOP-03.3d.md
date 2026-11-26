# TOP-03 Topiary Spiral — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/TOP-03.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Pure geometry (topiary rule: clean shape, ±0.02 vertex jitter). Soil disc and stem as in TOP-01 (shared wording).

## Catalogue

TOP-03 Топиарий «спираль» `FMS_Garden_Topiary_Spiral` — spiral of 3.5 turns around a cone, gap down to the trunk. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.7×0.7×1.8 | 900 | no | no | none |

Estimate: band 56 segments × 4 sides × 2 = 448 + end caps 8 + trunk 8-sided 3 segments ~50 + soil disc 36 → about 550.

## Parts

Axes: Y up. Pivot at the centre of the soil disc bottom on the ground (0, 0, 0). Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Soil disc | SOIL DISC (shared wording, see TOP-01): 12-sided flat cylinder Ø0.50, 0.04 tall, 36 tris | 12 soil `#805433` | none |
| Trunk | 8-sided prism, Ø0.10 at the base → Ø0.07 at Y 1.75, 3 segments (~48 tris), Y 0.04–1.75, with a 8-tri pointed tip cone to Y 1.80 (also ends inside the top turn). Bare visible 0.25 m at the bottom and in the gaps between turns | 13 bark `#7A5233` | none |
| Spiral band | One continuous helical ribbon swept along a helix of exactly 3.5 turns, 16 segments per turn (56 segments), starting at Y 0.25 and ending at Y 1.78 (vertical pitch ≈ 0.40 per turn). Cross-section a 4-sided trapezoid: inner edge on the trunk surface (r = 0.05 → 0.035, glued to the trunk), outer edge at radius R(y) falling linearly 0.35 at the start → 0.04 at the tip (silhouette = cone Ø0.7 → point), band height 0.20 at the outer edge, 0.12 at the inner edge (so the band is a shallow wedge and a gap of ≈ 0.20 remains between turns at the outer edge, ≈ 0.28 at the inner). Each segment 8 tris (4 sides × 2), both ends closed (4 tris each). All vertices jittered ±0.02 (fixed seed). Colour: upper faces of the trapezoid slot 3, outer and lower faces alternate by segment between slot 3 and slot 2 (lower faces slot 2) | 3 boxwood `#3F6B3A`, 2 `#4E7A3A` | none |

Checks: turns count = 3.5 (printed), through every gap the trunk is visible from the front view, silhouette fits 0.7×0.7×1.8, no segment self-intersects or leaves a gap > 1 mm between consecutive segments (shared vertices).

## Anchor

Closest approved model: none in this pack yet (shares soil disc/stem wording with TOP-01). By name only (preview not in this branch): Farm Nature `FMS_Tree_Spruce_S` — avoid its tiered silhouette; `FMS_Hedge_Straight` for the clipped-green look.

## What NOT to do

- Not a solid cone with a groove painted on: the gaps between turns are REAL openings down to the trunk.
- No smooth tube/rope: the ribbon is a faceted wedge with 16 segments per turn and visible flat faces; flat shading, no subdivision.
- No leaves, needles, alpha cards or flowers; no tiers.
- Not 3 or 4 turns — exactly 3.5; no thin ribbon (< 0.12 tall).
- Do not omit the soil disc or the 0.25 m bare trunk at the bottom; do not float the band off the trunk.
- No coplanar overlaps; do not exceed 900 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
