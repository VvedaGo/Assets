# BRD-06 Duckling - spec (Farm Animals extension, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-06.png` (1312x1199, front-left three-quarter, duckling yawed ~30 deg towards
its own right, so we see the face and its left (+X) side, tail nub on the image right; ~10 deg above). The bill points
further left than the head yaw explains (head slightly turned / close camera); we model a straight head (symmetric for the rig).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-06 - yellow, big bill, 0.18 x 0.15 m, 350 tris, skeleton B.
Lead brief: oversized head, broad oversized flat orange bill, two very short orange webbed legs, compact round body, tiny
tail, stub wings, dark disc eyes #2A1D17, ~350 tris (limit +20 % = 420), clearly a duckling, not a recoloured chick.
Anchors followed: BRD-03 Chick (`../Chick/build_chick.py`: geodesic-like faceted balls, Neck frustum in the crease, ray-cast
eyes, lens wings, COM pivot, check sheet + EEVEE preview via `_common/animal_render.py` read-only) and BRD-04 Duck
(`../Duck/build_duck.py`: 5-point spatula upper bill in Head + 4-point lower bill 1 mm below the mouth line, fan-topped
concave webbed foot with a sloped rim). House style 11/11b.

## Measured from the reference (feet y 1125 px, head top y 75 px -> 0.150 m => 0.000143 m/px)
| Feature | px | m (design) |
|---|---|---|
| head width / height above the body | 725 / 575 | 0.106 / ~0.085 (ellipsoid 0.053 x 0.046 x 0.046, centre z 0.104) |
| head centre ahead of body centre | ~85 px at the yaw | 0.024 |
| body width / height | 660 (diag.) / 420 | 0.084 / 0.064 (ellipsoid 0.042 x 0.048 x 0.032, centre z 0.048) |
| belly bottom | y 1010 | 0.016 |
| eye centre / diameter / spacing | y 365 / 80 / 335 | z 0.111 / 0.013 (8-gon, 2 mm proud) / x +-0.027 |
| bill (upper+lower) | x 213-765, y 370-590 | 0.045 out of the face, 0.043 wide at mid, top 0.104 -> 0.089 at the tip, 0.006 lower bill |
| leg visible / width | 85 / 65 | 0.012 / 0.010 (6-gon, apothem 5.0/4.6 mm) |
| legs apart | 248 | x +-0.017 |
| foot | 245 diag, ~25 rim | 0.031 long incl. heel, 0.030 wide at the toes, rim 3.5-4.5 mm, ankle 8.5 mm |
| wing | x 770-1010, y 650-860 | y 0.00..0.05, z 0.036-0.067, rear tip raised, 5-7 mm proud |
| tail nub | tip x 1040 y 620 | tip z 0.074, 0.02 out of the rump, up-back ~40 deg, flat pointed wedge |

## Features (must read at 128 px)
Big faceted yellow head (geodesic-like staggered rings, pentagon top cap, no pole fans) on a smaller round body with a soft
crease (Neck fills it, no ledge); broad flat orange spatula bill much wider than a chick beak (upper light orange, lower dark
orange); large dark 8-gon eyes; stub wings; tiny pointed tail; very short orange 6-gon legs; flat triangular webbed feet
with 3 toe tips.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Duckling on the ground under the centre of mass)
Body, Neck (single part, binds to Neck1/Neck2 later), Head (+ upper bill), Beak_Lower, Eye.L/.R, WingUpper.L/.R (shoulder
root), WingLower.L/.R (stub incl. tip; WingTip merged), TailFan1 (nub), LegUpper.L/.R (hidden thigh inside the body),
LegLower.L/.R, Foot.L/.R (webbed).

## Material class
Flat palette, own atlas `T_FarmAnimals_Duckling_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Duckling`.
0 body #F4C845, 1 body dark (belly underside) #E2B13A, 2 body light (spare), 3 wing #EDBA3C, 4 wing dark (spare),
5 bill #F68A2E, 6 bill dark #D8651E, 7 leg #F2862C, 8 foot rim #D8651E, 9 eye #2A1D17, 10-15 series spares.

## NOT modelled
ground, down fluff, nostrils, eyelids, claws, leg scales, back toe, ground shadow. No armature/weights/clips.

## Rounds (Workbench sheet: ref + ref view, side, front, back, rear 3/4, top, high front; EEVEE at ref and preview views; 128 px)
1. 420 tris, all checks 0. Worst: bill a long thin plank (0.04 out, 6 mm tip); body small so the Neck read as a collar;
   tail a long spike and the wing front a blunt lump. -> bill shorter (tip y -0.092), wider (half 0.025 mid), thicker
   (upper 10 mm at the tip, lower 5-8 mm); body radii 0.045/0.050/0.034; tail shorter; wing front tucked.
2. (EEVEE) sawtooth dark line under the upper bill; wing crumpled where WingUpper poked through WingLower. -> lower bill
   top buried 2.5 mm inside the upper bill (no near-coplanar mouth faces), WingUpper tucked inside WingLower; sawtooth
   remained = EEVEE filtered sun shadow at 4 cm scale -> local copy of the shared preview with sun shadow jitter + 128
   samples (shared module untouched).
3. Lower bill too close in colour to the upper, wing lost in the body. -> bill dark #C5561A, wing #E9B036. Exported.
Remaining nitpicks: the wing lobe still reads slightly faceted/busy on the shadow side (reference: one smooth lobe); head a
little taller/egg-shaped vs the reference's rounder cheeks; bill points straight ahead (reference head is turned left).

## Result
420 tris (target 350, +20 %, limit 420): Head 104 (incl. upper bill 26), Body 76, Foot 30 x2, Neck 28, LegLower 20 x2,
Eye 14 x2, WingLower 14 x2, Beak_Lower 12, TailFan1 12, LegUpper 8 x2, WingUpper 8 x2.
Size W 0.105 x L 0.159 (bill tip -> tail tip) x H 0.147 m; visible leg ~17 mm incl. foot, leg 10/9.2 mm thick (6-gon).
Pivot: root on the ground under the volume centroid (geometry shifted +0.0066 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000, worst contact gap 0, lowest z 0.
FBX re-import: 17 meshes + root, 420 tris, dims 0.105 x 0.159 x 0.147, texture found in FMS_Duckling.fbm.

## Deviations
- Length 0.159 m vs catalogue 0.18 (reference proportions: round head + short broad bill; a longer bill read as a plank).
- Head modelled straight (symmetric for the rig); the reference head is turned slightly to its right.
- Stub wings and a hidden 3-gon LegUpper added for skeleton B; WingTip merged into WingLower; single Neck part.
- Eyes 13 mm (reference ~12 mm), 1.2-2.9 mm proud of the facets.

## Rig / animation (rig_duckling.py + duckling_clips.py + swim_gif.py; mesh unchanged)
- Copied from ../Chick (same part list: 16 bones, ONE Neck, WingLower incl. tip, TailFan1) with the Duck clip set
  (waddle walk, Swim) ported to one neck. Chain-end tails measured from the mesh (bill tip, wing tip, tail tip).
  Eye.L/R -> Head; Neck blends 50/50 with Body (+-6 mm) and Head (+-4 mm), 8 blended vertices. Leg limits restored
  (the Chick table had LegLower/Foot inside a comment).
- Duckling_Idle 3.0 s / 90 f (4 breaths, head turns in 3-frame snaps, one bill dip at 0.66-0.80 with the lower bill open
  14 deg, 2 wing flutters, tail wag). Duckling_Walk 16 f (0.533 s; 0.05 m/s, step 0.015 m, lift 6 mm, waddle roll 8 deg
  + sway 2.5 mm, head bob, tail wag; Footstep events). Duckling_Swim 1.6 s / 48 f (bob 1.2 mm, rock, 2 paddle strokes per
  leg; Paddle events). Swim legs by FK (the hidden thigh is 6 mm: IK flipped it to -138 deg in round 1); the web is kept
  >= -1.5 mm (bisection towards flat).
- Metrics: closure 0.0 deg / 0.0 m all; lowest vertex 0.0 / -0.7 / -1.5 mm (tolerance -2 mm = the -1 cm rule scaled, as
  the Chick); walk slip 0.53 % of the step; limit violations 0.
- Water for Unity: surface 0.050 m above the root. GIF: swim_gif.py (copy of ../Duck/swim_gif.py, water 0.050, floor -0.06).
- FBX: 17 skinned parts + Rig (16 bones), takes 91 / 17 / 49 f, 420 tris, re-import vertex error 0.0 m, texture found.
