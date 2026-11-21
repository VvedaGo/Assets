# BRD-09 Sparrow - spec (Farm Animals, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-09.png` (1536x1024). Front three-quarter: the face and bib look almost
straight at the camera (head turned ~30-40 deg towards it), the body is yawed so the near (left, +X) wing and the tail
point to the right/back; elevation ~8-10 deg.
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-09 - brown-grey, black "beard", small, 0.14 x 0.12 m, 350 tris, skeleton B,
extension. Lead brief: ~450 tris, up to ~650 if it improves the look; eyes readable at 128 px.
Anchors followed: BRD-08 Pigeon v2 (`../Pigeon/build_pigeon.py`: egg head of horizontal tilted rings, pear body of
tilted rings with a pointed front vertex for the V, ray-cast eyes and wing shield, split_to_objects, checks, Workbench
sheet + EEVEE preview via `_common/animal_render.py` read-only) and BRD-03 Chick (tiny-bird preview framing).
House style 11/11b. New here: head and body lofts are built from explicit triangles with a chosen diagonal per quad, so
the colour areas (cap, cheeks, bib) end on clean slanted facet edges instead of quad stair steps.

## Measured from the reference (ground y~985 px, head top y~30 px -> 0.12 m => 0.000125 m/px)
| Feature | px | m (design) |
|---|---|---|
| head width / height above cheek bottom | 485 / 360 | 0.062 / 0.046 (huge round head, top z 0.120) |
| eye centre / diameter | y 215 / 45-50 | z 0.098 / 0.0084 (8-gon, +20 % for 128 px), ~38 deg from the front |
| beak base width / length | 135 / ~90 | 0.017 / 0.013, tip a little down |
| cheek patch | y 225-390, x 330-450 and 590-805 | z 0.074-0.097, lower front-side of the head |
| bib | y 285-515, 150-200 px wide, V point | z 0.059-0.086, 0.025-0.03 wide |
| belly bottom | y ~800 | z 0.022 |
| body width | ~560 px incl. wing | 0.074 (+ wings 0.082) |
| shank | 45 px wide, y 780-960 | 0.0072 (6-gon, +25 % chunkier), exposed z 0.024 -> 0 |
| feet | 180 px span, toes ~25 px | span 0.022, toes 3 front (12/11 mm) + back (7 mm), 3.4 mm wide |
| wing | shoulder (760,280) -> tip (1110,640) | z 0.080 -> 0.050, tip over the rump |
| tail | (1030,600) -> tip (1290,650), ~90 px wide at the end | 0.035 long, end 0.026 wide, back and a little up |
Design: length beak tip -> tail tip 0.14, height 0.12.

## Features (must read at 128 px)
Very round chubby bird: huge round head with a rust-brown cap (darker on the crown), big pale cream cheek patches under
the eyes, large black bib on the throat/upper chest as a rounded shield with a V point, dark 8-gon eyes on the brown,
short thick grey-brown cone beak slightly down; plump tan ball body with a lighter belly; chestnut wing shield with two
pale wing bars and a dark lower edge over the rump; short flat brown tail wedge; two thick orange legs with 3+1 toes.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Sparrow on the ground under the centre of mass)
Body, Neck1, Neck2 (hidden connectors), Head (+ upper beak), Beak_Lower, Eye.L/.R, WingUpper/WingLower/WingTip .L/.R,
TailFan1 (rump connector), TailFan2 (tail wedge), LegUpper (hidden thigh), LegLower (orange shank), Foot (4 toes).
Neighbours overlap 5-10 %.

## Material class
Flat palette, own atlas `T_FarmAnimals_Sparrow_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Sparrow`.
Cells: 0 cap #A85A3C, 1 crown dark #8A4630, 2 cap light #B86C4A, 3 cheek #D9B8A0, 4 nape #9A6A52, 5 bib #2B2420,
6 body #B49A82, 7 body dark #9C8470, 8 belly #CDB8A2, 9 wing chestnut #A0573A, 10 wing dark #6B3B28, 11 wing bar #D8BE9C,
12 tail #7C4A34, 13 beak #8E7A6C, 14 leg #E8A23A, 15 eye #2A1D17.

## NOT modelled
ground, individual feathers, claws, nostrils, eyelids, eye rings, leg scales, wing bars as separate geometry, head turn.
No armature, weights, animation clips; no LOD1 (small animal, same as the other birds).

Palette as built: cheek #ECD2B8 (lighter for contrast), nape #93583C, body #AD9480, body dark #8F7969, belly #C0AC99.

## Rounds (Workbench sheet ref|3/4|side|front|back|back-3/4|top|front-right + EEVEE look + 128 px)
1. 726 tris, 4 coplanar (toe bottoms overlapping at z=0). Body small vs head; bib a wide black band that read as an open
   mouth; cheeks missing. -> toes start 0.6 mm up, bigger body, bib narrowed, necks/thighs 4-gon, beak cone with tip.
2. Head a barrel with a hat-band colour line; black pocket under the beak (head throat recessed behind the chest).
   -> cheek areas as patches with slanted triangle edges, brown around the eyes, body front pushed forward.
3. Head still overhung the chest (bib split by a ledge); wing pale facet at the shoulder; body too wide for the head.
   -> head lower front pulled in, body R0 front moved forward (continuous bib shield), head x1.10, body narrower.
4. Grey wedges split the bib; body showed between wing and head; wing front a block end. -> bib widened on the body,
   shoulder brown, WingLower front tapered, TailFan2 a flat diamond (650 tris).
5. Far eye poked out of the head outline at the preview angle. -> eyes 22 deg from the front, preview yaw ~30 deg.
Views checked: reference 3/4, side, front, back, back-3/4, top, front-right, 128 px (bird, bib and eyes read).
Remaining: the wing reads weaker than in the reference from the front 3/4 (the reference turns the body further and the
head towards the camera); near cheek turns greyish in shade; crown slightly flat; legs ~15 % longer looking.

## Rework round 2 (coordinator review 3/5: tail hidden, wing small, near cheek one flat pale facet)
1. Tail: TailFan2 = 3 overlapping planks (centre 11.6-14.4 mm wide, sides splayed +-11 deg, rolled +-10 deg, 2.6 mm
   lower), 46 mm long, 24 deg up, 5.6 mm thick; rump shortened 4-6 mm so the total length stays 0.143 m.
2. Wing: WingUpper 0.062 long x 0.054 high, 15 mm proud; WingLower 13 mm proud; chestnut shield, pale bar on the lower
   face of WingUpper and on WingLower, dark lower edge and tip over the rump. Preview yaw 37 -> 43 deg, elevation 11 deg.
3. Cheek: vertex on ring H2 at 60 deg pushed out 3.2 mm; cream patch = 6 triangles fanned around it (flat bottom on the
   H1 ring, roof edges against the brown cap) -> rounded faceted patch. Eyes 20 deg from the front (far eye stays on
   the face at the new preview yaw).
Views checked: preview 3/4, reference 3/4, side, front, back, back-3/4, top, front-right, 128 px.
Remaining: tail planks read as 2-3 slats from the 3/4 view (reference: one solid wedge); the pale wing bar is one broad
band plus a thin second one; head still straight (reference turns it to the camera).

## Rework round 3 (second review 3/5: helmet head, triangle cheeks, two tail stubs, loose wing-tip piece)
1. Head rebuilt as a faceted ellipsoid ball 63 x 60 x 58 mm (0.75x body width 84 mm): 5 latitude rings of 12 vertices
   with alternating 15 deg offsets (antiprism strips, no vertical columns), a 6-vertex ring at 66 deg and an apex
   (rounded crown, no flat top). Colours per triangle from the centroid direction (cap, crown, bib, nape, tan below).
2. Cheeks: two 8-gon faceted cream domes (24 facets each), 20 mm across (0.32x head width), centred 42 deg from the
   front and 19 deg below the head centre (below-behind the eyes), rim sunk 0.6 mm, centre 0.9 mm proud, brown cap all
   round the top. The flat cheek triangles of round 2 are gone.
3. Tail: ONE flat 6-sided wedge, 60 mm (0.57x the body length), 20 deg down, 20 -> 36 mm wide, 9.6 -> 8 mm thick;
   TailFan1 = root part (mostly inside the rump), TailFan2 = rest, starting 0.8 mm inset inside TailFan1.
4. WingTip: a tapered dark plate folded from the rear of the wing onto the tail base (ends 1.2 mm above the tail top,
   x = +-8 mm); WingLower ends tucked under WingUpper (no piece hanging below the wing).
Preview yaw 45 deg, elevation 15 deg. Views checked: preview, reference 3/4, side, front, back, back-3/4, top, front-right, 128 px.
Remaining: from the front 3/4 the tail shows only its last ~2 cm beside the wing (the body and wing cover the rest);
cheek pads read as slightly raised discs; the far eye sits on the head outline at the preview angle.

## Deviations
- tris 704 vs catalogue 350 / brief ~450 / ceiling ~650 (+54: ball head with a crown apex, two 24-facet cheek pads).
- Size 0.154 L x 0.122 H x 0.110 W (incl. wings) vs ~0.14 x 0.12: the 0.6x-body-length tail asked in round 3 adds
  ~10 % length; the two numbers conflict, the tail length was kept.
- Head straight (symmetric rest pose); the reference turns the head to the camera. The tail points straight back on
  the centre line (symmetric rest pose); it shows to the back-right only through the preview camera yaw (~43 deg).
- Neck1/Neck2/LegUpper/TailFan1 are hidden or mostly hidden connectors kept for skeleton B.

## Rig + clips (2026-11-21) - skeleton B with flight
Files: `rig_sparrow.py` (species table `SPARROW` only) on ../Pigeon/rig_pigeon.py + pigeon_clips.py (read-only, see the
Pigeon spec "Rig + clips"); Fly GIF via ../Pigeon/fly_gif.py. Run `rig_sparrow.py -- BRD-09 bend|anim|export|meshcheck`.
Mesh unchanged (meshcheck 21 parts, max vertex diff 0.00000 m; texture byte-identical). Anchors: Hen rig B, Pigeon flight.
Wing: WingUpper head = spread pivot 1 cm behind the wing front, WingLower/WingTip heads on their front seams; WingLower is
the band under the shield, so it gets no lag; the tip plate gets a constant 14 deg up lag (it sits 16 deg inward of the
wing axis) + 18 deg beat lag. Hidden neck connectors Neck1 -> Body, Neck2 -> Head; ball head rigid (rotates in place).
WingUpper euler order XYZ (max middle angle 36 deg).
| Clip | s / frames | content |
|---|---|---|
| Idle | 3.0 / 90 | quick head turns in 2-frame snaps (yaw up to 46, tilt 18), fast breathing (5 per loop), 2 tail flicks up, 2 wing flicks |
| Hop | 0.5 / 15 | two-footed hop, 0.06 m per hop (0.12 m/s in place), contact 6 frames (landing dip 6 mm, push), air 9 frames (arc 30 mm, feet tucked 6 mm, toes down 35 deg), body over the feet, tail flick after landing; events Land f0, Takeoff f6 |
| Fly | 0.8 / 24 | 3 beats of 8 frames, flap 10 +- 60 deg, tip lag, sweep/twist on the upstroke, body pitched 22 deg, lowest vertex 0.022 m, feet tucked; Flap events f0/8/16 |
Metrics: loop closure 0.000 deg / 0.000 m; lowest vertex Idle 0.000, Hop -0.0006, Fly +0.022 m; Hop foot slip 0.00 % of the
step, stance feet z 0.000; limit violations 0. FBX re-import: 20 bones, 21 meshes, 704 tris, 3 takes, max vertex error 0.0 m.
GIFs: Idle 2.3 MB, Hop 0.51 MB, Fly 0.74 MB. Rounds: Hop 2 (hop 22 -> 30 mm), Fly 3 (tip plate pointed down off the
wing plane -> constant tip lag; framing).
Remaining: the spread wing reads as shield + pale band + a thin dark tip plate (the folded mesh), at the top of the
beat the two wings show their darker inner faces; not seen in Unity.
