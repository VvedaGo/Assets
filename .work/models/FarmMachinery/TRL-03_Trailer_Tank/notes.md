# TRL-03 Trailer_Tank (`FMS_Mach_Trailer_Tank`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-03_Trailer_Tank`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2….

## Layout (Unity, m; design shifted −0.215 in Z so the root is at the bbox centre)
- bbox X ±1.25, Y 0..3.06 (railing top), Z ±2.995 (eye front / tap end); length 5.99.
- `Body` (static): tank 16 segments, apothem 0.93 (Ø1.86 across flats), axis Y 1.78, Z −2.665..+1.735 (4.40 long),
  two-step chamfered ends, upper facets slot 5, lower slot 6, flat top facet; 2 grey bands (0.12 wide, 0.05 proud) on
  cradle saddles; rails X ±0.50..0.68 (top 0.88), 4 cross members under the tank; tandem running gear; dark mudguards
  over each side pair; rear light bar + orange reflectors; shared A-drawbar + cross bar + shared eye Ø0.24; galvanised
  hatch collar, catwalk (Y 2.78–2.82) with two supports and a short railing on the left; side ladder rear left
  (rails 0.06, 4 rungs 0.05, 2 brackets into the tank); rear outlet tap (8-sided pipe Ø0.20, valve block, dark handle).
- `Hatch` pivot (0, 2.84, −0.27) = hinge line at the rear edge of the lid (axis X): 12-sided lid Ø0.66, hinge block,
  handle. Rest = closed.
- Wheels Ø1.10 × 0.45, 12 lugs: FL/FR (∓1.025, 0.55, −0.615), RL/RR (∓1.025, 0.55, −1.915) (spacing 1.30).
- `Hitch_Front` (0, 0.55, +2.885) eye centre. No `Hitch_Rear` (catalogue).

## Deviations from the spec
- Height 3.06 (catalogue 2.8): the reference shows a railing beside the hatch above the tank top; tank top itself 2.71,
  hatch lid 2.86.
- Ladder from Y 1.26 (above the mudguard) to 2.46 instead of from ~0.6: the mudguard covers the rear wheels there.
- Tank Ø1.86 across flats (Ø1.89 across corners) and axis 1.78 so the tank bottom (0.85) clears the cross members.
- Shared eye Ø0.24 (CATALOG item 6) instead of ~0.28. LOD1 = `<part>_Low1` root children (CATALOG item 3).

## Rounds: 2
1. Saddles touched the rear tyres (4 mm), railing bars coplanar → saddles narrowed, rail offset.
2. Live round matches the reference (tank, bands, hatch + railing, ladder, tandem, drawbar). Exported.

## Remaining differences vs reference
- Reference ends look slightly more domed; tap sits a little lower in the reference.

## Checks (final)
Body 1236, Hatch 76, 4 wheels × 432 → 3040 / 3500 (87 %); LOD1 1515. Size 2.50 × 3.06 × 5.99 m. Non-manifold /
loose / degenerate 0, coplanar 0, gaps 0 (mirror X 0.42 by design: ladder, railing, tap). Tyre → body ≥ 0.040 m,
wheels touch only their axles; Hatch touches only its collar. FBX re-import: 14 nodes, points/pivots at the design values,
texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0.000000 m / 0°, 0 overlapping face pairs, min distance 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, 0 overlaps, min distance 4.1 mm.
