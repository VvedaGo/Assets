using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

namespace PackTools.Editor
{
    /// <summary>
    /// Shared pack importer (origin: Farm Processing, 2026-11-20): model import settings, one URP/Lit material per atlas,
    /// single-item prefabs in Art/Prefabs/&lt;Category&gt; with a BoxCollider, a LODGroup when the FBX carries "&lt;part&gt;_LOD1"
    /// children (Tools/blender/make_lod1.py), and Documentation/ImportReport.txt (tris, parts, LOD1, size, issues).
    /// The atlas of each FBX is read from the FBX bytes. Idempotent: GUIDs of prefabs and materials are kept.
    /// </summary>
    public static class PackPrefabBuilder
    {
        private static PackConfig C;
        private static string ModelDir => C.ModelDir;
        private static string MaterialDir => C.MaterialDir;
        private static string TextureDir => C.TextureDir;
        private static string PrefabDir => C.PrefabDir;
        private static string ReportPath => C.ReportPath;
        private static Regex TextureName;

        public static string Build(PackConfig config)
        {
            C = config;
            TextureName = new Regex(config.TextureRegex, RegexOptions.Compiled);
            Directory.CreateDirectory(MaterialDir);
            Directory.CreateDirectory(Path.GetDirectoryName(ReportPath));
            ConfigureTextures();
            ConfigureModels();

            var report = new StringBuilder();
            var lines = new List<string>();
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { ModelDir }).OrderBy(AssetDatabase.GUIDToAssetPath))
                lines.Add(BuildSingle(AssetDatabase.GUIDToAssetPath(guid)));

            AssetDatabase.SaveAssets();
            report.AppendLine($"[{C.Tag}] {lines.Count} prefabs, {lines.Count(l => l.Contains(" ! "))} with issues");
            foreach (var l in lines) report.AppendLine(l);
            File.WriteAllText(ReportPath, report.ToString());
            AssetDatabase.ImportAsset(ReportPath);
            Debug.Log(report.ToString());
            return report.ToString();
        }

        private static void ConfigureTextures()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { TextureDir }))
            {
                var importer = (TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GUIDToAssetPath(guid));
                if (importer.filterMode == FilterMode.Point && !importer.mipmapEnabled) continue;
                importer.filterMode = FilterMode.Point;          // flat-colour atlas cells must not bleed
                importer.mipmapEnabled = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
        }

        private static void ConfigureModels()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { ModelDir }))
            {
                var importer = (ModelImporter)AssetImporter.GetAtPath(AssetDatabase.GUIDToAssetPath(guid));
                if (importer.materialImportMode == ModelImporterMaterialImportMode.None && !importer.isReadable) continue;
                importer.materialImportMode = ModelImporterMaterialImportMode.None;   // URP materials are assigned by Build()
                importer.importCameras = false;
                importer.importLights = false;
                importer.importAnimation = false;
                importer.animationType = ModelImporterAnimationType.None;
                importer.isReadable = false;
                importer.meshCompression = ModelImporterMeshCompression.Off;
                importer.importNormals = ModelImporterNormals.Import;               // flat-shaded facets as authored
                importer.SaveAndReimport();
            }
        }

        private static string BuildSingle(string modelPath)
        {
            var category = Path.GetFileName(Path.GetDirectoryName(modelPath));
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var texture = TextureName.Matches(File.ReadAllText(modelPath, Encoding.GetEncoding(28591))).Select(m => m.Value).FirstOrDefault();

            var dir = $"{PrefabDir}/{category}";
            Directory.CreateDirectory(dir);

            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            instance.name = model.name;

            var issues = new List<string>();
            var material = texture != null ? UrpMaterial(texture) : null;
            if (material == null) issues.Add("no texture in FBX");

            foreach (var r in instance.GetComponentsInChildren<Renderer>(true))
                r.sharedMaterials = Enumerable.Repeat(material, r.sharedMaterials.Length).ToArray();

            // LOD1 parts are exported as direct children of the root ("<part>_LOD1"); move each under its part so it
            // follows the moving part, and build a LODGroup (LOD0 = parts, LOD1 = *_LOD1).
            var lod1 = instance.GetComponentsInChildren<Renderer>(true).Where(r => r.name.EndsWith("_LOD1")).ToArray();
            foreach (var r in lod1)
            {
                var partName = r.name.Substring(0, r.name.Length - 5);
                var part = instance.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == partName);   // parts can be nested (e.g. a crank under a stone)
                if (part != null) r.transform.SetParent(part, true);
            }
            var renderers = instance.GetComponentsInChildren<Renderer>(true).Where(r => !r.name.EndsWith("_LOD1")).ToArray();
            if (lod1.Length > 0)
            {
                var group = instance.AddComponent<LODGroup>();
                group.SetLODs(new[] { new LOD(C.Lod0Height, renderers), new LOD(C.CullHeight, lod1) });
                group.RecalculateBounds();
            }

            var bounds = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            var box = instance.AddComponent<BoxCollider>();
            box.center = bounds.center - instance.transform.position;
            box.size = bounds.size;

            var tris = renderers.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3);
            var lod1Tris = lod1.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3);
            var rootRot = instance.transform.localEulerAngles;
            if (rootRot.sqrMagnitude > 0.01f) issues.Add($"root rotation {rootRot}");
            if (Mathf.Abs(bounds.min.y) > 0.005f) issues.Add($"min Y {bounds.min.y:F3}");
            if ((instance.transform.localScale - Vector3.one).sqrMagnitude > 1e-6f) issues.Add($"root scale {instance.transform.localScale}");

            PrefabUtility.SaveAsPrefabAsset(instance, $"{dir}/{model.name}.prefab");
            Object.DestroyImmediate(instance);

            var parts = renderers.Length > 1 ? $"  parts {renderers.Length}" : "";
            if (lod1Tris > 0) parts += $"  LOD1 {lod1Tris}";
            return $"{category}/{model.name}  tris {tris}{parts}  size {bounds.size.x:F2}x{bounds.size.y:F2}x{bounds.size.z:F2}" +
                   (issues.Count > 0 ? "  ! " + string.Join(", ", issues) : "");
        }

        private static Material UrpMaterial(string texName)
        {
            var matName = texName.Replace("T_", "M_").Replace("_BaseColor", "");
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
            mat.SetFloat("_Smoothness", C.Smoothness);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            return mat;
        }
    }
}
