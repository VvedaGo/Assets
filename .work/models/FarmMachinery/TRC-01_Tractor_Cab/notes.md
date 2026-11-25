# TRC-01 Tractor_Cab (`FMS_Mach_Tractor_Cab`) — builder notes (Э7, 2026-11-24)

Built by Claude Opus in the owner's live Blender 5.2 via MCP (own scene + collection `TRC-01_Tractor_Cab` >
`FMS_Mach_Tractor_Cab`); source of truth `build.py` (`-- TRC-01 build|export`). Geometry in Unity coordinates, mapped to
Blender as (-x, -z, y). Wheels use the same pack wheel function as IMP-01 (copied; optional `lug_h` added, default
unchanged = 8 % of D). Shared pack atlas `T_FarmMachinery_Red_BaseColor.png` / material `M_FarmMachinery_Red`
(orchestrator note: one shared atlas layout for the pack). Body colour comes only from cells 5/6 → Green/Blue = atlas swap.

## Layout (Unity, m)
- Root on the ground at the footprint centre; bbox X ±1.20, Y 0..3.00, Z ±2.21 (rear fork plate end / front weights).
- Wheels: FL/FR Ø1.10 × 0.45 at (∓0.95, 0.55, +1.35), 12 lugs 0.088; RL/RR Ø1.70 × 0.60 at (∓0.90, 0.85, −1.00),
  16 lugs 0.10 (spec 0.06–0.10 m; the 8 % default would be 0.136). Origin at the centre, spin axis X, rot 0.
- Bonnet X ±0.42, Y 0.95–1.85, Z 0.22–2.00, 0.08 chamfer; grille with 5 bars, 2 headlights, 4 front weights.
- Cab X ±0.55 (pillars), Z −1.20..+0.30, cream base 1.28–1.40, glass 1.36–2.62, roof 2.66–2.92 (0.07 chamfer),
  beacon to 3.00. Cab is narrower than the rear tyre gap (inner tyre faces at ±0.60) so nothing intersects the tyres.
- `Door_L` (hinge axis Y at (−0.53, z +0.19), front edge), right side has a static look-alike door frame (reference).
- `Linkage_Rear` pivot (0, 0.60, −1.45), axis X, rest = lowered; lower links end in eyes at X ±0.505..0.565 with pins
  along X at (±0.45, 0.60, −2.00) (pins 0.90 apart). `Link3P_Rear` (child) (0, 0.60, −2.00); `PTO_Rear` (0, 0.70, −2.00);
  `Hitch_Rear` (0, 0.55, −2.15) on the vertical drawbar-fork pin; `Seat` (0, 1.60, −0.70).

## Deviations from the spec / notes
- Reference is a front-LEFT ¾ view (grille on the left of the image, left side with the door visible), so Door_L and
  the left steps match the spec; the exhaust is on the RIGHT of the bonnet and the beacon on the rear-left roof corner as
  in the reference (spec: exhaust beside the left pillar).
- Steps on both sides (left per spec, right for symmetry with the static right door); fuel tank on the left.
- Seat point (0, 1.60, −0.70) instead of ≈ (0, 1.25, −0.9): cab floor is at 1.40 and the cab spans Z −1.20..+0.30.
- Top link is part of `Linkage_Rear` (rotates with the arms); it touches the Body top-link bracket, not the other
  linkage pieces, so the linkage gap check reports `top_link` 0.35 (by design).
- LOD1 by `make_lod1.py` standard convention (orchestrator correction): `<part>_Low1` direct root children.
  The LOD1 bbox is 2.409 m wide (decimated rear tyres bulge 4.5 mm); LOD0 is 2.400.

## Rounds (reference angle: front-left ¾, ~45° off the nose, ~25° up, 70 mm)
1. Camera was front-right (mirror of the reference); docking with IMP-01 OK. Coplanar pairs fixed, tyre clearances
   raised to ≥ 0.05 (front fender r 0.645, rear 1.02, cab base ±0.545), lower step attached.
2. Front-left camera: matches the reference; exhaust moved right with an angled tip, beacon rear-left, bonnet top 1.85,
   top link lengthened. Remaining differences are nitpicks → exported.

## Remaining differences vs reference
- Reference camera has stronger perspective / lower elevation; reference roof looks slightly thinner.
- Cab is ~1.1 m wide (limited by the rear tyre gap) — the reference cab reads slightly wider.

## Checks (final)
Body 1132, Linkage_Rear 320, Door_L 72, Wheel_FL/FR 432 each, Wheel_RL/RR 480 each → 3348 / 7000 (48 %);
LOD1 1674. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0 except `top_link` (see above). Tyre → body min
distance 0.061 (front) / 0.050 (rear); wheels touch only their axles. IMP-01 docking (temporary copy, removed):
Link3P_Front→Link3P_Rear error 0, 0 overlapping face pairs, plough frame 5.8 mm from the linkage (lug ↔ link eye),
plough shares at Y 0. Headless export reproduces the live model (identical fingerprint and atlas md5).

## Fix 2026-11-24 (orchestrator decision, CATALOG item 6): drawbar fork mouth for the shared eye Ø0.24
- `fork_front`: Z −2.025..−1.975 (0.125–0.175 ahead of the pin), Y 0.405..0.645 — runs under the PTO stub (stub bottom
  0.654, end Z −2.00); was Z −2.08..−2.03, Y 0.40..0.70 (only 0.07 ahead of the pin).
- `fork_bottom` and `drawbar` lengthened into the new front plate; `fork_top` ends 0.12 ahead of the pin (held by the pin)
  so a mounted implement's PTO stub at PTO_Rear stays clear (IMP-04 overlapped the longer top jaw).
- Hitch_Rear (0, 0.55, −2.15), Link3P_Rear, PTO_Rear, bbox and everything else unchanged; tris unchanged (3348, LOD1
  1674); preview unchanged (fork not visible; file kept byte-identical).
- Mating after the fix: IMP-03 and IMP-05 on Hitch_Rear error 0, 0 overlapping face pairs (eye 10 mm from the plate),
  IMP-03 PTO_Front = PTO_Rear; IMP-01, IMP-02, IMP-04 on Link3P_Rear error 0, 0 overlaps (IMP-04 PTO 0, stubs 1 mm apart).
