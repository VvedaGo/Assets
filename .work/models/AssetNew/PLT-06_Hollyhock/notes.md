# PLT-06 Hollyhock `FMS_Garden_Hollyhock` (+ `_White`) — builder notes (Э7, batch 4, 2026-11-26)

Source of truth: `build.py` (`-- PLT-06 build|export|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in collection `PLT-06_Hollyhock` (+ child
`PLT-06_Hollyhock_White`, left in place). Owner's file not saved (no file path, not dirty after the run); Cube and other
collections untouched; selection (Cube, active Cube) saved before the live export and restored; no TMP scenes/objects
left. Atlas F loaded read-only (`pc.atlas_image` NOT used): MD5 `ae0f0dba…` unchanged, palette cells 0 mismatches;
atlas A not used (MD5 `119daf05…` unchanged). Shared material `M_Garden_Flora` reused.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Hollyhock.fbx`, `FMS_Garden_Hollyhock_White.fbx` (each + `.fbm` with the atlas F copy) |
| Blend | `art/AssetNew/Blend/FMS_Garden_Hollyhock.blend` (both collections only) |
| Preview | `art/AssetNew/Previews/FMS_Garden_PLT_06_Preview.png` (one, base, series 3/4) |
| Tris / budget | **684 / 700** — Stems 120 (3 × 40), End buds 36 (3 × 12), Cups 420 (15 × 28), Leaf plates 108 (6 × 18). LOD: none (catalogue) |
| Size X × Y(depth) × Z (Blender) | 0.766 × 0.785 × 1.800 m (catalogue 0.6 × 0.6 × 1.8) |
| Nodes | root empty `FMS_Garden_Hollyhock` + `FMS_Garden_Hollyhock_Body` (1 mesh, 1 material), scale 1, rot 0; same for `_White` |
| Pivot | (0, 0, 0) = centre of the foot on the ground; stems' ground caps at z 0 |
| Variant | `_White`: same mesh, UV cells 6 → 8 and 7 → 8 (cups white), centre 11 stays yellow, foliage unchanged |

## Axes
Blender X right, −Y front (reference camera; Unity +Z after the −Z-forward export), Z up (Unity Y). The plant has a FRONT:
all cups face the front half (az 230–320) as in the reference and the review lesson "cups tilted toward the viewer".

## Build
- **Stems ×3 (40 tris each)** — 6-sided tapered prism Ø0.06 → Ø0.038, 3 segments, quadratic Bezier sampled at
  t 0, 0.24, 0.55, 1 (bend sits low, inside the leaves), base ring horizontal on the ground (z 0) and capped; other rings
  mitred. Slot 0 (green). C (centre-back, az 100): near vertical, top ring 1.70. L (az 195): leans out low, vertical at
  the top, top 1.47, x −0.28. R (az 345): top 1.29, x +0.30.
- **End buds ×3 (12 tris)** — fused on each stem's top ring: 6 → 3-sided belt Ø0.072 at +0.035 → point at +0.10 (bud tips
  1.80 / 1.57 / 1.39). Belt slot 1, tip facets alternate 1 / 0.
- **Cups ×15 (28 tris, ONE closed shell each)** — `hollyhock_cup` v3: dark-green calyx triangle (r 0.02, slot 2) on the
  stem surface (centre 0.02 out from the stem axis, so the cup sits on and in the stem) → outer wall to the hexagonal rim
  Ø0.148 → 0.140 at 0.075 (9 tris, slot 7 light pink) → inside wall to a 6-ring 0.035 below the rim, twisted 30°
  (12 tris, alternating 7 / 6 = light lip + deep pink inside) → yellow centre cone Ø0.052, tip 0.015 above its ring
  (6 tris, slot 11). Axis tilted 40° up, azimuths zigzag left/right of each stem (230–245 / 305–320), anchor heights from
  the reference (642 px/m): C 0.88–1.53, L 0.84–1.36, R 0.64–1.17.
- **Leaf plates ×6 (18 tris)** — `leaf_plate`: 8-point ovate outline drooping from the base to the tip (−0.02 … −0.05),
  raised midrib (2 verts, 0.11 / 0.08 above the base plane = folded dome), one bottom vertex 0.045 below; noise ±0.008
  (seeds 61–66). L 0.34–0.37, W 0.32–0.35, at az 270 / 330 / 30 / 90 / 150 / 210, base r 0.03 (overlapping the stem
  bases), tilt 3–14° (back ones higher), lowest point z 0.015. Top facets slot 1 (normal z > 0.8) / 0, bottom slot 2.

## Checks (live = headless)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 (every shell overlaps another), coplanar overlapping pairs 0.
- Ground contact: min z 0.0000 (stem ground caps); leaves ≥ 0.015 above the ground, no vertex below 0.
- Cups touching each other: none (min cup-to-cup 0.021); cup in a leaf: none; cup touching a foreign stem: none; rim to own
  stem ≥ 0.0095 (the stem never cuts a cup opening); every cup overlaps its own stem (no floating flowers).
- Tris 684 ≤ 700. SNAP: no contract (not a module).
- FBX re-import (both): 2 nodes (empty + mesh), 684 tris, dims 0.766 / 0.785 / 1.800, min z 0, texture found in its `.fbm`.
- Headless `build.py -- PLT-06 export`: SHA1 of both meshes (world verts + face UV cells) == live
  `27fd517bbdd39e893cc1d7e60f4e49b1228470fc` (390 verts / 630 faces each). No `Tools/blender/__pycache__` left.

## Deviations from `prompts/PLT-06.3d.md` (for the reviewer / spec owner)
1. **Cup 28 tris, not 24** (and not an open cup): Opaque + Cull Back + non-manifold 0 need a closed shell. The spec's
   4-sided stalk is replaced by the calyx triangle on the stem surface (the cup sits on the stem). Paid for by the leaf
   plates (18 instead of ~36 tris) and the buds (12 instead of 6 + fused base). The yellow centre Ø0.052 (spec 0.04) so it
   reads at the 3/4 camera.
2. **Cup orientation**: zigzag facing the front half and tilted 40° (spec: 144° spiral, 50°). The reference shows all 15
   cups facing the viewer, and the review lesson says "cups tilted toward the viewer"; at 50° the upper rim hit the stem.
   Consequence: from behind the cups show their light-pink backs (check `PLT-06_checkback_live.png`); place with the front
   toward the camera / path.
3. **Cup positions** from the reference: upper ~half of each stem (fractions ≈ 0.50–0.90), not 0.35–0.92; rim
   Ø0.148 → 0.140 (reference cups are nearly equal), not 0.16 → 0.10.
4. **Size 0.77 × 0.79** (catalogue 0.6 × 0.6): reference width / height ≈ 0.5 (stem tips spread 0.63 m, rosette ≈ 0.85 m).
   Stem tips at x −0.28 / +0.30 and the leaf rosette Ø≈0.75; kept a little narrower than the reference.
5. **Leaf plates**: own 18-tri folded plate instead of an ico sphere (subdiv 0 = 20 tris looked like gems in earlier
   reviews); L 0.34–0.37 × W 0.32–0.35 (spec 0.26 × 0.20) to match the reference's big domed rosette; Y 0.015–0.20.
6. **Stem colour slot 0** (spec slot 2): the reference stems are mid green like the leaf sides; slot 2 rendered too dark.
   Slot 2 is used for the cup calyx and leaf undersides.
7. **Stem lean**: L / R lean ~15–20° low and are vertical at the top (reference curve), not 3–8° straight.

## Rounds (live, 5 of 5)
1. First build 642 tris, clean checks. Worst: leaf plates tiny and flat; cups (cone from a buried apex) read as pink
   spikes; stem spread narrower than the reference (0.44 vs 0.63 at the top), stems too dark.
2. Cup v2 (frustum + calyx cap + funnel + yellow pyramid), stems slot 0, wider spread, bigger leaves. Worst: yellow
   centre almost invisible, cup read as a flat hexagon; leaves flat tents.
3. Cup v3 (triangle base → hex rim, twisted inner ring with alternating 7/6 facets, yellow hex cone), buds 3-sided belt,
   cups turned more to the front. Cups now read like the reference. Worst: leaves low "tents", rosette narrow; stem kink.
4. Drooping leaf outline with a high midrib (domed gem leaves like the reference), rosette wider, stem bend moved low.
   Worst: front leaf too long (depth 0.84).
5. Leaves shortened (depth 0.785). 128 px thumbnail: three tall green stems with pink cups over a leaf rosette — reads as a
   hollyhock spire, not a sunflower (single head) or lavender (low tuft). `_White` checked (`PLT-06_check34_White_live.png`).

## Remaining differences vs the reference (nitpicks)
- No small green bracts at each cup node (budget); cup calyx is a dark-green triangle under the cup.
- From the 3/4 preview camera the left-facing cups are seen side-on (light pink cones); the reference is a front view.
- Bud is 3-faceted (reference ~6 facets); stems have one visible bend instead of a smooth curve (3 segments).
- Leaves slightly more pointed / gem-like than the soft reference domes.
