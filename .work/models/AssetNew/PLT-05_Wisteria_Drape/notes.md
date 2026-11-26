# PLT-05 Wisteria Drape `FMS_Garden_Wisteria_Drape` — builder notes (Э7, batch 4, 2026-11-26)

Source of truth: `build.py` (`-- PLT-05 build|export|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in collection `PLT-05_Wisteria_Drape` (left in place). Owner's
file not saved (no file path); Cube and other collections untouched; selection (Cube, active Cube) saved before the live
export and restored; no TMP scenes/objects left. Shared material `M_Garden_Flora` reused as is; atlas F loaded read-only
(`pc.atlas_image` NOT used) — MD5 `ae0f0dba…` unchanged, palette cells 0 mismatches. Atlas A not used (MD5 `119daf05…`
unchanged). STR-04 FBX imported read-only into a temporary scene for the mount check and removed again.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Wisteria_Drape.fbx` (+ `.fbm` with the atlas F copy) |
| Blend | `art/AssetNew/Blend/FMS_Garden_Wisteria_Drape.blend` (collection only) |
| Preview | `art/AssetNew/Previews/FMS_Garden_PLT_05_Preview.png` (one, series 3/4) |
| Tris / budget | **888 / 900** — Leaf clusters 384 (8 × 48), Racemes 368 (8 × 46), Vines 72 (2 × 36), Stalks 64 (8 × 8) |
| Size X × Y(depth) × Z (Blender) | 1.508 × 0.470 × 0.856 m (catalogue 1.5 × 0.6 × 0.9) |
| Nodes | root empty `FMS_Garden_Wisteria_Drape` + `FMS_Garden_Wisteria_Drape_Body` (1 mesh, 1 material), scale 1, rot 0 |
| LOD / variants | none (catalogue) |

## Axes, pivot, attachment plane
- Blender X = along the beam, −Y = front (Unity +Z after the −Z-forward export), Z = up (Unity Y).
- Pivot (0, 0, 0) = centre of the TOP face; max Z = 0.0000, everything hangs below (min Z −0.856). X centre −0.009,
  Y centre −0.001.
- Attachment plane Z = 0: the 8 leaf drops are cut flat on top (one 10-gon each, 0.162 m² in total, 13 faces inside the
  0.10 beam strip |y| ≤ 0.05). Neighbouring tops alternate Z 0 / −1.5 mm, so no coplanar overlap where drops meet.

## Build
- **Leaf clusters (8 × 48 tris)** — series drop generator cut in half: one hemisphere of the PLT-01 icosphere
  (subdiv 2 = 40 tris, random Z spin, noise ±0.035, fixed seeds 51–58) mapped onto a ball whose top is cut off
  (polar angle stretched so the cut ring sits 35° above the ball's equator = rounded shoulders, like the reference
  balls), cut ring (10 verts) exactly on the plane and closed by one face. D 0.26–0.31, vertical radius 0.15 (back) /
  0.18–0.195 (front): back drops hang to ≈ −0.24, front ones to ≈ −0.29 (reference: front drops lower). One drop over
  each raceme, X = raceme X, Y ±0.065 (front/back alternate) so the two rows merge into one band. Slots by normal:
  up > 0.55 → 1, down < −0.62 → 2, else 0; the hidden cut face slot 0.
- **Racemes (8 × 46 tris)** — 6-sided "two beads + tip" (reference): flat hex top r 0.064, upper bead belt r 0.102 at
  0.17 L, waist r 0.058 at 0.42 L, lower bead belt r 0.084 at 0.60 L, tip point; radii × 0.92–1.12 with the body length.
  Lilac slot 9 for 6 racemes with every 3rd facet of the tip cone in slot 8 (spec "liveliness"); white slot 8 (all facets)
  at X −0.09 and +0.46. Tilt ±4° alternating. Top 0.035 under the drop's surface over the whole top ring.
  Tip heights from the reference (777 px/m): −0.624, −0.856, −0.573, −0.744, −0.605, −0.817, −0.579, −0.705 for
  X −0.62, −0.46, −0.28, −0.09, +0.10, +0.28, +0.46, +0.62 (long ones 2 and 6, as in the reference). Body lengths
  0.30–0.54. Min gap between racemes 0.114 (spec ≥ 0.04).
- **Vines (2 × 36 tris)** — 4-sided bars 0.05 across (spec Ø0.05; the reference shows a lit flat top + darker side), 4
  segments, X −0.66 … +0.66 (ends inside the end drops). A behind (+Y 0.02–0.13), B in front (−Y), each zigzags in Z
  −0.10 / −0.23 out of phase, so they cross in the front view (weave) and show between the drops. Slot 13.
- **Stalks (8 × 8 tris)** — 3-sided, ~0.027 across, from the vine centre line (behind/in front, at the raceme X) into the
  raceme top (12 mm), 0.08–0.22 long, 2–30° from vertical; visible part ≈ 0.035 under the drop. Slot 2 (dark green).

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 (every shell overlaps another), coplanar overlapping pairs 0.
- Racemes touching each other: none; raceme inside a drop: none; every stalk overlaps its vine and its raceme (no floating
  raceme).
- ATTACH OK: max Z 0 (flush), flat top faces on the plane and under the beam strip, length 1.508 ≤ 1.52, depth 0.470,
  hang 0.856 ≤ 0.90, pivot centred.
- **MOUNT OK** (approved `FMS_Garden_Pergola.fbx`, read only, temporary scene; pivot placed at each beam's underside
  centre line, Blender y ±1.5, z 2.24): beam underside 2.2400; drape top − underside 0.0000; 15 drape vertices flush on
  the underside within the beam width; 0 vertices inside the beam; 0 inside the posts; drape X within the beam length
  (0.99 m clear of each beam end); lowest tip 1.384 m above the ground. Check render
  `%TEMP%/assetnew_check/PLT-05/PLT-05_check_mounted_*.png`.
- FBX re-import (live and headless): 2 nodes (empty + mesh), 888 tris, dims 1.508 / 0.470 / 0.856, texture found in
  `FMS_Garden_Wisteria_Drape.fbm`.
- Headless `build.py -- PLT-05 export`: geometry SHA1 == live `34fc6bcae685f75ac1cb11efd53d92001be52784`
  (496 verts / 684 faces, UV cells included). Final art files are from the headless export.

## Rounds (live, 5 of 5; headless debug builds before round 1)
- Headless debug: (a) bisect-cut 80-tri drops gave 86 tris each (1258 total) → topological equator cut (48 tris);
  (b) stretched hemispheres read as inverted cones; long green stalks (lollipops) → racemes under their own drop.
1. Ball-shaped drops with rounded shoulders, racemes hang 0.035 under them. Front view close to the reference; 3/4 shows
   two separate rows of "barrels" with a gap, vines hidden, racemes far off the axis.
2. Drops at Y ±0.065, depth not squashed, D +0.01–0.02: one continuous band. Raceme 2 grazed its drop.
3. Raceme top cleared over its whole top ring; cut face slot 1 → 0. Vines still mostly inside the band.
4. Vines Ø0.05 and swung further front/back at the low points: they now show between the drops. 128 px thumbnail: reads
   as a green band with lilac hanging racemes and a white one.
5. Vine ends pulled in to ±0.66 (stubs poked out of the end drops in the preview). Stopped: only nitpicks left.

## Deviations from the spec (reference wins / budget)
1. **Racemes start below the leaf band** (tops −0.25 … −0.32, spec −0.04) and the leaf drops hang to −0.24/−0.29 (spec
   −0.02…−0.16): the reference shows a deep leaf band with the racemes hanging under it on short stalks; tip heights and
   long/short order from the reference (longest 0.856 at X −0.46; spec order 0.90, 0.60, … not used).
2. **Depth 0.47** (catalogue 0.6, spec racemes at Z ±0.20): racemes at ±0.12 under their own drops (±0.065), so the stalks
   stay short and nearly vertical. The 0.10 beam is straddled as required.
3. **Vines 4-sided 4 segments** (spec 8-sided 5 segments ~60 tris): reference bars show flat faces; budget.
4. **Stalks 3-sided, slot 2 green** (spec 6-sided Ø0.025, slot 13): budget (8 tris each), and the batch-4 review lesson
   "green stems, no brown lollipop stalks".
5. Raceme ends X ±0.62 (spec ±0.65; reference ±0.62–0.64) to keep the length at 1.5.

## Remaining differences vs reference
- The flat cut tops of the drops are visible from above in the standalone 3/4 preview (light lids); hidden under the beam
  when mounted.
- Vines show less than in the reference (they run inside the band and appear in the gaps and at the ends); the reference
  has more brown X-crossings in front.
- Long racemes are slimmer than in the reference (body 0.50–0.54 vs ~0.43; same belt width ratio for the short ones).
- White speckle facets on the lilac tips (spec) are not in the reference.
- Drops have 48 tris (40-tri dome) — fewer facets than the reference's foliage balls (budget 900).
