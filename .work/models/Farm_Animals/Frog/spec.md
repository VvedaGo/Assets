# SML-05 Frog - spec (Farm Animals, skeleton H = Q-S without tail, long hind legs; MESH ONLY: no armature/weights/clips)

Reference: `planning/FarmAnimals/references/SML-05.png` (1536x1024). Chubby green tree frog seen from the front-left
(~30 deg yaw, ~25 deg above), sitting upright on straight front legs, hind legs folded Z-shaped beside the body.
Catalogue: FARM_ANIMALS_PACK.md 5.4 SML-05 - green, domed eyes, light belly, 0.10 x 0.06 m, 300 tris, skeleton H.
Lead brief: ~0.10 m long, ~0.07 m tall to the top of the eye domes; target ~900 tris, up to ~1300.
Anchors followed: Mouse (`../Mouse/build_mouse.py`: Model/loft, shared joint rings + hidden cones into the neighbour,
shade by normal, COM shift, objects/export/verify/preview, coplanar_true + x10 copy), Rabbit (Q-S naming), Duckling/Chick
(tiny-model framing, thick toes). `_common` and `Tools/blender` imported read-only.
Script: `build_frog.py -- SML-05 build|look|export`.

## Measured from the reference (eye-dome top y 90 px, front toes on the ground y ~895 px -> 0.070 m => ~0.0000886 m/px)
| Feature | px | model (m) |
|---|---|---|
| eye-dome top | 805 above ground | 0.070 |
| head width | 650 (265..915) | 0.058 |
| eye dome width | ~210 (32 % of the head) | dia ~0.0176 (30 %; brief 28 %) |
| eye disc | ~100-105 (~50 % of the dome silhouette) | 0.70 x socket front face (brief 70 %) |
| mouth line at the snout | 410 px -> 470 above ground | z ~0.041 |
| front leg width lower / upper | ~80 / ~105 | 0.0084 / 0.011 (6-gon) |
| front toes | ~35-40 wide, ~70 long (foreshortened) | 3.0-3.8 mm wide, 8.5 mm long, 2.4 mm thick |
| belly bottom | ~100 above ground | 0.008 |
| hind lump (thigh + shin) | ~280 x 400 | ~0.025 x 0.035 |
| hind toes | ~30 wide | 2.8-3.6 mm wide, 10.5 mm long |

## Features (must read at 128 px)
Wide flat head with a broad rounded snout and a mouth crease (green upper lip overhanging the cream lower jaw); two big
green eye domes on the top/side corners of the head, each with a dark-brown octagon disc facing forward/outward; chubby
body sloping down to the rump; cream bib from the chin over throat, chest and belly (per-triangle edge = slanted facets);
straight thick front legs (elbow slightly out) with 4 splayed flat toes widening to the tips; big folded hind legs (thigh
forward, shin back, long foot forward-outward with 5 splayed toes), no tail. Green in 5 tones by normal, cream in 3.

## Material class
Flat palette `T_FarmAnimals_Frog_BaseColor.png` (256 px, 4x4), `M_FarmAnimals_Frog` (slots listed in the script).

## Parts (object `FMS_Frog_<Part>`, direct children of empty `FMS_Frog`, pivot on the joint)
Pelvis, Spine1, Spine2, Neck1 (hidden connector), Head, Jaw, Eye.L/R, FrontUpper/Lower/Foot.L/R, HindUpper/Lower/Foot.L/R.

## NOT modelled
tongue, nostrils, eyelids/pupils/highlights, webbing, skin spots, ground.

## Rounds (EEVEE sheet: ref angle, side, front, back, top + 128 px; full-size ref-angle frame from round 4)
1. 1130 tris. Toes tiny and crossing (fan angle sign wrong); hind leg a long stick behind the body, body too long;
   head a flat "lid" with a deep groove (open-mouth look); 128 coplanar_true pairs = toe soles of one foot overlapping at
   z = 0 -> toe soles slope 0.8 mm (base) -> 0 (tip): neighbours never coplanar.
2. Toe direction fixed; body shortened (rump y 0.037), back lowered; head snout tapered (HEAD_TAPER), crease 0.6 mm.
3. Toes long thin sticks -> short chunky toes (front 5-6 mm wide, 7.5 mm long; hind 4.4-5.4 x 8.5 mm); chest/rump
   cone fans -> small flat caps; knee/heel cone fans -> flat caps; eye domes rounder; legs thicker.
4. Reference camera 25 -> 18 deg; thigh rounded front (extra ring), bigger, knee higher.
5. Front legs stood apart from a narrow bib -> chest wider/lower (bib 0.052 wide), legs tucked against it; hind thigh
   r 16.5 mm, knee z 0.036 -> reads as a Z fold in side view.
6. Preview self-shadow blotches on the thigh (EEVEE sun shadow texel 1 mm at a 7 cm model) -> preview copied into the
   script with `shadow_maximum_resolution` 0.05 mm, 3 shadow rays, 128 samples (render setting only, not geometry).
Remaining (nitpicks): hind lump is in the head's cast shadow and shows the shin as a separate wedge under the knee (ref:
one smooth tall oval); head is a rounder dome with smaller facets than the reference's big-plane wedge; the flat green
annulus around the eye disc reads slightly "goggle"-like.

## Rework round 2 (coordinator review 3/5: goggle eyes, blob hind leg, pole-like front legs)
1. Eyes: sphere dome, dia 0.0166 = 0.31 x head width; pupil = flush flat front cut of the sphere at 0.8 R, dia 0.6 x dome
   dia; no rim ring; axis forward/out/slightly down so green dome shows around and above the disc. 76 tris each.
2. Hind leg: one teardrop thigh (thin at the hip inside the body, swelling to a round knee: r 8.5 -> 15.5 -> 4.8 mm,
   length 0.0415 = 0.47 x snout-rump), knee out-forward-up (axis 40 deg off the reference view so it is not seen
   end-on); shin back-down on its outer side to the heel; long flat foot (pad 24 mm + toes 9 mm) forward with 5 toes.
   Tried first: thigh along the body pointing forward -> seen end-on from the reference angle (octagon "coin"); fixed.
   Preview sun azimuth mirrored (from the camera side) so the head no longer shadows the near hind leg.
3. Front legs: shoulder -> wrist 0.0279 -> 0.0243 m (-13 %, vertical span -21 %), splay from vertical 14 -> 26 deg;
   body/head lowered 2.5 mm (belly 1 mm). 4 flat toes kept, front foot turned 9 deg further out.
4. Head outline 10 -> 8 points and one level fewer: larger, cleaner facets (62 tris, Jaw 62).
Checked: reference angle, side, front, back, top, 128 px.

## Rework round 3 (second review 3/5: ball thigh, head cap with overhanging lip, non-standard preview)
1. Hind thigh: flattened angular wedge (6-vertex section, ridge top and bottom, flat outer face), hip (back, low) ->
   knee point (front, top) along the body side: 0.050 long (0.56 x snout-rump), 0.018 tall (0.38 x body height), 0.013
   thick (0.22 x body width); shin back-down to the heel, foot forward-out (5 toes). HindUpper 58 tris.
2. Head/jaw: lip ring and the jaw's top ring share one outline (flush), groove between them 0.6 mm deep, 1 mm wide; jaw
   sides under the mouth corners green (|n.x| > 0.62), no overhang step.
3. Preview: pack-standard sun (48, 0, -35) restored, low camera (0.55, -1.0, 0.15) with horizon + sky, fill 0.62 x 0.78
   (Cat/Pig setup); only the fine shadow-texel setting stays. Hind leg is not shadowed by the head with this camera.
Checked: reference angle, preview angle, side, front, back, top, 128 px.

## Result
tris 1048 (target ~900, limit ~1300): HindFoot 80 x2, Pelvis 78, Spine2 78, Eye 76 x2, FrontFoot 68 x2, Head 62, Jaw 62,
Spine1 60, HindUpper 58 x2, FrontUpper 24 x2, FrontLower 22 x2, HindLower 22 x2, Neck1 8 (hidden).
Size: width 0.119 x length 0.091 (snout -> rump 0.089) x height 0.066 (eye tops); head 0.053 wide, belly 0.0058.
Pivot: root at the ground under the volume centroid (shift +0.0133 m in Y); parts pivot on their joints.
Checks: non-manifold 0, loose 0, degenerate 0, mirror 0.000000, worst contact gap 0, coplanar shared 0, coplanar x10 0,
coplanar_true 0, min z 0.
FBX re-import: 20 meshes + root, 1048 tris, dims 0.119 x 0.091 x 0.066, texture found in FMS_Frog.fbm (256x256).

## Deviations
- tris 1048 vs catalogue 300 / brief target ~900 (brief allows up to ~1300).
- Height 0.066 to the eye tops (brief ~0.07): lowered for the shorter front legs and the 0.3 x head-width domes.
- Width 0.119 incl. the splayed hind toes (catalogue gives only 0.10 x 0.06).
- Preview render function copied from `_common/animal_render.preview` (standard camera/lights; finer sun shadow texels only).

## Rig + clips (new skeleton F, rig_frog.py / frog_clips.py; mesh unchanged)
Final export = `rig_frog.py -- SML-05 export`. 22 bones: Root, Pelvis, Spine1, Spine2, Neck1, Head, Jaw, Throat, Eye.L/R,
Front/Hind Upper/Lower/Foot.L/R. Parts rigid; Jaw underside blended onto Throat by height (scale keys = buccal pulse).
Hind knee hinge at HIP.lerp(KNEE, 0.8) (where the shin's hidden cone enters the thigh): a hinge at the thigh tip opened a
1-2 cm gap when the leg unfolds. Generic 2-bone IK (ik2) keeps the rest bend plane; planted feet keep the rest world orientation.
Idle 3.0 s/90 f: 2 breaths (chest only lowers: front legs are at full reach at rest), throat pumps 6x, eye blink, head micro turn.
Jump 1.5 s/45 f (loop with pause): crouch, push (feet planted until f17), air f17-26 (peak +0.078 m, hind legs trail
  extended, front legs fold then reach), front land f27, hind land + squash f29, eyes pulled in, settle; events Jump/Land.
Metrics: closure 0.000 deg / scale 0, lowest 0.0 mm both, planted-foot slip 0.000 mm (Idle) / 0.24 mm = 1.1 % of the foot (Jump),
0 limit violations; FBX re-import 22 bones, 20 meshes, 1048 tris, vertex error 0.0. GIFs: Idle --view 0.75 -1.0 0.22,
Jump --view 1.0 -0.45 0.14 --fill 0.70.
