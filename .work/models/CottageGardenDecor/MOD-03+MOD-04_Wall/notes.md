# MOD-03 Low stone wall `FMS_Garden_Wall_Stone` + MOD-04 Wall pillar `FMS_Garden_Wall_Pillar` — builder notes (Э7, series batch 1, 2026-11-25)

Source of truth: `build.py` (one registry script, `-- MOD-03|MOD-04 build|export|verify|dump`). Live Blender 5.2 via MCP
(add-on reported OUTDATED, fallback mode; execute_blender_code and look worked). Live work only in the collections
`MOD-03_Wall_Stone` and `MOD-04_Wall_Pillar` (left in place). Renders in temporary scenes (removed afterwards). The owner's
file was not saved (unsaved, not dirty before); the default Cube and other collections were not touched; selection
(Cube, active Cube) checked before/after the live export: unchanged.

## Result

| | MOD-03 | MOD-04 |
|---|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Wall_Stone.fbx` (+ .fbm) | `art/CottageGardenDecor/Meshes/FMS_Garden_Wall_Pillar.fbx` (+ .fbm) |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Wall_Stone.blend` | `art/CottageGardenDecor/Blend/FMS_Garden_Wall_Pillar.blend` |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_MOD_03_Preview.png` | `art/CottageGardenDecor/Previews/FMS_Garden_MOD_04_Preview.png` |
| Tris / budget | **464 / 600**: Blocks 432 (36 × 12), Core 12, Coping 20 | **256 / 300**: Blocks 144 (12 × 12), Core 12, Cap 20, Ball 80 |
| Size (Blender X × Y × Z) | 2.000 × 0.440 × 0.600 | 0.500 × 0.500 × 1.0495 |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same |
| LOD | none (catalogue) | none (catalogue) |

- Material `M_Garden_Build` + shared `art/CottageGardenDecor/Textures/FMS_Garden_AtlasA.png` (read only: loaded, never saved;
  MD5 `119daf05…` unchanged; palette check by pixel read: 0 mismatches). Same stone wording/cells as WTR-03 (atlas A):
  **A-12 Stone `#A7A39A`** = main masonry and core, **A-11 Stone light `#C9C3B6`** = limestone (coping, cap, ball) and the
  second-tone blocks. (FLB-01 used the same two colours on atlas F, cells 14/15.) Flat shading (0 smooth faces).
- Two-tone split: wall 8 of 36 blocks in A-11 (4 per side, 22 %), pillar 4 of 12 (33 %, three of them on the camera side as
  in the reference). Next to the A-12 blocks they read clearly, also at 128 px.

## Construction
- Every component is a closed convex box/prism; parts overlap (interpenetrate) instead of touching, so there are no
  coplanar faces. Joint 0.012 everywhere; the joints are 0.01 deep grooves down to the core (blocks 0.01 proud).
- MOD-03: core box X ±0.998 (2 mm inside the flat cut), Y ±0.19, Z 0.003–0.55 (top inside the coping). Front and back
  masonry are separate: blocks Y −0.20…−0.006 and 0.006…0.20 (a 12 mm joint in the middle of the end faces), 4 courses of
  0.135 (block heights 0.123, top course stops 6 mm under the coping = mortar bed). Courses alternate 5 / 4 blocks, face
  lengths 0.34–0.59 (reference ≈ 0.4), joints of neighbouring courses ≥ 0.18 apart, back pattern differs from the front,
  no joint within 0.1 of x = ±0.75 (pillar faces in an assembly → no slivers). End blocks are cut flush on x = ±1.0.
  Coping X ±1.0, Y ±0.22, Z 0.54–0.60, bevel 0.015 on the two long top edges only; short ends sharp.
- MOD-04: core 0.48 × 0.48, Z 0.004–0.75. 3 courses × 4 pinwheel blocks (0.29 along the face × 0.198 deep), chirality
  mirrored per course, so every face shows 2 pieces of different length (0.29 long face + 0.198 end of the neighbour) with
  staggered joints — the quoin look of the reference. Outer faces exactly ±0.25, top course 6 mm under the cap.
  Cap 0.50 × 0.50, Z 0.74–0.80, bevel 0.015 on the top edges. Ball: icosphere 80 tris (Blender subdivisions 2), Ø0.25,
  pole vertex down, sunk 0.5 mm into the cap (≤ 1 mm allowed), top 1.0495.
- "Hidden faces removed" (spec) was read as: no faces between joints/courses; the boxes keep their inner/bottom faces so
  the mesh stays closed (non-manifold 0). Cost: about 4 tris per block, within budget.

## Pivots and axes
- Root (0, 0, 0) = centre of the base for both; rot 0, scale 1. FBX: Y up, −Z forward baked (pc.export).
  Blender (x, y, z) → Unity (−x, z, −y). Wall length along Unity X, thickness along Unity Z.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0, mirror X 0.000000 (core/coping/cap; block pattern and ball
  excluded as asymmetric by design). Coplanar overlapping face pairs 0 (both). Max face non-planarity 0.0000 mm.
- Ground contact: min z 0.0000, bottom course blocks on z 0 (core bottom 3–4 mm higher, hidden).
- SNAP OK (printed by both runs, contract CATALOG «Модули и стыковка» item 2):
  MOD-03 bbox ±1.0 / ±0.22 / 0–0.60, thickness 0.40, coping 0.44 × 0.06; flat cut at x = ±1.0, nothing beyond;
  MOD-03 ↔ MOD-03 butt (+2.0): gap 0.000 mm, coping sections equal at both ends, 0 same-facing coplanar faces (9
  back-to-back contacts inside the joint, hidden). MOD-04 shaft + cap footprint ±0.25, ball sink 0.5 mm, bbox
  0.50 × 0.50 × 1.0495 (±1 mm). Free end: wall end on the pillar node, 0.25 inside the pillar; pillar faces ±0.25 vs wall
  ±0.20/±0.22 do not coincide; wall top 0.60 vs cap underside 0.74 (0.14). Corner (second wall turned 90°): coping overlap
  0.22 × 0.22 inside ±0.25. Wall | pillar and corner wall | pillar: 0 same-facing coplanar faces (only ground faces
  z = 0 facing down overlap — hidden). Straight joint through a pillar: butt gap 0. Doorway (skipped segment): clear 1.50
  (STR-02 1.4 fits). WTR-02: stele back at 0.22 from the wall axis. (Coplanar test validated: duplicate wall → 198 z-fight
  pairs found.)
- FBX re-import: MOD-03 2 nodes / 464 tris / dims 2.0 × 0.44 × 0.6; MOD-04 2 nodes / 256 tris / 0.5 × 0.5 × 1.05; texture
  found in each `.fbm`.
- Headless `build.py -- MOD-0x export` (PACK_ART = %TEMP%/assetnew_check/<ID>/headless_art, so art/ was not overwritten):
  geometry SHA1 == live — MOD-03 `dac03cdcae7f2ed1a7e28d883893885ca39dfc3d`, MOD-04
  `1fbc7abe808e14258bd607f8b463ead81a9c32ea`. No `Tools/blender/__pycache__` left.
- Check renders (reference angle, preview, 128 px thumb, end view, back view, assembly of 4 pillars + 3 walls with a
  corner) in `%TEMP%/assetnew_check/MOD-03|MOD-04/`.

## Rounds (live)
1. Wall blocks too long and brick-like (3 joints per course, up to 0.69) → 5/4 blocks per course, 0.34–0.59. Pillar
   second tone placed like the reference (bottom/top right face, middle short piece on the front face).
2. A 2 mm slit under the pillar cap rendered as a dotted line → top courses end a half joint (6 mm) under the cap/coping,
   reads as a mortar bed.
3. Wall end face read as three strips (front blocks | plain core | back blocks) → face blocks run to ±0.006, the end
   shows coursed masonry with a 12 mm middle joint.
Rounds used: MOD-03 3, MOD-04 2 (of 5).

## Remaining differences vs the references
1. Wall looks longer/lower than the reference (reference ≈ 0.9 m tall per 2 m); height 0.60 is a functional size of the
   snap contract and the spec forbids a taller wall (PIPE-04: functional sizes win).
2. Stone greyer and the limestone lighter/cooler than the beige reference — palette effect (cells 11/12), as WTR-03/FLB-01.
3. Reference blocks have softened edges and the pillar cap overhangs the shaft slightly; the spec forbids extra bevels and
   keeps the cap on the 0.50 footprint.
4. Reference ball looks ≈ 0.27 across; spec caps it at 0.25 (kept). The ball rests on its pole vertex (point contact,
   0.5 mm sunk), as the reference's vertex-up icosphere.
5. Pillar right face falls into the shade of the series key light in the preview (reference lit both faces evenly) —
   lighting only.
