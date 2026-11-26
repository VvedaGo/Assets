# PLT-04 Ivy Patch `FMS_Garden_Ivy_Patch` — builder notes (Э7, batch 4, 2026-11-26)

Source of truth: `build.py` (`-- PLT-04 build|export`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback mode;
execute_blender_code and look worked). Live work only in collection `PLT-04_Ivy_Patch` (left in place). Owner's file not
saved; Cube and other collections untouched; selection (Cube) saved before the live export and restored. Shared material
`M_Garden_Flora` reused as is; atlas F loaded read-only (`pc.atlas_image` NOT used) — MD5 `ae0f0dba…` unchanged, palette
cells 0 mismatches. Atlas A not used.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Ivy_Patch.fbx` (+ `.fbm` with the atlas F copy) |
| Blend | `art/AssetNew/Blend/FMS_Garden_Ivy_Patch.blend` (collection only) |
| Preview | `art/AssetNew/Previews/FMS_Garden_PLT_04_Preview.png` (one, series 3/4) |
| Tris / budget | **498 / 500** — Mat (back layer) 126, Middle leaves 114 (19 × 6), Front leaves 144 (24 × 6), Vines 114 (3 × 38) |
| Size X × Y(depth) × Z (Blender) | 1.041 × 0.124 × 1.010 m (catalogue 1.0 × 0.15 × 1.0; tips ≤ 0.04 beyond the 1 m square) |
| Nodes | root empty `FMS_Garden_Ivy_Patch` + `FMS_Garden_Ivy_Patch_Body` (1 mesh, 1 material), scale 1, rot 0 |
| LOD / variants | none (catalogue) |

## Axes, pivot, attachment plane
- Blender X = width, −Y = front (Unity +Z after the −Z-forward export; leaves grow toward it), Z = up (Unity Y).
- Pivot (0, 0, 0) = centre of the bottom edge on the back plane; min z = 0 (lowest hanging leaf tips), X bbox centred.
- Attachment plane Blender Y = 0 (Unity Z = 0): max Y = 0.0000; the back is ONE flat face (26 tris after triangulation,
  0.73 m²) — the back of the mat shell. Nothing else touches the plane: interior mat vertices 12 mm in front, leaves
  ≥ 12 mm, vines' wall-facing faces 14 mm (18 faces parallel to the plane, none coplanar with it).

## Build
- **Mat (back layer, slot 3)**: one closed shell = diamond tiling of 25 flat-based rhombus pyramids (rows 4/3/4/3/4/3/4,
  diamonds 0.25 × 0.24, shared base edges, lattice jitter ±0.022 / ±0.033 at the rim, interior base vertices raised 0.012,
  apex 0.040–0.056 shifted down 0.015), closed by the flat back face. The rim is a zigzag of diamond tips (irregular edge,
  no rectangular slab), bottom of the mat at z 0.03 so the lowest leaves hang below it as in the reference.
- **Leaf** = closed rhombus pyramid (4 front tris + 2 base tris, flat base toward the wall), apex over the centre shifted
  6 % toward the stem; tip points down ±30°, pitched 8–18° out of the wall plane (tip away from the wall).
  Middle (slot 2): 19 on a staggered 4 × 5 jittered grid (one removed on the centre vine for a gap), 0.17–0.21 × 0.15–0.19,
  apex 0.024–0.030. Front (slot 0): 24 on a half-step staggered 4 × 6 jittered grid, 0.19–0.25 × 0.18–0.23,
  apex 0.028–0.034; 4 front leaves use slot 1 on their upward-facing faces. Leaves are kept inside X ±0.54 / Z 0–1.07
  and pushed toward the wall (`settle`) until they overlap the geometry behind them (no floating leaf) and no face lies
  within 2 mm of a parallel foreign face (no coplanar bases).
- **Vines (slot 13)**: 3 at X −0.30 / 0.05 / 0.32, zigzag ±0.03, z 0.10–0.90, 6 segments, 3-sided prism r 0.02 (face to
  the wall, ridge to the front), centre 0.025 in front of the plane, so they sink into the mat apexes and show in the
  gaps between leaves.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 (every shell overlaps another), coplanar overlapping pairs 0.
- ATTACH OK: max Y 0, depth 0.124 ≤ 0.15, width 1.041 ≤ 1.08, height 1.010 ≤ 1.04, min z 0, X centred.
- MOUNT OK (headless, approved FBX imported read-only into the build scene and removed again):
  - MOD-03 `FMS_Garden_Wall_Stone`: back plane 1 mm in front of the coping face (wall Y −0.22 → patch back at −0.221),
    pivot on the ground; 0 patch vertices inside the wall, 0 overlapping face pairs; 21 mm off the wall body (face 0.20)
    below the cap; top 0.41 above the cap stands free (as the spec accepts); width 1.041 ≥ 1.0, so two patches at pitch
    1.0 cover one 2.0 bay (tips overlap by 0.04).
  - MOD-01 `FMS_Garden_Lattice_Panel`: nearest panel surface in the footprint at Y −0.029, back plane 1 mm in front of
    it, pivot at z 0.40; 0 vertices inside, 0 overlaps; patch x ±0.521, z 0.40–1.41 inside the frame (±0.94, 0.05–1.80).
- FBX re-import (live and headless): 2 nodes (empty + mesh), 498 tris, dims 1.041 / 0.124 / 1.010, min z 0, texture found
  in `FMS_Garden_Ivy_Patch.fbm`.
- Headless `build.py -- PLT-04 export`: geometry SHA1 == live `e4b9d7340a3d484894b5baecfbe13bd137a161e0`
  (343 verts / 444 faces, UV cells included).

## Rounds (live, 4 of 5)
1. First build 486 tris: structure right (dark mat, two leaf layers, vines); vines long and over the leaves, leaves narrow
   (gem-like). Two leaves floating at the mat notches.
2. Vines 6 segments, zigzag 0.03, pushed back to 0.03; leaves wider (near-square diamonds); one middle leaf removed on the
   centre vine; `settle` (no floating leaves) + inward slide at the mat notches; coplanar guard for leaf bases (1 pair).
3. Vines 0.025 (in the gaps), lower leaf apexes (less gem-like), front rows start at z 0.13 (no clamped bottom leaves).
4. Half-step stagger of the front rows (two look-alike leaves were stacked bottom-centre). Stopped: only nitpicks left.

## 128 px self-check
Reads as a flat green ivy panel of faceted diamond leaves in 2–3 greens with brown zigzag vines; dark back mass at the
edges; not a bush, not a slab.

## Deliberate deviations from the spec (reference wins, PIPE-04; functional sizes kept)
- Leaf sizes from the reference (≈750 px/m): middle 0.17–0.21, front 0.19–0.25 long (spec 0.14 × 0.10 is much smaller
  than the reference leaves).
- Leaf = closed 6-tri rhombus pyramid (flat base to the wall), not the 8-tri bipyramid: same front look (the reference
  leaves are 4-facet pyramids), and the 2 saved tris per leaf pay for 43 leaves (reference shows ~45) instead of 38.
  Counts 19 middle + 24 front (spec 24 + 14): the reference is dominated by the light front leaves.
- Back layer: one closed diamond-tiled shell (25 pyramids sharing base edges + one flat back face) instead of 30 separate
  rotated pyramids: separate pyramids with bases on Z = 0 would overlap coplanar (z-fighting) or would have to be
  staggered off the wall; the tiling keeps the back exactly flat and closed. No ±15° rotation (tiling), jitter instead.
- Vines: 3-sided prism, 6 segments (spec 6-sided, ~3 segments): the reference vines are tight zigzags; 6-sided × 6
  segments would cost 80 tris each.
- Leaf depth: stems start at 0.016–0.03 (middle) / 0.055–0.07 (front) out (spec bases 0.04–0.08 / 0.08–0.12), and
  `settle` pushes floating leaves further back (up to 0.055) until they touch the layer behind; total depth 0.124 ≤ 0.15.

## Remaining differences vs reference
- The reference mat reads as a thicker slab with a visible dark side wall on the right; here the rim is the zigzag of the
  mat diamonds (thin at the rim, 0.04–0.056 at the apexes).
- The reference's outline is closer to a square; here the top corners show dark mat diamonds and single leaves sticking
  out (inside the ±0.04 tip allowance).
- Vines are visible in fewer, longer gaps on the right than in the reference's many short zigzag bits.
