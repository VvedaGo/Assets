# PRD-11 Dough in a bowl

Material class: flat palette, one material, own padded 256px 4x4 atlas. Cells 0-9 retain pack layout; ceramic cream/shade 12/13 (#EADAB4/#D8C49A); dough 14/15 (#F1D9A8/#E2C48E).
Anchor: TOL_Tools/build_tools.py build_bowl, shell topology, render and export conventions; TOL-12 preview inspected. Its shallow profile is NOT reused. Anchor render_preview.py is absent; render is embedded in build_tools.py.
Reference measurement (1374x1145): rim outer x187..1183 =996px; inner opening ~898px; foot width ~490px; foot apparent height ~62px; front stripe spans roughly y650..825; rim front y600..717. Perspective changes vertical lengths; catalogue scale fixes width 0.350m. Image foot/rim ratio ~0.49; requested 0.55 used as design constraint.
Planned dimensions: X/Y 0.350m, Z 0.200m. Bowl rim Z .155m; rim width .018m; foot .1925m diameter, height .025m; stripe .035m tall centered at Z .070m (45% bowl height). Real wall thickness .012-.018m; dome edge .015m below rim, apex .045m above rim. Shell is 16 sided; food is 16 sectors by 4 bands with ~4mm vertex jitter and a polygon crown rather than pole fan.
Features: one cream deep bowl, steep flared sides, continuous red band, broad flat rim, small cream foot, single warm pale risen faceted dough mound filling opening. Root and body origin ground center; front -Y; no moving parts.
NOT modelled: table, flour speckles, utensils, scores, extra food, noise textures, smooth shading, labels, collision or LOD1.
Deviations: no catalogue size deviation intended; the written task's 4-5cm proud dough dome takes priority over the image's lower apparent crown. Irregular dough intentionally not mirror symmetric; bowl must mirror exactly.

## Compare rounds
Pending.

Round 1: looked at reference/render sheet and 128px thumbnails. Worst differences: stripe too low, upper ceramic band too tall, lighting washes out dough facets. Raised stripe to .070-.105m to match measured reference (center 56% of bowl height, deviation from written approximate 45%); doubled rim vertical thickness from 6 to 12mm; reduced key/fill strength. Dough stands prouder than image, as explicitly requested.

Round 2: inspected side-by-side sheet and thumbnail. Stripe placement and lip thickness improved; remaining differences were dough triangles aligning into radial strips and camera exposing less rear inner wall than reference. Increased angular jitter to break radial strips, shifted camera toward reference's front and slightly raised elevation for round 3. No budget or dimensional change.

Round 3 final gate: inspected compare3, 128px thumbnails, back, side and top views. Single mound and stripe read at 128px, shell has no external intersections, visible dough contour remains faceted. Remaining differences: dome is visibly higher than reference (required by written brief); dome facets are more triangular than the image's polygon patches, and bowl's lower shoulder is slightly more angular. All are recorded notes; no additional rounds. Verdict SHIP WITH NOTES, pending final export verification.


## Final verification
472 tris = bowl 316 + dough 156, budget 550; X/Y/Z .350/.350/.200m; root and body ground-center identity pivots, min Z=0, front -Y.
Non-manifold/loose/degenerate/gap all 0; bowl mirror 0; food intentionally asymmetric; VERIFY/SNAP OK.
FBX re-import: 2 nodes, body parent correct, 472 tris, matching dimensions, unit scale, atlas found in .fbm at 256x256; Blender re-imported nodes show 90-degree X axis conversion per shared exporter; Unity import unverified.
Delivered art/Farm_Processing/Meshes/FMS_Workshop_PRD_11.fbx and .fbm texture, Textures/T_FarmProcessing_PRD11_BaseColor.png, Blend/FMS_Workshop_PRD_11.blend, Previews/FMS_Workshop_PRD_11_Preview.png.
Sources and logs remain in this folder; three compare rounds, four angles, final full-size preview and 128px thumbnails inspected; temporary PNGs removed.
Final stripe .070-.105m supersedes planned position: center 56% vs approximate 45% to match reference; foot .025m tall and .1925m wide; rim .018m wide and .012m thick.
QA SHIP WITH NOTES: required higher crown, triangular rather than polygon-patch dough facets, angular lower shoulder, reference-matched stripe placement; no failed numeric checks.


## Lead review fixes (supersedes earlier stripe/camera notes)
Red band now spans Z .0575-.0975m: 4.0cm tall, center .0775m exactly 50% of the .155m BOWL height. Boundary radii follow the existing outer silhouette; geometry/material band stays continuous and manifold.
Preview elevation lowered from 30.8 degrees to 20.0 degrees, 70mm lens; mound remains visibly above rim. Dough geometry is unchanged, as approved by lead.
Re-exported same FBX, blend, atlas and fbm copy; re-rendered same 1280x800 preview, visually inspected full-size and side-by-side reference plus 128px thumbnail. Bowl wall and band are more prominent; final camera follows requested 18-22 degree range.
Re-verification: 472/550 tris (316 bowl + 156 dough), .350/.350/.200m, ground pivot; non-manifold/loose/degenerate/gap=0, bowl mirror=0; FBX re-import 2 nodes, 472 tris, same bounds, texture found 256x256. See export.log for printed evidence.
QA SHIP WITH NOTES (prior dome/triangular facets notes retained); no failed checks, Unity import remains unverified. Temporary comparison image deleted.


## Accepted-model polish and coordinator clarification
The coordinator withdrew the conflicting 25% height increase and explicitly confirmed rim .155m / apex .200m; those heights and the 20-degree camera are retained.
Narrowed lower bowl and foot radii by 10% (foot width .1925 -> .17325m, lower shoulder radius .109 -> .0981m), tapering the reduction to 6% at band bottom and 2% at band top, then zero at upper wall. Inner floor reduced correspondingly to retain real wall thickness; dough, parts, palette and pivots retained.
Widened red band from .040 to .045m (Z .055-.100m), still centered at .0775m = 50% bowl height.
Re-exported the same FBX/blend/texture paths and re-rendered the sole 1280x800 preview; final preview visually inspected with dome still clearly above the rim.
Tris before -> after: 472 -> 472 (bowl 316, dough 156), below 550; dimensions .350/.350/.200m; non-manifold/loose/degenerate/gap=0, bowl mirror=0, ground/pivots unchanged, VERIFY/SNAP OK.
FBX re-import verified 2 nodes, 472 tris, matching dimensions, unit scales and .fbm atlas found at 256x256; detailed evidence in export.log.
Verdict SHIP WITH NOTES (existing faceting notes only); requested polish complete, Unity import remains unverified.
