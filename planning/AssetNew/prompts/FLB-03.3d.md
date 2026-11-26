# FLB-03 Round Flower Bed — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/FLB-03.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.0×2.0×0.25 (`_Planted` up to 0.8) | 400 (`_Planted` 1800) | base: no; `_Planted`: yes (LOD1 via make_lod1.py) | no | 1: `_Planted` (mesh) |

## Parts

| Border | Ring of 16 trapezoid blocks (22.5° each), outer radius 1.0 (the ring's outer vertices on radius 1.0), width 0.12 (inner radius 0.88), height Y 0…0.25. Reveal between blocks 0.01 allowed. Top faces flat. 16 segments as for all round forms of this size. | F-14 Stone `#A7A39A` (sides), F-15 Stone light `#C9C3B6` (flat tops; may alternate by block) | Pivot: centre of the circle on the ground (X 0, Z 0, Y 0), which sits on a grid node |
| Soil dome | Faceted low dome, 16 sectors with a central apex, crown 0.20 at the centre, rim about 0.16 at the border. Closed against the border inner faces. Flat shading. | F-12 Soil `#805433` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 6: flower beds, grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Footprint exactly on the grid (circle Ø 2.0 with the centre at a grid node). Border width 0.12 inside the footprint, border top 0.25, soil 0.20. Neighbouring beds touch by their borders and do not overlap. `_Planted` flowers do not leave the footprint.
- Pivot (assumption, not stated in the catalogue): centre of the footprint bounding box on the ground; the placement script offsets by half-cells so the footprint edges land on grid lines.

## Variant `_Planted` (mesh variant, separate FBX and prefab)

Same border and soil as the base model, plus plants; budget 1800 tris in total (base 400); LOD1 generated with `make_lod1.py` (50% per part, palette recomputed). Plants are stylized primitives only: faceted leaf drops (low-subdivision displaced icospheres with visible flat facets), cones for spikes, 8-sided cup-shaped blooms about 0.08-0.10 m across, no alpha cards and no single-plane leaves, flat shading, two or three neighbouring green atlas cells alternated by face rather than noise. Foliage: Atlas F slots 0, 1, 2 (`#6E9F4A`, `#8AB257`, `#4E7A3A`), stems F-13 `#7A5233`. Flowers: rose pink F-6 `#E58FA0` (outer petals F-7 `#F2B8C2`), white F-8 `#F4F1E8`, lilac F-9 `#A58BC9`, yellow centres F-11 `#E8B83A`. Planted layout: tiered. The centre carries a cluster of tall lilac cone spikes with foliage reaching Y 0.80; a middle ring of pink and white cup blooms reaches about 0.55; the outer ring is low (about 0.40) with yellow small cups and foliage drops; plants are arranged in 8–10 clumps, higher in the centre, and keep at least 0.02 inside the outer radius 1.0. Same wording for plants as FLB-01.


## Anchor

Closest approved model in this pack: PLT-01 Rose Bush (foliage drops and cup blooms generator) and WTR-03 Birdbath (stone tones), if already approved. Earlier packs: Farm Nature `FMS_Flower_Tulip`, `FMS_Flower_Daisy`, `FMS_Bush_Flowering` (flower and foliage tone, превью нет в ветке); Farm Nature `FMS_Bed_Raised_2x1` is the wooden vegetable bed this must not look like. Same border and soil wording as FLB-01 (build FLB-01 first).

## What NOT to do

- Do not let the stone border exceed the footprint or exceed 0.12 wide: the footprint is exactly on the 1.0 m grid so neighbouring beds touch borders without overlapping.
- Do not raise the soil above 0.20 or lower the border below 0.25; the soil must stay visibly below the border tops.
- Do not make the base model's soil a flat disc or box coplanar with the border tops; it is a low faceted mound.
- Do not use alpha cards, single-plane leaves or smooth blobs for `_Planted`; do not let any plant cross the footprint or the stated height.
- Do not add soil bags, tools, a path or lawn around the bed.
- Do not use fewer than 12 or more than 16 border segments or a smooth ring; the facets must be visible.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
