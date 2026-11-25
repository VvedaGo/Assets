# TRC-02 Tractor_Large — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRC-02.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

`TRC-02 | Tractor_Large | 3 variants Red / Green / Blue (atlas swap) | 2.9×5.8×3.5 | 9000 tris | pilot: no | LOD yes | Lite yes`
Prefab names: `FMS_Mach_Tractor_Large_Red`, `_Green`, `_Blue` (one mesh/FBX, material swap only). The preview is Red.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.9 × 5.8 × 3.5 (X × Z × Y) | 9000 (LOD0, incl. wheels) | LOD1 50 % per part via `Tools/blender/make_lod1.py` | yes | Red / Green / Blue |

Suggested tris split (soft): 4 wheels ≈ 2600 (≈ 650 each), cab ≈ 1300, bonnet + grille + lights ≈ 1000, mudguards ≈ 900, chassis + steps + tank ≈ 600, front and rear linkage + hitch + PTO ≈ 1200, seat + mirrors + beacon + exhaust ≈ 400. Keep total ≤ 9000.

## Parts

Root: origin on the ground (Y = 0) at the centre of the footprint in X and Z, rotation (0,0,0), scale 1. Forward = +Z, up = +Y. The catalogue fixes diameters and overall extents only; wheel X/Z positions below are suggestions inside 2.9 × 5.8 m.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| `Wheel_FL`, `Wheel_FR` | Shared wheel function (see wheel rules), tyre Ø1.9 m, width ≈ 0.65 m. Centre Y = 0.95. X ≈ ±1.12 (outer edge ≈ 1.45), Z ≈ +1.75 | tyre + lugs 10, rim disc 3, inner 4, hub 7 / 8 | origin at wheel centre, axis local X, rest rotation (0,0,0); steer around local Y of the same pivot |
| `Wheel_RL`, `Wheel_RR` | Same, Ø1.9 m, width ≈ 0.65 m. Centre Y = 0.95. X ≈ ±1.12, Z ≈ −1.55 | same | origin at wheel centre, axis local X |
| Bonnet | Long broad bonnet over the front axle, single 45° chamfer on the top edge, grille block at the front | 5 top, 6 sides / lower | rigid |
| Grille + headlights | Grille block with chunky vertical bars, two headlight blocks at the corners | grille 11, lights 13 | rigid |
| Mudguards | Arches over all four wheels, ≥ 0.05 m clear of tyres, on the body | 5, inside 6, flaps 11 | rigid |
| Cab | Boxy four-pillar cab in the middle of the machine, flat roof with chamfer, flat opaque glass panels all round, cream stripe, side mirror blocks, top height 3.5 m (includes beacon) | pillars / roof 5 (6), glass 12, stripe 3, mirrors 11 | rigid; no interior |
| `Door_L` | Left cab door as separate object, glass in a frame, handle block | frame 5, glass 12 | origin on the hinge axis (front edge), hinge axis Y; rest = closed |
| Beacon | Small cylinder on the roof | 14 | rigid |
| Exhaust | Cylinder 6–8 segments beside the cab on the bonnet | 7 | rigid |
| Chassis + steps + tank | Dark chassis between axles, step plate under the door, fuel tank block | 11, tank 6 | rigid |
| `Linkage_Rear` | Two lower lift arms (bars ≥ 0.08 m), top link, simple lift struts | 7, 8 | origin on the lower-link pin axis, local X, at Y = 0.60; rest = lowered |
| `Link3P_Rear` (empty, child of `Linkage_Rear`) | Centre between the rear lower-link pins, Z ≈ −2.75 | — | Y = 0.60 at rest; lifts with the linkage |
| `Linkage_Front` | Front three-point frame: two short lower arms, top link, mounting frame at the nose | 7, 8 | origin on the pin axis, local X, at Y = 0.60; rest = lowered |
| `Link3P_Front` (empty, child of `Linkage_Front`) | Centre between the front lower-link pins, Z ≈ +2.75 | — | Y = 0.60 at rest; the weight `ATT-02` mounts here (its `Link3P_Rear` meets this point) |
| Drawbar fork | Chunky tow-hitch fork plate with pin hole under the rear deck | 7 / 8 | rigid |
| `Hitch_Rear` (empty) | Pin of the drawbar fork | — | Y = 0.55, X = 0, Z = −2.90 (CATALOG contract item 6) (within 5.8 m footprint); +Z forward |
| `PTO_Rear` (empty) | Shaft end stub (short chunky cylinder 6–8 segments) | 8 | Y = 0.70, X = 0, Z = −2.75 (same Z as `Link3P_Rear`, CATALOG contract item 6) |
| `Seat` (empty) | Driver seat point in the cab; seat block 0.4 × 0.4 m under glass allowed | block 11 | ≈ (0, 1.5, 0.1); +Z forward, +Y up |

### Wheel rules (shared with all FarmMachinery models; same pack function as TRC-01)

- One object per wheel (tyre + rim disc), origin exactly at the wheel centre, local X is the rotation axis, rest rotation (0,0,0), scale 1.
- Names front to back `Wheel_<Axle><Side>` with axle `F`, `M`, `R`, side `L`, `R`. This model: `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.
- Tyre: 16 segments, near-black (slot 10), 12–16 large blocky lugs (about 0.06–0.1 m), single chamfer on shoulders. Rim: cream disc (slot 3, inner slot 4), 8–12 segments, small hub. Same tread as TRC-01, scaled.
- LOD1 of each wheel is a child `<Wheel name>_LOD1` with zero offset (e.g. `Wheel_FL_LOD1`).
- Mudguards stay on the body.

## Moving parts summary

`Wheel_FL/FR/RL/RR` (centre, X), `Linkage_Rear` and `Linkage_Front` (pin axis, X), `Door_L` (hinge, Y). Rest = transport / closed. Each part has a `<Name>_LOD1` child with zero offset. Empties: `Hitch_Rear`, `Link3P_Rear` (child of `Linkage_Rear`), `Link3P_Front` (child of `Linkage_Front`), `PTO_Rear`, `Seat`. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Note: no `PTO_Front` on TRC-02 in the catalogue; do not add one.

## Palette slots (atlas 4×4, 64 px cells)

Body 5 / 6, cream 3 / 4, metal 7 / 8, tyre 10, chassis / seat / flaps 11, glass 12, lights 13, beacon 14. Atlas Red `#C8473B / #A8372E`; Green `#6E9F4A / #557D39` and Blue `#4A78A8 / #3A5F86` by material swap only; other cells identical in all atlases. One material per model.

## LOD / Lite

LOD yes (LOD1 50 % per part by `make_lod1.py`; LODGroup on the root). Lite: yes (13-model Lite). Not a pilot item.

## Anchor

Closest approved model: TRC-01 Tractor_Cab of this pack (same cab, bonnet chamfer, wheel function, colours) once approved; style anchor Farm Yard `FMS_Tractor` — preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`. Not a proportion anchor: the Farm Yard tractor is open and small; TRC-02 is a heavy four-equal-wheels cab tractor.

## What NOT to do

- Do not deviate from CATALOG "Игровая готовность" item 6: lower-link pins 0.90 m apart (X = ±0.45) at Y 0.60; Link3P/PTO/Hitch offsets as listed there.

- No small front wheels: all four wheels are Ø1.9 m with the same tread; no tracks, no twin wheels.
- Do not copy the `FMS_Tractor` silhouette (open seat, tall exhaust on short bonnet, grey rims). Keep a long bonnet, cab in the middle, cream rims.
- No interior, no transparent glass or second material.
- No hoses, wires, chains, bolts, cardan shaft, labels, logos; no part thinner than ~0.04 m.
- Wheels not baked into the body; do not rename; origin stays at the wheel centre.
- No `WheelCollider`, `Rigidbody`, animation.
- Both linkages stay inside the 5.8 m length (nose frame at Z ≈ +2.9 max, rear hitch at Z ≈ −2.9 min); do not stretch the bounding box.
- Front linkage must be built for `ATT-02` mating: `Link3P_Front` at 0.60 m, centred on X = 0.
- Mudguards clear the tyres ≥ 0.05 m; no coplanar overlapping faces.
- No separate files for colours.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRC-02_Tractor_Large/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
