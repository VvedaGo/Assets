# WTR-02 Wall Fountain Stele — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/WTR-02.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: WTR-02 Настенный фонтан-стела `FMS_Garden_Fountain_Wall`, atlas A `Garden_Build`, material `M_Garden_Build`. Silhouette difference from duplicates (Farm Yard `FMS_Well`, `FMS_Trough_Water`): flat tall stele with a spout and a half-round basin; no timber shaft, no trough.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.9×0.6×1.3 | 900 | no | no | none |

Static, no moving parts. Pivot: centre of the back face of the stele on the ground (X = 0, Z = 0 at the back face, Y = 0); the basin extends to +Z. Stands against MOD-03 or alone; when placed at the wall the back face sits 0.22 from the wall axis (catalogue, module section 2), so the back face must be exactly flat with no protruding parts. Root scale 1, rotation 0, Y up.

Shared wording, stone: pale limestone main `#C9C3B6` (slot 11), warm grey stone `#A7A39A` (slot 12) as second tone for plinths and inner faces only; chunky faceted forms, flat shading, bevel 0.01–0.02 on large edges only, none on small parts; no cracks, moss, carving or text.
Shared wording, water: opaque flat blue `#4A78A8` (slot 15); plain flat disc, no transparency, no ripples, splashes, droplets or foam; no separate material.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Stele slab | box 0.70 × 0.15 × 1.18 (Z 0–0.15, X ±0.35, Y 0–1.18), bevel 0.015 on front edges only, back face flat (~30) | 11 limestone | static |
| Stele cap | wider cap 0.80 × 0.19 × 0.12 at Y 1.18–1.30 with a low gabled top (ridge along X, 0.04 rise inside the total 1.3), overhangs 0.05 each side and front (~40) | 11 | static |
| Medallion | 12-sided disc Ø0.28, 0.03 thick, on the slab front at Y 0.88 centre, Z 0.15–0.18 (~48) | 12 stone | static |
| Spout | 8-sided pipe Ø0.08, length 0.12 from the slab front at Y 0.74 (centre), Z 0.15–0.27, tip faces +Z, short collar Ø0.12 × 0.02 at the base (~50) | 7 metal `#8E959B` | static |
| Basin drum | half-cylinder, 12 segments over 180° (radius 0.45, centre at Z 0.15), Y 0–0.50; plinth on its foot Y 0–0.06 in slot 12; flat back against the stele (~120) | 11, foot 12 | static |
| Basin coping | half-annulus ring on the drum, Y 0.50–0.55, outer R 0.45, inner R 0.34, chamfer 0.015 (~60) | 11 | static |
| Basin inner wall | half-ring slope from R 0.34 at Y 0.55 down to the water line R 0.30 at Y 0.46 (~24) | 12 | static |
| Water | flat half-disc, 12-gon halved, R 0.30 at Y 0.46, edge exactly on the inner wall (12 tris) | 15 water | static |
| Stream | one flat ribbon 0.05 wide × 0.02 thick from the spout tip (Z 0.27, Y 0.74) bending outwards by 0.03 and falling straight down to the water, 3 segments (~30); one face row in slot 9 `#A9AFB4` | 15, highlight 9 | static |

Sum is about 420 tris; up to 900 allowed. Spend extra on cleaner arcs and chamfers, not on detail under 0.03 m.

## Anchor

Closest approved model: WTR-03 (this pack, pilot, preview/spec not yet approved) for stone wording, facets and water. Earlier packs by name only: Farm Yard `FMS_Well` (stone scale), превью нет в ветке.

## What NOT to do

- No splashes, spray, droplets, foam; no transparent or wavy water; no particles.
- No wall, no brick backdrop, no pipes or tank behind: the back face is a plain flat plane at Z = 0.
- No lion head, face, relief figure, text or carving; the medallion is a plain disc.
- No thin pencil jet: the stream is a flat ribbon ≥ 0.05 wide.
- No rounded back; no part may protrude behind Z = 0.
- No basin floating off the stele: the drum is flush with the front face.
- No full round basin: it is exactly a half drum.
- No coplanar overlap between water half-disc and the inner slope; water stays 0.09 below the coping top.
- Do not exceed 900 tris.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
