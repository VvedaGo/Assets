# BRD-03 Chick - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-03.png` (1312x1199, near-front view, chick yawed ~22 deg towards its own
right, so the camera sees the face and a little of the left (+X) side; tail nub shows on the image right; ~8 deg above).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-03 - yellow ball with a small beak and thin legs, 0.15 x 0.15 m, 350 tris, skeleton B.
Lead brief: golden yellow #D8B65A, huge round head, tiny orange pointed beak, very short thin orange legs (8-10 mm thick),
three toes, tail nub, stub wings, dark disc eyes #2A1D17 readable at 128 px.
Anchors followed: BRD-01 Hen (`../Hen/build_hen.py` + spec: part names, joints dict, split_to_objects, ray-cast eyes with a
buried pyramid back, toes with a sloped sole, check sheet + EEVEE preview via `_common/animal_render.py` read-only);
Piglet/Lamb (baby proportions: head ~1.3x body, short legs). House style 11/11b.

## Measured from the reference (ground y 1140 px, head top y 30 px -> 0.150 m => 0.000136 m/px)
| Feature | px | m (design) |
|---|---|---|
| head width / height | 815 / 670 | 0.108 / 0.094 (ellipsoid 0.054 x 0.050 x 0.047, centre z 0.103) |
| head top | y 30 | 0.150 |
| body width / visible height | 620 / 415 | 0.084 / 0.056 (ellipsoid 0.043 x 0.041 x 0.031, centre z 0.040) |
| head centre ahead of body centre | 43 px at 22 deg yaw | 0.016 |
| eye centre / diameter / spacing | y 445 / 65 / 305 | z 0.094 / 0.011 (8-gon, 1.3x ref for 128 px) / x +-0.024 |
| beak centre / width / height | y 525 / 100 / 110 | z 0.084 / 0.015 / 0.014, 0.012 out of the face |
| leg visible incl. foot / width | 80 / 45 | 0.012 / 0.0084 (6-gon, brief 8-10 mm) |
| legs apart | 210 | x +-0.016 |
| tail nub | 75 x 115, up-back ~40 deg | 0.022 long, 0.014 wide root |

## Features (must read at 128 px)
Two faceted balls (geodesic-like: staggered 10-gon rings + pentagon caps, no pole fans, no discs): big head on a smaller
body with a soft crease (Neck fills it, no ledge); dark 8-gon disc eyes 2 mm proud; small orange two-tone diamond beak
(upper light, lower dark); stub wings; tail nub; short orange legs with 3 toes.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Chick on the ground under the centre of mass)
Body, Neck (single part, documented: binds to Neck1/Neck2), Head (+ upper beak), Beak_Lower, Eye.L/.R,
WingUpper.L/.R (shoulder root), WingLower.L/.R (stub incl. tip; WingTip merged, documented), TailFan1 (nub),
LegUpper.L/.R (hidden thigh inside the body), LegLower.L/.R (shank), Foot.L/.R (3 toes).

## Material class
Flat palette, own atlas `T_FarmAnimals_Chick_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Chick`.
0 body #D8B65A, 1 body dark (belly underside) #C9A64E, 2 body light (spare), 3 wing #C8A048, 4 wing dark, 5 beak #EE8A2A,
6 beak dark #C8681A, 7 leg #EE8A2A, 8 leg dark, 9 eye #2A1D17, 10-15 series spares.

## NOT modelled
ground, down fluff strands, nostrils, eyelids, claws, leg scales, back toe. No armature/weights/clips.

## Rounds (Workbench sheet: ref + ref view, side, front, back, rear 3/4, top, high front; EEVEE at ref and preview views; 128 px)
1. 386 tris, mirror 12 mm (pentagon caps at phase 0 not X-symmetric), wing a forward spike, body small and flat-topped so the
   neck read as a collar, eyes read as tilted pyramids. -> pentagons phase 18, body 5 rings + pentagon bottom, neck 33 mm.
2. Eyes: disc on the smooth normal blended with the facet, offset solved by ray casts (0.9 mm min above the facets);
   body lowered (visible leg 14 -> 11-12 mm); 3-gon thigh phase 90 (mirror 0).
3. (EEVEE) collar ledge under the head; wing crumpled (points followed the facets); beak small. -> body taller (c 0.040,
   crease at z ~0.067 like the reference), wing points from the smooth ellipsoid, beak +8 %.
4. Wing double ridge -> WingUpper tucked under WingLower, ridge lowered (hanging paddle, 6.5 mm proud), wing cell darker.
Remaining nitpicks: wing reads a little busy in the shadow side of the preview; eye discs 0.9-2.9 mm proud (straddle a
facet edge); reference has no visible wings and block feet.

## Result
406 tris (target 350, +16 %, limit 420): Head 100 (incl. upper beak 4), Body 86, Neck 28, Foot 24 x2, LegLower 20 x2,
Eye 14 x2, WingLower 14 x2, TailFan1 12, LegUpper 8 x2, WingUpper 8 x2, Beak_Lower 4.
Size W 0.107 x L 0.128 (beak tip -> tail tip) x H 0.147 m; visible leg 12 mm, leg 9 mm thick (6-gon apothem 4.5/4.0 mm).
Pivot: root on the ground under the volume centroid (geometry shifted +0.0065 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000, worst contact gap 0, lowest z 0.
FBX re-import: 17 meshes + root, 406 tris, dims 0.107 x 0.128 x 0.147, texture found in FMS_Chick.fbm.

## Deviations
- Length 0.128 m vs catalogue 0.15 (reference is a round ball, head depth ~0.10); height 0.147.
- Feet: 3 toes (lead brief) instead of the reference's hexagonal foot blocks; no back toe.
- Stub wings added (brief); the reference shows none.
- Colours: brief #D8B65A body (reference renders warmer, ~#F0C257).
- Eyes 13 mm vs ~9 mm measured (1.4x, for 128 px readability).
- Single Neck part (bind to Neck1/Neck2 later); WingTip merged into WingLower; LegUpper is a hidden 3-gon thigh inside the body.

## Rig (skeleton B adapted, 16 bones) - rig_chick.py + chick_clips.py (copies of ../Hen/rig_hen.py, hen_clips.py)
Run: `rig_chick.py -- BRD-03 bend|anim|export`. Mesh, part names and pivots unchanged from `build_chick.build()`.
- Bones (16, only parts that exist): Root > Body > {Neck > Head > Beak_Lower; WingUpper > WingLower (.L/.R);
  TailFan1; LegUpper > LegLower > Foot (.L/.R)}. Not present vs the Hen: Neck1/Neck2 (one Neck), WingTip (merged into
  WingLower), TailFan2. Eye.L/.R bound to Head; Neck blends 50/50 with Body at its head (+-6 mm) and Head at its tail (+-4 mm).
- Code changes vs the Hen besides the table: look() twists Neck; walk head bob = Neck pitch asin(-dy / neck length);
  peck uses neck_to_tip_z (Neck pitch solved for the beak height, head held at a set angle); neck-yaw metric on Neck;
  bend poses for one neck. LegUpper x limit widened to -130 (hidden thigh compensates the 34 deg peck body pitch).
- Bend test (8 extreme poses): no holes; neck bent far back shows the yellow neck ring under the chin (closed).

## Clips (30 fps, in place, NLA takes + bake_space_transform)
| Clip | s / frames | content |
|---|---|---|
| Idle | 3.0 / 90 | 5 quick breaths, head turns in 2-frame snaps (yaw <= 38, tilt <= 14 deg), 2 wing flutters, tail wag |
| Walk | 0.533 / 16 | 0.06 m/s, step 0.018 m, duty 0.55, lift 6 mm; head held in space 55 % of a step (0.009 m travel) then snaps forward; waddle, tail bob, wing twitch each step; Footstep LegL f0, LegR f8 |
| Peck | 2.0 / 60 | body tilts 30 deg + 4 deg jabs, drop 3 mm, 4 quick pecks (beak tip 3 mm above the ground) f18/25/32/38, cocked looks, tail up 20 deg; Peck events |
Metrics: loop closure 0.000 deg / 0.000 m (all); lowest vertex Idle -0.3, Walk -1.3, Peck -1.2 mm (tolerance used -2 mm =
the -1 cm rule scaled to the chick (0.37x the hen) and rounded down); Walk foot slip 0.13 % of the step; limit violations 0.
FBX re-import: 16 bones, 17 meshes, 406 tris, takes Chick_Idle/Walk/Peck (frames 1..91/17/61), vertex error 0.0 m on all
takes, texture found. Rounds: 1 per clip.
Remaining: the peck is mostly body tilt + head rotation (one short neck bone); not seen in Unity.
