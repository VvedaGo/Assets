# Task: polish STA-04 fruit crusher (minor review note)

First read `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md`. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

STA-04 is accepted; this is a small polish. Script: `.work\models\Farm_Processing\STA04_FruitCrusher\build_fruit_crusher.py` (read its spec.md for how it is run and exported). Reference: `planning\FarmProcessing\references\STA-04.png`. Current preview: `art\Farm_Processing\Previews\FMS_Workshop_STA_04_Preview.png`.

Note: the two rollers read as flat beige planks in the housing window. In the ref they read as round rollers.
- Make each roller a clearly round 10–12-sided cylinder that protrudes about 2 cm out of the window front, so the curvature shows.
- Give each roller chamfered ends and a darker hub disc at each end, visible in the window.
- Keep: the separate `_Roller_A/_Roller_B` parts with pivots on their axles, the clearances (they must not intersect the housing, chute or each other), and everything else.
- Budget up to about 2300 tris.

Re-export, re-verify and re-render the same files (one preview only). Report with worker_done: tris before → after, what changed, verdict.
