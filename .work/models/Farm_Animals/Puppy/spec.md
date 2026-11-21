# PET-03 Puppy - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/PET-03.png` (1536x1024): front-left three-quarter, ~10 deg above, head facing the
camera, body receding to the right, tail raised behind the rump.
Catalogue: FARM_ANIMALS_PACK.md 5.3 PET-03 - puppy, same tricolour as the Dog, big head and paws, 0.40 x 0.30, 1100 tris
(lead: target ~1500, up to ~2200 if it helps), skeleton Q.
Anchors followed: Dog (`../Dog/build_dog.py`: Model/loft/tuck, head loft along -Y, ray-cast eyes/nose/ears, tail spline,
pivots, objects/export/look) - copied and changed (no contour snap; explicit zig-zag triangle bands instead);
Kid / Piglet (baby proportions: head ~45% of the length, short thick legs, big paws). Preview: `_common/animal_render.preview`.
Script: `build_puppy.py -- PET-03 build|look|export`.

## Measured from the reference (ground ~1000 px, back top ~410 px -> back 0.30 m, ~0.51 mm/px; head ~10% nearer)
| Feature | px | model (m) |
|---|---|---|
| back top / belly / ruff tips low | 590 / ~200 / ~280 above ground | 0.30 / 0.115 / 0.145 |
| head crown / eyes / nose / chin | 940 / 700 / 570 / 490 (perspective-inflated) | 0.466 / 0.385 / 0.31 / 0.245 |
| head width (cheeks), ear span | 620 / 810 | 0.25 / ~0.36 |
| eye diameter | ~50 | 0.024 (8-gon, 2 mm proud) |
| blaze width forehead / muzzle | 90 / 200 | 0.04 / 0.06 |
| upper leg width | ~130 | 0.068 (8-gon) |
| paw width x height, sole | 160 x 95, 15 | 0.08 x 0.055, 7 mm |
| tail max diameter | ~250 (side) | 0.11 x 0.09 |

## Features
Chubby round barrel (10 sides, 10 rings), black saddle over back and upper flank, orange lower flank band whose border
with the black is a zig-zag made of alternating triangles (teeth every 2 rings), white belly. Huge head (0.25 wide,
0.22 tall): black skull and back of the head, white blaze (1 face column, narrow on the forehead, widening to the
muzzle) from the crown to the nose, orange brow patches and big orange cheeks, white muzzle + chin (Jaw), dark-brown
8-gon eyes in the orange, dark triangular nose pad. Ears: short rise from the skull, big flap folding out-forward-down,
black outside, orange inside (by face normal). Ruff: 3 rows of skirt plates (14 vertices, 7 pointed leaf tips per row,
rows staggered by half a tip) around the chest, sides wrapping the shoulders, back half sunk into body/neck/head,
underside cream shade. Legs: short thick 8-gon, orange upper / white lower with a zig-zag ring border, big round white
paws with a 7 mm dark sole. Tail: big bushy plume raised in a curve, black base, zig-zag border, big white tip.

## Material class
Flat palette `T_FarmAnimals_Puppy_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Puppy`: 0 white #F2E8D8, 1 white shade
#E6D9C3, 2 orange #D9823A, 3 orange light (spare) #E3A35E, 4 black-brown #3E3033, 5 cream shade #D8C8AE, 6 nose #2A1E1E,
7 sole #3A2E28, 8 eye #2A1D17, 9-15 series spares.

## NOT modelled
mouth line, tongue, teeth, eyelids/pupils, toes/claws, fur strands, collar/tag, ground, head turned to the camera.

## Rounds
1. Ears edge-on thin wings; legs long/thin, belly high; tail a thin stick with a small white tip; muzzle long, skull flat.
   -> legs r 0.038-0.040 (+15%), paws r 0.044, belly 0.10, tail radii x1.35, rounder/shorter head. First EEVEE render of a
   session came out dark -> warm-up render before the sheet and the preview.
2. Ears pricked like a fox (fold width collapsed), head narrower than the reference, compare view too frontal.
   -> ears rebuilt as a curved leaf in a near-frontal plane (rise, rounded fold, flap to eye level), head width 0.273,
   REF_VIEW more lateral. Duplicate angle in the last head ring removed (degenerate 2 -> 0).
3. Far ear a thin spike at 3/4; body short vs the reference flank. -> body stretched 14% behind the chest.
4. Ears chunky tapering wedge facing forward (half thickness 20 -> 6 mm); dark slit under the tail -> orange rear cap.
5. Eyes 0.0276 across, ruff wider/lower (tips to 0.114, half width 0.165), ears 1 cm lower.
6. (preview) needle-like ruff side tips -> thicker plates (inset 32 mm), ear root 5 mm outward.
Remaining (nitpicks): reference head turned to the camera (ours straight, rest pose), so at the preview angle the far
ear reads more pointed than in the reference; ruff seen from the side is a flatter curtain than the bulging reference
bib; one row-1 ruff tip shows as a small white point beside the muzzle at the preview angle; faint tuck seams between
body parts in the side view (pack rule 4 allows visible joints).

## Result
tris 1920 (target ~1500, allowed up to ~2200). Pelvis 96, Spine1 76, Spine2 96, Neck1 44, Neck2 60, Ruff 324, Head 188,
Jaw 32, Ear 2x56, Eye 2x14, Nose 44, FrontUpper/Lower/Foot 2x(60+28+60), HindUpper/Lower/Foot 2x(76+28+60),
Tail1 44, Tail2 60, Tail3 92.
Size: width 0.432 (ears) x length 0.594 (nose -> tail tip) x height 0.508 (ear tops); nose -> rump 0.418, back 0.298,
belly 0.110, crown 0.473, head width 0.273, tail top 0.439. Pivot: root on the ground under the volume centroid.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 28 meshes + root empty, 1920 tris, dims 0.432 x 0.594 x 0.508, texture found in FMS_Puppy.fbm.

## Deviations
- "0.40 m long" read as nose -> rump (0.418); the raised plume tail adds 0.18 (overall 0.594), as in the reference.
- Overall height 0.508 (head + ears) with back 0.30: the reference head is ~1.6x the back height.
- Tris 1920 vs catalogue 1100 / target 1500: ruff (324) and the plume tail carry the signature; within the lead's 2200.
- Head straight (rest pose); no LOD1 (mesh-only round, like the other animals).

## Rework round 2 (coordinator review 2/5) - supersedes Result/Deviations above where numbers differ
Defects: ears an arch + a pointed ear (not matching), ruff a beard of long spikes, body short.
1. Ears: identical mirrored thick hanging flaps (EAR_RINGS): root ring sunk in the skull top-side, folded-over ridge
   1.1 cm above the crown, slab hangs beside the head with its inner edge ray-cast onto the head side (6 mm sunk),
   tip z 0.368 (eyes 0.386). Visible length ~0.116 = 0.50 x head height (0.231); width 0.090-0.094, thickness
   0.019-0.020 (21% of width). Outer face dark brown, inner face + inner-edge bevel tan (#E3A35E), the bevel shows from the front.
2. Ruff -> one broad chest bib shell (RUFF_RINGS/RUFF_EDGE): 4 outer rings with +-4.5% facet jitter, under the cheeks
   (top sunk in head/neck) down to z 0.128 (mid-foreleg), max width ~0.37 = 1.34 x head width, zig-zag lower edge
   7 tips, notch rise 0.030 = 0.13 x head height, back half sunk into body/neck, sides wrap the shoulders. 324 -> 192 tris.
3. Body +15% (chest -> rump 0.339 -> 0.390, nose -> rump 0.469); hind legs and tail moved with it.
Also: legs single tapered prisms (upper bottom / lower top radius difference <= 0.4 mm); bib core ring moved off the
leg top caps (coplanar 8 -> 0); preview view (0.90, -1.0, 0.24).
Result: tris 1788 (Pelvis 96, Spine1 76, Spine2 96, Neck1 44, Neck2 60, Ruff 192, Head 188, Jaw 32, Ear 2x56, Eye 2x14,
Nose 44, legs per side 60+28+60 / 76+28+60, Tail 44+60+92). Size 0.411 x 0.645 x 0.484 (W x L x H), back 0.298, belly
0.110, crown 0.473, ear top 0.484. Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000, gap 0,
min z 0. FBX re-import 28 meshes + root, 1788 tris, dims 0.411 x 0.645 x 0.484, texture found.
Remaining: bib smoother/boxier than the reference's leafy layers; ears smaller than the reference's; head straight.

## Rig + clips (2026-11-21) - mesh unchanged (meshcheck vs the mesh-only FBX backup: 28 parts, max diff 0.0001 m = 4-decimal rounding; texture md5 unchanged)
Files: `rig_puppy.py -- PET-03 bend|anim|export|meshcheck` (copy of ../Dog/rig_dog.py), `puppy_clips.py` (copy of
../Dog/dog_clips.py: rest-offset leg IK, wag, gait_dog). Anchor: Dog rig QD (26 bones incl. Ruff), same weights + thigh /
shoulder tops above the joint 70/30 with Pelvis/Spine2 (Cat rule: no thigh block popping out of the flank in the Trot).
Limit widened (own table only): FrontUpper x -100 (Play_Bow: forearms reach forward).
| Clip | s / frames | content |
|---|---|---|
| Idle | 3.0 / 90 | 9 wags (3 Hz) lagged along Tail1-3 (tip +-0.14 m), rump wiggle, 2 breaths, head turn/tilt, ear twitches |
| Trot | 0.5 / 15 | diagonal trot, duty 0.45, 0.55 m/s, step 0.124 m, bob, plume bounce/sway, ruff/ear bounce; Footstep f0 / f8 pairs |
| Play_Bow | 2.5 / 75 | stand -> front paws hop 6 cm forward, chest down (pelvis pitch 21 deg about the hips, chest >= 2 cm above ground), head up, tail high + fast wag, 2 chest bounces, cocked head -> hop back -> stand; Takeoff/Land events |
Metrics: loop closure 0.000 deg; lowest vertex Idle -1.4 mm, Trot -0.1 mm, Play_Bow -3.5 mm; Trot slip 0.05 %; limit
violations 0. FBX re-import: 26 bones, 28 meshes, 1788 tris, 3 takes, vertex error 0.0 m, texture found.
GIFs: Puppy_Idle 3.50 MB, Puppy_Trot 0.68 MB, Puppy_Play_Bow 2.71 MB. Rounds: Play_Bow 3 (no bow: hind legs straight at
rest -> pitch about the hips; shoulder limit), Trot 2 (thigh top popped out of the flank).
Remaining: in Play_Bow the folded front legs are mostly hidden behind the bib; spine seams open at extreme bend-test poses
(not reached by the clips); not seen in Unity.
