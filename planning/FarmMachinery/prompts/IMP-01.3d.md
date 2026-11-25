# IMP-01 Plough — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/IMP-01.png  <!-- accepted by orchestrator 2026-11-24 -->

## Catalogue

Catalogue line: IMP-01 · Плуг навесной 4-корпусный (`Plough`) · prefab `FMS_Mach_Plough_Red` · pilot item (checks Link3P docking on TRC-01 Cab, CMP-01).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.6 × 3.6 × 1.4 (X × Z × Y) | 2500 (LOD0 incl. gauge wheel) | yes (LOD1 50 %, `make_lod1.py`) | yes | none (Red only; Green/Blue atlases ship in the pack) |

## Common rules (Игровая готовность, apply exactly)

- Root origin on the ground (Y = 0), centre of the bounding box in X and Z, rotation (0,0,0), scale 1. Unity: machine forward +Z, up +Y; follow `blender-unity-assets` axis conventions for export.
- The implement is modelled in its resting/lowered working stance: share tips and the lowest point of the gauge wheel touch Y = 0. The implement faces forward like the tractor: its hitch end (the front) is at +Z, it trails toward -Z.
- Empty objects only, no mesh, +Z forward, +Y up. Standard rest heights: Hitch 0.55 m, Link3P 0.60 m, PTO 0.70 m.
- No rigging, animation, scripts, Rigidbody, WheelCollider, constraints. No PTO shafts (owner decision). One material, Red atlas, flat shading, no textures.
- Wheels are children of the machine, one object each (tyre + rim), origin at the wheel centre, spin axis local X, rest rotation (0,0,0). LOD1 of every moving part is a child `<Name>_LOD1` with zero offset inside it.
- Shared wheel look (same builder function in all pack models): tyre 16 segments, near-black `#2B2D31` (slot 10) with 12–16 large blocky tread lugs standing proud of the carcass by about 8 % of the tyre diameter; rim a cream `#F2E6C9` (slot 3) dished disc with an 8–12 segment hub, inner face `#DCC9A0` (slot 4).
- Shared three-point linkage frame (same on all Link3P implements IMP-01/02/04/06 and ATT-01): a chunky A-shaped mast, two lower hitch lugs (flat plates with 8-segment pin holes) whose pin axes lie along X, centre-to-centre 0.90 m, and one top-link bracket above them. Steel grey `#8E959B`, darker `#6E757B` for undersides and lugs' bores.

## Hierarchy and points

```
Plough (root)
  Frame            (static; beam, mast, bottoms, stub arm)  [+ Frame_LOD1]
  Wheel_Gauge      (+ Wheel_Gauge_LOD1)
  Link3P_Front     (empty)
```

- `Link3P_Front` (empty): X = 0, Y = 0.60, Z = +1.55 (centre between the two lower lug pin axes, at the front of the mast). Forward +Z, up +Y. It must coincide in position and rotation with `Link3P_Rear` of TRC-01 when docked, and the lugs' pin axes must lie exactly along X through this point (lugs at X = ±0.45).
- The plough has no lift of its own: lifting is `Linkage_Rear` of the tractor.
- Root bounding box target: X -0.80..+0.80, Z -1.80..+1.80, Y 0..1.40.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Main beam | One square-section tube 0.14 × 0.14 m, chamfered 0.04, running diagonally in plan from front-left (X -0.55, Z +1.05) to rear-right (X +0.55, Z -1.65) at Y 0.50–0.64 | top face 5 `#C8473B`, sides/underside 7 `#8E959B`, bottom 8 `#6E757B` | Static |
| Hitch mast | A-frame: two sloped legs 0.12 m thick rising from the lower lugs (Y 0.60) to a top-link bracket at X = 0, Y = 1.30, Z = +1.45; cross plate between legs at Y 0.80; mast reaches Z = +1.80 at the lugs' front face. Mast body red with darker side faces. Top pin bracket: block with an 8-segment pin hole, pin axis along X | 5 and 6 for the mast, 7/8 for lugs and bracket | Static |
| Lower hitch lugs | Two flat plates 0.14 wide × 0.22 tall × 0.08 thick at X = ±0.45, centred at Y = 0.60, Z = +1.70, pin hole 8 segments, Ø 0.07 | 7 (bore 8) | Static |
| Plough bodies ×4 | Identical. Body i hangs from the beam at Z = +0.75, +0.05, -0.65, -1.35 and X = -0.52, -0.17, +0.17, +0.52 (spacing 0.35 in X, 0.70 in Z), forming the diagonal. Each: vertical leg (box 0.10 × 0.10 × 0.50, from the beam down to Y 0.10), mouldboard: a bent plate 0.30 wide (X) × 0.55 long (Z) × 0.40 tall built from 3 flat facets twisting from vertical at the front to leaning outward at the rear, plate thickness 0.04; share: a wedge 0.30 wide × 0.40 long, lowest edge at Y = 0.00, tip pointing forward (+Z); cutting edge strip on the share | leg 7, mouldboard 7, share 7 with edge strip 8 | Static |
| Gauge wheel stub arm | A horizontal cross-arm (box 0.10 × 0.10, Y 0.64–0.74, resting on the top face of the beam so it passes over body 4) along X at Z = -1.55 from the beam to X = -0.62, then a vertical plate 0.10 thick down to the wheel axle at Y 0.30, carrying the wheel on its inner side | 7 | Static |
| `Wheel_Gauge` | Shared wheel function, Ø 0.60, width 0.20, tyre lugs 12; centre X = -0.62, Y = 0.30, Z = -1.55 (outer face at X -0.72, inside the 0.80 half width) | tyre 10, rim 3 and 4 | Origin at wheel centre, spin axis X, rest (0,0,0) |
| `Link3P_Front` | Empty, see above | — | Point |

## Moving parts and LOD

- `Wheel_Gauge` is the only moving part (spin about X). `Wheel_Gauge_LOD1` is a child with zero offset; spinning the wheel turns both LODs.
- LOD1 50 % for `Frame` and `Wheel_Gauge`, built by `Tools/blender/make_lod1.py`; LODGroup is assembled on the root in Unity.
- Lite: yes.

## Tris budget guide (LOD0, total ≤ 2500)

Mast + lugs + bracket ≈ 350; beam + stub arm ≈ 120; four bodies ≈ 4 × 330 = 1320; `Wheel_Gauge` ≈ 450 (16 seg + 12 lugs); remaining ≈ 260 reserve. Do not exceed 2500.

## Anchor

Closest approved model: Farm Yard `FMS_Tractor` (shape language, chamfers, lug tyres, red) — preview `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`; its build script is not in this repository (no tractor script under `Tools/`). Shared helpers: `Tools/blender/pack_common.py`, `pack_shapes.py`.

## What NOT to do

- No reversible (flip-over) mechanism, no coulter discs, no skimmers, no hydraulic cylinder or hoses: only the parts in the table.
- No thin legs or plates under 0.04 m; legs and beam stay chunky (0.10–0.14 m). Mouldboards are readable faceted fins, not flat sheets.
- Do not make the four bodies parallel to the Z axis in a line: the diagonal stagger is the signature and must read from the top and from the ¾ view.
- Lower lug pin axes must be along X, spacing exactly 0.90 m, at Y 0.60; `Link3P_Front` exactly between them. A wrong height or spacing breaks docking on TRC-01.
- Nothing floats: legs touch the beam, the wheel stub touches the beam and the axle, shares sit at Y = 0.00 with no gap or penetration below it.
- No PTO shaft or PTO point (IMP-01 has no PTO), no text/logos, no mud or rust. Do not model the tractor's linkage.
- No coplanar overlapping faces (`pack_common.coplanar_overlaps` = 0). Flat shading, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/IMP-01_Plough/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
