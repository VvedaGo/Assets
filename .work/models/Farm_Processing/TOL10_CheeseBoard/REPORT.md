TOL-10 complete — SHIP WITH NOTES
Source: .work/models/Farm_Processing/TOL10_CheeseBoard/build_cheese_board.py, render_preview.py, spec.md; checks in verification.log.
Outputs under art/Farm_Processing: Meshes/FMS_Workshop_TOL_10.fbx; Blend/FMS_Workshop_TOL_10.blend; Previews/FMS_Workshop_TOL_10_Preview.png.
Atlas: Textures/T_FarmProcessing_TOL10_BaseColor.png plus Meshes/FMS_Workshop_TOL_10.fbm/T_FarmProcessing_TOL10_BaseColor.png; one M_FarmProcessing_TOL10 material.
Tris: Body 304 = frame44 + planks36 + handle64 + straps80 + bolts80; nominal80-180 exceeded, task permits about300 (4 over).
Size .450 X / .280 Y / .040 Z m, root/Body pivots ground bbox centre, identity transforms; handle +X, no moving parts.
Topology: non-manifold0, loose0, degenerate0, Y-mirror <1e-16, contacts gap0, no problems, hex-hole ray PASS, VERIFY CONTRACT OK; SNAP n/a.
FBX re-import asserted: 2 nodes/root+Body, 304 tris, same size, ground0, scale1, one material, 256px texture found; axis conversion +90 X follows anchors.
Three compare rounds and thumbnails plus four angle views and final 1280x800 preview inspected; temporary check images removed.
Notes: outward far bolts occluded in front preview, no continuous edge bevel, handle26mm, hole40mm, camera45deg for aperture visibility.
Lead seam fix: 1.25mm wall clearance, 1mm bottom/bed offset, shallow 3mm grooves; zero slivers, minimum triangle altitude 1.838mm.
Final preview inspected: dotted/sawtooth lines gone along both grooves and both plank ends; fine jittered shadows remove remaining shadow-map stepping.
Re-export/re-import passed at same output paths, 304 tris unchanged; Unity import unverified, no Unity files touched.
