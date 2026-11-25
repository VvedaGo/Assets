# ATT-02 FrontWeight — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/ATT-02.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

`ATT-02 | FrontWeight | — | 0.9×0.6×0.8 | 600 tris | no moving parts | LOD no | Lite yes | pilot no`
Prefab: `FMS_Mach_FrontWeight`. Mounts on the front linkage of TRC-02.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.9 × 0.6 × 0.8 (X × Z × Y) | 600 | none (no LOD1) | yes | none (Red; Green / Blue atlases shipped) |

## Parts

Root: origin at ground level (Y = 0) below the centre of the part in X and Z, rotation (0,0,0), scale 1; forward = +Z, up = +Y. One rigid mesh, no moving parts. The block hangs on the tractor front linkage: its bracket is at Y = 0.60 and the bounding box spans about Y 0.20 … 1.00; the model does not stand on the ground.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Weight block | Heavy chunky block, ≈ 0.9 wide × 0.45 deep × 0.8 tall, 45° chamfer on top and front edges (0.04–0.08 m), two shallow horizontal ribs on the front face | 5 top / front, 6 sides / lower faces | rigid |
| Mounting bracket | Rear side of the block: two thick horizontal steel arms and a vertical post with a flat plate, about 0.15 m deep, total depth stays ≤ 0.6 m | 7 | rigid |
| Pin blocks | Two short chunky pin blocks at the lower corners of the bracket at Y = 0.60 (X ≈ ±0.35) | 8 | rigid |
| `Link3P_Rear` (empty) | Centre between the two pin blocks, at the rear face of the bracket: meets TRC-02 `Link3P_Front` | — | Y = 0.60, X = 0, Z ≈ −0.30 (rear face); +Z forward, +Y up |

Because the block faces forward and the tractor is behind it, the rear face (−Z) is the mounting side.

## Anchor

None directly. Closest: TRC-02 front linkage once approved; style anchor Farm Yard `FMS_Tractor` preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png` (red, chamfer width, flat shading).

## Palette slots

Body 5 / 6 (red; Green and Blue atlases shipped, applied by the buyer), metal 7, metal dark 8. One material.

## LOD / Lite

No LOD. Lite: yes (part of CMP-03). Not a pilot item.

## What NOT to do

- Do not deviate from CATALOG "Игровая готовность" item 6: lower-link pins 0.90 m apart (X = ±0.45) at Y 0.60; Link3P/PTO/Hitch offsets as listed there.

- No wheels, no stand, no ground plate; it is not a standing object.
- No weight-plate stack, no hooks, no chains, no handles, no bolts, no inscriptions like "kg".
- No thin parts; bracket arms ≥ 0.08 m.
- Do not exceed 0.9 × 0.6 × 0.8 m; `Link3P_Rear` must be exactly at Y = 0.60 and X = 0.
- Do not add a `Link3P_Front`: this item mounts on the tractor only; nothing mounts on it.
- No coplanar overlapping faces; keep within ~600 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/ATT-02_FrontWeight/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
