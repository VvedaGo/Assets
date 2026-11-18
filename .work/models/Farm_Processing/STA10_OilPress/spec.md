# STA-10 Seed oil press

Reference: planning/FarmProcessing/references/STA-10.png. Anchor: approved STA05_JuicePress build functions, palette, checks and renderer (copied read-only); shared processing_common imported read-only.

Material class: flat palette; one 256px 4x4 atlas, cells 0-12 unchanged from STA-05. No grain or noise.

Features: tall four-legged splayed A-frame, diagonal braces beneath crossbeam, thick mid-height platform, low rectangular stretchers, red joint caps; small cream stave chamber, two metal hoops with hex rivets; grey pressing plate and hex collar; threaded spindle through square grey nut on beam; wooden octagonal-ended T-handle through hex metal hub; tapered square hopper on left dark wood block; open sloping U-channel outlet.

Measured reference image 1374x1145: silhouette x238..1125 (~887px), z35..1106 (1071px); chamber ~375px wide and ~290px high, platform ~62px thick, beam ~90px thick. Geometry targets: overall 0.98 x 0.80 x 1.40m; chamber diameter 0.40m / height 0.30m, platform top 0.42m, rim 0.72m, beam 0.94..1.06m, nut 1.06..1.12m, handle centre 1.34m. Catalogue size is a guide: follow reference's tall structure while retaining requested small chamber.

Hierarchy: identity ground-centred root FMS_Workshop_STA_10; direct children _Frame (hopper included), _Chamber (spout included), _Plate centre pivot, _Screw axis at nut centre. Screw and handle rotate together around Z (Unity Y).

NOT modelled: individual seeds (flat cream hopper fill instead), oil/drips, fruit, collection vessel, ground, text, LODs/collider/Unity setup.

Compare rounds: pending.

Round 1: compared side-by-side and at 128px. Worst differences: legs/caps too slender, handle ends too small, spindle reads as zigzag rather than threaded cylinder. Increased leg section .125 to .145m and caps .060 to .074m, handle radius .043 to .048m; changed thread to 12 facets and shallower tilt. Nut contact check found a 3.65mm chamfer-induced gap; sunk base 6mm into beam to ensure contact. Chamber remains smaller than reference proportion to honour explicit .40 x .30m brief.

Round 2: all mesh/contact checks pass; thumbnail distinguishes hopper and low chamber. Worst differences: thickened legs now conceal top red caps, lower caps almost flush with legs, T-bar ends too bevelled. Increased head depth to .31m and lower joint depth to .20m, moved caps onto those front surfaces; reduced end chamfer to .009m and thickened spindle .050/.038m. Nut gap corrected to zero.

Round 3: caps now visible and frame reads as an A-frame at 128px. Four angles show no unsupported components; full-size review exposes stacked-ring spindle rather than a convincing screw and too gradually tapered handle ends. Replaced tilted-ring approximation with a continuous helical radial profile (12 angular facets, three axial samples per pitch); shortened handle shoulders for distinct octagonal knobs.

Round 4: real helical thread and distinct handle knobs read clearly in full-size compare and thumbnail. Remaining issue: channel floor passed through the platform front edge and exposed a small patch of wood inside the oil channel. Raised the spout 33mm (rear centre .490, tip .383), retaining attachment to lower hoop and downward slope.

Round 5: final 1280x800 preview, side-by-side reference and 128px thumbnail inspected; open channel now has an uninterrupted grey floor clear of the platform. Alternate front/right/back/left renders inspected. Remaining notes: chamber smaller relative to frame than reference to honour explicit .40m diameter/.30m height; pack wood lighter; cream fill replaces individual seeds as requested.

## Historical evidence before lead correction: SHIP WITH NOTES
- Outputs relative to art/Farm_Processing: Meshes/FMS_Workshop_STA_10.fbx and its .fbm/T_FarmProcessing_STA10_BaseColor.png; Textures/T_FarmProcessing_STA10_BaseColor.png; Blend/FMS_Workshop_STA_10.blend; Previews/FMS_Workshop_STA_10_Preview.png (1280x800).
- Tris Frame 1052 + Screw 984 + Plate 156 + Chamber 1112 = 3304 / 1800-3500 budget.
- Size X/depth/height 1.013/.789/1.400m; minimum Z=0. Deviations +13mm width and -11mm depth due chunky feet and outlet.
- Chamber stave apothem .20m and height .30m; hoop-inclusive diameter .433m. Platform top = chamber base .420m.
- Pivots root/Frame (0,0,0), Chamber (0,0,.420), Plate centre (0,0,.676), Screw axis at nut centre (0,0,1.090). Handle rotates with Screw.
- Every part non-manifold 0 / loose 0 / degenerate 0 / mirrorX .000000 / worst gap .00000 / problems []. Helical spindle and asymmetric hopper excluded from mirror check; checks assert before export.
- Contacts screw base .735 < collar top .758, plate R .166 < inner apothem .174, plate top .697 < rim .720, hopper base = block top 1.115, nut sunk 6mm into beam to remove chamfer gap, feet Z=0; spout floor clears platform front edge by about 9mm. SNAP N/A freestanding.
- FBX reimport 5 nodes (root + four direct mesh children), 3304 tris, dimensions 1.013/.789/1.400m, min Z -0.0000, scales 1; texture found in .fbm at 256x256. Blend library contains only own asset data.
- Five compare rounds, 70mm camera, four-angle review, final full-size and thumbnail checks. One material M_FarmProcessing_STA10; compatible anchor palette cells 0-12. No noise, pole fans, floating parts or mixed shading.
- Anchor STA-05 and common helpers untouched, no Unity Assets edits. Unity import, LODs and collider remain downstream; no failed geometry/export checks. Approximate time 20 minutes.


## Lead correction — final evidence (supersedes earlier dimensions/results)
One requested fix round completed. Chamber enlarged from .40 x .30m to .50m across stave flats x .36m high (.420..780), centred under the screw, still resting on platform Z=.420. 22 staves replace 18: about 71mm width versus previous 70mm. Hoops centred at .490 and .710, each .048m high, equal .070m centre-to-end margins; eight mirror-symmetric hex rivets per hoop, except the lower front rivet under the outlet.
Plate enlarged to R=.216, top Z=.740 exactly 40mm below the stave tops; pivot at centre Z=.719; hex collar top .801 meets spindle starting at .778. Spindle thread crest diameter .090m, core .074m, 10 angular facets, dark-metal groove faces for thumbnail readability; nut increased .16 to .18m square. Helical spindle radius is sampled continuously rather than using separate thread pieces.
Outlet moved 51mm forward with the enlarged chamber (rear Y=-.237, tip Y=-.451), keeping the prior 26.6-degree downward slope. Rear floor Z~.465 meets the chamber/lower hoop, floor at platform front is above .45m (> platform .420), so it clears the platform. Frame/hopper/handle/camera remain as approved.
Final checks: Frame 1052 + Screw 792 + Plate 156 + Chamber 1384 = 3384 tris / 3500 ceiling. Size 1.013 x .840 x 1.400m, minimum Z=0; added depth is the relocated outlet. Chamber including hoops/rivets is .556m wide; stave diameter approximately .500m.
Every part non-manifold=loose=degenerate=0, mirrorX .000000 (asymmetric hopper and chiral spindle excluded), worst component gap .00000, problems []. Original ground-centre root and direct-child hierarchy retained; only Plate pivot changes to .719, Screw pivot remains (0,0,1.090).
FBX reimport: 5 nodes, 3384 tris, dimensions identical 1.013/.840/1.400m, scales 1, min Z -0.0000; 256px texture found at Meshes/FMS_Workshop_STA_10.fbm/T_FarmProcessing_STA10_BaseColor.png. Same FBX/atlas/blend/1280x800 preview paths overwritten, no additional deliverable files. Final preview, reference comparison and 128px thumbnail visually inspected.
Verdict SHIP. Remaining downstream work: Unity import, LODs/collider; no open model correction. Previous small-chamber caveat is resolved by this lead-authorized dimension change.
