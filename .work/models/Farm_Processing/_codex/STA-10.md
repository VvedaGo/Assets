# Task: build STA-10 "Seed oil press" (FMS_Workshop_STA_10)

First read and follow `C:\Users\Sergv\orca\workspaces\VFX\master-2\.work\models\Farm_Processing\_codex\CODEX_COMMON.md` (and the files it lists). Worktree root: `C:\Users\Sergv\orca\workspaces\VFX\master-2`.

- Reference: `planning\FarmProcessing\references\STA-10.png`
- Catalogue: "rustic manual seed oil screw press, wooden frame, small seed hopper, pressing chamber and oil spout, visibly distinct from fruit press"; size 1.0 (X) / 0.8 (depth) / 1.4 (height) m; LOD0 1800–3500 tris; moving parts: screw and handle.
- Your folder: `.work\models\Farm_Processing\STA10_OilPress\` (build_oil_press.py, render_preview.py, spec.md).
- Closest approved anchor: STA-05 (`STA05_JuicePress`), which has the same family of frame, stave chamber, hoops, threaded spindle and T-handle. Reuse its code (import its functions read-only or copy them into your script). Do not edit STA-05 files.

## How it must differ from STA-05 (from the reference)
- An A-frame: two splayed side legs per side meeting the posts, with diagonal braces under the crossbeam, a mid-height platform (thick wooden board) carrying the chamber, a low stretcher frame, and red caps on the joints.
- The pressing chamber is SMALLER and lower than STA-05's basket: about 0.40 m diameter × 0.30 m high, cream staves with 2 grey hoops and hex rivets, sitting ON the platform. Inside it is a grey pressing plate with a hex collar.
- The screw passes through a square grey nut block on top of the crossbeam. The T-handle is a wooden bar with octagonal ends, through a grey hex hub on top of the screw.
- A small grey square hopper (a tapered box) sits on a dark-wood block on the LEFT end of the crossbeam. The seeds inside are NOT modelled; a flat cream fill surface slightly below the rim is fine, no individual seeds.
- Oil spout: a grey open U-channel at the bottom front of the chamber, sloping down forward.
- Hierarchy: `_Frame` (incl. hopper), `_Chamber` (staves, hoops, rivets, spout), `_Plate` (pivot at its centre), `_Screw` (spindle + T-handle, pivot on the spindle axis at the nut). The handle is part of the screw, which matches the catalogue's "screw; handle" because they rotate together.
- Up to 5 compare rounds.
