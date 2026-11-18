# STA-07 Jam kettle - FMS_Workshop_STA_07

Reference: planning/FarmProcessing/references/STA-07.png (three-quarter front, camera slightly on the -X side, ~20 deg elevation).
Catalogue: "wide copper jam kettle on a small brick hearth, removable lid, separate wooden stirring paddle, opaque red jam surface",
X/depth/height 1.0/0.9/1.1 m, LOD0 1200-2400 tris, moving parts: lid (krishka), paddle (meshalka).

## Feature list (measured from the reference, 1 px ~ 1.16 mm at the pot; handles span = 1.0 m)
- Hearth (~0.40 m incl. top slabs, body width ~ pot width):
  - 2 stone plinth sills (left/right, full depth, 0.10 m, big top chamfer, project ~3 cm beyond the brick piers);
  - brick body 0.78 x 0.76, 2 courses of big red bricks (~0.10 m tall, 0.17-0.25 long), proud chamfered blocks over a dark
    mortar core, offset joints;
  - front fire opening 0.24 m wide from the ground, flat segmental arch (spring ~0.19, inner crown ~0.25) of 5 cream voussoirs,
    keystone taller, overlapping the slab front; dark soot chamber behind (no fire);
  - top: 3 x 2 grey-beige stone slabs (0.09 thick, top chamfer, 2.5 cm overhang), V-grooves between them.
- Kettle: wide copper pot (20 facets, D ~0.76, H ~0.33) RESTING ON the slab top: flat bottom D~0.58, darker lower taper band,
  bulging middle (widest ~ z+0.11..0.20), slight inward neck, thick rolled lip (light top). Inner wall ~6 cm above the jam.
- Handles: chunky round (8-gon, 3.8 cm) D-loops on +-X: from the rim lip out horizontally, round outer end, down-inwards to a
  copper octagonal boss plate with a grey hex bolt head on the bulge.
- Jam: flat opaque red surface (darker than #C8473B), 7 flat faceted hexagonal lumps (lighter red tops, darker sides), low.
- Paddle: wooden, blade (spade: wide flat blade with cut lower corners, tapered neck) stuck in the jam right of centre, facing
  the camera; chunky 8-gon handle (~4.8 cm) rising to the back-right, slightly thicker chamfered top end; top ~1.08 m.
- Lid: copper disc (fits the rim, D ~0.79), thick edge band + low dome, grey C-bar grip with feet, leaning on the hearth/pot at
  the LEFT side, bottom edge on the ground, face turned to the front-left.

## Material class
Flat palette (copper / brick / stone / jam / wood / metal; no textures, no noise). Own atlas T_FarmProcessing_STA07_BaseColor.png
(256 px, 4x4 solid cells, UVs at cell centres => padding), one material M_FarmProcessing_STA07.
Cells kept from STA-05 where the colour is used: 0 wood, 1 wood dark (= mortar), 3 cream, 4 cream dark, 5 red (lump tops),
6 red dark (lump sides), 7-9 metal, 11 wood darkest (= soot chamber). Repurposed (colour not used here): 2 -> stone #A7A39A,
10 -> copper #B87945, 12 -> copper light, 13 copper dark, 14 jam, 15 brick.

## NOT modelled
Fire, embers, smoke, ash, firewood, chimney, ground/floor, jam drips/splashes on the pot, jars, ladle, steam, text,
mortar texture/noise, rivets other than the handle bolts, interior pot floor (under the jam), LOD1 and collider (next step).

## Anchors followed
STA-01 cheese vat (closest: pot profile loft, round loop handles with hex bosses, ray-slid leaning lid with C-grip, paddle sweep,
checks/export/verify/render pipeline) and STA-05 juice press (palette layout, rect_prism/sweep helpers). Previews in
art/Farm_Processing/Previews/ (FMS_Workshop_STA_01_Preview.png, FMS_Workshop_STA_05_Preview.png).

## Hierarchy / pivots
FMS_Workshop_STA_07 (empty, ground centre of the hearth, identity) -> _Body (hearth + kettle + jam + handles, pivot 0,0,0),
_Lid (pivot at its bottom contact edge on the ground), _Paddle (pivot at the middle of the paddle axis). Front = -Y.

## Compare rounds (economy mode; ref | render | 128 px thumb via compare.py in %TEMP%, deleted)
1. Lid in front of the hearth and too face-on; lumps small/few; paddle too upright and thin; handles thin.
   -> lid azimuth 195, shift 0.05; lumps r 0.06-0.066 with 0.24 top inset; paddle top (0.50,0.20,1.08), blade 0.16; loops 4.2 cm.
2. Camera too high (big slab top); arch voussoirs small; copper dull brown; paddle blade narrow.
   -> VIEW_DIR z 0.32, arch bigger, copper light tone on the bulge bands (#D38E52), blade 0.19 x 0.04, handle 5.6 cm.
3. Pot too low vs ref (visible wall 0.30 of width vs 0.38); arch still small; lid hid the left plinth.
   -> pot height x1.12 (rim 0.767), opening half width 0.135, lid az 196 / shift 0, paddle more diagonal.
Final gate (full preview): arch voussoirs read as thin shards; jam ellipse too flat (camera too low); a slab corner pierced the
lid (white speck) -> elliptic arch (springers beside the opening, outer ring up to the slab, keystone over the slab edge),
VIEW_DIR z 0.38, lid RL 0.355 + back-off test (body vertices may not pierce the lid face; it was 8.9 cm, now <= 1 mm overlap).
Remaining nitpicks: ref stone is warmer/darker (pack stone #A7A39A kept), ref bolt bosses read more frontal, ref keystone larger,
ref lid slightly larger/more face-on, ref shows 7 lumps (5 visible here at the lower camera).

## Dimensions / deviations
Catalogue X/depth/height 1.0/0.9/1.1. Body 0.997 x 0.820 x 0.799 (handles span 1.00); with the paddle top Z 1.083.
Total X 1.261 / Y 0.917 because the lid stands set aside on the left as in the ref (same convention as STA-01).
Palette deviation: cells 2, 10, 12-15 repurposed (stone, copper x3, jam, brick) - cell 2 differs from STA-05 (wood mid unused here).

## Result
Tris (after lead review): Body 1876, Lid 256, Paddle 120 = 2252 (budget 1200-2400).
Checks: 0 non-manifold / loose / degenerate per part; Body X-mirror exact (jam lumps excluded); component gaps 0; plinths and
chamber wall on z=0; pot bottom rests on the slab top (3 mm sunk); lid touches the body (ray-slid + pierce back-off) with its
bottom edge on z=0; paddle blade sunk 6 cm in the jam.
FBX re-import: root empty + 3 meshes, 2252 tris, dims 1.261 x 0.917 x 1.084, texture found in FMS_Workshop_STA_07.fbm (256x256).
Pivots: Body (0,0,0); Lid (-0.628,-0.238,0) = bottom contact edge; Paddle (0.31,0.015,0.867) = middle of the paddle axis.
Lid and paddle are baked in their leaning pose (object rotation identity); "lid on the pot" needs a rotation in Unity.

## Lead review fix round
1. MAJOR arch rebuilt from one parametric ring: centre z 0.15, R 0.125/0.19 (keystone 0.205, tucked under the slab), 5 radial
   blocks (35/35/40/35/35 deg) with equal 1 cm joints, same depth, flush with the brick faces, on short brick jambs; front bricks
   around it are clipped along the voussoir faces / radial joints (1 cm joints); dark soot chamber floor added. Hearth +2.5 cm
   (brick top 0.335, slab top 0.425) to fit the round arch; courses 0.104-0.214 / 0.224-0.329.
2. Handles: copper boss plate + grey hex bolt at BOTH attachments (upper under the lip, lower on the bulge), handles turned 18 deg
   to the front so the bosses face the camera; loop top at rim level.
3. Brick #B9533D -> #D0583F (lighter, more orange; mortar contrast reads at 128 px).
Lid slide is now two-way (body vertices ray-cast onto the lid too) - the turned handle no longer pierces the lid.
