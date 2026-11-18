# MOD-05 Wall with doorway 2 m - FMS_Workshop_MOD_05

Reference: planning/FarmProcessing/references/MOD-05.png (front, camera on the +X side like MOD-04, slightly above).
Catalogue: "single timber-framed workshop wall module with an open walk-through doorway, no door leaf", 2.0 x 0.18 x 2.4 m, 300-650 tris, no moving parts.
Brief: clear opening >= 0.9 x 2.0 m, threshold flush with the ground (plinth cut away). Wall contract: ../MOD04_WallWindow/spec.md (unchanged).

## Build
Shared script ../MOD03_Wall/build_wall_modules.py (see MOD03 spec: reuses the MOD-04 script read-only, MOD-04 files md5-identical).
`build_wall_door.py` here = wrapper: `blender -b --factory-startup --python build_wall_door.py -- <dry|check|export> door [round] [--pair] [--back]`.
`--pair` renders MOD-03 | MOD-04 (its exported FBX, read only) | MOD-05 in a row at 2 m spacing (snap proof). Own render_preview.py.

## Feature list (ref) -> model
- Contract frame: half-posts, plate, top + rail joint blocks with red caps (front + back).
- Dark door casing: jambs to the ground + head, through the full depth -> ONE inverted-U loft (60 tris instead of 84 for 3 boxes), WOOD_D.
- Clear opening x +-0.48, z 0..2.01 (0.96 x 2.01 m); nothing in the opening (door_check: no verts, 0 ray hits through a 19x41 grid).
- Plaster gap between head (z 2.01..2.11) and plate (2.20).
- Short light rails between post and casing at the contract height (0.52..0.70).
- Brick plinth beside the opening: 2 rows (bottom 2 bricks, top 1) per side, pillow bevel 0.030 x 0.024, z 0..0.42.
- Braces "\ /" from the posts (z 1.45) to the plate (x +-0.62), WOOD_M like MOD-04.

## Material class
Flat palette, own atlas T_FarmProcessing_MOD05_BaseColor.png (same 16 cells as MOD-04/MOD-03), M_FarmProcessing_MOD05. No noise.

## NOT modelled
Door leaf, hinges, threshold board, wood grain, plaster cracks, ground, roof, neighbouring modules, MOD-06, LOD1, collider.

## Anchors followed
MOD-04 wall window (contract + script), STA-05 juice press (palette, preview), STA-02 cheese press (red caps on chamfered wood).

## Deviations
- Opening 2.01 m high (ref ~1.75): the walk-through rule pushes the head up to 0.09 m under the plate, so the braces are steeper
  and shorter than in the ref (they must clear the head; post-side extension clamped to stay inside the 0.10 half-post).
- No head overhang past the jambs (single U casing to fit the 650 budget with the brick plinth).
- Rails at the contract height 0.52..0.70 on both sides (ref: ~0.9 / ~0.8, asymmetric); X-symmetric bricks (ref differ per side).
- Braces WOOD_M (match MOD-04) while the casing is WOOD_D (ref: both the same dark tone).

## Compare rounds (economy, 2 of 3) - %TEMP%\FarmProcessing_check\MOD-05 (deleted)
1. 660 tris > 650 with 3 boxes for jambs/head -> U casing (636). Brace poked out of x=+1 by 0.5 mm -> clamp. Casing reads the same as the posts -> WOOD_D.
2. Dark casing reads as a doorway at 128 px; snap row MOD-03|MOD-04|MOD-05: seams read as one 0.20 post, plate/rails/stones continuous, no gap.
   Remaining: steep braces, no head overhang, lighter bricks than the ref (shared stone cells) -> nitpicks / contract.

## Result
636 tris (300-650): post 56, plate 28, rail 56, block 112, cap 96, stone 168, plaster 36, brace 24, casing 60.
non-manifold/loose/degenerate 0, X-mirror 0, Y-mirror 0, gaps 0, base z 0, SNAP OK, DOOR check OK.
FBX re-import: root empty + _Body, 636 tris, bbox -1..1 / -0.09..0.09 / 0..2.4, scale 1, texture found in .fbm. Not checked in Unity.
