# STR-06 Hexagonal gazebo `FMS_Garden_Gazebo` — builder notes (Э7, pilot 3/3, 2026-11-25)

Source of truth: `build.py` (`-- STR-06 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback
mode; execute_blender_code and look both worked). Live work only in collection `STR-06_Gazebo` (left in place); the owner's
file was not saved, the default Cube and the WTR-03 / PLT-01 collections were not touched. Headless the collection is named
`FMS_Garden_Gazebo`, because `make_lod1.py` looks the collection up by the asset name.

## Result

| | |
|---|---|
| Size (Blender X×Y×Z) | X 3.579 (−1.577 … +2.002, entrance +X) × Y 3.584 (±1.792) × Z 4.000 m |
| Tris LOD0 | **2314 / 5000** — Base 152 (Skirt 28, Deck 104, Steps 20) · Frame 512 (Posts 360, RingBeam 48, Rafters + boss 104) · Railings 600 (Rails 120, Balusters 480) · Benches 108 (Seats 36, Legs 72) · Roof 942 (Shingles 790, Ribs 72, Spire 80) |
| Tris LOD1 | 1156 (50 %, `make_lod1.py`): Base 76, Frame 256, Railings 300, Benches 54, Roof 470 |
| Hierarchy / pivot | root empty `FMS_Garden_Gazebo` at (0,0,0) = centre of the hexagon on the ground; 5 meshes `_Base _Frame _Railings _Benches _Roof` (+ 5 `_Low1`), all direct children, pivot (0,0,0), rot 0, scale 1. Static, no moving parts |
| Material | one, `M_Garden_Build` + the shared `FMS_Garden_AtlasA.png` (read only, MD5 unchanged `119daf05…`; palette checked by pixel read: 0 mismatches) |
| Checks | every part: non-manifold 0, loose 0, degenerate 0, internal gaps 0; coplanar overlaps 0 per part **and 0 for all parts merged**; part contacts all 0.0 (Base–Frame, Railings–Frame, Benches–Base, Roof–Frame); mirror across the entrance axis (Y) 0.000000; min z 0.0000 (skirt and steps on the ground) |
| Opening | clear height deck → ring beam 2.10 m; clear width between the front posts 1.27 m (1.21 m between the capitals above z 2.27) |
| FBX verify | after LOD1: 11 nodes (empty + 5 + 5 `_Low1`), 3470 tris (2314 + 1156), dims 3.579 / 3.584 / 4.0, texture found in `FMS_Garden_Gazebo.fbm` |
| Headless | `build.py -- STR-06 export` geometry SHA1 == live SHA1 `f7431db3556f05ed06f081a80823ce92c9ca8dc2` (verts 80/282/400/72/489) |

## Build (what is where)

- **Base**: skirt hex prism R 1.50 (z 0–0.24, dark wood) + deck R 1.55 (z 0.24–0.36) as ONE shell with a ledge, so deck
  and skirt share no coplanar faces. Deck top = 12 boards (light wood) + 11 flush 16 mm joint strips (mid wood) running
  across X, as in the reference; the deck edge walls are zipped to the board vertices (no T-junctions).
  Steps: one L-section solid, 1.40 wide, two 0.12 rises (deck = third), treads 0.33 deep, back face 2 mm inside the skirt.
- **Frame**: 6 posts 0.18 square (chamfer 0.015) at R 1.45, axis aligned (flat face to the front, as in the reference),
  flared into a 0.24 capital at z 2.27–2.47; hex ring beam 0.10 × 0.14 (z 2.46–2.60); 6 rafters under the hips + hex
  boss at the centre (all embedded 1–1.5 cm in the roof shell).
- **Railings**: 5 faces (entrance open): top rail 0.10 × 0.08 (z 1.18–1.26), bottom rail 0.07 × 0.08 (z 0.46–0.54), 8
  balusters 0.06 × 0.05 per face, ends embedded in the posts/rails.
- **Benches**: 3 back faces, trapezoid seats 0.40 deep × 0.08 thick, top 0.81, ends cut parallel to the mitres and clear
  of the posts; 2 white block legs each.
- **Roof**: one closed hex shell: soffit z 2.59 (white ceiling) → fascia 0.12 (white) → 6 cm overhang → 7 shingle courses
  (each course top slightly steeper than the 33.4° pitch, a 35 mm riser = stepped lower edge) → hex peak cap. Tiles ~0.22
  wide, half-tile offset every other row, two tones mostly alternating with random runs (no diagonal stripes); risers and
  cap dark red. Hip ribs 0.10 wide, 0.085 proud of the hip. Spire: 8-sided iron rod with a collar r 0.13 (hides the rib
  ends), icosphere ball r 0.105 (subdiv 1), top at 4.00.

## Deviations from `prompts/STR-06.3d.md` (for the reviewer / spec owner)

1. **Posts are taller than in the reference (kept on purpose).** The reference is ~12–15 % squatter overall (its clear
   height deck → beam is ~1.7 m). The spec's collider note asks for a clear opening ≥ 2.1 m, so deck → beam is 2.10 and
   the total height stays at the catalogue 4.0. If the owner prefers the reference proportion, lower `Z_CAP*`, `Z_BEAM*`,
   `Z_SOFFIT`, `Z_FASCIA`, `Z_PEAK` and the spire z by the same amount (≈0.3 m) — no other change needed.
2. **Steps 0.33 deep, not 0.55** — the reference treads are ~0.3 m (the spec allows reducing the step depth). X span is
   therefore 3.58 m (catalogue 3.9, −8 %).
3. **Y span 3.58 (catalogue 3.4, +5.4 %)**: the eave circumradius is 1.70 as specified (3.40 across); the hip ribs and the
   shingle overhang add 9 cm at the two ±Y vertices.
4. **Thicker members than the spec, from the reference**: posts 0.18 (spec 0.14; reference ≈ 0.057 × roof width ≈ 0.19),
   capitals 0.24, balusters 0.06 × 0.05 (spec 0.05), seat 0.08 (spec 0.05), top rail 0.10 wide.
5. **Clear entrance width 1.27 m** (spec asks ≥ 1.40): with posts at R 1.45 the face is 1.45 long, so 1.40 is not
   reachable with any post ≥ 0.05; the spec's own numbers give 1.31 for 0.14 posts.
6. **Tile tones**: slots 5 `#C8473B` / 14 `#9C3F33` (spec 14 / 6). The reference tiles are bright (`#C5483B`, `#B04A3C`
   sampled); slot 6 `#A8372E` is used for the risers (stepped edges), the overhang underside and the peak cap.
7. **Ring beam / ceiling heights**: beam 2.46–2.60 as spec; the ceiling (soffit) is at 2.59 under a 0.12 fascia, so the
   eave top is 2.71 and the peak 3.68 (rise 0.97, pitch 33.4°, reference ≈ 0.95).

## Rounds (live, 4 of 5)

0. Headless first build (spec numbers): checks clean; steps far too deep vs reference, tiles merged into bands.
1. Steps 0.33, tiles alternate, bigger ball. Worst: posts/balusters thinner than the reference; preview hid the entrance.
2. Posts 0.18 / capitals 0.24, balusters 0.06, top rail 0.10, seat 0.08; comparison camera 14°, preview 3/4 more frontal.
   128 px thumbnail reads (roof, open entrance, steps).
3. Detail renders (roof from above, underside): alternating tones formed diagonal stair stripes; rib ends poked out at
   the apex. Underside (ceiling, beam, rafters, boss) OK.
4. Tones mostly alternating with random runs; spire collar covers the rib ends. Only the proportion note (1.) left.

Remaining differences (nitpicks): reference squatter (see 1.); reference capitals have small brackets; reference benches
reach closer to the posts; reference ball is a rounder 12-facet sphere.

## For the next builders (series)

- Atlas A: `art/AssetNew/Textures/FMS_Garden_AtlasA.png` + `M_Garden_Build`, cell layout in `../WTR-03_Birdbath/notes.md`.
  `atlas_and_material()` in build.py LOADS the PNG (never rewrites it, unlike `pc.atlas_image`), checks every palette cell
  by pixel read, and creates the material only when it is missing (in live Blender it reuses the existing one untouched).
- Helpers in build.py worth copying: `zipper()` (strip between two parallel polylines with different vertex counts — joins
  subdivided rings without T-junctions), `hexc()`, the shingle-course roof (`build_roof`: one closed shell of rings,
  stepped courses, tiles with half offset, works for any n-gon hip roof), `cross_contacts()` (gap between separate part
  objects), `all_coplanar()` (coplanar check on all parts merged, catches overlaps between objects), `mirror_y()`,
  multi-object `geom_dump()`, `render()` (temporary scene, only listed objects).
- `make_lod1.py` needs an ABSOLUTE `--art` path, and writes `Tools/blender/__pycache__` unless run with
  `--python-expr "import sys; sys.dont_write_bytecode=True"` before `--python` (PYTHONDONTWRITEBYTECODE is ignored).
- For LOD-friendly parts, split the model into a few mesh objects by role (base / frame / railings / furniture / roof):
  make_lod1 decimates per object, so balusters thin out in groups while the roof and frame keep their silhouette.
