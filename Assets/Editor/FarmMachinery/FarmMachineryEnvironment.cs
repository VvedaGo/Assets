using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Demo environment DEM-01…09 (CATALOG "Демо-окружение", planning/FarmMachinery/prompts/DEM.3d.md): demo-only models, not catalogue
    /// products, so they live in Assets/FarmMachinery/Demo/Environment/{Models,Textures,Materials,Prefabs} and are not counted by
    /// FarmMachineryChecks. Import settings as PackPrefabBuilder (flat atlas: point filter, no mipmaps; models without
    /// materials), one URP/Lit material M_FarmMachinery_Demo, prefabs without colliders. Layouts place them with the '#! env' /
    /// '#! scatter' directives of FarmMachinerySceneBuilder by the keys of <see cref="PrefabPaths"/>: PackConfig.PrefabNames
    /// always resolves under Art/Prefabs/&lt;category&gt;, where these models must not go. Idempotent: paths, so GUIDs, are kept.
    /// FBX/PNG are copied from art/FarmMachinery/Demo/ beforehand, then AssetDatabase.Refresh in its own call.
    /// </summary>
    public static class FarmMachineryEnvironment
    {
        public const string Root = "Assets/FarmMachinery/Demo/Environment";
        /// <summary>Base atlases / materials made by Import (A/B base of LOOK v2): dev-only since Э14; the shipped prefabs use the
        /// v2 materials (FarmMachineryRelease.UseV2EnvironmentMaterials, run it again after a new Import).</summary>
        public const string BaseRoot = "Assets/_FarmMachineryDev/Demo/Environment";
        private const string Texture = "T_FarmMachinery_Demo_BaseColor";
        private const string MaterialName = "M_FarmMachinery_Demo";
        public const string ReportPath = ".work/ImportReport_FarmMachinery_Demo.txt";

        private static readonly (string Key, string Name)[] Models =
        {
            ("DEM-01", "IslandBase"), ("DEM-02", "FieldPloughed"), ("DEM-03", "FieldStubble"), ("DEM-04", "Road_Straight"),
            ("DEM-04_Corner", "Road_Corner"), ("DEM-05", "GrassTufts"), ("DEM-06", "Clouds"),
            // MEDIA v2 (scenes/changes/00_NEW_DEMO_ASSETS): second demo atlas T_FarmMachinery_Demo2_BaseColor
            ("DEM-07", "WheatField"), ("DEM-07_Edge", "WheatEdge"), ("DEM-08", "Bales"), ("DEM-09", "Seedlings"),
        };

        /// <summary>Models on the second demo atlas (material M_FarmMachinery_Demo2).</summary>
        private static bool OnDemo2(string key) => key.StartsWith("DEM-07") || key == "DEM-08" || key == "DEM-09";
        private const string Texture2Name = "T_FarmMachinery_Demo2_BaseColor";
        private const string Material2Name = "M_FarmMachinery_Demo2";

        private static string PrefabPath(string name) => $"{Root}/Prefabs/FMS_Mach_Demo_{name}.prefab";

        /// <summary>Layout key → prefab path: DEM-01…DEM-06, DEM-04_Corner, and DEM-05_&lt;Child&gt; / DEM-06_&lt;Child&gt; for each prop of the
        /// tuft FBX and each cloud of the cloud FBX.</summary>
        public static Dictionary<string, string> PrefabPaths()
        {
            var map = Models.ToDictionary(m => m.Key, m => PrefabPath(m.Name));
            foreach (var (key, name) in Models.Where(m => SplitChildren(m.Key)))
                foreach (var path in AssetDatabase.FindAssets($"t:Prefab FMS_Mach_Demo_{name}_", new[] { $"{Root}/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath))
                    map[key + "_" + Path.GetFileNameWithoutExtension(path).Substring($"FMS_Mach_Demo_{name}_".Length)] = path;
            return map;
        }

        [MenuItem("Tools/Farm Machinery/Import Demo Environment")]
        public static string Import()
        {
            Directory.CreateDirectory($"{BaseRoot}/Materials");
            Directory.CreateDirectory($"{Root}/Prefabs");
            var texPath = $"{BaseRoot}/Textures/{Texture}.png";
            var tex = (TextureImporter)AssetImporter.GetAtPath(texPath) ?? throw new System.InvalidOperationException($"{texPath} missing: copy and refresh first");
            if (tex.filterMode != FilterMode.Point || tex.mipmapEnabled)
            {
                tex.filterMode = FilterMode.Point;
                tex.mipmapEnabled = false;
                tex.textureCompression = TextureImporterCompression.Uncompressed;
                tex.SaveAndReimport();
            }
            var material = Material(AssetDatabase.LoadAssetAtPath<Texture2D>(texPath));
            var cloudMaterial = CloudMaterial(material);
            var tex2Path = $"{BaseRoot}/Textures/{Texture2Name}.png";
            var tex2 = (TextureImporter)AssetImporter.GetAtPath(tex2Path) ?? throw new System.InvalidOperationException($"{tex2Path} missing: copy and refresh first");
            if (tex2.filterMode != FilterMode.Point || tex2.mipmapEnabled)
            {
                tex2.filterMode = FilterMode.Point;
                tex2.mipmapEnabled = false;
                tex2.textureCompression = TextureImporterCompression.Uncompressed;
                tex2.SaveAndReimport();
            }
            var material2 = Material(AssetDatabase.LoadAssetAtPath<Texture2D>(tex2Path), Material2Name);

            var report = new StringBuilder($"[FarmMachinery demo environment] {Root} (demo only, not in the catalogue counts)\n");
            FarmMachineryCatalog.InPreviewScene(scene =>
            {
                foreach (var (key, name) in Models)
                {
                    var modelPath = $"{Root}/Models/FMS_Mach_Demo_{name}.fbx";
                    ConfigureModel(modelPath);
                    var go = FarmMachineryCatalog.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(modelPath), scene);
                    PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                    go.name = $"FMS_Mach_Demo_{name}";
                    foreach (var r in go.GetComponentsInChildren<Renderer>(true))
                    {
                        r.sharedMaterials = Enumerable.Repeat(key == "DEM-06" ? cloudMaterial : OnDemo2(key) ? material2 : material, r.sharedMaterials.Length).ToArray();
                        if (key == "DEM-06")       // clouds float around / below the island: no shadows either way
                        {
                            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                            r.receiveShadows = false;
                        }
                    }
                    report.AppendLine($"{key,-14} {Line(go)}");
                    PrefabUtility.SaveAsPrefabAsset(go, PrefabPath(name));

                    if (SplitChildren(key))   // one prefab per child (tuft props, clouds) for scattering, each at its own base centre
                        foreach (Transform child in go.transform.Cast<Transform>().ToList())
                        {
                            child.SetParent(null, true);
                            child.SetPositionAndRotation(Vector3.zero, child.rotation);
                            UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(child.gameObject, scene);
                            var propName = $"{name}_{child.name.Replace("Tuft_", "").Replace("Cloud_", "").Replace("Bale_", "")}";
                            child.name = $"FMS_Mach_Demo_{propName}";
                            report.AppendLine($"{key + "_" + propName.Substring(name.Length + 1),-14} {Line(child.gameObject)}");
                            PrefabUtility.SaveAsPrefabAsset(child.gameObject, PrefabPath(propName));
                            Object.DestroyImmediate(child.gameObject);
                        }
                    Object.DestroyImmediate(go);
                }
                return 0;
            });
            AssetDatabase.SaveAssets();
            File.WriteAllText(ReportPath, report.ToString());
            Debug.Log(report.ToString());
            return report.ToString();
        }

        /// <summary>FBX whose children are separate pieces (DEM-05 tuft props, DEM-06 clouds, DEM-08 bales).</summary>
        private static bool SplitChildren(string key) => key == "DEM-05" || key == "DEM-06" || key == "DEM-08";

        private static string Line(GameObject go)
        {
            var renderers = go.GetComponentsInChildren<MeshRenderer>(true);
            var b = FarmMachineryCatalog.Lod0Bounds(renderers);
            var rot = go.transform.rotation.eulerAngles;
            return $"{go.name}  tris {FarmMachineryCatalog.Tris(renderers)}  size {b.size.x:F2}x{b.size.y:F2}x{b.size.z:F2}  Y {b.min.y:F3}..{b.max.y:F3}" +
                   $"  centre {b.center.x:F2},{b.center.z:F2}" + (rot.sqrMagnitude > 0.01f ? $"  ! rotation {rot}" : "");
        }

        private static void ConfigureModel(string path)
        {
            var importer = (ModelImporter)AssetImporter.GetAtPath(path);
            if (importer.materialImportMode == ModelImporterMaterialImportMode.None && !importer.isReadable && !importer.importAnimation) return;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.isReadable = false;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.importNormals = ModelImporterNormals.Import;
            importer.SaveAndReimport();
        }

        /// <summary>
        /// M_FarmMachinery_Demo_Cloud: shader FarmMachinery/Demo/Cloud (unlit gradient by the face normal: white tops, cool
        /// blue-grey undersides, small facet accent). A lit material picked up the warm key and the brown trilight ground and
        /// read beige-brown; the clouds must stay white like the Farm Nature demo clouds. The material GUID is kept.
        /// </summary>
        private static Material CloudMaterial(Material demo)
        {
            var path = $"{BaseRoot}/Materials/M_FarmMachinery_Demo_Cloud.mat";
            var shader = Shader.Find("FarmMachinery/Demo/Cloud");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }
            else if (mat.shader != shader) mat.shader = shader;
            mat.SetColor("_TopColor", Cloud.Top);
            mat.SetColor("_SideColor", Cloud.Side);
            mat.SetColor("_BottomColor", Cloud.Bottom);
            mat.SetFloat("_FacetAccent", Cloud.FacetAccent);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        /// <summary>Cloud colours (SCENE_STYLE.md "Sky and clouds").</summary>
        private static class Cloud
        {
            public static readonly Color Top = new Color(1.0f, 1.0f, 1.0f);
            public static readonly Color Side = new Color(0.90f, 0.93f, 0.98f);
            public static readonly Color Bottom = new Color(0.72f, 0.80f, 0.92f);
            public const float FacetAccent = 0.08f;
        }

        private static Material Material(Texture2D texture, string materialName = MaterialName)
        {
            var path = $"{BaseRoot}/Materials/{materialName}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", texture);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", FarmMachineryPackBuilder.Config.Smoothness);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            return mat;
        }
    }
}
