using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace FarmNature.Editor
{
    /// <summary>
    /// Presentation environment for the beauty renders: gradient sky, warm light + trilight ambient + fog (global),
    /// and per stage (Overall, Showcase, six local compositions) a rocky underside under every island, low-poly clouds
    /// framing it and a perspective hero camera. Everything lives under FarmNature_Environment and is rebuilt on every run.
    /// Presentation only, not pack content. One clean frame per stage, no text.
    /// </summary>
    public static class FarmNatureEnvironmentBuilder
    {
        private const string ScenePath = "Assets/FarmNature/Demo/Scenes/Demo_FarmNature_Showcase.unity";
        private const string RootName = "FarmNature_Environment";
        private const string CompsRoot = "FarmNature_Compositions";
        private const string ShowcaseRoot = "FarmNature_Showcase";
        private const string Dir = "Assets/FarmNature/Demo";
        private const string OutDir = "AssetStore/FarmNature/Draft";
        private const float Fov = 24f;

        private static readonly Color HazeTop = new Color(0.86f, 0.91f, 0.95f);
        private static readonly Color HazeBottom = new Color(0.62f, 0.76f, 0.91f);
        private static readonly Color FogColor = new Color(0.82f, 0.88f, 0.94f);

        private class Stage
        {
            public string Name;      // also the output file name
            public string Target;    // path from the scene root
            public float Yaw, Pitch;
            public float Fill = 0.70f;
            public float? Distance;  // fixed framing (approved Overall shot); null = auto-fit
            public Vector3 LookOffset;
        }

        private static readonly Stage[] Stages =
        {
            new Stage { Name = "Beauty_01_Overall", Target = CompsRoot + "/Comp_Overall", Yaw = -6, Pitch = 33, Distance = 66, LookOffset = new Vector3(0.5f, -2.0f, 0.6f) },
            new Stage { Name = "Beauty_02_1_Beds", Target = ShowcaseRoot + "/Island_Beds", Yaw = 0, Pitch = 50 },
            new Stage { Name = "Beauty_02_2_Crops", Target = ShowcaseRoot + "/Island_Crops", Yaw = 0, Pitch = 50 },
            new Stage { Name = "Beauty_02_3_Trees", Target = ShowcaseRoot + "/Island_Trees", Yaw = 0, Pitch = 44 },
            new Stage { Name = "Beauty_02_4_Plants", Target = ShowcaseRoot + "/Island_Plants", Yaw = 0, Pitch = 50 },
            new Stage { Name = "Beauty_02_5_WaterRocks", Target = ShowcaseRoot + "/Island_WaterRocks", Yaw = 0, Pitch = 50 },
            new Stage { Name = "Beauty_02_6_Modules", Target = ShowcaseRoot + "/Island_Modules", Yaw = 0, Pitch = 52 },
            new Stage { Name = "Beauty_03_1_Garden", Target = CompsRoot + "/Comp_Ogorod", Yaw = 45, Pitch = 35 },
            new Stage { Name = "Beauty_03_2_Field", Target = CompsRoot + "/Comp_Pole", Yaw = 45, Pitch = 35 },
            new Stage { Name = "Beauty_03_3_Orchard", Target = CompsRoot + "/Comp_Sad", Yaw = 45, Pitch = 35 },
            new Stage { Name = "Beauty_03_4_PondBridge", Target = CompsRoot + "/Comp_Prud", Yaw = 45, Pitch = 35 },
            new Stage { Name = "Beauty_03_5_ForestEdge", Target = CompsRoot + "/Comp_Opushka", Yaw = 45, Pitch = 35 },
            new Stage { Name = "Beauty_03_6_FlowerPath", Target = CompsRoot + "/Comp_Tropa", Yaw = 45, Pitch = 35 },
        };

        // Cloud layout tuned on the Overall shot, in island extents: u along camera right (x eR), v along camera
        // forward (x eF), w up (x eR), size (x eR).
        private static readonly (float U, float V, float W, float S)[] CloudSpots =
        {
            (-1.42f, 0.17f, -0.27f, 0.085f), (1.42f, 0.35f, -0.24f, 0.091f),                                   // sides
            (-1.03f, 1.91f, 0.00f, 0.097f), (1.09f, 2.09f, 0.06f, 0.103f), (-0.06f, 2.61f, -0.09f, 0.085f),     // behind
            (-0.73f, -0.52f, -0.61f, 0.121f), (0.73f, -0.35f, -0.64f, 0.127f), (0.00f, -1.22f, -0.79f, 0.097f), // bank below
            (-1.45f, -1.22f, -0.61f, 0.073f), (1.52f, -1.04f, -0.61f, 0.079f),
            (-1.58f, -0.35f, 0.18f, 0.042f), (1.58f, -0.17f, 0.12f, 0.036f),                                   // small puffs
        };

        // ---------------- menus ----------------

        [MenuItem("Tools/Farm Nature/Build Environment")]
        public static void Build()
        {
            var scene = EditorSceneManager.GetActiveScene();
            if (scene.path != ScenePath) scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

            var old = GameObject.Find(RootName);
            if (old != null) Object.DestroyImmediate(old);
            var root = new GameObject(RootName).transform;

            SetupSkyAndLight();
            var cloudMat = CloudMaterial();
            var (soil, rock) = UndersideMaterials();
            Camera first = null;
            foreach (var stage in Stages)
            {
                var target = Find(stage.Target);
                var stageRoot = new GameObject("Stage_" + stage.Name).transform;
                stageRoot.SetParent(root, false);

                var hulls = BuildUndersides(target, stageRoot, soil, rock, out var centre, out var all);
                var cam = BuildCamera(stage, stageRoot, target, centre);
                BuildClouds(stage, stageRoot, cam, centre, all, cloudMat);
                if (first == null) first = cam;
            }

            EditorSceneManager.SaveScene(scene);
            var view = SceneView.lastActiveSceneView;
            if (view != null && first != null) view.AlignViewToObject(first.transform);
            Debug.Log($"[FarmNature] environment built: {Stages.Length} stages");
        }

        [MenuItem("Tools/Farm Nature/Render Beauty All")]
        public static void RenderAll()
        {
            foreach (var stage in Stages) RenderStage(stage);
            Debug.Log("[FarmNature] beauty renders -> " + OutDir);
        }

        [MenuItem("Tools/Farm Nature/Render Beauty 01 Overall")]
        public static void RenderOverall() => RenderStage(Stages[0]);

        private static void RenderStage(Stage stage)
        {
            Directory.CreateDirectory(OutDir);
            var stageRoot = GameObject.Find(RootName).transform.Find("Stage_" + stage.Name);
            var cam = stageRoot.Find("HeroCam").GetComponent<Camera>();
            var target = Find(stage.Target);

            // only this stage is visible: siblings along the target's path, other FarmNature roots and other stages are hidden
            var hidden = new List<GameObject>();
            void Hide(GameObject g) { if (g.activeSelf) { g.SetActive(false); hidden.Add(g); } }
            for (var t = target; t.parent != null; t = t.parent)
                foreach (Transform s in t.parent) if (s != t) Hide(s.gameObject);
            foreach (var g in target.gameObject.scene.GetRootGameObjects())
                if (g.name.StartsWith("FarmNature_") && g.transform != target.root && g.name != RootName) Hide(g);
            foreach (Transform s in GameObject.Find(RootName).transform) if (s != stageRoot) Hide(s.gameObject);

            // fog relative to this camera distance so distant clouds fade, the island stays crisp
            var d = Vector3.Distance(cam.transform.position, target.position);
            float oldStart = RenderSettings.fogStartDistance, oldEnd = RenderSettings.fogEndDistance;
            RenderSettings.fogStartDistance = d * 1.06f;
            RenderSettings.fogEndDistance = d * 2.6f;
            try { FarmNatureCompositionBuilder.RenderShot(cam, $"{OutDir}/{stage.Name}.png", 1920, 1080, 2); }
            finally
            {
                RenderSettings.fogStartDistance = oldStart;
                RenderSettings.fogEndDistance = oldEnd;
                foreach (var g in hidden) g.SetActive(true);
            }
        }

        private static Transform Find(string path)
        {
            var parts = path.Split('/');
            var t = GameObject.Find(parts[0]).transform;
            foreach (var p in parts.Skip(1)) t = t.Find(p);
            if (t == null) throw new Exception("not found: " + path);
            return t;
        }

        // ---------------- sky, light, fog ----------------

        private static void SetupSkyAndLight()
        {
            var sky = LoadOrCreate($"{Dir}/Materials/M_Demo_Sky.mat", "FarmNature/Demo/URP Panorama Sky");
            sky.SetTexture("_MainTex", SkyTexture());
            sky.SetFloat("_Exposure", 1f);
            sky.SetFloat("_Mapping", 1f);        // latitude-longitude
            sky.SetFloat("_ImageType", 0f);      // 360
            RenderSettings.skybox = sky;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.66f, 0.76f, 0.88f);
            RenderSettings.ambientEquatorColor = new Color(0.74f, 0.76f, 0.70f);
            RenderSettings.ambientGroundColor = new Color(0.42f, 0.38f, 0.33f);

            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = FogColor;
            RenderSettings.fogStartDistance = 70f;
            RenderSettings.fogEndDistance = 170f;

            var light = GameObject.Find("Directional Light").GetComponent<Light>();
            light.transform.rotation = Quaternion.Euler(48, 32, 0);   // warm sun from the upper left
            light.color = new Color(1f, 0.94f, 0.84f);
            light.intensity = 1.25f;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.8f;
        }

        /// <summary>Equirect sky: haze near the horizon, deeper blue up and down (the cameras look down, so the lower half is the backdrop).</summary>
        private static Texture2D SkyTexture()
        {
            var path = $"{Dir}/Textures/T_Demo_SkyPanorama.png";
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            const int w = 512, h = 512;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            var zenith = new Color(0.45f, 0.66f, 0.89f);
            var horizon = new Color(0.95f, 0.94f, 0.88f);
            for (var y = 0; y < h; y++)
            {
                var elev = (y + 0.5f) / h * 180f - 90f;
                Color c;
                if (elev >= 0) c = Color.Lerp(horizon, zenith, Mathf.SmoothStep(0, 1, elev / 70f));
                else
                {
                    var k = Mathf.Clamp01(-elev / 60f);
                    c = k < 0.3f ? Color.Lerp(horizon, HazeTop, k / 0.3f) : Color.Lerp(HazeTop, HazeBottom, Mathf.SmoothStep(0, 1, (k - 0.3f) / 0.7f));
                }
                for (var x = 0; x < w; x++) tex.SetPixel(x, y, c);
            }
            File.WriteAllBytes(path, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.wrapModeV = TextureWrapMode.Clamp;
            importer.mipmapEnabled = false;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        // ---------------- floating island undersides ----------------

        private static (Material, Material) UndersideMaterials()
        {
            var soil = LoadOrCreate($"{Dir}/Materials/M_Demo_UndersideSoil.mat", "Universal Render Pipeline/Lit");
            soil.SetColor("_BaseColor", new Color(0.43f, 0.28f, 0.17f));
            soil.SetFloat("_Smoothness", 0.05f);
            var rock = LoadOrCreate($"{Dir}/Materials/M_Demo_UndersideRock.mat", "Universal Render Pipeline/Lit");
            rock.SetColor("_BaseColor", new Color(0.56f, 0.50f, 0.44f));
            rock.SetFloat("_Smoothness", 0.05f);
            return (soil, rock);
        }

        /// <summary>
        /// One rocky underside per island: islands are the ground pieces (Ground / IslandTop / IslandSkirt / Slab / Pit)
        /// grouped by parent; the outline is the convex hull of their vertices. Returns the stage centre and all hull points.
        /// </summary>
        private static int BuildUndersides(Transform target, Transform stageRoot, Material soil, Material rock, out Vector3 centre, out List<Vector3> all)
        {
            var names = new HashSet<string> { "Ground", "IslandTop", "IslandSkirt", "Slab", "Pit" };
            var groups = target.GetComponentsInChildren<MeshFilter>(true).Where(f => names.Contains(f.name)).GroupBy(f => f.transform.parent);
            all = new List<Vector3>();
            var count = 0;
            foreach (var g in groups)
            {
                var pts = new List<Vector2>();
                var bottom = float.MaxValue;
                foreach (var f in g)
                    foreach (var v in f.sharedMesh.vertices)
                    {
                        var w = f.transform.TransformPoint(v);
                        pts.Add(new Vector2(w.x, w.z));
                        bottom = Mathf.Min(bottom, w.y);
                    }
                var hull = Resample(ConvexHull(pts), 64);
                var c2 = hull.Aggregate(Vector2.zero, (a, p) => a + p) / hull.Length;
                var extent = hull.Max(p => (p - c2).magnitude);
                BuildUnderside(stageRoot, new Vector3(c2.x, bottom, c2.y), hull.Select(p => p - c2).ToArray(), extent, soil, rock, ++count);
                all.AddRange(hull.Select(p => new Vector3(p.x, 0, p.y)));
            }
            var b = new Bounds(all[0], Vector3.zero);
            foreach (var p in all) b.Encapsulate(p);
            centre = new Vector3(b.center.x, target.position.y, b.center.z);
            return count;
        }

        private static void BuildUnderside(Transform parent, Vector3 origin, Vector2[] outline, float extent, Material soil, Material rock, int seed)
        {
            // (drop below the slab bottom in island extents, outline scale, radial jitter): near-vertical cliff, then the root
            var rings = new (float Y, float S, float J)[]
            {
                (0f, 1.00f, 0f), (0.09f, 0.985f, 0.025f), (0.19f, 0.92f, 0.05f), (0.29f, 0.74f, 0.08f), (0.38f, 0.48f, 0.10f), (0.47f, 0.22f, 0.10f),
            };
            var seg = outline.Length;
            var rnd = new System.Random(seed * 7 + 5);
            var pts = new Vector3[rings.Length, seg];
            for (var r = 0; r < rings.Length; r++)
                for (var i = 0; i < seg; i++)
                {
                    var j = 1 + (float)(rnd.NextDouble() * 2 - 1) * rings[r].J;
                    var dy = r == 0 ? 0 : (float)(rnd.NextDouble() * 2 - 1) * 0.02f * extent;
                    var o = outline[i] * rings[r].S * j;
                    pts[r, i] = new Vector3(o.x, -rings[r].Y * extent + dy, o.y);
                }
            var verts = new List<Vector3>();
            var soilTris = new List<int>();
            var rockTris = new List<int>();
            for (var r = 0; r < rings.Length - 1; r++)
                for (var i = 0; i < seg; i++)
                {
                    var a = pts[r, i];
                    var b = pts[r, (i + 1) % seg];
                    var c = pts[r + 1, (i + 1) % seg];
                    var d = pts[r + 1, i];
                    var list = r < 1 ? soilTris : rockTris; // soil layer, then a grey-brown rock band
                    AddTri(verts, list, a, c, b, Down((a + c) / 2));
                    AddTri(verts, list, a, d, c, Down((a + c) / 2));
                }
            var tip = new Vector3(0.04f * extent, -0.55f * extent, -0.03f * extent);
            for (var i = 0; i < seg; i++)
            {
                var a = pts[rings.Length - 1, i];
                AddTri(verts, rockTris, a, tip, pts[rings.Length - 1, (i + 1) % seg], Down(a));
            }
            var mesh = new Mesh { name = "Underside_" + seed };
            mesh.SetVertices(verts);
            mesh.subMeshCount = 2;
            mesh.SetTriangles(soilTris, 0);
            mesh.SetTriangles(rockTris, 1);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();

            var go = new GameObject("Underside_" + seed);
            go.transform.SetParent(parent, false);
            go.transform.position = origin;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterials = new[] { soil, rock };
        }

        private static Vector2[] ConvexHull(List<Vector2> pts)
        {
            var p = pts.Distinct().OrderBy(v => v.x).ThenBy(v => v.y).ToList();
            float Cross(Vector2 o, Vector2 a, Vector2 b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
            var h = new List<Vector2>();
            foreach (var pass in new[] { p, Enumerable.Reverse(p).ToList() })
            {
                var start = h.Count;
                foreach (var v in pass)
                {
                    while (h.Count >= start + 2 && Cross(h[h.Count - 2], h[h.Count - 1], v) <= 0) h.RemoveAt(h.Count - 1);
                    h.Add(v);
                }
                h.RemoveAt(h.Count - 1);
            }
            return h.ToArray();
        }

        private static Vector2[] Resample(Vector2[] poly, int count)
        {
            var lengths = new float[poly.Length];
            var total = 0f;
            for (var i = 0; i < poly.Length; i++) { lengths[i] = (poly[(i + 1) % poly.Length] - poly[i]).magnitude; total += lengths[i]; }
            var res = new Vector2[count];
            int seg = 0; float acc = 0;
            for (var k = 0; k < count; k++)
            {
                var target = k * total / count;
                while (acc + lengths[seg] < target) { acc += lengths[seg]; seg++; }
                var t = lengths[seg] > 0 ? (target - acc) / lengths[seg] : 0;
                res[k] = Vector2.Lerp(poly[seg], poly[(seg + 1) % poly.Length], t);
            }
            return res;
        }

        // ---------------- camera ----------------

        private static Camera BuildCamera(Stage stage, Transform stageRoot, Transform target, Vector3 centre)
        {
            var go = new GameObject("HeroCam");
            go.transform.SetParent(stageRoot, false);
            go.transform.rotation = Quaternion.Euler(stage.Pitch, stage.Yaw, 0);
            var cam = go.AddComponent<Camera>();
            cam.orthographic = false;
            cam.fieldOfView = Fov;
            cam.aspect = 16f / 9f;
            cam.nearClipPlane = 0.5f;
            cam.farClipPlane = 600f;
            cam.clearFlags = CameraClearFlags.Skybox;
            cam.enabled = false;

            if (stage.Distance.HasValue)
            {
                go.transform.position = target.position + stage.LookOffset - go.transform.forward * stage.Distance.Value;
                return cam;
            }

            // auto-fit on real vertices (bounding boxes bloat the frame): content + undersides fill `Fill` of the width
            var points = new List<Vector3>();
            foreach (var f in target.GetComponentsInChildren<MeshFilter>().Concat(stageRoot.GetComponentsInChildren<MeshFilter>()))
            {
                var m = f.transform.localToWorldMatrix;
                var vs = f.sharedMesh.vertices;
                for (var i = 0; i < vs.Length; i += 3) points.Add(m.MultiplyPoint3x4(vs[i]));
            }
            var look = centre;
            var d = 60f;
            var tanV = Mathf.Tan(Fov * 0.5f * Mathf.Deg2Rad);
            for (var it = 0; it < 10; it++)
            {
                go.transform.position = look - go.transform.forward * d;
                float minX = 1, maxX = 0, minY = 1, maxY = 0;
                foreach (var p in points)
                {
                    var v = cam.WorldToViewportPoint(p);
                    minX = Mathf.Min(minX, v.x); maxX = Mathf.Max(maxX, v.x);
                    minY = Mathf.Min(minY, v.y); maxY = Mathf.Max(maxY, v.y);
                }
                var hgt = 2 * d * tanV;
                look += go.transform.right * (((minX + maxX) / 2 - 0.5f) * hgt * cam.aspect) + go.transform.up * (((minY + maxY) / 2 - 0.5f) * hgt);
                d *= Mathf.Max((maxX - minX) / stage.Fill, (maxY - minY) / 0.80f);
            }
            go.transform.position = look - go.transform.forward * d;
            return cam;
        }

        // ---------------- clouds ----------------

        private static Material CloudMaterial()
        {
            var mat = LoadOrCreate($"{Dir}/Materials/M_Demo_Cloud.mat", "Universal Render Pipeline/Lit");
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Smoothness", 0f);
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", new Color(0.22f, 0.24f, 0.28f)); // keeps the shaded side airy, not grey
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None;
            return mat;
        }

        private static void BuildClouds(Stage stage, Transform stageRoot, Camera cam, Vector3 centre, List<Vector3> hull, Material mat)
        {
            var right = cam.transform.right; right.y = 0; right.Normalize();
            var fwd = cam.transform.forward; fwd.y = 0; fwd.Normalize();
            var eR = hull.Max(p => Mathf.Abs(Vector3.Dot(p - centre, right)));
            var eF = hull.Max(p => Mathf.Abs(Vector3.Dot(p - centre, fwd)));

            var parent = new GameObject("Clouds").transform;
            parent.SetParent(stageRoot, false);
            var seed = Math.Abs(stage.Name.GetHashCode()) % 1000;
            for (var i = 0; i < CloudSpots.Length; i++)
            {
                var (u, v, w, s) = CloudSpots[i];
                var go = new GameObject($"Cloud_{i:00}");
                go.transform.SetParent(parent, false);
                go.transform.position = centre + right * (u * eR) + fwd * (v * eF) + Vector3.up * (w * eR);
                go.transform.rotation = Quaternion.LookRotation(fwd) * Quaternion.Euler(0, (seed + i * 37) % 40 - 20, 0);
                go.AddComponent<MeshFilter>().sharedMesh = CloudMesh(seed + i, s * Mathf.Max(eR, 10f)); // small islands still get proper puffy clouds
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = mat;
                mr.shadowCastingMode = ShadowCastingMode.Off;
                mr.receiveShadows = false;
            }
        }

        /// <summary>Faceted puff cluster: icospheres along x, biggest in the middle, flat bottom.</summary>
        private static Mesh CloudMesh(int seed, float size)
        {
            var rnd = new System.Random(seed * 101);
            var verts = new List<Vector3>();
            var tris = new List<int>();
            var puffs = 5 + rnd.Next(4);
            var ico = Icosphere();
            for (var i = 0; i < puffs; i++)
            {
                var k = i / (float)(puffs - 1) * 2 - 1;     // -1..1
                var r = size * (0.55f + 0.45f * (1 - k * k)) * (0.85f + 0.3f * (float)rnd.NextDouble());
                var centre = new Vector3(k * size * 1.6f, r * 0.25f, (float)(rnd.NextDouble() * 2 - 1) * size * 0.45f);
                var rot = Quaternion.Euler((float)rnd.NextDouble() * 360, (float)rnd.NextDouble() * 360, 0);
                for (var t = 0; t < ico.tris.Length; t += 3)
                {
                    Vector3 V(int n)
                    {
                        var v = centre + rot * ico.verts[ico.tris[t + n]] * r;
                        v.y = Mathf.Max(v.y, 0) * 0.82f;   // flat bottom, slightly squashed
                        return v;
                    }
                    var a = V(0); var b = V(1); var c = V(2);
                    AddTri(verts, tris, a, b, c, (a + b + c) / 3 - centre);
                }
            }
            var mesh = new Mesh { name = "Cloud_" + seed, indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static (Vector3[] verts, int[] tris) Icosphere()
        {
            var t = (1 + Mathf.Sqrt(5)) / 2;
            var v = new List<Vector3>
            {
                new Vector3(-1, t, 0), new Vector3(1, t, 0), new Vector3(-1, -t, 0), new Vector3(1, -t, 0),
                new Vector3(0, -1, t), new Vector3(0, 1, t), new Vector3(0, -1, -t), new Vector3(0, 1, -t),
                new Vector3(t, 0, -1), new Vector3(t, 0, 1), new Vector3(-t, 0, -1), new Vector3(-t, 0, 1),
            }.Select(p => p.normalized).ToList();
            var f = new List<int>
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            var cache = new Dictionary<long, int>();
            int Mid(int a, int b)
            {
                var key = a < b ? ((long)a << 32) + b : ((long)b << 32) + a;
                if (cache.TryGetValue(key, out var idx)) return idx;
                v.Add(((v[a] + v[b]) / 2).normalized);
                cache[key] = v.Count - 1;
                return v.Count - 1;
            }
            var f2 = new List<int>();
            for (var i = 0; i < f.Count; i += 3)
            {
                int a = f[i], b = f[i + 1], c = f[i + 2];
                int ab = Mid(a, b), bc = Mid(b, c), ca = Mid(c, a);
                f2.AddRange(new[] { a, ab, ca, b, bc, ab, c, ca, bc, ab, bc, ca });
            }
            return (v.ToArray(), f2.ToArray());
        }

        // ---------------- helpers ----------------

        /// <summary>Adds a flat-shaded triangle whose face normal (Unity: cross(b-a, c-a)) points along <paramref name="outward"/>.</summary>
        private static void AddTri(List<Vector3> verts, List<int> tris, Vector3 a, Vector3 b, Vector3 c, Vector3 outward)
        {
            var i = verts.Count;
            verts.Add(a); verts.Add(b); verts.Add(c);
            if (Vector3.Dot(Vector3.Cross(b - a, c - a), outward) >= 0) tris.AddRange(new[] { i, i + 1, i + 2 });
            else tris.AddRange(new[] { i, i + 2, i + 1 });
        }

        /// <summary>Outward-and-down direction for an underside cone (island centre is the local origin).</summary>
        private static Vector3 Down(Vector3 p) => new Vector3(p.x, -2f, p.z);

        private static Material LoadOrCreate(string path, string shader)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find(shader));
                AssetDatabase.CreateAsset(mat, path);
            }
            EditorUtility.SetDirty(mat);
            return mat;
        }
    }
}
