# PRP-01 Windrow — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/PRP-01.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_Windrow`. Unity axes: +Z along the row, +Y up. Root origin on the ground (Y = 0) at the centre of the module (X 0, Z 0), rotation 0, scale 1. Module of the pack: exactly 4.000 m long along Z, ends at Z = ±2.000, identical end cross-sections; the pack script checks `SNAP OK` (end profiles equal when modules are placed at 4 m pitch).

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.4 × 4.0 × 0.4 | 300 LOD0 | no | no | none |

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Windrow (one mesh, one object) | extruded cross-section along Z: flat bottom at Y = 0 width 1.40 (X ±0.70), side walls rising with a chamfer to a shoulder at about Y 0.25 (X ±0.45), ridge top at Y 0.40 (X ±0.20); 6-8 profile vertices per section; sections at Z = -2.0, -1.0, 0, +1.0, +2.0 with the ridge height/offset varied by a few cm (max ±0.04) in the middle sections only (lumps); sections at Z = ±2.0 are EXACTLY the same profile (no lump, same vertices); closed end caps flat in the planes Z = ±2.0 | 15 | none (static prop) |

No moving parts, no points, no colliders in the model.

## Anchor

Closest approved model: none in this pack. For straw colour and level of detail: Farm Yard series straw (palette slot 15 = ART-02 straw); style bar `FMS_Tractor` for faceted chamfered flat shading `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`.

## What NOT to do

- No stalks, tufts, blades or noise displacement; no thin spikes.
- Length is exactly 4.000 m; origin is the module centre on the ground; end cross-sections identical at both ends (SNAP OK); do not taper the ends.
- No ground plane or soil piece under it; no hidden base slab: flat bottom only (do not sink below Y = 0).
- Only palette slot 15; no second material or colour.
- Do not exceed 300 tris; flat shading; no coplanar overlaps.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/PRP-01_Windrow/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
