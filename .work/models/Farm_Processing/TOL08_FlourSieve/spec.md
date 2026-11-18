# TOL-08 Flour sieve ? uniform lattice revision

Reference: planning/FarmProcessing/references/TOL-08.png (1374x1145). Measured ring x239-1130, rear/front rim y209/698, bottom y949; wall about .100m, rim .015-.020m, cream slats .014m, square openings about .030m. Anchors TOL_Tools for faceted ring, grey mitred loops and hex bolts; STA08_DryingRack for chunky real crossing lattice. Reuses processing_common.py read-only. No moving parts, flour, grain texture, collider or LOD1.

## Final geometry and material
Approved wood ring, dark band, eight red plates, shortened grey handles and four bolts unchanged. Ring outer apothem .150m, inner .130m, height .100m; lower band z .019-.043 proud .005m. Handle reach about .040m beyond ring wall. Overall X .380 x depth .310 x height .100m; catalogue footprint deviation retains reference ring and chunky handles.
Lattice and cream rim rebuilt as ONE continuous surface with true hole boundaries and shared top vertices, rather than intersecting or layered slat primitives. Six-by-six regular cell layout, .030m holes on .044m pitch gives .014m grid members. Four corner cells lie wholly outside the circular opening; 32 openings remain. Edge cells are clipped against all sixteen planes of the rim opening (apothem .115). Every peripheral opening is bounded by the perimeter; no patches fill holes. All top vertices are exactly Z .040; every vertical hole wall extends to Z .030, so every member is uniformly .010m thick, about .030m above the wooden ring bottom. Cream rim outer apothem .131 (1mm buried in wood), inner .115; top is integrated with the grid, with no separate overlapping faces at joints. Lattice underside is open as authorized; the sieve has no solid bottom.
Hierarchy root FMS_Workshop_TOL_08 plus one direct Body mesh, source transforms identity, origin/pivot ground centre (0,0,0), minZ0, front -Y. One M_FarmProcessing_TOL08 with own padded 256px 4x4 atlas; cells 0-12 match STA08. Wood #B5835A/#7A5233, cream #F2E6C9, red #C8473B, grey metal #8E959B. Flat shading; no noise.

## Budget approval and counts
Coordinator explicitly approved exporting 1038 triangles and raising allowance to about 1040 in reply to msg_9cb9c8af79af: "Export at 1038: keep the chunky 10 mm lattice with real hole walls". This supersedes the prior 750 ceiling; removing the 272 hole-wall triangles would make a zero-thickness sheet, which coordinator rejected.
Final Body 1038 tris: wood wall/band 288, unified lattice/rim 486 (top 214, real hole walls 272), red plates 96, handles 88, bolts 80. Fits approved 1040 with 2 spare. Original catalogue cap 400 exceeded for reference-signature real openings.

## Numeric and visual checks
Top triangulation area .0351089360338m2 equals outer perimeter area minus all holes (.0351089361813m2) within .000000001m2. All 32 holes pass 168 downward ray samples at centres and near every corner: no blocking top faces. Uniform top Z .040, no intersecting crossing members, no overlapping top surfaces. Intentional open underside boundaries 152; unexpected non-manifold 0, loose 0, degenerate 0, X-mirror .000000, worst component contact gap .00000, problems []. Grid/rim integrated, outer perimeter touches wood; all bolts and loops retain contact. VERIFY OK; no modular SNAP interfaces.
Headless Blender completed with process exit 0. FBX reimport: two nodes (root+Body), 1038 tris, dimensions [.380,.310,.100], origin zero, minZ -0.0000, unit scales, own 256px texture found in .fbm. X90 imported conversion follows anchor convention. check.log is final numeric/export evidence; grid_draft.log records preapproval budget evidence only.
Full-pack correction round replaces prior stepped/intersecting lattice. Inspected full 1280x800 preview, reference comparison, 128px thumbnail, straight top and underside; top view shows equal square central openings and regularly clipped peripheral holes, no left solid patch or staggered joints. All openings are visibly see-through. Remaining minor differences: wider simplified cream perimeter than reference, browner pack wood, simple square red caps and slightly different band/base proportions. QA SHIP WITH NOTES for approved budget/catalogue deviations and intentional open underside boundaries; no remaining Major lattice defect identified. Unity import remains unverified. Coordinator handles temporary comparison renders; art has exactly one preview.

## Files
- .work/models/Farm_Processing/TOL08_FlourSieve/build_flour_sieve.py
- .work/models/Farm_Processing/TOL08_FlourSieve/render_preview.py
- .work/models/Farm_Processing/TOL08_FlourSieve/spec.md
- .work/models/Farm_Processing/TOL08_FlourSieve/check.log
- art/Farm_Processing/Meshes/FMS_Workshop_TOL_08.fbx
- art/Farm_Processing/Meshes/FMS_Workshop_TOL_08.fbm/T_FarmProcessing_TOL08_BaseColor.png
- art/Farm_Processing/Textures/T_FarmProcessing_TOL08_BaseColor.png
- art/Farm_Processing/Blend/FMS_Workshop_TOL_08.blend
- art/Farm_Processing/Previews/FMS_Workshop_TOL_08_Preview.png
