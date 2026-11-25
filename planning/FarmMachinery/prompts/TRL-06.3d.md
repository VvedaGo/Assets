# TRL-06 Trailer_Bale — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-06.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-06 · Прицеп для тюков (`Trailer_Bale`) · prefab `FMS_Mach_Trailer_Bale_Red` (Red only; Green/Blue atlases ship). Always empty: no bales in this pack or its demos (owner decision).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.5×9.0×2.3 (drawbar included in 9.0) | 3000 (LOD0 incl. wheels); lattice panels may overrun up to ~2× if recorded in the builder notes | yes, LOD1 50 % by parts via `make_lod1.py` | no | none |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward, +Y up.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Chassis | Two chunky longitudinal rails (~0.18 m), 4-5 cross members, rail top at Y ~0.8; outer faces red, underside dark | rails 5 / 6, cross members and underside 7 / 8 | static |
| Deck | Flat wooden deck 2.4 m x ~7.2 m, top at Y ~0.9; 8-10 broad planks along Z (slots 0 and 2 alternating), gaps slot 1 (>= 0.04 m wide), steel edge strip around it | 0 / 2, gaps 1, edge 7 | static |
| Lattice panel, front | Stout frame ~2.4 m wide, rising from the deck to Y 2.3; frame bars >= 0.1 m; 3 horizontal + 5 vertical bars (>= 0.08 m) forming large open squares; 45° chamfers on the frame; bolted to the chassis by 2 chunky posts | 5 frame, 6 posts, bars 7 | static |
| Lattice panel, rear | Same as front, mirrored, same height | same | static |
| Drawbar | A-frame of two chunky bars (~0.14 m) converging into one bar ending in a thick round eye (outer Ø ~0.28 m, 8-12 segments) at Y 0.55 | 7 metal, ring 8 | static; `Hitch_Front` at eye centre |
| Hitch bracket (rear) | Chunky steel block with vertical pin under the rear cross member | 8 | static; `Hitch_Rear` at the pin |
| Wheel_FL, Wheel_FR | Front axle pair, Ø0.9 m (centre Y 0.45), width ~0.4 m; tyre 16 sides + 12-16 blocky lugs; rim 8-12 sides + hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, axis local X, rest rotation 0 |
| Wheel_RL, Wheel_RR | Rear axle pair, same function and size; axle spacing ~3.5 m or as the reference shows (front axle in the front third, rear axle in the rear third) | same | same |
| Mudguards | Flat block over each wheel, thickness >= 0.06 m, fixed to chassis | 11 | static |
| Reflectors, rear | 2 small blocks at rear corners | 14 | static |
| Hitch_Front | Empty, +Z forward, +Y up, eye centre, Y 0.55, X 0, front extremity | — | point |
| Hitch_Rear | Empty, +Z forward, +Y up, Y 0.55, X 0, rear extremity | — | point |

Wheels use the shared wheel function of the pack script; only Ø differs. No moving parts besides wheels. LOD: every wheel gets `<Name>_LOD1` at zero offset; LODGroup on root. Budget guide: wheels 4 x ~230, deck ~500, chassis ~600, lattice panels ~900, drawbar ~200. Lite: no.

No rig, no animation, no scripts, no collider modelling, no bales or load objects.

## Anchor

Closest approved model: none for this trailer. Style and chamfers: Farm Yard `FMS_Tractor` (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`). Must differ from Farm Yard `FMS_Wagon_HayLoad` (wooden cart with hay): long 9 m platform, steel chassis, rubber tyres, lattice panels, no built-in hay. Wood tone only: `FMS_Wagon` (`.../FarmYard_Wagon.png`).

## What NOT to do

- No bales, hay, straw or any load; the model is empty.
- No wooden side boards or stakes along the deck; lattice panels at front and rear only.
- No bars thinner than ~0.08 m in the lattice (thin sticks are rejected); grid squares large and open.
- No spoked wheels; wheel names exactly `Wheel_FL/FR/RL/RR`.
- Do not make it tandem-close: the two axles are widely spaced along the 9 m platform.
- No floating lattice or posts; they stand on the chassis. No coplanar overlapping faces between deck planks and edge strip.
- No hoses, chains, bolts, logos, text; no smooth shading.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-06_Trailer_Bale/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
