# STR-02 Rose arch, wrought iron `FMS_Garden_Arch_Iron` — builder notes (Э7, series batch 2, 2026-11-25)

Source of truth: `build.py` (`-- STR-02 build|export|verify|mount`). Live Blender 5.2 via MCP (add-on reported OUTDATED,
fallback mode; execute_blender_code and look worked). Live work only in collection `STR-02_Arch_Iron` (left in place); the
owner's file was not saved, the default Cube and the other collections were not touched; selection (Cube) restored after
the live export.

## Result

| | |
|---|---|
| FBX | `art/CottageGardenDecor/Meshes/FMS_Garden_Arch_Iron.fbx` (+ `.fbm` with the atlas copy) |
| Blend / preview | `art/CottageGardenDecor/Blend/FMS_Garden_Arch_Iron.blend` (collection only); ONE preview `art/CottageGardenDecor/Previews/FMS_Garden_STR_02_Preview.png` |
| Tris | **2722 / 1400 (1.94×)** — see "Budget" below. Frame 472 · Feet 120 · Cross-rods 84 · Spreaders 112 · Side scrolls 1072 · Corner scrolls 816 · Finial 46 |
| Size (Blender X×Y×Z) | 1.482 × 0.464 × 2.500 m (x ±0.741, y ±0.232, z 0 … 2.50) |
| Nodes | root empty `FMS_Garden_Arch_Iron` + mesh `_Body` + empties `Plant_L`, `Plant_R`, `Plant_Top` (bare names in the FBX, `<asset>_Plant_*` in the .blend) |
| Material | `M_Garden_Build` + shared `Textures/FMS_Garden_AtlasA.png` (read only, MD5 `119daf05…` unchanged; palette pixel check 0 mismatches). One slot only: 13 wrought iron `#3A3A3F` (cells used: [13]) |
| LOD | none (catalogue) |

## Pivots and axes
- Root (0, 0, 0) = centre of the footprint on the ground; rot 0, scale 1; FBX Y up, −Z forward baked. Static, no moving parts.
- Blender X = across the opening, −Y = front (Unity +Z), Z = up (Unity Y). Symmetric in X and Y.
- Empties: `Plant_L` (−0.64, 0, 0), `Plant_R` (+0.64, 0, 0) = the outer faces of the uprights (side plane, like the
  STR-01 post plane); `Plant_Top` (0, 0, 2.42) = top of the hoop crown (Blender X, Y, Z).

## Checks (live and headless identical)
- non-manifold 0, loose 0, degenerate 0, internal gaps 0 (every component touches another), mirror X 0.000000.
- Coplanar overlapping face pairs 0.
- Ground contact: 4 spike tips at z 0.0000 (x ±0.62, y ±0.20); nothing below 0, nothing floating.
- Scroll self-clearance (centre-lines, non-neighbouring samples): big 0.042, small 0.040 ≥ bar 0.030 → no self-touch.
- SNAP OK: clear passage 1.200 (upright inner faces) up to the corner scrolls at z 1.623; total width 1.482 ≤ 1.5 (fits the
  1.5 m gap between MOD-04 pillars, 9 mm per side); depth 0.464 ≤ 0.5; height 2.500; empties at the listed positions.
  Between the foot collars (z ≤ 0.13) the clear width is 1.176.
- Mount check (`-- STR-02 mount`, PLT-02 ×2 rotated ±90° at Plant_L/R, PLT-03 at Plant_Top, FBX from art/ read only,
  render `%TEMP%/assetnew_check/STR-02/STR-02_mount_headless.png`): side plants sit flat on the side planes and grow
  outward, swallowing parts of the outer scrolls (rose over ironwork, accepted). PLT-03 sits on the crown only — it is
  straight and the hoop is round, so its ends hang free above the hoop shoulders (reads as a wreath on top; the finial
  pokes into its underside). Fine as a decoration, but STR-01 remains the better garland carrier.
- FBX re-import: 5 nodes (root + Body + 3 empties), 2722 tris, dims 1.482 / 0.464 / 2.5, min z 0, texture found in `.fbm`.
- Headless `build.py -- STR-02 export` geometry SHA1 == live SHA1 `50dcffc880f0d8c5f28cb8d96d7a62e9e60e1c26`
  (mesh 1405 verts / 1498 faces + 3 empties).

## Build (what is where)
- Frames (2, y ±0.20): one continuous 8-sided sweep each, upright (z 0.11 → 1.90) + semi-elliptic hoop (12 segments,
  half-width 0.62, rise 0.50, crown centre-line 2.40, outer top 2.42) + upright; rod 0.040 across the flats.
- Feet (4): 8-sided spike, tip on the ground, cone to an inverted-frustum collar (z 0.095–0.130, 0.052 → 0.064 across);
  the upright starts inside the collar.
- Cross-rods (3) along Y on the hoop at the ellipse angles 45°/90°/135°; side spreaders (4) at z 0.30 and 1.85; all
  0.037 across (1.5 mm off the frame faces: no coplanar sides).
- S-scrolls (shared construction `s_curve()`): top curl (CCW spiral, 290°, radius 1.0 → 0.48 R) + Hermite spine with
  vertical end tangents + bottom curl (CW spiral); both curls touch the upright (bar sunk 4 mm). Bar 0.030 across, 8-sided.
  Side S (outer side of each upright): R 0.044, z 1.04–1.33, 7 segments per curl, curl 0.111 across, reaches x ±0.741.
  Corner S (inside each frame under the springing): R 0.042, z 1.62–1.85, 5 segments per curl, curl 0.107 across.
- Finial: 8-sided stub (from inside the crown) + diamond, widest 0.048 at z 2.458, tip at 2.50.

## Budget (spec allows ~2× for scrolls with a note; coordinator decision 2026-11-25: option A, keep the spec build)
2722 tris = 1.94 × 1400. The frame with feet, cross-rods, spreaders and finial alone is 834; 8 S-scrolls with 8-sided bars
(16 tris per segment) and 5–7 segments per curl are 1888. ≤ 1400 is not reachable without dropping scrolls or using
4-sided bars (rejected). Possible trims if the owner wants them: corner scrolls with 6-sided bars (−208, coordinator
allowed it; not done to keep every bar 8-sided as the FUR-03/04 anchor), side curls 6 segments (−128).

## Deviations from `prompts/STR-02.3d.md` (for the reviewer / spec owner)
1. **Uprights at x ±0.62 (spec ±0.60)** so the clear passage is 1.20 between the inner faces (same opening as STR-01; the
   spec's ±0.60 centres give 1.16). Consequence: total width 1.482 (catalogue 1.4) — the scrolls need ≥ 0.10 curls; still
   fits the 1.5 m wall gap with 9 mm per side.
2. **Hoop is a semi-ellipse, rise 0.50 (spec half-round r 0.60).** The reference hoop is visibly flatter (rise ≈ 0.75 ×
   half-width), and with springing 1.90 a half-round hoop alone would reach 2.52 — no room for the finial inside 2.5.
3. **Rods: frame 0.040, scroll bars 0.030 (spec ~0.035 for all).** The reference uprights are ~1.8× thicker than the scroll
   bars; with 0.035 bars the 0.10 curls closed into blobs (no eye).
4. **Feet**: spike 0.095 + collar 0.035 (spec cone 0 → 0.08) — the reference has a collar above the spike.
5. **Extra side spreaders under the springing (z 1.85)** and the bottom spreaders at z 0.30 (spec 0.20): both from the
   reference.
6. Corner scrolls start at z 1.62 (spec 1.6–1.9): they sit inside the frames, so above 1.62 the passage narrows by
   up to 0.10 per side.

## Rounds
- Headless pre-builds (3): spec numbers → curls too small/hook-like, comparison camera wrong side; then full 290–300°
  curls with an eye, thicker frame / thinner bars, uprights at ±0.62 (passage 1.20).
- Live round 1: build = headless; reference angle + 3/4 + front + 128 px thumbnail. Worst: S too slender (long straight
  spine), curls hexagonal (6 segments), budget.
- Live round 2: side S spine shorter (dv 0.19), 7 segments per side curl, corner curls 5 segments (budget < 2×); close-up of
  the scrolls, thumbnail reads (hoop, cross-rods, scrolls, spikes). Export live + headless.
- Rounds used: 2 of 5 live.

## Remaining differences vs the reference (nitpicks)
- Reference S-scrolls are larger (≈ 0.15 × 0.38 m) and rounder; ours are 0.10 × 0.29 (side) — limited by the 1.5 m wall
  gap and the budget.
- Reference curls have more facets (≈ 10–12 per turn); ours 5–7 per 290°.
- The reference image is a near-oblique projection (front frame level, back frame shifted up-right); no camera matches it
  exactly; comparison camera `VIEW_REF` = 3/4 front-right, 25°.
