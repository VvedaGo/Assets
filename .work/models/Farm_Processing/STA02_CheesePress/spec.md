# STA-02 Screw cheese press - FMS_Workshop_STA_02

Reference: planning/FarmProcessing/references/STA-02.png (three-quarter front, camera on the -X side, ~16-20 deg yaw, ~15 deg elevation).
Pack standard: FARM_PROCESSING_PACK.md s.5 (chunky, flat shading, no text) and s.6 (1 unit = 1 m, Y up, root identity).

## Feature list (from the reference)
- Bench: thick rectangular top with chamfered edges/corners; 4 splayed square legs (wider at the foot); low stretchers front/back/sides.
- Red square caps on the front/back faces of the top above each leg.
- Two vertical square posts from the table ends, chamfered pyramid tops, metal hex bolt on front and back at beam height.
- Diagonal braces (XZ plane, outside the posts) from the table edge to the post.
- Crossbeam between posts; metal nut block (chamfered octagonal block) in the middle.
- Metal spindle with readable slanted thread (stack of tilted 8-gon rings, crest/root), through the nut.
- T-handle: dark wood bar (thicker towards the ends), red octagonal knobs, red octagonal hub, metal hex cap on top.
- Round metal pressing plate (16 sides, chamfered) with a hex collar, sitting inside the mould top.
- Cream stave mould (14 staves, V-groove seams), two metal hoops with 7 hex rivets each.

## Material class
Flat palette: own atlas T_FarmProcessing_STA02_BaseColor.png (256 px, 4x4 solid cells of 64 px, UVs at cell centres => padding),
one material M_FarmProcessing_STA02. No noise/grain (the reference wood is plain colour).

## NOT modelled
Cheese / curd inside the mould, whey tray or spout, cloth, floor/base platform, text, screws/nails beyond the listed bolts and rivets,
wood grain, mould floor (hidden), LOD1 (pack s.6 asks LOD0+LOD1 for stations - not in this task, next step), collider.

## Anchors followed
- Scale (art/MarketFarm/Scale_Preview.png, .work/models/Scale/build_scale.py): metal + wood mechanism, component contact-gap check, mirror check.
- Cart (art/MarketFarm/Cart_Preview.png): chunky chamfered wood members, rails run into posts.
- Atlas/palette and material helpers after Farm_Nature/_common/nature_common.py (cells at UV centres, Closest filtering).

## Dimensions / deviations
Catalog X/Z/Y 0.8/0.7/1.2 (W/D/H). Reference proportions (post spacing vs height, table overhang, brace reach, splayed legs)
give a wider footprint: built X 0.88 x Y ~0.66 x Z 1.20. Deviation documented: width +0.08 m to follow the reference.

## Hierarchy / pivots
FMS_Workshop_STA_02 (empty, origin = ground centre, identity) -> _Frame (pivot 0,0,0), _Screw (pivot on spindle axis at nut centre),
_Plate (pivot at plate centre), _Mould (pivot at mould base centre on the table top). Front = -Y.

## Compare rounds (preview camera = reference angle, VIEW_DIR (-0.36, -1, 0.30))
1. All members too thin (posts, legs, beam, nut, handle); mould/plate too small and low; thread read as horizontal stripes.
   -> posts 0.11, beam 0.08, nut 0.17x0.13, knobs r0.05, mould apothem 0.235, TILT 0.016, root/crest 0.026/0.036.
2. Table too high (ref top ~0.37 m, short splayed legs); too little spindle between collar and nut; legs not splayed enough.
   -> table top 0.38, mould 0.38-0.67, plate 0.64-0.695, legs foot (0.39, 0.25) / top (0.34, 0.20).
3. Braces thin, hidden behind posts; legs slightly thin. -> brace board wider/deeper, legs 0.095/0.12, alternating stave tones.
4. 128 px thumbnail readable (frame / cream mould / grey screw / red accents). Brace still a bit less bold than ref -> brace depth 0.09, top +0.32.
5. Final full-size preview vs ref: remaining nitpicks only - wood less orange than ref (pack palette #B5835A kept on purpose),
   ref braces a little more prominent, ref plate slightly darker grey. Preview width share ~0.42 (tall model, height capped at 92%).

## Result
Tris: Frame 788, Screw 572, Plate 156, Mould 784 = 2300 (budget 1600-3000). Size X 0.903 x Y 0.621 x Z 1.200 m.
Checks: 0 non-manifold / loose / degenerate, X-mirror exact except the screw thread (chiral, 0.014 m), component gaps 0,
legs on z=0, mould base = table top 0.38, plate R 0.200 < mould inner apothem 0.205 (plate bottom 0.64 < rim 0.67),
thread 0.73-1.11 spans nut 0.845-1.0, spindle end inside collar, hoop-to-post clearance 4.7 mm.
FBX re-import: 5 nodes, 2300 tris, dims identical, texture found in FMS_Workshop_STA_02.fbm (256x256).
Movement: screw rotates about its local Z (Unity Y) and moves down with the plate; max travel down ~0.09 m (hub bottom 1.095
reaches nut top 1.0), plate stays inside the mould over that range. Limits to go into the pack README.
