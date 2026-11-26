# TOP-01 Topiary Standard (ball on a stem) — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/TOP-01.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Pure geometry (STYLE: topiaries are clean shapes with ±0.02 vertex jitter). Helpers shared with TOP-02/03/04: the soil disc and the stem; for `_Rose` the rose bloom of PLT-01.

## Catalogue

TOP-01 Топиарий «шар на штамбе» `FMS_Garden_Topiary_Standard` — faceted ball Ø0.6 on a bare stem 0.8, soil disc; planted in the ground or a bed. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.6×1.4 | 500 (`_Rose` 800) | no | no | 1 mesh: `_Rose` (standard rose: the ball carries 10 rose blooms; separate FBX + prefab) |

Estimate base: ball 320 + stem 32 + soil disc 36 → about 390. `_Rose`: +10 blooms × 34 = 340 → about 730.

## Parts

Axes: X, Z footprint, Y up. Pivot at the centre of the soil disc bottom on the ground (0, 0, 0). Root scale 1, rotation 0. Ball centre at Y = 1.10, its bottom at 0.80, top at 1.40 (total 1.4).

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Soil disc | SOIL DISC (shared wording TOP-01…04): 12-sided flat cylinder, Ø0.50, height 0.04 (Y 0–0.04), flat shading, 36 tris | 12 soil `#805433` | none |
| Stem | STEM: 8-sided prism, Ø0.07 at the base → Ø0.06 at the top, Y 0.04–0.88 (runs 0.08 into the ball for a solid join), 2 segments, no caps at the ground; 32 tris. Straight, no bend | 13 bark `#7A5233` | none |
| Ball | Icosphere subdivision 2 (320 tris), radius 0.30, centre (0, 1.10, 0). Each vertex displaced radially by ±0.02 (fixed seed) for a hand-clipped look; flat shading. Face colour alternates between slot 3 (main, about 75%) and slot 2 (about 25%, scattered by face index pattern, no noise texture) | 3 boxwood `#3F6B3A`, 2 `#4E7A3A` | none |
| Blooms ×10 (`_Rose` only) | ROSE BLOOM (shared wording, see below), outer rim Ø0.09, set flush on the ball surface: each bloom's axis is the ball normal at its position, base sunk 0.015 into the ball, so rims stand ~0.045 above the surface. Positions: 1 at the top pole, 5 on the upper ring (polar 50° from the pole, 72° apart), 4 on the equatorial ring (polar 100°, 90° apart, offset by 36°). The stem and ball keep their dimensions: the blooms add ~0.05 to the ball diameter (accepted; keep the model within 0.7 × 0.7 × 1.45 and report it) | 4 cup, 5 bud, 0 sepal (red base) | none |

**SOIL DISC (shared wording, identical in TOP-01/02/03/04):** a flat 12-sided cylinder Ø0.50, 0.04 tall, soil brown `#805433` (slot 12), top and sides only, 36 tris; the stem stands in its centre.

**ROSE BLOOM (shared wording, identical in PLT-01/02/03/TOP-01_Rose):** an open cup-shaped bloom: an 8-sided open frustum cup, bottom Ø0.05, rim Ø0.09 (range 0.08–0.10), height 0.06, with a closed bottom (24 tris), a smaller 6-sided pointed bud cone in the middle (base Ø0.05, 0.03 tall, base sunk 0.01 below the rim so the tip stands 0.02 above the rim; 6 tris), sitting on a 4-sided green sepal cone (Ø0.04 → Ø0.02, 0.025 tall; 4 tris). About 34 tris per bloom. Bloom axis = stalk axis. Cup slot 4 `#C8473B`, bud slot 5 `#A8372E`, sepal slot 0. No spiral, no flat disc, no petal cards.

`_Rose` colour: assumed red (slots 4/5) because the catalogue gives no colour; CMP-04 uses `TOP-01_Rose ×4`.

## Anchor

Closest approved model: for `_Rose` blooms — PLT-01 `FMS_Garden_Rose_Bush` (same pack, shared rose bloom). By name only (preview not in this branch): Farm Nature `FMS_Bush_Round` — the shape to differ from (it sits on the ground); `FMS_Hedge_Straight` for the green tone.

## What NOT to do

- NO round bush standing on the ground like Farm Nature `FMS_Bush_Round`: the ball is lifted on a bare stem with 0.8 m clear (the stem must read in the thumbnail).
- No smooth sphere: the ball is faceted (visible ico faces), flat-shaded, no subdivision surface, no smoothed normals.
- No leaves, no alpha cards, no foliage clusters on the ball; no hedge-like cube.
- No thick trunk > Ø0.08 and no thin stem < Ø0.06; no ground plane beyond the disc.
- In `_Rose`, blooms stay on the surface (no floating); do not add stalks; no noise on the ball.
- Do not exceed 500 tris (`_Rose` 800).

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
