# BRD-08 Pigeon - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-08.png` (1536x1024, front-left three-quarter: body yaw ~40 deg from the
front, head turned a little more to the camera (~20 deg), elevation ~8 deg; near side = pigeon's left = +X).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-08 - grey, slate-blue neck, white spot marking on the wing, 0.32 x 0.25 m, 600 tris,
skeleton B, extension. Lead brief: ~600 tris (max +15 % = 690), eyes readable at 128 px, short tail with a darker tip,
pale cere, thick pink-orange legs with toes.
Anchors followed: BRD-04 Duck (`../Duck/build_duck.py`: tilted body rings, horizontal neck rings, ray-cast eyes and wing
tiers, split_to_objects, checks, Workbench sheet + EEVEE preview via `_common/animal_render.py` read-only) and BRD-01 Hen
(toes, thigh cuff, polish lessons: breast flows into the neck, Neck2 flush into the back of the head). House style 11/11b.

## Measured from the reference (ground y~975 px, head top y~32 px -> 0.25 m => 0.000265 m/px vertical)
| Feature | px | m (design) |
|---|---|---|
| head top / eye centre | y 32 / 160 | 0.250 / 0.216 |
| head width x height | 310 x 270 | 0.078 x 0.072 (big round head, ~120 %) |
| eye disc | ~45 px | 0.014 (8-gon, 3 mm proud) |
| beak | cere top y 150, tip y 275 | 0.030 long, points down-forward, tip z ~0.185; pale cere on the base |
| blue neck band | front y 290-490, sides up to the head | z 0.128-0.20 front, up to 0.23 at the sides |
| chest (widest) | y 600-700, ~415 px wide | z 0.08-0.10, body width 0.115 |
| belly bottom / thighs | y 790-830 | 0.046 / grey thigh cuff 0.035-0.07 |
| shank | 65 px wide, y 830-930 | 0.019 (6-gon), exposed z ~0.035 -> 0 |
| foot | 200 px wide, 3 front toes + back toe | span ~0.05, toes 0.012 wide, 0.010 high |
| legs apart | 225 px | x = +-0.030 |
| wing | shoulder x700 y380 -> tip x1230 y720 | z 0.16 -> 0.08, diagonal down-back |
| white wing spot | x 830-1050, y 490-610 | lower-rear part of the light upper wing |
| tail | dark, x 1100-1230, y 630-720 | tip y +0.17, z ~0.07, tilted down-back |
Design: length beak tip -> tail tip 0.32, height 0.25, width ~0.13 incl. wings.

## Features (must read at 128 px)
Round faceted grey body with a puffed breast that flows up into a thick slate-blue neck (blue bib, lighter front, a small
lighter lilac-blue iridescent patch on the neck sides), round grey head, dark 8-gon disc eyes #2A1D17, short grey beak with
a pale cere, folded wing in bands: light grey coverts with a white spot, darker grey lower band, dark wing tip over the
rump; short flat tail with a darker tip; grey thigh cuffs, two thick orange 6-gon shanks, chunky toes (3 front + 1 back).

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Pigeon on the ground under the centre of mass)
Body, Neck1, Neck2, Head (+ upper beak and cere), Beak_Lower, Eye.L/.R, WingUpper/WingLower/WingTip .L/.R,
TailFan1 (rump wedge), TailFan2 (flat tail with dark tip), LegUpper (grey thigh cuff), LegLower (orange shank), Foot (4 toes).
Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Pigeon_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Pigeon`.
Cells: 0 body #9B9AA6, 1 body dark #7F7E8A, 2 body light (spare), 3 neck #557499, 4 neck light #6C8BB2, 5 iridescent
#7E86B8, 6 wing #8E8D99, 7 wing dark band #65656F, 8 white #EEEEF2, 9 wing tip / tail tip #4E4E57, 10 tail #6F6F79,
11 beak #8C8A96, 12 cere #D6D4DC, 13 leg #E89A3C, 14 leg dark #C97E2C, 15 eye #2A1D17.

## NOT modelled
ground, individual feathers, claws, nostrils, eyelids, eye rings, leg scales, wing bars as separate geometry.
No armature, weights, animation clips; no LOD1 (small animal, same as the other birds).

## Rounds
1. 726 tris (+21 %). Body long and horizontal, head small; tail + wing tip a long spike; eyes poked out of the head
   outline in front view; Neck1 top showed as a ledge from above. -> plumper, more upright body (rear 0.094 -> 0.076),
   head +10 %, shorter broader tail, eyes forward, Neck1 tucked inside Neck2; WingUpper/WingLower 3 rings, Neck1 2 rings,
   5-gon thigh (phase fixed for an exact mirror) -> 662 tris.
2. Wing tip ended in a thin spike, dark belly band read as a strap, eyes still lateral -> blunt tip, belly cell removed.
3. (EEVEE, reference angle) wing a stubby block, white spot only a thin strip; head overhung a narrower neck. -> longer
   4-ring upper wing with a constant middle section, white on two outer faces; wider neck; head underside blue.
4. Reference camera retuned (body yaw ~54 deg, matches the frame proportions); head +5 %, neck base pulled into the breast.
5. Neck read as stacked boxes, dark lower band hidden, thigh cuffs long -> smooth neck taper (Neck2 flush on Neck1),
   lower band 4 mm prouder and lower, cuffs shortened; head back ring widened (no ledge at the nape from behind/above).
Views checked: reference 3/4, side, front, back, top, 128 px thumbnail.
Remaining nitpicks: the neck shows 2-3 large flat facets (8-sided rings) instead of the reference's smooth blue bib; the
far eye shows only as a small edge (head not turned to the camera like in the reference); tail + wing tips taper to a
point from the 3/4 view where the reference tail end looks a little blunter.

## v2 rework (coordinator: "thin, small-headed bird"; the reference is plump, round, cute)
Diagnosis: the v1 check/preview camera was too side-on (head seen in profile), the body was 0.11 m wide, the head and
collar were front-to-back ring lofts (blue could only be painted in steps).
Rebuilt: body 12 sides, 0.154 m wide (+37 %), pear with the widest ring at the chest; head = 6 horizontal tilted rings
(12 sides), 0.10 m wide x 0.086 m high, ring H1 = collar line on the head; body ring R1 tilted with a pointed front
vertex = V of the collar on the chest; Neck1/Neck2 shrunk to hidden connectors so the visible blue is one band (head
segment 0 + body segment 0); eyes 8-gon 14.7 mm (~15 % of the head width) at 55 deg from the front; short rounded
5-point beak with a cere bump; 6-point shield wing with the white patch on its lower outer faces; thick fanned tail
with a squared dark end; shank 21 mm, feet 4 toes 46/40/40/22 mm. Camera yaw ~37 deg as the reference.
Rounds: v2.1 eyes buried (inward hit normal) + thin white stripe + flat head top -> normal flipped, taller patch face,
extra top ring; v2.2 head on a narrow blue stalk, flat collar edge, edge-on spike tail -> wide lower head, steeper R1
with V, thicker tail tilted down; v2.3 neck poked out under the beak with a sawtooth intersection, small dark band ->
necks hidden, lower band 8 mm lower, heavier wing tip; v2.4 light mouth sliver from the side -> lower beak as wide as
the upper. Views checked: reference 3/4 (EEVEE), side, front, back, top, 128 px.
Remaining: a short faceted crease where the head's blue segment meets the body's collar segment under the beak; the
white patch reads as a long stripe in the pure side view; the tail end still tapers to a point at the reference angle
(the wing tips converge over it).

## v3 rework (independent review 3/5: scarf-like two-tone collar with a dark ring under the beak, white plate,
## lower wing flap step, thin spike tail)
- Collar: one cell #5E7FA3 on head segment 0 + body segment 0 only. Head ring H0 dropped into the chest (front y -0.114,
  z 0.136, inside the body) so the head's blue segment is a near-vertical skirt from the chest to just under the beak:
  no throat notch, no down-facing cap, no dark ring; Neck1/Neck2 fully hidden. Top edge = head ring H1 (front z 0.19
  under the beak, rising to the cheeks), bottom edge = body ring R1 (rounded V on the chest). Throat 7 mm further forward
  and the beak tip tucked 4 mm (shorter beak cast shadow).
- Wing: one 7-point shield per side split along its length into WingUpper / WingLower / WingTip (each starts 4 mm inside
  the previous one, 1.5 mm smaller), explicit triangle diagonals; white = flush diagonal parallelogram of 4 triangles on
  the WingUpper rear segment (no raised plate); lower bevel row darker; WingTip dark, ends in a point at y 0.152 over the
  tail. Rear sections prouder (32 mm) so the shield faces sideways like the reference.
- Tail: TailFan2 thick flat wedge (root 36 mm, end 16 mm thick), 0.072 m wide (0.47x body width 0.154), squared dark end
  at y 0.192, 40 mm beyond the wing tip. Camera yaw 41 deg.
Views checked (EEVEE): reference 3/4, side, front, back, top; Workbench sheet; 128 px.
Remaining: the beak's own cast shadow (preview sun) leaves a short shaded streak on the collar; 1.5 mm steps at the
wing part joints are visible from above as thin lines.

## Deviations
- v3: tris 878 (coordinator allowed ~900); size 0.325 x 0.272 x 0.192 m.
- tris 830 vs 600 target (+38 %; the coordinator allowed ~900 for the rework).
- Size 0.329 x 0.272 x 0.188 m (L x H x W incl. wings); root pivot on the ground under the centre of mass.
- Head straight (symmetric rest pose); the reference turns the head towards the camera.
- Legs #E8A23A orange-yellow as in the reference.
- No separate iridescent patch: the coordinator asked for one smooth blue band.
- Neck1/Neck2 are hidden connectors inside head and body (kept for the skeleton B binding).

## Rig + clips (2026-11-21) - skeleton B with flight (first flying bird; Sparrow and Crow reuse it)
Files: `rig_pigeon.py` (species-generic rig: `main(SP, build_module)`, table `PIGEON`), `pigeon_clips.py` (copy of
../Hen/hen_clips.py + flight), `fly_gif.py` (Fly GIF wrapper around _common/anim_gif.py, read-only: shadow footprint in the
camera fit, sun 22 deg from vertical). Run `rig_pigeon.py -- BRD-08 bend|anim|export|meshcheck`. Mesh unchanged
(meshcheck vs the mesh-only FBX: 21 parts, max vertex diff 0.00000 m; texture byte-identical).
Anchors followed: BRD-01 Hen rig B (bones, binding, IK, peck, export/re-import), Bee bee_gif.py (wrapper pattern).
- Bones (20, hen names/hierarchy). Changes for flight: WingUpper head = spread pivot on the wing root (3 cm behind the
  wing front on the folded-wing axis, so the narrow front of the shield swings into the body); WingLower / WingTip heads
  on the seams between the wing parts, WingTip tail at the wing tip; virtual long neck (Neck1 head 0.012/0.118 inside the
  chest, Neck2 -0.030/0.165) for the peck reach; hidden connectors Neck1 -> Body, Neck2 -> Head; head collar ring H0
  (inside the chest) weighted to Body by a plane blend, ring H1 to Head: the blue band stretches into a neck.
- wing_set: folded frame (a = wing front -> tip, n = outer normal, c = n x a) mapped onto the flight frame (a' = out,
  n' = up): the patterned outer face becomes the top; then flap about the body axis, sweep, twist, lag/sweep of
  WingLower/WingTip about the seam hinges. Wing bones are generated as matrices; finalize() picks one euler order per
  bone over all clips (WingUpper ZYX, max middle angle 15 deg: no gimbal flips) and writes compat eulers.
- Limits: hen B_LIMITS + flight: WingUpper.L x -90..30, y -45..45, z -180..10 (.R mirrored), WingLower/WingTip +-45.
| Clip | s / frames | content |
|---|---|---|
| Idle | 4.0 / 120 | head looks around in 3-frame snaps with holds (yaw up to 38, tilt 14), breathing, tail flick, wing ruffle |
| Peck | 2.5 / 75 | lean 30 deg + 1.5 cm forward, 3 pecks (beak tip 3 mm above the ground 12 cm in front of the body centre) at f23/33/42, cocked look between, neck stretches; Peck events |
| Fly | 1.0 / 30 | 3 wing beats (10 frames, downstroke 55 %), flap 12 +- 55 deg, WingLower/WingTip lag 22/18 deg, sweep back + twist on the upstroke, body pitched 26 deg, lifted (lowest vertex 0.045 m), bobs 8 mm, feet tucked, head level; Flap events f0/10/20 |
Metrics: loop closure 0.000 deg / 0.000 m (all), lowest vertex Idle -0.0006, Peck -0.0011, Fly +0.045 m; limit violations 0;
span Fly 0.39-0.56 m; FBX re-import: 20 bones, 21 meshes, 878 tris, 3 takes, max vertex error 0.0 m, texture found.
GIFs (640x400, 20 fps): Idle 2.0 MB, Peck 1.5 MB, Fly 0.96 MB (fly_gif.py, view 0.85 -0.7 0.24, fill 0.9).
Rounds: Fly 4 (wings out of phase = mirror sign of the child sweep; framing/shadow out of frame; feet visible; bird small
in frame); Peck 3 (chest into the ground at 48 deg; head tucked under the chest -> target 12 cm forward, longer virtual neck).
Remaining: the stretched collar shows a lighter blue facet on the nape at the peck; the spread wing is the folded shield
(narrow paddle, chunky 2-3 cm thick), thin seam lines between the wing parts at the largest lag; not seen in Unity.
