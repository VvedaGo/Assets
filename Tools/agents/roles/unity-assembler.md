# Unity assembler (Э10)

You bring accepted models into the Unity pack and stage scenes from the scene references. Read first:
`Tools/README.md` (Unity section), summaries of `Assets/Editor/PackTools/PackPrefabBuilder.cs` and
`PackSceneBuilder.cs`, `Tools/unity/unity_eval.sh`, skill `unity:unity-cli`, `REQUIREMENTS.md` section 5 (TECH).

## Portion "import"
1. If missing, create the pack wrapper `Assets/Editor/<Pack>/` with one `PackConfig` (Root `Assets/<Pack>`, Tag, atlas
   regex, Prefix, LayoutDir `planning/<Pack>/layouts`) and menu items — pattern: `Assets/Editor/FarmProcessing/` of the
   `Farm-Processing` branch. Recompile and wait for `completed`.
2. Copy accepted FBX/textures from `art/<Pack>/` into `Assets/<Pack>/Art/Models/<CAT>/` and `Art/Textures/`; run
   `AssetDatabase.Refresh` in its own `unity_eval.sh` call.
3. Run `PackPrefabBuilder.Build(config)`; read `.work/ImportReport_<Tag>.txt`.
4. Check: every accepted ID has a prefab, scale 1/rotation 0 roots, pivots at base (TECH-01/02), no pink materials,
   collider and LODGroup where the catalogue says. Put the real tris/materials/textures numbers into the report — the
   release agent takes them from there.

## Portion "scene <Shot>"
1. From `scenes/<Shot>.png` + `<Shot>.md` write `planning/<Pack>/layouts/<Shot>.txt` (directives: ID x z rot y, row,
   floor, comp, shot, bg/ground — see the PackSceneBuilder summary). Ignore items marked "Not in pack — remove".
2. Build with `PackSceneBuilder.Build(config, layout, "<Shot>")`; renders land in `%TEMP%/<RenderTempDir>`.
3. LOOK at each render next to the reference; fix the layout (positions, camera, light) up to the round limit.
4. Copy accepted clean renders (no text) to `AssetStore/<Product>/Media/raw/<Shot>.png`.
5. On a render-review FIX: apply the notes appended to `layouts/<Shot>.txt` / `scenes/<Shot>.md`. A defect of the model
   itself goes back to the orchestrator (→ Э7), not fixed in Unity.

## Never
Edit shared PackTools code, lose `.meta`/GUIDs, put production tools or temp files into `Assets/<Pack>/`.

## Report
Prefab count vs accepted IDs; issues from ImportReport; real tris min/max/total LOD0, materials, textures; per shot:
layout path, render path, rounds, remaining differences.
