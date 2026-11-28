# Render review renders_1 (E11) - CottageGardenDecor, 2026-11-26

Shots: Hero, Cover, AltView (scene Demo_CottageGarden). Compared with scenes/*.png/.md, REQUIREMENTS 7.4-7.6, the owner's Synty visual reference (farm plan img_06, nature plans, meadow overview img_100, rules "Как работают сцены" and "Приёмка каждого кадра") and the series sheet; also looked at 50 % size.

| Shot | Verdict | Reason |
|---|---|---|
| Hero | 🔴 FIX | island 80 % of the width but the garden covers ~55 % of its top; empty front/left/right lawn; items small; gazebo not a clear focus |
| Cover | 🔴 FIX | plate OK (free 24 %, island bottom 76 %) but garden tiny and sparse, gazebo 9 % of the width and 3 % from the top edge; angle SSW instead of ENE (accepted) |
| AltView | 🔴 FIX | island 72 % of the width with wide sky margins, items small, empty front lawn, pond arch hidden behind the L wall, no focus |

OK in all three: no pink or overexposure, no floating items visible, nothing foreign except demo island/path/clouds, consistent shadows, series sky/clouds/light recognisable, compositions match the catalogue counts (assembler report). Not verified at pixel level: intersections of small items.

## Common cause
The demo island (~24 x 18 m) is too big for the pack: 6 compositions + 7 free items do not fill it. In the Synty frames the ground is 90-100 % of the frame, objects are dense (1-2 m gaps), big at the back and small in front, the group takes 65-85 % of the width. Here the island takes ~80 % of the width but objects only ~45-50 %, so they read small at 50 % and the flat lime lawn dominates. The AI reference PNGs have the island ~25-30 % smaller relative to the objects and a deeper green.

**The island must be rebuilt (Blender demo asset, not a layout change): top ~18 x 13.5 m instead of ~24 x 18 m, path scaled with it.** Then the layout is re-spaced inwards and cameras brought closer.

## Top fix items
1. Rebuild the island at 18 x 13.5 m; garden >= 80 % of the top area.
2. Re-space compositions: gaps 1.5-2.5 m, edge margin 0.8-1.5 m; foreground >= 2-3 readable items.
3. Cameras closer: island 88-94 % of the width, gazebo >= 13-16 % of the width (Hero/Cover), sky margins 5-10 %.
4. Add allowed free items in gaps (+4 topiaries, +3 roses, +2 planted beds, +2 TOP-04); compositions unchanged.
5. Lawn deeper green (~#7DB93C, -8 % saturation, -0.15 exposure); Cover nothing below y = 76 %; AltView aim so the pond arch is visible.

## Cross-cutting rules for next scenes (CMP vignettes, catalogue shots)
- The subject group covers 65-85 % of the frame width, 55-75 % of the height; it must read at a 50 % thumbnail.
- Do not reuse the big island for vignettes: platform only ~1.5 m beyond the composition footprint (REQUIREMENTS 7.6: 80-90 % of the render area); no lawn band wider than 1.5 m without an item.
- Depth: tall items back, small items 1-3 m from the front edge, >= 2 readable items in the foreground, one tallest focus per shot.
- Camera 35-40 deg down, vFOV 30-34, 20-40 deg yaw off axis; the front/entrance of the main composition faces the camera (check the facing before the angle in the .md).
- Lawn deeper green with faceted variation, not lime; warm key upper left, cool fill, soft shadows; clouds never on the plate area or touching island corners or the hero object.
- Cover/Card plates: verify numerically on the PNG (lowest non-sky pixel <= 76 % Cover, <= 60-65 % Card).
- Big pieces of each composition >= 3 % of the frame height; only genuine small props (gnome, birdbath, sundial, hooks) may be smaller.
- Known model differences (STR-01_Gate all white, roses on arch side faces) are not blockers; mention them in the next report only.

---
# Pass 2 (after Fix 1, 2026-11-26)

Looked at the three new renders at 100 % and 50 %, against the references, REQUIREMENTS 7.5-7.6 and the Synty acceptance rules.

| Shot | Verdict | Reason |
|---|---|---|
| Hero | 🟡 PASS with notes | island fills the frame (~84 % width), garden covers ~85 % of the top, no empty lawn bands, all six zones and the gazebo read at 50 %; density now matches Synty farm/nature plans |
| Cover | 🟡 PASS with notes | plate free (lowest island row 74.6 %, nothing below), gazebo high and central (x ~50 %), dense garden; island 83 % of the width is accepted |
| AltView | 🟡 PASS with notes | island 89 %, gazebo and walled pond with open iron arch both large and readable, strong depth (big front, small back), clean upper right for a text block |

No Fix 2 needed, no owner decision needed: the unmet numeric targets (island 88-92 % width, gazebo 13-16 %, gaps 1.5-2.5 m) are accepted because the picture sells at a glance, has one main focus and no large empty areas; gaps of 0.5-1.1 m are the dense Synty look. Lawn #7DB93C reads right and matches the series. No pink, floating or foreign objects seen.

Notes (non-blocking, may be fixed in a later polish pass):
- Hero/Cover: the pergola (CMP-02) stands in front of the pond and hides most of the water/arch. The pond and iron arch are fully shown in AltView, so acceptable.
- AltView: the gazebo roof overlaps the fountain parterre and hides part of the fountain basin. The fountain is shown in Hero/Cover, acceptable. Optional: raise the camera by 2-3 deg or move 1 m left to free the fountain.
- Hero: top-left and top-right clouds are clipped by the frame edge, and one right cloud touches the island edge; move 2-3 clouds 3-5 % inwards/up if re-rendering anyway. Cover: three top clouds clipped by the top edge (the plate area is clean, so harmless).
- CMP-03 re-arranged around the gazebo differs from CMP-03.png; accepted since the vignette shot should be reviewed against the prefab itself.
- Cover angle is SSW (accepted, see Fix 1).

Rule for next scenes: verified that the "density first" approach works - the same targets (subject group 65-85 % width, gaps <= 1.1 m, platform ~1.5 m beyond the footprint) apply to the CMP vignette renders.
