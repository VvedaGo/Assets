# SML-02 Fox - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/SML-02.png` (1536x1024): front-left three-quarter, ~15 deg above, head turned to
the camera (ours straight = rig rest pose), paper-craft red fox of large flat facets.
Catalogue: FARM_ANIMALS_PACK.md 5.4 SML-02 - red fox, white chest and tail tip, black paws, pointed muzzle, 0.90 x 0.50 m,
1500 tris (lead: up to ~2200 if it helps), skeleton Q.
Anchors followed: Cat (`../Cat/build_cat.py`: Model/loft, head loft along -Y, ray-cast eyes/ears/nose, cone eyes, tail
spline, COM shift), Dog rework (`../Dog/build_dog.py`: label field + contour snap for the bib, tucked joints, 3-segment bushy
tail with a white brush, plain tapered legs with one small knee step, EEVEE `look` sheet). Preview: `_common/animal_render.preview`.
Script: `build_fox.py -- SML-02 build|look|export`.

## Measured from the reference (ground ~950 px, back ~350 px -> 0.50 m: ~0.00083 m/px; head is nearer the camera, ~x1.15)
| Feature | px | model (m) |
|---|---|---|
| back top (level) | 600 above ground | 0.50 |
| belly / bib point | ~320 / ~280 above ground | 0.27 / 0.25 |
| head: chin / nose / eyes / crown | 490 / 520 / 645 / 830 (persp.) | 0.44 / 0.47 / 0.58 / 0.66 |
| ear height, base width | ~190, ~130 | 0.155, 0.11 |
| cheek ruff span (mutton chops) | ~470 (persp.) | 0.33 |
| eye diameter | ~40 | 0.032 (8-gon) |
| front leg width / stocking top | ~90 / 210 above ground | 0.08 / 0.20 |
| paw width, toes | ~125 | 0.09, 3 toe blocks |
| tail max diameter, length | ~250, ~600 along the curve | 0.22, ~0.6; tip at z ~0.1, white tip ~30% |

## Features
Slim faceted body (10 sides) with a level back; cream rounded-V bib (label field + contour snap) down the chest front;
thick short neck with a cream throat; pointed triangular head (10-sided custom profile) with flared cream mutton-chop
cheeks (slanted border from the cheek point up to under the eye), cream muzzle sides/chin, orange muzzle ridge to a dark
nose pad; dark-brown 8-gon eyes on the forward slope; big upright triangular ears (orange back + rim, cream inner dish);
plain tapered legs, orange to the elbow/hock, dark-brown stockings below (one 4 mm step), dark paws with 3 toe blocks;
big bushy tail Tail1-3 carried low, curving up at the tip, cream-white brush tip (~30%) with a saw-tooth border.
Orange shade by facet: top-facing faces light, underside faces dark (paper-craft look), cream underside shade.

## Material class
Flat palette `T_FarmAnimals_Fox_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Fox`: 0 orange #E2661E, 1 orange light
#EE7A2C, 2 orange dark #C9561A, 3 orange deep (spare) #B04716, 4 cream #F0DCC8, 5 cream shade #E1C8B0, 6 stocking
#3E2B25, 7 nose #2E1F1A, 8 eye #2A1D17, 9-15 series spares.

## Parts (object `FMS_Fox_<Part>`, direct children of empty `FMS_Fox`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R (toes are
part of the Foot), Tail1-3. Joints: the proximal part keeps the shared ring exactly and continues into the parent with a
hidden smaller ring (no seam groove); legs, ears, eyes, nose, jaw sunk into their parent.

## NOT modelled
whiskers, mouth line, teeth/tongue, eyelids/pupils, claws, fur strands, ground; head turned to the camera.

## Rounds
1. (Workbench) long weasel body, small head, thin legs, toes like claws, narrow bib -> body 0.58 m chest->rump,
   head rings bigger, legs/paws +15%, toes shorter and wider.
2. (EEVEE) head still small next to the reference, ears narrow, tail hidden at the ref angle -> head group x1.12 about
   the neck joint, ears base half-width 0.080, check views with a 35 mm lens (the reference is a close wide-angle shot).
3. Boxy body section, long muzzle, tail behind the rump -> rounder body sections (exp 2.15/2.3), muzzle 17 mm shorter,
   deeper chest, toes blunt.
4. Tail and white tip did not read in the 3/4 view, bib a thin strip, ears close together -> tail longer and more
   horizontal (0.72 m along the curve, radius 0.124), chest bulges forward with a wider bib, ears set wider and tilted out.
5. Neck-side zig-zag tried (read as spiky teeth) -> reverted to the straight throat border; angled dark brow facet over
   each eye; nose pad 17% smaller.
6. (preview) shoulder and hip showed box edges where the leg tops left the body -> leg top rings sunk inwards (x 0.6/0.55),
   legs leave the chest/thigh on a slant. Preview lens back to 50 mm (pack standard), view (1.0, -0.82, 0.24).
Remaining (nitpicks): reference head is turned to the camera (ours straight, rig rest pose), so the face reads 3/4 in the
preview; reference body looks stockier through its wide-angle perspective; the far ear shows its orange edge in the 3/4 view.

## Result
tris 1656 (target ~1500, +10%; lead limit ~2200). Pelvis 96, Spine1 76, Spine2 96, Neck1 44, Neck2 60, Head 136, Jaw 32,
Ear 2x32, Eye 2x14, Nose 44, FrontUpper/Lower/Foot 44/44/96 per side, HindUpper/Lower/Foot 60/44/96 per side
(Foot = paw 52 + 3 toes x 12 + caps), Tail1/2/3 44/60/108.
Size: width 0.410 (cheek ruffs) x length 1.422 (nose -> tail tip) x height 0.824 (ear tips); nose->rump 0.875, rump->tail
end 0.546, back 0.506, belly 0.244, crown 0.702, tail low point 0.069. Pivot: root on the ground under the volume
centroid (geometry shifted -0.122 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000, worst contact gap 0, min z 0.
FBX re-import: 27 meshes + root empty, 1656 tris, dims 0.410 x 1.422 x 0.824, texture found in FMS_Fox.fbm.

## Rework 2 (coordinator review 3/5) - supersedes the size and result above
1. Torso +35% deeper/wider at the same length: back 0.547 (was 0.506), chest bottom 0.196, belly 0.204, chest half width
   0.188 (was 0.140); neck radii x1.3 (0.13 x 0.115); head group raised 0.04.
2. Legs: Upper (orange) and Lower (dark) share the elbow/hock ring exactly (front z 0.170, hind 0.190, apothem 0.057 both
   sides) - no cuff, no step; tapered 0.066 -> 0.057 -> 0.050; paw apothem 0.055 = 1.1x the ankle; 3 toes protrude 11 mm.
3. Face: cheek factor 1.38 on the widest ring -> cheek span 0.492 = 1.42x the skull width (0.346); snout (eye ring ->
   tip) 0.096 x 1.10 = 0.106 m (was 0.106 x 1.12 = 0.119, -11%).
4. Bib: centred rounded V, front only (y < -0.20), top width 0.224 = 0.60x chest width 0.376, point at the chest bottom.
Checked: reference angle, side, front, back, top, 128 px (EEVEE). Preview view (0.85, -0.95, 0.25), 50 mm.
Result: tris 1720 (Upper front 60, hind 76; rest as before). Size 0.492 x 1.404 x 0.859; nose->rump 0.858, rump->tail
0.546. Checks 0/0/0/0, mirror 0, gap 0, min z 0. FBX re-import 27 meshes + root, 1720 tris, dims 0.492 x 1.404 x 0.859,
texture found.

## Deviations
- back height 0.547 vs catalogue 0.50 (coordinator: torso +35%).
- tris 1720 vs ~1500 (+15%); round 1 was 1656 (+10%): closed separate parts (hidden caps) and 3 toe blocks per paw (144 tris total).
- tail 0.72 m along the curve, adds 0.55 m behind the rump (lead: ~0.4) - the reference tail is as long as ~2/3 of the body.
- head straight (reference turns it to the camera). No LOD1, no armature (mesh-only round).

## Rig + clips (2026-11-21) - `rig_fox.py -- SML-02 bend|anim|lieviews|export`, `fox_clips.py`
Anchors: `../Cat/rig_cat.py` (copied: skeleton Q without horns = 25 bones, binding, spine/neck/tail path blends, export,
re-import check) + `../Dog/dog_clips.py` (rest-offset leg IK: fox hind lower rests at -18 deg) + Cat loaf search.
Mesh unchanged (build_fox.build(), 1720 tris, 27 parts). Scene 30 fps; takes Fox_Idle / Fox_Walk / Fox_Lie_Idle (NLA).
- Idle 4.0 s (121 fr): listens - head turns left with a tilt and holds, ears swivel to the sound (rotation about the ear
  axis), back, short right turn, ear flicks, 2 breaths, tail sway.
- Walk 1.2 s (37 fr): sneak - lateral sequence, duty 0.70, 0.30 m/s, step 0.252 m, body crouched 4.5 cm (+1.5 cm front),
  neck forward/low, ears forward, tail low and straight, high careful paw lift.
- Lie_Idle 4.0 s (121 fr): belly on the ground, front legs stretched forward, hind legs folded, spine + neck turned about
  the vertical to the left flank (world-yaw helper), head laid on the ground facing the tail, tail wrapped forward on the
  same flank; 2 breaths, ear flicks, tail-tip flick. GIF camera for this clip: `--view 1.0 0.2 0.35` (side, shows the face).
Metrics: loop closure 0.000 deg all; lowest vertex Idle -0.4 mm, Walk -2.9 mm, Lie -1.3 mm; Walk foot slip 0.77% of step;
joint-limit violations 0 (fox limits: Tail1-3 z +-85 for the wrap, FrontFoot x -100 for the crouched flat paw, HindLower
from the rest flex). FBX re-import: 25 bones, 27 meshes, 1720 tris, 3 takes, vertex error 0.0 m, texture found.
Known: the curl is a C-shape within the spine limits (+-15 deg per segment), front paws stretched forward, not tucked.

## Animation fixes round 1 (2026-11-21, ANIMATION_FIXES.md 7/8)
- Lie_Idle: spine yaw 28/28 deg (Spine1/2 z limit raised to +-30 for the curl), pelvis yaw -15, front paws folded
  (upper 70, forearm 20, wrist 110), head turned to the camera and laid low (chin 3 cm, roll 15) over the paws, tail
  wrapped forward along the near flank (yaw 84/84/47) with the white tip beside the head. Default anim_gif camera.
- Walk 1.1 s (33 fr): speed 0.40 m/s, duty 0.65, step 0.286 m (0.33 x nose->rump), body drop 2.1-5.0 cm (was 5.8-9.8),
  wrist lift 0.072 -> paw lowest vertex lifts 3.4 cm (front) / 4.0 cm (hind), paw flick 40/30 deg (wrist up-back).
Metrics: closure 0.000 all, lowest Idle -0.4 / Walk -2.5 / Lie 0.0 mm, slip 0.63%, violations 0, FBX re-import error 0.
Known (mesh): deep torso -> only ~16 cm of leg visible below the belly; the C-curl is limited by the long rigid pelvis part.
