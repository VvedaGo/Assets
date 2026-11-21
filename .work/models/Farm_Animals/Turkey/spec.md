# BRD-07 Turkey - spec (Farm Animals extension, skeleton B, MESH ONLY: no armature, weights or clips)

Reference: `planning/FarmAnimals/references/BRD-07.png` (1536x1024, front-left three-quarter, body yaw ~40 deg from the
front, elevation ~10 deg; turkey faces image-left, near side = turkey's left = +X, both eyes visible).
Catalogue: FARM_ANIMALS_PACK.md 5.2 BRD-07 - dark plumage, red coral on the neck, fan tail, 0.90 x 0.75 m, 1300 tris, B.
Anchors followed: BRD-02 Rooster (`../Rooster/build_rooster.py`, spec, preview): part names, tilted front body rings
(breast flows into the neck, body cap inside Neck1), ring-frame neck, ray-cast eyes / wing sections hugging the body,
diamond-section plates, 6-gon legs, toes with a sloped sole, Workbench sheet + EEVEE preview via
`_common/animal_render.py` (read-only). BRD-05 Goose for the big-bird body/legs. House style 11/11b.

## Measured from the reference (ground y~985 px, fan top y~30 px -> 0.75 m => ~0.000785 m/px vertical)
| Feature | px | m (design) |
|---|---|---|
| fan top / head top (with caruncles) | y 30 / 45 | 0.75 / 0.74 |
| eye centre / disc | y 105 / ~28 px | z 0.69 / 24 mm 8-gon |
| beak | y 135-225, ~60 px wide | top of base z 0.68, tip z 0.60, base 0.05 wide, points down-forward |
| head (without bumps) | ~150 px wide | 0.11 wide, z 0.60-0.71 |
| dewlap (long red wattle) | y 220-480, ~70 px wide | z 0.62 -> 0.39, 0.05 wide, in front of the neck onto the breast |
| neck | y 230-470, ~150 px wide incl. bumps | z 0.40-0.62, 0.10-0.13 wide, nearly upright |
| caruncles | ~35-45 px blobs | r 0.018-0.024, crown + neck sides |
| back / belly bottom | y 280 / 770 | 0.55 / 0.17 |
| wing | x 680-1030, y 380-840 | shoulder pad z 0.38-0.50, drooping primaries to z ~0.13 |
| thigh bottom / shank | y 810 / 60 px wide | z 0.14 / 6-gon r 0.024 |
| toes | ~130 px | front 0.11, sides 0.095, back 0.05 |
| fan | root behind the rump, 9+ broad plates | radius 0.41, spread +-80 deg, tilt back 15 deg, cupped forward |
Design: length beak tip -> fan rear ~0.80 (see deviations), height 0.75, width = fan ~0.80.

## Features (must read at 128 px)
Big round dark-brown egg body with a full breast; thick upright bare red neck + red head with caruncle bumps (crown,
neck sides) in a deeper red; long deeper-red dewlap from the chin onto the breast; tan beak pointing down; dark 8-gon eyes
#2A1D17; folded dark wing (shoulder pad, lower band, 3 drooping primaries); BIG upright fan of 9 chunky diamond-section
plates with depth-alternating overlaps, colour bands from the root: dark / mid brown / dark band / light-brown tips;
small near-black breast tuft; feathered thighs; thick orange 6-gon shanks, pad + 3 front toes + back toe.

## Parts (objects = skeleton B names, pivot at the joint; root empty FMS_Turkey on the ground under the centre of mass)
Body, Neck1, Neck2 (each with its own neck-side caruncles), Head (+ upper beak), Beak_Lower, Wattle (dewlap + crown
caruncles; bind to Head), Eye.L/.R, BreastTuft (bind to Body/Neck1), WingUpper/WingLower/WingTip .L/.R,
TailFan1 (rump wedge), TailFan2 (5 centre plates), TailFan_Side.L/.R (2 outer plates each; bind to TailFan2 or own bones
for the display spread), LegUpper/LegLower/Foot .L/.R. Neighbours overlap at joints.

## Material class
Flat palette, own atlas `T_FarmAnimals_Turkey_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Turkey`.
Cells: 0 body #3E2D28, 1 body dark #2F221E, 2 wing #4E3A32, 3 wing dark #3A2A25, 4 fan dark #33251F, 5 fan mid #5F4232,
6 fan tip #85603F, 7 body light #47352E, 8 head #D8656A, 9 head dark #B9474E, 10 wattle #CC2F38, 11 beak #EBB070,
12 beak dark #CF8F52, 13 leg #E57A30, 14 leg dark #C45F24, 15 eye / tuft #2A1D17.

## NOT modelled
ground, individual body feathers, separate snood over the beak (merged into the dewlap as in the reference), nostrils,
claws, spurs, leg scales, eyelids. No armature, weights or clips.

## Deviations (reference wins)
- Head/neck red-pink as in the reference, not bluish.
- Length: upright fan (display pose of the reference) gives ~0.80 m instead of the catalogue 0.90 (folded tail).
- Breast tuft: not visible in the reference (dark on dark); kept small per the brief.

## Rounds
1. 1418 tris, all checks 0. Worst: red neck hidden/thin, caruncles sparse small spikes; fan sky gaps near the root
   (front view); primaries thin sticks below the body. -> body front lowered, neck + head wider, 17 bumps, fan roots wider,
   2 wider primaries.
2. (EEVEE) caruncles crystal-like, one neck bump landed on the shoulder; flush near-black tuft read as a slot; eye small.
   -> 6-gon flatter bumps, lowest neck bump removed, straight hanging tassel, eye r 13.5 mm.
3. Tuft a thin stick, primaries thin blades from behind, crown bumps spiky. -> chunky short tuft wedge, thicker/shorter
   primaries, bigger crown bumps. Views checked: 3/4 ref, side, front, back, top, 128 px, EEVEE preview.
Remaining nitpicks: crown reads as a ring of bumps rather than the reference's fully bumpy head; head ~15 % smaller and
beak shorter than the reference; neck caruncles fewer (4 per side vs ~6); primaries visible as two plates from behind.

## Result
1442 tris (target 1300, +11 %). Size W 0.831 (fan) x L 0.699 x H 0.759 m. Checks: non-manifold 0, loose 0, degenerate 0,
coplanar 0, mirror 0.000000, worst contact gap 0, lowest z 0. FBX re-import: 25 meshes + root, 1442 tris, same dims,
texture found in FMS_Turkey.fbm.

## Rig / animation (rig_turkey.py + turkey_clips.py, copied from ../Rooster; mesh unchanged)
- Skeleton BT = bird B (20) + Wattle (child of Head) + TailFan_Side.L/.R (children of TailFan2) = 23 bones. Binding: parts
  rigid on their bone; Eye -> Head, BreastTuft -> Body; Wattle part split per vertex: crown caruncles (z >= 0.645) -> Head,
  dewlap -> Wattle bone; neck blends Body|Neck1|Neck2|Head (18 vertices). TailFan2 bone along the centre plate (round 1
  used a 40-deg plate tip: skewed local X, the fan pitch barely tilted it).
- Fan: Idle/Walk use a RELAXED fan (TailFan2 pitched 35 deg back, outer plates folded 44 deg in about the fan-plane
  normal = a lowered, closed tail); Display opens it to the full upright spread of the mesh (+6 deg wider). Dewlap drape:
  Wattle world rotation = slerp(head, Neck1, 0.8) + lagged swing, so it stays on the neck front while the head moves.
- Turkey_Idle 3.5 s / 105 f (chest out, breathing, head looks in jerks, dewlap swings after snaps, fan sway, wing settle).
  Turkey_Walk 1.0 s / 30 f (0.24 m/s, step 0.144 m, lift 5 cm, head-hold bob 5 cm, fan + dewlap sway; Footstep events).
  Turkey_Display 4.0 s / 120 f (fan rises/opens 0.05-0.22, held with chest puffed 9 deg, neck S pulled back, head low,
  wings out + primaries drooped, slow strut turn +-9 deg with feet planted, fan rattle 14 Hz at 0.42-0.57, closes
  0.76-0.94; events FanOpen f27, Rattle f52).
- Metrics: closure 0.0 deg / 0.0 m all; lowest vertex 0.0 / -0.7 / -0.9 mm; walk slip 0.21 %; limit violations 0
  (relaxed fan pitch 42 -> 35 deg to stay inside TailFan2 x >= -40).
- FBX: 25 skinned parts + Rig (23 bones), takes 106 / 31 / 121 f, 1442 tris, re-import vertex error 0.0 m, texture found.
- Unity note: the Idle/Walk fan is closed/lowered; the reference/preview pose (open fan) is the Display hold.
