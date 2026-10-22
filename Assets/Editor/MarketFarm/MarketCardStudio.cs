using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace MarketFarm.Editor
{
    /// <summary>
    /// Builds a dedicated Hero Card scene and renders high-quality 4:3 cards (1120x840 downsampled to 280x210)
    /// for the Unity Asset Store. Combines the best elements of both Market and Farm.
    /// </summary>
    public static class MarketCardStudio
    {
        private const string ScenePath = "Assets/Scenes/MarketCardStudio.unity";

        [MenuItem("Tools/MarketFarm/Render High-Quality Card Previews")]
        public static void BuildAndRenderCards()
        {
            BuildCardScene();

            var outDir = MarketSceneBuilder.OutputDir("Previews");
            var cardVariantsDir = Path.Combine(outDir, "Card_Variants");
            Directory.CreateDirectory(cardVariantsDir);

            // Render 3 different camera framings at 1120x840 (4x supersampling)
            // 1. Hero Market & Farm Master: Stall + Pumpkins + Wheelbarrow + Hay Stack + Barrels
            ShootCard(Path.Combine(cardVariantsDir, "Raw_HeroDiorama_1120x840.png"), 
                new Vector3(-1.8f, 2.1f, -3.8f), new Vector3(0.1f, 1.25f, 0.4f), 35f);

            // 2. Tight Fruit Stall Close-up: Red & White Canopy + Apple Crates + Pumpkins + Fresh Fruit sign
            ShootCard(Path.Combine(cardVariantsDir, "Raw_StallClose_1120x840.png"), 
                new Vector3(-0.6f, 1.85f, -2.8f), new Vector3(0.0f, 1.25f, 0.2f), 38f);

            // 3. Farm & Harvest Focus: Hay Stack + Wheelbarrow + Pumpkins + Tools + Barn in background
            ShootCard(Path.Combine(cardVariantsDir, "Raw_FarmHarvest_1120x840.png"), 
                new Vector3(2.6f, 2.1f, -3.2f), new Vector3(0.4f, 1.15f, 0.3f), 37f);

            // 4. Hero Close-up Screenshot for Gallery in 1920x1080
            var storeReadyDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "AssetStore", "Store_Ready_Images"));
            Directory.CreateDirectory(storeReadyDir);
            ShootCard(Path.Combine(storeReadyDir, "Screenshot_07_Hero_Diorama_1920x1080.png"), 
                new Vector3(-2.2f, 2.05f, -4.3f), new Vector3(0.2f, 1.15f, 0.4f), 36f, 1920, 1080);

            Debug.Log($"[MarketFarm] Raw card previews rendered to {cardVariantsDir} and Store_Ready_Images");
        }

        private static void BuildCardScene()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("CardStudio").transform;

            // 1. Studio Backdrop & Pedestal
            var ground = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ground.name = "StudioPedestal";
            ground.transform.SetParent(root, false);
            ground.transform.localPosition = new Vector3(0f, -0.1f, 0.3f);
            ground.transform.localScale = new Vector3(9f, 0.1f, 8f);
            ground.GetComponent<Renderer>().sharedMaterial = MarketGroundTextures.Cobble("M_Card_Cobble", new Vector2(4f, 4f));
            Object.DestroyImmediate(ground.GetComponent<Collider>());

            // Soft lush lawn surrounding
            var lawn = GameObject.CreatePrimitive(PrimitiveType.Plane);
            lawn.name = "StudioLawn";
            lawn.transform.SetParent(root, false);
            lawn.transform.localPosition = new Vector3(0f, -0.15f, 2f);
            lawn.transform.localScale = new Vector3(6f, 1f, 6f);
            lawn.GetComponent<Renderer>().sharedMaterial = MarketGroundTextures.Grass("M_Card_Grass", new Vector2(10f, 10f));
            Object.DestroyImmediate(lawn.GetComponent<Collider>());

            // Background soft hill
            var hill = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            hill.name = "BackdropHill";
            hill.transform.SetParent(root, false);
            hill.transform.localPosition = new Vector3(0f, -6f, 18f);
            hill.transform.localScale = new Vector3(32f, 14f, 18f);
            hill.GetComponent<Renderer>().sharedMaterial = MarketSceneBuilder.FlatMaterial("M_Card_Hill", new Color(0.38f, 0.65f, 0.24f));
            Object.DestroyImmediate(hill.GetComponent<Collider>());

            // 2. Central Hero: Street Stall with striped awning & fresh fruit
            Place("StreetStall_Wood", new Vector3(0f, 0f, 0.6f), 0f, root);

            // Counter goods
            Place("Crate_Fill_Apple", new Vector3(-0.75f, 0.88f, 0.6f), 0f, root);
            Place("Crate_Fill_Pear", new Vector3(-0.25f, 0.88f, 0.62f), 4f, root);
            Place("Scale_Weights", new Vector3(0.55f, 0.88f, 0.52f), -25f, root);

            // 3. Foreground Right: Pumpkins, Berries, Beets in rich wooden crates
            Place("Crate_Pumpkin", new Vector3(0.35f, 0f, -0.6f), -12f, root);
            Place("Crate_Tilted", new Vector3(1.25f, 0f, -0.4f), 15f, root);
            Place("Crate_Fill_Beet", new Vector3(1.25f, 0.05f, -0.4f), 15f, root);
            Place("Crate_Slatted_Low", new Vector3(1.05f, 0f, -1.05f), -5f, root);
            Place("Basket_Fill_Berries", new Vector3(1.05f, 0.08f, -1.05f), -5f, root);

            // 4. Foreground Left: Flour sacks, Standing barrel with tap, Chalkboard sign
            Place("Sack_Standing", new Vector3(-0.75f, 0f, -0.55f), 18f, root);
            Place("Sack_Lying", new Vector3(-1.35f, 0f, -0.3f), -35f, root);
            Place("Sign_Chalkboard", new Vector3(-1.15f, 0f, -1.1f), -18f, root);
            Place("Barrel_Tap", new Vector3(-1.75f, 0f, 0.2f), -75f, root);

            // 5. Farm side: Golden Hay Bales & Farmer's Wheelbarrow & Tools
            Place("HayBale_Stack3", new Vector3(1.95f, 0f, 0.8f), -15f, root);
            Place("Hay_Loose", new Vector3(1.6f, 0f, -0.2f), 30f, root);
            Place("Wheelbarrow", new Vector3(-2.2f, 0f, 0.95f), 35f, root);
            Place("Tool_Pitchfork", new Vector3(2.55f, 0.1f, 0.4f), 85f, root, tilt: -15f);
            Place("Tool_Rake", new Vector3(2.75f, 0.1f, 0.6f), 80f, root, tilt: -12f);

            // Wooden fence in background framing the diorama
            Place("Fence_Straight", new Vector3(-1.8f, 0f, 2.6f), 0f, root);
            Place("Fence_Straight", new Vector3(0.4f, 0f, 2.6f), 0f, root);
            Place("Fence_Straight", new Vector3(2.6f, 0f, 2.6f), 0f, root);
            Place("LanternPost", new Vector3(-2.6f, 0f, 2.4f), 20f, root);

            // Red Barn subtly visible in background
            Place("Barn_Red", new Vector3(-7.5f, 0f, 9.5f), 15f, root);

            // 6. 3-Point Studio Daylight
            SetupStudioDaylight();

            EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), ScenePath);
        }

        private static void SetupStudioDaylight()
        {
            // Main Key Sun: warm, golden, casting soft shadows
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1.0f, 0.94f, 0.83f);
            sun.intensity = 2.4f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.82f;
            sun.transform.rotation = Quaternion.Euler(38f, -28f, 0f);
            RenderSettings.sun = sun;

            // Fill Light: soft sky bounce
            var fill = new GameObject("Fill").AddComponent<Light>();
            fill.type = LightType.Directional;
            fill.color = new Color(0.72f, 0.85f, 1.0f);
            fill.intensity = 0.65f;
            fill.shadows = LightShadows.None;
            fill.transform.rotation = Quaternion.Euler(20f, 150f, 0f);

            // Rim Light: highlights back silhouettes
            var rim = new GameObject("Rim").AddComponent<Light>();
            rim.type = LightType.Directional;
            rim.color = new Color(1.0f, 0.98f, 0.90f);
            rim.intensity = 0.8f;
            rim.shadows = LightShadows.None;
            rim.transform.rotation = Quaternion.Euler(15f, 180f, 0f);

            RenderSettings.skybox = MarketLook.Sky();
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.68f, 0.80f, 1.0f);
            RenderSettings.ambientEquatorColor = new Color(0.65f, 0.65f, 0.60f);
            RenderSettings.ambientGroundColor = new Color(0.42f, 0.38f, 0.30f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.80f, 0.90f, 1.0f);
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogStartDistance = 25f;
            RenderSettings.fogEndDistance = 90f;

            // Post-Processing Profile: Juicy, vivid, slightly warm
            var volume = new GameObject("Global Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            
            var tone = profile.Add<Tonemapping>();
            tone.mode.Override(TonemappingMode.ACES);

            var bloom = profile.Add<Bloom>();
            bloom.threshold.Override(0.85f);
            bloom.intensity.Override(0.35f);
            bloom.scatter.Override(0.6f);

            var color = profile.Add<ColorAdjustments>();
            color.postExposure.Override(0.28f);
            color.contrast.Override(18f);
            color.saturation.Override(32f); // Delicious fruit & wood pop!

            var vignette = profile.Add<Vignette>();
            vignette.intensity.Override(0.20f);
            vignette.smoothness.Override(0.4f);

            volume.sharedProfile = profile;

            // Camera setup
            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            var cam = camGo.AddComponent<Camera>();
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 200f;
            var data = cam.GetUniversalAdditionalCameraData();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
        }

        private static GameObject Place(string prefabName, Vector3 pos, float yaw, Transform parent, float tilt = 0f)
        {
            var baseDir = MarketSceneBuilder.Root + "/Prefabs/Base";
            var path = $"{baseDir}/P_{prefabName}.prefab";
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (asset == null)
            {
                Debug.LogWarning($"[MarketCardStudio] Missing prefab {path}");
                return null;
            }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.Euler(tilt, yaw, 0f);
            return go;
        }

        private static void ShootCard(string file, Vector3 pos, Vector3 target, float fov, int w = 1120, int h = 840)
        {
            var cam = Camera.main;
            cam.transform.position = pos;
            cam.transform.LookAt(target);
            cam.fieldOfView = fov;

            var big = new RenderTexture(w * 2, h * 2, 24, RenderTextureFormat.ARGB32);
            var small = new RenderTexture(w, h, 0, RenderTextureFormat.ARGB32);
            small.filterMode = FilterMode.Bilinear;

            cam.targetTexture = big;
            cam.Render();
            Graphics.Blit(big, small);

            RenderTexture.active = small;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            File.WriteAllBytes(file, tex.EncodeToPNG());

            cam.targetTexture = null;
            RenderTexture.active = null;
            Object.DestroyImmediate(big);
            Object.DestroyImmediate(small);
            Object.DestroyImmediate(tex);
        }
    }
}
