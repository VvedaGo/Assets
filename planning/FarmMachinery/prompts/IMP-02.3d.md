# IMP-02 Seeder — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-02.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-02 · Сеялка навесная 3 м (`Seeder`) · prefab `FMS_Mach_Seeder_Red`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.0 × 1.9 × 1.7 (X × Z × Y), folded markers, lid closed | 3500 | yes | yes | none (Red only) |

## Hierarchy and points

```
Seeder (root)
  Frame            (tool bar, hopper, hitch mast, coulters, press row)  [+ Frame_LOD1]
  Lid              (+ Lid_LOD1)
  Marker_L, Marker_R (+ _LOD1)
  Wheel_L, Wheel_R (+ _LOD1)
  Link3P_Front     (empty)
```

- `Link3P_Front`: X = 0, Y = 0.60, Z = +0.85 (centre between the lower lug pin axes, at the front of the mast; front end of the model at Z = +0.95).
- Bounding box target (rest, folded markers, lid closed): X ±1.50, Z -0.95..+0.95, Y 0..1.70.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Tool frame | Steel box beam 3.0 m wide (0.12 × 0.14) at Y 0.40–0.54, Z ≈ 0; second parallel beam 0.5 m behind; two short side plates | 7, undersides 8 | Static |
| Mast | Shared three-point linkage frame at the front (Z +0.85..+0.95), mast reaching Y 1.10 | 5/6 mast, 7/8 lugs | Static |
| Hopper | Chamfered trapezoid box 2.80 W (X) × 0.90 D (Z) × 0.60 H (Y), narrower at the bottom (bottom 2.50 × 0.60); base at Y 0.75, top at Y 1.35; chamfer 0.06; two steel straps across | 5 sides/top, 6 lower and side faces, 7 straps | Static |
| `Lid` | Flat plate 2.70 × 0.80 × 0.05 on top of the hopper opening, with a small handle block on its front edge | 5 (handle 7) | Origin on the rear hinge edge, Z = -0.45, Y 1.35, hinge axis X; rest = closed (rotation 0); open ≈ -70° |
| Coulters ×9 | Wedge-shaped shoes 0.10 W × 0.28 H × 0.30 L under the front beam at even 0.33 m spacing across X ±1.32, bottom at Y 0.12, pointed forward | 8 | Static |
| Press row | Rear bar at Y 0.30, Z = -0.70, 2.8 m wide, with nine narrow press wheels (8-segment discs Ø 0.40, 0.08 wide) merged into the Frame mesh | 7, discs 8 | Static (not Wheel_*) |
| `Wheel_L`, `Wheel_R` | Shared wheel function, Ø 0.70, width 0.18; centres X = ±1.34, Y = 0.35, Z = -0.25; on short steel plates from the frame ends | tyre 10, rim 3/4 | Wheel centre, spin axis X |
| `Marker_L`, `Marker_R` | Chunky steel arm 0.10 × 0.10 × 1.00 m with a 8-segment disc Ø 0.40 × 0.04 at its tip; folded = pointing up vertically at the frame ends (X = ±1.50, base at Y 0.70, tip at Y 1.70); hinge pin ear on the frame | 7, disc 8, orange reflector block 14 | Origin at the hinge near the frame end, hinge axis Z; rest = folded (up); unfolded = swung outward ≈ 90° to horizontal (Marker_L to -X, Marker_R to +X) |
| Orange reflectors | Two flat blocks 0.10 × 0.10 at the hopper ends | 14 | Static |
| `Link3P_Front` | Empty, see above | — | Point |

## Moving parts and LOD

Moving: `Lid` (X), `Marker_L/R` (Z), `Wheel_L/R` (spin X). LOD1 50 % per part (each moving part has its own `_LOD1` child). Lite: yes.

## Tris budget guide (total ≤ 3500)

Hopper + lid ≈ 450; frame, beams, mast, lugs ≈ 500; nine coulters ≈ 600; press row ≈ 650; markers ≈ 250; two wheels ≈ 2 × 450 = 900; reserve ≈ 150.

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

- No seed tubes, hoses, wiring, chains, sprockets or gearboxes; no text on the hopper.
- No thin marker arms: arms are 0.10 m square minimum. Marker discs are chunky 8-segment discs.
- Do not make the hopper a plain box: chamfered, trapezoid (narrower at the bottom), lid is a separate plate hinged at the rear.
- Do not hide the coulter row: the nine shoes must be visible from the ¾ view below the frame bar.
- Wheels must not sit under the hopper: they are at the frame ends, outside the coulter row.
- Do not put PTO, Hitch or Link3P_Rear points on it. No Wheel_* other than Wheel_L and Wheel_R.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-02_Seeder/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
