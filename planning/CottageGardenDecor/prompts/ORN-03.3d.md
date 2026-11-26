# ORN-03 Stone Urn on Pedestal — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/ORN-03.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: ORN-03 Каменная урна на пьедестале `FMS_Garden_Urn` (+ variant `FMS_Garden_Urn_Planted`), atlas F `Garden_Flora` (the stone exists in F), material `M_Garden_Flora`. Silhouette difference from duplicates (Farm Market `FMS_Deco_Pot_Small/Medium/Large/Empty`, `FMS_Comp_FloralPlanterStand`): stone goblet on a square pedestal 1.2 m tall; Market pots are low terracotta 0.3–0.6 m.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.6×0.6×1.2 | 700 (`_Planted` 1300) | no | no | `_Planted` (mesh: drooping flowers) |

Static, no moving parts. Pivot: centre of the plinth base on the ground (Y = 0), root scale 1, rotation 0, Y up. Urn 12 segments (first vertex on +X), pedestal parts axis-aligned boxes.

Shared wording, stone (atlas F slots): pale limestone main `#C9C3B6` (F slot 15, same HEX as A-11), warm grey stone `#A7A39A` (F slot 14, same HEX as A-12) as second tone for plinths and inner faces only; chunky faceted forms, flat shading, bevel 0.01–0.02 on large edges only, none on small parts; no cracks, moss, carving or text.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Plinth | box 0.50 × 0.50 × 0.12, Y 0–0.12, top edge chamfer 0.015, no bottom face (~30) | F14 stone `#A7A39A` | static, model pivot at its base centre |
| Pedestal shaft | box 0.30 × 0.30 × 0.58, Y 0.12–0.70, vertical edges chamfer 0.01 (~40) | F15 limestone `#C9C3B6` | static |
| Pedestal cap | box 0.40 × 0.40 × 0.06, Y 0.70–0.76, edge chamfer 0.015 (~30) | F14 | static |
| Urn foot | frustum Ø0.28 at Y 0.76 → Ø0.20 at Y 0.82 (12 sides, ~24) | F15 | static |
| Urn stem | prism Ø0.18, Y 0.82–0.88 (~24) | F15 | static |
| Urn belly | lathe: Ø0.18 at Y 0.88 → Ø0.50 at Y 0.98 → Ø0.52 at Y 1.04 (max belly) → Ø0.38 at Y 1.12 (neck) (~100) | F15 | static |
| Urn lip | flared thick lip: Ø0.38 at Y 1.12 → Ø0.60 at Y 1.17 → vertical Ø0.60 to Y 1.20, flat top ring Ø0.60 → 0.50 at Y 1.20 (~80) | F15 | static |
| Urn inner wall | slope Ø0.50 at Y 1.20 → Ø0.46 at Y 1.14 (~24) | F14 | static |
| Soil | flat 12-gon disc Ø0.46 at Y 1.14, edge on the inner wall (12) | F12 soil `#805433` | static |

Sum about 365 tris, up to 700. Spend extra on cleaner profile rings and chamfers.

### Variant `_Planted` (mesh, extra geometry on the same atlas F, budget 1300)

Same urn plus (up to ~600 extra tris), from primitives only, no cards:

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Foliage mound | 3–4 displaced icospheres (faceted leaf clusters, 1 subdivision) heaped in the urn opening, Ø0.15–0.25 each, total mound up to Y 1.4 (above the lip) (~200) | F0 `#6E9F4A`, F2 `#4E7A3A`, F1 `#8AB257` alternating by faces | static |
| Drooping stems | 6–8 stems as 8-sided rods Ø0.03, arcing over the lip and hanging down the urn belly to Y 0.85–0.95, kept within the 0.6 footprint (~120) | F13 `#7A5233` | static |
| Hanging blooms | 8–10 cup-shaped blooms Ø0.08–0.10 at the stem ends and along the arc, with 2–3 small leaf clusters on the stems (~240) | F6 `#E58FA0`, F7 `#F2B8C2`, F8 `#F4F1E8`; centres F11 `#E8B83A` | static |

Planted height may exceed the base 1.2 (assumed up to about 1.4 with the foliage); the footprint stays 0.6 × 0.6. Blooms hang free of the pedestal.

## Anchor

Closest approved model: WTR-03 (this pack, pilot, preview/spec not yet approved) for the stone wording and facets (A slots 11/12 = F slots 15/14). For `_Planted` flora: PLT-01 (this pack, pilot, not yet approved). Earlier packs by name only: Farm Market `FMS_Deco_Pot_Large` (scale comparison), превью нет в ветке.

## What NOT to do

- No terracotta, no pot on the ground, no saucer, no handles, no relief carving, text or moss.
- No thin pedestal: the shaft is 0.30 wide, not narrower.
- No urn floating over the pedestal: foot rests on the cap block.
- Base model has NO plants and no flowers: only the soil disc. Plants exist only in `_Planted`.
- `_Planted`: no alpha cards or single-plane leaves, no smooth sphere clouds, no flowers outside the 0.6 footprint, no thin rods under Ø0.03.
- Use only atlas F cells; do not introduce atlas A cells (one model = one material).
- No coplanar overlap between soil disc and inner wall.
- Do not exceed 700 tris (`_Planted` 1300).

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
