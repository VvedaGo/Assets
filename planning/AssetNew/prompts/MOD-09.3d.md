# MOD-09 Pond Water — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-09.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.0×1.0×0.04 (top at Y 0.38, bottom 0.34) | ≤ 50 | no | no | none |

## Parts

| Water slab | Box X ±0.5, Z ±0.5, Y 0.34…0.38, raised inside the mesh (the pivot stays on the ground). Top face subdivided into about 3×3 quads / 18 triangles; all vertices on the border of the top are exactly at Y 0.38; inner vertices displaced within ±0.005 in Y for soft ripple facets. Bottom face and sides plain. Flat shading. | A-15 Water `#4A78A8` (opaque, same material M_Garden_Build as everything else; no transparent shader) | Pivot: centre of the base on the ground (X 0, Z 0, Y 0); the slab is lifted 0.34 inside the mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 4: formal pond, internal grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Water MOD-09: slab 1.0 × 1.0, top at Y = 0.38, bottom 0.34. Pivot: centre of the base (on the ground), the slab is raised inside the mesh. Placed at the centres of the cells of the 1.0 m grid.
- Border vertices of the top exactly at 0.38 and the ripple facets inside ±0.005, so neighbouring slabs butt without a step. Side faces at X, Z = ±0.5 touch the neighbouring slab's side faces (gap 0).
- Along the pond boundary the slab edge meets the inner face (Z = 0 line) of MOD-07 and MOD-08 with gap 0; the water top is 0.07 below the top of the edge (0.45).
- Opaque material only, per STYLE.md: a single atlas A cell, no transparent material, no sorting.


## Anchor

Closest approved model in this pack: MOD-07 Pond Edge (the edge that frames it). Earlier packs: Farm Nature water material is transparent and is explicitly not used here (превью нет в ветке).

## What NOT to do

- Do not make the water transparent or assign a second material; it is one opaque cell of atlas A.
- Do not put the slab on the ground: Y 0.34…0.38 inside the mesh, pivot at Y = 0.
- Do not raise or lower the border vertices off Y 0.38, and do not exceed ±0.005 on the ripple vertices (neighbouring slabs must show no step).
- Do not add waves, foam, lily pads, a basin bottom or rim; it is a single flat slab.
- Do not use the lighter metal cell A-9 for ripples: the whole slab is one colour.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
