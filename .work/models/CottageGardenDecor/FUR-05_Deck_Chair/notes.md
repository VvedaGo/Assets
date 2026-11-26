# FUR-05 Folding deck chair `FMS_Garden_Deck_Chair` (+ `_Blue`) — builder notes (Э7, batch 4, 2026-11-26)

Source of truth: `build.py` (`-- FUR-05 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in the collection `FUR-05_Deck_Chair` and its
child `FUR-05_Deck_Chair_Blue` (left in place). The owner's file was not saved (is_dirty False after every call); the
Cube, the other collections (incl. `FUR-04_Bistro_Chair`) and the selection (Cube, active Cube) were unchanged after
every call. Check renders in a temporary scene (`TMP_FUR05_*`, removed after each render), files in
`%TEMP%/assetnew_check/FUR-05/`. Shared atlases read only: A MD5 `119daf05…` and F MD5 `ae0f0dba…` unchanged; palette
checked by pixel read (0 mismatches).

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Deck_Chair.fbx` (+ `.fbm`), `FMS_Garden_Deck_Chair_Blue.fbx` (+ `.fbm`) — root empty + `<asset>_Body` each |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Deck_Chair.blend` (collection-only library with both collections; written by the headless export) |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_FUR_05_Preview.png` (one, series 3/4 from the front-right, base red) |
| Tris / budget | **384 / 400** each (base and `_Blue`) — FrontLegs 24, BackRails 24, RearLegs 24, Armrests 24, FootBar 12, TopBar 20, FrontBar 20, Cloth 236 |
| LOD | none (catalogue) |
| Size X × Y × Z (Blender) | 0.680 × 1.059 × 0.903 (Unity X × Z × Y); catalogue 0.6 × 1.0 × 0.9 |
| `_Blue` | identical vertices; stripe slot 5 → 15 (cells used: base 0/1/3/5, `_Blue` 0/1/3/15) |

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint bounding box on the ground; FBX Y up, −Z forward baked, scale 1. One static
  mesh per asset, pivot at the root. Blender X = right, −Y = front (Unity +Z: feet / seat toward the viewer), Z = up.
  X-symmetric (mirror 0.000000).

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 for every component; mirror X 0.000000; coplanar overlapping
  faces 0 (both assets).
- Ground: min z 0.0000; exactly 16 vertices on z = 0 = the flat-cut bottoms of the 2 front legs and 2 rear legs.
- Functional: cloth touches (sinks 2 mm into) the top bar and the front bar; cloth clear of rails, legs, armrests and
  foot bar (X-disjoint: cloth ±0.235, rail inner faces ±0.255); span bend at the bars below the facet angle (top 4.7°,
  front 14.0°: the cloth never cuts a bar); cloth lowest point 0.317 (seat sag), front bar top 0.39.
- SNAP: no contract (free-standing furniture).
- FBX re-import (both): 2 nodes (root + Body), 384 tris, dims 0.68 / 1.059 / 0.903, min z 0, texture found in the `.fbm`.
- Headless `build.py -- FUR-05 export` geometry SHA1 == live SHA1 `8aa354c897c398315653e88747d1c67d7ed316e8`
  (both meshes, positions + UV cells).

## Build (Blender coordinates; d = depth from the front-leg foot axis toward the back)
- Front legs 0.055 (X) × 0.06 at X ±0.28, foot d 0 → top (0.06, 0.56), slight backward lean, bottom cut flat on z = 0.
- Long back rails 0.05 × 0.06 at X ±0.28 from inside the front leg (d 0.012, z 0.10) to the top (d 0.97, z 0.88),
  perpendicular end; recline ~39° from the horizontal.
- Rear legs (A-frame) 0.05 × 0.06 at X ±0.31, from the foot (d 0.92, z 0) to inside the armrest back (d 0.57, z 0.53);
  they cross the back rails inside the armrest (2 cm halving overlap).
- Armrests 0.09 wide × 0.05 thick, X 0.2475–0.3375, d −0.005 → 0.63, top 0.58 at the front → 0.55 at the back; they
  cover the front leg, the rail and the rear leg tops.
- Foot bar 0.05 square, slot 1 dark wood, between the rear legs at z 0.10.
- Top bar: round, 6 sides, Ø0.05, X ±0.30, on the upper face of the rails 0.11 below their tips (sunk 5 mm).
- Front (seat) bar: 6 sides, 0.06 across, centre z 0.36, in front of the front legs (sunk 5 mm), ends 3.25 cm past the
  legs (X ±0.34).
- Cloth: closed shell 0.025 thick, 0.47 wide, 5 lengthwise stripes red 5 / cream 3 / red / cream / red (0.094 each),
  red edges and end caps; wraps 120° over the top bar and 180° over the front bar (top and front face of the bar
  covered — the front band of the reference); hanging span = gravity parabola, lowest centre line z 0.33 at d 0.22
  (just behind the front bar), 4 straight segments; each bar is turned so its flat next to the span is parallel to the
  span tangent (cloth lies on the flats). 9 segments along the length in total.

## Reference camera (measured)
Least-squares fit of 11 reference points (feet, armrest ends, rail tips, front bar ends) for lenses 70–400 mm: every
solution gives a front-right view, yaw ~34°, leg spacing ~0.51–0.56 m, rear feet ~0.93 behind the front feet, rail
tips ~0.95–1.0 back, armrest ~0.55–0.58 dipping ~3–5 cm to the back, front bar ~0.35. Check renders: yaw 34°,
elevation 28°, 150 mm (`VIEW_REF`, `REF_LENS`); at yaw 18–24° the right A-frame disappears, so the yaw is right and the
reference chair is genuinely wider than the catalogue.

## Deviations from `prompts/FUR-05.3d.md` / the catalogue (for the reviewer)
1. **Frame layout follows the reference, not the spec table**: long back rails run from the top down to the front legs
   near the ground, and a separate rear leg (A-frame) runs from the armrest back to the ground; the spec had rails
   standing on their own feet at Z −0.10 and no rear legs. The dark foot bar joins the rear legs (spec: rail feet).
2. **Round top bar** (6-sided Ø0.05) instead of the spec's square bar — reference (task envelope: follow the reference).
3. **No middle cross bar** (spec Z −0.28, Y 0.55): not visible in the reference; it would sit inside the cloth sag.
4. **Front (seat) bar at z 0.36 (top 0.39), not 0.45**, and armrest top 0.58→0.55 instead of 0.55→0.62 (rising): measured
   in the reference (front bar ≈ 0.6 of the armrest height; armrest level or dipping slightly to the back). The spec
   does not name 0.45 as a functional seat height; the sitting surface (cloth low point) is 0.317. If 0.45 is meant as
   a functional seat height, raise `FB_Z` / `SEAT_LOW` (one constant each).
5. **Size 0.68 × 1.06 × 0.90** vs catalogue 0.6 × 1.0 × 0.9: width +13 % from the reference fit (legs at ±0.28, cloth
   0.47); depth +6 % from the reference (rear feet 0.92 back, rails reclined to d 0.97). Height = catalogue.
6. **Cloth 0.47 wide, stripes 0.094** (spec 0.50 / 0.10): the cloth stays inside the rails (no intersections); sag modelled
   as a hanging (gravity) curve with the low point near the front bar, not a symmetric 0.06 sag — the reference seat
   flattens just behind the front bar. Hem = the 180° wrap band over the front bar.
7. **Front bar 6-sided** (reference end looks octagonal): 6 sides give a 180° wrap in 3 segments and keep the model
   under 400 tris; reads as the same chamfered bar.
8. **Frame 0.05–0.055 × 0.06**: the spec's "thin frame" exception for this small folding chair, at the 0.05 minimum;
   armrests wider (0.09) as in the reference.

## Rounds (5 live of 5)
1. First build: clean checks, 392 tris. Worst: rail tips did not protrude above the cloth, rear feet too close to the
   front, cloth covering the top bar ends.
2. Rails reclined further (top d 0.97), rear feet back to 0.92, armrest slightly lower and dipping to the back, top bar
   0.11 below the rail tips; reference camera fitted numerically and tested (yaw 18/24/34°). Worst: frame narrower than
   the reference; seat sag symmetric (reference seat flattens near the front).
3. Width ±0.28 (cloth 0.47); gravity parabola span with bars turned to the span tangent. Worst: cloth stopped short of
   the front face of the front bar; rail foot poked 1.8 mm through the front-leg face (seam line).
4. Front bar 6-sided with a 180° wrap (front band), rail foot moved back 12 mm. Worst: trough just behind the front bar
   too deep; the rail stuck out of the armrest's inner side (notch).
5. Seat low 0.33; armrest 0.2475–0.3375 covers rail + rear leg (rear legs at ±0.31). Only palette and nitpicks left;
   128 px thumbnail reads as a striped deck chair. Exported.

Remaining differences (nitpicks): red renders brighter/more saturated and cream whiter than the reference, wood a little
paler (fixed palette, series lighting); top bar ends show less than in the reference (they sit on the rails); rail tips
are plain perpendicular cuts (reference has a small chamfer); the seat surface has a mild fold where the span meets
the front-bar wrap; `_Blue` is not in the preview (check render `%TEMP%/assetnew_check/FUR-05/FUR-05_blue_live.png`).
