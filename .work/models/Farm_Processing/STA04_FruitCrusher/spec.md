# STA-04 Fruit crusher - FMS_Workshop_STA_04

## Accepted-model roller polish (2026-11-14; supersedes earlier roller results)
- Scope: two 12-sided cylinders with front vertices rather than broad flat front faces; radius 75.8 mm,
  end-to-end barrel length 550 mm, 17 mm beige end chamfers and integrated dark metal hub discs at both ends.
  Hub faces/bevels share mesh rings with the barrels (no overlapping coplanar caps); hubs are visible in the window.
- Frontmost barrel y = -0.260, exactly 20 mm proud of housing front y = -0.240.
  Axles move forward 9.23 mm to y = -0.1842; bearing bosses/caps and crank follow the same axis.
  Accepted housing, hopper, stand, chute geometry, palette and preview camera are preserved.
- Separate root children Roller_A / Roller_B retain X axle pivots at (0, -0.1842, 0.8754) and
  (0, -0.1842, 0.7108); crank pivot (-0.4, -0.1842, 0.8754), root ground identity.
- Tris 2016 -> 2240: Frame 1564, Roller_A 236, Roller_B 236, Crank 204; ceiling 2300.
  Overall size remains 1.236 x 0.700 x 1.200 m; feet min Z = 0.
- Checks: all parts non-manifold / loose / degenerate / component gaps = 0, expected X mirror = 0.
  Barrel BVH intersections with the entire frame (housing and chute included) = 0 for both;
  roller-to-roller intersections = 0. Axles intentionally pass through their bearings.
  Conservative clearances: inter-roller 13 mm, upper-lintel 3.8 mm, ends-plate 20 mm,
  ends-pillar 10 mm, lower-cylinder to sloped chute plane >= 8.70 mm.
- Three polish comparisons: (1) rounded facets/protrusion good, dark hubs too concealed by pillars;
  (2) widened dark hub discs inward so both ends are visible, other accepted visual differences unchanged;
  (3) unchanged geometry final check in front/side/back/top and 128 px, plus full 1280x800 preview inspected.
  Remaining differences: previously accepted machine proportions/palette and omitted fruit, no new defects.
- Re-exported same FBX / asset-only blend / atlas and texture copy / single preview paths.
  FBX re-import: 5 nodes, 2240 tris, size 1.236/0.700/1.200, scale 1, texture found (256x256).
  Evidence: polish_export.log and polish_build.log in this folder; temporary comparisons remain under
  %TEMP%/FarmProcessing_check/STA-04 because automatic approval review blocked both cleanup commands.
  Verdict SHIP. Unity import remains outside this task.

Run from worktree root in PowerShell:
`$env:PYTHONUTF8='1'; & 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python .work/models/Farm_Processing/STA04_FruitCrusher/build_fruit_crusher.py -- export`
Use `-- build views <tag>` instead for temporary multi-angle checks and the 128 px thumbnail;
`python .work/models/Farm_Processing/STA04_FruitCrusher/compare.py <tag> 400` creates the comparison sheet.

Reference: planning/FarmProcessing/references/STA-04.png (three-quarter front-left; measured from hopper/stand edges:
camera yaw ~30 deg to the -X side, elevation ~25 deg, moderate perspective).
Catalogue: "hand-cranked fruit crusher on a wooden stand, square hopper, two simple rollers, open output chute",
1.0 (X) / 0.8 (depth) / 1.2 (height) m, LOD0 1600-3000 tris, moving parts: crank handle + two rollers.

## Feature list (from the reference; px measured on the 1374x1145 ref, ~736 px/m)
- Wooden stand: 4 chamfered square legs, slightly splayed (feet ~0.12, tops ~0.10), feet ~ under the hopper rim corners.
  Chamfered head blocks (~0.15 square, z ~0.48-0.66) on the leg tops; red square caps on the front faces of the front heads
  and on the outer side faces of the back heads.
- Top side rails (along Y, between front and back heads, z 0.50-0.60) carry the housing; back top rail between back heads.
  No front top rail (the chute drops between the front heads).
- Low stretchers on all 4 sides at ~0.26 m (darker wood).
- Metal housing (blue-grey) on the side rails: two thick side plates, front corner pillars (flange), top front lintel,
  back plate; open front window showing the rollers. Hex bolts on the side plates (top-front, top-back, bottom-back).
- Two light beige rollers (10-gon, chamfered ends, D ~0.13 m, ~0.44 m long) stacked one above the other in the window,
  ~1 cm gap between them; axles through the side plates, small round bearing caps; upper roller axle carries the crank.
- Big round boss (10-gon, D ~0.17) on the left (-X) plate around the upper axle.
- Crank (-X side): square-ish bar axle out of the boss ~0.13 m, mitred elbow, arm straight down ~0.24 m, chunky orange
  octagonal wooden grip (D ~0.10) pointing -X, chamfered ends.
- Hopper: wide square funnel (warm grey), wider at the top (outer top ~0.80 x 0.62 incl. lip, bottom = housing top
  0.62 x 0.35), thick flat lip with chamfered edges, inner walls darker; rests ON the housing top (z 0.97), top at 1.20.
- Open U-chute (warm grey) leading out of the housing under the lower roller, sloping ~25 deg forward/down between the
  front heads; floor + two side boards with sloped top edges and chamfered front ends.

## Material class
Flat palette: own atlas T_FarmProcessing_STA04_BaseColor.png (256 px, 4x4 solid cells), one material M_FarmProcessing_STA04.
Cells 0-14 identical to STA-05 (13/14 = warm grey PLATE/PLATE_D, used for hopper/chute/boss); 15 = roller beige #D4CBBE.
No noise, no grain.

## NOT modelled
Fruit in the hopper (ref shows 6 apples - goods, not the machine), crushed pulp, a bucket under the chute, gears between the
rollers, nails/wood grain, floor/platform, text, LOD1 and collider (next step), housing bottom plate (hidden).

## Anchors followed
STA-05 juice press (approved: art/Farm_Processing/Previews/FMS_Workshop_STA_05_Preview.png + build_juice_press.py: chamfered
splayed legs with head blocks, red caps, hex bolts, palette, checks) and STA-02 cheese press (pilot; same helpers via
_common/processing_common.py). Headless structure (clear_scene / render / verify) copied from STA-03 build_butter_churn.py.

## Hierarchy / pivots (front = -Y, root identity, ground centre)
FMS_Workshop_STA_04 -> _Frame (0,0,0: stand + housing + hopper + chute + boss/caps/bolts),
_Roller_A (upper, axle axis point (0, ROLL_Y, ZA), rotates about local X), _Roller_B (lower, (0, ROLL_Y, ZB)),
_Crank (on the upper axle axis at the boss outer face, rotates about local X with Roller_A).

## Dimensions / deviations
Catalogue X/Y(depth)/Z 1.0/0.8/1.2. Built X 1.246 (stand + hopper + housing 0.992 = catalogue width; the crank sticks out
0.25 m on -X, x -0.750..0.496) x Y 0.660 (hopper lip 0.66; feet 0.58; chute lip at y -0.31) x Z 1.200 (hopper rim).
Width follows the reference: the housing is almost as wide as the hopper, the stand splays to the hopper corners and the ref crank
is long with a chunky grip; round 1-2 at the catalogue box read clearly too narrow. Depth -0.14 m vs catalogue (ref hopper/stand
are shallower than 0.8). If the pack grid needs 1.0 m including the crank, scale uniformly 0.8 (height 0.96 m).
Rollers are stacked vertically in the front window as in the ref (authoritative), not side by side.

## Compare rounds (check renders in %TEMP%\FarmProcessing_check\STA-04, deleted; overlay.py = ref/render 50% blend at equal height)
1. Heads too far apart in Y, housing sat between them (ref: housing rests on the head/rail top frame); chute far too long/flat;
   boss/crank tiny. -> heads y 0.265 -> 0.20, housing depth 0.40, chute 35 deg shorter, boss R 0.10, bigger rollers.
2. Camera too frontal (ref shows a wide left side face), chute still 1.5x too long on screen, crank axle short, housing too light.
   -> yaw 40, chute 30 deg lip y -0.31, elbow x -0.52, housing METAL_D.
3. Overlay: stand ~15% narrow in X / too deep in Y, housing narrower than the ref (ref hopper barely overhangs in X), grip small,
   chute lip high. -> heads (0.37, 0.18), feet (0.43, 0.23), housing 0.72 wide, rollers 0.55 long, grip R 0.062, chute 40 deg.
4. Camera calibration by overlay: the ref is not a strict pinhole image (front feet line flatter than the hopper rim); 35 mm made the
   feet line far too steep, 70 mm at yaw 28 / elevation 24 deg overlays best (bbox width 901 vs 920 px at equal height).
   Textured: chute read as a flat ramp facing the camera, crank thin/bluish, hopper walls as light as the rim.
   -> chute 30 deg, boards 35 mm thick and taller, crank bar 70x55 mm warm grey, grip R 0.066, hopper outer walls PLATE_D.
5. Board inner faces darker so the U-channel reads; final full-size preview checked; 128 px thumbnail reads as a crusher
   (grey hopper / blue-grey housing with cream rollers / orange stand / crank).
(Economy limit is 3 rounds for < 2000 tris; rounds 4-5 were the camera calibration + colour polish, no new geometry.)
Remaining nitpicks: ref wood more saturated orange (pack palette kept), ref hopper outer walls a bit darker, ref shows more of the
left side face (inconsistent projection in the ref), ref crank arm has a small kink, ref chute lip ~5 cm lower.

## Lead review fix round (front / crank)
1. Rollers: 8-sided, identical, both axes in one vertical plane y -0.175, fronts 5 mm proud of the window (housing front moved to
   y -0.24, still on the front heads); nothing hides the upper roller any more.
2. Chute: open U-channel, floor 28 deg from just under the lower roller (10 mm clear) to the lip at y -0.38 (12.5 cm in front of the
   heads), side walls 7 cm along the whole length; the tall flap is gone. Added a housing bottom plate behind the floor (the stand
   showed through the hopper throat).
3. Colours: hopper + chute grey metal pair (METAL #8E959B walls / METAL_L #A9AFB4 lip and floor), rollers beige, housing METAL_D.
4. Crank: light metal bar with the ref's Z-kink (axle -> down 0.10 -> offset -X 0.045 -> down to the handle), round 12-sided hub collar,
   round 12-sided boss disc (R 0.085, overhangs the plate front edge by 2 cm because the axle now sits near the window front),
   faceted 8-sided wooden handle.

## Result (after the fix round; supersedes the numbers below)
Tris: Frame 1564, Roller_A 124, Roller_B 124, Crank 204 = 2016. Size 1.236 x 0.70 x 1.20. Pivots: rollers (0, -0.175, 0.875 / 0.711),
crank (-0.40, -0.175, 0.875). Checks 0 / 0 / 0, gaps 0; FBX re-import 5 nodes, 2016 tris, texture found.

## Result (before the fix round)
Tris: Frame 1524, Roller_A 156, Roller_B 156, Crank 104 = 1940 (budget 1600-3000).
Checks: 0 non-manifold / loose / degenerate per part; X-mirror exact (boss, right upper cap, Roller_A axle, crank excluded:
asymmetric by design); component gaps 0; feet on z=0; housing bottom 0.62 = rail/head tops; hopper bottom 1.00 = housing top.
Clearances: roller-roller 13 mm, upper roller-lintel 7 mm, roller ends-plates 20 mm, lower roller-chute floor >= 24 mm,
chute-front heads 5 mm, crank arm-head 88 mm (sweep radius 0.335 m clears the stand), bolts-boss 10 mm.
FBX re-import: 5 nodes (root + Frame/Roller_A/Roller_B/Crank), 1940 tris, dims 1.246/0.66/1.2, texture found in
FMS_Workshop_STA_04.fbm (256x256). Blender shows rot X 90 on re-import (Y-up FBX axis conversion, same as the other pack FBXs).
Movement: Roller_A, Roller_B and Crank rotate about their local X axis (Unity X); Crank and Roller_A share the axle axis
(y -0.07, z 0.873), Roller_B axis z 0.71 (counter-rotate for crushing).
