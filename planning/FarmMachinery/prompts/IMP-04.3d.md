# IMP-04 Mower — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-04.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-04 · Косилка дисковая навесная (`Mower`) · prefab `FMS_Mach_Mower_Red_Transport` / `_Work`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| Work 3.2 × 1.6 × 1.0; Transport 1.7 × 1.6 × 3.1 (X × Z × Y) | 2500 | yes | yes | 2 poses Transport (rest) / Work, same FBX |

## Hierarchy and points

```
Mower (root)
  Frame            (mast, housing, swing arm base)  [+ Frame_LOD1]
  Bar              (swing arm + cutter bar + discs + guard)  [+ Bar_LOD1]
  Link3P_Front, PTO_Front  (empties)
```

- `Link3P_Front`: X = 0, Y = 0.60, Z = +0.70 (front end of the model Z = +0.80).
- `PTO_Front`: X = 0, Y = 0.70, Z = +0.70 (end face of a stub 0.10 m above/between the lugs, offset so that it does not collide with the top bracket).
- Bounding box rest (Transport, bar raised): X -0.85..+0.85, Z ±0.80, Y 0..3.10. Work (bar rotated down): X -0.85..+2.35, Y 0..1.00.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Frame | Shared three-point linkage frame (mast + two lugs 0.90 apart + top bracket), steel box frame 1.30 × 1.30 × 0.14 at Y 0.45–0.60, red transmission housing 0.60 × 0.50 × 0.40 on top with chamfer 0.06; hinge ear block on the right side | 7/8, housing 5/6, mast 5/6 | Static |
| `Bar` | One object: swing arm (box 0.14 × 0.14) from the hinge to the housing, flat cutter-bar housing 1.50 × 0.30 × 0.14 (long axis along the arm direction) carrying five flat 8-segment discs Ø 0.28 with darker blade tips; red protective guard curtain 1.50 × 0.35 × 0.04 along the back, signal-orange warning blocks at both ends | 7 arm/housing, discs 7 with tips 8, guard 5/6, blocks 14 | Origin on the hinge at X = +0.85, Y = 0.90 (right side of the frame), hinge axis Z. Rest = Transport: bar stands vertically up (tip at Y ≈ 2.5 with the 1.5 m bar; see the note below on reaching 3.1). Work = bar rotated down about the hinge by -90° so it lies horizontally to the right (+X) at Y ≈ 0.90–1.00 (builder verifies the sign) |
| `Link3P_Front`, `PTO_Front` | Empties | — | Points |

## Moving parts and LOD

Moving: `Bar` (Z hinge). `Bar_LOD1` child with zero offset. LOD1 50 %. Lite: yes.

## Tris budget guide (total ≤ 2500)

Frame + mast + lugs ≈ 700; housing ≈ 150; `Bar` ≈ 5 discs × 100 + housing 200 + guard 100 ≈ 800; reserve ≈ 850 for chamfers.

## Contradiction to note for the builder

Catalogue extents (Work width 3.2, Transport height 3.1, Work height 1.0) cannot all hold with the pivot at Y 0.90 and bar length 1.5 m: a bar 1.5 m from the pivot gives Transport height ≈ 2.5 m and Work width ≈ 3.2 m. The catalogue lists Bar pivot "Z, 0° work / 90° transport". Priority: (1) hinge on Z, rest = raised; (2) Work width 3.2 m; (3) Transport height as close to 3.1 m as the pivot allows (raise the pivot, or lengthen the swing arm, instead of changing the bar length); document the deviation in `notes.md`.

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

- Do not shorten the bar until the Work width cannot reach ~3.2 m; do not model the bar as a thin plank: housing 0.30 thick.
- No PTO shaft; no belts, no hoses, no hydraulic cylinder. No wheels (the mower is carried by the tractor linkage).
- The five discs are flat 8-segment discs with darker blade tips; do not draw spinning blades or blur.
- Nothing floats: arm touches frame, housing touches arm.
- Do not forget the guard curtain on the back: it is the red part that reads in the ¾ view.
- No Wheel_* object exists on this model.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-04_Mower/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
