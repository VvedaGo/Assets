# PLT-03 Climbing Rose, Top garland `FMS_Garden_Rose_Climbing_Top` (+ `_Pink`) — builder notes (Э7, batch 1, 2026-11-25)

Source of truth: `build.py` (`-- PLT-03 build|export`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in collection `PLT-03_Rose_Climbing_Top` + child
`PLT-03_Rose_Climbing_Top_Pink` (left in place). Owner's file not saved (is_dirty False after the session); Cube and the
other collections untouched; selection (Cube, active Cube) saved before the live export and restored; no TMP scenes or
objects left. Shared material `M_Garden_Flora` reused as is; atlas F loaded read-only (`pc.atlas_image` NOT used) —
MD5 `ae0f0dba44e0dabc5d4eb874de6485c7` unchanged (= PLT-02 note), palette cells 0 mismatches; atlas A not used
(MD5 `119daf05…` unchanged).

## Result

| | base | `_Pink` |
|---|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Rose_Climbing_Top.fbx` (+ .fbm) | `..._Pink.fbx` (+ .fbm) |
| Tris / budget | **1064 / 1100** | 1064 / 1100 |
| Size X × Y(depth) × Z (Blender) | 1.571 × 0.563 × 0.539 m | same |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same |

- Tris per part: Leaf clusters 400 (5 × 80), Blooms 408 (6 × 68, rose_bloom_v2 ×1.25), Canes 232 (2 × 116: 10 rings,
  6-sided, capped), Closed buds 24 (2 × 12).
- `.blend`: `art/AssetNew/Blend/FMS_Garden_Rose_Climbing_Top.blend` (both collections). ONE preview
  `art/AssetNew/Previews/FMS_Garden_PLT_03_Preview.png` (base, series 3/4). No LOD (catalogue).
- Variant `_Pink`: cups 4 → 7, inner petals + bud + closed buds 5 → 6; foliage, canes unchanged (same vertices).

## Axes, pivot, mounting
- Blender X = length, −Y = front (Unity +Z after the −Z-forward export), Z = up (Unity Y).
- Pivot (0, 0, 0) = centre of the underside; root rot 0 / scale 1. x −0.780 … 0.791, y −0.281 … 0.282, z 0 … 0.539.
- Attachment plane Blender Z = 0 (Unity Y = 0): min z 0.0000, nothing below. The canes touch it with one edge line at
  their low points (8 vertices at z 0, hex vertex pointing down); the front clusters are pressed flat at z 0.010,
  0.0115, 0.013, … (1.5 mm steps, no coplanar bottoms); the back clusters C2/C4 sit higher (bottom ~0.10) on the canes.
- STR-01 top measured on the exported `FMS_Garden_Arch_Wood.fbx` (headless import): X −0.80 … 0.80, beam tops at z 2.40
  over Y −0.335 … 0.335, `Plant_Top` empty at (0, 0, 2.40). Mounted check render (garland at Plant_Top) sits on the
  beams, fully inside the top footprint.
- SNAP OK: length 1.571 (≤ 1.60 arch top, ≥ 1.55), X centre +0.005, depth 0.563 (≤ 0.60, inside |y| ≤ 0.335 of the beam
  tops), Y centre 0.000; STR-04 beam (0.10 wide): cane surfaces within |y| ≤ 0.069 (centrelines ±0.045), so the canes
  lie over the beam; length 1.571 < beam 3.5; ground (attachment) contact min z 0.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 (every component touches another), coplanar overlapping pairs 0.
- Canes A/B do not intersect each other. Blooms touching each other: none. No bloom inside a foreign cluster; every
  calyx / bud base inside its own cluster (no warnings). Clusters C2–C3, C3–C4, C4–C5 interpenetrate (foliage mass).
- FBX re-import (both): 2 nodes, 1064 tris, dims 1.571 / 0.563 / 0.539, min z 0, texture found in each `.fbm`.
- Headless `build.py -- PLT-03 export`: geometry SHA1 == live `0f0116f68bd44210b519ec68ba9ccb44aa5632aa`
  (2 meshes, 562 verts / 956 faces each, UV cells included).

## Build
- Clusters: PLT-01 `leaf_cluster` (80 tris, domed, noise ±0.035), depth scaled 0.80. Measured on the reference
  (727 px/m, front ~12° above): front row C1/C3/C5 x −0.59 / −0.015 / 0.55, y −0.085, D 0.42, height 0.72 D, top ~0.29;
  back row C2/C4 x −0.25 / 0.285, y +0.085, D 0.45, height 0.75 D, bottom ~0.10, top ~0.44.
- Canes: two 6-sided prisms Ø0.055 → Ø0.045, braided as straight diagonals (triangle wave, period 0.60, z swing 0.16):
  from the front they make a steep X in each gap between the front clusters (x −0.30 / +0.30, as in the reference),
  in depth they pass front/back alternately (±0.045), turning points chamfered and hidden inside the front clusters;
  ends at x ±0.66 inside C1 / C5.
- Blooms: `rose_bloom_v2` ×1.25 (rim Ø0.145, reference ~0.16), 6 blooms (2 on C1, 1 on each of the others), tilted
  12–24° to the front and 0–12° outward, visible green neck 0.045.
- 2 closed buds (C2 right, C4 left), Ø0.068, 0.125 tall, near-upright.

## Rounds (live, 4 of 5)
0. Headless first build (1088 tris): canes read as one bar, back clusters sat on the plane and hid the canes.
1. Live: back clusters raised on the canes, canes thicker (Ø0.055); still no visible X (sine braid too shallow in the gaps);
   buds read as red thorns; X centre +0.02.
2. Clusters shifted −0.015 (X centred), buds with a longer green calyx; canes still one band.
3. Canes rebuilt as a triangle-wave braid (period 0.6, steep X in the gaps; front/back by the nearest crossing to keep
   them apart): X crossings now read as in the reference; 1064 tris.
4. Buds near-upright (side view no longer a fin from the front). Stopped: only nitpicks left.

## 128 px self-check
Reads as a long low garland: a row of green drops with red roses on top and a brown braided cane visible between them.
Not a round bush, not a hedge strip.

## Remaining differences vs reference / deviations
- Height 0.539 vs catalogue 0.40: follows the reference (blooms top ~0.55–0.59 at 727 px/m); height is not a functional
  size (length 1.6 and depth ≤ 0.6/0.7 are kept). Record in spec.md / catalogue as 1.6 × 0.56 × 0.54.
- Length 1.571 (reference/catalogue 1.6): end clusters are rounded, the 1.6 m arch top is not exceeded.
- Blooms are rose_bloom_v2 (owner note), not the reference's simple cup; rim 0.145 vs ~0.16 in the reference.
- Back clusters are raised on the canes (bottom ~0.10) as in the reference, so the underside is flat only under the
  canes and the front clusters (the attachment still works: canes on z 0, front clusters at 0.010–0.016).
- Clusters slightly lumpier / less round than the reference drops (PLT-01 generator kept for series consistency).
- Closed buds (owner note) are not in the reference; from some 3/4 angles the C4 bud reads as a small red spike.
