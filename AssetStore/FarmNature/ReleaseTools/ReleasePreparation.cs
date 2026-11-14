using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

public static class ReleasePreparation
{
    const string Root = "Assets/FarmNature";
    const string ScenePath = Root + "/Demo/Scenes/Demo_FarmNature_Showcase.unity";
    static string ReportDir => Path.GetFullPath("../Reports");
    static readonly List<string> Errors = new List<string>();
    static readonly List<string> Warnings = new List<string>();

    [InitializeOnLoadMethod]
    static void ResumeVerification()
    {
        if(SessionState.GetBool("FarmNature.Release.ImportPending",false)) EditorApplication.update+=WaitForImportedAssets;
    }

    static void WaitForImportedAssets()
    {
        if(EditorApplication.isCompiling||EditorApplication.isUpdating||!File.Exists(ScenePath))return;
        EditorApplication.update-=WaitForImportedAssets;
        SessionState.SetBool("FarmNature.Release.ImportPending",false);
        VerifyImported();
    }

    public static void Prepare()
    {
        try
        {
            Directory.CreateDirectory(ReportDir);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            CreatePipeline();
            var scene = EditorSceneManager.OpenScene(ScenePath);
            var roots = scene.GetRootGameObjects();
            var compositions = roots.First(x => x.name == "FarmNature_Compositions");
            var environment = roots.First(x => x.name == "FarmNature_Environment");
            var showcase = roots.First(x => x.name == "FarmNature_Showcase");
            var overall = compositions.transform.Find("Comp_Overall");
            var hero = environment.transform.Find("Stage_Beauty_01_Overall/HeroCam").GetComponent<Camera>();
            Vector3 position = hero.transform.position;
            Quaternion rotation = hero.transform.rotation;
            float fov = hero.fieldOfView;
            foreach (var camera in scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<Camera>(true)).ToArray()) Object.DestroyImmediate(camera.gameObject);
            foreach (var listener in scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<AudioListener>(true)).ToArray()) Object.DestroyImmediate(listener);
            var icon = compositions.transform.Find("Comp_Icon");
            if (icon != null) Object.DestroyImmediate(icon.gameObject);
            overall.SetParent(null, true);
            overall.name = "01_Overview";
            compositions.name = "02_SceneStudies";
            showcase.name = "03_AssetCollection";
            environment.name = "04_Presentation";
            var names = new Dictionary<string, string> { {"Comp_Ogorod","01_VegetableGarden"},{"Comp_Pole","02_HarvestField"},{"Comp_Sad","03_AppleOrchard"},{"Comp_Prud","04_PondAndBridge"},{"Comp_Opushka","05_ForestEdge"},{"Comp_Tropa","06_FlowerPath"} };
            foreach (Transform child in compositions.transform) if (names.TryGetValue(child.name, out var name)) child.name = name;
            var cameraObject = new GameObject("Main Camera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.SetPositionAndRotation(position, rotation);
            var main = cameraObject.AddComponent<Camera>();
            main.fieldOfView = fov;
            main.nearClipPlane = 0.5f;
            main.farClipPlane = 600;
            main.clearFlags = CameraClearFlags.Skybox;
            cameraObject.AddComponent<AudioListener>();
            // Remove empty production camera holders, retaining cloud and island presentation meshes.
            foreach (var go in scene.GetRootGameObjects().SelectMany(x => x.GetComponentsInChildren<Transform>(true)).Select(x => x.gameObject).ToArray())
                if (go != null && go.name.StartsWith("Shot_") && go.transform.childCount == 0 && go.GetComponents<Component>().Length == 1) Object.DestroyImmediate(go);
            EditorSceneManager.SaveScene(scene);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Validate();
            if (Errors.Count > 0) throw new Exception("Release validation failed: " + string.Join("; ", Errors));
            Render(main, Path.Combine(ReportDir, "Showcase_Overview.png"));
            var assets = AssetDatabase.GetAllAssetPaths().Where(p => p.StartsWith(Root + "/", StringComparison.Ordinal)).ToArray();
            AssetDatabase.ExportPackage(assets, Path.Combine(ReportDir, "FarmNature_1.0.0.unitypackage"), ExportPackageOptions.Default);
            File.WriteAllText(Path.Combine(ReportDir, "prepare-success.txt"), "Prepared and exported FarmNature 1.0.0\n" + DateTime.UtcNow.ToString("O"));
            EditorApplication.Exit(0);
        }
        catch (Exception e) { Directory.CreateDirectory(ReportDir); File.WriteAllText(Path.Combine(ReportDir,"failure.txt"),e.ToString()); Debug.LogException(e); EditorApplication.Exit(1); }
    }

    public static void RebuildRelease()
    {
        try
        {
            Directory.CreateDirectory(ReportDir);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            CreatePipeline();
            EditorSceneManager.OpenScene(ScenePath);
            AssetDatabase.SaveAssets();
            Validate();
            if(Errors.Count>0)throw new Exception(string.Join("; ",Errors));
            Render(Camera.main,Path.Combine(ReportDir,"Showcase_Overview.png"));
            var paths=AssetDatabase.GetAllAssetPaths().Where(p=>p.StartsWith(Root+"/",StringComparison.Ordinal)).ToArray();
            AssetDatabase.ExportPackage(paths,Path.Combine(ReportDir,"FarmNature_1.0.0.unitypackage"),ExportPackageOptions.Default);
            File.WriteAllText(Path.Combine(ReportDir,"prepare-success.txt"),"Rebuilt release\n"+DateTime.UtcNow.ToString("O"));
            EditorApplication.Exit(0);
        }
        catch(Exception e){File.WriteAllText(Path.Combine(ReportDir,"failure.txt"),e.ToString());Debug.LogException(e);EditorApplication.Exit(1);}
    }

    static void CreatePipeline()
    {
        Directory.CreateDirectory(Root + "/Demo/Settings");
        var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Root + "/Demo/Settings/FarmNature_DemoRenderer.asset");
        if (renderer == null) { renderer = ScriptableObject.CreateInstance<UniversalRendererData>(); AssetDatabase.CreateAsset(renderer, Root + "/Demo/Settings/FarmNature_DemoRenderer.asset"); }
        var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Root + "/Demo/Settings/FarmNature_DemoPipeline.asset");
        if (pipeline == null) { pipeline = UniversalRenderPipelineAsset.Create(renderer); AssetDatabase.CreateAsset(pipeline, Root + "/Demo/Settings/FarmNature_DemoPipeline.asset"); }
        pipeline.name = "FarmNature_DemoPipeline";
        pipeline.msaaSampleCount = 4;
        pipeline.shadowDistance = 100;
        EditorUtility.SetDirty(pipeline);
        GraphicsSettings.defaultRenderPipeline = pipeline;
        for (int i = 0; i < QualitySettings.names.Length; i++) { QualitySettings.SetQualityLevel(i, false); QualitySettings.renderPipeline = pipeline; }
        PlayerSettings.colorSpace = ColorSpace.Linear;
    }

    public static void VerifyImported()
    {
        try
        {
            Directory.CreateDirectory(ReportDir);
            if(!File.Exists(ScenePath))
            {
                SessionState.SetBool("FarmNature.Release.ImportPending",true);
                EditorApplication.update-=WaitForImportedAssets;
                EditorApplication.update+=WaitForImportedAssets;
                AssetDatabase.ImportPackage(Path.Combine(ReportDir,"FarmNature_1.0.0.unitypackage"),false);
                return;
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var pipeline = AssetDatabase.LoadAssetAtPath<RenderPipelineAsset>(Root+"/Demo/Settings/FarmNature_DemoPipeline.asset");
            GraphicsSettings.defaultRenderPipeline = pipeline;
            for(int i=0;i<QualitySettings.names.Length;i++) { QualitySettings.SetQualityLevel(i,false); QualitySettings.renderPipeline=pipeline; }
            var scene=EditorSceneManager.OpenScene(ScenePath);
            Validate();
            if(Errors.Count>0)throw new Exception(string.Join("; ",Errors));
            Render(Camera.main,Path.Combine(ReportDir,"CleanImport_Overview.png"));
            RunOfficialValidator();
            File.WriteAllText(Path.Combine(ReportDir,"import-success.txt"),"Clean Unity package import validated\n"+DateTime.UtcNow.ToString("O"));
            EditorApplication.Exit(0);
        }
        catch(Exception e){Directory.CreateDirectory(ReportDir);File.WriteAllText(Path.Combine(ReportDir,"import-failure.txt"),e.ToString());Debug.LogException(e);EditorApplication.Exit(1);}
    }

    static void RunOfficialValidator()
    {
        var assemblies=AppDomain.CurrentDomain.GetAssemblies();
        var type=assemblies.Select(a=>a.GetType("AssetStoreTools.Validator.CurrentProjectValidator")).FirstOrDefault(t=>t!=null);
        if(type==null){File.WriteAllText(Path.Combine(ReportDir,"AssetStore_Validator.txt"),"Not run: Asset Store Tools is not installed.");return;}
        var assembly=type.Assembly;
        var settingsType=assembly.GetType("AssetStoreTools.Validator.Data.CurrentProjectValidationSettings");
        var settings=Activator.CreateInstance(settingsType);
        settingsType.GetField("Category").SetValue(settings,"3d/environments/landscapes");
        settingsType.GetField("ValidationPaths").SetValue(settings,new List<string>{Root});
        var enumType=assembly.GetType("AssetStoreTools.Validator.Data.ValidationType");
        settingsType.GetField("ValidationType").SetValue(settings,Enum.Parse(enumType,"UnityPackage"));
        var validator=Activator.CreateInstance(type,new[]{settings});
        var result=type.GetMethod("Validate").Invoke(validator,null);
        var resultType=result.GetType();
        var lines=new List<string>{"Unity Asset Store Tools 12.0.6", "Scope: "+Root,"Status: "+resultType.GetField("Status").GetValue(result)};
        int failures=0,warnings=0,passed=0;
        foreach(var test in (System.Collections.IEnumerable)resultType.GetField("Tests").GetValue(result))
        {
            var tt=test.GetType();
            var title=tt.GetField("Title").GetValue(test);
            var tr=tt.GetField("Result").GetValue(test);var rt=tr.GetType();
            var status=rt.GetField("Status").GetValue(tr).ToString();
            if(status=="Fail")failures++;else if(status=="Pass")passed++;else warnings++;
            lines.Add(status+": "+title);
            int messages=(int)rt.GetProperty("MessageCount").GetValue(tr);
            for(int i=0;i<messages;i++){var message=rt.GetMethod("GetMessage").Invoke(tr,new object[]{i});lines.Add("  "+message.GetType().GetMethod("GetText").Invoke(message,null));}
        }
        lines.Insert(3,"Passed: "+passed+"; failed: "+failures+"; warnings/other: "+warnings);
        var exception=resultType.GetField("Exception").GetValue(result);if(exception!=null)lines.Add(exception.ToString());
        File.WriteAllLines(Path.Combine(ReportDir,"AssetStore_Validator.txt"),lines);
    }

    static void Validate()
    {
        Errors.Clear(); Warnings.Clear();
        var lines = new List<string> { "category,name,triangles,colliders" };
        int count=0,total=0,min=int.MaxValue,max=0;
        foreach(var guid in AssetDatabase.FindAssets("t:Prefab",new[]{Root+"/Art/Prefabs"}))
        {
            var path=AssetDatabase.GUIDToAssetPath(guid);
            var go=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            count++;
            if(go.transform.localPosition.sqrMagnitude>0.00001f||Quaternion.Angle(go.transform.localRotation,Quaternion.identity)>0.01f||go.transform.localScale!=Vector3.one)Errors.Add("Non-identity root: "+path);
            if(GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(go)>0)Errors.Add("Missing prefab script: "+path);
            int tris=0;
            foreach(var filter in go.GetComponentsInChildren<MeshFilter>(true))
            {
                if(filter.sharedMesh==null){Errors.Add("Missing mesh: "+path);continue;}
                tris+=filter.sharedMesh.triangles.Length/3;
            }
            foreach(var renderer in go.GetComponentsInChildren<Renderer>(true)) foreach(var mat in renderer.sharedMaterials)
                if(mat==null||mat.shader==null||mat.shader.name=="Hidden/InternalErrorShader"||!mat.shader.isSupported)Errors.Add("Invalid material: "+path);
            if(go.GetComponentsInChildren<Collider>(true).Length!=1)Errors.Add("Unexpected collider count: "+path);
            total+=tris;min=Math.Min(min,tris);max=Math.Max(max,tris);
            lines.Add(Path.GetFileName(Path.GetDirectoryName(path))+","+go.name+","+tris+","+go.GetComponentsInChildren<Collider>(true).Length);
        }
        if(count!=88)Errors.Add("Expected 88 art prefabs, got "+count);
        var scene=SceneManager.GetActiveScene();
        var all=scene.GetRootGameObjects().SelectMany(x=>x.GetComponentsInChildren<Transform>(true)).Select(x=>x.gameObject).ToArray();
        foreach(var go in all)
        {
            if(GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(go)>0)Errors.Add("Missing scene script: "+go.name);
            foreach(var f in go.GetComponents<MeshFilter>())if(f.sharedMesh==null)Errors.Add("Missing scene mesh: "+go.name);
            foreach(var r in go.GetComponents<Renderer>())foreach(var mat in r.sharedMaterials)
                if(mat==null||mat.shader==null||mat.shader.name=="Hidden/InternalErrorShader"||!mat.shader.isSupported)Errors.Add("Missing/unsupported scene material: "+go.name);
        }
        var cameras=all.SelectMany(x=>x.GetComponents<Camera>()).ToArray();
        if(cameras.Length!=1||!cameras[0].enabled)Errors.Add("Showcase must have one enabled camera.");
        var dependencies=AssetDatabase.GetDependencies(ScenePath,true);
        var external=dependencies.Where(x=>x.StartsWith("Assets/")&&!x.StartsWith(Root+"/")).ToArray();
        Errors.AddRange(external.Select(x=>"Outside-package scene dependency: "+x));
        var artDeps=AssetDatabase.GetDependencies(AssetDatabase.FindAssets("t:Prefab",new[]{Root+"/Art/Prefabs"}).Select(AssetDatabase.GUIDToAssetPath).ToArray(),true);
        Errors.AddRange(artDeps.Where(x=>x.StartsWith("Assets/")&&!x.StartsWith(Root+"/")).Select(x=>"Outside-package prefab dependency: "+x));
        File.WriteAllLines(Path.Combine(ReportDir,"Unity_Prefab_Audit.csv"),lines);
        File.WriteAllLines(Path.Combine(ReportDir,"Scene_Dependencies.txt"),dependencies);
        File.WriteAllText(Path.Combine(ReportDir,"Validation.txt"),"Unity "+Application.unityVersion+"\nPrefabs: "+count+"\nTriangles min/max/total: "+min+" / "+max+" / "+total+"\nScene objects: "+all.Length+"\nCameras: "+cameras.Length+"\nExternal Assets dependencies: "+external.Length+"\nErrors: "+Errors.Count+"\n"+string.Join("\n",Errors)+"\n"+string.Join("\n",Warnings));
    }

    static void Render(Camera camera,string filename)
    {
        var rt=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);
        var previous=RenderTexture.active;
        var oldTarget=camera.targetTexture;
        try
        {
            camera.targetTexture=rt;camera.aspect=16f/9f;
            camera.GetUniversalAdditionalCameraData();
            var request=new UniversalRenderPipeline.SingleCameraRequest { destination=rt };
            RenderPipeline.SubmitRenderRequest(camera,request);
            RenderTexture.active=rt;
            var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
            tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();File.WriteAllBytes(filename,tex.EncodeToPNG());Object.DestroyImmediate(tex);
        }
        finally{camera.targetTexture=oldTarget;RenderTexture.active=previous;rt.Release();Object.DestroyImmediate(rt);}
    }
}
