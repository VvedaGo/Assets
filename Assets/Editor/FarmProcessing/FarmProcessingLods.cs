using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace FarmProcessing.Editor
{
    /// <summary>(Not used for the release: Unity Mesh LOD smears the flat-colour atlas; LOD1 comes from _common/make_lod1.py.) Enables Unity 6 Mesh LOD generation on the 12 station models (STA) and reports LOD0/LOD1 triangles per model.</summary>
    public static class FarmProcessingLods
    {
        private const string StationDir = "Assets/FarmProcessing/Art/Models/STA";

        [MenuItem("Tools/Farm Processing/Generate Station LODs")]
        public static string Generate()
        {
            var report = new StringBuilder("[FarmProcessing] Station Mesh LODs\n");
            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { StationDir }).OrderBy(AssetDatabase.GUIDToAssetPath))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                if (!importer.generateMeshLods)
                {
                    importer.generateMeshLods = true;
                    importer.SaveAndReimport();
                }
                int lod0 = 0, lod1 = 0, lods = int.MaxValue;
                foreach (var mesh in AssetDatabase.LoadAllAssetsAtPath(path).OfType<Mesh>())
                {
                    lods = Mathf.Min(lods, mesh.lodCount);
                    for (var s = 0; s < mesh.subMeshCount; s++)
                    {
                        lod0 += (int)mesh.GetLod(s, 0).indexCount / 3;
                        lod1 += (int)mesh.GetLod(s, Mathf.Min(1, mesh.lodCount - 1)).indexCount / 3;
                    }
                }
                report.AppendLine($"{System.IO.Path.GetFileNameWithoutExtension(path)}  LOD0 {lod0}  LOD1 {lod1}  ({100f * lod1 / Mathf.Max(1, lod0):F0}%)  levels {lods}");
            }
            Debug.Log(report.ToString());
            return report.ToString();
        }

        /// <summary>Renders the station catalog shot with every station forced to the given Mesh LOD (visual check of LOD1).</summary>
        public static string RenderStationsAtLod(int lod)
        {
            UnityEditor.SceneManagement.EditorSceneManager.OpenScene("Assets/FarmProcessing/Demo/Scenes/Demo_Catalog.unity");
            var comp = GameObject.Find("Catalog_STA");
            foreach (var g in comp.GetComponentsInChildren<LODGroup>()) g.ForceLOD(lod);
            var cam = GameObject.Find("Cam_STA").GetComponent<Camera>();
            var path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "FarmProcessing_scene", $"Stations_LOD{lod}.png");
            FarmProcessingSceneBuilder.Render(cam, path, 1920, 1080, 2);
            foreach (var g in comp.GetComponentsInChildren<LODGroup>()) g.ForceLOD(-1);
            return path;
        }
    }
}
