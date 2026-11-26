# STR-01 Rose arch, wooden `FMS_Garden_Arch_Wood` (+ `_White`, `_Gate`) — builder notes (Э7, batch 1, 2026-11-25)

Source of truth: `build.py` (`-- STR-01 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look worked). Live work only in collection `STR-01_Arch_Wood` with the child collections
`STR-01_Arch_Wood_White` and `STR-01_Arch_Wood_Gate` (left in place). The owner's file was not saved; the default Cube and
the WTR-03 / PLT-01 / STR-06 collections were not touched; the selection (Cube) was restored after the live export.

## Result

| | base | `_White` | `_Gate` |
|---|---|---|---|
| FBX | `Meshes/FMS_Garden_Arch_Wood.fbx` (+ .fbm) | `Meshes/FMS_Garden_Arch_Wood_White.fbx` (+ .fbm) | `Meshes/FMS_Garden_Arch_Wood_Gate.fbx` (+ .fbm) |
| Tris / budget | 812 / 1000 | 812 / 1000 | 1264 / 1300 (Body 836 + Gate_Leaf 428) |
| Size X × Y × Z (Blender) | 1.600 × 0.700 × 2.400 | same | same (leaf inside) |
| Nodes | root empty + `_Body` + empties `Plant_L`, `Plant_R`, `Plant_Top` | same | root + `_Body` + `Gate_Leaf` + 3 empties |

- Tris per component (Body): Posts 112, Lintels 24, Purlins 24, Beams 60, Rims 64, Lattice 528 (+ Pintles 24 in `_Gate`).
  Gate_Leaf: Frame 140, Boards 60, Lattice 168, Hinges 48, Latch 12.
- One `.blend` (`Blend/FMS_Garden_Arch_Wood.blend`) holds all three collections; ONE preview (`Previews/FMS_Garden_STR_01_Preview.png`, base).
- Material `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette checked
  by pixel read: 0 mismatches). Slots: base 0 light wood, purlin + beam end faces 1 dark wood; `_White` everything 10
  (same vertices as the base, checked); `_Gate` arch 10, leaf 10, hinges / pintles / latch 13 wrought iron.
- No LOD (catalogue).

## Pivots and axes
- Root of every model: (0, 0, 0) = centre of the footprint on the ground; rot 0, scale 1. FBX Y up, −Z forward baked.
- Blender axes: X = across the opening, **−Y = front** (Unity +Z with the −Z-forward export), Z = up.
- Empties (spec names, written bare into the FBX): `Plant_L` (−0.66, 0, 0), `Plant_R` (+0.66, 0, 0), `Plant_Top` (0, 0, 2.40)
  (Blender X, Y, Z). In the `.blend` they are named `<asset>_Plant_*` because Blender needs unique names across the 3 models.
- `Gate_Leaf` (direct child of the root): pivot on the hinge axis at Blender (−0.59, 0, 0); rotation axis = Blender Z
  (Unity Y); closed = 0°. The leaf body lies behind the axis (Blender Y 0…0.05) so it can swing to the front.
  Note for Unity: Unity's FBX import flips the sign of X, so the hinge may read as X = +0.59 in Unity; it is the post on
  the viewer's LEFT when looking at the front of the arch.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 for every component of every mesh; mirror X 0.000000 (Body).
- Coplanar overlapping faces 0 per object and 0 for all objects of a model merged (also for `_Gate` arch + leaf).
- Ground contact: min z 0.0000 (4 posts on the ground; no ground plate).
- SNAP OK (all three): opening 1.200 wide (post inner faces) × 2.100 high (ground → lintel); top width 1.600 (PLT-03);
  side depth incl. posts 0.600 (PLT-02); total height 2.400; empties at the spec positions.
- `_Gate`: leaf does not overlap the arch at 0° (gap 4.5 mm at the hinge, pintles ↔ knuckles); gap leaf ↔ right post
  0.060 (≥ 0.05). Swing toward the front about the hinge axis: free 0…90°, **first contact at 91°** (see deviation 4).
- FBX re-import: base 5 nodes / 812 tris, `_White` 5 / 812, `_Gate` 6 / 1264; dims 1.6 / 0.7 / 2.4; texture found in each `.fbm`.
- Headless `build.py -- STR-01 export` geometry SHA1 == live SHA1 `db836ee0a1978ff4ebc5895ba653c178222d5c19`
  (all meshes + empties of the three models).

## Build (what is where)
- Posts 0.12 square, 0.01 chamfer (8-sided), centres X ±0.66, Y ±0.24, z 0 → 2.16 (tops buried in the lintels).
- Lintels 0.14 wide (1 cm wider than the posts: no coplanar sides) × 0.12, z 2.10–2.22, X ±0.76 (0.04 past the posts, as in
  the reference).
- Purlins 0.08 × 0.08 along Y (length 0.70), X ±0.66, seated 5 mm in the lintels (z 2.215–2.30). End faces dark.
- Cross-beams 5 × (1.60 × 0.07 × 0.10) at Y −0.30 … 0.30, seated 5 mm in the purlins (z 2.295–2.40), end faces dark.
- Side panels in the post plane X ±0.66: rim = one closed frame ring 0.05 thick × 0.05 wide (Y ±0.182, 2 mm into the posts;
  z 0.15–2.09, 1 cm under the lintel). Lattice = shared construction (`lattice()` in build.py): 45° slats 0.03 × 0.03,
  0.10 clear gaps, two layers (up-right outer, up-left inner) overlapping 1.6 cm in depth, ends cut square half-way in the
  rim, so the gaps are real and the lattice runs edge to edge into the rim. 11–12 slats per direction per panel.
- Gate leaf (only `_Gate`): white frame plate 1.10 wide × 0.05 (X −0.575 … 0.525), z 0.10–1.60, straight stiles 0.06 to
  z 1.05, semicircular top (r 0.55, 12 segments) with a 0.06 curved rail; bottom rail 0.10–0.18, mid rail 0.84–0.90.
  Lower half: 5 vertical boards 0.18 wide with 0.02 gaps (see deviation 3), inset (Y 0.012–0.038). Upper half: the shared
  lattice inside the arch rim. Iron: 2 knuckles on the axis + 2 strap hinges on the front face (z ≈ 0.22 and 0.77), latch
  bar on the mid rail; 2 static iron pintles in the arch body (from the left panel rim / inner slat layer to the axis, just
  under the knuckles).

## Deviations from `prompts/STR-01.3d.md` / the reference (for the reviewer / spec owner)
1. **Proportions vs reference:** the reference arch is squat (height ≈ opening width × 0.8; opening ≈ 1.2 × 1.0 at its scale).
   The functional sizes win (PIPE-04): opening 1.2 × 2.1, total 2.4 → the model is much taller and narrower than the picture.
2. **Colour vs reference:** the reference is all cream/white; the spec makes the base light wood (slot 0) with dark beam/purlin
   ends; the white look is the `_White` variant (and the arch of `_Gate`).
3. **Gate boards:** the spec's "5 boards 0.10 wide with 0.02 gaps" cannot fill the 0.98 m inner width; kept 5 boards and the
   0.02 gaps, so the boards are 0.18 wide.
4. **Gate swing 100° is not reachable** with the spec hinge (X −0.59, Z 0) and posts at Z ±0.24 (inner face X −0.60): beyond
   ~90° the leaf's front face sweeps into the front-left post. Measured: free up to 90°, contact at 91°. Unity should clamp
   the open angle to 90°; for 100° the axis would have to move ≥ ~0.05 inward (X ≥ −0.55, leaf 1.05 wide) — one constant
   (`HINGE_X`, `LEAF_X0`) in build.py.
5. Lintels 0.14 wide (spec 0.12) and 0.04 longer than the posts each side (spec: between the post outer faces): the width
   avoids coplanar post/lintel sides, the overhang is in the reference.
6. Lattice panel top at 2.09 (spec 2.10) so the rim top does not share the lintel's bottom plane.
7. Top cross-beams kept at the spec 0.07 × 0.10 (STYLE: beams ≥ 0.10). The reference beams are thinner flat boards with wide
   sky gaps between them when seen from above the front; ours read as a closed slab from a high frontal view, open in 3/4.
8. Lattice gap 0.10 (spec). The reference lattice looks a little denser; denser would exceed the 1000 budget (lattice 528 now).

## Rounds (live, 2 of 5)
0. Headless first build (spec numbers): all checks clean; 812 / 812 / 1264 tris.
1. Live build = headless. Compared with the reference at the front and 3/4; 128 px thumbnail reads (flat top with beams,
   lattice sides, open passage). Worst differences: squat reference proportions and cream colour (both fixed by the spec,
   deviations 1–2); gate swing limit found (91°).
2. Comparison camera moved to ~34° / 35 mm to match the reference; swing check at 1° steps. Nothing left but the spec-driven
   deviations, so no further geometry rounds. Export live + headless.

Remaining differences (nitpicks): beam proportions from a high frontal view (7.), lattice density (8.).
