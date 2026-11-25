using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// '#! look soft' (candidate, SCENE_STYLE.md "URP look — soft (candidate)"): the owner's softer grade after the Synty Farm
    /// mood reference — golden-hour key (warmer, lower), cool lifted shadows, gentle aerial haze, pastel cream-pink horizon,
    /// low contrast, soft bloom; demo grass / straw re-tinted to calm olive / ochre so the red body and the cool glass pop.
    /// The 'field' look stays untouched for A/B (its volume, sky material and demo atlas are not modified).
    /// </summary>
    public static class FarmMachinerySoftLook
    {
        public const string VolumePath = "Assets/_FarmMachineryDev/Demo/Settings/FarmMachinery_DemoVolume_Soft.asset";
        public const string SkyMaterialPath = "Assets/_FarmMachineryDev/Demo/Settings/M_FarmMachinery_Sky_Soft.mat";
        public const string SkyTexturePath = "Assets/_FarmMachineryDev/Demo/Textures/T_FarmMachinery_SkyPanorama_Soft.png";
        private const string DemoMaterialPath = "Assets/_FarmMachineryDev/Demo/Environment/Materials/M_FarmMachinery_Demo.mat";
        public const string DemoSoftMaterialPath = "Assets/_FarmMachineryDev/Demo/Environment/Materials/M_FarmMachinery_Demo_Soft.mat";
        public const string DemoSoftTexturePath = "Assets/_FarmMachineryDev/Demo/Environment/Textures/T_FarmMachinery_Demo_BaseColor_Soft.png";

        /// <summary>Values (SCENE_STYLE.md "URP look — soft (candidate)").</summary>
        public static class V
        {
            public static readonly Vector3 SunDirection = new Vector3(0.75f, -0.62f, 0.55f);   // ~33 deg elevation (field: ~50)
            public static readonly Color SunColor = new Color(1.0f, 0.80f, 0.58f);
            public const float SunIntensity = 2.3f, ShadowStrength = 0.75f;
            public static readonly Color FillColor = new Color(0.55f, 0.68f, 0.95f);
            public const float FillIntensity = 0.45f;
            public static readonly Color AmbientSky = new Color(0.50f, 0.58f, 0.75f);           // cool: shadows read cool
            public static readonly Color AmbientEquator = new Color(0.64f, 0.56f, 0.50f);
            public static readonly Color AmbientGround = new Color(0.40f, 0.34f, 0.28f);
            public static readonly Color FogColor = new Color(0.95f, 0.88f, 0.80f);              // warm cream horizon
            public const float FogDensity = 0.0022f;                                             // exp2: ~0.4 % at 30 m, ~2 % at 60 m, ~7 % at 120 m
            public const float PostExposure = 0.05f, Contrast = 8f, Saturation = 0f, Temperature = 0f, Tint = 2f;
            public static readonly Color SplitShadows = new Color(0.40f, 0.52f, 0.62f);
            public static readonly Color SplitHighlights = new Color(1.0f, 0.86f, 0.70f);
            public const float SplitBalance = 10f;
            public static readonly Vector4 Lift = new Vector4(1.0f, 0.99f, 1.02f, 0f);   // shadows a touch cool, not lifted
            public static readonly Vector4 Gain = new Vector4(1.02f, 1.0f, 0.97f, 0f);
            public const float BloomThreshold = 0.85f, BloomIntensity = 0.5f, BloomScatter = 0.7f;
            public static readonly Color BloomTint = new Color(1.0f, 0.93f, 0.82f);
            public const float Vignette = 0.16f, VignetteSmoothness = 0.5f;
        }

        /// <summary>Light, ambient, haze, Volume and soft demo material; post on the given shots.</summary>
        public static string Apply(Transform root, List<string> postShots)
        {
            var key = root.Find("Key_Sun").GetComponent<Light>();
            key.transform.localRotation = Quaternion.LookRotation(V.SunDirection);
            key.color = V.SunColor;
            key.intensity = V.SunIntensity;
            key.shadows = LightShadows.Soft;
            key.shadowStrength = V.ShadowStrength;
            var fill = root.Find("Fill_Sky").GetComponent<Light>();
            fill.color = V.FillColor;
            fill.intensity = V.FillIntensity;

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = V.AmbientSky;
            RenderSettings.ambientEquatorColor = V.AmbientEquator;
            RenderSettings.ambientGroundColor = V.AmbientGround;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = V.FogColor;
            RenderSettings.fogDensity = V.FogDensity;

            var volume = new GameObject("Look_Volume_Soft").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.priority = 10;
            volume.sharedProfile = Profile();
            foreach (var shot in postShots)
                root.Find("Cam_" + shot).GetComponent<UniversalAdditionalCameraData>().renderPostProcessing = true;

            // calm olive grass / ochre straw: swap the demo material for its soft copy on this scene's environment
            var demo = AssetDatabase.LoadAssetAtPath<Material>(DemoMaterialPath);
            var soft = DemoSoftMaterial(demo);
            var swapped = 0;
            var env = root.Find("Environment");
            if (env != null)
                foreach (var r in env.GetComponentsInChildren<Renderer>(true))
                {
                    var mats = r.sharedMaterials;
                    var changed = false;
                    for (var i = 0; i < mats.Length; i++)
                        if (mats[i] == demo) { mats[i] = soft; changed = true; }
                    if (changed) { r.sharedMaterials = mats; swapped++; }
                }
            return $"look soft: sun {V.SunIntensity} at ~33 deg, shadows {V.ShadowStrength}, haze exp2 {V.FogDensity}, volume {VolumePath}, soft demo material on {swapped} renderers, post on {postShots.Count} shots";
        }

        /// <summary>Soft sky material (pastel panorama) after '#! sky' set the field one.</summary>
        public static string Sky(float exposure)
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(SkyTexturePath);
            if (importer.mipmapEnabled || importer.wrapModeV != TextureWrapMode.Clamp)
            {
                importer.mipmapEnabled = false;
                importer.filterMode = FilterMode.Bilinear;
                importer.wrapModeU = TextureWrapMode.Repeat;
                importer.wrapModeV = TextureWrapMode.Clamp;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
            var mat = AssetDatabase.LoadAssetAtPath<Material>(SkyMaterialPath);
            if (mat == null)
            {
                mat = new Material(Shader.Find("FarmMachinery/Demo/URP Panorama Sky"));
                AssetDatabase.CreateAsset(mat, SkyMaterialPath);
            }
            mat.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(SkyTexturePath));
            mat.SetFloat("_Exposure", exposure);
            EditorUtility.SetDirty(mat);
            RenderSettings.skybox = mat;
            return $"sky soft: {SkyTexturePath}";
        }

        private static Material DemoSoftMaterial(Material demo)
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(DemoSoftTexturePath);
            if (importer.filterMode != FilterMode.Point || importer.mipmapEnabled)
            {
                importer.filterMode = FilterMode.Point;
                importer.mipmapEnabled = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
            var mat = AssetDatabase.LoadAssetAtPath<Material>(DemoSoftMaterialPath);
            if (mat == null)
            {
                mat = new Material(demo);
                AssetDatabase.CreateAsset(mat, DemoSoftMaterialPath);
            }
            else mat.CopyPropertiesFromMaterial(demo);
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(DemoSoftTexturePath));
            EditorUtility.SetDirty(mat);
            return mat;
        }

        public static VolumeProfile Profile()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(VolumePath));
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, VolumePath);
            }
            Set<Tonemapping>(profile, t => t.mode.Override(TonemappingMode.Neutral));
            Set<ColorAdjustments>(profile, c =>
            {
                c.postExposure.Override(V.PostExposure);
                c.contrast.Override(V.Contrast);
                c.saturation.Override(V.Saturation);
            });
            Set<WhiteBalance>(profile, w => { w.temperature.Override(V.Temperature); w.tint.Override(V.Tint); });
            Set<SplitToning>(profile, s =>
            {
                s.shadows.Override(V.SplitShadows);
                s.highlights.Override(V.SplitHighlights);
                s.balance.Override(V.SplitBalance);
            });
            Set<LiftGammaGain>(profile, l => { l.lift.Override(V.Lift); l.gain.Override(V.Gain); });
            Set<Bloom>(profile, b =>
            {
                b.threshold.Override(V.BloomThreshold);
                b.intensity.Override(V.BloomIntensity);
                b.scatter.Override(V.BloomScatter);
                b.tint.Override(V.BloomTint);
            });
            Set<Vignette>(profile, v => { v.intensity.Override(V.Vignette); v.smoothness.Override(V.VignetteSmoothness); });
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
    }
}
