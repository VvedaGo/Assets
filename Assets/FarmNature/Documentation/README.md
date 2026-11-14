# Farm Nature — Low Poly Crops, Trees & Landscape

Version 1.0.0. Support: sergvved@gmail.com.

Create colorful farm surroundings with crops, orchards, woodland details, flowers and mesh-based landscape pieces. The pack contains 88 individual art models and 88 art prefabs. Stage, size and appearance variants are counted individually.

## Getting started

Use Unity 6000.3.10f1 and Universal Render Pipeline 17.3.0. Open **Tools > Farm Nature > Getting Started**, then **Open Showcase Scene**. The window provides buttons to frame the overview, six scene studies and the asset collection. Use Unity's regular Scene view navigation to inspect the content. In Play mode, the main camera shows the overall landscape; there is no player controller or scripted camera navigation.

Existing URP projects can use their own render pipeline. For a fresh project, the optional assets in `Demo/Settings` provide a basic URP renderer and pipeline. Assign `FarmNature_DemoPipeline` under **Project Settings > Graphics** and the current **Quality** level. These are demo resources: importing the pack or opening its welcome window does not automatically change project-wide graphics settings. Built-in and HDRP materials are not supplied.

## Folder guide

- `Art/Models`: FBX source models, arranged by category.
- `Art/Prefabs`: 88 individual art prefabs, arranged by category.
- `Art/Materials`: 27 URP/Lit art materials.
- `Art/Textures`: 27 opaque RGB Base Color PNG textures, all 256x256.
- `Demo/Scenes`: the organized showcase scene.
- `Demo/Materials`, `Demo/Textures`: presentation ground, clouds, sky and underside resources, kept separate from the reusable art.
- `Demo/Settings`: optional demo URP configuration.
- `Documentation`: instructions, changelog and measured model inventory.
- `Editor`: the small Getting Started window. It is editor-only and adds no gameplay code to builds.

Production scripts, marketing images, concept generations, previous exports and validation logs are excluded from this asset folder and delivery package.

## Demo hierarchy

- `01_Overview`: assembled farm landscape.
- `02_SceneStudies`: vegetable garden, harvest field, apple orchard, pond and bridge, forest edge, flower path.
- `03_AssetCollection`: six grouped category displays.
- `04_Presentation`: clouds, island undersides and other demonstration framing.
- `Main Camera`: a single enabled overview camera and Audio Listener.

The scene studies are arranged scene objects, not separate composition prefab assets. Ground and sky elements in Demo are presentation resources. Individual reusable art is under Art/Prefabs.

## Contents

| Category | Individual prefabs |
|---|---:|
| Crops and wheat field tiles | 24 |
| Trees | 9 |
| Garden beds and supports | 6 |
| Flowers | 5 |
| Grass and reeds | 4 |
| Bushes | 3 |
| Hedges | 3 |
| Fern | 1 |
| Ground pieces | 6 |
| Paths | 7 |
| Water and crossing pieces | 9 |
| Rocks | 6 |
| Wood details | 5 |
| Total | 88 |

## Crop growth stages

Wheat, corn, carrot, cabbage, tomato, pumpkin and sunflower each have S1, S2 and S3 static prefabs. Replace an instance with the next stage in your own gameplay code. The three additional wheat field tiles represent green, golden and stubble fields. Timers, harvesting, saving and economy systems are not included.

## Placement and materials

Prefab roots use position zero, identity rotation and unit scale. File units are metre-scale with Y up. Place models with their lower geometry at the desired ground level; exact fits between path and water pieces can need manual adjustments. There is no automatic terrain, road generation or snapping tool.

Art uses color-palette/atlas-style UV layouts, one UV channel per source mesh, and URP/Lit materials. Textures use Point filtering without mipmaps. No PBR map set or lightmap UV channel is supplied. Duplicate a material before making project-specific color changes if other instances should keep their appearance.

Each art prefab has a simple Box Collider. These are whole-object bounds, not precise mesh collision. For walkable bridges, openings, curved paths and water triggers, configure the collider for your game's requirements. No Mesh Collider coverage is promised.

## Technical scope

Static meshes; no LODs, skeletons, skinned renderers, animation clips, wind animation or water simulation. No farming framework, another farm pack or additional gameplay plugin is required. Art FBX source files are included; native DCC project files are not.

`ModelInventory.csv` lists per-model triangle counts. Repeated instances in the demo do not count as new art models. This inventory does not include procedurally assembled demo ground and cloud geometry.

## Troubleshooting

**Pink materials:** install and activate URP. The supplied art is authored for URP/Lit. Check the pipeline override in the active Quality level as well as Graphics settings.

**Frame selected objects:** use the Getting Started window or select a hierarchy group and press F in Unity's Scene view. The overview camera does not provide navigation controls.

**Crop stages overlap:** place one stage at a time in the gameplay scene. Growth is represented by prefab replacement rather than a morph animation.

**A Box Collider covers too much:** adjust its bounds, use several primitive colliders, or choose a collider suited to your gameplay. Static water pieces should often use triggers or no collider.

## Support

Email sergvved@gmail.com with your Unity version, URP version, the relevant prefab name and reproduction steps. Include a screenshot if the issue is visual.
