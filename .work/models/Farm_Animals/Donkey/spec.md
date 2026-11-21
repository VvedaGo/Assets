# LIV-11 Donkey - spec (Farm Animals, skeleton Q-H, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-11.png` (1312x1199). Donkey seen from the front-left (near = its left side,
+X), camera ~40-45 deg off the front axis, ~12 deg above; the head is turned toward the camera (face almost frontal).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-11 - grey, light muzzle, long ears, black cross on the back, 1.9 x 1.3 m, 2100 tris, Q-H.
Lead brief: grey-brown body, cream muzzle and belly, very long upright ears with dark tips and cream inside, short stiff
upright mane (brush), dark cross stripe (withers band + dorsal stripe), thin tail with a dark tuft, sturdier shorter legs
than the horse, dark hooves (neutral dark grey), dark disc eyes #2A1D17. Target ~2100 tris, limit +15% = 2415.
Anchors followed: Foal (`../Foal/build_foal.py`: big head group, saw-tooth crest mane, eyes on the face corners, muzzle
colour by head segment, tapered leg tops) and Horse (`../Horse/build_horse.py`: Q-H part scheme, tuck joints, COM pivot,
check sheet, preview template). Script: `build_donkey.py -- LIV-11 build|look|export`.

## Measured from the reference (ground y~1080 px under the body, back top y~400-450 -> 1.3 m => ~0.0019 m/px at the body;
head and near legs are nearer the camera, ~1.1x)
| Feature | px | model (m) |
|---|---|---|
| withers / croup | ~630-645 above ground | 1.30 / 1.29 |
| belly underside | y ~760 -> ~310 above ground | 0.62 (short legs: leg ~48% of height) |
| poll / ear tips | 780 / 1085 above ground (head nearer) | poll ~1.55, ear tips ~2.0-2.05 |
| head poll -> muzzle bottom | 430 (frontal, foreshortened) | 0.70 along the head axis (tilt 58 deg) |
| head width at the eyes / muzzle | 260 / 155 | 0.46 / 0.28 |
| cream muzzle | lower 41% of the head | head segments from s 0.31/0.535 |
| eye | ~30, octagon, at 43% of the head | 8-gon, dia ~0.065, 5 mm proud |
| ear length / max width | 315 / 90, splayed ~15 deg out | 0.49 / 0.16 |
| mane brush | ~60-70 high, dark, jagged top | 0.09-0.15 high, 0.10 wide |
| cross stripe width / dorsal stripe | 45 / ~35 | 0.09 / 0.10 |
| forearm / cannon / hoof width (near front leg) | 90 / 75 / 95 | 0.21 / 0.15 / 0.18 |
| knee / hock height | 220 / 230 | 0.40 / 0.43 |
| hoof height | 60 | 0.10 |
| tail root / tuft / tip | y 440 / 640 / 770 | z 1.18 / 0.78 / 0.50; tail 0.05 thick, tuft 0.13 wide |

Colours sampled (lit/shade): body #A49C9B/#827A7A -> #908887 (task: grey-brown); muzzle #D8C9C0 -> #E0D2C6;
stripe/mane/tuft #4A4444 -> #403A3A / #383232; inner ear lighter warm grey -> cream #D6C7B9; hooves #3C3B3E.

## Features (must read at 128 px)
big head (10 sides) tilted 58 deg, broad forehead and cheeks, narrower muzzle with a cream flared pad, 2 nostrils, cream
chin block; dark 8-gon eye discs on the front corners of the face; VERY long upright leaf ears (cupped, cream inside, grey
outside, dark tips) splayed ~15 deg; dark upright tuft between the ears + short stiff upright brush mane with a jagged top
along the crest (symmetric); thick short neck; stocky barrel body (12 sides) with a dark dorsal stripe (one narrow top
facet, constant 0.10 m) from the withers to the tail and a slanted dark cross band over the shoulders; light cream belly
strip; short thick 8-sided legs, forearm/thigh tapering into the body, knee/hock bulge, fetlock bulge, dark flared hooves;
thin grey tail (dock + tail) ending in a dark pointed tuft.

## Material class
Flat palette `T_FarmAnimals_Donkey_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Donkey`: 0 body #908887, 1 body shade
(spare), 2 mane #383232, 3 mane 2 #463F3E, 4 inner ear cream #D6C7B9, 5 nostril #7F6D66, 6 eye #2A1D17, 7 hoof #3C3B3E,
8 stripe #403A3A, 9 muzzle cream #E0D2C6, 10 belly cream #C9BDB2, 11-15 series spares.

## Parts (object `FMS_Donkey_<Part>`, direct children of empty `FMS_Donkey`, pivot on the joint; Horse Q-H names)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nostrils, Forelock, Mane1/2/3,
Front/Hind Upper/Lower/Foot .L/.R (Foot = pastern + hoof, pivot at the fetlock), Tail1 (dock) / Tail2 (tail) / Tail3 (tuft).

## NOT modelled
halter, saddle/packs, teeth/tongue, eyelids/pupils, nostril holes, individual hairs, leg zebra stripes, chestnuts, ground;
head turn (rest pose is straight forward for the rig).

## Rounds (reference angle + side, front, back, top; 128 px thumbnail)
1. Head/ears too small and narrow vs the reference, muzzle not bulbous, legs thinner than the reference, eyes invisible
   from the front, mirror 0.011 (tail tuft ridge phase) -> HEAD_SCALE 1.40, ears +30% wide, muzzle rings +12% wide,
   LEG_K 1.28, eye apothem 0.028 turned toward the front, tuft ring phase 0 (mirror 0.000000).
2. Ears short (ear/head ~0.6 vs 0.73), inner ear and muzzle near white, slim shallow barrel (chest narrower than the head
   from the front) -> ears +20% long, cream toned down, belly 0.625 -> 0.57, barrel half width 0.315 -> 0.34, legs 0.19 apart.
3. Ear fronts still read as all-cream (reference: grey ear, lighter inner strip); cross band stopped above the belly line
   -> cream only on the inner middle strip + lower inner slopes, cross band down to the belly strip.
Remaining (nitpicks): head straight (the reference turns it toward the camera); in the preview angle the thin tail is
mostly hidden behind the rump (visible from the side/back); inner ears are more cream than the reference (lead brief).

## Result
tris 2144 (target 2100, +2.1%): Spine2 164, Spine1 116, Pelvis 116, Neck1 56, Neck2 76, Head 176, Jaw 44, Ear 80 x2,
Eye 28 x2, Nostrils 40, Forelock 26, Mane1/2/3 46/56/76, Upper 76 x4, Lower 60 x4, Foot 60 x4, Tail1/2/3 32/44/76.
Size: width 0.669 x length 2.183 (nose -> tail) x height 2.071 (ear tips); nose -> rump 1.951; withers 1.299; belly 0.571;
head width 0.482; head top 1.596.
Pivot: root on the ground under the volume centroid (geometry shifted in Y; x = 0 symmetry plane); parts pivot on their
joints (Horse scheme). Overlaps: body tucks 0.04 m, neck 0.035, mane chunks 0.03, tail 0.035, leg upper->lower 0.04,
lower->foot 0.02.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, worst contact gap 0.0, mirror 0.000000 (all parts), min z 0.
FBX re-import: 31 meshes + root, 2144 tris, dims 0.669 x 2.183 x 2.071, texture found in FMS_Donkey.fbm.

## Deviations
- Dark ear tips (lead brief); the reference ears are grey to the tip.
- Light cream belly strip (lead brief); the reference belly is grey.
- Nose -> rump 1.95 m (catalogue 1.9, +3%); ear tips 2.07 m.
- Head straight for the rig (the reference turns it toward the camera). No LOD1 (mesh-only round).

## Rig + clips (rig_donkey.py + donkey_clips.py; copy of Horse/rig_horse.py + horse_clips.py, mesh unchanged)
- Skeleton Q-H, 29 bones (Horse names), armature 'Rig'; 31 parts joined into ONE skinned mesh FMS_Donkey (1136 verts,
  2144 tris), rigid 1.0 per part (Eye.L/R + Nostrils -> Head). Horse bone-table constants scaled by body height.
- Horse rest-offset leg IK (hind hock rest 15.6 deg), pastern-tilt stance, back-line breathing; horse-local limits.
- Clips 30 fps, in place: Donkey_Idle 4.0 s / 120 f (Horse idle: ears swivel 55 deg back-out in turn, flick, both forward,
  breathing, tail swish, mane/forelock); Donkey_Walk 1.0 s / 30 f (four-beat LH-LF-RH-RF, 0.85 m/s, step 0.53 m, lift 0.09);
  Donkey_Graze 5.0 s / 150 f (FrontL 0.20 m forward, body pitch 5 deg nose-down, Neck1 50 / Neck2 10 / Head -30 found by
  search with Neck1 <= 50 and Head >= -40, muzzle 0.03 m, 10 chews, 2 head lifts; Mane3 counter-rotated -0.6 x Neck1 so the
  withers mane piece stays on the back instead of hooking up).
- Metrics: loop closure 0.000 deg all; lowest vertex Idle 0.000 / Walk -0.0006 / Graze 0.000 m; Walk slip 0.28 % of step;
  joint-limit violations 0 (first pass had Head.x -51 in Graze -> search bound -40); legs never cross the midline.
- Bend test: legs, neck down/yaw, ears, tail, mane, spine closed; extreme head-UP pose opens the Neck2/Head seam (as Horse).
- FBX re-import: 29 bones, 2144 tris, takes 120/30/150 f, vertex error 0.0 m, texture found. Events FMS_Donkey.events.json.
  GIFs Donkey_{Idle,Walk,Graze}.gif.
