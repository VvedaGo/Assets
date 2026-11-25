# ATT-01 QuickHitch (`FMS_Mach_QuickHitch`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `ATT-01_QuickHitch`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2…. No LOD.

## Layout (Unity, m; root on the ground below the centre)
- bbox X ±0.585 (pin ends), Y 0.47..1.40, Z ±0.22; size 1.17 × 0.93 × 0.44.
- `Frame` (one rigid mesh): frame plane at Z −0.10 — lower bar 1.04 × 0.12 × 0.12 at Y 0.725–0.845 (above the tractor
  drawbar fork), sloped side bars 0.11 into a dark top block (Y 1.16–1.34), dark triangular gusset (0.05); tractor side:
  two lugs X ±0.45 (0.08 × 0.26 × 0.14, 8-segment holes Ø0.07 on the pin axis Y 0.60, Z +0.15 — the IMP-01 lug pattern,
  the TRC lower-link pins pass through) on webs to the bar; implement side: dark hook jaws X ±0.50..0.56 with a slot from
  below and light pins (8-seg Ø0.052) on the axis Y 0.60, Z −0.15, X ±0.38..0.585 (through the implement lug holes);
  dark U-catch behind the top block.
- `Link3P_Front` (0, 0.60, +0.15) (meets TRC `Link3P_Rear`), `Link3P_Rear` (0, 0.60, −0.15) (meets the implement
  `Link3P_Front`), both +Z forward, +Y up.

## Deviations from the spec / reference
- The triangle stands BEHIND the tractor-side pin axis (frame plane Z −0.10) and its lower bar is raised to Y 0.725–0.845:
  TRC-01's drawbar fork, fork pin and top-link end reach 0.21 m behind its Link3P_Rear, so a frame through the pin axes at
  Y 0.60 (reference look) overlapped TRC-01 by 74 face pairs. The reference shows the lower bar at the pin height.
- Width 1.17 over the pins / 1.12 over the jaws (spec: frame ≤ 1.0): the jaws must sit outboard of the implement lugs
  (X ±0.41..0.49 on all IMP items) and the pins stick out like in the reference. Depth 0.44 (spec 0.3): the lugs and
  jaws extend ±0.07 around the two pin axes that are 0.30 apart.
- Tractor side has lugs with holes (the tractor provides the pins), the implement side has the pins + hooks — the
  reference shows pins + hooks on both lower corners.
- Tris 404 / 400 (101 %, soft budget).

## Rounds: 3
1. Reference-like frame through the pin axes: 74 overlapping pairs with TRC-01 (fork, fork pin, top link), 12 with IMP-01.
2. Frame moved behind / above the tractor hardware; jaws shortened (IMP-01 beam front end): 0 overlaps.
3. Live round, tris trimmed; exported.

## Checks (final)
Frame 404 tris. Non-manifold / loose / degenerate 0, coplanar 0, gaps 0, mirror X 0. FBX re-import: 4 nodes, both
Link3P points at the design values, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copies, removed)
- ATT-01 `Link3P_Front` on TRC-01 `Link3P_Rear`: error 0.000000 m / 0°, 0 overlapping face pairs, min distance 9.0 mm.
- IMP-01 `Link3P_Front` on ATT-01 `Link3P_Rear`: error 0, 0 overlaps, min distance 10.0 mm; IMP-01 vs TRC-01 in that
  chain: 0 overlaps (160.7 mm apart). Render: %TEMP%/farmmachinery_check/ATT-01/ATT-01_mate_TRC-01_IMP-01.png.
