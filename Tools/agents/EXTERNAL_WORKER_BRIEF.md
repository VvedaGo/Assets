# Common brief for model workers (Codex workers or Claude subagents)

Copy this file next to the per-item specs of a pack (e.g. `.work/models/<Pack>/_workers/COMMON.md`), fill the `<…>` fields,
and append one short spec per model (`<ID>.md`: reference path, catalogue line, folder, closest approved anchor, what the
reference shows with NUMBERS). Origin: Farm Processing, where these rules came out of ~40 worker rounds.

You build ONE stylized low-poly 3D model for the Unity Asset Store pack "<Pack>" with a procedural Blender Python script,
matching a reference image. Approved models of the pack are your style bar; yours must look like it belongs with them.

## Read first
1. `<repo>/Tools/README.md` and the pack's pipeline notes `<pack pipeline file>`.
2. `~/.claude/skills/blender-unity-assets/SKILL.md`: axes, naming, checks, export, reference loop, preview, house style, lessons.
3. Your reference image, and the anchor model named in your spec: its build script, `spec.md` and preview.
   Shared helpers: `<repo>/Tools/blender/pack_common.py`, `pack_shapes.py` (import read-only; copy a helper into your script
   if you must change it).

## Hard rules
- Blender headless only: `PYTHONUTF8=1 "<blender.exe>" --background --factory-startup --python <script> -- <args>`.
  No Blender MCP, no AI 3D generation, no downloads.
- Other workers run in the same worktree at the same time. Edit ONLY your folder `<pack work dir>/<ID>_<Name>/` and your own
  outputs `<art dir>/{Meshes,Textures,Previews,Blend}/<Prefix><ID_>*`. Never edit shared helpers, other models, plans or
  Unity `Assets/`. No git commits, stash or branch changes.
- Check renders go to `%TEMP%/<pack>_check/<ID>/`. If deleting them is refused, say so in the report (the lead cleans up).
- Write scripts to files; heredocs with triple quotes break the shell.
- Conflicting numbers in your spec: ask (orchestration `ask`) instead of guessing. Say which constraint you would drop.

## Style (the lead rejects work that breaks these)
- Bold chunky primitives, chamfered edges, faceted flat shading, 8–16 segments on round forms. No noise/speckle/checker
  textures, no thin spindly parts, no floating parts, no pole fans, no icosphere blobs.
- Furniture and frames are CHUNKY: legs/posts about 0.12–0.16 m on furniture, matching the reference. The most common
  rejection was "1.3–1.5x thinner than the reference".
- One flat-palette atlas (256 px 4x4) + one material; light/dark pairs per material, strong contrast between neighbours.
- Parts that touch really touch: containers rest ON their supports (no rail wrapping a pot at mid-height), legs on z = 0.
- Measure the reference in pixels → metres. The reference wins over catalogue sizes; document deviations in `spec.md`.

## Defects seen in previous rounds (check before you report)
- Coplanar overlapping faces → dotted/sawtooth seams. Touching parts share edges or are offset by ≥ 1 mm
  (`pack_common.coplanar_overlaps` must report 0).
- Lattices/meshes/perforations cover the WHOLE area the reference shows, edge to edge, ending in a rim.
- The signature feature (spout, collar, holes, knot, head of a fish) must read in the preview, not as a flat panel.
- Collars and sleeves are solid around their axis and flush with what they attach to.
- Organic shapes: one continuous profile (no separate head stuck on a body); ruffles are SOFT (2 vertices per crest,
  amplitude in cm from the spec), not a spiky crown.
- Staved barrels: straight staves, monotonic taper, hoops proud by a constant 12–15 mm; no bulges between hoops.
- Items on a surface have the surface height, not the floor height.

## Quality loop (≥ 3 rounds, ≤ 5)
Render at the reference camera angle (three-quarter, ~20–30° elevation, 70 mm), make a reference | render sheet, LOOK at it,
write the 2–3 worst differences into `spec.md`, fix them. Check a 128 px thumbnail. Stop when only nitpicks remain.

## Report (worker_done)
Output paths; tris per part and total vs budget; size in m; pivots; printed checks (non-manifold/loose/degenerate 0, mirror,
contacts, coplanar 0, SNAP); FBX re-import (nodes, tris, dims, texture found); rounds and remaining differences;
verdict SHIP / SHIP WITH NOTES / NO-SHIP. A failed check or missing export = the task failed; say so.
