# EQP-01 GrainAuger (`FMS_Mach_GrainAuger`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `EQP-01_GrainAuger`, removed afterwards), final export
headless (identical fingerprint to the live build). Series helpers as in batch 2. Shared atlas md5 eb6768e2… unchanged.

## Layout (Unity, m; design shifted +0.002 in Z so the root is at the bbox centre)
- bbox X ±0.80 (tyres), Y 0..5.01 (hood top), Z ±5.363 (eye front / hood elbow); size 1.60 × 5.01 × 10.73.
- `Frame` (static, rigid): straight 8-sided grey tube Ø0.50 on the spec centre line (0, 0.75, +3.60) → (0, 4.55, −4.85)
  (24.2° incline), end flanges and 3 dark joint bands; grey square discharge elbow pointing down with orange stripes on
  both sides; red receiving hopper (open top, 1.40 × 1.40 at Y 1.30, 0.50 × 0.50 at Y 0.50, Z +2.90..+4.30); grey drawbar
  under the hopper to the shared eye Ø0.24 with a support foot on the ground; red A-frame (clamp on the tube at
  (0, 2.91, −1.20), two 0.11 legs down to the axle brackets, cross bar), red diagonal brace from the hopper side to the
  clamp (left side, as in the reference), 8-sided axle into the hubs.
- Wheels Ø0.70 × 0.30, 12 lugs: L/R (∓0.65, 0.35, −0.80).
- `Hitch_Front` (0, 0.55, +5.252) eye centre; `Auger_Out` (0, 4.144, −5.089) at the hood opening (spec ≈ (0, 4.15, −5.15)).

## Deviations from the spec
- Hitch is the shared ring eye Ø0.24 (CATALOG item 6) instead of a flat eye plate.
- Hood elbow length set so the bbox stays symmetric with the eye (Hitch_Front +5.252 instead of exactly +5.25).
- Preview camera more side-on (~67° off the nose) — the reference shows the auger from the left side.
- LOD1 = `make_lod1.py` `<part>_Low1` root children (CATALOG item 3).

## Rounds: 3
1. A-frame legs / axle brackets cut into the tyres (wheels inner face X 0.50), end flanges coplanar with the tube caps.
2. Legs moved inboard (tyre → frame 0.071 m), flanges offset 1 cm; hood shortened for a symmetric bbox.
3. Camera matched to the reference; live round; exported.

## Remaining differences vs reference
- Reference legs spread a bit wider and the hood stripes read larger.

## Checks (final)
Frame 644, Wheel_L/R 432 each → 1508 / 3000 (50 %); LOD1 750. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0
(mirror X 0.11 by design: brace on the left). Wheels touch only the axle. FBX re-import: 9 nodes, points at the design
values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copy, removed)
- On TRC-01 `Hitch_Rear`: error 0 / 0°, 0 overlapping face pairs, min distance 10.0 mm.
