# STR-01 Arch_Wood — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/STR-01.png  (selected 2026-11-25, Э6 batch 1)

## Catalogue

Line: STR-01 · Rose arch, wooden · `FMS_Garden_Arch_Wood` · atlas A `Garden_Build` · prefab prefix `FMS_Garden_`.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.6×0.7×2.4 (top beams 1.6 wide, post outer faces ±0.72) | 1000 (`_Gate` 1300) | no | no | `_White` (colour: same mesh, UV to slot 10), `_Gate` (mesh: white arch + `Gate_Leaf`) |

Opening 1.2 wide × 2.1 high. Preview shows the base model only (light wood, no leaf); build the variants from the same script.

## Parts

Pivot of the model: centre of the footprint on the ground (Y = 0), root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Posts (4) | Wooden posts (shared construction): square 0.12×0.12, X = ±0.66, Z = ±0.24 centres, Y 0 → 2.22, faceted, 0.01 bevel on long edges. Inner faces at X = ±0.60 | 0 light wood (`_White`: 10) | static |
| Side lattice panels (2) | One per side, in the YZ plane, 0.6 deep (Z ±0.30 incl. posts), Y 0.15 → 2.10. Lattice (shared construction): diagonal slats crossing at 45°, about 0.03 m square, real open gaps of about 0.10 m between the slats, closed by a flat frame rim about 0.05 m wide. Real gaps, not a texture | 0 (`_White`: 10) | static |
| Lintels (2) | Front and rear beams along X between the post outer faces, 0.12 wide × 0.12 high, Y 2.10 → 2.22, Z = ±0.24 | 0 (`_White`: 10) | static |
| Purlins (2) | Along Z, 0.08×0.08, Y 2.22 → 2.30, X = ±0.66, length 0.70 | 0 (`_White`: 10) | static |
| Top cross-beams (5) | Along X, 1.6 long, 0.07 wide × 0.10 high, Y 2.30 → 2.40, at Z = −0.30, −0.15, 0, 0.15, 0.30; overhang 0.08 past the post outer faces; end faces in the dark slot | 0 (`_White`: 10); end faces 1 dark wood (`_White`: also 10) | static |
| Empties `Plant_L`, `Plant_R`, `Plant_Top` | Empty objects: `Plant_L` at (−0.66, 0, 0), `Plant_R` at (+0.66, 0, 0) (ground, centre of side panel), `Plant_Top` at (0, 2.40, 0) | — | for compositions (checked at assembly) |
| `Gate_Leaf` (only `_Gate`, +300 tris) | One white leaf 1.1 m wide, 0.05 thick, Y 0.10 → 1.60: straight side stiles 0.06 wide up to Y 1.05, then a semicircular top (radius 0.55, 12 segments) with a curved top rail. Lower half: 5 vertical boards 0.10 wide with 0.02 gaps. Upper half: the shared lattice (45° slats ~0.03, gaps ~0.10) inside the arch rim. Two small hinge straps and a latch plate as flat bars (dark iron) | 10 white; hinge straps and latch 13 wrought iron | Pivot on the hinge axis at the LEFT post inner face (X = −0.59, Z = 0, Y = 0), rotation axis Y, closed 0°, open up to 100° toward the front (+Z). Gap to the right post ≥ 0.05 |

Variant slots: `_White` re-maps every light-wood part to slot 10; `_Gate` is white (slot 10) with iron hinges. Parts of `_Gate` must not overlap the posts at 0°.

## Anchor

Within this pack: none before this model; STR-01 is the anchor for the lattice and posts of STR-03 and STR-07. Earlier packs: Farm Yard `FMS_Fence_Gate` / `FMS_Fence_Picket` (wood thickness only; превью нет в ветке).

## What NOT to do

- Do not make a curved or rounded top; the top is flat with cross-beams (the rounded shape belongs only to the gate leaf).
- Do not paint lattice as a texture or fill it with a solid panel: the gaps are real geometry and the lattice runs edge to edge, ending in the rim.
- Do not add a gate leaf to the base or `_White` models; only `_Gate` has `Gate_Leaf`.
- No floating beams: purlins sit on lintels, cross-beams sit on purlins; no coplanar overlapping faces (offset ≥ 1 mm).
- No thin posts (< 0.10), no roses or foliage on the arch (plants are separate PLT models), no chains or nails.
- Do not make the opening narrower than 1.2 or lower than 2.1.
- Do not add a ground plate under the arch.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
