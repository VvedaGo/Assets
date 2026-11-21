# LIV-06 Pig - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-06.png` (1536x1024). Pig seen from the front-left, camera ~28 deg off the
head-on axis, ~12 deg above, fairly strong perspective (head nearest, inflated ~1.25x against the rump).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-06 - pink, round body, snout disc, floppy ears, curly tail, dark hooves,
1.5 x 0.9 m, 1700 tris (lead: stay within +20%), skeleton Q.
Anchors followed: Calf (`../Calf/build_calf.py`: Model/loft/tuck/objects, part naming and pivots, COM shift, check sheet,
EEVEE preview via `_common/animal_render.preview`) and Cow (`../Cow/build_cow.py`: head frame, ray-cast eyes);
house style of Farm Processing (flat 4x4 palette, faceted, chunky). Shared `_common` modules are imported read-only.
Script: `build_pig.py -- LIV-06 build|look|export`.

## Measured from the reference (ground ~955 px under the rump, back top ~140 px -> 0.90 m => ~0.00114 m/px at the
rump; head is nearer, ~0.0009 m/px)
| Feature | px | model (m) |
|---|---|---|
| back top (rump slightly higher than shoulders) | 815 above ground | 0.91 |
| belly underside (mid) | ~250 | 0.29 |
| head height (poll -> jowl) | 555 | 0.45 (x0.8 perspective) |
| head width cheek-cheek | 600 | 0.50 (wider than tall, jowls widest low) |
| snout disc w x h | 290 x 260 | 0.26 x 0.23, 12-gon, protrudes ~0.08, chamfered rim |
| nostrils w x h, spacing | 55 x 70, 120 | 8-gon recess 0.046 x 0.058, centres +-0.055, 25 mm deep |
| eye diameter, spacing | 45-50, 285 | 0.052 (8-gon, 6 mm proud), x +-0.12 |
| ear length / width | ~320 / ~210 | 0.30 / 0.21, 0.07 thick at the root, folds forward ~125 deg |
| front leg width | ~120 | 0.12-0.14 (8-gon apothem 0.060-0.072) |
| hoof height / width | 75 / 135 | 0.075 / 0.14, flared at the bottom |
| tail curl diameter / tube | ~170 / ~32 | 0.19 / 0.046 -> 0.036 (6-gon), 1.15 turns |
| nose -> rump | - | 1.50 (catalogue) |

## Features (must read at 128 px)
Rounded faceted barrel (14 sides), back slightly darker, belly lighter; very big round head straight on the chest (no
visible neck), protruding salmon snout disc with 2 recessed dark nostrils; dark 8-gon eyes above the snout; large ears
rising from the top corners of the skull and flopping forward/outward over the cheeks, darker pink with a red-pink
inside; 4 short thick 8-gon legs with a knee ledge (darker band) and dark flared hooves; corkscrew tail in 3 chunky
segments curling up over the rump.

## Material class
Flat palette `T_FarmAnimals_Pig_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Pig`:
0 body pink #F2A6A1, 1 back #E59692, 2 belly #F8C0B9, 3 ear outside #DE8784, 4 ear inside #C8676A, 5 snout #EC8B88,
6 snout rim #D5767A, 7 nostril #8E3D42, 8 eye #2A1D17, 9 hoof #3A2E28, 10 knee band #E08E8B, 11-15 series spares.

## Parts (object `FMS_Pig_<Part>`, direct children of empty `FMS_Pig`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose (snout disc + nostril recesses),
FrontUpper/Lower/Foot.L/R, HindUpper/Lower/Foot.L/R, Tail1-3. Joints overlap via tuck rings (5-10%).

## NOT modelled
eyelids/pupils, teeth/tongue, hair/bristles, mud, ground, collar/ear tags, dewclaws, teats.

## Rounds
1. (Workbench sheet) ears small upright cones; body a long flat-ended sausage on thin legs; Jaw visible as a lip.
   -> new ear builder (spine blends up-out -> out-forward-down, common width axis, fold 0.02-0.15 m), body shortened
   with tapered ends, legs +15% thicker, head group x1.10 about the neck joint, Jaw sunk under the chin.
2. (EEVEE, reference angle) eyes on the side of a cone-shaped head; far ear seen edge-on as a spike; tail hidden behind
   the rump. -> broad flat face (front head rings wider), eye ray-cast from the front, ear flap normal turned
   forward, tail raised and its curl plane yawed 35 deg towards the front-left.
3. Eye ray was cast along +U from inside (eye landed on the cheek side, then read as a slit); ears covered the eyes;
   dark inner-ear colour on the root read as horns. -> ray along -U, disc axis = normal + U, ear roots moved back,
   flaps swung out and down to eye level, root bands outside colour; front legs forward under the chest, chest
   deeper, belly 0.265.
4. Ears too small vs the reference -> ear rings x1.22 (length 0.40 incl. fold, width 0.30).
5. Side view a straight-topped tube -> arched back (0.86 shoulders -> 0.91 hips) and rounder rump.
Remaining (nitpicks / for the owner): the reference turns the head towards the camera (modelled straight, rig rest
pose); reference ears hang a little further over the cheeks; the inner-ear root wedges show as small darker triangles
from behind; body facets are more regular (ring grid) than the reference's free triangles.

## Polish pass (coordinator, 7 items; judged on 6-view EEVEE sheets + close-ups of head, tail, leg joins)
1. Inner-ear wedges: EAR_IN only on flap bands, blended to #D47A7C (outside #E08985); root width axis laid along the
   skull surface, root rings narrowed and sunk 12 mm, flap lifted 45 mm off the skull (inner edge was buried 3-5 cm in
   the forehead and left a pointed apex). Clean from front, side and behind.
2. Ears: root higher on the skull, flap droops forward/down over the face corners (tips at eye level, ~0.46 m out).
3. Facets: symmetric deterministic jitter (body radial +-4.5 %, y +-22 mm; head +-3.5 %) and varied quad diagonals ->
   free triangles like the reference, no extra tris; belly tone kept off the rump end (was a light disc from behind).
4. Tail: reads from side, behind and rear 3/4; root sunk into the rump, tuck joints closed; tip rounded (2 taper rings).
5. Jaw: chin line under the snout reads as a lighter lip, no gap (checked in front-low and side close-ups).
6. Legs: knee band, flared dark hooves, upper legs enter the body without a step (side close-ups).
7. Side/behind checked; head 0.558 x 0.474, snout 0.29 x 0.25, belly 0.265 (ref ~0.285 measured at the rump).

## Rework round 2 (independent review 3/5: far ear a heart-shaped plate, near ear a sliver; noisy small body
triangles; stacked leg cylinders)
1. Ears rebuilt with the Piglet construction (`../Piglet/build_piglet.py` ear_rings: one triangular flap, fixed width
   axis, rises from the skull top corner leaning forward-out, folds 110 deg forward-down), pig scale: length 0.37 m
   along the spine (incl. 28 mm sunk root), width 0.26 m, thickness 0.065 m (0.12 x head width), tips just below eye
   level ~7 cm outside the skull, flap clear of the skull, mirror-symmetric, darker inner face. Larger than 0.45 x head
   width on purpose: at 0.45 x the flaps read as small tents against the reference ears.
2. Torso rebuilt: 10 sides x 8 rings (was 14 x 12), jitter 1.5 % (near-planar quads), no y jitter or random diagonals:
   Pelvis/Spine1/Spine2 76 tris each (436 -> 228, 52 %); ~30 facets per side view.
3. Legs: each one tapered 8-gon prism (bottom 0.080, top 0.092 = 1.15x), Upper/Lower split on the taper (Lower starts
   15 mm inside the Upper, 0.985x radius), one loop at the hoof line (dark hoof cap 0.075 m), no knee/fetlock bands.
Also: eyes as flush 12-gon discs (Piglet method; right eye mirrored from the left), body/head/tail lowered 0.035 m
(head bottom was 0.46 of the height vs 0.37 in the reference), preview camera at the reference 3/4 angle.

## Rework round 3 (ears only)
Ears replaced by `hanging_ear()` copied from `../Piglet/build_piglet.py` (sizes x head width, HEAD_HW 0.507 pre head
scale = 0.558 m in the model; widths/thicknesses/cup/sink unchanged from the Piglet). Pig-specific parameters, tuned
numerically (tip vs eye, flap clearance, eye gap) then by views:
target (0.19, 0.23, 0.17) root on the top-side skull corner near the brow; rise 0.20 (Piglet 0.14); face_yaw 75
(Piglet 48: at 48 the near ear read as a hood on top of the head from the 3/4 view); hang 50 deg, hang_fwd 1.0
(Piglet 72 / 0.25); length 0.30 (Piglet 0.24). Result: fold width 0.296 m (0.53 x head width), thickness 0.056 m
(0.10 x), tip 0.026 m above eye height and 0.05 m outside the eye, flap touching the skull (clearance 0.000), darker
inner face under the fold, exact mirror pair, both visible from 3/4, front, side, behind, above.
Remaining vs reference: the reference flaps are larger and hang lower/further out over the cheeks.

## Rework round 4 (ears only; second review: rounded cupped shells standing on top of the head)
Ears replaced by `flat_ear()` (own code): one flat triangular slab per ear, hexagonal section with flat outer/inner
faces (no cup), sunk root 30 mm; section 1 (40 % of the length) rises 60 deg forward + 25 deg out from vertical, one
fold line W = D1 x D2, section 2 drapes to a tip target level with the eyes just outside the cheek. Right ear = exact
X-mirror of the left (mirrored vertices, winding fixed by recalc normals). Sizes (model): base 0.251 m (0.45 x head
width), length 0.237 m (0.50 x head height), thickness 0.028 m (0.05 x head width); outer face head pink (cell 0),
inner face #D47A7C (cell 4), edges cell 3; 44 tris per ear.
Numbers (pre head scale, printed by the build): hinge (0.190, -0.585, 0.830), tip (0.254, -0.726, 0.756); model
pivots Ear.L/R (+-0.209, -0.479, 0.812); tip 0.013 m below eye height, tip X 0.280 m (cheek outside); nothing behind
the head's rear plane (0.000 m), highest ear point 0.006 m below the crown (fold height 0.035 m); flap 0.030 m clear
of the skull at fold and tip; eye gap 0.18 m; mirror 0.000000.
Remaining vs reference: at the requested 0.45 x / 0.50 x sizes the flaps are about half the size of the reference
ears (which hang lower over the cheeks); a bigger flap is a parameter change (FLAP base/length) if the lead wants it.

## Result
tris 1416: Head 164, Nose 156, Tail3 152, Pelvis/Spine1/Spine2 76 each, Ear.L/R 44 each, Eye.L/R 44 each, Tail2 56,
Jaw 44, Neck2 44, Tail1 32, Neck1 28, legs 28 per part (12 parts).
Size: width 0.660 x length 1.709 (snout -> tail curl) x height 0.935; nose -> rump 1.497, back top 0.878, belly 0.203,
head 0.558 w x 0.474 h.
Pivot: root at ground under the volume centroid; parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000 (Tail1-3 excluded: curl plane yawed on purpose),
worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 27 meshes + root, 1416 tris, dims 0.660 x 1.709 x 0.935, texture found in FMS_Pig.fbm.

## Deviations
- Head straight (the reference turns it slightly towards the camera).
- Tail curl plane yawed 35 deg to the pig's left so it reads face-on from the front-left (asymmetric by design).
- Jaw is a small chin block mostly inside the head (the reference shows no separate jaw); visible only as a lip line.
- No LOD1 (mesh-only round, as Calf/Cat).

## Rig + clips (rig_pig.py, pig_clips.py; mesh geometry, part names and pivots unchanged)
- Skeleton Q without Horn.L/R: 25 bones (Cow names + hierarchy, Tail1-3 along the curly tail), armature object `Rig`,
  registered at runtime as ar.SKELETONS['QP'] (shared modules untouched); check_rig names/hierarchy OK, roll_bad [].
  Bone heads = part pivots; Head -> Nose pivot, Ear along the hinge -> tip, Tail3 continues the Tail2 direction 0.10 m.
- Binding (Sheep pattern): every part object keeps its name, ONE vertex group weight 1.0 + Armature modifier, parented to
  Rig; Eye.L/R and Nose -> Head. No 2-bone blends needed for the clip ranges (bend test).
- Bend test: legs +-45/35, knees 100, neck down 110 total, neck yaw 85, ears, tail 40: no holes. Spine segments bent
  10 deg + body pitch 15 / roll 10 show steps between the rigid body parts and head-up -65 opens the neck -> clips keep
  spine bends <= 3 deg (no Spine2 counter-sway) and no head-up.
- Pig_Idle 3.5 s / 105 f: 2 breaths, head drift, 2 sniff bursts (fast small head nods), ear flops L 0.18 / R 0.52 /
  L twitch 0.84, curly tail twitch bursts 0.35 / 0.75.
- Pig_Walk 0.9 s / 27 f: lateral-sequence walk (Sheep gait copy), duty 0.60, 0.34 m/s, step 0.184 m, lift 4 cm, waddle
  roll 3 deg + Pelvis yaw sway 2 deg, head bob x2, ears bounce, tail curl bobs; Footstep events 0/7/14/20
  (FMS_Pig.events.json).
- Pig_Root 3.0 s / 90 f: front feet 3.5 cm forward (braced, legs straight), body -4 mm; grid search (Sheep Graze
  pattern, Neck1 slide keyed in every take, slide penalised): neck pitch 80 (Neck1 48 / Neck2 32), head -20, no slide ->
  snout disc min z 0.006 m in front of the hooves; 5 plough thrusts (push 4.5 cm forward along the ground, lift 1.8 cm and
  pull back), head digs 2.5 deg per push, ears hang 10 deg forward, tail wiggle 2 Hz. Snout lowest z over the clip
  -0.0027..+0.030 m. Rounds: 1 knees buckled (body drop + nose-down) -> feet-only brace; 2 neck ridge above the head
  (neck 55) -> 3 prefer head pitch: Neck1 slid 14 cm, staircase of neck rings -> 4 slide penalised: clean.
- Metrics: loop closure 0.0 deg (all 3); lowest vertex Idle 0.000 / Walk -0.0039 / Root -0.0027 m; walk foot slip 3.18 %
  of step (stance foot max height 1.3 mm); joint-limit violations 0; neck yaw total <= 3 deg.
- FBX: 27 skinned parts + Rig, 3 takes Pig_Idle 105 f / Pig_Walk 27 f / Pig_Root 90 f (NLA, bake_space_transform);
  re-import 25 bones, 27 meshes, 1416 tris, vertex error 0.0 m for all takes, texture found.
- GIFs (anim_gif.py): Previews/Anim/Pig_Idle.gif 1.71 MB 7.0 s, Pig_Walk.gif 0.92 MB 1.8 s, Pig_Root.gif 2.14 MB 6.0 s
  (2 passes each, 640 px, 20 fps).
- Known: in Root the far ear (rigid on Head) shows behind the crown from the 3/4 view; 27 SkinnedMeshRenderers per pig
  (part names kept) - merge at import if the draw-call budget needs it; FBX root 'Rig' Lcl Rotation -90 X (as the Cow).
