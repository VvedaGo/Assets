# STA-12 Hand honey extractor

## Reference measurements and features (1374 x 1145 image)
Object silhouette x250..1234 y48..1100; drum x348..908, lid x336..920.
Drum top front y392, bottom front y747 (projected); lid front y354, handle top y48.
Feet x250..1010; front foot y1098, side feet y964; four radial legs form a diamond.
Crank hub near (947,365), grip x1064..1234 y468..567; tap near (585,680).
Feature list: 16-facet grey drum, proud top/bottom bands; warm beige shallow opaque lid;
dark wooden bridge grip on light wood feet; four chunky splayed legs, chamfered heads,
red outward plates, low square stretchers; grey side gearbox, hex hub, Z arm and red octagonal grip;
front hex valve nut, red lever, square hollow downturned spout; hidden axle and two mesh frame panels.

## Numeric targets before build
Metres: drum radius .33, base .40, top .96; wall .018. Bands .014 proud.
Leg heads top .40 (drum rests ON them), foot radius .385, head radius .305; feet z0.
Lid radius .35, base .96, shallow cone top1.055; handle top1.20.
Crank X axis through (.38,0,.865), arm drops .16, grip extends to x .70.
Basket bounds radius < .29, z .43.. .93, <=300 tris.

## Material and anchors
Flat palette, single 256px 4x4 atlas, cells0..12 match approved common layout.
Wood #B5835A/#7A5233, red #C8473B, metal #8E959B/#6E757B, lid #C9C2B6.
STA06_HandMill: stand legs, chamfered heads and red plates; shared helpers and preview/check/export structure.
STA04_FruitCrusher: Z-kink arm, faceted hub, chunky grip.

## Catalogue deviations
Four legs follow the reference, overriding the catalogue three. Crank and splayed feet exceed
catalogue .8x.8 footprint to preserve reference proportions; height remains1.2m.

## Hierarchy and pivots
Root identity at ground centre, front -Y. Direct children Body(0,0,0), Lid(0,0,.96),
Crank(.38,0,.865) rotates local X, Basket(0,0,.43) rotates local Z.

## NOT modelled
Honey, bucket, ground/platform, gears inside gearbox, actual fine wire mesh, grain/noise,
LOD1/collider/animation clips, Unity integration.

## Compare rounds
Pending.

Round 1: gearbox edge-on, drum bands too subtle, grip thin. Rotated gearbox/crank -30deg around drum axis, deepened bands and enlarged grip R .058; neutral ambient fill. Topology/contact checks all zero after replacing basket chamfer beams with square bars (148 tris).

Round 2: bands overly dark, lid reads flat, crank projected reach short. Restored metal/light band pair, raised the shallow dome centre to1.075 and reduced its flat top radius .18->.10, extended grip to pre-rotation x.79 and widened wood handle feet. Retain pack metal blue-grey rather than inventing an incompatible atlas cell.

Round 3: rear, lid-off and thumbnail checked; basket clear. Full-size preview exposed lid feet mostly buried in the dome and a coplanar underside seam. Round 4 raises the wood feet and arch lower edges (overall1.20m unchanged), seats lid underside1mm into the rim to avoid coplanar render artefacts; pivot stays .96 nominal rim seat.

## Final QA / output evidence
Round 4 compare and 128px thumbnail inspected: lid wood feet now readable, contact seam clean.
Remaining minor differences: pack metal is bluer than reference neutral grey; tap lever and gear box
are a little slimmer; reference has softer shading and slightly broader side feet. No blockers.
Verdict SHIP WITH NOTES (catalogue footprint/four-leg deviations); no noise, loose/floating parts or pole fans.
Tris: Body1496 + Lid320 + Crank140 + Basket148 =2104 against1600..3200; basket <=300.
Size X1.140 x Y(depth).893 x Z1.200m; feet minZ0; root identity, front -Y.
Final crank pivot(.32909,-.190,.865), horizontal axis(.866025,-.5,0) in Blender root space
(rotate around that axis, not localX; geometry rotation is baked so object transforms stay identity).
Lid pivot(0,0,.960), 1mm concealed underside engagement with rim; basket pivot(0,0,.430), verticalZ axis.
All four meshes: non-manifold0 / loose0 / degenerate0; X mirror error0 with gearbox/crank/lever
excluded as designed; per-component worst gap0 / problems[]. Drum base.400 = level head tops.400.
Basket outerR<.260 vs vessel innerR.312; top.930 vs seat.960; no poke-through while rotating.
SNAP N/A: freestanding machine. UV0 padded palette-cell centres, flat shading, one material.
FBX re-import:5 nodes (root +4 DIRECT children),2104 tris,1.140/.893/1.200m, minZ0,
mesh scales1, texture256x256 found in FMS_Workshop_STA_12.fbm; X90 re-import conversion matches anchors.
Final preview1280x800,70mm, ~26deg elevation; rear, lid-off and thumbnail views checked.
Outputs under art/Farm_Processing:
- Meshes/FMS_Workshop_STA_12.fbx
- Meshes/FMS_Workshop_STA_12.fbm/T_FarmProcessing_STA12_BaseColor.png
- Textures/T_FarmProcessing_STA12_BaseColor.png
- Previews/FMS_Workshop_STA_12_Preview.png (only preview)
- Blend/FMS_Workshop_STA_12.blend (asset only)
Source build_honey_extractor.py is headless/idempotent; render_preview.py follows STA06 template.
Four compare rounds; temporary check images retained at %TEMP%/FarmProcessing_check/STA-12 because automatic approval review rejected Remove-Item cleanup. Unity import unverified.
Elapsed work approximately20 minutes.

