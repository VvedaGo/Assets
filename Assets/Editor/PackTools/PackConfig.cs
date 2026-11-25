using System.Collections.Generic;
using UnityEngine;

namespace PackTools.Editor
{
    /// <summary>
    /// Per-pack settings for the shared pack tools (PackPrefabBuilder, PackSceneBuilder). A pack keeps a tiny wrapper with
    /// its menu items and one PackConfig (see Tools/README.md). Folder layout under Root:
    ///   Art/Models/&lt;Category&gt;/*.fbx, Art/Textures/*.png, Art/Materials, Art/Prefabs/&lt;Category&gt;, Demo/Scenes, Documentation.
    /// </summary>
    public sealed class PackConfig
    {
        /// <summary>Pack root, e.g. "Assets/FarmProcessing".</summary>
        public string Root;
        /// <summary>Short tag for logs, e.g. "FarmProcessing".</summary>
        public string Tag;
        /// <summary>Regex that finds the atlas name inside an FBX, e.g. T_FarmProcessing_[A-Za-z0-9]+_BaseColor.</summary>
        public string TextureRegex;
        /// <summary>Prefab/asset name prefix in front of the ID with '_' (STA-05 -> FMS_Workshop_STA_05).</summary>
        public string Prefix = "FMS_";
        /// <summary>Folder with the scene layout text files.</summary>
        public string LayoutDir;
        /// <summary>Optional ID -> prefab file name without ".prefab", for packs whose prefabs are named after the FBX
        /// (TRC-01 -> FMS_Mach_Tractor_Cab); IDs not listed (or no map) use Prefix + ID.</summary>
        public Dictionary<string, string> PrefabNames;
        /// <summary>Floor fill codes for the 'floor' layout directive (code -> item ID).</summary>
        public Dictionary<string, string> FloorTiles = new Dictionary<string, string>();
        /// <summary>Folder under %TEMP% where scene shots are rendered.</summary>
        public string RenderTempDir = "pack_scene";
        public Color Backdrop = new Color32(0x17, 0x3C, 0x45, 0xFF);
        /// <summary>LODGroup screen heights: LOD0 down to this, LOD1 down to CullHeight.</summary>
        public float Lod0Height = 0.25f, CullHeight = 0.015f;
        public float Smoothness = 0.15f;

        public string ModelDir => Root + "/Art/Models";
        public string MaterialDir => Root + "/Art/Materials";
        public string TextureDir => Root + "/Art/Textures";
        public string PrefabDir => Root + "/Art/Prefabs";
        public string DemoDir => Root + "/Demo";
        public string ReportPath => ".work/ImportReport_" + Tag + ".txt";   // outside Assets: the Asset Store validator takes any .txt under the pack for documentation

        /// <summary>Prefab path of a catalogue ID: category = the part before the first '-' (STA-05 -> Art/Prefabs/STA/...);
        /// file name from PrefabNames when the ID is listed there.</summary>
        public string PrefabPath(string id)
        {
            var dash = id.IndexOf('-');
            var category = dash > 0 ? id.Substring(0, dash) : id;
            if (PrefabNames != null && PrefabNames.TryGetValue(id, out var name)) return $"{PrefabDir}/{category}/{name}.prefab";
            return $"{PrefabDir}/{category}/{Prefix}{id.Replace('-', '_')}.prefab";
        }
    }
}
