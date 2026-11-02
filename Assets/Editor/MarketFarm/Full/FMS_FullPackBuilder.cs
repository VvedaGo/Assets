using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using MarketFarm.Editor;
using UnityEditor;
using UnityEngine;

namespace FarmMarketStarter.Editor
{
    /// <summary>
    /// Builds URP materials and single-item prefabs of the Farm Market Full pack from Art/Models/&lt;Category&gt;.
    /// FBX children named *_LOD1/*_LOD2 become an LODGroup, *_Col becomes the root BoxCollider. Idempotent (GUIDs stay).
    /// </summary>
    public static class FMS_FullPackBuilder
    {
        private const string Root = "Assets/FarmMarketFull";
        private const string ModelDir = Root + "/Art/Models";
        private const string MaterialDir = Root + "/Art/Materials";
        private const string TextureDir = Root + "/Art/Textures";
        private const string SingleDir = Root + "/Art/Prefabs/Single";

        // Material names inside the FBX files -> final material asset names.
        private static readonly Dictionary<string, string> MaterialRenames = new Dictionary<string, string>
        {
            { "M_Barrels_v2", "M_Barrels" }, { "M_Hay2", "M_Hay" }, { "M_MarketBasket2", "M_MarketBasket" },
            { "M_MarketCorn2", "M_MarketCorn" }, { "M_MarketEggs2", "M_MarketEggs" }, { "M_MarketHoney2", "M_MarketHoney" },
            { "M_Shelves_v2", "M_Shelves" },
        };

        // Colour variants that only swap the base map: model name -> (variant suffix, texture).
        private static readonly (string Model, string Variant, string Texture)[] TextureVariants =
        {
            ("FMS_Stall_Umbrella", "Blue", "T_Umbrella_Blue_BaseColor"),
            ("FMS_Stall_Umbrella", "Green", "T_Umbrella_Green_BaseColor"),
        };

        private static readonly float[] LodHeights = { 0.35f, 0.12f, 0.015f };

        private static readonly Dictionary<string, Material> MaterialCache = new Dictionary<string, Material>();

        [MenuItem("Tools/Farm Market Full/Build Prefabs")]
        public static string Build()
        {
            MaterialCache.Clear();
            var report = new StringBuilder();
            var prefabByModel = new Dictionary<string, string>();

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { ModelDir }).OrderBy(AssetDatabase.GUIDToAssetPath))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var category = Path.GetFileName(Path.GetDirectoryName(path));
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var prefabPath = BuildSingle(model, category, report);
                prefabByModel[model.name] = prefabPath;
            }

            foreach (var (modelName, variant, texture) in TextureVariants)
                BuildTextureVariant(prefabByModel[modelName], variant, texture, report);

            AssetDatabase.SaveAssets();
            ReportUnusedTextures(report);
            report.Insert(0, $"[FarmMarketFull] {prefabByModel.Count} prefabs + {TextureVariants.Length} variants, {MaterialCache.Count} materials\n");
            Debug.Log(report.ToString());
            return report.ToString();
        }

        private static string BuildSingle(GameObject model, string category, StringBuilder report)
        {
            var prefabName = model.name;
            var dir = $"{SingleDir}/{category}";
            Directory.CreateDirectory(dir);

            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            instance.name = prefabName;

            Bounds? colBounds = null;
            foreach (var t in instance.GetComponentsInChildren<Transform>(true).Where(t => t.name.EndsWith("_Col")).ToList())
            {
                colBounds = t.GetComponent<Renderer>().bounds;
                Object.DestroyImmediate(t.gameObject);
            }

            var renderers = instance.GetComponentsInChildren<Renderer>(true);
            foreach (var r in renderers)
                r.sharedMaterials = r.sharedMaterials.Select(UrpMaterial).ToArray();

            var lod0 = renderers.Where(r => !r.name.EndsWith("_LOD1") && !r.name.EndsWith("_LOD2")).ToArray();
            var lod1 = renderers.Where(r => r.name.EndsWith("_LOD1")).ToArray();
            var lod2 = renderers.Where(r => r.name.EndsWith("_LOD2")).ToArray();
            if (lod1.Length > 0)
            {
                var group = instance.GetComponent<LODGroup>() ?? instance.AddComponent<LODGroup>();
                var levels = new List<LOD> { new LOD(LodHeights[0], lod0), new LOD(LodHeights[1], lod1) };
                if (lod2.Length > 0) levels.Add(new LOD(LodHeights[2], lod2));
                group.SetLODs(levels.ToArray());
                group.RecalculateBounds();
            }

            var bounds = Encapsulate(lod0);
            var box = instance.AddComponent<BoxCollider>();
            var fit = colBounds ?? bounds;
            box.center = fit.center;
            box.size = fit.size;

            var tris = lod0.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3);
            var prefabPath = $"{dir}/{prefabName}.prefab";
            PrefabUtility.SaveAsPrefabAsset(instance, prefabPath);
            Object.DestroyImmediate(instance);

            var issues = new List<string>();
            if (Mathf.Abs(bounds.min.y) > MarketFarmRules.PivotTolerance) issues.Add($"pivot min Y {bounds.min.y:F3}");
            if (lod1.Length == 0) issues.Add("no LOD");
            report.AppendLine($"{category}/{prefabName}  tris {tris}  size {bounds.size.x:F2}x{bounds.size.y:F2}x{bounds.size.z:F2}" +
                              (colBounds.HasValue ? "  col" : "") + (issues.Count > 0 ? "  ! " + string.Join(", ", issues) : ""));
            return prefabPath;
        }

        private static void BuildTextureVariant(string basePrefabPath, string variant, string textureName, StringBuilder report)
        {
            var basePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(basePrefabPath);
            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>($"{TextureDir}/{textureName}.png");
            var renderers = basePrefab.GetComponentsInChildren<Renderer>(true);
            var source = renderers[0].sharedMaterials[0];

            var mat = LoadOrCreateMaterial($"{source.name}_{variant}");
            mat.CopyPropertiesFromMaterial(source);
            mat.SetTexture("_BaseMap", texture);
            EditorUtility.SetDirty(mat);

            var variantName = $"{basePrefab.name}_{variant}";
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(basePrefab);
            instance.name = variantName;
            foreach (var r in instance.GetComponentsInChildren<Renderer>(true))
                r.sharedMaterials = r.sharedMaterials.Select(m => m == source ? mat : m).ToArray();
            var path = $"{Path.GetDirectoryName(basePrefabPath).Replace('\\', '/')}/{variantName}.prefab";
            PrefabUtility.SaveAsPrefabAsset(instance, path);
            Object.DestroyImmediate(instance);
            report.AppendLine($"variant {variantName} ({textureName})");
        }

        private static Material UrpMaterial(Material source)
        {
            if (MaterialCache.TryGetValue(source.name, out var cached)) return cached;
            var mat = LoadOrCreateMaterial(MaterialRenames.TryGetValue(source.name, out var renamed) ? renamed : source.name);
            if (source.mainTexture != null) mat.SetTexture("_BaseMap", source.mainTexture);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", 0.15f);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            MaterialCache[source.name] = mat;
            return mat;
        }

        private static Material LoadOrCreateMaterial(string name)
        {
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat != null) return mat;
            mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            AssetDatabase.CreateAsset(mat, path);
            return mat;
        }

        private static Bounds Encapsulate(Renderer[] renderers)
        {
            var bounds = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            return bounds;
        }

        private static void ReportUnusedTextures(StringBuilder report)
        {
            var used = new HashSet<string>(AssetDatabase.GetDependencies(
                AssetDatabase.FindAssets("t:Material", new[] { MaterialDir }).Select(AssetDatabase.GUIDToAssetPath).ToArray()));
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { TextureDir }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!used.Contains(path)) report.AppendLine($"unused texture {path}");
            }
        }
    }
}
