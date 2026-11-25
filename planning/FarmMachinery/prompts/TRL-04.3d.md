# TRL-04 Trailer_Header — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-04.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-04 · Тележка для жатки (`Trailer_Header`) · prefab `FMS_Mach_Trailer_Header_Red` (Red only; Green/Blue atlases ship). Carries the 6 m header ATT-03 lying lengthwise; towed from `Hitch_Rear` of a combine or tractor.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.2×7.2×1.1 (drawbar included in 7.2) | 2000 (LOD0 incl. wheels) | no (no LOD1; no LODGroup) | no | none |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward, +Y up.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Chassis | Two chunky longitudinal rails (~0.16 m) with 5-6 cross members, rail top at Y ~0.6; outer faces red, underside dark | rails 5 / 6, cross members and underside 7 / 8 | static |
| Deck | Flat open deck ~2.0 m x ~5.6 m at Y ~0.65: broad cross bars (~0.2 m wide, gaps >= 0.06 m) in metal with dark gaps visible; or one plate with 2 dark stripes | 7 metal, gaps 11 | static |
| Cradle supports | 3 saddle blocks along the deck (front, middle, rear), each = red stand + dark rubber-top slab (slot 11), top at Y ~0.95; a 2-sided V profile is allowed; spaced to carry a 6.2 m header lying along Z | 5 stand, 11 pad | static |
| Side guide rails | 2 low rails along the outer deck edges (top Y ~1.1), >= 0.08 m thick, ends chamfered; they reach 1.1 m height | 5 / 6 | static |
| Drawbar | Long A-frame of two chunky bars (~0.14 m) converging into one bar ending in a thick round eye (outer Ø ~0.28 m, 8-12 segments) at Y 0.55 | 7 metal, ring 8 | static; `Hitch_Front` at eye centre |
| Wheel_FL, Wheel_FR | Front axle pair, Ø0.7 m (centre Y 0.35), width ~0.3 m; tyre 16 sides + 12-16 blocky lugs; rim 8-12 sides + hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, axis local X, rest rotation 0 |
| Wheel_RL, Wheel_RR | Rear axle pair, same function and size | same | same |
| Mudguards | Flat block over each wheel, thickness >= 0.05 m, fixed to chassis | 11 | static |
| Reflectors, rear | 2 small blocks at rear corners | 14 | static |
| Hitch_Front | Empty, +Z forward, +Y up, eye centre, Y 0.55, X 0, front extremity | — | point |
| Header_Rest | Empty, +Z forward, +Y up: where the root of ATT-03 is placed; on the deck centreline (X 0) at the deck/saddle top height (Y ~0.95), Z at the centre of the saddle span. Exact position: builder fixes it so the header lies on all 3 saddles, and writes the value to the builder notes | — | point |

No `Hitch_Rear` is listed for this item in the catalogue; do not add one. Wheels use the shared wheel function of the pack script (smaller Ø0.7). No moving parts besides wheels. Budget guide: wheels 4 x ~200, chassis ~500, deck ~300, saddles ~200, rails ~150, drawbar ~200. Lite: no.

No rig, no animation, no scripts, no collider modelling.

## Anchor

Closest approved model: none. Style and chamfers: Farm Yard `FMS_Tractor` (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`). Not `FMS_Wagon`; no wood.

## What NOT to do

- Do not model the header on the trailer; `Header_Rest` is just a point.
- No LOD1 objects, no LODGroup (catalogue LOD «нет»).
- No tall walls; the trailer stays at 1.1 m height maximum.
- No spoked wheels, no thin wheels; wheel names exactly `Wheel_FL/FR/RL/RR`.
- No floating saddles or rails; they sit on the chassis.
- No hoses, chains, bolts, logos, text; no smooth shading; no coplanar overlapping faces.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-04_Trailer_Header/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
