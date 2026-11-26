# TOP-02 Topiary Cone — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/TOP-02.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Pure geometry (topiary rule: clean shape, ±0.02 vertex jitter). Soil disc and stem as in TOP-01 (shared wording).

## Catalogue

TOP-02 Топиарий «конус» `FMS_Garden_Topiary_Cone` — sharp geometric cone, 10–12 faces, short stem. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.7×0.7×1.6 | 300 | no | no | none |

Estimate: cone 12 sides × 3 rings = 12×(2+2+1) = 60 tris + base cap 12 + stem 32 + soil disc 36 → about 140; room left, do NOT spend it on tiers.

## Parts

Axes: Y up. Pivot at the centre of the soil disc bottom on the ground (0, 0, 0). Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Soil disc | SOIL DISC (shared wording, see TOP-01): 12-sided flat cylinder Ø0.50, 0.04 tall, 36 tris | 12 soil `#805433` | none |
| Stem | STEM (as TOP-01): 8-sided prism, Ø0.07 → Ø0.06, Y 0.04–0.30 (runs 0.08 into the cone), 32 tris | 13 bark `#7A5233` | none |
| Cone | 12-sided cone, base ring Ø0.70 at Y 0.20, apex Y 1.60 (height 1.40), base closed with a 12-tri cap (visible from below), 3 vertical rings (at Y 0.20, 0.62, 1.04) so the faces can be jittered: ring vertices displaced ±0.02 radially (fixed seed), apex ±0.01. Faces straight and planar-looking, 12 clear faces visible around; no tiers, no needles, no steps. Colour: every 3rd vertical face column slot 2, the others slot 3 (regular alternation) | 3 boxwood `#3F6B3A`, 2 `#4E7A3A` | none |

## Anchor

Closest approved model: none in this pack yet (shares soil disc/stem wording with TOP-01). By name only (preview not in this branch): Farm Nature `FMS_Tree_Spruce_S` — the shape to differ from (tiered conifer, 2×2×3.5), `FMS_Hedge_Straight` for the clipped-green look.

## What NOT to do

- No tiers, branches or needles like Farm Nature `FMS_Tree_Spruce_S`; the cone is smooth-sided, 12 clean faces.
- No smooth cone: flat shading, visible facets, no subdivision surface, no smoothed normals.
- No round bush, no hedge cube, no leaves or alpha cards.
- Do not stand the cone on the ground: 0.2 m of bare stem is visible under it; do not omit the soil disc.
- No stem thicker than Ø0.08; no coplanar overlaps (stem inside cone is OK, ends hidden).
- Do not exceed 300 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
