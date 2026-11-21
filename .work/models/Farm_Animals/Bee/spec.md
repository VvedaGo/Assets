# INS-01 Bee - spec v2 (Farm Animals, skeleton I parts, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/INS-01.png` (1536x1024, standing bee, 3/4 view from its front-left: face and
left (+X) side, ~12 deg above). v1 (294 tris) was built from text only and was rejected (brush legs, huge hexagon eyes,
slab wings, boxy body). v2 rebuilds from the reference; budget raised by the lead to 600-800 tris.
Catalogue: FARM_ANIMALS_PACK.md 5.5 INS-01 (enlarged to 0.06 m, skeleton I), 4 (look rules), 6 (I: Root -> Body -> Wing.L/.R
+ Abdomen + Head).
Anchors followed: BRD-03 Chick (`../Chick/build_chick.py`: geodesic-like ring balls without pole fans, ray-cast eyes with a
buried back, split_to_objects with joint pivots, Workbench check sheet with the reference tile + EEVEE preview);
Duck/Rooster/Chick previews as style bar. House style 11/11b.

## Measured from the reference, v3 (head width 430 px = 0.029 m => 6.7e-5 m/px; body enlarged per lead pass 2)
| Feature | px | m (design) |
|---|---|---|
| head (almost spherical, large flat 4-sided facets) | 430 w x 420 h | ellipsoid 0.0145 x 0.0130 x 0.0140, 10-gon quad bands x 5 + flat caps, 116 tris |
| thorax (smooth faceted ball, no fuzz noise) | ~330 h | ellipsoid 0.0122 x 0.0115 x 0.0122, 10-gon quad bands, 76 tris |
| abdomen (biggest part) | ~1.4 x head width long, 340 h | 10-gon loft, max 0.0145 x 0.0134, axis 0.029 + tip cone 0.005 |
| stripes | 2 wide dark bands + dark tip, edges lean forward at the top | 2 dark bands (20 % of the length each) + dark tip cone, planes slanted 16 deg |
| eyes | 65 px octagon, dark red-brown, raised | 8-gon dome r 0.0026, 0.7 mm rim + 0.8 mm dome, yaw 29 deg |
| antennae | 30 px thick, elbowed, knob tip | 5-gon tube r 1.0 mm, 8 mm up + 7 mm forward-out, knob r 1.5 mm |
| legs | 70 px thick, bent | 6-gon hip -> mitred knee -> flat flared sole, r 2.7 / 2.4 / 2.9 mm (1.2x v2) |
| wings | long teardrops, up-back V, faceted ridge | front 46 x 15 mm, back 30 x 9.6 mm; lens section 0.6 mm edge / 1.4 mm ridge |
| body axis height | | 0.024 m (standing pose, soles at z = 0) |

## Parts (objects; pivot at the joint; root empty FMS_Bee on the ground under the centre of mass)
Body (thorax), Abdomen (+ tip cone/stinger), Head, Eye.L/.R, Antenna.L/.R, Leg_1.L/.R (front), Leg_2.L/.R (middle),
Leg_3.L/.R (hind), WingFront.L/.R, WingBack.L/.R. Rig mapping (skeleton I): Body <- Body + Leg_*; Head <- Head + Eye.* +
Antenna.*; Abdomen <- Abdomen; Wing.L <- WingFront.L + WingBack.L (same for .R). Legs are split per pair so per-leg bones
can be added later without remodelling. Parts overlap at the joints (hips/roots buried 2-4 mm).

## Material class
Flat palette, own atlas `T_FarmAnimals_Bee_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Bee`.
0 yellow #EDBA55, 1 yellow underside #D29E3A, 2 dark stripe #4B4342, 3 dark under #3A3332, 4 thorax #E7B04A,
5 thorax under #C99238, 6 head #F2C462, 7 head under #DDAA48, 8 eye #4A2A20 (reference red-brown), 9 wing #E8ECEF,
10 wing edge #A9ADB0, 11 leg #4E4644, 12 leg dark #3E3735, 13-15 series spares. Colours sampled from the reference.
Wings are opaque palette cells; Unity may later switch WingFront/WingBack to a transparent material variant.

## NOT modelled
hairs, mouthparts, claws, wing veins as geometry, pollen, flower/ground. No armature/weights/clips.

## Convention
Lowest point z = 0 (soles on the ground, standing like the reference). Hover height is set in Unity/animation. The preview
lifts the root by 10 mm only for the render (steeper sun 28 deg so the shadow stays in frame).

## Rounds v2 (kept for history)
v2 (790 tris) was accepted as "on the right track"; lead pass 2 asked for a bigger body, quad head facets, thicker legs,
2 bands + tip, bigger wings.

## Rounds v3 (Workbench sheet: reference | ref view, side, front, back, top, rear 3/4, front-right; EEVEE; 128 px)
1. 866 tris. Head/thorax rebuilt as quad-band balls (flat 4-sided facets), body +16 %, legs 1.2x, 2 bands + tip, wings
   42/28 mm. -> wings swept too far back and seen edge-on from the reference angle.
2. Wing span more upright (up 0.65), plane normal aimed at side/front/top, wings 46/30 mm; eyes r 2.6 mm; lower leg
   segments near-vertical like the reference.
3. Abdomen bigger (0.029 x 0.0145) so it dominates like the reference; preview view (0.85, -1, 0.17) shows both eyes;
   preview EEVEE 128 samples + sun angle 3 deg (removed shadow speckle on the hindwing).
Remaining nitpicks: from the 3/4 front view the thorax hides part of the abdomen (the reference shows it longer, probably a
wider lens); far forewing reads as a thin sliver from the preview angle; rear view shows the slanted bands as rings.

## Review round 3 (independent side-by-side, 3/5) - fixes
1. Eyes moved to the front: yaw 26.5 deg -> centres x +-0.0065 = spacing 0.45 x head width (0.029); flush 8-gon discs
   (0.7 mm proud, no dome), #4A2A20. Preview camera now front 3/4 (0.55, -1, 0.12), 35 mm lens: both eyes, both antennae.
2. Antennae: single elbow, then a blunt round club (rings r 1.0 -> 1.5 -> 1.1 mm + flat cap), no fork; second segment
   points forward-out so both read from the front 3/4.
3. Wings: light grey #E8ECEF (cell 9) with darker edge strips #AEB6BD (cell 10); opaque in the render.
   TRANSPARENT WING MATERIAL IN UNITY: the wing faces use ONLY atlas cells 9 and 10 (cell 9: column 1, row 2 from the top,
   UV centre (0.375, 0.375); cell 10: column 2, row 2, UV centre (0.625, 0.375)), and only the meshes WingFront.L/.R and
   WingBack.L/.R use them, so a transparent material (same atlas, alpha ~0.5) can be assigned to those four renderers.
4. Legs: r 3.0 / 2.7 / 3.2 mm (hip/knee/sole, ~5.8 mm thick = 0.15 x the 0.038 m body top height), spread to
   x 0.0185-0.022 and y -0.0255..+0.0205; preview shows 5-6 legs (the far hind leg is partly behind the abdomen).
5. Abdomen: 3 bold dark bands (each 11 % of the abdomen length) + dark tip cone.
Trade-off: from the front 3/4 view needed for two eyes, the abdomen side is foreshortened, so the stripes read as band
edges and the stinger is hidden (accepted by the lead). The reference shows face and body side at once because its head
faces the camera; a turned head in the rest mesh would break symmetry for the rig, so it is not done.

## Review round 4 (second independent review, 3/5) - fixes
1. Face: HEAD YAW 32 deg is a REST-POSE CHOICE. The group Head + Eye.L/.R + Antenna.L/.R is built symmetric (mirror error
   of the group before the turn 0.000000), then rotated rigidly 32 deg about Z around the Head pivot (neck joint) toward the
   bee's left (+X). A rig can reset it by rotating the Head bone -32 deg. Everything else is exactly X-mirror symmetric
   (mirror 0.000000 with the head group skipped). Eyes now +-25 deg from the face centre line, r 3.2 mm
   (0.22 x head diameter), flush 8-gon discs #4A2A20. Preview camera 62 deg from the forward axis, 9 deg above, 50 mm:
   both eyes, both antennae, stripes, stinger, near legs and wings together.
2. Abdomen: 9-gon loft (flat top), 3 dark bands of 0.15 L each (~0.18 of the visible abdomen) with equal 0.15 L yellow
   gaps, bands wrap the whole abdomen, + dark tip cone; slanted 16 deg.
3. Wings: #E8ECEF light grey with neutral grey edge strips #A9ADB0 (no blue); dedicated cells 9 and 10 kept (see above).

## Result
904 tris (lead cap ~900, +0.4 %): Abdomen 196, Head 116, Body 76, WingFront 56 x2, WingBack 44 x2, Antenna 46 x2,
Leg_1/2/3 32 x6, Eye 16 x2.
Size: body length head -> stinger 0.0697 (lead allowed up to 0.07), overall X 0.050 x Y 0.073 x Z 0.064 (wing tips),
body width 0.033 (turned head), body top 0.038.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000 (head yaw group excluded; group symmetric
before the yaw), worst contact gap 0, lowest z 0, WingFront/WingBack plates do not intersect (not coplanar),
eye clearance above the head facets 0.45-0.70 mm.
FBX re-import: 17 meshes + root, 904 tris, dims 0.050 x 0.073 x 0.064, texture found in FMS_Bee.fbm.

## Deviations
- Enlarged ~4.6x (0.0697 m vs real 0.015 m), documented deviation from TECH-01 (pack plan 5.5); lead allowed <= 0.07.
- 3 dark bands + dark tip (review rounds 3-4; reference shows 2 + tip).
- Head turned 32 deg in the rest mesh (review round 4) - the only non-symmetric group.
- Wings opaque light grey in the FBX/preview; transparency is a Unity material choice (cells 9/10 above).

## Rig + clips (skeleton I, first insect rig) - rig_bee.py + bee_clips.py + bee_gif.py
Final export is `rig_bee.py -- INS-01 export` (build_bee.py export would overwrite the FBX with the static mesh).
Skeleton I, 16 bones: Root -> Body -> {Abdomen, Head -> {Antenna.L, Antenna.R}, WingFront.L/.R, WingBack.L/.R,
Leg_1/2/3.L/.R}. Bone heads = part pivots (no .L->.R mirroring, because the head group is yawed 32 deg in the rest mesh:
the Head bone and the antenna bones start from that pose; a rig/clip can turn the head back with Head z-rotation).
Tails: Root/Body fixed forward, Head towards the eye midpoint, all others to the farthest vertex of their part (wing tip,
foot, antenna club, stinger). Roll rule as animal_rig (sagittal bones local X = world X). 17 parts bound rigidly
(weight 1.0; Eye.L/.R -> Head), armature object 'Rig' like every species.
Reusable structure (Butterfly/Ladybug: copy rig_bee.py + bee_clips.py, edit only SPECIES): bones/parents, bind map,
tail rules, per-bone rotation limits, clip list, 'fly' and 'flower' parameter blocks. bee_clips.World writes poses as
rotations about armature-space axes through the bone head (R_local = Rest^T R Rest), so flap = about body Y, leg lift =
about Y, pitch = about X, independent of bone roll; all periodic terms have whole cycles per clip -> exact loops.
Clips (30 fps, NLA takes):
- Bee_Fly 1.0 s (30 frames): Root +0.10 m (airborne), 4 flaps/s (stylised beat, not the real ~200 Hz; 7.5 frames per
  flap at 30 fps, 5 at the GIF's 20 fps), forewing -15..+55 deg about the body axis + 12 deg feathering, hindwing
  0.7x with 0.1-cycle lag, body bob 1.5 + 2.5 mm and pitch 8 +- 2 deg nose-down, legs hang/swing 14-18 deg, abdomen
  sway 5/3 deg, antennae trail 12 +- 6 deg, head nod 3 deg.
- Bee_On_Flower 2.0 s (60 frames): Root and Body still (feet planted, no slip), wings folded back (front -20 deg about X +
  14 deg splay, back -4 deg), legs step in turn L1 R2 L3 R1 L2 R3 (lift 13 deg = 3.2 mm, forward reach 6 deg, 60 % of
  each 1/6 window), abdomen pumps 2x 3.5 deg, head yaw 7 / nod 4 deg, antennae 10/8 deg.
Metrics (metrics_report.json): loop closure 0.000 deg / 0.000 m both; no limit violations; Fly feet >= 0.089 m;
On_Flower 5-6 legs on the flower every frame, lowest vertex 0.000 (nothing below the flower top), max foot lift 3.2 mm;
part overlaps vs rest (BVH, every 2nd frame): On_Flower none, Fly Leg_3.L/Abdomen +2 face pairs at the buried hip
(rest already 19). Bend test (wings +-60, legs +-30, abdomen +-20, head +-30, body 25): no holes (rigid overlapping parts).
FBX re-import: 16 bones, 17 meshes, 904 tris, takes Bee_Fly 30 / Bee_On_Flower 60 frames, vertex error 0.0 m.
GIFs: `bee_gif.py -- Bee Fly On_Flower` (wrapper of the read-only anim_gif.py): Fly with the shadow kept in frame and a
steeper sun (25 deg) for that clip; On_Flower on a flower prop (orange centre disc r 0.036 top at -0.4 mm, 10 white
petals to r 0.068, stem, meadow lowered to -0.075 m).
Not judged: Unity import of the takes, flap readability at Unity frame rates other than 30, wing transparency.
