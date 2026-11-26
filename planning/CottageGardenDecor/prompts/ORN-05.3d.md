# ORN-05 Shepherd's Hook with Hanging Basket — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/ORN-05.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: ORN-05 Кованый крюк с подвесной корзиной `FMS_Garden_Shepherd_Hook` (+ variant `FMS_Garden_Shepherd_Hook_Feeder`), atlas F `Garden_Flora`, material `M_Garden_Flora`. Silhouette difference from duplicates (Farm Market `FMS_Deco_Lantern_Hanging`; Farm Yard `FMS_Birdhouse`): thin wrought-iron crook with a scroll, a basket of flowers or a cylinder feeder hanging from it; no lantern.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.5×0.3×1.7 | 600 | no | no | `_Feeder` (mesh: bird feeder instead of the basket) |

Pole at X = −0.20, the arc reaches +X to X = +0.30; basket centred at X +0.14, diameter 0.28 (Z ±0.14). Pivot of the model: foot of the pole on the ground (X = −0.20, Y = 0), so the footprint box is X −0.22…+0.30, Z ±0.15; root scale 1, rotation 0, Y up.

Moving part: `Hanging` — pivot at the hanging point (the end of the hook curl, about X +0.14, Y 1.64), static in the pack (may be rotated by the user); it contains the 3 suspension rods and the basket with its plants (or the feeder).

Shared wording, wrought iron: dark `#3A3A3F` (F slot 10, same HEX as A-13) matte paint; rods are 8-sided, Ø ≥ 0.03 m; scrolls are a swept 8-sided rod; no bevel, no gloss, no chain links.

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Spike | 8-sided cone Ø0.035 → point, Y 0–0.20, tapering to 0.01 tip (~16) | F10 iron `#3A3A3F` | static, model pivot at ground |
| Pole | 8-sided rod Ø0.035, Y 0.10–1.45 (~36) | F10 | static |
| Footrest | short crossbar 8-sided Ø0.03 × 0.16 along X at Y 0.18 (~16) | F10 | static |
| Small scroll | S-curl swept 8-sided rod Ø0.03, radius 0.04, attached to the pole at Y 0.9, 6 segments (~48) | F10 | static |
| Arc and curl | swept 8-sided rod Ø0.035 bending from the pole top (Y 1.45) over a hook arc of radius ~0.18 to the end of the arm, ending in a curl of radius 0.05 at Y 1.64, X +0.14; ~14 path segments (~120) | F10 | static, hanging point at the curl end |
| Ring | 8-sided ring Ø0.06 at the hanging point (~32) | F10 | `Hanging` |
| Suspension rods | 3 rods Ø0.03 from the ring down to the basket rim, 120° apart, rod length ~0.25 (~48) | F10 | `Hanging` |
| Basket bowl | 8-segment faceted bowl, Ø0.28 at the rim (Y 1.32), Ø0.16 at the bottom (Y 1.22), flat rim ring 0.02 high, inner face visible (~64) | F13 `#7A5233` | `Hanging` |
| Basket foliage | 3 displaced icosphere leaf clusters, Ø0.12–0.16, mound up to Y 1.45, spilling over the rim (~120) | F0 `#6E9F4A`, F2 `#4E7A3A` | `Hanging` |
| Basket blooms | 6–7 cup blooms Ø0.08–0.10, 6-sided cups with centre faces (~90) | F6 `#E58FA0`, F7 `#F2B8C2`, F8 `#F4F1E8`; centres F11 `#E8B83A` | `Hanging` |

Estimated sum ~590 tris, up to 600. Iron parts keep the 2× budget allowance only if explained in `spec.md`; the overall target stays 600.

### Variant `_Feeder` (mesh, budget 600)

Basket, foliage and blooms are removed; the hook, ring and suspension rods stay. Added under `Hanging`:

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Feeder body | 8-sided cylinder Ø0.20, height 0.18, Y 1.10–1.28, with a square window opening 0.10 × 0.06 on the front exposing the grain (~60) | F13 `#7A5233` | `Hanging` |
| Feeder tray | 8-sided disc Ø0.26, 0.02 thick at Y 1.08–1.10 | F14 stone `#A7A39A` | `Hanging` |
| Grain | small heap inside the window, 2–3 faceted lumps (~24) | F11 yellow `#E8B83A` | `Hanging` |
| Feeder roof | 8-sided cone roof Ø0.30, 0.10 high, overhanging the body, Y 1.28–1.38, with a small peak knob (~40) | F12 soil `#805433` | `Hanging` |

The three rods end at the roof; the top of the roof joins them. Total ≤ 600 tris. Feeder is empty: no birds.

## Anchor

Closest approved model: none in this pack yet (the wrought-iron wording will be shared with STR-02, FUR-03, FUR-04 once those are approved). Earlier packs by name only: Farm Market `FMS_Deco_Lantern_Hanging`, `FMS_Deco_Lantern_Post` (hanging point and slender iron scale), превью нет в ветке.

## What NOT to do

- No chain links (STYLE.md): use rods; no rods thinner than Ø0.03; no real-life Ø0.015.
- No lantern, no birdhouse box, no wall bracket, no pot stand or saucer.
- No flat leaf cards or single-plane leaves; flora is faceted clusters and cup blooms only.
- No floating basket: the three rods connect ring and basket rim; the ring really sits on the hook curl.
- No glossy or bright metal; iron is matte `#3A3A3F`.
- Do not use atlas A cells: only atlas F (one model = one material).
- Do not move the pivot: the model pivot is the pole foot; `Hanging` pivot is the hanging point.
- Do not exceed 600 tris; `_Feeder` has no birds and no seed particles.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
