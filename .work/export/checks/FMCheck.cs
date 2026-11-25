// Э14 clean-import check for Farm Machinery packages. Copied into Assets/Editor of a fresh URP project (not part of the
// package). Run: Unity -batchmode -projectPath <p> -executeMethod FMCheck.Run -fmOut <dir> -quit
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class FMCheck
{
    const string Root = "Assets/FarmMachinery";

    static string Arg(string name)
    {
        var a = System.Environment.GetCommandLineArgs();
        var i = System.Array.IndexOf(a, name);
        return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
    }

    static bool Pink(Material m) =>
        m == null || m.shader == null || m.shader.name == "Hidden/InternalErrorShader" || !m.shader.isSupported;

    static int Tris(Mesh m) => m == null ? 0 : Enumerable.Range(0, m.subMeshCount).Sum(s => (int)m.GetIndexCount(s)) / 3;

    static (int lod0, int lod1) PrefabTris(GameObject go)
    {
        var lg = go.GetComponent<LODGroup>();
        if (lg == null) return (go.GetComponentsInChildren<MeshFilter>(true).Sum(f => Tris(f.sharedMesh)), 0);
        var lods = lg.GetLODs();
        int Sum(int i) => i < lods.Length ? lods[i].renderers.Where(r => r != null).Select(r => r.GetComponent<MeshFilter>())
            .Where(f => f != null).Sum(f => Tris(f.sharedMesh)) : 0;
        return (Sum(0), Sum(1));
    }

    public static void Run()
    {
        var outDir = Arg("-fmOut") ?? "fm_check";
        Directory.CreateDirectory(outDir);
        var errors = new List<string>();
        Application.logMessageReceived += (msg, st, type) =>
        {
            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) errors.Add($"{type}: {msg}");
        };
        var r = new StringBuilder();
        r.AppendLine($"Unity {Application.unityVersion}, pipeline {(GraphicsSettings.currentRenderPipeline != null ? GraphicsSettings.currentRenderPipeline.GetType().Name + " " + GraphicsSettings.currentRenderPipeline.name : "BUILT-IN")}");
        r.AppendLine($"URP package: {UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(UnityEngine.Rendering.Universal.UniversalRenderPipeline).Assembly)?.version}");

        var all = AssetDatabase.FindAssets("", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath).Distinct().Where(p => !AssetDatabase.IsValidFolder(p)).ToList();
        r.AppendLine($"files under {Root}: {all.Count}");
        int Count(string dir, string ext) => all.Count(p => p.StartsWith($"{Root}/{dir}/") && p.EndsWith(ext));
        r.AppendLine($"Art/Models fbx {Count("Art/Models", ".fbx")}, Art/Prefabs prefabs {Count("Art/Prefabs", ".prefab")} (CMP {Count("Art/Prefabs/CMP", ".prefab")}), " +
                     $"Art/Materials {Count("Art/Materials", ".mat")}, Art/Textures {Count("Art/Textures", ".png")}, scenes {all.Count(p => p.EndsWith(".unity"))}, " +
                     $"Demo materials {all.Count(p => p.StartsWith(Root + "/Demo/") && p.EndsWith(".mat"))}, Demo textures {all.Count(p => p.StartsWith(Root + "/Demo/") && p.EndsWith(".png"))}, " +
                     $"Demo prefabs {all.Count(p => p.StartsWith(Root + "/Demo/") && p.EndsWith(".prefab"))}, Demo fbx {all.Count(p => p.StartsWith(Root + "/Demo/") && p.EndsWith(".fbx"))}, " +
                     $"shaders {all.Count(p => p.EndsWith(".shader"))}, scripts {all.Count(p => p.EndsWith(".cs") || p.EndsWith(".dll"))}");
        foreach (var s in AssetDatabase.FindAssets("t:Shader", new[] { Root }).Select(AssetDatabase.GUIDToAssetPath))
        {
            var sh = AssetDatabase.LoadAssetAtPath<Shader>(s);
            r.AppendLine($"shader {s}: supported {sh.isSupported}, errors {ShaderUtil.GetShaderMessageCount(sh)}");
        }

        // every prefab: instantiate, missing scripts, pink materials; numbers for the product prefabs
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        int prefabs = 0, inst = 0, missing = 0, pink = 0, baseCount = 0, variants = 0, lodModels = 0, boxed = 0, single = 0;
        int lod0Total = 0, lod1Total = 0, lod0Min = int.MaxValue, lod0Max = 0;
        var pinkList = new List<string>();
        foreach (var p in all.Where(p => p.EndsWith(".prefab")).OrderBy(p => p))
        {
            prefabs++;
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(p);
            var go = asset != null ? (GameObject)PrefabUtility.InstantiatePrefab(asset) : null;
            if (go == null) { r.AppendLine($"! cannot instantiate {p}"); continue; }
            inst++;
            foreach (var t in go.GetComponentsInChildren<Transform>(true)) missing += GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject);
            foreach (var rend in go.GetComponentsInChildren<Renderer>(true))
                foreach (var m in rend.sharedMaterials)
                    if (Pink(m)) { pink++; pinkList.Add($"{p} :: {rend.name}"); }
            if (p.StartsWith(Root + "/Art/Prefabs/") && !p.Contains("/CMP/"))
            {
                single++;
                if (go.GetComponent<BoxCollider>() != null) boxed++;
                if (PrefabUtility.GetPrefabAssetType(asset) == PrefabAssetType.Variant) variants++;
                else
                {
                    baseCount++;
                    var (l0, l1) = PrefabTris(asset);
                    lod0Total += l0; lod1Total += l1; lod0Min = Mathf.Min(lod0Min, l0); lod0Max = Mathf.Max(lod0Max, l0);
                    if (asset.GetComponent<LODGroup>() != null) lodModels++;
                }
            }
            Object.DestroyImmediate(go);
        }
        r.AppendLine($"prefabs {prefabs}, instantiated {inst}, missing scripts {missing}, pink/missing materials {pink}");
        foreach (var l in pinkList.Take(20)) r.AppendLine("  pink " + l);
        r.AppendLine($"product single prefabs {single} = base {baseCount} + variants {variants}; BoxCollider on {boxed}; LODGroup on {lodModels} base models");
        r.AppendLine($"LOD0 tris (base models): total {lod0Total}, min {lod0Min}, max {lod0Max}; LOD1 total {lod1Total}");

        // demo scenes: open, check, render the active camera
        foreach (var scenePath in all.Where(p => p.EndsWith(".unity")).OrderBy(p => p))
        {
            var scene = EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            int sMissing = 0, sPink = 0, renderers = 0;
            foreach (var root in scene.GetRootGameObjects())
                foreach (var t in root.GetComponentsInChildren<Transform>(true))
                {
                    sMissing += GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject);
                    var rend = t.GetComponent<Renderer>();
                    if (rend == null) continue;
                    renderers++;
                    foreach (var m in rend.sharedMaterials) if (Pink(m)) sPink++;
                }
            var sky = RenderSettings.skybox;
            var cams = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Camera>(false)).Where(c => c.isActiveAndEnabled).ToList();
            var name = Path.GetFileNameWithoutExtension(scenePath);
            var line = $"scene {name}: renderers {renderers}, missing scripts {sMissing}, pink {sPink}, skybox {(sky == null ? "none" : sky.shader.name + (Pink(sky) ? " PINK" : ""))}, active cameras {cams.Count} ({string.Join(", ", cams.Select(c => c.name))})";
            if (cams.Count > 0)
            {
                var cam = cams[0];
                var rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32);
                cam.targetTexture = rt;
                cam.Render(); cam.Render();
                RenderTexture.active = rt;
                var tex = new Texture2D(1920, 1080, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, 1920, 1080), 0, 0);
                tex.Apply();
                var px = tex.GetPixels32();
                var magenta = px.Count(c => c.r > 230 && c.g < 30 && c.b > 230);
                File.WriteAllBytes(Path.Combine(outDir, $"{name}.png"), tex.EncodeToPNG());
                RenderTexture.active = null; cam.targetTexture = null;
                line += $", render {name}.png, magenta pixels {magenta}";
            }
            r.AppendLine(line);
        }
        r.AppendLine($"errors logged during the check: {errors.Count}");
        foreach (var e in errors.Take(30)) r.AppendLine("  " + e);
        File.WriteAllText(Path.Combine(outDir, "check.txt"), r.ToString());
        Debug.Log("[FMCheck]\n" + r);
    }
}
