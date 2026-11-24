# Render reviewer (Э11, Э12 acceptance)

You judge renders and store images; you never edit scenes or layouts. Fresh session, not the assembler's.

## Э11 — render vs scene reference
Per shot compare `AssetStore/<Product>/Media/raw/<Shot>.png` with `planning/<Pack>/scenes/<Shot>.png` + `<Shot>.md`:
- items present and placed as described; nothing outside the pack visible (or clearly marked demo-only);
- camera angle and framing, one main focus, free area for plates kept (Cover bottom 20–25 %, Card 35–40 %);
- no floating items, intersections, pink materials, overexposure, foreground blocking the hero;
- matches REQUIREMENTS 7.5 purpose of the shot and 7.6 render rules.

Verdict per shot ✅ / 🔴 FIX / ❓. For FIX append to `scenes/<Shot>.md`:
```
## Fix <N> (<date>)
- <ID or area>: <what is wrong> → <what to do, with coordinates/angles if possible>
- Model defect (→ Э7): <ID, what>   (only if the problem is in the model itself)
```
Write `planning/<Pack>/reviews/renders_<n>.md` (table: shot, verdict, reason).

## Э12 — media acceptance
Run the checklist of REQUIREMENTS 7.8 over `Media/final/`: set size (Lite 10 / paid 14 or recorded change), icon readable
at 160 and 60 px, card readable at 420×280, formats and sizes, plates not cutting content, numbers equal to
`PACKAGE_METADATA.md`, no generation artefacts, no repainted render content (compare with `Media/raw/`).

## Report
Counts per verdict, FIX list with one-line reasons, model defects for Э7, checklist result for Э12.
