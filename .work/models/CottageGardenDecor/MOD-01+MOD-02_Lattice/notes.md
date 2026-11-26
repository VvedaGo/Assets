# MOD-01 Lattice panel `FMS_Garden_Lattice_Panel` + MOD-02 Lattice post `FMS_Garden_Lattice_Post` — builder notes (Э7, series batch 1, 2026-11-25)

Source of truth: `build.py` (one registry script, `-- MOD-01|MOD-02 build|export|verify|dump`). Live Blender 5.2 via MCP
(add-on reported OUTDATED, fallback mode; execute_blender_code and look worked). Live work only in the collections
`MOD-01_Lattice_Panel` and `MOD-02_Lattice_Post` (left in place). The owner's file was not saved (unsaved, filepath ''); the
default Cube and the other collections were not touched; selection (Cube, active Cube) checked before/after the live
export: unchanged. Temporary scenes (renders, FBX verify, PLT-02 bbox import) were removed; only `Scene` remains.

## Result

| | MOD-01 | MOD-02 |
|---|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Lattice_Panel.fbx` (+ .fbm) | `art/CottageGardenDecor/Meshes/FMS_Garden_Lattice_Post.fbx` (+ .fbm) |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Lattice_Panel.blend` | `art/CottageGardenDecor/Blend/FMS_Garden_Lattice_Post.blend` |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_MOD_01_Preview.png` | `art/CottageGardenDecor/Previews/FMS_Garden_MOD_02_Preview.png` |
| Tris / budget | 296 / 900 (Frame 32 + Slats 264 = 22 × 12) | 36 / 60 (Shaft 10 + Cap 26) |
| Size (Blender X × Y × Z) | 1.880 × 0.060 × 1.750 (z 0.05…1.80) | 0.160 × 0.160 × 1.950 |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same |
| LOD | none (catalogue) | none (catalogue) |

- Material `M_Garden_Build` + shared `art/CottageGardenDecor/Textures/FMS_Garden_AtlasA.png` (read only: loaded, never saved; MD5
  `119daf05…` unchanged; palette by pixel read: 0 mismatches). One cell: A-10 White paint `#EEEDE7` for everything
  (spec Palette note; same white as STR-01_White / STR-06 frame). Slot A-2 unused. Flat shading (0 smooth faces), no bevels.

## Construction
- **Frame**: one closed rectangular ring shell (outer ±0.94 × 0.05…1.80, inner ±0.86 × 0.13…1.72, thickness ±0.03): the
  4 members of the spec as one shell, so there are no internal stile/rail contact faces (would be coplanar overlaps).
- **Slats**: 0.05 wide (see deviations), 0.030 thick, perpendicular pitch 0.20, 11 per direction; centre lines through the
  opening centre, so layer A mirrored in X = layer B footprint (symmetric pattern). Layer A (+45°, spec Z 0…+0.03) at
  Blender Y −0.029…+0.001, layer B (−45°) at −0.001…+0.029: 1 mm behind the frame faces, 2 mm interpenetration at the
  crossings → no coplanar faces. Slats clipped to the opening expanded by 1 cm: the ends are buried in the frame members
  (visually flush on the inside faces, no end caps in the opening). Corner pieces smaller than 0.004 m² visible area are
  dropped (none were; smallest 0.017 m²). Real gaps, no faces over the openings.
- **Post**: one closed shell: shaft 0.12² z 0…1.80, horizontal step ring at 1.80 (cap underside), cap 0.16² z 1.80…1.93,
  chamfer 0.02 to a flat 0.12² top at 1.95, bottom face on the ground.

## Pivots and axes
- Both roots at (0, 0, 0) = centre of the base on the ground (Y = 0 in Unity), rot 0, scale 1. FBX: Y up, −Z forward
  baked (pc.export). Blender (x, y, z) → Unity (−x, z, −y). Spec "Z" (thickness / post axis) = Blender −Y.
- MOD-01 front (where PLT-02 mounts) = Blender −Y = Unity +Z; the panel is symmetric, either face works.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0; mirror X 0.000000 (frame / post; slats checked as layer A ↔ B
  footprint: True); max face non-planarity 0.0000 mm.
- Coplanar overlapping face pairs 0 (both).
- Ground: MOD-02 min z 0.0000 (whole base on the ground). MOD-01 min z 0.05 by contract (carried by the posts).
- SNAP OK (CATALOG «Модули и стыковка» item 1), printed by both runs: MOD-01 bbox ±0.94 / ±0.03 / 0.05…1.80; MOD-02 bbox
  0.16 × 0.16 × 1.95, shaft faces ±0.06 up to 1.80; posts at 0 and 2.0 + panel at 1.0: gap frame end ↔ shaft face
  0.000 / 0.000 mm, frame end faces inside the shaft faces, post pitch 2.000, frame top 1.800 = cap underside 1.800 (cap top
  1.95), no panel vertex inside a post; 90° corner (panel rotated about the shared post): gap 0.000 mm, panels do not overlap.
  Contact faces frame end ↔ shaft face and frame top ↔ cap underside strip (x 0.92…0.94) are coplanar by contract
  (gap = 0); they are enclosed by both solids, so not visible.
- PLT-02 mount (approved `FMS_Garden_Rose_Climbing_Side.fbx`, imported read-only into a temp scene): bbox 0.696 × 0.237 ×
  2.014, back plane y = 0. Pivot at the panel front face (y −0.03): back plane on the frame face, 1.0 mm in front of the
  slats; width 0.696 ≤ opening 1.72; stands on the ground (panel bottom 0.05); top 2.014 = +0.214 above the panel top and
  +0.064 above the post cap (climber spills over, as intended). Note: PLT-02 notes assumed panel top 1.85; actual 1.80.
- FBX re-import: MOD-01 2 nodes / 296 tris / dims 1.88 × 0.06 × 1.75; MOD-02 2 nodes / 36 tris / 0.16 × 0.16 × 1.95;
  texture found in each `.fbm`.
- Headless `build.py -- MOD-0x export` (PACK_ART = %TEMP%/assetnew_check/<ID>/headless_art): geometry SHA1 == live —
  MOD-01 `29960aac8cec487dc56f7163d413d5541039931e`, MOD-02 `8e95edb53fedca415a9a7ae42effb971e777b24a`.
  No `Tools/blender/__pycache__` left.
- Check renders: %TEMP%/assetnew_check/MOD-01 (ref angle, preview, 128 px thumb, assembly post+panel+post+corner),
  %TEMP%/assetnew_check/MOD-02.

## Rounds
- MOD-01: 2 rounds. Round 1 (spec slat 0.04): pattern, count (11/direction) and pitch match the reference, but the
  slats read thinner. Measured the reference (≈460 px/m): pitch ≈0.21 (spec 0.20 kept), slat ≈0.055 wide. Round 2: slat
  0.05 → matches; 128 px thumbnail reads as a white diamond lattice in a frame. Stopped (nitpicks only).
- MOD-02: 1 round. Cap/shaft width ratio 1.33 (reference ≈1.36), flat chamfered cap, square shaft; matches.

## Deviations / remaining differences vs the references
1. MOD-01 slat width 0.05 instead of spec 0.04 (reference wins, PIPE-04; not a functional size, zero tris cost).
   Thickness 0.030 per layer and all snap numbers unchanged.
2. Frame is one ring shell instead of 4 boxes: same outer/inner numbers; the reference's joint lines between stiles and
   rails are not modelled (flat white, no bevels per spec).
3. White `#EEEDE7` renders cooler/brighter than the reference's cream; palette fixed by the spec (same white as STR-01/06).
4. Lattice phase: centre lines through the opening centre (symmetric); the reference's corner pieces sit slightly
   differently. Not visible at 128 px.
5. MOD-02 chamfer 0.02 per spec; the reference's chamfer looks a little larger. Minor.
