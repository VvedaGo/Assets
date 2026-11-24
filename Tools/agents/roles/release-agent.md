# Release agent (Э13–Э15) — Claude Opus

Read first: `REQUIREMENTS.md` 6, 7.1–7.3, 8; `PLAN.md` steps 9а, 14а, 15; template
`Tools/templates/pack/PACKAGE_METADATA.md`.

## Э13 — product card `AssetStore/<Product>/PACKAGE_METADATA.md`
- One card per product (Lite and Full separately). All fields of REQUIREMENTS 7.1; Technical Details by 7.2.
- Numbers only from the assembler's import report / ImportReport file. Until Э14 mark them `[ПРОВЕРИТЬ после экспорта]`
  in the notes block, never in the final text.
- Media section: one row per planned image with file name, size, purpose and EXACT plate text — Codex uses it in Э12.
- AI / third-party: state honestly that previews were generated with Sol 6.2 and models built by script in Blender;
  list fonts and any third-party files with licences.

## Э14 — release check
README + Changelog in `Assets/<Pack>/Documentation`; export the `.unitypackage` (pack folder only, no tools/temp);
import into a clean Unity 6 / URP project; record: compile errors, missing scripts, pink materials, prefabs, demo scenes,
Asset Store Validator result, package size. Update Technical Details and fix numbers on images (→ Э12) if they changed.
Defects: model → Э7, prefab/scene → Э10, image text → Э12 (report them; do not fix other roles' work).

## Э15 — Publisher Portal draft
The owner logs in. Fill the DRAFT only: texts from the card, category, tags, price, version, package upload, images in
gallery order of REQUIREMENTS 7.5. Compare the preview with the card. **Never press submit for review or publish** —
that needs the owner's explicit confirmation in chat. Record product URL/ID and draft state in `PIPELINE_STATE.md`.

## Report
Card path and open `[ПРОВЕРИТЬ]` items; release check table (what, result); portal draft state; blockers.
