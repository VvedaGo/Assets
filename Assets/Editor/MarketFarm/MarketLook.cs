using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace MarketFarm.Editor
{
    /// <summary>URP post-processing profiles and the sky used by the Asset Store scenes ("juicy" look).</summary>
    internal static class MarketLook
    {
        private const string Dir = MarketSceneBuilder.Root + "/Rendering";

        // Warm, saturated, slightly bloomy — for the assembled market scene.
        internal static VolumeProfile MarketProfile() => Profile("VP_MarketJuicy", new Look
        {
            Exposure = 0.25f, Contrast = 16f, Saturation = 26f, Temperature = 9f,
            BloomThreshold = 0.85f, BloomIntensity = 0.45f, Vignette = 0.24f,
        });

        // Neutral and clean — for the catalogue so product colours stay honest.
        internal static VolumeProfile ShowcaseProfile() => Profile("VP_ShowcaseClean", new Look
        {
            Exposure = 0.1f, Contrast = 10f, Saturation = 14f, Temperature = 2f,
            BloomThreshold = 1.1f, BloomIntensity = 0.12f, Vignette = 0.10f,
        });

        internal static Material Sky()
        {
            Directory.CreateDirectory(Dir);
            var path = $"{Dir}/M_Sky_Day.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = new Material(Shader.Find("Skybox/Procedural"));
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.SetColor("_SkyTint", new Color(0.42f, 0.62f, 0.98f));
            mat.SetColor("_GroundColor", new Color(0.62f, 0.72f, 0.58f));
            mat.SetFloat("_AtmosphereThickness", 0.85f);
            mat.SetFloat("_Exposure", 1.25f);
            mat.SetFloat("_SunSize", 0.04f);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        /// <summary>The market's daylight: warm key light, bright sky ambient, procedural sky, haze. Shared so every render matches.</summary>
        internal static Light ApplyDaylight(Color fogColor, float fogStart, float fogEnd)
        {
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.93f, 0.80f);
            sun.intensity = 2.1f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.85f;
            sun.transform.rotation = Quaternion.Euler(44f, -34f, 0f);
            RenderSettings.sun = sun;
            RenderSettings.skybox = Sky();
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.60f, 0.76f, 1.0f);
            RenderSettings.ambientEquatorColor = new Color(0.62f, 0.62f, 0.58f);
            RenderSettings.ambientGroundColor = new Color(0.40f, 0.34f, 0.26f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = fogColor;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogStartDistance = fogStart;
            RenderSettings.fogEndDistance = fogEnd;
            return sun;
        }

        private struct Look
        {
            public float Exposure, Contrast, Saturation, Temperature, BloomThreshold, BloomIntensity, Vignette;
        }

        private static VolumeProfile Profile(string name, Look look)
        {
            Directory.CreateDirectory(Dir);
            var path = $"{Dir}/{name}.asset";
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, path);
            }
            // Rebuild the component list so re-running always matches the numbers above.
            foreach (var c in profile.components.ToArray()) profile.Remove(c.GetType());

            var tone = profile.Add<Tonemapping>();
            tone.mode.Override(TonemappingMode.ACES);

            var bloom = profile.Add<Bloom>();
            bloom.threshold.Override(look.BloomThreshold);
            bloom.intensity.Override(look.BloomIntensity);
            bloom.scatter.Override(0.65f);
            bloom.tint.Override(new Color(1f, 0.93f, 0.82f));

            var color = profile.Add<ColorAdjustments>();
            color.postExposure.Override(look.Exposure);
            color.contrast.Override(look.Contrast);
            color.saturation.Override(look.Saturation);

            var white = profile.Add<WhiteBalance>();
            white.temperature.Override(look.Temperature);

            var vignette = profile.Add<Vignette>();
            vignette.intensity.Override(look.Vignette);
            vignette.smoothness.Override(0.45f);

            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }
    }
}
