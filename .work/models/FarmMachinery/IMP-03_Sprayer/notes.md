# IMP-03 Sprayer (`FMS_Mach_Sprayer`) — builder notes (Э7 series batch 1, 2026-11-24)

Look rounds in the live Blender (scene/collection `IMP-03_Sprayer`), final export headless (same fingerprint).

## Layout (Unity, m), rest = Transport
- bbox X ±1.25, Y 0..3.00 (dome), Z ±2.911 (eye front / rear boom carrier).
- `Hitch_Front` (0, 0.55, +2.80) = shared drawbar eye centre (octagonal Ø0.24, hole 0.08); `PTO_Front` (0, 0.70, +2.95)
  = Hitch + (0, 0.15, 0.15); PTO stub on the drawbar Z 2.38..2.50.
- Tank: 16-segment cylinder, apothem 0.80 (Ø1.60), Z −1.95..+1.45 (3.40 long), chamfered ends, lower facets dark red,
  2 straps, grey octagonal filler dome (top 3.00), orange beacon; rear ladder (slot 9) with platform.
- `Boom_L/R` hinge (∓1.10, 1.90, −2.60) axis Y: lattice truss (rails 0.07, diagonals 0.06) folded forward along the tank
  at X ±1.20, big orange tip blocks at the tank front; rear carrier posts with pivot pins, front rest posts.
- `Wheel_L/R` Ø1.30 × 0.40, 16 lugs, at (∓1.05, 0.65, −0.50).
- Work pose = booms ±90° about Y (checked: span 10.46 m, no collisions); check render IMP-03_check_work.png.

## Deviations
- Tank Ø1.60 × 3.40 (spec Ø1.80 × 3.00) and boom tips at the tank front (boom 4.05 m, spec 4.90) — reference proportions
  (PIPE-04); Work span 10.5 m instead of 12.0.
- Dome grey (reference), spec 5/6 with a grey lid.
- bbox length 5.82 (spec 5.60): eye centre at +2.80 per spec plus the eye radius, mirrored at the rear for the root.

## Rounds: 2. Remaining differences vs reference: ladder placement simplified; the drawbar has no cross brace.

## Checks
Chassis 900, Boom_L/R 244 each, Wheel_L/R 480 each → 2348 / 5000 (47 %); LOD1 1174 (Chassis_Low1 447). Non-manifold/
loose/degenerate 0, coplanar 0, gaps 0. Re-import 13 nodes OK.
Mating: on TRC-01 Hitch_Rear error 0, PTO_Front = PTO_Rear (0.0000 m), but **25 overlapping face pairs**: the shared
drawbar eye (Ø0.24) hits the TRC-01 fork front plate (only 0.07 m ahead of its pin, eye needs 0.12) — TRC-01 fix needed
(move its fork front plate to ≥ 0.125 ahead of the pin, like TRC-02). On TRC-02 Hitch_Rear: error 0, PTO 0, 0 overlaps.
