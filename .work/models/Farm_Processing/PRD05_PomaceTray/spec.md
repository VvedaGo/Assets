# PRD-05 Apple pomace in a tray

Reference PRD-05.png, 1374x1145. Measured landmarks (pixels): overall silhouette x115..1258 y325..917; rim back edge (187,449) to (891,327), rim front edge (409,747) to (1257,556); bottom front (415,910) to (1123,760); left handle x115..309 y526..718, right x1008..1226 y325..515. Broad flat rim ~35px versus ~750px long edge gives roughly22mm; lower body inset ~30px gives tapered walls. Image perspective makes screen depth unreliable; physical depth follows catalogue.

Targets before build: pan outer rim0.500x0.350m; height0.120m; bottom0.430x0.280m; rim width22mm, 4mm top chamfer, actual base12mm and walls8-12mm. Handles16mm square section, projecting60mm each, under rim z0.101. Overall X approximately0.620m including handles (catalogue0.500m interpreted as vessel width, reference takes precedence); depth0.350m. Base8x5quads with14mm interior variation, edges die into walls; 20 red irregular low-poly chunks47-61mm,12tris each, half-sunk; 12 triangular pale chips17-24mm,8tris each, half-sunk. Food top below rim.

Features: one shallow tapered chamfered grey metal pan with real inside/bottom thickness; two mitred chamfered rectangular outline loops; coarse red pomace bed with irregular chunks and sparse pale accents. No separate whole apples. One static Body under ground-centred root FMS_Workshop_PRD_05, front -Y, no moving parts. Material class: flat palette, one padded256px4x4 atlas; cells0-12 preserved from anchor, cell13 pale#E8C9A0, cells14/15 red variation. Anchors: TOL_Tools colander shell and product build_cheese_mold/build_cut_wheel; TOL07_Funnel path_sweep and preview renderer copied, processing_common imported read-only.

NOT modelled: separate apples, stems, seeds, liquids, noise textures, animation, collider, unrelated supports. Budget catalogue250-600; detailed task ceiling about700; anticipated slight catalogue overrun for closed food base, solid chips and thick handles will be documented.

Round1: inspected reference/render sheet, 128px thumbnail and rear view. Main differences: chunks read as rectangular blocks; flecks disappear below chunks; handle loops read too flat. Replaced cubes with irregular eight-vertex hulls (pentagon foot, triangular crown) at12tris each, ray-projected pale chips onto food before sinking, raised outer handle edges by19mm. Base height range increased to20mm; 19 chunks after preflight budget adjustment704 to692tris.

Round2: inspected comparison/128px and low front. Flecks now read, loops improved. Main differences: triangular crowns too sharp; large flat areas between chunks; front long edge camera slope slightly excessive. Changed chunks to eight-vertex twisted irregular four-sided crowns, raised/rerolled coarse base and triangulated its nonplanar quads for actual faceted shading, adjusted camera X toward front. Task budget unchanged.

Round3: inspected reference comparison, 128px thumbnail, and end/side view (prior rounds rear and front also viewed). Chunk crowns now broad and irregular rather than blocks or pointed pyramids; faceted base fills between them, flecks read as accents. Final geometry locked. Remaining differences: fewer/larger/angular chunks than dense reference, cooler/lighter pack metal, handle loops lean upward less than reference rear loop. These are budget/style simplifications, no open blocker.

Final QA 2026-11-14: SHIP WITH NOTES.
- Files: art/Farm_Processing/Meshes/FMS_Workshop_PRD_05.fbx; Meshes/FMS_Workshop_PRD_05.fbm/T_FarmProcessing_PRD05_BaseColor.png; Textures/T_FarmProcessing_PRD05_BaseColor.png; Blend/FMS_Workshop_PRD_05.blend; Previews/FMS_Workshop_PRD_05_Preview.png (1280x800, inspected full-size).
- Reproducible source: build_pomace_tray.py, render_preview.py, run_validation.py; evidence validation.log (subprocess return0).
- Tris: Body692 = tray124 + handles44x2 + closed8x5 base156 +19chunks12x19=228 +12chips8x12=96. Catalogue600 ceiling exceeded by92 (15.3%); within explicit about700 task allowance.
- Dimensions X/Y/Z0.621/0.350/0.128m including handles; tray0.500/0.350/0.120m. Catalogue deviations: X includes60mm handles each side; tilted handles add8mm height. Base0.430x0.280m atZ0, flat ground.
- Root FMS_Workshop_PRD_05 empty + one direct child FMS_Workshop_PRD_05_Body; both origins0,0,0 at ground bbox centre, identity build transforms, front-Y, static.
- One M_FarmProcessing_PRD05, own256px4x4 flat padded atlas; cells0-12 match anchors; red5/6 dominates, pale13 accents. No noise, whole apples, floating parts or exposed intersections.
- Checks: non-manifold0, loose0, degenerate0, tray/handle mirrorX0.000000, contact worst gap0, problems[], food containmentOK, SNAP N/A static product. Food asymmetric by design, chips projected onto actual food and half-sunk.
- FBX re-import:2nodes (Body parent root),692tris, matching dimensions,minZ0, scales1;256x256texture found in FBM; axis conversion yields90degX imported root as anchors; Unity orientation unverified.
- Three comparison rounds with128px checks, rear/front/end-side views; final preview and side-by-side inspected. Remaining differences: sparser/angular pomace than reference, cooler/lighter pack metal, shallower loop tilt.
- Unity import/collider/LOD setup not performed per scope. Elapsed about12minutes.
Temporary check PNGs removed after visual QA.

## Accepted-model polish (2026-11-14)
Requested scope only: replace19 boxy chunks with30 rounded faceted chunks, diameter35-50mm, Z squash0.7, varied rotation, hexagonal main ring plus smaller triangular upper ring and shallow top vertex; increase pale flecks12 to22. Use four-triangle closed flat chips to retain budget. Tray/handles/base geometry, palette, pivots, hierarchy and preview framing unchanged. Before692tris; revised allowance about950.

Polish final: first preview exposed too little chunk volume; raised visible shoulders and kept final diameters44-50mm. Final evidence superseding original692-triangle QA follows:

# PRD-05 polish delivery

Verdict: SHIP WITH NOTES. Accepted-model polish only; same output names.
- Tris before -> after: 692 -> 936 (allowance about950). Body: tray124 + handles88 + unchangedbase156 +30roundedchunks480 +22flatflecks88.
- Chunks: 30 instead of19, rotated irregular six-sided main rings, smaller three-sided upper rings, shallow offset crown vertices, Z squash0.7,44-50mm diameter within requested35-50mm range. Closed16-triangle faceted polyhedra, sunk into food base; no box silhouettes.
- Flecks:22 instead of12, small14-21mm flat closed pale chips,4tris each, ray-projected onto actual food and sunk. Red remains dominant.
- Preserved pan, handles, base, palette, single Body/root hierarchy, pivots, preview framing, dimensions0.621x0.350x0.128m, groundZ0 and front-Y.
- Re-exported art/Farm_Processing/Meshes/FMS_Workshop_PRD_05.fbx and FBM texture; Textures/T_FarmProcessing_PRD05_BaseColor.png; Blend/FMS_Workshop_PRD_05.blend; one Previews/FMS_Workshop_PRD_05_Preview.png (1280x800).
- Topology/contact checks: non-manifold0, loose0, degenerate0, tray/handle mirrorX0.000000, worstgap0, problems[], food containmentOK; SNAP N/A.
- Re-import:2nodes, Body under root,936tris, matching dimensions,minZ0,scale1,256x256texture found; subprocess return0. Evidence validation.log.
- Inspected two polish comparisons,128px thumbnail and final full preview; adjustment raised chunks for clearer visible density. Existing cooler metal and coarser food than reference remain minor notes; Unity import unverified.
