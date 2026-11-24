# Codex Image (Э6, Э9, Э12)

You are a Codex worker. Image generator: **Sol 6.2**. If it is not available in your session, stop at once and report
that; do not substitute another generator. Read first: `STYLE.md`, `REQUIREMENTS.md` 7.4–7.6, and the mode below.

## Mode Э6 — item preview (reference for the 3D model)
- Input: `prompts/<ID>.preview.md`. Output: `planning/<Pack>/references/<ID>.png` (the selected image only).
- Append to the prompt file a "Generations" table: attempt, prompt changes, seed/settings, result (kept / rejected why).
- Limit: the envelope gives the attempts left for this ID (default 4 total). Stop at the limit.
- Reject your own result if: more than one object, cut off, ground/scene/text present, construction impossible to build
  (floating parts, legs that do not reach the floor), off-palette, style differs from approved previews of the pack.

## Mode Э9 — scene references (for staging in Unity, NOT for the store)
- Input: list of accepted models with their previews, STYLE.md, shot list (REQUIREMENTS 7.5: Hero, FullCollection,
  Closeups, Variants, Compositions…), free area for title bars (Cover bottom 20–25 %, Card bottom 35–40 %).
- Output per shot: `planning/<Pack>/scenes/<Shot>.png` + `<Shot>.md` (prompt, zones, which IDs stand where, camera
  angle and height, light, free area).
- Only items of the pack. If the generator adds buildings, plants or props that are not in the catalogue, regenerate or
  list them in `<Shot>.md` under "Not in pack — remove".

## Mode Э12 — store icon and media layout
- Input: accepted clean renders `AssetStore/<Product>/Media/raw/`, plate texts from `PACKAGE_METADATA.md` Media section,
  rules REQUIREMENTS 7.6 (dark plate `#20242A`, accent `#C8473B`, max two font families, logo position).
- Build the layouts with CODE over the real renders (Python + Pillow, or HTML/CSS rendered to PNG): crop, background,
  plates, text, badge. Do NOT regenerate or repaint the render with the image generator — the store must show the real
  content (MKT-01). The store icon is a crop/recomposition of a real render with a solid background.
- Outputs: editable sources in `Media/layout/` (script or HTML + font reference), finals in `Media/final/` with the file
  names and sizes of REQUIREMENTS 7.4 (01_Icon 160×160 + 1024 master, 02_Card 420×280 + 1260×840, 03_Cover 1950×1300,
  04_Social 1200×630, 05–14 1920×1080).
- Fonts: only fonts with a known licence (e.g. SIL OFL); write the font name and licence into `Media/layout/FONTS.md`.
- Numbers on plates come only from `PACKAGE_METADATA.md`; never invent counts.

## Report
Files written; generations used per ID/shot; rejected attempts and why; anything you could not satisfy.
