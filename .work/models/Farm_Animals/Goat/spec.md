# LIV-08 Goat - spec (Farm Animals, skeleton Q, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/LIV-08.png` (1536x1024): front-left three-quarter, ~14 deg above, chest
towards the camera; the head looks at the camera.
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-08: white with beige markings, horns curving back, beard, ears sideways,
1.1 x 0.8 m, 1700 tris (lead: stay within +15% = 1955), skeleton Q.
Anchors followed: Calf (`../Calf/build_calf.py`: part Model/loft/tuck, patch field with wobble + contour snap, objects(),
coplanar_all, check sheet), Sheep (ear leaf with a coloured inner face, dark/light split), Cow (horn = sunk tapered tube
with a darker tip), Horse (hind leg slanting back to the hock, cannon forward to the hoof). Preview: `_common/animal_render.preview`
(read-only). Script: `build_goat.py -- LIV-08 build|look|export`.

## Measured from the reference (ground ~975 px, back top ~365 px -> 0.80 m, ~0.0013 m/px; head nearer the camera)
| Feature | px | model (m) |
|---|---|---|
| back top | 610 above ground | 0.805 |
| belly | ~275 above ground | 0.30 (lowered from 0.345 in round 3: reference body reads deep) |
| poll / horn tops | ~845 / ~945 | 1.07 / 1.20 |
| nose / beard tip | ~620 / ~390 | 0.73 / 0.48 |
| head width at the eyes | 225 | 0.37 (incl. head x1.26 style scale) |
| ear length | ~190 | 0.23 per ear, span 0.81 m |
| eye diameter | ~45 | 0.065 (8-gon, 5 mm proud) |
| lower leg / hoof width, hoof height | 80 / 105, 60 | 0.11 / 0.13, 0.074 |
| knee / hock height | ~830 / ~790 | 0.235 / 0.255 |
| tail | ~190 tall | 0.27 above the rump root, 0.11 deep at the base |

## Features
White faceted barrel (14 sides x 13 rings) with a tan saddle over the back, a shoulder drape and a hip drape (ellipsoid
field + low-frequency wobble, 40 vertices snapped onto the contour, quads split along it -> rounded edges, no stair steps;
|x| field -> exact mirror). Thick neck with a beige throat so the bright beard reads. Big head (10-sided superellipse loft,
58 deg down, head group x1.26): bright blaze face, cream cheeks, dark 8-gon eyes on the head sides looking sideways-forward,
pink inverted-triangle nose pad, white chin block, long leaf ears sideways (white top/rim, tan inner face, cream back),
6-sided horns rising from the poll, curving back and outward, darker tip third. Chunky tapered beard (Beard, bind to Jaw).
Legs 6-sided: forearm/thigh flared into the body, proud cream knee/hock band, hind leg with a clear hock bend, dark
flared hooves. Upright pointed leaf tail Tail1-3.

## Material class
Flat palette `T_FarmAnimals_Goat_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Goat`: 0 white #F3EBDF, 1 cream #E3D6C5,
2 tan #D6B593, 3 throat #D5C4AC, 4 blaze/beard #FAF5EC, 5 horn #C9A685, 6 horn tip #86664B, 7 nose #D9A592, 8 eye #2A1D17,
9 hoof #3A2E28, 10 ear inner #B48D6C, 11 ear back #D6C8B3, 12-15 series spares. Brown variant: swap cells 0-3.

## Parts (object `FMS_Goat_<Part>`, direct children of empty `FMS_Goat`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Horn.L/R, Eye.L/R, Nose, Beard, Front/Hind Upper/Lower/Foot .L/.R,
Tail1-3. Joints overlap by tuck rings (body, neck, tail) or sunk ends (legs, ears, horns, eyes, beard).

## NOT modelled
rectangular pupils, mouth line, teeth/tongue, eyelids, udder, collar/bell, hair strands, ground; head turned to the camera.

## Rounds
1. (Workbench) legs long and thin, body slim, head narrow, horns spindly and too tall, beard small. -> body x1.13, legs
   x1.12, neck +20%, head x1.22, horns thicker/shorter, beard larger.
2. (EEVEE multi-view: reference angle, preview, side, back, front, top) legs still thin, head long and pointed, ears
   droop and look all tan, knee bands look like bandages. -> legs x1.32 below the body, hooves x1.18, head wider, eyes
   larger and more forward, ears flatter.
3. Body shallow, head long, beard invisible against the white chest, ears tan from every side. -> belly 0.30, head
   shorter (0.27) x1.26, ear leaf tilted so the white top/rim shows and only the inner face is tan, bands cream.
4. Beard still white on white, tail a thin spike, hock bend weak. -> beige throat cell, tail wider (leaf), hock 1 cm
   further back, saddle and shoulder drape larger. Accepted.
Remaining (nitpicks): the reference head is turned to the camera (ours straight, rig rest pose); the reference has a
little more tan low on the mid flank; knee bands are slightly more visible than in the reference.

## Rework round 2 (coordinator review 3/5)
1. Knee rings removed: each leg = one 8-sided tapered prism (Upper + Lower tucked, same radius at the joint, no band),
   visible top 0.064 -> bottom 0.056 (x1.14), dark hoof cap only; hind leg keeps the hock bend without a band.
2. Nose: small pink inverted triangle lying on the flat muzzle cap, 1.5 mm proud, fully inside the cap outline (no plate).
3. Horns: exact mirror (mirror 0, tops L = R = 1.238 m), thick root 0.046 x1.26, sunk 3.2 cm, up -> back, outward drift
   reduced to 0.09; tip 0.17 m above the poll (0.45 x vertical head height 0.377, 0.68 x head section height 0.25);
   preview camera made more frontal (0.68, -1, 0.20) so the far horn is not hidden behind the near one.
4. Beard: cream wedge (own cell 12 #EFE3CD), 0.135 m below the jaw = 0.40 x head length 0.34; head moved 2.5 cm forward
   and the neck front 2 cm back so the beard hangs in front of the throat.
5. Barrel half-width factor 1.18 -> 1.30 (+10%: body width 0.47 -> 0.52 m); legs x 0.13 -> 0.14, drapes follow.

## Result (round 1, superseded by the rework numbers below)
tris 1660 (target 1700, -2%). Size: width 0.810 (ears) x length 1.201 (nose -> tail) x height 1.198 (horn tips);
back 0.805, belly 0.301, poll 1.067. Pivot: root on the ground under the volume centroid (geometry shifted +0.077 m in Y).
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 30 meshes + root empty, 1660 tris, dims 0.810 x 1.201 x 1.198, texture found in FMS_Goat.fbm.

## Result after rework
tris 1740 (target 1700, +2.4%): Pelvis 136, Spine1 164, Spine2 164, Neck1 44, Neck2 60, Head 116, Jaw 44, Ear 44 x2,
Horn 80 x2, Eye 28 x2, Nose 8, Beard 44, FrontUpper 44 x2, HindUpper 60 x2, Lower 44 x4, Foot 44 x4, Tail1 20, Tail2 32,
Tail3 44. Size 0.810 (ears) x 1.232 (nose -> tail) x 1.238 (horns); back 0.805, belly 0.301, poll 1.067.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000, worst gap 0, min z 0.
FBX re-import: 30 meshes + root, 1740 tris, dims 0.810 x 1.232 x 1.238, texture found in FMS_Goat.fbm.

## Deviations
- nose -> tail 1.23 m vs 1.1 catalogue (+12%): reference body proportions + upright tail.
- head straight (reference turns it to the camera).
- No LOD1 (mesh-only round, like the other animals).

## Rig + clips (rig_goat.py, goat_clips.py; mesh unchanged)
Skeleton Q (Cow's 27 bones incl. Horn.L/R, Tail1-3) + Beard (child of Jaw) = 28 bones, heads on the part pivots. Parts kept
as 30 skinned objects (names unchanged), each bound 1.0 to its bone (Eye.L/R, Nose -> Head). Two-bone blends where the bend
test opened gaps: knee/hock line 50/50 Upper/Lower (Lower tuck ring -> Upper, bottom ring in the hoof -> Foot), neck
continuous along the path Spine2|Neck1 50/50 -> Neck1|Neck2 50/50 -> Neck2|Head 20/80 (120 blended vertices).
Leg IK with rest offsets (Horse copy): the hind hock rests 24 deg flexed; goat-local limit HindLower.x (-170, 24) (+24 = straight).
Clips (30 fps, in place): Goat_Idle 3.5 s, Goat_Walk 0.9 s (lateral sequence, step 0.216 m, 0.40 m/s, lift 6 cm,
Footstep events), Goat_Browse 4.0 s (neck pitch -30 split 16.5/13.5 + Neck1 stretch 3 cm keyed along the neck, head -30,
nose 1.09-1.20 m vs poll 1.07, 2 bites with a tug + 4 chews each, beard counter-rotated 57 deg to keep hanging).
Rounds: 1 hind foot 5 cm high in stance (collinear-leg IK) -> rest-offset IK; 2 jaw flap too big -> bite 12, chew 7 deg;
3 beard pointed forward with the head up -> gravity counter-rotation.
