# HRV-02 Baler_Round — 3D spec (Э5 → Э7)

Reference: planning/FarmMachinery/references/HRV-02.png  <!-- accepted by orchestrator 2026-11-24 -->

Prefab `FMS_Mach_Baler_Round_Closed` and `FMS_Mach_Baler_Round_Open` (same FBX; Open = Tailgate rotated ~80° in the prefab). Red only (Green/Blue atlases ship). Unity axes: +Z forward, +Y up. Root origin on the ground at the centre of the footprint, rotation 0, scale 1. No bale is built or required: the chamber is empty, no dependency on Farm Market.

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.7 × 4.3 × 2.7 (Z from -2.15 to +2.15, Tailgate closed) | 5000 LOD0 incl. 2 wheels | yes, LOD1 50 % per part via `make_lod1.py` | no | 2: Closed / Open (pose, rotation of Tailgate in the prefab) |

## Parts

Wheels: ONE shared pack wheel function (same tread as all machines): 16-segment chamfered tyre (slot 10) with 12-16 large blocky tread lugs (slot 10), cream rim (slot 3) with 8-12 segment hub and inner face (slot 4); one object per wheel (tyre + rim), origin at wheel centre, axis local X, rest rotation 0. LOD1 as child `<Name>_LOD1` with zero offset.

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Root | empty at ground centre | - | origin ground, X/Z centre |
| Wheel_L | Ø1.0, tyre width ~0.50, centre (-1.10, 0.50, -0.70) | 10 / 3 / 4 | centre, axis X |
| Wheel_R | same, centre (+1.10, 0.50, -0.70) | 10 / 3 / 4 | centre, axis X |
| Chamber (front half) | round bale chamber Ø1.8, axis X, centre (0, 1.45, -0.90), width ~1.7 (X ±0.85): two 16-gon side plates (slot 5), drum shell front half, steel-grey roller bands (slot 7), single chamfer 0.04-0.08; ~16 segments | 5, 6 rim, 7 | static |
| Tailgate | rear half of the chamber: rear half of the drum shell + two side-plate halves + short hydraulic rods; closed = flush with the front half; orange stripes on the sides | 5, 6, 7, 14 | hinge axis X at the top of the chamber, (0, 2.35, -0.90); 0° closed, about +80° open (rear lower edge swings up and back); rest = closed |
| Pickup | pickup drum Ø ~0.5 with 8 chunky tine bars (≥ 0.05 thick) plus a guard bar, width ~1.5, spans Z +0.10 … +1.40, Y 0.15 … 0.75, shoulder fenders/guard above | 7, 8, 5 | rear hinge axis X at about (0, 0.55, +0.10); rest = lowered |
| Frame / drawbar | chassis under the chamber, wheel fenders (slot 6/11) over the tyres, drive cover box on the front of the chamber, drawbar from the frame forward to Z +2.15, support stand | 7, 8, 6, 11, 5 | static |
| Hitch_Front | empty at the drawbar tip, X 0, **Y 0.55**, Z +2.15; geometry: flat steel eye plate with a round hole | 7 | +Z forward, +Y up |
| PTO_Front | empty at X 0, **Y 0.70**, above the drawbar; its Z offset from Hitch_Front must equal the TRC Hitch_Rear / PTO_Rear spacing. The catalogue gives no spacing: FIXED by CATALOG contract item 6: PTO_Front = Hitch_Front + (0, 0.15, 0.15), i.e. Z +2.30, shaft end above the drawbar. Confirm against the TRC-01 spec on the pilot and correct here | - | +Z forward |
| Bale_Out | empty at the rear, (0, 0.90, -2.15), where a bale would be released; no mesh | - | +Z forward |
| Colliders | none in the model (prefab gets BoxColliders on chamber and frame, no wheels) | - | - |

Exact names: Wheel_L, Wheel_R, Tailgate, Pickup, Hitch_Front, PTO_Front, Bale_Out.

## Anchor

Closest approved model: Farm Yard `FMS_Tractor` (chamfers, tyre lugs, series red) `C:/Users/Sergv/AppData/Local/Temp/claude/a96f3f7eb3db32ab/c5f43832-fa51-4315-8edc-a51f3e333944/scratchpad/refs/previews/FarmYard_Tractor.png`; Farm Yard `FMS_Silo` for banded cylinder segmentation `…/FarmYard_Silo.png`. Companion wording for wheels and hitch: TRL / IMP items of this pack.

## What NOT to do

- No bale and no Load mesh anywhere: the chamber is empty; do not reference Farm Market.
- The Tailgate is a separate object with the pivot at the top hinge; do not fuse it with the chamber. The FBX stays Closed; Open is made in the prefab.
- No belts, chains, hoses, drive shafts, bolts, logos; rods only as chunky simple cylinders ≥ 0.04 m.
- Do not make the chamber an octagonal box: it must read as a round drum (16 segments), about Ø1.8.
- Wheels not merged with the body; tyres sit on Y = 0; no floating parts; no coplanar overlaps (≥ 1 mm offset).
- Do not exceed 5000 tris without a recorded note; flat shading only.

## Builder notes

<!-- The builder keeps round notes in .work/models/FarmMachinery/HRV-02_Baler_Round/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
