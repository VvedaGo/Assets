# MOD-05 Brick Edging — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/MOD-05.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.0×0.10×0.15 | ≤ 200 | no | no | none |

## Parts

| Brick tooth ×8 | Each brick segment is 0.125 wide in X and 0.10 deep (Z ±0.05): a pentagonal prism with a flat bottom at Y 0, vertical sides to Y 0.0875, and a 45° roof (two sloped faces) to a sharp peak at Y 0.15 at the segment middle. Segment k spans X −0.5 + 0.125·k … −0.5 + 0.125·(k+1), k = 0…7; valleys at segment borders (Y 0.0875), so the profile starts and ends with a valley at X = ±0.5. Alternate colour per brick. | A-14 Brick `#9C3F33` (even bricks), A-6 Red dark `#A8372E` (odd bricks) | Pivot: centre of the base (X 0, Z 0, Y 0) |

## Snap contract (from CATALOG «Модули и стыковка», item 3: brick edging, grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Straight MOD-05: X from −0.5 to +0.5, section 0.10 (Z ±0.05) × 0.15. Pivot: centre of the base. Placed on a grid line at the middle of a cell (node + 0.5).
- Tooth pitch 0.125 (8 per metre); there is a valley at each end face, so the sawtooth is continuous across the joint. End faces are flat vertical cuts at X = ±0.5, identical profile at both ends.
- Joins the MOD-06 arc (tangent along the grid line, same 0.10 × 0.15 section) end to end. Four arcs make a ring of axis Ø 2.0.
- Checks: ends on grid nodes; cross-sections at the joint identical; tooth phase.


## Anchor

Closest approved model in this pack: none (MOD-05 is the first brick piece; MOD-06 is built from it). Earlier packs: none to match (Farm Nature `FMS_Path_Stone_*` is a different object).

## What NOT to do

- Do not model individual joints, mortar, cracks or a brick texture: eight flat-coloured tooth bricks only.
- Do not shorten the strip, change the tooth pitch or move a peak onto an end face; a valley must sit on each end.
- Do not make the strip a flat paving slab or add width: the section is 0.10 × 0.15.
- Do not merge the two brick colours into one: alternate per brick so the sawtooth reads on the icon.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
