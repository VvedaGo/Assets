# BRD-10 Crow - spec (Farm Animals, extension, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-10.png` (1536x1024, front-left three-quarter: body yaw ~55 deg from the
front, head turned to the camera (face frontal), elevation ~8 deg; near side = crow's left = +X).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-10 - black with a blue sheen (palette cell), grey beak, large; 0.50 x 0.40 m,
650 tris, skeleton B. Lead brief: ~900 tris (up to ~1200 if it helps), 0.50 m beak -> tail tip, 0.40 m tall.
Anchors followed: BRD-08 Pigeon v2 (`../Pigeon/build_pigeon.py`: pear body of tilted rings, egg head of horizontal tilted
rings, hidden Neck1/Neck2 connectors, ray-cast eyes, split_to_objects, checks, Workbench sheet + EEVEE preview via
`_common/animal_render.py` read-only) and BRD-02 Rooster (wing = overlapping plates projected on the body side, proud lower
edge; tail plates). House style 11/11b.

## Measured from the reference (ground y~985 px, head top y~20 px -> 0.40 m => ~0.000415 m/px vertical)
| Feature | px | m (design) |
|---|---|---|
| head top / eye centre | y 20 / 145 | 0.400 / 0.345 |
| head width (front) | x 290-610 = 320 | 0.124 (big round head, ~1/3 of the height) |
| eye disc, eye spacing | ~40 px, 190 px apart | 0.019 8-gon, yaw ~45 deg from the front, 4 mm proud |
| beak base width / drop | 115 px / y 130-290 | 0.048 wide, top 0.345 -> tip 0.282, length ~0.06, hooked tip |
| chest (widest) | ~355 px incl. depth | width 0.150, chest front y -0.162, z 0.21 |
| belly bottom / thighs | y 700-720 | 0.115 / dark thigh cuff down to 0.105 |
| shank | ~50 px wide, y 715-960 | 0.025 (6-gon r 0.0125), z 0.115 -> 0 |
| foot | toes span ~175 px | front toe 0.052, side toes 0.046 at +-32 deg, back toe 0.030; width 0.015 |
| legs apart | 190 px | x = +-0.040 |
| wing | shoulder (560,330) -> tip (1150,640) | 4 plates, z 0.30 -> 0.14, tip y ~+0.20 |
| tail | rump (930,600) -> tip (1365,800) | long broad wedge, tip z ~0.085, end width ~0.07 |
Design: length beak tip -> tail tip 0.50, height 0.40, width ~0.16 incl. wings.

## Features (must read at 128 px)
Upright solid near-black body (#2A2733 with light/dark facet shades), big rounded head flowing into a broad chest (no neck
step), thick grey wedge beak with a lighter ridge and a slightly hooked tip, dark brown 8-gon eyes with a lighter brown
rim, folded wing of 4 overlapping plates (light blue coverts, dark band, blue rows, long primaries) pointing down-back,
long broad tail wedge (dark sides, blue top + blue top plates) far past the wing tips, dark thigh cuffs, thick orange
6-gon shanks, 4 separated toes (3 front + 1 back) on an ankle pad.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Crow on the ground under the centre of mass)
Body, Neck1, Neck2 (hidden connectors), Head (+ upper beak), Beak_Lower, Eye.L/.R, WingUpper/WingLower/WingTip .L/.R
(plates), TailFan1 (rump wedge + covert plate), TailFan2 (tail wedge + top plate), LegUpper (thigh cuff), LegLower
(shank), Foot (pad + 4 toes). Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Crow_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Crow`.

## NOT modelled
ground, individual feathers, claws, nostril bristles, eyelids, leg scales. No armature, weights, clips, no LOD1.

## Rounds
1. 1108 tris. Body narrow, wing a small panel high on the back, tail a thin spike, beak long and curved, eyes invisible
   on the black head. -> body +10 % wider, eyes as frustums (dark disc + lighter brown rim), shorter deeper beak.
2. Chin ledge / collar line under the head, sawtooth crease on the throat (neck connectors and the body cap R0 poked out:
   new HIDDEN check printed 12 of 12 R0 verts outside the head). -> R0 tucked into the head, necks shrunk, chin softened
   (HIDDEN 0/72, 0/12).
3. Wing too small and plates not layered, wing tips splayed sideways past the tail (back/top views). -> 4 bigger plates
   further forward/lower with stepped proud (lower edge 22-30 mm), free plate parts at half proud so the tips converge
   over the tail; tail top faces + upper bevels blue.
4. Tail short and thin next to the reference, legs too far back, head a bit small, beak hooked like a raptor. -> thicker
   tail wedge with a dark side, wing tip shortened, legs 22 mm forward, head x1.06, straighter beak ridge.
Views checked: reference 3/4 (EEVEE + Workbench), side, front, back 3/4, top, 128 px thumbnail.
Remaining nitpicks: a soft crease on the upper chest where the head shell meets the body shell; the wing plates have
straight lower edges (the reference has more, smaller scalloped rows); the head top shows a small flat 12-gon cap from
above; head straight (reference turns it to the camera).

## Deviations
- tris 1140 vs 900 target (+27 %, inside the 1200 allowance; catalogue 650).
- Size 0.205 x 0.520 x 0.400 m (W x L x H incl. wings); root pivot on the ground under the centre of mass.
- Head straight (symmetric rest pose); the preview camera is at ~46 deg yaw (reference ~55 deg) so the face shows.
- Eyes have a lighter brown rim band (#5A3122) for readability on the near-black head; the reference has plain discs.
- Neck1/Neck2 are hidden connectors inside head and body (kept for the skeleton B binding).

## Rig + clip (2026-11-21) - skeleton B, flight-ready wing bones, Idle only this round
Files: `rig_crow.py` (species table `CROW` only) on ../Pigeon/rig_pigeon.py + pigeon_clips.py (read-only, see the Pigeon
spec "Rig + clips"). Run `rig_crow.py -- BRD-10 bend|anim|export|meshcheck`. Mesh unchanged (meshcheck 21 parts, max
vertex diff 0.00000 m; texture byte-identical). Anchors: Hen rig B, Pigeon flight rig.
Wing = 3 overlapping plates, so WingLower/WingTip keep the build pivots (layers, not a chain); WingUpper head = spread
pivot 4 cm behind the wing front. A provisional 'fly' table is exercised by the bend test (flap up/down with lags, tucked
feet): plates fan out like feathers, no holes. Walk/Fly clips: see the comment at the top of rig_crow.py.
| Clip | s / frames | content |
|---|---|---|
| Idle | 4.0 / 120 | deliberate head turns in 4-frame snaps with long holds: right (62 deg, cocked 14), back, left (66, -16), glance down, centre; breathing, one tail flick, one wing settle |
Metrics: loop closure 0.000 deg / 0.000 m; lowest vertex 0.000; neck yaw total 66 deg; limit violations 0. FBX re-import:
20 bones, 21 meshes, 1140 tris, 1 take, max vertex error 0.0 m. GIF Idle 1.6 MB. Rounds: 1.
Remaining: the head turn is small in the 640 px GIF (black head on a black body); not seen in Unity.

## Walk + Fly (2026-11-21, round 2) - mesh unchanged (meshcheck 0.00000 m, texture md5 unchanged), Idle table unchanged
Files: `crow_clips.py` (Walk = copy of ../Hen/hen_clips.gait + head-bob overlay, registered into pigeon_clips.CLIP_FUNCS in
memory; Pigeon files untouched), `rig_crow.py` ('gait' table, clips Idle/Walk/Fly, fly table tuned: 3 beats/s).
| Clip | s / frames | content |
|---|---|---|
| Walk | 0.8 / 24 | strut 0.22 m/s, step 0.106 m, duty 0.6, head held in space then thrust forward (60% of the ground travel), waddle roll 2.5, tail bob; Footstep L f0 / R f12 |
| Fly | 1.0 / 30 | 3 beats (downstroke 55 %), flap 10 +- 50 deg, lag 12/16 deg, body pitched 24, lifted (lowest vertex 0.12 m), feet tucked; Flap f0/10/20 |
Metrics: loop closure 0.000 deg / 0.000 m; lowest vertex Idle 0.000, Walk -0.0002 m; Walk slip 0.08 % of step; limit
violations 0. FBX re-import: 20 bones, 21 meshes, 1140 tris, 3 takes (Crow_Idle 120, Crow_Walk 24, Crow_Fly 30), max
vertex error 0.0 m, texture found. GIFs: Crow_Walk 0.79 MB, Crow_Fly 0.83 MB (../Pigeon/fly_gif.py, view 0.85 -0.7 0.24,
fill 0.9). Rounds: 1. Remaining: tucked shanks show as an orange stick under the tail in Fly; wing plates fan apart a little
at the top of the beat (plates are layers, as on the Pigeon); not seen in Unity.
