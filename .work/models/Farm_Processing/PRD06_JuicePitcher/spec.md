# PRD-06 Juice in a ceramic pitcher

Material class: opaque flat ceramic, wood, orange juice. One prop, one atlas/material, one static Body child; no moving parts. No transparency, text, droplets or extra objects.

Reference 1374x1145: object bounds roughly x220..1188,y81..1072; body belly x240..985 near y640; foot y998..1072 (~7.5%); waist y420..460 (~63% height); rim y81..350; stripe y640..788 (projected band follows facets); handle thickness ~75px, hole ~140px. Body maximum diameter to height is about .75; handle extends another .21 body diameter. These are projected measures, not orthographic dimensions.

Planned metres: ceramic 12-gon belly diameter .240 at z.115-.140, waist diameter .164 at z.230, flared collar diameter .216 at z.340; grey foot .024 high; red band .025 high. Raised V-spout tip .040 beyond round rim, .010 raised, exterior sloping from waist. Rim thickness .010; juice plane z.295 (45mm below rim), 5mm dark orange wall ring; single closed surface sharing edge loops with inner wall. Wooden octagon handle diameter .034, six centreline points with chamfered bends, flush immersed ends.

Catalogue .25/.25/.35m, 250-500 tris. Reference prioritizes wide belly and handle; anticipated width ~.35, depth .24,height .35. Root/Body origin at ground bbox centre, minz0, front -Y; Y symmetry only. Anchors: accepted TOL06 V-spout angular tip and shared rim outline, TOL12 bowl stripe as shared profile material band; processing_common imported read-only. No pole fans or coplanar overlaps.

Round 1: 376 tris, zero topology/contact/Y-mirror defects. Compared sheet and 128px silhouette: body too slender, collar reads like a funnel, cream too bright. Fix: widen vessel XY 17%, shift handle outward .020m preserving flush joins, reduce key light to 2.5; the wider collar restores broad pitcher opening.

Round 2: numeric checks unchanged, 376 tris; compared sheet and 128px thumbnail. Remaining: overly long collar, lower belly taper too severe, rim and wooden handle too light in silhouette. Fix: waist z.245, lower belly radius .112, rim inner radius .094, wooden section radius .020; camera elevation 32.7 degrees to expose juice like reference.

Round 3/final: 376 tris (vessel+juice284, handle92), topology and contacts passed. Viewed third comparison, top/back/spout, final 1280x800 preview, final comparison and 128px thumbnail. Remaining differences: taller-looking flared collar, slimmer lower silhouette and simpler handle bends than reference. Verdict SHIP WITH NOTES.

Final size .398/.281/.350m (X/depth/height); catalogue +.148/+.031/0m to retain reference width, outboard V and handle. Belly diameter .2808; waist z.245; foot .024; stripe .025; rim thickness .01638; V extension .0468 and rise .010; juice depth .045; handle diameter .040. Ground bbox-centred identity root and Body pivots, minz0, front -Y, Y symmetry only. Palette cells0-9 preserved; own wood10/11, juice13/14, foot15.

Checks: non-manifold0, loose0, degenerate0, Y-mirror0, contacts worst gap0/problems[]; SNAP N/A. FBX reimport2 nodes (root Empty+Body),376 tris,scale1/1/1,same bounds,minz0,texture found256x256. Evidence export.log; Unity import unverified. PowerShell reports Blender deprecation warnings as NativeCommandError; Blender completed export/reimport and quit normally.

Outputs: art/Farm_Processing/Meshes/FMS_Workshop_PRD_06.fbx and its .fbm texture; art/Farm_Processing/Textures/T_FarmProcessing_PRD06_BaseColor.png; art/Farm_Processing/Blend/FMS_Workshop_PRD_06.blend; art/Farm_Processing/Previews/FMS_Workshop_PRD_06_Preview.png. Source build_juice_pitcher.py/render_preview.py/compare.py. Three compare rounds plus final inspection complete.

## Lead silhouette revision — one fix round

Supersedes previous dimensions and proportions. Rebuilt profile with widest belly z=.147 (.42H), radius .140; round rim radius .125 (belly/rim apothem ratio1.12); foot radius .1008 (.72 belly); waist z=.245 (.70H), radius .1025 (.82 rim). Collar flares over the top30% only. Stripe now z=.180..205, centre .1925=.55H, height .025. Lower belly tapers into the foot. Rim, V-spout, orange juice and colours retained; V extension .040, raised .010, liquid z=.295. Handle now .034 across-flat octagon, top attachment z=.320, bottom z=.140=.40H, outer centreline .207 vs lower join .138 (arc .069), both ends flush/intersecting the surface.

One fix round: reference comparison, 128px thumbnail, top/back/spout and final full preview inspected. Belly is broader relative to the round opening, stripe higher, lower taper fuller; reference lighting and projected silhouette still differ slightly. SHIP WITH NOTES: catalogue X/depth deviation remains; Unity import unverified.

Revised checks: 376 tris (vessel+juice284, handle92) vs250-500; nonmanifold0/loose0/degenerate0/Y-mirror0/contact gap0/problems[]. Size .390/.280/.350m, ground bbox-centred identity root+Body, minz0. SNAP N/A. FBX reimport2 nodes,376 tris,same size,scale1/1/1,texture found256x256. Overwrote same FBX/blend/atlas/fbm/preview paths; export.log and revision.log contain current evidence. Temporary review PNGs removed after inspection.
