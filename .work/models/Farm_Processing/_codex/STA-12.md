# Task: build STA-12 "Hand honey extractor" (FMS_Workshop_STA_12)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (and the files it lists). Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\STA-12.png`
- Catalogue: "small hand-cranked cylindrical honey extractor on three legs, removable opaque lid, simple internal basket and bottom honey tap"; size 0.8 (X) / 0.8 (depth) / 1.2 (height) m; LOD0 1600–3200 tris; moving parts: lid, crank, basket.
- Your folder: `.work\models\Farm_Processing\STA12_HoneyExtractor\` (build_honey_extractor.py, render_preview.py, spec.md).
- Closest approved anchors: STA-06 (`STA06_HandMill`) for the round stand legs with red caps and its crank; STA-04 (`STA04_FruitCrusher`) for the Z-kink crank and hub.

## What the reference shows (measure it yourself)
- The reference has FOUR legs, not three. Follow the reference and note the catalogue deviation in spec.md. They are chunky splayed wooden legs with chamfered heads and red caps, joined by low stretchers into a square/cross frame.
- Drum: a grey metal cylinder (12–16 segments, light/dark metal pair), with a raised band/rim at the top and a band at the bottom. The drum's bottom rests ON the leg heads.
- Lid: a beige-grey (#C9C2B6 family) faceted shallow cone/dome lid with a chamfered rim that overhangs the drum slightly, and a wooden bridge handle (dark wood) on two small light-wood blocks. It is a separate child `_Lid`, pivot at its centre bottom.
- Crank: on the right side, a grey gearbox block mounted on the drum wall, a hex hub, a grey Z-kink arm, and a red octagonal handle. It is a separate child `_Crank` with its pivot on the hub axis (horizontal axis through the gearbox).
- Honey tap at the bottom front: a grey valve body with a hex nut, a red lever, and a square open spout pointing down.
- Basket: a simple internal frame (vertical axle + 2–4 rectangular mesh-frame panels) inside the drum, hidden while the lid is on. It is a separate child `_Basket` with its pivot on the drum axis. Keep it cheap (≤ 300 tris) and make sure it doesn't poke through the drum.
- Hierarchy: `_Body` (legs + drum + tap), `_Lid`, `_Crank`, `_Basket`. All are direct children of the root (see the nested-child FBX bug note in PIPELINE.md).
- Up to 5 compare rounds.
