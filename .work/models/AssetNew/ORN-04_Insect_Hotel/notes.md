# ORN-04 Insect hotel `FMS_Garden_Insect_Hotel` — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- ORN-04 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in the collection `ORN-04_Insect_Hotel` (left in place). The
owner's file was not saved; the default Cube and the other collections were not touched; the selection (Cube, active Cube)
was restored after the live export.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Insect_Hotel.fbx` (+ `.fbm/FMS_Garden_AtlasA.png`) |
| Blend | `art/AssetNew/Blend/FMS_Garden_Insect_Hotel.blend` (collection only) |
| Preview | `art/AssetNew/Previews/FMS_Garden_ORN_04_Preview.png` (one) |
| Tris | **888 / 900**: Frame 28, Legs 48, Dividers 48, Roof 20, Ridge 12, Logs 264, Straw 180, Bricks 288 |
| Size (Blender X × Y × Z) | 0.600 × 0.377 × 0.880 m (frame 0.54 × 0.28 × 0.565 on 0.14 legs; roof 0.60 wide, ridge top 0.88) |
| Nodes | root empty `FMS_Garden_Insect_Hotel` + one mesh `FMS_Garden_Insect_Hotel_Body`, scale 1, rot 0 |
| Pivot | (0, 0, 0) = centre of the footprint on the ground; open front = Blender −Y (Unity +Z with −Z-forward export) |
| Material | `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only; MD5 `119daf05…` unchanged, palette 0 mismatches) |
| LOD | none (catalogue) |

Slots: frame, legs, dividers, ridge, log sides 1 (dark wood); roof top 0 (light wood), roof edges/underside 2; log ends
0 (holed) / 2 (plain); straw sides 4, straw tops 3; brick front 6, brick top/sides 14; holes 8.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0; internal gaps 0 for all 38 components (each log, stalk, brick separate) — every
  filling touches the cell floor/shelf and logs/bricks also the back board; mirror X 0.000000 for the symmetric structure.
- Coplanar overlapping face pairs 0 (all contacts embedded 1–5 mm or offset ≥ 1 mm: upright fronts 4 mm behind the shelf
  fronts, ridge 5 mm short of the roof ends, logs overlapping 1.5 mm, top log 1.7 mm into the lower ones).
- Ground contact: min z 0.0000, 16 verts at z = 0 (4 legs, X ±0.18…0.26, Y ±0.05…0.13).
- SNAP: no contract (free-standing ornament).
- FBX re-import: 2 nodes (empty + mesh), 888 tris, dims 0.6 / 0.377 / 0.88, texture found in `.fbm`.
- Headless `build.py -- ORN-04 export` geometry SHA1 == live SHA1 `4ac9ae4adfe167c6cb6c1b04d247336aae79682e`
  (520 verts / 655 faces).

## Measured from the reference (it wins over the catalogue, PIPE-04)
Front face of the frame = 680 px for 0.54 m (≈ 1260 px/m). Cells ≈ 0.145 wide × 0.15 high (≈ 1:1), shelves ≈ 0.026,
legs ≈ 0.11 tall × 0.07, frame boards ≈ 0.03, roof clearly steeper than 25°. Overall bbox h/w ≈ 1.39 (ours at a similar
angle ≈ 1.33 after round 2, measured by eye). The reference is a squat cabinet, about 0.85–0.9 m tall at a 0.6 m width, not 1.1 m.

## Deviations from `prompts/ORN-04.3d.md` (for the reviewer / spec owner)
1. **Height 0.88, not 1.10.** Width 0.60 kept (catalogue); height follows the reference proportions (cells ~1:1, short legs,
   frame ≈ as tall as wide). Legs 0.14 (spec 0.20, reference ≈ 0.11), cells 0.127 × 0.135.
2. **Board thickness 0.05 kept** (spec, never trimmed) although the reference frame boards are thinner (~0.03); cells are
   therefore 0.127 wide instead of the reference ≈ 0.145.
3. **Legs 0.08 square** (spec 0.10, reference ≈ 0.07), 1 cm inside the frame outline as in the reference.
4. **Dividers in slot 1** like the frame (reference: one uniform dark frame/grid), not slot 0 as in the spec table — light
   log ends, pale straw and red bricks read better on a dark grid. One-line change (`dividers()` slot) if slot 0 is wanted.
5. **Roof pitch 38°** (spec 25°; the reference roof is steep). Roof = one closed chevron shell (two boards, no seam), 0.60
   wide, overhang 0.03 front/back/sides; ridge board 0.59 × 0.05 × 0.03 (5 mm short of the roof ends: no coplanar end
   faces). No gable infill: the gable triangle is open and shows the dark roof underside, as the reference's side.
6. **Logs: 3 hexagonal logs per cell in a honeycomb (pointy-top, 0.062 across flats), 2 holed** instead of the reference's
   4 octagonal logs — budget. 4 octagonal logs with 2 holes cost 140 tris per cell (420 total) and do not fit 900 with
   the bricks' 6 holes; the spec allows trimming log/hole counts and specifies 6-sided logs.
7. **Straw: 5 stalks per cell** (0.021 × 0.030, tapered to 80 %, slight fan-out lean), the reference shows 7–8 thinner
   sticks — budget (12 tris per closed stalk). Width 0.021 < the 0.03 STYLE minimum, depth 0.03; they read at 128 px.
8. **Holes** are recessed 6-gon cones (6 tris, slot 8, 4.5–5 cm deep so they stay dark), not tubes with a bottom — budget.
9. **Colour**: straw slot 4 is paler than the reference's yellow; holes (slot 8) are a lighter grey than the reference's
   near-black holes; palette kept (atlas read only).

## Rounds (live, 3 of 5)
1. First build (flat-top hex logs, pitch 30°, legs 0.12): logs left 1/3 of each log cell empty, roof flatter and the whole
   hotel squatter than the reference (bbox h/w 1.25 vs 1.39).
2. Logs → pointy-top honeycomb (fills 0.122 of the 0.135 cell), pitch 38°, legs 0.14: h/w ≈ 1.33, 128 px thumbnail reads
   as an open rack with logs / straw / bricks (clearly not the closed Farm Yard birdhouse).
3. Hole cones deepened (0.02 → 0.045/0.05) so they read darker; back/side check render: closed back, open gable triangle.

Remaining (nitpicks): straw count and tone, hex vs octagon logs, thicker frame boards than the picture, lighter holes.

## For the next builders
- Cheap recessed hole: 6-gon loop in the face (`pack_shapes.fill` with the hole loop) + a 6-tri cone to one apex
  (`hole_cone()` in build.py), +20 tris per hole incl. the face fill; keep it ≥ 4 cm deep so it renders dark.
- Frame with an open front recess as one closed shell (`frame()`): 28 tris instead of 4 boards + back panel.
