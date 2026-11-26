# AssetNew (Cottage Garden Decor) — Э10 portion "import" report (2026-11-26)

Unity 6000.3.10f1 URP, the Editor of this worktree. Shared PackTools left unchanged. Wrapper `Assets/Editor/AssetNew/AssetNewPackBuilder.cs`
(Root `Assets/AssetNew`, Tag `AssetNew`, TextureRegex `FMS_Garden_Atlas[AF]`, Prefix `FMS_Garden_`, LayoutDir `planning/AssetNew/layouts`,
menu Tools/Cottage Garden Decor/Build Prefabs). Naming: catalogue names, as the coordinator decided (answer A): prefab = FBX name,
`Art/Prefabs/<CAT>/FMS_Garden_<Name>[_<Variant>].prefab`.

## 1. Counts
- FBX in art/AssetNew/Meshes: 60 (42 base + 18 variants). Copied to Art/Models/<CAT>/: 60. Prefabs built: **60 = 60**.
  The `.fbm` folders were not copied (they hold only duplicate atlas PNGs). No `.fbm` was created in Assets.
- Per category (FBX = prefabs): STR 10, MOD 9, FLB 6, WTR 3, ORN 8, FUR 8, PLT 11, TOP 5.
- All 42 catalogue IDs have a prefab: STR-01..07, MOD-01..09, FLB-01..03, WTR-01..03, ORN-01..05, FUR-01..05, PLT-01..06, TOP-01..04.
  Variants: STR-01 _White/_Gate, STR-07 _White, FLB-01/02/03 _Planted, ORN-02 _Blue, ORN-03 _Planted, ORN-05 _Feeder, FUR-03/04 _White,
  FUR-05 _Blue, PLT-01 _Pink/_White, PLT-02 _Pink, PLT-03 _Pink, PLT-06 _White, TOP-01 _Rose.

## 2. ImportReport (.work/ImportReport_AssetNew.txt): 60 prefabs, 3 flagged, all three on purpose
- MOD-01 Lattice_Panel `min Y 0.050`: on purpose, the posts carry the panel (builder notes: z 0.05..1.80).
- MOD-09 Pond_Water `min Y 0.340`: on purpose, the slab sits 0.34–0.38 above a pivot on the ground (checklist: no prefab offset).
- PLT-05 Wisteria_Drape `min Y -0.856`: on purpose, the pivot is on the top face (hangs under the beam).
- Every root: position 0, rotation 0, scale 1. Every child too (scale 1, rotation 0). All other items have min Y 0.000 = pivot at base (TECH-01/02).
- Materials: 2 (`FMS_Garden_AtlasA.mat`, `FMS_Garden_AtlasF.mat`; URP/Lit, smoothness 0.15, GPU instancing on). No null or pink slots (153 renderers checked).
  87 renderers use A and 66 use F.
- Atlas per FBX (read from the FBX by the tool): A for STR, MOD, WTR, FUR, ORN-01/02/04. F for FLB (unplanted beds too), ORN-03 (+_Planted), ORN-05 (+_Feeder), PLT, TOP.
  This matches the checklist ("ORN-03/05 and their variants use atlas F").

## 3. X-flip check (Blender x -> Unity -x): the assumption holds for every checked item, so nothing goes back to Э7
| Item | Expected | Measured in the prefab | Result |
|---|---|---|---|
| MOD-06 arc | +X/+Z, ends (1,0,0) and (0,0,1) | bbox X 0..1.05, Z 0..1.05; the end at Z≈0 has X 0.95..1.05; the end at X≈0 has Z 0.95..1.05 | matches |
| MOD-08 corner | X ≤ 0, Z ≤ 0 | X -0.37..0, Z -0.37..0, Y 0..0.45 | matches |
| MOD-07 basin | basin to +Z, pivot on the inner face | edge X ±0.5, Z -0.37..0 (stone behind, basin toward +Z) | matches |
| MOD-09 slab | slab Y 0.34–0.38, pivot on the ground | Y 0.340..0.380, root at 0 | matches |
| FLB-02 missing quadrant | X>0, Z>0 empty | vertices with X>0.13 and Z>0.13: base 0, _Planted 0 (other quadrants 97–1550) | matches |
| STR-05 bay | posts X +3.0, beams +0.25..+3.25 | posts X 2.91..3.09, beams X 0.25..3.25 | matches (place at STR-04 + 1.5, then +3.0) |
| STR-01 _Gate hinge | viewer's left post (viewer at +Z) | `Gate_Leaf` pivot at X +0.59, leaf X -0.54..+0.006 local | matches (+X is the left of a viewer looking at the front) |
| ORN-05 hook | points to -X; `Hanging` a root child at the hang point | `Hanging` direct root child at (-0.296, 1.454, 0), same in _Feeder; basket X -0.43..-0.14 | matches (rotate 180° about Y if +X is wanted) |
| WTR-02 (extra) | basin to +Z, back at Z 0 | Z 0..0.59 | matches |

## 4. LODGroups (LOD0 down to 0.25, LOD1 down to 0.015 screen height, from PackConfig)
LODGroup on 9 prefabs, exactly the catalogue list: STR-03, STR-04, STR-05, STR-06, WTR-01, FUR-01, FLB-01/02/03 _Planted. No LODGroup anywhere else.
- STR-03: 3 parts + 3 `_Low1` (1276 / 638 tris). STR-04: 3+3 (332 / 178). STR-05: 3+3 (248 / 164). STR-06: 5+5 (2314 / 1156).
- WTR-01: 11 meshes + 11 `_Low1`, all paired (1258 / 788). FLB-01_Planted 6+6 (1456 / 830), FLB-02_Planted 7+7 (2024 / 1138), FLB-03_Planted 7+7 (1766 / 1008).
- Every `_Low1` is parented under its LOD0 part, and LOD0/LOD1 hold the same parts in the same order.
- FUR-01: `Seat` local position (0, 2.040, 0), rotation 0. `Seat_Low1` is a child of `Seat` (follows the swing). 4+4 (580 / 356).
- ORN-03 _Planted: two mesh nodes, `_Body` 436 and `_Plants` 860, as the checklist expects.

## 5. Colliders: the tool gives every prefab one BoxCollider over its LOD0 bounds; PackConfig has no option to change this
Prefabs were not edited by hand. Where the result differs from the checklist:
- **Openings blocked** (one solid box fills each opening):
  - STR-01 + variants: box 1.60×2.40×0.70; the 1.2×2.1 opening should be clear.
  - STR-02: 1.48×2.50×0.46; the clear 1.20 opening should be clear.
  - STR-03: 1.80×2.30×0.80; the clear 1.56 opening should be clear (the bench is inside the box).
  - STR-06: 3.58×4.00×3.58, centre X -0.212; the clear 1.27×2.1 opening should be clear, and the inside is not walkable.
  - STR-04/05 pergolas: full 3.5×2.62×3.5 / 3.0×2.62×3.5 boxes; the inside is not walkable.
- **Plants with blocking boxes**:
  - PLT-03 (+_Pink): box 1.57×0.54×0.56; the checklist wants no collider.
  - PLT-01/02/04/05/06 and variants: full boxes; the checklist wants none or a thin capsule. PLT-05's box is the hanging volume Y -0.86..0.
  - TOP-01..04: boxes, not a stem capsule plus a volume.
- **Shape differs**:
  - WTR-01: one 2.4×2.42×2.4 box; should be a basin cylinder plus a pedestal cylinder.
  - ORN-05 (+_Feeder): box 0.56×1.70×0.28 that includes the basket; should be a capsule on the pole.
  - FUR-01: one 2.48×2.16×1.50 box that includes the seat; should be two frame boxes, no seat collider.
  - FUR-02: one box over the cloth; should be foot/post boxes.
  - FLB-02 (+_Planted): the 2×2 box also covers the empty quadrant X>0, Z>0.
- **Match the checklist (boxes are fine)**:
  - ORN-01 0.45×0.96×0.45 (checklist ≈0.40×0.40×0.95).
  - ORN-03 0.60×1.20×0.60; _Planted 0.60×1.38×0.60, which includes the blooms.
  - FUR-03 0.70×0.75×0.70.
  - FUR-04 0.41×0.85×0.45 (the checklist's 0.45 is the seat height; the box includes the back).
  - FUR-05 0.68×0.90×1.06.
  - Plain boxes for MOD-01..09, STR-07, WTR-02, WTR-03, ORN-02, ORN-04, FLB-01, FLB-03.
- Correct colliders need either a per-ID collider spec in the shared PackPrefabBuilder/PackConfig or a post-pass in the wrapper. That is an owner/orchestrator decision; nothing was done here.

## 6. Real numbers for the store card
- Prefabs: 60 (42 items + 18 variants). Materials: 2 (URP/Lit).
- Textures: 2 PNG atlases, 256×256 each (FMS_Garden_AtlasA, FMS_Garden_AtlasF), point filter, no mips, uncompressed.
- LOD0 tris over all 60 prefabs: **min 36** (MOD-02 Lattice_Post; MOD-09 Pond_Water also 36), **max 2722** (STR-02 Arch_Iron), **total 47,604**, average 793.
  The 42 base prefabs alone: 26,918. LOD1 on 9 prefabs: 6,256 tris in total.
- Per prefab, LOD0 tris (+LOD1):
  - STR: STR-01 812, _White 812, _Gate 1264; STR-02 2722; STR-03 1276 (+638); STR-04 332 (+178); STR-05 248 (+164); STR-06 2314 (+1156); STR-07 236, _White 236.
  - MOD: MOD-01 296; MOD-02 36; MOD-03 464; MOD-04 256; MOD-05 100; MOD-06 148; MOD-07 76; MOD-08 80; MOD-09 36.
  - FLB: FLB-01 204, _Planted 1456 (+830); FLB-02 252, _Planted 2024 (+1138); FLB-03 250, _Planted 1766 (+1008).
  - WTR: WTR-01 1258 (+788); WTR-02 428; WTR-03 336.
  - ORN: ORN-01 348; ORN-02 586, _Blue 586; ORN-03 436, _Planted 1296; ORN-04 888; ORN-05 600, _Feeder 578.
  - FUR: FUR-01 580 (+356); FUR-02 784; FUR-03 1000, _White 1000; FUR-04 1096, _White 1096; FUR-05 384, _Blue 384.
  - PLT: PLT-01 1996, _Pink 1996, _White 1996; PLT-02 1600, _Pink 1600; PLT-03 1064, _Pink 1064; PLT-04 498; PLT-05 888; PLT-06 684, _White 684.
  - TOP: TOP-01 168, _Rose 848; TOP-02 158; TOP-03 672; TOP-04 328.
- Measured sizes are in the ImportReport and match CATALOG «Фактические размеры после сборки» (e.g. STR-06 3.58×4.00×3.58, WTR-01 2.40×2.42×2.40, FUR-01 2.48×2.16×1.50).
- Over budget: STR-02 2722 against the catalogue's 1400. That is within the "up to ~2×" allowance for wrought iron, but the spec must record it.

## Proposal for the scene portion: ID -> prefab name lookup (for the owner)
PackSceneBuilder.Place uses `PackConfig.PrefabPath(id)` = `Prefabs/<CAT>/FMS_Garden_<CAT>_<NN>.prefab`. That file does not exist when prefabs carry catalogue names.
- **Option 1 (recommended): an optional map in PackConfig.**
  - Add `public Dictionary<string,string> PrefabNames` (ID or ID_Variant -> name without the prefix, e.g. "STR-01" -> "Arch_Wood", "STR-01_Gate" -> "Arch_Wood_Gate").
    `PrefabPath` uses the map when the ID is in it and keeps the old ID path otherwise, so Farm Processing is unaffected.
  - Files: `Assets/Editor/PackTools/PackConfig.cs` (the field plus about 3 lines in PrefabPath), `Assets/Editor/AssetNew/AssetNewPackBuilder.cs` (60 map entries), and one line in `Tools/README.md`.
  - Layouts keep using catalogue IDs. The change is small, and later packs can reuse it.
- Option 2: a scene step inside the wrapper, as Farm-Animals did (`Assets/Editor/FarmAnimals/FarmAnimalsDemoBuilder.cs`).
  - Files: a new `Assets/Editor/AssetNew/AssetNewSceneBuilder.cs` that copies PackSceneBuilder's parsing, placement and rendering and adds its own lookup.
  - Shared code stays untouched, but about 230 lines get duplicated, and later fixes to PackSceneBuilder would not reach it.
- Option 3: write prefab names instead of IDs in the layouts. This still needs a PrefabPath change, because PrefabPath builds the category from the ID, so it is no better than option 1.

## Blocked / not done
- Nothing is blocked. No scenes, layouts, renders or store media; they are not part of this portion. Colliders were left as the tool builds them (see section 5).
- Not verified:
  - Visual check renders (deferred to a later portion).
  - Decor orientation items not on the Э10 list: ORN-01 gnomon, ORN-02 nose, ORN-04 front, PLT-04/06 facing, TOP-03 handedness. They need renders.

## Files written
- `Assets/Editor/AssetNew/AssetNewPackBuilder.cs` (+ .meta): PackConfig and the menu item Build Prefabs.
- `Assets/Editor/AssetNew/AssetNewImportChecks.cs` (+ .meta): read-only prefab dump used for checks 2–5 (menu Dump Prefab Checks; writes Unity `Temp/AssetNew_PrefabChecks.txt`).
- `Assets/AssetNew/Art/Models/<CAT>/*.fbx` (60), `Art/Textures/FMS_Garden_AtlasA.png` and `FMS_Garden_AtlasF.png`, `Art/Materials/FMS_Garden_AtlasA.mat` and `FMS_Garden_AtlasF.mat`,
  `Art/Prefabs/<CAT>/*.prefab` (60), and the `.meta` files Unity generated.
- `.work/ImportReport_AssetNew.txt` (written by the tool) and `.work/pipeline/AssetNew/import_report.md` (this file).
- No git writes. Shared tools, planning/, art/ and ProjectSettings/ are unchanged (the 3 ProjectSettings diffs were there before this task).
