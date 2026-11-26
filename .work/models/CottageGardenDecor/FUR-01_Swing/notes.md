# FUR-01 Garden swing, A-frame `FMS_Garden_Swing` — builder notes (Э7, batch 3, 2026-11-25)

Source of truth: `build.py` (`-- FUR-01 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in the collection `FUR-01_Swing` (left in place,
moving part named `FMS_Garden_Swing_Seat` there); headless the collection is `FMS_Garden_Swing` and the moving part is
the bare `Seat` (make_lod1.py loads the .blend by the asset name and re-exports it, so the final FBX keeps `Seat`).
The owner's file was not saved (is_dirty False after every call), the Cube and the other collections were not touched,
the selection (Cube, active Cube) was checked unchanged. Shared atlas A read only (MD5 `119daf05…` before/after;
palette checked by pixel read: 0 mismatches); atlas F not used and unchanged.

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Swing.fbx` (+ `.fbm` with the atlas copy) — LOD0 + `_Low1` children |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Swing.blend` (collection-only library, headless, LOD0 only) |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_FUR_01_Preview.png` (one, series 3/4 from the front-right) |
| Tris LOD0 / budget | **580 / 1600** — EndFrame_A 48 + EndFrame_B 48 (Legs 2×24, Apex 2×12, Braces 2×12), Beam 36 (beam 12, clamps 24), Seat 448 (SeatBoard 12, Aprons 24, ArmPosts 24, BackPosts 24, Armrests 24, Rails 24, Slats 96, Cushion 60, Brackets 48, Rods 112) |
| Tris LOD1 | 356 (61 %): EndFrame_A/B 48/48 and Beam 36 kept (≤ 60 tris, make_lod1 keeps them), Seat_Low1 224 (50 %) |
| Size X × Y × Z (Blender) | 2.480 × 1.501 × 2.160 (Unity X × Z × Y) |
| Nodes | root empty `FMS_Garden_Swing` + `_EndFrame_A`, `_EndFrame_B`, `_Beam`, `Seat` (+ `_Low1` of each), all direct root children |

Under budget on purpose: the reference is a set of plain boxes and rods; nothing in it needs more geometry.

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint on the ground; FBX Y up, −Z forward baked, scale 1.
- Blender axes: X = along the top beam, −Y = front (Unity +Z), Z = up. Model is X- and Y-symmetric, so the series
  Unity X-flip assumption has no effect (EndFrame_A = Blender −X end).
- **`Seat`** (bench + cushion + 4 hanger rods + 4 corner brackets): pivot on the top-beam axis, Blender (0, 0, 2.04) =
  Unity (0, 2.04, 0); rotation axis X; rest 0°, travel ±30°. Hanger top ends are on that axis (rod sweeps end at
  (±0.84, 0, 2.04)). Static frame parts pivot at the root.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 for every component; mirror X 0.000000 (whole frame before the
  split, Beam, Seat).
- Coplanar overlapping faces 0 per part and 0 for all parts merged.
- Parts touch: EndFrame_A/B ↔ Beam (apex blocks), Beam ↔ Seat (rods into the beam / clamps). Ground: min z 0.0000
  (4 leg feet cut flat on z = 0).
- Functional: seat board top 0.450; seat pivot on the beam axis (0.0000); seat lowest point 0.34 at rest;
  clearance seat → legs/braces/apex at rest **0.165** (≥ 0.15; seat max |x| 0.885, leg inner faces 1.04); swing −30…+30°
  in 5° steps: no overlap with legs/braces/apex, lowest seat point 0.322 (above the ground at every angle).
- SNAP: no contract (free-standing furniture).
- FBX re-import (after make_lod1): 9 nodes (root + 4 meshes + 4 `_Low1`), LOD0 580 + LOD1 356 = 936 tris,
  dims 2.48 / 1.501 / 2.16, min z 0, `Seat` at (0, 0, 2.04) in Blender space, texture found in the `.fbm`.
- Headless `build.py -- FUR-01 export` geometry SHA1 == live SHA1 `2ff94d7fbd76322b50788029127f4cc3586c491a`
  (4 meshes, world positions, UV cells, pivots).
- LOD1 check (`%TEMP%/assetnew_check/FUR-01/FUR-01_lod0.png` | `FUR-01_lod1.png`): frame identical, bench, slats,
  cushion and brackets hold; in `Seat_Low1` the front hanger rod on the −X side thins to a line and the others thin a
  little (decimation of the 8-sided rods; distance LOD, accepted like the STR-03 bench legs).

## Build (what is where, Blender coordinates)
- Legs: 4 plain 0.12 square posts (12 tris each, spec) in the frame planes X ±1.10, from the foot (Y ±0.687, cut flat
  on z = 0; outer leg faces at Y ±0.75 → depth 1.50) to the apex point (Y 0, z 2.04) on the beam axis.
- Apex blocks: 0.14 (X 1.03–1.17, 1 cm proud of the legs) × 0.20 × 0.24 (z 1.92–2.16), hide the leg crossing (reference).
- Top beam 0.12 square, X ±1.24, axis z 2.04 (top 2.10): ends stand 7 cm past the apex blocks (reference stub).
- Cross-braces: 0.10 square at z 0.45 (spec) in the frame planes, ends on the leg centre lines, dark wood slot 1.
- Iron clamps (slot 13, static, in `Beam`): 0.08 × 0.15 × 0.13 under the beam at X ±0.84 (z 1.93–2.06), 1.5 cm proud
  of the beam sides.
- Seat board 1.60 × 0.45 × 0.05 (z 0.40–0.45), front/rear aprons 0.04 × 0.055 under it, 1 cm inset (front face reads
  0.10 deep as in the reference).
- Side frames: front arm posts 0.06 square (z 0.355–0.705), back posts 0.06 square leaning back 10° (top z ≈ 1.04),
  armrests 0.09 × 0.065 (z 0.70–0.765) from 2 cm in front of the arm post into the back post.
- Backrest (10° back): bottom rail and top rail 0.04 deep between the back posts (top rail top z ≈ 1.00), 8 vertical
  slats 0.05 × 0.03 (reference), 1 cm into the rails.
- Cushion 1.40 × 0.39 × 0.10 (z 0.445–0.545, 5 mm sunk into the board), 8-sided chamfered outline with softened top and
  bottom edges; cream slot 3, bottom bevel slot 4.
- Hangers: 4 rods, 8-sided, 0.035 across flats (≥ 0.03), slot 13, in the planes X ±0.84, from the beam axis
  (±0.84, 0, 2.04) through (±0.84, ±0.22, 0.50) down to z 0.44 inside iron corner brackets 0.10 × 0.06 × 0.13
  (X 0.785–0.885, z 0.34–0.47) that wrap the seat corners. Narrow V (0.44 at the seat) as the spec assumes; no chains.

## Deviations from `prompts/FUR-01.3d.md` / the catalogue (for the reviewer)
1. **Width 2.48 instead of 2.40** (beam X ±1.24 instead of ±1.20): the reference shows the beam ends standing out past
   the apex blocks; with ±1.20 the stub would be 3 cm and invisible. +3.3 %.
2. **Apex blocks added** (not in the spec parts table, clearly in the reference): top 2.16 → height 2.16 instead of 2.10
   (+2.9 %). Beam axis 2.04 / top 2.10 unchanged.
3. **Hanger plane X ±0.84 instead of ±0.80**: with the 1.6 m bench (spec) the rods at ±0.80 would run through the side
   frames and armrests; the reference shows the rods just outside the bench ends. Seat-to-leg clearance stays ≥ 0.15
   (0.165). The rod line still passes the spec's seat-corner point (±0.22 at height 0.50).
4. **Backrest = posts + rails + 8 slats** instead of a single 1.6 × 0.40 × 0.04 board; top ≈ 1.00 (backrest about 0.45
   above the cushion, reference) instead of 0.40 high. Leaning 10° back as in the spec.
5. **Cushion 0.10 thick instead of 0.08** (reference), 0.39 deep instead of 0.40 (clears the backrest rail).
6. **Iron clamps under the beam and iron corner brackets on the seat**: both in the reference, not in the spec table.
7. **Frame exported as three static parts** (EndFrame_A, EndFrame_B, Beam) instead of one: make_lod1 halves every part
   over 60 tris, and halving the 132-tri frame of 12-tri boxes turned legs into wedges and braces into slivers (round 4).
   Parts of ≤ 60 tris are kept, so LOD1 saves tris only on the Seat (580 → 356).

## Rounds (4 of 5: 1 headless smoke run + 3 live)
1. Headless first build: checks clean except 2 coplanar pairs (arm-post bottoms on the apron bottom plane) → posts
   raised 5 mm. Worst differences vs the reference: backrest too low, armrests and cushion thin, apex blocks / beam stub
   too weak.
2. Live: backrest top ≈ 1.0, armrests 0.09 × 0.065, cushion 0.10, apex blocks to 2.16, beam ±1.24. Reference view,
   3/4, swing-30° and 128 px thumbnail checked: silhouette reads as an A-frame swing bench at 128 px.
3. Live: reference camera moved to front-right / wide lens. Only perspective and palette differences left — stopped
   modelling here.
4. Live + headless: LOD1 check showed the decimated frame broken → frame split into 3 parts ≤ 60 tris. Geometry
   unchanged; live SHA1 == headless SHA1.

Remaining differences (nitpicks): the reference is a wide-angle picture with strong convergence, so its A-frames look
more splayed and the bench looks larger relative to the frame (the bench is 1.6 m by spec and must keep 0.15 m from
the legs); the cross-braces in the reference sit a little lower (about 0.3–0.5 m, spec 0.45 kept); the light wood is
paler and the cushion cooler/whiter than the reference (palette decision); the braces are dark wood slot 1 (spec),
the reference draws them in the same wood, only shaded.
