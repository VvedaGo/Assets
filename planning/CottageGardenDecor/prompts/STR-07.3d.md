# STR-07 Obelisk — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/STR-07.png  (selected 2026-11-25, Э6 batch 2)

## Catalogue

Line: STR-07 · Obelisk for climbers · `FMS_Garden_Obelisk` · atlas A `Garden_Build` · prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.6×1.9 | 500 | no | no | `_White` (colour: same mesh, UV to slot 10; separate FBX and prefab) |

## Parts

Pivot: centre of the footprint on the ground (Y = 0).

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Posts (4) | Wooden posts (shared construction, slimmer for this small object: square 0.08×0.08, still above the 0.03 minimum): lean inward from base centres (±0.26, ±0.26) to top centres (±0.05, ±0.05) at Y 1.70, tapered tops cut flat; the outer base box is 0.6×0.6 | 2 medium wood (`_White`: 10) | static |
| Bands (3) | Square rings 0.05 × 0.05 section at Y = 0.35, 0.85, 1.35, wrapping the outside of the four posts, size following the post taper (the bands touch the posts, do not hang in space) | 2 (`_White`: 10) | static |
| Collar | Small square block 0.14 × 0.14 × 0.10 at the top, Y 1.66 → 1.76, joins the four posts | 2 (`_White`: 10) | static |
| Ball finial | Icosphere subdivision 1 (faceted), Ø0.16, centre Y 1.82 (bottom slightly sunk into the collar), top exactly 1.90, centred | 2 (`_White`: 10) | static |

## Anchor

Within this pack: STR-01 (post and frame wording). Earlier packs by name: Farm Nature `FMS_Bed_Trellis` and `FMS_Bed_Stakes_Row` (flat trellis; this model must differ: a 3D four-sided pyramid, not flat) — превью нет в ветке.

## What NOT to do

- Do not make it a flat panel or a ladder; it is a four-sided pyramid seen the same from all sides.
- Do not add lattice between posts; the openings are empty.
- No smooth sphere on top: an icosphere with visible facets (subdivision 1-2).
- No floating bands or collar; no base plate, no spikes below Y = 0.
- No posts thinner than 0.08; no coplanar faces between band and post.
- Do not exceed 500 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Orchestrator note (2026-11-25, review models_2)
- Wood is palette slot 0 (same as STR-01, STR-04/05, STR-06), not slot 2; `_White` uses slot 10. Collar 0.19. Size as built 0.60×0.60×1.90.
