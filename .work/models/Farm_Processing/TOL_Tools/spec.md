# TOL-01..05 — small processing tools (built by the lead, 2026-11-14)

One parametric script `build_tools.py -- <TOL0X> build|export` (registry `REG`). Headless Blender 5.2, shared helpers from `_common/processing_common.py` (read-only). New local helpers: `shell()` (n-gon solid of revolution with through-holes in wall bands and caps, via bmesh `triangle_fill` with hole loops + tubes), `path_sweep()` (mitred loop handles), `rest_on_ground()` (tilts a lying tool so both ends touch z=0), `bolt()`, `oct_rod()`.

Material class: flat palette, one material + own 4x4 atlas per item (`M_FarmProcessing_TOL0X`, `T_FarmProcessing_TOL0X_BaseColor.png`). Cells as STA-03/05 except cell 10 (hole interior) darkened to #B39C74 so perforations read, 13 handle wood #C99263, 14 spatula blade #A26A43, 15 colander foot #857B6E.
Hierarchy: root `FMS_Workshop_TOL_0X` + `_Body` (no moving parts). Pivot at ground centre of the bbox, min z = 0.
Anchors: STA-01 (handles with hex bolt plates), STA-03 (rounded handle sweep), STA-05 palette.

| ID | Item | Tris | Budget | Size X×Y×Z m | Notes |
|---|---|---|---|---|---|
| TOL-01 | Cheese mold | 1052 | 150–400 (×2.6) | 0.352×0.240×0.162 | 12 facets, 2 rows of through-holes (20 holes; ±X facets left plain for the handle plates), grey loop handles |
| TOL-02 | Curd harp | 436 | 120–350 (×1.25) | 0.240×0.570×0.056 | lying flat, 4 wires with end blocks, red ferrule + bolt, bulb grip |
| TOL-03 | Slotted paddle | 176 | 80–200 | 0.120×0.650×0.041 | lying flat, 3 through-slots, red collar |
| TOL-04 | Curd colander | 1504 | 200–500 (×3.0) | 0.354×0.266×0.147 | 2 hole rows on the wall + 7 bottom holes, grey rim band, flared foot, red octagon-section handles on bolted plates |
| TOL-05 | Ladle | 304 | 120–300 | 0.116×0.430×0.201 | bowl resting upright, handle rising at 25° from a bolted bracket |

Deviations:
- Orientation: the catalogue lists the long tools as height (Y) 0.55/0.65/0.45 m. They are modelled lying on a table (long axis = depth), as the references show them; rotate 90° in Unity to hang them on a rack.
- Budgets: the perforated items exceed the budget, because the holes are real geometry (≈32 tris per through-hole) — the refs' signature feature. A cheaper variant is possible (fewer holes / blind holes) if the pack needs it.
- Holes are hexagons (refs show rounder holes); mold has 2 rows instead of 3.

Compare rounds: 2 + final gate (economy mode, props). Round 1 → 2 fixes: colander deepened (rows read on the outer wall), darker hole interior cell, bigger mold holes and thicker handles, thicker harp wires/grip, cheaper harp blocks (436 from 564), spatula supports (blade tip + grip end on the ground).
Remaining differences (nitpicks): mold handles rise more steeply than the ref's; harp grip less bulbous; ladle bowl slightly shallower; colander rim band a bit wider than the ref.
Checks (all items): non-manifold 0, loose 0, degenerate 0, mirrorX 0, no gaps, min z 0; FBX re-import 2 nodes, same tris/dims, texture found. QA: SHIP WITH NOTES (budgets on TOL-01/04/02). Unity import not verified.

## Batch 2 (2026-11-14): TOL-11..15, same script

| ID | Item | Tris | Budget | Size X×Y×Z m | Notes |
|---|---|---|---|---|---|
| TOL-11 | Cheese knife | 312 | 80–200 (×1.6) | 0.072×0.300×0.048 | lying; spade blade with 3 octagonal through-holes (`flat_plate`), blade runs into the bolster, grip with red rivet |
| TOL-12 | Ceramic bowl | 348 | 150–350 | 0.328×0.328×0.128 | 16-gon `shell`, thick flat rim, red stripe band, grey foot |
| TOL-13 | Bread peel | 256 | 120–300 | 0.300×1.400×0.055 | lying; cream head, broad wooden shoulder (explicit rings, width only), bolted strap, red ring, dark knob |
| TOL-14 | Rolling pin | 324 | 100–250 (×1.3) | 0.080×0.504×0.080 | lying on its 8-gon body; grey end bands, red washers, bulb handles |
| TOL-15 | Smoking hook | 348 | 80–180 (×1.9) | 0.066×0.030×0.165 | upright S-hook (min z = 0; the hang point is the eye's inner top at z≈0.145), closed octagon eye (`path_sweep(closed=True)`), red clamp + bolt |

Fixes in this batch: `rest_on_ground()` had the tilt sign reversed and split the tool into halves (wrong support when a middle part dips). It now lays the lower convex hull (YZ) edge under the bbox centre on the table. TOL-02 harp handle axis was raised 6.5 mm so the frame edge (not the ferrule) is the front support, and TOL-02/03 were re-exported. New helper `flat_plate()` (outline + through-holes).
Rounds: 2 + final gate. Round 1 → 2: knife blade wider, no visible tang, thicker grip; bowl stripe wider/higher; peel shoulder, strap, shaft.
Remaining nitpicks: knife blade has no edge bevel; hook tip is a flat cap; bowl floor/wall junction shows a faint shading seam at the back.
Checks all items: non-manifold/loose/degenerate 0, no gaps, min z 0, X-mirror exact (hook is asymmetric by design); FBX re-import 2 nodes, same tris/dims, texture found. QA: SHIP WITH NOTES (budgets TOL-11/14/15). Unity not verified.

## Batch 3 (2026-11-14): TOL-16..18 + PRD-01/02, same script

Duplicate check (plan §4): Farm Market has FMS_Food_Cheese_Wheel (whole red-wax wheel), Cheese_Block, Cheese_Slice. PRD-02 (wheel with a wedge removed, cream interior with eyes) and PRD-01 (fresh cheese in a perforated mold) are different process props, so both are kept and nothing was copied.

| ID | Item | Tris | Budget | Size X×Y×Z m | Notes |
|---|---|---|---|---|---|
| TOL-16 | Oven tongs | 424 | 150–350 (×1.2) | 0.140×0.496×0.043 | lying, closed; arms cross at a beige pivot boss + hex nut (one arm raised over the other at the pivot), flat jaws, grips with dark collar + red band. X is wider than the catalogue 0.08 because the handles splay as in the ref |
| TOL-17 | Honeycomb frame | 1436 | 250–700 (×2.05) | 0.400×0.046×0.273 | upright; frame with lugs + red caps, comb panel with 25 recessed flat-top hex cells on EACH face (`blind()`); own honey palette cells 10/12/15 |
| TOL-18 | Oil strainer funnel | 1448 | 200–500 (×2.9) | 0.350×0.294×0.370 | tripod (3 splayed legs, ring, red caps, stretchers), grey bowl with a V spout (rim verts pulled out at 180°), perforated filter disc (19 blind holes) with lip and 3 clamps, loop handle on a bolted plate |
| PRD-01 | Cheese in mold | 828 | 200–450 (×1.8) | 0.250×0.250×0.141 | grey 16-gon mold, 2 staggered rows of octagonal holes showing cheese behind (blind holes with cream bottoms), domed fresh cheese just above the rim |
| PRD-02 | Cut cheese wheel | 348 | 200–450 | 0.342×0.343×0.150 | red wax 12-gon wheel, chamfered edges, 66° wedge removed; cut faces cream with a thin red rind margin and recessed hex eyes |

New helpers: `blind()` (recess with its own bottom colour), `shell(..., phase, a0)` + 4-tuple holes for blind recesses, per-item palette overrides (`REG[...]['pal']`).
Rounds: 1 + final gate (round 1 was already close). Fixes: comb cells larger/thinner walls and bigger red caps; bigger filter holes; cheese dome raised to the rim.
Remaining nitpicks: comb has a plain wax margin under the top bar (ref has partial cells at the edges); strainer filter shows 19 holes vs about 40 in the ref; PRD-01 hole rows are sparser than the ref.
Checks: non-manifold/loose/degenerate 0, no gaps, min z 0; FBX re-import 2 nodes, same tris/dims, texture found. Mirror is not exact on TOL-16 (layered arms), TOL-18 (spout, handle) and PRD-02 (wedge), all by design. QA: SHIP WITH NOTES (budgets TOL-17/18, PRD-01). Unity not verified.

## Batch 4 (2026-11-14): PRD-18 + FUR-01..04, same script

Duplicate check: Market Honey_Jar is a lidded orange jar with a HONEY label → PRD-18 (open striped crock + dipper) kept. Market Table_Plank (X-leg plank table), Stall_Table_*, Shelves (slanted crate display) → FUR-01 (stone-top workbench), FUR-02 (bottling table with back rail), FUR-03 (straight 4-tier slatted rack) are distinct. Nothing copied.

| ID | Item | Tris | Budget | Size X×Y×Z m | Notes |
|---|---|---|---|---|---|
| PRD-18 | Honey crock + dipper | 512 | 250–550 | 0.230×0.230×0.231 | 12-gon crock, red belly band, rolled lip, honey surface; grooved dipper (5 discs) resting in the honey, handle on the back-right rim. Pivot = crock axis (bbox is offset by the dipper) |
| FUR-01 | Cheesemaker's workbench | 604 | 500–1000 | 1.600×0.700×0.900 | splayed legs, leg heads with red caps, aprons, lower slatted shelf, pale stone top with bevels (own palette cells 10/15) |
| FUR-02 | Bottling table | 556 | 450–900 | 1.370×0.608×1.060 | splayed legs, back heads rise into posts with a back board, raised frame rim around 3 pale planks on a dark bed, low stretchers, side diagonal braces |
| FUR-03 | Cheese aging shelf | 1224 | 600–1200 (×1.02) | 1.210×0.502×1.800 | 4 posts, 4 slatted shelves (7 slats each, front-back), rails, side diagonal braces, red caps on the front posts |
| FUR-04 | Herb drying rail | 428 | 180–400 (×1.07) | 1.120×0.176×0.300 | wall-mounted: 2 chamfered mounting boards, rail with end blocks + red caps, 6 octagonal pegs tilted up 10°. Pivot = wall plane (y = 0) bottom centre, the model extends to −Y |

New helpers: `box`, `plain_box`, `splay_leg`, `red_cap`.
Rounds: 1 + final gate. Fixes: FUR-02 frame rebuilt as a closed ring (8 open edges); FUR-04 pegs thicker/longer, mounting boards re-outlined with chamfered ends; FUR-01 bigger red caps; PRD-18 bigger dipper head.
Remaining nitpicks: FUR-01 stone top edges are regular (ref has slightly irregular edges); FUR-03 posts thinner than ref; PRD-18 dipper slightly smaller than ref.
Checks: non-manifold/loose/degenerate 0, no gaps, min z 0; FBX re-import 2 nodes, same tris/dims, texture found. QA: SHIP WITH NOTES. Unity not verified.

## Batch 5 (2026-11-14): FUR-05..09, same script

Duplicate check: Market Stall_Cart_Empty (big-wheel market cart), Farm Yard Well/Wheelbarrow → FUR-08 trolley and FUR-06 washstand are distinct. Nothing copied.
New: multi-part builds (`build()` accepts [(Part, pivot)], each part a direct child of the root, so the nested-child FBX bug doesn't apply), `basin_loft()` (open rectangular basin with flange and floor, set into a top with a through-hole).

| ID | Item | Tris | Budget | Size X×Y×Z m | Parts / notes |
|---|---|---|---|---|---|
| FUR-05 | Pantry jar shelf | 692 | 400–850 | 0.885×0.397×1.420 | 4 posts, 3 thick pale boards on dark rails, side braces, red caps, short grey back rail |
| FUR-06 | Washstand + pump | 840 | 700–1400 | 0.996×0.600×1.230 | `_Body` (splayed legs, red caps front+sides, top with the basin opening, cream enamel basin, grey pump barrel + spout) and `_Lever` (pivot on the pump pin, rotates about Y) |
| FUR-07 | Press stand | 580 | 300–650 | 0.841×0.841×0.505 | legs splayed in X and Y, tall corner heads, red caps, low stretchers on 4 sides, diagonal braces |
| FUR-08 | Workshop trolley | 1244 | 600–1200 (×1.04) | 0.889×0.487×0.929 | `_Body` (posts, 2 framed pale shelves, joints with red caps, angled push handle with grey bar on +X) and `_Wheel_FL/FR/BL/BR` (10-gon wheels, pivot on the axle, axis Y, flat face on the ground) |
| FUR-09 | Baker's worktable | 604 | 600–1200 | 1.600×0.800×0.912 | splayed legs, red leg heads, aprons, low stretchers, thick top with a grey stone flour trough inset on +X |

Rounds: 1 + final gate. Fixes: stretcher gaps on FUR-06/09 (side stretchers now reach the legs), pump pin gap, wheel ground contact (10-gon apothem), trolley joints → 12-tri boxes (1452 → 1244 tris), bigger wheels, thicker pump/lever.
Remaining nitpicks: FUR-06 basin hangs less below the top than the ref; FUR-09 top has no plank seams; FUR-08 wheels have hub bolts only on the outer faces.
Checks: non-manifold/loose/degenerate 0, no gaps, min z 0; FBX re-import: FUR-06 3 nodes, FUR-08 6 nodes, others 2; tris/dims match, texture found. QA: SHIP WITH NOTES. Unity not verified.

## Batch 6 (2026-11-14): FUR-10..12 + MOD-01/02, same script

Duplicate check: nothing similar in Market/Yard (Farm Nature GRD tiles are outdoor terrain, not workshop floors).

| ID | Item | Tris | Budget | Size X×Y×Z m | Notes |
|---|---|---|---|---|---|
| FUR-10 | Smoking rail | 468 | 300–650 | 1.310×0.440×1.500 | 2 chunky uprights on long feet with triangular braces front/back, red bands, beige octagonal bosses, grey bar (no hooks) |
| FUR-11 | Honey frame draining stand | 588 | 400–850 | 0.728×0.558×0.730 | A-frame ends, top bar with bolts, frame rails on posts, cream tray tilted 8° to the front with a grey tap + red lever, low stretchers |
| FUR-12 | Low processing pallet | 412 | 200–450 | 0.800×0.600×0.150 | 5 broad chamfered slats (front-back), 2 dark stringers with red caps, 4 short feet |
| MOD-01 | Wood floor 2×2 | 220 | 120–300 | 2.000×2.000×0.150 | dark slab + 10 staggered planks in 5 rows (light/dark alternating), top-chamfered boards (`plank4`) |
| MOD-02 | Stone floor 2×2 | 388 | 180–400 | 2.000×2.000×0.150 | grey base, chamfered border ring, 16 jittered flagstones (3 cream, 3 red accents) with joints |

FLOOR SNAP CONTRACT (MOD-01/02): bbox exactly x,y −1.000..+1.000, z 0.000..0.150; side faces vertical at ±1.000 (only the top edge is chamfered → tiles butt with a small V seam, no gap/overlap); pivot at the bottom centre. The floor top is at +0.150, so walls (MOD-03..05, base z = 0) are placed at height 0.15 on a floor tile. The build asserts it (`SNAP OK`).
Rounds: 1 + final gate. Fixes: FUR-10 chunkier uprights/feet/braces/bosses/bar; FUR-11 thicker legs, tap moved forward so it shows; MOD-01 bigger plank bevels.
Remaining nitpicks: MOD-02 stones are flat quads (the ref has more varied polygon shapes and pillow bevels); FUR-11 tray reads small under the rails.
Checks: non-manifold/loose/degenerate 0, no gaps, min z 0; FBX re-import 2 nodes, tris/dims match, texture found. QA: SHIP WITH NOTES. Unity not verified.

## Batch 7 (2026-11-14): MOD-06..12, same script — catalogue complete (72/72)

| ID | Item | Tris | Budget | Size X×Y×Z m | Snap / notes |
|---|---|---|---|---|---|
| MOD-06 | Support post | 28 | 100–250 (under) | 0.200×0.200×2.400 | centred on the grid point; grey stone foot + red band as in the ref; encloses the wall half-posts (wall contract) |
| MOD-07 | Canopy beam 2 m | 28 | 60–150 (under) | 2.000×0.200×0.200 | flat square ends at x = ±1.000 (butt-joins), chamfered long edges |
| MOD-08 | Flat canopy roof 2×2 | 300 | 200–450 | 2.000×2.000×0.180 | frame rails flush on the grid, corner blocks, 6 terracotta slats over a dark sheet |
| MOD-09 | Workshop door leaf | 400 | 200–450 | 0.972×0.153×1.998 | separate part `_Leaf`, pivot on the hinge axis (x +0.478, vertical); fits the MOD-05 opening (0.96 × 2.02: leaf x −0.47..+0.47, z 0.006..2.004). 4 planks, cream Z-batten with red caps, 2 strap hinges, D-handle |
| MOD-10 | Low partition 2 m | 348 | 200–450 | 2.000×0.260×1.100 | rails end flat at x = ±1.000 (butt-join), posts on stone feet, 5 planks with uneven tops |
| MOD-11 | Corner post | 180 | 80–200 | 0.200×0.200×2.400 | like MOD-06 plus 2 recessed grooves per face (3 closed solids, no degenerate bands) |
| MOD-12 | Window shelf | 204 | 150–350 | 1.500×0.400×0.380 | wall-mounted (back = y 0, front −Y), 2 bracket posts with red caps, knee braces along the wall |

Snap checks (`snapbox`) assert the exact bbox per module and print `SNAP OK`.
Deliberate deviation: the MOD-09 ref has an ARCHED frame + leaf; the leaf is rectangular to fit the existing MOD-05 doorway (which is rectangular). An arched variant would need an arched MOD-05.
MOD-06/07 are simpler than their catalogue budget minimum (the refs are plain blocks); tris are a ceiling, not a target.
Rounds: 1 + final gate. Fixes: MOD-11 degenerate faces (zero-height bands) → 3 stacked solids (572 → 180 tris); MOD-10 rail/plank gap; MOD-09 bigger handle/hinges; MOD-12 caps were hidden by the braces → braces turned along the wall as in the ref.
Checks: non-manifold/loose/degenerate 0, no gaps, SNAP OK; FBX re-import 2 nodes, tris/dims match, texture found. Unity not verified.
