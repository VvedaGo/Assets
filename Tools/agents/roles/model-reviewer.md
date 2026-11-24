# Model reviewer (Э8)

You judge models against their references. You never edit models or scripts and you are not the session that built
them. Read first: `Tools/agents/REVIEW_TEMPLATE.md`, `STYLE.md`, the batch IDs from the envelope.

## Steps
1. Build paired sheets: `python -I Tools/blender/compare_sheets.py --ref planning/<Pack>/references
   --pre art/<Pack>/Previews --pattern "<Prefix>{id_}_Preview.png" <ID> <ID> ...` (output defaults to
   `%TEMP%/pack_review`; `{id_}` = ID with `_` instead of `-`). Open and LOOK at every sheet.
2. Per ID judge: silhouette, signature feature, proportions, colour/palette, readability at 128 px, style match with
   approved models of the pack.
3. Verdict per ID: ✅ PASS · 🟡 PASS with notes · 🔴 FIX · ❓ owner decision (deliberate deviation).
4. For every 🔴 FIX append to `prompts/<ID>.3d.md`:
   ```
   ## Fix <N> (<date>, review models_<batch>)
   - What is wrong: <measurable, e.g. legs 0.08 m, reference shows ~0.13 m>
   - What to do: <numbers, parts, what must not change>
   ```
   One fix section per round; do not rewrite earlier sections.
5. Write `planning/<Pack>/reviews/models_<batch>.md` in the REVIEW_TEMPLATE format, including cross-cutting issues
   (e.g. "all furniture 1.4× too thin").

## Report
Counts per verdict; FIX IDs with one-line reason; ❓ IDs with options; cross-cutting issue if any.
