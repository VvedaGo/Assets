# CottageGardenDecor: reference review, batch pilot (2026-11-25)

Every preview `art/CottageGardenDecor/Previews/FMS_Garden_<ID>_Preview.png` compared with `planning/CottageGardenDecor/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.
Status: WTR-03, PLT-01 and STR-06 reviewed (pilot complete; PLT-01 awaits its fix).

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | Close to the reference, no edits |
| 🟡 Pass with notes | 3 | WTR-03, STR-06, PLT-01 (after pass 2) |
| 🔴 Fix | 0 (PLT-01 was FIX in pass 1, cleared in pass 2) | Silhouette, signature feature or proportions clearly off |
| ❓ Decision | 0 | Deliberate deviation; the owner decides |

Cross-cutting issue: the pack stone (slots 11/12) renders greyer and lower-contrast than the references (references are warmer/beiger, with a clearer plinth vs limestone split). This is a palette effect, not geometry. Next stone models (WTR-01, WTR-02, ORN-01, ORN-03) should keep the palette but keep the 2-tone split (slot 12 on plinths/inner faces) as visible as possible; do not retint to chase the reference. Spec numbers in the .3d.md catalogue (heights, thicknesses) were estimates; the references win (PIPE-04), so builders should measure them first, as the WTR-03 builder did.

## 🔴 Fix
| ID | Model | What is wrong | What to do (with numbers) |
|---|---|---|---|
| none | | | |

## ❓ Decision
| ID | Model | Deviation | Options |
|---|---|---|---|
| none | | | |

## 🟡 Pass with notes
| ID | Model | Small difference |
|---|---|---|
| WTR-03 | Birdbath | Matches the reference silhouette on the sheet: faceted bowl with shallow blue water, flared collar, knob, tapering stem, stepped foot and plinth; reads as a birdbath without colour and clearly at 128 px. Notes below. |

WTR-03 deliberate deviations, judged:
- Height 0.70 vs 0.85: accepted. The reference is h/w about 1.37 at the 0.60 footprint (builder measured model 1.370); the 0.60 m footprint limit was kept. The sheet shows the same proportions.
- 12-sided bowl / 10-sided pedestal: accepted. It matches the reference facets, 336/350 tris, closed shell. Under the 12-16 segment allowance for large bowls in STYLE.
- Stem Ø0.10-0.13 vs spec waist ≥ Ø0.16: accepted, PASS-with-notes, no FIX. STYLE's actual minimum for posts and rods is ≥ 0.10 (the 0.16 waist is a catalogue number, not STYLE); the stem is at or above 0.10 everywhere, and the reference stem is equally slim (0.17-0.21 of bowl width). The stem is the thinnest part but is still readable in the sheet and the 128 px thumbnail. Optional: stem and trumpet radii ×1.25 (builder says no tris cost) would give ≈Ø0.13-0.16 and match "slightly fat" STYLE intent; not required. If the owner wants a chunkier look, that is a taste call, not a blocker.
- Plinth Ø0.33 vs 0.40, no separate chamfer band, bottom face kept: accepted; follows the reference, keeps mesh closed.
- Stone greyer than the reference: accepted as palette. Water slightly lighter and more saturated than the reference's deeper blue (render lighting; slot 15 is #4A78A8 as specified); fine. Collar band has lower contrast than the reference; minor.
- Open item from STYLE.md: comparing #A7A39A with Nature rocks is not possible (no Nature previews in this branch); leave to the owner.

## ✅ Pass
- none yet

## How to fix
- No fixes needed for WTR-03; it can serve as the stone anchor for WTR-01, WTR-02, ORN-01, ORN-03.
- After any later fix: re-export, re-import verify, new preview, second sheet pass; append a results table below.

---

# PLT-01 Rose Bush (review 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-01_PLT-01.png`; full preview also viewed. Variants `_Pink` and `_White` FBX (+ .fbm) exist in `art/CottageGardenDecor/Meshes/`; not visually checked (no previews).

## Verdict: 🔴 FIX

Key question: at 128 px it does NOT yet read as a rose bush. It reads as a small tree: one thick trunk in the middle carrying 8 separate flat-topped "mushroom plates" on bare sticks, with large sky gaps. The reference is a dense, overlapping mass of domed leaf drops on a fan of curved stems (vase-shaped, wide at the top, clusters touching and hiding most stems). Palette, flat shading, faceting and 3 cells of green match the series; the stem fan and bloom count are right.

| Criterion | Result |
|---|---|
| Silhouette (vase bush) | fail: gaps between clusters, central trunk, reads as a tree; vase width comes only from two outliers (TR, ML) |
| Signature feature (red cup blooms above foliage) | partial: 10 blooms, good colour and placement; cups are taller than wide with a tapered green neck and read as tulips/cones at 128 px |
| Proportions | partial: 0.84 x 0.64 x 1.0 m fine; clusters Ø0.24-0.28 are too small relative to the bush (reference clusters about 1.3x larger and overlapping) |
| Colour / palette | pass: atlas F foliage 0/1/2, cup 4, bud 5, bark 13; top light-green, side mid, underside dark |
| Readability at 128 px | fail as above (stems visible, but the "bush" is not) |
| Cluster shape | fail: the cut lower half plus a wide flat cap give hexagonal plates/lampshades, not domed drops (reference: round-topped drops, rounded underside) |
| Deliberate deviations | 10 blooms: accepted (matches reference). Bloom 44 tris closed shell: accepted. Depth 0.64: accepted. Top bloom tilt 8-12: accepted. Cluster 38 tris with the lower half removed: accepted in principle, but the result is the cause of the plate look (see fix); budget 964/1000 |

## Fix list (PLT-01) — written to prompts/PLT-01.3d.md as Fix 1
1. Clusters: D 0.26 -> 0.34-0.38 (upper tier 0.36, lower 0.34, top 0.32); lets neighbouring clusters overlap/interpenetrate by 0.03-0.06 (reference does). Zero tri cost.
2. Cluster profile: height 0.72 D -> 0.85 D, top dome (cap not flat; keep the widest ring about 40 % up from the base), underside rounded inward as before.
3. Stems: fan out, not a central trunk: base spread Ø0.2, lean 15-30 deg for all 6, bend at the kink 0.42-0.45; outer clusters sit at r 0.28-0.36.
4. Blooms: cup rim Ø0.10 keep, cup height 0.06 -> 0.045, bottom Ø0.06 -> 0.07; calyx neck visible length <= 0.025 (the rest buried); top three tilt 10-15 deg.
5. Keep: 964 tris max (1000), 10 blooms, palette, variants (rebuild `_Pink`/`_White` too, re-export, new preview, second sheet pass).

## Judgement on the primitives approach for the other 9 plant/topiary models
The approach itself (faceted drops + cup blooms, flat atlas, 2-3 green cells) is good enough and fits the series; the issue is the generator parameters, not the method. Before the other 9 reuse the generator, PLT-01 must pass: clusters must be big, domed and overlapping into a mass (reference-like), not plates on sticks. Shared lessons: (a) do not cut the lower half flat and widen the cap; (b) measure cluster size against the reference, not the spec number; (c) check the 128 px thumbnail for "tree" vs "bush" silhouette; (d) cup blooms must be wider than tall. Topiary (sphere/cone) models are lower risk.

---

# STR-06 Hexagonal gazebo (review 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-06_STR-06.png`; full preview also viewed. Reference is near-frontal, preview is a 3/4 view, so heights are compared by the builder's measured numbers, not by eye on the sheet.

## Verdict: 🟡 PASS with notes

Silhouette (hexagonal hip roof, white posts, open entrance with steps), signature features (two-tone stepped shingle rows, white hip ribs, iron spire with ball, railings with real gaps, 3 benches, open entrance) all match the reference and read clearly at 128 px: red roof, white frame, open front. No walls, no door, no glass.

| Criterion | Result |
|---|---|
| Silhouette | pass |
| Signature feature (shingled hip roof, open railed hex frame) | pass; tile rows are stepped and two-tone as required, no diagonal stripes |
| Proportions | pass with notes (squatness, below) |
| Colour / palette | pass: atlas A white 10, wood 0/1/2, roof 5/14/6, iron 13; roof is a brighter red than slot 14 alone (builder used 5 and 14, reference tiles are bright), acceptable, stays in the palette |
| Readability at 128 px | pass |
| Style match with WTR-03 | pass: same atlas A, flat shading, matte, same chunky bevel-light faceting; limestone vs white paint vs wood tones are clearly separate cells |

Deliberate deviations:
- Squatness (model about 12-15 % taller than the reference): ACCEPT with notes, no FIX. The catalogue height is 4.0 m (kept), the clear opening must be ≥ 2.1 m for the collider note (met: 2.10), and a 1.7 m clear height in the reference would not let characters pass. The 3/4 view vs frontal reference exaggerates the difference on the sheet. If the owner still wants it squatter, the builder note gives the recipe (lower the cap/beam/soffit/fascia/peak/spire by about 0.3 m), but that would break the 2.1 m collider requirement, so we do not recommend it.
- Steps 0.33 deep, X 3.58 (catalogue 3.9, -8 %): accepted, within the spec's allowance ("reduce the step depth"), matches the reference tread depth.
- Y 3.58 vs 3.4 (+5.4 %): accepted (ribs and overhang); marginal over the ±5 % rule, record in spec.md.
- Posts 0.18, capitals 0.24, balusters 0.06x0.05, seat 0.08: accepted, thicker than the spec, matches the reference and STYLE (≥0.10 posts, chunky members).
- Entrance clear width 1.27 vs ≥ 1.40: accepted with a note for Э8: the collider opening should be 1.27 wide x 2.1 high; update the spec/collider number (the spec's own geometry gives 1.31 at best).
- LOD0 2314/5000, LOD1 1156 inside the FBX (5 parts + 5 `_Low1`, 3470 tris total): fine; not Unity-verified here.
- Tile tone slots 5/14 instead of 14/6: accepted.

Visible nitpicks (optional): the shingle courses at the roof edge show a slightly jagged stepped fascia; the 2 benches visible look blocky; the reference has small capital brackets. None blocks.

## Cross-cutting notes for structures (STR-xx and other big models)
- A catalogue number can conflict with a collider rule (clear height 2.1 m, clear width 1.40 m): decide the collider opening first, then derive the proportions; the reference alone is not authoritative for walk-through openings.
- Check bbox against the catalogue ±5 % early; ribs and overhangs add to the span.
- Split large models into role-based mesh objects (base / frame / railings / furniture / roof) so `make_lod1.py` thins balusters in groups; STR-06 shows this works.
- Use real stepped shingle courses with half-tile offset and a random two-tone run; avoid regular alternation (diagonal stripes).
- Members of 0.18 posts and 0.06 balusters read well at 128 px; keep this thickness (STYLE minimums are lower bounds).

---

# PLT-01 — pass 2 (after Fix 1, 2026-11-25)

Sheet rebuilt and the full preview viewed. `_Pink`/`_White` FBX were not visually checked (no previews).

## Verdict: 🟡 PASS with notes

Key test at 128 px: it now reads as a leafy flowering bush with red rose cups, not a tree on sticks and not a flat-topped plate stack. The clusters are large, domed and overlapping into a mass; the narrow stem base widening upward gives a vase-like outline; 10 red cups sit on top of the foliage. It is still rounder and heavier than the reference vase, and not confusable with Farm Nature round bushes only because of the visible stem fan at the base and the red blooms.

| Criterion | Result |
|---|---|
| Silhouette | pass with notes: crown reads as a mass on a narrow stem base (vase-ish); rounder than the reference, front clusters hide most of the stem fan |
| Signature feature (red cup blooms above foliage) | pass: cups are now wider than tall; 10 present, readable red against green |
| Proportions | pass with notes: clusters Ø0.32-0.36 correct; blooms look a little small against the larger clusters, 2-3 lean sideways/hide partly in the cluster |
| Colour / palette | pass |
| Readability at 128 px | pass: green mass + red dots + brown base |
| Cluster shape | pass: domed drops, 0.80 D accepted (0.85 looked like eggs) |

Deviations judged:
- Width 1.01 x 0.69 x 1.05 m (catalogue 0.8 x 0.8 x 1.0): accepted. It follows the reference (wide upper tier, which carries the vase look); the extra 0.2 m is acceptable for a garden bush. Record it in spec.md / catalogue as 1.0 x 0.7 x 1.05; the build placement in the demo needs 1.0 m clearance.
- Dome 0.80 D instead of 0.85: accepted.
- Straight stems instead of curved: accepted (low-poly series, budget 964/1000).
- Stems mostly hidden in 3/4: accepted; visible at the base and between top clusters.

Optional (no re-review needed): lift the two lowest front clusters about 0.05 m or move them 0.03 outward to show more of the stems; raise cup rim Ø to 0.10-0.11 for stronger bloom read. Not required.

## Final note for the plant category (PLT-02/03/06, TOP-01_Rose and others)
- The generator is approved as the series anchor: big domed overlapping drops (D 0.32-0.38, height 0.80 D), flat shading, 3 green cells by normal, cup blooms wider than tall with a short calyx neck.
- Check at 128 px before submitting: green mass must show stems/vase base and the flower colour; blooms Ø0.10 minimum and not hidden by neighbouring clusters.
- Measure sizes against the reference; the catalogue width may grow (here +25 %) when the reference is wider than tall.
- Colour variants only remap UV cells; verify the _Pink/_White FBX exist (done for PLT-01) and review one variant preview when the variants of PLT-02/03 are built.

---

# PLT-01 — pass 3 (after Fix 2, budget 2000 tris, 2026-11-25)

Sheet rebuilt and the full preview viewed. `_Pink`/`_White` not visually checked.

## Verdict: 🟡 PASS with notes (clearly better than pass 2)

Fix 2 item by item:
| Item | Result |
|---|---|
| 1 Vase silhouette, stem fan visible | pass with notes: the stem fan is now clearly visible below the crown (about 0.3 m, curved and branching, with a gap between the left and right branches); the crown is still a rounded mass, not an open vase. Accepted. |
| 2 Curved stems, 6-7 stems, side shoots | pass: bent branches, tapered, 2 side shoots carrying blooms (one visible right, one left) |
| 3 Bumpier clusters, 8-9, tufts | pass with notes: clusters are bumpier and overlap; 80 tris instead of 90-110 accepted (deliberate, to stay within 2000); 3 leaf tufts are tiny and mostly invisible at 128 px, so they barely break the outline. Optional |
| 4 Rose bloom v2 | pass: two petal rings, rim Ø0.116, h 0.05, centre bud; from the side/above blooms clearly read as roses (several in the middle and lower tiers), noticeably richer than the pass-2 cups |
| 5 Closed buds | pass: small red buds visible (next to the centre bloom) |
| Must-not-change (palette, pivot, 1 mesh/material, variants) | pass per builder notes; 1996/2000 tris |

Size 1.05 x 0.88 x 1.09 m: accepted (wider and deeper than the catalogue 0.8; record in spec.md).

Weaknesses (not blockers): the top 3 blooms are seen mostly from the side and still read as flared cups with a small spike, i.e. "tulip-like", compared with the lower ones; the clusters are still large and smooth-looking relative to blooms; the crown is a dense round mass. At 128 px it reads as a flowering rose bush, not a tree or the round Farm Nature bush.

## Is rose_bloom_v2 good enough to propagate to PLT-02/03 and TOP-01_Rose? Yes, with notes
- Use it as the shared bloom (68 tris; rim Ø0.116, h 0.05).
- Orient so the bloom is seen at 25-45 deg from above (tilt 15-30 deg, not a near-upright top tilt that shows only the side wall); this is why the top three look weaker than the middle ones.
- Climbers/standards (PLT-02/03/TOP-01_Rose) have tight triangle budgets: confirm per-model bloom counts times 68 tris first; for the _Pink/_White variants the two-ring contrast depends on cells 6/7 and 8/8 (white has no ring contrast; accept, or let the inner ring use a different cell).
- Keep the leaf cluster at 80 tris, domed 0.80 D, and make the tufts larger (about 0.10-0.14 leaf length) if the family needs a broken outline.
