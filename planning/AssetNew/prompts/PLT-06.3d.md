# PLT-06 Hollyhock — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/PLT-06.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Stem helper from the approved pilot PLT-01; the cup flower is its own generator (shallow cup, not the rose bloom).

## Catalogue

PLT-06 Мальва `FMS_Garden_Hollyhock` — clump of 3 stems, cup flowers along the stem, plate leaves near the ground. Base colour pink. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.6×1.8 | 700 | no | no | 1 colour: `_White` (same mesh, UV remapped) |

Counts: 3 stems, 15 flowers, 3 end buds, 6 leaf plates. Estimate: stems 3×40 = 120 + flowers 15×24 = 360 + buds 3×6 = 18 + plates 6×36 = 216 → about 710; trim plates (or flower sides to 5) if over 700.

## Parts

Axes: X, Z footprint 0.6, Y up. Pivot at the centre of the foot on the ground (0, 0, 0). Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Stems ×3 | 6-sided prism, Ø0.06 at the base → Ø0.035 at the tip, 3 segments (40 tris incl. tip cap), straight with ≤ 4° kink per segment. Start at ring r = 0.04 at Y 0, lean outward 3°–8° in directions 0° / 120° / 240°. Heights 1.8, 1.6, 1.4 (tips). Lower 0.5 bare | 2 dark foliage `#4E7A3A` | none |
| Flowers ×15 | HOLLYHOCK CUP: 6-sided open frustum cup (12 side + 6 bottom = 18 tris), bottom Ø0.05, rim Ø0.16 (lowest) → Ø0.10 (top), depth 0.05 → 0.035; plus a yellow 6-sided cone centre (6 tris, base Ø0.04, 0.02 tall, tip 0.015 above the cup floor). ~24 tris. Mounted on a stalk (4-sided Ø0.02, 0.03–0.05; fused into the stem). 5 per stem at Y fractions 0.35, 0.50, 0.65, 0.80, 0.92 of the stem height, rotating 144° about the stem each step (spiral), axis tilted 50° up from horizontal pointing outward; no two cups intersect | 6 cup main `#E58FA0`, 7 alternate facets `#F2B8C2`, 11 centre `#E8B83A`, 2 stalk | none |
| End buds ×3 | 6-sided cone on each stem tip, Ø0.04, 0.09 tall (6 tris + base fused) | 0 `#6E9F4A` | none |
| Leaf plates ×6 | Flattened faceted solid: ico sphere subdivision 0–1 scaled (0.26, 0.04, 0.20) with vertices displaced ±0.01, ~36 tris, top facets slot 1, sides 0, bottom 2; radially around the foot at r 0.12–0.20, 60° apart, tilted up 10–20° outward, tips reach r = 0.30 (clump 0.6 wide), Y 0.03–0.15; each touches its stem base | 0 side, 1 up, 2 down | none |

Variant `_White`: cup 8 `#F4F1E8` (alternate facets also 8), centre 11 stays yellow; foliage unchanged.

## Anchor

Closest approved model: PLT-01 `FMS_Garden_Rose_Bush` (same pack; shared stem helper and leaf-tone logic). By name only (preview not in this branch): Farm Nature `FMS_Flower_Tulip`, `FMS_Flower_Daisy` for flower chunkiness, and `FMS_Crop_Sunflower_S3`, `FMS_Flower_Lavender` as the shapes to differ from.

## What NOT to do

- Not a sunflower (single head) and not a lavender tuft (low bunch 0.6): three tall stems 1.4–1.8 m with flowers along the upper two thirds, and the silhouette reads as a narrow vertical spire.
- No alpha cards, no single-plane leaves, no flat disc flowers, no transparent material; flowers are closed cups, leaf plates are solids with thickness 0.04.
- No round bush or ball of foliage; no leaf mass hiding the stems.
- Stems ≥ Ø0.035 (thin stems vanish at 10 m); no floating flowers; no coplanar overlaps; flat shading.
- Do not use the rose bloom shape: this flower is a wide shallow cup with a yellow centre.
- Do not exceed 700 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
