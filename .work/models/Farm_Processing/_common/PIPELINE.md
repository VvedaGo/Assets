# Farm Processing — model pipeline (shared brief for model-artist agents)

Root: `C:\Users\Sergv\orca\workspaces\VFX\master-2` (git worktree). No git commits, never touch Unity `Assets/`.

## Inputs
- Reference: `planning\FarmProcessing\references\<ID>.png` (read it first, write a feature list).
- Catalogue row: `planning\FarmProcessing\MODEL_CATALOG.csv` (size X/Z/Y = width/depth/height in m, LOD0 tris budget, separate moving parts).
- Pack visual standard: `FARM_PROCESSING_PACK.md` section 5.
- Palette: wood #B5835A / #7A5233, cream #F2E6C9, muted red #C8473B, green #6E9F4A, blue #4A78A8, metal #8E959B, stone #A7A39A, copper accent #B87945.
- Approved models (the style bar and code to copy):
  - STA-02 cheese press: `.work\models\Farm_Processing\STA02_CheesePress\` + `art\Farm_Processing\Previews\FMS_Workshop_STA_02_Preview.png`
  - STA-05 juice press: `.work\models\Farm_Processing\STA05_JuicePress\` (build_juice_press.py, render_preview.py, spec.md) + its preview.
  - Shared helpers: `.work\models\Farm_Processing\_common\processing_common.py` (Part, ngon, chamf_rect, sweep, zprism, rect_prism, chamf_spec, atlas/material, comp_checks, to_object, export, verify, save_lib). Use `rect_prism` for chamfered boxes (`inset()` flips corners when inset > corner chamfer).
  - **Read-only for you**: other agents run in parallel. Do NOT edit processing_common.py or any other model's folder/exports. If you need a new helper, put it in your own build script.

## Blender: headless, NOT the live MCP
Several agents build at the same time, so do not use the blender MCP (the user's open Blender). Run:
`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --python <script> -- <args>`
Use `PYTHONUTF8=1`. The STA-05 scripts were written for MCP exec (they create a scene `<ASSET>_Build`); adapt them so build + checks + export + verify + preview run in one headless call (factory startup = empty scene, so the build scene can simply be the default scene after deleting its objects). To see results, render PNGs and Read them.

## Output
- Folder `.work\models\Farm_Processing\<ID>_<Name>\`: one idempotent `build_<name>.py`, `render_preview.py`, `spec.md` (feature list, material class, NOT-modelled list, anchors, deviations from catalogue, compare rounds, remaining diffs).
- Material: own atlas `T_FarmProcessing_<IDnodash>_BaseColor.png` (256 px, 4x4, padding) + `M_FarmProcessing_<IDnodash>`; keep cells 0–12 the same layout as STA-05 where colours match, so atlases can merge later. No noise textures.
- Hierarchy: root `FMS_Workshop_<ID_>` (pivot ground centre, base Z=0, front facing -Y, identity transform), static parts in `_Frame`/`_Body`, each moving part a separate child with its pivot on the hinge/axis.
- Checks printed by the script: tris per part + total vs budget, non-manifold/loose/degenerate = 0, mirror symmetry where the ref is symmetric, contacts (no floating parts, no gaps), dimensions.
- Export: `art\Farm_Processing\Meshes\FMS_Workshop_<ID_>.fbx` (+ `.fbm\` texture copy, like STA-05), texture also in `art\Farm_Processing\Textures\`. Re-import verify (nodes, tris, dims, texture found).
- Preview: exactly ONE `art\Farm_Processing\Previews\FMS_Workshop_<ID_>_Preview.png` (1280x800, #c7ccd3, three-quarter front-left like the ref, no text; tall models fit by height 88%, wide models by width ~68–80%). Check/compare renders go to `%TEMP%\FarmProcessing_check\<ID>\` and are deleted at the end.
- `.blend` copy of only the asset: `art\Farm_Processing\Blend\FMS_Workshop_<ID_>.blend`.

## Quality loop
Economy mode for props ≤ ~2000 tris (max 3 compare rounds), up to 5 for stations > 2000 tris. Each round: render at the reference angle, put it next to the reference, name the 2–3 worst differences, fix in the script. Also judge a 128 px thumbnail. Section 11 house style of skill `blender-unity-assets`: bold faceted shapes, chamfers, no noise, no floating parts, no pole fans. Final QA verdict SHIP / SHIP WITH NOTES / NO-SHIP.

## Lessons from lead reviews (check these before your first render)
- Containers (pots, vats, basins, kettles) REST ON their support: the vessel's bottom sits on the stand/hearth top surface; no rail wrapping the vessel at mid-height, no vessel sinking into the frame.
- Barrels/staved bodies: staves are straight lines from bottom radius to top radius (monotonic taper as in the ref), hoops are bands a constant ~12–15 mm proud. No bulges between hoops.
- Handles are chunky: round loops 3–4 cm thick with bolt bosses, not thin flat frames. Paddles/stirrers chunky too (handle ~4–5 cm).
- Preview camera: match the reference elevation (usually ~20–30° above horizontal, not steeply top-down); a 70 mm lens matches the refs' low perspective better than 50 mm.
- Measure positions (hoop heights, part heights) from the reference image in pixels → metres, rather than guessing.
- FBX exporter bug (Blender 5.2, `bake_space_transform=True`): a SECOND-level child (e.g. a crank parented under a moving stone) gets a wrong transform. Keep moving parts as direct children of the root where possible; if nesting is needed, copy the export-time matrix fix from `STA06_HandMill\build_hand_mill.py` and verify the nested node's translation after re-import.
- Wall modules (MOD-*): contract in `MOD04_WallWindow\spec.md` (exact 2.0×0.18×2.4 box, 0.10 m half-posts at both ends, fixed plinth/beam heights, `SNAP OK`).

## Report (≤ 12 lines)
Files, tris total + per part vs budget, size, pivots, material, rounds + remaining diffs, verdict, unverified items (Unity import), time spent.
