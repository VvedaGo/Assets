# STA-03 Upright butter churn - FMS_Workshop_STA_03

Reference: planning/FarmProcessing/references/STA-03.png (almost frontal, slight camera yaw to the -X side, ~14 deg elevation).
Catalogue: "traditional upright wooden butter churn with a narrow barrel, removable lid and vertical dasher", 0.5/0.5/1.0 m,
700-1400 tris, moving parts: dasher rod (shtok) and lid (kryshka). Economy mode (small prop): max 3 compare rounds.

## Feature list (from the reference)
- Narrow barrel, straight taper, wider at the bottom (~0.41 m stave diameter at the foot, ~0.375 m at the top), ~0.59 m tall,
  16 staves with thin seams (uniform orange wood), stave ends below the lowest hoop with a small outer bottom chamfer.
- 3 thick dark-brown hoops (band ~0.064 m high) at ~0.12 / 0.30 / 0.535 m; the ref hoops are dark wood/leather brown, NOT grey
  metal (brief said "metal hoops" -> followed the reference, which is authoritative).
- Hex rivets on every hoop: 2 visible per hoop at about +-45 deg from the front -> 4 per hoop (45/135/225/315 deg), grey metal.
- Cream lid (16-gon, ~0.40 m, ~0.06 m thick), slight overhang over the barrel, chamfered top edge.
- Grey octagonal metal grommet ring around the rod hole on the lid top.
- Two red staple (U) handles on the lid top, left and right of the rod, long axis along X.
- Dasher: octagonal light-wood rod, thin at the lid (r ~0.015) widening to a grip at the top (r ~0.024), chamfered/rounded top,
  top at 1.0 m; at the bottom inside the barrel a cross of two boards (hidden, required by the brief).

## Material class
Flat palette: own atlas T_FarmProcessing_STA03_BaseColor.png (256 px, 4x4 solid cells), one material M_FarmProcessing_STA03.
Cells 0-12 identical to STA-05/STA-02 (mergeable); 13 = rod light wood #C99263; 14/15 spare. No noise, no grain.

## NOT modelled
Barrel bottom board (hidden), lid inner lip/plug, butter/cream inside, nails/wood grain, floor/platform, text, LOD1, collider.

## Anchors followed
STA-05 basket juice press (approved: art/Farm_Processing/Previews/FMS_Workshop_STA_05_Preview.png + build_juice_press.py:
stave/hoop/rivet code, palette, checks, export) and STA-02 cheese press (pilot; same helpers via _common/processing_common.py),
which follow MarketFarm Scale (contact/mirror checks) and Cart (chunky chamfered wood).

## Hierarchy / pivots
FMS_Workshop_STA_03 (empty, ground centre, identity) -> _Body (0,0,0: staves, hoops, rivets), _Lid (centre bottom on the barrel
top), _Dasher (rod axis at lid-top height; slides along local Z). Front = -Y.

## Dimensions / deviations
Catalogue 0.5/0.5/1.0. Built X 0.449 x Y 0.449 (bottom hoop + rivets) x Z 1.000 (rod top). Height kept at 1.0 m; width follows the
reference proportions (barrel 0.43 m stave diameter at the foot, 0.37 m at the top, lid 0.406 m) -> 0.05 m narrower than the
catalogue box. Hoops dark wood brown (ref) instead of the brief's "metal hoops"; rivets are metal.
Added a hidden 8-gon bottom board (0-0.03 m) so the stave seams do not show the backdrop through the open bottom.

## Compare rounds (preview camera, VIEW_DIR (-0.14, -1, 0.45), check renders in %TEMP%, deleted)
1. Lid budget too high (472 tris, chamfered handles), rivets small, rod thin and widening only near the top, camera too low.
   -> plain square staple handles, 4-ring grommet, rivets R 0.020, rod 0.0165 -> 0.0275 linear taper, hoops 20 mm thick, elev up.
2. Rivets/rod still light vs ref, barrel taper weaker than ref (hoop widths 430 -> 460 px in ref).
   -> rivets R 0.023, rod 0.0175 -> 0.030, grommet R 0.052, taper apothem 0.210 -> 0.185, elevation 0.45.
   Side render: light line in the bottom stave seam (backdrop seen through the open bottom) -> hidden bottom board; dasher cross
   made of plain boxes to keep the budget.
3. Final 1280x800 preview vs ref: silhouette, colour blocks, hoop/rivet layout, lid/grommet/handles match; 128 px thumbnail reads
   as a churn (cream lid + red handles + rod over a banded barrel).
4. Lead review (Major: barrel read as bulging/segmented, narrowing to the foot): straight staves with a stronger monotonic taper
   (outer apothem 0.214 -> 0.184, ratio 1.16), bottom chamfer 9 -> 4 mm, hoops 14 mm proud (was 20), hoops at 0.10 / 0.27 / 0.545
   (top hoop 10 mm under the lid), rounded staple handles (square section swept through 2 bends of 3 segments, mitred rings),
   preview lens 50 -> 70 mm (the 50 mm top-down perspective shrank the foot visually). Lead-approved overrun: 1448 tris.
Remaining nitpicks: ref rod slightly lighter; a 2-3 px light speck at the very bottom of the front seam (ray under the stave foot; hidden by any floor).

## Result
Tris: Body 972 (16 staves, 3 hoops, 12 rivets, bottom board), Lid 376 (lid, grommet, 2 rounded handles), Dasher 100 = 1448
(budget 700-1400; +48 over, approved by the lead up to ~1500 for the rounded handles).
Checks: 0 non-manifold / loose / degenerate per part; X-mirror exact on all parts; component gaps 0; staves/board on z=0;
lid bottom = barrel top 0.585; rod-to-grommet clearance 9.7 mm (rod apothem 16.2 mm, grommet 25.9 mm, lid hole 27.5 mm).
Dasher slides along local Z (Unity Y): up to 0.49 m (cross reaches the lid), down 0.04 m (cross reaches the bottom board).
FBX re-import: 4 nodes (root + Body/Lid/Dasher), 1448 tris, dims 0.449/0.449/1.0, texture found in FMS_Workshop_STA_03.fbm (256x256).
