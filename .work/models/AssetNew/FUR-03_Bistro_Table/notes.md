# FUR-03 Wrought-iron bistro table `FMS_Garden_Bistro_Table` (+ `_White`) — builder notes (Э7, series batch 3, 2026-11-25)

Source of truth: `build.py` (`-- FUR-03 build|export|verify|dump`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in collection `FUR-03_Bistro_Table` with the child
`FUR-03_Bistro_Table_White` (left in place); the owner's file was not saved, the default Cube and the other collections were
not touched; selection (Cube, active Cube) restored after the live export.

## Result

| | |
|---|---|
| FBX | `art/AssetNew/Meshes/FMS_Garden_Bistro_Table.fbx`, `art/AssetNew/Meshes/FMS_Garden_Bistro_Table_White.fbx` (each + `.fbm` with the atlas copy) |
| Blend / preview | `art/AssetNew/Blend/FMS_Garden_Bistro_Table.blend` (both collections only); ONE preview `art/AssetNew/Previews/FMS_Garden_FUR_03_Preview.png` (base) |
| Tris | **1000 / 1000** per model (budget raised 500 → 1000 by the coordinator, see "Budget"). Top + underside ring 140 · Hub 20 · Legs 3 × 152 = 456 · Hub scrolls 3 × 128 = 384 |
| Size (Blender X×Y×Z) | 0.700 × 0.700 × 0.750 m (x ±0.350, y ±0.350, z 0 … 0.750) |
| Nodes | root empty `FMS_Garden_Bistro_Table` + mesh `_Body` (same for `_White`) |
| Material | `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette pixel check 0 mismatches). Base: slot 13 wrought iron only; `_White`: slot 10 only, identical vertices |
| LOD | none (catalogue) |

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint on the ground; rot 0, scale 1; FBX Y up, −Z forward baked. Static, no moving parts.
- Blender X = right, −Y = front (Unity +Z), Z = up (Unity Y). Symmetric in X (mirror 0.000000).
- Legs at azimuths 90° (back, +Y), 210° and 330° (front left / right); the top has a flat facing the front.

## Checks (live and headless identical, both variants)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 (every component touches another), mirror X 0.000000.
- Coplanar overlapping face pairs 0.
- Ground contact: each foot curl rests on the ground with a bottom edge at z 0.0000 (2 verts per foot, radius 0.279);
  nothing below 0. Foot footprint x ±0.305, y −0.182 … +0.346: inside the 0.70 × 0.70 top.
- Curls: foot curl 0.126 across, hub-scroll curls 0.102 (bottom) / 0.105 (top), all ≥ 0.10; self-clearance of the
  centre-lines: leg 0.048 ≥ bar 0.036, scroll 0.043 ≥ bar 0.030 → no self-touch.
- SNAP: no module contract for this item (free-standing furniture). SIZE OK: 0.700 / 0.700 / 0.750.
- FBX re-import (both): 2 nodes (root + Body), 1000 tris, dims 0.7 / 0.7 / 0.75, min z 0, texture found in `.fbm`.
- Headless `build.py -- FUR-03 export` geometry SHA1 == live SHA1 `eac43892b37ef28d12dfb14da681c0c63631b6d9`
  (2 meshes × 516 verts / 538 faces).

## Build (what is where) — helpers for FUR-04
- Top + underside ring: one 12-sided solid of revolution (flat to the front): recessed field z 0.737, rim 0.030 wide up
  to 0.750, slab edge 0.70–0.75, frustum ring 0.46 → 0.42 across the flats, z 0.66–0.70.
- Hub: 6-sided prism 0.12 across the flats, z 0.40–0.46, flats facing the legs.
- Legs (`foot_leg()`): 6-sided rod 0.036 across the flats; Hermite from inside the hub (u 0.03, z 0.415, tangent out-down)
  to a vertical drop at r 0.238, 4 segments; then an outward foot curl (CCW spiral, R 0.055 → 0.42 R over 300°,
  8 segments) whose lowest edge is moved exactly onto z 0.
- Hub scrolls (`s_scroll()`, same wording as STR-02 `s_curve()`): 6-sided bar 0.030; bottom curl (CCW, R 0.045 → 0.45 R,
  290°, 4 segments) sunk 4 mm into the hub top, straight spine leaning 0.02 outward, top curl (CW, 5 segments) sunk
  4 mm into the underside ring; innermost centre-line at r 0.025 so the three scrolls never touch each other.
- Shared helpers documented at the top of `build.py`: `oct_sec(a, n)`, `plane_pt`, `plane_normal`, `rod_rings`, `hermite`,
  `foot_leg`, `s_scroll`, `s_clearance`. FUR-04 can import or copy them (same rod sizes, slot 13 / 10).

## Budget (coordinator decision 2026-11-25: option C)
Spec said ≤ 500. Measured prototypes: all bars 8-sided as STR-02 = 1488; 8-sided legs + 6-sided scroll bars ≈ 1140–1308;
≤ 500 only with 4-sided rods and 3-segment curls (square hooks). Coordinator chose **option C: all iron rods 6-sided,
cap 1000 (2.0×, the STR-02 ratio)**, recorded in CATALOG.md by the coordinator (FUR-03 500 → 1000; FUR-04 700 → 1400).
Final: exactly 1000. Segment split favours what is visible: foot curls 8 segments (round at 128 px), top scroll curls 5,
bottom scroll curls 4 (in the hub's shadow), straight scroll spine.

## Deviations from `prompts/FUR-03.3d.md` (for the reviewer / spec owner)
1. **Rods 6-sided (spec 8-sided)**: coordinator option C for the budget. Legs 0.036 across the flats, scroll bars 0.030
   (STR-02 scroll bars); ≥ 0.03 kept.
2. **Hub lower and hex: z 0.40–0.46, 6-sided 0.12 (spec 8-sided Ø0.10, z 0.58–0.68)**. The reference hub sits at about
   0.41–0.46 m (measured: 0.94 mm/px, top ellipse 0.30 → camera ~17° above), which gives the tall scroll zone of the
   reference (0.46 → 0.66). Hex saves 8 tris and lines its flats up with the three legs.
3. **Scrolls stand above the legs (same azimuths), not between them**: the reference shows the side scrolls over the side
   legs and the middle scroll over the back leg.
4. **Rim lip 0.013 high (field 0.737, rim top 0.750; spec rim 0.03 high on top of a 0.04 disc)**: the spec numbers add up
   to 0.77; total height 0.75 is the functional size, and the reference lip is low. Slab 0.70–0.75, underside ring a
   frustum 0.46 → 0.42 (spec Ø0.40 straight), as in the reference.
5. **Legs reach the ground at r 0.279 (spec ≈ 0.28) with the curl outward to r 0.346**, so the feet stay inside the 0.70
   top (back foot y +0.346).

## Rounds
- Headless prototypes (2): first pass (8-sided, 1248 tris, small square foot hooks, back foot outside the top); then
  rounder/larger curls, lower hub, scroll curls 6 segments → measured the budget options, asked the coordinator.
- Live round 1 (option C, 972 tris): worst: foot curls read as square hooks at 128 px (6 segments / 290°).
- Live round 2: foot curl R 0.055, 300°, 8 segments (round at 128 px); scroll curls 4 + 4 to pay for it. Worst: top
  scroll curls boxy (72° steps).
- Live round 3: top scroll curls 5 segments, hub 8 → 6 sides (1000 tris). Reference angle, 3/4, side, 128 px thumbnail and
  `_White` checked. Export live + headless.
- Rounds used: 3 of 5 live.

## Remaining differences vs the reference (nitpicks)
- Reference hub scrolls are more ornate (tighter, rounder curls, ≈ 10 facets per turn); ours 4–5 segments per 290° —
  budget. The bottom scroll curls meet near the axis and read as one cluster above the hub from the front.
- The reference back leg shows an S and a side-on foot curl from the front (the AI image is not consistent); ours is seen
  edge-on as a straight rod from the exact front view (it reads correctly in the 3/4 preview).
- Rods are 6-sided (faceting visible in close-ups), the reference looks rounder.
- Iron is the palette slot 13 `#3A3A3F`, very close to the reference; `_White` is the cool palette white (palette decision).
