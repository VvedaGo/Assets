# PRD-08 Apple slices on a drying tray
Reference: planning/FarmProcessing/references/PRD-08.png (1374 x 1145 px).
Anchor: STA08_DryingRack build, render, specification and preview; shared processing_common imported read-only. Product construction conventions from TOL_Tools cheese builders.

## Measurements and build plan
Reference corner tops approximately (153,430), (946,270), (1217,592), (365,776); projected long rail vector (793,-160), depth vector (212,346). Corner block width ~90px versus ~825px rail length, slat gaps ~7px, slice width ~150px versus tray long edge ~900px. Rail front-face height ~75px; slice sides ~24px. Twelve slices in three rows of four, all concavities pointing +Y. Four chunky wooden rails, four taller chamfered red corner blocks, five dark X-running slats and real air gaps. Pale flesh tops, curved red peel sides, flesh concave sides.
Width .500m, depth .350m; rails .025m thick/.035m high; corner blocks .045m square/.045m high. Floor bottom .006m/top .012m, five .0552m slats with .006m gaps across .300m interior, each extends .001m into rail supports. Slices .090 x .050 x .015m, bottom .012m (exact physical support, no coplanar overlapping top faces), top .027m. X centres -.162/-.054/.054/.162; Y centres -.093/0/.093. Each nine-point crescent prism 32 triangles. Initial tray 284 + food 384 = 668 triangles; final chamfered rails bring tray to 316 and total to 700, ceiling 700.
Material class: one opaque flat palette material, own 256px 4x4 atlas; slots 0-12 retain anchor colours, slot13 flesh #F3DDB8. Flat faceted shading, no texture noise.
Hierarchy: root FMS_Workshop_PRD_08 and one static _Body at ground bbox centre (0,0,0), identity transforms, front -Y. No moving parts.
Deviation: height .045m rather than catalogue .070m to match explicit 35mm rail and slightly taller corner requirement and reference shallow silhouette.
NOT modelled: seeds, grain, loose pieces, animation, collider or LOD1. No extra props.

## Comparison rounds
Three rounds completed below.

Round 1: inspected reference/render comparison and 128px thumbnail. Worst differences: long-edge projected slope too steep, sharp crown-like tips on slices, model framing smaller than reference. Changed camera X component -.55 to -.35 and softened/deepened main slice arc while retaining 90x50mm outline; camera framing will be adjusted after second comparison. Checks: 668 tris; non-manifold/loose/degenerate 0, exact X symmetry and zero support gaps.

Round 2: inspected side-by-side and 128px thumbnail. Main differences: caps too small, rails overly sharp, frame underfilled. Increased cap footprint to 45mm, clipped rail top shoulders by 2mm, increased final framing to 80% and balanced camera azimuth/elevation between rounds 1 and 2. Added exactly 32 triangles to rails; final budget 700. Slice outlines remain 90x50mm; 9 points are needed for faceted outer arc and concavity.

## Round 3 and final QA
Final 1280x800 preview, reference/render comparison, 128px thumbnail and back/side/front views inspected. Four red caps, five real slats and twelve similarly facing crescents with red curved peel read clearly. No visible z-fighting or unsupported food. Remaining minor differences: reference slices are rounder, wood warmer and perspective slightly different. No geometry changes after final rendering.
Final caps are 45mm square, 45mm tall; rail shoulders have 2mm chamfers. Final Body 700 triangles: tray 316 (rails 80, corners 176, slats 60), slices 384 (32 each). Budget 300-700 met exactly.
Dimensions .500 X / .350 Y / .045 Z metres, minZ0. Root and Body pivots ground bbox centre (0,0,0); source transforms identity, front -Y, no moving parts. One own atlas and material M_FarmProcessing_PRD08, slots 0-12 retain anchor colours.
check.log: non-manifold 0, loose 0, degenerate 0, mirrorX .000000, worst component gap .00000, problems []; SNAP/VERIFY OK. Slice bottoms .012m touch slat tops .012m, flesh tops .027m: hidden opposed contact faces touch, no coincident visible tops. Slat support overlap 1mm; real slat gaps 6mm.
FBX re-import: root empty plus one Body mesh, 700 tris, dimensions .500/.350/.045m, minZ0, scale one and correct hierarchy; 256px texture found in own .fbm. Standard 90-degree Blender importer axis conversion matches anchor.
Exactly three comparison rounds. QA verdict SHIP WITH NOTES for documented 45mm versus catalogue 70mm height and minor stylistic differences. No known blocker or major defect. Unity import, collider and LOD1 not verified/outside dispatch.
Files: own build_apple_slice_tray.py, render_preview.py, compare.py, spec.md and check.log; art/Farm_Processing/Meshes/FMS_Workshop_PRD_08.fbx; Meshes/FMS_Workshop_PRD_08.fbm/T_FarmProcessing_PRD08_BaseColor.png; Textures/T_FarmProcessing_PRD08_BaseColor.png; Blend/FMS_Workshop_PRD_08.blend; Previews/FMS_Workshop_PRD_08_Preview.png.

Temporary comparison, thumbnail and angle PNGs removed after visual inspection; only final preview remains in art. Temporary helper setup/refine scripts removed. Build duration approximately 12 minutes.
