using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Catalogue / technical raw renders (Э10, REQUIREMENTS 7.4–7.5 frames 06, 08, 09, 11, 12, 13): clean item sheets on the
    /// #E9E9EC background, no text. Called by <see cref="FarmMachinerySceneBuilder.Build"/> for layouts
    /// planning/FarmMachinery/layouts/Catalog_*.txt; '#!' directives:
    ///   #! look catalog                          neutral white key from the front-left, soft contact shadows, flat grey ambient,
    ///                                            ground plane matched to the background; every LODGroup forced to LOD0
    ///   #! catrows rot gapX gapZ                 rotation (layout rot: 35 = 3/4 front-left) and gaps of the following rows
    ///   #! catgroup name                         start an independent group (groups stand 90 m apart; one shot per group)
    ///   #! catrow TOKEN TOKEN ...                one row, left to right, centred on x; rows are listed back to front and stacked
    ///                                            by their real LOD0 bounds; '|' = a wider gap (pairs)
    ///   TOKEN = ID[@flag...][+parentPoint:ChildID:childPoint ...]   e.g. HRV-01+Feeder_Front:ATT-03:Feeder_Rear
    ///           flags: @wire (edge overlay), @lod1 (show LOD1), @box (BoxCollider outline), @gizmo (attach points), @rNNN (rotation)
    ///   #! fit shot group|* yaw pitch margin [bottomFree]   camera fitted to the real renderer bounds of the group
    /// Helper objects (gizmos, wires, outlines) exist only in the demo scene; prefabs are never modified.
    /// </summary>
    public static class FarmMachineryCatalogShots
    {
        public static readonly Color32 Background = new Color32(233, 233, 236, 255);
        /// <summary>Ground albedo that renders as the background colour under the catalogue light (calibrated on Catalog_06_Lite).</summary>
        public static Color GroundAlbedo = new Color(0.745f, 0.756f, 0.770f);

        private class Unit { public GameObject Go; public Bounds B; }

        public static string Apply(Transform root, string[] lines, Dictionary<string, (int W, int H)> shotSizes)
        {
            var log = new StringBuilder();
            var isCatalog = lines.Any(l => l.Trim().StartsWith("#! look catalog"));
            var hasRows = lines.Any(l => l.Trim().StartsWith("#! catrow "));
            if (!isCatalog && !hasRows) return "";
            if (isCatalog) log.AppendLine(Look(root));

            var catRoot = new GameObject("Catalog").transform;
            catRoot.SetParent(root, false);
            var groups = new List<(string Name, List<List<Unit>> Rows)>();
            float rot = 35, gapX = 1.0f, gapZ = 1.4f;
            var rowGaps = new List<(float GapX, float GapZ)>();
            var groupRowGaps = new Dictionary<string, List<(float, float)>>();
            var gridGroups = new HashSet<string>();   // '#! catgrid': columns aligned across rows (same cell per column)
            foreach (var raw in lines)
            {
                var t = raw.Trim().Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
                if (t.Length < 2 || t[0] != "#!") continue;
                if (t[1] == "catrows") { rot = F(t[2]); gapX = F(t[3]); gapZ = F(t[4]); }
                else if (t[1] == "catgroup") { groups.Add((t[2], new List<List<Unit>>())); groupRowGaps[t[2]] = new List<(float, float)>(); }
                else if (t[1] == "catgrid") gridGroups.Add(groups.Count > 0 ? groups[groups.Count - 1].Name : "main");
                else if (t[1] == "catrow")
                {
                    if (groups.Count == 0) { groups.Add(("main", new List<List<Unit>>())); groupRowGaps["main"] = new List<(float, float)>(); }
                    var row = new List<Unit>();
                    foreach (var tok in t.Skip(2))
                    {
                        if (tok == "|") { row.Add(null); continue; }
                        var u = BuildUnit(catRoot, tok, rot, log);
                        if (u != null) row.Add(u);
                    }
                    groups[groups.Count - 1].Rows.Add(row);
                    groupRowGaps[groups[groups.Count - 1].Name].Add((gapX, gapZ));
                }
            }

            // layout: rows back to front, the last row's centre at z 0, each earlier row behind the previous one
            for (var g = 0; g < groups.Count; g++)
            {
                var (name, rows) = groups[g];
                var gaps = groupRowGaps[name];
                var offsetX = (g - (groups.Count - 1) / 2f) * 90f;
                var zFront = 0f;
                // rows justified to the widest row of the group (even spacing, no ragged holes); the added gap is capped
                float RowTotal(List<Unit> rw, float g0) => rw.Sum(u => u == null ? g0 * 2.5f : u.B.size.x) + g0 * (rw.Count - 1);
                var widest = rows.Select((rw, i) => rw.Count(u => u != null) == 0 ? 0f : RowTotal(rw, gaps[i].Item1)).DefaultIfEmpty(0f).Max();
                // grid mode: column c is as wide as its widest unit; every unit sits centred in its cell
                var grid = gridGroups.Contains(name);
                var colW = new List<float>();
                if (grid)
                    foreach (var rw in rows)
                        for (var c = 0; c < rw.Count; c++)
                        {
                            while (colW.Count <= c) colW.Add(0f);
                            colW[c] = Mathf.Max(colW[c], rw[c] == null ? gaps[0].Item1 * 2.5f : rw[c].B.size.x);
                        }
                for (var r = rows.Count - 1; r >= 0; r--)
                {
                    var row = rows[r];
                    var (gx, gz) = gaps[r];
                    var units = row.Where(u => u != null).ToList();
                    if (units.Count == 0) continue;
                    var total = RowTotal(row, gx);
                    if (row.Count > 1)
                    {
                        var extra = Mathf.Min((widest - total) / (row.Count - 1), gx * JustifyCap);
                        gx += extra; total = RowTotal(row, gaps[r].Item1) + extra * (row.Count - 1);
                    }
                    var depth = units.Max(u => u.B.size.z);
                    var zc = zFront + depth / 2;
                    if (grid)
                    {
                        var gw = colW.Sum() + gaps[r].Item1 * (colW.Count - 1);
                        var cx = offsetX - gw / 2;
                        for (var c = 0; c < row.Count; c++)
                        {
                            var u = row[c];
                            if (u != null)
                            {
                                var d = new Vector3(cx + colW[c] / 2 - u.B.center.x, -u.B.min.y, zc - u.B.center.z);
                                u.Go.transform.position += d;
                                u.B.center += d;
                            }
                            cx += colW[c] + gaps[r].Item1;
                        }
                        zFront += depth + gz;
                        continue;
                    }
                    var x = offsetX - total / 2;
                    foreach (var u in row)
                    {
                        if (u == null) { x += gaps[r].Item1 * 2.5f + gx; continue; }
                        var d = new Vector3(x - u.B.min.x, -u.B.min.y, zc - u.B.center.z);
                        u.Go.transform.position += d;
                        u.B.center += d;
                        x += u.B.size.x + gx;
                    }
                    zFront += depth + gz;
                }
                log.AppendLine($"catalog group {name}: {rows.Count} rows, {rows.Sum(rr => rr.Count(u => u != null))} units at x {offsetX}");
            }

            foreach (var raw in lines)
            {
                var t = raw.Trim().Split((char[])null, System.StringSplitOptions.RemoveEmptyEntries);
                if (t.Length < 2 || t[0] != "#!") continue;
                if (t[1] == "focus") { log.AppendLine(Focus(root, groups.Where(gr => gr.Name == t[3] || t[3] == "*").SelectMany(gr => gr.Rows).SelectMany(rr => rr).Where(u => u != null).ToList(), t)); continue; }
                if (t[1] != "fit") continue;
                var shot = t[2];
                var cam = root.Find("Cam_" + shot)?.GetComponent<Camera>();
                if (cam == null) { log.AppendLine($"! fit: no camera {shot}"); continue; }
                var targets = t[3] == "*" ? groups.SelectMany(gr => gr.Rows) : groups.Where(gr => gr.Name == t[3]).SelectMany(gr => gr.Rows);
                var pts = new List<Vector3>();
                foreach (var u in targets.SelectMany(rr => rr).Where(u => u != null))
                    foreach (var r in u.Go.GetComponentsInChildren<Renderer>())
                        if (r.enabled && r.gameObject.activeInHierarchy) pts.AddRange(Corners(r.bounds));
                var size = shotSizes.TryGetValue(shot, out var s) ? s : (1920, 1080);
                var aspect = size.Item1 / (float)size.Item2;
                var margin = F(t[6]); var bottom = t.Length > 7 ? F(t[7]) : 0f;
                var pitch = 0f;
                if (t[5] == "auto")   // largest items: the pitch (26..34 deg) with the shortest fitted distance, one pitch per sheet
                {
                    var best = float.MaxValue;
                    for (var pc = 26f; pc <= 34f; pc += 2f)
                    {
                        Fit(cam, pts, F(t[4]), pc, margin, bottom, aspect, shot, out var dd);
                        if (dd < best - 0.01f) { best = dd; pitch = pc; }
                    }
                }
                else pitch = F(t[5]);
                log.AppendLine(Fit(cam, pts, F(t[4]), pitch, margin, bottom, aspect, shot, out _));
            }
            return log.ToString();
        }

        /// <summary>'#! focus shot group part radius yaw pitch [dx dy dz]': close-up camera on a named transform (attach point / part)
        /// of the group, distance chosen so a sphere of the radius fills the frame.</summary>
        private static string Focus(Transform root, List<Unit> units, string[] t)
        {
            var cam = root.Find("Cam_" + t[2])?.GetComponent<Camera>();
            var part = units.SelectMany(u => u.Go.GetComponentsInChildren<Transform>(true)).FirstOrDefault(x => x.name == t[4]);
            if (cam == null || part == null) return $"! focus {t[2]}: camera or part {t[4]} missing";
            float radius = F(t[5]), yaw = F(t[6]) * Mathf.Deg2Rad, pitch = F(t[7]) * Mathf.Deg2Rad;
            var target = part.position + (t.Length > 10 ? new Vector3(F(t[8]), F(t[9]), F(t[10])) : Vector3.zero);
            var f = new Vector3(Mathf.Cos(pitch) * Mathf.Sin(yaw), -Mathf.Sin(pitch), Mathf.Cos(pitch) * Mathf.Cos(yaw));
            var dist = radius / Mathf.Tan(cam.fieldOfView * Mathf.Deg2Rad / 2);
            cam.transform.position = target - f * dist;
            cam.transform.rotation = Quaternion.LookRotation(f);
            cam.nearClipPlane = 0.1f;
            return $"focus {t[2]}: {t[4]} at {target}, dist {dist:F1}";
        }

        /// <summary>One throw-away render: renderers enabled / disabled in the same editor call are drawn only from the second Render.</summary>
        public static void WarmUp(Camera cam)
        {
            var rt = RenderTexture.GetTemporary(64, 64, 24);
            var old = cam.targetTexture;
            cam.targetTexture = rt; cam.Render(); cam.targetTexture = old;
            RenderTexture.ReleaseTemporary(rt);
        }

        private static Unit BuildUnit(Transform parent, string token, float rot, StringBuilder log)
        {
            var parts = token.Split('+');
            var head = parts[0].Split('@');
            var id = head[0];
            var flags = head.Skip(1).ToList();
            var r = flags.FirstOrDefault(f => f.StartsWith("r") && f.Length > 1 && char.IsDigit(f[1]));
            if (r != null) rot = F(r.Substring(1));
            var unit = new GameObject("Unit_" + token).transform;
            unit.SetParent(parent, false);
            var go = Instantiate(id, unit, log);
            if (go == null) { Object.DestroyImmediate(unit.gameObject); return null; }
            go.transform.localRotation = Quaternion.Euler(0, rot + 180, 0);
            ForceLod(go, flags.Contains("lod1") ? 1 : 0);
            foreach (var a in parts.Skip(1))
            {
                var p = a.Split(':');
                var child = Instantiate(p[1], unit, log);
                if (child == null) continue;
                ForceLod(child, 0);
                var err = FarmMachineryCatalog.Attach(FarmMachineryCatalog.Require(go, p[0]), child, p[2]);
                log.AppendLine($"  {id}.{p[0]} <- {p[1]}.{p[2]}: {err * 1000:F1} mm");
            }
            if (flags.Contains("wire")) Wire(go);
            if (flags.Contains("box")) BoxOutline(go);
            if (flags.Contains("gizmo")) log.AppendLine(Gizmos(go, id));
            return new Unit { Go = unit.gameObject, B = RendererBounds(unit.gameObject) };
        }

        private static GameObject Instantiate(string id, Transform parent, StringBuilder log)
        {
            var path = FarmMachineryPackBuilder.Config.PrefabPath(id);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) { log.AppendLine("! missing prefab " + path); return null; }
            return (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
        }

        /// <summary>Shows one LOD level only (LODGroup off): catalogue renders at any distance stay on LOD0, @lod1 shows LOD1.</summary>
        private static void ForceLod(GameObject go, int level)
        {
            foreach (var g in go.GetComponentsInChildren<LODGroup>(true))
            {
                var lods = g.GetLODs();
                var show = Mathf.Min(level, lods.Length - 1);
                for (var i = 0; i < lods.Length; i++)
                    foreach (var r in lods[i].renderers)
                        if (r != null) r.enabled = i == show;
                g.enabled = false;
            }
        }

        private static Bounds RendererBounds(GameObject go)
        {
            var rs = go.GetComponentsInChildren<Renderer>().Where(r => r.enabled && r.gameObject.activeInHierarchy).ToList();
            var b = rs[0].bounds;
            foreach (var r in rs.Skip(1)) b.Encapsulate(r.bounds);
            return b;
        }

        private static IEnumerable<Vector3> Corners(Bounds b)
        {
            for (var i = 0; i < 8; i++)
                yield return new Vector3((i & 1) == 0 ? b.min.x : b.max.x, (i & 2) == 0 ? b.min.y : b.max.y, (i & 4) == 0 ? b.min.z : b.max.z);
        }

        /// <summary>scene_fit in C#: the camera looks along (yaw, pitch); distance and look point solved so every point fits the frame.</summary>
        private const float JustifyCap = 3f;

        private static string Fit(Camera cam, List<Vector3> pts, float yaw, float pitch, float margin, float bottom, float aspect, string shot, out float fitted)
        {
            float yr = yaw * Mathf.Deg2Rad, pr = pitch * Mathf.Deg2Rad;
            var f = new Vector3(Mathf.Cos(pr) * Mathf.Sin(yr), -Mathf.Sin(pr), Mathf.Cos(pr) * Mathf.Cos(yr));
            var right = new Vector3(Mathf.Cos(yr), 0, -Mathf.Sin(yr));
            var up = Vector3.Cross(f, right);
            var tv = Mathf.Tan(cam.fieldOfView * Mathf.Deg2Rad / 2); var th = tv * aspect;
            Vector2 Project(Vector3 pos, Vector3 p)
            {
                var d = p - pos; var zc = Vector3.Dot(d, f);
                return new Vector2(Vector3.Dot(d, right) / zc / th, Vector3.Dot(d, up) / zc / tv);
            }
            var target = pts.Aggregate(Vector3.zero, (a, p) => a + p) / pts.Count;
            float loX = -1 + 2 * margin, hiX = 1 - 2 * margin, loY = -1 + 2 * (bottom > 0 ? Mathf.Max(margin, bottom) : margin), hiY = 1 - 2 * margin;
            var dist = 10f; Vector3 pos = target;
            for (var it = 0; it < 80; it++)
            {
                float lo = 0.5f, hi = 600f;
                for (var k = 0; k < 50; k++)
                {
                    var dm = (lo + hi) / 2; var pp = target - f * dm;
                    var ok = pts.All(p => { var q = Project(pp, p); return Vector3.Dot(p - pp, f) > 0.3f && q.x >= loX && q.x <= hiX && q.y >= loY && q.y <= hiY; });
                    if (ok) hi = dm; else lo = dm;
                }
                dist = hi; pos = target - f * dist;
                var P = pts.Select(p => Project(pos, p)).ToList();
                var mx = (P.Min(q => q.x) + P.Max(q => q.x)) / 2 - (loX + hiX) / 2;
                var my = (P.Min(q => q.y) + P.Max(q => q.y)) / 2 - (loY + hiY) / 2;
                if (Mathf.Abs(mx) < 0.003f && Mathf.Abs(my) < 0.003f) break;
                target += (right * mx * th + up * my * tv) * dist * 0.5f;
            }
            fitted = dist;
            cam.transform.position = pos;
            cam.transform.rotation = Quaternion.LookRotation(f);
            cam.farClipPlane = Mathf.Max(200, dist * 3);
            var Q = pts.Select(p => Project(pos, p)).ToList();
            return $"fit {shot}: yaw {yaw} pitch {pitch} dist {dist:F1}, ndc x {Q.Min(q => q.x):F2}..{Q.Max(q => q.x):F2} y {Q.Min(q => q.y):F2}..{Q.Max(q => q.y):F2}";
        }

        // ---------------------------------------------------------------- look

        private static string Look(Transform root)
        {
            var key = root.Find("Key_Sun").GetComponent<Light>();
            key.color = new Color(1.0f, 0.97f, 0.93f);
            key.intensity = 1.55f;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = 0.55f;
            var fill = root.Find("Fill_Sky").GetComponent<Light>();
            fill.color = new Color(0.88f, 0.92f, 1.0f);
            fill.intensity = 0.45f;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.60f, 0.62f, 0.66f);
            RenderSettings.ambientEquatorColor = new Color(0.52f, 0.52f, 0.53f);
            RenderSettings.ambientGroundColor = new Color(0.40f, 0.40f, 0.41f);
            RenderSettings.fog = false;
            var ground = root.Find("Backdrop_Ground");
            if (ground != null)
            {
                ground.localScale = new Vector3(60, 1, 60);
                ground.localPosition = new Vector3(0, -0.002f, 0);
                var mat = ground.GetComponent<Renderer>().sharedMaterial;
                mat.SetColor("_BaseColor", GroundAlbedo);
                mat.SetFloat("_Smoothness", 0f);
                mat.SetFloat("_SpecularHighlights", 0f);
                mat.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
                EditorUtility.SetDirty(mat);
            }
            foreach (var cam in root.GetComponentsInChildren<Camera>()) cam.backgroundColor = Background;
            return $"look catalog: white key 1.55 (front-left), shadows 0.55, ground albedo {GroundAlbedo}, background #E9E9EC";
        }

        // ---------------------------------------------------------------- helpers (scene only)

        /// <summary>Wire thickness in metres: the 1-pixel line topology vanished after the 2x supersample, so edges are thin square tubes.</summary>
        private const float WireWidth = 0.02f;   // ~1.5-2 px at catalogue scale; light lines read on the red / dark fill

        private static void Tube(List<Vector3> verts, List<int> idx, Vector3 a, Vector3 b, float w)
        {
            var d = b - a;
            if (d.sqrMagnitude < 1e-8f) return;
            var u = Vector3.Cross(d, Mathf.Abs(d.normalized.y) < 0.9f ? Vector3.up : Vector3.right).normalized * (w / 2);
            var v = Vector3.Cross(d, u).normalized * (w / 2);
            var o = verts.Count;
            foreach (var p in new[] { a, b })
            {
                verts.Add(p + u + v); verts.Add(p - u + v); verts.Add(p - u - v); verts.Add(p + u - v);
            }
            for (var k = 0; k < 4; k++)
            {
                int k1 = (k + 1) % 4;
                idx.AddRange(new[] { o + k, o + 4 + k, o + 4 + k1, o + k, o + 4 + k1, o + k1 });
            }
        }

        private static Material Unlit(string name, Color c, bool onTop = false)
        {
            var mat = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = name };
            mat.SetColor("_BaseColor", c);
            mat.SetFloat("_Cull", 0f);
            if (onTop)
            {
                mat.SetFloat("_ZTest", (float)CompareFunction.Always);   // gizmos read through the model
                mat.renderQueue = 4000;
            }
            return mat;
        }

        /// <summary>Edge overlay of every shown mesh: a line mesh of the unique triangle edges, 4 mm out along the face normal.</summary>
        private static void Wire(GameObject go)
        {
            var mat = Unlit("M_Wire", new Color(0.93f, 0.93f, 0.90f));
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                var mr = mf.GetComponent<MeshRenderer>();
                if (mr == null || !mr.enabled || mf.sharedMesh == null) continue;
                var mesh = mf.sharedMesh;
                var v = mesh.vertices; var n = mesh.normals; var tri = mesh.triangles;
                var key = new Dictionary<(Vector3Int, Vector3Int), bool>();
                var verts = new List<Vector3>(); var idx = new List<int>();
                Vector3Int Q(Vector3 p) => new Vector3Int(Mathf.RoundToInt(p.x * 2000), Mathf.RoundToInt(p.y * 2000), Mathf.RoundToInt(p.z * 2000));
                for (var i = 0; i < tri.Length; i += 3)
                    for (var e = 0; e < 3; e++)
                    {
                        int a = tri[i + e], b = tri[i + (e + 1) % 3];
                        var qa = Q(v[a]); var qb = Q(v[b]);
                        var k = qa.x < qb.x || (qa.x == qb.x && (qa.y < qb.y || (qa.y == qb.y && qa.z <= qb.z))) ? (qa, qb) : (qb, qa);
                        if (key.ContainsKey(k)) continue;
                        key[k] = true;
                        var off = n.Length > 0 ? n[a] * 0.003f : Vector3.zero;
                        var offB = n.Length > 0 ? n[b] * 0.003f : Vector3.zero;
                        Tube(verts, idx, v[a] + off, v[b] + offB, WireWidth / Mathf.Max(0.001f, mf.transform.lossyScale.x));
                    }
                var lines = new Mesh { name = mesh.name + "_Wire", indexFormat = IndexFormat.UInt32 };
                lines.SetVertices(verts);
                lines.SetTriangles(idx, 0);
                lines.RecalculateBounds();
                var w = new GameObject(mf.name + "_Wire");
                w.transform.SetParent(mf.transform, false);
                w.AddComponent<MeshFilter>().sharedMesh = lines;
                var wr = w.AddComponent<MeshRenderer>();
                wr.sharedMaterial = mat;
                wr.shadowCastingMode = ShadowCastingMode.Off;
            }
        }

        /// <summary>BoxCollider outline: 12 thin unlit bars on the collider edges.</summary>
        private static void BoxOutline(GameObject go)
        {
            var mat = Unlit("M_ColliderOutline", new Color(0.10f, 0.75f, 0.30f));
            foreach (var bc in go.GetComponentsInChildren<BoxCollider>())
            {
                var c = new Vector3[8];
                for (var i = 0; i < 8; i++)
                {
                    var l = bc.center + Vector3.Scale(bc.size / 2, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    c[i] = bc.transform.TransformPoint(l);
                }
                foreach (var (a, b) in new[] { (0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7) })
                    Bar(go.transform, c[a], c[b], 0.035f, mat, "Collider_Edge");
            }
        }

        private static void Bar(Transform parent, Vector3 a, Vector3 b, float t, Material mat, string name)
        {
            var bar = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bar.name = name;
            Object.DestroyImmediate(bar.GetComponent<Collider>());
            bar.transform.SetParent(parent, true);
            bar.transform.position = (a + b) / 2;
            bar.transform.rotation = Quaternion.LookRotation(b - a);
            bar.transform.localScale = Vector3.one;
            var ls = bar.transform.lossyScale;
            bar.transform.localScale = new Vector3(t / ls.x, t / ls.y, (b - a).magnitude / ls.z);
            var r = bar.GetComponent<Renderer>();
            r.sharedMaterial = mat;
            r.shadowCastingMode = ShadowCastingMode.Off;
        }

        /// <summary>Attach-point gizmos: a sphere per point (colour by kind) and its local X/Y/Z axes (red/green/blue).</summary>
        private static string Gizmos(GameObject go, string id)
        {
            var baseId = id.Split('_')[0];
            var points = FarmMachineryCatalog.Item(baseId).Points.Where(p => p != "Seat").ToList();
            var axisMat = new[] { Unlit("M_Axis_X", new Color(0.9f, 0.15f, 0.15f), true), Unlit("M_Axis_Y", new Color(0.15f, 0.8f, 0.2f), true), Unlit("M_Axis_Z", new Color(0.15f, 0.35f, 0.95f), true) };
            var shown = new List<string>();
            foreach (var p in points)
            {
                var t = FarmMachineryCatalog.Find(go, p);
                if (t == null) continue;
                var col = p.StartsWith("Hitch") ? new Color(1.0f, 0.72f, 0.05f) : p.StartsWith("Link3P") ? new Color(0.05f, 0.75f, 1.0f)
                    : p.StartsWith("PTO") ? new Color(0.85f, 0.2f, 0.85f) : p.StartsWith("Feeder") ? new Color(0.2f, 0.85f, 0.3f) : new Color(0.55f, 0.35f, 0.95f);
                var s = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                s.name = "Gizmo_" + p;
                Object.DestroyImmediate(s.GetComponent<Collider>());
                s.transform.SetParent(go.transform, true);
                s.transform.position = t.position;
                s.transform.localScale = Vector3.one * 0.36f;
                var r = s.GetComponent<Renderer>();
                r.sharedMaterial = Unlit("M_Gizmo_" + p, col, true);
                r.shadowCastingMode = ShadowCastingMode.Off;
                var dirs = new[] { t.right, t.up, t.forward };
                for (var i = 0; i < 3; i++) Bar(go.transform, t.position, t.position + dirs[i] * 0.75f, 0.06f, axisMat[i], "Gizmo_Axis");
                shown.Add(p);
            }
            return $"  gizmos {id}: {string.Join(", ", shown)}";
        }

        private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);
    }
}
