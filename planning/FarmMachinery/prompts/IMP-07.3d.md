# IMP-07 HayRake — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-07.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-07 · Валкователь двухроторный (`HayRake`) · prefab `FMS_Mach_HayRake_Red_Transport` / `_Work`. Full only (not in Lite).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| Work 6.8 × 5.6 × 1.4; Transport 2.8 × 5.6 × 3.4 (X × Z × Y) | 5000 (tine lattices: up to ~2× overrun allowed, record the real figure) | yes | no | 2 poses Transport (rest) / Work, same FBX |

## Hierarchy and points

```
HayRake (root)
  Frame            (central frame, drawbar, wheel brackets)  [+ Frame_LOD1]
  Arm_L, Arm_R     (+ _LOD1)
    Rotor_L / Rotor_R  (children of the arms; hub + 12 tines)  [+ _LOD1]
  Wheel_L, Wheel_R (+ _LOD1)
  Hitch_Front, PTO_Front  (empties)
```

- `Hitch_Front`: X = 0, Y = 0.55, Z = +2.80 (drawbar eye centre; front end).
- `PTO_Front`: X = 0, Y = 0.70, Z = +2.95 (= Hitch_Front + (0, 0.15, 0.15), CATALOG contract item 6; the empty may sit ahead of the eye, the stub geometry stays on the drawbar) (end face of a short stub beside the drawbar).
- Bounding box rest (Transport): X ±1.40, Z ±2.80, Y 0..3.40.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Central frame | Chunky steel-box frame 1.60 W × 3.00 L, rails 0.14 × 0.16 at Y 0.70–0.86, red cover and gearbox housing 0.80 × 0.60 × 0.40 with chamfer 0.06 on the frame centre | 5/6 housing, 7/8 rails | Static |
| Drawbar | Shared drawbar from the frame front to the eye at Z = +2.80; PTO stub 0.10 m at Z +2.40..+2.50 | 7, eye 8, stub 8 | Static |
| `Arm_L`, `Arm_R` | Thick steel arm 0.16 × 0.16 × 2.00 m with a hinge block; built raised ≈ 70° above horizontal (Transport), outward; carries the rotor at its end. Arm_R the exact mirror of Arm_L | 7, hinge block 8 | Origin at the hinge on the frame edge, X = ±0.80, Y = 0.85, Z = -0.20, hinge axis Z; rest = raised (Transport); Work = lower by 70° to horizontal (Arm_L −70° toward -X, Arm_R +70° toward +X; builder verifies sign) |
| `Rotor_L`, `Rotor_R` | Hub: 8-segment cylinder Ø 0.35 × 0.25; 12 radial tine arms 0.07 × 0.07, 1.10 m long, evenly spaced every 30°, each ending in a bent tine tip 0.25 long, tilted 10° downward; rotor disc plane perpendicular to the arm tilt (in Work the rotor lies flat horizontal at Y ≈ 0.6–0.9, giving the 6.8 m span: rotor centres at X ±2.0, radius 1.4); small orange reflector on each arm | 7, tine tips 8, reflector 14 | Origin on the hub centre, spin axis = the rotor normal (local Y); rest rotation (0,0,0) in the arm frame |
| `Wheel_L`, `Wheel_R` | Shared wheel function, Ø 0.80, width 0.28; centres X = ±0.95, Y = 0.40, Z = -0.80, on brackets under the frame | tyre 10, rim 3/4 | Wheel centre, spin axis X |
| `Hitch_Front`, `PTO_Front` | Empties | — | Points |

## Moving parts and LOD

Moving: `Arm_L/R` (hinge Z), `Rotor_L/R` (spin Y), `Wheel_L/R` (spin X). LOD1 50 % per part; `Rotor_*_LOD1` is a child of the rotor. Full only.

## Tris budget guide (total ≈ 5000, up to 10000 permitted)

Frame, housing, drawbar ≈ 700; arms ≈ 200; two rotors: 12 tines × ≈ 70 + hub ≈ 950 each ≈ 1900; two wheels ≈ 2 × 400 ≈ 800; reserve for chamfers.

## Note for the builder

The catalogue gives only Arm pivot Z and Rotor pivot Y; the arm raise angle (≈ 70°) and the rotor centres (X ±2.0 in Work) are derived from the extents (Work 6.8 wide, Transport 3.4 tall): adjust within the extents and record the values in `notes.md`.

## Common rules (Игровая готовность, apply exactly)

- Root origin on the ground (Y = 0), centre of the bounding box in X and Z, rotation (0,0,0), scale 1. Unity: forward +Z, up +Y; follow `blender-unity-assets` axis conventions for export. The implement faces forward like the tractor: its hitch end (the front) is at +Z.
- Empty objects only for points, no mesh, +Z forward, +Y up. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m. Rule: the implement `_Front` point must coincide with the tractor `_Rear` point (`Hitch_Front` = drawbar eye centre, `Link3P_Front` = centre between the two lower lug pin axes, `PTO_Front` = end face of the PTO stub).
- No rigging, animation, scripts, Rigidbody, WheelCollider, constraints. No PTO driveshafts (owner decision): a PTO point is a bare empty with a short chunky stub (box/6–8 segment cylinder, 0.08 m) at most. One material, Red atlas (Green/Blue ship as atlases, no variant meshes), flat shading, no textures. Implements are Red only (owner decision).
- Moving parts: separate objects with origin on the hinge axis, rest = Transport/closed. A pose variant (Work, Open) is the same FBX; the prefab rotates the part. LOD1 of every moving part is a child `<Name>_LOD1` with zero offset inside it. LOD1 50 % via `Tools/blender/make_lod1.py`; LODGroup on the root in Unity.
- Wheels are children of the machine, one object each (tyre + rim), origin at the wheel centre, spin axis local X, rest rotation (0,0,0), names `Wheel_L` / `Wheel_R` (one axle) or `Wheel_Gauge`. Shared wheel look (same builder function in the whole pack): tyre 16 segments, near-black `#2B2D31` (slot 10) with 12–16 large blocky tread lugs standing proud of the carcass by about 8 % of the tyre diameter; rim a cream `#F2E6C9` (slot 3) dished disc with an 8–12 segment hub, inner face `#DCC9A0` (slot 4). Fenders are part of the body, not of the wheel.
- Shared three-point linkage frame (identical on all Link3P implements IMP-01/02/04/06 and ATT-01): chunky A-shaped mast, two lower hitch lugs (flat plates 0.14 × 0.22 × 0.08 with 8-segment pin holes Ø 0.07) whose pin axes lie along X at X = ±0.45 (0.90 m apart), Y = 0.60, and one top-link bracket above. Steel grey `#8E959B`, darker `#6E757B` for bores and undersides; mast painted red `#C8473B` / `#A8372E`.
- Shared drawbar (identical on all `Hitch_Front` implements and trailers): steel-grey `#8E959B` A-shaped or single beam drawbar, 0.12–0.14 m thick, ending in a chunky ring eye (octagonal outer 0.24 m, hole 0.08 m, 0.08 m thick, hole axis vertical), eye centre at Y = 0.55, `Hitch_Front` at the eye centre.
- Bodies/hoppers/frames: main edges chamfered 45° by 0.04–0.08 m; parts under 0.04 m are not modelled; parts that touch really touch; `pack_common.coplanar_overlaps` = 0.

## Anchor

Closest approved model: Farm Yard `FMS_Tractor` (chamfers, lug tyres, red, steel) — preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`; its build script is not in this repository. Within this pack, the closest model is IMP-01 Plough (pilot; shared mast, lugs and gauge wheel) — follow its spec for the linkage frame. Helpers: `Tools/blender/pack_common.py`, `pack_shapes.py`.

## What NOT to do

- Twelve tine arms per rotor, evenly spaced; no thin wire tines (arms ≥ 0.06 m). Do not simplify rotors to flat discs: radial tines must read.
- Wheels are on the central frame, not on the arms; do not parent them to Arm_*.
- No PTO driveshaft; no hoses, no hydraulic cylinders, no chains.
- Rotors must not intersect the wheels or the frame in Transport; Arm_L and Arm_R are exact mirrors.
- Do not attach Link3P points: this is a trailed machine with Hitch_Front only.
- No Wheel_* other than Wheel_L and Wheel_R. Built in Transport; Work is a prefab rotation.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-07_HayRake/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->


## Fix 1 (2026-11-24, review models_b3, owner decision B)
- What is wrong: Transport width 4.57 m (spec 2.8; CATALOG transport 2.8×5.6×3.4) — too wide next to 2.5 m trailers on road scenes.
- What to do: raise Arm_L/R in the Transport (rest) pose to 75–80° (instead of 70°), keep arm length hinge→hub 1.50 m and rotor radius 1.09 m; measure the real bbox (builder notes give hub X 1.52 — re-check). Targets: Transport width ≤ 3.0 m, height ≤ 3.4 m; Work span stays ~6.66 m (Work pose = arms lowered by the same angle). Re-check rotor×wheel clearance and mating on TRC-01/TRC-02 (Hitch + PTO). Nothing else changes.
