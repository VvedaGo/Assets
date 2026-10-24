using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using MarketFarm.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Random = System.Random;

namespace FarmMarketStarter.Editor
{
    /// <summary>
    /// Builds the Farm Market Full showcase: the market square (5 zones, S-shaped cobble path), the six FMS_Comp_* prefabs,
    /// light/sky/post and a set of shot cameras. Items are dropped onto real geometry with temporary mesh colliders,
    /// so produce lands on table tops, in crates and on each other. Deterministic (fixed seed), idempotent.
    /// </summary>
    public static class FMS_FullSceneBuilder
    {
        private const string Root = "Assets/FarmMarketFull";
        private const string SingleDir = Root + "/Art/Prefabs/Single";
        private const string CompositionDir = Root + "/Art/Prefabs/Compositions";
        private const string SettingsDir = Root + "/Demo/Settings";
        private const string TextureDir = Root + "/Demo/Textures";
        private const string MeshDir = Root + "/Demo/Meshes";
        public const string ScenePath = Root + "/Demo/Scenes/Demo_MarketSquare.unity";
        private const int Seed = 2026;

        private static readonly Dictionary<string, GameObject> Prefabs = new Dictionary<string, GameObject>();
        private static readonly SortedSet<string> Used = new SortedSet<string>();
        private static readonly List<Collider> TempColliders = new List<Collider>();
        private static readonly List<GameObject> TempObjects = new List<GameObject>();
        private static readonly List<BoxCollider> DisabledBoxes = new List<BoxCollider>();
        private static readonly List<Transform> Compositions = new List<Transform>();
        private static readonly List<Vector3> LampPoints = new List<Vector3>();
        private static Random _rng;
        private static Transform _studio;

        [MenuItem("Tools/Farm Market Full/Build Market Square Scene")]
        public static string Build()
        {
            _rng = new Random(Seed);
            Prefabs.Clear(); Used.Clear(); TempColliders.Clear(); TempObjects.Clear(); DisabledBoxes.Clear();
            Compositions.Clear(); LampPoints.Clear();
            foreach (var dir in new[] { CompositionDir, SettingsDir, TextureDir, MeshDir, Path.GetDirectoryName(ScenePath) })
                Directory.CreateDirectory(dir);
            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { SingleDir }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                Prefabs[Path.GetFileNameWithoutExtension(path)] = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            }

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            BuildLook();
            var env = new GameObject("Environment (demo only, not in pack)").transform;
            BuildGround(env);

            var market = new GameObject("Market").transform;
            VegetableRow(Composition(market, "FMS_Comp_VegetableRow", new Vector3(-3.45f, 0f, 3.75f), 4f));
            FruitRow(Composition(market, "FMS_Comp_FruitRow", new Vector3(0.95f, 0f, 4.0f), -4f));
            DairyFoodCorner(Composition(market, "FMS_Comp_DairyFoodCorner", new Vector3(5.35f, 0f, 3.35f), 0f));
            MerchantCartFull(Composition(market, "FMS_Comp_MerchantCartFull", new Vector3(-4.9f, 0f, -0.3f), 32f));
            MarketSquarePlaza(Composition(market, "FMS_Comp_MarketSquarePlaza", new Vector3(0.25f, 0f, -0.3f), 0f));
            FloralPlanterStand(Composition(market, "FMS_Comp_FloralPlanterStand", new Vector3(3.35f, 0f, -4.95f), 0f));
            Bakery(Group(market, "Zone_Bakery", new Vector3(6.05f, 0f, -0.85f), 90f));
            Unloading(Group(market, "Zone_Unloading", new Vector3(-4.7f, 0f, -4.7f), 20f));
            FrontStall(Group(market, "Zone_FrontStall", new Vector3(-2.75f, 0f, -3.4f), 35f));
            UmbrellaDisplay(Group(market, "Zone_UmbrellaDisplay", new Vector3(-6.4f, 0f, 2.4f), 40f));
            TentDisplay(Group(market, "Zone_TentDisplay", new Vector3(3.05f, 0f, 1.35f), -55f));
            PathDressing(Group(market, "Path_Dressing", Vector3.zero, 0f));
            Outskirts(Group(market, "Outskirts", Vector3.zero, 0f));
            Fillers(Group(market, "Fillers", Vector3.zero, 0f));

            var studio = _studio = new GameObject("Studio (catalogue and promo stages, demo only)").transform;
            Catalogue(Group(studio, "Catalogue", CatalogueOrigin, 0f));
            StallLineup(Group(studio, "Stalls_Lineup", StallsOrigin, 0f));
            IconStage(Group(studio, "Icon_Stage", IconOrigin, 0f));
            FoodStage(Group(studio, "Food_Stage", FoodOrigin, 0f));

            BuildLamps(market);
            Cleanup();
            SaveCompositions();
            CompositionLineup();
            BuildShotCameras();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            var missing = Prefabs.Keys.Where(k => !Used.Contains(k)).OrderBy(k => k).ToList();
            var report = $"[FarmMarketFull] {ScenePath}: {Used.Count}/{Prefabs.Count} prefabs used, " +
                         $"{market.GetComponentsInChildren<BoxCollider>(true).Length} placed objects" +
                         (missing.Count > 0 ? "\nmissing: " + string.Join(", ", missing) : "");
            Debug.Log(report);
            return report;
        }

        // ---------- Placement engine ----------

        private static Transform Group(Transform parent, string name, Vector3 pos, float yaw)
        {
            var t = new GameObject(name).transform;
            t.SetParent(parent, false);
            t.localPosition = pos;
            t.localRotation = Quaternion.Euler(0f, yaw, 0f);
            return t;
        }

        private static Transform Composition(Transform parent, string name, Vector3 pos, float yaw)
        {
            var t = Group(parent, name, pos, yaw);
            Compositions.Add(t);
            return t;
        }

        private static float R(float range) => ((float)_rng.NextDouble() * 2f - 1f) * range;
        private static float R01() => (float)_rng.NextDouble();

        private static GameObject Spawn(string name, Transform parent)
        {
            var full = name.StartsWith("FMS_") ? name : "FMS_" + name;
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Prefabs[full], parent);
            Used.Add(full);
            foreach (var box in go.GetComponents<BoxCollider>())
            {
                if (!box.enabled) continue;
                box.enabled = false;
                DisabledBoxes.Add(box);
            }
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.name.EndsWith("_LOD1") || mf.name.EndsWith("_LOD2")) continue;
                var mc = mf.gameObject.AddComponent<MeshCollider>();
                mc.sharedMesh = mf.sharedMesh;
                TempColliders.Add(mc);
            }
            return go;
        }

        /// <summary>Exact local placement.</summary>
        private static Transform Put(Transform parent, string name, Vector3 local, float yaw = 0f, float scale = 1f, float pitch = 0f, float roll = 0f)
        {
            var go = Spawn(name, parent);
            go.transform.localPosition = local;
            go.transform.localRotation = Quaternion.Euler(pitch, yaw, roll);
            go.transform.localScale = Vector3.one * scale;
            Physics.SyncTransforms();
            return go.transform;
        }

        /// <summary>Casts down from local (x, startY, z) and rests the item's lowest point on whatever it hits. Returns null if nothing was hit.</summary>
        private static Transform Drop(Transform parent, string name, float x, float z, float startY, float yaw = 0f, float scale = 1f,
            float pitch = 0f, float roll = 0f, float sink = 0.06f)
        {
            var start = parent.TransformPoint(new Vector3(x, startY, z));
            if (!Physics.Raycast(start, Vector3.down, out var hit, startY * 2f + 3f)) return null;
            var go = Spawn(name, parent);
            var t = go.transform;
            t.rotation = parent.rotation * Quaternion.Euler(pitch, yaw, roll);
            t.localScale = Vector3.one * scale;
            t.position = new Vector3(hit.point.x, hit.point.y, hit.point.z);
            var b = Bounds(go);
            var offsetXZ = new Vector3(hit.point.x - b.center.x, 0f, hit.point.z - b.center.z);
            t.position += offsetXZ + Vector3.up * (hit.point.y - b.min.y - sink * b.size.y);
            Physics.SyncTransforms();
            return t;
        }

        /// <summary>Hangs an item so its top is at local height <paramref name="topY"/>.</summary>
        private static Transform Hang(Transform parent, string name, Vector3 local, float topY, float yaw = 0f, float scale = 1f)
        {
            var t = Put(parent, name, local, yaw, scale);
            var b = Bounds(t.gameObject);
            t.position += Vector3.up * (parent.TransformPoint(new Vector3(0f, topY, 0f)).y - b.max.y);
            Physics.SyncTransforms();
            return t;
        }

        private static Bounds Bounds(GameObject go)
        {
            var renderers = go.GetComponentsInChildren<MeshRenderer>(true)
                .Where(r => !r.name.EndsWith("_LOD1") && !r.name.EndsWith("_LOD2")).ToArray();
            var b = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) b.Encapsulate(r.bounds);
            return b;
        }

        /// <summary>Heap of items inside a container, resting on a hidden false floor at local height <paramref name="floor"/>.</summary>
        private static void Fill(Transform container, string item, int count, float floor, float inset = 0.72f, float scale = 1f, float tilt = 25f)
        {
            var box = container.GetComponent<BoxCollider>();
            if (floor > 0f)
            {
                var plate = new GameObject("_false_floor");
                plate.transform.SetParent(container, false);
                plate.transform.localPosition = new Vector3(box.center.x, floor, box.center.z);
                plate.AddComponent<BoxCollider>().size = new Vector3(box.size.x * 0.96f, 0.01f, box.size.z * 0.96f);
                TempObjects.Add(plate);
                Physics.SyncTransforms();
            }
            for (var i = 0; i < count; i++)
            {
                var x = box.center.x + R(box.size.x * 0.5f * inset);
                var z = box.center.z + R(box.size.z * 0.5f * inset);
                Drop(container, item, x, z, box.center.y + box.size.y * 0.5f + 0.35f, R(180f), scale * (1f + R(0.07f)), R(tilt), R(tilt), 0.12f);
            }
        }

        /// <summary>Neat layered heap (pyramid) inside a container: grid per layer, each layer one row smaller. Long items lie along X.</summary>
        private static void Heap(Transform container, string item, float floor, int layers, float scale = 1f, bool round = false, float inset = 0.84f)
        {
            var box = container.GetComponent<BoxCollider>();
            var itemBox = Prefabs["FMS_" + item].GetComponent<BoxCollider>();
            var ls = container.lossyScale;
            var sx = itemBox.size.x * scale; var sy = itemBox.size.y * scale; var sz = itemBox.size.z * scale;
            var lng = sx > sz * 1.6f;
            var stepX = (lng ? sx : Mathf.Max(sx, sz)) * 0.92f;
            var stepZ = (lng ? sz : Mathf.Max(sx, sz)) * 0.92f;
            var w = box.size.x * ls.x * inset; var d = box.size.z * ls.z * inset;
            var nx = Mathf.Max(1, Mathf.FloorToInt(w / stepX)); var nz = Mathf.Max(1, Mathf.FloorToInt(d / stepZ));
            for (var l = 0; l < layers; l++)
            {
                var cx = nx - l; var cz = nz - (lng ? 2 * l : l);
                if (cx < 1 || cz < 1) break;
                for (var ix = 0; ix < cx; ix++)
                for (var iz = 0; iz < cz; iz++)
                {
                    var ox = (ix - (cx - 1) * 0.5f) * stepX + R(stepX * 0.08f);
                    var oz = (iz - (cz - 1) * 0.5f) * stepZ + R(stepZ * 0.08f);
                    if (round && ox * ox / (w * w * 0.25f) + oz * oz / (d * d * 0.25f) > 1f) continue;
                    var pos = new Vector3(box.center.x + ox / ls.x, floor + l * sy * 0.62f / ls.y, box.center.z + oz / ls.z);
                    var yaw = lng ? (R01() < 0.5f ? 0f : 180f) + R(10f) : R(180f);
                    Put(container, item, pos, yaw, scale / ls.x * (1f + R(0.06f)), R(12f), R(12f));
                }
            }
        }

        /// <summary>Loose pile on any surface around local (x, z).</summary>
        private static void Pile(Transform parent, string item, float x, float z, float radius, int count, float startY = 1.6f, float scale = 1f, float tilt = 30f)
        {
            for (var i = 0; i < count; i++)
            {
                var a = R01() * Mathf.PI * 2f;
                var r = Mathf.Sqrt(R01()) * radius;
                Drop(parent, item, x + Mathf.Cos(a) * r, z + Mathf.Sin(a) * r, startY, R(180f), scale * (1f + R(0.07f)), R(tilt), R(tilt), 0.12f);
            }
        }

        /// <summary>A crate on a surface, tilted toward the viewer (-Z), filled with produce.</summary>
        private static Transform Crate(Transform parent, string crate, float x, float z, float startY, float yaw, float pitch, string item, int count,
            float floor, float itemScale = 1f)
        {
            var c = Drop(parent, crate, x, z, startY, yaw, 1f, pitch, 0f, 0f);
            if (item != null) Fill(c, item, count, floor, 0.72f, itemScale);
            return c;
        }

        /// <summary>Crate_Base with one of the modular Crate_Fill_* meshes in it (fills sit at the crate's origin).</summary>
        private static Transform FilledCrate(Transform parent, string fill, float x, float z, float startY, float yaw, float pitch = 0f)
        {
            var c = Drop(parent, "Crate_Base", x, z, startY, yaw, 1f, pitch, 0f, 0f);
            Put(c, fill, Vector3.zero);
            return c;
        }

        private static void Lamp(Transform at, Vector3 local) => LampPoints.Add(at.TransformPoint(local));

        // ---------- Zone B: vegetable row (medium stall, shelves, crates) ----------

        private static void VegetableRow(Transform z)
        {
            var stall = Put(z, "Stall_Table_Medium_Canopy", Vector3.zero);
            const float top = 1.5f; // ray start under the canopy
            var carrots = Crate(stall, "Crate_Slatted_Empty", -0.62f, 0.02f, top, 0f, -14f, null, 0, 0f);
            Carrots(carrots);
            var tomatoes = Crate(stall, "Crate_Slatted_Empty", 0.0f, 0.02f, top, 0f, -14f, null, 0, 0f);
            Heap(tomatoes, "Veg_Tomato_Whole", 0.14f, 3, 1.1f);
            var cucumbers = Crate(stall, "Crate_Slatted_Empty", 0.62f, 0.02f, top, 0f, -14f, null, 0, 0f);
            Heap(cucumbers, "Veg_Cucumber", 0.15f, 2, 1.0f);
            Drop(stall, "Veg_Tomato_Half", -0.06f, -0.27f, top, 170f, 1.2f, 0f, 0f, 0f);
            Drop(stall, "Veg_Tomato_Half", 0.08f, -0.28f, top, 195f, 1.2f, 0f, 0f, 0f);
            Drop(stall, "Veg_Tomato_Branch", 0.32f, -0.27f, top, 10f, 1.1f);
            Drop(stall, "Veg_Pepper", -0.30f, -0.27f, top, 30f);
            Drop(stall, "Veg_Pepper", -0.40f, -0.25f, top, -40f, 0.95f);
            Drop(stall, "Veg_Parsley", 0.55f, -0.29f, top, -20f, 1.3f);
            Hang(stall, "Deco_Lantern_Hanging", new Vector3(-1.02f, 0f, -0.48f), 2.12f, 0f, 0.9f);
            Lamp(stall, new Vector3(-1.02f, 1.55f, -0.48f));
            // under the counter
            Drop(stall, "Crate_Framed_Closed", -0.55f, 0.05f, 0.7f, 6f);
            Drop(stall, "Crate_Sack_Closed", 0.45f, 0.08f, 0.7f, 30f, 0.85f);

            // tiered shelves to the left (front of the model is +Z, turned to face the aisle)
            var shelf = Put(z, "Stall_Shelves", new Vector3(-1.85f, 0f, 0.1f), 180f);
            for (var i = 0; i < 3; i++) Drop(shelf, "Veg_Pumpkin", -0.38f + i * 0.38f, 0.22f, 0.62f, R(180f), 0.62f + R(0.05f));
            for (var i = 0; i < 4; i++) Drop(shelf, "Veg_Cabbage", -0.42f + i * 0.28f, 0.06f, 1.0f, R(180f), 0.95f);
            for (var i = 0; i < 4; i++) Drop(shelf, i % 2 == 0 ? "Veg_Greens" : "Veg_Beet", -0.42f + i * 0.28f, -0.14f, 1.6f, R(180f), 0.95f);

            // front: potato, onion and beet crates, pumpkins on the ground, corn basket, radish tray, chalkboard
            FilledCrate(z, "Crate_Fill_Potato", -0.58f, -0.92f, 1.0f, 8f);
            FilledCrate(z, "Crate_Fill_Onion", -0.05f, -0.98f, 1.0f, -4f);
            FilledCrate(z, "Crate_Fill_Beet", -0.32f, -0.96f, 1.0f, 3f, -8f);
            Drop(z, "Veg_Pumpkin", 0.62f, -0.92f, 1.0f, 30f, 1.05f);
            Drop(z, "Veg_Pumpkin", 1.0f, -0.7f, 1.0f, -60f, 0.85f);
            Drop(z, "Veg_Pumpkin", 0.88f, -1.25f, 1.0f, 110f, 0.7f);
            var corn = Drop(z, "Crate_Basket_Small", -1.3f, -0.95f, 1.0f, 20f);
            for (var i = 0; i < 6; i++)
                Put(corn, "Veg_Corn", new Vector3(R(0.05f), 0.06f, R(0.05f)), i * 60f + R(15f), 1f, 0f, 62f + R(8f));
            var tray = Drop(z, "Crate_Wire_Empty", 0.3f, -1.45f, 1.0f, -12f);
            Heap(tray, "Veg_Radish", 0.06f, 2, 1.2f);
            Drop(z, "Deco_Signboard_Chalk", 1.25f, -1.4f, 1.0f, 180f + 22f, 0.9f);
            Drop(z, "Crate_Sack_Open", -1.75f, -0.75f, 1.0f, 30f);
            Pile(z, "Veg_Garlic", -1.1f, -1.45f, 0.08f, 3, 1.0f, 1.2f);
            Drop(z, "Veg_Eggplant", -0.62f, -1.42f, 1.0f, 70f, 1.1f);
            Drop(z, "Veg_Eggplant", -0.48f, -1.5f, 1.0f, 20f);
            Drop(z, "Veg_Potato", -0.25f, -1.45f, 1.0f, 10f, 1.15f);
            Drop(z, "Veg_Onion", -0.1f, -1.5f, 1.0f, 40f, 1.15f);
        }

        /// <summary>Carrots lying across a crate in a fan, leafy tops toward the viewer (-Z).</summary>
        private static void Carrots(Transform crate)
        {
            var box = crate.GetComponent<BoxCollider>();
            for (var layer = 0; layer < 2; layer++)
            for (var i = 0; i < 6; i++)
            {
                var x = (i - 2.5f) * 0.068f + R(0.01f);
                Put(crate, "Veg_Carrot", new Vector3(x, 0.12f + layer * 0.045f, box.center.z + 0.02f + R(0.02f)), 90f + R(14f), 1.05f, R(6f), 18f + R(8f));
            }
        }

        // ---------- Zone C: fruit row (small stall, umbrella, crates) ----------

        private static void FruitRow(Transform z)
        {
            var stall = Put(z, "Stall_Table_Canopy", Vector3.zero);
            const float top = 1.5f;
            var oranges = Crate(stall, "Crate_Wire_Empty", -0.42f, 0.03f, top, 0f, -14f, null, 0, 0f);
            Heap(oranges, "Fruit_Orange", 0.1f, 3, 1.1f);
            var lemons = Crate(stall, "Crate_Wire_Empty", 0.12f, 0.03f, top, 0f, -14f, null, 0, 0f);
            Heap(lemons, "Fruit_Lemon", 0.1f, 3, 1.1f);
            Drop(stall, "Fruit_Grape", 0.5f, -0.02f, top, 30f, 1.25f);
            Drop(stall, "Fruit_Grape", 0.6f, 0.12f, top, -20f, 1.15f);
            var berries = Drop(stall, "Crate_Basket_Small", 0.55f, -0.2f, top, 0f, 0.8f);
            Put(berries, "Crate_Basket_Fill_Berries", new Vector3(0f, 0.15f, 0f), 0f, 1.25f);
            for (var i = 0; i < 4; i++) Drop(stall, "Fruit_Lemon_Slice", -0.30f + i * 0.07f, -0.28f, top, R(180f), 1.3f);
            Drop(stall, "Fruit_Strawberry", 0.3f, -0.28f, top, 10f, 1.4f);
            Drop(stall, "Fruit_Strawberry", 0.35f, -0.25f, top, 80f, 1.4f);
            Drop(stall, "Fruit_Orange", -0.62f, -0.27f, top, 0f);
            Hang(stall, "Deco_Lantern_Hanging", new Vector3(0.78f, 0f, -0.45f), 2.12f, 0f, 0.9f);
            Lamp(stall, new Vector3(0.78f, 1.55f, -0.45f));
            Drop(stall, "Crate_Framed_Closed", 0.35f, 0.05f, 0.7f, -8f);
            var under = Drop(stall, "Crate_Basket_Large", -0.4f, 0.05f, 0.7f, 0f, 0.95f);
            Heap(under, "Fruit_Apple", 0.22f, 3, 1.1f, true);

            // red umbrella with melons, apples and pears underneath
            Put(z, "Stall_Umbrella", new Vector3(1.75f, 0f, -0.3f), 20f);
            Drop(z, "Fruit_Watermelon", 1.42f, -0.75f, 1.6f, 20f, 1.1f);
            Drop(z, "Fruit_Watermelon", 1.8f, -0.95f, 1.6f, -40f, 1.0f);
            Drop(z, "Fruit_Watermelon", 1.62f, -0.82f, 1.6f, 70f, 0.95f);
            Drop(z, "Fruit_Watermelon", 2.15f, -0.62f, 1.6f, 10f, 1.05f);
            FilledCrate(z, "Crate_Fill_Apple", 2.1f, -0.05f, 1.6f, -20f);
            FilledCrate(z, "Crate_Fill_Pear", 2.25f, 0.42f, 1.6f, -35f);

            // front: apple basket, pear crate, wire crate of oranges, fruit spilled
            var apples = Drop(z, "Crate_Basket_Large", -0.7f, -0.95f, 1.0f, 15f);
            Heap(apples, "Fruit_Apple", 0.24f, 4, 1.1f, true);
            FilledCrate(z, "Crate_Fill_Apple", -0.05f, -1.0f, 1.0f, -6f);
            FilledCrate(z, "Crate_Fill_Pear", 0.5f, -0.95f, 1.0f, 8f);
            Drop(z, "Crate_Wire_Full", 0.32f, -1.45f, 1.0f, -15f);
            var strawberries = Drop(z, "Crate_Basket_Small", -1.05f, -1.45f, 1.0f, 0f);
            Heap(strawberries, "Fruit_Strawberry", 0.14f, 3, 1.4f, true);
            var applesSmall = Drop(z, "Crate_Basket_Small", -0.42f, -1.5f, 1.0f, 30f);
            Put(applesSmall, "Crate_Basket_Fill_Apples", new Vector3(0f, 0.14f, 0f), 0f, 1.3f);
            Drop(z, "Fruit_Apple", -0.15f, -1.45f, 1.0f, 20f);
            Drop(z, "Fruit_Pear", -0.02f, -1.55f, 1.0f, 70f);
            Drop(z, "Crate_Framed_Closed", -1.45f, -0.55f, 1.0f, 10f);
            Drop(z, "Crate_Framed_Closed", -1.45f, -0.55f, 1.2f, 25f);
            Drop(z, "Fruit_Watermelon", -1.42f, -0.55f, 1.4f, 0f, 0.9f);
            Drop(z, "Deco_Signs_Hanging", 1.0f, -1.5f, 1.0f, 180f - 20f, 0.9f);
        }

        // ---------- Zone D: dairy & food corner (L-stall) ----------

        private static void DairyFoodCorner(Transform z)
        {
            var stall = Put(z, "Stall_Table_Corner_Canopy", Vector3.zero);
            const float top = 1.5f;
            // L-shaped counter: back arm z 0.19..0.58 (x -0.58..0.58), right arm x 0.19..0.58 (z -0.58..0.58)
            for (var i = 0; i < 3; i++) Drop(stall, "Food_Milk_Bottle", -0.50f + (i % 2) * 0.09f, 0.30f + i * 0.09f, top, R(180f));
            Drop(stall, "Food_Cheese_Wheel", -0.26f, 0.40f, top, 20f);
            Drop(stall, "Food_Cheese_Wheel", -0.26f, 0.40f, top, 70f, 0.9f);
            Drop(stall, "Food_Cheese_Block", 0.02f, 0.42f, top, -10f);
            var board = Drop(stall, "Food_Cutting_Board", 0.38f, 0.36f, top, 45f, 0.9f);
            Drop(board, "Food_Cheese_Slice", 0.05f, 0f, 0.4f, 30f);
            Drop(board, "Food_Cheese_Slice", -0.08f, 0.02f, 0.4f, -20f, 0.9f);
            Drop(stall, "Stall_Scale", 0.40f, 0.05f, top, 270f);
            Drop(stall, "Stall_Weights", 0.30f, -0.18f, top, 20f, 1.1f);
            Drop(stall, "Food_Honey_Jars_Set", 0.42f, -0.30f, top, 100f, 1.1f);
            Drop(stall, "Food_Jam_Jar", 0.47f, -0.50f, top, 80f, 1.1f);
            Drop(stall, "Food_Honey_Jar", 0.30f, -0.50f, top, 30f, 1.1f);
            Drop(stall, "Food_Honey_Dipper", 0.26f, -0.38f, top, 60f, 1.2f);
            Drop(stall, "Food_Milk", -0.05f, 0.25f, 0.7f, 200f);
            Drop(stall, "Stall_Cashbox", 0.38f, 0.30f, 0.7f, 220f, 0.9f);
            Hang(stall, "Deco_Lantern_Hanging", new Vector3(-0.85f, 0f, 0.85f), 2.12f, 0f, 0.9f);
            Lamp(stall, new Vector3(-0.85f, 1.55f, 0.85f));
            var meatCrate = Drop(z, "Crate_Framed_Closed", 1.25f, -0.35f, 1.2f, -15f);
            Drop(meatCrate, "Food_Meat_Fish", 0f, 0f, 1.0f, 75f, 0.9f);

            // ground: churns, bucket, eggs, bread basket, fish tray
            Drop(z, "Crate_Milk_Can", -1.2f, 0.75f, 1.2f, 20f);
            Drop(z, "Crate_Milk_Can_Open", -1.5f, 0.35f, 1.2f, -30f);
            Drop(z, "Food_Milk_Bucket", -1.15f, 0.15f, 1.2f, 0f, 1.1f);
            var barrel = Drop(z, "Deco_Barrel_Standing", -1.45f, -0.45f, 1.2f, 0f);
            Drop(barrel, "Crate_Egg_Tray", 0f, 0f, 1.5f, 15f);
            Drop(barrel, "Crate_Egg_Single", 0.18f, -0.12f, 1.5f, 0f);
            Drop(z, "Crate_Egg_Basket", -0.95f, -0.95f, 1.2f, 30f, 1.1f);
            var bread = Drop(z, "Crate_Basket_Small", -0.45f, -1.2f, 1.2f, 0f);
            Put(bread, "Crate_Basket_Fill_Bread", new Vector3(0f, 0.15f, 0f), 0f, 1.3f);
            var eggs = Drop(z, "Crate_Basket_Small", -1.62f, -1.05f, 1.2f, 40f);
            Put(eggs, "Crate_Basket_Fill_Eggs", new Vector3(0f, 0.14f, 0f), 0f, 1.35f);
            Drop(z, "Food_Cheese_Wheel", 0.05f, -1.1f, 1.2f, 40f, 1.1f);
            var fish = Drop(z, "Crate_Slatted_Low", 0.6f, -1.15f, 1.2f, -10f);
            Drop(fish, "Food_Fish", -0.08f, 0f, 0.5f, 90f + R(10f));
            Drop(fish, "Food_Fish", 0.08f, 0f, 0.5f, 90f + R(10f));
            Drop(z, "Food_Ham", 1.0f, -0.85f, 1.2f, -20f);
        }

        // ---------- Zone A: merchant cart ----------

        private static void MerchantCartFull(Transform z)
        {
            var cart = Put(z, "Stall_Cart_Empty", Vector3.zero);
            const float top = 1.6f;
            FilledCrate(cart, "Crate_Fill_Cabbage", 0f, -0.45f, top, 0f);
            FilledCrate(cart, "Crate_Fill_Potato", 0f, -0.08f, top, 0f);
            Drop(cart, "Veg_Pumpkin", -0.12f, -0.45f, top, 30f, 0.65f);
            Drop(cart, "Veg_Pumpkin", 0.12f, -0.1f, top, 100f, 0.6f);
            Drop(cart, "Fruit_Watermelon", 0.05f, -0.28f, top, 40f, 0.8f);
            Drop(cart, "Crate_Sack_Closed", 0.0f, 0.12f, top, 90f, 0.75f, 70f);

            Drop(z, "Crate_Sack_Lying", 0.75f, -0.35f, 1.4f, 80f);
            Drop(z, "Crate_Sack_Closed", 0.8f, 0.3f, 1.4f, 20f);
            Drop(z, "Crate_Milk_Can", -0.8f, -0.75f, 1.4f, 10f);
            Drop(z, "Crate_Milk_Can", -0.55f, -1.05f, 1.4f, 60f);
            Drop(z, "Deco_Hay_Bale_Rect", -0.9f, 0.55f, 1.4f, 75f);
            Drop(z, "Deco_Hay_Pile", 0.2f, 1.2f, 1.4f, 0f, 0.7f);
            Drop(z, "Deco_Barrel_Small", 1.15f, -0.85f, 1.4f, 0f);
            FilledCrate(z, "Crate_Fill_Cabbage", 0.35f, -1.25f, 1.4f, 15f);
            Drop(z, "Veg_Cabbage", 0.0f, -1.3f, 1.4f, 30f);
        }

        // ---------- Zone E: the square (picnic table, lamp, signs) ----------

        private static void MarketSquarePlaza(Transform z)
        {
            var table = Put(z, "Deco_Table_Set", Vector3.zero, 25f);
            Put(z, "Stall_Umbrella_Green", Vector3.zero, 25f);
            Drop(table, "Food_Bread_Loaf", -0.35f, 0.05f, 1.5f, 20f);
            var board = Drop(table, "Food_Cutting_Board", 0.25f, -0.05f, 1.5f, -10f);
            Drop(board, "Food_Cheese_Slice", 0f, 0f, 0.4f, 40f);
            Drop(table, "Food_Milk_Bottle", 0.55f, 0.15f, 1.5f, 0f);
            Drop(table, "Fruit_Apple", -0.6f, -0.15f, 1.5f, 0f);
            Drop(table, "Fruit_Pear", -0.68f, -0.05f, 1.5f, 50f);

            Put(z, "Deco_Signpost_Arrows", new Vector3(1.75f, 0f, -1.85f), 160f);
            Drop(z, "Deco_Signboard_Chalk", -1.35f, -1.75f, 1.4f, 180f + 20f, 0.9f);
            var barrel = Drop(z, "Deco_Barrel_Standing", 1.95f, 1.15f, 1.4f, 0f);
            Drop(barrel, "Stall_Cashbox", 0f, 0f, 1.6f, -30f, 0.9f);
            Drop(z, "Deco_Barrel_Small", 2.35f, 0.65f, 1.4f, 0f);
            Drop(z, "Deco_Planter_Box", -2.05f, 0.9f, 1.4f, 70f);
            Drop(z, "Deco_Pot_Medium", -2.0f, 0.15f, 1.4f, 0f);
            Drop(z, "Deco_Pot_Small", -1.75f, -0.2f, 1.4f, 0f);
            Drop(z, "Deco_Planter_Box_Yellow", 2.25f, -0.35f, 1.4f, -80f);
            Put(z, "Deco_Table_Plank", new Vector3(-0.1f, 0f, 2.15f), 8f, 0.9f);
        }

        // ---------- Floral & garden stand ----------

        private static void FloralPlanterStand(Transform z)
        {
            var table = Put(z, "Stall_Table_Open", Vector3.zero);
            const float top = 1.5f;
            Drop(table, "Deco_Pot_Medium", -0.5f, 0.05f, top, 0f);
            Drop(table, "Deco_Pot_Small", -0.2f, -0.1f, top, 40f);
            Drop(table, "Deco_Pot_Small", 0.05f, 0.1f, top, 10f);
            Drop(table, "Deco_Pot_Medium", 0.35f, 0.0f, top, 80f);
            Drop(table, "Deco_Pot_Empty", 0.6f, -0.15f, top, 0f);
            for (var i = 0; i < 4; i++) Drop(table, "Crate_Seed_Packet", -0.55f + i * 0.1f, -0.25f, top, R(20f));
            Drop(table, "Crate_Seed_Sack_Small", 0.62f, 0.18f, top, 30f);
            Drop(table, "Crate_Seed_Sack_Small", 0.0f, 0.05f, 0.7f, 10f);
            Drop(table, "Crate_Seed_Sack_Large", -0.4f, 0.05f, 0.7f, -20f, 0.9f);

            Drop(z, "Deco_Planter_Box", -0.35f, -0.85f, 1.2f, 0f);
            Drop(z, "Deco_Planter_Box_Yellow", 0.45f, -0.95f, 1.2f, 5f);
            Drop(z, "Deco_Planter_Box_Empty", 1.2f, -0.6f, 1.2f, 75f);
            Drop(z, "Deco_Pot_Large", -1.2f, -0.5f, 1.2f, 0f);
            Drop(z, "Deco_Pot_Medium", -1.0f, -1.0f, 1.2f, 30f);
            Drop(z, "Deco_Pot_Small", -1.45f, -0.95f, 1.2f, 0f);
            Drop(z, "Deco_Pot_Empty", -0.7f, -1.3f, 1.2f, 0f);
            Drop(z, "Crate_Seed_Sack_Large", 1.25f, 0.25f, 1.2f, -20f);
            Drop(z, "Deco_Barrel_Small", 1.35f, 0.75f, 1.2f, 0f);
            Put(z, "Deco_Bench_Plank", new Vector3(0f, 0f, 1.1f), 180f);
            Drop(z, "Deco_Pot_Small", -0.4f, 1.1f, 1.2f, 0f);
        }

        // ---------- Bakery (red canopy over an open medium table) ----------

        private static void Bakery(Transform z)
        {
            var table = Put(z, "Stall_Table_Medium_Open", Vector3.zero);
            Put(z, "Stall_Canopy", new Vector3(0f, 0f, 0.05f));
            const float top = 1.5f;
            for (var i = 0; i < 4; i++) Drop(table, "Food_Bread_Loaf", -0.85f + i * 0.22f, 0.12f, top, R(30f));
            for (var i = 0; i < 3; i++) Drop(table, "Food_Bread_Loaf", -0.75f + i * 0.22f, -0.12f, top, R(30f), 0.95f);
            var basket = Drop(table, "Crate_Basket_Large", 0.15f, 0.05f, top, 0f, 0.85f);
            for (var i = 0; i < 5; i++)
                Put(basket, "Food_Bread_Baguette", new Vector3(R(0.06f), 0.04f, R(0.06f)), i * 72f + R(10f), 1f / 0.85f, 0f, 68f + R(8f));
            var board = Drop(table, "Food_Cutting_Board", 0.62f, -0.05f, top, 90f, 1.1f);
            Pile(board, "Food_Bread_Croissant", 0f, 0f, 0.08f, 4, 0.5f);
            Drop(table, "Food_Bread_Croissant", 0.82f, 0.2f, top, 30f);
            var bread = Drop(table, "Crate_Basket_Small", 0.45f, 0.22f, top, 0f, 0.9f);
            Put(bread, "Crate_Basket_Fill_Bread", new Vector3(0f, 0.15f, 0f), 0f, 1.3f);
            Drop(table, "Food_Honey_Jar", 0.95f, -0.25f, top, 0f);
            Drop(table, "Food_Jam_Jar", -0.95f, -0.27f, top, 30f);
            Drop(table, "Crate_Sack_Closed", -0.5f, 0.05f, 0.7f, 20f, 0.85f);
            Drop(table, "Crate_Framed_Closed", 0.4f, 0.05f, 0.7f, 0f);

            Put(z, "Stall_Umbrella_Blue", new Vector3(1.95f, 0f, -0.4f), -15f);
            Drop(z, "Deco_Barrel_Open", 1.8f, -0.2f, 1.6f, 0f);
            Drop(z, "Crate_Sack_Open", -1.5f, -0.6f, 1.4f, -30f);
            Drop(z, "Crate_Sack_Closed", -1.3f, -0.95f, 1.4f, 10f);
            Put(z, "Deco_Lantern_Wall", new Vector3(-1.42f, 1.55f, -0.70f), 180f);
            Lamp(z, new Vector3(-1.42f, 1.68f, -1.25f));
            Drop(z, "Deco_Signboard_Chalk", 1.2f, -1.2f, 1.4f, 180f - 25f, 0.9f);
        }

        // ---------- Unloading: hay, sacks, barrels, crate stacks ----------

        private static void Unloading(Transform z)
        {
            Put(z, "Deco_Hay_Bale_Round", new Vector3(-1.6f, 0f, 0.8f), 70f);
            Put(z, "Deco_Hay_Stack", new Vector3(0.0f, 0f, 1.1f), 10f);
            Drop(z, "Deco_Hay_Bale_Rect", 1.0f, 0.4f, 2f, 80f);
            Drop(z, "Deco_Hay_Bale_Rect", 1.05f, 0.45f, 2f, 95f);
            Drop(z, "Deco_Hay_Pile", -0.4f, -0.5f, 2f, 0f, 0.8f);
            Drop(z, "Crate_Sack_Pile", 1.9f, -0.2f, 2f, -30f);
            Drop(z, "Crate_Sack_Closed", 2.3f, -0.8f, 2f, 10f);
            Drop(z, "Crate_Sack_Open", 1.55f, -1.0f, 2f, 40f);
            Drop(z, "Crate_Seed_Sack_Large", 2.5f, 0.4f, 2f, 0f);
            Drop(z, "Deco_Barrel_Lying", -1.3f, -0.9f, 2f, 60f);
            Drop(z, "Deco_Barrel_Standing", -2.2f, -0.3f, 2f, 0f);
            Drop(z, "Deco_Barrel_Small", -2.0f, -0.95f, 2f, 0f);
            Drop(z, "Crate_Framed_Closed", 0.5f, -1.4f, 2f, 15f);
            Drop(z, "Crate_Framed_Closed", 0.55f, -1.4f, 2.4f, 5f);
            var open = Drop(z, "Crate_Framed_Open", 1.0f, -1.75f, 2f, -20f);
            Heap(open, "Veg_Potato", 0.26f, 2, 1.15f);
            Drop(z, "Crate_Tilted", -0.25f, -1.55f, 2f, 30f);
            Pile(z, "Veg_Potato", -0.15f, -1.95f, 0.22f, 5, 2f, 1.1f);
        }

        // ---------- Front stall by the path entrance: root veg in crates, pumpkins, sacks ----------

        private static void FrontStall(Transform z)
        {
            var stall = Put(z, "Stall_Table_Canopy", Vector3.zero);
            const float top = 1.5f;
            FilledCrate(stall, "Crate_Fill_Beet", -0.45f, 0.0f, top, 0f, -14f);
            FilledCrate(stall, "Crate_Fill_Cabbage", 0.05f, 0.0f, top, 0f, -14f);
            var carrots = Drop(stall, "Crate_Slatted_Empty", 0.5f, 0.0f, top, 0f, 1f, -14f, 0f, 0f);
            Carrots(carrots);
            Drop(stall, "Veg_Cabbage", -0.2f, -0.27f, top, 0f, 0.9f);
            Drop(stall, "Veg_Beet", -0.55f, -0.27f, top, 60f);
            Drop(stall, "Veg_Radish", 0.3f, -0.28f, top, -30f, 1.2f);
            Drop(stall, "Veg_Radish", 0.38f, -0.25f, top, 40f, 1.2f);
            Drop(stall, "Crate_Sack_Closed", -0.4f, 0.05f, 0.7f, 10f, 0.85f);
            Drop(stall, "Crate_Framed_Closed", 0.35f, 0.05f, 0.7f, 0f);
            Hang(stall, "Deco_Lantern_Hanging", new Vector3(-0.78f, 0f, -0.45f), 2.12f, 0f, 0.9f);
            Lamp(stall, new Vector3(-0.78f, 1.55f, -0.45f));

            FilledCrate(z, "Crate_Fill_Potato", -0.5f, -0.9f, 1.2f, 6f);
            FilledCrate(z, "Crate_Fill_Onion", 0.02f, -0.95f, 1.2f, -8f);
            Drop(z, "Crate_Base", -0.22f, -0.92f, 1.6f, 0f, 1f, -10f);
            var corn = Drop(z, "Crate_Basket_Large", 0.6f, -0.95f, 1.2f, 0f);
            for (var i = 0; i < 9; i++)
                Put(corn, "Veg_Corn", new Vector3(R(0.08f), 0.06f, R(0.08f)), i * 40f + R(15f), 1.1f, 0f, 62f + R(8f));
            Drop(z, "Veg_Pumpkin", 1.15f, -0.55f, 1.2f, 20f, 1.15f);
            Drop(z, "Veg_Pumpkin", 1.25f, -1.05f, 1.2f, 80f, 0.85f);
            Drop(z, "Veg_Pumpkin", 1.6f, -0.8f, 1.2f, 140f, 0.7f);
            Drop(z, "Crate_Sack_Open", -1.15f, -0.6f, 1.2f, 20f);
            Drop(z, "Crate_Seed_Sack_Small", -1.25f, -1.05f, 1.2f, 0f);
            Drop(z, "Deco_Signboard_Chalk", -0.9f, -1.45f, 1.2f, 180f - 10f, 0.85f);
            Drop(z, "Veg_Onion", 0.25f, -1.4f, 1.2f, 30f, 1.15f);
            Drop(z, "Veg_Potato", 0.12f, -1.45f, 1.2f, 0f, 1.15f);
        }

        // ---------- Umbrella display: produce crates around the pole ----------

        private static void UmbrellaDisplay(Transform z)
        {
            Put(z, "Stall_Umbrella", Vector3.zero, 10f);
            FilledCrate(z, "Crate_Fill_Apple", -0.45f, -0.35f, 1.6f, 15f);
            FilledCrate(z, "Crate_Fill_Pear", 0.15f, -0.5f, 1.6f, -10f);
            FilledCrate(z, "Crate_Fill_Onion", 0.55f, 0.05f, 1.6f, 70f);
            var stack = Drop(z, "Crate_Framed_Closed", -0.45f, 0.35f, 1.6f, 5f);
            FilledCrate(stack, "Crate_Fill_Potato", 0f, 0f, 1.0f, 0f);
            var melons = Drop(z, "Crate_Basket_Large", 0.3f, 0.6f, 1.6f, 0f);
            Heap(melons, "Fruit_Orange", 0.24f, 3, 1.1f, true);
            Drop(z, "Fruit_Watermelon", -0.95f, -0.2f, 1.6f, 0f, 1.05f);
            Drop(z, "Fruit_Watermelon", -1.05f, 0.2f, 1.6f, 60f, 0.95f);
            Drop(z, "Veg_Pumpkin", 0.95f, -0.45f, 1.6f, 40f, 0.9f);
            Drop(z, "Crate_Sack_Closed", 1.0f, 0.55f, 1.6f, 10f);
            Drop(z, "Deco_Signboard_Chalk", -0.2f, -1.15f, 1.6f, 180f + 30f, 0.85f);
        }

        // ---------- Standalone tent over a ground display ----------

        private static void TentDisplay(Transform z)
        {
            Put(z, "Stall_Canopy", Vector3.zero);
            const float top = 1.8f;
            var shelf = Put(z, "Stall_Shelves", new Vector3(0f, 0f, 0.25f), 180f);
            for (var i = 0; i < 3; i++) Drop(shelf, "Fruit_Watermelon", -0.38f + i * 0.38f, 0.22f, 0.62f, R(180f), 0.8f);
            for (var i = 0; i < 4; i++) Drop(shelf, "Veg_Cabbage", -0.42f + i * 0.28f, 0.06f, 1.0f, R(180f), 0.95f);
            for (var i = 0; i < 5; i++) Drop(shelf, i % 2 == 0 ? "Veg_Eggplant" : "Veg_Pepper", -0.44f + i * 0.22f, -0.14f, 1.6f, R(180f), 1.1f);
            FilledCrate(z, "Crate_Fill_Cabbage", -1.0f, -0.25f, top, 10f);
            FilledCrate(z, "Crate_Fill_Beet", -1.05f, 0.2f, top, -5f);
            var tomatoes = Drop(z, "Crate_Slatted_Empty", 0.95f, -0.2f, top, -10f);
            Heap(tomatoes, "Veg_Tomato_Whole", 0.14f, 3, 1.1f);
            var peppers = Drop(z, "Crate_Wire_Empty", 1.0f, 0.3f, top, 15f);
            Heap(peppers, "Veg_Pepper", 0.1f, 2, 1.0f);
            Drop(z, "Veg_Pumpkin", -0.3f, -0.6f, top, 30f, 0.95f);
            Drop(z, "Veg_Pumpkin", 0.25f, -0.65f, top, 80f, 0.75f);
            Drop(z, "Deco_Barrel_Small", -1.55f, 0.6f, top, 0f);
        }

        // ---------- Along the path: bunting, lamps, arrows, loose produce ----------

        private static void PathDressing(Transform z)
        {
            Put(z, "Deco_Bunting_Pennants_Posts", new Vector3(0.1f, 0f, -6.6f), 12f);
            var back = LampString(z, "Deco_Bunting_Lanterns", new Vector2(-1.15f, 6.0f), 0f);
            var right = LampString(z, "Deco_Bunting_Pennants", new Vector2(2.6f, -2.35f), 74f);
            Arrow(z, "Deco_Sign_Arrow_Green", right[0], 1.55f, 200f);
            Arrow(z, "Deco_Sign_Arrow_Yellow", right[0], 1.35f, 330f);
            Arrow(z, "Deco_Sign_Arrow", back[1], 1.5f, 20f);
            Put(z, "Deco_Signpost_Single", new Vector3(-1.75f, 0f, -6.6f), 200f);

            // loose produce and crates on the path edges (foreground interest)
            FilledCrate(z, "Crate_Fill_Cabbage", -1.55f, -3.9f, 1.2f, 20f);
            FilledCrate(z, "Crate_Fill_Apple", -1.8f, -3.3f, 1.2f, -10f);
            Drop(z, "Crate_Base", -1.65f, -3.6f, 1.6f, 35f);
            Drop(z, "Fruit_Apple", -1.15f, -3.35f, 1.2f, 0f);
            Drop(z, "Fruit_Apple", -1.1f, -3.5f, 1.2f, 0f);
            Drop(z, "Veg_Cabbage", -1.2f, -4.3f, 1.2f, 30f);
            // pumpkin display on hay bales right of the entrance
            Drop(z, "Deco_Hay_Bale_Rect", 2.35f, -6.0f, 1.2f, 20f);
            Drop(z, "Deco_Hay_Bale_Rect", 2.95f, -5.6f, 1.2f, 30f);
            Drop(z, "Deco_Hay_Bale_Rect", 2.6f, -5.8f, 1.6f, 25f);
            Drop(z, "Veg_Pumpkin", 2.55f, -5.85f, 2.0f, 0f, 1.1f);
            Drop(z, "Veg_Pumpkin", 2.25f, -6.05f, 2.0f, 60f, 0.8f);
            Drop(z, "Veg_Pumpkin", 3.0f, -5.55f, 2.0f, 120f, 0.75f);
            Drop(z, "Veg_Pumpkin", 1.6f, -6.2f, 1.2f, 0f, 1.15f);
            Drop(z, "Veg_Pumpkin", 1.85f, -6.75f, 1.2f, 50f, 0.85f);
            Drop(z, "Veg_Pumpkin", 3.45f, -6.25f, 1.2f, 120f, 0.95f);
            Drop(z, "Veg_Pumpkin", 3.1f, -6.6f, 1.2f, 20f, 0.7f);
            Drop(z, "Crate_Tilted", 1.45f, -5.4f, 1.2f, -30f);
            Drop(z, "Fruit_Watermelon", 3.65f, -5.6f, 1.2f, 0f, 1.05f);
            Drop(z, "Fruit_Watermelon", 3.95f, -5.9f, 1.2f, 70f, 0.95f);
            var carrots = Drop(z, "Crate_Slatted_Low", -2.45f, -1.95f, 1.2f, 10f);
            Pile(carrots, "Veg_Carrot", 0f, 0f, 0.1f, 5, 0.6f);
            Drop(z, "Crate_Seed_Packet", -2.3f, -2.35f, 1.2f, 20f);
        }

        /// <summary>Two lamp posts 4 m apart (string length) with a garland hung between their tops.</summary>
        private static Vector3[] LampString(Transform parent, string garland, Vector2 center, float yaw)
        {
            var dir = Quaternion.Euler(0f, yaw, 0f) * Vector3.right;
            var c = new Vector3(center.x, 0f, center.y);
            var posts = new[] { c - dir * 2.0f, c + dir * 2.0f };
            for (var i = 0; i < 2; i++)
            {
                Put(parent, "Deco_Lantern_Post", posts[i], yaw + (i == 1 ? 180f : 0f));
                Lamp(parent, posts[i] + Vector3.up * 2.5f);
            }
            Hang(parent, garland, c, 2.66f, yaw);
            return posts;
        }

        /// <summary>Direction arrow nailed to a post: the pivot is the bottom centre of the board, which runs along local X.</summary>
        private static void Arrow(Transform parent, string arrow, Vector3 post, float height, float yaw)
        {
            var rot = Quaternion.Euler(0f, yaw, 0f);
            Put(parent, arrow, post + rot * new Vector3(0.33f, 0f, 0.07f) + Vector3.up * height, yaw);
        }

        // ---------- Back and edges: keep the frame full ----------

        private static void Outskirts(Transform z)
        {
            // behind the stall rows
            Put(z, "Deco_Hay_Stack", new Vector3(-6.4f, 0f, 6.4f), 20f);
            Put(z, "Deco_Hay_Bale_Round", new Vector3(-4.6f, 0f, 6.9f), 80f);
            Put(z, "Deco_Hay_Bale_Round", new Vector3(3.6f, 0f, 6.9f), 10f);
            Drop(z, "Crate_Sack_Pile", -2.4f, 6.3f, 2f, 10f);
            Drop(z, "Crate_Framed_Closed", -2.9f, 6.9f, 2f, 0f);
            Drop(z, "Crate_Framed_Closed", -2.5f, 7.0f, 2f, 20f);
            Drop(z, "Crate_Framed_Closed", -2.7f, 6.9f, 2.5f, 10f);
            Drop(z, "Deco_Barrel_Standing", 1.6f, 6.2f, 2f, 0f);
            Drop(z, "Deco_Barrel_Standing", 2.2f, 6.4f, 2f, 0f);
            Drop(z, "Deco_Barrel_Lying", 7.6f, 5.8f, 2f, 30f);
            Put(z, "Deco_Bunting_Pennants_Posts", new Vector3(4.6f, 0f, 7.4f), -10f);
            // right edge beyond the dairy corner and bakery
            Put(z, "Deco_Hay_Stack", new Vector3(8.6f, 0f, 1.6f), 40f);
            Drop(z, "Deco_Hay_Bale_Rect", 8.4f, -2.4f, 2f, 0f);
            Drop(z, "Crate_Framed_Closed", 7.9f, 3.9f, 2f, 0f);
            Drop(z, "Crate_Framed_Closed", 8.0f, 3.9f, 2.5f, 15f);
            // left edge behind the cart
            Put(z, "Deco_Hay_Bale_Round", new Vector3(-7.6f, 0f, 2.4f), 60f);
            Drop(z, "Crate_Sack_Closed", -7.3f, 0.4f, 2f, 0f);
            Drop(z, "Crate_Sack_Lying", -7.5f, -0.3f, 2f, 40f);
            Drop(z, "Deco_Hay_Pile", -6.9f, 4.6f, 2f, 0f, 0.9f);
            // front edge
            Drop(z, "Deco_Planter_Box", -3.6f, -7.6f, 2f, 10f);
            Drop(z, "Deco_Pot_Large", -2.8f, -8.0f, 2f, 0f);
            Drop(z, "Deco_Planter_Box_Yellow", 4.9f, -7.6f, 2f, -15f);
            Put(z, "Deco_Hay_Bale_Round", new Vector3(6.6f, 0f, -6.6f), 30f);
        }

        // ---------- Small groups and straw patches in the gaps between zones ----------

        private static void Fillers(Transform z)
        {
            // between the vegetable row and the square
            var crate = Drop(z, "Crate_Framed_Closed", -2.45f, 0.75f, 2f, 15f);
            var apples = Drop(crate, "Crate_Basket_Small", 0f, 0f, 1.0f, 0f);
            Heap(apples, "Fruit_Apple", 0.12f, 3, 1.1f, true);
            Drop(z, "Crate_Sack_Closed", -2.95f, 0.45f, 2f, 30f);
            Drop(z, "Crate_Sack_Lying", -2.7f, 1.25f, 2f, 100f);
            // under the pennant string, between the square and the flower stand
            FilledCrate(z, "Crate_Fill_Potato", 2.55f, -1.35f, 2f, 25f);
            Drop(z, "Veg_Pumpkin", 2.95f, -1.05f, 2f, 0f, 0.9f);
            Drop(z, "Veg_Pumpkin", 3.2f, -1.45f, 2f, 70f, 0.7f);
            Drop(z, "Crate_Milk_Can", 2.25f, -0.9f, 2f, 0f);
            // by the cart
            Drop(z, "Deco_Barrel_Standing", -3.55f, -1.2f, 2f, 0f);
            Drop(z, "Crate_Milk_Can_Open", -3.2f, -0.95f, 2f, 40f);
        }

        // ---------- Studio stages (off the market, solid backdrops for catalogue shots) ----------

        public static readonly Vector3 CatalogueOrigin = new Vector3(200f, 0f, 0f);
        public static readonly Vector3 StallsOrigin = new Vector3(260f, 0f, 0f);
        public static readonly Vector3 CompositionsOrigin = new Vector3(320f, 0f, 0f);
        public static readonly Vector3 IconOrigin = new Vector3(380f, 0f, 0f);
        public static readonly Vector3 FoodOrigin = new Vector3(440f, 0f, 0f);

        private static void StudioFloor(Transform parent, Vector2 size, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Plane);
            go.name = "Studio_Floor";
            go.transform.SetParent(parent, false);
            go.transform.localScale = new Vector3(size.x / 10f, 1f, size.y / 10f);
            go.GetComponent<MeshRenderer>().sharedMaterial = SolidMaterial($"M_Studio_{ColorUtility.ToHtmlStringRGB(color)}", color, false);
        }

        // Catalogue grid: one block per category, uniform cells; items scaled up to fill a cell, capped so big ones fit.
        private static readonly (string Category, float Cell, float MaxScale)[] CatalogueRows =
        {
            ("Stall", 1.6f, 0.8f), ("Deco", 1.0f, 1.3f), ("Crate", 0.85f, 2.0f), ("Food", 0.8f, 3.6f), ("Veg", 0.8f, 4.4f), ("Fruit", 0.85f, 5.0f),
        };

        private static void Catalogue(Transform z)
        {
            StudioFloor(z, new Vector2(80f, 80f), new Color(0.80f, 0.76f, 0.70f));
            const float rowWidth = 17f;
            var zRow = 5.4f;
            foreach (var (category, cell, maxScale) in CatalogueRows)
            {
                var names = Prefabs.Keys.Where(k => k.StartsWith($"FMS_{category}_")).OrderBy(k => k).ToList();
                var cols = Mathf.FloorToInt(rowWidth / cell);
                for (var i = 0; i < names.Count; i++)
                {
                    var col = i % cols;
                    if (i > 0 && col == 0) zRow -= cell;
                    var inRow = Mathf.Min(cols, names.Count - (i - col));
                    var b0 = Prefabs[names[i]].GetComponent<BoxCollider>();
                    var scale = Mathf.Min(maxScale, cell * 0.86f / Mathf.Max(b0.size.x, b0.size.z, b0.size.y * 0.8f));
                    var local = new Vector3((col - (inRow - 1) * 0.5f) * cell, 0f, zRow);
                    var t = Put(z, names[i], local, 0f, scale);
                    var b = Bounds(t.gameObject);
                    var want = z.TransformPoint(local);
                    t.position += new Vector3(want.x - b.center.x, -b.min.y, want.z - b.center.z);
                }
                zRow -= cell + 0.35f;
            }
        }

        private static void StallLineup(Transform z)
        {
            StudioFloor(z, new Vector2(60f, 60f), new Color(0.80f, 0.76f, 0.70f));
            var back = new[] { "Stall_Table_Corner_Canopy", "Stall_Table_Medium_Canopy", "Stall_Table_Canopy", "Stall_Canopy", "Stall_Shelves" };
            var front = new[] { "Stall_Umbrella", "Stall_Umbrella_Blue", "Stall_Umbrella_Green", "Stall_Table_Medium_Open", "Stall_Table_Open", "Stall_Cart_Empty" };
            Row(z, back, 2.2f, 0.5f);
            Row(z, front, -1.4f, 0.4f);
            var x = -3.2f;
            foreach (var n in new[] { "Deco_Table_Set", "Deco_Table_Plank", "Deco_Bench_Plank", "Stall_Scale", "Stall_Weights", "Stall_Cashbox" })
            {
                Put(z, n, new Vector3(x, 0f, -4.2f), 0f, n.StartsWith("Stall") ? 2f : 1f);
                x += n.StartsWith("Deco_Table") ? 2.1f : 1.3f;
            }
        }

        private static void Row(Transform z, string[] names, float zPos, float gap)
        {
            var widths = names.Select(n => Prefabs["FMS_" + n].GetComponent<BoxCollider>().size.x + gap).ToArray();
            var x = -widths.Sum() * 0.5f;
            for (var i = 0; i < names.Length; i++)
            {
                Put(z, names[i], new Vector3(x + widths[i] * 0.5f, 0f, zPos), names[i] == "Stall_Shelves" ? 180f : 0f);
                x += widths[i];
            }
        }

        private static void IconStage(Transform z)
        {
            StudioFloor(z, new Vector2(30f, 30f), new Color(1.0f, 0.93f, 0.80f));
            var crate = Put(z, "Crate_Slatted_Empty", Vector3.zero, -12f);
            Heap(crate, "Veg_Tomato_Whole", 0.14f, 3, 1.1f);
            Drop(z, "Veg_Tomato_Whole", 0.05f, -0.42f, 1f, 30f, 1.6f);
            Drop(z, "Veg_Tomato_Half", -0.22f, -0.38f, 1f, 160f, 1.6f, 0f, 0f, 0f);
            Drop(z, "Veg_Tomato_Branch", 0.32f, -0.3f, 1f, -20f, 1.3f);
        }

        private static void FoodStage(Transform z)
        {
            StudioFloor(z, new Vector2(40f, 40f), new Color(0.93f, 0.84f, 0.72f));
            var table = Put(z, "Stall_Table_Medium_Open", Vector3.zero);
            const float top = 1.5f;
            // left: cheese
            var board = Drop(table, "Food_Cutting_Board", -0.68f, -0.02f, top, 8f);
            Drop(board, "Food_Cheese_Wheel", -0.05f, 0.02f, 0.5f, 30f, 0.9f);
            Drop(board, "Food_Cheese_Slice", 0.14f, -0.02f, 0.5f, -30f);
            Drop(table, "Food_Cheese_Wheel", -0.82f, 0.18f, top, 0f);
            Drop(table, "Food_Cheese_Wheel", -0.82f, 0.18f, top, 50f, 0.92f);
            Drop(table, "Food_Cheese_Block", -0.4f, 0.15f, top, 15f);
            // centre: bread
            var basket = Drop(table, "Crate_Basket_Large", -0.05f, 0.12f, top, 0f, 0.8f);
            for (var i = 0; i < 6; i++)
                Put(basket, "Food_Bread_Baguette", new Vector3(R(0.06f), 0.04f, R(0.06f)), i * 60f + R(10f), 1f / 0.8f, 0f, 68f + R(8f));
            for (var i = 0; i < 3; i++) Drop(table, "Food_Bread_Loaf", -0.3f + i * 0.21f, -0.1f, top, R(25f));
            var croissants = Drop(table, "Food_Cutting_Board", 0.3f, 0.1f, top, 80f, 0.9f);
            Pile(croissants, "Food_Bread_Croissant", 0f, 0f, 0.08f, 4, 0.5f);
            // right: honey, jam, milk, meat
            Drop(table, "Food_Honey_Jars_Set", 0.62f, 0.15f, top, 10f, 1.1f);
            Drop(table, "Food_Jam_Jar", 0.82f, -0.12f, top, 30f, 1.1f);
            Drop(table, "Food_Honey_Jar", 0.68f, -0.2f, top, -20f, 1.1f);
            Drop(table, "Food_Honey_Dipper", 0.52f, -0.24f, top, 70f, 1.2f);
            Drop(table, "Food_Milk_Bottle", 0.9f, 0.22f, top, 0f);
            Drop(table, "Food_Milk_Bottle", 0.82f, 0.28f, top, 40f);
            // ground
            var barrel = Drop(z, "Deco_Barrel_Standing", 1.45f, -0.15f, top, 0f);
            Drop(barrel, "Food_Meat_Fish", 0f, 0f, 1.6f, 20f, 0.95f);
            var fish = Drop(z, "Crate_Slatted_Low", 1.25f, -0.85f, top, -10f);
            Drop(fish, "Food_Fish", -0.08f, 0f, 0.5f, 90f);
            Drop(fish, "Food_Fish", 0.08f, 0f, 0.5f, 95f);
            Drop(z, "Food_Ham", 0.7f, -0.75f, top, -30f, 1.1f);
            Drop(z, "Crate_Milk_Can", -1.45f, 0.05f, top, 20f);
            Drop(z, "Crate_Milk_Can_Open", -1.25f, -0.45f, top, -30f);
            Drop(z, "Food_Milk_Bucket", -0.85f, -0.75f, top, 0f, 1.15f);
            Drop(z, "Food_Milk", -1.55f, -0.6f, top, 30f);
            Drop(z, "Crate_Egg_Basket", -0.3f, -0.85f, top, 20f, 1.1f);
            Drop(z, "Crate_Egg_Tray", 0.2f, -0.82f, top, -10f, 1.1f);
            var bread = Drop(z, "Crate_Basket_Small", 0.3f, 0.75f, top, 0f);
            Put(bread, "Crate_Basket_Fill_Bread", new Vector3(0f, 0.15f, 0f), 0f, 1.3f);
            Drop(z, "Deco_Signboard_Chalk", -1.0f, 0.75f, top, 180f + 15f, 0.9f);
        }

        /// <summary>The six compositions as prefab instances in two rows (for the modular-compositions shot).</summary>
        private static void CompositionLineup()
        {
            var z = new GameObject("Compositions_Lineup").transform;
            z.SetParent(_studio, false);
            z.position = CompositionsOrigin;
            StudioFloor(z, new Vector2(60f, 60f), new Color(0.78f, 0.80f, 0.74f));
            var slots = new[]
            {
                new Vector3(-5.6f, 0f, 3.2f), new Vector3(0f, 0f, 3.4f), new Vector3(5.8f, 0f, 3.0f),
                new Vector3(-5.4f, 0f, -2.6f), new Vector3(0f, 0f, -2.6f), new Vector3(5.4f, 0f, -2.6f),
            };
            for (var i = 0; i < Compositions.Count; i++)
            {
                var asset = AssetDatabase.LoadAssetAtPath<GameObject>($"{CompositionDir}/{Compositions[i].name}.prefab");
                var go = (GameObject)PrefabUtility.InstantiatePrefab(asset, z);
                go.transform.localPosition = slots[i];
            }
        }

        // ---------- Lamps (warm point lights in the lanterns) ----------

        private static void BuildLamps(Transform market)
        {
            var holder = Group(market, "Lantern_Lights", Vector3.zero, 0f);
            foreach (var p in LampPoints)
            {
                var light = new GameObject("Lantern_Light").AddComponent<Light>();
                light.transform.SetParent(holder, true);
                light.transform.position = p;
                light.type = LightType.Point;
                light.color = new Color(1f, 0.72f, 0.42f);
                light.intensity = 1.0f;
                light.range = 2.6f;
                light.shadows = LightShadows.None;
            }
        }

        // ---------- Build-time collider cleanup and composition prefabs ----------

        private static void Cleanup()
        {
            foreach (var c in TempColliders) Object.DestroyImmediate(c);
            foreach (var g in TempObjects) Object.DestroyImmediate(g);
            foreach (var b in DisabledBoxes) if (b != null) b.enabled = true;
            TempColliders.Clear(); TempObjects.Clear(); DisabledBoxes.Clear();
        }

        private static void SaveCompositions()
        {
            foreach (var comp in Compositions)
            {
                var pos = comp.localPosition;
                var rot = comp.localRotation;
                comp.localPosition = Vector3.zero;
                comp.localRotation = Quaternion.identity;
                PrefabUtility.SaveAsPrefabAssetAndConnect(comp.gameObject, $"{CompositionDir}/{comp.name}.prefab", InteractionMode.AutomatedAction);
                comp.localPosition = pos;
                comp.localRotation = rot;
            }
        }

        // ---------- Ground: grass field, dirt plaza, cobble S-path, central cobble circle, grass tufts ----------

        private static readonly Vector2[] PathPoints =
        {
            new Vector2(-0.8f, -16f), new Vector2(-0.3f, -7.5f), new Vector2(1.3f, -4.4f), new Vector2(0.9f, -2.1f),
            new Vector2(0.2f, -0.3f), new Vector2(-0.7f, 1.5f), new Vector2(-1.15f, 3.2f), new Vector2(-1.15f, 9f),
        };

        private static readonly Vector2 PlazaCenter = new Vector2(0.3f, 0.2f);
        private const float PlazaRx = 9.0f, PlazaRz = 7.8f;

        private static void BuildGround(Transform env)
        {
            var grass = MarketGroundTextures.Grass(TextureDir, "M_Full_Grass", Vector2.one);
            var dirt = MarketGroundTextures.Dirt(TextureDir, "M_Full_Dirt", Vector2.one);
            var cobble = MarketGroundTextures.Cobble(TextureDir, "M_Full_Cobble", Vector2.one);
            MoveToSettings(grass); MoveToSettings(dirt); MoveToSettings(cobble);
            grass.SetColor("_BaseColor", new Color(0.62f, 0.70f, 0.55f));
            dirt.SetColor("_BaseColor", new Color(0.96f, 0.92f, 0.88f));
            cobble.SetColor("_BaseColor", new Color(0.86f, 0.84f, 0.80f));
            foreach (var m in new[] { grass, dirt, cobble }) EditorUtility.SetDirty(m);

            MeshObject(env, "Ground_Grass", Disc(new Vector2(0f, 2f), 90f, 90f, 0f, 0f, 48, 0f, 0.3f), grass, true);
            MeshObject(env, "Ground_Plaza_Dirt", Disc(PlazaCenter, PlazaRx, PlazaRz, 0.012f, 0.7f, 96, 3.5f, 0.6f), dirt, true);
            var hills = new GameObject("Hills").transform;
            hills.SetParent(env, false);
            var hillRng = new Random(31);
            for (var i = 0; i < 16; i++)
            {
                var a = i / 16f * Mathf.PI * 2f + (float)hillRng.NextDouble() * 0.3f;
                var r = 38f + (float)hillRng.NextDouble() * 22f;
                var rx = 10f + (float)hillRng.NextDouble() * 12f;
                var h = 2.5f + (float)hillRng.NextDouble() * 4.5f;
                var c = new Vector2(Mathf.Cos(a) * r, 2f + Mathf.Sin(a) * r);
                MeshObject(hills, $"Hill_{i:00}", Hill(c, rx, rx * (0.6f + (float)hillRng.NextDouble() * 0.4f), h, i), grass, false);
            }
            MeshObject(env, "Ground_Square_Cobble", Disc(new Vector2(0.25f, -0.3f), 2.5f, 2.3f, 0.026f, 0.1f, 64, 0.3f, 0.85f), cobble, true);
            MeshObject(env, "Ground_Path_Cobble", Ribbon(PathPoints, 1.9f, 0.022f, 0.85f), cobble, true);
            ScatterGrass(env);
        }

        private static void MoveToSettings(Material mat)
        {
            var path = AssetDatabase.GetAssetPath(mat);
            var target = $"{SettingsDir}/{Path.GetFileName(path)}";
            if (path != target)
            {
                AssetDatabase.DeleteAsset(target);
                AssetDatabase.MoveAsset(path, target);
            }
        }

        private static void MeshObject(Transform parent, string name, Mesh mesh, Material mat, bool collider)
        {
            var path = $"{MeshDir}/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mesh, path);
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = mat;
            if (collider) go.AddComponent<MeshCollider>().sharedMesh = mesh;
            go.isStatic = true;
        }

        /// <summary>Wobbly ellipse disc (fan), UVs in world metres * uvScale.</summary>
        private static Mesh Disc(Vector2 c, float rx, float rz, float y, float wobble, int segments, float wobbleFreq, float uvScale)
        {
            var verts = new List<Vector3> { new Vector3(c.x, y, c.y) };
            var rng = new Random(segments);
            var phase = (float)rng.NextDouble() * 6f;
            for (var i = 0; i < segments; i++)
            {
                var a = i / (float)segments * Mathf.PI * 2f;
                var w = 1f + (wobble / Mathf.Max(rx, rz)) * (Mathf.Sin(a * wobbleFreq + phase) * 0.6f + Mathf.Sin(a * wobbleFreq * 2.3f + phase * 2f) * 0.4f);
                verts.Add(new Vector3(c.x + Mathf.Cos(a) * rx * w, y, c.y + Mathf.Sin(a) * rz * w));
            }
            var tris = new List<int>();
            for (var i = 0; i < segments; i++) tris.AddRange(new[] { 0, 1 + (i + 1) % segments, 1 + i });
            return FlatMesh(verts, tris, uvScale);
        }

        /// <summary>Smooth low hill: dome profile on an ellipse, faceted like the props.</summary>
        private static Mesh Hill(Vector2 c, float rx, float rz, float height, int seed)
        {
            const int rings = 7, segments = 28;
            var rng = new Random(seed);
            var verts = new List<Vector3>();
            var tris = new List<int>();
            verts.Add(new Vector3(c.x, height, c.y));
            for (var ri = 1; ri <= rings; ri++)
            {
                var t = ri / (float)rings;
                var y = height * (1f - t * t) * (1f - 0.15f * t);
                for (var si = 0; si < segments; si++)
                {
                    var a = si / (float)segments * Mathf.PI * 2f;
                    var n = 1f + ((float)rng.NextDouble() - 0.5f) * 0.12f;
                    verts.Add(new Vector3(c.x + Mathf.Cos(a) * rx * t * n, ri == rings ? -0.05f : y, c.y + Mathf.Sin(a) * rz * t * n));
                }
            }
            for (var si = 0; si < segments; si++) tris.AddRange(new[] { 0, 1 + (si + 1) % segments, 1 + si });
            for (var ri = 1; ri < rings; ri++)
            for (var si = 0; si < segments; si++)
            {
                var a = 1 + (ri - 1) * segments + si; var b = 1 + (ri - 1) * segments + (si + 1) % segments;
                var c2 = a + segments; var d = b + segments;
                tris.AddRange(new[] { a, b, c2, b, d, c2 });
            }
            var mesh = FlatMesh(verts, tris, 0.3f);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            return mesh;
        }

        /// <summary>Path strip along a Catmull-Rom curve through the points.</summary>
        private static Mesh Ribbon(Vector2[] pts, float width, float y, float uvScale)
        {
            var curve = new List<Vector2>();
            for (var i = 0; i < pts.Length - 1; i++)
            {
                var p0 = pts[Mathf.Max(i - 1, 0)]; var p1 = pts[i]; var p2 = pts[i + 1]; var p3 = pts[Mathf.Min(i + 2, pts.Length - 1)];
                for (var s = 0; s < 12; s++)
                {
                    var t = s / 12f;
                    curve.Add(0.5f * (2f * p1 + (-p0 + p2) * t + (2f * p0 - 5f * p1 + 4f * p2 - p3) * t * t + (-p0 + 3f * p1 - 3f * p2 + p3) * t * t * t));
                }
            }
            curve.Add(pts[pts.Length - 1]);
            var verts = new List<Vector3>();
            var tris = new List<int>();
            for (var i = 0; i < curve.Count; i++)
            {
                var dir = (curve[Mathf.Min(i + 1, curve.Count - 1)] - curve[Mathf.Max(i - 1, 0)]).normalized;
                var side = new Vector2(-dir.y, dir.x);
                var w = width * 0.5f * (1f + 0.06f * Mathf.Sin(i * 0.7f));
                var a = curve[i] + side * w; var b = curve[i] - side * w;
                verts.Add(new Vector3(a.x, y, a.y));
                verts.Add(new Vector3(b.x, y, b.y));
                if (i == 0) continue;
                var k = i * 2;
                tris.AddRange(new[] { k - 2, k, k - 1, k - 1, k, k + 1 });
            }
            return FlatMesh(verts, tris, uvScale);
        }

        private static Mesh FlatMesh(List<Vector3> verts, List<int> tris, float uvScale)
        {
            var mesh = new Mesh { name = "Ground", indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, verts.Select(v => new Vector2(v.x, v.z) * uvScale).ToList());
            mesh.SetNormals(verts.Select(_ => Vector3.up).ToList());
            mesh.SetTriangles(tris, 0);
            // fix winding so every face points up
            var t = mesh.triangles;
            for (var i = 0; i < t.Length; i += 3)
            {
                var n = Vector3.Cross(verts[t[i + 1]] - verts[t[i]], verts[t[i + 2]] - verts[t[i]]);
                if (n.y < 0f) (t[i + 1], t[i + 2]) = (t[i + 2], t[i + 1]);
            }
            mesh.triangles = t;
            mesh.RecalculateBounds();
            mesh.RecalculateTangents();
            return mesh;
        }

        private static bool OnPlaza(float x, float z) => Mathf.Pow((x - PlazaCenter.x) / (PlazaRx - 0.2f), 2f) + Mathf.Pow((z - PlazaCenter.y) / (PlazaRz - 0.2f), 2f) < 1f;

        private static void ScatterGrass(Transform env)
        {
            var rng = new Random(99);
            float Rn() => (float)rng.NextDouble();
            var greens = new[] { new Color(0.27f, 0.50f, 0.14f), new Color(0.36f, 0.60f, 0.17f), new Color(0.48f, 0.70f, 0.22f) };
            var flowers = new[] { new Color(0.98f, 0.97f, 0.90f), new Color(1f, 0.82f, 0.22f), new Color(0.95f, 0.45f, 0.58f), new Color(0.66f, 0.48f, 0.90f) };
            var grassB = greens.Select(_ => new Blades()).ToArray();
            var flowerB = flowers.Select(_ => new Blades()).ToArray();

            for (var i = 0; i < 12000; i++)
            {
                // dense ring hugging the plaza edge, sparser further out
                var a = Rn() * Mathf.PI * 2f;
                var ring = i < 5000 ? 1.0f + Rn() * 0.18f : 1.0f + Mathf.Pow(Rn(), 1.6f) * 3.5f;
                var x = PlazaCenter.x + Mathf.Cos(a) * (PlazaRx + 0.2f) * ring;
                var z = PlazaCenter.y + Mathf.Sin(a) * (PlazaRz + 0.2f) * ring;
                if (OnPlaza(x, z)) continue;
                var s = 0.8f + Rn() * 0.8f;
                var b = grassB[i % 3];
                for (var k = 0; k < 6; k++)
                    b.Blade(new Vector3(x + (Rn() - 0.5f) * 0.2f, 0f, z + (Rn() - 0.5f) * 0.2f), Rn() * 6.28f, (0.14f + Rn() * 0.16f) * s, 0.035f, 0.05f + Rn() * 0.08f);
            }
            // tufts poking into the plaza edge and along the path
            for (var i = 0; i < 700; i++)
            {
                var a = Rn() * Mathf.PI * 2f;
                var x = PlazaCenter.x + Mathf.Cos(a) * PlazaRx * (0.93f + Rn() * 0.08f);
                var z = PlazaCenter.y + Mathf.Sin(a) * PlazaRz * (0.93f + Rn() * 0.08f);
                for (var k = 0; k < 5; k++)
                    grassB[k % 3].Blade(new Vector3(x + (Rn() - 0.5f) * 0.15f, 0f, z + (Rn() - 0.5f) * 0.15f), Rn() * 6.28f, 0.12f + Rn() * 0.12f, 0.03f, 0.05f);
            }
            for (var i = 0; i < 1400; i++)
            {
                var a = Rn() * Mathf.PI * 2f;
                var ring = 1.02f + Mathf.Pow(Rn(), 1.3f) * 2.2f;
                var x = PlazaCenter.x + Mathf.Cos(a) * (PlazaRx + 0.2f) * ring;
                var z = PlazaCenter.y + Mathf.Sin(a) * (PlazaRz + 0.2f) * ring;
                var h = 0.18f + Rn() * 0.12f;
                grassB[0].Blade(new Vector3(x, 0f, z), Rn() * 6.28f, h, 0.02f, 0.01f);
                flowerB[rng.Next(flowerB.Length)].Head(new Vector3(x, h + 0.01f, z), 0.035f + Rn() * 0.02f);
            }

            var holder = new GameObject("Grass_And_Flowers").transform;
            holder.SetParent(env, false);
            for (var i = 0; i < greens.Length; i++) BladeObject(holder, $"Full_Grass_{i}", grassB[i], SolidMaterial($"M_Full_Grass_{i}", greens[i], true));
            for (var i = 0; i < flowers.Length; i++) BladeObject(holder, $"Full_Flowers_{i}", flowerB[i], SolidMaterial($"M_Full_Flower_{i}", flowers[i], false));
        }

        private static void BladeObject(Transform parent, string name, Blades b, Material mat)
        {
            var mesh = b.ToMesh(name);
            var path = $"{MeshDir}/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mesh, path);
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = mat;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            go.isStatic = true;
        }

        private sealed class Blades
        {
            private readonly List<Vector3> _v = new List<Vector3>();
            private readonly List<Vector3> _n = new List<Vector3>();
            private readonly List<int> _t = new List<int>();

            public void Blade(Vector3 p, float yaw, float h, float w, float lean)
            {
                var dir = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));
                var side = new Vector3(Mathf.Cos(yaw), 0f, -Mathf.Sin(yaw));
                var mid = p + Vector3.up * h * 0.55f + dir * lean * 0.4f;
                var s = _v.Count;
                _v.Add(p - side * w * 0.5f); _v.Add(p + side * w * 0.5f);
                _v.Add(mid + side * w * 0.35f); _v.Add(mid - side * w * 0.35f);
                _v.Add(p + Vector3.up * h + dir * lean);
                for (var i = 0; i < 5; i++) _n.Add(Vector3.up);
                _t.AddRange(new[] { s, s + 3, s + 2, s, s + 2, s + 1, s + 3, s + 4, s + 2 });
            }

            public void Head(Vector3 c, float r)
            {
                var s = _v.Count;
                _v.Add(c + Vector3.up * r * 0.6f); _v.Add(c - Vector3.up * r * 0.4f);
                _v.Add(c + Vector3.right * r); _v.Add(c + Vector3.forward * r); _v.Add(c - Vector3.right * r); _v.Add(c - Vector3.forward * r);
                for (var i = 0; i < 6; i++) _n.Add(Vector3.up);
                for (var i = 0; i < 4; i++)
                {
                    var a = s + 2 + i; var b = s + 2 + (i + 1) % 4;
                    _t.AddRange(new[] { s, b, a, s + 1, a, b });
                }
            }

            public Mesh ToMesh(string name)
            {
                var m = new Mesh { name = name, indexFormat = IndexFormat.UInt32 };
                m.SetVertices(_v); m.SetNormals(_n); m.SetTriangles(_t, 0); m.RecalculateBounds();
                return m;
            }
        }

        private static Material SolidMaterial(string name, Color color, bool doubleSided)
        {
            var path = $"{SettingsDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", 0.1f);
            mat.SetFloat("_Metallic", 0f);
            if (doubleSided) mat.SetFloat("_Cull", 0f);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ---------- Light, sky, post ----------

        private static void BuildLook()
        {
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.87f, 0.70f);
            sun.intensity = 2.0f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.82f;
            sun.transform.rotation = Quaternion.Euler(36f, 68f, 0f);
            RenderSettings.sun = sun;

            AssetDatabase.DeleteAsset($"{SettingsDir}/M_Full_Sky.mat");
            var sky = new Material(Shader.Find("FarmMarketFull/Gradient Sky"));
            AssetDatabase.CreateAsset(sky, $"{SettingsDir}/M_Full_Sky.mat");
            sky.SetColor("_ZenithColor", new Color(0.34f, 0.55f, 0.86f));
            sky.SetColor("_HorizonColor", new Color(0.95f, 0.90f, 0.80f));
            sky.SetColor("_GroundColor", new Color(0.62f, 0.62f, 0.52f));
            sky.SetFloat("_Exponent", 0.55f);
            sky.SetFloat("_Exposure", 1.0f);
            EditorUtility.SetDirty(sky);
            RenderSettings.skybox = sky;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.66f, 0.76f, 0.92f);
            RenderSettings.ambientEquatorColor = new Color(0.78f, 0.70f, 0.58f);
            RenderSettings.ambientGroundColor = new Color(0.44f, 0.37f, 0.27f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.90f, 0.86f, 0.76f);
            RenderSettings.fogStartDistance = 22f;
            RenderSettings.fogEndDistance = 95f;

            Volume("Post_Global", GradeProfile(), 1f);
            Volume("Post_DoF", DofProfile(), 0f);
        }

        private static void Volume(string name, VolumeProfile profile, float weight)
        {
            var v = new GameObject(name).AddComponent<Volume>();
            v.isGlobal = true;
            v.weight = weight;
            v.sharedProfile = profile;
        }

        private static VolumeProfile Profile(string name)
        {
            var path = $"{SettingsDir}/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            var p = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(p, path);
            return p;
        }

        private static void SaveProfile(VolumeProfile p)
        {
            foreach (var c in p.components) AssetDatabase.AddObjectToAsset(c, p);
            EditorUtility.SetDirty(p);
        }

        private static VolumeProfile GradeProfile()
        {
            var p = Profile("VP_Full_Market");
            p.Add<Tonemapping>().mode.Override(TonemappingMode.ACES);
            var bloom = p.Add<Bloom>();
            bloom.threshold.Override(1.1f);
            bloom.intensity.Override(0.25f);
            bloom.scatter.Override(0.7f);
            bloom.tint.Override(new Color(1f, 0.92f, 0.80f));
            var color = p.Add<ColorAdjustments>();
            color.postExposure.Override(0.25f);
            color.contrast.Override(14f);
            color.saturation.Override(12f);
            p.Add<WhiteBalance>().temperature.Override(8f);
            var lift = p.Add<ShadowsMidtonesHighlights>();
            lift.shadows.Override(new Vector4(0.96f, 0.98f, 1.06f, 0.02f)); // cool, slightly lifted shadows
            var vignette = p.Add<Vignette>();
            vignette.intensity.Override(0.2f);
            vignette.smoothness.Override(0.5f);
            SaveProfile(p);
            return p;
        }

        private static VolumeProfile DofProfile()
        {
            var p = Profile("VP_Full_DoF");
            var dof = p.Add<DepthOfField>();
            dof.mode.Override(DepthOfFieldMode.Bokeh);
            dof.focusDistance.Override(2f);
            dof.focalLength.Override(70f);
            dof.aperture.Override(2.2f);
            SaveProfile(p);
            return p;
        }

        // ---------- Shots ----------

        private struct ShotSpec
        {
            public string Name;
            public int W, H, Supersample;
            public Vector3 Pos, Target;
            public float Fov, Focus;
            public Color Background; // alpha 0 = sky
        }

        private static readonly ShotSpec[] ShotSpecs =
        {
            new ShotSpec { Name = "03_Cover_1950x1300", W = 1950, H = 1300, Supersample = 2, Pos = new Vector3(-9.0f, 11.2f, -9.6f), Target = new Vector3(0.4f, 0.5f, 0.4f), Fov = 30f },
            new ShotSpec { Name = "04_Hero_Showcase_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(10.6f, 8.2f, -10.4f), Target = new Vector3(0.0f, 0.6f, 1.0f), Fov = 30f },
            new ShotSpec { Name = "10_Gameplay_TopDown_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(-8.6f, 18.4f, -8.4f), Target = new Vector3(0.4f, 0f, 0.4f), Fov = 30f },
            new ShotSpec { Name = "02_Card_1260x840", W = 1260, H = 840, Supersample = 2, Pos = new Vector3(-2.4f, 2.7f, -2.6f), Target = new Vector3(-1.4f, 0.9f, 3.0f), Fov = 40f },
            new ShotSpec { Name = "06_Produce_Closeup_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(0.25f, 1.45f, 2.45f), Target = new Vector3(0.85f, 0.95f, 3.85f), Fov = 32f, Focus = 1.55f },
            new ShotSpec { Name = "01_Icon_1024x1024", W = 1024, H = 1024, Supersample = 2, Pos = IconOrigin + new Vector3(-0.35f, 1.15f, -1.55f), Target = IconOrigin + new Vector3(0.0f, 0.2f, -0.12f), Fov = 26f, Background = new Color(1.0f, 0.945f, 0.84f) },
            new ShotSpec { Name = "05_Full_Collection_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = CatalogueOrigin + new Vector3(0f, 13.4f, -9.6f), Target = CatalogueOrigin + new Vector3(0f, 0f, -0.25f), Fov = 37f, Background = new Color(0.80f, 0.76f, 0.70f) },
            new ShotSpec { Name = "07_Stalls_Furniture_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = StallsOrigin + new Vector3(-3.0f, 8.5f, -12.5f), Target = StallsOrigin + new Vector3(0f, 0.8f, -0.4f), Fov = 36f, Background = new Color(0.80f, 0.76f, 0.70f) },
            new ShotSpec { Name = "09_Modular_Compositions_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = CompositionsOrigin + new Vector3(-4.0f, 11.5f, -13.5f), Target = CompositionsOrigin + new Vector3(0.2f, 0.4f, 0.4f), Fov = 38f, Background = new Color(0.78f, 0.80f, 0.74f) },
            new ShotSpec { Name = "08_Food_Bakery_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = FoodOrigin + new Vector3(-0.6f, 2.45f, -2.95f), Target = FoodOrigin + new Vector3(0.1f, 0.5f, -0.35f), Fov = 40f, Background = new Color(0.93f, 0.84f, 0.72f) },
        };

        private static void BuildShotCameras()
        {
            var holder = new GameObject("Shots (disabled cameras, used by Render Shots)").transform;
            foreach (var s in ShotSpecs)
            {
                var go = new GameObject(s.Name);
                go.transform.SetParent(holder, false);
                go.transform.position = s.Pos;
                go.transform.LookAt(s.Target);
                var cam = go.AddComponent<Camera>();
                cam.fieldOfView = s.Fov;
                cam.nearClipPlane = 0.1f;
                cam.farClipPlane = 200f;
                cam.enabled = false;
                var data = go.AddComponent<UniversalAdditionalCameraData>();
                data.renderPostProcessing = true;
            }

            var main = new GameObject("Main Camera") { tag = "MainCamera" };
            var mc = main.AddComponent<Camera>();
            mc.fieldOfView = 30f;
            mc.nearClipPlane = 0.1f;
            mc.farClipPlane = 200f;
            mc.clearFlags = CameraClearFlags.Skybox;
            main.AddComponent<AudioListener>();
            var md = main.AddComponent<UniversalAdditionalCameraData>();
            md.renderPostProcessing = true;
            md.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            main.transform.position = ShotSpecs[0].Pos;
            main.transform.LookAt(ShotSpecs[0].Target);
        }

        /// <summary>Renders every shot camera (name filter optional) into AssetStore/Full/Draft. <paramref name="resScale"/> &lt; 1 for quick previews.</summary>
        [MenuItem("Tools/Farm Market Full/Render Shots")]
        public static void RenderShotsMenu() => RenderShots(null, 1f);

        public static string RenderShots(string filter, float resScale)
        {
            if (EditorSceneManager.GetActiveScene().path != ScenePath) EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var roots = SceneManager.GetActiveScene().GetRootGameObjects();
            var shots = roots.First(g => g.name.StartsWith("Shots")).transform;
            var main = roots.First(g => g.name == "Main Camera").GetComponent<Camera>();
            var dof = roots.First(g => g.name == "Post_DoF").GetComponent<Volume>();
            var outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AssetStore", "Full", "Draft"));
            Directory.CreateDirectory(outDir);

            var oldPipeline = QualitySettings.renderPipeline;
            var pipeline = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var hero = MarketHeroShots.HeroPipeline(pipeline);
            var so = new SerializedObject(hero);
            so.FindProperty("m_ShadowDistance").floatValue = 60f;
            so.FindProperty("m_MainLightShadowmapResolution").intValue = 4096;
            so.ApplyModifiedPropertiesWithoutUndo();
            QualitySettings.renderPipeline = hero;
            var startPos = main.transform.position; var startRot = main.transform.rotation; var startFov = main.fieldOfView;
            var log = new StringBuilder();
            try
            {
                MarketHeroShots.Capture(main, null, 64, 64, 1);
                foreach (Transform shot in shots)
                {
                    if (filter != null && !shot.name.Contains(filter)) continue;
                    var spec = ShotSpecs.FirstOrDefault(s => s.Name == shot.name);
                    if (spec.Name == null) continue;
                    main.transform.SetPositionAndRotation(shot.position, shot.rotation);
                    main.fieldOfView = shot.GetComponent<Camera>().fieldOfView;
                    var studio = spec.Background.a > 0f;
                    main.clearFlags = studio ? CameraClearFlags.SolidColor : CameraClearFlags.Skybox;
                    main.backgroundColor = spec.Background;
                    RenderSettings.fog = !studio;
                    dof.weight = spec.Focus > 0f ? 1f : 0f;
                    if (spec.Focus > 0f && dof.sharedProfile.TryGet(out DepthOfField d)) d.focusDistance.Override(spec.Focus);
                    var w = Mathf.RoundToInt(spec.W * resScale); var h = Mathf.RoundToInt(spec.H * resScale);
                    var path = Path.Combine(outDir, spec.Name + ".png");
                    MarketHeroShots.Capture(main, path, w * spec.Supersample, h * spec.Supersample, spec.Supersample);
                    log.AppendLine(path);
                }
            }
            finally
            {
                QualitySettings.renderPipeline = oldPipeline;
                dof.weight = 0f;
                main.clearFlags = CameraClearFlags.Skybox;
                RenderSettings.fog = true;
                main.transform.SetPositionAndRotation(startPos, startRot);
                main.fieldOfView = startFov;
            }
            return log.ToString();
        }
    }
}
