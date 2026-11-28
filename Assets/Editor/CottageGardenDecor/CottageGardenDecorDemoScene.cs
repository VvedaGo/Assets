using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using PackTools.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace CottageGardenDecor.Editor
{
    /// <summary>
    /// Demo_CottageGarden (Э10): PackSceneBuilder builds the garden and the six composition prefabs from
    /// planning/CottageGardenDecor/layouts/Demo_CottageGarden.txt; this wrapper step then stages the series floating-island
    /// look (approach of Farm Machinery's FarmMachinerySceneBuilder, own code): demo island + path instead of the flat
    /// backdrop, gradient sky, white unlit clouds per shot, warm key light, trilight ambient, a post Volume, and re-renders the
    /// shots. Demo environment DEM-01..03 lives in Assets/CottageGardenDecor/Demo/{Meshes,Textures,Materials,Prefabs,Shaders}
    /// (demo-only, removable, not pack models). Layout lines read here start with '#!' (comments for PackSceneBuilder):
    ///   #! island                                  island + path prefabs at the origin (lawn top y 0)
    ///   #! sun dx dy dz intensity                  key light direction (travel direction) and intensity
    ///   #! sky                                     gradient sky material, shot cameras clear to the skybox
    ///   #! turn &lt;CompName&gt; yaw                     yaw of a composition instance about its origin (prefab root stays identity)
    ///   #! cloud &lt;shot&gt; &lt;A..E&gt; u v dist scale rotY   cloud on the camera ray through viewport (u, v); only active in that shot
    /// </summary>
    public static class CottageGardenDecorDemoScene
    {
        private static PackConfig C => CottageGardenDecorPackBuilder.Config;
        public const string LayoutFile = "Demo_CottageGarden.txt";
        public const string SceneName = "Demo_CottageGarden";
        private static string Demo => C.DemoDir;
        private static string MeshDir => Demo + "/Meshes";
        private static string PrefabDir => Demo + "/Prefabs";
        private static string MaterialDir => Demo + "/Materials";
        private static string AtlasPath => Demo + "/Textures/FMS_Garden_Demo_Atlas.png";
        private static string VolumePath => Demo + "/Settings/FMS_Garden_Demo_Volume.asset";
        private static readonly string[] CloudNames = { "A", "B", "C", "D", "E" };
        private static readonly Color Haze = new Color(0.74f, 0.84f, 0.95f);   // aerial depth in the sky horizon colour
        public static float HazeDensity = 0.003f;

        // ---------------- look (series values, see .work/pipeline/CottageGardenDecor/scene_demo_report.md) ----------------
        public static class Look
        {
            public static Color SkyZenith = new Color(0.30f, 0.52f, 0.80f);
            public static Color SkyHorizon = new Color(0.29f, 0.52f, 0.79f);   // the cameras look down: frame top ≈ near the horizon (deep blue)
            public static Color SkyBelow = new Color(0.86f, 0.93f, 0.99f);     // frame bottom (light)
            public static float SkySharpness = 1.6f;
        }

        [MenuItem("Tools/Cottage Garden Decor/Import Demo Environment")]
        public static string ImportEnvironment()
        {
            Directory.CreateDirectory(PrefabDir);
            Directory.CreateDirectory(MaterialDir);
            var tex = (TextureImporter)AssetImporter.GetAtPath(AtlasPath) ?? throw new FileNotFoundException(AtlasPath);
            if (tex.filterMode != FilterMode.Point || tex.mipmapEnabled)
            {
                tex.filterMode = FilterMode.Point;                 // flat-colour atlas cells must not bleed (as PackPrefabBuilder)
                tex.mipmapEnabled = false;
                tex.textureCompression = TextureImporterCompression.Uncompressed;
                tex.SaveAndReimport();
            }
            foreach (var name in new[] { "Island", "Path", "Clouds" })
            {
                var path = $"{MeshDir}/FMS_Garden_Demo_{name}.fbx";
                var mi = (ModelImporter)AssetImporter.GetAtPath(path) ?? throw new FileNotFoundException(path);
                if (mi.materialImportMode == ModelImporterMaterialImportMode.None && !mi.isReadable) continue;
                mi.materialImportMode = ModelImporterMaterialImportMode.None;
                mi.importCameras = false; mi.importLights = false; mi.importAnimation = false;
                mi.animationType = ModelImporterAnimationType.None;
                mi.isReadable = false;
                mi.meshCompression = ModelImporterMeshCompression.Off;
                mi.importNormals = ModelImporterNormals.Import;
                mi.SaveAndReimport();
            }

            var mat = Material("FMS_Garden_Demo_Atlas", "Universal Render Pipeline/Lit");
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(AtlasPath));
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Smoothness", 0.1f);
            EditorUtility.SetDirty(mat);
            var cloud = Material("FMS_Garden_Demo_Cloud", "CottageGardenDecor/Demo/Cloud");

            var log = new System.Text.StringBuilder();
            foreach (var name in new[] { "Island", "Path" })
            {
                var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{MeshDir}/FMS_Garden_Demo_{name}.fbx"));
                PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.OutermostRoot, InteractionMode.AutomatedAction);
                go.name = "FMS_Garden_Demo_" + name;
                foreach (var r in go.GetComponentsInChildren<Renderer>())
                {
                    r.sharedMaterials = Enumerable.Repeat(mat, r.sharedMaterials.Length).ToArray();
                    r.shadowCastingMode = name == "Path" ? ShadowCastingMode.Off : ShadowCastingMode.On;
                    r.receiveShadows = true;
                }
                PrefabUtility.SaveAsPrefabAsset(go, $"{PrefabDir}/{go.name}.prefab");
                Object.DestroyImmediate(go);
                log.AppendLine($"{PrefabDir}/FMS_Garden_Demo_{name}.prefab");
            }
            var clouds = AssetDatabase.LoadAssetAtPath<GameObject>($"{MeshDir}/FMS_Garden_Demo_Clouds.fbx");
            foreach (var letter in CloudNames)
            {
                var child = clouds.transform.Cast<Transform>().FirstOrDefault(t => t.name.EndsWith("Cloud_" + letter))
                            ?? throw new System.InvalidOperationException("Cloud_" + letter + " missing in the clouds FBX");
                var root = new GameObject("FMS_Garden_Demo_Cloud_" + letter);
                var piece = Object.Instantiate(child.gameObject, root.transform);
                piece.name = "Cloud_" + letter;
                piece.transform.localPosition = Vector3.zero;      // each cloud's origin = its own bottom centre
                foreach (var r in piece.GetComponentsInChildren<Renderer>())
                {
                    r.sharedMaterials = Enumerable.Repeat(cloud, r.sharedMaterials.Length).ToArray();
                    r.shadowCastingMode = ShadowCastingMode.Off;
                    r.receiveShadows = false;
                }
                PrefabUtility.SaveAsPrefabAsset(root, $"{PrefabDir}/{root.name}.prefab");
                Object.DestroyImmediate(root);
                log.AppendLine($"{PrefabDir}/FMS_Garden_Demo_Cloud_{letter}.prefab");
            }
            AssetDatabase.SaveAssets();
            Debug.Log("[CottageGardenDecor] demo environment:\n" + log);
            return log.ToString();
        }

        [MenuItem("Tools/Cottage Garden Decor/Build Demo Scene")]
        public static string Build() => Build(true);

        /// <summary>PackSceneBuilder pass (scene + composition prefabs), then the environment step and the final shot renders.</summary>
        public static string Build(bool savePrefabs)
        {
            var log = new System.Text.StringBuilder(PackSceneBuilder.Build(C, LayoutFile, SceneName, savePrefabs));
            log.Append(Environment());
            log.AppendLine(CottageGardenDecorSceneFinalize.Finalize(SceneName));   // ship with one Main Camera
            return log.ToString();
        }

        private sealed class Shot { public string Name; public int W, H; public Camera Cam; public Transform Clouds; }

        private static string Environment()
        {
            var log = new System.Text.StringBuilder();
            var root = GameObject.Find(C.Tag + "_Demo").transform;
            var lines = File.ReadAllLines($"{C.LayoutDir}/{LayoutFile}").Select(l => l.Trim()).ToList();
            var shots = new List<Shot>();
            foreach (var l in lines.Where(l => l.StartsWith("shot ")))
            {
                var t = Split(l);
                var cam = root.Find("Cam_" + t[1]).GetComponent<Camera>();
                var s = new Shot { Name = t[1], W = t.Length > 10 ? int.Parse(t[9]) : 1920, H = t.Length > 10 ? int.Parse(t[10]) : 1080, Cam = cam };
                cam.aspect = s.W / (float)s.H;
                cam.farClipPlane = 400;
                cam.GetComponent<UniversalAdditionalCameraData>().renderPostProcessing = true;
                s.Clouds = new GameObject("Clouds_" + s.Name).transform;
                s.Clouds.SetParent(root, false);
                shots.Add(s);
            }

            log.Append(ZeroCompositionRoots(root));
            var backdrop = root.Find("Backdrop_Ground");
            if (backdrop != null) Object.DestroyImmediate(backdrop.gameObject);
            AssetDatabase.DeleteAsset($"{Demo}/Materials/M_Demo_Backdrop_{SceneName}.mat");

            foreach (var l in lines.Where(l => l.StartsWith("#!")))
            {
                var t = Split(l.Substring(2));
                if (t.Length == 0) continue;
                switch (t[0])
                {
                    case "island":
                        foreach (var name in new[] { "Island", "Path" })
                        {
                            var go = (GameObject)PrefabUtility.InstantiatePrefab(LoadDemo("FMS_Garden_Demo_" + name), root);
                            go.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
                        }
                        log.AppendLine("island + path at the origin");
                        break;
                    case "sun":
                        Sun(root, new Vector3(F(t[1]), F(t[2]), F(t[3])), F(t[4]));
                        log.AppendLine($"sun {t[1]} {t[2]} {t[3]} x{t[4]}");
                        break;
                    case "sky":
                        RenderSettings.skybox = SkyMaterial();
                        foreach (var s in shots) s.Cam.clearFlags = CameraClearFlags.Skybox;
                        log.AppendLine("gradient sky");
                        break;
                    case "turn":
                        var comp = root.Find(t[1]) ?? throw new System.InvalidOperationException("turn: no composition " + t[1]);
                        comp.localRotation = Quaternion.Euler(0, F(t[2]), 0);
                        log.AppendLine($"turn {t[1]} {t[2]}");
                        break;
                    case "cloud":
                        var shot = shots.First(s => s.Name == t[1]);
                        var cloud = (GameObject)PrefabUtility.InstantiatePrefab(LoadDemo("FMS_Garden_Demo_Cloud_" + t[2]), shot.Clouds);
                        var ray = shot.Cam.ViewportPointToRay(new Vector3(F(t[3]), F(t[4]), 0));
                        cloud.transform.position = ray.origin + ray.direction * F(t[5]);
                        cloud.transform.rotation = Quaternion.Euler(0, shot.Cam.transform.eulerAngles.y + F(t[7]), 0);
                        cloud.transform.localScale = Vector3.one * F(t[6]);
                        break;
                }
            }
            CottageGardenDecorLook.AddVolume(root, shots.Select(sh => sh.Cam).ToArray());
            CottageGardenDecorLook.Haze(Haze, HazeDensity);
            AssetDatabase.DeleteAsset(VolumePath);                  // old per-scene profile, replaced by FMS_Garden_Look
            log.Append(SaveAndRender(root, shots));
            Debug.Log("[CottageGardenDecor] demo environment step:\n" + log);
            return log.ToString();
        }

        /// <summary>PackSceneBuilder saves a composition root at its scene position; the catalogue wants root identity (origin =
        /// front centre of the plot, as the Farm Processing / Farm Machinery CMP prefabs). Zero the asset roots and keep the
        /// scene instances where the layout put them (root position is an instance override).</summary>
        private static string ZeroCompositionRoots(Transform root)
        {
            var log = new System.Text.StringBuilder();
            foreach (Transform comp in root)
            {
                if (!PrefabUtility.IsAnyPrefabInstanceRoot(comp.gameObject)) continue;
                var path = PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(comp.gameObject);
                if (!path.StartsWith(C.PrefabDir + "/CMP/")) continue;
                var pos = comp.localPosition;
                var contents = PrefabUtility.LoadPrefabContents(path);
                contents.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
                contents.transform.localScale = Vector3.one;
                PrefabUtility.SaveAsPrefabAsset(contents, path);
                PrefabUtility.UnloadPrefabContents(contents);
                comp.SetLocalPositionAndRotation(pos, Quaternion.identity);
                log.AppendLine($"{path}: root zeroed, instance at {pos}");
            }
            return log.ToString();
        }

        /// <summary>Frame share of the first object named <paramref name="name"/> under root: viewport x/y range (y from the top)
        /// of its mesh vertices, for the shot acceptance numbers (island / gazebo width, plate rows).</summary>
        private static string Share(Camera cam, Transform root, string name)
        {
            var go = root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
            if (go == null) return name + " ?";
            float x0 = 1, x1 = 0, y0 = 1, y1 = 0;
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null || mf.name.EndsWith("_Low1")) continue;
                foreach (var v in mf.sharedMesh.vertices)
                {
                    var p = cam.WorldToViewportPoint(mf.transform.TransformPoint(v));
                    x0 = Mathf.Min(x0, p.x); x1 = Mathf.Max(x1, p.x); y0 = Mathf.Min(y0, 1 - p.y); y1 = Mathf.Max(y1, 1 - p.y);
                }
            }
            return $"{name} x {x0:P0}-{x1:P0} (w {x1 - x0:P1}) y {y0:P0}-{y1:P0}";
        }

        private static void Sun(Transform root, Vector3 dir, float intensity)
        {
            CottageGardenDecorLook.ApplyLights(root);           // one look: the key intensity comes from CottageGardenDecorLook, not the layout
            root.Find("Key_Sun").localRotation = Quaternion.LookRotation(dir);
        }

        /// <summary>Saves the scene (first shot's clouds active) and renders every shot with the shared look.</summary>
        private static string SaveAndRender(Transform root, List<Shot> shots)
        {
            var log = new System.Text.StringBuilder();
            for (var i = 0; i < shots.Count; i++) shots[i].Clouds.gameObject.SetActive(i == 0);   // saved scene: first shot's sky
            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
            EditorSceneManager.SaveScene(root.gameObject.scene);
            var outDir = Path.Combine(Path.GetTempPath(), C.RenderTempDir);
            foreach (var s in shots)
            {
                foreach (var o in shots) o.Clouds.gameObject.SetActive(o == s);
                var file = Path.Combine(outDir, $"{SceneName}_{s.Name}.png");
                CottageGardenDecorLook.Render(s.Cam, file, s.W, s.H);
                log.AppendLine($"render {file} ({s.Clouds.childCount} clouds); {Share(s.Cam, root, "FMS_Garden_Demo_Island")}; {Share(s.Cam, root, "FMS_Garden_Gazebo")}");
            }
            for (var i = 0; i < shots.Count; i++) shots[i].Clouds.gameObject.SetActive(i == 0);
            return log.ToString();
        }

        /// <summary>Look pass only (no rebuild, composition prefabs untouched): opens the saved Demo_CottageGarden scene, applies
        /// the shared look (lights, Volume FMS_Garden_Look, haze), saves and re-renders the shots with the unchanged cameras.</summary>
        [MenuItem("Tools/Cottage Garden Decor/Re-render Demo Scene (look only)")]
        public static string Relook()
        {
            EditorSceneManager.OpenScene($"{Demo}/Scenes/{SceneName}.unity", OpenSceneMode.Single);
            var root = GameObject.Find(C.Tag + "_Demo").transform;
            var lines = File.ReadAllLines($"{C.LayoutDir}/{LayoutFile}").Select(l => l.Trim()).ToList();
            var shots = new List<Shot>();
            foreach (var l in lines.Where(l => l.StartsWith("shot ")))
            {
                var t = Split(l);
                var cam = root.Find("Cam_" + t[1]).GetComponent<Camera>();
                cam.aspect = int.Parse(t[9]) / float.Parse(t[10]);
                shots.Add(new Shot { Name = t[1], W = int.Parse(t[9]), H = int.Parse(t[10]), Cam = cam, Clouds = root.Find("Clouds_" + t[1]) });
            }
            var sun = Split(lines.First(l => l.StartsWith("#! sun")).Substring(2));
            Sun(root, new Vector3(F(sun[1]), F(sun[2]), F(sun[3])), F(sun[4]));
            foreach (var v in root.GetComponentsInChildren<Volume>(true)) Object.DestroyImmediate(v.gameObject);
            RenderSettings.skybox = SkyMaterial();
            CottageGardenDecorLook.AddVolume(root, shots.Select(sh => sh.Cam).ToArray());
            CottageGardenDecorLook.Haze(Haze, HazeDensity);
            AssetDatabase.DeleteAsset(VolumePath);
            var log = SaveAndRender(root, shots);
            Debug.Log("[CottageGardenDecor] relook:" + "\n" + log);
            return log + CottageGardenDecorSceneFinalize.Finalize(SceneName);
        }

        private static Material SkyMaterial()
        {
            var mat = Material("FMS_Garden_Demo_Sky", "CottageGardenDecor/Demo/Gradient Sky");
            mat.SetColor("_ZenithColor", Look.SkyZenith);
            mat.SetColor("_HorizonColor", Look.SkyHorizon);
            mat.SetColor("_BelowColor", Look.SkyBelow);
            mat.SetFloat("_BelowSharpness", Look.SkySharpness);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static Material Material(string name, string shader)
        {
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            var sh = Shader.Find(shader) ?? throw new System.InvalidOperationException("shader not found: " + shader);
            if (mat == null) { mat = new Material(sh); AssetDatabase.CreateAsset(mat, path); }
            else if (mat.shader != sh) mat.shader = sh;
            return mat;
        }

        private static GameObject LoadDemo(string name) =>
            AssetDatabase.LoadAssetAtPath<GameObject>($"{PrefabDir}/{name}.prefab")
            ?? throw new FileNotFoundException($"{PrefabDir}/{name}.prefab (run Import Demo Environment)");

        private static string[] Split(string s) => s.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
