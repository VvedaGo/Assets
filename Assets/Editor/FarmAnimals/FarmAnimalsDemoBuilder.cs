using System.Collections.Generic;
using System.IO;
using System.Linq;
using FarmAnimals.Demo;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FarmAnimals.Editor
{
    /// <summary>
    /// Builds the Farm Animals demo content in the series style (Farm Nature / Processing): floating faceted grass islands
    /// with a soil rim and a rocky underside, a pale blue sky, low-poly clouds and a warm sun.
    ///   Demo_FarmAnimals_Showcase.unity    - one island per catalogue category, every animal cycling through its clips;
    ///   Art/Prefabs/CMP/FMS_CMP_*.prefab    - 8 compositions (animal prefabs only, pack content);
    ///   Demo_FarmAnimals_Compositions.unity - each composition on its own island, land animals wandering.
    /// Every island has a disabled shot camera (Cam_*), the Main Camera frames the whole scene.
    /// Idempotent: scenes, meshes, materials and composition prefabs are rebuilt in place (GUIDs kept).
    /// </summary>
    public static class FarmAnimalsDemoBuilder
    {
        private const string Root = "Assets/FarmAnimals";
        private const string PrefabDir = Root + "/Art/Prefabs";
        private const string CmpDir = PrefabDir + "/CMP";
        private const string DemoDir = Root + "/Demo";
        private const string SceneDir = DemoDir + "/Scenes";
        private const string MatDir = DemoDir + "/Materials";
        private const string MeshDir = DemoDir + "/Meshes";
        private const float Fov = 26f;

        private static readonly (string Name, string Folder, string[] Species)[] Categories =
        {
            ("Livestock", "LIV", new[] { "Cow", "Calf", "Bull", "Horse", "Foal", "Donkey", "Sheep", "Lamb", "Ram", "Goat", "Kid", "Pig", "Piglet" }),
            ("Birds", "BRD", new[] { "Hen", "Rooster", "Chick", "Turkey", "Duck", "Duckling", "Goose", "Pigeon", "Sparrow", "Crow" }),
            ("Pets", "PET", new[] { "Dog", "Puppy", "Cat", "Kitten" }),
            ("SmallAnimals", "SML", new[] { "Fox", "Rabbit", "Hedgehog", "Mouse", "Frog" }),
            ("Insects", "INS", new[] { "Bee", "Butterfly", "Ladybug" }),
        };

        private static readonly (string Name, string[] Animals)[] Compositions =
        {
            ("Pasture", new[] { "Cow", "Bull", "Calf", "Goat", "Kid" }),
            ("Stable", new[] { "Horse", "Foal", "Donkey" }),
            ("SheepFlock", new[] { "Sheep", "Sheep", "Ram", "Lamb", "Lamb", "Dog" }),
            ("Pigsty", new[] { "Pig", "Piglet", "Piglet", "Piglet" }),
            ("Barnyard", new[] { "Turkey", "Rooster", "Hen", "Hen", "Chick", "Chick", "Chick" }),
            ("Pond", new[] { "Goose", "Duck", "Duckling", "Duckling", "Frog" }),
            ("Garden", new[] { "Puppy", "Cat", "Kitten", "Rabbit", "Hedgehog", "Bee", "Bee", "Butterfly", "Butterfly", "Ladybug" }),
            ("Orchard", new[] { "Fox", "Crow", "Pigeon", "Pigeon", "Sparrow", "Sparrow", "Mouse" }),
        };

        internal static readonly HashSet<string> Fliers = new HashSet<string> { "Bee", "Butterfly" };

        internal sealed class Info
        {
            public GameObject Prefab;
            public Bounds Bounds;              // rest pose, prefab root at the origin
            public Vector3 Forward;            // local facing direction (XZ)
            public string[] Extras;            // bool parameters
            public bool Locomotion;
            public float Walk, Fast;
            public float Footprint => Mathf.Max(Bounds.size.x, Bounds.size.z);
        }

        private static readonly Dictionary<string, Info> Cache = new Dictionary<string, Info>();
        internal static Material _grass, _soil, _rock, _cloud;
        private static Mesh _cloudMesh;

        [MenuItem("Tools/Farm Animals/Build Demo Scenes And Compositions")]
        public static void BuildMenu() => Build();

        public static string Build()
        {
            Cache.Clear();
            Directory.CreateDirectory(SceneDir); Directory.CreateDirectory(MatDir); Directory.CreateDirectory(MeshDir); Directory.CreateDirectory(CmpDir);
            Materials();
            var log = new System.Text.StringBuilder();
            log.AppendLine(BuildCompositionPrefabs());
            log.AppendLine(BuildShowcase());
            log.AppendLine(BuildCompositionScene());
            AssetDatabase.SaveAssets();
            Debug.Log(log.ToString());
            return log.ToString();
        }

        // ---------------- animal data ----------------
        internal static Info Animal(string species)
        {
            if (Cache.TryGetValue(species, out var info)) return info;
            var path = AssetDatabase.FindAssets($"FMS_{species} t:Prefab", new[] { PrefabDir })
                .Select(AssetDatabase.GUIDToAssetPath).First(p => Path.GetFileNameWithoutExtension(p) == $"FMS_{species}");
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            info = new Info { Prefab = prefab, Bounds = FarmAnimalsBuilder.MeshBounds(go, go.GetComponentsInChildren<Renderer>()) };

            var t = go.GetComponentsInChildren<Transform>();
            var head = t.FirstOrDefault(x => x.name == "Head");
            var body = t.FirstOrDefault(x => x.name == "Pelvis") ?? t.FirstOrDefault(x => x.name == "Body") ?? t.FirstOrDefault(x => x.name == "Root");
            var f = head != null && body != null ? head.position - body.position : Vector3.forward;
            f.y = 0f;
            info.Forward = f.sqrMagnitude > 1e-6f ? go.transform.InverseTransformDirection(f.normalized) : Vector3.forward;

            var controller = (AnimatorController)go.GetComponent<Animator>().runtimeAnimatorController;
            info.Locomotion = controller.parameters.Any(p => p.name == "Speed");
            info.Extras = controller.parameters.Where(p => p.type == AnimatorControllerParameterType.Bool).Select(p => p.name).ToArray();
            if (controller.layers[0].stateMachine.defaultState.motion is BlendTree tree)
            {
                var th = tree.children.Select(c => c.threshold).OrderBy(x => x).ToArray();
                info.Walk = th.Length > 1 ? th[1] : 0.5f;
                info.Fast = th.Length > 2 ? th[2] : 0f;
            }
            Object.DestroyImmediate(go);
            Cache[species] = info;
            return info;
        }

        /// <summary>Y rotation that turns the model to face direction `toward` (world XZ) turned by `turn` degrees.</summary>
        internal static Quaternion Facing(Info info, Vector3 toward, float turn) =>
            Quaternion.Euler(0f, Vector3.SignedAngle(info.Forward, toward, Vector3.up) + turn, 0f);

        private static GameObject Place(string species, Transform parent, Vector3 local, Quaternion rot)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Animal(species).Prefab, parent);
            go.transform.localPosition = local;
            go.transform.localRotation = rot;
            return go;
        }

        private static void AddDemo(GameObject animal, string species, FarmAnimalDemo.DemoMode mode, float radius)
        {
            var info = Animal(species);
            if (!animal.TryGetComponent<FarmAnimalDemo>(out var demo)) demo = animal.AddComponent<FarmAnimalDemo>();
            demo.Configure(Fliers.Contains(species) ? FarmAnimalDemo.DemoMode.Cycle : mode, info.Extras, info.Locomotion, info.Walk, info.Fast, radius, info.Forward);
            EditorUtility.SetDirty(demo);
        }

        // ---------------- layouts ----------------
        /// <summary>Rows from the back to the front, each row centred; returns local positions and the half extents.</summary>
        private static List<Vector3> Rows(IList<string> species, out Vector2 half)
        {
            var sizes = species.Select(s => Animal(s).Footprint * 0.85f + Mathf.Clamp(Animal(s).Footprint * 0.3f, 0.06f, 0.35f)).ToList();
            var maxRow = Mathf.Clamp(Mathf.Sqrt(sizes.Sum(s => s * s)) * 1.7f, sizes.Max(), 14f);
            var rows = new List<List<int>> { new List<int>() };
            float w = 0f;
            for (var i = 0; i < sizes.Count; i++)
            {
                if (rows[rows.Count - 1].Count > 0 && w + sizes[i] > maxRow) { rows.Add(new List<int>()); w = 0f; }
                rows[rows.Count - 1].Add(i); w += sizes[i];
            }
            var depths = rows.Select(r => r.Max(i => sizes[i])).ToList();
            var total = depths.Sum();
            var pos = new Vector3[sizes.Count];
            var z = total / 2f;                                    // first row at the back (+z, away from the camera)
            half = Vector2.zero;
            for (var r = 0; r < rows.Count; r++)
            {
                z -= depths[r] / 2f;
                var rw = rows[r].Sum(i => sizes[i]);
                var x = -rw / 2f;
                foreach (var i in rows[r]) { pos[i] = new Vector3(x + sizes[i] / 2f, 0f, z); x += sizes[i]; }
                half.x = Mathf.Max(half.x, rw / 2f);
                z -= depths[r] / 2f;
            }
            half.y = total / 2f;
            return pos.ToList();
        }

        /// <summary>Loose cluster: biggest animals first near the centre, the rest on a spiral without overlaps.</summary>
        private static List<Vector3> Cluster(IList<string> species, int seed, out float radius)
        {
            var rnd = new System.Random(seed);
            var order = Enumerable.Range(0, species.Count).OrderByDescending(i => Animal(species[i]).Footprint).ToList();
            var pos = new Vector3[species.Count];
            var placed = new List<(Vector3 P, float R)>();
            foreach (var i in order)
            {
                var r = Animal(species[i]).Footprint * 0.42f + 0.12f;
                Vector3 p = Vector3.zero;
                for (var k = 0; k < 4000; k++)
                {
                    var a = k * 0.5f + (float)rnd.NextDouble() * 0.3f;
                    var d = k * 0.004f;
                    p = new Vector3(Mathf.Cos(a) * d * 1.25f, 0f, Mathf.Sin(a) * d);
                    if (placed.All(q => Vector3.Distance(q.P, p) >= q.R + r)) break;
                }
                placed.Add((p, r)); pos[i] = p;
            }
            radius = placed.Max(q => q.P.magnitude + q.R);
            return pos.ToList();
        }

        // ---------------- compositions (pack content) ----------------
        private static string BuildCompositionPrefabs()
        {
            var lines = new List<string>();
            foreach (var (name, animals) in Compositions)
            {
                var root = new GameObject($"FMS_CMP_{name}");
                var pos = Cluster(animals, name.GetHashCode(), out _);
                var rnd = new System.Random(name.Length * 7919);
                var toward = Quaternion.Euler(0f, 40f, 0f) * Vector3.back;    // compositions are shot from yaw -40 (front-left)
                for (var i = 0; i < animals.Length; i++)
                {
                    var go = Place(animals[i], root.transform, pos[i], Facing(Animal(animals[i]), toward, (float)rnd.NextDouble() * 110f - 55f));
                    go.name = $"{go.name}_{i + 1:00}";
                }
                var path = $"{CmpDir}/FMS_CMP_{name}.prefab";
                PrefabUtility.SaveAsPrefabAsset(root, path);
                Object.DestroyImmediate(root);
                lines.Add($"{name}: {animals.Length}");
            }
            return "[FarmAnimals] compositions " + string.Join(", ", lines);
        }

        // ---------------- scenes ----------------
        private static string BuildShowcase()
        {
            var scene = NewScene(out var world);
            var x = 0f; var all = new List<Transform>();
            foreach (var (name, _, species) in Categories)
            {
                var pos = Rows(species, out var half);
                var margin = Mathf.Clamp(species.Max(s => Animal(s).Footprint) * 0.35f, 0.15f, 0.7f);
                var island = Island(name, world, half.x + margin, half.y + margin, out var rx);
                island.position = new Vector3(x + rx, 0f, 0f);
                x += rx * 2f + Mathf.Max(1.2f, rx * 0.5f);
                var animals = new GameObject("Animals").transform; animals.SetParent(island, false);
                for (var i = 0; i < species.Length; i++)
                {
                    var info = Animal(species[i]);
                    var go = Place(species[i], animals, pos[i], Facing(info, Vector3.back, -30f));
                    AddDemo(go, species[i], FarmAnimalDemo.DemoMode.Cycle, 0f);
                }
                ShotCamera(island, $"Cam_{name}", 0f, 42f);
                all.Add(island);
            }
            Finish(world, all, 0f, 38f);
            var ground = FarmAnimalsShots.GroundAnimals(true);
            var path = $"{SceneDir}/Demo_FarmAnimals_Showcase.unity";
            EditorSceneManager.SaveScene(scene, path);
            return $"[FarmAnimals] showcase: {Categories.Length} islands, {Categories.Sum(c => c.Species.Length)} animals -> {path}\n{ground}";
        }

        private static string BuildCompositionScene()
        {
            var scene = NewScene(out var world);
            var all = new List<Transform>();
            for (var c = 0; c < Compositions.Length; c++)
            {
                var (name, animals) = Compositions[c];
                Cluster(animals, name.GetHashCode(), out var radius);
                var island = Island(name, world, radius * 1.2f + 0.6f, radius + 0.6f, out _);
                island.position = new Vector3((c % 4) * 13f, 0f, (c / 4) * -13f);
                var cmp = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{CmpDir}/FMS_CMP_{name}.prefab"), island);
                foreach (Transform a in cmp.transform)
                {
                    var species = a.name.Substring(4, a.name.LastIndexOf('_') - 4);
                    AddDemo(a.gameObject, species, FarmAnimalDemo.DemoMode.Wander, Mathf.Clamp(radius * 0.45f, 0.4f, 2f));
                }
                ShotCamera(island, $"Cam_{name}", -40f, 34f);
                all.Add(island);
            }
            Finish(world, all, -25f, 40f);
            var ground = FarmAnimalsShots.GroundAnimals(true);
            var path = $"{SceneDir}/Demo_FarmAnimals_Compositions.unity";
            EditorSceneManager.SaveScene(scene, path);
            return $"[FarmAnimals] compositions scene: {Compositions.Length} islands -> {path}\n{ground}";
        }

        internal static UnityEngine.SceneManagement.Scene NewScene(out Transform world, string profilePath = DemoDir + "/Settings/PP_FarmAnimalsDemo.asset")
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            world = new GameObject("FarmAnimals_Demo").transform;
            var volume = new GameObject("PostProcessing").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = PostProfile(profilePath);

            var sky = LoadOrCreate($"{MatDir}/M_Demo_Sky.mat", "Skybox/Procedural");
            sky.SetFloat("_SunDisk", 0f);
            sky.SetFloat("_AtmosphereThickness", 0.55f);
            sky.SetColor("_SkyTint", new Color(0.55f, 0.70f, 0.90f));
            sky.SetColor("_GroundColor", new Color(0.66f, 0.79f, 0.92f));     // the cameras look down: this is the backdrop
            sky.SetFloat("_Exposure", 1.25f);
            RenderSettings.skybox = sky;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.66f, 0.76f, 0.88f);
            RenderSettings.ambientEquatorColor = new Color(0.74f, 0.76f, 0.70f);
            RenderSettings.ambientGroundColor = new Color(0.42f, 0.38f, 0.33f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.82f, 0.88f, 0.94f);

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.transform.rotation = Quaternion.Euler(48f, 32f, 0f);              // warm sun from the upper left
            sun.color = new Color(1f, 0.94f, 0.84f);
            sun.intensity = 1.25f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.8f;
            return scene;
        }

        private static void Finish(Transform world, List<Transform> islands, float yaw, float pitch)
        {
            var cam = new GameObject("Main Camera") { tag = "MainCamera" }.AddComponent<Camera>();
            cam.fieldOfView = Fov;
            Post(cam);
            var b = BoundsOf(islands.Select(i => i.gameObject));
            Aim(cam, b, yaw, pitch, 0.72f);
            RenderSettings.fogStartDistance = Vector3.Distance(cam.transform.position, b.center) * 1.1f;
            RenderSettings.fogEndDistance = RenderSettings.fogStartDistance * 2.6f;
        }

        private static void ShotCamera(Transform island, string name, float yaw, float pitch)
        {
            var cam = new GameObject(name).AddComponent<Camera>();
            cam.transform.SetParent(island, false);
            cam.fieldOfView = Fov;
            Post(cam);
            Aim(cam, BoundsOf(new[] { island.gameObject }), yaw, pitch, 0.66f);
            cam.gameObject.SetActive(false);                                     // shot cameras for renders, Main Camera is live
        }

        private static void Aim(Camera cam, Bounds b, float yaw, float pitch, float fill)
        {
            var rot = Quaternion.Euler(pitch, yaw, 0f);
            var r = b.extents.magnitude;
            var d = r / Mathf.Sin(Fov * 0.5f * Mathf.Deg2Rad) * fill * 0.82f;
            cam.transform.rotation = rot;
            cam.transform.position = b.center - rot * Vector3.forward * d;
            cam.nearClipPlane = 0.1f; cam.farClipPlane = d * 6f;
        }

        /// <summary>Camera with URP post-processing and SMAA (the Volume in the scene sets the look).</summary>
        internal static void Post(Camera cam)
        {
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
        }

        /// <summary>Soft, warm presentation grade: neutral tonemapping (keeps the flat palette), a bit of contrast and
        /// saturation, warm white balance, gentle bloom on the sky and highlights, light vignette.</summary>
        internal static VolumeProfile PostProfile(string path)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
            if (profile == null) { profile = ScriptableObject.CreateInstance<VolumeProfile>(); AssetDatabase.CreateAsset(profile, path); }
            foreach (var c in profile.components.ToArray()) { profile.Remove(c.GetType()); Object.DestroyImmediate(c, true); }
            var tone = profile.Add<Tonemapping>(true); tone.mode.Override(TonemappingMode.Neutral);
            var color = profile.Add<ColorAdjustments>(true);
            color.postExposure.Override(0.15f); color.contrast.Override(12f); color.saturation.Override(14f);
            var white = profile.Add<WhiteBalance>(true); white.temperature.Override(6f); white.tint.Override(2f);
            var bloom = profile.Add<Bloom>(true);
            bloom.threshold.Override(0.95f); bloom.intensity.Override(0.3f); bloom.scatter.Override(0.65f);
            var vignette = profile.Add<Vignette>(true); vignette.intensity.Override(0.18f); vignette.smoothness.Override(0.45f);
            foreach (var c in profile.components) { c.hideFlags = HideFlags.HideInInspector | HideFlags.HideInHierarchy; AssetDatabase.AddObjectToAsset(c, profile); c.hideFlags = HideFlags.None; }
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        internal static Bounds BoundsOf(IEnumerable<GameObject> roots)
        {
            var rs = roots.SelectMany(r => r.GetComponentsInChildren<Renderer>()).Where(r => !r.name.StartsWith("Cloud")).ToList();
            var b = rs[0].bounds;
            foreach (var r in rs.Skip(1)) b.Encapsulate(r.bounds);
            return b;
        }

        // ---------------- island + clouds ----------------
        internal static Transform Island(string name, Transform world, float rx, float rz, out float radiusX, float relief = 0.06f, string meshDir = MeshDir)
        {
            radiusX = rx;
            var island = new GameObject($"Island_{name}").transform;
            island.SetParent(world, false);
            var ground = new GameObject("IslandGround");
            ground.transform.SetParent(island, false);
            ground.AddComponent<MeshFilter>().sharedMesh = IslandMesh(name, rx, rz, relief, meshDir);
            ground.AddComponent<MeshRenderer>().sharedMaterials = new[] { _grass, _soil, _rock };
            ground.AddComponent<MeshCollider>();

            var rnd = new System.Random(name.GetHashCode());
            // (u, v, w, size) in island extents: two at the sides, a bank below the front, two small puffs behind
            var spots = new[] { (-1.35f, 0.2f, -0.45f, 0.16f), (1.4f, 0.35f, -0.4f, 0.17f), (-0.5f, -0.9f, -1.0f, 0.2f),
                                (0.6f, -0.75f, -1.1f, 0.21f), (-0.85f, 1.35f, -0.1f, 0.11f), (0.9f, 1.4f, -0.15f, 0.1f) };
            var s = Mathf.Max(rx, rz);
            for (var i = 0; i < spots.Length; i++)
            {
                var (u, v, w, k) = spots[i];
                var cloud = new GameObject($"Cloud_{i + 1}");
                cloud.transform.SetParent(island, false);
                cloud.transform.localPosition = new Vector3(u * rx, w * s * 0.6f, v * rz);
                cloud.transform.localRotation = Quaternion.Euler(0f, (float)rnd.NextDouble() * 360f, 0f);
                cloud.transform.localScale = Vector3.one * k * s * (0.85f + (float)rnd.NextDouble() * 0.3f);
                cloud.AddComponent<MeshFilter>().sharedMesh = CloudMesh();
                var mr = cloud.AddComponent<MeshRenderer>(); mr.sharedMaterial = _cloud; mr.shadowCastingMode = ShadowCastingMode.Off;
            }
            return island;
        }

        /// <summary>Faceted floating island: flat grass top at y = 0, a soil band, a rocky cone underneath. 3 submeshes.</summary>
        internal static Mesh IslandMesh(string name, float rx, float rz, float relief = 0.06f, string meshDir = MeshDir)
        {
            var rnd = new System.Random(name.GetHashCode() ^ 0x5bd1);
            const int n = 20;
            float R() => (float)rnd.NextDouble();
            var rim = new Vector3[n]; var soil = new Vector3[n]; var rock1 = new Vector3[n]; var rock2 = new Vector3[n];
            var depth = Mathf.Clamp(Mathf.Min(rx, rz) * 0.9f, 0.35f, 4.5f);
            var band = Mathf.Clamp(Mathf.Min(rx, rz) * 0.12f, 0.05f, 0.32f);
            for (var k = 0; k < n; k++)
            {
                var a = (k + R() * 0.3f) / n * Mathf.PI * 2f;
                var r = 1f + (R() - 0.5f) * 0.08f;
                var dir = new Vector3(Mathf.Cos(a) * rx, 0f, Mathf.Sin(a) * rz);
                rim[k] = dir * r + Vector3.down * (R() * relief * 0.5f);
                soil[k] = dir * (r * 0.98f) + Vector3.down * (band * (1f + R() * 0.25f));
                rock1[k] = dir * (0.78f + R() * 0.08f) + Vector3.down * (depth * (0.42f + R() * 0.08f));
                rock2[k] = dir * (0.42f + R() * 0.1f) + Vector3.down * (depth * (0.75f + R() * 0.1f));
            }
            var tip = new Vector3((R() - 0.5f) * rx * 0.2f, -depth, (R() - 0.5f) * rz * 0.2f);
            var inner = rim.Select(p => new Vector3(p.x * 0.6f, 0f, p.z * 0.6f)).ToArray();
            var mid = rim.Select(p => new Vector3(p.x * 0.82f, (R() - 0.5f) * relief, p.z * 0.82f)).ToArray();   // gentle relief outside the herd

            var verts = new List<Vector3>(); var subs = new[] { new List<int>(), new List<int>(), new List<int>() };
            void Tri(int sub, Vector3 a, Vector3 b, Vector3 c)
            {
                // Unity is clockwise for front faces seen from outside
                var i = verts.Count; verts.Add(a); verts.Add(b); verts.Add(c); subs[sub].Add(i); subs[sub].Add(i + 1); subs[sub].Add(i + 2);
            }
            void Quad(int sub, Vector3 a, Vector3 b, Vector3 c, Vector3 d) { Tri(sub, a, b, c); Tri(sub, a, c, d); }
            for (var k = 0; k < n; k++)
            {
                var j = (k + 1) % n;
                Tri(0, Vector3.zero, inner[j], inner[k]);                       // top: centre fan
                Quad(0, inner[k], inner[j], mid[j], mid[k]);                     // top: bands
                Quad(0, mid[k], mid[j], rim[j], rim[k]);
                Quad(1, rim[k], rim[j], soil[j], soil[k]);                       // soil band
                Quad(2, soil[k], soil[j], rock1[j], rock1[k]);                   // rock
                Quad(2, rock1[k], rock1[j], rock2[j], rock2[k]);
                Tri(2, rock2[k], rock2[j], tip);
            }
            Directory.CreateDirectory(meshDir);
            var path = $"{meshDir}/Island_{name}.asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh == null) { mesh = new Mesh(); AssetDatabase.CreateAsset(mesh, path); }
            mesh.Clear();
            mesh.name = $"Island_{name}";
            mesh.SetVertices(verts);
            mesh.subMeshCount = 3;
            for (var s = 0; s < 3; s++) mesh.SetTriangles(subs[s], s);
            FixWinding(mesh);
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            return mesh;
        }

        /// <summary>Flips any triangle whose normal points towards the island axis/below the top (outward-facing faceted shell).</summary>
        private static void FixWinding(Mesh mesh)
        {
            var v = mesh.vertices;
            for (var s = 0; s < mesh.subMeshCount; s++)
            {
                var t = mesh.GetTriangles(s);
                for (var i = 0; i < t.Length; i += 3)
                {
                    var a = v[t[i]]; var b = v[t[i + 1]]; var c = v[t[i + 2]];
                    var nrm = Vector3.Cross(b - a, c - a);
                    var centre = (a + b + c) / 3f;
                    var outward = s == 0 ? Vector3.up : new Vector3(centre.x, s == 1 ? 0f : centre.y * 0.6f, centre.z);
                    if (Vector3.Dot(nrm, outward) < 0f) { var tmp = t[i + 1]; t[i + 1] = t[i + 2]; t[i + 2] = tmp; }
                }
                mesh.SetTriangles(t, s);
            }
        }

        /// <summary>Low-poly puff cluster (5 icosahedra), flat bottom.</summary>
        private static Mesh CloudMesh()
        {
            if (_cloudMesh != null) return _cloudMesh;
            var path = $"{MeshDir}/Cloud.asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh == null) { mesh = new Mesh(); AssetDatabase.CreateAsset(mesh, path); }
            var t = (1f + Mathf.Sqrt(5f)) / 2f;
            var ico = new[] { new Vector3(-1, t, 0), new Vector3(1, t, 0), new Vector3(-1, -t, 0), new Vector3(1, -t, 0), new Vector3(0, -1, t), new Vector3(0, 1, t),
                              new Vector3(0, -1, -t), new Vector3(0, 1, -t), new Vector3(t, 0, -1), new Vector3(t, 0, 1), new Vector3(-t, 0, -1), new Vector3(-t, 0, 1) }
                      .Select(p => p.normalized).ToArray();
            int[] f = { 0,11,5, 0,5,1, 0,1,7, 0,7,10, 0,10,11, 1,5,9, 5,11,4, 11,10,2, 10,7,6, 7,1,8, 3,9,4, 3,4,2, 3,2,6, 3,6,8, 3,8,9, 4,9,5, 2,4,11, 6,2,10, 8,6,7, 9,8,1 };
            var puffs = new[] { (new Vector3(0f, 0.45f, 0f), 0.75f), (new Vector3(-0.8f, 0.3f, 0.1f), 0.55f), (new Vector3(0.85f, 0.28f, -0.05f), 0.58f),
                                (new Vector3(-1.45f, 0.18f, 0f), 0.38f), (new Vector3(1.5f, 0.15f, 0.05f), 0.36f) };
            var verts = new List<Vector3>(); var tris = new List<int>();
            foreach (var (c, r) in puffs)
                for (var i = 0; i < f.Length; i += 3)
                {
                    foreach (var k in new[] { f[i], f[i + 2], f[i + 1] })
                    {
                        var p = c + ico[k] * r;
                        p.y = Mathf.Max(p.y, 0f);                                 // flat bottom
                        tris.Add(verts.Count); verts.Add(p);
                    }
                }
            mesh.Clear(); mesh.name = "Cloud";
            mesh.SetVertices(verts); mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            return _cloudMesh = mesh;
        }

        internal static void Materials()
        {
            _grass = Lit("M_Demo_Grass", new Color(0.45f, 0.70f, 0.24f));
            _soil = Lit("M_Demo_Soil", new Color(0.50f, 0.32f, 0.19f));
            _rock = Lit("M_Demo_Rock", new Color(0.56f, 0.50f, 0.44f));
            _cloud = Lit("M_Demo_Cloud", new Color(0.97f, 0.98f, 1f));
            _cloud.SetColor("_EmissionColor", new Color(0.25f, 0.27f, 0.30f));
            _cloud.EnableKeyword("_EMISSION");
            _cloudMesh = null;
        }

        internal static Material Lit(string name, Color color, string dir = MatDir)
        {
            Directory.CreateDirectory(dir);
            var m = LoadOrCreate($"{dir}/{name}.mat", "Universal Render Pipeline/Lit");
            m.SetColor("_BaseColor", color);
            m.SetFloat("_Smoothness", 0.05f);
            m.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(m);
            return m;
        }

        internal static Material LoadOrCreate(string path, string shader)
        {
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(Shader.Find(shader)); AssetDatabase.CreateAsset(m, path); }
            else if (m.shader.name != shader) m.shader = Shader.Find(shader);
            return m;
        }

        // ---------------- check renders (production only) ----------------
        /// <summary>Renders the Main Camera and every Cam_* of the open scene to %TEMP%/FarmAnimals_demo, animals posed
        /// at a random phase of their first clip.</summary>
        public static string RenderOpenScene(int width = 1600, int height = 900)
        {
            var dir = Path.Combine(Path.GetTempPath(), "FarmAnimals_demo");
            Directory.CreateDirectory(dir);
            var scene = EditorSceneManager.GetActiveScene();
            var cams = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Camera>(true)).ToList();
            var urp = (UnityEngine.Rendering.Universal.UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var oldDist = urp.shadowDistance; var oldRes = urp.mainLightShadowmapResolution;
            urp.shadowDistance = 250f; urp.mainLightShadowmapResolution = 4096;
            AnimationMode.StartAnimationMode();
            var rnd = new System.Random(7);
            var outPaths = new List<string>();
            try
            {
                AnimationMode.BeginSampling();
                foreach (var a in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Animator>()))
                {
                    var clip = a.runtimeAnimatorController.animationClips.FirstOrDefault(c => c.name.EndsWith("_Idle")) ?? a.runtimeAnimatorController.animationClips[0];
                    AnimationMode.SampleAnimationClip(a.gameObject, clip, (float)rnd.NextDouble() * clip.length);
                }
                AnimationMode.EndSampling();
                foreach (var cam in cams)
                {
                    var was = cam.gameObject.activeSelf; cam.gameObject.SetActive(true);
                    var hidden = new List<GameObject>();
                    var own = cam.transform.parent;                              // a shot camera lives under its island
                    if (own != null)
                        foreach (Transform sib in own.parent) if (sib != own && sib.gameObject.activeSelf) { sib.gameObject.SetActive(false); hidden.Add(sib.gameObject); }
                    var rt = new RenderTexture(width, height, 24) { antiAliasing = 8 };
                    cam.targetTexture = rt; cam.aspect = width / (float)height;
                    var fs = RenderSettings.fogStartDistance; var fe = RenderSettings.fogEndDistance;
                    var d = cam.transform.position.magnitude > 0 ? cam.farClipPlane / 6f : 50f;
                    RenderSettings.fogStartDistance = d * 1.15f; RenderSettings.fogEndDistance = d * 3f;
                    cam.Render();
                    RenderSettings.fogStartDistance = fs; RenderSettings.fogEndDistance = fe;
                    RenderTexture.active = rt;
                    var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
                    tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                    RenderTexture.active = null; cam.targetTexture = null;
                    var p = Path.Combine(dir, $"{scene.name}_{cam.name.Replace(' ', '_')}.png");
                    File.WriteAllBytes(p, tex.EncodeToPNG());
                    Object.DestroyImmediate(tex); Object.DestroyImmediate(rt);
                    cam.gameObject.SetActive(was);
                    foreach (var h in hidden) h.SetActive(true);
                    outPaths.Add(p);
                }
            }
            finally
            {
                AnimationMode.StopAnimationMode();
                urp.shadowDistance = oldDist; urp.mainLightShadowmapResolution = oldRes;
            }
            return string.Join("\n", outPaths);
        }
    }
}
