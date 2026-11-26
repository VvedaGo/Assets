# MOD-07 Pond Edge — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-07.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.0×0.37×0.45 | ≤ 120 | no | no | none |

## Parts

| Wall | Box X ±0.5, Z 0…−0.35, Y 0…0.40. Inner face (Z = 0) perfectly flat, no relief. Outer face carries 2 courses of 2 blocks of different lengths, staggered, standing 0.01 proud (outer face at Z −0.35, core at Z −0.34). Ends flat on X = ±0.5. | A-12 Stone `#A7A39A` (main), A-11 Stone light `#C9C3B6` (second tone, about one block in four) | Pivot: middle of the inner face at ground level (X 0, Y 0, Z 0) |
| Coping slab | Box X ±0.5, Z 0…−0.37 (flush with the inner face, overhanging the outer face by 0.02), Y 0.40…0.45. Bevel 0.015 on the outer long top edge only; end edges sharp. | A-11 Stone light `#C9C3B6` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 4: formal pond, internal grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Edge MOD-07: length 1.0 (X from −0.5 to +0.5). Inner face on Z = 0 (a grid line); outward to Z = −0.35; the coping projects outward another 0.02. Top at 0.45 (water 7 cm lower). Pivot: middle of the inner face at ground level.
- The inner face coincides with the edge of the MOD-09 water plates (gap 0). Ends are on grid nodes; adjacent edges butt end to end; the corner piece MOD-08 butts onto the last edge.
- A pond of N×M cells = N·M water plates + 2·(N+M) edges + 4 corners (example 3×2 = 6 + 10 + 4).
- Checks: ends on nodes; inner face of the edge = edge of the water (gap 0); water top is 0.07 below the edge top; no coincident top faces between neighbouring parts.


## Anchor

Closest approved model in this pack: MOD-03 Low Stone Wall (stone blocks, limestone cap wording) and WTR-03 Birdbath (stone tones), if approved. Earlier packs: Farm Nature `FMS_Water_Pond_Round` is the natural pond this must not look like (превью нет в ветке).

## What NOT to do

- Do not put relief or blocks on the inner face (Z = 0): it must be a flat plane that meets the water edge exactly.
- Do not exceed Z −0.37 or Y 0.45, or make the coping flush on the outer side: it overhangs by 0.02.
- Do not model water, a bottom or a liner inside the edge; the water is MOD-09.
- Do not round or bevel the end edges of the coping; sections must butt without notches.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
