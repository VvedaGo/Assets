using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FarmNature.Editor
{
    /// <summary>
    /// Builds Demo_FarmNature_Showcase.unity: six category islands (sheet 02 of NATURE_COMPOSITIONS),
    /// items laid out in rows from the back, left to right, numbered by catalogue order in object names.
    /// Idempotent: rebuilds the scene from prefabs.
    /// </summary>
    public static class FarmNatureShowcaseBuilder
    {
        private const string PrefabDir = "Assets/FarmNature/Art/Prefabs";
        private const string SceneDir = "Assets/FarmNature/Demo/Scenes";
        private const string MaterialDir = "Assets/FarmNature/Demo/Materials";
        private const float Gap = 0.5f;          // free edge around exhibits
        private const float Aisle = 4f;          // between islands (they float apart in the beauty render)
        private const float Margin = 0.05f;      // island border (compact islands, exhibits close to the edge like reference 02)
        private const float MaxRowWidth = 16f;
        private const float SlabHeight = 0.4f;

        private struct Island
        {
            public string Title;
            public string[][] Rows; // back row first; each item is a prefab name without the FMS_ prefix
            public float ItemGap;   // 0 = default Gap; wider for small items so number tags do not collide
            public float RowGap;    // extra depth between rows (tall trees hide the row behind at a 45 degree camera)
            public float MaxRow;    // 0 = default MaxRowWidth
        }

        private static readonly Island[] Islands =
        {
            new Island { Title = "Beds", Rows = new[]
            {
                new[] { "Bed_Row_Soil", "Bed_Raised_2x1", "Bed_Raised_1x1" },
                new[] { "Bed_Plot_4x4", "Bed_Trellis", "Bed_Stakes_Row" },
            } },
            new Island { Title = "Crops", ItemGap = 0.35f, Rows = new[]
            {
                new[] { "Crop_Wheat_S1", "Crop_Wheat_S2", "Crop_Wheat_S3" },
                new[] { "Crop_Corn_S1", "Crop_Corn_S2", "Crop_Corn_S3" },
                new[] { "Crop_Carrot_S1", "Crop_Carrot_S2", "Crop_Carrot_S3" },
                new[] { "Crop_Cabbage_S1", "Crop_Cabbage_S2", "Crop_Cabbage_S3" },
                new[] { "Crop_Tomato_S1", "Crop_Tomato_S2", "Crop_Tomato_S3" },
                new[] { "Crop_Pumpkin_S1", "Crop_Pumpkin_S2", "Crop_Pumpkin_S3" },
                new[] { "Crop_Sunflower_S1", "Crop_Sunflower_S2", "Crop_Sunflower_S3" },
                new[] { "Crop_WheatField_Green", "Crop_WheatField_Golden", "Crop_WheatField_Stubble" },
            } },
            new Island { Title = "Trees", ItemGap = 0.6f, RowGap = 2.5f, MaxRow = 30f, Rows = new[]
            {
                new[] { "Tree_Oak_L", "Tree_Oak_Autumn", "Tree_Birch", "Tree_Willow" },
                new[] { "Tree_Birch_S", "Tree_Spruce_L", "Tree_Spruce_S", "Tree_Apple_Fruit", "Tree_Apple_Blossom" },
            } },
            new Island { Title = "Plants", ItemGap = 0.45f, Rows = new[]
            {
                new[] { "Hedge_Straight", "Hedge_Corner", "Hedge_End", "Bush_Round", "Bush_Flowering", "Bush_Berry" },
                new[] { "Flower_Daisy", "Flower_Tulip", "Flower_Lavender", "Flower_Poppy", "Flower_Meadow" },
                new[] { "Grass_Tuft_S", "Grass_Tuft_M", "Grass_Tall", "Grass_Reeds", "Plant_Fern" },
            } },
            new Island { Title = "WaterRocks", ItemGap = 0.6f, Rows = new[]
            {
                new[] { "Water_Pond_Round", "Water_Pond_Oval", "Water_Puddle_Round", "Water_Puddle_Irregular" },
                new[] { "Water_Stream_Straight", "Water_Stream_Curve", "Water_Stream_End" }, // + bridge over the stream, lilies in the puddle (Dress)
                new[] { "Rock_S", "Rock_M", "Rock_L", "Rock_Flat", "Rock_Cluster", "Rock_Boulder" },
            } },
            new Island { Title = "Modules", ItemGap = 0.6f, Rows = new[]
            {
                new[] { "Path_Dirt_Straight", "Path_Dirt_Curve", "Path_Dirt_T", "Path_Dirt_End" },
                new[] { "Path_Stone_Straight", "Path_Stone_Curve", "Path_Stepping_Stones" },
                new[] { "Ground_Grass_4x4", "Ground_Dirt_4x4", "Ground_Edge" },
                new[] { "Ground_Corner_In", "Ground_Corner_Out", "Ground_Hill" },
                new[] { "Wood_Stump", "Wood_Log_Fallen", "Wood_Log", "Wood_Firewood_Stack", "Wood_Firewood_Pile" },
            } },
        };

        private const int Columns = 3;

        [MenuItem("Tools/Farm Nature/Build Showcase Scene")]
        public static void Build()
        {
            Directory.CreateDirectory(SceneDir);
            Directory.CreateDirectory(MaterialDir);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            // 1. lay out each island in its own local space
            var laid = Islands.Select(i => LayOut(i)).ToList();

            // 2. arrange islands on a grid with aisles; column width / row depth = max of members
            var rows = Mathf.CeilToInt(laid.Count / (float)Columns);
            var colW = new float[Columns];
            var rowD = new float[rows];
            for (var n = 0; n < laid.Count; n++)
            {
                colW[n % Columns] = Mathf.Max(colW[n % Columns], laid[n].Size.x);
                rowD[n / Columns] = Mathf.Max(rowD[n / Columns], laid[n].Size.y);
            }
            var totalW = colW.Sum() + Aisle * (Columns - 1);
            var totalD = rowD.Sum() + Aisle * (rows - 1);

            var root = new GameObject("FarmNature_Showcase").transform;
            for (var n = 0; n < laid.Count; n++)
            {
                var c = n % Columns;
                var r = n / Columns;
                var x = -totalW / 2 + colW.Take(c).Sum() + Aisle * c + colW[c] / 2;
                var z = totalD / 2 - rowD.Take(r).Sum() - Aisle * r - rowD[r] / 2; // row 0 at the back
                var island = laid[n];
                island.Root.SetParent(root, false);
                island.Root.localPosition = new Vector3(x, 0, z);

                // compact island sized to its exhibits (reference sheet 02), dressed like the reference, then grass + tufts
                Dress(island.Root, Islands[n].Title);
                FarmNatureCompositionBuilder.DecorateShowcaseIsland(island.Root, island.Size, n + 1);
            }

            ConfigureLightAndCamera(totalW, totalD);

            FarmNatureCompositionBuilder.BuildIntoOpenScene(); // compositions live in the same scene

            var scenePath = $"{SceneDir}/Demo_FarmNature_Showcase.unity";
            EditorSceneManager.SaveScene(scene, scenePath);
            RenderShot(Path.Combine(Path.GetTempPath(), "FarmNature_Showcase.png"));
            Debug.Log($"[FarmNature] showcase built: {laid.Sum(l => l.Count)} items, {totalW:F1}x{totalD:F1} m -> {scenePath}");
        }

        private struct LaidIsland
        {
            public Transform Root;
            public Vector2 Size;
            public int Count;
        }

        private static LaidIsland LayOut(Island island)
        {
            var root = new GameObject("Island_" + island.Title).transform;

            var Gap = island.ItemGap > 0 ? island.ItemGap : FarmNatureShowcaseBuilder.Gap;
            var MaxRowWidth = island.MaxRow > 0 ? island.MaxRow : FarmNatureShowcaseBuilder.MaxRowWidth;
            var rowGap = Gap + island.RowGap;
            // measure + wrap rows that exceed MaxRowWidth
            var lines = new List<List<(string Name, GameObject Go, Bounds B)>>();
            foreach (var row in island.Rows)
            {
                var line = new List<(string, GameObject, Bounds)>();
                var width = 0f;
                foreach (var name in row)
                {
                    var go = Instantiate(name);
                    if (name.StartsWith("Crop_Sunflower")) go.transform.rotation = Quaternion.Euler(0, 180, 0); // heads face +Z
                    var b = WorldBounds(go);
                    if (line.Count > 0 && width + Gap + b.size.x > MaxRowWidth)
                    {
                        lines.Add(line);
                        line = new List<(string, GameObject, Bounds)>();
                        width = 0;
                    }
                    width += (line.Count > 0 ? Gap : 0) + b.size.x;
                    line.Add((name, go, b));
                }
                lines.Add(line);
            }

            float LineWidth(List<(string Name, GameObject Go, Bounds B)> l) => l.Sum(i => i.B.size.x) + Gap * (l.Count - 1);
            float LineDepth(List<(string Name, GameObject Go, Bounds B)> l) => l.Max(i => i.B.size.z);

            var contentW = lines.Max(LineWidth);
            var contentD = lines.Sum(LineDepth) + rowGap * (lines.Count - 1);
            var size = new Vector2(contentW + 2 * (Margin + Gap), contentD + 2 * (Margin + Gap));

            var z = contentD / 2;
            var number = 0;
            foreach (var line in lines)
            {
                var depth = LineDepth(line);
                var x = -LineWidth(line) / 2;
                foreach (var (name, go, b) in line)
                {
                    number++;
                    go.name = $"{number:00}_{name}";
                    go.transform.SetParent(root, false);
                    // centre footprint on the cell, keep pivot on the ground
                    go.transform.localPosition = new Vector3(x + b.size.x / 2 - b.center.x, 0, z - depth / 2 - b.center.z);
                    x += b.size.x + Gap;
                }
                z -= depth + rowGap;
            }
            return new LaidIsland { Root = root, Size = size, Count = number };
        }

        /// <summary>Reference-style dressing: crops on soil strips, wheat on the ploughed plot, bridge over the stream, lilies in the puddle.</summary>
        private static void Dress(Transform island, string title)
        {
            var items = island.Cast<Transform>().ToList();
            Transform Item(string n) => items.First(t => t.name.EndsWith("_" + n));

            if (title == "Crops")
            {
                foreach (var row in items.Where(t => !t.name.Contains("WheatField")).GroupBy(t => t.name.Split('_')[2]))
                {
                    var bounds = row.Select(t => t.GetComponentsInChildren<Renderer>().Select(r => r.bounds).Aggregate((a, b) => { a.Encapsulate(b); return a; })).ToList();
                    var x0 = bounds.Min(b => b.min.x) - island.position.x - 0.3f;
                    var x1 = bounds.Max(b => b.max.x) - island.position.x + 0.3f;
                    var z = row.Average(t => t.localPosition.z);
                    FarmNatureCompositionBuilder.MakeSoilStrip(island, new Rect(x0, z - 0.32f, x1 - x0, 0.64f), 0.05f);
                    foreach (var t in row) t.localPosition += Vector3.up * 0.04f;
                }
            }
            if (title == "Beds")
            {
                // wheat growing on the ploughed plot: 5 ridges x 4, height from the plot surface
                var plot = Item("Bed_Plot_4x4");
                var mc = plot.GetComponentInChildren<MeshFilter>().gameObject.AddComponent<MeshCollider>();
                Physics.SyncTransforms();
                var rnd = new System.Random(3);
                for (var i = 0; i < 5; i++)
                    for (var j = 0; j < 4; j++)
                    {
                        var p = plot.position + new Vector3(-1.6f + i * 0.8f, 0, -1.2f + j * 0.8f);
                        var y = mc.Raycast(new Ray(p + Vector3.up * 3, Vector3.down), out var hit, 6f) ? hit.point.y : plot.position.y + 0.3f;
                        var w = Instantiate("Crop_Wheat_S3");
                        w.transform.SetParent(plot, true);
                        w.transform.position = new Vector3(p.x, y - 0.02f, p.z);
                        w.transform.rotation = Quaternion.Euler(0, (float)rnd.NextDouble() * 360, 0);
                        w.transform.localScale = Vector3.one * 0.85f;
                    }
                Object.DestroyImmediate(mc);
            }
            if (title == "Plants")
            {
                // flowers and small grass shown as clumps of three (like the flower patches on the reference)
                var rnd = new System.Random(11);
                foreach (var t in items.Where(t => t.name.Contains("_Flower_") || t.name.Contains("_Grass_Tuft_")))
                {
                    var name = System.Text.RegularExpressions.Regex.Replace(t.name, @"^\d\d_", "");
                    var spread = t.GetComponentsInChildren<Renderer>()[0].bounds.size.x * 0.55f;
                    for (var k = 0; k < 2; k++)
                    {
                        var extra = Instantiate(name);
                        extra.transform.SetParent(t, false);
                        var a = (k * 150 + 60 + rnd.Next(40)) * Mathf.Deg2Rad;
                        extra.transform.localPosition = new Vector3(Mathf.Cos(a) * spread, 0, Mathf.Sin(a) * spread);
                        extra.transform.localRotation = Quaternion.Euler(0, rnd.Next(360), 0);
                        extra.transform.localScale = Vector3.one * (0.8f + 0.2f * (float)rnd.NextDouble());
                    }
                }
            }
            if (title == "WaterRocks")
            {
                var stream = Item("Water_Stream_Straight");
                var bridge = Instantiate("Water_Bridge_Wood");
                bridge.transform.SetParent(stream, false);
                bridge.transform.localPosition = new Vector3(0, 0.30f, 0);   // stream gets sunk 0.30, the bridge stays on the grass
                bridge.transform.localRotation = Quaternion.Euler(0, 90, 0); // spans across the stream
                var puddle = Item("Water_Puddle_Irregular");
                var lily = Instantiate("Water_LilyPads");
                lily.transform.SetParent(puddle, false);
                lily.transform.localPosition = new Vector3(0, 0.03f, 0);
                lily.transform.localScale = Vector3.one * 0.9f;
            }
        }

        private static GameObject Instantiate(string name)
        {
            var category = name.Split('_')[0];
            var path = $"{PrefabDir}/{category}/FMS_{name}.prefab";
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            return (GameObject)PrefabUtility.InstantiatePrefab(prefab);
        }

        private static Bounds WorldBounds(GameObject go)
        {
            var renderers = go.GetComponentsInChildren<Renderer>();
            var b = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) b.Encapsulate(r.bounds);
            return b;
        }

        private static void ConfigureLightAndCamera(float totalW, float totalD)
        {
            var light = GameObject.Find("Directional Light").GetComponent<Light>();
            light.transform.rotation = Quaternion.Euler(50, 35, 0); // from top-left-back, like the reference renders
            light.color = new Color(1f, 0.96f, 0.88f);
            light.shadows = LightShadows.Soft;

            var cam = Camera.main;
            cam.orthographic = true;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.96f, 0.92f, 0.84f);
            cam.transform.rotation = Quaternion.Euler(42, 0, 0);
            var extent = Mathf.Max(totalW / 2 / cam.aspect, totalD / 2 * Mathf.Sin(42 * Mathf.Deg2Rad) + 4);
            cam.orthographicSize = extent * 1.08f;
            cam.transform.position = new Vector3(0, 2, 0) - cam.transform.forward * 150f;
            cam.nearClipPlane = 1;
            cam.farClipPlane = 400;
        }

        private static void RenderShot(string path)
        {
            var cam = Camera.main;
            var rt = new RenderTexture(1920, 1080, 24);
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            File.WriteAllBytes(path, tex.EncodeToPNG());
            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
        }

        private static Material LoadOrCreateMaterial(string name, Color color)
        {
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", 0.05f);
            EditorUtility.SetDirty(mat);
            return mat;
        }
    }
}
