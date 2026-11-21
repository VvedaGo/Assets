# LIV-09 Bull - spec (Farm Animals extension, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-09.png` (1536x1024): front-left three-quarter (camera ~28 deg off the
nose axis toward the bull's left, ~13 deg above), head facing the camera, body receding to the right.
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-09: brown, mighty withers, long horns forward, nose ring, 2.5 x 1.6 m,
2400 tris (lead: within +15% = 2760), skeleton Q.
Anchors followed: Goat (`../Goat/build_goat.py`: Model/loft/tuck, objects() per part with joint pivots, coplanar_all,
check sheet, EEVEE look sheet), Cow (horn = sunk tapered tube with a contrasting tip, ear leaf with an inner face,
hoof collar, knee band), Horse (stocky leg rings, hind leg slanting back to the hock, leg tops tapered into the body).
Preview: `_common/animal_render.preview` (read-only), same template as Cow/Horse/Goat.

## Measured from the reference (near front hoof y~1010, hump top y~115 -> 1.6 m => ~0.0018 m/px at the shoulder;
## the head is ~1 m nearer the camera: ~0.0016 m/px there)
| Feature | px | model (m) |
|---|---|---|
| hump (withers) top | 885 above ground | 1.63 |
| belly under the near front leg | ~290 above ground | 0.52 (short legs: 32% of height) |
| brisket / dewlap | lowest body point at the chest | 0.50 |
| rump top | perspective-reduced | 1.46 (top line falls 0.17 m from the hump) |
| poll top / horn tips | y 25 / y 30-40 (head nearer) | 1.66 / 1.95 |
| eyes / nose / ring bottom | y 230 / 370 / 450 | 1.50 / 1.07 / 0.93 |
| head width at the eyes | 270 | 0.50 (broad flat forehead) |
| horn span tip to tip | 765 | 1.25; base diameter 0.12, length ~0.55 per horn |
| eye diameter | ~40 | 0.07 (8-gon, 5 mm proud) |
| nose ring outer / tube | 105 / 18 | 0.17 / 0.032 |
| forearm / cannon / hoof width (near front leg) | 120 / 95 / 150 | 0.32 / 0.22 / 0.26 |
| hoof height | 85 | 0.13 |
| knee band | y 780-800 | z 0.39-0.46 |
| tail tuft | 150 long, 70 wide, bottom y 710 | 0.30 x 0.14, bottom 0.46 |
| body width (not measurable in the 3/4 view) | - | 0.98 at the shoulder (cow 0.81) |

## Features (must read at 128 px)
Massive faceted barrel (16 sides x 14 rings) with a high shoulder hump falling to a level back; very thick short neck
merging into the hump and a deep dewlap/chest; big broad head (12-sided loft, curved axis: forehead 64 deg down, muzzle
40 deg) with a flat forehead, lighter muzzle with two dark nostrils, grey chunky nose ring hanging from the septum;
dark 8-gon disc eyes #2A1D17 on the forehead corners; long horns out sideways then up and forward, tan with a cream tip
third; horizontal leaf ears below the horns (brown outside/rim, light pinkish inner face); short thick 8-sided legs with
a darker proud knee/hock band and dark flared hooves; thin tail arcing from the tail head with a dark spindle tuft.

## Material class
Flat palette `T_FarmAnimals_Bull_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Bull`. Cells: 0 brown #98563A,
1 brown dark (joint band) #6E3B26, 2 muzzle #B87A5E, 3 nostril #3A221A, 4 eye #2A1D17, 5 hoof #3A2E28, 6 horn #D2A06F,
7 horn tip #F4E2C6, 8 ear inner #D9A288, 9 ring metal #9AA0A6, 10 tuft #4A2C20, 11 ring dark (spare), 12-15 series spares.

## Parts (object `FMS_Bull_<Part>`, direct children of empty `FMS_Bull`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Horn.L/R, Eye.L/R, Nose (nostrils), NoseRing (bind to Head),
Front/Hind Upper/Lower/Foot .L/.R, Tail1-3. Joints overlap by tuck rings (body, neck, tail) or sunk ends (legs, ears,
horns, eyes, ring).

## NOT modelled
mouth line, teeth/tongue, eyelids, curly forehead hair, scrotum, dewlap folds, halter/rope, individual hairs, ground;
the reference head turn toward the camera (rest pose straight for the rig).

## Rounds
1. (Workbench, all angles) body a long uniform sausage with a regular quad grid and weak hump; head small and snouty,
   below the hump line; horns a steep V; Tail2/Tail3 coplanar (duplicated ring). -> body shortened 0.1 m, hump 1.67,
   odd body/neck rings turned half a step (triangle lattice), head +14% wide and raised (P0 z 1.64), horns out sideways
   then up, tail ring fix (coplanar 0).
2. (EEVEE ref/preview/side/back/front/top) legs slimmer than the reference, dark knee bands read as cuffs, muzzle a pink
   pig snout, horn base thin, nose->rump 2.36. -> legs x1.16 below 0.75 m, band colour softer, muzzle colour darker and
   wider, horns base 0.076, hump 1.70 / back 1.40-1.42, global length x1.05 (nose->rump 2.48).
3. Legs still slim, tail hidden behind the rump at the reference angle, lower legs wider than the hoof collar.
   -> LK 1.25, lower legs tapered into the hoof, tail set 0.12 m further back (reads at the reference and preview angle).
4. Waist behind the muzzle (snout bulb) and head relatively smaller than the reference. -> muzzle waist removed, head
   group x1.08 about the head/neck joint. Accepted (128 px: horns, ring, hump, hooves, tail tuft read).
Remaining (nitpicks / pose): reference head turned to the camera with the face nearly vertical (ours straight rest
pose, muzzle forward ~42 deg); reference hump bulges a little more over the shoulder; reference horns slightly more
horizontal; reference has no darker knee band (kept per the pack checklist, soft #85492F).

## Result
tris 2440 (target 2400, +1.7%). Per part: Pelvis 220, Spine1 156, Spine2 188, Neck1 68, Neck2 92, Head 188, Jaw 60,
Ear 56 x2, Horn 80 x2, Eye 28 x2, Nose 40, NoseRing 96, Front Upper/Lower/Foot 108/44/60 x2, Hind 108/44/60 x2,
Tail1 32, Tail2 44, Tail3 80.
Size: width 1.308 (horn span) x length 2.892 (nose -> tail tuft) x height 1.969 (horn tips); nose -> rump 2.514,
withers 1.690, belly 0.490, poll 1.757, ring bottom 0.961, tuft bottom 0.460. Pivot: root on the ground under the volume
centroid (geometry shifted +0.220 m in Y), x = 0 symmetry plane; part pivots on the joints.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000 (all parts), worst contact gap 0.0, min z 0.
FBX re-import: 30 meshes + root empty, 2440 tris, dims 1.308 x 2.892 x 1.969, texture found in FMS_Bull.fbm (256x256).

## Deviations
- withers 1.69 (catalogue 1.6): hump top ring; the back behind the hump is 1.40-1.55.
- head group x1.08 and global length x1.05 (style: big head, nose -> rump 2.51 m).
- head straight (reference turns it toward the camera). No LOD1 (mesh-only round, like the other animals).

## Rework 1 (coordinator, 7 items) - supersedes Result/Deviations above
Changes: body 12 sides x 9 rings on the muscle lines (chest, brisket, hump, behind shoulder, barrel x2, hip, rump, end),
no half-step lattice; neck 10 sides; head = 10-point polygon section (flat forehead, bevelled corners, brow ring at
s 0.115); 4 brown shades per facet (quad) from its normal: top #8E5638, flank #7E4A31, rear/low #6C3D27, belly #56301F;
muzzle #94593D, nose pad #A87253; horns one cream #F0C99A, sideways, base apothem 0.08, tip 3 mm; ears 0.276 m beyond the
head, tan inner #C99474; eyes 8-gon #2E1E17 apothem 0.046 on the forehead bevel under the brow; legs: belly 0.585
(0.34 of withers), knee/hock bulge 6 mm in the leg colour, hooves #4A3228 flared; tail 6-sided, 0.12 m behind the rump,
tuft #3F2519 down to 0.33 m (below the hocks), pointed.
Result: tris 2032 (target 2400, cap 2800). Pelvis 92, Spine1 92, Spine2 116, Neck1 56, Neck2 76, Head 136, Jaw 60,
Ear 56 x2, Horn 80 x2, Eye 28 x2, Nose 40, NoseRing 96, Upper/Lower/Foot 92/44/60 x4, Tail1 32, Tail2 44, Tail3 80.
Size 1.625 (horn span) x 2.662 (nose -> tail) x 1.907 (horn tips); nose -> rump 2.487, withers 1.730, poll 1.717,
head width 0.658, horn span / head width 2.47. Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000,
worst gap 0, min z 0. FBX re-import: 30 meshes + root, 2032 tris, dims 1.625 x 2.662 x 1.907, texture found.
Remaining: tail hidden behind the rump at the preview 3/4 angle (visible from the side and back; the reference shows
it through its own perspective); head straight (reference turned to the camera); withers 1.73 vs catalogue 1.6.

## Rework 2 (independent review 2/5, 5 items) - supersedes Rework 1 numbers
1. Torso wedge: rings with per-ring top power (1.9 at the hump = rounded ridge), withers 1.79, hip 1.48 (ratio 1.21),
   width 0.52 shoulder -> 0.40 hip -> 0.35 rump, brisket 0.60, belly rising to 0.74 at the flank; neck lowered 4-6 cm so
   the hump stands above the crest (poll 1.673). "Chest bottom 0.4x total height" read as chest depth ~0.66 of withers
   (brisket 0.60 = 0.34 of withers), because a literal 0.4 x 1.9 m = 0.76 m would make the chest shallower, not deeper.
2. Legs: one tapered 8-gon prism each (radius 0.165 -> 0.143 front, 0.170 -> 0.147 hind = 1.15x), Lower tucked inside
   Upper (shared ring, no band), hind hock angle 7 cm; hoof cap #4A3228 0.168 -> 0.152 apothem, flared.
3. Tail: root on the rump top, hangs 25 deg off vertical away from the rump, strand 0.066-0.072 m, diamond tuft 0.144 m
   (2x), tuft bottom 0.517; visible in the 3/4 preview.
4. Ears: horizontal flaps (width up-forward, inner face forward-down), shaded body brown, tan inner strip, 0.298 m beyond
   the head, under the horns.
5. Horns: 8 rings, sideways 0.35 m (~0.5x head width before the 1.15 head scale), then up over the last third; cream
   #F0C99A, root apothem 0.082; span 1.663 (2.37x head width 0.700).
Result: tris 1864. Pelvis 92, Spine1 92, Spine2 116, Neck1 56, Neck2 76, Head 136, Jaw 60, Ear 56 x2, Horn 92 x2,
Eye 28 x2, Nose 40, NoseRing 96, Upper/Lower/Foot 44/44/60 x4, Tail1 32, Tail2 44, Tail3 80.
Size 1.663 x 2.994 (nose -> tail tuft) x 1.915; nose -> rump 2.505. Checks: non-manifold 0, loose 0, degenerate 0,
coplanar 0, mirror 0.000000, worst gap 0, min z 0. FBX re-import: 30 meshes + root, 1864 tris, dims match, texture found.

## Rework 3 (second review 3/5, 5 items) - supersedes Rework 2 numbers
1. Withers 1.90 (was 1.79), hip 1.40 (was 1.48), rump 1.37: shoulder/hip 1.36 (was 1.21); hump ring top power 1.8.
2. Brisket 0.46 (was 0.60): chest depth 1.44 m (1.21x of 1.19); width shoulder 0.56 / hip 0.42 = 1.33x.
3. Head group x1.38 (was 1.15, = 1.2x), P0 raised 0.12 m, head tilt 58 -> 30 deg (muzzle level); poll 1.832, level with
   the hump front ring (1.78); head width 0.840.
4. Horns rebuilt: 8 rings, horizontal out 0.40 (pre-scale; ~0.9x head width per side incl. the up-turn), last third up and
   slightly forward; cream, root apothem 0.086; span 2.049 = 2.44x head width.
5. Legs x1.3: front 0.218 -> 0.188, hind 0.212 -> 0.184 (apothem), still one tapered prism; legs set wider (x 0.30 /
   0.27) so they do not touch; hoof caps 0.222 / 0.218.
Tail: arcs back to y +0.22 behind the rump, hangs 30 deg off vertical, tuft bottom 0.53; preview camera (0.92, -0.88, 0.20)
(45 deg three-quarter) so horns spread and the tail with tuft clears the hind quarters. Ears scaled 0.84 to stay ~0.29 m.
Result: tris 1864 (parts unchanged). Size 2.049 x 3.134 x 2.063; nose -> rump 2.546. Checks: non-manifold 0, loose 0,
degenerate 0, coplanar 0, mirror 0.000000, worst gap 0, min z 0. FBX re-import: 30 meshes + root, 1864 tris, dims
2.049 x 3.134 x 2.063, texture found.
Deviation: withers 1.90 m vs catalogue 1.6 (review asked for a much higher hump); total height 2.06 incl. horns.

## Rig + clips (rig_bull.py + bull_clips.py; copy of Calf/rig_calf.py, mesh unchanged)
- Skeleton Q, 27 bones (Cow names incl. Horn.L/R), armature 'Rig'; 30 parts joined into ONE skinned mesh FMS_Bull (992 verts,
  1864 tris), rigid 1.0 per part (Eye/Nose/NoseRing -> Head) + Calf 2-bone blends (body across Spine2|Spine1|Pelvis +-8 cm,
  Neck1 root -> Spine2, Neck2 -> Head, knee line 50/50, Lower bottom ring -> Foot); max 2 influences.
- Hind legs rest with a 14.5 deg hock (not collinear): Horse rest-offset leg IK copied (leg_ik_h), stance/swing reach limited
  to the REST hip->fetlock distance; bull-local limit HindLower x -170..15 (= straight cannon). Foot levelling step cancels
  the sideways tilt of the 0.44 m wide hooves (body roll / abduction). Breathing on the back line only (Horse breathe_h).
- Clips 30 fps, in place: Bull_Idle 4.0 s / 120 f (2 breaths, head sway + snort toss, ear flicks, tail swish);
  Bull_Walk 1.3 s / 39 f (heavy four-beat LH-LF-RH-RF, 0.78 m/s, step 0.67 m, lift 0.09, hoof flick 9/7 deg, roll 2.6 deg);
  Bull_Paw_Ground 3.0 s / 90 f (weight back/right + head down with horns forward, FrontL scrapes twice: lift + reach 0.14 m
  forward, drag 0.24 m back on the ground, return; other 3 hooves planted, tail swish).
- Metrics: loop closure 0.000 deg all; lowest vertex Idle 0.000 / Walk 0.000 / Paw -0.004 m; Walk slip 1.64 % of step
  (stance hoof max 0.010 m); planted hoof drift Idle 2.5 mm / Paw 0.0 mm; joint-limit violations 0.
- Bend test: legs, neck down, yaw, ears/tail, spine: closed; the extreme head-UP pose (Neck1 -35, Neck2 -30, Head -40) opens
  the Neck2/Head seam (no clip uses it; clips stay within Neck1 +-10, Head +-8).
- FBX re-import: 27 bones, 1864 tris, takes 120/39/90 f, vertex error 0.0 m, texture found. Events FMS_Bull.events.json
  (Walk Footstep x4, Paw x2, Snort). GIFs Bull_{Idle,Walk,Paw_Ground}.gif.
