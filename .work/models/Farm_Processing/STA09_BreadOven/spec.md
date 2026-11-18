# STA-09 Bread oven

Reference measured in 1374 x 1145 pixels: silhouette x246..1128, z30..1115; cap width234, dome width650, door width290, arch width480; stand top about y720 and stone top y650. Height ratios: stand 0.34, stone 0.08, dome 0.36, chimney 0.22. Perspective makes front legs longer on screen.

Feature list: four thick splayed chamfered wood legs, red square cap plates, rectangular top frame and four low stretchers; ten grey chamfered stone sectors; cream 12-sided five-ring plaster dome; nine radial brick voussoirs and two jamb courses; rounded grey metal door, two left hinges with hex bolts, right D-handle; red octagonal collar, two staggered octagonal stone chimney courses, hollow octagonal cap.

Dimensions before build: overall target 1.50 x1.44 x1.80 m; stand top 0.64; stone ring 0.64..0.78 outer radius0.72; dome base0.78 radius0.64, crown1.44; arch centre1.015 inner radius0.265 outer0.38; door hinge(-0.265,-0.66,0.79). Chimney collar1.40..1.49, stack1.49..1.73, cap1.71..1.80.

Material class: flat palette, 256px 4x4 own atlas, one material; cells0..12 retained from STA06, cells13 stone #A7A39A,14 stone dark #8C8B88,15 brick #D0583F. Cream #F2E6C9/#DCC9A0; wood #B5835A/#7A5233; metal #8E959B/#6E757B.

Anchors: STA07 parametric radial arch, block bevels and slabs; STA06 splayed legs, red cap plates, flat palette and check/export workflow. Shared processing_common.py is read-only.

Hierarchy: FMS_Workshop_STA_09 identity root at ground centre; direct children _Body and _Door. Door pivot vertical left hinge axis, front -Y. No nested moving nodes.

NOT modelled: bread, fire, smoke, floor, text, interior brick lining, collision, LOD1. Interior is a dark openable chamber with solid rear wall, not a solid dome behind the door.

Catalogue deviation: depth 1.44 instead of1.40 for ten-sector stone ring, reference proportions take priority. Round comparisons and numeric results appended after inspection.

## Final acceptance (supersedes initial dimensions)
Round3 compare, full1280x800 preview,128px thumbnail, front, side, rear and100deg open-door views inspected. No further geometry changes required. Remaining minor differences: plaster arch bridge is more pronounced from the side; dome facets/chimney joints more angular; pack plaster brighter and metal cooler than reference lighting. No noise, pole fans, detached parts or scope creep.

Body2492 + Door410 =2902tris (budget2200..4000). Closed dimensions1.506 x1.470 x1.800m including D-handle; stand depth1.426m. Root/Body pivot0,0,0; Door(-.273,-.665,.789), vertical localZ hinge, outward swing-110..0deg, visually tested at-100deg. Identity rotations/scales before export.

Both parts: non-manifold0, loose0, degenerate0, gaps0; BodyX mirror0 excluding left hinges; asymmetric door excluded from mirror test. Door-body hinge overlap asserted. Stone bottom.64 contacts support caps, stone top.78 equals dome base.78; grounded legsZ0. SNAP not applicable to freestanding station. UV overlap intentional at flat palette cell centres.

FBX re-import: root empty + Body + Door;2902tris; dimensions1.506 x1.470 x1.800m; minZ0; Door translation preserved; texture found in.fbm at256x256. Blender re-import90degX node rotations follow shared exporter axis conversion; Unity import unverified.

Outputs under art/Farm_Processing: Meshes/FMS_Workshop_STA_09.fbx, Meshes/FMS_Workshop_STA_09.fbm/T_FarmProcessing_STA09_BaseColor.png, Textures/T_FarmProcessing_STA09_BaseColor.png, Blend/FMS_Workshop_STA_09.blend, Previews/FMS_Workshop_STA_09_Preview.png. Own qa_log.txt preserves final export/re-import evidence. Own temporary check renders deleted after inspection.

Verdict SHIP WITH NOTES: minor reference differences above; Unity import remains unverified. Three comparison rounds, approximately20minutes.

Round1: arch visibly too thin relative to dome; incorrect dark exterior triangle from centroid-only chamber colouring; camera too far left. Increased outer arch radius .38 to .425 and plaster support to .443, classify chamber faces by inward normal, yaw reduced to19deg and elevation18deg. Body/door 2492/410=2902 tris; topology0, mirror0, gaps0; thumbnail readable.

Round2: 2902 tris, all mesh/mirror/contact checks zero. Back and door-open100deg views inspected: chamber open, hollow chimney readable, no detached parts. Three remaining differences: cream bridge halo too wide, handle thin, footprint too deep (1.506m). Reduced bridge to .430, handle to45mm, moved leg Y centres40mm inward; camera elevation21deg for round3. Stand feet now only4cm splay in depth relative to top caps; tops still overlap caps.
