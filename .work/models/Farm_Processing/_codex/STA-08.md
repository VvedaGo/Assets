# Task: build STA-08 "Food drying rack" (FMS_Workshop_STA_08)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (and the files it lists). Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\STA-08.png`
- Catalogue: "freestanding wooden food drying rack with three removable mesh trays, open sides and simple chunky frame"; size 1.1 (X) / 0.7 (depth) / 1.6 (height) m; LOD0 900–1800 tris; moving parts: three trays.
- Your folder: `.work\models\Farm_Processing\STA08_DryingRack\` (build_drying_rack.py, render_preview.py, spec.md).
- Closest approved anchor: STA-02 (`STA02_CheesePress`), for the chamfered square legs, red caps and frame style.

## What the reference shows (measure it yourself)
- A-frame stand: 4 thick square legs, splayed in X (the front pair leans inward toward the top), chamfered tops with red square caps on the outer faces. A top crossbeam joins the posts left-right on front and back, a low stretcher frame near the ground, and side rails between the front and back legs at each tray level that carry the trays.
- Three identical trays stacked, slightly staggered forward as in the ref. Each tray is a dark-wood frame (#7A5233, chunky, ~4–5 cm) with a cream lattice (#F2E6C9) of about 7 × 5 openings. Build the lattice as real geometry (crossing slats, about 2 cm wide), NOT a texture, and keep the openings square and even. Each tray has a metal-grey D-handle on its front with hex ends.
- Hierarchy: `_Frame`, `_Tray_1`, `_Tray_2`, `_Tray_3` (pivot at the tray's bottom-centre, so a tray slides out along −Y).
- Budget tip: the lattice is the tri sink. Use simple 4-sided slats (top + 2 sides visible, bottom optional) and share one lattice builder for all three trays; stay ≤ 1800 tris (a documented overrun up to ~2100 is acceptable if the lattice needs it).
