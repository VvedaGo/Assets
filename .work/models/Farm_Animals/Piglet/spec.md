# LIV-07 Piglet - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-07.png` (1536x1024). Body seen from the front-left, ~50-55 deg off the
head-on axis (leg spacing: near front->hind 420 px, front pair 215 px), camera ~10 deg above, weak perspective (near and
far hooves the same size). The HEAD IS TURNED to look at the camera (pose, not geometry - modelled straight as Pig/Calf).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-07 - pink, short legs, big head, 0.6 x 0.4 m (nose->rump x back), 1100 tris
(lead: stay within +15% = 1265), skeleton Q. Lead: baby, not a scaled pig: head ~150% of realistic, legs ~30% shorter
relative to the Pig, rounder body, floppy ears, small curly tail, eyes #2A1D17, snout disc + 2 nostrils, dark hooves.
Anchors followed: Pig (`../Pig/build_pig.py`: whole structure copied - Model/loft/tuck, head frame, ray-cast eyes and
ears, ear builder, snout fill + blind nostrils, corkscrew tail, part names, pivots, COM shift, views/close sheets, export)
and Calf (baby proportions, head straight deviation). `_common` and `Tools/blender` imported read-only.
Script: `build_piglet.py -- LIV-07 build|views|close|export`.

## Measured from the reference (ground 925 px, rump top 410 px -> back 0.40 m => ~0.00078 m/px)
| Feature | px | ratio | model (m) |
|---|---|---|---|
| back top (rump) | 515 above ground | - | 0.40 |
| belly underside | ~127 above ground | 0.25 of back | 0.085-0.10 (pig 0.29 of back -> legs ~30% shorter rel.) |
| head width (cheeks) | 720 | 1.40 x back (head nearest + turned) | 0.44 (1.1 x back, see deviations) |
| head height | 635 | 1.23 x back | 0.375 |
| snout disc w x h | 300 x 250 | 0.42 x 0.35 of head w | 0.18 x 0.15, 12-gon, protrudes ~0.045 |
| snout centre below head centre | 103 | 0.16 of head h | 0.06 |
| nostrils dia, spacing | 55-60, 120 | 0.40 of snout w | 0.034 x 0.037, centres +-0.037, 12 mm deep |
| eye dia, spacing | 70, 385 | 0.097 / 0.53 of head w | 0.043 (8-gon, 5 mm proud), x +-0.117 |
| ear length / width | ~300 / ~210 | 0.42 / 0.29 of head w | 0.20 / 0.14, 0.035 thick, folds forward-out |
| leg width | 120-135 | 0.23 of back | 0.088 (8-gon apothem 0.044) |
| hoof height / width | 45 / 135 | - | 0.036 / 0.10, flared |
| tail curl dia / tube | ~180 / ~40 | - | 0.10 / 0.032 -> 0.024 (6-gon), ~1.05 turns |
| nose -> rump | - | catalogue | 0.60 |

## Features (must read at 128 px)
Huge round faceted head (12 sides) carrying a big flat-fronted snout disc (rim + 2 recessed nostrils) and two dark 8-gon
eyes beside the top of the snout; ears rising from the top corners and flopping forward/out (outside pink, red-pink
inside); short round barrel body (10 sides) emerging behind the head; 4 stubby thick 8-gon legs with a slight knee band
and dark flared hooves; small chunky corkscrew tail on the rump. Uniform cool pink, only subtle back/belly tones.

## Material class
Flat palette `T_FarmAnimals_Piglet_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Piglet` (colours sampled from the
reference, lit areas, slightly deeper): 0 body #F3A5AE, 1 back #EC9BA5, 2 belly #F8BBC2, 3 ear outside #F0A0AA,
4 ear inside #D07282, 5 snout #EE96A0, 6 snout rim #E48A95, 7 nostril #B85A68, 8 eye #2A1D17, 9 hoof #3A2E28,
10 knee band #E28E99, 11-15 series spares.

## Parts (object `FMS_Piglet_<Part>`, direct children of empty `FMS_Piglet`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, FrontUpper/Lower/Foot.L/R,
HindUpper/Lower/Foot.L/R, Tail1-3. Joints overlap via tuck rings / sunk ends (5-10%).

## NOT modelled
eyelids/pupils/eye whites, teeth/tongue, bristles, mud, ground, ear tags, dewclaws, teats, head turn (pose).

## Rounds (EEVEE sheets: reference + 3/4, side, behind, rear 3/4, front, top; close-ups; 128 px thumbnail)
1. Legs read long (body bottom high at the leg stations, head above the belly); ears small cat-like and upright; head
   1.12x back height vs ~1.3x in the reference; 1332 tris. -> body bottom lowered (belly 0.062, flatter bottom
   exponent 2.9), legs shortened (knee band 0.060-0.076), head group x1.10 about the chin front, head lowered 17 mm,
   ears x1.2 with an earlier fold and the root ring sunk 15 mm (hidden root ring dropped), necks 4-gon, tail stations cut.
2. Close-ups: side view of the near ear edge-on, same pink as the head (thin blade). -> ear width axis turned towards
   the body axis (flap faces out), ear outside #E48C98 and inside #C9677A for contrast.
3. Preview: tail curl a square wire spiral (76 deg stations). -> 5-gon tube, 54 deg stations, tube 0.040 -> 0.030;
   paid for with a 4-gon hidden Jaw; preview fill 0.56 x 0.70 (Pig framing).
(first delivery 1242 tris; coordinator rework below, budget raised to ~1500)

## Rework (coordinator, 7 items)
R1 legs: body/head/tail raised DZ 0.035 (belly 0.096), legs thicker (apothem 0.047-0.054), knee band 0.074-0.090,
   hoof 0.042 high, hoof #5A3A2C. R2 snout: 14-gon disc, dark wall #DD7D8B + light bevel rim #F9B3B9, round 10-gon
   nostrils (r 0.0165), same protrusion. R3 eyes: 12-gon #4A2C22, x +-0.155, centre 0.06 above the snout centre line
   (was 0.03). R4 ears: x1.25 (0.30 long, 0.22 wide), upright root then forward-down fold, tips at eye level; width
   axis set so both ears show a face in 3/4, front and side views (far ear was an edge-on horn in the preview).
   R5 tail: bold 6-gon spiral 1.2 turns standing up from the rump, curl 0.13 m, tube 0.048 -> 0.034, 3 segments.
   R6 body: 12-sided barrel 0.54 m (1.07x head width), arched back, rounder ellipse rings, facet jitter 4.5% -> 1.5%
   (head 3.5% -> 1.5%) so quads stay planar = larger clean facets. Head x1.15. R7 colour: warm saturated pink in
   3 shades by face (top #F9B3B9, side #F6A4AC, low #F0909B).
Rounds: r5 (all 7 items) -> r6 ears flat wings, boxy barrel, head small -> r7 arched back -> r8 far ear edge-on fixed.
Remaining (nitpicks / owner): head straight (reference turns it to the camera); shadow side still slightly cooler
than the reference because of the shared preview template's blue sky fill; reference ears a little rounder.

## Rework 2 (independent review 2/5: ears broken, eyes buttons, stacked leg rings)
E1 ears: new builder, ONE flap per ear with a fixed width axis (no twist -> no funnel/spike): rises from the skull
   top corner leaning 24 deg forward-out, folds 100 deg about the width axis (tip 33 deg below horizontal over the
   brow); 0.25 m long (0.50 x head width), 0.06 m thick at the root (0.12 x), 0.19 m wide; root sunk 25 mm; inner
   face #CF6A7B; inner-face normal (0.50, -0.87) so both ears show a face from 3/4, front, side, behind, above.
E2 eyes: planar 12-gon discs on the planar front face (front ring widened to 0.39 x 0.33 m), 1.7 mm proud, 13 mm
   deep (< 0.03 x head = 15 mm), x +-0.133. (A disc on the cheek facets had to be 6.5 mm proud to clear a ridge;
   a surface-projected disc was cut by facet ridges - both rejected.)
E3 legs: one 8-gon taper per leg r 0.046 -> 0.053 (1.15x), Upper/Lower meet 0.3 mm inside each other (no visible
   step), no knee band; the only loop is the hoof line (z 0.042, +2%, #5A3A2C).
Rounds r9-r13 (views + close-ups + 128 px); remaining nitpick: reference ears hang a little lower (to eye level).

## Rework 3 (ears) - superseded: hanging flaps out at the cheek read as a cat ear + a plate on the neck in review.

## Rework 4 (ears only): reusable `flap_ear(hinge, out, up, tip, hw, E=EAR_FLAP)` in build_piglet.py
Plain thick triangular flap, one fold: hinge ray-cast on the upper outer skull corner (hidden base ring 0.06 hw
below), rise 0.09 hw leaning 30 deg outward, ONE fold line (113 deg between rise and droop), straight droop 37 deg
below horizontal forward-down to the tip; fixed width axis (no twist); widths 0.40 hw at the hinge -> 0.025 hw blunt
tip; thickness 0.10 hw; inner face #CF6A7B under the fold. Right ear = exact X-mirror of the left points.
World (m): Ear.L hinge (0.154, -0.127, 0.520), fold (0.177, -0.131, 0.560), tip (0.230, -0.267, 0.423) = 0.019
above the eye centre, 0.032 outside the front face edge (front face half width 0.198), in front of the head top.
Checks printed: ear mirror error 0.000000 (pivots 0.000000); from above all ear vertices |x| <= 0.248 (head 0.252),
y -0.272..-0.065 inside the head y -0.281..0.030 (none behind the rear plane); lowest ear point z 0.418 >= eye
centre 0.404. Looked at: 3/4 preview, front, side, behind, above, close-ups, 128 px. Round r20.

## Result
tris 1424 (coordinator limit ~1500): Nose 160, Head 140, Spine1 116, Pelvis 92, Spine2 92, Tail3 92, Ear 80 x2,
Tail2 68, Eye 44 x2, Tail1 44, Upper/Lower/Foot 28 x12, Neck1/Neck2/Jaw 12.
Size: width 0.504 (head) x length 0.786 (snout -> tail) x height 0.620 (ear fold); nose -> rump 0.708, back 0.440,
belly 0.096, head 0.504 w x 0.419 h (top 0.552).
Pivot: root at ground under the volume centroid; parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000 (Tail1-3 excluded: curl plane yawed on purpose),
worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 27 meshes + root, 1424 tris, dims 0.504 x 0.786 x 0.620, texture found in FMS_Piglet.fbm.

## Deviations
- Head width 1.15x back height (reference ~1.3-1.4x measured, inflated by perspective and the head turn).
- Nose -> rump 0.708 (catalogue 0.6): coordinator asked for a body ~1.1x head width; back 0.44 (catalogue 0.4).
- Head straight (pose, not geometry); tail curl plane yawed 35 deg (asymmetric by design, as the Pig).
- Knee band removed in rework 2 (review: legs are single tapered prisms as in the reference).
- No LOD1 (mesh-only round, as Pig/Calf).

## Rig + clips (rig_piglet.py, piglet_clips.py; copied from ../Pig/rig_pig.py + pig_clips.py, read-only pattern)
Skeleton QP (Q without Horn.L/R): 25 bones, Cow names/hierarchy, names_ok, hierarchy_ok, roll_bad []. Bone heads at the
part pivots; Neck2 tail points forward along the head axis (the Head pivot lies behind the Neck2 pivot after the x1.15
head scale; roll rule keeps local X = +X, pitch signs unchanged). Rigid binding: every part weight 1.0 to its bone,
Eye.L/R + Nose -> Head (no two-bone blends needed: bend test showed no holes). Ears bound to Ear.L/R; clips only lift
the ears (negative pitch) because a tip-down rotation pushes the flap into the face (seen in the bend test).
Clips (30 fps, in place, loops closed 0.0 deg): Piglet_Idle 3.0 s (90 f), Piglet_Walk 0.6 s (18 f, T 0.6, duty 0.60,
0.22 m/s, step 0.079 m, lift 14 mm, roll 2 deg, sway 1.5 deg), Piglet_Root 3.0 s (90 f, Neck1 reach (0.04, 0.04) local,
neck pitch 30 deg + head 10 deg, 6 thrusts of 30 mm, front feet 12 mm forward).
Metrics: Idle lowest 0.000; Walk slip 3.29 % of step, stance foot height 0.000, lowest -0.0017; Root lowest -0.0059,
snout lowest z -0.006..0.026; limit violations none. Footstep events in FMS_Piglet.events.json (HindL 0, FrontL 4,
HindR 9, FrontR 14). FBX: 25 bones, 27 meshes, 1424 tris, takes Piglet_Idle 90 / Walk 18 / Root 90 frames, re-import
max vertex error 0.0 m for all takes. Tuning rounds: Walk 4 (slip 5.5 -> 3.3 %, FrontFoot -65 -> within -60),
Root 3 (min total pitch 40 deg so the snout faces down; brace reduced for the hoof limit; thrusts enlarged).
