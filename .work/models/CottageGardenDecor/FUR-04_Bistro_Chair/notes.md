# FUR-04 Wrought-iron bistro chair `FMS_Garden_Bistro_Chair` (+ `_White`) — builder notes (Э7, series batch 4, 2026-11-26)

Source of truth: `build.py` (`-- FUR-04 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in collection `FUR-04_Bistro_Chair` with the child
`FUR-04_Bistro_Chair_White` (left in place); the owner's file was not saved, the default Cube and the other collections were
not touched; selection (Cube, active Cube) restored after the live export.

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Bistro_Chair.fbx`, `art/CottageGardenDecor/Meshes/FMS_Garden_Bistro_Chair_White.fbx` (each + `.fbm` with the atlas copy) |
| Blend / preview | `art/CottageGardenDecor/Blend/FMS_Garden_Bistro_Chair.blend` (both collections only); ONE preview `art/CottageGardenDecor/Previews/FMS_Garden_FUR_04_Preview.png` (base) |
| Tris | **1096 / 1400** per model. Seat 68 · Legs 4 × 20 = 80 · Ring brace 192 · Back hoop 272 · Back S-scroll 320 · Upper curl (branch) 164 (component counts before cap triangulation; total after = 1096) |
| Size (Blender X×Y×Z) | 0.410 × 0.450 × 0.850 m (x ±0.205, y ±0.225, z 0 … 0.850); seat top 0.450 |
| Nodes | root empty `FMS_Garden_Bistro_Chair` + mesh `_Body` (same for `_White`) |
| Material | `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette pixel check 0 mismatches). Base: slot 13 wrought iron only; `_White`: slot 10 only, identical vertices |
| LOD | none (catalogue) |

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint / bounding box on the ground; rot 0, scale 1; FBX Y up, −Z forward baked. Static.
- Blender X = right, −Y = front (Unity +Z), Z = up (Unity Y). Seat centre at y −0.02 (0.02 to the front, spec); the back
  hoop leans back to y +0.225, so the bbox is centred (y −0.225 … +0.225).
- X-symmetric except the back scroll (mirror check skips `Scroll` and `Curl`; everything else mirror 0.000000).

## Checks (live and headless identical, both variants)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 (every component touches another), mirror X 0.000000 (without the scroll).
- Coplanar overlapping face pairs 0.
- Ground contact: four flat leg feet, 6 verts each at z 0.0000, centres (±0.141, +0.121) and (±0.141, −0.161); nothing below 0.
- Seat top 0.4500 (functional). SIZE OK: width 0.410 ≤ 0.45, depth 0.450 ≤ 0.50, height 0.850.
- Curls: lower spiral 0.134 across, upper curl 0.102 across (≥ 0.10). Centre-line self-clearance: S 0.044 ≥ bar 0.034,
  branch curl 0.038 ≥ 0.034, branch vs S 0.069 → no self-touch.
- SNAP: no module contract for this item (free-standing furniture).
- FBX re-import (both): 2 nodes (root + Body), 1096 tris, dims 0.41 / 0.45 / 0.85, min z 0, texture found in `.fbm`.
- Headless `build.py -- FUR-04 export` geometry SHA1 == live SHA1 `40a08dd0341a16fe54e5c2a44776a167ec0c8e14`
  (2 meshes × 564 verts / 586 faces).
- Set check (headless, FUR-03 + both chairs from the FBX in art/, read only, `%TEMP%/assetnew_check/FUR-04/FUR-04_set_headless.png`):
  same iron cell and rod sizes, seat 0.45 under the 0.75 table top, reads as one set.

## Build (what is where)
- Seat: 12-sided slab (FUR-03 top wording, a flat to the front), 0.41 across the flats, z 0.40–0.45, top edge chamfer
  0.016 in / 0.012 down (the reference's light band).
- Legs: 4 straight 6-sided rods 0.036 across the flats, on the diagonals (45°/135°/225°/315°) around the seat centre,
  centre-line r 0.20 at the ground → r 0.15 at z 0.41 (spec), top sunk to z 0.435 inside the slab, foot cut flat on z 0.
- Ring brace: 16-segment closed 6-sided rod 0.030 at z 0.20; centre-line r 0.158 (Ø0.316, spec Ø0.30) = the legs' inner
  faces, so it sinks half into each leg and runs inside them (reference), vertices on the leg azimuths.
- Back hoop: one 6-sided rod 0.036 in a plane tilted back 15.4° from the seat top at y 0.10: ends at u ±0.14 sunk 0.022
  into the seat, Hermite sides widening to ±0.182 at 58 % of the height, 14-segment elliptic crown. Tilt and crown height
  are solved so the outer surface reaches z 0.850 and y +0.225 exactly.
- Back scroll (in the hoop plane, 6-sided bar 0.034): main S = lower spiral (15 segments, 400°, R 0.072 → 0.022, bar sunk
  4 mm into the seat top) → S spine (Hermite) → upper-left bowl → tangent into the hoop crown (end runs inside the hoop
  bar, cap hidden). Branch: small CCW curl (11 segments, 315°, R 0.050 → 0.021) springing from the spine, upper right.
- Iron helpers copied from FUR-03 `build.py` (`oct_sec`, `rod_rings` + closed loops, `hermite`, `s_clearance`) plus `spiral`.

## Reference measurements (references/FUR-04.png, 1254 px)
- Seat 540 px wide ≈ 0.40 → ~1350 px/m at the seat; hoop 510 px wide at its widest (0.40 outer), ends 400 px apart at the seat
  (centre-lines ±0.14); widest point at ~57 % of the hoop height; back top ~0.37 above the seat → 0.82–0.85 total (kept 0.85).
- S: lower spiral ~0.11–0.13 across, sitting on the seat; spine leaning right; upper bowl left, merging into the crown; a
  separate small spiral upper right (~0.06 across in the image, enlarged to 0.10 for the ≥ 0.10 rule).
- Seat edge ~75 px → ~0.05 thick with a chamfer band (spec 0.04): slab 0.40–0.45 (top stays at the functional 0.45).

## Deviations from `prompts/FUR-04.3d.md` (for the reviewer / spec owner)
1. **Rods 6-sided (spec 8-sided)**: orchestrator note / FUR-03 option C. Legs and hoop 0.036, scroll 0.034, ring 0.030 (≥ 0.03).
2. **Seat 12-sided, 0.41 across, 0.05 thick with a chamfered top edge (spec 10-sided Ø0.40, 0.04)**: reference shows ~14 facets
   and a light edge band; 12 matches the FUR-03 top. Seat top 0.45 kept.
3. **Hoop links (2) not separate**: the reference hoop runs straight into the seat; the lower hoop sides are the links.
   Hoop ends sit at u ±0.14 on the seat field (not at the back edge, which would leave the rod hanging off a round seat).
4. **Hoop top 0.045 behind the seat's back edge (spec 0.06)**: tilt 15.4°, so the depth is 0.45 and the bbox is centred;
   the reference back is nearly upright.
5. **Scroll = S plus a small branch curl (spec: one S touching the hoop at both ends)**: reference — the S stands on the seat,
   its top merges into the crown, and a small spiral springs from the spine upper right.
6. Ring Ø0.316 centre-line (spec 0.30) so it is sunk into the legs instead of floating inside them.

## Rounds
- Headless prototype (1): first build 1096 tris; worst: S top ended with a visible cut below the crown; upper curl 0.096
  (< 0.10) with self-clearance 0.031 (< bar); seat-top check picked scroll verts.
- Live round 1: S runs into the crown (end hidden), curl R 0.050 / 315° (0.102 across), seat 0.05 thick; reference angle,
  3/4, side, front, 128 px thumbnail and `_White` checked. Worst left: ring brace (circle through the leg centres, Ø0.35)
  bulged past the legs at the sides.
- Live round 2: ring on the legs' inner faces (Ø0.316). Only nitpicks left → export live + headless.
- Rounds used: 2 of 5 live.

## Remaining differences vs the reference (nitpicks)
- Reference legs look square (4-sided); ours are 6-sided (series rod wording) — reads the same at game size.
- The upper-right curl is larger than the reference's (0.10 rule) and the S's upper bowl is a little narrower.
- Reference back is nearly upright with slightly more splayed back legs; ours tilt 15° and the legs splay 0.05 (spec).
- Iron is palette slot 13 `#3A3A3F`, very close to the reference; `_White` is the cool palette white (palette decision).
- 128 px: seat, hoop, ring and the S read; the small branch curl merges with the S into one scroll mark.
