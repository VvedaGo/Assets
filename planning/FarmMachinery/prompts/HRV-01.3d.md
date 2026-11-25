# HRV-01 Combine — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/HRV-01.png  <!-- accepted by orchestrator 2026-11-24 -->

Pilot item, built together with ATT-03 (Header_Grain) in one pilot round. Prefab name `FMS_Mach_Combine_<Red|Green|Blue>`. Axes in this spec are Unity axes (+Z forward, +Y up, X to the right of the driver); the builder converts for Blender per the skill. Origin of the root: on the ground, centre of the footprint in X and Z, rotation 0, scale 1.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.6 × 8.4 × 4.0 (machine only, no header; Z from -4.2 to +4.2) | 12000 LOD0 incl. 4 wheels, excl. header (ATT-03 has its own 5000) | yes, LOD1 50 % per part via `make_lod1.py` | no | 3: Red / Green / Blue by material swap (atlas), same mesh, same UV |

## Feeder interface (must match ATT-03 exactly)

| Item | Value |
|---|---|
| Feeder_Front | empty child of `Feeder`, local +Z forward, +Y up; position in root space at rest: X 0, Y 0.80, Z +4.20 |
| Interface rectangle | 1.60 m wide (X) × 0.90 m high (Y), centred on Feeder_Front, so spans Y 0.35 … 1.25 and X ±0.80; a vertical plane (perpendicular to Z) |
| Front face of Feeder | the open throat of the feeder housing: a 1.60 × 0.90 rectangular frame, 0.10 m thick walls, flat vertical front face at Z = +4.20 |
| Header side | ATT-03 `Feeder_Rear` is the centre of its identical 1.60 × 0.90 rear frame. Prefab: header root placed at Feeder_Front + (0, -0.80, +1.05) so frames touch face to face (no overlap, no gap) |
| Pivot of Feeder | hinge axis X at (0, 2.00, +1.60); Feeder_Front rotates with it. Rest pose = header at working height (cutter bar ~0.10 m above ground) |

Any change to these numbers must be made in ATT-03.3d.md and ATT-04.3d.md at the same time.

## Parts

Wheels: ONE shared wheel function of the pack script builds all of them (same tread everywhere): 16-segment chamfered tyre (slot 10) with 12-16 large blocky tread lugs (slot 10), cream rim (slot 3) with 8-12 segment hub and inner face (slot 4). One object per wheel = tyre + rim, origin at the wheel centre, rotation axis local X, rest rotation (0,0,0). Steering wheels rotate about Y of the same pivot. LOD1 is a child `<Name>_LOD1` with zero offset.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Wheel_FL | drive wheel Ø1.8, tyre width ~0.9, centre (-1.35, 0.90, +1.20); fender-free so the tyre reads fully | 10 / 3 / 4 | centre of wheel, axis X |
| Wheel_FR | same, centre (+1.35, 0.90, +1.20) | 10 / 3 / 4 | centre, axis X |
| Wheel_RL | steering wheel Ø1.1, width ~0.5, centre (-1.00, 0.55, -3.00) | 10 / 3 / 4 | centre, axis X (steer about Y) |
| Wheel_RR | same, centre (+1.00, 0.55, -3.00) | 10 / 3 / 4 | centre, axis X |
| Chassis / body | boxy threshing body Z -1.6 … +2.4, Y 0.9 … 2.3, width ~2.6, chamfer 0.04-0.08 on main edges; dark lower skirts and side faces | 5, 6 (lower/sides), 11 (underside) | static |
| Grain tank | boxy tank above the body, Z -1.6 … +1.4, Y 2.3 … 3.4, width ~2.8, sloped cover, hatch lids | 5 top, 6 sides | static |
| Engine compartment | box at the rear Z -4.0 … -1.6, Y 1.0 … 2.9, grille block (slot 8), exhaust pipe 6-8 seg (slot 11) on the right | 5, 6, 8, 11 | static |
| Cab | closed four-post cab, floor Y 2.10, roof Y 3.60, Z +1.50 … +3.05, width ~1.7; posts + roof chamfered, flat glass panels (opaque, one material), cream stripe on roof edge, mirror block, headlights (slot 13), roof beacon (slot 14) reaching ~Y 3.9-4.0 | 5, 12, 3, 13, 14 | static |
| Door_L | left cab door panel with glass | 5, 12 | hinge at its front vertical edge, axis Y, about (-0.86, door mid-height, +2.85); rest closed |
| Feeder | inclined feeder housing, 1.60 wide, from the body front down to the interface frame; front face cut vertical at Z +4.20 (see interface table); chunky 0.10 walls | 5, 6, 8 inside edges | hinge axis X at (0, 2.00, +1.60); child Feeder_Front |
| Feeder_Front | empty, no mesh | - | see interface table, child of Feeder |
| Auger_Unload | tube 8 sides Ø~0.45 plus short vertical riser/hub at its base; folded pose lies along the left top edge of the tank pointing forward (+Z), about 3.6 long, tip beside the cab at Z ~ +2.2, Y ~3.6; discharge spout at the tip pointing down; child empty Auger_Out at the tip | 7 tube, 8 flights end, 14 stripe | pivot at the base, axis Y, about (-1.25, 3.45, -1.40); unfolds by about -90° so the tip points to -X (left); rest = folded |
| Auger_Out | empty, at the tube tip discharge opening, folded about (-1.25, 3.35, +2.20) | - | child of Auger_Unload, +Z forward |
| Hitch_Rear | empty at the rear centre, X 0, **Y 0.55**, Z -4.20; plus a simple steel clevis plate (fork) with pin hole as geometry | 7 | static; +Z forward, +Y up |
| Seat | empty in the cab at about (0, 2.45, +2.25); a dark seat block (slot 11) may be modelled | 11 | static |
| Lights | 2 front headlights on the cab roof/front, 2 rear lights | 13 | static |
| Colliders | none in the model (prefab gets simple BoxColliders on body, no wheels) | - | - |

All Wheel_*, Feeder, Feeder_Front, Auger_Unload, Auger_Out, Door_L, Hitch_Rear, Seat names are exact (Unity prefab and the pack check rely on them).

## Palette

Body colour slots 5 / 6 are the only ones swapped between the Red, Green and Blue atlases (Red #C8473B / #A8372E; Green #6E9F4A / #557D39; Blue #4A78A8 / #3A5F86). Everything else stays in slots 3, 4, 7, 8, 10-14 and must not be recoloured per variant. One material per model.

## Anchor

Closest approved model: Farm Yard, `FMS_Tractor` (chamfers on the hood, tyre lugs, series red); preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`. Use it for the level of detail and chamfer width, not for the silhouette. The combine must not look like the open `FMS_Tractor`.

## What NOT to do

- Do not make the cab a low box: it must be tall, glazed, at the front above the feeder, the highest mass at the front.
- Do not model cab interior, hoses, chains, drive shafts, bolts, decals, logos or brand colour/lettering.
- Do not bake the header into the combine mesh: it is a separate nested prefab (ATT-03) on Feeder_Front. The combine mesh ends at Z +4.20.
- Do not change the interface rectangle (1.60 × 0.90 at Y 0.80) or the Feeder hinge without changing ATT-03 and ATT-04.
- Do not put the unloading auger in a unfolded pose in the FBX; rest = folded. No thin tubes below ~0.04 m.
- Do not fuse wheels into the body or into one mesh: they are named, separate, with correct pivots. No floating wheel gaps: the tyre sits on Y = 0.
- No coplanar overlapping faces; touching parts share edges or are offset by at least 1 mm.
- Do not exceed 12000 tris without a recorded note (soft cap); do not use smooth shading.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/HRV-01_Combine/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
