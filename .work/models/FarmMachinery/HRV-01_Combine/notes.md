# HRV-01 Combine (`FMS_Mach_Combine`) — builder notes (Э7, 2026-11-24)

Built by Claude Opus; look rounds in the owner's live Blender 5.2 via MCP (own scene + collection `HRV-01_Combine`),
source of truth `build.py` (`-- HRV-01 build|export`). Geometry in Unity coordinates, mapped to Blender as (-x, -z, y).
Shared helpers (pack wheel, tbox, rod, render, verify) are verbatim copies from TRC-01 `build.py`. Shared atlas
`T_FarmMachinery_Red_BaseColor.png` / `M_FarmMachinery_Red` (byte-identical, md5 eb6768e2…). Header ATT-03 is not in
this FBX (nested prefab on `Feeder_Front`).

**Export was done headless**, not from the live session: in the live Blender the object names `Body`, `Wheel_*`,
`Door_L`, `Hitch_Rear`, `Seat` already belong to TRC-01 (Blender names are global), so live objects got `.001`.
The headless export has the exact names; its geometry fingerprint equals the live round-2 build.

## Layout (Unity, m)
- Root on the ground at the footprint centre; bbox X ±1.80 (drive tyres), Y 0..4.00 (beacon), Z −4.20 (hitch fork)
  .. +4.20 (feeder front face).
- Wheel_FL/FR Ø1.80 × 0.90 at (∓1.35, 0.90, +1.20), 16 lugs 0.12; Wheel_RL/RR Ø1.10 × 0.50 at (∓1.00, 0.55, −3.00),
  12 lugs 0.088. Origin at the centre, spin axis X, rot 0.
- Body: dark lower section ±0.85 between the drive wheels (Y 0.70–1.95), red upper section ±1.30 above them
  (Y 1.90–2.42), tank ±1.40 Y 2.40–3.40 with a 0.25 sloped cover and two hatch lids, engine ±1.25 Z −4.00..−1.50 with
  slatted side grilles, exhaust on the right, rear lights; rear steering axle on a pivot post; hitch fork.
- Cab Z 1.50..3.05, ±0.87, floor (nose) 1.98–2.18 with headlights, glass to 3.42, cream roof stripe, roof to 3.62,
  beacon to 4.00, mirrors both sides. `Door_L` hinge (−0.86, 2.77, +2.85), axis Y.
- `Feeder` pivot (0, 2.00, +1.60), axis X: housing 1.60 wide from inside the body to the interface frame
  1.60 × 0.90 (0.10 walls, front face Z +4.20) around a dark throat. `Feeder_Front` (child) (0, 0.80, +4.20).
- `Auger_Unload` pivot (−1.25, 3.45, −1.40), axis Y, folded along the LEFT top edge of the tank, tube Ø0.40 to the tip
  at Z +2.20 beside the cab, spout down, orange stripe; `Auger_Out` (child) (−1.25, 3.25, +2.20).
- `Hitch_Rear` (0, 0.55, −4.13) on the vertical fork pin; `Seat` (0, 2.45, +2.25).

## Deviations / notes
- Hitch_Rear Z −4.13 instead of −4.20: the empty sits on the fork pin (drawbar-eye contract) and the fork plates end at
  Z −4.20 so the bbox stays −4.20..+4.20 with the root at its centre.
- The reference shows the unloading auger along the RIGHT top edge of the tank; the spec (pivot X −1.25, Auger_Out)
  puts it on the LEFT — kept the spec (functional contract). Biggest visual difference vs the reference.
- Auger tube Ø0.40 (spec ~0.45) so it does not dominate the ¾ view.
- No right door (reference shows only the left side).

## Rounds (reference angle: front-left ¾, ~25° up, 70 mm)
1. Proportions and parts match; posts coplanar with the roof stripe fixed before the round. Auger reads heavy.
2. Auger thinner (Ø0.40). Remaining differences are nitpicks → exported.

## Checks (final)
Body 736, Feeder 76, Auger_Unload 112, Door_L 72, Wheel_FL/FR 480 each, Wheel_RL/RR 432 each → 2820 / 12000 (24 %);
LOD1 1410 (make_lod1.py, `<part>_Low1` root children). Non-manifold / loose / degenerate 0, coplanar 0, gaps 0.
Tyre → body ≥ 0.050 (front) / 0.080 (rear), wheels touch only their axles. FBX re-import: 21 nodes, 4230 tris
(LOD0 + LOD1), all pivots/empties at the design positions, texture found. Headless export = live build (fingerprint).
Feeder interface with ATT-03: see ATT-03 notes (error 0, overlaps 0, 1 mm face gap).

## Fix 2026-11-24 (orchestrator decision, CATALOG item 6): hitch plate for the shared eye Ø0.24
- `hitch_plate`: Z −4.005..−3.905 (0.125–0.225 ahead of the fork pin, `HITCH[1] + 0.125 / + 0.225`); was Z −4.02..−3.92
  (only 0.11 ahead — TRL-04's shared eye overlapped it by ~1 mm, 10 face pairs). Rear face 5 mm behind the engine rear face
  (−4.00), no coplanar faces. Same rule as the TRC-01 fork fix.
- Unchanged: Hitch_Rear (0, 0.55, −4.13), fork plates (end at Z −4.20), all other parts, pivots and points; bbox
  3.60 × 4.00 × 8.40; tris 2820 (LOD1 1410 via make_lod1.py). Checks: non-manifold / loose / degenerate 0, coplanar 0,
  gaps 0. FBX re-import: 21 nodes, points at the design values, texture found. Atlas md5 eb6768e2… unchanged.
- Preview: re-rendered image pixel-identical to the old one (the plate is hidden under the engine in the ¾ front view) →
  the original preview file was kept byte-identical (md5 91a88e9a…).
- Mating after the fix (temporary copies, removed): TRL-04 `Hitch_Front` on `Hitch_Rear` error 0, 0 overlapping face
  pairs, eye 10.0 mm from the plate; ATT-03 `Feeder_Rear` on `Feeder_Front` error 0, 0 overlaps, frames 1.00 mm apart;
  ATT-04 `Feeder_Rear` on `Feeder_Front` error 0, 0 overlaps, 1.0 mm.
