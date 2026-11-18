# Task: polish 8 accepted models (minor review notes) in the lead's shared script, TOL/PRD group

First read `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (hard rules, style, lessons) and the review `planning\FarmProcessing\REVIEW_2026-11-14.md`. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

All 8 models are built by ONE script: `.work\models\Farm_Processing\TOL_Tools\build_tools.py` (registry `REG`, one builder function per item). Run `PYTHONUTF8=1 "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build_tools.py -- <ID> build|export`, where ID is e.g. `TOL01`. `build` prints the checks and writes `%TEMP%\FarmProcessing_check\TOL\<ID>_check.png`; `export` writes the FBX, .blend and preview and runs the FBX re-import verify.

- You may edit ONLY the builder functions of the 8 items below (plus their `REG` entries' budget/view if needed). Do not touch other builders, the shared helpers' behaviour, or other items' exports. Another worker will edit the FUR/MOD builders in this file AFTER you finish, so make all your changes and report.
- These models are already accepted. These are small polish notes, so do NOT redesign anything: keep the silhouette, parts, palette and pivots, and change only what is listed. Compare against `planning\FarmProcessing\references\<ID>.png` and the current preview `art\Farm_Processing\Previews\FMS_Workshop_<ID_>_Preview.png`.
- After each item: `build`, look at the check render next to the reference, then `export`. Checks must stay clean (non-manifold/loose/degenerate 0, no gaps, min z 0).

| ID | Builder | Note | Target |
|---|---|---|---|
| TOL-01 | `build_mold` | Handles too small vs the ref (the ref has big grey loops) | Loops reach about 5.5 cm out from the wall, section about 1.4 cm, bolt plate about 4.5 × 6 cm |
| TOL-03 | `build_spatula` | Blade too light; the grip end is thin | Blade top a mid/dark brown (use WOOD_M top, WOOD_D sides), grip end bulb radius about 2.4 cm |
| TOL-12 | `build_bowl` | Red stripe narrower than the ref | Stripe about 3 cm tall on the lower-middle wall (move/widen the RED band in `prof`) |
| TOL-13 | `build_peel` | Shaft thin, head small vs the ref | Shaft section about 4.4 × 3.6 cm, head about 0.34 wide × 0.32 long (keep the total length 1.4 m) |
| TOL-16 | `build_tongs` | Jaws too narrow (the ref has broad flat paddles) | Each jaw about 5 cm wide at the tip, 1.6 cm thick |
| TOL-17 | `build_comb` | Cells too big and sparse (the ref is a dense comb with thin walls) | Cell radius about 1.9 cm, cell walls about 4 mm, fill the panel edge to edge (about 40+ cells per face); budget up to about 2200 tris |
| TOL-18 | `build_strainer` | Tripod legs thinner than the ref | Legs about 4.6 cm square, leg heads and ring about 1.3× thicker, stretchers about 3 cm |
| PRD-18 | `build_honey_crock` | Crock less bulbous, dipper smaller | Belly apothem about 1.12× (widest at about 45% height), dipper head about 1.25× (discs and handle) |

Report with worker_done: per item tris before → after, what changed, verdict; plus confirmation that only these 8 builders were edited.
