# LIV-02 Calf - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-02.png` (1536x1024). Calf stands with the body seen from the front-left
(~35-40 deg off the side view, low camera) while the HEAD IS TURNED to look straight at the camera.
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-02 - brown-and-white, huge head, short legs, no horns, 1.2 x 0.9 m, 1500 tris, Q.
Lead brief: head ~150% of realistic, legs 30-35% shorter relative to the cow, dark disc eyes #2A1D17, pink nose, dark
hooves, patches as per-face palette cells without stair-steps. Polish pass (coordinator): reference wins for ears and body
length, belly closer to 0.35, rounded patch blobs, round muzzle, face must read in the preview, <= +10% of 1572 tris.
Anchors followed: Cat (`../Cat/build_cat.py`: separate skeleton-Q parts, tuck joints, part naming) and Cow
(`../Cow/build_cow.py`: tilted head frame, ray-cast eyes/nostrils, hooves); preview via `_common/animal_render.preview`
(read-only, not changed).
Script: `build_calf.py -- LIV-02 build|look|export`.

## Measured from the reference (ground y=955 px, back y=295 px -> 0.90 m => ~0.00136 m/px; perspective: head is nearer)
| Feature | px | model (m) |
|---|---|---|
| back height | 660 | 0.89-0.90 |
| belly underside | 255 (0.35 m) | 0.32 (compromise with "legs 30-35% shorter") |
| body chest -> rump (projected 840 px, ~1.7 x head width) | | 1.125 |
| head width | 500 | 0.59 incl. scale 1.22 |
| ear length / width | 215 / 150 | 0.28 visible / 0.21 |
| eye diameter | 75 | 0.068 (8-gon, 5 mm proud) |
| leg width lower / hoof, hoof height | 155 / 170, 70 | 0.155 / 0.18, 0.085 |
| brown -> white on legs (knee) | y 790 | z 0.225 |

## Features (rework round 3)
big round faceted head (12 sides), lowered 5 cm: ONE centred white blaze face column (~0.27 x head width) from the poll to the
muzzle top, both cheeks brown, dark 8-gon eyes; the muzzle is the head's own rounded front (no box, no step under the nose),
covered by a pink shell 4 mm proud from s=0.38 (Nose part) with 2 slanted nostrils; Jaw tucked inside; large leaf ears
(brown rim, pink dish). Chubby barrel 0.56 m wide x 0.68 m deep (14 x 13 rings), WHITE base with 3 big brown patches: shoulder
(withers down into the front legs), mid-rear patch over the back, thigh patch into the hind legs; white chest, slanted white
band widening into the belly, white rump top. Patch edges: distance field with wobble, vertices snapped onto the contour
(centre-line vertices only slide along the body -> exact mirror), quads split along it. Legs: stubby 8-sided tapers
(r = 0.109 + 0.068 z, 1.15x ground -> belly 0.24 m), brown upper, white sock 0.075-0.17 m, dark hoof cap 4 mm proud; flush
Upper|Lower joint at the sock line. Tail swung 32 deg towards +X so it shows past the rump: brown root, cream middle, brown tuft.

## Material class
Flat palette `T_FarmAnimals_Calf_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Calf`: 0 brown #AE6740, 1 brown dark
#86492B (tuft), 2 white #F2E7DC, 3 spare, 4 nose pink #DE9B88, 5 nostril #9A5649, 6 ear pink #D4877A, 7 eye #2A1D17,
8 hoof #3A2E28, 9-15 series spares.

## Parts (object `FMS_Calf_<Part>`, direct children of empty `FMS_Calf`, pivot on the joint) - unchanged in the polish pass
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose (pad + nostrils), FrontUpper/Lower/Foot.L/R,
HindUpper/Lower/Foot.L/R, Tail1-3 (Tail3 includes the tuft).

## NOT modelled
horns, udder, eyelids/pupils, teeth/tongue, collar/bell/ear tags, hair strands, ground/grass,
head turned to the camera (rig rest pose = head straight forward; the turn is a pose, not geometry).

## Rounds
1-4 (first pass): horse-like head -> round big head; barcode stripes -> blocks; chest/leg step removed; tilt 50.
P1 (polish): body 0.82 -> 1.125 m, belly 0.29 -> 0.32, ears 0.22 -> 0.28, 12-sided rounded pad, blob field + contour snap.
P2: flank/rump still stripe-like, near cheek in sun shadow, head small vs the longer body -> broader blobs joined to the
belly, head scale 1.15 -> 1.22, brown slightly lighter, tilt 45 (face front turns to the template's front sun), preview
camera (0.70, -1, 0.14) in this script only.
Remaining (nitpicks): the reference head is turned to the camera (ours straight); the far cheek side of the face is
naturally darker in the preview (template sun); white areas are a bit smaller than in the reference.

Rework R2 (independent review 3/5): blaze was off-centre (face index bug: with the ring phase pi/12 the centred top face
is k=11, every head level was shifted one face to the right since round 1) -> fixed; zebra bands -> saddle + rump patch on
cream; lower-lip slab -> jaw inside one muzzle box; tail hidden -> swung out 20 deg; banded legs -> one taper, cream.
Views checked: reference angle, side, front, behind, above, 128 px, EEVEE preview.

Rework R3 (second review 3/5): legs long/thin, small body, brown-top/white-belly split, snout step, neck hunch.
-> belly 0.32 -> 0.24, legs 1.4x thicker, brown upper + white socks, barrel 1.3x wider / 1.19x deeper, 3 brown patches on
white, head lowered 5 cm, muzzle = head front + pink shell, slimmer upper neck rings, tail swing 32 deg.
Conflict noted: "55% of current leg" (0.18 m) and "leg 0.7x body depth" (0.48 m) cannot both hold; the reviewer measured the
cream leg + cream belly against the brown top. Chosen: visible leg 0.24 m = 0.35x body depth 0.68 (reference 0.63x).
Views checked: reference angle, side, front, behind, above, 128 px, EEVEE preview.

## Result
tris 1720 (+9.4% vs 1572; +14.7% vs 1500 catalogue): Spine1/Spine2 164, Head 164, Pelvis 136, Nose 132, Ear 76 x2, Tail3 76,
Neck2 60, Neck1 44, Jaw 44, Upper 44 x4, Lower 44 x4, Foot 28 x4, Tail1/2 32, Eye 28 x2.
Size: width 1.080 (ears) x length 1.796 (nose -> tuft) x height 1.153 (poll); nose -> rump 1.584, back 0.920, belly 0.24,
body 0.56 wide x 0.68 deep.
Pivot: root at ground under the volume centroid (geometry shifted +0.147 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000 (tail excluded: swung on purpose), worst contact gap 0,
coplanar 0, min z 0.
FBX re-import: 27 meshes + root, 1720 tris, dims 1.080 x 1.796 x 1.153, texture found in FMS_Calf.fbm.

## Deviations
- Head straight (reference turns it to the camera).
- Nose -> rump 1.58 m vs 1.2 m catalogue (reference body proportion wins, coordinator decision).
- Legs: belly 0.24 m; leg/height 0.26 vs cow 0.41 (37% shorter relative) - stubbier than the reference (0.35 m) per review.
- Patches mirror-symmetric L/R.
- No LOD1 (mesh-only round).

## Rig + minimum clips (rig_calf.py, calf_clips.py; mesh geometry, part names and pivots unchanged)
- Skeleton Q without Horn.L/R: 25 bones, Cow names + hierarchy, armature object `Rig`; bone heads = part pivots.
- One skinned mesh `FMS_Calf` (27 parts joined, 920 verts, 1720 tris), parts rigid 1.0 to their bone (Eye/Nose -> Head)
  except Cow-style 2-bone blends: body across Spine2|Spine1|Pelvis (+-8 cm), Neck1 root -> Spine2, Neck2 -> Head, knee line
  50/50 Upper/Lower, sock tuck -> Upper, sock bottom ring -> Foot (stops the thick sock poking below the hoof); max 2 influences.
- Bend test: legs +-60..75, knees 150, neck +-, ears, tail, spine 12-20 deg: no holes after the blends.
- Clips (30 fps, in place, NLA takes): Calf_Idle 3.0 s / 90 f, Calf_Walk 0.8 s / 24 f (diagonal sequence, 0.62 m/s,
  step 0.31 m, calf-local gait copy with reach 0.998 + exact per-frame body drop), Calf_Lie_Idle 3.5 s / 105 f
  (front/hind upper 30 deg, knees 150 deg, legs tucked under the body; chest rests on the folded legs, belly 0.075 m).
- Metrics: loop closure 0.0 deg (all), lowest vertex Idle 0.000 / Walk -0.0017 / Lie -0.0099 m, foot slip 0.76% of step,
  joint limit violations 0. FBX re-import: 25 bones, 1720 tris, 3 takes 90/24/105 f, vertex error 0.0 m, texture found.
- Events: FMS_Calf.events.json (Walk Footstep x4). GIFs: art/Farm_Animals/Previews/Anim/Calf_{Idle,Walk,Lie_Idle}.gif.
- Known: thin white sock edges visible under the chest in Lie_Idle; FBX root 'Rig' carries Lcl Rotation -90 X (as the Cow).
