# STR-06 Gazebo — 3D spec (Э5 → Э7)

Reference: planning/AssetNew/references/STR-06.png  (selected 2026-11-25, Э6 generation 2)

## Catalogue

Line: STR-06 · Hexagonal gazebo · `FMS_Garden_Gazebo` · atlas A `Garden_Build` · prefix `FMS_Garden_` · pilot (complex).

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 3.9×3.4×4.0 | 5000 | yes (LOD1 via `make_lod1.py`, 50% by parts) | no | — |

Catalogue check list for this pilot: opening, railings, shingled roof, LOD1, collider with a pass-through entrance.

## Parts

Pivot: centre of the hexagon at ground level (Y = 0), X = 0, Z = 0. Entrance faces +X. The bounding box is therefore asymmetric: X from −1.47 to +2.44 (roof apothem 1.47 at the back; front steps), Z ±1.70.

Assumed layout so that the 3.9×3.4 box is met (catalogue gives no breakdown): deck hexagon circumradius 1.55 with VERTICES on ±Z (apothem 1.34 on ±X); roof eave circumradius 1.70 (Z ±1.70 = 3.4, X back −1.47); steps 2 × 0.55 deep in front of the entrance face (front at X = 1.34 + 1.10 = 2.44) → X span 3.91. If it does not fit within ±5%, keep the hex and reduce the step depth.

| Part | Shape / how to build | Palette slot (atlas A) | Pivot / moving |
|---|---|---|---|
| Deck | Hexagonal prism, circumradius 1.55, Y 0.24 → 0.36 (top 0.36), 6 sides flat; plank joints as 3 shallow grooves optional (≤ 0.01) | 0 light wood | static |
| Deck skirt/plinth | Hexagonal prism Y 0 → 0.24, circumradius 1.50 (slightly inset), 6 sides | 1 dark wood | static |
| Steps (2) | Two boxes on the entrance face, width 1.40 (clear of the corner posts), outer step: X 1.89 → 2.44, top 0.12; inner step: X 1.34 → 1.89, top 0.24; the deck top 0.36 is the third rise, so every rise is 0.12; each step 0.55 deep; step risers dark | 0 treads, 1 risers | static |
| Posts (6) | Wooden posts (shared construction): square 0.14×0.14 at the six hexagon vertices of the deck (circumradius 1.45), Y 0.36 → 2.60 | 10 white paint | static |
| Ring beam | Hexagonal ring joining the post tops, 0.10 wide × 0.14 high, Y 2.46 → 2.60 | 10 | static |
| Railings (5 faces) | Rail height 0.90 above the deck: top rail 0.08 × 0.08 at Y 1.18-1.26 (between the post faces), bottom rail 0.08 × 0.08 at Y 0.46-0.54, balusters 0.05 × 0.05, one every 0.15 m (about 8 per face), real gaps. The entrance face has NO rail | 10 | static |
| Benches (3) | One along each of the 3 back faces inside: plank seat 0.40 deep × 0.05 thick, top at Y 0.36 + 0.45 = 0.81, on two or three 0.06 × 0.40 legs, ends cut flush against the posts (no collision with posts) | 0 seat, 10 legs | static |
| Roof | Hexagonal hip: eave circumradius 1.70 at Y 2.60, peak at Y 3.62, 6 triangular faces. Shingles: rows of tiles 0.20 high, each row offset half a tile from the previous, 5-6 rows per face, alternating two tones in a row (`#9C3F33` / `#A8372E`); real stepped lower edges (each row slightly stands out 0.015); peak cap hexagonal | 14 brick red, 6 dark red | static |
| Hip ribs (6) | Ridge beams on the six hips, 0.08 wide, white | 10 | static |
| Roof underside | Hexagonal flat ceiling Y 2.60, plus six rafter beams under the hips (0.08 × 0.10) toward the centre, white; this keeps the interior closed to view from below | 10 | static |
| Spire | Iron rod Ø0.06 8-sided from Y 3.62 → 3.88, a ball Ø0.14 icosphere (subdiv 1) on top to Y 4.0 | 13 wrought iron | static |

Collider note (for Э8): the deck, steps and the six posts block; the entrance face has a clear opening ≥ 1.40 wide and 2.1 high; do not generate a convex-hull collider.

## Anchor

Within this pack: none yet — STR-06 is the pilot for wood, white paint and roof; STR-01 (post wording) and the shingle tones are shared by wording. Earlier packs by name: Farm Yard `FMS_House` (shingle roof, rows with offset and two tones; the method to repeat, not the shape), Farm Yard `FMS_Shed` / `FMS_Coop` / `FMS_Dovecote` (closed buildings; this model is open and must read differently) — превью нет в ветке.

## What NOT to do

- No walls, no windows, no door; only railings. The entrance face is completely open.
- Do not model shingles as a texture: rows of tiles with an offset and a visible stepped lower edge, two tones.
- No railing around the steps; no handrail across the entrance.
- No thin posts (< 0.10) and no balusters thinner than 0.04.
- Do not float the roof: posts reach the ring beam; deck and plinth must not share coplanar faces (offset ≥ 1 mm).
- No benches blocking the entrance; no plants, lanterns, weathervane animals, glass.
- Do not smooth the roof normals; flat faces.
- Do not exceed 5000 tris; LOD1 must keep the posts, ring beam, roof, deck and steps and drop balusters in groups, not remove the silhouette.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->
