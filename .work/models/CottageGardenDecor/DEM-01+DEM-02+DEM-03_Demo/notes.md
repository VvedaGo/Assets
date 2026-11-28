# DEM-01 / DEM-02 / DEM-03 — demo environment of Demo_CottageGarden (builder notes, 2026-11-26)

> **CURRENT STATE = section «Fix 1 (renders_1)» below.** Sections further down describe the first build (2026-11-26 morning,
> 24 x 18 m garden) and are kept for history; their sizes / coordinates are superseded.

## Fix 1 (renders_1, 2026-11-26) — island x0.75, path centreline x0.75, deeper lawn
Review `planning/CottageGardenDecor/reviews/renders_1.md` + Fix 1 in scenes/Hero.md, Cover.md, AltView.md: garden too sparse on a
too big island. `PLAN = 0.75` in build.py.
- **Garden area (usable, layout space) = x -9..9, z -6.75..6.75 (18 x 13.5 m), origin = its centre, lawn top Y 0.**
- DEM-01 Island: the whole first design scaled uniformly x0.75 (outline, facets, underside): lawn 20.33 x 16.23 m
  (x -10.29..10.04, z -8.07..8.15), bbox 20.45 x 2.93 x 16.35 m, underside to Y -2.93 (cliff to ≈ -0.98). Tris 996 / 3000.
  Garden rectangle inside the lawn: corner margin 0.13 m, side margin ≥ 0.79 m; garden = 79 % of the lawn area.
  Checks: non-manifold / loose / degenerate / coplanar 0; 163 top vertices exactly Y 0, upward faces off Y 0: 0;
  ray grid 0.25 m over x -9..9, z -6.75..6.75 (4015 rays): misses 0, all on the flat Y 0 lawn.
- DEM-02 Path: centrelines scaled x0.75, **widths kept** (main 1.8 m, branch 1.5 m; review «width kept», task ≥ 1.5 m),
  top Y 0.01, bottom 0.002. Tris 308 / 600. Extent x -2.89..3.18, z -7.77..5.04 m. All 78 top vertices over the flat lawn,
  gap 0.0100 m. Control points (layout x, z; Catmull-Rom through them):
  - main: (-1.80, -7.68) south edge start (0.15 m inside the lawn edge, square end) → (-1.95, -5.55) → (-1.50, -3.45) →
    (-0.60, -1.35) → (0.30, 0.68) → (0.98, 2.40) → (1.88, 3.68) → **end (2.70, 4.28)** + 0.25 m blunt tip, heading NE
    (gazebo steps CMP-03: entrance ≈ (2.9, 4.5), facing SW).
  - branch: fork (0.53, 1.65) (inside the main path) → (-0.15, 2.70) → (-1.20, 3.45) → **end (-2.48, 3.90)** + 0.25 m tip
    (pond approach CMP-05 NW, arch opening towards it).
- Lawn cells: 0 `#7DB93C` (review target), 1 shade `#76B137`, 2 light `#84BF45` (demo atlas only; A / F untouched, md5
  A 119daf05…, F ae0f0dba…; demo atlas 8d6d6323…, identical copies in the three .fbm).
- DEM-03 Clouds: geometry unchanged (same fingerprints); re-exported only to refresh the atlas copy in its .fbm.
- Live (owner's Blender 5.2, scene DEM_Demo) == headless fingerprints: Island `(500, 996, -1299.981, 36340.7597)`,
  Path `(156, 257, 86.8461, 2579.1698)`, Clouds as before. FBX re-import: 2 / 2 / 6 nodes, 996 / 308 / 1360 tris, texture found.
- Unity: re-copy the three FBX + the demo atlas into the project (meta GUIDs kept by overwriting in place); island and path
  at (0, 0, 0); re-space the layout to x -9..9, z -6.75..6.75.

Demo-only assets (not catalogue models, removable, not counted), like `FMS_Mach_Demo_*` of Farm Machinery. Approach copied
from Farm Machinery `DEM_IslandBase` / `DEM_Clouds` (origin/Farm-Machinery, read-only): Unity-space design mapped to Blender
(-x, -z, y), FBX -Z forward / Y up baked, own demo atlas + material, `pc.export / save_lib`, headless re-import verify.

Build: ONE registry script `build.py -- <ID> check|build|export`. Live pass in the owner's Blender 5.2 through the MCP (own
scene `DEM_Demo`, collections `DEM_Demo/FMS_Garden_Demo_*`; owner's `Scene`, Cube and other collections untouched, file not
saved). Exports headless. Live and headless fingerprints are identical:
- Island `(500, 996, -1733.3078, 64605.7961)`, Path `(162, 267, 87.3728, 4553.8027)`,
  Clouds A `(168, 320, 606.0584, 2614.8994)` … E `(126, 240, 250.6352, 381.884)`.

## Layout convention (for the Unity assembler)
- Layout space = Unity world of the demo scene (PackSceneBuilder): X east (right), Y up, Z north (camera at -Z looking +Z).
- **Garden layout origin (0, 0, 0)** = centre of the 24 × 18 m garden: x -12..12, z -9..9. **Lawn top = Y 0** exactly.
- Island and path are both built in this space with the pivot at the origin: place both at (0, 0, 0), rotation 0, scale 1.
- Pack prefabs on the lawn: y 0 — pass y 0 explicitly in the layout (PackSceneBuilder default y is 0.15 = floor tile top).
- Items on the path (if any): y 0.01.

## DEM-01 `FMS_Garden_Demo_Island`
- Irregular faceted outline (56 points): rounded rectangle 26 × 20 m (corner radius 3 m) pushed **outwards only** by
  0.05–0.8 m of smooth noise. Lawn 27.10 × 21.63 m (x -13.72..13.39, z -10.77..10.87); bbox 27.26 × 3.90 × 21.79 m.
- Top: flat lawn at Y 0 (163 vertices, all exactly 0), CDT of the outline + jittered ~2.2 m grid → large flat triangles in
  three close lawn tones (68 / 17 / 15 %). Grass lip (dark green) to Y -0.20, soil top edge -0.34, faceted vertical soil cliff
  to ≈ -1.3, dark soil taper to ≈ -2.05, rock underside -2.9 / -3.5, bottom point Y -3.90. Two soil tones per band (facets).
- Tris 996 / 3000. Pivot (0, 0, 0) = garden origin on the lawn top. No LOD (demo).
- Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0; upward faces not at Y 0: 0; ray grid 0.25 m over x -12..12,
  z -9..9 (7081 rays): misses 0, all hits on the flat Y 0 lawn (|Y| ≤ 6e-8 = float ray precision). Garden rectangle inside
  the lawn: corner margin 0.17 m, side margin ≥ 1.05 m.
- Rounds 3: (1) outline too rectangular, underside too slab-like → corner radius 2.2 → 3.0, stronger noise, deeper taper;
  (2) lawn tone pattern busy → main tone 58 → 68 %.

## DEM-02 `FMS_Garden_Demo_Path`
- Thin closed slab: **top Y 0.01** (0.01 above the lawn), bottom Y 0.002 (no coplanar faces with the lawn, side faces 8 mm).
- Main path 1.8 m wide, gentle S-curve (Hero): starts square at the south edge, centre (-2.40, -10.30) — 0.15 m inside the
  lawn edge — through (-2.0, -4.6), (0.4, 0.9), (1.3, 3.2) and ends with a blunt facet at **(3.6, 5.7)** heading north-east
  = gazebo steps (CMP-03 NE: put the gazebo entrance at ≈ (3.9, 5.9) facing south-west).
- Branch 1.5 m wide leaves the main path at the fork ≈ (0.7, 2.2), runs north-west through (-1.6, 4.6) and ends at
  **(-3.3, 5.2)** = short approach to the pond (CMP-05 NW, arch opening towards the path, as in Cover).
- Faceted top: CDT union of both strips + centreline points, three sand tones; no bevels. Extent x -3.54..4.08,
  z -10.39..6.46 m. Tris 320 / 600. Pivot (0, 0, 0) = garden origin (place at the island origin).
- Checks: non-manifold 0, loose 0, degenerate 0, coplanar 0; 81 top vertices all over the flat lawn (temporary island copy,
  not exported), top-to-lawn gap min = max = 0.0100 m.
- Rounds 2: (1) straight diagonal and a hook-like branch → S-curve turning east to the gazebo, smooth fork; softer sand tones.

## DEM-03 `FMS_Garden_Demo_Clouds`
- One FBX: root `FMS_Garden_Demo_Clouds` + 5 child objects `Cloud_A..E`, each = one wide flat base lump + 2–3 rounded bumps
  (jittered icospheres subdiv 2, 80 tris each, lower halves squashed to 30 % → flat faceted bottom, faces turned down use the
  cloud-shade cell). Origin of each cloud at its own bottom centre (Y 0); laid out along X in the FBX.

| Cloud | Lumps | Tris | Size X × Y × Z, m | Origin in the FBX (Unity) |
|---|---|---|---|---|
| Cloud_A | 4 | 320 | 11.31 × 4.23 × 5.23 | (-22, 0, 0) |
| Cloud_B | 4 | 320 | 9.42 × 3.79 × 4.59 | (-8, 0, 0) |
| Cloud_C | 3 | 240 | 7.24 × 3.02 × 3.80 | (4, 0, 0) |
| Cloud_D | 3 | 240 | 6.18 × 2.48 × 3.40 | (13, 0, 0) |
| Cloud_E | 3 | 240 | 4.88 × 2.06 × 2.94 | (21, 0, 0) |
Total 1360 / 1500. Checks: non-manifold / loose / degenerate 0, coplanar 0 (lumps intersect inside — intended).
- Placement: move the child clouds individually (unpack the prefab or reposition the children). Hero / Cover: 4–6 clouds in
  the sky band behind the island (z ≈ +20…+35, y ≈ +2…+8 for the 40° Hero camera) and 1–2 lower in front/below the island
  corners (y ≈ -6…-3) for depth; uniform scale 0.8–1.5 is fine.
- Rounds 2: (1) separate balls → flat continuous base lump per cloud (Hero look).

## Demo atlas `art/CottageGardenDecor/Textures/FMS_Garden_Demo_Atlas.png` (256 px, 4 × 4 × 64 px), material `M_Garden_Demo`
Sand for the path is not in atlases A / F, so a separate demo atlas holds ALL demo cells (one demo material, removable with
the demo). Series HEX reused where the pack has the colour; `*` = new demo colour. Atlases A / F untouched (git clean).

| Cell | HEX | Use |
|---|---|---|
| 0 | `#8AB257` | lawn main (= F1 light leaf / demo grass Yard, Nature) |
| 1 | `#84AC52` | lawn shade * |
| 2 | `#90B75C` | lawn light * |
| 3 | `#6E9F4A` | grass lip (= F0 leaf) |
| 4 | `#805433` | soil (= F12) |
| 5 | `#8C5E3A` | soil light, top edge * |
| 6 | `#6B4429` | soil dark * |
| 7 | `#5E4436` | underside rock (= FM demo skirt lower) * |
| 8 | `#E2B07C` | path sand * |
| 9 | `#DBA874` | path sand shade, slab sides * |
| 10 | `#E7B985` | path sand light * |
| 11 | `#C8925E` | path bottom (never visible) * |
| 12 | `#F4F1E8` | cloud white (= F8 white flower) |
| 13 | `#E3E7EC` | cloud underside shade * |
| 14 | `#7A5233` | spare (= A1 dark wood), unused |
| 15 | `#A7A39A` | spare (= A12 stone), unused |

## Output
- `art/CottageGardenDecor/Demo/Meshes/FMS_Garden_Demo_{Island,Path,Clouds}.fbx` (+ `.fbm` with the atlas copy)
- `art/CottageGardenDecor/Demo/Blend/FMS_Garden_Demo_{Island,Path,Clouds}.blend` (collection-only)
- `art/CottageGardenDecor/Demo/Previews/FMS_Garden_Demo_{Island,Path,Clouds}_Preview.png` (path preview shows the island
  as context only)
- FBX re-import (headless): Island 2 nodes 996 tris, Path 2 nodes 320 tris (Y 0.002..0.01), Clouds 6 nodes 1360 tris;
  dims as built; texture found in the `.fbm`.
- Check renders: `%TEMP%/assetnew_check/DEM-0x/`, live assembly render `%TEMP%/assetnew_check/DEM_assembly_live.png`.
