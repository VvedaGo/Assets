# MOD-05 Brick edging `FMS_Garden_Edging_Brick` + MOD-06 Brick edging curve `FMS_Garden_Edging_Brick_Curve` — builder notes (Э7, series batch 1, 2026-11-25)

Source of truth: `build.py` (one registry script, `-- MOD-05|MOD-06 build|export|verify|dump`). Live Blender 5.2 via MCP
(add-on reported OUTDATED, fallback mode; execute_blender_code and look worked). Live work only in the collections
`MOD-05_Edging_Brick` and `MOD-06_Edging_Brick_Curve` (left in place). The owner's file was not saved; the default Cube and
the other collections were not touched; the selection (Cube, active Cube) was checked before/after the live export: unchanged.

## Result

| | MOD-05 | MOD-06 |
|---|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Edging_Brick.fbx` (+ .fbm) | `art/AssetNew/Meshes/FMS_Garden_Edging_Brick_Curve.fbx` (+ .fbm) |
| Blend | `art/AssetNew/Blend/FMS_Garden_Edging_Brick.blend` | `art/AssetNew/Blend/FMS_Garden_Edging_Brick_Curve.blend` |
| Preview | `art/AssetNew/Previews/FMS_Garden_MOD_05_Preview.png` | `art/AssetNew/Previews/FMS_Garden_MOD_06_Preview.png` |
| Tris / budget | 100 / 200 (Bricks 96 + Ends 4) | 148 / 300 (Bricks 144 + Ends 4) |
| Size (Blender X × Y × Z) | 1.000 × 0.100 × 0.150 | 1.050 × 1.050 × 0.150 |
| Nodes | root empty + `_Body` (1 mesh, 1 material) | same |
| LOD | none (catalogue) | none (catalogue) |

- Material `M_Garden_Build` + shared `art/AssetNew/Textures/FMS_Garden_AtlasA.png` (read only: loaded, never saved;
  MD5 `119daf05…` unchanged after all runs; palette check by pixel read: 0 mismatches). Cells: 14 Brick `#9C3F33`
  (even bricks), 6 Red dark `#A8372E` (odd bricks). Flat shading (0 smooth faces), no bevels, no ground plate.

## Construction
- One closed shell per module. Brick k = two pentagonal sides (flat bottom at 0, vertical sides to the valley 0.0875,
  roof to the peak 0.15 in the brick middle) + two roof quads + one bottom quad. Neighbouring bricks share the border edges
  (no internal faces → no coplanar overlaps). End faces = flat vertical rectangles 0.10 × 0.0875 at the valley.
- MOD-05: 8 bricks × 0.125 along Blender X (−0.5 … 0.5), depth Blender Y ±0.05, roof exactly 45°.
- MOD-06: 12 bricks × 7.5° on the axis radius 1.0 (0.95 … 1.05). All faces are planar (max non-planarity 0.0001 mm):
  the side pentagons lie on the chords (ridge ends at r·cos 3.75°), the roof planes contain the radial eave lines, so the
  ridge rises slightly outward: 0.144 at the inner face, 0.150 at the outer face (fitted so the max height = 0.15 = MOD-05).
  Roof slope ≈ 42° (45°-class). On the axis the first peak is 0.0654 m from the end vs 0.0625 on MOD-05.

## Pivots and axes
- MOD-05 root (0, 0, 0) = centre of the base; MOD-06 root (0, 0, 0) = circle centre at ground level. rot 0, scale 1.
  FBX: Y up, −Z forward baked (pc.export).
- Mapping Blender (x, y, z) → Unity (−x, z, −y) (Unity's FBX import negates X; same convention as STR-01/PLT-02 notes).
- MOD-06 is built in the Blender quadrant x ≤ 0, y ≤ 0 so its ends lie at Unity (1, 0, 0) [Blender (−1, 0, 0)] and Unity
  (0, 0, 1) [Blender (0, −1, 0)], as in the contract. **To confirm at Э8 in Unity**: the arc should occupy the +X/+Z
  quadrant of its pivot; if Unity shows it in −X/+Z, the X-flip assumption is wrong (fix = mirror the arc in build.py,
  `A0 = 1.5π` and reversed order, or rotate the prefab by −90°).

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0; mirror X 0.000000 (MOD-05); MOD-06 symmetric across the
  bisector 0.000000 (mirror X not applicable).
- Coplanar overlapping face pairs 0 (both).
- Ground contact: min z 0.0000, whole bottom on the ground (both).
- SNAP OK (printed by both runs, contract CATALOG «Модули и стыковка» item 3):
  MOD-05 bbox ±0.5 / ±0.05 / 0–0.15; end faces flat at x = ±0.5; MOD-05 ↔ MOD-05 end sections identical (0.000 mm);
  valley on both ends; placed at node + 0.5 → ends on nodes. MOD-06 bbox 1.05 × 1.05 × 0.15, end faces = radial cuts,
  end centres on grid nodes (Unity (1,0,0) and (0,0,1)), valley on both ends. MOD-05 ↔ MOD-06 joint A (strip on the grid
  line through the Unity (1,0,0) end) and joint B (Unity (0,0,1) end): 4/4 section vertices identical, 0.000 mm, no
  interpenetration. 4 × MOD-06 rotated 0/90/180/270 = closed ring of axis Ø2.0 (0.000 mm).
- Colour phase: each module starts with an even (slot 14) and ends with an odd (slot 6) brick, so chains laid in one
  direction keep the alternation (strip → strip, strip → arc, ring). Turned pieces can put two same-tone bricks together.
- FBX re-import: MOD-05 2 nodes / 100 tris / dims 1.0 × 0.1 × 0.15; MOD-06 2 nodes / 148 tris / 1.05 × 1.05 × 0.15;
  texture found in each `.fbm`.
- Headless `build.py -- MOD-0x export` (PACK_ART = %TEMP%/assetnew_check/<ID>/headless_art, so the live files were not
  overwritten): geometry SHA1 == live — MOD-05 `24e73fa49d92328cb08fee6357225cabc32f52b4`, MOD-06
  `de914758517020c55ef86ae217b1fb218731d89f`. No `Tools/blender/__pycache__` left.

## Rounds
- MOD-05: 1 round. Reference-angle render, preview and 128 px thumbnail: sawtooth reads clearly; proportions match the
  reference (brick h/w 1.2 vs ~1.23 measured on the reference).
- MOD-06: 2 rounds. Round 1: the visible inner faces were in shade (temporary sun fixed to world −Y, camera from the arc
  centre side). Round 2: render lights turned with the camera (`light_az` 100°) — affects only the preview, not the mesh.

## Remaining differences vs the references
1. Two-tone alternation is subtler than in the references (#9C3F33 vs #A8372E are close in value); palette is fixed by
   the spec and the atlas is read only, so kept.
2. Reference bricks have slightly softened edges; the spec forbids bevels, so edges are sharp.
3. MOD-06 reference bricks look taller relative to their width (h/w ≈ 1.6); the section 0.10 × 0.15 identical to MOD-05 is a
   functional snap size and wins (PIPE-04).
4. MOD-06 ridge slopes 6 mm across the brick depth (0.144 → 0.150), needed for planar flat-shaded faces; not visible.
