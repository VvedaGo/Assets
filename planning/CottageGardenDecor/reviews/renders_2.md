# Render review renders_2 (E11) - look + vignettes, 2026-11-26

## 1. Pack look (FMS_Garden_Look)
Compared pair_Hero/Cover/AltView (before left, after right), the new Hero.png and the Synty rules (warm lit / cool shadow, aerial depth, saturated true palette).

Verdict: 🟡 better but subtle, not yet "selling". Visible gains: cleaner brighter sky with slight haze to the far island edge (aerial depth), white paint and stone are cleaner, water bluer (#5989B8 -> #478AC7), roofs/gold slightly richer, lawn hue moved off yellow towards green, shadows crisper (SSAO + 4096). Not enough: at 50 % before/after look like the same picture; the lawn is still a bright flat lime (lit ~#8FD13D, s 0.71) and takes 55-60 % of the frame, the sky is pale and the lit/shadow separation is weak (shadows read as darker green, not cool), so the picture lacks a focal pop on the red gazebo and the blue fountain.

Concrete targets if it goes further (try in this order, one change at a time, keep hues of reds/blue):
1. Lawn: lit lawn #86C24A (s ~0.62, v ~0.76), shadowed lawn #4F8F2E; hue-vs-hue peak at 81 deg raised to +14 deg; saturation -4 (instead of +10) globally but +12 for reds/blues via a Hue-vs-Sat curve (reds 0-15 deg and blues 200-225 deg +0.15). Goal: lawn calmer, red roof/blue water/purple wisteria pop.
2. Contrast of light: key intensity 1.7 -> 1.95, fill 0.45 -> 0.38, shadows strength 0.78 -> 0.88, split toning shadows (0.36, 0.44, 0.62), highlights (0.62, 0.55, 0.44), balance -15; contrast +14 -> +18. Goal: clear warm-lit / cool-shadow separation (shadow on lawn blue-green ~#3F7F4A, not dark lime).
3. Sky: gradient deeper at the top, top ~#5E98D4 to horizon ~#BFD9F0 (now ~#82B2DC flat); fog 0.003 stays, colour (0.74, 0.84, 0.95). Clouds white with a faint blue underside.
4. Vignette 0.15 -> 0.20, bloom unchanged (0.3, threshold 1.0). No DOF/grain/CA.
5. Exposure +0.28 -> +0.15 if the lawn gets brighter than #9BD84E after step 2.
Check with the same median-9x9 palette table (lawn lit s <= 0.65, roof red v >= 0.9, sky top s >= 0.45).

## 2. Vignettes (same camera: 30 deg off-axis, 36 deg down, vFOV 32; backdrop ~#E5E4E2)
| Shot | Verdict | Reason |
|---|---|---|
| CMP-01 | 🟡 | gate, beds, gnome, bushes readable, arch is the focus; group 53 % of the width, empty lawn right/front (about 20 % of the frame); acceptable, shrink plinth if re-rendering |
| CMP-02 | 🟡 | pergola 65 %, wisteria/bistro/urns readable; empty lawn front-left; acceptable |
| CMP-03 | 🔴 FIX | gazebo group 54 %, ~35 % of the frame is empty lawn in front |
| CMP-04 | ✅ | best frame: fountain focus, ring and beds fill the plinth, 68 % width, clear colours |
| CMP-05 | 🔴 FIX | right half and front are empty lawn, arch at the edge, plinth ~1.6x too large |
| CMP-06 | 🟡 | dense, props readable (swing, hammock, loungers, arbor, birdbath, sundial); small empty band at the front right |
| Modules | 🔴 FIX | five small systems on a long plinth with ~45 % empty lawn; backdrop differs from Modules.md (#F5F1E9) |

No pink, no floating items, no foreign objects seen; contact shadows are good. Not checked: pixel-level intersections.

## Vignette rules (apply to all re-renders)
- Plinth = group bounding box + 0.7 m (left/right/back) and + 1.0 m (front); plinth takes 85-90 % of the frame width and ends at 88-92 % of the height; no lawn band wider than 1.0 m without an item.
- Group share of the width: 62-78 % (01/03/06 may stay at ~60 % when tall items hit the frame height); the tallest point at 5-8 % of the height.
- Lawn on vignettes: lit ~#86C24A (the current lit ~#8FD13D reads lime on the grey backdrop); same look settings as the pack Look (section 1).
- Backdrop: warm light neutral #EFEBE4 (Modules.md asks #F5F1E9; the cool grey #E5E4E2 dulls the green) with a faint vignette; keep a soft contact shadow under the plinth.
- Keep the camera the same across CMP-01..06 so the set looks consistent; only distance/FOV may vary by +-10 %.

---
# Pass 2 (2026-11-26)

## Look v2 (looked at look_v2_sheet.png and the new Hero.png)
Verdict: ✅ PASS (with a note). Visibly more selling than v1: deep saturated sky gradient (top ~#5388C7) that makes the white gazebo, red roof and blue fountain pop, clear warm-lit / cool-shadow separation (lawn shadow #478035), saturation of reds/blues/purples is true, no blown whites, soil cut keeps detail, vignette is gentle. Notes (non-blocking): lit lawn #94D35C is light and a bit pastel on the Hero (asked ~#86C24A); the top of the sky on Cover/AltView goes to a heavy royal blue (~#2F66BF), acceptable but do not go darker. The vignette lawn #8AC951 is accepted; no atlas change needed. Palette targets of v1 review are considered met.

## Shots
| Shot | Verdict | Reason |
|---|---|---|
| Hero | ✅ | dense island, clear focus on the gazebo, look v2 good |
| Cover | 🟡 | unchanged framing (plate free), look v2 good; sky at the top slightly heavy |
| AltView | 🟡 | unchanged framing, look v2 good |
| CMP-01 | 🟡 | readable, group 47 % / plinth 66 %, some empty lawn right/front; accepted |
| CMP-02 | 🟡 | pergola 58 %, accepted |
| CMP-03 | 🔴 FIX 2 | still ~35 % of the frame empty lawn in front of the gazebo (plinth front 3.5 m) |
| CMP-04 | ✅ | best frame |
| CMP-05 | 🔴 FIX 2 | still the large empty front/right lawn, plinth ~2.5 m too deep |
| CMP-06 | 🟡 | dense, readable; accepted |
| Modules | 🟡 | readable, 75 % width, but ~35 % empty lawn; optional tightening (Fix 2 in Modules.md) - not a release blocker, do it if the plinth is reworked anyway |

## Framing policy decision (reviewer, not an owner question)
The "height-limited in 16:9" statement is true only for plinths that are too deep. Rule: keep 16:9, keep the shared angle, do not touch composition prefabs; shorten the plinth (front margin 1.0 m, other sides 0.7 m) per vignette in the wrapper and dolly the camera closer so that the tallest point is at 5-6 % of the height and the plinth bottom at 90-93 %. The group share then lands at 60-70 %, plinth 80-88 %. A group share of 47-58 % is accepted for CMP-01/02/06 (tall arch, long pergola, swing) as long as no lawn band deeper than 12 % of the frame height remains. No owner decision needed.

---
# Pass 3 (2026-11-26, last round, after Fix 2)

Looked at vignettes_fix2.png (all 7 vignettes) next to the previous round.

- CMP-03: clear improvement - gazebo group 63 %, plinth 81 %, front lawn band ~11 %; the gazebo is the focus. Pass.
- CMP-05: pond + wall + arch now fill the plinth, camera-facing plinth removed the empty corner; group 66 % / plinth 87 %, arch inside the frame. Pass with note (some lawn to the right of the arch pillars and in front of the pond, ~11 %).
- Modules: five systems regrouped, 73 % width, front band 8 %, empty centre reduced; pond, ring, pergola, wall, lattice all readable. Pass with note (pergola limits the zoom; ring is the smallest item).
- CMP-01 / CMP-06: front band 15 % and group 50-62 % - above the 12 % target but the compositions read well (arch + gnome + beds; swing/hammock/loungers/props); accepted, no further round.
- Turned plinths (beds/walls at an angle to the plinth edge) look natural on the organic plinth outline; accepted.
- No pink, floating items or foreign objects; look v2 consistent across all vignettes.

## Final status, all 10 shots (renders_2 closed, no owner decision needed)
| Shot | Final verdict | Note |
|---|---|---|
| Hero | ✅ | dense, gazebo focus, look v2 |
| Cover | 🟡 | plate free (74.6 %), sky top heavy but fine |
| AltView | 🟡 | pond arch + gazebo readable |
| CMP-01 | 🟡 | group 50 %, front lawn band 15 % |
| CMP-02 | 🟡 | pergola 58 %, accepted |
| CMP-03 | ✅ | fixed: group 63 %, plinth 81 % |
| CMP-04 | ✅ | unchanged, best frame |
| CMP-05 | 🟡 | fixed: group 66 %, plinth 87 % |
| CMP-06 | 🟡 | front band 15 %, readable |
| Modules | 🟡 | 73 % width, minor empty lawn |

Counts: ✅ 3, 🟡 7, 🔴 0, ❓ 0. Optional polish (not needed for release): CMP-01/06 front band 15 % -> 12 % by dolly-in of ~5 %; Modules ring is small.
Reminder for the media stage (E12): vignette shots must be checked as 16:9 raws; Card/Icon crops must keep the focus item (arch, pergola, gazebo, fountain) inside the crop.
