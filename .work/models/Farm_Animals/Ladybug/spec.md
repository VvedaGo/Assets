# INS-03 Ladybug - spec (Farm Animals extension, skeleton I parts, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/INS-03.png` (1536x1024). Chubby ladybug standing, front 3/4 view from its
front-left (face + left (+X) flank), ~25 deg above. Big flat facets, red high dome of two elytra with a groove, big dark
hexagon spots, wide black octagon head with 2 dark-brown octagon eyes, elbowed club antennae, 6 chunky black legs.
Catalogue: FARM_ANIMALS_PACK.md 5.5 INS-03 (enlarged to 0.05 m, deliberate deviation from TECH-01; catalogue 200 tris,
lead brief ~800, up to ~1100), section 4 (look rules), 6 (skeleton I), 7 (clips Walk, Idle, Open_Wings later).
Anchors followed: INS-01 Bee (`../Bee/build_bee.py`: Part/qball/tube_rings, split_to_objects with joint pivots, COM
shift, Workbench sheet + EEVEE preview), Mouse (tiny-model coplanar: shared check + x10 copy + coplanar_true),
Hedgehog (domed back idea). Shared `Tools/blender` and `_common` imported read-only.

## Measured from the reference (head width 480 px = 0.021 m -> ~4.4e-5 m/px on the head plane)
| Feature | px | model (m) |
|---|---|---|
| body length head front -> dome back | (catalogue) | 0.050 |
| dome width / height above rim | ~0.6 height:width | 0.036 wide, 0.022 above the rim (rim z 0.0095, top z ~0.031) |
| head (octagon block) | 480 w x 370 h | 0.021 x 0.016, z 0.006..0.022, front face y -0.0255 |
| eyes (octagons, brown) | ~55 px | r 0.0019 (dia 3.8 mm, ~1.4x ref for 128 px), x +-0.0050 |
| antennae | 40 px thick, knob 70 px | r 0.0009, club r 0.0015, elbow ~6.5 mm above the head |
| legs | ~78 px wide | 6-gon r 0.0020 (3.5 mm across flats), knee r 0.0021, foot flare r 0.0023 |
| spots | biggest ~22 % of dome width | hex circumradius 0.0042 / 0.0034 / 0.0032, 3 per half (6 total) |
| split groove | thin dark line | gap 0.5 mm + 0.45 mm bevel strips each side, 0.6 mm drop |

## Construction
Elytra: each half = constrained Delaunay (mathutils delaunay_2d_cdt) on an azimuthal domain half-disc, mapped to a
superellipsoid dome (theta 0..95 deg, rim curls under = overhang). Spots are constraint hexagons computed in the
tangent plane (regular in 3D) and flattened to one plane = crisp flat hex facets; split edge row lowered + bevel row
= clean groove; rim lip band + flat underside cap + flat split wall close the solid. Red shade by facet normal (4).
Body: 10-gon quad-band ellipsoid (black), Head: octagon loft with front bevel, Eyes: 8-gon proud discs with bevel,
Antennae: 6-gon elbow tubes with club, Legs: 6-gon hip -> knee -> flared foot, flat sole on z = 0,
Wings: thin 4-vert-section plates folded under the elytra, tip 2-3 mm out behind the rim.
Pivots: Elytra at the hinge on the top-front of the split; legs at hips; antennae at the base; head at the neck.

## Material class
Flat palette `T_FarmAnimals_Ladybug_BaseColor.png` (256 px 4x4), `M_FarmAnimals_Ladybug`:
0 red top #E25B44, 1 red #D4432F, 2 red low #C23A28, 3 red rim #A5301F, 4 spot #3A2E2C, 5 spot low #2F2523,
6 groove #7E2418, 7 elytra underside #6E2016, 8 head #3A2E2C, 9 head top #463836, 10 eye #4A2A20, 11 eye rim #241815,
12 body/legs #3A2E2C, 13 legs dark #2C2321, 14 wing #CFC7BC, 15 wing edge #A39A8E.

Final palette change (round 3): cell 8 = eye front cap #653A29 (head uses cell 12, same #3A2E2C); red low/rim lifted
to #CB3D2B / #B5362A (round 2).

## Rounds (Workbench sheet: ref | ref view, side, front, back, top, rear 3/4, front-right + 128 px; EEVEE look)
1. 996 tris, all checks 0. Legs tapered to points (uniform mitre bulge at the knee, sole narrower than the ankle); view
   too high; front/rear spots small, little black underbody visible. -> exact mitre (stretch only in the bend plane),
   leg radii 2.1/2.2/2.3/2.5 mm with near-vertical shins, spots 3.8/4.3/3.7 mm, body lower/wider, view lowered.
2. 50 mm lens exaggerated the head and the head was boxy; wing tip read as a spike; lower reds too brown. -> 70 mm lens,
   double front bevel on the head (rounder octagon), blunt 4-station wing tip, lighter low/rim reds, antennae r 1.0 mm,
   club 1.6 mm.
3. View more frontal like the reference (face ~35 deg off camera); eyes unreadable at 128 px (#4A2A20 on #3A2E2C) ->
   lighter brown front cap with the #4A2A20 bevel and a darker rim band; wing tip lowered under the rim.
4. (cheap fix) near antenna read as a nail from the 3/4 view -> elbow leans outward, club points out/forward.
Remaining nitpicks: from the reference angle 3 spots read (ref shows 4), spot hexes slightly smaller than the
reference's; the reference camera is a bit lower, so its dome looks taller; underwing edge only visible from behind.

## Polish round 2 (independent review 4/5: long thin splayed legs, shell high; few/small spots)
- Everything except the legs lowered by DZ = 2.0 mm: rim z 0.0095 -> 0.0075, dome top 0.0314 -> 0.0294, head z centre
  0.012, body bottom cap ~0.003. Legs rebuilt in final coords: lower segment (knee -> sole) 6.6 -> 4.0 mm, knees just
  outside the rim (x 0.0160 / 0.0196 / 0.0172), radii 2.1/2.2/2.3/2.5 -> 2.5/2.6/2.8/3.0 mm (+19-24 %).
  Leg clearance to the elytra: no intersection, min 0.52-0.54 mm.
- Spots: 4 per half (8 total, mirror-symmetric): circumradius 4.2 (top-front), 5.2 (flank, dia ~10.4 mm = 0.25x the
  41 mm shell length), 4.2 (rear flank), 4.5 mm (new, front flank). 4 spots read from the reference angle.
- NEW Elytra hinge pivots: Elytra.L (+0.0003, -0.0146, 0.0193), Elytra.R (-0.0003, -0.0146, 0.0193) (was z 0.0213).
  Head pivot (0, -0.0126, 0.012); Wing.L/.R (+-0.0035, -0.0026, 0.0088).
Result after polish: 1028 tris (unchanged per part), size X 0.047 x Y 0.052 x Z 0.029, lowest z 0; all checks 0
(non-manifold, loose, degenerate, coplanar real/x10/x10 triangulated/true), mirror 0.000000, worst gap 0;
FBX re-import 16 meshes + root, 1028 tris, dims 0.047 x 0.052 x 0.029, texture found.

## Result (before polish round 2)
1028 tris (target ~800, cap 1100): Elytra 166 x2, Body 76, Head 76, Antenna 68 x2, Eye 44 x2, Leg_1/2/3 44 x6, Wing 28 x2.
Size: X 0.046 (feet; dome 0.036) x Y 0.052 (head+eyes -> wing tip; head front -> dome back 0.050) x Z 0.031 (dome top),
rim z 0.0095, lowest z 0 (soles). Pivot: root on the ground under the centre of mass; Elytra at the hinge
(+-0.0003, -0.0146, 0.0213); legs at hips; head at the neck (0, -0.0126, 0.014); wings at the root.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar 0 (real scale), 0 (x10),
0 (x10 triangulated), coplanar_true 0.
FBX re-import: 16 meshes + root, 1028 tris, dims 0.046 x 0.052 x 0.031, min z 0, texture found in FMS_Ladybug.fbm (256x256).

## Deviations
- Enlarged to 0.050 m body length (pack 5.5, documented TECH-01 deviation).
- 1028 tris vs catalogue 200 / brief ~800 (brief allows ~1100).
- Eye front cap #653A29 (lighter than #4A2A20) for 128 px readability; #4A2A20 kept on the eye bevel.
- 6 spots (3 per half, mirror-symmetric).

## NOT modelled
mouthparts, claws, pronotum white marks, hairs, spot texture, ground/leaf. No armature/weights/clips.

## Rig + clips (skeleton I, rig_ladybug.py + ladybug_clips.py + ladybug_gif.py; copy of the Bee rig, mesh unchanged)
Final export = `rig_ladybug.py -- INS-03 export` (build_ladybug.py export would overwrite the FBX with the static mesh).
15 bones: Root -> Body -> {Head -> Antenna.L/R, Elytra.L/R, Wing.L/R, Leg_1-3.L/R}; 16 parts rigid (Eye -> Head).
Legs are one rigid part each: a leg points at its sole target by the smallest rotation about the hip + a translation along
the hip->sole line (hip ball slides <= 2 mm inside the body), so planted soles are exact (pure yaw cannot keep a forward leg's
sole on a straight line).
Idle 3.0 s/90 f: antennae sweep + one flick each, head yaw 6 / nod 3, body breath, feet planted (slip 0).
Crawl 16 f: tripod gait (L1 R2 L3 / R1 L2 R3), step 5 mm, root speed 0.019 m/s, lift 1.1 mm, body sway/roll; events Footstep x2.
Fly 1.0 s/30 f: Root +0.045 m, body 22 deg nose-up, elytra open as hard shells (rear up 38, out 28, roll 12 deg, hinges 0.8 mm
  apart), hind wings unfold 78 deg sideways and flap 5x (+12 +-34 deg), legs folded back/hanging; events WingFlap x5.
Metrics: closure 0.000 deg / 0.000 m, lowest -0.05 / -0.23 mm / +29.8 mm, Crawl slip 0.0 %, 0 limit violations; new
overlaps vs rest: Crawl swing knees touch the elytra underside (7-11 face pairs, under the rim), Fly Wing/Leg_2 4 pairs.
FBX re-import 15 bones, 16 meshes, 1028 tris, vertex error 0.0. GIFs: ladybug_gif.py --view 0.85 -1.0 0.30 --fill 0.62
(Fly: --view 0.85 -1.0 0.22 --fill 0.80, sun 8 deg so the shadow stays under it).
