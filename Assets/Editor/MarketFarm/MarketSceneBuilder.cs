using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace MarketFarm.Editor
{
    /// <summary>
    /// Builds Base prefabs from the FBX files, Group prefabs from the Base prefabs, and the MarketDemo scene.
    /// Idempotent: re-running overwrites the same assets (GUIDs stay).
    /// </summary>
    public static class MarketSceneBuilder
    {
        internal const string Root = "Assets/Art/MarketFarm";
        internal const string BaseDir = Root + "/Prefabs/Base";
        internal const string GroupDir = Root + "/Prefabs/Groups";
        internal const string MaterialDir = Root + "/Materials";
        internal const string SceneryDir = Root + "/Prefabs/Scenery";
        private const string ScenePath = "Assets/Scenes/MarketDemo.unity";
        internal const string VolumeProfilePath = "Assets/Settings/SampleSceneProfile.asset";

        private static readonly string[] ModelFolders = { Root, "Assets/Art/StreetStall" };

        private static Dictionary<string, GameObject> _bases;
        private static Dictionary<string, GameObject> _groups;

        [MenuItem("Tools/MarketFarm/Build Demo Market")]
        public static void Build()
        {
            foreach (var dir in new[] { BaseDir, GroupDir, MaterialDir, SceneryDir }) Directory.CreateDirectory(dir);

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            _bases = BuildBasePrefabs();
            _groups = BuildGroupPrefabs();
            BuildScene();

            EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), ScenePath);
            AssetDatabase.SaveAssets();
            Debug.Log($"[MarketFarm] built {_bases.Count} base prefabs, {_groups.Count} groups, scene {ScenePath}");
        }

        internal static string OutputDir(string subfolder)
        {
            var root = System.Environment.GetEnvironmentVariable("MARKET_SHOTS");
            if (string.IsNullOrEmpty(root)) root = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AssetStore"));
            var dir = Path.Combine(root, subfolder);
            Directory.CreateDirectory(dir);
            return dir;
        }

        // Batch entry: build + render previews into the folder given by MARKET_SHOTS (or default AssetStore_Media).
        [MenuItem("Tools/MarketFarm/Render Asset Store Previews")]
        public static void BuildAndShoot()
        {
            Build();
            var dir = System.Environment.GetEnvironmentVariable("MARKET_SHOTS");
            if (string.IsNullOrEmpty(dir))
            {
                dir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AssetStore_Media"));
            }
            Directory.CreateDirectory(dir);

            // 1920x1080 Cover & Gallery Screenshots
            Shoot(Path.Combine(dir, "Cover_1920x1080.png"), new Vector3(-12f, 8f, -13f), new Vector3(0f, 0f, 2f), 36f, 1920, 1080);
            Shoot(Path.Combine(dir, "Screenshot_1_Wide_1920x1080.png"), new Vector3(-12f, 8f, -13f), new Vector3(0f, 0f, 2f), 36f, 1920, 1080);
            Shoot(Path.Combine(dir, "Screenshot_2_Front_1920x1080.png"), new Vector3(0f, 7f, -15f), new Vector3(0f, 0f, 2f), 42f, 1920, 1080);
            Shoot(Path.Combine(dir, "Screenshot_3_Stalls_1920x1080.png"), new Vector3(-2f, 3.2f, -2f), new Vector3(-2f, 1f, 6f), 45f, 1920, 1080);
            Shoot(Path.Combine(dir, "Screenshot_4_Farm_1920x1080.png"), new Vector3(-6f, 3.2f, -9f), new Vector3(-11.5f, 0.5f, -2f), 45f, 1920, 1080);
            Shoot(Path.Combine(dir, "Screenshot_5_Right_1920x1080.png"), new Vector3(5f, 3.5f, -9f), new Vector3(11f, 0.5f, -1f), 45f, 1920, 1080);

            // Required Asset Store format cards:
            Shoot(Path.Combine(dir, "Card_280x210.png"), new Vector3(-2f, 3.2f, -2f), new Vector3(-2f, 1f, 6f), 45f, 280, 210);
            Shoot(Path.Combine(dir, "Social_1200x630.png"), new Vector3(-12f, 8f, -13f), new Vector3(0f, 0f, 2f), 36f, 1200, 630);

            Debug.Log($"[MarketFarm] Previews successfully exported to: {dir}");
        }

        // ---------- Base prefabs ----------

        private static Dictionary<string, GameObject> BuildBasePrefabs()
        {
            var result = new Dictionary<string, GameObject>();
            var materials = BuildModelMaterials();
            foreach (var guid in AssetDatabase.FindAssets("t:Model", ModelFolders))
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(guid));
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
                PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                instance.name = $"P_{model.name}";

                foreach (var r in instance.GetComponentsInChildren<Renderer>(true))
                {
                    var shared = r.sharedMaterials;
                    for (var i = 0; i < shared.Length; i++)
                        if (materials.TryGetValue(shared[i].name, out var replacement)) shared[i] = replacement;
                    r.sharedMaterials = shared;
                }

                foreach (var t in instance.GetComponentsInChildren<Transform>(true))
                {
                    if (!t.name.EndsWith("_Col")) continue;
                    var mesh = t.GetComponent<MeshFilter>().sharedMesh;
                    Object.DestroyImmediate(t.GetComponent<MeshRenderer>());
                    Object.DestroyImmediate(t.GetComponent<MeshFilter>());
                    t.gameObject.AddComponent<MeshCollider>().sharedMesh = mesh;
                }

                var prefab = PrefabUtility.SaveAsPrefabAsset(instance, $"{BaseDir}/{instance.name}.prefab");
                Object.DestroyImmediate(instance);
                result.Add(model.name, prefab);
            }
            return result;
        }

        // The FBX-embedded materials have no MSA and a default 0.5 smoothness; project materials replace them by name.
        // Normal/MSA maps stay off until the texture importers are fixed (Normal = NormalMap, MSA = linear) — see handoff notes.
        private static Dictionary<string, Material> BuildModelMaterials()
        {
            var map = new Dictionary<string, Material>();
            void Add(string name, string baseColor, float smoothness)
            {
                var path = $"{MaterialDir}/{name}.mat";
                var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (mat == null)
                {
                    mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                    AssetDatabase.CreateAsset(mat, path);
                }
                mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{Root}/Textures/{baseColor}.png"));
                mat.SetColor("_BaseColor", Color.white);
                mat.SetFloat("_Metallic", 0f);
                mat.SetFloat("_Smoothness", smoothness);
                EditorUtility.SetDirty(mat);
                map.Add(name, mat);
            }
            Add("M_MarketProps", "T_MarketProps_BaseColor", 0.18f);
            Add("M_MarketFood", "T_MarketFood_BaseColor", 0.12f);
            Add("M_MarketCloth", "T_MarketCloth_BaseColor", 0.08f);
            Add("M_MarketCloth_Green", "T_MarketCloth_Green_BaseColor", 0.08f);
            return map;
        }

        // ---------- Groups ----------

        private static Dictionary<string, GameObject> BuildGroupPrefabs()
        {
            var groups = new Dictionary<string, GameObject>();
            void Group(string name, System.Action<Transform> fill)
            {
                var root = new GameObject(name);
                fill(root.transform);
                groups.Add(name, PrefabUtility.SaveAsPrefabAsset(root, $"{GroupDir}/{name}.prefab"));
                Object.DestroyImmediate(root);
            }

            Group("G_CrateStack", t =>
            {
                Place(t, "Crate_Tomato", new Vector3(-0.27f, 0f, 0f), 2f);
                Place(t, "Crate_Carrot", new Vector3(0.27f, 0f, 0.02f), -3f);
                Place(t, "Crate_AppleRed", new Vector3(0f, 0.33f, 0f), 6f);
            });
            Group("G_SackPile", t =>
            {
                Place(t, "Sack_Flour", new Vector3(-0.27f, 0f, 0f), 10f);
                Place(t, "Sack_Grain", new Vector3(0.27f, 0f, 0.03f), -8f);
                Place(t, "Sack_Groats", new Vector3(0f, 0.55f, 0f), 35f, tilt: 4f);
                Place(t, "Sack_Bundle", new Vector3(0.6f, 0f, -0.35f), -25f);
            });
            Group("G_HayStack", t =>
            {
                Place(t, "HayBale_1", new Vector3(0f, 0f, 0f), 0f);
                Place(t, "HayBale_1", new Vector3(0f, 0.44f, 0f), 180f);
                Place(t, "HayBale_2", new Vector3(1.05f, 0f, 0.1f), 12f);
            });
            Group("G_BarrelRow", t =>
            {
                Place(t, "Barrel_Standing", new Vector3(-0.7f, 0f, 0f), 0f);
                Place(t, "Barrel_Standing", new Vector3(0f, 0f, 0.05f), 40f);
                Place(t, "Barrel_Small", new Vector3(0.6f, 0f, -0.05f), 0f);
                Place(t, "Barrel_Small", new Vector3(0.35f, 0f, -0.55f), 70f);
            });
            Group("G_TableDisplay", t =>
            {
                Place(t, "Table_Cloth", Vector3.zero, 0f);
                Place(t, "Basket_Round", new Vector3(-0.35f, 0.8f, 0f), 0f);
                Place(t, "Crate_AppleGreen", new Vector3(0.3f, 0.8f, 0f), 4f);
                Place(t, "Scale_Weights", new Vector3(0.62f, 0.8f, -0.1f), -30f);
            });
            Group("G_StallFront", t =>
            {
                Place(t, "Crate_Pumpkin", new Vector3(-0.8f, 0f, -2.2f), 5f);
                Place(t, "Basket_Rect", new Vector3(-0.2f, 0f, -2.3f), -10f);
                Place(t, "Crate_Tomato", new Vector3(0.45f, 0f, -2.2f), 3f);
                Place(t, "Sack_Flour", new Vector3(1.0f, 0f, -2.15f), 30f);
            });
            Group("G_FarmCorner", t =>
            {
                Place(t, "Wheelbarrow", new Vector3(0f, 0f, 0f), 20f);
                Place(t, "Tool_Pitchfork", new Vector3(1.0f, 0.1f, 0.4f), 90f, tilt: -14f);
                Place(t, "Tool_Rake", new Vector3(1.3f, 0.1f, 0.25f), 85f, tilt: -16f);
                Place(t, "Tool_Shovel", new Vector3(1.6f, 0.1f, 0.4f), 95f, tilt: -12f);
            });
            Group("G_CartLoad", t =>
            {
                Place(t, "Cart", Vector3.zero, 0f);
                Place(t, "Sack_Flour", new Vector3(0f, 0.42f, -0.35f), 0f);
                Place(t, "Sack_Grain", new Vector3(0f, 0.42f, 0.25f), 20f);
                Place(t, "Crate_Carrot", new Vector3(0f, 0.42f, 0.8f), 90f);
            });
            Group("G_FenceRun", t =>
            {
                for (var i = 0; i < 4; i++) Place(t, "Fence_Straight", new Vector3(i * 2.16f, 0f, 0f), 0f);
            });
            return groups;
        }

        // ---------- Scene ----------

        private static void BuildScene()
        {
            var env = new GameObject("Environment").transform;
            var stalls = new GameObject("Stalls").transform;
            var props = new GameObject("Props").transform;
            var fences = new GameObject("Fences").transform;
            var lights = new GameObject("Lighting").transform;

            BuildGround(env);

            // Back row: four stalls, goods between them.
            foreach (var x in new[] { -9f, -3f, 3f, 9f }) Place(stalls, "StreetStall", new Vector3(x, 0f, 6f), 0f);
            foreach (var x in new[] { -9f, -3f, 3f, 9f }) PlaceGroup(props, "G_StallFront", new Vector3(x, 0f, 6f), 0f);
            PlaceGroup(props, "G_SackPile", new Vector3(-6f, 0f, 5.8f), -8f);
            PlaceGroup(props, "G_BarrelRow", new Vector3(0f, 0f, 6.2f), 0f);
            PlaceGroup(props, "G_CrateStack", new Vector3(6f, 0f, 5.8f), 6f);
            Place(props, "Sign_Chalkboard", new Vector3(-1.4f, 0f, 3.7f), -15f);
            Place(props, "Sign_Chalkboard", new Vector3(10.7f, 0f, 3.9f), 12f);

            // Left row: green canopy with a cloth table, facing the square (+X).
            Place(stalls, "Canopy_Green", new Vector3(-12f, 0f, 1.8f), -90f);
            PlaceGroup(props, "G_TableDisplay", new Vector3(-12f, 0f, 1.8f), -90f);
            Place(props, "Shelf_CheeseBread", new Vector3(-14.2f, 0f, 6.2f), -90f);

            // Right row: canopy + cart load.
            Place(stalls, "Canopy_Green", new Vector3(12f, 0f, 2.2f), 90f);
            PlaceGroup(props, "G_TableDisplay", new Vector3(12f, 0f, 2.2f), 90f);
            PlaceGroup(props, "G_CartLoad", new Vector3(11f, 0f, -3f), 70f);

            // Centre of the square.
            PlaceGroup(props, "G_CartLoad", new Vector3(0.5f, 0f, -0.5f), -28f);
            PlaceGroup(props, "G_CrateStack", new Vector3(-3.3f, 0f, 1.6f), -20f);
            PlaceGroup(props, "G_SackPile", new Vector3(3.6f, 0f, 2.4f), 25f);
            Place(props, "Basket_Round", new Vector3(-1.9f, 0f, 2.1f), 0f);
            Place(props, "Basket_Small", new Vector3(-1.5f, 0f, 1.7f), 40f);
            Place(props, "Barrel_Tap", new Vector3(4.6f, 0f, -2.2f), -100f);

            // Farm corner (front left).
            PlaceGroup(props, "G_FarmCorner", new Vector3(-12f, 0f, -3.2f), 0f);
            PlaceGroup(props, "G_HayStack", new Vector3(-8.6f, 0f, -4.8f), 15f);
            Place(props, "HayBale_Stack", new Vector3(-14.2f, 0f, -4.4f), 20f);

            // Seeded scatter of small goods so the square does not look staged.
            var rng = new System.Random(11);
            string[] small = { "Crate_Empty", "Crate_Tomato", "Crate_AppleGreen", "Crate_Pumpkin", "Basket_Round", "Basket_Small", "Basket_Rect", "Sack_Empty", "Sack_Bundle", "Barrel_Small" };
            foreach (var anchor in new[] { new Vector3(-8f, 0f, 2.2f), new Vector3(8f, 0f, 2.4f), new Vector3(-5f, 0f, -4f), new Vector3(5.5f, 0f, -4.2f), new Vector3(0f, 0f, -3f), new Vector3(-8.5f, 0f, -1.5f), new Vector3(8.5f, 0f, -1f) })
                for (var i = 0; i < 3; i++)
                {
                    var offset = new Vector3((float)(rng.NextDouble() - 0.5) * 2.4f, 0f, (float)(rng.NextDouble() - 0.5) * 2.0f);
                    Place(props, small[rng.Next(small.Length)], anchor + offset, rng.Next(360));
                }

            // Fences: back (behind stalls), sides, with a gate in the back centre.
            PlaceGroup(fences, "G_FenceRun", new Vector3(-17.3f, 0f, 9.5f), 0f);
            Place(fences, "Fence_Gate", new Vector3(0f, 0f, 9.5f), 0f);
            PlaceGroup(fences, "G_FenceRun", new Vector3(1.1f, 0f, 9.5f), 0f);
            PlaceGroup(fences, "G_FenceRun", new Vector3(9.8f, 0f, 9.5f), 0f);
            for (var i = 0; i < 8; i++)
            {
                Place(fences, "Fence_Straight", new Vector3(-16f, 0f, 8.4f - i * 2.16f), 90f);
                Place(fences, "Fence_Straight", new Vector3(16f, 0f, 8.4f - i * 2.16f), 90f);
            }

            // Front fence with an open entrance in the middle.
            for (var x = -15.3f; x < 16f; x += 2.16f)
            {
                if (Mathf.Abs(x) < 3.2f) continue;
                Place(fences, "Fence_Straight", new Vector3(x, 0f, -6.9f), 0f);
            }

            // Lanterns with warm point lights.
            foreach (var p in new[] { new Vector3(-6f, 0f, -2.5f), new Vector3(6f, 0f, -2.5f), new Vector3(-6f, 0f, 3.5f), new Vector3(6f, 0f, 3.5f) })
            {
                Place(lights, "LanternPost", p, 0f);
                var glow = new GameObject("LanternGlow");
                glow.transform.SetParent(lights, false);
                glow.transform.position = p + new Vector3(0f, 2.1f, 0f);
                var l = glow.AddComponent<Light>();
                l.type = LightType.Point;
                l.color = new Color(1f, 0.72f, 0.4f);
                l.intensity = 2.5f;
                l.range = 6f;
                l.shadows = LightShadows.None;
            }

            BuildScenery(env);
            BuildSunAndCamera();
            foreach (var t in new[] { env, stalls, props, fences, lights })
                foreach (var tr in t.GetComponentsInChildren<Transform>())
                    GameObjectUtility.SetStaticEditorFlags(tr.gameObject, StaticEditorFlags.BatchingStatic | StaticEditorFlags.ContributeGI | StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic);
        }

        private static void BuildGround(Transform parent)
        {
            var grass = GroundMaterial("M_Ground_Grass", new Color(0.30f, 0.46f, 0.20f), 0.10f, 80f);
            var dirt = GroundMaterial("M_Ground_Dirt", new Color(0.52f, 0.41f, 0.29f), 0.14f, 6f);

            var field = GameObject.CreatePrimitive(PrimitiveType.Plane);
            field.name = "Grass";
            field.transform.SetParent(parent, false);
            field.transform.localScale = new Vector3(40f, 1f, 40f);
            field.GetComponent<Renderer>().sharedMaterial = grass;

            var plaza = GameObject.CreatePrimitive(PrimitiveType.Cube);
            plaza.name = "Plaza";
            plaza.transform.SetParent(parent, false);
            plaza.transform.localPosition = new Vector3(0f, -0.02f, 1.5f);
            plaza.transform.localScale = new Vector3(32f, 0.06f, 17f);
            plaza.GetComponent<Renderer>().sharedMaterial = dirt;
        }

        private static Material GroundMaterial(string name, Color tint, float contrast, float tiling)
        {
            var texPath = $"{MaterialDir}/T_{name}.png";
            if (!File.Exists(texPath))
            {
                const int size = 256;
                var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
                var seed = (name.GetHashCode() & 0xFF) * 3.7f;
                for (var y = 0; y < size; y++)
                for (var x = 0; x < size; x++)
                {
                    var n = TileableNoise(seed, x, y, size, 5f) * 0.6f + TileableNoise(seed + 50f, x, y, size, 18f) * 0.4f;
                    var v = 1f + (n - 0.5f) * 2f * contrast * 3f;
                    tex.SetPixel(x, y, new Color(tint.r * v, tint.g * v, tint.b * v));
                }
                File.WriteAllBytes(texPath, tex.EncodeToPNG());
                Object.DestroyImmediate(tex);
                AssetDatabase.ImportAsset(texPath);
            }

            var matPath = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, matPath);
            }
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(texPath));
            mat.SetTextureScale("_BaseMap", new Vector2(tiling, tiling));
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Smoothness", 0.05f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ---------- Scenery (scene dressing only, not part of the asset pack) ----------

        private static void BuildScenery(Transform parent)
        {
            var scenery = new GameObject("Scenery").transform;
            scenery.SetParent(parent, false);

            var hill = FlatMaterial("M_Scenery_Hill", new Color(0.27f, 0.43f, 0.20f));
            foreach (var (pos, scale) in new[]
            {
                (new Vector3(-45f, -9f, 75f), new Vector3(110f, 40f, 60f)),
                (new Vector3(40f, -9f, 90f), new Vector3(120f, 46f, 60f)),
                (new Vector3(-85f, -9f, 15f), new Vector3(60f, 36f, 100f)),
                (new Vector3(85f, -9f, 20f), new Vector3(60f, 40f, 100f)),
                (new Vector3(0f, -9f, 120f), new Vector3(200f, 60f, 60f)),
            })
            {
                var h = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                h.name = "Hill";
                h.transform.SetParent(scenery, false);
                h.transform.localPosition = pos;
                h.transform.localScale = scale;
                h.GetComponent<Renderer>().sharedMaterial = hill;
                Object.DestroyImmediate(h.GetComponent<Collider>());
            }

            var dirt = AssetDatabase.LoadAssetAtPath<Material>($"{MaterialDir}/M_Ground_Dirt.mat");
            foreach (var (z, len) in new[] { (30f, 40f), (-27f, 40f) })
            {
                var road = GameObject.CreatePrimitive(PrimitiveType.Cube);
                road.name = "Road";
                road.transform.SetParent(scenery, false);
                road.transform.localPosition = new Vector3(0f, -0.03f, z);
                road.transform.localScale = new Vector3(5.5f, 0.05f, len);
                road.GetComponent<Renderer>().sharedMaterial = dirt;
                Object.DestroyImmediate(road.GetComponent<Collider>());
            }

            var trees = BuildTreePrefabs();
            var rng = new System.Random(5);
            var placed = 0;
            while (placed < 90)
            {
                var x = (float)(rng.NextDouble() * 120 - 60);
                var z = (float)(rng.NextDouble() * 70 - 28);
                var insideMarket = x > -24f && x < 24f && z > -14f && z < 26f;
                var onRoad = Mathf.Abs(x) < 4.5f;
                if (insideMarket || onRoad) continue;
                var tree = (GameObject)PrefabUtility.InstantiatePrefab(trees[rng.Next(trees.Length)], scenery);
                tree.transform.localPosition = new Vector3(x, 0f, z);
                tree.transform.localRotation = Quaternion.Euler(0f, rng.Next(360), 0f);
                tree.transform.localScale = Vector3.one * (0.8f + (float)rng.NextDouble() * 0.7f);
                placed++;
            }
        }

        private static GameObject[] BuildTreePrefabs()
        {
            var trunk = FlatMaterial("M_Scenery_Trunk", new Color(0.36f, 0.25f, 0.16f));
            var leaves = new[]
            {
                FlatMaterial("M_Scenery_LeafA", new Color(0.24f, 0.49f, 0.19f)),
                FlatMaterial("M_Scenery_LeafB", new Color(0.40f, 0.57f, 0.21f)),
                FlatMaterial("M_Scenery_LeafC", new Color(0.55f, 0.52f, 0.20f)),
            };
            var result = new GameObject[leaves.Length];
            for (var i = 0; i < leaves.Length; i++)
            {
                var root = new GameObject($"P_Scenery_Tree{(char)('A' + i)}");
                Part(root.transform, PrimitiveType.Cylinder, new Vector3(0f, 0.9f, 0f), new Vector3(0.38f, 0.9f, 0.38f), trunk);
                Part(root.transform, PrimitiveType.Sphere, new Vector3(0f, 2.7f, 0f), new Vector3(2.5f, 2.2f, 2.5f), leaves[i]);
                Part(root.transform, PrimitiveType.Sphere, new Vector3(0.35f, 3.7f, 0.1f), new Vector3(1.8f, 1.6f, 1.8f), leaves[i]);
                Part(root.transform, PrimitiveType.Sphere, new Vector3(-0.2f, 4.4f, -0.1f), new Vector3(1.1f, 1.0f, 1.1f), leaves[i]);
                result[i] = PrefabUtility.SaveAsPrefabAsset(root, $"{SceneryDir}/{root.name}.prefab");
                Object.DestroyImmediate(root);
            }
            return result;
        }

        private static void Part(Transform parent, PrimitiveType type, Vector3 pos, Vector3 scale, Material mat)
        {
            var go = GameObject.CreatePrimitive(type);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = mat;
            Object.DestroyImmediate(go.GetComponent<Collider>());
        }

        internal static Material FlatMaterial(string name, Color color, float smoothness = 0.1f)
        {
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", smoothness);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // Perlin noise blended across the seams so the texture tiles without visible edges.
        private static float TileableNoise(float seed, int x, int y, int size, float freq)
        {
            float N(float px, float py) => Mathf.PerlinNoise(seed + px / size * freq, seed + py / size * freq);
            float fx = (float)x / size, fy = (float)y / size;
            return N(x, y) * (1f - fx) * (1f - fy) + N(x - size, y) * fx * (1f - fy)
                 + N(x, y - size) * (1f - fx) * fy + N(x - size, y - size) * fx * fy;
        }

        private static void BuildSunAndCamera()
        {
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.94f, 0.82f);
            sun.intensity = 1.6f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(48f, -32f, 0f);
            RenderSettings.sun = sun;
            RenderSettings.skybox = AssetDatabase.GetBuiltinExtraResource<Material>("Default-Skybox.mat");
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.62f, 0.72f, 0.85f);
            RenderSettings.ambientEquatorColor = new Color(0.50f, 0.52f, 0.50f);
            RenderSettings.ambientGroundColor = new Color(0.30f, 0.27f, 0.22f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.74f, 0.82f, 0.90f);
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogStartDistance = 45f;
            RenderSettings.fogEndDistance = 160f;

            var volume = new GameObject("Global Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);

            var cam = new GameObject("Main Camera") { tag = "MainCamera" }.AddComponent<Camera>();
            cam.fieldOfView = 36f;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 200f;
            cam.transform.position = new Vector3(-12f, 8f, -13f);
            cam.transform.LookAt(new Vector3(0f, 0f, 2f));
            cam.gameObject.AddComponent<AudioListener>();
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
        }

        // ---------- Helpers ----------

        private static GameObject Place(Transform parent, string baseName, Vector3 pos, float yaw, float tilt = 0f)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(_bases[baseName], parent);
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.Euler(tilt, yaw, 0f);
            return go;
        }

        private static GameObject PlaceGroup(Transform parent, string groupName, Vector3 pos, float yaw)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(_groups[groupName], parent);
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            return go;
        }

        internal static void Shoot(string file, Vector3 pos, Vector3 target, float fov, int width = 1920, int height = 1080)
        {
            var cam = Camera.main;
            cam.transform.position = pos;
            cam.transform.LookAt(target);
            cam.fieldOfView = fov;

            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            File.WriteAllBytes(file, tex.EncodeToPNG());

            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
        }
    }
}
