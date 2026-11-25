# TRL-02 Trailer_Flatbed — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-02.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-02 · Прицеп-платформа 2-осный (`Trailer_Flatbed`) · prefab `FMS_Mach_Trailer_Flatbed_Red` (Red only; Green/Blue atlases ship).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.5×6.6×1.7 (drawbar included in 6.6) | 2500 (LOD0 incl. wheels) | yes, LOD1 50 % by parts via `make_lod1.py` | yes | none |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward, +Y up.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Chassis (static) | Two chunky longitudinal rails (~0.18 m), 3-4 cross members, top at Y ~0.85; outer faces of the rails body red, underside dark | rails 5 / 6, cross members and underside 7 / 8 | static |
| Deck | Flat wooden deck 2.4 m x ~5.0 m, top at Y ~0.95, ~0.08 m thick; 8-10 broad planks along Z, alternating slots 0 and 2, gaps 1 (0.02 m deep real gaps or dark strips, not thinner than 0.04 m wide); plank ends slot 1; steel edge strip around it | 0 / 2 planks, 1 gaps, 7 edge strip | static |
| Headboard | Low solid panel at the front of the deck, width = deck, height ~0.6 m above deck (top Y ~1.55-1.7), thickness >= 0.08 m, 45° chamfer on the top edge, 2 chunky vertical stiffeners | 5 body, edge 6 | static |
| Drawbar | A-frame of two chunky bars (~0.14 m) converging into one bar ending in a thick round eye (outer Ø ~0.28 m, 8-12 segments) at Y 0.55 | 7 metal, ring 8 | static; `Hitch_Front` at eye centre |
| Hitch bracket (rear) | Chunky steel block with vertical pin at the rear end of the chassis | 8 | `Hitch_Rear` at the pin |
| Wheel_FL, Wheel_FR | Tandem front pair, Ø1.0 m (centre Y 0.5), width ~0.4 m; tyre 16 sides + 12-16 blocky lugs; rim 8-12 sides + hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, axis local X, rest rotation 0 |
| Wheel_RL, Wheel_RR | Tandem rear pair, same function and size; axle spacing ~1.3 m, group under the rear half | same | same |
| Mudguards | Flat block over each side pair of wheels, thickness >= 0.06 m, fixed to the chassis | 11 | static |
| Reflectors, rear | 2 small blocks at rear corners | 14 | static |
| Hitch_Front | Empty, +Z forward, +Y up, eye centre, Y 0.55, X 0, front extremity | — | point |
| Hitch_Rear | Empty, +Z forward, +Y up, Y 0.55, X 0, rear extremity | — | point |

Wheels use the shared wheel function of the pack script (same tread everywhere), only Ø differs. No moving parts besides the wheels. LOD: wheel and any other part get `<Name>_LOD1` children at zero offset; LODGroup on root. Budget guide: wheels 4 x ~230, deck ~500, chassis ~500, drawbar ~200, headboard ~150, mudguards ~100. Lite: yes.

No rig, no animation, no scripts, no collider modelling.

## Anchor

Closest approved model: none for the platform. Style and chamfers: Farm Yard `FMS_Tractor` (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`). Wood tone only: Farm Yard `FMS_Wagon` (`.../FarmYard_Wagon.png`), but our trailer must read as a different machine (steel frame, tandem rubber tyres, drawbar with eye, no spoked wheels, no wooden side boards, no shafts).

## What NOT to do

- No wooden side walls or stakes along the deck; only the low front headboard.
- No spoked wheels, no thin wheels; no wheels inside the deck outline in a way that makes them vanish (they stay outside the frame, readable in side view).
- Do not make the deck a single flat box without plank breaks; the gaps must read at 128 px.
- No sagging or non-flat deck; deck is level in rest.
- No hoses, chains, bolts, logos, text; no smooth shading.
- Wheel names exactly `Wheel_FL/FR/RL/RR`; no second hitch variant.
- No coplanar overlapping faces between planks and edge strip.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-02_Trailer_Flatbed/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
