# FarmMachinery — release check (Э14, re-run after the Lite / Full split, 2026-11-26)

Packages: `FarmMachinery_1.0.0.unitypackage` (3,429,097 B; 127 files + 51 folders) and `FarmMachinery_Lite_1.0.0.unitypackage`
(1,748,725 B; 75 files + 28 folders); entries with GUIDs in `*_files.txt`. Built by `FarmMachineryRelease.Export()`
(Assets/Editor/FarmMachinery/FarmMachineryRelease.cs, menu Tools/Farm Machinery/Release).

## Layout (owner request: separate Lite and Full folders, no duplicated assets)
```
Assets/FarmMachinery/
  Lite/  Art/{Models,Prefabs}/{ATT,IMP,TRC,TRL,CMP}, Art/Materials, Art/Textures,
         Demo/{Scenes,Environment,Materials,Settings,Shaders,Textures}, Documentation   — 75 files (everything Lite needs)
  Full/  Art/{Models,Prefabs}/{ATT,EQP,HRV,IMP,PRP,TRL,CMP}, Demo/{Scenes,Environment}, Documentation — 52 files (Full-only)
Assets/_FarmMachineryDev/Demo/...   dev-only (media / catalogue shot scenes, A/B looks, generated backdrop materials)
```
- Lite: 13 Lite models (FBX + prefabs + 8 variants), CMP_01–03, Red/Green/Blue materials + atlases, demo look (Volume, sky,
  shaders, v2 env materials + atlases, catalogue backdrop), the 6 env FBX / 11 env prefabs the Lite scenes use, Demo_FieldWork,
  Demo_Catalog_Lite, README_Lite.txt, Changelog.txt.
- Full: 13 Full-only models (HRV-01..03, ATT-03..05, TRL-04..06, EQP-01/02, IMP-07, PRP-01) + 7 variants, CMP_04–05, Full-only
  env (5 FBX: bales, stubble, road corner, wheat field / edge; 9 prefabs incl. the combined Clouds / GrassTufts), Demo_Harvest,
  Demo_Catalog, README.txt. Demo_FieldWork is shared (Lite's).
- Packages: Lite = `Assets/FarmMachinery` + `Lite`; Full = `Assets/FarmMachinery` + `Lite` + `Full` (Full ⊃ Lite, same GUIDs).
- Shared PackTools untouched: the wrapper runs every build "staged" (`FarmMachineryRelease.Staged`): Full files are moved
  (GUIDs kept) into the Lite working root (`PackConfig.Root = Assets/FarmMachinery/Lite`), the build runs, then everything outside
  the Lite dependency set goes back to Full and empty working folders are removed. Scene builds stage dev scenes / their generated
  materials in and out the same way (GUIDs now kept on media rebuilds).

## Checks
| Check | Result |
|---|---|
| Compile (master-2) | OK |
| File GUIDs before → after split | 200 → 200, 0 lost, 0 new (127 moved); folders: 34 kept, 6 temp category folders replaced by new Lite/Full folders |
| Lite → Full references | 0 (GetDependencies of each of the 75 Lite files) ; Full deps outside the pack 0; packages used: URP core + universal |
| Build All after split | same 200 GUIDs, no path changes; model and variant prefabs byte-identical; CMP_02–05 re-serialised with new internal fileIDs (composition builder) — demo scenes unaffected (render of Demo_FieldWork md5-identical to Э14, catalogues identical) |
| Media rebuild | Catalog_09_Technical_Lite byte-identical to Media/raw; Icon_Full: 2 of 1,048,576 pixels differ by ≤ 6/255 |

## Clean import (fresh Unity 6000.3.10f1 URP-template projects, URP 17.3.0, batchmode -importPackage)
| Check | Full | Lite | Lite → Full upgrade |
|---|---|---|---|
| Compile errors / pack errors+warnings in logs | 0 / 0 | 0 / 0 | 0 / 0 |
| Files under Assets/FarmMachinery (Lite + Full), folders | 127 (75 + 52), 50 | 75 (75 + 0), 27 | 127 (75 + 52), 50 — no duplicates |
| Prefabs instantiated / missing scripts / pink | 66/66 / 0 / 0 | 35/35 / 0 / 0 | 66/66 / 0 / 0 |
| Demo scenes open + render (no magenta) | 4/4 (incl. Demo_Catalog_Lite from Lite) | 2/2 | 4/4 |
| Models / single prefabs / CMP | 26 / 41 / 5 | 13 / 21 / 3 | 26 / 41 / 5 |
| LOD0 tris (min…max) / LOD1 | 54,464 (76…3,708) / 25,580 | 28,872 (312…3,708) / 14,100 | = Full |
| BoxCollider / LODGroup | 41 / 22 | 21 / 11 | 41 / 22 |
Renders: `checks/{Full,Lite,Upgrade}/*.png` (Demo_FieldWork identical in all three); reports `checks/*/check.txt`; logs `checks/logs/`.

## Asset Store Tools Validator 12.0.6 (category 3D) — `checks/Validator_FarmMachinery.txt`
- `Assets/FarmMachinery`: 36 Pass, 1 Warning, 0 Fail. Warning: Check Model Orientation — `Full/Art/Models/IMP/FMS_Mach_HayRake.fbx`
  (rake arms rest at 90° about their hinge = transport pose; by design).
- `Assets/FarmMachinery/Lite`: 37 Pass, 0 Warning, 0 Fail.

## For Э12 / owner
- `Media/raw/Catalog/14_Unity_Full.png` and `14_Unity_Lite.png` re-captured with the new folders (Prefab Mode, Inspector with LOD Group
  + Box Collider, Project at `Assets > FarmMachinery > Full|Lite > Art > Prefabs > HRV|TRC`); no account toolbar, paths or user
  names; editor restored. The final `14_UnityAndComparison` (Full) must be rebuilt from the new raw.
- Orchestrator decision 2026-11-26: the Full package has 4 demo scenes (Demo_FieldWork + Demo_Catalog_Lite from Lite, Demo_Harvest,
  Demo_Catalog); Lite has 2. Full card, README.txt and Changelog updated; packages re-exported with the new docs (sizes above).
  Э12: Full 10_DemoAndVersion line `4 DEMO SCENES: FIELD WORK · HARVEST · 2 CATALOGUES`, 14_UnityAndComparison `DEMO SCENES 2 | 4`.
