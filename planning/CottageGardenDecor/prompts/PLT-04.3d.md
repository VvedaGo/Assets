# PLT-04 Ivy Patch — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/PLT-04.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Build with the stem helper of the approved pilot PLT-01; the ivy leaf is its own generator (rhombus leaf).

## Catalogue

PLT-04 Плющ на стену `FMS_Garden_Ivy_Patch` — carpet of faceted rhombus leaves in 3 tones, flat back (to the wall). Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.0×0.15×1.0 | 500 | no | no | none |

Estimate: back layer 30×4 = 120 + middle layer 24×8 = 192 + front layer 14×8 = 112 + stems 3×~20 = 60 → about 485.

## Parts

Axes: X width, Z depth (leaves grow toward +Z), Y up. Pivot at the centre of the bottom edge on the back plane: (X 0, Y 0, Z 0). The back plane Z = 0 is the ATTACHMENT PLANE: flat, nothing behind it, no part dips below Z = 0. Total depth ≤ 0.15. Root scale 1, rotation 0. Patch extent X ±0.5, Y 0–1.0; leaf tips may poke out ≤ 0.04.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Back layer ×30 | Flat-based rhombus pyramid: base rhombus 0.20 long × 0.15 wide lying in the XY plane on Z = 0, apex 0.03 above the plane (4 side tris, no base needed). Staggered grid 5 columns × 6 rows (step 0.20 × 0.17, odd rows shifted half), rotated ±15° at random (fixed seed), so the back plane is fully covered edge to edge with a rim | 3 deep green `#3F6B3A` | none |
| Middle layer ×24 | Ivy leaf: rhombus 0.14 long × 0.10 wide, folded along the long axis: bipyramid with a raised ridge 0.025 (8 tris), pitched 15–25° out of the wall plane, base at Z 0.04–0.08; pointing down ±40° (leaf tip hangs down, never up). Staggered 4×6 grid with jitter ±0.03, overlapping the back layer by 30% | 2 dark foliage `#4E7A3A` | none |
| Front layer ×14 | Same leaf as the middle layer, 0.14×0.10, 8 tris, base at Z 0.08–0.12, tip at ≤ Z 0.15; 14 scattered over the area, 2–3 along the edges sticking out | 0 foliage `#6E9F4A` | none |
| Vines ×3 | 6-sided prism Ø0.035, ~3 segments (~20 tris), running up through the patch at X −0.3 / 0.05 / 0.32 with a zigzag, Z 0.02–0.05, visible in 3–4 gaps (leave small holes in the middle layer) | 13 bark `#7A5233` | none |

Leaf colour is by LAYER (3 tones, slots 3/2/0), not noise; light accents: up to 4 front-layer leaves use slot 1 `#8AB257` on their upward-facing faces.

Mounting (from the catalogue, keep true):
- MOD-03 stone wall: 2.0×0.40×0.60 (cap 0.44 wide, ±0.22). Place the back plane on the wall face at Z = ±0.20 (wall body) — below the cap at Y ≤ 0.54 — or at ±0.22 over the cap overhang. The 1.0 m height exceeds the 0.60 wall: the patch stands 0.4 m above the cap, so put it on a taller surface or accept that the upper part stands free; two patches (2.0 m) cover one wall bay.
- MOD-01 lattice screen: 1.88×0.06×1.80; the back plane touches the panel face (Z = ±0.03); 1.0 m patch covers about half the panel width.
- STR-04 pergola posts (0.16 square) are narrower than the patch and are not a mounting target.

## Anchor

Closest approved model: PLT-01 `FMS_Garden_Rose_Bush` (same pack; shared stem helper, tone of foliage). By name only (preview not in this branch): Farm Nature `FMS_Bush_Flowering` for foliage tone.

## What NOT to do

- No alpha cards, no single-plane leaves, no transparent material; every leaf is a closed solid with a ridge. Cull Back only.
- No geometry behind Z = 0; back stays flat; no leaf rotates through the plane.
- No smooth blob/cloud shapes; no heart-shaped or lobed real ivy outline (rhombus only); no flowers/berries.
- No wall included; do not make a rectangular slab: the edge is irregular but inside the 1 m square (± 0.04 tips).
- Tones follow the 3 layers only; no noise.
- No coplanar overlaps (stagger leaf Z by ≥ 0.005); no floating leaves (each overlaps the layer behind); flat shading.
- Do not exceed 500 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
