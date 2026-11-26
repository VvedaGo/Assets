# MOD-04 Wall Pillar — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-04.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.50×0.50×1.05 | ≤ 300 | no | no | none |

## Parts

| Shaft | Box 0.48 × 0.48 core, Y 0…0.74, plus masonry blocks (3 courses per face, 2 blocks per face, different lengths, staggered) standing 0.01 proud so the outer faces are exactly X ±0.25 and Z ±0.25. Hidden faces removed. | A-12 Stone `#A7A39A` (main), A-11 Stone light `#C9C3B6` (second tone, about one block in four) | Pivot: centre of the base |
| Cap slab | Box 0.50 × 0.50 × 0.06, Y 0.74…0.80, same footprint as the shaft. Bevel 0.015 on the top edges. | A-11 Stone light `#C9C3B6` | Part of the single mesh |
| Ball finial | Icosphere, 1 subdivision (80 tris), diameter 0.25, centre Y 0.925 so it rests on the cap (Y 0.80) and tops out at 1.05. Flat shading. | A-11 Stone light `#C9C3B6` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 2: low stone wall, grid 2.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Pillar MOD-04: 0.50 × 0.50 × 0.80 + ball up to 1.05. Pivot: centre of the base. Placed at a node of the 2.0 m grid.
- Mandatory at every corner and free end of a MOD-03 wall (it hides the 0.2 × 0.2 coping overlap at a corner); optional on a straight joint. Wall ends (X ±1.0 from the span middle) reach the pillar faces: pillar faces at ±0.25 from the node, wall faces at ±0.20 / ±0.22, so no faces coincide.
- Wall top 0.60 is below the pillar cap underside (0.74): the wall coping runs into the pillar shaft, 0.14 below the cap.


## Anchor

Closest approved model in this pack: MOD-03 Low Stone Wall (build MOD-03 first; same blocks, same limestone). Earlier packs: Farm Nature `FMS_Rock_M` for the stone tone (превью нет в ветке).

## What NOT to do

- Do not make the pillar wider than 0.50 (relief and cap must stay inside X, Z ±0.25) or the ball larger than 0.25 across.
- Do not use a smooth sphere for the ball: faceted icosphere, 1 subdivision.
- Do not add a base plinth or a decorative flare; the pillar is a straight shaft.
- Do not float the ball above the cap or sink it into the cap by more than 1 mm.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
