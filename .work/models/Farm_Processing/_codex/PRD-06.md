# Task: build PRD-06 "Juice in a ceramic pitcher" (FMS_Workshop_PRD_06)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Products" and "Lessons") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\PRD-06.png`
- Catalogue: "single wide-mouth cream ceramic juice pitcher with a simple opaque orange liquid surface"; size 0.25 (X) / 0.25 (depth) / 0.35 (height) m; LOD0 250–500 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\PRD06_JuicePitcher\`.
- Closest anchor: TOL-06 measuring jug (`TOL06_MeasuringJug`, accepted after its spout fix: read its spec for how the V-spout was made) and TOL-12 bowl (`TOL_Tools`, `build_bowl` for the stripe band).

## What the reference shows (measure it yourself)
- A 12-sided cream ceramic body (#F2E6C9 light/dark pair): a bulbous belly (widest at about 40% height), narrowing to a waist at about 65%, then a FLARED wide neck/collar up to the rim. A grey-beige foot band at the bottom (about 7% of the height). A red stripe band (#C8473B, about 2.5 cm) around the widest part of the belly.
- Rim: a thick flat rim with real wall thickness. On −X the rim pulls out into a clear V-SPOUT (the TOL-06 lesson: lip tip about 4 cm beyond the round rim, raised about 1 cm, with the wall under it sloping out).
- Juice: a flat opaque orange surface (#F2921E light, #E07B12 shade ring at the wall) about 4–5 cm below the rim. It is part of the body, meeting the inner wall with a shared edge loop (no coplanar overlap, no gap).
- Handle on +X: a chunky wooden (#C98A55 / #A86F40) octagon-section D-handle (about 3 cm thick) from just under the rim to the belly, with chamfered bends, attached flush.
- Mirror: Y-symmetric only.
