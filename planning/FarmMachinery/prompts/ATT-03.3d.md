# ATT-03 Header_Grain — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/ATT-03.png  <!-- accepted by orchestrator 2026-11-24 -->

Pilot item, built and fitted together with HRV-01 (Combine) in one pilot round. Prefab `FMS_Mach_Header_Grain` (Red; Green/Blue atlases ship). Unity axes: +Z forward, +Y up. Root origin on the ground at the centre of the footprint (X 0, Z 0), rotation 0, scale 1; the cutter bar sits ~0.10 m above Y = 0.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 6.2 × 2.1 × 1.5 (Z from -1.05 to +1.05) | 5000 LOD0 | yes, LOD1 50 % per part via `make_lod1.py` | no | none (single Red prefab) |

## Feeder interface (must match HRV-01 exactly)

| Item | Value |
|---|---|
| Feeder_Rear | empty, +Z forward, +Y up; position in root space: X 0, Y 0.80, Z -1.05 |
| Interface rectangle | rear frame 1.60 m wide (X) × 0.90 m high (Y), centred on Feeder_Rear (spans Y 0.35 … 1.25, X ±0.80); vertical plane at Z = -1.05; 0.10 m thick chamfered frame around an open throat |
| Fitting | header root = combine Feeder_Front + (0, -0.80, +1.05); the two frames touch face to face, same rectangle, no gap, no overlap (≥ 1 mm offset only where faces would be coplanar and overlapping) |

Same numbers are in HRV-01.3d.md and ATT-04.3d.md.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Frame / platform | chunky platform 6.2 wide, sloped floor from the cutter bar (front, Y ~0.15) up to the auger trough; tall rear wall to Y ~1.25; end walls as wedges; main edges chamfered 0.04-0.08 | 5, 6 sides and underside | static |
| Cutter bar | full-width bar along the front edge, Z +0.80 … +1.05, Y 0.10 … 0.35, flat finger points as blocky wedges | 8 (dark edge), 7 | static |
| Auger_Cross | 8-sided cylinder Ø ~0.55 across the whole width (X ±3.0) in the trough, ring flights as chunky rings (slot 8) every ~0.4; centre section open toward the throat | 7, 8 | axis X at (0, 0.70, -0.45), local rotation about X |
| Throat | open 1.60 × 0.90 rectangular frame in the rear wall (see interface) | 5, 8 inside | static |
| Feeder_Rear | empty, no mesh | - | position per interface table |
| Reel_Arm | two chunky arms (each ~0.10 × 0.20) at X ≈ ±3.0, rising and going forward from the rear hinge to the reel axle, plus a central cross brace linking them (one object, both arms) | 5, 6 | hinge axis X at (0, 1.25, -0.70); rest = lowered working position shown; may rotate about X to lift |
| Reel | 8 bars (slot 7) 8-sided or flat chunky bars Ø/size ≥ 0.06, mounted on 2 end discs of 8 segments, axle through the centre; Ø 1.10 (radius 0.55), width ~5.7 | 7 bars, 8 discs/axle | child of Reel_Arm; own origin on its axle at (0, 0.95, +0.45), rotation about local X; top of reel Y ~1.50 |
| Dividers | pointed crop dividers at both ends (wedge to Z +1.05), orange tips | 5, 14 | static |
| Warning stripes | orange chunky stripes on the end walls and divider tips | 14 | static |
| Colliders | none in the model (prefab gets one BoxCollider on the platform) | - | - |

Exact names: Reel_Arm (contains Reel), Auger_Cross, Feeder_Rear. LOD1 of Reel_Arm, Reel and Auger_Cross are children named `Reel_Arm_LOD1`, `Reel_LOD1`, `Auger_Cross_LOD1` with zero offset inside their parents.

## Anchor

Closest approved model: Farm Yard, `FMS_Tractor` (chamfers, series red); preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`. Level of detail and chamfer only. Companion item: HRV-01 (same pilot round).

## What NOT to do

- Do not change the throat rectangle, Feeder_Rear position or header depth: they are tied to HRV-01 and ATT-04.
- No cutter-bar teeth thinner than 0.04 m, no reel tines as thin wires: reel bars are chunky (≥ 0.06 m).
- Do not attach wheels or a trailer axle: transport is TRL-04.
- No decals, brand logos, lettering; no wheat/crop geometry.
- Do not merge Reel, Reel_Arm and Auger_Cross into the body mesh: separate objects with pivots on their axes.
- No floating reel: the arms and axle really touch the reel discs; no coplanar overlaps (≥ 1 mm offset).
- Do not exceed 5000 tris without a recorded note; flat shading only.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/ATT-03_Header_Grain/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
