Read your brief: Tools/agents/roles/codex-image.md (mode Э9 — scene references for staging in Unity, NOT store images). Repo root = this worktree (C:\Users\Sergv\orca\workspaces\Assets_Farm\AssetNew).
Pack: CottageGardenDecor (product Cottage Garden Decor, final pack of the farm series) · Stage: Э9 · Portion: Э9 scene references
Inputs:
- Accepted models: one preview per model in art/CottageGardenDecor/Previews/FMS_Garden_<ID_with_underscore>_Preview.png (42 files) — these are the ONLY objects allowed in the scenes, drawn as they look there. Variants exist as listed in planning/CottageGardenDecor/CATALOG.md (e.g. _Planted beds with flowers, _Pink/_White roses, STR-01 _Gate with a gate leaf, FUR-05 _Blue). Real sizes: CATALOG.md section «Фактические размеры после сборки».
- Compositions CMP-01..06 and demo scenes: CATALOG.md section «Композиции и демо» (exact item lists and counts).
- planning/CottageGardenDecor/STYLE.md; REQUIREMENTS.md 7.4–7.6 (shot purposes, free areas for plates).
- SERIES STYLE (owner instruction: the pack must look like one line with earlier packs): .work/pipeline/CottageGardenDecor/series_media/ — FN_Beauty_Garden.png and FN_03_Cover.png (Farm Nature: garden plot as a floating grass island with a brown soil edge, bright sky with soft low-poly clouds), FM_05_Hero.png / FM_03_Cover.png (Farm Machinery: 35–45° view, sky and clouds), FP_12_Compositions.png and FP_07_Closeups.png (Farm Processing: composition vignettes on a calm light background in a grid). sheet.png is a contact sheet of all. Match this environment, light, camera height and warm palette.
- Template: Tools/templates/pack/SHOT.md.
Demo-only environment allowed (not counted as pack models, CATALOG «Демо-сцены»): grass island/lawn, a simple path, sky and clouds. Nothing else that is not in the pack — no houses, fences, trees, people, animals, extra flowers or props from other packs.
Shots (one reference image + one .md each; names exactly as below):
1. Hero — Demo_CottageGarden overview: ~24×18 m garden island, the six compositions around a central path, free items between them; 35–45° down, one main focus (gazebo STR-06 with roses); for 05_Hero.
2. Cover — same garden, different angle/composition than Hero, main focus fully above the bottom 20–25 % reserved for the title plate; for 03_Cover and 04_Social (Social = clean, centre-weighted crop).
3. Card — CMP-01 RoseArchEntrance close (rose arch with gate, climbing roses, beds, gnome) on a small island; content in the top 60–65 %, bottom 35–40 % free for the plate; also the source for 01_Icon (arch + roses as a compact silhouette).
4. AltView — the demo from another side (e.g. from the pond/wall corner looking toward the gazebo); for 10_DemoAndVersion.
5. Modules — modular assembly proof: the pond kit assembled 3×2 (MOD-07/08/09), pergola STR-04 + STR-05 bay with wisteria, brick edging ring (MOD-05/06), stone wall with pillars (MOD-03/04), lattice screens with posts (MOD-01/02); for 08_VariantsAndModules (assembled part of the shot).
6–11. CMP-01 … CMP-06 — one vignette per composition, exact item list from the catalogue, each on its own small island/plinth, same camera for all six, calm light background like FP_12_Compositions; for 12_Compositions and 07_Closeups.
Catalogue grids (06_FullCollection, 09_Technical, 11_CategoryDetails, 13_Materials, 14_Unity) are NOT in this portion.
Write only: planning/CottageGardenDecor/scenes/<Shot>.png and planning/CottageGardenDecor/scenes/<Shot>.md (from SHOT.md: purpose, prompt, zones with items ID × count — counts must match the catalogue for CMP shots, camera/light/background, free area, «Not in pack — remove» list). Create the folder. Nothing else.
Limits: max 3 generations per shot (33 max total). No git, no downloads, no paid 3D tools, no secrets. Generator: built-in image tool of this Codex session (= Sol 6.2, owner decision).
Self-check per image: only pack items (+ allowed demo environment); recognisable as the previews; scale plausible from the real sizes; free plate area respected; series look. If the generator adds non-pack objects you cannot remove by regeneration, list them in «Not in pack — remove».
Done when: 11 shots each have a PNG + MD, or the attempt limit is reached (reason recorded).
Report (worker_done): per shot: generations used, kept file, rejected attempts and why, non-pack objects listed; anything not satisfied.
Placement: this machine (local), the user's worktree.
