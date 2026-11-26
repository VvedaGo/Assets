using System.Collections.Generic;
using System.Linq;
using PackTools.Editor;
using UnityEditor;
using UnityEngine;

namespace AssetNew.Editor
{
    /// <summary>Cottage Garden Decor (AssetNew) settings and menu for the shared PackTools (Assets/Editor/PackTools, Tools/README.md).
    /// Prefabs carry catalogue names (FMS_Garden_&lt;Name&gt;[_&lt;Variant&gt;]); PrefabNames maps layout IDs to them.
    /// The pack ships without colliders (owner, 2026-11-26): Build() strips the BoxColliders PackPrefabBuilder adds.</summary>
    public static class AssetNewPackBuilder
    {
        public static readonly PackConfig Config = new PackConfig
        {
            Root = "Assets/AssetNew",
            Tag = "AssetNew",
            TextureRegex = @"FMS_Garden_Atlas[AF]",
            Prefix = "FMS_Garden_",
            LayoutDir = "planning/AssetNew/layouts",
            RenderTempDir = "AssetNew_scene",
            PrefabNames = new Dictionary<string, string>
            {
            { "FLB-01", "Bed_Straight" },
            { "FLB-01_Planted", "Bed_Straight_Planted" },
            { "FLB-02", "Bed_Corner" },
            { "FLB-02_Planted", "Bed_Corner_Planted" },
            { "FLB-03", "Bed_Round" },
            { "FLB-03_Planted", "Bed_Round_Planted" },
            { "FUR-01", "Swing" },
            { "FUR-02", "Hammock" },
            { "FUR-03", "Bistro_Table" },
            { "FUR-03_White", "Bistro_Table_White" },
            { "FUR-04", "Bistro_Chair" },
            { "FUR-04_White", "Bistro_Chair_White" },
            { "FUR-05", "Deck_Chair" },
            { "FUR-05_Blue", "Deck_Chair_Blue" },
            { "MOD-01", "Lattice_Panel" },
            { "MOD-02", "Lattice_Post" },
            { "MOD-03", "Wall_Stone" },
            { "MOD-04", "Wall_Pillar" },
            { "MOD-05", "Edging_Brick" },
            { "MOD-06", "Edging_Brick_Curve" },
            { "MOD-07", "Pond_Edge" },
            { "MOD-08", "Pond_Edge_Corner" },
            { "MOD-09", "Pond_Water" },
            { "ORN-01", "Sundial" },
            { "ORN-02", "Gnome" },
            { "ORN-02_Blue", "Gnome_Blue" },
            { "ORN-03", "Urn" },
            { "ORN-03_Planted", "Urn_Planted" },
            { "ORN-04", "Insect_Hotel" },
            { "ORN-05", "Shepherd_Hook" },
            { "ORN-05_Feeder", "Shepherd_Hook_Feeder" },
            { "PLT-01", "Rose_Bush" },
            { "PLT-01_Pink", "Rose_Bush_Pink" },
            { "PLT-01_White", "Rose_Bush_White" },
            { "PLT-02", "Rose_Climbing_Side" },
            { "PLT-02_Pink", "Rose_Climbing_Side_Pink" },
            { "PLT-03", "Rose_Climbing_Top" },
            { "PLT-03_Pink", "Rose_Climbing_Top_Pink" },
            { "PLT-04", "Ivy_Patch" },
            { "PLT-05", "Wisteria_Drape" },
            { "PLT-06", "Hollyhock" },
            { "PLT-06_White", "Hollyhock_White" },
            { "STR-01", "Arch_Wood" },
            { "STR-01_Gate", "Arch_Wood_Gate" },
            { "STR-01_White", "Arch_Wood_White" },
            { "STR-02", "Arch_Iron" },
            { "STR-03", "Arbor_Bench" },
            { "STR-04", "Pergola" },
            { "STR-05", "Pergola_Bay" },
            { "STR-06", "Gazebo" },
            { "STR-07", "Obelisk" },
            { "STR-07_White", "Obelisk_White" },
            { "TOP-01", "Topiary_Standard" },
            { "TOP-01_Rose", "Topiary_Standard_Rose" },
            { "TOP-02", "Topiary_Cone" },
            { "TOP-03", "Topiary_Spiral" },
            { "TOP-04", "Topiary_Tiered" },
            { "WTR-01", "Fountain_Tiered" },
            { "WTR-02", "Fountain_Wall" },
            { "WTR-03", "Birdbath" },
            },
        };

        [MenuItem("Tools/Cottage Garden Decor/Build Prefabs")]
        public static string Build()
        {
            var report = PackPrefabBuilder.Build(Config);
            return report + RemoveColliders();
        }

        /// <summary>Removes every Collider (root and children) from the pack prefabs; buyers add their own MeshCollider.</summary>
        public static string RemoveColliders()
        {
            var removed = 0;
            var prefabs = AssetDatabase.FindAssets("t:Prefab", new[] { Config.PrefabDir }).Select(AssetDatabase.GUIDToAssetPath).ToArray();
            foreach (var path in prefabs)
            {
                var root = PrefabUtility.LoadPrefabContents(path);
                var colliders = root.GetComponentsInChildren<Collider>(true);
                foreach (var c in colliders) Object.DestroyImmediate(c);
                if (colliders.Length > 0) PrefabUtility.SaveAsPrefabAsset(root, path);
                PrefabUtility.UnloadPrefabContents(root);
                removed += colliders.Length;
            }
            AssetDatabase.SaveAssets();
            var line = $"[{Config.Tag}] colliders removed: {removed} in {prefabs.Length} prefabs\n";
            Debug.Log(line);
            return line;
        }
    }
}
