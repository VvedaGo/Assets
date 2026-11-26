# PLT-02 Climbing Rose, Side — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/PLT-02.png  (selected 2026-11-25, Э6 batch 1)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Build with the helpers of the approved pilot PLT-01 (leaf cluster, rose bloom, stem prism).

## Catalogue

PLT-02 Плетистая роза, вертикальная `FMS_Garden_Rose_Climbing_Side` — flat plait for the side of arch STR-01/03, lattice MOD-01, wall. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.7×0.3×2.0 | 1000 | no | no | 1 colour: `_Pink` (same mesh, UV remapped) |

Counts: 3 canes, 8 leaf clusters, 8 blooms. Estimate: canes 3×72 = 216 + clusters 8×~50 = 400 + blooms 8×34 = 272 → about 890.

## Parts

Axes: X width, Z depth (plant grows toward +Z), Y up. Pivot at the centre of the base on the flat back plane at the ground: (X 0, Y 0, Z 0). Back plane Z = 0 is the ATTACHMENT PLANE: nothing goes behind it, the back is flat, and the canes lie at Z 0.02–0.06 (touching it); the parts nearest the plane are clipped flat at Z = 0.01 so the model sits flush. Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Canes ×3 | 6-sided prism, Ø0.04 at the base → Ø0.03 at the top, 6 segments each (72 tris), zigzagging up in the XY plane: base at X −0.10 / 0 / +0.10, crossing every 0.35 m; half-width envelope 0.15 at Y 0.3, 0.35 at Y 0.9–1.4 (full 0.7), 0.20 at Y 1.9; tops at Y 1.85, 1.95, 2.0. Lowest 0.3 m bare (no leaves/blooms). Z 0.02–0.06 | 13 bark `#7A5233` | none |
| Leaf clusters ×8 | LEAF CLUSTER (shared wording, see PLT-01): Ø0.20–0.26, here additionally scaled (1.0, 0.7, 0.6) in X,Y,Z and the part behind Z = 0.01 cut flat, ~50 tris. Placed on canes, Y: 0.45, 0.75, 1.00, 1.20, 1.40, 1.60, 1.80, 1.95 alternating left/right, front surface reaches Z ≤ 0.18 | 0 side, 1 up, 2 down | none |
| Blooms ×8 | ROSE BLOOM (shared wording, see PLT-01), Ø0.09 rim. Y: 0.55, 0.80, 1.05, 1.25, 1.45, 1.65, 1.85, 1.98; alternate X sides (±0.05–0.30 per envelope), axis pointing to +Z tilted up 20°, on stalks Ø0.025 0.04–0.08 long, rim front at Z ≤ 0.30. Never overlap the neighbours | 4 cup, 5 bud, 13 stalk, 0 sepal | none |

**ROSE BLOOM (shared wording, identical in PLT-01/02/03/TOP-01_Rose):** an open cup-shaped bloom: an 8-sided open frustum cup, bottom Ø0.05, rim Ø0.09 (range 0.08–0.10), height 0.06, with a closed bottom (24 tris), a smaller 6-sided pointed bud cone in the middle (base Ø0.05, 0.03 tall, base sunk 0.01 below the rim so the tip stands 0.02 above the rim; 6 tris), sitting on a 4-sided green sepal cone (Ø0.04 → Ø0.02, 0.025 tall; 4 tris). About 34 tris per bloom. Bloom axis = stalk axis. Cup slot 4 `#C8473B`, bud slot 5 `#A8372E`, sepal slot 0. No spiral, no flat disc, no petal cards.

**LEAF CLUSTER (shared wording, identical in PLT-01/02/03/06):** a faceted "drop" of foliage: ico sphere subdivision 1 (80 tris), vertices randomly displaced by ±0.03 (fixed seed), squashed, lower third cut off flat, ~50–56 tris. Flat shading. Face colour by normal: up → slot 1 `#8AB257`, sideways → slot 0 `#6E9F4A`, down → slot 2 `#4E7A3A`.

Variant `_Pink`: cup slot 7 `#F2B8C2`, bud slot 6 `#E58FA0`; foliage and canes unchanged.

Mounting (the builder must keep these true; they come from the catalogue):
- STR-01 / STR-03 side lattice: depth 0.6 along the arch's Z, arch height 2.4, opening 1.2. This plant's width 0.7 runs along that 0.6 depth (0.05 overhang per end), height 2.0 stands from the ground (0.4 below the arch top).
- MOD-01 lattice panel: 1.88×0.06×1.80, bottom at Y 0.05. The plant's back plane touches the panel face (offset 0.03 from its axis); plant top 0.2 above the panel top.
- MOD-03 wall (0.60 high, 0.40 thick, cap ±0.22): the back plane touches the cap overhang; the plant rises 1.4 above the wall.
- Empty objects `Plant_L`, `Plant_R` of STR-01/03 are the placement points; this model needs no extra empties.

## Anchor

Closest approved model: PLT-01 `FMS_Garden_Rose_Bush` (same pack; preview and build script appear after its pilot round; leaf cluster, rose bloom and stem helpers are shared). By name only (preview not in this branch): Farm Nature `FMS_Bush_Flowering`.

## What NOT to do

- No alpha cards, no single-plane leaves, no transparent material; no smooth blobs.
- No geometry behind Z = 0; the back stays flat and flush — no stems or blooms poking through the attachment plane.
- No round bush shape: the silhouette is a tall narrow plait, wider in the middle; do not turn it into a flat sheet of leaves hiding the canes.
- No arch, trellis or wall geometry included; the plant is a separate model.
- No spiral/realistic roses, no disc blooms; blooms Ø ≥ 0.08.
- Canes ≥ Ø0.03; no floating clusters/blooms; no coplanar overlaps; flat shading only.
- Do not exceed 1000 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Owner note (2026-11-25, before build)
- Tris budget raised: <= 1600 tris (was 1000). Use it for a richer rose look matching the reworked PLT-01 (Fix 2 of PLT-01.3d.md): copy `rose_bloom_v2` (two petal rings, rim Ø0.11-0.12, ~70-90 tris) and the bumpier `leaf_cluster` from .work/models/AssetNew/PLT-01_Rose_Bush/build.py once PLT-01 Fix 2 is accepted; canes curved (4-6 smooth segments), a few closed buds. This note overrides the 34-tri bloom wording above.
