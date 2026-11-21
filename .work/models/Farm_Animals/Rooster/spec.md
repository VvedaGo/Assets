# BRD-02 Rooster - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-02.png` (1312x1203, front-left three-quarter, yaw ~45 deg from the front,
elevation ~10 deg, rooster faces image-left, near side = rooster's left = +X, both eyes visible).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-02 - red-gold rooster, tall comb, long arched tail 5-7 feathers, 0.55 x 0.55 m,
1000 tris, skeleton B.
Anchors followed: BRD-01 Hen (`../Hen/build_hen.py`, spec, preview): part structure and names, tilted front body rings
(breast flows into the neck, body cap inside Neck1), comb = outline loft (ridge + shrunk flat sides), wattle drops,
ray-cast eyes, diamond-section tail plates, 6-gon legs, toes with a sloped sole (no coplanar sole), Workbench sheet +
EEVEE preview via `_common/animal_render.py` (read-only). House style 11/11b.

## Measured from the reference (ground y~1150 px, comb top y~10 px -> 0.55 m => 0.000482 m/px vertical)
| Feature | px | m (design) |
|---|---|---|
| comb top / head top | y 10 / 150 | 0.55 / 0.48 |
| comb | 4 spikes + rear lobe, ~220 px long | 0.11 long, 0.08 above the head, ~26 mm thick |
| eye centre | y 265 | 0.43, disc ~20 mm |
| beak | y 280-330 | base 0.032 high, tip z 0.39, short, slightly hooked |
| wattles | 2 lobes ~90 x 150 px each | ~0.035 wide x 0.08 high, bottom z 0.32 |
| head width | 195 px | 0.094 (big head, red face) |
| hackle (gold cape) bottom spikes | front y 690, side ~600, back y 545 | z 0.22 front, 0.29 sides, 0.32 back |
| back at the tail base | y 520 | 0.30-0.32 |
| belly bottom / thigh bottom | y 840 / 880 | 0.14 / 0.12 |
| shank width top / ankle | 70 / 50 px | 0.034 / 0.026 (6-gon, chunky) |
| shank visible | y 860-1000 | z 0.13 -> 0.02 |
| toes | front ~0.075, back ~0.035 | 3 front + 1 back |
| tail top / lowest tip | y 150 / 880 | 0.47 / 0.13; 8 sickles visible, rear tip ~0.17 m behind the rump |
Design: length beak tip -> tail tip ~0.56, height 0.55 incl. comb, body width ~0.20 (+ thighs, wings).

## Features (must read at 128 px)
Tall 4-spike chunky red comb; red face + big two-lobe red wattles; yellow-orange two-part beak; dark 8-gon eyes #2A1D17;
gold hackle cape with a jagged spiky lower edge over the upper breast, shoulders and back; red body, darker belly;
layered red-orange wing (upper band / darker lower band / rear tip); long arched tail of 7 chunky diamond-section plates
(2 longest = Tail_Sickle) in dark red / red-orange / gold; big red feathered thighs over thick orange 6-gon shanks;
ankle pad + 3 front toes + back toe.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Rooster on the ground under the centre of mass)
Body, Neck1, Neck2, Head (+ upper beak), Beak_Lower, Comb, Wattle, Hackle (bind later to Neck1/Neck2), Eye.L/.R,
WingUpper/WingLower/WingTip .L/.R, TailFan1 (rump wedge), TailFan2 (5 plates), Tail_Sickle (2 longest, bind to TailFan2),
LegUpper/LegLower/Foot .L/.R. Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Rooster_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Rooster`.
Cells: 0 body #B8352B, 1 body dark #8C2620, 2 wing #D24A2E, 3 wing dark #9E2E26, 4 gold #F2B23C, 5 gold dark #E39A2A,
6 tail dark red #9A2B25, 7 tail red-orange #D9562E, 8 comb #C8473B, 9 head #BC3E33, 10 beak #F4B740, 11 beak dark #E39A2C,
12 leg #F07B2C, 13 leg dark #D9631E, 14 eye #2A1D17, 15 green-black sheen #1F2B26 (spare, variant).

## NOT modelled
ground, individual body feathers, claws, nostrils, ear lobes, eyelids, leg scales, spurs. No armature/weights/clips.

## Deviations from the brief text (reference wins)
- Wings red-orange in two tones (reference), not "dark with gold edges"; tail dark red / red-orange / gold (reference), not
  green-black: the sheen colour is kept as spare cell 15 for a variant.

## Rounds
1. 1322 tris, checks 0 but mirror 1.5 mm (hackle rays on non-planar quads). Worst: tail a flat stack of near-parallel
   plates; hackle a smooth cone with tiny spikes; body too narrow. -> feathers droop (start 86..-10 deg, turn -146..-88),
   wider plates, hackle 16 directions + mirrored half ring, bigger spikes, body +8 % wider, 6-sided hidden neck, 5-sided wattles.
2. Tail still compact, hackle spikes small. -> spikes +16/-9 deg, fan spread.
3. (EEVEE, ref angle) hackle spike tips cut through the convex breast (gold specks below the edge); rump wedge a red block on
   the back; tail ~half the reference projection. -> surface-projected mid ring per spike, rump lower/tapered, plates
   20 % longer and wider (sickle top z 0.47, lowest tips z 0.12), chunkier thighs/shanks/pad.
4. Small body poke through the hackle on the upper breast -> hackle mid offsets 19/21 mm. Views checked: 3/4 ref, side,
   front, back, top, 128 px. Remaining nitpicks: tail fan a little narrower than the reference; upper-wing front cap reads as
   a small block; comb spikes slightly thinner at the tips than the reference; from behind the tail is a 19 mm plate (real).

## Rework v2 (coordinator: flatter, lower, less proud than the reference; budget up to ~1800)
Changes: upright body (rings sliced chest-high -> rump, back slopes to the tail), belly 0.175, visible leg ~0.15 m, neck
rises vertically, head 0.45-0.54, comb 5 thick spikes to 0.645 (+30 %, 32 mm ridge, #D8412F), heart wattles (lobes meet
at the bottom) to z 0.37; Hackle = 4 overlapping rows of pointed gold plates (rows alternate #F0B033 / #F6C54E,
placed by height with normal offsets, mid ring so no plate cuts into the chest, lower rows longer points); wings = 4
projected leaf plates per side (WingUpper 1, WingLower 2, WingTip 1) pointing down/back, #C93A25 / #DD5A2C against
the chest #9A2A1F; tail = 8 thick (22 mm) arched plates, curl increasing to the tip (phi = a0 + turn s^p), peak z 0.620,
Tail_Sickle 3 longest + TailFan2 5; legs #F08A33, thicker shanks, separated toes; legs under the centre of mass.
Palette: cell 15 is now the light gold of the alternating hackle rows (the green-black spare is dropped).
Rounds v2: (1) hackle rows bunched at the chest top -> red windows; (2) rows by height; small windows from chords;
(3) mid ring + more overlap; (4) longer lower-row points. Views: ref 3/4 (EEVEE), side, front, back, top, 128 px.
Remaining: hackle reads as a dense collar, plates less separated than the reference leaves; from behind the tail is a
22 mm plate; comb is 32 mm thick (front view narrow, like the reference).
Result v2: 1734 tris (budget 1800). W 0.274 x L 0.655 x H 0.645 m. Checks all 0, mirror 0.000000, gap 0, lowest z 0.
FBX re-import 1734 tris, same dims, texture found.

## Polish v3 (review 4/5: hackle noisy small triangles; neck/head slightly small)
- Hackle rebuilt: 2 overlapping rows x 8 large leaf wedges (upper row at 0/45/../180 deg, lower row offset 22.5 deg and
  hanging over the breast to z 0.26). Each wedge = closed double pyramid on a 5-point outline (base L/R, shoulders, tip)
  with a raised ridge: 10 tris, 4 visible facets, gold #F0B033 at the base and warm orange-gold #E8992A (cell 15) at the
  tip, underside gold dark. Hackle 464 -> 160 tris.
- Head group (Head + beak, Beak_Lower, Comb, Wattle, eyes) scaled 1.10 about (0, -0.110, 0.470) and lowered 12 mm;
  neck rings +8-10 %, Neck2 top lowered to 0.505 (it poked out behind the bigger-scaled head).
- Result v3: 1430 tris, W 0.274 x L 0.665 x H 0.650 m; checks all 0, mirror 0, gap 0, lowest z 0; FBX re-import 1430 tris,
  same dims, texture found. Views: ref 3/4 (EEVEE), side, front, back, top, 128 px.
- Remaining: the upper-row side wedge at 135 deg reads as a separate spike over the shoulder; small red gaps between
  the lower-row tips on the breast (as in the reference).

## Result v1 (superseded)
1322 tris (target 1000: +32 %; within +15 % of the 1200 upper range). Size W 0.267 x L 0.602 x H 0.556 m (length incl.
the bigger reference tail; catalogue 0.55). Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0, mirror 0.000000,
worst contact gap 0, lowest z 0. FBX re-import: 25 meshes + root, 1322 tris, same dims, texture found.

## Rig + clips (skeleton B, copy of the Hen rig; mesh, part names and pivots unchanged)
Files: `rig_rooster.py` (copy of ../Hen/rig_hen.py: imports, paths, species table ROOSTER) + `rooster_clips.py` (copy of
../Hen/hen_clips.py: toolkit unchanged; clips Idle/Walk/Crow). Run `rig_rooster.py -- BRD-02 bend|anim|export`.
- Bones 20 (no extra bones: the bend test showed no holes at the Hackle or the sickles). Binding: Comb, Wattle, Eye -> Head;
  Hackle -> Neck1 with linear blends to Body (below the Neck1 head, +-40 mm) and Neck2 (above the Neck1 tail, +-50 mm, so
  the upper plates follow the head); Tail_Sickle -> TailFan2 (sways with a phase lag behind TailFan1). 118 blended verts.
- Idle 3.5 s / 105 f: chest out (Body pitch -3), breathing, head turns in 3-frame snaps with holds (yaw to 36 deg), damped
  head-roll wobble after each snap (comb + wattles swing; they have no own bones), tail sickles sway, one wing settle.
- Walk 0.9 s / 27 f: strut 0.22 m/s, step 0.119 m, lift 48 mm, chest out; head bob 0.045 m placed AHEAD of the rest pose
  (the rest neck is nearly straight; a bob behind the rest pose sank the face behind the hackle); Footstep LegL f0, LegR f14.
- Crow 3.0 s / 90 f (loop with a pause): inhale dip, lean back 20 deg, neck back, head up 55 deg, beak open 30 deg with a
  tremor, wings out 16 deg, tail up 10 deg, hold ~1.1 s (f25-58), relax by f76, pause; Vocal event f24.
Metrics: loop closure 0.000 deg / 0.000 m (all); lowest vertex Idle 0.000, Walk -0.0003, Crow 0.000 m; Walk foot slip
0.09 % of the step; joint limit violations 0. FBX re-import: 20 bones, 25 meshes, 1430 tris, 3 takes, vertex error 0.0 m.
Rounds: Idle 1, Crow 2 (stronger lean/head-up), Walk 4 (face sank behind the hackle: bob capped, blend widened, bob moved
ahead of the rest pose). Not verified in Unity (Generic avatar import, takes, events).
