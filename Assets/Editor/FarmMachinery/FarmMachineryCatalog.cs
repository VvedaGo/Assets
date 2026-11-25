using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FarmMachinery.Editor
{
    /// <summary>One catalogue row of planning/FarmMachinery/CATALOG.md as far as the Unity import needs it.</summary>
    public sealed class FarmMachineryItem
    {
        public string Id, Name;
        public int Budget;
        public bool Lod, Lite;
        public string[] Points, Parts;
        public string Category => Id.Substring(0, Id.IndexOf('-'));
    }

    /// <summary>
    /// Catalogue registry (CATALOG.md v0.1, 2026-11-24) and shared helpers of the Farm Machinery wrapper. Base prefabs are made by
    /// PackPrefabBuilder and named after the FBX: Art/Prefabs/&lt;CAT&gt;/FMS_Mach_&lt;Name&gt;.prefab.
    /// </summary>
    public static class FarmMachineryCatalog
    {
        // ID | Name | LOD0 budget | LOD | Lite | points (empties) | moving parts
        private const string Table = @"
TRC-01|Tractor_Cab|7000|1|1|Hitch_Rear,Link3P_Rear,PTO_Rear,Seat|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR,Linkage_Rear,Door_L
TRC-02|Tractor_Large|9000|1|1|Hitch_Rear,Link3P_Rear,Link3P_Front,PTO_Rear,Seat|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR,Linkage_Rear,Linkage_Front,Door_L
IMP-01|Plough|2500|1|1|Link3P_Front|Wheel_Gauge
IMP-02|Seeder|3500|1|1|Link3P_Front|Lid,Marker_L,Marker_R,Wheel_L,Wheel_R
IMP-03|Sprayer|5000|1|1|Hitch_Front,PTO_Front|Boom_L,Boom_R,Wheel_L,Wheel_R
IMP-04|Mower|2500|1|1|Link3P_Front,PTO_Front|Bar
IMP-05|DiscHarrow|4000|1|1|Hitch_Front|Wing_L,Wing_R,Wheel_L,Wheel_R
IMP-06|Cultivator|2500|1|1|Link3P_Front|Roller
TRL-01|Trailer_Tipper|4000|1|1|Hitch_Front,Hitch_Rear|Bed,Tailgate,Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR,Load_Grain
TRL-02|Trailer_Flatbed|2500|1|1|Hitch_Front,Hitch_Rear|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR
TRL-03|Trailer_Tank|3500|1|1|Hitch_Front|Hatch,Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR
ATT-01|QuickHitch|400|0|1|Link3P_Front,Link3P_Rear|
ATT-02|FrontWeight|600|0|1|Link3P_Rear|
HRV-01|Combine|12000|1|0|Feeder_Front,Auger_Out,Hitch_Rear,Seat|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR,Feeder,Auger_Unload,Door_L
ATT-03|Header_Grain|5000|1|0|Feeder_Rear|Reel_Arm,Reel,Auger_Cross
ATT-04|Header_Corn|4500|1|0|Feeder_Rear|
ATT-05|Header_Pickup|2500|1|0|Feeder_Rear|Pickup
TRL-04|Trailer_Header|2000|0|0|Hitch_Front,Header_Rest|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR
HRV-02|Baler_Round|5000|1|0|Hitch_Front,PTO_Front,Bale_Out|Pickup,Tailgate,Wheel_L,Wheel_R
HRV-03|ForageHarvester|11000|1|0|Feeder_Front,Spout_Out,Seat|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR,Feeder,Spout,Spout_Tip,Door_L
TRL-05|GrainCart|5000|1|0|Hitch_Front,PTO_Front,Auger_Out|Auger_Unload,Wheel_L,Wheel_R,Load_Grain
TRL-06|Trailer_Bale|3000|1|0|Hitch_Front,Hitch_Rear|Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR
EQP-01|GrainAuger|3000|1|0|Hitch_Front,Auger_Out|Wheel_L,Wheel_R
EQP-02|GrainBin|3500|1|0||Door,Roof_Hatch
IMP-07|HayRake|5000|1|0|Hitch_Front,PTO_Front|Arm_L,Arm_R,Rotor_L,Rotor_R,Wheel_L,Wheel_R
PRP-01|Windrow|300|0|0||";

        public static readonly IReadOnlyList<FarmMachineryItem> Items = Table.Trim().Split('\n').Select(line =>
        {
            var t = line.Trim().Split('|');
            string[] List(string s) => s.Length == 0 ? Array.Empty<string>() : s.Split(',');
            return new FarmMachineryItem
            {
                Id = t[0], Name = t[1], Budget = int.Parse(t[2]), Lod = t[3] == "1", Lite = t[4] == "1", Points = List(t[5]), Parts = List(t[6]),
            };
        }).ToList();

        public const string Prefix = "FMS_Mach_";

        /// <summary>Variant prefabs of CATALOG.md (15): colour 8, pose 5, load 2.</summary>
        public static readonly (string Id, string Variant)[] Variants =
        {
            ("TRC-01", "Green"), ("TRC-01", "Blue"), ("TRC-02", "Green"), ("TRC-02", "Blue"), ("HRV-01", "Green"), ("HRV-01", "Blue"),
            ("HRV-03", "Green"), ("HRV-03", "Blue"), ("IMP-03", "Work"), ("IMP-04", "Work"), ("IMP-05", "Work"), ("IMP-07", "Work"),
            ("HRV-02", "Open"), ("TRL-01", "Grain"), ("TRL-05", "Full"),
        };

        /// <summary>Composition prefabs CMP-01..05: Art/Prefabs/CMP/FMS_Mach_CMP_XX_&lt;Name&gt;.prefab (PackSceneBuilder 'comp' folder).</summary>
        public static readonly (string Id, string Name)[] Compositions =
        {
            ("CMP-01", "CMP_01_Ploughing"), ("CMP-02", "CMP_02_GrainHaul"), ("CMP-03", "CMP_03_MachineYard"),
            ("CMP-04", "CMP_04_Harvest"), ("CMP-05", "CMP_05_Haymaking"),
        };

        /// <summary>
        /// PackConfig.PrefabNames for the layouts of PackSceneBuilder: "TRC-01" -> FMS_Mach_Tractor_Cab, variant "TRC-01_Green" ->
        /// FMS_Mach_Tractor_Cab_Green, composition "CMP-01" -> FMS_Mach_CMP_01_Ploughing (the folder is the part before '-').
        /// </summary>
        public static Dictionary<string, string> PrefabNames()
        {
            var map = Items.ToDictionary(i => i.Id, i => Prefix + i.Name);
            foreach (var (id, variant) in Variants) map[$"{id}_{variant}"] = $"{Prefix}{Item(id).Name}_{variant}";
            foreach (var (id, name) in Compositions) map[id] = Prefix + name;
            return map;
        }

        public static FarmMachineryItem Item(string id) => Items.First(i => i.Id == id);

        /// <summary>Base prefab (made by PackPrefabBuilder from the FBX of the same name).</summary>
        public static string BasePath(string id)
        {
            var item = Item(id);
            return $"{FarmMachineryPackBuilder.Config.PrefabDir}/{item.Category}/{FarmMachineryPackBuilder.Config.Prefix}{item.Name}.prefab";
        }

        /// <summary>Variant prefab next to its base: FMS_Mach_&lt;Name&gt;_&lt;Variant&gt;.prefab; variant null = base.</summary>
        public static string PrefabPath(string id, string variant) =>
            variant == null ? BasePath(id) : BasePath(id).Replace(".prefab", $"_{variant}.prefab");

        public static GameObject LoadPrefab(string id, string variant = null)
        {
            var path = PrefabPath(id, variant);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) throw new InvalidOperationException($"Prefab missing: {path}");
            return prefab;
        }

        public static Transform Find(GameObject root, string name) =>
            root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);

        public static Transform Require(GameObject root, string name) =>
            Find(root, name) ?? throw new InvalidOperationException($"{root.name}: child '{name}' missing");

        /// <summary>World AABB of the LOD0 renderers (no *_Low1) that are active (with all their parents).</summary>
        public static Bounds Lod0Bounds(GameObject root) => Lod0Bounds(root.GetComponentsInChildren<MeshRenderer>(false));

        public static Bounds Lod0Bounds(IEnumerable<MeshRenderer> renderers)
        {
            var first = true; var b = new Bounds();
            foreach (var r in renderers)
            {
                if (r.name.EndsWith("_Low1") || !ActiveChain(r.transform)) continue;
                var mesh = r.GetComponent<MeshFilter>().sharedMesh;
                var mb = mesh.bounds; var m = r.transform.localToWorldMatrix;
                for (var i = 0; i < 8; i++)
                {
                    var p = m.MultiplyPoint3x4(mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (first) { b = new Bounds(p, Vector3.zero); first = false; } else b.Encapsulate(p);
                }
            }
            return b;
        }

        /// <summary>activeSelf of the object and all its parents (activeInHierarchy is false for every object of a prefab asset).</summary>
        public static bool ActiveChain(Transform t)
        {
            for (; t != null; t = t.parent) if (!t.gameObject.activeSelf) return false;
            return true;
        }

        public static int Tris(IEnumerable<MeshRenderer> renderers) =>
            renderers.Sum(r => r.GetComponent<MeshFilter>().sharedMesh.triangles.Length / 3);

        /// <summary>Runs work with a preview scene (the user's open scenes are not touched).</summary>
        public static T InPreviewScene<T>(Func<Scene, T> work)
        {
            var scene = EditorSceneManager.NewPreviewScene();
            try { return work(scene); }
            finally { EditorSceneManager.ClosePreviewScene(scene); }
        }

        public static GameObject Instantiate(GameObject prefab, Scene scene) => (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);

        /// <summary>
        /// Turns a moving part about its own Y hinge (parent-space up, from its rest rotation) so that its outlet point comes as
        /// close as possible, in plan, to the target (1 deg steps): unloading augers and spouts over a cart. Returns the angle and
        /// the remaining horizontal distance.
        /// </summary>
        public static (float Angle, float Error) AimPartY(GameObject go, string part, string outPoint, Vector3 target)
        {
            var p = Require(go, part);
            var o = Require(go, outPoint);
            var rest = p.localRotation;
            float best = float.MaxValue, bestAngle = 0;
            for (var a = 0; a < 360; a++)
            {
                p.localRotation = Quaternion.AngleAxis(a, Vector3.up) * rest;
                var d = new Vector2(o.position.x - target.x, o.position.z - target.z).magnitude;
                if (d < best) { best = d; bestAngle = a; }
            }
            p.localRotation = Quaternion.AngleAxis(bestAngle, Vector3.up) * rest;
            return (bestAngle, best);
        }

        /// <summary>Moves child so that its point childPoint coincides in position and rotation with parentPoint. Returns the position error in metres.</summary>
        public static float Attach(Transform parentPoint, GameObject child, string childPoint)
        {
            var cp = Require(child, childPoint);
            var relRot = Quaternion.Inverse(child.transform.rotation) * cp.rotation;
            var relPos = child.transform.InverseTransformPoint(cp.position);
            var rot = parentPoint.rotation * Quaternion.Inverse(relRot);
            child.transform.SetPositionAndRotation(parentPoint.position - rot * relPos, rot);
            return Vector3.Distance(cp.position, parentPoint.position);
        }
    }
}
