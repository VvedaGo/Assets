# LIV-03 Horse - spec (Farm Animals, skeleton Q-H, MESH ONLY this round)

Reference: `planning/FarmAnimals/references/LIV-03.png` (1312x1171, near = horse's left side (+X) from the front-left,
~10-15 deg above; the head is turned slightly toward the camera - modelled straight for the rig).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-03 - bay: brown body, black mane/tail/socks, mane 6-8 thick strands,
2.4 x 1.65 m, 2600 tris, skeleton Q-H (Q + Mane1-3 + longer tail).
Anchors followed: Cat (`../Cat/build_cat.py`: separate parts with skeleton names, tuck joints, per-face palette,
ray-cast placement, check sheet, `_common/animal_render.preview`), Cow (head frame along a tilted axis, leg rings,
hoof), house style 11/11b. Script: `build_horse.py -- LIV-03 build|look|export`.

## Measured from the reference (ground y~1120 px, back top y~370 px -> withers 1.65 m => ~0.0022 m/px)
| Feature | px | m (design) |
|---|---|---|
| withers / back | 740 above ground | 1.65 withers, back 1.59-1.63 |
| belly bottom | y 690 -> 430 above ground | 0.93 |
| ear tips | y 15 (head nearer the camera, scale ~1.1) | ~2.30-2.35 |
| head poll -> muzzle | 340 (foreshortened, ~58 deg down) | 0.77 along the head axis |
| head width at the eyes / muzzle | 175 / 120 (near camera) | 0.32 / 0.23 |
| eye | 25, hexagon | 6-gon disc, apothem 0.03 |
| ear height / base width | 110 / 55 | 0.25 / 0.12 |
| forearm / cannon (sock) / hoof width, near front leg | 110 / 85 / 105 | 0.20-0.25 / 0.16 / 0.20 |
| sock top | ~280 above ground | 0.62 front, 0.66 hind |
| fetlock band | y 1000-1040 | z 0.235-0.305, proud 13 mm |
| hoof height | 65 | 0.155 |
| tail: root / tip | y 410 / 960 | z 1.44 / 0.36, broad blade, 3 pointed strand tips |
| mane strands | 7 visible, tips 150 px below the crest | 0.22-0.34 long, 0.12-0.13 wide |

## Features (must read at 128 px)
slim faceted barrel body (14 sides) with raised withers and croup; deep tall neck (10 sides) with black crest ridge and
7 thick diamond-section mane strands hanging on the near side; long head (10 sides, flat forehead/face plane) tilted
58 deg down, flat muzzle front with 2 dark nostrils, separate chin/jaw block; dark 6-gon eye discs #2A1D17, 5 mm proud;
upright cupped ears (brown outside, dark inner) between them a 3-strand black forelock; 8-sided legs: brown forearm/thigh,
black sock from 0.62 m, knee/hock joint band (proud, dark grey), cannon, fetlock band (proud, dark grey), pastern, dark
flared hoof; tail: black dock + broad mass + 3 pointed strands of different length.

## Material class
Flat palette `T_FarmAnimals_Horse_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Horse`. Cells: 0 bay brown #A05A33,
1 brown shade (spare), 2 mane black #2B2725, 3 mane black 2 #3A3532 (alternate strands), 4 inner ear #4E2C1C,
5 nostril #3A221A, 6 eye #2A1D17, 7 hoof #3A2E28, 8 sock #2F2B29, 9 joint band #4A4440, 10-15 series spares.
Variants (dapple grey, black, white, chestnut) swap cells 0-3 and 8-9.

## Parts (skeleton Q-H names; object `FMS_Horse_<Part>`, direct children of empty `FMS_Horse`, pivot = joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nostrils, Forelock, Mane1 (poll) / Mane2 / Mane3
(withers), Front/Hind Upper/Lower/Foot .L/.R (Foot = pastern + hoof, pivot at the fetlock), Tail1 (dock) / Tail2 (mass) /
Tail3 (3 strands). Joints overlap via tuck rings (child end = parent end ring + 1 mm, inner 0.86 ring 5-8% deep inside).

## NOT modelled
saddle/bridle/halter, teeth/tongue, eyelids, nostril holes, individual hairs, chestnuts/ergots, shoes, ground.

## Rounds
1. Body/neck/legs 1.2-1.4x too thin (spindly); mane = small spikes; head small/narrow; mirror 0.024 (Tail2 ridge phase);
   -> body +12% wide, neck deeper, LEG_K 1.18, head group x1.12, strands 0.17-0.18 wide, phase fix (mirror 0.004).
2. Strands followed the neck circumference toward the throat (comb look, crest ridge read as a bar); belly shallow;
   neck base poked out under the chest; stacked step rings on the legs; 4 coplanar pairs at the mane chunk joints
   -> strands hang by gravity (world -Z) on neck+body surface, belly -4..7 cm, fuller chest, smooth knee/hock bulge
   + tapered fetlock band, ridge cross-section differs per chunk (coplanar 0).
3. Head a thin snout + jaw stuck out (open-mouth look); weak thigh/shoulder; rear strands sunk in the body
   -> deeper head rings, jaw recessed, thigh/forearm tops larger, shorter rear strands.
4. Mane a flat patch; ledge where forearm/thigh tops leave the belly; head still narrow -> strands 0.20-0.22 wide,
   tips lifted 13 cm, leg tops narrower at the belly, head rings +10% wide.
5. Mane band narrower than the reference -> middle strands 0.50-0.55 long. Preview camera moved toward the side so the
   tail reads (the reference shows it as a main silhouette feature).
Delivered after round 5 with notes: slim build, faint forearm ledge, one-sided mane, plan hoof colour, mirror 0.0043.

## Polish pass (lead: reference wins over the plan wording; checked at the ref angle, side-on, from behind, far side)
6. Stockier farm horse: belly 0.79 (was 0.86), withers ring 1.65, barrel half width 0.39 (was 0.355), rump rings
   +10% wide, neck rings +12-16%, legs LEG_K 1.26 (was 1.18), hooves kept at 0.22 m wide. Forearm/thigh tops taper
   inward into the body (top ring 0.70 x offset, smaller radius - Cat approach), no cap rim outside the belly.
   Mane: the 7 strands are mirrored to the far side (14 strands, Mane1-3 still separate), roots 2.5 cm off the crest;
   forelock 3 strands bigger (centre 0.36 m) and built mirrored; ears +12%; tail dock/mass/strands +15-25% volume.
   Palette: hoof #3C3B3E (reference neutral dark grey), sock #2D2C2E, band #4A494B, mane #2A2929/#373636.
   Mirror now 0.000000 over ALL parts (asymmetric ray-cast roots replaced by mirrored copies).
7. Side/far views: hind stifle ring jutted forward under the flank -> thigh rings narrower front-back (sy 1.15).
Remaining: head modelled straight (reference turned toward the camera - rig rest pose); hind stifle shows as an
anatomical crease where the gaskin leaves the flank (no shelf).

## Rework round 2 (independent review 3/5)
- Socks: each Lower = ONE 8-sided black prism knee/hock -> hoof (top apothem 1.15x bottom: front 0.109/0.095,
  hind 0.113/0.098), no rings/bands; Foot = hoof cap 1.15x -> 1.24x the prism bottom, 0.155 m high, + hidden stem
  (pivot at the fetlock 0.27). Upper = all brown, last two rings a 4 mm parallel offset of the prism (no cuff).
  Knee 0.50 (cannon leans 1.5 cm forward), hock 0.56 behind the slanted gaskin (cannon slopes 5 cm forward).
- Head: cheeks +20% (half width 0.168 -> 0.20), muzzle -10% (HEAD_LEN 0.68 -> 0.615), eye 6-gon apothem 0.036 x 1.18
  = 0.085 m across (0.11-0.12 x head length 0.73), on the surface normal, 8 mm proud at the centre.
- Body: girth bottom 0.79 -> 0.71 (+10% depth, 0.94 m), barrel 0.85 deep at mid, half width 0.41; neck base +12%.
  NOT the full +15%: legs would drop to ~48% of the withers height while the reference measures ~57% (ref wins).
- Mane strand tips lifted 9 cm (was 13): the two-sided mane flared like wings from the front.

## Result
tris 2424 (target 2600, -7%). Size 0.929 x 2.964 x 2.396 m; nose -> tail root 2.384 m; body top 1.641 m.
Joint overlaps: sock prism 0.06 m inside the upper leg (15-17% of the prism), hoof stem 0.115 m inside the prism.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, gap 0.0, mirror 0.000000 (all parts), min z 0.
FBX re-import: 31 meshes + root, 2424 tris, dims 0.929 x 2.964 x 2.396, texture found.

## Result (polish pass, superseded)
tris 3000 (target 2600, +15%; +7.0% over the first delivery 2804). Size 0.971 x 3.005 x 2.394 m (W x L incl. tail
x H to ear tips); nose -> tail root 2.424 m; body top at the withers 1.642 m.
Pivot: root at the ground under the volume centroid (geometry shifted +0.164 m in Y; x = 0 symmetry plane); part pivots
on the joints, scheme unchanged. Joint overlaps: body tucks 0.05 m (8-12%), neck 0.035 (12%), mane chunks 0.035,
tail 0.04; leg upper->lower 0.04-0.05 m, lower->foot 0.04 m (6-15% of the shorter part).
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, worst contact gap 0.0, mirror 0.000000 (all parts), min z 0.
FBX re-import: 31 meshes + root, 3000 tris, dims 0.971 x 3.005 x 2.394, texture found in FMS_Horse.fbm.

## Deviations
- tris 3000 vs 2600 (+15%): separate overlapping parts (tuck rings, caps), knee/fetlock bands, two-sided mane (392).
- head group scaled 1.18 about the poll (head 0.80 m long) - reference head is big.
- body top 1.642 m at the withers ring (target ~1.65); the neck crest + mane ridge make the visual withers ~1.73.

## Rig + animation (rig_horse.py, horse_clips.py; mesh unchanged)
- Skeleton Q-H, 29 bones: Q without Horn.L/R + Forelock (Head) + Mane1 (Neck2) - Mane2 (Mane1), Mane3 (Neck1); each mane
  bone is parented to the neck bone it sits on. Bone heads on the part pivots / joints (body bones on the part boundaries).
- 31 parts joined into ONE skinned mesh FMS_Horse (2424 tris, 1312 verts), weight 1.0 per part, 1 influence per vertex
  (Eye.L/R + Nostrils -> Head). Bend test: legs, tail, ears, mane, forelock, neck-down/yaw hold; the extreme head-UP pose
  (Neck1 -40, Neck2 -35, Head -45) opens seams between the rigid neck/head parts (not used by any clip).
- Horse-local leg IK (rest offsets: hind cannon 29.7 deg off the gaskin) and pastern tilt in stance (front legs straight
  at rest); breathing on the back line only (Spine1/Spine2 counter-rotate, shoulder height constant).
- Clips 30 fps, in place: Horse_Idle 4.0 s (120 f), Horse_Walk 1.1 s (33 f, LH-LF-RH-RF, 0.95 m/s, stance travel 0.627 m,
  stride 1.045 m), Horse_Graze 5.0 s (150 f, muzzle 0.027 m, FrontL 0.20 m forward, 10 chews, 2 head lifts).
  Metrics: loop closure 0.000 deg all; lowest vertex Idle -0.002 / Walk -0.0048 / Graze 0.000 m; Walk slip 0.89 %;
  no joint-limit violations (horse-local HindLower x -140..30: hock rests at 30 deg flexion).
- FBX: skinned mesh + Rig + 3 takes (NLA, bake_space_transform, all bones), Footstep events in FMS_Horse.events.json.
