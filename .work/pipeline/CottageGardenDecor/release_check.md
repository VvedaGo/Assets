# CottageGardenDecor — Э14 release check (2026-11-26)

Release agent, this worktree (`C:/Users/Sergv/orca/workspaces/Assets_Farm/AssetNew`), its open Editor Unity 6000.3.10f1 (URP 17.3.0).
Product: Cottage Garden Decor 1.0.0 (one paid product, no Lite). No git writes, no portal actions, no changes to models,
prefabs or scenes.

## 1. Release check table

| What | Result | Evidence |
|---|---|---|
| README + Changelog | Created: `Assets/CottageGardenDecor/Documentation/README.txt` (requirements, quick start, folders, all 60 prefabs by category, compositions, setup contract with pivots/grids/attach points, atlases A/F, LOD1 on 9 prefabs, NO COLLIDERS, URP setup, 3 demo scenes, demo-only environment, series, support via publisher profile) and `Changelog.txt` (1.0.0, 2026-11-26). Style follows Farm Machinery README | the two files (+ .meta from Refresh) |
| Dependencies of the pack folder | `AssetDatabase.GetDependencies` over all 155 pack files: 169 deps, 14 outside the folder — all URP / Core RP package files (Lit.shader, Lit.mat, Volume.cs, VolumeProfile.cs, Bloom, ColorAdjustments, ColorCurves, SplitToning, Tonemapping, Vignette, WhiteBalance, UniversalAdditionalCameraData, UniversalAdditionalLightData, URP Editor AssetVersion.cs). **0 dependencies on `Assets/Editor/**` or other `Assets/` paths** | eval output in this report |
| Export | `AssetDatabase.ExportPackage("Assets/CottageGardenDecor", …, Recurse)` from this worktree's Editor | `.work/release/CottageGardenDecor_1.0.0.unitypackage` |
| Package size | **2,550,536 bytes = 2.6 MB (2.43 MiB)** | file size |
| File count | **155 files + 32 folders = 187 entries**, all under `Assets/CottageGardenDecor`: Art/Models 60 FBX, Art/Prefabs 66 (60 + 6 CMP), Art/Materials 2, Art/Textures 2, Demo/Materials 6, Demo/Meshes 3, Demo/Prefabs 7, Demo/Scenes 3, Demo/Settings 1, Demo/Shaders 2, Demo/Textures 1, Documentation 2. Nothing from `Assets/Editor`, `MediaOnly`, `.work`, `art/`, `planning/` | `.work/release/CottageGardenDecor_1.0.0_files.txt` (GUID + path) |
| Clean project | New project `CGD_CleanTest` (`unity projects create`, template `com.unity.template.urp-blank` 17.1.0 = Universal 3D, Unity 6000.3.10f1, URP asset PC_RPAsset) in `C:/Users/Sergv/AppData/Local/Temp/claude/7a0e116d5fa480c3/062772ef-7982-4023-bd79-41b214500eba/scratchpad/CGD_CleanTest` | — |
| Clean import (batch, `-importPackage`) | Exit 0, 155 files imported, 0 errors or warnings mentioning `CottageGardenDecor`. Log noise is from the fresh template only: VisualScripting `DirectoryNotFoundException` (YamlDotNet dll in a long PackageCache path) and URP `TryEnsure` "Host type is not matching any asset type" for URP's own shadergraph/urtshader files, plus licensing/curl offline messages — none from the pack | `.work/release/logs/clean_import.log` |
| Compile errors | 0 (`EditorUtility.scriptCompilationFailed = False`; the pack has no scripts; the only script in the clean project is the check script, added after the import) | `.work/release/clean_check/check.txt` |
| Missing scripts | 0 in 73 prefabs, 0 in 3 scenes | check.txt |
| Pink / missing materials | 0: 8 materials (2 art URP/Lit, 6 demo: 4 URP/Lit, 2 own shaders) all supported; 2 demo shaders supported, 0 compile errors; 0 null or unsupported material slots in prefabs and scenes; renders of all 3 scenes have 0 magenta pixels | check.txt |
| Prefabs load | **73 / 73** = 60 single + 6 CMP (66 product) + 7 demo; colliders 0 (as stated); LODGroups 22 = 9 single prefabs + 13 nested inside the CMP prefabs | check.txt |
| Demo scenes | Demo_Catalog: 714 objects, 191 prefab instances, 66 ID TextMeshes; Demo_Compositions: 530 / 182; Demo_CottageGarden: 491 / 155. Each: 0 missing references, 0 broken prefab instances, 0 missing scripts, 1 camera (Main Camera, active, post-processing on), 1 Volume with profile `FMS_Garden_Look` (Tonemapping, ColorAdjustments, WhiteBalance, SplitToning, Bloom, Vignette, ColorCurves), skybox on the pack's Gradient Sky shader | check.txt |
| Post Volume / render | Batch-mode camera render of each scene. **Looked at** `clean_DemoCottageGarden.png`: full garden island, graded colours, gradient sky + clouds, gazebo, fountain, pergola, pond, all compositions; no pink, nothing missing. Demo_Compositions render: 7 plinths in a row, no pink (overview camera far — items small, see notes) | `.work/release/clean_DemoCottageGarden.png`, `.work/release/clean_check/clean_Demo_*.png` |
| Console warnings summary | Pack: 0 warnings, 0 errors. Template/environment: VisualScripting path exception, URP "Host type is not matching" errors on URP package files, licensing token / curl (offline) — unrelated to the package | logs |
| Asset Store Validator | Asset Store Tools 12.0.6 (embedded package in this worktree), run from the CLI via reflection on the internal `CurrentProjectValidator` (same code as the window): category `3D`, path `Assets/CottageGardenDecor`, type UnityPackage. **37 tests: 37 Pass, 0 Warning, 0 Fail**, status RanToCompletion, no compilation errors | `.work/release/Validator_CottageGardenDecor.txt` |
| Card update | 7 `[ПРОВЕРИТЬ после экспорта]` items closed; Technical Details: Files / Sources (+ Documentation, 155 files / 32 folders), Demo / Scripts (6 demo materials instead of 8, one Main Camera per scene), Compatibility "tested with 6000.3.10f1" (table + Compatibility block), Package Size 2.6 MB | `AssetStore/CottageGardenDecor/PACKAGE_METADATA.md` |
| Numbers on images | Unchanged: 42 / 18 / 60 / 6, tris, LOD1 on 9, 2 atlases — nothing to change in Э12. Demo material count does not appear on any image | card Media section |

## 2. REQUIREMENTS section 8 — release readiness, one by one

| # | Criterion | State | Evidence / what is missing |
|---|---|---|---|
| 1 | Composition approved, factual register ready; variants and compositions counted separately | ✅ | CATALOG.md approved 2026-11-25; 42 models + 18 variants (11 colour / 7 mesh) + 6 CMP, verified on disk and in the export |
| 2 | Visual and technical checks done per pack spec | ✅ | reviews models_1…4, renders_1…3; import_report.md (60 prefabs, X-flip, LOD, no colliders); clean import above |
| 3 | Exported package checked in a clean project in all claimed configurations; no blocking errors, missing scripts, pink materials | ✅ | Claimed configuration: Unity 6000.3 + URP 17.3 only — tested 6000.3.10f1 / URP 17.3.0: 0 compile errors, 0 missing scripts, 0 pink, 73/73 prefabs, 3/3 scenes |
| 4 | README, Changelog, store description and technical data consistent with the export | ✅ | README/Changelog numbers = card numbers = export (60 FBX, 66 prefabs, 2 materials, 2 textures, 3 scenes, 6 demo materials, LOD1 on 9, 0 colliders) |
| 5 | Separate card per product version by 7.1–7.3; Title, Category, Tags, Summary, Description, Technical Details ready | ✅ | `AssetStore/CottageGardenDecor/PACKAGE_METADATA.md` (one product, no Lite); Category and portal field limits still to be matched with the live portal form at Э15 (Notes) |
| 6 | Media show the release content; required portal files prepared | ✅ | 17 finals in AssetStore/CottageGardenDecor/Media/final (Э12, 2026-11-26): icon 160+1024, card 420+1260, cover, social, gallery 05–14 + 06b; 14_UnityAndComparison built from an automatic capture of this project's Editor (orchestrator update) |
| 7 | Image register filled, acceptance by 7.4–7.8 passed | ✅ | Register = card Media section; acceptance planning/CottageGardenDecor/reviews/media_1.md pass 2: ✅ 15, 🟡 2, 🔴 0 (orchestrator update) |
| 8 | Dependencies, asset origin and disclosures checked | ✅ | Dependencies: URP 17.3 only (export deps check). Origin: AI / Third-party block of the card (Sol 6.2 references, scripted Blender models, Unity renders, Montserrat OFL for images only); no third-party files in the package |
| 9 | Version, date, package size, Validator result and remaining limitations recorded | ✅ | 1.0.0, 2026-11-26, 2,550,536 bytes, Validator 37/37 Pass; limitations in card Description and README (no colliders, no scripts/animations, opaque water, demo-only environment) |

**Release state:** the package itself is ready (criteria 1–5, 8, 9). Media (6, 7) done in Э12 — all section 8 criteria met; next Э15 portal draft (orchestrator update 2026-11-26)
and accepted. Submission/publication remain separate owner-confirmed states (Э15).

## 3. Defects and notes by role

- **Э7 (models):** none.
- **Э10 (prefabs/scenes):** no defects. Note (optional, not blocking): the single Main Camera of Demo_Compositions frames all 7 plinths from far
  away, so items are small in the Game view; a closer default view or a README hint would help users. Demo_CottageGarden and Demo_Catalog read well.
- **Э12 (image text):** no number on any image changed. Final images produced and accepted (media_1); 14_Unity captured automatically.
- **Validator caveat:** "Check Colliders" only inspects prefabs marked Static; ours are not static, so its Pass does not mean colliders exist —
  the card and README state "No colliders" explicitly.

## 4. Files written

- `Assets/CottageGardenDecor/Documentation/README.txt`, `Changelog.txt` (+ `.meta`, `Documentation.meta` from Refresh)
- `.work/release/CottageGardenDecor_1.0.0.unitypackage`, `CottageGardenDecor_1.0.0_files.txt`, `Validator_CottageGardenDecor.txt`,
  `clean_DemoCottageGarden.png`, `clean_check/` (check.txt + 3 renders), `logs/clean_import.log`, `logs/clean_check.log`
- Clean project (outside the repo): `C:/Users/Sergv/AppData/Local/Temp/claude/7a0e116d5fa480c3/062772ef-7982-4023-bd79-41b214500eba/scratchpad/CGD_CleanTest`
  (check script `Assets/Editor/CGDCleanCheck.cs` lives only there)
- `AssetStore/CottageGardenDecor/PACKAGE_METADATA.md` (Э14 items), this report
