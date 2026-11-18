# Task: build TOL-10 "Cheese board" (FMS_Workshop_TOL_10)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Small tools") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\TOL-10.png`
- Catalogue: "single thick rectangular cheese cutting board with a short handle and no food"; size 0.45 (X) / 0.28 (depth) / 0.04 (height) m; LOD0 80–180 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\TOL10_CheeseBoard\`.
- Closest anchors: TOL-03 paddle (`TOL_Tools`), for a flat outline with a through-hole via `fill()` (top/bottom fills with a hole loop + side walls + hole tube); MOD-04 for the red caps and bolts.

## What the reference shows (measure it yourself)
- Lying flat. The board's long axis is along X, with the handle on +X (the catalogue X = 0.45 includes the handle).
- Board: a thick slab (about 4 cm) with chamfered corners, a darker wood frame border (#B5835A / #9C6B44 sides), and an inset top of 3 lighter planks (#E8CFA6-ish; use CREAM_D #DCC9A0 or a light wood cell) running along X, separated by 2 thin grooves. The planks sit about 3–4 mm below the frame top.
- Handle: a paddle that narrows from the board end into a short neck, then a rounded-hexagonal end with a real HEXAGONAL THROUGH-HOLE (about 3.5 cm), the same thickness as the frame or slightly thinner.
- Four red metal corner straps (#C8473B) wrapping over the long edges near the corners: each is a thin strap on top that bends down over the edge, with one grey hex bolt on its side face.
- Budget 180 is tight. Grooves can be simple inset steps between plank faces. Up to about 300 tris is acceptable if documented.
