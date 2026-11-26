# WTR-03 Birdbath `FMS_Garden_Birdbath` — builder notes (Э7, pilot 1/3, 2026-11-25)

Source of truth: `build.py` (`-- WTR-03 build|export`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback mode;
execute_blender_code and look both worked). Live work only in collection `WTR-03_Birdbath`; the owner's file was not saved.

## Result

| | |
|---|---|
| Size | X 0.599 × Z(depth) 0.599 × Y(height) 0.700 m (Blender X×Y×Z) |
| Tris | 336 / 350 — Plinth 48, Foot 20, Knob 60, Stem 20, Collar 82 (trumpet 40 + band 20 + ledge 22), Bowl 96, Water 10 |
| Pivot | centre of the plinth base on the ground (0,0,0); root empty `FMS_Garden_Birdbath` + one mesh `FMS_Garden_Birdbath_Body`, scale 1, rot 0 |
| Material | one, `M_Garden_Build` (atlas A, `FMS_Garden_AtlasA.png`), slots 11 limestone / 12 stone / 15 water |
| Checks | non-manifold 0, loose 0, degenerate 0, mirror X 0, gaps 0 (single closed shell), coplanar overlaps 0, min z 0.0000 (plinth on ground) |
| FBX verify | 2 nodes (empty + mesh), 336 tris, dims 0.599/0.599/0.70, texture found in `.fbm` |
| Headless | `build.py -- WTR-03 export` geometry SHA1 == live model SHA1 (`813afcaf…`, 170 verts / 188 faces) |

## Measured from the reference (it wins over the catalogue, PIPE-04)

The reference is a front view, ~22° above, practically orthographic (rim and plinth ellipses give the same angle).
Scale: bowl across flats 0.60 m = 762 px. Heights from centre-column colour edges + side silhouette, checked by an
orthographic render at the same angle (bbox h/w: ref 1.365, model 1.370; row widths within 1–4 % of the bowl width).

| Ring | z, m | R (vertex), m | sides |
|---|---|---|---|
| plinth wall | 0 – 0.070 | 0.1665 | 10 |
| plinth top (slight slope = chamfered top) | 0.070 → 0.078 | 0.1665 → 0.115 | 10 |
| foot cone | 0.078 → 0.179 | 0.115 → 0.068 | 10 |
| knob chamfer / band / chamfer | 0.179 → 0.205 → 0.242 → 0.257 | 0.068 → 0.0866 → 0.0866 → 0.064 | 10 |
| stem (tapers up) | 0.257 → 0.433 | 0.064 → 0.0515 | 10 |
| trumpet (2 bands, concave) | 0.433 → 0.478 → 0.509 | 0.0515 → 0.070 → 0.105 | 10 |
| collar band | 0.509 → 0.548 | 0.105 → 0.109 | 10 |
| ledge under the bowl (flat, faces down) | 0.548 | 0.109 (10) → 0.138 (12) | 10/12 |
| bowl underside | 0.548 → 0.657 | 0.138 → 0.310 | 12 |
| rim wall / rim top | 0.657 → 0.700 | 0.310 (0.599 across flats) → 0.2588 | 12 |
| inner wall → water disc | 0.700 → 0.676 | 0.2588 → 0.2535 | 12 |

## Deviations from `prompts/WTR-03.3d.md` (for the reviewer / spec owner)

1. **Height 0.70, not 0.85.** At the 0.60 footprint the reference is 0.70 m tall (h/w 1.365). The footprint limit was kept
   and the height follows the reference.
2. **Bowl, rim and water are 12-sided, the pedestal 10-sided.** The rim vertices in the reference sit at x = ±0.966/±0.707/±0.259 R
   (12-gon, flat faces to front and sides; matched within 3 px), and the water outline is a 12-gon too. The plinth, knob and stem
   facet widths match a 10-gon (vertex on +X). The two are joined by a flat 10→12 ledge under the bowl that shares both rings.
3. **Stem is Ø0.10–0.13 (spec: waist ≥ Ø0.16).** The reference stem is 0.17–0.21 of the bowl width. Kept as in the reference; it
   still reads in the 128 px thumbnail. If the owner wants it chunkier, scale the Stem/Trumpet radii ×1.25 (no budget cost).
4. **Plinth Ø0.33 (spec 0.40)**, from the reference (plinth/bowl = 0.555). Top is one gently sloped band, not a separate
   0.015 chamfer band (the reference top edge is crisp, and that saves 20 tris for the 12-gon bowl).
5. **Bottom face kept** (spec: "no bottom face") so that the mesh is a closed manifold (non-manifold 0 is an acceptance criterion).
6. **Water** is the top cap of the inner wall (0.024 m below the rim, R 0.2535), with no hidden inner wall below it, so it
   cannot overlap or z-fight anything.
7. **Colour**: the reference renders the stone warmer/beiger than palette slot 11 `#C9C3B6`. The palette from STYLE.md was kept (atlas A).
   Plinth vs limestone contrast is lower than in the reference for the same reason. Owner to judge the stone tone in the pilot review
   (STYLE.md asked to compare `#A7A39A` against Nature rocks; no Nature preview is available in this branch).

## Rounds (live, 5 of 5)

1. First build (all 10-gon, catalogue-like stem): with the 70 mm check camera the comparison was distorted. The reference is near-
   orthographic, so check renders were switched to an orthographic camera at 22°. Ortho: height matches (0.70). Worst: rim/water polygon
   reads differently, bowl side silhouette too short.
2. Bowl → 12-gon, re-measured all rings. Silhouette within ~1–2 % except the bowl underside (reference fuller near the bottom).
3. Bowl bottom ring wider (overhang over the collar). Worst left: the collar band does not read as a separate ring.
4. Trumpet top flattened so it creases against the vertical collar band; overhang 2.9 cm. The 128 px thumbnail reads well.
5. Preview light: sun angle 28° (softer shadow) + ambient 0.65. The bowl's hard cast shadow had hidden the collar band.
   Geometry unchanged.

Remaining (nitpicks): bowl underside ~1–2 cm slimmer at mid-height than the reference (no tris left for a convex mid ring);
collar band contrast lower than in the reference; stone tone (palette).

## Atlas A — `art/AssetNew/Textures/FMS_Garden_AtlasA.png` (shared by all atlas-A models)

256 px, 4×4 cells of 64 px, one colour per cell; slot = row * 4 + col, row 0 at the top of the PNG; UVs at cell centres
(`pack_common.cell_uv`). Written by `pack_common.atlas_image` from `PAL_A` in build.py (= STYLE.md table, verified by pixel read).

| row \ col | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | 0 wood light `#B5835A` | 1 wood dark `#7A5233` | 2 wood mid `#9C6B44` | 3 cream `#F2E6C9` |
| 1 | 4 cream dark `#DCC9A0` | 5 red `#C8473B` | 6 red dark `#A8372E` | 7 metal `#8E959B` |
| 2 | 8 metal dark `#6E757B` | 9 metal light `#A9AFB4` | 10 white paint `#EEEDE7` | 11 limestone `#C9C3B6` |
| 3 | 12 stone `#A7A39A` | 13 wrought iron `#3A3A3F` | 14 tile/brick `#9C3F33` | 15 water `#4A78A8` |

Material `M_Garden_Build`: Principled, image Closest, Metallic 0, Roughness 0.85 (Smoothness ≈ 0.15), Specular IOR level 0.25.

## For the next builders (PLT-01 is atlas F, STR-06 is atlas A)

- Atlas A: reuse `FMS_Garden_AtlasA.png` + `M_Garden_Build` exactly. Copy `PAL_A`, `ATLAS_TEX`, `ATLAS_MAT` and the roughness line from
  build.py. Do not write a second atlas-A PNG. Atlas F needs its own file (e.g. `FMS_Garden_AtlasF.png`, `M_Garden_Flora`).
- Live Blender: the owner's scene has a 2 m default Cube at the origin that hides any model in `look` (viewport/rendered).
  Do not touch it. Render through a temporary scene instead (`render()` in build.py links only your collection, then removes
  its own scene/world/lights/camera) and view the PNG with `look image=<path>`.
- Helpers in build.py worth copying: `rings()` + `bands()` (lofts with shared rings, so there are no gaps and no coplanar seams),
  mixed segment counts joined with `pack_shapes.fill` (annulus between two rings), `render()` (temporary scene, ortho for
  reference matching or 70 mm for the preview, auto-fit), `geom_dump()` (SHA1 of world-space verts + face UV cells, used to prove
  headless == live), live exec form with `LIVE_ARGS` (only clears its own collection; headless also drops the factory objects).
- `sys.dont_write_bytecode = True` before importing pack_common, otherwise `Tools/blender/__pycache__` appears in git status.
- Reference matching: measure first whether the reference is perspective or orthographic (compare the rim and base ellipse
  angles); compare row widths normalised by bbox width; count facets from vertex x positions (n-gon cos table).
