# PRD-07 Jam pot under cloth

Reference measured at 1374 x 1145: cap x322..1027 y109..459; cord y393..507; skirt x248..1108 y420..668; body x282..1062 y590..1060; knot x700..837 y436..552; tails end y748/785. Total silhouette approximately 860 x951 pixels. Body widest near y730 (about 40% height from bottom), base width about 545 px. Reference body is wider than its own height, unlike MarketFarm tall straight Jam_Jar_v2 (inspected).

Features: squat opaque red 12-sided ceramic belly, flat base; plain cream faceted dome with two radial transitions; thick ruffled skirt with twelve tips alternating longer/shorter; brown round-section neck cord, front-right chunky knot, two flat hanging tails differing by 10 mm. No label, checker pattern, transparency or moving parts.

Initial dimensions before build (metres): pot base radius .060, belly .080 at z .066, shoulder .060 at z .139; cloth neck z .134 r .061, dome .180; skirt hem .098/.106 with valleys .113, maximum radius .082. Cord diameter .012, neck radius .064. Skirt thickness .0015, outside vessel at least .002 in its lower region. Catalogue .16/.16/.20; target .164/.164/.180 follows reference's squat silhouette (height -10%, cloth overhang +2.5%). Front -Y, ground-centre pivot (0,0,0).

Material: own 256px padded 4x4 palette, single M_FarmProcessing_PRD07; cells 0-9 retain pack palette, dedicated cells 10-15 for fruit red light/dark, cream light/dark, cord light/dark. No noise. Anchors: TOL_Tools cheese mold/cut wheel Part/loft and per-item palette; STA05 export/check/render conventions. Shared processing_common imported read-only.

Not modelled: hidden jam/interior cavity, cloth weave, knot loops/thread grooves, label, LOD1, collider. Original procedural geometry only.

## Compare rounds
See the three recorded rounds below.

## Verification
See final verification below.

Round 1: body reads narrower than reference, dome too conical, knot reads as a cube and tails spread too far at their attachment. Fix: reduce vertical scale 6%, lower preview elevation to 20 degrees, widen flat cap plateau, replace knot with a six-sided solid, bring tail roots together. Four-angle inspection: all surfaces closed and skirt offset clean; 128px silhouette distinct from MarketFarm.


Round 2: silhouette now near reference, but skirt valleys cut too deeply and knot still presents a rectangular side. Fix: valleys .116 -> .110 and shorter tips .106 -> .104; turn knot axis radial so six-sided face reads at front, thicken it to 24 mm high. Final dimensions .164 x .167 x .1692 m: reference silhouette chosen over catalogue .20 m height (-15.4%); actual pot is .160m wide below cloth and .1307m tall (wider than tall). Tail length difference after vertical fit 9.4mm.

Round 3/final gate: inspected side-by-side reference, 128px thumbnail, four angles, and final 1280x800 preview. Knot visibly attached, plain cream skirt has twelve tips, red opaque belly and unlabelled silhouette remain distinct from MarketFarm. Remaining differences: skirt folds more angular; knot a simplified hexagonal solid rather than detailed overhand weave; cap plateau has six vertices to stay within budget. QA: SHIP WITH NOTES (visual simplifications and documented size deviation).

## Final evidence
- Body 448 tris / budget 200-450: pot 92, thick skirt 144, dome 56, four-facet cord 96, knot 20, each tail 20.
- Size X .164, Y .167, Z .1692 m; min Z 0; root and Body pivot (0,0,0), ground bbox centred, identity source transforms, no moving parts.
- Non-manifold 0, loose 0, degenerate 0; mirrorX 0 (asymmetric knot/tails excluded); contact gaps 0, problems []; SNAP N/A standalone prop.
- FBX re-import: 2 nodes (empty root + Body), 448 tris, size .164/.167/.169, min Z 0, scale 1. Texture found 256x256 in own .fbm folder. Standard FBX axis conversion gives 90-degree X on Blender re-import; Unity import unverified.
- Single M_FarmProcessing_PRD07; atlas cells 0-9 unchanged, dedicated food/cloth/cord cells 10-15. UVs deliberately collapsed to padded cell centres, flat shading.
- Outputs under art/Farm_Processing: Meshes/FMS_Workshop_PRD_07.fbx; Meshes/FMS_Workshop_PRD_07.fbm/T_FarmProcessing_PRD07_BaseColor.png; Textures/T_FarmProcessing_PRD07_BaseColor.png; Blend/FMS_Workshop_PRD_07.blend; Previews/FMS_Workshop_PRD_07_Preview.png.
- Repro scripts and numeric logs in this folder; check images only in TEMP/FarmProcessing_check/PRD07, cleaned after inspection. Exactly one art preview. Elapsed approximately 6 minutes; no Unity Assets touched.


