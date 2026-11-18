# Full-pack review revision: head and pose (current delivered version)

Supersedes historical notes below. Continuous shell now bends8degrees in XZ, lower .083m bends10degrees toward -Y. Side-opening35mm V mouth has upper snout at x=-.042/z=.016 and lower jaw x=-.025/z=0 before posing. Two6-point curved crescent gill edges follow surface behind eyes and rise5mm. Grey octagonal eye discs20mm diameter, approximately4mm proud. Cord, tail fork, wraps and fins retained. Widest section remains35.3% from mouth; pectorals just behind gill edge.

Final Body588/650 tris: fish140,eyes56,crescents88,dorsal16,ventral16,pectorals32,tail32,wraps88,cord120. Bounds .132/.061/.400m; mouth minZ0; hang pivot and highest cord vertex (0,0,.400). Non-manifold0,loose0,degenerate0,contact gaps0,problems=[]; base bilateral mirror1.23e-17 before intentional head bend; posed Y asymmetry expected; SNAP N/A. Blender exit0. FBX re-import2 nodes,588 tris,same dimensions,minZ0,scale1,256x256 texture found. Same material and atlas.

Final full preview, reference comparison,thumbnail and four views inspected. Head now reads through jaw, eye,crescent and forward pose. Remaining simplifications: angular crescent and flat fin faces. QA SHIP WITH NOTES; lead acceptance and Unity import external/unverified. Same FBX/.fbm/texture/blend and single preview replaced. Numeric evidence build.log; stderr only anchor preview deprecation warnings.

---
Historical notes follow (superseded).
# Lead revision: continuous fish profile (current delivered version)

This section supersedes the initial build notes and counts below. One requested lead-fix round completed: removed separate head and gill patches, replacing them with one watertight continuous octagonal spindle from notched snout through head/body to tail stalk. Head is lower .083m of .278m fish (29.9%). Maximum body width .100m is at z=.098m, 35.3% of fish length from mouth; upper body tapers continuously to .020m stalk diameter. Lower profile rounds through section radii .022/.034/.044/.046m toward the .050m widest section, without the old neck/pinch. Bottom ring has a real V notch and bevelled jaw corners. Gill line is an integrated shared-vertex step ring: radius .046 at z.076, raised to .049 at .079, then .047 at .083 (3mm rise). No separate head shell or gill patch remains.

Eyes are rooted at |Y|=.017 on the existing head face (surface about .020) and end at .023: slightly proud, not floating. Pectoral roots now start z=.087, immediately behind the .079..083 gill line. Cord, tail, other fins, palette and hang pivot retained.

Final current Body 532/600 tris: continuous fish/gill shell172; two eyes56; dorsal16; ventral16; pectorals32; tail32; wraps88; loop120. Overall dimensions .138/.055/.400m, mouth minZ0, exact top-loop hang point (0,0,.400); root/Body origins there, identity rotations/scales and child local translation0. Non-manifold0, loose0, degenerate0, worst contact gap0, problems=[]; Y mirror error6.74e-18; X asymmetry intentional; SNAP N/A. Build exited0. FBX re-import2 nodes,532 tris,same dimensions,minZ0,scale1,256x256 texture found in same .fbm path. One material and atlas unchanged.

Viewed updated full preview, normalized reference comparison,128px thumbnail and front/back/side/top. Old separate-head Major is resolved by shared ring topology and continuous outer profile. Remaining simplifications: broad planar fins, angular mouth/jaw and straight circumferential gill line versus reference's more sculpted contours. Verdict SHIP WITH NOTES; Unity import remains unverified. Re-exported FBX, texture/.fbm, asset-only blend and single final preview at the same paths listed below; source and build.log updated. Temporary check renders removed after inspection.

---
Historical initial-build notes follow (counts/geometry superseded above).
# PRD-16 Hanging smoked fish

Measured reference 1374x1145: object bounds x494..821, y36..1058; cord top y36, tail lobes y200..360, wraps y330..390, body y385..1058. At .40m per 1022px this gives .264m body, .075m visible tail, .115m loop above binding, and projected width .128m including fins. Body width near y690 about 270px; use .10m body and .055m depth (eight-sided laterally flattened section).

Planned geometry: mouth minimum z=0, head/gill z=.00.. .095, spindle to tail stalk z=.275; forked red tail z=.278.. .337; two tight cream wraps centred z=.274/.286; six-sided cream cord closed loop extends to z=.400. Root and Body origin are at the hang point world (0,0,.400), local mesh extends down to -.400. Static one-Body prop, front -Y. Catalogue depth .08 is a guide: flattened reference body .055 plus attached side fins gives about .067m depth; silhouette wins.

Features: faceted orange spindle, light belly, blunt head with real V mouth notch, raised gill edge, two octagonal grey eyes, forked two-lobe tail, dorsal and ventral edge fins, paired pectoral fins, two wrap bands, closed tall loop passing between tail lobes. All attachments intersect their supports, no coplanar seams. Budget <=600 tris, plan 576. X mirror is intentionally not expected (dorsal/ventral and mouth differ); exact Y mirror is required.

Material class flat palette, one 256px padded 4x4 atlas; cells0..9 pack layout, product colours cells10..15. Anchors: PRD09_HerbBunch for hanging origin/export/preview structure; TOL_Tools solid prism and path-sweep approach; processing_common.py reused read-only. No raw Fish geometry copied. NOT modelled: rack, hook, smoke, stand, animation, collider, other goods, noise or painted scales.

## Compare round 1
Viewed reference comparison and 128px thumbnail. Worst differences: head/body transition made a sharp step, tail lobes lacked faceted bevels, wrap bands were flat. Fixes: sixth spindle ring and widened low body to merge with the head, smaller gill plate, bevelled tail lobes and wrap rims. Initial topology/contact tests passed, 476 tris.

## Compare round 2
Viewed normalized side-by-side and thumbnail. Worst differences: head was still a flat extruded plate, body had too few longitudinal facets, belly colour was on the wrong edge. Fixes: bevelled the actual head volume; moved budget from tail bevels to two more spindle rings; mirrored the palette in Y and moved pale belly to +X. Wrap bevels retained; round 2 was 564 tris.

## Compare round 3 / final gate
Viewed full 1280x800 preview, normalized reference comparison, 128px thumbnail, front/back/side/top. Final fixes within this round widened upper head to remove the neck step and translated geometry so the highest loop vertex is exactly the origin axis at (0,0,.400). Body has eight octagonal section rings and the head has bevelled silhouette edges; closed loop and paired wraps read at thumbnail scale.
Remaining differences: fins and tail use simpler flat faces instead of the reference's sculpted bevels; head and gill have fewer shaping planes; reference is rounder and has an extra small rear edge fin (not in requested feature list). Loop above the wraps is .107m rather than the approximate .09m brief, following reference pixel ratio. Silhouette includes edge fins, so width is .138m versus catalogue .10m; body itself is .10m and depth .055m versus catalogue .08m, matching flattened reference. No moving parts.

## Final evidence / QA
Verdict SHIP WITH NOTES: all required signature parts present, topology/contact/export checks pass, simplified fins and head recorded above. Three compare rounds, anchors PRD09_HerbBunch + TOL_Tools and read-only processing_common. Final Blender process exit code 0; stderr contains only World.use_nodes deprecation warnings from the anchor preview helper.
One Body =592 tris /600 maximum: spindle124, notched bevelled head68, gill plates40, eyes56, dorsal16, ventral16, paired pectorals32, tail lobes32, wrap bands88, closed six-sided cord120. No moving parts. Bounds X .138 /Y .055 /Z .400m, mouth minZ=0. Top cord vertex is (0,0,.400000006); root and Body origins world (0,0,.400), child local translation0, rotation0, scale1. Front -Y. X mirror excluded because edge fins, mouth and loop lean are intentionally asymmetric; exact Y mirror error 1.23e-17m. All components contact their supports: worst gap0; non-manifold0, loose0, degenerate0, problems=[] asserted; SNAP not applicable. One material M_FarmProcessing_PRD16 with padded 256x256 4x4 atlas, cells0..9 pack-compatible.
FBX re-import: 2 nodes (root Empty + Body Mesh),592 tris, same .138/.055/.400m bounds,minZ=0,scales1, texture found at .fbm path with correct 256x256 size. Standard pack FBX conversion returns90degX on re-imported nodes; world bounds and hang point preserved. Unity import not verified. No asset or shared files outside assigned namespace edited.
Outputs:
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_16.fbx
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_16.fbm/T_FarmProcessing_PRD16_BaseColor.png
- art/Farm_Processing/Textures/T_FarmProcessing_PRD16_BaseColor.png
- art/Farm_Processing/Blend/FMS_Workshop_PRD_16.blend (asset-only library)
- art/Farm_Processing/Previews/FMS_Workshop_PRD_16_Preview.png (one final 1280x800 preview)
Rebuild: headless Blender5.2 --python build_smoked_fish.py -- export. Local scripts: build_smoked_fish.py,render_preview.py,compare.py; numeric evidence in build.log. Check renders removed after QA. About15minutes spent.



Latest cleanup note: automatic approval review rejected deletion of C:/Users/Sergv/AppData/Local/Temp/FarmProcessing_check/PRD16 as blocked by policy; final check renders remain there. Art folder has exactly one final preview.
