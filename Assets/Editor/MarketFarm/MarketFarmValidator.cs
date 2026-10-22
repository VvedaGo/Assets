using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace MarketFarm.Editor
{
    public static class MarketFarmValidator
    {
        private const string MeshRoot = "Assets/Art/MarketFarm";

        [MenuItem("Tools/MarketFarm/Validate Models")]
        public static void ValidateAll()
        {
            var guids = AssetDatabase.FindAssets("t:Model", new[] { MeshRoot });
            var failed = 0;
            foreach (var guid in guids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var issues = MarketFarmRules.Check(Measure(model));
                if (issues.Count == 0) continue;
                failed++;
                Debug.LogWarning($"[MarketFarm] {path}\n - {string.Join("\n - ", issues)}", model);
            }
            Debug.Log($"[MarketFarm] validated {guids.Length} models, {failed} with issues");
        }

        public static MarketModelStats Measure(GameObject root)
        {
            var filters = root.GetComponentsInChildren<MeshFilter>(true).Where(f => IsLod0(f.transform) && !IsCollision(f.transform)).ToArray();
            var renderers = root.GetComponentsInChildren<Renderer>(true).Where(r => IsLod0(r.transform) && !IsCollision(r.transform)).ToArray();

            var tris = 0;
            var uvMin = new Vector2(float.MaxValue, float.MaxValue);
            var uvMax = new Vector2(float.MinValue, float.MinValue);
            var uvs = new List<Vector2>();
            foreach (var f in filters)
            {
                var mesh = f.sharedMesh;
                for (var i = 0; i < mesh.subMeshCount; i++) tris += (int)mesh.GetIndexCount(i) / 3;
                mesh.GetUVs(0, uvs);
                foreach (var uv in uvs)
                {
                    uvMin = Vector2.Min(uvMin, uv);
                    uvMax = Vector2.Max(uvMax, uv);
                }
            }

            var minY = renderers.Min(r => r.bounds.min.y) - root.transform.position.y;
            var materials = renderers.SelectMany(r => r.sharedMaterials).Distinct().Count();
            return new MarketModelStats(root.name, tris, materials, minY, uvMin, uvMax,
                root.GetComponentInChildren<Collider>(true) != null || HasCollisionMesh(root),
                root.GetComponentInChildren<LODGroup>(true) != null || root.GetComponentsInChildren<Transform>(true).Any(t => t.name.EndsWith("_LOD1")));
        }

        // FBX ships collision as a *_Col child mesh; MarketSceneBuilder turns it into a MeshCollider on the base prefab.
        private static bool IsCollision(Transform t) => t.name.EndsWith("_Col");
        private static bool HasCollisionMesh(GameObject root) => root.GetComponentsInChildren<Transform>(true).Any(IsCollision);

        // LOD meshes are children named *_LOD1 / *_LOD2; everything else counts as LOD0.
        private static bool IsLod0(Transform t) => !t.name.EndsWith("_LOD1") && !t.name.EndsWith("_LOD2");
    }
}
