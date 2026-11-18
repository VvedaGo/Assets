# PRD-13 Bread rolls on a baking tray

Reference measurement (1374 x 1145 px): tray extreme corners approximately (109,520), (934,261), (1267,565), (409,899). Long edge 865 px, depth edge 439 px under foreshortening; front rim outer/inner separation 23-35 px. Rolls occupy about 80% of tray length; pale lower band occupies 42-46% of the visible bread height; exactly two diagonal pale cuts per dome.

Target before building: tray 0.450 x 0.300 m, sheet floor 0.004 m, sloped rim top Z=0.026 m (22 mm above floor), rim thickness 0.004 m and corner chamfer 0.018 m. Three ten-sided rolls, nominal 0.130 X x 0.110 Y x 0.075 Z, centres X=-0.121,0,+0.121, floor Z=0.004; 9 mm overlap baked into one union mesh. Crumb/crust boundary Z=0.038 (45% bread height); crown top Z=0.079. Two oblique V cuts per roll, about 0.065 long, 0.012 wide, 0.007 deep. Budget <=700 triangles; no moving parts.

Material class: flat palette, faceted normals, one material/256px 4x4 atlas. Cells 0-9 pack-identical; 10 crust shade #C97E3D, 11 tray dark #4E4643, 12 crumb #EFD3A0, 13 crust #E09A55, 14 tray light #6E6560, 15 score interior #F3DDB0.

Anchors: TOL_Tools/build_tools.py PRD-01/02, shell/loft construction, single Body hierarchy, per-product palette and verification; STA05_JuicePress/render_preview.py camera/light conventions. Own roll geometry, no copying existing breads. Not modelled: crumbs, baking paper, handles, moving parts, textures/noise.

Catalogue deviation: reference tray depth 0.300 instead of 0.350; height 0.079 instead of 0.120 follows the specified reference roll height. Root + Body at ground bbox centre, front -Y, identity transforms. Unity import is outside this task.

Round 1: side-by-side and 128px viewed. Worst differences: rolls too shallow along Y relative to tray, tray outside reads paper-thin, scoring too steep in projection. Fix: roll depth 0.165m (reference visual proportion takes precedence over approximate 0.110), crown fuller; solid outside rim with 26mm silhouette height and 12mm lip width; score direction rotated -20 degrees in XY.

Round 2: side-by-side and thumbnail viewed. Worst differences: rolls still undersized against tray, baked joins too narrow, cuts too horizontal and tray floor too light. Fix: roll X width 0.145m/depth 0.180m with 24mm maximum overlap (union removes internal skins), scoring turned +6 degrees, dark floor and lighter thick outer rim; lower camera elevation to 29 degrees. Crumb height remains exactly 45% (34mm of 75mm).

Round 3: comparison, 128px thumbnail, back/side/top views inspected. Six pale V grooves visible, bread is joined with no internal overlapping skins, chamfered dark tray reads clearly. Remaining differences: reference has a more swollen pale side band in projection and slightly broader scores; ours uses a flatter crown and more regular ten-sided facets. No noise, pole fans, floating geometry, mixed smoothing, or extras. QA: SHIP WITH NOTES for these reference-shape differences and documented dimensional deviations. No further modelling rounds.

Final geometry: Tray 76 tris + JoinedBread 436 tris = Body 512/700 (73.1%). Overall X/Y/Z 0.450/0.300/0.079m, ground min Z=0.000, bbox-centre ground pivot (0,0,0), root/body identity, static. Rolls 0.145 X / 0.180 Y / 0.075 height, centre separation 0.121; geometric UNION removes overlapping faces. Score ridge nominal max depth 7mm, nominal width 12mm, tapered ends. Palette cells 0-9 unchanged; UVs deliberately collapse to padded cell centres.

Checks: non-manifold 0, loose 0, degenerate 0, tray mirrorX 0.000000m, contact gap 0, no problems. Bread base silhouette exact X mirror, diagonal score handedness excluded intentionally. Boolean sub-0.05mm slivers cleaned with remove_doubles and dissolve_degenerate. SNAP not applicable (product).

FBX round trip verified: 2 nodes (root EMPTY, Body MESH), 512 tris, dimensions 0.450/0.300/0.079m, minZ ~0, unit scales. Blender importer reports 90-degree FBX axis conversion; Unity import unverified. Texture found at Meshes/FMS_Workshop_PRD_13.fbm/T_FarmProcessing_PRD13_BaseColor.png, 256x256. Final 1280x800 preview opened after export. Blender completed normally; PowerShell captures World.use_nodes deprecation stderr as NativeCommandError despite successful export.
Cleanup limitation: automatic command policy rejected deletion of C:/Users/Sergv/AppData/Local/Temp/FarmProcessing_check/PRD13 (blocked by policy); temporary QA PNGs remain there for coordinator cleanup.

## Accepted-model minor polish
Only requested scoring and joins changed: six V grooves now run exactly 35 degrees to X (the task's roll length direction), two parallel cuts per roll. Neighbour centres moved inward 2.5mm to spacing 0.1185m, giving 26.5mm maximum overlap, approximately 2cm. The existing boolean union shell is split at the two joins to assign a 5mm shared pale crumb seam using existing palette cell 12; no overlays or coplanar faces. Tray, roll profiles, material/palette, hierarchy, source pivots and preview camera retained.
Tris before 512 -> after 592/700: Tray 76 unchanged, JoinedBread 436 -> 516. Non-manifold/loose/degenerate 0, tray mirror 0, contact gap 0, ground Z=0; same dimensions 0.450/0.300/0.079m. Re-exported same FBX/blend/atlas and exactly one preview; opened final 1280x800 preview. FBX re-import 2 nodes, 592 tris, matching dimensions/minZ, unit scales, texture found at 256x256. Atlas SHA256 unchanged: 29BC823D0E21E224B176CAA796C80D3DCBD983BDAC0817100ECD18DBB67B3613. Evidence: polish_export.log. Verdict SHIP (requested minor polish); Unity remains unverified as before.
