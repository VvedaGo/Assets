# Farm Animals — Asset Store package metadata

Updated: 2026-11-25. Scope: Assets/FarmAnimals on branch Farm-Animals (commit 6cd6542 and later). Status: all text fields prepared; price proposed and awaiting the owner's confirmation; clean-project import and Asset Store Validator not run yet (see [PUBLISHER_NOTES.md](PUBLISHER_NOTES.md)). No portal fields were changed.

Copy-ready English fields are below and, one file per field, in [Copy_Fields](Copy_Fields). Measured facts: [PACKAGE_AUDIT.txt](PACKAGE_AUDIT.txt) (generated in Unity by `FarmAnimals.Editor.FarmAnimalsAudit`) and `Assets/FarmAnimals/Documentation/ImportReport.txt`. Media registry: [Media/README.md](Media/README.md).

Title length: 41 characters. Summary length: 180 characters including spaces. Tags: 15. These are local preparation figures; current portal limits have not been inspected.

## Title

```text
Farm Animals - Low Poly Rigged & Animated
```

## Category

```text
3D / Characters / Animals
```

## Price

```text
14.99 USD
```

## Version

```text
1.0.0
```

## Support

```text
For questions and support, contact sergvved@gmail.com. Please include your Unity version, render pipeline version and a description of the issue.
```

## Support Email

```text
sergvved@gmail.com
```

## Tags

```text
low poly, stylized, farm, animals, livestock, poultry, pets, rigged, animated, cow, horse, chicken, dog, cat, URP
```

## Summary

```text
35 rigged and animated low-poly farm animals: livestock, birds, pets, small animals and insects. 113 clips, Animator Controllers, animation events, 8 groups and 2 demo scenes. URP.
```

## Description

```text
Bring your farm to life.

Farm Animals is a colorful low-poly pack of 35 rigged and animated animals for farm games, cozy countryside scenes and stylized worlds. Every animal is a ready prefab with its own Animator Controller, so you can drop it into a scene and press Play: cows graze, hens peck, ducks swim, the dog sits and the fox sneaks.

The animals share the faceted flat-color style of the Farm series (Farm Market, Farm Yard, Farm Nature) and fit next to those packs, but they do not need them.

KEY FEATURES

- 35 animals with a Generic rig each (15-29 bones), skinned meshes and a valid Generic avatar.
- 113 in-place animation clips at 30 fps: 2-3 per animal, 14 for the cow.
- One Animator Controller per animal: a Locomotion blend tree driven by "Speed" (Idle - Walk - Run/Trot) plus one bool per extra clip (Graze, Peck, Swim, Lie_Idle, Sit_Idle...).
- 182 animation events (footsteps, pecks, wing flaps, paddling, landing...) received by a small FarmAnimalEvents component and re-raised as C# events for your sounds and effects.
- 8 composition prefabs: Pasture, Stable, Sheep Flock, Pigsty, Barnyard, Pond, Garden, Orchard.
- 2 demo scenes on floating islands with a demo script that cycles every clip or lets the animals wander.
- One 256 x 256 palette atlas and one URP/Lit material per animal.

WHAT'S INSIDE

Livestock (13): cow, calf, bull, horse, foal, donkey, sheep, lamb, ram, goat, kid, pig, piglet.
Birds (10): hen, rooster, chick, turkey, duck, duckling, goose, pigeon, sparrow, crow.
Pets (4): dog, puppy, cat, kitten.
Small animals (5): fox, rabbit, hedgehog, mouse, frog.
Insects (3): bee, butterfly, ladybug (shown larger than life so they read on a game camera).

ANIMATIONS

Most animals have Idle, a movement clip (Walk, Hop, Scurry, Crawl or Trot) and one signature clip: Graze, Peck, Swim, Root, Browse, Crow, Display, Play_Hop, Play_Bow, Pounce, Nibble, Curl_Up, Paw_Ground, Lie_Idle, Sit_Idle or Fly. The cow has the full set: Idle, Idle_Look, Walk, Run, Eat, Drink, Graze, Lie_Down, Lie_Idle, Sleep, Stand_Up, Moo, Tail_Swish and Hit_React. Clips are in place; the Speed thresholds are the real speed of each clip, so moving the transform at that speed keeps the feet from sliding.

DEMO SCENES

Demo_FarmAnimals_Showcase shows every animal on a floating island per category, cycling through all its clips. Demo_FarmAnimals_Compositions shows the 8 composition prefabs, with the ground animals wandering around their island. Each island has a shot camera for screenshots.

SCOPE

This is an animated art pack, not a farming system: AI, needs, economy, breeding, sounds and riding are not included. Clips are in place (no root motion) and there are no transitions between lying, sitting and standing except the cow's Lie_Down and Stand_Up. Buildings, fences and plants seen in some screenshots come from Farm Yard and Farm Nature and are not included. Source models are supplied as FBX; Blender files are not included. Supplied materials target URP.
```

## Technical Details

```text
ASSETS AND PREFABS
35 FBX models (one animal each) and 35 animal prefabs; 8 composition prefabs that reuse the animal prefabs (Art/Prefabs/CMP). No color variants. 43 prefabs in total.

POLYGON COUNT
406-2,424 triangles per animal, mean 1,366, total 47,816 across the 35 models (each counted once; repeated animals in compositions are not counted again). Measured from the imported Unity meshes.
Livestock: 13 models, 1,144-2,424 triangles, 22,998 total.
Birds: 10 models, 406-1,442 triangles, 9,606 total.
Pets: 4 models, 1,362-1,924 triangles, 6,534 total.
Small animals: 5 models, 906-1,720 triangles, 5,936 total.
Insects: 3 models, 810-1,028 triangles, 2,742 total.

MESHES AND RENDERERS
Cow, bull, calf, horse, foal and donkey are one skinned mesh each. The other 29 animals are built from 16-33 separate skinned part meshes (head, ears, legs...) that share one material. Plan draw calls for large herds accordingly.

LODS
None.

TEXTURES
35 PNG Base Color atlases, 256 x 256, RGB, one per animal. Point filtering, no mipmaps, uncompressed. No normal, metallic, roughness, occlusion or emission maps. The demo uses no texture files.

MATERIALS AND SHADERS
35 materials using Universal Render Pipeline/Lit, one per animal (GPU instancing enabled).
Demo only: 5 materials (4 URP/Lit for grass, soil, rock and clouds; 1 sky material using the included URP shader FarmAnimals/Demo/URP Gradient Sky), 14 generated mesh assets (islands, cloud) and 1 URP Volume profile (tonemapping, color adjustments, white balance, bloom, vignette).

UVS
One UV channel per mesh, laid out on the palette atlas. No lightmap UVs.

RIGGING AND ANIMATIONS
Generic rig and Generic avatar per animal, 15-29 bones; bones stay visible in the hierarchy for attachments.
113 animation clips (109 looping, 4 one-shot), 30 fps, in place, stored inside the FBX files:
Cow 14 (Idle, Idle_Look, Walk, Run, Eat, Drink, Graze, Lie_Down, Lie_Idle, Sleep, Stand_Up, Moo, Tail_Swish, Hit_React).
Calf, Cat, Fox: Idle, Walk, Lie_Idle. Bull: Idle, Walk, Paw_Ground. Horse, Donkey, Ram, Sheep, Goose: Idle, Walk, Graze. Foal: Idle, Walk, Trot. Goat: Idle, Walk, Browse. Lamb, Kid: Idle, Walk, Play_Hop. Pig, Piglet: Idle, Walk, Root. Hen, Chick: Idle, Walk, Peck. Rooster: Idle, Walk, Crow. Turkey: Idle, Walk, Display. Duck, Duckling: Idle, Walk, Swim. Pigeon: Idle, Peck, Fly. Sparrow: Idle, Hop, Fly. Crow: Idle, Walk, Fly. Dog: Idle, Walk, Sit_Idle. Puppy: Idle, Trot, Play_Bow. Kitten: Idle, Walk, Pounce. Rabbit: Idle, Hop, Nibble. Mouse: Idle, Scurry, Nibble. Hedgehog: Idle, Walk, Curl_Up. Frog: Idle, Jump. Bee: Fly, On_Flower. Butterfly: Fly, Perch_Idle. Ladybug: Idle, Crawl, Fly.
182 animation events in the clips (Footstep, Peck, Flap, WingFlap, Paddle, Land, Takeoff, Jump, Sniff, Nibble, Curl, Paw, Pounce, Display, Vocal); FarmAnimalEvents receives them.
35 Animator Controllers: Locomotion blend tree by the float "Speed" plus one bool parameter per extra clip.

COLLIDERS
One CapsuleCollider per animal prefab (35), fitted to the rest pose along the body; it does not follow the animation.

SCALE AND SETUP
1 unit = 1 m, Y up, the animals face +Z, pivot on the ground. Sizes follow the stylized proportions of the models (big heads), for example cow 2.66 m long and 1.81 m to the top of the head, horse 2.97 x 2.39 m, dog 1.15 x 1.15 m, chick 0.13 x 0.15 m. Insects are enlarged: bee 0.08 m, butterfly 0.16 m, ladybug 0.05 m. Prefab names use the FMS_ prefix.

FILES AND SOURCES
Assets/FarmAnimals: 35 FBX, 35 PNG, 35 materials (+5 demo), 35 Animator Controllers, 43 prefabs, 2 scenes, 2 scripts with their assembly definitions, 1 demo sky shader (URP), documentation (GettingStarted.txt, ImportReport.txt, Changelog.txt). No Blender source files, audio or video.

DEMO AND SCRIPTS
Demo_FarmAnimals_Showcase.unity and Demo_FarmAnimals_Compositions.unity (Demo/Scenes); press Play to see the animations. Floating islands and the cloud are 14 generated mesh assets (Demo/Meshes). No camera controller and no input handling; each island has a disabled shot camera.
FarmAnimalEvents (runtime, assembly FarmAnimals.Runtime): receives the clip events and raises C# events.
FarmAnimalDemo (demo only, assembly FarmAnimals.Demo): cycles the clips, wanders or patrols. Not needed in a game.

COMPATIBILITY AND DEPENDENCIES
Created and tested in Unity 6000.3.10f1 with Universal Render Pipeline 17.3.0 (demo scenes played in the Editor without errors). URP is required for the supplied materials. No other packages; the scripts do not use the Input System. Other Unity versions, Built-in and HDRP are not supported or tested; player builds and mobile performance have not been tested.

PACKAGE SIZE
Version 1.0.0 test export of Assets/FarmAnimals: 9,570,046 bytes (9.13 MiB).
```

## Release Notes

```text
Version 1.0.0 - initial release:
- 35 rigged low-poly animals (Generic rig and avatar) with 35 prefabs.
- 113 in-place animation clips, 182 animation events, 35 Animator Controllers.
- FarmAnimalEvents component for clip events.
- 8 composition prefabs.
- 2 demo scenes with a demo script.
- 35 palette atlases and 35 URP/Lit materials.
```

## Changelog

```text
1.0.0 (2026-11-25)
- Initial release: 35 rigged and animated animals, 113 clips, 35 Animator Controllers, 8 compositions, 2 demo scenes, FarmAnimalEvents.
```

## Compatibility

```text
Unity 6000.3.10f1, Universal Render Pipeline 17.3.0. URP is required. Built-in and HDRP are not supported. Other Unity versions and player builds have not been tested.
```

## Dependencies

```text
Universal Render Pipeline (com.unity.render-pipelines.universal 17.3.0 in the authoring project) for the supplied materials and the demo post-processing. No other packages, no third-party assets. The animal prefabs need only the FarmAnimalEvents script included in the pack; the demo script is optional.
```

## AI Disclosure

```text
AI tools were used to create functional content of this package. The 3D models, rigs and animation clips were generated procedurally by Python scripts for Blender that were written with AI coding assistants (Anthropic Claude); concept reference images for the models were generated with an AI image model and are not included. The C# scripts (FarmAnimalEvents, FarmAnimalDemo), the demo sky shader and the Unity import and demo-scene tooling were written with AI assistance. The marketing icon is an AI-generated illustration based on the cow model; the other store images are renders and captures of the actual package in Unity. All content was reviewed and adjusted by the publisher.
```

## Third-Party Content

```text
None. The package contains no third-party models, textures, code, fonts or audio.
```

## Submission Notes

```text
Farm Animals is an animated art package: 35 FBX animals with Generic rigs, 113 in-place clips stored in the FBX files, 35 Animator Controllers and 35 animal prefabs, plus 8 composition prefabs that reuse the animal prefabs. Supplied materials use URP/Lit.

The prefabs carry one small runtime component, FarmAnimalEvents, which receives the clips' animation events (without it Unity would log "AnimationEvent has no receiver"). The demo script FarmAnimalDemo is only used by the two demo scenes; both scripts have their own assembly definitions and no package dependencies.

29 of the 35 animals are made of several skinned part meshes sharing one material; this is stated in Technical Details.

Some store images show buildings and plants from the publisher's Farm Yard and Farm Nature packs as set dressing; the images say "not included". The icon is an AI-generated illustration; see the AI disclosure.
```

## Media

| File, relative to Media/Final | Dimensions | Status |
|---|---|---|
| `01_Icon.png` (master) / `01_Icon_160x160.png` | 1024x1024 / 160x160 | Prepared, local review complete |
| `02_Card.png` (master) / `02_Card_420x280.png` | 1260x840 / 420x280 | Prepared, local review complete |
| `03_Cover.png` | 1950x1300 | Prepared, local review complete |
| `04_Social.png` | 1200x630 | Prepared, local review complete |
| `05_Hero.png` | 1920x1080 | Prepared, local review complete |
| `06_FullCollection.png` | 1920x1080 | Prepared, local review complete |
| `07_Closeups.png` | 1920x1080 | Prepared, local review complete |
| `08_Animations.png` | 1920x1080 | Prepared, local review complete |
| `09_Technical.png` | 1920x1080 | Prepared, local review complete |
| `10_Demo.png` | 1920x1080 | Prepared, local review complete |
| `11_CategoryDetails.png` | 1920x1080 | Prepared, local review complete |
| `12_Compositions.png` | 1920x1080 | Prepared, local review complete |
| `13_Materials.png` | 1920x1080 | Prepared, local review complete |
| `14_Unity.png` | 1920x1080 | Prepared, local review complete |

Video (Media/Video, 1920x1080, 30 fps, 10 s each, slow camera orbit): V1_Farmyard.mp4, V2_Pasture.mp4, V3_PondAndBirds.mp4, V4_Garden.mp4, 10_AllAnimals.mp4. Not uploaded; the portal takes video as a YouTube/Vimeo link, so a 30-60 s edit and an upload are still needed. Final images are PNG; JPG upload copies have not been made. Social caption for a text-free image: "Plants, fences and other set dressing are from Farm Yard / Farm Nature (not included)."

## Publication fields still awaiting publisher data

Price confirmation (14.99 USD proposed), publisher website and documentation link, publisher logo for the title plates, confirmation of the AI disclosure wording. Clean-project import, Asset Store Validator and the final .unitypackage are still to be done. See PUBLISHER_NOTES.md.
