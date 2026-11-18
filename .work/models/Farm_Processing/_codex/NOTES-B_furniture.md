# Task: polish 9 accepted models (minor review notes): furniture and workshop modules

First read `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (hard rules, style, lessons) and the review `planning\FarmProcessing\REVIEW_2026-11-14.md`. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

Scripts:
- FUR-01/02/06/11/12 and MOD-06/10/12 are built by `.work\models\Farm_Processing\TOL_Tools\build_tools.py`. Run `PYTHONUTF8=1 "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python build_tools.py -- <ID> build|export`, where ID is e.g. `FUR01`.
- MOD-03 is built by `.work\models\Farm_Processing\MOD03_Wall\build_wall_modules.py -- dry|check|export plain 9`. That script also builds MOD-05 (`door`, arched doorway) and reuses MOD-04's script. Do NOT change anything that affects `door` or `window`: no MOD-05/MOD-04 export, and the WALL CONTRACT (`MOD04_WallWindow\spec.md`) must stay exact (SNAP OK). Before and after your change, run `dry door 9` and confirm its tris/bbox are unchanged.

- You may edit ONLY the builders of the 9 items below. Another worker edited the TOL/PRD builders in build_tools.py before you, so do not touch those.
- These models are already accepted. These are small polish notes, so do NOT redesign anything: keep the silhouette, parts, palette, pivots and snap boxes (MOD-06/10 `snapbox` must stay SNAP OK), and change only what is listed. Compare against `planning\FarmProcessing\references\<ID>.png` and the current preview.
- After each item: `build`, look at the check render next to the reference, then `export`. Checks must stay clean.

| ID | Note | Target |
|---|---|---|
| FUR-01 `build_workbench` | Legs thinner than the ref; stone top edges are too regular | Legs 0.10 → 0.13 with head blocks about 0.15; jitter the stone top outline vertices ±8–10 mm in plan, keeping the top face flat and the chamfers |
| FUR-02 `build_bottling_table` | Still a bit thinner than the ref | Legs 0.12 → 0.14, heads about 0.16, low stretchers about 7 cm tall |
| FUR-06 `build_washstand` | The basin hardly shows below the top | Basin body visibly hangs about 20 cm below the top in the preview: make it deeper (bottom about ZT − 0.24), wider at the bottom, and move it about 4 cm toward the front so the front face shows |
| FUR-11 `build_honey_stand` | The tray reads small under the rails | Tray about 0.55 wide × 0.30 deep and about 1.3× deeper, still tilted 8° with the tap at the front |
| FUR-12 `build_pallet` | Slats thinner and feet lower than the ref | Slats about 4 cm thick, feet about 9 cm tall (the total height may become about 0.18 m, document it) |
| MOD-03 (plain wall) | Plinth stones flat | Stronger pillow bevel on the 3 plinth stones (about 1.5× the current bevel inset/depth), no contract change |
| MOD-06 `build_post` (plain) | Grey stone foot hardly visible | Stone foot about 4 cm tall in a lighter grey (#B4AEA5), red band above it unchanged; keep the 0.2 × 0.2 × 2.4 bbox |
| MOD-10 `build_partition` | Posts thinner than the ref | Posts 0.12 → 0.15, feet scaled accordingly; rails still end flat at x = ±1.000 |
| MOD-12 `build_window_shelf` | Board thinner than the ref | Board about 10 cm thick with a 2 cm chamfer, bracket posts about 1.3× wider |

Report with worker_done: per item tris before → after, what changed, verdict; MOD-05 dry-run numbers before/after (must be identical).
