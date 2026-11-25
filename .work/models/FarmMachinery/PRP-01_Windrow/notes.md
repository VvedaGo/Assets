# PRP-01 Windrow (`FMS_Mach_Windrow`) — builder notes (Э7 series batch 3, 2026-11-24)

Look rounds in the owner's live Blender (own scene/collection `PRP-01_Windrow`, removed afterwards), final export headless
(identical fingerprint to the live build). Shared atlas md5 eb6768e2… unchanged. No LOD (catalogue), no points.

## Layout (Unity, m; root = module centre on the ground)
- bbox X ±0.70, Y 0..0.44, Z ±2.000 (exactly 4.000 m).
- `Windrow` (one mesh, palette cell 15 only): 8-vertex faceted cross-section — flat bottom X ±0.70 on Y 0, chamfered side
  (0.62, 0.12), shoulder (0.45, 0.25), ridge (±0.20, 0.40) — extruded through 5 sections at Z −2, −1, 0, +1, +2; lumps only in
  the 3 middle sections (ridge height ±0.04, ridge offset ≤ 0.03, shoulder ±0.03); end sections at Z ±2.000 identical,
  closed flat end caps.

## SNAP (module check, CATALOG "Модули")
- `SNAP OK`: the end profiles at Z +2.000 and −2.000 are identical (8 / 8 vertices), length 4.0000 m, min Y 0.0000.
- Two modules end to end (temporary copy 4.000 m further along +Z, removed): 8 / 8 joint vertices coincide, max mismatch
  0.0 m → OK. Check render %TEMP%/farmmachinery_check/PRP-01/PRP-01_check_snap2.png (seamless joint). The two end caps meet
  face to face at the joint by design (modules laid in a row).

## Deviations
- Top Y 0.44 (spec ridge 0.40 + lump up to +0.04).

## Rounds: 2
1. Lumps too subtle against the reference → raised to the spec maximum (±0.04) with alternating signs.
2. Live round; exported.

## Checks (final)
76 / 300 tris (25 %). Non-manifold / loose / degenerate 0, coplanar 0, flat bottom on Y 0 (no slab, nothing below 0).
FBX re-import: 2 nodes, 76 tris, size 1.40 × 0.44 × 4.00, texture found. Headless export = live build (fingerprint identical).
