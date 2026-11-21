# BRD-05 Goose - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-05.png` (1312x1203, front-left three-quarter, body yaw ~45 deg from the
front, elevation ~10 deg, goose faces image-left with the head turned to the camera; near side = goose's left = +X).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-05 - white goose, long neck, orange bill with a knob, broad wings, 0.80 x 0.60 m,
1100 tris, skeleton B.
Anchors followed: BRD-01 Hen and BRD-02 Rooster (`../Hen/build_hen.py`, `../Rooster/build_rooster.py`, specs, previews):
part names, tilted front body rings (breast flows into the neck, body cap inside Neck1), ring-frame neck lofts with
overlap rings, ray-cast eyes and wing sections hugging the body, diamond-section tail plates, 6-gon legs, Workbench sheet
+ EEVEE preview via `_common/animal_render.py` (read-only). House style 11/11b.

## Measured from the reference (ground y~1150 px, head top y~5 px -> 0.60 m => 0.000524 m/px vertical)
| Feature | px | m (design) |
|---|---|---|
| head top / eye centre | y 5 / 105 | 0.60 / 0.55 |
| eye diameter | ~35 | 0.018 -> 0.022 (8-gon, + grey ring 0.034 so it reads on white) |
| knob | x 360-445, y 50-110 | ~0.045 wide, ~0.02 proud above the bill line |
| bill tip | y ~250 | z ~0.47, bill ~0.10 long, broad blunt tip |
| head width / neck width | 250 / 170 px | head 0.11, neck 0.09 at the top, 0.13 at the base |
| neck | y 250-500 | z 0.48 -> 0.30, nearly upright, slight S |
| back (shoulder) / tail tip | y 490 / ~640 | 0.35 / 0.27-0.30 |
| belly bottom | y 935 | 0.11 |
| shank width / visible length | 70 / 165 px | 0.037 (6-gon r 0.019) / 0.09 |
| foot | ~200 px | 0.09-0.10 long, 3 toes with web, toe ridges |
| legs apart | 220 px | x = +-0.062 |
| wing | x 540-1000, y 540-890 | big shield: y -0.11..+0.25, z 0.16-0.33, rear tip over the tail base |
Design: height 0.60, length bill tip -> tail tip ~0.60 (see deviations), body width ~0.27 (+ wings ~0.30).

## Features (must read at 128 px)
Big faceted egg body with a low round breast flowing into a thick upright neck (Neck1 + Neck2, gentle S, overlap rings);
big round white head; orange bill pointing forward-down with a clear rounded basal knob at the forehead and a darker lower
bill; dark 8-gon disc eyes #2A1D17 on a small warm-grey ring; broad folded wings in two warm-white tiers with a proud lower
lip and a rear tip lying over the tail base; short chunky tail fan of 5 broad plates tilted up; white thigh cuff; thick
orange 6-gon shanks; webbed orange feet (3 toe ridges, scalloped web edge, darker ankle pad).

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Goose on the ground under the centre of mass)
Body, Neck1, Neck2, Head (+ upper bill + knob), Beak_Lower, Eye.L/.R (disc + grey ring), WingUpper/WingLower/WingTip .L/.R,
TailFan1 (rump wedge), TailFan2 (5 plates), LegUpper/LegLower/Foot .L/.R. Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Goose_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Goose`.
Cells: 0 body #F3EEE5, 1 body dark (belly/underside) #E0D8CB, 2 body light (top) #FBF8F2, 3 wing #ECE5D9, 4 wing dark
#D9D0C2, 5 tail #E6DFD3, 6 neck/head #F7F3EC, 7 bill #F07A22, 8 bill dark #D7611B, 9 knob #E86C1E, 10 leg #F28A2E,
11 leg dark (pad, web underside) #D96A1E, 12 eye #2A1D17, 13 eye ring #B0A69B, 14 cream #F2E6C9 (spare), 15 green spare.

## NOT modelled
ground, nostrils (dark marks in the ref), bill nail, claws, leg scales, individual feathers, eyelids.
No armature, weights or animation.

## Rounds
1. 1164 tris, checks 0. Worst: body long and duck-like (breast not ahead of the neck), head small + bill long/thin,
   tail a thin horizontal spike, wings flared from the front. -> shorter, deeper body with the breast 5 cm further forward
   and lower, head +10 %, bill 0.088 steeper (39 deg) and thicker, bigger knob, wings 25 % less proud, tail pitched plates.
2. Tail still a spike from the side; neck base too narrow; legs behind the COM. -> chunkier plates at 10-20 deg, wider
   Neck1 base funnel, legs 2.5 cm forward.
3. (EEVEE, ref angle) neck front stood out of the breast as a ledge; whites clipped in the sun so facets did not read;
   eye ring large. -> bigger front body ring inside Neck1 (breast rises up the neck front), Neck1 base lower/inside,
   whites one step darker (warm-white range #C2B8A8..#EAE4DA), ring 15 mm. Final: rump wedge 3 rings, longer and thicker.
Views checked: 3/4 ref, side, front, back, top, 128 px, EEVEE preview. Remaining nitpicks: tail plates still ~3 cm thick
at the tips from the side (ref reads a little fuller); wing outline softer than the ref's big shield at the shoulder;
the grey eye ring is an addition (not in the ref) for 128 px readability.

4. Polish (coordinator review 4/5): ankle ring step above the toes; neck slightly thin at mid-height. -> ankle pad
   removed, one tapered 6-gon shank (r 19.5 -> 17 mm) runs straight into the web; Neck1/Neck2 rings at z 0.40-0.50
   +10 % (S-curve and overlap rings kept). Views re-checked: 3/4 ref, side, front, back, top, 128 px, preview.

## Result
1136 tris after polish (target 1100, +3 %); was 1176 before. Size W 0.324 x L 0.582 x H 0.600 m. Checks: non-manifold 0, loose 0, degenerate 0,
coplanar 0, mirror 0.000000, worst contact gap 0, lowest z 0. FBX re-import: 21 meshes + root, 1136 tris, same dims,
texture found in FMS_Goose.fbm.

## Deviations
- Length: the reference proportions (upright neck, compact body) give ~0.60 m bill tip -> tail tip at 0.60 m height;
  the catalogue 0.80 m would need a much longer body or a stretched neck. Reference wins (rule 11b.10); height 0.60 kept.

## Rig + clips (skeleton B, copied from the Hen: rig_goose.py + goose_clips.py)
Run: `rig_goose.py -- BRD-05 bend|anim|export`. Mesh, part names and pivots unchanged from `build_goose.build()`.
- 20 bones (B template, names/hierarchy ok, roll ok); 21 parts bound rigid (Eye.L/.R -> Head), linear neck blends
  (Body/Neck1 +-20 mm, Neck1/Neck2 +-15 mm, Neck2/Head +-14 mm; 26 vertices).
- Goose changes vs the Hen: species table GOOSE (ends: Head tail = bill tip, Beak_Lower, WingTip, TailFan2); limits widened
  for the long neck (Neck1 x -60..110, Neck2 x -110..130, Head x -125..90); Graze neck IK with bend +1 (arches up-forward)
  and a polar head path around the neck base (neck stays extended at the half lift); rest S-curve kept by the rigid parts.
- Bend test (8 extreme poses): no holes; folded neck poses show faceted creases between Neck1/Neck2 (closed).
| Clip | s / frames | content |
|---|---|---|
| Idle | 4.0 / 120 | smooth looks with holds (9-frame turns): yaw up to 50 deg spread over Neck1/Neck2/Head, tilt 18, reach; breathing; 2 tail wag bursts; 2 wing twitches |
| Walk | 1.0 / 30 | 0.15 m/s, step 0.09 m, duty 0.6; waddle roll 5 deg + sway 8 mm; neck sways 10 deg per step, head level (pitch + roll); webbed toes curl 18 deg in swing; Footstep LegL f0, LegR f15 |
| Graze | 4.0 / 120 | body pitch 14 deg + 12 mm drop, arched neck lowers the bill to 2 cm above the grass 0.34 m ahead; 9 nibbles (Peck events) with the lower bill opening 14 deg; half lift at 0.5, full lift at the seam; tail up 16 deg |
Metrics: loop closure 0.000 deg / 0.000 m all clips; lowest vertex 0.000 / -0.001 / 0.000 m; Walk foot slip 0.39 % of the
step; limit violations 0. FBX re-import: 20 bones, 21 meshes, 1136 tris, 3 takes (121/31/121 frames), vertex error 0.0 m.
Rounds: Idle 1, Walk 2 (neck sway 7 -> 10 deg), Graze 4 (target too close -> neck folded; elbow side; half-lift fold).
Known: the arched graze neck shows faceted step creases at the Neck1/Neck2 seam (rigid parts, no holes).
