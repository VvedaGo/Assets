# HRV-02 Baler_Round (`FMS_Mach_Baler_Round`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `HRV-02_Baler_Round`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2…. No bale /
no load mesh.

## Layout (Unity, m; root on the ground at the bbox centre, no shift)
- bbox X ±1.36 (fenders), Y 0..2.45 (hinge knuckles), Z ±2.261 (eye front / rear bale ramp); size 2.72 × 2.45 × 4.52.
- `Body` (static): front half of the 16-sided bale chamber (vertex radius 0.90 → Ø1.8, axis X at (1.45, −0.90), side
  plates X ±0.82 with dark 0.06 chamfer rims), 3 grey bands, top hinge shaft with 3 knuckles, ram bosses, drive cover box
  on the chamber front, chassis beams + front cross member + axle, red fenders over the wheels (bracket to the side
  plates), rear bale ramp, red A-drawbar (chamber front at Y 1.05 → over the pickup → down to the grey tip) with the
  shared eye Ø0.24, PTO stub, support stand on a foot plate (touches Y 0).
- `Tailgate` pivot (0, 2.35, −0.90) = hinge at the top of the chamber, axis X: rear half of the drum (4 mm seam to the
  front half), 3 bands, orange stripes on both side plates, two hydraulic rams to the front-half bosses. Rest = closed;
  Open = +80° (rear lower edge swings up and back, checked: lowest point 2.04 m, 0 contact with the wheels).
- `Pickup` pivot (0, 0.55, +0.10) = rear hinge, axis X: hinge rod, side arms, 12-sided drum Ø0.40 at (0.48, +0.90),
  8 rows × 6 chunky tines (0.05) reaching Y 0.15 / Z +1.23, red guard over the rear half, side shields, guard bar.
- Wheels Ø1.00 × 0.50, 14 lugs: L/R (∓1.10, 0.50, −0.70).
- `Hitch_Front` (0, 0.55, +2.15) eye centre; `PTO_Front` (0, 0.70, +2.30) = Hitch + (0, 0.15, 0.15); `Bale_Out`
  (0, 0.90, −2.15) above the bale ramp.

## Deviations from the spec
- Drawbar A-arms red (reference) with the grey tip + shared eye; spec listed frame/drawbar slots 7/8.
- Pickup drum Ø0.40 (spec ~0.5) so that the tines (to radius 0.33) stay within Y 0.15..0.81 / Z ≤ 1.23.
- Rear bale ramp added (real baler part, not in the reference view): it makes the bbox symmetric so the spec points
  (Hitch_Front +2.15, Bale_Out −2.15) stay exact with the root at the bbox centre.
- Side plates at X ±0.82 (spec ~±0.85) to keep 3 cm between the tyres and the chamber.
- LOD1 = `make_lod1.py` `<part>_Low1` root children (CATALOG item 3).

## Rounds: 3
1. Coplanar beams / hangers / pickup arm caps, bands floating 4.6 mm off the facets, guard bar floating, fenders cutting
   into the tailgate side → fixed (bands embedded 5 mm, fenders 5 mm outboard on a bracket to the front half).
2. Bale ramp for the symmetric bbox; Open pose check render (HRV-02_check_open.png).
3. Guard reduced to the rear half so the tine rows read like the reference; live round; exported.

## Remaining differences vs reference
- Reference wheels look slightly bigger; reference drawbar has a cross bar near the pickup front.
- Expected contacts Tailgate × Body (117 face pairs at rest): hinge shaft, ram ends in their bosses, tailgate lower edge
  on the chassis beams. Pickup × Body: hinge rod through the chassis beams.

## Checks (final)
Body 868, Tailgate 464, Pickup 792, Wheel_L/R 456 each → 3036 / 5000 (61 %); LOD1 1518. Non-manifold / loose /
degenerate 0, coplanar 0, gaps 0, mirror X 0. Tyre → body / tailgate ≥ 0.030 m. FBX re-import: 14 nodes, all points and
pivots at the design values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- On TRC-01 `Hitch_Rear`: error 0.000000 m / 0°, `PTO_Front` = `PTO_Rear` (0.0000 m), 0 overlapping face pairs, 10.0 mm.
- On TRC-02 `Hitch_Rear`: error 0, PTO 0.0000 m, 0 overlaps, 4.1 mm.
