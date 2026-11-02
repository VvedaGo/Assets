using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using FarmMarketStarter.Demo;
using Random = System.Random;

namespace FarmMarketStarter.Editor
{
    /// <summary>Builds materials, single-item prefabs, the vegetable-stand composition and Demo_Lite_Showcase. Idempotent.</summary>
    public static class FMS_LiteDemoBuilder
    {
        private const string Root = "Assets/FarmMarketStarter";
        private const string ModelDir = Root + "/Art/Models";
        private const string MaterialDir = Root + "/Art/Materials";
        private const string SingleDir = Root + "/Art/Prefabs/Single";
        private const string CompositionDir = Root + "/Art/Prefabs/Compositions";
        private const string DemoTextureDir = Root + "/Demo/Textures";
        private const string DemoSettingsDir = Root + "/Demo/Settings";
        private const string ScenePath = Root + "/Demo/Scenes/Demo_Lite_Showcase.unity";

        private static readonly Dictionary<string, string> PrefabByModel = new Dictionary<string, string>();
        private static readonly Dictionary<string, Material> MaterialCache = new Dictionary<string, Material>();
        private static Random _rng;

        [MenuItem("Tools/Farm Market Starter/Build Lite Demo")]
        public static void Build()
        {
            foreach (var dir in new[] { MaterialDir, SingleDir, CompositionDir, DemoTextureDir, DemoSettingsDir, Path.GetDirectoryName(ScenePath) })
                Directory.CreateDirectory(dir);
            _rng = new Random(7);
            PrefabByModel.Clear();
            MaterialCache.Clear();

            BuildSinglePrefabs();
            var stand = BuildVegetableStandComposition();
            BuildScene(stand);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[FarmMarketStarter] built {PrefabByModel.Count} prefabs + composition + scene {ScenePath}");
        }

        // ---------- Single prefabs ----------

        private static void BuildSinglePrefabs()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { ModelDir }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var category = Path.GetFileName(Path.GetDirectoryName(path));
                var prefabName = PrefabName(category, model.name);

                var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
                PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                instance.name = prefabName;

                var bounds = new Bounds();
                var first = true;
                foreach (var r in instance.GetComponentsInChildren<Renderer>(true))
                {
                    r.sharedMaterials = r.sharedMaterials.Select(UrpMaterial).ToArray();
                    if (first) { bounds = r.bounds; first = false; } else bounds.Encapsulate(r.bounds);
                }
                var box = instance.AddComponent<BoxCollider>();
                box.center = bounds.center;
                box.size = bounds.size;

                var prefab = PrefabUtility.SaveAsPrefabAsset(instance, $"{SingleDir}/{prefabName}.prefab");
                Object.DestroyImmediate(instance);
                PrefabByModel[model.name] = AssetDatabase.GetAssetPath(prefab);
            }
        }

        // FMS_<Category>_<Name>_<Variant>
        private static string PrefabName(string category, string modelName)
        {
            var raw = modelName.ToLowerInvariant().Replace("item_produce_", "").Replace("item_stalls_", "").Replace("_v2", "");
            var tokens = raw.Split('_').ToList();
            if (tokens.Count > 1 && tokens[0] == category.ToLowerInvariant()) tokens.RemoveAt(0);
            var cased = tokens.Select(t => CultureInfo.InvariantCulture.TextInfo.ToTitleCase(t));
            return $"FMS_{category}_{string.Join("_", cased)}";
        }

        private static Material UrpMaterial(Material source)
        {
            if (MaterialCache.TryGetValue(source.name, out var cached)) return cached;
            var path = $"{MaterialDir}/{source.name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", source.mainTexture);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", 0.15f);
            EditorUtility.SetDirty(mat);
            MaterialCache[source.name] = mat;
            return mat;
        }

        // ---------- Placement helpers ----------

        private static GameObject Spawn(Transform parent, string model, Vector3 pos, float yaw = 0f, float scale = 1f)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabByModel[model]);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            var box = prefab.GetComponent<BoxCollider>();
            var minY = (box.center.y - box.size.y * 0.5f) * scale;
            if (Mathf.Abs(minY) > 0.003f) pos.y -= minY;
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            go.transform.localScale = Vector3.one * scale;
            return go;
        }

        // Everything faces one point: the demo camera. Objects are placed on an arc around it.
        private static readonly Vector3 CamGround = new Vector3(1.0f, 0f, -4.2f);

        private static void OnArc(Transform t, float angleDeg, float radius, bool frontIsMinusZ = true)
        {
            var a = angleDeg * Mathf.Deg2Rad;
            var pos = CamGround + new Vector3(Mathf.Sin(a) * radius, 0f, Mathf.Cos(a) * radius);
            var d = CamGround - pos;
            d.y = 0f;
            d.Normalize();
            var yaw = frontIsMinusZ ? Mathf.Atan2(-d.x, -d.z) : Mathf.Atan2(d.x, d.z);
            t.SetPositionAndRotation(pos, Quaternion.Euler(0f, yaw * Mathf.Rad2Deg, 0f));
        }

        private static float Rand(float range) => ((float)_rng.NextDouble() * 2f - 1f) * range;

        /// <summary>Fills a nx*nz grid centred on origin; skips cells outside maxRadius (use for round containers).</summary>
        private static void Grid(Transform parent, string model, Vector3 origin, int nx, int nz, float dx, float dz,
            float jitter, float yawRange, float maxRadius = float.MaxValue, float scale = 1f)
        {
            for (var ix = 0; ix < nx; ix++)
            for (var iz = 0; iz < nz; iz++)
            {
                var ox = (ix - (nx - 1) * 0.5f) * dx + Rand(jitter);
                var oz = (iz - (nz - 1) * 0.5f) * dz + Rand(jitter);
                if (new Vector2(ox, oz).magnitude > maxRadius) continue;
                Spawn(parent, model, origin + new Vector3(ox, 0f, oz), Rand(yawRange) + (yawRange > 90f ? 180f : 0f), scale);
            }
        }

        // ---------- Composition: vegetable stand ----------

        private const float Top = 0.80f;      // table-top height
        private const float Facing = 180f;    // signs/boards are modelled facing +Z; the camera looks from -Z

        private static GameObject BuildVegetableStandComposition()
        {
            var root = new GameObject("FMS_Comp_VegetableStand").transform;

            Spawn(root, "item_stalls_table_canopy", Vector3.zero);

            // The table top is only ~0.37 m deep, so everything sits in one row on z = 0.
            // the one crate: tomatoes
            var tomatoCrate = new Vector3(-0.6f, Top, 0f);
            Spawn(root, "item_stalls_crate_framed_open", tomatoCrate);
            HeapGrid(root, "Tomato_Whole", tomatoCrate, 4, 0.085f, 0.12f, 0.07f, 4);

            // apples in a large basket
            var basket = new Vector3(-0.08f, Top, 0f);
            Spawn(root, "item_stalls_basket_large_v2", basket);
            HeapGrid(root, "item_produce_apple", basket, 3, 0.1f, 0.2f, 0.08f, 3, 0.14f);

            // one tomato slice, then scale + weights on the right
            Spawn(root, "Tomato_Half", new Vector3(-0.32f, Top, 0f), 0f);
            Spawn(root, "item_stalls_scale", new Vector3(0.44f, Top, 0f), 0f);
            Spawn(root, "item_stalls_weights", new Vector3(0.2f, Top, 0f), 0f);

            // price signs on their own feet beside the stall
            Spawn(root, "item_stalls_signs_hanging", new Vector3(1.25f, 0f, -0.55f), Facing);

            var prefab = PrefabUtility.SaveAsPrefabAsset(root.gameObject, $"{CompositionDir}/FMS_Comp_VegetableStand.prefab");
            Object.DestroyImmediate(root.gameObject);
            return prefab;
        }

        /// <summary>Stacked square layers (n x n, then n-1 x n-1 ...) forming a neat heap; optional radius clip for round baskets.</summary>
        private static void HeapGrid(Transform parent, string model, Vector3 origin, int n, float spacing, float y0, float layerStep,
            int layers, float maxRadius = float.MaxValue)
        {
            for (var l = 0; l < layers; l++)
            {
                var count = Mathf.Max(1, n - l);
                Grid(parent, model, origin + new Vector3(0f, y0 + l * layerStep, 0f), count, count, spacing, spacing, 0.004f, 180f, maxRadius);
            }
        }

        // ---------- Scene ----------

        private static void BuildScene(GameObject stand)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var world = new GameObject("World").transform;
            BuildGround(world);
            BuildEnvironment(world);

            var market = new GameObject("Market").transform;
            OnArc(((GameObject)PrefabUtility.InstantiatePrefab(stand, market)).transform, 0f, 6.3f);

            BuildFruitTable(market);
            BuildCart(market);
            BuildGroundProps(market);
            BuildGallery(market);

            BuildLighting();
            BuildCamera();

            EditorSceneManager.SaveScene(scene, ScenePath);
            var scenes = EditorBuildSettings.scenes.ToList();
            if (scenes.All(s => s.path != ScenePath))
            {
                scenes.Add(new EditorBuildSettingsScene(ScenePath, true));
                EditorBuildSettings.scenes = scenes.ToArray();
            }
        }

        private static void BuildFruitTable(Transform parent)
        {
            var g = new GameObject("Stall_Fruit").transform;
            g.SetParent(parent, false);
            OnArc(g, -21f, 6.6f);

            Spawn(g, "item_stalls_table_canopy", Vector3.zero);
            // one row on z = 0 (the table top is ~0.37 m deep), laid out left to right
            Spawn(g, "item_produce_pumpkin", new Vector3(-0.62f, Top, 0f), 0f);
            Spawn(g, "Cabbage", new Vector3(-0.28f, Top, 0f), 0f);
            Spawn(g, "item_produce_watermelon", new Vector3(0.02f, Top, 0f), 0f);
            Spawn(g, "item_stalls_basket_small_v2", new Vector3(0.34f, Top, 0f), 0f);
            HeapGrid(g, "Potato", new Vector3(0.34f, Top, 0f), 2, 0.07f, 0.12f, 0.07f, 2);
            Spawn(g, "Carrot", new Vector3(0.68f, Top, 0f), 0f);
        }

        private static void BuildCart(Transform parent)
        {
            var g = new GameObject("Cart").transform;
            g.SetParent(parent, false);
            OnArc(g, 22f, 6.2f);
            const float floor = 0.56f;

            Spawn(g, "item_stalls_cart_empty", Vector3.zero);
            Spawn(g, "item_produce_watermelon", new Vector3(0f, floor, -0.45f), 0f);
            Spawn(g, "item_produce_pumpkin", new Vector3(0f, floor, -0.15f), 0f);
            Spawn(g, "Cabbage", new Vector3(0f, floor, 0.08f), 0f);
        }

        private static void BuildGroundProps(Transform parent)
        {
            var g = new GameObject("GroundProps").transform;
            g.SetParent(parent, false);

            // a single chalkboard in front of the main stall
            OnArc(Spawn(g, "item_stalls_signboard_chalk", Vector3.zero, 0f, 0.7f).transform, 6f, 4.7f, false);
        }

        // ---------- Gallery: one of every item on a grid, off to the side of the main shot ----------

        private static readonly Vector3 GalleryCenter = new Vector3(17f, 0f, 2f);
        private static Transform _galleryTarget;

        private static bool InGallery(Vector3 p) => Mathf.Abs(p.x - GalleryCenter.x) < 10.5f && Mathf.Abs(p.z - GalleryCenter.z) < 8f;

        // Row 0 is closest to the camera: small produce first, big stalls last.
        private static int GalleryRow(string name)
        {
            if (name.Contains("_Veg_") || name.Contains("_Fruit_")) return 0;
            if (name.Contains("_Crate_") || name.Contains("_Scale") || name.Contains("_Weights")) return 1;
            if (name.Contains("_Deco_") || name.Contains("_Cart")) return 2;
            return 3;
        }

        private static void BuildGallery(Transform parent)
        {
            const float gap = 0.12f;
            const float rowGap = 0.3f;
            const float floorTop = 0.02f;

            var g = new GameObject("Gallery").transform;
            g.SetParent(parent, false);
            g.position = GalleryCenter;

            var rows = AssetDatabase.FindAssets("t:Prefab", new[] { SingleDir })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<GameObject>)
                .GroupBy(x => GalleryRow(x.name))
                .OrderBy(x => x.Key)
                .Select(x => x.OrderBy(i => i.name).ToList())
                .ToList();

            float Footprint(GameObject prefab, bool turned, out float depth)
            {
                var size = prefab.GetComponent<BoxCollider>().size;
                depth = size.z;
                return turned ? size.z : size.x;
            }

            // measure
            var rowWidths = new List<float>();
            var rowDepths = new List<float>();
            foreach (var row in rows)
            {
                float width = 0f, maxDepth = 0f;
                foreach (var prefab in row)
                {
                    width += Footprint(prefab, false, out var d) + gap;
                    maxDepth = Mathf.Max(maxDepth, d);
                }
                rowWidths.Add(width - gap);
                rowDepths.Add(maxDepth);
            }
            var totalDepth = rowDepths.Sum() + rowGap * (rows.Count - 1);
            var totalWidth = rowWidths.Max();

            // one continuous floor under everything
            var slab = GameObject.CreatePrimitive(PrimitiveType.Cube);
            slab.name = "Gallery_Floor";
            Object.DestroyImmediate(slab.GetComponent<Collider>());
            slab.transform.SetParent(g, false);
            slab.transform.localPosition = new Vector3(0f, floorTop * 0.5f, 0f);
            slab.transform.localScale = new Vector3(totalWidth + 1.2f, floorTop, totalDepth + 1.2f);
            slab.GetComponent<MeshRenderer>().sharedMaterial = DemoMaterial("M_Demo_Planks", PlankTexture(), 2.5f);

            // place rows front (-Z) to back (+Z), each row centred and packed
            var z = -totalDepth * 0.5f;
            for (var r = 0; r < rows.Count; r++)
            {
                var x = -rowWidths[r] * 0.5f;
                var rowCenterZ = z + rowDepths[r] * 0.5f;
                foreach (var prefab in rows[r])
                {
                    var box = prefab.GetComponent<BoxCollider>();
                    var w = box.size.x;
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, g);
                    var faceBack = prefab.name.Contains("Signboard") || prefab.name.Contains("Signs_Hanging");
                    var minY = box.center.y - box.size.y * 0.5f;
                    // place by the collider centre so items are packed by their real footprint
                    var sign = faceBack ? -1f : 1f; // a 180-degree turn mirrors the collider centre
                    var local = new Vector3(x + w * 0.5f - sign * box.center.x, floorTop - minY, rowCenterZ - sign * box.center.z);
                    go.transform.localPosition = local;
                    go.transform.localRotation = Quaternion.Euler(0f, faceBack ? 180f : 0f, 0f);
                    x += w + gap;
                }
                z += rowDepths[r] + rowGap;
            }

            _galleryTarget = new GameObject("GalleryTarget").transform;
            _galleryTarget.SetParent(g, false);
            _galleryTarget.localPosition = new Vector3(0f, 0.3f, 0f);
        }

        // ---------- Environment ----------

        private static void BuildGround(Transform parent)
        {
            var grass = DemoMaterial("M_Demo_Grass", GrassTexture(), 30f);
            var dirt = DemoMaterial("M_Demo_Dirt", NoiseTexture("T_Demo_Dirt", new Color(0.55f, 0.43f, 0.29f), new Color(0.46f, 0.36f, 0.24f), 4f), 6f);
            var cobble = DemoMaterial("M_Demo_Cobble", CobbleTexture(), 5f);
            cobble.SetFloat("_Smoothness", 0.12f);

            var plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
            plane.name = "Ground";
            plane.transform.SetParent(parent, false);
            plane.transform.localScale = new Vector3(10f, 1f, 10f);
            plane.GetComponent<MeshRenderer>().sharedMaterial = grass;

            // worn earth ring that blends the cobbles into the grass
            var ring = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ring.name = "Plaza_Earth";
            ring.transform.SetParent(parent, false);
            ring.transform.localPosition = new Vector3(0f, 0.003f, 1.2f);
            ring.transform.localScale = new Vector3(13f, 0.003f, 10f);
            Object.DestroyImmediate(ring.GetComponent<Collider>());
            ring.GetComponent<MeshRenderer>().sharedMaterial = dirt;

            var plaza = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            plaza.name = "Plaza_Cobble";
            plaza.transform.SetParent(parent, false);
            plaza.transform.localPosition = new Vector3(0f, 0.012f, 1.2f);
            plaza.transform.localScale = new Vector3(10.4f, 0.012f, 7.8f);
            Object.DestroyImmediate(plaza.GetComponent<Collider>());
            plaza.GetComponent<MeshRenderer>().sharedMaterial = cobble;

            ScatterGrass(parent);
        }

        // ---------- Grass tufts + flowers (combined meshes, a handful of draw calls) ----------

        private static bool InPlaza(float x, float z) => Mathf.Pow(x / 6.7f, 2f) + Mathf.Pow((z - 1.2f) / 5.2f, 2f) < 1f;
        private static bool InGalleryFloor(float x, float z) => Mathf.Abs(x - GalleryCenter.x) < 4.2f && Mathf.Abs(z - GalleryCenter.z) < 3.8f;

        private sealed class MeshBuilder
        {
            public readonly List<Vector3> Verts = new List<Vector3>();
            public readonly List<Vector3> Normals = new List<Vector3>();
            public readonly List<Vector2> Uvs = new List<Vector2>();
            public readonly List<int> Tris = new List<int>();

            public void Blade(Vector3 basePos, float yaw, float height, float width, float lean)
            {
                var dir = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));
                var side = new Vector3(Mathf.Cos(yaw), 0f, -Mathf.Sin(yaw));
                var mid = basePos + Vector3.up * height * 0.55f + dir * lean * 0.4f;
                var start = Verts.Count;
                Verts.Add(basePos - side * width * 0.5f);
                Verts.Add(basePos + side * width * 0.5f);
                Verts.Add(mid + side * width * 0.35f);
                Verts.Add(mid - side * width * 0.35f);
                Verts.Add(basePos + Vector3.up * height + dir * lean);
                for (var i = 0; i < 5; i++) Normals.Add(Vector3.up);
                Uvs.Add(new Vector2(0f, 0f)); Uvs.Add(new Vector2(1f, 0f)); Uvs.Add(new Vector2(1f, 0.55f));
                Uvs.Add(new Vector2(0f, 0.55f)); Uvs.Add(new Vector2(0.5f, 1f));
                Tris.AddRange(new[] { start, start + 3, start + 2, start, start + 2, start + 1, start + 3, start + 4, start + 2 });
            }

            public void Head(Vector3 center, float r)
            {
                var start = Verts.Count;
                Verts.Add(center + Vector3.up * r * 0.7f);
                Verts.Add(center - Vector3.up * r * 0.5f);
                Verts.Add(center + Vector3.right * r);
                Verts.Add(center + Vector3.forward * r);
                Verts.Add(center - Vector3.right * r);
                Verts.Add(center - Vector3.forward * r);
                for (var i = 0; i < 6; i++) { Normals.Add(Vector3.up); Uvs.Add(Vector2.zero); }
                for (var i = 0; i < 4; i++)
                {
                    var a = start + 2 + i;
                    var b = start + 2 + (i + 1) % 4;
                    Tris.AddRange(new[] { start, b, a, start + 1, a, b });
                }
            }

            public Mesh ToMesh(string name)
            {
                var mesh = new Mesh { name = name, indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
                mesh.SetVertices(Verts);
                mesh.SetNormals(Normals);
                mesh.SetUVs(0, Uvs);
                mesh.SetTriangles(Tris, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }

        private static void ScatterGrass(Transform parent)
        {
            var rng = new Random(99);
            const string meshDir = Root + "/Demo/Meshes";
            Directory.CreateDirectory(meshDir);

            var grassBuilders = new[] { new MeshBuilder(), new MeshBuilder(), new MeshBuilder() };
            var flowerColors = new[]
            {
                new Color(0.96f, 0.96f, 0.92f), new Color(0.98f, 0.82f, 0.25f),
                new Color(0.93f, 0.45f, 0.58f), new Color(0.62f, 0.45f, 0.85f)
            };
            var flowerBuilders = flowerColors.Select(_ => new MeshBuilder()).ToArray();

            float R() => (float)rng.NextDouble();
            bool Sample(float maxR, out float x, out float z)
            {
                for (var tries = 0; tries < 20; tries++)
                {
                    var angle = R() * Mathf.PI * 2f;
                    var radius = Mathf.Sqrt(R()) * maxR;
                    x = 1f + Mathf.Cos(angle) * radius * 1.15f;
                    z = 2f + Mathf.Sin(angle) * radius * 0.9f;
                    if (!InPlaza(x, z) && !InGalleryFloor(x, z)) return true;
                }
                x = z = 0f;
                return false;
            }

            for (var i = 0; i < 3600; i++)
            {
                if (!Sample(26f, out var x, out var z)) continue;
                var builder = grassBuilders[i % 3];
                var scale = 0.8f + R() * 0.7f;
                var blades = 5 + rng.Next(3);
                for (var b = 0; b < blades; b++)
                {
                    var offset = new Vector3((R() - 0.5f) * 0.14f, 0f, (R() - 0.5f) * 0.14f);
                    builder.Blade(new Vector3(x, 0f, z) + offset, R() * Mathf.PI * 2f, (0.12f + R() * 0.14f) * scale,
                        0.03f + R() * 0.02f, 0.03f + R() * 0.07f);
                }
            }

            for (var i = 0; i < 420; i++)
            {
                if (!Sample(22f, out var x, out var z)) continue;
                var height = 0.16f + R() * 0.1f;
                grassBuilders[0].Blade(new Vector3(x, 0f, z), R() * Mathf.PI * 2f, height, 0.018f, 0.01f);
                flowerBuilders[rng.Next(flowerBuilders.Length)].Head(new Vector3(x, height + 0.01f, z), 0.03f + R() * 0.02f);
            }

            var grassGreens = new[] { new Color(0.30f, 0.50f, 0.16f), new Color(0.38f, 0.58f, 0.20f), new Color(0.46f, 0.66f, 0.25f) };
            var holder = new GameObject("Grass_And_Flowers").transform;
            holder.SetParent(parent, false);

            void Emit(MeshBuilder builder, string name, Material mat)
            {
                if (builder.Verts.Count == 0) return;
                var path = $"{meshDir}/{name}.asset";
                AssetDatabase.DeleteAsset(path);
                var mesh = builder.ToMesh(name);
                AssetDatabase.CreateAsset(mesh, path);
                var go = new GameObject(name);
                go.transform.SetParent(holder, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = mat;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            }

            for (var i = 0; i < grassBuilders.Length; i++)
            {
                var mat = SolidMaterial($"M_Demo_Grass_{i}", grassGreens[i]);
                mat.SetFloat("_Cull", 0f);
                EditorUtility.SetDirty(mat);
                Emit(grassBuilders[i], $"Grass_{i}", mat);
            }
            for (var i = 0; i < flowerBuilders.Length; i++)
                Emit(flowerBuilders[i], $"Flowers_{i}", SolidMaterial($"M_Demo_Flower_{i}", flowerColors[i]));
        }

        // Demo-only scenery (primitives, not part of the pack)
        private static void BuildEnvironment(Transform parent)
        {
            var env = new GameObject("Demo_Environment (not in pack)").transform;
            env.SetParent(parent, false);
            var trunk = SolidMaterial("M_Demo_Trunk", new Color(0.36f, 0.25f, 0.16f));
            var leafA = SolidMaterial("M_Demo_LeafA", new Color(0.30f, 0.50f, 0.22f));
            var leafB = SolidMaterial("M_Demo_LeafB", new Color(0.38f, 0.56f, 0.24f));
            var rng = new Random(21);

            for (var i = 0; i < 30; i++)
            {
                var angle = (i / 30f) * Mathf.PI * 2f + (float)rng.NextDouble() * 0.2f;
                var radius = 17f + (float)rng.NextDouble() * 20f;
                var pos = new Vector3(Mathf.Cos(angle) * radius, 0f, 2f + Mathf.Sin(angle) * radius);
                if (InGallery(pos)) continue;
                var s = 0.6f + (float)rng.NextDouble() * 0.5f;
                var tree = new GameObject("Tree").transform;
                tree.SetParent(env, false);
                tree.position = pos;
                tree.localScale = Vector3.one * s;
                Part(tree, PrimitiveType.Cylinder, new Vector3(0f, 1.1f, 0f), new Vector3(0.35f, 1.1f, 0.35f), trunk);
                Part(tree, PrimitiveType.Sphere, new Vector3(0f, 3.1f, 0f), Vector3.one * 3.2f, leafA);
                Part(tree, PrimitiveType.Sphere, new Vector3(0.5f, 4.3f, 0.2f), Vector3.one * 2.4f, leafB);
                Part(tree, PrimitiveType.Sphere, new Vector3(-0.7f, 3.7f, -0.3f), Vector3.one * 2.1f, leafB);
            }
            for (var i = 0; i < 16; i++)
            {
                var angle = (float)rng.NextDouble() * Mathf.PI * 2f;
                var radius = 8.5f + (float)rng.NextDouble() * 4f;
                var bushPos = new Vector3(Mathf.Cos(angle) * radius, 0f, 2f + Mathf.Sin(angle) * radius);
                if (InGallery(bushPos)) continue;
                var bush = new GameObject("Bush").transform;
                bush.SetParent(env, false);
                bush.position = bushPos;
                var s = 0.8f + (float)rng.NextDouble() * 0.8f;
                Part(bush, PrimitiveType.Sphere, new Vector3(0f, 0.4f * s, 0f), new Vector3(1.6f, 1.0f, 1.6f) * s, i % 2 == 0 ? leafA : leafB);
            }
        }

        private static void Part(Transform parent, PrimitiveType type, Vector3 localPos, Vector3 scale, Material mat)
        {
            var go = GameObject.CreatePrimitive(type);
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = scale;
            go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        }

        private static Material SolidMaterial(string name, Color color)
        {
            var path = $"{DemoSettingsDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", 0.05f);
            mat.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static Material DemoMaterial(string name, Texture2D tex, float tiling)
        {
            var path = $"{DemoSettingsDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", tex);
            mat.SetTextureScale("_BaseMap", new Vector2(tiling, tiling));
            mat.SetFloat("_Smoothness", 0f);
            mat.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // Tileable noise: periodic in both axes, so textures repeat without seams.
        private static float TN(int x, int y, int size, float freq, float offset)
        {
            var u = x / (float)size * Mathf.PI * 2f;
            var v = y / (float)size * Mathf.PI * 2f;
            return Mathf.PerlinNoise(freq * (Mathf.Cos(u) + Mathf.Cos(v)) + offset, freq * (Mathf.Sin(u) + Mathf.Sin(v)) + offset);
        }

        private static Texture2D SaveTexture(string name, Color[] pixels, int size)
        {
            var path = $"{DemoTextureDir}/{name}.png";
            var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
            tex.SetPixels(pixels);
            File.WriteAllBytes(path, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 8;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        private static Texture2D NoiseTexture(string name, Color a, Color b, float scale)
        {
            const int size = 512;
            var px = new Color[size * size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var n = TN(x, y, size, scale, 20f) * 0.6f + TN(x, y, size, scale * 3f, 50f) * 0.4f;
                var speckle = (float)_rng.NextDouble() * 0.05f - 0.025f;
                px[y * size + x] = Color.Lerp(a, b, Mathf.Clamp01(n + speckle));
            }
            return SaveTexture(name, px, size);
        }

        private static Texture2D GrassTexture()
        {
            const int size = 512;
            var dark = new Color(0.22f, 0.36f, 0.12f);
            var mid = new Color(0.34f, 0.51f, 0.18f);
            var light = new Color(0.50f, 0.67f, 0.26f);
            var px = new Color[size * size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var broad = TN(x, y, size, 1.2f, 50f);
                var patch = TN(x, y, size, 3.5f, 80f);
                var fine = TN(x, y, size, 14f, 120f);
                var c = Color.Lerp(dark, mid, broad * 0.65f + fine * 0.35f);
                if (patch > 0.6f) c = Color.Lerp(c, light, (patch - 0.6f) * 0.9f);
                var r = (float)_rng.NextDouble();
                if (r < 0.06f) c *= 0.8f;
                else if (r < 0.11f) c = Color.Lerp(c, light, 0.4f);
                px[y * size + x] = c;
            }
            return SaveTexture("T_Demo_Grass", px, size);
        }

        private static Texture2D CobbleTexture()
        {
            const int size = 512;
            const int cells = 8;
            const float cell = size / (float)cells;
            var rng = new Random(5);
            var jitter = new Vector2[cells, cells];
            var tint = new float[cells, cells];
            for (var i = 0; i < cells; i++)
            for (var j = 0; j < cells; j++)
            {
                jitter[i, j] = new Vector2(0.2f + (float)rng.NextDouble() * 0.6f, 0.2f + (float)rng.NextDouble() * 0.6f);
                tint[i, j] = (float)rng.NextDouble();
            }

            var stoneA = new Color(0.72f, 0.69f, 0.64f);
            var stoneB = new Color(0.52f, 0.50f, 0.46f);
            var grout = new Color(0.24f, 0.21f, 0.17f);
            var px = new Color[size * size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                float d1 = float.MaxValue, d2 = float.MaxValue;
                var id = Vector2Int.zero;
                var cx = (int)(x / cell);
                var cy = (int)(y / cell);
                for (var gy = -1; gy <= 1; gy++)
                for (var gx = -1; gx <= 1; gx++)
                {
                    var ix = cx + gx;
                    var iy = cy + gy;
                    var wx = ((ix % cells) + cells) % cells;
                    var wy = ((iy % cells) + cells) % cells;
                    var point = new Vector2((ix + jitter[wx, wy].x) * cell, (iy + jitter[wx, wy].y) * cell);
                    var d = Vector2.Distance(new Vector2(x, y), point);
                    if (d < d1) { d2 = d1; d1 = d; id = new Vector2Int(wx, wy); }
                    else if (d < d2) d2 = d;
                }

                var edge = (d2 - d1) / cell;
                var stone = Color.Lerp(stoneA, stoneB, tint[id.x, id.y]);
                stone *= 0.96f + (TN(x, y, size, 3f, 30f) - 0.5f) * 0.1f;
                var bevel = Mathf.SmoothStep(0f, 1f, (edge - 0.05f) / 0.16f);
                px[y * size + x] = Color.Lerp(grout, stone * Mathf.Lerp(0.8f, 1.05f, bevel), Mathf.SmoothStep(0f, 1f, (edge - 0.04f) / 0.06f));
            }
            return SaveTexture("T_Demo_Cobble", px, size);
        }

        private static Texture2D PlankTexture()
        {
            const int size = 512;
            const int planks = 8;
            const int plankH = size / planks;
            var rng = new Random(11);
            var plankTint = new float[planks];
            var joint = new int[planks];
            for (var i = 0; i < planks; i++) { plankTint[i] = (float)rng.NextDouble(); joint[i] = rng.Next(size); }

            var woodA = new Color(0.66f, 0.50f, 0.33f);
            var woodB = new Color(0.50f, 0.36f, 0.23f);
            var gap = new Color(0.18f, 0.12f, 0.08f);
            var px = new Color[size * size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var row = y / plankH;
                var within = (y % plankH) / (float)plankH;
                var c = Color.Lerp(woodA, woodB, plankTint[row]);
                var grain = TN(x, y, size, 5f, 10f) * 0.6f + TN(x * 3 % size, y, size, 9f, 60f) * 0.4f;
                c *= 0.86f + grain * 0.28f;
                var joinDist = Mathf.Min(Mathf.Abs(x - joint[row]), size - Mathf.Abs(x - joint[row]));
                if (within < 0.035f || within > 0.975f || joinDist < 2) c = gap;
                px[y * size + x] = c;
            }
            return SaveTexture("T_Demo_Planks", px, size);
        }

        private static void BuildLighting()
        {
            var sunGo = new GameObject("Sun");
            sunGo.transform.rotation = Quaternion.Euler(34f, -38f, 0f);
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.9f, 0.74f);
            sun.intensity = 1.9f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.85f;
            RenderSettings.sun = sun;

            var skyMat = new Material(Shader.Find("FarmMarketStarter/Gradient Sky"));
            skyMat.SetColor("_ZenithColor", new Color(0.30f, 0.50f, 0.86f));
            skyMat.SetColor("_HorizonColor", new Color(0.80f, 0.89f, 0.97f));
            skyMat.SetColor("_GroundColor", new Color(0.62f, 0.66f, 0.55f));
            var skyPath = $"{DemoSettingsDir}/M_Demo_Sky.mat";
            AssetDatabase.CreateAsset(skyMat, skyPath);
            RenderSettings.skybox = skyMat;
            RenderSettings.ambientMode = AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 1.1f;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogDensity = 0.022f;
            RenderSettings.fogColor = new Color(0.80f, 0.86f, 0.90f);

            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            var bloom = profile.Add<Bloom>();
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(0.5f);
            bloom.scatter.Override(0.6f);
            profile.Add<Tonemapping>().mode.Override(TonemappingMode.ACES);
            var color = profile.Add<ColorAdjustments>();
            color.postExposure.Override(0.15f);
            color.contrast.Override(10f);
            color.saturation.Override(14f);
            color.colorFilter.Override(new Color(1f, 0.97f, 0.92f));
            var dof = profile.Add<DepthOfField>();
            dof.mode.Override(DepthOfFieldMode.Bokeh);
            dof.focusDistance.Override(6.6f);
            dof.focalLength.Override(55f);
            dof.aperture.Override(7f);
            var vignette = profile.Add<Vignette>();
            vignette.intensity.Override(0.2f);
            vignette.smoothness.Override(0.5f);
            var profilePath = $"{DemoSettingsDir}/FMS_Demo_VolumeProfile.asset";
            AssetDatabase.CreateAsset(profile, profilePath);
            foreach (var sub in profile.components) AssetDatabase.AddObjectToAsset(sub, profile);

            var volumeGo = new GameObject("Post Processing");
            var volume = volumeGo.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = profile;
        }

        private static void BuildCamera()
        {
            var targetGo = new GameObject("CameraTarget");
            targetGo.transform.position = new Vector3(1.0f, 0.8f, 2.1f);

            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            camGo.transform.position = new Vector3(1.0f, 1.9f, -4.2f);
            var cam = camGo.AddComponent<Camera>();
            cam.fieldOfView = 46f;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 120f;
            cam.clearFlags = CameraClearFlags.Skybox;
            camGo.AddComponent<AudioListener>();
            var data = camGo.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            camGo.transform.LookAt(targetGo.transform.position);

            var orbit = camGo.AddComponent<FMS_DemoCamera>();
            var so = new SerializedObject(orbit);
            so.FindProperty("target").objectReferenceValue = targetGo.transform;
            so.FindProperty("galleryTarget").objectReferenceValue = _galleryTarget;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        // ---------- Screenshot (hero shot for the store page / visual check) ----------

        public static string Shoot(string outPath, float x, float y, float z, float lx, float ly, float lz, float fov, int w, int h)
        {
            var cam = Camera.main;
            var orbit = cam.GetComponent<FMS_DemoCamera>();
            if (orbit != null) orbit.enabled = false;
            cam.transform.position = new Vector3(x, y, z);
            cam.transform.LookAt(new Vector3(lx, ly, lz));
            cam.fieldOfView = fov;

            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Default) { antiAliasing = 4 };
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            File.WriteAllBytes(outPath, tex.EncodeToPNG());
            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
            return outPath;
        }
    }
}
