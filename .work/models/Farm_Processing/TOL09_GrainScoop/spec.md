# TOL-09 Grain scoop

## Lead revision 2 ? current deliverable: SHIP
Closed the collar completely: solid octagonal sleeve with front and rear caps, no bore, no visible arch or hole from any direction. Kept 55 mm across flats; rear face Y=0.054, front face follows the back wall slope exactly (Y=0.025+0.1*(Z-0.025)), giving about 25 mm length near the top. The contact face is flush to the outer back wall, not floating.
Lowered grip and sleeve axis together from Z=0.070 to Z=0.0525 m. Sleeve spans Z=0.025..0.080 m and overlaps the back wall up to its Z=0.075 top edge, leaving just 5 mm above the rim. Grip size, swelling, chamfer, colors and length stay as approved. Overall dimensions now 0.150 x 0.320 x 0.080 m due to lowered grip axis.
164 tris total (shell 76, sleeve 28, grip 60), below 250. Ground-centred source pivots retained, min Z=0; all topology, symmetry and contact checks zero, problems []. Re-exported the same FBX, Blend and atlas files and re-rendered the same 1280x800 preview. FBX re-import verifies 2 nodes, 164 tris, matching dimensions, unit scale, min Z=-0.0 and texture found True; validation.log replaced with current evidence.
Inspected front, side, rear, bottom, three-quarter check and full final preview: no collar hole, wall gap or floating sleeve. Verdict SHIP. Only Unity-side import remains unverified; no requested work remains. Temporary QA retained for coordinator cleanup.


## Lead revision 1 (superseded by revision 2)
Rebuilt collar as a genuine closed annular octagonal ring, 55 mm across flats and 25 mm long, centered on the grip axis at Z=0.070 m. Bottom Z=0.0425 m; no truncation or flat-bottom cut. Its front face seats 1 mm into the rear wall; rear check render confirms the complete ring around the grip.
Shortened trough rear station spacing from 0.215 to 0.190 m (59.4% of overall length), preserving its cross-section, rim, open mouth and dark interior. Grip is now 0.130 m from its seated start to end (40.6% including the portion inside the collar; 0.106 m exposed beyond collar), 35 mm across flats at collar, swelling to 45 mm before a chamfered end. Uses #7A5233 / #9C6B44 side-face pair, with dark end.
Final total **200 tris**: shell 76, true collar 64, grip 60, within 250. Dimensions **0.150 x 0.320 x 0.0975 m**, root/Body bbox-ground-centre pivots and identity source transforms, min Z=0. Printed topology/mirror/contact checks all zero, problems [].
One requested fix round: reference comparison + 128 px thumbnail and rear collar view inspected; final 1280x800 preview inspected. Existing FBX/FBM/texture/Blend/preview paths overwritten, no new art files. FBX re-import two nodes, 200 tris, matching dimensions, min Z=-0.0, unit scale and texture found True. See validation.log.
Verdict **SHIP**. No remaining requested changes; Unity import remains unverified. Temporary QA files retained for coordinator cleanup as requested.


## Reference and planned geometry (before build)
Reference TOL-09.png is 1374 x 1145 px. Approximate projected key points: lip midpoint (300,932), back/collar junction (941,419), grip end (1161,159); body axis ~820 px versus exposed grip ~340 px (perspective dependent). Lip span (135,843) to (449,1026) ~362 px; rim thickness 30-40 px against body width ~510 px = about 0.010-0.012 m at 0.15 m width. These projected measures establish a body/handle length ratio near 2.2 and 8% thick walls.
Features: broad open trough, sloping side walls, chamfered elongated plan, flat floor and rim, low mouth facing -Y, closed back; red octagonal collar; short darker swelling octagonal grip with chamfered end. Empty dark inner floor must read at thumbnail scale.
Initial planned size X/Y/Z: 0.150/0.320/0.075 m. Body Y -0.160..+0.055 (0.215 m); grip finishes +0.160; collar 0.024 m including 4 mm seating; walls 0.012 m at rim; base 0.012 m; grip diameter 0.039 m across flats. Catalogue height 0.100 is reduced to 0.075 for reference proportions and lying orientation.
Material class: flat palette, 256x256 4x4 atlas, 1 material. Wood #B5835A outside, #9C6B44 walls inside and #7A5233 floor; #C8473B collar. Cells 0-12 as common palette, no noise.
Anchor: TOL-03 paddle in TOL_Tools: lying convention, red collar, oct_rod(), center_on_ground(), registry renderer, checks and exports copied locally; processing_common imported read-only. TOL_Tools contains no separate render_preview.py; renderer is embedded in build_tools.py.
NOT modelled: grain/product, table, decoration, moving parts.
Root FMS_Workshop_TOL_09 with one child _Body. Pivot bbox ground centre, identity transforms, min Z=0. No tilt: bowl flat on bottom; handle suspended above floor.

## Compare rounds
Round 1: compare + 128 px viewed. Worst differences: grip/collar hidden behind high back wall; exterior side lacks the broad lower facet; camera too elevated. Fix: raise axis to 0.077..0.080 m (final height near catalogue 0.100), add broad lower chine, lower view elevation to 31 degrees. Geometry before revision: 148 tris, zero topology/contact errors.

Round 2: compare and thumbnail viewed. Raised collar now visible, open floor clear and lower exterior facet reads. Remaining differences: grip swelling is too subtle; red collar slightly undersized relative to body. Fix: neck radius 0.0145, swelling 0.023 m and red collar radius 0.024 m. No other silhouette changes needed.

Round 3: compare sheet + 128 px thumbnail + top view inspected. All signature shapes read, clear empty interior and open mouth, red collar and swelling grip. Only nitpicks: simplified planar interior, more regular symmetrical silhouette than painted reference. Grain intentionally absent. Final target matches catalogue 0.150/0.320/0.100 m after raising handle. Final preview and export verification passed.


## Original build evidence (superseded by lead revision above)
Final size X/Y/Z 0.150/0.320/0.100 m (rounded to mm), catalogue matched after grip revision. Min Z=0, root and Body pivot bbox ground centre (0,0,0), identity source transforms, front -Y, handle +Y.
Single Body 164 tris versus 100-250 budget: shell 76, red collar 28, grip 60. One material M_FarmProcessing_TOL09 and 256x256 atlas T_FarmProcessing_TOL09_BaseColor.png, centered palette-cell UVs.
Printed checks: non-manifold 0, loose 0, degenerate 0, mirrorX 0.000000, worst gap 0.00000, problems []. Normals recalculated; flat shading. SNAP not applicable to handheld prop.
FBX re-import: 2 nodes (EMPTY root and MESH child), 164 tris, dims 0.150/0.320/0.100 m, min Z=-0.0, unit scale [1,1,1]; FBM texture found True, 256x256. Standard pipeline axis conversion appears as X rotation 90 degrees in Blender re-import. Unity import not verified.
Three reference comparison rounds including 128 px thumbnails inspected; top/front/side/rear/bottom views inspected and final 1280x800 preview inspected. No noise, pole fans, floating parts or grain. Remaining nitpicks: simpler planar interior and regular symmetry versus painted reference.
Outputs under art/Farm_Processing/: Meshes/FMS_Workshop_TOL_09.fbx; Meshes/FMS_Workshop_TOL_09.fbm/T_FarmProcessing_TOL09_BaseColor.png; Textures/T_FarmProcessing_TOL09_BaseColor.png; Blend/FMS_Workshop_TOL_09.blend; Previews/FMS_Workshop_TOL_09_Preview.png (one preview).
Rebuild headless via build_grain_scoop.py -- export with PYTHONUTF8=1. validation.log records final checks/export/re-import. No Unity Assets touched. Verdict SHIP; only Unity import remains unverified. Time spent approximately 12 minutes.

Cleanup note: automatic approval review rejected Remove-Item of the verified task-specific temp folder C:/Users/Sergv/AppData/Local/Temp/FarmProcessing_check/TOL09 as blocked by policy; temporary QA PNGs therefore remain there. No deliverable/check is affected.
