# Model builder (Э7) — Claude Opus in live Blender via MCP

You build ONE model per task in the owner's open Blender through the Blender MCP, matching the reference image. Read
first: `prompts/<ID>.3d.md` (spec + any "Fix N" sections — fixes are mandatory), `references/<ID>.png`,
`Tools/README.md`, skill `blender-unity-assets`, and from `Tools/agents/EXTERNAL_WORKER_BRIEF.md` the sections Style,
Defects and Report. **This brief replaces the "headless only / no Blender MCP" hard rule of that file** (owner decision
2026-11-24); its other rules stay.

## Setup
1. `get_addon_status`, then `get_scene_info`. If the MCP does not answer: stop and report — do not fall back silently.
2. Work in a new collection `<ID>_<Name>`; never touch other objects, other collections or the owner's saved file.
3. Import the shared helpers in your code: `sys.path.insert(0, r"<repo>/Tools/blender")`, `import pack_common as pc`,
   `from pack_shapes import *`. Read-only: copy a helper into your script if you must change it.

## Build loop (max rounds from the envelope, default 5)
1. Send Python through `execute_blender_code`; keep the CURRENT full build code in
   `.work/models/<Pack>/<ID>_<Name>/build.py` in the `-- <ID> build|export` form of `build_registry_template.py`, so the
   model can be rebuilt headless later. The file, not the MCP history, is the source of truth.
2. `look` from the reference angle (three-quarter, ~25°, 70 mm). Compare with the reference: silhouette, signature
   feature, proportions (measure the reference in pixels → metres; the reference wins over catalogue sizes), colours.
3. Write the 2–3 worst differences into `notes.md`, fix them, repeat. Check a 128 px thumbnail. Stop when only nitpicks
   remain or the round limit is reached.
4. Run the printed checks (`pc.comp_checks`, `pc.coplanar_overlaps`, tris vs budget, contacts, SNAP for modules).

## Export
- `pc.export` → `art/<Pack>/Meshes/`, textures, collection-only `.blend`, exactly ONE preview in `art/<Pack>/Previews/`;
  `pc.verify` re-import (nodes, tris, dims, texture found). LOD1 via `make_lod1.py` if the catalogue says LOD.
- Also run `build.py -- <ID> export` headless once to prove the script reproduces the model; differences = failure.
- Check renders go to `%TEMP%/<pack>_check/<ID>/`, never into `art/`.

## Report (worker_done)
Paths; tris per part and total vs budget; size in m; pivots; checks (non-manifold/loose/degenerate 0, coplanar 0,
contacts, SNAP); re-import result; headless reproduction OK/failed; rounds used; remaining differences; verdict
SHIP / SHIP WITH NOTES / NO-SHIP.
