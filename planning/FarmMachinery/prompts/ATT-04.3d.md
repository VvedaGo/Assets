# ATT-04 Header_Corn — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/ATT-04.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_Header_Corn` (Red). Interchangeable header of HRV-01: shares the Feeder interface with ATT-03. Unity axes: +Z forward, +Y up. Root origin on the ground at the centre of the footprint, rotation 0, scale 1.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 5.6 × 2.6 × 1.3 (Z from -1.30 to +1.30) | 4500 LOD0 | yes, LOD1 50 % per part via `make_lod1.py` | no | none |

## Feeder interface (same as ATT-03 and HRV-01)

| Item | Value |
|---|---|
| Feeder_Rear | empty, +Z forward, +Y up; position in root space: X 0, Y 0.80, Z -1.30 (rear face of the header) |
| Interface rectangle | rear frame 1.60 m wide × 0.90 m high centred on Feeder_Rear (Y 0.35 … 1.25, X ±0.80), vertical plane at Z = -1.30, 0.10 m thick chamfered frame around an open throat |
| Fitting | header root = combine Feeder_Front + (0, -0.80, +1.30); frames touch face to face |

The 0.90 m height keeps the frame inside the 1.3 m header height. Changing the interface requires changing HRV-01 and ATT-03 too.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Frame / platform | chunky platform 5.6 wide, floor sloping from the front (Y ~0.20) up to the cross auger trough; tall rear wall to Y ~1.25; end walls ±2.8 solid, chamfered 0.04-0.08 | 5, 6 | static |
| Snout_1 … Snout_7 (merged into one mesh) | 7 pointed snout hoods, pitch 0.80 m at X = -2.4, -1.6, -0.8, 0, +0.8, +1.6, +2.4; each hood ~0.45 m wide at the rear, tapering to a blunt tip at Z +1.30, tip height ~0.20 m, rising to ~1.0 m at the platform; 4-sided pyramid-like chunky block (not thin cones) | 5 top, 6 sides, 14 front 0.20 m tip | static |
| Row channels | 6 channels of ~0.35 m between snouts; gathering strip bar (slot 8) and a chunky stalk-roll cylinder 6-8 seg (slot 7, Ø ≥ 0.10) in each | 8, 7 | static |
| Cross auger trough | 8-sided cylinder Ø ~0.55 across X ±2.4 at Y ~0.75, Z ~ -0.70, chunky ring flights | 7, 8 | static (rigid header, no moving parts) |
| Throat | open 1.60 × 0.90 frame in the rear wall | 5, 8 | static |
| Feeder_Rear | empty, no mesh | - | position per interface table |
| End walls / warning | orange stripes on both end walls | 14 | static |
| Colliders | none in the model (prefab gets one BoxCollider) | - | - |

No moving parts, only the empty `Feeder_Rear`.

## Anchor

Closest approved model: companion ATT-03 (same pack, pilot) for the frame, throat and cutter-platform wording; Farm Yard `FMS_Tractor` for chamfers (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`).

## What NOT to do

- Exactly 7 snouts and 6 equal row channels; not 6 snouts, not uneven spacing.
- Snouts are chunky wedge/pyramid hoods, not thin spikes or needles; no part thinner than ~0.04 m.
- Do not model corn plants, chains, hoses, bolts, logos.
- Do not change Feeder_Rear position or the 1.60 × 0.90 throat.
- No wheels or support legs: transport is TRL-04.
- No coplanar overlaps (≥ 1 mm offset), no floating hoods; flat shading; do not exceed 4500 tris without a recorded note.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/ATT-04_Header_Corn/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
