# IMP-05 DiscHarrow — 3D spec (Э5 → Э7)

Reference: none — owner decision 2026-11-24: build from this spec without a preview reference (6 generations rejected). Style anchors: planning/FarmMachinery/references/IMP-01.png, IMP-03.png and the built IMP-01/IMP-03 models.

## Catalogue

Catalogue line: IMP-05 · Борона дисковая прицепная (`DiscHarrow`) · prefab `FMS_Mach_DiscHarrow_Red_Transport` / `_Work`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| Work 4.0 × 5.0 × 1.3; Transport 2.6 × 5.0 × 2.4 (X × Z × Y) | 4000 | yes | yes | 2 poses Transport (rest) / Work, same FBX |

Preview shows the Work pose; Transport pose derived from hinge angles below.

## Hierarchy and points

```
DiscHarrow (root)
  Frame            (drawbar, central frame, central disc sections)  [+ Frame_LOD1]
  Wing_L, Wing_R   (disc sections of both batteries + wing frame)  [+ _LOD1]
  Wheel_L, Wheel_R (+ _LOD1)
  Hitch_Front      (empty)
```

- `Hitch_Front`: X = 0, Y = 0.55, Z = +2.50 (drawbar eye centre, front end).
- Bounding box rest (Transport): X ±1.30, Z ±2.50, Y 0..2.40.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Drawbar | Shared drawbar, A-shaped, from the frame front (Z +1.2) to the eye at Z = +2.50 | 7, eye 8 | Static |
| Central frame | Chunky steel box frame 1.60 W × 3.2 L, rails 0.14 × 0.14 at Y 0.60–0.74, red top cover panels | 5/6 on the covers, 7/8 on rails | Static |
| Disc batteries (central) | Two batteries in an X/V layout (front gang angled ≈ 12° left-back, rear gang ≈ 12° right-back): 4 discs per battery in the central section; disc flat 12-segment Ø 0.70, 0.04 thick, chamfer, spacing 0.30 along a square axle 0.08; centre Y 0.35, so the bottom edge is at Y 0.00 | discs 7, rim edge 8, axle 8 | Static (in `Frame`) |
| `Wing_L`, `Wing_R` | Wing = frame arm 0.12 × 0.12 + one 4-disc section per battery (same discs and spacing, mirrored layout), signal-orange tip block 0.15. Built folded: rotated ≈ 65° up around the hinge (Z axis), so the wing reaches X ±1.30 and Y ≈ 2.40; Wing_R exact mirror of Wing_L | 7, orange 14 | Origin at the hinge on the central-frame edge at X = ±0.80, Y = 0.67, hinge axis Z; rest = Transport (folded up); Work = unfold by 65° down to horizontal (Wing_L −65°, Wing_R +65°, builder checks the sign) |
| `Wheel_L`, `Wheel_R` | Shared wheel function, Ø 0.90, width 0.30; centres X = ±0.70, Y = 0.45, Z = -0.80, on the central frame; outer face stays within the folded envelope | tyre 10, rim 3/4 | Wheel centre, spin axis X |
| `Hitch_Front` | Empty | — | Point |

## Moving parts and LOD

Moving: `Wing_L/R` (hinge Z), `Wheel_L/R` (spin X). LOD1 50 % per part. Lite: yes.

## Tris budget guide (total ≤ 4000)

About 24 discs × ≈ 48 tris (12-segment, two faces plus rim, chamfer on the rim only) ≈ 1150; frame, wings, axles ≈ 900; drawbar ≈ 150; wheels 2 × 450 ≈ 900; reserve ≈ 900.

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

- Discs are flat 12-segment discs, not cones or domes; do not make them thin cardboard: 0.04 m thick, with chamfered rim.
- No hydraulic cylinders or hoses, no chains, no lift lever; no PTO (there is none).
- Do not leave wings floating: each wing hinge is a bracket pinned to the central frame.
- Do not collide the folded wings with the wheels: wheels are inboard on the central frame (X ±0.70).
- No Wheel_* other than Wheel_L and Wheel_R. Do not forget that the model is built folded (Transport); Work is a prefab rotation.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-05_DiscHarrow/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
