# PET-02 Cat - spec (Farm Animals, skeleton Q, MESH ONLY this round)

Reference: `planning/FarmAnimals/references/PET-02.png` (1536x1024, left side from the front-left, ~45 deg azimuth, ~15 deg above).
Catalogue: FARM_ANIMALS_PACK.md 5.3 PET-02 - orange tabby, raised tail, pointed ears, white chest, 0.5 x 0.30 m, 1300 tris, Q.
Anchors followed: pilot Cow (`../Cow/build_cow.py`: ring lofts, superellipse sections, palette by face, eye ray-cast, EEVEE
preview via `_common/animal_render.preview`), Farm Processing house style (flat 4x4 palette, faceted, chunky).
Script: `build_cat.py -- PET-02 build|look|export` (look = EEVEE frames from the reference angle into %TEMP%).

## Measured from the reference (relative, ratios from the 3/4 view; perspective makes absolute px->m approximate)
| Feature | ratio in ref | model (m) |
|---|---|---|
| back height | catalogue | 0.300 |
| body depth / total height (to ear tips) | 0.36 | 0.185 / 0.475 |
| legs (belly->ground) / total height | 0.32 | 0.115 |
| leg width / total height | 0.11 | upper 0.072, lower 0.058 (8-gon) |
| paw width / total height | 0.14 | 0.072 x 0.086, 0.042 high, dark sole 7 mm |
| head height / body depth | ~0.85 | 0.163 (incl. scale 1.15) |
| eye diameter / head height | 0.24 | 0.033 |
| tail thickness | ~0.45 x leg | 0.051 -> 0.043, length 0.25, tip hooks forward |

## Features
faceted barrel body (10 sides) with cream belly strip and big cream bib; 4 bold slanted tabby stripes per flank + shoulder
stripe, ends pointed (one triangle); round faceted head with cream muzzle/cheeks/chin, pink inverted-triangle nose, dark
8-gon eye discs 3 mm proud, temple/cheek/crown stripes as pointed triangles; thick triangular ears with pink inner dish and
orange rim; 8-sided legs with a stripe band at the knee (joint band) and one mid-lower stripe; cream paws with dark soles;
raised tail with 4 stripe rings and an orange rounded tip.
Stripes: per-face palette cells on the lofted grid (the body rings are slanted so stripe edges follow the facets - no
stair-steps); no raised plates needed.

## Material class
Flat palette, `T_FarmAnimals_Cat_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Cat`. Cells: 0 orange #F0913A, 1 orange shade
(spare), 2 stripe #C45A1C, 3 stripe dark (spare), 4 cream #F6DFB8, 5 cream shade (spare), 6 ear pink #EE9E8A, 7 nose #E3837C,
8 eye #2A1D17, 9 sole #3A2E28, 10-15 series spares. Variants (black/grey/white) swap cells 0-4 only.

## Parts (skeleton Q names; object `FMS_Cat_<Part>`, direct children of empty `FMS_Cat`, pivot = joint / bone head)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, FrontUpper/Lower/Foot.L/R, HindUpper/Lower/Foot.L/R,
Tail1-3. Joints: child's proximal end = one 0.965-scale ring 12-20 mm inside the parent's capped end (body, neck, tail); leg tops sunk into the body, lower legs start inside the upper leg (knee step),
lower legs end inside the paws. No bones, no weights.

## NOT modelled
whiskers, collar, teeth/tongue, eyelids/pupils, claws/toes, fur strands, ground.

## Rounds
1. Body too long/narrow, head small, thin barcode stripes, spiky ears, thin tail, 1880 tris -> body 0.34 m and wider, 4 bold
   stripes, wider ears, tail +15%, fewer rings (1660 tris).
2. (EEVEE) legs ~1.3x too thin and paws small, body too shallow -> legs/paws +30%, belly 2 cm lower.
3. Head group too small -> Head/Jaw/Ears/Eyes/Nose scaled 1.15 about the neck joint.
4. Face stripes hidden behind the ears, ears narrow -> temple/cheek/forehead marks as pointed triangles, wider shorter ears.
5. (preview) hind thigh tops boxed out of the flank -> thigh tapers into the body; rump end rounder.
Polish pass (coordinator list):
6. rump domed (rear rings 0.166/0.177/0.183, w 0.072->0.034); belly cream stops before the rump (was visible under the tail).
7. left/right flank stripe tables differ (L bands 4,6,9,11,13 / R bands 3,6,8,10,12, different lengths); mesh mirror 0.
8. front upper legs taper from 0.022 to 0.035 into the chest; their front faces under the bib are cream -> no step.
9. ears wider (base half 0.049 -> 0.056 after scale), upright, facing forward, sunk 11 mm; pink dish with orange rim.
10. eyes 8-gon apothem 0.0143 (was 0.0167), 2 mm proud, flat cone discs (14 tris each).
11. tris 1660 -> 1448: one hidden overlap ring per joint instead of two (body, neck, tail), 6-sided neck, 2-band jaw,
    2-band lower legs, shorter tail tip, cone eyes.
12. side/back/right views checked; throat/under-chin faces cream (no orange sliver), head cream on muzzle + lower cheeks.
Remaining notes: a contact shadow line shows in the head/chest crease (geometry, not colour); stripes are on the ring
grid, so they are straighter than the hand-painted reference stripes.

## Deviations
- tris 1448 vs ~1300 target (+11%): separate closed parts (end caps kept for 0 non-manifold) and stripe bands on legs/tail.
- length 0.518 m incl. tail (nose->rump 0.451), height 0.478 m to ear tips (back 0.300), width 0.221 m (ears; body 0.18).
- pivot: root at the ground under the volume centroid (geometry shifted +0.026 m in Y); centroid counts overlapping parts twice (approx.).

## Rig + clips (rig_cat.py, cat_clips.py; pattern ../Dog, lying pose idea ../Calf)
Skeleton Q without Horn.L/R: 25 bones (Root, Pelvis, Spine1-2, Neck1-2, Head, Jaw, Ear.L/R, 4 x Upper/Lower/Foot, Tail1-3),
heads on the part pivots; Eye.L/R and Nose -> Head. Weights 1.0 per part plus blends: spine path Pelvis|Spine1|Spine2,
neck path (Dog copy), tail path Tail1|2|3, knee line 50/50 (+-6 mm), upper-leg tops above the hip/shoulder 70/30 with the
body bone (folded thigh stays in the flank). 235 blended vertices. Bend test incl. 10 deg spine undulation: no holes.
Legs rest straight -> shared leg_ik (no rest-offset IK needed). Cat limits: Tail1 x down to -105 (tail lies flat),
FrontFoot x down to -70 (paw stays flat at push-off).
Clips (30 fps, in place): Cat_Idle 3.5 s (tail S-wave x2, breathing, head turn, 3 ear twitches), Cat_Walk 0.8 s
(lateral sequence, 0.36 m/s, step 0.179 m, paws at 80% track width, spine yaw +-3 deg), Cat_Lie_Idle 4.0 s (loaf: belly
on the ground, front legs folded under the chest, hind legs folded forward beside the belly, tail curled on the ground
round the left rear flank; breathing, head drift, ear twitches, tail-tip flicks).
Known: thin dark sole edges show at the folded paws in Lie_Idle; the folded thigh top still shows a small seam on the flank.
