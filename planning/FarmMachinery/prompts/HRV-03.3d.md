# HRV-03 ForageHarvester — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/HRV-03.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_ForageHarvester_<Red|Green|Blue>`. Unity axes: +Z forward, +Y up. Root origin on the ground at the centre of the footprint, rotation 0, scale 1.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.5 × 8.0 × 4.0 (Z from -4.0 to +4.0) | 11000 LOD0 incl. 4 wheels and built-in pickup | yes, LOD1 50 % per part via `make_lod1.py` | no | 3: Red / Green / Blue by material swap (atlas), same mesh and UV |

## Parts

Wheels: ONE shared pack wheel function (same tread as all machines): 16-segment chamfered tyre (slot 10) with 12-16 large blocky tread lugs (slot 10), cream rim (slot 3) with 8-12 segment hub and inner face (slot 4); one object per wheel (tyre + rim), origin at wheel centre, axis local X, rest rotation 0; rear wheels steer about Y of the same pivot. LOD1 as child `<Name>_LOD1` with zero offset.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Wheel_FL | Ø1.8, tyre width ~0.75, centre (-1.375, 0.90, +0.90) | 10 / 3 / 4 | centre, axis X |
| Wheel_FR | same, centre (+1.375, 0.90, +0.90) | 10 / 3 / 4 | centre, axis X |
| Wheel_RL | Ø1.2, width ~0.55, centre (-1.20, 0.60, -2.60) | 10 / 3 / 4 | centre, axis X (steer about Y) |
| Wheel_RR | same, centre (+1.20, 0.60, -2.60) | 10 / 3 / 4 | centre, axis X |
| Chassis / body | chunky chopper body Z -4.0 … +2.4, Y 0.8 … 2.4, width ~2.6; chamfers 0.04-0.08; dark underside and skirts | 5, 6, 11 | static |
| Cab | closed four-post glazed cab, raised at the front, floor Y ~2.3, roof Y ~3.6, Z +0.6 … +2.4, width ~1.7; flat opaque glass, mirror block, headlights (slot 13), beacon (slot 14) | 5, 12, 3, 13, 14 | static |
| Door_L | left cab door with glass | 5, 12 | hinge at its front vertical edge, axis Y; rest closed |
| Header | built-in pickup header ~3.3 wide, Z +2.2 … +4.0, Y 0.15 … 1.3: steel pickup drum Ø ~0.6 with chunky tine bars, red guard hood, feed intake behind it; built into the model (not swappable) | 5, 6, 7, 8 | hinge axis X at the rear, (0, 1.00, +2.30); rest = lowered |
| Engine compartment | boxy hood at the rear Z -4.0 … -0.2, Y 1.2 … 2.9, grille (slot 8), exhaust pipe 6-8 seg (slot 11) | 5, 6, 8, 11 | static |
| Spout | tall thick curved silage chute: round base hub Ø ~0.9 at the rear of the cab roof, neck rising to Y ~3.85, arching backwards over the engine to Z ~ -3.0; built from 3-4 chunky 8-sided segments (≥ 0.5 wide); steel rim bands | 5, 6, 7 | base at (0, 2.90, -0.60), axis Y (swings left/right) |
| Spout_Tip | short hood flap at the end of the spout pointing slightly down; top of the silhouette ~Y 4.0; child empty Spout_Out | 5, 7 | hinge axis X at the spout end, about (0, 3.65, -3.00); child of Spout |
| Spout_Out | empty at the discharge opening, about (0, 3.40, -3.60); +Z forward | - | child of Spout_Tip |
| Seat | empty in the cab at about (0, 2.65, +1.45); a dark seat block (slot 11) allowed | 11 | static |
| Lights | 2 front headlights, 2 rear lights | 13 | static |
| Colliders | none in the model (prefab gets BoxColliders on body and cab, no wheels) | - | - |

There are no Hitch_*/PTO_* points on this machine (not in the catalogue). Exact names: Wheel_FL/FR/RL/RR, Header, Spout, Spout_Tip, Spout_Out, Door_L, Seat.

## Palette

Body colour slots 5 / 6 are the only ones swapped between atlases (Red #C8473B / #A8372E; Green #6E9F4A / #557D39; Blue #4A78A8 / #3A5F86); all other slots identical. One material.

## Anchor

Closest approved model: Farm Yard `FMS_Tractor` (chamfers, tyre lugs, series red) `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`. Companion: HRV-01 for cab, wheels and hitch/auger wording. Level of detail only, not the silhouette.

## What NOT to do

- The tall curved spout is the silhouette feature: do not shrink it to a stub or a flat panel.
- No second header or interchangeable header interface; the pickup is built in (no Feeder_* points).
- Do not model cab interior, hoses, chains, drive shafts, bolts, logos, brand colours.
- Do not fuse wheels into the body; tyres on Y = 0; named separate wheel objects with correct pivots.
- Spout pivots on the axes given (base Y, tip X); no tubes thinner than ~0.04 m, no floating segments, no coplanar overlaps (≥ 1 mm offset).
- Do not exceed 11000 tris without a recorded note; flat shading only.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/HRV-03_ForageHarvester/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Fix 1 (2026-11-24, owner decision: detachable header)
- What is wrong: the pickup `Header` is built into the model; the owner wants swappable headers like HRV-01.
- What to do: remove `Header` from HRV-03 (it becomes ATT-05 Header_Pickup). Add a `Feeder` part (inclined feed channel at the front, rear hinge axis X) with child empty `Feeder_Front` using EXACTLY the HRV-01 interface: opening 1.60 × 0.90 m, Feeder_Front at Y 0.80, +Z forward, so ATT-03, ATT-04 and ATT-05 all mount with Feeder_Rear onto it. Keep cab, spout, wheels, body, Spout_Out, Seat, Door_L unchanged; the overall length without header may shrink (catalogue: size given without adapter). Preview: HRV-03 without header, like HRV-01's preview.
