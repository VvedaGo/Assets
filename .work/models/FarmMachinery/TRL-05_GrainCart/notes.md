# TRL-05 GrainCart (`FMS_Mach_GrainCart`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `TRL-05_GrainCart`, removed afterwards), final export
headless (identical fingerprint to the live build). Series helpers as in batch 2 (see TRL-01 notes). Shared atlas md5
eb6768e2… unchanged.

## Layout (Unity, m; design shifted −1.305 in Z so the root is at the bbox centre)
- bbox X ±1.82 (mudguards; tyres ±1.80), Y 0..3.60 (folded auger spout), Z ±3.405; size 3.64 × 3.60 × 6.81.
- `Hopper` (static, hopper + chassis): trapezoid hopper — sloped dark lower walls from a 1.40 × 2.50 bottom (Y 1.00) to
  the 2.90 × 3.90 top section at Y 2.55, vertical red band to the chamfered rim at Y 3.00, 0.08 walls, dark inner walls and
  floor; grey rim bars on the long sides; rear orange reflectors on the rim; two chassis beams, 4 posts, front cross
  member, thick axle beam Ø0.20 into the hubs; dark half-round mudguards on brackets; auger base saddle and a rest block for
  the folded tube; shared A-drawbar + cross bar + eye Ø0.24, dark gearbox block with PTO stub, support foot on the ground.
- `Load_Grain` (child of Hopper): faceted flat-topped heap 5 cm inside the walls, top 0.15 below the rim; hidden only in
  the preview (Empty like the reference).
- `Auger_Unload` pivot (−1.15, 1.30, +0.755) = base at the front-left corner, axis Y: base housing, 8-sided tube Ø0.45
  rising across the front wall to the front-right corner (top end Y 3.38), 2 bands, spout housing + chute (top Y 3.60).
  `Auger_Out` (child) (1.32, 2.95, +0.755) at the chute outlet.
- Wheels Ø1.80 × 0.60, 16 lugs: L/R (∓1.50, 0.90, −1.605).
- `Hitch_Front` (0, 0.55, +3.295) eye centre; `PTO_Front` (0, 0.70, +3.445) = Hitch + (0, 0.15, 0.15).

## Deviations from the spec / reference
- Auger base on the front-LEFT corner (spec pivot) — the reference draws it at the front-right corner rising to the left
  (mirror). Tube length 3.15 m (spec ~4 m): the folded tube must stay within the front wall width.
- Hopper bottom section 1.40 × 2.50 and the slope break at Y 2.55 (vertical band 2.55–3.00): keeps the sloped walls clear of
  the Ø1.80 tyres and their mudguards (tyre → hopper ≥ 0.033 m).
- Shared eye Ø0.24 (CATALOG item 6) instead of ~0.3. LOD1 = `make_lod1.py` `<part>_Low1` root children (CATALOG item 3).
- Unfolded pose (for the prefab): Auger_Unload +150° about Y → the tube points left-forward, Auger_Out (−3.29, 2.95, +1.99).

## Rounds: 3
1. Lower walls touched the tyre tops / mudguards → slope break raised to 2.55; posts coplanar with the hopper bottom.
2. Support foot moved under the drawbar cross bar (was floating between the converging arms).
3. Live round; matches the reference layout (trapezoid hopper, corner auger, single big axle, drawbar with gearbox + foot).

## Checks (final)
Hopper 696, Load_Grain 44, Auger_Unload 136, Wheel_L/R 480 each → 1836 / 5000 (37 %); LOD1 940. Non-manifold / loose /
degenerate 0, coplanar 0, gaps 0. Auger touches the hopper only at its saddle / rest block. FBX re-import: 14 nodes, all
points and pivots at the design values (Load_Grain under Hopper, Auger_Out under Auger_Unload), texture found. Headless
export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0 / 0°, PTO_Front = PTO_Rear (0.0000 m), 0 overlapping face pairs, 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, PTO 0.0000 m, 0 overlaps, 4.1 mm.
- Unfolded auger over a TRL-01 bed: Auger_Out at Y 2.95 = 0.45 m above the TRL-01 side-wall top (2.50) and 0.25 m above
  its headboard (2.70). With the TRL-01 bed centred under the outlet the rising tube cuts its near wall (18 face pairs);
  with TRL-01 0.40 m further out: 0 overlaps and the outlet is 0.72 m inside the near bed edge (bed |X| 2.57–4.81).
