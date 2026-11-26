# ORN-01 Sundial — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/ORN-01.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: ORN-01 Солнечные часы `FMS_Garden_Sundial`, atlas A `Garden_Build`, material `M_Garden_Build`. No duplicate in the series; silhouette is a square column with a round dial, kept distinct from the round baluster birdbath WTR-03.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.45×0.45×0.95 | 400 | no | no | none |

Static, no moving parts. Pivot: centre of the plinth base on the ground (Y = 0), root scale 1, rotation 0, Y up. Dial plate 12 segments (first vertex on +X); the square parts are axis-aligned boxes.

Shared wording, stone: pale limestone main `#C9C3B6` (slot 11), warm grey stone `#A7A39A` (slot 12) as second tone for plinths and inner faces only; chunky faceted forms, flat shading, bevel 0.01–0.02 on large edges only, none on small parts; no cracks, moss, carving or text.
Shared wording, wrought iron: dark `#3A3A3F` (slot 13) matte paint; rods are 8-sided, Ø ≥ 0.03 m; scrolls are a swept 8-sided rod; no bevel, no gloss, no chain links.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Plinth | box 0.40 × 0.40 × 0.10, Y 0–0.10, top edge chamfer 0.015, no bottom face (~30) | 12 stone `#A7A39A` | static, model pivot at its base centre |
| Base moulding | box 0.30 × 0.30 × 0.06, Y 0.10–0.16 (~12) | 11 limestone `#C9C3B6` | static |
| Shaft | box 0.22 × 0.22 × 0.59, Y 0.16–0.75, vertical edges chamfer 0.01 (~40) | 11 | static |
| Capital | box 0.34 × 0.34 × 0.07, Y 0.75–0.82, edge chamfer 0.015 (~30) | 11 | static |
| Dial plate | 12-gon disc Ø0.45, thickness 0.03, Y 0.82–0.85, flat top, centred; overhangs the capital 0.055 (~50) | 7 metal `#8E959B` | static |
| Dial rim | low ring Ø0.45 → Ø0.40, height 0.02, Y 0.85–0.87 (~48) | 7 | static |
| Hour ribs | 12 raised ribs 0.03 wide × 0.05 long × 0.02 high, radial at 30° steps just inside the rim, at Y 0.85–0.87 (~96) | 8 metal dark `#6E757B` | static |
| Gnomon | triangular blade extruded 0.03 thick: base 0.14 along the 12 o'clock axis (+Z), apex above the dial centre at Y 0.95, hypotenuse falling toward the 6 o'clock side; sits on a small 0.05 × 0.05 × 0.02 foot; total top Y = 0.95 (~40) | 13 iron `#3A3A3F` | static |

Sum about 350 tris, up to 400.

## Anchor

Closest approved model: WTR-03 (this pack, pilot, preview/spec not yet approved) for the stone wording and the palette A stone slots. Earlier packs by name only: Farm Yard `FMS_Well` (stone scale), превью нет в ветке.

## What NOT to do

- No numerals, letters, engraved text or zodiac symbols; hour marks are plain ribs only.
- No thin gnomon wire: the blade is 0.03 thick, ≥ 0.10 tall.
- No round baluster shaft (that is the birdbath) and no bowl; the shaft is square.
- No tilted dial plate: it is horizontal, centred on the capital.
- No brass or glossy metal; metal is matte slots 7 / 8, iron slot 13.
- No ribs overlapping the rim in a coplanar way: ribs sit inside the rim ring, tops 0.00–0.02 above the plate with no shared faces.
- No coplanar overlap between capital top and dial underside (offset ≥ 1 mm or share edges).
- Do not exceed 400 tris or the 0.45 × 0.45 footprint.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
