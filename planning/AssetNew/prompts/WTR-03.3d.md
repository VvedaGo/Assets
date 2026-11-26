# WTR-03 Birdbath — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/WTR-03.png  (selected 2026-11-25, Э6 generation 2)

Pilot of the pack (simple type): this model fixes the stone, the facets and the palette A for WTR-01, WTR-02, ORN-01, ORN-03. Build it exactly to these numbers; deviations go to `spec.md`.

## Catalogue

Line: WTR-03 Поилка для птиц `FMS_Garden_Birdbath`, atlas A `Garden_Build`, material `M_Garden_Build`. Silhouette difference from duplicates (Farm Yard `FMS_Birdhouse`, `FMS_Dovecote`): a different object, a bowl on a pedestal, no house.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.6×0.85 | 350 (estimate of the parts below: ~300) | no | no | none |

Single static mesh, one material, no moving parts. Pivot: centre of the plinth base on the ground (Y = 0), root scale 1, rotation 0, Y up. Axis-symmetric, 10 segments on every round part (all rings share the same 10 angles, first vertex on +X).

Shared wording, stone: pale limestone main `#C9C3B6` (slot 11), warm grey stone `#A7A39A` (slot 12) as second tone for plinths and inner faces only; chunky faceted forms, flat shading, bevel 0.01–0.02 on large edges only, none on small parts; no cracks, moss, carving or text.
Shared wording, water: opaque flat blue `#4A78A8` (slot 15); plain flat disc, no transparency, no ripples, splashes, droplets or foam; no separate material.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Plinth | 10-sided prism Ø0.40, Y 0–0.08, top edge chamfer 0.015; no bottom face (~50 tris) | 12 stone `#A7A39A` | static, pivot at its base centre = model pivot |
| Foot | frustum Ø0.34 at Y 0.08 → Ø0.22 at Y 0.16 (~20 tris) | 11 limestone `#C9C3B6` | static |
| Lower stem | frustum Ø0.22 at Y 0.16 → Ø0.16 at Y 0.30 (~20) | 11 | static |
| Knob | ring bulge: Ø0.16 at Y 0.30 → Ø0.24 at Y 0.36 → Ø0.16 at Y 0.42 (two frustums, ~40) | 11 | static |
| Waist | straight prism Ø0.16, Y 0.42–0.54 (~20) | 11 | static |
| Collar | frustum Ø0.16 at Y 0.54 → Ø0.30 at Y 0.66, flat ledge on top (~30) | 11 | static |
| Bowl underside | frustum Ø0.30 at Y 0.66 → Ø0.60 at Y 0.80 (~20) | 11 | static |
| Rim wall | vertical prism Ø0.60, Y 0.80–0.85 (~20) | 11 | static |
| Rim top | flat annulus, outer Ø0.60 → inner Ø0.52 at Y 0.85 (~20) | 11 | static |
| Inner wall | two sloping rings: Ø0.52 at Y 0.85 → Ø0.47 at Y 0.83 (water line) → Ø0.34 at Y 0.78; no floor disc needed (~40) | 12 stone `#A7A39A` (inner face second tone) | static |
| Water | flat 10-gon disc Ø0.47 at Y 0.83, its edge vertices exactly on the inner wall ring (10 tris) | 15 water `#4A78A8` | static |

Colour split: plinth and inner wall in slot 12, everything else stone in slot 11, water slot 15. Three palette cells only.

## Anchor

Closest approved model: none in this pack yet. This is the stone anchor for the pack (WTR-01, WTR-02, ORN-01, ORN-03 copy its stone). Earlier packs by name only: Farm Yard `FMS_Well` (stone scale), Farm Nature `FMS_Rock_M` (stone tone), превью нет в ветке. STYLE.md asks to compare `#A7A39A` against Nature rocks on this pilot.

## What NOT to do

- No birdhouse, roof, box, hole or perch; no birds or animals.
- No thin spindly pedestal: the narrowest part (waist) is Ø0.16, not thinner.
- No bowl floating above the pedestal: collar ledge, bowl underside and stem share edges.
- No rim wall around the bowl taller than 0.05; the bowl stays shallow (depth about 0.07 from the rim).
- No transparent or wavy water, no splash, no second water object, no separate material.
- No smoothing of normals, no more than 10 segments, no carving, text, moss or cracks.
- No coplanar overlap between the water disc and the inner wall, between rim top and wall.
- Do not exceed 350 tris or 0.6 m footprint.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
