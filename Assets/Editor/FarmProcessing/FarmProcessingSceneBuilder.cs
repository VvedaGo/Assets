using PackTools.Editor;
using UnityEditor;
using UnityEngine;

namespace FarmProcessing.Editor
{
    /// <summary>Farm Processing demo scenes, built by the shared PackSceneBuilder from the text layouts next to this file.</summary>
    public static class FarmProcessingSceneBuilder
    {
        private static PackConfig C => FarmProcessingPackBuilder.Config;

        [MenuItem("Tools/Farm Processing/Build Courtyard Scene")]
        public static string BuildCourtyard() => PackSceneBuilder.Build(C, "FarmProcessingCourtyard.txt", "Demo_WorkshopCourtyard");

        [MenuItem("Tools/Farm Processing/Build Media Scene")]
        public static string BuildMedia() => PackSceneBuilder.Build(C, "FarmProcessingMedia.txt", "Demo_Media", savePrefabs: false);

        [MenuItem("Tools/Farm Processing/Build Catalog Scene")]
        public static string BuildCatalog() => PackSceneBuilder.Build(C, "FarmProcessingCatalog.txt", "Demo_Catalog", savePrefabs: false);

        [MenuItem("Tools/Farm Processing/Build Compositions (CMP prefabs)")]
        public static string BuildCompositions() => PackSceneBuilder.Build(C, "FarmProcessingCompositions.txt", "Demo_Compositions");

        public static void Render(Camera cam, string path, int width, int height, int supersample) =>
            PackSceneBuilder.Render(cam, path, width, height, supersample);
    }
}
