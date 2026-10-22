using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Random = System.Random;

namespace MarketFarm.Editor
{
    /// <summary>
    /// Builds Assets/Scenes/MarketHero.unity: the Farm Market Starter Lite promo diorama (see
    /// AssetStore/Lite_Reference_Concepts). Only pack prefab instances; the cobble island, grass tufts, light and post
    /// are staging and live in Assets/Scenes/Hero. Deterministic (fixed seed) and idempotent.
    /// </summary>
    public static class MarketHeroBuilder
    {
        private const string PackPrefabs = "Assets/FarmMarketStarter/Art/Prefabs";
        private const string DemoSettings = "Assets/FarmMarketStarter/Demo/Settings";
        private const string DemoTextures = "Assets/FarmMarketStarter/Demo/Textures";
        private const string HeroDir = "Assets/Scenes/Hero";
        public const string ScenePath = "Assets/Scenes/MarketHero.unity";
        public const string RootName = "Diorama";
        private const int Seed = 2026;
        private const float Top = 0.80f;   // table-top height of the pack stalls

        private static readonly Dictionary<string, GameObject> PrefabCache = new Dictionary<string, GameObject>();
        public static readonly SortedSet<string> UsedPrefabs = new SortedSet<string>();
        private static Random _rng;

        [MenuItem("Tools/MarketFarm/Build Hero Scene")]
        public static void Build()
        {
            _rng = new Random(Seed);
            PrefabCache.Clear();
            UsedPrefabs.Clear();
            AssetDatabase.DeleteAsset(HeroDir); // staging assets are rebuilt from scratch
            Directory.CreateDirectory(HeroDir);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject(RootName).transform;
            BuildIsland(root);
            BuildDiorama(root);
            BuildCardDiorama(root);
            BuildCloseupDiorama(root);
            BuildLayoutDiorama(root);
            BuildCollectionDiorama(root);
            BuildVariationsDiorama(root);
            BuildIconDiorama(root);
            BuildLighting();
            BuildCamera();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log($"[MarketHero] built {ScenePath}: {UsedPrefabs.Count} distinct pack prefabs");
        }

        // ---------- Placement ----------

        public static string[] AllPackPrefabNames() =>
            AssetDatabase.FindAssets("t:Prefab", new[] { PackPrefabs })
                .Select(g => Path.GetFileNameWithoutExtension(AssetDatabase.GUIDToAssetPath(g)))
                .OrderBy(n => n, System.StringComparer.Ordinal).ToArray();

        private static GameObject Prefab(string name)
        {
            if (PrefabCache.TryGetValue(name, out var cached)) return cached;
            var path = AssetDatabase.FindAssets($"{name} t:Prefab", new[] { PackPrefabs })
                .Select(AssetDatabase.GUIDToAssetPath)
                .First(p => Path.GetFileNameWithoutExtension(p) == name);
            return PrefabCache[name] = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        }

        private static GameObject Spawn(Transform parent, string name, Vector3 local, Vector3 euler, float scale = 1f)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Prefab(name), parent);
            go.transform.localPosition = local;
            go.transform.localRotation = Quaternion.Euler(euler);
            go.transform.localScale = Vector3.one * scale;
            UsedPrefabs.Add(name);
            return go;
        }

        private static GameObject Spawn(Transform parent, string name, Vector3 local, float yaw = 0f, float scale = 1f) =>
            Spawn(parent, name, local, new Vector3(0f, yaw, 0f), scale);

        private static float Rand(float range) => ((float)_rng.NextDouble() * 2f - 1f) * range;

        /// <summary>Stacked square layers (n x n, n-1 x n-1, ...) forming a heap; optional radius clip for round containers.</summary>
        private static void Heap(Transform parent, string model, Vector3 origin, int n, float spacing, float y0, float step,
            int layers, float maxRadius = float.MaxValue)
        {
            for (var l = 0; l < layers; l++)
            {
                var count = Mathf.Max(1, n - l);
                for (var ix = 0; ix < count; ix++)
                for (var iz = 0; iz < count; iz++)
                {
                    var ox = (ix - (count - 1) * 0.5f) * spacing + Rand(0.004f);
                    var oz = (iz - (count - 1) * 0.5f) * spacing + Rand(0.004f);
                    if (new Vector2(ox, oz).magnitude > maxRadius) continue;
                    Spawn(parent, model, origin + new Vector3(ox, y0 + l * step, oz), Rand(180f) + 180f, 1f + Rand(0.05f));
                }
            }
        }

        /// <summary>A bunch of carrots lying in a crate, leafy tops sticking out toward the viewer (-Z).</summary>
        private static void Carrots(Transform crate, float tilt = 55f)
        {
            // carrots stand in a fan: roots down in the crate, leafy ends up and out toward the viewer
            for (var i = 0; i < 7; i++)
            {
                var x = (i - 3f) * 0.055f + Rand(0.008f);
                var back = i % 2 == 0 ? 0.03f : -0.04f;
                Spawn(crate, "FMS_Veg_Carrot", new Vector3(x, 0.14f, back), new Vector3(Rand(8f), 90f + Rand(12f), tilt + Rand(8f)), 1.3f);
            }
        }

        // ---------- Scene content ----------

        private static void BuildDiorama(Transform root)
        {
            // --- The stall: canopy table, three crates of produce on the counter, tilted toward the viewer.
            var stall = new GameObject("Stall").transform;
            stall.SetParent(root, false);
            stall.localRotation = Quaternion.Euler(0f, -8f, 0f);
            Spawn(stall, "FMS_Stall_Table_Canopy", Vector3.zero);
            var carrotCrate = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(-0.50f, Top + 0.05f, 0.02f), new Vector3(-22f, 0f, 0f)).transform;
            Carrots(carrotCrate);
            var cabbageCrate = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(0.0f, Top + 0.05f, 0.02f), new Vector3(-22f, 0f, 0f)).transform;
            Heap(cabbageCrate, "FMS_Veg_Cabbage", Vector3.zero, 2, 0.145f, 0.12f, 0.12f, 2);
            var appleCrate = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(0.50f, Top + 0.05f, 0.02f), new Vector3(-22f, 0f, 0f)).transform;
            Heap(appleCrate, "FMS_Fruit_Apple", Vector3.zero, 4, 0.085f, 0.12f, 0.075f, 3);

            // --- Left, tight against the stall: a stack of tomato crates and two crates leaning on its legs.
            var lower = Spawn(root, "FMS_Crate_Framed_Open", new Vector3(-1.18f, 0f, 0.30f), 8f).transform;
            Heap(lower, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.12f, 0.07f, 3);
            var upper = Spawn(root, "FMS_Crate_Framed_Open", new Vector3(-1.18f, 0.40f, 0.30f), new Vector3(-16f, 14f, 0f)).transform;
            Heap(upper, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.12f, 0.07f, 4);

            var leanTomato = Spawn(root, "FMS_Crate_Framed_Open", new Vector3(-1.05f, 0.10f, -0.48f), new Vector3(-24f, 18f, 0f)).transform;
            Heap(leanTomato, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.12f, 0.07f, 3);
            var leanCabbage = Spawn(root, "FMS_Crate_Framed_Open", new Vector3(-0.50f, 0.10f, -0.78f), new Vector3(-24f, 4f, 0f)).transform;
            Heap(leanCabbage, "FMS_Veg_Cabbage", Vector3.zero, 2, 0.145f, 0.12f, 0.12f, 2);

            // --- Front: baskets in a row, chalkboard against the stall's right leg, scale with weights.
            Spawn(root, "FMS_Crate_Basket_Large", new Vector3(0.05f, 0f, -1.00f), 12f);
            Spawn(root, "FMS_Crate_Basket_Small", new Vector3(-0.62f, 0f, -1.38f), 40f);
            Heap(root, "FMS_Veg_Potato", new Vector3(-0.62f, 0f, -1.38f), 2, 0.07f, 0.12f, 0.07f, 2);
            Spawn(root, "FMS_Deco_Signboard_Chalk", new Vector3(0.78f, 0f, -0.72f), 180f + 8f, 1.15f);
            Spawn(root, "FMS_Stall_Scale", new Vector3(1.45f, 0f, -1.25f), 192f, 1.6f);
            Spawn(root, "FMS_Stall_Weights", new Vector3(0.98f, 0f, -1.62f), 20f, 1.4f);

            // --- Between the stall and the cart: a closed crate with a pumpkin on top.
            Spawn(root, "FMS_Crate_Framed_Closed", new Vector3(1.38f, 0f, 0.42f), 10f);
            Spawn(root, "FMS_Veg_Pumpkin", new Vector3(1.40f, 0.40f, 0.42f), 40f, 0.8f);

            // --- Right: loaded cart (wheel toward the viewer, handle toward the left), basket with apples beside it.
            var cart = new GameObject("Cart").transform;
            cart.SetParent(root, false);
            cart.localPosition = new Vector3(2.45f, 0f, 0.20f);
            cart.localRotation = Quaternion.Euler(0f, -62f, 0f);
            Spawn(cart, "FMS_Stall_Cart_Empty", Vector3.zero);
            const float bed = 0.56f; // body spans z -0.75..0.25 (the handle is at +z)
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.14f, bed, -0.52f), 12f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.16f, bed, -0.50f), -40f, 0.95f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(-0.12f, bed, -0.14f), -25f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.17f, bed, -0.10f), 50f, 0.9f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(0.0f, bed + 0.24f, -0.34f), 35f, 0.9f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(0.02f, bed + 0.22f, -0.58f), 100f, 0.85f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.08f, bed + 0.26f, -0.30f), -30f, 0.85f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.10f, bed + 0.30f, -0.12f), 70f, 0.8f);

            Spawn(root, "FMS_Crate_Basket_Large", new Vector3(3.15f, 0f, -0.70f), -15f);
            Heap(root, "FMS_Fruit_Apple", new Vector3(3.15f, 0f, -0.70f), 3, 0.1f, 0.2f, 0.08f, 3, 0.14f);
            Spawn(root, "FMS_Veg_Pumpkin", new Vector3(2.05f, 0f, -0.55f), 30f, 0.85f);
            Spawn(root, "FMS_Fruit_Watermelon", new Vector3(2.45f, 0f, -1.25f), -20f, 0.8f);
            Spawn(root, "FMS_Fruit_Apple", new Vector3(-0.15f, 0f, -0.55f), 0f);
            Spawn(root, "FMS_Fruit_Apple", new Vector3(0.00f, 0f, -0.45f), 40f, 0.95f);
        }

        // ---------- 02 Store card: one stall, shown from the front, packed with produce ----------

        public static readonly Vector3 CardOrigin = new Vector3(100f, 0f, 0f);

        /// <summary>Carrots standing in a round basket, roots down, leafy ends fanning out and up.</summary>
        private static void CarrotsInBasket(Transform basket)
        {
            for (var i = 0; i < 9; i++)
            {
                var a = i * 40f + Rand(8f);
                var r = i < 8 ? 0.09f : 0.0f;
                var pos = new Vector3(Mathf.Cos(a * Mathf.Deg2Rad) * r, 0.33f + (i == 8 ? 0.04f : 0f), Mathf.Sin(a * Mathf.Deg2Rad) * r);
                Spawn(basket, "FMS_Veg_Carrot", pos, new Vector3(0f, -a, 62f + Rand(6f)), 1.5f);
            }
        }

        private static void BuildCardDiorama(Transform root)
        {
            var card = new GameObject("Card").transform;
            card.SetParent(root, false);
            card.localPosition = CardOrigin;

            // thin cobble patch under the group, like the reference
            var cobble = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Cobble.mat");
            var earth = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Earth.mat");
            var center = new Vector3(0.35f, 0f, -0.35f);
            Slab(card, "Earth", center + new Vector3(0f, -0.07f, 0f), new Vector3(4.4f, 0.12f, 2.3f), earth); // hidden under the cobble: no dark rim on the card
            Slab(card, "Cobble", center + new Vector3(0f, 0.005f, 0f), new Vector3(4.8f, 0.03f, 2.6f), cobble);
            var tufts = new[]
            {
                new Vector3(-1.9f, 0f, -0.9f), new Vector3(-1.2f, 0f, -1.35f), new Vector3(0.3f, 0f, -1.7f), new Vector3(1.4f, 0f, -1.5f),
                new Vector3(2.0f, 0f, -0.2f), new Vector3(-1.9f, 0f, 0.35f), new Vector3(0.7f, 0f, 0.55f)
            };
            var go = new GameObject("Grass_Tufts");
            go.transform.SetParent(card, false);
            go.AddComponent<MeshFilter>().sharedMesh = TuftMesh("Card_Tufts", tufts);
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>($"{DemoSettings}/M_Demo_Grass_1.mat");
            mr.shadowCastingMode = ShadowCastingMode.Off;

            // --- stall, facing the viewer; the counter holds a crate of cabbages, a basket of carrots and the scale
            Spawn(card, "FMS_Stall_Table_Canopy", Vector3.zero, -6f);
            var cab = Spawn(card, "FMS_Crate_Slatted_Empty", new Vector3(-0.50f, Top, 0.02f), 0f).transform;
            Spawn(cab, "FMS_Veg_Cabbage", new Vector3(-0.10f, 0.17f, 0f), 20f);
            Spawn(cab, "FMS_Veg_Cabbage", new Vector3(0.10f, 0.17f, 0f), -40f);
            Spawn(cab, "FMS_Veg_Cabbage", new Vector3(0f, 0.30f, 0f), 80f, 0.95f);
            var topBasket = Spawn(card, "FMS_Crate_Basket_Large", new Vector3(-0.06f, Top, 0.02f), 10f).transform;
            CarrotsInBasket(topBasket);
            Spawn(card, "FMS_Stall_Scale", new Vector3(0.50f, Top, 0.0f), 0f, 1.35f);
            Spawn(card, "FMS_Stall_Weights", new Vector3(0.22f, Top, -0.1f), 25f, 1.2f);

            // --- left: two crates of pumpkins stacked, two crates of tomatoes stacked in front of them
            var pumpLow = Spawn(card, "FMS_Crate_Framed_Open", new Vector3(-1.05f, 0f, -0.42f), 5f).transform;
            Spawn(pumpLow, "FMS_Veg_Pumpkin", new Vector3(-0.05f, 0.26f, -0.04f), 20f, 0.7f);
            Spawn(pumpLow, "FMS_Veg_Pumpkin", new Vector3(0.07f, 0.24f, 0.08f), -35f, 0.5f);
            var pumpHigh = Spawn(card, "FMS_Crate_Framed_Open", new Vector3(-1.05f, 0.40f, -0.40f), new Vector3(-14f, -4f, 0f)).transform;
            Spawn(pumpHigh, "FMS_Veg_Pumpkin", new Vector3(-0.05f, 0.28f, -0.04f), 60f, 0.72f);
            Spawn(pumpHigh, "FMS_Veg_Pumpkin", new Vector3(0.07f, 0.26f, 0.08f), 10f, 0.5f);

            var tomLow = Spawn(card, "FMS_Crate_Framed_Open", new Vector3(-0.45f, 0f, -0.72f), -6f).transform;
            Heap(tomLow, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.18f, 0.07f, 3);
            var tomHigh = Spawn(card, "FMS_Crate_Framed_Open", new Vector3(-0.45f, 0.40f, -0.64f), new Vector3(-16f, 4f, 0f)).transform;
            Heap(tomHigh, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.18f, 0.07f, 4);

            // --- centre front: a basket of carrots
            var carrotBasket = Spawn(card, "FMS_Crate_Basket_Large", new Vector3(0.25f, 0f, -0.78f), -8f, 1.15f).transform;
            CarrotsInBasket(carrotBasket);

            // --- right front: a wide crate of watermelons
            var melonCrate = Spawn(card, "FMS_Crate_Slatted_Empty", new Vector3(1.02f, 0f, -0.55f), 4f, 1.45f).transform;
            Spawn(melonCrate, "FMS_Fruit_Watermelon", new Vector3(-0.08f, 0.14f, 0.02f), -20f, 0.95f);
            Spawn(melonCrate, "FMS_Fruit_Watermelon", new Vector3(0.11f, 0.15f, -0.02f), 150f, 0.85f);

            // --- chalkboard against the stall's right leg
            Spawn(card, "FMS_Deco_Signboard_Chalk", new Vector3(1.78f, 0f, -0.42f), 180f + 10f, 1.25f);
            Spawn(card, "FMS_Fruit_Apple", new Vector3(1.45f, 0f, -1.0f), 20f);
        }

        // ---------- 03 Detail close-up: loaded cart in front, crates leaning on it, blurred stall behind ----------

        public static readonly Vector3 CloseupOrigin = new Vector3(300f, 0f, 0f);

        private static void BuildCloseupDiorama(Transform root)
        {
            var g = new GameObject("Closeup").transform;
            g.SetParent(root, false);
            g.localPosition = CloseupOrigin;

            // a wide cobble floor with bigger stones than the island, running out to the background
            var floor = StageMaterial("M_Hero_CobbleBig", "T_Demo_Cobble", new Vector2(13f, 10f), 0.08f, new Color(0.9f, 0.8f, 0.7f));
            Slab(g, "Floor", new Vector3(0f, 0.005f, 3f), new Vector3(18f, 0.03f, 14f), floor);

            // --- the cart: its +x side (with the wheel) faces the camera, the handle points to the right and forward
            var cart = new GameObject("Cart").transform;
            cart.SetParent(g, false);
            cart.localPosition = new Vector3(-0.30f, 0f, 0.45f);
            cart.localRotation = Quaternion.Euler(0f, 128f, 0f);
            Spawn(cart, "FMS_Stall_Cart_Empty", Vector3.zero);
            const float bed = 0.56f;
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.10f, bed, -0.30f), 95f, 1.0f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.10f, bed, -0.04f), 80f, 1.0f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.08f, bed + 0.02f, -0.62f), 30f, 0.85f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.02f, bed + 0.28f, -0.16f), 100f, 0.95f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.07f, bed + 0.26f, 0.07f), 75f, 0.9f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(-0.08f, bed + 0.26f, -0.58f), 70f, 1.0f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(0.02f, bed + 0.36f, -0.38f), 10f, 1.0f);

            // --- in front of the cart, on the ground: a tomato crate leaning on the cart's front, a carrot crate next to it, a basket of apples
            var tomato = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(0.55f, 0.07f, -0.15f), new Vector3(-22f, 24f, 0f), 0.9f).transform;
            Heap(tomato, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.14f, 0.07f, 3);
            var carrot = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(1.0f, 0.05f, 0.0f), new Vector3(-20f, 10f, 0f), 0.9f).transform;
            CarrotsInBasket(carrot);
            var basket = Spawn(g, "FMS_Crate_Basket_Large", new Vector3(1.6f, 0f, 0.1f), -12f, 1.0f).transform;
            Heap(basket, "FMS_Fruit_Apple", Vector3.zero, 3, 0.1f, 0.22f, 0.08f, 3, 0.14f);

            // --- background, out of focus: two stalls with crates and baskets on the counters
            var back = new GameObject("Background").transform;
            back.SetParent(g, false);
            var stallA = Spawn(back, "FMS_Stall_Table_Canopy", new Vector3(1.5f, 0f, 2.0f), -4f).transform;
            var crateA = Spawn(back, "FMS_Crate_Framed_Open", new Vector3(1.1f, Top, 2.0f), new Vector3(-14f, 0f, 0f)).transform;
            Heap(crateA, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.14f, 0.07f, 3);
            Spawn(back, "FMS_Crate_Basket_Large", new Vector3(1.8f, Top, 2.0f), 0f);
            Spawn(back, "FMS_Crate_Basket_Small", new Vector3(2.2f, Top, 1.95f), 20f);
            var stallB = Spawn(back, "FMS_Stall_Table_Canopy", new Vector3(-2.2f, 0f, 2.6f), 6f).transform;
            Spawn(back, "FMS_Crate_Basket_Large", new Vector3(-2.4f, Top, 2.6f), 0f);
            Spawn(back, "FMS_Crate_Basket_Small", new Vector3(-1.85f, Top, 2.55f), 0f);
        }

        // ---------- 04 Stall layout: the whole stall on one plate, cart on the left, baskets and chalkboard on the right ----------

        public static readonly Vector3 LayoutOrigin = new Vector3(500f, 0f, 0f);

        private static void TomatoBasket(Transform parent, Vector3 pos, float yaw)
        {
            var b = Spawn(parent, "FMS_Crate_Basket_Large", pos, yaw).transform;
            Heap(b, "FMS_Veg_Tomato_Whole", Vector3.zero, 3, 0.085f, 0.2f, 0.07f, 3, 0.15f);
        }

        private static void BuildLayoutDiorama(Transform root)
        {
            var g = new GameObject("Layout").transform;
            g.SetParent(root, false);
            g.localPosition = LayoutOrigin;

            var cobble = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Cobble.mat");
            var earth = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Earth.mat");
            var center = new Vector3(0.15f, 0f, -0.25f);
            Slab(g, "Earth", center + new Vector3(0f, -0.07f, 0f), new Vector3(5.5f, 0.14f, 3.6f), earth);
            Slab(g, "Cobble", center + new Vector3(0f, 0.005f, 0f), new Vector3(5.2f, 0.03f, 3.3f), cobble);
            var tufts = new[]
            {
                new Vector3(-2.3f, 0f, -0.8f), new Vector3(-1.9f, 0f, 1.2f), new Vector3(0.9f, 0f, -1.5f), new Vector3(2.4f, 0f, -0.7f),
                new Vector3(2.35f, 0f, 1.0f), new Vector3(-0.8f, 0f, -1.4f)
            };
            var go = new GameObject("Grass_Tufts");
            go.transform.SetParent(g, false);
            go.AddComponent<MeshFilter>().sharedMesh = TuftMesh("Layout_Tufts", tufts);
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>($"{DemoSettings}/M_Demo_Grass_1.mat");
            mr.shadowCastingMode = ShadowCastingMode.Off;

            // --- the stall: basket of tomatoes and potatoes plus the scale on the counter; pumpkin and cabbage crates underneath
            var stall = new GameObject("Stall").transform;
            stall.SetParent(g, false);
            stall.localPosition = new Vector3(0.35f, 0f, 0.5f);
            stall.localRotation = Quaternion.Euler(0f, -8f, 0f);
            Spawn(stall, "FMS_Stall_Table_Canopy", Vector3.zero);
            var counter = Spawn(stall, "FMS_Crate_Basket_Large", new Vector3(-0.30f, Top, 0.02f), 10f, 1.1f).transform;
            Heap(counter, "FMS_Veg_Tomato_Whole", new Vector3(-0.03f, 0f, 0f), 3, 0.085f, 0.2f, 0.07f, 3, 0.15f);
            Spawn(counter, "FMS_Veg_Potato", new Vector3(0.07f, 0.34f, 0.06f), 30f);
            Spawn(counter, "FMS_Veg_Potato", new Vector3(0.10f, 0.33f, -0.02f), 110f);
            Spawn(stall, "FMS_Stall_Scale", new Vector3(0.45f, Top, 0f), 0f, 1.35f);
            Spawn(stall, "FMS_Stall_Weights", new Vector3(0.12f, Top, -0.1f), 25f, 1.2f);

            var pump = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(-0.62f, 0.02f, -0.12f), 4f).transform;
            Spawn(pump, "FMS_Veg_Pumpkin", new Vector3(-0.05f, 0.26f, -0.04f), 20f, 0.7f);
            Spawn(pump, "FMS_Veg_Pumpkin", new Vector3(0.07f, 0.24f, 0.08f), -35f, 0.5f);
            var pump2 = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(-0.12f, 0.02f, -0.18f), new Vector3(-8f, -6f, 0f)).transform;
            Spawn(pump2, "FMS_Veg_Pumpkin", new Vector3(-0.05f, 0.28f, -0.04f), 60f, 0.72f);
            Spawn(pump2, "FMS_Veg_Pumpkin", new Vector3(0.07f, 0.26f, 0.08f), 10f, 0.5f);
            var cab = Spawn(stall, "FMS_Crate_Framed_Open", new Vector3(0.44f, 0.02f, -0.2f), new Vector3(-10f, 6f, 0f)).transform;
            Heap(cab, "FMS_Veg_Cabbage", Vector3.zero, 2, 0.145f, 0.17f, 0.13f, 2);

            // --- cart on the left, wheel toward the viewer, handle to the right; watermelons and a crate of carrots
            var cart = new GameObject("Cart").transform;
            cart.SetParent(g, false);
            cart.localPosition = new Vector3(-1.55f, 0f, 0.3f);
            cart.localRotation = Quaternion.Euler(0f, 128f, 0f);
            Spawn(cart, "FMS_Stall_Cart_Empty", Vector3.zero);
            const float bed = 0.56f;
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.10f, bed, -0.32f), 95f, 1.0f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(0.10f, bed, -0.10f), 80f, 0.95f);
            Spawn(cart, "FMS_Fruit_Watermelon", new Vector3(-0.02f, bed + 0.28f, -0.20f), 100f, 0.9f);
            // pumpkins fill the rest of the bed so the cart reads as a full load
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(-0.26f, bed, -0.05f), 20f, 0.85f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(0.24f, bed, -0.33f), -30f, 0.75f);
            Spawn(cart, "FMS_Veg_Pumpkin", new Vector3(0.22f, bed + 0.24f, -0.12f), 70f, 0.7f);
            var cartCarrots = Spawn(cart, "FMS_Crate_Slatted_Empty", new Vector3(0f, bed, -0.60f), 90f, 0.8f).transform;
            CarrotsInBasket(cartCarrots);

            // --- two crates of apples leaning forward from the cart
            var applesA = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(-0.85f, 0.08f, -0.50f), new Vector3(-24f, 20f, 0f)).transform;
            Heap(applesA, "FMS_Fruit_Apple", Vector3.zero, 4, 0.085f, 0.14f, 0.075f, 3);
            var applesB = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(-0.38f, 0.04f, -0.88f), new Vector3(-30f, 8f, 0f)).transform;
            Heap(applesB, "FMS_Fruit_Apple", Vector3.zero, 4, 0.085f, 0.14f, 0.075f, 3);

            // --- right: chalkboard against the stall's leg and three baskets
            Spawn(g, "FMS_Deco_Signboard_Chalk", new Vector3(1.78f, 0f, 0.30f), 180f + 8f, 1.25f);
            var apples = Spawn(g, "FMS_Crate_Basket_Large", new Vector3(1.55f, 0f, -0.72f), 0f).transform;
            Heap(apples, "FMS_Fruit_Apple", Vector3.zero, 3, 0.1f, 0.22f, 0.08f, 3, 0.14f);
            TomatoBasket(g, new Vector3(2.12f, 0f, -0.55f), 30f);
            TomatoBasket(g, new Vector3(1.85f, 0f, -1.12f), -20f);
        }


        // ---------- 05 / 07: catalogue boards (every Lite prefab laid out; small produce is scaled up for display) ----------

        public static readonly Vector3 CollectionOrigin = new Vector3(700f, 0f, 0f);
        public static readonly Vector3 VariationsOrigin = new Vector3(900f, 0f, 0f);
        private const float DisplayScale = 3.0f;

        private static Transform CatalogueBase(Transform root, string name, Vector3 origin)
        {
            var g = new GameObject(name).transform;
            g.SetParent(root, false);
            g.localPosition = origin;
            var cobble = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Cobble.mat");
            var earth = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Earth.mat");
            Slab(g, "Earth", new Vector3(0f, -0.07f, -0.2f), new Vector3(12.4f, 0.12f, 5.4f), earth);
            Slab(g, "Cobble", new Vector3(0f, 0.005f, -0.2f), new Vector3(12.8f, 0.03f, 5.8f), cobble);
            return g;
        }

        private static void BuildCollectionDiorama(Transform root)
        {
            var g = CatalogueBase(root, "Collection", CollectionOrigin);
            // back row: stalls, the ready-made stand, cart, chalkboard
            Spawn(g, "FMS_Stall_Table_Canopy", new Vector3(-4.2f, 0f, 1.3f), -4f);
            Spawn(g, "FMS_Stall_Table_Open", new Vector3(-2.2f, 0f, 1.3f), 3f);
            Spawn(g, "FMS_Comp_VegetableStand", new Vector3(0.3f, 0f, 1.3f), 0f);
            Spawn(g, "FMS_Stall_Cart_Empty", new Vector3(3.0f, 0f, 1.2f), 128f);
            Spawn(g, "FMS_Deco_Signboard_Chalk", new Vector3(4.9f, 0f, 1.3f), 188f, 1.25f);
            // middle row: scale, weights, crates, baskets, hanging signs
            Spawn(g, "FMS_Stall_Scale", new Vector3(-4.6f, 0f, -0.1f), 0f, 1.35f);
            Spawn(g, "FMS_Stall_Weights", new Vector3(-3.8f, 0f, -0.1f), 25f, 1.8f);
            Spawn(g, "FMS_Crate_Framed_Open", new Vector3(-2.7f, 0f, -0.1f), 5f, 1.1f);
            Spawn(g, "FMS_Crate_Framed_Closed", new Vector3(-1.7f, 0f, -0.1f), -4f, 1.1f);
            Spawn(g, "FMS_Crate_Slatted_Empty", new Vector3(-0.5f, 0f, -0.1f), 3f, 1.1f);
            Spawn(g, "FMS_Crate_Basket_Large", new Vector3(0.7f, 0f, -0.1f), 10f, 1.1f);
            Spawn(g, "FMS_Crate_Basket_Small", new Vector3(1.7f, 0f, -0.1f), -8f, 1.1f);
            Spawn(g, "FMS_Deco_Signs_Hanging", new Vector3(3.6f, 0f, -0.1f), 180f);
            // front row: all produce
            var names = new[]
            {
                "FMS_Veg_Tomato_Whole", "FMS_Veg_Tomato_Half", "FMS_Veg_Tomato_Branch", "FMS_Veg_Carrot", "FMS_Veg_Potato",
                "FMS_Veg_Cabbage", "FMS_Veg_Pumpkin", "FMS_Fruit_Apple", "FMS_Fruit_Watermelon"
            };
            for (var i = 0; i < names.Length; i++)
                Spawn(g, names[i], new Vector3(-4.6f + i * 1.15f, 0f, -1.5f), 20f + i * 37f, DisplayScale);
        }

        private static void BuildVariationsDiorama(Transform root)
        {
            var g = CatalogueBase(root, "Variations", VariationsOrigin);
            // back row: produce and its variants (scaled up for display)
            var back = new (string name, float scale)[]
            {
                ("FMS_Veg_Tomato_Whole", DisplayScale), ("FMS_Veg_Tomato_Half", DisplayScale), ("FMS_Veg_Tomato_Branch", DisplayScale),
                ("FMS_Veg_Pumpkin", 1.6f), ("FMS_Veg_Pumpkin", 2.3f), ("FMS_Veg_Pumpkin", 3.1f),
                ("FMS_Fruit_Watermelon", 2.4f), ("FMS_Fruit_Apple", DisplayScale), ("FMS_Veg_Carrot", DisplayScale)
            };
            for (var i = 0; i < back.Length; i++)
                Spawn(g, back[i].name, new Vector3(-4.6f + i * 1.15f, 0f, 1.1f), 15f + i * 41f, back[i].scale);
            // middle row: containers, filled
            var open = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(-4.0f, 0f, -0.5f), 4f, 1.25f).transform;
            Heap(open, "FMS_Veg_Tomato_Whole", Vector3.zero, 4, 0.085f, 0.18f, 0.07f, 3);
            var closed = Spawn(g, "FMS_Crate_Framed_Closed", new Vector3(-2.3f, 0f, -0.5f), -3f, 1.25f);
            var slat = Spawn(g, "FMS_Crate_Slatted_Empty", new Vector3(-0.4f, 0f, -0.5f), 2f, 1.45f).transform;
            Spawn(slat, "FMS_Fruit_Watermelon", new Vector3(-0.08f, 0.14f, 0.02f), -20f, 0.95f);
            Spawn(slat, "FMS_Fruit_Watermelon", new Vector3(0.11f, 0.15f, -0.02f), 150f, 0.85f);
            var basketL = Spawn(g, "FMS_Crate_Basket_Large", new Vector3(1.5f, 0f, -0.5f), 8f, 1.3f).transform;
            Heap(basketL, "FMS_Fruit_Apple", Vector3.zero, 3, 0.1f, 0.22f, 0.08f, 3, 0.14f);
            var basketS = Spawn(g, "FMS_Crate_Basket_Small", new Vector3(3.0f, 0f, -0.5f), -8f, 1.3f).transform;
            CarrotsInBasket(basketS);
            // front row: the same containers empty
            Spawn(g, "FMS_Crate_Framed_Open", new Vector3(-3.6f, 0f, -2.0f), 6f, 1.25f);
            Spawn(g, "FMS_Crate_Framed_Closed", new Vector3(-1.9f, 0f, -2.0f), 3f, 1.25f);
            Spawn(g, "FMS_Crate_Slatted_Empty", new Vector3(0.1f, 0f, -2.0f), -2f, 1.45f);
            Spawn(g, "FMS_Crate_Basket_Large", new Vector3(1.9f, 0f, -2.0f), 8f, 1.3f);
            Spawn(g, "FMS_Crate_Basket_Small", new Vector3(3.2f, 0f, -2.0f), -8f, 1.3f);
        }


        // ---------- 01 Icon: one crate heaped with tomatoes ----------

        public static readonly Vector3 IconOrigin = new Vector3(1100f, 0f, 0f);

        private static void BuildIconDiorama(Transform root)
        {
            var g = new GameObject("Icon").transform;
            g.SetParent(root, false);
            g.localPosition = IconOrigin;
            var cobble = AssetDatabase.LoadAssetAtPath<Material>($"{HeroDir}/M_Hero_Cobble.mat");
            Slab(g, "Cobble", new Vector3(0f, 0.005f, 0f), new Vector3(2.4f, 0.03f, 2.4f), cobble);
            var crate = Spawn(g, "FMS_Crate_Framed_Open", new Vector3(0f, 0.01f, 0f), new Vector3(0f, -18f, 0f), 1.25f).transform;
            Heap(crate, "FMS_Veg_Tomato_Whole", Vector3.zero, 5, 0.09f, 0.17f, 0.075f, 3);
            Spawn(g, "FMS_Veg_Tomato_Branch", new Vector3(0.25f, 0.01f, -0.38f), 25f, 2.2f);
            Spawn(g, "FMS_Veg_Tomato_Whole", new Vector3(-0.28f, 0.01f, -0.40f), 40f, 2.6f);
            Spawn(g, "FMS_Veg_Tomato_Half", new Vector3(-0.05f, 0.01f, -0.47f), 160f, 2.6f);
        }

        // ---------- Cobble island (staging, not part of the pack) ----------

        private static Material StageMaterial(string name, string texName, Vector2 tiling, float smoothness, Color color)
        {
            var path = $"{HeroDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", texName == null ? null : AssetDatabase.LoadAssetAtPath<Texture2D>($"{DemoTextures}/{texName}.png"));
            mat.SetTextureScale("_BaseMap", tiling);
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", smoothness);
            mat.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static void BuildIsland(Transform root)
        {
            var island = new GameObject("Island").transform;
            island.SetParent(root, false);
            var cobble = StageMaterial("M_Hero_Cobble", "T_Demo_Cobble", new Vector2(6f, 4.5f), 0.1f, new Color(0.88f, 0.86f, 0.84f));
            var earth = StageMaterial("M_Hero_Earth", "T_Demo_Dirt", new Vector2(2f, 1f), 0f, new Color(0.85f, 0.7f, 0.5f));

            var center = new Vector3(0.85f, 0f, -0.45f);
            Slab(island, "Earth", center + new Vector3(0f, -0.12f, 0f), new Vector3(7.7f, 0.24f, 5.4f), earth);
            Slab(island, "Cobble", center + new Vector3(0f, 0.005f, 0f), new Vector3(7.2f, 0.03f, 4.9f), cobble);

            // a few grass tufts on the rim
            var grassMat = AssetDatabase.LoadAssetAtPath<Material>($"{DemoSettings}/M_Demo_Grass_1.mat");
            var tufts = new[]
            {
                new Vector3(-2.2f, 0f, 0.55f), new Vector3(-2.35f, 0f, -1.35f), new Vector3(3.9f, 0f, -1.1f), new Vector3(3.8f, 0f, 0.45f),
                new Vector3(0.9f, 0f, -2.6f), new Vector3(2.6f, 0f, 1.3f), new Vector3(-1.0f, 0f, -2.2f), new Vector3(0.1f, 0f, 1.55f),
                new Vector3(-0.55f, 0f, 0.7f), new Vector3(1.0f, 0f, 0.15f)
            };
            var go = new GameObject("Grass_Tufts");
            go.transform.SetParent(island, false);
            go.AddComponent<MeshFilter>().sharedMesh = TuftMesh("Hero_Tufts", tufts);
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = grassMat;
            mr.shadowCastingMode = ShadowCastingMode.Off;
        }

        private static void Slab(Transform parent, string name, Vector3 pos, Vector3 size, Material mat)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = name;
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos;
            go.transform.localScale = new Vector3(size.x, size.y * 0.5f, size.z); // cylinder is 2 m tall
            go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        }

        private static Mesh TuftMesh(string name, IEnumerable<Vector3> positions)
        {
            var verts = new List<Vector3>();
            var tris = new List<int>();
            var uvs = new List<Vector2>();
            foreach (var p in positions)
            for (var b = 0; b < 7; b++)
            {
                var yaw = (float)_rng.NextDouble() * Mathf.PI * 2f;
                var h = 0.18f + (float)_rng.NextDouble() * 0.2f;
                var dir = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));
                var side = new Vector3(Mathf.Cos(yaw), 0f, -Mathf.Sin(yaw));
                var o = p + new Vector3(((float)_rng.NextDouble() - 0.5f) * 0.2f, 0f, ((float)_rng.NextDouble() - 0.5f) * 0.2f);
                var s = verts.Count;
                verts.Add(o - side * 0.045f);
                verts.Add(o + side * 0.045f);
                verts.Add(o + Vector3.up * h + dir * 0.08f);
                uvs.Add(Vector2.zero); uvs.Add(Vector2.right); uvs.Add(new Vector2(0.5f, 1f));
                tris.AddRange(new[] { s, s + 2, s + 1, s, s + 1, s + 2 }); // double-sided
            }
            var mesh = new Mesh { name = name };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.SetNormals(new List<Vector3>(System.Linq.Enumerable.Repeat(Vector3.up, verts.Count)));
            mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh, $"{HeroDir}/{mesh.name}.asset");
            return mesh;
        }

        // ---------- Light, sky, post (values from README_Lite_Composition_Guide.md) ----------

        private static void BuildLighting()
        {
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color32(0xFF, 0xF2, 0xDF, 0xFF);
            sun.intensity = 1.85f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.9f;
            sun.shadowBias = 0.5f;
            sun.shadowNormalBias = 0.6f;
            sun.transform.rotation = Quaternion.Euler(40f, 38f, 0f);
            RenderSettings.sun = sun;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color32(0xA8, 0xD0, 0xE6, 0xFF);
            RenderSettings.ambientEquatorColor = new Color32(0xE8, 0xC5, 0xA5, 0xFF);
            RenderSettings.ambientGroundColor = new Color32(0x8C, 0x73, 0x55, 0xFF);
            RenderSettings.fog = false;

            // cool fill from the opposite side (no shadows) so shadowed wood stays colourful instead of grey
            var fill = new GameObject("Fill").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.72f, 0.82f, 1f);
            fill.intensity = 0.35f;
            fill.shadows = LightShadows.None;
            fill.transform.rotation = Quaternion.Euler(28f, 215f, 0f);

            CreateVolume("Post_Global", GradeProfile(), 1f);
            CreateVolume("Post_DoF", DofProfile(), 0f);
        }

        private static void CreateVolume(string name, VolumeProfile profile, float weight)
        {
            var v = new GameObject(name).AddComponent<Volume>();
            v.isGlobal = true;
            v.weight = weight;
            v.sharedProfile = profile;
        }

        private static VolumeProfile NewProfile(string name)
        {
            var p = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(p, $"{HeroDir}/{name}.asset");
            return p;
        }

        private static void Save(VolumeProfile p)
        {
            foreach (var c in p.components) AssetDatabase.AddObjectToAsset(c, p);
            EditorUtility.SetDirty(p);
        }

        private static VolumeProfile GradeProfile()
        {
            var p = NewProfile("VP_Hero_Grade");
            p.Add<Tonemapping>().mode.Override(TonemappingMode.Neutral);
            var bloom = p.Add<Bloom>();
            bloom.threshold.Override(0.95f);
            bloom.intensity.Override(0.22f);
            bloom.scatter.Override(0.7f);
            var color = p.Add<ColorAdjustments>();
            color.postExposure.Override(0.15f);
            color.contrast.Override(12f);
            color.saturation.Override(20f);
            p.Add<WhiteBalance>().temperature.Override(7f);
            var vig = p.Add<Vignette>();
            vig.intensity.Override(0.17f);
            vig.smoothness.Override(0.5f);
            Save(p);
            return p;
        }

        private static VolumeProfile DofProfile()
        {
            var p = NewProfile("VP_Hero_DoF");
            var dof = p.Add<DepthOfField>();
            dof.mode.Override(DepthOfFieldMode.Bokeh);
            dof.focusDistance.Override(3f);
            dof.focalLength.Override(85f);
            dof.aperture.Override(1.4f);
            Save(p);
            return p;
        }

        private static void BuildCamera()
        {
            var go = new GameObject("Hero Camera") { tag = "MainCamera" };
            var cam = go.AddComponent<Camera>();
            cam.fieldOfView = 27.5f;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 100f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.99f, 0.89f, 0.77f);
            go.AddComponent<AudioListener>();
            var data = go.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            go.transform.position = new Vector3(-3.4f, 4.4f, -6.6f);
            go.transform.LookAt(new Vector3(0.85f, 0.85f, -0.3f));
        }
    }
}
