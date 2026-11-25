# ATT-05 Header_Pickup (`FMS_Mach_Header_Pickup`) — builder notes (owner decision 2026-11-24)

Former built-in HRV-03 `Header` (geometry accepted in review b2), made detachable. Look check in the owner's live Blender
(own scene, removed afterwards), export headless (identical fingerprint). Shared atlas md5 eb6768e2… unchanged.

## Layout (Unity, m; design = the former HRV-03 header numbers, root re-centred, −3.1005 in Z)
- bbox X ±1.65, Y 0.15..1.30, Z ±0.8995; size 3.30 × 1.15 × 1.80 (catalogue ~3.3 × 2.0 × 1.3).
- `Frame`: red tray floor, back wall, chamfered side walls, rear top beam, front lip (unchanged code) + rear adapter: interface
  frame 1.60 × 0.90 (outer chamfer 0.06, opening 1.40 × 0.70) on the back wall, rear face 1 mm in front of the interface
  plane, dark throat plate in the opening (ATT-03 / ATT-04 look).
- `Pickup` pivot (0, 0.62, +0.2995) = drum axis X: 10-sided steel drum Ø0.52, 11 curved tines (unchanged code).
- `Feeder_Rear` (0, 0.80, −0.9005) = centre of the adapter opening, +Z forward.

## Deviations
- Lowest point 0.15 m above the root (spec "~0.10"): the former header floor is kept unchanged (accepted geometry).
- Feeder_Rear Z −0.9005 (not a round number): root at the bbox centre with the 1 mm interface gap.
- Depth 1.80 (catalogue ~2.0).

## Rounds: 1 (geometry reused; adapter + Pickup split added). LOD1 by `make_lod1.py` (Frame_Low1 98, Pickup_Low1 172).

## Checks
Frame 196, Pickup 344 → 540 / 2500 (22 %); LOD1 270. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0. Pickup touches
the frame only where the drum ends enter the side walls (expected). FBX re-import: 6 nodes, Feeder_Rear and Pickup pivot at the
design values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On HRV-03 `Feeder_Front`: error 0 / 0°, root = Feeder_Front + (0, −0.80, +0.9005), 0 overlapping face pairs, 1.0 mm.
- On HRV-01 `Feeder_Front`: error 0 / 0°, 0 overlapping face pairs, 1.0 mm (fits HRV-01 as well).
- On TRL-04 `Header_Rest` (fit only): 0 overlaps, but the header is only 3.30 m long — it sits over the middle saddle only
  (saddles 2.2 m apart) and 5 cm above it (Header_Rest assumes a header lowest point of 0.10 m; ATT-05's is 0.15 m). Usable as
  a display pose; a dedicated rest point would be needed for a snug fit.
