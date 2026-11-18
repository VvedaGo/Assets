# Task: build PRD-11 "Dough in a bowl" (FMS_Workshop_PRD_11)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-11.png`
- Catalogue: "single ceramic mixing bowl holding one large risen bread dough mound"; size 0.35 (X) / 0.35 (depth) / 0.2 (height) m; LOD0 250–550 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD11_DoughBowl\`.
- Anchor: TOL-12 ceramic bowl (`TOL_Tools\build_tools.py`, `build_bowl`, preview `FMS_Workshop_TOL_12_Preview.png`). PRD-11 is a DIFFERENT bowl shape (deeper, steeper, with a wider red stripe), so do not copy TOL-12's profile. Build your own `shell()` profile from the ref.

## What the reference shows (measure it yourself)
- Bowl: a 16-sided cream ceramic (#EADAB4 light / #D8C49A shade) deep bowl, with steep sides flaring out to the rim. A thick flat rim (about 1.8 cm wide). A small foot ring (about 2.5 cm tall, about 55% of the rim width). A wide RED stripe band (#C8473B, about 3.5 cm tall) at about 45% of the bowl height. Real wall thickness.
- Dough: one large risen mound that fills the bowl and domes ABOVE the rim by about 4–5 cm. It is a faceted dome with irregular polygonal planes (a "Voronoi-ish" low-poly look: build it as a subdivided dome with vertex jitter of about 4 mm and 16 x 4 rings, NOT smooth). Its colour is a warm pale dough (#F1D9A8 light / #E2C48E shade). The dome's lower edge tucks INTO the inner wall about 1.5 cm below the rim, so there is no gap and no coplanar overlap.
- Budget at or under 550.
