COTTAGE GARDEN DECOR  (v1.0.0)
Stylized low poly cottage garden decor: 42 models (60 prefabs with colour and mesh variants) + 6 ready compositions.
Rose arches, hexagonal gazebo, pergola with extension bay, fountains, flower beds, roses, topiaries, garden furniture,
modular lattice screen, stone wall, brick edging and formal pond. Final pack of our Farm series.

REQUIREMENTS
- Unity 6000.3 (tested with 6000.3.10f1).
- Universal Render Pipeline (URP) 17.3. Built-in Render Pipeline and HDRP are not supported.
- No scripts, no other packages.

QUICK START
1. Open Demo/Scenes/Demo_CottageGarden.unity and look through the Game view (or press Play).
2. Demo/Scenes/Demo_Compositions.unity shows each composition and the modular systems on their own plinths;
   Demo/Scenes/Demo_Catalog.unity shows all 60 prefabs and the 6 compositions in rows with ID labels.
3. Drag any prefab from Art/Prefabs/<Category> into your scene. Art/Prefabs/CMP holds the ready compositions.

FOLDERS  (Assets/CottageGardenDecor)
  Art/Models        FBX meshes, one FBX per prefab, grouped by category (LOD1 parts are inside the FBX where used)
  Art/Textures      2 colour atlases, 256 x 256 PNG: FMS_Garden_AtlasA, FMS_Garden_AtlasF
  Art/Materials     2 URP/Lit materials: FMS_Garden_AtlasA, FMS_Garden_AtlasF
  Art/Prefabs       Prefabs by category (STR, MOD, FLB, WTR, ORN, FUR, PLT, TOP) and compositions (CMP)
  Demo              Demo scenes and demo-only assets (floating island, path, clouds, sky, plinth and catalogue floor
                    materials, post-processing volume). Not counted as product models. Safe to delete.
  Documentation     This readme and the changelog

PREFABS  (naming: FMS_Garden_<Name> for a base prefab, FMS_Garden_<Name>_<Variant> for a variant)
STR Structures (7)   Arch_Wood (+ _White, _Gate), Arch_Iron, Arbor_Bench, Pergola, Pergola_Bay, Gazebo,
                     Obelisk (+ _White)
MOD Modular (9)      Lattice_Panel, Lattice_Post, Wall_Stone, Wall_Pillar, Edging_Brick, Edging_Brick_Curve,
                     Pond_Edge, Pond_Edge_Corner, Pond_Water
FLB Flower beds (3)  Bed_Straight, Bed_Corner, Bed_Round (+ _Planted of each)
WTR Water (3)        Fountain_Tiered, Fountain_Wall, Birdbath
ORN Ornaments (5)    Sundial, Gnome (+ _Blue), Urn (+ _Planted), Insect_Hotel, Shepherd_Hook (+ _Feeder)
FUR Furniture (5)    Swing, Hammock, Bistro_Table (+ _White), Bistro_Chair (+ _White), Deck_Chair (+ _Blue)
PLT Plants (6)       Rose_Bush (+ _Pink, _White), Rose_Climbing_Side (+ _Pink), Rose_Climbing_Top (+ _Pink),
                     Ivy_Patch, Wisteria_Drape, Hollyhock (+ _White)
TOP Topiary (4)      Topiary_Standard (+ _Rose), Topiary_Cone, Topiary_Spiral, Topiary_Tiered
                     60 prefabs = 42 models + 18 variants (11 colour: same mesh, other atlas cells;
                     7 mesh: added gate, flowers, feeder or roses)
CMP Compositions (6) Comp_RoseArchEntrance, Comp_PergolaTerrace, Comp_GazeboRetreat, Comp_FountainParterre,
                     Comp_WalledPondCorner, Comp_WildlifeLawn (built only from the prefabs above; they add no new
                     models; origin at the front centre)

SETUP CONTRACT
- Scale 1 unit = 1 m, Y up. The root pivot is on the ground (Y = 0) at the base centre; root scale 1, rotation 0.
- Deliberate exceptions: Lattice_Panel frame starts 0.05 m above its pivot (the posts carry it); Pond_Water slab top is
  at 0.38 m with the pivot on the ground; Wisteria_Drape has its pivot on the top face (hang it under a beam, e.g. the
  pergola beam at 2.24 m); Pond_Edge pivot is at the middle of its inner face, Pond_Edge_Corner pivot at the inner
  corner, Edging_Brick_Curve pivot at the circle centre.
- Modular grids:
    Lattice screen  Lattice_Post on the 2 m grid nodes, Lattice_Panel in the middle of each span (node + 1 m).
    Stone wall      Wall_Pillar on the 2 m grid nodes (always on corners and free ends), Wall_Stone in each span.
                    Leave one span out for a 1.5 m opening (fits Arch_Iron).
    Brick edging    Edging_Brick on 1 m cells (cell centre), Edging_Brick_Curve on a node; 4 curves = a 2 m ring.
    Formal pond     N x M cells = N*M Pond_Water + 2*(N+M) Pond_Edge + 4 Pond_Edge_Corner, all on a 1 m grid.
    Pergola         Pergola_Bay at Pergola + (1.5, 0, 0) m, every next bay + 3.0 m along X.
    Flower beds     fill whole 1 m cells (2 x 1, L 2 x 2, round 2 m); neighbouring beds touch, never overlap.
- Plant attach points: empty objects Plant_L, Plant_R, Plant_Top on Arch_Wood (+ variants), Arch_Iron and Arbor_Bench.
  Put Rose_Climbing_Side on Plant_L / Plant_R and Rose_Climbing_Top on Plant_Top.
- Separate pivoted objects (not animations): Gate_Leaf on Arch_Wood_Gate (hinge axis Y, at the viewer's left post),
  Seat on Swing (top-beam axis X), Hanging basket / feeder on Shepherd_Hook (hang point; the hook points to -X).
  Rotate them from your own code or animation clips.

MATERIALS AND ATLASES
- 2 materials, Universal Render Pipeline/Lit, opaque, smoothness 0.15, GPU instancing on. Every model uses one of them.
- Atlas A (FMS_Garden_AtlasA): structures, furniture, stone, metal, water, gnome, sundial, insect hotel.
- Atlas F (FMS_Garden_AtlasF): plants, flower beds, topiary, urn, shepherd's hook.
- Each atlas is a 4 x 4 grid of flat colour cells; every face uses one cell. Point filter, no mipmaps, uncompressed.
  Recolour a model by editing the atlas cells or by moving UVs to another cell.

LOD AND COLLIDERS
- LOD Group with LOD0 + LOD1 on 9 prefabs: Gazebo, Pergola, Pergola_Bay, Arbor_Bench, Fountain_Tiered, Swing and the
  three _Planted flower beds (LOD1 = 50-66% of LOD0). No LOD on the other prefabs.
- Triangles LOD0: 36 to 2,722 per model, 26,918 for all 42 models (47,604 for all 60 prefabs).
- NO COLLIDERS. The prefabs ship without colliders on purpose. Add a MeshCollider or primitive colliders (Box /
  Capsule) where your game needs them.

URP SETUP
- The materials use Universal Render Pipeline/Lit. The project must use a URP pipeline asset.
- The demo scenes use a URP Volume (Demo/Settings/FMS_Garden_Look) for post-processing, a gradient sky and unlit
  clouds (Demo/Shaders). Post-processing must be enabled on the URP renderer / camera to see the grade.

DEMO SCENES (3)
- Demo_CottageGarden: all six compositions and free-standing items in one garden on a floating island.
- Demo_Compositions: the 6 compositions and the 5 modular systems, each on its own island plinth.
- Demo_Catalog: all 60 prefabs in rows by category and the 6 compositions, with ID labels (TextMesh).
- Each scene has one camera (Main Camera). There is no camera controller.
- The island, path, clouds, plinths, sky and catalogue floor are demo-only: delete the Demo folder if you do not need it.

NOT INCLUDED
No scripts, colliders, rigs or animation clips. Water is opaque stylized geometry (no water shader or simulation);
plants are static meshes without wind. Blender files and build scripts are not included.

FARM SERIES
Same style, palette and scale as Farm Market, Farm Yard, Farm Nature, Farm Processing, Farm Machinery and Farm Animals.
Cottage Garden Decor repeats none of their items and works on its own.

SUPPORT
Contact us through the publisher profile on the Asset Store. Reviews are appreciated.
