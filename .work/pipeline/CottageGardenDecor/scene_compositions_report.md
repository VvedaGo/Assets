# Э10 scene Demo_Compositions — composition vignettes + Modules (Unity assembler, 2026-11-26)

Scene `Assets/CottageGardenDecor/Demo/Scenes/Demo_Compositions.unity`, layout `planning/CottageGardenDecor/layouts/Demo_Compositions.txt`,
wrapper `Assets/Editor/CottageGardenDecor/CottageGardenDecorCompositionsScene.cs` (menu Tools/Cottage Garden Decor/Build Compositions Scene).

- PackSceneBuilder places only the plain module items (`savePrefabs: false`, no `comp` lines). The six CMP prefabs are placed as
  **prefab instances** by `#! cmp` and are not re-saved (asset files unchanged since Fix 1).
- Plinth per shot: the demo island DEM-01 scaled to the group footprint + 0.9 m (x) / 0.6 m (z) on each side, underside × 0.12
  (≈ 0.35 m soil cut), with the vignette-only material `Demo/Materials/FMS_Garden_Demo_Plinth.mat` (demo atlas × (0.80, 0.84,
  0.80)): at this distance the lawn fills ~40 % of the frame and the full-bright lawn competed with the items.
- One camera rule for all six: bearing 150° (front-right, 30° off the front axis; fronts/entrances face the camera, key light
  from the camera's upper left), 36° down, vFOV 32°; distance fitted so the group is 68 % of the frame width, limited by
  group + plinth ≤ 97 % width / 96 % height; framed on the centre of group + plinth. 1920×1080.
- Backdrop: soft light gradient (`FMS_Garden_Demo_Backdrop.mat`, gradient sky shader, #F4F2EE → #E4E5EA, exposure 1.25), rendered
  ≈ #E5E4E2 at the top / #DFDEDD at the bottom (catalogue tone ~#E9E9EC after ACES). Same for all six and Modules.
- Look: the shared pack look (CottageGardenDecorLook, Volume FMS_Garden_Look), no fog, no DOF.

| Shot | Render | Group width | Group rows | Group + plinth (w / h) | Rounds |
|---|---|---|---|---|---|
| CMP-01 RoseArchEntrance | AssetStore/CottageGardenDecor/Media/raw/CMP-01.png | 52.6 % (x 23–75) | 2–79 % | 73.6 % / 96 % | 4 (+ backdrop) |
| CMP-02 PergolaTerrace | …/raw/CMP-02.png | 65.3 % (x 15–81) | 2–89 % | 73.6 % / 96 % | 4 |
| CMP-03 GazeboRetreat | …/raw/CMP-03.png | 54.3 % (x 27–81) | 2–65 % | 75.6 % / 96 % | 4 |
| CMP-04 FountainParterre | …/raw/CMP-04.png | 67.9 % (x 15–83) | 2–82 % | 84.2 % / 96 % | 4 |
| CMP-05 WalledPondCorner | …/raw/CMP-05.png | 68.0 % (x 16–84) | 3–71 % | 79.7 % / 94 % | 4 |
| CMP-06 WildlifeLawn | …/raw/CMP-06.png | 60.0 % (x 22–82) | 2–70 % | 82.0 % / 96 % | 4 |
| Modules | …/raw/Modules.png | 80.0 % (x 10–90) | 12–76 % | 82.6 % / 75 % | 2 |

Rounds: R1 margin 1.5 m, depth 0.25, pitch 38 (groups 41–55 %, height-limited by the plinth) → R2 margin 1.0, pitch 36, share
0.68 → R3 separate x/z margins 1.0/0.7 → R4 margins 0.9/0.6, frame limits 97/96 %, dimmed plinth material; then backdrop exposure
(bg had come out #DCDBD9). Modules: R1 sets spread (68 %) → R2 wall and pergola moved in, share 0.80.

Modules layout (Modules.md): pond 3×2 front left (MOD-09 ×6, MOD-07 ×10, MOD-08 ×4), brick ring front centre (MOD-05 ×4 + MOD-06 ×4,
3×3 m by axis), lattice front right (MOD-01 ×2, MOD-02 ×3), stone wall back left (MOD-03 ×2, MOD-04 ×3), pergola back right (STR-04 +
STR-05 at +1.5, PLT-05 ×4 under the front beam at 2.24).

## Remaining differences vs references / rules
- Group width below 65 % on CMP-01 (52.6 %), CMP-03 (54.3 %) and CMP-06 (60.0 %): in a 16:9 frame at 36° the tall rose arch /
  4 m gazebo / swing frame make group + plinth reach 96 % of the height first. The references are 1:1; a 1:1 or 4:3 crop of the
  same renders would meet 65–85 %.
- CMP-03 follows the current prefab (flowers around the gazebo, arch angled 35°), not CMP-03.png.
- References use a cream background #F5F1E9 and a thin octagonal slab; here the series floating-island plinth and a neutral light
  grey (#E5E4E2).
- Lawn reads a saturated green (atlas #7DB93C, dimmed ~18 % on the plinths); references show a more olive lawn.
- Modules uses the vignette camera rule (36°, front-right) instead of Modules.md (SE 43°, vFOV 35); the lattice stands straight,
  not diagonal as in Modules.png.
- Known model points: STR-01_Gate all white; climbers on the arch side faces.

## Fix renders_2 (2026-11-26)

Vignette rules of renders_2 + Fix 1 of CMP-03, CMP-05, Modules applied to all six + Modules (CMP-04 = model frame, same rule):
- Plinth = group bounds + 0.7 m left/right/back, + 1.0 m front (`#! plinth 0.7 0.7 1.0 0.08`, underside × 0.08 ≈ 0.23 m),
  material tint (0.90, 0.94, 0.90): plinth lawn lit **#8AC951–#8CCC52** (target #86C24A), shadow #34702A–#458531.
- Camera (all six): bearing 150° (30° off-axis), 36° down, vFOV 32; Modules 42° down (Modules.md 43°). Fit: distance so the
  plinth takes 87 % of the width unless group + plinth exceed 87 % of the height; then plinth centred horizontally, lowest plinth
  pixel at 92 %, tallest point at 5 %. Distances 11.2–16.2 m.
- Backdrop: warm light neutral, rendered **#EFEBE4** at the top centre (#E6E0D9 in the vignette corners), same for all seven.
- Rendered through the HDR path (see Look v2) with the v2 look; prefabs unchanged (no item moved in CMP-03/CMP-05: the Fix
  suggestions "move bed and topiaries" / "move the arch" would change the composition prefabs, which this stage must not re-save).
- Modules layout tightened (gaps 0.8–1.2 m): front row pond / ring / lattice aligned at the pond front, back row wall (1 m
  behind the pond, 1 m left of the pergola) / pergola.

| Shot | Group width | Plinth width | Top / plinth bottom | Rounds |
|---|---|---|---|---|
| CMP-01 | 47.4 % | 65.5 % | 5 % / 92 % | 5 |
| CMP-02 | 58.0 % | 65.5 % | 5 % / 92 % | 5 |
| CMP-03 | 49.1 % | 67.8 % | 5 % / 92 % | 5 |
| CMP-04 | 60.7 % | 75.3 % | 5 % / 92 % | 5 |
| CMP-05 | 62.0 % | 72.4 % | 5 % / 92 % | 5 |
| CMP-06 | 53.8 % | 73.1 % | 5 % / 92 % | 5 |
| Modules | 74.7 % | 78.0 % | 5 % / 92 % | 5 |

Rounds: R1 new plinth/fit rule (height-limited, edges 6/90 %) → R2 edges 5/92 %, thinner underside → R3 HDR render fix + backdrop
exposure 1.42 (#EFEBE4) → R4 plinth tint for #86C24A → R5 Modules front row aligned.

Remaining: every vignette is height-limited — with the fixed angle (36° down, 30° off-axis) and a 16:9 frame, group + plinth
reach the 5 %–92 % height window before the plinth reaches 85–90 % of the width (plinth 65–78 %, group 47–62 %; the rule allows
~60 % only for tall items). Reaching the width targets needs either a squarer frame (the CMP references are 1:1), a lower
camera, or tighter compositions (moving prefab items — not allowed here). CMP-03 and CMP-05 keep their internal empty zones
(front-right of CMP-05, front of CMP-03). No soft shadow under the plinth (the backdrop is a sky material, nothing receives it).

## Fix 2 (renders_2 pass 2, 2026-11-26)

Look v2, 16:9, the shared angle (bearing 150° = 30° off-axis, 36° down, vFOV 32) and the CMP prefabs unchanged.
- Measured footprints first: the plinths already were group bounds + 0.7 m sides/back + 1.0 m front (CMP-03 group 8.94 × 5.65 m;
  the "3.5 m front" is the distance from the gazebo steps, the arch and climbers stand ~2 m in front of the steps; CMP-05 right
  margin was 0.7 m from the arch pillar). The visible empty lawn came from the **axis-aligned plinth corner that points at the
  camera** (front-right) in diagonal compositions, plus that corner defining the lowest frame row.
- Wrapper change: plinth = minimum rectangle around the group footprint (convex hull of the item vertices) + margins, optionally
  **turned to the camera view** (`#! cmp … face`: yaw −30°, front edge parallel to the frame bottom, footprint measured in that
  frame). Used for CMP-01, 03, 05, 06 (each improved); CMP-02, CMP-04 (model frame) and Modules stay axis-aligned (turning made
  them worse). CMP-03 / CMP-05 front margin 0.7 m from the front-most item (arch / urn) to bring the front lawn band ≤ 12 %.
- Modules (Fix 2): systems moved together, gaps 0.8–1.0 m (pond +0.5 m right / +0.2 m back, ring next to it, lattice 0.85 m from the
  ring, wall 0.8 m behind the pond and 0.8 m left of the pergola). Plinth 14.15 × 9.20 m (asked ~14.5 × 8.5).
- Camera: same fit (plinth 87 % of the width unless height-limited; tallest point 5 %, plinth bottom 92 %).

| Shot | Plinth (m) | Yaw | Cam dist (m) | Group width | Plinth width | Group rows | Plinth bottom | Front lawn band |
|---|---|---|---|---|---|---|---|---|
| CMP-01 | 6.92 × 5.92 | −30° | 10.7 | 49.9 % | 70.8 % | 5.0–76.8 % | 92.0 % | 15.3 % |
| CMP-02 | 8.40 × 5.93 | 0° | 13.6 | 58.0 % | 65.5 % | 5.0–81.7 % | 92.0 % | 10.3 % |
| CMP-03 | 9.77 × 7.68 | −30° | 12.3 (was 16.2) | **63.3 %** (was 49.1) | **80.8 %** (was 67.8) | 5.0–80.8 % | 92.0 % | **11.2 %** |
| CMP-04 | 7.50 × 7.80 | 0° | 12.0 | 60.7 % | 75.3 % | 5.0–75.4 % | 92.0 % | 16.7 % (unchanged) |
| CMP-05 | 9.28 × 7.79 | −30° | 11.6 (was 12.3) | **65.8 %** (was 62.0) | **87.0 %** (was 72.4) | 14.1–81.2 % | 92.0 % | **10.9 %** |
| CMP-06 | 8.55 × 7.38 | −30° | 11.2 (was 12.9) | 61.8 % (was 53.8) | 84.3 % (was 73.1) | 5.0–76.8 % | 92.0 % | 15.2 % |
| Modules | 14.15 × 9.20 | 0° | 19.2 | 72.6 % | 77.4 % | 5.0–83.6 % | 92.0 % | 8.4 % |

Rounds 5: R1 tightened Modules + oriented min-area plinth (no gain: never ≥ 8 % smaller than axis-aligned) → R2 camera-facing plinth
for all (CMP-03/05/06/01 better, CMP-04/02/Modules worse) → R3 per-shot `face` → R4 front-band measurement → R5 CMP-03/05 front
0.7 m. Renders: AssetStore/CottageGardenDecor/Media/raw/CMP-01…06.png, Modules.png (CMP-02/04 re-rendered identical).

Remaining vs Fix 2: CMP-03 group 63 % ✓ (60–64), plinth 81 % ✓ (80–86), band 11 % ✓; CMP-05 group 66 % (asked 72–78) at plinth 87 %
(width limit; arch top at 14 % instead of 5–6 %), band 11 % ✓, arch 18 % from the right edge ✓; Modules plinth 77 % (asked 84–88 %,
height-limited by the pergola at 42°), CMP-01/06 front band 15 % (> 12 %, accepted frames per the review). The plinth turned 30° to the
compositions shows the beds/walls at an angle to the plinth edge.
