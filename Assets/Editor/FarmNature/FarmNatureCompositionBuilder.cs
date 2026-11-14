using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Object = UnityEngine.Object;

namespace FarmNature.Editor
{
    /// <summary>
    /// Builds the hand-placed compositions (NATURE_COMPOSITIONS sheets 01 and 03) into the demo scene,
    /// next to the showcase islands. Layout lives in FarmNatureCompositions.txt (see its header for the syntax).
    /// Each composition gets a disabled ortho shot camera; Build renders every shot into %TEMP%.
    /// </summary>
    public static class FarmNatureCompositionBuilder
    {
        private const string LayoutPath = "Assets/Editor/FarmNature/FarmNatureCompositions.txt";
        private const string ScenePath = "Assets/FarmNature/Demo/Scenes/Demo_FarmNature_Showcase.unity";
        private const string PrefabDir = "Assets/FarmNature/Art/Prefabs";
        private const string MaterialDir = "Assets/FarmNature/Demo/Materials";
        private const string RootName = "FarmNature_Compositions";
        private const float BaseBottom = -0.6f;
        private const float PitTop = -0.3f;
        private const float TreeFootprint = 1.2f;

        internal class Comp
        {
            public string Name;
            public Transform Root;
            public readonly List<Vector2[]> Polys = new List<Vector2[]>();
            public readonly List<Rect> Blocked = new List<Rect>();
            public readonly List<Vector2> Scattered = new List<Vector2>();
            public Camera Shot;
            public Vector2[] Island;
            public float Skirt;
            public readonly List<GameObject> Water = new List<GameObject>();
        }

        private const float GrassTile = 6.7f;   // world size of one repeat of the faceted grass texture
        private const float IslandStep = 0.2f;  // grid of the island top; holes are cut where water is

        [MenuItem("Tools/Farm Nature/Build Compositions")]
        public static void BuildMenu()
        {
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var comps = BuildIntoOpenScene();
            EditorSceneManager.SaveScene(scene);
            foreach (var c in comps)
                Render(c.Shot, Path.Combine(Path.GetTempPath(), $"FarmNature_Comp_{c.Name}.png"));
            Debug.Log($"[FarmNature] compositions built: {string.Join(", ", comps.Select(c => c.Name))}");
        }

        internal static List<Comp> BuildIntoOpenScene()
        {
            var old = GameObject.Find(RootName);
            if (old != null) Object.DestroyImmediate(old);
            var root = new GameObject(RootName).transform;

            var (grass, soil) = GroundMaterials();

            var comps = new List<Comp>();
            Comp comp = null;
            var lineNo = 0;
            foreach (var raw in File.ReadAllLines(LayoutPath))
            {
                lineNo++;
                var line = raw.Split('#')[0].Trim();
                if (line.Length == 0) continue;
                var t = line.Split((char[])null, StringSplitOptions.RemoveEmptyEntries);
                try
                {
                    switch (t[0])
                    {
                        case "comp":
                            if (comp?.Island != null) BuildIsland(comp, grass, soil);
                            comp = new Comp { Name = t[1], Root = new GameObject("Comp_" + t[1]).transform };
                            comp.Root.SetParent(root, false);
                            comp.Root.localPosition = new Vector3(F(t[2]), 0, F(t[3]));
                            comp.Shot = CreateShot(comp, F(t[4]), F(t[5]), F(t[6]), new Vector3(F(t[7]), F(t[8]), F(t[9])));
                            comps.Add(comp);
                            break;
                        case "island":
                            comp.Island = SuperEllipse(F(t[1]), F(t[2]), F(t[3]), int.Parse(t[4]));
                            comp.Skirt = F(t[5]);
                            comp.Polys.Add(comp.Island);
                            break;
                        case "octagon":
                            AddPoly(comp, Octagon(F(t[1]), F(t[2]), F(t[3])), grass, soil, 0);
                            break;
                        case "poly":
                            var pts = new Vector2[(t.Length - 1) / 2];
                            for (var i = 0; i < pts.Length; i++) pts[i] = new Vector2(F(t[1 + 2 * i]), F(t[2 + 2 * i]));
                            AddPoly(comp, pts, grass, soil, 0);
                            break;
                        case "pit":
                            var x0 = F(t[1]); var z0 = F(t[2]); var x1 = F(t[3]); var z1 = F(t[4]);
                            MakePrism(comp.Root, "Pit", new[] { new Vector2(x0, z0), new Vector2(x1, z0), new Vector2(x1, z1), new Vector2(x0, z1) }, PitTop, BaseBottom, soil, soil);
                            break;
                        case "scatter":
                            Scatter(comp, t);
                            break;
                        case "row":
                            Row(comp, t);
                            break;
                        default:
                            Place(comp, t[0], F(t[1]), F(t[2]), Rot(t, 3, F(t[1]), F(t[2])), t.Length > 4 ? F(t[4]) : 1f, t.Length > 5 ? F(t[5]) : 0f, true);
                            break;
                    }
                }
                catch (Exception e)
                {
                    throw new Exception($"{LayoutPath}:{lineNo}: '{line}' -> {e.Message}", e);
                }
            }
            if (comp?.Island != null) BuildIsland(comp, grass, soil);
            return comps;
        }

        private static (Material Grass, Material Soil) GroundMaterials()
        {
            var grass = LoadOrCreateMaterial("M_Demo_GroundGrass", Color.white);
            grass.SetTexture("_BaseMap", LoadOrCreateGrassTexture());
            var soil = LoadOrCreateMaterial("M_Demo_GroundSoil", new Color(0.46f, 0.29f, 0.16f));
            return (grass, soil);
        }

        /// <summary>Showcase island ground: chamfered slab (grass + soil skirt) and grass tufts around the exhibits.</summary>
        internal static void DecorateShowcaseIsland(Transform root, Vector2 size, int seed)
        {
            var (grass, soil) = GroundMaterials();
            var poly = Octagon(size.x / 2, size.y / 2, 0.6f);
            var comp = new Comp { Name = root.name, Root = root };
            comp.Polys.Add(poly);
            foreach (var r in root.GetComponentsInChildren<Renderer>())
            {
                var b = r.bounds;
                comp.Blocked.Add(new Rect(b.min.x - root.position.x, b.min.z - root.position.z, b.size.x, b.size.z));
            }
            // water blocks (banks at 0.30) are sunk flush; the grass top then gets holes over the water
            foreach (Transform item in root)
            {
                var n = System.Text.RegularExpressions.Regex.Replace(item.name, @"^\d\d_", "");
                if (!(n.StartsWith("Water_Stream") || n.StartsWith("Water_Pond") || n == "Water_Puddle_Round")) continue;
                item.localPosition += Vector3.down * 0.30f;
                comp.Water.Add(item.gameObject);
            }
            if (comp.Water.Count > 0)
            {
                comp.Island = poly;
                comp.Skirt = 0.5f;
                BuildIsland(comp, grass, soil);
            }
            else MakePrism(root, "Slab", poly, 0, -0.5f, grass, soil);
            var count = Mathf.RoundToInt(size.x * size.y * 0.45f);
            string I(float v) => v.ToString(CultureInfo.InvariantCulture);
            Scatter(comp, new[] { "scatter", "Grass_Tuft_S,Grass_Tuft_M", "0", "0", I(size.x / 2), I(size.y / 2), count.ToString(), seed.ToString() });
        }

        /// <summary>Thin tilled-soil strip (crop rows on the showcase island).</summary>
        internal static void MakeSoilStrip(Transform parent, Rect r, float height)
        {
            var mat = LoadOrCreateMaterial("M_Demo_SoilStrip", new Color(0.38f, 0.24f, 0.14f));
            var pts = new[] { new Vector2(r.xMin, r.yMin), new Vector2(r.xMax, r.yMin), new Vector2(r.xMax, r.yMax), new Vector2(r.xMin, r.yMax) };
            MakePrism(parent, "SoilStrip", pts, height, -0.01f, mat, mat);
        }

        // ---------- placement ----------

        private static GameObject Place(Comp comp, string name, float x, float z, float rot, float scale, float y, bool block)
        {
            var category = name.Split('_')[0];
            var path = $"{PrefabDir}/{category}/FMS_{name}.prefab";
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) throw new Exception("missing prefab " + path);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, comp.Root);
            go.transform.localPosition = new Vector3(x, y, z);
            go.transform.localRotation = Quaternion.Euler(0, rot, 0);
            go.transform.localScale = Vector3.one * scale;
            if (name.StartsWith("Water_Stream") || name.StartsWith("Water_Pond")) comp.Water.Add(go);
            if (block)
            {
                if (category == "Tree")
                    comp.Blocked.Add(new Rect(x - TreeFootprint / 2, z - TreeFootprint / 2, TreeFootprint, TreeFootprint));
                else
                {
                    var b = go.GetComponentsInChildren<Renderer>().Select(r => r.bounds).Aggregate((a, c) => { a.Encapsulate(c); return a; });
                    var local = comp.Root.position;
                    comp.Blocked.Add(new Rect(b.min.x - local.x, b.min.z - local.z, b.size.x, b.size.z));
                }
            }
            return go;
        }

        // scatter A,B,C cx cz rx rz count seed [smin smax]  -- random points in an ellipse, skipping blocked areas
        private static void Scatter(Comp comp, string[] t)
        {
            var names = t[1].Split(',');
            float cx = F(t[2]), cz = F(t[3]), rx = F(t[4]), rz = F(t[5]);
            int count = int.Parse(t[6]), seed = int.Parse(t[7]);
            float smin = t.Length > 8 ? F(t[8]) : 0.85f, smax = t.Length > 9 ? F(t[9]) : 1.15f;
            var rnd = new System.Random(seed);
            var placed = 0;
            for (var attempt = 0; attempt < count * 40 && placed < count; attempt++)
            {
                var a = rnd.NextDouble() * Math.PI * 2;
                var r = Math.Sqrt(rnd.NextDouble());
                var p = new Vector2(cx + (float)(Math.Cos(a) * r * rx), cz + (float)(Math.Sin(a) * r * rz));
                if (!comp.Polys.Any(poly => Inside(poly, p, 0.3f))) continue;
                if (comp.Blocked.Any(b => Inflate(b, 0.15f).Contains(p))) continue;
                if (comp.Scattered.Any(s => (s - p).sqrMagnitude < 0.35f * 0.35f)) continue;
                var name = names[rnd.Next(names.Length)];
                var scale = smin + (float)rnd.NextDouble() * (smax - smin);
                Place(comp, name, p.x, p.y, (float)rnd.NextDouble() * 360f, scale, 0, false);
                comp.Scattered.Add(p);
                placed++;
            }
        }

        // row A,B x0 z0 x1 z1 count [rot|r] [y] [scale]
        private static void Row(Comp comp, string[] t)
        {
            var names = t[1].Split(',');
            float x0 = F(t[2]), z0 = F(t[3]), x1 = F(t[4]), z1 = F(t[5]);
            var count = int.Parse(t[6]);
            var y = t.Length > 8 ? F(t[8]) : 0f;
            var scale = t.Length > 9 ? F(t[9]) : 1f;
            for (var i = 0; i < count; i++)
            {
                var k = count == 1 ? 0.5f : i / (float)(count - 1);
                var x = Mathf.Lerp(x0, x1, k);
                var z = Mathf.Lerp(z0, z1, k);
                Place(comp, names[i % names.Length], x, z, Rot(t, 7, x, z), scale, y, true);
            }
        }

        private static float Rot(string[] t, int index, float x, float z)
        {
            if (t.Length <= index) return 0f;
            if (t[index] != "r") return F(t[index]);
            var h = Mathf.Abs(Mathf.Sin(x * 12.9898f + z * 78.233f) * 43758.547f);
            return (h - Mathf.Floor(h)) * 360f;
        }

        // ---------- ground ----------

        private static void AddPoly(Comp comp, Vector2[] pts, Material top, Material side, float topY)
        {
            comp.Polys.Add(pts);
            MakePrism(comp.Root, "Ground", pts, topY, BaseBottom, top, side);
        }

        private static Vector2[] Octagon(float hx, float hz, float c) => new[]
        {
            new Vector2(-hx + c, -hz), new Vector2(hx - c, -hz), new Vector2(hx, -hz + c), new Vector2(hx, hz - c),
            new Vector2(hx - c, hz), new Vector2(-hx + c, hz), new Vector2(-hx, hz - c), new Vector2(-hx, -hz + c),
        };

        /// <summary>Convex prism: flat top (submesh 0) and vertical sides + bottom (submesh 1).</summary>
        private static void MakePrism(Transform parent, string name, Vector2[] pts, float top, float bottom, Material topMat, Material sideMat, bool capTop = true)
        {
            var centre = pts.Aggregate(Vector2.zero, (a, p) => a + p) / pts.Length;
            var verts = new List<Vector3>();
            var topTris = new List<int>();
            var sideTris = new List<int>();

            void Tri(List<int> list, Vector3 a, Vector3 b, Vector3 c, Vector3 outward)
            {
                var i = verts.Count;
                verts.Add(a); verts.Add(b); verts.Add(c);
                // Unity: front face is clockwise seen from outside; cross(b-a, c-a) must point outward
                if (Vector3.Dot(Vector3.Cross(b - a, c - a), outward) >= 0) list.AddRange(new[] { i, i + 1, i + 2 });
                else list.AddRange(new[] { i, i + 2, i + 1 });
            }

            for (var i = 0; i < pts.Length; i++)
            {
                var p = pts[i];
                var q = pts[(i + 1) % pts.Length];
                if (capTop) Tri(topTris, V(centre, top), V(p, top), V(q, top), Vector3.up);
                Tri(sideTris, V(centre, bottom), V(q, bottom), V(p, bottom), Vector3.down);
                var mid = (p + q) / 2 - centre;
                var outward = new Vector3(mid.x, 0, mid.y);
                Tri(sideTris, V(p, top), V(q, top), V(q, bottom), outward);
                Tri(sideTris, V(p, top), V(q, bottom), V(p, bottom), outward);
            }

            var mesh = new Mesh { name = name };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, verts.Select(v => new Vector2(v.x, v.z) / GrassTile).ToList());
            mesh.subMeshCount = 2;
            mesh.SetTriangles(topTris, 0);
            mesh.SetTriangles(sideTris, 1);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();

            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterials = new[] { topMat, sideMat };
            go.AddComponent<MeshCollider>().sharedMesh = mesh;
        }

        private static Vector3 V(Vector2 p, float y) => new Vector3(p.x, y, p.y);

        private static bool Inside(Vector2[] poly, Vector2 p, float margin)
        {
            // convex polygon, either winding: all edge cross products share a sign and clear the margin
            var sign = 0;
            for (var i = 0; i < poly.Length; i++)
            {
                var a = poly[i];
                var b = poly[(i + 1) % poly.Length];
                var e = b - a;
                var cross = e.x * (p.y - a.y) - e.y * (p.x - a.x);
                var dist = cross / e.magnitude;
                var s = dist > 0 ? 1 : -1;
                if (Mathf.Abs(dist) < margin) return false;
                if (sign == 0) sign = s;
                else if (s != sign) return false;
            }
            return true;
        }

        private static Rect Inflate(Rect r, float m) => new Rect(r.x - m, r.y - m, r.width + 2 * m, r.height + 2 * m);

        // ---------- organic island with water holes ----------

        private static Vector2[] SuperEllipse(float a, float b, float n, int count)
        {
            var pts = new Vector2[count];
            for (var i = 0; i < count; i++)
            {
                var t = i / (float)count * Mathf.PI * 2;
                float c = Mathf.Cos(t), s = Mathf.Sin(t);
                pts[i] = new Vector2(a * Mathf.Sign(c) * Mathf.Pow(Mathf.Abs(c), 2 / n), b * Mathf.Sign(s) * Mathf.Pow(Mathf.Abs(s), 2 / n));
            }
            return pts;
        }

        /// <summary>Grid top at y=0 (cells touching water skipped, outer vertices snapped to the convex outline) + soil skirt.</summary>
        private static void BuildIsland(Comp comp, Material grass, Material soil)
        {
            var temp = new List<MeshCollider>();
            foreach (var w in comp.Water)
                foreach (var mf in w.GetComponentsInChildren<MeshFilter>())
                {
                    var mc = mf.gameObject.AddComponent<MeshCollider>();
                    mc.sharedMesh = mf.sharedMesh;
                    temp.Add(mc);
                }
            Physics.SyncTransforms();

            var outline = comp.Island;
            float minX = outline.Min(p => p.x), maxX = outline.Max(p => p.x), minZ = outline.Min(p => p.y), maxZ = outline.Max(p => p.y);
            var nx = Mathf.CeilToInt((maxX - minX) / IslandStep);
            var nz = Mathf.CeilToInt((maxZ - minZ) / IslandStep);
            var inside = new bool[nx + 1, nz + 1];
            var wet = new bool[nx + 1, nz + 1];
            var pos = new Vector2[nx + 1, nz + 1];
            for (var i = 0; i <= nx; i++)
                for (var j = 0; j <= nz; j++)
                {
                    var p = new Vector2(minX + i * IslandStep, minZ + j * IslandStep);
                    inside[i, j] = Inside(outline, p, 0);
                    pos[i, j] = inside[i, j] ? p : Nearest(outline, p);
                    wet[i, j] = IsWater(comp.Root.TransformPoint(new Vector3(p.x, 0, p.y)), temp);
                }
            foreach (var mc in temp) Object.DestroyImmediate(mc);

            var verts = new List<Vector3>();
            var tris = new List<int>();
            for (var i = 0; i < nx; i++)
                for (var j = 0; j < nz; j++)
                {
                    if (!(inside[i, j] || inside[i + 1, j] || inside[i, j + 1] || inside[i + 1, j + 1])) continue;
                    if (wet[i, j] || wet[i + 1, j] || wet[i, j + 1] || wet[i + 1, j + 1]) continue;
                    var k = verts.Count;
                    verts.Add(V(pos[i, j], 0)); verts.Add(V(pos[i, j + 1], 0)); verts.Add(V(pos[i + 1, j + 1], 0)); verts.Add(V(pos[i + 1, j], 0));
                    tris.AddRange(new[] { k, k + 1, k + 2, k, k + 2, k + 3 }); // clockwise seen from above
                }
            var mesh = new Mesh { name = "IslandTop", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, verts.Select(v => new Vector2(v.x, v.z) / GrassTile).ToList());
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            var top = new GameObject("IslandTop");
            top.transform.SetParent(comp.Root, false);
            top.AddComponent<MeshFilter>().sharedMesh = mesh;
            top.AddComponent<MeshRenderer>().sharedMaterial = grass;

            MakePrism(comp.Root, "IslandSkirt", outline, -0.01f, -comp.Skirt, soil, soil, capTop: false); // a cap would hide the water
        }

        private static bool IsWater(Vector3 world, List<MeshCollider> water)
        {
            foreach (var hit in Physics.RaycastAll(world + Vector3.up * 5, Vector3.down, 10f))
            {
                var mc = hit.collider as MeshCollider;
                if (mc == null || !water.Contains(mc)) continue;
                var mesh = mc.sharedMesh;
                for (var s = 0; s < mesh.subMeshCount; s++)
                {
                    var sm = mesh.GetSubMesh(s);
                    if (hit.triangleIndex >= sm.indexStart / 3 && hit.triangleIndex < (sm.indexStart + sm.indexCount) / 3
                        && mc.GetComponent<Renderer>().sharedMaterials[s].name.Contains("Water"))
                        return true;
                }
            }
            return false;
        }

        private static Vector2 Nearest(Vector2[] poly, Vector2 p)
        {
            var best = poly[0];
            var bestD = float.MaxValue;
            for (var i = 0; i < poly.Length; i++)
            {
                var a = poly[i];
                var b = poly[(i + 1) % poly.Length];
                var ab = b - a;
                var q = a + ab * Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude);
                var d = (q - p).sqrMagnitude;
                if (d < bestD) { bestD = d; best = q; }
            }
            return best;
        }

        /// <summary>Faceted low-poly grass: seamless Voronoi patches in a few close greens. Regenerated on every build.</summary>
        private static Texture2D LoadOrCreateGrassTexture()
        {
            const string path = "Assets/FarmNature/Demo/Textures/T_Demo_Grass.png";
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            const int size = 256;
            var rnd = new System.Random(7);
            var seeds = Enumerable.Range(0, 70).Select(_ => new Vector2((float)rnd.NextDouble() * size, (float)rnd.NextDouble() * size)).ToArray();
            var tones = new[]
            {
                // matched to the bank greens of the Shore atlas, so stream/pond tiles do not show lighter halos
                new Color(0.51f, 0.72f, 0.23f), new Color(0.55f, 0.76f, 0.25f), new Color(0.49f, 0.70f, 0.22f),
                new Color(0.57f, 0.77f, 0.26f), new Color(0.53f, 0.74f, 0.24f),
            };
            var seedTone = seeds.Select(_ => tones[rnd.Next(tones.Length)]).ToArray();
            var tex = new Texture2D(size, size, TextureFormat.RGB24, false);
            for (var y = 0; y < size; y++)
                for (var x = 0; x < size; x++)
                {
                    var best = 0;
                    var bestD = float.MaxValue;
                    for (var s = 0; s < seeds.Length; s++)
                    {
                        var dx = Mathf.Abs(x - seeds[s].x); dx = Mathf.Min(dx, size - dx);
                        var dy = Mathf.Abs(y - seeds[s].y); dy = Mathf.Min(dy, size - dy);
                        var d = dx * dx + dy * dy;
                        if (d < bestD) { bestD = d; best = s; }
                    }
                    tex.SetPixel(x, y, seedTone[best]);
                }
            File.WriteAllBytes(path, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }


        // ---------- shots ----------

        private static Camera CreateShot(Comp comp, float yaw, float size, float pitch, Vector3 look)
        {
            var go = new GameObject("Shot_" + comp.Name);
            go.transform.SetParent(comp.Root, false);
            go.transform.localRotation = Quaternion.Euler(pitch, yaw, 0);
            go.transform.localPosition = look - go.transform.forward * 40f; // within the 50 m URP shadow distance
            var cam = go.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = size;
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 120;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.96f, 0.92f, 0.84f);
            cam.enabled = false;
            return cam;
        }

        /// <summary>Transparent masters for Icon / Card / Cover / Social (composited by compose_main.py).</summary>
        [MenuItem("Tools/Farm Nature/Render Main Images Parts")]
        public static void RenderMainParts()
        {
            const string dir = "AssetStore/FarmNature/Draft/_main";
            Directory.CreateDirectory(dir);
            var root = GameObject.Find(RootName).transform;
            RenderFitted(root.Find("Comp_Overall"), 0, 38, 4800, 2700, $"{dir}/Overall_alpha.png", 0.01f, true);
            RenderFitted(root.Find("Comp_Icon"), 30, 28, 2048, 2048, $"{dir}/Icon_alpha.png", 0.02f, true);
            Debug.Log("[FarmNature] main image parts -> " + dir);
        }

        [MenuItem("Tools/Farm Nature/Render Hero 02 Showcase Parts")]
        public static void RenderHero02()
        {
            const string dir = "AssetStore/FarmNature/Draft/_parts02";
            Directory.CreateDirectory(dir);
            foreach (Transform island in GameObject.Find("FarmNature_Showcase").transform)
                RenderFitted(island, 0, 45, 1208, 836, $"{dir}/{island.name}.png");
            Debug.Log("[FarmNature] showcase parts -> " + dir);
        }

        [MenuItem("Tools/Farm Nature/Render Hero 03 Local Parts")]
        public static void RenderHero03()
        {
            const string dir = "AssetStore/FarmNature/Draft/_parts03";
            Directory.CreateDirectory(dir);
            var root = GameObject.Find(RootName).transform;
            foreach (var name in new[] { "Ogorod", "Pole", "Sad", "Prud", "Opushka", "Tropa" })
                RenderFitted(root.Find("Comp_" + name), 45, 40, 1208, 836, $"{dir}/{name}.png");
            Debug.Log("[FarmNature] local parts -> " + dir);
        }

        /// <summary>
        /// Ortho shot fitted to every renderer under target; also writes &lt;png&gt;.json with viewport anchors of the
        /// numbered children ("01_Name"): front-bottom centre and left-middle, for the sheet composer.
        /// </summary>
        private static void RenderFitted(Transform target, float yaw, float pitch, int width, int height, string png, float margin = 0.03f, bool transparent = false)
        {
            var go = new GameObject("TempShot");
            var cam = go.AddComponent<Camera>();
            cam.enabled = false;
            cam.orthographic = true;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.96f, 0.92f, 0.84f, transparent ? 0f : 1f);
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 200;
            cam.aspect = width / (float)height;
            cam.transform.rotation = Quaternion.Euler(pitch, yaw, 0);

            var filters = target.GetComponentsInChildren<MeshFilter>().Where(f => f.GetComponent<Renderer>().enabled).ToArray();
            var all = filters[0].GetComponent<Renderer>().bounds;
            foreach (var f in filters) all.Encapsulate(f.GetComponent<Renderer>().bounds);
            cam.transform.position = all.center - cam.transform.forward * 30f; // inside the 60 m hero shadow distance
            // fit to the actual vertices (bounding boxes leave a lot of empty frame at 45 degrees)
            float minX = float.MaxValue, maxX = float.MinValue, minY = float.MaxValue, maxY = float.MinValue;
            var toCam = cam.transform.worldToLocalMatrix;
            foreach (var f in filters)
            {
                var m = toCam * f.transform.localToWorldMatrix;
                foreach (var v in f.sharedMesh.vertices)
                {
                    var l = m.MultiplyPoint3x4(v);
                    minX = Mathf.Min(minX, l.x); maxX = Mathf.Max(maxX, l.x);
                    minY = Mathf.Min(minY, l.y); maxY = Mathf.Max(maxY, l.y);
                }
            }
            cam.transform.position += cam.transform.right * ((minX + maxX) / 2) + cam.transform.up * ((minY + maxY) / 2);
            cam.orthographicSize = Mathf.Max((maxY - minY) / 2, (maxX - minX) / 2 / cam.aspect) * (1 + margin);

            // only the target is visible: hide the other islands/compositions (lights stay on)
            var hidden = new List<GameObject>();
            foreach (var rootGo in target.gameObject.scene.GetRootGameObjects())
                if (rootGo.name.StartsWith("FarmNature_") && rootGo.activeSelf) { rootGo.SetActive(false); hidden.Add(rootGo); }
            var chain = new List<GameObject>();
            for (var t = target; t != null; t = t.parent)
            {
                if (!t.gameObject.activeSelf) { t.gameObject.SetActive(true); chain.Add(t.gameObject); }
                if (t.parent == null) break;
                foreach (Transform sibling in t.parent)
                    if (sibling != t && sibling.gameObject.activeSelf) { sibling.gameObject.SetActive(false); hidden.Add(sibling.gameObject); }
            }
            try
            {
                Render(cam, png, width, height);
                WriteAnchors(cam, target, Path.ChangeExtension(png, ".json"));
            }
            finally
            {
                foreach (var h in hidden) h.SetActive(true);
                foreach (var c in chain) if (c.transform.parent == null) c.SetActive(true);
                Object.DestroyImmediate(go);
            }
        }

        private static void WriteAnchors(Camera cam, Transform target, string path)
        {
            var lines = new List<string>();
            foreach (Transform child in target)
            {
                var m = System.Text.RegularExpressions.Regex.Match(child.name, @"^(\d\d)_(.+)$");
                if (!m.Success) continue;
                var rs = child.GetComponentsInChildren<Renderer>();
                var b = rs[0].bounds;
                foreach (var r in rs) b.Encapsulate(r.bounds);
                // tall items (trees, corn): tag at the pivot (trunk base); low/flat items: at the front edge
                var front = cam.WorldToViewportPoint(b.size.y > 1.5f ? child.position : new Vector3(b.center.x, b.min.y, b.min.z));
                var left = cam.WorldToViewportPoint(new Vector3(b.min.x, b.min.y, b.center.z));
                string I(float v) => v.ToString("F4", CultureInfo.InvariantCulture);
                lines.Add($"{{\"num\":{int.Parse(m.Groups[1].Value)},\"name\":\"{m.Groups[2].Value}\",\"fx\":{I(front.x)},\"fy\":{I(front.y)},\"lx\":{I(left.x)},\"ly\":{I(left.y)}}}");
            }
            File.WriteAllText(path, "[\n" + string.Join(",\n", lines) + "\n]\n");
        }

        [MenuItem("Tools/Farm Nature/Render Hero 01 Overall")]
        public static void RenderHero()
        {
            var cam = GameObject.Find(RootName).transform.Find("Comp_Overall/Shot_Overall").GetComponent<Camera>();
            const string dir = "AssetStore/FarmNature/Draft";
            Directory.CreateDirectory(dir);
            Render(cam, $"{dir}/01_Overall_Composition_3840.png", 3840, 2160);
            Render(cam, $"{dir}/01_Overall_Composition.png", 1920, 1080, 2);
            Debug.Log("[FarmNature] hero render -> " + dir);
        }

        internal static void RenderShot(Camera cam, string path, int width, int height, int supersample) => Render(cam, path, width, height, supersample);

        private static void Render(Camera cam, string path, int width = 1600, int height = 900, int supersample = 1)
        {
            // hero quality for this render only; the project's URP asset is restored afterwards
            var urp = (UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset)UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline;
            var oldRes = urp.mainLightShadowmapResolution;
            var oldDist = urp.shadowDistance;
            urp.mainLightShadowmapResolution = 4096;
            urp.shadowDistance = 120;
            try { RenderTo(cam, path, width, height, supersample); }
            finally
            {
                urp.mainLightShadowmapResolution = oldRes;
                urp.shadowDistance = oldDist;
            }
        }

        private static void RenderTo(Camera cam, string path, int width, int height, int supersample)
        {
            var rt = new RenderTexture(width * supersample, height * supersample, 24) { antiAliasing = 8 };
            cam.targetTexture = rt;
            cam.aspect = width / (float)height;
            cam.Render();
            var final = rt;
            if (supersample > 1)
            {
                final = new RenderTexture(width, height, 0);
                Graphics.Blit(rt, final); // bilinear 2:1 = box filter
            }
            RenderTexture.active = final;
            // a clear colour with alpha 0 means "transparent background" (store media are composited later)
            var tex = new Texture2D(width, height, cam.backgroundColor.a < 1 ? TextureFormat.RGBA32 : TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            if (final != rt) { RenderTexture.active = null; Object.DestroyImmediate(final); }
            File.WriteAllBytes(path, tex.EncodeToPNG());
            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
        }

        private static Material LoadOrCreateMaterial(string name, Color color)
        {
            Directory.CreateDirectory(MaterialDir);
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_BaseColor", color);
            mat.SetFloat("_Smoothness", 0.05f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
