using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
using static FarmMachinery.Editor.FarmMachineryCatalog;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// Composition prefabs CMP-01..05 of CATALOG.md "Композиции и демо" in Art/Prefabs/CMP/FMS_Mach_CMP_XX_&lt;Name&gt;.prefab (FarmMachineryCatalog.Compositions).
    /// Only pack prefabs (nested instances of bases and variants); attached items are placed by the attach points (child `_Front`
    /// onto parent `_Rear`, Feeder_Rear onto Feeder_Front). Owner decisions: no bales, no Farm Nature. Root at the centre of the
    /// composition on the ground, machines drive along +Z. Idempotent: same paths, GUIDs kept.
    /// </summary>
    public static class FarmMachineryCompositions
    {
        private sealed class Comp
        {
            public readonly Transform Root;
            public readonly List<(GameObject Go, string Label)> Items = new List<(GameObject, string)>();
            public readonly HashSet<(GameObject, GameObject)> Joined = new HashSet<(GameObject, GameObject)>();
            public readonly StringBuilder Log = new StringBuilder();
            private readonly Scene scene;

            public Comp(string name, Scene scene)
            {
                this.scene = scene;
                Root = new GameObject(name).transform;
                SceneManager.MoveGameObjectToScene(Root.gameObject, scene);
            }

            /// <summary>Free-standing item at (x, z), facing +Z rotated by rotY.</summary>
            public GameObject Place(string id, string variant, float x, float z, float rotY = 0)
            {
                var go = Instantiate(LoadPrefab(id, variant), scene);
                go.transform.SetParent(Root, false);
                go.transform.SetLocalPositionAndRotation(new Vector3(x, 0, z), Quaternion.Euler(0, rotY, 0));
                var label = variant == null ? id : $"{id} {variant}";
                go.name = $"{label.Replace(' ', '_')}_{go.name}";
                Items.Add((go, label));
                return go;
            }

            /// <summary>Item attached to parent: child point onto parent point (and checks a second point pair, e.g. PTO).</summary>
            public GameObject Attach(GameObject parent, string parentPoint, string id, string variant, string childPoint, string checkParent = null, string checkChild = null)
            {
                var go = Place(id, variant, 0, 0);
                var err = FarmMachineryCatalog.Attach(Require(parent, parentPoint), go, childPoint);
                var angle = Quaternion.Angle(Require(parent, parentPoint).rotation, Require(go, childPoint).rotation);
                var line = $"  {Items.Last().Label}.{childPoint} -> {Label(parent)}.{parentPoint}: error {err * 1000:F1} mm, {angle:F1}°";
                if (checkParent != null)
                    line += $"; {checkChild} -> {checkParent}: {Vector3.Distance(Require(parent, checkParent).position, Require(go, checkChild).position) * 1000:F1} mm";
                Log.AppendLine(line);
                Joined.Add((parent, go));
                return go;
            }

            /// <summary>Moves the tractor so that its point meets the point of the already placed child (the child stays).</summary>
            public void Tow(GameObject tractor, string tractorPoint, GameObject child, string childPoint)
            {
                var tp = Require(tractor, tractorPoint); var cp = Require(child, childPoint);
                tractor.transform.position += cp.position - tp.position;
                Log.AppendLine($"  {Label(child)}.{childPoint} <- {Label(tractor)}.{tractorPoint}: error {Vector3.Distance(cp.position, tp.position) * 1000:F1} mm");
                Joined.Add((tractor, child));
            }

            /// <summary>Intended contact that is not an attach-point joint (e.g. a pickup over the windrow).</summary>
            public void Expect(GameObject a, GameObject b) => Joined.Add((a, b));

            public string Label(GameObject go) => Items.First(i => i.Go == go).Label;
        }

        [MenuItem("Tools/Farm Machinery/Build Compositions")]
        public static string Build() => FarmMachineryRelease.Staged(BuildStaged);

        private static string BuildStaged()
        {
            var dir = $"{FarmMachineryPackBuilder.Config.PrefabDir}/CMP";
            Directory.CreateDirectory(dir);
            MoveFromOldFolder(dir);
            var log = new StringBuilder("[FarmMachinery] compositions\n");
            InPreviewScene(scene =>
            {
                var makers = new System.Action<Comp>[] { Ploughing, GrainHaul, MachineYard, Harvest, Haymaking };
                foreach (var ((_, name), make) in FarmMachineryCatalog.Compositions.Zip(makers, (c, m) => (c, m)))
                {
                    var comp = new Comp(FarmMachineryPackBuilder.Config.Prefix + name, scene);
                    make(comp);
                    Center(comp);
                    var b = Lod0Bounds(comp.Root.gameObject);
                    var path = $"{dir}/{comp.Root.name}.prefab";
                    PrefabUtility.SaveAsPrefabAsset(comp.Root.gameObject, path, out var ok);
                    log.AppendLine($"{comp.Root.name}: {comp.Items.Count} items ({string.Join(", ", comp.Items.Select(i => i.Label))}), " +
                                   $"size {b.size.x:F1}x{b.size.y:F1}x{b.size.z:F1}, min Y {b.min.y:F3}" + (ok ? "" : "  ! save failed"));
                    log.Append(comp.Log);
                    foreach (var o in Overlaps(comp)) log.AppendLine("  overlap (AABB, not attached): " + o);
                    Object.DestroyImmediate(comp.Root.gameObject);
                }
                return 0;
            });
            AssetDatabase.SaveAssets();
            Debug.Log(log.ToString());
            return log.ToString();
        }

        // CMP-01 Пахота (Lite): TRC-01 Red, IMP-01 on Link3P_Rear (linkage at rest = lowered, plough on the ground).
        private static void Ploughing(Comp c)
        {
            var tractor = c.Place("TRC-01", null, 0, 0);
            c.Attach(tractor, "Link3P_Rear", "IMP-01", null, "Link3P_Front");
        }

        // CMP-02 Перевозка зерна (Lite): TRC-02 Blue, TRL-01 Grain, TRL-01 Empty, chain over Hitch_Rear.
        private static void GrainHaul(Comp c)
        {
            var tractor = c.Place("TRC-02", "Blue", 0, 0);
            var full = c.Attach(tractor, "Hitch_Rear", "TRL-01", "Grain", "Hitch_Front");
            c.Attach(full, "Hitch_Rear", "TRL-01", null, "Hitch_Front");
        }

        // CMP-03 Двор техники (Lite): the whole Lite fleet parked in two dense lines side by side (owner 2026-11-24 "кучнее"; was
        // one 50 m line after the scene reference), nose to tail along +Z (front first), Gap apart. ATT-01 / ATT-02 hang on a
        // linkage by spec: parked, they are lowered onto their lowest point (y = −min Y) so they stand on the ground.
        private static void MachineYard(Comp c)
        {
            var rows = new[]
            {
                new (string Id, string Variant)[] { ("TRC-01", "Green"), ("TRC-02", null), ("ATT-01", null), ("ATT-02", null), ("IMP-02", null), ("IMP-04", null), ("IMP-06", null) },
                new (string Id, string Variant)[] { ("IMP-03", null), ("IMP-05", null), ("TRL-02", null), ("TRL-03", null) },
            };
            var groups = new List<GameObject[]>();
            foreach (var row in rows)
            {
                var z = 0f;
                var placed = new List<GameObject>();
                foreach (var (id, variant) in row)
                {
                    var go = c.Place(id, variant, 0, 0);
                    var b = Lod0Bounds(go);
                    go.transform.position = new Vector3(-b.center.x, -b.min.y, z - b.max.z);
                    if (b.min.y > 0.005f) c.Log.AppendLine($"  {c.Label(go)} parked on the ground (lowered {b.min.y:F2} m)");
                    z -= b.size.z + Gap;
                    placed.Add(go);
                }
                groups.Add(placed.ToArray());
            }
            PackAlongX(groups, RowGap);
        }

        /// <summary>Gap between neighbouring machines and groups in the compositions (owner: objects close to each other).</summary>
        private const float Gap = 0.7f;

        /// <summary>Gap between the two CMP-03 parking lines: a tall machine (sprayer tank ~3 m) hides about h / tan(pitch) of
        /// the ground behind it, so 0.7 m made the back line disappear behind the front one in the demo cameras.</summary>
        private const float RowGap = 3.0f;

        /// <summary>Places the groups side by side along +X, each group's bounding box gap after the previous one.</summary>
        private static void PackAlongX(IEnumerable<GameObject[]> groups, float gap = Gap)
        {
            float? edge = null;
            foreach (var g in groups)
            {
                var b = Lod0Bounds(g.SelectMany(go => go.GetComponentsInChildren<MeshRenderer>()));
                var shift = edge.HasValue ? edge.Value + gap - b.min.x : 0f;
                foreach (var go in g) go.transform.position += new Vector3(shift, 0, 0);
                edge = b.max.x + shift;
            }
        }

        // CMP-04 Жатва (Full): HRV-01 Red with ATT-03 unloading (auger swung out) into TRL-05 Full towed by TRC-02 Green beside it;
        // the cart's own auger unfolded over TRL-01 Grain towed by TRC-01 Red.
        private static void Harvest(Comp c)
        {
            var combine = c.Place("HRV-01", null, 0, 0);
            c.Attach(combine, "Feeder_Front", "ATT-03", null, "Feeder_Rear");

            // TRC-02 Green + cart drive beside the combine, the cart hopper level with the combine's unloading auger hinge (Demo_Harvest
            // 2026-11-24): the combine's Auger_Unload (3.6 m reach) is swung out over the hopper centre.
            var large = c.Place("TRC-02", "Green", -5.3f, 6.1f);
            var cart = c.Attach(large, "Hitch_Rear", "TRL-05", "Full", "Hitch_Front", "PTO_Rear", "PTO_Front");
            FarmMachineryVariants.UnfoldGrainCartAuger(cart);
            var hopper = Lod0Bounds(Require(cart, "Hopper").GetComponents<MeshRenderer>());
            var (augerAngle, augerError) = AimPartY(combine, "Auger_Unload", "Auger_Out", hopper.center);
            var combineAuger = Require(combine, "Auger_Unload");
            c.Log.AppendLine($"  HRV-01 Auger_Unload turned {augerAngle} deg: outlet {augerError:F2} m (plan) from the TRL-05 hopper centre, " +
                             $"Y {Require(combine, "Auger_Out").position.y:F2} over the hopper rim {hopper.max.y:F2}, auger vertices inside the hopper box: {VerticesInside(combineAuger, hopper)}");
            c.Expect(combine, cart);
            var outlet = Require(cart, "Auger_Out").position;

            var tipper = c.Place("TRL-01", "Grain", 0, 0);
            var bed = Lod0Bounds(Require(tipper, "Bed").GetComponentsInChildren<MeshRenderer>());
            tipper.transform.position = new Vector3(outlet.x - bed.center.x, 0, outlet.z - bed.center.z);
            // The rising auger tube must clear the near side wall: move the tipper away from the cart until no auger vertex is
            // inside the bed box, keeping the outlet over the bed.
            var auger = Require(cart, "Auger_Unload");
            var away = Mathf.Sign(tipper.transform.position.x - cart.transform.position.x);
            var shift = 0f;
            for (; shift < bed.extents.x - 0.25f && VerticesInside(auger, BedBox(tipper)) > 0; shift += 0.05f)
                tipper.transform.position += new Vector3(away * 0.05f, 0, 0);
            var box = BedBox(tipper);
            var cab = c.Place("TRC-01", null, 0, 0);
            c.Tow(cab, "Hitch_Rear", tipper, "Hitch_Front");
            c.Log.AppendLine($"  TRL-05 Auger_Out (Y {outlet.y:F2}) over the TRL-01 Grain bed (top Y {box.max.y:F2}), {Mathf.Abs(outlet.x - box.center.x):F2} m off the bed centre " +
                             $"(tipper moved {shift:F2} m out), auger vertices inside the bed box: {VerticesInside(auger, box)}");
            c.Expect(cart, tipper);
        }

        // CMP-05 Сенокос (Full): TRC-01 Green + IMP-04 Work, TRC-01 Red + IMP-07 Work, TRC-02 Red + HRV-02 Open picking up the
        // windrow (PRP-01 ×4 snapped every 4 m along Z, lying ahead of the baler under the straddling tractor), TRL-06 empty
        // parked (no bales).
        private static void Haymaking(Comp c)
        {
            var baler = c.Place("HRV-02", "Open", 0, -6f);
            var large = c.Place("TRC-02", null, 0, 0);
            c.Tow(large, "Hitch_Rear", baler, "Hitch_Front");
            c.Log.AppendLine($"  PTO_Front -> PTO_Rear: {Vector3.Distance(Require(large, "PTO_Rear").position, Require(baler, "PTO_Front").position) * 1000:F1} mm");
            var start = Lod0Bounds(Require(baler, "Pickup").GetComponentsInChildren<MeshRenderer>()).max.z - 0.5f;   // pickup over the windrow end
            var balerGroup = new List<GameObject> { baler, large };
            for (var i = 0; i < 4; i++)
            {
                var w = c.Place("PRP-01", null, 0, start + 2f + 4f * i);
                c.Expect(w, baler);
                c.Expect(w, large);
                balerGroup.Add(w);
            }

            var rakeTractor = c.Place("TRC-01", null, 6.5f, 2.0f);
            var rake = c.Attach(rakeTractor, "Hitch_Rear", "IMP-07", "Work", "Hitch_Front", "PTO_Rear", "PTO_Front");
            var mowTractor = c.Place("TRC-01", "Green", 12.5f, 6.0f);
            var mower = c.Attach(mowTractor, "Link3P_Rear", "IMP-04", "Work", "Link3P_Front", "PTO_Rear", "PTO_Front");
            var bales = c.Place("TRL-06", null, -5.0f, -4.0f);
            // owner 2026-11-24 ("кучнее"): the four groups side by side, Gap apart (z staggering as before)
            PackAlongX(new[] { new[] { bales }, balerGroup.ToArray(), new[] { rakeTractor, rake }, new[] { mowTractor, mower } });
        }

        /// <summary>The first import saved the compositions in Art/Prefabs/Compositions; move them (GUIDs kept) to the 'comp' folder.</summary>
        private static void MoveFromOldFolder(string dir)
        {
            var old = $"{FarmMachineryPackBuilder.Config.PrefabDir}/Compositions";
            if (!AssetDatabase.IsValidFolder(old)) return;
            AssetDatabase.Refresh();
            foreach (var path in AssetDatabase.FindAssets("t:Prefab", new[] { old }).Select(AssetDatabase.GUIDToAssetPath))
            {
                var error = AssetDatabase.MoveAsset(path, $"{dir}/{Path.GetFileName(path)}");
                if (!string.IsNullOrEmpty(error)) throw new System.InvalidOperationException(error);
            }
            AssetDatabase.DeleteAsset(old);
        }

        private static Bounds BedBox(GameObject tipper) => Lod0Bounds(Require(tipper, "Bed").GetComponents<MeshRenderer>());

        private static int VerticesInside(Transform part, Bounds box) =>
            part.GetComponentsInChildren<MeshFilter>().Where(f => !f.name.EndsWith("_Low1"))
                .Sum(f => f.sharedMesh.vertices.Count(v => box.Contains(f.transform.TransformPoint(v))));

        /// <summary>Shifts the items so the composition footprint is centred on the root (X/Z) with the ground at Y 0.</summary>
        private static void Center(Comp c)
        {
            var b = Lod0Bounds(c.Root.gameObject);
            var shift = new Vector3(-b.center.x, 0, -b.center.z);
            foreach (Transform t in c.Root) t.position += shift;
        }

        private static IEnumerable<string> Overlaps(Comp c)
        {
            var boxes = c.Items.Select(i => (i.Go, i.Label, B: Lod0Bounds(i.Go))).ToList();
            for (var a = 0; a < boxes.Count; a++)
                for (var b = a + 1; b < boxes.Count; b++)
                {
                    if (c.Joined.Contains((boxes[a].Go, boxes[b].Go)) || c.Joined.Contains((boxes[b].Go, boxes[a].Go))) continue;
                    var A = boxes[a].B; var B = boxes[b].B;
                    var d = Vector3.Min(A.max, B.max) - Vector3.Max(A.min, B.min);
                    if (d.x > 0.01f && d.y > 0.01f && d.z > 0.01f)
                        yield return $"{boxes[a].Label} x {boxes[b].Label} ({d.x:F2} x {d.y:F2} x {d.z:F2} m)";
                }
        }
    }
}
