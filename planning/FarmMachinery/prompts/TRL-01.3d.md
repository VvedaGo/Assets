# TRL-01 Trailer_Tipper — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-01.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-01 · Прицеп-самосвал 2-осный (`Trailer_Tipper`) · prefab `FMS_Mach_Trailer_Tipper_Red` (single Red prefab per variant; Green/Blue atlases ship, buyer swaps).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.5×6.6×2.7 (drawbar included in 6.6) | 4000 (LOD0 incl. wheels and load) | yes, LOD1 50 % by parts via `Tools/blender/make_lod1.py` | yes | 2: Empty / Grain (Load_Grain on/off) |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward (drawbar end), +Y up.

## Parts

Approximate positions are given so the pieces fit; the reference image wins over them, deviations go to the builder notes.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Chassis (static, root child) | Steel frame: two chunky longitudinal rails (~0.18 m), 3 cross members, rail top at Y ~1.1; underside darker; 45° chamfer on outer edges | 7 metal, underside 8 | static |
| Drawbar | A-frame of two chunky bars (~0.14 m) converging at the front into one bar ending in a thick round eye (ring, outer Ø ~0.28 m, 8-12 segments), eye lowered so its centre is at Y 0.55 | 7 metal, ring 8 | static; point `Hitch_Front` at the eye centre |
| Hitch bracket (rear) | Chunky steel block with a vertical pin under the rear cross member | 8 metal dark | static; point `Hitch_Rear` at the pin |
| Bed | Box 2.4 m wide x ~4.6 m long, floor at Y ~1.2, side walls ~1.3 m high, front headboard up to Y 2.7; solid walls with 45° chamfer 0.04-0.08 m on top edges; 4-5 flat vertical stiffener ribs per side (0.08 m proud, no thinner than 0.08 m); floor visible from above, no interior detail | 5 body, floor and lower rails 6 | `Bed`: origin on the rear tipping axis (X axis, at the bed's rear lower edge, Y ~1.15, Z ~ -2.3). Rest = lowered. Do not animate |
| Tailgate | Wall panel closing the rear, same height as the side walls, with 2 chunky latch blocks | 5 body, latches 7 | `Tailgate`: origin on the upper hinge line (X axis, top rear edge of the bed). Child of `Bed` so it tips together with it |
| Hydraulic cylinder | One simple stick: 8-sided steel cylinder from chassis to the front underside of the bed, thickness >= 0.1 m; static in rest pose (cosmetic) | 7 metal | static child of chassis |
| Wheel_FL, Wheel_FR | Tandem front axle pair, Ø1.1 m (centre Y 0.55), width ~0.45 m; one object = tyre + rim; tyre 16 sides, 12-16 blocky lugs; rim 8-12 sides with hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, spin axis local X, rest rotation 0 |
| Wheel_RL, Wheel_RR | Tandem rear axle pair, same function and size as the front pair; axle spacing ~1.3 m centre-to-centre, whole group under the rear half | tyre 10, rim 3 / 4 inner | same |
| Mudguards | One flat block over each side pair of wheels (both axles), thickness >= 0.06 m, rubber-dark, fixed to the chassis, not to the wheels | 11 | static |
| Load_Grain | Heap of grain inside the bed: a flat-topped faceted mound (6-10 facets) with a peak towards the rear, filling the bed up to ~Y 2.1, ends 0.05 m inside the walls | 15 grain | child of `Bed`; OFF in Empty prefab, ON in Grain prefab; the Empty variant must still look finished |
| Reflectors, rear | 2 small flat blocks at rear corners | 14 orange | static |
| Hitch_Front | Empty, +Z forward, +Y up, at the eye of the drawbar, Y 0.55, X 0, at the front extremity | — | point |
| Hitch_Rear | Empty, +Z forward, +Y up, Y 0.55, X 0, at the rear extremity | — | point |

LOD: every moving part and every wheel gets a child `<Name>_LOD1` (Bed_LOD1, Tailgate_LOD1, Wheel_FL_LOD1 ...) at zero offset inside it; LODGroup is built on the root. Rotating `Wheel_FL` rotates LOD0 and LOD1.

Wheel geometry comes from the shared wheel function of the pack script (same tread for all machines); only Ø changes. Budget guide: wheels ~4 x 250 tris, bed + tailgate ~1500, chassis + drawbar ~800, grain heap ~100, rest for ribs and details. Lite: yes.

Colliders are set on the prefab later (BoxCollider on bed and chassis); do not model collision. No rig, no animation, no scripts.

## Anchor

Closest approved model: none for the trailer body. Style and chamfers: Farm Yard `FMS_Tractor` (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`). Silhouette must differ from Farm Yard `FMS_Wagon` (`.../FarmYard_Wagon.png`, wooden horse cart): steel box, rubber tyres, A-frame drawbar with an eye.

## What NOT to do

- No wooden planks, no spoked wheels, no shafts (oglobli): this is not `FMS_Wagon`.
- Do not model wheels separately from the machine or use another wheel function; wheel names exactly `Wheel_FL/FR/RL/RR`.
- No pivot of `Bed` at the bed centre; the tipping axis is the rear edge. Do not rotate `Bed` or `Tailgate` in the exported FBX (rest = closed).
- No grain baked into the Empty mesh; `Load_Grain` is a separate child object.
- No thin sheet-metal walls with zero thickness; walls >= 0.06 m, ribs >= 0.08 m wide.
- No floating hydraulic cylinder or reflectors; every part touches its support. No coplanar overlapping faces.
- No hoses, chains, bolts, logos, text.
- No smooth shading.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-01_Trailer_Tipper/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
