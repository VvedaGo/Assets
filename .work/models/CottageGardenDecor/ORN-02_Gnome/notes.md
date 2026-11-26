# ORN-02 Garden Gnome `FMS_Garden_Gnome` (+ `_Blue`) — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- ORN-02 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in collection `ORN-02_Gnome` with the child collection
`ORN-02_Gnome_Blue` (left in place). The owner's file (unsaved, no path) was not saved; the default Cube and the other
collections were not touched; the selection (Cube, active Cube) was restored after every live run and after the export.
Check renders in a temporary scene → `%TEMP%/assetnew_check/ORN-02/`, viewed with `look image=`.

## Result

| | base | `_Blue` |
|---|---|---|
| FBX | `Meshes/FMS_Garden_Gnome.fbx` (+ .fbm) | `Meshes/FMS_Garden_Gnome_Blue.fbx` (+ .fbm) |
| Tris / budget | 586 / 600 | 586 / 600 |
| Size X × Y × Z (Blender) | 0.243 × 0.226 × 0.450 | same (same vertices, checked) |
| Nodes | root empty `FMS_Garden_Gnome` + `FMS_Garden_Gnome_Body` | same with `_Blue` |

- Tris per component: Boots 40 (2 × 20), Coat 76 (incl. painted belt band), Head 44, Hat 78, Arms 64 (2 × 32),
  Hands 160 (2 × 80), Nose 80, Beard 44.
- One `.blend` (`Blend/FMS_Garden_Gnome.blend`) holds both collections; ONE preview
  (`Previews/FMS_Garden_ORN_02_Preview.png`, base).
- Material `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette checked by
  pixel read: 0 mismatches). Atlas F not used.
- Slots base: boots 1, coat + arms 15, belt 13, head/hands/nose 3, beard 10, hat 5. `_Blue`: hat 15, coat + arms 5,
  rest unchanged (UV only).
- No LOD, no Lite (catalogue).

## Pivot and axes
- Root (0, 0, 0) = centre between the boots on the ground; rot 0, scale 1. FBX Y up, −Z forward baked.
- Blender: X right, −Y front (= Unity +Z, spec "faces +Z"), Z up. Mirror X 0.000000.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 (every component touches another); coplanar overlaps 0.
- Ground contact: min z 0.0000, 8 ground vertices (2 boot soles); nothing below 0.
- Contacts: wrists end inside the hands; hands sunk into the belly (back at y −0.070 vs coat front ~−0.08); nose sunk into the
  beard; beard top tucked 7 mm under the hat; head top inside the hat, bottom inside the coat; boot tops 6 mm inside the coat
  hem; hat tip ring Ø0.030 (spec ≥ 0.03) with a short apex point above.
- Size: height 0.450 exactly (apex), X 0.243, Y 0.226 (≤ 0.25 catalogue). No SNAP contract (free-standing decor).
- FBX re-import: 2 nodes each / 586 tris, dims 0.243 / 0.226 / 0.45, texture found in each `.fbm`.
- Headless `build.py -- ORN-02 export` geometry SHA1 == live SHA1 `d99eb25b64e0be534dc3ecf5a180dc27f8a64c7e`.

## Rounds (3 live)
1. All checks OK, 584. vs reference: camera too high; cream band of the head visible at the back between the shoulders and
   the hat (read as a bald neck); beard narrow and pyramid-like (single front apex); sleeves thin.
   → hat lowered 0.262 → 0.245 and coat top raised 0.215 → 0.222 (gap closed); beard wider (half-width 0.076) with a vertical
   front ridge (2 ridge vertices → gem facets); sleeves apothem 0.028 → 0.031; reference camera elevation lowered.
2. Back clean, beard reads as the reference shield. Remaining: hat lean less visible than the reference; boots tall boxes.
   → apex bent back 0.036 → 0.050 (progressive bend through the rings); boot straight part 0.032 → 0.026, top chamfer 0.014.
3. Matches the reference: cone hat leaning back, nose ball under the brim, shield beard to the belt, hands at the beard sides,
   dark belt, boots. 128 px thumbnail: red cone + white beard + blue coat read as a gnome. Stopped (only nitpicks left).

## Deviations from `prompts/ORN-02.3d.md` (for the reviewer)
1. **Spheres = bmesh icosphere subdivisions 2 (80 facets)**: Blender's subdivision 1 is a bare 20-face icosahedron; the spec's
   ~80-tri estimates match subdivision 2. Hands therefore 2 × 80 = 160 (spec ~80 for both); paid for by a cheaper head
   (8-sided 3-ring loft, 44 tris, mostly hidden) and boots (4-sided, 20 each).
2. **Head = 8-sided rounded loft**, not an icosphere (hidden under hat and beard; only a sliver shows at the back).
3. **Belt = painted band of the coat loft** (flush, as the reference), z 0.085–0.110, not a separate Ø0.19 ring at 0.115–0.135:
   the reference belt sits ~1/5 of the coat height above the hem and the beard tip touches it.
4. **Hat base 0.245** (spec 0.27) so the brim sits on the shoulders (reference; no neck gap); apex 0.450, bent back 0.050
   (spec 0.02; the reference apex leans clearly). Brim band 0.012 high.
5. **Boots 0.075 × 0.12 × 0.056** (spec 0.07 × 0.10 × 0.05): reference boots are wider and their toes show in front of the hem;
   top 6 mm inside the coat so no coplanar seam with the hem.
6. Arms 6-sided Ø ≈ 0.050–0.062 (spec ≥ 0.04; reference sleeves are chunky).

## Remaining differences vs the reference
- Hat cone straight-sided with a gentle back bend; the reference shows a slight kink and a stronger lean to the back-right.
- Boots are chamfered boxes; the reference toes are a bit rounder.
- Palette as fixed for the pack (white beard `#EEEDE7` cooler than the warm reference white; blue `#4A78A8`).
