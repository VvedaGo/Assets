# TRL-03 Trailer_Tank — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-03.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-03 · Прицеп-цистерна (`Trailer_Tank`) · prefab `FMS_Mach_Trailer_Tank_Red` (Red only; Green/Blue atlases ship).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.5×6.0×2.8 (drawbar included in 6.0) | 3500 (LOD0 incl. wheels) | yes, LOD1 50 % by parts via `make_lod1.py` | yes | none |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward, +Y up.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Tank | Horizontal cylinder along Z, 16 segments, outer Ø ~1.9 m, length ~4.4 m (axis at Y ~1.75, top ~2.7), chamfered/domed end caps (single 45° chamfer 0.06-0.08 m); upper facets slot 5, lower facets slot 6; 2 chunky bands (~0.12 m wide, 0.05 m proud) in metal | 5 / 6, bands 7 | static |
| Chassis | Two chunky longitudinal rails (~0.18 m) with cross members and 2 cradle saddles carrying the tank, rail top at Y ~0.85-0.9; wide enough that the wheels sit outside | 7, underside 8 | static |
| Drawbar | A-frame of two chunky bars (~0.14 m) converging into one bar ending in a thick round eye (outer Ø ~0.28 m, 8-12 segments) at Y 0.55 | 7 metal, ring 8 | static; `Hitch_Front` at the eye centre |
| Hatch | Short wide 12-16-sided cylinder (~0.6 m Ø, 0.15 m high) with a flat lid and a hinge block on its rear side, on the top of the tank near the middle; plus a small flat catwalk strip beside it | 9 galvanised | `Hatch`: origin on the hinge line (X axis, rear edge of the hatch lid at the tank top). Rest = closed |
| Ladder | Chunky vertical ladder on the left rear of the tank: 2 side rails >= 0.06 m and 4 rungs >= 0.05 m, from Y ~0.6 to the tank top, standing off the tank by ~0.1 m on 2 bracket blocks | 9 | static |
| Outlet tap | Short thick pipe (6-8 sided, Ø ~0.2 m) with a valve block at the rear-lower end of the tank | 7 metal, handle 8 | static; no hose |
| Wheel_FL, Wheel_FR | Tandem front pair, Ø1.1 m (centre Y 0.55), width ~0.45 m; tyre 16 sides + 12-16 blocky lugs; rim 8-12 sides + hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, axis local X, rest rotation 0 |
| Wheel_RL, Wheel_RR | Tandem rear pair, same function and size; axle spacing ~1.3 m under the rear half | same | same |
| Mudguards | Flat block over each side wheel pair, thickness >= 0.06 m, fixed to chassis | 11 | static |
| Reflectors, rear | 2 small blocks | 14 | static |
| Hitch_Front | Empty, +Z forward, +Y up, eye centre, Y 0.55, X 0, front extremity | — | point |

Only `Hitch_Front` exists on this trailer (no `Hitch_Rear` in the catalogue; do not add one). Wheels use the shared wheel function of the pack script. LOD: every wheel and `Hatch` get `<Name>_LOD1` children at zero offset; LODGroup on root. Budget guide: tank 16 segments ~450 incl. caps and bands, wheels 4 x 250, chassis ~500, hatch ~100, ladder ~150, rest for details. Lite: yes.

No rig, no animation, no scripts, no collider modelling.

## Anchor

Closest approved model: Farm Yard `FMS_Silo` for cylinder segmentation and metal bands (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Silo.png`); chamfer style from `FMS_Tractor` (`.../FarmYard_Tractor.png`).

## What NOT to do

- No smooth cylinder shading; 16 clearly visible flat facets.
- No hoses, pipes running along the tank, sprayer booms, pump details or valves smaller than ~0.04 m.
- No ladder rungs thinner than ~0.05 m, no floating ladder; it must touch brackets.
- Do not make the tank ride on top of the wheels or intersect them; wheels outside the chassis, tank clear of the tyres.
- `Hatch` pivot on the hinge line, not at the centre of the lid; rest = closed.
- Wheel names exactly `Wheel_FL/FR/RL/RR`; no `Hitch_Rear`.
- No text, logos or hazard decals; no smooth shading; no coplanar overlapping faces between bands and tank (offset >= 1 mm or share edges).

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-03_Trailer_Tank/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
