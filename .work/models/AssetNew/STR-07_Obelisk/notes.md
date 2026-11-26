# STR-07 Obelisk `FMS_Garden_Obelisk` (+ `_White`) — builder notes (Э7, batch 2, 2026-11-25)

Source of truth: `build.py` (`-- STR-07 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in collection `STR-07_Obelisk` with the child collection
`STR-07_Obelisk_White` (left in place). The owner's file was not saved (not dirty); the default Cube and the other
collections were not touched; the selection (Cube, active Cube) was restored after the live export.

## Result

| | base | `_White` |
|---|---|---|
| FBX | `Meshes/FMS_Garden_Obelisk.fbx` (+ .fbm) | `Meshes/FMS_Garden_Obelisk_White.fbx` (+ .fbm) |
| Tris / budget | 236 / 500 | 236 / 500 |
| Size X × Y × Z (Blender) | 0.600 × 0.600 × 1.900 | same (same vertices, checked) |
| Nodes | root empty `FMS_Garden_Obelisk` + `FMS_Garden_Obelisk_Body` | same with `_White` |

- Tris per component: Posts 48 (4 × 12), Bands 96 (3 × 32), Collar 12, Ball 80 (icosphere subdivisions 2).
- One `.blend` (`Blend/FMS_Garden_Obelisk.blend`) holds both collections; ONE preview (`Previews/FMS_Garden_STR_07_Preview.png`, base).
- Material `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette checked
  by pixel read: 0 mismatches). Base: everything slot 0 (light wood, same as STR-01); `_White`: everything slot 10.
- No LOD (catalogue).

## Pivot and axes
- Root (0, 0, 0) = centre of the footprint on the ground; rot 0, scale 1. FBX Y up, −Z forward baked.
- Blender: X right, −Y front, Z up. The obelisk is the same from all four sides (rotation-90 check 0.000000 for posts,
  bands and collar; only the icosphere is not 90°-symmetric, it is X-mirror symmetric).

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0; mirror X 0.000000.
- Coplanar overlapping faces 0 (object and merged).
- Ground contact: min z 0.0000, 16 ground vertices (4 post feet, cut flat on z = 0); no base plate, nothing below 0.
- Contacts: every band rail end buried 0.070–0.076 in each post, rail outer face 5–11 mm inside the post face; post outer
  faces at the collar bottom ±0.0905 inside the collar ±0.095; post tops (z 1.73) inside the collar (1.70–1.77);
  ball bottom 1.74, 3 cm in the collar; posts do not touch each other (gap 0.0116 at their tops).
- Sizes: footprint 0.600 × 0.600 centred, height 1.900 (ball pole vertex). No SNAP contract for STR-07.
- FBX re-import: base 2 nodes / 236 tris, `_White` 2 / 236; dims 0.6 / 0.6 / 1.9; texture found in each `.fbm`.
- Headless `build.py -- STR-07 export` geometry SHA1 == live SHA1 `2128c128472c26dd29396cc7d2e7969304363397`.

## Build (what is where)
- Posts: sheared square prisms with HORIZONTAL 0.081 sections (faces axis-aligned, front faces face the viewer as in the
  reference). The posts lean ~7° per axis, so the true perpendicular section is 0.0804 (≥ 0.08). Axis from base centres
  (±0.2595, ±0.2595) at z 0 (outer base box exactly 0.60) through (±0.05, ±0.05) at z 1.70, continued to z 1.73 inside
  the collar; feet and tops cut horizontally.
- Bands: 3 closed square rings, section 0.05 × 0.05, centres z 0.36 / 0.90 / 1.40, outer face 8 mm inside the post outer
  face at the band centre (rails run between the posts, corners buried in the posts).
- Collar: box 0.19 × 0.19 × 0.07, z 1.70–1.77.
- Ball: icosphere Ø0.16, subdivisions 2 (80 faceted tris), centre z 1.82, pole on top at exactly 1.90.

## Deviations from `prompts/STR-07.3d.md` (for the reviewer / spec owner)
1. **Collar 0.19 × 0.19 × 0.07 at 1.70–1.77** (spec 0.14 × 0.14 × 0.10 at 1.66–1.76). With 0.08 posts and top centres at
   ±0.05 (spec) the post outer faces are at ±0.09 at the collar, so a 0.14 collar cannot join them (the posts would pierce
   its sides); posts may not overlap each other either (their front faces are coplanar). The reference collar is as wide
   as the post cluster and flatter (h ≈ 0.6 × width), and it starts higher (~1.75 measured), so it sits at 1.70–1.77.
2. **Ball subdivisions 2** (80 facets) instead of 1: Blender's subdivision 1 is a bare 20-face icosahedron; the reference
   ball shows ~80 facets; the spec's "What NOT to do" allows 1–2.
3. **Bands at 0.36 / 0.90 / 1.40** (spec 0.35 / 0.85 / 1.35): reference measured through a calibrated camera at
   ~0.37 / 0.96 / 1.39 (screen-even spacing); mid band set between spec and reference.
4. **Bands between the posts, not wrapping outside** (spec wording "wrapping the outside"): the reference rails run between
   the posts, faces about flush; a ring 8 mm proud showed corner "ears" in round 1.
5. **Colour slot 0 light wood** (spec says slot 2 medium wood): the dispatch says "same wood/white as STR-01" (slot 0) and
   the reference colour (~#C8844F) is closer to slot 0 (#B5835A) than slot 2 (#9C6B44). One constant (`WOOD` → `WOOD_M`
   in `build_obelisk(...)`) if slot 2 is wanted.
6. Post tops buried 3 cm into the collar (z 1.73) on the same axis, so the visible posts meet the collar at the spec point.

## Rounds (live, 2 of 5)
0. Headless first build from the spec numbers: 236 tris, all checks clean; the collar conflict (deviation 1) found.
1. Live build = headless. Compared with the reference (full + crops of the band joint and the top): bands wrapped outside
   with corner ears → rails between the posts; ball small vs collar (ref ball ≈ collar width) → collar flatter/higher.
   Comparison camera found (~27° yaw from the front-right, ~28° above, 28 mm: the 4 legs evenly spaced as in the reference).
2. Band heights measured through that camera (projection of the front-left post) → 0.36 / 0.90 / 1.40; collar 1.70–1.77,
   ball back to the spec Ø0.16. Sheet reference | ref-view | 3/4 | 128 px: reads as a four-sided obelisk with a faceted
   ball at 128 px. Export live + headless.

## Remaining differences vs the reference (nitpicks / spec-driven)
- Posts are chunkier (0.08 by STYLE/spec vs ~0.045 in the picture), so the whole obelisk reads heavier; the reference
  also looks ~10 % wider at the base relative to its height (camera-dependent; kept the catalogue 0.6 × 0.6 footprint).
- Top cluster (collar + ball, 0.20 m) is larger than in the reference (~0.13–0.15 m) because the collar must contain the
  thicker posts and the ball keeps the spec Ø0.16 (ball/collar 0.84 vs ≈ 1.0 in the reference).
- Colour: light wood slot 0 is a little paler / less orange than the reference.
