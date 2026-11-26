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
    /// Release layout of Farm Machinery (owner request 2026-11-26): two shipped folders, no duplicated assets.
    ///   Assets/FarmMachinery/Lite  — everything Farm Machinery Lite needs (13 Lite models, their variants, CMP_01–03, shared
    ///                                materials / atlases, the demo look and environment the Lite scenes use, Demo_FieldWork,
    ///                                Demo_Catalog_Lite, README_Lite + Changelog).
    ///   Assets/FarmMachinery/Full  — only the Full-only content (13 models, variants, CMP_04–05, Full-only demo environment,
    ///                                Demo_Harvest, Demo_Catalog, README). Full references Lite assets; Lite never references Full.
    /// Packages: Lite = Assets/FarmMachinery + Lite; Full = Assets/FarmMachinery + Lite + Full (same GUIDs → in-place upgrade).
    /// The shared PackTools work under one PackConfig root, so every build runs <see cref="Staged"/>: the Full files are moved
    /// (GUIDs kept) into the Lite working root, the build runs, then <see cref="Unstage"/> moves everything outside the Lite
    /// dependency set back to Full. Dev-only content (media / catalogue shot scenes, A/B looks, generated backdrop / zone
    /// materials) lives in Assets/_FarmMachineryDev/Demo/... and is staged / moved back by the scene hooks.
    /// </summary>
    public static class FarmMachineryRelease
    {
        public const string PackRoot = "Assets/FarmMachinery";
        public const string LiteRoot = PackRoot + "/Lite";
        public const string FullRoot = PackRoot + "/Full";
        public const string DevRoot = "Assets/_FarmMachineryDev";
        public const string Version = "1.0.0";
        public static readonly string[] LiteScenes = { "Demo_FieldWork", "Demo_Catalog_Lite" };
        public static readonly string[] FullScenes = { "Demo_Harvest", "Demo_Catalog" };
        public static IEnumerable<string> ShippedScenes => LiteScenes.Concat(FullScenes);
        /// <summary>Camera that stays active in each shipped scene (the others are kept as inactive viewpoints).</summary>
        private static readonly Dictionary<string, string> MainCamera = new Dictionary<string, string>
        {
            ["Demo_FieldWork"] = "Cam_Overview", ["Demo_Harvest"] = "Cam_Overview",
        };
        public const string CatalogBackdrop = LiteRoot + "/Demo/Materials/M_FarmMachinery_Demo_CatalogBackdrop.mat";
        private const string ExportDir = ".work/export";

        /// <summary>Scene path in the working (staged) root, where builds create and save scenes.</summary>
        public static string WorkScenePath(string name) => $"{LiteRoot}/Demo/Scenes/{name}.unity";
        /// <summary>Home of a scene when nothing is staged.</summary>
        public static string ScenePath(string name) =>
            LiteScenes.Contains(name) ? WorkScenePath(name) : FullScenes.Contains(name) ? $"{FullRoot}/Demo/Scenes/{name}.unity" : DevPath(WorkScenePath(name));
        /// <summary>Lite (working) path → the same sub-path under the dev folder (Demo/...).</summary>
        public static string DevPath(string workPath) => DevRoot + workPath.Substring(LiteRoot.Length);
        public static bool Shipped(string sceneName) => ShippedScenes.Contains(sceneName);

        // ------------------------------------------------------------------ staging (one PackConfig root for the shared tools)

        private static int _stageDepth;
        public static bool IsStaged => _stageDepth > 0;

        public static string Staged(System.Func<string> work)
        {
            if (_stageDepth++ == 0) Stage();
            try { return work(); }
            finally { if (--_stageDepth == 0) Unstage(); }
        }

        private static List<string> FilesUnder(string root) => !AssetDatabase.IsValidFolder(root) ? new List<string>() :
            AssetDatabase.FindAssets("", new[] { root }).Select(AssetDatabase.GUIDToAssetPath).Distinct()
                .Where(p => !AssetDatabase.IsValidFolder(p)).OrderBy(p => p).ToList();

        private static List<string> FoldersUnder(string root) => !AssetDatabase.IsValidFolder(root) ? new List<string>() :
            AssetDatabase.GetSubFolders(root).SelectMany(f => new[] { f }.Concat(FoldersUnder(f))).ToList();

        /// <summary>Moves every Full file (except its Documentation) to the same sub-path under the Lite working root.</summary>
        public static string Stage()
        {
            var moved = 0;
            foreach (var p in FilesUnder(FullRoot).Where(p => !p.StartsWith(FullRoot + "/Documentation/")))
            {
                Move(p, LiteRoot + p.Substring(FullRoot.Length));
                moved++;
            }
            return $"staged {moved} Full files into {LiteRoot}";
        }

        /// <summary>Everything under the Lite working root that the Lite set does not need goes (back) to Full; then empty
        /// working folders are removed.</summary>
        public static string Unstage()
        {
            var lite = new HashSet<string>(LiteSetStaged());
            var moved = 0;
            foreach (var p in FilesUnder(LiteRoot).Where(p => !lite.Contains(p)))
            {
                Move(p, FullRoot + p.Substring(LiteRoot.Length));
                moved++;
            }
            foreach (var folder in FoldersUnder(LiteRoot).OrderByDescending(f => f.Length))
                if (FilesUnder(folder).Count == 0 && AssetDatabase.GetSubFolders(folder).Length == 0) AssetDatabase.DeleteAsset(folder);
            AssetDatabase.SaveAssets();
            return $"unstaged {moved} files to {FullRoot}";
        }

        /// <summary>Lite content, computed in the working root: Lite prefabs, variants, CMP_01–03, Lite scenes and all their
        /// dependencies; all product materials and atlases (implements are recoloured by material swap); Lite docs.</summary>
        private static IEnumerable<string> LiteSetStaged()
        {
            var roots = new List<string>();
            foreach (var item in FarmMachineryCatalog.Items.Where(i => i.Lite))
            {
                roots.Add(FarmMachineryCatalog.BasePath(item.Id));
                roots.AddRange(FarmMachineryCatalog.Variants.Where(v => v.Id == item.Id).Select(v => FarmMachineryCatalog.PrefabPath(v.Id, v.Variant)));
            }
            roots.AddRange(FarmMachineryCatalog.Compositions.Take(3).Select(c => $"{LiteRoot}/Art/Prefabs/CMP/{FarmMachineryCatalog.Prefix}{c.Name}.prefab"));
            roots.AddRange(LiteScenes.Select(WorkScenePath));
            roots = roots.Where(r => AssetDatabase.LoadMainAssetAtPath(r) != null).ToList();
            var set = new HashSet<string>(AssetDatabase.GetDependencies(roots.ToArray(), true).Where(p => p.StartsWith(LiteRoot + "/")));
            set.UnionWith(FilesUnder($"{LiteRoot}/Art/Materials"));
            set.UnionWith(FilesUnder($"{LiteRoot}/Art/Textures"));
            set.UnionWith(FilesUnder($"{LiteRoot}/Documentation"));
            return set;
        }

        private static void Move(string src, string dst)
        {
            if (src == dst) return;
            EnsureFolder(Path.GetDirectoryName(dst).Replace('\\', '/'));
            if (AssetDatabase.LoadMainAssetAtPath(dst) != null) throw new System.InvalidOperationException($"move {src}: {dst} exists");
            var error = AssetDatabase.MoveAsset(src, dst);
            if (!string.IsNullOrEmpty(error)) throw new System.InvalidOperationException($"move {src} -> {dst}: {error}");
        }

        // ------------------------------------------------------------------ one-time split and layout

        /// <summary>One-time split of the old single-root layout: Assets/FarmMachinery/{Art,Demo,Documentation} → Lite (folders
        /// moved, GUIDs kept), README.txt → Full/Documentation, then the Full-only files → Full.</summary>
        [MenuItem("Tools/Farm Machinery/Release/Split Lite And Full")]
        public static string SplitLiteFull()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            EnsureFolder(LiteRoot);
            foreach (var dir in new[] { "Art", "Demo", "Documentation" })
                if (AssetDatabase.IsValidFolder($"{PackRoot}/{dir}")) Move($"{PackRoot}/{dir}", $"{LiteRoot}/{dir}");
            var readme = $"{LiteRoot}/Documentation/README.txt";
            if (AssetDatabase.LoadMainAssetAtPath(readme) != null) Move(readme, $"{FullRoot}/Documentation/README.txt");
            return Unstage();
        }

        /// <summary>Full release preparation: V2 materials on the environment prefabs, catalogue scenes, shipped scene cameras,
        /// then everything not needed by the shipped scenes moves to the dev folder.</summary>
        [MenuItem("Tools/Farm Machinery/Release/Prepare Layout")]
        public static string PrepareLayout() => Staged(() =>
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
            return log.ToString();
        });

        /// <summary>Moves every Demo asset that no shipped scene and no environment prefab uses to the dev folder (staged).</summary>
        public static string MoveDevAssets()
        {
            var keep = new HashSet<string>(ShippedScenes.Select(WorkScenePath).Where(File.Exists)
                .SelectMany(p => AssetDatabase.GetDependencies(p, true)));
            foreach (var prefab in AssetDatabase.FindAssets("t:Prefab", new[] { $"{LiteRoot}/Demo/Environment/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath))
                keep.UnionWith(AssetDatabase.GetDependencies(prefab, true));
            var moved = new List<string>();
            foreach (var dir in new[] { "Scenes", "Materials", "Settings", "Textures", "Shaders", "Environment/Materials", "Environment/Textures" })
            {
                var folder = $"{LiteRoot}/Demo/{dir}";
                if (!AssetDatabase.IsValidFolder(folder)) continue;
                foreach (var path in FilesUnder(folder).Where(p => Path.GetDirectoryName(p).Replace('\\', '/') == folder))
                {
                    if (keep.Contains(path)) continue;
                    MoveToDev(path);
                    moved.Add(path.Substring(LiteRoot.Length + 1));
                }
            }
            return $"moved to {DevRoot}: {moved.Count}\n  " + string.Join("\n  ", moved);
        }

        public static void MoveToDev(string workPath)
        {
            var dst = DevPath(workPath);
            EnsureFolder(Path.GetDirectoryName(dst).Replace('\\', '/'));
            if (AssetDatabase.LoadMainAssetAtPath(dst) != null) AssetDatabase.DeleteAsset(dst);
            var error = AssetDatabase.MoveAsset(workPath, dst);
            if (!string.IsNullOrEmpty(error)) throw new System.InvalidOperationException($"move {workPath} -> {dst}: {error}");
        }

        public static void EnsureFolder(string folder)
        {
            if (AssetDatabase.IsValidFolder(folder)) return;
            var parent = Path.GetDirectoryName(folder).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(folder));
        }

        private static List<string> GeneratedMaterials(string folder, string sceneName) =>
            !AssetDatabase.IsValidFolder(folder) ? new List<string>() :
            AssetDatabase.FindAssets("t:Material", new[] { folder }).Select(AssetDatabase.GUIDToAssetPath)
                .Where(p => Path.GetFileName(p).StartsWith($"M_Demo_Backdrop_{sceneName}.") || Path.GetFileName(p).StartsWith($"M_Demo_Zone_{sceneName}_")).ToList();

        /// <summary>Hook at the start of a staged FarmMachinerySceneBuilder.Build: a dev scene and its generated materials come
        /// back to the working root so PackSceneBuilder overwrites them in place (GUIDs kept).</summary>
        public static void BeforeSceneBuild(string sceneName)
        {
            var work = WorkScenePath(sceneName);
            var dev = DevPath(work);
            if (AssetDatabase.LoadMainAssetAtPath(work) == null && AssetDatabase.LoadMainAssetAtPath(dev) != null)
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                Move(dev, work);
            }
            foreach (var p in GeneratedMaterials($"{DevRoot}/Demo/Materials", sceneName))
            {
                var dst = $"{LiteRoot}/Demo/Materials/{Path.GetFileName(p)}";
                if (AssetDatabase.LoadMainAssetAtPath(dst) == null) Move(p, dst);
            }
        }

        /// <summary>Hook at the end of a staged FarmMachinerySceneBuilder.Build: a non-shipped scene (media, catalogue sheets) and
        /// the backdrop / zone materials PackSceneBuilder generated for it go to the dev folder; a shipped scene keeps only the
        /// generated materials it really uses and gets its camera setup again (Unstage then moves Full scenes home).</summary>
        public static string AfterSceneBuild(string sceneName)
        {
            var scene = WorkScenePath(sceneName);
            if (!File.Exists(scene)) return "";
            var used = new HashSet<string>(AssetDatabase.GetDependencies(scene, true));
            var generated = GeneratedMaterials($"{LiteRoot}/Demo/Materials", sceneName);
            var log = new StringBuilder();
            if (!Shipped(sceneName))
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                MoveToDev(scene);
                foreach (var p in generated) MoveToDev(p);
                log.AppendLine($"dev scene -> {DevPath(scene)} (+{generated.Count} generated materials)");
            }
            else
            {
                foreach (var p in generated.Where(p => !used.Contains(p))) { MoveToDev(p); log.AppendLine($"unused {p} -> dev"); }
                if (MainCamera.TryGetValue(sceneName, out var cam)) log.AppendLine(PrepareShippedScene(sceneName, cam));
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);   // the file may move on Unstage
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
            var folders = new[] { $"{LiteRoot}/Demo/Environment/Prefabs", $"{FullRoot}/Demo/Environment/Prefabs" }.Where(AssetDatabase.IsValidFolder).ToArray();
            foreach (var path in AssetDatabase.FindAssets("t:Prefab", folders).Select(AssetDatabase.GUIDToAssetPath))
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

        /// <summary>Shipped catalogue scene from a catalogue sheet scene (staged): all prefabs in rows, one camera ("Main Camera"),
        /// the backdrop on a shipped neutral material.</summary>
        public static string MakeCatalogScene(string sourceScene, string targetName)
        {
            var src = File.Exists(WorkScenePath(sourceScene)) ? WorkScenePath(sourceScene) : DevPath(WorkScenePath(sourceScene));
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
            EditorSceneManager.SaveScene(scene, WorkScenePath(targetName));
            return $"{targetName}: from {src}, {cams.Length} camera(s)";
        }

        /// <summary>One active camera (tag MainCamera) so the Game view is predictable; the other shot cameras stay as inactive
        /// viewpoints.</summary>
        public static string PrepareShippedScene(string sceneName, string mainCamera)
        {
            var scene = EditorSceneManager.OpenScene(IsStaged ? WorkScenePath(sceneName) : ScenePath(sceneName), OpenSceneMode.Single);
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

        // ------------------------------------------------------------------ package contents (unstaged layout)

        /// <summary>Package entries: the shared Assets/FarmMachinery folder plus the given roots (folders and files).</summary>
        private static List<string> PackageEntries(params string[] roots) =>
            new[] { PackRoot }.Concat(roots).Concat(roots.SelectMany(FoldersUnder)).Concat(roots.SelectMany(FilesUnder)).Distinct().ToList();

        public static List<string> LiteFiles() => FilesUnder(LiteRoot);
        public static List<string> FullFiles() => FilesUnder(LiteRoot).Concat(FilesUnder(FullRoot)).ToList();

        /// <summary>Lite files may depend only on Lite (and packages); Full files only on Lite + Full; no Full-only model under Lite.</summary>
        [MenuItem("Tools/Farm Machinery/Release/Check Dependencies")]
        public static string CheckShippedDependencies()
        {
            if (IsStaged) return "staged: run unstaged";
            var lite = LiteFiles();
            var full = FullFiles();
            var liteOut = AssetDatabase.GetDependencies(lite.ToArray(), true).Where(p => !p.StartsWith(LiteRoot + "/") && !p.StartsWith("Packages/")).Distinct().ToList();
            var fullOut = AssetDatabase.GetDependencies(full.ToArray(), true).Where(p => !p.StartsWith(PackRoot + "/") && !p.StartsWith("Packages/")).Distinct().ToList();
            var perAsset = lite.Count(p => AssetDatabase.GetDependencies(p, true).Any(d => d.StartsWith(FullRoot + "/")));
            var fullOnlyModels = FarmMachineryCatalog.Items.Where(i => !i.Lite).Select(i => $"/{FarmMachineryCatalog.Prefix}{i.Name}").ToList();
            var liteFullOnly = lite.Where(p => p.Contains("/Art/") && fullOnlyModels.Any(m => p.Contains(m + ".") || p.Contains(m + "_"))).ToList();
            var packages = AssetDatabase.GetDependencies(full.ToArray(), true).Where(p => p.StartsWith("Packages/"))
                .Select(p => p.Split('/')[1]).Distinct().OrderBy(p => p).ToList();
            return $"lite files {lite.Count}, full-only files {full.Count - lite.Count}, full package files {full.Count}\n" +
                   $"lite deps outside Lite: {liteOut.Count} {string.Join(", ", liteOut)}\n" +
                   $"lite assets (checked one by one) that reference Full: {perAsset}\n" +
                   $"full deps outside the pack: {fullOut.Count} {string.Join(", ", fullOut)}\n" +
                   $"full-only art under Lite: {liteFullOnly.Count} {string.Join(", ", liteFullOnly)}\n" +
                   $"package dependencies: {string.Join(", ", packages)}";
        }

        [MenuItem("Tools/Farm Machinery/Release/Export Packages")]
        public static string Export()
        {
            if (IsStaged) return "staged: run unstaged";
            Directory.CreateDirectory(ExportDir);
            var log = new StringBuilder();
            foreach (var (name, entries) in new[] { ($"FarmMachinery_{Version}", PackageEntries(LiteRoot, FullRoot)), ($"FarmMachinery_Lite_{Version}", PackageEntries(LiteRoot)) })
            {
                var path = $"{ExportDir}/{name}.unitypackage";
                AssetDatabase.ExportPackage(entries.ToArray(), path, ExportPackageOptions.Default);
                var files = entries.Where(e => !AssetDatabase.IsValidFolder(e)).ToList();
                File.WriteAllLines($"{ExportDir}/{name}_files.txt", entries.Select(f => $"{AssetDatabase.AssetPathToGUID(f)}  {f}{(AssetDatabase.IsValidFolder(f) ? "/" : "")}"));
                log.AppendLine($"{path}: {files.Count} files + {entries.Count - files.Count} folders, {new FileInfo(path).Length} bytes");
            }
            return log.ToString();
        }

        /// <summary>Renders the active camera of each shipped scene to outDir/&lt;scene&gt;.png (1920×1080, same as the clean-import check).</summary>
        public static string RenderShippedScenes(string outDir)
        {
            Directory.CreateDirectory(outDir);
            var log = new StringBuilder();
            foreach (var name in ShippedScenes)
            {
                var scene = EditorSceneManager.OpenScene(ScenePath(name), OpenSceneMode.Single);
                var cam = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Camera>(false)).FirstOrDefault(c => c.isActiveAndEnabled);
                if (cam == null) { log.AppendLine($"{name}: no active camera"); continue; }
                var rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32);
                cam.targetTexture = rt;
                cam.Render(); cam.Render();
                RenderTexture.active = rt;
                var tex = new Texture2D(1920, 1080, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, 1920, 1080), 0, 0);
                tex.Apply();
                File.WriteAllBytes(Path.Combine(outDir, name + ".png"), tex.EncodeToPNG());
                RenderTexture.active = null; cam.targetTexture = null;
                Object.DestroyImmediate(rt); Object.DestroyImmediate(tex);
                log.AppendLine($"{name}: {cam.name}");
            }
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            return log.ToString();
        }

        // ------------------------------------------------------------------ 14_Unity editor shots (Э12 raw)

        /// <summary>Step 1 of a 14_Unity shot: prefab in Prefab Mode with its hierarchy expanded and the root selected (Inspector),
        /// the Project window showing the prefab's folder. Step 2 (<see cref="CaptureMainWindow"/>) runs in a later call, after
        /// the editor has repainted.</summary>
        public static string SetupUnityShot(string prefabPath)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            AssetDatabase.OpenAsset(prefab);
            var stage = UnityEditor.SceneManagement.PrefabStageUtility.GetCurrentPrefabStage();
            if (stage == null) return "no prefab stage";
            var root = stage.prefabContentsRoot;
            Selection.activeGameObject = root;
            var asm = typeof(EditorWindow).Assembly;
            var hierarchyType = asm.GetType("UnityEditor.SceneHierarchyWindow");
            foreach (var w in Resources.FindObjectsOfTypeAll(hierarchyType))
                hierarchyType.GetMethod("SetExpandedRecursive", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                    ?.Invoke(w, new object[] { root.GetInstanceID(), true });
            var folder = AssetDatabase.LoadAssetAtPath<Object>(Path.GetDirectoryName(prefabPath).Replace('\\', '/'));
            var browserType = asm.GetType("UnityEditor.ProjectBrowser");
            var widthField = browserType.GetField("m_DirectoriesAreaWidth", BindingFlags.Instance | BindingFlags.NonPublic);
            var shown = 0;
            foreach (var w in Resources.FindObjectsOfTypeAll(browserType))
            {
                if (widthField != null && !_savedDirWidth.ContainsKey(w)) { _savedDirWidth[w] = (float)widthField.GetValue(w); widthField.SetValue(w, 0f); }
                shown++;
            }
            EditorApplication.delayCall += () =>
            {
                foreach (var w in Resources.FindObjectsOfTypeAll(browserType))
                {
                    const BindingFlags any = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
                    var getId = browserType.GetMethods(any).First(m => m.Name == "GetFolderInstanceID" && m.GetParameters().Length == 1);
                    var id = getId.Invoke(getId.IsStatic ? null : w, new object[] { AssetDatabase.GetAssetPath(folder) });   // EntityId in Unity 6.3
                    browserType.GetMethods(any).First(m => m.Name == "ShowFolderContents" && m.GetParameters().Length == 2).Invoke(w, new[] { id, (object)false });
                    ((EditorWindow)w).Repaint();
                }
                foreach (var insp in Resources.FindObjectsOfTypeAll(asm.GetType("UnityEditor.InspectorWindow"))) ((EditorWindow)insp).Focus();
                Selection.activeGameObject = root;
                foreach (var ew in Resources.FindObjectsOfTypeAll<EditorWindow>()) ew.Repaint();
            };
            return $"prefab mode {prefab.name}, project windows {shown}, folder {AssetDatabase.GetAssetPath(folder)}";
        }

        /// <summary>Step 2: screen pixels of the main editor window → PNG (outPath).</summary>
        public static string CaptureMainWindow(string outPath)
        {
            var r = EditorGUIUtility.GetMainWindowPosition();
            var ppp = EditorGUIUtility.pixelsPerPoint;
            var w = Mathf.RoundToInt(r.width * ppp); var h = Mathf.RoundToInt(r.height * ppp);
            var pixels = UnityEditorInternal.InternalEditorUtility.ReadScreenPixel(r.position * ppp, w, h);
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.SetPixels(pixels);
            tex.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(outPath));
            File.WriteAllBytes(outPath, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            return $"{outPath}: {w}x{h}";
        }

        private static readonly Dictionary<Object, float> _savedDirWidth = new Dictionary<Object, float>();

        /// <summary>Back to the main stage, empty selection, Project folder trees restored, the given tab focused again.</summary>
        public static string EndUnityShot(string focusTabTitle)
        {
            var browserType = typeof(EditorWindow).Assembly.GetType("UnityEditor.ProjectBrowser");
            var widthField = browserType.GetField("m_DirectoriesAreaWidth", BindingFlags.Instance | BindingFlags.NonPublic);
            foreach (var kv in _savedDirWidth) if (kv.Key != null) { widthField.SetValue(kv.Key, kv.Value); ((EditorWindow)kv.Key).Repaint(); }
            _savedDirWidth.Clear();
            foreach (var w in Resources.FindObjectsOfTypeAll<EditorWindow>().Where(w => w.titleContent.text == focusTabTitle)) w.Focus();
            UnityEditor.SceneManagement.StageUtility.GoToMainStage();
            Selection.activeObject = null;
            return "main stage";
        }

        /// <summary>Names from the README that no shipped prefab contains (documentation check).</summary>
        public static string MissingNames(string spaceSeparated)
        {
            var names = new HashSet<string>();
            var folders = new[] { $"{LiteRoot}/Art/Prefabs", $"{FullRoot}/Art/Prefabs" }.Where(AssetDatabase.IsValidFolder).ToArray();
            foreach (var path in AssetDatabase.FindAssets("t:Prefab", folders).Select(AssetDatabase.GUIDToAssetPath))
                foreach (var t in AssetDatabase.LoadAssetAtPath<GameObject>(path).GetComponentsInChildren<Transform>(true)) names.Add(t.name);
            return "missing: " + string.Join(" ", spaceSeparated.Split(' ').Where(n => !names.Contains(n)));
        }

        // ------------------------------------------------------------------ Asset Store Tools validator (internal API)

        [MenuItem("Tools/Farm Machinery/Release/Validate")]
        public static string Validate() => Validate(PackRoot, "3D") + Validate(LiteRoot, "3D");

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
