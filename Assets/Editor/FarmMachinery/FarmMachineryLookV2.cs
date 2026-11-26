using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace FarmMachinery.Editor
{
    /// <summary>
    /// '#! look v2' (LOOK v2, planning/FarmMachinery/scenes/changes/00_LOOK_v2.changes.md; SCENE_STYLE.md "URP look — v2"), built
    /// from the 'soft' candidate: low golden sun (~25 deg) with long shadows, warm brownish shadows (cold only in the ambient
    /// sky and the glass), almost no haze, warm light sand / ochre ground, lighter warm olive grass, a saturated red body,
    /// warm cream horizon -> clean blue sky, lighter clouds. 'field' and 'soft' stay for A/B.
    /// </summary>
    public static class FarmMachineryLookV2
    {
        public const string VolumePath = "Assets/FarmMachinery/Lite/Demo/Settings/FarmMachinery_DemoVolume_V2.asset";
        public const string SkyMaterialPath = "Assets/FarmMachinery/Lite/Demo/Settings/M_FarmMachinery_Sky_V2.mat";
        public const string SkyTexturePath = "Assets/FarmMachinery/Lite/Demo/Textures/T_FarmMachinery_SkyPanorama_V2.png";
        private const string DemoMaterialPath = "Assets/_FarmMachineryDev/Demo/Environment/Materials/M_FarmMachinery_Demo.mat";   // base (A/B), dev-only
        public const string DemoSoftMaterialPath = "Assets/FarmMachinery/Lite/Demo/Environment/Materials/M_FarmMachinery_Demo_V2.mat";
        public const string DemoSoftTexturePath = "Assets/FarmMachinery/Lite/Demo/Environment/Textures/T_FarmMachinery_Demo_BaseColor_V2.png";

        /// <summary>Values (SCENE_STYLE.md "URP look — v2").</summary>
        public static class V
        {
            public static readonly Vector3 SunDirection = new Vector3(0.75f, -0.434f, 0.55f);  // ~25 deg elevation: long shadows (field ~50)
            public static readonly Color SunColor = new Color(1.0f, 0.87f, 0.72f);
            public const float SunIntensity = 2.4f, ShadowStrength = 0.82f;
            public static readonly Color FillColor = new Color(0.62f, 0.70f, 0.90f);
            public const float FillIntensity = 0.35f;
            public static readonly Color AmbientSky = new Color(0.52f, 0.60f, 0.78f);           // cool: shadows read cool
            public static readonly Color AmbientEquator = new Color(0.64f, 0.56f, 0.48f);
            public static readonly Color AmbientGround = new Color(0.42f, 0.35f, 0.27f);
            public static readonly Color FogColor = new Color(0.96f, 0.90f, 0.80f);              // warm cream horizon
            public const float FogDensity = 0.0008f;                                             // exp2: ~0.1 % at 40 m, ~0.9 % at 120 m: no veil
            public const float PostExposure = 0.2f, Contrast = 16f, Saturation = 6f, Temperature = 0f, Tint = 0f;
            public static readonly Color SplitShadows = new Color(0.52f, 0.46f, 0.41f);      // warm brownish shadows
            public static readonly Color SplitHighlights = new Color(0.53f, 0.51f, 0.48f);  // 0.5 grey = neutral: a light warm push only
            public const float SplitBalance = 0f;
            public static readonly Vector4 Lift = new Vector4(1.0f, 1.0f, 1.0f, 0f);     // neutral
            public static readonly Vector4 Gain = new Vector4(1.01f, 1.0f, 0.98f, 0f);
            public const float BloomThreshold = 0.8f, BloomIntensity = 0.6f, BloomScatter = 0.7f;
            public static readonly Color BloomTint = new Color(1.0f, 0.90f, 0.75f);
            public const float Vignette = 0.18f, VignetteSmoothness = 0.5f;
            public const float RedHueShift = 0.006f;   // Color Curves Hue vs Hue around 11 deg: measured lit red 10.5 -> ~7 deg
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

            var volume = new GameObject("Look_Volume_V2").AddComponent<Volume>();
            volume.transform.SetParent(root, false);
            volume.isGlobal = true;
            volume.priority = 10;
            volume.sharedProfile = Profile();
            foreach (var shot in postShots)
                root.Find("Cam_" + shot).GetComponent<UniversalAdditionalCameraData>().renderPostProcessing = true;

            // warm sand / ochre ground, light olive grass: swap the demo material for its v2 copy on this scene's environment
            var demo = AssetDatabase.LoadAssetAtPath<Material>(DemoMaterialPath);
            var soft = DemoSoftMaterial(demo, DemoSoftMaterialPath, DemoSoftTexturePath);
            // second demo atlas (DEM-07 wheat, DEM-08 bales, DEM-09 seedlings): lighter warm straw for v2
            var demo2 = AssetDatabase.LoadAssetAtPath<Material>(Demo2MaterialPath);
            var demo2V2 = demo2 != null ? DemoSoftMaterial(demo2, Demo2V2MaterialPath, Demo2V2TexturePath) : null;
            var swapped = 0;
            var env = root.Find("Environment");
            if (env != null)
                foreach (var r in env.GetComponentsInChildren<Renderer>(true))
                {
                    var mats = r.sharedMaterials;
                    var changed = false;
                    for (var i = 0; i < mats.Length; i++)
                        if (mats[i] == demo) { mats[i] = soft; changed = true; }
                        else if (demo2 != null && mats[i] == demo2) { mats[i] = demo2V2; changed = true; }
                    if (changed) { r.sharedMaterials = mats; swapped++; }
                }
            var cloud = AssetDatabase.LoadAssetAtPath<Material>(CloudMaterialPath);
            if (cloud != null && env != null)
            {
                var cloudV2 = CloudMaterial(cloud);
                foreach (var r in env.GetComponentsInChildren<Renderer>(true))
                    if (r.sharedMaterial == cloud) r.sharedMaterial = cloudV2;
            }
            return $"look v2: sun {V.SunIntensity} at ~25 deg, shadows {V.ShadowStrength}, haze exp2 {V.FogDensity}, volume {VolumePath}, soft demo material on {swapped} renderers, post on {postShots.Count} shots";
        }

        /// <summary>v2 sky material (warm cream horizon -> clean blue) after '#! sky' set the field one.</summary>
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
            return $"sky v2: {SkyTexturePath}";
        }

        private const string Demo2MaterialPath = "Assets/_FarmMachineryDev/Demo/Environment/Materials/M_FarmMachinery_Demo2.mat";
        public const string Demo2V2MaterialPath = "Assets/FarmMachinery/Lite/Demo/Environment/Materials/M_FarmMachinery_Demo2_V2.mat";
        public const string Demo2V2TexturePath = "Assets/FarmMachinery/Lite/Demo/Environment/Textures/T_FarmMachinery_Demo2_BaseColor_V2.png";

        private static Material DemoSoftMaterial(Material demo, string materialPath, string texturePath)
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(texturePath);
            if (importer.filterMode != FilterMode.Point || importer.mipmapEnabled)
            {
                importer.filterMode = FilterMode.Point;
                importer.mipmapEnabled = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
            var mat = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (mat == null)
            {
                mat = new Material(demo);
                AssetDatabase.CreateAsset(mat, materialPath);
            }
            else mat.CopyPropertiesFromMaterial(demo);
            mat.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath));
            // Э14: the copy also took the base atlas in the legacy _MainTex slot; point it at the v2 atlas so the shipped
            // material does not drag the dev-only base texture into the package
            mat.SetTexture("_MainTex", AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath));
            EditorUtility.SetDirty(mat);
            return mat;
        }

        private const string CloudMaterialPath = "Assets/_FarmMachineryDev/Demo/Environment/Materials/M_FarmMachinery_Demo_Cloud.mat";
        public const string CloudV2MaterialPath = "Assets/FarmMachinery/Lite/Demo/Environment/Materials/M_FarmMachinery_Demo_Cloud_V2.mat";

        /// <summary>Lighter clouds for v2: brighter sides and undersides, warm-white tops.</summary>
        private static Material CloudMaterial(Material cloud)
        {
            var mat = AssetDatabase.LoadAssetAtPath<Material>(CloudV2MaterialPath);
            if (mat == null)
            {
                mat = new Material(cloud);
                AssetDatabase.CreateAsset(mat, CloudV2MaterialPath);
            }
            mat.SetColor("_TopColor", new Color(1.0f, 0.99f, 0.96f));
            mat.SetColor("_SideColor", new Color(0.96f, 0.96f, 0.98f));
            mat.SetColor("_BottomColor", new Color(0.84f, 0.88f, 0.95f));
            mat.SetFloat("_FacetAccent", 0.06f);
            foreach (var slot in mat.GetTexturePropertyNames())   // Э14: no stale atlas refs from the lit material it was cloned from
                if (mat.shader.FindPropertyIndex(slot) < 0 && mat.GetTexture(slot) != null) mat.SetTexture(slot, null);
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
            // Hue vs Hue: the warm key pushes the lit red body to 9-12 deg (orange); pull only reds / red-oranges back to 5-9 deg,
            // straw (~40 deg) and grass stay untouched (MEDIA v2 polish)
            Set<ColorCurves>(profile, c => c.hueVsHue.Override(new TextureCurve(new[]
            {
                new Keyframe(0.0f, 0.5f - V.RedHueShift * 0.5f), new Keyframe(0.03f, 0.5f - V.RedHueShift),
                new Keyframe(0.085f, 0.5f), new Keyframe(0.94f, 0.5f),
            }, 0.5f, true, new Vector2(0f, 1f))));
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
