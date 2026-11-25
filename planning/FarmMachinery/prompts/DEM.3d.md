# DEM-01…05 Demo environment — 3D spec (owner decision 2026-11-24)

Reference: no generated preview. Style targets: the FarmMarket demo render (git show origin/FarmMarket:AssetStore/Full/Draft/10_Demo_Scene_2730x1536.jpg — round grass island with soil sides, dirt and cobble paths, saturated warm look) and planning/FarmMachinery/SCENE_STYLE.md (FarmMachinery tones: soil 182 137 115, route 210 191 167, stubble 177 184 157 as rendered targets). Stylized low-poly, faceted flat shading, chunky shapes, same language as the machines. No textures besides the flat palette atlas.

## Common
- Separate demo atlas `T_FarmMachinery_Demo_BaseColor` (256 px, 4×4 cells, flat colours): grass light/dark, soil dark/light, furrow shadow, dirt road light/dark, straw/stubble light/dark, flower white/yellow/blue, rock grey; material `M_FarmMachinery_Demo`. The machines' shared atlas MUST stay unchanged (md5 eb6768e2).
- Root origin on the ground (Y 0 = top walking surface for DEM-01…04), centre of bbox in X/Z, scale 1, rotation 0, +Z forward.
- No LOD (flat, low tris). One FBX per ID (DEM-05: one FBX with 3 separate root objects or 3 FBX — builder's choice, documented).
- Modules (DEM-02, DEM-03, DEM-04) snap edge to edge on their stated grid; top surface at Y 0 (furrow ridges/stubble above it), so machines stand on Y 0 everywhere.

## Items
| ID | Build | Notes |
|---|---|---|
| DEM-01 Diorama base | irregular rounded outline ~64×44 m (12–20 outline points, soft bevel), top grass at Y 0 (two greens as large faceted patches, not noise), side skirt 0.8 m of soil with 2 strata | Like the FarmMarket island; leaves room for 2–3 field modules and a road |
| DEM-02 Ploughed field 16×12 | ridges along Z every ~0.5 m, triangle profile 0.15–0.25 m, dark/light soil alternating | Must read as "freshly ploughed" from 35–45° down |
| DEM-03 Stubble field 16×12 | light soil base + short straw stubble rows (low wedges or thin boxes) every ~0.4 m | Under the combine / windrows |
| DEM-04 Dirt road | straight 8×4 m and 90° corner 8×8 m, two tyre ruts slightly darker, grass verge strips 0.3 m | snaps on an 8 m grid |
| DEM-06 Clouds (4 variants) | low-poly faceted white cumulus: 3–6 merged lumpy spheres/icospheres per cloud, flat-ish bottom, sizes ~6–16 m wide; colours: white + very light blue-grey shade cells in the demo atlas | Style target: Farm Nature clouds — `git show origin/Farm-Nature:AssetStore/FarmNature/Draft/Beauty_01_Overall.png` |
| DEM-07 Standing wheat | module 16×12 (field) + edge strip 16×2: dense faceted wheat clumps 0.8–1.0 m tall (stalk + ear blocks), warm straw/ochre two tones, top at ~1.0 m, base at Y 0; rows along Z; edge strip has an irregular cut edge | Synty 014.webp: combine drives into standing wheat, stalks as big foreground |
| DEM-08 Straw bales (demo only) | rectangular 1.2×0.5×0.4 and round Ø1.4×1.2, faceted, straw two tones, round bale with spiral ring hint | Not catalogue products, not Farm Market; on stubble behind HRV-02 and on TRL-06 |
| DEM-09 Seedling rows | module 16×12: soil base + rows of small 2–4-leaf seedlings every ~0.6 m, light fresh green | FieldWork: seeder/cultivator next to it |
| DEM-05 Grass tufts / flowers | 3 small clusters (grass tuft, tuft with 3 flowers, small rock+grass) | scatter on DEM-01 |

## What NOT to do
- No trees, fences, buildings, bales, animals (other packs / not in scope).
- No high-frequency noise, no smooth shading, no alpha textures.

## Fixes
