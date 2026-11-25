# FarmMachinery: reference review, batch b1 (2026-11-24)

Previews `art/FarmMachinery/Previews/FMS_Mach_<Name>_Preview.png` for TRC-02, IMP-02, IMP-03, IMP-04 compared with
`planning/FarmMachinery/references/<ID>.png` on paired sheets (`Tools/blender/compare_sheets.py`; staged as `<ID_>_Preview.png`;
sheets `sheet_00_TRC-02_IMP-03.png` (TRC-02, IMP-02, IMP-03) and `sheet_01_IMP-04_IMP-04.png`). IMP-05 has no reference (owner
decision): judged against its spec, the Work-pose check render (`farmmachinery_check/IMP-05/IMP-05_check_work.png`) and the
style of IMP-01 / IMP-03. Criteria: silhouette, signature feature, proportions, colour, readability at 128 px. Technical
numbers are taken from builder notes (not re-measured). Already decided, not counted as deviations: IMP-04 cutter bar on the right;
IMP-02 coulters at X +-1.12 and top bracket Y 1.12; TRC-02 wheel positions per the reference; IMP-05 changed fold geometry.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | |
| 🟡 Pass with notes | 5 | TRC-02, IMP-02, IMP-03, IMP-04, IMP-05 |
| 🔴 Fix | 0 | |
| ❓ Decision | 0 | (IMP-04 transport height 2.5 vs 3.1 m is noted below as optional) |

Cross-cutting issue: the preview camera differs from the reference camera in elevation/yaw, so hopper/tank/cab sides cover the
lower parts (IMP-02 press row and left wheel, IMP-03 far wheel, TRC-02 far side). No model edit needed; if the previews are
re-rendered for the store, a slightly lower elevation would match the references better. Mast colour (red instead of the
grey in the references of IMP-02, IMP-04) follows the shared-linkage rule of the spec; consistent across the batch.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| TRC-02 | FMS_Mach_Tractor_Large | Silhouette, chamfered bonnet, grille with headlights, cream-striped four-pillar cab, orange beacon, four lugged wheels with cream rims, front linkage all match and read at 128 px. Notes: (1) the far-side front mudguard looks like a second raised block with dark gaps beside the bonnet (open slots), reads cluttered in this angle; the reference has a clean mudguard hugging the bonnet. (2) One mirror and a straight exhaust pole instead of two mirrors and a bent exhaust. (3) Cab looks a little boxier/taller against the wheels. Optional only. |
| IMP-02 | FMS_Mach_Seeder | Trapezoid red hopper with straps, orange reflectors, grey lid tabs, coulter row below the bar, markers folded up with discs, lugged wheels at the ends: all present. Notes: (1) hopper is visually dominant; the press row and the far wheel are hidden, near wheel small (spec Ø0.70, reference looks larger). (2) Lid handle of the reference is missing (spec: handle block on the front edge; lid shows only four hinge tabs). (3) About 7 coulters visible instead of 9 (X +-1.12, decided). (4) Mast is red, reference grey (spec rule). |
| IMP-03 | FMS_Mach_Sprayer | Red 16-sided tank with straps, grey filler dome, orange beacon, orange boom tip blocks, lattice boom along the tank, single-axle lug wheels, A-drawbar with ring eye: signature all read. Notes: tank slimmer relative to the wheels and boom than in the reference; reference rear ladder not visible from this angle; no cross brace on the drawbar (builder note); the second wheel is hidden. |
| IMP-04 | FMS_Mach_Mower | Raised cutter bar with five discs, red guard curtain with orange diagonal stripes, red gearbox, linkage frame with lugs: reads as in the reference (side mirrored, decided). Notes: (1) bar relatively shorter, bbox height 2.50 m vs catalogue 3.1 (builder: bar length kept for the 3.13 m Work width). Optional: if the owner wants 3.1 m catalogue height, lengthen the bar; otherwise update the catalogue. (2) The red curtain stands out above the grey bar top and looks slightly detached from it; the reference curtain is flush. (3) Added parking stands (right-hand leg) are not in the reference. |
| IMP-05 | FMS_Mach_DiscHarrow | No reference. Against the spec: A-drawbar with ring eye at the front, central frame with three red cover panels, two V gangs (front and rear) of 4-disc central sections plus 4-disc wing sections (24 discs, chunky 12-segment discs), orange wing tip blocks, wings hinged to the frame, two lug wheels Ø0.90 inboard (no collision, Work check shows discs on the ground, width 4.06 m). Style matches IMP-01/IMP-03 (grey steel, red panels, cream-rim lug tyres). Notes: (1) the preview shows the Transport pose, the spec says Work: the folded wings hide discs behind beams and the picture reads cluttered; the Work check render reads much better, recommended for the store preview (optional). (2) Mostly grey with small red accents. (3) Accepted deviations: fold 90 deg, transport height 1.73 (spec 2.4), length 5.22 (spec 5.0), disc spacing 0.25. |

## ✅ Pass
- none

## How to fix
- No fixes required. Optional polish only (TRC-02 far mudguard clean-up, IMP-02 lid handle, IMP-04 curtain flush with the bar,
  IMP-05 preview in Work pose); none blocks the batch.
- Not verified in this review: topology/FBX/LOD (builder notes taken as is), Unity import, mating with the tractors (builder
  notes: TRC-02 0 overlaps; TRC-01 overlap of IMP-03/IMP-05 eye is handled by the separate TRC-01 fork fix).
