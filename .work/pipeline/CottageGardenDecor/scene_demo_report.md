# Э10 scene Demo_CottageGarden — report (Unity assembler, 2026-11-26)

## Series study (before building)

Sources: `.work/pipeline/CottageGardenDecor/series_media/` (FN cover + Beauty_Garden, FM cover/hero, FP cover/hero/12),
`origin/Farm-Machinery:Assets/Editor/FarmMachinery/{FarmMachinerySceneBuilder,FarmMachineryEnvironment,FarmMachineryLookV2}.cs`
and `FarmMachinery/Lite/Demo/Shaders/{FarmMachinerySky,FarmMachineryCloud}.shader` (read-only).

- Look: floating faceted grass island with a brown soil cut over a pale-blue sky with white low-poly clouds (FN Beauty
  Garden, FM hero/cover); FP/FMk workshop shots use a dark teal flat bg — not for an outdoor garden.
- Sun: one warm directional key (FM v2 `#FFDEB8`-ish, colour 1.0/0.87/0.72, intensity 2.4) from the camera's upper left,
  soft shadows, strength 0.82; FM v2 used a low ~25° sun, FM field ~50°; series shots read best with medium shadows.
- Fill: cool directional fill 0.62/0.70/0.90 at 0.35, no shadows. Ambient: Trilight, sky 0.52/0.60/0.78 (cool shadows),
  equator 0.64/0.56/0.48, ground 0.42/0.35/0.27.
- Sky: own panorama skybox shader (vertical gradient: warm cream horizon → clean blue), all shot cameras clear to the
  skybox; FN Beauty: light grey-blue at the frame top → more saturated blue lower (camera looks down, so the visible sky
  is below the horizon).
- Clouds: separate demo meshes with an unlit gradient-by-normal shader (white tops, cool blue-grey undersides, small
  facet accent from the sun), no shadow casting/receiving, placed around/below the island for depth.
- Camera: 35–40° down, high (≈20 m), vertical FOV 33–40°, island ≈ 85 % of the frame width, sky margins on all sides.
- Shadows: shot render with 4096 shadow map and long shadow distance (FM 120 m for the island); SSAO of PC_Renderer on.
- Post: global Volume — Neutral tonemapping, contrast +16, saturation +6, post exposure +0.2, light bloom (thr 0.8,
  int 0.6, warm tint), vignette 0.18; fog exp2 0.0008 in a warm cream (no veil).
- Applied here: warm key (1.0/0.92/0.80, 1.95, soft, strength 0.78) from the camera's upper left at ~40° elevation
  (`#! sun 0.62 -0.80 0.55`), cool fill 0.45, trilight ambient; gradient sky (horizon 0.76/0.87/0.98 → below 0.50/0.72/0.96),
  white unlit clouds (own copy of the series cloud shader), Volume: Neutral, contrast 15, saturation 16, bloom 0.3, vignette
  0.12; cameras 31–36° vFOV, 36–40° down; island ≈ 72–85 % of the frame width. Lawn keeps the DEM atlas colour (= FN demo
  grass), so it reads lighter/limier than the AI references — series consistency over the reference.

## What was built

- Wrapper `Assets/Editor/CottageGardenDecor/CottageGardenDecorDemoScene.cs` (menu Tools/Cottage Garden Decor/Import Demo
  Environment, Build Demo Scene): runs `PackSceneBuilder.Build(Config, "Demo_CottageGarden.txt", "Demo_CottageGarden")`,
  then the environment step from the `#!` lines of the layout (island + path at the origin, sun, sky, `turn` of a
  composition instance, clouds per shot on the camera ray), removes the builder's flat backdrop (and its material), adds
  the post Volume, zeroes the CMP prefab roots (builder saves them at their scene position; catalogue/series = root
  identity, origin front centre), saves the scene and re-renders the shots. PackTools untouched.
- Demo environment (demo-only, removable): `Assets/CottageGardenDecor/Demo/` — Meshes (3 FBX copied from art/, no .fbm),
  Textures/FMS_Garden_Demo_Atlas.png (point, no mips, uncompressed), Materials (FMS_Garden_Demo_Atlas URP/Lit,
  FMS_Garden_Demo_Cloud, FMS_Garden_Demo_Sky), Shaders (FMS_Garden_Demo_Sky gradient skybox, FMS_Garden_Demo_Cloud),
  Prefabs (FMS_Garden_Demo_Island, _Path, _Cloud_A…E, no colliders, clouds cast/receive no shadows),
  Settings/FMS_Garden_Demo_Volume.asset. No DEM map keys added (placed by the wrapper, not the layout).
- Scene `Assets/CottageGardenDecor/Demo/Scenes/Demo_CottageGarden.unity`: 132 pack prefab instances (6 compositions +
  7 free items), island, path, 3 shot cameras, cloud groups Clouds_Hero (active) / Clouds_Cover / Clouds_AltView.
- Layout: `planning/CottageGardenDecor/layouts/Demo_CottageGarden.txt` (one file: environment lines, shots, free items,
  six `comp` blocks).

## Composition prefabs (Assets/CottageGardenDecor/Art/Prefabs/CMP/, root (0,0,0) / rot 0 / scale 1, 0 colliders)

Counted in Unity from the saved assets (source prefab of every child):

| Prefab | Items | Catalogue | Content check |
|---|---:|---:|---|
| FMS_Garden_Comp_RoseArchEntrance | 13 | 13 | STR-01_Gate 1, PLT-02 2, PLT-03 1, FLB-01_Planted 2, PLT-01 1, PLT-01_Pink 1, MOD-05 4, ORN-02 1 ✓ |
| FMS_Garden_Comp_PergolaTerrace | 17 | 17 | STR-04 1, STR-05 1, PLT-05 4, PLT-03_Pink 1, FUR-03 1, FUR-04 2, MOD-01 2, MOD-02 3, ORN-03_Planted 2 ✓ |
| FMS_Garden_Comp_GazeboRetreat | 14 | 14 | STR-06 1, STR-01 1, PLT-02_Pink 2, FLB-03_Planted 1, PLT-06 2, PLT-06_White 1, PLT-01_White 2, TOP-03 2, TOP-02 2 ✓ |
| FMS_Garden_Comp_FountainParterre | 33 | 33 | WTR-01 1, FLB-02_Planted 4, TOP-02 4, TOP-01_Rose 4, MOD-05 16, MOD-06 4 ✓ (ring 6 × 6 by axis) |
| FMS_Garden_Comp_WalledPondCorner | 33 | 33 | MOD-03 4, MOD-04 4, STR-02 1, WTR-02 1, PLT-04 2, MOD-07 10, MOD-08 4, MOD-09 6, ORN-03 1 ✓ (pond 3 × 2) |
| FMS_Garden_Comp_WildlifeLawn | 15 | 15 | FUR-01, FUR-02, FUR-05, FUR-05_Blue, STR-03, STR-07, WTR-03, ORN-01, ORN-02_Blue, ORN-04, ORN-05, ORN-05_Feeder 1 each, TOP-04 2, TOP-01 1 ✓ |

Free items in the scene (Hero.md «Между композициями»): FLB-01, FLB-02, FLB-03 (empty, where the removed mini-parterre was),
STR-01_White, STR-07_White, FUR-03_White, FUR-04_White (north centre, near the pond) — 7 ✓.
Snap use: pergola bay at STR-04 + 1.5 (needs rot 180 in the layout because PackSceneBuilder turns every item 180°);
edging ring 4 straight per side + 4 arcs on 1 m nodes; pond edges/corners on the 1 m inner grid, water y 0.38 inside;
walls on the 2 m grid with the arch in the skipped span; stela back 0.22 from the wall axis; ivy back on the coping face
(0.221); wisteria under the front beam (y 2.24), garlands on the beam top (2.46) / arch top (2.40); climbers on the outer
faces of the arch side panels (x ±0.72).

## Renders (clean, no text) — AssetStore/CottageGardenDecor/Media/raw/

| Shot | File | Size | Camera | Rounds |
|---|---|---|---|---|
| Hero (05_Hero) | Hero.png | 1920×1080 | from S (8° east), 40° down, vFOV 31; island 10–91 % × 17–95 % | 5 + final check render |
| Cover (03_Cover) | Cover.png | 1950×1300 | from SSW, 37° down, vFOV 35; island lowest point at 76 %, gazebo at x 52 % | 4 |
| AltView (10_DemoAndVersion) | AltView.png | 1920×1080 | from NW, 36° down, vFOV 36; island 14–86 % × 18–98 % | 5 + final check render |

Rounds: R1 first build (bay mirrored, island cropped, lawn too bright) → R2 bay rot 180, cameras pulled back, Cover moved
to SSW, darker exposure → R3 closer cameras, CMP-01/CMP-06 moved closer to the path → R4 centring/FOV, cloud tidy → R5 Hero
centring, AltView from NW instead of WNW; final pass = framing only (Hero vFOV 31, AltView target) + CMP root zeroing (no
visual change).

## Remaining differences vs the references

- STR-01_Gate prefab is an all-white arch (the reference/CMP-01 PNG show a wooden arch with a white leaf) — model as
  approved, not changed in Unity.
- Cover: Cover.md names ENE; round 1 from ENE showed the gazebo's back (its entrance faces SW to the path end). Final camera
  from SSW = composition of the chosen Cover.png (gazebo high in the centre, pond top left, entrance bottom left, wildlife
  right), different angle from Hero. Orchestrator/reviewer may want ENE anyway.
- AltView: AltView.png is not consistent with the map (seen from W with the walls behind the pond); render follows
  AltView.md (NW, pond in front, gazebo left behind the path). The walled corner is seen from the outer side of its L wall;
  the iron arch is in the north wall, not facing the path branch.
- Gazebo reads smaller than in the AI references (true 3.58 × 4.0 m); it is still the tallest red accent.
- CMP-03 instance is turned 30° in the scene (`#! turn`) so its steps meet the demo path end; the prefab itself is axis-aligned
  (front = −Z).
- Climbing roses PLT-02 sit on the outer side faces of the arches (model mount contract), not on the post fronts as in
  CMP-01.png; four wisteria drapes overlap ~0.2 m along the 6 m beam.
- Some open lawn between the path and CMP-06/CMP-04 (the references are denser); lawn lighter than in the references (see above).

## Notes / not blocked

- Unity: two Editors answer on port 7800 (this project and D:\GitProjects\Carswarnew); `--project-path .` works, one submit
  failed with "Unauthorized" right after a recompile and passed on retry.
- `ProjectSettings/URPProjectSettings.asset` shows as modified in `git status` with an empty content diff (Editor touch);
  not edited by me. No git writes.
- Composition vignette renders (CMP-0x shots) were not part of this portion.

## Fix 1 (2026-11-26, review renders_1)

Inputs: reviews/renders_1.md, `## Fix 1` of scenes/Hero.md, Cover.md, AltView.md, Synty reference (synty_ref text + img_06,
img_49, img_107 looked at), DEM notes «Fix 1 (renders_1)».

**Demo assets.** The 3 rebuilt FBX + demo atlas (md5 8d6d6323…, lawn #7DB93C) copied over the Unity copies in place (.meta /
GUIDs kept), Refresh; demo prefabs pick up the new meshes (Island 996 tris, lawn x -10.29..10.04 / z -8.07..8.15; Path 308
tris). Nothing re-imported by hand, no new demo assets.

**Layout** (`planning/CottageGardenDecor/layouts/Demo_CottageGarden.txt`, re-spaced into x -9..9 / z -6.75..6.75, checked with
a top-down footprint script: no overlaps between groups/free items, no item off the lawn, only intended path overlaps =
gazebo deck over the path tip and the rose arch over the path):
- Zones kept: SW CMP-01, W CMP-02, NW CMP-05, E CMP-04, SE CMP-06, N/NE CMP-03 (gazebo faces S, steps on the last path
  segment, path tip under its deck; the 30° `turn` of round 1 is gone).
- Compositions keep their content (counts re-checked in Unity: 13 / 17 / 14 / 33 / 33 / 15 = catalogue, roots (0,0,0),
  0 colliders). Re-saved because item positions changed: CMP-01 2.9 → 2.7 m deep (arch z 1.9, beds/bushes closer);
  CMP-03 re-arranged around the gazebo (no room for the 7 x 7 m vignette layout: flowers on both flanks, round bed and
  spiral/cone/hollyhock NE of the gazebo, rose arch turned 35° to straddle the path); CMP-05 L-wall 0.6 m shallower
  (arms still 2 segments, gap 1.5 m with STR-02, stela back 0.22 from the wall axis, ivy on two segments); CMP-06 compacted
  8.3 x 5.2 → 7.5 x 4.4 m (hammock and loungers 1–2 m nearer the front edge); CMP-02, CMP-04 unchanged inside.
- Free items: the 7 required (3 empty beds now as a bed group right of the path + one at SE corner, white arch / obelisk /
  table / chair moved to the NE corner — away from the gazebo front) + 11 densify items: TOP-02 ×2, TOP-01 ×2 along the
  edges, PLT-01 / _Pink / _White near the front edge, FLB-01_Planted ×2 (fork east + front centre), TOP-04 ×2 (by the
  swing and SE). 143 objects in the scene (132 + 11).
- **Not met:** gaps between compositions are 0.5–1.1 m (Fix asked 1.5–2.5) and several edge items are 0.2–0.5 m from the lawn
  edge (asked 0.8–1.5): the six compositions (~210 m² of footprints) + path + 18 free items do not fit an 18 x 13.5 m garden
  with those gaps. The garden bbox covers x -9.6..9.5, z -7.4..7.5 (≈ 90 % of the lawn top).

**Look.** Lawn: atlas #7DB93C, post saturation 16 → 0, post exposure 0 → -0.15, sun 1.95 → 1.6 and less warm
(1.0/0.95/0.88); lit lawn now reads #88BC43–#95C652 (was #A5D24F / #95C933). Sky top bluer (zenith 0.46/0.68/0.95, horizon
0.70/0.84/0.98). Clouds: no cloud on island corners; Hero 4 (top corners + far sides), Cover 4 small top clouds clear of
the gazebo, AltView 2 at the upper right (upper-left corner clean for the composition block). Shadows/key unchanged.

**Shots** (measured: island/gazebo = projected mesh vertices in Unity; plate = lowest non-sky pixel row of the PNG):

| Shot | Camera | Island width / rows | Gazebo width / rows | Plate / bottom | Rounds |
|---|---|---|---|---|---|
| Hero | S 8° E, 40° down, vFOV 31 | 83.9 % (x 8–92), y 16–94 % | 12.0 % (x 55–67), apex 5 % | lowest pixel 93.9 % | 5 |
| Cover | SSW (200°), 30° down, vFOV 31 | 82.7 % (x 11–94), y 18–75 % | 11.0 % (x 44–55, centre 49.5 %), apex 7 % | lowest non-sky row 970/1300 = 74.6 % (rows 971–1300 clean sky) | 4 (+ unchanged re-render) |
| AltView | NNW (335°), 33° down, vFOV 33 | 89.0 % (x 2–91), y 13–96 % | 16.6 % (x 22–39) | lowest pixel 96.1 % | 5 |

Rounds: R1 first frame on the new island (bottoms cropped, lawn #95C933) → R2 distances/targets, sun 1.7 → R3 fit
(Cover wide/low, AltView cropped) → R4 Cover plate + apex, AltView up, saturation 0, sun 1.6 → R5 Hero top margin,
AltView down 3 %.

**Remaining differences vs Fix 1**
- Island width: Hero 84 % (asked 88–92), Cover 83 % (asked 90–94); gazebo 12 % / 11 % (asked ≥ 13–16 %). With the gazebo near
  the north edge its 4 m height sticks out above the far edge: at 40° (Hero) / any pitch with the Cover plate rule
  (island + gazebo inside 7–76 % of the height) the island cannot be wider without cutting the gazebo apex or the plate.
  Cover pitch lowered 37° → 30° to gain width (outside the cross-cutting 35–40° rule). AltView meets 86–90 %; its soil
  bottom is at 96 % (asked 93–95).
- Gaps / edge margins smaller than asked (see Layout). CMP-03 prefab arrangement now differs from CMP-03.png (flowers around
  the gazebo, angled arch) — the vignette stage may want its own arrangement.
- AltView is from NNW (not "towards W"): CMP-05's arch passage runs N–S, so the arch opening reads only when looking roughly
  along it; from W it is edge-on. Stela is inside the L (faces E), seen from above/behind the wall.
- Known model points (not blockers): STR-01_Gate all white; climbers on the arch side faces.

## Look (2026-11-26, owner: "красивый постпроцессинг, продающая картинка")

One shared look for every render of the pack: `Assets/Editor/CottageGardenDecor/CottageGardenDecorLook.cs` + URP Volume profile
`Assets/CottageGardenDecor/Demo/Settings/FMS_Garden_Look.asset` (package components only; the old
`FMS_Garden_Demo_Volume.asset` removed). Demo_CottageGarden re-rendered by `CottageGardenDecorDemoScene.Relook()` (menu
"Re-render Demo Scene (look only)"): opens the saved scene, swaps lights/Volume, re-renders — cameras, layout and CMP prefabs
untouched (framing numbers identical to Fix 1; Cover lowest non-sky row still 970/1300 = 74.6 %).

| Setting | Value | Why |
|---|---|---|
| Tonemapping | ACES | A/B with Neutral (round 2): Neutral pushed the lit lawn to s 0.83 (#90CD23, lime) and warmed the whites; ACES kept lawn s 0.71 and white paint neutral |
| Color Adjustments | post exposure +0.28, contrast +14, saturation +10 | ACES darkens: exposure restores brightness; contrast/saturation for a crisper selling read; whites ≤ v 0.89 (not blown), soil cut v 0.49 (no crushed blacks) |
| White Balance | temperature 0, tint 0 | +6 (round 1) turned the lawn yellow; warmth comes from the key colour and split highlights |
| Split Toning | shadows (0.42, 0.48, 0.60), highlights (0.58, 0.53, 0.46), balance −10 | cool shadows / warm lit surfaces (Synty «Свет и гамма») |
| Color Curves | Hue vs Hue: hues 61–101° pulled +10° towards green (peak at 81°) | lit lawn drifted to yellow-green (81–84°) under the warm key; now 87–93° (atlas lawn #7DB93C = 92°); reds, sand, gold, blue outside the curve |
| Bloom | threshold 1.0, intensity 0.3, scatter 0.6, tint (1.0, 0.92, 0.80), HQ filtering | only HDR highlights (white paint / water edges in full sun), no glow on the lawn |
| Vignette | 0.15, smoothness 0.45, dark violet-grey | subtle frame focus |
| Key light | colour (1.0, 0.94, 0.85), intensity 1.7, soft shadows, strength 0.78, direction (0.62, −0.80, 0.55) ≈ 44° from the upper left | warm lit faces, readable facets |
| Fill / ambient | cool fill (0.66, 0.76, 0.95) 0.45; trilight sky (0.60, 0.70, 0.86), equator (0.66, 0.62, 0.54), ground (0.40, 0.36, 0.30) | cool shadows |
| Aerial depth | exp2 fog 0.003 in (0.78, 0.86, 0.96), Demo_CottageGarden only | slight distance haze; 0.006 (round 1) greyed the island |
| Render settings | 4096 shadow map, shadow distance 60 m, 2x supersampling + MSAA x8 (PackSceneBuilder.Render); SSAO of PC_Renderer raised 0.4/0.3 → 0.7/0.35 for the shot only (reflection, restored after, asset not dirtied — verified) | contact shadows under furniture, pots and beds |
| Not used | DOF, grain, chromatic aberration, custom render features | REQUIREMENTS 7.6 |

Palette check (Hero, same pixels, median 9×9, before → after): roof red #D85D51 → #EF5843 (hue 5 → 7°), lawn lit #8FC34A →
#8FD13D (hue 86 → 87°), lawn far #679B3B → #5DA224 (92 → 93°), stone #A49C8F → #AEA492, water #5989B8 → #478AC7, sand #DBC192 →
#ECCF96, white rail #D5D0C7 → #E4DED1 (s 0.07 → 0.08), soil cut v 0.51 → 0.49, sky #81AACE → #82B2DC: hues within ±2°, slightly
brighter and more saturated, palette recognisable.

Rounds: R1 Neutral + WB +6 + fog 0.006 (washed, hazy; also an invisible-island render, fixed by disabling async shader
compilation during the offscreen render) → R2 Neutral vs ACES A/B → R3 ACES + hue curve 6° → R4 contrast 14, exposure 0.28,
sun 1.7, hue 10° (accepted). Compared at 100 % / 50 % with Synty img_104, img_105.
Before/after: `.work/pipeline/CottageGardenDecor/look/before_*.png`, `after_*.png`, `pair_*.png` (side by side, 50 %); final files
overwrite `AssetStore/CottageGardenDecor/Media/raw/Hero.png, Cover.png, AltView.png`.

## Look v2 (2026-11-26, review renders_2)

Steps of renders_2 §1 applied in CottageGardenDecorLook / CottageGardenDecorDemoScene (Volume FMS_Garden_Look regenerated):

| Setting | v1 | v2 (final) |
|---|---|---|
| Key light | 1.6 (the layout `#! sun` value overrode the look's 1.7 in v1 — now the look value always wins) | **1.95**, colour (1.0, 0.94, 0.85), direction (0.62, −0.80, 0.55) |
| Fill | 0.45 | **0.38** (0.66, 0.76, 0.95) |
| Shadow strength | 0.78 | **0.88** |
| Ambient trilight | sky (0.60, 0.70, 0.86), equator (0.66, 0.62, 0.54) | sky **(0.70, 0.80, 0.96)**, equator **(0.68, 0.66, 0.60)**, ground (0.40, 0.36, 0.30) — cooler/lighter lawn shadows (not in the review list; used instead of lowering contrast) |
| Tonemapping | ACES | ACES |
| Post exposure / contrast / saturation | +0.28 / +14 / +10 | **+0.05** (step 5: lawn was > #9BD84E at +0.28 and +0.15) / **+18** / **−4** |
| Color Curves | hue-vs-hue +10° (61–101°) | hue-vs-hue **+14°** peak at 81°; **hue-vs-sat** reds 0–15° and blues 200–225° at **0.65** (= +0.15) |
| Split toning | (0.42,0.48,0.60) / (0.58,0.53,0.46), −10 | **(0.36, 0.44, 0.62) / (0.62, 0.55, 0.44), −15** |
| White balance / bloom | 0 / 0.3, thr 1.0 | unchanged |
| Vignette | 0.15 | **0.20** |
| Sky (Demo_CottageGarden) | flat ~#82B2DC | frame top deep → bottom light: shader horizon (0.29, 0.52, 0.79), below (0.86, 0.93, 0.99), power 1.6; fog 0.003 in (0.74, 0.84, 0.95) |
| Render target | PackSceneBuilder.Render (ARGB32 → URP took an LDR camera colour buffer, scene clamped at 1.0 before ACES) | **CottageGardenDecorLook.RenderHdr** (DefaultHDR target, same 4096 shadows / MSAA / 2x supersampling); found while the backdrop would not get lighter than #DBDAD8 |

Measured on Hero (lawn = 70–90th / 3–12th percentile of lawn-hue pixels; palette = same median 9×9 points):
- lawn lit **#94D35C** (h 92, s 0.56, v 0.83; target #86C24A, ≤ #9BD84E ✓, s ≤ 0.65 ✓), lawn shadow **#478035** (h 106, s 0.59,
  v 0.50; target #4F8F2E / blue-green #3F7F4A). Lit is ~8 % brighter than the target with key 1.95 / exposure +0.05; reaching
  #86C24A exactly would need either a lower key or a darker atlas lawn cell (builder) — not changed.
- roof red #FC452D (v 0.99 ✓, hue 7°), water #3187D0, white rail #E5E0D5 (s 0.07), stone #A8A092, soil cut v 0.50, sky top
  **#5388C7** (s 0.58 ✓; target #5E98D4), sky frame bottom #A7BCD2 (target #BFD9F0: lighter values greyed out after ACES).
- Cover lowest non-sky row 970/1300 = 74.6 % ✓; framing of all three shots unchanged (projected shares identical to Fix 1).

Rounds: R1 all review steps (lawn #9ADA63 too bright) → R2 exposure +0.15 + lighter sky bottom (#95D35C) → R3 exposure +0.05 +
deeper sky top → R4 contrast 12 test (shadows unchanged, roof v 0.88 → rejected) → R5 contrast 18 + cooler ambient (accepted);
then a correction pass after the HDR render fix (demo values unchanged by it, roof v 0.91 → 0.99).
Before/after: `.work/pipeline/CottageGardenDecor/look/before_*.png` (= v1 files), `after_*.png`, `pair_*.png` for all ten media
files; v1 pairs kept in `look/r1/`.
