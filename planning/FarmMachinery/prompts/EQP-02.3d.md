# EQP-02 GrainBin — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/EQP-02.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_GrainBin`. Unity axes: +Z forward, +Y up. Root origin on the ground at the centre of the footprint (the bin axis), rotation 0, scale 1. Stationary: no wheels, no hitch points. Door faces +Z (front); ladder on the +X side.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 6.0 × 6.0 × 7.2 | 3500 LOD0 | yes, LOD1 50 % per part via `make_lod1.py` | no | none |

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, bin axis |
| Wall | 24-sided cylinder, wall radius 2.90, Y 0.20 … 5.60; flat-shaded facets (the 24 facets are the corrugation read); 12 chunky vertical ribs (about 0.10 wide, 0.05 proud) spaced around, flat | 9 | static |
| Bands | 5 horizontal rings, each ~0.14 tall, 0.05 proud, evenly from Y 0.9 to 5.0; alternate slots 7 and 8 | 7, 8 | static |
| Base ring | heavy ring Y 0 … 0.20, radius 3.00 (overall Ø6.0), chamfered | 8 | static |
| Roof | low wide cone, eave radius 3.00 at Y 5.60 (overhang 0.10 with a single 0.04-0.08 chamfer), apex Y ~7.0 (cone rise ~1.4), 24 sides; top cap/vent knob up to Y 7.20 | 7 roof, 8 eave edge | static |
| Door_Frame | frame around the door at the base, ~0.9 wide × 1.8 tall, 0.08 deep, on the +Z side | 8 | static |
| Door | door panel in the frame, with a chunky handle block | 7, 8 | hinge on its left vertical edge, axis Y, at about (-0.45, 0, +2.92) in root space (origin on the hinge line); rest closed |
| Roof_Hatch | square hatch ~0.8 × 0.8 on the cone slope near the top, with a lid slab | 8, 9 | hinge axis X at the upper edge of the lid (about (0, 6.85, -0.5), on the slope); rest closed |
| Ladder | straight ladder: two rails (≥ 0.08) and 8-10 rungs (≥ 0.06) on the +X side from Y 0.2 to the eave ~5.6, brackets to the wall, short rail along the roof slope up to the hatch | 9 | static |
| Colliders | none in the model (prefab gets one simple BoxCollider ~6×7.2×6) | - | - |

Exact names: Door, Roof_Hatch (moving, origin on the hinge axis), plus LOD1 children `Door_LOD1`, `Roof_Hatch_LOD1` with zero offset.

## Anchor

Closest approved model: Farm Yard `FMS_Silo` for cylinder segmentation and metal bands `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Silo.png` (build script of the Farm Yard pack). Take the band/ladder/door grammar only. EQP-02 must NOT be mistaken for it (see CATALOG "Дубли").

## What NOT to do

- Do not make it tall and narrow or domed: width Ø6.0 vs height 7.2, low cone roof, grey galvanised, no blue.
- Do not copy the silo's proportions, dome or colours.
- No foundation slab, no pipes, hoses, chains, bolts, logos or lettering; nothing thinner than ~0.04 m (ladder rails ≥ 0.08).
- Ladder must touch the wall through brackets, no floating rungs; band rings are chamfered solid rings, no coplanar overlaps (≥ 1 mm offset).
- Do not use smooth shading; 24 segments for the wall (not 16, not 32).
- Do not exceed 3500 tris without a recorded note.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/EQP-02_GrainBin/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
