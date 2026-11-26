# WTR-01 Tiered fountain `FMS_Garden_Fountain_Tiered` — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- WTR-01 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in the collection `WTR-01_Fountain_Tiered` (left in
place). Renders in a temporary scene (removed afterwards). The owner's file was not saved (unsaved, not dirty); the default
Cube and the other collections were not touched; selection (Cube, active Cube) checked before/after the live export: unchanged.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Fountain_Tiered.fbx` (+ `.fbm/FMS_Garden_AtlasA.png`), LOD0 + `_Low1` children |
| Blend | `art/AssetNew/Blend/FMS_Garden_Fountain_Tiered.blend` (collection `FMS_Garden_Fountain_Tiered`, headless export) |
| Preview | `art/AssetNew/Previews/FMS_Garden_WTR_01_Preview.png` (one) |
| Tris LOD0 | **1258 / 2800** — Basin 124 · Lower 360 (pedestal 172 + bowl 188) · Upper 454 (neck 156 + bowl 188 + finial 110) · Streams 320 (8 objects × 40: upper ribbon 20 + lower ribbon 20) |
| Tris LOD1 | **788** (`make_lod1.py`): Basin 62, Lower 180, Upper 226, Streams 8 × 40 (kept: ≤ 60 tris per object, so the ribbons are untouched) |
| Size | X 2.400 × Y 2.400 × Z 2.420 m (Blender) |
| Hierarchy / pivot | root empty `FMS_Garden_Fountain_Tiered` at (0,0,0) = centre of the basin on the ground; 11 meshes `_Basin _Lower _Upper _Stream1.._Stream8` (+ 11 `_Low1`), all direct children, pivot (0,0,0), rot 0, scale 1. Static |
| Material | one, `M_Garden_Build` + shared `FMS_Garden_AtlasA.png` (read only: loaded, never saved; MD5 `119daf05…` before = after; palette pixel check 0 mismatches). Cells: A-11 limestone, A-12 stone (basin inner wall, foot block, bowl inner walls, finial tier bands), A-15 water, A-9 light row on the ribbons |

## Checks (live = headless)
- Per part: non-manifold 0, loose 0, degenerate 0; mirror X 0.000000 (whole model); smooth faces 0.
- Coplanar overlapping face pairs 0 per part and 0 with all parts merged.
- Contacts: Basin ↔ Lower, Lower ↔ Upper interpenetrate (each tier starts 4 cm under the water of the tier below and ends
  inside the bowl above: no floating, no coplanar seams). Every ribbon: rim contact OK (5 mm sunk into the rim top) and
  water contact OK (ends 15 mm under the water disc, inside the disc: upper r 0.43–0.47 < 0.59, lower r 0.75–0.78 < 0.96).
  `comp_checks` prints a "gap" between the two ribbons of one Stream object — by design (they are 0.11–0.12 apart,
  each is checked against its own rim/water above).
- Ground: min z 0.0000 (basin bottom on z 0).
- SNAP: no contract for WTR-01 in CATALOG «Модули и стыковка» → n/a.
- FBX re-import (after LOD1): 23 nodes (root + 11 + 11 `_Low1`), 1258 + 788 tris, dims 2.4 / 2.4 / 2.42, texture found in `.fbm`.
- Headless `build.py -- WTR-01 export` geometry SHA1 == live SHA1 `5ae3078ea4b5a9be83de381a0edb8c4af4918dea` (673 verts / 690 faces).
  The headless export is the one in `art/` (its `.blend` collection is named by the asset, which `make_lod1.py` needs).
  No `Tools/blender/__pycache__` left.

## Measured from the reference (it wins over the catalogue, PIPE-04)
Reference: front view ~24° above, close to orthographic (basin wall at the front vertex 125 px vs side vertex 122 px).
Scale: basin 2.4 m = 966 px → 402 px/m; elevation from the basin front-bottom vertex (+197 px vs the side vertices).
Ortho check render with the same scale and bottom line: bbox 144..1109 × 74..1159 vs reference 140..1106 × 73..1160.

| Element | Built (z m, apothem m) | Spec |
|---|---|---|
| Basin | 16 sides, vertex to the front (as reference), Ø2.4, top 0.34, wall/top ring 0.22, water 0.21 | 12 sides, top 0.50 (wall 0.45 + coping) |
| Lower pedestal | 8 sides, flat front: block a 0.265 to 0.31, flare → waist 0.165, knob band a 0.20 (0.50–0.555), neck 0.15→0.14 to 0.80, collar 0.21 | baluster 12 sides, Ø0.55/0.30/0.50 |
| Lower bowl | 16 sides, flat front; underside 0.87→1.255, rim band to 1.37, outer a 0.735 (Ø1.47), rim top 0.145, water 1.33 | Ø1.3, rim 0.97 |
| Upper neck | 8 sides: foot a 0.165→0.11, knob a 0.135 (1.47–1.50), neck a 0.093 (1.53–1.68), flare 0.145 | Ø0.28/0.20/0.34 |
| Upper bowl | 16 sides; underside 1.72→1.965, rim to 2.03, outer a 0.42 (Ø0.84), rim top 0.08, water 2.01 | Ø0.7, rim 1.42 |
| Finial | 8 sides, rises straight out of the upper water (no visible stem, as reference): inverted cone a 0.075→0.175 (2.14), shoulder, band a 0.125 (2.18–2.25), slope, band a 0.07 (2.29–2.34), tip 2.42 | stem Ø0.12 + cone to 1.90 |
| Streams | 8 per bowl at 22.5° + 45k (both bowls, as reference: front pair ±22.5° from the front), 0.07 × 0.035, hook over the rim (5 mm sunk, starts 1 cm over the water), mitred bend, straight drop | 0.05 × 0.02, lower set offset 22.5° |

## Deviations from `prompts/WTR-01.3d.md` (for the reviewer / spec owner)
1. **Height 2.42, not 1.9.** At the 2.4 m footprint the reference is 2.42 m tall (checked by an orthographic render at the
   reference scale: top and bottom lines within 1 px). Footprint kept; heights follow the reference (as WTR-03).
2. **Basin 16 sides** (reference facets match a 16-gon with a vertex to the front: x = 0.41/0.73/0.945 of R); **bowls 16
   sides with a flat face to the front** so all 8 ribbons sit on face centres; **pedestals and finial 8 sides** (reference).
   All rings are symmetric to the YZ plane; the basin has a vertex on +X, bowls/pedestals a flat face on +X (spec said
   "first vertex on +X" for all rings; the reference shows flat fronts on bowls and pedestals).
3. **Basin lower (0.34) with no separate coping lip and no chamfer**: the reference shows one flat top ring on a plain
   wall; a 0.015 chamfer would read as a line the reference does not have. Water 0.13 below the top (reference shows a
   clearly visible inner wall at the back), spec said 0.10.
4. **Bowls larger** than the spec (Ø1.47 / Ø0.84 vs 1.3 / 0.7), measured on the reference.
5. **Upper neck Ø0.186 across flats / 0.20 across corners**: the reference neck is ≈ Ø0.15; kept at the spec minimum
   ("no pedestal thinner than Ø0.2", across corners).
6. **Finial without a stem**: the reference bulb rises straight out of the upper water; it is sunk 5 cm into the bowl.
7. **Ribbons 0.07 × 0.035, hooked over the rim**, both sets at the same azimuths (reference), not "starting outside the rim"
   and not offset 22.5° (spec). Top face of the hook and one side face in A-9 (light), the rest A-15 water.
8. **No basin floor face**: the water discs are the top caps of closed shells (as WTR-03), nothing under them is visible.
9. **LOD1 788 = 63 %**, not 50 %: the 8 stream objects (40 tris each) are kept intact by `make_lod1.py` (≤ 60 tris), which
   is what the spec asks for ("LOD1 keeps the ribbons"). The decimated basin in LOD1 is irregular in its lower ring
   (visible only up close; three discs and the ribbons keep the silhouette).
10. Stone colour: as WTR-03/MOD-03, slots 11/12 render greyer/whiter than the beige reference — palette, not retinted.

## Rounds (live, 3 of 5)
1. First build from the measurements: height/width matched the reference (ortho render, bbox within 4 px). Worst: upper
   bowl too small (Ø0.72 vs 0.84), upper water too small/rim too wide, ribbons read as blue spokes over the rims.
2. Upper bowl Ø0.84, rim 0.08; lower bowl Ø1.47; basin water lower (0.21) and top ring 0.22; lower pedestal knob/block
   re-proportioned; upper neck foot as a trapezoid, neck at the spec minimum. Worst left: ribbon hooks blue and long.
3. Ribbon hook: top face A-9 (light, as the reference), start 1 cm (was 2 cm) over the water. 128 px thumbnail reads as a
   tiered fountain (three blue discs, white stone, ribbons).
   A perspective camera fit (headless, 7–10 m) was tried and rejected: it matched the reference worse than the orthographic one.

Remaining (nitpicks): reference stone warmer/beiger (palette); reference upper neck slimmer (spec minimum kept); reference
upper-bowl ellipse slightly flatter than the ortho model (AI picture inconsistency, ~2–3 cm in the rim height); reference
ribbons look slightly lighter overall.
