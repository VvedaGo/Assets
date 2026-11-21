# LIV-04 Sheep - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-04.png` (1536x1024, front-left three-quarter, ~17 deg above; the head is
turned towards the camera - we model the rig rest pose with the head straight, see Deviations).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-04 - white, fluffy wool of 30-40 lobes, dark legs and face, ears sideways,
1.3 x 0.85 m, 1800 tris (lead: stay within +20%), skeleton Q.
Anchors followed: Cat (`../Cat/build_cat.py`: part objects named after skeleton Q, pivot = joint, tuck rings at body joints,
eye ray-cast, objects()/coplanar_all/check sheet, EEVEE preview via `_common/animal_render.preview`), Cow (palette,
superellipse head loft along a tilted head axis), Farm Processing house style (flat 4x4 palette, faceted, chunky).
Script: `build_sheep.py -- LIV-04 build|look|export`.

## Measured from the reference (ground ~960 px at mid body, back top 215 px -> 0.85 m, ~0.00114 m/px; head is nearer
the camera, so head sizes are inflated ~10% by perspective)
| Feature | px | model (m) |
|---|---|---|
| wool top (back) | 745 above ground | 0.86 |
| wool bottom (belly) | ~180 above ground | 0.28-0.30 |
| head tuft top | ~935 | ~1.02 |
| eyes height | ~715 | 0.83 |
| chin | ~500 | 0.57 |
| face width at the eyes | ~280 | 0.29 (head 120% style) |
| eye diameter | ~45 | 0.046 (8-gon, apothem 0.023) |
| ear length / width | ~190 / ~90 | 0.19 / 0.10, 0.04 thick |
| leg width (visible lower leg) | ~70 | 0.075-0.08 (6-gon) |
| hoof width / height | ~95 / ~60 | 0.11 / 0.075 |
| lobe diameter | 150-220 | lobe radius 0.12-0.15 |
| body (wool) length / depth | ~890 / 565 | 1.0 / 0.60, width 0.70 (not visible, chunky) |

## Features
Wool: 32 body/neck lobes + 8 head-cap lobes = 40 faceted puffs (antiprism domes: flat 6-/5-gon top facet, two triangle
bands, base sunk into a hidden core). Body lobes in 6 regular staggered rows over a superellipsoid core (sections
cos(theta)^0.6 -> full chest and rump), size jitter +-3%, tilt +-0.05, exact X mirror. Shades by face assignment: lobe
top + upper band = white #F8F5EF or cream #EBE1D2 (checker per lobe), lower band = shade #D9CBB7, core = #CBBCA6.
Head: faceted brown wedge (8-sided superellipse loft, axis 58 deg down, head group x1.12), full wool cap of 8 lobes
(wider than the face), dark 8-gon eye discs #2A1D17 6 mm proud on a lighter brow ring #946A5A, dark nose pad, chin block,
flat leaf ears sideways, 15 deg down (see rework 2).
Legs: 6-sided brown prisms tapering to the hoof (as the reference: no dark band), small knee lip where the lower leg
starts, dark flared hoof with a chamfered top.
Tail: stub (Tail1) + white puff (Tail2) above the rump. Skeleton Q has Tail1-3; the sheep has Tail1-2 only.

## Material class
Flat palette `T_FarmAnimals_Sheep_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Sheep`. Cells: 0 wool white, 1 wool cream,
2 wool shade, 3 wool core, 4 face brown, 5 face shade, 6 leg brown, 7 leg dark (spare), 8 eye #2A1D17, 9 hoof #3A2E28,
10 ear inner, 11 nose, 12 eye ring, 13-15 series spares. Black-sheep variant swaps cells 0-3.

## Parts (object `FMS_Sheep_<Part>`, direct children of empty `FMS_Sheep`, pivot = joint / bone head)
Pelvis, Spine1, Spine2 (hidden wool core), Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R,
Tail1, Tail2, Wool_Pelvis, Wool_Spine1, Wool_Spine2, Wool_Neck (-> bones Pelvis/Spine1/Spine2/Neck1), Wool_Head (head tuft
-> bone Head; extra group, same naming scheme). Joints overlap (tuck rings / sunk ends).

## NOT modelled
horns, mouth line, teeth/tongue, eyelids, individual curls/strands, ground, collar/bell, ear tags.

## Rounds
1. (Workbench) lobes read as flat hexagonal plates; head long and snout-like, pointing down; legs thin; neck core visible
   behind the head; 2208 tris. -> rounder lobes, head shorter and steeper (58 deg), legs +20%, 2 neck lobe rows (Wool_Neck).
2. (EEVEE) head too small and sunk in the wool; lumpy silhouette (balls sticking out); legs look long (no wool under the
   belly); 43 lobes. -> head group x1.25 + 4 cm forward, lobes sunk 6% into the core, core 2 cm lower, belly rows at
   155 deg, 40 lobes, inner ear less salmon.
3. Ears were stubby cones towards the camera -> broad flat leaves swept sideways/back; legs and hooves +6%.
Polish pass (coordinator, 7 items; multi-view EEVEE sheet: reference angle, preview, side, back, front):
4. Cap -> 8 smaller 5-gon lobes (wider than the face); body -> superellipsoid core, 6 regular rows, 32 lobes, less jitter;
   cream darker (#EBE1D2); eyes larger + lighter brow ring; head x1.12 (front view: face was too big for the wool);
   body 3 cm lower, core length tuned -> 1.33 x 0.854 m; ears +10% and swept back; legs plain taper (reference has no
   bands), knee 2-3 cm lower so it stays below the wool.
5. Cream patchy/beige, eye ring like goggles, cap of scattered balls -> cream #EBE1D2, ring 0.037, cap lobes +15%.
6. Tail hidden in the rump -> puff r 0.10 raised above the rump lobes.
7. (preview) core visible as a beige patch below the near ear -> neck lobe pair larger and lower, core tone lighter.
Remaining (judged as acceptable): the reference head is turned to the camera; ours is straight (rig rest pose), so from the
pack's 3/4 preview angle the near ear is seen at ~40 deg and looks shorter than in the reference.

Rework 2 (independent review 3/5; sheet: reference angle, preview, side, back, front, top, 128 px):
8. Ears -> two mirrored flat leaves in face brown, root sunk under the cap at the head corners, 15 deg down, 20 deg
   forward (so the far ear clears the head in the 3/4 view); visible part beyond the cap 0.45 x head length (0.15 m),
   width 0.10 m, thickness 0.03 m (0.18 x visible length, 29% of the width).
9. Eyes -> plain 8-gon discs #2A1D17, 0.045 m (0.13 x head width), 3 mm proud; brow rings removed (Eye = disc only).
10. Wool -> one colour #EEE9E2 on every puff + 2 shades by facet direction (#F4F1EC facing up, #E3DDD4 facing down);
    core the same shade; no grey-blue/beige cells (the bluish tint left in shadow comes from the pack preview sky light).
11. Legs -> Upper + Lower on one 6-sided cone (top radius 1.15 x bottom), lower tucked 0.5 mm inside the upper (no
    visible step), dark brown #553A32 with a darker hoof cap #3A2E28; body lowered 2 cm -> visible leg 0.21 m (-10%).
Preview camera: (0.85, -1, 0.2), slightly more frontal than the cat/cow template, like the LIV-04 reference.

## Deviations
- tris 2026 vs 1800 (+13%; -2.3% vs 2074): 40 closed lobes = 1154 tris.
- size: length 1.326 m incl. tail puff (catalogue 1.3), wool back top 0.834 m (catalogue 0.85, -2% after the leg
  shortening), 0.988 m to the head cap, width 0.707 m.
- skeleton Q tail: Tail1 + Tail2 only (no Tail3).
- extra wool group Wool_Head (8 cap lobes) -> bind to Head; Wool_Neck -> Neck1, Wool_Spine2/1 -> Spine2/1, Wool_Pelvis -> Pelvis.
- pivot: root on the ground under the volume centroid (geometry shifted +0.023 m in Y; overlapping parts counted twice, approx.).
- palette cells 7 (leg dark), 10 (ear inner), 12 (eye ring) are unused spares now.

## Rig / animation (rig_sheep.py + sheep_clips.py; mesh, part names, Wool_* groups and pivots unchanged)
- Skeleton Q-S: Cow Q names/hierarchy without Horn.L/R and Tail3 = 24 bones (Root, Pelvis, Spine1-2, Neck1-2, Head, Jaw,
  Ear.L/R, 12 leg bones, Tail1-2); bone heads = part pivots, tails = next joint (Head -> nose pad, Ear along the leaf).
  Registered at runtime as ar.SKELETONS['QS'] (shared animal_rig.py untouched); check_rig names/hierarchy OK, roll_bad [].
- Binding: every part object keeps its name and gets ONE vertex group (weight 1.0) + Armature modifier, parented to `Rig`:
  part -> same-named bone; Eye.L/R, Nose, Wool_Head -> Head; Wool_Neck -> Neck1; Wool_Spine2/1 -> Spine2/1; Wool_Pelvis -> Pelvis.
  The shared Skel/metrics run on a TMP joined copy (never exported).
- Bend test (extremes): legs +-60/45 deg, knee/hock 150 deg, neck down 115 deg total, neck yaw 110 deg, ears +-60, tail 70,
  body pitch 20 / roll 12: no holes. Head UP -100 deg total (neck -35/-30, head -35) opens a gap between head/cap and the
  neck wool (rigid groups) -> keep head-up under ~45 deg total in future clips.
- Clips: Sheep_Idle 3.0 s (90 frames): 2 breaths (Pelvis +-5 mm, Spine pitch), head drift, ear flicks L 0.15 / R 0.48 /
  L twitch 0.80, tail wiggle + burst at 0.62. Sheep_Walk 0.9 s (27 frames): lateral-sequence walk, duty 0.60, 0.33 m/s,
  step 0.178 m, lift 4.5 cm, head bob x2, Spine1/2 wool bounce with lag, body drop 0.9-2.0 cm, Footstep events in
  FMS_Sheep.events.json (frames 0/7/14/20). Short steps on purpose: the rest legs are fully extended, longer steps crouch.
- Metrics: closure 0.0 deg both; lowest vertex 0.0 / -1.1 mm; walk foot slip 1.19% of step; no joint-limit violations.
- FBX: 31 skinned parts + Rig (24 limb nodes), takes Sheep_Idle 90 f / Sheep_Walk 27 f; re-import 24 bones, 31 meshes,
  2026 tris, vertex error 0.0 m. Unity note: 31 SkinnedMeshRenderers per sheep (part names kept as asked) - merge into one
  skinned mesh at import if the draw-call budget needs it.
- Sheep_Graze 4.0 s (120 frames, loop): FrontL 5 cm forward, body -3 mm / 1 deg nose-down (legs stay straight), neck pitch
  90 deg (Neck1 54 / Neck2 36) + Neck1 reach 0.18 m (keyed location) + head -45 deg -> head axis 101.5 deg below the
  horizon, muzzle min z 0.022 m in front of the hooves (grid search, rounds: 1 head tucked under the chest + Z-bent legs ->
  head-axis limit 65-105 deg, no crouch; 2 muzzle only 0.097 -> search to the joint limits). Overlay: 5 bite tugs, 10
  chews (Jaw 9 deg), 1 s head lift at t 0.55, ear flicks 0.20 / 0.72, tail wiggle + burst 0.40, 2 breaths.
  Neck1 location is keyed in every take (0 in Idle/Walk) - without it the Graze reach leaked into Idle/Walk on re-import
  (0.18 m error); motion of Idle/Walk unchanged. Re-import error 0.0 m for all 3 takes.
