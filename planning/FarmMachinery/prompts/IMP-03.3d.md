# IMP-03 Sprayer — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-03.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-03 · Опрыскиватель прицепной (`Sprayer`) · prefab `FMS_Mach_Sprayer_Red_Transport` / `_Work`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| Transport 2.5 × 5.6 × 3.0; Work 12.0 × 5.6 × 2.6 (X × Z × Y) | 5000 (booms are lattices: up to ~2× overrun allowed, write the actual figure into spec/notes) | yes | yes | 2 poses Transport (rest) / Work, same FBX |

## Hierarchy and points

```
Sprayer (root)
  Chassis          (frame, tank, ladder, filler dome, drawbar)  [+ Chassis_LOD1]
  Boom_L, Boom_R   (+ _LOD1)
  Wheel_L, Wheel_R (+ _LOD1)
  Hitch_Front, PTO_Front  (empties)
```

- `Hitch_Front`: X = 0, Y = 0.55, Z = +2.80 (drawbar eye centre; front end of the model).
- `PTO_Front`: X = 0, Y = 0.70, Z = +2.95 (= Hitch_Front + (0, 0.15, 0.15), CATALOG contract item 6; the empty may sit ahead of the eye, the stub geometry stays on the drawbar) (end face of a short stub under/beside the drawbar; not a shaft).
- Bounding box rest (Transport): X ±1.25, Z -2.80..+2.80, Y 0..3.00.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Chassis frame | Steel box rails 0.14 × 0.16 at Y 0.75–0.90 running the full length, cross members, axle beam over the wheels | 7, undersides 8 | Static |
| Tank | Horizontal 16-segment cylinder Ø 1.80, length 3.00 along Z, centre Y 1.90, Z = -0.20; chamfered flat end caps (0.06); two steel straps; lower facets darker | 5 top, 6 lower facets, 7 straps | Static |
| Filler dome | 8-segment dome-cylinder Ø 0.55 × 0.30 on top at Z = -0.20, lid plate; top at Y 3.00 | 5/6, lid 7 | Static |
| Ladder + platform | Short steel ladder at the rear left of the chassis (rails 0.06, 3 rungs) and a small platform | 9 | Static |
| Drawbar | Shared drawbar: A-shaped beam from the chassis front to Z = +2.80, drops to Y 0.55 at the eye | 7, eye 8 | Static |
| PTO stub | Box/6-segment stub 0.10 at Z +2.40..+2.50 beside the drawbar | 8 | Static |
| Beacon | Small signal-orange block/8-segment lens on the tank top at the rear | 14 | Static |
| `Boom_L`, `Boom_R` | Chunky lattice truss ~4.90 m long: top and bottom rail 0.07 × 0.07 spaced 0.50 apart (truss Y centre ≈ 1.90), zig-zag diagonals 0.06 thick every 0.6 m, end caps; outer 0.5 m section in signal orange with a tip reflector. Transport: folded forward along the tank sides, hinge pivot at X = ±1.10, Z = -2.60, truss at Y 1.65–2.15 and X ±1.10..±1.35 (above the wheel tops, beside the tank) | 7, rails 8, tip/stripes 14 | Origin at the hinge axis (X = ±1.10, Z = -2.60), hinge axis Y; rest = folded forward (Transport); Work = Boom_L rotated -90° toward -X and Boom_R +90° toward +X (about Y, builder checks the sign so each swings outward); span in Work = 12.0 m |
| `Wheel_L`, `Wheel_R` | Shared wheel function, Ø 1.30, width 0.40; centres X = ±1.05 (outer face 1.25), Y = 0.65, Z = -0.50 | tyre 10, rim 3/4 | Wheel centre, spin axis X |
| `Hitch_Front`, `PTO_Front` | Empties, see above | — | Points |

## Moving parts and LOD

Moving: `Boom_L/R` (Y), `Wheel_L/R` (spin X). LOD1 50 % per part. Lite: yes. Prefab Work = same FBX with the two boom rotations.

## Tris budget guide (total ≈ 5000, up to 10000 permitted for the lattice)

Tank + dome + straps ≈ 700; chassis + drawbar + ladder ≈ 500; two wheels ≈ 2 × 600 = 1200 (Ø 1.3 tyres with 16 lugs); two booms ≈ 2 × 1100.

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

- No hoses, no nozzle pipes, no wiring, no thin pipe lattice: truss members are at least 0.06 m thick and the boom reads as a chunky lattice from 128 px.
- Do not model the tank as a smooth sphere or a box: horizontal 16-segment cylinder with chamfered flat end caps.
- No PTO driveshaft: the PTO point is a bare empty at the end of a short stub.
- Booms must not intersect the wheels or the tank in transport: boom pivots are outside the tank and above the wheel tops.
- Do not make Boom_L/Boom_R different shapes: Boom_R is the exact mirror of Boom_L.
- No Wheel_* other than Wheel_L and Wheel_R. No coplanar faces between truss rails and diagonals.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-03_Sprayer/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
