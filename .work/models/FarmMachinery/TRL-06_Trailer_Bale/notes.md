# TRL-06 Trailer_Bale (`FMS_Mach_Trailer_Bale`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-06_Trailer_Bale`, removed afterwards), final export
headless (identical fingerprint to the live build). Series helpers as in batch 2; deck/apron/mudguard pattern of TRL-02.
Shared atlas md5 eb6768e2… unchanged. Always empty (no bales / load objects).

## Layout (Unity, m; design shifted −0.365 in Z so the root is at the bbox centre)
- bbox X ±1.26 (tyres), Y 0..2.30 (lattice panels), Z ±4.495 (eye front / rear fork jaws); size 2.52 × 2.30 × 8.99.
- `Chassis` (static): red rails X ±0.62..0.80 (Y 0.79–0.97), 5 grey cross members; deck 2.40 × 7.20: dark base plate,
  8 planks (slots 0 / 2) with 4 cm gaps 2 cm deep, top Y 1.035, red aprons with grey edge caps, grey rear strip, rear orange
  reflectors; two red lattice panels (front / rear, 2.40 wide, to Y 2.30, cut top corners): plates 0.10 thick with 5 × 3
  open squares (frame 0.12, bars 0.09), each on two chunky posts from the rails; axles + hangers; a dark mudguard over each
  wheel with a bracket; shared A-drawbar + cross bar + eye Ø0.24; rear drawbar fork.
- Wheels Ø0.90 × 0.40, 12 lugs: FL/FR (∓1.06, 0.45, +1.635), RL/RR (∓1.06, 0.45, −3.165) — axles 4.80 apart (front axle in
  the front third, rear axle in the rear third, reference).
- `Hitch_Front` (0, 0.55, +4.385) eye centre; `Hitch_Rear` (0, 0.55, −4.425) on the fork pin (front plate 0.125 ahead).

## Deviations from the spec
- Deck top Y 1.035 (spec ~0.9): like TRL-02 the deck runs above the Ø0.90 tyres and their mudguards (reference shows
  the deck edge over the wheels).
- Lattice = 5 columns × 3 rows of open squares (frame + 4 vertical + 2 horizontal inner bars), as the reference shows.
- Tris 3172 / 3000 (106 %): lattice overrun allowed up to ~2× (spec); four shared wheels = 1728.
- Shared eye Ø0.24 (CATALOG item 6) instead of ~0.28. LOD1 = `<part>_Low1` root children (CATALOG item 3).

## Rounds: 3
1. Mudguards swept the wrong way (thickness downward into the tyres), axles short of the hubs, posts coplanar with the
   rail undersides → fixed.
2. Edge caps coplanar with the front panel face → shortened 5 mm.
3. Live round; matches the reference (long deck, two lattice panels, widely spaced axles). Exported; chain check after export.

## Checks (final)
Chassis 1444, 4 wheels × 432 → 3172 tris; LOD1 1579. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0. Tyre →
chassis ≥ 0.015 m; wheels touch only their axles. FBX re-import: 13 nodes, points / pivots at the design values, texture
found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0 / 0°, 0 overlapping face pairs, min distance 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, 0 overlaps, 4.1 mm.
- Second TRL-06 `Hitch_Front` on this `Hitch_Rear` (chain): error 0, 0 overlaps, 46.9 mm.
