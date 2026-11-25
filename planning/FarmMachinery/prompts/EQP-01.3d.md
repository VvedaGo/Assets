# EQP-01 GrainAuger — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/EQP-01.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_GrainAuger`. Unity axes: +Z forward (towing direction), +Y up. Root origin on the ground at the centre of the footprint, rotation 0, scale 1. The tube angle is fixed; no moving parts.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.6 × 10.5 × 5.0 (Z from -5.25 to +5.25) | 3000 LOD0 incl. 2 wheels | yes, LOD1 50 % per part via `make_lod1.py` | no | none |

## Parts

Wheels: ONE shared pack wheel function (same tread as all machines): 16-segment chamfered tyre (slot 10) with 12-16 large blocky lugs, cream rim (slot 3) with 8-12 segment hub and inner face (slot 4); one object per wheel, origin at wheel centre, axis local X, rest rotation 0. LOD1 as child `<Name>_LOD1` with zero offset.

Layout: the low end with the hopper and the drawbar is at the FRONT (+Z, towed by a tractor), the tube rises toward the REAR (-Z) and ends high at Z ≈ -5.0. Numbers are guides; the reference wins within the bounding box.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Wheel_L | Ø0.7, tyre width ~0.30, centre (-0.65, 0.35, -0.80) | 10 / 3 / 4 | centre, axis X |
| Wheel_R | same, centre (+0.65, 0.35, -0.80) | 10 / 3 / 4 | centre, axis X |
| Tube | straight inclined 8-sided tube Ø ~0.50, centre line from about (0, 0.75, +3.60) to (0, 4.55, -4.85) (about 26° incline); 3-4 darker joint bands (slot 8); chunky end flanges | 7, 8 | static, rigid |
| Discharge hood | short hood at the top end, angled down, with orange warning stripes; top of silhouette Y ≈ 5.0 | 7, 14 | static |
| Hopper | wide receiving funnel at the low end, Z +2.8 … +4.4, Y 0.50 … 1.30, width ≤ 1.6, open top, sloped chamfered sides | 5, 6 | static |
| Frame | red A-frame truss under the tube: two legs from the axle up to the tube, a diagonal brace toward the hopper; members ≥ 0.10 m thick; axle beam Ø 8-sided between the wheels | 5, 6, 7 | static |
| Drawbar | steel drawbar from the hopper frame to Z +5.25 with a flat eye hitch plate (round hole) and a small support foot under it | 7, 8 | static |
| Hitch_Front | empty at the drawbar tip, X 0, **Y 0.55**, Z +5.25; +Z forward, +Y up | - | static |
| Auger_Out | empty at the discharge hood opening, about (0, 4.15, -5.15); +Z forward | - | static |
| Colliders | none in the model (prefab gets a BoxCollider on the frame and tube, no wheels) | - | - |

Exact names: Wheel_L, Wheel_R, Hitch_Front, Auger_Out.

## Anchor

Closest approved model: Farm Yard `FMS_Silo` for cylinder segmentation and metal bands `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Silo.png`; Farm Yard `FMS_Tractor` for red, chamfers and tyre lugs. Hitch wording shared with the trailers of this pack.

## What NOT to do

- Do not make the tube spindly: Ø ≥ 0.5 m, 8 sides, support members ≥ 0.10 m. No spiral flights visible through a net or open lattice.
- Do not bend or animate the tube; fixed angle, rigid.
- No wheels bigger than Ø0.7; no extra axle; no hoses, chains, motors, bolts, logos.
- No floating tube ends: the hood, flanges and frame really touch; the tube is supported by the frame, not hanging.
- No coplanar overlaps (≥ 1 mm offset); do not fuse wheels into the frame mesh.
- Do not exceed 3000 tris without a recorded note (truss may go up to 2× with a note); flat shading only.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/EQP-01_GrainAuger/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
