# Review renders_3 (Э11, 2026-11-26): catalogue shots, Card, IconSource

Checked at 100 %, downscaled to 50 % (06, 09), 420x280 (Card), 160 and 60 px (Icon). Look v2 not questioned.

| Shot | Verdict | Reason |
|---|---|---|
| 06_FullCollection | 🟡 | All 42 base items present (STR 7 incl. assembled pergola+bay, WTR 3, FUR 5, FLB 3, PLT 6, MOD 9, ORN 5, TOP 4), same scale, equal gaps, ~#EAE9EC floor, label strip under each row exists. Content x 15-87 % (side margins ~15 %), height 5-90 %: both axes are nearly at limit (row 1 sets the width, 5 rows the height), so it cannot be enlarged without re-packing; margins are acceptable. At 50 % gnome (~10x18 px), edging brick, pond tiles, hooks are tiny - covered by 06_2. Optional: pack row 1 narrower / rows 4-5 wider to use the sides. Not a blocker. |
| 06_FullCollection_2 | 🟡 | PLT 6 + TOP 4 + ORN 5 larger, readable at 50 %. Items overlap in 2D: topiary cone tip touches the rose edging, spiral topiary covers the ivy panel; shadows overlap. Optional: +0.6 m row gap between PLT and TOP rows. Not a blocker. |
| 11_CategoryDetails | ✅ | STR 7 + FUR 5 all visible and separate, 67 % width, readable, no overlaps, label space under rows. |
| 08_Variants_A | ✅ | 9 variants (STR-01 W/Gate, STR-07 W, FLB x3 Planted, PLT-02 Pink, PLT-06 White, FUR-05 Blue) each right of its base, same camera, colours correct, no pink materials. |
| 08_Variants_B | 🟡 | 9 variants present and correct. Layout uneven: hook ORN-05 / ORN-05_Feeder stand in front of PLT-03_Pink (overlap), gnomes small at bottom-left (~65 px), irregular gaps. Optional re-pack; not a blocker. |
| 09_Technical | ✅ | Real LOD0 (2314) vs LOD1 (1156) gazebo, rose bush, pond kit with wireframe; lines visible at 50 % on roof, railing and pond (rose bush wire dense but ok); free floor left/right/below for tris labels and "No colliders". Numbers match scene_catalog_report/ImportReport. Note: pond and rose bush are small (~370x200 / 140x140 px). |
| 13_Materials | ✅ | Atlas A group (back) and atlas F group (front), left ~36 % free for two 256² swatches; no pink, no overexposure. Swing sits ~75 px from the right edge: acceptable. |
| Card | 🔴 | Rules OK (content 8-62 %, bottom 38 % free sky) but the hero is small: arch 13 % wide / 43 % tall, ~55x120 px at 420x280; island has big empty front grass; two red rails read as stray sticks; gnome 25 px dissolves; left cloud cut by the frame. See scenes/Catalog_fixes.md Fix 1. |
| IconSource | ✅ | Arch with roses on the island, contrast blue background, silhouette 80 % wide / 60 % tall. At 160 px clear; at 60 px the white arch + gate read, bushes become dots. Optional for Э12: crop slightly tighter (~85 % width). |
| 14_Unity | ❓ | Not produced (CLI capture grabbed another window). Needs a manual Editor screenshot from the owner. |

Counts: ✅ 5 (11, 08A, 09, 13, Icon), 🟡 3 (06, 06_2, 08B), 🔴 1 (Card), ❓ 1 (14_Unity, not produced).
Model defects (→ Э7): none seen.

## Pass 2 (2026-11-26, Card return 1 of 3)

Re-viewed Card.png, 06_FullCollection_2.png, 08_Variants_B.png at 100 %.
- Card: ✅. Arch + garland now ~55 % of the height and ~20 % of the width; beds and rose bushes in one line, rails gone, gnome by the right post, left cloud inside the frame, bottom ~35 % free sky. Minor: left bed corner sits on the island edge; not a blocker.
- 06_FullCollection_2: ✅. Rows are separated, no overlaps of topiaries with garland/ivy.
- 08_Variants_B: ✅. 9 variants each beside its base, hooks no longer overlap PLT-03_Pink, even gaps. Note: the group is a wide strip (4-97 % width, 28-72 % height), items are smaller than before (gnomes ~65 px); width-limited, accepted.

## Final table renders_3

| Shot | Verdict |
|---|---|
| 06_FullCollection | 🟡 accepted (small items covered by 06_2; no fix required) |
| 06_FullCollection_2 | ✅ |
| 11_CategoryDetails | ✅ |
| 08_Variants_A | ✅ |
| 08_Variants_B | ✅ |
| 09_Technical | ✅ |
| 13_Materials | ✅ |
| Card | ✅ |
| IconSource | ✅ |
| 14_Unity | ❓ needs owner's manual Editor screenshot |

Counts: ✅ 8, 🟡 1 (accepted), 🔴 0, ❓ 1.
