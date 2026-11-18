# STA-06 Hand millstones / quern - FMS_Workshop_STA_06

Reference: planning/FarmProcessing/references/STA-06.png (three-quarter front-left, camera ~30 deg yaw to -X, ~20 deg elevation).
Catalogue: "two horizontal circular millstones on a low wooden support, central grain inlet, upper stone with a hand crank and
flour outlet", 0.9/0.8/0.9 m, LOD0 1000-2000 tris, moving parts: upper millstone and crank handle. Economy mode: max 3 rounds.

## Feature list (measured from the reference, R = stone radius = 340 px)
- Two 16-gon stones of equal radius, flat faceted sides, chamfered edges; V-seam between them (dark line).
  Lower stone (warm light grey) ~0.37R tall, upper stone (cooler darker grey) ~0.31R tall.
- Upper stone: central grain-inlet hole (r ~0.26R, real hole through the stone); octagonal cream funnel hopper
  (top r ~0.54R, ~0.75R tall above the stone, thick rim) whose neck sits in a red octagonal collar set into the hole.
- Crank: on the upper stone top at ~0.55R radius, front-right (-45 deg): grey octagonal flange + smaller octagonal nut, square
  grey arm rising, bent diagonally up and running out horizontally past the rim (~1.3R), small grey collar, vertical octagonal
  wooden grip with a chamfered cap (top ~1.1R above the stone top = highest point).
- Flour outlet on the lower stone facet at 67.5 deg from -Y toward -X: red rectangular frame, dark opening, cream U-channel chute
  sloping down and out past the support ring.
- Support: thick 16-gon wooden ring under the lower stone (outer ~1.12R), 4 splayed square legs on the diagonals (top r ~1.22R,
  foot r ~1.3R) ending in chamfered square cap blocks at the ring with a red square plate on the outward face; 4 square
  stretchers low between adjacent legs (~0.5R above ground).

## Material class
Flat palette: own atlas T_FarmProcessing_STA06_BaseColor.png (256 px, 4x4 solid cells), one material M_FarmProcessing_STA06.
Cells 0-12 identical to STA-05/STA-03 (mergeable); 13 stone #A7A39A (lower), 14 stone dark #8C8B88 (upper), 15 stone deep
#66635E (seam chamfers, hole wall, outlet opening). No noise, no grain, no flour dust.

## NOT modelled
Spindle/rynd inside the eye, stone dressing grooves, flour/grain, sack under the chute, diagonal brace under the front cap,
nails/wood grain, floor, text, LOD1, collider.

## Anchors followed
STA-05 juice press (approved preview + build_juice_press.py structure, palette, checks, export) and STA-03 butter churn
(headless build/export/verify/preview script structure, ring()/torus_loft usage, mitred square-section sweep for the arm);
both follow MarketFarm Scale (contact/mirror checks) and Cart (chunky chamfered wood).

## Hierarchy / pivots
FMS_Workshop_STA_06 (empty, ground centre, identity) -> _Base (0,0,0: ring, legs, caps, plates, stretchers, lower stone, outlet
frame, chute), _UpperStone (centre of its bottom face on the axis; stone + red collar + hopper; rotates about local Z),
_UpperStone -> _Crank (pivot = vertical axis of the crank peg at the stone top; flange, nut, arm, collar, grip). The crank is
parented under the upper stone so it turns with it; its own pivot allows a swivel/peg animation. Front = -Y.

## Dimensions / deviations
Catalogue 0.9/0.8/0.9. Built X 0.933 (chute tip on -X; legs alone 0.80) x Y 0.796 x Z 0.900 (crank grip top). The model is built
from ref ratios (stone apothem 0.325, support 0.07 lower than first measured) and then scaled uniformly by S = 1.08 to the
0.9 m height. Stones 0.70 m across. The back-left cap's plate faces away at the preview angle (in the ref it is visible).
The outlet sits on the 16-gon facet at 67.5 deg from -Y toward -X, the crank peg on the front-right diagonal (-45 deg), as measured.

## Compare rounds (preview camera VIEW_DIR (-0.5, -0.866, 0.38), 70 mm; check renders in %TEMP%, deleted)
1. Legs/caps/stretchers thin, flour outlet and chute too small, hopper slightly small -> legs 0.074-0.088, caps 0.122,
   stretchers 0.056, frame 0.144 x 0.10, chute 0.096 wide, hopper rim r 0.188.
2. Crank hub small and thin arm vs ref -> flange r 0.064, nut r 0.042 lower, arm 34 mm. First export: the FBX re-import showed the
   crank wrong (Blender 5.2 exporter bug with bake_space_transform for 2nd-level children) -> crank matrix pre-compensated during
   export only; FBX dump confirms Lcl Translation (0.1375, 0.108, 0.1375), rotation 0.
3. Full preview vs ref: base ~15% too tall relative to the stones (seam-to-foot 0.82 vs 0.70 stone diameters), stretchers thin,
   chute narrow -> support lowered 7 cm, whole model scaled x1.08 back to 0.9 m, stretchers 0.062 at 0.11 m, chute 0.102 wide.
Remaining nitpicks: wood/metal follow the pack palette (ref wood more orange, ref metal neutral grey vs bluish #8E959B); ref chute
seen slightly more frontally; back-left cap plate hidden at this angle.

## Result
Tris: Base 996 (ring, lower stone, 4 legs, 4 caps, 4 plates, 4 stretchers, outlet frame, opening, chute), UpperStone 352
(stone with through-hole, red collar, hopper), Crank 188 (flange, nut, bent arm, collar, grip) = 1536 (budget 1000-2000).
Checks: 0 non-manifold / loose / degenerate per part; X-mirror exact on Base (outlet/chute excluded) and UpperStone; component gaps 0;
legs on z=0; upper stone bottom = lower stone top (0.405), lower stone bottom = ring top (0.2754); crank flange sunk 3 mm into the
stone top, inside the flat top face; chute clears the ring top by 6 mm; collar embedded 1 mm into the hole wall (grain path open).
FBX re-import: 4 nodes, hierarchy root -> Base, UpperStone -> Crank, 1536 tris, dims 0.933 x 0.796 x 0.9, texture found in .fbm.
