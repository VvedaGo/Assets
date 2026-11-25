# FarmMachinery: reference review, batch pilot (2026-11-24)

Every preview `art/FarmMachinery/Previews/FMS_Mach_<Name>_Preview.png` compared with `planning/FarmMachinery/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`; previews are named by model name, so they were staged as `<ID_>_Preview.png`). Criteria: silhouette,
signature feature, proportions, colour, readability at 128 px. Also checked against the CATALOG "Игровая готовность" contract and STYLE.md.
Technical checks (topology, gaps, FBX) are taken from the builder notes; Unity import is a separate step.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | |
| 🟡 Pass with notes | 4 | IMP-01 (after the owner decision of 2026-11-24, see below), TRC-01, HRV-01, ATT-03 |
| 🔴 Fix | 0 | |
| ❓ Decision | 0 | IMP-01 was ❓ (LOD1 naming, per-item atlas); resolved by the orchestrator, see "Решение оркестратора" |

Cross-cutting issue: the LOD1 convention of `Tools/blender/make_lod1.py` (`<Part>_Low1` as a root child, re-parented by
`PackPrefabBuilder`) contradicts CATALOG contract item 3 (`<Name>_LOD1` child inside the part). It will hit every pilot and later model with a moving part.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|
| IMP-01 | FMS_Mach_Plough | (1) LOD1 objects are `Frame_Low1` / `Wheel_Gauge_Low1`, direct children of the root, not `<Name>_LOD1` inside the part (CATALOG item 3, spec "Common rules"). The contract text does not allow it. The tool comment says `_LOD1` was avoided on purpose (Unity treats `_LODn` as an LOD set and warns about missing `_LOD0`); `PackPrefabBuilder` re-parents `*_Low1` under its part and builds the LODGroup. (2) Per-item atlas `T_FarmMachinery_IMP01_BaseColor.png` vs STYLE.md "Материалы и текстуры": 3 shared atlases Red/Green/Blue of one layout, colour variant = material swap. Builder says it is the Red layout with cells 10-15 replaced, but a separate file per item is not in the plan. | (1a) Keep `_Low1` and amend CATALOG item 3 to "`<Name>_Low1` in the FBX; the prefab builder moves it under the part as a child with zero offset" (recommended: the prefab result equals the contract, no tool change, no Unity warning). (1b) Change `make_lod1.py` to emit `<Name>_LOD1` as a child inside the part (needs a Unity-side check for the `_LODn` warning). (1c) Rename in the prefab builder only. (2a) Use the shared `T_FarmMachinery_Red` atlas for all models, delete the per-item PNG, re-point the material (recommended if the cells are identical to STYLE; Green/Blue swap then works). (2b) Keep per-item atlases and update STYLE.md, accepting that Green/Blue need one atlas per item. Please also confirm that the cells 10-15 in the per-item file equal the STYLE.md table. |

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| IMP-01 (visual part) | FMS_Mach_Plough | Visual verdict alone would be 🟡. See notes below. |

### IMP-01 notes (sheet `sheet_00_IMP-01_IMP-01.png`, preview 1280x800, reference 1536x1024)
Criteria:
- Silhouette: pass. Red A-frame with three lugs, long diagonal red beam with grey clamps, four bodies, gauge wheel at the beam end all read. Reads at 128 px (builder's check, sheet thumbnail agrees).
- Signature feature (diagonal stagger of 4 bodies): pass, but weaker than the reference. Stagger is 0.22 m per body (reference looks ~0.35), so the mouldboards overlap into one grey wall in the 3/4 view and the curled fins of the reference are less readable (smaller and flatter, mostly leg plus plate). Optional: widen the stagger only if the bbox allows (now X 1.44 m vs 1.6 target).
- Proportions: pass with note. The gauge wheel sits on a long grey cross-arm (about 0.6 m, out beyond the beam) while the reference has a short post at the beam end; this is the biggest visible difference. Mast legs slightly thinner than the reference. Size 1.44 x 1.40 x 3.62 m vs 1.6 x 1.4 x 3.6 target: X is 10 % narrow (consequence of the owner's one-straight-beam decision), acceptable.
- Colour: pass. Red top / dark red sides, grey lower band and clamps, near-black lugged tyre, cream rim all match; one material.
- Contract: 1260 / 2500 tris, LOD1 630 (50 %): pass. Root origin, Link3P_Front (0, 0.60, +1.74) on the lower pin axes (owner decision), lugs X +-0.45, Y 0.60: not independently verified (no Blender/FBX inspection done in this review; from builder notes). Hierarchy Frame / Wheel_Gauge / Link3P_Front matches the spec. No PTO: ok.
- Deviations that are NOT flagged (owner decisions): one straight beam, Link3P_Front on the pin axes.
- Style match with approved pack models: none exist yet in FarmMachinery; the shared wheel and linkage frame look consistent with the spec's shared functions.

Verdict IMP-01: ❓ (owner decision on LOD1 convention and atlas); the model art itself is 🟡 and needs no FIX round.

## ✅ Pass
- none yet

## How to fix
- IMP-01: no geometry fix. After the owner decides (1) and (2): update CATALOG item 3 or `make_lod1.py`, and re-point the atlas if 2a. Optional polish for a later pass: shorten the wheel arm.
- Later pilot items are appended below as separate sections.


## Решение оркестратора по ❓ IMP-01 (2026-11-24)

- LOD1: вариант (a). Соглашение `*_Low1` на корне правильное (PackPrefabBuilder.cs 101–113 переносит их внутрь частей); ошибся текст контракта, CATALOG п. 3 исправлен. Отступления нет.
- Атлас: вариант (a). Общий атлас пака `T_FarmMachinery_Red_BaseColor` уже утверждён в STYLE.md; поатласный файл IMP-01 — отступление строителя, строитель переэкспортирует IMP-01 с общим атласом после TRC-01 (геометрия и UV не меняются).
- Итог IMP-01: 🟡 PASS с замечаниями (визуальные отличия выше: опорное колесо на длинном кронштейне, корпуса сливаются в ракурсе 3/4, ширина 1.44 м). Переделка по ним — только по команде владельца `переделать IMP-01`.


---

## TRC-01 (FMS_Mach_Tractor_Cab), review 2026-11-24

Sheet `sheet_00_TRC-01_TRC-01.png` (preview 1280x800, reference 1536x1024); also viewed both images and the Farm Yard `FMS_Tractor` preview.

**Verdict TRC-01: 🟡 PASS with notes** (no FIX round; no owner decision needed, deviations below are already justified by the reference or the builder's constraints).

Criteria:
- Silhouette: pass. Long chamfered bonnet, tall closed cab with flat roof, big rear fender over the large rear tyre, small front fender, grille + 2 headlights + grey front weights, orange beacon rear-left, exhaust, mirrors: all read, same front-left 3/4 angle as the reference. Reads at 128 px (sheet thumbnail agrees).
- Difference from Farm Yard `FMS_Tractor`: clear. Closed cab (roof at 3.0 m, glass, door) vs open tractor with seat and steering wheel; red/cream/black palette with cream rims vs grey discs; no tall exhaust on the bonnet top. Not a copy.
- Signature feature (closed cab with glass): pass, weaker than the reference. Cab is ~1.1 m wide (rear tyre gap) and the roof overhangs it; the roof reads as a thick slab over a narrow box, the glass area is smaller and the red pillars/door frame thicker than in the reference. Acceptable under the 2.4 m width limit.
- Proportions: pass. Bonnet/cab/wheel relations match; rear fender slightly bulkier, exhaust is short and sits right against the cab pillar (reference: taller, further forward on the bonnet). Size 2.40 x 3.00 x 4.42 m inside the 2.4 x 4.4 x 3.0 catalogue box (Z +0.02 m, as in the builder's bbox ±2.21; not flagged).
- Colour: pass with note. Red top / dark red sides, blue-grey glass, black tyres, grey weights, orange beacon, yellow lights match. Rim discs read greyish beige and a bit dull next to the reference's warm cream (shading in the preview or atlas cell 3/4; check in Unity render, no model change implied).
- Contract (builder notes, not independently inspected in Blender/FBX): 3348 / 7000 tris, LOD1 1674 (50 %), `<part>_Low1` root children per CATALOG item 3, shared atlas `T_FarmMachinery_Red_BaseColor`, Link3P_Rear/PTO_Rear/Hitch_Rear/Seat heights as in the spec, IMP-01 mating check error 0. Rear linkage and drawbar are not visible in this preview angle: not verifiable from the image.
- Deviations that are NOT flagged: exhaust on the right and beacon rear-left (reference wins over spec, PIPE-04); seat point (0, 1.60, -0.70) instead of (0, 1.25, -0.9) (cab floor 1.40); right-side static look-alike door frame and right steps.

Optional polish (only on owner command): widen the glass panels / thin the pillars, raise the exhaust ~0.2 m and move it forward off the pillar.


---

## HRV-01 (FMS_Mach_Combine), review 2026-11-24

Sheet `sheet_00_HRV-01_ATT-03.png`. The preview shows the combine WITHOUT header (by design), so the overall look was judged on the
assembly render `HRV-01_assembly_ATT-03.png` against `references/HRV-01.png`. The assembly camera is higher and more from the side than the reference.

**Verdict HRV-01: 🟡 PASS with notes** (no FIX, no owner decision).

Criteria:
- Silhouette: pass. Tall glazed cab at the front over a sloped feeder housing, long red tank/engine body, two big lugged drive tyres at the front and two small rear tyres, side grille, exhaust at the rear, rear steering wheels: all read. Cab-forward, highest mass at the front, as in the reference.
- Unloading auger side: **acceptable, not a FIX.** The builder's note says the reference shows it on the right; on the image it is on the machine's LEFT. The reference camera is front-left: the visible long side is the left side (same side as the door beside the front glass and the grille), and the auger lies on the top edge of that visible side, with the riser next to the cab. The model's auger is on the same visible edge, with the same riser at the cab, grey tube, orange band; its shape is a straight tube with a vertical spout block, the reference has a bent spout at the rear end. The spec pivot (-1.25, 3.45, -1.40) is therefore consistent with the reference, and PIPE-04 gives no conflict. Please correct the note in the builder's file if it is kept as a record. The exhaust is on the far (right) side in both.
- Detail / tris (2820 of 12000, 24 %): not underbuilt. The reference is a low-poly flat-shaded render of the same level: the model has the same part set (lugged tyres with cream rims, slatted grille, mirrors, beacon, lights, cream roof stripe, door with handle, auger bands, hitch fork). Compared with TRC-01 (3348 tris, 28 % of its budget) it is on the same detail level. No parts must be added.
- Proportions: pass with notes. Body is a plain long box; the reference has chamfered shoulders on the tank and a shorter, deeper feeder housing; the model feeder is longer and narrower in the 3/4 view and the dark lower skirt between the wheels is more visible. Drive tyres are about as big as in the reference and read well. Rear box looks slightly longer than the reference (within the 8.4 m spec).
- Colour: pass. Red top / dark red sides, dark lower section, blue-grey glass, cream rims, grey auger, orange accents match.
- Contract (builder notes, not independently inspected in Blender/FBX): 2820 / 12000 tris, LOD1 1410 (50 %), `<part>_Low1` root children, shared atlas, bbox X +-1.80, Z +-4.20, Y 0..4.00, Feeder_Front (0, 0.80, +4.20), Hitch_Rear Z -4.13 on the fork pin (instead of -4.20, justified), exact part names. No coplanar faces/gaps/non-manifold per the notes.
- Feeder mating: assembly render reads like the reference: header in front of the feeder, frames meet face to face, no visible gap or overlap. Builder error 0.

Optional polish (only on owner command): chamfer the tank shoulders, shorten the feeder housing, bend the auger spout.

---

## ATT-03 (FMS_Mach_Header_Grain), review 2026-11-24

Sheet `sheet_00_HRV-01_ATT-03.png` (lower row), reference `ATT-03.png`, assembly render.

**Verdict ATT-03: 🟡 PASS with notes** (no FIX).

Criteria:
- Silhouette: pass. Wide red trough, comb-like cutter bar with fingers, octagonal reel end discs with spokes and 8 bars, centre auger with flights, orange divider tips, black throat plate in the middle of the rear wall. Reads at 128 px.
- Signature feature (reel + auger + cutter bar): pass. All three visible and distinct. The model reel bars and discs are slightly lighter than in the reference, the flights read a bit smaller, the reel arm and its cross brace are not visible in the preview angle.
- Proportions: pass with notes. The end walls are lower and flatter than the reference, where they are tall sloped wedges with large orange tips; the reference header looks deeper. Width 6.2 m x depth about 2.1 m is within the spec. The sheet angle differs (model camera is lower and closer to the front), which exaggerates the difference.
- Colour: pass. Red trough, dark red inside, grey cutter bar/reel/auger, orange tips match.
- Contract (builder notes, not inspected in Blender/FBX): 1408 / 5000 tris, LOD1 650 (46 %), shared atlas, Feeder_Rear (0, 0.80, -1.05), 1.60 x 0.90 interface, header lowest point 0.10 m. Deviations: auger tube 0.50 / flights 0.70 (reel clearance 0.029 m), dark throat plate: accepted by the reference. Assembly with HRV-01 matches the HRV-01 reference overall.

Optional polish (only on owner command): taller end walls with larger orange tips.

## Cross-cutting (pilot)
No new cross-cutting issue from HRV-01/ATT-03. The recorded rule of thumb: model previews are rendered from a different camera than the references, so the proportions in this batch were judged mostly by part layout, not by pixel comparison. Suggest that the orchestrator renders the assembly from the reference angle for later composite items.
