# FarmMachinery: reference review, rework after series (2026-11-24)

Items: HRV-03 (Fix 1: detachable header), ATT-05 (new Header_Pickup), IMP-07 (Fix 1: Transport width). Inspected: paired sheet
`%TEMP%/pack_review/sheet_00_HRV-03_IMP-07.png` (compare_sheets, rows paired correctly), previews of the three models, ATT-05 vs
`FMS_Mach_Header_Grain_Preview.png` (series sibling), assembly render `%TEMP%/farmmachinery_check/HRV-03/HRV-03_assembly_ATT-05.png`
vs `references/HRV-03.png`, "## Fix 1" sections of the specs, builder report. Numbers (tris, bbox 2.92 x 3.38, mating 0 error, points)
are taken from the builder report, not re-measured; the Work pose of IMP-07 has no preview and was not looked at.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | |
| 🟡 Pass with notes | 3 | HRV-03, ATT-05, IMP-07 |
| 🔴 Fix | 0 | |
| ❓ Decision | 0 | |

Cross-cutting issue: none new. The preview camera still differs from the reference camera (rotated, higher), known from b1-b3.
CATALOG.md needs syncing by the planner/orchestrator: HRV-03 size without header (3.5 x 4.88 x 6.52 m, catalogue says 8.0 long
incl. pickup), ATT-05 as a new line (3.3 x 1.8 x 1.15), IMP-07 Transport 2.92 x 3.38 (cat. 2.8 x 3.4; Work 6.66).

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| HRV-03 | FMS_Mach_ForageHarvester | Fix 1 done as written: built-in Header removed, a red feed-channel stub `Feeder` with a dark opening at the front (reads as a headerless chopper, like HRV-01), Feeder_Front = HRV-01 interface (1.60 x 0.90, Y 0.80, +Z), cab, spout, wheels, body, Spout_Out, Seat, Door_L kept. Assembly with ATT-05 reads like the reference: same red cab with beacon, tall arched spout with grey tip, exhaust, big front / small rear lugs, pickup header in front. Notes: the spout is narrower and its arch lower than the reference (carried over from b2); the preview camera shows the stub from a steep angle, the opening is clear. Re-centred root (+0.74 m Z on all points): expected after the header removal (root = centre of the footprint), no issue if the prefab/layout take points from the re-imported FBX. Overall length 6.52 m is without header, as the Fix allows. |
| ATT-05 | FMS_Mach_Header_Pickup | Reads as the reference pickup: red guard hood, side walls, grey drum with ~11 bent tines, dark throat/adapter at the rear; 3.30 x 1.80 x 1.15 fits the Feeder interface (Feeder_Rear Y 0.80). As a sibling of ATT-03/ATT-04: same palette (red body, grey steel), same mounting, but a more massive closed hood and no orange accents; reads as a different header type, which is right. Notes: (1) lowest point 0.15 m vs the spec's ~0.10: accepted (spec says "~", geometry kept; no ground-skid issue). (2) Tines are thinner and more numerous than the reference's ~8 big curved tines; acceptable, readable. (3) On TRL-04 it sits only on the middle saddle, 5 cm above, 0 overlaps: ATT-05 is 3.3 m wide on a 2.2 m trailer rest; acceptable for the transport carrier, optional: show headers on TRL-04 only in the demo if the 5 cm gap looks floating. |
| IMP-07 | FMS_Mach_HayRake | Fix 1 done in intent: Transport width 2.92 m (target <= 3.0), height 3.38 (<= 3.4), nothing else changed (frame, wheels, drawbar, tine count, 12 tines per rotor). Deviation from the written text, accepted: the Fix said 75-80 deg, the builder showed this cannot reach <= 3.0 m (80 deg = 3.78 m); the orchestrator chose 90 deg, which meets the goal. Transport readability: two tall grey arms with two big 12-tine orange-tipped rotors in vertical planes beside the red frame, clearly a two-rotor rake and clearly narrower, the same shape in the same pose reads from the front/side; from the front the rotors are edge-on slim stripes (expected). The V shape of the reference is only in Work, as stated. Notes: frame rails still read thin (b3 note); rotors are close to the wheels in the side view but do not intersect (builder: 0 overlaps, rotor lowest ~1.26 m); the Work pose was not rendered here: please include one Work render in the Unity step. |

## ✅ Pass
- None in this batch.

## How to fix
- No fixes required. After the orchestrator syncs CATALOG.md the rework is closed for HRV-03, ATT-05 and IMP-07.
- Not verified here: topology/FBX/LOD, Unity import, mating numbers, IMP-07 Work pose and TRC-01/TRC-02 clearance (taken from the builder report).
