# BRD-04 Duck (mallard drake) - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-04.png` (1312x1199, front-left three-quarter, yaw ~45 deg from the front,
elevation ~10 deg, duck faces image-left, near side = duck's left = +X, both eyes visible).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-04 - grey-brown, green drake head, orange flat bill, webbed feet, 0.50 x 0.35 m,
800 tris, skeleton B. Lead brief: ~800 tris (max +15 % = 920), eyes #2A1D17, bill = flat spatula with a dark nostril cell,
webbed feet 6-8 mm thick, white neck ring, short upturned tail with a dark curl.
Anchors followed: BRD-01 Hen (`../Hen/build_hen.py`, spec, preview) and BRD-02 Rooster: part names, tilted front body rings
(breast flows into the neck, body cap inside Neck1), Neck2 flush into the back of the head, ray-cast eyes and wing tiers,
6-gon legs, Workbench check sheet + EEVEE preview via `_common/animal_render.py` (read-only). House style 11/11b.

## Measured from the reference (ground y~1085 px, head top y~18 px; vertical 0.000375 m/px, horizontal along the body
~0.0004 m/px after the 45 deg yaw)
| Feature | px | m (design) |
|---|---|---|
| head top / eye centre | y 18 / 168 | 0.400 / 0.345 |
| eye disc | ~40 px | 0.017 (8-gon, 4 mm proud) |
| head width | 315 px (near, perspective) | 0.100 |
| bill | base y 215-290, tip y 340, tip width ~90 px | 0.077 long from the face, 0.036-0.039 wide, 0.030 high at the base, 0.008 at the tip |
| neck ring (cream) | y 425-470 | z 0.218-0.240 at the front |
| neck width at the ring | 240 px | 0.084 |
| back top | y 380 | 0.262 |
| chest front (widest) | y 600 | z 0.18 |
| belly bottom | y 870 | 0.078 |
| leg width | 55-60 px | 0.024 (6-gon), exposed z 0.078 -> 0.008 |
| foot | 255 px along the diagonal | 0.09 (heel 0.014 + middle toe 0.074), 7 mm web edge, 13-18 mm ridges |
| wing | x 520-1090, y 380-740 | y -0.09..0.21, z 0.13-0.256; speculum white/blue/white at z 0.15-0.19, rear half |
| tail | cream point tip x 1150 y 600; dark rump under it | tip y +0.255, z 0.215 (upturned) |

## Size decision (conflict)
Reference proportions are height/length ~0.8; the catalogue says 0.50 x 0.35 (0.7). Kept length 0.50 (bill tip -> tail tip)
and the reference proportions -> height ~0.40. Constraint dropped: catalogue height 0.35 (reference wins, skill 11b.10).

## Features (must read at 128 px)
Big round green head (#6E9F4A) on a thick green neck with a cream ring at its base; dark 8-gon disc eyes; flat broad orange
spatula bill with darker lower bill and two dark nostril cells; chestnut-brown chest; plump grey-brown body; folded wing in
three bands: light coverts / darker lower band with the white-blue-white speculum / dark brown tip; dark rump wedge with
a cream pointed upturned tail and a small dark curl on top; two thick orange 6-gon legs; flat triangular 3-toe webbed feet.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Duck on the ground under the centre of mass)
Body, Neck1 (cream ring + green), Neck2, Head (+ upper bill), Beak_Lower, Eye.L/.R, WingUpper/WingLower/WingTip .L/.R,
TailFan1 (dark rump wedge), TailFan2 (cream tail point + dark curl), LegUpper/LegLower/Foot .L/.R. Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Duck_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Duck`.
Cells: 0 body #968679, 1 belly #74665D, 2 chest #7C4E3F, 3 chest dark / nostril #4E3128, 4 head #6E9F4A, 5 head dark
#5B8A3D, 6 cream #EEE6D3, 7 wing #AC9E92, 8 wing lower #85766C, 9 wing tip / rump #5A4B44, 10 speculum #4B5277,
11 bill #F28C38, 12 bill dark #CF6420, 13 leg #F08A36, 14 eye #2A1D17, 15 tail curl #3B302C.

## NOT modelled
ground, water, individual body feathers, claws, toe scales, eyelids, ear openings, tongue. No armature/weights/clips.

## Rounds
1. 974 tris, mirror 10.9 mm (right-foot side axis sign bug). Worst: head small and high on a thin neck (reference: big
   head ~0.12 m on a thick neck); dark curl a thin antenna spike; body/tail long behind. -> head 0.118 wide x 0.124 high,
   neck +20 %, bigger bill (0.044 wide), body 9 rings and shorter rear, chunky 3-ring curl, thicker legs, 4-point wing tip,
   WingLower 6 rings, foot axis fixed (894 tris, mirror 0).
2. (EEVEE at the reference angle) brown chest ran far back along the side with a dark patch at the shoulder; speculum low;
   cream tail point hidden; feet small; cream ring 30+ mm. -> chest by position + facing, wing tiers moved up/forward,
   feet +13 %, tail point bigger, ring top 0.234.
3. Chest still wrapped the near side. -> chest = forward-facing faces only (bib), wing fronts at y -0.118 / -0.092.
4. Concave fold beside the neck -> front body ring (inside Neck1) widened 32 -> 46 mm. Views checked: 3/4 ref, side,
   front, back, top, 128 px.
Remaining nitpicks: a forward-facing brown chest facet at the shoulder still reads darker than the reference; the upper
wing front reads as a small faceted block; the curl is visible mainly from the side/back (reference shows none); the wing
is a little more boxy/layered than the reference's smooth single patch.

## Deviations
- Height 0.402 m vs catalogue 0.35 (reference proportions kept, length 0.506 m bill tip -> tail tip).
- Dark curl added on the tail (lead brief); the reference shows only a dark rump and a cream point.
- Nostrils = two dark shoulder cells on the upper bill (reference shows none; lead brief asks for them).
- TailFan1 = dark rump wedge, TailFan2 = cream point + curl.

## Rig + clips (rig_duck.py, duck_clips.py, swim_gif.py)
Copied from the Hen rig (read-only): skeleton B, 20 bones (Root, Body, Neck1, Neck2, Head, Beak_Lower, WingUpper/WingLower/
WingTip .L/.R, TailFan1, TailFan2, LegUpper/LegLower/Foot .L/.R); Eye.L/.R bound to Head, other parts rigid on their own
bone, linear blends at Body-Neck1-Neck2-Head (14 verts). Mesh, part names and pivots unchanged.
Clips (30 fps, in place, loops closed 0.000 deg / 0.000 m):
- Duck_Idle 3.5 s (105 f): 3 breaths, smooth 8-frame head turns (+-35 deg), bill dip 28 deg at 64-79 % with the lower bill
  opening 12 deg, two tail-wag bursts. Lowest vertex 0.0.
- Duck_Walk 0.9 s (27 f): waddle roll 9 deg + sway 8 mm, step 0.054 m at 0.10 m/s, lift 26 mm, toe curl 12 deg, small head
  bob, tail wag. Foot slip 0.97 % of the step, lowest -1.5 mm, Footstep events (FMS_Duck.events.json).
- Duck_Swim 2.0 s (60 f): body bob 3 mm, pitch 1.5 / roll 2 deg, 2 paddle strokes per leg alternating (power stroke back,
  toes 20 deg down; recovery forward raised, toes 55 deg), neck up 4 deg with a 2 deg bob, tail wag; Paddle events.
  Feet stay above z -6 mm. Water line for Unity: water surface 0.18 m above the root (place the root 0.18 m below it).
Rounds: 1) walk toes dipped 15 mm (toe curl 25 / lift 20 mm) and the swim knee folded to 153 deg (> 150 limit) -> step
0.054, lift 26, curl 12; paddle targets lower/back. 2) all metrics pass, limits 0 violations.
Swim GIF: swim_gif.py runs the shared anim_gif.py functions (file not edited) with a translucent water disc at 0.18 m.
