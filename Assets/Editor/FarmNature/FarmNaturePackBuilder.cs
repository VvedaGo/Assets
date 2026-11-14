using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace FarmNature.Editor
{
    /// <summary>
    /// Builds URP materials and single-item prefabs of the Farm Nature pack from Art/Models/&lt;Category&gt;.
    /// Texture of each FBX is read from its own bytes (T_FarmNature_*_BaseColor). Idempotent (GUIDs stay).
    /// </summary>
    public static class FarmNaturePackBuilder
    {
        private const string Root = "Assets/FarmNature";
        private const string ModelDir = Root + "/Art/Models";
        private const string MaterialDir = Root + "/Art/Materials";
        private const string TextureDir = Root + "/Art/Textures";
        private const string PrefabDir = Root + "/Art/Prefabs";

        private static readonly Regex TextureName = new Regex(@"T_FarmNature_[A-Za-z0-9]+_BaseColor", RegexOptions.Compiled);

        private static readonly Dictionary<string, Material> MaterialCache = new Dictionary<string, Material>();

        [MenuItem("Tools/Farm Nature/Build Prefabs")]
        public static string Build()
        {
            MaterialCache.Clear();
            Directory.CreateDirectory(MaterialDir);
            ConfigureTextures();

            var report = new StringBuilder();
            var count = 0;
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { ModelDir }).OrderBy(AssetDatabase.GUIDToAssetPath))
            {
                BuildSingle(AssetDatabase.GUIDToAssetPath(guid), report);
                count++;
            }

            AssetDatabase.SaveAssets();
            report.Insert(0, $"[FarmNature] {count} prefabs, {MaterialCache.Count} materials\n");
            Debug.Log(report.ToString());
            return report.ToString();
        }

        private static void ConfigureTextures()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { TextureDir }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = (TextureImporter)AssetImporter.GetAtPath(path);
                if (importer.filterMode == FilterMode.Point && !importer.mipmapEnabled) continue;
                importer.filterMode = FilterMode.Point; // atlas cells must not bleed
                importer.mipmapEnabled = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
        }

        private static void BuildSingle(string modelPath, StringBuilder report)
        {
            var category = Path.GetFileName(Path.GetDirectoryName(modelPath));
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var textures = TextureName.Matches(File.ReadAllText(modelPath, Encoding.GetEncoding(28591))).Select(m => m.Value).Distinct().ToList();

            var dir = $"{PrefabDir}/{category}";
            Directory.CreateDirectory(dir);

            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            instance.name = model.name;

            var renderers = instance.GetComponentsInChildren<Renderer>(true);
            foreach (var r in renderers)
                r.sharedMaterials = r.sharedMaterials.Select(m => UrpMaterial(m, textures, model.name, report)).ToArray();

            var bounds = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            var box = instance.AddComponent<BoxCollider>();
            box.center = bounds.center;
            box.size = bounds.size;

            var tris = renderers.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3);
            PrefabUtility.SaveAsPrefabAsset(instance, $"{dir}/{model.name}.prefab");
            Object.DestroyImmediate(instance);

            var issues = new List<string>();
            if (Mathf.Abs(bounds.min.y) > 0.005f) issues.Add($"pivot min Y {bounds.min.y:F3}");
            report.AppendLine($"{category}/{model.name}  tris {tris}  size {bounds.size.x:F2}x{bounds.size.y:F2}x{bounds.size.z:F2}" +
                              (issues.Count > 0 ? "  ! " + string.Join(", ", issues) : ""));
        }

        private static Material UrpMaterial(Material source, List<string> textures, string model, StringBuilder report)
        {
            var texName = PickTexture(source.name, textures);
            if (texName == null)
            {
                report.AppendLine($"! {model}: no texture for material {source.name} (FBX lists {string.Join(",", textures)})");
                return source;
            }

            var matName = texName.Replace("T_", "M_").Replace("_BaseColor", "");
            if (MaterialCache.TryGetValue(matName, out var cached)) return cached;

            var path = $"{MaterialDir}/{matName}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{TextureDir}/{texName}.png"));
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", 0.1f);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            MaterialCache[matName] = mat;
            return mat;
        }

        // One texture in the FBX -> it. Several (Water: Shore + Water) -> the one whose name is contained in the material name.
        private static string PickTexture(string materialName, List<string> textures)
        {
            if (textures.Count == 1) return textures[0];
            var key = Norm(materialName);
            return textures.FirstOrDefault(t => key.Contains(Norm(t.Replace("T_FarmNature_", "").Replace("_BaseColor", ""))));
        }

        private static string Norm(string s) => s.Replace("_", "").ToLowerInvariant();
    }
}
