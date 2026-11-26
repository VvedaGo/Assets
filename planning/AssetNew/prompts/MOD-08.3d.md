# MOD-08 Pond Edge Corner — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-08.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.37×0.37×0.45 | ≤ 60 | no | no | none |

## Parts

| Block | Box X 0…−0.35, Z 0…−0.35, Y 0…0.40; the two inner faces (X = 0, Z = 0) are flat, no relief. The two outer faces carry blocks standing 0.01 proud (1–2 courses, staggered, different lengths), same wording and tones as MOD-07. | A-12 Stone `#A7A39A` (main), A-11 Stone light `#C9C3B6` (second tone) | Pivot: the inner corner of the basin at ground level (X 0, Y 0, Z 0); the block extends towards −X and −Z |
| Coping slab | Box X 0…−0.37, Z 0…−0.37, Y 0.40…0.45: flush with the two inner faces, overhanging the two outer sides by 0.02. Bevel 0.015 on the two outer top edges only. | A-11 Stone light `#C9C3B6` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 4: formal pond, internal grid 1.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Corner MOD-08: block 0.35 × 0.35 × 0.45 outside the inner corner of the basin, plus a coping projection of 0.02 on the two outer sides (bounding box 0.37 × 0.37 × 0.45). Pivot: the inner corner of the basin at ground level.
- Orientation assumed to match MOD-07 (basin interior towards +Z of an edge piece): the corner sits at X ≤ 0, Z ≤ 0 around its pivot, and butts onto the end of a MOD-07 on its +X side (X = 0 face) and onto a MOD-07 rotated 90° on its +Z side (Z = 0 face). The assembly script rotates the corner for the other three corners.
- The inner faces touch the end faces of the adjacent MOD-07 pieces (gap 0); no coincident top faces between neighbouring parts.


## Anchor

Closest approved model in this pack: MOD-07 Pond Edge (same stone and coping wording; build MOD-07 first). Earlier packs: none.

## What NOT to do

- Do not fill the corner into a pillar or add a ball or taller cap: top stays at 0.45, same as MOD-07.
- Do not put relief on the two inner faces; they must stay flat so the neighbouring pieces and the water meet them with gap 0.
- Do not change the pivot: it is the inner corner of the basin, not the centre of the block.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Fix 1 (2026-11-25, review models_2)
- What is wrong: the outer faces carry one quoin stone per course (2 stones total: dark bottom, light top, 24 tris), so the corner reads as two stacked slabs under a cap. The spec asks for 1-2 courses of staggered blocks of different lengths on both outer faces, and the reference (and MOD-07 beside it) shows 2 blocks per course with visible joints; the corner does not continue the masonry.
- What to do: raise the tris budget 60 -> 80 (coordinator records it). Keep the shell (32 tris), the box 0.37 x 0.37 x 0.45, the pivot, the inner flat faces, courses z 0..0.194 and 0.206..0.394, block face at 0.35 (0.01 proud), blocks 6 mm short of the butt faces. Per course build 2 blocks (12 tris each, 4 x 12 = 48, total 80): one quoin wrapping the outer corner (about 0.21 long on the X face, 0.35 on the Y face) plus one face block of different length on the other side so joints do not align (pinwheel: the joint on the X face in the bottom course, on the Y face in the top course). Tones: bottom course quoin A-12 + face block A-11, top course quoin A-11 + face block A-12, so no two equal tones touch across the joint. Must not change: outer size, coping, bevels, snap faces, material, palette cells. Re-run the SNAP for edge|corner and the closed 2x2 and 3x2 ponds.
