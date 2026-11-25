using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using FarmAnimals;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace FarmAnimals.Editor
{
    /// <summary>
    /// Production importer for the Farm Animals pack (not shipped). For every Art/Models/&lt;Category&gt;/FMS_&lt;Species&gt;.fbx:
    /// Generic rig and avatar, one clip per FBX take (loop flags and AnimationEvents from
    /// art/Farm_Animals/Meshes/FMS_&lt;Species&gt;.events.json in the repo), one URP/Lit material per palette atlas, one
    /// AnimatorController (Locomotion blend tree by Speed + one bool per other clip), and a prefab in
    /// Art/Prefabs/&lt;Category&gt; with the Animator, a CapsuleCollider and FarmAnimalEvents. Writes Documentation/ImportReport.txt.
    /// Idempotent: material, controller and prefab GUIDs are kept on rebuild.
    /// </summary>
    public static class FarmAnimalsBuilder
    {
        private const string Root = "Assets/FarmAnimals";
        private const string ModelDir = Root + "/Art/Models";
        private const string TextureDir = Root + "/Art/Textures";
        private const string MaterialDir = Root + "/Art/Materials";
        private const string AnimatorDir = Root + "/Art/Animators";
        private const string PrefabDir = Root + "/Art/Prefabs";
        private const string ReportPath = Root + "/Documentation/ImportReport.txt";
        private const string EventsDir = "art/Farm_Animals/Meshes";      // repo folder next to Assets (production data)
        private const float Smoothness = 0.15f;

        // Clips that move the animal: the first one found becomes the walk entry of the Locomotion blend tree,
        // the second list adds a faster entry.
        private static readonly string[] MoveClips = { "Walk", "Hop", "Scurry", "Crawl" };
        private static readonly string[] FastClips = { "Run", "Trot" };

        [MenuItem("Tools/Farm Animals/Import And Build Prefabs")]
        public static void BuildMenu() => Build();

        public static string Build()
        {
            Directory.CreateDirectory(MaterialDir);
            Directory.CreateDirectory(AnimatorDir);
            Directory.CreateDirectory(Path.GetDirectoryName(ReportPath));
            ConfigureTextures();

            var models = AssetDatabase.FindAssets("t:Model", new[] { ModelDir })
                .Select(AssetDatabase.GUIDToAssetPath).OrderBy(p => p).ToList();
            foreach (var path in models) ConfigureModel(path);

            var lines = models.Select(BuildAnimal).ToList();
            AssetDatabase.SaveAssets();

            var report = new StringBuilder();
            report.AppendLine($"[FarmAnimals] {lines.Count} prefabs, {lines.Count(l => l.Contains(" ! "))} with issues");
            foreach (var l in lines) report.AppendLine(l);
            File.WriteAllText(ReportPath, report.ToString());
            AssetDatabase.ImportAsset(ReportPath);
            Debug.Log(report.ToString());
            return report.ToString();
        }

        private static string Species(string modelPath) => Path.GetFileNameWithoutExtension(modelPath).Substring(4);   // FMS_Cow -> Cow

        private static void ConfigureTextures()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { TextureDir }))
            {
                var importer = (TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GUIDToAssetPath(guid));
                if (importer.filterMode == FilterMode.Point && !importer.mipmapEnabled) continue;
                importer.filterMode = FilterMode.Point;          // flat-colour atlas cells must not bleed
                importer.mipmapEnabled = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
        }

        // ---------------- model import: rig, clips, events ----------------
        private static void ConfigureModel(string modelPath)
        {
            var importer = (ModelImporter)AssetImporter.GetAtPath(modelPath);
            importer.materialImportMode = ModelImporterMaterialImportMode.None;      // URP material assigned below
            importer.importCameras = false;
            importer.importLights = false;
            importer.isReadable = false;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.importNormals = ModelImporterNormals.Import;                   // flat-shaded facets as authored
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            importer.optimizeGameObjects = false;                                  // part names repeat the root name in some FBX; keep bones visible for attachments
            importer.importAnimation = true;
            importer.animationCompression = ModelImporterAnimationCompression.Optimal;
            importer.SaveAndReimport();                                            // takes are known only after a Generic import

            var spec = ReadEvents(Species(modelPath));
            var clips = new List<ModelImporterClipAnimation>();
            foreach (var take in importer.defaultClipAnimations)
            {
                var name = take.takeName.Contains("|") ? take.takeName.Substring(take.takeName.LastIndexOf('|') + 1) : take.takeName;
                var key = name.Substring(name.IndexOf('_') + 1);                      // Cow_Lie_Idle -> Lie_Idle
                spec.TryGetValue(key, out var clipSpec);
                var loop = clipSpec == null || Bool(clipSpec, "loop", true);
                take.name = name;
                take.loopTime = loop;
                take.loopPose = loop;
                take.lockRootRotation = take.lockRootHeightY = take.lockRootPositionXZ = false;
                take.events = clipSpec == null ? new AnimationEvent[0] : Events(clipSpec, take.lastFrame - take.firstFrame);
                clips.Add(take);
            }
            importer.clipAnimations = clips.ToArray();
            importer.SaveAndReimport();
        }

        private static AnimationEvent[] Events(Dictionary<string, object> clipSpec, float frames)
        {
            if (!clipSpec.TryGetValue("events", out var raw) || !(raw is List<object> list)) return new AnimationEvent[0];
            return list.Cast<Dictionary<string, object>>().Select(e => new AnimationEvent
            {
                functionName = (string)e["name"],
                stringParameter = e.TryGetValue("stringParameter", out var p) ? p as string ?? "" : "",
                time = Mathf.Clamp01((float)(double)e["frame"] / Mathf.Max(1f, frames)),   // normalized in ModelImporter
            }).ToArray();
        }

        private static Dictionary<string, Dictionary<string, object>> ReadEvents(string species)
        {
            var result = new Dictionary<string, Dictionary<string, object>>();
            var path = Path.Combine(Path.GetDirectoryName(Application.dataPath), EventsDir, $"FMS_{species}.events.json");
            if (!File.Exists(path)) return result;                                    // Bee: no events file, all clips loop
            var json = (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(path));
            foreach (var kv in (Dictionary<string, object>)json["clips"]) result[kv.Key] = (Dictionary<string, object>)kv.Value;
            return result;
        }

        private static bool Bool(Dictionary<string, object> d, string key, bool fallback) =>
            d.TryGetValue(key, out var v) && v is bool b ? b : fallback;

        private static float Number(Dictionary<string, object> d, string key, float fallback) =>
            d != null && d.TryGetValue(key, out var v) && v is double n ? (float)n : fallback;

        // ---------------- prefab ----------------
        private static string BuildAnimal(string modelPath)
        {
            var species = Species(modelPath);
            var category = Path.GetFileName(Path.GetDirectoryName(modelPath));
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            var clips = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__")).ToList();
            var issues = new List<string>();

            var material = UrpMaterial(species, issues);
            var controller = Controller(species, clips, ReadEvents(species), issues);

            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            instance.name = model.name;

            var renderers = instance.GetComponentsInChildren<Renderer>(true);
            foreach (var r in renderers) r.sharedMaterials = Enumerable.Repeat(material, r.sharedMaterials.Length).ToArray();

            if (!instance.TryGetComponent<Animator>(out var animator)) animator = instance.AddComponent<Animator>();
            animator.runtimeAnimatorController = controller;
            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
            if (animator.avatar == null) issues.Add("no avatar");
            if (instance.GetComponent<FarmAnimalEvents>() == null) instance.AddComponent<FarmAnimalEvents>();

            var bounds = MeshBounds(instance, renderers);
            if (!instance.TryGetComponent<CapsuleCollider>(out var capsule)) capsule = instance.AddComponent<CapsuleCollider>();
            capsule.direction = bounds.size.z >= bounds.size.x ? 2 : 0;               // along the body
            capsule.radius = Mathf.Min(bounds.size.y, capsule.direction == 2 ? bounds.size.x : bounds.size.z) * 0.5f;
            capsule.height = Mathf.Max(capsule.direction == 2 ? bounds.size.z : bounds.size.x, capsule.radius * 2f);
            capsule.center = bounds.center;

            var tris = renderers.Select(MeshOf).Where(m => m != null).Sum(m => m.triangles.Length / 3);
            if (instance.transform.localEulerAngles.sqrMagnitude > 0.01f) issues.Add($"root rotation {instance.transform.localEulerAngles}");
            if (Mathf.Abs(bounds.min.y) > 0.01f) issues.Add($"min Y {bounds.min.y:F3}");
            if (clips.Count == 0) issues.Add("no clips");

            var dir = $"{PrefabDir}/{category}";
            Directory.CreateDirectory(dir);
            PrefabUtility.SaveAsPrefabAsset(instance, $"{dir}/{model.name}.prefab");
            Object.DestroyImmediate(instance);

            var events = clips.Sum(c => AnimationUtility.GetAnimationEvents(c).Length);
            return $"{category}/{model.name}  tris {tris}  clips {clips.Count} ({string.Join(", ", clips.Select(c => c.name.Substring(species.Length + 1) + (c.isLooping ? "" : "*")))})" +
                   $"  events {events}  size {bounds.size.x:F2}x{bounds.size.y:F2}x{bounds.size.z:F2}" +
                   (issues.Count > 0 ? "  ! " + string.Join(", ", issues) : "");
        }

        // Exact bounds of the rest pose from the real vertices (SkinnedMeshRenderer.bounds is a loose estimate).
        internal static Bounds MeshBounds(GameObject root, Renderer[] renderers)
        {
            var b = new Bounds(); var first = true; var baked = new Mesh();
            foreach (var r in renderers)
            {
                Vector3[] verts;
                if (r is SkinnedMeshRenderer s) { s.BakeMesh(baked, true); verts = baked.vertices; }
                else { var m = MeshOf(r); if (m == null) continue; verts = m.vertices; }
                foreach (var v in verts)
                {
                    var w = r.transform.TransformPoint(v) - root.transform.position;
                    if (first) { b = new Bounds(w, Vector3.zero); first = false; } else b.Encapsulate(w);
                }
            }
            Object.DestroyImmediate(baked);
            return b;
        }

        private static Mesh MeshOf(Renderer r) =>
            r is SkinnedMeshRenderer s ? s.sharedMesh : r.TryGetComponent<MeshFilter>(out var f) ? f.sharedMesh : null;

        private static Material UrpMaterial(string species, List<string> issues)
        {
            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>($"{TextureDir}/T_FarmAnimals_{species}_BaseColor.png");
            if (texture == null) issues.Add("no atlas texture");
            var path = $"{MaterialDir}/M_FarmAnimals_{species}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetTexture("_BaseMap", texture);
            mat.SetColor("_BaseColor", Color.white);
            mat.SetFloat("_Metallic", 0f);
            mat.SetFloat("_Smoothness", Smoothness);
            mat.enableInstancing = true;
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // ---------------- animator controller ----------------
        private static AnimatorController Controller(string species, List<AnimationClip> clips,
            Dictionary<string, Dictionary<string, object>> spec, List<string> issues)
        {
            var path = $"{AnimatorDir}/AC_FarmAnimals_{species}.controller";
            var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(path) ?? AnimatorController.CreateAnimatorControllerAtPath(path);
            foreach (var p in controller.parameters.ToArray()) controller.RemoveParameter(p);
            var sm = controller.layers[0].stateMachine;
            foreach (var t in sm.anyStateTransitions.ToArray()) sm.RemoveAnyStateTransition(t);
            foreach (var s in sm.states.ToArray()) sm.RemoveState(s.state);
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath(path).OfType<BlendTree>().ToArray()) Object.DestroyImmediate(o, true);

            AnimationClip Clip(string key) => clips.FirstOrDefault(c => c.name == $"{species}_{key}");
            var idle = Clip("Idle");
            var moveKey = MoveClips.FirstOrDefault(k => Clip(k) != null);
            var fastKey = FastClips.FirstOrDefault(k => Clip(k) != null);
            var used = new HashSet<AnimationClip>();

            AnimatorState home;
            if (idle != null && (moveKey != null || fastKey != null))
            {
                controller.AddParameter("Speed", AnimatorControllerParameterType.Float);
                home = controller.CreateBlendTreeInController("Locomotion", out var tree, 0);
                tree.blendParameter = "Speed";
                tree.useAutomaticThresholds = false;
                tree.AddChild(idle, 0f); used.Add(idle);
                var walkSpeed = 0.5f;
                if (moveKey != null)
                {
                    spec.TryGetValue(moveKey, out var s);
                    walkSpeed = Number(s, "speed_mps", 0.5f);
                    tree.AddChild(Clip(moveKey), walkSpeed); used.Add(Clip(moveKey));
                }
                if (fastKey != null)
                {
                    spec.TryGetValue(fastKey, out var s);
                    tree.AddChild(Clip(fastKey), Mathf.Max(Number(s, "speed_mps", walkSpeed * 2.2f), walkSpeed + 0.1f)); used.Add(Clip(fastKey));
                }
            }
            else
            {
                var first = idle ?? clips.FirstOrDefault();
                if (first == null) { issues.Add("empty controller"); return controller; }
                home = sm.AddState(first.name.Substring(species.Length + 1));
                home.motion = first; used.Add(first);
            }
            sm.defaultState = home;

            // every other clip: a bool parameter of the same name; true -> play it, false -> back home
            foreach (var clip in clips.Where(c => !used.Contains(c)).OrderBy(c => c.name))
            {
                var key = clip.name.Substring(species.Length + 1);
                controller.AddParameter(key, AnimatorControllerParameterType.Bool);
                var state = sm.AddState(key);
                state.motion = clip;
                var enter = sm.AddAnyStateTransition(state);
                enter.AddCondition(AnimatorConditionMode.If, 0, key);
                enter.canTransitionToSelf = false;
                enter.hasExitTime = false;
                enter.duration = 0.25f;
                var exit = state.AddTransition(home);
                exit.AddCondition(AnimatorConditionMode.IfNot, 0, key);
                exit.hasExitTime = false;
                exit.duration = 0.25f;
            }
            EditorUtility.SetDirty(controller);
            return controller;
        }

        // ---------------- tiny JSON reader (objects, arrays, strings, numbers, bools, null) ----------------
        private static class MiniJson
        {
            public static object Parse(string s) { var i = 0; return Value(s, ref i); }

            private static void Ws(string s, ref int i) { while (i < s.Length && char.IsWhiteSpace(s[i])) i++; }

            private static object Value(string s, ref int i)
            {
                Ws(s, ref i);
                switch (s[i])
                {
                    case '{':
                        var obj = new Dictionary<string, object>(); i++;
                        for (Ws(s, ref i); s[i] != '}'; Ws(s, ref i))
                        {
                            var key = Str(s, ref i); Ws(s, ref i); i++;          // ':'
                            obj[key] = Value(s, ref i); Ws(s, ref i);
                            if (s[i] == ',') i++;
                        }
                        i++; return obj;
                    case '[':
                        var list = new List<object>(); i++;
                        for (Ws(s, ref i); s[i] != ']'; Ws(s, ref i))
                        {
                            list.Add(Value(s, ref i)); Ws(s, ref i);
                            if (s[i] == ',') i++;
                        }
                        i++; return list;
                    case '"': return Str(s, ref i);
                    case 't': i += 4; return true;
                    case 'f': i += 5; return false;
                    case 'n': i += 4; return null;
                    default:
                        var start = i;
                        while (i < s.Length && "+-0123456789.eE".IndexOf(s[i]) >= 0) i++;
                        return double.Parse(s.Substring(start, i - start), CultureInfo.InvariantCulture);
                }
            }

            private static string Str(string s, ref int i)
            {
                var sb = new StringBuilder(); i++;
                for (; s[i] != '"'; i++)
                {
                    if (s[i] == '\\') { i++; sb.Append(s[i] == 'n' ? '\n' : s[i]); }
                    else sb.Append(s[i]);
                }
                i++; return sb.ToString();
            }
        }
    }
}
