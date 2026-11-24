# Pack file templates

Used by `/pack-pipeline` (skill `.claude/skills/pack-pipeline/`). Layout of the pack files: `Tools/agents/roles/README.md`.

| Template | Copied to | When |
|---|---|---|
| `PIPELINE_STATE.md` | `planning/<Pack>/PIPELINE_STATE.md` | `start` |
| `01_THEME.md` | `planning/<Pack>/01_THEME.md` | `start` |
| `02_DEMAND.md` | `planning/<Pack>/02_DEMAND.md` | `start` (a new copy per checked subtheme; the old one is kept as `02_DEMAND_<subtheme>.md`) |
| `CATALOG.md`, `STYLE.md` | `planning/<Pack>/` | `start` |
| `ID.preview.md`, `ID.3d.md` | `planning/<Pack>/prompts/<ID>.preview.md`, `<ID>.3d.md` | Э5, per ID |
| `SHOT.md` | `planning/<Pack>/scenes/<Shot>.md` | Э9, per shot |
| `PACKAGE_METADATA.md` | `AssetStore/<Product>/PACKAGE_METADATA.md` | Э13, per product |

Owner-facing files (state, theme, demand, catalogue, style) are in Russian; prompts, specs and store texts in English.
