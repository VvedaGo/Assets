# PET-01 · seated collie

The standing dog supplied the skull, cheek tufts, jaw, eye discs, nose, folded-ear construction and the original white/rust/black palette. The head group is scaled to 79% of the standing build, pitched 2° and turned 9° toward the front-left view. The mane uses shortened tufts and the ear tips fold farther down. The pelvis, spine, neck, bib, legs and three-piece tail are new faceted lofts with closed caps and buried overlaps. The mesh has 28 separately named parts under a ground-level root. Blender uses metres, +Z up and −Y forward. The pack exporter bakes Y up and −Z forward for FBX at scale 1.

The pelvis-to-shoulder line rises about 60°. The rump and all four paws touch the ground. Narrow tapered forelegs run about 8° forward under the breast, with the elbows tucked in. The rear feet sit slightly behind and outside the forefeet, with much less white above the toes than the folded standing mesh. The rounded haunches carry the seated silhouette, the chest bib drops nearly straight down, and the tail lies along the ground to the dog's left. The comparison sheet uses frame 0 of the existing sit GIF.

The short muzzle and angular ear folds still read closer to the current standing mesh than to the softer reference. Hard faceted seams can be seen at the haunch and at the tail base. The rig transfer and Unity import were outside this static Blender check.

## Verification

Blender 5.2 headless build completed successfully. The pack checks returned 0 non-manifold edges, 0 loose vertices, 0 degenerate faces and no component contact gaps. The saved Blender file reopened with 28 meshes and a packed 256 × 256 flat atlas. Each triangle samples one of the 16 cell centers. The FBX round-trip preserved all mesh names and vertex positions to within approximately 0.1 micrometre. The four 1000 × 625 meadow views and the comparison were reviewed visually.

## Transfer to the Generic rig

The table records each mesh origin and XYZ Euler rotation relative to the ground root in Blender coordinates. Imported Unity positions map from Blender (x, y, z) to (x, z, −y). Mesh names carry the `Dog_Sit_Codex_` prefix. The Euler values describe the part frames shown here, with approximate rest-axis references on the rebuilt lofts. Use the origins as pose targets and derive the actual pose-bone rotations in the rig's rest and parent bases. Recompute the limb and spine rotations from adjacent target joints and keep the rig's calibrated roll and bend plane. The torso, rear leg proportions and paw geometry differ from the standing mesh, so matching all contacts will require retargeting or geometry adjustments. Eyes and nose are head attachments.



2056 tris. Width × length × height 0.7249, 0.8324, 0.9772 m. FBX re-import maximum world vertex error 1e-07 m.

| Part | Location XYZ (m) | Rotation XYZ (°) | Tris |
|---|---:|---:|---:|
| Root | 0, 0, 0 | 0, 0, 0 | 0 |
| Pelvis | -0.0132, 0.1533, 0.1680 | -63.2679, 0.0000, 0.0000 | 76 |
| Spine1 | -0.0132, 0.0843, 0.3050 | -58.3303, 0.0000, 0.0000 | 76 |
| Spine2 | -0.0132, -0.0107, 0.4590 | -58.3925, 0.0000, 0.0000 | 76 |
| Neck1 | -0.0132, -0.0827, 0.5760 | -3.2851, 0.0000, 0.0000 | 60 |
| Neck2 | -0.0132, -0.1137, 0.6570 | -10.1915, 0.0000, 0.0000 | 60 |
| Ruff | -0.0132, -0.1747, 0.6600 | 7.7309, -0.0000, 0.0000 | 92 |
| Head | -0.0132, -0.1317, 0.7290 | 1.9754, -0.3128, 8.9946 | 260 |
| Jaw | 0.0078, -0.2618, 0.6533 | 1.9754, -0.3128, 8.9946 | 32 |
| Ear.L | 0.0881, -0.1812, 0.8871 | 1.9754, -0.3128, 8.9946 | 32 |
| Ear.R | -0.0960, -0.2103, 0.8861 | 1.9754, -0.3128, 8.9946 | 32 |
| Eye.L | 0.0870, -0.2888, 0.7912 | 1.9754, -0.3128, 8.9946 | 14 |
| Eye.R | -0.0607, -0.3122, 0.7904 | 1.9754, -0.3128, 8.9946 | 14 |
| Nose | 0.0228, -0.3597, 0.7305 | 1.9754, -0.3128, 8.9946 | 44 |
| FrontUpper.L | 0.0618, -0.1457, 0.4880 | -8.2807, 0.5324, -0.0385 | 60 |
| FrontLower.L | 0.0598, -0.1767, 0.2750 | -7.6306, 0.2717, -0.0181 | 76 |
| FrontFoot.L | 0.0588, -0.2047, 0.0660 | 0.0000, -0.0000, 0.0000 | 76 |
| FrontUpper.R | -0.0882, -0.1457, 0.4880 | -8.2807, -0.5324, 0.0385 | 60 |
| FrontLower.R | -0.0862, -0.1767, 0.2750 | -7.6306, -0.2717, 0.0181 | 76 |
| FrontFoot.R | -0.0852, -0.2047, 0.0660 | 0.0000, -0.0000, 0.0000 | 76 |
| HindUpper.L | 0.0858, 0.1373, 0.1530 | -99.6218, -28.6038, 25.2306 | 108 |
| HindLower.L | 0.1608, -0.0257, 0.1560 | -39.2321, -2.0350, 0.7253 | 76 |
| HindFoot.L | 0.1658, -0.1147, 0.0470 | 0.0000, -0.0000, 0.0000 | 76 |
| HindUpper.R | -0.1122, 0.1373, 0.1530 | -99.6218, 28.6038, -25.2306 | 108 |
| HindLower.R | -0.1872, -0.0257, 0.1560 | -39.2321, 2.0350, -0.7253 | 76 |
| HindFoot.R | -0.1922, -0.1147, 0.0470 | 0.0000, -0.0000, 0.0000 | 76 |
| Tail1 | -0.0132, 0.2533, 0.1800 | -25.9731, -11.5898, -16.6226 | 60 |
| Tail2 | 0.0408, 0.3503, 0.0630 | 20.5898, -23.7000, -91.7326 | 92 |
| Tail3 | 0.2988, 0.3403, 0.0580 | -20.5420, -74.6872, -101.2095 | 92 |
