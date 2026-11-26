# TOP-04 Topiary Tiered (three balls) — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/TOP-04.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Pure geometry (topiary rule: clean shape, ±0.02 vertex jitter). Soil disc and stem as in TOP-01 (shared wording).

## Catalogue

TOP-04 Топиарий «три шара» `FMS_Garden_Topiary_Tiered` — three decreasing balls on one stem. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.7×0.7×1.7 | 600 | no | no | none |

Estimate: bottom ball 320 + middle 80 + top 80 + stem 32 + soil disc 36 → about 550.

## Parts

Axes: Y up. Pivot at the centre of the soil disc bottom on the ground (0, 0, 0). Root scale 1, rotation 0. All three ball centres on the Y axis.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Soil disc | SOIL DISC (shared wording, see TOP-01): 12-sided flat cylinder Ø0.50, 0.04 tall, 36 tris | 12 soil `#805433` | none |
| Stem | STEM (as TOP-01): 8-sided prism, Ø0.07, Y 0.04–0.40 (ends inside the bottom ball), 32 tris. Visible bare length 0.25 under the bottom ball | 13 bark `#7A5233` | none |
| Ball 1 (bottom) | Icosphere subdivision 2 (320 tris), Ø0.70, centre Y 0.60 (0.25–0.95); vertices ±0.02 jitter | 3 boxwood `#3F6B3A`, ~25% facets 2 | none |
| Ball 2 (middle) | Icosphere subdivision 1 (80 tris), Ø0.50, centre Y 1.15 (0.90–1.40), penetrates ball 1 by 0.05 so the stack is one solid mass | 3, ~25% facets 2 | none |
| Ball 3 (top) | Icosphere subdivision 1 (80 tris), Ø0.32, centre Y 1.54 (1.38–1.70), penetrates ball 2 by 0.02 | 3, ~25% facets 2 | none |

Top Y = 1.70 exactly. Facet colouring: 2 alternating facets per ~4, regular pattern by face index (no noise). Subdivision-1 facets on the upper balls have edges ≈ 0.15, comparable to the bottom ball (subdiv 2, ≈ 0.12).

## Anchor

Closest approved model: TOP-01 `FMS_Garden_Topiary_Standard` (same pack: soil disc, stem, ball wording; not yet built at the time of writing). By name only (preview not in this branch): Farm Nature `FMS_Bush_Round` — the shape to differ from.

## What NOT to do

- NO ball sitting on the ground like Farm Nature `FMS_Bush_Round`; the bottom ball is lifted 0.25 on a visible stem.
- No smooth spheres: ico faces must be visible, flat shading, no subdivision surface, no smooth normals.
- Balls decrease strictly (0.70 / 0.50 / 0.32) and stack touching/overlapping — no gaps showing the stem between balls, no floating ball.
- No leaves, flowers, alpha cards; no tiered conifer look; no hedge.
- Do not omit the soil disc; no coplanar overlaps; do not exceed 600 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
