# ATT-01 QuickHitch — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/ATT-01.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

`ATT-01 | QuickHitch | — | 1.0×0.3×0.9 | 400 tris | no moving parts | LOD no | Lite yes | pilot no`
Prefab: `FMS_Mach_QuickHitch`. Sits between the tractor linkage and an implement.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.0 × 0.3 × 0.9 (X × Z × Y) | 400 | none (no LOD1) | yes | none |

## Parts

Root: origin at the ground level (Y = 0) below the centre of the part in X and Z, rotation (0,0,0), scale 1; forward = +Z, up = +Y. The model is one rigid mesh with no moving parts, no LOD and no wheels. Lower pins are at Y = 0.60 (standard Link3P height), so the frame hangs above the ground; the object is NOT meant to stand on the ground. The bounding box spans about Y 0.45 … 1.35 (0.9 m tall); the root stays on the ground per the pack contract.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| A-frame | Upright triangle: lower cross bar (≈ 1.0 m wide), two sloped side bars, narrow top, bars about 0.1 m square section, depth 0.3 m, one 45° chamfer on edges | 7 | rigid |
| Gusset | Flat triangular plate inside the frame, ≥ 0.05 m thick | 8 | rigid |
| Lower hook pins (left, right) | Two chunky horizontal cylinders, 6–8 segments, axis along X, sticking out sideways at Y = 0.60, with dark hook jaws around them | pins 9, jaws 8 | rigid |
| Top mast + catch | Chunky mast block at the top with a hook-shaped catch | 8 | rigid |
| `Link3P_Front` (empty) | Centre between the lower pins on the tractor side: meets the tractor `Link3P_Rear` | — | Y = 0.60, X = 0, Z ≈ +0.15 (front face); +Z forward, +Y up |
| `Link3P_Rear` (empty) | Centre between the rear lower hooks: meets the implement `Link3P_Front` | — | Y = 0.60, X = 0, Z ≈ −0.15 (rear face); +Z forward, +Y up |

Mating note: the quick hitch mounts to the tractor via its `Link3P_Front` (to the tractor's `Link3P_Rear`), and the implement mounts to its `Link3P_Rear`. The two empties are 0.3 m apart in Z in the model; the Э10 assembly must position the implement by the quick hitch's `Link3P_Rear`, not by the tractor's.

## Anchor

None in this pack for rigid linkage frames. Use the lower-link pin / hook look of TRC-01 `Linkage_Rear` once approved. Style: Farm Yard `FMS_Tractor` preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png` (chamfer and metal tone only).

## Palette slots

Metal 7 (frame), metal dark 8 (jaws, catch, gusset), metal light 9 (pins). No body red, no tyre. One material (the Red atlas; Green and Blue atlases are shipped with the pack but this part is metal only).

## LOD / Lite

No LOD (400 tris, not worth it). Lite: yes (part of CMP-03 yard).

## What NOT to do

- Do not deviate from CATALOG "Игровая готовность" item 6: lower-link pins 0.90 m apart (X = ±0.45) at Y 0.60; Link3P/PTO/Hitch offsets as listed there.

- No wheels, no legs, no stand, no ground plate: it is an attachment, not a standing object.
- Do not make thin bars; every bar ≥ 0.1 m (or ≥ 0.04 m thickness for plates).
- No hydraulic hoses, no chains, no bolts, no pins with cotter detail.
- Do not make the frame wider than 1.0 m or deeper than 0.3 m.
- Keep both Link3P empties at exactly Y = 0.60; do not fold them into mesh.
- No coplanar overlapping faces; pins pass through jaws with a ≥ 1 mm offset, not coplanar.
- Do not exceed ~400 tris; no cylinders above 8 segments.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/ATT-01_QuickHitch/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
