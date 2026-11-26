using PackTools.Editor;
using UnityEditor;

namespace AssetNew.Editor
{
    /// <summary>Cottage Garden Decor (AssetNew) settings and menu for the shared PackTools (Assets/Editor/PackTools, Tools/README.md).</summary>
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
        };

        [MenuItem("Tools/Cottage Garden Decor/Build Prefabs")]
        public static string Build() => PackPrefabBuilder.Build(Config);
    }
}
