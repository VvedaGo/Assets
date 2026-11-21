# LIV-13 Kid (baby goat) - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-13.png` (1536x1024): front-left three-quarter (~45 deg azimuth, ~15 deg
above), head turned fully to the camera, body receding to the right.
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-13: kid, white, small horns, long ears, 0.6 x 0.5 m (length nose-tail x back
height, section 5 convention), 1200 tris (lead: within +15% = 1380), skeleton Q.
Lead brief: white, tiny horn buds, long ears drooping sideways, no beard, big head (~140-150% of realistic, clearly a baby),
short body, slim legs with dark hooves, short upright tail, dark disc eyes #2A1D17.
Anchors followed: Goat (`../Goat/build_goat.py`: Model/loft/tuck, ears as leaf lofts, horn = sunk tapered tube, objects(),
coplanar_all, check sheet, export), Lamb (baby proportions, head group scale about the neck joint, cupped ear colours),
preview `_common/animal_render.preview` (read-only). Script: `build_kid.py -- LIV-13 build|look|export`.

## Measured from the reference (ground ~920 px, back top ~470 px -> back 0.46 m, ~1.05 mm/px; head ~10% nearer)
| Feature | px | model (m) |
|---|---|---|
| back top | 450 above ground | 0.46 |
| belly | ~180 above ground | 0.20 |
| head width (cheeks) / height (poll-chin) | 460 / 510 (perspective-inflated) | ~0.36 / ~0.40 (compromise, see Deviations) |
| ear length / width, span | ~300 / ~140, 1085 | 0.29 / 0.15 each, span ~0.9 |
| eye (hexagon, pointy top) | ~65 | 0.06 |
| horn height / base | ~110 / ~70 | 0.09 / 0.06 |
| lower leg / hoof width, hoof height | ~85 / ~100, ~55 | 0.085 / 0.10, 0.06 |
| tail | ~120 tall | 0.12, flattened leaf, up-back |

## Features (after the coordinator rework)
Warm-white faceted barrel (10 sides x 7 rings, 0.46 m long), short neck; rounded-cube head (8-vertex rings with a wide flat
face facet, big side facets, flat top, small forward muzzle; 0.31 m wide), dark hexagon eyes (pointy top) flush on the
face facet and set wide apart, pink inverted-triangle nose with a philtrum stem, chin block; large flat horizontal pointed
ear leaves (0.26 m visible) with a cupped pink inner face facing forward, shaded back; thick dark grey-brown horn nubs leaning
out/up; four 6-sided legs 0.09 m without bands, flat-topped dark hoof caps 0.108 m x 0.062 m; large upright leaf tail
(0.15 m). Coat cells by face normal (warm white / shade / underside, bright face facet).

## Material class
Flat palette `T_FarmAnimals_Kid_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Kid`: 0 warm white #F2E8DE, 1 shade #E6D9CC,
2 underside #D6C7B8, 3 bright face #F8F1E9, 4 horn #857169, 5 horn tip #6B5850, 6 nose #E5A49C, 7 ear inner #D9958E,
8 eye #2A1D17, 9 hoof #3A2E28, 10-11 spare, 12-15 series spares.

## Parts (object `FMS_Kid_<Part>`, direct children of empty `FMS_Kid`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Horn.L/R, Eye.L/R, Nose, Front/Hind Upper/Lower/Foot .L/.R,
Tail1-3. No Beard (reference shows none). Joints overlap by tuck rings (body, neck, tail) or sunk ends (legs, ears, horns,
eyes, jaw).

## NOT modelled
beard, mouth line, teeth, eyelids, pupils, hair, collar/bell, ground; head turned to the camera (rest pose straight).

## Rounds (first pass)
1-4: first pass (head 0.42 m wide, 1316 tris, banded legs) - superseded by the rework below.

## Coordinator rework (8 items)
R1. head x0.72 (0.418 -> 0.30), rounded-cube head (8-vertex rings), body 0.50 long, legs without bands + flat hoof caps,
    ears 0.26 m horizontal, thicker darker horns, tail 0.15 m, warm palette, NB 10, preview sun mirrored to the camera side.
R2. head too small vs the coordinator's own ratio (body/head 1.68), ring under the chin (jaw/neck), head floating high.
    -> head 0.31 (x1.035), body 0.46 long (ratio 1.48), head lowered onto the chest, jaw fully in the muzzle, eyes 0.028.
R3. legs looked long under a shallow body; jaw floating (gap 9 mm). -> body deeper (belly 0.205, back 0.51), jaw pokes 5 mm.
R4. jaw cap a small ring under the nose in the front view -> jaw moved behind the chin. Preview camera (1.0, -0.72, 0.19):
    the template's lower, more frontal view hid the torso behind the head.
Views checked: reference angle, preview, side, back, front, top, 128 px.
Remaining (nitpicks): reference head turned to the camera; body seams between tuck rings in the side view (as Goat);
from behind the head and ear backs are in the sun shadow (darker).

## Coordinator rework 2 (independent review 3/5: slanted eyes, tongue-like nose, ears hidden, long legs)
Q1. Head built straight down (tilt 90): vertical face; rings 1-2 share their front -> two planar vertical eye facets 18 deg
    outward with a centre ridge; hexagon eyes (pointy top, axis = facet normal) flush, 3 mm proud -> round, not skewed.
    Nose: muzzle rings 3-4 share one vertical face plane; pink triangle 1.5 mm proud + philtrum 0.8 mm proud, flush.
    Ears straight out (d = 1, 0, -0.03), pink side forward-up, span 2.2x head. Legs: body/neck/head/tail lowered 0.045,
    each leg one continuous taper r 0.052 -> 0.046 (1.13x), flat hoof caps 0.110 x 0.058. Head x1.14 (0.342 wide, +10%).
Q2. far ear hidden behind the deep head in 3/4 -> ear roots moved to the front of the head sides, 8.5 deg forward.
Q3. white sliver on the rear flank (hind leg top ring 3 mm outside the body) -> top ring 0.060 at z 0.33.
Views checked: reference angle, preview (0.72, -0.80, 0.20), side, back, front, top, 128 px.
Remaining (nitpicks): far eye foreshortened in the 3/4 view (reference turns the head to the camera); body tuck seams.

## Coordinator rework 3 (second review 3/5: box-lid head top, chest/shoulder wedge, near ear like a fin)
T1. Crown: the flat top cap ring replaced by 3 bevel rings + a small cap (s -0.048/-0.034/-0.008): crown raised 0.055 m
    (16% of head height), rounded faceted ball; horn buds re-seated on the crown (base sunk 0.036).
T2. Wedge found by hiding parts: Spine2's steep high-shouldered front ring + flat front cap. Chest rebuilt as a gradual dome
    (rings y -0.252/-0.238/-0.205/-0.158, front top 0.41-0.50, tiny cap) -> one convex volume from under the chin into the barrel.
T3. Ear roots moved to the head side at eye level (s 0.085), pointing horizontally outward (d = 1, -0.12, 0); in 3D clear of
    the body (lower ear edge 0.06 m above the chest top); both ears visible in the 3/4 preview.
Views checked: reference angle, preview, side, back, front, top, 128 px.
Remaining (nitpicks): the near ear overlaps the back silhouette in the 3/4 projection (straight rest-pose head; the reference
turns the head); far eye foreshortened in 3/4; body tuck seams.

## Result
tris 1144. Per part: Pelvis 56, Spine1 76, Spine2 116, Neck1 44, Neck2 60, Head 140, Jaw 44, Ear 56x2, Horn 32x2, Eye 20x2,
Nose 20, Upper 32x4, Lower 20x4, Foot 20x4, Tail1 20, Tail2 32, Tail3 32.
Size: width 0.751 (ears) x length 0.681 (nose -> tail) x height 0.768 (horn tips); back 0.467, belly 0.160, poll 0.689,
chin 0.295, head 0.342 x 0.394, ear span 0.751 (2.2 x head). Pivot: root on the ground under the volume centroid (shift
+0.087 m in Y). Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst gap 0, coplanar 0, min z 0.
FBX re-import: 29 meshes + root empty, 1144 tris, dims 0.751 x 0.681 x 0.768, texture found in FMS_Kid.fbm.

## Deviations
- nose -> tail 0.68 m vs 0.6 catalogue (+13%); back 0.47 vs 0.5.
- preview: local copy of `_common/animal_render.preview` with the key sun mirrored to the camera side, camera
  (0.72, -0.80, 0.20); otherwise the pack template.
- head straight (reference turns it to the camera). No Beard. No LOD1 (mesh-only round).

## Rig / animation (rig_kid.py + kid_clips.py; copied from ../Lamb (Play_Hop) with the Goat skeleton/tails; mesh unchanged)
- Skeleton Q: Cow's 27 bones (Horn.L/R, Tail1-3; no Beard - the kid has none). Rigid binding, Eye/Nose -> Head.
- The kid legs bend at a LOW joint (Lower pivot 0.10 m, Lower = 4.5 cm pastern): every leg folds with the pastern going
  back (knee-forward IK branch for all four legs, runtime-only change of the leg table) and off the ground the hoof
  follows the pastern (foot pitch >= -12 deg, backed off where the hoof block would dip under the ground). Kid-local limits
  HindLower x (-3, 170) / HindFoot x (-60, 120) (fetlock-like, = front). Round 1: hooves held vertical read as broken
  ankles + FrontFoot -79 deg -> this fold; hop squash 2.5 -> 1.2 cm.
- Kid_Idle 3.0 s / 90 f; Kid_Walk 0.6 s / 18 f (0.24 m/s, step 0.084 m, lift 3 cm, hoof flick 30 deg; Footstep events);
  Kid_Play_Hop 1.0 s / 30 f (squash 1.2 cm, all four feet off frames 8-20, arc 0.11 m, pitch +-7 deg, legs tucked, tail
  and ears lag; Takeoff f8 / Land f20 events).
- Metrics: closure 0.0 deg all; lowest vertex 0.0 / -0.5 mm / 0.0; walk slip 0.78 %; limit violations 0.
- FBX: 29 skinned parts + Rig (27 bones), takes 91 / 19 / 31 f, 1144 tris, re-import vertex error 0.0 m, texture found.
