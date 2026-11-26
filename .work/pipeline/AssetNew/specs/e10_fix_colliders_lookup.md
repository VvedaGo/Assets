Owner decisions 2026-11-26 on your import report (same portion, follow-up):

1. Colliders: the pack ships WITHOUT colliders. Buyers add a MeshCollider themselves if they need one. Implement it as a post-pass in the pack wrapper (Assets/Editor/AssetNew/AssetNewPackBuilder.cs): after PackPrefabBuilder builds, remove every Collider component from all prefabs under Assets/AssetNew/Art/Prefabs (root and children), save the prefabs. The menu item "Build Prefabs" must run build + post-pass, so a rebuild stays consistent. Do NOT change PackPrefabBuilder for this.

2. Scene lookup: your option 1 is approved — optional ID -> name map in the shared PackConfig:
   - Assets/Editor/PackTools/PackConfig.cs: add `public Dictionary<string,string> PrefabNames` (ID or ID_Variant -> name without the prefix); PrefabPath uses the map when the key is present and keeps the old ID path otherwise (Farm Processing and other packs unaffected). Keep the change minimal, with an XML summary in the style of the file.
   - Assets/Editor/AssetNew/AssetNewPackBuilder.cs: fill the map for all 60 prefabs (42 IDs + 18 variants, e.g. "STR-01" -> "Arch_Wood", "STR-01_Gate" -> "Arch_Wood_Gate").
   - Tools/README.md: one line in the Unity section about the optional PrefabNames map.
   - Check PackSceneBuilder: confirm (read-only) that every place it resolves a prefab goes through PrefabPath; if a variant syntax in layouts (e.g. "STR-01_Gate") needs anything else, report it instead of changing PackSceneBuilder.
   This is the only shared-code change allowed.

Write only: Assets/Editor/PackTools/PackConfig.cs, Assets/Editor/AssetNew/*.cs (+ meta), the prefabs under Assets/AssetNew/Art/Prefabs (via the post-pass), Tools/README.md (one line), .work/ImportReport_AssetNew.txt, .work/pipeline/AssetNew/import_report.md (add a section "Follow-up 2026-11-26"). No git writes.
Verify: recompile completed with 0 errors; rerun "Build Prefabs" (build + post-pass); 60 prefabs, 0 Collider components in any prefab (count them); for all 60 map entries PrefabPath(key) resolves to an existing prefab (print missing = 0); LODGroups, materials and the X-flip results unchanged (spot check 3 prefabs); prefab GUIDs unchanged after the rebuild (compare the .meta GUIDs before/after for all 60 — they must stay the same so references survive).
Report (worker_done): what changed in each file; collider count before/after; map resolve result; GUID check; anything blocked.
