# MOD-06 Brick Edging Curve — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/MOD-06.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.05×1.05×0.15 | ≤ 300 | no | no | none |

## Parts

| Brick tooth ×12 | The MOD-05 brick section revolved around the Y axis through the pivot: radial section 0.95…1.05 (0.10 wide), flat bottom at Y 0, vertical sides to Y 0.0875, 45°-class roof to a sharp peak at Y 0.15 on the brick middle. 12 bricks of 7.5° each (pitch about 0.131 m on the axis, close to MOD-05's 0.125; 12 is the integer count that keeps a valley on both ends). Valleys at the brick borders, including both end faces. Alternate colour per brick. | A-14 Brick `#9C3F33` (even bricks), A-6 Red dark `#A8372E` (odd bricks) | Pivot: centre of the circle at ground level (arc centre, Y = 0) |

## Snap contract (from CATALOG «Модули и стыковка», item 3: brick edging, grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Arc MOD-06: 90°, radius on the axis 1.0. Pivot: the circle centre, placed at a grid node. The ends lie at the points (1.0, 0, 0) and (0, 0, 1.0); the tangents run along the grid lines (end faces are radial cuts at Z = 0 and X = 0). Bounding box about 1.05 × 1.05 (outer radius 1.05).
- Section 0.10 × 0.15, identical to MOD-05, so a MOD-05 strip butts onto an arc end and the sawtooth stays continuous (valley on every end face). Four arcs make a ring of axis diameter 2.0.
- Checks: ends on grid nodes; cross-sections at the joint identical; tooth phase.


## Anchor

Closest approved model in this pack: MOD-05 Brick Edging (same bricks, tones and section; build MOD-05 first). Earlier packs: none.

## What NOT to do

- Do not use a different section or height from MOD-05: the joint must show no step.
- Do not make the arc an ellipse or a different angle; it is exactly 90° at radius 1.0 on the axis, with the pivot at the circle centre, not on the arc.
- Do not smooth the sawtooth into a wavy line: peaks stay sharp and flat-shaded; no mortar, no joints.
- Do not cut the end faces off the radial lines (X = 0 and Z = 0 planes).
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
