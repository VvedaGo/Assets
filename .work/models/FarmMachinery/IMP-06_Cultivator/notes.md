# IMP-06 Cultivator (`FMS_Mach_Cultivator`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender 5.2 via MCP (own scene/collection `IMP-06_Cultivator`), final export headless
(identical geometry fingerprint to the last live build). `build.py` = batch-2 series helpers (verbatim copies of the
accepted batch-1 helpers: pack wheel, tbox, rod, plate_x/y/z, prism_x, linkage_frame, render, verify) + item code.
Shared atlas `T_FarmMachinery_Red_BaseColor.png` / `M_FarmMachinery_Red` (md5 eb6768e2… unchanged).

## Layout (Unity, m; root on the ground at the bbox centre, no shift needed)
- bbox X ±1.50, Y 0..1.40, Z ±1.10.
- `Frame`: 3 cross beams 3.0 × 0.10 × 0.12 (Y 0.55–0.67) at Z +0.40 / −0.05 / −0.50, side beams at X ±1.40, two mast-base
  beams X ±0.45 from the front beam to the lugs, shared linkage frame (IMP-01 pattern: lugs X ±0.45 with pin holes on the
  pin axis Y 0.60 Z +1.03, red A-mast, top-link bracket (1.30, +0.78)), 20 S-tines (7 / 6 / 7, rows interleaved, pitch
  0.45, middle row offset 0.225): clamp block + 5-point S-sweep 0.07 × 0.09 + pointed share 0.14 wide, tips at Y ≈ 0.003.
  Roller arms X ±1.45 from the rear beam to the axle bosses.
- `Roller` pivot (0, 0.25, −0.85), spin axis X: cage Ø0.50 × 2.80 — 2 solid 16-gon end discs, 3 inner 16-gon rings,
  8 flat bars, axle into the arm bosses; bottom facet on Y 0.
- `Link3P_Front` (0, 0.60, +1.03) = centre between the lug pin axes; lug front face Z +1.10 (bbox front).

## Deviations from the spec
- Mast top Y 1.40 (spec 1.30): the top-link bracket uses the IMP-01 offsets (Y 1.30, 0.25 m behind the pins); with the
  spec position (Y ~1.2, 0.15 behind) the mast cross bar and bracket hit TRC-01's fork and top link (45 face pairs).
- `Link3P_Front` Z +1.03 (spec +0.95) so the lug front face is the bbox front +1.10 and the root stays centred.
- Mast centred at X 0 (pack contract, Link3P_Front X 0); the reference draws the A-mast at the left end of the front
  beam — kept the contract.
- No centre diagonal brace (reference has none). Roller arms at X ±1.45 (spec ±1.25 would cut through the 2.80 m roller).
- Roller is an open cage (reference) on 16 segments rather than a closed drum with ribs.
- LOD1 by `make_lod1.py` (`<part>_Low1` root children), not `<part>_LOD1` children as in the spec text (CATALOG item 3).

## Rounds: 3
1. Tris 2980 (over), 36 coplanar pairs (bars flush with ring faces, arm vs boss faces), mast clashed with TRC-01.
2. Lighter clamps/shares/bars (2372), coplanar 0, IMP-01 mast offsets → 0 overlaps on TRC-01.
3. Camera matched to the reference (more frontal, rows nearly level); tines thickened. Remaining: nitpicks.

## Remaining differences vs reference
- Mast centred (reference: at the left end). Roller sits on the ground per spec, so it is lower and mostly hidden behind
  the frame in the ¾ view; the reference shows it at frame height and slightly larger.

## Checks (final)
Frame 1744, Roller 628 → 2372 / 2500 (95 %); LOD1 1166 (Frame_Low1 852, Roller_Low1 314). Size 3.00 × 1.40 × 2.20 m
(X × Y × Z). Non-manifold / loose / degenerate 0, coplanar 0, component gaps 0, mirror X 0. Roller touches the frame
only at its axle / bosses (expected). FBX re-import: 6 nodes, pivots and Link3P_Front at the design values, texture found.
Headless export = live build (fingerprint Frame (1016, 982, 1135.4, 1414.7252), Roller (336, 348, 0.0, 350.761)).
Mating: on TRC-01 `Link3P_Rear` error 0.000000 m / 0°, 0 overlapping face pairs, min distance 5.0 mm (lug ↔ link eye).
