# FLB-01 Straight flower bed `FMS_Garden_Bed_Straight` (+ `_Planted`) — builder notes (Э7, series batch 1, 2026-11-25)

Source of truth: `build.py` (`-- FLB-01 build|export|verify`). Live Blender 5.2 via MCP (add-on reported OUTDATED;
execute_blender_code and look work). Live work only in collection `FLB-01_Bed_Straight` (+ child `FLB-01_Bed_Straight_Planted`).

## Rounds

### Round 1 (live)
All checks pass (base 202/300, planted 1454/1500, non-manifold/loose/degenerate 0, coplanar 0, SNAP all OK).
Worst differences vs reference / spec intent:
1. Soil mound reads flat: relief 0.155-0.20 over 1.78 m gives ~6 deg facets, no visible facet tones (reference: lumpy
   facets with clear light/dark planes). -> more interior points, crown points alternating 0.20/0.19, side valleys 0.165-0.17,
   rim 0.145-0.165.
2. `_Planted` cups read as flat squares/diamonds: cups only 0.035 deep, tilted OUTWARD (back clumps tilt away from the
   camera), square 4-gon centre dominates. -> deeper cups (0.045), raised petal tips + deeper notches (0.72 r), tilt
   towards the viewer side (front-left) mixed with a little outward.
3. Brown stalks 0.15-0.20 visible -> "lollipops"; clumps stand apart on bare soil. -> bigger drops (D 0.38-0.40, ends
   0.34), stalk tops capped at drop top + 0.11 (visible stalk <= ~0.08); crown 0.70 carried by the lilac spikes.

### Round 2 (live)
Cups lean towards the viewer, drops bigger, stalks shorter: reads as a planted bed. Left: cups still read as squares
(4 petal tips = square outline); soil still flat. -> rim almost round (notch 0.90 r, notch 0.014 lower = wavy rim),
stalk cap 0.09, soil valleys lowered to 0.157-0.162.

### Round 3 (live)
Blooms read as round flowers (pink/white with yellow centres, yellow small cups, lilac spikes). 128 px thumbnails:
base = stone kerb with soil, `_Planted` = green clumps + colour dots + lilac crown. Soil relief stays subtle (see below).

### Round 4 (live)
LOD test showed the 64-tri soil was decimated by make_lod1 (threshold > 60): soil reduced to 8 interior points = 60 tris,
so it keeps its exact LOD0 shape (rim closed against the blocks) in LOD1. Accepted; exported.

## Result

| | Base `FMS_Garden_Bed_Straight` | `FMS_Garden_Bed_Straight_Planted` |
|---|---|---|
| Size (Blender X × Y × Z) | 2.000 × 1.000 × 0.250 | 2.000 × 1.000 × 0.700 |
| Tris | **204 / 300**: blocks 144 (12 × 12), soil 60 | **1456 / 1500**: Border_S 48, Border_N 48, Border_Ends 48, Soil 60, Foliage 560 (7 drops × 80), Flowers 692 (16 cups × 22, 12 small cups × 16, 7 spikes × 12, 8 stalks × 8) |
| LOD1 | none (catalogue) | `make_lod1.py`: 830 (57 %): borders and soil kept (≤ 60 tris each), Foliage 280, Flowers ~342-346 |
| Objects | root empty + `_Body` | root empty + 6 parts (+ 6 `_Low1` after make_lod1) |
| Pivot | centre of the footprint on the ground (0,0,0), scale 1, rot 0 | same |
| Material | `M_Garden_Flora`, atlas F `FMS_Garden_AtlasF.png` (loaded read-only, palette verified by pixel read, 0 mismatches) | same |

Slots: block sides/bottom 14 `#A7A39A`, block tops 15 `#C9C3B6`, soil 12; foliage 0/1/2 by face normal, stalks 13,
pink cups 7 outer / 6 inner / 11 centre, white cups 8/8/11, yellow small cups 11, lilac spikes 9.

Checks (both, whole model): non-manifold 0, loose 0, degenerate 0, coplanar overlapping pairs 0 (all parts merged),
contact gaps 0 (every block touches the soil, every plant shell sits in its drop), blocks on the ground (min z 0.0000),
planting shells touching border blocks: none, all bloom/cup/spike bases inside their drops.
SNAP (all OK): footprint exactly X ±1.000, Y ±0.500, min z 0; bed|bed along X (+2.0) and Y (+1.0) gap 0.0000 for base,
planted and base|planted; border top 0.250; soil crown 0.200; planting X −0.812…0.816, Y −0.340…0.342, top 0.700,
margin to the outer face 0.158 (≥ 0.02).
FBX re-import: base 2 nodes, 204 tris, dims 2.0/1.0/0.25; planted after LOD1 13 nodes (empty + 6 + 6 `_Low1`),
2282 tris (1456 + 826), dims 2.0/1.0/0.7; texture found in each `.fbm`.
Headless `build.py -- FLB-01 export` SHA1 of all 7 meshes (world verts + face UV cells) == live: `f6019a6a…`.

## Build

- Border: 12 closed boxes (long sides 4 blocks each, running the full 2.0 incl. the corners: front 0.55/0.45/0.52/0.45,
  back 0.42/0.56/0.48/0.51 — joints staggered; short ends 2 blocks each 0.40/0.33 between the long blocks), 0.01
  reveals, outer faces exactly on the footprint, all tops 0.25.
- Soil: CDT (`delaunay_2d_cdt`) of a 12-point rim (0.146-0.165) + 8 interior points (crown 0.20/0.19, valleys 0.157-0.162),
  skirt to z 0.005 and bottom cap; the rim reaches 0.01 into the blocks (closed against the inner faces, no coplanar
  faces; bottom 5 mm above the block bottoms).
- Planting: 7 clumps zig-zag along the bed (yellow, pink, white, lilac, pink, white, yellow — no equal colours touch),
  PLT-01 `leaf_cluster` drops (D 0.34-0.40, 0.80 D, sunk 0.03 into the soil); pink/white: 2 cups on the foliage + 2 on
  short brown stalks; yellow: 6 small cups; lilac: 7 spikes, centre tip at 0.70. Crown envelope 0.70 (centre) → 0.45
  (x ±0.66).

## Deviations / remaining differences vs reference

1. Soil relief reads subtler than in the reference: the contract (rim ~0.16, crown 0.20, border 0.25) limits the facets
   to ~10° slopes, so under the series light the planes differ only slightly in tone. Not changed (contract numbers win).
2. Stone looks greyer/cooler than the reference's beige blocks — palette effect (slots 14/15), as noted for WTR-03.
3. Soil top 26 tris, not 6-8 (spec): the reference shows many more facets; base still 204/300.
4. `_Planted` crown: only the lilac spikes reach 0.70; pink/white stalk blooms stop at drop top + 0.09 (≈0.55-0.58)
   instead of the envelope (0.59-0.67), to avoid long bare stalks ("lollipops").
5. Extra file outside the listed write set: `art/AssetNew/Blend/FMS_Garden_Bed_Straight_Planted.blend` — make_lod1.py
   reads `<art>/Blend/<NAME>.blend` with a collection named NAME, so the LOD1 the catalogue asks for needs it.
6. `_Planted` borders split into 3 parts of 4 blocks (48 tris) so make_lod1 keeps them exact (> 60 tris would be
   collapsed into wedges and break the snap faces in LOD1).
7. Preview is the base bed (one preview per ID); `_Planted` check renders only in %TEMP%/assetnew_check/FLB-01/.
