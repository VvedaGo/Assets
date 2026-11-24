# Prompt writer (Э5)

For each ID in your envelope write two independent documents. Read first: `CATALOG.md`, `STYLE.md`,
`Tools/agents/EXTERNAL_WORKER_BRIEF.md` (what the builder needs), templates `Tools/templates/pack/ID.preview.md` and
`ID.3d.md`.

## `prompts/<ID>.preview.md` → Codex Image (Э6)
- Starts with the STYLE BLOCK from STYLE.md, verbatim.
- One object, whole, three-quarter view (~25° elevation), neutral light-grey background, soft studio light.
- Silhouette, proportions, colours (HEX names from the palette), materials, the signature feature, functional parts.
- Negative block: no ground, no scene, no text, no logo, no extra objects, no people, no photo-realism, no noise.
- Exceptions (e.g. a structural base that belongs to the model) are written explicitly.

## `prompts/<ID>.3d.md` → Model builder (Э7)
- Catalogue line; size and tris budget; parts and pivots; moving parts; palette slots per part; LOD; Lite.
- Closest approved anchor model (from this or an earlier pack) if any.
- "What NOT to do" list specific to this object.
- Field `Reference: —` stays empty; the orchestrator fills it after Э6. Leave the section "Fixes" empty.

Consistency: items of one category share wording for shared parts (same leg, same crate slats) so the series matches.

## Report
List of IDs with both files written; IDs where catalogue data was missing or contradictory.
