# WTR-02 Wall fountain stele `FMS_Garden_Fountain_Wall` — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- WTR-02 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in collection `WTR-02_Fountain_Wall` (left in place).
Renders in temporary scenes (removed afterwards). The owner's file was not saved (unsaved, path empty); the default Cube
and the other collections were not touched; selection (Cube, active Cube) checked before/after the live export: unchanged.

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Fountain_Wall.fbx` (+ `.fbm` with the atlas copy) |
| Blend / preview | `art/CottageGardenDecor/Blend/FMS_Garden_Fountain_Wall.blend` (collection only); ONE preview `art/CottageGardenDecor/Previews/FMS_Garden_WTR_02_Preview.png` |
| Tris | **428 / 900** — Slab 22, Cap 22, Basin 150 (plinth, drum, coping, bottom, back), InnerWall 18, Water 8, Medallion 68, Collar 44, Pipe 60, Stream 36 |
| Size (Blender X×Y×Z) | 0.900 × 0.590 × 1.300 m (x ±0.45, y −0.59…0, z 0…1.30); catalogue 0.9 × 0.6 × 1.3 |
| Nodes | root empty `FMS_Garden_Fountain_Wall` + one mesh `_Body`, rot 0, scale 1 |
| Material | `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only: loaded, never saved; MD5 `119daf05…` unchanged; palette pixel check 0 mismatches). Cells: 11 limestone, 12 stone (plinth, inner wall, medallion), 7 metal (pipe, collar), 8 metal dark (bore), 15 water, 9 metal light (one stream side row). Flat shading (0 smooth faces) |
| LOD | none (catalogue) |

## Pivot and axes
- Root (0, 0, 0) = centre of the BACK face of the stele on the ground. Everything at y ≤ 0 (max y 0.000000): the back is
  one flat polygon (slab + cap outline, 7 tris after triangulation, normal +Y) in the plane y = 0; the cap is flush at the
  back (overhang 0.05 to the sides and the front only). Static, no moving parts.
- Blender −Y = front (Unity +Z, the basin side), Z = up (Unity Y). FBX Y up, −Z forward baked (pc.export). X-symmetric.

## Construction
- Stele + cap = one closed solid (no seam between slab and cap, so the back is truly one plane): slab 0.70 × 0.15,
  front vertical edges chamfered 0.02; gabled top (ridge front-to-back, gable facing the front as in the reference),
  slope 0.30 (16.7°); cap 0.80 × 0.20, 0.085 thick (vertical), underside apex 1.215, underside 1.11 at the slab sides and 1.095 at x ±0.40, ridge 1.30.
- Basin: half of a 16-gon (flat face to the front, half facets at both ends = 7 full + 2 half facets, as the reference),
  back plane at y −0.14 (1 cm inside the slab, so no coplanar contact with the slab front). Rings (vertex R, z): plinth
  0.456 z 0–0.05 (slot 12, 1.2 cm proud) + chamfer, drum 0.444 to 0.37, flat ledge, coping 0.459 z 0.37–0.425,
  top chamfer to 0.444 at 0.44, coping top to 0.374, inner wall (slot 12) down to the water line R 0.364 at z 0.37
  (7 cm under the coping top). Water = flat half-disc on that ring (8 tris), no hidden faces under it.
- Medallion: 12-gon Ø0.28 (flat top), 0.03 proud + 8 mm front chamfer, centre z 1.00, slot 12.
- Spout: 8-gon pipe (flat bottom) Ø≈0.09, 0.15 from the slab front, centre z 0.78, hollow tip (lip + 3.5 cm bore in
  slot 8); collar 8-gon Ø≈0.14 × 0.024 with front chamfer. Collar and pipe sunk into the slab / collar.
- Stream: ribbon 0.05 × 0.02, starts on the bore floor (4 mm sunk), over the lip, out 0.03, straight down 1.5 cm into the
  water. Front and back faces slot 15, the +X side slot 9 (as the WTR-01 streams). Contacts: pipe OK, water OK, basin
  walls clear.

## Checks (live = headless)
- Part checks: non-manifold 0, loose 0, degenerate 0, mirror X 0.000000, internal gaps 0 (every component touches another).
- Final triangulated mesh: non-manifold 0, loose 0, degenerate 0 (min corner angle 4.0°), smooth 0, mirror X 0.000000.
- Coplanar overlapping face pairs 0.
- Ground contact: min z 0.0000 (slab bottom and basin plinth on z = 0). Note: the basin bottom and the slab bottom overlap
  in a 1 cm strip (y −0.15…−0.14) on the ground plane, both facing down (hidden on the ground, same as MOD-03's ground faces).
- SNAP OK (CATALOG «Модули и стыковка»: back face 0.22 from the MOD-03 wall axis): MOD-03 FBX imported read-only, axis put
  at y = +0.22 → coping front face y 0.0000, wall face under the coping y 0.0200; fountain back y 0.0000, 0 fountain
  vertices inside the wall. Back-to-back contact with the coping band z 0.54–0.60 over x ±0.35 (both faces hidden).
  Stele 1.30 rises above the wall (0.60); basin wings (x ±0.35…0.45) sit in front of the wall, nothing reaches behind.
- FBX re-import: 2 nodes (empty + mesh), 428 tris, dims 0.9 / 0.59 / 1.3, min z 0, texture found in `.fbm`.
- Headless `build.py -- WTR-02 export` (PACK_ART = %TEMP%/assetnew_check/WTR-02/headless_art, art/ not overwritten):
  geometry SHA1 == live `fcc7d0575057552737c0cf68137ed88a9e5215dc` (226 verts / 266 faces). No `Tools/blender/__pycache__`.
- Check renders (reference angle, 3/4, 128 px thumb, back view, sheets) in `%TEMP%/assetnew_check/WTR-02/`.

## Measured from the reference (AI image, not a calibrated camera; ratios only)
- Verticals are parallel (zero-pitch perspective). Medallion Ø0.28 = 192 px gives ≈ 690 px/m on the stele front.
- Basin coping top ≈ 0.40–0.47 above the ground (spec 0.55): the reference basin is clearly lower, the spout and the
  medallion higher (spout ≈ 0.77–0.78, medallion centre ≈ 1.0; spec 0.74 / 0.88). Water ≈ 0.07 under the coping
  (spec 0.09). Water/coping width ≈ 0.79 (spec 0.67). Drum facets: 7 full + 2 half per 180° (16-gon; spec 12 per 180°).
- Gable: the slab top and the cap are gabled with the ridge running front-to-back (spec: low gable 0.04, ridge along X).
  Rise ≈ 0.10–0.12 over the half width.

## Deviations from `prompts/WTR-02.3d.md` (reference wins, PIPE-04; no functional size involved)
1. Gabled stele top + gabled cap with the ridge front-to-back, slope 16.7° (spec: low 0.04 gable, ridge along X) — as the reference.
2. Basin lower: coping top 0.44, water 0.37 (spec 0.55 / 0.46); drum 16-gon half (spec 12 segments per 180°); coping ring
   narrower (water R 0.364 vs coping 0.459). Width kept at the catalogue 0.90, depth 0.59.
3. Spout centre 0.78, medallion centre 1.00 (spec 0.74 / 0.88); pipe 0.15 long, Ø≈0.09 (spec 0.12, Ø0.08), hollow tip
   added (bore in slot 8) as in the reference; collar Ø≈0.14 × 0.024 (spec 0.12 × 0.02).
4. Cap 0.085 thick (spec 0.12 incl. gable), overhang 0.05 sides/front as specified, none at the back.
5. Stream: 4 segments (spec 3); slot 9 on the +X side, not on the front (series rule from WTR-01; the reference shows
   the wide front face light grey, which read as a metal bar in the first check render).
6. Plinth 1.2 cm proud of the drum (spec: plinth band in slot 12, no step given); the reference shows no plinth — kept
   for the two-tone split (review lesson).

## Rounds (live, 3 of 5)
1. First build = headless. Check camera too low; stream front face slot 9 read as a grey bar and bent out like a hook.
2. Camera raised to ~32°, stream front blue / +X side slot 9, straighter fall. Worst left: basin narrower than the
   reference, spout short/thin, gable flatter and cap thinner than the reference.
3. Basin to the catalogue width 0.90 (coping R 0.459), pipe 0.15 / Ø0.09, collar Ø0.14, gable slope 0.30, cap 0.085.
   128 px thumbnail reads: stele with medallion, spout, blue stream, half basin. Only nitpicks left → export.

## Remaining differences vs the reference (nitpicks)
- Stone greyer and the limestone cooler/lighter than the beige reference (palette, accepted series-wide); medallion
  (slot 12) contrast lower than in the reference.
- The reference shows a wide light strip on the left front edge of the slab (bigger bevel); here the spec chamfer 0.02.
- Stream bends out slightly at the lip; the reference drops almost straight from the lower lip.
- Reference stele may be a little deeper (≈0.2); kept 0.15 (spec), back plane unaffected.
