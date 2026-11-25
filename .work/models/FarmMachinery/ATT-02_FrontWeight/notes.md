# ATT-02 FrontWeight (`FMS_Mach_FrontWeight`) — builder notes (Э7 series batch 2, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `ATT-02_FrontWeight`), final export headless (identical
fingerprint to the last live build). Batch-2 series helpers (see TRL-01 notes). Shared atlas md5 eb6768e2…. No LOD.

## Layout (Unity, m; design shifted +0.02 in Z so the root is at the bbox centre)
- bbox X ±0.49 (lugs), Y 0.20..1.17, Z ±0.35; size 0.98 × 0.97 × 0.70.
- `Body` (one rigid mesh): red block 0.90 × 0.80 × 0.45 (Y 0.20–1.00, Z −0.13..+0.32), 0.08 chamfers on the four long
  edges and 0.05 chamfers on the side edges, top/front slot 5, sides/lower/rear slot 6, two horizontal ribs on the front
  face (0.04 proud); grey mounting frame on the rear: lower cross bar between the lugs, two dark lugs X ±0.45
  (0.08 × 0.22 × 0.14, 8-segment holes Ø0.07 on the pin axis Y 0.60), centre post, top-link bracket (Y 1.03–1.17, it
  receives the end of TRC-02's front top link), two diagonal braces.
- `Link3P_Rear` (0, 0.60, −0.28) = centre between the lug pin axes; meets TRC-02 `Link3P_Front`. No `Link3P_Front`.

## Deviations from the spec
- Pin blocks at X ±0.45 (CATALOG item 6; spec table said ≈ ±0.35, its own "What NOT" says ±0.45).
- Height to Y 1.17 (spec bbox Y 0.2..1.0): the top-link bracket sits where TRC-02's front top link ends (Y 1.10).
- Depth 0.70 (spec 0.6): lugs (±0.07 around the pin axis) + frame + 0.45 block; `Link3P_Rear` Z −0.28 (spec ≈ −0.30)
  after centring the root.
- Ribs are proud strips; the reference shows recessed panels (nitpick).

## Rounds: 2
1. Cross bar touched TRC-02's front lower-link pins (16 face pairs) → bar starts 1.5 cm in front of the pin axis.
2. 0 overlaps; matches the reference (block in front, grey A-bracket with lugs behind). Live round, exported.

## Checks (final)
Body 312 / 600 tris (52 %). Non-manifold / loose / degenerate 0, coplanar 0, gaps 0, mirror X 0. FBX re-import:
3 nodes, Link3P_Rear at the design value, texture found. Headless export = live build (fingerprint identical).

## Mating (temporary copy, removed)
- On TRC-02 `Link3P_Front`: error 0.000000 m / 0°, 0 overlapping face pairs, min distance 8.8 mm (lug ↔ link eye).
  Render: %TEMP%/farmmachinery_check/ATT-02/ATT-02_mate_TRC-02.png.
