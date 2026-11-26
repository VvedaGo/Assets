import os
SP='.work/pipeline/CottageGardenDecor/specs'
tasks=[
 ('MOD-05+MOD-06',[('MOD-05','Edging_Brick','straight brick edging 1 m'),('MOD-06','Edging_Brick_Curve','90 deg brick edging curve')],'A','Build both in ONE registry script (Tools/blender/build_registry_template.py form, `-- <ID> build|export`); prove the SNAP contract between MOD-05 and MOD-06 (print SNAP OK).'),
 ('MOD-01+MOD-02',[('MOD-01','Lattice_Panel','white lattice screen 2 m'),('MOD-02','Lattice_Post','lattice post')],'A','ONE registry script for both; prove SNAP between panel and posts (print SNAP OK). Lattice white per the spec Palette note (#EEEDE7), same white wording as STR-01/STR-06. PLT-02 climbing rose must mount on the panel (check art/CottageGardenDecor/Meshes/FMS_Garden_Rose_Climbing_Side.fbx dims / its notes).'),
 ('MOD-03+MOD-04',[('MOD-03','Wall_Stone','low stone wall 2 m'),('MOD-04','Wall_Pillar','wall pillar with ball')],'A','ONE registry script for both; prove SNAP between wall and pillar (print SNAP OK). Two-tone stone split (slots 11/12) clearly visible, as the pilot review asked. Same stone wording/cells as FLB-01 kerb and WTR-03 (see their notes).'),
]
for name,items,atlas,extra in tasks:
    ids=[i for i,_,_ in items]
    folder='.work/models/CottageGardenDecor/'+'+'.join(ids)+'_'+items[0][1].split('_')[0]
    itemlines='\n'.join(f'- {i} `FMS_Garden_{n}` - {d}' for i,n,d in items)
    inputs='; '.join(f'planning/CottageGardenDecor/prompts/{i}.3d.md, planning/CottageGardenDecor/references/{i}.png' for i in ids)
    fbx='; '.join(f'art/CottageGardenDecor/Meshes/FMS_Garden_{n}.fbx (+ .fbm), art/CottageGardenDecor/Blend/FMS_Garden_{n}.blend, exactly ONE preview art/CottageGardenDecor/Previews/FMS_Garden_{i.replace("-","_")}_Preview.png' for i,n,_ in items)
    spec=f'''Read your brief: Tools/agents/roles/model-builder.md (repo root = this worktree, C:/Users/Sergv/orca/workspaces/Assets_Farm/AssetNew). Also load the skill `blender-unity-assets`.
Pack: CottageGardenDecor (product Cottage Garden Decor) · Stage: Э7 · Portion: Series batch 1 (one builder at a time on the live Blender; others wait for you)
Items:
{itemlines}
Inputs: {inputs}; planning/CottageGardenDecor/STYLE.md; planning/CottageGardenDecor/CATALOG.md (rows + «Модули и стыковка»); Tools/README.md; Tools/blender/pack_common.py, pack_shapes.py, build_registry_template.py, make_lod1.py; Tools/agents/EXTERNAL_WORKER_BRIEF.md (Style, Defects, Report). The reference image wins over catalogue numbers (PIPE-04) except functional sizes in the spec (snap grid, heights, mounting dimensions).
Approved anchors of this pack: WTR-03 birdbath, STR-06 gazebo, STR-01 arch (atlas A, white members, posts >= 0.10), FLB-01 bed (stone kerb), PLT-01/02/03 roses (atlas F) - previews in art/CottageGardenDecor/Previews/, scripts and notes in .work/models/CottageGardenDecor/*/. Review lessons: planning/CottageGardenDecor/reviews/models_pilot.md, models_1.md.
Atlas: {atlas}. Reuse art/CottageGardenDecor/Textures/FMS_Garden_AtlasA.png read-only (do NOT rewrite it; if a colour is missing, ask via orchestration ask first).
{extra}
Blender: owner's Blender 5.2 with the MCP add-on (outdated add-on, but execute_blender_code and look work). Start with get_addon_status + get_scene_info. If execute or look fail: stop and report failed. Work only in your new collection(s) named <ID>_<Name>; never touch other collections, the owner's Cube or the saved file. The 2 m default Cube at the origin hides models in look - render in a temporary scene (copy the render helper from .work/models/CottageGardenDecor/WTR-03_Birdbath/build.py) and view with look image=. Save the selection before a live pc.export and restore it after.
Headless check: "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python <script> -- <args> (PYTHONUTF8=1). make_lod1.py needs an absolute --art path and sys.dont_write_bytecode (do not leave Tools/blender/__pycache__).
Write only: {folder}/ (ONE registry build.py in the `-- <ID> build|export` form, notes.md); {fbx}. Check renders only in %TEMP%/assetnew_check/<ID>/. Nothing else.
Limits: max 5 self-check rounds per model in live Blender. No paid generate_3d, no search_assets/import_asset, no downloads, no git, no secrets. LOD as in the catalogue row.
Done when: each model exported, re-import verify OK, headless export reproduces it, checks printed (non-manifold/loose/degenerate 0, coplanar 0, ground contact, tris <= budget, SNAP OK).
Report (worker_done): per ID: paths; tris per part and total vs budget; size m; pivot; checks; SNAP; re-import; headless reproduction; rounds used; remaining differences vs reference; verdict SHIP / SHIP WITH NOTES / NO-SHIP.
Placement: this machine (local), the user's worktree.
'''
    open(f'{SP}/spec_b1_{name}.md','w',encoding='utf-8').write(spec)
print(sorted(os.listdir(SP)))
