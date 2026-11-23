# PET-01 Dog - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/PET-01.png` (1536x1024): front-left three-quarter, ~11 deg above, chest towards
the camera, head looking at the camera (ours straight: rig rest pose).
Catalogue: FARM_ANIMALS_PACK.md 5.3 PET-01 - herding collie, white/rust/black tricolour, white collar, drooping triangular
ears, bushy tail, 1.0 x 0.65 m, 1800 tris (lead: stay within +15% = 2070), skeleton Q.
Anchors followed: Cat (`../Cat/build_cat.py`: Model/loft/tuck, head loft along -Y, cone eyes, ray-cast face parts, tail
spline), Goat (`../Goat/build_goat.py`: patch field + contour snap -> rounded patch edges, leg joint bands, `look` sheet),
Horse/Goat (hind leg slanting back to the hock). Preview: `_common/animal_render.preview` (read-only).
Script: `build_dog.py -- PET-01 build|look|export`.

## Size decision
Pack convention: "0.65" = back height. The reference proportions (wheelbase ~ back height, body depth 0.56 x back,
legs 0.44 x back, head + ears reach 1.45 x back) with 1.0 m nose -> tail give back ~0.45 m and ear tips ~0.65 m.
The lead's words "1.0 m long, 0.65 m tall" are taken literally (overall height); back height deviates from the catalogue
convention (reference wins). Documented below with the real numbers.

## Measured from the reference (ground ~990 px, ear tips ~20 px -> 0.65 m, ~0.00067 m/px; head nearer the camera)
| Feature | px | model (m) |
|---|---|---|
| back top (withers) | 665 above ground | 0.47 (ruff at the withers), rump 0.43 |
| belly / ruff bottom | ~290 / ~230 above ground | 0.25 / 0.20 |
| head: chin / nose / eyes / crown | 600 / 645 / 785 / 895 | 0.40 / 0.47 / 0.53 / 0.59 |
| ear span | 515 (perspective) | 0.30 |
| eye diameter | ~32 | 0.024 (8-gon, 2 mm proud) |
| nose pad | ~70 x 45 | 0.052 x 0.035 |
| upper / lower leg width | 130 / 105 | 0.094 / 0.074 (8-gon) |
| paw width x height, sole | 140 x 70, 12 | 0.10 x 0.056, 9 mm |
| tail diameter (middle), length | ~160 | 0.11, ~0.36 along the curve, tip at z 0.13 |

## Features
Faceted barrel body (14 sides) with a deep white chest ruff (bib down to 0.20), black saddle from behind the white
collar over the back and rump, rust shoulder/elbow and rust thigh, narrow white belly strip; patches = world-space label
field (white > black > rust, low-frequency wobble), ring vertices snapped onto the contours -> rounded irregular edges;
left/right layouts differ (two fields, both contours snapped on both sides -> geometry stays mirror-exact).
Thick short neck (black nape + rust sides on Neck2, white collar on Neck1). Head 12-sided loft: black cap and back of the
skull, white blaze widening to a white muzzle, rust brows/cheeks around the dark eyes, white chin block (Jaw), dark nose pad.
Folded ears: thick 6-point leaf rising from the skull then folding forward-out-down; rust inner face + rust rim, black
outer flap. Legs 8-sided, white socks, white front of the front legs (bib flows down), rust elbow and thigh, cream joint
band at knee/hock, big white paws with dark soles. Bushy tail Tail1-3 carried low: black top, rust underside/band,
white rounded brush tip.

## Material class
Flat palette `T_FarmAnimals_Dog_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Dog`: 0 white #F3EDE3, 1 joint band/cream
#E2D6C4, 2 rust #D2843F, 3 rust shade (spare) #B96C2C, 4 black coat #3F3332, 5 black shade (spare) #2F2625, 6 nose
#262020, 7 sole #3A2E28, 8 eye #2A1D17, 9-15 series spares. Variants (black-white, red) swap cells 0-4 only.

## Parts (object `FMS_Dog_<Part>`, direct children of empty `FMS_Dog`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R, Tail1-3.
Joints overlap by tuck rings (body, neck, tail) or sunk ends (legs, ears, eyes, nose, jaw).

## NOT modelled
mouth line, teeth/tongue, eyelids/pupils, toes/claws, fur strands, collar/tag, ground; head turned to the camera.

## Rounds
1. (Workbench) body/ruff slim and shallow -> legs looked long; no mane; ears pricked like a cat; tail thin; saddle high.
   -> ruff hw 0.18 down to z 0.16, barrel hw 0.15, legs/paws +10%, head x1.06, tail radii +25%, saddle lower mid-flank.
2. (EEVEE 6 views) ears still rust pricked triangles, no black mane framing the face, collar a thin ribbon, joint bands
   look like bandages. -> wide Neck2 mane (black), collar line moved back/steeper, flatter lighter joint band.
3. Ear flap twisted edge-on (width axis re-projected per ring) -> fixed hinge axis, flap folds forward-out-down over it:
   black outer flap over rust inner face from the front, rust rim on the standing part from behind. Black brow bars -> rust.
4. Tail thicker with a bigger white brush, domed rump; centre-line vertices no longer snap sideways (mirror 0.019 -> 0).
5. (preview) thigh top poked a rust sliver through the black hip -> thigh top sunk into the pelvis.
Remaining (nitpicks): reference head turned to the camera (ours straight, rest pose); reference ruff is shaggier with
rust on its upper sides; one small dark facet at the thigh/saddle edge; hock bend subtler than a real dog.

## Result
tris 1900 (target 1800, +5.6%, limit 2070). Body 492 (Pelvis 164, Spine1 136, Spine2 192), Neck 104, Head 188, Jaw 32,
Ears 2x32, Eyes 2x14, Nose 44, legs per side Front 76+44+60 / Hind 92+44+60, Tail 44+60+92.
Size: width 0.351 (ears) x length 1.048 (nose -> tail) x height 0.641 (ear tops); back 0.472, belly 0.209, crown 0.593,
tail tip low point 0.123. Pivot: root on the ground under the volume centroid (geometry shifted +0.015 m in Y).
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0, min z 0; 36 contour-
snapped vertices; 3 body faces coloured differently L/R (asymmetric patches, symmetric mesh).
FBX re-import: 27 meshes + root empty, 1900 tris, dims 0.351 x 1.048 x 0.641, texture found in FMS_Dog.fbm.

## Deviations
- back height 0.47 m instead of 0.65 (catalogue convention = back height); 0.65 taken as overall height (0.641) to match
  the reference proportions at 1.0 m length (1.048 incl. the tail brush).
- head straight (reference turns it to the camera). No LOD1 (mesh-only round, like the other animals).

## Rework (coordinator, 2026-11-20) - supersedes the size, parts, rounds and result above
Changes: back 0.628 (was 0.47), nose->tail 1.317, ear tops 0.916, belly 0.322 (legs 35% of the height); body 10 sides x 10
rings (large facets), black saddle neck -> tail base, orange flanks + thigh "trousers" to the hock, white belly/chest;
new part Ruff (10-sided shield, front crease, 3 cream shades #F2E8D8/#E6D9C3/#D8C8AE, bind to Neck1/Spine2); head 10-sided
wedge x1.08 with a 1-face white blaze nose -> forehead, orange brows/cheeks around 8-gon dark-brown eyes, black cap, long
narrow muzzle; ears semi-erect (0.09 standing + 0.066 flap folded forward over a fixed hinge), tan inner face framed black;
tail 3 segments, 0.20 m wide at the middle, 0.51 m long, black top / orange sides+band / white brush tip, carried low;
legs plain tapered (no bands), one 4-6 mm knee/hock step, big rounded white paws with a 6 mm dark sole.
Palette: 0 #F2E8D8, 1 #E6D9C3, 2 orange #D2843F, 3 ear tan #E3A35E, 4 black #3F3332, 5 #D8C8AE, 6 nose #262020,
7 sole #3A2E28, 8 eye #2A1D17.
Rework rounds: R1 ruff an egg in front of the chest, legs spindly, jagged trouser edge -> ruff wraps back, legs +15%,
per-ring leg colours. R2 ruff hid the cheeks -> ruff top lowered to 0.69, head x1.08. R3 weak mane, tiny fold -> wider
mane with orange lower sides, longer flap. R4 tail merged with the black rump -> lifted root, orange sides/band, preview
camera turned to (1.0, -0.62, 0.22) so the tail reads.
Result: tris 1696 (budget 2800). Checks 0/0/0/0, mirror 0, gap 0, min z 0. FBX re-import 28 meshes + root, 1696 tris,
dims 0.434 x 1.317 x 0.916, texture found.
Remaining: ruff smoother than the shaggy reference; tail partly behind the thigh at the preview angle; head straight.

## Rework 2 (independent review 2/5) - supersedes rework 1 where different
1. Ruff = mane: 12-sided horizontal slices from under the ears/cheeks (z 0.76) down to the chest, max half width 0.235
   (~1.5x the neck), back half sunk into neck/shoulders, jagged lower edge with 5 points (z 0.215, notches 0.30); white
   front, #E6D9C3 sides, #D8C8AE fringe, orange sides and black nape blending into neck and shoulders. 140 tris.
2. Tail: flattened bushy wedge (h/w 1/0.8), 0.50 m long (0.52x body), max 0.23 m tall, root on the rump top, pointing back
   ~19 deg down, clear of the hind legs; black top, orange underside, white last third.
3. Paws: chamfered flat-bottomed boxes, 1.1x the lower-leg width (0.126 x 0.16), 6 mm dark sole.
4. Head 12-sided: one centred top face = narrow blaze forehead -> nose; orange brows/muzzle sides; snout -15%.
5. Body 0.96 m (1.53x the head+ruff height 0.63), back level 0.628; legs plain taper (lower leg 1.5 mm inside the upper).
Fixes after the preview: white leg-top corner poking through the shoulder (leg top ring sunk), ruff lower side facets orange.
Result: 1688 tris; 0.470 x 1.693 x 0.921 m; checks 0/0/0/0, mirror 0, gap 0, min z 0; FBX re-import 28 meshes + root,
1688 tris, dims match, texture found. Preview camera (1.0, -0.78, 0.22).

## Rework 3 (second review 2/5; reference rules, old length limits dropped) - supersedes reworks 1-2 where different
1. Torso 0.58 m (0.753x the rework-2 torso; asked 0.65x - kept slightly longer so the saddle/flank/thigh patches still
   fit), depth 0.342 (1.2x) -> length/depth 1.70; belly 0.392, back 0.757; width x1.15 (hw 0.24). Legs 35% of height.
2. Head group x1.46 (1.35x the rework-2 head): head width 0.38, muzzle 0.36x head length (SNOUT 0.75), blunt tip (last
   rings wider/taller); centred 1-face blaze, orange mask, dark nose kept.
3. Ears: base 0.152 wide (0.40x head width), stand 2/3 + fold forward 1/3, black outside, tan inner, mirror-identical.
4. Black frame: two black cheek-fur fins (part of Head, 6-sided, sunk into the head side) from below the ears to the jaw
   corner + black back of the skull, Neck2 sides and ruff top; orange mask kept.
5. Ruff lower edge raised to the chest line (points 0.395, notches 0.46), jagged 5 points kept.
6. Thigh sunk into the pelvis (top ring 0.058 inside the body), no hip plank; flank/thigh orange from the body field.
Legs x1.15 thicker (lower r 0.063-0.069), paws 1.1x (0.144 x 0.18), tail stations relative to its length (white last 1/3).
Result: 1800 tris; 0.507 x 1.355 x 1.116 m; checks 0/0/0/0, mirror 0, gap 0, min z 0; FBX re-import 28 meshes + root,
1800 tris, dims match, texture found.

## Rig + clips (2026-11-20; mesh unchanged)
Scripts: `rig_dog.py -- PET-01 bend|anim|export`, `dog_clips.py` (pattern: Goat; rest-offset leg IK copy from Horse/Goat;
front legs forced to the forward-knee side because the paw rests 2 cm ahead of the shoulder).
Skeleton QD = Cow Q without Horn.L/R + Ruff (child of Spine2) = 26 bones. Eye.L/R, Nose -> Head; cheek fins in Head.
Weights 1.0 per part; blends (244 verts): knee/hock line 50/50, neck path Spine2|Neck1|Neck2|Head (Goat), tail path
Tail1|Tail2|Tail3 50/50 at the joints, Ruff = Ruff bone at the chest fading (smoothstep) to Neck1 under the cheeks.
Bend test (legs +-45 deg, knees 100/-90, neck +-40, turn 25, tail 35, ears, roll 8, ruff 10): no holes seen.
Dog_Idle 90 fr (3.0 s): 7 wags (2.33 Hz) with a 0.10-cycle lag per tail bone (15/21/27 deg), tail tip +-0.24 m, rump
counter-sway, 2 breaths, head turn 6 deg, ear twitches. Dog_Walk 24 fr (0.8 s): diagonal trot-walk (duty 0.58, step 0.39 m,
0.85 m/s), tail sway 7/10/13 deg + bounce, ruff bounce 2.5 deg, head level. Footstep events 0/1/12/13.
Metrics: loops 0.000 deg; lowest vertex Idle -1.3 mm, Walk -3.9 mm; Walk slip 0.02%; no limit violations.
FBX re-import: 26 bones, 28 meshes, 1800 tris, takes Dog_Idle 90 / Dog_Walk 24, vertex error 0.0 m.
GIFs: Previews/Anim/Dog_Idle.gif (6.0 s, 2.66 MB), Dog_Walk.gif (1.6 s, 0.89 MB).

## Sit_Idle (2026-11-20; rig, Idle and Walk unchanged)
Dog_Sit_Idle 105 fr (3.5 s), built in dog_clips.sit_pose/sit_clip with the existing bones: pitch searched so the shoulders
stand at 0.975x the front-leg length (front legs straight, vertical, paws 3 cm ahead) and the rump seats <= 6 cm:
pelvis -59 deg + Spine1/2 -8/-10 (hip 0.142, shoulder 0.508), neck/head counter-pitched to look ahead, Ruff +40 deg so it
hangs on the chest, hind legs folded (hock on the ground behind the hip at z 0.085, cannon forward 9 deg, paw under the
hip, spread 5 cm), tail on the ground behind curving right (-18/-38 deg). Motion: 2 breaths (Spine1/2, Ruff, Neck1), head
turn 6 + tilt 5 deg, ears twitch in turn (0.22 L, 0.64 R), tail tip lifts 16 deg twice with a slow wag 12 deg.
Deviation: torso tilt ~70 deg (hip->shoulder line), not 35-45: with front legs 0.52 m and hip->shoulder 0.39 m, straight
vertical front legs + a grounded rump need ~70 deg (at 45 deg the rump floats 11 cm). Metric limits widened for the sit
(my species table only): Pelvis x -65, FrontUpper x 70, HindUpper x 130, Ruff x 50.
Metrics: loop 0.000 deg, lowest vertex -5.9 mm, no limit violations; Idle/Walk re-verified unchanged (-1.3 / -3.9 mm, slip 0.02%).
FBX: 3 takes (Dog_Idle 90, Dog_Walk 24, Dog_Sit_Idle 105), re-import 26 bones / 28 meshes / 1800 tris, vertex error 0.0.
GIF: Previews/Anim/Dog_Sit_Idle.gif (7.0 s, 1.20 MB).

## Animation fixes round 1 (ANIMATION_FIXES.md 4-6, 2026-11-21; mesh and weights unchanged)
Walk rebuilt (`dog_clips.walk_dog`): 34 fr (1.133 s), stride 0.60 m (0.44x nose->tail), stance travel 0.36 m, 0.53 m/s, duty
0.60, diagonal couplets (HindL+FrontR, HindR+FrontL, front 0.18 cycle after its hind) -> same-side paws >= 0.20 m apart.
Stance windows centred under shoulder/hip. Body drop solved per frame from FK: front legs at 0.9995 of their length in
stance (bow <= 1.3 cm, was 8-14 cm), shoulder roll (Spine2, +-4.6 deg, neck counter-rolls) in front double support so
both front legs stay straight; hind drop = smooth envelope (hock bends more, backward). Swing: cycloid + sine lift
0.065 m, front wrist folds forward with the paw flipping back (flick 32), hind hock folds back.
Idle: hind girdle 3 cm lower + hind paws 2 cm back (hock flex 37-45 deg, visible), pitch solved per frame so the front legs
stay straight, sideways weight shift 1.2 cm + yaw, 2 breaths (spine x1.6, ruff), tail lifted 14/6/2 deg and wagging
24/32/40 deg (tip +-0.33 m, was +-0.24).
Sit_Idle: torso tilt 57 deg (asked 40-50), rump on the ground (lowest -4 mm), hip z 0.093, front legs straight and slanted
~32 deg forward, paws 4 cm apart; thighs splayed 50 deg (thigh frame built with X = hock hinge, hock pure X flex 128 deg),
cannon forward along the ground. Blocker for 40-50 deg: hip->shoulder joint distance 0.39 m < front leg 0.52 m, so with
the rump down the shoulder can rise at most 0.48 m (needs 0.52 for vertical legs); at 48 deg the straight legs slant 42 deg
and the dog looks like it slides. Fix needs a mesh change (longer torso or shorter front legs) - not done.
Limits (species table only): HindUpper z widened to +-80 (sit: euler z -76 = 50 deg splay with the pelvis pitched -54).
Metrics: loops 0.000 deg; lowest Idle -2.6 / Walk -1.4 / Sit -4.3 mm; Walk slip 0.31 %; 0 limit violations;
0 wrong-way knee/hock frames (new `leg_checks`). FBX re-import: 26 bones, 28 meshes, 1800 tris, takes Dog_Idle 91 /
Dog_Walk 35 / Dog_Sit_Idle 106 (import ranges), vertex error 0.0. GIFs: Walk 1.19 MB, Sit_Idle 1.51 MB, Idle 2.66 MB.
Remaining: in the sit, the white top of the metatarsus shows as a "heel" behind the 128 deg hock fold (rigid part, hip only
9 cm above the ground).

## Head rework 4 + Sit rig round 2 (2026-11-21, user-approved mesh change) - supersedes the head and Sit_Idle above
Head (build_dog.py, built in final metres around the head pivot HP, old x1.46 group scale removed):
- Skull 12-sided loft with non-uniform ring angles (narrow top face = blaze): broad crown (0.36 wide), real stop,
  muzzle 0.09 from the stop to the tip (was ~0.14, narrow, flat-topped -> fox), jaw shortened with it.
- Colours: black cap down to the brows, narrow white blaze crown -> nose widening to a white muzzle, orange mask
  around the eyes and cheeks, white chin. Eyes 8-gon discs r 0.024 (was 0.02), forward on the stop, 0.19 apart.
- Nose: broad flat pad 0.092 x 0.06. Ears: 0.115 standing (leaning out 39 deg) + 0.13 flap folded forward over a
  hinge = d1 x d2 (bug fixed: the old width axis collapsed the fold ring), tan inner face + tan flap underside, black
  outside. Mane: 7 black + 2 orange flattened 4-sided tufts per side (sunk in the skull) framing the face from behind
  the ears down past the cheeks. Cheek "headphone" fins removed.
Rounds (head sheet: ref | 3/4 | front | side | preview angle): R1 thin spike tufts, pointed ears -> chunky tufts;
R2 forehead orange, spikes sideways -> black cap, tufts down; R3/R4 fold collapsed / face sideways -> hinge fix, flap
forward; R5 ok from front; R6 muzzle -2.5 cm, 2 filler tufts.
Legs: lower-leg bottom rings 8% thinner, front pastern 6 mm forward (cheap, barely visible).
Result: 1796 tris (Head 296 incl. tufts, Jaw 32, Ears 2x32, Eyes 2x14, Nose 44); 0.509 x 1.279 x 1.134 m; checks
non-manifold/loose/degenerate 0/0/0, mirror 0, gap 0, coplanar 0, min z 0. Palette unchanged (16 cells, none added).

Sit_Idle (rig round 2):
- Geometry note: moving the shoulder pivot 0.12 m straight down only gains ~0.035 m in the sit (the joint also drops
  0.12*cos(tilt)), so it alone cannot fix a 45-50 deg sit. Done: FrontUpper pivot 0.52 -> 0.40 (chest bottom; leg mesh
  above z pivot+0.05 bound to Spine2; standing silhouette unchanged) PLUS a shoulder slide in Sit_Idle only: FrontUpper
  location keyed (world-vertical 0.059 m into the chest, like the scapula); own write_action copy keys FrontUpper
  location; leg IK accounts for it.
- Torso tilt (Pelvis->Spine2 joint line) 47.1 deg, hip 0.096, front legs straight, 8 deg forward, paws 0.29 apart;
  thighs forward-out (38 deg splay) beside the belly, white lower legs forward along the ground turned in 30 deg, hind
  paws 1.3 cm behind the front paws; joint raised until the paw box rests on the ground; tail on the ground.
- In the sit the hind joint folds FORWARD (it plays the stifle): leg_checks reports 210 "wrong-way" frames for Sit_Idle
  by design; Dog-only limits widened: HindUpper x -115, HindLower x +95 (Walk/Idle still 0 wrong-way frames).
Metrics: loops 0.0 deg; lowest Idle -4.6 / Walk -6.4 / Sit -5.5 mm; Walk slip 1.2 %; 0 limit violations.
FBX re-import: 26 bones, 28 meshes, 1796 tris, takes Dog_Idle 91 / Dog_Walk 35 / Dog_Sit_Idle 106, vertex error 0.0.
Remaining: thin light sliver under the belly between front leg and thigh in the sit; a few black tuft tips poke through
the ruff side; the head is straight (reference turns it to the camera).
