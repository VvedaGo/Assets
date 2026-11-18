# MOD-03 Workshop wall 2 m - FMS_Workshop_MOD_03

Reference: planning/FarmProcessing/references/MOD-03.png (front, camera on the -X side: left end face visible, slightly above).
Catalogue: "single timber-framed cream plaster workshop wall module, flat straight side edges", 2.0 x 0.18 x 2.4 m, 250-550 tris, no moving parts.
Wall contract: ../MOD04_WallWindow/spec.md (unchanged: exact bbox, 0.10 half-posts, fixed plinth / rail / plate / joint-block heights, SNAP OK).

## Build (shared with MOD-05)
ONE shared script `build_wall_modules.py` (this folder) builds MOD-03 (`-- <dry|check|export> plain`) and MOD-05 (`door`;
`../MOD05_WallDoor/build_wall_door.py` only forwards to it). It exec's `../MOD04_WallWindow/build_wall_window.py` up to its
module-level `build()` call WITHOUT editing it (contract constants, ybox/xb/yr helpers, snap_check, ymirror_check, build,
verify_headless), then overrides `build_wall`, the 'plain'/'door' KINDS entries, `brace_ext` (clamp for steep braces, identical
result for MOD-03) and the paths. MOD-04 is never built/exported here: its 3 work files + FBX, .fbm, texture, .blend, preview were
md5-checked before/after -> byte-identical. The KINDS 'plain'/'door' entries inside the MOD-04 file are now stale (superseded here).
Own `render_preview.py` (copy of MOD-04's, camera -X side like this ref).

## Feature list (ref) -> model
- Posts both ends, top plate, top joint blocks with red square caps -> contract half-posts, plate, blocks + caps (front and back).
- Dark centre stud from plinth to plate + dark mid rail crossing it (rail in front) -> stud x +-0.07 (z 0.68..2.22), mid rail z 1.30..1.46, WOOD_M.
- Two braces "/ \" from the rail/post corner up to the plate near the stud -> brace (1.52 on the post, 0.24 on the plate), WOOD_M.
- Cream plaster infill, recessed -> contract plaster.
- Plinth of 3 long grey pillow stones -> 3 x 0.60 stones (was 5 in MOD-04; contract heights 0..0.42 kept).

## Material class
Flat palette, own atlas T_FarmProcessing_MOD03_BaseColor.png (256 px, 4x4) = same 16 cells as MOD-04 (cells 0-12 = STA-02/05),
one material M_FarmProcessing_MOD03. Own file (not MOD-04's) so MOD-04's texture is never rewritten. No noise.

## NOT modelled
Wood grain, plaster cracks, stone chisel facets, nails, ground/floor, roof, neighbouring modules, MOD-06 post, LOD1, collider (box = bbox).

## Anchors followed
MOD-04 wall window (contract + script, accepted), STA-05 juice press (palette cells 0-12, render_preview structure), STA-02 cheese press (red caps on chamfered wood).

## Deviations (all from the tiling contract)
Low rail 0.52..0.70 + rail-height joint blocks kept (absent in the ref); plinth 0.42 m and only between the posts (ref: taller, under the posts too);
posts 0.10 half-posts (ref ~0.15); top blocks smaller than the ref's post caps; stone colour shared with MOD-04 (ref warmer).

## Compare rounds (economy, 1 of 3 used) - %TEMP%\FarmProcessing_check\MOD-03 (deleted)
1. Stud + mid rail + braces + 3 stones match the ref layout; 128 px thumb reads (dark cross, braces, cream, stone row, red pegs).
   Remaining differences are the contract deviations above -> stopped.

## Result
496 tris (250-550): post 56, plate 28, rail 28, block 112, cap 96, stone 84, plaster 12, stud 28, midrail 28, brace 24.
non-manifold/loose/degenerate 0, X-mirror 0, Y-mirror 0, gaps 0, base z 0, SNAP OK, brace ends hidden.
FBX re-import: root empty + _Body, 496 tris, bbox -1..1 / -0.09..0.09 / 0..2.4, scale 1, texture found in .fbm. Not checked in Unity.
