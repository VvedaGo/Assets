# DEM-06 Demo Clouds (`FMS_Mach_Demo_Clouds`) — builder notes (2026-11-24, owner request "the sky is too plain")

Demo environment piece (not a catalogue product). Built and checked HEADLESS only — **no live MCP pass** (the live Blender
MCP server was still not reachable). Style target: Farm Nature `Beauty_01_Overall.png` (white faceted cumulus around / below
the floating island).

## Output
- One FBX `art/FarmMachinery/Demo/Meshes/FMS_Mach_Demo_Clouds.fbx`: root `FMS_Mach_Demo_Clouds` + 4 separate child objects
  `Cloud_A..D`, each with its origin at its own bottom centre (Y 0), laid out along X (−18.7 / −0.7 / +13.3 / +23.3); the demo
  scene places / scales them freely around and below the island. Blend + one preview in Demo/{Blend,Previews}.
- Each cloud = 3–5 merged jittered icospheres (subdivision 2, 80 tris each), upper halves full, lower halves squashed to 30 %
  → flat-ish faceted bottom; lumps overlap (merged look, separate shells inside one object — intentional, no seams visible).

| Cloud | Lumps | Tris | Size X × Y × Z, m |
|---|---|---|---|
| Cloud_A | 5 | 400 | 15.5 × 5.1 × 7.2 |
| Cloud_B | 4 | 320 | 12.1 × 4.3 × 6.2 |
| Cloud_C | 4 | 320 | 8.9 × 3.3 × 4.9 |
| Cloud_D | 3 | 240 | 6.1 × 2.0 × 3.7 |
Total 1280 tris (catalogue 150–400 each — all within). No LOD.

## Atlas
- The demo atlas has no free cell: all 16 cells are used (assembler recolour, md5 8b41ff7e…). Adding white + blue-grey
  shade cells would need changing an existing cell, which the task forbids → **atlas unchanged**: the clouds use the existing
  white cell 9 (#EDEAE0); the shade comes from the faceted shading. build.py loads the atlas as is (never rewrites it).
  md5 after export: art 8b41ff7e (unchanged), machines' atlas eb6768e2 (unchanged).
- If a cooler shade underside is wanted later: it needs a 5×4 / larger atlas or a cell sacrificed — owner / assembler decision.

## Checks
Non-manifold / loose / degenerate 0, coplanar 0, gaps 0 (per lump). FBX re-import: 5 nodes, 1280 tris, texture found.
Rounds 2 (round 1: subdivision 1 lumps read as crystals → subdivision 2; bottoms aligned to Y 0).
