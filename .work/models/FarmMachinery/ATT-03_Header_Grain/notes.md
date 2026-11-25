# ATT-03 Header_Grain (`FMS_Mach_Header_Grain`) — builder notes (Э7, 2026-11-24)

Built by Claude Opus; look rounds in the owner's live Blender 5.2 via MCP (own scene + collection
`ATT-03_Header_Grain`), source of truth `build.py` (`-- ATT-03 build|export`). Geometry in Unity coordinates, mapped to
Blender as (-x, -z, y). Shared helpers copied from TRC-01 `build.py`. Shared atlas `T_FarmMachinery_Red_BaseColor.png`
/ `M_FarmMachinery_Red`. Export done headless (in the live Blender the name `Frame` belongs to IMP-01); the headless
fingerprint equals the live round-3 build.

## Layout (Unity, m; root on the ground at the footprint centre)
- bbox X ±3.10 (end-wall stripes), Y 0.10 (cutter bar) .. 1.50 (reel top), Z −1.049 (rear frame) .. +1.05 (dividers).
- `Frame`: rear wall Z −1.02..−0.88, top 1.15 with a raised centre to 1.42 around the throat; interface frame
  1.60 × 0.90 (outer chamfer 0.06, opening 1.40 × 0.70) on its back, rear face at Z −1.049 (1 mm in front of the
  interface plane −1.05: no coplanar faces with the combine frame); dark plate inside the wall closing the throat
  (reference shows it black); sloped floor from the cutter bar (Y 0.17) to the trough (0.22) and the rear wall; end walls
  X ±2.98..3.08 with orange divider tips and stripes; cutter bar with 36 blocky fingers; reel-arm hinge posts.
- `Auger_Cross` pivot (0, 0.70, −0.45), axis X: tube Ø0.50, 8 flights Ø0.70, central paddle block Ø0.64.
- `Reel_Arm` pivot (0, 1.25, −0.70), axis X: two arms at X ±3.0 + cross brace (one object).
- `Reel` (child of Reel_Arm) pivot (0, 0.95, +0.45), axis X: 8 bars (6-sided Ø0.07), 2 octagonal spoked end discs at
  X ±2.85, axle; bar circle R 0.52 → top Y 1.505.
- `Feeder_Rear` (0, 0.80, −1.05), rot 0.

## Deviations / notes
- Auger tube Ø0.50 / flights Ø0.70 (spec tube Ø~0.55): with the spec reel (axle (0.95, 0.45), Ø1.10) a bigger auger
  would hit the reel while both rotate; swept clearance now 0.029 m.
- Throat closed by a dark plate 0.08 m inside the wall (reference shows a black throat; spec said open).
- Spec mentions `<part>_LOD1` children; LOD1 follows CATALOG item 3 (make_lod1.py `<part>_Low1` root children).

## Rounds (reference angle: front-left ¾, ~30° up, 70 mm)
1. Matches the reference layout; throat showed the background through the hole → dark plate.
2. Rear view: auger flights stuck out above the low rear wall → rear wall raised to 1.15 (round 3 confirmed).
3. Assembly on HRV-01 compared with HRV-01.png: matches (header in front, feeder, cab above). Exported.

## Feeder mating with HRV-01 (temporary copy of the exported HRV-01 .blend, removed afterwards)
Feeder_Rear → Feeder_Front position error 0.000000 m, rotations both 0; header root − Feeder_Front = (0, −0.80, +1.05)
exactly as specified; 0 overlapping face pairs between any header and combine mesh; header frame ↔ combine feeder
frame distance 1.00 mm (identical 1.60 × 0.90 rings face to face); header lowest point 0.10 m above the ground.
Assembly render: %TEMP%/farmmachinery_check/HRV-01/HRV-01_assembly_ATT-03.png.

## Checks (final)
Frame 576, Auger_Cross 280, Reel_Arm 84, Reel 468 → 1408 / 5000 (28 %); LOD1 650 (Frame_Low1 254, Auger_Cross 140,
Reel_Arm 42, Reel 234). Non-manifold / loose / degenerate 0, coplanar 0, gaps 0. Reel touches only its arms; FBX
re-import: 10 nodes, 2078 tris (LOD0 + LOD1), Reel nested under Reel_Arm at (0, 0.95, 0.45), Feeder_Rear at
(0, 0.80, −1.05), texture found. Headless export = live build (fingerprint).
