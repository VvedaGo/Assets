# FarmMachinery: reference review, batch b2 (2026-11-24)

Previews `art/FarmMachinery/Previews/FMS_Mach_<Name>_Preview.png` for IMP-06, TRL-01, TRL-02, TRL-03, ATT-01, ATT-02, ATT-04,
TRL-04, HRV-02, HRV-03 compared with `planning/FarmMachinery/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`; staged as `<ID_>_Preview.png`; sheets `sheet_00_IMP-06_TRL-02.png`,
`sheet_01_TRL-03_ATT-02.png`, `sheet_02_ATT-04_HRV-02.png`, `sheet_03_HRV-03_HRV-03.png`; TRL-01, ATT-01, TRL-04 are on
sheets 00, 01, 02). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px. Technical numbers
are taken from the builder report/notes (not re-measured). Already accepted, not counted as deviations: shared drawbar eye
Ø0.24; ATT-02 lugs X +-0.45; TRL-04 without Hitch_Rear; HRV-03 spout 4.88 m; tris overruns ATT-01 404/400 and TRL-04
2648/2000 (judged visually only: neither reads as over-detailed).

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 1 | ATT-04 |
| 🟡 Pass with notes | 9 | IMP-06, TRL-01, TRL-02, TRL-03, ATT-01, ATT-02, TRL-04, HRV-02, HRV-03 |
| 🔴 Fix | 0 | |
| ❓ Decision | 0 | |

Cross-cutting issue: (1) the preview camera is rotated and slightly higher than the reference camera, so the far-side wheels
and low parts are hidden (trailer wheels TRL-01/02/03 read smaller and darker than the reference cream-rim wheels; IMP-06
roller hidden behind the frame; ATT-02 lugs at the side). Same remark as in b1; no model edit needed, a lower elevation for
the store renders would match the references better. (2) Shared lug tyres are slightly smaller against the trailer bodies
than in the references (bodies are longer); acceptable, not a fix. Series style (red body, grey steel, cream rims, flat
shading, chamfers) is consistent with the pilot and b1.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| IMP-06 | FMS_Mach_Cultivator | S-tines with pointed shares in interleaved rows, rear cage roller, A-mast with lugs, grey steel frame: all present. Notes: (1) the roller (reference signature, large and visible at the rear) is almost hidden behind the frame in the preview (only the end disc at the right); it sits on the ground per spec. (2) Frame beams with clamp blocks look busier/boxier than the slim reference frame; fewer tines read (about 12 of 20). (3) Mast red and centred (shared rule, contract), reference grey and at the left. Optional: a slightly lower camera for the store image. |
| TRL-01 | FMS_Mach_Trailer_Tipper | Red high-sided tipper box with ribs, chamfered front wall, orange reflectors, A-drawbar with eye, tandem lug wheels: silhouette and colour match. Notes: wheels small and the far pair mostly hidden under the bed (reference wheels bigger with clear cream rims); the reference hydraulic ram stub on the front wall is missing; walls slightly lower relative to length. |
| TRL-02 | FMS_Mach_Trailer_Flatbed | Red headboard, wooden deck planks with grey frame edge, A-drawbar, tandem wheels: matches. Notes: wheels smaller and half hidden under the deck (deck 1.135, accepted); headboard slightly thinner; planks a bit darker/more uniform. |
| TRL-03 | FMS_Mach_Trailer_Tank | Red faceted tank with two straps, hatch dome, railing, ladder, tandem wheels, A-drawbar: matches well. Notes: wheels hidden by the tank and darker; reference rear valve/pipe stub and orange lamp not visible; hatch dome a little smaller. |
| ATT-01 | FMS_Mach_QuickHitch | Triangular grey frame with top bracket, two lower hooks with pins: reads as a quick hitch. Notes: hooks point down/outward in thin plates while the reference hooks are chunky C-hooks, pins stick out sideways in the reference; the lower beam is raised (builder, for mating), so the triangle is less closed than the reference; top block is a plain box without the hook slot. |
| ATT-02 | FMS_Mach_FrontWeight | Chamfered red block with two horizontal ribs, grey A-bracket with top-link block and dark lugs: matches. Notes: ribs are proud strips, the reference has recessed panels; block looks taller/deeper in this camera (0.97 m with the bracket), reference is wider and flatter; one lug visible only. |
| TRL-04 | FMS_Mach_Trailer_Header | Long red/grey frame with grey cross members, three dark header cradles, A-drawbar, four wheels: matches the reference idea. Notes: cradles are long lengthwise bars (header rotated 90 deg, accepted) instead of short saddles; frame rails thinner and the red chassis rails less visible; wheels near-black with small cream rims, readable. |
| HRV-02 | FMS_Mach_Baler_Round | Red round chamber with three grey straps, orange side reflectors, drawbar arms, pickup with tines, big lug wheel, hydraulic arm on top: signature reads. Notes: a large red hood/ramp block covers the pickup so the tines are less visible than in the reference (open rake in front); chamber a little shorter/rounder; hydraulic cylinder on the left is thinner. |
| HRV-03 | FMS_Mach_ForageHarvester | Red cab with glass and orange beacon, engine cover with grille, tall curved spout with grey tip, tined pickup header at the front, big front wheels, small rear wheels: silhouette and palette match. Notes: spout is narrower and its grey tip smaller than the reference arch; body behind the cab is long and flat (looks more like a long box), cab slightly taller; the rear wheels look smaller than in the reference; no exhaust stack and mirrors in the reference position. |

## ✅ Pass
- Attachments: ATT-04 (corn header: seven red pointed row units, grey roller bar/chains, dark centre window, orange tips; matches closely).

## How to fix
- No fixes required. Optional polish only: lower preview camera for the store (hidden roller/wheels), IMP-06 cleaner frame,
  ATT-01 chunkier hooks, HRV-02 lower hood over the pickup, HRV-03 wider spout; none blocks the batch.
- Not verified in this review: topology/FBX/LOD, Unity import, mating (builder numbers taken as is). Known open item from the
  builder: TRL-04 on HRV-01 (10 face pairs, ~1 mm) is fixed on HRV-01 separately.
