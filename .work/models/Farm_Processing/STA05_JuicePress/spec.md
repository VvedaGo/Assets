# STA-05 Basket juice press - FMS_Workshop_STA_05 (pack cover / hero)

Reference: planning/FarmProcessing/references/STA-05.png (three-quarter front, camera on the -X side, ~20 deg yaw, ~18 deg elevation).
Built from the STA-02 pilot (build_cheese_press.py structure, render_preview.py, palette layout); helpers now shared in
../_common/processing_common.py (STA-02's script untouched and still standalone).

## Feature list (from the reference, verified)
- Raised bench: thick table slab (reads as the front/side beams), 4 thick tapered splayed square legs with chamfered head blocks
  standing above the table corners, red square caps on the front and back faces of the heads.
- Stretchers on all 4 sides at ~0.2 m; diagonal braces "/ \" in the back plane from the back stretcher to the table underside
  (the ref shows them between the front legs, behind the front stretcher).
- Two tall square posts on the table sides, pyramid-chamfered tops; crossbeam near the top (darker front/back faces like the ref);
  big hex bolts on the post front/back faces at beam height.
- Thick metal spindle with a slanted thread (tilted 8-gon crest/root rings) straight through the crossbeam (no nut block, unlike STA-02).
- T-handle: wooden bar thin at the hub, thick faceted ends with big end chamfers; red chamfered square hub.
- Big cream basket: 21 separate staves (V seams, chamfered outer corners, chamfered top block per stave above the top hoop),
  alternating cream tones, inner faces darker; two thick metal hoops, 7 hex rivets each (centre + about 51 deg spacing, as in the ref).
- Round grey-beige pressing plate (16-gon, chamfered top) inside the basket below the rim, octagonal metal collar with a base step.
- Juice outlet: wide bolted flange plate under the lower hoop, square metal spout sloping 28 deg forward/down, open hollow end
  (inner walls + dark back face visible).

## Material class
Flat palette: own atlas T_FarmProcessing_STA05_BaseColor.png (256 px, 4x4 solid cells), one material M_FarmProcessing_STA05.
Cells 0-12 identical to STA-02 (mergeable later); 13 = plate #B4AA9D, 14 = plate side #978D82, 15 spare. No noise/grain.

## NOT modelled
Juice/fruit/pomace in the basket, a collecting bucket or tray under the spout, drips, cloth, floor/platform, text, nails,
wood grain, basket floor (hidden under the plate), LOD1 and collider (next step), the inside of the spout beyond 0.12 m.

## Anchors followed
STA-02 cheese press (accepted pilot: art/Farm_Processing/Previews/FMS_Workshop_STA_02_Preview.png + build_cheese_press.py),
which itself follows Scale (contact/mirror checks) and Cart (chunky chamfered wood members).

## Dimensions / deviations
Catalog X/Y(depth)/Z 1.0/0.9/1.6. Built X 1.226 x Y 1.169 (0.95 without the spout; the spout tip at y -0.645) x Z 1.600.
Height kept at the catalog 1.6 m; width follows the reference (posts and basket are ~1.24x wider relative to height than a 1.0 m
build; round 1 at 1.0 m read clearly too narrow). Deviation: +0.23 m width, depth +0.05 (+0.27 incl. spout). If the pack grid needs
1.0 m, scale uniformly 0.82 (height becomes 1.31 m) rather than squeezing X.
Flange: the ref shows 2 bolts (one each side of the spout), the brief said 4 -> followed the ref.

## Hierarchy / pivots
FMS_Workshop_STA_05 (empty, ground centre, identity) -> _Frame (0,0,0), _Screw (spindle axis at crossbeam centre z 1.25),
_Plate (plate centre z 0.91), _Basket (basket base centre on the table top z 0.47; includes flange + spout). Front = -Y.

## Compare rounds (preview camera, VIEW_DIR (-0.36, -1, 0.36), check renders in %TEMP%, deleted)
1. Too narrow overall (ref ~1.24x wider), basket too small, all members thin, spout/flange small.
   -> posts at +-0.50, basket apothem 0.375, thicker posts/legs/beam/bar/hub/spindle, flange 0.27 x 0.12, spout 0.095.
2. Members still light; staves too narrow (ref ~10-11 per half); rivet spacing; camera a bit low; front stretcher too low.
   -> 21 staves, rivet every 3rd (7 per hoop), posts 0.165, legs 0.185/0.15, beam 0.14 x 0.13, bar R 0.058, hub 0.17,
      spindle 0.064/0.046, elevation 15.8 -> 18.7 deg, rails at 0.20.
3. Close; 128 px thumbnail readable (frame / cream basket / dark hoops / red hub+caps). Remaining: ref crossbeam darker than posts.
4. Crossbeam front/back/bottom -> WOOD_M. Spout close-up: hollow end, flange bolts, clears the table front.
5. Full-size preview: found a crease on post tops / leg heads / inner spout corners (inset() flipped corner vertices when the
   inset exceeded the corner chamfer) -> new rect_prism() helper + scaled inner spout ring. Re-rendered: clean.
Remaining nitpicks: wood paler/less orange than the ref (pack palette kept), ref is still slightly wider overall and has a bit
stronger perspective, ref thread grooves a little deeper.

## Result
Tris: Frame 1000, Screw 388, Plate 212, Basket 1452 = 3052 (budget 2200-4000).
Checks: 0 non-manifold / loose / degenerate per part; X-mirror exact (thread excluded, chiral); component gaps 0; legs on z=0;
basket base = table top 0.47; plate R 0.315 < inner apothem 0.33, plate top 0.945 < rim 1.0; hoop-to-post clearance 17 mm,
rivets 12 mm; spout bottom clears the table front edge.
FBX re-import: 5 nodes, 3052 tris, dims identical, texture found in FMS_Workshop_STA_05.fbm (256x256).
Movement: screw rotates about local Z (Unity Y); hub bottom 1.45 reaches the beam top 1.32 after 0.13 m down; the plate moves
with it and stays inside the basket.
