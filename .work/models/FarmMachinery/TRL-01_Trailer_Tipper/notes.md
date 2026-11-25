# TRL-01 Trailer_Tipper (`FMS_Mach_Trailer_Tipper`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-01_Trailer_Tipper`), final export headless (identical
geometry fingerprint to the last live build). Batch-2 series helpers (verbatim batch-1 helpers + `a_drawbar` = IMP-03
drawbar with the shared eye Ø0.24, `rear_fork` = TRC-01 fork after the 2026-11-24 fix). Shared atlas, md5 eb6768e2….

## Layout (Unity, m; design shifted −0.29 in Z so the root is at the bbox centre)
- bbox X ±1.25 (tyres), Y 0..2.70 (headboard), Z −3.22 (rear fork jaws) .. +3.22 (eye front); length 6.44.
- `Chassis`: rails X ±0.46..0.64 Y 0.93–1.11, 3 cross members, tandem bogie (hangers, walking beams, axles into the
  hubs), dark mudguard over each side pair (sloped ends, bracket), rear light bar with orange reflectors, bed hinge
  knuckles, tipping ram (static, 8-sided), shared A-drawbar with cross bar and the shared eye, rear drawbar fork.
- `Bed` pivot (0, 1.11, −3.01) = rear lower edge (tipping axis X): floor, sills on the rails, side walls X ±1.04
  (dark lower band, red wall with chamfered top 2.50), 4 ribs per side (0.08 proud, 0.10 wide), headboard to 2.70 with
  cut top corners, front reflectors.
- `Tailgate` (child of Bed) pivot (0, 2.50, −3.035) = top rear hinge, panel between the side walls, 2 latch blocks.
- `Load_Grain` (child of Bed, pivot = Bed pivot): 8-faceted flat-topped heap, base 5 cm inside the walls, crest to
  Y 2.10 shifted to the rear. Hidden only in the preview render (preview = Empty like the reference); exported visible —
  the Empty prefab disables it.
- Wheels Ø1.10 × 0.45, 12 lugs: FL/FR (∓1.025, 0.55, −0.84), RL/RR (∓1.025, 0.55, −2.14) — axle spacing 1.30.
- `Hitch_Front` (0, 0.55, +3.11) eye centre; `Hitch_Rear` (0, 0.55, −3.15) on the fork pin (front plate 0.125 ahead).

## Deviations from the spec
- Bed 2.08 m wide over the walls (2.24 over the ribs) instead of 2.4: the reference shows the tyres standing out beyond
  the bed sides (PIPE-04); with 2.4 the wheels disappeared under the bed in the ¾ view.
- Drawbar eye = shared eye Ø0.24 / hole 0.08 (CATALOG item 6) instead of the spec Ø~0.28.
- Bed floor top Y 1.30, walls 1.20–2.50 (spec floor ~1.2): bed bottom sits 1 cm above the mudguards that cover the tyres.
- Reflectors: rear pair on the chassis light bar (static, per spec), front pair on the headboard (reference).
- LOD1 by `make_lod1.py` (`<part>_Low1` root children, CATALOG item 3), not `<part>_LOD1` children (spec text).

## Rounds: 3
1. Bed 2.4 m covered the wheels; mudguard bracket gap 0.11; coplanar ends (floor/headboard, light bar/rails).
2. Narrower bed, brackets into the mudguard, coplanar 0, degenerate 0 (wall top chamfer 0.03 on a 0.08 wall).
3. Live round matches the reference layout; exported. Chain check after export.

## Remaining differences vs reference
- Reference shows more of the grey chassis (posts under the bed front); here the rails sit inside under the bed.

## Checks (final)
Chassis 628, Bed 240, Tailgate 100, Load_Grain 44, 4 wheels × 432 → 2740 / 4000 (68 %); LOD1 1392. Size 2.50 × 2.70 ×
6.44 m. Non-manifold / loose / degenerate 0, coplanar 0, component gaps 0. Tyre → chassis ≥ 0.030, tyre → bed ≥ 0.10;
wheels touch only their axles. Tipping check: Bed raised 45° about its axis → 0 overlaps with the wheels (hinge only).
FBX re-import: 19 nodes (Tailgate and Load_Grain nested under Bed, nested-child fix applied), points/pivots at design
values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies from art/FarmMachinery/Blend, removed in the same run)
- On TRC-01 `Hitch_Rear`: error 0.000000 m / 0°, 0 overlapping face pairs, min distance 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, 0 overlaps, min distance 4.1 mm.
- Second TRL-01 `Hitch_Front` on this `Hitch_Rear` (chain, CMP-02): error 0, 0 overlaps, min distance 46.9 mm.
