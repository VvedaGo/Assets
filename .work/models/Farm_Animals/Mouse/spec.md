# SML-03 Mouse - spec (Farm Animals, skeleton Q-S, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/SML-03.png` (1536x1024). Mouse seen from the front-left, ~15-20 deg above:
near front foot -> near hind foot ~410 px, near -> far front foot ~190 px (body axis ~50 deg off the view axis, as the
Rabbit reference). The HEAD IS TURNED towards the camera (eyes symmetric about the nose) - pose, not geometry: modelled
straight (as Rabbit/Piglet).
Catalogue: FARM_ANIMALS_PACK.md 5.4 SML-03 - grey, round ears, thin tail, 0.10 x 0.05 m, 300 tris, Q-S.
Lead brief: ~0.10 m nose -> rump, tail +0.13 m, 0.06 m tall; target ~600 tris, up to ~900 if it improves the look.
Anchors followed: Rabbit (`../Rabbit/build_rabbit.py`: Model/loft, shared joint rings + hidden overlap, ray-cast eyes,
fur shade by normal, COM shift, objects/export/verify/preview), Cat (Catmull-Rom tail Tail1-3), Chick (tiny-model
preview framing). `_common` and `Tools/blender` imported read-only.
Script: `build_mouse.py -- SML-03 build|look|export`.

## Measured from the reference (ground y 880 px, back top y 330 px -> back 0.050 m => ~0.000091 m/px)
| Feature | px | model (m) |
|---|---|---|
| back top | 550 above ground | 0.050-0.052 |
| head top | 655 above ground | 0.060 (head 0.041 w x 0.039 h; nearest to the camera -> inflated in px) |
| ear tips | 810 above ground | ~0.073 |
| ear disc | 310 x 350 (head 410 x 375) | dia 0.031 (~80 % of the head height; brief says ~70 %, ref ~90 %) |
| ear rim thickness | ~30 | 0.004 total, rim band ~0.24 R, pink dish 0.76 R, 2.6 mm deep |
| eye dia / spacing | 40 / 216 (turned head) | 0.005 (8-gon, ~1.2x the ref for 128 px), x +-0.0105 |
| nose w x h | 90 x 75 | 0.0088 x 0.0064, hexagon, z 0.031 (lower third of the head) |
| body height | 390 (330 -> 720) | 0.040, belly 0.012-0.015 |
| leg width | ~60 | 0.0064 (6-gon apothem 0.0032, chunky) |
| foot | ~95 wide | 0.008 wide pad + 3 toes, 0.011 long |
| tail root dia | ~45 | 0.0052 -> point, ~0.13 visible, curving out (+X) and back down, tip turns up |

## Features (must read at 128 px)
Big round faceted head with a short pointed muzzle and a pink hexagon nose; two HUGE thick disc ears (grey rim + back,
deep pink dish facing forward/outward) on the top-back corners of the head; dark-brown 8-gon eye discs; plump oval body
(8-gon rings, flat top); four short chunky legs with pink feet (pad + 3 toe blocks); long pink tapering tail (Tail1-3).
Fur grey in 5 face-assigned shades by normal (top light, sides mid, front, rear, underside dark).

## Material class
Flat palette `T_FarmAnimals_Mouse_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Mouse`: 0 top #9D9696, 1 side #8F8888,
2 front #968E8D, 3 rear #868080, 4 under #787272, 5 ear pink walls #D48B87, 6 nose #E2A19F, 7 eye #3A2219,
8 ear dish floor #DA9692, 9 feet #E0A09E, 10 tail #D99895, 11-15 series spares.

## Parts (object `FMS_Mouse_<Part>`, direct children of empty `FMS_Mouse`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, FrontUpper/Lower/Foot.L/R,
HindUpper/Lower/Foot.L/R, Tail1, Tail2, Tail3. Neck1/Neck2/Jaw and the Upper legs are hidden connectors (Q-S short neck).
Body joints share the joint ring exactly (no seam line) and each part closes with a hidden cone reaching ~8 mm into the
neighbour (overlap for a later bend); tail segments the same.

## NOT modelled
whiskers, mouth, teeth, eyelids/pupils/highlights, claws, fur strands, ground, head turn (pose).

## Rounds (Workbench sheet, then EEVEE sheet: ref angle, preview angle, side, front, back, top + 128 px thumbnail)
1. 992 tris (over 900); muzzle long and pointed (rat-like side view), head small vs body; legs spindly (6.6 mm);
   shared coplanar check flagged 81 pairs = false positives at mouse scale (toe soles sharing the ground plane 2 mm apart)
   -> own `coplanar_true` (plane < 0.01 mm AND real 2D overlap, SAT) + the shared check on a x10 copy; head x1.15
   (0.046 w), muzzle 2.5 mm shorter and fuller, body shorter/plumper; one-band foot pad, hidden connectors 3-gon (896 tris).
2. Body top low/flat, ears smaller than the reference, Jaw fully hidden -> false gap. -> body top +3 mm, exponent 2.5,
   ear R 0.019 (dia 0.038 = 84 % of the head height), rim 5 mm thick, jaw bottom 0.5 mm under the chin.
3. Legs still read thin, tail root thin vs the reference -> lower legs apothem 6.0/4.5 mm (12 mm / 9 mm wide), feet
   11 mm wide, toes 3.3 mm, tail root radius 3.4 mm tapering to a point.
Remaining (nitpicks): head straight (reference turns it to the camera); tail leaves the rump a little higher and straighter
than the reference's droop; top view shows the ears as thin edges (discs, by design).

## Polish round 2 (coordinator review 4/5)
P1. Legs long/thin -> body, neck, head group and hidden upper legs dropped 2.2 mm (visible leg ~9.5 -> ~7.5 mm, -21 %),
    lower legs apothem 6.0/4.5 -> 6.9/5.2 mm (+15 %), flats facing +-X; foot pad 11 -> 12.8 mm wide, toes 3.3 -> 3.8 mm
    wide, 2.6 mm high, 4.8 mm long. Pads still 0.4 mm above the ground, toes on z = 0.
P2. Tail rose (ran straight back, read as rising in 3/4) -> leaves the rump low (z 0.018 at exit), drops to 3-2.2 mm
    centre height by y 0.08, then a gentle S along the ground towards +X (x up to 0.054) and back towards +Y; min z 0.8 mm.
    Tail1/Tail2 got a middle ring each, Tail3 ends in one apex (+10 tris).

## Result
tris 906 (target ~600, limit ~900, +0.7 %): Head 116, Ear 76 x2, Pelvis 62, Foot 56 x4 (pad 20 + 3 toes x12),
Spine2 46, Spine1 32, Nose 32, Tail1 28, Tail2 30, Tail3 20, Lower legs 20 x4, Eye 14 x2, Upper legs 8 x4,
Neck1/Neck2/Jaw 8.
Size: width 0.094 (tail sweep; ears 0.080, body 0.047, head 0.046) x length 0.214 (nose -> tail tip) x height 0.077
(ear tips); nose -> rump 0.100, back 0.0515, head top 0.062, belly 0.0106, tail curve 0.146.
Pivot: root at the ground under the volume centroid (geometry shifted +0.0025 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000 (tail excluded: deliberate S-curve to +X; 0.10 with it),
worst contact gap 0, coplanar_true 0, coplanar x10 0, min z 0 (toes on z = 0; pads 0.4 mm above).
FBX re-import: 27 meshes + root, 906 tris, dims 0.094 x 0.214 x 0.077, texture found in FMS_Mouse.fbm (256x256).

## Deviations
- Head straight (reference pose turns it to the camera).
- Ears dia 0.038 = 84 % of the head height (brief ~70 %, reference ~90 %).
- Eyes 5.6 mm (~1.2x the reference) for 128 px readability.
- Height 0.077 to the ear tips (head top 0.062, back 0.0515); catalogue 0.10 x 0.05.
- tris 906 vs catalogue 300 / brief target ~600 (brief allows up to ~900).
- Foot pads float 0.4 mm above the ground (only the toes touch z = 0) to avoid coplanar soles.
- Tail asymmetric (S-curve to +X), excluded from the mirror check.

## Rig + clips (skeleton Q-S, rig_mouse.py / mouse_clips.py; copy of the Rabbit rig, mesh unchanged)
Final export = `rig_mouse.py -- SML-03 export`. 26 bones: Q without Horn.L/R, Tail1-3 kept, + Nose under Head; parts rigid
(weight 1.0, Eye.L/R -> Head). Feet flat by world orientation (foot_flat). TailClear: each tail bone lifts just enough that its
own distal vertices + the child's hidden apex cone stay >= 0.2 mm (the tail lies on the ground in the rest mesh).
Idle 3.0 s/90 f: 6 shallow breaths, 3 sniff bursts (head up/forward, nose 11 Hz, jaw quiver), ears swivel, tail S-sway; events Sniff x3.
Scurry 8 f (0.267 s): trot pairs, step 10 mm, root speed 0.075 m/s, legs near-straight (reach 1.0, rigid lower ring would
  sink otherwise), ears back, tail lifted 6 deg + sway; events Footstep x4.
Nibble 2.0 s/60 f: sits up (pelvis -42 deg, hunched spine), rump + tail root settled on the ground, head bowed, paws at
  the mouth by FK grid search (gap 1.6 mm), jaw gnaws 16x (8 Hz), tail laid along the ground; limits Pelvis x -50, HindUpper x
  125 (hidden thigh connector folds for the sit).
Metrics: loop closure 0.000 deg, lowest -0.3 / 0.0 / -0.2 mm (limit -0.5 mm = pack -1 cm scaled to 0.10 m), Scurry slip 0.01 %,
0 limit violations; FBX re-import 26 bones, 27 meshes, 906 tris, vertex error 0.0. GIFs: anim_gif.py --view 1.0 -1.15 0.24 --fill 0.74.
