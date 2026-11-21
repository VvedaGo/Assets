# INS-02 Butterfly - spec v1 (Farm Animals, skeleton I parts, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/INS-02.png` (1536x1024). Near-frontal view from the butterfly's front-right
(-X side, abdomen visible to image-left), ~15 deg above. Orange/dark-brown monarch-like butterfly, wings held up and open
toward the viewer (wing faces seen almost square-on from the front), round orange head with two dark eye domes, two straight
antennae with club tips, dark thorax, short orange/dark striped abdomen going back-down, six dark chunky folded legs.
Catalogue: FARM_ANIMALS_PACK.md 5.5 INS-02 (wingspan enlarged to 0.15 m on purpose, documented deviation from TECH-01;
catalogue tris 150 -> lead target ~350-450, "polished over minimal"), 4 (look rules), 6 (skeleton I, two bones per wing).
Anchor followed: INS-01 Bee (`../Bee/build_bee.py`: qball faceted balls without pole fans, ray-cast eye domes, mitred
tube legs with flat soles, wing plates with real thickness, split_to_objects with joint pivots, Workbench check sheet with
the reference tile, EEVEE preview with hover lift). House style 11/11b.

## Measured from the reference (wingspan 1435 px = 0.15 m => ~1.0e-4 m/px; ground = leg soles at py 965)
| Feature | px | m (design) |
|---|---|---|
| wingspan (forewing tip to tip) | 1435 | 0.150 (scaled to exactly 0.150) |
| forewing (root -> apex) | 685 x 555 | 0.069 out x 0.056 up, 9-vertex outline, 4 orange cells (5/5/4/4 corners) |
| hindwing | 540 x 275 | 0.054 x 0.028, 9-vertex outline, one orange cell with the black wedge vein |
| black border | 40-95 | 4-9 mm (widest at the forewing apex), veins 2-3 mm |
| head (orange faceted ball) | 240 w x 205 h | ellipsoid 0.0122 x 0.0105 x 0.0104, 8-gon quad bands x 3 + flat caps |
| eyes | 50 dia | 6-gon dark domes r 2.6 mm, 0.6 mm proud + 0.9 mm dome |
| antennae | 20 thick, 240 long, club 60 x 40 | 4-gon r 1.1 mm, 24 mm, club r 2.4 mm |
| thorax (dark) | 235 w | ellipsoid 0.0118 x 0.0135 x 0.0125 |
| abdomen (slim, striped) | 110 thick | 6-gon loft, r 6 mm, 34 mm long, tilted 22 deg down |
| legs (dark, chunky, folded) | 35-40 thick, 175 high | 4-gon r 2.3 mm, hip in thorax -> knee out -> vertical shin, flat sole at z 0 |

## Wings (thin double-sided plates)
Plate = 2D pattern layout (outline + orange cell loops + white dot loops, scanfill with holes), mapped into the wing frame,
front sheet +0.6 mm and back sheet -0.6 mm along the plate normal (1.2 mm thick) + dark rim band. Frame: wing plane tilted
back 30 deg from vertical (faces read from the front and from above), folded back 18 deg at the root (shallow V seen from
above), tips droop back/down by 4 mm (quadratic bend). Hindwing sits 2.5 mm behind the forewing (parallel, not coplanar,
not intersecting). Root strips are sunk ~5 mm into the thorax.

## Parts (objects; pivot at the joint; root empty FMS_Butterfly on the ground under the thorax centre)
Body (thorax + striped abdomen), Head, Eye.L/.R, Antenna.L/.R, WingFront.L/.R, WingBack.L/.R, Leg_1/2/3.L/.R (as the Bee).
Rig mapping (skeleton I, 2 bones per wing): Body <- Body + Leg_*; Head <- Head + Eye.* + Antenna.*;
Wing1.L <- WingFront.L, Wing2.L <- WingBack.L (same for .R). Wing pivots at the wing root on the thorax side.

## Material class
Flat palette, own atlas `T_FarmAnimals_Butterfly_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Butterfly`.

## NOT modelled
scales/hair, proboscis, claws, vein geometry (veins are face colours), flower/ground, white dots on the body.
No armature/weights/clips.

## Convention
Lowest point z = 0 (leg soles touch the ground, like the Bee). Hover height belongs to Unity/animation; the preview lifts
the root only for the render.

## Rounds (Workbench sheet: reference | ref view, side, front, back, top, rear 3/4, front-right; EEVEE look; 128 px)
1. 794 tris, span 0.138. -> span short, head boxy 8-gon, legs spidery (knees far out) and thin.
2. Uniform scale to span 0.150 (K 1.089), head x1.12 as 10-gon x 5 rings (round), eyes r 3.0 mm, legs r 2.8 mm,
   knees pulled in; dots 4+2 -> 3+1 per side (budget).
3. Abdomen tilted 28 deg and 37 mm long, knees slightly out again. FBX re-import lost 3 tris: the concave hindwing cell
   was triangulated after the bend and duplicated a border triangle -> cells now tessellated in 2D, duplicate-face check
   added (0).
Remaining differences: abdomen mostly hidden behind the hindwings from the front (reference shows it under the wing);
wing plane leans back 30 deg (reference: almost square to the camera) so wings read from above too; white dots are a lead
request (not in the reference), front face only; legs straighter than the reference's.

## Result
798 tris (target ~350-450, over on purpose: patterned double-sided wings = 400): WingFront 128 x2, WingBack 72 x2,
Body 102, Head 96, Antenna 28 x2, Eye 12 x2, Leg_1/2/3 20 x6.
Size X 0.150 (span) x Y 0.080 x Z 0.082, body head->tip 0.069, body top 0.057, lowest z 0 (soles).
Checks: non-manifold 0, loose 0, degenerate 0, duplicate faces 0, coplanar 0, mirror 0.000000, worst gap 0, front/back
wing plates do not intersect, wings do not touch the head; eye clearance 0.44-0.90 mm.
FBX re-import: 16 meshes + root, 798 tris, 0.150 x 0.080 x 0.082, texture found in FMS_Butterfly.fbm.
Cut options if the lead wants ~450: no dots (-64), plain back face border+field (-~90), thorax 6-gon (-12), head 8-gon x4 (-36).

## Rework round 2 (independent review 3/5)
Defects: abdomen not visible in the preview; left wing pair tilted back and foreshortened (18 deg backward sweep).
Changes: sweep 0 (both pairs symmetric); forewing plane leans back 30 deg, hindwing plane 10 deg the other way (lower edge
back) so the abdomen shows under it; hindwing 5.5 mm behind the forewing at the root; wing roots, thorax and head raised
5/1.5/2 mm. Abdomen (still part of Body): 6-gon loft r 8.0 x 7.8 mm (pre-scale), 42 mm long, 26 deg down-back, dark with
2 orange bands + dark tip cone; lowest abdomen point z 0.0035 (legs carry z 0). Leg_3 moved 2.5 mm forward. Dots raised
0.2 mm (removes a coplanar false positive). Preview: front 3/4 from the butterfly's right (-X) like the reference,
(-0.55, -1, 0.14), 120 mm lens; check sheet uses the same lens.
Interpretation: "20 deg dihedral" read as the V the wings form seen from the front (forewing axes rise ~25 deg); a true
near-horizontal 20 deg dihedral would show the wings edge-on from the reference angle. Not done: literal horizontal pose.
Numbers: wing pair screen area L/R ratio 0.83 at the reference angle, 0.76 in the preview (perspective only, the planes are
mirror images); abdomen rear verts visible 6/14 in the preview (rest hidden by the near legs, as in the reference).
Result: 810 tris (Body 114, rest unchanged); 0.150 x 0.065 x 0.075 m; all checks 0, x10 coplanar 0, duplicates 0.

## Preview round 3 (preview only, mesh/FBX/blend/atlas untouched)
Pack-standard preview via animal_render.preview: `-- INS-02 std_preview`, view (0.34, -1, 0.18) = 19 deg yaw from the front-left,
~10 deg above the ground, 40 mm, standard sun 48 deg / fill / sky + horizon, no hover. Wing pair screen-area ratio 0.64
(40 mm perspective), abdomen shows as a striped sliver behind the far legs (more yaw hides the far antenna).

## Rig + clips (rig_butterfly.py + butterfly_clips.py + butterfly_gif.py; copy of the Bee insect rig, mesh unchanged)
Final export = `rig_butterfly.py -- INS-02 export` (build_butterfly.py export would overwrite the FBX with the static mesh).
Skeleton I, 15 bones: Root -> Body -> {Head -> {Antenna.L/.R}, WingFront.L/.R, WingBack.L/.R, Leg_1/2/3.L/.R}; 16 parts rigid
(weight 1.0, Eye.L/.R -> Head), armature 'Rig'. No Abdomen bone (abdomen is part of Body).
Wing kinematics: the plates are frontal, so a flap about the body axis would spin them in-plane. "Closing" = one rotation
R_close (115 deg about axis (0.55, -0.16, 0.82) for .L, mirrored for .R) that maps the forewing frame to a sagittal resting
frame (forewing up, hindwing back); open<->closed = fraction k of that axis-angle. Fore+hind wing of a side move as one rigid
pair (hindwing rotated about the forewing pivot) so the 5.5 mm plate gap never closes. k > 0.85 crosses the hindwings ->
closed pose k = 0.82.
Clips (30 fps, NLA takes): Butterfly_Fly 1.0 s / 30 f (Root +0.06 m, 2 soft flaps k -0.08..0.82, body bob 7 mm + drift 6 mm,
pitch -6+-3 deg, legs tucked back 25-34 deg, antennae trail); Butterfly_Perch_Idle 4.0 s / 120 f (open hold, close 1.2 s,
closed hold with 2.5 % tremble, open 1.2 s; head yaw 6 / nod 3, antennae; Root/Body still, 6 feet on z = 0).
Metrics: loop closure 0.000 deg / 0.000 m; limit violations 0; Fly lowest 0.048 m; Perch lowest 0.000, 6 feet on ground,
foot slip 0.000; new overlaps vs rest only at the wing roots buried in the thorax (3-6 face pairs, not visible).
FBX re-import: 15 bones, 16 meshes, 810 tris, takes 30/120 f, vertex error 0.0 m, texture found. Events: WingFlap x2 (Fly).
GIFs via butterfly_gif.py (Fly: shadow kept in frame, sun 12 deg).
