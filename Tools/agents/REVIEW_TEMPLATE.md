# <Pack>: reference review (<date>)

Every preview `art/<Pack>/Previews/<Prefix><ID>_Preview.png` compared with `planning/<Pack>/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | | Close to the reference, no edits |
| 🟡 Pass with notes | | Shippable; small differences, optional edit |
| 🔴 Fix | | Silhouette, signature feature or proportions clearly off |
| ❓ Decision | | Deliberate deviation; the owner decides |

Cross-cutting issue (if any): <e.g. furniture members 1.3–1.5x thinner than the references; fix = one thickness factor>.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|

## ✅ Pass
- <category>: <IDs>

## How to fix
- Which items share one script (fix in one pass), which go back to the worker who built them.
- After each fix: re-export, re-import verify, new preview, then a second sheet pass; append a results table below.
