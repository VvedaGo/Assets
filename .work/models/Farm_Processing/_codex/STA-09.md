# Task: build STA-09 "Bread oven" (FMS_Workshop_STA_09)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (and the files it lists). Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\STA-09.png`
- Catalogue: "small freestanding rustic brick bread oven with a domed chamber, arched opening, hinged metal door and short chimney"; size 1.5 (X) / 1.4 (depth) / 1.8 (height) m; LOD0 2200–4000 tris; moving part: door.
- Your folder: `.work\models\Farm_Processing\STA09_BreadOven\` (build_bread_oven.py, render_preview.py, spec.md).
- Closest approved anchors: STA-07 (`STA07_JamKettle`): its parametric 5-voussoir arch, brick colours and stone slabs. STA-06 (`STA06_HandMill`): its round stand of chunky legs with red caps.

## What the reference shows (measure it yourself)
- Wooden stand: 4 thick splayed legs with red caps, a rectangular top frame and stretchers. On it sits a ring of grey stone slabs (8–10 chamfered blocks around the dome base), and the dome rests ON that ring.
- A cream plaster dome (#F2E6C9 light/dark pair), faceted low-poly: about 10–12 segments around and 4–5 rings, flat-shaded, with no pole fan at the top (the chimney collar covers the top).
- Front: a raised red-brick arch (#D0583F) of about 9 voussoirs around a rounded-top opening. The arch is thick and protrudes ~6–8 cm from the dome, with radial block sides and equal gaps. Build it from ONE parametric ring, as STA-07 does.
- Door: a grey metal slab with a rounded top filling the opening, two hinges with hex bolts on the LEFT, and a D-handle on the right. It is a separate child `_Door` with its pivot on the hinge axis (vertical, at the left edge), so it swings open.
- Chimney: a red octagonal collar on top of the dome, a grey stone/brick stack (2 courses), and an octagonal grey cap that is hollow on top.
- Hierarchy: `_Body` (stand + stone ring + dome + arch + chimney) and `_Door`.
- Hero-sized station: up to 5 compare rounds.
