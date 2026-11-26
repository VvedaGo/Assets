# STR-03 Arbor with bench `FMS_Garden_Arbor_Bench` — builder notes (Э7, batch 2, 2026-11-25)

Source of truth: `build.py` (`-- STR-03 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in the collection `STR-03_Arbor_Bench` (left in
place); headless the collection is `FMS_Garden_Arbor_Bench` (make_lod1.py loads it by the asset name). The owner's file
was not saved (is_dirty False after every call), the Cube and the other collections were not touched; the selection
(Cube, active Cube) was checked unchanged after the live export.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Arbor_Bench.fbx` (+ `.fbm` with the atlas copy) — LOD0 + `_Low1` children |
| Blend | `art/AssetNew/Blend/FMS_Garden_Arbor_Bench.blend` (collection-only library, headless, LOD0 only) |
| Preview | `art/AssetNew/Previews/FMS_Garden_STR_03_Preview.png` (one, series 3/4 from the front-right) |
| Tris LOD0 / budget | **1276 / 1600** — Frame 340 (Posts 112, Rafters 168, CrossSlats 60), Panels 840 (Rims 96, LatticeSide 432, LatticeBack 312), Bench 96 (Seat 12, Legs 48, Rails 36) |
| Tris LOD1 | 638 (50 %): Frame_Low1 170, Panels_Low1 420, Bench_Low1 48 (`make_lod1.py`, palette re-snapped) |
| Size X × Y × Z (Blender) | 1.800 × 0.800 × 2.300 |
| Nodes | root empty `FMS_Garden_Arbor_Bench` + `_Frame`, `_Panels`, `_Bench` (+ `_Low1` of each) + empties `Plant_L`, `Plant_R`, `Plant_Top` |

- Material `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only; MD5 `119daf05…` unchanged before/after;
  palette checked by pixel read: 0 mismatches). Slots: everything 10 white paint, seat 0 light wood.
- Three mesh parts (not one Body) so that make_lod1 halves each role separately.

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint on the ground; rot 0, scale 1. FBX Y up, −Z forward baked; all parts pivot at the root.
- Blender axes: X = across, **−Y = front / open side** (Unity +Z), Z = up. Back wall at Blender Y +0.34 (Unity Z −0.34).
- Empties: `Plant_L` (−0.84, 0, 0), `Plant_R` (+0.84, 0, 0), `Plant_Top` (0, 0, 2.30) (Blender X, Y, Z). Bare names in the
  FBX and in the headless .blend; in the live file they are `FMS_Garden_Arbor_Bench_Plant_*` (STR-01 uses the same
  bare names), renamed only for the live export. Same Unity X-flip note as STR-01 (symmetric model, no effect).

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 for every component; mirror X 0.000000 (Frame, Bench; Panels
  with the back lattice excluded — its two slat layers are not mirror images by construction, as in STR-01/MOD-01).
- Coplanar overlapping faces 0 per part and 0 for all parts merged.
- Parts touch: Frame ↔ Panels ↔ Bench (BVH overlap). Ground contact: min z 0.0000 (4 posts + 4 bench legs on the ground).
- SNAP OK: inner clear width 1.560 (≥ 1.5), seat top 0.450, width 1.800, depth 0.800, height 2.300, empties at the
  spec positions. INFO: rafter underside at the opening edge 1.995, at the centre 2.148; rafter seats on the posts 1.95.
- FBX re-import (after make_lod1): 10 nodes, LOD0 1276 + LOD1 638 = 1914 tris, dims 1.8 / 0.8 / 2.3, texture found in the .fbm.
- Headless `build.py -- STR-03 export` geometry SHA1 == live SHA1 `6ed39497332cca22c9ec673c383a04ae6e11edcf`
  (3 meshes + 3 empties with positions and UV cells).
- LOD1 checked visually (`%TEMP%/assetnew_check/STR-03/STR-03_lod_check.png`, LOD0 | LOD1): silhouette, arch, lattice and
  seat colour hold; the bench legs collapse to wedges and some lattice crossings flatten (distance LOD, acceptable).

## Build (what is where)
- Posts 0.12 square, 0.01 chamfer (8-sided), centres X ±0.84, Y ±0.34, z 0 → 1.97 (top 2 cm inside the rafter seat).
- Rafters (front Y −0.34, rear +0.34): 0.10 thick plate, outline = flat seat on the post top (z 1.95, X ±0.775…±0.895),
  8-segment top arc from 2.05 at the ends to the crown 2.248, inner arc 0.10 below it; flat faces.
- Cross slats 5 × 0.06 square at X −0.72, −0.36, 0, 0.36, 0.72, radial to the arc, 8 mm seated into the rafters,
  length 0.77 (Y ±0.385, 5 mm inside the rafter outer faces); slat tops at the crown = 2.30.
- Side panels in the post plane X ±0.84 (Y ±0.282, 2 mm into the posts, z 0.15–1.94); back panel at Y +0.34
  (X ±0.782 into the rear posts, z 0.44–1.94, its bottom rim 1 cm inside the seat). Rim = one closed frame ring 0.05 × 0.05.
  Lattice = the shared construction of STR-01 (`lattice()`): 45° slats, two layers overlapping 1.6 cm in depth, ends cut
  square half-way inside the rim, real gaps edge to edge; slat 0.05 wide (MOD-01 / reference) × 0.03 deep, 0.10 clear gap.
- Bench: seat slab X ±0.79 (1 cm into the front and rear posts), Y −0.30 → +0.32 (into the back rim), z 0.38–0.45;
  4 legs 0.09 square at X ±0.62 (Y −0.24 / +0.255); front rail under the seat edge (0.06 × 0.105, between the legs);
  side rails 0.04 front leg → rear leg. All rails/legs 5–10 mm into the seat.

## Deviations from `prompts/STR-03.3d.md` / the reference (for the reviewer)
1. **Arch crown 2.248 instead of 2.30** (rafter outer top): the spec also puts cross slats ON the curve and the catalogue
   height is 2.30 with `Plant_Top` at 2.30. With the crown at 2.30 the model would be 2.36 tall and `Plant_Top` inside a
   slat; lowered so the slat tops end at 2.30. The rise (0.20) is still a little more than the reference's (~0.18).
2. **Seat 1.58 × 0.62 × 0.07 instead of 1.5 × 0.45 × 0.05**: the spec's own rules ("bench attached to the posts and
   lattice", "lattice back starts at the seat") and the reference (seat spans post to post and reaches the back lattice)
   need the seat to touch both; with the spec's front edge (Unity Z +0.30) and back wall (−0.34) that is 0.62 deep.
   Thickness 0.07 measured on the reference (~0.08). Seat top 0.45 kept (functional).
3. **Supports: 4 legs 0.09 + front rail + side rails** instead of "2 side supports 0.06 wide": the reference shows square
   legs (≈0.09) with a front apron; STYLE asks for chunky furniture members. Front rail is between the legs (1.17 long),
   not 1.5.
4. **Cross slats 0.77 long instead of 0.68** so they cover both rafters to their outer faces, as in the reference.
5. Rafter ends at X ±0.895 (5 mm inside the post outer faces) and post tops 1.97 inside the rafter: avoids coplanar end
   faces / caps; panel tops 1.94 (1 cm under the post-top plane) for the same reason.
6. Lattice slats 0.05 wide (task: identical to MOD-01; spec "about 0.03"; reference ≈0.05) with the spec's 0.10 gaps.

## Rounds (live, 3 of 5)
1. Live build = headless first build, all checks clean (first headless run found: crown slat tilted → mirror 0.008,
   height 2.357, seat-height probe wrong → fixed before the live round). Worst difference: comparison camera mirrored.
2. Reference camera fixed (the reference is seen from the front-right: rear posts shift right). Sheet reference | render:
   silhouette, lattice density, back panel from the seat up, light-wood seat on a white frame all match. Worst
   differences: seat too thin, legs thin (0.08) vs the reference.
3. Seat 0.07, legs 0.09; reference camera ~30° / 70 mm. Thumbnail 128 px reads (white lattice box, arch with slats,
   orange seat). Stopped: only nitpicks / palette / camera left.

Remaining differences (nitpicks): white is cooler than the reference cream (pack palette decision); the cross slats stand
6 cm proud on the arch (reference slats look flatter, closer to flush); the reference has a little overhang of the
arch ends past the posts (not in the spec, not modelled); the reference picture has an inconsistent perspective (seat
seen almost edge-on, arch top from above), so the comparison camera is a compromise.
