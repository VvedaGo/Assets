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
    /// Demo_Compositions (Э10): the six composition vignettes and the modular sets, each on its own small plinth (the demo
    /// island DEM-01 scaled to the group footprint + margin), one camera rule for all (same bearing, pitch, vFOV; distance fitted
    /// so the group takes the same share of the frame width), a soft light backdrop and the shared pack look
    /// (CottageGardenDecorLook). PackSceneBuilder places the plain module items of
    /// planning/CottageGardenDecor/layouts/Demo_Compositions.txt (no 'comp' lines: the CMP prefabs are NOT re-saved); this
    /// step reads the '#!' lines:
    ///   #! cmp &lt;Shot&gt; &lt;CompName&gt; x z [face [front]] instance of Art/Prefabs/CMP/FMS_Garden_&lt;CompName&gt; at (x, 0, z), one shot;
    ///                                        face = plinth rectangle turned to the camera view (front edge parallel to the frame
    ///                                        bottom; diagonal compositions otherwise leave an empty plinth corner pointing at the camera)
    ///   #! group &lt;Shot&gt; x0 z0 x1 z1 [pitch]       shot of the loose items whose bounds centre lies in the rectangle (Modules)
    ///   #! camera bearing pitch vfov share       bearing of the camera from the target (180 = front), share = plinth width / frame
    ///   #! plinth side back front depthScale     plinth = island scaled to footprint + margins (front = towards the camera); underside scale
    ///   #! backdrop r g b r g b                  backdrop gradient: frame top colour, frame bottom colour (0–255)
    /// </summary>
    public static class CottageGardenDecorCompositionsScene
    {
        private static PackConfig C => CottageGardenDecorPackBuilder.Config;
        public const string LayoutFile = "Demo_Compositions.txt";
        public const string SceneName = "Demo_Compositions";
        private static string Demo => C.DemoDir;
        // lawn top of FMS_Garden_Demo_Island (DEM-01, Fix 1): x -10.29..10.04, z -8.07..8.15
        private static readonly Rect IslandLawn = Rect.MinMaxRect(-10.29f, -8.07f, 10.04f, 8.15f);
        private const int Width = 1920, Height = 1080;

        private sealed class Shot
        {
            public string Name; public Transform Group; public Transform Plinth; public Camera Cam; public string Log; public float Pitch; public string PlinthInfo; public bool Face; public float Front = -1;
        }

        [MenuItem("Tools/Cottage Garden Decor/Build Compositions Scene")]
        public static string Build()
        {
            var log = new System.Text.StringBuilder(PackSceneBuilder.Build(C, LayoutFile, SceneName, false));
            var root = GameObject.Find(C.Tag + "_Demo").transform;
            var lines = File.ReadAllLines($"{C.LayoutDir}/{LayoutFile}").Select(l => l.Trim()).Where(l => l.StartsWith("#!"))
                .Select(l => Split(l.Substring(2))).Where(t => t.Length > 0).ToList();
            float bearing = 150, pitch = 36, fov = 32, share = 0.87f, side = 0.7f, back = 0.7f, front = 1.0f, depth = 0.12f;
            Color top = new Color32(0xF4, 0xF2, 0xEE, 255), bottom = new Color32(0xE4, 0xE5, 0xEA, 255);
            foreach (var t in lines)
            {
                if (t[0] == "camera") { bearing = F(t[1]); pitch = F(t[2]); fov = F(t[3]); share = F(t[4]); }
                if (t[0] == "plinth") { side = F(t[1]); back = F(t[2]); front = F(t[3]); depth = F(t[4]); }
                if (t[0] == "backdrop") { top = C32(t, 1); bottom = C32(t, 4); }
            }

            var backdrop = root.Find("Backdrop_Ground");
            if (backdrop != null) Object.DestroyImmediate(backdrop.gameObject);
            AssetDatabase.DeleteAsset($"{Demo}/Materials/M_Demo_Backdrop_{SceneName}.mat");

            var shots = new List<Shot>();
            var loose = root.Cast<Transform>().Where(t => t.GetComponentInChildren<Renderer>() != null).ToList();
            foreach (var t in lines)
            {
                if (t[0] == "cmp")
                {
                    var path = $"{C.PrefabDir}/CMP/{C.Prefix}{t[2]}.prefab";
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path) ?? throw new FileNotFoundException(path);
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, root);
                    go.transform.SetLocalPositionAndRotation(new Vector3(F(t[3]), 0, F(t[4])), Quaternion.identity);
                    shots.Add(new Shot { Name = t[1], Group = go.transform, Face = t.Length > 5 && t[5] == "face", Front = t.Length > 6 ? F(t[6]) : -1 });
                }
                else if (t[0] == "group")
                {
                    var rect = Rect.MinMaxRect(F(t[2]), F(t[3]), F(t[4]), F(t[5]));
                    var group = new GameObject("Group_" + t[1]).transform;
                    group.SetParent(root, false);
                    foreach (var item in loose)
                    {
                        var c = Bounds(item).center;
                        if (rect.Contains(new Vector2(c.x, c.z))) item.SetParent(group, true);
                    }
                    shots.Add(new Shot { Name = t[1], Group = group, Pitch = t.Length > 6 ? F(t[6]) : 0 });
                }
            }

            // backdrop: gradient sky material in light catalogue tones (frame top -> bottom), cameras clear to it
            var sky = AssetDatabase.LoadAssetAtPath<Material>($"{Demo}/Materials/FMS_Garden_Demo_Backdrop.mat");
            if (sky == null)
            {
                sky = new Material(Shader.Find("CottageGardenDecor/Demo/Gradient Sky"));
                AssetDatabase.CreateAsset(sky, $"{Demo}/Materials/FMS_Garden_Demo_Backdrop.mat");
            }
            sky.SetColor("_ZenithColor", top); sky.SetColor("_HorizonColor", top); sky.SetColor("_BelowColor", bottom);   // frame top (near horizon) -> frame bottom
            sky.SetFloat("_BelowSharpness", 1.0f);
            sky.SetFloat("_Exposure", BackdropExposure);   // lifts the warm input to ~#EFEBE4 after ACES (renders_2)
            EditorUtility.SetDirty(sky);
            RenderSettings.skybox = sky;

            var island = AssetDatabase.LoadAssetAtPath<GameObject>($"{Demo}/Prefabs/FMS_Garden_Demo_Island.prefab");
            foreach (var s in shots)
            {
                var plinth = (GameObject)PrefabUtility.InstantiatePrefab(island, root);
                plinth.name = "Plinth_" + s.Name;
                s.PlinthInfo = PlacePlinth(plinth.transform, Points(s.Group), side, back, s.Front >= 0 ? s.Front : front, depth, s.Face ? (180 - bearing) * Mathf.Deg2Rad : (float?)null);
                foreach (var r in plinth.GetComponentsInChildren<Renderer>())
                    r.sharedMaterials = Enumerable.Repeat(PlinthMaterial(), r.sharedMaterials.Length).ToArray();
                s.Plinth = plinth.transform;

                var cam = new GameObject("Cam_" + s.Name).AddComponent<Camera>();
                cam.transform.SetParent(root, false);
                cam.fieldOfView = fov; cam.nearClipPlane = 0.3f; cam.farClipPlane = 200;
                cam.clearFlags = CameraClearFlags.Skybox;
                cam.aspect = Width / (float)Height;
                cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
                s.Cam = cam;
                s.Log = Fit(s, bearing, s.Pitch > 0 ? s.Pitch : pitch, share);
            }

            CottageGardenDecorLook.ApplyLights(root);
            CottageGardenDecorLook.Haze(Color.white, 0);
            CottageGardenDecorLook.AddVolume(root, shots.Select(s => s.Cam).ToArray());
            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
            EditorSceneManager.SaveScene(root.gameObject.scene);

            var outDir = Path.Combine(Path.GetTempPath(), C.RenderTempDir);
            Directory.CreateDirectory(outDir);
            foreach (var s in shots)
            {
                var file = Path.Combine(outDir, $"{SceneName}_{s.Name}.png");
                CottageGardenDecorLook.Render(s.Cam, file, Width, Height);
                log.AppendLine($"render {file}: {s.PlinthInfo}; {s.Log}");
            }
            Debug.Log("[CottageGardenDecor] compositions:\n" + log);
            return log + CottageGardenDecorSceneFinalize.Finalize(SceneName);
        }

        /// <summary>Camera at the given bearing/pitch looking at the group (renders_2 vignette rules): distance so the plinth takes
        /// <paramref name="share"/> of the frame width, limited by group + plinth ≤ 84 % of the height (tallest point ≥ 6 % from the
        /// top); then plinth centred horizontally and its lowest pixel put at 90 % of the height.</summary>
        private static string Fit(Shot s, float bearing, float pitch, float share)
        {
            var groupPts = Points(s.Group);
            var plinthPts = Points(s.Plinth);
            var allPts = groupPts.Concat(plinthPts).ToList();
            var gb = Bounds(s.Group);
            var target = new Vector3(gb.center.x, gb.size.y * 0.3f, gb.center.z);
            var rad = Mathf.Deg2Rad;
            var backDir = new Vector3(Mathf.Sin(bearing * rad) * Mathf.Cos(pitch * rad), Mathf.Sin(pitch * rad), Mathf.Cos(bearing * rad) * Mathf.Cos(pitch * rad));
            Rect g, a, p;
            for (var pass = 0; pass < 5; pass++)
            {
                float lo = 2, hi = 120;
                for (var i = 0; i < 30; i++)
                {
                    var d = (lo + hi) / 2;
                    Place(s.Cam, target, backDir, d);
                    a = Viewport(s.Cam, allPts); p = Viewport(s.Cam, plinthPts);
                    var k = Mathf.Max(p.width / share, a.width / 0.97f, a.height / 0.87f);   // tallest point at 5 %, plinth bottom at 92 %
                    if (k > 1) lo = d; else hi = d;
                }
                Place(s.Cam, target, backDir, hi);
                a = Viewport(s.Cam, allPts); p = Viewport(s.Cam, plinthPts);
                var dist = (s.Cam.transform.position - target).magnitude;
                var h = 2 * dist * Mathf.Tan(s.Cam.fieldOfView * 0.5f * rad);
                var w = h * s.Cam.aspect;
                target += s.Cam.transform.right * ((p.center.x - 0.5f) * w) + s.Cam.transform.up * ((a.yMin - 0.08f) * h);
            }
            g = Viewport(s.Cam, groupPts); a = Viewport(s.Cam, allPts); p = Viewport(s.Cam, plinthPts);
            return $"group w {g.width:P1} (x {g.xMin:P0}-{g.xMax:P0}), group rows {1 - g.yMax:P1}-{1 - g.yMin:P1}, top {1 - a.yMax:P1}; plinth w {p.width:P1}, bottom {1 - a.yMin:P1}, front band {g.yMin - a.yMin:P1}; " +
                   $"cam {s.Cam.transform.position.ToString("F2")} bearing {bearing} pitch {pitch} vfov {s.Cam.fieldOfView} dist {(s.Cam.transform.position - target).magnitude:F1}";
        }

        /// <summary>Plinth = the demo island scaled to the minimum-area rectangle around the group footprint (convex hull of the
        /// mesh vertices, rotating calipers; kept axis-aligned unless the turned one is ≥ 8 % smaller) + margins: sides and back
        /// <paramref name="side"/>/<paramref name="back"/>, the camera-facing side (−z) <paramref name="front"/> (renders_2 pass 2:
        /// diagonal compositions such as CMP-03 left an empty front corner inside an axis-aligned plinth).</summary>
        private static string PlacePlinth(Transform plinth, List<Vector3> pts, float side, float back, float front, float depth, float? fixedT = null)
        {
            var hull = Hull(pts.Select(p => new Vector2(p.x, p.z)).ToList());
            float bestA = float.MaxValue, bestT = 0, axisA = 0;
            Rect bestR = default, axisR = default;
            for (var i = 0; i < hull.Count; i++)
            {
                var e = hull[(i + 1) % hull.Count] - hull[i];
                var t = Mathf.Atan2(e.y, e.x);
                t = Mathf.Repeat(t + Mathf.PI / 4, Mathf.PI / 2) - Mathf.PI / 4;   // fold into (−45°, 45°]: v stays the front-back axis
                var r = RotRect(hull, t);
                if (r.width * r.height < bestA) { bestA = r.width * r.height; bestT = t; bestR = r; }
            }
            axisR = RotRect(hull, 0); axisA = axisR.width * axisR.height;
            if (bestA > axisA * 0.92f) { bestT = 0; bestR = axisR; }
            if (fixedT.HasValue) { bestT = fixedT.Value; bestR = RotRect(hull, bestT); }   // plinth turned to face the camera
            // margins in the turned frame: u = sides, v0 = front (towards the camera), v1 = back
            var r2 = Rect.MinMaxRect(bestR.xMin - side, bestR.yMin - front, bestR.xMax + side, bestR.yMax + back);
            var sx = r2.width / IslandLawn.width;
            var sz = r2.height / IslandLawn.height;
            var c = Unrot(r2.center, bestT);
            var yaw = -bestT * Mathf.Rad2Deg;
            var q = Quaternion.Euler(0, yaw, 0);
            plinth.localScale = new Vector3(sx, depth, sz);
            plinth.rotation = q;
            plinth.position = new Vector3(c.x, 0, c.y) - q * new Vector3(IslandLawn.center.x * sx, 0, IslandLawn.center.y * sz);
            return $"plinth {r2.width:F2} x {r2.height:F2} m (footprint {bestR.width:F2} x {bestR.height:F2}, yaw {yaw:F0}°, axis-aligned {axisR.width:F2} x {axisR.height:F2})";
        }

        private static Rect RotRect(List<Vector2> pts, float t)
        {
            float c = Mathf.Cos(t), s = Mathf.Sin(t), x0 = float.MaxValue, x1 = float.MinValue, y0 = float.MaxValue, y1 = float.MinValue;
            foreach (var p in pts)
            {
                var u = p.x * c + p.y * s; var v = -p.x * s + p.y * c;
                x0 = Mathf.Min(x0, u); x1 = Mathf.Max(x1, u); y0 = Mathf.Min(y0, v); y1 = Mathf.Max(y1, v);
            }
            return Rect.MinMaxRect(x0, y0, x1, y1);
        }

        private static Vector2 Unrot(Vector2 uv, float t) =>
            new Vector2(uv.x * Mathf.Cos(t) - uv.y * Mathf.Sin(t), uv.x * Mathf.Sin(t) + uv.y * Mathf.Cos(t));

        private static List<Vector2> Hull(List<Vector2> p)
        {
            p = p.Distinct().OrderBy(a => a.x).ThenBy(a => a.y).ToList();
            if (p.Count < 3) return p;
            var h = new List<Vector2>();
            float Cross(Vector2 o, Vector2 a, Vector2 b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
            foreach (var pt in p) { while (h.Count >= 2 && Cross(h[h.Count - 2], h[h.Count - 1], pt) <= 0) h.RemoveAt(h.Count - 1); h.Add(pt); }
            var lower = h.Count + 1;
            for (var i = p.Count - 2; i >= 0; i--) { var pt = p[i]; while (h.Count >= lower && Cross(h[h.Count - 2], h[h.Count - 1], pt) <= 0) h.RemoveAt(h.Count - 1); h.Add(pt); }
            h.RemoveAt(h.Count - 1);
            return h;
        }

        private static void Place(Camera cam, Vector3 target, Vector3 back, float d)
        {
            cam.transform.position = target + back * d;
            cam.transform.rotation = Quaternion.LookRotation(target - cam.transform.position);
        }

        private static Rect Viewport(Camera cam, List<Vector3> pts)
        {
            float x0 = 9, x1 = -9, y0 = 9, y1 = -9;
            foreach (var p in pts)
            {
                var v = cam.WorldToViewportPoint(p);
                x0 = Mathf.Min(x0, v.x); x1 = Mathf.Max(x1, v.x); y0 = Mathf.Min(y0, v.y); y1 = Mathf.Max(y1, v.y);
            }
            return Rect.MinMaxRect(x0, y0, x1, y1);
        }

        private static List<Vector3> Points(Transform t)
        {
            var pts = new List<Vector3>();
            foreach (var mf in t.GetComponentsInChildren<MeshFilter>())
            {
                var r = mf.GetComponent<Renderer>();
                if (mf.sharedMesh == null || r == null || !r.enabled || mf.name.EndsWith("_LOD1") || mf.name.EndsWith("_Low1")) continue;
                var m = mf.transform.localToWorldMatrix;
                var v = mf.sharedMesh.vertices;
                for (var i = 0; i < v.Length; i += 2) pts.Add(m.MultiplyPoint3x4(v[i]));
            }
            return pts;
        }

        private static Bounds Bounds(Transform t)
        {
            var rs = t.GetComponentsInChildren<Renderer>();
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }

        /// <summary>Plinth = demo atlas material slightly dimmed (vignettes only): the lawn of a close plinth fills ~40 % of the
        /// frame and must stay calmer than the pack items.</summary>
        private static Material PlinthMaterial()
        {
            var path = $"{Demo}/Materials/FMS_Garden_Demo_Plinth.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(AssetDatabase.LoadAssetAtPath<Material>($"{Demo}/Materials/FMS_Garden_Demo_Atlas.mat"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", PlinthTint);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        public static Color PlinthTint = new Color(0.90f, 0.94f, 0.90f);   // renders_2: plinth lawn lit ~#86C24A
        public static float BackdropExposure = 1.42f;   // HDR render: renders ~#EFEBE4

        private static Color C32(string[] t, int i) => new Color32((byte)int.Parse(t[i]), (byte)int.Parse(t[i + 1]), (byte)int.Parse(t[i + 2]), 255);
        private static string[] Split(string s) => s.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
