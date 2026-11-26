# MOD-07 Pond edge `FMS_Garden_Pond_Edge` + MOD-08 Pond edge corner `FMS_Garden_Pond_Edge_Corner` + MOD-09 Pond water `FMS_Garden_Pond_Water` — builder notes (Э7, series batch 2, 2026-11-25)

Source of truth: `build.py` (one registry script, `-- MOD-07|MOD-08|MOD-09 build|export|verify|dump`). Live Blender 5.2 via
MCP (add-on reported OUTDATED, fallback mode; execute_blender_code and look/renders worked). Live work only in the
collections `MOD-07_Pond_Edge`, `MOD-08_Pond_Edge_Corner`, `MOD-09_Pond_Water` (left in place). Renders in temporary
scenes (removed afterwards). Owner's file unsaved and not saved by me; default Cube and other collections untouched;
selection (Cube, active Cube) checked before/after the live export: unchanged.

## Result

| | MOD-07 | MOD-08 | MOD-09 |
|---|---|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Pond_Edge.fbx` (+ .fbm) | `…/FMS_Garden_Pond_Edge_Corner.fbx` (+ .fbm) | `…/FMS_Garden_Pond_Water.fbx` (+ .fbm) |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Pond_Edge.blend` | `…/FMS_Garden_Pond_Edge_Corner.blend` | `…/FMS_Garden_Pond_Water.blend` |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_MOD_07_Preview.png` | `…/FMS_Garden_MOD_08_Preview.png` | `…/FMS_Garden_MOD_09_Preview.png` |
| Tris / budget | **76 / 120**: Shell 28 (core + coping), Blocks 48 (4 × 12) | **56 / 60**: Shell 32, Blocks 24 (2 × 12) | **36 / 50**: top 18, sides 16, bottom 2 |
| Size Unity W × D × H | 1.000 × 0.370 × 0.450 | 0.370 × 0.370 × 0.450 | 1.000 × 1.000 × 0.040 (Y 0.34–0.38) |
| Pivot | middle of the inner face, ground | inner corner of the basin, ground | centre of the base, ground (slab raised 0.34) |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same | same |
| LOD | none (catalogue) | none | none |

- Material `M_Garden_Build` + shared `art/CottageGardenDecor/Textures/FMS_Garden_AtlasA.png` (read only: loaded, never saved; MD5
  `119daf05…` unchanged, same file copied into each `.fbm`; palette pixel check 0 mismatches). Cells exactly as MOD-03 /
  FLB-01: **A-12 Stone `#A7A39A`** = core and main blocks, **A-11 Stone light `#C9C3B6`** = coping and second-tone blocks.
  Water as WTR-03: **A-15 `#4A78A8`**, opaque, same material, no transparency. Flat shading (0 smooth faces).
- No variants, no LOD (catalogue rows).

## Construction (Blender axes; Blender (x, y, z) → Unity (−x, z, −y), so Unity Z = −Blender y)
- MOD-07: one closed **shell** = core + coping as a prism along x (−0.5…0.5) from an 8-point section: core y 0…0.34,
  z 0.003…0.40; coping y 0…0.37, z 0.40…0.45 with the 0.015 bevel on the outer long top edge only; ends flat and sharp.
  The inner face (y = 0) is two flat coplanar faces sharing an edge (core A-12 below z 0.40, coping band A-11 above) —
  no relief, one plane. End faces: core quad + coping fan (no degenerate triangles). **Blocks**: 2 courses (z 0…0.194,
  0.206…0.394: 12 mm joint, 6 mm mortar bed under the coping), 2 blocks each, outer face y 0.35 (0.01 proud of the core),
  back face 0.33 inside the core; joints at x +0.02 (bottom) / −0.12 (top), lengths 0.37–0.61; blocks stop 6 mm short of
  the ends, so neighbouring edges show the same 12 mm joint. Light blocks: top course right / bottom course left in the
  reference view (2 of 4, as the reference; the spec says "about one in four" — the picture wins).
- MOD-08: one closed shell (core 0…0.34², coping 0…0.37², two mitred 0.015 bevels on the outer top edges only, inner butt
  faces x = 0 and y = 0 flat, split at the coping like MOD-07 so their section equals the MOD-07 end section exactly).
  Two **quoin stones** (one per course, same course heights as MOD-07, wrap the outer corner, faces 0.35, 6 mm short of
  the butt faces): bottom A-12, top A-11 (the reference is light next to the corner on top, dark below).
- MOD-09: slab ±0.5, z 0.34…0.38; top 3 × 3 quads = 18 triangles (diagonals alternate), all 12 border vertices exactly at
  0.38; 4 inner vertices lowered by 1–5 mm (−4, −1, −2, −5 mm; only downwards so the bbox stays 0.04 and the top stays at
  0.38). Sides 4 triangles each (no degenerate ones), bottom 1 quad.
- Core bottoms 3 mm above the ground (blocks own z 0) — same trick as MOD-03, avoids coplanar bottoms; hidden.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 (all three); mirror X 0.000000 (MOD-07 shell; blocks, corner and
  water excluded as asymmetric by design); coplanar overlapping face pairs 0 (all three); max face non-planarity 0.0000 mm.
- Ground contact: MOD-07 / MOD-08 min z 0.0000 (bottom course on the ground); MOD-09 min z 0.34 by design (pivot on the
  ground, slab raised inside the mesh).
- **SNAP OK** (printed by every run, contract CATALOG «Модули и стыковка» item 4): MOD-07 bbox ±0.5 / 0…0.37 / 0…0.45;
  inner face only on y = 0; blocks 0.35, core 0.34, coping overhang 0.02; ends flat with equal sections. MOD-08 bbox
  0…0.37² × 0.45, pivot inner corner; butt faces = MOD-07 end section (8 verts). MOD-09 1.0 × 1.0, top border at 0.38,
  ripple within ±0.005; water top 0.07 below the edge top. edge | edge at a node: gap 0.000 mm, 0 volume overlaps, 0
  same-facing coplanar faces. edge | corner | turned edge: gaps 0, outer coping lines continue (0.37), 0 overlaps, 0
  z-fight. Closed **2×2** (4 + 8 + 4) and **3×2** (6 + 10 + 4 = catalogue example) ponds: 16 / 20 pieces, 42 / 55 touching
  pairs, 0 volume overlaps, 0 same-facing coplanar faces (incl. coping tops); water covers the interior exactly (area
  4.000 / 6.000, all slabs inside); stone inner faces enclose the water on all four sides with gap 0, nothing inside the
  basin; neighbouring water slabs: 0 mismatched shared top vertices (no step). Test validated: an edge shifted by 0.3 →
  29 z-fight pairs, corner shifted 0.1 → 23, water shifted 0.5 → 17; transforms use exact quarter turns in double
  precision (mathutils float32 matrices gave fake 1e-8 overlaps in the first run).
- FBX re-import (pc.verify): each 2 nodes (empty + mesh), tris 76 / 56 / 36, dims 1.0 × 0.37 × 0.45 / 0.37 × 0.37 × 0.45 /
  1.0 × 1.0 × 0.04, texture found in each `.fbm`.
- Headless `build.py -- MOD-0x export` (PACK_ART = %TEMP%/assetnew_check/<ID>/headless_art, art/ not overwritten):
  geometry SHA1 == live — MOD-07 `e29cb1b160e418edfe10e956732f9b4d222ae0b5`, MOD-08
  `8c909343bc385249836b2035c7fc40066a7c138b`, MOD-09 `e32eec2933d041c5e8286e0fcc29331307a30827`. No
  `Tools/blender/__pycache__` left.
- Check renders (reference angle, preview, 128 px thumb, closed 3×2 pond, 2×2 pond from the outside corner) in
  `%TEMP%/assetnew_check/MOD-07|MOD-08|MOD-09/`.

## Rounds (live)
1. All three built; MOD-07 matched the reference at the first look (block layout, two-tone, coping, end face). SNAP run
   failed on float32 noise in the assembly transforms → exact quarter-turn transforms (check fix, not a model change).
2. MOD-09: the +5 mm ripple made the slab 0.045 tall (bbox above 0.38) → ripple only downwards, slab exactly 0.34…0.38;
   preview camera turned closer to the reference diagonal.
Rounds used: MOD-07 1, MOD-08 1, MOD-09 2 (of 5).

## Remaining differences vs the references
1. **MOD-08 (main note):** the reference front face shows 4 blocks (2 per course, dark wide + light narrow) and a plain
   right face; the model has one quoin stone per course wrapping both outer faces (top light, bottom dark). Reason: the
   catalogue budget 60 — the closed shell with the split inner faces, L underside and two mitred bevels costs 32 tris, so
   only 2 closed blocks (12 each) fit; the spec layout (blocks on both faces, 2 per course) needs ~100–125 tris. In a pond
   the quoins continue the MOD-07 courses and read as corner stones (see the assembly renders). If the owner wants the
   reference look, raise the MOD-08 budget to ~80 (one corner stone + one face block per course, pinwheel) — one
   constant per stone in `geo_corner`.
2. Stone greyer and the coping/light blocks paler and cooler than the beige references — palette effect (cells 11/12),
   as MOD-03 / WTR-03 / FLB-01; light blocks and coping share cell 11, so the top-right light block merges with the coping
   more than in the picture (the reference coping is pinker than its blocks). Two-tone split is kept visible.
3. MOD-07 reference end face shows the block courses running round the end; the spec wants flat sharp ends for butting,
   so the end shows the shell section with the 2 cm block edges set back 6 mm.
4. MOD-09 ripple facets are almost invisible at preview distance (±5 mm limit) — the reference is a flat slab too.
5. Unity import: the corner is built at Blender x ≥ 0, y ≥ 0 = Unity X ≤ 0, Z ≤ 0 under the series' X-flip assumption
   (same as MOD-06/STR-01, flagged in models_1.md) — verify once on the first import (Э8).

## Fix 1 — MOD-08 (2026-11-25, review models_2; `MOD-08.3d.md` "## Fix 1")
Budget raised 60 → **80** (CATALOG.md row already updated by the coordinator; `REG['MOD-08'].budget = 80`). Only
`geo_corner` blocks changed; shell, size, coping, bevels, snap faces, pivot, material and cells untouched. MOD-07 / MOD-09
outputs were not re-exported (MD5 of their FBX/.blend/previews unchanged); the "one quoin per course" text in the sections
above and remaining-difference 1 are superseded by this section.

- Per course 2 blocks in a pinwheel (`C_QUOIN = 0.21`, joints 12 mm): bottom course quoin x 0.006…0.35 × y 0.146…0.35
  (whole y face 0.344 + 0.204 of the x face) + face block on the x face y 0.006…0.134 (0.128) → joint on the x face; top
  course mirrored: quoin whole x face + 0.204 of the y face, face block 0.128 on the y face → joint on the y face. Faces
  0.35 (0.01 proud), backs 0.33 / inner sides inside the core, 6 mm short of the butt faces, courses 0…0.194 / 0.206…0.394.
- Tones as Fix 1: bottom quoin A-12 + face block A-11, top quoin A-11 + face block A-12.
- Tris **80 / 80**: Shell 32 + Blocks 48 (4 × 12). Size 0.37 × 0.37 × 0.45, pivot inner corner, min z 0.
- Checks (live = headless): non-manifold 0, loose 0, degenerate 0, gaps 0, coplanar pairs 0, non-planarity 0.
  **SNAP OK**: edge | corner | turned edge (gaps 0, outer lines continue, 0 overlaps / 0 z-fight), closed 2×2 and 3×2 ponds
  (0 volume overlaps, 0 same-facing coplanar faces, water cover exact, inner faces enclose with gap 0, no water step).
- FBX re-import: 2 nodes, 80 tris, dims 0.37 × 0.37 × 0.45, texture found in `.fbm`. Headless `-- MOD-08 export`
  SHA1 == live `acf146d73890e868da677e99fb02604e12074a68` (50 verts / 46 faces). New preview
  `FMS_Garden_MOD_08_Preview.png`; check renders (ref view, thumb, 3×2, 2×2 outside corner) in `%TEMP%/assetnew_check/MOD-08/`.
- Rounds: 1 (of 5). Read: both outer faces now show 2 blocks per course with staggered joints and alternating tones; in
  the assembled pond the corner continues the MOD-07 courses. Remaining: the reference's plain right face is not copied
  (spec + Fix 1 want blocks on both faces); palette greyer/cooler as the rest of the kit; the quoin's 0.204 short leg
  (0.21 incl. half joint) as asked by Fix 1.
