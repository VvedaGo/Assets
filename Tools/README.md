# Pack production tools (shared by all packs)

Origin: Farm Processing (72 models, 2026-11-13…20). Everything here was used in production on that pack; the pack itself
keeps its own build scripts under `.work/models/<Pack>/` in its branch. New packs start from these files instead of copying
the previous pack's helpers.

## Pipeline at a glance

| Step | What | Tool |
|---|---|---|
| 1. Plan | Catalogue (ID, size, tris budget, moving parts), one reference image per ID, duplicate check against earlier packs, pilot items and SNAP contracts for modules (walls, floors, posts) | pack plan + REQUIREMENTS.md section 10 |
| 2. Build | One idempotent procedural script per model or one registry script for a family of small props: `build_xxx.py -- <ID> build|export` | `blender/pack_common.py`, `blender/pack_shapes.py`, `blender/build_registry_template.py` |
| 3. Check | Printed numbers (tris per part, non-manifold/loose/degenerate 0, mirror, contacts, SNAP), check render at the reference angle + 128 px thumbnail | `pack_common.comp_checks`, `coplanar_overlaps`, `report` |
| 4. Export | FBX (Y up, −Z forward baked, scale 1; nested-child fix built in), `.fbm` texture copy, collection-only `.blend`, ONE preview PNG, FBX re-import verify | `pack_common.export/verify/save_lib` |
| 5. LOD | Stations/hero props: LOD1 = 50% per part, palette re-snapped (never Unity's automatic Mesh LOD on a flat atlas) | `blender/make_lod1.py` |
| 6. Review | Every model against its reference on paired sheets; verdict file pass / notes / fix / decision | `blender/compare_sheets.py`, `agents/REVIEW_TEMPLATE.md` |
| 7. Unity | Import settings, URP material per atlas, prefabs + BoxCollider + LODGroup, report at `.work/ImportReport_<Tag>.txt` | `Assets/Editor/PackTools/PackPrefabBuilder.cs` |
| 8. Scenes | Courtyard, compositions (CMP prefabs), catalog, store media: text layouts → scenes → renders | `Assets/Editor/PackTools/PackSceneBuilder.cs` |
| 9. Commit | After every accepted batch (not at the end) | git |

## Blender (headless)

```
set PYTHONUTF8=1
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python <script> -- <args>
```
- Headless is the default: several builds can run in parallel and nothing depends on the live MCP add-on (it disconnects
  and cannot be shared). Use the live MCP only to look at something interactively.
- No AI 3D generators were available; models are procedural from the reference image. Measure the reference in pixels.
- Write Python to files and run them; heredocs with triple quotes break the Bash tool.
- Check renders go to `%TEMP%`, never into `art/`. `art/<Pack>/Previews` holds exactly one preview per model.

### Files
- `blender/pack_common.py` — Part (faces + palette slot), profiles, flat atlas (256 px, 4x4 cells), URP-friendly material,
  `comp_checks`, `coplanar_overlaps`, `to_object`, `report`, `export` (with the Blender 5.2 nested-child FBX fix),
  `verify`, `save_lib`.
- `blender/pack_shapes.py` — standard 16-cell palette constants and shapes: `shell` (solid of revolution with through/blind
  holes), `fill` (planar region with holes), `path_sweep` (mitred loop handles), `flat_plate`, `bolt`, `oct_rod`, `plank4`,
  `basin_loft`, `poly_offset`, `arc`, `box`, `plain_box`, `splay_leg`, `red_cap`, `rest_on_ground` (lays a lying tool on its
  convex-hull support), `center_on_ground`.
- `blender/build_registry_template.py` — skeleton of a registry script (many items, one file, `-- <ID> build|export`).
- `blender/make_lod1.py -- --art <art dir> NAME...` — LOD1 children for the Unity LODGroup. Rerun after any re-export.
- `blender/compare_sheets.py --ref <dir> --pre <dir> --pattern ...` — reference | model sheets.

## Unity (6000.3, URP)

- Per pack: a small wrapper with menu items and a `PackConfig` (root, tag, atlas regex, prefix, floor codes, layout dir).
  Example: `Assets/Editor/FarmProcessing/` in the `Farm-Processing` branch.
- Drive the open Editor with `unity command eval` through `unity/unity_eval.sh` (detached job + poll: direct eval stops
  after 5 s). Refresh the AssetDatabase in its own call after copying files in.
- Layout space and directives: see the summary of `PackSceneBuilder`. Items without an explicit y stand at 0.15 (floor top).

## Agents

- `agents/EXTERNAL_WORKER_BRIEF.md` — common brief for model workers (Codex or Claude subagents), with the defects the lead
  rejected most often. Append a short item spec per model.
- `agents/REVIEW_TEMPLATE.md` — review file format.
