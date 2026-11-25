using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using PackTools.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Farm Machinery demo scenes: built by the shared PackSceneBuilder from planning/FarmMachinery/layouts/&lt;Scene&gt;.txt, then
    /// the flat ground zones of the scene reference and the look are added and the shots rendered again (PackSceneBuilder has
    /// one ground colour and one neutral light only). '#!' lines are comments for PackSceneBuilder, read here
    /// (planning/FarmMachinery/SCENE_STYLE.md):
    ///   #! plane x0 z0 x1 z1                 resize the PackSceneBuilder ground plane (its far edge is the horizon line)
    ///   #! zone &lt;name&gt; r g b x0 z0 x1 z1     flat colour patch on the ground (layout space), later zones lie on top
    ///   #! look field|soft|v2|catalog|neutral  field = warm FarmMarket-like light + post volume (SCENE_STYLE.md "URP look");
    ///                                        soft = candidate softer grade (FarmMachinerySoftLook, Synty-like mood);
    ///                                        v2 = LOOK v2 (FarmMachineryLookV2, the accepted media grade);
    ///                                        neutral (default) = PackSceneBuilder light, no post (catalogue / item sheets)
    ///   #! shotlook &lt;shot&gt; neutral          post off for one shot of a field scene
    ///   #! sky [exposure] [rotation]        panorama skybox (Farm Nature sky solution, own copy), cameras clear to it
    ///   #! plane off                         remove the PackSceneBuilder ground plane (the island DEM-01 is the ground)
    ///   #! env &lt;KEY&gt; x z [rotY] [y] [sx sz]  one demo environment prefab (FarmMachineryEnvironment.PrefabPaths keys,
    ///                                        DEM-01…05, DEM-04_Corner, DEM-05_Grass|Flowers|Rock); rotY = plain Euler Y;
    ///                                        optional local x/z scale of the module (e.g. stretch road modules to the edge)
    ///   #! envrow &lt;KEY&gt; x0 z0 x1 z1 n [rotY] [y] [sx sz]   n copies on a line
    ///   #! scatter | cluster | border ...   props on the free island grass, see <see cref="ScatterAll"/>
    ///   #! clouds count seed dMin dMax yMin yMax sMin sMax   DEM-06 clouds on an elliptical ring around the island, see <see cref="Clouds"/>
    ///   #! aim &lt;object&gt; &lt;part&gt; &lt;outPoint&gt; &lt;targetObject&gt; [targetPart]   turn an auger / spout about its Y hinge over a target, see <see cref="Aim"/>
    ///   #! shothide shot name / shotmove shot name dx dy dz   per-shot hide / move (undone after that render)
    ///   #! catrows / catgroup / catrow / fit  catalogue sheets, see <see cref="FarmMachineryCatalogShots"/>
    /// Shots are rendered by <see cref="RenderShot"/> (PackSceneBuilder.Render with a 120 m shadow distance, for the island).
    /// </summary>
    public static class FarmMachinerySceneBuilder
    {
        public const string VolumePath = "Assets/_FarmMachineryDev/Demo/Settings/FarmMachinery_DemoVolume.asset";   // A/B look, dev-only (Э14)

        private static PackConfig C => FarmMachineryPackBuilder.Config;

        [MenuItem("Tools/Farm Machinery/Build Demo_FieldWork")]
        public static string BuildFieldWork() => Build("Demo_FieldWork");

        /// <summary>Builds the scene of planning/FarmMachinery/layouts/&lt;sceneName&gt;.txt; renders go to
        /// %TEMP%/&lt;RenderTempDir&gt;/&lt;sceneName&gt;_&lt;shot&gt;&lt;renderSuffix&gt;.png.</summary>
        public static string Build(string sceneName, string renderSuffix = "", string lookOverride = null)
        {
            var layout = $"{sceneName}.txt";
            var log = new StringBuilder(PackSceneBuilder.Build(C, layout, sceneName, savePrefabs: false));
            var scene = SceneManager.GetActiveScene();
            var root = scene.GetRootGameObjects().First(g => g.name == C.Tag + "_Demo").transform;

            var shots = new List<(string Name, int W, int H)>();
            var neutralShots = new HashSet<string>();
            var look = "neutral";
            float? skyExposure = null; var skyRotation = 0f;
            var zoneIndex = 0;
            var env = FarmMachineryEnvironment.PrefabPaths();
            Transform envRoot = null;
            var scatters = new List<string[]>();
            var cloudLines = new List<string[]>();
            GameObject PlaceEnv(string key, float x, float z, float rotY, float y) => PlaceEnvScaled(key, x, z, rotY, y, 1, 1);
            GameObject PlaceEnvScaled(string key, float x, float z, float rotY, float y, float sx, float sz)
            {
                if (envRoot == null) { envRoot = new GameObject("Environment").transform; envRoot.SetParent(root, false); }
                var prefab = env.TryGetValue(key, out var p) ? AssetDatabase.LoadAssetAtPath<GameObject>(p) : null;
                if (prefab == null) { log.AppendLine($"! missing environment prefab {key}"); return null; }
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, envRoot);
                go.transform.SetLocalPositionAndRotation(new Vector3(x, y, z), Quaternion.Euler(0, rotY, 0));
                if (sx != 1 || sz != 1) go.transform.localScale = new Vector3(sx, 1, sz);   // local axes of the module
                return go;
            }
            foreach (var raw in File.ReadAllLines($"{C.LayoutDir}/{layout}"))
            {
                var line = raw.Trim();
                var t = line.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
                if (t.Length == 0) continue;
                if (t[0] == "shot")
                    shots.Add((t[1], t.Length > 10 ? int.Parse(t[9]) : 1920, t.Length > 10 ? int.Parse(t[10]) : 1080));
                if (t[0] != "#!") continue;
                if (t[1] == "look") look = t[2];
                else if (t[1] == "sky") { skyExposure = Opt(t, 2, 1f); skyRotation = Opt(t, 3, 0f); }
                else if (t[1] == "shotlook" && t[3] == "neutral") neutralShots.Add(t[2]);
                else if (t[1] == "plane" && t[2] == "off")
                {
                    Object.DestroyImmediate(root.Find("Backdrop_Ground").gameObject);
                    log.AppendLine("ground plane removed");
                }
                else if (t[1] == "env")
                    PlaceEnvScaled(t[2], F(t[3]), F(t[4]), Opt(t, 5, 0), Opt(t, 6, 0), Opt(t, 7, 1), Opt(t, 8, 1));
                else if (t[1] == "envrow")
                {
                    var n = int.Parse(t[7]);
                    for (var i = 0; i < n; i++)
                    {
                        var k = n == 1 ? 0 : i / (float)(n - 1);
                        PlaceEnvScaled(t[2], Mathf.Lerp(F(t[3]), F(t[5]), k), Mathf.Lerp(F(t[4]), F(t[6]), k), Opt(t, 8, 0), Opt(t, 9, 0), Opt(t, 10, 1), Opt(t, 11, 1));
                    }
                }
                else if (t[1] == "scatter" || t[1] == "cluster" || t[1] == "border") scatters.Add(t);
                else if (t[1] == "clouds") cloudLines.Add(t);
                else if (t[1] == "aim") log.AppendLine(Aim(root, t));
                else if (t[1] == "plane")
                {
                    var ground = root.Find("Backdrop_Ground");   // Unity plane: 10 x 10 m at scale 1
                    float x0 = F(t[2]), z0 = F(t[3]), x1 = F(t[4]), z1 = F(t[5]);
                    ground.localPosition = new Vector3((x0 + x1) / 2, ground.localPosition.y, (z0 + z1) / 2);
                    ground.localScale = new Vector3(Mathf.Abs(x1 - x0) / 10, 1, Mathf.Abs(z1 - z0) / 10);
                    log.AppendLine($"ground plane {x0}..{x1} x {z0}..{z1}");
                }
                else if (t[1] == "zone")
                {
                    var color = new Color32((byte)int.Parse(t[3]), (byte)int.Parse(t[4]), (byte)int.Parse(t[5]), 255);
                    float x0 = F(t[6]), z0 = F(t[7]), x1 = F(t[8]), z1 = F(t[9]);
                    var zone = GameObject.CreatePrimitive(PrimitiveType.Quad);
                    zone.name = "Zone_" + t[2];
                    Object.DestroyImmediate(zone.GetComponent<Collider>());
                    zone.transform.SetParent(root, false);
                    // above the ground plane (y -0.002), below the machines (y 0); later zones a little higher
                    zone.transform.localPosition = new Vector3((x0 + x1) / 2, -0.0015f + 0.0002f * zoneIndex++, (z0 + z1) / 2);
                    zone.transform.localRotation = Quaternion.Euler(90, 0, 0);
                    zone.transform.localScale = new Vector3(Mathf.Abs(x1 - x0), Mathf.Abs(z1 - z0), 1);
                    zone.GetComponent<Renderer>().sharedMaterial = ZoneMaterial($"M_Demo_Zone_{sceneName}_{t[2]}", color);
                    log.AppendLine($"zone {t[2]} rgb {t[3]},{t[4]},{t[5]}  {x0}..{x1} x {z0}..{z1}");
                }
            }
            if (scatters.Count > 0) log.AppendLine(ScatterAll(envRoot, scatters, PlaceEnv));
            foreach (var t in cloudLines) log.AppendLine(Clouds(env.Keys.Where(k => k.StartsWith("DEM-06_")).OrderBy(k => k).ToList(), t, PlaceEnv));
            // catalogue sheets (Catalog_*.txt): rows by real bounds, attachments, technical overlays, fitted cameras
            log.Append(FarmMachineryCatalogShots.Apply(root, File.ReadAllLines($"{C.LayoutDir}/{layout}"),
                shots.GroupBy(sh => sh.Name).ToDictionary(g => g.Key, g => (g.First().W, g.First().H))));
            if (lookOverride != null) look = lookOverride;     // A/B renders of another look without editing the layout
            var postShots = shots.Select(sh => sh.Name).Where(n => !neutralShots.Contains(n)).ToList();
            if (look == "field") log.AppendLine(ApplyFieldLook(root, postShots));
            else if (look == "soft") log.AppendLine(FarmMachinerySoftLook.Apply(root, postShots));
            else if (look == "v2") log.AppendLine(FarmMachineryLookV2.Apply(root, postShots));
            if (skyExposure.HasValue)
            {
                log.AppendLine(ApplySky(root, shots.Select(sh => sh.Name).ToList(), skyExposure.Value, skyRotation));
                if (look == "soft") log.AppendLine(FarmMachinerySoftLook.Sky(skyExposure.Value));
                if (look == "v2") log.AppendLine(FarmMachineryLookV2.Sky(skyExposure.Value));
            }
            EditorSceneManager.SaveScene(scene);

            var outDir = Path.Combine(Path.GetTempPath(), C.RenderTempDir);
            // '#! shothide <shot> <name part>' / '#! shotmove <shot> <name part> dx dy dz': scene changes for one shot only
            // (e.g. a machine out of a low close-up), undone after its render
            var perShot = File.ReadAllLines($"{C.LayoutDir}/{layout}").Select(l => l.Trim().Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries))
                .Where(t => t.Length > 3 && t[0] == "#!" && (t[1] == "shothide" || t[1] == "shotmove")).ToList();
            foreach (var (name, w, h) in shots)
            {
                var cam = root.Find("Cam_" + name).GetComponent<Camera>();
                var path = Path.Combine(outDir, $"{sceneName}_{name}{renderSuffix}.png");
                var undo = new List<System.Action>();
                foreach (var t in perShot.Where(t => t[2] == name))
                    foreach (var tr in root.GetComponentsInChildren<Transform>(true).Where(x => x.name.Contains(t[3]) && (x.parent == null || !x.parent.name.Contains(t[3]))).ToList())
                    {
                        if (t[1] == "shothide") { var go = tr.gameObject; var was = go.activeSelf; go.SetActive(false); undo.Add(() => go.SetActive(was)); }
                        else { var p0 = tr.position; tr.position += new Vector3(F(t[4]), F(t[5]), F(t[6])); undo.Add(() => tr.position = p0); }
                        log.AppendLine($"{t[1]} {name}: {tr.name}");
                    }
                FarmMachineryCatalogShots.WarmUp(cam);   // objects toggled in this call render empty on the first Render
                RenderShot(cam, path, w, h);
                foreach (var u in undo) u();
                log.AppendLine("render " + path);
            }
            AssetDatabase.SaveAssets();
            log.Append(FarmMachineryRelease.AfterSceneBuild(sceneName));   // Э14: non-shipped scenes go to Assets/_FarmMachineryDev
            Debug.Log(log.ToString());
            return log.ToString();
        }

        /// <summary>
        /// Prop scatter on the free island grass; a point is kept only when a ray from above hits the island DEM-01 first (not a
        /// module, not a machine BoxCollider). Temporary MeshColliders on the environment while scattering. Deterministic per seed.
        ///   scatter KEYS count seed x0 z0 x1 z1 [s0 s1]                         uniform in the rectangle
        ///   cluster KEYS clusters perCluster radius seed x0 z0 x1 z1 [s0 s1]    clumps: centres uniform, points gaussian (sigma =
        ///                                                                       radius), each clump 0.5..1.5 x perCluster
        ///   border KEYS count width seed x0 z0 x1 z1 [s0 s1]                    a band outside the rectangle outline (field / road
        ///                                                                       edges), distance from the edge |gauss| * width
        /// KEYS = KEY:weight,...; each prop gets a random Y rotation, scale s0..s1 and a 0.85..1.25 height stretch.
        /// </summary>
        private static string ScatterAll(Transform envRoot, List<string[]> lines, System.Func<string, float, float, float, float, GameObject> place)
        {
            var temp = new List<Collider>();
            GameObject island = null;
            foreach (var mf in envRoot.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.GetComponent<Collider>() != null) continue;
                var c = mf.gameObject.AddComponent<MeshCollider>();
                c.sharedMesh = mf.sharedMesh;
                temp.Add(c);
                if (mf.name.Contains("IslandBase")) island = mf.gameObject;
            }
            Physics.SyncTransforms();
            var log = new StringBuilder();
            var total = 0;
            foreach (var t in lines)
            {
                var keys = t[2].Split(',').Select(k => k.Split(':')).Select(k => (Key: k[0], W: k.Length > 1 ? F(k[1]) : 1f)).ToList();
                var weight = keys.Sum(k => k.W);
                var mode = t[1];
                var a = mode == "cluster" ? 7 : mode == "border" ? 6 : 5;     // index of x0; the seed is just before it
                var random = new System.Random(int.Parse(t[a - 1]));
                float x0 = F(t[a]), z0 = F(t[a + 1]), x1 = F(t[a + 2]), z1 = F(t[a + 3]), s0 = Opt(t, a + 4, 0.8f), s1 = Opt(t, a + 5, 1.3f);
                float U() => (float)random.NextDouble();
                float Gauss() => Mathf.Sqrt(-2f * Mathf.Log(Mathf.Max(1e-6f, U()))) * Mathf.Cos(2f * Mathf.PI * U());
                var points = new List<Vector2>();
                if (mode == "scatter")
                    for (var i = 0; i < int.Parse(t[3]); i++) points.Add(new Vector2(Mathf.Lerp(x0, x1, U()), Mathf.Lerp(z0, z1, U())));
                else if (mode == "cluster")
                {
                    int clusters = int.Parse(t[3]), per = int.Parse(t[4]);
                    var radius = F(t[5]);
                    for (var c = 0; c < clusters; c++)
                    {
                        var centre = new Vector2(Mathf.Lerp(x0, x1, U()), Mathf.Lerp(z0, z1, U()));
                        var n = Mathf.RoundToInt(per * Mathf.Lerp(0.5f, 1.5f, U()));
                        for (var i = 0; i < n; i++) points.Add(centre + new Vector2(Gauss(), Gauss()) * radius);
                    }
                }
                else    // border: band outside the rectangle outline
                {
                    var width = F(t[4]);
                    float w = x1 - x0, h = z1 - z0, perimeter = 2 * (w + h);
                    for (var i = 0; i < int.Parse(t[3]); i++)
                    {
                        float s = U() * perimeter, d = Mathf.Abs(Gauss()) * width;
                        points.Add(s < w ? new Vector2(x0 + s, z0 - d)
                                 : s < w + h ? new Vector2(x1 + d, z0 + s - w)
                                 : s < 2 * w + h ? new Vector2(x1 - (s - w - h), z1 + d)
                                 : new Vector2(x0 - d, z1 - (s - 2 * w - h)));
                    }
                }
                var placed = 0;
                foreach (var p in points)
                {
                    var pick = U() * weight; var key = keys[0].Key;
                    foreach (var k in keys) { if (pick < k.W) { key = k.Key; break; } pick -= k.W; }
                    float rot = U() * 360f, scale = Mathf.Lerp(s0, s1, U()), stretch = Mathf.Lerp(0.85f, 1.25f, U());
                    if (!Physics.Raycast(new Vector3(p.x, 30, p.y), Vector3.down, out var hit, 60) || hit.collider.gameObject != island || hit.point.y < -0.05f) continue;
                    var go = place(key, p.x, p.y, rot, hit.point.y);
                    if (go == null) continue;
                    go.transform.localScale = new Vector3(scale, scale * stretch, scale);
                    placed++;
                }
                total += placed;
                log.AppendLine($"{mode} {t[2]}: {placed} of {points.Count} points on free island grass");
            }
            foreach (var c in temp) Object.DestroyImmediate(c);
            log.Append($"props scattered: {total}");
            return log.ToString();
        }

        /// <summary>
        /// '#! clouds count seed dMin dMax yMin yMax sMin sMax': DEM-06 clouds (random variant A..D, Y rotation, scale) on an elliptical
        /// ring around the island (half axes 32 + d and 22 + d, d = dMin..dMax m outside the island edge) at heights yMin..yMax
        /// (negative = below the island top): the Farm Nature floating-island look. Deterministic per seed.
        /// </summary>
        private static string Clouds(List<string> keys, string[] t, System.Func<string, float, float, float, float, GameObject> place)
        {
            if (keys.Count == 0) return "! clouds: no DEM-06 prefabs (run Import Demo Environment)";
            int count = int.Parse(t[2]);
            var random = new System.Random(int.Parse(t[3]));
            float U() => (float)random.NextDouble();
            float d0 = F(t[4]), d1 = F(t[5]), y0 = F(t[6]), y1 = F(t[7]), s0 = F(t[8]), s1 = F(t[9]);
            for (var i = 0; i < count; i++)
            {
                var a = (i + 0.35f * U()) / count * 2f * Mathf.PI;              // spread evenly around, jittered
                var d = Mathf.Lerp(d0, d1, U());
                var go = place(keys[random.Next(keys.Count)], Mathf.Cos(a) * (32f + d), Mathf.Sin(a) * (22f + d), U() * 360f, Mathf.Lerp(y0, y1, U()));
                if (go != null) go.transform.localScale = Vector3.one * Mathf.Lerp(s0, s1, U());
            }
            return $"clouds: {count} on a ring {d0}..{d1} m outside the island, y {y0}..{y1}";
        }

        /// <summary>
        /// '#! aim object part outPoint targetObject [targetPart]': turns the part of the object (unloading auger, forage spout) about
        /// its Y hinge so that its outlet point is over the centre of the target (its part, or the whole object) in plan.
        /// Objects are found by name: a path of name fragments separated by '/', each matched exactly first, then as a substring,
        /// among the descendants of the previous one (e.g. FMS_Mach_ForageHarvester, or CMP_04/Combine for a nested prefab).
        /// </summary>
        private static string Aim(Transform root, string[] t)
        {
            var obj = FindByPath(root, t[2]);
            var target = FindByPath(root, t[5]);
            if (obj == null || target == null) return $"! aim: {(obj == null ? t[2] : t[5])} not found";
            var targetTransform = t.Length > 6 ? FarmMachineryCatalog.Require(target.gameObject, t[6]) : target;
            var bounds = FarmMachineryCatalog.Lod0Bounds(targetTransform.GetComponentsInChildren<MeshRenderer>());
            var (angle, error) = FarmMachineryCatalog.AimPartY(obj.gameObject, t[3], t[4], bounds.center);
            var outY = FarmMachineryCatalog.Require(obj.gameObject, t[4]).position.y;
            return $"aim {obj.name}.{t[3]}: {angle} deg, outlet {error:F2} m (plan) from the {targetTransform.name} centre, Y {outY:F2} over its top {bounds.max.y:F2}";
        }

        private static Transform FindByPath(Transform root, string path)
        {
            var current = root;
            foreach (var token in path.Split('/'))
            {
                var all = current.GetComponentsInChildren<Transform>(true).Where(x => x != current).ToList();
                current = all.FirstOrDefault(x => x.name == token) ?? all.FirstOrDefault(x => x.name.Contains(token));
                if (current == null) return null;
            }
            return current;
        }

        /// <summary>PackSceneBuilder.Render with a longer shadow distance (the island is ~80 m deep from the overview camera).</summary>
        public static void RenderShot(Camera cam, string path, int width, int height, int supersample = 2, float shadowDistance = 120f)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var oldRes = urp.mainLightShadowmapResolution; var oldDist = urp.shadowDistance;
            urp.mainLightShadowmapResolution = 4096; urp.shadowDistance = shadowDistance;
            try
            {
                var rt = new RenderTexture(width * supersample, height * supersample, 24) { antiAliasing = 8 };
                cam.targetTexture = rt; cam.aspect = width / (float)height; cam.Render();
                var final = new RenderTexture(width, height, 0);
                Graphics.Blit(rt, final);
                RenderTexture.active = final;
                var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                File.WriteAllBytes(path, tex.EncodeToPNG());
                cam.targetTexture = null; RenderTexture.active = null;
                Object.DestroyImmediate(rt); Object.DestroyImmediate(final); Object.DestroyImmediate(tex);
            }
            finally { urp.mainLightShadowmapResolution = oldRes; urp.shadowDistance = oldDist; }
        }

        private static float Opt(string[] t, int i, float d) => t.Length > i ? F(t[i]) : d;

        public const string SkyPath = "Assets/_FarmMachineryDev/Demo/Settings/M_FarmMachinery_Sky.mat";   // field sky, dev-only (v2 sky ships)
        public const string SkyTexturePath = "Assets/_FarmMachineryDev/Demo/Textures/T_FarmMachinery_SkyPanorama.png";

        /// <summary>
        /// '#! sky [exposure] [rotation]': panorama skybox (shader FarmMachinery/Demo/URP Panorama Sky + T_FarmMachinery_SkyPanorama,
        /// the Farm Nature demo sky solution, own copy) instead of the flat `bg` colour: saturated blue zenith, warm cream band at
        /// the horizon, light blue below it (the cameras look down, so the lower half is the backdrop around the floating island).
        /// All shot cameras clear to the skybox. The panorama is a vertical gradient, so the rotation only matters for edits.
        /// </summary>
        private static string ApplySky(Transform root, List<string> shots, float exposure, float rotation)
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(SkyTexturePath)
                           ?? throw new System.InvalidOperationException($"{SkyTexturePath} missing");
            if (importer.mipmapEnabled || importer.wrapModeV != TextureWrapMode.Clamp || importer.textureCompression != TextureImporterCompression.Uncompressed)
            {
                importer.mipmapEnabled = false;                     // as the Farm Nature panorama: no mips, bilinear, uncompressed, sRGB
                importer.filterMode = FilterMode.Bilinear;
                importer.wrapModeU = TextureWrapMode.Repeat;
                importer.wrapModeV = TextureWrapMode.Clamp;         // no bleeding between zenith and nadir rows
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.sRGBTexture = true;
                importer.SaveAndReimport();
            }
            var shader = Shader.Find("FarmMachinery/Demo/URP Panorama Sky");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(SkyPath);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, SkyPath);
            }
            else if (mat.shader != shader) mat.shader = shader;     // the material existed with the earlier gradient-sky shader (GUID kept)
            mat.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(SkyTexturePath));
            mat.SetFloat("_Exposure", exposure);
            mat.SetFloat("_Rotation", rotation);
            EditorUtility.SetDirty(mat);
            RenderSettings.skybox = mat;
            foreach (var shot in shots) root.Find("Cam_" + shot).GetComponent<Camera>().clearFlags = CameraClearFlags.Skybox;
            return $"sky: panorama {SkyTexturePath} (exposure {exposure}, rotation {rotation}) -> {SkyPath}";
        }

        /// <summary>
        /// Warm outdoor look of the series (FarmMarket demo values, SCENE_STYLE.md "URP look"): sun, trilight ambient, optional linear
        /// fog in the sky colour (the plane edge melts into the sky), a global Volume with FarmMachinery_DemoVolume and
        /// post-processing on the given shot cameras. PackSceneBuilder's Key_Sun / Fill_Sky are re-used.
        /// </summary>
        private static string ApplyFieldLook(Transform root, List<string> postShots)
        {
            var key = root.Find("Key_Sun").GetComponent<Light>();
            key.color = Look.SunColor;
            key.intensity = Look.SunIntensity;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = Look.ShadowStrength;
            var fill = root.Find("Fill_Sky").GetComponent<Light>();
            fill.intensity = Look.FillIntensity;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = Look.AmbientSky;
            RenderSettings.ambientEquatorColor = Look.AmbientEquator;
            RenderSettings.ambientGroundColor = Look.AmbientGround;
            RenderSettings.fog = Look.Fog;   // off: at 45-160 m the URP linear fog greyed the whole overview (look round 1)
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = postShots.Count > 0 ? root.Find("Cam_" + postShots[0]).GetComponent<Camera>().backgroundColor : Color.gray;
            RenderSettings.fogStartDistance = Look.FogStart;
            RenderSettings.fogEndDistance = Look.FogEnd;

            var volume = new GameObject("Look_Volume").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.priority = 10;
            volume.sharedProfile = DemoProfile();

            foreach (var shot in postShots)
                root.Find("Cam_" + shot).GetComponent<UniversalAdditionalCameraData>().renderPostProcessing = true;
            return $"look field: sun {Look.SunIntensity}, fill {Look.FillIntensity}, fog {(Look.Fog ? $"{Look.FogStart}-{Look.FogEnd} m" : "off")}, volume {VolumePath}, post on {postShots.Count} shots";
        }

        /// <summary>Values of the field look (SCENE_STYLE.md "URP look").</summary>
        private static class Look
        {
            public static readonly Color SunColor = new Color(1.0f, 0.87f, 0.70f);
            public const float SunIntensity = 2.0f, ShadowStrength = 0.82f, FillIntensity = 0.5f;
            public static readonly Color AmbientSky = new Color(0.66f, 0.76f, 0.92f);
            public static readonly Color AmbientEquator = new Color(0.78f, 0.70f, 0.58f);
            public static readonly Color AmbientGround = new Color(0.44f, 0.37f, 0.27f);
            public const bool Fog = false;
            public const float FogStart = 45f, FogEnd = 160f;
        }

        /// <summary>Creates or updates the post-processing profile of the demo scenes (idempotent, GUID kept).</summary>
        public static VolumeProfile DemoProfile()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(VolumePath));
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, VolumePath);
            }
            Set<Tonemapping>(profile, t => t.mode.Override(TonemappingMode.Neutral));
            Set<ColorAdjustments>(profile, c =>
            {
                c.postExposure.Override(0.0f);
                c.contrast.Override(22f);
                c.saturation.Override(14f);
            });
            Set<WhiteBalance>(profile, w => { w.temperature.Override(-8f); w.tint.Override(0f); });
            Set<Bloom>(profile, b =>
            {
                b.threshold.Override(1.0f);
                b.intensity.Override(0.25f);
                b.scatter.Override(0.6f);
            });
            Set<Vignette>(profile, v =>
            {
                v.intensity.Override(0.12f);
                v.smoothness.Override(0.45f);
            });
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        private static void Set<T>(VolumeProfile profile, System.Action<T> set) where T : VolumeComponent
        {
            if (!profile.TryGet<T>(out var component))
            {
                component = profile.Add<T>();
                component.name = typeof(T).Name;
                AssetDatabase.AddObjectToAsset(component, profile);
            }
            component.active = true;
            set(component);
            EditorUtility.SetDirty(component);
        }

        private static Material ZoneMaterial(string name, Color color)
        {
            var path = $"{C.DemoDir}/Materials/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", 0f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
