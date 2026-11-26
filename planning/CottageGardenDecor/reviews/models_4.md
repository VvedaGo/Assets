# CottageGardenDecor: reference review, batch 4 (2026-11-26)

Every preview `art/CottageGardenDecor/Previews/FMS_Garden_<ID>_Preview.png` compared with `planning/CottageGardenDecor/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.
Status: FINAL. All 9 batch-4 items reviewed (FUR-04, FUR-05, PLT-04, PLT-05, PLT-06, TOP-01 (+ _Rose), TOP-02, TOP-03, TOP-04). No second pass needed.

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 1 | TOP-02 |
| 🟡 Pass with notes | 8 | FUR-04, FUR-05, PLT-04, PLT-05, PLT-06, TOP-01, TOP-03, TOP-04 |
| 🔴 Fix | 0 | Silhouette, signature feature or proportions clearly off |
| ❓ Decision | 0 | Deliberate deviation; the owner decides |

Cross-cutting issues (batch 4):
1. All 9 items pass, no geometry fixes. Palette effects (red brighter, cream and white cooler, wood paler than the references) are the palette decision, not defects.
2. The reference wins where no functional size is involved (FUR-05 seat bar 0.36, PLT-06 footprint 0.77 x 0.79, TOP-02 base 0.30); functional sizes were kept (FUR-04 seat top 0.45, PLT-05 clearance, PLT-04 flat back plane).
3. Nothing was too tight for its signature (FUR-04 1096/1400, FUR-05 384/400, PLT-04 498/500, PLT-05 888/900, PLT-06 684/700, TOP-01_Rose 848/860, TOP-03 672/900); no raise needed.
4. Plants and topiaries reuse rose_bloom_v2, cups toward the viewer, green stems; plants with a front (PLT-06 cups, TOP-01_Rose blooms, PLT-04 leaves) must be placed with the front toward the path or camera.
5. Variants without previews (FUR-04 `_White`, FUR-05 `_Blue`, PLT-06 `_White`; TOP-01 `_Rose` judged from a check render) need one render each at assembly.

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
| FUR-04 | Bistro_Chair (+ _White) | Hoop leans back 15.4 deg (reference near upright), 6-sided legs (reference square), branch curl slightly larger than the reference, seat 12-sided 0.05; 1096/1400; `_White` not previewed. See the FUR-04 section. |
| FUR-05 | Deck_Chair (+ _Blue) | Reference layout instead of the spec table (A-frame rear legs, long rails, no middle bar, round top bar), seat bar 0.36 (spec 0.45), 0.68 x 1.06 x 0.90 (catalogue 0.6 x 1.0), red brighter and cream whiter (palette), 384/400, `_Blue` not previewed. See the FUR-05 section. |
| PLT-04 | Ivy_Patch | Reads as a diamond-leaf ivy panel; outline more ragged and less square than the reference, layer contrast lower (front leaves bright, dark mat less dominant), leaves read a little gem-like, small sky gaps at the left, brown vines in few long gaps; 498/500, no raise needed. See the PLT-04 section. |
| PLT-05 | Wisteria_Drape | Leaf band is eight big smooth-looking 48-tri drops, deeper and chunkier than the reference's small leaves; racemes start below the band on short green stalks (spec -0.04); slimmer racemes; flat drop tops visible from above; vines mostly hidden; depth 0.47 (catalogue 0.6); 888/900. See the PLT-05 section. |
| PLT-06 | Hollyhock (+ _White) | Footprint 0.77 x 0.79 (catalogue 0.6), cups face the front half only (backs seen from behind), left cups side-on in the 3/4 view, no bracts, stems slot 0 (spec 2), leaf plates slightly gem-like and smaller in mass than the reference rosette; 684/700; `_White` not previewed. See the PLT-06 section. |
| TOP-01 | Topiary_Standard (+ _Rose) | Ball a little rounder than the reference, light facets brighter and more contrasty, soil disc larger; `_Rose` blooms on the ball rim are seen edge-on, upper and front ones read as roses; 168/500, `_Rose` 848/860. See the TOP section. |
| TOP-03 | Topiary_Spiral | Spiral with real gaps, but more ragged and thinner than the reference smooth wide ribbon, light/dark facets slightly checkered, upper turns narrow; 672/900. See the TOP section. |
| TOP-04 | Topiary_Tiered | Bottom ball narrower than the reference (catalogue 0.70 kept), light facets brighter; 328/600. See the TOP section. |

## ✅ Pass
- Topiary: TOP-02 (Topiary_Cone)

## FUR-04 Bistro_Chair (+ _White) (reviewed 2026-11-26)

Sheet: `%TEMP%/pack_review/sheet_00_FUR-04_FUR-03.png` (FUR-04 plus FUR-03 to judge the set); full preview also viewed. `_White` (same vertices, slot 10) not visually checked (no variant preview). Tris 1096/1400, size, curl sizes, ground contact and the set render are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FUR-04.3d.md`. Budget 1400 (orchestrator note, 700 -> 1400) accepted; 1096 is enough, the reference has nothing finer.

| Criterion | Result |
|---|---|
| Silhouette | pass: round seat on four splayed legs with a ring brace, open round-topped hoop back with an S-scroll; reads as a bistro chair, not a plank Market chair |
| Signature feature (hoop + S-scroll + branch curl) | pass: lower spiral standing on the seat, spine leaning right, upper bowl merging into the crown, small separate curl upper right; same layout as the reference |
| Proportions | pass: 0.41 x 0.45 x 0.85, seat top 0.45 (functional); hoop widest at about 57 % of its height as in the reference; the hoop leans back more than the reference |
| Colour / palette | pass: single slot 13 `#3A3A3F`, matte, same cell as STR-02 / FUR-03 / ORN-05; `_White` = slot 10 on identical vertices |
| Readability at 128 px | pass: the scroll sits in the open hoop against the light background and is the clearest part of the chair at sheet size (about 200 px tall); seat, ring and legs read; the branch curl and the S merge into one scroll mark at the smallest size, which is fine |
| Set with FUR-03 | pass: same iron cell, same rod weight (0.036 legs / 0.030-0.034 bars), same 12-sided flat-to-front seat/top wording, seat 0.45 under a 0.75 top; reads as one wrought-iron set. FUR-04 has no foot curls (reference chair has straight legs), FUR-03 has |
| Iron consistency with STR-02 / FUR-03 / ORN-05 | pass: 6-sided rods >= 0.03, curls >= 0.10 (0.134 / 0.102), slot 13; same helpers as FUR-03 |

Deliberate deviations judged:
- Rods 6-sided (spec 8-sided): ACCEPT, orchestrator note and FUR-03 precedent.
- Seat 12-sided, 0.41 across flats, 0.05 thick with a 0.016 / 0.012 top chamfer (spec 10-sided Ø0.40, 0.04): ACCEPT, from the reference band and the FUR-03 top; seat top 0.45 kept. The chamfer is the reference's light band, a single large edge, within STYLE.
- Hoop links not separate, ends sunk 0.022 into the seat at u +-0.14: ACCEPT, as the reference; every part touches the seat, nothing floats.
- Hoop tilt 15.4 deg and top 0.045 behind the seat edge (spec 0.06, reference near upright): ACCEPT. It gives the depth 0.45 inside the 0.50 limit and a comfortable back; the silhouette in the 3/4 view reads the same. Optional: none.
- S plus a small branch curl (spec: one S touching the hoop at both ends): ACCEPT, the reference shows exactly this; the branch is 0.102 across, slightly larger than the picture, due to the 0.10 minimum.
- Ring Ø0.316 (spec 0.30), sunk into the legs: ACCEPT, no floating brace.
- Legs 6-sided where the reference looks square: ACCEPT, series rod wording; no visible difference at game size.
- Legs straight with 0.05 splay, no foot curls: ACCEPT (spec and reference).
- Iron dark, scroll in front of a dark seat only in the lower spiral: ACCEPT; the batch-3 warning about dark iron in shadow does not apply, because the scroll stands in the open hoop against the background.
- Differs from Farm Market `FMS_Deco_Table_Set` benches: pass.

Unity import checks flagged (for Э8, not verifiable here):
- Blender -Y = front becomes Unity +Z under the series X-flip assumption; the chair is X-symmetric except the back scroll, so after the flip the S sits mirrored (decorative, no check needed). The hoop is on Unity -Z.
- Static mesh, pivot at the footprint centre on the ground; collider: one box about 0.41 x 0.45 x 0.45 for the seat and legs, or box plus thin hoop box; the hoop and scroll need none.
- `_White`: verify once visually (cool white, as FUR-03 `_White`); with FUR-03 `_White` it makes the white set.

## FUR-05 Deck_Chair (+ _Blue) (reviewed 2026-11-26)

Sheet: `%TEMP%/pack_review/sheet_00_FUR-05_FUR-05.png`; full preview also viewed. `_Blue` (same vertices, stripe slot 5 -> 15) not visually checked (no variant preview); verify one render at assembly. Tris 384/400, checks and clearances are from the builder notes, not re-measured.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FUR-05.3d.md`.

Open question: is 0.45 a functional seat height? Decision: NO, accept 0.36. The spec lists 0.45 only as the Y of the front bar in a part table, an estimate from the first sketch; it is not a stated functional size (unlike FUR-04's seat top 0.45 at a table, the swing clearance or the walk-through openings), nothing mates with this chair, and no collision or clearance depends on it. A deck chair is a low sling seat: cloth low point 0.317, bar top 0.39, armrest 0.55 to 0.58, all measured on the reference, which clearly shows the bar near 0.6 of the armrest height. Raising the bar to 0.45 would move it above two thirds of the armrest height and change the silhouette the reference shows. Action for the coordinator: no catalogue seat-height number is needed; record 0.68 x 1.06 x 0.90.

| Criterion | Result |
|---|---|
| Silhouette | pass: reclined A-frame with long rails, rear legs to the ground, wide armrests, a sling from the top bar to the front bar; matches the reference pose, folding deck chair read |
| Signature feature (striped sling cloth) | pass: five lengthwise stripes red / cream / red / cream / red over a sagging seat, wrapped on the front bar with a red hem band; a thick shell, not a card |
| Proportions | pass with notes: 0.68 x 1.06 x 0.90; +13 % wide and +6 % deep from the camera fit (catalogue 0.6 x 1.0); height 0.90 as catalogue; the sheet shows the same ratio as the reference |
| Colour / palette | pass: stripes red slot 5 and cream slot 3 (not cream/blue like FUR-02, so the two are clearly distinct), wood slot 0 with the dark foot bar slot 1; red brighter and cream whiter than the reference (palette) |
| Readability at 128 px | pass: bold red/cream stripes dominate; the frame members (0.05-0.06 wood, armrests 0.09) read as clear tan bars, none thinner than 0.05 |
| Style match | pass: flat matte facets, wood slot 0 same as STR-01 / FUR-01 / FUR-02, same chunky square section wording; stripes follow the FUR-02 wording |

Deliberate deviations judged:
- Frame follows the reference (long rails to the front legs, separate rear A-frame legs, foot bar between the rear legs) instead of the spec's rails standing on their own feet: ACCEPT, the reference is unambiguous and the result is a stable unfolded deck chair; no floating parts, per builder checks.
- Round 6-sided top bar (spec square), no middle bar, 6-sided front bar: ACCEPT (reference; the middle bar would sit hidden under the sag; 6 sides keep the budget).
- Front bar 0.36 and armrest 0.58 -> 0.55 dipping to the back (spec 0.45 / 0.55 -> 0.62 rising): ACCEPT, see above.
- Size +13 % / +6 %: ACCEPT, beyond the 5 % rule but from a numeric camera fit on the reference, no functional size; the width shows in the demo spacing (0.68 plus 0.3 clearance).
- Cloth 0.47 wide, stripes 0.094, gravity sag with the low point near the front bar: ACCEPT (reference seat flattens near the front); cloth clear of the rails with 0.02 gap.
- Frame 0.05-0.055 x 0.06: ACCEPT, the spec's thin-frame exception, at the 0.05 minimum.
- Budget 384/400: ACCEPT, tight but every spec part is present; no raise needed.
- Seat has a mild fold where the span meets the front-bar wrap: ACCEPT, visible only up close and part of the flat-shaded look.

Unity import checks flagged (for Э8, not verifiable here):
- Blender -Y = front becomes Unity +Z; the chair is X-symmetric, so the X-flip does not change the look. Static mesh, pivot at the footprint centre on the ground.
- Colliders: one box about 0.68 x 1.06 x 0.58 or two boxes (front frame, rear legs); the cloth need not block. `_Blue`: verify once.

## PLT-04 Ivy_Patch (reviewed 2026-11-26)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-04_PLT-04.png`; full preview also viewed. Tris 498/500, ATTACH and MOUNT checks (MOD-03, MOD-01), flat back and FBX are from the builder notes, not re-measured. Seen from the 3/4 camera the preview shows the front of a wall patch, so its apparent width is a little narrower than in the frontal reference.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `PLT-04.3d.md`.

Is 500 too tight? No. The reference is made of plain 4-facet pyramid leaves on a dark mat with brown zigzag vines, and the model has all of it: 43 leaves (reference shows about 45), a dark back mat, three vines. More tris would only add leaves or fold ridges the 128 px thumbnail cannot show, and the reference leaves are not folded. No raise.

| Criterion | Result |
|---|---|
| Silhouette | pass with notes: an upright patch about 1.04 x 1.01 of overlapping diamond leaves; the reference outline is closer to a square, here the rim is ragged with single leaves and a notch at the top left; sky shows through small gaps at the left edge. Still a plant patch and not a slab |
| Signature feature (carpet of rhombus leaves in 3 tones, vines) | pass: dark mat, mid-green layer, bright front leaves, light accents on 4 leaves, brown vines visible in a few gaps; no flowers, no alpha cards, closed solids |
| Proportions | pass: 1.041 x 0.124 x 1.010 vs 1.0 x 0.15 x 1.0; leaves 0.17-0.25 as measured on the reference (spec 0.14 was too small); depth under 0.15 |
| Colour / palette | pass with notes: atlas F slots 3 / 2 / 0 / 1 / 13, the same greens as the PLT-01 bush (0 `#6E9F4A`, 1 `#8AB257`, 2 `#4E7A3A`) and the same bark cell; consistent with PLT-01..03 and `M_Garden_Flora`. Front leaves are brighter and more uniform than the reference, and the dark mat shows less, so the layer contrast is lower (lighting and the 24 front leaves) |
| Readability at 128 px | pass: green faceted leaf mass with a few brown vine lines; reads as ivy on a wall rather than as a bush, because it is flat-edged vertically with a ragged outline; vines are thin but only accents |
| Style match | pass with notes: flat matte facets, no outline; the large pyramids look somewhat like gems or octahedrons from this angle, but the reference leaves are the same shape, and the spec says rhombus only |

Deliberate deviations judged:
- Leaf size 0.17-0.25 (spec 0.14 x 0.10), 19 middle + 24 front (spec 24 + 14): ACCEPT, measured on the reference (PIPE-04: the reference wins).
- Leaf a closed 6-tri pyramid with a flat base, not the folded 8-tri bipyramid: ACCEPT (reference leaves are 4-facet pyramids; saved tris pay for more leaves). No ridge fold; "closed solid" is respected.
- Back layer one diamond-tiled closed shell (25 pyramids) with one flat back face, no random rotation: ACCEPT. It is the right way to keep Z = 0 exactly flat with no z-fighting; MOUNT OK on MOD-03 (back 1 mm in front of the coping face) and MOD-01.
- Vines 3-sided prism r 0.02 (spec 6-sided Ø0.035), 6 segments: ACCEPT. Width 0.035-0.04 across the corners is at the spec value; the vines are the only brown, and the series rule against bare brown stalks is about plant stems standing free, while here the reference shows the vines.
- Size 1.04 wide with tips (limit 1.0 + 0.04): ACCEPT; two patches at pitch 1.0 cover one 2.0 bay.
- Depth 0.124, leaf bases pushed back until touching the layer behind (no floating): ACCEPT.
- Builder's remaining notes (thinner zigzag rim, dark mat diamonds at the top corners, fewer/longer vine gaps): ACCEPT; optional.

Optional (no re-review): recolour 4-6 of the 24 front leaves to slot 2 to bring the layer contrast closer to the reference (same vertices, UV only); close the small notch at the left edge by moving one leaf 0.05 in.

Unity import checks flagged (for Э8, not verifiable here):
- Blender -Y = front becomes Unity +Z, so the back plane is Unity Z 0 (leaves toward +Z). Place on MOD-03 with the back on the wall face; on the wall body (face at 0.20) there is a 21 mm air gap, on the coping (0.22) it is flush. The patch is mirror-asymmetric (random leaves), so after the series X-flip the arrangement is mirrored; harmless.
- Static mesh, pivot at the bottom-edge centre on the back plane, no collider; uses `M_Garden_Flora`.

## PLT-05 Wisteria_Drape (reviewed 2026-11-26)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-05_PLT-05.png`; full preview also viewed. Tris 888/900, ATTACH and MOUNT (STR-04, top flush on the beam underside, 0 vertices in the beam or posts), gaps and FBX are from the builder notes, not re-measured. The reference is a near-frontal picture and the preview a 3/4 view, so rows overlap more in the preview and some racemes stand behind the front drops.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `PLT-05.3d.md`.

Decisions you asked for:
- Lowest tip 1.384 m above the ground: ACCEPT, racemes stay. The drapes hang under the two side beams of the pergola (beam axis Z +-1.5, depth 0.47, so they reach only Z +-1.27 at most) and the walk path is the 3.0 m bay between those beams, over 2.5 m of it free of any drape. The spec itself allowed a lowest tip of 1.34, so 1.384 is 4 cm better. The drape is decoration with no collider, so it blocks no one even where a character brushes the edge. Shortening the racemes would remove the long/short rhythm that is the signature in the reference. Coordinator action for CMP-02: hang the four drapes under the side beams, not over the central axis, and keep the drape out of the centre line of the entrance.
- Is 900 too tight? No. The reference has 8 drops, 8 racemes of two beads and a tip, and brown vines; the model has all of them with racemes at 46 tris (spec estimate 36). The weaker items (smooth drops with 48 tris, vines hidden, slim racemes) are tuning rather than budget limits: the drops are chunky because they are big, not because tris are missing. No raise.

| Criterion | Result |
|---|---|
| Silhouette | pass: a horizontal green band with lilac and one-two white racemes hanging in a long/short rhythm; reads as a wisteria drape at once, including from the 3/4 camera |
| Signature feature (cone racemes under a leaf band, lilac plus white) | pass: faceted two-bead racemes ending in a point, lilac slot 9 with white slot 8 on two (X -0.09 and +0.46, as the spec), light tips on lilac as the spec; same read as the reference |
| Proportions | pass with notes: 1.508 x 0.470 x 0.856; hang 0.856 under 0.90; the band is deeper and the drops bigger than in the reference (reference leaves are small and spread), racemes slimmer (body 0.50-0.54 vs about 0.43) |
| Colour / palette | pass: atlas F slots 0 / 1 / 2 greens (same as PLT-01), 9 lilac, 8 white, 13 bark vines, stalks slot 2 green; consistent with PLT-01..03 |
| Readability at 128 px | pass: green band, lilac blobs and a white one hang clearly; vines are a brown accent at the ends; stalks are small green ticks |
| Style match | pass: same domed drop look as the series, flat matte facets, no cards; the drops show a few large smooth-looking faces (48 tris), but remain faceted; "no brown lollipop stalks" respected (green 3-sided stalks 0.027 across, visible length 0.035) |

Deliberate deviations judged:
- Racemes start below the leaf band (tops -0.25 to -0.32, spec -0.04) with leaf drops to -0.24 / -0.29 (spec -0.02 to -0.16): ACCEPT, measured on the reference; the long order (X -0.46 and +0.28 longest) is from the reference, not the spec; total hang 0.856 within 0.90.
- Depth 0.47 (catalogue 0.6, racemes at Z +-0.12 not +-0.20): ACCEPT, keeps the stalks short and vertical; the 0.10 beam is still straddled. Record 1.51 x 0.47 x 0.86 in the catalogue.
- Vines 4-sided 0.05, 4 segments, stalks 3-sided slot 2 (spec 8-sided slot 13 and 6-sided): ACCEPT, budget, and the series rule on green stems.
- Drops are half-balls with a flat top at Z 0 (visible from above as light lids in the standalone preview): ACCEPT, the top is the attachment plane and is hidden by the beam; the alternating 0 / -1.5 mm tops avoid coplanar overlaps.
- Raceme ends at X +-0.62 (spec +-0.65): ACCEPT.
- White speckle facets in the lilac tips (spec "liveliness", absent from the reference): ACCEPT, as specified.

Optional (no re-review): widen the long racemes slightly (belt radii x 1.08) to match the reference's heavier look; shift the vines 0.02 lower so they show more between the drops.

Unity import checks flagged (for Э8, not verifiable here):
- Pivot at the centre of the flat top face; place it at the beam underside Y 2.24, the top face flush. The model is asymmetric in X (racemes and drops), so the series X-flip mirrors the order of long/short racemes; harmless.
- Atlas F / `M_Garden_Flora`; no collider. Hang under the pergola side beams only (see above).

## PLT-06 Hollyhock (+ _White) (reviewed 2026-11-26)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-06_PLT-06.png`; full preview also viewed. `_White` (same mesh, cups 6/7 -> 8) not visually checked (no variant preview); verify one render at assembly. Tris 684/700, cup clearances and FBX are from the builder notes, not re-measured. The reference is a front view, the preview a 3/4 view, so the left-facing cups look side-on in the preview.

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `PLT-06.3d.md`.

Budget: 700 is not too tight, no raise. All parts of the spec are there (3 stems, 15 cups, 3 buds, 6 leaf plates); the unbuilt items (bracts at the nodes, a 6-facet bud) are small and would not show at 128 px.

| Criterion | Result |
|---|---|
| Silhouette | pass: a narrow vertical spire of three tall green stems of different height (1.80 / 1.57 / 1.39) over a ground rosette; clearly not the Farm Nature sunflower (single head) or lavender (low tuft) |
| Signature feature (cups along the stems, yellow centres, rosette) | pass: 15 pink cups with yellow centres up the upper half of each stem, a bud on each tip, leaf rosette at the foot; the cup is a shallow wide cup, not the rose bloom |
| Proportions | pass with notes: 1.80 high as catalogue, footprint 0.77 x 0.79 against 0.6 (+28 %), from the reference (stem tips spread about 0.6, rosette about 0.85), kept narrower than the reference; no functional size involved; record 0.77 x 0.79 x 1.80 |
| Colour / palette | pass: atlas F green slots 0 / 1 / 2, pink 6 / 7, yellow 11, the same pink and green cells as PLT-01 and the `_Pink` roses; stems are slot 0 (mid green) and the dark green only on the calyx and undersides, so no brown stalks |
| Readability at 128 px | pass: three green lines, pink dots with yellow points and a green rosette; the stems are 0.038-0.06, above the 0.035 minimum, and hold |
| Style match with PLT-01..03 | pass: flat matte facets, closed 28-tri shells, cups tilted toward the viewer (series lesson); not copies of the rose cups, so it differs in kind, as the spec requires; leaf plates are 18-tri folded domes in three green tones |

Deliberate deviations judged:
- Cup 28 tris and one closed shell (spec 24, open cup): ACCEPT, Cull Back and a closed solid are the series rules; yellow centre Ø0.052 (spec 0.04) reads at 128 px.
- Cups in a zigzag facing the front half, tilted 40 degrees (spec 144 degree spiral, 50 degrees): ACCEPT, consistent with the reference and the batch lessons. Consequence for assembly: the plant has a FRONT; from behind the cups show light-pink backs (the builder checked it). Place with the front to the path, or rotate the prefab; note for the CMP / demo items.
- Cup heights on the upper half only (fractions about 0.5-0.9), rim Ø0.148 to 0.140 (spec 0.16 to 0.10): ACCEPT, measured on the reference (cups nearly equal); the lower 0.6 m stays bare green stem, as in the reference.
- Footprint 0.77 x 0.79: ACCEPT, as above; keep 0.8 m clearance in the demo.
- Leaf plates: own 18-tri folded dome, 0.34-0.37 x 0.32-0.35 (spec 0.26 x 0.20): ACCEPT, matches the large rosette in the reference; they look somewhat pointed and gem-like, which the builder notes too; the reference is softer. Optional.
- Stems slot 0 not slot 2: ACCEPT, the reference stems are mid green; slot 2 reads too dark; in line with the "no brown or bare stalks" lesson.
- Lean 15-20 degrees low and vertical at the top, 3 segments with one visible bend (spec 3-8 degrees straight): ACCEPT, matches the reference curve; the bend on the left stem is visible as a kink; optional.
- No green bracts, 3-faceted buds (reference about 6 facets): ACCEPT, budget; the buds read as green points at the tips.

Optional (no re-review): lift two of the left-stem cups a few degrees toward the front (azimuth 230-245 -> 250-260) so they are less side-on in a 3/4 view; scale the leaf plates 1.05 wider for a fuller rosette.

Unity import checks flagged (for Э8, not verifiable here):
- Blender -Y = front becomes Unity +Z under the series FBX assumption; the cups face that half. After the X-flip the plant is mirrored left-right; harmless.
- Pivot at the centre of the foot on the ground; atlas F / `M_Garden_Flora`; collider: none, or a thin capsule at the stems (about Ø0.15 x 1.8); `_White` verify once.

## TOP-01 Topiary_Standard (+ _Rose), TOP-02 Topiary_Cone, TOP-03 Topiary_Spiral, TOP-04 Topiary_Tiered (reviewed 2026-11-26)

Sheets: `%TEMP%/pack_review/sheet_00_TOP-01_TOP-03.png` (TOP-01, TOP-02, TOP-03) and `%TEMP%/pack_review/sheet_01_TOP-04_TOP-04.png`. `_Rose` judged from the check render `%TEMP%/assetnew_check/TOP-01/TOP-01_Rose_check.png` (same camera, not in `art/CottageGardenDecor/Previews/`; one preview per ID). Tris, checks and FBX (all four built by one registry script) are from the builder notes, not re-measured.

Verdicts: TOP-01 🟡, `_Rose` 🟡, TOP-02 ✅, TOP-03 🟡, TOP-04 🟡. No FIX, so no "## Fix 1" in any `TOP-0x.3d.md`.

| Criterion | TOP-01 (+ _Rose) | TOP-02 | TOP-03 | TOP-04 |
|---|---|---|---|---|
| Silhouette | pass: faceted ball on a long bare stem over a soil disc; a lollipop standard, not a ground bush | pass: sharp 12-faced cone with 0.26 of bare stem visible over the soil disc; same shape as the reference | pass with notes: a helical band around a cone silhouette with real gaps, 3.5 turns; more ragged than the reference's smooth ribbon, upper turns narrow | pass with notes: three decreasing balls on a short stem; bottom ball narrower than the reference |
| Signature feature | pass: clipped sphere on a stem; `_Rose`: 10 red roses on the ball | pass: clean planar faces from base to apex | pass: gaps open down to the trunk (0.10-0.20); band 0.28 thick | pass: stacked balls forming one mass |
| Proportions | pass: 0.58 x 0.61 x 1.39 (catalogue 1.4); `_Rose` 1.45 | pass: 1.60 tall, cone 1.30 on a stem from 0.30 (spec 0.20), as in the reference | pass: 0.735 x 0.668 x 1.80; reference about 0.79 wide | pass with notes: 0.674 x 0.692 x 1.68, radii 0.36 / 0.26 / 0.165; bottom ball less wide than the picture, catalogue kept |
| Colour / palette | pass: boxwood slot 3 plus light facets slot 0, soil 12, bark 13; light facets brighter and more contrasty than the reference's | pass: same two greens, regular light/dark face columns | pass with notes: light share 1 in 4, facets slightly checkered | pass with notes: as TOP-01 |
| Readability at 128 px | pass | pass | pass: the spiral and the gaps showing the trunk read | pass |

Key checks:
- Not Farm Nature `FMS_Bush_Round` standing on the ground: pass. TOP-01 has 0.76 m of bare stem and TOP-04 0.21 m, and a disc under every ball. Not the spruce (TOP-02): pass; a smooth-sided 12-faced cone with no tiers, branches or needles and a bare stem, a clean clipped geometric shape.
- Clipped look: pass; facet size follows the references (80-tri icosphere shows about 5 facets across, as the reference), straight edges, jitter 0.02 only; no leaves or cards.
- Greens consistent with PLT-01..06: pass; slots 3 / 0 / 2 of atlas F (`#3F6B3A`, `#6E9F4A`, `#4E7A3A`), bark 13, soil 12; same wording and `M_Garden_Flora`.
- `_Rose` blooms read from above: pass with notes. The ten blooms (rose_bloom_v2, 68 tris, tilted 22 degrees toward the viewer) read as red roses on the top and front of the ball (rims and bud tips visible); the ones on the silhouette edge are seen edge-on as red flaps, as expected on a sphere; none floats, calyxes are inside the ball. Reads as a standard rose at 128 px by red dots on green.

Deliberate deviations judged:
- Balls 80 tris (spec 320), light facets slot 0 (spec slot 2): ACCEPT. The references show about five big facets across the ball, and 320 tris read smooth and lumpy; slot 2 against slot 3 was nearly invisible, and slot 0 measures like the reference's light facets (about `#668B3A`). Consistent with the PLT-01..03 drops.
- `_Rose` budget 860 (spec 800, raised by the coordinator for ten rose_bloom_v2 blooms): ACCEPT; 848 used.
- TOP-02 base 0.30 and cone 1.30 (spec 0.20 / 1.40), jitter per face column: ACCEPT (reference measured; straight faces as the spec wants). 158/300; the unused budget is not a defect ("do not spend it on tiers").
- TOP-03 band section with 5 vertices, outer height 0.28 / inner 0.16 (spec 0.20 / 0.12), outer radius 0.36 to 0.07, width 0.735 (spec 0.7): ACCEPT, measured on the reference (bands about 0.29, small gaps); within 5 % of the catalogue. Exactly 3.5 turns, 56 segments, gaps real. Light share 1 in 4 was chosen to reduce a checkerboard; a little remains.
- TOP-04 radii 0.36 / 0.26 / 0.165, centres 0.60 / 1.15 / 1.535, all 80 tris (spec bottom 320): ACCEPT; bottom ball narrower than the reference, catalogue footprint 0.7 kept, balls overlap into one stack, bare stem 0.21.
- Soil disc 12-sided Ø0.50 closed (44 tris, spec 36) and 8-sided stem 44 tris: ACCEPT (manifold shells).

Optional (no re-review): lower the light facet share to 1 in 4-5 on TOP-01/04 (UV only); TOP-04 bottom ball radius 0.36 to 0.38 if the 0.7 footprint allows it.

Unity import checks flagged (for Э8, not verifiable here):
- All four: pivot at the centre of the soil disc bottom on the ground, static, atlas F / `M_Garden_Flora`; TOP-03 and `_Rose` are not mirror-symmetric (spiral handedness flips under the series X-flip, harmless). `_Rose` blooms face Blender -Y = Unity +Z: place the plant with the front toward the viewer.
- Colliders: TOP-01 capsule on the stem (about Ø0.07) plus a sphere on the ball, or one cylinder; TOP-02 cone box 0.65 x 1.3; TOP-03 cone box 0.7 x 1.8; TOP-04 capsule plus a box 0.7 x 0.7 x 1.1 over the balls; the disc needs none.

## How to fix
- Batch 4 (9 items) needs no fixes. Nothing to re-export.
- After any later fix: re-export, re-import verify, new preview, second sheet pass; append a results table below.

---

# SERIES SUMMARY: CottageGardenDecor, all 42 models (pilot + batches 1-4, 2026-11-26)

Reviews: `models_pilot.md` (3: WTR-03, PLT-01, STR-06), `models_1.md` (10), `models_2.md` (10), `models_3.md` (10), `models_4.md` (9). Colour variants are counted with their base model. Every item was judged on its paired sheet; technical checks (topology, FBX, SNAP/MOUNT) come from the builder notes.

## Totals per verdict (final state)
| Status | Count | IDs |
|---|---:|---|
| ✅ Pass | 3 | MOD-02, MOD-09, TOP-02 |
| 🟡 Pass with notes | 39 | all the rest (pilot 3, batch 1 9, batch 2 9, batch 3 10, batch 4 8) |
| 🔴 Fix (open) | 0 | none |
| ❓ Decision | 0 | none |

Returns (items that went back to the builder): PLT-01 (FIX in pass 1, Fix 2 in pass 2 with budget 1000 -> 2000, 🟡 in pass 3; became the plant anchor) and MOD-08 (Fix 1: budget 60 -> 80, pinwheel masonry, 🟡 in pass 2). Nothing else needed a second pass; no repair is open.

## Cross-cutting rules that held across the series
1. Palette (stone greyer, white cooler, wood paler, red brighter than the references) is the pack palette decision, not a defect; no per-model retint.
2. Functional sizes win over pictures (openings 1.2 x 2.1, seat tops 0.45, swing clearance, pond/wall contracts, mount planes); the reference wins elsewhere.
3. Budget raises were granted only with a measured reason (STR-02, FUR-03, FUR-04, PLT-01, MOD-08, TOP-01_Rose); under-budget models are fine where the reference is simple; nothing in batch 4 was too tight.
4. Iron family (STR-02, ORN-05, FUR-03, FUR-04): slot 13, rods >= 0.03, curls >= 0.10, 8- or 6-sided rods as budgeted. Organics: rose_bloom_v2, 80-tri domed drops, cups toward the viewer, no brown lollipop stalks.

## Open optional notes worth doing before the media (no re-review needed; UV or constant tweaks unless said)
- PLT-01 / PLT-02 / PLT-03: lift the two lowest front PLT-01 clusters about 0.05 m so the stems show; thicken the lowest 0.4 m of PLT-02 canes to Ø0.05; shorten the two PLT-03 red buds to about 0.09 and widen their base to Ø0.08.
- FLB-01 / FLB-02 / FLB-03: lower the soil valleys to about 0.12-0.14 (no tri cost) for clearer soil facets.
- ORN-03 `_Planted`: one leaf drop or bloom on the bare right vine; ORN-05 `_Feeder`: swap roof and body slots for a clearer split; WTR-01: widen only the light slot 9 face row of the streams if softer water is wanted.
- PLT-04: recolour 4-6 front leaves to slot 2 for layer contrast; PLT-05: slightly heavier long racemes, vines lower; PLT-06: two left cups turned to the front, leaf plates 1.05 wider; TOP-01/03/04: light facet share 1 in 4-5; TOP-04 bottom ball 0.38.
- Media: prefer STR-01 `_White` for the cream match and the `_Planted` beds for hero shots; there are no previews for variants (`_White`, `_Blue`, `_Pink`, `_Gate`, `_Planted`, `_Feeder`, `_Rose`), so render one of each at assembly.

## Consolidated catalogue size corrections (coordinator action)
- Pilot: WTR-03 0.60 x 0.60 x 0.70; PLT-01 1.05 x 0.88 x 1.09 (budget 2000); STR-06 3.58 x 3.58 x 4.0 (steps 0.33 deep, clear opening 1.27 x 2.1).
- Batch 1: PLT-03 height 0.54 (catalogue 0.40; arch with garland about 2.94 m).
- Batch 2: STR-02 1.48 x 0.46 x 2.50; STR-05 extent 3.00 x 3.50 x 2.62; STR-03 crown 2.25 (slats to 2.30); MOD-08 budget 80.
- Batch 3: WTR-01 2.4 x 2.4 x 2.42; WTR-02 0.90 x 0.59 x 1.30; ORN-01 0.45 x 0.45 x 0.955; ORN-02 0.243 x 0.226 x 0.45; ORN-03 0.6 x 0.6 x 1.2 (`_Planted` 1.384); ORN-04 0.60 x 0.38 x 0.88; ORN-05 0.56 x 0.28 x 1.70 (`_Feeder` 0.57 x 0.30); FUR-01 2.48 x 1.50 x 2.16; FUR-02 3.06 x 0.90 x 1.10; FUR-03 0.70 x 0.70 x 0.75 (budget 1000). Specs and STYLE: ORN-04 dividers slot 1, FUR-02 rings on the inner post faces, FUR-01 hangers at X +-0.84, WTR-01 basin 16 sides 0.34 high, ORN-03 on atlas F.
- Batch 4: FUR-04 0.41 x 0.45 x 0.85 (budget 1400, seat top 0.45); FUR-05 0.68 x 1.06 x 0.90 (front bar 0.36, no fixed seat height); PLT-04 1.04 x 0.12 x 1.01; PLT-05 1.51 x 0.47 x 0.86 (lowest tip 1.384 m under the 2.24 beam); PLT-06 0.77 x 0.79 x 1.80; TOP-01 0.58 x 0.61 x 1.39 (`_Rose` 0.58 x 0.61 x 1.45, budget 860); TOP-02 0.68 x 0.69 x 1.60; TOP-03 0.74 x 0.67 x 1.80; TOP-04 0.67 x 0.69 x 1.68.
- STYLE.md: the wood slot 2 row still lists the obelisk (built in slot 0); MOD-01 slats are built in slot 10.

## Consolidated Unity-import check list (Э8, not verifiable in the reviews)
Series assumption: the Unity FBX import negates X, so Blender (x, y, z) -> Unity (-x, z, -y); Blender -Y = front = Unity +Z. Verify one asset of each kind on the first import; fix by mirroring in build.py or rotating the prefab.
- Quadrants and contracts: MOD-06 arc must lie in +X/+Z with ends at (1,0,0) and (0,0,1) (else mirror or rotate -90 deg); MOD-08 corner built at Unity X <= 0, Z <= 0 (check the edge|corner join, else mirror or rotate 90 deg); MOD-07 basin to Unity +Z; MOD-09 slab raised 0.34 inside the mesh with the pivot on the ground (no prefab offset); STR-05 posts at Unity X +3.0 and beams +0.25 to +3.25 (else rotate the bay 180 deg about Y; placement STR-04 + 1.5, then +3.0); FLB-02 missing quadrant at Unity X > 0, Z > 0 (if flipped, mirror, rotation does not help); FLB-02/03 join FLB-01 by the kerb faces (check one run); WTR-02 basin to Unity +Z with the back face at Z 0 (MOD-03 back 0.22 from the wall axis).
- Orientation and decor: STR-01 `_Gate` hinge on the left post as seen by the viewer, open angle clamped to 90 deg; PLT-02 and MOD-05 follow the same flip; ORN-05 hook points to Unity -X (rotate 180 deg about Y if +X is wanted), `Hanging` is a static direct child of the root with its pivot at the hang point (Blender (0.296, 0, 1.454)); ORN-01 gnomon tall edge at Unity -Z; ORN-02 nose to +Z; ORN-04 open front to +Z; ORN-03/05 and their variants use atlas F; PLT-04 leaves toward +Z with the back plane at Z 0 (flush on the MOD-03 coping, 21 mm air gap on the wall body); PLT-05 pivot at the top face on the beam underside, hang under the pergola side beams, not the centre axis; PLT-06 cups and TOP-01 `_Rose` blooms face +Z, so those plants need their front toward the path; TOP-03 spiral handedness flips under the X-flip.
- Moving parts and LOD: FUR-01 `Seat` pivot at Unity (0, 2.04, 0), axis X, travel +-30 deg, `Seat_Low1` must follow it; STR-03 and STR-04 ship LOD1 (check the LOD group set-up; STR-03 bench legs collapse in LOD1); WTR-01 has 23 nodes (11 meshes + 11 `_Low1` + root) and the LOD group pairs each mesh; STR-06 five parts + five `_Low1`; ORN-03 `_Planted` has two mesh nodes (`_Body`, `_Plants`).
- Colliders and openings: STR-06 clear 1.27 x 2.1; STR-01 opening 1.2 x 2.1; STR-02 clear 1.20 (width 1.48 in a 1.5 m wall gap); STR-03 clear 1.56; PLT-03 garland no collider (arch with garland about 2.94 m, collider 2.4 m; it sits on the beam top at 2.46 and its foliage passes through 3-4 rafters); WTR-01 basin cylinder 2.4 x 0.34 plus a pedestal cylinder; ORN-01 box 0.40 x 0.40 x 0.95; ORN-03 box about 0.5 x 0.5 x 1.2 (ignore hanging blooms); ORN-05 capsule on the pole only; FUR-01 two frame boxes, no seat collider at rest; FUR-02 foot/post boxes, cloth not a blocker; FUR-03 box 0.7 x 0.7 x 0.75; FUR-04 box about 0.41 x 0.45 x 0.45; FUR-05 box about 0.68 x 1.06 x 0.58; PLT-04/05/06 none or a thin capsule; TOP-01..04 capsule on the stem plus a ball or cone volume.
- Variants to render once at assembly: STR-01 `_White`/`_Gate`, STR-07 `_White`, PLT-01..03 `_Pink`/`_White`, FLB-01/02/03 `_Planted`, ORN-02 `_Blue`, ORN-03 `_Planted`, ORN-05 `_Feeder`, FUR-03 `_White`, FUR-04 `_White`, FUR-05 `_Blue`, PLT-06 `_White`, TOP-01 `_Rose`.
