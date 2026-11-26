# FUR-02 Hammock on a stand `FMS_Garden_Hammock` — builder notes (Э7, batch 3, 2026-11-25)

Source of truth: `build.py` (`-- FUR-02 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in the collection `FUR-02_Hammock` (left in place);
headless the collection is `FMS_Garden_Hammock`. The owner's file was not saved (is_dirty False after every call), the
Cube and the other collections were not touched, the selection (Cube, active Cube) was unchanged after every call.
Check renders were made in a temporary scene (`TMP_FUR02_*`, removed after each render). Shared atlas A read only
(MD5 `119daf05…` unchanged; palette checked by pixel read: 0 mismatches); atlas F not used and unchanged.

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Hammock.fbx` (+ `.fbm` with the atlas copy) — root empty + `FMS_Garden_Hammock_Body` |
| Blend | `art/CottageGardenDecor/Blend/FMS_Garden_Hammock.blend` (collection-only library, headless) |
| Preview | `art/CottageGardenDecor/Previews/FMS_Garden_FUR_02_Preview.png` (one, series 3/4 from the front-right) |
| Tris / budget | **784 / 1000** — Feet 24, Posts 24, Beam 100, Rings 280, Cords 48, Cloth 308 |
| LOD | none (catalogue) |
| Size X × Y × Z (Blender) | 3.060 × 0.900 × 1.100 (Unity X × Z × Y) |

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint on the ground; FBX Y up, −Z forward baked, scale 1. One static mesh, pivot at
  the root. Blender X = along the hammock, −Y = front (Unity +Z), Z = up. The model is X- and Y-symmetric.

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, contact gaps 0 for every component; mirror X 0.000000.
- Coplanar overlapping faces 0.
- Ground: min z 0.0000, exactly the 8 bottom vertices of the 2 feet on z = 0; nothing else touches the ground.
- Functional: cloth bottom at X = 0 = 0.592 (spec 0.59); cloth → beam clearance 0.216 (no overlap); cloth → posts 0.22;
  beam lowest point 0.13 above the ground.
- SNAP: no contract (free-standing furniture).
- FBX re-import: 2 nodes (root + Body), 784 tris, dims 3.06 / 0.9 / 1.1, min z 0, texture found in the `.fbm`.
- Headless `build.py -- FUR-02 export` geometry SHA1 == live SHA1 `2e1a15bec370ffdab40dfec50ec119f8b67d4c3b`.

## Build (Blender coordinates)
- Cross-feet 0.16 (X) × 0.12 high × 0.90 (Y) at X ±1.45; posts 0.14 square, z 0.11 → 1.10 (1 cm into the foot).
- Bowed beam 0.12 × 0.12, 12 equal straight segments (mitred) on a half-ellipse: centre line 0.72 at the post axis,
  0.19 at X = 0 (bottom 0.13); both ends end inside the posts.
- Iron eyes: 8-sided rod 0.04 across flats, open ring (gap 85°–135°, upper inner side) of centre-line radius 0.06
  (outer Ø 0.16), centre z 1.00 on the inner post face, sunk ~1 cm into the post; ring plane XZ.
- Cords: 4 rods 0.04 square, slot 4, from 3 cm inside the gathered cloth end (Y ±0.055) to the lowest point of the ring.
- Cloth: closed shell 0.03 thick (measured normal to the sag), X ±1.16, 12 segments; centre-stripe top 0.62 at X = 0
  rising to 0.84 at the ends (cosh curve); width 0.90 in the middle → 0.14 at the ends; shallow dish (edges 6 cm higher
  in the middle); 5 lengthwise stripes cream 3 / blue 15 / cream / blue / cream on top and bottom, cream-dark 4 edges
  and end caps.

## Deviations from `prompts/FUR-02.3d.md` / the catalogue (for the reviewer)
1. **Beam joins the posts at 0.72, not 0.93**, and dips to 0.19 instead of 0.25 at X = 0: measured on the reference
   (joint ≈ 0.66–0.73 of the post height above the ground, beam middle close to the foot tops). Cloth clearance kept.
2. **Posts 0.14 square instead of 0.12, beam 0.12 deep instead of 0.14, feet 0.16 wide**: the spec beam (0.14 deep)
   would stick out of a 0.12 post at the joint; the reference post is wider than the beam; feet differ from the post
   width so their side faces are not coplanar.
3. **Posts 1.10 high with the rings on the inner face at z 0.94–1.06** (spec: rings above the post tops at 1.00–1.10):
   the reference shows the eyes below the post tops. Total height 1.10 = catalogue.
4. **Width 3.06 instead of 3.2** (catalogue): posts at X ±1.45 as the spec; nothing in the reference extends further.
5. **Cloth ends at X ±1.16, not ±1.30**: the reference cords are about 0.2–0.25 m long; with ±1.30 they would be
   almost invisible.
6. **Rings Ø 0.16 outer, rod 0.04** instead of ≈ Ø 0.12 / 0.035: the reference eyes are large and must read at 10 m.

## Rounds (3 live of 5)
1. First build: all checks clean, 784 tris. Worst differences at the reference angle: beam bow too shallow, cloth ends
   too close to the rings (cords hardly visible), rings small.
2. Beam middle 0.19 and steeper ends (ellipse half-axis 1.48), cloth ends ±1.16 and a steeper cloth sag (k 2.4), rings
   Ø 0.16; reference camera reproduced (front-left, yaw 28°, elevation 17°, long lens). Preview angle and 128 px
   thumbnail checked: reads as a striped hammock on an arched stand.
3. Cords spread to Y ±0.055 (two cords read as a V); close-up of the ring/cord/cloth end and a view from below checked.
   Only palette and nitpicks left — stopped here.

Remaining differences (nitpicks): cream cloth renders whiter and the wood paler than the reference (fixed palette); the
0.04 cords are slightly thicker than the gathered cloth end, so their tips show 5 mm above/below the cloth near the
end; the reference shows a slightly darker gathered band at the cloth ends (here the end caps and edges are cream-dark
slot 4 only); the reference perspective makes the posts look a little taller relative to the span.
