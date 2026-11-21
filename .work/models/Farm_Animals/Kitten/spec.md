# PET-04 Kitten - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/PET-04.png` (1536x1024): front three-quarter, ~10 deg above; the head is turned
to the camera (face almost frontal), the body recedes to the right at ~35-40 deg, tail raised behind the rump.
Catalogue: FARM_ANIMALS_PACK.md 5.3 PET-04 - kitten, grey, big ears, 0.25 x 0.18, 900 tris (lead: up to ~1400), Q.
Anchors followed: Cat (`../Cat/build_cat.py`: Model/loft, ring_xyz superellipse sections, ray-cast eyes/nose/ears,
tail spline, pivots, objects/export) - copied and changed; Puppy/Kid/Piglet (baby: huge head, chubby short body, short
thick legs). Preview: `_common/animal_render.preview` (read-only).
Script: `build_kitten.py -- PET-04 build|look|export`.

## Measured from the reference (ground ~1050 px, back top at the rump ~590 px -> back 0.18 m, ~0.39 mm/px near the body)
| Feature | px | model (m) |
|---|---|---|
| back top / belly above ground | 460 / ~150 | 0.18 / 0.063 |
| head crown -> chin | 155 -> 700 (545, head ~10% nearer) | 0.315 -> 0.13 (0.185) |
| head width (cheeks, widest 2/3 down) | 785 | 0.238 (= torso length) |
| eye 8-gon, across / centre spacing | 75 / 290 | 0.025 / 0.094 |
| eye centre below crown | 0.6 of head height | z 0.212 |
| nose triangle w x h | 70 x 45 | 0.024 x 0.015, z 0.19 |
| ear base / length (tilt out ~23 deg) | ~230 / ~280 | 0.09 / 0.10 |
| leg width / gap between front legs | 110 / 165 | 0.047 / ~0.05 |
| dark sole band | ~30 | 0.010 |
| tail thickness / rise above back | ~100 / ~180 | 0.042 -> 0.036 / ~0.08 |

## Features
Chubby barrel torso (10 sides), huge round faceted head (12 sides, widest at the cheeks, rounder crown), wide face plane
with two dark-brown 8-gon eye discs 2.5 mm proud, dark-brown inverted-triangle nose on top of a V-shaped muzzle wedge
(two cheek facets + centre crease, = Jaw), two big upright triangular ears (thick, lighter inner dish, grey rim, base
sunk into the skull), four short thick 8-gon legs with a slight flare and a 10 mm dark-brown sole band, short thick tail
curving back-up-forward in 3 segments with a blunt tip.
Joints without seam lines: neighbouring body/leg/tail parts SHARE the boundary ring (identical vertices) and the child
continues as a hidden band (scale 0.94) inside the parent; every part is closed by caps that are hidden inside the
neighbour.

## Material class
Flat palette `T_FarmAnimals_Kitten_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Kitten`: 0 grey #9A9496, 1 grey light,
2 grey dark, 3 ear inner #BFB8BA, 4 eye #3A261F, 5 nose #4A3530, 6 sole #3A2E28, 7 grey darker, 8-15 series spares.

## NOT modelled
whiskers, mouth line, teeth/tongue, eyelids/pupils/highlights, toes/claws, fur strands, collar, ground, head turn.

## Rounds (EEVEE look frames: reference angle, preview angle, side, front, back; Workbench sheet incl. top; 128 px)
1. Ears thin tall spikes, body/legs slim under the head, head not wide enough (w/h 1.30 vs 1.44), tail thin
   -> ear base half 0.058, body half width 0.086, legs r 0.0275, head w 0.262, tail r 0.025.
2. Head ~10% small vs back height (ref 1.18x), legs read long, ears pale cones without rim, muzzle hangs like a lip
   -> head group x1.10 about the chin/chest contact, belly 0.054, wider rim + grey ear tip (3-ring ear), tilt 29 deg.
3. Legs still long (round belly rises at the legs), light "lip" from the up-facing jaw top (facet shade), tail hidden
   at the reference angle -> belly 0.048, legs r 0.030, jaw/ears excluded from facet shading, compare view more lateral.
4. Proportions measured equal to the ref (legs 13.5% vs 14.5% of height, chin 33% vs 34%); tail thinner than a leg
   -> tail r 0.0285 -> 0.0245, longer forward hook; 2 coplanar tail pairs -> hidden tail bands scale 0.84 (0 now).
5. Ears narrow, muzzle a shelf, tail not beside the head -> ear base half 0.068, tail reaches back to y +0.195.
6. Legs outside the body width (outer side ran up the flank) -> legs at x 0.048 under a flat belly (pb 4.0);
   muzzle moved 1.2 cm forward/up to carry the nose.
7. (preview) muzzle read as a pale beak, tail hidden behind the head at 37 deg -> flatter V muzzle, steeper top band,
   preview azimuth 45 deg (face + tail both visible). Ear back ridge deeper (side view less of a spike).
Remaining (nitpicks): reference head is turned to the camera (ours straight, rest pose), so the ref face is frontal
while the body is at 3/4; reference ears are a bit broader/rounder at the base; the muzzle "W" is softer than in the
reference; ears from the pure side view are still a narrow wedge (0.05 m deep at the base).

## Result
tris 1362 (target ~900, ceiling ~1400): Pelvis 96, Spine1 76, Spine2 96, Neck1 20, Neck2 32, Head 164, Jaw 38,
Ear 2x32, Eye 2x14, Nose 8, Front/Hind Upper 4x44, Lower 4x44, Foot 4x60, Tail1 44, Tail2 44, Tail3 60.
Size: width 0.296 (ears; head 0.288, body 0.172) x length 0.413 (nose -> tail) x height 0.396 (ear tips);
nose -> rump 0.317, back 0.181, belly 0.048, crown 0.332, tail top 0.313. Pivot: root on the ground under the volume
centroid (geometry shifted +0.039 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 27 meshes + root empty, 1362 tris, dims 0.296 x 0.413 x 0.396, texture found in FMS_Kitten.fbm.

## Deviations
- Length: catalogue 0.25 m; with the reference proportions (head width = torso length, back 0.18) nose -> rump is
  0.317 (torso 0.237). Kept the back height and the reference proportions; scaling to 0.25 would drop the back to 0.14.
- Height 0.396 to the ear tips (back 0.181): the reference head + ears are ~2.2x the back height.
- Tris 1362 vs 900: closed parts with hidden joint bands (seam-free joints) and 12-sided head; within the lead's 1400.
- Facet shades: fur faces facing up (n.z > 0.8) use grey light, underside (n.z < -0.55) grey dark; the rest grey.
- Preview at 45 deg azimuth (reference ~10 deg for the turned head) so the tail is visible next to the head.

## Rig + clips (2026-11-21) - mesh unchanged (meshcheck vs the mesh-only FBX backup: 27 parts, max diff 0.0001 m = 4-decimal rounding; texture md5 unchanged)
Files: `rig_kitten.py -- PET-04 bend|anim|export|meshcheck|lowdbg` (copy of ../Cat/rig_cat.py: QC 25 bones, spine/neck/tail
paths, knee line, thigh tops 70/30), `kitten_clips.py` (copy of ../Cat/cat_clips.py + the Dog rest-offset IK). Kitten leg:
upper 0.074, knee band 0.018, paw 0.018 m -> any leg shortening folds the tiny knee band hard (ankle angles > limits, band
dips into the ground), so the clips keep the legs nearly straight: short quick steps, almost no crouch.
| Clip | s / frames | content |
|---|---|---|
| Idle | 3.5 / 105 | tail S-wave x2, 2 breaths, head turn + small tilt, 3 ear twitches (Cat Idle copy) |
| Walk | 0.5 / 15 | lateral sequence, 0.15 m/s, step 0.046 m, duty 0.62, paws at 85 % track, spine yaw 2 deg; Footstep x4 |
| Pounce | 2.0 / 60 | head low + ears forward + tail low, butt wiggle (pelvis yaw 7 x2, tail tip twitch) -> spring forward/up (body +3 cm fwd, 2.6 cm up, pitch -16, front paws reach 7 cm ahead, hind paws hop along) -> land head down on the "prey", tail flick -> all paws bounce back -> stand; Pounce f28, Land f36 |
Metrics: loop closure 0.000 deg; lowest vertex Idle -0.6 mm, Walk -3.8 mm, Pounce -3.5 mm (limit scaled to the kitten: -6 mm);
Walk slip 3.16 % of step; limit violations 0. FBX re-import: 25 bones, 27 meshes, 1362 tris, 3 takes, vertex error 0.0 m.
GIFs: Kitten_Idle 2.66 MB, Kitten_Walk 0.55 MB, Kitten_Pounce 1.58 MB.
Rounds: Walk 5 (foot angles > limits and -13 mm dips with the 0.8 s / 0.18 m stride; non-integer frame count 13.5 gave 4-6 %
slip -> T 0.5 s, step 0.046 m), Pounce 3 (hind paws over-stretched -> hop along; bigger air phase).
Remaining: the crouch is only 3 mm (legs cannot fold without tearing/dipping) - the pounce reads through head, tail,
wiggle and the leap; in the leap the front legs reach straight and do not touch their target until landing (airborne);
not seen in Unity.
