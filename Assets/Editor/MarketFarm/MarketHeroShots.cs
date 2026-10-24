using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Object = UnityEngine.Object;

namespace MarketFarm.Editor
{
    /// <summary>Renders the camera set of MarketHero.unity into AssetStore/Hero (PNG, RGB, MSAA 4x, box-downsampled from a supersampled render).</summary>
    public static class MarketHeroShots
    {
        private struct Shot
        {
            public string File;
            public int W, H, Supersample;
            public Vector3 Pos, Target;
            public float Fov, Focus;   // Focus > 0 enables the depth-of-field volume at this distance
            public Color Background;   // alpha 0 = keep the scene camera colour
            public Vector3 SunEuler;   // SunIntensity > 0 overrides the sun for this shot
            public Color SunColor;
            public float SunIntensity;
            public string Dir;         // output folder under AssetStore (null = Hero)
        }

        private static readonly Shot[] Shots =
        {
            // 01_Lite_Hero_Cover: high 3/4 view of the whole diorama, 3:2 like the Asset Store cover (1950x1300)
            // 02_Lite_Store_Card: tight frontal view of one packed stall, 3:2. Rendered at 1260x840 (3x the 420x280 card, for the image step) and at 420x280.
            // 03_Lite_Detail_Closeup: low golden light from the right, shallow depth of field focused on the crates, warm blurred backdrop
            new Shot { File = "03_Lite_Detail_Closeup_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(300.4f, 1.5f, -2.7f), Target = new Vector3(300.5f, 0.6f, 0.4f), Fov = 31f, Focus = 3.0f,
                Background = new Color(0.62f, 0.46f, 0.30f), SunEuler = new Vector3(24f, 292f, 0f), SunColor = new Color(1f, 0.74f, 0.45f), SunIntensity = 2.4f },
            // 04_Lite_Stall_Layout_Staging: blueprint view of the whole stall on a plate, neutral grey-beige backdrop
            new Shot { File = "04_Lite_Stall_Layout_Staging_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(498.9f, 3.5f, -6.1f), Target = new Vector3(500.15f, 0.8f, 0.0f), Fov = 29f,
                Background = new Color(0.74f, 0.69f, 0.62f) },
            new Shot { File = "02_Lite_Store_Card_1260x840", W = 1260, H = 840, Supersample = 2, Pos = new Vector3(98.5f, 2.6f, -5.3f), Target = new Vector3(100.4f, 1.0f, -0.3f), Fov = 30f, Background = new Color(0.64f, 0.60f, 0.55f) },
            new Shot { File = "02_Lite_Store_Card_420x280", W = 420, H = 280, Supersample = 4, Pos = new Vector3(98.5f, 2.6f, -5.3f), Target = new Vector3(100.4f, 1.0f, -0.3f), Fov = 30f, Background = new Color(0.64f, 0.60f, 0.55f) },
            new Shot { File = "01_Lite_Hero_Cover_1950x1300", W = 1950, H = 1300, Supersample = 2, Pos = new Vector3(-3.4f, 4.4f, -6.6f), Target = new Vector3(0.85f, 0.85f, -0.3f), Fov = 27.5f },

            // ---- final Asset Store set (AssetStore/Final)
            new Shot { Dir = "Final", File = "01_Icon_1024x1024", W = 1024, H = 1024, Supersample = 2, Pos = new Vector3(1100f, 1.2f, -1.75f), Target = new Vector3(1100f, 0.26f, -0.05f), Fov = 22f, Background = new Color(1.0f, 0.945f, 0.84f) },
            new Shot { Dir = "Final", File = "02_Card_1260x840", W = 1260, H = 840, Supersample = 2, Pos = new Vector3(98.5f, 3.0f, -6.6f), Target = new Vector3(100.4f, 1.05f, -0.3f), Fov = 34f, Background = new Color(0.64f, 0.6f, 0.55f) },
            new Shot { Dir = "Final", File = "02_Card_420x280", W = 420, H = 280, Supersample = 4, Pos = new Vector3(98.5f, 3.0f, -6.6f), Target = new Vector3(100.4f, 1.05f, -0.3f), Fov = 34f, Background = new Color(0.64f, 0.6f, 0.55f) },
            new Shot { Dir = "Final", File = "03_Cover_1950x1300", W = 1950, H = 1300, Supersample = 2, Pos = new Vector3(-4.8f, 4.6f, -8.0f), Target = new Vector3(3.5f, 1.0f, -0.3f), Fov = 34f, Background = new Color(0.99f, 0.89f, 0.77f) },
            new Shot { Dir = "Final", File = "04_Hero_Showcase_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(498.9f, 3.2f, -6.1f), Target = new Vector3(500.15f, 0.8f, 0.0f), Fov = 29f, Background = new Color(0.93f, 0.8f, 0.62f), SunEuler = new Vector3(32f, 300f, 0f), SunColor = new Color(1f, 0.82f, 0.58f), SunIntensity = 2.2f },
            new Shot { Dir = "Final", File = "05_Full_Collection_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(700f, 4.2f, -9.6f), Target = new Vector3(700f, 0.8f, -0.1f), Fov = 37f, Background = new Color(0.74f, 0.69f, 0.62f) },
            new Shot { Dir = "Final", File = "07_Variations_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(900f, 3.8f, -8.6f), Target = new Vector3(900f, 0.5f, -0.1f), Fov = 34f, Background = new Color(0.74f, 0.69f, 0.62f) },
            new Shot { Dir = "Final", File = "08_Gameplay_Use_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(506.5f, 6.3f, -6.6f), Target = new Vector3(500.3f, 0.5f, 0.0f), Fov = 22f, Background = new Color(0.78f, 0.83f, 0.8f) },
            new Shot { Dir = "Final", File = "09_Second_Environment_1920x1080", W = 1920, H = 1080, Supersample = 2, Pos = new Vector3(498.9f, 3.2f, -6.1f), Target = new Vector3(500.15f, 0.8f, 0.0f), Fov = 29f, Background = new Color(0.52f, 0.56f, 0.72f), SunEuler = new Vector3(12f, 250f, 0f), SunColor = new Color(1f, 0.58f, 0.34f), SunIntensity = 2.0f },
            new Shot { Dir = "Final", File = "10_Tile_Stall_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(99.8f, 2.0f, -3.4f), Target = new Vector3(100.3f, 0.9f, 0.0f), Fov = 32f, Background = new Color(0.97f, 0.92f, 0.82f) },
            new Shot { Dir = "Final", File = "10_Tile_Cart_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(300.4f, 1.6f, -3.0f), Target = new Vector3(300.4f, 0.55f, 0.2f), Fov = 33f, Background = new Color(0.97f, 0.92f, 0.82f) },
            new Shot { Dir = "Final", File = "10_Tile_Crates_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(500.8f, 1.4f, -3.4f), Target = new Vector3(500.7f, 0.3f, -0.8f), Fov = 30f, Background = new Color(0.97f, 0.92f, 0.82f) },
            new Shot { Dir = "Final", File = "10_Tile_ScaleSigns_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(101.4f, 1.6f, -3.0f), Target = new Vector3(101.2f, 0.7f, -0.4f), Fov = 30f, Background = new Color(0.97f, 0.92f, 0.82f) },
            new Shot { Dir = "Final", File = "10_Tile_Produce_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(699.9f, 1.7f, -5.6f), Target = new Vector3(699.5f, 0.4f, -1.5f), Fov = 28f, Background = new Color(0.97f, 0.92f, 0.82f) },
            new Shot { Dir = "Final", File = "10_Tile_Variants_640x540", W = 640, H = 540, Supersample = 2, Pos = new Vector3(900.6f, 1.5f, -4.6f), Target = new Vector3(900.6f, 0.3f, 1.3f), Fov = 30f, Background = new Color(0.97f, 0.92f, 0.82f) },
        };

        [MenuItem("Tools/MarketFarm/Render Hero Shots")]
        public static void RenderAll() => Render(null, null);

        [MenuItem("Tools/MarketFarm/Render Final Shots")]
        public static void RenderFinal() => Render(null, "Final");

        /// <summary>Renders every shot whose file name starts with <paramref name="prefix"/> (all when null).</summary>
        public static void Render(string prefix, string dir = null)
        {
            if (EditorSceneManager.GetActiveScene().path != MarketHeroBuilder.ScenePath)
                EditorSceneManager.OpenScene(MarketHeroBuilder.ScenePath, OpenSceneMode.Single);

            var cam = GameObject.Find("Hero Camera").GetComponent<Camera>();
            var dofVolume = GameObject.Find("Post_DoF").GetComponent<Volume>();
            var pipeline = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;

            // a private copy of the project's pipeline: MSAA 4x, render scale 1, SSAO tuned for the promo look (project assets stay untouched)
            var sceneBackground = cam.backgroundColor;
            var sceneSunRotation = RenderSettings.sun.transform.rotation;
            var sceneSunColor = RenderSettings.sun.color;
            var sceneSunIntensity = RenderSettings.sun.intensity;
            var oldPipeline = QualitySettings.renderPipeline;
            QualitySettings.renderPipeline = HeroPipeline(pipeline);
            try
            {
                Capture(cam, null, 64, 64, 1); // the first render after a scene load comes out blank
                foreach (var s in Shots)
                {
                    if (prefix != null && !s.File.StartsWith(prefix)) continue;
                    if ((s.Dir ?? "Hero") != (dir ?? "Hero")) continue;
                    var outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AssetStore", s.Dir ?? "Hero"));
                    Directory.CreateDirectory(outDir);
                    cam.transform.position = s.Pos;
                    cam.transform.LookAt(s.Target);
                    cam.fieldOfView = s.Fov;
                    var sun = RenderSettings.sun;
                    sun.transform.rotation = s.SunIntensity > 0f ? Quaternion.Euler(s.SunEuler) : sceneSunRotation;
                    sun.color = s.SunIntensity > 0f ? s.SunColor : sceneSunColor;
                    sun.intensity = s.SunIntensity > 0f ? s.SunIntensity : sceneSunIntensity;
                    cam.backgroundColor = s.Background.a > 0f ? s.Background : sceneBackground;
                    dofVolume.weight = s.Focus > 0f ? 1f : 0f;
                    if (s.Focus > 0f)
                    {
                        dofVolume.sharedProfile.TryGet(out DepthOfField dof);
                        dof.focusDistance.Override(s.Focus);
                    }
                    var path = Path.Combine(outDir, s.File + ".png");
                    Capture(cam, path, s.W * s.Supersample, s.H * s.Supersample, s.Supersample);
                    Debug.Log($"[MarketHero] rendered {path}");
                }
            }
            finally
            {
                QualitySettings.renderPipeline = oldPipeline;
                dofVolume.weight = 0f;
                cam.backgroundColor = sceneBackground;
                RenderSettings.sun.transform.rotation = sceneSunRotation;
                RenderSettings.sun.color = sceneSunColor;
                RenderSettings.sun.intensity = sceneSunIntensity;
            }
        }

        internal static UniversalRenderPipelineAsset HeroPipeline(UniversalRenderPipelineAsset source)
        {
            const string dir = "Assets/Scenes/Hero";
            Directory.CreateDirectory(dir);
            var sourceData = new SerializedObject(source).FindProperty("m_RendererDataList").GetArrayElementAtIndex(0).objectReferenceValue;
            AssetDatabase.DeleteAsset($"{dir}/Hero_Renderer.asset");
            AssetDatabase.DeleteAsset($"{dir}/Hero_RP.asset");
            AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(sourceData), $"{dir}/Hero_Renderer.asset");
            AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(source), $"{dir}/Hero_RP.asset");
            var rp = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>($"{dir}/Hero_RP.asset");
            var data = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>($"{dir}/Hero_Renderer.asset");

            var so = new SerializedObject(rp);
            so.FindProperty("m_RendererDataList").GetArrayElementAtIndex(0).objectReferenceValue = data;
            so.ApplyModifiedPropertiesWithoutUndo();
            rp.msaaSampleCount = 4;
            rp.renderScale = 1f;

            var tuned = false;
            foreach (var feature in data.rendererFeatures)
            {
                if (feature.GetType().Name != "ScreenSpaceAmbientOcclusion") continue;
                var fso = new SerializedObject(feature);
                fso.FindProperty("m_Settings.Intensity").floatValue = 1.2f;
                fso.FindProperty("m_Settings.Radius").floatValue = 0.4f;
                fso.FindProperty("m_Settings.DirectLightingStrength").floatValue = 0.25f;
                fso.FindProperty("m_Settings.Samples").intValue = 2; // high
                fso.ApplyModifiedPropertiesWithoutUndo();
                tuned = true;
            }
            if (!tuned) Debug.LogWarning("[MarketHero] no SSAO feature in the renderer; frames render without it");
            AssetDatabase.SaveAssets();
            return rp;
        }

        internal static void Capture(Camera cam, string path, int w, int h, int downsample)
        {
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = rt;
            cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(rt);

            if (path != null)
            {
                if (downsample > 1) tex = BoxDownsample(tex, downsample);
                File.WriteAllBytes(path, tex.EncodeToPNG());
            }
            Object.DestroyImmediate(tex);
        }

        private static Texture2D BoxDownsample(Texture2D src, int k)
        {
            var w = src.width / k;
            var h = src.height / k;
            var srcPx = src.GetPixels();
            var dst = new Color[w * h];
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                Color sum = default;
                for (var dy = 0; dy < k; dy++)
                for (var dx = 0; dx < k; dx++)
                    sum += srcPx[(y * k + dy) * src.width + x * k + dx];
                dst[y * w + x] = sum / (k * k);
            }
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.SetPixels(dst);
            tex.Apply();
            Object.DestroyImmediate(src);
            return tex;
        }
    }
}
