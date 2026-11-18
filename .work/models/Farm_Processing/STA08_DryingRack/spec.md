# STA-08 Food drying rack - full-pack review revision

Reference: planning/FarmProcessing/references/STA-08.png. Anchor: STA02_CheesePress for square chamfered legs, oversized head blocks, red caps and chunky framing. Uses read-only processing_common helpers; headless Blender only.
Material class: flat palette, own 256px padded 4x4 atlas, one M_FarmProcessing_STA08 material; wood #B5835A, secondary/tray wood #7A5233, lattice top #E6D3A8 / sides #CDB88C (dedicated atlas cells 13/14), red #C8473B, grey metal #8E959B. No texture noise or grid textures.

## Reference and scope
Reference measured at 1374x1145: top posts y43-153, top tray face y365-423, middle y574-633, low y779-844, feet y1096. Signature features: strongly splayed four-post stand, enlarged chamfered heads with red caps, upper crossbeams, low stretcher rectangle, three removable lattice trays on side rails, centred D-handles with hex ends.
NOT modelled: food, base/floor, grain texture, loose screws, animation clips, LOD1, collider.

## Lead review correction round (supersedes initial build)
Initial three comparison rounds were superseded by lead review: lattice thin, front posts hid tray edges, legs lacked the intended splay/head blocks.
One correction round fixes all three together. Coordinator clarified conflicting initial lattice measurements: keep about 7x5 openings, scale holes to about 7-8cm and slats to 3.5-4cm instead of adding openings; silhouette and dense lattice take priority.
Legs are .11m square with .008m corner chamfers. X centre spacing at ground 1.20m; projected centre spacing at Z1.60 is .80m. Four separate heads are .14 x .14 x .12m, Z1.48-1.60, with chamfered crowns and red outer-face square caps. Upper crossbeams join the heads; the full low stretcher perimeter remains.
Trays sit strictly between the front posts, increase width toward the bottom, and project .10m forward of the front leg faces. Dark wooden frames .060m tall and .045m thick. Side rails follow the tray widths, overlap their underside and meet the posts. Centred metal D-handles retained.

## Full-pack readability correction (current final state)
One further lead-requested round thickens every lattice slat to .045m wide and .020m tall. Each slat top uses #E6D3A8, all sides and undersides #CDB88C. Dedicated spare atlas cells preserve the shared cells 0-12. Tray frames are explicitly confirmed to use dark #7A5233 throughout.
The real-geometry 7x5 layout, tray widths, leg/head structure, 10cm front projection and -Y sliding axis remain. Depth changes only 1.4-2.9mm to preserve exact square openings with the wider slats; bottom-centre pivots follow those tiny depth changes.
Full-size preview vs reference and before/after 128px game-distance thumbnails inspected. The lattice now reads as a stronger cream mesh surface at small size; square openings remain visible at normal preview size. No additional triangles required.

## Final dimensions (metres)
| Tray (bottom to top) | Frame W x D | Bottom Z | Centre Y | Square opening | Slat width | Slat thickness | Interior coverage |
|---|---|---|---|---|---|---|---|
| Tray_1 | .950 x .691429 | .430 | -.089286 | .084286 | .045 | .020 | 51.9% |
| Tray_2 | .870 x .634286 | .770 | -.117857 | .072857 | .045 | .020 | 56.2% |
| Tray_3 | .790 x .577143 | 1.110 | -.146429 | .061429 | .045 | .020 | 61.3% |

Each tray has exactly 7 x 5 equal square openings from six longitudinal and four cross slats. Crossing members overlap slightly in Z for solid contact; real geometry throughout. Final square holes are 8.43/7.29/6.14cm bottom-to-top as the trays taper, with constant 4.5cm slats on all tiers; the wider slats intentionally increase coverage for full-pack game-distance readability.
Rectangular slats use simple closed six-face boxes: 120 tris for each lattice. Closed bottoms cost only 20 extra tris per tray and retain zero non-manifold edges; the entire asset is still below the original 1800 budget, so no open-bottom shortcut or overrun is needed.
Final overall size X1.310 x Y.887 x Z1.600m. Footprint exceeds catalogue 1.1 x .7 to meet lead's explicit 1.20m foot-centre spacing and 10cm forward tray projection, including handles/caps. Feet exactly on Z0.

## Hierarchy / pivots
Root FMS_Workshop_STA_08 at ground origin, source transforms identity. Direct children _Frame, _Tray_1, _Tray_2, _Tray_3. Frame pivot origin; tray pivots at their frame bottom centres: (0,-.089286,.43), (0,-.117857,.77), (0,-.146429,1.11). Front and sliding direction are -Y; all trays clear the posts while extracted. Hand support required after leaving their rails.

## Checks and export evidence
LOD0: Frame 792, Tray_1 316, Tray_2 316, Tray_3 316 = 1740 tris; original cap 1800, clarified permitted cap 2100.
All four parts: non-manifold 0, loose 0, degenerate 0, X-mirror error .000000, worst component gap .00000, no component problems. Each tray/rail vertical gap 0; flat support overlap .026m. Post clearances over full tray height bottom/middle/top .00875/.00625/.00375m; forward projection .100m each. SNAP/VERIFY OK.
FBX re-import: five nodes (root plus four meshes), 1740 tris, identical 1.310/.887/1.600m dimensions, base Z0, correct tray pivots, scale one and 256px texture found in own .fbm folder. Blender importer presents the approved anchor's same 90-degree axis-conversion rotations.
Full-size final preview and reference side-by-side inspected, plus 128px thumbnail and front/side/back views. Full-pack-corrected darker lattice reads chunky, A-splay and head blocks read clearly, front legs no longer cover tray front edges. Remaining minor differences: pack wood less orange, handles slightly more angular than ref, rear portion of each top tray is shorter to retain square holes while width tapers. No noise, pole fans, floating parts, shading inconsistency or extra scope.
QA verdict: SHIP WITH NOTES for documented footprint deviation and minor stylistic differences. No remaining Major defect identified in this round. Unity import, LOD1 and colliders remain outside dispatch.

## Files
- .work/models/Farm_Processing/STA08_DryingRack/build_drying_rack.py
- .work/models/Farm_Processing/STA08_DryingRack/render_preview.py
- .work/models/Farm_Processing/STA08_DryingRack/spec.md
- .work/models/Farm_Processing/STA08_DryingRack/check.log (complete numeric/export evidence)
- art/Farm_Processing/Meshes/FMS_Workshop_STA_08.fbx
- art/Farm_Processing/Meshes/FMS_Workshop_STA_08.fbm/T_FarmProcessing_STA08_BaseColor.png
- art/Farm_Processing/Textures/T_FarmProcessing_STA08_BaseColor.png
- art/Farm_Processing/Blend/FMS_Workshop_STA_08.blend
- art/Farm_Processing/Previews/FMS_Workshop_STA_08_Preview.png

Check/compare PNGs were inspected then removed from the STA08 temporary directory; art contains exactly one final preview.
