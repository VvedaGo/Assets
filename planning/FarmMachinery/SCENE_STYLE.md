# FarmMachinery — scene style (Э10, 2026-11-24)

Owner instruction: scenes and renders must read as the same series as the successful packs (environment, gamma,
presentation). Study done read-only (`git show`), copies for viewing in `%TEMP%/farmmachinery_style/` (small/ = 1000 px).

## What the series does

| Pack | Environment | Light | Camera / framing |
|---|---|---|---|
| Farm Market Starter (`FarmMarket`) | Outdoor diorama: textured grass, dirt and cobble ground, hay bales and lamps; gradient sky (zenith 0.34/0.55/0.86, horizon 0.95/0.90/0.80), linear fog 45–160 m | Warm sun (1.0, 0.87, 0.70) ×2.0, soft shadows 0.82; trilight ambient sky (0.66, 0.76, 0.92) / equator (0.78, 0.70, 0.58) / ground (0.44, 0.37, 0.27); post-processing on | High ¾ view 35–60° down, FOV 36; the whole set fills the frame, warm saturated colours |
| Farm Processing (`Farm-Processing`, same PackSceneBuilder as this pack) | Workshop bay on a flat teal backdrop **(23, 60, 69)** (`ground` = `bg`); catalogue / compositions on light grey **(233, 233, 236)** | PackSceneBuilder: warm golden key from the upper left (1.0, 0.84, 0.62) ×2.6, soft shadows 0.85; cool fill from the right (0.55, 0.80, 0.98) ×0.7; trilight ambient (0.45, 0.58, 0.66) / (0.44, 0.40, 0.36) / (0.30, 0.30, 0.30); no post | Hero 40–55° down, FOV 37; close-ups FOV 30–33; compositions centred with wide clean margins |
| Farm Nature (`Farm-Nature`) | Floating low-poly island on a pale sky-blue gradient with low-poly clouds | Soft daylight from the upper left, light contact shadows | ¾ view ~35° down, island fills ~80 % of the width |

What made them look good: one warm key from the upper left with soft but present contact shadows plus a cool sky fill
(never flat, never black shadows); calm, slightly desaturated large surfaces so the saturated models carry the colour;
a single consistent ¾ high view; every silhouette complete with a clean margin; no text in raw renders; a flat
light-grey catalogue background **#E9E9EC** (REQUIREMENTS) for item sheets.

## FarmMachinery rules (to read as the same line)

- **Light (neutral / catalogue; field scenes use "URP look" below):** PackSceneBuilder lights unchanged (= Farm Processing): key (1.0, 0.84, 0.62) ×2.6 from the upper left of the
  layout (direction 0.75, −1.1, 0.55), soft shadows 0.85; fill (0.55, 0.80, 0.98) ×0.7; trilight ambient as above; no fog,
  no post. Shadow map 4096, distance 60 m during renders (PackSceneBuilder.Render).
- **Field scenes (Demo_FieldWork, Demo_Harvest, Hero/Cover):** since 2026-11-24 the ground is the demo island DEM-01
  (64 × 44 m, grass top, soil skirt) with field / road modules DEM-02…04 lying 0.01 m above it and DEM-05 tufts scattered
  on the free grass; the island floats in the sky colour (Farm Nature-like island, Farm Market-like lively grass). The
  earlier flat plane with colour zones is kept only as layout grammar (`#! plane`, `#! zone`). No Farm Nature / Farm Market
  assets, no bales.
- **Catalogue / item sheets:** `bg 233 233 236`, `ground 233 233 236` (as Farm Processing catalogue shots).
- **Gamma:** Linear colour space, URP, no tonemapping. Ground base colours are set darker and cooler than the target tones
  because the warm key brightens and warms them; calibrated on Demo_FieldWork round 1 (target → base):
  route 210 191 167 → 146 146 147, stubble 177 184 157 → 122 141 137, soil 182 137 115 → 125 102 98. Measured on the
  accepted render: route 208 188 165, stubble 177 182 154, soil 181 135 113, sky 165 182 202.
- **Cameras:** overview ¾ 30–40° down, FOV 37–38, horizon line in the top ~15–20 % of the frame, yaw ~20° to the main
  lane so rows read diagonally; close-ups FOV 26–30, 35° down, other groups out of the frame. Clean margin ≈ 5 %.
- **Machines** face screen-left (layout `rot 90`) in field scenes, like the scene references.

## Layout directives used (PackSceneBuilder grammar + `#!` lines of FarmMachinerySceneBuilder)

```
#! look field                         # URP look
bg 173 191 217                       # sky around the island
#! plane off                          # no PackSceneBuilder plane: the island is the ground
#! env DEM-01 0 0 0 0                 # island, centred on the origin (env rotY = plain Euler Y)
#! envrow DEM-04 -24.86 1 27.26 1 7 90 0.01 1 1.0857   # road edge to edge (modules stretched to 8.686 m)
#! env DEM-02 -9 -9.5 90 0.01         # ploughed field, furrows along x, under CMP-01
#! env DEM-03 7 -10.5 90 0.01         # stubble field, rows along x (along z they stripe in the overview)
CMP-01 -10.5 -13 90 0.01             # machines on modules stand at y 0.01, on the grass at y 0
#! scatter DEM-05_Grass:7,DEM-05_Flowers:1,DEM-05_Rock:0.4 1500 7 -32 -22 32 22 0.7 1.4      # sparse base
#! cluster DEM-05_Grass:5,DEM-05_Flowers:4,DEM-05_Rock:0.4 90 14 1.0 11 -32 -22 32 22 0.8 1.6 # clumps
#! border DEM-05_Grass:7,DEM-05_Flowers:2,DEM-05_Rock:0.5 260 0.8 21 -15 -17.5 -3 -1.5 0.8 1.6 # field edge band
shot Overview -15.61 32.12 -38.73 -4 0 -5 38
shot CloseCMP01 -12.4 8.9 -24.3 -10.4 0.9 -13 26
shot Beauty -29.1 3.5 -17.0 -12.5 1.2 -13 28
```
Catalogue scenes: `bg 233 233 236` / `ground 233 233 236`, no `#! look`, no environment.

## URP look (field scenes, 2026-11-24, owner: "сочнее картинка")

Switched on per layout with `#! look field` (FarmMachinerySceneBuilder); without it a scene keeps the neutral PackSceneBuilder
light and no post (catalogue / item sheets: `bg 233 233 236`, `ground 233 233 236`). `#! shotlook <shot> neutral` turns post
off for one shot of a field scene. Nothing in PackTools or in the shared URP assets (`Assets/Settings/PC_RPAsset`,
`PC_Renderer`) was changed.

- **Volume** `Assets/FarmMachinery/Demo/Settings/FarmMachinery_DemoVolume.asset`, global `Look_Volume` (priority 10) in the
  scene, post-processing on the shot cameras (values of 2026-11-24, environment round 3):
  - Tonemapping **Neutral** (ACES turned the series red #C8473B orange: body hue 13.6° vs 5.1° in the atlas);
  - Color Adjustments: post-exposure **0.0**, contrast **+22**, saturation **+14** (+22 made the island grass lime);
  - White Balance: temperature **−8**, tint 0 (cools the warm sun back so the red stays red and the grass green);
  - Bloom: threshold **1.0**, intensity **0.25**, scatter 0.6;
  - Vignette: intensity **0.12**, smoothness 0.45.
  - SSAO: already active on the shared `PC_Renderer` (renderer feature, Intensity 0.4, radius 0.3) for all content — left as
    it is, no separate SSAO.
- **Light** (FarmMarket demo values): Key_Sun colour (1.0, 0.87, 0.70) ×**2.0**, soft shadows, strength **0.82**, direction
  as PackSceneBuilder (upper left); Fill_Sky (0.55, 0.80, 0.98) ×**0.5**; ambient Trilight sky (0.66, 0.76, 0.92) / equator
  (0.78, 0.70, 0.58) / ground (0.44, 0.37, 0.27). **Fog off** (URP linear fog 45–160 m greyed the whole overview); renders by
  `FarmMachinerySceneBuilder.RenderShot` with a 120 m shadow distance (PackSceneBuilder.Render uses 60 m — too short for the
  island).
- **Body red** (median hue of saturated red pixels): atlas #C8473B 5.1°, Farm Market reds ≈ 2–6°, Farm Processing ≈ 8°;
  FarmMachinery before = 7.7° (no post), ACES look = 13.6° (orange), final = **6.9°** (CloseCMP01) / **7.5°** (Overview).
  No clipped pixels (no channel ≥ 252 anywhere, cream rims included).
- Known limits vs Farm Market: its grass is a textured carpet with highlight tips and its plaza is packed with props and
  bunting; ours is flat faceted grass (two close greens) with scattered 3D tufts, the large field modules read flat from the
  overview, and its golden light / bloom is stronger.

## Demo scene recipe (from Demo_FieldWork polish, 2026-11-24 — use for the other scenes)

1. **Ground** = island DEM-01 at the origin + modules (DEM-02 ploughed, DEM-03 stubble, DEM-04 road) at y **0.01**; turn field
   modules so furrows / rows run along the driving direction; roads run edge to edge (stretch modules with `sx sz` so the
   ends meet the island edge, no overhang). Machines on modules at y 0.01, on grass at y 0. `#! plane off`, `bg 173 191 217`.
2. **Demo atlas** `T_FarmMachinery_Demo_BaseColor` (art/ and Assets/ copies byte-identical; machine atlas untouched), cells
   changed on 2026-11-24: 0 grass light **#375F0F**, 1 grass dark **#2C520C** (was #6F9A43 / #557D33: lime), 5 road
   **#9A8F80**, 6 rut **#7D7268** (warmer than grey), 7 straw light **#A28C58**, 8 straw dark **#94804F**, 15 stubble ground
   **#8C7A50** (low contrast: no stripes / moiré at overview distance). Note: the `.fbm` copies next to the FBX in
   art/FarmMachinery/Demo/Meshes still hold the old atlas (not used by Unity).
3. **Rendered targets** (measured on the accepted renders vs Farm Market 10_Demo_Scene): grass hue **96°**, sat **0.80**, val
   **0.43** (p25 0.41, p75 0.49), median rgb (53, 110, 24) — Farm Market 97° / 0.84 / 0.44, (56, 111, 22). Body red hue
   6.9–7.5° (atlas 5.1°). No pixel with a channel ≥ 252.
4. **Scatter density** (DEM-05 props, only on free island grass): base `scatter` ≈ 1 try per 1.9 m² of the rectangle (half land
   on free grass); `cluster` 90 clumps × 14 (σ 1.0 m, 0.5–1.5× per clump) per ~2200 m² of grass; `border` bands 0.8 m wide
   outside every field (~4.6 tries per metre of perimeter: 260 per 12 × 16 field) and road (500 along a 61 m road, both
   sides); weights grass 7 : flowers 1–2 (4 in clumps) : rocks 0.4–0.5; scale 0.7–1.6, height stretch 0.85–1.25. Result on
   the 64 × 44 island: **2325 props**, 2493 renderers, 284k tris in the scene, one 1920×1080 shot (2× supersampled) renders in
   ~0.15 s. Keep rocks rare — many white flowers / grey rocks read as noise from the overview.
5. **Cameras**: overview fills the frame with the island (far edge ~9 % from the top, soil skirt at the bottom), yaw ~19°,
   ~42° down, FOV 38; close-up FOV 26, 35° down; beauty low (3–4 m) from outside the island with its soil edge in the frame,
   yaw chosen so that no other group overlaps the hero silhouette (check by projecting the group boxes, as done here).
6. **Look**: `#! look field` (Volume and light above). Compare every render next to the Farm Market demo; measure grass and red.
7. **Sky and clouds** (owner 2026-11-24: "найди скайбокс получше, все однотонно" -> the series' own Farm Nature solution, own
   copy, no Farm Nature dependency, no photo HDRI): `#! sky 1` = skybox `M_FarmMachinery_Sky` with shader
   `FarmMachinery/Demo/URP Panorama Sky` (Assets/FarmMachinery/Demo/Shaders/FarmMachinerySky.shader, latitude-longitude) and
   the panorama `T_FarmMachinery_SkyPanorama` (512 px vertical gradient, sRGB, no mips, bilinear, V clamp; script-made).
   Rows (0 = zenith, 256 = horizon): 0 **(84, 140, 220)**, 90 (100, 154, 224), 170 (130, 176, 232), 215 (160, 196, 238),
   234 **(190, 214, 242)** light blue ~8 deg above the horizon, 247 (246, 226, 196), 256 **(255, 224, 178)** warm cream horizon
   (saturated, the grade cools it), 262 (236, 230, 220), 285 **(196, 219, 242)** haze below the horizon, 350 (166, 200, 237),
   430 (146, 188, 234), 511 (138, 182, 232). A low camera sees only rows ~237..256 (0..6 deg): keep that part a thin warm band
   plus saturated light blue — a wide cream band read flat grey after WB -8. Ambient stays Trilight. Field-look shot cameras
   clear to the skybox; catalogue / neutral shots keep the solid `bg`.
   **Clouds** DEM-06 (art/FarmMachinery/Demo/Meshes/FMS_Mach_Demo_Clouds.fbx, 4 low-poly clouds A..D, 6–15.5 m) imported to
   Demo/Environment as DEM-06_A..D with `M_FarmMachinery_Demo_Cloud` = shader `FarmMachinery/Demo/Cloud`
   (FarmMachineryCloud.shader: unlit gradient by the face normal — top (1, 1, 1), sides (0.90, 0.93, 0.98), undersides
   (0.72, 0.80, 0.92), facet accent 0.08 from the main light; a lit material took the warm key and the brown trilight ground
   and read beige-brown), no shadows cast or received. `#! clouds count seed dMin dMax yMin yMax sMin sMax` puts them on an
   elliptical ring around the island (half axes 32 + d, 22 + d): Demo_FieldWork uses a low ring `18 5 3 22 -14 -3 0.9 1.6`
   (around and under the island edge) and a far ring `12 9 22 50 -2 4 1.2 2.2` (around the horizon, below the eye level of
   low cameras). The overview shows the whole floating island (outline and soil skirt fitted with ~8 % margin, 30 deg down).
8. **Dense, large machines** (owner 2026-11-24, twice: "кучнее, объекты близко друг к другу, масштабнее"): rows and groups
   **0.8 m apart box to box** (attached pairs by their points), compositions packed with a 0.7 m gap (CMP-03 = two dense
   parking lines, 6.3 x 25.8 m instead of one 50 m line; CMP-05 groups side by side, 17.7 x 19.7 m); every shot fitted to the
   machine boxes with a **3 %** margin (scratch tool scene_fit.py: yaw / pitch / FOV from the scene reference, distance and
   look point solved; lower the pitch to 30–36 deg when the fit is height-limited so the machines fill the frame width too).
   Card shots keep the bottom 38 %, Cover shots the bottom 25 % free (calm grass, no props in front of the hero). Card/Cover
   heroes stand at rot 60–70 (nose left and towards the camera), seen in 3/4 (yaw 24 for Card); keep the hero out of the
   silhouette of the group behind it (shift it sideways rather than spreading the scene).

## Scene layouts (2026-11-24)

| Scene | Layout | Shot (size) | Render (AssetStore/FarmMachinery/Media/raw/) |
|---|---|---|---|
| Demo_FieldWork | layouts/Demo_FieldWork.txt | Overview, CloseCMP01, Beauty (1920×1080) | Demo_FieldWork_*.png |
| Hero_Lite | layouts/Hero_Lite.txt | Hero (1920×1080) | Hero_Lite_Hero.png |
| Cover_Lite | layouts/Cover_Lite.txt | Cover (1536×1024, bottom 25 % free) | Cover_Lite_Cover.png |
| Card_Lite | layouts/Card_Lite.txt | Card (1536×1024, bottom 38 % free) | Card_Lite_Card.png |
| Hero_Full | layouts/Hero_Full.txt | Hero (1920×1080) | Hero_Full_Hero.png |
| Cover_Full | layouts/Cover_Full.txt | Cover (1536×1024, bottom 25 % free) | Cover_Full_Cover.png |
| Card_Full | layouts/Card_Full.txt | Card (1536×1024, bottom 38 % free) | Card_Full_Card.png |
| Demo_Harvest | layouts/Demo_Harvest.txt | Overview (1920×1080) | Demo_Harvest_Overview.png |

MEDIA v2 (look v2, 2026-11-24) — Media/raw names: Demo_FieldWork_{Overview,Beauty,CloseCMP01,LowNode_Plough},
Demo_Harvest_{Overview,Beauty,CloseHaymaking,CloseGrainYard,LowNode_Header} (1920×1080), Hero_Lite / Hero_Full (1920×1080),
Cover_Lite / Cover_Full (1950×1300, bottom 22 % free), Card_Lite / Card_Full (1260×840, bottom 37 % free), Icon_Lite /
Icon_Full (1024×1024, layouts/Icon_*.txt), Social_Lite / Social_Full (1200×630, `shot Social` of Hero_Lite / Hero_Full).

## URP look — soft (candidate)

Owner 2026-11-24: "поищи пост-процессинг, чтобы были более мягкие цвета, как в референсе" (mood reference:
planning/FarmMachinery/SYNTY_ASSET_STORE_VISUAL_REFERENCE.html, Synty Farm scenes 03/05/06/11 — read-only, never copied).
Switched on with `#! look soft` (FarmMachinerySoftLook.cs) or `FarmMachinerySceneBuilder.Build(scene, suffix, "soft")` for
A/B; the 'field' look, its Volume, sky material and demo atlas stay untouched.

- **Light (golden hour):** Key_Sun turned lower, direction (0.75, -0.62, 0.55) ≈ 33 deg elevation (field ≈ 50), colour
  (1.0, 0.80, 0.58) ×2.3, soft shadows strength 0.75; Fill_Sky cool (0.55, 0.68, 0.95) ×0.45; ambient Trilight cool sky
  (0.50, 0.58, 0.75) / equator (0.64, 0.56, 0.50) / ground (0.40, 0.34, 0.28) — warm lit surfaces, cool shadows.
- **Aerial haze:** fog ExponentialSquared, density 0.0022 (≈ 2 % at 60 m, 7 % at 120 m: near machines crisp), colour warm
  cream (0.95, 0.88, 0.80).
- **Volume** `Assets/FarmMachinery/Demo/Settings/FarmMachinery_DemoVolume_Soft.asset`: Tonemapping Neutral; Color Adjustments
  post-exposure +0.05, contrast +8, saturation 0; White Balance temperature 0, tint +2; Split Toning shadows (0.40, 0.52,
  0.62) cool, highlights (1.0, 0.86, 0.70) warm, balance +10; Lift-Gamma-Gain lift (1.0, 0.99, 1.02, 0) (shadows a touch
  cool, not lifted), gain (1.02, 1.0, 0.97, 0); Bloom threshold 0.85, intensity 0.5, scatter 0.7, tint (1.0, 0.93, 0.82);
  Vignette 0.16 / 0.5.
- **Sky** `M_FarmMachinery_Sky_Soft` + `T_FarmMachinery_SkyPanorama_Soft` (same panorama shader): zenith (96, 146, 212) ->
  (118, 164, 220) -> (156, 190, 228) -> (198, 208, 226) ~10 deg -> narrow cream-pink band (240, 216, 204) / horizon
  (248, 222, 200) -> pink haze (236, 218, 212) / (214, 212, 224) -> (184, 198, 226) -> bottom (160, 184, 222).
- **Demo palette (soft only):** `M_FarmMachinery_Demo_Soft` + `T_FarmMachinery_Demo_BaseColor_Soft` swapped onto the
  environment of the scene: grass light #5A6E28 / dark #4B5E22 (calm olive), straw #B29660 / #A08656, stubble ground
  #967E54 (soft ochre) — calmer than the red body and the cool glass (Synty text: "оливу и солому спокойнее красного
  корпуса и холодного стекла").
- **Measured** (A/B round 3): grass hue 64–70 deg, sat 0.33–0.41, val 0.40–0.46 (Synty Farm 62–65 / 0.31–0.34; our field
  look 94–100 / 0.73–0.80); lit body red 8.6–9.3 deg (field 6.7–7.1; round 2 with a less warm sun gave 5–6); luma p5 58–106,
  p50 124–151 (Synty 51–70 / 115–130: ours still a bit lighter / hazier); no clipped pixels. A/B sheet:
  %TEMP%/farmmachinery_scene/AB_soft_vs_field.png.
- Status: candidate — superseded by LOOK v2 below (kept for A/B).

## URP look — v2 (accepted media grade, MEDIA v2 2026-11-24)

Owner 2026-11-24 "добавь, да, везде как считаешь нужным" (scenes/changes/00_LOOK_v2.changes.md; mood: Synty 014 / 006 / 008,
read-only). `#! look v2` (FarmMachineryLookV2.cs) in every layout; 'field' and 'soft' stay for A/B
(`FarmMachinerySceneBuilder.Build(scene, suffix, "field")`). Built from 'soft' in 3 calibration rounds on the two Beauty shots.

- **Light:** Key_Sun low, direction (0.75, -0.434, 0.55) ≈ 25 deg elevation (long shadows), colour (1.0, 0.87, 0.72) ×2.4,
  soft shadows 0.82; Fill_Sky (0.62, 0.70, 0.90) ×0.35; ambient Trilight sky (0.52, 0.60, 0.78) (the only cold part) /
  equator (0.64, 0.56, 0.48) / ground (0.42, 0.35, 0.27). The sun comes from -x / -z: cameras stand on that side (yaw 25–50)
  so the noses and left sides they see are lit; heroes turn to rot 60–105 (nose to -x, towards the camera).
- **Haze:** fog ExponentialSquared 0.0008 (≈ 0.1 % at 40 m, 0.9 % at 120 m: no veil), warm cream (0.96, 0.90, 0.80).
- **Volume** `Assets/FarmMachinery/Demo/Settings/FarmMachinery_DemoVolume_V2.asset`: Tonemapping Neutral; post-exposure
  +0.2, contrast +16, saturation +6; White Balance 0 / 0; Split Toning shadows (0.52, 0.46, 0.41) warm brownish,
  highlights (0.53, 0.51, 0.48) (0.5 grey = neutral: a light warm push only — the soft look's (1.0, 0.86, 0.70) turned the
  whole frame mustard), balance 0; Lift neutral (1, 1, 1, 0), gain (1.01, 1.0, 0.98, 0); Bloom threshold 0.8, intensity 0.6,
  scatter 0.7, tint (1.0, 0.90, 0.75); Vignette 0.18 / 0.5.
  Color Curves Hue vs Hue (MEDIA v2 polish): keys (0, 0.497) (0.03, 0.494) (0.085, 0.5) (0.94, 0.5) looped — pulls only
  reds / red-oranges back by ~3 deg (`V.RedHueShift` 0.006; 0.012 overshot to 3.9 deg): lit body red 6–9 deg.
- **Sky** `M_FarmMachinery_Sky_V2` + `T_FarmMachinery_SkyPanorama_V2`: zenith (70, 130, 220) -> (96, 156, 234) -> (128, 180,
  240) -> (176, 206, 240) ~3 deg -> thin warm cream horizon (232, 228, 212) / (242, 232, 204) -> (226, 226, 222) -> clean
  blue below (172, 202, 240) -> (146, 188, 240) -> (136, 180, 236); clouds `M_FarmMachinery_Demo_Cloud_V2` lighter: top
  (1.0, 0.99, 0.96), sides (0.96, 0.96, 0.98), undersides (0.84, 0.88, 0.95), facet accent 0.06.
- **Demo palette (v2):** `M_FarmMachinery_Demo_V2` + `T_FarmMachinery_Demo_BaseColor_V2`: grass light #84924C / dark
  #74823F (lighter warm olive), road #B8A27E / rut #9C8668 (warm sand), straw #D0B272 / #BFA060, stubble ground #B69A68;
  soil cells as 'field'. Second atlas `M_FarmMachinery_Demo2_V2` + `T_FarmMachinery_Demo2_BaseColor_V2` (DEM-07..09):
  wheat / bale straw cells 0–7 lightened to #E6CE96 #D6B47A #B8965E #9A7C4E / #E0C690 #C8A66E #BC9C64 #A08458 (the builder's
  tones read as a dark brown mat under the v2 key).
- **Measured** (calibration round 3, Beauty shots; A/B sheet %TEMP%/farmmachinery_scene/AB_v2.png, field | v2): grass hue
  62–64 deg sat 0.51–0.55 (Synty 014: 62 / 0.34; field 97–100 / 0.73–0.76); lit body red 8.8–11 deg sat 0.64–0.77; luma
  p5 44–75, p50 109–133 (014: 60 / 126); sky 0–12 %; no channel ≥ 252. Scene renders: lit red 9.8–11.7 deg, p50 96–165.

### Recipe additions (DEM-07..09, MEDIA v2)

9. **Standing wheat DEM-07** (16×12 module, ~1.1 m faceted canopy; `DEM-07_Edge` 16×2 ragged strip): ahead of and beside the
   combine header so the machine "enters" the uncut crop (header ≤ 1.3 m into the wheat), stubble DEM-03 everywhere the
   machines have been; `env` sx / sz scale fits it into the island (Demo_Harvest 0.41 × 0.375). Wheat v2 (separate stalks):
   a second module offset by half a clump cell and 1 cm up densifies the stalks (Hero_Full, Demo_Harvest). It reads best low and close
   (Beauty, LowNode) as a cropped foreground; from high cameras (Hero 47 deg) it reads as a faceted straw mat.
10. **Demo bales DEM-08** (`DEM-08_Rect` 0.51×0.41×1.2, `DEM-08_Round` Ø1.4×1.2 lying): round bales scattered on the stubble
    behind the baler HRV-02, rectangular bales in rows on the TRL-06 deck at y 1.045 (deck raycast 1.035 + module y), two
    layers. Demo only — never in Lite shots or the catalogue.
11. **Seedling rows DEM-09** (16×12): next to the ploughed field (Demo_FieldWork), the seeder IMP-02 working on it.
12. **Icon / Social:** Icon 1024×1024 = one hero (TRC-01 Red / HRV-01 + ATT-03) at rot 105 from yaw 40–50, silhouette ≈ 80 %
    of the square, on its field module (opaque warm ground); check the 160 and 60 px downscales. Social 1200×630 = an
    extra `shot Social` in Hero_Lite / Hero_Full fitted to the focus groups only (6 % margin), the farm runs out to the edges.

## Thumbnails this is based on

- `origin/FarmMarket:AssetStore/Full/Draft/04_Hero_Showcase_1920x1080.png`, `…/10_Demo_Scene_2730x1536.jpg`
- `origin/Farm-Processing:AssetStore/FarmProcessing/Draft/Courtyard_Hero_r5.png`, `…/Draft/Catalog_STA.png`, `…/Draft/CMP_03_Grain.png`
- `origin/Farm-Nature:AssetStore/FarmNature/Draft/Beauty_03_2_Field.png`, `…/Beauty_01_Overall.png`
- Layout sources: `origin/Farm-Processing:Assets/Editor/FarmProcessing/FarmProcessingMedia.txt` (teal 23 60 69),
  `…/FarmProcessingCourtyard.txt` (Hero FOV 37), `origin/FarmMarket:Assets/Editor/MarketFarm/MarketSceneBuilder.cs` and
  `Full/FMS_FullSceneBuilder.cs` (sun, sky, ambient values).
- Local copies: `%TEMP%/farmmachinery_style/small/*.jpg`.

## Catalogue raw renders (Э10, 2026-11-24)

Clean item sheets for REQUIREMENTS 7.4–7.5 frames 06, 08, 09, 11, 12, 13 (no text; plates and captions in Э12):
`FarmMachinerySceneBuilder.Build("Catalog_<name>")` with layouts `planning/FarmMachinery/layouts/Catalog_*.txt` and the
directives of `FarmMachineryCatalogShots.cs`: `#! look catalog` (neutral white key from the front-left, shadow strength 0.55,
grey trilight, ground albedo (0.745, 0.756, 0.770) calibrated so the lit ground renders exactly #E9E9EC = the background,
every LODGroup forced to LOD0), `#! catrows rot gapX gapZ`, `#! catgroup`, `#! catrow TOKEN…` (rows back to front, packed by
the real LOD0 bounds; TOKEN = `ID[@wire|@lod1|@box|@gizmo|@rNNN][+parentPoint:ChildID:childPoint…]`), `#! fit shot group yaw
pitch margin [bottomFree]` (camera solved on the real renderer bounds). Defaults: rot 35 (3/4 front-left), yaw 0, pitch 30,
4 % margin; tractor + rear implement rows at rot 150 (rear 3/4) so the linkage reads. Outputs and composites (12 grid, 13
models) in `AssetStore/FarmMachinery/Media/raw/Catalog/`; numbers for 09 in `09_Technical_numbers.md` there.
