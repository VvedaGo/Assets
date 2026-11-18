# Task: build PRD-03 "Butter block on a board" (FMS_Workshop_PRD_03)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Small tools", "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-03.png`
- Catalogue: "single rectangular butter block on a small dedicated wooden butter board"; size 0.22 (X) / 0.16 (depth) / 0.08 (height) m; LOD0 120–300 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD03_ButterBoard\`.
- Duplicate check done by the lead: Farm Market has a separate cutting board but no butter. This item is the butter-on-board combo, so do not copy any Market file.

## What the reference shows (measure it yourself)
- Board: a thick (about 2.2 cm) wooden board with chamfered corners, wood #B5835A top and #7A5233/#9C6B44 sides. A short paddle handle on +X narrows into a rounded-hex end with a real HEXAGONAL THROUGH-HOLE (copy the approach from TOL-10 cheese board: `TOL10_CheeseBoard`, and avoid its first-round z-fighting mistake). The catalogue X 0.22 is the board without the handle; with the handle about 0.30 is fine if the ref proportions need it (document it).
- Butter: one block about 0.15 x 0.08 x 0.065 m, a pale butter yellow (#F3E3B5 top, #E8D3A0 sides; add 2 cells), with big chamfers on all edges (chamfer about 1.2 cm on the top edges, like the ref), sitting ON the board. The block bottom is exactly on the board top, offset 0 or overlapping 1 mm, but never coplanar with the board top face.
- Budget: easily under 300.
