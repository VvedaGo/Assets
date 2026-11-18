# Task: build PRD-09 "Bunch of dried herbs" (FMS_Workshop_PRD_09)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-09.png`
- Catalogue: "single tied bunch of dried culinary herbs hanging stem-up, simple clustered leaves"; size 0.2 (X) / 0.15 (depth) / 0.4 (height) m; LOD0 200–500 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD09_HerbBunch\`.
- Leaf technique reference: the Farm Nature pack solved leaves without spikes or floating strips. Read the leaf helpers (`serrated_blade`, `heart_leaf`, `star`, the leaf placement in `Plants/build_plants.py`) in `C:\Users\Sergv\orca\workspaces\VFX\ModelGenerator\.work\models\Farm_Nature\_common\nature_common.py`, read-only. Use broad, faceted, slightly folded leaves (a 2-sided double fan with a centre crease), not flat cards.

## What the reference shows (measure it yourself)
- Hanging stem-up: the stem ends at the TOP, the leaves hang DOWN. Pivot at the top centre of the stem bundle (the hang point). Set min z = 0 at the leaf tips, and document the hang-point height in spec.md.
- Stems: 8–9 thick octagonal stalks (about 1.2–2 cm), in three wood tones (#B5835A / #9C6B44 / #7A5233), gathered in a bundle with slightly different lengths and flat-cut tops.
- Tie: a red cloth band (#C8473B), 2 wraps, with a knot and two short tails hanging on the front.
- Below the tie the stems fan out into a teardrop-shaped cluster: about 28–36 sage-green leaves (#8E956A light / #6F7552 dark), elongated ovals about 6–8 cm, each with a centre fold. They grow from thin twigs that branch off the stems, overlap, and point mostly downward and outward. The cluster is widest at about 35% height and narrows to a point at the bottom.
- 3 small clusters of 3 pale cream seed pods (#E8D6A8, faceted balls about 1.8 cm) at the twig tips, as in the ref.
- Front-facing like the ref, but give it depth too (leaves in front and behind the stems), so the side view isn't a flat card.
- Budget about 500; up to about 650 is OK if the leaves need it (document it).
