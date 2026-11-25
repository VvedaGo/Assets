using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Э14 release layout of Farm Machinery. Shipped: Assets/FarmMachinery (Art, Demo with the shipped demo scenes and their
    /// look assets, Documentation). Dev-only (media / catalogue shot scenes, A/B look variants, generated backdrop and zone
    /// materials) lives in Assets/_FarmMachineryDev with the same sub-paths and GUIDs, so every media rebuild still works:
    /// <see cref="AfterSceneBuild"/> moves the output of a non-shipped layout there after FarmMachinerySceneBuilder.Build.
    /// Packages: .work/export/FarmMachinery_1.0.0.unitypackage (Assets/FarmMachinery without README_Lite / Demo_Catalog_Lite) and
    /// FarmMachinery_Lite_1.0.0.unitypackage (Lite prefabs + Lite scenes + their dependencies + README_Lite + Changelog);
    /// same files → same GUIDs. Editor wrappers and PackTools are not exported.
    /// </summary>
    public static class FarmMachineryRelease
    {
        public const string PackRoot = "Assets/FarmMachinery";
        public const string DevRoot = "Assets/_FarmMachineryDev";
        public const string Version = "1.0.0";
        public static readonly string[] ShippedScenes = { "Demo_FieldWork", "Demo_Harvest", "Demo_Catalog", "Demo_Catalog_Lite" };
        public static readonly string[] LiteScenes = { "Demo_FieldWork", "Demo_Catalog_Lite" };
        /// <summary>Camera that stays active in each shipped scene (the others are kept as inactive viewpoints).</summary>
        private static readonly Dictionary<string, string> MainCamera = new Dictionary<string, string>
        {
            ["Demo_FieldWork"] = "Cam_Overview", ["Demo_Harvest"] = "Cam_Overview",
        };
        public const string CatalogBackdrop = PackRoot + "/Demo/Materials/M_FarmMachinery_Demo_CatalogBackdrop.mat";
        private const string DocDir = PackRoot + "/Documentation";
        private const string ExportDir = ".work/export";

        public static string ScenePath(string name) => $"{PackRoot}/Demo/Scenes/{name}.unity";
        public static string DevPath(string packPath) => DevRoot + packPath.Substring(PackRoot.Length);
        public static bool Shipped(string sceneName) => ShippedScenes.Contains(sceneName);

        // ------------------------------------------------------------------ layout

        /// <summary>Full release preparation: V2 materials on the environment prefabs, catalogue scenes, shipped scene cameras,
        /// then everything not needed by the shipped scenes moves to the dev folder.</summary>
        [MenuItem("Tools/Farm Machinery/Release/Prepare Layout")]
        public static string PrepareLayout()
        {
            var log = new StringBuilder();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            log.AppendLine(UseV2EnvironmentMaterials());
            log.AppendLine(MakeCatalogScene("Catalog_06_Full", "Demo_Catalog"));
            log.AppendLine(MakeCatalogScene("Catalog_06_Lite", "Demo_Catalog_Lite"));
            foreach (var kv in MainCamera) log.AppendLine(PrepareShippedScene(kv.Key, kv.Value));
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            log.AppendLine(MoveDevAssets());
            AssetDatabase.SaveAssets();
            log.AppendLine(CheckShippedDependencies());
            return log.ToString();
        }

        /// <summary>Moves every Demo asset that no shipped scene and no environment prefab uses to the dev folder.</summary>
        public static string MoveDevAssets()
        {
            var keep = new HashSet<string>(ShippedScenes.Select(ScenePath).Where(File.Exists)
                .SelectMany(p => AssetDatabase.GetDependencies(p, true)));
            foreach (var prefab in AssetDatabase.FindAssets("t:Prefab", new[] { $"{PackRoot}/Demo/Environment/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath))
                keep.UnionWith(AssetDatabase.GetDependencies(prefab, true));
            var moved = new List<string>();
            foreach (var dir in new[] { "Scenes", "Materials", "Settings", "Textures", "Shaders", "Environment/Materials", "Environment/Textures" })
            {
                var folder = $"{PackRoot}/Demo/{dir}";
                if (!AssetDatabase.IsValidFolder(folder)) continue;
                foreach (var path in AssetDatabase.FindAssets("", new[] { folder }).Select(AssetDatabase.GUIDToAssetPath).Distinct()
                             .Where(p => !AssetDatabase.IsValidFolder(p) && Path.GetDirectoryName(p).Replace('\\', '/') == folder).ToList())
                {
                    if (keep.Contains(path)) continue;
                    MoveToDev(path);
                    moved.Add(path.Substring(PackRoot.Length + 1));
                }
            }
            return $"moved to {DevRoot}: {moved.Count}\n  " + string.Join("\n  ", moved);
        }

        public static void MoveToDev(string path)
        {
            var dst = DevPath(path);
            EnsureFolder(Path.GetDirectoryName(dst).Replace('\\', '/'));
            if (AssetDatabase.LoadMainAssetAtPath(dst) != null) AssetDatabase.DeleteAsset(dst);
            var error = AssetDatabase.MoveAsset(path, dst);
            if (!string.IsNullOrEmpty(error)) throw new System.InvalidOperationException($"move {path} -> {dst}: {error}");
        }

        public static void EnsureFolder(string folder)
        {
            if (AssetDatabase.IsValidFolder(folder)) return;
            var parent = Path.GetDirectoryName(folder).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(folder));
        }

        /// <summary>Hook at the end of FarmMachinerySceneBuilder.Build: a non-shipped scene (media, catalogue sheets) and the
        /// backdrop / zone materials PackSceneBuilder generated for it go to the dev folder; a shipped scene keeps only the
        /// generated materials it really uses and gets its camera setup again.</summary>
        public static string AfterSceneBuild(string sceneName)
        {
            var scene = ScenePath(sceneName);
            if (!File.Exists(scene)) return "";
            var used = new HashSet<string>(AssetDatabase.GetDependencies(scene, true));
            var generated = AssetDatabase.FindAssets("t:Material", new[] { $"{PackRoot}/Demo/Materials" }).Select(AssetDatabase.GUIDToAssetPath)
                .Where(p => Path.GetFileName(p).StartsWith($"M_Demo_Backdrop_{sceneName}.") || Path.GetFileName(p).StartsWith($"M_Demo_Zone_{sceneName}_")).ToList();
            var log = new StringBuilder();
            if (!Shipped(sceneName))
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                MoveToDev(scene);
                foreach (var p in generated) MoveToDev(p);
                EditorSceneManager.OpenScene(DevPath(scene));
                log.AppendLine($"dev scene -> {DevPath(scene)} (+{generated.Count} generated materials)");
            }
            else
            {
                foreach (var p in generated.Where(p => !used.Contains(p))) { MoveToDev(p); log.AppendLine($"unused {p} -> dev"); }
                if (MainCamera.TryGetValue(sceneName, out var cam)) log.AppendLine(PrepareShippedScene(sceneName, cam));
            }
            AssetDatabase.SaveAssets();
            return log.ToString();
        }

        /// <summary>Environment prefabs use the accepted LOOK v2 materials directly (the base / soft A/B materials are dev-only).
        /// FarmMachineryLookV2.Apply still swaps base → v2 on scene instances, so rebuilt scenes look the same.</summary>
        [MenuItem("Tools/Farm Machinery/Release/Use V2 Environment Materials")]
        public static string UseV2EnvironmentMaterials()
        {
            var map = new Dictionary<Material, Material>();
            void Pair(string baseName, string v2Path)
            {
                var v2 = AssetDatabase.LoadAssetAtPath<Material>(v2Path);
                foreach (var b in AssetDatabase.FindAssets($"t:Material {baseName}", new[] { PackRoot, DevRoot }).Select(AssetDatabase.GUIDToAssetPath)
                             .Where(p => Path.GetFileNameWithoutExtension(p) == baseName).Select(AssetDatabase.LoadAssetAtPath<Material>))
                    if (b != null && v2 != null) map[b] = v2;
            }
            Pair("M_FarmMachinery_Demo", FarmMachineryLookV2.DemoSoftMaterialPath);
            Pair("M_FarmMachinery_Demo2", FarmMachineryLookV2.Demo2V2MaterialPath);
            Pair("M_FarmMachinery_Demo_Cloud", FarmMachineryLookV2.CloudV2MaterialPath);
            var changed = 0;
            foreach (var path in AssetDatabase.FindAssets("t:Prefab", new[] { $"{PackRoot}/Demo/Environment/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath))
            {
                var root = PrefabUtility.LoadPrefabContents(path);
                var dirty = false;
                foreach (var r in root.GetComponentsInChildren<Renderer>(true))
                {
                    var mats = r.sharedMaterials;
                    for (var i = 0; i < mats.Length; i++)
                        if (mats[i] != null && map.TryGetValue(mats[i], out var v2)) { mats[i] = v2; dirty = true; }
                    if (dirty) r.sharedMaterials = mats;
                }
                if (dirty) { PrefabUtility.SaveAsPrefabAsset(root, path); changed++; }
                PrefabUtility.UnloadPrefabContents(root);
            }
            // the v2 cloud material was cloned from a lit material: drop texture slots its shader does not have (stale atlas ref)
            var cleared = 0;
            foreach (var mat in map.Values.Distinct())
                foreach (var name in mat.GetTexturePropertyNames())
                    if (mat.shader.FindPropertyIndex(name) < 0 && mat.GetTexture(name) != null) { mat.SetTexture(name, null); EditorUtility.SetDirty(mat); cleared++; }
            AssetDatabase.SaveAssets();
            return $"environment prefabs switched to v2 materials: {changed} ({map.Count} material pairs), stale texture slots cleared {cleared}";
        }

        /// <summary>Shipped catalogue scene from a catalogue sheet scene: all prefabs in rows, one camera ("Main Camera"), the
        /// backdrop on a shipped neutral material.</summary>
        public static string MakeCatalogScene(string sourceScene, string targetName)
        {
            var src = File.Exists(ScenePath(sourceScene)) ? ScenePath(sourceScene) : DevPath(ScenePath(sourceScene));
            var scene = EditorSceneManager.OpenScene(src, OpenSceneMode.Single);
            var root = scene.GetRootGameObjects().First(g => g.name == FarmMachineryPackBuilder.Config.Tag + "_Demo").transform;
            var backdrop = root.Find("Backdrop_Ground");
            if (backdrop != null)
            {
                var mat = AssetDatabase.LoadAssetAtPath<Material>(CatalogBackdrop);
                if (mat == null)
                {
                    mat = new Material(backdrop.GetComponent<Renderer>().sharedMaterial);
                    AssetDatabase.CreateAsset(mat, CatalogBackdrop);
                }
                backdrop.GetComponent<Renderer>().sharedMaterial = mat;
            }
            var cams = root.GetComponentsInChildren<Camera>(true);
            for (var i = 0; i < cams.Length; i++)
            {
                if (i == 0) { cams[i].gameObject.name = "Main Camera"; cams[i].gameObject.tag = "MainCamera"; cams[i].gameObject.SetActive(true); }
                else cams[i].gameObject.SetActive(false);
            }
            EditorSceneManager.SaveScene(scene, ScenePath(targetName));
            return $"{targetName}: from {src}, {cams.Length} camera(s), units {root.Cast<Transform>().Count(t => t.name.StartsWith("Unit_"))}";
        }

        /// <summary>One active camera (tag MainCamera) so the Game view is predictable; the other shot cameras stay as inactive
        /// viewpoints.</summary>
        public static string PrepareShippedScene(string sceneName, string mainCamera)
        {
            var scene = EditorSceneManager.OpenScene(ScenePath(sceneName), OpenSceneMode.Single);
            var root = scene.GetRootGameObjects().First(g => g.name == FarmMachineryPackBuilder.Config.Tag + "_Demo").transform;
            var names = new List<string>();
            foreach (var cam in root.GetComponentsInChildren<Camera>(true))
            {
                var main = cam.gameObject.name == mainCamera;
                cam.gameObject.SetActive(main);
                cam.gameObject.tag = main ? "MainCamera" : "Untagged";
                names.Add(cam.gameObject.name + (main ? "*" : ""));
            }
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            return $"{sceneName}: cameras {string.Join(", ", names)}";
        }

        // ------------------------------------------------------------------ package contents

        public static List<string> FullAssets() => AssetDatabase.FindAssets("", new[] { PackRoot }).Select(AssetDatabase.GUIDToAssetPath).Distinct()
            .Where(p => !AssetDatabase.IsValidFolder(p) && !p.EndsWith("/README_Lite.txt") && !p.EndsWith("/Demo_Catalog_Lite.unity")).OrderBy(p => p).ToList();   // Lite-only files

        public static List<string> LiteAssets()
        {
            var roots = new List<string>();
            foreach (var item in FarmMachineryCatalog.Items.Where(i => i.Lite))
            {
                roots.Add(FarmMachineryCatalog.BasePath(item.Id));
                roots.AddRange(FarmMachineryCatalog.Variants.Where(v => v.Id == item.Id).Select(v => FarmMachineryCatalog.PrefabPath(v.Id, v.Variant)));
            }
            roots.AddRange(FarmMachineryCatalog.Compositions.Take(3).Select(c => $"{PackRoot}/Art/Prefabs/CMP/{FarmMachineryCatalog.Prefix}{c.Name}.prefab"));
            roots.AddRange(LiteScenes.Select(ScenePath));
            var set = new HashSet<string>(AssetDatabase.GetDependencies(roots.ToArray(), true).Where(p => p.StartsWith(PackRoot + "/")));
            // Green / Blue materials ship with Lite: implements and trailers are recoloured by swapping the material (README)
            foreach (var p in AssetDatabase.FindAssets("", new[] { $"{PackRoot}/Art/Materials", $"{PackRoot}/Art/Textures" }).Select(AssetDatabase.GUIDToAssetPath))
                set.Add(p);
            set.Add($"{DocDir}/README_Lite.txt");
            set.Add($"{DocDir}/Changelog.txt");
            return set.Where(p => !AssetDatabase.IsValidFolder(p)).OrderBy(p => p).ToList();
        }

        /// <summary>Dependencies of the shipped files that lie outside the shipped set (must be empty), and Full-only files that
        /// the Lite set would pull in (must be empty).</summary>
        [MenuItem("Tools/Farm Machinery/Release/Check Dependencies")]
        public static string CheckShippedDependencies()
        {
            var full = FullAssets();
            var fullSet = new HashSet<string>(full);
            var outside = AssetDatabase.GetDependencies(full.ToArray(), true)
                .Where(p => !fullSet.Contains(p) && !p.StartsWith("Packages/")).Distinct().ToList();
            var lite = LiteAssets();
            var liteSet = new HashSet<string>(lite);
            var liteOutside = AssetDatabase.GetDependencies(lite.ToArray(), true).Where(p => !liteSet.Contains(p) && !p.StartsWith("Packages/")).Distinct().ToList();
            var fullOnlyModels = FarmMachineryCatalog.Items.Where(i => !i.Lite).Select(i => $"/{FarmMachineryCatalog.Prefix}{i.Name}").ToList();
            var liteFullOnly = lite.Where(p => p.Contains("/Art/") && fullOnlyModels.Any(m => p.Contains(m + ".") || p.Contains(m + "_"))).ToList();
            var packages = AssetDatabase.GetDependencies(full.ToArray(), true).Where(p => p.StartsWith("Packages/"))
                .Select(p => p.Split('/')[1]).Distinct().OrderBy(p => p).ToList();
            return $"full files {full.Count}, lite files {lite.Count}\n" +
                   $"full deps outside the pack: {outside.Count} {string.Join(", ", outside)}\n" +
                   $"lite deps outside the lite set: {liteOutside.Count} {string.Join(", ", liteOutside)}\n" +
                   $"full-only art in lite: {liteFullOnly.Count} {string.Join(", ", liteFullOnly)}\n" +
                   $"package dependencies: {string.Join(", ", packages)}";
        }

        [MenuItem("Tools/Farm Machinery/Release/Export Packages")]
        public static string Export()
        {
            Directory.CreateDirectory(ExportDir);
            var log = new StringBuilder();
            foreach (var (name, files) in new[] { ($"FarmMachinery_{Version}", FullAssets()), ($"FarmMachinery_Lite_{Version}", LiteAssets()) })
            {
                var path = $"{ExportDir}/{name}.unitypackage";
                AssetDatabase.ExportPackage(files.ToArray(), path, ExportPackageOptions.Default);
                File.WriteAllLines($"{ExportDir}/{name}_files.txt", files.Select(f => $"{AssetDatabase.AssetPathToGUID(f)}  {f}"));
                log.AppendLine($"{path}: {files.Count} files, {new FileInfo(path).Length} bytes");
            }
            return log.ToString();
        }

        /// <summary>Names from the README that no shipped prefab contains (documentation check).</summary>
        public static string MissingNames(string spaceSeparated)
        {
            var names = new HashSet<string>();
            foreach (var path in AssetDatabase.FindAssets("t:Prefab", new[] { $"{PackRoot}/Art/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath))
                foreach (var t in AssetDatabase.LoadAssetAtPath<GameObject>(path).GetComponentsInChildren<Transform>(true)) names.Add(t.name);
            return "missing: " + string.Join(" ", spaceSeparated.Split(' ').Where(n => !names.Contains(n)));
        }

        // ------------------------------------------------------------------ Asset Store Tools validator (internal API)

        [MenuItem("Tools/Farm Machinery/Release/Validate")]
        public static string Validate() => Validate(PackRoot, "3D");

        public static string Validate(string folder, string category)
        {
            var asm = System.AppDomain.CurrentDomain.GetAssemblies().First(a => a.GetName().Name == "asset-store-tools-editor" || a.GetType("AssetStoreTools.Validator.CurrentProjectValidator") != null);
            var settingsType = asm.GetType("AssetStoreTools.Validator.Data.CurrentProjectValidationSettings");
            var settings = System.Activator.CreateInstance(settingsType);
            settingsType.GetField("ValidationPaths").SetValue(settings, new List<string> { folder });
            var vtype = asm.GetType("AssetStoreTools.Validator.Data.ValidationType");
            settingsType.GetField("ValidationType").SetValue(settings, System.Enum.Parse(vtype, "UnityPackage"));
            settingsType.BaseType.GetField("Category").SetValue(settings, category);
            var validator = System.Activator.CreateInstance(asm.GetType("AssetStoreTools.Validator.CurrentProjectValidator"),
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic, null, new[] { settings }, null);
            var result = validator.GetType().GetMethod("Validate").Invoke(validator, null);
            EditorUtility.ClearProgressBar();
            var rt = result.GetType();
            var sb = new StringBuilder($"validator {folder} (category '{category}'): status {rt.GetField("Status").GetValue(result)}");
            var ex = rt.GetField("Exception").GetValue(result);
            if (ex != null) sb.Append($" exception {ex}");
            sb.AppendLine();
            foreach (var test in (System.Collections.IEnumerable)rt.GetField("Tests").GetValue(result))
            {
                var tt = test.GetType();
                var title = tt.GetField("Title").GetValue(test);
                var res = tt.GetField("Result").GetValue(test);
                var status = res.GetType().GetField("Status").GetValue(res);
                var count = (int)res.GetType().GetProperty("MessageCount").GetValue(res);
                sb.AppendLine($"  [{status}] {title}");
                for (var i = 0; i < count && status.ToString() != "Pass"; i++)
                {
                    var msg = res.GetType().GetMethod("GetMessage").Invoke(res, new object[] { i });
                    var text = (string)msg.GetType().GetMethod("GetText").Invoke(msg, null);
                    var objs = (int)msg.GetType().GetProperty("MessageObjectCount").GetValue(msg);
                    var names = new List<string>();
                    for (var o = 0; o < objs && o < 12; o++)
                    {
                        var mo = msg.GetType().GetMethod("GetMessageObject").Invoke(msg, new object[] { o });
                        var obj = mo.GetType().GetMethod("GetObject")?.Invoke(mo, null) as Object;
                        names.Add(obj != null ? AssetDatabase.GetAssetPath(obj) is var ap && ap.Length > 0 ? ap : obj.name : "?");
                    }
                    sb.AppendLine($"      - {text.Replace("\n", " ")}{(names.Count > 0 ? " :: " + string.Join("; ", names) + (objs > 12 ? $" (+{objs - 12})" : "") : "")}");
                }
            }
            return sb.ToString();
        }
    }
}
