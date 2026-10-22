using System.IO;
using UnityEditor;
using UnityEngine;

namespace MarketFarm.Editor
{
    /// <summary>Base → Variant: a material asset (with _BaseMap_ST) and a Prefab Variant per preset.</summary>
    public static class MarketVariantGenerator
    {
        private const string MaterialDir = "Assets/Art/MarketFarm/Materials/Variants";
        private const string PrefabDir = "Assets/Art/MarketFarm/Prefabs/Variants";

        [MenuItem("Tools/MarketFarm/Generate Variants (selected Set)")]
        public static void GenerateSelected()
        {
            var set = Selection.activeObject as MarketVariantSet;
            if (set == null)
            {
                Debug.LogError("[MarketFarm] Select a MarketVariantSet asset first");
                return;
            }
            Generate(set);
        }

        public static void Generate(MarketVariantSet set)
        {
            Directory.CreateDirectory(MaterialDir);
            Directory.CreateDirectory(PrefabDir);

            foreach (var preset in set.Presets)
            {
                var issues = MarketFarmRules.CheckPreset(preset.VariantName, preset.BaseMapST);
                if (issues.Count > 0)
                    throw new System.InvalidOperationException($"Preset '{preset.name}': {string.Join("; ", issues)}");

                var material = CreateMaterial(set, preset);
                CreatePrefabVariant(set, preset, material);
            }
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"[MarketFarm] {set.Family}: generated {set.Presets.Count} variants");
        }

        private static Material CreateMaterial(MarketVariantSet set, MarketVariantPreset preset)
        {
            var source = preset.MaterialOverride != null ? preset.MaterialOverride : set.SharedMaterial;
            var path = $"{MaterialDir}/{MarketFarmRules.VariantMaterialName(set.Family, preset.VariantName)}.mat";

            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(source);
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.CopyPropertiesFromMaterial(source);
            }

            var st = preset.BaseMapST;
            material.SetTextureScale("_BaseMap", new Vector2(st.x, st.y));
            material.SetTextureOffset("_BaseMap", new Vector2(st.z, st.w));
            EditorUtility.SetDirty(material);
            return material;
        }

        private static void CreatePrefabVariant(MarketVariantSet set, MarketVariantPreset preset, Material material)
        {
            var path = $"{PrefabDir}/{MarketFarmRules.VariantPrefabName(set.Family, preset.VariantName)}.prefab";

            // Re-generation edits the existing variant in place so its GUID (and scene references) survive.
            if (!File.Exists(path))
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(set.BasePrefab);
                PrefabUtility.SaveAsPrefabAsset(instance, path);
                Object.DestroyImmediate(instance);
            }

            var root = PrefabUtility.LoadPrefabContents(path);
            try
            {
                foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
                {
                    var shared = renderer.sharedMaterials;
                    for (var i = 0; i < shared.Length; i++) shared[i] = material;
                    renderer.sharedMaterials = shared;
                }
                PrefabUtility.SaveAsPrefabAsset(root, path);
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(root);
            }
        }
    }
}
