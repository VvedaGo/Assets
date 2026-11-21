# LIV-05 Lamb - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-05.png` (1536x1024, front-left three-quarter, ~20 deg above; head turned
towards the camera - modelled straight for the rig rest pose, see Deviations).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-05 - lamb, smaller, wool of 18-24 lobes, light face, 0.8 x 0.55 m, 1300 tris
(lead: +20% = 1560), skeleton Q. Lead brief: head ~150% of realistic, legs ~30% shorter relative to the sheep, rounder
body, small ears sideways, short tail, dark disc eyes #2A1D17.
Anchors followed: Sheep (`../Sheep/build_sheep.py`: puff/antiprism lobes, ell_point rows, tuck rings, part naming,
objects()/coplanar_all/check sheet, head-group scale about the neck joint), Cat/Cow (EEVEE preview template via
`_common/animal_render.preview`, read-only). Script: `build_lamb.py -- LIV-05 build|look|export`.

## Measured from the reference (ground ~940 px mid body, back top 385 px -> 0.55 m, ~1.0 mm/px; head nearer the camera
-> ~10% inflated)
| Feature | px | model (m) |
|---|---|---|
| wool back top | 555 above ground | 0.57 |
| wool belly bottom | 150-180 above ground | 0.136 |
| head tuft top | ~925 above front ground | 0.90 (perspective-inflated in the ref) |
| face width at the eyes | ~355 | 0.37 (head group x1.22) |
| eye diameter | ~50 | 0.052 (8-gon) |
| ear length / width | ~176 / ~110 | 0.18 visible / 0.13, 0.04 thick |
| leg width / hoof width | ~80 / ~90 | 0.104 / 0.117 (6-gon) |
| hoof height | ~60 | 0.06 |

## Features (after rework round 2)
Wool: 30 faceted lobes + tail puff = 19 body (Wool_Spine2 4, Wool_Spine1 9, Wool_Pelvis 6) + chest bib and chin puff
(Wool_Neck 2) + 9-lobe hood (Wool_Head). Lobe = hidden apex + equator ring + top ring + flat top facet (22 tris), sunk 21%.
One warm off-white #EEE9E2; up-facing facets #F5F1EA, down-facing #E9E0D1 (by facet direction), crevice core #DCD0BE.
Head: cream 8-sided loft (28 deg down), head group x1.22 then moved 0.030 back / 0.036 down so the chin sinks into the
chest wool; pointed muzzle, small soft nose, light jaw; eyes 8-gon dark discs 6 mm proud; ears = thin flat cream leaves (round 3): 0.20 m visible (0.55 x face width 0.371), 0.044 m thick (0.12 x),
0.107 m wide, pointing sideways 13 deg down and 15 deg forward (no backward sweep), leaf face turned forward/up,
slightly darker cream inner #EAD0AE, roots sunk 4 cm, .R = exact mirror of .L.
Legs: one tapered cream prism per leg (Upper + Lower tucked 1.5 mm, top apothem 1.15 x bottom 0.046 m), no band,
dark hoof cap 0.06 m. Tail: stub + 0.084 m puff at the rear of the rump, mid-height (z 0.42).

## Material class
Flat palette `T_FarmAnimals_Lamb_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Lamb`. Cells: 0 wool up #F5F1EA, 1 wool base
#EEE9E2, 2 wool down #E9E0D1, 3 core #DCD0BE, 4 face #F4DFBF, 5 face shade #EBD2B0, 6 leg #EED5B2, 7 spare (= leg),
8 eye #2A1D17, 9 hoof #3A2E28, 10 ear inner #EAD0AE, 11 nose #E6BE9E, 12-15 series spares.

## Parts (object `FMS_Lamb_<Part>`, direct children of empty `FMS_Lamb`, pivot = joint) - same names as Sheep
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R, Tail1, Tail2,
Wool_Pelvis/Spine1/Spine2/Neck/Head (-> Pelvis/Spine1/Spine2/Neck1/Head). Joints overlap (tuck rings, sunk ends).

## NOT modelled
mouth line, teeth, eyelids, individual curls, ground/shadow plate, collar/bell, Tail3.

## Rounds
1. (Workbench) head small vs body (0.35 vs 0.43 m), muzzle a long beak-like wedge, body lobes stick out as balls.
   -> head group x1.12, shorter blunt muzzle, lobes sunk deeper, bigger hood lobes, wider ears.
2. (EEVEE) legs thin/long, body narrower than the head, head still small, salmon inner ear/nose.
   -> legs 0.104 m + hooves 0.117 m, core wider and lower, head x1.22, back crown lobe (nape lobe dropped), beige ear inner.
3. near ear hidden behind the cheek lobe, flat muzzle end + nose pad read as a pig snout, face tilted down.
   -> ear root forward + pointing slightly forward, tilt 28 deg, narrower muzzle tip.
4. (preview check) snout still pig-like from the low preview angle -> pointed muzzle end, nose pad 0.02 m, low contrast.
Polish pass (coordinator, 7 items): smaller regular body lobes (19 x ~0.12 m, low jitter, row phases), hood 9 lobes
(closed cap from behind), lobes sunk deeper (no spiky balls in side/back view), hidden-apex lobes/eyes/nose and 2-ring
neck (-134 tris), longer/wider ears pointing sideways, muzzle light (throat shade only behind), body wider (0.55 m),
tail puff larger, white/cream contrast up. Views checked: 3/4 ref, preview, side, front, back, low, top + 128 px.
Rework round 2 (review 3/5): head moved down/back + chin puff (no gap from any side incl. low view); ears horizontal
cream flaps; wool one warm off-white by facet direction; knee bands removed, tapered legs; tail at rump mid-height.
Views checked: reference 3/4, preview, side, front, back, top, low + 128 px.
Rework round 3 (ears, review 3/5): puffy peach ears swept back -> thin flat cream leaves pointing sideways/down,
15 deg forward so the far ear clears the face in the 3/4 view; both ears visible in front, 3/4, preview and top views.
Remaining (nitpicks): ref head turned to the camera (ours straight for the rig); wool facets in shadow pick up the blue
sky fill of the shared preview lighting (palette is warm); the preview uses the pack template camera (3/4 front-left, low).

## Deviations
- tris 1352 vs 1300 (+4%).
- wool lobes 30 (+ tail puff) vs catalogue 18-24: the reference shows smaller, more numerous lobes; reference wins.
- height 0.884 m to the hood top (catalogue 0.55 = back height; wool back top 0.559); length 0.858 m nose-tail (cat. 0.8);
  width 0.721 m incl. ears (wool body 0.551).
- skeleton Q tail: Tail1 + Tail2 only (no Tail3), same as Sheep.
- Nose: the reference shows no nose pad; a small low-contrast pad exists for the rig part.
- pivot: root on the ground under the volume centroid (geometry shifted +0.069 m in Y).

## Rig / animation (rig_lamb.py + lamb_clips.py; mesh, part names, Wool_* groups and pivots unchanged)
- Skeleton Q-S as the Sheep: Q without Horn.L/R and Tail3 = 24 bones, armature `Rig`; bone heads = part pivots, Ear bones
  along the leaf (0.20 m), Tail1-2. check_rig names/hierarchy OK, roll_bad [].
- Binding: 31 parts, each ONE vertex group weight 1.0 (Eye/Nose/Wool_Head -> Head, Wool_Neck -> Neck1, Wool_Spine2/1 ->
  Spine2/1, Wool_Pelvis -> Pelvis). Bend test (legs +-45..60, knees 150, neck down/up/yaw, ears +-50..60, tail 70, body
  pitch 20/roll 12): no holes -> no 2-bone blends needed.
- Clips (30 fps, in place): Lamb_Idle 3.0 s/90 f (2 breaths, head drift, ear flicks, tail wiggle + burst);
  Lamb_Walk 0.7 s/21 f (lateral sequence, duty 0.58, 0.22 m/s, step 0.089 m, lift 3.2 cm, head bob, wool lag);
  Lamb_Play_Hop 1.0 s/30 f (squash 3.0 cm -> push -> all four feet off frames 8-20, arc 0.10 m, pitch +-6 deg,
  legs tucked -> land -> squash; ears/tail/head lag; Footstep events Takeoff f8 / Land f20).
- Metrics: closure 0.0 deg (all); lowest vertex Idle 0.0 / Walk -1.3 mm / Hop 0.0; walk slip 2.23% of step; joint-limit
  violations 0 (hop squash limited to 3 cm by FrontFoot x >= -60: worst -58.2).
- FBX: 31 skinned parts + Rig, takes Lamb_Idle 90 / Lamb_Walk 21 / Lamb_Play_Hop 30 f; re-import 24 bones, 31 meshes,
  1352 tris, vertex error 0.0 m, texture found. Events: FMS_Lamb.events.json. GIFs: art/Farm_Animals/Previews/Anim/Lamb_*.gif.
