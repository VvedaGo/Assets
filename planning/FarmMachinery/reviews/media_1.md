# FarmMachinery — Э12 media acceptance (media_1)

Reviewer: render-reviewer (fresh session), 2026-11-25. Reviewed: all 10 Lite + 14 Full finals (plus 1024 masters, 1260x840 cards, 60 px checks), cards `Lite/PACKAGE_METADATA.md` and `Full/PACKAGE_METADATA.md` (Media + Technical Details), `Media/layout/` CHECKS.md, FONTS.md, GENERATIONS.md, `build_media.py`. No image or other file was edited.
Method: every final image was viewed; sizes/mode read with Pillow; render pixels independently re-diffed against `Media/raw` (see Pixel checks).

## Verdict summary
- Lite: 10 files, 10 ✅, 0 FIX.
- Full: 14 files, 11 ✅, 3 🔴 FIX (02_Card and 03_Cover: `3D` corner not in the card; 11_CategoryDetails: crop artefacts).
- Totals: 24 images, 21 ✅, 3 🔴 FIX, 0 ❓. Plus a doc-only fix of the card texts (Fix 1).

## Lite (AssetStore/FarmMachinery/Lite/Media/final)
| Image | Size ok | Verdict | Reason |
|---|---|---|---|
| 01_Icon (160 / 1024 / 60_check) | 160, 1024, 60 | ✅ | AI icon, owner-allowed. Faithful to TRC-01 (cab, cream rims, front weight, red mudguards, beacon, exhaust; compared with raw Icon_Lite). Flat teal bg, `3D` corner + `LITE` tag. Silhouette and `3D` readable at 160 and 60; `LITE` at 60 is small but legible as a tag. No logo. |
| 02_Card (420x280 + 1260x840) | yes | ✅ | Readable at 1:1 420x280: badge `LITE`, title, accent. Plate about 36.6 % of height, tractor+plough fully above it. Accent `13 MODELS + 3 COMPOSITIONS` = card. |
| 03_Cover | 1950x1300 | ✅ | Plate 22 %, no model under it; only Lite machines (red/blue tractor, tipper, sprayer, seeder). Accent `13 MODELS · SEPARATE WHEELS · HITCH POINTS` = card. |
| 04_Social | 1200x630 | ✅ | Clean render, no text, bit-identical to Social_Lite raw; only Lite content. |
| 05_Hero | 1920x1080 | ✅ | Plate `FARM MACHINERY LITE / FIELD WORK` (312 px wide) clear of the tractor wheel; render equals raw outside plate. |
| 06_FullCollection | 1920x1080 | ✅ | 21 items counted = 21 prefabs. Legend and plate = card. |
| 07_Closeups | 1920x1080 | ✅ | 5 panels, captions = card; top panels letterboxed with light bars but clean. |
| 08_VariantsAndModules | 1920x1080 | ✅ | 4 panels, captions and footnote = card. Polish note, not a blocker: modularity items are small inside large grey cells. |
| 09_Technical | 1920x1080 | ✅ | Wireframe LOD0/LOD1 + collider; 3,348/1,674, 1,260/630, 28,872, 11 models = card Tech + `09_Technical_numbers.md`. |
| 10_DemoAndVersion | 1920x1080 | ✅ | Lite demo overview; Full content only as text under `FULL ONLY — NOT INCLUDED IN LITE`; demo-only footnote present. IMG-04 respected. |

## Full (AssetStore/FarmMachinery/Full/Media/final)
| Image | Size ok | Verdict | Reason |
|---|---|---|---|
| 01_Icon (160 / 1024 / 60_check) | yes | ✅ | AI icon, owner-allowed. Faithful to HRV-01 + grain header ATT-03 (wide reel, yellow dividers, cab, unload tube, exhaust). `3D` corner readable at 160 and 60; combine+header recognisable at 60. |
| 02_Card | yes | 🔴 FIX | Image has a red `3D` corner triangle (code-drawn). Card Media row 02_Card lists only Title + Accent, and the plate-system line says no top badge. Doc/image mismatch (Fix 2). Otherwise OK: readable at 420, plate clear, `26 MODELS + 5 COMPOSITIONS` = card. |
| 03_Cover | yes | 🔴 FIX | Same `3D` triangle not in card Media row 03_Cover (Fix 2). Plate 22 %, no model under it, accent = card. |
| 04_Social | yes | ✅ | Clean render, no text, identical to raw. |
| 05_Hero | yes | ✅ | `FARM MACHINERY / HARVEST` plate over grass only; render = raw. Demo bales and silos footnoted on 07 and 10. |
| 06_FullCollection | yes | ✅ | 41 items counted (8+8+8+8+9); legend/plate = card. |
| 07_Closeups | yes | ✅ | 5 captions + footnote = card. |
| 08_VariantsAndModules | yes | ✅ | 4 panels, captions, footnote = card. |
| 09_Technical | yes | ✅ | 3 rows (2,820/1,410; 3,348/1,674; 1,260/630), 54,464, 22 models = card. |
| 10_DemoAndVersion | yes | ✅ | Block text = card; footnote present. |
| 11_CategoryDetails | yes | 🔴 FIX | Labels = card, but tile crops contain edge fragments of neighbouring models: combine tile top (grey bin/auger slivers), forage tile top (slivers), round-baler tile bottom (part of another baler). Reads as stray elements (Fix 3). |
| 12_Compositions | yes | ✅ | 5 vignettes + footnote = card; CMP_05 readable. |
| 13_Materials | yes | ✅ | 3 atlases RED/GREEN/BLUE, 3 colour tractors, info line = card (256×256, URP/LIT). |
| 14_UnityAndComparison | yes | ✅ | Real Unity screenshot (FMS_Mach_Combine, 2820/1410, Box Collider), 4 callouts + Lite-vs-Full table = card. Unity UI text is small but callouts carry the message. No user/path data visible (only Assets > FarmMachinery > Art > Prefabs > HRV). |

## Checklist (REQUIREMENTS 7.8 + task extras)
| Item | Result |
|---|---|
| Set size Lite 10 / Full 14 | PASS (10 / 14 numbered files, plus masters and 60 px checks) |
| Exact sizes 7.4 | PASS, all RGB PNG, verified with Pillow |
| Icon readable at 160 and 60 | PASS (opened `_60_check`; tractor / combine and `3D` readable; Lite tag small) |
| Card readable at 420x280 | PASS (both; title, accent, badge legible) |
| Plates never cover hero/models/labels | PASS |
| Cropping of names/badges; text vs models | PASS |
| Gallery covers catalogue, details, variants, technical | PASS |
| Lite shows only Lite content or labelled Full-only (IMG-04) | PASS |
| Same line Lite/Full (fonts, plates, treatment) | PASS |
| No watermark/UI junk/generation artefacts/pink | PASS except Fix 3. No misspellings found in any image text |
| No repainted render content | PASS (see Pixel checks) |
| Font licence recorded (OFL) | PASS: Montserrat, `fonts/OFL.txt`, FONTS.md with source and SHA-256; SHA-256 of `Montserrat.ttf` re-computed, matches |
| No personal data (names, local paths) in images / PNG metadata | PASS (no text chunks; visible text reviewed) |
| No logo | PASS |
| Price Lite Free / Full 19.99 | PASS in cards (prices not on images) |
| Social crop-safe | PASS |
| Card Media registry current (IMG-06) | FAIL, doc only (Fix 1) |

## Pixel checks (independent of CHECKS.md)
Decoded diffs against `Media/raw` outside the declared plates/corner: Lite+Full 04_Social 0; Lite+Full 05_Hero 0; Lite+Full 03_Cover 0; Lite+Full 02_Card_1260x840 0; Lite 10 demo tile (Lanczos 1188x668) 0; Full 12 CMP_01 tile 0; Lite 02_Card 420 differs only in the badge box (11,11,56,30); icon masters equal `layout/icons/Icon_*.png` resized, 0. CHECKS.md table (all 0) is consistent. `build_media.py` reads all strings from the card Media section and aborts on any render-pixel change. Raw icons vs generated icons checked visually (shape, parts, colours match).

## Numbers / strings diff (image vs card Media + Technical Details)
Every plate, caption, legend and callout was compared literally with the "Captions inside images" and plate columns: all equal, including middle dot, multiplication sign, arrow, em dash, case and wrapped lines.
| Number | Image | Card | Equal |
|---|---|---|---|
| Lite 13 models / 21 prefabs / 3 comp / 2 demo scenes | 02, 03, 06, 10 | Desc, Tech | yes |
| Lite 28,872 tris, LOD1 on 11 | 09 | Tech | yes |
| Lite TRC-01 3,348/1,674; IMP-01 1,260/630 | 09 | Tech + 09_Technical_numbers | yes |
| Lite groups 2/6/3/2; variants 4/3/1 | 06 | Tech | yes |
| Full 26 / 41 / 5 / 3 scenes | 02, 03, 06, 10, 12, 14 | Desc, Tech | yes |
| Full 54,464 tris, LOD1 on 22 | 09 | Tech | yes |
| Full HRV-01 2,820/1,410 | 09, 14 | numbers.md, Tech | yes |
| Full groups 2/7/6/5/3/2/1; variants 8/5/2 | 06 | Tech | yes |
| CMP prefab counts 2/3/11/6/11 | 12 | Media captions | yes (only in Media captions, not derivable from Tech) |
| 256x256, 3 atlases, URP/Lit | 13 | Tech | yes |
| Comparison 13/26, 21/41, 3/5, 2/3 | 14 | Media | yes |

Only non-equality: the `3D` triangle on Full Card/Cover (not in the card text).

## Fix 1
Card text (release-agent scope, both PACKAGE_METADATA.md), not images:
- Media tables still say "Final files: Э12" and Status "final — Э12" / "block — Э12" / "panel — Э12". IMG-06 wants file, size, format, text, source, version and status: set Status to accepted and add Format PNG RGB.
- "Fonts on store images ... open, being finalised by Codex" and the Notes lines about Arial Bold draft / empty logo square are stale: record Montserrat (SIL OFL 1.1, `Media/layout/fonts/OFL.txt`, FONTS.md). Keep the note that 01_Icon lettering is AI-drawn (family unknown).

## Fix 2
Full 02_Card (420 and 1260 versions) and 03_Cover: `3D` corner triangle vs card. Choose one:
- (preferred, no re-render) In `Full/PACKAGE_METADATA.md` Media add "Corner badge: `3D`" to rows 02_Card and 03_Cover, and change the plate-system line "Card/Cover — no top badge" to "corner `3D` triangle (REQUIREMENTS 7.6, optional paid badge)". Re-run `build_media.py` to confirm it still reads the card.
- or remove the triangle (`full_corner=None` for Full title pages in `build_media.py`), rebuild, update CHECKS.md rows.

## Fix 3
Full 11_CategoryDetails: tighten crop boxes in `build_media.py::categories()` (source `Catalog/11_Category_Harvest`). Combine tile `(523,383,981,730)` and forage tile `(1070,376,1456,708)`: start a few px lower so the sheet-top slivers of the bin/auger disappear; round-baler tile `(1177,797,1486,1004)`: end above the neighbouring baler fragment at the bottom. Check at 1:1 that no foreign object edges remain; render pixels must stay equal to the raw crop; update the CHECKS.md row for 11.

## Open / ❓
None blocking. Owner-taste observations only: modularity panels (Lite 08, Full 08) use small items in large grey cells; top panels of 07/12 are letterboxed.
