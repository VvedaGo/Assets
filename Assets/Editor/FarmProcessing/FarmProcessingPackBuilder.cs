using System.Collections.Generic;
using PackTools.Editor;
using UnityEditor;

namespace FarmProcessing.Editor
{
    /// <summary>Farm Processing settings and menu for the shared PackTools (Assets/Editor/PackTools, Tools/README.md).</summary>
    public static class FarmProcessingPackBuilder
    {
        public static readonly PackConfig Config = new PackConfig
        {
            Root = "Assets/FarmProcessing",
            Tag = "FarmProcessing",
            TextureRegex = @"T_FarmProcessing_[A-Za-z0-9]+_BaseColor",
            Prefix = "FMS_Workshop_",
            LayoutDir = "Assets/Editor/FarmProcessing",
            RenderTempDir = "FarmProcessing_scene",
            FloorTiles = new Dictionary<string, string> { { "W", "MOD-01" }, { "S", "MOD-02" }, { "P", "MOD-02_Plain" } },
        };

        [MenuItem("Tools/Farm Processing/Build Prefabs")]
        public static string Build() => PackPrefabBuilder.Build(Config);
    }
}
