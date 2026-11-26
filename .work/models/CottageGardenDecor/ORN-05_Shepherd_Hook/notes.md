# ORN-05 Shepherd's hook `FMS_Garden_Shepherd_Hook` (+ `_Feeder`): builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- ORN-05 build|export|verify|dump`). Built in the owner's live Blender 5.2 through the MCP
(the add-on reports OUTDATED; `execute_blender_code` and `look` worked). Live work only in the collections
`ORN-05_Shepherd_Hook` and `ORN-05_Shepherd_Hook_Feeder` (left in place). Renders ran in a temporary scene. The owner's
file was not saved. The default Cube and the other collections were not touched. The selection (Cube, active) was the
same before and after the live export.

## Result

| | base `FMS_Garden_Shepherd_Hook` | `_Feeder` |
|---|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Shepherd_Hook.fbx` (+ `.fbm`) | `art/CottageGardenDecor/Meshes/FMS_Garden_Shepherd_Hook_Feeder.fbx` (+ `.fbm`) |
| Blend (collection only) | `art/CottageGardenDecor/Blend/FMS_Garden_Shepherd_Hook.blend` | `art/CottageGardenDecor/Blend/FMS_Garden_Shepherd_Hook_Feeder.blend` |
| Preview | ONE: `art/CottageGardenDecor/Previews/FMS_Garden_ORN_05_Preview.png` (base) | check render only: `%TEMP%/assetnew_check/ORN-05/ORN-05_Feeder_check.png` (headless) |
| Tris / budget | **600 / 600**: Body 310 (Hook 222, Scroll 76, Footrest 12) + Hanging 290 (Ring 30, Rods 60, Bowl 44, Drops 60, Blooms 96) | **578 / 600**: Body 310 + Hanging 268 (Ring 30, Rods 60, Tray 28, Feeder body 60, Grain 48, Roof 30, Knob 12) |
| Size (Blender X × Y × Z) | 0.557 × 0.282 × 1.701 (x −0.124…0.433, y −0.145…0.137) | 0.572 × 0.304 × 1.701 (x −0.124…0.448, y ±0.152) |
| Nodes | root empty + `_Body` + `Hanging` (bare spec name in the FBX, `<asset>_Hanging` in the .blend) | same |
| Material | `M_Garden_Flora` + shared `Textures/FMS_Garden_AtlasF.png` (read only, MD5 `ae0f0dba…` unchanged; palette pixel check 0 mismatches) | same |
| Cells | F0/F1/F2 leaves, F6/F7/F8 petals, F11 centres, F10 iron, F12 soil, F13 basket | F10 iron, F11 grain, F12 roof, F13 body, F14 tray |
| LOD | none (catalogue) | none |

## Pivots and axes
- Root (0, 0, 0) = foot of the pole = spike tip on the ground; rot 0, scale 1; FBX Y up, −Z forward baked. The spec gives
  "pole at X −0.20, pivot at the pole foot". I read this as root = pole foot, so in model space the pole is at x 0 and
  everything else is +0.20 from the spec numbers (hanging point spec +0.14 → +0.34; built +0.296).
- `Hanging` (direct root child): pivot at Blender (0.296, 0, 1.454) = centre-line of the hook curl at its bottom segment,
  where the ring hangs. Static. It holds the ring, the 3 rods and the basket with its plants (or the feeder).
- Blender X = towards the hook, −Y = front, Z = up. Under the series assumption that Unity's FBX import negates X, the hook
  points to Unity −X. It is decorative and can be rotated 180° about Y in the prefab; the pivot does not move.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0 on both parts of both assets. Internal gaps 0: every component touches another.
- Coplanar overlapping face pairs 0 (Body + Hanging merged, both assets).
- Ground contact: one ground point, the spike tip (0, 0, 0); min z 0.0000; nothing below 0.
- Ring on the hook: BVH overlap with the curl rod (gap 0). The ring rests on the rod top with 1 mm overlap.
- Scroll self-clearance (centre-lines, non-neighbouring samples) 0.043 ≥ bar 0.030. Curls are 0.10–0.12 across.
- SNAP: no module contract for this item. Footprint ≈ 0.56 × 0.28 (catalogue 0.5 × 0.3, see below).
- FBX re-import (both): 3 nodes (root, Body, `Hanging`), tris 600 / 578, dims 0.557/0.282/1.701 and 0.572/0.304/1.701,
  min z 0, `Hanging` at (0.296, 0, 1.454). Atlas found in the `.fbm`.
- Headless `build.py -- ORN-05 export` geometry SHA1 == live SHA1 `cf5749e1550c79ef12fdfe65f62d3c6e4374baf7`
  (4 meshes, verts 161/171/161/160, faces 162/241/162/195). The headless run wrote the final art files.

## Build (what is where; measured on references/ORN-05.png: height 1137 px = 1.70 m)
- Hook: ONE closed 8-sided sweep from the spike tip (ground) → collar ring Ø0.054 at z 0.13 → pole Ø0.040 from 0.165 to
  the bend at 1.50 → semicircular arc R 0.18 in 6 segments (outer top 1.70, right side at x 0.36) → spiral curl in
  5 × 60° (R 0.066 → 0.024, tapering to Ø0.030), end cap. Reference: bend ~1.50, top 1.70, hanging point ~1.47.
- Footrest: square bar 0.03 along +X at z 0.28, to x 0.15 (reference 0.28; spec 0.18).
- S-scroll on the −X side (reference): the STR-02 `s_curve()` (both curls touch the pole, bar sunk 4 mm). R 0.045,
  curls 4 + 4 segments, 290°, top curl centre z 1.04, bottom 0.86; reaches x −0.124. Square bar 0.03, flat face to the front.
- Ring: pentagon with a flat top and a vertex at the bottom, triangular wire 0.024. It sits in the YZ plane, threaded on the
  curl's bottom segment (there the rod runs along X). Ring ~0.09 high.
- Rods: 3 × 6-sided Ø0.03 from the ring's bottom vertex to the rim (r 0.122, z 1.138). Azimuths 8.7° / 128.7° / 248.7°:
  two at ±60° from the preview camera, one behind.
- Basket: 8-sided flared bowl (flat to −Y): bottom across-flats 0.16 at z 1.03, rim 0.274 at 1.15, sloped inner lip to
  the soil disc (F12) at 1.136.
- Foliage: 3 drops (PLT-01 `leaf_cluster` v2, scaled down to ico sub 1 = 20 tris), D 0.17, between the rods, mound to ~1.27.
- Blooms: 6 cups, 6-sided, 16 tris, Ø0.09 (2 white F8, 2 pink F7/F6, 2 deep pink F6), yellow F11 centres. They sit on the
  drops (ray cast) and tilt towards the preview camera. One white cup is on the crown, as in the reference.
- Feeder (`_Feeder`): the same Body, ring and rods. Tray: 8-sided, across flats 0.26, z 0.935–0.955, F14. Body: 8-sided,
  across flats 0.20, z 0.95–1.132, F13. Two windows 0.064 × 0.08, on the front (−Y) and right (+X) facets, each with a
  0.045 recess and 3 yellow grain lumps poking out. Roof: eave band + cone, across flats 0.30, z 1.127–1.227, F12, with a
  knob to 1.268. The rods end inside the roof slope. No birds.

## Budget decisions (target 600, the spec sum underestimated caps)
- 8-sided as the spec asks: the hook (pole, arc, curl). The spike and collar are part of the same sweep, so no extra caps.
- 6-sided: the suspension rods (Ø0.03). Square 0.03 bar: the S-scroll and the footrest. This is the usual flat-faced
  wrought-iron scroll bar. It frees 16 + 8 tris, which give the scroll curls 4 segments each instead of 3; with
  97° steps they read as square hooks (round 1).
- Ring: 5 segments, triangular wire (30 tris). Bowl without a separate rim band (44 tris).
- STR-02's anchor scroll bar is 8-sided. An 8-sided scroll here would cost ~+40 tris, and the base is already at 600.

## Rounds (live, 4 of 5)
1. 658 tris (over). The scroll curls were square (3 × 97°). The ring and curl formed a tight knot, and the feeder window was tiny.
2. Square bars for the scroll and footrest, ring with a triangular section, bowl without the band, curl R0 0.056 → 0.066,
   bigger feeder window → 598.
3. Pole Ø0.040 (STR-02 anchor), 5-segment ring (−6 tris) → bottom scroll curl 4 segments, second feeder window (+X) → 600.
4. Blooms rearranged. The crown was empty, and the reference has a white cup on top.

## Remaining differences vs the reference
- The ring hangs in the YZ plane (threaded on the curl). From the front reference view it is edge-on; the reference
  draws it as a full circle facing the viewer. From the series preview angle it reads as an oval link.
- The rods meet in one node under the ring. The 6-sided ends make a small knot, and the two front rods cross in front of
  the flowers in the preview.
- The flower mound is a little lower and sparser than the reference (3 drops / 6 cups within 600 tris). The basket has
  no separate rim band.
- Scroll bars are square, not 8-sided, and the curl facets stay visible (4 segments per curl).
- Size 0.557 × 0.282 × 1.701 vs catalogue 0.5 × 0.3 × 1.7. The scroll on the −X side (reference) adds 0.124 to the left of
  the pole, which the catalogue footprint (X −0.22…+0.30, pole at −0.20) did not include.
- Heights follow the reference, not the spec table: bend 1.50 (spec 1.45), hanging point 1.454 (spec 1.64), rim 1.15
  (spec 1.32), footrest 0.28 (spec 0.18).
- `_Feeder`: the roof F12 `#805433` and body F13 `#7A5233` (as specified) are almost the same brown; only the lighting
  separates them. Windows are 0.064 wide instead of 0.10, because an 8-sided Ø0.20 body has 0.083-wide facets. The second
  window (+X) is an addition, so the feeder reads from the preview side.
