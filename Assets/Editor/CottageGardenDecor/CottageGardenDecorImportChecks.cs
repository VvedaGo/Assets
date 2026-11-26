using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace CottageGardenDecor.Editor
{
    /// <summary>Read-only dump of the built prefabs (transforms, renderers, materials, LODGroups, colliders) for the import report.</summary>
    public static class CottageGardenDecorImportChecks
    {
        public const string DumpPath = "Temp/CottageGardenDecor_PrefabChecks.txt";   // Unity Temp/: scratch, not part of the pack;

        [MenuItem("Tools/Cottage Garden Decor/Dump Prefab Checks")]
        public static string Dump()
        {
            var sb = new StringBuilder();
            var prefabDir = CottageGardenDecorPackBuilder.Config.PrefabDir;
            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { prefabDir }).OrderBy(AssetDatabase.GUIDToAssetPath))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var t = go.transform;
                sb.AppendLine($"# {path.Substring(prefabDir.Length + 1)}  pos {V(t.localPosition)} rot {V(t.localEulerAngles)} scale {V(t.localScale)}");
                foreach (var tr in go.GetComponentsInChildren<Transform>(true).Skip(1))
                {
                    var line = $"  node {Path(tr, t)}  lpos {V(tr.localPosition)} lrot {V(tr.localEulerAngles)} lscale {V(tr.localScale)}";
                    var mf = tr.GetComponent<MeshFilter>();
                    var mr = tr.GetComponent<MeshRenderer>();
                    if (mf != null && mf.sharedMesh != null)
                    {
                        var verts = mf.sharedMesh.vertices.Select(v => tr.localToWorldMatrix.MultiplyPoint3x4(v)).ToArray();
                        var min = new Vector3(verts.Min(v => v.x), verts.Min(v => v.y), verts.Min(v => v.z));
                        var max = new Vector3(verts.Max(v => v.x), verts.Max(v => v.y), verts.Max(v => v.z));
                        var mats = mr != null ? string.Join("|", mr.sharedMaterials.Select(m => m == null ? "NULL" : m.name + "/" + m.shader.name + "/" + (m.GetTexture("_BaseMap") ? m.GetTexture("_BaseMap").name : "notex"))) : "no renderer";
                        line += $"  tris {mf.sharedMesh.triangles.Length / 3} min {V(min)} max {V(max)} mats {mats}";
                    }
                    sb.AppendLine(line);
                }
                var lg = go.GetComponent<LODGroup>();
                if (lg != null)
                {
                    var lods = lg.GetLODs();
                    for (var i = 0; i < lods.Length; i++)
                        sb.AppendLine($"  LOD{i} h {lods[i].screenRelativeTransitionHeight:F3}: " + string.Join(", ", lods[i].renderers.Select(r => r == null ? "NULL" : Path(r.transform, t))));
                }
                foreach (var c in go.GetComponentsInChildren<Collider>(true))
                {
                    var bc = c as BoxCollider;
                    sb.AppendLine(bc != null ? $"  collider Box on {c.name} center {V(bc.center)} size {V(bc.size)}" : $"  collider {c.GetType().Name} on {c.name}");
                }
            }
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(DumpPath));
            File.WriteAllText(DumpPath, sb.ToString());
            return "dumped " + sb.Length;
        }

        private static string V(Vector3 v) => $"({v.x:F3},{v.y:F3},{v.z:F3})".Replace("-0.000", "0.000");
        private static string Path(Transform tr, Transform root) => tr == root ? "" : (tr.parent == root ? tr.name : Path(tr.parent, root) + "/" + tr.name);
    }
}
