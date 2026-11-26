# CottageGardenDecor: reference review, batch 2 (2026-11-25)

Every preview `art/CottageGardenDecor/Previews/FMS_Garden_<ID>_Preview.png` compared with `planning/CottageGardenDecor/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.
Status: FINAL, all 10 batch-2 items reviewed (STR-02, STR-03, STR-04, STR-05, STR-07, MOD-07, MOD-08, MOD-09, FLB-02, FLB-03); MOD-08 re-checked after Fix 1.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 1 | MOD-09 |
| 🟡 Pass with notes | 9 | STR-02, STR-03, STR-04, STR-05, STR-07, MOD-07, MOD-08 (after Fix 1), FLB-02, FLB-03 |
| 🔴 Fix | 0 | Silhouette, signature feature or proportions clearly off (MOD-08 was 🔴 in pass 1, closed in pass 2) |
| ❓ Decision | 0 | Deliberate deviation; the owner decides |

Cross-cutting issues (batch 2, and rules for batch 3):
1. Palette vs references: stone greyer, white cooler, light wood paler than the references (all batch-2 items). Palette decision, not a defect; keep the two-tone splits visible.
2. Functional sizes win over the pictures: arch opening 1.20, bench seat 0.45, pond edge/water contract, pergola heights 2.24 / 2.46 / 2.62. Accepted everywhere.
3. Over-budget is acceptable only where the spec allows it and the builder notes explain it (STR-02 1.94x for the scrolls). Under-budget is fine when the reference is equally simple (STR-04/05, STR-07). A budget too tight to build the reference's signature is a FIX with a stated budget raise (MOD-08, 60 -> 80).
4. Thin iron/slat members: STYLE minimums (wrought rods >= 0.03, slats >= 0.03, posts >= 0.08-0.10) are the rule, not an exception request. STR-02 is the anchor for FUR-03/04 iron: 8-sided rod 0.040 frame / 0.030 scroll bars, slot 13, `s_curve()` S-scroll; curls >= 0.10 across; check at 128 px.
5. Wood slot: slot 0 `#B5835A` is the series wood for arch, pergola, obelisk, arbor seat; slot 2 is for lattice slats only if a model needs a second tone. STYLE.md row for slot 2 still lists the obelisk: update it (coordinator action).
6. Stone modules (pond edge, corner, beds) share cells 11/12 (atlas A) and 14/15 (atlas F); for corner or end pieces, the masonry pattern must continue the neighbour (courses, joint width, tone alternation), not collapse into plain slabs.
7. Planted variants (`_Planted`) have no previews in `art/CottageGardenDecor/Previews/` and are judged from check renders; for Asset Store media use `_Planted`, and add previews at assembly.
8. Batch-3 watch list: FUR-03/04 must reuse the STR-02 iron wording; FUR-01/02/05 furniture must differ from Farm Market `FMS_Deco_Bench_Plank` (check seat 0.45, member >= 0.08); PLT-04..06 and TOP-01..04 organics keep rose_bloom_v2 / 80-tri domed drops / cups tilted toward the viewer and no brown lollipop stalks, check 128 px; WTR-01/02 water uses the opaque slot 15 and the same stone cells as WTR-03/MOD-07; ORN-01..05 small ornaments: check 128 px and the 0.03 minimum detail.

## Consolidated Unity-import check list (Э8, not verifiable in this review)
Under the series assumption that Unity's FBX import negates X (Blender (x, y, z) -> Unity (-x, z, -y)); verify one asset of each kind on the first import:
- MOD-06 arc quadrant: must lie in +X/+Z with ends at (1,0,0) and (0,0,1); else mirror in build.py or rotate the prefab by -90 degrees.
- MOD-08 corner: built at Blender x >= 0, y >= 0 = Unity X <= 0, Z <= 0; verify the edge|corner join; else mirror or rotate 90 degrees.
- MOD-07 edge: basin interior towards Unity +Z; MOD-09 water slab raised 0.34 inside the mesh with the pivot on the ground (no prefab offset).
- STR-05 bay: built at Blender -X; posts must land at Unity X +3.0 and beams at +0.25 ... +3.25 (placement STR-04 + 1.5, then +3.0); else rotate the bay prefab 180 degrees about Y.
- FLB-02 L-shape: missing quadrant at Unity X > 0, Z > 0; if flipped, mirror the prefab (rotation does not help). FLB-02/03 join with FLB-01: check one run.
- STR-01 `_Gate`: hinge on the viewer's left post; open angle clamped to 90 degrees. PLT-02, MOD-05: same X-flip assumption.
- PLT-03 garland: 0.54 high decoration, no collider; arch with garland about 2.94 m, collider 2.4 m; on STR-04/05 it sits on the beam top at 2.46 and its foliage passes through 3-4 rafters.
- Collider openings: STR-06 clear 1.27 x 2.1, STR-01 opening 1.2 x 2.1, STR-02 clear 1.20 (width 1.48 in a 1.5 m wall gap), STR-03 clear 1.56; STR-03 and STR-04 ship LOD1 (check LOD group setup).
- Catalogue sizes to correct: STR-02 1.48 x 0.46 x 2.50; STR-05 extent 3.00 x 3.50 x 2.62; STR-03 crown 2.25 with slats to 2.30; MOD-08 budget 80.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|
| none open | | | MOD-08 Fix 1 (budget 60 -> 80, pinwheel blocks) is done, see the second-pass section |

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|
| none | | | |

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| FLB-03 | Bed_Round (+ _Planted) | Soil flatter and one-toned vs the reference, stone greyer, joints taper; planted: some soil visible between the outer clumps. See the FLB-02 / FLB-03 section. |
| FLB-02 | Bed_Corner (+ _Planted) | Soil flatter and one-toned vs the reference, stone greyer; planted: lilac spikes short. See the FLB-02 / FLB-03 section. |
| MOD-07 | Pond_Edge | Block ends set back 6 mm, lighter/greyer palette, reference shows blocks running round the end. See the pond kit section. |
| MOD-08 | Pond_Edge_Corner | After Fix 1: pinwheel masonry reads, tone contrast is low and the layout differs slightly from the reference. See the pond kit section, pass 2. |
| STR-07 | Obelisk | Posts and top cluster chunkier than the reference, collar 0.19, slot 0 wood instead of spec slot 2, `_White` has no preview. See the STR-07 section. |
| STR-05 | Pergola_Bay | Rafter ends cut (reference plain), symmetric overhang vs the reference's uneven one; bay built at Blender -X (Unity X-flip to confirm). See the STR-04 / STR-05 section. |
| STR-04 | Pergola | Posts 0.18 / rafters 0.08 (reference, above spec minimums), uniform rafter overhang, lighter tone contrast. See the STR-04 / STR-05 section. |
| STR-03 | Arbor_Bench | Taller/narrower than the reference, crown 2.25 with slats to 2.30, white cooler than cream, bench legs collapse in LOD1. See the STR-03 section. |
| STR-02 | Arch_Iron | Scrolls smaller and sparser than the reference (0.10 x 0.29 vs about 0.15 x 0.38), taller/narrower proportions, 2722/1400 tris. See the STR-02 section. |

## ✅ Pass
- Modules: MOD-09 (Pond_Water)

## STR-02 Arch_Iron (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-02_STR-02.png`; full preview and STR-06 preview also viewed. No variants.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `STR-02.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: tall rounded hoop on four rods with spiked feet, two frames with cross-rods across the crown, lower spreaders and a finial; reads as a wrought-iron rose arch, not as a frame or a gate |
| Signature feature (scroll curls) | pass with notes: 8 S-scrolls with a visible eye, in the right places (outer side of the uprights, under the springing); smaller and sparser than the reference's large round curls, they read as small clips rather than a decorative filigree; still recognisable |
| Proportions | pass with notes: 1.48 x 0.46 x 2.50 m, hoop rise 0.50 (semi-ellipse, flatter like the reference); a little taller and narrower than the reference picture; functional opening 1.20 wins (PIPE-04) |
| Colour / palette | pass: single slot 13 `#3A3A3F`, same cell as the STR-06 spire; matte, no highlights |
| Readability at 128 px | pass with notes: hoop, uprights, cross-rods and spikes read clearly on the thumbnail; scrolls shrink to small dark marks but remain visible as ornaments |
| Style match | pass: flat shading, 8-sided rods, chunky enough next to STR-06 and STR-01 |

Deliberate deviations judged:
- Rod thickness: frame 0.040, scroll bars 0.030. Not an exception to STYLE: STYLE says wrought rods >= 0.03 (spec 0.035 nominal), so both satisfy it. ACCEPT; the thinner bars are what let the 0.10 curls keep an eye.
- Uprights at X +-0.62 (spec +-0.60), width 1.482 vs 1.4: ACCEPT, it gives the 1.20 clear opening and still fits the 1.5 m wall gap (9 mm per side). Record the new size in the catalogue/spec.
- Semi-elliptic hoop rise 0.50 instead of half-round r 0.60: ACCEPT, closer to the reference and keeps the finial inside 2.5.
- Scrolls smaller than the reference: ACCEPT, limited by the 1.5 m gap and the budget. Optional: none required.
- Budget 2722 vs 1400 (1.94x): JUSTIFIED. The spec explicitly allows up to about 2x for scrolls with a note, and the note is present with a breakdown (frame and parts 834, scrolls 1888). The scrolls are the signature, and 8-sided bars are the anchor for FUR-03/04. Optional trim if the budget matters elsewhere: corner scrolls with 6-sided bars (-208) or 6 segments per side curl (-128); not needed.
- PLT-03 only perches on the crown (it is straight, the hoop is round, ends hang above the shoulders): ACCEPT, it reads as a wreath on top; STR-01 remains the better garland carrier. Plant_L/R sit on the outer upright faces; roses swallow some outer scrolls: accepted by the builder, fine.
- Spreaders at z 0.30 and extra ones at z 1.85, feet with a collar: accept (from the reference).
- Snap numbers (clear passage 1.200, width 1.482, nothing below 0) from the builder notes, not re-measured here.

Notes (optional): the iron looks a touch lighter than in the STR-06 spire in the preview only because of the thin lit faces; it is the same cell.

## STR-03 Arbor_Bench (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-03_STR-03.png`; full preview also viewed. LOD1 only from the builder notes (check render not opened).

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `STR-03.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: closed back and sides, open front, arched rafter top with cross slats, bench inside; reads as a garden arbor with a bench at 128 px |
| Signature feature (bench built into the lattice arbor) | pass: light-wood seat spans post to post and touches the back lattice, lattice starts at seat height; clearly not a free-standing bench |
| Proportions | pass with notes: 1.8 x 0.8 x 2.3 reads taller and narrower than the squat reference; contract size wins (PIPE-04). Crown rise slightly more than the reference, still a clear arch |
| Colour / palette | pass: white slot 10 plus light-wood seat slot 0; cooler than the cream reference (palette decision, not a defect) |
| Readability at 128 px | pass: lattice diamonds, arch and orange seat are readable; slats are open at the top |
| Difference from Farm Market `FMS_Deco_Bench_Plank` | pass: the model is read as an architectural structure (posts, lattice, rafters) with a white bench base; a plank bench is only a part of it |
| Match with STR-01 / MOD-01 | pass: same 45 degree lattice, slat 0.05, gap 0.10, rim, post wording and white slot 10 |

Deliberate deviations judged:
- Crown 2.248 (slat tops 2.30), seat 1.58 x 0.62 x 0.07, 4 legs 0.09 with rails, slats 0.77 long: ACCEPT (functional contact with posts and back lattice, reference shows the same).
- Cross slats stand about 6 cm proud of the rafters: ACCEPT, they read as pergola slats and keep the top open, as in the reference.
- Clear width 1.56, seat top 0.45: functional, ACCEPT.
- LOD1 bench legs collapse to wedges, 638 tris: ACCEPT (distance LOD).
- Tris 1276/1600: fine. SNAP numbers taken from the builder notes, not re-measured.

## STR-04 Pergola and STR-05 Pergola_Bay (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-04_STR-05.png` (both on one sheet); both full previews viewed. LOD1, SNAP numbers and the PLT-03 beam mount are from the builder notes, not re-measured.

Verdicts: STR-04 🟡 PASS with notes; STR-05 🟡 PASS with notes. No FIX, so no "## Fix 1" written.

| Criterion | STR-04 | STR-05 |
|---|---|---|
| Silhouette | pass: four square posts, two beams with overhang, 7 rafters across with open gaps; reads as an open garden pergola, not a stall or a gazebo | pass: two posts at the far end, open joining end, 6 rafters; reads as an extension bay |
| Signature feature (rafter row, beams, rafter end cut) | pass: rafters rest on the beams, stepped end cut with a dark end face is visible and gives the only detail | pass: same |
| Proportions | pass: 3.5 x 3.5 x 2.62; posts 0.18, rafters 0.08 match the reference mass better than the spec minimums | pass: 3.0 x 3.5 x 2.62 (the catalogue 3.25 is the far beam end) |
| Colour / palette | pass: light wood slot 0 (same as STR-01 arch), dark slot 1 on the cut ends; the references are a more orange wood, the palette decision applies | pass |
| Readability at 128 px | pass: rafter row and beams stay readable | pass |
| Style match | pass: flat matte, chunky members as STR-01/STR-06 | pass |

Richness vs budget (332/1600, 248/1000): NOT too sparse. The references are equally simple (plain posts, beams and rafters, no brackets, no braces, no carving), so there is nothing measurable missing. The model already adds the rafter end cut that is not in the reference (STR-05 reference has plain ends). The spec forbids bracing and carving finer than 0.03, so the unused budget is not a defect.

Deliberate deviations judged:
- Posts 0.18 and rafters 0.08 instead of 0.16 / 0.06: ACCEPT (reference measured, above the spec minimums, snap centres unchanged).
- Rafter overhang 0.25 on both ends, whereas the reference front ends are almost flush: ACCEPT (spec; reference inconsistent).
- Bay keeps the STR-04 end cut though its reference is plain: ACCEPT, a module run reads as one pergola.
- 5 mm seats of posts and rafters (no coplanar faces), functional heights 2.24 / 2.46 / 2.62 exact: ACCEPT.
- Wood consistency: STR-04/05 use slot 0 exactly like STR-01 `_Wood` and the STR-06 deck; the STR-03 arbor and STR-01 `_White` are white (slot 10), so a pergola next to a white arch is a deliberate contrast. STR-07 not compared here (not yet in the batch).
- PLT-03 on the beam top at 2.46: from builder notes, the foliage passes through 3-4 rafters; decoration, no collider; accepted.

Unity import checks flagged (for Э8, not verifiable here):
- STR-05 is built at Blender -X on the assumption that Unity's FBX import negates X: after import the bay posts must land at Unity X +3.0 and the beams at +0.25 ... +3.25. If they land at -3.0, rotate the prefab 180 degrees about Y (the module is symmetric in Z). Same X-flip assumption as MOD-06 and the STR-01 gate; verify these together on the first import.
- Placement: STR-05 = STR-04 pivot + (1.5, 0, 0); next bay +3.0.
- Catalogue note: STR-05 extent is 3.00 x 3.50 x 2.62, not 3.25.

## STR-07 Obelisk (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-07_STR-07.png`; full preview also viewed. `_White` FBX exists; not visually checked (no variant preview).

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `STR-07.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: tall four-sided pyramid of leaning posts with a collar and a faceted ball; same from all sides, reads as an obelisk at 128 px |
| Signature feature (bands, ball) | pass: three square bands with visible corner ears, faceted ball on a collar |
| Proportions | pass with notes: 0.60 x 0.60 x 1.90; posts 0.08 and the top cluster (collar 0.19 + ball 0.16) are heavier than the slender reference (ball about 0.13-0.15 there); chunkier is the STYLE direction |
| Colour / palette | pass with notes: slot 0 light wood, a little paler than the orange reference; see the slot decision |
| Readability at 128 px | pass: posts, bands and ball readable |
| Difference from Farm Nature `FMS_Bed_Trellis` | pass: a free-standing 3D four-sided pyramid with open sides, no flat panel or lattice |
| Style match | pass: flat matte faces, same chunky wooden wording as STR-01 and STR-04 |

Slot decision: ACCEPT slot 0 (light wood `#B5835A`) for the base. STYLE and the spec list slot 2 (`#9C6B44`) for the obelisk, but slot 0 is the wood of the STR-01 arch, the STR-04/05 pergola and the STR-06 deck, and it is closer to the reference colour. An obelisk is placed next to arches and pergolas, so one wood tone is better for series consistency; slot 2 would read as a different, darker wood. The base stays on slot 0 and `_White` stays on slot 10. Action for the coordinator: update the STYLE.md slot 2 row (remove "obelisk") and the STR-07 spec so the docs match; one constant in the build script if the owner prefers slot 2 later.

Deliberate deviations judged:
- Collar 0.19 x 0.19 x 0.07 (z 1.70-1.77) instead of 0.14 x 0.14 x 0.10: ACCEPT, 0.14 cannot contain 0.08 posts without piercing; the reference collar is nearly as wide.
- Ball subdivision 2 (80 tris) instead of 1: ACCEPT, allowed by the spec ("1-2"), reads as faceted and not a smooth sphere.
- Bands at z 0.36 / 0.90 / 1.35-1.40 measured from the reference: ACCEPT.
- Post tops buried 3 cm in the collar: ACCEPT.
- Tris 236/500: fine; the reference is equally simple, so nothing is missing.
- `_White` (slot 10, same mesh) not visually checked; verify once at assembly.

## MOD-07 Pond_Edge, MOD-08 Pond_Edge_Corner, MOD-09 Pond_Water (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_MOD-07_MOD-09.png` (all three on one sheet); MOD-08 preview viewed in full. SNAP results (edge|edge, edge|corner, closed 2x2 and 3x2, water cover, 0.07 below the edge) are from the builder notes, not re-measured.

Verdicts: MOD-07 🟡 PASS with notes; MOD-08 🔴 FIX; MOD-09 ✅ PASS.

| Criterion | MOD-07 | MOD-08 | MOD-09 |
|---|---|---|---|
| Silhouette | pass: low rectangular stone wall with a slab coping; formal raised basin edge, clearly not the natural Farm Nature pond | pass: square block with coping, same height 0.45 | pass: flat square slab |
| Signature feature | pass: 2 courses of 2 staggered blocks, two tones, light coping | FAIL: one quoin per course gives two stacked flat slabs (dark below, light above) with a visible seam; no block joints, no stagger; it does not read as masonry and does not match MOD-07 beside it (the reference shows 4 blocks with joints) | pass: opaque flat blue slab, edges flat |
| Proportions | pass: 1.0 x 0.37 x 0.45 | pass: 0.37 x 0.37 x 0.45 | pass: 1.0 x 1.0 x 0.04 |
| Colour / palette | pass with notes: stone greyer, coping paler/cooler than the beige reference (palette); light blocks keep the two-tone | pass with notes: same | pass: slot 15 `#4A78A8`, lighter in the render than the reference; same cell as the other water |
| Readability at 128 px | pass | pass with notes: reads as a plain box with a cap | pass |
| Style match | pass: same cells and wording as MOD-03 | pass for colours; not for the block pattern | pass |

Pond kit differs from Farm Nature natural ponds: pass. Raised rectangular stone basin with coping and an opaque flat water tile; no organic outline.

MOD-08 decision: FIX with a raised budget, 60 -> **80 tris**. The reason is the corner is the only place in a pond where the masonry is seen from two faces; a smooth two-slab corner will stand out in every assembled pond (4 per pond) and the cost is only +24 tris per piece. The builder already measured that about 80 tris are enough, so the budget change is small and no snap change is required. See `MOD-08.3d.md` Fix 1.

Deliberate deviations judged (MOD-07 / MOD-09):
- Light blocks 2 of 4 instead of "about one in four": ACCEPT (reference wins; the two-tone is visible).
- Block ends 6 mm short of the end faces, ends flat and sharp: ACCEPT (butt contract; the spec forbids relief on ends).
- Light block adjacent to the coping merges more than in the reference (same cell 11): ACCEPT.
- MOD-09 ripple +-5 mm invisible, border vertices 0.38: ACCEPT (the reference is a flat slab too; the contract forbids a step).
- Tris 76/120, 36/50: fine.

Unity import checks flagged (for Э8, not verifiable here):
- MOD-08 is built at Blender x >= 0, y >= 0, i.e. Unity X <= 0, Z <= 0 under the X-flip assumption (same as MOD-06, STR-01 gate, STR-05). Verify one corner on the first import; if flipped, mirror the assembled corner or rotate the prefab 90 degrees.
- MOD-07: pivot at the middle of the inner face; basin interior towards Unity +Z of the edge piece, per the contract; check with the first edge piece placed.
- MOD-09: slab is raised 0.34 inside the mesh with the pivot on the ground; the prefab must not add an offset.

### MOD-08 pass 2 (after Fix 1, 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_MOD-08_MOD-08.png`; new preview viewed in full. 80/80 tris, SNAP (edge|corner, 2x2, 3x2), re-import and headless equality are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes (Fix 1 closed, no Fix 2).

| Criterion | Result |
|---|---|
| Silhouette | pass: block with a flat coping, same 0.45 top as MOD-07 |
| Signature feature (masonry) | pass: each outer face now shows a quoin and a shorter face block per course, with joints and the pinwheel stagger; tones alternate between courses (dark bottom quoin with a light block, light top quoin with a dark block); continues the MOD-07 masonry |
| Proportions / pivot / snap faces | unchanged |
| Colour / palette | pass with notes: tone contrast low and stone greyer than the beige reference; the light top quoin merges with the coping (same cell 11) as before |
| Readability at 128 px | pass: no longer a plain box |

Notes (optional): the layout differs from the reference (the reference has the long dark block on the top-left face and the light block at the corner bottom); not required.

## FLB-02 Bed_Corner and FLB-03 Bed_Round (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_FLB-02_FLB-03.png` (base previews); `_Planted` judged from the headless check renders `%TEMP%/assetnew_check/FLB-02/FLB-02_Planted_check.png` and `.../FLB-03/FLB-03_Planted_check.png` (same camera as the previews, not files in `art/CottageGardenDecor/Previews/`). LOD1 (1138 / 1008) and SNAP (incl. joins with FLB-01) from the builder notes, not re-measured.

Verdicts: FLB-02 base 🟡, `_Planted` 🟡; FLB-03 base 🟡, `_Planted` 🟡. No FIX, so no "## Fix 1" written.

| Criterion | FLB-02 | FLB-03 |
|---|---|---|
| Silhouette | pass: 2 x 2 L-shape with one missing quadrant, stone kerb with light tops; reads as a corner bed | pass: round bed, 16-sided stone ring, light tops; reads as a round formal bed |
| Signature feature | pass with notes: kerb blocks with joints, soil inside; soil is much flatter and one-toned than the reference's lumpy facets (contract crown 0.20 / rim 0.16 limits slopes) | pass with notes: same; blocks taper (no parallel joint) to keep the bbox exact: not visible |
| Proportions | pass: 2.0 x 2.0 x 0.25, planted 0.70 | pass: O2.0, planted 0.80 |
| Colour / palette | pass with notes: stone greyer than the beige reference (palette); two-tone tops kept | same |
| Readability at 128 px | pass | pass |
| Consistency with FLB-01 | pass: same kerb height, border, stone cells 14/15, soil cell and flat shading | pass |

`_Planted`:

| Criterion | FLB-02 | FLB-03 |
|---|---|---|
| Reads as a planted cottage bed | pass: 10 green domed clumps with pink, white and yellow blooms, spikes in the corner square; clumps stay inside the kerb, front soil mostly covered | pass: tiered layout (lilac centre, pink/white ring, yellow outer ring), a clear radial composition |
| Style match with FLB-01 / PLT-01 | pass: same 80-tri domed drops, same three-green split, flat 5-petal cups now tilted toward the viewer (better than the FLB-01 lollipop look), no brown stalks | pass |
| Crown | pass with notes: lilac spikes only about 0.2 above the foliage (0.70 limit), a small crown; the corner is still the tallest | pass: spikes reach 0.80, a clear crown |
| Gaps | pass: a single filler at the right arm end stands a bit alone | pass with notes: some soil visible between the outer yellow clumps; acceptable, gives a legible tiered layout |

Deliberate deviations judged:
- Soil relief subtler than both references: ACCEPT, no FIX (as FLB-01; the contract caps soil at 0.20 and the kerb at 0.25). Optional: lower the valleys to about 0.12-0.14 for clearer facet tones, no tri cost.
- Stone greyer: accept (palette).
- FLB-03 tapered joints: ACCEPT, the exact bbox at R 1.0 matters for round-bed snaps.
- Soil top 34 / 28 tris: accept.
- `_Planted` tris 2024/2200 and 1766/1800: within budget.
- Previews are the base bed (one per ID); Asset Store media should use `_Planted`, as with FLB-01.

Unity import checks flagged (for Э8, not verifiable here):
- FLB-02: the L is built with the missing quadrant at Blender x < 0, y < 0, which is Unity X > 0, Z > 0 under the X-flip assumption. Verify once together with MOD-06, STR-01, STR-05, MOD-08; if flipped, the prefab needs a mirror (do not rotate: the L is not symmetric under rotation by 90 degrees to the contract).
- FLB-02 and FLB-03 join with FLB-01 by their kerb faces; check one assembled run after import.

## How to fix
- Batch 2 needs no further fixes. MOD-08 Fix 1 was done and passed the second sheet pass (80/80 tris, SNAP OK, new preview).
- Optional polish only (see per-item notes); after any later fix: re-export, re-import verify, new preview, second sheet pass.
- After any later fix: re-export, re-import verify, new preview, second sheet pass; append a results table below.
