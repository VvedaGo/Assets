# Catalogue planner (Э4)

You turn the approved subtheme into a countable catalogue and a concrete style. Read first: `01_THEME.md`,
`02_DEMAND.md`, `REQUIREMENTS.md` sections 3–5 and 10 (PIPE-03…05), `PLAN.md` step 2–3, catalogues of earlier packs
the envelope points to (for duplicates and style continuity).

## Output 1 — `planning/<Pack>/CATALOG.md` (template in `Tools/templates/pack/CATALOG.md`)
- One row per standalone object, permanent ID `<CAT>-<NN>`; variants (colour, size, open/closed, empty/full) as their own
  rows or an explicit variant column with a number. No row "set of tools" with an unknown count.
- Size in metres (W×D×H), tris budget (soft ceiling), moving parts with pivot, LOD yes/no, Lite yes/no.
- Mark 2–3 pilot items of different types: simple, characteristic, complex. If the pack has modules (walls, floors,
  posts) write the snap contract: exact grid size, post halves, heights.
- Totals: models, variants, prefabs, planned compositions, demo scenes.

## Output 2 — `planning/<Pack>/STYLE.md`
Shapes and detail level, proportions, shading, palette with HEX (series palette REQUIREMENTS ART-02 as a base),
materials, texturing (flat atlas per Tools/README), target Unity/URP, and the STYLE BLOCK: 3–5 English sentences that
every image prompt starts with.

## Output 3 — duplicate check (in CATALOG.md, section "Duplicates")
Compare with earlier packs; for each match either replace the item or state the visible silhouette difference.

## Report
Paths, totals, pilot IDs, duplicates found, questions the owner must answer before approval.
