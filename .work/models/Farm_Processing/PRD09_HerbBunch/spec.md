# PRD-09 measured specification
Reference PRD-09.png: 1374 x 1145 px. Visible prop bounds approximately x350..1020, y42..1100 (670 x1058); upper cut stalks y42..335, wraps y310..438, foliage y500..1100; maximum width near y800 (28% above bottom). Reference projected width/height .63; use catalogue .20 x .15 x .40 m with depth and a narrower frontal projection.

Features: eight flat-cut octagonal stalks in three pack wood tones, stem-up; two red wraps, front knot, two cloth tails; 28 closed broad folded leaves, including rear leaves; three cream seed-pod trios attached to twig tips. The leaf topology adapts the read-only Nature berry_leaf / heart_leaf closed double-fan technique; no cards or floating strips.
Planned heights: tips 0, foliage 0..0.225, tie 0.268..0.308, stalk ends .345.. .400 m. Root and Body pivot = top bundle centre, hang point at z=.400 m in build world; asset mesh extends downward from pivot. Export world min Z=0 as requested.
Material: own 256px 4x4 atlas, one material; cells0..9 pack-compatible. Leaves #8E956A / #6F7552, pods #E8D6A8. No moving parts, no collider, no LOD1, no texture noise, no vein lines. Anchor: TOL_Tools/build_tools.py product structure and preview; processing_common.py read-only helpers.
Budget plan: about 650 tris, closed double-sided folded leaves prioritized. Asymmetric organic arrangement intentionally exempt from exact X mirror.

## Compare round 1
Looked at side-by-side and 128px thumbnail. Worst differences: sparse canopy with long vertical gaps, leaves too narrow, lower outline flat rather than pointed; exposed stalks thin and parallel. Fix: broader overlapping blades, staggered lower ranks with inward terminal leaves, slightly wider top stems and splayed cut ends.

## Compare round 2
Looked at side-by-side. Canopy overlap improved, but stalks pierce outside the wraps and hide their silhouette; cream pods are obscured; foliage lower edge needs a single stronger tip. Fix: stalks converge through the tie then cross/splay below, seed clusters moved forward, one central terminal leaf extended. Total remains 620 tris, within task's expanded allowance.

## Compare round 3 / final gate
Viewed final full-size 1280x800 preview, reference comparison, 128px thumbnail, side, back and top. Corrected the leaf normals around the radial stalk layout during this round so the side shows broad leaves rather than edge strips. Wrapping now gathers the converging stalks, all three seed trios read on the front, and the lower canopy ends in a central point.
Remaining differences: reference is fuller and rounder, especially its cream pods; this version uses economical octahedral seeds and 6 diamond-outline rear leaves among 22 hexagonal-outline blades. Stalks taper more strongly than reference and wrap/knot edges have simpler bevels. These are visible simplifications documented for the lead.

## Final evidence
QA: SHIP WITH NOTES (620 tris, 24% above original 500, within the explicitly allowed approximately 650). No moving parts. Eight flat-cut octagonal stalks =112 tris; 28 manifold folded leaves =312; 9 pods =72; 8 supporting twigs =32; two solid wraps =56; two tails =24; knot =12. Combined single Body =620.
Bounds X .200 / Y .150 / Z .400 m; min Z 0; X -.099.. .101, Y -.082.. .068. Root hang pivot world (0,0,.400) and Body local origin at the same hang point; Body local translation zero, rotation zero, scale one; root rotation zero and scale one. Front -Y. No exact mirror expected for this staggered botanical arrangement; printed mirror zero is from explicitly skipping asymmetric components. SNAP not applicable for a handheld/hanging product.
Checks: non-manifold=0, loose=0, degenerate=0; worst component contact gap=0.00000, problems=[] (asserted). One material M_FarmProcessing_PRD09 and one padded 256x256 palette atlas. Disconnected shells intentionally overlap at attachments without coplanar faces.
FBX re-import: 2 nodes (root Empty + Body Mesh), 620 tris, dimensions .200/.150/.400, minZ=0, scales 1; texture found at FMS_Workshop_PRD_09.fbm/T_FarmProcessing_PRD09_BaseColor.png, size256x256. Blender's FBX axis conversion reports 90deg X on re-imported root/body, as with the standard pack export settings; world bounds preserved. Unity import unverified.
Outputs (relative to worktree):
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_09.fbx
- art/Farm_Processing/Meshes/FMS_Workshop_PRD_09.fbm/T_FarmProcessing_PRD09_BaseColor.png
- art/Farm_Processing/Textures/T_FarmProcessing_PRD09_BaseColor.png
- art/Farm_Processing/Blend/FMS_Workshop_PRD_09.blend (asset-only library)
- art/Farm_Processing/Previews/FMS_Workshop_PRD_09_Preview.png (exactly one final preview)
Rebuild headless with build_herb_bunch.py -- export; supporting render_preview.py and compare.py are local. Full numeric output retained in build.log. Temporary check renders removed after visual QA. Approximately 15 minutes spent.

## Lead full-pack revision (supersedes prior final evidence)
Added eight outer-ring folded leaves on eight attached twig branches; 36 leaves now, with more front/back coverage and authored outward angles 35-55 degrees before envelope fitting. Moved all three pod trios to outer twig tips. Two revision comparisons: first kept .20 m envelope and still read narrow; second widened the tip envelope to .26 m and depth to .18 m, maintaining height .40 m and hang pivot z.40. Width deviation from approximate .20 m is explicit for lead review: central canopy about .20 m, projecting tips .26 m; prioritizes noticeably broader reference silhouette. Widest outer rank around z.14; central lower point retained.
Body748 tris versus760 revised cap: stalks112, original leaves312, outer leaves96, pods72, original twigs32, outer twigs32, wraps56, tails24, knot12. Non-manifold/loose/degenerate all0, worst contact gap0, problems=[]; asymmetry intentional; SNAP not applicable.
FBX re-import: 2 nodes, 748 tris, dimensions .260/.180/.400m, minZ0, scales1, texture found256x256. Same FBX, atlas/fbm copy, asset blend and single preview replaced. Final reference comparison, full-size front, 128px thumbnail, side/back/top viewed; Unity import unverified. Verdict SHIP WITH NOTES for .26 m outer-tip width instead of approximate .20 target and economical angular seed pods.
