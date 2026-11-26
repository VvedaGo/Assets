using System.Text;
using PackTools.Editor;
using UnityEditor;

namespace FarmMachinery.Editor
{
    /// <summary>Farm Machinery settings and menu for the shared PackTools (Assets/Editor/PackTools, Tools/README.md).</summary>
    public static class FarmMachineryPackBuilder
    {
        public static readonly PackConfig Config = new PackConfig
        {
            Root = FarmMachineryRelease.LiteRoot,   // working root: Full-only items are staged in for every build (FarmMachineryRelease.Staged)
            Tag = "FarmMachinery",
            TextureRegex = @"T_FarmMachinery_[A-Za-z0-9]+_BaseColor",
            Prefix = FarmMachineryCatalog.Prefix,
            PrefabNames = FarmMachineryCatalog.PrefabNames(),   // prefabs are named after the FBX, layouts use IDs (see FarmMachineryCatalog)
            LayoutDir = "planning/FarmMachinery/layouts",
            RenderTempDir = "farmmachinery_scene",
        };

        [MenuItem("Tools/Farm Machinery/Build Prefabs")]
        public static string Build() => FarmMachineryRelease.Staged(() => PackPrefabBuilder.Build(Config));

        /// <summary>Base prefabs (shared builder) → variants → compositions → checks. Variants and compositions depend on the bases,
        /// so rerun them after every Build Prefabs.</summary>
        [MenuItem("Tools/Farm Machinery/Build All")]
        public static string BuildAll() => FarmMachineryRelease.Staged(() => new StringBuilder()
            .AppendLine(Build())
            .AppendLine(FarmMachineryVariants.Build())
            .AppendLine(FarmMachineryCompositions.Build())
            .AppendLine(FarmMachineryChecks.Run())
            .ToString());
    }
}
