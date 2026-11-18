# STA-11 Smoking cabinet

Material class: flat palette, one 256x256 atlas, no noise.
Anchors: STA07_JamKettle brick proud-of-mortar construction, parametric voussoirs and slab seams; MOD04_WallWindow chunky posts and red square caps. Shared processing_common imported read-only.

Reference measurement (1374x1145 image): total silhouette z pixels 25..1085 = 1060; front base ground 1058 to cap 800 = 258 (24.3%); cabinet cap 800 to lintel 350 = 450 (42.5%); roof ridge 170; flue top 25. Front width approx 470 px, right depth projection 140 px. The task estimate of 40% base conflicts with the image; image wins.
Target dimensions before build: closed static width .90 m; depth .80 m; height 1.80 m. Base top .48 (26.7%); cabinet posts .48..1.28; roof ridge 1.56; flue cap 1.80. Base .84 x .72; cabinet .72 x .64; roof .90 x .80. Door hinge (-.315,-.354,.50), opens -100 degrees around Z; racks .56x.54 at z .72 and .98, bottom-centre pivots, slide -Y.

Features: 3 running-bond red brick courses on light mortar, stone cap ring, grey static firebox door with stone segmented arch and jambs; light timber corner posts and red caps; vertical dark boards forming solid inner/back walls; cream plank gable with red ridge block; two four-board pitched roof slabs and ridge; octagonal right flue with hex collar bolts and truncated conical cap; separate dark-framed cream door, left hinges and bolted chunky grey D handle; two separate framed 7-slat light shelves on side cleats.
NOT modelled: food, smoke, ground plane, grain, cracks, extra props, animation clips, LOD1, collision, Unity import settings.
Deviations: open door increases deployed width/depth; catalogue dimensions describe closed cabinet. Base proportion follows measured reference.

Compare rounds: pending.

Round 1: side-by-side and 128px viewed. Worst: open door hardware faces away, roof boards merge visually and roof edges too thin, side projection too strong. Fix: put hardware on visible open face, 2 mm roof board seams and 68 mm thick slabs, camera X ratio .48 instead of .65. Numeric budget reduced from initial 3892 to 2948 by simplifying hidden edges and shelf slats; all component gaps now zero.

Round 2: compare sheet and thumbnail viewed. Hardware now reads on open door; board seams visible but roof board orientation differs from reference; cream door seam gaps too subtle. Fix: run roof boards ridge-to-eave (four depthwise boards on each pitch), widen door seams to 7 mm, centre gable seams for exact symmetry. Remaining lower-detail firebox handle and side bricks are budget-driven.

Round 3: comparison, 128 px, rear and left views inspected. Main silhouette and all hardware read correctly; back backing core masks external board seams, so recess it 10 mm for the final pass. Other remaining differences: more regular masonry and simpler firebox hardware than reference; pack dark wall palette deliberately darker; no irregular wear. Numeric structural X mirror = 0, component gaps = 0, both rack contacts and door closed hinge contact = 0.

Round 4: reference comparison and 128 px viewed, final 1280 preview inspected. Main remaining readability issue: shelf gaps foreshorten too much at the low camera angle. Fix for round 5: 30 mm slats with 35 mm gaps, 18 mm slat thickness; keep seven slats and same shelf frame/support contacts.

Round 5: final compare sheet, 128 px thumbnail and final 1280x800 preview inspected after widening shelf gaps; seven slats now readable at reference elevation. Five rounds total, no further changes. Rear/left coverage was round 3; backing core subsequently recessed to expose rear seams.

## Final evidence / QA
- Verdict SHIP WITH NOTES: regular brickwork, simplified firebox hardware, darker side walls than illustrated reference. No blockers or major defects; five-round limit reached.
- Tris: Body 2244, Door 440, Rack_1 132, Rack_2 132 = 2948 / budget 1600–3000.
- Static body .906 x .827 x 1.800 m; closed full .906 x .828 x 1.800; deployed .907 x 1.363 x 1.800. Ground Z=0. Roof thickness adds 6 mm width, 27 mm depth versus guide.
- Root ground-centre identity; direct children Body, Door, Rack_1, Rack_2. Door pivot (-.315,-.337,.500), baked open -100 degrees; local Z +100 closes. Rack pivots (0,0,.720), (0,0,.980), bottom-centre; slide -Y.
- Non-manifold/loose/degenerate = 0 all parts; structural X mirror 0.000000 (flue and firebox right hinges excluded; door deliberately asymmetric). Component contact gaps 0; rack-body and closed hinge-body contacts 0; positive scales. SNAP not applicable to standalone station.
- FBX re-import: 5 nodes, 4 meshes directly under root, 2948 tris, .907 x 1.363 x 1.800 m, minZ -0.0000; pivots preserved, scales 1; 256x256 texture found in .fbm. Blender +90 X axis conversion matches approved exporter; Unity import unverified.
- One M_FarmProcessing_STA11 and T_FarmProcessing_STA11_BaseColor.png; UV palette centres and padding, cells 0–12 standard, 13–15 stone/brick/mortar; no noise or downloads.
- Outputs: art/Farm_Processing/Meshes/FMS_Workshop_STA_11.fbx and FMS_Workshop_STA_11.fbm/T_FarmProcessing_STA11_BaseColor.png; art/Farm_Processing/Textures/T_FarmProcessing_STA11_BaseColor.png; art/Farm_Processing/Blend/FMS_Workshop_STA_11.blend; art/Farm_Processing/Previews/FMS_Workshop_STA_11_Preview.png.
- Build/export/re-import evidence: final.log; inputs: build_smoker.py, render_preview.py. No Unity Assets changes or commits.
