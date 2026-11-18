# Task: build PRD-10 "Open flour sack" (FMS_Workshop_PRD_10)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-10.png` (shape reference)
- Catalogue: "single small open flour sack with rolled cloth rim and a pale flour mound visible inside"; size 0.35 (X) / 0.3 (depth) / 0.45 (height) m; LOD0 250–550 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD10_FlourSack\`.

## DUPLICATE RISK: read this first
Two existing models look similar, and yours must be clearly different from both:
1. Farm Market `Sack_Open` (preview `C:\Users\Sergv\orca\workspaces\VFX\ModelGenerator\art\MarketFarm\Sack_Open_v2_Preview.png`): a TALL straight burlap cylinder with a woven texture and ORANGE grain.
2. Our own PRD-04 curd bundle (`art\Farm_Processing\Previews\FMS_Workshop_PRD_04_Preview.png`): a cream cloth sack with a RED ribbon, a ruffled rim and white lumps.
So, deviating from the ref on purpose: use the ref's SQUAT shape and THICK ROLLED CUFF rim, but make the cloth a darker sackcloth tan (#C9A06A light / #A9824F dark, flat colour, no woven noise), and the tie a brown twine cord (#7A5233, round section about 1.4 cm, 2 wraps) with a simple knot and two short frayed-end tails instead of the red ribbon. The flour is white (#F6F2EA light / #E4DDCD shade).

## Shape (from the ref, measure it yourself)
- Body: 12-sided, a wide flat-bottomed base (bottom apothem about 0.95 of the widest), widest at about 25% height, tapering up to a pinched neck at about 55% height where the twine sits. The body is faceted with gentle vertical folds (alternate ring verts ±4 mm).
- Rolled cuff above the neck: a fat torus-like roll (section about 6 cm tall, 4 cm thick, 12 segments around, 5–6 sided section) whose outer diameter is about 1.1x the neck. It sits ON the neck cloth and is joined to it, with no gap.
- Flour: a faceted mound inside the cuff with a raised irregular peak (5–8 big planes), the top about 3 cm above the cuff's inner edge, filling the opening edge to edge.
- Budget at or under 550.
