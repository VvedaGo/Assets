# PLT-01 Rose Bush — 3D spec (Э5 → Э7)

Reference: planning/CottageGardenDecor/references/PLT-01.png  (selected 2026-11-25, Э6 generation 2)

PILOT (characteristic type): organic + atlas F + new pink colours. Its generator (leaf cluster, rose bloom, stem) is reused by PLT-02, PLT-03, PLT-06 and TOP-01_Rose; keep the helpers parametric and importable. Atlas F `Garden_Flora`, material `M_Garden_Flora`.

## Catalogue

PLT-01 Куст розы `FMS_Garden_Rose_Bush` — vase-shaped bush: 5–7 stems, 6–9 faceted leaf "drops", 9–12 cup blooms Ø0.08–0.10. Organic risk.

| Size W×D×H, m | Tris budget | LOD | Lite | Variants |
|---|---:|---|---|---|
| 0.8×0.8×1.0 | 1000 | no | no | 2 colour: `_Pink`, `_White` (same mesh, UV remapped to other atlas-F cells, separate FBX + prefab) |

Fixed counts for the pilot (do not drift): **6 stems, 8 leaf clusters, 10 blooms**. Estimated tris: stump 16 + stems 6×20 = 120 + clusters 8×~56 = 450 + blooms 10×34 = 340 → about 930.

## Parts

Axes: X width, Z depth, Y up; pivot at the centre of the stump base on the ground (Y = 0); root scale 1, rotation 0. Flat shading, no smoothing.

| Part | Shape / how to build | Palette slot (atlas F) | Pivot / moving |
|---|---|---|---|
| Stump | 8-sided short prism, Ø0.12 → Ø0.10, Y 0–0.10, no bottom cap needed beyond ground; 16 tris | 13 bark `#7A5233` | none; model origin |
| Stems ×6 | 6-sided tapered prism, Ø0.05 at the base → Ø0.035 at the tip, 2 segments with a kink at Y≈0.45 (20 tris each, open ends, tip capped). All leave the stump top at Y 0.10 spaced 60° apart (hexagonal), each leans outward 12°–28° from vertical (alternate 12/28 for irregularity), outer tip radius 0.28–0.36 at Y 0.80–0.95, so the silhouette is a vase: ~Ø0.2 at the base, widest Ø0.8 at Y≈0.75, Ø0.65 at the top. Stem lengths differ (tips at Y 0.80, 0.85, 0.90, 0.92, 0.95, 1.00 m); stems must touch the stump and the clusters/blooms they carry | 13 | none |
| Leaf clusters ×8 | LEAF CLUSTER (shared wording, see below). Ø0.22–0.30 (alternate 0.22/0.26/0.30). Two tiers: 3 lower at Y 0.35–0.50 (radius 0.12–0.22 from axis), 5 upper at Y 0.60–0.88 (radius 0.22–0.32). Each cluster is penetrated by a stem (centre on a stem); leave visible stem gaps ≥ 0.10 between tiers — the bush is NOT a closed ball | 0 (side faces), 1 (upward faces), 2 (downward faces) | none |
| Blooms ×10 | ROSE BLOOM (shared wording, see below). Distribution: 3 at the top rim (Y 0.90–1.00), 4 on the outer upper shell (Y 0.65–0.85, radius 0.30–0.36), 3 on the lower outer shell (Y 0.45–0.60, radius 0.25–0.30). Each on a 4-sided stalk Ø0.025, 0.04–0.08 long, bloom axis tilted 20°–45° outward from vertical. No two blooms touch. Blooms rise above the foliage — they are the signature feature | 4 outer cup, 5 inner bud, 13 stalk, 0 sepal (red base) | none |

**LEAF CLUSTER (shared wording, identical in PLT-01/02/03/06):** a faceted "drop" of foliage: ico sphere subdivision 1 (80 tris), vertices randomly displaced by ±0.03 (fixed seed), squashed to scale (1.0, 0.7, 1.0), lower third cut off flat, giving ~50–56 tris. Flat shading. Face colour by normal: facing up → slot 1 `#8AB257`, sideways → slot 0 `#6E9F4A`, facing down → slot 2 `#4E7A3A` (two to three adjacent cells per model, alternation by faces, never noise).

**ROSE BLOOM (shared wording, identical in PLT-01/02/03/TOP-01_Rose):** an open cup-shaped bloom: an 8-sided open frustum cup, bottom Ø0.05, rim Ø0.09 (range 0.08–0.10), height 0.06, with a closed bottom (24 tris), a smaller 6-sided pointed bud cone in the middle (base Ø0.05, 0.03 tall, base sunk 0.01 below the rim so the tip stands 0.02 above the rim; 6 tris), sitting on a 4-sided green sepal cone (Ø0.04 → Ø0.02, 0.025 tall; 4 tris). About 34 tris per bloom. Bloom axis = stalk axis. Cup slot 4 `#C8473B`, bud slot 5 `#A8372E`, sepal slot 0. No spiral, no flat disc, no petal cards.

Variant UV remap (same mesh):

| Variant | Cup | Bud | Notes |
|---|---|---|---|
| base (red) | 4 `#C8473B` | 5 `#A8372E` | |
| `_Pink` | 7 `#F2B8C2` | 6 `#E58FA0` | foliage unchanged |
| `_White` | 8 `#F4F1E8` | 8 `#F4F1E8` | bud separated from cup only by facet shading; foliage unchanged |

## Anchor

Closest approved model: none in this pack — PLT-01 IS the organic pilot and becomes the anchor for PLT-02/03/06 and TOP-01_Rose. By name only (preview not in this branch): Farm Nature `FMS_Bush_Flowering`, `FMS_Flower_Tulip` — for foliage tone and bloom chunkiness; the rose must not look more realistic than they do.

## What NOT to do

- No round or dome bush on the ground like Farm Nature `FMS_Bush_Round` / `FMS_Bush_Flowering`: the stems are visible and the leaf clusters are separate with gaps. The silhouette reads as a vase without colour.
- No alpha cards, no single-plane leaves, no cross-planes, no transparent material; everything is closed, opaque, Cull Back.
- No smooth blobs: icosphere clusters must keep visible facets; no smooth shading, no subdivision surface.
- No spiral/realistic roses, no flat disc blooms, no petal cards; blooms never smaller than Ø0.08.
- No thorns, no extra buds, no noise textures; colour only via atlas cells.
- No stems thinner than Ø0.035; no floating clusters or blooms (each touches a stem or stalk); no coplanar overlaps.
- Do not exceed 1000 tris; if over, cut cluster tris first (cut a bigger part of the lower third), never the bloom count.

## Builder notes

<!-- The builder keeps round notes in .work/models/<Pack>/<ID>_<Name>/notes.md, not here. -->

## Fixes

<!-- The model reviewer appends "## Fix N (<date>, review models_<batch>)" sections below. Do not edit earlier ones. -->

## Fix 1 (2026-11-25, review models_pilot)
- What is wrong: the bush reads as a small tree at 128 px. Leaf clusters are Ø0.24-0.28 flat-topped hexagonal plates (height 0.72 D, cap flat) on bare sticks around a thick central trunk, with large gaps; in the reference clusters are about 1.3x larger, domed, and overlap into a mass on a curved stem fan. Cups are taller than wide with a long green neck and read as tulips/cones.
- What to do: (1) cluster D to 0.34-0.38 (upper tier 0.36, lower 0.34, top 0.32) and let neighbours overlap 0.03-0.06; (2) cluster height 0.85 D, domed top (no flat cap), widest ring ~40 % up, rounded underside kept; (3) stems fan out: base spread Ø~0.2, all 6 lean 15-30 deg, kink at Y 0.42-0.45, outer clusters r 0.28-0.36 so no central trunk look; (4) blooms: rim Ø0.10 stays, cup height 0.045 (was 0.06), bottom Ø0.07 (was 0.06), visible calyx neck <= 0.025, top three tilt 10-15 deg. Must not change: 10 blooms, <= 1000 tris (cut cluster tris, never blooms), palette cells, pivot, atlas F, one mesh/material; rebuild `_Pink` and `_White` FBX, new preview, then a second sheet pass.

## Fix 2 (2026-11-25, owner request: improve the rose, higher tris budget)
- Why: owner wants the rose bush richer. Pass-2 review notes (reviews/models_pilot.md): still rounder than the reference vase, low front clusters hide the stem fan, stems straight, cups small / partly hidden.
- New budget: **<= 2000 tris** (was 1000). Spend it on visible quality, not on hidden faces.
- What to do:
  1. Vase silhouette: lift the low front clusters 0.04-0.06 m and move them outward so 0.25-0.35 m of the stem fan is visible from the 3/4 view; widest point at Y 0.75-0.85, base spread Ø0.2.
  2. Curved stems: 8-sided, 4-5 segments each with a smooth bend (not one kink), Ø0.05 → Ø0.03; 6-7 stems; 1-2 short side shoots carrying blooms.
  3. Leaf clusters: bumpier — ico subdivision 2 base reduced to ~90-110 tris each, displaced ±0.03-0.04 with fixed seed, keep domed 0.80 D, keep overlaps; 8-9 clusters; 2-3 small loose leaf tufts (3-4 faceted leaves) near the blooms to break the round outline.
  4. Rose bloom v2 (becomes the shared bloom for PLT-02/03 and TOP-01_Rose): rim Ø0.11-0.12, two rings of petals (outer 8-sided open cup + inner 6-sided cup offset 30°, rims slightly flared), a small spiral bud cone in the centre; cup wider than tall (h 0.05); about 70-90 tris per bloom; 10-12 blooms, none more than half hidden by foliage from the 3/4 view, top 3 tilted 10-15°.
  5. Optional: 2-3 closed buds (small 6-sided cones, slot 5) on short stalks.
- Must not change: palette cells / atlas F (no new cells unless unavoidable — then ask), pivot at stump base centre, one mesh + one material, variants `_Pink` / `_White` rebuilt, ONE preview.
- Afterwards: export the reusable `rose_bloom_v2` and `leaf_cluster` helpers clearly in build.py — PLT-02/03 builders will copy them.
