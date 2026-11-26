# ORN-01 Sundial `FMS_Garden_Sundial` + ORN-03 Urn `FMS_Garden_Urn` (+ `_Planted`) — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: ONE registry script `build.py` (`-- ORN-01|ORN-03 build|export|verify`). Live Blender 5.2 via MCP
(add-on reported OUTDATED; execute_blender_code and look worked). Live work only in collections `ORN-01_Sundial` and
`ORN-03_Urn` (+ child `ORN-03_Urn_Planted`); the owner's Cube, other collections and the saved file were not touched; the
owner's selection (Cube, active) was restored after each live export. Renders in a temporary scene, viewed with look image=.

Shared code: `lathe()` + `box_stage()` / `ng_stage()` / `stack()` = the pedestal profile helper used by both models
(square blocks with optional horizontal-edge chamfers and n-gon lathe stages lofted into ONE closed shell; ledges between
blocks are flat bands owned by the wider block, so stacked blocks have no coplanar faces and no gaps).
Planted helpers copied from FLB-01 / PLT-01: `leaf_cluster` (80-tri domed drops), `cup_bloom` (22-tri cup), `bridge`, `ring`.
Atlases A / F are loaded READ ONLY (palette verified by pixel read: 0 mismatches; PNG mtimes unchanged).

## Rounds

### ORN-01 (3 live rounds)
1. All checks pass, 348/400. vs reference: capital too thin, its underside slope invisible (slope too flat); moulding low;
   ribs a little short. -> capital 0.095 -> 0.115, moulding +0.015, ribs 0.065 -> 0.076 long, dial thicker (0.050).
2. Capital slope still not visible (41 deg slope is foreshortened at 26 deg elevation). Crop of the reference: capital =
   ~0.065 vertical face + ~0.08 steep slope. -> capital 0.605-0.750, slope inset 0.062 over 0.080 (52 deg).
3. Matches the reference sheet (capital, moulding, shaft, dial overhang, gnomon). 128 px: column + dial + dark blade read.
   Remaining: palette only (see below).

### ORN-03 base (1 live round) + `_Planted` (4 live rounds)
1. Base matches the reference on the sheet (goblet, foot, neck, flared lip, soil, pedestal proportions) -> accepted.
   `_Planted`: 4-segment stems stood far from the urn like spider legs, bare, budget 1266/1300, footprint exceeded.
2. Stems re-routed: 2 segments (inside the mound -> over the lip edge -> hanging down past the belly), small 20-tri leaf
   drops on the hanging parts, mound drops D 0.30, base lip outer chamfer removed (not in the reference, -24 tris).
   Footprint still 0.62 (end blooms tilted toward the viewer stuck out in -Y).
3. Stems on near-diagonal azimuths (±40/50, ±130/141), blooms tilted less toward the viewer, arc blooms on the lip,
   leaves without outward offset -> footprint exactly 0.600 x 0.600. Right stem (az 40) bare (lollipop look).
4. Cap underside chamfer removed (reference shows a sharp cap, -8 tris), one leaf drop on the az 40 stem. Accepted.

## Result

| | ORN-01 `FMS_Garden_Sundial` | ORN-03 `FMS_Garden_Urn` | `FMS_Garden_Urn_Planted` |
|---|---|---|---|
| Size (Blender X × Y × Z) | 0.450 × 0.450 × 0.955 | 0.600 × 0.600 × 1.200 | 0.600 × 0.600 × 1.384 |
| Tris | **348 / 400**: Plinth 26, Moulding 28, Shaft 16, Capital 30, Dial 92, Ribs 144 (12 × 12), Gnomon 12 | **436 / 700**: Plinth 30, Shaft 16, Cap 44, Urn 336, Soil 10 | **1296 / 1300**: Body 436 + Plants 860 (3 mound drops 240, 9 leaf drops 180, 6 stems 264, 8 blooms 176) |
| LOD | none (catalogue) | none | none |
| Objects | root empty + `_Body` | root empty + `_Body` | root empty + `_Body` + `_Plants` |
| Pivot | centre of the plinth base on the ground (0,0,0), scale 1, rot 0 | same | same |
| Material | `M_Garden_Build`, atlas A | `M_Garden_Flora`, atlas F | same |

Slots ORN-01 (A): plinth 12, moulding/shaft/capital 11, dial 7 (underside chamfer + bottom 8), ribs 8, gnomon 13.
Slots ORN-03 (F): plinth 14, shaft 15, cap 14, urn 15, inner wall 14, soil 12; plants: drops 0/1/2 by face normal,
stems 2, blooms pink 7/6/11, white 8/8/11, deep pink 6/6/11.

Checks (whole model, all parts merged): non-manifold 0, loose 0, degenerate 0, coplanar overlapping pairs 0, contact
gaps 0 (dial sunk 3 mm into the capital, ribs and gnomon 3 mm into the dial; urn foot fused to the cap by a flat ledge;
mound drops sunk 0.03 in the soil, stems start inside the mound/lip, blooms and leaves sit on their stems), plinth min z
0.0000 (on the ground), mirrorX 0 for the base meshes. Footprint: ORN-01 0.450 × 0.450 (limit 0.45), ORN-03 and
`_Planted` exactly ±0.300 (limit 0.6 × 0.6); planted lowest point 0.846 (blooms hang free of the pedestal, cap top 0.635).
SNAP: no contract (free-standing ornaments).
FBX re-import: Sundial 2 nodes, 348 tris, dims 0.45/0.45/0.955; Urn 2 nodes, 436 tris, 0.6/0.6/1.2; Urn_Planted 3 nodes,
1296 tris, 0.6/0.6/1.384; texture found in each `.fbm`.
Headless `build.py -- <ID> export` SHA1 (world verts + face UV cells) == live: ORN-01 `accba917…`, ORN-03 (3 meshes) `7288084…`.

## Measurements (reference -> metres)

- ORN-01 (`references/ORN-01.png`, ~26 deg elevation, azimuth ~37 deg; dial O0.45 = ~490 px => ~1090 px/m across):
  plinth 0.34 (0.330 measured), moulding 0.25 (0.243), shaft 0.18 (0.174), capital 0.34 (0.336), dial O0.45;
  heights: plinth 0.10, moulding 0.105, shaft 0.40, capital 0.145 (0.065 vertical + 0.08 slope), dial 0.05, gnomon
  0.16 above the dial; total 0.955 (catalogue 0.95).
- ORN-03 (`references/ORN-03.png`, ~22 deg elevation; lip O0.60 = 467 px => ~780 px/m): plinth 0.418, shaft 0.279,
  cap 0.353, belly O0.54, neck O0.44, inner opening O0.45, foot O0.26, stem O0.12; pedestal top ~0.64, urn ~0.57 tall.

## Deviations / remaining differences (for the reviewer)

ORN-01:
1. Proportions from the reference, not the spec part table: plinth 0.34 (spec 0.40), moulding 0.25 (0.30), shaft 0.18
   (0.22), capital 0.145 tall with a steep underside slope (0.07), dial top 0.797 (spec 0.85-0.87), gnomon 0.16 tall
   (spec ~0.08-0.10). Dial O0.45, capital 0.34 and total height 0.955 agree with the catalogue; the reference column is
   simply more slender. No functional sizes involved.
2. Dial rim = top chamfer band (R 0.225 -> 0.21) and a bottom chamfer, as in the reference, instead of a raised rim
   ring; ribs 0.030 × 0.076 × 0.014 sit on the flat top inside the chamfer (no coplanar faces).
3. Gnomon from the reference: blade 0.034 thick, low tip at the dial centre, tall vertical edge at r 0.178 near the rim,
   small flat top, no foot. 12 o'clock axis = Blender +Y (tall edge to the back in the series preview, as in the
   reference) = Unity −Z under the series X-flip assumption; the spec said +Z. Rotate the prefab 180 deg if it matters.
   Ribs at the dial flats (15° + 30° k) so no rib sits under the blade.
4. Plinth keeps a bottom face (closed manifold for Unity/LOD tools; spec "no bottom face", +2 tris).
5. Palette: stone greyer and limestone cooler than the reference; dial slot 7 lighter, ribs slot 8 lighter than the
   reference's near-black ribs (spec slots kept).

ORN-03:
1. Atlas F for the base and `_Planted` (catalogue + spec: "one model = one material"); the dispatch envelope line
   "Atlas: A (+F for _Planted)" read as A for ORN-01 and F for ORN-03.
2. Proportions from the reference: pedestal top 0.635 (spec 0.76), urn 0.565 tall (spec 0.44) with a belly O0.544 at
   z 0.93, plinth 0.44 (spec 0.50; reference 0.42), cap 0.37 (spec 0.40; reference 0.35). Shaft 0.30 kept (spec: "not
   narrower"; reference 0.28). Lip O0.60 and total 1.20 = catalogue.
3. No chamfer on the cap underside and the lip top (reference sharp); plinth top and cap top keep the 0.012 chamfer, shaft
   vertical edges 0.010.
4. `_Planted` stems are GREEN (F2), not F13 brown (review lesson: no brown stalks); stems are 8-sided Ø0.03, 2 segments
   each, 6 stems; leaf drops 20 tris (ico sub 1, D 0.095) on the hanging parts — they read as small faceted leaves, a
   little gem-like up close. 8 blooms (6 stem ends + 2 on the lip arc), cups tilted outward and toward the viewer.
5. `_Planted` mound: 3 domed drops D 0.31 (spec 3-4, O0.15-0.25: larger so they spill over the lip and cover the soil;
   a little soil stays visible at the back), top 1.384 (≤ 1.4).
6. The short horizontal stem segment over the lip is bare on the right stem (az 40); budget is at 1296/1300.
7. Palette: stone whiter/cooler than the beige reference (fixed palette).
