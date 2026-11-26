# FLB-01 Straight Flower Bed — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/FLB-01.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.0×1.0×0.25 (`_Planted` up to 0.7) | 300 (`_Planted` 1500) | base: no; `_Planted`: yes (LOD1 via make_lod1.py) | no | 1: `_Planted` (mesh) |

## Parts

| Border | Rectangular ring on the footprint outline X ±1.0, Z ±0.5, width 0.12 (inner rectangle 1.76 × 0.76), height Y 0…0.25. About 12 hewn blocks of different lengths (0.4–0.6) with staggered joints, small 0.01 reveal between them allowed; the outer faces exactly on X ±1.0, Z ±0.5. Top faces flat. | F-14 Stone `#A7A39A` (sides), F-15 Stone light `#C9C3B6` (flat tops) | Pivot: centre of the footprint bounding box on the ground (X 0, Z 0, Y 0) |
| Soil mound | Faceted low mound inside the border, 6–8 triangles on top plus the edge skirt, crown 0.20, rim about 0.16 at the border. Closed against the border inner faces. Flat shading. | F-12 Soil `#805433` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 6: flower beds, grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Footprint exactly on the grid (2.0 × 1.0). Border width 0.12 inside the footprint, border top 0.25, soil 0.20. Neighbouring beds touch by their borders and do not overlap. `_Planted` flowers do not leave the footprint.
- Pivot (assumption, not stated in the catalogue): centre of the footprint bounding box on the ground; the placement script offsets by half-cells so the footprint edges land on grid lines.

## Variant `_Planted` (mesh variant, separate FBX and prefab)

Same border and soil as the base model, plus plants; budget 1500 tris in total (base 300); LOD1 generated with `make_lod1.py` (50% per part, palette recomputed). Plants are stylized primitives only: faceted leaf drops (low-subdivision displaced icospheres with visible flat facets), cones for spikes, 8-sided cup-shaped blooms about 0.08-0.10 m across, no alpha cards and no single-plane leaves, flat shading, two or three neighbouring green atlas cells alternated by face rather than noise. Foliage: Atlas F slots 0, 1, 2 (`#6E9F4A`, `#8AB257`, `#4E7A3A`), stems F-13 `#7A5233`. Flowers: rose pink F-6 `#E58FA0` (outer petals F-7 `#F2B8C2`), white F-8 `#F4F1E8`, lilac F-9 `#A58BC9`, yellow centres F-11 `#E8B83A`. Planted layout: a mixed set of 7–9 clumps; the crown of the planting is on the long centre line and reaches Y 0.70 (about 0.5 above the soil), falling to about 0.45 at the short ends; clump types alternate along the bed (pink cups, white cups, tall lilac cone spikes, yellow small cups) so that no two clumps of the same colour touch; keep every plant at least 0.02 inside the outer face of the border.


## Anchor

Closest approved model in this pack: PLT-01 Rose Bush (foliage drops and cup blooms generator) and WTR-03 Birdbath (stone tones), if already approved. Earlier packs: Farm Nature `FMS_Flower_Tulip`, `FMS_Flower_Daisy`, `FMS_Bush_Flowering` (flower and foliage tone, превью нет в ветке); Farm Nature `FMS_Bed_Raised_2x1` is the wooden vegetable bed this must not look like.

## What NOT to do

- Do not let the stone border exceed the footprint or exceed 0.12 wide: the footprint is exactly on the 1.0 m grid so neighbouring beds touch borders without overlapping.
- Do not raise the soil above 0.20 or lower the border below 0.25; the soil must stay visibly below the border tops.
- Do not make the base model's soil a flat disc or box coplanar with the border tops; it is a low faceted mound.
- Do not use alpha cards, single-plane leaves or smooth blobs for `_Planted`; do not let any plant cross the footprint or the stated height.
- Do not add soil bags, tools, a path or lawn around the bed.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
