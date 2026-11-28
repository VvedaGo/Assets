using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using PackTools.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace CottageGardenDecor.Editor
{
    /// <summary>
    /// Catalogue scene and catalogue media (Э10): PackSceneBuilder places the items of a layout (no 'comp' lines, CMP prefabs
    /// are never re-saved), then this step reads the '#!' lines:
    ///   #! labels                               ID labels (TextMesh, flat on the floor in front of every item) — scene only,
    ///                                           hidden while rendering (renders stay text-free)
    ///   #! floor x0 z0 x1 z1                    light neutral floor plane (catalogue background, receives shadows)
    ///   #! cmp &lt;CompName&gt; x z                  composition prefab instance (one item)
    ///   #! lod x z level                        force a LOD level on the item nearest to (x, z) (09_Technical)
    ///   #! wire x0 z0 x1 z1                     wireframe overlay (edge line meshes, unlit) on the items in the rectangle
    ///   #! island x0 z0 x1 z1 side back front d demo island scaled to the items in the rectangle + margins (sky shots)
    ///   #! shot Name File W H x0 z0 x1 z1 bearing pitch vfov shareW top bottom floor|sky [supersample]
    ///                                           camera fitted to the items in the rectangle: width share, rows top..bottom
    ///   #! cloud &lt;Shot&gt; &lt;A..E&gt; u v dist scale rotY  cloud on the camera ray (sky shots)
    /// Every shot writes &lt;File&gt;.png and &lt;File&gt;_labels.json (item ID / prefab → pixel rect, category rects) for Э12.
    /// All LOD groups are forced to LOD0 for the shots (catalogue scale would otherwise pick LOD1), except '#! lod'.
    /// </summary>
    public static class CottageGardenDecorCatalogScene
    {
        private static PackConfig C => CottageGardenDecorPackBuilder.Config;
        private static string Demo => C.DemoDir;
        public const string RawDir = "AssetStore/CottageGardenDecor/Media/raw";
        /// <summary>Materials used only by the media renders: outside the pack root so they do not ship.</summary>
        public const string MediaOnly = "Assets/Editor/CottageGardenDecor/MediaOnly";
        private static readonly Rect IslandLawn = Rect.MinMaxRect(-10.29f, -8.07f, 10.04f, 8.15f);
        public static Color FloorColor = new Color(0.84f, 0.85f, 0.90f);
        public static Color FloorBackground = new Color(0.80f, 0.80f, 0.83f);

        private sealed class Item { public GameObject Go; public string Id; public string Prefab; public Bounds B; }
        private sealed class Shot
        {
            public string Name, File; public int W, H, Ss = 2; public Rect Area; public float Bearing, Pitch, Fov, Share, Top, Bottom;
            public bool Sky; public float Left = 0, Right = 1; public string SkyMat; public Camera Cam; public List<Item> Items; public Transform Clouds; public Transform Plinth; public string Log;
        }

        [MenuItem("Tools/Cottage Garden Decor/Build Catalog Scene")]
        public static string BuildCatalog() => Build("Demo_Catalog.txt", "Demo_Catalog", true, Path.Combine(Path.GetTempPath(), C.RenderTempDir))
            + CottageGardenDecorSceneFinalize.Finalize("Demo_Catalog");

        [MenuItem("Tools/Cottage Garden Decor/Render Catalog Shots")]
        public static string BuildShots() => Build("Catalog_Shots.txt", "Catalog_Shots", false, RawDir);

        public static string Build(string layoutFile, string sceneName, bool keepScene, string outDir, string only = null)
        {
            var log = new StringBuilder(PackSceneBuilder.Build(C, layoutFile, sceneName, false));
            var root = GameObject.Find(C.Tag + "_Demo").transform;
            var backdrop = root.Find("Backdrop_Ground");
            if (backdrop != null) Object.DestroyImmediate(backdrop.gameObject);
            AssetDatabase.DeleteAsset($"{Demo}/Materials/M_Demo_Backdrop_{sceneName}.mat");
            var lines = File.ReadAllLines($"{C.LayoutDir}/{layoutFile}").Select(l => l.Split('#')[0].Length == 0 && l.TrimStart().StartsWith("#!") ? l.Trim().Substring(2) : null)
                .Where(l => l != null).Select(Split).Where(t => t.Length > 0 && !t[0].StartsWith("<")).ToList();

            var reverse = C.PrefabNames.ToDictionary(kv => C.Prefix + kv.Value, kv => kv.Key);
            var items = new List<Item>();
            foreach (Transform t in root)
                if (t.GetComponentInChildren<Renderer>() != null && PrefabUtility.IsAnyPrefabInstanceRoot(t.gameObject)) items.Add(MakeItem(t.gameObject, reverse));
            foreach (var t in lines.Where(t => t[0] == "cmp"))
            {
                var path = $"{C.PrefabDir}/CMP/{C.Prefix}{t[1]}.prefab";
                var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path) ?? throw new FileNotFoundException(path), root);
                go.transform.position = new Vector3(F(t[2]), 0, F(t[3]));
                items.Add(MakeItem(go, reverse));
            }
            LastForced.Clear();
            foreach (var lg in root.GetComponentsInChildren<LODGroup>(true)) lg.ForceLOD(0);   // catalogue = LOD0

            foreach (var t in lines)
            {
                switch (t[0])
                {
                    case "floor": Floor(root, Rect.MinMaxRect(F(t[1]), F(t[2]), F(t[3]), F(t[4]))); break;
                    case "lod":
                        var p = new Vector3(F(t[1]), 0, F(t[2]));
                        var near = items.OrderBy(i => (new Vector3(i.B.center.x, 0, i.B.center.z) - p).sqrMagnitude).First();
                        var lodGroup = near.Go.GetComponent<LODGroup>();
                        if (lodGroup != null) { lodGroup.ForceLOD(int.Parse(t[3])); LastForced[lodGroup] = int.Parse(t[3]); near.Id += $" (LOD{t[3]})"; }
                        break;
                    case "wire":
                        var area = Rect.MinMaxRect(F(t[1]), F(t[2]), F(t[3]), F(t[4]));
                        var wired = 0;
                        foreach (var i in items.Where(i => area.Contains(new Vector2(i.B.center.x, i.B.center.z)))) wired += Wire(i.Go);
                        log.AppendLine($"wire: {wired} line meshes");
                        break;
                }
            }

            var labels = lines.Any(t => t[0] == "labels") ? Labels(root, items) : null;
            var shots = new List<Shot>();
            foreach (var t in lines.Where(t => t[0] == "shot"))
            {
                var s = new Shot
                {
                    Name = t[1], File = t[2], W = int.Parse(t[3]), H = int.Parse(t[4]), Area = Rect.MinMaxRect(F(t[5]), F(t[6]), F(t[7]), F(t[8])),
                    Bearing = F(t[9]), Pitch = F(t[10]), Fov = F(t[11]), Share = F(t[12]), Top = F(t[13]), Bottom = F(t[14]), Sky = t[15] == "sky",
                    Ss = t.Length > 16 ? int.Parse(t[16]) : 2,
                };
                s.Items = items.Where(i => s.Area.Contains(new Vector2(i.B.center.x, i.B.center.z))).ToList();
                if (!s.Sky) Floor(root, Rect.MinMaxRect(s.Area.xMin - 45, s.Area.yMin - 45, s.Area.xMax + 45, s.Area.yMax + 45));
                shots.Add(s);
            }
            foreach (var t in lines.Where(t => t[0] == "frame")) { var s = shots.First(x => x.Name == t[1]); s.Left = F(t[2]); s.Right = F(t[3]); }
            foreach (var t in lines.Where(t => t[0] == "lightsky")) shots.First(x => x.Name == t[1]).SkyMat = "light";
            foreach (var t in lines.Where(t => t[0] == "island"))
            {
                var area = Rect.MinMaxRect(F(t[1]), F(t[2]), F(t[3]), F(t[4]));
                var shot = shots.First(s => s.Sky && s.Area.Overlaps(area));
                shot.Plinth = Island(root, shot.Items, F(t[5]), F(t[6]), F(t[7]), F(t[8]));
            }

            var sky = AssetDatabase.LoadAssetAtPath<Material>($"{Demo}/Materials/FMS_Garden_Demo_Sky.mat");
            if (sky != null) RenderSettings.skybox = sky;
            CottageGardenDecorLook.ApplyLights(root);
            CottageGardenDecorLook.Haze(Color.white, 0);
            foreach (var s in shots)
            {
                var cam = new GameObject("Cam_" + s.Name).AddComponent<Camera>();
                cam.transform.SetParent(root, false);
                cam.fieldOfView = s.Fov; cam.nearClipPlane = 0.3f; cam.farClipPlane = 400; cam.aspect = s.W / (float)s.H;
                cam.clearFlags = s.Sky ? CameraClearFlags.Skybox : CameraClearFlags.SolidColor;
                cam.backgroundColor = FloorBackground;
                cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
                s.Cam = cam;
                s.Log = Fit(s);
                s.Clouds = new GameObject("Clouds_" + s.Name).transform;
                s.Clouds.SetParent(root, false);
            }
            foreach (var t in lines.Where(t => t[0] == "cloud"))
            {
                var s = shots.First(x => x.Name == t[1]);
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{Demo}/Prefabs/FMS_Garden_Demo_Cloud_{t[2]}.prefab");
                var cloud = (GameObject)PrefabUtility.InstantiatePrefab(prefab, s.Clouds);
                var ray = s.Cam.ViewportPointToRay(new Vector3(F(t[3]), F(t[4]), 0));
                cloud.transform.position = ray.origin + ray.direction * F(t[5]);
                cloud.transform.rotation = Quaternion.Euler(0, s.Cam.transform.eulerAngles.y + F(t[7]), 0);
                cloud.transform.localScale = Vector3.one * F(t[6]);
            }
            CottageGardenDecorLook.AddVolume(root, shots.Select(s => s.Cam).ToArray());

            if (keepScene)
            {
                EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
                EditorSceneManager.SaveScene(root.gameObject.scene);
            }
            Directory.CreateDirectory(outDir);
            if (labels != null) labels.gameObject.SetActive(false);
            foreach (var s in shots)
            {
                if (only != null && s.Name != only) continue;
                if (s.Sky) RenderSettings.skybox = s.SkyMat == "light" ? LightSky() : sky;
                foreach (var o in shots) o.Clouds.gameObject.SetActive(o == s);
                var png = Path.Combine(outDir, s.File + ".png");
                CottageGardenDecorLook.Render(s.Cam, png, s.W, s.H, s.Ss);
                File.WriteAllText(Path.Combine(outDir, s.File + "_labels.json"), LabelMap(s));
                log.AppendLine($"render {png}: {s.Items.Count} items; {s.Log}");
            }
            if (labels != null) labels.gameObject.SetActive(true);
            foreach (var o in shots) o.Clouds.gameObject.SetActive(true);
            if (keepScene)
            {
                EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
                EditorSceneManager.SaveScene(root.gameObject.scene);
            }
            else
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                AssetDatabase.DeleteAsset($"{Demo}/Scenes/{sceneName}.unity");
            }
            Debug.Log("[CottageGardenDecor] catalogue:\n" + log);
            return log.ToString();
        }

        private static Item MakeItem(GameObject go, Dictionary<string, string> reverse)
        {
            var src = PrefabUtility.GetCorrespondingObjectFromSource(go);
            var prefab = src != null ? src.name : go.name;
            string id;
            if (!reverse.TryGetValue(prefab, out id))
            {
                var comps = new[] { "RoseArchEntrance", "PergolaTerrace", "GazeboRetreat", "FountainParterre", "WalledPondCorner", "WildlifeLawn" };
                var ci = System.Array.FindIndex(comps, c => prefab.EndsWith(c));
                id = ci >= 0 ? $"CMP-0{ci + 1}" : prefab;
            }
            return new Item { Go = go, Id = id, Prefab = prefab, B = Bounds(go.transform) };
        }

        private static void Floor(Transform root, Rect r)
        {
            var path = $"{Demo}/Materials/FMS_Garden_Demo_CatalogFloor.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", FloorColor);
            mat.SetFloat("_Smoothness", 0f);
            EditorUtility.SetDirty(mat);
            var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
            floor.name = "Catalog_Floor";
            floor.transform.SetParent(root, false);
            floor.transform.position = new Vector3(r.center.x, -0.003f, r.center.y);
            floor.transform.localScale = new Vector3(r.width / 10f, 1, r.height / 10f);
            floor.GetComponent<Renderer>().sharedMaterial = mat;
            Object.DestroyImmediate(floor.GetComponent<Collider>());
        }

        private static Transform Labels(Transform root, List<Item> items)
        {
            var parent = new GameObject("ID_Labels").transform;
            parent.SetParent(root, false);
            var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            foreach (var i in items)
            {
                var go = new GameObject("Label_" + i.Id);
                go.transform.SetParent(parent, false);
                go.transform.position = new Vector3(i.B.center.x, 0.01f, i.B.min.z - 0.25f);
                go.transform.rotation = Quaternion.Euler(90, 0, 0);
                var tm = go.AddComponent<TextMesh>();
                tm.text = i.Id; tm.font = font; tm.fontSize = 64; tm.characterSize = 0.035f;
                tm.anchor = TextAnchor.UpperCenter; tm.alignment = TextAlignment.Center; tm.color = new Color(0.13f, 0.15f, 0.18f);
                go.GetComponent<MeshRenderer>().sharedMaterial = font.material;
            }
            return parent;
        }

        /// <summary>Shaded wireframe: per mesh an edge-line mesh (deduplicated edges of the rendered LOD), unlit dark lines pushed
        /// 4 mm along the vertex normals so they sit on the shaded surface.</summary>
        private static int Wire(GameObject go)
        {
            Directory.CreateDirectory(MediaOnly);
            var path = MediaOnly + "/FMS_Garden_Demo_Wire.mat";   // media-only, never shipped
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Unlit")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_BaseColor", new Color(0.10f, 0.12f, 0.16f));
            EditorUtility.SetDirty(mat);
            var lg = go.GetComponentInChildren<LODGroup>();
            IEnumerable<Renderer> renderers = go.GetComponentsInChildren<MeshRenderer>();
            if (lg != null)
            {
                var lods = lg.GetLODs();
                var level = LastForced.TryGetValue(lg, out var l) ? l : 0;
                renderers = lods[Mathf.Min(level, lods.Length - 1)].renderers;
            }
            var count = 0;
            foreach (var r in renderers.Where(r => r != null).ToList())
            {
                var mf = r.GetComponent<MeshFilter>();
                if (mf == null || mf.sharedMesh == null) continue;
                var m = mf.sharedMesh; var v = m.vertices; var n = m.normals; var tri = m.triangles;
                var key = new Dictionary<Vector3Int, int>(); var verts = new List<Vector3>(); var edges = new HashSet<long>(); var idx = new List<int>();
                int Id(int k)
                {
                    var p = v[k]; var q = new Vector3Int(Mathf.RoundToInt(p.x * 2000), Mathf.RoundToInt(p.y * 2000), Mathf.RoundToInt(p.z * 2000));
                    if (!key.TryGetValue(q, out var id)) { id = verts.Count; key[q] = id; verts.Add(p + (n.Length > k ? n[k] * 0.004f : Vector3.zero)); }
                    return id;
                }
                for (var i = 0; i < tri.Length; i += 3)
                    for (var e = 0; e < 3; e++)
                    {
                        int a = Id(tri[i + e]), b = Id(tri[i + (e + 1) % 3]);
                        var lo = Mathf.Min(a, b); var hi = Mathf.Max(a, b);
                        if (edges.Add(((long)lo << 32) | (uint)hi)) { idx.Add(lo); idx.Add(hi); }
                    }
                var lines = new Mesh { indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
                lines.SetVertices(verts); lines.SetIndices(idx, MeshTopology.Lines, 0); lines.RecalculateBounds();
                var w = new GameObject("Wire");
                w.transform.SetParent(r.transform, false);
                w.AddComponent<MeshFilter>().sharedMesh = lines;
                var wr = w.AddComponent<MeshRenderer>();
                wr.sharedMaterial = mat; wr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; wr.receiveShadows = false;
                count++;
            }
            return count;
        }

        private static readonly Dictionary<LODGroup, int> LastForced = new Dictionary<LODGroup, int>();

        /// <summary>Calmer, lighter variant of the demo sky for the Card / Icon sources (plate text and the small icon need a quiet
        /// background; the Hero sky of Look v2 stays unchanged).</summary>
        private static Material LightSky()
        {
            Directory.CreateDirectory(MediaOnly);
            var path = MediaOnly + "/FMS_Garden_Demo_Sky_Light.mat";   // media-only (Card / Icon sources)
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("CottageGardenDecor/Demo/Gradient Sky")); AssetDatabase.CreateAsset(mat, path); }
            mat.SetColor("_ZenithColor", LightSkyTop); mat.SetColor("_HorizonColor", LightSkyTop); mat.SetColor("_BelowColor", LightSkyBottom);
            mat.SetFloat("_BelowSharpness", 1.2f); mat.SetFloat("_Exposure", 1f);
            EditorUtility.SetDirty(mat);
            return mat;
        }
        public static Color LightSkyTop = new Color(0.50f, 0.72f, 0.95f), LightSkyBottom = new Color(0.78f, 0.88f, 0.98f);

        private static Transform Island(Transform root, List<Item> items, float side, float back, float front, float depth)
        {
            var b = items[0].B; foreach (var i in items) b.Encapsulate(i.B);
            var island = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Demo}/Prefabs/FMS_Garden_Demo_Island.prefab"), root);
            island.name = "Plinth_Island";
            var w = b.size.x + 2 * side; var d = b.size.z + back + front;
            var sx = w / IslandLawn.width; var sz = d / IslandLawn.height;
            var cz = b.center.z + (back - front) / 2;
            island.transform.localScale = new Vector3(sx, depth, sz);
            island.transform.position = new Vector3(b.center.x - IslandLawn.center.x * sx, 0, cz - IslandLawn.center.y * sz);
            return island.transform;
        }

        /// <summary>Camera at bearing/pitch; distance so the items take shareW of the width and fit between top and bottom rows; then
        /// centred horizontally with the top of the items at 'top'.</summary>
        private static string Fit(Shot s)
        {
            var pts = s.Items.SelectMany(i => Points(i.Go)).ToList();
            if (s.Plinth != null) pts.AddRange(Points(s.Plinth.gameObject));
            var gb = s.Items[0].B; foreach (var i in s.Items) gb.Encapsulate(i.B);
            var target = new Vector3(gb.center.x, gb.size.y * 0.25f, gb.center.z);
            var rad = Mathf.Deg2Rad;
            var back = new Vector3(Mathf.Sin(s.Bearing * rad) * Mathf.Cos(s.Pitch * rad), Mathf.Sin(s.Pitch * rad), Mathf.Cos(s.Bearing * rad) * Mathf.Cos(s.Pitch * rad));
            Rect a = default;
            for (var pass = 0; pass < 5; pass++)
            {
                float lo = 2, hi = 300;
                for (var i = 0; i < 32; i++)
                {
                    var d = (lo + hi) / 2;
                    Place(s.Cam, target, back, d); a = Viewport(s.Cam, pts);
                    var k = Mathf.Max(a.width / (s.Share * (s.Right - s.Left)), a.height / (s.Bottom - s.Top));
                    if (k > 1) lo = d; else hi = d;
                }
                Place(s.Cam, target, back, hi); a = Viewport(s.Cam, pts);
                var dist = (s.Cam.transform.position - target).magnitude;
                var h = 2 * dist * Mathf.Tan(s.Cam.fieldOfView * 0.5f * rad); var w = h * s.Cam.aspect;
                target += s.Cam.transform.right * ((a.center.x - (s.Left + s.Right) / 2) * w) + s.Cam.transform.up * ((a.center.y - (1 - (s.Top + s.Bottom) / 2)) * h);
            }
            a = Viewport(s.Cam, pts);
            return $"items x {a.xMin:P0}-{a.xMax:P0} (w {a.width:P1}) rows {1 - a.yMax:P1}-{1 - a.yMin:P1}; cam {s.Cam.transform.position.ToString("F2")} dist {(s.Cam.transform.position - target).magnitude:F1}";
        }

        private static string LabelMap(Shot s)
        {
            var sb = new StringBuilder();
            sb.Append("{\n  \"shot\": \"").Append(s.File).Append("\", \"width\": ").Append(s.W).Append(", \"height\": ").Append(s.H)
              .Append(",\n  \"note\": \"pixel rects [x, y, w, h], origin top-left, of the projected LOD0 meshes; labels go under the rect\",\n  \"items\": [\n");
            var cats = new SortedDictionary<string, Rect>();
            var first = true;
            foreach (var i in s.Items.OrderBy(i => i.Id))
            {
                var r = Pixel(Viewport(s.Cam, Points(i.Go)), s);
                var cat = i.Id.Length >= 3 ? i.Id.Substring(0, 3) : i.Id;
                cats[cat] = cats.TryGetValue(cat, out var c) ? Rect.MinMaxRect(Mathf.Min(c.xMin, r.xMin), Mathf.Min(c.yMin, r.yMin), Mathf.Max(c.xMax, r.xMax), Mathf.Max(c.yMax, r.yMax)) : r;
                if (!first) sb.Append(",\n"); first = false;
                sb.Append($"    {{\"id\": \"{i.Id}\", \"prefab\": \"{i.Prefab}\", \"rect\": [{r.x:F0}, {r.y:F0}, {r.width:F0}, {r.height:F0}]}}");
            }
            sb.Append("\n  ],\n  \"categories\": {\n");
            sb.Append(string.Join(",\n", cats.Select(kv => $"    \"{kv.Key}\": [{kv.Value.x:F0}, {kv.Value.y:F0}, {kv.Value.width:F0}, {kv.Value.height:F0}]")));
            sb.Append("\n  }\n}\n");
            return sb.ToString();
        }

        private static Rect Pixel(Rect v, Shot s) => Rect.MinMaxRect(v.xMin * s.W, (1 - v.yMax) * s.H, v.xMax * s.W, (1 - v.yMin) * s.H);

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

        private static List<Vector3> Points(GameObject go)
        {
            var pts = new List<Vector3>();
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null || mf.name == "Wire" || mf.name.EndsWith("_Low1") || mf.name.EndsWith("_LOD1")) continue;
                if (mf.sharedMesh.GetTopology(0) != MeshTopology.Triangles) continue;
                var m = mf.transform.localToWorldMatrix; var v = mf.sharedMesh.vertices;
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

        private static string[] Split(string s) => s.Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
