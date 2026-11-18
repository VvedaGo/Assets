# PRD-17 hanging smoked ham

Reference measured at 1374x1145 pixels: complete prop approx x384..885, y50..1084; lower meat mass x384..885, y503..1084; shank/knob x680..876, y275..510; loop x670..802,y50..365; cut x384..776,y638..1083. Width/height image ratio 0.485; loop ~0.12m tall including overlap, body/knob ~0.30m.

Target: width 0.20, depth 0.16, total height 0.40m. Broad 12-sided pear body, six broad lower rings narrowing into a 0.045m shank with tilted rounded knob. Cut is built by removing skin with a plane, then closing that SAME boundary with a 0.012m cream fat annulus and red polygon surface; no decal or overlapping skin. Two tight hex-section 0.012m cord wraps and tall faceted loop.

Material class: flat palette, one M_FarmProcessing_PRD17 with 256px 4x4 own atlas. Cells 0-9 match shared pack; food/twine overrides at 10-15. Flat shading throughout, no texture noise.

Anchors: TOL_Tools build_cheese_mold/build_cut_wheel (connected cut surface, food palette), shared processing_common helpers, STA05 render_preview template. Farm Market Ham differs: lying with bone end; this prop hangs shank-up with golden smoked skin and integrated cord; no geometry copied.

Pivot exception requested: root and body origin at TOP outer cord loop; mesh world min z=0. Hang point height documented after numeric verification. Front -Y, no moving parts. NOT modelled: hook/rack, bone, smoke, loose fibres, floor, animation, collider or additional LODs.

Final round 3: tall cut, restored depth, broad red regions. Viewed matched-height comparison, final preview, 128px thumbnail and back/left/right views. QA SHIP WITH NOTES: skin brighter, red regions fewer and wraps more level than reference.

Final evidence: 596/600 tris (ham 284, wraps 96 each, loop 120), size X/depth/height 0.205/0.156/0.402474m, min z=0. Root and Body pivot at actual top outer cord vertex (0.03263137,-0.012,0.40247354)m; hang-point height 0.40247354m. Topology non-manifold/loose/degenerate 0, contacts gap 0, problems empty; mirror intentionally skipped for asymmetric cut/knob, SNAP not applicable. Cut shares skin boundary; fat rim raised 1.5mm; flat normals, padded cell UVs, no noise/pole fans. FBX re-import 2 nodes, same 596 tris and dimensions, texture found 256x256, unit scales; pack-standard conversion reports +90deg X on re-import. Unity import unverified.

Outputs: art/Farm_Processing/Meshes/FMS_Workshop_PRD_17.fbx plus matching .fbm/T_FarmProcessing_PRD17_BaseColor.png; art/Farm_Processing/Textures/T_FarmProcessing_PRD17_BaseColor.png; art/Farm_Processing/Blend/FMS_Workshop_PRD_17.blend; art/Farm_Processing/Previews/FMS_Workshop_PRD_17_Preview.png. One M_FarmProcessing_PRD17, own 256px atlas, cells 0-9 unchanged. Reproduce headless Blender with build_smoked_ham.py -- 3. Detailed numeric log round3.log. Approx work time 15 minutes.

Round 1: topology/contact all pass, 590 tris. Worst differences: cut too small and round, red field too uniformly divided, and cord wraps visually narrow relative to mass. Fix: cut plane moved deeper into lower mass and tilted downward to make the larger lower-left cut; normalization keeps min z=0.

Round 2: 590 tris, all topology/contact checks pass. Worst differences: cut faces downward and reads as a short oval, depth 0.145m instead of 0.16m, and meat has too few large regions. Fix: make cut plane closer to vertical, restore back depth, and keep broad red facets instead of adding noisy detail.
