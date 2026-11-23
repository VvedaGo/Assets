# Farm Processing - Low Poly Workshops & Production Props

Documentation, version 1.0.0

## Contents

1. Overview
2. Requirements
3. Folder structure
4. Naming
5. What is included
6. Demo scenes
7. Using the prefabs
8. Technical details
9. Limitations
10. Support

## 1. Overview

A low poly art pack for farm food-processing workshops: cheese, butter, juice, flour, jam, dried fruit, bread, seed oil, smoked food and honey. It contains stations, tools, products, furniture, a modular workshop kit and ready-made compositions. The pack has no scripts and needs no setup.

## 2. Requirements

- Unity 6000.3 (tested with 6000.3.10f1)
- Universal Render Pipeline (URP) 17.3
- Built-in Render Pipeline and HDRP are not supported

## 3. Folder structure

```
FarmProcessing/
  Art/
    Models/      FBX files, one per item (STA, TOL, PRD, FUR, MOD)
    Prefabs/     ready prefabs (STA, TOL, PRD, FUR, MOD) and CMP compositions
    Materials/   one URP Lit material per item
    Textures/    one 256x256 Base Color texture per item
  Demo/
    Scenes/      demo scenes
    Materials/   backdrop materials used by the demo scenes
  Documentation/ this file
```

## 4. Naming

Prefabs are named `FMS_Workshop_<CATEGORY>_<NN>`.

| Code | Category | Count |
|---|---|---|
| STA | Production stations | 12 |
| TOL | Tools | 18 |
| PRD | Processed products | 18 |
| FUR | Furniture | 12 |
| MOD | Modular workshop pieces (plus `MOD_02_Plain`, a plain-floor variant) | 12 + 1 |
| CMP | Ready workshop compositions | 8 |

## 5. What is included

- 12 stations: cheese vat, cheese press, butter churn, fruit crusher, juice press, hand mill, jam kettle, drying rack, bread oven, oil press, smoker, honey extractor.
- 18 tools and 18 processed products (cheese, butter, curds, pomace, juice, jam, dried fruit, flour, dough, bread, oil, smoked fish and ham, honey).
- 12 furniture pieces: tables, shelves, racks, sink, cart and others.
- 12 modular pieces on a 2 m grid: floors, walls, window and door walls, posts, beams, roof panel, shelf.
- 8 compositions: `CMP_01_Dairy`, `CMP_02_Juice`, `CMP_03_Grain`, `CMP_04_JamDrying`, `CMP_05_Bakery`, `CMP_06_SeedOil`, `CMP_07_Smokehouse`, `CMP_08_Honey`.

## 6. Demo scenes

In `Demo/Scenes`:

- `Demo_Catalog` - all items laid out by category.
- `Demo_WorkshopCourtyard` - a full workshop courtyard.
- `Demo_Compositions` - the 8 compositions side by side.
- `Demo_Media` - camera set-up scene used for the store images.

Open a scene and press Play, or use the Scene view. No setup is needed.

## 7. Using the prefabs

1. Drag a prefab from `Art/Prefabs/<category>` into your scene.
2. All prefab roots are at position 0, rotation 0, scale 1. Items stand on the ground at y = 0, except the hanging items (herb bunch, smoked fish, smoked ham), which also rest on the ground and can be raised to any hook height.
3. Stations contain separate child objects for moving parts (lids, screws, handles, doors). Rotate or move these children yourself or with your own animation. No animation clips are included.
4. Stations have a LOD Group (LOD0 and a simplified LOD1).
5. To build interiors, snap modular pieces on a 2 m grid (wall height 2.4 m, door 0.9 x 2 m).
6. Single items have a Box Collider on the root. Compositions contain the colliders of their items.
7. Materials use the URP Lit shader with a Base Color texture. To recolour, edit the item's material or texture.

## 8. Technical details

- 1 Unity unit = 1 metre, Y up.
- 73 FBX files, 81 prefabs (73 single items and 8 compositions).
- Triangles: 28 to 3,384 per item, 63,924 for all single items.
- 73 materials and 73 Base Color textures (256x256, PNG, flat colour atlas, point filtering).
- UV0 only. No rigs, no skins, no animation clips.

## 9. Limitations

This is an art pack. It has no production logic, inventory, recipes, economy, saving, characters, animation clips or fluid simulation. Separated moving parts are not ready-made animations.

## 10. Support

Email: sergvved@gmail.com. Please include your Unity version, render pipeline and the name of the affected prefab.
