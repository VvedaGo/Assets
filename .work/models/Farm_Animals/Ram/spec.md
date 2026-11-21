# LIV-12 Ram - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-12.png` (1536x1024, front-left three-quarter, ~15 deg above, head turned
slightly to the camera - modelled straight for the rig rest pose).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-12 - white wool, curled horns, dense neck; 1.4 x 0.95 m, 2000 tris (lead: <= +15%).
Anchors followed: Sheep (`../Sheep/build_sheep.py`: superellipsoid core + lobe rows, part naming, tuck rings, head group
scale about the neck joint), Lamb (`../Lamb/build_lamb.py`: hidden-apex lobes 22 tris, cone eyes/nose, cream face/legs),
Bull/Goat (horn = tapered 6-sided tube from the poll, lighter tip). Shared `_common` and `Tools/blender` only imported.
Script: `build_ram.py -- LIV-12 build|look|export`.

## Measured from the reference (front hooves ~935 px, back top ~245 px -> 0.95 m, ~1.38 mm/px; head nearer the camera)
| Feature | px | model (m) |
|---|---|---|
| wool back top | 690 above ground | 0.950 |
| wool belly bottom | 175-230 above ground | 0.252 |
| horn top | ~915 (inflated) | 1.191 |
| eye height | ~700 | 0.963 |
| face width at the eyes | ~220 | 0.348 incl. cheeks (head group x1.16) |
| eye diameter | ~30 | 0.058 (8-gon apothem 0.025 x1.16) |
| horn tube at the root / tip | ~95 / ~40 | 0.139 / 0.046 diameter (apothem 0.060 / 0.020 x1.16) |
| horn curl outer diameter | ~270 | ~0.49 (2 x 0.21 + tube), span both horns 0.836 |
| leg width / hoof width / hoof height | ~80 / ~95 / ~45 | 0.12-0.14 / 0.14 / 0.07 |
| ear length | ~110 | 0.23 incl. root sunk in the head |
| lobe diameter | 150-200 | radius 0.16-0.17 (neck 0.145-0.15) |

## Features
Wool: 33 body/neck lobes (Wool_Spine2 9, Wool_Spine1 5, Wool_Pelvis 15, Wool_Neck 4 = throat bib, neck pair, nape) +
4 poll tuft lobes (Wool_Head) + tail puff. ONE wool colour #EEE9E2 + 2 warm-white shades by facet direction
(normal z > 0.55 -> #F3EFE9, z < -0.35 -> #E5DED2); no per-lobe checker, no grey/blue cell.
Head: broad 8-sided loft, 55 deg down, Roman (convex) nose profile, cream #F0DCC3 with a darker throat, dark inverted-
triangle nose, chin block, 8-gon eye discs #2A1D17 6 mm proud, ears tucked under the horn roots (root sunk 60 mm into the
head), sideways and down, cream with a subtle pink inner strip (#E3BBAA).
Horns: 6-sided open spiral tubes, 20 stations, 355 deg sweep from the top-back of the skull: back, down beside the cheek,
forward under the ear, tip curling up inside the curl at eye level; curl radius 0.183 -> 0.073 m (x1.16 head scale =
0.21 -> 0.085 m, ~0.5x -> 0.2x head height 0.41), plane normal (0.80,-0.58,0.12) (sideways, a little forward), outward
drift 0.20*t^1.5 so the inner turn lies outside the outer one (never a closed ring); tube apothem 0.060 -> 0.020
(x1.16: root 0.070 = 0.2x head width); root sunk 45 mm into the skull; ridge rings = every other station x0.92 and
alternating tan bands; light tip.
Legs: one straight cream 6-gon taper per leg (radius 0.055 at the hoof -> 1.15x at 0.30 m), Upper/Lower split at the knee
(Lower continues the same taper 0.5% thinner, top tucked inside Upper: no band, no step), dark hoof cap #3A2E28. Tail: stub + white puff above the rump.

## Material class
Flat palette `T_FarmAnimals_Ram_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Ram`. Cells: 0 wool white, 1 wool cream,
2 wool shade, 3 core, 4 face, 5 face shade, 6 leg, 7 spare, 8 eye, 9 hoof, 10 ear inner, 11 nose, 12 horn,
13 horn ridge, 14 horn tip, 15 spare.

## Parts (object `FMS_Ram_<Part>`, direct children of empty `FMS_Ram`, pivot = joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Horn.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R,
Tail1, Tail2, Wool_Pelvis/Spine1/Spine2/Neck/Head (-> Pelvis/Spine1/Spine2/Neck1/Head). Joints overlap (tuck rings, sunk ends).

## NOT modelled
mouth line, teeth, eyelids, individual curls, ground, collar/bell, Tail3, eye ring (the face is light, see Deviations).

## Rounds
1. (Workbench sheet, 8 views) head small and low in the wool; legs thin; horns slightly thin, curl not above the poll.
   -> head group x1.12 + 3 cm up, legs/hooves +12%, core 1.5 cm lower (belly 0.25), horn tube +3%.
2. (EEVEE ref/side/front/back/top/preview) near ear lost inside the horn curl; horn curl top too low vs the cap.
   -> head x1.16, curl centre further out/down (bigger curl), horn +6%, longer ears, knee lip colour softer.
3. ears still small in 3/4 -> root forward, longer leaf, pink inner on 3 faces. 128 px thumb: reads as a ram.
Rework round 2 (independent review 2/5: near horn a closed donut around the ear, ears detached blocks, wool grey/
patchy, legs banded):
4. horns rebuilt as an open spiral (sagittal-ish plane, outward drift, 0.4 radius ratio); ears sunk under the horn roots,
   subtle pink; wool one colour + 2 facet shades; legs single taper, no lip/band. Views: ref, side, front, back, top,
   preview, 128 px.
5. 3/4 view: inner curl hidden behind the ear, horn looked like a C -> plane turned to (0.80,-0.58), drift 0.20*t^1.5,
   curl +9%, ears shorter (0.20) and pointing more down. Spiral readable from the reference angle, side and front.
Remaining (nitpicks): horns slightly thinner and the curl smaller than the reference drawing (spec ratios 0.5x/0.2x head
height followed); from the front the horn tips point outward; the preview sky light cools the wool shadow side (shared
render template, palette is warm); reference lobes slightly smaller/more.

## Deviations
- Face and legs CREAM (reference) instead of "dark brown face and legs" in the lead brief: the reference wins; therefore no
  lighter eye ring (dark eyes read on the cream face). A dark variant = palette cells 4-7 swap only.
- tris 2120 vs 2000 (+6.0%).
- size: length 1.459 m (nose to tail puff; catalogue 1.4, +4%: bigger head), wool back 0.950 m, horn top 1.191 m,
  width 0.836 m across the horns (wool 0.779).
- skeleton Q tail: Tail1 + Tail2 only. Wool_Head is an extra group bound to Head.
- pivot: root on the ground under the volume centroid (geometry shifted +0.047 m in Y).

## Rig / animation (rig_ram.py + ram_clips.py, copied from ../Sheep; mesh, part names, Wool_* groups and pivots unchanged)
- Skeleton Q-R: Q without Tail3 = 26 bones (Horn.L/R kept: the mesh has Horn parts; Horn bones along the curl centroid,
  never keyed away from the head). Rigid binding: each part = one vertex group 1.0; Eye/Nose/Wool_Head -> Head, Wool_Neck ->
  Neck1, Wool_Spine2/1 -> Spine2/1, Wool_Pelvis -> Pelvis. check_rig names/hierarchy OK, roll_bad [].
- Bend test (legs +-45..60, knee/hock 150, neck down/up/yaw, ears, tail, body pitch 20/roll 12): no holes; head UP to the
  extreme lifts the face out of the neck wool (as the Sheep) -> clips keep head-up small.
- Ram_Idle 3.5 s / 105 f (2 breaths, head drift, ear flicks, tail wiggle). Ram_Walk 1.0 s / 30 f (lateral sequence, duty
  0.60, 0.36 m/s, step 0.216 m, lift 5 cm, head bob, wool lag; Footstep events). Ram_Graze 4.0 s / 120 f (FrontL 5 cm
  forward, neck pitch 90 + Neck1 reach 0.18 m keyed, head -40, muzzle 2.8 cm above the ground, horns >= 3 cm; bites,
  chews, 1 s head lift, ears, tail). Round 1: head pitch hit the -50 limit (+ overlay) -> search limited to >= -40.
- Metrics: closure 0.0 deg all; lowest vertex 0.0 / -0.8 mm / 0.0; walk slip 0.61 % of the step; limit violations 0.
- FBX: 33 skinned parts + Rig (26 bones), takes Ram_Idle 106 / Ram_Walk 31 / Ram_Graze 121 f (1-based on re-import),
  2120 tris, re-import vertex error 0.0 m, texture found. Events FMS_Ram.events.json. GIFs Previews/Anim/Ram_*.gif.
