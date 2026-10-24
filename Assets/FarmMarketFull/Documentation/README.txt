FARM MARKET STARTER - FULL  (v1.0.0)
Stylized low-poly farm market props: 119 single prefabs in 6 categories + 6 ready compositions, LOD0-2.

REQUIREMENTS
- Unity 6 (6000.3 or newer), Universal Render Pipeline (URP).

QUICK START
1. Open Demo/Scenes/Demo_MarketSquare.unity: a complete market square built only from pack props
   (vegetable row, fruit row, dairy corner, bakery, merchant cart, flower stand, picnic square).
2. Drag any prefab from Art/Prefabs/Single/<Category> into your scene.
3. Art/Prefabs/Compositions holds ready-made, filled market modules (FMS_Comp_*):
   VegetableRow, FruitRow, DairyFoodCorner, MerchantCartFull, MarketSquarePlaza, FloralPlanterStand.

FOLDERS
Art/Models        FBX meshes with LOD0-2, grouped by category (Veg, Fruit, Crate, Stall, Deco, Food)
Art/Materials     URP/Lit materials
Art/Textures      Base color textures
Art/Prefabs       Single props (per category) and compositions
Demo              Demo scene, ground textures, sky and post-processing profiles. Safe to delete if you do not need it.
Documentation     This file and the changelog

PREFABS
Naming: FMS_<Category>_<Name>_<Variant>; the FBX of every prefab has the same name.
Veg (17):    Tomato (whole, half, branch), Carrot, Potato, Cabbage, Corn, Pumpkin, Cucumber, Onion, Garlic,
             Peppers, Eggplant, Beet, Radish, Greens, Parsley
Fruit (8):   Apple, Pear, Watermelon, Grape, Strawberry, Lemon, Lemon Slice, Orange
Crate (32):  Produce crates (framed, slatted, wire, tilted) and fills, wicker baskets and fills,
             sacks, seed sacks & packets, eggs, milk cans
Stall (14):  Stalls (open, medium, corner, canopy), Canopy, Merchant Cart, Display Shelves, Balance Scale,
             Weights, Cash Box, Market Umbrella (red, blue, green)
Deco (31):   Signs & Chalkboards, Bunting & Lanterns, Street Lanterns, Picnic Table & Benches,
             Planters & Pots, Signposts, Barrels, Hay Bales
Food (17):   Bread & Bakery, Cheese, Milk Bottles & Bucket, Honey & Jam Jars, Meat & Fish, Cutting Board
Comp (6):    VegetableRow, FruitRow, DairyFoodCorner, FloralPlanterStand,
             MerchantCartFull, MarketSquarePlaza

NOTES
- Scale: 1 unit = 1 meter. Pivot at the base of each object.
- Every prefab has a collider and an LOD Group (LOD1 ~56%, LOD2 ~16% triangles).
- SRP Batcher and GPU Instancing compatible.
- Built for URP. For Built-in or HDRP, convert materials with the standard Unity material upgrade tools.

SUPPORT
Contact us through the publisher profile on the Asset Store. Reviews are appreciated.
