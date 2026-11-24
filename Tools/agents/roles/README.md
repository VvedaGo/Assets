# Role briefs of the pack pipeline

One brief per role of [AGENT_PIPELINE.md](../../../AGENT_PIPELINE.md). The orchestrator (`/pack-pipeline`, skill in
`.claude/skills/pack-pipeline/`) starts every task with "Read your brief: Tools/agents/roles/<role>.md" plus a task
envelope (pack, stage, items, inputs, write scope, limits, done criterion, report fields).

| Brief | Role | Stages |
|---|---|---|
| [researcher.md](researcher.md) | Themes, competitors, demand verdict | Э1–Э3 |
| [planner.md](planner.md) | Catalogue, style, pilots, duplicates | Э4 |
| [prompt-writer.md](prompt-writer.md) | Preview prompt + 3D spec per ID | Э5 |
| [codex-image.md](codex-image.md) | Item previews, scene references, store media layout | Э6, Э9, Э12 |
| [model-builder.md](model-builder.md) | Model in live Blender via MCP, export | Э7 |
| [model-reviewer.md](model-reviewer.md) | Model vs preview, fix notes | Э8 |
| [unity-assembler.md](unity-assembler.md) | Import, prefabs, scenes, renders | Э10 |
| [render-reviewer.md](render-reviewer.md) | Render vs scene reference, media acceptance | Э11, Э12 |
| [release-agent.md](release-agent.md) | Metadata card, export check, portal draft | Э13–Э15 |

## Rules for every role

- Write only inside the scope given in the envelope. Never edit shared tools (`Tools/`, `Assets/Editor/PackTools/`),
  other items, `AGENT_PIPELINE.md`, `PLAN.md`, `REQUIREMENTS.md`. Propose changes in the report instead.
- No git commits, stash, branch changes or pushes. No paid generation or downloads. Never read or print secrets.
- Conflicting or missing inputs: stop and ask (orchestration `ask` for Orca workers, or say so in the report) instead
  of guessing. Name the constraint you would drop.
- Report facts you checked. A failed check or a missing file means the task failed; say so.

## Pack file layout (in the pack branch)

```
planning/<Pack>/
  PIPELINE_STATE.md            orchestrator state, journal          (template: Tools/templates/pack/)
  01_THEME.md  02_DEMAND.md    Э1–Э3
  CATALOG.md   STYLE.md        Э4
  prompts/<ID>.preview.md      Э5 → Э6
  prompts/<ID>.3d.md           Э5 → Э7, fixes appended by Э8
  references/<ID>.png          Э6, selected preview = the model's reference
  reviews/models_<batch>.md    Э8 (format: Tools/agents/REVIEW_TEMPLATE.md)
  scenes/<Shot>.png, <Shot>.md Э9 scene references + description
  layouts/<Shot>.txt           Э10 PackSceneBuilder layouts (PackConfig.LayoutDir)
  reviews/renders_<n>.md       Э11
.work/models/<Pack>/<ID>_<Name>/  build.py, notes.md, check renders stay in %TEMP%
art/<Pack>/{Meshes,Textures,Previews,Blend}/   exported model files, ONE preview per model
Assets/<Pack>/                 Unity pack (Art/Models, Art/Prefabs, Demo, Documentation)
Assets/Editor/<Pack>/          pack wrapper: PackConfig + menu items
AssetStore/<Product>/PACKAGE_METADATA.md, Media/raw/, Media/layout/, Media/final/
```

IDs are `<CAT>-<NN>` (e.g. `STA-05`): `PackConfig.PrefabPath` takes the category from the part before the dash.
