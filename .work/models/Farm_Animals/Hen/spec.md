# BRD-01 Hen - spec (Farm Animals, skeleton B, MESH ONLY this round)

Reference: `planning/FarmAnimals/references/BRD-01.png` (1217x1293, front-left three-quarter, yaw ~40 deg from the side,
elevation ~10 deg, hen faces image-left, near side = hen's left = +X).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-01 - russet-brown hen, red comb + wattles, yellow beak, fan tail 5-7 feathers,
0.45 x 0.40 m, 900 tris, skeleton B, pilot.
Anchors followed: pilot Cow (`../Cow/build_cow.py`: ring lofts, palette atlas via pack_common, surface ray-cast placement of
eyes, Workbench check sheet + EEVEE preview from `_common/animal_render.py`, imported read-only); house style 11/11b.

## Measured from the reference (ground y~1195 px, comb top y=45 px -> 0.40 m => 0.000348 m/px vertical;
horizontal on the centre line / cos(40 deg) => ~0.000455 m/px along the body)
| Feature | px | m (design) |
|---|---|---|
| comb top (lobe 2) | y 43 | 0.400 |
| comb lobes (4) tips | x 285/370/450/515, y 83/43/50/123 | 0.387 / 0.401 / 0.398 / 0.373 |
| head top / eye centre | y 165 / 272 | 0.358 / 0.320 |
| eye diameter | 47 | 0.017 (8-gon) |
| beak tip / base (centre line) | x 140 / 265 | length ~0.055-0.06 |
| upper / lower beak height at base | 68 / 40 | 0.024 / 0.014 |
| wattle lobe (near) | 85 x 150 | 0.030 x 0.053, bottom z 0.249 |
| back line at the tail base | y 470 | 0.25 |
| breast front | y 640-700 | z 0.17-0.19 |
| belly bottom | y 990 | 0.068 |
| shank width top / ankle | 80 / 55 | 0.028 / 0.022 (6-gon, chunky) |
| shank visible | y 1000-1110 | 0.039 |
| toes length (front / back) | 230 px foot span | 0.055 / 0.028, height 0.012-0.017 |
| legs apart | 210 px | x = +-0.052 |
| wing (near) | x 500-950, y 525-830 | Y -0.11..0.10, z 0.125-0.232, two tiers + rear tip |
| tail fan tips | 7 tips, 8..113 deg from horizontal-back | 6 feathers 10..105 deg, 0.10-0.15 long |
Design sizes: length beak tip -> tail tip 0.45, height 0.40 incl. comb, body width 0.20 (chunky).

## Features (must read at 128 px)
Pear-shaped faceted body with a big low breast and a thick neck flowing into the head (no thin neck); big head (~120 %);
4-lobe chunky red comb with a ridge (two tones per lobe); two red wattle drops under the beak; yellow two-part beak with a
visible mouth line (lower beak narrower and darker); dark 8-gon disc eyes #2A1D17, 19 mm, 4 mm proud; folded chestnut wing as one
shape (light upper band, darker lower band, rear tip, flush); 6 chunky diamond-section tail feathers in a fan with
small gaps; short feathered thigh cuff (dark body colour = hock joint band) above a thick yellow 6-gon shank running straight
into 3 front toes + 1 back toe flat on the ground.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Hen at the ground under the centre of mass)
Body, Neck1, Neck2, Head (+ upper beak), Beak_Lower, Comb, Wattle, Eye.L/.R, WingUpper.L/.R (upper covert band),
WingLower.L/.R (lower band, under WingUpper), WingTip.L/.R (rear point), TailFan1 (rump wedge), TailFan2 (6 feathers),
LegUpper.L/.R (feathered thigh), LegLower.L/.R (shank), Foot.L/.R (hidden ankle knuckle + 4 toes). Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Hen_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Hen`.
Cells: 0 body #C2582A, 1 body dark (belly, thigh) #9C4422, 2 body light (spare/variant), 3 wing #8A3826, 4 wing dark
#6B2A1B, 5 tail #B9532A, 6 tail dark, 7 comb #E3262E, 8 comb dark, 9 beak #F6BE2C, 10 beak dark (lower beak) #E09A1A,
11 leg #F5BF2B, 12 leg dark (spare) #D99420, 13 eye #2A1D17, 14-15 series spares. Variants (white, black-speckled)
swap cells 0-6.

## NOT modelled
ground, straw, eggs, nest, individual feathers on the body, claws, nostrils, ear lobes, eyelids, scales on the legs.
No armature, no weights, no animation (this round).

## Rounds
1. Wattles hidden inside the neck; tail feathers thin sticks with big gaps; body long/boxy, beak thin; 1444 tris; 2 coplanar
   pairs (wing tip cap on the body rear cap plane). -> neck moved back, wattles forward + bigger, feathers wider with
   alternating thickness, pear body (9 rings), beak +20 %, cheaper eyes/pads/thighs/wattle (1308 tris), tip cap moved.
2. Tail fan sparse, wing flat, back flat to the tail. -> broader feathers, fan root forward/up, wing 30-50 % prouder, rear back raised.
3. (EEVEE at the reference angle) fan too compact/upright, brown thigh cuff too visible, breast cap reads as a disc.
   -> fan longer and tilted back, thigh cuff 7 mm, cap shrunk; tail cell lighter (ref tail = body colour).
4. Breast cap still visible as a disc -> cap ring 6 mm (left a small faceted point).
5. Polish pass (coordinator): breast point, neck step behind the head, tail fan too upright/high, 1308 tris.
   -> front body rings tilted (section plane through front-bottom and back-top points): the breast curves up into the neck
   and the body cap sits inside Neck1; Neck1 base ring pulled inside the breast (its underside showed as a ledge); Neck1
   tapers into Neck2, Neck2 runs flush into the back of the head (no ruff); fan root lower/forward, feather tips matched to
   the reference heights (top tip at eye level, 110..9 deg); eye 19 mm, 4 mm proud, pyramid back; tris cut to 1104
   (body 10 sides, neck 8 sides, 5-point wing sections, 2-ring shanks, 5-sided wattles, leaner comb base, 6-sided rump).
   Remaining: a shallow faceted crease where the neck meets the breast (no ledge or hole); fan still a little less spread
   than the reference.

6. Review round 3 (4/5): ankle ring, thin neck + step at the head/neck/chest junction, two-tier wing step.
   -> Foot pad = small LEG-coloured knuckle under the shank (shank runs to z 0.005 into the toes, no darker ring);
   Neck1 4 rings, base +15 % wide, its front follows the breast curve and crosses it at z~0.20; breast top lowered under the
   neck; Neck2 flush into the jaw and the back of the head; wings = one shared outline + one outer surface, WingUpper /
   WingLower / WingTip are bands of it (upper overlaps the lower by a 1.5 mm lip; colours light / dark / light).
   Views checked: reference angle, side, front, behind, above, 128 px. Tris 1156.

## Deviations
- tris 1156 vs 900 target (+28 %): 23 separate closed parts for later binding, diamond-section tail feathers 120,
  wings 216, 4-ring neck base.
- length 0.461 m beak tip to tail tip (catalogue 0.45), height 0.403 m incl. comb, width 0.263 m incl. wings (body 0.21).
- eyes 19 mm, 4 mm proud (plan says about 5 mm; 4 mm reads at 128 px without looking like a button).
- TailFan1 = rump wedge, TailFan2 = all 6 feathers (no split of each feather into two halves).
- Objects are named exactly after the skeleton B parts (Body, Eye.L, ...); mesh data are named FMS_Hen_<Part>.

## Bird rig (skeleton B) - reusable for Rooster, Chick, Duck, Goose ...
Files: `rig_hen.py` (bone template, species table, binding, bend test, export) + `hen_clips.py` (bird clip toolkit + clips).
Run: `rig_hen.py -- BRD-01 bend|anim|export` (headless Blender 5.2). Mesh from `build_hen.build()` unchanged (parts, pivots).
To reuse: copy both files, change `import build_hen` -> your build module and the species table `HEN`; nothing else.
- **Bones (20)**: Root > Body > {Neck1 > Neck2 > Head > Beak_Lower; WingUpper > WingLower > WingTip (.L/.R);
  TailFan1 > TailFan2; LegUpper > LegLower > Foot (.L/.R)}. `B_BONES` is registered as `animal_rig.SKELETONS['B']` at runtime
  and built with `animal_rig.build_armature` (roll rule: local X = world X, so euler x = pitch for every sagittal bone).
- **Bone heads = part pivots**; tails = next joint (`CHAIN_TAIL`); chain ends take `ends` offsets from the table (Head tail =
  beak tip, Body tail 8 cm forward so Body y = roll and z = yaw), Foot tail straight down to the ground (foot target).
- **Axes used by the clips**: Body x pitch (+ nose down), y roll, z yaw; Neck1/Neck2 x pitch (+ forward), y twist (yaw);
  Head x pitch, y tilt (cock the head), z yaw; WingUpper.L z < 0 / .R z > 0 = wing out/up (flap about the shoulder);
  TailFan1 x + = tail up, z = wag; LegUpper/LegLower/Foot x by the leg IK (knee forward), Foot x + = toes curl down.
- **Binding**: each part = one bone, weight 1.0 (`bind`: Comb, Wattle, Eye.L/.R -> Head). Linear two-bone blends only at
  the neck (`blend`: Neck1 head 50/50 with Body over +-14 mm, Neck1/Neck2 and Neck2/Head over +-10 mm; 11 vertices).
  Bend test (legs 110 deg knee, neck 60/50 down, 45/40 back, twist 40/45 + head yaw 80, wings out 60/90 deg, tail up/down/
  wag, body pitch 35/-25 + roll 12): no holes; the wing top edge stays buried in the body when the wing swings out.
- **Toolkit (hen_clips.py)**: `BirdSkel` (FK/skin, legs table, mover bone), `body`, `lower_body`, `leg_ik` (copy of the Q
  leg IK), `plant`, `settle` (lower the body until both legs reach), `neck_ik2` (analytic planar 2-bone neck IK to a head
  pivot target, fixed bend side = arched neck), `set_head_down` (signed head pitch), `jerk` (bird holds + 3-frame snaps),
  `env`, `look`, `gait` (biped walk in place: feet back at speed in stance, swing arc + toe curl, body height from reach,
  waddle roll/sway), `write_action` (location keys on Body only), `metrics` (loop closure, lowest vertex, foot slip,
  head travel, beak height, joint limits).
- **Species table keys**: bind, ends, blend, gait.Walk (T, duty, speed, lift, toe_curl, crouch, pitch, roll, sway, yaw,
  phases, hold = head-hold share of a step, head_dz, head_nod, tail), clips, limits (`B_LIMITS`), poses (stand_bend,
  wing_out, idle_look keys, peck_* lean envelope, hit times, pitch, drop, target y/z, head angles, tail, feet offsets).

## Clips (30 fps, in place, Actions Hen_<Clip>, FBX takes via NLA + bake_space_transform)
| Clip | s / frames | content |
|---|---|---|
| Idle | 3.5 / 105 | head looks around in 3-frame snaps with holds (yaw up to 44 deg, cocked tilt up to 16 deg, nods), breathing, tail wag burst, one wing ruffle |
| Walk | 0.8 / 24 | biped walk 0.20 m/s, step 0.096 m, duty 0.6; head held still in space for 66% of each step (travels 0.053 m back relative to the body) then snaps forward before touchdown; waddle, tail bob; Footstep events LegL f0, LegR f12 |
| Peck | 2.5 / 75 | lean 32 deg, 3 quick pecks (beak tip to 4 mm above the ground 18 cm in front of the hips) at f23/33/42 with a cocked look between, left foot 2.2 cm forward, tail up 26 deg while the head is down; Peck events |
Metrics: loop closure 0.000 deg / 0.000 m (all), lowest vertex Idle 0.000, Walk -0.0008, Peck 0.000 m; Walk foot slip
0.61% of the step; joint limit violations 0 (own B_LIMITS; Neck1 x up to 100, Neck2 x down to -110 deg for the peck).
Rounds: Idle 1; Walk 2 (toe curl 40 -> 22 deg: toes dipped 1 cm in mid swing); Peck 6 (more than the 4 asked: the Newton
neck IK folded, the beak target sat under the breast, the head pitch measure was unsigned, the elbow side flipped mid-lean,
the ready pose folded the neck).
Remaining: when the neck moves (walk bob, peck) the Neck1 base slides over the breast and shows a small light seam at the
junction (rigid parts); not verified in Unity (Generic avatar import, takes, events).
