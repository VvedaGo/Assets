# ORN-02 Garden Gnome — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/ORN-02.png  (selected 2026-11-25, Э6 batch 3)

## Catalogue

Line: ORN-02 Садовый гном `FMS_Garden_Gnome` (+ variant `FMS_Garden_Gnome_Blue`), atlas A `Garden_Build`, material `M_Garden_Build`. Silhouette difference from duplicates (Farm Yard `FMS_Scarecrow_Classic`, `_Pumpkin`): a 0.45 m statuette with a cone hat; the scarecrow is a life-size figure on a pole. A statuette, not a character: no facial expression.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.25×0.25×0.45 | 600 | no | no | `_Blue` (colour: blue hat, red jacket) |

Static, no moving parts. Pivot: centre between the boots on the ground (Y = 0), root scale 1, rotation 0, Y up; the figure faces +Z. Round parts < 0.3 m use 8 segments; spheres are icospheres, 1 subdivision (visible facets).

## Parts

| Part | Shape / how to build | Palette slot | Pivot / moving |
|---|---|---|---|
| Boots | 2 stubby blocks 0.07 × 0.10 × 0.05 (toes toward +Z), X = ±0.04, Y 0–0.05, small chamfer 0.01 (~30) | 1 dark wood `#7A5233` | static, model pivot between them at ground |
| Body | 8-sided tapered prism Ø0.18 at Y 0.05 → Ø0.14 at Y 0.22, slightly rounded belly bulge on the front (~60) | 15 water blue `#4A78A8` (base jacket) | static |
| Belt | 8-sided band Ø0.19, Y 0.115–0.135 (~16) | 13 iron `#3A3A3F` | static |
| Arms | 2 chunky tapered 6-sided prisms Ø0.04, hanging along the body then forward to the belly, X = ±0.09 (~50) | 15 | static |
| Hands | 2 icospheres Ø0.045 at the belly front (~80) | 3 cream `#F2E6C9` | static |
| Head | icosphere Ø0.13 centred at Y 0.25, mostly hidden under hat and beard (~80) | 3 cream | static |
| Nose | icosphere Ø0.05, protruding 0.07 in front of the head at Y 0.255 (~80) | 3 cream | static |
| Beard | faceted wedge hanging from the lower head to the belt, 0.12 wide × 0.06 deep × 0.12 high, 5–6 facets pointing down, a few tuft facets (~70) | 10 white `#EEEDE7` | static |
| Hat | 8-sided cone: base Ø0.17 at Y 0.27, apex at Y 0.45, apex bent 0.02 backwards; short brim ring 0.01 high (~70) | 5 red `#C8473B` | static |

Sum about 540 tris, up to 600. Hat covers the eyes (no eyes modelled); only the nose breaks the face.

### Variant `_Blue` (colour)

Same mesh, UV reassigned only: hat to slot 15 `#4A78A8`; body and arms to slot 5 `#C8473B`. Separate FBX and prefab, no new material, no geometry change.

## Anchor

Closest approved model: none in this pack. Earlier packs by name only: Farm Yard `FMS_Scarecrow_Classic` (hat colour and chunk scale), превью нет в ветке.

## What NOT to do

- No facial expression: no eyes, mouth, eyebrows; only the nose.
- No tools, fishing rod, lantern, wheelbarrow, mushroom seat or pedestal; he stands on his own boots.
- No thin limbs: arms ≥ 0.04, hat apex still ≥ 0.03 wide at its tip (do not collapse to a needle).
- No smooth sphere clouds for the beard: faceted wedge with visible facets.
- No floating hands, nose or beard: all touch the body or head.
- No glossy paint, gradients, text or shading tricks; flat palette cells only.
- Do not exceed 600 tris or 0.45 m height; `_Blue` is the same mesh with UV remapped only.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
