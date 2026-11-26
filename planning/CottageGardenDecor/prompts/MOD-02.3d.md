# MOD-02 Lattice Post — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/MOD-02.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.16×0.16×1.95 | ≤ 60 | no | no | none |

## Parts

| Shaft | Box 0.12 × 0.12, Y 0…1.80, centred on the pivot (X ±0.06, Z ±0.06). No bevel. | A-10 White paint `#EEEDE7` | Pivot: centre of the base, Y = 0 |
| Cap | Box 0.16 × 0.16, Y 1.80…1.95 (0.15 tall), centred; top edges chamfered 0.02 (frustum top). Cap underside Y = 1.80 exactly. | A-10 White paint `#EEEDE7` | Same pivot |

## Snap contract (from CATALOG «Модули и стыковка», item 1: lattice screen, grid 2.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Post MOD-02: section 0.12 × 0.12, cap 0.16 × 0.16 × 0.15, height 1.95. Pivot: centre of the base. Placed at the nodes of the 2.0 m grid.
- The MOD-01 panel frame (X ±0.94 about the span middle, thickness 0.06 on the post axis, bottom Y 0.05, top Y 1.80) touches the shaft faces at ±0.06: gap = 0. The frame top is level with the cap underside (Y 1.80) and below the cap.
- At a 90° corner the panel is rotated around the shared post; there is one post per corner; a free end is always a post.


## Anchor

Closest approved model in this pack: MOD-01 (same white paint and frame wording). Earlier packs: none to match (stakes of Farm Nature `FMS_Bed_Stakes_Row` are a different object, превью нет в ветке).

## What NOT to do

- Do not make the shaft thicker than 0.12 or the cap wider than 0.16: the panel frame must touch the shaft faces, not the cap.
- Do not add a finial, ball or pointed top; the cap is a flat-topped chamfered block.
- Do not raise the cap underside above or below Y = 1.80.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
