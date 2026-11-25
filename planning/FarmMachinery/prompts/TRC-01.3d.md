# TRC-01 Tractor_Cab — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/TRC-01.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

`TRC-01 | Tractor_Cab | 3 variants Red / Green / Blue (atlas swap) | 2.4×4.4×3.0 | 7000 tris | pilot: yes ("characteristic") | LOD yes | Lite yes`
Prefab names: `FMS_Mach_Tractor_Cab_Red`, `_Green`, `_Blue` (one mesh/FBX, material swap only; no new UV). The preview is Red.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.4 × 4.4 × 3.0 (X × Z × Y) | 7000 (LOD0, incl. wheels) | LOD1 50 % per part via `Tools/blender/make_lod1.py` | yes | Red / Green / Blue |

Suggested tris split (soft): 4 wheels ≈ 1800 (front ≈ 400, rear ≈ 500 each), cab ≈ 1100, bonnet + grille + lights ≈ 900, mudguards ≈ 700, chassis + steps + fuel tank ≈ 500, linkage + hitch + PTO ≈ 600, seat + mirrors + beacon + exhaust ≈ 400. Keep total ≤ 7000.

## Parts

Root: origin on the ground (Y = 0) at the centre of the footprint in X and Z, rotation (0,0,0), scale 1. Forward = +Z, up = +Y. Wheels, doors and linkage are child objects; no rigging, no scripts, no colliders in the FBX.

Wheel positions below are suggestions derived from the catalogue (the catalogue fixes only diameters and X/Z extents); keep the whole model inside 2.4 × 4.4 × 3.0 m.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| `Wheel_FL`, `Wheel_FR` | Shared wheel function (see wheel rules below), tyre Ø1.1 m, width ≈ 0.45 m. Centre height Y = 0.55. X ≈ ±0.95, Z ≈ +1.35 | tyre + lugs 10, rim disc 3, rim inner face 4, hub 8 or 7 | origin at wheel centre, rotation axis local X, rest rotation (0,0,0); steer around local Y of the same pivot |
| `Wheel_RL`, `Wheel_RR` | Same function, tyre Ø1.7 m, width ≈ 0.6 m. Centre height Y = 0.85. X ≈ ±1.0 (outer tyre edge ≈ 1.2 m), Z ≈ −1.0 | same | origin at wheel centre, axis local X |
| Bonnet | Long narrow box over the front axle, top edge with a single 45° chamfer 0.04–0.08 m, front face as grille block | 5 top, 6 side / lower faces; grille 11 | rigid |
| Grille + headlights | Grille block with 5–6 chunky vertical bars (0.04+ m thick); two headlight blocks at the front corners | grille 11, lights 13 | rigid |
| Front weight bar | Steel bar under the nose | 7 | rigid |
| Front mudguards | Chamfered arches over `Wheel_FL/FR`, clear of the tyres by ≥ 0.05 m, do not rotate with the wheel | 5, inside 6 | rigid, on body |
| Rear mudguards | Wide arches over `Wheel_RL/RR`, inner mud flaps | 5, flaps 11 | rigid, on body |
| Cab | Closed four-pillar cab over the rear half: 4 pillars (≥ 0.08 m thick), flat roof with single 45° chamfer, flat glass panels on all sides (single opaque panels, no interior, no seat visible through the glass), cream stripe along the lower edge, mirror blocks on both sides, top height 3.0 m | pillars / roof 5 (inside edges 6), glass 12, stripe 3, mirrors 11 | rigid; the glass is opaque, same material |
| `Door_L` | Left cab door as a separate object: flat glass panel in a 4-bar frame, handle block | frame 5, glass 12 | origin on the hinge axis (front edge of the door), hinge axis Y; rest = closed |
| Beacon | Small cylinder (6–8 segments) on the roof corner | 14 | rigid |
| Exhaust | Cylinder 6–8 segments beside the left cab pillar on the bonnet | 7 | rigid |
| Chassis + steps | Dark chassis box between the axles, left step plate under the door, fuel tank block | 11, tank 6 | rigid |
| `Seat` (empty) | Driver seat point inside the cab (no seat mesh needed, only a simple seat block 0.4 × 0.4 m is allowed under the glass; no interior is visible) | seat block 11 | empty, +Z forward, +Y up. ≈ (0, 1.25, −0.9) |
| `Linkage_Rear` | Two lower lift arms (chunky bars ≥ 0.08 m) plus top link and lift struts as simple rods only where they hold the arms; rigid steel parts | 7, bars 8 | origin on the lower-link pin axis (X axis), at Y = 0.60; rest = lowered. Children below |
| `Link3P_Rear` (empty, child of `Linkage_Rear`) | Centre between the pins of the two lower links, Z ≈ −2.0 | — | Y = 0.60 in rest pose; follows the linkage when it lifts; +Z forward, +Y up |
| `Hitch_Rear` (empty) | Position of the drawbar fork pin on the tractor rear drawbar | — | Y = 0.55, X = 0, Z ≈ −2.15 (inside the 4.4 m footprint); +Z forward, +Y up |
| Drawbar fork | Chunky tow-hitch fork plate with pin hole, lower than the linkage | 7 / 8 | rigid, pivot on the root |
| `PTO_Rear` (empty) | Shaft end stub (short chunky cylinder 6–8 segments allowed) | 8 | Y = 0.70, X = 0, Z ≈ −2.0; +Z forward, +Y up |

### Wheel rules (shared with all FarmMachinery models; builder uses the same pack function)

- One object per wheel (tyre + rim disc together), origin exactly at the wheel centre, local X is the rotation axis, rest rotation (0,0,0), scale 1.
- Names, front to back: `Wheel_<Axle><Side>` with axle `F`, `M`, `R`, side `L`, `R`. This model uses `Wheel_FL`, `Wheel_FR`, `Wheel_RL`, `Wheel_RR`.
- Tyre: 16 segments around, near-black (slot 10), 12–16 large blocky tread lugs (about 0.06–0.1 m high), single chamfer on the shoulder. Rim: cream disc (slot 3, inner face slot 4), 8–12 segments, small hub.
- LOD1 of each wheel is a child `<Wheel name>_LOD1` with zero offset (e.g. `Wheel_FL_LOD1`), so rotating `Wheel_FL` rotates both LODs.
- Fenders and mudguards stay on the body, not on the wheels.

## Moving parts summary

`Wheel_FL/FR/RL/RR` (centre, X axis), `Linkage_Rear` (lower-link pin axis, X), `Door_L` (hinge, Y). Rest pose = transport / closed. Every part has its own `<Name>_LOD1` child with zero offset. Empties: `Hitch_Rear`, `Link3P_Rear` (child of `Linkage_Rear`), `PTO_Rear`, `Seat`. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m (confirm on the pilot together with IMP-01).

## Palette slots (atlas 4×4, 64 px cells)

Body 5 / 6, cream 3 / 4, metal 7 / 8, tyre 10, chassis / seat / mud flaps 11, glass 12, lights 13, beacon 14. Atlas Red `#C8473B / #A8372E`; Green `#6E9F4A / #557D39` and Blue `#4A78A8 / #3A5F86` are only swapped at the material level. All other 14 cells are identical in all three atlases, so UV must reference cells, not a fixed colour. One material per model.

## LOD / Lite

LOD yes (LOD1 50 % per part by `make_lod1.py`; LODGroup on the root). Lite: yes. Pilot item (characteristic), built together with IMP-01.

## Anchor

Closest approved model: Farm Yard, `FMS_Tractor` — preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`; build script: Farm Yard pack script for `FMS_Tractor` (location per the pack's pipeline notes). Style anchor only (chamfer width, lug size, red, flat shading), NOT a proportion or silhouette anchor: TRC-01 is a closed-cab tractor, FMS_Tractor is an open tractor.

## What NOT to do

- Do not deviate from CATALOG "Игровая готовность" item 6: lower-link pins 0.90 m apart (X = ±0.45) at Y 0.60; Link3P/PTO/Hitch offsets as listed there.

- Do not copy the `FMS_Tractor` silhouette: no open seat, no tall exhaust on a short bonnet, no grey wheel discs. The cab must be the tallest part (≈3.0 m), the bonnet long and chamfered, the rims cream.
- No interior, no steering wheel, no seat visible through the glass, no transparent glass or second material.
- No hoses, wires, chains, bolts, labels, logos, cardan shaft or small levers; no part thinner than ~0.04 m.
- Wheels must not be merged into the body mesh or baked in the root; do not rename them; do not move the origin away from the wheel centre.
- Do not add `WheelCollider`, `Rigidbody` or animation; no hydraulic cylinders other than simple rods under the lift arms.
- Mudguards, steps and the exhaust must not intersect the tyres; leave ≥ 0.05 m clearance.
- No coplanar overlapping faces; parts that touch share edges or are offset ≥ 1 mm.
- Do not exceed 2.4 m width including tyres and mudguards; do not scale the model to fit.
- Do not make separate files for colours: Red / Green / Blue are one mesh with different materials.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/TRC-01_Tractor_Cab/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
