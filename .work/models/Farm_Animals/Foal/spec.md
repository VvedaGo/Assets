# LIV-10 Foal - spec (Farm Animals, skeleton Q-H, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-10.png` (1312x1199). Foal stands with the body seen from the front-left
(near = foal's left side, +X), camera ~40 deg off the front axis, ~12 deg above; the face is seen almost frontally.
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-10 - light brown, long thin legs, short mane, 1.4 x 1.1 m, 1800 tris, Q-H.
Lead brief: big head (~140-150% of real), short muzzle, big upright ears, short fluffy dark mane + tuft forelock, long slim
legs (unlike the calf), dark socks and hooves (hoof neutral dark grey like the horse), short tail with a dark tuft,
dark disc eyes #2A1D17. Target ~1800 tris, limit +15% = 2070.
Anchors followed: Horse (`../Horse/build_horse.py` - Q-H part names, tuck joints, crest ridge, forelock strands, leg rings,
tapered leg tops, COM pivot, check sheet, preview template) and Calf (baby proportions: big head, shorter body).
Script: `build_foal.py -- LIV-10 build|look|export`.

## Measured from the reference (ground y~1120 px, back top y~440 px -> withers 1.10 m => ~0.00165 m/px at the body,
~0.0015 m/px at the near legs, head nearer the camera)
| Feature | px | model (m) |
|---|---|---|
| withers / back | 665-680 above ground | 1.10 |
| belly underside | y ~700 -> 420 above ground | 0.65-0.67 (long legs: leg ~60% of height) |
| ear tips | y 10 (head nearer, inflated) | ~1.75 |
| head width at the eyes / muzzle | 315 / 170 | 0.33 / 0.20 |
| head poll -> muzzle | 390 projected | 0.56 along the head axis (tilt 60 deg) |
| eye | ~50, octagon | 8-gon, apothem 0.034, 5 mm proud |
| ear height / base width | 170 / 70 | 0.27 / 0.13 |
| forearm / knee / cannon / hoof width (near front leg) | 95 / 95 / 72 / 98 | 0.14 / 0.13 / 0.10 / 0.13 |
| knee / hock / fetlock height | y 860 / 830 / 1040 | 0.42 / 0.44 / 0.15 |
| hoof height | 60 | 0.09 |
| tail root / tip | y 480 / 870 | z 1.02 / 0.38, blade ~0.16 deep |

Colours sampled: body #B47D55..#C78C62 -> #BA8158; muzzle #8B6147; mane #3F2C22; tail #47342B; ear inside #8E5C3D;
hoof (reference) #503C31 dark brown.

## Features (must read at 128 px)
compact barrel body (12 sides), raised withers; thick upright neck (10 sides) with a dark saw-tooth crest mane (short
tufts leaning back, symmetric); big head (10 sides) tilted 60 deg, wide forehead/cheeks, short tapering muzzle with a
darker muzzle pad, 2 dark nostrils, chin block; big dark 8-gon eye discs on the front corners of the face; big upright
pointed ears (brown outside, darker inner) at the top corners of the head; dark tuft forelock (3 strands) between the ears;
long slim 8-sided legs with forearm/thigh tapering into the body, knee and hock bulge, fetlock band, dark pastern sock and
dark hoof; short dark tail: dock + blade + 3 pointed strand tips.

## Material class
Flat palette `T_FarmAnimals_Foal_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Foal`: 0 body #BA8158, 1 body light (spare),
2 mane #3F2C22, 3 mane 2 #4E382B, 4 ear inside #8A5A3C, 5 nostril #3A251B, 6 eye #2A1D17, 7 hoof #3F3A39,
8 sock #5E4434, 9 muzzle #8B6147, 10-15 series spares.

## Parts (object `FMS_Foal_<Part>`, direct children of empty `FMS_Foal`, pivot on the joint; Horse Q-H names)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nostrils, Forelock, Mane1/2/3,
Front/Hind Upper/Lower/Foot .L/.R (Foot = pastern + hoof, pivot at the fetlock), Tail1 (dock) / Tail2 (blade) / Tail3 (tips).

## NOT modelled
halter, teeth/tongue, eyelids/pupils, nostril holes, individual hairs, chestnuts/ergots, ground; head turn (rest pose
is straight forward).

## Rounds (checked at the reference angle + side, front, back, top, far side; 128 px thumbnail)
1. Adult-horse head (small, long, eyes on the sides), body long/narrow, thin neck, 2244 tris (> 2070); nostrils ray-cast
   onto the poll (wrong ray direction) -> head shorter + wider, scale 1.15, body 1.0 -> 0.93 m, neck +12%, legs x1.15,
   one ring less on upper/lower legs, 6-sided jaw, 3-ring dock (2060 tris), nostril ray fixed.
2. Head still long, dark muzzle covered half the face, narrow chest -> HEAD_LEN 0.44, muzzle colour only on the last
   third, barrel half width 0.238, legs spread 0.135/0.138.
3. Head ~23% of the height vs ~28% in the reference, mane/forelock thin -> HEAD_SCALE 1.30, tilt 64 (face more upright),
   ears -10% height, mane tufts 0.15-0.16 high and 0.12-0.15 wide, forelock raised 4 cm.
4. Narrow muzzle with nostrils underneath, narrow ears, eyes high, flat chest -> flared muzzle pad, nostrils on the
   front of the pad, ears +15% wide, eyes lower (s 0.175), chest front 3 cm forward.
5. Eyes still mostly side-on from the front, nostrils made a dark beak side-on -> eye axis toward the front (reads like
   the reference from the front), nostrils 1.5 cm back and 3 mm proud.
Remaining (nitpicks): the reference turns the head toward the camera (ours straight for the rig); the reference body is
slightly rounder/shorter in the flank; the forelock is a spiky crown rather than a soft tuft.

## Result
tris 2060 (target 1800, +14.4%; limit 2070): Spine1/Spine2 116, Pelvis 92, Head 156, Neck2 76, Neck1 56, Jaw 44,
Ear 56 x2, Eye 28 x2, Nostrils 40, Forelock 84, Mane1/2/3 36/44/60, Upper 76 x4, Lower 60 x4, Foot 60 x4,
Tail1/2/3 44/60/84.
Size: width 0.504 x length 1.726 (nose -> tail tip) x height 1.682 (ear tips); nose -> rump 1.416; withers (body top)
1.094; belly 0.662; head width 0.455 (head group scaled 1.30 about the poll).
Pivot: root on the ground under the volume centroid (geometry shifted +0.184 m in Y; x = 0 symmetry plane); parts pivot
on their joints (Horse scheme). Joint overlaps: body tucks 0.04 m, neck 0.03, mane chunks 0.03, tail 0.035, leg
upper->lower 0.025-0.045, lower->foot 0.025.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, worst contact gap 0.0, mirror 0.000000 (all parts), min z 0.
FBX re-import: 31 meshes + root, 2060 tris, dims 0.504 x 1.726 x 1.682, texture found in FMS_Foal.fbm.

## Rework r2 (coordinator, independent review 3/5) - supersedes the Result numbers above
Defects: adult-horse head (long, narrow, small eyes); two-tone hoof (sock band + black cap) step; thin body.
1. Head: muzzle (eyes -> tip) 0.265 -> 0.20 (-25%), HEAD_LEN 0.44 -> 0.375, cranium rings +15%, head 12 sides,
   HEAD_SCALE 1.30 -> 1.25 (head width 0.487), muzzle colour on the last 1/3; eyes flush 8-gon discs (2 mm proud),
   placed forward on the face, diameter 0.097 = 0.177 x head height 0.550; forelock = 3 short tapered strands (0.14/0.11,
   blunt tips 32% width, 1-2 cm off the forehead) -> soft tuft.
2. Legs: Upper and Lower each ONE tapered 8-sided prism (top apothem 1.15 x bottom; Upper keeps a hidden root ring
   inside the body), no knee/hock/fetlock rings, LEG_K 1.25; Foot = brown pastern + ONE dark-brown hoof cap #4A3527
   flaring to the ground (shared ring, no band, no step). Sock removed (reference legs plain brown).
3. Body +10% wide and deep (top line kept, belly 0.662 -> 0.618), neck rings +10%; legs spread 0.15/0.152.
Preview camera = reference 3/4 view (0.85, -1.0, 0.22).
Result r2: tris 1772 (target 1800, -1.6%): Head 188, Spine1/Spine2 116, Pelvis 92, Neck1/2 56/76, Jaw 44, Ear 56 x2,
Eye 28 x2, Nostrils 40, Forelock 84, Mane1/2/3 36/44/60, Upper 44 x4, Lower 28 x4, Foot 44 x4, Tail1/2/3 44/60/84.
Size 0.510 x 1.676 x 1.684 m; nose -> rump 1.376; withers 1.094; belly 0.618. Checks: non-manifold 0, loose 0,
degenerate 0, coplanar 0, mirror 0.000000, worst gap 0, min z 0. FBX re-import: 31 meshes + root, 1772 tris,
dims 0.510 x 1.676 x 1.684, texture found in FMS_Foal.fbm. Views: reference angle, side, front, back, top, far, 128 px.
Remaining: no knee/hock bulge (the reference shows slight ones; removed on the coordinator's instruction); head straight.

## Deviations
- Hoof one dark-brown cap #4A3527 (r2; r1 used neutral grey with a sock band).
- Legs without joint rings (coordinator r2), the reference shows slight knee/hock bulges.
- Tail all dark (as in the reference), not a body-coloured dock with a dark tuft.
- Head straight (the reference turns it slightly toward the camera).
- Ear tips 1.68 m (the reference looks taller because the head is nearer the camera).
- No LOD1 (mesh-only round).

## Rig + clips (rig_foal.py + foal_clips.py; copy of Horse/rig_horse.py + horse_clips.py, mesh unchanged)
- Skeleton Q-H, 29 bones (Horse names: + Forelock, Mane1-3), armature 'Rig'; 31 parts joined into ONE skinned mesh FMS_Foal
  (958 verts, 1772 tris), rigid 1.0 per part (Eye.L/R + Nostrils -> Head). Horse bone-table constants (Pelvis head, Spine2
  tail, ear/jaw/forelock/mane/tail tail lengths) scaled by body height (Spine1 pivot z / 1.30).
- Horse rest-offset leg IK (hind hock rests at 18.7 deg, foot 5.3 deg) + pastern-tilt stance (foot_tilt), breathing on the
  back line only; horse-local limits (HindLower x -140..30).
- Clips 30 fps, in place: Foal_Idle 3.0 s / 90 f (Horse idle: breathing, ear swivels + flicks, tail swish, mane/forelock);
  Foal_Walk 0.9 s / 27 f (four-beat LH-LF-RH-RF, 0.80 m/s, step 0.43 m, roll 1.2); Foal_Trot 0.6 s / 18 f (two-beat
  diagonal pairs, duty 0.44 with suspension, 1.9 m/s, step 0.50 m, lift 0.13, hoof flick 50/38 deg, body compression 22 mm
  at mid-stance, tail lifted 14 deg, livelier mane).
- Metrics: loop closure 0.000 deg all; lowest vertex Idle 0.000 / Walk -0.0003 / Trot 0.000 m; slip Walk 0.23 % / Trot 0.0 %
  of step; joint-limit violations 0; legs never cross the midline.
- Bend test: legs, neck down/yaw, ears, tail, mane, spine closed; extreme head-UP pose opens the Neck2/Head seam (as Horse; no
  clip uses it).
- FBX re-import: 29 bones, 1772 tris, takes 90/27/18 f, vertex error 0.0 m, texture found. Events FMS_Foal.events.json
  (Footstep x4 per gait). GIFs Foal_{Idle,Walk,Trot}.gif.
