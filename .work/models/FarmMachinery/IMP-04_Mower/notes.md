# IMP-04 Mower (`FMS_Mach_Mower`) — builder notes (Э7 series batch 1, 2026-11-24)

Look rounds in the live Blender (scene/collection `IMP-04_Mower`), final export headless (same fingerprint).

## Layout (Unity, m), rest = Transport (bar raised)
- bbox X ±0.80, Y 0..2.50, Z ±0.77.
- `Frame`: shared linkage frame (lugs X ±0.45, pins Y 0.60 Z 0.70 → `Link3P_Front` (0, 0.60, 0.70); top bracket Y 1.12 Z 0.49),
  base rails, red gearbox housing, nose block with a short PTO stub (end face 1 mm behind `PTO_Front` (0, 0.70, 0.70)),
  swing arm and hinge ear on the right, two parking stands (feet at Y 0).
- `Bar` hinge (0.73, 0.90, −0.10) axis Z: knuckle, cutter-bar housing 0.14 × 0.30 up to Y 2.45, five 8-segment discs
  Ø0.28 on the −X face (dark rims), red guard curtain behind (−Z) with four orange diagonal stripes.
- Work pose = Bar 90° about Z (Blender rot_y −90°): X −0.80..+2.33 (width 3.13 m), bar at Y 0.83..1.21.

## Deviations
- The reference shows the bar on the machine's LEFT (mirror image); catalogue ("брус вправо") and spec (hinge X +0.85,
  Work to +X) put it on the right — kept the catalogue/spec.
- Transport height 2.50 (catalogue 3.1): bar length kept for the Work width (spec priority), as the spec note predicts.
- Swing arm is part of `Frame` (spec lists it in `Bar`): an arm rotating about its own outer hinge would swing up.
- Hinge X 0.73 (spec 0.85) and parking stands so the bbox is symmetric (root at the bbox centre, Link3P at X 0).
- No part in X ±0.09, Y 0.40..0.70, Z 0.49..0.67 (TRC-01 drawbar fork when docked); the PTO stub is a 2.4 cm disc.
- Mast red (spec), grey in the reference.

## Rounds: 2. Remaining differences: mirrored side (above); bar relatively shorter; stands not in the reference.

## Checks
Frame 528, Bar 380 → 908 / 2500 (36 %); LOD1 453. Non-manifold/loose/degenerate 0, coplanar 0, gaps 0.
Re-import 7 nodes OK. Mating on TRC-01 Link3P_Rear: error 0, PTO_Front = PTO_Rear (stub faces 1 mm apart), 0 overlaps.
