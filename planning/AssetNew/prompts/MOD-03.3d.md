# MOD-03 Low Stone Wall — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/MOD-03.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 2.0×0.44×0.60 | ≤ 600 | no | no | none |

## Parts

| Core | Box X ±1.0, Z ±0.19, Y 0…0.54. Ends exactly on X = ±1.0 (flat cut). | A-12 Stone `#A7A39A` | Pivot: centre of the base |
| Masonry blocks | 4 courses of about 0.135 m height, blocks of different lengths with staggered joints, standing 0.01 proud of the core on both long faces (outer faces at Z ±0.20). Blocks at the two ends are cut flush on X = ±1.0. Mostly slot A-12, about one block in four in the second tone A-11. Hidden faces removed. | A-12 Stone `#A7A39A` (main), A-11 Stone light `#C9C3B6` (second tone) | Part of the single mesh |
| Coping slab | Box X ±1.0 (length exactly 2.0), Z ±0.22 (0.44 wide), Y 0.54…0.60. Bevel 0.015 on the two long top edges only; the short end edges stay sharp so butted segments show no notch. | A-11 Stone light `#C9C3B6` | Part of the single mesh |

## Snap contract (from CATALOG «Модули и стыковка», item 2: low stone wall, grid 2.0 m)

1 unit = 1 m, Y up, pivot on the ground (Y = 0), root scale 1, rotation 0. Snap tolerance 0 +/- 1 mm; no overlapping identical faces in one plane (touching parts share an edge or are offset by at least 1 mm). The assembly script prints `SNAP OK` for each pair.

- Wall MOD-03: length exactly 2.0 (X from −1.0 to +1.0), thickness 0.40, coping 0.44 × 0.06, top 0.60. Pivot: centre of the base. Placed at the middle of a span (node + 1.0).
- Segments butt end to end; the masonry pattern at the ends is a plain flat cut. Wall lengths are multiples of 2 m only (no half segment).
- A MOD-04 pillar (0.50 × 0.50 × 0.80 + ball up to 1.05, pivot at the node) is mandatory at every corner and free end. At a corner the copings of two walls at the same height 0.60 overlap in a 0.2 × 0.2 square; the 0.50 pillar hides it completely. On a straight joint the pillar is optional.
- A doorway in the wall is a skipped segment between two pillars: clear width 1.5 m (the iron arch STR-02, 1.4 wide, fits).
- WTR-02 against the wall: the back face of the stele is 0.22 from the wall axis (touching the coping overhang).
- Checks: butt joint of the ends = 0; at a corner the coping overlap lies inside the pillar; the pillar faces (±0.25) do not coincide with the wall faces (±0.20 / ±0.22).


## Anchor

Closest approved model in this pack: WTR-03 Birdbath for the stone and limestone tones, if already approved. Earlier packs: Farm Nature `FMS_Rock_M` (stone tone, превью нет в ветке); Farm Yard `FMS_Well` (stone scale, превью нет в ветке).

## What NOT to do

- Do not make the wall taller than 0.60 or thicker than 0.40 (0.44 at the coping): it must stay a low garden wall, not a workshop wall.
- Do not let stones, mortar or the coping stick out past X = ±1.0 and do not stagger the ends: butted segments must meet with a flat joint.
- Do not model cracks, moss or rounded boulders; blocks are boxes in two flat tones with 0.01 relief.
- Do not put the coping or block tops in the same plane as a neighbouring face (coplanar overlap); the coping is on Y 0.54…0.60 exactly, above the core.
- Do not add a ground plane, base plate, grass or any scenery to the mesh (the pivot is on the ground, the mesh is only the piece).
- Do not change the dimensions, the pivot or the numbers of the snap contract above; the reference image never overrides them.
- Do not use smooth shading, bevels beyond those listed, normal maps, gradients or extra materials: one flat-palette atlas, one material.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
