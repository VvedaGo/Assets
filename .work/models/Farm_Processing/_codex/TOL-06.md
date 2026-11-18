# Task: build TOL-06 "Measuring jug" (FMS_Workshop_TOL_06)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (including "Small tools") and the files it lists. Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\TOL-06.png`
- Catalogue: "single opaque cream enamel measuring jug with a spout and handle, no writing or transparent glass"; size 0.25 (X) / 0.2 (depth) / 0.3 (height) m; LOD0 200–450 tris; no moving parts.
- Your folder: `.work\models\Farm_Processing\TOL06_MeasuringJug\` (build_measuring_jug.py, render_preview.py or a render function, spec.md).
- Closest anchors: TOL-05 ladle and TOL-04 colander (`TOL_Tools`, for the `shell()` bowl, rim and bolts); STA-03 (rounded handle sweep).

## What the reference shows (measure it yourself)
- Body: a 12-gon tapered cup, wider at the bottom (bottom apothem about 1.25x the top), straight sides, cream enamel (#F2E6C9 light/dark pair). A grey-beige base band about 12% of the height, slightly proud, with a chamfered bottom edge.
- Real wall thickness, open top, inner floor visible.
- Spout on the −X side (front-left in the ref): the rim outline is pulled out into a V-lip, and the wall under it slopes out. Build it by moving the top-ring vertices of 2–3 facets outward and up (not a separate stuck-on cone). The inside must stay a clean surface.
- A grey metal rim band follows the whole top outline including the spout (about 1.2 cm tall, proud about 4 mm, chamfered).
- Handle on +X: a chunky red square-section D-handle (about 2.4 cm section, chamfered bends) attached at two grey chamfered plates (upper just below the rim, lower at about 35% height), each plate with a red hex bolt.
- Mirror symmetry: in Y only (the spout and handle break X symmetry, so skip the X-mirror check or mirror in Y and document it).
