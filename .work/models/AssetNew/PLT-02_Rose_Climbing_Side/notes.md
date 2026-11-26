# PLT-02 Climbing Rose, Side `FMS_Garden_Rose_Climbing_Side` (+ `_Pink`) — builder notes (Э7, batch 1, 2026-11-25)

Source of truth: `build.py` (`-- PLT-02 build|export`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback mode;
execute_blender_code and look worked). Live work only in collection `PLT-02_Rose_Climbing_Side` + child
`PLT-02_Rose_Climbing_Side_Pink` (left in place). Owner's file not saved; Cube and other collections untouched; selection
(Cube) saved before the live export and restored. Shared material `M_Garden_Flora` reused as is (live); atlas F loaded
read-only (`pc.atlas_image` is NOT used because it rewrites the PNG) — MD5 `ae0f0dba…` unchanged, palette cells 0 mismatches.

## Result

| | base | `_Pink` |
|---|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Rose_Climbing_Side.fbx` (+ .fbm) | `..._Pink.fbx` (+ .fbm) |
| Tris / budget | **1600 / 1600** | 1600 / 1600 |
| Size X × Y(depth) × Z (Blender) | 0.696 × 0.237 × 2.014 m | same |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same |

- Tris per part: Leaf clusters 640 (8 × 80), Blooms 544 (8 × 68, rose_bloom_v2 ×1.15), Canes 372 (A, B 11 segments 6-sided
  = 140 each; C left edge 7 segments = 92), Closed buds 24 (2 × 12), Stump 20 (6-sided).
- `.blend`: `art/AssetNew/Blend/FMS_Garden_Rose_Climbing_Side.blend` (both collections). ONE preview
  `art/AssetNew/Previews/FMS_Garden_PLT_02_Preview.png` (base, series 3/4). No LOD (catalogue).
- Variant `_Pink`: outer petals 4 → 7, inner petals + bud + closed buds 5 → 6; foliage, canes unchanged (same vertices).

## Axes, pivot, mounting
- Blender X = width, −Y = front (Unity +Z after the −Z-forward export; the plant grows toward it), Z = up (Unity Y).
- Pivot (0, 0, 0) = base centre on the back plane at the ground; root rot 0 / scale 1.
- Attachment plane Blender Y = 0 (Unity Z = 0): max Y = 0.0000, nothing behind it. Canes touch it with one edge line
  (hex vertex pointing back), stump with one edge; cluster backs pressed flat at Y −0.010 … −0.0205 (1.5 mm steps per
  cluster, so no coplanar backs between overlapping clusters). Front depth 0.237 (≤ 0.30).
- SNAP OK: width 0.696 ≤ 0.70 (STR-01/03 side 0.6 + 2 × 0.05 overhang); top 2.014 < lintel 2.10 (0.39 below arch top
  2.40); MOD-01 top 0.164 above panel top 1.85, width < 1.88; MOD-03 rises 1.41 above the wall top 0.60; ground min z 0.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0, coplanar overlapping pairs 0.
- Blooms touching each other: none. Every calyx / bud base inside its own cluster. Bloom L4 grazes the underside of
  cluster T (visible, not hidden). Clusters L4–R3, L4–T interpenetrate (foliage mass at the top).
- FBX re-import (both): 2 nodes, 1600 tris, dims 0.696 / 0.237 / 2.014, min z 0, texture found in each `.fbm`.
- Headless `build.py -- PLT-02 export`: geometry SHA1 == live `0244ea08d6e7fa8ee418dac7c876cf58bc51d851`
  (2 meshes, 844 verts / 1420 faces each, UV cells included).

## Build
- Clusters: PLT-01 `leaf_cluster` (80 tris, domed, noise ±0.035), D 0.33–0.35, height 0.72 D, depth scaled 0.62,
  centres at Y −0.085; X ±0.155–0.16 left/right, top at (−0.06, 1.775). Heights measured on the reference (575 px/m):
  L 0.48 / 0.84 / 1.19 / 1.56, R 0.66 / 1.10 / 1.52, top 1.78 (reference wins over the spec list 0.45 … 1.95).
- Canes: A/B mirrored sine braid, period 0.86 (crossing every 0.43 m), amplitude 0 → 0.15 (z 0.05–0.62) → 0.08 at the
  top, weaving in depth over/under (centres 0.02–0.06 in front of the plane); Ø0.045 → 0.03. Cane C runs up the left
  edge (x −0.29, as in the reference) and into the top cluster. Lowest 0.36 m bare.
- Blooms: `rose_bloom_v2` ×1.15 (rim Ø0.133, reference ~0.14), on top of each cluster 0.05 toward the front, axis
  tilted 18–24° to the front and 8–12° outward (seen from above, not side-on); visible green neck 0.045.
- 2 closed buds (R2 right, L3 left), Ø0.06, 0.10 tall.

## Rounds (live, 4 of 5)
1. First build 1584 tris: width 0.754, blooms small and sunk, left cane hidden behind the left clusters.
2. Clusters to the reference heights and X ±0.155, D 0.33–0.35 (width 0.696); blooms ×1.15 with a visible neck; cane C
   out to the left edge. Structure matches the reference (diamond braid, alternating drops, a rose on each).
3. Top cluster lowered (height 2.04 → 2.01), stump 8 → 6 sides, 2 closed buds (1600 tris). Buds read as specks.
4. Buds larger (Ø0.06, 0.10), L4 bloom moved outward. Stopped: only nitpicks left.

## 128 px self-check
Reads as a tall narrow climbing rose: green drops alternating left/right on a brown braided cane, a red rose on each
drop, stump at the base. Not a round bush, not a flat sheet of leaves.

## Remaining differences vs reference
- Base: the reference has one short trunk out of the stump that splits at ~0.2 m; here the three canes leave the stump
  separately and the braid crosses once low (z ~0.3).
- Clusters are a little flatter / lumpier than the reference's rounded "heart" drops (PLT-01 generator kept for series
  consistency). No leaf tufts (budget fully used).
- Blooms are rose_bloom_v2 (owner note), not the reference's simple cup.
- Height 2.014 (catalogue 2.0), depth 0.237 (catalogue 0.3 is the allowed maximum).
