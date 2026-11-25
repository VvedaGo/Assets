# FarmMachinery — Э14 release check (2026-11-25)

Packages: `FarmMachinery_1.0.0.unitypackage` (3,407,161 B, 125 files) and `FarmMachinery_Lite_1.0.0.unitypackage`
(1,745,816 B, 75 files); file lists with GUIDs in `*_files.txt`. Built by `FarmMachineryRelease.Export()`
(Assets/Editor/FarmMachinery/FarmMachineryRelease.cs, menu Tools/Farm Machinery/Release).

## Shipping layout
- Ships: `Assets/FarmMachinery/{Art, Demo, Documentation}`. Demo = Demo_FieldWork, Demo_Harvest, Demo_Catalog (Full),
  Demo_FieldWork, Demo_Catalog_Lite (Lite); look v2 only (DemoVolume_V2, Sky_V2 + panorama V2, env materials *_V2 + 2 atlases V2,
  2 shaders); environment FBX/prefabs (Lite: only what its scenes use).
- Dev-only, moved with GUIDs to `Assets/_FarmMachineryDev/Demo/...`: 28 media/catalogue shot scenes, 32 backdrop/zone materials,
  A/B looks (field/soft volumes, skies, panoramas, base/soft env materials and atlases). Media rebuilds still work:
  `FarmMachinerySceneBuilder.Build` → `FarmMachineryRelease.AfterSceneBuild` moves non-shipped outputs to the dev folder;
  Icon_Lite and Catalog_09_Technical_Lite rebuilt after the move are byte-identical to `Media/raw`.
- Environment prefabs use the v2 materials directly; shipped scenes have one active camera (Cam_Overview / Main Camera).
- Not exported: Editor wrappers, PackTools, `_FarmMachineryDev`. Lite ⊂ Full with shared GUIDs (73 shared files, 0 mismatches);
  Lite-only: Demo_Catalog_Lite.unity, README_Lite.txt.

## Clean import (fresh Unity 6000.3.10f1 URP-template project, URP 17.3.0, batchmode -importPackage)
| Check | Full | Lite |
|---|---|---|
| Compile errors | 0 | 0 |
| Pack errors / warnings in import + check logs | 0 / 0 | 0 / 0 |
| Prefabs instantiated | 66/66 | 35/35 |
| Missing scripts | 0 | 0 |
| Pink / missing materials, shader errors | 0, 0 | 0, 0 |
| Demo scenes open + render (no magenta) | 3/3 | 2/2 |
| Models / single prefabs (base + variants) / CMP | 26 / 41 (26+15) / 5 | 13 / 21 (13+8) / 3 |
| BoxCollider / LODGroup | 41 / 22 | 21 / 11 |
| LOD0 tris total (min…max) / LOD1 total | 54,464 (76…3,708) / 25,580 | 28,872 (312…3,708) / 14,100 |
| Materials / textures (product) | 3 / 3 | 3 / 3 |
| Upgrade Lite → Full in place | 127 files, no duplicates, 0 errors | — |

Renders: `checks/Full/*.png`, `checks/Lite/*.png`; reports `checks/*/check.txt`; logs `checks/logs/`; check script `checks/FMCheck.cs`.

## Asset Store Tools Validator 12.0.6 (Assets/FarmMachinery, category 3D)
36 Pass, 1 Warning, 0 Fail (`checks/Validator_FarmMachinery.txt`). Warning: Check Model Orientation — FMS_Mach_HayRake.fbx
(rake arms rest at 90° about their hinge = transport pose, pivots on the hinge axes; by design).
