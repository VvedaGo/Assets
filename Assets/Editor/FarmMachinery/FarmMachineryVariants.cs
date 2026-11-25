using System;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using static FarmMachinery.Editor.FarmMachineryCatalog;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Variant prefabs of CATALOG.md (15): Prefab Variants of the PackPrefabBuilder base prefab, saved next to it as
    /// FMS_Mach_&lt;Name&gt;_&lt;Variant&gt;. Colour = material swap to M_FarmMachinery_Green/Blue; pose = the named parts rotated about
    /// their hinge (angles from the builder notes .work/models/FarmMachinery/&lt;ID&gt;_*/notes.md); load = Load_Grain on.
    /// Bases stay Red / Transport / Closed / Empty (Load_Grain is switched off in the base). Idempotent: paths, so GUIDs, are kept.
    /// </summary>
    public static class FarmMachineryVariants
    {
        private sealed class Pose
        {
            public string Part; public Vector3 Axis; public float Angle;
            /// <summary>Picks the sign of the rotation: the larger score wins (the builder notes give the direction, not the sign).</summary>
            public Func<Transform, float> Score;
        }

        private static float OutwardX(Transform part) => Mathf.Abs(Lod0Bounds(part.GetComponentsInChildren<MeshRenderer>()).center.x);
        private static float TowardPlusX(Transform part) => Lod0Bounds(part.GetComponentsInChildren<MeshRenderer>()).center.x;
        private static float Backward(Transform part) => -Lod0Bounds(part.GetComponentsInChildren<MeshRenderer>()).center.z;

        // IMP-03 booms ±90° about Y outward (span 10.46 m); IMP-04 bar 90° about Z to +X (width 3.13 m); IMP-05 wings 90° about Z
        // down (width 4.06 m); IMP-07 arms 90° about Z down (span 6.66 m, Fix 1); HRV-02 tailgate +80° about X, rear edge up and back.
        private static readonly (string Id, string Variant, Pose[] Poses)[] PoseVariants =
        {
            ("IMP-03", "Work", new[] { new Pose { Part = "Boom_L", Axis = Vector3.up, Angle = 90, Score = OutwardX }, new Pose { Part = "Boom_R", Axis = Vector3.up, Angle = 90, Score = OutwardX } }),
            ("IMP-04", "Work", new[] { new Pose { Part = "Bar", Axis = Vector3.forward, Angle = 90, Score = TowardPlusX } }),
            ("IMP-05", "Work", new[] { new Pose { Part = "Wing_L", Axis = Vector3.forward, Angle = 90, Score = OutwardX }, new Pose { Part = "Wing_R", Axis = Vector3.forward, Angle = 90, Score = OutwardX } }),
            ("IMP-07", "Work", new[] { new Pose { Part = "Arm_L", Axis = Vector3.forward, Angle = 90, Score = OutwardX }, new Pose { Part = "Arm_R", Axis = Vector3.forward, Angle = 90, Score = OutwardX } }),
            ("HRV-02", "Open", new[] { new Pose { Part = "Tailgate", Axis = Vector3.right, Angle = 80, Score = Backward } }),
        };

        private static readonly string[] ColourIds = { "TRC-01", "TRC-02", "HRV-01", "HRV-03" };
        private static readonly string[] Atlases = { "Green", "Blue" };
        private static readonly (string Id, string Variant)[] LoadVariants = { ("TRL-01", "Grain"), ("TRL-05", "Full") };

        /// <summary>TRL-05 Full in CMP-04: auger unfolded, +150° about Y (builder notes: Auger_Out at (−3.29, 2.95, +1.99)).</summary>
        public static void UnfoldGrainCartAuger(GameObject cart)
        {
            var target = new Vector3(-3.29f, 2.95f, 1.99f);
            Rotate(cart, new Pose { Part = "Auger_Unload", Axis = Vector3.up, Angle = 150, Score = p => -Vector3.Distance(cart.transform.InverseTransformPoint(Require(cart, "Auger_Out").position), target) });
        }

        [MenuItem("Tools/Farm Machinery/Build Variants")]
        public static string Build()
        {
            var log = new StringBuilder("[FarmMachinery] variants\n");
            foreach (var (id, _) in LoadVariants) EmptyBase(id, log);
            var materials = Atlases.ToDictionary(a => a, AtlasMaterial);

            InPreviewScene(scene =>
            {
                foreach (var id in ColourIds)
                    foreach (var atlas in Atlases)
                        SaveVariant(id, atlas, scene, log, go =>
                        {
                            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
                                r.sharedMaterials = Enumerable.Repeat(materials[atlas], r.sharedMaterials.Length).ToArray();
                            return $"material {materials[atlas].name}";
                        });

                foreach (var (id, variant, poses) in PoseVariants)
                    SaveVariant(id, variant, scene, log, go =>
                    {
                        var info = string.Join(", ", poses.Select(p => Rotate(go, p)));
                        var b = Lod0Bounds(go);
                        var box = go.GetComponent<BoxCollider>();       // posed parts reach outside the base box
                        box.center = b.center - go.transform.position;
                        box.size = b.size;
                        go.GetComponent<LODGroup>()?.RecalculateBounds();
                        return $"{info}; size {b.size.x:F2}x{b.size.y:F2}x{b.size.z:F2}, min Y {b.min.y:F3}";
                    });

                foreach (var (id, variant) in LoadVariants)
                    SaveVariant(id, variant, scene, log, go =>
                    {
                        Require(go, "Load_Grain").gameObject.SetActive(true);
                        return "Load_Grain on";
                    });
                return 0;
            });
            AssetDatabase.SaveAssets();
            Debug.Log(log.ToString());
            return log.ToString();
        }

        private static void SaveVariant(string id, string variant, UnityEngine.SceneManagement.Scene scene, StringBuilder log, Func<GameObject, string> modify)
        {
            var go = Instantiate(LoadPrefab(id), scene);
            var info = modify(go);
            var path = PrefabPath(id, variant);
            PrefabUtility.SaveAsPrefabAsset(go, path, out var ok);
            UnityEngine.Object.DestroyImmediate(go);
            var isVariant = PrefabUtility.GetPrefabAssetType(AssetDatabase.LoadAssetAtPath<GameObject>(path)) == PrefabAssetType.Variant;
            log.AppendLine($"{id} {variant}: {System.IO.Path.GetFileName(path)}  {info}" + (ok && isVariant ? "" : "  ! not saved as a Prefab Variant"));
        }

        /// <summary>Rotates the part about its hinge (axis in the parent space) by ±Angle; the sign with the larger score is kept.</summary>
        private static string Rotate(GameObject go, Pose pose)
        {
            var part = Require(go, pose.Part);
            var rest = part.localRotation;
            float best = float.NegativeInfinity, sign = 1;
            foreach (var s in new[] { 1f, -1f })
            {
                part.localRotation = Quaternion.AngleAxis(s * pose.Angle, pose.Axis) * rest;
                var score = pose.Score(part);
                if (score > best) { best = score; sign = s; }
            }
            part.localRotation = Quaternion.AngleAxis(sign * pose.Angle, pose.Axis) * rest;
            return $"{pose.Part} {sign * pose.Angle:+0;-0}° about {AxisName(pose.Axis)}";
        }

        private static string AxisName(Vector3 a) => a == Vector3.up ? "Y" : a == Vector3.right ? "X" : "Z";

        /// <summary>Base of a load variant = Empty: Load_Grain inactive (PackPrefabBuilder exports it active).</summary>
        private static void EmptyBase(string id, StringBuilder log)
        {
            var path = BasePath(id);
            var root = PrefabUtility.LoadPrefabContents(path);
            try
            {
                var load = Require(root, "Load_Grain").gameObject;
                if (load.activeSelf)
                {
                    load.SetActive(false);
                    PrefabUtility.SaveAsPrefabAsset(root, path);
                }
                log.AppendLine($"{id} base: Load_Grain off");
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
        }

        /// <summary>M_FarmMachinery_&lt;Atlas&gt; = copy of the Red material made by PackPrefabBuilder with the other atlas.</summary>
        private static Material AtlasMaterial(string atlas)
        {
            var c = FarmMachineryPackBuilder.Config;
            var red = AssetDatabase.LoadAssetAtPath<Material>($"{c.MaterialDir}/M_FarmMachinery_Red.mat")
                      ?? throw new InvalidOperationException("M_FarmMachinery_Red missing: run Build Prefabs first");
            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>($"{c.TextureDir}/T_FarmMachinery_{atlas}_BaseColor.png")
                          ?? throw new InvalidOperationException($"T_FarmMachinery_{atlas}_BaseColor.png missing");
            var path = $"{c.MaterialDir}/M_FarmMachinery_{atlas}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(red);
                AssetDatabase.CreateAsset(mat, path);
            }
            else mat.CopyPropertiesFromMaterial(red);
            mat.SetTexture("_BaseMap", texture);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            return mat;
        }
    }
}
