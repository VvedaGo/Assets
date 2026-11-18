# Farm Processing — common rules for Codex model workers

You build ONE stylized low-poly 3D model for a Unity Asset Store pack ("Farm Processing & Workshops") with a procedural Blender Python script, matching a reference image. Ten models of the pack are already done and approved; yours must look like it belongs with them.

## Read first (in this order)
1. `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_common\PIPELINE.md`: the full pipeline (inputs, palette, output paths, naming, hierarchy, checks, export, preview, and "Lessons from lead reviews"). Follow it exactly. Where it says "agent", that means you.
2. `C:\Users\Sergv\.claude\skills\blender-unity-assets\SKILL.md`: sections 2–4, 9–13 (axes, naming, checks, FBX export, reference-matching loop, preview, house style, acceptance gate).
3. Your reference image and the approved model named in your Task as the closest anchor: its `build_*.py`, `render_preview.py` and `spec.md` under `.work\models\Farm_Processing\<ID>_<Name>\`, plus its preview PNG in `art\Farm_Processing\Previews\`. Copy its structure; reuse `_common\processing_common.py` (import it read-only).

## Small tools (TOL-*): extra conventions
- The anchor for tools is `.work\models\Farm_Processing\TOL_Tools\build_tools.py` + `spec.md` + previews `FMS_Workshop_TOL_01..05_Preview.png` (built by the lead). It has proven helpers: `shell()` (n-gon solid of revolution with real through-holes via bmesh `triangle_fill` hole loops + tubes), `fill()`, `path_sweep()` (mitred loop handles), `bolt()`, `oct_rod()`, `rest_on_ground()`, `center_on_ground()`, plus a registry-driven `render()` / `verify()`. COPY the helpers you need into your own script. Do not import that file (it builds on import) and do not edit it.
- Tools have no moving parts: root empty `FMS_Workshop_TOL_XX` + one child `_Body`. Pivot at the ground centre of the bbox, min z = 0, front −Y.
- Long tools lie on the table (long axis along Y, handle toward +Y). Containers stand upright.
- Real holes and lattices cost tris. Stay near the budget; up to about 2x is acceptable if the holes or lattice are the reference's signature feature, and you must document it.

## Products (PRD-*): extra conventions
- Anchors: `TOL_Tools\build_tools.py` builders `build_cheese_mold` (PRD-01) and `build_cut_wheel` (PRD-02), plus helpers `shell()`, `blind()`, `fill()`, `flat_plate()`, and per-item palette overrides (`REG[...]['pal']`). Copy what you need; don't import it.
- A product is ONE prop, usually its container plus the food. The food is chunky, faceted and readable at 128 px: a few large lumps, not hundreds of tiny pieces. Lumps are half-sunk into a base surface, so nothing floats. No noise textures.
- Food colours are your own palette cells (per-item atlas); keep cells 0–9 like the pack.

## Lessons from the previous Codex rounds (the lead rejects these)
- Coplanar overlapping faces show as dotted/sawtooth seams (z-fighting). Parts that touch must share edges or be offset by at least 1 mm; never two faces in the same plane.
- A lattice, mesh or perforation must cover the whole area the reference shows, edge to edge, ending in a rim. No ragged partial patches.
- The reference's signature feature (a spout, collar, holes, tied knot) must be clearly readable in the preview. If it reads as a flat panel, the round failed.
- Collars and sleeves are SOLID around their axis (no visible hollow), and they sit flush against what they attach to.

## Hard rules
- Blender: headless only, `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python <script> -- <args>`, with env `PYTHONUTF8=1`. Do NOT use any Blender MCP or the user's open Blender. No AI 3D generation, no downloads.
- Four other workers build other models at the same time in the same worktree. Edit ONLY your own folder `.work\models\Farm_Processing\<ID>_<Name>\` and your own output files `art\Farm_Processing\{Meshes,Textures,Previews,Blend}\FMS_Workshop_<ID_>*`. Never edit `_common\`, other models' folders or exports, PLAN files or `Assets\`. No git commits, no git stash, no branch changes.
- Your check renders go to `%TEMP%\FarmProcessing_check\<ID>\` and are deleted at the end. `art\` gets exactly one preview PNG.
- Python heredocs with triple quotes break shells: write scripts to files and run them.

## Style (the lead rejects work that breaks these)
- Bold chunky primitives, chamfered edges, faceted flat shading, 8–16 segments on round forms. No noise or speckle textures, no grid/checker textures, no thin spindly parts, no floating parts, no pole fans, no icosphere blobs.
- Flat palette atlas (256 px 4x4, padding), one material. Wood is the pack wood #B5835A with dark #7A5233 for shaded and secondary members. Don't make every wooden part the same flat orange; use the light/dark pair the way the approved models do. Red caps #C8473B, metal #8E959B (light/dark pair), cream #F2E6C9, stone #A7A39A, brick #D0583F with light mortar.
- Parts that touch really touch: containers rest ON their supports, legs on Z=0, no gaps, no interpenetration visible from outside.
- Measure proportions from the reference in pixels and convert to metres (the catalogue size is a guide; the reference wins, but document deviations).
- Give numbers to yourself: write key dimensions in spec.md before building, then check them in the printed output.

## Quality loop (mandatory, ≥ 3 rounds, ≤ 5)
Each round: render at the reference's camera angle (three-quarter, about 20–30° elevation, 70 mm lens), make a side-by-side sheet (reference | your render) and LOOK at it (open the PNG), write the 2–3 worst differences in spec.md, fix them in the script. Also check a 128 px thumbnail. Stop when only nitpicks remain.

## Done = worker_done with evidence
Report: output file paths; tris per part and total vs the budget; size in m; pivots; the check results printed by the script (non-manifold/loose/degenerate = 0, mirror, contacts, SNAP/verify); FBX re-import result (nodes, tris, dims, texture found); rounds and remaining differences; QA verdict SHIP / SHIP WITH NOTES / NO-SHIP. A failed check or a missing export means the Task failed. Say so; don't report it as done.
