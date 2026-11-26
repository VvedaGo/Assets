# MOD-01 Lattice Panel — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-01.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.88×0.06×1.80 | ≤ 900 (est. 350–450) | no | no | none |

## Parts

| Frame | 4 boxes, member width 0.08, thickness 0.06 (Z −0.03…+0.03): 2 stiles X ±0.86…±0.94 over Y 0.05…1.80; top rail Y 1.72…1.80 and bottom rail Y 0.05…0.13 between the stiles. Outer extents exactly X ±0.94, Y 0.05…1.80. No bevel. | A-10 White paint `#EEEDE7` | Part of the single mesh |
| Lattice slats | Slat 0.04 wide × 0.03 thick, two layers at ±45°: layer 1 (+45°) at Z 0…+0.03, layer 2 (−45°) at Z −0.03…0, perpendicular pitch 0.20 (about 12 slats per direction). Slats are clipped to the opening X ±0.86, Y 0.13…1.72 and end flush on the inside faces of the frame. Real gaps, no cap faces over the openings. No bevel. | A-10 White paint `#EEEDE7` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 1: lattice screen, grid 2.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Pivot: centre of the base. The panel is placed at the middle of a span (post node + 1.0 m).
- Frame X from −0.94 to +0.94 (post half-width 0.06 on each side): the frame ends touch the faces of the MOD-02 posts, gap = 0. Thickness 0.06 on the post axis (Z = 0). Frame bottom at Y = 0.05, top at Y = 1.80 (below the post cap that starts at Y = 1.80).
- Post pitch is exactly 2.000 m. At a 90° corner the panel is rotated around the shared post; there is one post per corner; a free end is always a post.
- Checks: gap frame end ↔ post face = 0; post pitch 2.000; frame top below the post cap.

## Palette note

The lead brief calls the lattice white; STYLE.md lists slot A-2 `#9C6B44` for the MOD-01 slats. This spec uses white `#EEEDE7` for the whole panel. Slot A-2 is unused here. If the orchestrator prefers medium-wood slats, change only the "Lattice slats" row.


## Anchor

Closest approved model in this pack: none yet (build MOD-01 before MOD-02 so the post matches). White paint tone is checked against STR-06 Gazebo once it is approved. Earlier packs: Farm Yard `FMS_Fence_Picket` for wood thickness (превью нет в ветке).

## What NOT to do

- Do not make the lattice a rectangular grid or a flat textured plane with alpha holes: the diagonal slats and the gaps are real geometry.
- Do not make the panel thinner than 0.06 or the slats thinner than 0.03; they must read at 10 m and on a 160 px icon.
- Do not extend the frame under Y = 0.05 or past X ±0.94, and do not add feet, posts or a cap: the posts are MOD-02.
- Do not leave slat ends poking out of the frame or floating inside the opening; do not put two coplanar slat faces on the same plane (the two layers sit at different Z).
- Do not use the medium-wood colour for the slats unless the Palette note is changed by the orchestrator.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
