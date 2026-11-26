# FLB-02 Corner bed `FMS_Garden_Bed_Corner` + FLB-03 Round bed `FMS_Garden_Bed_Round` (each + `_Planted`) — builder notes (Э7, series batch 2, 2026-11-25)

Source of truth: `build.py` (`-- FLB-02|FLB-03 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED;
execute_blender_code and look work). Live work only in collections `FLB-02_Bed_Corner` (+ child `..._Planted`) and
`FLB-03_Bed_Round` (+ child `..._Planted`). Kerb block, soil relief contract, plant generators copied from FLB-01
`build.py` (PLT-01 leaf drops, cup blooms, small cups, spikes).

## Rounds

### Pre-check (headless, before the live rounds)
Both models build with all checks green except: FLB-02 three filler drops touched the border blocks; FLB-03 `_Planted`
1826/1800 tris. Soil dome/mound read flat; filler drops (sub-1 icospheres) stood alone on bare soil like green stones.
-> fillers bigger (D 0.24-0.28) and nestled against the clumps at the front gaps; yellow clumps 4 small cups (was 6);
valleys lowered to 0.150-0.158, rim spread 0.141-0.168.

### FLB-02 round 1 (live)
All checks pass (base 252/400, planted 2012/2200, SNAP all OK incl. FLB-01 joins). Reads as an L planted bed at 128 px.
Worst differences:
1. Base soil still nearly one-toned vs the reference's lumpy facets (contract crown 0.20 / rim ~0.16 limits the slopes).
2. Corner lilac crown small: the tallest planting in the corner square should dominate more (spec: tallest in the corner,
   falling to ~0.45 at the arm ends); pink/white clumps all at the same ~0.5.
3. Front is now mostly covered; the filler at the right-arm end stands a bit alone.

### FLB-03 round 1 (live)
All checks pass (base 246/400, planted 1762/1800, SNAP all OK). Tiers read: lilac spikes centre 0.80, pink/white middle
ring ~0.55, yellow outer ring ~0.43. Worst differences:
1. Soil dome one-toned (4 shoulder points 0.18-0.19, rim 0.14-0.17: slopes too small to show facets).
2. Front filler drop (sub-1 icosphere) stands alone in front of the pink clump like a green stone.
3. Block joints (tapered reveal) read as thin dark lines as in the reference — OK.

### Round 2 (live, both)
FLB-02: lilac drop D 0.48 + 8 ring spikes (tip drop 0.03-0.08), corner pinks D 0.40, L valleys 0.142-0.150.
FLB-03: dome = apex 0.20 + 6 shoulders (0.172-0.194, R 0.47-0.52) + rim 0.136-0.168 (58 tris), fillers to R 0.61.
Result: soil still subtle (contract), FLB-03 front filler still separate, FLB-02 lilac crown still low over its drop.

### Round 3 (live, both) — accepted
FLB-02: lilac drop flatter (H 0.70) so the spikes stand ~0.2 clear; right-arm end filler nestled between the yellow and
pink clumps. FLB-03: fillers R 0.56, H 0.64 — they now read as the low foliage skirt of the middle-ring clumps.
128 px thumbnails: L / round stone kerb with green mass, colour dots and a lilac crown (corner / centre). Only nitpicks
left -> exported.

## Result

| | FLB-02 base `FMS_Garden_Bed_Corner` | FLB-02 `_Planted` | FLB-03 base `FMS_Garden_Bed_Round` | FLB-03 `_Planted` |
|---|---|---|---|---|
| Size (Blender X × Y × Z) | 2.000 × 2.000 × 0.250 | 2.000 × 2.000 × 0.700 | 2.000 × 2.000 × 0.250 | 2.000 × 2.000 × 0.800 |
| Tris LOD0 | **252 / 400**: blocks 192 (16 × 12), soil 60 | **2024 / 2200**: 4 border parts × 48, soil 60, Foliage 920 (10 drops × 80 + 6 fillers × 20), Flowers 852 (28 cups × 22, 8 small cups × 16, 9 spikes × 12) | **250 / 400**: blocks 192, soil 58 | **1766 / 1800**: 4 border parts × 48, soil 58, Foliage 800 (9 × 80 + 4 × 20), Flowers 716 (16 cups, 16 small cups, 9 spikes) |
| LOD1 (make_lod1) | none (catalogue) | 1138 (56 %): borders/soil kept, Foliage 460, Flowers 426 | none | 1008 (57 %): borders/soil kept, Foliage 400, Flowers 358 |
| Objects | root + `_Body` | root + 7 parts (+ 7 `_Low1`) | root + `_Body` | root + 7 parts (+ 7 `_Low1`) |

Pivot: centre of the 2.0 × 2.0 footprint bounding box on the ground (0,0,0), scale 1, rot 0. Material `M_Garden_Flora`,
atlas F `FMS_Garden_AtlasF.png` loaded read-only (palette verified by pixel read, 0 mismatches; file untouched).
Slots as FLB-01: block sides/bottom 14, tops 15, soil 12, foliage 0/1/2 by normal, pink cups 7/6/11, white 8/8/11,
yellow 11, lilac 9.

Checks (each model, whole model merged): non-manifold 0, loose 0, degenerate 0, coplanar overlapping pairs 0, contact
gaps 0, blocks on the ground (min z 0.0000), planting shells touching the border: none.

SNAP (all OK, printed by `build`):
- FLB-02: bbox exactly ±1.000, every vertex inside the L polygon (missing quadrant Blender x<0,y<0 empty), each of the
  6 outline edges carries block faces exactly on it; FLB-02|FLB-01 at the back-arm end (FLB-01 at x −2, y +0.5) and
  FLB-01 turned 90° at the right-arm end (x +0.5, y −2) and along the back (y +1.5): penetration 0.0000, touching;
  FLB-02|FLB-02 along X and Y (+2.0): 0.0000; FLB-01 border top 0.250 = FLB-02; soil crown 0.200; planting top
  0.700, margin to the outer faces 0.145.
- FLB-03: bbox exactly ±1.000, 16 outer vertices on R 1.0000; FLB-03|FLB-01 tangent (x +2), FLB-03|FLB-03 along X/Y:
  penetration 0.0000, touching at the cardinal vertices; soil crown 0.200; planting top 0.800, margin 0.157.

FBX re-import (after LOD1): FLB-02 base 2 nodes 252 tris dims 2/2/0.25; `_Planted` 15 nodes 3162 tris (2024 + 1138)
dims 2/2/0.7; FLB-03 base 2 nodes 250 tris; `_Planted` 15 nodes 2774 (1766 + 1008) dims 2/2/0.8; texture found in each
`.fbm`. Headless `build.py -- <ID> export` geometry SHA1 (world verts + face UV cells of all 8 meshes) == live:
FLB-02 `14351a49…`, FLB-03 `11416fff…`. Live selection/active restored after the exports.

## Build

- FLB-02 border: 16 boxes, 0.01 reveals, outer faces exactly on the L outline. Back (y 0.88..1) 0.48/0.42/0.50/0.44 from
  x −0.87 (owns corner +x+y); right 0.44/0.50/0.42/0.48 from y 0.87 down (owns +x−y); right-arm front 0.46/0.40 from x 0
  (owns 0,−1); inner x side 0.45/0.53 from y −0.87 (the 0.53 block is the closed re-entrant corner block, x 0..0.12,
  y −0.41..0.12); inner y side 0.52/0.46 from x −1 (owns −1,0); left 0.42/0.44 from y 0.13 (owns −1,+1).
- FLB-03 border: 16 trapezoid blocks (22.5°), outer vertices shared exactly on R 1.0 (bbox ±1.0, beds touch at points),
  inner corners pulled back along the inner 16-gon edge by 0.005 -> tapered reveal 0 (outer) .. 0.01 (inner): dark joint
  line on top as in the reference, joint faces 4.8° apart (no coplanar faces).
- Soil: CDT (`delaunay_2d_cdt`, inside-only) of the rim polygon + interior points, closed solid, rim 0.01 into the blocks,
  bottom 5 mm above the block bottoms. L: 16 rim + 10 interior points, skirt one vertical polygon per outline edge down to
  the 6 corners, L cap -> 60 tris. Round: 16 rim + apex + 6 shoulders, skirt 24 triangles to an octagon on R 0.963,
  octagon cap -> 58 tris. Both ≤ 60 so make_lod1 keeps them exact (rim stays closed against the blocks in LOD1).
- Planting (FLB-01 generators, PLT-01 drops): FLB-01 review applied — no brown stalks (no lollipops), pink/white cups sit
  on the foliage (4 per clump) tilted 26-40° (≈10° more than FLB-01) towards the viewer; low sub-1 filler drops nestled
  against clumps at the front gaps. FLB-02: 10 clumps zig-zag along both arms (Y P W P | W L | P W P Y), lilac (8+1
  spikes, top 0.70) in the corner square (Blender x,y 0..1 = Unity X,Z −1..0), yellow clumps at the free arm ends
  (~0.45), 6 fillers. FLB-03: 9 clumps tiered — centre lilac D 0.46 (9 spikes, top 0.80), middle ring R 0.37 pink/white
  D 0.40 (~0.55), outer ring R 0.62 yellow D 0.38 (~0.43), 4 fillers at R 0.56.

## Deviations / remaining differences vs reference

1. Soil relief subtler than in both references (contract crown 0.20 / rim ~0.16 limits slopes to ~5-8°); same as
   FLB-01. Rim varies 0.136-0.168 (“about 0.16”), valleys 0.142-0.150.
2. Stone greyer/cooler than the beige reference blocks — palette decision (slots 14/15), as FLB-01/WTR-03.
3. FLB-03 joints taper (0 at the outer face) instead of a parallel 0.01 reveal, to keep the 16 outer vertices exactly on
   R 1.0 (a parallel reveal would pull the bbox to 0.9992 and leave a 1.6 mm gap between touching round beds).
4. Soil top: 34 tris (FLB-02) / 28 (FLB-03) instead of a plain 16-sector fan — more facets as in the references.
5. Unity orientation: the L is built with the missing quadrant at Blender x<0, y<0 = Unity X>0, Z>0 under the series'
   X-flip assumption (Blender (x,y,z) -> Unity (−x,z,−y)); verify once at the first import (Э8) with MOD-06/STR-01.
6. `_Planted` blends (`..._Planted.blend`) written for make_lod1 (as FLB-01). Live export wrote the files first; the
   headless export then rewrote them (identical geometry, collections named after the asset for make_lod1).
7. Preview = base bed (one preview per ID); `_Planted` check renders (headless, preview camera):
   `%TEMP%/assetnew_check/FLB-02/FLB-02_Planted_check.png`, `%TEMP%/assetnew_check/FLB-03/FLB-03_Planted_check.png`.
8. FLB-03 front ring shows some soil between the outer yellow clumps (tiered layout); FLB-02 lilac spikes are short
   (~0.2 above the foliage) because the corner limit is 0.70.
