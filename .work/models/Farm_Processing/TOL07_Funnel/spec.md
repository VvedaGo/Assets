# TOL-07 bottling funnel

Reference: planning/FarmProcessing/references/TOL-07.png (1374 x 1145).
Measured image landmarks: top rim x245..1125 (880 px), handles x128..1245 (1117 px); rim back y137, front lip y449..550; cone to collar y755; collar y755..890; stem y868..1048. Perspective affects these screen heights. Using 0.175 m rim across flats gives handle width about 0.222 m; catalogue 0.2 m width is exceeded to preserve handles.

Target dimensions before build: rim 0.175 m across flats, 0.025 m tall; cone bottom 0.060 m across flats at z0.085, cone top at z0.195; total height 0.220 m. Octagonal wood collar 0.064 m across flats and 0.035 m tall at z0.050..0.085; octagonal stem 0.040 m across flats and 0.050 m exposed length. Wall 0.004..0.006 m. Handle section about 0.012 m, horizontal outline with chamfered corners, bilateral X symmetry.

Features: upright 12-facet grey hollow cone, thick proud rim/light top; two flat metal outline loops, attached bosses with hex bolts; octagonal light/dark wood collar with red front square; short octagonal hollow stem resting at z0. Front -Y. Root FMS_Workshop_TOL_07 + Body, no moving parts, both pivots ground bbox centre.
Material: one flat 256px 4x4 atlas, anchor cells 0..12 unchanged. Anchor: TOL_Tools build_tools.py colander, ringco/path_sweep/render/verify copied; processing_common imported read-only. No separate render_preview exists for anchor (render lives in build_tools.py).
Not modelled: liquid, bottle, wear/noise, moving parts. Budget target 250, allowance about350: geometry cost will be recorded after build.

Round 1: looked at compare1 and 128px thumbnail. Worst differences: cone too tall versus the reference; bosses too central and detached visually from handle ends; model small in the landscape preview. Fixed cone length from 110 to 75 mm (total height now 185 mm, reference wins over 220 mm catalogue); handle ends spread along Y and bosses moved to front-side facets; next render will review framing. Stem remains physically upright, so a normal above-ground camera cannot see its bottom opening as the reference's inconsistent perspective does.

Round 2: looked at compare2, rear view and 128px thumbnail. Worst differences: top rim face still too thin; red badge undersized; small outer handle bends cost budget without improving thumbnail. Widened top lip to 10 mm, badge to 14 mm, simplified loops to a six-sided outline including their attachment edge (four sweep points, square flat section) saving 32 triangles; increased preview width fill. Bosses are hexagonal simplified raised bolt plates, with a tapered hex head, rather than separate octagonal round bosses; avoids buried cap faces.

Round 3: looked at compare3, side/front view and 128px thumbnail. Final silhouette reads as a wide funnel, wood collar/red badge and short stem. No further geometry changes. Remaining differences: loops reduced from octagonal to six-sided outline; mounting bosses simplified to hexagonal tapered bolt plates; pack metal renders cooler/darker than reference; bottom opening is physically real but hidden from the above-ground preview (inspect underside check). No blocker or major topology defect.

Final evidence / QA (2026-11-14): SHIP WITH NOTES.
- Outputs: art/Farm_Processing/Meshes/FMS_Workshop_TOL_07.fbx + FMS_Workshop_TOL_07.fbm/T_FarmProcessing_TOL07_BaseColor.png; Textures/T_FarmProcessing_TOL07_BaseColor.png; Blend/FMS_Workshop_TOL_07.blend; Previews/FMS_Workshop_TOL_07_Preview.png (1280x800, one preview).
- Tris: one Body 348 = cone/rim 120 + collar/stem 96 + handles 2x28 + bolt plates 2x32 + red plate 12; catalogue 100-250 exceeded x1.39, within task allowance of about350.
- Final size X/Y/Z: 0.224/0.175/0.185 m; catalogue 0.2/0.2/0.22. Reference silhouette takes precedence: 0.175 rim, handles broaden X, shortened cone preserves width/height ratio (reference bbox ~1.22; model bbox ~1.21).
- Root empty FMS_Workshop_TOL_07 + FMS_Workshop_TOL_07_Body; identity transforms, both pivots (0,0,0), bbox centred X/Y, minZ0, front -Y. No moving parts.
- One M_FarmProcessing_TOL07, own 256px flat 4x4 padded atlas, anchor palette. Real hollow metal walls/stem, no pole fans/no noise.
- Checks: non-manifold0, loose0, degenerate0, mirrorX0.000000, worst contact gap0, problems []; static hierarchy/pivot/ground OK. SNAP not applicable (not a modular asset).
- FBX re-import: 2 nodes, Body parent root, 348 tris, same 0.224/0.175/0.185 dimensions, scale1, minZ0, texture found256x256; actual Blender subprocess return code0 (validation.log).
- Three visual rounds with reference sheets + 128px thumbnails; front, rear, side/front, underside inspected; final full1280 preview and comparison inspected. Underside view confirms open stem/inside wall. Temporary check renders removed after QA.
- Remaining notes: six-sided loop outlines/flat square section; simplified hex boss/head profile; cooler house metal than reference; bottom opening hidden in above-ground preview; wood collar/badge lack microbevels to retain budget. Unity import remains unverified.
- Elapsed work approximately 20 minutes. Rebuild: headless Blender --python build_funnel.py -- export; render_preview.py invokes same export/preview pipeline; run_validation.py captures subprocess status and FBX evidence.
