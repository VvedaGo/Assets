# CottageGardenDecor: reference review, batch 1 (2026-11-25)

Every preview `art/CottageGardenDecor/Previews/FMS_Garden_<ID>_Preview.png` compared with `planning/CottageGardenDecor/references/<ID>.png` on paired sheets
(`Tools/blender/compare_sheets.py`). Criteria: silhouette, signature feature, proportions, colour, readability at 128 px.
Technical checks (topology, gaps, FBX) are already done at build time; Unity import is a separate step.
Status: FINAL, all 10 batch-1 items reviewed (STR-01, PLT-02, PLT-03, FLB-01, MOD-01..MOD-06).

## Summary

| Status | Count | Meaning |
|---|---:|---|
| ✅ Pass | 1 (MOD-02) | Close to the reference, no edits |
| 🟡 Pass with notes | 9 | STR-01, PLT-02, PLT-03, FLB-01, MOD-01, MOD-03, MOD-04, MOD-05, MOD-06 |
| 🔴 Fix | 0 | Silhouette, signature feature or proportions clearly off |
| ❓ Decision | 0 | Deliberate deviation; the owner decides |

Cross-cutting issues (batch 1):
1. Palette vs references: stone renders greyer and white renders cooler than the beige/cream references (WTR-03, FLB-01, MOD-03, MOD-04, STR-01, MOD-01/02). This is the pack's palette decision (slots 10, 11, 12); the contrast between tones is lower than in the references. Do not retint per model; keep the two-tone splits visible.
2. Functional/contract sizes win over references (PIPE-04): arches, walls, edgings, gazebo are taller/lower/narrower than the pictures; accepted everywhere, builders documented it. References drawn squatter and cream.
3. Soft details in the references (softened edges, cap overhangs, brick two-tone) are flatter in the models because the specs forbid bevels beyond the stated ones: accepted.
4. Plants: rose_bloom_v2 + 80-tri drop cluster are the shared generator; keep clusters large, domed and overlapping; check the 128 px read.
5. Variants (_White, _Gate, _Pink, _Planted) have no own previews except the FLB-01 `_Planted` check render; verify variants visually once at assembly.

## Unity import checks flagged (not verifiable in this review; for Э8)
- MOD-06 arc quadrant: the arc is built in Blender -X/-Y assuming Unity negates X; after import it must lie in the +X/+Z quadrant of its pivot with ends at (1,0,0) and (0,0,1). If it lands in -X/+Z, mirror it in build.py or rotate the prefab by -90 degrees.
- STR-01 `_Gate`: gate hinge sits on the viewer's left post; Unity's X-flip may show it at X = +0.59; the open angle must be clamped to 90 degrees (contact with the front-left post at 91).
- PLT-03 garland: 0.54 m high decoration on the arch top; no collider; the arch with garland is about 2.94 m, collider stays 2.4 m.
- Same X-flip assumption underlies STR-01, PLT-02, MOD-05/06: verify one asset of each on first import.
- Collider openings: STR-06 clear 1.27 x 2.1; STR-01 opening 1.2 x 2.1.

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
| MOD-04 | Wall_Pillar | Ball 0.25 vs about 0.27, flush cap (no overhang), stone greyer. See the MOD-03 / MOD-04 section. |
| MOD-03 | Wall_Stone | Lower and longer than the reference (0.60 contract), coping contrast lower, stone greyer. See the MOD-03 / MOD-04 section. |
| MOD-01 | Lattice_Panel | Diamond lattice reads as the reference; slightly coarser than the reference, white cooler than cream. See the MOD-01 / MOD-02 section. |
| MOD-05 | Edging_Brick | Sawtooth reads like the reference; two-tone alternation subtler, edges sharp. See the MOD-05 / MOD-06 section. |
| MOD-06 | Edging_Brick_Curve | 90 deg arc reads, bricks lower than the reference (shared section); Unity X-flip of the arc to confirm at import. |
| FLB-01 | Bed_Straight (+ _Planted) | Base: soil flatter and one-toned vs the reference, stone greyer. `_Planted`: reads as a planted cottage bed; blooms are flat petal discs on short sticks, lilac spikes lavender-like. See the FLB-01 section. |
| PLT-03 | Rose_Climbing_Top (+ _Pink) | Reads as a rose garland; canes mostly hidden, 5 clusters read as separate lumps, closed buds look like red spikes, height 0.54 vs catalogue 0.40. See the PLT-03 section. |
| PLT-02 | Rose_Climbing_Side (+ _Pink) | Reads as a climbing rose; canes thin and straight-segmented, stump reads as a block, clusters flatter than PLT-01. See the PLT-02 section. |
| STR-01 | Arch_Wood (+ _White, _Gate) | See the STR-01 section below: taller/narrower than the reference (functional opening), light wood instead of cream (variant covers cream), roof beams read denser from a high front view. |

## ✅ Pass
- Modules: MOD-02 (Lattice_Post)

## STR-01 Arch_Wood (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_STR-01_STR-01.png`; full preview also viewed. Variant FBX `_White` and `_Gate` (+ .fbm) exist in `art/CottageGardenDecor/Meshes/`; not visually checked (no previews).

Verdict: 🟡 PASS with notes.

| Criterion | Result |
|---|---|
| Silhouette | pass: flat top of cross-beams on lintels/purlins, four posts, side lattice panels, clear open passage; reads as a garden arch/pergola gateway at 128 px |
| Signature feature (diamond lattice sides with real gaps, flat beam top) | pass: lattice is real geometry running into the rim, gaps visible; 5 top beams with sky gaps in 3/4 |
| Proportions | pass with notes: much taller and narrower than the reference (2.4 x 1.6 vs a squat reference), see decision |
| Colour / palette | pass with notes: light wood (slot 0) with dark beam ends, vs cream in the reference, see decision |
| Readability at 128 px | pass |
| Style match | pass: same atlas A, flat matte faces, chunky members as WTR-03 and STR-06; wood slot 0 reads clearly different from the white paint slot 10 used on STR-06, so the arch will sit well with the gazebo (use `_White` next to it for a matching pair) |

Deliberate deviations judged:
- Squatness: ACCEPT, no FIX. The opening 1.2 x 2.1 m is functional (walk-through, 2.1 m high, PLT-02/03 mounts) and wins over the picture (PIPE-04). The same rule was applied to STR-06.
- Colour light wood vs cream: ACCEPT. The catalogue defines the base as light wood and `_White` (slot 10, same vertices) as the cream/white look, which is what the reference actually shows; ship both. Recommendation for the owner: use `_White` for Asset Store hero shots if the match to the cream key art matters, but the base needs no change.
- Gate swing max 90 degrees instead of 100: accept; Unity must clamp the open angle to 90 (note for Э8/prefab). Alternatively move the hinge axis inward by 0.05 (one constant), but this is not required.
- Gate boards 0.18 wide instead of 5 x 0.10: accept (the 0.10 spec cannot fill the 0.98 m width).
- Beams 0.07 x 0.10 (STYLE chunk size): accept; reads like a closed slab from a high frontal camera only, open in 3/4. Optional: none.
- Lintels 0.14 wide and 0.04 longer on each side, lattice top at 2.09: accepted, as in the reference and for no coplanar faces.
- Lattice gap 0.10, denser reference would exceed the budget: accept (812/1000 base, 1264/1300 gate). The plant mounts `Plant_L/R/Top` exist per the notes; not opened in Blender here.

Notes (optional): the preview framing is fine; lattice slats are thin (0.03 as specified) but readable at the preview size, and may thin out at 128 px; acceptable by STYLE (>= 0.03).

## PLT-02 Rose_Climbing_Side (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-02_PLT-02.png`; full preview also viewed. `_Pink` FBX (+ .fbm) exists in `art/CottageGardenDecor/Meshes/`; not visually checked (no previews). The reference still shows the old cup bloom; the owner note (rose_bloom_v2, budget 1600) overrides it.

Verdict: 🟡 PASS with notes.

| Criterion | Result |
|---|---|
| Silhouette | pass: tall narrow vertical plant, drops alternating left and right up a braided cane, topped by a cluster and a rose; reads as a climbing rose, not as a bush or a tree, at 128 px |
| Signature feature (red roses on every cluster, braided canes) | pass: 8 roses plus 2 buds; the braid (crossing every 0.43 m) is visible between the drops |
| Proportions | pass: 0.70 x 0.24 x 2.01 m, fits the arch side panel (SNAP OK for STR-01/03, MOD-01, MOD-03, per builder); flat back plane at the pivot |
| Bloom tilt / read from above | pass: the v2 roses are tilted 18-24 deg to the front and show the petal rings and centre; clearly better than the PLT-01 top row, and all 8 read as roses |
| Colour / palette | pass: same atlas F cells and green split as PLT-01 |
| Consistency with PLT-01 | pass: same drop cluster shape and bloom, same palette and flat shading; clusters are slightly flatter and smaller (depth scaled 0.62) as needed for a flat-backed plant |
| Readability at 128 px | pass with notes: roses and drops read; the canes are thin (Ø0.03-0.045, STYLE minimum 0.03) and may fade at small sizes |

Deliberate deviations judged:
- Canes leave the stump separately (no short trunk), stump looks like a small block at the base: accept. Visual nitpick only; the reference has a thicker trunk that splits.
- Clusters flatter, no leaf tufts: accept (budget fully used, 1600/1600; PLT-01 tufts were barely visible anyway).
- Heights follow the reference rather than the spec list: accept (reference wins, PIPE-04).
- Old cup bloom replaced by rose_bloom_v2 x1.15 (rim Ø0.133): accept per the owner note.
- `_Pink` not checked visually; per the builder only outer petals 4 to 7 and inner 5 to 6, so the two-ring contrast is kept (unlike `_White` on PLT-01).

Optional improvements (not required): thicken the lowest 0.4 m of the canes to Ø0.05 so the base reads at 128 px; make the stump slightly taller and narrower than the current rock-like block.

rose_bloom_v2 as a shared bloom is confirmed good enough: it reads well when tilted toward the camera, as recommended in the PLT-01 pass 3 note.

## PLT-03 Rose_Climbing_Top (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_PLT-03_PLT-03.png`; full preview also viewed. `_Pink` FBX (+ .fbm) exists in `art/CottageGardenDecor/Meshes/`; not visually checked (no previews). The reference shows the old cup bloom; the owner note (rose_bloom_v2, budget 1100) overrides it.

Verdict: 🟡 PASS with notes.

| Criterion | Result |
|---|---|
| Silhouette | pass: long low row of domed green drops with roses on top (front row of 3, back row of 2), reads as a garland/rose crown for the arch top, not a bush or hedge, at 128 px |
| Signature feature (v2 roses on foliage, braided canes) | pass with notes: 6 roses read well from above (tilt 12-24 deg); the braid is visible only in two gaps (zig-zag cane pieces), mostly hidden by the drops |
| Proportions | pass with notes: 1.57 x 0.56 x 0.54 m, fits the STR-01 top (1.6 x 0.67), see decision |
| Colour / palette | pass: same atlas F cells as PLT-01/02 |
| Consistency with PLT-01/02 | pass: same cluster, bloom and flat shading; bloom x1.25 (rim Ø0.145) is larger than on PLT-02 (x1.15) but this matches the reference's big blooms on a low garland |
| Readability at 128 px | pass |

Decisions:
- Height 0.54 vs 0.40 in the catalogue: ACCEPT. It follows the reference (PIPE-04), it sits on the STR-01 top (measured: fits inside the beam footprint, mounted check render done) and over the STR-04 beam. Consequence: the arch with the garland is about 2.94 m tall; compositions, demo scene and colliders must use 2.4 m for the arch and add the garland as a decoration without collider. Record the new size in the catalogue/spec.md.
- Closed bud spike: ACCEPT, no FIX. The two buds (Ø0.068, 0.125 tall, slot 5) stand out as sharp red cones beside the roses; they read as thorns/spikes from the 3/4 view, though they are a minor accent. Optional: shorten to about 0.09 and widen the base to about Ø0.08 so they read as a bud, not a spike; or drop them if triangles are needed elsewhere. Not required.
- Canes mostly hidden: accept; they give the cue "growing on the beam".
- Five clusters read as separate lumps with gaps (the reference is one continuous overlapped row): accept; the clusters interpenetrate in the middle, and gaps give a better silhouette for a garland.
- Triangles 1064/1100: ok. SNAP checks for STR-01/STR-04 taken from the builder notes, not re-measured.

## FLB-01 Bed_Straight (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_FLB-01_FLB-01.png`; full preview also viewed. The single preview shows the BASE bed (empty, stone kerb with soil). `_Planted` (1456/1500 tris, LOD1 830) has no preview in the repo, so it was first not verifiable; later judged from `%TEMP%/assetnew_check/FLB-01/FLB-01_Planted_check.png` (same camera/light as the preview); files exist in `art/CottageGardenDecor/Meshes/` (`FMS_Garden_Bed_Straight.fbx`, `..._Planted.fbx` with .fbm) and `Blend/FMS_Garden_Bed_Straight_Planted.blend`.

Verdict (base): 🟡 PASS with notes. `_Planted`: 🟡 PASS with notes (judged from the headless check render, see below).

| Criterion | Result |
|---|---|
| Silhouette | pass: low rectangular stone kerb of staggered hewn blocks around a soil mound; reads clearly as a flower bed (not the wooden Farm Nature raised bed) at 128 px |
| Signature feature (staggered blocks, faceted soil mound) | pass with notes: 12 blocks of different lengths with visible joints and light tops; the soil mound is far flatter and one-toned than the reference's lumpy planes, reads almost as a flat brown slab |
| Proportions | pass: 2.0 x 1.0 x 0.25, border 0.12, soil visibly below the border tops (snap contract kept) |
| Colour / palette | pass with notes: stone sides greyer than the reference's beige blocks (palette effect, as WTR-03); light tops give a clear two-tone; soil colour matches slot 12 |
| Readability at 128 px | pass |
| Style match | pass: same stone cells 14/15 as WTR-03 (tops/sides split instead of the birdbath's plinth split), flat shading |

Deliberate deviations judged:
- Soil relief subtler than the reference: ACCEPT with notes, no FIX. The contract caps the soil at 0.20 and the border at 0.25. Optional within the contract: lower the valleys to about 0.12-0.14 (rim stays 0.15-0.16, crown stays 0.20) to give clearer facet tones; no tri cost.
- Stone greyer: accept (palette).
- Soil top 26 tris instead of 6-8: accept (204/300).
- `_Planted` crown: only lilac spikes reach 0.70; stalk blooms ~0.55-0.58: accept per notes; judge on a planted render.
- Extra `FMS_Garden_Bed_Straight_Planted.blend` needed by make_lod1: accept; it is a build input, keep it.
- `_Planted` borders split into 3 parts so make_lod1 keeps the snap faces exact; SNAP OK (bed|bed gap 0) per the builder, not re-measured here.

### `_Planted` (judged from the check render)

Verdict: 🟡 PASS with notes. No FIX, so no "## Fix 1" in `FLB-01.3d.md`.

| Criterion | Result |
|---|---|
| Reads as a planted cottage flower bed at 128 px | pass: 7 green drop clumps with yellow, pink and white blooms and a lilac spike crown in the centre; the colour dots and green mass read clearly on the stone-and-soil frame |
| Plants poking through the kerb | pass: all clumps stay well inside the kerb (builder margin 0.158 m to the outer face); no leaf or stalk crosses the kerb tops in the render |
| Style consistency with PLT-01 (atlas F) | pass: the same domed 80-tri drops, same three-green split by normal, flat shading, same pink/white/yellow cells |
| Not a duplicate of Farm Nature flowers | pass with notes: the arrangement (clumps of drops with flat-faced small blooms, kerb frame) differs from tulip/daisy/sunflower/poppy; the lilac cone spikes are the closest to Farm Nature lavender, but they are short chunky cones in a clump of mixed colours, so acceptable |
| Crown height and layout | pass: 0.70 lilac crown in the middle, lower to the ends, no two equal colours touching |

Notes (optional):
- Pink and white blooms read as flat 5-petal discs on thin short brown sticks (a bit "lollipop" at the front clumps), flatter and less rich than the PLT-01 v2 roses; they are fine for a mixed bed, but with 44 tris free (1456/1500) nothing more can be added. Optionally tilt the cups 10 degrees further toward the viewer.
- The bed is a little sparse: soil is visible at the front and the ends; clumps are 7. Not required to change.
- The planted variant LOD1 (830 tris) was not rendered; builder notes only.

Asset Store media for FLB-01 should use `_Planted` (the base is a plain kerb); the check render is not a preview file in `art/CottageGardenDecor/Previews/`.

## MOD-05 Edging_Brick and MOD-06 Edging_Brick_Curve (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_MOD-05_MOD-06.png` (both on one sheet); the MOD-06 preview was also viewed in full. FBX (+ .fbm) exist for both in `art/CottageGardenDecor/Meshes/`.

Verdicts: MOD-05 🟡 PASS with notes; MOD-06 🟡 PASS with notes. No FIX, so no "## Fix 1" written.

| Criterion | MOD-05 | MOD-06 |
|---|---|---|
| Silhouette | pass: eight pentagonal "house" bricks in a sawtooth row, valley at both ends; matches the reference | pass: a 90-degree arc of 12 sawtooth bricks, ridge height constant; reads as a curved edging piece |
| Signature feature (alternating two-tone sawtooth bricks) | pass with notes: alternation visible but subtle (#9C3F33 vs #A8372E are close in value); light-dark shading from the faces helps | pass with notes: same; the facing light/dark faces carry the rhythm better than the cell contrast |
| Proportions | pass: 1.0 x 0.10 x 0.15, brick h/w 1.2 as measured by the builder (reference about 1.23) | pass with notes: 1.05 x 1.05 x 0.15; bricks lower than in the reference (reference h/w about 1.6) because the shared 0.10 x 0.15 section wins |
| Colour / palette | pass: atlas A cells 14 and 6 (brick red) | pass |
| Readability at 128 px | pass | pass |
| Style match | pass: flat matte, same atlas A, no mortar/texture; as simple as WTR-03 stone | pass |

Deliberate deviations judged:
- Two-tone subtler than the reference: accept (palette fixed by the spec; the atlas is read-only).
- Sharp edges without bevels: accept (the spec forbids bevels; the sharp look fits the flat-shaded style).
- MOD-06 bricks lower than the reference: accept; the identical section is the snap contract (no step at the joint) and wins over the picture (PIPE-04).
- MOD-06 ridge 0.144 inside to 0.150 outside (planar faces): not visible; accept.
- Colour phase: each module starts on an even brick and ends on an odd brick, so rows laid in one direction alternate; turned pieces may put two equal tones together: accept, minor.
- SNAP OK (identical joint section 0.000 mm, valleys on both ends, 4 arcs = closed ring) is taken from the builder notes, not re-measured here.

For the Unity trial import (not verifiable here): MOD-06 is built in the Blender -X/-Y quadrant on the assumption that Unity's FBX import negates X, so the arc should land in the +X/+Z quadrant of its pivot with the ends at (1,0,0) and (0,0,1). Check that at the first import (Э8); if it lands in -X/+Z, mirror the arc in build.py or rotate the prefab by -90 degrees. The same X-flip assumption applies to STR-01's gate hinge.

## MOD-01 Lattice_Panel and MOD-02 Lattice_Post (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_MOD-01_MOD-02.png`; the MOD-01 preview was also viewed in full. FBX (+ .fbm) exist for both in `art/CottageGardenDecor/Meshes/`.

Verdicts: MOD-01 🟡 PASS with notes; MOD-02 ✅ PASS. No FIX, so no "## Fix 1" written.

| Criterion | MOD-01 | MOD-02 |
|---|---|---|
| Silhouette | pass: square white frame with a diagonal diamond lattice, real gaps, two visibly crossing layers | pass: slim square post with a wider cap and chamfered top, as in the reference |
| Signature feature | pass: over/under crossing of slats gives depth and shadows; lattice runs into the frame | pass: cap wider than the shaft with a visible step at the underside |
| Proportions | pass with notes: 1.88 x 0.06 x 1.75; slats 0.05 wide, pitch 0.20 (about 11 per direction) give a slightly coarser, more open lattice than the reference (about 13-14 diagonals), which reads fine and was kept for the 128 px readability | pass: 0.16 x 0.16 x 1.95; chamfer 0.02 a little smaller than the reference, minor |
| Colour / palette | pass: white #EEEDE7 (slot 10), a bit cooler than the reference's cream | pass |
| Readability at 128 px | pass: diamond pattern clearly reads | pass: a post with cap |
| Style match | pass: flat matte, chunky members above the STYLE minimum (slats 0.05 >= 0.03) | pass |

White consistency: MOD-01 and MOD-02 use the same slot 10 `#EEEDE7` as the STR-06 white members and the intended STR-01 `_White` (the same cell, no new colour), so they will match exactly. All of these are cooler than the cream references; this is the pack's palette decision, not a defect. Recommendation: keep slot 10 everywhere and do not retint per model.

Deliberate deviations judged:
- Slats 0.05 instead of 0.04: accept (reference wins; STYLE minimum 0.03; no tri cost).
- Frame as one ring shell with no joint lines between stiles and rails: accept (flat white, no bevels per spec).
- Symmetric lattice phase, different corner pieces than the reference: accept (not visible at 128 px).
- Snap numbers (gap 0.000, pitch 2.000, frame top = cap underside 1.80) and PLT-02 mount: SNAP OK from the builder notes, not re-measured here.
- Tris 296/900 and 36/60: fine.

## MOD-03 Wall_Stone and MOD-04 Wall_Pillar (reviewed 2026-11-25)

Sheet: `%TEMP%/pack_review/sheet_00_MOD-03_MOD-04.png`. FBX (+ .fbm) exist for both in `art/CottageGardenDecor/Meshes/`.

Verdicts: MOD-03 🟡 PASS with notes; MOD-04 🟡 PASS with notes. No FIX, so no "## Fix 1" written.

| Criterion | MOD-03 | MOD-04 |
|---|---|---|
| Silhouette | pass: long low wall with a slab coping; reads as a garden wall | pass: square pillar with a cap slab and a faceted ball; reads as a wall pillar |
| Signature feature | pass: 4 courses of staggered blocks, about one in four in the light tone, light coping | pass: 3 courses with 2 blocks per face, ball finial on the cap |
| Proportions | pass with notes: 2.0 x 0.44 x 0.60, reads longer and lower than the reference's picture (contract height wins); coping has the same footprint with no visible overhang | pass with notes: 0.50 x 0.50 x 1.05; ball 0.25 vs about 0.27 in the reference; cap flush with the shaft (no overhang) |
| Colour / palette | pass with notes: stone greyer than the reference's beige; coping is nearly white, with less contrast to the blocks than in the reference | same |
| Readability at 128 px | pass | pass |

Stone consistency with WTR-03 and the FLB-01 kerb: pass. All use the same atlas cells (12 `#A7A39A` for the main blocks and plinths, 11 `#C9C3B6` for tops, coping and ball), flat shading and chunky faceting, so wall, pillar, birdbath and flower bed read as one stone family. The kerb (slot 14/15 on atlas F, same hexes) is the same colour as the wall (slot 12/11 on atlas A); fine, as the hex values are identical. The coping is the lightest part, as in the references.

Deliberate deviations judged:
- Wall reads longer/lower than the reference: accept (contract 0.60 high, 2.0 long, PIPE-04).
- No softened edges / cap overhang: accept (spec: bevel 0.015 on top edges only; overhang would break the pillar/wall faces rule).
- Ball 0.25 vs 0.27: accept (spec size).
- Snap contract (butt gap 0, corner coping inside the pillar, wall top 0.60 under the cap 0.74) from the builder notes, not re-measured here.

## How to fix
- No fixes in batch 1 (9 PASS with notes, 1 PASS). Optional polish only (see per-item notes).
- After any later fix: re-export, re-import verify, new preview, second sheet pass; append a results table below.
