# Task: build STA-11 "Smoking cabinet" (FMS_Workshop_STA_11)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (and the files it lists). Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\STA-11.png`
- Catalogue: "freestanding wooden food smoking cabinet on a brick base, hinged front door, two removable racks and short metal flue"; size 0.9 (X) / 0.8 (depth) / 1.8 (height) m; LOD0 1600–3000 tris; moving parts: door and two racks.
- Your folder: `.work\models\Farm_Processing\STA11_Smoker\` (build_smoker.py, render_preview.py, spec.md).
- Closest approved anchors: STA-07 (`STA07_JamKettle`) for the brick base, the parametric arch and stone slabs; MOD-04 (`MOD04_WallWindow`) for the timber frame members and red caps.

## What the reference shows (measure it yourself)
- Brick base, about 40% of the height: red bricks #D0583F in a running bond with light mortar (real geometry: bricks slightly proud of a mortar core), a grey stone cap slab ring on top, and a small grey firebox door with a stone arch surround at the front. The firebox door is static, part of the body.
- Wooden cabinet ON the base: a box with corner posts (light wood), dark plank walls with vertical board seams, red square caps at the post corners, open front.
- Gable roof: two pitched slabs of 3–4 boards each with overhang, a ridge board, and a cream plank gable front with a red block.
- Metal flue: a grey octagonal pipe on the right roof slope with a hex-bolted collar and a conical cap. It is static.
- Door: a framed plank door (dark frame, cream planks), 2 grey hinges with bolts on the LEFT, a grey D-handle. In the reference it is open about 100°, so keep it open like that in the preview. It is a separate child `_Door` with its pivot on the hinge axis.
- Two racks: light-wood slatted shelves (a frame plus 6–7 slats) resting on side cleats inside the cabinet. They are separate children `_Rack_1` and `_Rack_2`, each with its pivot at its bottom-centre (they slide out along −Y).
- Visible interior: back and side walls inside with board seams, dark-wood tone. The inside must not be empty or see-through.
- Up to 5 compare rounds.
