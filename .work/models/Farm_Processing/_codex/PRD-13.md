# Task: build PRD-13 "Bread rolls on a baking tray" (FMS_Workshop_PRD_13)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-13.png`
- Catalogue: "single flat dark baking tray with three attached small scored bread rolls"; size 0.45 (X) / 0.35 (depth) / 0.12 (height) m; LOD0 300–700 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD13_BreadTray\`.
- Duplicate check by the lead: Farm Market has a Bread_Loaf / Baguette / Croissant (single breads). This item is a tray of 3 joined rolls, so it is distinct. Don't copy anything.

## What the reference shows (measure it yourself)
- Tray: a dark brown-grey metal sheet tray (#6E6560 light / #4E4643 dark) with a low sloped rim (about 2.2 cm), chamfered corners, a flat floor, and real thickness. It is a rectangle about 0.45 x 0.30.
- Rolls: 3 rolls in a row along X that touch and slightly merge (they baked together), sitting on the tray floor. Each is about 0.13 m long x 0.11 deep x 0.075 high: a faceted dome (about 10 sides, 3 rings) with a flat-ish bottom and a pale crumb side (#EFD3A0) under a golden-orange crust top (#E09A55 light / #C97E3D shade). Put the colour split at about 45% height, as in the ref, so the bottom band reads lighter.
- Scoring: 2 diagonal SCORE cuts on top of each roll. Each is a shallow V-groove (about 7 mm deep, about 1.2 cm wide) with pale inner faces (#F3DDB0), cut into the crust geometry. It must be geometry, not a texture, and must not leave coplanar faces.
- The rolls touch each other with a slight overlap (they merge), without z-fighting at the joins (move the neighbours apart if needed or merge them into one mesh loop).
- Budget at or under 700.
