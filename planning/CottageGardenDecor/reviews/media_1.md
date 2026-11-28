# Review media_1 (Э12 media acceptance, 2026-11-26)

Checked: exact pixel sizes of all 16 PNG in `AssetStore/CottageGardenDecor/Media/final/`; Card 1260 and 420 px, Icon 160 / 60 px (downscaled and viewed); all galleries at 100 %; texts against the Media section of PACKAGE_METADATA.md; labels of 06/06b/11 against `*_labels.json`; atlas swatches against `Assets/CottageGardenDecor/Art/Textures/FMS_Garden_Atlas{A,F}.png` (both 256x256, 16 colours = the 4x4 swatches shown, real); plate colours by pixel (#20242A, #C8473B correct); series comparison with Farm Machinery Card/Cover (same plate/accent/3D badge system, same title style).

Sizes: all as required (160, 1024, 420x280, 1260x840, 1950x1300, 1200x630, 1920x1080). No generation artefacts, no pink materials, no UI/watermarks, no non-pack objects except island/lawn/path/sky/clouds/plinths (labelled as demo-only on 07, 10, 12). Logo slot is empty on Card and Cover (title starts at x=150 of 1260 / x=235 of 1950): acceptable, noted.

| File | Verdict | Note |
|---|---|---|
| 01_Icon 160 + 1024 | ✅ | Arch + roses clear at 160 px; at 60 px arch, gate and red badge still read. |
| 02_Card 420 + 1260 | ✅ | Title and accent readable at 420x280, text = metadata (`COTTAGE GARDEN DECOR`, `42 MODELS + 6 COMPOSITIONS`), plate 35.2 % (lower bound of 35-40 %), arch/garland fully above the plate. |
| 03_Cover | ✅ | Plate 22 %, gazebo and island fully visible above it, text = metadata. |
| 04_Social | ✅ | Clean, no text, gazebo apex inside, centre crop OK. |
| 05_Hero | ✅ | Plate 9.7 %, over bare sky/island edge, no item covered. |
| 06_FullCollection | 🔴 | See FIX 1. |
| 06b_FullCollection | 🟡 | All 15 labels match items and the map. Minor: BALL STANDARD and SHEPHERD'S HOOK are set smaller than the other labels (FIX 4); render seam (FIX 5). |
| 07_Closeups | ✅ | Captions = metadata, demo-only footnote present, no key item cut (background items in the small panels are cropped, acceptable). |
| 08_VariantsAndModules | 🔴 | See FIX 2. |
| 09_Technical | 🟡 | Numbers all equal the card (2,314 / 1,156 / 1,996 / 76-80-36 / 26,918 / 36-2,722 / LOD1 9 / no colliders). Only seam (FIX 5). |
| 10_DemoAndVersion | ✅ | Text block = metadata, demo-only footnote, nothing covered. |
| 11_CategoryDetails | 🟡 | 7 STR + 5 FUR, all labels match the map. Only seam (FIX 5). |
| 12_Compositions | ✅ | Six vignettes, labels and counts = metadata. |
| 13_Materials | 🟡 | Real atlases. Seam visible here (8 levels, FIX 5); swatch captions are small (FIX 6). |
| 14_UnityAndComparison | ❓ | Pending the owner's screenshot. |

Counts: ✅ 8, 🟡 4, 🔴 2, ❓ 1 (file groups: 16 files + 14 pending).

## FIX list (for Codex; edit `build_media.py`, never the raws)

**FIX 1 - 06_FullCollection (🔴).** (a) The render is shrunk to ~70 % of the canvas (panel x 285-1634, y 10-880) because a two-line legend sits under it; the smallest items (gnome ~12 px, edging, hooks, pond tiles) are tiny and side margins are 15 %. Put the render at full width (0-1920 x 0-1080, as in the raw) and move the legend to ONE line (or drop line 2 into the plate line) in the empty floor at the bottom right (x > 1000, y > 1000, raw is empty there); keep the plate bottom left (raw floor under x < 590, y > 950 is empty). (b) Label `STRUCTURES 7` is at x 747 / y 312, i.e. nearer the fountain row than the structures (union rect of STR is centred at x ~980 in raw) and reads as a label of WTR. Centre it under the STR rect (x of the union centre, y just under the row, ahead of the pergola legs) or place it left of the row as a heading with a thin rule; check that it is closer to the STR row than to any other row. (c) `TOPIARY 4` (y 877) touches the legend line (y 899): after (a) leave >= 25 px between any label and the legend.
**FIX 2 - 08_VariantsAndModules (🔴).** Labels collide: `TOPIARY: BALL · ROSE STANDARD` touches `URN: EMPTY · PLANTED` (no gap at x ~648); `CLIMBING ROSE: RED · PINK` touches `HOLLYHOCK: PINK · WHITE` (x ~428); `HOOK: BASKET · BIRD FEEDER` ends 2 px from the panel edge. Variants are shown at ~60 px per item while labels are larger than the items; the modules panel on the right is half empty (y 80-260 and 760-950 free). Rebalance: make the two variant panels wider/taller (e.g. panels 1050 x 400 each, using the free vertical space; modules panel narrower or vertically centred and larger), keep one caption per group with >= 20 px gap between neighbouring captions (stagger on two heights or shorten the text to the `ARCH: WOOD · WHITE · GATE` form only if the card text is changed too - otherwise keep the exact card text and widen the panel).
**FIX 3 - (info, no change).** Card plate is exactly at 35.2 %; if the Card is re-rendered keep >= 35 %.
**FIX 4 - 06b label size (🟡).** `BALL STANDARD` and `SHEPHERD'S HOOK` are auto-shrunk to a smaller size than the other labels; use one font size for all labels of the frame (reduce the size of all, or allow a two-line label for these two).
**FIX 5 - render seam (🟡; 06, 06b, 09, 11, 13).** The raw floor (e.g. 236,234,237 in 06; 238,237,240 in 09; 241,239,242 in 13) is lighter than the layout background (233,233,236 = #E9E9EC), so a lighter rectangle with hard edges is visible around the render. Either feather the render edges into the background (20-40 px gradient mask) or tone-match the panel to #E9E9EC (multiply by the per-frame mean ratio) without touching the rendered content inside.
**FIX 6 - 13_Materials captions (🟡).** `ATLAS A · STRUCTURES & FURNITURE` / `ATLAS F · PLANTS & BEDS` are ~14 px high: raise to the size of the model labels (>= 18 px).

## For the owner / Э12 closure
14_UnityAndComparison: manual Editor screenshot still required (Project on Art/Prefabs/STR, `FMS_Garden_Gazebo` selected, Inspector with LOD Group). Gallery file sizes are 0.55-1.36 MB against a 300-500 KB guideline; recorded by the assembler, not a blocker.

## Pass 2 (2026-11-26)

Viewed at 100 % and 50 %: 06, 06b, 08, 09, 11, 13, 14. The seam is now feathered (floor at the edges equals #E9E9EC), so FIX 5 is closed. FIX 4 (06b label size) and FIX 6 (13 captions, now two-line and larger) closed. FIX 2 closed: no touching captions in 08, the panels are larger. FIX 1 mostly closed: render is full-frame, `STRUCTURES 7` has a rule line to its row, `TOPIARY 4` no longer touches the legend.
- 06_FullCollection 🟡: `ORNAMENTS 5` sits 6 px from the right edge of the plate (x 600 vs plate end 594); the one-line legend at the bottom right is ~13 px high and unreadable at 50 %. Optional: shift `ORNAMENTS 5` +30 px right (or up 20 px) and raise the legend to >= 16 px (it can wrap onto two lines at x > 620). Not a blocker.
- 08: ✅ (modules panel keeps empty white bands above/below the render with tags in them; acceptable).
- 14_UnityAndComparison 🟡: the capture is this project's Editor only (Scene, Project at Assets > CottageGardenDecor > Art > Prefabs > STR, Hierarchy `Demo_Catalog`, Inspector `FMS_Garden_Gazebo`); no other apps, paths outside `Assets/`, user names or secrets visible. UI text is small (~14 px) but the callouts carry the message. Callouts: `LOD GROUP: 2,314 / 1,156 TRIS` brackets the real LOD0 2314 / LOD1 1156 rows; `PIVOT ON THE GROUND · 1 UNIT = 1 M` brackets Transform (0,0,0 / scale 1); texts and `PACKAGE STRUCTURE` block = the card's 14 row exactly. Weak point: the `ONE MATERIAL: FMS_Garden_AtlasA` arrow points at the prefab row in Project; the material itself is not visible anywhere in the capture (Inspector is cut above the Materials). Optional FIX 7: point that callout at an element that shows the material (scroll the Inspector to the renderer/material or capture with `FMS_Garden_AtlasA` selected in Project and a second small inset) or accept as is. Minor: the Inspector shows "Active LOD bias is 2,0" warning and floor ID labels in the scene view are mirrored; harmless.

## Final table (17 files)

| File | Verdict |
|---|---|
| 01_Icon (160) | ✅ |
| 01_Icon_1024 (master) | ✅ |
| 02_Card (420x280) | ✅ |
| 02_Card_1260x840 (master) | ✅ |
| 03_Cover | ✅ |
| 04_Social | ✅ |
| 05_Hero | ✅ |
| 06_FullCollection | 🟡 (optional label/legend tweak) |
| 06b_FullCollection | ✅ |
| 07_Closeups | ✅ |
| 08_VariantsAndModules | ✅ |
| 09_Technical | ✅ |
| 10_DemoAndVersion | ✅ |
| 11_CategoryDetails | ✅ |
| 12_Compositions | ✅ |
| 13_Materials | ✅ |
| 14_UnityAndComparison | 🟡 (material callout points at a prefab row) |

Counts: ✅ 15, 🟡 2, 🔴 0, ❓ 0. The set can be accepted; the two 🟡 are optional. Owner screenshot not needed.
