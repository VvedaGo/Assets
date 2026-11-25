# FarmMachinery: reference review, batch b3 (2026-11-24)

Previews `art/FarmMachinery/Previews/FMS_Mach_<Name>_Preview.png` for TRL-05, TRL-06, EQP-01, EQP-02, IMP-07, PRP-01 compared
with `planning/FarmMachinery/references/<ID>.png` on paired sheets (`Tools/blender/compare_sheets.py`; staged as
`<ID_>_Preview.png`; sheets `sheet_00_TRL-05_EQP-01.png` (TRL-05, TRL-06, EQP-01) and `sheet_01_EQP-02_PRP-01.png`
(EQP-02, IMP-07, PRP-01); pairing checked, every row shows the right reference/model). Criteria: silhouette, signature
feature, proportions, colour, readability at 128 px. Technical numbers (tris, mating 0 error, SNAP OK, sizes) are taken from the
builder report/notes, not re-measured. EQP-02 was also compared with Farm Yard `FMS_Silo` (blue, tall, domed, 3 flat bands):
clearly distinct (grey corrugated, squat, low cone, hatch). Accepted, not counted as deviations: TRL-06 3172/3000 tris
(lattice overrun allowed); shared eye Ø0.24.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | |
| 🟡 Pass with notes | 5 | TRL-05, TRL-06, EQP-01, EQP-02, PRP-01 |
| 🔴 Fix | 0 | |
| ❓ Decision | 1 | IMP-07 |

Cross-cutting issue: (1) as in b1/b2 the preview camera differs from the reference camera (rotated, higher), so far-side
wheels are hidden or small and dark (TRL-05, TRL-06, EQP-01 wheels); no model edit, a lower camera for the store renders helps.
(2) Thin members on the slender machines: EQP-01 frame legs/hopper/wheels and IMP-07 frame rails read thinner than in the
references (about 1.3x), still readable. (3) Two catalogue figures no longer match the models and CATALOG.md should be
synced by the planner/orchestrator after the decision: EQP-02 6.0 x 6.0 x 6.0 (cat. 7.2 high; ladder side -X) and IMP-07
Transport width. Series style (red body, grey steel, cream rims, flat shading) is consistent with the pilot, b1 and b2.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|
| IMP-07 | FMS_Mach_HayRake | Transport width 4.57 m (X, bbox +-2.28), height 3.09, instead of catalogue 2.8 x 3.4. Reason (builder): rotors stand in the arm plane at 70 deg; the reference itself draws a wide, flared Transport (about 4.9 m). A rake in transport pose is normally road-narrow (<= 3 m), and the demo/store may show it next to tractors and the 2.5 m trailers. Look otherwise matches (red frame, two arms with 12-tine rotors, orange tips, lug wheels). Work span 6.66 (spec 6.8) is fine. | A) Accept 4.57 m (matches the reference silhouette; update CATALOG to 4.6 x 4.6 x 3.1; no rebuild). B) Steeper arms in Transport: raise angle 75-80 deg instead of 70 (Work = lowering by the same angle, PART_ROT = +-75..80 deg; arm hinge -> hub 1.50 m, rotor R 1.09 unchanged). Estimate: hub X = 0.80 + 1.50 cos 75 = 1.19, rotor half-extent 1.09 cos 75 = 0.28 plus tips/tines 10 deg -> half width about 1.5, i.e. Transport width about 3.0 m; height 0.85 + 1.50 sin 75 + 1.09 sin 75 = about 3.35 m (spec 3.4). Work span stays 6.66 m. Builder must re-measure the real bbox; target <= 3.0 m wide, <= 3.4 m high; re-check rotor x wheels/frame clearance and mating. Recommendation: B if the pack is shown with road scenes or next to tractors, otherwise A; owner decides. |

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| TRL-05 | FMS_Mach_GrainCart | Red faceted hopper with side rail, orange lamps, fender and lug wheel, long A-drawbar with eye, unloading auger at the front-left: reads as a grain cart. Notes: (1) the auger tube rises steeply high above the hopper rim, the reference auger is short and lies along the front-left wall (tube 3.15 m for the spec, accepted); (2) hopper is shallower and drawbar longer than in the reference, wheel is darker/smaller under the fender; (3) the auger and the hopper mirror the reference side (accepted: spec). |
| TRL-06 | FMS_Mach_Trailer_Bale | Low long red/grey chassis, wooden plank deck, two red lattice headboards, tandem lug wheels, A-drawbar: silhouette and palette match closely. Notes: wheels small and mostly hidden under the deck (deck 1.035 above the tyres, as TRL-02); lattice grid a bit coarser/thicker bars; planks darker. |
| EQP-01 | FMS_Mach_GrainAuger | Inclined grey tube with joint bands and end hood, red hopper at the low end, red A-frame on a wheel pair, drawbar with eye: signature reads, same angle and layout. Notes: hopper smaller/shallower and the tube and frame legs thinner than the reference (spec Ø0.50 followed), wheels smaller (Ø0.7 cap), reference outlet hood has orange stripes (missing); drawbar plain ring eye instead of a plate (accepted). Optional: hopper 1.2x larger, legs about 0.14 m. |
| EQP-02 | FMS_Mach_GrainBin | Squat grey corrugated cylinder with bands, low conical roof with hatch and knob, ladder, door: matches the reference and is clearly different from Farm Yard `FMS_Silo`. Height 6.0 m instead of 7.2 is accepted: the reference is wider than tall (about 1.1 : 1), 7.2 would read as a tall tank, which the Duplicates section forbids. Notes: wall ribs and bands are subtler than the reference vertical panels; ladder narrower and on -X (reference on the right side; the hatch hinge Z, accepted); roof slightly taller than the reference cone. Update CATALOG to 6.0 x 6.0 x 6.0. |
| PRP-01 | FMS_Mach_Windrow | Golden chamfered ridge, trapezoid profile, tapered ends: the colour, size and silhouette match; SNAP OK (8/8 vertices at both ends). Notes: reference ridge is lumpier with distinct bulges, the model ridge is smoother with a mild wave; optional: 3-4 stronger lumps (not above 0.44 m, ends identical). |

## ✅ Pass
- None in this batch.

## How to fix
- No required fixes. Only IMP-07 needs an owner decision (option A: no work; option B: one pass in the builder script of IMP-07,
  arm angle and PART_ROT, then re-export, re-import verify, new preview, mating recheck on TRC-01/TRC-02).
- Optional polish: EQP-01 thickness and hopper, TRL-05 shorter auger, PRP-01 lumps, lower preview camera for the store.
- Not verified in this review: topology/FBX/LOD, Unity import, mating and SNAP numbers (taken from the builder report as is).
