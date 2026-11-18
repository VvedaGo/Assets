# Task: build PRD-17 "Hanging smoked ham" (FMS_Workshop_PRD_17)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-17.png`
- Catalogue: "single smoked ham hanging from an integrated short cord, simple reddish brown meat shape"; size 0.2 (X) / 0.16 (depth) / 0.4 (height) m; LOD0 250–600 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD17_SmokedHam\`.
- Duplicate check by the lead: Farm Market has `Ham` (preview `C:\Users\Sergv\orca\workspaces\VFX\ModelGenerator\art\MarketFarm\Ham_Preview.png`), a lying ham with a bone end. Yours HANGS shank-up on a cord with a smoked golden-brown skin, so it's distinct; don't copy it. Keep the silhouette clearly a hanging leg (a pear/teardrop shape), as in the ref.
- Hanging prop: pivot at the TOP of the cord loop (the hang point). Set min z = 0 at the bottom of the ham, and document the hang-point height in spec.md.

## What the reference shows (measure it yourself)
- Ham: a pear/teardrop shape, a big faceted rounded lower mass (about 0.19 m across, slightly flattened front-to-back, about 0.16 deep) that narrows upward into a SHANK (about 4.5 cm thick) ending in a rounded knob tilted slightly to one side. Skin a smoked golden brown (#D08A55 light / #A9683A dark), with bold flat facets (about 12 around, 6–7 rings), no smooth shading.
- Cut face: the lower front-left side has a flat CUT surface (an irregular polygon about 0.13 m across) showing red meat (#C8473B / #A8372E facets) bordered by a cream fat rim (#EFD7A8, about 1.2 cm wide, slightly raised), as in the ref. The cut is a planar region of the mesh, so build it into the surface, not as a decal on top.
- Cord: cream twine (#EAD6AE / #D2BA8A), 2 tight wraps around the shank under the knob plus a tall loop (about 11 cm) above, with a 6-sided section about 1.2 cm.
- Budget at or under 600.
