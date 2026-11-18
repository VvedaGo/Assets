# PRD-15 Ceramic oil bottle

Material class: flat palette. Anchor: TOL-12 bowl (red stripe integrated into ring facets; thick cream rim), TOL-14 rolling pin (clean low-segment revolution and wooden ends). TOL_Tools has its renderer embedded in build_tools.py, so render_preview.py is extracted from that function. Shared processing_common.py is imported read-only.

Reference pixel landmarks (1374x1145): stopper top y56; lip top y143, underside y240; neck lower y380-400; shoulder upper y490-560; red front top y660, bottom y835; base front y1085; body maximum x443..926. Perspective moves rear ring edges upward. Measured width/height=483/1029=.469 before perspective correction.

Planned dimensions: body apothem .0571 m, 10 sides, bbox .120 x .1141; z0 base, chamfer to .012; straight body to .166; lower shoulder to .190; upper shoulder to .223; neck apothem .022, z.223-.283; lip apothem .028, z.283-.298; inner mouth .0195, recess floor .289; octagonal stopper bottom .289 top .320, visible .022, top chamfer .002. Band initially .090-.146, as measured in the reference (28-46% versus task approximate 40-58%); compare visually before final. One child Body, no moving parts, root/pivot (0,0,0), front -Y.

NOT modelled: label, text, oil, transparent glass, full hollow bottle, separate band shell, loose stopper motion, extra props.
Catalogue deviation: regular decagon bounding box is .120 x .1141 x .320, apothem ~.057, matching requested ~.055; depth 5% below catalogue because 10-sided rotational symmetry precludes equal orthogonal bbox dimensions. Stripe position follows measured reference rather than the task's approximate percentage.

Compare rounds: pending. QA pending.

Round 1 (compare + 128px viewed): worst differences were slender body/neck, undersized lip, and overbright cream. Widened body apothem .0571 to .071, neck .022 to .027, lip .028 to .034, stopper .019 to .023; reduced sun from 3.4 to 2.6 and camera elevation from 22.5 to 18.7 degrees. Reference silhouette wins over catalogue: revised bbox about .149 x .142 x .320 m (24% width deviation). Stripe is correctly placed visually at .090-.146 (28-46%).

Round 2 (compare + 128px viewed): silhouette and lip now close. Worst remaining differences: lower shoulder cream ramp was too tall, neck-to-shoulder transition slightly high, and reference red slightly warmer under its lighting. Lowered intermediate shoulder from .190 to .181 and neck start .223 to .219; retained specified exact red palette and 22mm exposed stopper. Colour difference is a lighting nitpick.

Round 3 final: viewed comparison, full final preview, back/side/top and 128px thumbnail. Remaining nitpicks: reference body marginally wider in normalized comparison, cream/red lighting slightly different. QA SHIP WITH NOTES for reference-led size and stripe deviations. No noise, pole fans, floating parts, or overlapping band shell.
Final dimensions .149308 x .142 x .320 m; body apothem .071, neck .027; shoulder rings z.166/.181/.219, collar .283-.298, mouth floor .289, stopper top .320. Root and Body pivots ground centre (0,0,0); identity source transforms; minZ=0. 336 tris Body (ceramic 276 + stopper 60), budget 200-450, one material M_FarmProcessing_PRD15 with 256px atlas. Non-manifold/loose/degenerate 0, mirrorX below 1e-16, worst contact gap 0, no problems, ground SNAP OK. FBX re-import two nodes, 336 tris, same world dimensions, minZ approximately 0, scales 1; texture found in .fbm at 256px. Common FBX conversion reports 90-degree X rotations on re-import; world geometry correct. Unity import not verified. Evidence in round1-3.log and checks.json. Approximately 10 minutes.
