# STR-04 Pergola `FMS_Garden_Pergola` + STR-05 Pergola bay `FMS_Garden_Pergola_Bay` — builder notes (Э7, batch 2, 2026-11-25)

Source of truth: `build.py` (one registry script, `-- STR-04|STR-05 build|export|verify|dump|lodcheck`). Live Blender 5.2
via MCP (add-on reported OUTDATED, fallback mode; execute_blender_code and look worked). Live work only in the collections
`STR-04_Pergola` and `STR-05_Pergola_Bay` (left in place). The owner's file was not saved (no file path, is_dirty False after
the session); the Cube and the other collections were not touched; selection (Cube, active Cube) saved before the live
export and restored; no TMP scenes/objects left. Shared atlas A loaded read only (`pc.atlas_image` not used): MD5
`119daf0562690ceb5916362cdf5f2b69` unchanged, palette 0 mismatches; atlas F not used (MD5 `ae0f0dba…` unchanged).
`M_Garden_Build` reused.

## Result

| | STR-04 `FMS_Garden_Pergola` | STR-05 `FMS_Garden_Pergola_Bay` |
|---|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Pergola.fbx` (+ `.fbm`) | `art/CottageGardenDecor/Meshes/FMS_Garden_Pergola_Bay.fbx` (+ `.fbm`) |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Pergola.blend` | `art/CottageGardenDecor/Blend/FMS_Garden_Pergola_Bay.blend` |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_STR_04_Preview.png` | `art/CottageGardenDecor/Previews/FMS_Garden_STR_05_Preview.png` |
| LOD0 tris / budget | **332 / 1600** — Posts 112, Beams 24, Rafters 196 | **248 / 1000** — Posts 56, Beams 24, Rafters 168 |
| LOD1 tris (`make_lod1.py`) | 178 (54 %) — Posts 56, Beams 24, Rafters 98 | 164 (66 %) — Posts 56 (≤ 60 tris, kept), Beams 24, Rafters 84 |
| Size (Unity X × Z × Y) | 3.50 × 3.50 × 2.62 | 3.00 × 3.50 × 2.62 (beams Unity X 0.25 → 3.25) |
| Nodes | root empty + `_Posts`, `_Beams`, `_Rafters` (+ 3 `_Low1`) | same |

- One mesh object per role (Posts / Beams / Rafters) so that make_lod1 halves each role separately (STR-06 lesson); one
  material, cells 0 light wood (= STR-01) and 1 dark wood (rafter cut ends).
- The `.blend` libraries carry the collection under the asset name (make_lod1 looks it up by it); live the collections are
  `STR-04_Pergola` / `STR-05_Pergola_Bay` (renamed only while writing the library).

## Axes, pivots, snap direction
- Blender (x, y, z) → Unity (−x, z, −y) (Unity's FBX import negates X; same convention as STR-01 / MOD-06).
- STR-04 pivot: centre of the footprint on the ground. STR-05 pivot: middle of the shared post line on the ground.
- **The bay is built at Blender −X** (posts at Blender x −3.0, beams −3.25 … −0.25) so that it extends to **Unity +X**
  as the contract says. Placement: STR-05 = STR-04 pivot + Unity (1.5, 0, 0); next STR-05 = previous + (3.0, 0, 0).
  To confirm at the first Unity import (Э8) together with MOD-06 / STR-01: the bay's posts must land at Unity X +3.0. If
  they land at −3.0, the X-flip assumption is wrong: rotate the bay prefab 180° about Y (the module is symmetric in Z).

## Build
- Posts 4 (STR-04) / 2 (STR-05): 0.18 × 0.18, 0.01 chamfer on the long edges (8-sided), centres (±1.5, ±1.5) / (3.0, ±1.5),
  z 0 → 2.245 (top seated 5 mm in the beam: no coplanar post-top / beam-underside faces).
- Beams 2: 0.10 (Z) × 0.22, underside 2.24, top 2.46, X −1.75 … 1.75 (STR-04) / 0.25 … 3.25 (STR-05), plain square ends.
- Rafters 7 / 6: 0.08 wide, z 2.455 → 2.62 (bottom seated 5 mm in the beam top, so beam top and rafter bottom are not a
  coplanar pair; plants still rest on the beam top at 2.46), Z ±1.75 (overhang 0.25). End: stepped point in side view —
  vertical end face 0.075 high, steep 45° chamfer (0.05 long), shallow ~18° chamfer to the top (0.12 long); end face and steep
  chamfer dark wood (slot 1), shallow chamfer and the rest light (slot 0). +8 tris per end over a plain box. The cut starts
  0.03 outside the beam face.
- STR-05 has no post and no rafter on its joining line (x = 0): the neighbour owns them.

## Checks (live = headless)
- Whole model: non-manifold 0, loose 0, degenerate 0, every member touches another (worst gap 0.00000), mirror X 0.000000
  (STR-04; STR-05 asymmetric by design). Coplanar overlapping faces 0 per part and 0 for all parts merged.
- Ground contact: min z 0.0000 (posts on the ground). Part contacts: Posts↔Beams, Beams↔Rafters (seated).
- Functional sizes: beam underside 2.240, beam top 2.460, rafter top 2.620; bbox exactly as specified (±1.75 / −3.25 … −0.25).
- **SNAP OK** (catalogue «Модули и стыковка» item 5), printed for both pairs:
  - STR-04|STR-05 (bay at Unity +1.5): both beam joints at Unity X 1.75, gap 0.000 mm, identical section; 2 posts on the
    shared line (both STR-04), bay posts at Unity 4.5, post-line pitch 3.0; 13 rafters, pitch 0.5 continuous, 0 duplicates;
    no volume overlap between the modules; beam underside/top and rafter top equal.
  - STR-05|STR-05 (bays at +1.5 / +4.5): same, joint at Unity X 4.75, 12 rafters pitch 0.5, 0 duplicates.
  - Real meshes STR-04 + STR-05 + STR-05 merged: coplanar pairs 4 = exactly the 2 joints × 2 beams (beam end faces back to
    back, both hidden). Visual: `%TEMP%/assetnew_check/STR-05/STR-05_assembly_live.png` (seam invisible, rafters continuous).
- **PLT-03 garland on a beam** (approved FBX, read only, temporary scene): pivot centred on the front beam top
  (STR-04 x 0 / STR-05 Unity x 1.75, z 2.46): min z 2.4600, its 8 lowest vertices (the cane low points) all over the
  beam top (beam |y| ≤ 0.05 around the beam axis), garland 1.571 within the beam length → OK. The foliage passes through
  3 (STR-04) / 4 (STR-05) rafters (decoration, no collider; same as on the STR-01 top). Check renders
  `%TEMP%/assetnew_check/STR-0x/STR-0x_rose_mount_*.png`.
- FBX re-import (after make_lod1): STR-04 7 nodes (empty + 3 + 3 `_Low1`), 332 + 178 = 510 tris, dims 3.5 / 3.5 / 2.62,
  min z 0, texture found in `FMS_Garden_Pergola.fbm`; STR-05 7 nodes, 248 + 164 = 412 tris, dims 3.0 / 3.5 / 2.62, texture
  found in `FMS_Garden_Pergola_Bay.fbm`.
- Headless `build.py -- <ID> export`: geometry SHA1 == live — STR-04 `f64399f7fe20d6594124e7c0b0b6df492b1742f8`,
  STR-05 `107f8020a04ce9ab461a567f829642a0cc318f87` (all meshes, UV cells included). Final art files are from the headless
  export + make_lod1.
- LOD1 checked visually (`%TEMP%/assetnew_check/STR-0x/STR-0x_LOD1.png`): silhouette, rafters and dark ends hold; the
  rafter tips flatten to a single slope; STR-04 posts become 4-sided.

## Deviations from the spec / catalogue (for the reviewer)
1. **Posts 0.18** (spec 0.16, "not thinner than 0.16"): the reference posts measure ≈ 0.18 (post width / roof width
   0.051 in the reference vs 0.044 with 0.16). Snap contract unaffected (centres unchanged).
2. **Rafters 0.08 wide** (spec 0.06, minimum 0.06): reference ≈ 0.09 (tips ~30 px at ~315 px/m); 0.08 keeps the 0.5 pitch
   airy. Height 0.165 (0.16 + 5 mm seat in the beam); top 2.62 unchanged.
3. Posts end at 2.245 and rafters start at 2.455 (5 mm seats instead of touching planes) — the spec forbids coplanar
   overlaps; the functional heights 2.24 / 2.46 / 2.62 are exact.
4. Rafter overhang 0.25 at both ends (spec). The reference shows the front rafter ends almost flush with the front beam and
   a longer overhang at the back (inconsistent picture); the symmetric spec overhang is kept.
5. STR-05 reference has plain square rafter ends; the spec requires the STR-04 end cut on the bay ("do not change the end
   cut") — kept, so a run of modules reads as one pergola.
6. Catalogue size of STR-05 "3.25×3.5×2.62" is the far beam end (X 0.25 → 3.25); the real extent is 3.00 × 3.50 × 2.62.

## Rounds (live: STR-04 2 of 5, STR-05 1 of 5)
0. Headless first build of both (spec numbers): checks clean, SNAP OK; PLT-03 mount check fixed (temporary-scene view
   layer was not updated, so the garland was measured at the origin).
1. STR-04 live = headless. Worst differences vs reference: rafters thinner (0.06 vs ≈ 0.09), posts slightly thinner,
   camera a little higher than the reference. → rafters 0.08, posts 0.18, comparison camera lowered.
2. STR-04 after the fixes: proportions, rafter tips and post weight match the reference; 128 px thumbnail reads as an open
   pergola. Only nitpicks left (front rafter overhang, tip size).
1. STR-05 (same parts): matches its reference (two posts at the far end, open joining end); assembly render checked.
   Export live + headless, make_lod1, verify.

Remaining differences (nitpicks): front rafter overhang vs the reference (4.), bay rafter ends cut instead of plain (5.),
wood tone per palette slot 0 (same as STR-01).
