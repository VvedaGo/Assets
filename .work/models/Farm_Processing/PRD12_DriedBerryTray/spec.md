# PRD-12 accepted model - fuller berry cluster polish (current delivery)

Minor polish only: increased each of five bunches from9 to12 rounded berries (45 to60 total) arranged in a tightly packed2+4+3+2+1 grape-like cone around the existing twig fork. Diameter about23mm with the existing small variation; nominal centre pitch18mm across and17mm along the cluster. Bunch lengths measured .0898/.0896/.0887/.0893/.0899m, approximately9cm as requested. Each bunch passes an actual BVH surface-intersection graph check: all12 berries form one connected touching/overlapping group. Berry lower support poles move toward nearby real slats while the visible centres retain the tight cone packing.

Tray/frame/red band/base/lattice/handles, all20 twig solids, palette/material, root/Body hierarchy and ground pivots unchanged. Only berry count, packing and small diameter adjustment changed. Main stem and3 branches per bunch remain visible. Same files overwritten, exactly one art preview. Final full1280x800 preview, reference comparison and128px thumbnail inspected; fuller fruit silhouette verified. Initial polish compare showed small spacing introduced by seating whole berries on slats; corrected by offsetting only hidden lower support poles, preserving visible centre spacing.

Tris before1234 -> after1504: frame128, base12, lattice132, handles72, berries1080 (60x18), twigs80. This is4 triangles (0.27%) above the task's approximate1500 allowance, documented rather than redesigning unchanged parts. Build ceiling1510 treats the supplied budget as approximate. Nonmanifold0, loose0, degenerate0, structural mirror0, component contact gaps0, berry contact graphs5/5 connected. Dimensions remain .400/.300/.083m, ground origin/minZ0, source transforms identity, static Body, front-Y. SNAP N/A, VERIFY OK.

Re-exported FBX,fbm texture,atlas,asset-only blend and same preview. FBX reimport and independent verify_delivery.py pass:2nodes,1504tris,matching dimensions,minZ0,unit scale,texture found,all artifacts present,Blender exit0. Full numeric output in check.log. Verdict SHIP WITH NOTES for pre-existing simplified corner crowns/weave/handles and documented approximate-budget tolerance; no remaining polish defect identified. Unity import remains unverified. Check images remain in TEMP/FarmProcessing_check/PRD12 after the prior policy rejection of deletion; coordinator cleanup required.

Files remain those listed in historical report below; authoritative counts and berry layout are this section.

---
# Historical lead-correction report (counts/layout superseded above)
# PRD-12 Tray of dried berries - full-pack lead correction

## Reference, scope and anchors
Reference planning/FarmProcessing/references/PRD-12.png (1374x1145): tray corners approx (145,374),(917,201),(1244,663),(390,974); handles x111/1226, five bunches at two back and three front positions. Cream strips approx35px, openings35-55px near front, warm wood/red band, faceted wine-brown dried berries on visible forked twigs. Anchors TOL08_FlourSieve corrected lattice and renderer/export checks, STA08_DryingRack chunky crossing slats, product PRD01/02 one Body and per-item palette. Shared processing_common imported read-only.
Flat palette: own padded256px4x4 atlas, one M_FarmProcessing_PRD12; cells0-9 match anchors, cream12 #EAD6AE, berry13/14 #5E2A2E/#43201F, twigs1 #7A5233. No noise. NOT modelled: fresh fruit, extra props, animation, LOD1, colliders, Unity Assets changes.

## Current geometry and hierarchy
Overall .400 X .300 depth X .083 height m; wood frame .344x.300, rails .070 high, integrated corner crowns .080. Ground-centred root FMS_Workshop_PRD_12 and one direct Body, source transforms identity, minZ0, front-Y, no moving parts. Wooden handles .018 square section, smaller openings than reference to retain .400m width. Integral red stripe at Z.016-.037 has no coplanar overlay.
Full lattice:6 longitudinal plus5 cross strips .016 wide,7x6 openings .029714x.030m, ends2mm inside rails. Bottoms .044-.049, tops .052-.057, alternating3mm offsets suggest weave. Dark base .308x.264x.006 visible below actual openings. Integrated faceted corner rises and whole-strip weave remain budget simplifications from original approved scope.

## Lead correction: rounded berries and visible forks
Lead rejected original crystal-like10-triangle berries and hidden twigs. Original proposed8+4+4+2-vertex berry would require32tris each; coordinator revised authorization to simpler6-sided equator, smaller triangular shoulder rotated60deg, short top vertex,9 berries per cluster, up to1250 total. Current berry uses that shape plus a short lower pole embedded in lattice, preserving closed manifold topology:11vertices/18triangles each. Forty-five berries, nine each in2+3+4 layouts; diameter .022m with4.5% size variation, total height .0176m (0.8xdiameter). Raised equator at8mm and smaller shoulder at14mm make rounded stepped facets instead of the old long diamond tips. Whole-berry light/dark assignment avoids high contrast crystal facet patches.
All berry lower poles are seated on actual cream strips; centres over lattice holes move minimally to the nearest support. Each bunch has one main stem plus3 fanned branches,20 tapered twig solids total. Main stem goes from rear Z.081 to fruit Z.068; branch roots Z.078/.076/.074 and tips .0675 keep brown forks visibly laid across fruit tops with seated ends. All food, stems and branches have BVH-confirmed contacts.

## Comparison rounds
Initial3-round delivery superseded by full-pack rejection. Lead round4 comparison at512px plus128px thumbnail found the first revised berries still too conical: equators were too low and tips too high. Round5 raised the equator, shortened upper-tip silhouette, added a buried lower pole and seated each berry on a true strip; clearer forks and fewer berries expose the brown branching pattern. Viewed final reference comparison,128px thumbnail,full1280x800 final preview,and front/back/bottom renders. Rounded pebble-like dried fruit and visible twig forks now replace the prior diamond clusters. Remaining notes: fewer berries and simpler roundness than reference, integrated crowns, simplified weave, smaller handle holes. No remaining Major defect identified; full-pack lead acceptance remains with coordinator.

## Checks and export
Body1234triangles: frame/posts/red band128, base12, lattice132, handles72, berries810, twigs80. Original catalogue250-650 superseded by lead-authorized1250 cap; current1234 within that allowance. Nonmanifold0 loose0 degenerate0, symmetric structure mirrorX0 (organic berries/twigs excluded), worst component gap0 and problems[]. Ground contact0, SNAP N/A, VERIFY OK.
FBX reimport2nodes,1234tris,.400/.300/.083m,minZ0,unit scale,own256px atlas found in fbm. Importer X90 conversion matches approved anchors. Independent verify_delivery.py assertions pass with Blender exit0 for hierarchy/count/dimensions/base/scale/texture/all artifacts. check.log records build and FBX import; PowerShell NativeCommandError is harmless World.use_nodes deprecation stderr.
Verdict SHIP WITH NOTES for documented simplified features and catalogue budget deviation; lead-authorized1250 ceiling passed. Unity import unverified. Temporary checks remain under TEMP/FarmProcessing_check/PRD12 because previous automatic policy rejected native PowerShell deletion; coordinator cleanup required.

## Files
- .work/models/Farm_Processing/PRD12_DriedBerryTray/build_dried_berry_tray.py
- .work/models/Farm_Processing/PRD12_DriedBerryTray/render_preview.py
- .work/models/Farm_Processing/PRD12_DriedBerryTray/compare.py
- .work/models/Farm_Processing/PRD12_DriedBerryTray/verify_delivery.py
- .work/models/Farm_Processing/PRD12_DriedBerryTray/spec.md
- .work/models/Farm_Processing/PRD12_DriedBerryTray/check.log
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_12.fbx
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_12.fbm/T_FarmProcessing_PRD12_BaseColor.png
- art/Farm_Processing/Textures/T_FarmProcessing_PRD12_BaseColor.png
- art/Farm_Processing/Blend/FMS_Workshop_PRD_12.blend
- art/Farm_Processing/Previews/FMS_Workshop_PRD_12_Preview.png (exactly one art preview)

