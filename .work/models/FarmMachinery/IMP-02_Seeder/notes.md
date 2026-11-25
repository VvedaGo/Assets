# IMP-02 Seeder (`FMS_Mach_Seeder`) — builder notes (Э7 series batch 1, 2026-11-24)

Look rounds in the live Blender (scene/collection `IMP-02_Seeder`), final export headless (same fingerprint).

## Layout (Unity, m)
- bbox X ±1.52 (marker arms), Y 0..1.685 (marker discs), Z ±0.92 (lug front / press wheels).
- Shared linkage frame: lugs X ±0.45, pins at (Y 0.60, Z 0.85) → `Link3P_Front` (0, 0.60, 0.85); top bracket (Y 1.12, Z 0.64);
  red mast legs, cross bar at Y 0.85, two struts to the front beam.
- Tool bar (front beam Z 0, rear beam Z −0.50), hopper 2.80 × 0.90 top / 2.50 × 0.60 bottom (Y 0.75–1.35, chamfer 0.06),
  straps, orange reflectors; 9 coulters; press row (bar Z −0.735, 9 press wheels Ø0.40).
- Moving: `Lid` hinge (0, 1.35, −0.45) axis X; `Marker_L/R` hinge (∓1.47, 0.70, −0.65) axis Z (folded up);
  `Wheel_L/R` Ø0.70 × 0.18 at (∓1.34, 0.35, −0.25).

## Deviations
- Coulters at X ±1.12 step 0.28 (spec ±1.32 step 0.33 would cut into the wheels at X 1.25..1.43).
- Top bracket at Y 1.12 (spec mast ~1.10; reference apex near the hopper top): a higher bracket collides with the TRC-01
  top link (tried 1.28 → 22 overlapping face pairs); 1.12 clears it by 1.5 cm.
- Mast cross bar at Y 0.85 so it clears a tractor drawbar fork when docked.
- Mast red (spec shared frame) — the reference shows it grey.
- Markers at X ±1.47 → bbox ±1.52 (spec ±1.50).

## Rounds: 3. Remaining differences vs reference: mast colour; wheels a bit smaller than the reference look; coulters
slightly shorter.

## Checks
Frame 1204, Lid 100, Marker_L/R 88 each, Wheel_L/R 432 each → 2344 / 3500 (67 %); LOD1 1172. Non-manifold/loose/
degenerate 0, coplanar 0, gaps 0, tyre→frame 0.050. Re-import 14 nodes OK. Mating on TRC-01 Link3P_Rear: error 0,
0 overlapping face pairs, 9 mm to the TRC-01 linkage.
