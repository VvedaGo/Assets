# Task: build PRD-04 "Curd in a cloth bundle" (FMS_Workshop_PRD_04)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-04.png`
- Catalogue: "single cloth-lined curd bundle with an open top showing simple white curds"; size 0.25 (X) / 0.25 (depth) / 0.18 (height) m; LOD0 250–600 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD04_CurdBundle\`.
- Closest anchors: TOL-12 bowl / TOL-01 mold (`TOL_Tools`) for the `shell()` revolution body.

## What the reference shows (measure it yourself)
- A cream cloth sack (#EAD6AE light / #D9C08F shade): a wide round belly (widest about 35% up), pinched at a neck at about 60% height where a RED band ties it (a band about 2.5 cm tall, proud about 6 mm). Above the tie the cloth flares out again into an OPEN, irregular ruffled rim (8–10 soft points/folds around, slight up-and-down variation), with real thickness, and the inside is visible.
- The belly is faceted (12–16 sides). Give it gentle vertical folds: alternate ring vertices in/out by about 4–6 mm. These are folds, not noise.
- The tie: a red band around the neck, plus a knot block at the front-right and TWO hanging tails (flat strips about 2.5 cm wide that taper to a V-cut end and hang down over the belly). The tails must touch the belly surface; they must not float or cut deep into it.
- Curds: 9–12 chunky white faceted lumps (#F4F1E8 / #E6E1D3), each a low-poly squashed polyhedron about 4–6 cm, half-sunk into a hidden fill disc just below the rim, filling the opening as in the ref. No floating lumps and no tiny bits.
- The bottom is flat on the ground (min z = 0).
