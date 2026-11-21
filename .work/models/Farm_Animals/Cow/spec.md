# LIV-01 Cow - spec (pilot of Farm Animals, skeleton Q)

Reference: `planning/FarmAnimals/references/LIV-01.png` (1536x1024, near-side view from front-left, slightly above).
Catalogue: FARM_ANIMALS_PACK.md 5.1 LIV-01 - Holstein, 2.3 x 1.45 m, 2200 tris, skeleton Q, pilot.
Anchors followed: house style of Farm Processing previews (flat 4x4 palette, faceted, chunky) and the preview template
(`render_preview_template.py`, 1280x800 EEVEE, three-quarter front-left); Pumpkin/Cabbage approach for organic bodies
(lofted faceted rings, no UV spheres, features sunk into the body). No earlier rigged anchor exists - this is the first.

## Measured from the reference (ground y=950 px, withers y=215 px -> 1.45 m, ~0.00197 m/px)
| Feature | px | m (design) |
|---|---|---|
| withers / back height | 735 | 1.45 (back flat 1.43-1.45) |
| belly underside | 310 | 0.60 (legs ~42% of height) |
| head top (poll, no horns) | 850 | 1.60-1.62 |
| horn tips | 920 | 1.74 |
| nose centre | 600 | 1.13 |
| head length poll->nose, 40 deg down | ~320 | 0.58 (about 120% of a real cow head) |
| leg width upper / knee / lower | 85 / 70 / 65 | 0.21 / 0.17 / 0.14 (8-sided) |
| hoof height / width | 45 / 80 | 0.10 / 0.17 (dark) |
| udder bottom / teat tips | 690 / 725 | 0.48 / 0.42 |
| tail tuft bottom | 710 | 0.44 |
| nose -> rump | - | 2.30 (catalogue; 3/4 view foreshortens) |
Body width (not visible in a 3/4 view): 0.81 m chunky barrel (real Holstein ~0.65).

## Features (all must read at 128 px)
boxy faceted barrel with flat back, big head tilted 40 deg down, white blaze + pink muzzle with 2 dark nostrils,
black patch around eyes and ears, dark disc eyes (8 sides, 5 mm proud), horizontal black leaf ears, 2 small cream horns,
short thick neck wedge into the chest, 4 thick 8-sided legs with knee band and dark flared hooves, pink udder with
4 teats, thin tail with black spindle tuft. Holstein patches: 3 big black patches per side (shoulder, mid body over
the back, rump wrapping the rear), asymmetric left/right; face colours assigned per triangle by distance to ellipsoid
patch centres (body 440 triangles).

## Material class
Flat palette, own atlas `T_FarmAnimals_Cow_BaseColor.png` (256 px, 4x4), material `M_FarmAnimals_Cow`.
Cells: 0 white, 1 white shade, 2 black (patch), 3 black dark (tuft), 4 pink muzzle, 5 pink dark (teats), 6 udder,
7 nostril, 8 eye, 9 hoof #3A2E28, 10 horn, 11 horn tip, 12-15 spare series colours. Variants (brown/red/black)
swap cells 2/3 only.

## NOT modelled
ground, grass, trough, bell/collar, ear tags, eyelids, nostril holes, teeth/tongue, dewlap folds, individual hair.

## Rig / animation
Skeleton Q (27 bones) from `_common/animal_species.py`; parts bound rigidly, smooth weights at body (Pelvis/Spine1/
Spine2), neck rings, leg tops and knees, tail rings. 13 clips Cow_*; events in `FMS_Cow.events.json`.

## Rounds
1. Patches read as vertical bands (ring spacing 0.28 m); head small/low; lower legs thin; right horn base used the
   unmirrored direction (mirror error 13.7 mm). -> 15 body rings x 18 sides, compound ellipsoid patches, head +12%,
   legs +12%, horn fix (mirror 0).
2. (EEVEE preview) muzzle pink/white sawtooth (centroid colouring of triangles); ears face the camera and vanish in the
   head patch; horns parallel posts; no sky (camera too high). -> muzzle by ring band, ears swept out/back and larger,
   horns flared, head +7%, preview camera lowered.
3. Remaining (nitpicks / for the owner): near ear still merges with the black head patch from the preview angle;
   patch edges are staircase-like (quad grid) where the reference has free triangular outlines; no knee band on legs;
   short stylized neck -> Eat muzzle at 0.10 m (tall grass), not at the ground.

4. Polish pass (coordinator list): pink inner-ear strip with black rim; body rings slanted (0.13) + half-step phase on odd
   rings + patch-boundary vertex snapping (80 verts moved along their edges onto the ellipsoid field) -> rounded, slanted
   patch blobs; front/hind leg tops flared into chest/thigh, knee/hock band; head group x1.12 about the skull centre;
   udder fuller/lower (teats to 0.365 m); tail set 6 cm further back, bigger tuft; lower legs/hooves +10%; withers hump
   removed (neck top line lowered). Clips (cow-local `cow_clips.py`): Eat muzzle 0.03 m via 0.11 m Neck1 reach (keyed
   location), Lie_Down kneels left then right, Stand_Up pushes up on the left front leg, Sleep head turned 70 deg left and
   hung to the grass beside the left foreleg. Reference angle compare: only pose differences remain (reference head is
   turned toward the camera; ours is the forward rest pose).

## Deviations (polish pass supersedes the list below where they differ)
- tris 2448 (+7% vs the 2288 pilot, +11% vs the 2200 catalogue): knee/hock bands and leg flares (+160).
- mirror: vertex mirror 0 on all non-patched parts; patch-snapped body/neck/head are shape-symmetric within 2.4 cm
  (snapped vertices slide along their own edges, so the silhouette is unchanged).
- Bone overrides kept cow-local (shared animal_species.py untouched): Tail1-3 set back 3-6 cm, Jaw/Ear/Horn/Head tail
  scaled x1.12 about the skull centre. Names and hierarchy unchanged.
- Eat and Sleep key Neck1 location (0.11 m reach); all other clips leave it at rest.
- Tail_Swish: the action keys Tail1-3 only, but Blender's FBX NLA bake writes curves for all bones (tested with
  bake_anim_use_all_bones False: still 28 curve targets) -> Unity clip mask documented in FMS_Cow.events.json.
- tris 2288 vs 2200 target (+4%): 536 on the patched body grid.
- length 2.52 m incl. tail tuft (nose->rump 2.30 m), height 1.79 m incl. horns (withers 1.45 m), width 0.99 m incl. ears.
- Eat muzzle height 0.10 m (neck too short to reach the ground in front of the hooves without curling).
- Tail_Swish keys only Tail1-3; the FBX take still bakes all bones (at rest) - use it with a tail AvatarMask.
- FBX root `Rig` node has Lcl Rotation -90 X (Blender does not bake armatures with bake_space_transform); mesh node 0.
- No LOD1 this round (make_lod1.py works on rigid parts, not on a skinned mesh).

## Round 2 rework (independent review 3/5)
- Torso rebuilt: 11 aligned slanted rings x 14 sides = 304 tris (57% of 536), large facets; patches painted by WHOLE
  triangles from side-projected ellipses (3 per side, white bands and belly between), tooth/notch clean-up (4 passes):
  straight + diagonal facet-border edges, no sawtooth. Side-area shares L 20.8/16.0/9.5 %, R 11.5/17.2/8.6 %.
- Tail: 5-sided strand 0.65 m (0.45 x withers), 15 deg behind vertical, black 5-sided diamond tuft 2x strand width,
  ends at 0.45 m (hock height); Tail1-3 bones moved along it (cow-local override). Tail_Swish amplitude -25%.
- Legs: one taper per leg (apothem 0.101 at z 0.62 -> 0.088 at z 0.10 = 1.15x), parts split invisibly at the knee,
  hoof cap only, hind hock point 2.2 cm back. Head and udder unchanged.

## Cow_Idle rebuild (ANIMATIONS.md: ears + tail)
- 3.6 s / 108 frames loop: 2 subtle breaths, head drift +-2.5 deg, left ear flick (t 0.14) / right ear flick (t 0.46) / small left twitch (t 0.80): up to 16 deg up + 28-35 deg back, fast rise then relax; tail lagged sway (2 cycles, 5/7/9 deg) + one S-swish at t 0.58 (up to 34 deg at the tip). GIF/MP4 via _common/anim_gif.py.
- Graze added (4.0 s loop, Eat pose + bite tugs, 8 chews, 1.2 s head lift, ear flicks, tail sway); Walk sway params raised (nod 5, tail 6/9/12, ear 5). FBX now 14 takes.
