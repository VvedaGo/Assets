# STA-01 Cheese-making vat - FMS_Workshop_STA_01

Reference: planning/FarmProcessing/references/STA-01.png (three-quarter front, camera on the -X side, ~20 deg yaw, ~20 deg elevation).
Catalogue: "open round cheese-making vat on a low stand, a removable lid and separate stirring paddle, simple cream curd surface",
X/depth/height 1.2/1.0/1.1 m, LOD0 1200-2400 tris, moving parts: lid, paddle.

## Feature list (from the reference)
- Big straight-walled METAL pot (grey, ~20 facets), thick outward rim lip with a light top face, darker inner wall band
  visible above the curd, chamfered bottom edge; pot is wide and fairly shallow (D ~0.86, visible wall ~0.4 m).
- Two loop handles on the +-X sides: octagonal boss on the wall under the rim, flat bar loop going out and up, top bar at rim
  height, running back into the rim lip.
- Curd: cream surface ~6 cm below the rim, slightly domed, faceted, with a few big pale low faceted curd chunks (not noise).
- Wooden stand (low stool): thick chamfered 20-gon ring board; the pot's flat bottom rests ON it, 4 chunky splayed square legs at the diagonals with chamfered head blocks
  protruding through/above the ring, red square caps on the heads' front/back faces, low stretchers on 4 sides.
- Lid: round flat metal lid with chamfered edge, slight dome, C-shaped bar grip; leaning against the stand on the front-left,
  bottom edge on the ground (kept where the ref shows it).
- Paddle: wooden stirring paddle, square chamfered handle with a slightly flared chamfered top end, flat blade with a tapered neck,
  blade stuck in the curd right of centre, handle leaning to the back-right, top above the right handle.

## Material class
Flat palette (metal pot + plain wood, no grain in the ref): own atlas T_FarmProcessing_STA01_BaseColor.png (256 px, 4x4 solid
cells, UVs at cell centres => padding), one material M_FarmProcessing_STA01. Cells 0-12 identical to STA-02/STA-05;
13 = curd surface, 14 = curd edge (darker), 15 spare. No noise.

## NOT modelled
Fire/heater under the pot, thermometer, cloth, whey, drips, floor/platform, text, nails/screws besides the red caps and handle
bosses, wood grain, pot floor interior (hidden under the curd), individual curd crumbs, LOD1 and collider (next step).

## Anchors followed
STA-05 juice press (build_juice_press.py: leg heads + red caps, splayed legs, stretchers, rect_prism/sweep helpers, checks, export,
render_preview.py) and STA-02 cheese press (palette layout, accepted pilot). Both previews in art/Farm_Processing/Previews/.

## Hierarchy / pivots
FMS_Workshop_STA_01 (empty, ground centre, identity) -> _Body (0,0,0: pot + stand + curd + handles),
_Lid (pivot at its bottom contact edge on the ground, as leaning in the ref), _Paddle (pivot at the middle of the paddle axis).
Front = -Y.

## Compare rounds (economy mode; preview camera, ref | render | 128 px thumb sheets via compare.py, %TEMP%, deleted)
1. Lid faced the camera and hid the whole front-left stand; stand too tall vs pot; paddle short/thin; camera too low (curd ellipse flat).
   -> pot R 0.41, rim 0.80, ring 0.32-0.45, heads/legs chunkier, paddle 0.24x0.15 blade + 0.046 handle, elevation 0.40 -> 0.55.
2. Lid too edge-on; handles thin wire-like; curd chunks few/small.
   -> lid azimuth 201, handle bar 0.038x0.05, 9 larger chunks. Back view (0.9,1,0.45) checked: lid leans on the left handle + ring.
3. Lid still covered the front-left leg (ref: leg + red cap visible right of the lid); heads barely above the ring.
   -> lid azimuth 205 and moved to the left (LID_SHIFT 0.16), head top 0.525. Confirmed in the r4 check and the final preview.
Remaining nitpicks: ref metal is neutral darker grey and wood more orange (pack palette kept); ref legs splay a bit more; ref
paddle blade shows its face more; the ref lid is slightly more face-on.

## Lead review fixes (round 4-5)
Pot now sits ON a ring board (top 0.40, pot 0.40-0.88; stand ~45% / pot ~55% of the body height, paddle top 1.10);
round 8-gon loop handles (3.8 cm, 6-segment arc) between two hex bolt bosses per side; chunky lid bracket (4.6x5.2 cm);
paddle: 8-gon 4.8 cm handle, 12 cm blade rising at the back right; curd chunks = faceted half-sunk mounds (8);
preview elevation ~23 deg (VIEW_DIR z 0.45). Lid moved further left (LID_SHIFT 0.24) so the front-left leg stays visible.
Remaining nitpicks: paddle still slimmer than the ref; blade partly hidden by a chunk; ref metal darker/neutral, wood more orange.

## Dimensions / deviations
Catalogue X/depth/height 1.2/1.0/1.1. Body (pot + stand + handles) 1.177 x 1.026 x 0.896; with the paddle top Z 1.111.
Total X 1.413 because the lid stands set aside on the left as in the ref (ref itself is ~1.5 pot widths wide). If a tight
footprint is needed, place the lid on the pot in Unity or move it; the body alone matches 1.2/1.0.

## Result
Tris: Body 2012, Lid 256, Paddle 120 = 2388 (budget 1200-2400).
Checks: 0 non-manifold / loose / degenerate per part; Body X-mirror exact (curd chunks excluded); component gaps 0; legs on z=0;
lid touches the body (ray-slid until contact, 1.5 mm overlap) with its bottom edge on z=0; paddle blade sunk in the curd.
FBX re-import: root empty + 3 meshes, 2388 tris, dims 1.413 x 1.026 x 1.110, texture found in FMS_Workshop_STA_01.fbm (256x256).
Pivots: Body (0,0,0); Lid (-0.671,-0.124,0) = its bottom contact edge; Paddle (0.315,0.2,0.935) = middle of the paddle axis.
Lid and paddle meshes are baked in their leaning pose (object rotation identity), so "lid on the pot" needs a rotation in Unity.
