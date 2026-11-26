using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace FarmAnimals.Editor
{
    /// <summary>
    /// Production tool (not shipped): measures the facts for the Asset Store card (Technical Details) from the project
    /// and exports a test .unitypackage of Assets/FarmAnimals to measure its size. Output: AssetStore/FarmAnimals/PACKAGE_AUDIT.txt
    /// </summary>
    public static class FarmAnimalsAudit
    {
        private const string Root = "Assets/FarmAnimals";

        [MenuItem("Tools/Farm Animals/Audit Package")]
        public static string Run()
        {
            var sb = new StringBuilder();
            var prefabs = AssetDatabase.FindAssets("t:Prefab", new[] { Root + "/Art/Prefabs" }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            var animals = prefabs.Where(p => !p.Contains("/CMP/")).OrderBy(p => p).ToList();
            var comps = prefabs.Where(p => p.Contains("/CMP/")).ToList();
            sb.AppendLine($"prefabs animals {animals.Count} compositions {comps.Count}");
            int totalTris = 0, totalBones = 0, minB = int.MaxValue, maxB = 0, clipsTotal = 0, eventsTotal = 0, loops = 0, capsules = 0;
            var perCat = animals.GroupBy(p => Path.GetFileName(Path.GetDirectoryName(p)));
            foreach (var g in perCat)
            {
                var tris = g.Select(p =>
                {
                    var go = AssetDatabase.LoadAssetAtPath<GameObject>(p);
                    return go.GetComponentsInChildren<SkinnedMeshRenderer>(true).Sum(r => r.sharedMesh.triangles.Length / 3);
                }).ToList();
                sb.AppendLine($"cat {g.Key}: {tris.Count} models, tris {tris.Min()}-{tris.Max()}, total {tris.Sum()}");
                totalTris += tris.Sum();
            }
            var allTris = animals.Select(p => AssetDatabase.LoadAssetAtPath<GameObject>(p).GetComponentsInChildren<SkinnedMeshRenderer>(true).Sum(r => r.sharedMesh.triangles.Length / 3)).ToList();
            sb.AppendLine($"tris all: min {allTris.Min()} max {allTris.Max()} mean {allTris.Average():F1} total {allTris.Sum()}");
            foreach (var p in animals)
            {
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(p);
                var smr = go.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                var bones = smr.SelectMany(r => r.bones).Where(b => b != null).Distinct().Count();
                totalBones += bones; minB = Mathf.Min(minB, bones); maxB = Mathf.Max(maxB, bones);
                if (go.GetComponent<CapsuleCollider>() != null) capsules++;
                var anim = go.GetComponent<Animator>();
                var clips = anim.runtimeAnimatorController.animationClips.Distinct().ToList();
                clipsTotal += clips.Count; loops += clips.Count(c => c.isLooping);
                eventsTotal += clips.Sum(c => AnimationUtility.GetAnimationEvents(c).Length);
                sb.AppendLine($"  {go.name}: smr {smr.Length} bones {bones} clips {clips.Count} [{string.Join(",", clips.Select(c => c.name.Substring(c.name.IndexOf('_') + 1) + "=" + c.length.ToString("F2") + (c.isLooping ? "L" : "")))}] avatar {(anim.avatar != null && anim.avatar.isValid)} generic {(anim.avatar != null && !anim.avatar.isHuman)}");
            }
            sb.AppendLine($"bones min {minB} max {maxB}; clips {clipsTotal} (loop {loops}); events {eventsTotal}; capsules {capsules}");

            var tex = AssetDatabase.FindAssets("t:Texture2D", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            foreach (var g in tex.GroupBy(t => t.StartsWith(Root + "/Demo") ? "demo" : "art"))
                sb.AppendLine($"textures {g.Key}: {g.Count()} sizes {string.Join(",", g.Select(t => { var x = AssetDatabase.LoadAssetAtPath<Texture2D>(t); return x.width + "x" + x.height; }).Distinct())}");
            var mats = AssetDatabase.FindAssets("t:Material", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            foreach (var g in mats.GroupBy(t => t.StartsWith(Root + "/Demo") ? "demo" : "art"))
                sb.AppendLine($"materials {g.Key}: {g.Count()} shaders {string.Join(",", g.Select(t => AssetDatabase.LoadAssetAtPath<Material>(t).shader.name).Distinct())}");
            var ctrl = AssetDatabase.FindAssets("t:AnimatorController", new[] { Root }).Length;
            var scenes = AssetDatabase.FindAssets("t:Scene", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            var scripts = AssetDatabase.FindAssets("t:MonoScript", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            var meshes = AssetDatabase.FindAssets("t:Mesh", new[] { Root + "/Demo" }).Length;
            var volumes = AssetDatabase.FindAssets("t:VolumeProfile", new[] { Root }).Length;
            sb.AppendLine($"controllers {ctrl}; scenes {scenes.Count} [{string.Join(", ", scenes.Select(Path.GetFileName))}]; scripts [{string.Join(", ", scripts.Select(Path.GetFileName))}]; demo mesh assets {meshes}; volume profiles {volumes}");
            var models = AssetDatabase.FindAssets("t:Model", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).ToList();
            var uv2 = models.Count(m => ((ModelImporter)AssetImporter.GetAtPath(m)).generateSecondaryUV);
            var uvCh = models.Select(m => AssetDatabase.LoadAllAssetsAtPath(m).OfType<Mesh>().Max(x => Enumerable.Range(0, 8).Count(i => x.HasVertexAttribute(UnityEngine.Rendering.VertexAttribute.TexCoord0 + i)))).Distinct();
            sb.AppendLine($"models {models.Count}; generateSecondaryUV {uv2}; uv channels per mesh {string.Join(",", uvCh)}");
            var deps = AssetDatabase.GetDependencies(AssetDatabase.FindAssets("", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).Distinct().ToArray(), true)
                .Where(d => !d.StartsWith(Root)).Select(d => d.StartsWith("Packages/") ? d.Substring(0, d.IndexOf('/', 9)) : d).Distinct();
            sb.AppendLine($"outside deps: {string.Join(", ", deps)}");

            var folderBytes = Directory.GetFiles(Root, "*", SearchOption.AllDirectories).Sum(f => new FileInfo(f).Length);
            var pkg = Path.Combine(Path.GetTempPath(), "FarmAnimals_test.unitypackage");
            AssetDatabase.ExportPackage(Root, pkg, ExportPackageOptions.Recurse);
            sb.AppendLine($"folder bytes {folderBytes}; test export {pkg} bytes {new FileInfo(pkg).Length}");
            sb.AppendLine($"unity {Application.unityVersion}");
            Directory.CreateDirectory("AssetStore/FarmAnimals");
            File.WriteAllText("AssetStore/FarmAnimals/PACKAGE_AUDIT.txt", sb.ToString());
            return sb.ToString();
        }
    }
}
