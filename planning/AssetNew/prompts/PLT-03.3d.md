# PLT-03 Climbing Rose, Top — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/PLT-03.png  (selected 2026-11-25, Э6 batch 1)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Build with the helpers of the approved pilot PLT-01 (leaf cluster, rose bloom, stem prism).

## Catalogue

PLT-03 Плетистая роза, гирлянда `FMS_Garden_Rose_Climbing_Top` — for the top of STR-01 and a pergola beam; pivot at the centre of the bottom. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.6×0.6×0.4 | 700 | no | no | 1 colour: `_Pink` (same mesh, UV remapped) |

Counts: 2 canes, 5 leaf clusters, 6 blooms. Estimate: canes 2×72 = 144 + clusters 5×~50 = 250 + blooms 6×34 = 204 → about 600.

## Parts

Axes: X length (1.6), Z depth (0.6), Y up. Pivot at the centre of the underside: (0, 0, 0). All geometry has Y ≥ 0 (nothing hangs below the pivot); the underside is the ATTACHMENT PLANE, flat, Y = 0 (canes touch it at Y 0.02 base of the prism, clusters clipped flat at Y = 0.01). Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Canes ×2 | 6-sided prism, Ø0.05 → Ø0.04, 6 segments each (72 tris), running along X from −0.78 to +0.78 at Y 0.03–0.10, weaving around each other in Z (±0.10, one full twist), gentle arch up to Y 0.10 at X = 0 | 13 bark `#7A5233` | none |
| Leaf clusters ×5 | LEAF CLUSTER (shared wording, see PLT-01), Ø0.24–0.30, scaled (1.0, 0.6, 0.9), lower part cut flat at Y = 0.01, ~50 tris. X positions −0.60, −0.30, 0.05, 0.38, 0.65; Z offsets alternate ±0.12–0.18; top ≤ Y 0.28 | 0 side, 1 up, 2 down | none |
| Blooms ×6 | ROSE BLOOM (shared wording, see PLT-01), Ø0.09 rim. X: −0.70, −0.42, −0.12, 0.20, 0.50, 0.72; Z ±0.05–0.25 alternating; rim at Y 0.32–0.40 (highest points), on stalks Ø0.025, axes tilted outward/up 15–40°. Not overlapping | 4 cup, 5 bud, 13 stalk, 0 sepal | none |

**ROSE BLOOM (shared wording, identical in PLT-01/02/03/TOP-01_Rose):** an open cup-shaped bloom: an 8-sided open frustum cup, bottom Ø0.05, rim Ø0.09 (range 0.08–0.10), height 0.06, with a closed bottom (24 tris), a smaller 6-sided pointed bud cone in the middle (base Ø0.05, 0.03 tall, base sunk 0.01 below the rim so the tip stands 0.02 above the rim; 6 tris), sitting on a 4-sided green sepal cone (Ø0.04 → Ø0.02, 0.025 tall; 4 tris). About 34 tris per bloom. Bloom axis = stalk axis. Cup slot 4 `#C8473B`, bud slot 5 `#A8372E`, sepal slot 0. No spiral, no flat disc, no petal cards.

**LEAF CLUSTER (shared wording, identical in PLT-01/02/03/06):** a faceted "drop" of foliage: ico sphere subdivision 1 (80 tris), vertices randomly displaced by ±0.03 (fixed seed), squashed, lower third cut off flat, ~50–56 tris. Flat shading. Face colour by normal: up → slot 1 `#8AB257`, sideways → slot 0 `#6E9F4A`, down → slot 2 `#4E7A3A`.

Variant `_Pink`: cup slot 7 `#F2B8C2`, bud slot 6 `#E58FA0`; foliage and canes unchanged.

Mounting (from the catalogue, keep true):
- STR-01 top: 1.6 wide, 0.7 deep, top Y 2.4, flat with crossbars. The garland's 1.6 length equals the arch top width; its 0.6 depth fits within the 0.7 arch depth. Placed at (arch X 0, Y 2.4).
- STR-04 pergola beam: 0.10×0.22 along X, top Y 2.46, centred on Z = ±1.5. The garland lies along X on the beam (length 1.6 < 3.5), its 0.6 depth straddles the 0.10 wide beam (0.25 each side); placed at Y 2.46, X by the composer; the canes sit over the beam.
- MOD-01 lattice top (1.80) is not a target.

## Anchor

Closest approved model: PLT-01 `FMS_Garden_Rose_Bush` (same pack; preview and build script appear after its pilot round; shared helpers). By name only (preview not in this branch): Farm Nature `FMS_Bush_Flowering`.

## What NOT to do

- No alpha cards, no single-plane leaves, no transparent material; no smooth blobs.
- Nothing below Y = 0: no hanging stems or blooms (the hanging look belongs to PLT-05); underside is flat.
- No beam/arch geometry inside the model; it is a separate plant.
- No round bush mound: keep it a long low garland of two canes with sparse clusters; canes stay visible.
- No spiral/realistic roses, no disc blooms; blooms Ø ≥ 0.08.
- Canes ≥ Ø0.04; no floating clusters/blooms; no coplanar overlaps; flat shading only.
- Do not exceed 700 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Owner note (2026-11-25, before build)
- Tris budget raised: <= 1100 tris (was 700). Use it for a richer rose look matching the reworked PLT-01 (Fix 2 of PLT-01.3d.md): copy `rose_bloom_v2` (two petal rings, rim Ø0.11-0.12, ~70-90 tris) and the bumpier `leaf_cluster` from .work/models/AssetNew/PLT-01_Rose_Bush/build.py once PLT-01 Fix 2 is accepted; canes curved (4-6 smooth segments), a few closed buds. This note overrides the 34-tri bloom wording above.
