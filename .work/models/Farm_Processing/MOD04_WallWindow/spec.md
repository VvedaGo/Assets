# MOD-04 Workshop wall with window 2 m - FMS_Workshop_MOD_04

Reference: planning/FarmProcessing/references/MOD-04.png (front view from slightly above, the RIGHT end face and the top are
visible -> camera on the +X side; the reference perspective is oblique/inconsistent, judged by parts and proportions).
Catalogue: "single timber-framed workshop wall module with a large open window and thick sill, no glass", 2.0 x 0.18 x 2.4 m,
350-700 tris, no moving parts. Pack standard FARM_PROCESSING_PACK.md s.5. Pilot item 3: defines the WALL MODULE CONTRACT.

## Feature list (from the reference)
- Timber frame: post at each end (full height), top plate along the whole top, mid rail at ~0.6 m (between posts).
- Joint blocks (slightly proud of the frame) where the rail and the top plate meet the posts, red square peg cap on each.
- Diagonal braces "\ /" in the upper corners, darker wood, from post to top plate.
- Cream plaster infill, recessed behind the frame.
- Stone plinth: row of 5 grey stones below the rail (z 0..~0.42), bevelled (pillow) faces, V-grooves between stones.
- Window: open rectangular opening (no glass), wood jambs + head board through the full wall depth (wood reveal),
  thick protruding sill that extends past the jambs on both sides.
- Both faces finished identically (wall is seen from inside and outside) -> geometry mirrored in Y.

## Material class
Flat palette: own atlas T_FarmProcessing_MOD04_BaseColor.png (256 px, 4x4 solid cells, UVs at cell centres => padding),
one material M_FarmProcessing_MOD04. Cells 0-12 identical to STA-02/05 (mergeable); 13 stone #A7A39A, 14 stone bevel #8F8B83,
15 plaster #F4E3C1 (warmer cream infill, slightly more saturated than CREAM like the ref). No noise, no grain, no stone texture.

## NOT modelled
Glass, shutters, curtains, window bars, nails/bolts besides the red peg caps, wood grain, plaster cracks, stone facet noise,
floor/ground, roof, neighbouring modules, the corner post MOD-06 (separate asset), LOD1 / collider (box collider = bbox).

## Anchors followed
STA-05 juice press (build_juice_press.py structure, render_preview.py, palette cells 0-12; preview
art/Farm_Processing/Previews/FMS_Workshop_STA_05_Preview.png) and STA-02 cheese press (red square caps on chunky chamfered
wood members). Helpers from ../_common/processing_common.py (read-only). Section 11 house style: bold chamfered members,
flat shading, no noise.

## WALL MODULE CONTRACT (MOD-03 plain / MOD-04 window / MOD-05 door; MOD-06 post)
- Bounding box EXACTLY x -1.000..+1.000, y -0.090..+0.090, z 0.000..2.400 (2.000 x 0.180 x 2.400). Nothing pokes out.
- Pivot = bottom centre (0,0,0), root identity transform, wall plane centred on y=0, front face -Y (both faces identical).
- Grid: modules are placed every 2.000 m along their local X; end faces at x = +-1.000 are flat, vertical and coplanar.
- HALF-POSTS: each module owns a half-width post 0.100 m (x 0.900..1.000) at each end. Two neighbours form one 0.200 m post,
  same width as MOD-06. Every part touching x = +-1 (post, top plate, joint blocks) has square (unchamfered) corners on that
  plane, and the end-face cross-sections at +1 and -1 are identical (X-mirror) -> butted modules show no gap, overlap or groove.
- Open wall end / corner: place MOD-06 (0.2 x 0.2 x 2.4) centred on the grid point; it encloses the half-post
  (0.20 > 0.15 frame depth). Joint blocks/caps stay visible on its faces as peg details.
- Relief layers (front; back mirrored), y of the front face: plaster 0.045, braces 0.060, stones 0.072, frame (posts/plate/rail)
  0.075, window jambs/head 0.080/0.082, joint blocks 0.084, peg caps 0.090, sill 0.090.
- Fixed heights shared by all kinds: stones 0..0.42, rail 0.52..0.70, top plate 2.20..2.40, joint blocks (x 0.80..1.00)
  rail 0.48..0.74 / top 2.08..2.36. Openings are a parameter (KINDS dict): window x +-0.43, z 1.05..1.77 (sill 0.94..1.05,
  x +-0.65); door x +-0.48, z 0..2.02 (rail and stones stop at the jambs).
- build_wall(kind='window'|'plain'|'door') in build_wall_window.py; check `snap_check()` asserts the contract and prints SNAP OK.
- Final numbers in the script: frame face y 0.075 (frame depth 0.150), plaster 0.045, braces 0.060 (half-width 0.05), stones 0.072
  (pillow bevel 0.050 x 0.034), jambs/head 0.080/0.082, joint blocks 0.084 (x 0.80..1.00), caps 0.090 (0.085 sq), sill 0.090.
  Heights: stones 0..0.42, rail 0.52..0.70, plate 2.20..2.40, blocks 0.48..0.74 / 2.08..2.36; window opening x +-0.43,
  z 1.05..1.77 (0.86 x 0.72 m), jambs 0.12, head x +-0.58 z 1.77..1.91, sill x +-0.65 z 0.94..1.05.
- Each brace runs past the post face / plate underside far enough to hide its square end (brace_ext(), asserted).

## Deviations
- The posts are thinner than the reference (0.10 m half-posts on a standalone module, ref ~0.15). This is the price of the tiling
  contract: at a seam, two half-posts read as one 0.20 m post (same as MOD-06). The joint blocks are widened to 0.20 m so the ends still read as chunky.
- Bbox depth is exactly 0.18 (catalogue), so all relief (sill, blocks, caps) fits inside y +-0.09; the timber frame itself is 0.15 deep.
- The preview fits by HEIGHT (88 %), not by width: the module is 2.0 wide x 2.4 high, so it is taller than wide. Camera on the +X side, like the ref.
- Wood keeps the pack palette (#B5835A), which is paler and less orange than the ref. Plaster cell 15 #F6E2BC is warmer, like the ref.

## Compare rounds (economy, 3) - check renders in %TEMP%\FarmProcessing_check\MOD-04 (deleted)
1. Members too thin (plate, rail, braces), joint blocks/caps too small, stones flat. Wall reads thin (frame 0.13 deep).
   -> frame 0.15 deep, plate 0.20, rail 0.18, blocks 0.20 x 0.26/0.28, caps 0.085, braces 0.10, jamb 0.12, head 0.14, sill 0.11 x +-0.65.
2. Snap pair render: the seam reads as one 0.20 post with a double-peg block, top plate continuous, no gap/groove.
   Remaining: stones still flat and cold. Plaster too pale.
   -> pillow bevel 0.050 x 0.034, stone #ADA89E / bevel #8C877E, plaster #F6E2BC.
3. The stones read as pillows, the back side matches the front (Y-mirror), and the 128 px thumbnail is readable (frame / cream / window / stone row / red pegs).
Remaining nitpicks: the ref stones have chiselled irregular facets (kept as clean bevels, by design), the posts are thinner (contract),
the wood is less orange (palette), and the ref's top-left block sits at the very top while the top-right one sits under the plate (the ref is inconsistent; ours is symmetric).

## Result
Tris 628 (budget 350-700): post 56, plate 28, rail 28, blocks 112, caps 96, stones 140, plaster 32, braces 24, jambs 56, head 28, sill 28.
Checks: non-manifold / loose / degenerate 0; X-mirror 0.000000; Y-mirror 0.000000; component gaps 0; base z = 0; SNAP OK
(12 + 12 identical planar end faces, frame section 0.15 x 2.40 fully covered). MOD-03 'plain' 496 tris and MOD-05 'door'
548 tris both pass the same checks and SNAP OK. They are checks only, not exported, and still need their own look rounds.
FBX re-import: 2 nodes (root empty + _Body), 628 tris, bbox -1..1 / -0.09..0.09 / 0..2.4, scale 1, texture found in .fbm (256 px).
Blender shows a +90 X rotation on the re-imported nodes (FBX Y-up axis conversion, same export path as STA-05). Not checked in Unity.
