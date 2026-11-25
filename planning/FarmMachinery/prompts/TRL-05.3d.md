# TRL-05 GrainCart — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRL-05.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Line: TRL-05 · Бункер-перегрузчик (`GrainCart`) · prefab `FMS_Mach_GrainCart_Red` (Red only; Green/Blue atlases ship), variants Empty / Full.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.6×6.8×3.6 (width across the wheels, drawbar included in 6.8, auger folded) | 5000 (LOD0 incl. wheels and load) | yes, LOD1 50 % by parts via `make_lod1.py` | no | 2: Empty / Full (Load_Grain on/off) |

Root origin: on the ground (Y = 0), centre of the bounding box in X and Z, rotation 0, scale 1; +Z forward, +Y up.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Hopper | Trapezoid body: top opening ~2.9 m wide x ~3.8 m long at Y ~3.0; narrower bottom (~1.4 m wide); steep front wall, sloped sides and rear; wall thickness >= 0.06 m; 45° chamfer 0.04-0.08 m on the rim; upper faces slot 5, lower faces 6; empty floor visible from above; 2 chunky steel rim bars on the top edge | 5 / 6, rim bars 7 | static |
| Chassis | Heavy steel frame under the hopper with one thick axle beam (~0.2 m) between the wheels; hopper rests on it | 7 / 8 | static |
| Drawbar | Short steel tongue (~0.18 m bars) from the hopper front forward, ending in a thick round eye (outer Ø ~0.3 m, 8-12 segments) at Y 0.55; a small gearbox block (~0.3 m) on the drawbar as the PTO stub, no shaft; a short chunky support foot (leg ~0.12 m) under the tongue | 7 / 8, gearbox 11 | static; `Hitch_Front` at eye, `PTO_Front` at the stub end |
| Wheel_L, Wheel_R | Big single-axle pair, Ø1.8 m (centre Y 0.9), width ~0.6 m; tyre 16 sides + 12-16 blocky lugs; rim 8-12 sides + hub | tyre 10, rim 3 / 4 inner | origin at wheel centre, axis local X, rest rotation 0; outer faces at X ±1.8 |
| Mudguards | Half-round (flat-faceted) guard above each wheel, thickness >= 0.06 m, fixed to the chassis | 11 | static |
| Auger_Unload | Inclined 8-sided steel tube Ø ~0.45 m with a chunky base housing and a spout housing with a downward chute at the top; length ~4 m; in rest (folded) it lies across the front wall from the front-left corner base up to above the front-right corner, top reaching Y 3.6 | 7 metal, base and spout 8 | origin at the base at the front corner (left front, Y axis through the base). Rotates about Y: rest = folded along the front wall, unfolded = swung outward to the side. Rest pose only is exported |
| Auger_Out | Empty at the auger tip, at the spout outlet, pointing down | — | child of `Auger_Unload` |
| Load_Grain | Heap in the hopper: a flat-topped faceted mound filling the hopper to ~0.15 m below the rim (6-10 facets), 0.05 m inside the walls | 15 grain | child of the hopper; OFF in Empty, ON in Full |
| Reflectors, rear | 2 small blocks at rear corners | 14 | static |
| Hitch_Front | Empty, +Z forward, +Y up, eye centre, Y 0.55, X 0, front extremity | — | point |
| PTO_Front | Empty, +Z forward, +Y up, X 0, Y 0.70, Z = Hitch_Front Z + 0.15 (CATALOG contract item 6; the empty may sit ahead of the eye) | — | point |

LOD: every wheel and `Auger_Unload` get a `<Name>_LOD1` child at zero offset; LODGroup on root. Budget guide: wheels 2 x ~300, hopper ~700, chassis ~400, auger ~500, drawbar ~300, grain heap ~100. Lite: no.

No rig, no animation, no scripts, no collider modelling. The support foot is a builder detail so the single-axle cart stands upright; keep it chunky (>= 0.1 m) and out of the way.

## Anchor

Closest approved model: none for the cart. Style and chamfers: Farm Yard `FMS_Tractor` (`C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`); cylinder segmentation: `FMS_Silo` (`.../FarmYard_Silo.png`).

## What NOT to do

- No driveshaft (карданные валы не моделируются); the PTO stub is a block only.
- No hoses; no flat rectangular open box: the hopper must read as a trapezoid.
- Do not put the wheels inside the hopper; they sit outside the sloped sides and may not intersect the hopper.
- No thin auger tube (>= 0.4 m Ø); no pole fan or icosphere ends.
- `Auger_Unload` pivot at the front-corner base (vertical axis), not the centre of the tube.
- Wheel names exactly `Wheel_L` / `Wheel_R`.
- No grain baked into the Empty mesh; `Load_Grain` is a separate child.
- No text, logos; no smooth shading; no coplanar overlapping faces.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRL-05_GrainCart/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
