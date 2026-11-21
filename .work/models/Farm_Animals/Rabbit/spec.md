# SML-01 Rabbit - spec (Farm Animals, skeleton Q-S, MESH ONLY: no armature, no weights, no clips)

Reference: `planning/FarmAnimals/references/SML-01.png` (1536x1024). Body seen from the front-left: near front leg ->
near hind leg ~450 px, near -> far front leg ~180 px => body axis ~55 deg off the view axis, camera ~20 deg above.
The HEAD IS TURNED to the camera (eyes symmetric about the nose) - pose, not geometry: modelled straight (as Piglet).
Catalogue: FARM_ANIMALS_PACK.md 5.4 SML-01 - white, long ears, round pom-pom tail, pink nose, 0.45 x 0.30 m, 800 tris
(lead: stay within +15% = 920), skeleton Q-S (short neck, long hind feet).
Anchors followed: Cat (`../Cat/build_cat.py`: Model/loft/tuck, ray-cast eyes/nose/ears, ear dish profile, COM shift,
objects/export/verify/preview), Piglet/Lamb (baby proportions, big head). `_common` and `Tools/blender` imported read-only.
Script: `build_rabbit.py -- SML-01 build|look|export`.

## Measured from the reference (ground 948 px, back top ~450 px -> back 0.30 m => ~0.0006 m/px)
| Feature | px | model (m) |
|---|---|---|
| back top behind the head | ~500 above ground | 0.29-0.30 |
| head top | 680 above ground | 0.415 (head 0.21 w x 0.19 h, nearest to the camera -> perspective-inflated in px) |
| ear tips | 935 above ground | ~0.56 (ears 0.18 long, 0.072 wide, 0.028 thick) |
| eye dia / spacing | 55 / 240 | 0.032 (8-gon), x +-0.058 |
| nose w x h | 80 x 50 | 0.042 x 0.026 inverted triangle |
| leg width | 90-105 | 0.058-0.064 (6-gon, apothem 0.029-0.033) |
| belly above ground | ~130 | 0.08-0.09 |
| tail ball dia | ~190 (further away) | 0.086 |
| nose -> rump | catalogue | ~0.42, ~0.47 with the tail |

## Features (must read at 128 px)
Big round faceted head with chubby lower cheeks, two long upright ears in a slight V (pink inner dish, white rim and
back, 28 mm thick), dark 8-gon eye discs, pink inverted-triangle nose; compact rounded body with a big rump; rounded
haunch bulges (HindUpper) on the flanks; short chunky front legs; long flat hind feet; round faceted pom-pom tail high on
the rump. White in 5 face-assigned shades (top bright, front warm, sides neutral, rear cool, underside grey-warm).

## Material class
Flat palette `T_FarmAnimals_Rabbit_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Rabbit`: 0 top #FBF9F6, 1 side #F2EEEB,
2 front warm #F5ECE6, 3 rear cool #E8E8EE, 4 under #DCD5D4, 5 ear pink #EFA7B2, 6 nose #EC93A3, 7 eye #2A1D17,
8 eye rim (spare) #C9BFC0, 9-15 series spares. Grey variant (5.6) swaps cells 0-4.

## Parts (object `FMS_Rabbit_<Part>`, direct children of empty `FMS_Rabbit`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1, Neck2, Head, Jaw, Ear.L/R, Eye.L/R, Nose, FrontUpper/Lower/Foot.L/R,
HindUpper/Lower/Foot.L/R, Tail1. Q-S: Tail2/Tail3 not needed (the pom-pom is one rigid part on Tail1); necks short and
hidden inside the chest/head; HindUpper = haunch, HindFoot = long foot.

## NOT modelled
whiskers, mouth line, teeth, eyelids/pupils/eye highlights, toes/claws, fur strands, ground, head turn (pose).

## Rounds (Workbench sheet, then EEVEE: reference angle, side, front, back, top, 128 px thumbnail)
1. Head small and high (chin far above the chest); haunches read as stuck-on octagon plates; body boxy; 968 tris.
   -> head group x1.2 about a point behind the crown (grows down/forward), body exponents 2.15/2.1, haunch 3 rings,
   feet 3 rings (888 tris).
2. Body long and lanky, legs thin; head long front-to-back; ears long/narrow; tail ball small and low.
   -> body shorter/wider/deeper (half width 0.118, belly 0.070), legs apothem 0.034-0.038, head rings compressed in Y,
   head x1.28, ears 0.152 (pre-scale) and w 0.034, tail ball r 0.047 raised to 0.262.
3. Dark crease under the chin (chest front too far back); ears too upright/narrow. -> chest front ring forward to
   -0.142 and wider, ears w 0.038 with more V lean. Front close-up: Jaw block showed as a white "teeth" sliver -> raised,
   only its rear end touches the head underside (2 mm, behind the chin).
4. Preview: haunch still a side plate; camera more side-on than the reference. -> haunch axis tilted out/back/down
   (blends into the rump), outer cap r 0.026; preview/ref view (1, -1.25, 0.30) - both eyes visible as in the reference.

## Coordinator rework (7 items, budget raised to ~1100)
R1. Head x1.52 (was 1.28) about (0,-0.12,0.384) -> chin 0.144, top 0.436; cheeks wb +8-20%, section exponents 2.2
    (rounder); small V nose 0.049 x 0.027 + thin grey-pink mouth line (#C4949B, 7 mm wide, 1.5 mm proud, ray-cast ends,
    part of Nose). Eyes 10-gon, apothem 0.019 (dia 0.038), x +-0.094. Ears w 0.040 (0.12 m wide after scale), 0.046 m
    thick, 5 rings with rounded tips, pink dish 76% of the width, dish turned 17 deg towards the 3/4 view.
    Body exponents 2.0 (oval), half width up to 0.128, back 0.304, belly 0.064; seams removed: the joint ring is shared
    exactly by both parts and each part continues one hidden band inwards (scale 0.80, 26 mm) = overlap, no tuck line.
    Haunch dome r 0.088. Legs +30%: front 0.033->0.048 / lower 0.044, feet 0.10 x 0.098 x 0.050; hind lower 0.045,
    hind feet 0.096 x 0.144 x 0.054. Tail ball r 0.062 (dia ~0.124 = ~38% of the head width), 5 rings.
    White shades #F7F2EF / #F4EDE9 / #EEE6E3 / #E5DADA / #D8C8CA by quad normal; pink #F2A6B0 ears, #EE9AA7 nose.
R2. Near ear pink read narrow; tail ball too far behind -> dish 64% -> 76% of width, w 0.037 -> 0.040; tail 12 mm forward.
R3. Preview: near FrontUpper poked out of the chest side as a spike -> top ring r 0.033 and 14 mm inwards.
Remaining (nitpicks): the light chest band under the chin in the front view (chest shows below the big head);
reference ears a touch broader at mid-length; head straight (reference turned).

## Coordinator rework round 3 (independent review 3/5)
(1) Lavender cast -> warm whites, 4 tones by facet direction: top #F8F5F2, front #F4F0EE, side/rear #EEE7E1, under
    #DFD0C7 (warm grey-pink); pinks unchanged.
(2) Boot-like slab feet -> rounded wedge paws: 6-vertex section (flat bottom, domed top), low rounded heel, high instep,
    tapering low toe; front 0.108 w x 0.100 l x 0.052 h (1.1x the leg), hind 0.108 x 0.160 x 0.056 (1.6x the front).
(3) Haunch dome edge / step at the hind leg -> HindUpper is now a thigh column: 8-gon ring inside the pelvis (z 0.205),
    haunch ring r 0.064 bulging out of the lower flank (z 0.138), ring r 0.048 at the hock (z 0.074) over the shin;
    first pass had a stretched (sy 1.18) haunch ring whose back vertex poked out of the narrow rump -> round ring,
    12 mm forward (found by tinting parts pink in check renders, env RABBIT_DBG).
(4) Tail with a flat cut face -> icosphere (1 subdivision, 80 tris), r 0.066 (dia 0.132 = 40% of the head width),
    centre on the rump surface ray + 0.4 r, i.e. 30% of the diameter sunk; spun 90 deg about Z so it is X-symmetric.
Jaw hidden block 6-gon -> 4-gon (-8 tris for the paws).

## Result
tris 1096 (target 800, rework limit ~1100): Pelvis 116, Head 116, Spine2 96, Tail1 80, Spine1 76, Ear 56 x2,
HindFoot 56 x2, FrontFoot 44 x2, HindUpper 44 x2, Nose 20 (nose 8 + mouth line 12), Front/HindLower 20 x4,
FrontUpper 20 x2, Eye 18 x2, Jaw 12, Neck1/Neck2 12.
Size: width 0.331 (head; body 0.243, haunches 0.288) x length 0.519 (nose -> tail ball) x height 0.597 (ear tips);
nose -> rump 0.436, back 0.304, head top 0.436, belly 0.064.
Pivot: root at the ground under the volume centroid (geometry shifted +0.046 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0, min z 0.
FBX re-import: 25 meshes + root, 1096 tris, dims 0.331 x 0.519 x 0.597, texture found in FMS_Rabbit.fbm (256x256).

## Deviations
- Head straight (reference turns it to the camera: pose, not geometry).
- Nose -> rump 0.436, 0.519 with the tail (catalogue 0.45); height 0.597 to the ear tips (reference ~0.56).
- Tail2/Tail3 not built (pom-pom is one rigid part on Tail1, Q-S variant).
- Hind feet long (0.160) per the Q-S brief and round 3; haunch as a thigh column (brief + round 3).
- tris 1096 = +37% over the catalogue 800 (coordinator raised the limit to ~1100 for the rework).

## Rig + clips (skeleton Q-S, rig_rabbit.py / rabbit_clips.py)
24 bones: Q without Horn.L/R, Tail2, Tail3, plus Nose (child of Head: nose + mouth line twitch). Bone heads = part
pivots; every part weight 1.0 on its own bone (Eye.L/R -> Head). Bend test (8 extreme poses): no holes, so no 2-bone blends.
Rabbit limits: FrontUpper x -115..60 / z +-30, FrontFoot x -150..120 (nibble paws), HindUpper x -70..75, Nose +-12, Ear y +-50.
Feet: leg_ik keeps only the pitch; foot_flat() sets the world orientation (else the leg abduction rolls the wide paws into the ground).
Idle 3.0 s (90 f): 3 breaths, head turn +-4 deg, 3 nose-twitch bursts (5 Hz), ears independent (flick, tilt back, swivel), tail wiggle.
Hop 0.6 s (18 f): front off f3, takeoff f5, airborne f6-10 (peak 0.10 m, feet 8.3 cm up at f9), front land f11, hind land f13;
  ears lag (blown back, flop forward/out), in place. Nibble 2.0 s (60 f): sits back (chest up 18 deg), head dips, front paws
  raised to the chin by FK (grid search), Jaw chews 12x (6 Hz), nose twitch, ears relaxed back/out.
Metrics: loop closure 0.000 deg (all), lowest vertex Idle -1.5 / Hop -0.5 / Nibble +0.3 mm (limit -2 mm = pack -1 cm scaled
  to 0.45 m), 0 joint-limit violations. FBX re-import: 24 bones, 25 meshes, 1096 tris, 3 takes, vertex error 0.0 m.
