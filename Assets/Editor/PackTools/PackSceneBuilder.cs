using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace PackTools.Editor
{
    /// <summary>
    /// Shared demo-scene builder (origin: Farm Processing, 2026-11-20). Reads a text layout, builds a scene of pack prefabs,
    /// saves composition roots as prefabs and renders every shot to %TEMP%/&lt;RenderTempDir&gt;. Layout space = world:
    /// x right of the camera, z away from it, y up, metres; the camera sits at -z; rot 0 = the model faces the camera.
    /// Directives (one per line, '#' comments):
    ///   &lt;ID&gt; x z [rot] [y]                 one prefab; y defaults to 0.15 = top of a floor tile (pass y when there is no floor!)
    ///   row &lt;ID&gt; x0 z0 x1 z1 n [rot] [y]   n copies on a line
    ///   floor &lt;code&gt; x0 z0 x1 z1          2x2 m tiles (PackConfig.FloorTiles), tile centres stepped by 2
    ///   scaled &lt;ID&gt; x z sx sz             one prefab scaled in x/z (e.g. a 3x3 m plot from one 2x2 tile)
    ///   comp &lt;Name&gt; ox oz                  following lines go into a composition root, saved as Art/Prefabs/CMP/&lt;Prefix&gt;&lt;Name&gt;
    ///   shot &lt;name&gt; px py pz lx ly lz fov [w h]   camera relative to the current comp origin
    ///   bg r g b / ground r g b            background of the following shots / colour of the backdrop floor plane
    /// </summary>
    public static class PackSceneBuilder
    {
        private static PackConfig C;
        private static string PrefabDir => C.PrefabDir;
        private static string DemoDir => C.DemoDir;
        private static string LayoutDir => C.LayoutDir;
        private static string RootName => C.Tag + "_Demo";
        private static Color Backdrop => C.Backdrop;

        private sealed class Shot
        {
            public string Name; public Vector3 Pos; public Vector3 Look; public float Fov; public Color Bg; public int W = 1920; public int H = 1080;
        }

        /// <summary>Builds the scene from a layout file, saves it, renders every 'shot' line to %TEMP%/RenderTempDir.</summary>
        public static string Build(PackConfig config, string layoutFile, string sceneName, bool savePrefabs = true)
        {
            C = config;
            Directory.CreateDirectory($"{DemoDir}/Scenes");
            Directory.CreateDirectory($"{DemoDir}/Materials");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var root = new GameObject(RootName).transform;        // layout space = world space (camera at -z looking +z)
            var parent = root; var origin = Vector3.zero; var bg = Backdrop; var groundColor = Backdrop;
            var comps = new List<Transform>();
            var shots = new List<Shot>();
            var log = new System.Text.StringBuilder();
            var count = 0;

            foreach (var raw in File.ReadAllLines($"{LayoutDir}/{layoutFile}"))
            {
                var line = raw.Split('#')[0].Trim();
                if (line.Length == 0) continue;
                var t = line.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
                switch (t[0])
                {
                    case "shot":    // relative to the current comp origin
                        shots.Add(new Shot { Name = t[1], Pos = origin + V(t, 2), Look = origin + V(t, 5), Fov = F(t[8]), Bg = bg,
                                             W = t.Length > 10 ? int.Parse(t[9]) : 1920, H = t.Length > 10 ? int.Parse(t[10]) : 1080 });
                        break;
                    case "ground":  // ground r g b (0-255): colour of the backdrop floor plane
                        groundColor = new Color32((byte)int.Parse(t[1]), (byte)int.Parse(t[2]), (byte)int.Parse(t[3]), 255);
                        break;
                    case "bg":      // bg r g b (0-255): background of the following shots
                        bg = new Color32((byte)int.Parse(t[1]), (byte)int.Parse(t[2]), (byte)int.Parse(t[3]), 255);
                        break;
                    case "comp":    // comp <Name> ox oz : following lines go into a composition root (saved as a prefab)
                        origin = new Vector3(F(t[2]), 0, F(t[3]));
                        parent = new GameObject(t[1]).transform;
                        parent.SetParent(root, false);
                        parent.localPosition = origin;
                        comps.Add(parent);
                        break;
                    case "floor":   // floor <code> x0 z0 x1 z1 : fill a rectangle of 2x2 tiles (tile centres)
                        var id = C.FloorTiles[t[1]];
                        for (var x = F(t[2]); x <= F(t[4]) + 0.01f; x += 2)
                            for (var z = F(t[3]); z <= F(t[5]) + 0.01f; z += 2) { Place(parent, id, x, 0, z, 0, log); count++; }
                        break;
                    case "scaled":  // scaled <ID> x z sx sz : one prefab scaled in x/z (e.g. a 3x3 m floor from one 2x2 tile)
                        Place(parent, t[1], F(t[2]), 0, F(t[3]), 0, log);
                        if (parent.childCount > 0) parent.GetChild(parent.childCount - 1).localScale = new Vector3(F(t[4]), 1, F(t[5]));
                        count++;
                        break;
                    case "row":     // row <ID> x0 z0 x1 z1 n [rot] [y]
                        var n = int.Parse(t[6]);
                        for (var i = 0; i < n; i++)
                        {
                            var k = n == 1 ? 0 : i / (float)(n - 1);
                            Place(parent, t[1], Mathf.Lerp(F(t[2]), F(t[4]), k), Opt(t, 8, 0.15f), Mathf.Lerp(F(t[3]), F(t[5]), k), Opt(t, 7, 0), log);
                            count++;
                        }
                        break;
                    default:        // <ID> x z [rot] [y]
                        Place(parent, t[0], F(t[1]), Opt(t, 4, 0.15f), F(t[2]), Opt(t, 3, 0), log);
                        count++;
                        break;
                }
            }

            BuildBackdrop(root, groundColor, sceneName);
            BuildLights(root);
            var cams = new List<Camera>();
            foreach (var s in shots) cams.Add(BuildCamera(root, s));

            if (comps.Count > 0 && savePrefabs)
            {
                Directory.CreateDirectory($"{PrefabDir}/CMP");
                foreach (var c in comps)
                {
                    c.SetParent(null, true);                            // prefab root: identity rotation/scale, origin = front centre
                    PrefabUtility.SaveAsPrefabAssetAndConnect(c.gameObject, $"{PrefabDir}/CMP/{C.Prefix}{c.name}.prefab", InteractionMode.AutomatedAction);
                    c.SetParent(root, true);
                }
                log.AppendLine($"{comps.Count} composition prefabs -> {PrefabDir}/CMP");
            }
            EditorSceneManager.SaveScene(scene, $"{DemoDir}/Scenes/{sceneName}.unity");
            var outDir = Path.Combine(Path.GetTempPath(), C.RenderTempDir);
            Directory.CreateDirectory(outDir);
            for (var i = 0; i < shots.Count; i++) Render(cams[i], Path.Combine(outDir, $"{sceneName}_{shots[i].Name}.png"), shots[i].W, shots[i].H, 2);

            log.Insert(0, $"[{C.Tag}] {sceneName}: {count} objects, {shots.Count} shots -> {outDir}\n");
            Debug.Log(log.ToString());
            return log.ToString();
        }

        private static void Place(Transform root, string id, float x, float y, float z, float rot, System.Text.StringBuilder log)
        {
            var path = C.PrefabPath(id);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) { log.AppendLine("! missing prefab " + path); return; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, root);
            go.transform.localPosition = new Vector3(x, y, z);
            go.transform.localRotation = Quaternion.Euler(0, rot + 180, 0);   // rot 0 faces the camera
        }

        private static void BuildBackdrop(Transform root, Color color, string sceneName)
        {
            var mat = LoadOrCreateMaterial("M_Demo_Backdrop_" + sceneName, color, 0.0f);
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Backdrop_Ground";
            ground.transform.SetParent(root, false);
            ground.transform.localPosition = new Vector3(0, -0.002f, 5);
            ground.transform.localScale = new Vector3(40, 1, 40);
            ground.GetComponent<Renderer>().sharedMaterial = mat;
            Object.DestroyImmediate(ground.GetComponent<Collider>());
        }

        private static void BuildLights(Transform root)
        {
            // warm golden key from the upper left (layout space), cool fill from the right
            var key = new GameObject("Key_Sun").AddComponent<Light>();
            key.type = LightType.Directional;
            key.transform.SetParent(root, false);
            key.transform.localRotation = Quaternion.LookRotation(new Vector3(0.75f, -1.1f, 0.55f));
            key.color = new Color(1.0f, 0.84f, 0.62f);
            key.intensity = 2.6f;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = 0.85f;

            var fill = new GameObject("Fill_Sky").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.transform.SetParent(root, false);
            fill.transform.localRotation = Quaternion.LookRotation(new Vector3(-0.9f, -0.6f, 0.4f));
            fill.color = new Color(0.55f, 0.80f, 0.98f);
            fill.intensity = 0.7f;
            fill.shadows = LightShadows.None;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.45f, 0.58f, 0.66f);
            RenderSettings.ambientEquatorColor = new Color(0.44f, 0.40f, 0.36f);
            RenderSettings.ambientGroundColor = new Color(0.30f, 0.30f, 0.30f);
            RenderSettings.fog = false;
        }

        private static Camera BuildCamera(Transform root, Shot s)
        {
            var go = new GameObject("Cam_" + s.Name);
            go.transform.SetParent(root, false);
            go.transform.localPosition = s.Pos;
            go.transform.localRotation = Quaternion.LookRotation(s.Look - s.Pos);
            var cam = go.AddComponent<Camera>();
            cam.fieldOfView = s.Fov;
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 200;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = s.Bg;
            var data = go.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = false;
            data.antialiasing = AntialiasingMode.None;
            return cam;
        }

        public static void Render(Camera cam, string path, int width, int height, int supersample)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var oldRes = urp.mainLightShadowmapResolution; var oldDist = urp.shadowDistance;
            urp.mainLightShadowmapResolution = 4096; urp.shadowDistance = 60;
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

        private static Material LoadOrCreateMaterial(string name, Color color, float smooth)
        {
            var path = $"{DemoDir}/Materials/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", smooth);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
        private static float Opt(string[] t, int i, float d) => t.Length > i ? F(t[i]) : d;
        private static Vector3 V(string[] t, int i) => new Vector3(F(t[i]), F(t[i + 1]), F(t[i + 2]));
    }
}
