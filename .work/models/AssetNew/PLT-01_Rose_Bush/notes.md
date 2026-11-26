# PLT-01 Rose Bush `FMS_Garden_Rose_Bush` (+ `_Pink`, `_White`) — builder notes (Э7, pilot 2/3, 2026-11-25)

Source of truth: `build.py` (`-- PLT-01 build|export`). Live Blender 5.2 via MCP (add-on reported OUTDATED, fallback mode;
execute_blender_code and look both worked). Live work only in collection `PLT-01_Rose_Bush` (+ child collections
`PLT-01_Rose_Bush_Pink`, `PLT-01_Rose_Bush_White`); the owner's file was not saved, the Cube and `WTR-03_Birdbath` were not
touched, the owner's selection (Cube) was restored after the live export.

## Result

| | |
|---|---|
| Size | X 0.844 × Z(depth) 0.643 × Y(height) 0.996 m (Blender X×Y×Z) |
| Tris | **964 / 1000** — Stump 28, Stems 192 (6 × 32), Leaf clusters 304 (8 × 38), Blooms 440 (10 × 44) |
| Pivot | centre of the stump base on the ground (0,0,0); root empty `FMS_Garden_Rose_Bush` + one mesh `FMS_Garden_Rose_Bush_Body`, scale 1, rot 0 |
| Material | one, `M_Garden_Flora` (atlas F, `FMS_Garden_AtlasF.png`), slots 0/1/2 foliage, 4 cup, 5 bud, 13 bark, 0 calyx |
| Variants | `FMS_Garden_Rose_Bush_Pink` (cup 7, bud 6), `FMS_Garden_Rose_Bush_White` (cup 8, bud 8): same mesh, UV cells remapped, separate FBX each |
| Checks | non-manifold 0, loose 0, degenerate 0, coplanar overlaps 0, contact gaps 0 (every shell touches another), stump min z 0.0000 (on ground); clusters touching each other: none; blooms touching each other: none; bloom inside a foreign cluster: none; every calyx apex inside its own cluster |
| FBX verify | each of the 3 FBX: 2 nodes (empty + mesh), 964 tris, dims 0.844/0.643/0.996, texture found in its `.fbm` |
| Headless | `build.py -- PLT-01 export` SHA1 of all three meshes (world verts + face UV cells) == live: `c6cde1a6…` (532 verts / 884 faces each) |

## Parts (Blender Z up; az = azimuth from +X, front = −Y = reference camera)

| Part | Build | Tris |
|---|---|---|
| Stump | 8-sided frustum Ø0.12 → Ø0.10, z 0–0.10, both caps | 28 |
| Stems ×6 | `stem()`: 6-sided tapered prism Ø0.05 → Ø0.042 (kink) → Ø0.035, base inside the stump (z 0.05), mitred kink, tip ends inside the cluster it carries, both ends capped | 6 × 32 |
| Leaf clusters ×8 | `leaf_cluster()`: ico sphere 80 tris (bpy `subdivisions=2`), random Z spin, lower half removed, equator ring pulled in ×0.58 and down, welded 10 → 5 verts, flat cap; width ≈ D, height 0.72 D, ±0.03 noise (fixed seeds 11–18, cap stays planar). Face slot by normal: up (n.z > 0.6) → 1, down (n.z < −0.2) and cap → 2, sides → 0 | 8 × 38 |
| Blooms ×10 | `rose_bloom()`: ONE closed shell — 8-sided green calyx/stalk cone from an apex 0.05 inside the cluster to the cup bottom 0.03 above the cluster surface (slot 0) → 8-sided frustum cup Ø0.06 → Ø0.10, 0.06 tall (slot 4) → inner funnel from the rim to the 6-sided bud base, 0.02 below the rim (slot 4) → 6-sided bud, tip 0.008 above the rim (slot 5) | 10 × 44 |

Layout (from the reference, 3 lower + 5 upper clusters as in the spec):

| Cluster | az | r | centre z | D | blooms (tilt outward) |
|---|---|---|---|---|---|
| T (top, back-centre) | 96 | 0.11 | 0.81 | 0.28 | 1 (8°) |
| TL / TR | 150 / 28 | 0.31 | 0.73 / 0.74 | 0.26 | 1 each (12°) |
| ML / MR | 235 / 305 | 0.25 | 0.64 / 0.66 | 0.26 | 1 each (25°) |
| L / R (lower) | 195 / 345 | 0.26 | 0.37 / 0.39 | 0.26 | 2 each (20°/26°, ±10° sideways) |
| C (lower, front) | 270 | 0.18 | 0.34 | 0.24 | 1 (20°) |

Stems: T (own), TL and TR (pass through L / R at the kink, then up to TL / TR — the vase line), ML, MR (own, kink at
z 0.42–0.44), C (short, front).

## Deviations from `prompts/PLT-01.3d.md` (for the reviewer / spec owner)

1. **Bloom count 10** (spec). The reference also shows 10 (T 1, TL 1, TR 1, ML 1, MR 1, L 2, C 1, R 2) — the "12" in
   the dispatch note is a miscount. Distribution follows the reference: 3 top (z 0.92–1.0), 2 upper-mid (~0.80), 5 on the
   lower tier (~0.50–0.55), not 3/4/3 as in the spec text.
2. **Bloom = 44 tris, one closed shell, not 34.** Opaque + Cull Back + non-manifold 0 do not allow a single-sided open cup:
   the far inside wall would be culled. The cup interior is a shallow funnel from the rim to the bud base. The separate
   4-sided stalk + 4-sided sepal of the spec are merged into one 8-sided green calyx cone whose apex is buried in the
   cluster (no hidden caps, no floating). Cup bottom Ø0.06 (spec 0.05) and rim Ø0.10 (range max) so the cups read as big as
   in the reference.
3. **Bud sunk deeper:** base 0.02 below the rim, tip 0.008 above (spec 0.01 / 0.02). With the spec numbers the bud stuck
   out like a crown; the reference shows the tip at about rim level with the interior visible.
4. **Leaf cluster 38 tris, not ~50–56.** A real "lower third cut" of the 80-tri sphere costs 68 tris (bisect even more,
   with sliver faces). Instead the lower half is removed and the rim pulled in/down and welded 10→5: the widest facets
   stay above a rounded, inward-sloping dark underside (as in the reference). Height/width 0.72 instead of 0.7 squash.
   This bought the tris for the closed cups (spec: "cut cluster tris first, never the bloom count").
5. **Bloom tilt:** top three 8–12° (spec 20–45°); the reference shows them nearly upright with the inside visible, and at
   20° they leaned away from the front camera and read as cones. Others 20–26°.
6. **Stem leans:** T stem near-vertical (reference: central stem straight up); the other lower segments lean 15–18°
   (ML, MR, C) and 37° (TL/TR stems through L/R), so the base is ~Ø0.2 and the bush widest (~0.84) at z ≈ 0.75, i.e. the vase. Stem tips are where
   their clusters are (C 0.34, L/R inside, ML/MR 0.64–0.66, TL/TR 0.73–0.74, T 0.81), not 0.80–1.00: tips inside clusters.
7. **Depth 0.64, width 0.84** (catalogue 0.8 × 0.8). The reference is a front view; the back half is populated by T,
   TL, TR, but a deeper bush would need clusters behind T, which the reference does not show.
8. **Lower clusters at r 0.18–0.26** (spec 0.12–0.22) to match the reference (lower L/R are as wide as the top tier).

## Rounds (live, 5 of 5)

1. First build (964 tris, clean checks, vase readable). Worst: cups narrow and tall with a 4-sided bottom (tulip / crown
   look), bud sticking out; bush only 0.55 deep; clusters a bit flat.
2. Cups wider/shorter, bud sunk, layout spread in depth (0.66), clusters taller. Worst: 4→8 cup facets still read as
   crowns; clusters T and TR touched.
3. Cup → 8-sided frustum with an 8-sided calyx (+8 tris per bloom), paid for by welding the hidden cluster rim 10→5
   (−10 per cluster); T/TR separated. Worst: cluster undersides became vertical "box" walls.
4. Rim narrower (×0.58) and higher → rounded dark undersides like the reference; cups 0.06 tall; check view 25°.
   Worst: the three top blooms leaned away from the camera and read as cones.
5. Top bloom tilt 8–12°. 128 px thumbnail: vase of separate green drops with red cups on top, stems visible — reads.

Remaining (nitpicks): reference stems are a little thicker and more curved near the stump (ours are straight 2-segment
prisms, Ø0.05 as specified); reference clusters are slightly bumpier (more facets than the 38-tri drop); in the 3/4 view
the right side (TR) looks a bit sparse because TR stands alone on a long stem.

## Atlas F — `art/AssetNew/Textures/FMS_Garden_AtlasF.png` (shared by all atlas-F models: PLT, TOP, FLB, ORN-03, ORN-05)

256 px, 4×4 cells of 64 px, one colour per cell; slot = row * 4 + col, row 0 at the top of the PNG; UVs at cell centres
(`pack_common.cell_uv`). Written by `pack_common.atlas_image` from `PAL_F` in build.py (= STYLE.md table, verified by
pixel read of all 16 cells).

| row \ col | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | 0 foliage `#6E9F4A` | 1 foliage light `#8AB257` | 2 foliage dark `#4E7A3A` | 3 deep green `#3F6B3A` |
| 1 | 4 rose red `#C8473B` | 5 rose red dark `#A8372E` | 6 rose pink `#E58FA0` | 7 pink light `#F2B8C2` |
| 2 | 8 white flower `#F4F1E8` | 9 lilac `#A58BC9` | 10 wrought iron `#3A3A3F` | 11 yellow `#E8B83A` |
| 3 | 12 soil `#805433` | 13 bark/stem `#7A5233` | 14 stone `#A7A39A` | 15 stone light `#C9C3B6` |

Material `M_Garden_Flora`: Principled, image Closest, Metallic 0, Roughness 0.85 (Smoothness ≈ 0.15), Specular IOR level 0.25.

## For the next builders (STR-06 is atlas A; PLT-02/03/06, TOP-01_Rose are atlas F)

- Atlas F: reuse `FMS_Garden_AtlasF.png` + `M_Garden_Flora`; copy `PAL_F`, `ATLAS_TEX`, `ATLAS_MAT` and the roughness line.
  Each atlas-F build rewrites the same PNG from the same palette (byte-identical); do not change `PAL_F`.
- Organic generators to copy from build.py (parametric, no globals except slot constants):
  `leaf_cluster(c, D, seed, H, noise, rim_k, rim_drop, ...)` → (temp bmesh, face slots) + `add_bmesh()` to put it into a Part;
  `rose_bloom(P, anchor, axis, ...)` (closed 44-tri bloom); `stem(P, [base, kink, tip], radii, n, az)` (capped tapered
  prism with mitred kinks); `ring()` / `bridge()` (rings with different vertex counts zipped by angle, e.g. 8 → 6).
  Blooms are anchored with a BVH ray down onto their cluster (`bvh[...].ray_cast`) and the calyx apex is checked to be inside.
- Checks worth copying: `overlaps(P, prefix_a, prefix_b)` (which shells touch: cluster–cluster, bloom–bloom, bloom in a
  foreign cluster), `part_tris(P)`, `geom_dump([objs])` (SHA1 incl. UV cells for variant FBXs), `make_variant()` (UV remap
  by cell for colour variants, own child collection so `pc.export` exports it alone), `save_lib()` for several collections.
- `render(objs, ...)` renders a temporary collection in a temporary scene (only the listed objects), so variants or other
  collections do not leak into previews; the owner's 2 m Cube is not in it.
- Live export changes the selection (pc.export); save the selection before and restore it after (done here).

---

# Fix 1 (2026-11-25, review models_pilot) — applied

Live Blender 5.2 via MCP, 5 of 5 fix rounds, only collection `PLT-01_Rose_Bush` (+ variant children); `WTR-03_Birdbath`,
`STR-06_Gazebo`, the Cube and the owner's selection untouched / restored; owner file not saved. Pre-fix script kept at
`%TEMP%/assetnew_check/PLT-01/build_before_fix1.py`. **The tables above describe the pre-fix model; this section wins.**

## Result after Fix 1

| | |
|---|---|
| Size | X 1.012 × Z(depth) 0.690 × Y(height) 1.046 m |
| Tris | **964 / 1000** — Stump 28, Stems 192 (6 × 32), Leaf clusters 304 (8 × 38), Blooms 440 (10 × 44) — unchanged |
| Pivot | stump base centre (0,0,0); root empty + one mesh `_Body`, scale 1, rot 0; one material `M_Garden_Flora`, atlas F unchanged |
| Checks | non-manifold 0, loose 0, degenerate 0, coplanar 0, contact gaps 0, min z 0.0000; blooms touching each other: none; every calyx apex inside its own cluster |
| Overlaps (wanted by Fix 1) | C–ML, L–ML, MR–R, T–TR clusters interpenetrate; L6 / R7 blooms dip into the ML / MR cluster sides (visually: bloom nestled against the neighbour) |
| FBX verify | base, `_Pink`, `_White`: 2 nodes, 964 tris, dims 1.012/0.69/1.046, texture found in each `.fbm` |
| Headless | `build.py -- PLT-01 export` SHA1 == live `ae9ccc73…` (3 meshes, 532 verts / 884 faces each) |

## Fix 1 items

| Item | Done |
|---|---|
| (1) cluster D | top T 0.32, upper TL/TR/ML/MR 0.36, lower L/R/C 0.34; neighbours overlap (pairs above) |
| (2) domed profile | `leaf_cluster(prof=...)`: same 38-tri topology, rows re-profiled — rim r 0.62 at the base (flat, hidden cap), widest ring at 40 % of the height (r 1.0), upper ring at 82 % (r 0.70), apex on top: dome, no flat top, rounded inward underside. **Height 0.80 D** (Fix: ~0.85): at 0.85 the drops read as tall eggs/acorns in the 25° view and the crown became one ball (round 1–3); 0.80 kept the dome |
| (3) stem fan | bases spread over the stump top (r 0.03), lower segments lean T 15°, C 23°, ML/MR 28°, TL/TR 30°; kinks at z 0.42–0.45 (C 0.30, it ends in the low front cluster); outer clusters at r 0.28–0.33; T stem no longer vertical in the middle (base az 135 → kink az 120 → T) |
| (4) blooms | rim Ø0.10, cup height 0.045, bottom Ø0.07, visible calyx neck 0.02, bud base 0.018 below the rim, tip 0.008 above; top three tilt 10° / 14° / 14°; still 10 blooms, 44 tris each |
| keep | 10 blooms, 964 tris, palette cells, pivot, atlas F file content (same PAL_F), one mesh/material; `_Pink`/`_White` re-exported; new preview |

Layout after Fix 1 (az, r, centre z, D): T 90/0.08/0.86/0.32 · TL 160/0.32/0.78/0.36 · TR 20/0.32/0.79/0.36 ·
ML 215/0.28/0.62/0.36 · MR 325/0.28/0.63/0.36 · L 190/0.33/0.40/0.34 · R 350/0.33/0.40/0.34 · C 270/0.22/0.41/0.34.
ML/MR moved from the front (235/305) to the sides (215/325) so the low front cluster C and its bloom are in front of them, as in the reference.

## Rounds (Fix 1, live, 5 of 5)

1. Fix numbers applied literally (D 0.32–0.36, H 0.85, fan). Dense mass, but lower tier hung low and hid the stem fan; width 1.01.
2. Lower tier raised (bottoms ~0.30), outer r pulled to 0.30. Stem fan visible in front view; C hidden behind ML/MR.
3. ML/MR to the sides, C forward. Front ok; in 3/4 the crown read as one ball on a stem bundle (tiers squeezed, eggs).
4. Lower tier lower and wider (r 0.33, z 0.40), tiers separated as in the reference, outer stems 28–30°, H 0.80.
   Front view matches the reference structure (3 top / 2 mid / 3 low, fan of stems below). 128 px: bush, not tree.
5. Stem bases spread on the stump, T/C stems turned. Little change in the 3/4 view (the base is behind the low clusters).

## Remaining after Fix 1 (for the second sheet pass)

- Size 1.01 × 0.69 × 1.05 (catalogue 0.8 × 0.8 × 1.0): Fix 1 cluster sizes and radii make it wider; the reference proportions (h/w ≈ 1.1) match.
- 3/4 preview: the stem fan is mostly hidden by the low front clusters (only ~0.15 m of stems shows); the front view shows the
  full fan like the reference. At 128 px the 3/4 thumbnail reads as a dense round shrub with a short base, not a tree with
  plates, but it is rounder than the reference vase.
- Reference stems are thicker and curved; ours are straight 2-segment prisms (Ø0.05 → 0.035 as specified).
- Clusters are 38 tris; the reference drops look a little bumpier.

## Shared lessons for PLT-02/03/06, TOP-01_Rose (update)
- Use `leaf_cluster(..., prof=...)` with the Fix 1 profile; do not cut a flat top. Measure the drop size on the reference
  (here 0.32–0.36). Check the 25° view: a drop taller than ~0.8 D reads as an egg.
- Keep the low front drop in front of the mid ones; tiers separated by visible stems; outer stems at 28–30°.

---

# Fix 2 (2026-11-25, owner request: richer rose, budget <= 2000) — applied

Live Blender 5.2 via MCP, **4 of 5 rounds**, only collection `PLT-01_Rose_Bush` (+ variant children); other collections,
the Cube and the owner's selection untouched / restored; owner file not saved. Pre-Fix-2 script kept at
`%TEMP%/assetnew_check/PLT-01/build_before_fix2.py`. **This section supersedes the Fix 1 numbers above.**

## Result after Fix 2

| | |
|---|---|
| Size | X 1.045 × Z(depth) 0.878 × Y(height) 1.092 m |
| Tris | **1996 / 2000** — Stump 28, Stems 456 (6 × 76), Side shoots 64 (2 × 32), Shoot leaves 32 (4 × 8), Leaf clusters 640 (8 × 80), Blooms 680 (10 × 68), Closed buds 24 (2 × 12), Leaf tufts 72 (3 × 3 leaves × 8) |
| Pivot | stump base centre (0,0,0); root empty + one mesh `_Body`, scale 1, rot 0; one material `M_Garden_Flora`; atlas F cells unchanged (no new cells) |
| Checks | non-manifold 0, loose 0, degenerate 0, coplanar 0, contact gaps 0 (every shell touches another), min z 0.0000; blooms touching each other: none; every calyx / bud base inside its own cluster (no warnings) |
| Overlaps | clusters C–ML, L–ML, ML–TL, MR–R, MR–TR, T–TL interpenetrate (mass); blooms L5 / R6 touch the side of ML / MR |
| FBX verify | base, `_Pink`, `_White`: 2 nodes, 1996 tris, dims 1.045/0.878/1.092, texture found in each `.fbm` |
| Headless | `build.py -- PLT-01 export` SHA1 == live `70ee007f…` (3 meshes, 1082 verts / 1772 faces each) |

## Fix 2 items

| Item | Done |
|---|---|
| 1 vase / stem fan | Lower tier lifted 0.05–0.06 (centres z 0.46–0.47, bottoms ~0.33) and moved out (L/R r 0.34, C r 0.27 at az 255, out of the 3/4 camera line); ~0.3 m of the stem fan (3 stems diverging from the stump) visible in the 3/4 view, full fan in front. Widest at z ~0.78 (top tier); stem bases spread on the stump top |
| 2 curved stems | 6 stems, 8-sided, 4 segments each on a quadratic Bezier (`bezier_pts`: passes a mid point at t 0.5, then up into its cluster), Ø0.05 → Ø0.03 (`taper`); TL/TR stems pass through L/R. 2 side shoots (6-sided, 2 segments, Ø0.032 → 0.025) from the TR and ML stems, each ending in a bloom and carrying 2 leaves |
| 3 clusters | 8 drops, FULL 80-tri ico sphere (no cut, no cap), re-profiled: widest ring 40 % up, dome top, underside pulled in (under_k 0.85), height 0.80 D, noise ±0.035 (fixed seeds) — bumpier outline. **80 tris, not 90–110**: that would cost +80–240 tris, spent on blooms/stems instead. 3 leaf tufts (3 faceted leaves each, 0.15 long) on TL, MR, C break the outline (TL tuft clearly at the top-left) |
| 4 rose_bloom_v2 | rim Ø0.116, cup h 0.05 (wider than tall); outer 8-sided petal ring with petal tips (rim rotated 22.5°), inside of the outer petals, inner 6-sided petal cup offset 30° (slot 5, darker), twisted spiral bud cone, green calyx; 68 tris each (Fix: ~70–90). 10 blooms: 8 on cluster tops + 2 on side shoots (S1 above the top between T and TR, S2 out to the left); top three tilt 12/14/14°; none more than half hidden in the 3/4 view (L and R ones partly behind ML/MR) |
| 5 closed buds | 2 (on L and MR): 6-sided bipyramid, green calyx cone + red cone (slot 5), 12 tris each |
| keep | palette cells, pivot, one mesh/material, `_Pink`/`_White` rebuilt (remap: outer petals 4→7/8, inner petals + bud + closed buds 5→6/8), ONE preview |

## Rounds (Fix 2, live)

1. First build 1964 tris: stem fan visible in 3/4, two-ring roses read. Worst: tufts buried (slits), S1 bloom stacked on the TR bloom, L/R blooms half hidden.
2. Tufts bigger, S1 moved between T and TR above the top, L/R blooms 0.08 outward. Worst: bare shoot sticks, tufts lying flat.
3. +2 leaves per shoot (1996 tris), tufts on the upper side. Shoot leaves sat at the cluster surface (invisible).
4. Shoot leaves moved up to the visible part near the bloom, tufts lifted (stand up). 128 px: flowering bush, stem fan visible. Stopped here.

## 128 px self-check (3/4 preview)

Reads as a flowering bush: a lumpy green mass with ~10 red roses spread over it (2 on shoots above / out of the outline),
a leaf tuft on the top-left and a visible fan of 3 brown stems below from the stump. It is not a plate stack and not a
lollipop on one trunk; it is still a rounded crown (wider top than base) rather than an open vase.

## Remaining

- Size 1.05 × 0.88 × 1.09 (catalogue 0.8 × 0.8 × 1.0; pass 2 accepted 1.0 × 0.7 × 1.05): shoots and tufts add ~0.05–0.1.
- Clusters 80 tris (Fix: 90–110). Tufts on MR / C read only at close range.
- Stems are smooth Bezier curves but still read rather straight at 128 px.

## Reusable helpers for PLT-02/03, TOP-01_Rose (copy from build.py)

- `leaf_cluster(c, D, seed, H=0.80, widest=0.40, noise=0.035, sub=2, under_k=0.85)` + `add_bmesh(P, name, bm, slots, comp)` → 80-tri drop.
- `rose_bloom_v2(P, anchor, axis, spin, depth, neck, r_base, r_rim, h_rim, r_in0, h_in0, r_in1, h_in1, r_bud, h_bud, h_tip, twist, slot_calyx, slot_outer, slot_inner)` → 68 tris; scale all radii/heights together for smaller roses (e.g. ×0.7 for a climbing rose).
- `closed_bud(P, anchor, axis, ...)` 12 tris; `leaf(P, base, dir, L, W, T)` 8 tris; `leaf_tuft(P, anchor, out, n, spread, lift, sink, L, W, seed)`.
- `bezier_pts(p0, pmid, p2, n)` + `stem(P, pts, radii, n, az)` + `taper(r0, r1, n)` for curved stems / shoots; `ring()` / `bridge()` for lofts between rings with different vertex counts.
- Placement: `top_hit(bvh, centre, offset)` (anchor on a drop's top), `inside(bvh, point)` (buried calyx check); checks `overlaps()`, `part_tris()`, `geom_dump()`; variants `make_variant()`.
