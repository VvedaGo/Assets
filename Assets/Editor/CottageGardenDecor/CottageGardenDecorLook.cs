using System.IO;
using System.Linq;
using System.Reflection;
using PackTools.Editor;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace CottageGardenDecor.Editor
{
    /// <summary>
    /// The one shared look of every Cottage Garden Decor render (owner, 2026-11-26: "красивый постпроцессинг, продающая
    /// картинка"): warm key from the upper left at ~44°, cool fill and cool trilight ambient (cool shadows), a normal URP
    /// Volume with the profile Demo/Settings/FMS_Garden_Look.asset (Tonemapping, Color Adjustments, White Balance, Split Toning,
    /// Bloom, Vignette — package components only, ships with the demo scenes) and the shot render settings (4096 shadow map,
    /// SSAO of the active renderer slightly stronger for contact shadows while rendering, 2x supersampling + MSAA).
    /// Used by CottageGardenDecorDemoScene (Demo_CottageGarden) and CottageGardenDecorCompositionsScene (Demo_Compositions).
    /// </summary>
    public static class CottageGardenDecorLook
    {
        private static PackConfig C => CottageGardenDecorPackBuilder.Config;
        public static string ProfilePath => C.DemoDir + "/Settings/FMS_Garden_Look.asset";

        // ---- light (world-fixed: travel direction of the key) ----
        public static readonly Vector3 SunDirection = new Vector3(0.62f, -0.80f, 0.55f);       // ~44° elevation, from the SW / camera upper left
        public static float SunIntensity = 1.95f;
        public static Color SunColor = new Color(1.0f, 0.94f, 0.85f);
        public static float ShadowStrength = 0.88f;
        public static readonly Color FillColor = new Color(0.66f, 0.76f, 0.95f);
        public static float FillIntensity = 0.38f;
        public static Color AmbientSky = new Color(0.70f, 0.80f, 0.96f);        // cool: lifts lawn shadows to blue-green (renders_2)
        public static Color AmbientEquator = new Color(0.68f, 0.66f, 0.60f);
        public static readonly Color AmbientGround = new Color(0.40f, 0.36f, 0.30f);

        // ---- post (tuned by look rounds; see scene_demo_report.md «Look») ----
        public static TonemappingMode Tonemap = TonemappingMode.ACES;   // vs Neutral: lawn s 0.71 vs 0.83, whites stay neutral
        public static float PostExposure = 0.05f, Contrast = 18f, Saturation = -4f;   // renders_2 step 5: lawn was brighter than #9BD84E at +0.28/+0.15
        public static float Temperature = 0f, Tint = 0f;   // warmth comes from the key colour + split highlights; +WB turned the lawn yellow
        public static Color SplitShadows = new Color(0.36f, 0.44f, 0.62f), SplitHighlights = new Color(0.62f, 0.55f, 0.44f);
        public static float SplitBalance = -15f;
        public static float BloomThreshold = 1.0f, BloomIntensity = 0.3f, BloomScatter = 0.6f;
        public static Color BloomTint = new Color(1.0f, 0.92f, 0.80f);
        public static float Vignette = 0.20f, VignetteSmoothness = 0.45f;
        /// <summary>Hue vs Hue: lit lawn drifts to yellow-green (~81°) under the warm key; pull 68–100° hues by this many degrees
        /// towards green (atlas lawn #7DB93C = 92°). Reds, sand, gold flowers and blues are outside the curve.</summary>
        public static float LawnHueShift = 14f;
        /// <summary>Hue vs Sat: reds (0–15°) and blues (200–225°) boosted (0.5 = neutral) so roof, roses, water pop over the calmer lawn.</summary>
        public static float RedBlueSat = 0.65f;

        // ---- render-time renderer settings (restored after each shot) ----
        public static float SsaoIntensity = 0.7f, SsaoRadius = 0.35f;

        /// <summary>Key/fill/ambient on the PackSceneBuilder lights (Key_Sun, Fill_Sky under root).</summary>
        public static void ApplyLights(Transform root, float? intensity = null)
        {
            var key = root.Find("Key_Sun").GetComponent<Light>();
            key.transform.localRotation = Quaternion.LookRotation(SunDirection);
            key.color = SunColor;
            key.intensity = intensity ?? SunIntensity;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = ShadowStrength;
            var fill = root.Find("Fill_Sky").GetComponent<Light>();
            fill.color = FillColor;
            fill.intensity = FillIntensity;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = AmbientSky;
            RenderSettings.ambientEquatorColor = AmbientEquator;
            RenderSettings.ambientGroundColor = AmbientGround;
        }

        /// <summary>Optional aerial depth: exp2 fog in the given colour (overview shots only; the skybox is not fogged).</summary>
        public static void Haze(Color color, float density)
        {
            RenderSettings.fog = density > 0;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = color;
            RenderSettings.fogDensity = density;
        }

        /// <summary>Global Volume with the shared profile under root; post-processing on the given cameras.</summary>
        public static Volume AddVolume(Transform root, params Camera[] cameras)
        {
            var volume = new GameObject("Look_Volume").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.priority = 10;
            volume.sharedProfile = Profile();
            foreach (var cam in cameras)
            {
                var data = cam.GetComponent<UniversalAdditionalCameraData>() ?? cam.gameObject.AddComponent<UniversalAdditionalCameraData>();
                data.renderPostProcessing = true;
                data.antialiasing = AntialiasingMode.None;      // MSAA x8 on the shot RT + 2x supersampling (PackSceneBuilder.Render)
                data.renderShadows = true;
            }
            return volume;
        }

        public static VolumeProfile Profile()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(ProfilePath));
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            Set<Tonemapping>(profile, t => t.mode.Override(Tonemap));
            Set<ColorAdjustments>(profile, c =>
            {
                c.postExposure.Override(PostExposure);
                c.contrast.Override(Contrast);
                c.saturation.Override(Saturation);
            });
            Set<ColorCurves>(profile, c => c.hueVsHue.Override(new TextureCurve(new[]
            {
                new Keyframe(0.17f, 0.5f), new Keyframe(0.225f, 0.5f + LawnHueShift / 360f), new Keyframe(0.28f, 0.5f),
            }, 0.5f, true, new Vector2(0f, 1f))));
            Set<ColorCurves>(profile, c => c.hueVsSat.Override(new TextureCurve(new[]
            {
                new Keyframe(0f, RedBlueSat), new Keyframe(0.042f, RedBlueSat), new Keyframe(0.075f, 0.5f), new Keyframe(0.53f, 0.5f),
                new Keyframe(0.556f, RedBlueSat), new Keyframe(0.625f, RedBlueSat), new Keyframe(0.66f, 0.5f), new Keyframe(0.955f, 0.5f),
            }, 0.5f, true, new Vector2(0f, 1f))));
            Set<WhiteBalance>(profile, w => { w.temperature.Override(Temperature); w.tint.Override(Tint); });
            Set<SplitToning>(profile, s =>
            {
                s.shadows.Override(SplitShadows);
                s.highlights.Override(SplitHighlights);
                s.balance.Override(SplitBalance);
            });
            Set<Bloom>(profile, b =>
            {
                b.threshold.Override(BloomThreshold);
                b.intensity.Override(BloomIntensity);
                b.scatter.Override(BloomScatter);
                b.tint.Override(BloomTint);
                b.highQualityFiltering.Override(true);
            });
            Set<Vignette>(profile, v => { v.intensity.Override(Vignette); v.smoothness.Override(VignetteSmoothness); v.color.Override(new Color(0.12f, 0.10f, 0.14f)); });
            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        private static void Set<T>(VolumeProfile profile, System.Action<T> set) where T : VolumeComponent
        {
            if (!profile.TryGet<T>(out var component))
            {
                component = profile.Add<T>();
                component.name = typeof(T).Name;
                AssetDatabase.AddObjectToAsset(component, profile);
            }
            component.active = true;
            set(component);
            EditorUtility.SetDirty(component);
        }

        /// <summary>PackSceneBuilder.Render (4096 shadow map, 2x supersampling, MSAA x8) with the renderer's SSAO raised to the
        /// look values for this shot only; the renderer asset is restored (never saved) afterwards.</summary>
        public static void Render(Camera cam, string path, int width, int height, int supersample = 2)
        {
            var restore = SetSsao(SsaoIntensity, SsaoRadius);
            var async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;   // new keyword variants (fog, post) must be compiled before the offscreen render
            try { RenderHdr(cam, path, width, height, supersample); }
            finally { restore?.Invoke(); ShaderUtil.allowAsyncCompilation = async; }
        }

        /// <summary>As PackSceneBuilder.Render (4096 shadow map, shadow distance 60, MSAA x8, supersampling), but the camera target
        /// is an HDR texture: URP takes the camera colour format from targetTexture, and the ARGB32 target of the shared Render
        /// clamped the scene at 1.0 before tonemapping (whites/backdrop capped grey, no bloom). Result converted to sRGB PNG.</summary>
        public static void RenderHdr(Camera cam, string path, int width, int height, int supersample)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            var oldRes = urp.mainLightShadowmapResolution; var oldDist = urp.shadowDistance;
            urp.mainLightShadowmapResolution = 4096; urp.shadowDistance = 60;
            RenderTexture rt = null, final = null; Texture2D tex = null;
            try
            {
                rt = new RenderTexture(width * supersample, height * supersample, 24, RenderTextureFormat.DefaultHDR) { antiAliasing = 8 };
                cam.targetTexture = rt; cam.aspect = width / (float)height; cam.Render();
                final = new RenderTexture(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
                Graphics.Blit(rt, final);
                RenderTexture.active = final;
                tex = new Texture2D(width, height, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                File.WriteAllBytes(path, tex.EncodeToPNG());
            }
            finally
            {
                cam.targetTexture = null; RenderTexture.active = null;
                if (rt != null) Object.DestroyImmediate(rt);
                if (final != null) Object.DestroyImmediate(final);
                if (tex != null) Object.DestroyImmediate(tex);
                urp.mainLightShadowmapResolution = oldRes; urp.shadowDistance = oldDist;
            }
        }

        private static System.Action SetSsao(float intensity, float radius)
        {
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            const BindingFlags F = BindingFlags.Instance | BindingFlags.NonPublic;
            var list = typeof(UniversalRenderPipelineAsset).GetField("m_RendererDataList", F)?.GetValue(urp) as ScriptableRendererData[];
            var index = (int)(typeof(UniversalRenderPipelineAsset).GetField("m_DefaultRendererIndex", F)?.GetValue(urp) ?? 0);
            var data = list != null && index < list.Length ? list[index] : null;
            var ssao = data?.rendererFeatures.FirstOrDefault(f => f != null && f.GetType().Name == "ScreenSpaceAmbientOcclusion");
            var settings = ssao?.GetType().GetField("m_Settings", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(ssao);
            if (settings == null) return null;
            var fi = settings.GetType().GetField("Intensity", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            var fr = settings.GetType().GetField("Radius", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            if (fi == null || fr == null) return null;
            var oldI = fi.GetValue(settings); var oldR = fr.GetValue(settings);
            fi.SetValue(settings, intensity); fr.SetValue(settings, radius);
            return () => { fi.SetValue(settings, oldI); fr.SetValue(settings, oldR); };
        }
    }
}
