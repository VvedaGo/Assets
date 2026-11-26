# PLT-05 Wisteria Drape — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/PLT-05.png  (selected 2026-11-26, Э6 batch 4)

Atlas F `Garden_Flora`, material `M_Garden_Flora`. Leaf cluster and stem helpers from the approved pilot PLT-01; raceme is its own generator.

## Catalogue

PLT-05 Глициния, свисающая гроздь `FMS_Garden_Wisteria_Drape` — pivot on the top face (hangs under a pergola beam at 2.24 m), 7–9 cone racemes, lilac/white. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 1.5×0.6×0.9 | 900 | no | no | none (racemes: 6 lilac + 2 white inside the one mesh) |

Counts: 2 vines, 8 leaf clusters, 8 racemes. Estimate: vines 2×~60 = 120 + clusters 8×~45 = 360 + racemes 8×~36 = 290 → about 770.

## Parts

Axes: X along the beam (1.5), Z across (0.6), Y up. Pivot at the centre of the TOP face: (0, 0, 0). The top plane Y = 0 is the ATTACHMENT PLANE (flat, horizontal); all geometry has Y ≤ 0, hanging to Y = −0.90. Hung under the beam: pivot placed at Y 2.24 (beam underside), so the lowest tip is at 1.34 m above the ground. Root scale 1, rotation 0.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Vines ×2 | 8-sided prism Ø0.05, 5 segments each (~60 tris), along X from −0.75 to +0.75 at Y −0.03 to −0.07 (upper face clipped flat at Y = 0), weaving around each other in Z (±0.08) | 13 bark `#7A5233` | none |
| Leaf clusters ×8 | LEAF CLUSTER (shared wording, see PLT-01), Ø0.22–0.28, scaled (1.0, 0.6, 0.9), top cut flat at Y = −0.005 (flattened against the beam), ~45 tris; X −0.65…+0.65 evenly (step ~0.19), Z ±0.12 alternating; they sit at Y −0.02…−0.16 and never cover the racemes' roots completely | 0 side, 1 up, 2 down | none |
| Racemes ×8 | Inverted cone made of 2 stacked 6-sided frusta + a 6-sided tip cone (~36 tris incl. a 6-tri top cap). Top Ø0.14 at Y −0.04, taper to a point. Lengths (down to) 0.90, 0.60, 0.80, 0.50, 0.70, 0.45, 0.85, 0.55 for X = −0.65, −0.46, −0.28, −0.09, +0.10, +0.28, +0.46, +0.65; Z ±0.20 alternating front/back; hang vertical with ±5° tilt; stem stub 6-sided Ø0.025 connecting the raceme top to the vine (≥ 0.02 long). Racemes never touch each other (gap ≥ 0.04 at the widest point) | 9 lilac `#A58BC9` for racemes 1–6 (every 3rd facet of the lower section slot 8 `#F4F1E8` for liveliness); 8 white `#F4F1E8` for racemes at X −0.09 and +0.46 (all facets); stub slot 13 | none |

Mounting (from the catalogue, keep true): STR-04 pergola beams are 0.10×0.22 along X at Z = ±1.5, underside Y 2.24; the drape's 1.5 length runs along the beam (beam length 3.5, bay 3.0), 0.6 depth straddles the 0.10 wide beam. CMP-02 hangs 4 of them (PLT-05 ×4), placed by pivot under the beam.

## Anchor

Closest approved model: PLT-01 `FMS_Garden_Rose_Bush` (same pack; shared leaf cluster helper, tone of foliage). By name only (preview not in this branch): Farm Nature `FMS_Bush_Flowering`.

## What NOT to do

- No alpha cards, no single-plane leaves, no strings of thin petals, no transparent material; racemes are chunky closed faceted cones.
- Nothing above Y = 0; the top is flat and flush; do not model the beam.
- No smooth blobs or smooth cones: 6-sided facets visible, flat shading.
- No more than 2 white racemes; no colours outside atlas F cells 8, 9 (+ foliage 0–2, bark 13).
- No floating racemes (each stub touches a vine); no coplanar overlaps.
- Do not exceed 900 tris; no petals/flowers as separate micro-meshes.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
