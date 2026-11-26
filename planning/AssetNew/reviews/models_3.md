# AssetNew: reference review, batch 3 (2026-11-25)

Every preview `art/AssetNew/Previews/FMS_Garden_<ID>_Preview.png` compared with `planning/AssetNew/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.
Status: FINAL. All 10 batch-3 items reviewed (WTR-01, WTR-02, ORN-01, ORN-03 (+ _Planted), ORN-02, ORN-04, ORN-05 (+ _Feeder), FUR-01, FUR-02, FUR-03). No second pass needed.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 0 | Close to the reference, no edits |
| 🟡 Pass with notes | 10 | WTR-01, WTR-02, ORN-01, ORN-02, ORN-03, ORN-04, ORN-05, FUR-01, FUR-02, FUR-03 |
| 🔴 Fix | 0 | Silhouette, signature feature or proportions clearly off |
| ❓ Decision | 0 | Deliberate deviation; the owner decides |

Cross-cutting issues (batch 3, and rules for batch 4):
1. All 10 items are 🟡: no geometry fixes were needed. The palette effect (stone greyer/cooler, white cooler, wood paler than the references) is a palette decision, not a defect.
2. The reference wins over the catalogue where no functional size is involved: WTR-01 height 2.42, ORN-04 height 0.88, FUR-01 2.48 x 2.16, FUR-02 width 3.06, ORN-01/02/03 proportions. Functional sizes were kept (seat top 0.45, swing clearance 0.165, hammock cloth 0.59, MOD-03 back face 0.22).
3. Wrought-iron family: STR-02 (8-sided 0.040 / 0.030), ORN-05 (8-sided hook, square 0.03 scroll bars, 6-sided rods), FUR-03 (6-sided 0.036 / 0.030, budget 1000). All at or above the 0.03 minimum. FUR-04 must reuse the FUR-03 helpers and wording (budget 1400): foot curls 8 segments, curls >= 0.10 across, slot 13 / `_White` slot 10, check at 128 px.
4. Dark iron under a dark top or in shadow loses its detail (FUR-03 hub scrolls, ORN-05 ring): keep legs and curls as the read and put ornament where it is lit.
5. Water: opaque slot 15 flat discs, light slot 9 on one face row of the streams (WTR-01/02); stiff straight ribbons, no spray.
6. Budget use: under-budget is fine where the reference is simple (FUR-01 580/1600, FUR-02 784/1000); ORN-04 888/900 and ORN-05 600/600 are tight but read at 128 px, so no raise was needed.
7. Batch-4 watch list: FUR-04 chair (FUR-03 iron wording, seat 0.45, differ from Farm Market chairs, budget 1400); FUR-05 deck chair (red/cream stripes, differ from FUR-02 cream/blue, wood slot 0); PLT-04 ivy, PLT-05 wisteria, PLT-06 hollyhock and TOP-01..04 topiary: reuse rose_bloom_v2 and the 80-tri domed drops (20-tri leaf drops read gem-like, use 80-tri where budget allows), cups tilted toward the viewer, green stems (no brown lollipop stalks, no bare stem tops), measure against the reference, check the 128 px thumbnail for the vine/bush read; atlas F models use `M_Garden_Flora`.
8. One preview per ID means variants (`_Blue`, `_White`, `_Feeder`, `_Planted`) have no preview: verify one render of each at assembly.

Catalogue size corrections from this batch (coordinator action):
- WTR-01 2.4 x 2.4 x 2.42 (catalogue 1.9); WTR-02 0.90 x 0.59 x 1.30; ORN-01 0.45 x 0.45 x 0.955; ORN-02 0.243 x 0.226 x 0.45; ORN-03 0.6 x 0.6 x 1.2 (`_Planted` 1.384); ORN-04 0.60 x 0.38 x 0.88 (catalogue 1.1); ORN-05 0.56 x 0.28 x 1.70 (catalogue 0.5 x 0.3), `_Feeder` 0.57 x 0.30 x 1.70; FUR-01 2.48 x 1.50 x 2.16; FUR-02 3.06 x 0.90 x 1.10 (catalogue 3.2); FUR-03 0.70 x 0.70 x 0.75, budget 1000.
- Specs and STYLE: ORN-04 dividers slot 1 (spec 0), FUR-02 rings on the inner post faces, FUR-01 hangers at X +-0.84, WTR-01 basin 16 sides 0.34 high (spec 12 sides 0.50), ORN-03 is on atlas F as the catalogue says (the envelope said A).

## Consolidated Unity-import additions from batch 3 (Э8, not verifiable in this review)
Same series assumption as batch 2 (Blender (x, y, z) -> Unity (-x, z, -y)); append to the batch-2 list:
- ORN-05: the hook points to Unity -X; rotate the prefab 180 degrees about Y if +X is wanted; `Hanging` is a static direct child of the root with its pivot at the hang point (Blender (0.296, 0, 1.454)); the pole foot is the root pivot.
- ORN-01: the gnomon tall edge is at Blender +Y = Unity -Z (spec said +Z); decorative, rotate the prefab 180 degrees about Y if wanted.
- FUR-01: `Seat` pivot Unity (0, 2.04, 0), axis X, travel +-30 degrees; `Seat_Low1` must follow it in the LOD group.
- WTR-02: basin to Unity +Z, back face at Z 0; verify with the first MOD-03 placement (back 0.22 from the wall axis).
- WTR-01: 23 nodes (11 meshes + 11 `_Low1` + root), LOD group pairing per mesh.
- ORN-02: nose toward Unity +Z; `_Blue` is the same mesh with remapped UVs, verify one render. ORN-04: open front to Unity +Z.
- ORN-03/05 and `_Planted`/`_Feeder` use atlas F (`M_Garden_Flora`); `_Planted` has two mesh nodes (`_Body`, `_Plants`).
- FUR-02 and FUR-03: X-symmetric statics, no flip issue; FUR-03 `_White` verify once.
- Colliders: WTR-01 basin cylinder 2.4 x 0.34 plus a pedestal cylinder; ORN-01 box 0.40 x 0.40 x 0.95; ORN-03 box about 0.5 x 0.5 x 1.2 (ignore hanging blooms); ORN-05 capsule on the pole only; FUR-01 two frame boxes, no seat collider at rest; FUR-02 foot/post boxes, the cloth is not a blocker.

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
| FUR-03 | Bistro_Table (+ _White) | Hub scrolls smaller and less ornate than the reference and in the shadow of the top; 6-sided rods; budget 1000 (raised from 500); `_White` not previewed. See the FUR-03 section. |
| FUR-02 | Hammock | Width 3.06 (catalogue 3.2), beam joins posts at 0.72 and dips to 0.19, rings on the inner post faces, cloth ends at X +-1.16, cord tips show at the cloth ends, cloth whiter and wood paler (palette). See the FUR-02 section. |
| FUR-01 | Swing | Width 2.48 / height 2.16 (catalogue 2.4 / 2.1), hangers at X +-0.84, braces dark slot 1, iron clamps and brackets added, 580/1600 (reference equally simple), LOD1 hanger rod thins. See the FUR-01 section. |
| ORN-05 | Shepherd_Hook (+ _Feeder) | Ring/curl form a small knot, rods cross in front of the flowers, square scroll bars, sparser mound, feeder roof and body nearly one brown, 600/600. See the ORN-05 section. |
| ORN-04 | Insect_Hotel | Height 0.88 (catalogue 1.1, reference squat); 3 hex logs per cell vs 4 octagons, 5 straw stalks vs 7-8, thicker frame, lighter holes, 888/900. See the ORN-04 section. |
| ORN-02 | Gnome (+ _Blue) | Hat a straight cone with a milder lean than the reference, boots boxier, whites cooler, `_Blue` not previewed. See the ORN-02 section. |
| ORN-03 | Urn (+ _Planted) | Urn and pedestal re-proportioned from the reference; planted: stems green, mound large, small leaf drops gem-like, one stem partly bare, 1296/1300. See the ORN-01 / ORN-03 section. |
| ORN-01 | Sundial | Column more slender than the spec table, ribs/dial lighter than the reference, gnomon faces Unity -Z (spec +Z). See the ORN-01 / ORN-03 section. |
| WTR-02 | Fountain_Wall | Stream bends out slightly at the lip, medallion contrast low, smaller front chamfer than the reference, stone paler/greyer. See the WTR-02 section. |
| WTR-01 | Fountain_Tiered | Height 2.42 (catalogue 1.9, reference wins); ribbons are stiff blue bars with light hook tops, read as water curtain but a bit like blue posts; stone paler than WTR-03 render only by lighting. See the WTR-01 section. |

## ✅ Pass
- none yet

## WTR-01 Fountain_Tiered (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_WTR-01_WTR-01.png`; full preview also viewed. LOD1 (788), checks and SNAP (n/a) are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `WTR-01.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: wide 16-sided basin, two bowls stacked on faceted pedestals, faceted pine-cone finial; reads as a tiered fountain, not as the Farm Yard well or trough |
| Signature feature (tiers + streams) | pass with notes: three blue water discs, 8 + 8 streams falling from the rims, finial rising from the upper water, as in the reference |
| Proportions | pass: bowl/basin/finial ratios match the reference on the sheet (builder ortho check within 4 px); upper neck is a little thicker than the reference's slim one (spec minimum 0.20) |
| Colour / palette | pass: slots 11/12 limestone and stone, 15 water, 9 light hook tops; the preview stone is a warm light cream, close to the reference and consistent with the WTR-03 cells; two-tone split (inner basin wall, foot, bowl inner slopes) visible |
| Readability at 128 px | pass: three blue discs, white stone tiers and the vertical streams keep the fountain legible; streams are the weakest read (see below) |
| Style match with WTR-03 / MOD-03 | pass: same cells, flat shading, chunky faceted stone, no bevel, no carving |

Decisions:
- Height 2.42 vs catalogue 1.9: ACCEPT. The reference is 2.42 m tall at the 2.4 m footprint (ortho render within 1 px); a 1.9 m fountain on a 2.4 m basin would look squat and lose the finial. There is no walk-through opening, so no functional size wins here; PIPE-04 puts the reference first (same as WTR-03). Action for the coordinator: catalogue/spec size 2.4 x 2.4 x 2.42; check demo clearance (nothing taller than 2.42 above it).
- Stream ribbons at 128 px: ACCEPT. Eight stiff 0.07 x 0.035 ribbons per bowl in the flat blue cell 15, with light slot 9 on the hook top and one side, read as falling water curtains: they are vertical, blue, start at the rim and land in the next disc, exactly as in the reference. They do look a little like blue posts or spokes in the 3/4 preview (hook caps stand slightly proud), and the lower set is less rhythmic than the reference's; the reference is equally stiff, and the spec forbids spray, droplets or thin jets, so no change. Optional: none required; if the owner wants it softer, widen only the light slot 9 face row, no geometry change.
- 16-sided basin and bowls, 8-sided pedestals and finial, flat faces to the front: ACCEPT (reference facets; the spec's 12 sides were an estimate).
- Basin 0.34 high, no coping lip, no chamfer, water 0.13 below the top: ACCEPT (reference is one flat ring; spec says no bevel beyond what the reference shows). Basin is lower than the spec 0.50 but the sheet shows the same proportion as the reference.
- Bowls Ø1.47 / Ø0.84 (spec 1.3 / 0.7): ACCEPT, measured on the reference, within the 2.4 footprint.
- Upper neck at 0.20 across corners: ACCEPT, at the spec minimum; it is the thinnest part but reads at 128 px.
- Finial without a stem: ACCEPT (reference bulb sits in the water).
- Ribbons not offset 22.5 degrees, both sets same azimuths: ACCEPT (reference).
- Tris 1258/2800: fine, the reference has nothing finer; LOD1 788 (63 %, ribbons kept intact): ACCEPT. LOD1 basin lower ring irregular: ACCEPT (distance only; three discs and ribbons keep the silhouette).
- Stone/water consistency with WTR-03 and MOD-03: pass: cells 11/12 and 15, matte flat, same wording; the water disc is a flat opaque slab like MOD-09, no ripples.

Unity import checks flagged (for Э8, not verifiable here):
- Pivot at the basin centre on the ground; 23 nodes (11 meshes + 11 `_Low1` + root); LOD group must pair each mesh with its `_Low1`.
- Basin has a vertex on +X, bowls and pedestals a flat face on +X; symmetric about the YZ plane, so the X-flip does not change the look.
- Collider: one cylinder about Ø2.4 x 0.34 for the basin plus a thin cylinder for the pedestal is enough; streams need none.

## WTR-02 Fountain_Wall (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_WTR-02_WTR-02.png`; full preview also viewed. SNAP against MOD-03 (coping face flush, 0 verts inside), flat back face and tris are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `WTR-02.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: tall stele with a gabled cap, half-round basin in front on a faceted half drum; clearly a wall fountain, not the well, trough or WTR-01 |
| Signature feature (spout + stream + medallion) | pass: round medallion, metal spout with a visible bore, one blue stream falling into the half-disc water; matches the reference |
| Proportions | pass: 0.90 x 0.59 x 1.30; basin lower and stele taller than the spec, as in the reference; the gable is slightly steeper/deeper than the reference's but the same read |
| Colour / palette | pass: slots 11/12 stone, 7 metal spout, 15 water, 9 light side of the stream; preview stone is warm cream, close to WTR-01/WTR-03; medallion in slot 12 has lower contrast than the reference (palette) |
| Readability at 128 px | pass: stele, round medallion, blue stream and half basin all read; the stream is the clearest feature |
| Style match | pass: flat matte facets, no carving; water is a flat opaque half disc like WTR-01/MOD-09 |

Decisions:
- Gabled stele and cap with the ridge front-to-back, 16.7 degrees, cap 0.085 thick (spec: 0.04 gable, ridge along X): ACCEPT (reference; the silhouette feature).
- Basin coping 0.44 / water 0.37 (spec 0.55 / 0.46), 16-gon half drum, spout 0.78, medallion 1.00: ACCEPT, measured from the reference; water 7 cm under the coping is close to the spec rule of 9 cm and still shows an inner wall. Back plane exactly flat at Z 0, so the MOD-03 contract (0.22 from the wall axis) stays valid: ACCEPT.
- Spout: slot 7 `#8E959B` as in the spec and the reference (grey metal), not wrought iron slot 13: ACCEPT. STR-02 iron (slot 13, dark) is a different object type; the grey spout reads as a brass or zinc pipe and is a better contrast against the cream stone. Spout is Ø0.09 with a collar Ø0.14, above the 0.03 minimum.
- Stream in slot 15 with the light row on the +X side only (same rule as WTR-01 ribbons): ACCEPT. It bends out slightly at the lip, a small hook, reads as a pour; the reference falls straighter; optional only.
- Plinth 1.2 cm proud in slot 12 (reference has none): ACCEPT, keeps the two-tone split, as requested in the pilot lesson.
- Stele depth 0.15, front chamfer 0.02 (reference chamfer wider): ACCEPT.
- Tris 428/900, no LOD: fine; reference has nothing finer.
- Stone/water consistency with WTR-01, WTR-03, MOD-03: pass: same cells 11/12/15, flat opaque water, same wording.

Unity import checks flagged (for Э8, not verifiable here):
- Blender -Y = front becomes Unity +Z under the series FBX assumption: basin must extend to +Z and the back face lie at Z 0. Verify with the first placement against MOD-03 (back 0.22 from the wall axis); stele symmetric in X, so the X-flip does not matter.
- Colliders: box for the stele (0.70 x 0.15 x 1.30) plus a half-cylinder or box for the basin; the stream needs none.

## ORN-01 Sundial and ORN-03 Urn (+ _Planted) (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_ORN-01_ORN-03.png`; both full previews not re-opened separately (sheet is the same render); `_Planted` judged from `%TEMP%/assetnew_check/ORN-03/ORN-03_Planted_check.png` (not in `art/AssetNew/Previews/`). Tris, checks, footprint and FBX are from the builder notes, not re-measured.

Verdicts: ORN-01 🟡 PASS with notes; ORN-03 base 🟡 PASS with notes; ORN-03 `_Planted` 🟡 PASS with notes. No FIX, so no "## Fix 1" written.

| Criterion | ORN-01 | ORN-03 |
|---|---|---|
| Silhouette | pass: stepped plinth, moulding, slender square shaft, flared capital, round dial with tall blade; reads as a sundial, distinct from the birdbath WTR-03 (square, no bowl) | pass: square plinth, shaft, cap block, goblet urn with foot, belly and flared lip; reads as an urn on a pedestal |
| Signature feature | pass: 12 dark ribs on a grey dial and an iron gnomon blade (dark, tall edge near the rim); the ribs read as hour marks without numerals | pass: faceted belly, thick flared lip, brown soil disc in the opening |
| Proportions | pass: 0.45 x 0.45 x 0.955; slender column and steep capital follow the reference (spec table was an estimate, PIPE-04); same silhouette on the sheet | pass: 0.6 x 0.6 x 1.2; urn larger on a lower 0.635 pedestal as in the reference; shaft 0.30 kept |
| Colour / palette | pass with notes: dial/ribs lighter than the reference's near-black ribs; stone greyer (palette) | pass: stone cooler/whiter than the beige reference (palette) |
| Readability at 128 px | pass: column, dial disc and dark blade read; individual ribs become a dotted ring | pass: urn, pedestal and soil read |
| Style match with WTR-01/02/03 | pass: same cells 12/11 plus 7/8 metal, 13 iron; matte flat, chunky; no carving | pass: F 14/15 are the same HEX as A 12/11; the preview stone is visually the same limestone and warm grey as WTR-01/02/03 |

Must differ from Farm Market pots: pass. A 1.2 m square pedestal with a stone goblet urn (pale limestone, faceted, no terracotta, no saucer) is a different object from the low terracotta `FMS_Deco_Pot_*` and `FMS_Comp_FloralPlanterStand`.

`_Planted` (ORN-03):

| Criterion | Result |
|---|---|
| Reads as a planted urn | pass: green mound of three domed drops heaped over the opening, pink/white cup blooms with yellow centres, vines hanging over the belly; reads as a trailing-flower urn at normal size |
| Style match with PLT-01 / FLB-02/03 | pass with notes: same 80-tri domed drops and three-green split; cups tilted toward the viewer, no brown stalks (stems green, F2) as the series lesson says; the small 20-tri leaf drops on the vines look gem-like up close |
| Gaps / bare stems | pass with notes: the right stem is bare along its horizontal segment over the lip (a short green bar, lollipop-like), the rest of the vines carry leaves; acceptable, optional leaf or bloom there |
| 128 px | not fully verified: mound plus a few pink/white dots should survive; vines are thin (Ø0.03 = the STYLE minimum), so they thin into dark green lines but the blooms carry the read |
| Footprint / budget | 0.600 x 0.600 (blooms hang free of the pedestal, lowest 0.846), height 1.384; 1296/1300; accepted, at the limit |

Deliberate deviations judged:
- ORN-01 plinth 0.34 / moulding 0.25 / shaft 0.18 / dial top 0.797 / gnomon 0.16 tall (spec 0.40 / 0.30 / 0.22 / 0.85 / ~0.09): ACCEPT, from the reference; all parts above the 0.10 minimum, total height 0.955 and footprint 0.45 match the catalogue.
- Dial rim as a chamfer band instead of a raised ring; ribs 0.030 x 0.076 x 0.014 on the flat top; ribs at the dial flats: ACCEPT (reference; ribs are at the 0.03 minimum width and stay readable).
- Plinth keeps its bottom face (+2 tris): ACCEPT.
- Gnomon direction: the sundial is a decorative object, with no functional orientation in the game, so the direction does NOT matter for play; the blade stands at Blender +Y (reference/preview look), which becomes Unity -Z. The spec said +Z. ACCEPT; add one line to the Unity import list: after the first import the blade's tall edge is on the back of the dial from the standard view, and if the owner wants it toward Unity +Z, rotate the prefab 180 degrees about Y (the dial and column are symmetric, so this is free).
- ORN-03 atlas F instead of A: ACCEPT. Catalogue and spec say atlas F, so the builder was right and the envelope line was wrong; the stone cells F14/F15 hold the same HEX as A12/A11, so the stone matches WTR-01/02/03; material `M_Garden_Flora`. Note for assembly: the urn and its `_Planted` use a different material from the other stone models (two draw calls in a scene, no visual difference).
- ORN-03 pedestal top 0.635, urn 0.565 tall, plinth 0.44, cap 0.37, no cap-underside or lip chamfer: ACCEPT (reference measured; sharp edges as the reference shows).
- `_Planted` mound 3 drops D 0.31 (spec 3-4, 0.15-0.25), 6 vines and 8 blooms in place of 6-8 stems and 8-10 blooms, stems green F2 instead of F13 brown: ACCEPT (size to cover the soil, 1300 budget, series rule no brown stalks).
- Planted height 1.384 (up to 1.4): fine.

Optional (no re-review): add one leaf drop or bloom on the bare right vine if the budget is freed (4 tris margin only); enlarge the leaf drops slightly or flatten them to reduce the gem look.

Unity import checks flagged (for Э8, not verifiable here):
- ORN-01 gnomon orientation (see above); both ornaments are free-standing with a pivot at the plinth base centre on the ground.
- ORN-03 `_Planted` has two mesh nodes (`_Body` + `_Plants`); the colliders for the pedestal and urn should be a simple box about 0.5 x 0.5 x 1.2, ignoring the hanging blooms.
- Medium-size ornament colliders: ORN-01 box 0.40 x 0.40 x 0.95.

## ORN-02 Gnome (+ _Blue) (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_ORN-02_ORN-02.png`; full preview also viewed. `_Blue` FBX (same mesh, UV swap: hat 15, coat and arms 5) not visually checked (no variant preview); verify one render at assembly. Tris, pivot and checks are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `ORN-02.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: tall red cone hat leaning back, wide white shield beard, blue coat with dark belt, stubby boots; reads as a garden gnome without colour |
| Signature feature (hat, beard, nose, hands) | pass: nose ball under the brim, beard to the belt, two cream hands at the beard sides, no eyes or mouth; no facial expression as the spec requires |
| Proportions | pass: 0.243 x 0.226 x 0.450 (limit 0.25 / 0.45); hat about 40 % of the height as in the reference; boots wider than the spec, as in the reference |
| Colour / palette | pass: slots 5 / 10 / 15 / 13 / 3 / 1 as the spec; whites cooler than the reference (palette), cream hands and nose stay distinct from the white beard |
| Readability at 128 px | pass: red cone, white beard and blue coat form three clear masses; the nose and hands are cream dots; the belt reads as a dark line |
| Style match | pass: faceted flat matte shapes, chunky arms (0.05-0.06), 80-facet icosphere hands and nose with visible facets; reads as a stylized statuette, not a character illustration (no expression, no eyes, no outlines) |
| Difference from Farm Yard scarecrows | pass: a 0.45 m squat figure standing on its own boots with a big beard and a short cone hat, no pole, straw or pumpkin; hat colour is the only common element |

Deliberate deviations judged:
- Icosphere subdivision 2 (80 facets) for hands and nose, because Blender's subdivision 1 is a bare 20-face icosahedron; hands 160 tris against the spec's rough 80 for both: ACCEPT. Facets are visible and the spec's own tri estimate corresponds to subdivision 2; budget held by a cheaper head and boots. Total 586/600 is at the limit but within it.
- Head is an 8-sided loft (hidden), belt is a flush painted band of the coat, not a ring: ACCEPT (reference; avoids a floating ring and a coplanar seam). Belt remains readable.
- Hat base 0.245 (spec 0.27), apex bent back 0.05 (spec 0.02), brim 0.012: ACCEPT (reference leans clearly; tip ring Ø0.030 meets the apex minimum).
- Boots 0.075 x 0.12 x 0.056: ACCEPT (reference). They read a bit boxy; optional rounding, no need.
- Hat is a straight-sided cone with a gentle back bend, not the reference's slight kink: ACCEPT.
- `_Blue` is the same mesh and UVs remapped, no geometry change: ACCEPT (variant contract); the blue hat will use water-blue slot 15, the same colour as the coat in the base: fine.
- Facing: Blender -Y = Unity +Z, as required for a facing statuette; the figure is X-symmetric, so the X-flip does not matter. Add to the Unity list: confirm the nose points to +Z.

Optional: none required. If the owner wants a closer lean, increase the apex bend from 0.05 to about 0.07 (hat stays within 0.45).

## ORN-04 Insect_Hotel (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_ORN-04_ORN-04.png`; full preview also viewed. Tris, checks and the FBX are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `ORN-04.3d.md`. The budget is not too tight for the signature, so no budget raise.

| Criterion | Result |
|---|---|
| Silhouette | pass: gabled roof with a ridge board, open grid of nine cells on short legs; reads as an insect hotel, clearly not the closed Farm Yard `FMS_Birdhouse` (no closed box, no entrance hole, open front) |
| Signature feature (3 x 3 cells: logs / straw / bricks) | pass: the three fillings alternate so no two neighbours match, as in the reference (log / straw / brick on every row and column) |
| Proportions | pass with notes: 0.60 x 0.377 x 0.88, squat like the reference; cells about 1:1; roof steep as in the reference; the frame is a little thicker and the cells slightly smaller than the picture |
| Colour / palette | pass: dark wood frame (slot 1), light-wood roof (0), straw (4), bricks (14/6); straw paler and holes lighter grey than the reference (palette) |
| Readability at 128 px | pass: cells read as three distinct fillings: red bricks with holes, cream straw bundles, brown hex log ends; holes read as grey dots, which is enough |
| Style match | pass: flat matte chunky wood, same wording as the STR-04 and Market wood; no thin slats |

Cell filling vs budget (888/900): readable and sufficient. Honeycomb of three hex log ends with holes fills each log cell and reads as "logs with holes" at 128 px; four octagons would add about 140 tris per cell and would not change the read at that size. Five straw stalks per cell read as a straw bundle (the reference's 7-8 would only add noise at 128 px). The 6-hole bricks are the clearest cell. The signature (a rack of different nesting materials) is intact, so the budget is not a defect; no FIX.

Deliberate deviations judged:
- Height 0.88 vs catalogue 1.1: ACCEPT. The reference is a squat cabinet (h/w about 1.4 including the roof and legs, i.e. about 0.85-0.9 m at 0.6 m wide) and no functional size is involved; a 1.1 m version would need taller cells and look like the sheet in the spec table. Width 0.60 kept. Action for the coordinator: catalogue size 0.60 x 0.38 x 0.88; ridge and roof under the 1.10 limit.
- Boards 0.05 kept (spec minimum, never trimmed) though the reference is thinner: ACCEPT; STYLE minimum applies.
- Dividers in slot 1 (dark) instead of slot 0: ACCEPT, as in the reference; light log ends, straw and bricks read better on the dark grid. Spec and STYLE are for the coordinator to update.
- Roof pitch 38 degrees (spec 25): ACCEPT, from the reference; ridge top at 0.88 inside the limit. Open gable triangle showing the roof underside: ACCEPT (reference side view).
- Straw stalk width 0.021 (STYLE minimum for slats 0.03): ACCEPT with a note. They are filling bundles, not structural slats, depth 0.03, and they read at 128 px; widening them would cost cell space and the 12-tri-per-stalk budget.
- Hex logs, 3 per cell, 2 holed; 6-gon cone holes (render mid-grey, not black): ACCEPT; the spec asks for 6-sided logs and allows trimming counts.
- Legs 0.08 and 0.14 high (spec 0.10 and 0.20): ACCEPT (reference legs are shorter and thinner).
- Ridge board 5 mm short of the roof ends: fine.

Unity import checks flagged (for Э8, not verifiable here): open front Blender -Y = Unity +Z; the model is X-symmetric. Collider: one box about 0.6 x 0.38 x 0.88; no per-cell colliders.

## ORN-05 Shepherd_Hook (+ _Feeder) (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_ORN-05_ORN-05.png`; full preview also viewed. `_Feeder` judged from the headless check render `%TEMP%/assetnew_check/ORN-05/ORN-05_Feeder_check.png` (same camera, not in `art/AssetNew/Previews/`). Tris, checks and pivots are from the builder notes, not re-measured.

Verdicts: base 🟡 PASS with notes; `_Feeder` 🟡 PASS with notes. No FIX, so no "## Fix 1" in `ORN-05.3d.md`. 600 is tight but not too tight for the signature: no budget raise.

| Criterion | Base | `_Feeder` |
|---|---|---|
| Silhouette | pass: tall thin iron pole with a ground spike, footrest, S-scroll on the pole, hooked arc with a curl, basket hanging from three rods | pass: same hook; a roofed eight-sided feeder with a tray hangs from the rods |
| Signature feature | pass: the shepherd-hook arc with the curl and the hanging basket of flowers; scroll present | pass: feeder reads as a hanging bird feeder (cone roof, knob, grain windows), no birds |
| Proportions | pass: 1.70 m high, bend 1.50, basket rim 1.15; reference measured (1137 px = 1.70 m); wider than the catalogue (0.56 vs 0.5) because the reference scroll sits on the left of the pole | pass |
| Colour / palette | pass: iron F10 (same `#3A3A3F` as STR-02), basket F13, leaves F0/1/2, pink/white blooms with yellow centres | pass with notes: roof F12 and body F13 are nearly the same brown, separated only by light; grain yellow windows and the pale tray give the read |
| Readability at 128 px | pass: the thin pole and arc stay readable because rods are 0.03-0.04; basket with pink/white dots reads as hanging flowers; the scroll is a small dark mark | pass: roof, body and grain dots read |
| Difference from Farm Market `FMS_Deco_Lantern_Hanging` | pass: a 1.7 m ground-spiked crook with an open basket (or feeder), no glass, no lantern body, no cap | pass |
| Iron consistency with STR-02 | pass with notes: same slot colour, matte flat, same `s_curve()` scroll wording and 0.04 pole; the scroll and footrest are square 0.03 bars (STR-02 is 8-sided) and the suspension rods are 6-sided; hook sweep is 8-sided; see below | same |
| Basket plants vs PLT-01 | pass: same domed 3-green drops (scaled to 20 tris), cup blooms tilted toward the viewer, no brown stalks, mound to about 1.27 | n/a |

Deliberate deviations judged:
- Budget 600/600 and the iron wording: ACCEPT square 0.03 scroll and footrest bars and 6-sided Ø0.03 rods. They keep the STYLE minimum (>= 0.03) and the flat faces still read as forged iron; an 8-sided scroll would cost about +40 tris. This is a justified departure from the STR-02 anchor (8-sided) for budget reasons, and the builder explained it. The scroll curls show 4 segments and look slightly angular (a zigzag from the front); recognisable as an S-scroll. Optional: none required.
- Is 600 too tight? No. The signature items are all present: arc with curl, ring, three rods, bowl, three drops, six blooms, scroll. What was lost is detail the thumbnail cannot show (more drops/blooms, rim band, 8-sided scroll). No FIX.
- Heights from the reference (bend 1.50, hanging point 1.454, rim 1.15, footrest 0.28) rather than the spec table: ACCEPT; no functional size involved. Width 0.557 and depth 0.282 vs 0.5 x 0.3: ACCEPT; record in the catalogue (the scroll adds 0.124 left of the pole).
- Ring edge-on in the YZ plane (the reference draws it facing the viewer), forming a small knot with the curl and the rod tops: ACCEPT. At 3/4 it reads as a link; the crossing front rods hide part of the flowers; both only a nitpick. The `Hanging` object is fine as a separate pivoted node.
- Flower mound a bit lower and sparser than the reference: ACCEPT.
- `_Feeder`: windows 0.064 (spec 0.10) because the 8-sided body has 0.083 facets, a second window on +X added: ACCEPT. Roof and body nearly one brown: ACCEPT as specified (F12 and F13); optional, swap the roof to F13 and the body to F12, or the roof to the lighter F14 stone, if the owner wants a clearer split; no tri cost.
- `_Feeder` has no preview in `art/AssetNew/Previews/`: judged from the check render; one preview per ID as the pipeline says, so nothing is missing.

Unity import checks flagged (for Э8, not verifiable here):
- Under the series X-flip assumption the hook points to Unity -X. It is decorative: rotate the prefab 180 degrees about Y if the owner wants the hook toward +X; the pivot (pole foot) does not move. Verify together with the MOD-06 / STR-01 / STR-05 / MOD-08 / FLB-02 items.
- Pole foot pivot at (0, 0, 0), `Hanging` node pivot at the hang point (0.296, 0, 1.454) in Blender space: after import it must be a direct child of the root, static (rotation by the user only).
- Collider: capsule on the pole only (about Ø0.05 x 1.7); basket and feeder need none.

## FUR-01 Swing (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_FUR-01_FUR-01.png`; full preview also viewed. LOD1 (356), the swing-range clearance (+-30 degrees, 0.165 from the legs, lowest seat point 0.322), `Seat` pivot and tris are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FUR-01.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: two A-frames with a top beam, braces, a bench on four iron hangers; reads as an A-frame garden swing at 128 px |
| Signature feature (swinging bench) | pass: the bench hangs clear of the frame and the ground, slatted backrest with 8 slats, armrests, a cream cushion, hangers in a narrow V from clamps on the beam |
| Proportions | pass with notes: 2.48 x 1.50 x 2.16; the reference is a wide-angle picture, so its frames look more splayed and its bench larger; the model follows the functional numbers (seat top 0.45, beam axis 2.04) |
| Colour / palette | pass: light wood slot 0 (same as STR-01/STR-04), dark braces slot 1, iron slot 13 (clamps, hangers, brackets), cream cushion slot 3; wood paler and the cushion cooler than the reference (palette) |
| Readability at 128 px | pass: frame, rods and the pale cushion read; the slatted backrest is visible; the iron rods are thin dark lines but the clamps and corner brackets anchor them |
| Style match | pass: flat matte chunky posts 0.12 and braces 0.10, same wording as STR-01/04; iron rods 8-sided 0.035 on the STR-02 anchor |

Richness vs budget (580/1600): NOT too sparse. The reference is made of plain posts, a slatted bench and rods: the preview shows all of its elements (apex blocks, beam stubs, clamps, 8 slats, armrests, brackets, cushion). Nothing measurable is missing, and the spec forbids detail beyond that (no canopy, no rope, no chain links). The unused budget is not a defect, as for STR-04/05.

Deliberate deviations judged:
- Width 2.48 and height 2.16 (catalogue 2.4 / 2.1): ACCEPT (+3.3 % / +2.9 %). The reference shows the beam ends standing out past the apex blocks and the apex blocks on top; no walk-through opening is involved. Update the catalogue size to 2.48 x 1.50 x 2.16.
- Hanger plane X +-0.84 (spec +-0.80): ACCEPT, functional: the 1.6 m bench would otherwise cut through the side frames; the rods just outside the bench ends match the reference; clearance to the legs is still 0.165 (>= 0.15).
- Backrest as posts, rails and 8 slats (0.05 x 0.03), top about 1.00, cushion 0.10 thick: ACCEPT (reference; slats at the 0.03 minimum depth, and they read).
- Apex blocks, iron clamps under the beam and corner brackets at the seat: ACCEPT (all visible in the reference).
- Braces in dark slot 1 and at 0.45 (reference draws them in the same wood, a little lower): ACCEPT per spec; the dark tone gives the two-tone split.
- Frame split into three static parts (EndFrame_A, EndFrame_B, Beam) so LOD1 keeps it: ACCEPT. `Seat` stays a separate node with its pivot on the beam axis (0, 2.04, 0).
- LOD1: seat 224 tris, front hanger rod thins to a line: ACCEPT (distance LOD, as STR-03 bench legs).
- Wood consistency with STR-01/STR-04: pass, same slot 0 and 0.10-0.12 post section.
- Difference from Farm Market `FMS_Deco_Bench_Plank`: pass; a hanging bench in an A-frame is a different object.

Unity import checks flagged (for Э8, not verifiable here):
- `Seat` pivot at Unity (0, 2.04, 0), rotation axis X, rest 0, travel +-30 degrees; check the node is a direct child of the root and that its LOD child `Seat_Low1` rotates with it (LOD group pairing).
- The model is X- and Y-symmetric, so the series X-flip does not matter.
- Colliders: two leg boxes or one box for each frame plus the beam; the seat needs none in the rest position.

## FUR-02 Hammock (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_FUR-02_FUR-02.png`; full preview also viewed. Tris, clearances (cloth bottom 0.592, 0.216 above the beam) and FBX are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FUR-02.3d.md`.

| Criterion | Result |
|---|---|
| Silhouette | pass: two upright posts on cross-feet, a bowed wooden beam in a deep U under a sagging striped cloth, iron eyes at the post tops; reads as a hammock on a stand, not a bench or a swing |
| Signature feature (striped sagging cloth) | pass: a closed shell sling gathered to the ends, 5 lengthwise stripes cream / blue / cream / blue / cream, cords to the rings; reads from the shape and stripes at 128 px |
| Proportions | pass with notes: 3.06 x 0.90 x 1.10; the curved beam is a little shallower than the reference's bowl and the cloth sits higher above it, but the reference is a long-lens picture; the cloth bottom 0.59 / beam clearance 0.216 follow the spec |
| Colour / palette | pass: cloth cream slot 3 and blue slot 15 (cream/blue, not the red-cream of FUR-05), edges and cords cream-dark slot 4, wood slot 0, iron slot 13; cloth whiter and wood paler than the reference (palette) |
| Readability at 128 px | pass: the striped cloth is the strongest read; the iron rings are small dark marks and the cords thin, but the cloth ends are legible |
| Style match | pass: flat matte facets, chunky posts 0.14 and beam 0.12; no fringe, pillow or ground plate |

Stripes: cream/blue (3 / 15) alternating with a cream centre stripe, exactly as the spec says, so FUR-05 (red/cream) will differ. Only the blue cell is shared with the water, as in the series (slot 15 = blue serie).

Deliberate deviations judged:
- Beam joins the posts at 0.72 (spec 0.93) and dips to 0.19 centre line (bottom 0.13) at X = 0: ACCEPT, measured from the reference; the bowl reads deeper and closer to the ground, like the picture. Cloth clearance 0.216 above the beam top is kept, and the beam does not touch the cloth.
- Posts 0.14, beam 0.12, feet 0.16 x 0.12 high x 0.90: ACCEPT (reference; avoids a beam deeper than the post); all above the 0.10 post minimum.
- Posts 1.10 high with the rings on the inner post faces (spec: above the tops): ACCEPT, as in the reference; total height 1.10 = catalogue.
- Width 3.06 vs the catalogue 3.2: ACCEPT (-4.4 %, within the 5 % rule); posts at X +-1.45 as the spec. Record 3.06 x 0.90 x 1.10 in the catalogue.
- Cloth ends at X +-1.16 (spec +-1.30), so the cords are visible: ACCEPT.
- Rings Ø0.16, rod 0.04 (spec about Ø0.12 / 0.035), 280 tris: ACCEPT, reads from 10 m and above the 0.03 minimum; iron slot 13 as in STR-02.
- Cord tips 5 mm proud of the gathered cloth end: ACCEPT, visible only close up.
- Tris 784/1000 and no LOD: fine; the reference (cloth, beam, posts, rings) is equally simple, nothing measurable missing.
- Wood consistency with STR-01/FUR-01: pass, slot 0 `#B5835A` as the arch, pergola and the swing frame; the darker slot 1 is not used on this model.

Unity import checks flagged (for Э8, not verifiable here):
- The model is X- and Y-symmetric, so the series X-flip does not matter; one static mesh, pivot at the footprint centre.
- Colliders: boxes for the two feet and posts; the cloth should not block (decoration height 0.59-0.84 above the ground). The beam dip (bottom 0.13) can be left without a collider.

## FUR-03 Bistro_Table (+ _White) (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_FUR-03_FUR-03.png`; full preview also viewed. `_White` (same vertices, slot 10) not visually checked (no variant preview). Tris 1000/1000, curl sizes and ground contact are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FUR-03.3d.md`. Budget 1000 (raised from 500 by the orchestrator, option C) accepted.

| Criterion | Result |
|---|---|
| Silhouette | pass: round 12-sided top on a three-legged iron tripod with outward foot curls and short scrolls under the top; reads as a wrought-iron bistro table, not a picnic table |
| Signature feature (S-curved legs with curled feet, hub scrolls) | pass with notes: the legs have an S sweep and round curled feet (0.126 across); the hub scrolls under the top are smaller, less ornate and mostly in the shadow of the top, so they read as a dark cluster; legs and feet carry the read |
| Proportions | pass: 0.70 x 0.70 x 0.75; legs end at r 0.28, curls inside the top outline; the lower hex hub (0.40-0.46) and the tall scroll zone follow the reference |
| Colour / palette | pass: single slot 13 `#3A3A3F`, matte, the same cell as STR-02 and ORN-05; `_White` is slot 10 on the same vertices |
| Readability at 128 px | pass: top disc, three legs and curled feet read; the hub scrolls become a dark knot under the top |
| Difference from Farm Market `FMS_Deco_Table_Set` | pass: a round iron tripod with S legs and curled feet; the Market set is rectangular plank picnic furniture |
| Iron consistency with STR-02 / ORN-05 | pass: 6-sided rods (0.036 legs, 0.030 scroll bars), same `s_curve()` scroll wording, curls >= 0.10, same slot; STR-02 itself is 8-sided and ORN-05 uses square scroll bars: three variants of one wrought-iron family, all at or above the 0.03 minimum |

Deliberate deviations judged:
- Budget 1000 (2x the original 500), rods 6-sided: ACCEPT. The spec parts do not fit 500 (the builder measured 1140-1488 for 8-sided variants), and the orchestrator decision follows the STR-02 precedent. The budget is spent on round foot curls (8 segments) so they read at 128 px.
- Hub lower and hex (0.40-0.46, spec 0.58-0.68), scrolls above the legs rather than between them: ACCEPT, measured from the reference; this gives the tall scroll zone.
- Rim lip 0.013 and field at 0.737 (spec 0.03 rim on a 0.04 disc, which would sum to 0.77): ACCEPT; the 0.75 total is the functional size.
- Underside ring as a frustum 0.46 -> 0.42: ACCEPT (reference). Feet curl outward to r 0.346, inside the 0.70 top: ACCEPT.
- Hub scrolls less ornate than the reference: ACCEPT (budget).
- FUR-04 reuse: the helpers (`foot_leg`, `s_scroll`, `hermite`, `oct_sec`) are documented in `build.py`; FUR-04 must keep this wording (6-sided rods 0.036 / 0.030, slot 13 / 10, curls >= 0.10, 8-segment foot curls) and its raised budget (700 -> 1400).

Unity import checks flagged (for Э8, not verifiable here): static mesh, pivot at the footprint centre, symmetric, flat of the top to the front; collider one box 0.7 x 0.7 x 0.75 or a cylinder; verify `_White` once visually (very cool white).

## How to fix
- Batch 3 needs no fixes (10 items, all 🟡). Nothing to re-export.
- Optional polish only, see the per-item notes; after any later fix: re-export, re-import verify, new preview, second sheet pass; append a results table below.
