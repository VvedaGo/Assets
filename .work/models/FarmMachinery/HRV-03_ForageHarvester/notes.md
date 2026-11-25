# HRV-03 ForageHarvester (`FMS_Mach_ForageHarvester`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `HRV-03_ForageHarvester`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes) + HRV-01 cab/door pattern. Shared atlas
md5 eb6768e2…; body colour only in cells 5/6 → Green/Blue are atlas swaps (same mesh/UV).

## Layout (Unity, m; root on the ground at the bbox centre, no shift)
- bbox X ±1.75 (drive tyres), Y 0..4.877 (spout arch), Z ±4.00 (header front / engine rear); size 3.50 × 4.88 × 8.00.
- `Body` (static): dark lower body between the drive wheels and under the engine, drive axle, rear steering post +
  axle; red platform over the drive wheels (Y 1.86–2.30) carrying the cab; feed nose down to the header hinge; engine
  compartment Z −4.00..−0.20 (dark lower band, red block to 2.90 with 0.15 top chamfer), slatted side grilles, exhaust
  (left, 8-seg slot 11), rear lights; grey spout turret ring Ø0.90 on the engine top; cab Z +0.60..+2.40, ±0.85, red
  base with 2 headlights, opaque glass, dark posts, red chamfered roof to 3.60, orange beacon, mirrors; left step ladder.
- `Door_L` pivot (−0.86, 2.89, +1.65) = front vertical edge, axis Y.
- `Header` pivot (0, 1.00, +2.30) = rear hinge, axis X: red tray (floor, back wall, chamfered side walls X ±1.50..1.65,
  rear top beam, front lip), 10-sided grey pickup drum Ø0.52 at (0.62, +3.40), 11 curved tines; Y 0.15..1.30,
  Z +2.30..+4.00, width 3.30. Built in (no Feeder points).
- `Spout` pivot (0, 2.90, −0.60), axis Y: 8-sided tube 0.55 rising from the turret to Y 4.6 and arching back over the
  engine (5-point mitred path), grey collar, 2 grey rim bands. Swing ±90° checked: only the collar/turret contact.
- `Spout_Tip` (child of Spout) pivot (0, 4.30, −3.00), axis X: grey hood pointing down/back, hinge rod.
- `Spout_Out` (child of Spout_Tip) (0, 3.85, −3.50); `Seat` (0, 2.65, +1.45).
- Wheels: FL/FR Ø1.80 × 0.75, 16 lugs 0.12 at (∓1.375, 0.90, +0.90); RL/RR Ø1.20 × 0.55, 12 lugs at (∓1.20, 0.60, −2.60).

## Deviations from the spec
- Spout much taller: arch top Y 4.877 (spec silhouette ~4.0), `Spout_Tip` hinge (0, 4.30, −3.00) instead of
  (0, 3.65, −3.00), `Spout_Out` (0, 3.85, −3.50) instead of (0, 3.40, −3.60). The reference shows the spout rising
  well above the cab (≈ 5 m by pixel measure; cab roof 3.6) — it is the silhouette feature (PIPE-04: reference wins).
  Height 4.88 vs catalogue 4.0.
- Cab posts / door frame dark (slot 11) like the reference (spec lists 5 / 12 / 3); exhaust on the left (reference).
- **LOD1 is made inside build.py, not by make_lod1.py**: `Spout_Out` is a 3rd-level child (root > Spout > Spout_Tip >
  Spout_Out). `pack_common.export` compensates the Blender 5.2 FBX nested-child bug only for 2nd-level children; the
  re-import put Spout_Out at (0, 2.30, −5.05). Export/re-import tests gave the general rule (parents first):
  `L'(o) = L'(parent)^-1 · G · L(parent) · L(o)`. build.py `export` therefore adds LOD1 with a verbatim copy of
  `make_lod1.lod1_for` (ratio 0.5, `<part>_Low1` direct root children, palette re-snap) and exports with that rule.
  **Do not run make_lod1.py on this model** (it re-exports through pack_common.export and breaks Spout_Out again).
  Proposal for Tools: generalise the nested fix in `pack_common.export` with the rule above.

## Rounds: 3
1. Spout too low (hidden behind the cab — reference shows a tall arch); coplanar posts/roof, lights/engine.
2. Tall arch spout, exhaust to the visible side; check render matches the reference.
3. Live round; export; Spout_Out re-import error found and fixed with the 3-level export rule.

## Remaining differences vs reference
- Reference arch reaches slightly further back over the engine; reference engine front slopes down toward the cab.
- Reference shows a grey block at the rear (hitch-like); not modelled (no hitch points in the catalogue).

## Checks (final)
Body 704, Door_L 72, Header 448, Spout 176, Spout_Tip 72, Wheel_FL/FR 480 each, Wheel_RL/RR 432 each → 3296 / 11000
(30 %); LOD1 1640. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0 (mirror X by design: door, exhaust, steps).
Tyre → body ≥ 0.046 m, wheels touch only their axles. FBX re-import: 21 nodes, all pivots and points at the design values
(Spout_Out (0, 3.85, −3.50) under Spout_Tip), texture found. Headless export = live build (fingerprint identical).
No mating (no hitch / PTO / feeder points in the catalogue).

## Fix 1 (2026-11-24, owner decision: detachable header) — done
- Built-in pickup `Header` removed (now ATT-05 Header_Pickup, same geometry). The feed nose prism of `Body` is replaced by a
  moving `Feeder` part (HRV-01 feeder pattern): inclined channel from inside the front body (hinge axis X at design
  (Y 1.40, Z 1.25)) down to the interface frame 1.60 × 0.90 (0.10 walls, dark throat 0.25 deep), front face at design Z 2.20 —
  i.e. where the old header's back wall was, so HRV-03 + ATT-05 looks exactly like the former model.
- `Feeder_Front` (child of Feeder): exactly the HRV-01 interface — opening 1.60 × 0.90, Y 0.80, +Z forward.
- Steps narrowed from X −1.00..−0.70 to −1.00..−0.82 (the lowest step cut the feeder channel); nothing else changed in Body,
  cab, Door_L, Spout, Spout_Tip, Spout_Out, Seat, wheels.
- Without the header the bbox front is the cab mirror (design Z 2.52): bbox Z −4.00..+2.52 → the root is re-centred
  (+0.74 in Z). Final (Unity): bbox 3.50 × 4.88 × 6.52; Feeder pivot (0, 1.40, +1.99), Feeder_Front (0, 0.80, +2.94),
  Body (0, 0, +0.74), Door_L (−0.86, 2.89, +2.39), Spout (0, 2.90, +0.14), Spout_Tip (0, 4.30, −2.26),
  Spout_Out (0, 3.85, −2.76), Seat (0, 2.65, +2.19), wheels FL/FR (∓1.375, 0.90, +1.64), RL/RR (∓1.20, 0.60, −1.86).
- The local nested-export workaround (in-script LOD1 + 3-level export) is removed: the fixed `pack_common.export` and the
  standard `make_lod1.py` now give Spout_Out (0, 3.85, −2.76) under Spout_Tip correctly (FBX re-import verified).
- Tris: Body 688, Door_L 72, Feeder 76, Spout 176, Spout_Tip 72, wheels 480 / 480 / 432 / 432 → 2908 / 11000 (26 %); LOD1 1452.
  Non-manifold / loose / degenerate 0, coplanar 0, gaps 0; tyre → body ≥ 0.046, tyre → feeder ≥ 0.225 m. Re-import 22 nodes.
  Headless export = live build (fingerprint identical). Preview re-rendered without header (reference camera).
- Mating (temporary copies, removed): ATT-05 / ATT-04 / ATT-03 `Feeder_Rear` on `Feeder_Front`: error 0, 0 overlapping face
  pairs, frames 1.0 mm apart; header roots at Feeder_Front + (0, −0.80, +0.9005 / +1.30 / +1.05); lowest points 0.15 / 0.10 /
  0.10 m. Assembly render with ATT-05: %TEMP%/farmmachinery_check/HRV-03/HRV-03_assembly_ATT-05.png (matches HRV-03.png like
  the former built-in version).
