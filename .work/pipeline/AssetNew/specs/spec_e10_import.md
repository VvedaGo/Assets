Read your brief: Tools/agents/roles/unity-assembler.md (repo root = this worktree, C:/Users/Sergv/orca/workspaces/Assets_Farm/AssetNew). Also load the skill `unity:unity-cli`.
Pack: AssetNew (product Cottage Garden Decor) · Stage: Э10 · Portion: "import" (import + materials + prefabs for ALL 42 accepted models; no scenes yet)
Items: all 42 IDs of planning/AssetNew/CATALOG.md (STR-01..07, MOD-01..09, FLB-01..03, WTR-01..03, ORN-01..05, FUR-01..05, PLT-01..06, TOP-01..04) plus their variants (_White, _Gate, _Pink, _Planted, _Blue, _Feeder, _Rose) — every FBX in art/AssetNew/Meshes/.
Inputs:
- art/AssetNew/Meshes/*.fbx (+ .fbm), art/AssetNew/Textures/FMS_Garden_AtlasA.png and FMS_Garden_AtlasF.png (two atlases: A = structures, F = plants; ORN-03 and parts of ORN-05/FLB _Planted use F).
- planning/AssetNew/CATALOG.md (IDs, names, LOD yes/no, colliders notes; section «Фактические размеры после сборки»), planning/AssetNew/STYLE.md.
- planning/AssetNew/reviews/models_4.md — section "Consolidated Unity-import check list": this is the main checklist of this portion. Also the per-model notes in .work/models/AssetNew/*/notes.md where needed.
- Shared tools (read, do NOT edit): Assets/Editor/PackTools/PackConfig.cs, PackPrefabBuilder.cs, PackSceneBuilder.cs; Tools/unity/unity_eval.sh; Tools/README.md (Unity section).
- Wrapper pattern of an earlier pack: Assets/Editor/FarmProcessing/ in the git branch origin/Farm-Processing — read it with `git show origin/Farm-Processing:<path>` / `git ls-tree` (read-only git commands only).
Unity: the Editor of THIS worktree is open (project 6000.3.10f1, URP); `bash Tools/unity/unity_eval.sh '"ok"'` returns completed/ok. Another Unity (D:/GitProjects/Carswarnew) is also open — never touch it; always pass --project-path . (the script does).
Write only:
- Assets/Editor/AssetNew/ (pack wrapper: one PackConfig — Root "Assets/AssetNew", Tag "AssetNew", TextureRegex matching both atlases, Prefix per the series convention you find in PackPrefabBuilder/PackConfig, LayoutDir "planning/AssetNew/layouts" — plus menu items), with .meta files Unity generates.
- Assets/AssetNew/Art/Models/<CAT>/, Art/Textures/, Art/Materials/, Art/Prefabs/<CAT>/ (copies of the FBX/atlases + generated assets).
- .work/ImportReport_AssetNew.txt and .work/pipeline/AssetNew/import_report.md (your report, see below).
Nothing else: do not edit Tools/, Assets/Editor/PackTools/, planning/ files, art/ files, Packages/, ProjectSettings/ (if a project setting blocks you, ask). No git writes.
Steps: wrapper → recompile (wait for completed) → copy files → AssetDatabase.Refresh in its own call → PackPrefabBuilder build → read the ImportReport → verify.
Naming: follow what PackPrefabBuilder/PackConfig do (prefab name from Prefix + ID, model name from the FBX). If the tool cannot map our FBX names (FMS_Garden_<Name>.fbx, variants FMS_Garden_<Name>_<Variant>.fbx) to IDs without changing shared code, STOP and ask via orchestration ask with the exact options — do not hack around it.
Verify (record numbers per ID in the report):
1. Every catalogue ID and every variant FBX has a prefab; count prefabs vs FBX.
2. Root scale 1, rotation 0, pivot at base (TECH-01/02); no pink/missing materials; atlases A/F assigned correctly (URP Lit or the tool's material).
3. X-flip assumption of the series (Blender x -> Unity -x): check one asset of each kind from the checklist — MOD-06 arc quadrant (+X/+Z, ends (1,0,0) and (0,0,1)), MOD-08 corner quadrant, FLB-02 missing quadrant, STR-05 bay at +X, STR-01 _Gate hinge side, ORN-05 hook direction, MOD-07/MOD-09 basin direction and water slab height. Report the actual result for each: matches the assumption or not. If NOT, do not fix models — report exactly which items and the rotation/mirror needed (the orchestrator sends it back to Э7).
4. LODGroups where the catalogue says LOD (STR-03, STR-04, STR-05, STR-06, WTR-01, FUR-01, FLB _Planted): LOD0/LOD1 children paired correctly; FUR-01 Seat pivot (0, 2.04, 0) and Seat_Low1 under it.
5. Colliders per the checklist (openings: STR-06 1.27 × 2.1, STR-01 1.2 × 2.1, STR-02 1.20, STR-03 1.56; PLT-03 and plants without blocking colliders). Use what PackPrefabBuilder generates; list where it differs from the checklist (do not hand-edit prefabs unless the tool supports it through its config).
6. Real numbers for the store card: tris min/max/total LOD0 over all prefabs, material count, texture count and sizes.
7. One check render per variant family is NOT needed now (later portion).
Limits: no scenes, no layouts, no store media now. No paid tools, no downloads, no secrets. If Unity errors persist after 3 attempts on the same step, stop and report.
Done when: wrapper compiles, all FBX imported, prefabs built, ImportReport read, checks 1–6 reported.
Report (worker_done, and the same in .work/pipeline/AssetNew/import_report.md): prefab count vs FBX count; ImportReport issues; X-flip results per checked item; LOD and collider findings; real tris/materials/textures; anything blocked; files written.
Placement: this machine (local), the user's worktree.
