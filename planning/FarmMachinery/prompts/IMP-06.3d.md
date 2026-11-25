# IMP-06 Cultivator — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-06.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-06 · Культиватор навесной 3 м (`Cultivator`) · prefab `FMS_Mach_Cultivator_Red`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.0 × 2.2 × 1.3 (X × Z × Y) | 2500 | yes | yes | none (Red only) |

## Hierarchy and points

```
Cultivator (root)
  Frame            (beams, mast, tines)  [+ Frame_LOD1]
  Roller           (+ Roller_LOD1)
  Link3P_Front     (empty)
```

- `Link3P_Front`: X = 0, Y = 0.60, Z = +0.95 (centre between the lower lug pin axes; front end of the model Z = +1.10).
- Bounding box: X ±1.50, Z ±1.10, Y 0..1.30.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Frame beams | Three cross beams 3.0 m long (0.10 × 0.12) at Y 0.55–0.67, Z = +0.40, -0.05, -0.50; two side beams 0.10 × 0.12 at X = ±1.40 joining them; centre diagonal brace | 7, undersides 8 | Static |
| Mast | Shared three-point linkage frame at the front (Z +0.85..+1.10), mast top at Y 1.30 | 5/6 mast, 7/8 lugs | Static |
| Tines ×20 | Rows: 7 at Z = +0.40 (X = -1.35 + 0.45·i), 6 at Z = -0.05 (X offset by 0.225), 7 at Z = -0.50 (same as row 1). Each tine: clamp block on the beam, then a chunky faceted S-curve of 4–5 box segments (0.06 × 0.08) sweeping back and down to a pointed sweep share 0.14 wide at Y 0.00 | 7, share 8 | Static (in `Frame`) |
| Roller arms | Two steel arms 0.10 × 0.10 from the rear beam back to the roller axle (X = ±1.25) | 7 | Static |
| `Roller` | Cage roller: 16-segment cylinder Ø 0.50 × 2.80 length along X with 8 chunky ribs standing proud 0.04 and darker end caps; centre Y 0.25, Z = -0.85 (bottom touches Y 0) | 7, ribs 8, caps 8 | Origin at the roller centre, spin axis X; rest rotation (0,0,0) |
| `Link3P_Front` | Empty | — | Point |

## Moving parts and LOD

Moving: `Roller` (spin X). LOD1 50 %. Lite: yes.

## Tris budget guide (total ≤ 2500)

Tines ≈ 20 × 70 = 1400 (reduce segments to 4 if over budget); frame and mast ≈ 550; roller ≈ 400; reserve ≈ 150.

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

- Tines are chunky faceted S-curves (4–5 straight box segments, section ≥ 0.06), not wire; the three rows must interleave and read from the top.
- No wheels (no Wheel_* objects); no PTO; no hydraulic cylinders or hoses.
- Do not make it look like the disc harrow: no discs. Roller is a cage with chunky ribs on 16 segments, not a smooth drum.
- Do not leave the roller floating: it hangs from two arms and touches Y = 0.
- Do not use a different linkage frame from IMP-01.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-06_Cultivator/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
