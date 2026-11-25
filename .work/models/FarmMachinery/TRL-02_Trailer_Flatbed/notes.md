# TRL-02 Trailer_Flatbed (`FMS_Mach_Trailer_Flatbed`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-02_Trailer_Flatbed`), final export headless
(identical fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2….

## Layout (Unity, m; design shifted −0.32 in Z so the root is at the bbox centre)
- bbox X ±1.26 (tyres / mudguards), Y 0..1.68 (headboard), Z ±3.34 (eye front / rear fork jaws); length 6.68.
- `Chassis` (one static mesh): red rails X ±0.62..0.80 Y 0.88–1.07, 4 grey cross members; deck 2.40 × 5.02: dark
  base plate, 8 planks (slots 0 / 2 alternating, 0.246 wide) with 4 cm gaps 2 cm deep, top Y 1.135; red side aprons
  X ±1.14..1.20 with a grey edge cap, grey rear strip; low red headboard (top 1.68, cut top corners) with 2 stiffeners;
  tandem running gear (hangers, walking beams, axles); dark mudguards (0.055 thick) under the apron over each side pair;
  rear orange reflectors; shared A-drawbar + cross bar + shared eye Ø0.24; rear drawbar fork.
- Wheels Ø1.00 × 0.40, 12 lugs: FL/FR (∓1.06, 0.50, −1.17), RL/RR (∓1.06, 0.50, −2.47) (spacing 1.30).
- `Hitch_Front` (0, 0.55, +3.23) eye centre; `Hitch_Rear` (0, 0.55, −3.27) on the fork pin.

## Deviations from the spec
- Deck top Y 1.135 (spec ~0.95) and rails top 1.07 (spec ~0.85): the reference shows a full-width deck running over
  the tandem wheels with the mudguards right under its edge; with Ø1.0 tyres (top 1.00) the deck must sit above
  1.07. Height 1.68 stays within the catalogue 1.7.
- Gaps are real 2 cm recesses (deck base slot 1), planks 0.246 wide (8 planks).
- Shared eye Ø0.24 (CATALOG item 6) instead of the spec Ø~0.28.
- LOD1 by `make_lod1.py` (`<part>_Low1` root children, CATALOG item 3).

## Rounds: 3
1. Narrow deck between outboard wheels: mudguards towered over the deck — did not match the reference.
2. Full-width deck above the wheels, mudguards under the apron; coplanar plank/strip faces fixed.
3. Live round: matches the reference; exported.

## Remaining differences vs reference
- The red side band is thinner than in the reference (apron 5 cm, limited by the tyre clearance); headboard top edge
  has no front chamfer.

## Checks (final)
Chassis 708, 4 wheels × 432 → 2436 / 2500 (97 %); LOD1 1216. Size 2.52 × 1.68 × 6.68 m. Non-manifold / loose /
degenerate 0, coplanar 0, gaps 0. Tyre → chassis ≥ 0.015 m (mudguards), wheels touch only their axles. FBX re-import:
13 nodes, points/pivots at the design values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0.000000 m / 0°, 0 overlapping face pairs, min distance 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, 0 overlaps, min distance 4.1 mm.
